import allure
from playwright.sync_api import Page
from pages.base_page import BasePage


class SearchFilterPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Date filter — the "Created Date" control is a react-select dropdown whose
        # placeholder div carries the text. Matching [class*='placeholder'] targets it
        # regardless of the build-hash suffix and excludes the p-column-title span in
        # the data table (which also reads "Created Date" but has no 'placeholder' class).
        self.date_filter_button = page.locator("[class*='placeholder']").filter(has_text="Created Date")
        # City filter
        self.city_filter_button = page.get_by_role("button", name="City")
        self.city_search_input  = page.get_by_role("textbox", name="Search City")
        # Bank filter
        self.bank_filter_button = page.get_by_role("button", name="Bank")
        self.bank_search_input  = page.get_by_role("textbox", name="Search Bank")
        # Anchor — always visible on the leads page regardless of filter results
        self.search_box         = page.get_by_role("textbox", name="Search by id or name...")
        # Leads count badge — the "(N)" span rendered inside the "All Leads" tab.
        # Reused as the live result count after a search (same element the
        # advanced-filters flow reads via HomePage.all_leads_count()).
        self.leads_count_badge = self.healing_locator(
            page.locator("div.teamtab", has_text="All Leads").locator("span"),
            page.locator("div.teamtab", has_text="All Leads"),
            name="leads_count_badge",
        )

    @allure.step("Apply date filter: {option}")
    def apply_date_filter(self, option: str = "Yesterday"):
        self.date_filter_button.wait_for(state="visible")
        self.date_filter_button.click()
        self.page.get_by_text(option, exact=True).click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Apply city filter: {city}")
    def apply_city_filter(self, search: str, city: str):
        self.city_filter_button.wait_for(state="visible")
        self.city_filter_button.click()
        self.city_search_input.wait_for(state="visible")
        self.city_search_input.fill(search)
        self.page.get_by_text(city, exact=True).click()
        # .filter-checkbox-custom is a custom widget — no ARIA role is set by the
        # frontend. First visible instance is always the selected city's checkbox.
        # TODO: ask frontend team to add role="checkbox" + aria-label to this element.
        self.page.locator(".filter-checkbox-custom").first.click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Apply bank filter: {search}")
    def apply_bank_filter(self, search: str):
        self.bank_filter_button.wait_for(state="visible")
        self.bank_filter_button.click()
        self.bank_search_input.wait_for(state="visible")
        self.bank_search_input.fill(search)
        # nth-child(2) skips the header row — first result is always the matched bank.
        # TODO: ask frontend team to add role="checkbox" + aria-label to make this semantic.
        self.page.locator(".filter-checkbox-custom").nth(1).click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Search leads for: {query}")
    def search(self, query: str):
        """Type into the leads search box and submit with Enter. Caller is
        responsible for waiting afterward — the app re-renders the table and
        the "All Leads (N)" badge asynchronously, and (for zero-result
        queries) can even remove/disable the search box itself, so a fixed
        wait here would either be too short or mask that exact behavior."""
        self.search_box.wait_for(state="visible")
        self.search_box.click()
        self.search_box.fill(query)
        self.search_box.press("Enter")
