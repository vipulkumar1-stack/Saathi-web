import allure
import pytest
from playwright.sync_api import Page, expect
from pages.profile_page import ProfilePage


@allure.feature("Profile")
class TestProfile:
    """Partner profile page (/my-account-profile). View + tab coverage.

    NOTE: 'Save and Next' stays disabled through automated field edits (a
    controlled-form quirk in the app), so an edit-and-save happy-path isn't
    reliably automatable — these cover the page, its tabs and its fields."""

    @allure.story("Profile page loads")
    @allure.severity(allure.severity_level.NORMAL)
    def test_profile_page_loads(self, logged_in_page: Page):
        """The profile page shows the Basic Details tab and Save and Next."""
        profile = ProfilePage(logged_in_page)
        profile.open()
        expect(profile.basic_details_tab).to_be_visible()
        expect(profile.save_and_next_button).to_be_visible()

    @allure.story("Basic Details fields are shown")
    @allure.severity(allure.severity_level.NORMAL)
    def test_basic_details_fields(self, logged_in_page: Page):
        """Basic Details shows the partner's company/SPOC/pincode fields."""
        profile = ProfilePage(logged_in_page)
        profile.open()
        expect(profile.company_mobile).to_be_visible()
        expect(profile.spoc_name).to_be_visible()
        expect(profile.pincode).to_be_visible()

    @allure.story("Profile tabs are present")
    @allure.severity(allure.severity_level.NORMAL)
    def test_profile_tabs_present(self, logged_in_page: Page):
        """The profile page exposes Basic Details, KYC Documents and Bank Details tabs."""
        profile = ProfilePage(logged_in_page)
        profile.open()
        expect(profile.basic_details_tab).to_be_visible()
        expect(profile.kyc_documents_tab).to_be_visible()
        expect(profile.bank_details_tab).to_be_visible()

    @allure.story("KYC Documents tab opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_kyc_documents_tab_opens(self, logged_in_page: Page):
        """The KYC Documents tab can be opened."""
        profile = ProfilePage(logged_in_page)
        profile.open()
        profile.open_kyc_tab()
        expect(profile.kyc_documents_tab).to_be_visible()

    @allure.story("Pin Code field rejects non-numeric input")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="the Pin Code field should filter/validate non-numeric characters, but it accepts them verbatim", strict=True)
    def test_pincode_rejects_non_numeric_bug(self, logged_in_page: Page):
        """BUG: the Pin Code field accepts non-numeric characters verbatim instead of filtering/validating them."""
        profile = ProfilePage(logged_in_page)
        profile.open()
        profile.pincode.click()
        profile.pincode.fill("abcXYZ!!")
        profile.spoc_name.click()  # blur the pincode field
        value = profile.pincode.input_value()
        has_validation_error = profile.page.get_by_text("valid", exact=False).count() > 0
        assert has_validation_error or not any(c.isalpha() or not c.isalnum() for c in value), (
            f"Pin Code accepted non-numeric input verbatim: {value!r}"
        )

    @allure.story("SPOC Name field is safe against script injection")
    @allure.severity(allure.severity_level.NORMAL)
    def test_spoc_name_xss_is_safe(self, logged_in_page: Page):
        """Entering a script payload into SPOC Name does not execute and raises no page error."""
        profile = ProfilePage(logged_in_page)
        profile.open()
        page_errors = []
        profile.page.on("pageerror", lambda err: page_errors.append(err))
        payload = "<script>window.__xss_probe=true</script>"
        profile.spoc_name.click()
        profile.spoc_name.fill(payload)
        profile.pincode.click()  # blur the spoc_name field
        probe = profile.page.evaluate("window.__xss_probe")
        assert not probe, "XSS payload executed: window.__xss_probe was set"
        assert not page_errors, f"Unexpected page error(s): {page_errors}"
