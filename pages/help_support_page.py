import allure
from playwright.sync_api import Page
from pages.base_page import BasePage


class HelpSupportPage(BasePage):
    """Help & Support page — FAQs and Tickets tabs plus the Raise a Query entry point.

    FAQs and Tickets are <button> toggles (not role='tab'). Each FAQ question is a
    collapsible row; clicking it reveals its answer text.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.help_nav_link    = page.get_by_role("link", name="Help & Support")
        self.faqs_tab         = page.get_by_role("button", name="FAQs")
        self.tickets_tab      = page.get_by_role("button", name="Tickets")
        # 'Raise a Query' is a styled <div> (not a <button>), matched by exact text.
        self.raise_query_btn  = page.get_by_text("Raise a Query", exact=True)

    @allure.step("Navigate to Help & Support page")
    def go_to_help_support(self):
        self.help_nav_link.first.click()
        self.page.wait_for_url("**/help-support", timeout=30000)
        self.page.wait_for_load_state("networkidle")

    @allure.step("Open FAQs tab")
    def open_faqs(self):
        self.faqs_tab.click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Open Tickets tab")
    def open_tickets(self):
        self.tickets_tab.click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Toggle the first FAQ question")
    def toggle_first_faq(self):
        # The first FAQ renders expanded by default; clicking its question header
        # collapses it (and clicking again re-expands). Returns the answer locator
        # so callers can assert on its visibility before/after the toggle.
        first_q = self.page.get_by_text("How long will it take", exact=False).first
        first_q.click()
        self.page.wait_for_timeout(700)

    def first_faq_answer(self):
        return self.page.locator("p.accordionDetail").first

    @allure.step("Open the Raise a Query form")
    def open_raise_query(self):
        self.raise_query_btn.click()
        self.page.wait_for_load_state("networkidle")
