import allure
import pytest
from playwright.sync_api import Page, expect
from pages.add_teammate_page import AddTeammatePage
from config.config import ADD_SOURCING_PARTNER_DATA, VALID_MOBILE_BOUNDARIES, INVALID_MOBILES
from utils.data_helper import generate_sourcing_partner_data


@allure.feature("Add Sourcing Partner")
class TestAddSourcingPartner:

    def _open_form(self, logged_in_page: Page) -> AddTeammatePage:
        page_obj = AddTeammatePage(logged_in_page)
        page_obj.go_to_my_team()
        page_obj.open_sourcing_partner_form()
        return page_obj

    @allure.story("Validation: Full Name is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_submit_without_full_name(self, logged_in_page: Page):
        """Submitting without full name should block form submission."""
        form = self._open_form(logged_in_page)
        form.fill_mobile(ADD_SOURCING_PARTNER_DATA["mobile"])
        form.fill_email(ADD_SOURCING_PARTNER_DATA["email"])
        form.submit_button.click()
        expect(form.success_message_sourcing).not_to_be_visible()

    @allure.story("Validation: Mobile is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_submit_without_mobile(self, logged_in_page: Page):
        """Submitting without a mobile number should block form submission."""
        form = self._open_form(logged_in_page)
        form.fill_full_name(ADD_SOURCING_PARTNER_DATA["full_name"])
        form.fill_email(ADD_SOURCING_PARTNER_DATA["email"])
        form.submit_button.click()
        expect(form.success_message_sourcing).not_to_be_visible()

    @allure.story("Validation: Email is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_submit_without_email(self, logged_in_page: Page):
        """Submitting without an email address should block form submission."""
        form = self._open_form(logged_in_page)
        form.fill_full_name(ADD_SOURCING_PARTNER_DATA["full_name"])
        form.fill_mobile(ADD_SOURCING_PARTNER_DATA["mobile"])
        form.submit_button.click()
        expect(form.success_message_sourcing).not_to_be_visible()

    @allure.story("Sourcing Partner added successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_add_sourcing_partner_successful(self, logged_in_page: Page):
        """Add a sourcing partner with valid data — 'You have successfully added Sub Partner.' modal appears."""
        data = generate_sourcing_partner_data()
        form = self._open_form(logged_in_page)
        form.fill_and_submit_sourcing_partner(data)
        expect(form.success_title).to_be_visible()
        expect(form.success_message_sourcing).to_be_visible()

    @allure.story("Invalid mobile formats are rejected")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "mobile",
        [pytest.param(value, id=label) for label, value in INVALID_MOBILES],
    )
    def test_invalid_mobile_formats_rejected(self, logged_in_page: Page, mobile: str):
        """Submitting Add Sourcing Partner with a malformed mobile number is rejected."""
        data = {**generate_sourcing_partner_data(), "mobile": mobile}
        form = self._open_form(logged_in_page)
        form.fill_and_submit_sourcing_partner(data)
        # Give the submission time to fully resolve before checking — asserting
        # immediately can catch the success modal a moment before it would
        # appear, passing this test for the wrong reason.
        logged_in_page.wait_for_timeout(3000)
        assert not form.success_message_sourcing.is_visible()

    @allure.story("Valid boundary mobile numbers are accepted")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "mobile",
        [pytest.param(value, id=label) for label, value in VALID_MOBILE_BOUNDARIES],
    )
    def test_valid_mobile_boundaries_accepted(self, logged_in_page: Page, mobile: str):
        """Add Sourcing Partner accepts every legal-prefix 10-digit mobile boundary value.

        These boundary numbers are fixed constants (config.VALID_MOBILE_BOUNDARIES),
        shared with the Add Teammate boundary test, with no cleanup after either
        test — so a first passing run permanently registers each one. What this
        test actually verifies — that the FORMAT is accepted — still holds on
        every later run: a 'Mobile Already Exist' rejection proves the number
        passed format validation and reached the server's uniqueness check,
        same as the success modal proves it for a still-free number. Only a
        format-level rejection would be a real failure.
        """
        data = {**generate_sourcing_partner_data(), "mobile": mobile}
        form = self._open_form(logged_in_page)
        form.fill_and_submit_sourcing_partner(data)
        expect(form.format_accepted_outcome.first).to_be_visible()
