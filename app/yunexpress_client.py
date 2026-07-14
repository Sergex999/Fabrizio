"""Browser automation against yuntrack.com to resolve an international
tracking number to its "Last Mile" carrier, official tracking website, and
local tracking number.

yuntrack.com is a public tracking form (no login required). The results
page is reachable directly by URL, so no form interaction is needed.
"""

from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright

RESULT_URL = "https://www.yuntrack.com/parcelTracking?id={tracking_number}"
DEBUG_SCREENSHOT = Path(__file__).parent.parent / "yunexpress_debug.png"
DEBUG_HTML = Path(__file__).parent.parent / "yunexpress_debug.html"


class YunExpressClient:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def _save_debug_artifacts(self, page):
        """Saves a screenshot and the page HTML so a failed lookup can be
        inspected afterwards without keeping the browser open."""
        try:
            page.screenshot(path=str(DEBUG_SCREENSHOT))
        except Exception:
            pass
        try:
            DEBUG_HTML.write_text(page.content(), encoding="utf-8")
        except Exception:
            pass

    def get_last_mile(self, tracking_number: str) -> Optional[dict]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            try:
                page.goto(RESULT_URL.format(tracking_number=tracking_number))

                try:
                    page.locator(".cookies-btn-accept").first.click(timeout=3000)
                except Exception:
                    pass  # no cookie banner this time

                # The "Additional Notes" box loads later than the rest of the
                # page, so wait for the actual "Last Mile" text to show up.
                try:
                    page.locator("p", has_text="Last Mile:").first.wait_for(timeout=30000)
                except Exception:
                    self._save_debug_artifacts(page)
                    return None

                container = page.locator(".rightTop", has_text="Additional Notes").first
                if container.count() == 0:
                    self._save_debug_artifacts(page)
                    return None

                carrier_line = container.locator("p", has_text="Last Mile:").first
                if carrier_line.count() == 0:
                    self._save_debug_artifacts(page)
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
