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
DEBUG_HTML = Path(__file__).parent.parent / "dianxiaomi_debug.html"

TRACKING_SPAN = "span.pointer[title='点击查看物流追踪']"


class DianxiaomiClient:
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

        # Dismiss a notice/announcement popup that sometimes covers the page
        # on load and blocks clicks underneath it.
        try:
            page.locator(".notice-list-modal__header-close").first.click(timeout=3000)
        except Exception:
            pass  # no popup this time

        # Switch the order list into "search" mode.
        page.locator(".switch-search-mode--item", has_text="搜索").click()
        # Pick "收件人" (recipient) as the field to search by.
        page.locator(".d-tag-group-item__inner", has_text="收件人").click()
        # Type the recipient name and submit the search.
        page.fill("#orderSearchInput", recipient_name)
        page.locator("button[type='submit']", has_text="搜索").click()

        # The results table re-renders asynchronously after the search, so
        # wait for the tracking span itself rather than checking right away.
        try:
            page.wait_for_selector(TRACKING_SPAN, state="attached", timeout=15000)
        except Exception:
            self._save_debug_artifacts(page)
            return None

        tracking_span = page.locator(TRACKING_SPAN).first
        tracking_text = (tracking_span.text_content() or "").strip()
        if not tracking_text:
            self._save_debug_artifacts(page)
            return None
        return tracking_text
