import allure
import pytest
from playwright.sync_api import Page, expect
from pages.home_page import HomePage
from pages.lead_detail_page import LeadDetailPage
from config.config import LEAD_DETAIL_DATA
from config.constants import LeadDetail as Msg

# Minimal valid PDF used to exercise the Documents upload (accept=image/*,.pdf).
_PDF_BYTES = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF"


def _open_lead(logged_in_page: Page, lead_id: str) -> LeadDetailPage:
    home = HomePage(logged_in_page)
    home.search_lead(lead_id)
    lead_page = home.open_lead_in_new_tab(lead_id)
    lead_page.wait_for_load_state("networkidle")
    lead_page.wait_for_timeout(2000)
    return LeadDetailPage(lead_page)


@allure.feature("Lead Detail")
class TestLeadDetail:
    """Lead detail page: Details/Documents/History tabs, Remarks, the edit wizard,
    and Reopen (for a lost lead). Runs on the created lead in a full run, else on
    LEAD_DETAIL_ID; Reopen uses a lost lead (REOPEN_LEAD_ID / after mark-as-lost)."""

    # ── Details tab (#8) ──────────────────────────────────────────────────────
    @allure.story("Details tab shows the lead's info cards")
    @allure.severity(allure.severity_level.NORMAL)
    def test_details_tab_shows_cards(self, logged_in_page: Page, lead_detail_id: str):
        """The Details tab shows Loan / Customer / Income / Property cards."""
        detail = _open_lead(logged_in_page, lead_detail_id)
        detail.open_details_tab()
        expect(detail.loan_details_card).to_be_visible()
        expect(detail.customer_details_card).to_be_visible()
        expect(detail.income_details_card).to_be_visible()
        expect(detail.property_details_card).to_be_visible()

    @allure.story("Details edit wizard opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_wizard_opens(self, logged_in_page: Page, lead_detail_id: str):
        """The edit pencil opens the multi-step edit wizard (Save & Exit / Next)."""
        detail = _open_lead(logged_in_page, lead_detail_id)
        detail.open_edit()
        expect(detail.edit_heading).to_be_visible()
        expect(detail.save_and_exit_button).to_be_visible()
        expect(detail.next_button).to_be_visible()

    @allure.story("Editing loan details saves successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_edit_loan_details_saves(self, logged_in_page: Page, lead_detail_id: str):
        """Editing loan details and clicking Save & Exit shows a success toast."""
        detail = _open_lead(logged_in_page, lead_detail_id)
        detail.open_edit()
        detail.edit_loan_details_and_save(LEAD_DETAIL_DATA["loan_amount"])
        expect(detail.toast(Msg.EDIT_SUCCESS)).to_be_visible()

    # ── History tab (#7) ──────────────────────────────────────────────────────
    @allure.story("History tab shows the activity timeline")
    @allure.severity(allure.severity_level.NORMAL)
    def test_history_tab_shows_timeline(self, logged_in_page: Page, lead_detail_id: str):
        """The History tab lists timeline entries, each with a 'BY <author>' line."""
        detail = _open_lead(logged_in_page, lead_detail_id)
        detail.open_history_tab()
        expect(detail.history_entries().first).to_be_visible()

    # ── Remarks (#6) ──────────────────────────────────────────────────────────
    @allure.story("Remarks modal opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_remarks_modal_opens(self, logged_in_page: Page, lead_detail_id: str):
        """Clicking Remarks opens a modal with a text area and Save button."""
        detail = _open_lead(logged_in_page, lead_detail_id)
        detail.open_remarks()
        expect(detail.modal_textarea.first).to_be_visible()
        expect(detail.modal_save_button).to_be_visible()

    @allure.story("Validation: remark text is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_remark_without_text_shows_error(self, logged_in_page: Page, lead_detail_id: str):
        """Saving an empty remark shows 'Please enter a remark'."""
        detail = _open_lead(logged_in_page, lead_detail_id)
        detail.open_remarks()
        detail.save_remark()
        expect(detail.toast(Msg.REMARK_EMPTY)).to_be_visible()

    @allure.story("Remark added successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_add_remark_successfully(self, logged_in_page: Page, lead_detail_id: str):
        """Entering a remark and saving shows 'Remark saved successfully'."""
        detail = _open_lead(logged_in_page, lead_detail_id)
        detail.open_remarks()
        detail.fill_remark(LEAD_DETAIL_DATA["remark"])
        detail.save_remark()
        expect(detail.toast(Msg.REMARK_SUCCESS)).to_be_visible()

    # ── Documents tab (#9) ─────────────────────────────────────────────────────
    @allure.story("Documents tab exposes an upload control")
    @allure.severity(allure.severity_level.NORMAL)
    def test_documents_tab_shows_upload(self, logged_in_page: Page, lead_detail_id: str):
        """The Documents tab has file inputs restricted to images/PDF."""
        detail = _open_lead(logged_in_page, lead_detail_id)
        detail.open_documents_tab()
        assert detail.doc_file_input.count() > 0
        expect(detail.doc_file_input.first).to_have_attribute("accept", "image/*,.pdf")

    @allure.story("Rapid tab switching and back/forward do not break the page")
    @allure.severity(allure.severity_level.MINOR)
    def test_rapid_tab_switch_and_back_forward(self, logged_in_page: Page, lead_detail_id: str):
        """Switching Documents -> History -> Details in quick succession, then
        navigating back and forward, should leave the page on a lead-detail
        URL with the Details cards still rendered — no stuck/blank state.
        Revived from
        tests/_scratch_explore.py::test_e_lead_detail_rapid_tabs_and_backforward,
        which only printed the observed state at each step."""
        detail = _open_lead(logged_in_page, lead_detail_id)
        detail.open_documents_tab()
        detail.open_history_tab()
        detail.open_details_tab()
        expect(detail.loan_details_card).to_be_visible()

        lead_page = detail.page
        url_before_back = lead_page.url
        lead_page.go_back()
        lead_page.wait_for_timeout(1500)
        lead_page.go_forward()
        lead_page.wait_for_timeout(1500)
        assert lead_page.url == url_before_back, (
            f"Expected go_back()+go_forward() to return to {url_before_back!r}, "
            f"got {lead_page.url!r}"
        )

    @allure.story("An edit left unsaved is discarded when navigating away")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_field_discarded_when_navigating_away_without_saving(self, logged_in_page: Page, lead_detail_id: str):
        """Typing into an edit-wizard field, then navigating away without
        saving, should discard the change — reopening the wizard must show
        the original value, not the unsaved one. Revived from
        tests/_scratch_explore.py::test_f_edit_field_navigate_away_data_loss,
        which only printed the filled value and post-navigation URL without
        checking whether the edit actually persisted."""
        detail = _open_lead(logged_in_page, lead_detail_id)
        detail.open_edit()
        amount_box = detail.page.get_by_role("textbox").first
        original_value = amount_box.input_value()
        amount_box.fill("999999999")
        # The field re-renders through an Indian lakh/crore grouping mask (e.g.
        # '999999999' -> '99,99,99,999'), so compare digits, not the raw string.
        assert LeadDetailPage.digits_only(amount_box.input_value()) == "999999999"

        detail.page.go_back()
        detail.page.wait_for_timeout(1500)
        detail.open_edit()
        reopened_box = detail.page.get_by_role("textbox").first
        expect(reopened_box).to_have_value(original_value)

    @allure.story("Documents tab renders even for a lead with no file inputs yet")
    @allure.severity(allure.severity_level.MINOR)
    def test_documents_tab_loads_without_recommended_docs(self, logged_in_page: Page, lead_detail_id: str):
        """Opening Documents should not error out regardless of whether the
        lead currently has any recommended-docs file inputs — the tab itself
        must stay usable either way. Revived from
        tests/_scratch_explore.py::test_g_docs_no_recommended_docs_lead, which
        only printed the file-input count."""
        detail = _open_lead(logged_in_page, lead_detail_id)
        detail.open_documents_tab()
        expect(detail.documents_tab).to_be_visible()

    @allure.story("A file type outside the accepted list is not reported as uploaded")
    @allure.severity(allure.severity_level.NORMAL)
    def test_invalid_file_type_upload_not_reported_success(self, logged_in_page: Page, lead_detail_id: str, tmp_path):
        """The Documents input restricts selection to accept='image/*,.pdf'
        (see test_documents_tab_shows_upload), but that attribute is only a
        client-side hint — set_input_files can still force a non-matching
        file into the input. When that happens, the app must not report it
        as a successful upload. Revived from
        tests/_scratch_explore.py::test_h_invalid_file_type_upload, which
        only printed the files-length and a raw "error" text count."""
        detail = _open_lead(logged_in_page, lead_detail_id)
        detail.open_documents_tab()
        bad_file = tmp_path / "bad.exe"
        bad_file.write_bytes(b"MZ\x00\x00fakeexe")
        detail.doc_file_input.first.set_input_files(str(bad_file))
        logged_in_page.wait_for_timeout(2000)
        assert not detail.toast(Msg.DOC_SUCCESS).is_visible(), (
            "A .exe file forced past the accept='image/*,.pdf' filter should "
            "not be reported as successfully uploaded"
        )

    @allure.story("Documents upload accepts a PDF")
    @allure.severity(allure.severity_level.NORMAL)
    def test_document_upload_accepts_pdf(self, logged_in_page: Page, lead_detail_id: str, tmp_path):
        """Selecting a PDF populates the upload control (the app then uploads it).

        The post-upload success toast is state/lead-dependent (some doc slots emit
        'Document uploaded successfully', others none), so this asserts the control
        accepted the file rather than a flaky toast."""
        detail = _open_lead(logged_in_page, lead_detail_id)
        detail.open_documents_tab()
        pdf = tmp_path / "doc.pdf"
        pdf.write_bytes(_PDF_BYTES)
        detail.upload_document(str(pdf))
        assert detail.doc_file_input.first.evaluate("el => el.files.length") == 1

    # ── Reopen (#5) — needs a LOST lead ────────────────────────────────────────
    @allure.story("A lost lead shows the Reopen control")
    @allure.severity(allure.severity_level.NORMAL)
    def test_lost_lead_shows_reopen(self, logged_in_page: Page, reopen_lead_id: str):
        """A lost lead shows a 'Lost' badge and a Reopen button."""
        detail = _open_lead(logged_in_page, reopen_lead_id)
        expect(detail.reopen_button).to_be_visible()
        expect(detail.lost_badge.first).to_be_visible()

    @allure.story("Validation: reopen remarks are required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_reopen_without_remarks_shows_error(self, logged_in_page: Page, reopen_lead_id: str):
        """Saving the Re-open modal with no remarks shows 'Please enter remarks'."""
        detail = _open_lead(logged_in_page, reopen_lead_id)
        detail.open_reopen()
        detail.save_reopen()
        expect(detail.toast(Msg.REOPEN_EMPTY)).to_be_visible()

    @allure.story("Lead reopened successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_reopen_lead_successfully(self, logged_in_page: Page, reopen_lead_id: str):
        """Entering remarks and saving the Re-open modal shows a success toast.
        NOTE: this reopens the lead (consuming its Lost state), so it needs a
        freshly-lost lead — run it after mark-as-lost or point REOPEN_LEAD_ID at
        a lost lead."""
        detail = _open_lead(logged_in_page, reopen_lead_id)
        detail.open_reopen()
        detail.fill_reopen_remarks("Reopened via automated test")
        detail.save_reopen()
        expect(detail.toast(Msg.REOPEN_SUCCESS)).to_be_visible()
