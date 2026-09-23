# `make help` (the .DEFAULT_GOAL, set in the root Makefile) — self-documenting:
# it scans every file in $(MAKEFILE_LIST) (the root Makefile plus every
# included make/*.mk) for two comment conventions rather than hand-listing
# targets, so a target's help entry can never drift from its recipe:
#
#   ##@ Section name       — starts a new section heading
#   target: ## description — adds `target` to the menu under the current heading
#
# Only the ~40 group-level targets carry a `##` tag; the ~190 single-test
# targets are intentionally left untagged so `make help` stays a feature-level
# menu, not a full test list (see README.md / PROJECT_OVERVIEW.md, or grep
# tests/ and the make/*.mk files, for the full per-test target list).
.PHONY: help

help:
	@echo ""
	@echo "Automation Saathi — available commands"
	@echo "======================================="
	@awk 'BEGIN {FS = ":.*##"} \
		/^##@/ {printf "\n%s\n", substr($$0, 5); next} \
		/^[a-zA-Z0-9_.-]+:.*##/ {printf "  make %-32s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Each feature above also exposes one target per test case (e.g. make login-no-mobile)."
	@echo "Run 'make check-targets' to confirm every tests/test_*.py file has a target."
	@echo ""
