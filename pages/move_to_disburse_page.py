import allure
from playwright.sync_api import Page
from pages.move_to_login_page import MoveToLoginPage
from config.constants import MoveToDisburse as Msg


class MoveToDisbursePage(MoveToLoginPage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.loan_amount_input = page.get_by_role("textbox", name="₹ 0", exact=True)
        self.balance_transfer_checkbox = page.get_by_role("checkbox", name="Balance Transfer")
        self.disbursal_date_input = page.locator("input[name='disbursal_date_0']")
        self.disbursed_id_input = page.get_by_role("textbox", name="Enter Disbursed ID")
        self.congratulations_popup        = page.get_by_text(Msg.SUCCESS, exact=True)
        # [class*=...] matches the component+element name without the build hash.
        # The full class looks like: disbursementSuccessModal_closeButton__<hash>
        # Using the stable prefix means this survives every frontend rebuild.
        self.close_button = page.locator("button[class*='disbursementSuccessModal_closeButton']")
        self.error_toast_disbursed_id     = page.get_by_text(Msg.ERROR_DISBURSED_ID)
        self.error_toast_amount_date      = page.get_by_text(Msg.ERROR_AMOUNT_DATE)
        self.error_toast_exceeds_sanction = page.get_by_text(Msg.ERROR_EXCEEDS)

    def _error_toasts(self) -> list:
        # Override — the inherited login toasts never match a disburse-stage
        # error, so _submit() would raise a bogus "no toast recognised" error
        # even when one of these IS visible.
        return [self.error_toast_disbursed_id, self.error_toast_amount_date,
                self.error_toast_exceeds_sanction]

    def _success_indicators(self) -> list:
        # Override — confirmed live: the inherited `success_toast` ("Email
        # sent successfully") fires here as a generic email-confirmation step
        # even when the disbursement itself is later rejected (e.g. amount
        # exceeds sanction). Treating it as "done" made _submit() exit before
        # the real rejection toast had a chance to render. The actual
        # completion signal for this form is `congratulations_popup`.
        return [self.congratulations_popup]

    @allure.step("Fill disbursed ID")
    def fill_disbursed_id(self, disbursed_id: str):
        self.disbursed_id_input.click()
        self.disbursed_id_input.fill(disbursed_id)
        self._assert_filled(self.disbursed_id_input, disbursed_id, "Disbursed ID")

    @allure.step("Fill and submit Move To Disburse form")
    def fill_and_submit(self, data: dict):
        self.balance_transfer_checkbox.check()
        # Checking Balance Transfer triggers an async re-render that re-applies the
        # pre-filled amount and resets branch/banker. Wait for it to settle BEFORE
        # filling the amount — otherwise the digits typed by fill_loan_amount
        # concatenate with the re-applied value, producing a wildly inflated amount
        # (e.g. ₹1,00,00,00,00,000) that exceeds the sanction and blocks submission.
        self.page.wait_for_timeout(2000)
        if data.get("loan_amount"):
            self.fill_loan_amount(data["loan_amount"])
        if data.get("select_disbursal_date", True):
            self._pick_date(self.disbursal_date_input, data.get("disbursal_date") or None)
        if self._is_empty("Select Bank") and data.get("bank_search"):
            self.select_bank(data["bank_search"], data["bank_name"])
        # Re-render resets banker to empty; the placeholder may take longer than the
        # initial 2 s wait to appear — wait up to 5 s before checking so we don't
        # mistake a not-yet-rendered field for a pre-filled one.
        if data.get("banker"):
            try:
                self.page.get_by_text("Select Banker", exact=True).wait_for(state="visible", timeout=5000)
            except Exception:
                pass  # already pre-filled or field not present
        banker_selected = not self._is_empty("Select Banker")
        if self._is_empty("Select Banker") and data.get("banker"):
            self.select_banker(data["banker"])
            banker_selected = True
        if banker_selected and data.get("branch"):
            # After banker selection the branch field reloads; wait for its placeholder
            # to appear before checking whether a selection is still needed.
            try:
                self.page.get_by_text("Select Branch", exact=True).wait_for(state="visible", timeout=5000)
            except Exception:
                pass
            if self._is_empty("Select Branch"):
                self.select_branch(data["branch"])
                self.page.wait_for_timeout(500)
        if data.get("disbursed_id"):
            self.fill_disbursed_id(data["disbursed_id"])
        self._submit()
