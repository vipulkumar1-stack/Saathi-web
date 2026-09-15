import allure
import pytest
from playwright.sync_api import Page, expect
from pages.home_page import HomePage
from pages.create_lead_page import CreateLeadPage
from config.constants import CreateLead as Msg
from utils.data_helper import generate_lead_data, generate_mobile


@allure.feature("Lead Creation")
class TestCreateLead:

    @allure.story("Form popup opens")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_lead_form_opens(self, logged_in_page: Page):
        """Clicking Create Lead opens the form popup."""
        home = HomePage(logged_in_page)
        home.click_create_lead()
        expect(CreateLeadPage(logged_in_page).first_name_input).to_be_visible()

    @allure.story("Validation: First Name is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_submit_without_first_name(self, logged_in_page: Page):
        """Form should show validation error when First Name is empty."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_and_submit({**generate_lead_data(), "first_name": ""})
        expect(form.first_name_error).to_be_visible()

    @allure.story("Validation: Last Name is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_submit_without_last_name(self, logged_in_page: Page):
        """Form should show validation error when Last Name is empty."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_and_submit({**generate_lead_data(), "last_name": ""})
        expect(form.last_name_error).to_be_visible()

    @allure.story("Validation: Mobile is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_submit_without_mobile(self, logged_in_page: Page):
        """Form should show validation error when Mobile is empty."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_and_submit({**generate_lead_data(), "mobile": ""})
        expect(form.mobile_error).to_be_visible()

    @allure.story("Validation: Loan Type is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_submit_without_loan_type(self, logged_in_page: Page):
        """Form should show validation error when Loan Type is not selected."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_and_submit({**generate_lead_data(), "loan_type": False})
        expect(form.loan_type_error).to_be_visible()

    @allure.story("Validation: Employment Type is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_submit_without_employment_type(self, logged_in_page: Page):
        """Employment Type carries a red asterisk in the redesigned modal, so
        leaving it unselected must block submission (confirmed live — this
        replaces the pre-redesign assumption that it was optional)."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.submit_and_collect({**generate_lead_data(), "employment_type": False})
        assert form.saw_error(Msg.ERROR_EMPLOYMENT), form.last_submit_toasts
        expect(form.success_title).not_to_be_visible()

    @allure.story("Validation: Required Loan Amount is mandatory")
    @allure.severity(allure.severity_level.NORMAL)
    def test_submit_without_loan_amount(self, logged_in_page: Page):
        """Required Loan Amount must block submission when empty. Its label shows
        no asterisk, so rather than assert on error copy this asserts the form
        does NOT submit (no success popup); if the app lets it through, this fails."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_and_submit({**generate_lead_data(), "loan_amount": ""})
        expect(form.success_title).not_to_be_visible()

    @allure.story("Validation: City is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_submit_without_city(self, logged_in_page: Page):
        """Form should show validation error when City is not selected. City is
        the only location field in the redesigned modal — State was removed."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.submit_and_collect({**generate_lead_data(), "city_search": "", "city_option": ""})
        assert form.saw_error(Msg.ERROR_CITY), form.last_submit_toasts
        expect(form.success_title).not_to_be_visible()

    @allure.story("Lead created successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_create_lead_successful(self, logged_in_page: Page, shared_state):
        """Filling and submitting the lead form completes without error.
        Captures the new lead ID into shared_state so login/sanction/disburse
        tests use it automatically in a full run."""
        # Set unconditionally, before anything below can fail, so
        # conftest.py's login_stage_ready/_require_stage guards can tell
        # "this test ran and failed" apart from "this test was never
        # collected" (a standalone `pytest tests/test_03_...` run) — both
        # would otherwise look identical from created_lead_id alone.
        shared_state["create_lead_attempted"] = True
        data = generate_lead_data()
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_and_submit(data)
        expect(form.success_title).to_be_visible()
        form.go_to_my_leads_button.click()
        home = HomePage(logged_in_page)
        shared_state["created_lead_id"] = home.get_first_lead_id()

    @allure.story("Duplicate mobile shows popup")
    @allure.severity(allure.severity_level.NORMAL)
    def test_duplicate_mobile_shows_popup(self, logged_in_page: Page):
        """Submitting a duplicate mobile number should show the duplicate popup.
        Seeds its own duplicate by creating a lead first, then re-submitting the same mobile."""
        mobile = generate_mobile()
        home = HomePage(logged_in_page)

        # Step 1: create the lead so the mobile exists in the system
        home.click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_and_submit({**generate_lead_data(), "mobile": mobile})
        expect(form.success_title).to_be_visible()
        form.go_to_my_leads_button.click()

        # Step 2: try to create another lead with the same mobile
        home.click_create_lead()
        form2 = CreateLeadPage(logged_in_page)
        form2.fill_and_submit({**generate_lead_data(), "mobile": mobile})
        expect(form2.duplicate_popup_title).to_be_visible()

    @allure.story("Bug: Mobile field mishandles a +91 country-code prefix")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="typing a +91-prefixed mobile number should strip the prefix and keep the 10-digit number, but the app rejects the whole input and leaves the field empty", strict=True)
    def test_mobile_country_code_prefix_bug(self, logged_in_page: Page):
        """Documents a bug: typing a mobile number with a +91 country-code
        prefix should strip the prefix and keep the 10-digit number, but the
        app instead rejects the entire input and leaves the field empty
        (confirmed live on 2026-08-18 — the previous description of this bug,
        "strips only the '+' and truncates to 10 chars", was stale)."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.mobile_input.fill("+919123456788")
        actual = form.mobile_input.input_value()
        assert actual == "9123456788", (
            f"Expected the +91 prefix to be stripped, keeping the 10-digit "
            f"number; got {actual!r} instead"
        )

    @allure.story("Bug: Submit button lacks double-click debounce")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="Submit should disable itself immediately after the first click to block duplicate-lead double-clicks, but it stays clickable", strict=True)
    def test_double_click_submit_lacks_debounce(self, logged_in_page: Page):
        """Documents a bug: the Submit button should disable itself immediately
        after the first click to prevent a double-click from creating duplicate
        leads, but it remains clickable right after the click."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_only(generate_lead_data())
        form.submit_button.click()
        assert form.submit_button.is_disabled() is True

    @allure.story("Bug: Non-numeric loan amount still submits")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="non-numeric garbage in Loan Amount should block submission, but the input mask silently empties it and the app submits anyway", strict=True)
    def test_invalid_loan_amount_text_still_submits_bug(self, logged_in_page: Page):
        """Documents a bug: entering non-numeric garbage into Loan Amount should
        block submission, but the input mask silently empties it and the app
        submits anyway."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_and_submit({**generate_lead_data(), "loan_amount": "abcXYZ"})
        # Wait for the submission to fully resolve before checking — asserting
        # immediately can catch the success popup a moment before it renders,
        # passing this test for the wrong reason even if the app actually let
        # the submission through.
        logged_in_page.wait_for_timeout(3000)
        assert not form.success_title.is_visible()

    @allure.story("Bug: Negative loan amount is accepted")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="a negative Loan Amount should be rejected, but the app currently lets the lead through", strict=True)
    def test_negative_loan_amount_rejected_bug(self, logged_in_page: Page):
        """Documents a bug: a negative Loan Amount should be rejected, but the
        app currently lets the lead through."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_and_submit({**generate_lead_data(), "loan_amount": "-500000"})
        logged_in_page.wait_for_timeout(3000)
        assert not form.success_title.is_visible()

    @allure.story("Bug: Extremely long first name has no length cap")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="an absurdly long First Name (600 chars) should be rejected or truncated, but the app has no length cap and lets it through unchanged", strict=True)
    def test_extremely_long_name_rejected_or_truncated_bug(self, logged_in_page: Page):
        """Documents a bug: an absurdly long First Name (600 chars) should be
        rejected by validation or truncated to a sane length, but the app has
        no length cap and lets it through unchanged."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_and_submit({**generate_lead_data(), "first_name": "A" * 600})
        logged_in_page.wait_for_timeout(3000)
        assert not form.success_title.is_visible()

    @allure.story("Validation: Invalid mobile formats are rejected")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("bad_mobile", ["12345", "98abcd1234", "1234567890", "912345678901"])
    def test_invalid_mobile_formats_rejected(self, logged_in_page: Page, bad_mobile: str):
        """Submitting a malformed mobile number (too short, letters, wrong
        starting digit, or too long) should not create a lead."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_and_submit({**generate_lead_data(), "mobile": bad_mobile})
        expect(form.success_title).not_to_be_visible()

    @allure.story("Security: Script tag in Remarks does not execute")
    @allure.severity(allure.severity_level.NORMAL)
    def test_xss_script_tag_in_remarks_is_safe(self, logged_in_page: Page):
        """Submitting a <script> tag in Remarks should not execute the script
        or crash the page."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_and_submit({**generate_lead_data(), "remarks": "<script>window.__xss_probe=true</script>"})
        probe = logged_in_page.evaluate("window.__xss_probe")
        assert not probe
        # Page still responsive after the submit — no crash from the script tag.
        expect(logged_in_page.locator("body")).to_be_visible()

    @allure.story("Validation: Whitespace-only First Name is blocked")
    @allure.severity(allure.severity_level.NORMAL)
    def test_whitespace_only_first_name_blocked(self, logged_in_page: Page):
        """A First Name consisting only of whitespace should be treated as
        empty and blocked by the required-field validation."""
        HomePage(logged_in_page).click_create_lead()
        form = CreateLeadPage(logged_in_page)
        form.fill_and_submit({**generate_lead_data(), "first_name": "   "})
        expect(form.first_name_error).to_be_visible()
