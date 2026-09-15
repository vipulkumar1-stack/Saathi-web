import allure
import pytest
from playwright.sync_api import Page, expect
from pages.add_teammate_page import AddTeammatePage
from config.config import ADD_TEAMMATE_DATA, ADD_SOURCING_PARTNER_DATA, LEAD_DATA, LOGIN_MOBILE, VALID_MOBILE_BOUNDARIES, INVALID_MOBILES
from utils.data_helper import generate_teammate_data


@allure.feature("Add Teammate")
class TestAddTeammate:

    def _open_form(self, logged_in_page: Page) -> AddTeammatePage:
        page_obj = AddTeammatePage(logged_in_page)
        page_obj.go_to_my_team()
        page_obj.open_form()
        return page_obj

    def _create_teammate(self, logged_in_page: Page, form: AddTeammatePage, attempts: int = 3) -> dict:
        """Submit a fresh random teammate, retrying with new random data if the
        submission is rejected for a reason unrelated to what the caller is
        actually testing (seen live: a freshly-generated random mobile can hit
        a transient server-side "Incorrect Referral Code" 400, even though the
        identical form flow succeeds moments later with different random data).

        On a rejection, reload() is used to recover — confirmed live that a
        stuck "Add Team Member" modal is reliably cleared this way, whereas the
        modal's own close icon overlaps a menu-close icon with the same glyph
        and is not a safe target to click blindly. Returns the data that was
        actually accepted.
        """
        last_error = None
        for attempt in range(attempts):
            data = generate_teammate_data()
            form.fill_and_submit(data)
            try:
                expect(form.success_title).to_be_visible(timeout=8000)
                expect(form.success_message).to_be_visible()
                return data
            except AssertionError as exc:
                last_error = exc
                if attempt < attempts - 1:
                    logged_in_page.reload(wait_until="domcontentloaded")
                    logged_in_page.wait_for_timeout(1500)
                    form.open_form()
        raise AssertionError(
            f"Could not create a seed teammate after {attempts} attempts: {last_error}"
        )

    @allure.story("Validation: Full Name is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_submit_without_full_name(self, logged_in_page: Page):
        """Submitting without full name should block form submission."""
        form = self._open_form(logged_in_page)
        form.fill_mobile(ADD_TEAMMATE_DATA["mobile"])
        form.select_designation()
        form.submit_button.click()
        expect(form.success_message).not_to_be_visible()

    @allure.story("Validation: Mobile is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_submit_without_mobile(self, logged_in_page: Page):
        """Submitting without a mobile number should block form submission."""
        form = self._open_form(logged_in_page)
        form.fill_full_name(ADD_TEAMMATE_DATA["full_name"])
        form.select_designation()
        form.submit_button.click()
        expect(form.success_message).not_to_be_visible()

    @allure.story("Validation: Designation is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_submit_without_designation(self, logged_in_page: Page):
        """Submitting without selecting a designation should block form submission."""
        form = self._open_form(logged_in_page)
        form.fill_full_name(ADD_TEAMMATE_DATA["full_name"])
        form.fill_mobile(ADD_TEAMMATE_DATA["mobile"])
        form.submit_button.click()
        expect(form.success_message).not_to_be_visible()

    @allure.story("Teammate added successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_add_teammate_successful(self, logged_in_page: Page):
        """Add a teammate with valid data — 'You have Successfully Added Team Member.' modal appears."""
        data = generate_teammate_data()
        form = self._open_form(logged_in_page)
        form.fill_and_submit(data)
        expect(form.success_title).to_be_visible()
        expect(form.success_message).to_be_visible()

    @allure.story("Duplicate mobile number is rejected")
    @allure.severity(allure.severity_level.NORMAL)
    def test_duplicate_teammate_mobile_rejected(self, logged_in_page: Page):
        """Creating a second teammate reusing an already-registered mobile number is rejected."""
        form = self._open_form(logged_in_page)
        data = self._create_teammate(logged_in_page, form)
        form.go_to_team_list_btn.click()
        logged_in_page.wait_for_timeout(3000)

        dup_data = {**generate_teammate_data(), "mobile": data["mobile"]}
        form.open_form()
        form.fill_and_submit(dup_data)
        # Give the submission time to fully resolve before checking — asserting
        # immediately can catch the success modal a moment before it would (or
        # wouldn't) appear, passing this test for the wrong reason.
        logged_in_page.wait_for_timeout(3000)
        assert not form.success_message.is_visible()
        assert form.mobile_exists_error.is_visible()

    @allure.story("Invalid mobile formats are rejected")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "mobile",
        [pytest.param(value, id=label) for label, value in INVALID_MOBILES],
    )
    def test_invalid_mobile_formats_rejected(self, logged_in_page: Page, mobile: str):
        """Submitting Add Teammate with a malformed mobile number is rejected."""
        data = {**generate_teammate_data(), "mobile": mobile}
        form = self._open_form(logged_in_page)
        form.fill_and_submit(data)
        # Give the submission time to fully resolve before checking — asserting
        # immediately can catch the success modal a moment before it would
        # appear, passing this test for the wrong reason.
        logged_in_page.wait_for_timeout(3000)
        assert not form.success_message.is_visible()

    @allure.story("Valid boundary mobile numbers are accepted")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "mobile",
        [pytest.param(value, id=label) for label, value in VALID_MOBILE_BOUNDARIES],
    )
    def test_valid_mobile_boundaries_accepted(self, logged_in_page: Page, mobile: str):
        """Add Teammate accepts every legal-prefix 10-digit mobile boundary value.

        These boundary numbers are fixed constants (config.VALID_MOBILE_BOUNDARIES)
        with no cleanup after the test, so a first passing run permanently
        registers each one. What this test actually verifies — that the FORMAT
        is accepted — still holds on every later run: a 'Mobile Already Exist'
        rejection proves the number passed format validation and reached the
        server's uniqueness check, same as the success modal proves it for a
        still-free number. Only a format-level rejection would be a real failure.
        """
        data = {**generate_teammate_data(), "mobile": mobile}
        form = self._open_form(logged_in_page)
        form.fill_and_submit(data)
        expect(form.format_accepted_outcome.first).to_be_visible()
