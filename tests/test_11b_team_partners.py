import allure
import pytest
from playwright.sync_api import Page, expect
from pages.team_partners_page import TeamPartnersPage
from utils.data_helper import generate_mobile, generate_email


def _open(logged_in_page: Page) -> TeamPartnersPage:
    page_obj = TeamPartnersPage(logged_in_page)
    page_obj.go_to_my_team()
    return page_obj


@allure.feature("My Team — Partners")
class TestTeamPartners:
    """Channel Partner tab and the Business Partner add flow.

    NOTE (app bug): the Business Partner form disables Submit whenever the PAN
    field has a value, and submitting without PAN creates no record — so a
    create-success path isn't achievable. These tests cover the picker, the form,
    and the enable/disable behaviour instead. Channel Partner has no add form; its
    add flow is Sourcing Partner (covered by the add-sourcing-partner tests)."""

    # ── Add role picker ────────────────────────────────────────────────────────
    @allure.story("Add picker offers the team roles")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_picker_offers_roles(self, logged_in_page: Page):
        """'+ Add Teammate' offers Team Member, Sourcing Partner and Business Partner."""
        team = _open(logged_in_page)
        team.open_add_picker()
        expect(team.role_team_member).to_be_visible()
        expect(team.role_sourcing_partner).to_be_visible()
        expect(team.role_business_partner).to_be_visible()

    # ── Business Partner (#11) ─────────────────────────────────────────────────
    @allure.story("Business Partner form shows its fields")
    @allure.severity(allure.severity_level.NORMAL)
    def test_business_partner_form_fields(self, logged_in_page: Page):
        """The Business Partner form shows Full Name, Mobile, Email and PAN fields."""
        team = _open(logged_in_page)
        team.open_business_partner_form()
        expect(team.bp_full_name).to_be_visible()
        expect(team.bp_mobile).to_be_visible()
        expect(team.bp_email).to_be_visible()
        expect(team.bp_pan).to_be_visible()

    @allure.story("Submit is enabled with valid Name/Mobile/Email")
    @allure.severity(allure.severity_level.NORMAL)
    def test_business_partner_submit_enabled_when_filled(self, logged_in_page: Page):
        """Submit is enabled after Full Name, Mobile and Email are filled (no PAN)."""
        team = _open(logged_in_page)
        team.open_business_partner_form()
        team.fill_business_partner("Test Business Partner", generate_mobile(), generate_email())
        expect(team.bp_submit).to_be_enabled()

    @allure.story("PAN entry disables Submit (known app bug)")
    @allure.severity(allure.severity_level.MINOR)
    def test_business_partner_pan_disables_submit(self, logged_in_page: Page):
        """Entering a PAN disables Submit — documents the current form behaviour."""
        team = _open(logged_in_page)
        team.open_business_partner_form()
        team.fill_business_partner("Test Business Partner", generate_mobile(), generate_email())
        expect(team.bp_submit).to_be_enabled()
        team.bp_pan.fill("ABCDE1234F")
        team.bp_pan.blur()
        expect(team.bp_submit).to_be_disabled()

    # ── Channel Partner tab (#10) ──────────────────────────────────────────────
    @allure.story("Channel Partner tab is selectable")
    @allure.severity(allure.severity_level.NORMAL)
    def test_channel_partner_tab_loads(self, logged_in_page: Page):
        """The Channel Partner tab opens and the Add control stays available."""
        team = _open(logged_in_page)
        team.open_channel_partner_tab()
        expect(team.channel_partner_tab.first).to_be_visible()
        expect(team.add_button).to_be_visible()

    @allure.story("Channel Partner add flow is Sourcing Partner")
    @allure.severity(allure.severity_level.MINOR)
    def test_channel_partner_add_is_sourcing_partner(self, logged_in_page: Page):
        """From the Channel Partner tab, the Add picker offers the Sourcing Partner
        role (Channel Partner has no dedicated add form)."""
        team = _open(logged_in_page)
        team.open_channel_partner_tab()
        team.open_add_picker()
        expect(team.role_sourcing_partner).to_be_visible()

    # ── List search ─────────────────────────────────────────────────────────────
    @allure.story("Search box handles special/unusual input safely")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "query",
        [
            pytest.param("' OR 1=1 --", id="sql_injection_like"),
            pytest.param("<script>alert(1)</script>", id="script_tag"),
            pytest.param("🎉🚀💥", id="emoji"),
            pytest.param("zzzznoresultxyz123", id="nonexistent_partner"),
        ],
    )
    def test_search_handles_special_characters_safely(self, logged_in_page: Page, query: str):
        """Searching the team list with SQL/script/emoji/nonexistent input never
        throws a page error and shows either matching rows or a clean
        'No records found' empty state."""
        errors = []
        logged_in_page.on("pageerror", lambda err: errors.append(str(err)))
        team = _open(logged_in_page)
        team.search(query)
        logged_in_page.wait_for_timeout(2000)
        assert errors == []
        # The table always renders at least one row: either a "No records
        # found" placeholder or genuine matching data rows — never a blank/
        # broken table.
        assert team.page.locator("table tbody tr").count() >= 1
