import re
import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.constants import CheckOffers as Msg


class CheckOffersPage(BasePage):
    """Loan Offer Calculator — the redesigned "Check Offers" tool.

    It is opened per-lead via the "Checkout Loan Offers!" CTA on the lead detail
    page (in a new browser tab) and runs against that lead's context; opening it
    standalone from My Tools fails with a "Lead ID is missing" toast. The tool no
    longer creates a lead — it walks a multi-step wizard and renders an offers
    results screen. These methods drive the default Self-Employed non-Professional
    path, which collects business details + manual ITR/NPAT income.

    Wizard steps:
      1. Loan type + product + employment type  -> Get Started!
      2. Loan amount (+ auto-filled tenure)      -> Continue
      3. Company type, age of business, credit score, age -> Continue
      4. Income (manual ITR/NPAT)                -> Continue
      5. Property details                        -> Check Offers
      6. Offers results screen ("Share Offers")
    """

    def __init__(self, page: Page):
        super().__init__(page)
        # Step 1 — loan type / product / employment
        self.get_started_button   = page.get_by_role("button", name="Get Started!")
        # Step 2 — loan details
        self.loan_amount_input     = page.get_by_role("textbox", name="Enter loan amount")
        self.continue_button       = page.get_by_role("button", name="Continue")
        # Step 3 — business & eligibility
        self.age_of_business_input = page.get_by_role("textbox", name="Enter age of business in years")
        # Step 4 — income
        self.enter_income_button   = page.get_by_text("Enter income details", exact=False)
        # Step 5 — property
        self.expected_value_input  = page.locator("[name='expectedValue']")
        self.check_offers_button   = page.get_by_role("button", name="Check Offers")
        # Result
        self.offers_results        = page.get_by_text(Msg.RESULTS_MARKER, exact=False)

    # ── option helper ──────────────────────────────────────────────────────────
    def _pick_option(self, text: str) -> None:
        """Click an option in an open react-select menu by exact visible text.
        The dropdowns here use the `employment-select` class prefix, whose option
        nodes match `[class*='option']`."""
        self.page.locator("[class*='option']").filter(
            has_text=re.compile(rf"^{re.escape(text)}$")
        ).first.click()

    # ── Step 1: loan type / product / employment ───────────────────────────────
    @allure.step("Select loan type: {loan_type}")
    def select_loan_type(self, loan_type: str):
        self.page.get_by_role("button", name=loan_type).first.click()

    @allure.step("Select loan product: {product}")
    def select_loan_product(self, product: str):
        self.page.get_by_text(product, exact=True).first.click()

    @allure.step("Select employment type: {employment}")
    def select_employment_type(self, employment: str):
        # Employment Type is a react-select. The business-details step (step 3:
        # company type, age of business, …) only renders for the self-employed
        # path, so it must be selected explicitly — otherwise a Salaried lead
        # never shows those fields and the flow stalls. Open the dropdown via its
        # select control (NOT by the current value's text): the default is
        # "Salaried", but the calculator persists the last choice back to the
        # lead, so the current value varies between runs.
        self.page.locator("[class*='-control']").first.click()
        self._pick_option(employment)

    @allure.step("Click Get Started")
    def click_get_started(self):
        self.get_started_button.click()

    # ── Step 2: loan details ────────────────────────────────────────────────────
    @allure.step("Fill loan amount: {amount}")
    def fill_loan_amount(self, amount: str):
        self.loan_amount_input.wait_for(state="visible")
        self.loan_amount_input.fill(amount)

    @allure.step("Click Continue")
    def click_continue(self):
        self.continue_button.click()

    # ── Step 3: business & eligibility ──────────────────────────────────────────
    @allure.step("Fill business & eligibility details")
    def fill_business_details(self, company_type: str, age_of_business: str,
                              credit_score: str, age_range: str, gender: str = None):
        # Company Type renders either with a "Select Company Type" placeholder
        # (needs a selection) or pre-filled with a default value (e.g. Propreitor),
        # depending on the lead — only open and choose when the placeholder shows.
        placeholder = self.page.get_by_text("Select Company Type", exact=True)
        if placeholder.count():
            placeholder.first.click()
            self._pick_option(company_type)
        self.age_of_business_input.wait_for(state="visible")
        self.age_of_business_input.fill(age_of_business)
        self.page.get_by_role("button", name=credit_score, exact=True).click()
        self.page.get_by_role("button", name=age_range, exact=True).click()
        # A Gender step (Male/Female) is part of this screen; select it when the
        # option is present so Continue can proceed.
        if gender:
            gender_btn = self.page.get_by_role("button", name=gender, exact=True)
            if gender_btn.count():
                gender_btn.first.click()

    # ── Step 4: income (manual ITR / NPAT) ──────────────────────────────────────
    @allure.step("Enter income manually")
    def fill_income_manually(self, income: dict):
        self.enter_income_button.first.click()
        for name, value in income.items():
            field = self.page.locator(f"[name='{name}']")
            field.first.wait_for(state="visible")
            field.first.fill(value)
        # Other Obligations -> No, Additional Income -> No
        no_options = self.page.get_by_text("No", exact=True)
        for i in range(no_options.count()):
            no_options.nth(i).click()

    # ── Step 5: property details ────────────────────────────────────────────────
    @allure.step("Fill property details")
    def fill_property_details(self, expected_value: str, state: str):
        self.page.get_by_text("No", exact=True).first.click()   # Property Identified -> No
        self.expected_value_input.first.fill(expected_value)
        self.page.get_by_text("Select...", exact=True).nth(0).click()   # State
        self._pick_option(state)
        # City list loads after the state is chosen; pick the first available city.
        self.page.get_by_text("Select...", exact=True).first.wait_for(state="visible")
        self.page.get_by_text("Select...", exact=True).first.click()
        self.page.locator("[class*='option']").first.click()

    @allure.step("Click Check Offers")
    def click_check_offers(self):
        self.check_offers_button.first.click()

    # ── Full happy-path flow ────────────────────────────────────────────────────
    @allure.step("Run full Loan Offer Calculator flow")
    def run_full_flow(self, data: dict):
        self.select_loan_type(data["loan_type"])
        self.select_loan_product(data["loan_product"])
        if data.get("employment_type"):
            self.select_employment_type(data["employment_type"])
        self.click_get_started()
        self.fill_loan_amount(data["loan_amount"])
        self.click_continue()
        self.fill_business_details(
            data["company_type"], data["age_of_business"],
            data["credit_score"], data["age_range"], data.get("gender"),
        )
        self.click_continue()
        self.fill_income_manually(data["income"])
        self.click_continue()
        self.fill_property_details(data["expected_property_value"], data["state"])
        self.click_check_offers()
