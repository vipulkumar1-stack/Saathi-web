import allure
from playwright.sync_api import Page
from pages.base_page import BasePage


class AdvancedFiltersPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.open_button = page.get_by_role("button", name="filter Advanced Filters")

        # ── Dropdown triggers ─────────────────────────────────────────────────
        # Source / Banks are custom div triggers (not React Select).
        # Each is the innermost div that contains only its placeholder text,
        # scoped via get_by_text + parent div to avoid positional .nth().
        self.source_trigger        = page.get_by_text("Select Source", exact=True)
        self.banks_trigger         = page.get_by_text("Select Banks", exact=True)

        # React Select triggers — matched by their visible placeholder text.
        self.sub_source_trigger    = page.locator(".filter-group").filter(has_text="Sub Source").locator("[class*='-control']").first
        self.purchase_type_trigger = page.get_by_text("Select Purchase Type", exact=True)
        self.product_type_trigger  = page.get_by_text("Select Product Type", exact=True)
        self.sub_type_trigger      = page.get_by_text("Select Sub Type", exact=True)
        self.fulfillment_trigger   = page.get_by_text("Select Fulfillment", exact=True)
        self.cities_trigger        = page.get_by_text("Select Cities", exact=True)
        self.designation_trigger   = page.get_by_text("Select Designation", exact=True).first
        # Teammate role uses the second "Select Designation" placeholder (after the
        # first one for the main Designation field). Scoped by heading to avoid nth().
        self.teammate_role_trigger = page.locator("section, div").filter(
            has_text="Teammate"
        ).get_by_text("Select Designation", exact=True)
        self.team_member_trigger   = page.get_by_text("Select Team Member", exact=True)
        self.assigned_to_trigger   = page.get_by_text("Assigned_to", exact=True)
        self.checklist_item_trigger = page.get_by_text("Select Checklist Item", exact=True)

        # Status and Sub Status — anchored to the "Status and Sub Status" section
        # heading, which uniquely identifies the container. The "Underwriting" section
        # also has a STATUS control (next to Checklist Item), so we must NOT anchor
        # to the Checklist filter-group: that was fragile and broke when the
        # Underwriting STATUS started rendering even in its disabled state.
        _status_section = page.locator("div, section").filter(
            has=page.get_by_text("Status and Sub Status", exact=True)
        ).last
        self.status_trigger     = _status_section.locator("[class*='-control']").first
        self.sub_status_trigger = _status_section.locator("[class*='-control']").nth(1)

        # Dropdown verification: react-select menu, ARIA listbox, or custom modal.
        self.dropdown_menu = page.locator(
            "[class*='-menu']:visible, [role='listbox']:visible, [class*='selectOptionsModal_selectOptionsContent']:visible"
        ).first

        # Panel actions
        self.apply_button     = page.get_by_role("button", name="Apply", exact=True)
        self.clear_all_button = page.get_by_role("button", name="Clear All")

    @allure.step("Open Advanced Filters panel")
    def open(self):
        self.open_button.click()
        # Wait for the panel's Apply action — always present, and (unlike the
        # "Select Source" placeholder) still there when a filter is already
        # applied (advanced filters persist server-side).
        self.apply_button.wait_for(state="visible")

    @allure.step("Reset all advanced filters")
    def reset(self):
        """Clear any applied filters via the toolbar Clear button (one click, no
        panel). Used for a clean baseline and cleanup, since advanced filters
        persist server-side. The in-panel Apply is disabled with no selection, so
        the toolbar Clear is the reliable reset."""
        clear = self.page.get_by_role("button", name="Clear", exact=True)
        clear.click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Select the first Source option")
    def select_first_source(self):
        self.source_trigger.click()
        # Wait for the option list to render before clicking (clicking too early,
        # while the panel is still opening, silently selects nothing).
        option = self.page.locator("[class*='-option']").first
        option.wait_for(state="visible")
        option.click()
        self.page.wait_for_timeout(500)

    @allure.step("Apply filters")
    def apply(self):
        self.apply_button.click()
        self.page.wait_for_load_state("networkidle")
        # Let the "All Leads (N)" badge re-render with the filtered count.
        self.page.wait_for_timeout(1500)

    @allure.step("Clear all filters")
    def clear_all(self):
        self.clear_all_button.click()

    @allure.step("Close Advanced Filters panel")
    def close(self):
        # Click outside the panel using the Escape key — more reliable than a
        # backdrop class that could be renamed.
        self.page.keyboard.press("Escape")
