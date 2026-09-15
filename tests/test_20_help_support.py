import allure
from playwright.sync_api import Page, expect
from pages.help_support_page import HelpSupportPage


@allure.feature("Help & Support")
class TestHelpSupport:

    @allure.story("Help & Support page loads with FAQs / Tickets tabs")
    @allure.severity(allure.severity_level.NORMAL)
    def test_help_page_loads(self, logged_in_page: Page):
        """Help & Support opens from the nav menu and shows FAQs, Tickets and Raise a Query."""
        h = HelpSupportPage(logged_in_page)
        h.go_to_help_support()
        expect(h.faqs_tab).to_be_visible()
        expect(h.tickets_tab).to_be_visible()
        expect(h.raise_query_btn.first).to_be_visible()

    @allure.story("FAQs tab lists frequently asked questions")
    @allure.severity(allure.severity_level.NORMAL)
    def test_faqs_tab_lists_questions(self, logged_in_page: Page):
        """The FAQs tab renders the list of FAQ questions."""
        h = HelpSupportPage(logged_in_page)
        h.go_to_help_support()
        h.open_faqs()
        expect(logged_in_page.get_by_text("How long will it take", exact=False).first).to_be_visible()

    @allure.story("FAQ accordion toggles its answer open and closed")
    @allure.severity(allure.severity_level.NORMAL)
    def test_faq_accordion_toggles(self, logged_in_page: Page):
        """The first FAQ shows its answer by default; clicking the question collapses it."""
        h = HelpSupportPage(logged_in_page)
        h.go_to_help_support()
        h.open_faqs()
        answer = h.first_faq_answer()
        expect(answer).to_be_visible()   # expanded by default
        h.toggle_first_faq()
        expect(answer).to_be_hidden()    # collapses on click

    @allure.story("Tickets tab loads the support contact view")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tickets_tab_loads(self, logged_in_page: Page):
        """The Tickets tab renders the Ambak support contact section."""
        h = HelpSupportPage(logged_in_page)
        h.go_to_help_support()
        h.open_tickets()
        expect(logged_in_page.get_by_text("Reach out to Ambak", exact=False).first).to_be_visible()
