import allure
import pytest
from playwright.sync_api import Page, expect
from pages.search_filter_page import SearchFilterPage
from config.config import SEARCH_FILTER_DATA


@allure.feature("Search Filters")
class TestSearchFilter:

    @allure.story("Filter by Created Date")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_by_date(self, logged_in_page: Page):
        """Selecting 'Yesterday' from the Created Date filter loads filtered results."""
        f = SearchFilterPage(logged_in_page)
        f.apply_date_filter(SEARCH_FILTER_DATA["date_option"])
        expect(f.search_box).to_be_visible()

    @allure.story("Filter by City")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_by_city(self, logged_in_page: Page):
        """Selecting a city from the City filter loads filtered results."""
        f = SearchFilterPage(logged_in_page)
        f.apply_city_filter(SEARCH_FILTER_DATA["city_search"], SEARCH_FILTER_DATA["city_option"])
        expect(f.search_box).to_be_visible()

    @allure.story("Filter by Bank")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_by_bank(self, logged_in_page: Page):
        """Selecting a bank from the Bank filter loads filtered results."""
        f = SearchFilterPage(logged_in_page)
        f.apply_bank_filter(SEARCH_FILTER_DATA["bank_search"])
        expect(f.search_box).to_be_visible()

    @allure.story("Bug: search box becomes unresponsive after a quote-containing query")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="a quote-containing search query should leave the search box visible/usable, but it renders removed from the DOM", strict=True)
    def test_search_box_survives_quote_containing_query_bug(self, logged_in_page: Page):
        """Documents a bug: searching a query containing quote characters
        (e.g. "' OR '1'='1") should leave the search box visible and usable,
        but it renders removed from the DOM / permanently unresponsive."""
        f = SearchFilterPage(logged_in_page)
        f.search("' OR '1'='1")
        logged_in_page.wait_for_timeout(3000)
        assert f.search_box.is_visible()
        f.search_box.fill("")  # confirm it's still interactable

    @allure.story("Zero-result search shows a real (0) count")
    @allure.severity(allure.severity_level.NORMAL)
    def test_zero_result_search_shows_zero_badge(self, logged_in_page: Page):
        """Searching a query with no matches shows the All Leads badge as (0),
        not blank or missing."""
        f = SearchFilterPage(logged_in_page)
        f.search("zzzzznonexistentqueryxyz")
        logged_in_page.wait_for_timeout(2000)
        assert f.leads_count_badge.inner_text().strip() == "(0)"

    @allure.story("Bug: quote-containing zero-result query shows a blank count")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="a quote-containing zero-result query should show the (0) badge like any other zero-result search, but it renders blank", strict=True)
    def test_quote_query_shows_zero_badge_not_blank_bug(self, logged_in_page: Page):
        """Documents a bug: a quote-containing query that matches nothing
        should show the All Leads badge as (0), same as any other zero-result
        search, but it renders a blank () instead."""
        f = SearchFilterPage(logged_in_page)
        f.search("' OR '1'='1")
        logged_in_page.wait_for_timeout(2000)
        assert f.leads_count_badge.inner_text().strip() == "(0)"
