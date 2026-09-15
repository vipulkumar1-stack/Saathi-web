import re
import allure
import pytest
from playwright.sync_api import Page, expect
from pages.cibil_page import CibilPage
from config.config import CIBIL_DATA
from config.constants import Cibil as Msg


@allure.feature("Check CIBIL Score")
class TestCibil:
    """Check CIBIL Score tool — PAN + personal details form that validates each
    field and advances to a fulfilment/loan-type step. A live bureau score needs
    a PAN with real data, so the happy path asserts reaching the fulfilment step."""

    def _open(self, logged_in_page: Page) -> CibilPage:
        page_obj = CibilPage(logged_in_page)
        page_obj.go_to_my_tools()
        page_obj.open_tool()
        return page_obj

    @allure.story("CIBIL tool loads")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cibil_page_loads(self, logged_in_page: Page):
        """Opening the tool shows the PAN form and the 'no impact on score' note."""
        cibil = self._open(logged_in_page)
        expect(cibil.pan_input).to_be_visible()
        expect(cibil.no_impact_note).to_be_visible()

    @allure.story("Validation: Fetch requires a PAN")
    @allure.severity(allure.severity_level.NORMAL)
    def test_fetch_without_pan_shows_error(self, logged_in_page: Page):
        """Clicking Fetch with no PAN shows the 'valid 10-digit PAN' error."""
        cibil = self._open(logged_in_page)
        cibil.click_fetch()
        expect(cibil.toast("valid 10-digit PAN number")).to_be_visible()

    @allure.story("Validation: Fetch rejects a malformed PAN")
    @allure.severity(allure.severity_level.NORMAL)
    def test_fetch_invalid_pan_shows_error(self, logged_in_page: Page):
        """Fetching with a malformed PAN ('ABC') shows the PAN-format error."""
        cibil = self._open(logged_in_page)
        cibil.fill_pan("ABC")
        cibil.click_fetch()
        expect(cibil.toast("valid 10-digit PAN number")).to_be_visible()

    @allure.story("Fetch succeeds for a valid-format PAN")
    @allure.severity(allure.severity_level.NORMAL)
    def test_fetch_valid_pan_success(self, logged_in_page: Page):
        """Fetching with a valid-format PAN shows 'PAN details fetched successfully!'."""
        cibil = self._open(logged_in_page)
        cibil.fill_pan(CIBIL_DATA["pan"])
        cibil.click_fetch()
        expect(cibil.toast(Msg.FETCH_SUCCESS)).to_be_visible()

    @allure.story("Validation: Continue requires a PAN")
    @allure.severity(allure.severity_level.NORMAL)
    def test_continue_without_details_shows_pan_error(self, logged_in_page: Page):
        """Clicking Continue on an empty form shows a PAN-required error."""
        cibil = self._open(logged_in_page)
        cibil.click_continue()
        expect(cibil.toast("PAN number")).to_be_visible()

    @allure.story("Validation: First name is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_continue_without_first_name(self, logged_in_page: Page):
        """Continue with everything but a first name shows 'Please enter first name'."""
        cibil = self._open(logged_in_page)
        cibil.fill_pan(CIBIL_DATA["pan"])
        cibil.last_name_input.fill(CIBIL_DATA["last_name"])
        cibil.email_input.fill(CIBIL_DATA["email"])
        cibil.mobile_input.fill(CIBIL_DATA["mobile"])
        cibil.set_dob(CIBIL_DATA["dob_year"], CIBIL_DATA["dob_day"])
        cibil.click_continue()
        expect(cibil.toast(Msg.ERROR_FIRST_NAME)).to_be_visible()

    @allure.story("Validation: Email must be valid")
    @allure.severity(allure.severity_level.NORMAL)
    def test_continue_with_invalid_email(self, logged_in_page: Page):
        """Continue with a malformed email shows 'Please enter a valid email'."""
        cibil = self._open(logged_in_page)
        cibil.fill_pan(CIBIL_DATA["pan"])
        cibil.fill_details(CIBIL_DATA["first_name"], CIBIL_DATA["last_name"],
                           "not-an-email", CIBIL_DATA["mobile"])
        cibil.set_dob(CIBIL_DATA["dob_year"], CIBIL_DATA["dob_day"])
        cibil.click_continue()
        expect(cibil.toast(Msg.ERROR_EMAIL)).to_be_visible()

    @allure.story("Validation: Mobile must be 10 digits")
    @allure.severity(allure.severity_level.NORMAL)
    def test_continue_with_invalid_mobile(self, logged_in_page: Page):
        """Continue with a short mobile shows the 'valid 10-digit mobile' error."""
        cibil = self._open(logged_in_page)
        cibil.fill_pan(CIBIL_DATA["pan"])
        cibil.fill_details(CIBIL_DATA["first_name"], CIBIL_DATA["last_name"],
                           CIBIL_DATA["email"], "123")
        cibil.set_dob(CIBIL_DATA["dob_year"], CIBIL_DATA["dob_day"])
        cibil.click_continue()
        expect(cibil.toast(Msg.ERROR_MOBILE)).to_be_visible()

    @allure.story("Validation: Date of birth is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_continue_without_dob(self, logged_in_page: Page):
        """Continue with all fields but no DOB shows 'Please enter date of birth'."""
        cibil = self._open(logged_in_page)
        cibil.fill_pan(CIBIL_DATA["pan"])
        cibil.fill_details(CIBIL_DATA["first_name"], CIBIL_DATA["last_name"],
                           CIBIL_DATA["email"], CIBIL_DATA["mobile"])
        cibil.click_continue()
        expect(cibil.toast(Msg.ERROR_DOB)).to_be_visible()

    @allure.story("Date-of-birth picker sets a date")
    @allure.severity(allure.severity_level.NORMAL)
    def test_dob_picker_sets_date(self, logged_in_page: Page):
        """Selecting a year then a day fills the DOB field as dd/mm/yyyy."""
        cibil = self._open(logged_in_page)
        cibil.set_dob(1995, 15)
        expect(cibil.dob_input).to_have_value(re.compile(r"15/\d{2}/1995"))

    @allure.story("Valid form advances to the fulfilment step")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_full_form_advances_to_fulfilment_step(self, logged_in_page: Page):
        """A fully valid form advances to 'Would you like Ambak to fulfil this lead?'.
        (Stops before 'Create Lead & Get CIBIL', so no lead is created.)"""
        cibil = self._open(logged_in_page)
        cibil.fill_form_and_continue(CIBIL_DATA)
        expect(cibil.fulfilment_prompt).to_be_visible()
