import re
import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.constants import Cibil as Msg


class CibilPage(BasePage):
    """Check CIBIL Score tool (/my-tool-cibil).

    Opened from My Tools via the "Check CIBIL Score" card. The form collects
    PAN + personal details; "Fetch" pulls PAN details, "Continue" validates the
    form and advances to a fulfilment/loan-type step ("Create Lead & Get CIBIL").
    A real bureau score is only returned for a PAN with data — the test PAN
    reaches the fulfilment step, which is the reliable happy-path signal.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        # Tool card on My Tools — deepest div holding both the title and its
        # own "Check Now" button (a bare has_text would match the whole grid).
        self.check_now_button = (
            page.locator("div")
            .filter(has=page.get_by_text("Check CIBIL Score", exact=True))
            .filter(has=page.get_by_role("button", name="Check Now"))
            .last
            .get_by_role("button", name="Check Now")
        )
        # Form fields — stable ids on the live tool.
        self.pan_input        = page.locator("#pan_card")
        self.first_name_input = page.locator("#first_name")
        self.last_name_input  = page.locator("#last_name")
        self.email_input      = page.locator("#email")
        self.mobile_input     = page.locator("#mobile")
        self.dob_input        = page.locator("input.date-picker-input")
        self.fetch_button     = page.get_by_text("Fetch", exact=True)
        self.continue_button  = page.get_by_role("button", name="Continue")
        # Markers
        self.no_impact_note   = page.get_by_text(Msg.NO_IMPACT_NOTE, exact=False)
        self.fulfilment_prompt = page.get_by_text(Msg.FULFILMENT_PROMPT, exact=False)

    # ── toast helper ────────────────────────────────────────────────────────
    def toast(self, text: str):
        """Locator for a react-toastify message containing `text`."""
        return self.page.locator("[class*='Toastify__toast-body']").filter(
            has_text=text
        )

    # ── navigation ──────────────────────────────────────────────────────────
    @allure.step("Navigate to My Tools")
    def go_to_my_tools(self):
        self.page.get_by_role("link", name="tools My Tools").click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Open Check CIBIL Score tool")
    def open_tool(self):
        self.check_now_button.wait_for(state="visible")
        self.check_now_button.click()
        self.pan_input.wait_for(state="visible")

    # ── field actions ─────────────────────────────────────────────────────────
    @allure.step("Enter PAN: {pan}")
    def fill_pan(self, pan: str):
        self.pan_input.fill(pan)

    @allure.step("Click Fetch")
    def click_fetch(self):
        self.fetch_button.click()

    @allure.step("Fill personal details")
    def fill_details(self, first_name: str, last_name: str, email: str, mobile: str):
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.email_input.fill(email)
        self.mobile_input.fill(mobile)

    @allure.step("Select date of birth: {day}/{year}")
    def set_dob(self, year: int, day: int):
        """Pick a DOB via the cascading date picker.

        Clicking the header year opens a year grid; selecting a year returns to
        the day view for that year (month left at the current month, which is a
        valid adult DOB). Then the day cell is clicked.
        """
        self.dob_input.click()
        # header year label -> year grid
        self.page.get_by_text(re.compile(r"^(19|20)\d\d$")).first.click()
        # choose the target year -> back to day view for that year
        year_cell = self.page.get_by_text(str(year), exact=True).first
        year_cell.scroll_into_view_if_needed()
        year_cell.click()
        # choose the day
        day_cell = self.page.get_by_text(re.compile(rf"^{day}$")).first
        day_cell.scroll_into_view_if_needed()
        day_cell.click()

    @allure.step("Click Continue")
    def click_continue(self):
        self.continue_button.click()

    @allure.step("Fill the CIBIL form and continue to the fulfilment step")
    def fill_form_and_continue(self, data: dict):
        self.fill_pan(data["pan"])
        self.fill_details(data["first_name"], data["last_name"],
                          data["email"], data["mobile"])
        self.set_dob(data["dob_year"], data["dob_day"])
        self.click_continue()
