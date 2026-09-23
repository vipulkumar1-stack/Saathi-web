# Leads list page: tests/test_13_team_filter.py, test_12_search_filter.py,
# test_17_edit_columns_advanced_filters.py, test_07_reassign_leads.py,
# test_18_reports_advanced_filters.py, test_09b_lead_detail.py,
# test_08_recommended_docs.py.

.PHONY: columns-and-filters lead-detail

##@ Leads page

# ── My Team Filter tests (2) ───────────────────────────────────────────────────

team-filter: ## My Team filter tests
	pytest tests/test_13_team_filter.py -v

team-filter-date:
	pytest tests/test_13_team_filter.py::TestTeamFilter::test_filter_by_date -v

team-filter-city:
	pytest tests/test_13_team_filter.py::TestTeamFilter::test_filter_by_city -v

# ── Search Filter tests (3) ────────────────────────────────────────────────────

search-filter: ## Lead search filter tests
	pytest tests/test_12_search_filter.py -v

search-filter-date:
	pytest tests/test_12_search_filter.py::TestSearchFilter::test_filter_by_date -v

search-filter-city:
	pytest tests/test_12_search_filter.py::TestSearchFilter::test_filter_by_city -v

search-filter-bank:
	pytest tests/test_12_search_filter.py::TestSearchFilter::test_filter_by_bank -v

# ── Edit Columns tests (1) ─────────────────────────────────────────────────────

edit-columns: ## Edit Columns panel test
	pytest tests/test_17_edit_columns_advanced_filters.py::TestEditColumns -v

edit-columns-panel-opens:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestEditColumns::test_edit_columns_panel_opens -v

# ── Advanced Filters tests (14) ────────────────────────────────────────────────

advanced-filters: ## All Advanced Filters dropdown tests
	pytest tests/test_17_edit_columns_advanced_filters.py::TestAdvancedFilters -v

advanced-filters-source:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestAdvancedFilters::test_source_dropdown_opens -v

advanced-filters-sub-source:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestAdvancedFilters::test_sub_source_dropdown_opens -v

advanced-filters-banks:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestAdvancedFilters::test_banks_dropdown_opens -v

advanced-filters-property-type:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestAdvancedFilters::test_property_type_dropdown_opens -v

advanced-filters-product-type:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestAdvancedFilters::test_product_type_dropdown_opens -v

advanced-filters-sub-type:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestAdvancedFilters::test_sub_type_dropdown_opens -v

advanced-filters-fulfillment:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestAdvancedFilters::test_fulfillment_dropdown_opens -v

advanced-filters-cities:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestAdvancedFilters::test_cities_dropdown_opens -v

advanced-filters-designation:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestAdvancedFilters::test_designation_dropdown_opens -v

advanced-filters-teammate:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestAdvancedFilters::test_teammate_dropdown_opens -v

advanced-filters-assigned-to:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestAdvancedFilters::test_assigned_to_dropdown_opens -v

advanced-filters-checklist-item:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestAdvancedFilters::test_checklist_item_dropdown_opens -v

advanced-filters-status:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestAdvancedFilters::test_status_dropdown_opens -v

advanced-filters-sub-status:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestAdvancedFilters::test_sub_status_dropdown_opens -v

# Run Edit Columns + all Advanced Filters together
columns-and-filters: ## Edit Columns + Advanced Filters together
	pytest tests/test_17_edit_columns_advanced_filters.py -v

# ── Recommended Docs tests (1) ────────────────────────────────────────────────

recommended-docs: ## Recommended Docs test
	pytest tests/test_08_recommended_docs.py -v

recommended-docs-success:
	pytest tests/test_08_recommended_docs.py::TestRecommendedDocs::test_get_recommended_docs_successfully -v

# ── Reassign Leads tests (4) ───────────────────────────────────────────────────

reassign-leads: ## Reassign Leads tests
	pytest tests/test_07_reassign_leads.py -v

reassign-leads-empty-search:
	pytest tests/test_07_reassign_leads.py::TestReassignLeads::test_search_with_empty_text -v

reassign-leads-no-lead:
	pytest tests/test_07_reassign_leads.py::TestReassignLeads::test_assign_lead_disabled_without_lead_selected -v

reassign-leads-no-assignee:
	pytest tests/test_07_reassign_leads.py::TestReassignLeads::test_assign_lead_disabled_without_assignee_selected -v

reassign-leads-success:
	pytest tests/test_07_reassign_leads.py::TestReassignLeads::test_reassign_lead_successfully -v

# ── Reports Advanced Filters tests (7) ────────────────────────────────────────

reports-filters: ## Reports Advanced Filters dropdown tests
	pytest tests/test_18_reports_advanced_filters.py -v

reports-filters-filter-1:
	pytest tests/test_18_reports_advanced_filters.py::TestReportsAdvancedFilters::test_filter_1_dropdown_opens -v

reports-filters-filter-2:
	pytest tests/test_18_reports_advanced_filters.py::TestReportsAdvancedFilters::test_filter_2_dropdown_opens -v

reports-filters-filter-3:
	pytest tests/test_18_reports_advanced_filters.py::TestReportsAdvancedFilters::test_filter_3_dropdown_opens -v

reports-filters-source:
	pytest tests/test_18_reports_advanced_filters.py::TestReportsAdvancedFilters::test_source_dropdown_opens -v

reports-filters-filter-5:
	pytest tests/test_18_reports_advanced_filters.py::TestReportsAdvancedFilters::test_filter_5_dropdown_opens -v

reports-filters-sub-source:
	pytest tests/test_18_reports_advanced_filters.py::TestReportsAdvancedFilters::test_sub_source_dropdown_opens -v

reports-filters-banks:
	pytest tests/test_18_reports_advanced_filters.py::TestReportsAdvancedFilters::test_banks_dropdown_opens -v

# ── Lead Detail tests (16) ─────────────────────────────────────────────────────

lead-detail: ## Lead Detail tests
	pytest tests/test_09b_lead_detail.py -v

lead-detail-details-tab:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_details_tab_shows_cards -v

lead-detail-edit-wizard-opens:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_edit_wizard_opens -v

lead-detail-edit-loan-saves:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_edit_loan_details_saves -v

lead-detail-history-tab:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_history_tab_shows_timeline -v

lead-detail-remarks-modal-opens:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_remarks_modal_opens -v

lead-detail-remark-no-text:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_remark_without_text_shows_error -v

lead-detail-add-remark-success:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_add_remark_successfully -v

lead-detail-documents-tab:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_documents_tab_shows_upload -v

lead-detail-rapid-tab-switch:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_rapid_tab_switch_and_back_forward -v

lead-detail-edit-discarded-on-nav:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_edit_field_discarded_when_navigating_away_without_saving -v

lead-detail-documents-no-recommended-docs:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_documents_tab_loads_without_recommended_docs -v

lead-detail-invalid-file-type-bug:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_invalid_file_type_upload_not_reported_success -v

lead-detail-document-upload-pdf:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_document_upload_accepts_pdf -v

lead-detail-lost-shows-reopen:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_lost_lead_shows_reopen -v

lead-detail-reopen-no-remarks:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_reopen_without_remarks_shows_error -v

lead-detail-reopen-success:
	pytest tests/test_09b_lead_detail.py::TestLeadDetail::test_reopen_lead_successfully -v
