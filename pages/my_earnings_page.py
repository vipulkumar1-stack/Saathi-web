import re
import allure
from playwright.sync_api import Page
from pages.base_page import BasePage


class MyEarningsPage(BasePage):
    """My Earnings page — Projected / Earned / Paid tabs and the keyword search filter.

    Tabs are plain clickable text (no role='tab'), so they are matched by exact
    visible text. The search panel reuses the app-wide React Select control
    (label 'Search Type') plus a keyword textbox and Search / Reset buttons.
    """

    TABS = ("Projected", "Earned", "Paid")

    def __init__(self, page: Page):
        super().__init__(page)
        self.earnings_nav_link = page.get_by_role("link", name="My Earnings")
        self.search_type_button = page.get_by_role("button", name="Search By")
        self.keyword_input     = page.get_by_placeholder("Enter Keyword")
        self.search_button     = page.get_by_role("button", name="Search", exact=True)
        self.reset_button      = page.get_by_role("button", name="Reset")
        self.results_table     = page.locator("table")

    @allure.step("Navigate to My Earnings page")
    def go_to_my_earnings(self):
        self.earnings_nav_link.first.click()
        self.page.wait_for_url("**/my-saathi-earnings", timeout=30000)
        self.page.wait_for_load_state("networkidle")
        self._wait_for_table()

    def _wait_for_table(self):
        # The grid re-renders on every tab switch / filter apply. Waiting for at
        # least one body row is the end-to-end signal that data has loaded.
        self.page.wait_for_selector("table tbody tr", timeout=15000)

    @allure.step("Switch to {tab} tab")
    def open_tab(self, tab: str):
        self.page.get_by_text(tab, exact=True).first.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_table()

    @allure.step("Read first Lead ID from the earnings table")
    def get_first_lead_id(self) -> str:
        self._wait_for_table()
        first_row = self.page.locator("table tbody tr").first
        for cell in first_row.locator("td").all():
            text = cell.inner_text().strip()
            if text.isdigit():
                return text
        return first_row.locator("td").first.inner_text().strip()

    def row_count(self) -> int:
        return self.page.locator("table tbody tr").count()

    @allure.step("Search earnings by Lead ID: {lead_id}")
    def search_by_lead_id(self, lead_id: str):
        # The 'Search By' control reveals two options rendered as
        # <label class='filter-opts-label'> ('Customer Name' / 'Lead ID').
        # Choosing 'Lead ID' surfaces the keyword box the grid filters on.
        self.search_type_button.click()
        # Let the options panel render, then commit the 'Lead ID' choice. A brief
        # settle after each step is needed — the grid binds the chosen search type
        # asynchronously, and filling/searching before it commits silently falls
        # back to the default type and returns the unfiltered list.
        self.page.wait_for_timeout(800)
        self.page.locator("label.filter-opts-label").filter(
            has_text=re.compile(r"^Lead ID$")
        ).click()
        self.page.wait_for_timeout(500)
        self.keyword_input.wait_for(state="visible")
        self.keyword_input.fill(lead_id)
        self.search_button.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(800)

    @allure.step("Reset the earnings search filter")
    def reset_filter(self):
        self.reset_button.click()
        self.page.wait_for_load_state("networkidle")
        # The grid repopulates the full list a beat after the network settles;
        # pause so callers read the restored rows, not the pre-reset view.
        self.page.wait_for_timeout(1500)
        self._wait_for_table()
