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
# file/dir in the repo (e.g. `report`, `reports`) can never shadow them. Each
# included make/*.mk file below declares .PHONY for the targets it defines.
.PHONY: install all e2e headless stage-login stage-sanction stage-disburse \
        reset-session clean

# Per-feature targets live under make/ — see that directory's file names for
# what each one covers, or run `make help` for the full command menu.
include make/pipeline.mk make/leads.mk make/team.mk make/tools.mk \
        make/account.mk make/reports.mk make/help.mk

# ── Setup ──────────────────────────────────────────────────────────────────────

##@ Setup

install: ## Install all dependencies and Playwright browser
	python3 -m venv "$(VENV)"
	"$(VENV)/bin/pip" install -r requirements.txt
	"$(VENV)/bin/playwright" install chromium

# ── Run all tests ──────────────────────────────────────────────────────────────

##@ Run tests

all: ## Run all tests
	$(GUARD) pytest

e2e: ## Run only the happy-path tests (e2e mark)
	$(GUARD) pytest -m e2e

headless: ## Run all tests without a visible browser window
	HEADLESS=true $(GUARD) pytest

# ── Run the happy path up to a chosen stage ─────────────────────────────────────
# Each target runs ONLY the happy-path (e2e-marked) cases needed to drive a lead
# up to and including the named stage. They are cumulative:
#   stage-login    → login → create lead → move to login
#   stage-sanction → … + move to sanction
#   stage-disburse → … + move to disburse  (full lifecycle)

##@ Run happy path up to a stage (cumulative — only those cases run)

stage-login: ## Login -> create lead -> move to login
	pytest -m e2e tests/test_01_login.py tests/test_02_create_lead.py tests/test_03_move_to_login.py -v

stage-sanction: ## ... up to and including move to sanction
	pytest -m e2e tests/test_01_login.py tests/test_02_create_lead.py tests/test_03_move_to_login.py tests/test_04_move_to_sanction.py -v

stage-disburse: ## ... full lifecycle, ending at disburse
	pytest -m e2e tests/test_01_login.py tests/test_02_create_lead.py tests/test_03_move_to_login.py tests/test_04_move_to_sanction.py tests/test_05_move_to_disburse.py -v

# ── Utilities ──────────────────────────────────────────────────────────────────

##@ Utilities

# Delete saved login session — next run will prompt for a fresh OTP
reset-session: ## Force a fresh OTP login on next run
	rm -f auth_state.json

# Remove generated reports and pytest cache
clean: ## Remove all generated reports and cache files
	rm -f log-report.html test-report.xlsx test-summary.html allure-report.html heal-report.json
	rm -rf allure-results allure-report .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
