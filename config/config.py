import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://pre-saathi.ambak.com/")

BROWSER = os.getenv("BROWSER", "chromium")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
SLOW_MO = int(os.getenv("SLOW_MO", "0"))

# Credentials must come from .env — no defaults in source so secrets never
# land in git history. A missing value fails fast at login with a clear error.
LOGIN_MOBILE = os.getenv("LOGIN_MOBILE", "")
LOGIN_OTP = os.getenv("LOGIN_OTP", "")

TIMEOUT     = int(os.getenv("TIMEOUT",     "45000"))  # ms — element actions
NAV_TIMEOUT = int(os.getenv("NAV_TIMEOUT", "60000"))  # ms — page navigation

# The redesigned "Add New Lead" modal dropped the State field entirely — City
# is now the only location field. Purchase Type is a new, optional field
# (#property_type); left unset by default since most tests don't need it.
LEAD_DATA = {
    "first_name": "Test",
    "last_name": "User",
    "mobile": os.getenv("LEAD_DUPLICATE_MOBILE", "9275620745"),
    "loan_type":     os.getenv("LEAD_LOAN_TYPE",     "Home Loan"),
    "loan_sub_type": os.getenv("LEAD_LOAN_SUB_TYPE", "BT"),
    "employment_type": os.getenv("LEAD_EMPLOYMENT_TYPE", "Salaried"),
    "purchase_type": os.getenv("LEAD_PURCHASE_TYPE", ""),  # optional; empty = leave unset
    "city_search":   os.getenv("LEAD_CITY_SEARCH",   "gurgaon"),
    "city_option":   os.getenv("LEAD_CITY_OPTION",   "Gurgaon"),
    "loan_amount":   os.getenv("LEAD_LOAN_AMOUNT",   "5000000"),
    "remarks":       os.getenv("LEAD_REMARKS",       "Automated test lead - please ignore"),
}

FOLLOWUP_DATA = {
    "type":    os.getenv("FOLLOWUP_TYPE",    "Call"),
    "time":    os.getenv("FOLLOWUP_TIME",    "12:00"),
    "comment": os.getenv("FOLLOWUP_COMMENT", "Automated test followup - please ignore"),
}

MOVE_TO_LOGIN_DATA = {
    # No "lead_id" key here — the lead to move is always resolved by the
    # `lead_id` conftest fixture (shared_state, then --lead-id/LOGIN_LEAD_ID),
    # never read out of this dict.
    "loan_amount": os.getenv("LOGIN_AMOUNT",  "10000000"),
    "login_date":  os.getenv("LOGIN_DATE",    ""),   # YYYY-MM-DD; empty = today
    "bank_search": os.getenv("LOGIN_BANK_SEARCH", "icici"),
    "bank_name":   os.getenv("LOGIN_BANK_NAME",   "ICICI Bank"),
    "branch":      os.getenv("LOGIN_BRANCH",      "testing"),
    "banker":      os.getenv("LOGIN_BANKER",      "abhishek.pathak@ambak.com"),
    "rsm":         os.getenv("LOGIN_RSM",         "abhishek.pathak@ambak.com"),
    "login_id":    os.getenv("LOGIN_ID",          "42jgrsas"),
}

MOVE_TO_SANCTION_DATA = {
    # No "lead_id" key — resolved by the `sanction_lead_id` fixture, same as
    # MOVE_TO_LOGIN_DATA above.
    "loan_amount":   os.getenv("SANCTION_AMOUNT",       "10000000"),
    "sanction_date": os.getenv("SANCTION_DATE",         ""),   # YYYY-MM-DD; empty = today
    # Must match the bank's LAN format (4 alphanum + 4 letters + 10 letters) —
    # confirmed live on 2026-08-18; a plain alphanumeric string like the old
    # default ("vewggef3") is rejected with "Invalid Sanction ID format".
    "sanction_id":   os.getenv("SANCTION_ID",           "A1B2wxyzabcdefghij"),
    "bank_search":   os.getenv("SANCTION_BANK_SEARCH",  "icici"),
    "bank_name":     os.getenv("SANCTION_BANK_NAME",    "ICICI Bank"),
    "branch":        os.getenv("SANCTION_BRANCH",       "testing"),
    "banker":        os.getenv("SANCTION_BANKER",       "abhishek.pathak@ambak.com"),
}

ADD_TEAMMATE_DATA = {
    "full_name": os.getenv("TEAMMATE_FULL_NAME", "Test User"),
    "mobile":    os.getenv("TEAMMATE_MOBILE",    "7903723573"),
}

ADD_SOURCING_PARTNER_DATA = {
    "full_name": os.getenv("SOURCING_PARTNER_FULL_NAME", "Test Partner"),
    "mobile":    os.getenv("SOURCING_PARTNER_MOBILE",    "8903821084"),
    "email":     os.getenv("SOURCING_PARTNER_EMAIL",     "test.partner@testmail.com"),
}

# Edge-case mobile numbers for the Add Teammate / Add Sourcing Partner forms.
# Each tuple is (label, value) — labels double as pytest ids so failures are
# readable without decoding the raw string. Kept in one place so both forms
# exercise the same matrix. See the "Edge-case mobile-number coverage" plan.
VALID_MOBILE_BOUNDARIES = [
    ("prefix_6_all_zeros",   "6000000000"),
    ("prefix_9_all_nines",   "9999999999"),
    ("prefix_7_low_edge",    "7000000001"),
    ("prefix_8_high_edge",   "8999999999"),
]

INVALID_MOBILES = [
    # wrong length
    ("too_short_9_digits",   "999999999"),
    # The Mobile field has maxlength=10, so browsers truncate any typed value
    # to its first 10 characters before it can be submitted — an 11-digit
    # value starting with a valid prefix (e.g. "9999999999...") would simply
    # truncate to a valid 10-digit number and legitimately succeed. Starting
    # with an illegal prefix keeps the truncated value itself invalid, so
    # this still genuinely exercises the "too long" input path.
    ("too_long_11_digits",   "59999999999"),
    # illegal prefix
    ("prefix_5_illegal",     "5999999999"),
    ("prefix_1_illegal",     "1234567890"),
    ("leading_zero",         "0987654321"),
    ("all_zeros",            "0000000000"),
    # paste artifacts
    ("country_code_plus91",  "+919876543210"),
    ("country_code_91_space","91 9876543210"),
    ("hyphenated",           "98765-43210"),
    ("internal_space",       "9876 543210"),
    ("leading_trailing_ws",  " 9876543210 "),
    ("excel_scientific",     "9.8765e+09"),
    # non-numeric
    ("alpha_suffix",         "98765abcde"),
    ("pure_alpha",           "abcdefghij"),
    ("fullwidth_digits",     "９８７６５４３２１０"),
    ("script_injection",     "<script>alert(1)</script>"),
    ("negative_sign",        "-987654321"),
    ("whitespace_only",      "   "),
]

TEAM_FILTER_DATA = {
    "date_range_days": int(os.getenv("TEAM_FILTER_DATE_RANGE_DAYS", "2")),
    "city_search":     os.getenv("TEAM_FILTER_CITY_SEARCH", "gurga"),
}

SEARCH_FILTER_DATA = {
    "date_option":  os.getenv("FILTER_DATE_OPTION",  "Yesterday"),
    "city_search":  os.getenv("FILTER_CITY_SEARCH",  "gurg"),
    "city_option":  os.getenv("FILTER_CITY_OPTION",  "Gurgaon"),
    "bank_search":  os.getenv("FILTER_BANK_SEARCH",  "icici"),
}

MARK_AS_LOST_DATA = {
    # No "lead_id" key — mark_as_lost_lead_id always self-seeds a fresh,
    # markable lead (see conftest.py); MARK_AS_LOST_LEAD_ID is intentionally
    # not consulted since a marked-lost lead can't be re-marked on rerun.
    # "post offer" reasons only appear once a lead has an offer; for a pre-login
    # lead the base reason list is shown, so default to one that always exists.
    "reason":  os.getenv("MARK_AS_LOST_REASON",  "Customer not interested"),
    "comment": os.getenv("MARK_AS_LOST_COMMENT",  "No comment"),
}

ROLE_DATA = {
    "name":        os.getenv("ROLE_NAME",        ""),  # generated per run if empty
    "description": os.getenv("ROLE_DESCRIPTION", "Test role - automated test run"),
}

RAISE_QUERY_DATA = {
    "issue":       os.getenv("QUERY_ISSUE",       "Lead/Case issue"),
    "subissue":    os.getenv("QUERY_SUBISSUE",     "Incorrect Details"),
    "description": os.getenv("QUERY_DESCRIPTION",  "Test query - please ignore. Automated test run."),
}

PAYOUT_CALCULATOR_DATA = {
    "loan_amount":     os.getenv("PAYOUT_LOAN_AMOUNT",     "1000000"),
    "product_type":    os.getenv("PAYOUT_PRODUCT_TYPE",    "Home Loan"),
    "fulfilment_type": os.getenv("PAYOUT_FULFILMENT_TYPE", "I will do it myself"),
}

# The Check Offers tool was redesigned into a per-lead "Loan Offer Calculator"
# opened via "Checkout Loan Offers!" on the lead detail page (it errors with
# "Lead ID is missing" if opened standalone from My Tools). It no longer creates
# a lead — it computes offers for an existing one. These values drive the default
# Self-Employed non-Professional path through to the offers results screen.
CHECK_OFFERS_DATA = {
    "loan_type":        os.getenv("CHECK_OFFERS_LOAN_TYPE",        "New Loan"),
    "loan_product":     os.getenv("CHECK_OFFERS_LOAN_PRODUCT",     "Home Loan"),
    # The income/business fields below drive the Self-Employed path, so the
    # employment type must be selected explicitly (the tool defaults to Salaried,
    # whose step 3 has no business-details fields). Options offered by the tool:
    # "Salaried" / "Self-Employed non-Professional".
    "employment_type":  os.getenv("CHECK_OFFERS_EMPLOYMENT_TYPE",  "Self-Employed non-Professional"),
    "loan_amount":      os.getenv("CHECK_OFFERS_LOAN_AMOUNT",      "1000000"),
    "company_type":     os.getenv("CHECK_OFFERS_COMPANY_TYPE",     "Pvt Ltd"),
    "age_of_business":  os.getenv("CHECK_OFFERS_AGE_OF_BUSINESS",  "5"),
    "credit_score":     os.getenv("CHECK_OFFERS_CREDIT_SCORE",     "750 - 780"),
    "age_range":        os.getenv("CHECK_OFFERS_AGE_RANGE",        "21-40 yrs"),
    "gender":           os.getenv("CHECK_OFFERS_GENDER",           "Male"),
    "expected_property_value": os.getenv("CHECK_OFFERS_PROPERTY_VALUE", "5000000"),
    "state":            os.getenv("CHECK_OFFERS_STATE",            "Karnataka"),
    # Manual ITR / NPAT income (2-year assessment) — field names match the form.
    "income": {
        "npat_curr": "1200000", "depreciation_curr": "50000",
        "interest_curr": "10",  "taxpaid_curr": "100000",
        "npat_prev": "1000000", "depreciation_prev": "40000",
        "interest_prev": "10",  "taxpaid_prev": "80000",
    },
}

RECOMMENDED_DOCS_DATA = {
    # No "lead_id" key — always overridden by the recommended_docs_lead_id
    # fixture at the call site (tests/test_08_recommended_docs.py).
    "employment_type": os.getenv("REC_DOCS_EMPLOYMENT_TYPE", "Salaried"),
    # TODO: rename co_applicant to match the actual field label once confirmed
    "co_applicant":    os.getenv("REC_DOCS_CO_APPLICANT",    "Yes"),
    "doc_type":        os.getenv("REC_DOCS_DOC_TYPE",        "Builder Endorsement"),
    "property_status": os.getenv("REC_DOCS_PROPERTY_STATUS", "Ready to move"),
}

REASSIGN_LEAD_DATA = {
    # No "lead_id" key — always resolved by the reassign_lead_id fixture.
    "assignee_id": os.getenv("REASSIGN_ASSIGNEE_ID", "28"),
}

CIBIL_DATA = {
    # PAN is a valid-format test PAN. The dummy PAN returns no real bureau data,
    # so the happy path advances to the fulfilment step rather than a live score.
    "pan":        os.getenv("CIBIL_PAN",        "ABCDE1234F"),
    "first_name": os.getenv("CIBIL_FIRST_NAME", "Test"),
    "last_name":  os.getenv("CIBIL_LAST_NAME",  "User"),
    "email":      os.getenv("CIBIL_EMAIL",      "test.user@example.com"),
    "mobile":     os.getenv("CIBIL_MOBILE",     "9876543210"),
    "dob_year":   int(os.getenv("CIBIL_DOB_YEAR", "1995")),
    "dob_day":    int(os.getenv("CIBIL_DOB_DAY",  "15")),
}

LEAD_DETAIL_DATA = {
    # No "lead_id" key — always resolved by the lead_detail_id fixture
    # (LEAD_DETAIL_ID / --lead-detail-id is read there, not from this dict).
    "loan_amount": os.getenv("LEAD_DETAIL_LOAN_AMOUNT", "2000000"),
    "remark":      os.getenv("LEAD_DETAIL_REMARK", "Automated test remark — please ignore"),
}

# REOPEN_LEAD_ID (a lost lead for isolated Reopen-only runs) is read directly
# from the environment by the reopen_lead_id fixture in conftest.py — not
# through a module constant here, so a stale hardcoded default can't linger.

APF_SEARCH_DATA = {
    "city":            os.getenv("APF_CITY",            "Bangalore"),
    # A random string that no builder matches, to exercise the empty state.
    "no_match_query":  os.getenv("APF_NO_MATCH_QUERY",  "zzqwxnobuilder"),
}

MOVE_TO_DISBURSE_DATA = {
    # No "lead_id" key — resolved by the `disburse_lead_id` fixture, same as
    # MOVE_TO_LOGIN_DATA above.
    "loan_amount":   os.getenv("DISBURSE_AMOUNT",      "10000000"),
    "disbursal_date": os.getenv("DISBURSE_DATE",       ""),   # YYYY-MM-DD; empty = today
    "disbursed_id":  os.getenv("DISBURSE_ID",          "vreg4ge4g"),
    "bank_search":   os.getenv("DISBURSE_BANK_SEARCH", "icici"),
    "bank_name":     os.getenv("DISBURSE_BANK_NAME",   "ICICI Bank"),
    "branch":        os.getenv("DISBURSE_BRANCH",      "testing"),
    "banker":        os.getenv("DISBURSE_BANKER",      "abhishek.pathak@ambak.com"),
}
