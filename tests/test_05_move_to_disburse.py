import allure
import pytest
from datetime import datetime, timedelta
from playwright.sync_api import Page, expect
from pages.home_page import HomePage
from pages.lead_detail_page import LeadDetailPage
from pages.move_to_disburse_page import MoveToDisbursePage
from pages.schedule_followup_page import ScheduleFollowupPage
from config.config import MOVE_TO_DISBURSE_DATA, FOLLOWUP_DATA
from config.constants import MoveToDisburse as DisburseMsg
from utils.data_helper import generate_disburse_data


@allure.feature("Move To Disburse")
class TestMoveToDisburse:

    @pytest.fixture(autouse=True)
    def _stage_guard(self, disburse_stage_ready):
        """Skip this class fast when the lead never reached Sanctioned in this
        run, instead of every test independently burning a 45s timeout
        waiting on a 'Move To Disburse' button that cannot exist yet — this is
        exactly what happened on 2026-08-18 when test_04's sanction move
        failed and all five disburse tests still ran to their timeouts."""
        pass

    def _open_lead(self, logged_in_page: Page, disburse_lead_id: str):
        """Open the lead detail page in a new tab and return the page handle."""
        home = HomePage(logged_in_page)
        home.click_sanctioned_tab()
        home.search_lead(disburse_lead_id)
        return home.open_lead_in_new_tab(disburse_lead_id)

    def _open_followup(self, logged_in_page: Page, disburse_lead_id: str) -> ScheduleFollowupPage:
        """Open the lead detail page and open the Schedule Follow-up form directly."""
        lead_page = self._open_lead(logged_in_page, disburse_lead_id)
        followup = ScheduleFollowupPage(lead_page)
        followup.open_form()
        return followup

    def _open_form(self, logged_in_page: Page, disburse_lead_id: str) -> MoveToDisbursePage:
        lead_page = self._open_lead(logged_in_page, disburse_lead_id)
        LeadDetailPage(lead_page).click_move_to_disburse()
        return MoveToDisbursePage(lead_page)

    @allure.story("Pre-condition: Lead is present in Sanctioned tab")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_lead_present_in_sanctioned_tab(self, logged_in_page: Page, disburse_lead_id: str):
        """The lead must appear in the Sanctioned tab before it can be moved to Disburse."""
        home = HomePage(logged_in_page)
        home.click_sanctioned_tab()
        home.search_lead(disburse_lead_id)
        assert home.is_lead_present(disburse_lead_id), \
            f"Lead {disburse_lead_id} was not found in the Sanctioned tab"

    @allure.story("Validation: Loan Amount is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_move_to_disburse_without_loan_amount(self, logged_in_page: Page, disburse_lead_id: str):
        """Form should show amount/date error toast when Loan Amount is empty."""
        form = self._open_form(logged_in_page, disburse_lead_id)
        form.fill_and_submit({**MOVE_TO_DISBURSE_DATA, "loan_amount": ""})
        # Checked against the toasts _submit() already collected during its
        # own poll rather than a fresh expect() here — this toast auto-
        # dismisses within a few seconds and may already be gone by the time
        # fill_and_submit() returns control to this line.
        assert any(DisburseMsg.ERROR_AMOUNT_DATE in t for t in form.last_submit_toasts), (
            f"Expected a toast containing {DisburseMsg.ERROR_AMOUNT_DATE!r}; toasts "
            f"seen during submit: {form.last_submit_toasts}"
        )

    @allure.story("Validation: Disbursed ID is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_move_to_disburse_without_disbursed_id(self, logged_in_page: Page, disburse_lead_id: str, disburse_amount: str):
        """Form should show disbursement ID error toast when Disbursed ID is empty."""
        form = self._open_form(logged_in_page, disburse_lead_id)
        form.fill_and_submit({**MOVE_TO_DISBURSE_DATA, "loan_amount": disburse_amount, "disbursed_id": ""})
        assert any(DisburseMsg.ERROR_DISBURSED_ID in t for t in form.last_submit_toasts), (
            f"Expected a toast containing {DisburseMsg.ERROR_DISBURSED_ID!r}; toasts "
            f"seen during submit: {form.last_submit_toasts}"
        )

    @allure.story("Validation: Disbursal Date is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_move_to_disburse_without_disbursal_date(self, logged_in_page: Page, disburse_lead_id: str, disburse_amount: str):
        """Form should show amount/date error toast when Disbursal Date is not selected."""
        form = self._open_form(logged_in_page, disburse_lead_id)
        form.fill_and_submit({**MOVE_TO_DISBURSE_DATA, "loan_amount": disburse_amount, "select_disbursal_date": False})
        assert any(DisburseMsg.ERROR_AMOUNT_DATE in t for t in form.last_submit_toasts), (
            f"Expected a toast containing {DisburseMsg.ERROR_AMOUNT_DATE!r}; toasts "
            f"seen during submit: {form.last_submit_toasts}"
        )

    @allure.story("Validation: Amount cannot exceed sanctioned amount")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_move_to_disburse_amount_exceeds_sanction(self, logged_in_page: Page, disburse_lead_id: str):
        """Form should show error toast when disbursal amount exceeds the sanctioned amount.

        The exceeding amount is derived from the lead's *actual* sanctioned amount read
        off the detail page — not a fixture/.env value. This keeps the test correct whether
        it runs standalone (fixed .env lead) or chained after a freshly created lead, where
        the sanctioned amount differs and a hardcoded baseline would no longer 'exceed'.
        """
        lead_page = self._open_lead(logged_in_page, disburse_lead_id)
        detail = LeadDetailPage(lead_page)
        sanctioned_amount = detail.get_sanction_amount()
        # Belt-and-suspenders alongside get_sanction_amount()'s own guard: a
        # bogus '0' here would make exceeded_amount just '1', which the app
        # correctly accepts (it doesn't exceed anything) and actually
        # disburses the lead instead of exercising this validation.
        assert int(sanctioned_amount) > 0, (
            f"Cannot compute an 'exceeds sanction' amount: sanctioned_amount read "
            f"as {sanctioned_amount!r} for lead {disburse_lead_id}"
        )
        exceeded_amount = str(int(sanctioned_amount) + 1)
        detail.click_move_to_disburse()
        form = MoveToDisbursePage(lead_page)
        form.fill_and_submit({**generate_disburse_data(), "loan_amount": exceeded_amount})
        # Check the toast text _submit() already collected during its own poll
        # rather than a fresh expect() here — this toast, like the app's
        # others, auto-dismisses within a few seconds, and by the time
        # fill_and_submit() returns control to this line it may already be
        # gone, independent of whether the app actually showed it.
        assert any(DisburseMsg.ERROR_EXCEEDS in t for t in form.last_submit_toasts), (
            f"Expected a toast containing {DisburseMsg.ERROR_EXCEEDS!r}; toasts "
            f"seen during submit: {form.last_submit_toasts}"
        )

    @allure.story("Disbursal date: dates before sanction date are disabled")
    @allure.severity(allure.severity_level.NORMAL)
    def test_disbursal_dates_before_sanction_are_disabled(self, logged_in_page: Page, disburse_lead_id: str):
        """Dates before the lead's sanction date should be disabled in the disbursal date picker."""
        lead_page = self._open_lead(logged_in_page, disburse_lead_id)
        detail = LeadDetailPage(lead_page)
        sanction_date = detail.get_sanction_date()
        detail.click_move_to_disburse()
        form = MoveToDisbursePage(lead_page)
        day_before_sanction = sanction_date - timedelta(days=1)
        assert form.is_calendar_date_disabled(form.disbursal_date_input, day_before_sanction), \
            f"Expected {day_before_sanction.strftime('%Y-%m-%d')} (day before sanction date " \
            f"{sanction_date.strftime('%Y-%m-%d')}) to be disabled in the disbursal date picker"

    @allure.story("Follow-up: Validation: Date is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_followup_without_date(self, logged_in_page: Page, disburse_lead_id: str):
        """Submitting the Schedule Follow-up form without a date should show the date error."""
        followup = self._open_followup(logged_in_page, disburse_lead_id)
        followup.fill_and_submit({**FOLLOWUP_DATA, "pick_date": False})
        expect(followup.date_error).to_be_visible()

    @allure.story("Follow-up: Validation: Time is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_followup_without_time(self, logged_in_page: Page, disburse_lead_id: str):
        """Submitting the Schedule Follow-up form without a time should show the time error."""
        followup = self._open_followup(logged_in_page, disburse_lead_id)
        followup.fill_and_submit({**FOLLOWUP_DATA, "time": ""})
        expect(followup.time_error).to_be_visible()

    @allure.story("Follow-up: Validation: Comment is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_followup_without_comment(self, logged_in_page: Page, disburse_lead_id: str):
        """Submitting the Schedule Follow-up form without a comment should show the comment error."""
        followup = self._open_followup(logged_in_page, disburse_lead_id)
        followup.fill_and_submit({**FOLLOWUP_DATA, "comment": ""})
        expect(followup.comment_error).to_be_visible()

    @allure.story("Follow-up: Scheduled successfully and appears in list")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_followup_scheduled_successfully(self, logged_in_page: Page, disburse_lead_id: str):
        """Filling the Schedule Follow-up form completely and submitting should close
        the form and show the new entry in the Followups section."""
        followup = self._open_followup(logged_in_page, disburse_lead_id)
        followup.fill_and_submit(FOLLOWUP_DATA)
        expect(followup.followup_item).to_be_visible()

    @allure.story("Lead moved to Disburse stage successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_move_lead_to_disburse(self, logged_in_page: Page, disburse_lead_id: str, disburse_amount: str, shared_state):
        """Search for a lead in Sanctioned tab, open it, and move it to Disburse stage."""
        form = self._open_form(logged_in_page, disburse_lead_id)
        form.fill_and_submit({**generate_disburse_data(), "loan_amount": disburse_amount})
        expect(form.congratulations_popup).to_be_visible()
        shared_state["stage_reached"] = "disburse"
