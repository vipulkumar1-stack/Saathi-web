# Calculators & tools: tests/test_14_payout_calculator.py,
# test_06_check_offers.py, test_21_cibil.py, test_22_abb_calculator.py,
# test_23_apf_search.py, test_19_my_earnings.py, test_20_help_support.py.

.PHONY: cibil abb-calculator apf-search

##@ Calculators & tools

# ── Payout Calculator tests (4) ────────────────────────────────────────────────

payout-calculator: ## Payout Calculator tests
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

check-offers: ## Check Offers tests
	pytest tests/test_06_check_offers.py -v

check-offers-opens:
	pytest tests/test_06_check_offers.py::TestCheckOffers::test_check_offers_calculator_opens -v

check-offers-success:
	pytest tests/test_06_check_offers.py::TestCheckOffers::test_check_offers_shows_offers -v

# ── Check CIBIL Score tests (11) ───────────────────────────────────────────────

cibil: ## Check CIBIL Score tests
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

abb-calculator: ## ABB Calculator tests
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

apf-search: ## APF Search Engine tests
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

# ── My Earnings tests (5) ──────────────────────────────────────────────────────

my-earnings: ## My Earnings tab + search tests
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

help-support: ## Help & Support FAQs/Tickets tests
	pytest tests/test_20_help_support.py -v

help-support-loads:
	pytest tests/test_20_help_support.py::TestHelpSupport::test_help_page_loads -v

help-support-faqs:
	pytest tests/test_20_help_support.py::TestHelpSupport::test_faqs_tab_lists_questions -v

help-support-faq-toggle:
	pytest tests/test_20_help_support.py::TestHelpSupport::test_faq_accordion_toggles -v

help-support-tickets:
	pytest tests/test_20_help_support.py::TestHelpSupport::test_tickets_tab_loads -v
