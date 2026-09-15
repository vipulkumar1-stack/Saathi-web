import re
import allure
from playwright.sync_api import Page
from pages.base_page import BasePage


class EditColumnsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.open_button = page.get_by_role("button", name="Edit Columns")

        # Panel content headings (visible once the panel is open)
        self.select_fields_heading = page.get_by_text("Select Fields to show", exact=True)
        self.order_fields_heading  = page.get_by_text("Order Fields", exact=True)
        self.set_default_button    = page.get_by_role("button", name="Set Default")
        self.field_checkboxes      = page.get_by_role("checkbox")

        # Pagination control at the bottom of the leads table (react-js-pagination
        # style: <ul class="pagination"> of numbered <li><a aria-label="Page N">).
        # Two copies can render (top/bottom of the table) — .first is the live one.
        self.pagination = self.healing_locator(
            page.locator("ul.pagination").first,
            page.locator("[class*='pagination']").first,
            name="pagination",
        )

    @allure.step("Open Edit Columns panel")
    def open(self):
        self.open_button.click()
        self.select_fields_heading.wait_for(state="visible")

    def table_column_count(self) -> int:
        """Number of columns currently shown in the leads table header."""
        self.page.wait_for_selector("table thead th", timeout=15000)
        return self.page.locator("table thead th").count()

    def _first_toggleable_field(self):
        """First field checkbox that is enabled and checked — an optional column
        currently shown. Mandatory columns (e.g. Lead ID) render checked+disabled
        and can't be toggled."""
        for i in range(self.field_checkboxes.count()):
            cb = self.field_checkboxes.nth(i)
            if cb.is_enabled() and cb.is_checked():
                return cb
        return None

    @allure.step("Hide the first optional field")
    def hide_first_optional_field(self):
        cb = self._first_toggleable_field()
        cb.uncheck()
        return cb

    @allure.step("Re-show a field")
    def show_field(self, checkbox):
        checkbox.check()

    @allure.step("Hide every optional (non-mandatory) field")
    def hide_all_optional_fields(self):
        """Uncheck every enabled+checked checkbox (skips the disabled mandatory
        Lead ID checkbox, which can't be toggled). Returns the checkboxes
        toggled so the caller can restore them afterward."""
        toggled = []
        for i in range(self.field_checkboxes.count()):
            cb = self.field_checkboxes.nth(i)
            if cb.is_enabled() and cb.is_checked():
                cb.uncheck()
                toggled.append(cb)
        return toggled

    @allure.step("Re-check every previously hidden field")
    def show_all_fields(self, checkboxes):
        for cb in checkboxes:
            self.show_field(cb)

    def last_page_number(self) -> int:
        """Return the highest page number shown in the pagination control."""
        links = self.pagination.locator("li a[aria-label^='Page ']")
        numbers = []
        for i in range(links.count()):
            label = links.nth(i).get_attribute("aria-label") or ""
            m = re.search(r"Page (\d+)", label)
            if m:
                numbers.append(int(m.group(1)))
        return max(numbers) if numbers else -1

    @allure.step("Go to the last pagination page")
    def go_to_last_page(self) -> int:
        """Click the highest-numbered page link and return that page number."""
        last = self.last_page_number()
        self.pagination.get_by_role("button", name=f"Page {last}", exact=True).click()
        return last
