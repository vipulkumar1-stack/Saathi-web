import allure
import pytest
from playwright.sync_api import Page, expect  # type: ignore[import-not-found]
from pages.home_page import HomePage
from pages.documents_page import DocumentsPage
from config.config import RECOMMENDED_DOCS_DATA


@allure.feature("Recommended Docs")
class TestRecommendedDocs:

    def _open_docs_form(self, logged_in_page: Page, lead_id: str) -> DocumentsPage:
        """Open the lead, navigate to Documents, and open the recommended-docs form."""
        home = HomePage(logged_in_page)
        home.search_lead(lead_id)
        lead_page = home.open_lead_in_new_tab(lead_id)
        docs = DocumentsPage(lead_page)
        docs.open_documents_tab()
        docs.open_recommended_docs_form()
        return docs

    @allure.story("Get Recommended Doc List successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_get_recommended_docs_successfully(self, logged_in_page: Page, recommended_docs_lead_id: str):
        """Fill all four fields and submit twice; the Success toast should appear."""
        docs = self._open_docs_form(logged_in_page, recommended_docs_lead_id)
        docs.fill_and_submit({**RECOMMENDED_DOCS_DATA, "lead_id": recommended_docs_lead_id})
        expect(docs.success_toast).to_be_visible()
