"""Floating pill nav — orta stil (aktif bubble + home line)."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from time import sleep

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QFrame

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from overlay import NAV_ITEMS, NavPill, UsageOverlay, _NAV_BUBBLE, _NAV_GLYPH_PX  # noqa: E402


def check(name: str, ok: bool, detail: str = "") -> None:
    mark = "OK" if ok else "FAIL"
    extra = f" — {detail}" if detail else ""
    print(f"[{mark}] {name}{extra}", flush=True)
    if not ok:
        raise SystemExit(1)


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    tmp = tempfile.TemporaryDirectory()
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, tmp.name)
    QSettings("TokenTracker", "ui").setValue("license_accepted_ver", "1")

    win = UsageOverlay(auto_fetch=False, for_test=True)
    win.show()
    app.processEvents()

    check("NAV_ITEMS 5", len(NAV_ITEMS) == 5)
    check("nav btn sayısı", len(win._nav_btns) == len(NAV_ITEMS))
    pills = win.findChildren(NavPill)
    check("NavPill var", len(pills) == 1)
    check("aktif kota", win.home_btn._active is True and win.home_btn._lift >= 0.99)
    check("pasif öneriler", win.ideas_btn._active is False and win.ideas_btn._lift <= 0.01)
    check("tüm ikonlar boyalı", all(not b._pix.isNull() for b in win._nav_btns))

    hl = [f for f in win.findChildren(QFrame) if f.objectName() == "navHomeLine"]
    check("home indicator", len(hl) == 1 and hl[0].parent() is pills[0])

    win.ideas_btn.click()
    app.processEvents()
    check("anim başladı", win.ideas_btn._anim.state() == win.ideas_btn._anim.State.Running or win.ideas_btn._lift > 0)

    for _ in range(40):
        app.processEvents()
        if win.ideas_btn._lift >= 0.99 and win.home_btn._lift <= 0.01:
            break
        sleep(0.02)
    check("aktif taşındı", win.ideas_btn._active is True and win.ideas_btn._lift >= 0.99)
    check("kota pasif", win.home_btn._active is False and win.home_btn._lift <= 0.01)
    check("paint icon", not win.ideas_btn._pix.isNull() and win.ideas_btn._pix.width() == _NAV_GLYPH_PX)
    check("bubble widget", win.home_btn.bubble.width() >= _NAV_BUBBLE)
    # Takılma kaynağı olmamalı
    check("stylesheet yok", win.ideas_btn.bubble.styleSheet() == "")
    check("graphicsEffect yok", win.ideas_btn.bubble.graphicsEffect() is None)
    accent = win.theme_accent().name().lower()
    check("tema accent css", accent in win.panel.styleSheet().lower())

    win.set_theme("aurora")
    app.processEvents()
    app.processEvents()
    check("aurora accent", win.theme_accent().name().lower() in win.panel.styleSheet().lower())
    check("aurora bubble aktif", win.ideas_btn._active is True and win.ideas_btn._lift >= 0.99)

    print("NAV PILL OK", flush=True)
    os._exit(0)


if __name__ == "__main__":
    raise SystemExit(main())
