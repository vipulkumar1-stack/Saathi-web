import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.constants import AbbCalculator as Msg


class AbbCalculatorPage(BasePage):
    """ABB (Average Bank Balance) Calculator.

    Opened from My Tools via the "ABB Calculator" card. It renders in-place on
    the tools page (no route change). The tool takes a customer's bank statement
    PDF and computes the average balance. The file input is restricted to PDF
    (accept="application/pdf"); a successful ABB result needs a real statement,
    so these tests cover the upload UI, the PDF-only restriction, and the
    instructional copy rather than a parsed result.

    Flow note: the tool was redesigned to open on a "Loan Applicant" selector
    screen (existing applicants + their statements, with "Analyse"/"Add More").
    The statement-upload UI (intro prompt, PDF-only/OD-CC/most-recent notes and
    the "Upload statement" file input) is now reached by clicking "Add More" on
    that selector screen, so open_tool() walks through it.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.check_now_button = (
            page.locator("div")
            .filter(has=page.get_by_text("ABB Calculator", exact=True))
            .filter(has=page.get_by_role("button", name="Check Now"))
            .last
            .get_by_role("button", name="Check Now")
        )
        # Applicant-selector screen (shown first after Check Now); "Add More"
        # opens the statement-upload UI.
        self.add_more_button = page.get_by_role("button", name="Add More")
        self.heading         = page.get_by_text(Msg.PAGE_HEADING, exact=True)
        self.intro_prompt    = page.get_by_text(Msg.INTRO_PROMPT, exact=False)
        self.pdf_only_note   = page.get_by_text(Msg.PDF_ONLY_NOTE, exact=False)
        self.od_cc_note      = page.get_by_text(Msg.OD_CC_NOTE, exact=False)
        self.recent_note     = page.get_by_text(Msg.RECENT_NOTE, exact=False)
        self.upload_button   = page.get_by_role("button", name="Upload statement")
        self.file_input      = page.locator("input[type='file']")

    @allure.step("Navigate to My Tools")
    def go_to_my_tools(self):
        self.page.get_by_role("link", name="tools My Tools").click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Open ABB Calculator tool")
    def open_tool(self):
        self.check_now_button.wait_for(state="visible")
        self.check_now_button.click()
        # The redesigned tool opens on the applicant-selector screen; the upload
        # UI lives behind "Add More". When no applicant/statement context exists
        # the upload screen may show directly, so only click "Add More" if it
        # appears and the upload button isn't already visible.
        try:
            self.add_more_button.wait_for(state="visible", timeout=8000)
            if not self.upload_button.is_visible():
                self.add_more_button.click()
        except Exception:
            pass
        self.upload_button.wait_for(state="visible")

    @allure.step("Upload statement file")
    def upload_statement(self, file_path: str):
        self.file_input.first.set_input_files(file_path)
