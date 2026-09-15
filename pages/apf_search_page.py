import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.constants import ApfSearch as Msg


class ApfSearchPage(BasePage):
    """APF Search Engine ("APF Finder", /apf-search).

    Opened from My Tools via the "APF Search Engine" card. A city react-select
    scopes the search; a text box searches builders/projects and results render
    in a BUILDER / PROJECT / BANK / ACTION table. This is a read-only search
    tool, so all flows here are non-mutating.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.check_now_button = (
            page.locator("div")
            .filter(has=page.get_by_text("APF Search Engine", exact=True))
            .filter(has=page.get_by_role("button", name="Check Now"))
            .last
            .get_by_role("button", name="Check Now")
        )
        self.heading      = page.get_by_text(Msg.PAGE_HEADING, exact=True)
        self.search_input = page.locator("#search")
        self.result_rows  = page.locator("tbody tr")
        # City react-select — the sole react-select control on this page.
        self.city_control = page.locator("[class*='-control']").first
        self.empty_state  = page.get_by_text(Msg.EMPTY_STATE, exact=False)
        # Column headers render uppercase via CSS but their DOM text is title-case
        # (e.g. <th>Builder</th>), so match them as column headers by role.
        self.col_builder  = page.get_by_role("columnheader", name="Builder")
        self.col_project  = page.get_by_role("columnheader", name="Project")
        self.col_bank     = page.get_by_role("columnheader", name="Bank")

    @allure.step("Navigate to My Tools")
    def go_to_my_tools(self):
        self.page.get_by_role("link", name="tools My Tools").click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Open APF Search Engine tool")
    def open_tool(self):
        self.check_now_button.wait_for(state="visible")
        self.check_now_button.click()
        self.heading.wait_for(state="visible")
        # The tool fires a project-data POST for the default (unfiltered) list on
        # open. That request must settle BEFORE any search: it renders the full
        # builder list (>1 row), and if a search is typed while it is still in
        # flight, its late response overwrites the search results — e.g. clobbering
        # the "Builder Not Found" empty state with the full list. Wait for the
        # initial list (more than the single empty-state row) so the tool is truly
        # ready before callers search.
        self.page.wait_for_function(
            "document.querySelectorAll('tbody tr').length > 1", timeout=15000
        )

    @allure.step("Open the city dropdown")
    def open_city_dropdown(self):
        self.city_control.click()

    def city_options(self):
        """Locator for the open city react-select's option nodes."""
        return self.page.locator("[class*='-option']")

    @allure.step("Select city: {city}")
    def select_city(self, city: str):
        self.open_city_dropdown()
        self.city_options().filter(has_text=city).first.click()

    @allure.step("Search builder/project: {query}")
    def search(self, query: str):
        self.search_input.fill(query)
        self.search_input.press("Enter")
