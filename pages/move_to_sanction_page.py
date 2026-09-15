import allure
from playwright.sync_api import Page
from pages.move_to_login_page import MoveToLoginPage
from config.constants import MoveToSanction as Msg


class MoveToSanctionPage(MoveToLoginPage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.sanction_id_input = page.get_by_role("textbox", name="Enter Sanction ID")
        self.success_toast = page.get_by_text(Msg.SUCCESS, exact=True)
        self.error_toast_loan_amount = page.get_by_text(Msg.ERROR_LOAN_AMOUNT, exact=True)
        self.error_toast_sanction_id_format = page.get_by_text(Msg.ERROR_SANCTION_ID_FORMAT, exact=True)

    def _error_toasts(self) -> list:
        # Override — the sanction form's own copy differs from Move To
        # Login's ("Sanction Amount is required" vs "Login Amount is
        # required"), so the inherited toasts never match and _submit()
        # would raise a bogus "no toast recognised" error on a real
        # validation failure.
        return [self.error_toast_loan_amount, self.error_toast_sanction_id_format]

    @allure.step("Fill sanction ID")
    def fill_sanction_id(self, sanction_id: str):
        self.sanction_id_input.click()
        self.sanction_id_input.fill(sanction_id)
        self._assert_filled(self.sanction_id_input, sanction_id, "Sanction ID")

    @allure.step("Fill and submit Move To Sanction form")
    def fill_and_submit(self, data: dict):
        if data.get("loan_amount"):
            self.fill_loan_amount(data["loan_amount"])
        if data.get("select_date", True):
            self.select_today_date(data.get("sanction_date") or None)
        if self._is_empty("Select Bank") and data.get("bank_search"):
            self.select_bank(data["bank_search"], data["bank_name"])
        # The banker field may load asynchronously after bank selection; wait up to
        # 5 s for its placeholder to appear before deciding whether to select it.
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
            try:
                self.page.get_by_text("Select Branch", exact=True).wait_for(state="visible", timeout=5000)
            except Exception:
                pass
            if self._is_empty("Select Branch"):
                self.select_branch(data["branch"])
                self.page.wait_for_timeout(500)
        if data.get("sanction_id"):
            if self.sanction_id_input.count() == 0:
                raise AssertionError("Sanction ID field is not present on the Move To Sanction form")
            if not self.sanction_id_input.is_enabled():
                if not data.get("loan_amount"):
                    # Intentional: the field is gated on a loan amount having
                    # been entered, and this test case deliberately omits the
                    # amount — leaving Sanction ID unfilled is the expected
                    # path, not a framework failure.
                    pass
                else:
                    raise AssertionError(
                        "Sanction ID field is disabled despite a loan amount "
                        f"({self.loan_amount_input.input_value()!r}) already being entered"
                    )
            else:
                self.fill_sanction_id(data["sanction_id"])
        self._submit()
