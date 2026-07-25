# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build of the Cor Bloom Tracking Assistant.

Built as a folder (not a single file): the bundle carries a full Chromium for
Playwright, and a one-file build would unpack all of it to a temp directory on
every launch.
"""

from PyInstaller.utils.hooks import collect_all

datas = [
    ("app/templates", "app/templates"),
    ("app/carriers.json", "app"),
]
binaries = []
hiddenimports = [
    "uvicorn.logging",
    "uvicorn.loops.auto",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan.on",
]

# Pulls in the Playwright driver and, because build_exe.bat installs Chromium
# with PLAYWRIGHT_BROWSERS_PATH=0, the browser that now lives inside the
# playwright package.
pw_datas, pw_binaries, pw_hiddenimports = collect_all("playwright")
datas += pw_datas
binaries += pw_binaries
hiddenimports += pw_hiddenimports

a = Analysis(
    ["run_app.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "tkinter"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CorBloomTrackingAssistant",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="CorBloomTrackingAssistant",
)
