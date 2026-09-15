import re
from playwright.sync_api import Page, Locator
from config.config import TIMEOUT, NAV_TIMEOUT
from utils.healing_locator import HealingLocator


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.page.set_default_timeout(TIMEOUT)

    def navigate(self, url: str):
        self.page.goto(url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)

    def wait_for_url(self, pattern: str):
        self.page.wait_for_url(pattern, timeout=NAV_TIMEOUT)

    @staticmethod
    def digits_only(raw: str) -> str:
        """Strip everything but digits, e.g. '₹50,00,000' -> '5000000'.

        Several amount fields on this app render/re-render through an Indian
        lakh/crore grouping mask (',' separators) and/or a '₹' prefix — reading
        one back with input_value()/inner_text() and comparing it directly
        against the raw digits a test typed or expects will fail even though
        the value is correct. Normalize both sides through this before
        comparing.
        """
        return re.sub(r"[^\d]", "", raw)

    def _assert_filled(self, locator: Locator, expected: str, field_name: str):
        """Read a just-filled field back and raise if the value doesn't match.

        Several inputs on this app apply a mask/format that can silently reject
        part or all of what was typed (e.g. the mobile field on a '+91' prefix,
        or a Sanction/Login/Disbursed ID that fails a bank's LAN format) —
        without this, that shows up only much later as an unrelated toast or
        timeout, far from the fill() call that actually caused it.
        """
        actual = locator.input_value()
        if actual != expected:
            raise AssertionError(
                f"{field_name}: expected {expected!r} after fill, got {actual!r} "
                f"(the field's input mask likely rejected the value)"
            )

    # ── React Select helpers ───────────────────────────────────────────────────
    # All pages use these instead of repeating React Select CSS class fragments.
    # If the app switches dropdown libraries, only these methods need updating —
    # every page object gets the fix automatically.

    def _rs_container(self, label: str, container_id: str = None) -> Locator:
        """Return the innermost div that contains a React Select control.

        Prefer `container_id` when the form gives the control a stable id —
        it survives label-text changes and skips the label/div scan entirely.
        Falls back to the label-anchored lookup (survives grid/layout class
        changes) for forms whose selects have no id."""
        if container_id:
            return self.page.locator(f"#{container_id}")
        return (
            self.page.locator("div")
            .filter(has=self.page.locator("label", has_text=label))
            .filter(has=self.page.locator("[class*='-control']"))
            .last
        )

    def open_select(self, label: str, container_id: str = None) -> None:
        """Open a React Select dropdown by its visible field label (or stable id)."""
        self._rs_container(label, container_id).locator("[class*='-control']").click()

    def type_in_select(self, label: str, text: str, container_id: str = None) -> None:
        """Type a search string into the open React Select for the given label.
        Scoped to visible inputs only — excludes hidden native <input> elements
        that React Select injects alongside the visible search box."""
        self._rs_container(label, container_id).locator("input:not([type='hidden'])").fill(text)

    def choose_option(self, option: str) -> None:
        """Click a React Select option by its exact visible text.
        This app's React Select does not set role='option', so we match on the
        BEM class fragment and filter by exact text."""
        self.page.locator("[class*='-option']").filter(
            has_text=re.compile(f"^{re.escape(option)}$")
        ).click()

    def choose_first_option(self) -> None:
        """Click the first available option in an open React Select."""
        self.page.locator("[class*='-option']").first.click()

    def select_option(self, label: str, search: str, option: str, container_id: str = None) -> None:
        """Open → search → select a React Select dropdown in one call."""
        self.open_select(label, container_id)
        self.type_in_select(label, search, container_id)
        self.choose_option(option)

    # ── Self-healing locator factory ──────────────────────────────────────────

    def healing_locator(
        self,
        primary: Locator,
        *fallbacks: Locator,
        name: str = "",
        heal_timeout: int = 1500,
    ) -> HealingLocator:
        """
        Return a HealingLocator that tries `primary` first, then each fallback
        in order.  Use this for any selector that might change when the UI is
        updated.

        Example
        -------
        self.submit_btn = self.healing_locator(
            page.locator("#submit-btn"),             # primary
            page.get_by_role("button", name="Submit"),  # fallback 1
            page.get_by_text("Submit", exact=True),     # fallback 2
            name="submit_button",
        )
        """
        return HealingLocator(
            self.page, primary, list(fallbacks),
            name=name, heal_timeout=heal_timeout,
        )
