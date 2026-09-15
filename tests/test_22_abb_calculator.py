import os
import allure
from playwright.sync_api import Page, expect
from pages.abb_calculator_page import AbbCalculatorPage


# A tiny PDF fixture created on the fly, used only to prove the file input
# accepts a PDF. It is not a real bank statement, so no ABB result is asserted.
_PDF_BYTES = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF"


@allure.feature("ABB Calculator")
class TestAbbCalculator:
    """ABB Calculator — bank-statement upload tool. The file input is restricted
    to PDF and a real statement is needed for a parsed result, so these tests
    cover the upload UI, the PDF-only restriction, and the instructional copy."""

    def _open(self, logged_in_page: Page) -> AbbCalculatorPage:
        page_obj = AbbCalculatorPage(logged_in_page)
        page_obj.go_to_my_tools()
        page_obj.open_tool()
        return page_obj

    @allure.story("ABB tool opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_abb_tool_opens(self, logged_in_page: Page):
        """Opening the tool shows the ABB heading and the upload button."""
        abb = self._open(logged_in_page)
        expect(abb.heading).to_be_visible()
        expect(abb.upload_button).to_be_visible()

    @allure.story("ABB shows the upload prompt")
    @allure.severity(allure.severity_level.NORMAL)
    def test_abb_shows_intro_prompt(self, logged_in_page: Page):
        """The 'How would you like to share the income details?' prompt is shown."""
        abb = self._open(logged_in_page)
        expect(abb.intro_prompt).to_be_visible()

    @allure.story("ABB lists the statement requirements")
    @allure.severity(allure.severity_level.NORMAL)
    def test_abb_shows_statement_instructions(self, logged_in_page: Page):
        """The PDF-only / OD-CC / most-recent statement instructions are shown."""
        abb = self._open(logged_in_page)
        expect(abb.pdf_only_note).to_be_visible()
        expect(abb.od_cc_note).to_be_visible()
        expect(abb.recent_note).to_be_visible()

    @allure.story("ABB restricts uploads to PDF")
    @allure.severity(allure.severity_level.NORMAL)
    def test_abb_file_input_accepts_pdf_only(self, logged_in_page: Page):
        """The file input enforces PDF-only via accept='application/pdf'."""
        abb = self._open(logged_in_page)
        expect(abb.file_input.first).to_have_attribute("accept", "application/pdf")

    @allure.story("ABB accepts a PDF selection")
    @allure.severity(allure.severity_level.NORMAL)
    def test_abb_accepts_pdf_file(self, logged_in_page: Page, tmp_path):
        """Selecting a PDF populates the file input (upload control is wired up)."""
        abb = self._open(logged_in_page)
        pdf = tmp_path / "statement.pdf"
        pdf.write_bytes(_PDF_BYTES)
        abb.upload_statement(str(pdf))
        # The input now holds exactly one file.
        count = abb.file_input.first.evaluate("el => el.files.length")
        assert count == 1
