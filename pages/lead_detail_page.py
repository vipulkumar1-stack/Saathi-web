import re
import time
import allure
from datetime import datetime
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.constants import LeadDetail as Msg


class LeadDetailPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # As of 2026-09-15 this button no longer exists in the DOM for a
        # Pre-Login lead (see tests/test_03_move_to_login.py — app
        # regression, tracked via known_bug/xfail there). The app's
        # `logintomovebtn` class is now on the *Remarks* button instead — do
        # NOT retarget this locator at that class, it would click Remarks.
        self.move_to_login_button    = page.get_by_role("button", name="Move To Login")
        self.move_to_sanction_button = page.get_by_role("button", name="Move To Sanction")
        self.move_to_disburse_button = page.get_by_role("button", name="Move To Disburse")
        self.mark_as_lost_button     = page.get_by_role("button", name="Mark as lost")

        # ── Tabs & detail-view cards ─────────────────────────────────────────
        self.details_tab   = page.get_by_role("button", name=Msg.TAB_DETAILS, exact=True)
        self.documents_tab = page.get_by_role("button", name=Msg.TAB_DOCUMENTS, exact=True)
        self.history_tab   = page.get_by_role("button", name=Msg.TAB_HISTORY, exact=True)
        self.loan_details_card     = page.get_by_text(Msg.CARD_LOAN, exact=True)
        self.customer_details_card = page.get_by_text(Msg.CARD_CUSTOMER, exact=True)
        self.income_details_card   = page.get_by_text(Msg.CARD_INCOME, exact=True)
        self.property_details_card = page.get_by_text(Msg.CARD_PROPERTY, exact=True)

        # ── Remarks / Reopen / Edit controls ─────────────────────────────────
        self.remarks_button = page.get_by_role("button", name="Remarks")
        self.reopen_button  = page.get_by_role("button", name="Reopen")
        self.lost_badge     = page.get_by_text("Lost", exact=True)
        # Modal Save (exact avoids matching the edit wizard's "Save & Exit").
        self.modal_save_button = page.get_by_role("button", name="Save", exact=True)
        self.modal_textarea    = page.locator("textarea")
        # Edit wizard
        self.edit_heading      = page.get_by_text(Msg.EDIT_HEADING, exact=True)
        self.save_and_exit_button = page.get_by_role("button", name="Save & Exit")
        self.next_button          = page.get_by_role("button", name="Next")
        # The edit pencil (icon-only, no visible text or aria-label — a real
        # app accessibility gap worth reporting, not one to route around with
        # another positional guess). `.editbtn` was the app's own class for it
        # and was unique on the page as of 2026-09-04. It no longer is: the app
        # added a second `button.editbtn` for "Raise Fulfillment Issue"
        # (confirmed live 2026-09-15, strict-mode violation on every
        # open_edit()), so the bare class is now ambiguous. Scope to the
        # pencil's icon child instead of `.first`/`.nth()` — `.first` here
        # would silently click "Raise Fulfillment Issue" (it renders before
        # the pencil in DOM order), and a positional index breaks again the
        # moment a third `.editbtn` appears, same failure mode as the old
        # "first button after History" locator that this replaced.
        self.edit_pencil_button = page.locator("button.editbtn").filter(
            has=page.locator("i.ic-createmode_editedit")
        )
        # Documents
        self.doc_file_input = page.locator("input[type='file']")

    # ── toast helper ─────────────────────────────────────────────────────────
    def toast(self, text: str):
        return self.page.locator("[class*='Toastify__toast-body']").filter(has_text=text)

    def _wait_for_stage_button(self, locator: Locator, name: str, timeout: int = 15000):
        """Wait for a stage-action button with a bounded timeout that reports
        the lead's REAL current stage on failure, instead of the default 45s
        TIMEOUT silently expiring. This button only exists once the lead has
        reached the prior stage — e.g. 'Move To Disburse' cannot appear until
        the lead is Sanctioned — so a bare wait_for() timeout here previously
        gave no clue *why* (this is what a broken sanction move looked like
        for all five Move To Disburse tests on 2026-08-18)."""
        try:
            locator.wait_for(state="visible", timeout=timeout)
        except Exception:
            visible = [
                b for b in (self.move_to_login_button, self.move_to_sanction_button,
                            self.move_to_disburse_button, self.mark_as_lost_button)
                if b.is_visible()
            ]
            raise AssertionError(
                f"'{name}' button did not appear within {timeout}ms — the lead is "
                f"probably not yet at the required stage. Buttons currently visible: "
                f"{[b.inner_text() for b in visible] or 'none'}"
            )

    @allure.step("Read sanctioned amount")
    def get_sanction_amount(self, timeout: int = 10000) -> str:
        """Read sanctioned amount (e.g. '₹50,00,000' -> '5000000') from the Sanction card.

        Scopes to the Sanction card via its 20px header span, then the 'Amount' row —
        the same anchor pattern _get_card_date uses. (The row text is 'Amount ₹50,00,000',
        so get_by_text('Amount', exact=True) never matches; that's why it must anchor on
        the card header and select the float-right value span.)

        Polls instead of reading once: _wait_for_stage_button only waits for the
        'Move To Disburse' BUTTON to appear, which can render before the card's
        Amount value has finished populating (e.g. still showing '--'). A single
        blind read here previously returned '0', which drove
        test_move_to_disburse_amount_exceeds_sanction to submit ₹1 as the
        'exceeding' amount — the app correctly accepted it (₹1 does not exceed
        the real sanctioned amount) and genuinely disbursed the lead. Raising
        here instead of returning a fake '0' stops that at the source.
        """
        self._wait_for_stage_button(self.move_to_disburse_button, "Move To Disburse")
        locator = self.page.locator(
            "xpath=//span[normalize-space(.)='Sanction' and contains(@style,'font-size: 20px')]"
            "/ancestor::div[1]/following-sibling::div[starts-with(normalize-space(.),'Amount')]/span"
        ).first
        deadline = time.monotonic() + timeout / 1000
        raw = ""
        while time.monotonic() < deadline:
            raw = locator.inner_text()
            digits = self.digits_only(raw)
            if digits and int(digits) > 0:
                return digits
            self.page.wait_for_timeout(300)
        raise AssertionError(
            f"Sanction Amount never populated with a real value within {timeout}ms "
            f"(last read: {raw!r})"
        )

    def _get_card_date(self, card_title: str) -> datetime:
        """Read the Date row (e.g. '22 May, 2026') from the named status card."""
        value = self.page.locator(
            f"xpath=//span[normalize-space(.)='{card_title}' and contains(@style,'font-size: 20px')]"
            "/ancestor::div[1]/following-sibling::div[starts-with(normalize-space(.),'Date')]/span"
        )
        return datetime.strptime(value.first.inner_text().strip(), "%d %b, %Y")

    @allure.step("Read login date")
    def get_login_date(self) -> datetime:
        """Read the lead's login date from the Login card (e.g. '22 May, 2026')."""
        self._wait_for_stage_button(self.move_to_sanction_button, "Move To Sanction")
        return self._get_card_date("Login")

    @allure.step("Read sanction date")
    def get_sanction_date(self) -> datetime:
        """Read the lead's sanction date from the Sanction card (e.g. '21 May, 2026')."""
        self._wait_for_stage_button(self.move_to_disburse_button, "Move To Disburse")
        return self._get_card_date("Sanction")

    @allure.step("Click Move To Login")
    def click_move_to_login(self):
        self.page.wait_for_load_state("networkidle")
        self._wait_for_stage_button(self.move_to_login_button, "Move To Login")
        self.move_to_login_button.click()

    @allure.step("Click Move To Sanction")
    def click_move_to_sanction(self):
        self.page.wait_for_load_state("networkidle")
        self._wait_for_stage_button(self.move_to_sanction_button, "Move To Sanction")
        self.move_to_sanction_button.click()

    @allure.step("Click Move To Disburse")
    def click_move_to_disburse(self):
        self.page.wait_for_load_state("networkidle")
        self._wait_for_stage_button(self.move_to_disburse_button, "Move To Disburse")
        self.move_to_disburse_button.click()

    @allure.step("Click Mark as Lost")
    def click_mark_as_lost(self):
        self.page.wait_for_load_state("networkidle")
        self.mark_as_lost_button.wait_for(state="visible")
        self.mark_as_lost_button.click()

    # ── Tabs ─────────────────────────────────────────────────────────────────
    @allure.step("Open Documents tab")
    def open_documents_tab(self):
        self.documents_tab.click()
        self.page.wait_for_timeout(1500)

    @allure.step("Open History tab")
    def open_history_tab(self):
        self.history_tab.click()
        self.page.wait_for_timeout(1500)

    @allure.step("Open Details tab")
    def open_details_tab(self):
        self.details_tab.click()
        self.page.wait_for_timeout(1000)

    def history_entries(self):
        """Timeline rows show a 'BY <name>' author line; count them."""
        return self.page.get_by_text(re.compile(r"^BY\s"))

    # ── Remarks ──────────────────────────────────────────────────────────────
    @allure.step("Open Remarks modal")
    def open_remarks(self):
        self.remarks_button.click()
        self.modal_save_button.wait_for(state="visible")

    @allure.step("Fill remark: {text}")
    def fill_remark(self, text: str):
        self.modal_textarea.first.fill(text)

    @allure.step("Save remark")
    def save_remark(self):
        self.modal_save_button.click()

    # ── Reopen (lost lead) ─────────────────────────────────────────────────────
    @allure.step("Open Reopen modal")
    def open_reopen(self):
        self.reopen_button.click()
        self.modal_save_button.wait_for(state="visible")

    @allure.step("Fill reopen remarks: {text}")
    def fill_reopen_remarks(self, text: str):
        self.modal_textarea.first.fill(text)

    @allure.step("Save reopen")
    def save_reopen(self):
        self.modal_save_button.click()

    # ── Details edit wizard ────────────────────────────────────────────────────
    @allure.step("Open lead-details edit wizard")
    def open_edit(self):
        self.edit_pencil_button.click()
        self.save_and_exit_button.wait_for(state="visible")

    @allure.step("Edit loan details and save")
    def edit_loan_details_and_save(self, loan_amount: str):
        # Loan Amount is the first textbox on the wizard's first step; the
        # Desired Tenure react-select must have a value for Save & Exit to pass.
        amount = self.page.get_by_role("textbox").first
        amount.fill(loan_amount)
        control = self.page.locator("[class*='-control']")
        if control.count():
            control.first.click()
            self.page.wait_for_timeout(600)
            option = self.page.locator("[class*='-option']")
            if option.count():
                option.first.click()
        self.save_and_exit_button.click()

    # ── Documents ─────────────────────────────────────────────────────────────
    @allure.step("Upload a document")
    def upload_document(self, file_path: str):
        self.doc_file_input.first.set_input_files(file_path)
