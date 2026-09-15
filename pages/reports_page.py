import allure
from playwright.sync_api import Page
from pages.base_page import BasePage


class ReportsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.nav_link                = page.get_by_role("link", name="tools Reports")
        self.advanced_filters_button = page.get_by_role("button", name="Advanced Filters")

        # ── Advanced Filter triggers ──────────────────────────────────────────
        # All dropdowns below use "Select an option" as placeholder.
        # TODO: rename filter_1–filter_5 once the actual field labels are known.
        self.filter_1_trigger  = page.get_by_text("Select an option").nth(0)
        self.filter_2_trigger  = page.get_by_text("Select an option").nth(1)
        self.filter_3_trigger  = page.get_by_text("Select an option").nth(2)
        # Source is at index 3 (confirmed: "Website" is one of its options)
        self.source_trigger    = page.get_by_text("Select an option").nth(3)
        self.filter_5_trigger  = page.get_by_text("Select an option").nth(4)
        # After a Source value is chosen, Source leaves the "Select an option"
        # pool and Sub Source takes index 3
        self.sub_source_trigger = page.get_by_text("Select an option").nth(3)

        self.banks_trigger     = page.get_by_text("Select Banks")

        self.dropdown_menu = page.locator(
            "[class*='-menu']:visible, [role='listbox']:visible, [class*='selectOptionsModal_selectOptionsContent']:visible"
        ).first

        # ── Dashboard (report tiles + stat cards) ─────────────────────────────
        self.business_hygiene_button = page.get_by_role("button", name="Business Hygiene Report")
        self.more_reports_button     = page.get_by_role("button", name="More Reports")
        self.total_active_leads      = page.get_by_text("Total Active Leads", exact=False).first
        self.lost_analysis           = page.get_by_text("Lost Analysis", exact=False).first
        self.stat_pre_login          = page.get_by_text("Pre Login", exact=True)
        self.stat_sanctioned         = page.get_by_text("Sanctioned", exact=True)
        self.stat_disbursed          = page.get_by_text("Disbursed", exact=True)
        self.coming_soon             = page.get_by_text("Coming Soon", exact=False)

    @allure.step("Navigate to Reports page")
    def navigate(self):
        self.nav_link.click()
        self.advanced_filters_button.wait_for(state="visible")

    @allure.step("Open More Reports")
    def open_more_reports(self):
        self.more_reports_button.click()

    @allure.step("Open Reports Advanced Filters panel")
    def open_advanced_filters(self):
        self.advanced_filters_button.click()
        self.page.get_by_text("Select an option").first.wait_for(state="visible")
