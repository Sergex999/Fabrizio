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

    def _pause_for_inspection(self, page):
        """When running with a visible browser, keep the page open for a
        while so it can be inspected manually before it closes."""
        if not self.headless:
            page.wait_for_timeout(60000)

    def get_last_mile(self, tracking_number: str) -> Optional[dict]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            try:
                page.goto(TRACK_URL)
                page.wait_for_selector("#search", timeout=15000)

                try:
                    page.locator(".cookies-btn-accept").first.click(timeout=3000)
                except Exception:
                    pass  # no cookie banner this time

                page.fill("#search", tracking_number)
                page.locator(".btn", has_text="Track").click()

                try:
                    page.wait_for_selector(".rightTop", timeout=15000)
                except Exception:
                    self._pause_for_inspection(page)
                    return None

                # .where only contains its own first line in the real DOM
                # (nested <p> tags get auto-closed by the browser), so scope
                # to the surrounding "Additional Notes" container instead.
                # There's also a "Shipment Information" box that shares the
                # .rightTop class, so filter specifically for the one that
                # has the "Additional Notes" heading.
                container = page.locator(".rightTop", has_text="Additional Notes").first
                if container.count() == 0:
                    self._pause_for_inspection(page)
                    return None

                carrier_line = container.locator("p", has_text="Last Mile:").first
                if carrier_line.count() == 0:
                    self._pause_for_inspection(page)
                    return None
                carrier = carrier_line.inner_text().split(":", 1)[1].strip()

                website_link = container.locator("a[href^='http']").first
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
