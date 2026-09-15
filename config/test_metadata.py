"""Curated step-by-step descriptions for each test case, keyed by ClassName::test_method_name.

Any test NOT listed in _EXPLICIT_STEPS is auto-populated at import time from
its docstring, so new tests appear in reports without manual maintenance here."""

import ast
from pathlib import Path


def _scan_docstrings() -> dict[str, str]:
    """Walk tests/ and return {ClassName::test_name: docstring} for tests
    not already covered by _EXPLICIT_STEPS."""
    result: dict[str, str] = {}
    tests_dir = Path(__file__).parent.parent / "tests"
    for path in sorted(tests_dir.glob("test_*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                    key = f"{node.name}::{item.name}"
                    doc = ast.get_docstring(item)
                    if doc:
                        result[key] = doc.strip()
    return result


_EXPLICIT_STEPS: dict[str, str] = {

    # ── Login ──────────────────────────────────────────────────────────────────
    "TestLogin::test_login_rejects_wrong_otp_then_succeeds": (
        "1. Open the login page URL\n"
        "2. Enter the registered mobile number and submit to send an OTP\n"
        "3. Enter a wrong OTP (000000) and click Verify\n"
        "4. Verify the Verify button is still visible (login was rejected)\n"
        "5. Verify the URL is still NOT the leads dashboard\n"
        "6. Enter the correct OTP in the same session and click Verify\n"
        "7. Verify the URL is now the leads dashboard\n"
        "8. Save the browser storage state to auth_state.json for later tests"
    ),

    "TestLogin::test_login_page_loads": (
        "1. Open the login page URL\n"
        "2. Verify mobile number input is visible\n"
        "3. Verify Submit button is visible"
    ),
    "TestLogin::test_submit_without_mobile": (
        "1. Open the login page URL\n"
        "2. Click Submit without entering a mobile number\n"
        "3. Verify OTP input does NOT appear"
    ),
    "TestLogin::test_login_rejects_wrong_otp_then_succeeds": (
        "1. Open the login page URL, enter a valid mobile number and submit\n"
        "2. Enter a wrong OTP and verify — confirm it's rejected and the page\n"
        "   stays on the login screen (Verify button still visible, URL unchanged)\n"
        "3. Enter the correct OTP (same session) and verify\n"
        "4. Verify redirect to /saathi-leads and save the session to auth_state.json"
    ),

    # ── Create Lead — Self-fulfilled ───────────────────────────────────────────
    "TestCreateLead::test_submit_without_loan_amount": (
        "1. From the home page click Create Lead to open the Add New Lead form\n"
        "2. Fill every field with generated data EXCEPT Loan Amount\n"
        "3. Leave Loan Amount empty and click Submit\n"
        "4. Verify the success popup does NOT appear — submission was blocked"
    ),

    "TestCreateLead::test_create_lead_form_opens": (
        "1. Navigate to home page\n"
        "2. Click 'Create Lead' button\n"
        "3. Verify Create Lead popup opens with First Name input visible"
    ),
    "TestCreateLead::test_submit_without_first_name": (
        "1. Open the Create Lead form\n"
        "2. Fill all fields except First Name (leave empty)\n"
        "3. Click Submit\n"
        "4. Verify First Name validation error is visible"
    ),
    "TestCreateLead::test_submit_without_last_name": (
        "1. Open the Create Lead form\n"
        "2. Fill all fields except Last Name (leave empty)\n"
        "3. Click Submit\n"
        "4. Verify Last Name validation error is visible"
    ),
    "TestCreateLead::test_submit_without_mobile": (
        "1. Open the Create Lead form\n"
        "2. Fill all fields except Mobile (leave empty)\n"
        "3. Click Submit\n"
        "4. Verify Mobile validation error is visible"
    ),
    "TestCreateLead::test_submit_without_loan_type": (
        "1. Open the Create Lead form\n"
        "2. Fill all fields except Loan Type (do not select)\n"
        "3. Click Submit\n"
        "4. Verify Loan Type validation error is visible"
    ),
    "TestCreateLead::test_submit_without_employment_type": (
        "1. Open the Create Lead form\n"
        "2. Fill all fields except Employment Type (do not select)\n"
        "3. Click Submit\n"
        "4. Verify Employment Type validation error is visible"
    ),
    "TestCreateLead::test_submit_without_city": (
        "1. Open the Create Lead form\n"
        "2. Fill all fields — leave City unselected (the only location field;\n"
        "   State was removed from the modal in the 2026-09 redesign)\n"
        "3. Click Submit\n"
        "4. Verify City validation error is visible"
    ),
    "TestCreateLead::test_create_lead_successful": (
        "1. Open the Create Lead form\n"
        "2. Fill all required fields with valid random data\n"
        "3. Click Submit\n"
        "4. Verify success popup title appears\n"
        "5. Click 'Go to My Leads'\n"
        "6. Capture the new lead ID for downstream tests"
    ),
    "TestCreateLead::test_duplicate_mobile_shows_popup": (
        "1. Open the Create Lead form\n"
        "2. Fill all fields using a mobile number that already exists\n"
        "3. Click Submit\n"
        "4. Verify duplicate mobile warning popup appears"
    ),

    # ── Lead Entry Mode (Add Manually / Bulk Upload / Purchase Type) ───────────
    # Not explicitly listed — TestLeadEntryMode's docstrings are picked up
    # automatically by _scan_docstrings() below, same as any other new test.

    # ── Move to Login ──────────────────────────────────────────────────────────
    "TestMoveToLogin::test_lead_present_in_pre_login_tab": (
        "1. On the leads dashboard click the Pre-Login tab and wait for the grid\n"
        "2. Search for the lead by its ID and wait for the filtered row to render\n"
        "3. Verify a table cell matching the lead ID is visible in the Pre-Login tab"
    ),

    "TestMoveToLogin::test_move_to_login_without_loan_amount": (
        "1. Navigate to Pre-Login tab and search for the lead\n"
        "2. Open the lead detail page\n"
        "3. Click 'Move to Login'\n"
        "4. Fill all fields except Loan Amount (leave empty)\n"
        "5. Click Submit\n"
        "6. Verify Loan Amount error toast is visible"
    ),
    "TestMoveToLogin::test_move_to_login_without_bank": (
        "1. Navigate to Pre-Login tab and open lead\n"
        "2. Click 'Move to Login'\n"
        "3. Fill all fields except Bank (do not select)\n"
        "4. Click Submit\n"
        "5. Verify Bank error toast is visible"
    ),
    "TestMoveToLogin::test_move_to_login_without_login_id": (
        "1. Navigate to Pre-Login tab and open lead\n"
        "2. Click 'Move to Login'\n"
        "3. Fill all fields except Login ID (leave empty)\n"
        "4. Click Submit\n"
        "5. Verify Login ID error toast is visible"
    ),
    "TestMoveToLogin::test_move_to_login_without_date": (
        "1. Navigate to Pre-Login tab and open lead\n"
        "2. Click 'Move to Login'\n"
        "3. Fill all fields but skip Login Date selection\n"
        "4. Click Submit\n"
        "5. Verify date error toast is visible"
    ),
    "TestMoveToLogin::test_move_to_login_without_branch": (
        "1. Navigate to Pre-Login tab and open lead\n"
        "2. Click 'Move to Login'\n"
        "3. Fill all fields except Branch (do not select)\n"
        "4. Click Submit\n"
        "5. Verify Branch error toast is visible"
    ),
    "TestMoveToLogin::test_move_to_login_without_banker": (
        "1. Navigate to Pre-Login tab and open lead\n"
        "2. Click 'Move to Login'\n"
        "3. Fill all fields except Banker (do not select)\n"
        "4. Click Submit\n"
        "5. Verify Banker error toast is visible"
    ),
    "TestMoveToLogin::test_followup_without_date": (
        "1. Navigate to Pre-Login tab and open lead\n"
        "2. Click 'Schedule Follow-up'\n"
        "3. Fill all fields except Date (do not select)\n"
        "4. Click Submit\n"
        "5. Verify date error message is visible"
    ),
    "TestMoveToLogin::test_followup_without_time": (
        "1. Navigate to Pre-Login tab and open lead\n"
        "2. Click 'Schedule Follow-up'\n"
        "3. Fill all fields except Time (leave empty)\n"
        "4. Click Submit\n"
        "5. Verify time error message is visible"
    ),
    "TestMoveToLogin::test_followup_without_comment": (
        "1. Navigate to Pre-Login tab and open lead\n"
        "2. Click 'Schedule Follow-up'\n"
        "3. Fill all fields except Comment (leave empty)\n"
        "4. Click Submit\n"
        "5. Verify comment error message is visible"
    ),
    "TestMoveToLogin::test_followup_scheduled_successfully": (
        "1. Navigate to Pre-Login tab and open lead\n"
        "2. Click 'Schedule Follow-up'\n"
        "3. Fill Date, Time, and Comment with valid data\n"
        "4. Click Submit\n"
        "5. Verify new follow-up entry appears in the Followups section"
    ),
    "TestMoveToLogin::test_move_lead_to_login": (
        "1. Navigate to Pre-Login tab and search for the lead\n"
        "2. Open the lead detail page\n"
        "3. Click 'Move to Login'\n"
        "4. Fill all fields with valid random data\n"
        "5. Click Submit\n"
        "6. Verify 'Email sent successfully' toast appears"
    ),

    "TestMoveToLogin::test_back_forward_discards_entered_data_bug": (
        "1. Navigate to Pre-Login tab and search for a freshly seeded lead\n"
        "2. Open the lead detail page and click 'Move to Login'\n"
        "3. Type a Loan Amount into the form\n"
        "4. Navigate back, then forward, on the form's own page\n"
        "5. Verify the typed Loan Amount is still present"
    ),

    # ── Move to Sanction ───────────────────────────────────────────────────────
    "TestMoveToSanction::test_lead_present_in_logged_in_tab": (
        "1. On the leads dashboard click the Logged In tab and wait for the grid\n"
        "2. Search for the lead by its ID and wait for the filtered row to render\n"
        "3. Verify a table cell matching the lead ID is visible in the Logged In tab"
    ),

    "TestMoveToSanction::test_move_to_sanction_without_loan_amount": (
        "1. Navigate to Logged-In tab and search for the lead\n"
        "2. Open the lead detail page\n"
        "3. Click 'Move to Sanction'\n"
        "4. Fill all fields except Loan Amount (leave empty)\n"
        "5. Click Submit\n"
        "6. Verify success toast is NOT visible"
    ),
    "TestMoveToSanction::test_move_to_sanction_without_sanction_id": (
        "1. Navigate to Logged-In tab and open lead\n"
        "2. Click 'Move to Sanction'\n"
        "3. Fill all fields except Sanction ID (leave empty)\n"
        "4. Click Submit\n"
        "5. Verify success toast is NOT visible"
    ),
    "TestMoveToSanction::test_move_to_sanction_without_date": (
        "1. Navigate to Logged-In tab and open lead\n"
        "2. Click 'Move to Sanction'\n"
        "3. Fill all fields but skip Sanction Date selection\n"
        "4. Click Submit\n"
        "5. Verify success toast is NOT visible"
    ),
    "TestMoveToSanction::test_sanction_dates_before_login_are_disabled": (
        "1. Navigate to Logged-In tab and open lead\n"
        "2. Click 'Move to Sanction'\n"
        "3. Open the Sanction Date calendar picker\n"
        "4. Check that yesterday's date is disabled\n"
        "5. Verify the past date cannot be selected"
    ),
    "TestMoveToSanction::test_followup_without_date": (
        "1. Navigate to Logged-In tab and open lead\n"
        "2. Click 'Schedule Follow-up'\n"
        "3. Fill all fields except Date (do not select)\n"
        "4. Click Submit\n"
        "5. Verify date error message is visible"
    ),
    "TestMoveToSanction::test_followup_without_time": (
        "1. Navigate to Logged-In tab and open lead\n"
        "2. Click 'Schedule Follow-up'\n"
        "3. Fill all fields except Time (leave empty)\n"
        "4. Click Submit\n"
        "5. Verify time error message is visible"
    ),
    "TestMoveToSanction::test_followup_without_comment": (
        "1. Navigate to Logged-In tab and open lead\n"
        "2. Click 'Schedule Follow-up'\n"
        "3. Fill all fields except Comment (leave empty)\n"
        "4. Click Submit\n"
        "5. Verify comment error message is visible"
    ),
    "TestMoveToSanction::test_followup_scheduled_successfully": (
        "1. Navigate to Logged-In tab and open lead\n"
        "2. Click 'Schedule Follow-up'\n"
        "3. Fill Date, Time, and Comment with valid data\n"
        "4. Click Submit\n"
        "5. Verify new follow-up entry appears in the Followups section"
    ),
    "TestMoveToSanction::test_move_lead_to_sanction": (
        "1. Navigate to Logged-In tab and search for the lead\n"
        "2. Open the lead detail page\n"
        "3. Click 'Move to Sanction'\n"
        "4. Fill Loan Amount, Sanction ID, and Sanction Date with valid data\n"
        "5. Click Submit\n"
        "6. Verify 'Email sent successfully' toast appears"
    ),

    # ── Move to Disburse ───────────────────────────────────────────────────────
    "TestMoveToDisburse::test_lead_present_in_sanctioned_tab": (
        "1. On the leads dashboard click the Sanctioned tab and wait for the grid\n"
        "2. Search for the lead by its ID and wait for the filtered row to render\n"
        "3. Verify a table cell matching the lead ID is visible in the Sanctioned tab"
    ),

    "TestMoveToDisburse::test_move_to_disburse_without_loan_amount": (
        "1. Navigate to Sanctioned tab and search for the lead\n"
        "2. Open the lead detail page\n"
        "3. Click 'Move to Disburse'\n"
        "4. Fill all fields except Loan Amount (leave empty)\n"
        "5. Click Submit\n"
        "6. Verify amount/date error toast is visible"
    ),
    "TestMoveToDisburse::test_move_to_disburse_without_disbursed_id": (
        "1. Navigate to Sanctioned tab and open lead\n"
        "2. Click 'Move to Disburse'\n"
        "3. Fill all fields except Disbursed ID (leave empty)\n"
        "4. Click Submit\n"
        "5. Verify Disbursed ID error toast is visible"
    ),
    "TestMoveToDisburse::test_move_to_disburse_without_disbursal_date": (
        "1. Navigate to Sanctioned tab and open lead\n"
        "2. Click 'Move to Disburse'\n"
        "3. Fill all fields but skip Disbursal Date selection\n"
        "4. Click Submit\n"
        "5. Verify amount/date error toast is visible"
    ),
    "TestMoveToDisburse::test_move_to_disburse_amount_exceeds_sanction": (
        "1. Navigate to Sanctioned tab and open lead\n"
        "2. Click 'Move to Disburse'\n"
        "3. Enter a Loan Amount greater than the sanctioned amount\n"
        "4. Fill remaining fields with valid data\n"
        "5. Click Submit\n"
        "6. Verify 'cannot exceed' error toast is visible"
    ),
    "TestMoveToDisburse::test_disbursal_dates_before_sanction_are_disabled": (
        "1. Navigate to Sanctioned tab and open lead\n"
        "2. Click 'Move to Disburse'\n"
        "3. Open the Disbursal Date calendar picker\n"
        "4. Check that yesterday's date is disabled\n"
        "5. Verify the past date cannot be selected"
    ),
    "TestMoveToDisburse::test_followup_without_date": (
        "1. Navigate to Sanctioned tab and open lead\n"
        "2. Click 'Schedule Follow-up'\n"
        "3. Fill all fields except Date (do not select)\n"
        "4. Click Submit\n"
        "5. Verify date error message is visible"
    ),
    "TestMoveToDisburse::test_followup_without_time": (
        "1. Navigate to Sanctioned tab and open lead\n"
        "2. Click 'Schedule Follow-up'\n"
        "3. Fill all fields except Time (leave empty)\n"
        "4. Click Submit\n"
        "5. Verify time error message is visible"
    ),
    "TestMoveToDisburse::test_followup_without_comment": (
        "1. Navigate to Sanctioned tab and open lead\n"
        "2. Click 'Schedule Follow-up'\n"
        "3. Fill all fields except Comment (leave empty)\n"
        "4. Click Submit\n"
        "5. Verify comment error message is visible"
    ),
    "TestMoveToDisburse::test_followup_scheduled_successfully": (
        "1. Navigate to Sanctioned tab and open lead\n"
        "2. Click 'Schedule Follow-up'\n"
        "3. Fill Date, Time, and Comment with valid data\n"
        "4. Click Submit\n"
        "5. Verify new follow-up entry appears in the Followups section"
    ),
    "TestMoveToDisburse::test_move_lead_to_disburse": (
        "1. Navigate to Sanctioned tab and search for the lead\n"
        "2. Open the lead detail page\n"
        "3. Click 'Move to Disburse'\n"
        "4. Fill Loan Amount (≤ sanctioned), Disbursed ID, and Disbursal Date\n"
        "5. Click Submit\n"
        "6. Verify 'Congratulations for your Disbursement!' toast appears"
    ),

    # ── Mark as Lost ──────────────────────────────────────────────────────────
    "TestMarkAsLost::test_mark_as_lost_without_reason": (
        "1. Search for the lead and open the detail page\n"
        "2. Click 'Mark as Lost'\n"
        "3. Click Save without selecting any reason\n"
        "4. Verify 'Please select reason' error toast is visible"
    ),
    "TestMarkAsLost::test_mark_as_lost_without_comment": (
        "1. Search for the lead and open the detail page\n"
        "2. Click 'Mark as Lost'\n"
        "3. Select a lost reason but leave Comment empty\n"
        "4. Click Save\n"
        "5. Verify 'Please enter comment' error toast is visible"
    ),
    "TestMarkAsLost::test_mark_lead_as_lost": (
        "1. Search for the lead and open the detail page\n"
        "2. Click 'Mark as Lost'\n"
        "3. Select a lost reason\n"
        "4. Enter a comment\n"
        "5. Click Save\n"
        "6. Verify 'Lead updated successfully.' toast appears"
    ),

    # ── Add Teammate ──────────────────────────────────────────────────────────
    "TestAddTeammate::test_submit_without_full_name": (
        "1. Navigate to My Team\n"
        "2. Open the Add Teammate form\n"
        "3. Fill Mobile and select Designation, leave Full Name empty\n"
        "4. Click Submit\n"
        "5. Verify success message is NOT visible"
    ),
    "TestAddTeammate::test_submit_without_mobile": (
        "1. Navigate to My Team\n"
        "2. Open the Add Teammate form\n"
        "3. Fill Full Name and select Designation, leave Mobile empty\n"
        "4. Click Submit\n"
        "5. Verify success message is NOT visible"
    ),
    "TestAddTeammate::test_submit_without_designation": (
        "1. Navigate to My Team\n"
        "2. Open the Add Teammate form\n"
        "3. Fill Full Name and Mobile, skip Designation selection\n"
        "4. Click Submit\n"
        "5. Verify success message is NOT visible"
    ),
    "TestAddTeammate::test_add_teammate_successful": (
        "1. Navigate to My Team\n"
        "2. Open the Add Teammate form\n"
        "3. Fill Full Name and Mobile with valid random data\n"
        "4. Select a Designation\n"
        "5. Click Submit\n"
        "6. Verify 'You have Successfully Added Team Member.' modal appears"
    ),

    # ── Add Sourcing Partner ───────────────────────────────────────────────────
    "TestAddSourcingPartner::test_submit_without_full_name": (
        "1. Navigate to My Team\n"
        "2. Open the Add Sourcing Partner form\n"
        "3. Fill Mobile and Email, leave Full Name empty\n"
        "4. Click Submit\n"
        "5. Verify success message is NOT visible"
    ),
    "TestAddSourcingPartner::test_submit_without_mobile": (
        "1. Navigate to My Team\n"
        "2. Open the Add Sourcing Partner form\n"
        "3. Fill Full Name and Email, leave Mobile empty\n"
        "4. Click Submit\n"
        "5. Verify success message is NOT visible"
    ),
    "TestAddSourcingPartner::test_submit_without_email": (
        "1. Navigate to My Team\n"
        "2. Open the Add Sourcing Partner form\n"
        "3. Fill Full Name and Mobile, leave Email empty\n"
        "4. Click Submit\n"
        "5. Verify success message is NOT visible"
    ),
    "TestAddSourcingPartner::test_add_sourcing_partner_successful": (
        "1. Navigate to My Team\n"
        "2. Open the Add Sourcing Partner form\n"
        "3. Fill Full Name, Mobile, and Email with valid random data\n"
        "4. Click Submit\n"
        "5. Verify 'You have successfully added Sub Partner.' modal appears"
    ),

    # ── Search Filters ─────────────────────────────────────────────────────────
    "TestSearchFilter::test_filter_by_date": (
        "1. Navigate to the leads list\n"
        "2. Open the search filter panel\n"
        "3. Select 'Yesterday' from the Created Date dropdown\n"
        "4. Apply the filter\n"
        "5. Verify search box remains visible (filtered results loaded)"
    ),
    "TestSearchFilter::test_filter_by_city": (
        "1. Navigate to the leads list\n"
        "2. Open the search filter panel\n"
        "3. Type and select a city in the City filter\n"
        "4. Apply the filter\n"
        "5. Verify search box remains visible (filtered results loaded)"
    ),
    "TestSearchFilter::test_filter_by_bank": (
        "1. Navigate to the leads list\n"
        "2. Open the search filter panel\n"
        "3. Search for and select ICICI in the Bank filter\n"
        "4. Apply the filter\n"
        "5. Verify search box remains visible (filtered results loaded)"
    ),

    # ── My Team Filters ────────────────────────────────────────────────────────
    "TestTeamFilter::test_filter_by_date": (
        "1. Navigate to My Team\n"
        "2. Open the filter panel\n"
        "3. Select a start and end date in the date range picker\n"
        "4. Apply the filter\n"
        "5. Verify Add Teammate button remains visible (list loaded)"
    ),
    "TestTeamFilter::test_filter_by_city": (
        "1. Navigate to My Team\n"
        "2. Open the filter panel\n"
        "3. Search for and select a city in the City filter\n"
        "4. Apply the filter\n"
        "5. Verify Add Teammate button remains visible (list loaded)"
    ),

    # ── Check Offers ───────────────────────────────────────────────────────────
    "TestCheckOffers::test_check_offers_calculator_opens": (
        "1. On the leads dashboard click the Pre-Login tab\n"
        "2. Search for the lead and open it in a new tab\n"
        "3. Wait for the lead detail page to settle\n"
        "4. Click the 'Checkout Loan Offers!' CTA\n"
        "5. Verify the Loan Offer Calculator's Get Started button is visible"
    ),
    "TestCheckOffers::test_check_offers_shows_offers": (
        "1. Open the lead in a new tab and click 'Checkout Loan Offers!'\n"
        "2. Select loan type, loan product and employment type\n"
        "3. Click Get Started, fill the loan amount and click Continue\n"
        "4. Fill business details (company type, age of business, credit score,\n"
        "   age range, gender) and click Continue\n"
        "5. Enter the income manually and click Continue\n"
        "6. Fill expected property value and state, then click Check Offers\n"
        "7. Verify the offers results screen is visible"
    ),

    "TestCheckOffers::test_check_offers_without_employment_type": (
        "1. Navigate to My Tools → Check Offers\n"
        "2. Select a Loan Type but do NOT select Employment Type\n"
        "3. Click 'Get Started'\n"
        "4. Verify Loan Amount input does NOT appear (flow blocked)"
    ),
    "TestCheckOffers::test_check_offers_without_loan_amount": (
        "1. Navigate to My Tools → Check Offers\n"
        "2. Select Employment Type and Loan Type, click 'Get Started'\n"
        "3. Select Tenure but leave Loan Amount empty\n"
        "4. Click 'Continue'\n"
        "5. Verify age selection step does NOT appear (flow blocked)"
    ),
    "TestCheckOffers::test_check_offers_creates_lead_successfully": (
        "1. Navigate to My Tools → Check Offers\n"
        "2. Select Employment Type, Loan Type, and Loan Amount\n"
        "3. Select Tenure and proceed through all steps\n"
        "4. Complete remaining steps with valid data and submit\n"
        "5. Verify 'Your Lead Successfully Uploaded' popup appears"
    ),

    # ── Payout Calculator ──────────────────────────────────────────────────────
    "TestPayoutCalculator::test_payout_calculator_without_loan_amount": (
        "1. Navigate to My Tools → Payout Calculator\n"
        "2. Select Product Type and Fulfilment Type\n"
        "3. Leave Loan Amount empty\n"
        "4. Click 'Calculate now'\n"
        "5. Verify Payout Details section does NOT appear"
    ),
    "TestPayoutCalculator::test_payout_calculator_without_product_type": (
        "1. Navigate to My Tools → Payout Calculator\n"
        "2. Fill Loan Amount but do NOT select Product Type\n"
        "3. Click 'Calculate now'\n"
        "4. Verify Payout Details section does NOT appear"
    ),
    "TestPayoutCalculator::test_payout_calculator_without_fulfilment_type": (
        "1. Navigate to My Tools → Payout Calculator\n"
        "2. Fill Loan Amount and select Product Type\n"
        "3. Do NOT select Fulfilment Type\n"
        "4. Click 'Calculate now'\n"
        "5. Verify Payout Details section does NOT appear"
    ),
    "TestPayoutCalculator::test_payout_calculates_successfully": (
        "1. Navigate to My Tools → Payout Calculator\n"
        "2. Fill Loan Amount with a valid value\n"
        "3. Select Product Type\n"
        "4. Select Fulfilment Type\n"
        "5. Click 'Calculate now'\n"
        "6. Verify 'Payout Details' result section is visible"
    ),

    # ── Raise Query ────────────────────────────────────────────────────────────
    "TestRaiseQuery::test_raise_query_without_issue_type": (
        "1. Navigate to Help & Support\n"
        "2. Open the Raise a Query form\n"
        "3. Fill Description but do NOT select Issue Type\n"
        "4. Click Submit\n"
        "5. Verify success message does NOT appear"
    ),
    "TestRaiseQuery::test_raise_query_without_description": (
        "1. Navigate to Help & Support\n"
        "2. Open the Raise a Query form\n"
        "3. Select Issue Type and Sub-issue, leave Description empty\n"
        "4. Click Submit\n"
        "5. Verify success message does NOT appear"
    ),
    "TestRaiseQuery::test_raise_query_successfully": (
        "1. Navigate to Help & Support\n"
        "2. Open the Raise a Query form\n"
        "3. Select Issue Type and Sub-issue\n"
        "4. Enter a description\n"
        "5. Click Submit\n"
        "6. Verify 'Thanks for letting us know!' message appears"
    ),

    # ── Add Role ───────────────────────────────────────────────────────────────
    "TestAddRole::test_add_role_without_name": (
        "1. Navigate to My Tools → Role Management\n"
        "2. Open the Add Role form\n"
        "3. Fill Description and select Permissions, leave Role Name empty\n"
        "4. Click Submit\n"
        "5. Verify form remains open (Role Name input still visible)"
    ),
    "TestAddRole::test_add_role_without_description": (
        "1. Navigate to My Tools → Role Management\n"
        "2. Open the Add Role form\n"
        "3. Fill Role Name and select Permissions, leave Description empty\n"
        "4. Click Submit\n"
        "5. Verify form remains open (Role Name input still visible)"
    ),
    "TestAddRole::test_add_role_successfully": (
        "1. Navigate to My Tools → Role Management\n"
        "2. Open the Add Role form\n"
        "3. Fill Role Name and Description with valid random data\n"
        "4. Select Permissions\n"
        "5. Click Submit\n"
        "6. Verify Roles and Permissions list heading is visible"
    ),

    # ── Edit Columns ───────────────────────────────────────────────────────────
    "TestEditColumnsApply::test_hiding_a_field_removes_its_column": (
        "1. On the leads dashboard count the current table header columns\n"
        "2. Open the Edit Columns panel and wait for 'Select Fields'\n"
        "3. Un-check the first toggleable optional field\n"
        "4. Verify the table header now has one column fewer\n"
        "5. Re-check the same field\n"
        "6. Verify the header column count is restored to the original"
    ),
    "TestEditColumnsApply::test_set_default_button_present": (
        "1. On the leads dashboard open the Edit Columns panel\n"
        "2. Verify the Set Default button is visible in the panel"
    ),

    "TestEditColumns::test_edit_columns_panel_opens": (
        "1. Navigate to the leads list\n"
        "2. Click 'Edit Columns'\n"
        "3. Verify 'Select Fields to show' section heading is visible\n"
        "4. Verify 'Order Fields' section heading is visible"
    ),

    # ── Advanced Filters ───────────────────────────────────────────────────────
    "TestAdvancedFiltersApply::test_apply_source_filter_changes_results": (
        "1. Click the toolbar Clear button to reset any server-side filter\n"
        "2. Read the baseline count from the 'All Leads (N)' tab\n"
        "3. Open the Advanced Filters panel\n"
        "4. Open the Source dropdown and select the first option\n"
        "5. Click Apply and wait for the grid to reload\n"
        "6. Verify the new All Leads count is lower than the baseline\n"
        "7. Clear the filter again so no persistent filter is left behind"
    ),
    "TestAdvancedFiltersApply::test_clear_all_resets_source": (
        "1. Click the toolbar Clear button to reset any server-side filter\n"
        "2. Open the Advanced Filters panel\n"
        "3. Open the Source dropdown and select the first option\n"
        "4. Click Clear All (this clears the selection and closes the panel)\n"
        "5. Re-open the Advanced Filters panel\n"
        "6. Verify the 'Select Source' placeholder is visible again"
    ),

    "TestAdvancedFilters::test_source_dropdown_opens": (
        "1. Navigate to leads list and open Advanced Filters panel\n"
        "2. Click the Source filter trigger\n"
        "3. Verify dropdown menu is visible"
    ),
    "TestAdvancedFilters::test_sub_source_dropdown_opens": (
        "1. Open Advanced Filters panel\n"
        "2. Click Source and select any option (unlocks Sub Source)\n"
        "3. Click the Sub Source filter trigger\n"
        "4. Verify Sub Source dropdown menu is visible"
    ),
    "TestAdvancedFilters::test_banks_dropdown_opens": (
        "1. Open Advanced Filters panel\n"
        "2. Click the Banks filter trigger\n"
        "3. Verify dropdown menu is visible"
    ),
    "TestAdvancedFilters::test_purchase_type_dropdown_opens": (
        "1. Open Advanced Filters panel\n"
        "2. Click the Purchase Type filter trigger\n"
        "3. Verify dropdown menu is visible"
    ),
    "TestAdvancedFilters::test_product_type_dropdown_opens": (
        "1. Open Advanced Filters panel\n"
        "2. Click the Product Type filter trigger\n"
        "3. Verify dropdown menu is visible"
    ),
    "TestAdvancedFilters::test_sub_type_dropdown_opens": (
        "1. Open Advanced Filters panel\n"
        "2. Click the Sub Type filter trigger\n"
        "3. Verify dropdown menu is visible"
    ),
    "TestAdvancedFilters::test_fulfillment_dropdown_opens": (
        "1. Open Advanced Filters panel\n"
        "2. Click the Fulfillment filter trigger\n"
        "3. Verify dropdown menu is visible"
    ),
    "TestAdvancedFilters::test_cities_dropdown_opens": (
        "1. Open Advanced Filters panel\n"
        "2. Click the Cities filter trigger\n"
        "3. Verify dropdown menu is visible"
    ),
    "TestAdvancedFilters::test_designation_dropdown_opens": (
        "1. Open Advanced Filters panel\n"
        "2. Click the Designation filter trigger\n"
        "3. Verify dropdown menu is visible"
    ),
    "TestAdvancedFilters::test_teammate_dropdown_opens": (
        "1. Open Advanced Filters panel\n"
        "2. Click Teammate Role trigger and select any role (unlocks Team Member)\n"
        "3. Click the Team Member dropdown trigger\n"
        "4. Verify Team Member dropdown is visible"
    ),
    "TestAdvancedFilters::test_assigned_to_dropdown_opens": (
        "1. Open Advanced Filters panel\n"
        "2. Click the Assigned To filter trigger\n"
        "3. Verify dropdown menu is visible"
    ),
    "TestAdvancedFilters::test_checklist_item_dropdown_opens": (
        "1. Open Advanced Filters panel\n"
        "2. Click the Checklist Item filter trigger\n"
        "3. Verify dropdown menu is visible"
    ),
    "TestAdvancedFilters::test_status_dropdown_opens": (
        "1. Open Advanced Filters panel\n"
        "2. Click Checklist Item and select any option (unlocks Status)\n"
        "3. Click the Status filter trigger\n"
        "4. Verify Status dropdown is visible"
    ),
    "TestAdvancedFilters::test_sub_status_dropdown_opens": (
        "1. Open Advanced Filters panel\n"
        "2. Click Checklist Item → select option to unlock Status\n"
        "3. Click Status → select option to unlock Sub Status\n"
        "4. Click the Sub Status filter trigger\n"
        "5. Verify Sub Status dropdown is visible"
    ),

    # ── Reassign Leads ─────────────────────────────────────────────────────────
    "TestReassignLeads::test_search_with_empty_text": (
        "1. Navigate to Actions → Reassign Leads\n"
        "2. Select a search type from the dropdown\n"
        "3. Click Search without entering any search text\n"
        "4. Verify lead results count is 0"
    ),
    "TestReassignLeads::test_assign_lead_disabled_without_lead_selected": (
        "1. Navigate to Actions → Reassign Leads\n"
        "2. Search for a lead by ID\n"
        "3. Click 'Reassign Leads' without selecting any lead\n"
        "4. Verify Assign Lead button has cursor: not-allowed"
    ),
    "TestReassignLeads::test_assign_lead_disabled_without_assignee_selected": (
        "1. Navigate to Actions → Reassign Leads\n"
        "2. Search for a lead, check the lead checkbox\n"
        "3. Click 'Reassign Leads' without selecting an assignee\n"
        "4. Verify Assign Lead button has cursor: not-allowed"
    ),
    "TestReassignLeads::test_reassign_lead_successfully": (
        "1. Navigate to Actions → Reassign Leads\n"
        "2. Search for the lead by ID\n"
        "3. Select the lead via its checkbox\n"
        "4. Select an assignee from the assignee panel\n"
        "5. Click 'Assign Lead'\n"
        "6. Verify 'Data updated in the system' toast appears"
    ),

    # ── Reports Dashboard ──────────────────────────────────────────────────────
    "TestReportsDashboard::test_reports_dashboard_loads": (
        "1. Click the Reports link in the navigation\n"
        "2. Wait for the Advanced Filters button to confirm the page has loaded\n"
        "3. Verify the Total Active Leads stat is visible\n"
        "4. Verify the Sanctioned and Disbursed stat cards are visible\n"
        "5. Verify the Lost Analysis section is visible"
    ),
    "TestReportsDashboard::test_more_reports_coming_soon": (
        "1. Navigate to the Reports page\n"
        "2. Click the More Reports button\n"
        "3. Verify the 'Coming Soon' state is visible"
    ),

    # ── Reports Advanced Filters ───────────────────────────────────────────────
    "TestReportsAdvancedFilters::test_filter_1_dropdown_opens": (
        "1. Navigate to the Reports page\n"
        "2. Open the Advanced Filters panel\n"
        "3. Click the first filter dropdown\n"
        "4. Verify dropdown menu is visible"
    ),
    "TestReportsAdvancedFilters::test_filter_2_dropdown_opens": (
        "1. Navigate to the Reports page\n"
        "2. Open the Advanced Filters panel\n"
        "3. Click the second filter dropdown\n"
        "4. Verify dropdown menu is visible"
    ),
    "TestReportsAdvancedFilters::test_filter_3_dropdown_opens": (
        "1. Navigate to the Reports page\n"
        "2. Open the Advanced Filters panel\n"
        "3. Click the third filter dropdown\n"
        "4. Verify dropdown menu is visible"
    ),
    "TestReportsAdvancedFilters::test_source_dropdown_opens": (
        "1. Navigate to Reports page and open Advanced Filters\n"
        "2. Click the Source filter trigger\n"
        "3. Verify dropdown menu is visible"
    ),
    "TestReportsAdvancedFilters::test_filter_5_dropdown_opens": (
        "1. Navigate to the Reports page\n"
        "2. Open the Advanced Filters panel\n"
        "3. Click the fifth filter dropdown\n"
        "4. Verify dropdown menu is visible"
    ),
    "TestReportsAdvancedFilters::test_sub_source_dropdown_opens": (
        "1. Navigate to Reports page and open Advanced Filters\n"
        "2. Click Source and select any option (unlocks Sub Source)\n"
        "3. Click the Sub Source filter trigger\n"
        "4. Verify Sub Source dropdown is visible"
    ),
    "TestReportsAdvancedFilters::test_banks_dropdown_opens": (
        "1. Navigate to Reports page and open Advanced Filters\n"
        "2. Click the Banks filter trigger\n"
        "3. Verify dropdown menu is visible"
    ),

    # ── Recommended Docs ───────────────────────────────────────────────────────
    "TestRecommendedDocs::test_get_recommended_docs_successfully": (
        "1. Navigate to home page and search for the lead\n"
        "2. Open the lead detail page in a new tab\n"
        "3. Navigate to the Documents tab\n"
        "4. Open the Recommended Docs form\n"
        "5. Fill all four required fields with valid data\n"
        "6. Submit the form and confirm\n"
        "7. Verify the Success toast appears"
    ),

    # ── Lead Detail ────────────────────────────────────────────────────────────
    "TestLeadDetail::test_details_tab_shows_cards": (
        "1. Search for the lead on the dashboard and open it in a new tab\n"
        "2. Open the Details tab\n"
        "3. Verify the Loan Details card is visible\n"
        "4. Verify the Customer Details card is visible\n"
        "5. Verify the Income Details card is visible\n"
        "6. Verify the Property Details card is visible"
    ),
    "TestLeadDetail::test_edit_wizard_opens": (
        "1. Search for the lead and open it in a new tab\n"
        "2. Click the edit pencil next to the History tab\n"
        "3. Verify the edit wizard heading is visible\n"
        "4. Verify the Save & Exit button is visible\n"
        "5. Verify the Next button is visible"
    ),
    "TestLeadDetail::test_edit_loan_details_saves": (
        "1. Search for the lead and open it in a new tab\n"
        "2. Click the edit pencil to open the edit wizard\n"
        "3. Fill the Loan Amount field on the wizard's first step\n"
        "4. Select the first Desired Tenure option (required for the save to pass)\n"
        "5. Click Save & Exit\n"
        "6. Verify the edit success toast appears"
    ),
    "TestLeadDetail::test_history_tab_shows_timeline": (
        "1. Search for the lead and open it in a new tab\n"
        "2. Open the History tab\n"
        "3. Verify the first timeline entry (with its 'BY <author>' line) is visible"
    ),
    "TestLeadDetail::test_remarks_modal_opens": (
        "1. Search for the lead and open it in a new tab\n"
        "2. Click the Remarks button and wait for the modal\n"
        "3. Verify the remark text area is visible\n"
        "4. Verify the modal Save button is visible"
    ),
    "TestLeadDetail::test_remark_without_text_shows_error": (
        "1. Search for the lead and open it in a new tab\n"
        "2. Open the Remarks modal\n"
        "3. Click Save without entering any text\n"
        "4. Verify the 'Please enter a remark' error toast appears"
    ),
    "TestLeadDetail::test_add_remark_successfully": (
        "1. Search for the lead and open it in a new tab\n"
        "2. Open the Remarks modal\n"
        "3. Enter the remark text in the text area\n"
        "4. Click Save\n"
        "5. Verify the 'Remark saved successfully' toast appears"
    ),
    "TestLeadDetail::test_documents_tab_shows_upload": (
        "1. Search for the lead and open it in a new tab\n"
        "2. Open the Documents tab\n"
        "3. Verify at least one document file input is present\n"
        "4. Verify the first file input's accept attribute is 'image/*,.pdf'"
    ),
    "TestLeadDetail::test_document_upload_accepts_pdf": (
        "1. Search for the lead and open it in a new tab\n"
        "2. Open the Documents tab\n"
        "3. Write a small valid PDF to a temporary path\n"
        "4. Set that PDF on the first document file input\n"
        "5. Verify the input now holds exactly one file (the control accepted it)"
    ),
    "TestLeadDetail::test_lost_lead_shows_reopen": (
        "1. Search for the lost lead and open it in a new tab\n"
        "2. Verify the Reopen button is visible\n"
        "3. Verify the 'Lost' status badge is visible"
    ),
    "TestLeadDetail::test_reopen_without_remarks_shows_error": (
        "1. Search for the lost lead and open it in a new tab\n"
        "2. Click Reopen and wait for the modal\n"
        "3. Click Save without entering any remarks\n"
        "4. Verify the 'Please enter remarks' error toast appears"
    ),
    "TestLeadDetail::test_reopen_lead_successfully": (
        "1. Search for the lost lead and open it in a new tab\n"
        "2. Click Reopen and wait for the modal\n"
        "3. Enter the reopen remarks in the text area\n"
        "4. Click Save\n"
        "5. Verify the reopen success toast appears"
    ),

    # ── My Team — Partners ─────────────────────────────────────────────────────
    "TestTeamPartners::test_add_picker_offers_roles": (
        "1. Navigate to My Team\n"
        "2. Click '+ Add Teammate' to open the role picker\n"
        "3. Verify the Team Member role option is visible\n"
        "4. Verify the Sourcing Partner role option is visible\n"
        "5. Verify the Business Partner role option is visible"
    ),
    "TestTeamPartners::test_business_partner_form_fields": (
        "1. Navigate to My Team and open the Add role picker\n"
        "2. Choose the Business Partner role\n"
        "3. Verify the Full Name field is visible\n"
        "4. Verify the Mobile field is visible\n"
        "5. Verify the Email field is visible\n"
        "6. Verify the PAN field is visible"
    ),
    "TestTeamPartners::test_business_partner_submit_enabled_when_filled": (
        "1. Navigate to My Team and open the Business Partner form\n"
        "2. Fill Full Name, a generated mobile and a generated email\n"
        "3. Leave PAN empty (a PAN value disables Submit — known app bug)\n"
        "4. Verify the Submit button is enabled"
    ),
    "TestTeamPartners::test_business_partner_pan_disables_submit": (
        "1. Navigate to My Team and open the Business Partner form\n"
        "2. Fill Full Name, mobile and email, leaving PAN empty\n"
        "3. Verify Submit is enabled at this point\n"
        "4. Enter a valid-format PAN and blur the field\n"
        "5. Verify Submit is now disabled — documents the current app behaviour"
    ),
    "TestTeamPartners::test_channel_partner_tab_loads": (
        "1. Navigate to My Team\n"
        "2. Click the Channel Partner tab and wait for it to load\n"
        "3. Verify the Channel Partner tab is visible\n"
        "4. Verify the Add control is still available on this tab"
    ),
    "TestTeamPartners::test_channel_partner_add_is_sourcing_partner": (
        "1. Navigate to My Team and open the Channel Partner tab\n"
        "2. Click the Add control to open the role picker\n"
        "3. Verify the Sourcing Partner role is offered\n"
        "   (Channel Partner has no dedicated add form of its own)"
    ),

    # ── Bulk Actions ───────────────────────────────────────────────────────────
    "TestBulkActions::test_actions_menu_options": (
        "1. On the leads dashboard click the Actions button\n"
        "2. Wait for the menu items to render and read their combined text\n"
        "3. Verify 'Reassign Leads' is offered\n"
        "4. Verify 'Bulk Import' is offered\n"
        "5. Verify 'Export Leads' is offered"
    ),

    # ── My Earnings ────────────────────────────────────────────────────────────
    "TestMyEarnings::test_earnings_page_loads": (
        "1. Click My Earnings in the navigation menu\n"
        "2. Wait for the /my-saathi-earnings URL and the grid to load\n"
        "3. Verify the earnings results table is visible\n"
        "4. Verify the table has at least one row"
    ),
    "TestMyEarnings::test_tab_switching": (
        "1. Navigate to My Earnings and wait for the grid\n"
        "2. Click the tab under test (Earned / Paid / Projected)\n"
        "3. Wait for the network to settle and the table to reload\n"
        "4. Verify the results table is visible\n"
        "5. Verify that tab loaded with at least one row"
    ),
    "TestMyEarnings::test_search_by_lead_id": (
        "1. Navigate to My Earnings and wait for the grid\n"
        "2. Read the Lead ID from the first row of the table\n"
        "3. Open the 'Search By' control and choose 'Lead ID'\n"
        "4. Fill that lead ID into the keyword box and click Search\n"
        "5. Verify the searched lead ID is present in the results body\n"
        "6. Verify every returned row matches the queried Lead ID"
    ),
    "TestMyEarnings::test_reset_filter": (
        "1. Navigate to My Earnings and record the full row count\n"
        "2. Read the Lead ID from the first row\n"
        "3. Search by that Lead ID and verify the grid narrowed\n"
        "4. Click Reset and wait for the grid to repopulate\n"
        "5. Verify the row count is back to the original full count"
    ),

    # ── Help & Support ─────────────────────────────────────────────────────────
    "TestHelpSupport::test_help_page_loads": (
        "1. Click Help & Support in the navigation menu\n"
        "2. Wait for the /help-support URL and the page to settle\n"
        "3. Verify the FAQs tab is visible\n"
        "4. Verify the Tickets tab is visible\n"
        "5. Verify the Raise a Query button is visible"
    ),
    "TestHelpSupport::test_faqs_tab_lists_questions": (
        "1. Navigate to Help & Support\n"
        "2. Click the FAQs tab\n"
        "3. Verify a known FAQ question ('How long will it take...') is listed"
    ),
    "TestHelpSupport::test_faq_accordion_toggles": (
        "1. Navigate to Help & Support and open the FAQs tab\n"
        "2. Locate the first FAQ's answer paragraph\n"
        "3. Verify the answer is visible (expanded by default)\n"
        "4. Click the first FAQ question to toggle it\n"
        "5. Verify the answer is now hidden (collapsed)"
    ),
    "TestHelpSupport::test_tickets_tab_loads": (
        "1. Navigate to Help & Support\n"
        "2. Click the Tickets tab\n"
        "3. Verify the 'Reach out to Ambak' support contact section is visible"
    ),

    # ── Profile ────────────────────────────────────────────────────────────────
    "TestProfile::test_profile_page_loads": (
        "1. Navigate directly to the profile page URL\n"
        "2. Wait for the page to settle and Save and Next to appear\n"
        "3. Verify the Basic Details tab is visible\n"
        "4. Verify the Save and Next button is visible"
    ),
    "TestProfile::test_basic_details_fields": (
        "1. Open the profile page\n"
        "2. Verify the company mobile field is visible\n"
        "3. Verify the SPOC name field is visible\n"
        "4. Verify the pincode field is visible"
    ),
    "TestProfile::test_profile_tabs_present": (
        "1. Open the profile page\n"
        "2. Verify the Basic Details tab is visible\n"
        "3. Verify the KYC Documents tab is visible\n"
        "4. Verify the Bank Details tab is visible"
    ),
    "TestProfile::test_kyc_documents_tab_opens": (
        "1. Open the profile page\n"
        "2. Click the KYC Documents tab\n"
        "3. Verify the KYC Documents tab is visible after opening"
    ),

    # ── CIBIL ──────────────────────────────────────────────────────────────────
    "TestCibil::test_cibil_page_loads": (
        "1. Navigate to My Tools and open the CIBIL tool\n"
        "2. Verify the PAN input is visible\n"
        "3. Verify the 'no impact on your credit score' note is visible"
    ),
    "TestCibil::test_fetch_without_pan_shows_error": (
        "1. Open the CIBIL tool from My Tools\n"
        "2. Click Fetch with the PAN field left empty\n"
        "3. Verify the 'valid 10-digit PAN number' error toast appears"
    ),
    "TestCibil::test_fetch_invalid_pan_shows_error": (
        "1. Open the CIBIL tool from My Tools\n"
        "2. Enter a malformed PAN ('ABC') in the PAN field\n"
        "3. Click Fetch\n"
        "4. Verify the 'valid 10-digit PAN number' error toast appears"
    ),
    "TestCibil::test_fetch_valid_pan_success": (
        "1. Open the CIBIL tool from My Tools\n"
        "2. Enter a valid-format PAN\n"
        "3. Click Fetch\n"
        "4. Verify the 'PAN details fetched successfully!' toast appears"
    ),
    "TestCibil::test_continue_without_details_shows_pan_error": (
        "1. Open the CIBIL tool from My Tools\n"
        "2. Click Continue with the whole form left empty\n"
        "3. Verify a PAN-required error toast appears"
    ),
    "TestCibil::test_continue_without_first_name": (
        "1. Open the CIBIL tool from My Tools\n"
        "2. Fill the PAN field\n"
        "3. Fill last name, email and mobile, leaving first name empty\n"
        "4. Set the date of birth via the year/day picker\n"
        "5. Click Continue\n"
        "6. Verify the 'Please enter first name' error toast appears"
    ),
    "TestCibil::test_continue_with_invalid_email": (
        "1. Open the CIBIL tool from My Tools\n"
        "2. Fill the PAN field\n"
        "3. Fill first name, last name and mobile, with a malformed email\n"
        "4. Set the date of birth via the year/day picker\n"
        "5. Click Continue\n"
        "6. Verify the 'Please enter a valid email' error toast appears"
    ),
    "TestCibil::test_continue_with_invalid_mobile": (
        "1. Open the CIBIL tool from My Tools\n"
        "2. Fill the PAN field\n"
        "3. Fill first name, last name and email, with a short mobile ('123')\n"
        "4. Set the date of birth via the year/day picker\n"
        "5. Click Continue\n"
        "6. Verify the 'valid 10-digit mobile' error toast appears"
    ),
    "TestCibil::test_continue_without_dob": (
        "1. Open the CIBIL tool from My Tools\n"
        "2. Fill the PAN field\n"
        "3. Fill first name, last name, email and mobile\n"
        "4. Leave the date of birth unset and click Continue\n"
        "5. Verify the 'Please enter date of birth' error toast appears"
    ),
    "TestCibil::test_dob_picker_sets_date": (
        "1. Open the CIBIL tool from My Tools\n"
        "2. Click the DOB field to open the date picker\n"
        "3. Click the header year label to open the year grid\n"
        "4. Select the year 1995, returning to the day view\n"
        "5. Select day 15\n"
        "6. Verify the DOB field reads 15/<mm>/1995"
    ),
    "TestCibil::test_full_form_advances_to_fulfilment_step": (
        "1. Open the CIBIL tool from My Tools\n"
        "2. Fill the PAN field\n"
        "3. Fill first name, last name, email and mobile with valid data\n"
        "4. Set a valid date of birth via the picker\n"
        "5. Click Continue\n"
        "6. Verify the 'Would you like Ambak to fulfil this lead?' prompt appears\n"
        "   (the flow stops here, so no lead is actually created)"
    ),

    # ── ABB Calculator ─────────────────────────────────────────────────────────
    "TestAbbCalculator::test_abb_tool_opens": (
        "1. Navigate to My Tools and open the ABB Calculator\n"
        "2. Verify the ABB heading is visible\n"
        "3. Verify the upload button is visible"
    ),
    "TestAbbCalculator::test_abb_shows_intro_prompt": (
        "1. Open the ABB Calculator from My Tools\n"
        "2. Verify the 'How would you like to share the income details?' prompt\n"
        "   is visible"
    ),
    "TestAbbCalculator::test_abb_shows_statement_instructions": (
        "1. Open the ABB Calculator from My Tools\n"
        "2. Verify the PDF-only instruction note is visible\n"
        "3. Verify the OD/CC account instruction note is visible\n"
        "4. Verify the most-recent-statement instruction note is visible"
    ),
    "TestAbbCalculator::test_abb_file_input_accepts_pdf_only": (
        "1. Open the ABB Calculator from My Tools\n"
        "2. Verify the file input's accept attribute is exactly 'application/pdf'"
    ),
    "TestAbbCalculator::test_abb_accepts_pdf_file": (
        "1. Open the ABB Calculator from My Tools\n"
        "2. Write a small valid PDF to a temporary path\n"
        "3. Set that PDF on the statement file input\n"
        "4. Verify the input now holds exactly one file"
    ),

    # ── APF Search ─────────────────────────────────────────────────────────────
    "TestApfSearch::test_apf_page_loads": (
        "1. Navigate to My Tools and open the APF Finder\n"
        "2. Verify the APF Finder heading is visible\n"
        "3. Verify the search box is visible"
    ),
    "TestApfSearch::test_apf_results_table_headers": (
        "1. Open the APF Finder from My Tools\n"
        "2. Verify the BUILDER column header is visible\n"
        "3. Verify the PROJECT column header is visible\n"
        "4. Verify the BANK column header is visible"
    ),
    "TestApfSearch::test_apf_city_dropdown_opens": (
        "1. Open the APF Finder from My Tools\n"
        "2. Click the city control to open its dropdown\n"
        "3. Verify the first city option is visible\n"
        "4. Verify at least one city option is listed"
    ),
    "TestApfSearch::test_apf_select_city": (
        "1. Open the APF Finder from My Tools\n"
        "2. Open the city dropdown\n"
        "3. Click the option matching the configured test city\n"
        "4. Verify that city name is now shown on the page"
    ),
    "TestApfSearch::test_apf_search_no_match_shows_empty_state": (
        "1. Open the APF Finder from My Tools\n"
        "2. Type a nonsense query into the search box and press Enter\n"
        "3. Verify the 'Builder Not Found' empty state is visible"
    ),

    # ── Website Settings ───────────────────────────────────────────────────────
    "TestWebsiteSettings::test_website_settings_page_loads": (
        "1. Navigate to My Tools and open Website Settings\n"
        "2. Verify each of the nine editor section headings is visible"
    ),
    "TestWebsiteSettings::test_all_sections_have_save_buttons": (
        "1. Open Website Settings from My Tools\n"
        "2. Count the Save Changes buttons on the page\n"
        "3. Verify there is exactly one per section (nine total)"
    ),
    "TestWebsiteSettings::test_save_header_section": (
        "1. Open Website Settings from My Tools\n"
        "2. Scroll to the Header section and click its Save Changes button\n"
        "3. Verify the Header success toast appears"
    ),
    "TestWebsiteSettings::test_save_hero_section": (
        "1. Open Website Settings from My Tools\n"
        "2. Scroll to the Hero Section and click its Save Changes button\n"
        "3. Verify the Hero success toast appears"
    ),
    "TestWebsiteSettings::test_save_testimonials_section": (
        "1. Open Website Settings from My Tools\n"
        "2. Scroll to the Testimonials section and click its Save Changes button\n"
        "3. Verify the generic save success toast appears"
    ),
    "TestWebsiteSettings::test_save_calculator_section": (
        "1. Open Website Settings from My Tools\n"
        "2. Scroll to the Calculator Section and click its Save Changes button\n"
        "3. Verify the generic save success toast appears"
    ),
    "TestWebsiteSettings::test_save_faq_section": (
        "1. Open Website Settings from My Tools\n"
        "2. Scroll to the FAQs section and click its Save Changes button\n"
        "3. Verify the FAQ success toast appears"
    ),
    "TestWebsiteSettings::test_edit_hero_heading_and_save": (
        "1. Open Website Settings from My Tools\n"
        "2. Read the current hero heading value\n"
        "3. Re-fill the field with that same value (live content unchanged)\n"
        "4. Click the Hero Section's Save Changes button\n"
        "5. Verify the Hero success toast appears"
    ),
    "TestWebsiteSettings::test_add_feature_adds_row": (
        "1. Open Website Settings from My Tools\n"
        "2. Count the existing feature inputs\n"
        "3. Click '+ Add Feature'\n"
        "4. Verify the feature input count increased by exactly one"
    ),
    "TestWebsiteSettings::test_add_faq_block": (
        "1. Open Website Settings from My Tools\n"
        "2. Count the existing input and textarea elements on the page\n"
        "3. Click '+ Add FAQ' and let the new block render\n"
        "4. Verify the input/textarea count has increased (a new FAQ block added)"
    ),

    # ── Logout ─────────────────────────────────────────────────────────────────
    "TestLogout::test_logout_redirects_to_login": (
        "1. Open the profile page\n"
        "2. Navigate to the logout route to end the session\n"
        "3. Wait for the redirect to complete\n"
        "4. Verify the login page's 'Mobile or Email *' input is visible again"
    ),
}

# Auto-scanned docstrings fill in any test not in _EXPLICIT_STEPS.
# Explicit entries always win; this only adds what's missing.
TEST_STEPS: dict[str, str] = {**_scan_docstrings(), **_EXPLICIT_STEPS}
