import allure
from datetime import datetime, timedelta
from playwright.sync_api import Page
from pages.base_page import BasePage


def _gridcell_label(date: datetime) -> str:
    """Format a date as the aria-label used in the date picker, e.g. 'Tuesday, 12 May'."""
    return f"{date.strftime('%A')}, {date.day} {date.strftime('%B')}"


class TeamFilterPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Date range filter — scoped to exclude the p-column-title span in the data table,
        # which also contains "Created Date" and causes a strict-mode violation.
        self.date_filter_button = page.locator("span:not(.p-column-title)").filter(has_text="Created Date")
        # City filter
        self.city_filter_button = page.get_by_role("button", name="City")
        self.city_search_input  = page.get_by_role("textbox", name="Search City")
        # Shared Apply button
        self.apply_button        = page.get_by_role("button", name="Apply")
        # Anchor — always visible on My Team page
        self.add_teammate_button = page.get_by_role("button", name="+ Add Teammate")

    @allure.step("Navigate to My Team page")
    def go_to_my_team(self):
        self.page.get_by_role("link", name="teams My Team").click()
        self.page.wait_for_load_state("networkidle")

    def _pick_picker_date(self, target: datetime, today: datetime):
        """The picker opens on the current month. Navigate back to target's month
        (when it falls in an earlier month, e.g. near the start of a month) before
        clicking its gridcell."""
        months_back = (today.year - target.year) * 12 + (today.month - target.month)
        for _ in range(months_back):
            # click() auto-waits for the arrow and the month advances
            # synchronously, so no fixed delay between hops is needed.
            self.page.get_by_role("button", name="Previous Month").first.click()
        self.page.get_by_role("gridcell", name=_gridcell_label(target)).first.click()

    @allure.step("Apply date range filter: last {days} days")
    def apply_date_filter(self, days: int = 2):
        today = datetime.today()
        start = today - timedelta(days=days)
        self.date_filter_button.wait_for(state="visible")
        self.date_filter_button.click()
        # Date picker renders exactly two date textboxes: [0] = start, [1] = end, and
        # each opens on the current month. get_by_label("Start") / get_by_label("End")
        # would be ideal — ask frontend team to add aria-label attributes to the inputs.
        self.page.get_by_role("textbox").first.wait_for(state="visible")
        self.page.get_by_role("textbox").first.click()
        self._pick_picker_date(start, today)
        self.page.get_by_role("textbox").nth(1).click()
        self._pick_picker_date(today, today)
        self.apply_button.click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Apply city filter: {search}")
    def apply_city_filter(self, search: str):
        self.city_filter_button.wait_for(state="visible")
        self.city_filter_button.click()
        self.city_search_input.wait_for(state="visible")
        self.city_search_input.fill(search)
        # .filter-checkbox-custom is a custom widget — no ARIA role is set by the
        # frontend. First visible instance is always the matched city's checkbox.
        # TODO: ask frontend team to add role="checkbox" + aria-label to this element.
        self.page.locator(".filter-checkbox-custom").first.click()
        self.apply_button.click()
        self.page.wait_for_load_state("networkidle")
