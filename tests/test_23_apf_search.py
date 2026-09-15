import allure
from playwright.sync_api import Page, expect
from pages.apf_search_page import ApfSearchPage
from config.config import APF_SEARCH_DATA


@allure.feature("APF Search Engine")
class TestApfSearch:
    """APF Finder — read-only builder/project search scoped by city, rendering a
    BUILDER / PROJECT / BANK / ACTION table with a 'Builder Not Found' empty state."""

    def _open(self, logged_in_page: Page) -> ApfSearchPage:
        page_obj = ApfSearchPage(logged_in_page)
        page_obj.go_to_my_tools()
        page_obj.open_tool()
        return page_obj

    @allure.story("APF Finder loads")
    @allure.severity(allure.severity_level.NORMAL)
    def test_apf_page_loads(self, logged_in_page: Page):
        """Opening the tool shows the APF Finder heading and search box."""
        apf = self._open(logged_in_page)
        expect(apf.heading).to_be_visible()
        expect(apf.search_input).to_be_visible()

    @allure.story("Results table headers are present")
    @allure.severity(allure.severity_level.NORMAL)
    def test_apf_results_table_headers(self, logged_in_page: Page):
        """The results table shows BUILDER, PROJECT and BANK column headers."""
        apf = self._open(logged_in_page)
        expect(apf.col_builder).to_be_visible()
        expect(apf.col_project).to_be_visible()
        expect(apf.col_bank).to_be_visible()

    @allure.story("City dropdown opens with options")
    @allure.severity(allure.severity_level.NORMAL)
    def test_apf_city_dropdown_opens(self, logged_in_page: Page):
        """Opening the city dropdown lists selectable city options."""
        apf = self._open(logged_in_page)
        apf.open_city_dropdown()
        expect(apf.city_options().first).to_be_visible()
        assert apf.city_options().count() > 0

    @allure.story("City can be changed")
    @allure.severity(allure.severity_level.NORMAL)
    def test_apf_select_city(self, logged_in_page: Page):
        """Selecting a city updates the control to show that city."""
        apf = self._open(logged_in_page)
        apf.select_city(APF_SEARCH_DATA["city"])
        expect(apf.page.get_by_text(APF_SEARCH_DATA["city"], exact=False).first).to_be_visible()

    @allure.story("Search with no match shows the empty state")
    @allure.severity(allure.severity_level.NORMAL)
    def test_apf_search_no_match_shows_empty_state(self, logged_in_page: Page):
        """Searching a nonsense string shows the 'Builder Not Found' empty state."""
        apf = self._open(logged_in_page)
        apf.search(APF_SEARCH_DATA["no_match_query"])
        expect(apf.empty_state).to_be_visible()
