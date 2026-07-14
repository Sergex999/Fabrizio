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

        try:
            page.screenshot(path=str(DEBUG_SCREENSHOT))
        except Exception:
            pass  # debugging aid only, never block the real lookup

        # Switch the order list into "search" mode.
        page.locator(".switch-search-mode--item", has_text="搜索").click()
        # Pick "收件人" (recipient) as the field to search by.
        page.locator(".d-tag-group-item__inner", has_text="收件人").click()
        # Type the recipient name and submit the search.
        page.fill("#orderSearchInput", recipient_name)
        page.locator("button[type='submit']", has_text="搜索").click()
        page.wait_for_load_state("networkidle")

        # The international tracking number is shown as a clickable span.
        tracking_span = page.locator("span.pointer[title='点击查看物流追踪']").first
        if tracking_span.count() == 0:
            return None
        return tracking_span.inner_text().strip()
