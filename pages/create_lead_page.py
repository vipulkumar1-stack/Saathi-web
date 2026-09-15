import time
import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.constants import CreateLead as Msg


class CreateLeadPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # Healing locators — primary is the current selector; fallbacks are tried
        # automatically if the primary breaks.  If a fallback fires, the name
        # appears in heal-report.json so you can update the primary selector.
        self.first_name_input = self.healing_locator(
            page.locator("#first_name"),
            page.get_by_label("First Name"),
            page.get_by_placeholder("First Name"),
            name="create_lead.first_name",
        )
        self.last_name_input = self.healing_locator(
            page.locator("#last_name"),
            page.get_by_label("Last Name"),
            page.get_by_placeholder("Last Name"),
            name="create_lead.last_name",
        )
        self.mobile_input = self.healing_locator(
            page.locator("#mobile"),
            page.get_by_label("Mobile"),
            page.get_by_placeholder("Mobile"),
            name="create_lead.mobile",
        )
        # Required Loan Amount — placeholder reads "Loan Amount*"; label is
        # "Required Loan Amount".  get_by_placeholder matches on substring.
        self.loan_amount_input = self.healing_locator(
            page.get_by_placeholder("Loan Amount"),
            page.get_by_label("Required Loan Amount"),
            name="create_lead.loan_amount",
        )
        self.remarks_input = self.healing_locator(
            page.get_by_placeholder("Enter remarks"),
            page.get_by_label("Remarks"),
            name="create_lead.remarks",
        )
        self.submit_button = self.healing_locator(
            page.get_by_role("button", name="Submit"),
            page.get_by_text("Submit", exact=True),
            name="create_lead.submit",
        )

        # Success popup
        self.success_title = page.get_by_text(Msg.SUCCESS_TITLE, exact=True)
        self.go_to_my_leads_button = page.get_by_role("button", name="Go to My Leads")

        # Duplicate mobile popup
        self.duplicate_popup_title = page.get_by_text(Msg.DUPLICATE_MOBILE)
        self.new_lead_button = page.get_by_role("button", name="+ New Lead")
        self.continue_button = page.get_by_role("button", name="Continue")

        # Lead entry mode — redesigned modal replaced the old "I will do it
        # myself" / "Refer to Ambak" radios with a fixed lead-type banner and
        # an Add Manually / Bulk Upload choice (see test_02b_lead_entry_mode.py).
        self.add_manually_radio = page.locator("label[for='add_manually']")
        self.bulk_upload_radio  = page.locator("label[for='bulk_upload']")
        self.lead_type_banner   = page.get_by_text("getting created for type")

        # Field validation errors
        self.first_name_error = page.get_by_text(Msg.ERROR_FIRST_NAME, exact=True)
        self.last_name_error  = page.get_by_text(Msg.ERROR_LAST_NAME, exact=True)
        self.mobile_error     = page.get_by_text(Msg.ERROR_MOBILE, exact=True)
        self.loan_type_error  = page.get_by_text(Msg.ERROR_LOAN_TYPE, exact=True)
        # Redesigned form surfaces this both as a Toastify toast (role=alert) and
        # an inline <p>; target the paragraph (like city) to avoid a
        # strict-mode match on two elements.
        self.employment_error = page.get_by_role("paragraph").filter(has_text=Msg.ERROR_EMPLOYMENT)
        self.city_error       = page.get_by_role("paragraph").filter(has_text=Msg.ERROR_CITY)

        # Toasts auto-dismiss, so a plain `expect(...).to_be_visible()` can race
        # a toast that has already vanished. submit_and_collect() polls and
        # records every toast body seen during submission into this set.
        self.toast_bodies = page.locator("[class*='Toastify__toast-body']")
        self.last_submit_toasts: set = set()

    @allure.step("Select loan type: {loan_type}")
    def select_loan_type(self, loan_type: str = None):
        self.open_select("Loan Type", "loan_type")
        if loan_type:
            self.choose_option(loan_type)
        else:
            self.choose_first_option()

    @allure.step("Select loan sub-type: {sub_type}")
    def select_loan_sub_type(self, sub_type: str):
        self.open_select("Loan Sub Type", "loan_sub_type")
        self.choose_option(sub_type)

    @allure.step("Select employment type: {employment_type}")
    def select_employment_type(self, employment_type: str = None):
        # Employment Type is mandatory (carries a red asterisk in the redesigned
        # modal). Options: Salaried, Self-Employed Professional, Self-Employed
        # non-Professional.
        self.open_select("Employment Type", "profession")
        if employment_type:
            self.choose_option(employment_type)
        else:
            self.choose_first_option()

    @allure.step("Select purchase type: {purchase_type}")
    def select_purchase_type(self, purchase_type: str = None):
        # Purchase Type — new field introduced by the redesign, optional (no
        # asterisk).
        self.open_select("Purchase Type", "property_type")
        if purchase_type:
            self.choose_option(purchase_type)
        else:
            self.choose_first_option()

    @allure.step("Select city: {option}")
    def select_city(self, search: str, option: str):
        self.open_select("City", "cra_city")
        self.type_in_select("City", search, "cra_city")
        self.choose_option(option)

    @allure.step("Fill lead creation form without submitting")
    def fill_only(self, data: dict):
        """Fill every field present in `data`, stopping short of clicking
        Submit — used both by fill_and_submit and by tests that need to
        inspect state right at the moment of submission (e.g. double-click
        debounce checks)."""
        self.first_name_input.wait_for(state="visible")
        if data.get("first_name"):
            self.first_name_input.fill(data["first_name"])
        if data.get("last_name"):
            self.last_name_input.fill(data["last_name"])
        if data.get("mobile"):
            self.mobile_input.fill(data["mobile"])
        loan_type = data.get("loan_type", True)
        if loan_type:
            self.select_loan_type(loan_type if isinstance(loan_type, str) else None)
            if data.get("loan_sub_type"):
                self.select_loan_sub_type(data["loan_sub_type"])
        employment_type = data.get("employment_type", True)
        if employment_type:
            self.select_employment_type(employment_type if isinstance(employment_type, str) else None)
        purchase_type = data.get("purchase_type")
        if purchase_type:
            self.select_purchase_type(purchase_type if isinstance(purchase_type, str) else None)
        if data.get("city_search"):
            self.select_city(data["city_search"], data["city_option"])
        if data.get("loan_amount"):
            self.loan_amount_input.fill(data["loan_amount"])
        if data.get("remarks"):
            self.remarks_input.fill(data["remarks"])

    @allure.step("Fill and submit lead creation form")
    def fill_and_submit(self, data: dict):
        self.fill_only(data)
        self.submit_button.click()

    @allure.step("Submit and collect validation toasts")
    def submit_and_collect(self, data: dict = None, settle_ms: int = 4000):
        """Fill (if `data` given) and click Submit, then poll for toasts until
        the form settles into a success/duplicate popup or the poll window
        elapses. Populates `last_submit_toasts` with every toast body text
        seen — Toastify toasts auto-dismiss, so a snapshot expect() taken too
        late can miss one that already fired and vanished."""
        if data is not None:
            self.fill_only(data)
        self.last_submit_toasts = set()
        self.submit_button.click()
        deadline = time.monotonic() + settle_ms / 1000
        while time.monotonic() < deadline:
            for t in self.toast_bodies.all():
                try:
                    text = t.inner_text().strip()
                    if text:
                        self.last_submit_toasts.add(text)
                except Exception:
                    pass
            if self.success_title.is_visible() or self.duplicate_popup_title.is_visible():
                return
            self.page.wait_for_timeout(150)

    def saw_error(self, msg: str) -> bool:
        """True if `msg` appeared either as a toast collected by
        submit_and_collect(), or as an inline <p> currently on the page."""
        if any(msg in t for t in self.last_submit_toasts):
            return True
        return self.page.get_by_role("paragraph").filter(has_text=msg).count() > 0
