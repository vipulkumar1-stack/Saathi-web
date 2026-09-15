import allure
import pytest
from playwright.sync_api import Page, expect
from pages.edit_columns_page import EditColumnsPage
from pages.advanced_filters_page import AdvancedFiltersPage
from pages.home_page import HomePage


@allure.feature("Edit Columns")
class TestEditColumns:

    @allure.story("Edit Columns panel shows Select Fields and Order Fields sections")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_columns_panel_opens(self, logged_in_page: Page):
        """Clicking Edit Columns should open the panel with both the
        'Select Fields to show' (left) and 'Order Fields' (right) sections visible."""
        panel = EditColumnsPage(logged_in_page)
        panel.open()
        expect(panel.select_fields_heading).to_be_visible()
        expect(panel.order_fields_heading).to_be_visible()


@allure.feature("Advanced Filters")
class TestAdvancedFilters:

    def _open(self, page: Page) -> AdvancedFiltersPage:
        f = AdvancedFiltersPage(page)
        f.open()
        return f

    # ── Individual dropdown tests ──────────────────────────────────────────────

    @allure.story("Source dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_source_dropdown_opens(self, logged_in_page: Page):
        """Clicking the Source filter should open its dropdown."""
        f = self._open(logged_in_page)
        f.source_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Sub Source dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sub_source_dropdown_opens(self, logged_in_page: Page):
        """Sub Source is only enabled after a Source is selected. Select a Source
        option first, then verify the Sub Source dropdown opens."""
        f = self._open(logged_in_page)
        # Step 1: select any Source to unlock Sub Source
        f.source_trigger.click()
        expect(f.dropdown_menu).to_be_visible()
        logged_in_page.locator("[class*='-option']").first.click()
        # Step 2: Sub Source is now enabled
        f.sub_source_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Banks dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_banks_dropdown_opens(self, logged_in_page: Page):
        """Clicking the Banks filter should open its dropdown."""
        f = self._open(logged_in_page)
        f.banks_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Purchase Type dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_purchase_type_dropdown_opens(self, logged_in_page: Page):
        """Clicking the Purchase Type filter should open its dropdown."""
        f = self._open(logged_in_page)
        f.purchase_type_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Product Type dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_type_dropdown_opens(self, logged_in_page: Page):
        """Clicking the Product Type filter should open its dropdown."""
        f = self._open(logged_in_page)
        f.product_type_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Sub Type dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sub_type_dropdown_opens(self, logged_in_page: Page):
        """Clicking the Sub Type filter should open its dropdown."""
        f = self._open(logged_in_page)
        f.sub_type_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Fulfillment dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_fulfillment_dropdown_opens(self, logged_in_page: Page):
        """Clicking the Fulfillment filter should open its dropdown."""
        f = self._open(logged_in_page)
        f.fulfillment_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Cities dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cities_dropdown_opens(self, logged_in_page: Page):
        """Clicking the Cities filter should open its dropdown."""
        f = self._open(logged_in_page)
        f.cities_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Designation dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_designation_dropdown_opens(self, logged_in_page: Page):
        """Clicking the Designation filter should open its dropdown."""
        f = self._open(logged_in_page)
        f.designation_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Teammate: Role then Team Member dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_teammate_dropdown_opens(self, logged_in_page: Page):
        """Selecting a role in the Teammate section should reveal and open
        the Team Member dropdown."""
        f = self._open(logged_in_page)
        # Step 1: open the role/designation picker inside the Teammate section
        f.teammate_role_trigger.click()
        expect(f.dropdown_menu).to_be_visible()
        # Step 2: pick the first available role so Team Member becomes enabled
        logged_in_page.locator("[class*='-option']").first.click()
        # Step 3: verify Team Member dropdown opens
        f.team_member_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Assigned To dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_assigned_to_dropdown_opens(self, logged_in_page: Page):
        """Clicking the Assigned To filter should open its dropdown."""
        f = self._open(logged_in_page)
        f.assigned_to_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Checklist Item dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_checklist_item_dropdown_opens(self, logged_in_page: Page):
        """Clicking the Checklist Item filter should open its dropdown."""
        f = self._open(logged_in_page)
        f.checklist_item_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Status dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_status_dropdown_opens(self, logged_in_page: Page):
        """Status is only enabled after a Checklist Item is selected. Select a
        Checklist Item option first, then verify the Status dropdown opens."""
        f = self._open(logged_in_page)
        # Step 1: select any Checklist Item to unlock Status
        f.checklist_item_trigger.click()
        expect(f.dropdown_menu).to_be_visible()
        logged_in_page.locator("[class*='-option']").first.click()
        # Step 2: Status is now enabled
        f.status_trigger.click()
        expect(f.dropdown_menu).to_be_visible()

    @allure.story("Sub Status dropdown opens")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sub_status_dropdown_opens(self, logged_in_page: Page):
        """Sub Status requires Checklist Item → Status to be selected first.
        Walk through both prerequisites, then verify Sub Status dropdown opens."""
        f = self._open(logged_in_page)
        # Step 1: select any Checklist Item to unlock Status
        f.checklist_item_trigger.click()
        expect(f.dropdown_menu).to_be_visible()
        logged_in_page.locator("[class*='-option']").first.click()
        # Step 2: select any Status to unlock Sub Status
        f.status_trigger.click()
        expect(f.dropdown_menu).to_be_visible()
        logged_in_page.locator("[class*='-option']").first.click()
        # Step 3: Sub Status is now enabled
        f.sub_status_trigger.click()
        expect(f.dropdown_menu).to_be_visible()


@allure.feature("Edit Columns")
class TestEditColumnsApply:
    """Applying an Edit Columns change (toggling a field live-updates the table)."""

    @allure.story("Hiding a field removes its table column")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_hiding_a_field_removes_its_column(self, logged_in_page: Page):
        """Un-checking an optional field removes its column live; re-checking restores it."""
        panel = EditColumnsPage(logged_in_page)
        before = panel.table_column_count()
        panel.open()
        checkbox = panel.hide_first_optional_field()
        expect(logged_in_page.locator("table thead th")).to_have_count(before - 1)
        panel.show_field(checkbox)
        expect(logged_in_page.locator("table thead th")).to_have_count(before)

    @allure.story("Set Default is available")
    @allure.severity(allure.severity_level.NORMAL)
    def test_set_default_button_present(self, logged_in_page: Page):
        """The Edit Columns panel offers a Set Default action."""
        panel = EditColumnsPage(logged_in_page)
        panel.open()
        expect(panel.set_default_button).to_be_visible()

    @allure.story("Hiding every optional column never crashes the table")
    @allure.severity(allure.severity_level.NORMAL)
    def test_hide_all_columns_then_restore(self, logged_in_page: Page):
        """Unchecking every optional field leaves the table rendering (the
        mandatory Lead ID column still visible, no page error); re-checking
        every field restores the full column set."""
        page_errors: list[str] = []
        logged_in_page.on("pageerror", lambda err: page_errors.append(str(err)))

        panel = EditColumnsPage(logged_in_page)
        panel.open()
        hidden = panel.hide_all_optional_fields()
        logged_in_page.wait_for_timeout(2000)

        assert logged_in_page.get_by_role("columnheader", name="Lead ID", exact=True).is_visible()
        assert page_errors == []

        panel.show_all_fields(hidden)
        logged_in_page.wait_for_timeout(2000)

        # Spot-check a few previously-hidden columns are restored. exact=True
        # avoids "Source" ambiguously matching the "Sourced by" header too.
        for header in ("Bank", "Status", "Source"):
            assert logged_in_page.get_by_role("columnheader", name=header, exact=True).is_visible()


@allure.feature("Edit Columns")
class TestPagination:
    """The leads-list pagination control."""

    @allure.story("Bug: last pagination page can render empty despite a non-zero total")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="the pagination control's last page should show at least one row whenever the header total is non-zero, but it has been observed empty", strict=True)
    def test_pagination_last_page_matches_total_bug(self, logged_in_page: Page):
        """Documents a possible bug: jumping to the pagination control's last
        page should show at least one row whenever the header's total lead
        count is non-zero, but the last page has been observed to render
        empty (a stale/off-by-one pagination total)."""
        home = HomePage(logged_in_page)
        panel = EditColumnsPage(logged_in_page)
        total = home.all_leads_count()
        assert total > 0, f"expected a non-zero All Leads total, got {total}"

        last_page = panel.go_to_last_page()
        logged_in_page.wait_for_timeout(3000)

        row_count = logged_in_page.locator("table tbody tr").count()
        assert row_count > 0, (
            f"last page ({last_page}) rendered empty despite an All Leads total of {total}"
        )


@allure.feature("Advanced Filters")
class TestAdvancedFiltersApply:
    """Applying an advanced filter actually filters the leads table."""

    @allure.story("Applying a Source filter changes the results")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_apply_source_filter_changes_results(self, logged_in_page: Page):
        """Selecting a Source and clicking Apply reduces the All Leads count.
        Advanced filters persist server-side, so this resets before and after."""
        home = HomePage(logged_in_page)
        f = AdvancedFiltersPage(logged_in_page)
        f.reset()                                  # clean baseline
        before = home.all_leads_count()
        try:
            f.open()
            f.select_first_source()
            f.apply()
            after = home.all_leads_count()
            assert after < before, f"expected filtered count < {before}, got {after}"
        finally:
            f.reset()                              # don't leave a persistent filter

    @allure.story("Clear All resets a selected filter")
    @allure.severity(allure.severity_level.NORMAL)
    def test_clear_all_resets_source(self, logged_in_page: Page):
        """Clear All clears the selected Source: re-opening the panel shows the
        'Select Source' placeholder again (Clear All also closes the panel)."""
        f = AdvancedFiltersPage(logged_in_page)
        f.reset()                                  # clean baseline
        f.open()
        f.select_first_source()                    # 'Select Source' replaced by a value
        f.clear_all()                              # clears selection + closes panel
        f.open()                                   # re-open to inspect
        expect(f.source_trigger).to_be_visible()   # placeholder restored


@allure.feature("Bulk Actions")
class TestBulkActions:
    """The leads-list Actions menu (Reassign / Bulk Import / Export Leads)."""

    @allure.story("Actions menu lists the bulk options")
    @allure.severity(allure.severity_level.NORMAL)
    def test_actions_menu_options(self, logged_in_page: Page):
        """The Actions menu offers Reassign Leads, Bulk Import and Export Leads."""
        home = HomePage(logged_in_page)
        home.open_actions_menu()
        text = " ".join(
            home.actions_items.nth(i).inner_text()
            for i in range(home.actions_items.count())
        )
        assert "Reassign Leads" in text
        assert "Bulk Import" in text
        assert "Export Leads" in text
