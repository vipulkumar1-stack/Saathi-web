import re
import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.constants import WebsiteSettings as Msg


class WebsiteSettingsPage(BasePage):
    """Website Settings CMS (/website-settings).

    Opened from My Tools via the "Website Settings" card. A single page editor
    for the public marketing site, split into sections (Header, Hero, Services,
    Testimonials, FAQs, ...), each with its own "Save Changes" button that emits
    a "<Section> section updated successfully" toast.

    Section Save buttons share a common wrapper, so a section is targeted by the
    FIRST "Save Changes" button that follows its heading in the DOM — robust to
    section reordering, unlike a positional index.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.check_now_button = (
            page.locator("div")
            .filter(has=page.get_by_text("Website Settings", exact=True))
            .filter(has=page.get_by_role("button", name="Check Now"))
            .last
            .get_by_role("button", name="Check Now")
        )
        self.save_buttons     = page.get_by_role("button", name=re.compile("Save Changes"))
        self.hero_heading_input = page.get_by_placeholder("Enter heading text")
        self.feature_inputs   = page.get_by_placeholder("Enter feature")
        self.add_feature_button     = page.get_by_role("button", name="+ Add Feature")
        self.add_faq_button         = page.get_by_role("button", name="+ Add FAQ")
        self.add_testimonial_button = page.get_by_role("button", name="+ Add Testimonial")
        self.add_statistic_button   = page.get_by_role("button", name="+ Add Statistic")

    # ── helpers ─────────────────────────────────────────────────────────────
    def toast(self, text: str):
        return self.page.locator("[class*='Toastify__toast-body']").filter(has_text=text)

    def section_heading(self, name: str):
        return self.page.get_by_role("heading", name=name, exact=True)

    def _section_save(self, heading: str):
        """First 'Save Changes' button that follows the given section heading."""
        return self.page.locator(
            "xpath=(//*[normalize-space(text())="
            f"{heading!r}]/following::button[normalize-space()='Save Changes'])[1]"
        )

    # ── navigation ──────────────────────────────────────────────────────────
    @allure.step("Navigate to My Tools")
    def go_to_my_tools(self):
        self.page.get_by_role("link", name="tools My Tools").click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Open Website Settings tool")
    def open_tool(self):
        self.check_now_button.wait_for(state="visible")
        self.check_now_button.click()
        self.save_buttons.first.wait_for(state="visible")

    # ── actions ─────────────────────────────────────────────────────────────
    @allure.step("Save the '{heading}' section")
    def save_section(self, heading: str):
        btn = self._section_save(heading)
        btn.scroll_into_view_if_needed()
        btn.click()

    @allure.step("Add a feature row")
    def add_feature(self):
        self.add_feature_button.first.click()

    @allure.step("Add an FAQ block")
    def add_faq(self):
        self.add_faq_button.first.click()

    @allure.step("Add a testimonial block")
    def add_testimonial(self):
        self.add_testimonial_button.first.click()

    @allure.step("Add a statistic block")
    def add_statistic(self):
        self.add_statistic_button.first.click()
