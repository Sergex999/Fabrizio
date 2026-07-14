"""Browser automation against yuntrack.com to resolve an international
tracking number to its "Last Mile" carrier, official tracking website, and
local tracking number.

yuntrack.com is a public tracking form (no login required).
"""

from typing import Optional

from playwright.sync_api import sync_playwright

TRACK_URL = "https://www.yuntrack.com/"


class YunExpressClient:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def get_last_mile(self, tracking_number: str) -> Optional[dict]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            try:
                page.goto(TRACK_URL)
                page.wait_for_selector("#search", timeout=15000)

                try:
                    page.locator("button", has_text="Accept").first.click(timeout=3000)
                except Exception:
                    pass  # no cookie banner this time

                page.fill("#search", tracking_number)
                page.locator(".btn", has_text="Track").click()

                try:
                    page.wait_for_selector(".where", timeout=15000)
                except Exception:
                    return None

                where = page.locator(".where").first
                if where.count() == 0:
                    return None

                carrier_line = where.locator("p", has_text="Last Mile:").first
                if carrier_line.count() == 0:
                    return None
                carrier = carrier_line.inner_text().split(":", 1)[1].strip()

                website_link = where.locator("a[href^='http']").first
                tracking_url = (
                    website_link.get_attribute("href") if website_link.count() > 0 else None
                )

                return {
                    "carrier": carrier,
                    "tracking_url": tracking_url,
                    "local_tracking_number": None,
                }
            finally:
                browser.close()
