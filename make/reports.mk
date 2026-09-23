# Report generation/opening + email + the check-targets drift guard.
# Depends on ALLURE and GUARD from the root Makefile.

.PHONY: open-log-report open-excel-report open-report generate-report \
        allure-report open-reports reports report report-email check-email check-targets

##@ Reports

open-log-report:
	xdg-open log-report.html 2>/dev/null || open log-report.html 2>/dev/null || echo "Open log-report.html in your browser"

open-excel-report: ## Open the Excel report only
	xdg-open test-report.xlsx 2>/dev/null || open test-report.xlsx 2>/dev/null || echo "Open test-report.xlsx in your spreadsheet app"

# Allure needs a working JVM. This environment's JAVA_HOME points at a
# non-existent JDK, which makes allure's launcher abort; unset it so allure
# falls back to `java` on PATH.
ALLURE_RUN := env -u JAVA_HOME $(ALLURE)

# `make reports` — opens ALL THREE reports for the latest run:
#   1. test-summary.html   — plain-English (Cucumber-style) summary; failed tests detailed
#   2. allure-report/...   — Allure technical report (full steps, traces, logs)
#   3. test-report.xlsx    — Excel summary
reports: ## Open the plain-English summary (grouped by feature + make command)
	@$(ALLURE_RUN) generate allure-results -o allure-report --clean --single-file 2>/dev/null || echo "(Allure report generation skipped)"
	@xdg-open test-summary.html 2>/dev/null || open test-summary.html 2>/dev/null || echo "Open test-summary.html in your browser"
	@xdg-open allure-report/index.html 2>/dev/null || open allure-report/index.html 2>/dev/null || echo "Open allure-report/index.html in your browser"
	@xdg-open test-report.xlsx 2>/dev/null || open test-report.xlsx 2>/dev/null || echo "Open test-report.xlsx in your spreadsheet app"
	@echo "Opened: test-summary.html (plain English) + allure-report/index.html (Allure) + test-report.xlsx (Excel)"

# Allure (technical view) only: full steps, stack traces, browser logs, timeline.
allure-report: ## Open the Allure report (technical: full steps + stack traces)
	@$(ALLURE_RUN) generate allure-results -o allure-report --clean --single-file
	@echo "Allure report: $(CURDIR)/allure-report/index.html"
	@xdg-open allure-report/index.html 2>/dev/null || open allure-report/index.html 2>/dev/null || echo "Open allure-report/index.html in your browser"

# Live, server-backed Allure report (interactive; blocks until you stop it).
open-report: ## Open the Allure report as a live server (interactive)
	$(ALLURE_RUN) serve allure-results

# Generate the multi-file Allure report into allure-report/ without opening.
generate-report:
	$(ALLURE_RUN) generate allure-results -o allure-report --clean

# Open the legacy HTML log report (browser console logs) + Excel report.
open-reports: ## Open the legacy HTML log report + Excel report
	xdg-open log-report.html 2>/dev/null || open log-report.html 2>/dev/null || true
	xdg-open test-report.xlsx 2>/dev/null || open test-report.xlsx 2>/dev/null || true

# Run the whole suite, then open all three reports — the one-shot command.
# The leading `-` is required: a run with any failures exits non-zero, and
# without it `make` would abort before the `reports` step it exists to reach.
report: ## Run the whole suite, then open all three reports
	-$(GUARD) pytest
	@$(MAKE) reports

# Run the whole suite and email the report with NO prompt — for cron/CI or an
# unattended overnight run. The leading `-` is required: a run with failures
# exits non-zero, and the email must still go out.
report-email: ## Run the whole suite and email the report, no prompt
	-$(GUARD) pytest --email

# Validate the email config without running any tests or sending mail: checks
# the REPORT_EMAIL_* env vars are present and that the SMTP server accepts the
# app password. Use this after rotating REPORT_EMAIL_PASSWORD.
check-email: ## Validate REPORT_EMAIL_* config without sending mail
	@"$(VENV)/bin/python" -c "from reporters.email_reporter import check_config; check_config()"

# Drift guard: fails (exit 1) if any tests/test_*.py file has no bare
# `pytest tests/<file>.py` make target — catches a new test file that was
# never wired into this Makefile. Uses the same Makefile parser the reports
# use (reporters/make_map.py) so this can never disagree with them.
check-targets: ## Fail if any test file has no make target (drift guard)
	@"$(VENV)/bin/python" -c "from reporters.make_map import untargeted_test_files as u; import sys; m = u(); print('\n'.join(m)) if m else print('All test files have a make target.'); sys.exit(1 if m else 0)"
