import re
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


def _is_leads_list_response(resp) -> bool:
    """Match the leads-list GraphQL response. All tab/search queries share one
    POST endpoint (finex/api/v1/graphql), so the URL alone can't distinguish
    them — match on the response body shape instead."""
    if resp.request.method != "POST" or "graphql" not in resp.url:
        return False
    try:
        return '"lead_list"' in resp.text()
    except Exception:
        return False


class HomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.create_lead_button = page.get_by_role("button", name="Create Lead")
        self.pre_login_tab = page.locator("div.teamtab", has_text="Pre-Login")
        self.logged_in_tab = page.locator("div.teamtab", has_text="Logged In")
        self.sanctioned_tab = page.locator("div.teamtab", has_text="Sanctioned")
        self.search_box = page.get_by_role("textbox", name="Search by id or name...")
        # Bulk Actions menu
        self.actions_button = page.get_by_role("button", name="Actions")
        self.actions_items  = page.locator(".actions-dropdown-item")
        self.last_presence_debug = ""

    @allure.step("Open the bulk Actions menu")
    def open_actions_menu(self):
        self.actions_button.wait_for(state="visible")
        self.actions_button.click()
        self.actions_items.first.wait_for(state="visible")

    def all_leads_count(self) -> int:
        """Read the count shown on the 'All Leads (N)' tab."""
        self.page.wait_for_load_state("networkidle")
        m = re.search(r"All Leads\s*\((\d+)\)", self.page.locator("body").inner_text())
        return int(m.group(1)) if m else -1

    @allure.step("Click Create Lead button")
    def click_create_lead(self):
        self.page.wait_for_load_state("networkidle")
        self.create_lead_button.wait_for(state="visible")
        expect(self.create_lead_button).to_be_enabled()
        self.create_lead_button.click()
        self.page.get_by_text("Add New Lead", exact=True).wait_for(state="visible")

    def _click_tab_and_wait(self, tab_locator, retries: int = 2):
        """Click a tab and wait for THAT tab's data — not just any row.

        Waiting on `table tbody tr` existing is satisfied by the outgoing
        tab's stale rows (the table doesn't clear before the new tab's data
        arrives), which is how a lead was once reported present in a tab that
        was actually empty. All tabs share one GraphQL endpoint, so the fix
        reads the leads-list RESPONSE BODY directly — an empty `lead_list` is
        then a confirmed, fast, legitimate outcome instead of being
        indistinguishable from "still loading" (which a DOM-only wait can't
        tell apart without guessing at an empty-state selector).
        """
        for attempt in range(retries + 1):
            tab_locator.wait_for(state="visible")
            try:
                with self.page.expect_response(_is_leads_list_response, timeout=10000) as resp_info:
                    tab_locator.click()
                self.page.wait_for_load_state("load")
                body = resp_info.value.json()
                lead_list = body["data"]["leads"][0]["lead_list"]
                if lead_list:
                    self.page.wait_for_selector("table tbody tr", timeout=10000)
                return
            except Exception:
                if attempt < retries:
                    self.page.reload(wait_until="load")
        raise AssertionError(
            f"Tab did not report a leads-list response with loaded data after "
            f"{retries + 1} attempts"
        )

    @allure.step("Navigate to Pre-Login tab")
    def click_pre_login_tab(self):
        self._click_tab_and_wait(self.pre_login_tab)

    @allure.step("Navigate to Logged In tab")
    def click_logged_in_tab(self):
        self._click_tab_and_wait(self.logged_in_tab)

    @allure.step("Navigate to Sanctioned tab")
    def click_sanctioned_tab(self):
        self._click_tab_and_wait(self.sanctioned_tab)

    def _row_locator(self, lead_id: str):
        """A row cell scoped to the table body and matched EXACTLY on lead ID.

        get_by_role(name=...) matches by substring by default, which is how a
        stale row from the previously-viewed tab (or an unrelated cell whose
        text merely contains this lead_id) was once mistaken for the real
        one. Anchoring the regex and scoping to `table tbody` fixes both."""
        return self.page.locator("table tbody tr").locator(
            "td", has_text=re.compile(rf"^\s*{re.escape(lead_id)}\s*$")
        )

    @allure.step("Search for lead: {lead_id}")
    def search_lead(self, lead_id: str, retries: int = 2, required: bool = True):
        """Fill the search box and wait for the filtered row to actually render.

        fill() only sets the input value — it doesn't wait for the app's search
        API round-trip or table re-render, so a caller that clicks the result
        immediately can race the filter and time out even though the lead is
        genuinely present. Waiting here (with a re-fill retry) keeps that race
        out of every caller instead of each one needing its own workaround.

        Raises when the lead never appears (unless required=False, for a
        caller that is deliberately checking a negative-search case) instead
        of returning silently and letting the caller act on an unfiltered or
        stale table."""
        SEARCH_TIMEOUT = 8000
        for attempt in range(retries + 1):
            # Every interaction here is explicitly bounded to SEARCH_TIMEOUT —
            # left at the page's default TIMEOUT (45s), any one of these (not
            # just the initial wait_for) reproduces the original 45s hang if
            # the search box becomes unavailable mid-retry (e.g. the tab
            # reloads or empties between attempts).
            self.search_box.wait_for(state="visible", timeout=SEARCH_TIMEOUT)
            self.search_box.click(timeout=SEARCH_TIMEOUT)
            self.search_box.fill(lead_id, timeout=SEARCH_TIMEOUT)
            if self.is_lead_present(lead_id, timeout=SEARCH_TIMEOUT):
                return
            if attempt < retries:
                # The search box unmounts entirely when the current tab's
                # result set goes empty (confirmed live: a tab reading e.g.
                # 'Sanctioned (0)' renders no search input at all). Detect that
                # up front instead of burning the full SEARCH_TIMEOUT on a
                # fill() against an input that will never attach — this was
                # previously indistinguishable from an ordinary slow search.
                if not self.search_box.is_visible():
                    raise AssertionError(
                        f"Search box disappeared before the retry reset while searching "
                        f"for lead {lead_id} — the current tab likely emptied out (e.g. "
                        f"the lead moved to a different stage during this run). "
                        f"{self.last_presence_debug}"
                    )
                self.search_box.fill("", timeout=SEARCH_TIMEOUT)
        if required:
            raise AssertionError(
                f"Lead {lead_id} did not appear in the search results after "
                f"{retries + 1} attempts. {self.last_presence_debug}"
            )

    @allure.step("Check if lead {lead_id} is present in current tab")
    def is_lead_present(self, lead_id: str, timeout: int = 10000) -> bool:
        """Return True if a row for the given lead ID is visible in the current tab's table.

        Assumes the caller has already navigated to the desired tab and (optionally)
        searched for the lead.
        """
        try:
            self._row_locator(lead_id).first.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            try:
                rows = self.page.locator("table tbody tr").all_inner_texts()
            except Exception:
                rows = []
            self.last_presence_debug = f"Rows currently in table: {rows[:10]}"
            return False

    @allure.step("Read first lead ID from table")
    def get_first_lead_id(self) -> str:
        """Return the lead ID (first numeric cell) from the first row of the current tab."""
        self.page.wait_for_selector("table tbody tr", timeout=10000)
        first_row = self.page.locator("table tbody tr").first
        for cell in first_row.locator("td").all():
            text = cell.inner_text().strip()
            if text.isdigit():
                return text
        return first_row.locator("td").first.inner_text().strip()

    @allure.step("Open lead {lead_id} in new tab")
    def open_lead_in_new_tab(self, lead_id: str) -> Page:
        # The table re-renders from background polling on this app, which can
        # detach the exact row mid-click; a single retry after a fresh look-up
        # of the row (rather than the default 45s of retrying against the
        # same, now-detached, element handle) resolves the common case fast.
        for attempt in range(2):
            try:
                with self.page.expect_popup(timeout=15000) as popup_info:
                    self._row_locator(lead_id).first.click(timeout=15000)
                break
            except Exception:
                if attempt == 1:
                    raise
        popup = popup_info.value
        popup.wait_for_load_state("domcontentloaded")
        return popup
