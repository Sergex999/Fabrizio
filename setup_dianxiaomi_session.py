"""One-time interactive login to dianxiaomi.com.

dianxiaomi.com requires a CAPTCHA at login, so this script opens a real
browser window for you to log in by hand (username, password, and the
captcha code). Once you're logged in and see the dianxiaomi dashboard, come
back to this terminal and press Enter to save the session — the app will
then reuse it without logging in again, until the session expires (re-run
this script when that happens).
"""

from app.session_setup import run_interactive_login

if __name__ == "__main__":
    run_interactive_login()
