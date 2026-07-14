"""One-time interactive login to dianxiaomi.com.

dianxiaomi.com requires a CAPTCHA at login, so this script opens a real
browser window for you to log in by hand (username, password, and the
captcha code). Once you're logged in and see the dianxiaomi dashboard, come
back to this terminal and press Enter to save the session — the app will
then reuse it without logging in again, until the session expires (re-run
this script when that happens).
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

STATE_FILE = Path(__file__).parent / "dianxiaomi_state.json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.dianxiaomi.com/index.htm")
    input(
        "Log in manually in the browser window (username, password, captcha).\n"
        "Once you see the dianxiaomi dashboard, come back here and press Enter..."
    )
    context.storage_state(path=str(STATE_FILE))
    browser.close()
    print(f"Session saved to {STATE_FILE}")
