import allure
import pytest
from playwright.sync_api import Page, expect
from pages.add_role_page import AddRolePage
from config.config import ROLE_DATA
from utils.data_helper import generate_role_data


@allure.feature("Add Role")
class TestAddRole:

    def _open_form(self, logged_in_page: Page) -> AddRolePage:
        page_obj = AddRolePage(logged_in_page)
        page_obj.go_to_my_tools()
        page_obj.open_role_management()
        page_obj.open_add_role_form()
        return page_obj

    @allure.story("Validation: Role name is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_role_without_name(self, logged_in_page: Page):
        """Submitting the form without a role name should not show a success message."""
        form = self._open_form(logged_in_page)
        form.fill_description(ROLE_DATA["description"])
        form.select_permissions()
        form.submit_button.click()
        expect(form.role_name_input).to_be_visible()  # still on the form — name field visible

    @allure.story("Validation: Description is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_role_without_description(self, logged_in_page: Page):
        """Submitting the form without a description should not navigate away from the form."""
        form = self._open_form(logged_in_page)
        data = generate_role_data()
        form.fill_role_name(data["name"])
        form.select_permissions()
        form.submit_button.click()
        expect(form.role_name_input).to_be_visible()  # still on the form — name field visible

    @allure.story("Role added successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_add_role_successfully(self, logged_in_page: Page):
        """Filling all fields and submitting should show a success message."""
        data = generate_role_data()
        form = self._open_form(logged_in_page)
        form.fill_and_submit(data)
        expect(form.roles_list_heading).to_be_visible()

    @allure.story("Bug: Duplicate role names are not rejected")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="creating a role with a name that already exists should be rejected, but the app has no uniqueness check and creates a second row sharing the name", strict=True)
    def test_duplicate_role_name_rejected_bug(self, logged_in_page: Page):
        """Documents a bug: creating a second role with a name that already
        exists should be rejected, but the app has no uniqueness check and
        happily creates a second role sharing the same name."""
        data = generate_role_data()
        form = self._open_form(logged_in_page)
        form.fill_and_submit(data)
        expect(form.roles_list_heading).to_be_visible()

        dup_data = {**generate_role_data(), "name": data["name"]}
        form.open_add_role_form()
        form.fill_and_submit(dup_data)
        expect(form.roles_list_heading).to_be_visible()
        # Let the list finish rendering the newly-created row before counting —
        # checking immediately can catch the count still at 1 a moment before
        # the duplicate row appears, passing this test for the wrong reason.
        logged_in_page.wait_for_timeout(3000)
        # Bug: the list now has two rows sharing this name instead of one.
        assert form.roles_list_rows_named(data["name"]).count() == 1

    @allure.story("Bug: Roles can be created with zero permissions")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="submitting Add Role with no permission selected should be blocked, but the app creates an active role with zero permissions", strict=True)
    def test_role_with_no_permissions_rejected_bug(self, logged_in_page: Page):
        """Documents a bug: submitting Add Role with a valid name and
        description but no permission selected should be blocked, but the app
        happily creates an active role with zero permissions."""
        data = generate_role_data()
        form = self._open_form(logged_in_page)
        form.fill_role_name(data["name"])
        form.fill_description(data["description"])
        # Intentionally skip select_permissions() — no permission is chosen.
        form.submit_button.click()
        # Give the submission time to fully resolve (navigate away or not)
        # before checking — asserting immediately can catch the form still
        # rendered a moment before it closes, passing this test for the wrong
        # reason even though the app actually let the submission through.
        logged_in_page.wait_for_timeout(3000)
        assert form.role_name_input.is_visible()  # still on the form — name field visible
