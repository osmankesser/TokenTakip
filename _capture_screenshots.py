"""Generate deterministic English screenshots for the GitHub release."""
from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

import overlay
from github_live import _fallback_from_catalog
from overlay import STYLE, UsageOverlay
from prompt_coach import ChatBurn, CoachReport, Finding, TokenTip
from usage_client import Meter, ProviderUsage, UsageSnapshot

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "screenshots"


def _snap() -> UsageSnapshot:
    return UsageSnapshot(
        checked_at="21:15",
        providers=[
            ProviderUsage(
                name="CURSOR",
                plan="Pro",
                meters=[
                    Meter(label="Total", remaining_percent=18, remaining_text="18%", reset_text="Resets in 3h 12m"),
                    Meter(label="Auto", remaining_percent=42, remaining_text="42%", reset_text="Resets in 3h 12m"),
                ],
            ),
            ProviderUsage(
                name="CODEX",
                plan="Plus",
                meters=[
                    Meter(label="5 hours", remaining_percent=88, remaining_text="88%", reset_text="Resets in 4h 05m"),
                ],
            ),
            ProviderUsage(
                name="CLAUDE",
                plan="Pro",
                meters=[
                    Meter(label="5 hours", remaining_percent=64, remaining_text="64%", reset_text="Resets in 1h 40m"),
                ],
            ),
            ProviderUsage(
                name="GEMINI",
                plan="Google AI",
                meters=[
                    Meter(label="Gemini 2.5 Pro", remaining_percent=76, remaining_text="76%", reset_text="Daily"),
                ],
            ),
            ProviderUsage(
                name="GITHUB COPILOT",
                plan="Individual",
                meters=[
                    Meter(label="Premium", remaining_percent=91, remaining_text="91%", reset_text="Monthly"),
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
            ChatBurn("Cursor", "Refactor the overlay", 8, 4, 42_000, "read_file", when="today"),
            ChatBurn("Codex", "Build the release", 3, 2, 18_500, "shell", when="yesterday"),
        ],
        findings=[
            Finding("paste", "Cursor", "I pasted the entire file...", [], "overlay.py", "today", 3),
            Finding("vague", "Codex", "Fix this", [], "", "yesterday", 2),
        ],
        tips=[
            TokenTip("tip_paste", weight=100),
            TokenTip("tip_mcp", helpers=["github"], weight=90, detail="github"),
            TokenTip("tip_baseline", weight=10),
        ],
        mcps=["github", "browser"],
        skills=["ponytail"],
    )


def _grab(win: UsageOverlay, name: str) -> None:
    win.show()
    deadline = time.monotonic() + 0.32
    while time.monotonic() < deadline:
        QApplication.processEvents()
        time.sleep(0.01)
    path = OUT / name
    assert win.grab().save(str(path)), path
    print(path)


def _theme(win: UsageOverlay, name: str) -> None:
    win._theme = name
    win.panel.setProperty("theme", name)
    win.setStyleSheet(STYLE)
    win.panel.setStyleSheet(overlay._theme_css(name))
    win._sync_theme_surfaces()
    win._refresh_theme_icons()
    win._sync_nav(force=True)


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
    win.resize(420, 720)
    win._lang = "en"
    win._apply_language()

    _theme(win, "night")
    win.goto("usage")
    win._apply(_snap())
    win._set_live_state("live")
    _grab(win, "01-overview.png")

    _theme(win, "frost")
    win._coach = _coach()
    win.goto("ideas")
    _grab(win, "02-ideas.png")

    win.goto("agents")
    _grab(win, "03-agents.png")

    win._gh_projects = _fallback_from_catalog()
    win.goto("github")
    _grab(win, "04-github.png")

    win._gh_detail_repo = win._gh_projects[0].repo
    win.goto("github_detail")
    _grab(win, "05-github-detail.png")

    _theme(win, "aurora")
    win.goto("settings")
    win.set_pct_decimals(4)
    win._settings_scroll.ensureWidgetVisible(win.pct_dec_label)
    _grab(win, "06-settings.png")

    win.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
