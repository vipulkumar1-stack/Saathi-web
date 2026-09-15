"""
Self-healing Playwright locator.

When the primary selector fails to find an element, HealingLocator tries each
fallback strategy in order.  The first one that finds an attached element wins.

Every healing event is recorded in a global log. At the end of the pytest
session, conftest.py writes that log to heal-report.json so the team can
identify and fix broken primary selectors.

Usage in a page object:
    self.first_name_input = self.healing_locator(
        page.locator("#first_name"),            # primary  — HTML id
        page.get_by_label("First Name"),        # fallback 1 — label text
        page.get_by_placeholder("First Name"),  # fallback 2 — placeholder
        name="first_name_input",
    )
"""

import logging
from datetime import datetime
from playwright.sync_api import Locator, Page

# Python's isinstance() checks obj.__class__ when type(obj) doesn't match.
# Exposing __class__ = Locator as a property makes
#   isinstance(healing_locator, Locator)  →  True
# which is required for Playwright's expect() to accept HealingLocator.
_LOCATOR_CLASS = Locator

logger = logging.getLogger("playwright_healer")

# Module-level list — conftest.py imports this to write the report.
_heal_log: list[dict] = []

# HealingLocator's own instance attributes. __getattr__ refuses to resolve for
# these so a partially-built instance can't recurse; every other attribute
# (including Playwright internals like _impl_obj) forwards to the real locator.
_OWN_ATTRS = frozenset(
    {"_page", "_primary", "_fallbacks", "_name", "_heal_timeout", "_resolved"}
)


def get_heal_log() -> list[dict]:
    """Return all healing events recorded in this pytest session."""
    return _heal_log


class HealingLocator:
    """
    Drop-in replacement for a Playwright Locator.

    Every attribute access (click, fill, wait_for, …) is forwarded to the
    first strategy whose element is attached in the DOM.  If the primary
    locator works, there is zero overhead.  If it fails, fallbacks are tried
    in the order supplied, and a warning is logged.

    Caveat — negative / absence assertions:
        Resolution requires *some* strategy to be attached to the DOM. If you
        expect the element to be ABSENT (e.g. expect(loc).not_to_be_visible()
        or .to_have_count(0)), _resolve() will exhaust every strategy and raise
        TimeoutError instead of letting the assertion run. Use a plain
        Playwright locator for those checks, not a HealingLocator.

    Parameters
    ----------
    page          : the Playwright Page instance.
    primary       : the normal locator you would have used before healing.
    fallbacks     : ordered list of alternative locators.
    name          : human-readable name shown in logs and the heal report.
    heal_timeout  : ms to wait per strategy before trying the next one.
                    Keep this low (≤1500ms) so test speed is not affected.
    """

    def __init__(
        self,
        page: Page,
        primary: Locator,
        fallbacks: list[Locator],
        name: str = "",
        heal_timeout: int = 1500,
    ):
        self._page = page
        self._primary = primary
        self._fallbacks = fallbacks
        self._name = name
        self._heal_timeout = heal_timeout
        self._resolved: Locator | None = None

    # ── Resolution ────────────────────────────────────────────────────────────

    def _resolve(self) -> Locator:
        """
        Walk through [primary] + fallbacks and return the first locator whose
        element is attached to the DOM within heal_timeout ms.

        The winning locator is cached for the lifetime of this instance (one
        page object ≈ one test): Playwright locators are lazy and re-query the
        DOM on every action, so caching only skips repeated strategy probing —
        it does not pin a stale element. This avoids re-paying the full
        strategy walk on every attribute access (expect() + click() + … would
        otherwise resolve several times each).
        """
        if self._resolved is not None:
            return self._resolved

        strategies = [self._primary] + self._fallbacks
        for index, locator in enumerate(strategies):
            try:
                # "attached" (exists in DOM) is intentional — the actual
                # interaction method (click / fill / …) handles visibility
                # and scroll automatically, so we just need to confirm the
                # element exists before delegating to it.
                locator.wait_for(state="attached", timeout=self._heal_timeout)
                if index > 0:
                    self._record_heal(index, locator)
                self._resolved = locator
                return locator
            except Exception:
                continue

        raise TimeoutError(
            f"[HealingLocator] '{self._name}': "
            f"all {len(strategies)} strategies exhausted "
            f"(heal_timeout={self._heal_timeout}ms each)"
        )

    def _record_heal(self, strategy_index: int, winning_locator: Locator) -> None:
        """Append a healing event to the session log and emit a warning."""
        entry = {
            "timestamp":       datetime.now().isoformat(timespec="seconds"),
            "name":            self._name,
            "strategy_used":   strategy_index,
            "winning_locator": str(winning_locator),
            "action":          "primary failed — update this selector",
        }
        _heal_log.append(entry)
        logger.warning(
            "⚕️  HEALED  [%-35s]  primary failed → strategy #%d: %s",
            self._name,
            strategy_index,
            winning_locator,
        )

    # ── Transparent proxy ─────────────────────────────────────────────────────

    @property
    def __class__(self):
        """
        Report ourselves as a Playwright Locator to isinstance() checks.
        Python's isinstance() reads obj.__class__ when type(obj) doesn't match,
        so this makes expect(healing_locator) pass Playwright's type guard and
        forward assertion calls through __getattr__ to the resolved locator.
        """
        return _LOCATOR_CLASS

    def __getattr__(self, attr: str):
        """
        Forward every Locator method or property to the resolved locator.
        This makes HealingLocator a drop-in replacement — page objects do not
        need to change their interaction code at all.
        """
        # Guard against infinite recursion: __getattr__ only fires for missing
        # attributes. If one of OUR OWN internals is accessed before __init__
        # has set it (copy, pickle, partially-built instance), resolving here
        # would re-enter __getattr__ for _primary/_resolved/… forever. Block
        # only those names — everything else (including Playwright's own
        # private attrs like _impl_obj, which expect() reads) must forward to
        # the resolved locator.
        if attr in _OWN_ATTRS:
            raise AttributeError(attr)
        return getattr(self._resolve(), attr)

    def __repr__(self) -> str:
        return (
            f"HealingLocator(name={self._name!r}, "
            f"strategies={1 + len(self._fallbacks)})"
        )
