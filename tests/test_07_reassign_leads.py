import allure
import pytest
from playwright.sync_api import Page, expect
from pages.reassign_leads_page import ReassignLeadsPage
from config.config import REASSIGN_LEAD_DATA


@allure.feature("Reassign Leads")
class TestReassignLeads:

    @allure.story("Validation: Empty search returns no results")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_with_empty_text(self, logged_in_page: Page):
        """Clicking Search without entering any text should return no lead results."""
        r = ReassignLeadsPage(logged_in_page)
        r.open()
        r.search_type_trigger.click()
        logged_in_page.locator("[class*='-option']").first.click()
        r.search_button.click()
        expect(r.lead_results).to_have_count(0)

    @allure.story("Validation: Assign Lead is disabled when no lead is selected")
    @allure.severity(allure.severity_level.NORMAL)
    def test_assign_lead_disabled_without_lead_selected(self, logged_in_page: Page, reassign_lead_id: str):
        """Proceeding to the assignee panel without selecting a lead should
        leave the Assign Lead button in a disabled (cursor: not-allowed) state."""
        r = ReassignLeadsPage(logged_in_page)
        r.open()
        r.search_lead(reassign_lead_id)
        r.reassign_leads_button.click()
        expect(r.assign_lead_button).to_have_css("cursor", "not-allowed")

    @allure.story("Validation: Assign Lead is disabled when no assignee is selected")
    @allure.severity(allure.severity_level.NORMAL)
    def test_assign_lead_disabled_without_assignee_selected(self, logged_in_page: Page, reassign_lead_id: str):
        """Opening the assignee panel without checking any assignee should
        leave the Assign Lead button in a disabled (cursor: not-allowed) state."""
        r = ReassignLeadsPage(logged_in_page)
        r.open()
        r.search_lead(reassign_lead_id)
        logged_in_page.locator(f"#lead-{reassign_lead_id}").check()
        r.reassign_leads_button.click()
        expect(r.assign_lead_button).to_have_css("cursor", "not-allowed")

    @allure.story("Lead reassigned successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_reassign_lead_successfully(self, logged_in_page: Page, reassign_lead_id: str):
        """Search for a lead by ID via the Actions → Reassign Leads modal,
        select it, pick the assignee, and confirm the success toast appears."""
        r = ReassignLeadsPage(logged_in_page)
        r.open()
        r.search_lead(reassign_lead_id)
        r.reassign(reassign_lead_id, REASSIGN_LEAD_DATA["assignee_id"])
        expect(r.success_toast).to_be_visible()
