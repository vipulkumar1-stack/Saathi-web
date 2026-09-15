import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.constants import MarkAsLost as Msg


class MarkAsLostPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.comment_input   = page.get_by_role("textbox", name="Comment")
        self.save_button     = page.get_by_role("button", name="Save")
        self.error_toast_reason  = page.get_by_text(Msg.ERROR_REASON, exact=True)
        self.error_toast_comment = page.get_by_text(Msg.ERROR_COMMENT, exact=True)
        self.success_toast       = page.get_by_text(Msg.SUCCESS, exact=True)

    @allure.step("Select reason: {reason}")
    def select_reason(self, reason: str):
        # The "Close Lead / Mark as Lost" modal has no field <label>, so open_select
        # (which anchors on a label) can't find it. Scope to the "List Of Reason"
        # placeholder instead. The control is a React Select with app-generated class
        # names (e.g. css-xxx-control), so match the generic '-control' fragment —
        # NOT a 'react-select__' prefix, which this app does not emit.
        control = self.page.locator("[class*='-control']").filter(
            has=self.page.get_by_text("List Of Reason")
        )
        control.click()
        # The available reasons vary by lead state and change over time, so we don't
        # search for a specific label (e.g. "Customer not interested" is no longer
        # offered). Any valid reason satisfies the form, so pick the first option.
        self.choose_first_option()

    @allure.step("Fill comment")
    def fill_comment(self, comment: str):
        self.comment_input.wait_for(state="visible")
        self.comment_input.click()
        self.comment_input.fill(comment)

    @allure.step("Fill and submit Mark as Lost form")
    def fill_and_submit(self, data: dict):
        if data.get("reason"):
            self.select_reason(data["reason"])
        self.save_button.click()
        if data.get("comment"):
            self.fill_comment(data["comment"])
            self.save_button.click()
