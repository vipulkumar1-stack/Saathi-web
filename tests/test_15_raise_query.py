import allure
import pytest
from playwright.sync_api import Page, expect
from pages.raise_query_page import RaiseQueryPage
from config.config import RAISE_QUERY_DATA


@allure.feature("Raise a Query")
class TestRaiseQuery:

    def _open_form(self, logged_in_page: Page) -> RaiseQueryPage:
        page_obj = RaiseQueryPage(logged_in_page)
        page_obj.go_to_help_support()
        page_obj.open_raise_query()
        return page_obj

    @allure.story("Validation: Issue type is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_raise_query_without_issue_type(self, logged_in_page: Page):
        """Submitting the form without selecting an issue type should not show the success message."""
        form = self._open_form(logged_in_page)
        form.fill_description(RAISE_QUERY_DATA["description"])
        form.submit()
        expect(form.success_message).not_to_be_visible()

    @allure.story("Validation: Description is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_raise_query_without_description(self, logged_in_page: Page):
        """Submitting the form without a description should not show the success message."""
        form = self._open_form(logged_in_page)
        form.select_issue(RAISE_QUERY_DATA["issue"])
        form.select_subissue(RAISE_QUERY_DATA["subissue"])
        form.submit()
        expect(form.success_message).not_to_be_visible()

    @allure.story("Query raised successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_raise_query_successfully(self, logged_in_page: Page):
        """Filling all fields and submitting shows 'Thanks for letting us know! We'll reach out to you soon.'"""
        form = self._open_form(logged_in_page)
        form.fill_and_submit(RAISE_QUERY_DATA)
        expect(form.success_message).to_be_visible()

    @allure.story("Rapid double submit is debounced")
    @allure.severity(allure.severity_level.NORMAL)
    def test_rapid_double_submit_is_debounced(self, logged_in_page: Page):
        """A second immediate click on Submit does not trigger a duplicate submission."""
        form = self._open_form(logged_in_page)
        form.select_issue(RAISE_QUERY_DATA["issue"])
        form.select_subissue(RAISE_QUERY_DATA["subissue"])
        form.fill_description(RAISE_QUERY_DATA["description"])
        form.submit()
        assert form.submit_button.is_disabled(), "Submit button should be disabled immediately after first click"
        expect(form.success_message).to_be_visible()
