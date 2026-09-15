import allure
import pytest
from playwright.sync_api import Page, expect
from pages.profile_page import ProfilePage


@allure.feature("Logout")
class TestLogout:
    """Logout — deliberately the LAST test in the suite so that, if the server
    revokes the session on logout, no later test is affected. Logout lives on the
    profile page."""

    @allure.story("Logout returns the user to the login screen")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_logout_redirects_to_login(self, logged_in_page: Page):
        """Clicking Logout ends the session and shows the login page."""
        profile = ProfilePage(logged_in_page)
        profile.open()
        profile.logout()
        logged_in_page.wait_for_timeout(3000)
        # Back on the login screen: the mobile input is shown again.
        expect(
            logged_in_page.get_by_role("textbox", name="Mobile or Email *")
        ).to_be_visible()
