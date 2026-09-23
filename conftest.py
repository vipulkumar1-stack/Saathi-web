import os
import sys
import base64
import random
import shutil
import traceback
import pytest
from datetime import datetime
from pathlib import Path

# Fail fast when pytest isn't running from the project .venv. A bare `pytest`
# (rather than `make ...` or an activated .venv) silently picks up whatever's
# on PATH — a materially different set of pytest/playwright/allure versions,
# possibly a different installed Chromium build, or (as with a neighbouring
# project's venv) no playwright at all — and either produces results from an
# environment nobody intended to test with, or dies below with a raw
# ImportError instead of this message. Checked here, above the imports that
# would otherwise be the first thing to fail.
#
# A plain sys.exit(), not pytest.exit(): raising pytest.exit()'s Exit
# exception THIS early — during conftest's own module import, before pytest's
# session has started — gets caught by pytest's conftest loader and re-reported
# as "ImportError while loading conftest", with exit code 4 (usage error)
# instead of the 3 below, burying this message under a confusing traceback.
# sys.exit() during conftest import propagates cleanly with the code given.
# ALLOW_SYSTEM_PYTHON=1 opts out, for CI images that install globally.
#
# The mismatch has three distinct causes, each with a different fix, so the
# message below is branched rather than generic:
#   1. Another project's venv is active in this shell (e.g. `pytest` run here
#      right after working in a sibling repo) — fix is `deactivate` then
#      activate this one.
#   2. No venv is active at all — fix is to activate this one.
#   3. This project's venv IS active (VIRTUAL_ENV points at it) but a pytest
#      binary from outside it won the PATH lookup anyway (stale shell hash,
#      or a global install ahead on PATH) — "activate the venv" is useless
#      advice here since it already is; the fix is `hash -r` / `python -m pytest`.
_project_venv = Path(__file__).resolve().parent / ".venv"
if (
    _project_venv.is_dir()
    and os.getenv("ALLOW_SYSTEM_PYTHON", "").strip() != "1"
    and Path(sys.prefix).resolve() != _project_venv.resolve()
):
    _active = Path(sys.prefix).resolve()
    _in_some_venv = _active != Path(sys.base_prefix).resolve()
    _declared = os.getenv("VIRTUAL_ENV", "").strip()

    if _in_some_venv:
        _label = _active.name if _active.name not in (".venv", "venv", ".env") else _active.parent.name
        _diagnosis = f"the venv of another project, '{_label}':\n  {_active}"
        _fix = "deactivate\n  source .venv/bin/activate"
    elif _declared and Path(_declared).resolve() == _project_venv.resolve():
        _diagnosis = (
            f"the system Python:\n  {_active}\n"
            f"(this project's venv IS activated — a pytest from outside it is "
            f"shadowing it on PATH)"
        )
        _fix = "hash -r          # drop the cached pytest path\n  python -m pytest   # or bypass PATH entirely"
    else:
        _diagnosis = f"the system Python:\n  {_active}"
        _fix = "source .venv/bin/activate"

    print(
        f"\nRefusing to run: pytest is using {_diagnosis}\n"
        f"not the project venv at {_project_venv}.\n"
        f"Fix: {_fix}\n"
        f"(or run `make all` / any other `make` target, which uses the venv "
        f"automatically)\n"
        f"To run intentionally outside the venv (e.g. CI with a global "
        f"install), set ALLOW_SYSTEM_PYTHON=1.",
        file=sys.stderr,
    )
    sys.exit(3)

import allure
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from config.config import BROWSER, HEADLESS, SLOW_MO, LOGIN_MOBILE, LOGIN_OTP, BASE_URL, LEADS_URL, TIMEOUT, NAV_TIMEOUT
from reporters.log_reporter import LogCollector, generate_log_report
from reporters.excel_reporter import generate_excel_report
from config.test_metadata import TEST_STEPS
from utils.healing_locator import get_heal_log

AUTH_STATE = Path("auth_state.json")
TRACE_DIR = Path("traces")  # Playwright trace.zip files, failed tests only — gitignored

# Session-level stores populated during the run
_log_collector = LogCollector()
_test_results: list[dict] = []
_shared_state: dict = {}   # carries lead ID and amounts across test stages
_pytest_config = None      # stashed in pytest_sessionstart, used by _progress

# Row statuses, ordered worst-signal-first — the canonical order every
# reporter sorts by, so the four reports can never disagree.
#   failed   a real regression
#   xpassed  a strict-xfail known_bug test PASSED: the app bug appears FIXED,
#            the xfail marker is now a lie and must be removed (pytest counts
#            this as a failure, so the run also exits non-zero — intended)
#   skipped  a genuine skip (missing lead id, stage-guard cascade)
#   xfailed  a known_bug test failed as expected — benign, no action
#   passed
STATUS_ORDER = ("failed", "xpassed", "skipped", "xfailed", "passed")
STATUS_LABEL = {"xfailed": "XFAIL", "xpassed": "XPASS"}  # display only; others use .upper()


def _progress(msg: str) -> None:
    """Announce a step inside a fixture that can otherwise sit silent for tens
    of seconds (browser launch, auth_state validity check, fresh login) — with
    no output, a slow-but-working step and a genuine stall look identical.
    Writes through pytest's terminal reporter so the line survives output
    capture; falls back to print if the reporter isn't available yet."""
    reporter = None
    if _pytest_config is not None:
        reporter = _pytest_config.pluginmanager.get_plugin("terminalreporter")
    if reporter is not None:
        reporter.write_line(f"    … {msg}")
    else:
        print(f"    … {msg}")


def _meta_key(item) -> str:
    """Build the ClassName::test_name key used to look up TEST_STEPS.

    Uses item.originalname rather than item.name so that parametrized tests
    resolve too: pytest sets item.name to "test_tab_switching[Earned]", which
    never matches a TEST_STEPS key and would silently leave the Steps column
    blank for every generated case. originalname is the undecorated function
    name ("test_tab_switching") and is only set on parametrized items, so the
    fallback to item.name covers everything else."""
    cls_name = item.cls.__name__ if item.cls else ""
    base = getattr(item, "originalname", None) or item.name
    return f"{cls_name}::{base}" if cls_name else base


def _record_result(entry: dict) -> None:
    """Store one result row, keyed by node id so the FINAL attempt wins.

    With --reruns, a flaky test invokes pytest_runtest_makereport once per
    attempt. pytest-rerunfailures only rewrites report.outcome to "rerun" AFTER
    runtestprotocol has already called makereport (in pytest_runtest_protocol),
    so our hook always sees the raw "failed"/"passed" outcome — meaning a
    fail-then-pass test would otherwise record BOTH a failed row and a passed
    row, and the report would count the discarded rerun as a failure. Replacing
    any existing row for the same node id keeps exactly one row per test: its
    last (final) outcome, never an intermediate retry."""
    node_id = entry.get("node_id")
    for i, existing in enumerate(_test_results):
        if existing.get("node_id") == node_id:
            # A failed-then-passed rerun is a real signal (the sanction-tab
            # false positive on 2026-08-18 was exactly this: a failure hidden
            # by a later pass). Both reporters key only off `status`, so
            # surface it in the text instead of adding a new status value that
            # would fall through their status->style lookups.
            if existing.get("status") == "failed" and entry.get("status") == "passed":
                first_error = str(existing.get("actual_outcome", ""))[:120]
                entry = {
                    **entry,
                    "actual_outcome": f"{entry.get('actual_outcome', '')} "
                                      f"(passed on rerun — first attempt failed: {first_error})",
                }
            _test_results[i] = entry
            return
    _test_results.append(entry)


def pytest_sessionstart(session):
    """Start each run with an empty Allure results dir.

    pytest's --alluredir appends to allure-results every run, so it grows
    unbounded and a generated report ends up reflecting every historical run
    (and gets far too large to email). Clearing it here keeps each run's report
    self-contained and small. Set ALLURE_KEEP_RESULTS=1 to retain history.

    The allure plugin creates and holds the directory at configure time (before
    this hook), so we empty its CONTENTS rather than removing the directory —
    deleting the dir itself crashes the plugin when it writes results."""
    global _pytest_config
    _pytest_config = session.config

    if os.getenv("ALLURE_KEEP_RESULTS", "").strip().lower() in ("1", "true", "yes"):
        return
    # A --collect-only session runs no tests and writes no new results/traces —
    # wiping here would only destroy a previous real run's artifacts while
    # someone is just listing tests (e.g. `pytest --collect-only -q`), which is
    # exactly what happened to the 2026-09-09 run's evidence.
    if session.config.getoption("collectonly", False):
        return
    results = Path("allure-results")
    if not results.is_dir():
        return
    for item in results.iterdir():
        if item.is_dir() and not item.is_symlink():
            shutil.rmtree(item, ignore_errors=True)
        else:
            try:
                item.unlink()
            except OSError:
                pass

    # Same reasoning as allure-results above: trace.zip files (written only
    # for failed tests, see the context/logged_in_page fixtures) would
    # otherwise accumulate across every run indefinitely.
    if TRACE_DIR.is_dir():
        shutil.rmtree(TRACE_DIR, ignore_errors=True)

    # Fail fast on a dead REPORT_EMAIL_PASSWORD instead of discovering it only
    # after the full suite has run. Previously check_config() was never called
    # until pytest_sessionfinish tried to actually send — on 2026-09-10 and
    # 2026-09-15 that meant an SMTPAuthenticationError surfaced 78+ minutes in,
    # after the run's results had nowhere else to go (see email-report.log).
    # Warn and continue: a bad email credential must never abort a test run.
    if not session.config.getoption("collectonly", False) \
            and _should_send_email(session.config) \
            and os.getenv("REPORT_EMAIL_TO", "").strip():
        try:
            from reporters.email_reporter import check_config
            check_config()
        except Exception as e:
            print(
                f"\n⚠️  REPORT_EMAIL_* preflight failed: {type(e).__name__}: {e}\n"
                "   The suite will still run, but the result email will NOT be "
                "sent at the end. Fix REPORT_EMAIL_PASSWORD/TO in .env and "
                "re-verify with `make check-email`.\n"
            )


def pytest_addoption(parser):
    parser.addoption("--lead-id", action="store", default=None,
        help="Lead ID for move-to-login tests.")
    parser.addoption("--sanction-lead-id", action="store", default=None,
        help="Lead ID for move-to-sanction tests.")
    parser.addoption("--disburse-lead-id", action="store", default=None,
        help="Lead ID for move-to-disburse tests.")
    parser.addoption("--login-amount", action="store", default=None,
        help="Loan amount for move-to-login tests.")
    parser.addoption("--sanction-amount", action="store", default=None,
        help="Loan amount for move-to-sanction tests.")
    parser.addoption("--disburse-amount", action="store", default=None,
        help="Loan amount for move-to-disburse tests.")
    parser.addoption("--mark-as-lost-lead-id", action="store", default=None,
        help="Lead ID for mark-as-lost tests.")
    parser.addoption("--reassign-lead-id", action="store", default=None,
        help="Lead ID for reassign-leads tests.")
    parser.addoption("--recommended-docs-lead-id", action="store", default=None,
        help="Lead ID for recommended-docs tests.")
    parser.addoption("--lead-detail-id", action="store", default=None,
        help="Lead ID for lead-detail tab tests (Details/Documents/History/Remarks).")
    parser.addoption("--reopen-lead-id", action="store", default=None,
        help="A LOST lead ID for the Reopen tests.")
    # Email report control. Default (neither flag) = send whenever
    # REPORT_EMAIL_TO is configured (any run — one test, one file, or the full
    # suite). --no-email is the only opt-out.
    parser.addoption("--email", action="store_true", default=False,
        help="No-op, kept for backward compatibility — sending is now the default whenever REPORT_EMAIL_TO is configured.")
    parser.addoption("--no-email", action="store_true", default=False,
        help="Never send the report email for this run.")


def _require_lead_id(cli_value, env_var, flag):
    value = cli_value or os.getenv(env_var)
    if not value:
        pytest.skip(f"No lead ID — pass {flag} or set {env_var} in .env")
    return value

def _resolve_amount(cli_value, env_var):
    return cli_value or os.getenv(env_var) or str(random.randint(100000, 1000000))


@pytest.fixture(scope="session")
def shared_state():
    """Mutable dict shared across the whole session.
    test_02 writes 'created_lead_id'; stage fixtures read it so a full run needs
    no manual .env edits between stages. Isolated runs fall back to .env as before."""
    return _shared_state


# ── Lead ID fixtures ─────────────────────────────────────────────────────────
# In a full run the lead created in test_02 is reused for all three stage tests.
# When running a single stage the fixture falls back to the .env / CLI value.

def _seed_fresh_lead(browser: Browser, auth_state: str) -> str:
    """Create a brand-new lead and return its ID.

    Used to self-seed the mark-as-lost flow: the lifecycle lead created in
    test_02 gets moved Login->Sanction->Disburse by test_03-05, and a disbursed
    lead can't be marked lost, so mark-as-lost needs its own fresh, markable
    lead. Creating one here (instead of reading a hand-maintained .env ID that
    goes stale the moment it's marked lost) keeps the run self-contained."""
    from pages.home_page import HomePage
    from pages.create_lead_page import CreateLeadPage
    from utils.data_helper import generate_lead_data
    ctx = browser.new_context(storage_state=auth_state)
    ctx.set_default_timeout(TIMEOUT)
    try:
        pg = ctx.new_page()
        pg.goto(LEADS_URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
        HomePage(pg).click_create_lead()
        form = CreateLeadPage(pg)
        form.fill_and_submit(generate_lead_data())
        form.success_title.wait_for(state="visible")
        form.go_to_my_leads_button.click()
        return HomePage(pg).get_first_lead_id()
    finally:
        ctx.close()


@pytest.fixture(scope="session")
def mark_as_lost_lead_id(request, browser, auth_state, shared_state):
    # Priority: an explicit CLI override wins (targeting a specific lead);
    # otherwise SELF-SEED a fresh, markable lead so the mark-as-lost -> reopen
    # chain needs nothing from .env and never goes stale. The MARK_AS_LOST_LEAD_ID
    # env var is intentionally NOT consulted — a marked-lost lead can't be
    # re-marked, so a fixed ID breaks on the second run.
    override = request.config.getoption("--mark-as-lost-lead-id")
    if override:
        return override
    if not shared_state.get("mark_as_lost_seed_id"):
        shared_state["mark_as_lost_seed_id"] = _seed_fresh_lead(browser, auth_state)
    return shared_state["mark_as_lost_seed_id"]


@pytest.fixture(scope="session")
def reassign_lead_id(browser: Browser, auth_state: str, shared_state):
    # Must NOT reuse the test_02 lifecycle lead: by the time test_07 runs,
    # test_03-05 have already moved it Login->Sanction->Disburse, so
    # #lead-<id> never appears in the reassign search results and the test
    # times out 45s waiting for a row that will never exist. Same self-seeding
    # pattern as check_offers_lead_id, for the same reason.
    if not shared_state.get("reassign_seed_id"):
        shared_state["reassign_seed_id"] = _seed_fresh_lead(browser, auth_state)
    return shared_state["reassign_seed_id"]


@pytest.fixture(scope="session")
def recommended_docs_lead_id(browser: Browser, auth_state: str, shared_state):
    # Same reasoning as reassign_lead_id above — must not reuse the disbursed
    # lifecycle lead, so always self-seed a fresh one.
    if not shared_state.get("recommended_docs_seed_id"):
        shared_state["recommended_docs_seed_id"] = _seed_fresh_lead(browser, auth_state)
    return shared_state["recommended_docs_seed_id"]


@pytest.fixture(scope="session")
def lead_id(request, shared_state):
    if shared_state.get("created_lead_id"):
        return shared_state["created_lead_id"]
    return _require_lead_id(request.config.getoption("--lead-id"), "LOGIN_LEAD_ID", "--lead-id")

@pytest.fixture(scope="session")
def check_offers_lead_id(browser, auth_state, shared_state):
    # The Loan Offer Calculator's "Checkout Loan Offers!" CTA only shows on an
    # early-stage (pre-login) lead. It must NOT reuse the test_02 lifecycle lead:
    # test_03-05 move that lead Login->Sanction->Disburse before this test runs,
    # and a disbursed lead has no CTA (so the wait times out). A hand-maintained
    # CLI/env lead ID isn't durable — nothing stops the lead it points to from
    # being moved out of pre-login by other activity on the account, and the
    # test then fails with a search timeout instead of a clear error. Always
    # self-seeding a fresh pre-login lead keeps this fixture correct regardless.
    if not shared_state.get("check_offers_seed_id"):
        shared_state["check_offers_seed_id"] = _seed_fresh_lead(browser, auth_state)
    return shared_state["check_offers_seed_id"]

# Lifecycle stages in the order the tests advance the lead through them
# (test_03 -> "login", test_04 -> "sanction", test_05 -> "disburse"). Reaching a
# later stage implies every earlier one — which is exactly what the old
# `!= needed` equality check below got wrong: by the time test_04's last test
# (test_sanction_button_gone_after_already_sanctioned) ran,
# test_move_lead_to_sanction had already advanced stage_reached to "sanction",
# so the guard skipped a test whose precondition was more than satisfied.
_STAGE_ORDER = ("login", "sanction", "disburse")


def _stage_index(stage) -> int:
    """Position of a REACHED stage in _STAGE_ORDER. None (nothing completed
    yet) or an unrecognised value sorts before every real stage, so the
    cascade guard below still protects against the case it was written for."""
    try:
        return _STAGE_ORDER.index(stage)
    except ValueError:
        return -1


def _require_stage(shared_state: dict, needed: str):
    """Skip fast instead of letting a cascade of downstream tests each burn a
    full 45s timeout waiting on a button/tab state that cannot exist because
    an earlier stage never completed (the 2026-08-18 run lost ~8 minutes this
    way when Move To Sanction failed and all five Move To Disburse tests
    still ran to their individual timeouts).

    Gated on shared_state['create_lead_attempted'] (set unconditionally at the
    top of test_02::test_create_lead_successful), NOT on 'created_lead_id'.
    Gating on created_lead_id alone can't tell "test_02 was never collected in
    this session" (a standalone `pytest tests/test_05_...` run against a fixed
    .env lead, which must proceed normally) apart from "test_02 WAS collected
    and failed to produce a lead" (a real precondition failure this guard
    exists to catch) — both leave created_lead_id unset. That gap is exactly
    why this guard didn't fire during the 2026-09-09 run: test_02 failed on
    the State-field regression, created_lead_id stayed unset, and every one of
    test_04/test_05's "guarded" tests still ran to a full timeout instead of
    skipping.

    Compares stage POSITION, not equality: a lead already past `needed` is
    trivially ready (a test ordered after test_move_lead_to_sanction sees
    stage_reached == "sanction" but may only need "login"). `needed` is looked
    up with .index() directly (not _stage_index) so a typo in a caller raises
    here instead of silently disabling the guard."""
    if not shared_state.get("create_lead_attempted"):
        return  # test_02 wasn't part of this session — standalone run against a fixed .env lead
    needed_idx = _STAGE_ORDER.index(needed)
    reached = shared_state.get("stage_reached")
    if _stage_index(reached) < needed_idx:
        pytest.skip(
            f"Prior stage '{needed}' did not complete in this run "
            f"(shared_state['stage_reached']={reached!r}) — "
            f"skipping to avoid cascade timeouts"
        )


@pytest.fixture(scope="function")
def login_stage_ready(shared_state):
    """Require that test_02 actually produced a lead before a Move To Login
    test runs. Unlike sanction_stage_ready/disburse_stage_ready this isn't a
    _require_stage() call — test_03 doesn't need a PRIOR stage reached, it
    needs test_02::test_create_lead_successful itself to have succeeded.
    A standalone `pytest tests/test_03_...` run (test_02 never collected, so
    'create_lead_attempted' is never set) proceeds normally, falling back to
    LOGIN_LEAD_ID / --lead-id via the `lead_id` fixture as before."""
    if shared_state.get("created_lead_id"):
        return
    if shared_state.get("create_lead_attempted"):
        pytest.skip(
            "test_02::test_create_lead_successful ran in this session but did "
            "not produce a lead — skipping to avoid cascade timeouts"
        )


@pytest.fixture(scope="function")
def sanction_stage_ready(shared_state):
    """Require that the lead actually reached Logged In before a Move To
    Sanction test runs. Set by test_03::test_move_lead_to_login."""
    _require_stage(shared_state, "login")


@pytest.fixture(scope="function")
def disburse_stage_ready(shared_state):
    """Require that the lead actually reached Sanctioned before a Move To
    Disburse test runs. Set by test_04::test_move_lead_to_sanction."""
    _require_stage(shared_state, "sanction")


@pytest.fixture(scope="session")
def back_forward_lead_id(browser: Browser, auth_state: str, shared_state):
    # The back/forward bug test must NOT reuse the test_02 lifecycle lead_id:
    # test_move_lead_to_login runs immediately before it in file order and
    # moves that lead out of Pre-Login, which starved this test's search and
    # made it time out (45s) before it ever reached its assertion. Same
    # self-seeding pattern as check_offers_lead_id for the same reason: a
    # fixed/shared lead id here would go stale the moment anything else in
    # the run moves it.
    if not shared_state.get("back_forward_seed_id"):
        shared_state["back_forward_seed_id"] = _seed_fresh_lead(browser, auth_state)
    return shared_state["back_forward_seed_id"]


@pytest.fixture(scope="session")
def mark_lost_edge_case_lead_id(browser: Browser, auth_state: str, shared_state):
    # Edge-case mark-lost/reopen probes (revived from tests/_scratch_explore.py)
    # must NOT reuse mark_as_lost_lead_id: that lead is the one
    # test_mark_lead_as_lost marks lost and stashes as shared_state["lost_lead_id"]
    # for test_09b's reopen tests to consume. Cycling it through an extra
    # reopen/re-lost round here first would leave test_09b operating on a lead
    # whose state history no longer matches its own assumptions. Same
    # self-seeding pattern as back_forward_lead_id/check_offers_lead_id for the
    # same reason: these probes need a lead nothing else in the run depends on.
    if not shared_state.get("mark_lost_edge_case_seed_id"):
        shared_state["mark_lost_edge_case_seed_id"] = _seed_fresh_lead(browser, auth_state)
    return shared_state["mark_lost_edge_case_seed_id"]


@pytest.fixture(scope="session")
def lead_detail_id(browser: Browser, auth_state: str, shared_state):
    # Lead-detail tab tests (Details/Documents/History/Remarks). Must not reuse
    # the test_02 lifecycle lead — by the time these run it may already be
    # Sanctioned/Disbursed, and test_04/test_05's stage-button assertions could
    # be confused by an edit made here. Same self-seeding pattern as
    # check_offers_lead_id/reassign_lead_id, for the same reason.
    if not shared_state.get("lead_detail_seed_id"):
        shared_state["lead_detail_seed_id"] = _seed_fresh_lead(browser, auth_state)
    return shared_state["lead_detail_seed_id"]


@pytest.fixture(scope="session")
def reopen_lead_id(request, shared_state):
    # Reopen needs a LOST lead. In a run that also exercises mark-as-lost, the
    # mark-as-lost e2e test stashes the lead it just lost in shared_state, so the
    # reopen tests reuse that exact lead (chained: mark-as-lost -> reopen) with no
    # .env maintenance. Isolated reopen-only runs fall back to REOPEN_LEAD_ID.
    if shared_state.get("lost_lead_id"):
        return shared_state["lost_lead_id"]
    return _require_lead_id(
        request.config.getoption("--reopen-lead-id"),
        "REOPEN_LEAD_ID",
        "--reopen-lead-id",
    )


@pytest.fixture(scope="session")
def sanction_lead_id(request, shared_state):
    if shared_state.get("created_lead_id"):
        return shared_state["created_lead_id"]
    return _require_lead_id(request.config.getoption("--sanction-lead-id"), "SANCTION_LEAD_ID", "--sanction-lead-id")

@pytest.fixture(scope="session")
def disburse_lead_id(request, shared_state):
    if shared_state.get("created_lead_id"):
        return shared_state["created_lead_id"]
    return _require_lead_id(request.config.getoption("--disburse-lead-id"), "DISBURSE_LEAD_ID", "--disburse-lead-id")


# ── Amount fixtures ───────────────────────────────────────────────────────────
# Amounts chain through stages: login_amount → sanction_amount → disburse_amount.
# Each fixture stores its value in shared_state so the next stage picks it up.

@pytest.fixture(scope="session")
def login_amount(request, shared_state):
    val = _resolve_amount(request.config.getoption("--login-amount"), "LOGIN_AMOUNT")
    shared_state["login_amount"] = val
    return val

@pytest.fixture(scope="session")
def sanction_amount(request, shared_state):
    # Only chain the prior stage's amount when we're operating on the lead that
    # was created earlier in this run. Without a created lead the stage falls
    # back to a fixed .env lead, whose real sanctioned amount is tied to
    # SANCTION_AMOUNT — chaining login_amount here would clobber that and break
    # amount-comparison tests (e.g. "amount exceeds sanction").
    val = ((shared_state.get("created_lead_id") and shared_state.get("login_amount")) or
           _resolve_amount(request.config.getoption("--sanction-amount"), "SANCTION_AMOUNT"))
    shared_state["sanction_amount"] = val
    return val

@pytest.fixture(scope="session")
def disburse_amount(request, shared_state):
    return ((shared_state.get("created_lead_id") and shared_state.get("sanction_amount")) or
            _resolve_amount(request.config.getoption("--disburse-amount"), "DISBURSE_AMOUNT"))


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance):
    mode = "headless" if HEADLESS else "headed (a real window will open)"
    _progress(f"launching {BROWSER} ({mode})…")
    browser_type = getattr(playwright_instance, BROWSER)
    br = browser_type.launch(headless=HEADLESS, slow_mo=SLOW_MO)
    _progress(f"{BROWSER} launched")
    yield br
    br.close()


def _fresh_login(browser: Browser):
    """Log in with credentials and persist the session to auth_state.json."""
    if not LOGIN_MOBILE or not LOGIN_OTP:
        pytest.fail(
            "LOGIN_MOBILE / LOGIN_OTP not set — add them to .env "
            "(no defaults are baked into source).",
            pytrace=False,
        )
    _progress("logging in with LOGIN_MOBILE/LOGIN_OTP…")
    from pages.login_page import LoginPage
    ctx = browser.new_context()
    page = ctx.new_page()
    LoginPage(page).login(mobile=LOGIN_MOBILE, otp=LOGIN_OTP)
    _progress(f"OTP submitted, waiting up to {NAV_TIMEOUT / 1000:.0f}s for login to land…")
    # login() returns as soon as "Verify" is clicked and the SPA then redirects
    # off /login (to the Dashboard, not My Leads — see LEADS_URL). Once off
    # /login, navigate straight to My Leads so the teamtab wait below (and every
    # downstream test) lands on the page that actually has it.
    page.wait_for_url(lambda url: "/login" not in url, timeout=NAV_TIMEOUT)
    page.goto(LEADS_URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
    # The SPA writes its auth data to localStorage progressively: the JWT
    # first, then userAccess / loginUserInfo which gate page access. Saving
    # before those land persists a session that reuses into /login (no token)
    # or /no-access (token but no access). Waiting for the leads tabs to
    # render is the end-to-end signal that every required key has been written.
    page.locator("div.teamtab", has_text="Sanctioned").wait_for(state="visible", timeout=NAV_TIMEOUT)
    ctx.storage_state(path=str(AUTH_STATE))
    ctx.close()
    _progress("fresh login complete, auth_state.json saved")


def _state_is_valid(browser: Browser) -> bool:
    """Return True if the saved auth_state still authenticates.
    The app stores a JWT in localStorage but validates it server-side on boot;
    an invalidated session is wiped and the app redirects to /login. The JWT's
    own exp claim is therefore not a reliable check — we must load the app and
    see whether it stays logged in."""
    _progress(f"checking saved auth_state.json (up to {NAV_TIMEOUT / 1000:.0f}s + 5s settle)…")
    ctx = browser.new_context(storage_state=str(AUTH_STATE))
    pg = ctx.new_page()
    try:
        pg.goto(BASE_URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
        pg.wait_for_timeout(5000)
        return "/login" not in pg.url
    except Exception:
        return False
    finally:
        ctx.close()


@pytest.fixture(scope="session")
def auth_state(browser: Browser):
    """Login once per session and save cookies/storage to auth_state.json.
    Reuses the saved file if it still authenticates; if the session has been
    invalidated server-side (app redirects to /login), it re-logs in
    automatically so a stale file no longer breaks the whole run."""
    if not AUTH_STATE.exists():
        _progress("no auth_state.json found — logging in fresh")
        _fresh_login(browser)
    elif not _state_is_valid(browser):
        _progress("saved auth_state.json is no longer valid — re-logging in")
        AUTH_STATE.unlink()
        _fresh_login(browser)
    else:
        _progress("saved auth_state.json is still valid — reusing it")
    return str(AUTH_STATE)


def _trace_path(nodeid: str) -> Path:
    """Filesystem-safe trace.zip path for a test node id.

    Node ids contain '::', '/' and (for parametrized tests) '[...]' — all
    invalid or awkward in a filename — so collapse everything but
    alnum/dash/dot/underscore to '_'."""
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in nodeid)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    return TRACE_DIR / f"{safe}.zip"


def _failed(request) -> bool:
    """True if the current test failed during setup or call. Read from the
    reports pytest_runtest_makereport stashes on the item — see there for why
    that's safe to rely on from fixture teardown."""
    for when in ("setup", "call"):
        rep = getattr(request.node, f"rep_{when}", None)
        if rep is not None and rep.failed:
            return True
    return False


@pytest.fixture(scope="function")
def context(browser: Browser, request):
    # try/finally so the context (and its visible window) always closes, even if
    # setup raises before the yield — a bare `yield ... ; ctx.close()` skips the
    # close on any pre-yield error and leaks the browser window.
    ctx = browser.new_context()
    ctx.set_default_timeout(TIMEOUT)
    ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    try:
        yield ctx
    finally:
        if _failed(request):
            ctx.tracing.stop(path=str(_trace_path(request.node.nodeid)))
        else:
            ctx.tracing.stop()  # no path => discard, matches screenshot-on-failure-only policy
        ctx.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext, request) -> Page:
    pg = context.new_page()
    node_id = request.node.nodeid
    pg.on("console", lambda msg: _log_collector.add(node_id, msg.type, msg.text))
    pg.on("pageerror", lambda err: _log_collector.add(node_id, "pageerror", str(err)))
    yield pg


@pytest.fixture(scope="function")
def logged_in_page(browser: Browser, auth_state: str, request) -> Page:
    """Each test gets a fresh page pre-loaded with the saved auth session.

    A per-test context (not a shared one) is deliberate: sharing a single page or
    context was measured to be NO faster — the per-test cost is the app's
    goto()/SPA boot, and returning a shared page to a clean state costs as much
    (or more, due to background polling) as a fresh load. Fresh-per-test keeps
    each test fully isolated and runnable on its own. To cut total wall-clock,
    parallelize (pytest-xdist) rather than share an instance."""
    # try/finally so the context always closes even when setup fails before the
    # yield — most commonly when pg.goto(BASE_URL) times out. Without it that
    # navigation failure orphans the context and leaves its window open (doubled
    # by --reruns), which is why windows lingered on setup-phase failures.
    ctx = browser.new_context(storage_state=auth_state)
    ctx.set_default_timeout(TIMEOUT)
    ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    setup_failed = False
    try:
        pg = ctx.new_page()
        node_id = request.node.nodeid
        pg.on("console", lambda msg: _log_collector.add(node_id, msg.type, msg.text))
        pg.on("pageerror", lambda err: _log_collector.add(node_id, "pageerror", str(err)))
        pg.goto(LEADS_URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
        yield pg
    except Exception:
        # An exception here (most commonly the goto() timeout the comment
        # above already guards for) happens before item.rep_call exists — the
        # "call" phase report our hook stashes it into is only generated once
        # setup completes — so this is the only signal we have that THIS
        # setup failed and its trace is worth keeping.
        setup_failed = True
        raise
    finally:
        if setup_failed or _failed(request):
            ctx.tracing.stop(path=str(_trace_path(request.node.nodeid)))
        else:
            ctx.tracing.stop()  # no path => discard, matches screenshot-on-failure-only policy
        ctx.close()


def _extract_actual_outcome(error_str: str) -> str:
    """Pull the most meaningful line from a pytest failure repr."""
    if not error_str:
        return ""
    lines = [l.strip() for l in error_str.splitlines() if l.strip()]
    for line in reversed(lines):
        low = line.lower()
        if any(k in low for k in ("assertionerror", "assert ", "expected", "not visible", "timeout")):
            return line[:220]
    return lines[-1][:220] if lines else ""


def _classify(item, call, rep) -> str:
    """Map a 'call'-phase report onto one of STATUS_ORDER.

    pytest gives xfail no outcome of its own: _pytest/skipping.py rewrites
    rep.outcome to "skipped" and attaches rep.wasxfail (an xfailed test), or —
    for strict=True that unexpectedly PASSES — rewrites it to "failed" with NO
    wasxfail and longrepr "[XPASS(strict)] <reason>". Reading only
    rep.passed/rep.failed therefore filed every known_bug test as "skipped",
    and would have filed a FIXED bug as a plain "failed" with no signal that
    it deserves attention."""
    if hasattr(rep, "wasxfail"):
        # skipped+wasxfail = expected failure; passed+wasxfail = non-strict XPASS.
        return "xfailed" if rep.skipped else "xpassed"
    if (
        rep.failed
        and call.excinfo is None                          # nothing was actually raised…
        and item.get_closest_marker("xfail") is not None   # …yet the test is xfail-marked
        and not item.config.option.runxfail
    ):
        return "xpassed"                                   # strict XPASS
    if rep.passed:
        return "passed"
    if rep.failed:
        return "failed"
    return "skipped"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    # Stash each phase's report on the item (the standard pytest pattern for
    # exposing pass/fail to fixture teardown, which runs after this hook has
    # already fired for "setup" and "call"). The context/logged_in_page
    # fixtures read item.rep_call in their `finally` to decide whether to save
    # a Playwright trace — tracing every test would slow the run and bloat
    # disk for no benefit; only a failure needs the trace.
    setattr(item, f"rep_{rep.when}", rep)

    # --reruns retries failed tests. pytest-rerunfailures rewrites the intermediate
    # attempt's outcome to "rerun", but only AFTER runtestprotocol has called this
    # hook, so we normally still see the raw "failed" here. The real dedupe that
    # keeps one row per test (its final outcome) happens in _record_result; this
    # guard is a cheap safety net for any path that does surface "rerun" directly.
    if getattr(rep, "outcome", "") == "rerun":
        return

    if rep.when == "call":
        status = _classify(item, call, rep)

        # Capture a screenshot only on failure — passing tests don't need one,
        # and full-page captures for every test slow the run and bloat reports.
        # Gated on `status`, not `rep.failed`: a strict XPASS also reports
        # rep.failed=True even though the test body ran clean and passed.
        screenshot_b64 = ""
        if status == "failed":
            for fixture_name in ("logged_in_page", "page"):
                pg = item.funcargs.get(fixture_name)
                if pg:
                    # Every stage form (Move To Login/Sanction/Disburse) lives
                    # on a POPUP tab, not this dashboard page — a screenshot
                    # of just `pg` showed the list view for all 13 failures in
                    # the 2026-08-18 run, never the form that actually failed.
                    # Walk every open page in the context and attach each;
                    # each gets its own try/except because tests routinely
                    # close(lead_page) before the test ends, and a closed page
                    # must not abort the loop.
                    try:
                        all_pages = list(pg.context.pages)
                    except Exception:
                        all_pages = [pg]
                    last_shot = None
                    for idx, p in enumerate(all_pages):
                        try:
                            shot = p.screenshot(full_page=True)
                            allure.attach(
                                shot,
                                name=f"screenshot_on_failure_{idx}_{p.url}",
                                attachment_type=allure.attachment_type.PNG,
                            )
                            last_shot = shot  # most-recently-opened page wins
                        except Exception:
                            pass
                    if last_shot:
                        screenshot_b64 = base64.b64encode(last_shot).decode("utf-8")
                    break

        # Description from docstring (first line only)
        description = ""
        if hasattr(item, "function") and item.function.__doc__:
            description = item.function.__doc__.strip().splitlines()[0].strip()

        # Expected outcome from @allure.story marker; feature for grouping.
        expected_outcome = ""
        feature = ""
        for marker in item.iter_markers("allure_label"):
            ltype = marker.kwargs.get("label_type")
            if ltype == "story" and not expected_outcome:
                expected_outcome = marker.kwargs.get("value", "")
            elif ltype == "feature" and not feature:
                feature = marker.kwargs.get("value", "")
        if not feature:
            feature = (item.cls.__name__ if item.cls else "") or "Tests"

        # Steps from static metadata (keyed by ClassName::test_name)
        meta_key = _meta_key(item)
        steps = TEST_STEPS.get(meta_key, "")

        # Actual outcome
        if status == "passed":
            actual_outcome = f"Verified: {expected_outcome}" if expected_outcome else "Test passed"
        elif status == "failed":
            actual_outcome = _extract_actual_outcome(str(rep.longrepr))
        elif status == "xfailed":
            # rep.wasxfail is the marker's reason (or "reason: <msg>" from a
            # pytest.xfail() call) — the documented app defect, in prose.
            actual_outcome = f"Known bug still present (expected failure) — {getattr(rep, 'wasxfail', '')}"[:400]
        elif status == "xpassed":
            actual_outcome = (
                "UNEXPECTED PASS — this known bug appears FIXED. Remove "
                "@pytest.mark.known_bug / @pytest.mark.xfail from this test. "
                f"[{getattr(rep, 'wasxfail', '') or str(rep.longrepr)}]"
            )[:400]
        else:
            actual_outcome = "Skipped"

        _record_result({
            "node_id":         item.nodeid,
            "name":            item.name,
            "status":          status,
            "duration":        f"{rep.duration:.2f}s",
            # xfailed keeps error="" so the log report doesn't render a red
            # traceback for a benign, expected failure; xpassed keeps it since
            # that IS the actionable "the bug looks fixed" signal.
            "error":           str(rep.longrepr) if status in ("failed", "xpassed") else "",
            "screenshot_b64":  screenshot_b64,
            "description":     description,
            "steps":           steps,
            "expected_outcome": expected_outcome,
            "actual_outcome":  actual_outcome,
            "feature":         feature,
        })

        # Attach browser JS console logs to the Allure report
        js_logs = _log_collector.get(item.nodeid)
        if js_logs:
            log_text = "\n".join(
                f"[{e['time']}] [{e['type'].upper():8s}] {e['message']}"
                for e in js_logs
            )
            allure.attach(log_text, name="browser_console_logs", attachment_type=allure.attachment_type.TEXT)

    elif rep.when == "setup" and rep.skipped:
        # @pytest.mark.xfail(run=False) produces a setup-phase skip carrying
        # wasxfail rather than actually running the test body — treat it as
        # xfailed, not a genuine skip, for the same reason as the call branch.
        setup_status = "xfailed" if hasattr(rep, "wasxfail") else "skipped"
        meta_key = _meta_key(item)
        _record_result({
            "node_id":          item.nodeid,
            "name":             item.name,
            "status":           setup_status,
            "duration":         "",
            "error":            "",
            "screenshot_b64":   "",
            "description":      "",
            "steps":            TEST_STEPS.get(meta_key, ""),
            "expected_outcome": "",
            "actual_outcome":   "Known bug (not run)" if setup_status == "xfailed" else "Skipped",
            # The "call"-branch row always sets this (used by email_reporter's
            # per-feature grouping); a setup-skip must too, or any reporter
            # keying off it raises KeyError on a skip-cascade row.
            "feature":          (item.cls.__name__ if item.cls else "") or "Tests",
        })


def _should_send_email(config) -> bool:
    """Send whenever REPORT_EMAIL_TO is configured. --no-email is the only
    opt-out; --email is kept as a no-op for backward compatibility with
    existing `make` targets and scripts that already pass it.

    Previously this asked interactively on /dev/tty and defaulted to NOT
    sending whenever there was no controlling terminal (cron/CI/an agent
    shell) or the 60s prompt timed out — so only `make report-email` (the one
    target that passes --email) ever actually delivered a report; every
    `make report` / `make all` / unattended run silently declined with
    'Email skipped by choice.'. Configuring REPORT_EMAIL_TO is itself the
    opt-in to sending; asking again after that was the bug."""
    return not config.getoption("--no-email")


EMAIL_LOG = Path("email-report.log")  # append-only run journal, gitignored


def _log_email(status: str, detail: str, trace: str = "") -> None:
    """Print AND persist one line about this run's email attempt.

    Every path here used to be print-only inside an `except Exception` — once
    the console scrolled away there was no artifact anywhere on disk to answer
    "why didn't last Tuesday's report arrive?". Appends (never truncates) so
    the file is a running journal across invocations. Never raises: a logging
    problem must not be the thing that fails an otherwise-green suite."""
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {status:<12} {detail}"
    icon = {"SENT": "📧", "FAILED": "⚠️ ", "DECLINED": "✉️ ",
            "UNCONFIGURED": "✉️ ", "SKIPPED": "✉️ "}.get(status, "✉️ ")
    print(f"{icon} {line}")
    try:
        with EMAIL_LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
            if trace:
                fh.write("".join(f"    {l}\n" for l in trace.strip().splitlines()))
    except Exception:
        pass


def pytest_sessionfinish(session, exitstatus):
    # Surface skips loudly. The `_stage_guard` autouse fixtures in
    # test_04/test_05 skip TestMoveToSanction (10 tests) / TestMoveToDisburse
    # (11 tests) wholesale when the upstream stage failed — a real defense
    # against the 2026-08-18 cascade (an 8-minute wait per test as each one
    # independently timed out looking for a button that couldn't exist), but
    # it means a "green" run can still be missing ~10% of the suite with no
    # visible signal unless someone scrolls through the full test list. Print
    # a count so a skip cascade is impossible to miss in the console summary.
    # known_bug tests (@pytest.mark.xfail) are classified separately from
    # genuine skips (see _classify) — split the banner accordingly so it only
    # ever lists real skips, and known-bug results get their own, distinct
    # signal instead of hiding inside "skipped".
    genuine_skips = [r for r in _test_results if r["status"] == "skipped"]
    xfailed_rows  = [r for r in _test_results if r["status"] == "xfailed"]
    xpassed_rows  = [r for r in _test_results if r["status"] == "xpassed"]

    if genuine_skips:
        print(f"\n\n⚠️  {len(genuine_skips)} test(s) skipped this run:")
        for r in genuine_skips:
            print(f"   - {r['name']}")
        print(
            "   A cluster of skips in TestMoveToSanction/TestMoveToDisburse "
            "usually means an earlier stage (Move To Login/Sanction) failed — "
            "check that test's result, not just these skips."
        )

    if xfailed_rows:
        # Benign and expected — these are the known_bug tests documenting live
        # app defects; one line, no per-test list needed.
        print(f"\nℹ️  {len(xfailed_rows)} known-bug test(s) failed as expected (XFAIL) — no action needed.")

    if xpassed_rows:
        print(f"\n\n🎉 {len(xpassed_rows)} known-bug test(s) UNEXPECTEDLY PASSED (XPASS) — the app bug(s) look FIXED:")
        for r in xpassed_rows:
            print(f"   - {r['name']}  ({r['node_id']})")
        print(
            "   Remove @pytest.mark.known_bug + @pytest.mark.xfail(strict=True) from each. "
            "Until then strict xfail counts these as failures, so the run exits non-zero."
        )

    # Each reporter is isolated so one failing (bad path, openpyxl error, etc.)
    # never suppresses the others or the heal report below.
    attachments: list[str] = []
    if _test_results:
        # Label each row with the `make <target>` that reruns it (per-test) and
        # the one that reruns its whole file (per-feature), parsed straight from
        # the Makefile so the mapping can't drift. Isolated like the reporters
        # below: a missing/unparseable Makefile must never block report generation.
        try:
            from reporters.make_map import annotate_results
            annotate_results(_test_results)
        except Exception as e:
            print(f"⚠️  make-target annotation skipped: {e}")
        try:
            from reporters.bdd_reporter import generate_bdd_report
            summary_path = generate_bdd_report(_test_results, "test-summary.html")
            print(f"\n\nTest summary:   {summary_path}   (open with: make reports)")
            # Attached (zipped, see email_reporter): the email BODY already renders
            # an equivalent summary inline, but recipients who want the standalone,
            # fully-rendering page get it too. Zipped because mail clients preview
            # a raw .html attachment as source, not the rendered page.
            attachments.append(str(summary_path))
        except Exception as e:
            print(f"\n\n⚠️  Summary report generation failed: {e}")
        try:
            report_path = generate_log_report(_test_results, _log_collector, "log-report.html")
            print(f"Log JS report:  {report_path}")
            # Attached (zipped, see email_reporter) for the same reason as
            # test-summary.html above — full console-log/screenshot detail beyond
            # what the email body summarises inline.
            attachments.append(str(report_path))
        except Exception as e:
            print(f"⚠️  Log report generation failed: {e}")
        try:
            excel_path = generate_excel_report(_test_results, "test-report.xlsx")
            print(f"Excel report:   {excel_path}")
            attachments.append(str(excel_path))
        except Exception as e:
            print(f"⚠️  Excel report generation failed: {e}")

        # Email the reports after ANY run — single test, one feature file, or the
        # full suite. Isolated like the reporters above: an SMTP/config error is
        # logged (both to console and email-report.log) but never fails the run.
        if not os.getenv("REPORT_EMAIL_TO", "").strip():
            # Previously totally silent — an unset recipient list and a
            # successful send were indistinguishable in the console.
            _log_email(
                "UNCONFIGURED",
                "REPORT_EMAIL_TO is unset — no report email sent. Set "
                "REPORT_EMAIL_TO/USER/PASSWORD in .env (see .env.example), "
                "then verify with `make check-email`."
            )
        else:
            passed  = sum(1 for r in _test_results if r["status"] == "passed")
            xfailed = sum(1 for r in _test_results if r["status"] == "xfailed")
            xpassed = sum(1 for r in _test_results if r["status"] == "xpassed")
            total   = len(_test_results)
            summary = f"Run finished: {passed}/{total} passed"
            if xfailed:
                summary += f", {xfailed} xfail"
            if xpassed:
                summary += f", {xpassed} XPASS (bug fixed?)"
            summary += "."
            if not _should_send_email(session.config):
                _log_email(
                    "DECLINED",
                    "not sent: --no-email was passed for this run. "
                    f"{summary}"
                )
            else:
                # Build a self-contained single-file Allure report to attach.
                # Isolated like the other reporters: a missing CLI or a failed
                # generation is logged but never blocks the email. Size is capped
                # in email_reporter against the actual zipped payload, not the raw
                # file, since that's what counts toward Gmail's message limit.
                try:
                    from reporters.allure_reporter import generate_single_file_report
                    allure_path = generate_single_file_report()
                    if not allure_path:
                        print("⚠️  Allure report skipped (no results to render).")
                    else:
                        attachments.append(allure_path)
                        size_mb = os.path.getsize(allure_path) / (1024 * 1024)
                        print(f"Allure report:  {allure_path}  ({size_mb:.1f} MB)")
                except Exception as e:
                    print(f"⚠️  Allure report generation failed: {e}")
                try:
                    from reporters.email_reporter import send_report_email
                    recipients = send_report_email(_test_results, attachments)
                    _log_email("SENT", f"to {', '.join(recipients)}  |  {summary}")
                except Exception as e:
                    _log_email("FAILED", f"{type(e).__name__}: {e}", traceback.format_exc())
    else:
        _log_email("SKIPPED", "no test results collected (collection error or 0 tests) — nothing to email.")

    heals = get_heal_log()
    if heals:
        import json
        heal_path = "heal-report.json"
        try:
            with open(heal_path, "w") as f:
                json.dump(heals, f, indent=2)
            print(f"⚕️  Heal report: {heal_path}  ({len(heals)} selector(s) were healed — update primary locators)")
        except Exception as e:
            print(f"⚠️  Heal report generation failed: {e}")
