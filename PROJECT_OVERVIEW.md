# Automation Saathi — Project Overview

---

## What is this project?

**Automation Saathi** is a production-grade browser automation testing framework for the **Saathi lead management platform** ([pre-saathi.ambak.com](https://pre-saathi.ambak.com)) — a loan management SaaS application used by Ambak's sales and operations teams.

The framework opens a real Chromium browser, logs in, fills forms, clicks buttons, navigates through workflows, and verifies that the platform behaves correctly at every step. If anything is broken, it reports exactly what failed, captures a screenshot as proof, and records browser console errors — all without a human touching the keyboard.

---

## What problem does it solve?

Before this project, validating the Saathi platform meant someone had to manually:

- Log in with OTP every session
- Create a new lead with test data
- Move it through each stage (Login → Sanction → Disburse)
- Check that every required field showed the right error when left empty
- Repeat the same clicks across 20+ different flows

This was repetitive, time-consuming, and easy to miss. A single deployment could silently break a form and no one would know until a customer reported it.

**With Automation Saathi, all 267 test cases run automatically — no manual effort required.**

---

## Technology Stack

| Tool | Purpose |
|---|---|
| **Python 3.10+** | Core programming language |
| **Playwright** | Browser automation — controls real Chromium |
| **pytest** | Test runner, assertions, fixtures, CLI options |
| **Allure** | Rich visual test reports with history and timelines |
| **openpyxl** | Excel report generation |
| **python-dotenv** | Environment configuration via `.env` files |
| **pytest-rerunfailures** | Auto-retry flaky tests (2 retries, 3s delay) |
| **pytest-playwright** | Playwright integration plugin for pytest |

---

## Project Structure

```
Automation Saathi/
├── config/
│   ├── config.py                       # All URLs, credentials, test data loaded from .env
│   ├── constants.py                    # Expected UI message strings for assertions
│   └── __init__.py
│
├── pages/                              # Page Object Model — 29 page classes + BasePage
│   ├── base_page.py                    # Shared navigation, timeouts, react-select helpers
│   ├── login_page.py                   # Login form interactions
│   ├── home_page.py                    # Home page, tab navigation, lead search
│   ├── create_lead_page.py             # Create Lead form (Self-fulfilled + Refer to Ambak)
│   ├── lead_detail_page.py             # Lead detail view, stage transition buttons, edit wizard, reopen
│   ├── move_to_login_page.py           # Move to Login stage form
│   ├── move_to_sanction_page.py        # Move to Sanction stage form
│   ├── move_to_disburse_page.py        # Move to Disburse stage form
│   ├── mark_as_lost_page.py            # Mark as Lost form
│   ├── add_teammate_page.py            # Add Team Member and Sourcing Partner forms
│   ├── search_filter_page.py           # Lead search filter interactions
│   ├── team_filter_page.py             # My Team filter interactions
│   ├── team_partners_page.py           # Business Partner / Channel Partner tabs
│   ├── schedule_followup_page.py       # Schedule Follow-up form
│   ├── documents_page.py               # Document management + Recommended Docs form
│   ├── advanced_filters_page.py        # Advanced filters UI (14 dropdowns)
│   ├── edit_columns_page.py            # Edit Columns panel + pagination
│   ├── check_offers_page.py            # Check Offers / Loan Offer Calculator flow
│   ├── payout_calculator_page.py       # Payout Calculator tool
│   ├── raise_query_page.py             # Raise Query / Support ticket form
│   ├── add_role_page.py                # Add Role form
│   ├── reports_page.py                 # Reports page navigation + advanced filters
│   ├── reassign_leads_page.py          # Reassign Leads functionality
│   ├── profile_page.py                 # Partner profile view/tabs, logout
│   ├── my_earnings_page.py             # My Earnings tabs and search
│   ├── help_support_page.py            # Help & Support FAQs/Tickets
│   ├── cibil_page.py                   # Check CIBIL Score tool
│   ├── abb_calculator_page.py          # ABB Calculator tool
│   ├── apf_search_page.py              # APF Finder tool
│   ├── website_settings_page.py        # Website Settings CMS
│   └── __init__.py
│
├── tests/                              # 29 test modules — 267 total test cases
│   ├── test_01_login.py                # 4 tests
│   ├── test_02_create_lead.py          # 22 tests (Self-fulfilled)
│   ├── test_02b_create_lead_refer.py   # 10 tests (Refer to Ambak)
│   ├── test_03_move_to_login.py        # 13 tests
│   ├── test_04_move_to_sanction.py     # 12 tests
│   ├── test_05_move_to_disburse.py     # 11 tests
│   ├── test_06_check_offers.py         # 2 tests   ┐ lead lifecycle
│   ├── test_07_reassign_leads.py       # 4 tests   │ (uses the created
│   ├── test_08_recommended_docs.py     # 1 test    │  lead in sequence)
│   ├── test_09_mark_as_lost.py         # 5 tests   ┘ last lead op (terminal)
│   ├── test_09b_lead_detail.py         # 16 tests (Details/Docs/History/Remarks/Reopen/edge cases; runs after mark-as-lost)
│   ├── test_10_add_teammate.py         # 27 tests (incl. 18+4 shared mobile edge-case matrix)
│   ├── test_11_add_sourcing_partner.py # 26 tests (incl. the same shared mobile edge-case matrix)
│   ├── test_11b_team_partners.py       # 10 tests (Business Partner add + Channel Partner tab)
│   ├── test_12_search_filter.py        # 6 tests
│   ├── test_13_team_filter.py          # 2 tests
│   ├── test_14_payout_calculator.py    # 8 tests
│   ├── test_15_raise_query.py          # 4 tests
│   ├── test_16_add_role.py             # 5 tests
│   ├── test_17_edit_columns_advanced_filters.py  # 22 tests (dropdowns + apply, edit-columns, bulk actions)
│   ├── test_18_reports_advanced_filters.py       # 9 tests (filters + dashboard)
│   ├── test_19_my_earnings.py          # 6 tests
│   ├── test_20_help_support.py         # 4 tests
│   ├── test_20b_profile.py             # 6 tests (partner profile view/tabs)
│   ├── test_21_cibil.py                # 11 tests (Check CIBIL Score tool)
│   ├── test_22_abb_calculator.py       # 5 tests (ABB Calculator tool)
│   ├── test_23_apf_search.py           # 5 tests (APF Finder tool)
│   ├── test_24_website_settings.py     # 10 tests (Website Settings CMS)
│   ├── test_25_logout.py               # 1 test (logout — runs last)
│   └── __init__.py
│
├── utils/
│   ├── data_helper.py                  # Random data generators
│   └── healing_locator.py              # HealingLocator wrapper + heal log
│
├── reporters/
│   ├── log_reporter.py                 # HTML log report + browser console capture
│   ├── excel_reporter.py               # Excel report generation
│   ├── bdd_reporter.py                 # BDD-style HTML summary
│   ├── allure_reporter.py              # Single-file Allure report
│   └── email_reporter.py               # Report emailing — subject/body render inline, reports.zip
│                                        #   + Excel attached; sent automatically after every run
│                                        #   whenever REPORT_EMAIL_TO is set, unless --no-email is
│                                        #   passed (see README "Email Report")
│
├── conftest.py                         # Fixtures, session management, CLI options
├── pytest.ini                          # pytest config (retry, allure, markers: e2e, known_bug)
├── requirements.txt                    # Python dependencies
├── Makefile                            # Setup, whole-suite runs, utilities; includes make/*.mk
├── make/                                # 230+ shortcut commands, split by feature domain
│   ├── pipeline.mk                     #   Login → create lead → move to login/sanction/disburse
│   ├── leads.mk                        #   Leads list: filters, columns, reassign, lead detail
│   ├── team.mk                         #   Add teammate/sourcing partner/role, team partners
│   ├── tools.mk                        #   Payout/CIBIL/ABB/APF/offers calculators, earnings, help
│   ├── account.mk                      #   Profile, website settings, raise a query, logout
│   ├── reports.mk                      #   Allure/Excel/HTML report targets, email, check-targets
│   └── help.mk                         #   Self-generated `make help` menu
├── .env.example                        # Template for environment configuration
├── .env                                # Live environment values (gitignored)
└── auth_state.json                     # Saved login session (auto-created)
```

---

## What Does It Test? — Full Coverage

### 1. Login (4 tests)
- Login page renders correctly; OTP submit blocked without a mobile number
- Wrong OTP is rejected, then the correct one logs in and redirects to `/saathi-leads`
- **Known bug (`xfail`):** direct navigation to a protected route without a session should redirect to `/login`, but the SPA shell renders in place

### 2. Create Lead — Self-fulfilled (22 tests)
- Form opens from the home page; each required field (First Name, Last Name, Mobile, Loan Type, Employment Type, Loan Amount, State, City) blocks submission when empty
- Lead created successfully with valid data; duplicate mobile shows the warning popup
- Invalid mobile formats (4 parametrized cases) rejected; XSS in Remarks is rendered safely; whitespace-only First Name blocked
- **Known bugs (`xfail`, 5):** `+91` prefix mishandled, no double-click debounce on Submit, non-numeric Loan Amount still submits, negative Loan Amount accepted, no length cap on First Name

### 2b. Create Lead — Refer to Ambak (10 tests)
- Same validation coverage for the Refer to Ambak variant, plus successful creation and duplicate-mobile popup

### 3. Move to Login Stage (13 tests)
- Each required field blocks submission when empty: Loan Amount, Bank, Login ID, Date, Branch, Banker
- Schedule Follow-up validation (date/time/comment) and successful scheduling from this stage
- Lead moves to Login stage successfully, confirmed present in the Logged In tab
- **Known bug (`xfail`):** back/forward navigation discards an entered Loan Amount

### 4. Move to Sanction Stage (12 tests)
- Each required field blocks submission when empty: Loan Amount, Sanction ID, Date; non-numeric Sanction Amount is rejected
- Dates before the login date are disabled in the sanction date picker
- Schedule Follow-up validation and successful scheduling from this stage
- Lead moves to Sanction stage successfully, confirmed present in the Sanctioned tab
- An already-sanctioned lead no longer exposes "Move To Sanction" (offers "Move To Disburse" instead)

### 5. Move to Disburse Stage (11 tests)
- Each required field blocks submission when empty: Loan Amount, Disbursed ID, Disbursal Date
- Disbursed amount cannot exceed the sanctioned amount; dates before the sanction date are disabled
- Schedule Follow-up validation and successful scheduling from this stage
- Lead moves to Disburse stage successfully

### 6. Check Offers (2 tests)
- Loan Offer Calculator opens; the full flow completes and shows offer results

### 7. Reassign Leads (4 tests)
- Search with empty text; Assign Lead disabled until both a lead and an assignee are selected
- Lead reassigned to a selected team member successfully

### 8. Recommended Documents (1 test)
- Recommended documents are retrieved and displayed correctly for a lead

### 9. Mark as Lost (5 tests)
- Submitting without a reason/comment shows the correct error; lead marked lost successfully with reason + comment
- Mark lost → reopen → mark lost again all succeed on a dedicated self-seeded lead (state is freely reversible)
- A 5000-character comment does not block the mark-lost submit

### 9b. Lead Detail (16 tests)
- Details tab shows Loan/Customer/Income/Property cards; edit wizard opens and saves; History tab shows the activity timeline
- Remarks modal: validation and successful add; Documents tab shows the upload control and accepts a PDF
- Lost lead shows Reopen; reopen validation and successful reopen
- Rapid tab switching + back/forward leaves the page intact; an unsaved edit-wizard field is discarded on navigate-away
- Documents tab renders even with no file inputs yet; a file type outside `accept="image/*,.pdf"` forced past the input is not reported as a successful upload

### 10. Add Team Member (27 tests)
- Each required field (Full Name, Mobile, Designation) blocks submission when empty; successful add; duplicate mobile rejected
- Shared mobile edge-case matrix (also used by Add Sourcing Partner): 18 invalid formats rejected, 4 valid boundary values accepted

### 11. Add Sourcing Partner (26 tests)
- Each required field (Full Name, Mobile, Email) blocks submission when empty; successful add
- Same shared mobile edge-case matrix as Add Team Member

### 11b. Team / Business / Channel Partners (10 tests)
- Add-role picker offers Team Member / Sourcing Partner / Business Partner; Business Partner form fields and submit-enable logic; PAN disables submit
- Channel Partner tab loads and its "add" reuses the Sourcing Partner flow; search is safe against SQL-injection-like input, script tags, emoji, and no-match queries

### 12. Lead Search Filters (6 tests)
- Filter by date/city/bank; zero-result search shows a real `(0)` badge
- **Known bugs (`xfail`, 2):** a quote-containing query breaks the search box; a quote-containing zero-result query shows a blank count instead of `(0)`

### 13. My Team Filters (2 tests)
- Date range and city filters load a filtered team list

### 14. Payout Calculator (8 tests)
- Required-field validation (Loan Amount, Product Type, Fulfilment Type); successful calculation; zero-amount and whole-number scaling checks
- **Known bugs (`xfail`, 2):** a decimal-suffixed loan amount inflates the payout percentage; a negative amount is silently accepted

### 15. Raise Query (4 tests)
- Required-field validation (issue type, description); successful submission; rapid double-submit is debounced

### 16. Add Role (5 tests)
- Required-field validation (name, description); successful creation
- **Known bugs (`xfail`, 2):** duplicate role names are not rejected; a role with zero permissions is not rejected

### 17. Edit Columns and Advanced Filters (22 tests)
- Edit Columns panel opens, hides/restores columns, "Set Default"
- All 14 Advanced Filters dropdowns open; Source filter apply/clear changes results
- Bulk Actions menu lists Reassign Leads / Bulk Import / Export Leads (menu labels only — no functional test yet)
- **Known bug (`xfail`):** the pagination control's last page can render empty despite a non-zero leads total

### 18. Reports — Advanced Filters (9 tests)
- 7 advanced-filter dropdowns open (field labels behind `filter_1`–`filter_5` are still placeholders — see `pages/reports_page.py`); dashboard loads; "More Reports" shows "Coming Soon"

### 19. My Earnings (6 tests)
- Page loads; tab switching across Earned/Paid/Projected; search by Lead ID; reset filter

### 20. Help & Support (4 tests)
- Page loads; FAQs tab lists questions and the accordion toggles; Tickets tab loads

### 20b. Profile (6 tests)
- Page loads; Basic Details fields render; profile tabs present; KYC Documents tab opens; SPOC Name is safe against XSS
- **Known bug (`xfail`):** Pin Code accepts non-numeric input verbatim instead of validating it

### 21. Check CIBIL Score (11 tests)
- PAN fetch validation and success; personal-details form validation (name, email, mobile, DOB); DOB picker; full form advances to the fulfilment step

### 22. ABB Calculator (5 tests)
- Tool opens with intro/instructions; file input is PDF-only; accepts a PDF selection (no statement parsing/result assertion yet)

### 23. APF Search (5 tests)
- Page loads; results table headers render; city dropdown and selection; no-match search shows an empty state

### 24. Website Settings (10 tests)
- Page loads; every section has a Save button; Header/Hero/Testimonials/Calculator/FAQ sections save successfully; hero heading edit-and-save; add a feature row / FAQ block
- 4 of 9 `WebsiteSettings.SECTIONS` still lack a save test: Hero Sub-section, Services Section, About Us, Lead Creation Journey

### 25. Logout (1 test)
- Logout redirects to the login page

---

**Total: 267 automated test cases across 29 modules.** 15 of them are `@pytest.mark.known_bug` + `xfail(strict=True)` — they assert the *correct* behaviour for a documented app defect, so a run stays green while the bug exists and a fix surfaces immediately as an `XPASS` failure (prompting the test to be un-xfailed) rather than silently passing.

---

## Features

| Feature | Description |
|---|---|
| **Session persistence** | Logs in once, saves the session to `auth_state.json`. All 267 tests reuse it — no repeated OTPs between tests or across runs |
| **Intelligent lead ID chaining** | The lead created in test_02 is automatically captured and passed to all downstream stage tests. No manual `.env` edits needed between stages |
| **Chained loan amounts** | The login amount flows to sanction, and the sanction amount flows to disburse — all three stay in sync automatically |
| **Dynamic test data generation** | Each run generates fresh random first/last names, mobile numbers, transaction IDs, and email addresses — so no two runs use the same data |
| **Flexible input via `.env`** | Every piece of test data — credentials, lead fields, loan amounts, transaction IDs, filter values — can be overridden by setting the corresponding variable in `.env`. No code changes required to test with different data |
| **Filled and empty form coverage for Sanction and Disburse** | Both the Sanction and Disburse stage forms are tested twice: once with all fields correctly filled (happy path) and once with each required field deliberately left empty. Every blank-field error message is validated individually before the success path is confirmed |
| **Toast and modal validation** | Every error scenario checks that the exact expected message appears — not just that the form was blocked silently |
| **Centralised message constants** | All expected toast messages, modal text, and validation error strings are defined as named constants in `config/constants.py`. Tests import constants by name rather than using raw strings, so when the UI text changes only one file needs updating |
| **Negative tests before positive** | Every flow tests all empty-field and invalid-input scenarios before the happy path. Validations are confirmed working before the full flow is confirmed |
| **Stable, label-based selectors** | Form fields are found by their visible labels ("Loan Type", "State") rather than internal IDs that change when the frontend is rebuilt |
| **Real browser testing** | Tests execute in actual Chromium, exactly as a user would interact. No mocked DOM, no jsdom — real network requests, real rendering |
| **Auto-retry on failure** | pytest-rerunfailures retries any failing test up to 2 times with a 3-second delay before marking it as a final failure |
| **Browser console capture** | JavaScript errors and warnings from the browser console are captured per test and attached to the Allure report — surfaces client-side issues invisible in the UI |
| **Three auto-generated reports** | HTML log report, Excel spreadsheet, and Allure visual dashboard are produced automatically after every run |
| **Headless mode** | `make headless` or `HEADLESS=true` runs all tests without a visible browser window — suitable for CI/CD pipelines |
| **Environment switching** | Change one line in `.env` (`BASE_URL`) to point the entire suite at staging or production — no code changes needed |
| **Makefile with 230+ commands** | Every test, report, and utility operation is wrapped in a named `make` target, split across `Makefile` + `make/*.mk` by feature domain. Run a full suite, a single feature area, one specific test, a headless run, or open any of the three reports — all with short memorable commands. Run `make help` to see the full list |
| **Run any test individually** | Every single test case has its own `make` target (e.g. `make create-lead-duplicate`, `make move-to-sanction-success`, `make payout-calculator-calculate`). Any test can be isolated and re-run without touching surrounding tests |
| **Manual lead ID override** | Pass `--lead-id`, `--sanction-lead-id`, or `--disburse-lead-id` on the CLI to target any specific lead, bypassing the auto-chaining |
| **Follow-up scheduling coverage** | Schedule Follow-up is tested from within Login, Sanction, and Disburse stage flows — not just independently |

---

## How to Run It

### Setup (one time)
```bash
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # then fill in your credentials
```

### Run all 267 tests
```bash
make all
```

### Run by feature area
```bash
make login                    # Authentication tests
make create-lead              # Self-fulfilled create lead
make create-lead-refer        # Refer to Ambak create lead
make move-to-login            # Move to Login stage
make move-to-sanction         # Move to Sanction stage
make move-to-disburse         # Move to Disburse stage
make mark-as-lost             # Mark as Lost
make add-teammate             # Add Team Member
make add-sourcing-partner     # Add Sourcing Partner
make search-filter            # Lead search filters
make team-filter              # My Team filters
make check-offers             # Check Offers flow
make payout-calculator        # Payout Calculator
make raise-query              # Raise Query
make add-role                 # Add Role
make advanced-filters         # Edit Columns + Advanced Filters
make reassign-leads           # Reassign Leads
make reports                  # Reports page filters
make recommended-docs         # Recommended Documents
```

### Run a specific test
```bash
make login-success
make create-lead-success
make create-lead-duplicate
make mark-as-lost-success
make add-teammate-success
make payout-calculator-success
```

### Run with a specific lead ID
```bash
make move-to-login-id ID=162981
make move-to-sanction-id ID=162966
make move-to-disburse-id ID=115653
```

### Headless (no visible browser window)
```bash
make headless
```

### Reset login session (force fresh OTP)
```bash
make reset-session
```

### View reports
```bash
make open-log-report          # HTML report in browser
make open-excel-report        # Excel spreadsheet
make open-report              # Allure visual dashboard
make open-reports             # All reports at once
```

Run `make help` to see every available target.

---

## Reports

Three reports are auto-generated after every run:

### Log Report — `log-report.html`
An HTML page showing:
- Pass / fail status per test with colour coding
- Duration of each test
- Screenshot of the browser at the end of each test
- Captured browser console logs (errors, warnings)

### Excel Report — `test-report.xlsx`
A spreadsheet with two sheets:
- **Summary** — total count, pass rate, run start/end time, total duration
- **Results** — one row per test with name, status, duration, and error message if failed

### Allure Report — `allure-results/`
A rich visual dashboard showing:
- Test history and trend over multiple runs
- Timeline of test execution
- Step-by-step drill-down into each test (via `@allure.step` decorators)
- Attachments: screenshots, console logs
- Categorised failures (product defect, test defect, broken)

---

## Configuration

Everything lives in `.env` and is loaded into `config/config.py`:

| Variable | Purpose |
|---|---|
| `BASE_URL` | Application URL (e.g. `https://pre-saathi.ambak.com/`) |
| `LOGIN_MOBILE` | Mobile number for login |
| `LOGIN_OTP` | OTP for login |
| `BROWSER` | Browser engine — default `chromium` |
| `HEADLESS` | `true` / `false` — whether to show the browser window |
| `TIMEOUT` | Element interaction timeout in ms — default `45000` |
| `NAV_TIMEOUT` | Page navigation timeout in ms — default `60000` |
| `LEAD_*` | Lead creation fields (name, mobile, loan type, state, city) |
| `MOVE_TO_LOGIN_*` | Login stage fields (amount, bank, login ID, date, city, branch, banker) |
| `MOVE_TO_SANCTION_*` | Sanction stage fields (amount, sanction ID, date) |
| `MOVE_TO_DISBURSE_*` | Disburse stage fields (amount, disbursed ID, date) |
| `MARK_AS_LOST_*` | Lost fields (lead ID, reason, comment) |
| `ADD_TEAMMATE_*` | Teammate fields (name, mobile, designation) |
| `ADD_SOURCING_PARTNER_*` | Sourcing partner fields (name, mobile, email) |
| `SEARCH_FILTER_*` | Filter values (date preset, city, bank) |
| `TEAM_FILTER_*` | Team filter values (date range, city) |

---

## Architecture and Design

### Page Object Model (POM)
Each page or form in the application has a dedicated Python class in `pages/`. The class owns:
- All element locators (found by label text or ARIA role, never by internal IDs)
- All action methods (click, fill, select, assert)
- `@allure.step()` decorators for detailed report steps

Test files import page objects and call their methods — tests never contain raw selectors.

`BasePage` provides shared utilities (navigate, wait for URL, consistent timeouts) that all page classes inherit.

### Fixture System
`conftest.py` provides all shared state and setup:

| Fixture | Purpose |
|---|---|
| `shared_state` | Session-scoped dict — passes created lead ID and amounts between test modules |
| `auth_state` | Saves login session to file on first use; reloads on subsequent tests |
| `logged_in_page` | Pre-authenticated Playwright page, ready for test use |
| `page` | Unauthenticated page — used only by login tests |
| `lead_id` | Lead ID from `shared_state` or `.env` fallback |
| `sanction_lead_id` | Lead ID for sanction tests (chained or manual) |
| `disburse_lead_id` | Lead ID for disburse tests (chained or manual) |
| `login_amount` | Loan amount captured from the Login stage test |
| `sanction_amount` | Loan amount captured from the Sanction stage test |
| `disburse_amount` | Loan amount passed through to disburse flow |

### Lead Data Flow (Full Run)
```
test_02_create_lead
  → Creates lead with random data
  → Captures lead ID → shared_state["created_lead_id"]

test_03_move_to_login
  → Reads shared_state["created_lead_id"]
  → Moves lead to Login
  → Captures login_amount → shared_state["login_amount"]

test_04_move_to_sanction
  → Reads shared_state["created_lead_id"] + ["login_amount"]
  → Moves lead to Sanction
  → Captures sanction_amount → shared_state["sanction_amount"]

test_05_move_to_disburse
  → Reads shared_state["created_lead_id"] + ["sanction_amount"]
  → Validates disbursed amount cannot exceed sanctioned amount
  → Moves lead to Disburse
```

No `.env` changes or manual intervention needed between stages in a full run.

### Data Generation (`utils/data_helper.py`)
Each run generates fresh random:
- **Mobile numbers** — valid 10-digit Indian format
- **Names** — first and last names drawn from curated lists
- **Transaction IDs** — 8-character alphanumeric strings
- **Email addresses** — generated from the random name
- **Role names** — unique names for add-role tests

### UI Constants (`config/constants.py`)
All expected toast messages, modal text, and error strings are defined as named constants rather than being hardcoded in tests. When the UI text changes, only `constants.py` needs updating.

---

## Adding a New Test Flow

1. Create `pages/new_flow_page.py` — define locators and action methods
2. Add test data variables to `config/config.py` (loaded from `.env`)
3. Create `tests/test_NN_new_flow.py` — negative tests first, positive last
4. If the flow needs a lead ID, add a CLI option and fixture in `conftest.py`
5. Add `make` targets in the matching `make/*.mk` file (or `Makefile` for a whole-suite/utility
   target), tagging the group-level target with `## description` so it shows up in `make help`

---

## What Can Be Added Next

- **CI/CD integration** — run the full suite automatically on every deployment via GitHub Actions
- **Slack alerts** — notify the team when any test fails in CI (email alerts already exist — see README "Email Report" and `reporters/email_reporter.py`)
- **Bulk Import / Export — functional coverage** — today only the Actions menu's labels are asserted; needs a real import (valid + malformed file, partial-failure rows) and export (download verification) test, plus a `pages/bulk_actions_page.py`
- **Reports — real field labels** — `pages/reports_page.py`'s `filter_1`–`filter_5` triggers are still positional placeholders (`TODO: rename once the actual field labels are known`); needs a live pass to name them and add apply-and-verify assertions like the Source filter already has
- **Advanced Filters — apply assertions for the other 13 dropdowns** — only Source currently verifies that applying it changes the leads count; the remaining 13 only assert "opens"
- **Website Settings — the remaining 4 sections** — Hero Sub-section, Services Section, About Us, and Lead Creation Journey have no save test yet
- **Lead rejection flow** — test the rejection path and confirm lead status updates
- **Partner Business Statement** — a manual test-case spreadsheet (`Partner_Business_Statement_test_cases.xlsx`) exists for this feature with no page object or tests behind it yet
- **Multi-environment matrix** — run staging and production in parallel and diff results
- **Expanded lost reason coverage** — only one lost reason is exercised end-to-end; test each available reason code individually
- **API / network-failure coverage** — no test currently intercepts the leads-list GraphQL call to simulate a 500/timeout/offline response
- **Performance timing assertions** — assert that key pages load within acceptable time thresholds
