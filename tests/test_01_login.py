import allure
import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from config.config import LOGIN_MOBILE, LOGIN_OTP, BASE_URL


@allure.feature("Login")
class TestLogin:

    @allure.story("Page loads correctly")
    @allure.severity(allure.severity_level.MINOR)
    def test_login_page_loads(self, page: Page):
        """Login page renders the mobile input and submit button."""
        login_page = LoginPage(page)
        login_page.open()
        expect(login_page.mobile_input).to_be_visible()
        expect(login_page.submit_button).to_be_visible()

    @allure.story("Cannot submit with empty mobile")
    @allure.severity(allure.severity_level.NORMAL)
    def test_submit_without_mobile(self, page: Page):
        """Submitting with empty mobile should not proceed to OTP screen."""
        login_page = LoginPage(page)
        login_page.open()
        login_page.submit_mobile()
        expect(login_page.otp_input).not_to_be_visible()

    @allure.story("Wrong OTP is rejected, correct OTP logs in")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_login_rejects_wrong_otp_then_succeeds(self, page: Page):
        """A single OTP session: a wrong OTP is rejected (stays on the login
        screen), then the correct OTP logs in and reaches the dashboard.

        Wrong-OTP and successful-login are combined into one flow on purpose —
        each mobile submit sends a fresh OTP with a re-send cooldown, so two
        separate OTP-sending tests back-to-back would rate-limit each other."""
        login_page = LoginPage(page)
        login_page.open()
        login_page.enter_mobile(LOGIN_MOBILE)
        login_page.submit_mobile()
        # Wrong OTP → rejected, still on the login screen.
        login_page.enter_otp("000000")
        login_page.verify_otp()
        page.wait_for_timeout(3000)
        expect(login_page.verify_button).to_be_visible()
        expect(page).not_to_have_url("https://pre-saathi.ambak.com/saathi-dashboard")
        # Correct OTP (same session) → logged in.
        login_page.otp_input.fill(LOGIN_OTP)
        login_page.verify_otp()
        expect(page).to_have_url("https://pre-saathi.ambak.com/saathi-dashboard")
        page.context.storage_state(path="auth_state.json")

    @allure.story("Protected page reachable without a session")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="direct nav to a protected route without a session should redirect to /login, but the SPA shell renders in place", strict=True)
    def test_direct_navigation_to_protected_page_without_session_bug(self, page: Page):
        """BUG: direct navigation to /my-account-profile with no session should
        redirect to the login page, but the SPA shell renders in place instead.

        Uses the `page` fixture (an unauthenticated fresh context, same as a
        manually built one) instead of building its own context from `browser`
        — a manually built context is closed in this test's own `finally`,
        which runs BEFORE pytest_runtest_makereport's failure-screenshot hook
        ever sees it, so this test previously produced no screenshot at all.
        `page`'s context outlives the hook."""
        protected_url = BASE_URL.rstrip("/") + "/my-account-profile"
        page.goto(protected_url, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        assert "login" in page.url, (
            f"Expected an unauthenticated visit to redirect to login, "
            f"but stayed at {page.url}"
        )
