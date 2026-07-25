"""Entry point for the packaged Cor Bloom Tracking Assistant.

Starts the local web server and opens the browser on it. Run with
--setup-session to redo the manual dianxiaomi login instead of starting the
server.
"""

import os
import socket
import sys
import threading
import time
import webbrowser

from app.paths import app_dir, is_frozen

# In a build, the Chromium that build_exe.bat downloaded is bundled inside the
# playwright package itself, which is what PLAYWRIGHT_BROWSERS_PATH=0 means.
# From source we leave Playwright's normal browser location alone.
if is_frozen():
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "0")

HOST = "127.0.0.1"
PREFERRED_PORT = 8000


def pick_port() -> int:
    for port in (PREFERRED_PORT, 0):
        with socket.socket() as sock:
            try:
                sock.bind((HOST, port))
            except OSError:
                continue
            return sock.getsockname()[1]
    raise RuntimeError("No free port available on 127.0.0.1")


def open_browser_when_up(url: str) -> None:
    deadline = time.time() + 30
    while time.time() < deadline:
        with socket.socket() as sock:
            sock.settimeout(0.5)
            if sock.connect_ex((HOST, int(url.rsplit(":", 1)[1]))) == 0:
                webbrowser.open(url)
                return
        time.sleep(0.3)


def main() -> None:
    if "--setup-session" in sys.argv:
        from app.session_setup import run_interactive_login

        run_interactive_login()
        return

    import uvicorn

    from app.main import app

    if not (app_dir() / ".env").exists():
        print(
            f"WARNING: no .env file found in {app_dir()} - Shopify lookups will be "
            "skipped and every field has to be filled in by hand.\n",
            flush=True,
        )

    port = pick_port()
    url = f"http://{HOST}:{port}"
    print(f"Cor Bloom Tracking Assistant is starting on {url}", flush=True)
    print("Keep this window open while you use the app. Close it to stop.\n", flush=True)

    threading.Thread(target=open_browser_when_up, args=(url,), daemon=True).start()
    uvicorn.run(app, host=HOST, port=port, log_level="info")


if __name__ == "__main__":
    main()
