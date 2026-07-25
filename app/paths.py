"""Path helpers that work both from source and from a PyInstaller build.

In a frozen build the read-only files (templates, carriers.json) are unpacked
into a temporary folder, while everything the user edits or the app writes
(.env, the saved dianxiaomi session, debug screenshots) has to live next to
the .exe so it survives across runs.
"""

import sys
from pathlib import Path


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def bundle_dir() -> Path:
    """Folder containing the read-only files shipped with the app."""
    if is_frozen():
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def app_dir() -> Path:
    """Folder for files the user edits or the app writes."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent
