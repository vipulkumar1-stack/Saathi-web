import re
import allure
import pytest
from playwright.sync_api import Page, expect
from pages.home_page import HomePage
from pages.check_offers_page import CheckOffersPage
from utils.data_helper import generate_check_offers_data


@allure.feature("Check Offers")
class TestCheckOffers:
    """The Check Offers tool is now a per-lead Loan Offer Calculator opened from
    the lead detail page via 'Checkout Loan Offers!' (in the same tab). It requires
    a lead context and no longer creates leads — reaching the offers results screen
    is the success signal."""

    def _open_calculator(self, logged_in_page: Page, lead_id: str) -> CheckOffersPage:
        home = HomePage(logged_in_page)
        home.click_pre_login_tab()
        home.search_lead(lead_id)
        lead_page = home.open_lead_in_new_tab(lead_id)
        # The "Checkout Loan Offers!" CTA renders the Loan Offer Calculator inside
        # the same lead-detail tab (it is not a popup). Wait for the page to settle
        # so the CTA's click handler is hydrated, click it, then wait for the
        # calculator's first screen to appear.
        lead_page.wait_for_load_state("networkidle")
        cta = lead_page.get_by_text(re.compile("Checkout Loan Offers")).first
        cta.wait_for(state="visible")
        cta.click()
        offers = CheckOffersPage(lead_page)
        offers.get_started_button.wait_for(state="visible")
        return offers

    @allure.story("Calculator opens for a lead")
    @allure.severity(allure.severity_level.NORMAL)
    def test_check_offers_calculator_opens(self, logged_in_page: Page, check_offers_lead_id: str):
        """Opening 'Checkout Loan Offers!' from a lead launches the Loan Offer
        Calculator on its first step (Get Started)."""
        tool = self._open_calculator(logged_in_page, check_offers_lead_id)
        expect(tool.get_started_button).to_be_visible()

    @allure.story("Offers calculated successfully for a lead")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_check_offers_shows_offers(self, logged_in_page: Page, check_offers_lead_id: str):
        """Full Loan Offer Calculator flow — the offers results screen is reached."""
        data = generate_check_offers_data()
        tool = self._open_calculator(logged_in_page, check_offers_lead_id)
        tool.run_full_flow(data)
        expect(tool.offers_results).to_be_visible()
