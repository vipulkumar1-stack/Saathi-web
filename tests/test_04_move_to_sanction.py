import allure
import pytest
from datetime import datetime, timedelta
from playwright.sync_api import Page, expect
from pages.home_page import HomePage
from pages.lead_detail_page import LeadDetailPage
from pages.move_to_sanction_page import MoveToSanctionPage
from pages.schedule_followup_page import ScheduleFollowupPage
from config.config import MOVE_TO_SANCTION_DATA, FOLLOWUP_DATA
from config.constants import MoveToSanction as SanctionMsg
from utils.data_helper import generate_sanction_data


@allure.feature("Move To Sanction")
class TestMoveToSanction:

    @pytest.fixture(autouse=True)
    def _stage_guard(self, sanction_stage_ready):
        """Skip this class fast (instead of each test independently hanging
        on a button/tab that can't exist) when the lead never reached Logged
        In in this run — only applies to a chained run off the test_02
        lifecycle lead; a standalone .env-lead run is unaffected."""
        pass

    def _open_lead(self, logged_in_page: Page, sanction_lead_id: str):
        """Open the lead detail page in a new tab and return the page handle."""
        home = HomePage(logged_in_page)
        home.click_logged_in_tab()
        home.search_lead(sanction_lead_id)
        return home.open_lead_in_new_tab(sanction_lead_id)

    def _open_followup(self, logged_in_page: Page, sanction_lead_id: str) -> ScheduleFollowupPage:
        """Open the lead detail page and open the Schedule Follow-up form directly."""
        lead_page = self._open_lead(logged_in_page, sanction_lead_id)
        followup = ScheduleFollowupPage(lead_page)
        followup.open_form()
        return followup

    def _open_form(self, logged_in_page: Page, sanction_lead_id: str) -> MoveToSanctionPage:
        lead_page = self._open_lead(logged_in_page, sanction_lead_id)
        LeadDetailPage(lead_page).click_move_to_sanction()
        return MoveToSanctionPage(lead_page)

    @allure.story("Pre-condition: Lead is present in Logged In tab")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_lead_present_in_logged_in_tab(self, logged_in_page: Page, sanction_lead_id: str):
        """The lead must appear in the Logged In tab before it can be moved to Sanction."""
        home = HomePage(logged_in_page)
        home.click_logged_in_tab()
        home.search_lead(sanction_lead_id)
        assert home.is_lead_present(sanction_lead_id), \
            f"Lead {sanction_lead_id} was not found in the Logged In tab"

    @allure.story("Validation: Loan Amount is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_move_to_sanction_without_loan_amount(self, logged_in_page: Page, sanction_lead_id: str):
        """Form should not submit when Loan Amount is empty."""
        form = self._open_form(logged_in_page, sanction_lead_id)
        form.fill_and_submit({**MOVE_TO_SANCTION_DATA, "loan_amount": ""})
        # Positive assertion (confirmed live on 2026-08-18) instead of only
        # `not_to_be_visible()` on success — that alone passes whenever the
        # form is broken for ANY reason, which is exactly how the sanction
        # cascade on the same day went unnoticed for three tests in a row.
        # Checked against the toasts _submit() already collected during its
        # own poll (rather than a fresh expect() here) since this toast, like
        # the app's others, auto-dismisses within a few seconds and may
        # already be gone by the time fill_and_submit() returns.
        assert SanctionMsg.ERROR_LOAN_AMOUNT in form.last_submit_toasts, (
            f"Expected {SanctionMsg.ERROR_LOAN_AMOUNT!r}; toasts seen during "
            f"submit: {form.last_submit_toasts}"
        )
        expect(form.success_toast).not_to_be_visible()

    @allure.story("Validation: Sanction ID is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_move_to_sanction_without_sanction_id(self, logged_in_page: Page, sanction_lead_id: str, sanction_amount: str):
        """Form should not submit when Sanction ID is empty."""
        form = self._open_form(logged_in_page, sanction_lead_id)
        form.fill_and_submit({**MOVE_TO_SANCTION_DATA, "loan_amount": sanction_amount, "sanction_id": ""})
        # No distinguishable toast for this omission was captured live (it
        # either doesn't render one or dismisses too fast to catch) — confirmed
        # instead, live, that the submit genuinely does not go through: no
        # success toast AND the lead does not reach Sanctioned.
        expect(form.success_toast).not_to_be_visible()
        home = HomePage(logged_in_page)
        home.click_sanctioned_tab()
        assert not home.is_lead_present(sanction_lead_id, timeout=5000), \
            f"Lead {sanction_lead_id} reached Sanctioned despite an empty Sanction ID"

    @allure.story("Validation: Sanction Date is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_move_to_sanction_without_date(self, logged_in_page: Page, sanction_lead_id: str, sanction_amount: str):
        """Form should not submit when Sanction Date is not selected."""
        form = self._open_form(logged_in_page, sanction_lead_id)
        form.fill_and_submit({**MOVE_TO_SANCTION_DATA, "loan_amount": sanction_amount, "select_date": False})
        # Same as the Sanction ID case above: no distinguishable toast was
        # captured live, so this asserts the confirmed real outcome (no
        # success, lead does not reach Sanctioned) rather than success-absence
        # alone.
        expect(form.success_toast).not_to_be_visible()
        home = HomePage(logged_in_page)
        home.click_sanctioned_tab()
        assert not home.is_lead_present(sanction_lead_id, timeout=5000), \
            f"Lead {sanction_lead_id} reached Sanctioned despite no Sanction Date selected"

    @allure.story("Validation: non-numeric Loan Amount does not submit")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sanction_non_numeric_amount_rejected(self, logged_in_page: Page, sanction_lead_id: str):
        """Entering non-numeric text into Sanction Amount should not submit —
        same 'no distinguishable toast' pattern as the missing-ID/date cases:
        confirm the real outcome (no success, lead stays out of Sanctioned)
        rather than trusting success-absence alone. Revived from
        tests/_scratch_explore.py::test_a_sanction_non_numeric_amount, which
        only printed the observed field value/toast state."""
        form = self._open_form(logged_in_page, sanction_lead_id)
        form.fill_and_submit({**generate_sanction_data(), "loan_amount": "abcdef"})
        expect(form.success_toast).not_to_be_visible()
        home = HomePage(logged_in_page)
        home.click_sanctioned_tab()
        assert not home.is_lead_present(sanction_lead_id, timeout=5000), \
            f"Lead {sanction_lead_id} reached Sanctioned despite a non-numeric Sanction Amount"

    @allure.story("Sanction date: dates before login date are disabled")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sanction_dates_before_login_are_disabled(self, logged_in_page: Page, sanction_lead_id: str):
        """Dates before the lead's login date should be disabled in the sanction date picker."""
        lead_page = self._open_lead(logged_in_page, sanction_lead_id)
        detail = LeadDetailPage(lead_page)
        login_date = detail.get_login_date()
        detail.click_move_to_sanction()
        form = MoveToSanctionPage(lead_page)
        day_before_login = login_date - timedelta(days=1)
        assert form.is_calendar_date_disabled(form.login_date_input, day_before_login), \
            f"Expected {day_before_login.strftime('%Y-%m-%d')} (day before login date " \
            f"{login_date.strftime('%Y-%m-%d')}) to be disabled in the sanction date picker"

    @allure.story("Follow-up: Validation: Date is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_followup_without_date(self, logged_in_page: Page, sanction_lead_id: str):
        """Submitting the Schedule Follow-up form without a date should show the date error."""
        followup = self._open_followup(logged_in_page, sanction_lead_id)
        followup.fill_and_submit({**FOLLOWUP_DATA, "pick_date": False})
        expect(followup.date_error).to_be_visible()

    @allure.story("Follow-up: Validation: Time is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_followup_without_time(self, logged_in_page: Page, sanction_lead_id: str):
        """Submitting the Schedule Follow-up form without a time should show the time error."""
        followup = self._open_followup(logged_in_page, sanction_lead_id)
        followup.fill_and_submit({**FOLLOWUP_DATA, "time": ""})
        expect(followup.time_error).to_be_visible()

    @allure.story("Follow-up: Validation: Comment is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_followup_without_comment(self, logged_in_page: Page, sanction_lead_id: str):
        """Submitting the Schedule Follow-up form without a comment should show the comment error."""
        followup = self._open_followup(logged_in_page, sanction_lead_id)
        followup.fill_and_submit({**FOLLOWUP_DATA, "comment": ""})
        expect(followup.comment_error).to_be_visible()

    @allure.story("Follow-up: Scheduled successfully and appears in list")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_followup_scheduled_successfully(self, logged_in_page: Page, sanction_lead_id: str):
        """Filling the Schedule Follow-up form completely and submitting should close
        the form and show the new entry in the Followups section."""
        followup = self._open_followup(logged_in_page, sanction_lead_id)
        followup.fill_and_submit(FOLLOWUP_DATA)
        expect(followup.followup_item).to_be_visible()

    @allure.story("Lead moved to Sanction stage successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_move_lead_to_sanction(self, logged_in_page: Page, sanction_lead_id: str, sanction_amount: str, shared_state):
        """Search for a lead in Logged In tab, open it, and move it to Sanction stage."""
        form = self._open_form(logged_in_page, sanction_lead_id)
        form.fill_and_submit({**generate_sanction_data(), "loan_amount": sanction_amount})
        expect(form.success_toast).to_be_visible()
        # A toast alone was proven unreliable in the 2026-08-18 run: the lead
        # stayed in Logged In (Sanctioned tab empty) while a rerun of the
        # tab-membership check still reported a pass. Confirm the lead is
        # really in the Sanctioned tab before test_05 builds on it.
        home = HomePage(logged_in_page)
        home.click_sanctioned_tab()
        home.search_lead(sanction_lead_id)
        assert home.is_lead_present(sanction_lead_id), \
            f"Lead {sanction_lead_id} was not found in the Sanctioned tab after a successful-looking submit"
        shared_state["stage_reached"] = "sanction"

    @allure.story("Bug-check: an already-sanctioned lead cannot be re-sanctioned")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sanction_button_gone_after_already_sanctioned(self, logged_in_page: Page, sanction_lead_id: str):
        """Once a lead is sanctioned, its detail page should offer 'Move To
        Disburse' next, not still offer 'Move To Sanction' — reopening the
        detail page for the now-sanctioned lead must not expose a way to
        resubmit the sanction form. Runs after test_move_lead_to_sanction so
        the lead is already past this stage. Revived from
        tests/_scratch_explore.py::test_b_sanction_resubmit_twice, which only
        printed whether the button was clickable again."""
        home = HomePage(logged_in_page)
        home.click_sanctioned_tab()
        home.search_lead(sanction_lead_id)
        lead_page = home.open_lead_in_new_tab(sanction_lead_id)
        detail = LeadDetailPage(lead_page)
        detail._wait_for_stage_button(detail.move_to_disburse_button, "Move To Disburse")
        expect(detail.move_to_sanction_button).not_to_be_visible()
