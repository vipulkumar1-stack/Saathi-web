import allure
import pytest
from playwright.sync_api import Page, expect
from pages.my_earnings_page import MyEarningsPage


@allure.feature("My Earnings")
class TestMyEarnings:

    @allure.story("My Earnings page loads with the earnings table")
    @allure.severity(allure.severity_level.NORMAL)
    def test_earnings_page_loads(self, logged_in_page: Page):
        """My Earnings opens from the nav menu and shows the earnings table."""
        e = MyEarningsPage(logged_in_page)
        e.go_to_my_earnings()
        expect(e.results_table.first).to_be_visible()
        assert e.row_count() > 0, "Earnings table loaded with no rows"

    @allure.story("Switch to Earned tab")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("tab", ["Earned", "Paid", "Projected"])
    def test_tab_switching(self, logged_in_page: Page, tab: str):
        """Each earnings tab (Earned / Paid / Projected) loads its data grid."""
        e = MyEarningsPage(logged_in_page)
        e.go_to_my_earnings()
        e.open_tab(tab)
        expect(e.results_table.first).to_be_visible()
        assert e.row_count() > 0, f"{tab} tab loaded with no rows"

    @allure.story("Search earnings by Lead ID returns the matching record")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_by_lead_id(self, logged_in_page: Page):
        """Filtering by a Lead ID narrows the grid to that single matching lead."""
        e = MyEarningsPage(logged_in_page)
        e.go_to_my_earnings()
        lead_id = e.get_first_lead_id()
        e.search_by_lead_id(lead_id)
        body = logged_in_page.locator("table tbody").inner_text()
        assert lead_id in body, f"Searched lead {lead_id} not present in results"
        assert e.row_count() <= 1 or all(
            lead_id in row.inner_text()
            for row in logged_in_page.locator("table tbody tr").all()
        ), "Search returned rows that do not match the queried Lead ID"

    @allure.story("Reset restores the full earnings list")
    @allure.severity(allure.severity_level.NORMAL)
    def test_reset_filter(self, logged_in_page: Page):
        """After a Lead ID search, Reset clears the filter and restores all rows."""
        e = MyEarningsPage(logged_in_page)
        e.go_to_my_earnings()
        full_count = e.row_count()
        lead_id = e.get_first_lead_id()
        e.search_by_lead_id(lead_id)
        assert e.row_count() <= full_count
        e.reset_filter()
        assert e.row_count() == full_count, "Reset did not restore the full earnings list"
