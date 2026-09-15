import re
import time
import allure
from datetime import datetime, timedelta
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.constants import MoveToLogin as Msg


class MoveToLoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.loan_amount_input = page.get_by_role("textbox", name="₹")
        self.login_date_input = page.locator("input[name='loginDate']")
        self.login_id_input = page.get_by_role("textbox", name="Enter Login ID")
        self.request_confirmation_button = page.get_by_role("button", name="Request Confirmation")
        self.send_now_button = page.get_by_role("button", name="Send Now")
        self.success_toast = page.get_by_text(Msg.SUCCESS, exact=True)
        self.toast_bodies = page.locator("[class*='Toastify__toast-body']")

        # Validation error toasts
        self.error_toast_loan_amount = page.get_by_text(Msg.ERROR_LOAN_AMOUNT, exact=True)
        self.error_toast_date        = page.get_by_text(Msg.ERROR_DATE, exact=True)
        self.error_toast_login_id    = page.get_by_text(Msg.ERROR_LOGIN_ID, exact=True)
        self.error_toast_bank        = page.get_by_text(Msg.ERROR_BANK, exact=True)
        self.error_toast_branch      = page.get_by_text(Msg.ERROR_BRANCH, exact=True)
        self.error_toast_banker      = page.get_by_text(Msg.ERROR_BANKER, exact=True)

        # Populated by _submit() with every toast text seen during the submit
        # poll (even ones that appeared and auto-dismissed within the window),
        # so a caller/report can see *why* a submit was rejected.
        self.last_submit_toasts: set = set()

    def _day_button_label(self, dt: datetime) -> str:
        day = dt.day
        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return f"Choose {dt.strftime('%A')}, {dt.strftime('%B')} {day}{suffix},"

    def _is_empty(self, placeholder: str) -> bool:
        return self.page.get_by_text(placeholder, exact=True).is_visible()

    def _wait_calendar_open(self):
        """Give the date picker a moment to render after the input is clicked.
        A fixed delay is used deliberately: this picker exposes no reliable
        DOM signal that is always present on open (the month-navigation arrows
        only appear/are-named consistently when navigation is possible, so
        waiting on them breaks for current-month/today selections)."""
        self.page.wait_for_timeout(400)

    def _error_toasts(self) -> list:
        """The known validation-error toasts for this form. Subclasses (e.g.
        MoveToSanctionPage, MoveToDisbursePage) MUST override this to return
        their own locators — inheriting the login ones means a stage-specific
        error can never be recognised, and _submit() falls through to raising
        an unhelpful timeout instead of reporting the real toast text."""
        return [
            self.error_toast_loan_amount, self.error_toast_date, self.error_toast_login_id,
            self.error_toast_bank, self.error_toast_branch, self.error_toast_banker,
        ]

    def _success_indicators(self) -> list:
        """The signal(s) that this form's submission has FULLY completed, used
        to end the post-'Send Now' poll early. Confirmed live: for Move To
        Login/Sanction, the 'Email sent successfully' toast is sent only AFTER
        the underlying lead update succeeds, so it's a reliable trailing
        signal. MoveToDisbursePage overrides this — that same toast fires
        there as a generic email-confirmation step even when the disbursement
        itself is later rejected (e.g. amount exceeds sanction), so treating
        it as "done" there would exit before the real rejection toast ever
        renders."""
        return [self.success_toast]

    def _collect_and_check_error(self, error_toasts: list) -> bool:
        """Poll-body helper: accumulate any visible toast text into
        last_submit_toasts, and return True if a recognised error toast is
        currently visible."""
        try:
            for text in self.toast_bodies.all_text_contents():
                if text:
                    self.last_submit_toasts.add(text)
        except Exception:
            pass
        for toast in error_toasts:
            if toast.is_visible():
                # Not every validation message on every form renders inside a
                # [class*='Toastify__toast-body'] container (some are inline
                # messages, not react-toastify toasts) — the generic scan
                # above can miss them, so also capture the matched locator's
                # own text directly.
                try:
                    self.last_submit_toasts.add(toast.inner_text())
                except Exception:
                    pass
                return True
        return False

    def _submit(self):
        self.last_submit_toasts = set()
        self.request_confirmation_button.click()
        # Two different outcomes race here: a validation error toast (shown
        # immediately, then auto-dismissed after a few seconds) or the "Login
        # Confirmation Required" modal (which can take longer than a couple of
        # seconds to render its email preview). Poll for whichever comes first
        # instead of committing to one fixed wait — waiting the full modal
        # timeout on a validation-error run lets the toast vanish before the
        # caller's assertion ever sees it.
        error_toasts = self._error_toasts()
        deadline = time.monotonic() + 10
        modal_appeared = False
        while time.monotonic() < deadline:
            if self._collect_and_check_error(error_toasts):
                return "error"
            if self.send_now_button.is_visible():
                self.send_now_button.click()
                modal_appeared = True
                break
            self.page.wait_for_timeout(200)
        if not modal_appeared:
            if self.last_submit_toasts:
                raise AssertionError(
                    f"Move To Login submit: no confirmation modal or recognised "
                    f"error toast appeared within 10s, but these toasts were "
                    f"seen — a new Msg.ERROR_* constant + _error_toasts() entry "
                    f"is probably needed: {self.last_submit_toasts}"
                )
            raise AssertionError(
                "Move To Login submit: no confirmation modal appeared and no "
                "toast of any kind was seen within 10s after clicking Request "
                "Confirmation."
            )
        # Confirmed live on 2026-08-18: some validation (e.g. an invalid
        # Sanction ID format) is only enforced at this final "Send Now" commit
        # step, not at "Request Confirmation" — a caller that stopped polling
        # the instant the modal was dismissed would never see that error toast.
        # Exit the moment EITHER outcome appears rather than always waiting
        # the full window — the success toast itself auto-dismisses within a
        # few seconds, and a caller's own expect(success_toast) runs right
        # after this returns, so lingering here after success already showed
        # risks making that check race the toast's own dismissal instead.
        post_deadline = time.monotonic() + 8
        success_indicators = self._success_indicators()
        while time.monotonic() < post_deadline:
            if self._collect_and_check_error(error_toasts):
                return "error"
            if any(s.is_visible() for s in success_indicators):
                return "submitted"
            self.page.wait_for_timeout(200)
        return "submitted"

    @allure.step("Fill loan amount: {amount}")
    def fill_loan_amount(self, amount: str, attempts: int = 3):
        # Retries the whole clear+type sequence rather than typing once: on a
        # just-created lead, opening this form can still be settling an async
        # re-render shortly after load (the same class of race
        # fill_and_submit's Balance-Transfer wait already works around on the
        # Disburse form) — confirmed live and reproducible, typing here too
        # soon lets that re-render reset the field mid-keystroke and drop the
        # leading digit(s) (e.g. '2000000' -> '000000'). A short settle wait
        # before the first attempt, plus retrying on a mismatch, clears it.
        expected_digits = self.digits_only(amount)
        actual_digits = None
        for attempt in range(attempts):
            if attempt == 0:
                self.page.wait_for_timeout(500)
            self.loan_amount_input.click()
            self.loan_amount_input.press("End")
            # Delete any pre-filled value character by character from the end.
            # Ctrl+A + single Backspace is unreliable when the field has an existing
            # value (cursor lands at position 0, Backspace does nothing, then
            # press_sequentially inserts into the old value).
            for _ in range(15):
                self.loan_amount_input.press("Backspace")
            self.loan_amount_input.press_sequentially(amount, delay=100)
            # Unlike fill_disbursed_id / fill_login_id, this field re-renders through
            # the same Indian lakh/crore grouping mask documented in
            # LeadDetailPage.get_sanction_amount() (e.g. '999999999' displays as
            # '99,99,99,999'), so _assert_filled()'s exact string compare would
            # false-fail here — compare digits instead.
            actual_digits = self.digits_only(self.loan_amount_input.input_value())
            if actual_digits == expected_digits:
                return
            if attempt < attempts - 1:
                self.page.wait_for_timeout(500)
        raise AssertionError(
            f"Loan Amount: expected digits {expected_digits!r} after fill, got "
            f"{actual_digits!r} after {attempts} attempts (the field's input "
            f"mask likely rejected part of the value)"
        )

    def _pick_date(self, date_input, date_str: str = None):
        target = datetime.now()
        if date_str:
            try:
                target = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                pass  # unparseable — fall back to today

        date_input.click()
        self._wait_calendar_open()

        today = datetime.now()
        months_diff = (target.year - today.year) * 12 + (target.month - today.month)
        nav = "Next Month" if months_diff > 0 else "Previous Month"
        for _ in range(abs(months_diff)):
            self.page.get_by_role("button", name=nav).click()

        self.page.get_by_role("button", name=self._day_button_label(target)).click()

    def is_calendar_date_disabled(self, date_input, target_date: datetime) -> bool:
        """Open the calendar for date_input and return whether target_date's button is disabled."""
        date_input.click()
        self._wait_calendar_open()

        today = datetime.now()
        months_diff = (target_date.year - today.year) * 12 + (target_date.month - today.month)
        nav = "Next Month" if months_diff > 0 else "Previous Month"
        for _ in range(abs(months_diff)):
            nav_button = self.page.get_by_role("button", name=nav)
            # When the target month is outside the calendar's selectable range,
            # react-datepicker removes (or disables) the month-navigation arrow —
            # e.g. the whole previous month is before the min date. The month is
            # then unreachable, so target_date is disabled by definition.
            if nav_button.count() == 0 or nav_button.is_disabled():
                self._close_calendar()
                return True
            # click() auto-waits for the arrow to be actionable and the month to
            # advance synchronously, so no fixed delay is needed between hops.
            nav_button.first.click()

        # NOTE: when target_date is disabled, react-datepicker does not render a
        # "Choose <day>…" button (disabled days are relabeled "Not available
        # …"), so this locator matches nothing and is_disabled() blocks for the
        # full default timeout before the except path returns True. That ~45s
        # wait is the dominant cost of this test. Fixing it properly needs the
        # real disabled-day selector (e.g. the "Not available …" name or the
        # react-datepicker--disabled class) confirmed against the live DOM —
        # left as-is here to avoid changing the test's pass/fail behavior.
        btn = self.page.get_by_role("button", name=self._day_button_label(target_date))
        try:
            disabled = btn.is_disabled()
        except Exception:
            disabled = True  # not rendered as a selectable "Choose" button → disabled

        self._close_calendar()
        return disabled

    def _close_calendar(self):
        """Dismiss the open date picker. Best-effort cleanup only — the target
        tab can be torn down around this point, so a closed-page error here must
        not fail the test (it previously surfaced as a flaky TargetClosedError)."""
        try:
            self.page.keyboard.press("Escape")
        except Exception:
            pass

    @allure.step("Select date")
    def select_today_date(self, date_str: str = None):
        self._pick_date(self.login_date_input, date_str)

    @allure.step("Select bank: {bank_name}")
    def select_bank(self, search: str, bank_name: str):
        self.page.get_by_text("Select Bank", exact=True).click()
        modal = self.page.locator("[class*='selectOptionsModal_selectOptionsContent']")
        modal.wait_for(state="visible")
        modal.get_by_role("textbox", name="Search by bank name...").fill(search)
        # The option click below auto-waits for the filtered result to appear,
        # so no fixed delay after typing the search term is needed.
        modal.locator("[class*='selectOptionsModal_optionLabel']", has_text=bank_name).click()
        modal.wait_for(state="hidden")

    def _placeholder_trigger(self, trigger_text: str):
        """The clickable field placeholder that opens a selectOptionsModal.
        Anchored to the placeholder <span> rather than get_by_text, because
        optional fields (e.g. RSM) render the same text in both the <label> and
        the placeholder <span>, which makes an exact get_by_text match ambiguous
        (strict-mode violation). Mandatory fields carry a '*' in the label, so
        only their placeholder matched before — this makes all fields robust."""
        return self.page.locator("[class*='updateStatusForm_placeholder']").filter(
            has_text=re.compile(rf"^{re.escape(trigger_text)}$")
        )

    def _select_from_modal(self, trigger_text: str, option: str, search: str = None):
        """Open a selectOptionsModal by clicking trigger_text, then pick an option."""
        self._placeholder_trigger(trigger_text).click()
        modal = self.page.locator("[class*='selectOptionsModal_selectOptionsContent']")
        modal.wait_for(state="visible")
        search_input = modal.locator("input[class*='selectOptionsModal_searchInput']")
        if search and search_input.count() and search_input.is_visible():
            search_input.fill(search)
        # The option click auto-waits for the filtered result, so the previous
        # fixed delay after typing the search term is unnecessary.
        opt = modal.get_by_text(option, exact=True).first
        opt.scroll_into_view_if_needed()
        # Some option lists (e.g. RSM) render the row inside a scroll container
        # that intercepts the pointer at the option's centre even once it is
        # visible and stable; force past the interceptor to click the option.
        opt.click(force=True)
        modal.wait_for(state="hidden")

    def _select_first_enabled_option(self, trigger_text: str):
        """Select the first available value from a dependent-field drawer.

        Banker and branch availability is determined by the currently selected
        bank and by the signed-in user's permissions.  Their values must not be
        hard-coded in test data: a valid option today can disappear tomorrow.
        """
        self._placeholder_trigger(trigger_text).click()
        modal = self.page.locator("[class*='selectOptionsModal_selectOptionsContent']")
        modal.wait_for(state="visible")
        # Banker and Branch have different row markup. Selecting a banker can
        # also auto-map a branch, highlighted in the drawer as the suggested
        # row — but merely dismissing the drawer leaves the outer "Select
        # Branch" field empty (the highlight is a suggestion, not a committed
        # selection), so that mapped row still needs an explicit click.
        if trigger_text == "Select Branch":
            selected_branch = modal.locator("[class*='selectOptionsModal_branchItemSelected']")
            if selected_branch.count() and selected_branch.first.is_visible():
                selected_branch.first.scroll_into_view_if_needed()
                selected_branch.first.click(force=True)
                modal.wait_for(state="hidden")
                return
            row_class = "selectOptionsModal_branchItem"
        else:
            row_class = "selectOptionsModal_bankerItem"
        option = modal.locator(
            f"[class*='{row_class}']:not([aria-disabled='true']):not([disabled])"
        ).first
        option.wait_for(state="visible")
        option.scroll_into_view_if_needed()
        option.click(force=True)
        modal.wait_for(state="hidden")

    @allure.step("Select first available branch")
    def select_branch(self, branch: str = None):
        self._select_first_enabled_option("Select Branch")

    @allure.step("Select first available banker")
    def select_banker(self, banker: str = None):
        self._select_first_enabled_option("Select Banker")

    @allure.step("Select first available RSM")
    def select_rsm(self, rsm: str = None):
        # RSM is optional (no asterisk on the form). Same selectOptionsModal
        # pattern as Bank/Banker/Branch: available RSMs depend on the selected
        # bank and are not stable test data (a valid person today can disappear
        # tomorrow), so pick the first enabled option rather than searching for
        # a hard-coded name. One twist: when the current lead's RSM is already
        # assigned, their row renders disabled ("Selected as RSM") and cannot be
        # re-clicked (the modal would never close) — skip disabled rows, and if
        # none are enabled, that already-satisfied state just needs the modal
        # closed.
        self._placeholder_trigger("Select RSM").click()
        modal = self.page.locator("[class*='selectOptionsModal_selectOptionsContent']")
        modal.wait_for(state="visible")
        row = modal.locator(
            "[class*='selectOptionsModal_optionItem']"
            ":not([aria-disabled='true']):not([disabled]):not([class*='Disabled'])"
        ).first
        if not row.count():
            # This is a right-side drawer with no close control; clicking the
            # backdrop (top-left, clear of the drawer) dismisses it. Escape does
            # not close it.
            self.page.mouse.click(5, 5)
            modal.wait_for(state="hidden")
            return
        row.scroll_into_view_if_needed()
        row.click(force=True)
        modal.wait_for(state="hidden")

    @allure.step("Fill login ID")
    def fill_login_id(self, login_id: str):
        self.login_id_input.click()
        self.login_id_input.fill(login_id)
        self._assert_filled(self.login_id_input, login_id, "Login ID")

    @allure.step("Fill and submit Move To Login form")
    def fill_and_submit(self, data: dict):
        if data.get("loan_amount"):
            self.fill_loan_amount(data["loan_amount"])
        if data.get("select_date", True):
            self.select_today_date(data.get("login_date") or None)
        bank_selected = False
        if data.get("bank_search"):
            self.select_bank(data["bank_search"], data["bank_name"])
            bank_selected = True
        if bank_selected:
            banker_selected = False
            if data.get("banker"):
                self.page.get_by_text("Select Banker", exact=True).wait_for(state="visible", timeout=5000)
                self.select_banker(data["banker"])
                banker_selected = True
            branch_selected = False
            if banker_selected and data.get("branch"):
                self.page.get_by_text("Select Branch", exact=True).wait_for(state="visible", timeout=5000)
                self.select_branch(data["branch"])
                branch_selected = True
            # RSM is optional — select it only when provided.
            if branch_selected and data.get("rsm"):
                self._placeholder_trigger("Select RSM").wait_for(state="visible", timeout=5000)
                self.select_rsm(data["rsm"])
            if branch_selected and data.get("login_id"):
                self.fill_login_id(data["login_id"])
        self._submit()
