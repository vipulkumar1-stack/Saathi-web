import allure
import pytest
from playwright.sync_api import Page, expect
from pages.website_settings_page import WebsiteSettingsPage
from config.constants import WebsiteSettings as Msg


@allure.feature("Website Settings")
class TestWebsiteSettings:
    """Website Settings CMS — a multi-section editor for the public marketing
    site. Each section has its own Save Changes button that emits a
    '<Section> section updated successfully' toast.

    Save tests re-save a section's current content (no content is altered).
    Add-item tests add a row without saving, so nothing is persisted."""

    def _open(self, logged_in_page: Page) -> WebsiteSettingsPage:
        page_obj = WebsiteSettingsPage(logged_in_page)
        page_obj.go_to_my_tools()
        page_obj.open_tool()
        return page_obj

    @allure.story("Website Settings loads with all sections")
    @allure.severity(allure.severity_level.NORMAL)
    def test_website_settings_page_loads(self, logged_in_page: Page):
        """All nine editor sections render on the page."""
        web = self._open(logged_in_page)
        for section in Msg.SECTIONS:
            expect(web.section_heading(section)).to_be_visible()

    @allure.story("Every section has a Save Changes button")
    @allure.severity(allure.severity_level.NORMAL)
    def test_all_sections_have_save_buttons(self, logged_in_page: Page):
        """There is one Save Changes button per section (nine total)."""
        web = self._open(logged_in_page)
        assert web.save_buttons.count() == len(Msg.SECTIONS)

    @allure.story("Save Header section")
    @allure.severity(allure.severity_level.NORMAL)
    def test_save_header_section(self, logged_in_page: Page):
        """Saving the Header section shows its success toast."""
        web = self._open(logged_in_page)
        web.save_section("Header")
        expect(web.toast(Msg.HEADER_SUCCESS)).to_be_visible()

    @allure.story("Save Hero section")
    @allure.severity(allure.severity_level.NORMAL)
    def test_save_hero_section(self, logged_in_page: Page):
        """Saving the Hero Section shows its success toast."""
        web = self._open(logged_in_page)
        web.save_section("Hero Section")
        expect(web.toast(Msg.HERO_SUCCESS)).to_be_visible()

    @allure.story("Save Testimonials section")
    @allure.severity(allure.severity_level.NORMAL)
    def test_save_testimonials_section(self, logged_in_page: Page):
        """Saving the Testimonials section shows a success toast."""
        web = self._open(logged_in_page)
        web.save_section("Testimonials")
        expect(web.toast(Msg.SAVE_SUCCESS)).to_be_visible()

    @allure.story("Save Calculator section")
    @allure.severity(allure.severity_level.NORMAL)
    def test_save_calculator_section(self, logged_in_page: Page):
        """Saving the Calculator Section shows a success toast."""
        web = self._open(logged_in_page)
        web.save_section("Calculator Section")
        expect(web.toast(Msg.SAVE_SUCCESS)).to_be_visible()

    @allure.story("Save FAQs section")
    @allure.severity(allure.severity_level.NORMAL)
    def test_save_faq_section(self, logged_in_page: Page):
        """Saving the FAQs section shows its success toast."""
        web = self._open(logged_in_page)
        web.save_section("FAQs")
        expect(web.toast(Msg.FAQ_SUCCESS)).to_be_visible()

    @allure.story("Edit and re-save the hero heading")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_edit_hero_heading_and_save(self, logged_in_page: Page):
        """Re-entering the hero heading and saving persists successfully.
        (Re-fills the existing value, so the live content is unchanged.)"""
        web = self._open(logged_in_page)
        current = web.hero_heading_input.first.input_value()
        web.hero_heading_input.first.fill(current)
        web.save_section("Hero Section")
        expect(web.toast(Msg.HERO_SUCCESS)).to_be_visible()

    @allure.story("Add a feature row")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_feature_adds_row(self, logged_in_page: Page):
        """Clicking '+ Add Feature' adds a new feature input."""
        web = self._open(logged_in_page)
        before = web.feature_inputs.count()
        web.add_feature()
        expect(web.feature_inputs).to_have_count(before + 1)

    @allure.story("Add an FAQ block")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_faq_block(self, logged_in_page: Page):
        """Clicking '+ Add FAQ' adds inputs to the page (a new FAQ block)."""
        web = self._open(logged_in_page)
        before = web.page.locator("input, textarea").count()
        web.add_faq()
        web.page.wait_for_timeout(800)
        assert web.page.locator("input, textarea").count() > before
