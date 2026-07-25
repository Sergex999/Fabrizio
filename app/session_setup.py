"""One-time interactive login to dianxiaomi.com.

dianxiaomi.com requires a CAPTCHA at login, so this opens a real browser
window for a manual login. The resulting cookies are saved next to the app so
DianxiaomiClient can reuse them without logging in again.
"""

from playwright.sync_api import sync_playwright

from app.paths import app_dir

LOGIN_URL = "https://www.dianxiaomi.com/index.htm"
STATE_FILE = app_dir() / "dianxiaomi_state.json"


def run_interactive_login() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(LOGIN_URL)
        input(
            "Log in manually in the browser window (username, password, captcha).\n"
            "Once you see the dianxiaomi dashboard, come back here and press Enter..."
        )
        context.storage_state(path=str(STATE_FILE))
        browser.close()
    print(f"Session saved to {STATE_FILE}")
