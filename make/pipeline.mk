# Lead lifecycle: tests/test_01_login.py, test_02_create_lead.py,
# test_02b_lead_entry_mode.py, test_03_move_to_login.py,
# test_04_move_to_sanction.py, test_05_move_to_disburse.py,
# test_09_mark_as_lost.py.

.PHONY: followup

##@ Lead pipeline (login → create lead → move to login/sanction/disburse, incl. follow-ups)

# ── Login tests (4) ────────────────────────────────────────────────────────────

login: ## Login tests
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

create-lead: ## Create Lead validation/success tests
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

lead-entry-mode: ## Add Manually / Bulk Upload / Purchase Type tests
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

move-to-login: ## Move to Login tests
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

login-followup: ## Followup tests within Move to Login
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

move-to-sanction: ## Move to Sanction tests
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

sanction-followup: ## Followup tests within Move to Sanction
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

move-to-disburse: ## Move to Disburse tests
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

disburse-followup: ## Followup tests within Move to Disburse
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
followup: ## All followup tests (login + sanction + disburse)
	pytest tests/test_03_move_to_login.py tests/test_04_move_to_sanction.py tests/test_05_move_to_disburse.py -k "followup" -v

# ── Mark as Lost tests (3) ─────────────────────────────────────────────────────

mark-as-lost: ## Mark as Lost tests
	pytest tests/test_09_mark_as_lost.py -v

mark-as-lost-no-reason:
	pytest tests/test_09_mark_as_lost.py::TestMarkAsLost::test_mark_as_lost_without_reason -v

mark-as-lost-no-comment:
	pytest tests/test_09_mark_as_lost.py::TestMarkAsLost::test_mark_as_lost_without_comment -v

mark-as-lost-success:
	pytest tests/test_09_mark_as_lost.py::TestMarkAsLost::test_mark_lead_as_lost -v
