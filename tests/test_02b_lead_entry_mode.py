import allure
from playwright.sync_api import Page, expect
from pages.home_page import HomePage
from pages.create_lead_page import CreateLeadPage
from utils.data_helper import generate_lead_data


@allure.feature("Lead Creation")
class TestLeadEntryMode:
    """Coverage for the redesigned Add New Lead modal's entry-mode controls —
    the "I will do it myself" / "Refer to Ambak" tabs this file replaces
    (see the retired test_02b_create_lead_refer.py) no longer exist. The
    modal now always creates an 'ambak'-type lead (a fixed banner says so)
    and instead offers a choice between filling the form manually and
    bulk-uploading a CSV. Purchase Type is a genuinely new, optional field
    introduced by the same redesign.

    Every assertion here was checked against the live modal DOM before being
    written — see the probe evidence: Add Manually is the default, the
    banner always reads "...type ambak", Bulk Upload swaps in an
    upload/CSV-reference panel, and Purchase Type accepts one of
    ['Resale', 'Builder direct allotment', 'Builder endorsement',
    'Authority allotment'] with no validation error when left unset."""

    @allure.story("Add Manually is the default entry mode")
    @allure.severity(allure.severity_level.MINOR)
    def test_add_manually_selected_by_default(self, logged_in_page: Page):
        """Opening Create Lead should default to Add Manually, not Bulk Upload."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        expect(form.first_name_input).to_be_visible()
        assert form.page.locator("#add_manually").is_checked()
        assert not form.page.locator("#bulk_upload").is_checked()

    @allure.story("Lead-type banner shows the fixed 'ambak' type")
    @allure.severity(allure.severity_level.MINOR)
    def test_lead_type_banner_shows_ambak(self, logged_in_page: Page):
        """The modal always shows a fixed banner naming the lead type as
        'ambak' — there is no longer a self/refer choice to make."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        expect(form.lead_type_banner).to_be_visible()
        assert "ambak" in form.lead_type_banner.inner_text()

    @allure.story("Bulk Upload replaces the manual entry fields")
    @allure.severity(allure.severity_level.NORMAL)
    def test_bulk_upload_switches_form(self, logged_in_page: Page):
        """Selecting Bulk Upload should hide the manual entry fields and show
        the file-upload panel instead."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.bulk_upload_radio.click()
        expect(form.page.locator("#bulk_upload")).to_be_checked()
        # NOTE: first_name_input is a HealingLocator — per utils/healing_locator.py
        # it must never be used for an absence assertion (not_to_be_visible /
        # to_have_count(0)): it exhausts every fallback strategy and raises
        # TimeoutError instead of letting the assertion evaluate. Use the plain
        # #first_name locator here instead.
        expect(form.page.locator("#first_name")).not_to_be_visible()
        expect(form.page.get_by_text("Drop your file")).to_be_visible()
        expect(form.page.get_by_text("City Reference")).to_be_visible()

    @allure.story("Switching back to Add Manually restores the form")
    @allure.severity(allure.severity_level.NORMAL)
    def test_switch_back_to_add_manually_restores_form(self, logged_in_page: Page):
        """After selecting Bulk Upload, switching back to Add Manually should
        bring the manual entry fields back."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.bulk_upload_radio.click()
        # NOTE: first_name_input is a HealingLocator — per utils/healing_locator.py
        # it must never be used for an absence assertion (not_to_be_visible /
        # to_have_count(0)): it exhausts every fallback strategy and raises
        # TimeoutError instead of letting the assertion evaluate. Use the plain
        # #first_name locator here instead.
        expect(form.page.locator("#first_name")).not_to_be_visible()
        form.add_manually_radio.click()
        expect(form.page.locator("#add_manually")).to_be_checked()
        expect(form.first_name_input).to_be_visible()

    @allure.story("Purchase Type is optional")
    @allure.severity(allure.severity_level.NORMAL)
    def test_purchase_type_is_optional(self, logged_in_page: Page):
        """A lead should be created successfully with Purchase Type left
        unselected — it carries no asterisk in the live form."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_and_submit(generate_lead_data())
        expect(form.success_title).to_be_visible()

    @allure.story("Purchase Type can be selected and does not block submission")
    @allure.severity(allure.severity_level.NORMAL)
    def test_purchase_type_selectable(self, logged_in_page: Page):
        """Selecting a Purchase Type option should not prevent the lead from
        being created."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_and_submit({**generate_lead_data(), "purchase_type": "Resale"})
        expect(form.success_title).to_be_visible()
