import allure
from playwright.sync_api import Page, expect
from pages.team_filter_page import TeamFilterPage
from config.config import TEAM_FILTER_DATA


@allure.feature("My Team — Search Filters")
class TestTeamFilter:

    @allure.story("Filter by Created Date range")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_by_date(self, logged_in_page: Page):
        """Apply a date range filter on My Team — filtered list loads successfully."""
        f = TeamFilterPage(logged_in_page)
        f.go_to_my_team()
        f.apply_date_filter(TEAM_FILTER_DATA["date_range_days"])
        expect(f.add_teammate_button).to_be_visible()

    @allure.story("Filter by City")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_by_city(self, logged_in_page: Page):
        """Apply a city filter on My Team — filtered list loads successfully."""
        f = TeamFilterPage(logged_in_page)
        f.go_to_my_team()
        f.apply_city_filter(TEAM_FILTER_DATA["city_search"])
        expect(f.add_teammate_button).to_be_visible()
