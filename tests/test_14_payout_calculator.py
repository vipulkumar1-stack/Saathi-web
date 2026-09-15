import allure
import pytest
from playwright.sync_api import Page, expect
from pages.payout_calculator_page import PayoutCalculatorPage
from config.config import PAYOUT_CALCULATOR_DATA


@allure.feature("Payout Calculator")
class TestPayoutCalculator:

    def _open_calculator(self, logged_in_page: Page) -> PayoutCalculatorPage:
        page_obj = PayoutCalculatorPage(logged_in_page)
        page_obj.go_to_my_tools()
        page_obj.open_payout_calculator()
        return page_obj

    @allure.story("Validation: Loan amount is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_payout_calculator_without_loan_amount(self, logged_in_page: Page):
        """Clicking Calculate now without a loan amount should not show payout results."""
        calc = self._open_calculator(logged_in_page)
        calc.select_product_type(PAYOUT_CALCULATOR_DATA["product_type"])
        calc.select_fulfilment_type(PAYOUT_CALCULATOR_DATA["fulfilment_type"])
        calc.calculate()
        expect(calc.payout_result).not_to_be_visible()

    @allure.story("Validation: Product type is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_payout_calculator_without_product_type(self, logged_in_page: Page):
        """Clicking Calculate now without selecting a product type should not show payout results."""
        calc = self._open_calculator(logged_in_page)
        calc.fill_loan_amount(PAYOUT_CALCULATOR_DATA["loan_amount"])
        calc.calculate()
        expect(calc.payout_result).not_to_be_visible()

    @allure.story("Validation: Fulfilment type is required")
    @allure.severity(allure.severity_level.NORMAL)
    def test_payout_calculator_without_fulfilment_type(self, logged_in_page: Page):
        """Clicking Calculate now without selecting a fulfilment type should not show payout results."""
        calc = self._open_calculator(logged_in_page)
        calc.fill_loan_amount(PAYOUT_CALCULATOR_DATA["loan_amount"])
        calc.select_product_type(PAYOUT_CALCULATOR_DATA["product_type"])
        calc.calculate()
        expect(calc.payout_result).not_to_be_visible()

    @allure.story("Payout calculated successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_payout_calculates_successfully(self, logged_in_page: Page):
        """Filling all fields and clicking Calculate now should display payout results."""
        calc = self._open_calculator(logged_in_page)
        calc.fill_and_calculate(PAYOUT_CALCULATOR_DATA)
        expect(calc.payout_result).to_be_visible()

    @allure.story("Bug: payout results never render after Calculate now")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(
        reason="the payout results panel should show each bank's payout percentage "
               "after Calculate now, but no percentage (or bank card of any kind) "
               "renders at all any more — confirmed live 2026-09-04: the panel "
               "correctly retitles itself 'Payout Details' and the backend GraphQL "
               "call returns 200 with no console/page errors, yet the results area "
               "stays completely blank for every loan amount tried (0, 1000000, "
               "2000000, 1000000.50), so no percentage can be read to compare",
        strict=True,
    )
    def test_decimal_loan_amount_does_not_inflate_payout(self, logged_in_page: Page):
        """Documents a bug: a decimal-suffixed loan amount (e.g. 1000000.50)
        should show the same payout percentage as the whole-number amount, but
        the results panel renders no percentage for either amount — see the
        xfail reason above. This test previously carried its own history of an
        older, now-superseded version of this same defect (a rupee amount that
        used to be shown and divided out inflated); that symptom is gone
        because the whole results section is gone, not because it was fixed."""
        calc = self._open_calculator(logged_in_page)
        calc.fill_loan_amount("1000000")
        calc.select_product_type(PAYOUT_CALCULATOR_DATA["product_type"])
        calc.select_fulfilment_type(PAYOUT_CALCULATOR_DATA["fulfilment_type"])
        calc.calculate()
        expect(calc.payout_result).to_be_visible()
        whole_pct = calc.get_first_payout_percent()

        calc2 = self._open_calculator(logged_in_page)
        calc2.fill_loan_amount("1000000.50")
        calc2.select_product_type(PAYOUT_CALCULATOR_DATA["product_type"])
        calc2.select_fulfilment_type(PAYOUT_CALCULATOR_DATA["fulfilment_type"])
        calc2.calculate()
        expect(calc2.payout_result).to_be_visible()
        decimal_pct = calc2.get_first_payout_percent()

        assert abs(whole_pct - decimal_pct) < 0.01, (
            f"Payout percentage should be identical for the same amount whether or not "
            f"it carries a decimal: whole={whole_pct}% vs decimal={decimal_pct}%"
        )

    @allure.story("Bug: negative loan amount silently accepted")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(reason="a negative loan amount should be rejected, but the calculator silently treats it as positive and shows a payout", strict=True)
    def test_negative_loan_amount_rejected_bug(self, logged_in_page: Page):
        """BUG: a negative loan amount should be rejected, but the calculator silently treats it as positive and shows a plausible payout result."""
        calc = self._open_calculator(logged_in_page)
        calc.fill_loan_amount("-500000")
        calc.select_product_type(PAYOUT_CALCULATOR_DATA["product_type"])
        calc.select_fulfilment_type(PAYOUT_CALCULATOR_DATA["fulfilment_type"])
        calc.calculate()
        # A plain expect(...).not_to_be_visible() would pass immediately (before
        # the result has had a chance to render) even when the app goes on to
        # show a result a moment later — negative assertions only wait when
        # currently failing, not for the state to stay put. Give the app the
        # same rendering window the other calculations need, then assert.
        logged_in_page.wait_for_timeout(4000)
        assert not calc.payout_result.is_visible(), (
            "BUG: a negative loan amount should be rejected, but a payout "
            "result was shown as if the amount were positive"
        )

    @allure.story("Bug: payout results never render after Calculate now")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(
        reason="a zero loan amount should calculate cleanly and show the same "
               "payout percentage as any other amount, but no percentage (or bank "
               "card of any kind) renders at all any more — confirmed live "
               "2026-09-04: the results panel stays completely blank for every "
               "loan amount tried, zero included, so there is no percentage to "
               "compare against a non-zero baseline",
        strict=True,
    )
    def test_zero_amount_calculates_cleanly(self, logged_in_page: Page):
        """Documents a bug: entering a zero loan amount should calculate
        without a page error and show the same payout percentage as any other
        amount, but the results panel renders no percentage for zero OR for a
        normal amount — see the xfail reason above."""
        errors = []
        logged_in_page.on("pageerror", lambda err: errors.append(str(err)))
        calc = self._open_calculator(logged_in_page)
        calc.fill_loan_amount("0")
        calc.select_product_type(PAYOUT_CALCULATOR_DATA["product_type"])
        calc.select_fulfilment_type(PAYOUT_CALCULATOR_DATA["fulfilment_type"])
        calc.calculate()
        expect(calc.payout_result).to_be_visible()
        zero_pct = calc.get_first_payout_percent()

        calc2 = self._open_calculator(logged_in_page)
        calc2.fill_and_calculate(PAYOUT_CALCULATOR_DATA)
        expect(calc2.payout_result).to_be_visible()
        baseline_pct = calc2.get_first_payout_percent()

        assert not errors, f"Unexpected page error(s) on zero amount: {errors}"
        assert zero_pct == baseline_pct, (
            f"Expected the same payout percentage regardless of loan amount, "
            f"got {zero_pct}% for zero vs {baseline_pct}% for a normal amount"
        )

    @allure.story("Bug: payout results never render after Calculate now")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.known_bug
    @pytest.mark.xfail(
        reason="doubling a whole-number loan amount should leave the payout "
               "percentage unchanged (a fixed slab rate, not computed "
               "proportionally), but no percentage (or bank card of any kind) "
               "renders at all any more — confirmed live 2026-09-04: the results "
               "panel stays completely blank for every loan amount tried, so "
               "there is no percentage to compare at either amount",
        strict=True,
    )
    def test_whole_number_math_scales_proportionally(self, logged_in_page: Page):
        """Documents a bug: doubling a whole-number loan amount should not
        change the payout percentage shown, but the results panel renders no
        percentage at either amount — see the xfail reason above."""
        calc = self._open_calculator(logged_in_page)
        calc.fill_loan_amount("1000000")
        calc.select_product_type(PAYOUT_CALCULATOR_DATA["product_type"])
        calc.select_fulfilment_type(PAYOUT_CALCULATOR_DATA["fulfilment_type"])
        calc.calculate()
        expect(calc.payout_result).to_be_visible()
        base_pct = calc.get_first_payout_percent()

        calc2 = self._open_calculator(logged_in_page)
        calc2.fill_loan_amount("2000000")
        calc2.select_product_type(PAYOUT_CALCULATOR_DATA["product_type"])
        calc2.select_fulfilment_type(PAYOUT_CALCULATOR_DATA["fulfilment_type"])
        calc2.calculate()
        expect(calc2.payout_result).to_be_visible()
        doubled_pct = calc2.get_first_payout_percent()

        assert base_pct == doubled_pct, (
            f"Doubling the loan amount should not change the payout percentage: "
            f"base={base_pct}%, doubled={doubled_pct}%"
        )
