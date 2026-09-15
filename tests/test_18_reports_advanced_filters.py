import allure
from playwright.sync_api import Page, expect
from pages.reports_page import ReportsPage


@allure.feature("Reports Advanced Filters")
class TestReportsAdvancedFilters:

    def _open(self, page: Page) -> ReportsPage:
        f = ReportsPage(page)
        f.navigate()
        f.open_advanced_filters()
        return f

    # ── Individual dropdown tests ──────────────────────────────────────────────

    @allure.story("Filter 1 dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_1_dropdown_opens(self, logged_in_page: Page):
        """First 'Select an option' dropdown (index 0) should open on click.
        TODO: rename this test once the field label is confirmed."""
        f = self._open(logged_in_page)
        f.filter_1_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Filter 2 dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_2_dropdown_opens(self, logged_in_page: Page):
        """Second 'Select an option' dropdown (index 1) should open on click.
        TODO: rename this test once the field label is confirmed."""
        f = self._open(logged_in_page)
        f.filter_2_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Filter 3 dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_3_dropdown_opens(self, logged_in_page: Page):
        """Third 'Select an option' dropdown (index 2) should open on click.
        TODO: rename this test once the field label is confirmed."""
        f = self._open(logged_in_page)
        f.filter_3_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Source dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_source_dropdown_opens(self, logged_in_page: Page):
        """Clicking the Source filter (index 3) should open its dropdown."""
        f = self._open(logged_in_page)
        f.source_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Filter 5 dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_5_dropdown_opens(self, logged_in_page: Page):
        """Fifth 'Select an option' dropdown (index 4) should open on click.
        TODO: rename this test once the field label is confirmed."""
        f = self._open(logged_in_page)
        f.filter_5_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Sub Source dropdown opens after Source is selected")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sub_source_dropdown_opens(self, logged_in_page: Page):
        """Sub Source is only available after a Source is selected.
        Once Source is chosen, Sub Source occupies index 3 in the
        'Select an option' pool and its dropdown should open."""
        f = self._open(logged_in_page)
        # Step 1: open Source and pick first available option
        f.source_trigger.click()
        expect(f.dropdown_menu).to_be_visible()
        logged_in_page.locator("[class*='-option']").first.click()
        # Step 2: Sub Source is now enabled at index 3
        f.sub_source_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Banks dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_banks_dropdown_opens(self, logged_in_page: Page):
        """Clicking the Banks filter should open its dropdown."""
        f = self._open(logged_in_page)
        f.banks_trigger.click()
        expect(f.dropdown_menu).to_be_visible()


@allure.feature("Reports Dashboard")
class TestReportsDashboard:
    """The Reports landing page — stat cards and the report tiles. There is no
    export/download; 'More Reports' is a Coming Soon placeholder."""

    @allure.story("Reports dashboard renders its stat cards")
    @allure.severity(allure.severity_level.NORMAL)
    def test_reports_dashboard_loads(self, logged_in_page: Page):
        """The Reports page shows the pipeline stat cards and totals."""
        reports = ReportsPage(logged_in_page)
        reports.navigate()
        expect(reports.total_active_leads).to_be_visible()
        expect(reports.stat_sanctioned.first).to_be_visible()
        expect(reports.stat_disbursed.first).to_be_visible()
        expect(reports.lost_analysis).to_be_visible()

    @allure.story("More Reports is a Coming Soon placeholder")
    @allure.severity(allure.severity_level.NORMAL)
    def test_more_reports_coming_soon(self, logged_in_page: Page):
        """Clicking More Reports shows the 'Coming Soon' state."""
        reports = ReportsPage(logged_in_page)
        reports.navigate()
        reports.open_more_reports()
        expect(reports.coming_soon).to_be_visible()
