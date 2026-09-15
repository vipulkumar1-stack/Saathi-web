import allure
from datetime import datetime, timedelta
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.constants import ScheduleFollowup as Msg


class ScheduleFollowupPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Trigger button visible on the lead detail page (second plusicon — first is unrelated)
        self.add_button = page.get_by_role("img", name="plusicon").nth(1)

        # Form fields (visible after opening the Schedule Follow-up panel)
        self.call_radio       = page.get_by_role("radio", name="Call")
        self.doc_pickup_radio = page.get_by_role("radio", name="Doc Pickup")
        self.date_input       = page.get_by_role("textbox").first
        self.time_input       = page.get_by_role("textbox", name="Time")
        self.comment_input    = page.locator("textarea[name='comment']")
        self.schedule_button  = page.get_by_role("button", name="Schedule Now")

        # Validation errors
        self.date_error    = page.get_by_text(Msg.ERROR_DATE, exact=True)
        self.time_error    = page.get_by_text(Msg.ERROR_TIME, exact=True)
        self.comment_error = page.get_by_text(Msg.ERROR_COMMENT, exact=True)

        # Followup list item — used to verify a followup exists after creation
        self.followup_item = page.get_by_text("Next Follow-up").first

    def _day_button_label(self, dt: datetime) -> str:
        return f"{dt.strftime('%A')}, {dt.day} {dt.strftime('%B')}"

    @allure.step("Pick follow-up date")
    def pick_date(self, date_str: str = None):
        # Default to tomorrow so the date is always in the future
        target = datetime.now() + timedelta(days=1)
        if date_str:
            try:
                target = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                pass

        self.date_input.click()
        # Fixed delay for the calendar to render: this picker exposes no DOM
        # signal that is reliably present on open for a current-month selection.
        self.page.wait_for_timeout(400)

        today = datetime.now()
        months_diff = (target.year - today.year) * 12 + (target.month - today.month)
        nav = "Next Month" if months_diff > 0 else "Previous Month"
        for _ in range(abs(months_diff)):
            self.page.get_by_role("button", name=nav).click()

        self.page.get_by_role("gridcell", name=self._day_button_label(target)).click()

    @allure.step("Open Schedule Follow-up form")
    def open_form(self):
        self.add_button.click()
        self.schedule_button.wait_for(state="visible")
        self.date_input.wait_for(state="visible")

    @allure.step("Fill and submit Schedule Follow-up form")
    def fill_and_submit(self, data: dict):
        followup_type = data.get("type", "Call")
        if followup_type == "Doc Pickup":
            self.doc_pickup_radio.check()
        else:
            self.call_radio.check()

        if data.get("pick_date", True):
            self.pick_date(data.get("date"))

        if data.get("time"):
            self.time_input.click()
            self.time_input.fill(data["time"])

        if data.get("comment"):
            self.comment_input.click()
            self.comment_input.fill(data["comment"])

        self.schedule_button.click()
