import allure
from playwright.sync_api import Page
from pages.base_page import BasePage


class ReassignLeadsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.actions_button        = page.get_by_role("button", name="Actions")
        self.reassign_leads_item   = page.get_by_text("Reassign Leads")
        self.search_type_trigger   = page.get_by_text("Search Type")
        self.search_text_input     = page.get_by_role("textbox", name="Search Text")
        self.search_button         = page.get_by_role("button", name="Search")
        self.lead_results          = page.locator("[id^='lead-']")
        self.reassign_leads_button = page.get_by_role("button", name="Re-assign Leads")
        self.assign_lead_button    = page.get_by_role("button", name="Assign Lead", exact=True)
        self.success_toast         = page.get_by_text("Data updated in the system")

    @allure.step("Open Reassign Leads modal")
    def open(self):
        self.actions_button.click()
        self.reassign_leads_item.click()
        self.search_type_trigger.wait_for(state="visible")

    @allure.step("Search for lead {lead_id}")
    def search_lead(self, lead_id: str):
        self.search_type_trigger.click()
        self.choose_first_option()
        self.search_text_input.fill(lead_id)
        self.search_button.click()
        self.page.locator(f"#lead-{lead_id}").wait_for(state="visible")

    @allure.step("Select lead and reassign to assignee {assignee_id}")
    def reassign(self, lead_id: str, assignee_id: str):
        self.page.locator(f"#lead-{lead_id}").check()
        self.reassign_leads_button.click()
        self.page.locator(f"#re_assign_{assignee_id}").check()
        self.assign_lead_button.click()
