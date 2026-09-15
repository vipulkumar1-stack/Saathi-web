import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from config.config import BASE_URL


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.mobile_input = page.get_by_role("textbox", name="Mobile or Email *")
        self.submit_button = page.get_by_role("button", name="Submit")
        self.otp_input = page.get_by_role("textbox", name="OTP *")
        self.verify_button = page.get_by_role("button", name="Verify")

    @allure.step("Open login page")
    def open(self):
        self.navigate(BASE_URL)

    @allure.step("Enter mobile number")
    def enter_mobile(self, mobile: str):
        self.mobile_input.click()
        self.mobile_input.fill(mobile)

    @allure.step("Submit mobile number")
    def submit_mobile(self):
        self.submit_button.click()

    @allure.step("Enter OTP")
    def enter_otp(self, otp: str):
        self.otp_input.wait_for(state="visible")
        self.otp_input.fill(otp)

    @allure.step("Verify OTP")
    def verify_otp(self):
        self.verify_button.click()

    @allure.step("Login with mobile and OTP")
    def login(self, mobile: str, otp: str):
        self.open()
        self.enter_mobile(mobile)
        self.submit_mobile()
        self.enter_otp(otp)
        self.verify_otp()
