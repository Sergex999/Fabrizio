"""Browser automation against dianxiaomi.com to resolve a recipient name to
an international tracking number.

IMPORTANT: dianxiaomi.com returned HTTP 403 when probed from the development
sandbox used to write this module (likely bot-protection blocking that
network), so the CSS selectors below could not be verified against the real,
logged-in page. Run this once with PLAYWRIGHT_HEADLESS=false against a real
account and fix any selector that doesn't match before relying on it.
"""

from typing import Optional

from playwright.sync_api import sync_playwright

LOGIN_URL = "https://www.dianxiaomi.com/user/login.htm"
ORDERS_URL = "https://www.dianxiaomi.com/web/order/all?go=m1-1"


class DianxiaomiClient:
    def __init__(self, username: str, password: str, headless: bool = True):
        self.username = username
        self.password = password
        self.headless = headless

    def find_tracking_number(self, recipient_name: str) -> Optional[str]:
        if not self.username or not self.password:
            return None
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            try:
                self._login(page)
                return self._search_recipient(page, recipient_name)
            finally:
                browser.close()

    def _login(self, page):
        page.goto(LOGIN_URL)
        page.wait_for_load_state("networkidle")
        # PLACEHOLDER SELECTORS: verify against the real login form.
        page.fill("input[name='username']", self.username)
        page.fill("input[name='password']", self.password)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")

    def _search_recipient(self, page, recipient_name: str) -> Optional[str]:
        page.goto(ORDERS_URL)
        page.wait_for_load_state("networkidle")
        # PLACEHOLDER SELECTOR: verify against the real search box for the
        # recipient/consignee name filter.
        search_box = page.locator(
            "input[placeholder*='收件人'], input[name='receiverName']"
        ).first
        search_box.fill(recipient_name)
        search_box.press("Enter")
        page.wait_for_load_state("networkidle")

        # PLACEHOLDER SELECTOR: verify against the real results table cell
        # that holds the international tracking number.
        tracking_cell = page.locator("td.tracking-number, .track-no").first
        if tracking_cell.count() == 0:
            return None
        return tracking_cell.inner_text().strip()
