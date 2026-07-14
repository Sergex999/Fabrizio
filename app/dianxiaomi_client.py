"""Browser automation against dianxiaomi.com to resolve a recipient name to
an international tracking number.

dianxiaomi.com requires solving a CAPTCHA at login, which can't be automated
reliably. Instead of logging in on every run, this client reuses a saved
browser session (cookies) created once via setup_dianxiaomi_session.py after
a manual login. Re-run that script whenever the saved session expires.
"""

from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright

ORDERS_URL = "https://www.dianxiaomi.com/web/order/all?go=m1-1"
STATE_FILE = Path(__file__).parent.parent / "dianxiaomi_state.json"
DEBUG_SCREENSHOT = Path(__file__).parent.parent / "dianxiaomi_debug.png"


class DianxiaomiClient:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def find_tracking_number(self, recipient_name: str) -> Optional[str]:
        if not STATE_FILE.exists():
            raise RuntimeError(
                "No saved dianxiaomi session found. Run "
                "'python setup_dianxiaomi_session.py' once to log in manually "
                "(including the captcha) and save the session."
            )
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(storage_state=str(STATE_FILE))
            page = context.new_page()
            try:
                return self._search_recipient(page, recipient_name)
            finally:
                browser.close()

    def _search_recipient(self, page, recipient_name: str) -> Optional[str]:
        page.goto(ORDERS_URL)
        page.wait_for_load_state("networkidle")

        # Always save a screenshot so the real page structure can be
        # inspected if the selectors below don't match.
        page.screenshot(path=str(DEBUG_SCREENSHOT), full_page=True)

        # PLACEHOLDER SELECTOR: verify against the real search box for the
        # recipient/consignee name filter.
        search_box = page.locator(
            "input[placeholder*='收件人'], input[name='receiverName']"
        ).first
        if search_box.count() == 0:
            return None
        search_box.fill(recipient_name)
        search_box.press("Enter")
        page.wait_for_load_state("networkidle")

        # PLACEHOLDER SELECTOR: verify against the real results table cell
        # that holds the international tracking number.
        tracking_cell = page.locator("td.tracking-number, .track-no").first
        if tracking_cell.count() == 0:
            return None
        return tracking_cell.inner_text().strip()
