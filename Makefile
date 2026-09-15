ALLURE    := $(HOME)/allure/bin/allure
JAVA_HOME := /usr/lib/jvm/java-17-openjdk-amd64
export JAVA_HOME

# All recipes run out of the repo-local virtualenv created by `make install`.
# Prepending it to PATH means every bare `pytest` / `playwright` recipe below
# picks it up with no per-target changes, and silently falls back to whatever
# is on the ambient PATH when .venv/ does not exist yet.
VENV := $(CURDIR)/.venv
export PATH := $(VENV)/bin:$(PATH)

# Outer, coarse backstop for unattended full-suite runs, wrapping `all` /
# `headless` / `e2e` below — NOT the per-test timeout (see pytest.ini for
# that; this is a different, process-level layer). pytest.ini's per-test
# `timeout = 300` (SIGALRM) reliably bounds a stall that Playwright's own
# call raises out of cleanly, but proved (scratchpad probes, see the commit
# that added this) unable to bound one where the alarm has to interrupt an
# in-flight driver call: the interrupted call can leave the browser driver's
# IPC channel broken, and the context/browser `.close()` in fixture teardown
# then blocks forever on it with no further alarm left to interrupt IT (the
# 300s alarm is a single, non-repeating shot covering setup+call+teardown as
# one window). That is the one residual case an unattended overnight run
# could still wedge on indefinitely. SUITE_TIMEOUT is the real backstop for
# it: guarantees the whole process — including any half-wedged Chromium/
# driver — is torn down, at the cost of losing that run's report. Tune with
# `make all SUITE_TIMEOUT=45m`; --kill-after covers a process that ignores
# the initial SIGTERM (plausible for exactly this broken-IPC state).
SUITE_TIMEOUT ?= 90m
GUARD := timeout --kill-after=30s $(SUITE_TIMEOUT)

# Exported so the email report can name the target that produced it in its
# subject line (see reporters/email_reporter.py::_run_scope). MAKECMDGOALS is
# set by make itself to the goal(s) given on the command line.
export MAKECMDGOALS

# Bare `make` shows the help menu rather than running the first target (install).
.DEFAULT_GOAL := help

# These verb targets are commands, not files — declare phony so a same-named
# file/dir in the repo (e.g. `report`, `reports`) can never shadow them.
.PHONY: install all e2e headless followup columns-and-filters \
        stage-login stage-sanction stage-disburse \
        open-log-report open-excel-report open-report generate-report \
        allure-report open-reports reports report report-email check-email check-targets \
        lead-detail team-partners profile cibil abb-calculator apf-search \
        website-settings logout \
        reset-session clean help

# ── Setup ──────────────────────────────────────────────────────────────────────

install:
	python3 -m venv "$(VENV)"
	"$(VENV)/bin/pip" install -r requirements.txt
	"$(VENV)/bin/playwright" install chromium

# ── Run all tests ──────────────────────────────────────────────────────────────

all:
	$(GUARD) pytest
	

# Run only the happy-path tests (login → create lead → login stage → sanction → disburse → mark as lost)
e2e:
	$(GUARD) pytest -m e2e

# Run all tests without a visible browser window
headless:
	HEADLESS=true $(GUARD) pytest

# ── Run the happy path up to a chosen stage ─────────────────────────────────────
# Each target runs ONLY the happy-path (e2e-marked) cases needed to drive a lead
# up to and including the named stage. They are cumulative:
#   stage-login    → login → create lead → move to login
#   stage-sanction → … + move to sanction
#   stage-disburse → … + move to disburse  (full lifecycle)

# Stop at the Login stage
stage-login:
	pytest -m e2e tests/test_01_login.py tests/test_02_create_lead.py tests/test_03_move_to_login.py -v

# Stop at the Sanction stage
stage-sanction:
	pytest -m e2e tests/test_01_login.py tests/test_02_create_lead.py tests/test_03_move_to_login.py tests/test_04_move_to_sanction.py -v

# Stop at the Disburse stage (entire lead lifecycle)
stage-disburse:
	pytest -m e2e tests/test_01_login.py tests/test_02_create_lead.py tests/test_03_move_to_login.py tests/test_04_move_to_sanction.py tests/test_05_move_to_disburse.py -v

# ── Login tests (4) ────────────────────────────────────────────────────────────

login:
	pytest tests/test_01_login.py -v

login-page-loads:
	pytest tests/test_01_login.py::TestLogin::test_login_page_loads -v

login-no-mobile:
	pytest tests/test_01_login.py::TestLogin::test_submit_without_mobile -v

login-success:
	pytest tests/test_01_login.py::TestLogin::test_login_rejects_wrong_otp_then_succeeds -v

login-no-session-bug:
	pytest tests/test_01_login.py::TestLogin::test_direct_navigation_to_protected_page_without_session_bug -v

# ── Create Lead – Self Fulfilled tests (8) ─────────────────────────────────────

create-lead:
	pytest tests/test_02_create_lead.py -v

create-lead-form-opens:
	pytest tests/test_02_create_lead.py::TestCreateLead::test_create_lead_form_opens -v

create-lead-no-first-name:
	pytest tests/test_02_create_lead.py::TestCreateLead::test_submit_without_first_name -v

create-lead-no-last-name:
	pytest tests/test_02_create_lead.py::TestCreateLead::test_submit_without_last_name -v

create-lead-no-mobile:
	pytest tests/test_02_create_lead.py::TestCreateLead::test_submit_without_mobile -v

create-lead-no-loan-type:
	pytest tests/test_02_create_lead.py::TestCreateLead::test_submit_without_loan_type -v

create-lead-no-employment-type:
	pytest tests/test_02_create_lead.py::TestCreateLead::test_submit_without_employment_type -v

create-lead-no-city:
	pytest tests/test_02_create_lead.py::TestCreateLead::test_submit_without_city -v

create-lead-success:
	pytest tests/test_02_create_lead.py::TestCreateLead::test_create_lead_successful -v

create-lead-duplicate:
	pytest tests/test_02_create_lead.py::TestCreateLead::test_duplicate_mobile_shows_popup -v

# ── Lead Entry Mode tests (6) ───────────────────────────────────────────────────
# The redesigned Add New Lead modal replaced the "I will do it myself" /
# "Refer to Ambak" tabs with a fixed "type ambak" banner plus an Add Manually /
# Bulk Upload choice, and added an optional Purchase Type field. This replaces
# the retired test_02b_create_lead_refer.py / refer-to-ambak-* targets.

lead-entry-mode:
	pytest tests/test_02b_lead_entry_mode.py -v

lead-entry-mode-default:
	pytest tests/test_02b_lead_entry_mode.py::TestLeadEntryMode::test_add_manually_selected_by_default -v

lead-entry-mode-banner:
	pytest tests/test_02b_lead_entry_mode.py::TestLeadEntryMode::test_lead_type_banner_shows_ambak -v

lead-entry-mode-bulk-upload:
	pytest tests/test_02b_lead_entry_mode.py::TestLeadEntryMode::test_bulk_upload_switches_form -v

lead-entry-mode-switch-back:
	pytest tests/test_02b_lead_entry_mode.py::TestLeadEntryMode::test_switch_back_to_add_manually_restores_form -v

lead-entry-mode-purchase-type-optional:
	pytest tests/test_02b_lead_entry_mode.py::TestLeadEntryMode::test_purchase_type_is_optional -v

lead-entry-mode-purchase-type-selectable:
	pytest tests/test_02b_lead_entry_mode.py::TestLeadEntryMode::test_purchase_type_selectable -v

# ── Move to Login tests (11) ───────────────────────────────────────────────────

move-to-login:
	pytest tests/test_03_move_to_login.py -v

move-to-login-no-amount:
	pytest tests/test_03_move_to_login.py::TestMoveToLogin::test_move_to_login_without_loan_amount -v

move-to-login-no-bank:
	pytest tests/test_03_move_to_login.py::TestMoveToLogin::test_move_to_login_without_bank -v

move-to-login-no-login-id:
	pytest tests/test_03_move_to_login.py::TestMoveToLogin::test_move_to_login_without_login_id -v

move-to-login-no-date:
	pytest tests/test_03_move_to_login.py::TestMoveToLogin::test_move_to_login_without_date -v

move-to-login-no-branch:
	pytest tests/test_03_move_to_login.py::TestMoveToLogin::test_move_to_login_without_branch -v

move-to-login-no-banker:
	pytest tests/test_03_move_to_login.py::TestMoveToLogin::test_move_to_login_without_banker -v

move-to-login-success:
	pytest tests/test_03_move_to_login.py::TestMoveToLogin::test_move_lead_to_login -v

login-followup:
	pytest tests/test_03_move_to_login.py -k "followup" -v

login-followup-no-date:
	pytest tests/test_03_move_to_login.py::TestMoveToLogin::test_followup_without_date -v

login-followup-no-time:
	pytest tests/test_03_move_to_login.py::TestMoveToLogin::test_followup_without_time -v

login-followup-no-comment:
	pytest tests/test_03_move_to_login.py::TestMoveToLogin::test_followup_without_comment -v

login-followup-success:
	pytest tests/test_03_move_to_login.py::TestMoveToLogin::test_followup_scheduled_successfully -v

# ── Move to Sanction tests (9) ─────────────────────────────────────────────────

move-to-sanction:
	pytest tests/test_04_move_to_sanction.py -v

move-to-sanction-no-amount:
	pytest tests/test_04_move_to_sanction.py::TestMoveToSanction::test_move_to_sanction_without_loan_amount -v

move-to-sanction-no-sanction-id:
	pytest tests/test_04_move_to_sanction.py::TestMoveToSanction::test_move_to_sanction_without_sanction_id -v

move-to-sanction-no-date:
	pytest tests/test_04_move_to_sanction.py::TestMoveToSanction::test_move_to_sanction_without_date -v

move-to-sanction-date-disabled:
	pytest tests/test_04_move_to_sanction.py::TestMoveToSanction::test_sanction_dates_before_login_are_disabled -v

move-to-sanction-success:
	pytest tests/test_04_move_to_sanction.py::TestMoveToSanction::test_move_lead_to_sanction -v

sanction-followup:
	pytest tests/test_04_move_to_sanction.py -k "followup" -v

sanction-followup-no-date:
	pytest tests/test_04_move_to_sanction.py::TestMoveToSanction::test_followup_without_date -v

sanction-followup-no-time:
	pytest tests/test_04_move_to_sanction.py::TestMoveToSanction::test_followup_without_time -v

sanction-followup-no-comment:
	pytest tests/test_04_move_to_sanction.py::TestMoveToSanction::test_followup_without_comment -v

sanction-followup-success:
	pytest tests/test_04_move_to_sanction.py::TestMoveToSanction::test_followup_scheduled_successfully -v

# ── Move to Disburse tests (10) ────────────────────────────────────────────────

move-to-disburse:
	pytest tests/test_05_move_to_disburse.py -v

move-to-disburse-no-amount:
	pytest tests/test_05_move_to_disburse.py::TestMoveToDisburse::test_move_to_disburse_without_loan_amount -v

move-to-disburse-no-disbursed-id:
	pytest tests/test_05_move_to_disburse.py::TestMoveToDisburse::test_move_to_disburse_without_disbursed_id -v

move-to-disburse-no-disbursal-date:
	pytest tests/test_05_move_to_disburse.py::TestMoveToDisburse::test_move_to_disburse_without_disbursal_date -v

move-to-disburse-exceeds-sanction:
	pytest tests/test_05_move_to_disburse.py::TestMoveToDisburse::test_move_to_disburse_amount_exceeds_sanction -v

move-to-disburse-date-disabled:
	pytest tests/test_05_move_to_disburse.py::TestMoveToDisburse::test_disbursal_dates_before_sanction_are_disabled -v

move-to-disburse-success:
	pytest tests/test_05_move_to_disburse.py::TestMoveToDisburse::test_move_lead_to_disburse -v

disburse-followup:
	pytest tests/test_05_move_to_disburse.py -k "followup" -v

disburse-followup-no-date:
	pytest tests/test_05_move_to_disburse.py::TestMoveToDisburse::test_followup_without_date -v

disburse-followup-no-time:
	pytest tests/test_05_move_to_disburse.py::TestMoveToDisburse::test_followup_without_time -v

disburse-followup-no-comment:
	pytest tests/test_05_move_to_disburse.py::TestMoveToDisburse::test_followup_without_comment -v

disburse-followup-success:
	pytest tests/test_05_move_to_disburse.py::TestMoveToDisburse::test_followup_scheduled_successfully -v

# Run all followup tests across Login, Sanction, and Disburse stages
followup:
	pytest tests/test_03_move_to_login.py tests/test_04_move_to_sanction.py tests/test_05_move_to_disburse.py -k "followup" -v

# ── Add Teammate tests (4) ─────────────────────────────────────────────────────

add-teammate:
	pytest tests/test_10_add_teammate.py -v

add-teammate-no-name:
	pytest tests/test_10_add_teammate.py::TestAddTeammate::test_submit_without_full_name -v

add-teammate-no-mobile:
	pytest tests/test_10_add_teammate.py::TestAddTeammate::test_submit_without_mobile -v

add-teammate-no-designation:
	pytest tests/test_10_add_teammate.py::TestAddTeammate::test_submit_without_designation -v

add-teammate-success:
	pytest tests/test_10_add_teammate.py::TestAddTeammate::test_add_teammate_successful -v

# ── Add Sourcing Partner tests (4) ─────────────────────────────────────────────

add-sourcing-partner:
	pytest tests/test_11_add_sourcing_partner.py -v

add-sourcing-partner-no-name:
	pytest tests/test_11_add_sourcing_partner.py::TestAddSourcingPartner::test_submit_without_full_name -v

add-sourcing-partner-no-mobile:
	pytest tests/test_11_add_sourcing_partner.py::TestAddSourcingPartner::test_submit_without_mobile -v

add-sourcing-partner-no-email:
	pytest tests/test_11_add_sourcing_partner.py::TestAddSourcingPartner::test_submit_without_email -v

add-sourcing-partner-success:
	pytest tests/test_11_add_sourcing_partner.py::TestAddSourcingPartner::test_add_sourcing_partner_successful -v

# ── My Team Filter tests (2) ───────────────────────────────────────────────────

team-filter:
	pytest tests/test_13_team_filter.py -v

team-filter-date:
	pytest tests/test_13_team_filter.py::TestTeamFilter::test_filter_by_date -v

team-filter-city:
	pytest tests/test_13_team_filter.py::TestTeamFilter::test_filter_by_city -v

# ── Search Filter tests (3) ────────────────────────────────────────────────────

search-filter:
	pytest tests/test_12_search_filter.py -v

search-filter-date:
	pytest tests/test_12_search_filter.py::TestSearchFilter::test_filter_by_date -v

search-filter-city:
	pytest tests/test_12_search_filter.py::TestSearchFilter::test_filter_by_city -v

search-filter-bank:
	pytest tests/test_12_search_filter.py::TestSearchFilter::test_filter_by_bank -v

# ── Edit Columns tests (1) ─────────────────────────────────────────────────────

edit-columns:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestEditColumns -v

edit-columns-panel-opens:
	pytest tests/test_17_edit_columns_advanced_filters.py::TestEditColumns::test_edit_columns_panel_opens -v

# ── Advanced Filters tests (14) ────────────────────────────────────────────────

advanced-filters:
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
columns-and-filters:
	pytest tests/test_17_edit_columns_advanced_filters.py -v

# ── Recommended Docs tests (1) ────────────────────────────────────────────────

recommended-docs:
	pytest tests/test_08_recommended_docs.py -v

recommended-docs-success:
	pytest tests/test_08_recommended_docs.py::TestRecommendedDocs::test_get_recommended_docs_successfully -v

# ── Reassign Leads tests (1) ───────────────────────────────────────────────────

reassign-leads:
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

reports-filters:
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

# ── Add Role tests (3) ─────────────────────────────────────────────────────────

add-role:
	pytest tests/test_16_add_role.py -v

add-role-no-name:
	pytest tests/test_16_add_role.py::TestAddRole::test_add_role_without_name -v

add-role-no-description:
	pytest tests/test_16_add_role.py::TestAddRole::test_add_role_without_description -v

add-role-success:
	pytest tests/test_16_add_role.py::TestAddRole::test_add_role_successfully -v

# ── Raise a Query tests (3) ────────────────────────────────────────────────────

raise-query:
	pytest tests/test_15_raise_query.py -v

raise-query-no-issue:
	pytest tests/test_15_raise_query.py::TestRaiseQuery::test_raise_query_without_issue_type -v

raise-query-no-description:
	pytest tests/test_15_raise_query.py::TestRaiseQuery::test_raise_query_without_description -v

raise-query-success:
	pytest tests/test_15_raise_query.py::TestRaiseQuery::test_raise_query_successfully -v

# ── Payout Calculator tests (4) ────────────────────────────────────────────────

payout-calculator:
	pytest tests/test_14_payout_calculator.py -v

payout-no-loan-amount:
	pytest tests/test_14_payout_calculator.py::TestPayoutCalculator::test_payout_calculator_without_loan_amount -v

payout-no-product-type:
	pytest tests/test_14_payout_calculator.py::TestPayoutCalculator::test_payout_calculator_without_product_type -v

payout-no-fulfilment-type:
	pytest tests/test_14_payout_calculator.py::TestPayoutCalculator::test_payout_calculator_without_fulfilment_type -v

payout-success:
	pytest tests/test_14_payout_calculator.py::TestPayoutCalculator::test_payout_calculates_successfully -v

# ── Check Offers tests (2) ─────────────────────────────────────────────────────

check-offers:
	pytest tests/test_06_check_offers.py -v

check-offers-opens:
	pytest tests/test_06_check_offers.py::TestCheckOffers::test_check_offers_calculator_opens -v

check-offers-success:
	pytest tests/test_06_check_offers.py::TestCheckOffers::test_check_offers_shows_offers -v

# ── Mark as Lost tests (3) ─────────────────────────────────────────────────────

mark-as-lost:
	pytest tests/test_09_mark_as_lost.py -v

mark-as-lost-no-reason:
	pytest tests/test_09_mark_as_lost.py::TestMarkAsLost::test_mark_as_lost_without_reason -v

mark-as-lost-no-comment:
	pytest tests/test_09_mark_as_lost.py::TestMarkAsLost::test_mark_as_lost_without_comment -v

mark-as-lost-success:
	pytest tests/test_09_mark_as_lost.py::TestMarkAsLost::test_mark_lead_as_lost -v

# ── Reports ────────────────────────────────────────────────────────────────────

open-log-report:
	xdg-open log-report.html 2>/dev/null || open log-report.html 2>/dev/null || echo "Open log-report.html in your browser"

open-excel-report:
	xdg-open test-report.xlsx 2>/dev/null || open test-report.xlsx 2>/dev/null || echo "Open test-report.xlsx in your spreadsheet app"

# Allure needs a working JVM. This environment's JAVA_HOME points at a
# non-existent JDK, which makes allure's launcher abort; unset it so allure
# falls back to `java` on PATH.
ALLURE_RUN := env -u JAVA_HOME $(ALLURE)

# `make reports` — opens ALL THREE reports for the latest run:
#   1. test-summary.html   — plain-English (Cucumber-style) summary; failed tests detailed
#   2. allure-report/...   — Allure technical report (full steps, traces, logs)
#   3. test-report.xlsx    — Excel summary
reports:
	@$(ALLURE_RUN) generate allure-results -o allure-report --clean --single-file 2>/dev/null || echo "(Allure report generation skipped)"
	@xdg-open test-summary.html 2>/dev/null || open test-summary.html 2>/dev/null || echo "Open test-summary.html in your browser"
	@xdg-open allure-report/index.html 2>/dev/null || open allure-report/index.html 2>/dev/null || echo "Open allure-report/index.html in your browser"
	@xdg-open test-report.xlsx 2>/dev/null || open test-report.xlsx 2>/dev/null || echo "Open test-report.xlsx in your spreadsheet app"
	@echo "Opened: test-summary.html (plain English) + allure-report/index.html (Allure) + test-report.xlsx (Excel)"

# Allure (technical view) only: full steps, stack traces, browser logs, timeline.
allure-report:
	@$(ALLURE_RUN) generate allure-results -o allure-report --clean --single-file
	@echo "Allure report: $(CURDIR)/allure-report/index.html"
	@xdg-open allure-report/index.html 2>/dev/null || open allure-report/index.html 2>/dev/null || echo "Open allure-report/index.html in your browser"

# Live, server-backed Allure report (interactive; blocks until you stop it).
open-report:
	$(ALLURE_RUN) serve allure-results

# Generate the multi-file Allure report into allure-report/ without opening.
generate-report:
	$(ALLURE_RUN) generate allure-results -o allure-report --clean

# Open the legacy HTML log report (browser console logs) + Excel report.
open-reports:
	xdg-open log-report.html 2>/dev/null || open log-report.html 2>/dev/null || true
	xdg-open test-report.xlsx 2>/dev/null || open test-report.xlsx 2>/dev/null || true

# Run the whole suite, then open all three reports — the one-shot command.
# The leading `-` is required: a run with any failures exits non-zero, and
# without it `make` would abort before the `reports` step it exists to reach.
report:
	-$(GUARD) pytest
	@$(MAKE) reports

# Run the whole suite and email the report with NO prompt — for cron/CI or an
# unattended overnight run. The leading `-` is required: a run with failures
# exits non-zero, and the email must still go out.
report-email:
	-$(GUARD) pytest --email

# Validate the email config without running any tests or sending mail: checks
# the REPORT_EMAIL_* env vars are present and that the SMTP server accepts the
# app password. Use this after rotating REPORT_EMAIL_PASSWORD.
check-email:
	@"$(VENV)/bin/python" -c "from reporters.email_reporter import check_config; check_config()"

# Drift guard: fails (exit 1) if any tests/test_*.py file has no bare
# `pytest tests/<file>.py` make target — catches a new test file that was
# never wired into this Makefile. Uses the same Makefile parser the reports
# use (reporters/make_map.py) so this can never disagree with them.
check-targets:
	@"$(VENV)/bin/python" -c "from reporters.make_map import untargeted_test_files as u; import sys; m = u(); print('\n'.join(m)) if m else print('All test files have a make target.'); sys.exit(1 if m else 0)"

# ── My Earnings tests (5) ──────────────────────────────────────────────────────

my-earnings:
	pytest tests/test_19_my_earnings.py -v

my-earnings-loads:
	pytest tests/test_19_my_earnings.py::TestMyEarnings::test_earnings_page_loads -v

my-earnings-tabs:
	pytest "tests/test_19_my_earnings.py::TestMyEarnings::test_tab_switching" -v

my-earnings-search:
	pytest tests/test_19_my_earnings.py::TestMyEarnings::test_search_by_lead_id -v

my-earnings-reset:
	pytest tests/test_19_my_earnings.py::TestMyEarnings::test_reset_filter -v

# ── Help & Support tests (4) ───────────────────────────────────────────────────

help-support:
	pytest tests/test_20_help_support.py -v

help-support-loads:
	pytest tests/test_20_help_support.py::TestHelpSupport::test_help_page_loads -v

help-support-faqs:
	pytest tests/test_20_help_support.py::TestHelpSupport::test_faqs_tab_lists_questions -v

help-support-faq-toggle:
	pytest tests/test_20_help_support.py::TestHelpSupport::test_faq_accordion_toggles -v

help-support-tickets:
	pytest tests/test_20_help_support.py::TestHelpSupport::test_tickets_tab_loads -v

# ── Lead Detail tests (16) ─────────────────────────────────────────────────────

lead-detail:
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

# ── Team Partners tests (7) ────────────────────────────────────────────────────

team-partners:
	pytest tests/test_11b_team_partners.py -v

team-partners-add-picker-roles:
	pytest tests/test_11b_team_partners.py::TestTeamPartners::test_add_picker_offers_roles -v

team-partners-business-form-fields:
	pytest tests/test_11b_team_partners.py::TestTeamPartners::test_business_partner_form_fields -v

team-partners-business-submit-enabled:
	pytest tests/test_11b_team_partners.py::TestTeamPartners::test_business_partner_submit_enabled_when_filled -v

team-partners-business-pan-disables-submit:
	pytest tests/test_11b_team_partners.py::TestTeamPartners::test_business_partner_pan_disables_submit -v

team-partners-channel-tab-loads:
	pytest tests/test_11b_team_partners.py::TestTeamPartners::test_channel_partner_tab_loads -v

team-partners-channel-add-sourcing-partner:
	pytest tests/test_11b_team_partners.py::TestTeamPartners::test_channel_partner_add_is_sourcing_partner -v

team-partners-search-special-chars:
	pytest tests/test_11b_team_partners.py::TestTeamPartners::test_search_handles_special_characters_safely -v

# ── Profile tests (6) ──────────────────────────────────────────────────────────

profile:
	pytest tests/test_20b_profile.py -v

profile-page-loads:
	pytest tests/test_20b_profile.py::TestProfile::test_profile_page_loads -v

profile-basic-details-fields:
	pytest tests/test_20b_profile.py::TestProfile::test_basic_details_fields -v

profile-tabs-present:
	pytest tests/test_20b_profile.py::TestProfile::test_profile_tabs_present -v

profile-kyc-tab-opens:
	pytest tests/test_20b_profile.py::TestProfile::test_kyc_documents_tab_opens -v

profile-pincode-bug:
	pytest tests/test_20b_profile.py::TestProfile::test_pincode_rejects_non_numeric_bug -v

profile-spoc-xss-safe:
	pytest tests/test_20b_profile.py::TestProfile::test_spoc_name_xss_is_safe -v

# ── Check CIBIL Score tests (11) ───────────────────────────────────────────────

cibil:
	pytest tests/test_21_cibil.py -v

cibil-page-loads:
	pytest tests/test_21_cibil.py::TestCibil::test_cibil_page_loads -v

cibil-no-pan:
	pytest tests/test_21_cibil.py::TestCibil::test_fetch_without_pan_shows_error -v

cibil-invalid-pan:
	pytest tests/test_21_cibil.py::TestCibil::test_fetch_invalid_pan_shows_error -v

cibil-valid-pan-success:
	pytest tests/test_21_cibil.py::TestCibil::test_fetch_valid_pan_success -v

cibil-continue-no-details:
	pytest tests/test_21_cibil.py::TestCibil::test_continue_without_details_shows_pan_error -v

cibil-continue-no-first-name:
	pytest tests/test_21_cibil.py::TestCibil::test_continue_without_first_name -v

cibil-continue-invalid-email:
	pytest tests/test_21_cibil.py::TestCibil::test_continue_with_invalid_email -v

cibil-continue-invalid-mobile:
	pytest tests/test_21_cibil.py::TestCibil::test_continue_with_invalid_mobile -v

cibil-continue-no-dob:
	pytest tests/test_21_cibil.py::TestCibil::test_continue_without_dob -v

cibil-dob-picker:
	pytest tests/test_21_cibil.py::TestCibil::test_dob_picker_sets_date -v

cibil-full-form-success:
	pytest tests/test_21_cibil.py::TestCibil::test_full_form_advances_to_fulfilment_step -v

# ── ABB Calculator tests (5) ───────────────────────────────────────────────────

abb-calculator:
	pytest tests/test_22_abb_calculator.py -v

abb-calculator-opens:
	pytest tests/test_22_abb_calculator.py::TestAbbCalculator::test_abb_tool_opens -v

abb-calculator-intro-prompt:
	pytest tests/test_22_abb_calculator.py::TestAbbCalculator::test_abb_shows_intro_prompt -v

abb-calculator-statement-instructions:
	pytest tests/test_22_abb_calculator.py::TestAbbCalculator::test_abb_shows_statement_instructions -v

abb-calculator-pdf-only:
	pytest tests/test_22_abb_calculator.py::TestAbbCalculator::test_abb_file_input_accepts_pdf_only -v

abb-calculator-accepts-pdf:
	pytest tests/test_22_abb_calculator.py::TestAbbCalculator::test_abb_accepts_pdf_file -v

# ── APF Search Engine tests (5) ────────────────────────────────────────────────

apf-search:
	pytest tests/test_23_apf_search.py -v

apf-search-page-loads:
	pytest tests/test_23_apf_search.py::TestApfSearch::test_apf_page_loads -v

apf-search-table-headers:
	pytest tests/test_23_apf_search.py::TestApfSearch::test_apf_results_table_headers -v

apf-search-city-dropdown:
	pytest tests/test_23_apf_search.py::TestApfSearch::test_apf_city_dropdown_opens -v

apf-search-select-city:
	pytest tests/test_23_apf_search.py::TestApfSearch::test_apf_select_city -v

apf-search-no-match-empty-state:
	pytest tests/test_23_apf_search.py::TestApfSearch::test_apf_search_no_match_shows_empty_state -v

# ── Website Settings tests (10) ────────────────────────────────────────────────

website-settings:
	pytest tests/test_24_website_settings.py -v

website-settings-page-loads:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_website_settings_page_loads -v

website-settings-save-buttons:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_all_sections_have_save_buttons -v

website-settings-save-header:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_save_header_section -v

website-settings-save-hero:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_save_hero_section -v

website-settings-save-testimonials:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_save_testimonials_section -v

website-settings-save-calculator:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_save_calculator_section -v

website-settings-save-faq:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_save_faq_section -v

website-settings-edit-hero-heading:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_edit_hero_heading_and_save -v

website-settings-add-feature-row:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_add_feature_adds_row -v

website-settings-add-faq-block:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_add_faq_block -v

# ── Logout tests (1) ───────────────────────────────────────────────────────────

logout:
	pytest tests/test_25_logout.py -v

logout-redirects:
	pytest tests/test_25_logout.py::TestLogout::test_logout_redirects_to_login -v

# ── Utilities ──────────────────────────────────────────────────────────────────

# Delete saved login session — next run will prompt for a fresh OTP
reset-session:
	rm -f auth_state.json

# Remove generated reports and pytest cache
clean:
	rm -f log-report.html test-report.xlsx test-summary.html allure-report.html heal-report.json
	rm -rf allure-results allure-report .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ── Help ───────────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "Automation Saathi — available commands"
	@echo "======================================="
	@echo ""
	@echo "Setup"
	@echo "  make install                       Install all dependencies and Playwright browser"
	@echo ""
	@echo "Run tests"
	@echo "  make all                           Run all 267 tests"
	@echo "  make e2e                           Run only the happy-path tests (e2e mark)"
	@echo "  make headless                      Run all tests without a visible browser window"
	@echo ""
	@echo "Run happy path up to a stage (cumulative — only those cases run)"
	@echo "  make stage-login                   Login -> create lead -> move to login"
	@echo "  make stage-sanction                ... up to and including move to sanction"
	@echo "  make stage-disburse                ... full lifecycle, ending at disburse"
	@echo ""
	@echo "Create Lead"
	@echo "  make create-lead                   Create Lead validation/success tests (9)"
	@echo "  make lead-entry-mode               Add Manually / Bulk Upload / Purchase Type tests (6)"
	@echo ""
	@echo "Pipeline stages"
	@echo "  make move-to-login                 Move to Login tests (11)"
	@echo "  make move-to-sanction              Move to Sanction tests (9)"
	@echo "  make move-to-disburse              Move to Disburse tests (10)"
	@echo "  make mark-as-lost                  Mark as Lost tests (3)"
	@echo ""
	@echo "Follow-ups (across all pipeline stages)"
	@echo "  make followup                      All followup tests (login + sanction + disburse)"
	@echo "  make login-followup                Followup tests within Move to Login"
	@echo "  make sanction-followup             Followup tests within Move to Sanction"
	@echo "  make disburse-followup             Followup tests within Move to Disburse"
	@echo ""
	@echo "Leads page"
	@echo "  make edit-columns                  Edit Columns panel test (1)"
	@echo "  make advanced-filters              All Advanced Filters dropdown tests (14)"
	@echo "  make columns-and-filters           Edit Columns + Advanced Filters together (15)"
	@echo "  make search-filter                 Lead search filter tests (3)"
	@echo "  make team-filter                   My Team filter tests (2)"
	@echo ""
	@echo "Other features"
	@echo "  make login                         Login tests (3)"
	@echo "  make recommended-docs              Recommended Docs test (1)"
	@echo "  make reassign-leads                Reassign Leads tests (4)"
	@echo "  make reports-filters               Reports Advanced Filters dropdown tests (7)"
	@echo "  make add-teammate                  Add Teammate tests (4)"
	@echo "  make add-sourcing-partner          Add Sourcing Partner tests (4)"
	@echo "  make check-offers                  Check Offers tests (2)"
	@echo "  make payout-calculator             Payout Calculator tests (4)"
	@echo "  make add-role                      Add Role tests (3)"
	@echo "  make raise-query                   Raise a Query tests (3)"
	@echo "  make my-earnings                   My Earnings tab + search tests (5)"
	@echo "  make help-support                  Help & Support FAQs/Tickets tests (4)"
	@echo "  make lead-detail                   Lead Detail tests (16)"
	@echo "  make team-partners                 My Team - Partners tests (7)"
	@echo "  make profile                       Profile tests (6)"
	@echo "  make cibil                         Check CIBIL Score tests (11)"
	@echo "  make abb-calculator                ABB Calculator tests (5)"
	@echo "  make apf-search                    APF Search Engine tests (5)"
	@echo "  make website-settings              Website Settings tests (10)"
	@echo "  make logout                        Logout test (1)"
	@echo ""
	@echo "Reports  (results captured automatically after every run)"
	@echo "  make report                        Run the whole suite, then open all three reports"
	@echo "  make reports                       Open the plain-English summary (grouped by feature + make command)"
	@echo "  make allure-report                 Open the Allure report (technical: full steps + stack traces)"
	@echo "  make open-report                   Open the Allure report as a live server (interactive)"
	@echo "  make open-reports                  Open the legacy HTML log report + Excel report"
	@echo "  make open-excel-report             Open the Excel report only"
	@echo "  make report-email                  Run the whole suite and email the report, no prompt"
	@echo "  make check-email                   Validate REPORT_EMAIL_* config without sending mail"
	@echo "  make check-targets                 Fail if any test file has no make target (drift guard)"
	@echo ""
	@echo "Utilities"
	@echo "  make reset-session                 Force a fresh OTP login on next run"
	@echo "  make clean                         Remove all generated reports and cache files"
	@echo ""
