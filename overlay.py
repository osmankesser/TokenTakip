"""PC kota penceresi. Görsel: açık panel, üç sayfa, simgeler kodla."""

from __future__ import annotations

import os
import shutil
import sys
from collections import Counter, deque
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Literal

from math import cos, pi, sin

from platform_util import (
    STARTUP_ARG,
    app_cache_dir,
    platform_ok,
    set_startup as _set_startup,
    show_platform_error,
    startup_on as _startup_on,
    startup_registered as _startup_registered,
)

from PySide6.QtCore import (
    QEvent,
    QObject,
    QPoint,
    QPointF,
    Property,
    QEasingCurve,
    QPropertyAnimation,
    QRectF,
    QSettings,
    QSize,
    QStandardPaths,
    Qt,
    QThread,
    QTime,
    QTimer,
    QUrl,
    Signal,
)
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtGui import (
    QAction,
    QColor,
    QFont,
    QDesktopServices,
    QGuiApplication,
    QIcon,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRegion,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

ROOT = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lang_packs import TEXTS, validate_langs  # noqa: E402
from prompt_coach import CoachReport, Finding, PATHY, build_report  # noqa: E402
from agent_advice import build_agent_advice  # noqa: E402
from agent_catalog import discover_agent_kits  # noqa: E402
from agent_story import build_agent_story  # noqa: E402
from github_live import (  # noqa: E402
    LiveProject,
    build_guide,
    fetch_top_projects,
    get_project,
    localize_blurb,
    localize_guide,
    ranked_live,
)
from weekly_projects import (  # noqa: E402
    CAT_ORDER,
    agents_from_providers,
    detect_local_agents,
)
from usage_client import Meter, ProviderUsage, UsageSnapshot, _sort_key, fetch_snapshot  # noqa: E402

THEMES = ("night", "frost", "aurora", "ember")
THEME_TR = {"night": "Gece", "frost": "Buz", "aurora": "Aurora", "ember": "Kor"}  # legacy; use t("theme_*")
THEME_PALETTE = {
    "frost": {
        "shell_bg": "#f8fbff", "shell_bg2": "#eef6ff", "shell_border": "#cfe3f8",
        "content": "#f1f7fd", "card": "#ffffff", "card_border": "#dbeafe",
        "text": "#1e3a5f", "title": "#0c1929", "muted": "#486581", "faint": "#8ba3bd",
        "accent": "#0369a1", "accent_deep": "#075985", "accent_soft": "#dbeafe",
        "accent_bg": "#e0f2fe", "accent_border": "#bae6fd", "line": "#dbeafe",
        "segment": "#e8f2fc", "icon_mark": "#f0f9ff", "icon_mark_border": "#cfe8ff",
        "field_border": "#93c5fd", "icon": "#475569", "success": "#047857", "success_soft": "#d1fae5",
        "error": "#b91c1c", "bar_ok": "#0ea5e9", "bar_warn": "#eab308", "bar_crit": "#ef4444",
        "card_crit_bg": "#fff7f7", "card_crit_border": "#fecaca",
        "idea_warn_bg": "#fffbeb", "idea_warn_border": "#fde68a",
        "idea_info_bg": "#eff6ff", "idea_info_border": "#93c5fd",
        "idea_danger_bg": "#fef2f2", "idea_danger_border": "#fecaca",
    },
    "night": {
        "shell_bg": "#0a101c", "shell_bg2": "#141c2b", "shell_border": "#2d3f58",
        "content": "#0f1623", "card": "#1a2438", "card_border": "#334866",
        "text": "#e2e8f0", "title": "#f8fafc", "muted": "#b0bdd0", "faint": "#8494a8",
        "accent": "#38bdf8", "accent_deep": "#0369a1", "accent_soft": "#1a3348",
        "accent_bg": "#102a44", "accent_border": "#1e5a7a", "line": "#243044",
        "segment": "#1a2438", "icon_mark": "#151f33", "icon_mark_border": "#3d4f68",
        "field_border": "#4b5f78", "icon": "#cbd5e1", "success": "#4ade80", "success_soft": "#064e3b",
        "error": "#fca5a5", "bar_ok": "#38bdf8", "bar_warn": "#eab308", "bar_crit": "#f87171",
        "card_crit_bg": "#281818", "card_crit_border": "#dc2626",
        "idea_warn_bg": "#252118", "idea_warn_border": "#a16207",
        "idea_info_bg": "#152238", "idea_info_border": "#2563eb",
        "idea_danger_bg": "#281818", "idea_danger_border": "#dc2626",
    },
    "aurora": {
        "shell_bg": "#faf5ff", "shell_bg2": "#ede9fe", "shell_border": "#c4b5fd",
        "content": "#f5f3ff", "card": "#ffffff", "card_border": "#ddd6fe",
        "text": "#3730a3", "title": "#1e1b4b", "muted": "#6366b1", "faint": "#8b5cf6",
        "accent": "#7c3aed", "accent_deep": "#6d28d9", "accent_soft": "#ede9fe",
        "accent_bg": "#f3e8ff", "accent_border": "#d8b4fe", "line": "#e9d5ff",
        "segment": "#ede9fe", "icon_mark": "#faf5ff", "icon_mark_border": "#ddd6fe",
        "field_border": "#a78bfa", "icon": "#5b21b6", "success": "#047857", "success_soft": "#d1fae5",
        "error": "#b91c1c", "bar_ok": "#8b5cf6", "bar_warn": "#eab308", "bar_crit": "#f43f5e",
        "card_crit_bg": "#fff1f2", "card_crit_border": "#fda4af",
        "idea_warn_bg": "#fffbeb", "idea_warn_border": "#fcd34d",
        "idea_info_bg": "#eef2ff", "idea_info_border": "#818cf8",
        "idea_danger_bg": "#fff1f2", "idea_danger_border": "#fda4af",
    },
    "ember": {
        "shell_bg": "#fff7ed", "shell_bg2": "#ffedd5", "shell_border": "#fdba74",
        "content": "#fff4e8", "card": "#fffbf7", "card_border": "#fed7aa",
        "text": "#7c2d12", "title": "#431407", "muted": "#9a3412", "faint": "#c2410c",
        "accent": "#c2410c", "accent_deep": "#9a3412", "accent_soft": "#ffedd5",
        "accent_bg": "#ffedd5", "accent_border": "#fdba74", "line": "#fed7aa",
        "segment": "#ffe8cc", "icon_mark": "#fff7ed", "icon_mark_border": "#fdba74",
        "field_border": "#fb923c", "icon": "#9a3412", "success": "#047857", "success_soft": "#dcfce7",
        "error": "#b91c1c", "bar_ok": "#f97316", "bar_warn": "#eab308", "bar_crit": "#ef4444",
        "card_crit_bg": "#fff1f2", "card_crit_border": "#fecaca",
        "idea_warn_bg": "#fef9c3", "idea_warn_border": "#facc15",
        "idea_info_bg": "#fff7ed", "idea_info_border": "#fb923c",
        "idea_danger_bg": "#fee2e2", "idea_danger_border": "#f87171",
    },
}
THEME_KEYS = (
    "shell_bg", "shell_bg2", "shell_border", "content", "card", "card_border",
    "text", "title", "muted", "faint", "accent", "accent_deep", "accent_soft",
    "accent_bg", "accent_border", "line", "segment", "icon_mark", "icon_mark_border",
    "field_border", "icon", "success", "success_soft", "error",
    "bar_ok", "bar_warn", "bar_crit", "card_crit_bg", "card_crit_border",
    "idea_warn_bg", "idea_warn_border", "idea_info_bg", "idea_info_border",
    "idea_danger_bg", "idea_danger_border",
)


def _check_theme_palettes() -> None:
    for name in THEMES:
        pal = THEME_PALETTE.get(name)
        if not pal:
            raise ValueError(f"THEME_PALETTE eksik: {name}")
        missing = [k for k in THEME_KEYS if k not in pal]
        if missing:
            raise ValueError(f"Tema {name} eksik anahtar: {missing}")


def _lum(hex_c: str) -> float:
    h = hex_c.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))

    def chan(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def _contrast(fg: str, bg: str) -> float:
    l1, l2 = _lum(fg), _lum(bg)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


# ponytail: WCAG AA — gövde 4.5:1, büyük/buton 3:1; tema paleti yüklemede doğrulanır
_THEME_CONTRAST_PAIRS = (
    ("govde", "text", "card", 4.5),
    ("baslik", "title", "card", 3.0),
    ("ikincil", "muted", "card", 4.5),
    ("ikincil-icerik", "muted", "content", 4.5),
    ("plan-rozet", "accent", "accent_bg", 4.5),
    ("seg-pasif", "text", "segment", 4.5),
    ("kota-yesil", "success", "card", 4.5),
    ("nav-pasif", "muted", "content", 4.5),
    ("nav-aktif", "accent", "content", 4.5),
    ("ikon", "icon", "content", 4.5),
    ("idea-govde-warn", "muted", "idea_warn_bg", 4.5),
    ("idea-govde-info", "muted", "idea_info_bg", 4.5),
    ("idea-govde-danger", "muted", "idea_danger_bg", 4.5),
    ("btn-beyaz", "#ffffff", "accent_deep", 3.0),
    ("hata", "error", "card", 4.5),
)


def _check_theme_contrast() -> None:
    for theme in THEMES:
        p = THEME_PALETTE[theme]
        for label, fg_k, bg_k, need in _THEME_CONTRAST_PAIRS:
            fg = p[fg_k] if fg_k in p else fg_k
            bg = p[bg_k]
            got = _contrast(fg, bg)
            if got < need:
                raise ValueError(f"Tema {theme} kontrast {label}: {got:.2f} < {need} ({fg} / {bg})")


_check_theme_palettes()
_check_theme_contrast()
from version import VERSION  # noqa: E402
# Next legal draft: carve out LGPL PySide6/shiboken6/Qt replace + debug reverse-eng + lawful interoperability from any general RE limit.
LICENSE_DOC_VER = "1"
LICENSE_FILENAME = "LISANS-SOZLESMESI.txt"


def resolve_license_path(override: Path | str | None = None) -> Path:
    if override is not None:
        return Path(override)
    return ROOT / LICENSE_FILENAME


def read_license_text(path: Path | str) -> tuple[str | None, Literal["", "missing", "empty", "unreadable"]]:
    p = Path(path)
    try:
        if not p.is_file():
            return None, "missing"
        text = p.read_text(encoding="utf-8")
    except OSError:
        return None, "unreadable"
    if not text.strip():
        return None, "empty"
    return text, ""

APP_NAME = "Token Tracker"
APP_ID = "TokenTracker"
SETTINGS_ORG = "TokenTracker"
_INSTANCE_SOCK = "TokenTracker.single"
RUN_NAME = "TokenTracker"
_RUN_LEGACY = "PulseTokenTakip"
ROUND = 18
DOMAINS = {
    "CURSOR": "cursor.com",
    "CHATGPT": "chatgpt.com",
    "CODEX": "openai.com",
    "CLAUDE": "claude.ai",
    "GEMINI": "gemini.google.com",
    "COPILOT": "copilot.microsoft.com",
    "OLLAMA": "ollama.com",
    "WINDSURF": "windsurf.com",
    "ANTIGRAVITY": "google.com",
    "CONTINUE": "continue.dev",
    "TRAE": "trae.ai",
    "LM STUDIO": "lmstudio.ai",
    "TABNINE": "tabnine.com",
    "AMAZON Q": "aws.amazon.com",
    "JETBRAINS AI": "jetbrains.com",
    "AIDER": "aider.chat",
    "GROQ": "groq.com",
    "QWEN": "tongyi.aliyun.com",
    "CLINE": "cline.bot",
    "MANUS": "manus.im",
    "CODEIUM": "codeium.com",
    "KIRO": "kiro.dev",
    "WARP": "warp.dev",
}
_ICON_MEM: dict[str, QPixmap] = {}
_LOGO_CUT: QPixmap | None = None
_LOGO_TRIM: QPixmap | None = None
_LOGO_HEADER_PX = 40
_PROVIDER_ICON_PX = 32
_PROVIDER_MARK_PX = 40
_NAV_GLYPH_PX = 16
_NAV_AGENTS_GLYPH_PX = 18
_NAV_BUBBLE = 34
_NAV_ICON_CACHE: dict[tuple[str, str], QPixmap] = {}

# React NavbarTabs tarzı veri — page anahtarı + glif
NAV_ITEMS: tuple[dict[str, str], ...] = (
    {"kind": "kota", "page": "usage", "label": "usage"},
    {"kind": "ideas", "page": "ideas", "label": "ideas"},
    {"kind": "agents", "page": "agents", "label": "agents_nav"},
    {"kind": "github", "page": "github", "label": "github_nav"},
    {"kind": "settings", "page": "settings", "label": "settings"},
)
_ACTION_GLYPH_PX = 20
_STAT_GLYPH_PX = 22
_IDEA_GLYPH_PX = 26
_FLUENT = {
    "kota": 0xE9D2,
    "ideas": 0xEA80,
    "tips": 0xE74B,
    "agents": 0xE716,  # People — nav boyutu için net; özel sarılma okunmuyordu
    "github": 0xE8F1,
    "chat": 0xE8BD,
    "settings": 0xE713,
    "close": 0xE711,
    "clip": 0xE16C,
    "send": 0xE724,
    "warn": 0xE7BA,
    "info": 0xE946,
    "stop": 0xE71A,
    "stat_chat": 0xE8BD,
    "stat_tok": 0xE9D9,
    "stat_tools": 0xE90F,
    "danger": 0xE783,
}
_CHIP_GLYPH_PX = 18
_LIVE_GLYPH_PX = 14
_LIVE_OK = QColor("#22c55e")
_LIVE_ERR = QColor("#ef4444")


def _asset_path(name: str) -> Path:
    if getattr(sys, "frozen", False):
        for base in (Path(getattr(sys, "_MEIPASS", "")), ROOT / "_internal", ROOT):
            if not base:
                continue
            p = base / name
            if p.is_file():
                return p
    return ROOT / name


def _logo_cutout() -> QPixmap | None:
    """logo.png koyu arka planını (siyah + lacivert squircle) şeffaf yap."""
    global _LOGO_CUT
    if _LOGO_CUT is not None and not _LOGO_CUT.isNull():
        return _LOGO_CUT
    path = _asset_path("logo.png")
    if not path.is_file():
        return None
    src = QPixmap(str(path)).toImage().convertToFormat(QImage.Format.Format_ARGB32)
    w, h = src.width(), src.height()
    img = src.copy()
    seen = bytearray(w * h)
    q: deque[tuple[int, int]] = deque()

    def dark(x: int, y: int) -> bool:
        return img.pixelColor(x, y).lightness() <= 58

    for x in range(w):
        for y in (0, h - 1):
            if dark(x, y) and not seen[y * w + x]:
                seen[y * w + x] = 1
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if dark(x, y) and not seen[y * w + x]:
                seen[y * w + x] = 1
                q.append((x, y))
    while q:
        x, y = q.popleft()
        img.setPixelColor(x, y, Qt.transparent)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h:
                i = ny * w + nx
                if not seen[i] and dark(nx, ny):
                    seen[i] = 1
                    q.append((nx, ny))
    _LOGO_CUT = QPixmap.fromImage(img)
    return _LOGO_CUT


def _logo_trimmed() -> QPixmap | None:
    """Kesilmiş logodaki şeffaf kenar boşluğunu at; simge daha büyük görünsün."""
    global _LOGO_TRIM
    if _LOGO_TRIM is not None and not _LOGO_TRIM.isNull():
        return _LOGO_TRIM
    src = _logo_cutout()
    if src is None or src.isNull():
        return None
    img = src.toImage()
    w, h = img.width(), img.height()
    min_x, min_y, max_x, max_y = w, h, -1, -1
    for y in range(h):
        for x in range(w):
            if img.pixelColor(x, y).alpha() > 10:
                if x < min_x:
                    min_x = x
                if y < min_y:
                    min_y = y
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y
    if max_x < min_x:
        return src
    _LOGO_TRIM = src.copy(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    return _LOGO_TRIM


def _logo_pix(size: int = 32) -> QPixmap:
    src = _logo_trimmed()
    if src is None or src.isNull():
        return _letter_pix("T", size)
    return src.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


def _username() -> str:
    return os.environ.get("USERNAME") or os.environ.get("USER") or "kullanıcı"


def _cache_root() -> Path:
    root = app_cache_dir()
    bad = root / "icons" / "copilot.png"
    if bad.is_file():
        bad.unlink(missing_ok=True)
    return root


def _cache_dir() -> Path:
    path = _cache_root() / "icons"
    path.mkdir(parents=True, exist_ok=True)
    return path


def tempfile_fallback() -> str:
    return str(ROOT / ".icon-cache")


def _letter_pix(name: str, size: int = 36) -> QPixmap:
    hue = sum(ord(c) for c in name) % 360
    color = QColor.fromHsv(hue, 140, 200)
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(color)
    p.setPen(Qt.NoPen)
    p.drawEllipse(1, 1, size - 2, size - 2)
    p.setPen(QColor("#ffffff"))
    p.setFont(QFont("Segoe UI", int(size * 0.38), QFont.Bold))
    p.drawText(pix.rect(), Qt.AlignCenter, (name[:1] or "?").upper())
    p.end()
    return pix


# Offline brand marks — no network (privacy: no favicon URLs in overlay).
_BRAND: dict[str, tuple[str, str]] = {
    "CURSOR": ("#1d4ed8", "Cu"),
    "CLAUDE": ("#d97757", "✦"),
    "CODEX": ("#10a37f", "Cx"),
    "CHATGPT": ("#10a37f", "GPT"),
    "OLLAMA": ("#111827", "Ol"),
    "GEMINI": ("#4285f4", "Ge"),
    "COPILOT": ("#2ea8ff", "Co"),
    "WINDSURF": ("#0ea5e9", "Ws"),
    "ANTIGRAVITY": ("#ea4335", "Ag"),
    "CONTINUE": ("#22c55e", "Ct"),
    "TRAE": ("#a855f7", "Tr"),
    "LM STUDIO": ("#6366f1", "LM"),
    "TABNINE": ("#1368e0", "T9"),
    "AMAZON Q": ("#ff9900", "Q"),
    "JETBRAINS AI": ("#fe315d", "JB"),
    "AIDER": ("#0f766e", "Ai"),
    "GROQ": ("#f55036", "Gq"),
    "QWEN": ("#6a3de8", "Qw"),
    "CLINE": ("#eab308", "Cn"),
    "MANUS": ("#7c3aed", "Ma"),
    "CODEIUM": ("#09b6a2", "Cd"),
    "KIRO": ("#f59e0b", "Ki"),
    "WARP": ("#01a4ef", "Wp"),
}


def _brand_pix(name: str, size: int = 36) -> QPixmap:
    key = name.upper()
    if key == "COPILOT":
        return _copilot_pix(size)
    color_hex, label = _BRAND.get(key, ("#64748b", (name[:1] or "?").upper()))
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.TextAntialiasing)
    p.setBrush(QColor(color_hex))
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(1, 1, size - 2, size - 2, size * 0.22, size * 0.22)
    p.setPen(QColor("#ffffff"))
    scale = 0.28 if len(label) >= 3 else (0.34 if len(label) == 2 else 0.42)
    p.setFont(QFont("Segoe UI", max(7, int(size * scale)), QFont.Bold))
    p.drawText(pix.rect(), Qt.AlignCenter, label)
    p.end()
    return pix


def _icon_files(name: str) -> list[Path]:
    """Yerel .ico/.png/.exe adayları — ağ yok."""
    key = name.upper()
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    roaming = Path(os.environ.get("APPDATA", ""))
    pf = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
    pkgs = local / "Packages"
    out: list[Path] = []
    hits: dict[str, list[Path]] = {
        "OLLAMA": [
            local / "Programs" / "Ollama" / "app.ico",
            local / "Programs" / "Ollama" / "Ollama.exe",
        ],
        "CHATGPT": [
            local / "Microsoft" / "WindowsApps" / "chatgpt-classic.exe",
            local / "Programs" / "ChatGPT" / "ChatGPT.exe",
        ],
        "CLAUDE": [
            local / "Claude" / "Claude.exe",
            local / "Programs" / "Claude" / "Claude.exe",
            pf / "Claude" / "Claude.exe",
        ],
        "CURSOR": [
            local / "Programs" / "cursor" / "Cursor.exe",
            local / "Programs" / "Cursor" / "Cursor.exe",
        ],
        "WINDSURF": [local / "Programs" / "Windsurf" / "Windsurf.exe"],
        "TRAE": [local / "Programs" / "Trae" / "Trae.exe"],
        "LM STUDIO": [local / "Programs" / "LM Studio" / "LM Studio.exe"],
    }
    out.extend(hits.get(key, []))
    # Store package logos (best-effort)
    prefixes = {
        "CLAUDE": "Claude_",
        "CHATGPT": "OpenAI.ChatGPT",
        "CODEX": "OpenAI.Codex",
        "MANUS": "Manus",
    }
    prefix = prefixes.get(key)
    if prefix and pkgs.is_dir():
        try:
            for pkg in pkgs.iterdir():
                if not pkg.name.startswith(prefix):
                    continue
                for pat in ("**/icon-128.png", "**/logo*.png", "**/StoreLogo*.png", "**/AppList*.png"):
                    for path in pkg.glob(pat):
                        if path.is_file() and 400 < path.stat().st_size < 400_000:
                            out.append(path)
                            if len(out) > 12:
                                return out
        except OSError:
            pass
    return out


def _pix_from_file(path: Path, size: int) -> QPixmap | None:
    if not path.is_file():
        return None
    if path.suffix.lower() == ".exe":
        return _pix_from_exe(path, size)
    pix = QPixmap(str(path))
    if pix.isNull():
        icon = QIcon(str(path))
        if icon.isNull():
            return None
        pix = icon.pixmap(size, size)
    if pix.isNull():
        return None
    return pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


def _exe_for(name: str) -> Path | None:
    key = name.upper()
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs"
    roaming = Path(os.environ.get("APPDATA", ""))
    pf = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
    la = Path(os.environ.get("LOCALAPPDATA", ""))
    hits = {
        "CURSOR": [local / "cursor" / "Cursor.exe", local / "Cursor" / "Cursor.exe"],
        "OLLAMA": [local / "Ollama" / "Ollama.exe", pf / "Ollama" / "Ollama.exe"],
        "CHATGPT": [
            la / "Microsoft" / "WindowsApps" / "chatgpt-classic.exe",
            local / "ChatGPT" / "ChatGPT.exe",
            pf / "ChatGPT" / "ChatGPT.exe",
        ],
        "CLAUDE": [
            la / "Claude" / "Claude.exe",
            local / "Claude" / "Claude.exe",
            pf / "Claude" / "Claude.exe",
        ],
        "WINDSURF": [local / "Windsurf" / "Windsurf.exe"],
        "TRAE": [local / "Trae" / "Trae.exe"],
        "LM STUDIO": [local / "LM Studio" / "LM Studio.exe"],
        "GEMINI": [roaming / "Google" / "Gemini" / "Gemini.exe"],
        "COPILOT": [
            local / "Programs" / "Microsoft VS Code" / "Code.exe",
            pf / "Microsoft VS Code" / "Code.exe",
            local / "Programs" / "Microsoft VS Code Insiders" / "Code - Insiders.exe",
        ],
    }.get(key, [])
    for path in hits:
        if path.is_file():
            return path
    which = {
        "CURSOR": "cursor",
        "OLLAMA": "ollama",
        "CODEX": "codex",
        "CLAUDE": "claude",
        "WINDSURF": "windsurf",
        "TRAE": "trae",
    }.get(key)
    if which:
        found = shutil.which(which)
        if found:
            path = Path(found)
            if path.suffix.lower() == ".exe":
                return path
    return None


def _pix_from_exe(path: Path, size: int) -> QPixmap | None:
    icon = QIcon(str(path))
    if icon.isNull():
        return None
    pix = icon.pixmap(size, size)
    return None if pix.isNull() else pix


def _pix_from_cache(name: str, size: int) -> QPixmap | None:
    key = f"{name.lower().replace(' ', '_')}.png"
    for base in (_cache_root() / "icons",):
        path = base / key
        if not path.is_file():
            continue
        pix = QPixmap(str(path))
        if pix.isNull():
            continue
        return pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return None


def _copilot_pix(size: int) -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    m = size * 0.12
    r = QRectF(m, m, size - 2 * m, size - 2 * m)
    grad = QLinearGradient(r.topLeft(), r.bottomRight())
    grad.setColorAt(0, QColor("#2ea8ff"))
    grad.setColorAt(1, QColor("#9b6bff"))
    p.setBrush(grad)
    p.setPen(Qt.NoPen)
    p.drawEllipse(r)
    p.setPen(QColor("#ffffff"))
    p.setFont(QFont("Segoe UI", max(8, int(size * 0.34)), QFont.Bold))
    p.drawText(r, Qt.AlignCenter, "C")
    p.end()
    return pix


def provider_pix(name: str, size: int = 36) -> QPixmap:
    key = f"{name}:{size}"
    if key in _ICON_MEM:
        return _ICON_MEM[key]
    pix = _pix_from_cache(name, size)
    if pix is None:
        exe = _exe_for(name)
        pix = _pix_from_exe(exe, size) if exe else None
    if pix is None:
        for path in _icon_files(name):
            pix = _pix_from_file(path, size)
            if pix is not None:
                break
    if pix is None:
        pix = _brand_pix(name, size)
    _ICON_MEM[key] = pix
    return pix


def _round_provider_pix(name: str, size: int = 56) -> QPixmap:
    """Yuvarlak kırpılmış ajan logosu."""
    key = f"round:{name}:{size}"
    if key in _ICON_MEM:
        return _ICON_MEM[key]
    src = provider_pix(name, size)
    scaled = src.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    out = QPixmap(size, size)
    out.fill(Qt.transparent)
    p = QPainter(out)
    p.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0.5, 0.5, size - 1, size - 1)
    p.setClipPath(path)
    x = (size - scaled.width()) // 2
    y = (size - scaled.height()) // 2
    p.drawPixmap(x, y, scaled)
    p.setClipping(False)
    p.setPen(QPen(QColor(255, 255, 255, 40), 1))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(1, 1, size - 2, size - 2)
    p.end()
    _ICON_MEM[key] = out
    return out


def _pix_has_ink(pix: QPixmap) -> bool:
    img = pix.toImage()
    for row in range(img.height()):
        for col in range(img.width()):
            if img.pixelColor(col, row).alpha() > 24:
                return True
    return False


def _font_pix(ch: str, color: QColor, size: int, families: tuple[str, ...], scale: float = 0.72) -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.TextAntialiasing)
    for family in families:
        f = QFont(family, max(10, int(size * scale)))
        p.setFont(f)
        if p.fontMetrics().horizontalAdvance(ch) < 2:
            continue
        p.setPen(color)
        p.drawText(pix.rect(), Qt.AlignCenter, ch)
        break
    p.end()
    return pix


def _glyph(kind: str, color: QColor, size: int = 22, phase: float = 0.0, press: float = 0.0) -> QPixmap:
    cp = _FLUENT.get(kind)
    if cp is not None:
        # People glifi diğerlerinden daha geniş; aynı kutuda kenarlara yapışmasın.
        scale = 0.68 if kind == "agents" else 0.78
        pix = _font_pix(chr(cp), color, size, ("Segoe Fluent Icons", "Segoe MDL2 Assets"), scale)
        if _pix_has_ink(pix):
            return pix
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    pen = QPen(color, max(2.0, size * 0.09))
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    m = size * 0.18
    r = QRectF(m, m, size - 2 * m, size - 2 * m)
    if kind == "kota":
        p.drawEllipse(r)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(r.center())
        path.arcTo(r, 90, -230)
        path.closeSubpath()
        p.drawPath(path)
    elif kind == "ideas":
        path = QPainterPath()
        path.moveTo(r.center().x(), r.top())
        path.lineTo(r.right(), r.bottom())
        path.lineTo(r.left(), r.bottom())
        path.closeSubpath()
        p.drawPath(path)
        p.drawLine(int(r.center().x()), int(r.top() + r.height() * 0.38), int(r.center().x()), int(r.bottom() - 6))
        p.drawPoint(int(r.center().x()), int(r.bottom() - 3))
    elif kind == "tips":
        c = r.center()
        p.drawLine(QPointF(c.x(), r.top() + 2), QPointF(c.x(), r.bottom() - 6))
        p.drawLine(QPointF(c.x(), r.bottom() - 6), QPointF(c.x() - 5, r.bottom() - 12))
        p.drawLine(QPointF(c.x(), r.bottom() - 6), QPointF(c.x() + 5, r.bottom() - 12))
        p.drawLine(QPointF(r.left() + 3, r.bottom() - 2), QPointF(r.right() - 3, r.bottom() - 2))
    elif kind == "agents":
        # Fluent People yoksa yedek: iki kafa + omuz
        hr = r.width() * 0.16
        lx = r.left() + r.width() * 0.30
        rx = r.right() - r.width() * 0.30
        ly = r.top() + r.height() * 0.28
        p.drawEllipse(QPointF(lx, ly), hr, hr)
        p.drawEllipse(QPointF(rx, ly), hr, hr)
        p.drawArc(QRectF(lx - hr * 1.3, ly + hr * 0.5, hr * 2.6, r.height() * 0.65), 25 * 16, 130 * 16)
        p.drawArc(QRectF(rx - hr * 1.3, ly + hr * 0.5, hr * 2.6, r.height() * 0.65), 25 * 16, 130 * 16)
    elif kind == "github":
        # simple repo mark: circle + fork-ish lines
        c = r.center()
        p.drawEllipse(QPointF(c.x(), c.y() - 2), r.width() * 0.22, r.width() * 0.22)
        p.drawLine(QPointF(c.x(), c.y() + 2), QPointF(c.x(), r.bottom() - 3))
        p.drawLine(QPointF(c.x(), c.y() + 4), QPointF(r.right() - 4, r.bottom() - 6))
        p.drawEllipse(QPointF(r.right() - 4, r.bottom() - 6), 2.2, 2.2)
    elif kind == "live_ok":
        c = r.center()
        rad = r.width() * 0.28
        glow = QColor(color)
        glow.setAlpha(70)
        p.setPen(Qt.NoPen)
        p.setBrush(glow)
        p.drawEllipse(c, rad * 1.55, rad * 1.55)
        p.setBrush(color)
        p.drawEllipse(c, rad, rad)
    elif kind == "live_err":
        # inverted triangle (point down) + bang
        path = QPainterPath()
        path.moveTo(r.left() + 2, r.top() + 3)
        path.lineTo(r.right() - 2, r.top() + 3)
        path.lineTo(r.center().x(), r.bottom() - 2)
        path.closeSubpath()
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawPath(path)
        p.setPen(QPen(QColor("#ffffff"), max(1.6, size * 0.09), Qt.SolidLine, Qt.RoundCap))
        cx = r.center().x()
        p.drawLine(QPointF(cx, r.top() + r.height() * 0.28), QPointF(cx, r.top() + r.height() * 0.58))
        p.setBrush(QColor("#ffffff"))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, r.top() + r.height() * 0.70), size * 0.05, size * 0.05)
    elif kind == "chat":
        p.drawRoundedRect(r.adjusted(0, 0, 0, -4), 4, 4)
        p.drawLine(int(r.left() + 4), int(r.bottom() - 4), int(r.left() + 8), int(r.bottom()))
    elif kind == "settings":
        p.drawEllipse(r.adjusted(6, 6, -6, -6))
        c = r.center()
        for i in range(8):
            a = i * pi / 4
            p.drawLine(c.x() + 5 * cos(a), c.y() + 5 * sin(a), c.x() + 9 * cos(a), c.y() + 9 * sin(a))
    elif kind == "refresh":
        p.drawArc(r, 40 * 16, 270 * 16)
        p.setBrush(color)
        tip = r.topRight().toPoint()
        p.drawPolygon([tip, tip + QPoint(-5, 6), tip + QPoint(4, 8)])
    elif kind == "tray_token":
        drop = (phase + press * 0.45) * size * 0.11
        pen_w = max(2.0, size * 0.10)
        pen = QPen(color, pen_w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        bx = r.left() + 1
        by = r.bottom() - 2
        bw = r.width() - 2
        lip = size * 0.12
        p.drawLine(QPointF(bx, by - lip), QPointF(bx, by))
        p.drawLine(QPointF(bx, by), QPointF(bx + bw, by))
        p.drawLine(QPointF(bx + bw, by), QPointF(bx + bw, by - lip))
        coin = size * 0.50
        cx = r.center().x()
        cy = by - lip - coin * 0.38 + drop
        circle = QRectF(cx - coin / 2, cy - coin / 2, coin, coin)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(circle)
        p.setBrush(color)
        pie = QPainterPath()
        pie.moveTo(circle.center())
        pie.arcTo(circle, 105, -210)
        pie.closeSubpath()
        p.drawPath(pie)
    elif kind == "close":
        pen_w = max(2.5, size * 0.125)
        p.setPen(QPen(color, pen_w, Qt.SolidLine, Qt.RoundCap))
        half = r.width() * (0.34 + phase * 0.06 - press * 0.04)
        c = r.center()
        p.save()
        p.translate(c)
        p.rotate(phase * 90.0)
        p.drawLine(QPointF(-half, -half), QPointF(half, half))
        p.drawLine(QPointF(half, -half), QPointF(-half, half))
        p.restore()
    elif kind == "clip":
        p.drawArc(r.adjusted(6, 2, -6, -8), 0, 180 * 16)
        p.drawLine(int(r.left() + 6), int(r.center().y() - 2), int(r.left() + 6), int(r.bottom() - 4))
        p.drawLine(int(r.right() - 6), int(r.center().y() - 2), int(r.right() - 6), int(r.bottom() - 4))
    elif kind == "send":
        path = QPainterPath()
        path.moveTo(r.left(), r.top())
        path.lineTo(r.right(), r.center().y())
        path.lineTo(r.left(), r.bottom())
        path.lineTo(r.left() + 4, r.center().y())
        path.closeSubpath()
        p.setBrush(color)
        p.setPen(Qt.NoPen)
        p.drawPath(path)
    elif kind == "warn":
        path = QPainterPath()
        path.moveTo(r.center().x(), r.top())
        path.lineTo(r.right(), r.bottom())
        path.lineTo(r.left(), r.bottom())
        path.closeSubpath()
        p.setBrush(color)
        p.setPen(Qt.NoPen)
        p.drawPath(path)
        p.setPen(QPen(QColor("#ffffff"), 1.2))
        p.drawLine(int(r.center().x()), int(r.top() + 4), int(r.center().x()), int(r.center().y()))
        p.drawPoint(int(r.center().x()), int(r.bottom() - 4))
    elif kind == "info":
        p.setBrush(color)
        p.setPen(Qt.NoPen)
        p.drawEllipse(r)
        p.setPen(QPen(QColor("#ffffff"), 1.6))
        p.drawLine(int(r.center().x()), int(r.top() + 4), int(r.center().x()), int(r.center().y() + 1))
        p.drawPoint(int(r.center().x()), int(r.bottom() - 4))
    elif kind == "danger":
        path = QPainterPath()
        path.moveTo(r.center().x(), r.top())
        path.lineTo(r.right(), r.bottom())
        path.lineTo(r.left(), r.bottom())
        path.closeSubpath()
        p.setBrush(color)
        p.setPen(Qt.NoPen)
        p.drawPath(path)
        p.setPen(QPen(QColor("#ffffff"), 1.4))
        p.drawLine(int(r.center().x() - 3), int(r.center().y() - 1), int(r.center().x() + 3), int(r.center().y() + 4))
        p.drawLine(int(r.center().x() + 3), int(r.center().y() - 1), int(r.center().x() - 3), int(r.center().y() + 4))
    elif kind == "stop":
        p.setBrush(Qt.NoBrush)
        p.drawRect(r.adjusted(4, 4, -4, -4))
    elif kind == "stat_chat":
        p.drawRoundedRect(r.adjusted(1, 3, -1, -3), 3, 3)
        p.drawPolygon([
            r.bottomLeft().toPoint() + QPoint(3, -5),
            r.bottomLeft().toPoint() + QPoint(8, -2),
            r.bottomLeft().toPoint() + QPoint(3, 0),
        ])
    elif kind == "stat_tok":
        p.drawLine(int(r.center().x()), int(r.top()), int(r.center().x()), int(r.bottom()))
        p.drawLine(int(r.left()), int(r.center().y()), int(r.right()), int(r.center().y()))
        p.drawEllipse(r.adjusted(5, 5, -5, -5))
    elif kind == "stat_tools":
        p.drawRect(r.adjusted(3, 3, -9, -9))
        p.drawRect(r.adjusted(9, 3, -3, -9))
        p.drawRect(r.adjusted(3, 9, -9, -3))
    p.end()
    return pix


class HeaderIconBtn(QPushButton):
    """Üst başlık — net simge + hover/tık animasyonu."""

    def __init__(self, kind: str, color: QColor, parent=None):
        super().__init__(parent)
        self._kind = kind
        self._icon_color = color
        self._phase = 0.0
        self._press = 0.0
        self._pix = None
        self.setObjectName("roundBtn")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(36, 36)
        self._hover_anim = QPropertyAnimation(self, b"hoverPhase")
        self._hover_anim.setDuration(200)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._press_anim = QPropertyAnimation(self, b"pressPhase")
        self._press_anim.setDuration(140)
        self._press_anim.setEasingCurve(QEasingCurve.Type.OutBack)

    def _hover_phase(self) -> float:
        return self._phase

    def _set_hover_phase(self, value: float) -> None:
        self._phase = value
        self.update()

    hoverPhase = Property(float, _hover_phase, _set_hover_phase)

    def _press_phase(self) -> float:
        return self._press

    def _set_press_phase(self, value: float) -> None:
        self._press = value
        self.update()

    pressPhase = Property(float, _press_phase, _set_press_phase)

    def set_icon_color(self, color: QColor) -> None:
        self._icon_color = color
        self._pix = None
        self.update()

    def enterEvent(self, event) -> None:  # noqa: N802
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._phase)
        self._hover_anim.setEndValue(1.0)
        self._hover_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._phase)
        self._hover_anim.setEndValue(0.0)
        self._hover_anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        self._press_anim.stop()
        self._press_anim.setStartValue(0.0)
        self._press_anim.setEndValue(1.0)
        self._press_anim.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self._press_anim.stop()
        self._press_anim.setStartValue(self._press)
        self._press_anim.setEndValue(0.0)
        self._press_anim.start()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if self._phase > 0.01 or self._press > 0.01:
            alpha = int(24 + 36 * self._phase + 20 * self._press)
            p.setBrush(QColor(100, 116, 139, alpha))
            p.setPen(Qt.NoPen)
            p.drawEllipse(3, 3, self.width() - 6, self.height() - 6)
        scale = 1.0 + self._phase * 0.06 - self._press * 0.08
        px = _ACTION_GLYPH_PX
        x = (self.width() - px) / 2
        y = (self.height() - px) / 2
        if self._pix is None:
            self._pix = _glyph(self._kind, self._icon_color, px, 0.0, 0.0)
        pix = self._pix
        p.translate(self.width() / 2, self.height() / 2)
        p.scale(scale, scale)
        p.translate(-self.width() / 2, -self.height() / 2)
        p.drawPixmap(int(x), int(y), pix)
        p.end()


INTERVALS = (5, 30, 60, 300)
PCT_DECIMALS = (0, 2, 4, 6, 8, 12)
PCT_TEXT_MAX = 20


def _pct_drop(store: dict[str, float], key: str, pct: float | None) -> float | None:
    prev = store.get(key)
    if pct is not None:
        store[key] = pct
    if prev is None or pct is None:
        return None
    drop = prev - pct
    return drop if drop > 0.00005 else None


def _display_name(name: str) -> str:
    m = {"CHATGPT": "ChatGPT", "CODEX": "Codex", "CURSOR": "Cursor", "OLLAMA": "Ollama", "LM STUDIO": "LM Studio", "MANUS": "Manus", "VS CODE": "VS Code"}
    return m.get(name.upper(), name.title())


_KIT_PROVIDER = {
    "Cursor": "CURSOR",
    "Codex": "CODEX",
    "Claude": "CLAUDE",
    "Copilot": "COPILOT",
    "VS Code": "VS CODE",
}


def _kit_for_provider(name: str):
    key = name.upper()
    for kit in discover_agent_kits():
        mapped = _KIT_PROVIDER.get(kit.agent, kit.agent.upper())
        if mapped == key or kit.agent.upper() == key:
            return kit
    return None


def _agent_logo_names(providers) -> list[str]:
    """Kota listesi + yerel kit ajanları — logo ızgarası sırası."""
    names: list[str] = []
    seen: set[str] = set()
    for p in providers or []:
        n = getattr(p, "name", None) or str(p)
        key = n.upper()
        if key in seen:
            continue
        seen.add(key)
        names.append(n)
    for kit in discover_agent_kits():
        mapped = _KIT_PROVIDER.get(kit.agent)
        if not mapped or mapped in seen:
            continue
        seen.add(mapped)
        names.append(mapped)
    return names


def _idea_kind(code: str) -> str:
    if code in ("paste", "rebuild") or code.startswith("tip_"):
        if code.startswith("tip_"):
            return "info"
        return "danger"
    if code == "helper":
        return "info"
    return "warn"


# (dil kodu, yerel ad) — bayrağı flagcdn'den doğrulanmış
LANGS: tuple[tuple[str, str], ...] = (
    ("tr", "Türkçe"),
    ("en", "English"),
    ("es", "Español"),
    ("pt", "Português"),
    ("ar", "العربية"),
    ("fa", "فارسی"),
    ("hi", "हिन्दी"),
    ("bn", "বাংলা"),
    ("ur", "اردو"),
    ("zh", "中文"),
    ("ja", "日本語"),
    ("ko", "한국어"),
    ("vi", "Tiếng Việt"),
    ("ms", "Bahasa Melayu"),
    ("sv", "Svenska"),
    ("cs", "Čeština"),
    ("sk", "Slovenčina"),
    ("hr", "Hrvatski"),
    ("sr", "Српски"),
    ("az", "Azərbaycanca"),
    ("sw", "Kiswahili"),
)
LANG_CODES = {code for code, _ in LANGS}
assert len(LANGS) == 21 == len(LANG_CODES)
validate_langs(LANG_CODES)
# dil kodu -> ülke kodu (flags_draw)
FLAG_ISO = {
    "en": "gb", "zh": "cn", "ja": "jp", "ko": "kr",
    "ar": "sa", "fa": "ir", "hi": "in", "bn": "bd",
    "ur": "pk", "sw": "ke", "sr": "rs", "cs": "cz",
    "vi": "vn", "ms": "my",
}
_FLAG_ICON_PX = 24
_FLAG_ICONS: dict[str, QIcon] = {}


def _flag_country(lang: str) -> str:
    return FLAG_ISO.get(lang, lang)


def _flag_cache_path(lang: str) -> Path:
    return _cache_dir() / "flags" / f"{_flag_country(lang)}.png"


def _flag_asset_path(cc: str) -> Path:
    return ROOT / "assets" / "flags" / f"{cc.lower()}.png"


def _flag_pix(lang: str, size: int = _FLAG_ICON_PX) -> QPixmap:
    cc = _flag_country(lang)
    for path in (_flag_cache_path(lang), _flag_asset_path(cc)):
        if path.is_file() and path.stat().st_size > 180:
            pix = QPixmap(str(path))
            if not pix.isNull() and _pix_has_ink(pix):
                return pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return _letter_pix(lang.upper()[:2], size)


def _fetch_flags_sync(langs: list[str]) -> None:
    """Gomulu PNG bayraklari cache'e kopyala; ag yok."""
    cache_dir = _cache_dir() / "flags"
    cache_dir.mkdir(parents=True, exist_ok=True)
    want = {_flag_country(lang) for lang in langs}
    for stale in cache_dir.glob("*.png"):
        if stale.stem not in want:
            stale.unlink(missing_ok=True)
    for lang in langs:
        cc = _flag_country(lang)
        src = _flag_asset_path(cc)
        dst = _flag_cache_path(lang)
        if src.is_file():
            shutil.copy2(src, dst)
        _FLAG_ICONS.pop(lang, None)


def _flag_icon(lang: str) -> QIcon:
    if lang in _FLAG_ICONS:
        return _FLAG_ICONS[lang]
    icon = QIcon()
    for sz in (16, _FLAG_ICON_PX, 32):
        icon.addPixmap(_flag_pix(lang, sz))
    _FLAG_ICONS[lang] = icon
    return icon



def _theme_css(theme: str) -> str:
    p = THEME_PALETTE.get(theme, THEME_PALETTE["frost"])
    a, ad = p["accent"], p["accent_deep"]
    return f"""
QFrame#contentArea {{ background: {p["content"]}; }}
QFrame#headerLine {{ background: {p["line"]}; }}
QFrame#navBar {{ border: none; background: transparent; }}
QWidget#navWrap {{ background: transparent; }}
QWidget#navTab {{ background: transparent; }}
QLabel#navBubble, QWidget#navBubble {{
    background: transparent; border: none;
}}
QFrame#navHomeLine {{
    background: {p["faint"]}; border: none; border-radius: 2px; max-height: 3px;
}}
QLabel#navText {{ color: {p["muted"]}; }}
QLabel#navText[active="true"] {{ color: {a}; font-weight: 800; }}
QWidget#listInner {{ background: {p["content"]}; }}
QScrollArea#list {{ background: transparent; border: none; }}
QLabel {{ color: {p["text"]}; }}
QLabel#welcomeTitle, QLabel#pageTitle, QLabel#cardName, QLabel#statN, QLabel#ideaTitle {{
    color: {p["title"]};
}}
QLabel#stamp, QLabel#section, QLabel#settingTitle, QLabel#settingHint,
QLabel#meterName, QLabel#meterMeta, QLabel#versionLabel, QLabel#ideaBody,
QLabel#statL, QLabel#ideaDate {{
    color: {p["muted"]};
}}
QCheckBox#switch::indicator {{ background: {p["segment"]}; border-radius: 13px; }}
QCheckBox#switch::indicator:checked {{ background: {a}; }}
QLabel#error {{ color: {p["error"]}; }}
QLabel#ideaSource {{ color: {p["title"]}; }}
QLabel#meterValue, QLabel#leftPct, QLabel#ideaFix {{ color: {p["success"]}; }}
QLabel#leftPct[tone="warn"] {{ color: {p["bar_warn"]}; }}
QLabel#leftPct[tone="crit"] {{ color: {p["bar_crit"]}; }}
QLabel#plan {{
    color: {a}; background: {p["accent_bg"]}; border: 1px solid {p["accent_border"]};
}}
QLabel#planLocal {{
    color: {p["text"]}; background: {p["segment"]}; border: 1px solid {p["card_border"]};
}}
QFrame#card, QFrame#statBox, QFrame#settingRow {{
    background: {p["card"]}; border: 1px solid {p["card_border"]};
}}
QFrame#card[critical="true"] {{
    background: {p["card_crit_bg"]}; border: 1px solid {p["card_crit_border"]};
    border-left: 3px solid {p["bar_crit"]};
}}
QFrame#card[dragging="true"] {{
    background: {p["segment"]}; border: 2px dashed {a};
    min-height: 72px;
}}
QFrame#cardSkeleton {{
    background: {p["segment"]}; border: 1px solid {p["card_border"]}; border-radius: 14px; min-height: 88px;
}}
QLabel#usageSummary {{ color: {p["muted"]}; }}
QLabel#usageOrderHint {{ color: {p["faint"]}; }}
QFrame#ideaCard {{
    background: {p["card"]}; border: 1px solid {p["card_border"]};
}}
QFrame#ideaCard[kind="warn"] {{
    background: {p["idea_warn_bg"]}; border-color: {p["idea_warn_border"]};
}}
QFrame#ideaCard[kind="info"] {{
    background: {p["idea_info_bg"]}; border-color: {p["idea_info_border"]};
}}
QFrame#ideaCard[kind="danger"] {{
    background: {p["idea_danger_bg"]}; border-color: {p["idea_danger_border"]};
}}
QPushButton#lookBtn {{
    background: {p["card"]}; color: {p["title"]}; border: 1px solid {p["field_border"]};
}}
QPushButton#orderBtn {{
    background: transparent; color: {p["muted"]}; border: none;
    border-radius: 6px; padding: 0; font-size: 11px; font-weight: 700; min-height: 0;
}}
QPushButton#orderBtn:hover {{ color: {p["title"]}; background: {p["segment"]}; }}
QFrame#iconMark {{
    background: {p["icon_mark"]}; border: none; border-radius: 20px;
}}
QPushButton#agentLogoBtn {{
    background: transparent; border: none; border-radius: 32px; padding: 0;
}}
QPushButton#agentLogoBtn:hover {{
    background: {p["segment"]};
}}
QLabel#agentLogoName {{
    color: {p["text"]}; font-size: 10px; font-weight: 700;
}}
QLabel#ghCat {{
    color: {p["muted"]}; font-size: 10px; font-weight: 700; letter-spacing: 0.2px;
}}
QLabel#ghRank {{
    color: {p["accent_deep"]}; background: {p["accent_soft"]};
    border: 1px solid {p["accent_border"]}; border-radius: 10px;
    font-size: 11px; font-weight: 800;
}}
QFrame#ghFilterBar {{
    background: {p["segment"]}; border: none; border-radius: 12px;
}}
QFrame#ghTile {{
    background: {p["card"]}; border: 1px solid {p["card_border"]}; border-radius: 12px;
}}
QFrame#ghTile:hover {{
    background: {p["accent_soft"]}; border-color: {p["field_border"]};
}}
QLabel#ghTileTitle {{
    color: {p["title"]}; font-size: 12px; font-weight: 800;
}}
QLabel#ghTileRepo {{
    color: {p["faint"]}; font-size: 9px; font-weight: 600;
}}
QLabel#ghTileBody {{
    color: {p["muted"]}; font-size: 10px;
}}
QLabel#ghCode {{
    color: {p["text"]}; background: {p["segment"]};
    border: 1px solid {p["line"]}; border-radius: 8px;
    padding: 8px; font-family: Consolas, 'Courier New', monospace; font-size: 10px;
}}
QLabel#ghCatChip {{
    color: {p["accent_deep"]}; background: {p["accent_soft"]};
    border: 1px solid {p["accent_border"]}; border-radius: 8px;
    padding: 2px 6px; font-size: 9px; font-weight: 800;
}}
QLabel#ghFitChip {{
    color: {p["success"]}; background: {p["success_soft"]};
    border-radius: 8px; padding: 2px 6px; font-size: 9px; font-weight: 700;
}}
QLabel#ghFitChip[kind="partial"] {{
    color: {p["text"]}; background: {p["segment"]};
}}
QLabel#ghFitChip[kind="gap"] {{
    color: {p["muted"]}; background: transparent; border: 1px solid {p["line"]};
}}
QFrame#segment {{ background: {p["segment"]}; }}
QPushButton#segBtn {{ color: {p["text"]}; }}
QPushButton#segBtn[active="true"] {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {ad}, stop:1 {ad});
    color: #ffffff;
}}
QComboBox {{
    background: {p["card"]}; color: {p["title"]}; border: 1px solid {p["field_border"]};
}}
QComboBox::down-arrow {{ border-top-color: {p["muted"]}; }}
QLabel#navText {{ color: {p["muted"]}; }}
QLabel#navText[active="true"] {{ color: {a}; font-weight: 800; }}
QFrame#ideaCard[kind="warn"] QLabel#ideaBody,
QFrame#ideaCard[kind="warn"] QLabel#ideaTitle,
QFrame#ideaCard[kind="warn"] QLabel#ideaFix,
QFrame#ideaCard[kind="info"] QLabel#ideaBody,
QFrame#ideaCard[kind="info"] QLabel#ideaTitle,
QFrame#ideaCard[kind="info"] QLabel#ideaFix,
QFrame#ideaCard[kind="danger"] QLabel#ideaBody,
QFrame#ideaCard[kind="danger"] QLabel#ideaTitle,
QFrame#ideaCard[kind="danger"] QLabel#ideaFix,
QFrame#ideaCard[kind="danger"] QLabel#ideaSource {{
    color: {p["text"]};
}}
QFrame#ideaCard[kind="warn"] QLabel#ideaDate,
QFrame#ideaCard[kind="info"] QLabel#ideaDate,
QFrame#ideaCard[kind="danger"] QLabel#ideaDate {{
    color: {p["muted"]};
}}
QPushButton#roundBtn {{ background: transparent; border: none; }}
"""


STYLE = """
QWidget#shell { background: transparent; font-family: 'Segoe UI'; }
QWidget#panel { background: transparent; border: none; }
QFrame#headerLine { background: #eef2f6; max-height: 1px; border: none; }
QFrame#contentArea {
    background: transparent; border: none; border-radius: 0px;
}
QFrame#navBar {
    background: transparent; border: none;
}
QWidget#navWrap { background: transparent; }
QWidget#navTab { background: transparent; }
QLabel#navBubble, QWidget#navBubble {
    background: transparent; border: none;
}
QFrame#navHomeLine {
    background: #94a3b8; border: none; border-radius: 2px; max-height: 3px;
}
QLabel#navIcon { background: transparent; border-radius: 17px; padding: 5px; min-width: 44px; }
QLabel#navIcon[active="true"] { background: #dbeafe; }
QLabel#navText { font-size: 10px; font-weight: 700; color: #64748b; }
QLabel#navText[active="true"] { color: #2563eb; }
QStackedWidget, QStackedWidget > QWidget { background: transparent; border: none; }
QLabel { color: #1e293b; background: transparent; }
QLabel#welcomeTitle { font-size: 15px; font-weight: 800; color: #0f172a; }
QLabel#pageTitle { font-size: 15px; font-weight: 800; color: #0f172a; }
QLabel#cardName { font-size: 14px; font-weight: 800; color: #0f172a; }
QLabel#stamp { color: #64748b; font-size: 11px; font-weight: 600; }
QLabel#versionLabel { color: #94a3b8; font-size: 10px; font-weight: 600; }
QLabel#section { font-size: 12px; font-weight: 700; color: #64748b; margin-top: 4px; margin-bottom: 2px; }
QLabel#settingTitle { font-size: 12px; font-weight: 700; color: #64748b; margin: 0; padding: 0; }
QLabel#settingHint { color: #94a3b8; font-size: 10px; margin: 0; padding: 0; }
QLabel#plan {
    color: #2563eb; font-size: 9px; font-weight: 700;
    background: #eff6ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 1px 6px;
}
QLabel#planLocal {
    color: #64748b; font-size: 9px; font-weight: 700;
    background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1px 6px;
}
QFrame#iconMark {
    background: #f8fafc; border: none; border-radius: 20px;
}
QPushButton#agentLogoBtn {
    background: transparent; border: none; border-radius: 32px; padding: 0;
}
QPushButton#agentLogoBtn:hover {
    background: #e2e8f0;
}
QLabel#agentLogoName {
    color: #334155; font-size: 10px; font-weight: 700;
}
QLabel#ghCat {
    color: #64748b; font-size: 10px; font-weight: 700;
}
QLabel#ghRank {
    color: #075985; background: #e0f2fe;
    border: 1px solid #bae6fd; border-radius: 10px;
    font-size: 11px; font-weight: 800;
}
QFrame#ghFilterBar {
    background: #e8f2fc; border: none; border-radius: 12px;
}
QFrame#ghTile {
    background: #ffffff; border: 1px solid #dbeafe; border-radius: 12px;
}
QFrame#ghTile:hover {
    background: #eff6ff; border-color: #93c5fd;
}
QLabel#ghTileTitle {
    color: #0f172a; font-size: 12px; font-weight: 800;
}
QLabel#ghTileRepo {
    color: #94a3b8; font-size: 9px; font-weight: 600;
}
QLabel#ghTileBody {
    color: #64748b; font-size: 10px;
}
QLabel#ghCode {
    color: #1e293b; background: #e8f2fc;
    border: 1px solid #dbeafe; border-radius: 8px;
    padding: 8px; font-family: Consolas, 'Courier New', monospace; font-size: 10px;
}
QLabel#ghCatChip {
    color: #075985; background: #e0f2fe;
    border: 1px solid #bae6fd; border-radius: 8px;
    padding: 2px 6px; font-size: 9px; font-weight: 800;
}
QLabel#ghFitChip {
    color: #047857; background: #d1fae5;
    border-radius: 8px; padding: 2px 6px; font-size: 9px; font-weight: 700;
}
QLabel#ghFitChip[kind="partial"] {
    color: #334155; background: #e2e8f0;
}
QLabel#ghFitChip[kind="gap"] {
    color: #64748b; background: transparent; border: 1px solid #e2e8f0;
}
QLabel#ghTileBadge {
    color: #0369a1; font-size: 9px; font-weight: 700;
}
QFrame#cardSkeleton {
    background: #f1f5f9; border: 1px solid #e8ecf1; border-radius: 14px; min-height: 88px;
}
QPushButton#orderBtn {
    background: transparent; color: #64748b; border: none;
    border-radius: 6px; padding: 0; font-size: 11px; font-weight: 700; min-height: 0;
}
QLabel#meterName { font-size: 11px; font-weight: 600; color: #64748b; }
QLabel#meterValue { font-size: 11px; font-weight: 700; color: #16a34a; }
QLabel#meterMeta { color: #94a3b8; font-size: 10px; }
QLabel#leftPct { color: #16a34a; font-size: 13px; font-weight: 800; }
QLabel#usageOrderHint { color: #94a3b8; font-size: 10px; font-weight: 600; padding: 0 2px 4px 2px; }
QLabel#usageSummary { color: #64748b; font-size: 11px; font-weight: 600; padding: 2px 2px 6px 2px; }
QLabel#error { color: #dc2626; font-size: 11px; }
QLabel#ideaTitle { font-size: 13px; font-weight: 800; color: #0f172a; }
QLabel#ideaBody { color: #64748b; font-size: 11px; line-height: 1.3; }
QLabel#ideaFix { color: #16a34a; font-size: 11px; }
QLabel#ideaDate { color: #94a3b8; font-size: 10px; }
QLabel#statN { font-size: 18px; font-weight: 800; color: #0f172a; }
QLabel#statL { font-size: 10px; font-weight: 600; color: #64748b; }
QFrame#logoBadge {
    background: transparent; border: none;
}
QLabel#ideaSource { color: #334155; font-size: 11px; font-weight: 700; }
QFrame#statBox { border: 1px solid #e8ecf1; border-radius: 12px; min-height: 76px; }
QFrame#settingRow { border: 1px solid #e8ecf1; border-radius: 12px; min-height: 56px; }
QFrame#card, QFrame#ideaCard { border: 1px solid #e8ecf1; border-radius: 14px; }
QFrame#ideaCard[kind="warn"] { border-color: #fde68a; background: #fffef5; }
QFrame#ideaCard[kind="info"] { border-color: #bfdbfe; background: #f8fbff; }
QFrame#ideaCard[kind="danger"] { border-color: #fecaca; background: #fffafa; }
QFrame#segment { border: none; border-radius: 10px; }
QPushButton#segBtn {
    background: transparent; border: none; border-radius: 8px;
    font-size: 11px; font-weight: 700; min-height: 32px; padding: 4px 10px;
}
QPushButton#lookBtn {
    background: #ffffff; color: #334155;
    border: 1px solid #cbd5e1; border-radius: 10px;
    font-size: 11px; font-weight: 700; min-height: 32px; padding: 4px 12px;
}
QWidget#navTab { background: transparent; }
QLabel#navIcon { background: transparent; border-radius: 17px; padding: 5px; min-width: 44px; }
QLabel#navIcon[active="true"] { background: #dbeafe; }
QLabel#navText { font-size: 10px; font-weight: 700; color: #64748b; }
QLabel#navText[active="true"] { color: #2563eb; }
QComboBox { border-radius: 10px; font-size: 12px; min-height: 34px; padding: 6px 10px; }
QComboBox#langCombo { padding-left: 8px; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox::down-arrow { image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid #64748b; margin-right: 8px; }
QScrollArea#list { background: transparent; border: none; }
QScrollArea#list QScrollBar:vertical { width: 0px; background: transparent; }
QScrollArea#list QScrollBar:horizontal { height: 0px; background: transparent; }
QScrollArea#list QWidget#listInner { background: transparent; }
QCheckBox#switch::indicator {
    width: 46px; height: 26px; border-radius: 13px; background: #cbd5e1;
}
QCheckBox#switch::indicator:checked { background: #2563eb; }
"""


def make_icon() -> QIcon:
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        icon.addPixmap(_logo_pix(size))
    return icon


class FaviconWorker(QThread):
    done = Signal(str, object)

    def __init__(self, name: str, domain: str, parent=None):
        super().__init__(parent)
        self.name, self.domain = name, domain

    def run(self) -> None:
        return


class CoachWorker(QThread):
    finished_ok = Signal(object)
    failed = Signal(str)

    def __init__(self, allow_chat: bool = False, parent=None):
        super().__init__(parent)
        self._allow_chat = allow_chat

    def run(self) -> None:
        try:
            self.finished_ok.emit(build_report(allow_chat=self._allow_chat))
        except Exception:
            self.failed.emit("error.generic")


class FetchWorker(QThread):
    finished_ok = Signal(object)
    failed = Signal(str)

    def __init__(self, allow_quota: bool = False, parent=None):
        super().__init__(parent)
        self._allow_quota = allow_quota

    def run(self) -> None:
        try:
            self.finished_ok.emit(fetch_snapshot(allow_quota=self._allow_quota))
        except Exception:
            self.failed.emit("error.generic")


class GhFetchWorker(QThread):
    finished_ok = Signal(object)
    failed = Signal(str)

    def __init__(self, *, force: bool = False, parent=None):
        super().__init__(parent)
        self._force = force

    def run(self) -> None:
        try:
            if self.isInterruptionRequested():
                return
            self.finished_ok.emit(fetch_top_projects(force=self._force))
        except Exception:
            self.failed.emit("error.generic")


class GhLocalizeWorker(QThread):
    """GitHub açıklamalarını arka planda UI diline çevir."""

    finished_ok = Signal(str, object)  # lang, {repo: text}

    def __init__(self, pairs: list[tuple[str, str]], lang: str, parent=None):
        super().__init__(parent)
        self._pairs = pairs
        self._lang = lang

    def run(self) -> None:
        try:
            out: dict[str, str] = {}
            for repo, text in self._pairs:
                if self.isInterruptionRequested():
                    return
                out[repo] = localize_blurb(text, self._lang) if text else ""
            self.finished_ok.emit(self._lang, out)
        except Exception:
            self.finished_ok.emit(self._lang, {})


_BAR_H = 12


def _provider_lowest(provider: ProviderUsage) -> float | None:
    vals = [m.remaining_percent for m in provider.meters if m.remaining_percent is not None]
    return min(vals) if vals else None


def _tone_for(remaining: float | None, warn: float, crit: float) -> str:
    if remaining is None:
        return ""
    if remaining < crit:
        return "crit"
    if remaining < warn:
        return "warn"
    return ""


def _bar_fill_color(theme: str, remaining: float, warn: float = 40, crit: float = 15) -> QColor:
    pal = THEME_PALETTE.get(theme, THEME_PALETTE["frost"])
    tone = _tone_for(remaining, warn, crit)
    if tone == "crit":
        return QColor(pal["bar_crit"])
    if tone == "warn":
        return QColor(pal["bar_warn"])
    return QColor(pal["bar_ok"])


class _ClickFrame(QFrame):
    """Tıklanabilir kutu — QPushButton child layout’u ezmez."""

    clicked = Signal()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class Bar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0.0
        self.setFixedHeight(_BAR_H)

    def set_remaining(self, remaining: float | None) -> None:
        self._value = 0.0 if remaining is None else max(0.0, min(100.0, remaining))
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        track_col = QColor("#eef2f6")
        theme = "frost"
        win = self.window()
        if isinstance(win, UsageOverlay):
            theme = win._theme
            pal = THEME_PALETTE.get(theme, THEME_PALETTE["frost"])
            track_col = QColor(pal["line"])
        track = QPainterPath()
        track.addRoundedRect(QRectF(0, 0, self.width(), self.height()), self.height() / 2, self.height() / 2)
        painter.fillPath(track, track_col)
        width = max(4.0, self.width() * self._value / 100.0)
        warn, crit = 40.0, 15.0
        if isinstance(win, UsageOverlay):
            warn, crit = float(win._warn_pct), float(win._crit_pct)
        color = _bar_fill_color(theme, self._value, warn, crit)
        fill = QPainterPath()
        fill.addRoundedRect(QRectF(0, 0, width, self.height()), self.height() / 2, self.height() / 2)
        painter.fillPath(fill, color)


class _CardInteractFilter(QObject):
    def __init__(self, overlay: "UsageOverlay", name: str):
        super().__init__(overlay)
        self._overlay = overlay
        self._name = name
        self._press: QPoint | None = None
        self._dragging = False

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        et = event.type()
        if et == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton:
                gp = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
                self._overlay._provider_context_menu(self._name, gp)
                return True
            if event.button() == Qt.LeftButton:
                self._press = event.position().toPoint() if hasattr(event, "position") else event.pos()
                self._dragging = False
            return False
        if et == QEvent.MouseMove and self._press is not None and event.buttons() & Qt.LeftButton:
            pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
            gp = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
            if not self._dragging and (pos - self._press).manhattanLength() >= 10:
                self._dragging = True
                self._overlay._start_card_drag(self._name, obj, self._press)
            if self._dragging:
                self._overlay._move_card_drag(gp)
            return False
        if et == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            dragged = self._dragging
            self._press = None
            self._dragging = False
            gp = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
            if dragged:
                self._overlay._end_card_drag()
                self._overlay._drop_provider_at(self._name, gp)
                return True
            pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
            child = obj.childAt(pos)
            while child is not None and child is not obj:
                if isinstance(child, QPushButton):
                    return False
                child = child.parentWidget()
            self._overlay._open_usage_detail(self._name, from_page="usage")
            return False
        return False


class MeterRow(QWidget):
    def __init__(self, parent=None, compact: bool = False, hide_value: bool = False):
        super().__init__(parent)
        self._compact = compact
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(4 if compact else 3)
        top = QHBoxLayout()
        self.name, self.value = QLabel(), QLabel()
        self.name.setObjectName("meterName")
        self.value.setObjectName("meterValue")
        self.value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.value.setVisible(not hide_value)
        top.addWidget(self.name)
        top.addWidget(self.value, 1)
        layout.addLayout(top)
        self.bar = Bar()
        layout.addWidget(self.bar)
        self.meta = QLabel()
        self.meta.setObjectName("meterMeta")
        if not compact:
            layout.addWidget(self.meta)

    def set_meter(
        self,
        meter: Meter,
        translate,
        left_fmt: str,
        detail: str = "",
        *,
        pct_fmt=None,
    ) -> None:
        self.name.setText(translate(meter.label))
        if meter.remaining_percent is not None:
            if callable(pct_fmt):
                self.value.setText(pct_fmt(meter.remaining_percent))
            else:
                self.value.setText(left_fmt.format(n=meter.remaining_percent))
        else:
            self.value.setText(translate(meter.remaining_text) or "—")
        self.bar.set_remaining(meter.remaining_percent)
        bits = [translate(bit) for bit in (meter.reset_text, meter.detail) if bit]
        if detail:
            bits.insert(0, detail)
        self.meta.setText(" · ".join(bits))
        self.meta.setVisible(bool(bits) and not self._compact)



class NavPill(QFrame):
    """Yuvarlak pill bar — üstte floating bubble için boşluk bırakır."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navBar")
        self.setFixedHeight(60)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        theme = "frost"
        win = self.window()
        if isinstance(win, UsageOverlay):
            theme = win._theme
        pal = THEME_PALETTE.get(theme, THEME_PALETTE["frost"])
        fill, border = QColor(pal["card"]), QColor(pal["card_border"])
        rect = QRectF(1, 12, self.width() - 2, self.height() - 16)
        path = QPainterPath()
        path.addRoundedRect(rect, rect.height() / 2, rect.height() / 2)
        p.setPen(QPen(border, 1))
        p.setBrush(fill)
        p.drawPath(path)


class NavBubble(QWidget):
    """Sadece paint — stylesheet/layout yok (takılma/flicker önler)."""

    def __init__(self, owner: "NavTab"):
        super().__init__(owner)
        self._owner = owner
        self.setObjectName("navBubble")
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(False)

    def paintEvent(self, event) -> None:  # noqa: N802
        o = self._owner
        lift = o._lift
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        top = o._IDLE_TOP * (1.0 - lift)
        cx = self.width() * 0.5
        cy = top + _NAV_BUBBLE * 0.5
        rad = _NAV_BUBBLE * 0.5
        if lift > 0.01:
            accent = o._accent()
            p.setPen(Qt.NoPen)
            glow = QColor(accent.red(), accent.green(), accent.blue(), int(85 * lift))
            p.setBrush(glow)
            p.drawEllipse(QPointF(cx, cy + 2.0), rad + 3.0, rad + 3.0)
            fill = QColor(accent.red(), accent.green(), accent.blue(), int(255 * lift))
            p.setBrush(fill)
            p.drawEllipse(QPointF(cx, cy), rad - 0.5, rad - 0.5)
        pix = o._pix
        if not pix.isNull():
            p.drawPixmap(int(cx - pix.width() / 2), int(cy - pix.height() / 2), pix)


class NavTab(QWidget):
    """Floating-circle sekme — ortadaki pill nav stili."""

    _IDLE_TOP = 12
    _ANIM_MS = 240

    def __init__(self, overlay: "UsageOverlay", kind: str, page: str, parent=None):
        super().__init__(parent)
        self._overlay = overlay
        self.setObjectName("navTab")
        self.setAccessibleName(page + "Btn")
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self._kind, self._page = kind, page
        self.setMinimumHeight(48)
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)
        self.bubble = NavBubble(self)
        self._lay.addWidget(self.bubble)
        self.text = QLabel()
        self.text.setObjectName("navText")
        self.text.hide()
        self._active = None
        self._hover = False
        self._lift = 0.0
        self._pix = QPixmap()
        self._icon_key: tuple | None = None
        self._anim = QPropertyAnimation(self, b"lift", self)
        self._anim.setDuration(self._ANIM_MS)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._sync_icon()

    def set_text(self, label: str) -> None:
        self.text.setText(label)
        self.setToolTip(label)
        self.setAccessibleName(label)

    def _accent(self) -> QColor:
        return self._overlay.theme_accent() if hasattr(self._overlay, "theme_accent") else QColor("#0369a1")

    def _get_lift(self) -> float:
        return self._lift

    def _set_lift(self, value: float) -> None:
        v = max(0.0, min(1.0, float(value)))
        if abs(v - self._lift) < 0.0005:
            return
        self._lift = v
        self._sync_icon()
        self.bubble.update()

    lift = Property(float, _get_lift, _set_lift)

    def set_active(self, on: bool, *, force: bool = False) -> None:
        if not force and self._active is on:
            return
        self._active = on
        target = 1.0 if on else 0.0
        self._anim.stop()
        if force or abs(self._lift - target) < 0.001:
            # lift aynı kalsa bile ikon boyansın (ilk pasif sekmeler boş kalıyordu)
            self._lift = target
            self._sync_icon()
            self.bubble.update()
            return
        self._anim.setStartValue(self._lift)
        self._anim.setEndValue(target)
        self._anim.start()

    def _sync_icon(self) -> None:
        # İkon rengi lift’e bağlı: daire kaybolmadan muted’a düşmesin (yanıp sönme)
        if self._lift >= 0.18:
            color = QColor("#ffffff")
        elif self._hover:
            color = self._accent()
        else:
            color = self._overlay.theme_muted() if hasattr(self._overlay, "theme_muted") else QColor("#486581")
        key = (self._kind, color.name(), "nav")
        if key == self._icon_key and not self._pix.isNull():
            return
        self._icon_key = key
        pix = _NAV_ICON_CACHE.get(key)
        if pix is None:
            size = _NAV_AGENTS_GLYPH_PX if self._kind == "agents" else _NAV_GLYPH_PX
            pix = _glyph(self._kind, color, size)
            _NAV_ICON_CACHE[key] = pix
        self._pix = pix

    def enterEvent(self, event) -> None:  # noqa: N802
        self._hover = True
        self._icon_key = None
        self._sync_icon()
        self.bubble.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        self._hover = False
        self._icon_key = None
        self._sync_icon()
        self.bubble.update()
        super().leaveEvent(event)

    def click(self) -> None:
        self._overlay.goto(self._page)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._overlay.goto(self._page)
        super().mousePressEvent(event)


class StatBox(QFrame):
    def __init__(self, glyph: str, parent=None):
        super().__init__(parent)
        self._glyph = glyph
        self.setObjectName("statBox")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(4)
        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setPixmap(_glyph(glyph, QColor("#64748b"), _STAT_GLYPH_PX))
        self.num = QLabel("—")
        self.num.setObjectName("statN")
        self.num.setAlignment(Qt.AlignCenter)
        self.lbl = QLabel()
        self.lbl.setObjectName("statL")
        self.lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.icon)
        lay.addWidget(self.num)
        lay.addWidget(self.lbl)

    def set_glyph_color(self, color: QColor) -> None:
        self.icon.setPixmap(_glyph(self._glyph, color, _STAT_GLYPH_PX))

    def set_values(self, num: str, label: str) -> None:
        self.num.setText(num)
        self.lbl.setText(label)


class UsageOverlay(QWidget):
    def __init__(
        self,
        auto_fetch: bool = True,
        for_test: bool = False,
        *,
        license_path: Path | str | None = None,
        license_prompt: Callable[[str], bool] | None = None,
    ):
        super().__init__()
        self.setObjectName("shell")
        self.setWindowIcon(make_icon())
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self.setMinimumSize(360, 520)
        self._drag = None
        self._pinned = True
        self._worker = None
        self._fav_workers: list[FaviconWorker] = []
        self._favicon_pending: set[str] = set()
        self._mask_timer = QTimer(self)
        self._mask_timer.setSingleShot(True)
        self._mask_timer.timeout.connect(self._sync_mask)
        self._auto_fetch = auto_fetch
        self._for_test = for_test
        self._license_path = resolve_license_path(license_path)
        self._license_prompt = license_prompt
        self._license_granted = False
        self._settings = QSettings(SETTINGS_ORG, "ui")
        if for_test:
            self._lang, self._theme, self._interval = "tr", "night", 60
            self._quota_access = False
            self._chat_analysis = False
            self._consent_seen = True
            self._warn_pct, self._crit_pct = 40, 15
            self._pct_decimals = 4
            import auto_translate as _at

            _at.FORCE_OFFLINE = True
        else:
            self._lang = str(self._settings.value("lang", "en"))
            if self._lang not in LANG_CODES:
                self._lang = "en"
            self._theme = str(self._settings.value("theme", "frost"))
            if self._theme not in THEMES:
                self._theme = "frost"
            try:
                self._interval = int(self._settings.value("interval", 60))
            except (TypeError, ValueError):
                self._interval = 60
            if self._interval not in INTERVALS:
                self._interval = 60
            self._quota_access = self._settings.value("quota_access", False, type=bool)
            self._chat_analysis = self._settings.value("chat_analysis", False, type=bool)
            self._consent_seen = self._settings.value("consent_seen", False, type=bool)
            try:
                self._warn_pct = int(self._settings.value("warn_pct", 40))
            except (TypeError, ValueError):
                self._warn_pct = 40
            try:
                self._crit_pct = int(self._settings.value("crit_pct", 15))
            except (TypeError, ValueError):
                self._crit_pct = 15
            if self._warn_pct not in (30, 40, 50):
                self._warn_pct = 40
            if self._crit_pct not in (10, 15, 20):
                self._crit_pct = 15
            try:
                self._pct_decimals = int(self._settings.value("pct_decimals", 4))
            except (TypeError, ValueError):
                self._pct_decimals = 4
            if self._pct_decimals not in PCT_DECIMALS:
                self._pct_decimals = 4
        self._snap: UsageSnapshot | None = None
        self._last_pcts: dict[str, float] = {}
        self._recent_drops: dict[str, float] = {}
        self._live_state = "idle"  # idle | live | busy | err
        self._live_blink_on = True
        self._drag_ghost: QLabel | None = None
        self._drag_source: QWidget | None = None
        self._drag_hotspot = QPoint()
        self._drag_name = ""
        self._drag_slot = -1
        self._drag_hidden_children: list[QWidget] = []
        self._coach: CoachReport | None = None
        self._coach_worker = None
        self._page = "usage"
        self._detail_provider: str | None = None
        self._detail_from = "usage"
        self._idea_filter = "all"
        self._idea_source_filter = "all"
        self._github_cat = "all"
        self._gh_filter_btns: list[tuple[str, QPushButton]] = []
        self._gh_projects: list[LiveProject] = []
        self._gh_detail_repo: str | None = None
        self._gh_worker: GhFetchWorker | None = None
        self._gh_loc_worker: GhLocalizeWorker | None = None
        self._gh_i18n: dict[tuple[str, str], str] = {}
        self._src_filter_btns: list[tuple[str, QPushButton]] = []
        self._quitting = False
        self._restore_pin_after_show = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.panel = QFrame()
        self.panel.setObjectName("panel")
        self.panel.setProperty("theme", self._theme)
        self.panel.setAutoFillBackground(False)
        outer.addWidget(self.panel)
        root = QVBoxLayout(self.panel)
        root.setContentsMargins(14, 12, 14, 10)
        root.setSpacing(8)

        cap = QHBoxLayout()
        logo = QFrame()
        logo.setObjectName("logoBadge")
        logo.setFixedSize(_LOGO_HEADER_PX, _LOGO_HEADER_PX)
        self.logo_badge = logo
        logo_l = QVBoxLayout(logo)
        logo_l.setContentsMargins(0, 0, 0, 0)
        self.grip = QLabel()
        self.grip.setPixmap(_logo_pix(_LOGO_HEADER_PX))
        self.grip.setAlignment(Qt.AlignCenter)
        logo_l.addWidget(self.grip)
        cap.addWidget(logo)
        titles = QVBoxLayout()
        titles.setSpacing(0)
        self.title = QLabel()
        self.title.setObjectName("welcomeTitle")
        ver_row = QHBoxLayout()
        ver_row.setContentsMargins(0, 0, 0, 0)
        ver_row.setSpacing(6)
        self.live_icon = QLabel()
        self.live_icon.setObjectName("liveIcon")
        self.live_icon.setFixedSize(_LIVE_GLYPH_PX + 2, _LIVE_GLYPH_PX + 2)
        self.live_icon.setAlignment(Qt.AlignCenter)
        self._live_opacity = QGraphicsOpacityEffect(self.live_icon)
        self._live_opacity.setOpacity(1.0)
        self.live_icon.setGraphicsEffect(self._live_opacity)
        self.subtitle = QLabel()
        self.subtitle.setObjectName("versionLabel")
        ver_row.addWidget(self.live_icon, 0, Qt.AlignVCenter)
        ver_row.addWidget(self.subtitle, 0, Qt.AlignVCenter)
        ver_row.addStretch(1)
        titles.addWidget(self.title)
        titles.addLayout(ver_row)
        cap.addLayout(titles, 1)
        self.stamp = QLabel()
        self.stamp.setObjectName("stamp")
        cap.addWidget(self.stamp, 0, Qt.AlignVCenter)
        self.tray_btn = HeaderIconBtn("tray_token", QColor("#334155"))
        self.tray_btn.setAccessibleName("trayBtn")
        self.tray_btn.clicked.connect(self.hide_to_tray)
        self.close_btn = HeaderIconBtn("close", QColor("#334155"))
        self.close_btn.setAccessibleName("closeBtn")
        self.close_btn.clicked.connect(self.hide_to_tray)
        cap.addWidget(self.tray_btn)
        cap.addWidget(self.close_btn)
        root.addLayout(cap)
        header_line = QFrame()
        header_line.setObjectName("headerLine")
        header_line.setFixedHeight(1)
        root.addWidget(header_line)

        self.global_error = QLabel()
        self.global_error.setObjectName("error")
        self.global_error.setWordWrap(True)
        self.global_error.hide()
        root.addWidget(self.global_error)

        self.content = QFrame()
        self.content.setObjectName("contentArea")
        content_l = QVBoxLayout(self.content)
        content_l.setContentsMargins(4, 4, 4, 4)
        content_l.setSpacing(0)
        self.pages = QStackedWidget()
        usage_page = QWidget()
        usage_l = QVBoxLayout(usage_page)
        usage_l.setContentsMargins(0, 0, 0, 0)
        usage_l.setSpacing(4)
        self.usage_summary = QLabel()
        self.usage_summary.setObjectName("usageSummary")
        self.usage_summary.hide()
        usage_l.addWidget(self.usage_summary)
        self.usage_order_hint = QLabel()
        self.usage_order_hint.setObjectName("usageOrderHint")
        usage_l.addWidget(self.usage_order_hint)
        self.usage_hidden_row = QLabel()
        self.usage_hidden_row.setObjectName("usageOrderHint")
        self.usage_hidden_row.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.usage_hidden_row.linkActivated.connect(self._unhide_provider)
        self.usage_hidden_row.hide()
        usage_l.addWidget(self.usage_hidden_row)
        self.scroll = QScrollArea()
        self.scroll.setObjectName("list")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_inner = QWidget()
        self.list_inner.setObjectName("listInner")
        self.cards_layout = QVBoxLayout(self.list_inner)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(8)
        self.scroll.setWidget(self.list_inner)
        usage_l.addWidget(self.scroll)
        self.pages.addWidget(usage_page)

        ideas_page = QWidget()
        ideas_l = QVBoxLayout(ideas_page)
        ideas_l.setContentsMargins(0, 0, 0, 0)
        ideas_l.setSpacing(8)
        self.stat_chats = StatBox("stat_chat")
        self.stat_tok = StatBox("stat_tok")
        self.stat_tools = StatBox("stat_tools")
        stats = QHBoxLayout()
        for box in (self.stat_chats, self.stat_tok, self.stat_tools):
            stats.addWidget(box, 1)
        ideas_l.addLayout(stats)
        filt_seg = QFrame()
        filt_seg.setObjectName("segment")
        self._filt_seg = filt_seg
        filt = QHBoxLayout(filt_seg)
        filt.setContentsMargins(3, 3, 3, 3)
        filt.setSpacing(2)
        self.filter_all = self._chip("", "filterAll")
        self.filter_warn = self._chip("", "filterWarn")
        self.filter_danger = self._chip("", "filterDanger")
        self.filter_info = self._chip("", "filterInfo")
        self.filter_all.clicked.connect(lambda: self._set_filter("all"))
        self.filter_warn.clicked.connect(lambda: self._set_filter("warn"))
        self.filter_danger.clicked.connect(lambda: self._set_filter("danger"))
        self.filter_info.clicked.connect(lambda: self._set_filter("info"))
        for b in (self.filter_all, self.filter_warn, self.filter_danger, self.filter_info):
            b.setObjectName("segBtn")
            filt.addWidget(b, 1)
        ideas_l.addWidget(filt_seg)
        src_seg = QFrame()
        src_seg.setObjectName("segment")
        self._src_filt_seg = src_seg
        self._src_filt_layout = QHBoxLayout(src_seg)
        self._src_filt_layout.setContentsMargins(3, 3, 3, 3)
        self._src_filt_layout.setSpacing(2)
        ideas_l.addWidget(src_seg)
        ideas_scroll = QScrollArea()
        ideas_scroll.setObjectName("list")
        self._ideas_scroll = ideas_scroll
        ideas_scroll.setWidgetResizable(True)
        ideas_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ideas_inner = QWidget()
        self.ideas_inner.setObjectName("listInner")
        self.ideas_layout = QVBoxLayout(self.ideas_inner)
        self.ideas_layout.setContentsMargins(0, 0, 0, 0)
        self.ideas_layout.setSpacing(8)
        ideas_scroll.setWidget(self.ideas_inner)
        ideas_l.addWidget(ideas_scroll, 1)
        self.pages.addWidget(ideas_page)

        agents_page = QWidget()
        agents_l = QVBoxLayout(agents_page)
        agents_l.setContentsMargins(0, 0, 0, 0)
        agents_l.setSpacing(8)
        agents_scroll = QScrollArea()
        agents_scroll.setObjectName("list")
        self._agents_scroll = agents_scroll
        agents_scroll.setWidgetResizable(True)
        agents_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.agents_inner = QWidget()
        self.agents_inner.setObjectName("listInner")
        self.agents_layout = QVBoxLayout(self.agents_inner)
        self.agents_layout.setContentsMargins(0, 0, 0, 0)
        self.agents_layout.setSpacing(8)
        agents_scroll.setWidget(self.agents_inner)
        agents_l.addWidget(agents_scroll, 1)
        self.pages.addWidget(agents_page)

        github_page = QWidget()
        github_l = QVBoxLayout(github_page)
        github_l.setContentsMargins(0, 0, 0, 0)
        github_l.setSpacing(8)
        github_scroll = QScrollArea()
        github_scroll.setObjectName("list")
        self._github_scroll = github_scroll
        github_scroll.setWidgetResizable(True)
        github_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.github_inner = QWidget()
        self.github_inner.setObjectName("listInner")
        self.github_layout = QVBoxLayout(self.github_inner)
        self.github_layout.setContentsMargins(0, 0, 0, 0)
        self.github_layout.setSpacing(8)
        github_scroll.setWidget(self.github_inner)
        github_l.addWidget(github_scroll, 1)
        self.pages.addWidget(github_page)

        gh_detail_page = QWidget()
        gd_l = QVBoxLayout(gh_detail_page)
        gd_l.setContentsMargins(0, 0, 0, 0)
        gd_l.setSpacing(8)
        gd_head = QHBoxLayout()
        self.gd_back = QPushButton(self.t("ideas_detail_back"))
        self.gd_back.setObjectName("lookBtn")
        self.gd_back.setCursor(Qt.PointingHandCursor)
        self.gd_back.clicked.connect(lambda: self.goto("github"))
        gd_head.addWidget(self.gd_back)
        gd_head.addStretch(1)
        self.gd_open = QPushButton(self.t("gh_open_web"))
        self.gd_open.setObjectName("lookBtn")
        self.gd_open.setCursor(Qt.PointingHandCursor)
        self.gd_open.clicked.connect(self._open_github_web)
        gd_head.addWidget(self.gd_open)
        gd_l.addLayout(gd_head)
        self.gd_title = QLabel("")
        self.gd_title.setObjectName("pageTitle")
        self.gd_title.setWordWrap(True)
        gd_l.addWidget(self.gd_title)
        self.gd_meta = QLabel("")
        self.gd_meta.setObjectName("ideaSource")
        self.gd_meta.setWordWrap(True)
        gd_l.addWidget(self.gd_meta)
        gd_scroll = QScrollArea()
        gd_scroll.setObjectName("list")
        gd_scroll.setWidgetResizable(True)
        gd_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.gd_inner = QWidget()
        self.gd_inner.setObjectName("listInner")
        self.gd_body = QVBoxLayout(self.gd_inner)
        self.gd_body.setContentsMargins(0, 0, 0, 0)
        self.gd_body.setSpacing(8)
        gd_scroll.setWidget(self.gd_inner)
        gd_l.addWidget(gd_scroll, 1)
        self.pages.addWidget(gh_detail_page)

        detail_page = QWidget()
        detail_l = QVBoxLayout(detail_page)
        detail_l.setContentsMargins(0, 0, 0, 0)
        detail_l.setSpacing(8)
        detail_head = QHBoxLayout()
        self.detail_back = QPushButton(self.t("ideas_detail_back"))
        self.detail_back.setObjectName("lookBtn")
        self.detail_back.setCursor(Qt.PointingHandCursor)
        self.detail_back.clicked.connect(self._idea_detail_back)
        detail_head.addWidget(self.detail_back)
        detail_head.addStretch(1)
        detail_l.addLayout(detail_head)
        self.detail_title = QLabel(self.t("ideas_detail_title"))
        self.detail_title.setObjectName("ideaTitle")
        detail_l.addWidget(self.detail_title)
        self._detail_meta = QLabel("")
        self._detail_meta.setObjectName("ideaSource")
        detail_l.addWidget(self._detail_meta)
        detail_scroll = QScrollArea()
        detail_scroll.setObjectName("list")
        self._detail_scroll = detail_scroll
        detail_scroll.setWidgetResizable(True)
        detail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._detail_inner = QWidget()
        self._detail_inner.setObjectName("listInner")
        detail_inner_l = QVBoxLayout(self._detail_inner)
        detail_inner_l.setContentsMargins(0, 0, 0, 0)
        detail_inner_l.setSpacing(10)
        self._detail_lbl_problem = QLabel(self.t("ideas_detail_problem"))
        self._detail_lbl_problem.setObjectName("settingTitle")
        self._detail_problem = QLabel("")
        self._detail_problem.setObjectName("ideaBody")
        self._detail_problem.setWordWrap(True)
        self._detail_lbl_cause = QLabel(self.t("ideas_detail_cause"))
        self._detail_lbl_cause.setObjectName("settingTitle")
        self._detail_cause = QLabel("")
        self._detail_cause.setObjectName("ideaBody")
        self._detail_cause.setWordWrap(True)
        self._detail_lbl_solution = QLabel(self.t("ideas_detail_solution"))
        self._detail_lbl_solution.setObjectName("settingTitle")
        self._detail_solution = QLabel("")
        self._detail_solution.setObjectName("ideaFix")
        self._detail_solution.setWordWrap(True)
        self._detail_lbl_example = QLabel(self.t("ideas_detail_example"))
        self._detail_lbl_example.setObjectName("settingTitle")
        self._detail_example = QLabel("")
        self._detail_example.setObjectName("ideaBody")
        self._detail_example.setWordWrap(True)
        self._detail_lbl_suggest = QLabel(self.t("ideas_detail_suggest"))
        self._detail_lbl_suggest.setObjectName("settingTitle")
        self._detail_suggest = QLabel("")
        self._detail_suggest.setObjectName("ideaFix")
        self._detail_suggest.setWordWrap(True)
        detail_copy_row = QHBoxLayout()
        detail_copy_row.addStretch(1)
        self.detail_copy = QPushButton(self.t("ideas_detail_copy"))
        self.detail_copy.setObjectName("lookBtn")
        self.detail_copy.setCursor(Qt.PointingHandCursor)
        self.detail_copy.clicked.connect(self._copy_detail_suggest)
        detail_copy_row.addWidget(self.detail_copy)
        for w in (
            self._detail_lbl_problem, self._detail_problem,
            self._detail_lbl_cause, self._detail_cause,
            self._detail_lbl_solution, self._detail_solution,
            self._detail_lbl_example, self._detail_example,
            self._detail_lbl_suggest, self._detail_suggest,
        ):
            detail_inner_l.addWidget(w)
        detail_inner_l.addLayout(detail_copy_row)
        detail_inner_l.addStretch(1)
        detail_scroll.setWidget(self._detail_inner)
        detail_l.addWidget(detail_scroll, 1)
        self.pages.addWidget(detail_page)
        self._detail_code = ""
        self._detail_snippet = ""
        self._detail_helpers: list[str] = []
        self._detail_source = ""
        self._detail_when = ""
        self._detail_count = 1
        self._detail_suggest_text = ""

        ud_page = QWidget()
        ud_l = QVBoxLayout(ud_page)
        ud_l.setContentsMargins(0, 0, 0, 0)
        ud_l.setSpacing(8)
        ud_head = QHBoxLayout()
        self.ud_back = QPushButton()
        self.ud_back.setObjectName("lookBtn")
        self.ud_back.setCursor(Qt.PointingHandCursor)
        self.ud_back.clicked.connect(self._usage_detail_back)
        ud_head.addWidget(self.ud_back)
        ud_head.addStretch(1)
        self.ud_hide = QPushButton()
        self.ud_hide.setObjectName("lookBtn")
        self.ud_hide.setCursor(Qt.PointingHandCursor)
        self.ud_hide.clicked.connect(self._hide_detail_provider)
        ud_head.addWidget(self.ud_hide)
        ud_l.addLayout(ud_head)
        self.ud_title = QLabel()
        self.ud_title.setObjectName("pageTitle")
        ud_l.addWidget(self.ud_title)
        self.ud_plan = QLabel()
        self.ud_plan.setObjectName("plan")
        self.ud_plan.hide()
        ud_l.addWidget(self.ud_plan)
        self.ud_reset = QLabel()
        self.ud_reset.setObjectName("meterMeta")
        ud_l.addWidget(self.ud_reset)
        self.ud_model = QLabel()
        self.ud_model.setObjectName("meterMeta")
        self.ud_model.hide()
        ud_l.addWidget(self.ud_model)
        self.ud_usage = QLabel()
        self.ud_usage.setObjectName("meterMeta")
        self.ud_usage.hide()
        ud_l.addWidget(self.ud_usage)
        self.ud_error = QLabel()
        self.ud_error.setObjectName("error")
        self.ud_error.setWordWrap(True)
        self.ud_error.hide()
        ud_l.addWidget(self.ud_error)
        ud_scroll = QScrollArea()
        ud_scroll.setObjectName("list")
        self._ud_scroll = ud_scroll
        ud_scroll.setWidgetResizable(True)
        ud_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._ud_inner = QWidget()
        self._ud_inner.setObjectName("listInner")
        self.ud_body = QVBoxLayout(self._ud_inner)
        self.ud_body.setContentsMargins(0, 0, 0, 0)
        self.ud_body.setSpacing(8)
        ud_scroll.setWidget(self._ud_inner)
        ud_l.addWidget(ud_scroll, 1)
        self.pages.addWidget(ud_page)

        settings_page = QWidget()
        settings_outer = QVBoxLayout(settings_page)
        settings_outer.setContentsMargins(0, 0, 0, 0)
        settings_outer.setSpacing(4)
        settings_scroll = QScrollArea()
        settings_scroll.setObjectName("list")
        self._settings_scroll = settings_scroll
        settings_scroll.setWidgetResizable(True)
        settings_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        settings_scroll.setFrameShape(QFrame.NoFrame)
        settings_inner = QWidget()
        settings_inner.setObjectName("listInner")
        self._settings_inner = settings_inner
        set_l = QVBoxLayout(settings_inner)
        set_l.setContentsMargins(0, 0, 0, 8)
        set_l.setSpacing(10)
        self.settings_title = QLabel()
        self.settings_title.setObjectName("pageTitle")
        self.lang_label = QLabel()
        self.lang_label.setObjectName("section")
        self.lang_combo = QComboBox()
        self.lang_combo.setObjectName("langCombo")
        self.lang_combo.setCursor(Qt.PointingHandCursor)
        self.lang_combo.setMinimumHeight(38)
        self.lang_combo.setIconSize(QSize(_FLAG_ICON_PX, _FLAG_ICON_PX))
        for code, name in LANGS:
            self.lang_combo.addItem(_flag_icon(code), name, code)
        self.lang_combo.currentIndexChanged.connect(self._lang_picked)
        self.theme_label = QLabel()
        self.theme_label.setObjectName("section")
        theme_seg = QFrame()
        theme_seg.setObjectName("segment")
        self._theme_seg = theme_seg
        theme_row = QHBoxLayout(theme_seg)
        theme_row.setContentsMargins(3, 3, 3, 3)
        theme_row.setSpacing(2)
        self.theme_btns: list[tuple[str, QPushButton]] = []
        for name in THEMES:
            btn = QPushButton()
            btn.setObjectName("segBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, n=name: self.set_theme(n))
            self.theme_btns.append((name, btn))
            theme_row.addWidget(btn, 1)
        self.interval_label = QLabel()
        self.interval_label.setObjectName("section")
        int_seg = QFrame()
        int_seg.setObjectName("segment")
        self._int_seg = int_seg
        int_row = QHBoxLayout(int_seg)
        int_row.setContentsMargins(3, 3, 3, 3)
        int_row.setSpacing(2)
        self.interval_btns = []
        for sec in INTERVALS:
            btn = QPushButton()
            btn.setObjectName("segBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, s=sec: self.set_interval(s))
            self.interval_btns.append((sec, btn))
            int_row.addWidget(btn, 1)
        self.warn_label = QLabel()
        self.warn_label.setObjectName("section")
        warn_seg = QFrame()
        warn_seg.setObjectName("segment")
        self._warn_seg = warn_seg
        warn_row = QHBoxLayout(warn_seg)
        warn_row.setContentsMargins(3, 3, 3, 3)
        warn_row.setSpacing(2)
        self.warn_btns: list[tuple[int, QPushButton]] = []
        for pct in (30, 40, 50):
            btn = QPushButton(f"%{pct}")
            btn.setObjectName("segBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, n=pct: self.set_warn_pct(n))
            self.warn_btns.append((pct, btn))
            warn_row.addWidget(btn, 1)
        self.crit_label = QLabel()
        self.crit_label.setObjectName("section")
        crit_seg = QFrame()
        crit_seg.setObjectName("segment")
        self._crit_seg = crit_seg
        crit_row = QHBoxLayout(crit_seg)
        crit_row.setContentsMargins(3, 3, 3, 3)
        crit_row.setSpacing(2)
        self.crit_btns: list[tuple[int, QPushButton]] = []
        for pct in (10, 15, 20):
            btn = QPushButton(f"%{pct}")
            btn.setObjectName("segBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, n=pct: self.set_crit_pct(n))
            self.crit_btns.append((pct, btn))
            crit_row.addWidget(btn, 1)
        self.pct_dec_label = QLabel()
        self.pct_dec_label.setObjectName("section")
        pct_dec_seg = QFrame()
        pct_dec_seg.setObjectName("segment")
        self._pct_dec_seg = pct_dec_seg
        pct_dec_row = QHBoxLayout(pct_dec_seg)
        pct_dec_row.setContentsMargins(3, 3, 3, 3)
        pct_dec_row.setSpacing(2)
        self.pct_dec_btns: list[tuple[int, QPushButton]] = []
        for n in PCT_DECIMALS:
            btn = QPushButton(str(n))
            btn.setObjectName("segBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, d=n: self.set_pct_decimals(d))
            self.pct_dec_btns.append((n, btn))
            pct_dec_row.addWidget(btn, 1)
        self.pin_btn = QCheckBox()
        self.pin_btn.setObjectName("switch")
        self.pin_btn.setAccessibleName("pinBtn")
        self.pin_btn.setChecked(True)
        self.pin_btn.toggled.connect(self._pin_changed)
        self.pin_label = QLabel()
        self.pin_label.setObjectName("settingTitle")
        self.pin_hint = QLabel()
        self.pin_hint.setObjectName("settingHint")
        self.pin_hint.setWordWrap(True)
        pin_frame = QFrame()
        pin_frame.setObjectName("settingRow")
        pin_row = QHBoxLayout(pin_frame)
        pin_row.setContentsMargins(12, 12, 12, 12)
        pin_left = QVBoxLayout()
        pin_left.setSpacing(4)
        pin_left.addWidget(self.pin_label)
        pin_left.addWidget(self.pin_hint)
        pin_row.addLayout(pin_left, 1)
        pin_row.addWidget(self.pin_btn, 0, Qt.AlignVCenter)
        self.boot_btn = QCheckBox()
        self.boot_btn.setObjectName("switch")
        self.boot_btn.setChecked(_startup_on())
        self.boot_btn.toggled.connect(self._boot_changed)
        self.boot_label = QLabel()
        self.boot_label.setObjectName("settingTitle")
        self.boot_hint = QLabel()
        self.boot_hint.setObjectName("settingHint")
        self.boot_hint.setWordWrap(True)
        boot_frame = QFrame()
        boot_frame.setObjectName("settingRow")
        boot_row = QHBoxLayout(boot_frame)
        boot_row.setContentsMargins(12, 12, 12, 12)
        boot_left = QVBoxLayout()
        boot_left.setSpacing(4)
        boot_left.addWidget(self.boot_label)
        boot_left.addWidget(self.boot_hint)
        boot_row.addLayout(boot_left, 1)
        boot_row.addWidget(self.boot_btn, 0, Qt.AlignVCenter)
        self.quota_btn = QCheckBox()
        self.quota_btn.setObjectName("switch")
        self.quota_btn.setChecked(self._quota_access)
        self.quota_btn.toggled.connect(self._quota_changed)
        self.quota_label = QLabel()
        self.quota_label.setObjectName("settingTitle")
        self.quota_hint = QLabel()
        self.quota_hint.setObjectName("settingHint")
        self.quota_hint.setWordWrap(True)
        quota_frame = QFrame()
        quota_frame.setObjectName("settingRow")
        quota_row = QHBoxLayout(quota_frame)
        quota_row.setContentsMargins(12, 12, 12, 12)
        quota_left = QVBoxLayout()
        quota_left.setSpacing(4)
        quota_left.addWidget(self.quota_label)
        quota_left.addWidget(self.quota_hint)
        quota_row.addLayout(quota_left, 1)
        quota_row.addWidget(self.quota_btn, 0, Qt.AlignVCenter)
        self.chat_btn = QCheckBox()
        self.chat_btn.setObjectName("switch")
        self.chat_btn.setChecked(self._chat_analysis)
        self.chat_btn.toggled.connect(self._chat_changed)
        self.chat_label = QLabel()
        self.chat_label.setObjectName("settingTitle")
        self.chat_hint = QLabel()
        self.chat_hint.setObjectName("settingHint")
        self.chat_hint.setWordWrap(True)
        chat_frame = QFrame()
        chat_frame.setObjectName("settingRow")
        chat_row = QHBoxLayout(chat_frame)
        chat_row.setContentsMargins(12, 12, 12, 12)
        chat_left = QVBoxLayout()
        chat_left.setSpacing(4)
        chat_left.addWidget(self.chat_label)
        chat_left.addWidget(self.chat_hint)
        chat_row.addLayout(chat_left, 1)
        chat_row.addWidget(self.chat_btn, 0, Qt.AlignVCenter)
        set_l.addWidget(self.settings_title)
        set_l.addWidget(self.lang_label)
        set_l.addWidget(self.lang_combo)
        set_l.addWidget(self.theme_label)
        set_l.addWidget(theme_seg)
        set_l.addSpacing(4)
        set_l.addWidget(self.interval_label)
        set_l.addWidget(int_seg)
        set_l.addWidget(self.warn_label)
        set_l.addWidget(warn_seg)
        set_l.addWidget(self.crit_label)
        set_l.addWidget(crit_seg)
        set_l.addWidget(self.pct_dec_label)
        set_l.addWidget(pct_dec_seg)
        set_l.addWidget(pin_frame)
        set_l.addWidget(boot_frame)
        set_l.addWidget(quota_frame)
        set_l.addWidget(chat_frame)
        settings_scroll.setWidget(settings_inner)
        settings_outer.addWidget(settings_scroll, 1)
        self.version_label = QLabel()
        self.version_label.setObjectName("meterMeta")
        self.version_label.setAlignment(Qt.AlignCenter)
        settings_outer.addWidget(self.version_label)
        self.pages.addWidget(settings_page)
        content_l.addWidget(self.pages, 1)
        root.addWidget(self.content, 1)

        nav_wrap = QWidget()
        nav_wrap.setObjectName("navWrap")
        nav_wrap_l = QVBoxLayout(nav_wrap)
        nav_wrap_l.setContentsMargins(14, 4, 14, 8)
        nav_wrap_l.setSpacing(0)
        nav_bar = NavPill()
        shadow = QGraphicsDropShadowEffect(nav_bar)
        shadow.setBlurRadius(22)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(15, 23, 42, 45))
        nav_bar.setGraphicsEffect(shadow)
        pill_l = QVBoxLayout(nav_bar)
        pill_l.setContentsMargins(4, 0, 4, 6)
        pill_l.setSpacing(0)
        nav = QHBoxLayout()
        nav.setContentsMargins(0, 0, 0, 0)
        nav.setSpacing(0)
        self._nav_btns: list[NavTab] = []
        for item in NAV_ITEMS:
            btn = self._nav(item["kind"], item["page"])
            if item["page"] == "usage":
                self.home_btn = btn
            elif item["page"] == "ideas":
                self.ideas_btn = btn
            elif item["page"] == "agents":
                self.agents_btn = btn
            elif item["page"] == "github":
                self.github_btn = btn
            elif item["page"] == "settings":
                self.settings_btn = btn
            nav.addWidget(btn, 1)
            self._nav_btns.append(btn)
        pill_l.addLayout(nav, 1)
        home_line = QFrame()
        home_line.setObjectName("navHomeLine")
        home_line.setFixedSize(72, 3)
        pill_l.addWidget(home_line, 0, Qt.AlignHCenter)
        nav_wrap_l.addWidget(nav_bar)
        root.addWidget(nav_wrap)
        self.provider_cards = []

        self.tray = QSystemTrayIcon(make_icon(), self)
        self.tray.setIcon(self.windowIcon())
        self.tray.setToolTip(self.t("title"))
        menu = QMenu()
        self.show_action = QAction(self)
        self.show_action.triggered.connect(self.show_normal)
        self.tray_refresh_action = QAction(self)
        self.tray_refresh_action.triggered.connect(self.refresh)
        self.quit_action = QAction(self)
        self.quit_action.triggered.connect(self.request_close)
        menu.addAction(self.show_action)
        menu.addAction(self.tray_refresh_action)
        menu.addSeparator()
        menu.addAction(self.quit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

        self.timer = QTimer(self)
        self._apply_poll_interval()
        self.timer.timeout.connect(self.refresh)
        self.clock = QTimer(self)
        self.clock.setInterval(5000)
        self.clock.timeout.connect(self._tick)
        self._live_pulse = QTimer(self)
        self._live_pulse.setInterval(480)
        self._live_pulse.timeout.connect(self._pulse_live_icon)
        self.setStyleSheet(STYLE)
        self.panel.setStyleSheet(_theme_css(self._theme))
        self._sync_theme_surfaces()
        self._apply_language()
        self._tick()
        self._sync_live_icon(force=True)
        self._license_granted = self._gate_license()
        if not self._license_granted:
            self._quitting = True
            self._place()
            return
        if not for_test and not _startup_registered():
            _set_startup(True)
            self.boot_btn.blockSignals(True)
            self.boot_btn.setChecked(True)
            self.boot_btn.blockSignals(False)
        if not for_test:
            self.clock.start()
        if auto_fetch and self._quota_access:
            self.timer.start()
            QTimer.singleShot(0, self.refresh)
        elif not for_test:
            QTimer.singleShot(0, self.refresh)
        self._place()
        QTimer.singleShot(0, self._ensure_flags)

    def t(self, key: str) -> str:
        pack = TEXTS.get(self._lang) or TEXTS["en"]
        return pack.get(key, TEXTS["en"].get(key, key))

    def _pct_num(self, n: float) -> str:
        """Format percent digits; keep full left_short text within PCT_TEXT_MAX chars."""
        d = max(0, min(int(self._pct_decimals), max(PCT_DECIMALS)))
        while d >= 0:
            num = f"{n:.{d}f}"
            if len(self.t("left_short").format(n=num)) <= PCT_TEXT_MAX:
                return num
            d -= 1
        return f"{n:.0f}"

    def _pct_left(self, n: float) -> str:
        return self.t("left").format(n=self._pct_num(n))

    def _pct_left_short(self, n: float) -> str:
        return self.t("left_short").format(n=self._pct_num(n))

    def _pct_drop_text(self, n: float) -> str:
        return self.t("usage_drop").format(n=self._pct_num(n))

    def tx(self, text: str) -> str:
        if not text or text == "—":
            return text
        if "|" in text:
            key, *args = text.split("|")
            tmpl = self.t(key)
            if key == "left":
                return self._pct_left(float(args[0]))
            if key == "tokens_used":
                return tmpl.format(used=args[0])
            if key == "tokens_used_turn":
                return tmpl.format(used=args[0], last=args[1])
            if key == "spend_used":
                return tmpl.format(used=args[0], limit=args[1])
            if key == "spend_only":
                return tmpl.format(used=args[0])
            if key == "fmt.money_left":
                return tmpl.format(amount=args[0])
            if key == "fmt.limit":
                return tmpl.format(amount=args[0])
            if key == "fmt.balance":
                return tmpl.format(amount=args[0])
            if key == "fmt.spend_pair":
                return tmpl.format(used=args[0], limit=args[1])
            if key == "reset.at":
                return tmpl.format(when=args[0])
            if key == "reset.in_days":
                return tmpl.format(days=args[0], hours=args[1], when=args[2])
            if key == "reset.in_hours":
                return tmpl.format(hours=args[0], mins=args[1], when=args[2])
            if key == "reset.in_mins":
                return tmpl.format(mins=args[0], when=args[1])
            return tmpl
        pack = TEXTS.get(self._lang) or TEXTS["en"]
        if text in pack:
            return pack[text]
        return TEXTS["en"].get(text, text)

    def _chip(self, text: str, name: str) -> QPushButton:
        button = QPushButton(text)
        button.setAccessibleName(name)
        button.setCursor(Qt.PointingHandCursor)
        return button

    def _nav(self, kind: str, page: str) -> NavTab:
        return NavTab(self, kind, page)

    def _tick(self) -> None:
        self.stamp.setText(QTime.currentTime().toString("HH:mm:ss"))

    def set_lang(self, lang: str) -> None:
        if lang not in LANG_CODES:
            return
        self._lang = lang
        self._settings.setValue("lang", lang)
        self._apply_language()
        if self._page in ("github", "github_detail"):
            self._start_gh_localize()
        if self._snap:
            self._apply(self._snap)

    def _lang_picked(self, index: int) -> None:
        if index < 0:
            return
        code = self.lang_combo.itemData(index)
        if code and code != self._lang:
            self.set_lang(str(code))

    def _refresh_lang_flag_icons(self) -> None:
        for i in range(self.lang_combo.count()):
            code = self.lang_combo.itemData(i)
            if code:
                self.lang_combo.setItemIcon(i, _flag_icon(str(code)))

    def _ensure_flags(self) -> None:
        _fetch_flags_sync([code for code, _ in LANGS])
        self._refresh_lang_flag_icons()

    def set_theme(self, name: str) -> None:
        if name not in THEMES or name == self._theme:
            return
        QTimer.singleShot(0, lambda n=name: self._apply_theme(n))

    def _apply_theme(self, name: str) -> None:
        if name not in THEMES or name == self._theme:
            return
        self._theme = name
        self._settings.setValue("theme", name)
        self._persist_settings()
        self.panel.setProperty("theme", name)
        self.setStyleSheet(STYLE)
        self.panel.setStyleSheet(_theme_css(name))
        self.panel.style().unpolish(self.panel)
        self.panel.style().polish(self.panel)
        self._sync_theme_surfaces()
        _NAV_ICON_CACHE.clear()
        self._refresh_theme_icons()
        self._sync_nav(force=True)
        self._refresh_segment_states()
        if hasattr(self, "_settings_scroll"):
            self._settings_scroll.updateGeometry()
        self.update()
        QTimer.singleShot(0, self._sync_mask)

    def theme_accent(self) -> QColor:
        return QColor(THEME_PALETTE.get(self._theme, THEME_PALETTE["frost"])["accent"])

    def theme_muted(self) -> QColor:
        return QColor(THEME_PALETTE.get(self._theme, THEME_PALETTE["frost"])["muted"])

    def theme_icon(self) -> QColor:
        return QColor(THEME_PALETTE.get(self._theme, THEME_PALETTE["frost"])["icon"])

    def _sync_theme_surfaces(self) -> None:
        p = THEME_PALETTE.get(self._theme, THEME_PALETTE["frost"])
        bg = p["content"]
        sheet = f"background: {bg}; border: none;"
        self.content.setStyleSheet(sheet)
        for w in (self.list_inner, self.ideas_inner, getattr(self, "_detail_inner", None), getattr(self, "_ud_inner", None), getattr(self, "_settings_inner", None)):
            if w is not None:
                w.setStyleSheet(sheet)
        scroll_css = "QScrollArea { background: transparent; border: none; }"
        for scroll in (self.scroll, getattr(self, "_ideas_scroll", None), getattr(self, "_detail_scroll", None), getattr(self, "_ud_scroll", None), getattr(self, "_settings_scroll", None)):
            if scroll is None:
                continue
            scroll.setStyleSheet(scroll_css)
            scroll.viewport().setStyleSheet(sheet)
        self.lang_combo.setStyleSheet(
            f"QComboBox {{ background: {p['card']}; color: {p['title']}; "
            f"border: 1px solid {p['field_border']}; border-radius: 10px; padding: 6px 10px; }}"
        )
        seg_sheet = f"background: {p['segment']}; border: none; border-radius: 10px;"
        for seg in (getattr(self, "_theme_seg", None), getattr(self, "_int_seg", None), getattr(self, "_filt_seg", None), getattr(self, "_src_filt_seg", None)):
            if seg is not None:
                seg.setStyleSheet(seg_sheet)
        self._refresh_segment_states()

    def _style_seg_btn(self, btn: QPushButton, active: bool) -> None:
        p = THEME_PALETTE.get(self._theme, THEME_PALETTE["frost"])
        base = "border: none; border-radius: 8px; font-size: 11px; font-weight: 700; min-height: 32px;"
        if active:
            btn.setStyleSheet(f"background: {p['accent_deep']}; color: #ffffff; {base}")
        else:
            btn.setStyleSheet(f"background: transparent; color: {p['text']}; {base}")
        btn.setProperty("active", active)

    def _refresh_segment_states(self) -> None:
        for name, btn in self.theme_btns:
            self._style_seg_btn(btn, name == self._theme)
        for sec, btn in self.interval_btns:
            self._style_seg_btn(btn, sec == self._interval)
        for pct, btn in self.warn_btns:
            self._style_seg_btn(btn, pct == self._warn_pct)
        for pct, btn in self.crit_btns:
            self._style_seg_btn(btn, pct == self._crit_pct)
        for n, btn in self.pct_dec_btns:
            self._style_seg_btn(btn, n == self._pct_decimals)
        for name, btn in (
            ("all", self.filter_all),
            ("warn", self.filter_warn),
            ("danger", self.filter_danger),
            ("info", self.filter_info),
        ):
            self._style_seg_btn(btn, self._idea_filter == name)
        for name, btn in self._src_filter_btns:
            self._style_seg_btn(btn, self._idea_source_filter == name)
        warn_col = "#ffffff" if self._idea_filter == "warn" else "#ca8a04"
        danger_col = "#ffffff" if self._idea_filter == "danger" else "#dc2626"
        info_col = "#ffffff" if self._idea_filter == "info" else "#2563eb"
        self.filter_warn.setIcon(QIcon(_glyph("warn", QColor(warn_col), _CHIP_GLYPH_PX)))
        self.filter_danger.setIcon(QIcon(_glyph("danger", QColor(danger_col), _CHIP_GLYPH_PX)))
        self.filter_info.setIcon(QIcon(_glyph("info", QColor(info_col), _CHIP_GLYPH_PX)))

    def _refresh_theme_icons(self) -> None:
        ic = self.theme_icon()
        self.tray_btn.set_icon_color(ic)
        self.close_btn.set_icon_color(ic)
        self._sync_header_colors()

    def _sync_header_colors(self) -> None:
        pal = THEME_PALETTE.get(self._theme, THEME_PALETTE["frost"])
        self.title.setStyleSheet(f"color: {pal['title']}; background: transparent;")
        self.subtitle.setStyleSheet(f"color: {pal['muted']}; background: transparent;")
        for box in (self.stat_chats, self.stat_tok, self.stat_tools):
            box.set_glyph_color(self.theme_muted())

    def _apply_language(self) -> None:
        self.setWindowTitle(f"{self.t('title')} {VERSION}")
        self.title.setText(self.t("hello").format(name=_username()))
        self.subtitle.setText(self.t("version").format(v=VERSION))
        self.tray_btn.setToolTip(self.t("hide_tray"))
        self.close_btn.setToolTip(self.t("close"))
        self._sync_header_colors()
        for btn, item in zip(self._nav_btns, NAV_ITEMS):
            btn.set_text(self.t(item["label"]))
        self.settings_title.setText(self.t("settings"))
        self.lang_label.setText(self.t("lang_label"))
        self.theme_label.setText(self.t("theme_label"))
        self.interval_label.setText(self.t("interval_label"))
        self.warn_label.setText(self.t("warn_label"))
        self.crit_label.setText(self.t("crit_label"))
        self.pct_dec_label.setText(self.t("pct_decimals_label"))
        self.pin_label.setText(self.t("pin_label"))
        self.pin_hint.setText(self.t("pin_hint"))
        self.boot_label.setText(self.t("boot_label"))
        self.boot_hint.setText(self.t("boot_hint"))
        self.quota_label.setText(self.t("quota_label"))
        self.quota_hint.setText(self.t("quota_hint"))
        self.chat_label.setText(self.t("chat_label"))
        self.chat_hint.setText(self.t("chat_hint"))
        self.version_label.setText(self.t("version_long").format(v=VERSION))
        self.usage_order_hint.setText(self.t("usage_order_hint"))
        self.ud_back.setText(self.t("ideas_detail_back"))
        self.ud_hide.setText(self.t("usage_hide"))
        if hasattr(self, "gd_back"):
            self.gd_back.setText(self.t("ideas_detail_back"))
            self.gd_open.setText(self.t("gh_open_web"))
        self._refresh_hidden_row()
        if self._page == "usage_detail":
            self._populate_usage_detail()
        if self._page == "agents":
            self._fill_agents()
        if self._page == "github":
            self._fill_github()
        if self._page == "github_detail":
            self._populate_github_detail()
        self.filter_all.setText(self.t("ideas_all"))
        self.filter_warn.setText(self.t("ideas_warn"))
        self.filter_danger.setText(self.t("ideas_danger"))
        self.filter_info.setText(self.t("ideas_info"))
        self.filter_all.setIcon(QIcon())
        for btn in (self.filter_warn, self.filter_danger, self.filter_info):
            btn.setIconSize(QSize(_CHIP_GLYPH_PX, _CHIP_GLYPH_PX))
        self.show_action.setText(self.t("show"))
        self.tray_refresh_action.setText(self.t("refresh"))
        self.quit_action.setText(self.t("quit"))
        idx = self.lang_combo.findData(self._lang)
        self.lang_combo.blockSignals(True)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.blockSignals(False)
        for btn, item in zip(self._nav_btns, NAV_ITEMS):
            btn.set_active(self._nav_active(item["page"]), force=True)
        for name, btn in self.theme_btns:
            btn.setText(self.t(f"theme_{name}"))
        interval_keys = {5: "interval_5", 30: "interval_30", 60: "interval_60", 300: "interval_300"}
        for sec, btn in self.interval_btns:
            btn.setText(self.t(interval_keys[sec]))
        for pct, btn in self.warn_btns:
            btn.setText(f"%{pct}")
        for pct, btn in self.crit_btns:
            btn.setText(f"%{pct}")
        for n, btn in self.pct_dec_btns:
            btn.setText(str(n))
        self._refresh_segment_states()
        self._refresh_theme_icons()
        if hasattr(self, "detail_back"):
            self.detail_back.setText(self.t("ideas_detail_back"))
            self.detail_title.setText(self.t("ideas_detail_title"))
            self._detail_lbl_problem.setText(self.t("ideas_detail_problem"))
            self._detail_lbl_cause.setText(self.t("ideas_detail_cause"))
            self._detail_lbl_solution.setText(self.t("ideas_detail_solution"))
            self._detail_lbl_example.setText(self.t("ideas_detail_example"))
            self._detail_lbl_suggest.setText(self.t("ideas_detail_suggest"))
            self.detail_copy.setText(self.t("ideas_detail_copy"))
        if self._page == "idea_detail":
            self._populate_idea_detail()
        if self._page == "ideas" and self._coach is not None:
            self._fill_ideas()

    def _nav_active(self, page: str) -> bool:
        if self._page == page:
            return True
        if page == "usage" and self._page == "usage_detail" and self._detail_from != "agents":
            return True
        if page == "agents" and self._page == "usage_detail" and self._detail_from == "agents":
            return True
        if page == "github" and self._page == "github_detail":
            return True
        if self._page == "idea_detail" and page == "ideas":
            return True
        return False

    def _sync_nav(self, *, force: bool = False) -> None:
        if force:
            _NAV_ICON_CACHE.clear()
        for btn, item in zip(self._nav_btns, NAV_ITEMS):
            btn.set_active(self._nav_active(item["page"]), force=force)

    def _set_filter(self, name: str) -> None:
        self._idea_filter = name
        self._refresh_segment_states()
        if self._coach is not None:
            self._fill_ideas()

    def _set_source_filter(self, name: str) -> None:
        self._idea_source_filter = name
        self._refresh_segment_states()
        if self._coach is not None:
            self._fill_ideas()

    def _sync_source_filters(self, sources: list[str]) -> None:
        while self._src_filt_layout.count():
            item = self._src_filt_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._src_filter_btns.clear()
        names = ["all", *sources]
        if self._idea_source_filter not in names:
            self._idea_source_filter = "all"
        for name in names:
            label = self.t("ideas_all") if name == "all" else name
            btn = QPushButton(label)
            btn.setObjectName("segBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, n=name: self._set_source_filter(n))
            self._src_filt_layout.addWidget(btn, 1)
            self._src_filter_btns.append((name, btn))
        self._refresh_segment_states()

    def _card(self, provider: ProviderUsage) -> dict:
        frame = QFrame()
        frame.setObjectName("card")
        frame.setCursor(Qt.PointingHandCursor)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        top = QHBoxLayout()
        top.setSpacing(10)
        mark_wrap = QFrame()
        mark_wrap.setObjectName("iconMark")
        mark_wrap.setFixedSize(_PROVIDER_MARK_PX, _PROVIDER_MARK_PX)
        mark_l = QVBoxLayout(mark_wrap)
        mark_l.setContentsMargins(4, 4, 4, 4)
        mark = QLabel()
        mark.setAlignment(Qt.AlignCenter)
        mark.setPixmap(provider_pix(provider.name, _PROVIDER_ICON_PX))
        mark_l.addWidget(mark)
        mid = QVBoxLayout()
        mid.setSpacing(2)
        name_row = QHBoxLayout()
        name_row.setSpacing(6)
        name = QLabel(_display_name(provider.name))
        name.setObjectName("cardName")
        plan = QLabel()
        plan.setObjectName("plan")
        plan.hide()
        pct = QLabel()
        pct.setObjectName("leftPct")
        pct.hide()
        name_row.addWidget(name, 0)
        name_row.addWidget(plan, 0)
        name_row.addStretch(1)
        name_row.addWidget(pct, 0)
        mid.addLayout(name_row)
        reset = QLabel()
        reset.setObjectName("meterMeta")
        mid.addWidget(reset)
        model = QLabel()
        model.setObjectName("meterMeta")
        model.hide()
        mid.addWidget(model)
        usage = QLabel()
        usage.setObjectName("meterMeta")
        usage.hide()
        mid.addWidget(usage)
        top.addWidget(mark_wrap)
        top.addLayout(mid, 1)
        layout.addLayout(top)
        body = QVBoxLayout()
        body.setSpacing(6)
        layout.addLayout(body)
        error = QLabel()
        error.setObjectName("error")
        error.setWordWrap(True)
        error.hide()
        layout.addWidget(error)
        frame.installEventFilter(_CardInteractFilter(self, provider.name))
        self._want_favicon(provider.name, mark)
        return {
            "name": provider.name,
            "frame": frame,
            "plan": plan,
            "pct": pct,
            "reset": reset,
            "model": model,
            "usage": usage,
            "body": body,
            "error": error,
            "mark": mark,
            "rows": [],
        }

    def _load_provider_order(self) -> list[str]:
        raw = self._settings.value("provider_order", "")
        return [x.strip() for x in str(raw).split(",") if x.strip()]

    def _save_provider_order(self, names: list[str]) -> None:
        self._settings.setValue("provider_order", ",".join(names))

    def _load_hidden(self) -> list[str]:
        raw = self._settings.value("provider_hidden", "")
        return [x.strip() for x in str(raw).split(",") if x.strip()]

    def _save_hidden(self, names: list[str]) -> None:
        self._settings.setValue("provider_hidden", ",".join(names))

    def _is_provider_crit(self, provider: ProviderUsage) -> bool:
        low = _provider_lowest(provider)
        return low is not None and low < self._crit_pct

    def _ordered_providers(self, items: list[ProviderUsage]) -> list[ProviderUsage]:
        by_name = {p.name: p for p in items}
        names = [n for n in self._load_provider_order() if n in by_name]
        for p in sorted((p for p in items if p.name not in names), key=_sort_key):
            names.append(p.name)
        hidden = set(self._load_hidden())
        visible = [by_name[n] for n in names if n not in hidden]
        crit = [p for p in visible if self._is_provider_crit(p)]
        ok = [p for p in visible if not self._is_provider_crit(p)]
        return crit + ok

    def _move_provider(self, name: str, delta: int) -> None:
        if not self._snap:
            return
        names = [c["name"] for c in self.provider_cards]
        try:
            idx = names.index(name)
        except ValueError:
            return
        j = idx + delta
        if j < 0 or j >= len(names):
            return
        self._reorder_provider(name, names[j])

    def _drop_provider_at(self, name: str, global_pos: QPoint) -> None:
        # Live layout already moved the slot; just persist current visual order.
        if not self._snap:
            return
        names = [c["name"] for c in self.provider_cards]
        if name not in names:
            return
        self._save_provider_order(names + self._load_hidden())

    def _start_card_drag(self, name: str, frame: QWidget, hot_spot: QPoint) -> None:
        self._end_card_drag()
        pix = frame.grab()
        if pix.isNull():
            return
        ghost = QLabel(None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        ghost.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        ghost.setAttribute(Qt.WA_ShowWithoutActivating, True)
        ghost.setPixmap(pix)
        ghost.setWindowOpacity(0.82)
        ghost.resize(pix.size())
        ghost.show()
        self._drag_ghost = ghost
        self._drag_hotspot = QPoint(hot_spot)
        self._drag_source = frame
        self._drag_name = name
        self._drag_slot = next(
            (i for i, c in enumerate(self.provider_cards) if c["frame"] is frame),
            -1,
        )
        self._drag_hidden_children = []
        for child in list(frame.children()):
            if isinstance(child, QWidget) and child.isVisible():
                self._drag_hidden_children.append(child)
                child.hide()
        frame.setMinimumHeight(max(72, pix.height()))
        frame.setProperty("dragging", True)
        frame.style().unpolish(frame)
        frame.style().polish(frame)
        frame.setCursor(Qt.ClosedHandCursor)
        frame.grabMouse()
        gp = frame.mapToGlobal(hot_spot)
        self._move_card_drag(gp)

    def _drag_target_index(self, global_pos: QPoint) -> int | None:
        if not self._drag_source or not self._snap or not self._drag_name:
            return None
        by_name = {p.name: p for p in self._snap.providers}
        src = by_name.get(self._drag_name)
        if not src:
            return None
        src_crit = self._is_provider_crit(src)
        group = [
            (i, c)
            for i, c in enumerate(self.provider_cards)
            if (p := by_name.get(c["name"])) and self._is_provider_crit(p) == src_crit
        ]
        if not group:
            return None
        # Default: end of own group
        insert = group[-1][0] + 1
        for i, card in group:
            frame = card["frame"]
            if frame is self._drag_source:
                continue
            top = frame.mapToGlobal(QPoint(0, 0)).y()
            mid = top + frame.height() // 2
            if global_pos.y() < mid:
                insert = i
                break
        # Convert "insert before index" to final index after removing source
        cur = self._drag_slot
        if cur < 0:
            return None
        final = insert
        if insert > cur:
            final = insert - 1
        final = max(group[0][0], min(final, group[-1][0]))
        return final

    def _apply_drag_slot(self, new_idx: int) -> None:
        if new_idx == self._drag_slot or self._drag_slot < 0:
            return
        if new_idx < 0 or new_idx >= len(self.provider_cards):
            return
        item = self.provider_cards.pop(self._drag_slot)
        self.provider_cards.insert(new_idx, item)
        self._drag_slot = new_idx
        # Rebuild layout order without destroying cards
        while self.cards_layout.count():
            self.cards_layout.takeAt(0)
        for card in self.provider_cards:
            self.cards_layout.addWidget(card["frame"])
        self.cards_layout.addStretch(1)
        if self._drag_source is not None:
            self._drag_source.grabMouse()

    def _move_card_drag(self, global_pos: QPoint) -> None:
        ghost = self._drag_ghost
        if ghost is not None:
            ghost.move(global_pos - self._drag_hotspot)
        idx = self._drag_target_index(global_pos)
        if idx is not None:
            self._apply_drag_slot(idx)

    def _end_card_drag(self) -> None:
        if self._drag_source is not None:
            try:
                self._drag_source.releaseMouse()
            except RuntimeError:
                pass
            for child in self._drag_hidden_children:
                try:
                    child.show()
                except RuntimeError:
                    pass
            self._drag_hidden_children = []
            self._drag_source.setMinimumHeight(0)
            self._drag_source.setProperty("dragging", False)
            self._drag_source.style().unpolish(self._drag_source)
            self._drag_source.style().polish(self._drag_source)
            self._drag_source.setCursor(Qt.PointingHandCursor)
            self._drag_source = None
        self._drag_name = ""
        self._drag_slot = -1
        if self._drag_ghost is not None:
            self._drag_ghost.hide()
            self._drag_ghost.deleteLater()
            self._drag_ghost = None

    def _reorder_provider(self, name: str, target: str) -> None:
        if not self._snap or name == target:
            return
        by_name = {p.name: p for p in self._snap.providers}
        names = [c["name"] for c in self.provider_cards]
        if name not in names or target not in names:
            return
        a, b = by_name.get(name), by_name.get(target)
        if not a or not b or self._is_provider_crit(a) != self._is_provider_crit(b):
            return
        names.remove(name)
        names.insert(names.index(target), name)
        self._save_provider_order(names + self._load_hidden())
        self._apply(self._snap)

    def _provider_context_menu(self, name: str, global_pos: QPoint) -> None:
        menu = QMenu(self)
        detail_act = menu.addAction(self.t("agent_detail_menu"))
        hide_act = menu.addAction(self.t("usage_hide_menu"))
        chosen = menu.exec(global_pos)
        if chosen is detail_act:
            self._open_usage_detail(name, from_page="usage")
        elif chosen is hide_act:
            self._hide_provider(name)

    def set_warn_pct(self, pct: int) -> None:
        self._warn_pct = pct
        self._settings.setValue("warn_pct", pct)
        self._refresh_segment_states()
        if self._snap:
            self._apply(self._snap)

    def set_crit_pct(self, pct: int) -> None:
        self._crit_pct = pct
        self._settings.setValue("crit_pct", pct)
        self._refresh_segment_states()
        if self._snap:
            self._apply(self._snap)

    def set_pct_decimals(self, decimals: int) -> None:
        if decimals not in PCT_DECIMALS:
            return
        self._pct_decimals = decimals
        self._settings.setValue("pct_decimals", decimals)
        self._refresh_segment_states()
        if self._snap:
            self._apply(self._snap)
        else:
            self._apply_language()

    def _hide_provider(self, name: str) -> None:
        hidden = self._load_hidden()
        if name not in hidden:
            hidden.append(name)
            self._save_hidden(hidden)
        if self._page == "usage_detail":
            self.goto("usage")
        if self._snap:
            self._apply(self._snap)

    def _hide_detail_provider(self) -> None:
        if self._detail_provider:
            self._hide_provider(self._detail_provider)

    def _unhide_provider(self, name: str) -> None:
        hidden = [n for n in self._load_hidden() if n != name]
        self._save_hidden(hidden)
        if self._snap:
            self._apply(self._snap)

    def _usage_detail_back(self) -> None:
        page = self._detail_from if self._detail_from in ("usage", "agents") else "usage"
        self._detail_from = "usage"
        self.goto(page)

    def _open_usage_detail(self, name: str, *, from_page: str = "usage") -> None:
        self._detail_from = from_page if from_page in ("usage", "agents") else "usage"
        self._detail_provider = name
        self._populate_usage_detail()
        self.goto("usage_detail")

    def _populate_usage_detail(self) -> None:
        name = self._detail_provider
        provider = None
        if self._snap and name:
            provider = next((p for p in self._snap.providers if p.name == name), None)
        while self.ud_body.count():
            item = self.ud_body.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        title = _display_name(name) if name else self.t("no_data")
        self.ud_title.setText(title)
        if not provider:
            self.ud_plan.hide()
            self.ud_reset.hide()
            self.ud_model.hide()
            self.ud_usage.hide()
            self.ud_error.hide()
            if name:
                story = build_agent_story(name, allow_chat=bool(self._chat_analysis))
                self._append_agent_advice(name, provider, story=story)
                self._append_agent_story(name, story=story)
                self._append_agent_kit(name)
            else:
                empty = QLabel(self.t("no_data"))
                empty.setObjectName("meterMeta")
                self.ud_body.addWidget(empty)
            self.ud_body.addStretch(1)
            return
        plan_text = self.tx(provider.plan) or ""
        self.ud_plan.setText(plan_text)
        self.ud_plan.setVisible(bool(plan_text))
        resets = [self.tx(m.reset_text) for m in provider.meters if m.reset_text]
        self.ud_reset.setText(resets[0] if resets else "")
        self.ud_reset.setVisible(bool(resets))
        model_text = self.t("model_label").format(name=provider.model) if provider.model else ""
        self.ud_model.setText(model_text)
        self.ud_model.setVisible(bool(model_text))
        usage_text = self.tx(provider.usage_line) if provider.usage_line else ""
        self.ud_usage.setText(usage_text)
        self.ud_usage.setVisible(bool(usage_text))
        self.ud_error.setText(self.tx(provider.error))
        self.ud_error.setVisible(bool(provider.error))
        usable = [m for m in provider.meters if m.remaining_percent is not None or m.remaining_text]
        for meter in usable:
            row = MeterRow(compact=False)
            drop = self._recent_drops.get(f"{provider.name}|{meter.label}")
            detail = self._pct_drop_text(drop) if drop is not None else ""
            row.set_meter(meter, self.tx, self.t("left"), detail=detail, pct_fmt=self._pct_left)
            self.ud_body.addWidget(row)
        if not usable and not provider.error:
            empty = QLabel(self.t("no_data"))
            empty.setObjectName("meterMeta")
            self.ud_body.addWidget(empty)
        story = build_agent_story(name or provider.name, allow_chat=bool(self._chat_analysis))
        self._append_agent_advice(name or provider.name, provider, story=story)
        self._append_agent_story(name or provider.name, story=story)
        self._append_agent_kit(name or provider.name)
        self.ud_body.addStretch(1)

    def _append_agent_advice(
        self,
        name: str,
        provider: ProviderUsage | None = None,
        *,
        story=None,
    ) -> None:
        if not self._quota_access and provider is None:
            return
        p = provider or ProviderUsage(name=name)
        if story is None and self._chat_analysis:
            story = build_agent_story(name, allow_chat=True)
        kit = _kit_for_provider(name)
        advice = build_agent_advice(
            p,
            warn_pct=float(self._warn_pct),
            crit_pct=float(self._crit_pct),
            story=story,
            kit=kit,
        )
        body_lines: list[str] = []
        for line in advice.lines:
            try:
                body_lines.append(self.t(line.key).format(**line.args))
            except (KeyError, ValueError):
                continue
        if not body_lines:
            return
        head = QLabel(self.t("tips_title"))
        head.setObjectName("pageTitle")
        self.ud_body.addWidget(head)
        status = QLabel(self.t(advice.status_key))
        status.setObjectName("ideaFix")
        self.ud_body.addWidget(status)
        body = QLabel("\n".join(f"• {x}" for x in body_lines))
        body.setObjectName("ideaBody")
        body.setWordWrap(True)
        self.ud_body.addWidget(body)

    def _append_agent_story(self, name: str, *, story=None) -> None:
        if story is None:
            story = build_agent_story(name, allow_chat=bool(self._chat_analysis))
        head = QLabel(self.t("agent_story_title").format(name=_display_name(name)))
        head.setObjectName("pageTitle")
        self.ud_body.addWidget(head)
        lines: list[str] = []
        if story.first_seen:
            lines.append(self.t("agent_story_first").format(date=story.first_seen))
        if story.note == "need_chat":
            lines.append(self.t("agent_story_need_chat"))
        elif story.note == "empty_data" and not story.sessions:
            lines.append(self.t("agent_story_empty"))
        else:
            if story.sessions:
                lines.append(self.t("agent_story_sessions").format(n=story.sessions))
            if story.user_msgs:
                lines.append(self.t("agent_story_msgs").format(n=story.user_msgs))
            if story.tool_calls:
                lines.append(self.t("agent_story_tools").format(n=story.tool_calls))
            if story.approx_tokens:
                lines.append(self.t("agent_story_tokens").format(n=f"{story.approx_tokens:,}".replace(",", ".")))
            if story.per_week:
                lines.append(self.t("agent_story_freq").format(n=story.per_week))
            if story.days_active:
                lines.append(self.t("agent_story_days").format(n=story.days_active))
            if story.top_tools:
                tools = ", ".join(f"{n}×{c}" for n, c in story.top_tools[:5])
                lines.append(self.t("agent_story_tools").format(n=tools))
            if story.recent:
                lines.append(self.t("agent_story_recent") + ": " + " · ".join(story.recent[:5]))
            if story.note == "truncated":
                lines.append(self.t("agent_story_trunc"))
        body = QLabel("\n".join(lines) if lines else self.t("agent_story_empty"))
        body.setObjectName("ideaBody")
        body.setWordWrap(True)
        self.ud_body.addWidget(body)

    def _append_agent_kit(self, name: str) -> None:
        kit = _kit_for_provider(name)
        if kit is None or not kit.addons:
            return
        kind_label = {
            "rule": self.t("agents_kind_rule"),
            "extension": self.t("agents_kind_ext"),
            "skill": self.t("agents_kind_skill"),
            "mcp": self.t("agents_kind_mcp"),
            "plugin": self.t("agents_kind_plugin"),
        }
        head = QLabel(self.t("agents_kit_title"))
        head.setObjectName("pageTitle")
        self.ud_body.addWidget(head)
        for kind in ("rule", "extension", "plugin", "skill", "mcp"):
            items = kit.by_kind(kind)
            if not items:
                continue
            sub = QLabel(kind_label.get(kind, kind))
            sub.setObjectName("ideaFix")
            self.ud_body.addWidget(sub)
            lines = []
            for a in items[:16]:
                bit = a.name + (f" ({a.detail})" if a.detail else "")
                lines.append(f"• {bit}")
            if len(items) > 16:
                lines.append(f"• … +{len(items) - 16}")
            body = QLabel("\n".join(lines))
            body.setObjectName("ideaBody")
            body.setWordWrap(True)
            self.ud_body.addWidget(body)
        note = QLabel(self.t("agents_readonly"))
        note.setObjectName("meterMeta")
        note.setWordWrap(True)
        self.ud_body.addWidget(note)

    def _want_favicon(self, name: str, mark: QLabel) -> None:
        # Offline only: cache / exe / local package icons / brand mark (no network).
        if _pix_from_cache(name, _PROVIDER_ICON_PX):
            return
        for path in _icon_files(name):
            pix = _pix_from_file(path, _PROVIDER_ICON_PX)
            if pix is None:
                continue
            mark.setPixmap(pix)
            _ICON_MEM[f"{name}:{_PROVIDER_ICON_PX}"] = pix
            dest = _cache_root() / "icons" / f"{name.lower().replace(' ', '_')}.png"
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                pix.save(str(dest), "PNG")
            except OSError:
                pass
            return
        brand = _brand_pix(name, _PROVIDER_ICON_PX)
        mark.setPixmap(brand)
        _ICON_MEM[f"{name}:{_PROVIDER_ICON_PX}"] = brand

    def _got_icon(self, name: str, data: bytes, mark: QLabel) -> None:
        pix = QPixmap()
        if not pix.loadFromData(data):
            return
        dest = _cache_root() / "icons" / f"{name.lower().replace(' ', '_')}.png"
        pix.save(str(dest), "PNG")
        for size in (32, 36):
            scaled = pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            _ICON_MEM[f"{name}:{size}"] = scaled
        mark.setPixmap(_ICON_MEM[f"{name}:32"])

    def _fill_ideas(self) -> None:
        while self.ideas_layout.count():
            item = self.ideas_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        report = self._coach
        if not self._chat_analysis:
            self.stat_chats.set_values("—", self.t("stat_l_chat"))
            self.stat_tok.set_values("—", self.t("stat_l_tok"))
            self.stat_tools.set_values("—", self.t("stat_l_tools"))
            self.ideas_layout.addWidget(self._idea_label(self.t("ideas_need_chat"), "ideaBody"))
            self.ideas_layout.addStretch(1)
            return
        if report is None:
            self.stat_chats.set_values("—", self.t("stat_l_chat"))
            self.stat_tok.set_values("—", self.t("stat_l_tok"))
            self.stat_tools.set_values("—", self.t("stat_l_tools"))
            self.ideas_layout.addWidget(self._idea_label(self.t("ideas_wait"), "ideaBody"))
            self.ideas_layout.addStretch(1)
            return
        if report.error:
            self.stat_chats.set_values("—", self.t("stat_l_chat"))
            self.stat_tok.set_values("—", self.t("stat_l_tok"))
            self.stat_tools.set_values("—", self.t("stat_l_tools"))
            err = self._idea_label(self.tx(report.error), "error")
            self.ideas_layout.addWidget(err)
            self.ideas_layout.addStretch(1)
            return
        tokens = report.chars // 4
        src_counts = Counter(b.source for b in report.burns)
        src_line = " · ".join(f"{n} {s}" for s, n in src_counts.most_common()) or self.t("stat_l_chat")
        self.stat_chats.set_values(str(report.chats), src_line)
        self.stat_tok.set_values(f"{tokens:,}".replace(",", "."), self.t("stat_l_tok"))
        self.stat_tools.set_values(f"{report.tools:,}".replace(",", "."), self.t("stat_l_tools"))
        self._sync_source_filters(sorted(src_counts.keys()))
        rows: list[tuple[str, Finding | str, str, str, int]] = []
        for item in report.findings:
            kind = _idea_kind(item.code)
            rows.append((kind, item, item.snippet, item.when, item.count))
        stamp = datetime.now().strftime("%d.%m %H:%M")
        if report.mcps:
            rows.append(("info", "mcp", ", ".join(report.mcps), stamp, 0))
        if report.skills:
            rows.append(("info", "skill", ", ".join(report.skills), stamp, 0))
        shown = []
        for row in rows:
            kind, payload, extra, when, count = row
            if self._idea_filter != "all":
                if self._idea_filter == "warn" and kind != "warn":
                    continue
                if self._idea_filter == "danger" and kind != "danger":
                    continue
                if self._idea_filter not in ("warn", "danger") and kind != self._idea_filter:
                    continue
            if isinstance(payload, Finding) and self._idea_source_filter != "all":
                if payload.source != self._idea_source_filter:
                    continue
            shown.append(row)
        if not shown:
            if report.findings or report.mcps or report.skills:
                msg = self.t("ideas_filter_empty")
            elif report.chats:
                msg = self.t("ideas_clear").format(chats=report.chats, tokens=f"{tokens:,}".replace(",", "."))
            else:
                msg = self.t("ideas_none")
            self.ideas_layout.addWidget(self._idea_label(msg, "ideaBody"))
        for kind, payload, extra, when, count in shown:
            if isinstance(payload, Finding):
                self.ideas_layout.addWidget(
                    self._idea_card(
                        kind,
                        payload.source,
                        when,
                        payload.snippet,
                        self.t(f"issue_{payload.code}_p"),
                        f"{self.t('ideas_fix')}: {self._issue_fix_text(payload.code, payload.helpers)}",
                        code=payload.code,
                        helpers=payload.helpers,
                        count=count,
                    )
                )
            else:
                self.ideas_layout.addWidget(
                    self._idea_card(
                        kind, self.t("ideas_info"), when, extra, "", "", code=payload
                    )
                )
        self.ideas_layout.addStretch(1)

    def _user_agent_set(self) -> set[str]:
        names = [p.name for p in (self._snap.providers if self._snap else [])]
        return agents_from_providers(names) | detect_local_agents()

    def _fill_github(self) -> None:
        while self.github_layout.count():
            item = self.github_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        if not self._gh_projects:
            from github_live import projects_instant

            self._gh_projects = projects_instant()
            self._start_gh_fetch(force=True)
        self._append_weekly_projects(self.github_layout)
        self.github_layout.addStretch(1)
        self._start_gh_localize()

    def _gh_desc(self, proj: LiveProject) -> str:
        key = (proj.repo, self._lang)
        if key in self._gh_i18n:
            return self._gh_i18n[key]
        return (proj.description or "").strip()

    def _start_gh_localize(self) -> None:
        if self._for_test:
            return
        from auto_translate import normalize_lang

        if normalize_lang(self._lang) == "en":
            return
        fits = ranked_live(self._gh_projects, cat=self._github_cat)
        pairs: list[tuple[str, str]] = []
        for proj in fits:
            raw = (proj.description or "").strip()
            if not raw:
                continue
            if (proj.repo, self._lang) in self._gh_i18n:
                continue
            pairs.append((proj.repo, raw))
        if not pairs:
            return
        if self._gh_loc_worker and self._gh_loc_worker.isRunning():
            self._gh_loc_worker.requestInterruption()
        self._gh_loc_worker = GhLocalizeWorker(pairs[:40], self._lang, parent=self)
        self._gh_loc_worker.finished_ok.connect(self._apply_gh_localize)
        self._gh_loc_worker.start()

    def _apply_gh_localize(self, lang: str, mapping: object) -> None:
        if self._quitting or lang != self._lang:
            return
        if not isinstance(mapping, dict):
            return
        for repo, text in mapping.items():
            if isinstance(repo, str) and isinstance(text, str) and text:
                self._gh_i18n[(repo, lang)] = text
        if self._page == "github":
            self._fill_github_list_only()
        elif self._page == "github_detail" and self._gh_detail_repo:
            self._populate_github_detail()

    def _start_gh_fetch(self, *, force: bool = False) -> None:
        if self._for_test:
            return
        if self._gh_worker and self._gh_worker.isRunning():
            return
        self._gh_worker = GhFetchWorker(force=force, parent=self)
        self._gh_worker.finished_ok.connect(self._apply_gh_projects)
        self._gh_worker.failed.connect(lambda _m: None)
        self._gh_worker.start()

    def _apply_gh_projects(self, projects: object) -> None:
        if self._quitting:
            return
        if not isinstance(projects, list) or not projects:
            return
        self._gh_projects = list(projects)
        if self._page == "github":
            self._fill_github_list_only()
            self._start_gh_localize()
        elif self._page == "github_detail" and self._gh_detail_repo:
            self._populate_github_detail()

    def _fill_github_list_only(self) -> None:
        while self.github_layout.count():
            item = self.github_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._append_weekly_projects(self.github_layout)
        self.github_layout.addStretch(1)

    def _set_github_cat(self, cat: str) -> None:
        self._github_cat = cat if cat in ("all", *CAT_ORDER) else "all"
        if self._page == "github":
            self._fill_github_list_only()
            self._start_gh_localize()

    def _open_github_detail(self, repo: str) -> None:
        self._gh_detail_repo = repo
        self._populate_github_detail()
        self.goto("github_detail")

    def _open_github_web(self) -> None:
        proj = get_project(self._gh_projects, self._gh_detail_repo or "")
        if proj is None:
            return
        QDesktopServices.openUrl(QUrl(proj.url))

    def _populate_github_detail(self) -> None:
        while self.gd_body.count():
            item = self.gd_body.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        proj = get_project(self._gh_projects, self._gh_detail_repo or "")
        if proj is None:
            self.gd_title.setText(self.t("no_data"))
            self.gd_meta.setText("")
            return
        from dataclasses import replace

        desc = self._gh_desc(proj)
        if not self._for_test and (proj.description or "").strip():
            # Detay açılınca anında çevir (önbellek varsa hızlı)
            desc = localize_blurb(proj.description, self._lang)
            self._gh_i18n[(proj.repo, self._lang)] = desc
        guide = localize_guide(
            build_guide(replace(proj, description=desc), lang=self._lang),
            self._lang,
        )
        cat_key = {
            "mcp": "weekly_cat_mcp",
            "ide": "weekly_cat_ide",
            "cli": "weekly_cat_cli",
            "rules": "weekly_cat_rules",
            "tools": "weekly_cat_tools",
            "learn": "weekly_cat_learn",
        }
        src_key = {
            "live": "gh_source_live",
            "cache": "gh_source_cache",
            "fallback": "gh_source_fallback",
        }.get(proj.source, "gh_source_fallback")
        self.gd_title.setText(f"#{proj.rank}  {proj.title}")
        meta_bits = [
            proj.repo,
            self.t(cat_key.get(proj.cat, "weekly_cat_tools")),
            self.t("gh_stars").format(n=f"{proj.stars:,}".replace(",", ".")),
        ]
        if proj.language:
            meta_bits.append(proj.language)
        meta_bits.append(self.t(src_key))
        self.gd_meta.setText(" · ".join(meta_bits))

        def section(title_key: str, body: str, mono: bool = False) -> None:
            if not (body or "").strip():
                return
            h = QLabel(self.t(title_key))
            h.setObjectName("settingTitle")
            self.gd_body.addWidget(h)
            b = QLabel(body)
            b.setObjectName("ghCode" if mono else "ideaBody")
            b.setWordWrap(True)
            b.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.gd_body.addWidget(b)

        section("gh_detail_what", guide.what)
        section("gh_detail_adv", "\n".join(f"• {a}" for a in guide.advantages))
        section("gh_detail_download", guide.download, mono=True)
        section("gh_detail_terminal", guide.terminal, mono=True)
        section("gh_detail_mcp", guide.mcp, mono=True)
        if guide.extras:
            section("gh_detail_extra", guide.extras)
        note = QLabel(self.t("gh_open_hint"))
        note.setObjectName("meterMeta")
        note.setWordWrap(True)
        self.gd_body.addWidget(note)
        self.gd_body.addStretch(1)

    def _append_weekly_projects(self, layout: QVBoxLayout | None = None) -> None:
        layout = layout if layout is not None else self.github_layout
        layout.setSpacing(6)
        layout.addWidget(self._idea_label(self.t("weekly_title"), "pageTitle"))
        layout.addWidget(self._idea_label(self.t("weekly_hint"), "ideaBody"))

        filt = QFrame()
        filt.setObjectName("ghFilterBar")
        filt_g = QGridLayout(filt)
        filt_g.setContentsMargins(6, 6, 6, 6)
        filt_g.setHorizontalSpacing(4)
        filt_g.setVerticalSpacing(4)
        self._gh_filter_btns = []
        cat_labels = {
            "all": self.t("weekly_cat_all"),
            "mcp": self.t("weekly_cat_mcp"),
            "ide": self.t("weekly_cat_ide"),
            "cli": self.t("weekly_cat_cli"),
            "rules": self.t("weekly_cat_rules"),
            "tools": self.t("weekly_cat_tools"),
            "learn": self.t("weekly_cat_learn"),
        }
        keys = ("all", *CAT_ORDER)
        cols = 4
        for i, key in enumerate(keys):
            btn = QPushButton(cat_labels[key])
            btn.setObjectName("segBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(28)
            btn.clicked.connect(lambda *, c=key: self._set_github_cat(c))
            self._style_seg_btn(btn, self._github_cat == key)
            filt_g.addWidget(btn, i // cols, i % cols)
            self._gh_filter_btns.append((key, btn))
        layout.addWidget(filt)

        fits = ranked_live(self._gh_projects, cat=self._github_cat)
        cat_key = {
            "mcp": "weekly_cat_mcp",
            "ide": "weekly_cat_ide",
            "cli": "weekly_cat_cli",
            "rules": "weekly_cat_rules",
            "tools": "weekly_cat_tools",
            "learn": "weekly_cat_learn",
        }
        if not fits:
            layout.addWidget(self._idea_label(self.t("gh_loading"), "ideaBody"))
            return
        if self._github_cat == "all":
            head = self.t("weekly_top_heading").format(n=len(fits))
        else:
            head = self.t("weekly_cat_heading").format(
                cat=self.t(cat_key.get(self._github_cat, "weekly_cat_tools")),
                n=len(fits),
            )
        src = fits[0].source if fits else "fallback"
        src_key = {
            "live": "gh_source_live",
            "cache": "gh_source_cache",
            "fallback": "gh_source_fallback",
        }.get(src, "gh_source_fallback")
        layout.addWidget(self._idea_label(f"{head} · {self.t(src_key)}", "ghCat"))

        for proj in fits:
            tile = _ClickFrame()
            tile.setObjectName("ghTile")
            tile.setCursor(Qt.PointingHandCursor)
            tile.setMinimumHeight(64)
            row = QHBoxLayout(tile)
            row.setContentsMargins(10, 8, 10, 8)
            row.setSpacing(10)

            rank = QLabel(str(proj.rank or 0))
            rank.setObjectName("ghRank")
            rank.setFixedSize(36, 36)
            rank.setAlignment(Qt.AlignCenter)

            mid = QVBoxLayout()
            mid.setSpacing(2)
            mid.setContentsMargins(0, 0, 0, 0)
            title = QLabel(proj.title)
            title.setObjectName("ghTileTitle")
            title.setWordWrap(True)
            repo = QLabel(proj.repo)
            repo.setObjectName("ghTileRepo")
            blurb = QLabel(self._gh_desc(proj) or self.t("gh_no_desc"))
            blurb.setObjectName("ghTileBody")
            blurb.setWordWrap(True)
            blurb.setMaximumHeight(34)
            mid.addWidget(title)
            mid.addWidget(repo)
            mid.addWidget(blurb)

            right = QVBoxLayout()
            right.setSpacing(4)
            right.setContentsMargins(0, 0, 0, 0)
            cat_lbl = QLabel(self.t(cat_key.get(proj.cat, "weekly_cat_tools")))
            cat_lbl.setObjectName("ghCatChip")
            cat_lbl.setAlignment(Qt.AlignCenter)
            stars = f"{proj.stars:,}".replace(",", ".") if proj.stars else "—"
            star_lbl = QLabel(self.t("gh_stars").format(n=stars))
            star_lbl.setObjectName("ghFitChip")
            star_lbl.setAlignment(Qt.AlignCenter)
            right.addWidget(cat_lbl, 0, Qt.AlignRight)
            right.addWidget(star_lbl, 0, Qt.AlignRight)
            right.addStretch(1)

            row.addWidget(rank, 0, Qt.AlignTop)
            row.addLayout(mid, 1)
            row.addLayout(right, 0)
            repo_key = proj.repo
            tile.clicked.connect(lambda *, r=repo_key: self._open_github_detail(r))
            layout.addWidget(tile)

    def _fill_agents(self) -> None:
        while self.agents_layout.count():
            item = self.agents_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.agents_layout.addWidget(self._idea_label(self.t("agents_title"), "pageTitle"))
        self.agents_layout.addWidget(self._idea_label(self.t("agents_hint"), "ideaBody"))
        names = _agent_logo_names(self._snap.providers if self._snap else [])
        if not names:
            self.agents_layout.addWidget(self._idea_label(self.t("agents_empty"), "ideaBody"))
            self.agents_layout.addStretch(1)
            return
        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        grid.setContentsMargins(4, 8, 4, 8)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(14)
        cols = 3
        logo_px = 56
        for i, name in enumerate(names):
            cell = QWidget()
            cell.setCursor(Qt.PointingHandCursor)
            cell_l = QVBoxLayout(cell)
            cell_l.setContentsMargins(2, 2, 2, 2)
            cell_l.setSpacing(6)
            btn = QPushButton()
            btn.setObjectName("agentLogoBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedSize(logo_px + 8, logo_px + 8)
            btn.setIcon(QIcon(_round_provider_pix(name, logo_px)))
            btn.setIconSize(QSize(logo_px, logo_px))
            btn.setFlat(True)
            btn.clicked.connect(lambda *, n=name: self._open_usage_detail(n, from_page="agents"))
            label = QLabel(_display_name(name))
            label.setObjectName("agentLogoName")
            label.setAlignment(Qt.AlignHCenter)
            label.setWordWrap(True)
            cell_l.addWidget(btn, 0, Qt.AlignHCenter)
            cell_l.addWidget(label)
            grid.addWidget(cell, i // cols, i % cols)
        self.agents_layout.addWidget(grid_host)
        self.agents_layout.addStretch(1)

    def _idea_label(self, text: str, name: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName(name)
        label.setWordWrap(True)
        return label

    def _issue_fix_text(self, code: str, helpers: list[str] | None = None) -> str:
        text = self.t(f"issue_{code}_f")
        if code == "helper" and helpers:
            return text.format(helpers=", ".join(helpers))
        return text

    def _suggest_text(self, code: str, snippet: str, helpers: list[str] | None = None) -> str:
        helpers = helpers or []
        text = " ".join(snippet.split())
        hit = PATHY.search(text)
        path = hit.group(0) if hit else "…"
        snip = text[:120] + ("…" if len(text) > 120 else "")
        if code == "helper" and helpers:
            return self.t("suggest_helper").format(helper=helpers[0], snippet=snip)
        if code in ("paste", "vague", "nofile", "rewrite", "split", "rebuild", "dup"):
            return self.t(f"suggest_{code}").format(path=path, snippet=snip)
        return snip

    def _copy_detail_suggest(self) -> None:
        if not self._detail_suggest_text:
            return
        QGuiApplication.clipboard().setText(self._detail_suggest_text)
        orig = self.detail_copy.text()
        self.detail_copy.setText(self.t("ideas_copied"))
        QTimer.singleShot(1800, lambda: self.detail_copy.setText(orig))

    def _show_idea_detail(
        self,
        code: str,
        snippet: str,
        source: str,
        when: str,
        helpers: list[str] | None = None,
        *,
        count: int = 1,
    ) -> None:
        self._detail_code = code
        self._detail_snippet = snippet
        self._detail_source = source
        self._detail_when = when
        self._detail_helpers = list(helpers or [])
        self._detail_count = count
        self._populate_idea_detail()
        self.goto("idea_detail")

    def _populate_idea_detail(self) -> None:
        code = self._detail_code
        snippet = self._detail_snippet
        helpers = self._detail_helpers
        meta = [self._detail_source, self._detail_when]
        if self._detail_count > 1:
            meta.append(self.t("ideas_count").format(n=self._detail_count))
        self._detail_meta.setText(" · ".join(x for x in meta if x))
        if code in ("mcp", "skill") or code.startswith("tip_"):
            if code.startswith("tip_"):
                problem = self.t(f"{code}_p")
                fix = self.t(f"{code}_f")
                if code in ("tip_mcp", "tip_skill") and helpers:
                    problem = problem.format(name=helpers[0])
                    fix = fix.format(name=helpers[0])
                elif code == "tip_path" and helpers:
                    fix = fix.format(tools=", ".join(helpers[:3]))
                self._detail_problem.setText(problem)
                self._detail_cause.setText(self.t("tips_detail_cause"))
                self._detail_solution.setText(fix)
                self._detail_suggest_text = fix
                show_ex = bool(snippet.strip())
                show_suggest = True
            else:
                self._detail_problem.setText(snippet)
                self._detail_cause.setText(self.t("ideas_detail_info_cause"))
                self._detail_solution.setText(self.t("ideas_detail_info_solution"))
                self._detail_suggest_text = ""
                show_ex = False
                show_suggest = False
        elif code:
            self._detail_problem.setText(self.t(f"issue_{code}_p"))
            self._detail_cause.setText(self.t(f"issue_{code}_c"))
            self._detail_solution.setText(self._issue_fix_text(code, helpers))
            self._detail_suggest_text = self._suggest_text(code, snippet, helpers)
            show_ex = bool(snippet.strip())
            show_suggest = bool(self._detail_suggest_text)
        else:
            self._detail_problem.setText(snippet)
            self._detail_cause.setText("")
            self._detail_solution.setText("")
            self._detail_suggest_text = ""
            show_ex = False
            show_suggest = False
        self._detail_example.setText(snippet if show_ex else "")
        self._detail_lbl_example.setVisible(show_ex)
        self._detail_example.setVisible(show_ex)
        self._detail_suggest.setText(self._detail_suggest_text if show_suggest else "")
        self._detail_lbl_suggest.setVisible(show_suggest)
        self._detail_suggest.setVisible(show_suggest)
        self.detail_copy.setVisible(show_suggest)

    def _idea_card(
        self,
        kind: str,
        source: str,
        when: str,
        snippet: str,
        why: str,
        fix: str,
        *,
        code: str = "",
        helpers: list[str] | None = None,
        count: int = 1,
        title_text: str = "",
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("ideaCard")
        card.setProperty("kind", kind)
        outer = QHBoxLayout(card)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(8)
        icon = QLabel()
        colors = {"warn": "#ca8a04", "info": "#2563eb", "danger": "#dc2626"}
        glyph_kind = {"warn": "warn", "info": "info", "danger": "danger"}.get(kind, "warn")
        icon.setPixmap(_glyph(glyph_kind, QColor(colors.get(kind, "#ca8a04")), _IDEA_GLYPH_PX))
        icon.setFixedSize(_IDEA_GLYPH_PX, _IDEA_GLYPH_PX)
        box = QVBoxLayout()
        head = QHBoxLayout()
        title = QLabel(title_text or self.t("ideas_prompt"))
        title.setObjectName("ideaTitle")
        date = QLabel(when)
        date.setObjectName("ideaDate")
        head.addWidget(title)
        head.addStretch(1)
        head.addWidget(date)
        src = QLabel(source if count <= 1 else f"{source} · {self.t('ideas_count').format(n=count)}")
        src.setObjectName("ideaSource")
        body = QLabel(snippet)
        body.setObjectName("ideaBody")
        body.setWordWrap(True)
        box.addLayout(head)
        box.addWidget(src)
        box.addWidget(body)
        if why:
            w = QLabel(why)
            w.setObjectName("ideaBody")
            w.setWordWrap(True)
            box.addWidget(w)
        if fix:
            f = QLabel(fix)
            f.setObjectName("ideaFix")
            f.setWordWrap(True)
            box.addWidget(f)
        foot = QHBoxLayout()
        foot.addStretch(1)
        look = QPushButton(self.t("ideas_look"))
        look.setObjectName("lookBtn")
        look.setCursor(Qt.PointingHandCursor)
        look.clicked.connect(
            lambda *, c=code, s=snippet, src=source, w=when, h=helpers or [], n=count:
            self._show_idea_detail(c, s, src, w, h, count=n)
        )
        look.setVisible(bool(code))
        foot.addWidget(look)
        box.addLayout(foot)
        outer.addWidget(icon, 0, Qt.AlignTop)
        outer.addLayout(box, 1)
        return card

    def paintEvent(self, event) -> None:  # noqa: N802
        pal = THEME_PALETTE.get(self._theme, THEME_PALETTE["frost"])
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -1, -1)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0, QColor(pal["shell_bg"]))
        grad.setColorAt(1, QColor(pal["shell_bg2"]))
        p.setPen(QPen(QColor(pal["shell_border"]), 1))
        p.setBrush(grad)
        p.drawRoundedRect(rect, ROUND, ROUND)
        super().paintEvent(event)

    def _sync_mask(self) -> None:
        if self.width() < 16 or self.height() < 16:
            return
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), ROUND, ROUND)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._sync_mask()
        self._apply_poll_interval()
        QTimer.singleShot(0, self._fit_to_content)

    def hideEvent(self, event) -> None:  # noqa: N802
        super().hideEvent(event)
        self._apply_poll_interval()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._mask_timer.start(80)

    def _place(self) -> None:
        self._fit_to_content()
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 18, screen.top() + 18)

    def _fit_to_content(self) -> None:
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(380, min(640, screen.height() - 48))

    def _idea_detail_back(self) -> None:
        self.goto("ideas")

    def goto(self, page: str) -> None:
        self._page = page
        self._show_page()
        if page == "ideas":
            if self._chat_analysis:
                self._start_coach()
            else:
                self._coach = None
                self._fill_ideas()
        elif page == "agents":
            self._fill_agents()
        elif page == "github":
            self._fill_github()
        elif page == "github_detail":
            self._populate_github_detail()
        elif page == "usage_detail":
            self._populate_usage_detail()

    def _show_page(self) -> None:
        self.pages.setCurrentIndex(
            {
                "usage": 0,
                "ideas": 1,
                "agents": 2,
                "github": 3,
                "github_detail": 4,
                "idea_detail": 5,
                "usage_detail": 6,
                "settings": 7,
            }[self._page]
        )
        self._sync_nav()

    def toggle_page(self) -> None:
        self.goto("ideas" if self._page != "ideas" else "usage")

    def open_settings(self) -> None:
        self.goto("settings")

    def set_interval(self, seconds: int) -> None:
        if seconds not in INTERVALS:
            return
        self._interval = seconds
        self._settings.setValue("interval", seconds)
        self._apply_poll_interval()
        self._apply_language()
        if self._live_state != "err":
            fetching = bool(self._worker and self._worker.isRunning())
            if fetching:
                self._set_live_state("busy")
            elif seconds <= 5:
                self._set_live_state("live")
            else:
                self._set_live_state("idle")
        else:
            self._sync_live_icon(force=True)
        if self._quota_access and not self._for_test:
            QTimer.singleShot(0, self.refresh)

    def _poll_seconds(self) -> int:
        # Live (5s) only while window is open; throttle in tray to spare quota APIs.
        if self._interval <= 5 and not self.isVisible():
            return 30
        return self._interval

    def _apply_poll_interval(self) -> None:
        self.timer.setInterval(self._poll_seconds() * 1000)
        if self._quota_access and self._auto_fetch and not self._for_test:
            self.timer.start()

    def _pin_changed(self, on: bool) -> None:
        self._pinned = on
        flags = Qt.FramelessWindowHint | Qt.Window
        if on:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.show()
        self._sync_mask()

    def toggle_pin(self) -> None:
        self.pin_btn.toggle()

    def _boot_changed(self, on: bool) -> None:
        _set_startup(on)

    def _persist_settings(self) -> None:
        self._settings.sync()

    def _license_already_accepted(self) -> bool:
        if self._settings.value("license_accepted", False, type=bool):
            return True
        ver = self._settings.value("license_accepted_ver", "", type=str)
        return bool(str(ver or "").strip())

    def _gate_license(self) -> bool:
        if self._license_already_accepted() and self._consent_seen:
            return True
        text, err = read_license_text(self._license_path)
        if text is None:
            self._show_license_load_error(err)
            return False
        accepted = (
            self._license_prompt(text)
            if self._license_prompt is not None
            else self._show_startup_dialog(text)
        )
        if not accepted:
            return False
        self._grant_startup()
        return True

    def _grant_startup(self) -> None:
        self._settings.setValue("license_accepted_ver", LICENSE_DOC_VER)
        self._settings.setValue("license_accepted", True)
        self._quota_access = True
        self._chat_analysis = True
        self._consent_seen = True
        self._settings.setValue("quota_access", True)
        self._settings.setValue("chat_analysis", True)
        self._settings.setValue("consent_seen", True)
        self._persist_settings()
        self.quota_btn.blockSignals(True)
        self.quota_btn.setChecked(True)
        self.quota_btn.blockSignals(False)
        self.chat_btn.blockSignals(True)
        self.chat_btn.setChecked(True)
        self.chat_btn.blockSignals(False)
        _set_startup(True)
        self.boot_btn.blockSignals(True)
        self.boot_btn.setChecked(True)
        self.boot_btn.blockSignals(False)
        if self._auto_fetch and not self._for_test:
            self.timer.start()
            QTimer.singleShot(0, self.refresh)

    def _show_license_load_error(self, _err: str) -> None:
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Critical)
        box.setWindowTitle(self.t("license_title"))
        box.setText(self.t("license_missing"))
        box.addButton(QMessageBox.Ok)
        box.exec()

    def _show_license_text(self, text: str) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle(self.t("license_title"))
        dlg.resize(520, 420)
        lay = QVBoxLayout(dlg)
        body = QTextEdit()
        body.setReadOnly(True)
        body.setPlainText(text)
        lay.addWidget(body)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dlg.reject)
        buttons.accepted.connect(dlg.accept)
        close_btn = buttons.button(QDialogButtonBox.Close)
        if close_btn is not None:
            close_btn.clicked.connect(dlg.accept)
        lay.addWidget(buttons)
        dlg.exec()

    def _show_startup_dialog(self, text: str) -> bool:
        box = QMessageBox(self)
        box.setWindowTitle(self.t("license_title"))
        box.setText(self.t("license_body"))
        box.setIcon(QMessageBox.Information)
        view = box.addButton(self.t("license_view"), QMessageBox.ActionRole)
        accept = box.addButton(self.t("license_accept"), QMessageBox.AcceptRole)
        box.addButton(self.t("license_reject"), QMessageBox.RejectRole)
        box.setDefaultButton(accept)
        while True:
            box.exec()
            clicked = box.clickedButton()
            if clicked is view:
                self._show_license_text(text)
                continue
            return clicked is accept

    def _quota_changed(self, on: bool) -> None:
        self._quota_access = on
        self._settings.setValue("quota_access", on)
        if on:
            if self._auto_fetch and not self._for_test:
                self.timer.start()
            QTimer.singleShot(0, self.refresh)
        else:
            self.timer.stop()
            self.refresh()
        self._sync_live_icon(force=True)

    def _chat_changed(self, on: bool) -> None:
        self._chat_analysis = on
        self._settings.setValue("chat_analysis", on)
        if self._page == "ideas":
            if on:
                self._start_coach()
            else:
                self._coach = None
                self._fill_ideas()

    def hide_to_tray(self) -> None:
        self.setVisible(False)
        if self._pinned and (self.windowFlags() & Qt.WindowStaysOnTopHint):
            self._restore_pin_after_show = True
            flags = Qt.FramelessWindowHint | Qt.Window
            self.setWindowFlags(flags)
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.setVisible(False)
        else:
            self._restore_pin_after_show = False
        self._apply_poll_interval()
        icon = make_icon()
        self.tray.setIcon(icon)
        self.tray.show()

    def request_close(self) -> None:
        self._quitting = True
        for w in (self._worker, self._coach_worker, self._gh_worker, self._gh_loc_worker, *self._fav_workers):
            if w and w.isRunning():
                w.requestInterruption()
                w.wait(800)
        self.tray.hide()
        self.close()
        QApplication.quit()

    def show_normal(self) -> None:
        if self._restore_pin_after_show and self._pinned:
            flags = Qt.FramelessWindowHint | Qt.Window | Qt.WindowStaysOnTopHint
            self.setWindowFlags(flags)
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self._restore_pin_after_show = False
        self.setWindowState((self.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
        self.show()
        self.raise_()
        self.activateWindow()
        if sys.platform == "win32":
            try:
                import ctypes

                ctypes.windll.user32.SetForegroundWindow(int(self.winId()))
            except Exception:
                pass
        if self._auto_fetch and not self._for_test and self._quota_access:
            self._apply_poll_interval()
            if not self._snap:
                QTimer.singleShot(0, self.refresh)
        self._sync_mask()
        QTimer.singleShot(0, lambda: self._sync_nav(force=True))

    def closeEvent(self, event) -> None:  # noqa: N802
        if self._quitting:
            super().closeEvent(event)
            return
        event.ignore()
        self.hide_to_tray()

    def _tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_normal()
        elif reason == QSystemTrayIcon.Trigger:
            self.hide() if self.isVisible() else self.show_normal()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() != Qt.LeftButton:
            return
        kid = self.childAt(event.position().toPoint())
        if kid in (self.grip, self.logo_badge, self.title, self.subtitle, self.live_icon, self.stamp) or kid is None:
            self._drag = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._drag is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self._drag = None

    def refresh(self) -> None:
        if not self._quota_access:
            self.usage_summary.hide()
            self._snap = UsageSnapshot(checked_at=datetime.now().strftime("%H:%M:%S"))
            self.global_error.hide()
            while self.cards_layout.count():
                item = self.cards_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.provider_cards = []
            empty = QLabel(self.t("usage_need_quota"))
            empty.setObjectName("meterMeta")
            self.cards_layout.addWidget(empty)
            self.cards_layout.addStretch(1)
            self._sync_live_icon(force=True)
            return
        if self._worker and self._worker.isRunning():
            return
        if self.isVisible() and self._page == "usage" and not self.provider_cards:
            self._show_usage_skeleton()
        self._set_live_state("busy")
        self._worker = FetchWorker(allow_quota=True, parent=self)
        self._worker.finished_ok.connect(self._apply, Qt.ConnectionType.UniqueConnection)
        self._worker.failed.connect(self._fail, Qt.ConnectionType.UniqueConnection)
        self._worker.start()

    def _apply(self, snap: UsageSnapshot) -> None:
        try:
            self._snap = snap
            self.global_error.hide()
            items = self._ordered_providers(snap.providers)
            self._recent_drops = self._collect_drops(items)
            self._set_usage_summary(items, snap.checked_at)
            names = [p.name for p in items]
            if self.provider_cards and [c["name"] for c in self.provider_cards] == names:
                for card, provider in zip(self.provider_cards, items):
                    self._fill(card, provider)
            else:
                while self.cards_layout.count():
                    item = self.cards_layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
                self.provider_cards = []
                if not items:
                    empty = QLabel(self.t("empty"))
                    empty.setObjectName("meterMeta")
                    self.cards_layout.addWidget(empty)
                for provider in items:
                    card = self._card(provider)
                    self._fill(card, provider)
                    self.cards_layout.addWidget(card["frame"])
                    self.provider_cards.append(card)
                self.cards_layout.addStretch(1)
            ranked = sorted(
                (
                    (p, low)
                    for p in items
                    if (low := _provider_lowest(p)) is not None
                ),
                key=lambda x: x[1],
            )
            if ranked:
                worst, low = ranked[0]
                tip = self.t("tray_lowest").format(name=_display_name(worst.name), n=self._pct_num(low))
                more = [
                    f"{_display_name(p.name)} {self._pct_num(v)}%"
                    for p, v in ranked[1:4]
                ]
                if more:
                    tip = tip + "\n" + " · ".join(more)
                self.tray.setToolTip(tip)
            else:
                self.tray.setToolTip(self.t("title"))
            if self._page == "usage_detail":
                self._populate_usage_detail()
            self._set_live_state("live" if self._interval <= 5 else "idle")
        except Exception:
            self._fail("error.generic")

    def _start_coach(self) -> None:
        if not self._chat_analysis:
            self._coach = None
            self._fill_ideas()
            return
        if self._coach_worker and self._coach_worker.isRunning():
            return
        self._coach = None
        self._fill_ideas()
        self._coach_worker = CoachWorker(allow_chat=True, parent=self)
        self._coach_worker.finished_ok.connect(self._apply_coach)
        self._coach_worker.failed.connect(self._fail_coach)
        self._coach_worker.start()

    def _apply_coach(self, report: CoachReport) -> None:
        if not self._chat_analysis:
            return
        self._coach = report
        self._fill_ideas()

    def _fail_coach(self, message: str) -> None:
        self._coach = CoachReport(chats=0, chars=0, tools=0, error="error.generic")
        self._fill_ideas()

    def _fail(self, message: str) -> None:
        key = message if isinstance(message, str) and message.startswith("error.") else "error.generic"
        if not self.provider_cards:
            while self.cards_layout.count():
                item = self.cards_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.cards_layout.addStretch(1)
        self.global_error.setText(self.tx(key))
        self.global_error.show()
        self._set_live_state("err")

    def _set_live_state(self, state: str) -> None:
        if state == self._live_state and state != "busy":
            self._sync_live_icon()
            return
        self._live_state = state
        self._live_blink_on = True
        self._sync_live_icon(force=True)

    def _sync_live_icon(self, *, force: bool = False) -> None:
        if not hasattr(self, "live_icon"):
            return
        if not self._quota_access:
            self.live_icon.hide()
            self._live_pulse.stop()
            return
        self.live_icon.show()
        err = self._live_state == "err"
        kind = "live_err" if err else "live_ok"
        color = _LIVE_ERR if err else _LIVE_OK
        self.live_icon.setPixmap(_glyph(kind, color, _LIVE_GLYPH_PX))
        blink = self._live_state in ("live", "busy", "err")
        if blink:
            self._live_pulse.setInterval(700 if err else 480)
            if not self._live_pulse.isActive() or force:
                self._live_blink_on = True
                self._live_pulse.start()
            self._live_opacity.setOpacity(1.0 if self._live_blink_on else (0.28 if err else 0.22))
        else:
            self._live_pulse.stop()
            self._live_opacity.setOpacity(1.0)
        tip_key = {
            "live": "live_tip_on",
            "busy": "live_tip_busy",
            "err": "live_tip_err",
            "idle": "live_tip_idle",
        }.get(self._live_state, "live_tip_idle")
        self.live_icon.setToolTip(self.t(tip_key))

    def _pulse_live_icon(self) -> None:
        if self._live_state not in ("live", "busy", "err"):
            self._live_pulse.stop()
            self._live_opacity.setOpacity(1.0)
            return
        self._live_blink_on = not self._live_blink_on
        dim = 0.28 if self._live_state == "err" else 0.22
        self._live_opacity.setOpacity(1.0 if self._live_blink_on else dim)

    def _collect_drops(self, providers: list[ProviderUsage]) -> dict[str, float]:
        drops: dict[str, float] = {}
        for provider in providers:
            for meter in provider.meters:
                if meter.remaining_percent is None:
                    continue
                key = f"{provider.name}|{meter.label}"
                drop = _pct_drop(self._last_pcts, key, meter.remaining_percent)
                if drop is not None:
                    drops[key] = drop
        return drops

    def _fill(self, card: dict, provider: ProviderUsage) -> None:
        plan_text = self.tx(provider.plan) or ""
        card["plan"].setText(plan_text)
        card["plan"].setObjectName("planLocal" if provider.plan == "plan.local" else "plan")
        card["plan"].style().unpolish(card["plan"])
        card["plan"].style().polish(card["plan"])
        card["plan"].setVisible(bool(plan_text))
        card["pct"].clear()
        card["pct"].hide()
        card["error"].setText(self.tx(provider.error))
        card["error"].setVisible(bool(provider.error))
        meters = provider.meters
        reset_bits = [self.tx(m.reset_text) for m in meters if m.reset_text]
        reset_text = reset_bits[0] if reset_bits else ""
        card["reset"].setText(reset_text)
        card["reset"].setVisible(bool(reset_text))
        model_text = self.t("model_label").format(name=provider.model) if provider.model else ""
        card["model"].setText(model_text)
        card["model"].setVisible(bool(model_text))
        usage_text = self.tx(provider.usage_line) if provider.usage_line else ""
        card["usage"].setText(usage_text)
        card["usage"].setVisible(bool(usage_text))
        usable = [m for m in meters if m.remaining_percent is not None or m.remaining_text]
        lowest = _provider_lowest(provider)
        critical = lowest is not None and lowest < self._crit_pct
        card["frame"].setProperty("critical", critical)
        card["frame"].style().unpolish(card["frame"])
        card["frame"].style().polish(card["frame"])
        if not meters and not provider.error:
            while card["body"].count():
                item = card["body"].takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            card["rows"] = []
            empty = QLabel(self.t("no_data"))
            empty.setObjectName("meterMeta")
            card["body"].addWidget(empty)
            return
        if usable:
            primary = usable[0]
            if primary.remaining_percent is not None:
                pct_text = self._pct_left_short(primary.remaining_percent)
                tone = _tone_for(primary.remaining_percent, self._warn_pct, self._crit_pct)
                drop = self._recent_drops.get(f"{provider.name}|{primary.label}")
                if drop is not None:
                    pct_text = f"{pct_text}{self._pct_drop_text(drop)}"
            else:
                pct_text = self.tx(primary.remaining_text)
                tone = ""
            card["pct"].setText(pct_text)
            card["pct"].setProperty("tone", tone)
            card["pct"].style().unpolish(card["pct"])
            card["pct"].style().polish(card["pct"])
            card["pct"].setVisible(bool(pct_text))
        rows = card.get("rows") or []
        if rows and len(rows) == len(usable):
            for i, (row, meter) in enumerate(zip(rows, usable)):
                drop = self._recent_drops.get(f"{provider.name}|{meter.label}") if i > 0 else None
                detail = self._pct_drop_text(drop) if drop is not None else ""
                row.set_meter(meter, self.tx, self.t("left"), detail=detail, pct_fmt=self._pct_left)
            return
        while card["body"].count():
            item = card["body"].takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        card["rows"] = []
        for i, meter in enumerate(usable):
            row = MeterRow(compact=True, hide_value=(i == 0))
            drop = self._recent_drops.get(f"{provider.name}|{meter.label}") if i > 0 else None
            detail = self._pct_drop_text(drop) if drop is not None else ""
            row.set_meter(meter, self.tx, self.t("left"), detail=detail, pct_fmt=self._pct_left)
            card["body"].addWidget(row)
            card["rows"].append(row)
        detail_text = next((self.tx(m.detail) for m in meters if m.detail), "")
        if detail_text:
            det = QLabel(detail_text)
            det.setObjectName("meterMeta")
            card["body"].addWidget(det)

    def _set_usage_summary(self, items: list[ProviderUsage], checked_at: str = "") -> None:
        if not items:
            self.usage_summary.hide()
            self._refresh_hidden_row()
            return
        crit = sum(1 for p in items if self._is_provider_crit(p))
        ok = len(items) - crit
        text = self.t("usage_summary").format(crit=crit, ok=ok)
        if checked_at:
            text = f"{text} · {self.t('usage_checked').format(t=checked_at)}"
        self.usage_summary.setText(text)
        self.usage_summary.show()
        self._refresh_hidden_row()

    def _refresh_hidden_row(self) -> None:
        hidden = self._load_hidden()
        if not hidden:
            self.usage_hidden_row.hide()
            return
        bits = [
            f'<a href="{n}">{_display_name(n)} — {self.t("usage_unhide")}</a>'
            for n in hidden
        ]
        self.usage_hidden_row.setText(
            self.t("usage_hidden_hint").format(n=len(hidden)) + "<br>" + " · ".join(bits)
        )
        self.usage_hidden_row.show()

    def _show_usage_skeleton(self) -> None:
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.provider_cards = []
        self.usage_summary.hide()
        for _ in range(3):
            sk = QFrame()
            sk.setObjectName("cardSkeleton")
            self.cards_layout.addWidget(sk)
        self.cards_layout.addStretch(1)


def _ping_existing_instance() -> bool:
    sock = QLocalSocket()
    sock.connectToServer(_INSTANCE_SOCK)
    if not sock.waitForConnected(400):
        return False
    sock.write(b"raise")
    sock.flush()
    sock.waitForBytesWritten(1000)
    sock.disconnectFromServer()
    return True


def _bind_single_instance(win: UsageOverlay, server: QLocalServer) -> None:
    def _raise_existing() -> None:
        conn = server.nextPendingConnection()
        if conn is None:
            return
        conn.waitForReadyRead(300)
        conn.readAll()
        conn.disconnectFromServer()
        win.show_normal()

    server.newConnection.connect(_raise_existing)
    server.setParent(win)


def _start_single_instance_server() -> QLocalServer | None:
    QLocalServer.removeServer(_INSTANCE_SOCK)
    server = QLocalServer()
    if server.listen(_INSTANCE_SOCK):
        return server
    if _ping_existing_instance():
        return None
    QLocalServer.removeServer(_INSTANCE_SOCK)
    return server if server.listen(_INSTANCE_SOCK) else None


def main() -> int:
    ok, err = platform_ok()
    if not ok:
        show_platform_error(err)
        return 1
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        except Exception:
            pass
    app = QApplication(sys.argv)
    if _ping_existing_instance():
        return 0
    instance_server = _start_single_instance_server()
    if instance_server is None:
        return 0
    app.setQuitOnLastWindowClosed(False)
    app.setOrganizationName(SETTINGS_ORG)
    app.setApplicationName(SETTINGS_ORG)
    app.setApplicationDisplayName(APP_NAME)
    app.setWindowIcon(make_icon())
    app.setFont(QFont("Segoe UI", 10))
    win = UsageOverlay()
    if not win._license_granted:
        instance_server.close()
        return 1
    _bind_single_instance(win, instance_server)
    if STARTUP_ARG in sys.argv:
        win.hide_to_tray()
    else:
        win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
