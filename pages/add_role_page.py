import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.constants import AddRole as Msg


class AddRolePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Role management lives behind the "Access Control" tool card on My Tools
        # (formerly the 6th "Check Now" button — a positional .nth(5) that broke when
        # the tool was renamed/reordered). Scope to the card that holds both the
        # "Access Control" title and a "Check Now" button, then click that button.
        self.access_control_card = (
            page.locator("div")
            .filter(has=page.get_by_text("Access Control", exact=True))
            .filter(has=page.get_by_role("button", name="Check Now"))
            .last
        )
        self.check_now_button   = self.access_control_card.get_by_role("button", name="Check Now")
        self.add_role_button    = page.get_by_role("button", name="Add Role")
        self.role_name_input    = page.get_by_placeholder("Enter the name of the role")
        self.description_input  = page.get_by_placeholder("Enter the description of the")
        self.permissions_select = page.locator(".react-select__control")
        self.submit_button      = page.get_by_role("button", name="Submit")
        # After a successful submit the app navigates back to the roles list page
        self.roles_list_heading = page.get_by_text(Msg.ROLES_LIST_HEADING, exact=True)

    @allure.step("Navigate to My Tools")
    def go_to_my_tools(self):
        self.page.get_by_role("link", name="tools My Tools").click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Open Role Management tool")
    def open_role_management(self):
        self.check_now_button.wait_for(state="visible")
        self.check_now_button.click()

    @allure.step("Open Add Role form")
    def open_add_role_form(self):
        self.add_role_button.wait_for(state="visible")
        self.add_role_button.click()
        self.role_name_input.wait_for(state="visible")

    @allure.step("Fill role name")
    def fill_role_name(self, name: str):
        self.role_name_input.click()
        self.role_name_input.fill(name)

    @allure.step("Fill description")
    def fill_description(self, description: str):
        self.description_input.wait_for(state="visible")
        self.description_input.click()
        self.description_input.fill(description)

    @allure.step("Select first available permission")
    def select_permissions(self):
        self.permissions_select.click()
        self.choose_first_option()

    @allure.step("Fill and submit Add Role form")
    def fill_and_submit(self, data: dict):
        self.fill_role_name(data["name"])
        self.fill_description(data["description"])
        self.select_permissions()
        self.submit_button.click()

    def roles_list_rows_named(self, name: str):
        """Rows in the roles list table whose name column exactly matches `name`.
        Used to detect duplicate role names (the app has no uniqueness check)."""
        return self.page.locator("tbody tr").filter(has=self.page.get_by_text(name, exact=True))
