import allure
import pytest
from playwright.sync_api import Page, expect
from pages.home_page import HomePage
from pages.lead_detail_page import LeadDetailPage
from pages.move_to_login_page import MoveToLoginPage
from pages.schedule_followup_page import ScheduleFollowupPage
from config.config import MOVE_TO_LOGIN_DATA, FOLLOWUP_DATA
from utils.data_helper import generate_login_data


@allure.feature("Move To Login")
class TestMoveToLogin:

    # ── App regression: "Move To Login" is gone (2026-09-15) ───────────────
    # The "Move To Login" button no longer exists anywhere in the lead-detail
    # DOM for a Pre-Login lead — not hidden, not disabled, absent. Confirmed
    # from Playwright traces on two different freshly-created leads, both
    # loading cleanly (no network errors). Every button actually present:
    #   'Mark as lost'            class=markloatbrn
    #   'Remarks'                 class=logintomovebtn   <-- see warning below
    #   'Details'/'Documents'/'History'/'Confirmation' tabs
    #   'Raise Fulfillment Issue' class=editbtn (new)
    #   ''  (edit pencil)         class=editbtn
    # DO NOT "fix" this by pointing move_to_login_button at `.logintomovebtn`
    # — that class is now on the *Remarks* button. Doing so would click
    # Remarks instead and pass silently, hiding a real regression.
    # The 6 validation tests below plus test_move_lead_to_login are marked
    # known_bug/xfail(strict=True) until the app team confirms whether this
    # was intentional (progression moved into the new "Confirmation" tab) or
    # a regression. strict=True means a fix shows up as XPASS, not a silent
    # green — remove these marks once the button is confirmed restored.

    # Skip fast if test_02::test_create_lead_successful already ran this
    # session and failed to produce a lead — same pattern as
    # TestMoveToSanction/TestMoveToDisburse, so a broken Add New Lead form
    # costs one skip message per test instead of a 45s search timeout each.
    @pytest.fixture(autouse=True)
    def _stage_guard(self, login_stage_ready):
        pass

    def _open_lead(self, logged_in_page: Page, lead_id: str):
        """Open the lead detail page in a new tab and return the page handle."""
        home = HomePage(logged_in_page)
        home.click_pre_login_tab()
        home.search_lead(lead_id)
        return home.open_lead_in_new_tab(lead_id)

    def _open_followup(self, logged_in_page: Page, lead_id: str) -> ScheduleFollowupPage:
        """Open the lead detail page and open the Schedule Follow-up form directly."""
        lead_page = self._open_lead(logged_in_page, lead_id)
        followup = ScheduleFollowupPage(lead_page)
        followup.open_form()
        return followup

    def _open_form(self, logged_in_page: Page, lead_id: str) -> MoveToLoginPage:
        lead_page = self._open_lead(logged_in_page, lead_id)
        LeadDetailPage(lead_page).click_move_to_login()
        return MoveToLoginPage(lead_page)

    @allure.story("Pre-condition: Lead is present in Pre-Login tab")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_lead_present_in_pre_login_tab(self, logged_in_page: Page, lead_id: str):
        """The lead must appear in the Pre-Login tab before it can be moved to Login."""
        home = HomePage(logged_in_page)
        home.click_pre_login_tab()
        home.search_lead(lead_id)
        assert home.is_lead_present(lead_id), \
            f"Lead {lead_id} was not found in the Pre-Login tab"

    @allure.story("Validation: Loan Amount is required")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="the lead-detail page should offer 'Move To Login' for a "
                               "Pre-Login lead, but the button no longer exists in the DOM",
                        strict=True)
    def test_move_to_login_without_loan_amount(self, logged_in_page: Page, lead_id: str):
        """Form should show error toast when Loan Amount is empty."""
        form = self._open_form(logged_in_page, lead_id)
        form.fill_and_submit({**MOVE_TO_LOGIN_DATA, "loan_amount": ""})
        expect(form.error_toast_loan_amount).to_be_visible()

    @allure.story("Validation: Bank is required")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="the lead-detail page should offer 'Move To Login' for a "
                               "Pre-Login lead, but the button no longer exists in the DOM",
                        strict=True)
    def test_move_to_login_without_bank(self, logged_in_page: Page, lead_id: str, login_amount: str):
        """Form should show error toast when Bank is not selected."""
        form = self._open_form(logged_in_page, lead_id)
        form.fill_and_submit({**MOVE_TO_LOGIN_DATA, "loan_amount": login_amount, "bank_search": "", "bank_name": ""})
        expect(form.error_toast_bank).to_be_visible()

    @allure.story("Validation: Login ID is required")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="the lead-detail page should offer 'Move To Login' for a "
                               "Pre-Login lead, but the button no longer exists in the DOM",
                        strict=True)
    def test_move_to_login_without_login_id(self, logged_in_page: Page, lead_id: str, login_amount: str):
        """Form should show error toast when Login ID is empty."""
        form = self._open_form(logged_in_page, lead_id)
        form.fill_and_submit({**MOVE_TO_LOGIN_DATA, "loan_amount": login_amount, "login_id": ""})
        expect(form.error_toast_login_id).to_be_visible()

    @allure.story("Validation: Login Date is required")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="the lead-detail page should offer 'Move To Login' for a "
                               "Pre-Login lead, but the button no longer exists in the DOM",
                        strict=True)
    def test_move_to_login_without_date(self, logged_in_page: Page, lead_id: str, login_amount: str):
        """Form should show error toast when Login Date is not selected."""
        form = self._open_form(logged_in_page, lead_id)
        form.fill_and_submit({**MOVE_TO_LOGIN_DATA, "loan_amount": login_amount, "select_date": False})
        expect(form.error_toast_date).to_be_visible()

    @allure.story("Validation: Branch is required")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="the lead-detail page should offer 'Move To Login' for a "
                               "Pre-Login lead, but the button no longer exists in the DOM",
                        strict=True)
    def test_move_to_login_without_branch(self, logged_in_page: Page, lead_id: str, login_amount: str):
        """Form should show error toast when Branch is not selected."""
        form = self._open_form(logged_in_page, lead_id)
        form.fill_and_submit({**MOVE_TO_LOGIN_DATA, "loan_amount": login_amount, "branch": ""})
        expect(form.error_toast_branch).to_be_visible()

    @allure.story("Validation: Banker is required")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="the lead-detail page should offer 'Move To Login' for a "
                               "Pre-Login lead, but the button no longer exists in the DOM",
                        strict=True)
    def test_move_to_login_without_banker(self, logged_in_page: Page, lead_id: str, login_amount: str):
        """Form should show error toast when Banker is not selected."""
        form = self._open_form(logged_in_page, lead_id)
        form.fill_and_submit({**MOVE_TO_LOGIN_DATA, "loan_amount": login_amount, "banker": ""})
        expect(form.error_toast_banker).to_be_visible()

    @allure.story("Follow-up: Validation: Date is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_followup_without_date(self, logged_in_page: Page, lead_id: str):
        """Submitting the Schedule Follow-up form without a date should show the date error."""
        followup = self._open_followup(logged_in_page, lead_id)
        followup.fill_and_submit({**FOLLOWUP_DATA, "pick_date": False})
        expect(followup.date_error).to_be_visible()

    @allure.story("Follow-up: Validation: Time is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_followup_without_time(self, logged_in_page: Page, lead_id: str):
        """Submitting the Schedule Follow-up form without a time should show the time error."""
        followup = self._open_followup(logged_in_page, lead_id)
        followup.fill_and_submit({**FOLLOWUP_DATA, "time": ""})
        expect(followup.time_error).to_be_visible()

    @allure.story("Follow-up: Validation: Comment is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_followup_without_comment(self, logged_in_page: Page, lead_id: str):
        """Submitting the Schedule Follow-up form without a comment should show the comment error."""
        followup = self._open_followup(logged_in_page, lead_id)
        followup.fill_and_submit({**FOLLOWUP_DATA, "comment": ""})
        expect(followup.comment_error).to_be_visible()

    @allure.story("Follow-up: Scheduled successfully and appears in list")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_followup_scheduled_successfully(self, logged_in_page: Page, lead_id: str):
        """Filling the Schedule Follow-up form completely and submitting should close
        the form and show the new entry in the Followups section."""
        followup = self._open_followup(logged_in_page, lead_id)
        followup.fill_and_submit(FOLLOWUP_DATA)
        expect(followup.followup_item).to_be_visible()

    @allure.story("Lead moved to Login stage successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="the lead-detail page should offer 'Move To Login' for a "
                               "Pre-Login lead, but the button no longer exists in the DOM",
                        strict=True)
    def test_move_lead_to_login(self, logged_in_page: Page, lead_id: str, login_amount: str, shared_state):
        """Search for a lead, open it, and move it to Login stage."""
        form = self._open_form(logged_in_page, lead_id)
        form.fill_and_submit({**generate_login_data(), "loan_amount": login_amount})
        expect(form.success_toast).to_be_visible()
        # The success toast alone was proven unreliable in the 2026-08-18 run
        # (a later stage's success toast appeared while the lead had NOT
        # actually moved) — confirm the lead is really in the Logged In tab
        # before later stages build on it.
        home = HomePage(logged_in_page)
        home.click_logged_in_tab()
        home.search_lead(lead_id)
        assert home.is_lead_present(lead_id), \
            f"Lead {lead_id} was not found in the Logged In tab after a successful-looking submit"
        shared_state["stage_reached"] = "login"

    @allure.story("Bug: Back/forward navigation discards entered form data")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="typing a Loan Amount then navigating back/forward should leave the typed value intact, but the app silently discards it", strict=True)
    def test_back_forward_discards_entered_data_bug(self, logged_in_page: Page, back_forward_lead_id: str):
        """Documents a bug: entering a Loan Amount, then navigating back and
        forward, should leave the typed value intact, but the app silently
        discards it."""
        # A fresh, self-seeded lead (not the shared lead_id) — test_move_lead_to_login
        # runs immediately before this in file order and moves the shared lead
        # out of Pre-Login, which previously starved this test's search and made
        # it time out before ever reaching the assertion below.
        form = self._open_form(logged_in_page, back_forward_lead_id)
        # The Move To Login form is a real route (confirmed live: opening it
        # pushes a history entry), not a modal — so back()/forward() must act
        # on the FORM'S OWN page, not the dashboard tab (logged_in_page), and
        # must actually change the URL, or this test can pass vacuously
        # without ever exercising the documented bug.
        form_page = form.page
        url_before = form_page.url
        assert form_page.evaluate("history.length") > 1, (
            "Move To Login form has no back-history — back()/forward() cannot "
            "exercise the documented bug on this page"
        )
        typed_amount = "1234567"
        form.fill_loan_amount(typed_amount)
        form_page.go_back()
        assert form_page.url != url_before, "go_back() did not navigate away from the form"
        form_page.go_forward()
        assert form_page.url == url_before, "go_forward() did not return to the form"
        assert typed_amount in form.loan_amount_input.input_value()
