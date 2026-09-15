import allure
import pytest
from playwright.sync_api import Page, expect
from pages.home_page import HomePage
from pages.lead_detail_page import LeadDetailPage
from pages.mark_as_lost_page import MarkAsLostPage
from config.config import MARK_AS_LOST_DATA


@allure.feature("Mark as Lost")
class TestMarkAsLost:

    def _open_form(self, logged_in_page: Page, lead_id: str) -> MarkAsLostPage:
        home = HomePage(logged_in_page)
        home.search_lead(lead_id)
        lead_page = home.open_lead_in_new_tab(lead_id)
        LeadDetailPage(lead_page).click_mark_as_lost()
        return MarkAsLostPage(lead_page)

    @allure.story("Validation: Reason is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_mark_as_lost_without_reason(self, logged_in_page: Page, mark_as_lost_lead_id: str):
        """Clicking Save without selecting a reason shows 'Please select reason'."""
        form = self._open_form(logged_in_page, mark_as_lost_lead_id)
        form.save_button.click()
        expect(form.error_toast_reason).to_be_visible()

    @allure.story("Validation: Comment is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_mark_as_lost_without_comment(self, logged_in_page: Page, mark_as_lost_lead_id: str):
        """Selecting a reason but leaving comment empty shows 'Please enter comment'."""
        form = self._open_form(logged_in_page, mark_as_lost_lead_id)
        form.select_reason(MARK_AS_LOST_DATA["reason"])
        form.save_button.click()
        expect(form.error_toast_comment).to_be_visible()

    @allure.story("Lead marked as lost successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_mark_lead_as_lost(self, logged_in_page: Page, mark_as_lost_lead_id: str, shared_state):
        """Open a pre-login lead, select a lost reason, add a comment, and save.

        On success, stash the now-lost lead in shared_state so the reopen tests
        (test_09b) reuse it in the same run — chaining mark-as-lost -> reopen."""
        form = self._open_form(logged_in_page, mark_as_lost_lead_id)
        form.fill_and_submit(MARK_AS_LOST_DATA)
        expect(form.success_toast).to_be_visible()
        shared_state["lost_lead_id"] = mark_as_lost_lead_id

    @allure.story("Mark lost -> reopen -> mark lost again all succeed")
    @allure.severity(allure.severity_level.NORMAL)
    def test_mark_lost_then_reopen_then_mark_lost_again(self, logged_in_page: Page, mark_lost_edge_case_lead_id: str):
        """Marking a lead lost, reopening it, then marking it lost a second
        time should succeed at every step — a lead's lost/active state should
        be freely reversible, not a one-way door. Uses its own self-seeded
        lead (mark_lost_edge_case_lead_id), not mark_as_lost_lead_id, so it
        doesn't disturb the lost lead test_09b's reopen tests depend on.
        Revived from
        tests/_scratch_explore.py::test_c_mark_lost_then_reopen_then_mark_lost_again,
        which only printed toast/button visibility at each step."""
        home = HomePage(logged_in_page)
        home.search_lead(mark_lost_edge_case_lead_id)
        lead_page = home.open_lead_in_new_tab(mark_lost_edge_case_lead_id)
        detail = LeadDetailPage(lead_page)
        detail.click_mark_as_lost()
        form = MarkAsLostPage(lead_page)
        form.fill_and_submit(MARK_AS_LOST_DATA)
        expect(form.success_toast).to_be_visible()

        lead_page.reload(wait_until="load")
        expect(detail.reopen_button).to_be_visible()
        detail.open_reopen()
        detail.fill_reopen_remarks("scratch reopen")
        detail.save_reopen()
        expect(detail.toast("Success")).to_be_visible()

        lead_page.reload(wait_until="load")
        expect(detail.mark_as_lost_button).to_be_visible()
        detail.click_mark_as_lost()
        form2 = MarkAsLostPage(lead_page)
        form2.fill_and_submit(MARK_AS_LOST_DATA)
        expect(form2.success_toast).to_be_visible()

    @allure.story("An oversized comment does not block the mark-lost submit")
    @allure.severity(allure.severity_level.MINOR)
    def test_mark_lost_long_comment_accepted(self, logged_in_page: Page, mark_lost_edge_case_lead_id: str):
        """A 5000-character comment should either be accepted as-is or
        truncated by the field, but must not silently block the submit.
        Runs on the same self-seeded lead as the reopen/re-lost test above —
        by this point it's already Lost, so this reopens it first (a plain
        precondition step, not itself under test) before re-marking it lost
        with the oversized comment. Revived from
        tests/_scratch_explore.py::test_d_mark_lost_long_comment, which only
        printed the toast/field state."""
        home = HomePage(logged_in_page)
        home.search_lead(mark_lost_edge_case_lead_id)
        lead_page = home.open_lead_in_new_tab(mark_lost_edge_case_lead_id)
        detail = LeadDetailPage(lead_page)
        detail.open_reopen()
        detail.fill_reopen_remarks("reopen for long-comment probe")
        detail.save_reopen()
        expect(detail.toast("Success")).to_be_visible()

        lead_page.reload(wait_until="load")
        detail.click_mark_as_lost()
        form = MarkAsLostPage(lead_page)
        long_comment = "A" * 5000
        form.fill_and_submit({**MARK_AS_LOST_DATA, "comment": long_comment})
        expect(form.success_toast).to_be_visible()
