import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.config import BASE_URL


class ProfilePage(BasePage):
    """Partner profile (/my-account-profile).

    Tabs: Basic Details / KYC Documents / Bank Details. The Basic Details form
    holds the partner's company/SPOC details with a "Save and Next" button. The
    Logout control also lives on this page.

    NOTE: "Save and Next" stays disabled through automated field edits (a
    controlled-form quirk), so edit-and-save isn't reliably automatable — these
    cover the view/tabs and the logout entry point.
    """

    URL = BASE_URL.rstrip("/") + "/my-account-profile"

    def __init__(self, page: Page):
        super().__init__(page)
        self.profile_link  = page.get_by_role("link", name="View Profile")
        self.basic_details_tab = page.get_by_text("Basic Details", exact=True)
        self.kyc_documents_tab = page.get_by_text("KYC Documents", exact=True)
        self.bank_details_tab  = page.get_by_text("Bank Details", exact=True)
        self.save_and_next_button = page.get_by_role("button", name="Save and Next")
        # Representative Basic Details fields
        self.company_mobile = page.get_by_placeholder("Company Mobile Number*")
        self.spoc_name      = page.get_by_placeholder("SPOC Name*")
        self.pincode        = page.get_by_placeholder("Pin Code")
        # Logout is a header-menu link (<a href="/logout">) that is hidden until
        # the menu is opened; its route is the reliable entry point.
        self.logout_control = page.get_by_text("Logout", exact=True)
        self.logout_url = BASE_URL.rstrip("/") + "/logout"

    @allure.step("Open the profile page")
    def open(self):
        self.navigate(self.URL)
        self.page.wait_for_load_state("networkidle")
        self.save_and_next_button.wait_for(state="visible")

    @allure.step("Open KYC Documents tab")
    def open_kyc_tab(self):
        self.kyc_documents_tab.click()

    @allure.step("Open Bank Details tab")
    def open_bank_tab(self):
        self.bank_details_tab.click()

    @allure.step("Log out")
    def logout(self):
        """Trigger logout via its route (the header-menu Logout link points here
        and is otherwise hidden until the menu is expanded)."""
        self.navigate(self.logout_url)
        self.page.wait_for_load_state("networkidle")
