"""Browser automation against yuntrack.com to resolve an international
tracking number to its "Last Mile" carrier and local tracking number.

IMPORTANT: yuntrack.com returned HTTP 403 when probed from the development
sandbox used to write this module, so the CSS selectors below are best-effort
placeholders based on the described page layout, not verified against the
real DOM. Run this once with PLAYWRIGHT_HEADLESS=false and fix any selector
mismatch before relying on it.
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
                page.wait_for_load_state("networkidle")
                # PLACEHOLDER SELECTOR: verify against the real "Track" input.
                page.fill(
                    "input[name='trackNumber'], input#trackingNumber",
                    tracking_number,
                )
                page.click("button:has-text('Track')")
                page.wait_for_load_state("networkidle")

                # PLACEHOLDER SELECTORS: verify against the real "Last Mile"
                # panel on the results page.
                carrier = page.locator(".last-mile-carrier").first
                local_tracking = page.locator(".last-mile-tracking-number").first
                if carrier.count() == 0:
                    return None
                return {
                    "carrier": carrier.inner_text().strip(),
                    "local_tracking_number": (
                        local_tracking.inner_text().strip()
                        if local_tracking.count()
                        else None
                    ),
                }
            finally:
                browser.close()
