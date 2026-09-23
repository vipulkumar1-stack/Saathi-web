# Automation Saathi — Test Framework

Playwright + pytest automation framework for [pre-saathi.ambak.com](https://pre-saathi.ambak.com).

---

## Project Structure

```
Automation Saathi/
├── config/
│   └── config.py              # URLs, credentials, test data
├── pages/
│   ├── base_page.py              # Shared page methods (navigate, wait, react-select helpers)
│   ├── login_page.py             # Login flow
│   ├── home_page.py              # Home page tabs, search, open lead
│   ├── create_lead_page.py       # Create Lead popup form (Self-fulfilled + Refer to Ambak)
│   ├── lead_detail_page.py       # Lead detail — stage transition buttons, edit wizard, reopen
│   ├── move_to_login_page.py     # Move To Login form
│   ├── move_to_sanction_page.py  # Move To Sanction form
│   ├── move_to_disburse_page.py  # Move To Disburse form
│   ├── mark_as_lost_page.py      # Mark as Lost form
│   ├── add_teammate_page.py      # Add Teammate / Sourcing Partner form
│   ├── team_partners_page.py     # Business Partner / Channel Partner tabs
│   ├── schedule_followup_page.py # Schedule Follow-up form
│   ├── documents_page.py         # Document management + Recommended Docs form
│   ├── search_filter_page.py    # Lead search filter interactions
│   ├── team_filter_page.py      # My Team filter interactions
│   ├── advanced_filters_page.py  # Advanced filters UI (14 dropdowns)
│   ├── edit_columns_page.py      # Edit Columns panel + pagination
│   ├── check_offers_page.py      # Check Offers / Loan Offer Calculator flow
│   ├── payout_calculator_page.py # Payout Calculator tool
│   ├── raise_query_page.py       # Raise Query / Support ticket form
│   ├── add_role_page.py          # Add Role form
│   ├── reports_page.py           # Reports page navigation + advanced filters
│   ├── reassign_leads_page.py    # Reassign Leads functionality
│   ├── profile_page.py           # Partner profile view/tabs, logout
│   ├── my_earnings_page.py       # My Earnings tabs and search
│   ├── help_support_page.py      # Help & Support FAQs/Tickets
│   ├── cibil_page.py             # Check CIBIL Score tool
│   ├── abb_calculator_page.py    # ABB Calculator tool
│   ├── apf_search_page.py        # APF Finder tool
│   └── website_settings_page.py  # Website Settings CMS
├── tests/
│   ├── test_01_login.py             # Login tests
│   ├── test_02_create_lead.py       # Create Lead tests
│   ├── test_03_move_to_login.py     # Move To Login tests
│   ├── test_04_move_to_sanction.py  # Move To Sanction tests
│   ├── test_05_move_to_disburse.py  # Move To Disburse tests
│   ├── test_06_check_offers.py          # Check Loan Offers tests        ┐ lead lifecycle,
│   ├── test_07_reassign_leads.py        # Reassign Leads tests           │ in sequence on
│   ├── test_08_recommended_docs.py      # Recommended Docs tests         │ the created lead
│   ├── test_09_mark_as_lost.py          # Mark as Lost (last lead op — terminal state)
│   ├── test_09b_lead_detail.py          # Lead detail: Details/Documents/History/Remarks/Reopen
│   ├── test_10_add_teammate.py          # Add Teammate (Team Member) tests
│   ├── test_11_add_sourcing_partner.py  # Add Sourcing Partner tests
│   ├── test_11b_team_partners.py        # Business Partner add + Channel Partner tab
│   ├── test_12_search_filter.py         # Lead search filter tests
│   ├── test_13_team_filter.py           # My Team filter tests
│   ├── test_14_payout_calculator.py     # Payout Calculator tests
│   ├── test_15_raise_query.py           # Raise Query tests
│   ├── test_16_add_role.py              # Add Role (Access Control) tests
│   ├── test_17_edit_columns_advanced_filters.py  # Edit Columns / Advanced Filters tests
│   ├── test_18_reports_advanced_filters.py       # Reports filter tests
│   ├── test_19_my_earnings.py           # My Earnings tests
│   ├── test_20_help_support.py          # Help & Support tests
│   ├── test_20b_profile.py              # Partner profile (view/tabs)
│   ├── test_21_cibil.py                 # Check CIBIL Score tool tests    ┐
│   ├── test_22_abb_calculator.py        # ABB Calculator tool tests       │ My Tools
│   ├── test_23_apf_search.py            # APF Finder tool tests           │ group
│   ├── test_24_website_settings.py      # Website Settings CMS tests      ┘
│   └── test_25_logout.py                # Logout (runs last)
├── utils/
│   └── data_helper.py         # Random mobile number generator
├── conftest.py                # Fixtures: browser, auth session, CLI options
├── pytest.ini                 # pytest configuration
├── Makefile                   # Setup, whole-suite runs, utilities; includes make/*.mk below
├── make/
│   ├── pipeline.mk             # Login → create lead → move to login/sanction/disburse
│   ├── leads.mk                # Leads list: filters, columns, reassign, lead detail
│   ├── team.mk                 # Add teammate/sourcing partner/role, team partners
│   ├── tools.mk                # Payout/CIBIL/ABB/APF/offers calculators, my earnings, help & support
│   ├── account.mk              # Profile, website settings, raise a query, logout
│   ├── reports.mk              # Allure/Excel/HTML report targets, email, check-targets
│   └── help.mk                 # Self-generated `make help` menu
└── requirements.txt           # Dependencies
```

---

## Setup

```bash
make install
# equivalent to:
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
```

All `make` targets use `.venv` automatically (its `bin/` is prepended to `PATH`). To run `pytest`
directly, either `source .venv/bin/activate` first or call `.venv/bin/pytest`.

`conftest.py` enforces this: `pytest` exits immediately (before collecting anything) if it detects
it isn't running from the project's `.venv`, so a stray global `pytest` never runs the suite against
the wrong dependency versions. Set `ALLOW_SYSTEM_PYTHON=1` to opt out (e.g. a CI image that installs
globally instead of into a venv).

The message identifies which of three situations caused the mismatch — another project's venv is
active, no venv is active, or this venv is active but a global `pytest` shadowed it on PATH — and
prints the matching fix, so read it rather than reaching straight for `make install`.

If a test goes silent for longer than `faulthandler_timeout` (180s, set in `pytest.ini`), pytest
dumps every thread's stack to stderr — the test's file:line plus the Playwright call underneath it —
so a real stall is diagnosable instead of showing nothing until you Ctrl+C. Tighten it for one run
with `-o faulthandler_timeout=N` (it's an ini-only setting, there's no CLI flag), e.g.
`make login-page-loads PYTEST_ADDOPTS="-o faulthandler_timeout=1"`.

---

## Running Tests

### All tests
```bash
make all
```

### By module
```bash
make login               # All login tests
make create-lead         # All create lead tests
make move-to-login       # All move-to-login tests
make move-to-sanction    # All move-to-sanction tests
make move-to-disburse    # All move-to-disburse tests
make mark-as-lost        # All mark-as-lost tests
make add-teammate              # All add-teammate tests
make add-sourcing-partner      # All add-sourcing-partner tests
make team-filter               # My Team filter tests
make search-filter             # Lead search filter tests
```

### Single test
```bash
make login-success
make create-lead-success
make create-lead-duplicate
make mark-as-lost-success
make add-teammate-success
```

### With a specific lead ID
```bash
make move-to-login-id ID=162981
make move-to-sanction-id ID=162966
make move-to-disburse-id ID=115653
```

### Headless mode (no browser window)
```bash
make headless
```

---

## HTML Report

Every test run automatically generates `report.html` in the project root.  
Open it in a browser after any run:

```bash
xdg-open report.html
```

---

## Email Report

Every run — a single test, one feature file, or the full suite — can email the
report to a distribution list. Nothing is sent unless `REPORT_EMAIL_TO` is
configured; configuring it *is* the opt-in.

**Setup** — add to `.env` (see `.env.example`):

```dotenv
REPORT_EMAIL_TO=you@example.com,teammate@example.com   # comma-separated
REPORT_EMAIL_USER=your.account@gmail.com
REPORT_EMAIL_PASSWORD=xxxxxxxxxxxxxxxx                 # 16-char Google App Password
```

`REPORT_EMAIL_PASSWORD` must be a **Google App Password**
(https://myaccount.google.com/apppasswords), not your normal Gmail login password —
Gmail rejects the real password over SMTP. Optional overrides:
`REPORT_EMAIL_FROM` (defaults to `REPORT_EMAIL_USER`), `REPORT_EMAIL_HOST`
(default `smtp.gmail.com`), `REPORT_EMAIL_PORT` (default `587`).

Validate the config any time — checks the env vars and logs in over SMTP, sends
no mail:

```bash
make check-email
```

**Sends automatically** — once `REPORT_EMAIL_TO` is set, every run emails the
report, no prompt. `--no-email` is the only opt-out:

```bash
pytest --no-email    # never send, this run only
make report-email    # = full suite + explicit send, for cron/an unattended overnight run
```

Every attempt — sent, declined, unconfigured, or a send failure — is printed to
the console and appended to `email-report.log`, so a run that didn't email
always leaves a reason on disk (`tail email-report.log` to check).

**What arrives** — the report contents render directly in the email body (pass/fail
counts, pass rate, a callout of every failed test with its repro steps and the
`make <target>` to rerun it, a separate callout for any known-bug test that
unexpectedly passed (XPASS — the app bug may be fixed), then the full
per-feature breakdown), so nothing needs opening just to see the result.
Attached is `reports.zip` (`test-summary.html` — plain-English summary;
`log-report.html` — browser console logs + failure screenshots;
`allure-report.html` — full Allure detail; zipped because mail clients
preview a raw `.html` attachment as source, not the rendered page) plus
`test-report.xlsx` directly. If the zip would exceed ~20 MB, the largest report
(normally Allure) is dropped from the email and noted in the body — it's still
saved locally.

The subject line names what ran, e.g.
`Saathi Automation Report — make cibil — 11/11 passed, 0 failed`, so a
single-test email and a full-suite email are distinguishable in an inbox. It
also calls out `N xfail` (known bugs, expected) and `N XPASS (bug fixed?)`
(known bugs that unexpectedly passed) when either is present.

---

## Session Management

The framework logs in once and saves the session to `auth_state.json`. All subsequent tests load from this file — no repeated logins or OTP waits.

```bash
make reset-session   # Delete auth_state.json to force a fresh login
```

---

## Test Coverage

219 → 267 tests as of the 2026-08-20 coverage audit (see `PROJECT_OVERVIEW.md` → "What Does It Test? — Full Coverage" for the complete per-test breakdown across all 29 modules). Highlights below; counts are current as of the same audit, except test_02/test_02b (updated 2026-09-09 for the Add New Lead modal redesign — see the note under that heading) — 267 → 262 tests. `PROJECT_OVERVIEW.md`'s per-module numbers still reflect the 2026-08-20 audit and are due the same update.

### test_01_login (4 tests)
| Test | Description |
|---|---|
| test_login_page_loads | Login page renders correctly |
| test_submit_without_mobile | OTP screen does not appear without mobile |
| test_login_rejects_wrong_otp_then_succeeds | Wrong OTP rejected, then correct OTP redirects to /saathi-leads |
| test_direct_navigation_to_protected_page_without_session_bug | `known_bug` (xfail): protected route reachable without a session |

### test_02_create_lead (21 tests) / test_02b_lead_entry_mode (6 tests)
The "Add New Lead" modal was redesigned in 2026-09: the State field was
removed (City is now the only location field), Employment Type became
required, and a new optional Purchase Type field was added. The old "I will
do it myself" / "Refer to Ambak" tabs are gone too — the modal now always
creates an `ambak`-type lead (a fixed banner says so) and instead offers a
choice between filling the form manually and bulk-uploading a CSV. The
retired `test_02b_create_lead_refer.py` (which mirrored test_02 for the old
Refer to Ambak tab) is replaced by `test_02b_lead_entry_mode.py`, which
covers the Add Manually / Bulk Upload choice and Purchase Type instead.

| Test | Description |
|---|---|
| test_create_lead_form_opens | Create Lead popup opens |
| test_submit_without_first_name / _last_name / _mobile / _loan_type / _employment_type / _loan_amount / _city | Form blocked — each required field empty |
| test_create_lead_successful | Lead created — success popup appears |
| test_duplicate_mobile_shows_popup | Duplicate mobile warning popup appears |
| test_invalid_mobile_formats_rejected | 4 parametrized malformed mobile cases rejected |
| test_xss_script_tag_in_remarks_is_safe | Script tag in Remarks renders safely, no injection |
| test_whitespace_only_first_name_blocked | Whitespace-only First Name blocked |
| test_mobile_country_code_prefix_bug, test_double_click_submit_lacks_debounce, test_invalid_loan_amount_text_still_submits_bug, test_negative_loan_amount_rejected_bug, test_extremely_long_name_rejected_or_truncated_bug | `known_bug` (xfail), 5 documented defects |

| test_02b_lead_entry_mode | Description |
|---|---|
| test_add_manually_selected_by_default | Add Manually is the default entry mode |
| test_lead_type_banner_shows_ambak | Fixed "...type ambak" banner renders |
| test_bulk_upload_switches_form | Bulk Upload swaps in the file-upload panel |
| test_switch_back_to_add_manually_restores_form | Switching back restores the manual fields |
| test_purchase_type_is_optional | Lead created successfully with Purchase Type unset |
| test_purchase_type_selectable | Selecting a Purchase Type option doesn't block submission |

### test_03_move_to_login (13 tests)
| Test | Description |
|---|---|
| test_move_to_login_without_loan_amount / _bank / _login_id / _date / _branch / _banker | Form blocked — each required field empty |
| test_followup_without_date / _time / _comment | Schedule Follow-up validation |
| test_followup_scheduled_successfully | Follow-up scheduled from Login stage |
| test_move_lead_to_login | Lead moved to Login — confirmed present in Logged In tab |
| test_back_forward_discards_entered_data_bug | `known_bug` (xfail): back/forward discards a typed Loan Amount |

### test_04_move_to_sanction (12 tests)
| Test | Description |
|---|---|
| test_move_to_sanction_without_loan_amount / _sanction_id / _date | Form blocked — each required field empty |
| test_sanction_non_numeric_amount_rejected | Non-numeric Sanction Amount does not submit |
| test_sanction_dates_before_login_are_disabled | Dates before login date disabled in the sanction date picker |
| test_followup_* / test_move_lead_to_sanction | Follow-up validation/scheduling; lead moved to Sanction |
| test_sanction_button_gone_after_already_sanctioned | An already-sanctioned lead no longer offers "Move To Sanction" |

### test_05_move_to_disburse (11 tests)
| Test | Description |
|---|---|
| test_move_to_disburse_without_loan_amount / _disbursed_id / _disbursal_date | Form blocked — each required field empty |
| test_move_to_disburse_amount_exceeds_sanction | Form blocked — Amount exceeds sanctioned amount |
| test_disbursal_dates_before_sanction_are_disabled | Dates before sanction date disabled in the disbursal date picker |
| test_followup_* / test_move_lead_to_disburse | Follow-up validation/scheduling; lead moved to Disburse |

### test_09_mark_as_lost (5 tests) / test_09b_lead_detail (16 tests)
| Test | Description |
|---|---|
| test_mark_as_lost_without_reason / _without_comment | Required-field validation |
| test_mark_lead_as_lost | Lead marked lost — "Lead updated successfully." toast |
| test_mark_lost_then_reopen_then_mark_lost_again | Lost/reopen/lost cycle all succeed on a dedicated self-seeded lead |
| test_mark_lost_long_comment_accepted | A 5000-character comment does not block the submit |
| test_details_tab_shows_cards / test_edit_wizard_opens / test_edit_loan_details_saves | Details tab + edit wizard |
| test_history_tab_shows_timeline | History tab lists timeline entries |
| test_remarks_modal_opens / test_remark_without_text_shows_error / test_add_remark_successfully | Remarks validation + success |
| test_documents_tab_shows_upload / test_document_upload_accepts_pdf | Documents tab + PDF upload |
| test_lost_lead_shows_reopen / test_reopen_without_remarks_shows_error / test_reopen_lead_successfully | Reopen flow |
| test_rapid_tab_switch_and_back_forward / test_edit_field_discarded_when_navigating_away_without_saving / test_documents_tab_loads_without_recommended_docs / test_invalid_file_type_upload_not_reported_success | Edge-case probes (revived from the former `_scratch_explore.py`) |

### test_10_add_teammate (27 tests) / test_11_add_sourcing_partner (26 tests)
| Test | Description |
|---|---|
| test_submit_without_full_name / _mobile / _designation (or _email for Sourcing Partner) | Form blocked — each required field empty |
| test_add_teammate_successful / test_add_sourcing_partner_successful | Successful add |
| test_duplicate_teammate_mobile_rejected | Duplicate mobile rejected |
| test_invalid_mobile_formats_rejected | 18-value shared `INVALID_MOBILES` matrix rejected (both forms) |
| test_valid_mobile_boundaries_accepted | 4-value shared `VALID_MOBILE_BOUNDARIES` matrix accepted (both forms) |

### test_11b_team_partners (10 tests)
| Test | Description |
|---|---|
| test_add_picker_offers_roles | Add-role picker offers Team Member / Sourcing Partner / Business Partner |
| test_business_partner_form_fields / _submit_enabled_when_filled / _pan_disables_submit | Business Partner form behaviour |
| test_channel_partner_tab_loads / _add_is_sourcing_partner | Channel Partner tab and its add flow |
| test_search_handles_special_characters_safely | 4 parametrized cases: SQL-injection-like text, script tag, emoji, no-match |

### test_12_search_filter (6 tests)
| Test | Description |
|---|---|
| test_filter_by_date / _city / _bank | Apply each filter — results page loads |
| test_zero_result_search_shows_zero_badge | Zero-result search shows a real `(0)` badge |
| test_search_box_survives_quote_containing_query_bug, test_quote_query_shows_zero_badge_not_blank_bug | `known_bug` (xfail), 2 documented defects |

### test_13_team_filter (2 tests)
| Test | Description |
|---|---|
| test_filter_by_date | Apply date range filter on My Team — filtered list loads |
| test_filter_by_city | Apply city filter on My Team — filtered list loads |

### test_14_payout_calculator (8 tests)
| Test | Description |
|---|---|
| test_payout_calculator_without_loan_amount / _product_type / _fulfilment_type | Required-field validation |
| test_payout_calculates_successfully / test_zero_amount_calculates_cleanly / test_whole_number_math_scales_proportionally | Successful calculation cases |
| test_decimal_loan_amount_inflates_payout_bug, test_negative_loan_amount_rejected_bug | `known_bug` (xfail), 2 documented defects |

### test_16_add_role (5 tests)
| Test | Description |
|---|---|
| test_add_role_without_name / _without_description | Required-field validation |
| test_add_role_successfully | New role created |
| test_duplicate_role_name_rejected_bug, test_role_with_no_permissions_rejected_bug | `known_bug` (xfail), 2 documented defects |

### test_17_edit_columns_advanced_filters (22 tests) / test_18_reports_advanced_filters (9 tests)
| Test | Description |
|---|---|
| test_edit_columns_panel_opens / hide-and-restore / set-default | Edit Columns panel behaviour |
| 14 `test_*_dropdown_opens` tests | Every Advanced Filters dropdown opens |
| test_apply_source_filter_changes_results / test_clear_all_resets_source | Source filter apply/clear verified against real results |
| test_actions_menu_options | Bulk Actions menu lists Reassign / Bulk Import / Export Leads (labels only) |
| test_pagination_last_page_matches_total_bug | `known_bug` (xfail) |
| test_reports_dashboard_loads / test_more_reports_coming_soon | Reports dashboard |
| 7 Reports `test_*_dropdown_opens` tests | Reports advanced filters (field labels still placeholders — see `pages/reports_page.py`) |

### test_19_my_earnings (6) / test_20_help_support (4) / test_20b_profile (6)
| Test | Description |
|---|---|
| test_earnings_page_loads / test_tab_switching / test_search_by_lead_id / test_reset_filter | My Earnings |
| test_help_page_loads / test_faqs_tab_lists_questions / test_faq_accordion_toggles / test_tickets_tab_loads | Help & Support |
| test_profile_page_loads / test_basic_details_fields / test_profile_tabs_present / test_kyc_documents_tab_opens / test_spoc_name_xss_is_safe | Profile |
| test_pincode_rejects_non_numeric_bug | `known_bug` (xfail) |

### test_21_cibil (11) / test_22_abb_calculator (5) / test_23_apf_search (5) / test_24_website_settings (10) / test_25_logout (1)
See `PROJECT_OVERVIEW.md` for the full per-test list — CIBIL PAN fetch + form validation, ABB PDF-only upload, APF city search, Website Settings section saves (5 of 9 sections covered), and logout redirect.

---

## Configuration

All test data lives in `config/config.py`:

| Variable | Purpose |
|---|---|
| `BASE_URL` | Application URL |
| `LOGIN_MOBILE` | Login mobile number |
| `LOGIN_OTP` | Login OTP |
| `LEAD_DATA` | Base data for create lead form |
| `MOVE_TO_LOGIN_DATA` | Data for move-to-login form |
| `MOVE_TO_SANCTION_DATA` | Data for move-to-sanction form |
| `MOVE_TO_DISBURSE_DATA` | Data for move-to-disburse form |
| `MARK_AS_LOST_DATA` | Data for mark-as-lost form (lead ID, reason, comment) |
| `ADD_TEAMMATE_DATA` | Base data for add-teammate form (full name, mobile) |
| `ADD_SOURCING_PARTNER_DATA` | Base data for add-sourcing-partner form (full name, mobile, email) |
| `TEAM_FILTER_DATA` | Filter values for My Team date range and city filter tests |
| `SEARCH_FILTER_DATA` | Filter values for lead date, city, and bank filter tests |

---

## Adding a New Flow

1. Create `pages/new_flow_page.py` — add locators and methods
2. Add test data to `config/config.py`
3. Create `tests/test_0N_new_flow.py` — negative tests first, positive last
4. Add a `--new-lead-id` CLI option + fixture in `conftest.py`
5. Add `make` targets in the matching `make/*.mk` file (or `Makefile` for a whole-suite/utility
   target), tagging the group-level target with `## description` so it shows up in `make help`
# Saathi-web
