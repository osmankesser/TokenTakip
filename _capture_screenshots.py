"""Ekran goruntuleri — .venv\\Scripts\\python.exe _capture_screenshots.py"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QSettings, QTimer
from PySide6.QtWidgets import QApplication

from overlay import UsageOverlay
from prompt_coach import ChatBurn, CoachReport, Finding
from usage_client import Meter, ProviderUsage, UsageSnapshot

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "screenshots"


def _snap() -> UsageSnapshot:
    return UsageSnapshot(
        checked_at="19:04",
        providers=[
            ProviderUsage(
                name="CURSOR",
                plan="Pro",
                meters=[
                    Meter(label="Toplam", remaining_percent=18, remaining_text="18%", reset_text="3s 12dk"),
                    Meter(label="Otomatik", remaining_percent=42, remaining_text="42%", reset_text="3s 12dk"),
                ],
            ),
            ProviderUsage(
                name="CODEX",
                plan="Plus",
                meters=[
                    Meter(label="5 saat", remaining_percent=88, remaining_text="88%", reset_text="4s 05dk"),
                ],
            ),
            ProviderUsage(
                name="CLAUDE",
                plan="Pro",
                meters=[
                    Meter(label="5 saat", remaining_percent=64, remaining_text="64%", reset_text="1s 40dk"),
                ],
            ),
            ProviderUsage(
                name="GITHUB COPILOT",
                plan="Individual",
                meters=[
                    Meter(label="Premium", remaining_percent=91, remaining_text="91%", reset_text="28 Agustos"),
                ],
            ),
        ],
    )


def _coach() -> CoachReport:
    return CoachReport(
        chats=12,
        chars=184_000,
        tools=34,
        burns=[
            ChatBurn("Cursor", "Refactor overlay", 8, 4, 42_000, "read_file", when="bugun"),
            ChatBurn("Codex", "Build release", 3, 2, 18_500, "shell", when="dun"),
        ],
        findings=[
            Finding("paste", "Cursor", "tum dosyayi yapistirdim...", [], "overlay.py", "bugun", 3),
            Finding("vague", "Codex", "duzelt sunu", [], "", "dun", 2),
        ],
        mcps=["github", "browser"],
        skills=["ponytail"],
    )


def _grab(win: UsageOverlay, name: str) -> None:
    win.show()
    QApplication.processEvents()
    QTimer.singleShot(0, lambda: None)
    QApplication.processEvents()
    path = OUT / name
    assert win.grab().save(str(path)), path
    print(path)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.mkdtemp()
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, tmp)
    s = QSettings("TokenTracker", "ui")
    s.setValue("license_accepted_ver", "1")
    s.setValue("consent_seen", True)
    s.setValue("quota_access", True)
    s.setValue("chat_analysis", True)
    s.sync()

    app = QApplication(sys.argv or ["TokenTracker"])
    win = UsageOverlay(auto_fetch=False, for_test=True)
    win._license_granted = True
    win._quota_access = True
    win._chat_analysis = True

    win.goto("usage")
    win._apply(_snap())
    _grab(win, "01-usage.png")
    _grab(win, "usage-tr.png")

    win._theme = "frost"
    win.panel.setStyleSheet(__import__("overlay")._theme_css("frost"))
    win._sync_theme_surfaces()
    _grab(win, "04-usage-night.png")

    win._theme = "night"
    win.panel.setStyleSheet(__import__("overlay")._theme_css("night"))
    win._sync_theme_surfaces()

    win._lang = "en"
    win._apply_language()
    win.goto("settings")
    _grab(win, "02-settings.png")
    _grab(win, "settings-en.png")

    win._lang = "tr"
    win._apply_language()
    _grab(win, "settings-tr.png")

    win.goto("ideas")
    win._coach = _coach()
    win._fill_ideas()
    _grab(win, "03-ideas.png")

    win.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
