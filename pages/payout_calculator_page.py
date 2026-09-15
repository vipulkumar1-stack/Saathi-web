import re
import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.constants import PayoutCalculator as Msg


class PayoutCalculatorPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Double-filter: find the deepest div that contains BOTH "Payout Calculator"
        # text AND a "Check Now" button — that is the card div itself. Using just
        # has_text would also match ancestor containers that hold all tool cards.
        self.check_now_button = (
            page.locator("div")
            .filter(has_text="Payout Calculator")
            .filter(has=page.get_by_role("button", name="Check Now"))
            .last
            .get_by_role("button", name="Check Now")
        )

        # Form fields — placeholder/role based, no CSS classes.
        self.loan_amount_input = page.get_by_role("textbox", name="Enter Loan Amount")
        # Product type placeholder is "Select Product Type" (differs from its label).
        # Fulfilment type placeholder is "Fulfilment Type" (same text as the label —
        # use .last so the dropdown control is targeted, not the label above it).
        self.product_type_dropdown    = page.get_by_text("Select Product Type", exact=True)
        self.fulfilment_type_dropdown = page.get_by_text("Fulfilment Type", exact=True).last
        self.calculate_button         = page.get_by_role("button", name="Calculate now")

        # Heading that appears on the results page after a successful calculation.
        self.payout_result = page.get_by_text(Msg.RESULT_HEADING, exact=True)

        # Top bank card's payout value — a percentage-slab description, e.g.
        # "10% on Ambak collection". Confirmed live on 2026-08-20: each result
        # card (`div.RightBankAMt`) now holds a single `div.amountPercnt` under
        # a "Payout %" label; there is no separate rupee "Payout Amount" value
        # on this screen for any bank, at any loan amount (including ₹0). The
        # slab percentage itself does not vary with the loan amount entered.
        # `.first` pins this to the first (top-listed) bank card so repeated
        # calculations compare the same row.
        self.first_payout_value = self.healing_locator(
            page.locator("div.RightBankAMt .amountPercnt").first,
            page.locator("div.RightBankAMt").filter(has_text="Payout %").first
                .locator("div.amountPercnt"),
            name="first_payout_value",
        )

    @allure.step("Navigate to My Tools")
    def go_to_my_tools(self):
        self.page.get_by_role("link", name="tools My Tools").click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Open Payout Calculator")
    def open_payout_calculator(self):
        self.check_now_button.wait_for(state="visible")
        self.check_now_button.click()

    @allure.step("Fill loan amount")
    def fill_loan_amount(self, amount: str):
        self.loan_amount_input.wait_for(state="visible")
        self.loan_amount_input.click()
        self.loan_amount_input.fill(amount)

    @allure.step("Select product type: {product_type}")
    def select_product_type(self, product_type: str):
        self.product_type_dropdown.wait_for(state="visible")
        self.product_type_dropdown.click()
        self.page.get_by_text(product_type, exact=True).click()

    @allure.step("Select fulfilment type: {fulfilment_type}")
    def select_fulfilment_type(self, fulfilment_type: str):
        self.fulfilment_type_dropdown.wait_for(state="visible")
        self.fulfilment_type_dropdown.click()
        self.page.get_by_text(fulfilment_type, exact=True).click()

    @allure.step("Click Calculate now")
    def calculate(self):
        self.calculate_button.click()

    @allure.step("Fill all fields and calculate payout")
    def fill_and_calculate(self, data: dict):
        self.fill_loan_amount(data["loan_amount"])
        self.select_product_type(data["product_type"])
        self.select_fulfilment_type(data["fulfilment_type"])
        self.calculate()

    @allure.step("Read first bank's payout percentage")
    def get_first_payout_percent(self) -> float:
        """Parse the top bank card's payout slab text (e.g. '10% on Ambak
        collection') into a float percentage (10.0)."""
        self.first_payout_value.wait_for(state="visible")
        text = self.first_payout_value.inner_text()
        match = re.search(r"([\d.]+)\s*%", text)
        if not match:
            raise AssertionError(f"No percentage found in payout cell: {text!r}")
        return float(match.group(1))
