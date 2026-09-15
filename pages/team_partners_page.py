import re
import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.constants import TeamPartners as Msg


class TeamPartnersPage(BasePage):
    """My Team — Channel Partner tab and the Business Partner add flow.

    The "+ Add Teammate" button opens a role picker ("Who do you want to add to
    your team?") offering Team Member, Sourcing Partner and Business Partner.
    Channel Partner is only a list tab — its add flow is the Sourcing Partner one
    (covered by the add-sourcing-partner tests).
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.add_button   = page.get_by_role("button", name="+ Add Teammate")
        self.picker_title = page.get_by_text("Who do you want to add", exact=False)
        self.role_team_member      = page.get_by_text(Msg.ROLE_TEAM_MEMBER, exact=True)
        self.role_sourcing_partner = page.get_by_text(Msg.ROLE_SOURCING_PARTNER, exact=True)
        self.role_business_partner = page.get_by_text(Msg.ROLE_BUSINESS_PARTNER, exact=True)

        # Business Partner form fields
        self.bp_full_name = page.get_by_placeholder("Full Name")
        self.bp_mobile    = page.get_by_placeholder("Mobile")
        self.bp_email     = page.get_by_placeholder("Email*")
        self.bp_pan       = page.get_by_placeholder("PAN Card Number")
        self.bp_submit    = page.locator("button.submitbtnnewlead")

        # Tabs
        self.channel_partner_tab  = page.locator("div.teamtab").filter(has_text=Msg.TAB_CHANNEL_PARTNER)
        self.business_partner_tab = page.locator("div.teamtab").filter(has_text=Msg.TAB_BUSINESS_PARTNER)

        # List search box ("search by name or id") — filters the team/partner
        # table shown on whichever tab is currently open.
        self.search_input   = self.healing_locator(
            page.get_by_placeholder("search by name or id"),
            name="search_input",
        )
        self.no_records_row = page.locator("table tbody tr").filter(has_text="No records found")

    def toast(self, text: str):
        return self.page.locator("[class*='Toastify__toast-body']").filter(has_text=text)

    @allure.step("Navigate to My Team")
    def go_to_my_team(self):
        self.page.get_by_role("link", name="teams My Team").click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Open the Add role picker")
    def open_add_picker(self):
        self.add_button.wait_for(state="visible")
        self.add_button.click()
        self.role_business_partner.wait_for(state="visible")

    @allure.step("Open the Business Partner form")
    def open_business_partner_form(self):
        self.open_add_picker()
        self.role_business_partner.click()
        self.bp_full_name.wait_for(state="visible")

    @allure.step("Fill Business Partner fields")
    def fill_business_partner(self, full_name: str, mobile: str, email: str):
        # PAN is intentionally NOT filled: the live form disables Submit whenever
        # the PAN field has a value (a known app-side validation bug), so a
        # successful submit is only possible without it.
        for field, value in ((self.bp_full_name, full_name),
                             (self.bp_mobile, mobile),
                             (self.bp_email, email)):
            field.click()
            field.fill(value)
            field.blur()
            self.page.wait_for_timeout(300)

    @allure.step("Select Channel Partner tab")
    def open_channel_partner_tab(self):
        self.channel_partner_tab.first.click()
        self.page.wait_for_timeout(1500)

    @allure.step("Search the team/partner list for {query}")
    def search(self, query: str):
        self.search_input.click()
        self.search_input.fill(query)
