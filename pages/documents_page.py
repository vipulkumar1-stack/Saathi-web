import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class DocumentsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.documents_tab_button = page.get_by_role("button", name="Documents")
        self.get_rec_docs_button  = page.get_by_role("button", name="Get Recommended Doc List")
        # The page also contains a promotional div with role=button. Restrict
        # this locator to the form's literal Submit button so it remains unique.
        self.submit_button        = page.get_by_role("button", name="Submit", exact=True)
        self.success_toast        = page.get_by_text("Success")
        self.select_placeholder   = page.get_by_text("Select...", exact=True)

    @allure.step("Open Documents tab")
    def open_documents_tab(self):
        self.documents_tab_button.click()
        self.get_rec_docs_button.wait_for(state="visible")

    @allure.step("Open Get Recommended Doc List form")
    def open_recommended_docs_form(self):
        self.get_rec_docs_button.click()
        self.submit_button.wait_for(state="visible")

    def _select_visible_option(self, value: str):
        self.select_placeholder.first.click()
        self.page.get_by_text(value, exact=True).click()

    @allure.step("Select employment type: {value}")
    def select_employment_type(self, value: str):
        if not self.select_placeholder.count():
            return
        self._select_visible_option(value)

    @allure.step("Select co-applicant: {value}")
    def select_co_applicant(self, value: str):
        if not self.select_placeholder.count():
            return
        self._select_visible_option(value)

    @allure.step("Select doc type: {value}")
    def select_doc_type(self, value: str):
        if not self.select_placeholder.count():
            return
        self._select_visible_option(value)

    @allure.step("Select property status: {value}")
    def select_property_status(self, value: str):
        if not self.select_placeholder.count():
            return
        self._select_visible_option(value)

    @allure.step("Submit recommended docs form")
    def submit(self):
        expect(self.submit_button).to_be_enabled()
        self.submit_button.click()   # step 1: fetch recommended doc list
        expect(self.submit_button).to_be_enabled()
        self.submit_button.click()   # step 2: confirm / apply to lead

    @allure.step("Fill and submit recommended docs form")
    def fill_and_submit(self, data: dict):
        self.select_employment_type(data["employment_type"])
        self.select_co_applicant(data["co_applicant"])
        self.select_doc_type(data["doc_type"])
        self.select_property_status(data["property_status"])
        self.submit()
