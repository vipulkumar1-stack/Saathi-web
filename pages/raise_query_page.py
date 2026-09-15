import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.constants import RaiseQuery as Msg


class RaiseQueryPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # All form elements live inside a support widget iframe
        self._frame = page.frame_locator('[data-testid="widget-frame"]')

        self.issue_input       = self._frame.get_by_test_id("cf_issue").get_by_test_id("downshift-input")
        self.subissue_input    = self._frame.get_by_test_id("cf_subissue").get_by_test_id("downshift-input")
        self.description_input = self._frame.get_by_test_id("text-area-input")
        self.submit_button     = self._frame.get_by_test_id("form-button")
        self.success_message   = self._frame.get_by_text(Msg.SUCCESS, exact=False)

    @allure.step("Navigate to Help & Support")
    def go_to_help_support(self):
        self.page.get_by_role("link", name="tools Help & Support").click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Open Raise a Query form")
    def open_raise_query(self):
        self.page.get_by_text("Raise a Query", exact=True).click()
        self.issue_input.wait_for(state="visible")

    @allure.step("Select issue type: {issue}")
    def select_issue(self, issue: str):
        self.issue_input.click()
        self._frame.get_by_role("option", name=issue).click()

    @allure.step("Select sub-issue: {subissue}")
    def select_subissue(self, subissue: str):
        self.subissue_input.click()
        self._frame.get_by_role("option", name=subissue).click()

    @allure.step("Fill description")
    def fill_description(self, text: str):
        self.description_input.click()
        self.description_input.fill(text)

    @allure.step("Submit query")
    def submit(self):
        self.submit_button.click()

    @allure.step("Fill and submit Raise a Query form")
    def fill_and_submit(self, data: dict):
        self.select_issue(data["issue"])
        self.select_subissue(data["subissue"])
        self.fill_description(data["description"])
        self.submit()
