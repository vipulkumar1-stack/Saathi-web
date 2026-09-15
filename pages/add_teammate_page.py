import re
import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.constants import AddTeammate as Msg


class AddTeammatePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.add_teammate_button = page.get_by_role("button", name="+ Add Teammate")
        self.team_member_role    = page.locator("div").filter(
            has_text=re.compile(r"^Team Member$")
        ).first
        self.full_name_input     = page.get_by_role("textbox", name="Full Name*")
        self.mobile_input        = page.get_by_role("textbox", name="Mobile*")
        self.designation_select  = page.locator("#designation")
        self.submit_button       = page.get_by_role("button", name="Submit")
        self.success_title       = page.get_by_text(Msg.SUCCESS_TITLE, exact=True)
        self.success_message     = page.get_by_text(Msg.SUCCESS_TEAMMATE, exact=True)
        self.go_to_team_list_btn = page.get_by_role("button", name="Go to My Team List")
        # Shown when submitting a mobile number already used by another teammate
        self.mobile_exists_error = self.healing_locator(
            page.get_by_text("Mobile Already Exist", exact=True),
            page.locator("[class*='Toastify__toast-body']").filter(has_text="Mobile Already Exist"),
            name="mobile_exists_error",
        )
        # Either outcome proves the mobile FORMAT was accepted by the form and
        # reached the server: the success modal (number was free) or a
        # "Mobile Already Exist" rejection (a prior run already burned that
        # exact number, but it still passed format validation to get that far).
        # Built from plain locators, not self.mobile_exists_error — that one is
        # a HealingLocator, which resolves eagerly through __getattr__, so
        # chaining .or_() on it would defeat the point of waiting on either.
        self.format_accepted_outcome = (
            page.get_by_text(Msg.SUCCESS_TITLE, exact=True)
            .or_(page.get_by_text("Mobile Already Exist", exact=True))
            .or_(page.locator("[class*='Toastify__toast-body']")
                     .filter(has_text="Mobile Already Exist"))
        )

        # Sourcing Partner form
        self.sourcing_partner_role     = page.locator("div").filter(
            has_text=re.compile(r"^Sourcing Partner$")
        ).first
        self.no_radio                  = page.get_by_role("radio", name="No")
        self.email_input               = page.get_by_role("textbox", name="Email Address*")
        self.success_message_sourcing  = page.get_by_text(Msg.SUCCESS_SOURCING, exact=True)
        self.go_to_sub_partners_btn    = page.get_by_role("button", name="Go to Sub Partners")

    @allure.step("Navigate to My Team page")
    def go_to_my_team(self):
        self.page.get_by_role("link", name="teams My Team").click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Open Add Teammate form")
    def open_form(self):
        self.add_teammate_button.wait_for(state="visible")
        self.add_teammate_button.click()
        self.team_member_role.wait_for(state="visible")
        self.team_member_role.click()

    @allure.step("Fill full name")
    def fill_full_name(self, name: str):
        self.full_name_input.wait_for(state="visible")
        self.full_name_input.fill(name)

    @allure.step("Fill mobile")
    def fill_mobile(self, mobile: str):
        self.mobile_input.fill(mobile)

    @allure.step("Select first designation")
    def select_designation(self):
        self.designation_select.click()
        self.choose_first_option()

    @allure.step("Fill and submit Add Teammate form")
    def fill_and_submit(self, data: dict):
        if data.get("full_name"):
            self.fill_full_name(data["full_name"])
        if data.get("mobile"):
            self.fill_mobile(data["mobile"])
        self.select_designation()
        self.submit_button.click()

    # ── Sourcing Partner ─────────────────────────────────────────────────────

    @allure.step("Open Add Sourcing Partner form")
    def open_sourcing_partner_form(self):
        self.add_teammate_button.wait_for(state="visible")
        self.add_teammate_button.click()
        self.sourcing_partner_role.wait_for(state="visible")
        self.sourcing_partner_role.click()
        self.no_radio.wait_for(state="visible")
        self.no_radio.click()

    @allure.step("Fill email address")
    def fill_email(self, email: str):
        self.email_input.wait_for(state="visible")
        self.email_input.fill(email)

    @allure.step("Fill and submit Add Sourcing Partner form")
    def fill_and_submit_sourcing_partner(self, data: dict):
        if data.get("full_name"):
            self.fill_full_name(data["full_name"])
        if data.get("mobile"):
            self.fill_mobile(data["mobile"])
        if data.get("email"):
            self.fill_email(data["email"])
        # Blur the email field and let the form's validation settle before
        # submitting. fill() alone doesn't always fire the blur/change the React
        # form needs, so an immediate Submit click can no-op against stale state —
        # the form stays open and no success modal ever appears (flaky failure).
        self.email_input.blur()
        self.page.wait_for_timeout(500)
        self.submit_button.click()
