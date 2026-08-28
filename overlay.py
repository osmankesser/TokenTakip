"""PC kota penceresi. Görsel: açık panel, üç sayfa, simgeler kodla."""

from __future__ import annotations

import os
import shutil
import sys
import winreg
from collections import Counter, deque
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Literal

from math import cos, pi, sin

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
    Signal,
)
from PySide6.QtGui import (
    QAction,
    QColor,
    QFont,
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
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
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
}
_ICON_MEM: dict[str, QPixmap] = {}
_LOGO_CUT: QPixmap | None = None
_LOGO_TRIM: QPixmap | None = None
_LOGO_HEADER_PX = 40
_PROVIDER_ICON_PX = 32
_PROVIDER_MARK_PX = 40
_NAV_GLYPH_PX = 24
_NAV_ICON_CACHE: dict[tuple[str, str], QPixmap] = {}
_ACTION_GLYPH_PX = 20
_STAT_GLYPH_PX = 22
_IDEA_GLYPH_PX = 26
_FLUENT = {
    "kota": 0xE9D2,
    "ideas": 0xEA80,
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
    root = Path(os.environ.get("LOCALAPPDATA", str(ROOT))) / "TokenTracker" / "cache"
    root.mkdir(parents=True, exist_ok=True)
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


def _exe_for(name: str) -> Path | None:
    key = name.upper()
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs"
    roaming = Path(os.environ.get("APPDATA", ""))
    pf = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
    hits = {
        "CURSOR": [local / "cursor" / "Cursor.exe", local / "Cursor" / "Cursor.exe"],
        "OLLAMA": [local / "Ollama" / "Ollama.exe", pf / "Ollama" / "Ollama.exe"],
        "CHATGPT": [local / "ChatGPT" / "ChatGPT.exe", pf / "ChatGPT" / "ChatGPT.exe"],
        "CLAUDE": [local / "Claude" / "Claude.exe", pf / "Claude" / "Claude.exe"],
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
    if name.upper() == "COPILOT":
        pix = _copilot_pix(size)
        _ICON_MEM[key] = pix
        return pix
    exe = _exe_for(name)
    pix = _pix_from_exe(exe, size) if exe else None
    if pix is None:
        pix = _pix_from_cache(name, size)
    if pix is None:
        pix = _letter_pix(name, size)
    _ICON_MEM[key] = pix
    return pix


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
        pix = _font_pix(chr(cp), color, size, ("Segoe Fluent Icons", "Segoe MDL2 Assets"), 0.78)
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


def _display_name(name: str) -> str:
    m = {"CHATGPT": "ChatGPT", "CODEX": "Codex", "CURSOR": "Cursor", "OLLAMA": "Ollama", "LM STUDIO": "LM Studio"}
    return m.get(name.upper(), name.title())


def _idea_kind(code: str) -> str:
    if code in ("paste", "rebuild"):
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
QFrame#navBar {{ border-top: 1px solid {p["line"]}; }}
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
QLabel#navIcon[active="true"] {{ background: {p["accent_soft"]}; }}
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
QLabel#loadingLabel {{ color: {p["muted"]}; font-size: 11px; }}
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
    background: transparent; border: none; border-top: 1px solid #eef2f6;
}
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
QLabel#loadingLabel { color: #64748b; font-size: 11px; font-weight: 600; padding: 8px; }
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


class _CardClickFilter(QObject):
    def __init__(self, overlay: "UsageOverlay", name: str):
        super().__init__(overlay)
        self._overlay = overlay
        self._name = name

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
            child = obj.childAt(pos)
            while child is not None and child is not obj:
                if isinstance(child, QPushButton):
                    return False
                child = child.parentWidget()
            self._overlay._open_usage_detail(self._name)
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

    def set_meter(self, meter: Meter, translate, left_fmt: str, detail: str = "") -> None:
        self.name.setText(translate(meter.label))
        if meter.remaining_percent is not None:
            self.value.setText(left_fmt.format(n=meter.remaining_percent))
        else:
            self.value.setText(translate(meter.remaining_text) or "—")
        self.bar.set_remaining(meter.remaining_percent)
        bits = [translate(bit) for bit in (meter.reset_text, meter.detail) if bit]
        if detail:
            bits.insert(0, detail)
        self.meta.setText(" · ".join(bits))
        self.meta.setVisible(bool(bits) and not self._compact)



class NavTab(QWidget):
    def __init__(self, overlay: "UsageOverlay", kind: str, page: str, parent=None):
        super().__init__(parent)
        self._overlay = overlay
        self.setObjectName("navTab")
        self.setAccessibleName(page + "Btn")
        self.setCursor(Qt.PointingHandCursor)
        self._kind, self._page = kind, page
        lay = QVBoxLayout(self)
        lay.setContentsMargins(2, 4, 2, 2)
        lay.setSpacing(2)
        self.icon = QLabel()
        self.icon.setObjectName("navIcon")
        self.icon.setFixedSize(50, 34)
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setScaledContents(False)
        self.text = QLabel()
        self.text.setObjectName("navText")
        self.text.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.icon, 0, Qt.AlignHCenter)
        lay.addWidget(self.text)
        self._active = None

    def set_text(self, label: str) -> None:
        self.text.setText(label)

    def set_active(self, on: bool, *, force: bool = False) -> None:
        if not force and self._active is on:
            return
        self._active = on
        self.icon.setProperty("active", on)
        self.text.setProperty("active", on)
        color = self._overlay.theme_accent() if on else self._overlay.theme_muted()
        key = (self._kind, color.name())
        pix = _NAV_ICON_CACHE.get(key)
        if pix is None:
            pix = _glyph(self._kind, color, _NAV_GLYPH_PX)
            _NAV_ICON_CACHE[key] = pix
        self.icon.setPixmap(pix)
        for w in (self.icon, self.text):
            w.style().unpolish(w)
            w.style().polish(w)

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
            if self._interval not in (30, 60, 300):
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
        self._snap: UsageSnapshot | None = None
        self._coach: CoachReport | None = None
        self._coach_worker = None
        self._page = "usage"
        self._detail_provider: str | None = None
        self._idea_filter = "all"
        self._idea_source_filter = "all"
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
        self.subtitle = QLabel()
        self.subtitle.setObjectName("versionLabel")
        titles.addWidget(self.title)
        titles.addWidget(self.subtitle)
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
        self.loading_label = QLabel()
        self.loading_label.setObjectName("loadingLabel")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        usage_l.addWidget(self.loading_label)
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

        detail_page = QWidget()
        detail_l = QVBoxLayout(detail_page)
        detail_l.setContentsMargins(0, 0, 0, 0)
        detail_l.setSpacing(8)
        detail_head = QHBoxLayout()
        self.detail_back = QPushButton(self.t("ideas_detail_back"))
        self.detail_back.setObjectName("lookBtn")
        self.detail_back.setCursor(Qt.PointingHandCursor)
        self.detail_back.clicked.connect(lambda: self.goto("ideas"))
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
        self.ud_back.clicked.connect(lambda: self.goto("usage"))
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
        for sec, label in ((30, "30 sn"), (60, "1 dk"), (300, "5 dk")):
            btn = QPushButton(label)
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

        nav_bar = QFrame()
        nav_bar.setObjectName("navBar")
        nav = QHBoxLayout(nav_bar)
        nav.setContentsMargins(0, 8, 0, 2)
        nav.setSpacing(4)
        self.home_btn = self._nav("kota", "usage")
        self.ideas_btn = self._nav("ideas", "ideas")
        self.settings_btn = self._nav("settings", "settings")
        for b in (self.home_btn, self.ideas_btn, self.settings_btn):
            nav.addWidget(b, 1)
        root.addWidget(nav_bar)
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
        self.timer.setInterval(self._interval * 1000)
        self.timer.timeout.connect(self.refresh)
        self.clock = QTimer(self)
        self.clock.setInterval(5000)
        self.clock.timeout.connect(self._tick)
        self.setStyleSheet(STYLE)
        self.panel.setStyleSheet(_theme_css(self._theme))
        self._sync_theme_surfaces()
        self._apply_language()
        self._tick()
        self._license_granted = self._gate_license()
        if not self._license_granted:
            self._quitting = True
            self._place()
            return
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

    def tx(self, text: str) -> str:
        if not text or text == "—":
            return text
        if "|" in text:
            key, *args = text.split("|")
            tmpl = self.t(key)
            if key == "left":
                return tmpl.format(n=float(args[0]))
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
        self.home_btn.set_text(self.t("usage"))
        self.ideas_btn.set_text(self.t("ideas"))
        self.settings_btn.set_text(self.t("settings"))
        self.settings_title.setText(self.t("settings"))
        self.lang_label.setText(self.t("lang_label"))
        self.theme_label.setText(self.t("theme_label"))
        self.interval_label.setText(self.t("interval_label"))
        self.warn_label.setText(self.t("warn_label"))
        self.crit_label.setText(self.t("crit_label"))
        self.pin_label.setText(self.t("pin_label"))
        self.pin_hint.setText(self.t("pin_hint"))
        self.boot_label.setText(self.t("boot_label"))
        self.boot_hint.setText(self.t("boot_hint"))
        self.quota_label.setText(self.t("quota_label"))
        self.quota_hint.setText(self.t("quota_hint"))
        self.chat_label.setText(self.t("chat_label"))
        self.chat_hint.setText(self.t("chat_hint"))
        self.version_label.setText(self.t("version_long").format(v=VERSION))
        self.loading_label.setText(self.t("loading"))
        self.usage_order_hint.setText(self.t("usage_order_hint"))
        self.ud_back.setText(self.t("ideas_detail_back"))
        self.ud_hide.setText(self.t("usage_hide"))
        for card in getattr(self, "provider_cards", ()):
            btns = getattr(card["frame"], "_order_btns", ())
            if len(btns) == 2:
                btns[0].setToolTip(self.t("usage_order_up"))
                btns[1].setToolTip(self.t("usage_order_down"))
        self._refresh_hidden_row()
        if self._page == "usage_detail":
            self._populate_usage_detail()
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
        pairs = (
            (self.home_btn, "usage"),
            (self.ideas_btn, "ideas"),
            (self.settings_btn, "settings"),
        )
        for btn, page in pairs:
            btn.set_active(
                self._page == page
                or (page == "ideas" and self._page == "idea_detail")
                or (page == "usage" and self._page == "usage_detail"),
                force=True,
            )
        for name, btn in self.theme_btns:
            btn.setText(self.t(f"theme_{name}"))
        interval_keys = {30: "interval_30", 60: "interval_60", 300: "interval_300"}
        for sec, btn in self.interval_btns:
            btn.setText(self.t(interval_keys[sec]))
        for pct, btn in self.warn_btns:
            btn.setText(f"%{pct}")
        for pct, btn in self.crit_btns:
            btn.setText(f"%{pct}")
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

    def _sync_nav(self, *, force: bool = False) -> None:
        if force:
            _NAV_ICON_CACHE.clear()
        for btn, page in (
            (self.home_btn, "usage"),
            (self.ideas_btn, "ideas"),
            (self.settings_btn, "settings"),
        ):
            btn.set_active(
                self._page == page
                or (page == "ideas" and self._page == "idea_detail")
                or (page == "usage" and self._page == "usage_detail"),
                force=force,
            )

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
        order_col = QVBoxLayout()
        order_col.setContentsMargins(0, 0, 0, 0)
        order_col.setSpacing(0)
        up = QPushButton("↑")
        down = QPushButton("↓")
        for btn in (up, down):
            btn.setObjectName("orderBtn")
            btn.setFixedSize(26, 22)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFocusPolicy(Qt.NoFocus)
        up.setToolTip(self.t("usage_order_up"))
        down.setToolTip(self.t("usage_order_down"))
        up.clicked.connect(lambda _, n=provider.name: self._move_provider(n, -1))
        down.clicked.connect(lambda _, n=provider.name: self._move_provider(n, 1))
        order_col.addWidget(up)
        order_col.addWidget(down)
        frame._order_btns = (up, down)
        top.addWidget(mark_wrap)
        top.addLayout(mid, 1)
        top.addLayout(order_col, 0)
        layout.addLayout(top)
        body = QVBoxLayout()
        body.setSpacing(6)
        layout.addLayout(body)
        error = QLabel()
        error.setObjectName("error")
        error.setWordWrap(True)
        error.hide()
        layout.addWidget(error)
        frame.installEventFilter(_CardClickFilter(self, provider.name))
        self._want_favicon(provider.name, mark)
        return {
            "name": provider.name,
            "frame": frame,
            "plan": plan,
            "pct": pct,
            "reset": reset,
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
        by_name = {p.name: p for p in self._snap.providers}
        names = [c["name"] for c in self.provider_cards]
        try:
            idx = names.index(name)
        except ValueError:
            return
        j = idx + delta
        if j < 0 or j >= len(names):
            return
        a, b = by_name.get(names[idx]), by_name.get(names[j])
        if not a or not b or self._is_provider_crit(a) != self._is_provider_crit(b):
            return
        names[idx], names[j] = names[j], names[idx]
        self._save_provider_order(names + self._load_hidden())
        self._apply(self._snap)

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

    def _open_usage_detail(self, name: str) -> None:
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
        if not provider:
            self.ud_title.setText(self.t("no_data"))
            self.ud_plan.hide()
            self.ud_reset.hide()
            self.ud_error.hide()
            return
        self.ud_title.setText(_display_name(provider.name))
        plan_text = self.tx(provider.plan) or ""
        self.ud_plan.setText(plan_text)
        self.ud_plan.setVisible(bool(plan_text))
        resets = [self.tx(m.reset_text) for m in provider.meters if m.reset_text]
        self.ud_reset.setText(resets[0] if resets else "")
        self.ud_reset.setVisible(bool(resets))
        self.ud_error.setText(self.tx(provider.error))
        self.ud_error.setVisible(bool(provider.error))
        usable = [m for m in provider.meters if m.remaining_percent is not None or m.remaining_text]
        for meter in usable:
            row = MeterRow(compact=False)
            row.set_meter(meter, self.tx, self.t("left"))
            self.ud_body.addWidget(row)
        if not usable and not provider.error:
            empty = QLabel(self.t("no_data"))
            empty.setObjectName("meterMeta")
            self.ud_body.addWidget(empty)
        self.ud_body.addStretch(1)

    def _want_favicon(self, name: str, mark: QLabel) -> None:
        domain = DOMAINS.get(name.upper())
        if not domain or _pix_from_cache(name, _PROVIDER_ICON_PX):
            return
        exe = _exe_for(name)
        if exe and (pix := _pix_from_exe(exe, _PROVIDER_ICON_PX)):
            mark.setPixmap(pix)
            return

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
            if report.findings:
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
        if code in ("mcp", "skill"):
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
        title = QLabel(self.t("ideas_prompt"))
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
        QTimer.singleShot(0, self._fit_to_content)

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

    def goto(self, page: str) -> None:
        self._page = page
        self._show_page()
        if page == "ideas":
            if self._chat_analysis:
                self._start_coach()
            else:
                self._coach = None
                self._fill_ideas()
        elif page == "usage_detail":
            self._populate_usage_detail()

    def _show_page(self) -> None:
        self.pages.setCurrentIndex(
            {"usage": 0, "ideas": 1, "idea_detail": 2, "usage_detail": 3, "settings": 4}[self._page]
        )
        self._sync_nav()

    def toggle_page(self) -> None:
        self.goto("ideas" if self._page != "ideas" else "usage")

    def open_settings(self) -> None:
        self.goto("settings")

    def set_interval(self, seconds: int) -> None:
        self._interval = seconds
        self._settings.setValue("interval", seconds)
        self.timer.setInterval(seconds * 1000)
        self._apply_language()

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
        icon = make_icon()
        self.tray.setIcon(icon)
        self.tray.show()

    def request_close(self) -> None:
        self._quitting = True
        for w in (self._worker, self._coach_worker, *self._fav_workers):
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
        self.show()
        self.raise_()
        self.activateWindow()
        if self._auto_fetch and not self._for_test and self._quota_access:
            self.timer.start()
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
        if kid in (self.grip, self.logo_badge, self.title, self.subtitle, self.stamp) or kid is None:
            self._drag = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._drag is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self._drag = None

    def refresh(self) -> None:
        if not self._quota_access:
            self.loading_label.hide()
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
            return
        if self._worker and self._worker.isRunning():
            return
        if self.isVisible() and self._page == "usage":
            self.loading_label.setText(self.t("loading"))
            self.loading_label.show()
            self._show_usage_skeleton()
        self._worker = FetchWorker(allow_quota=True, parent=self)
        self._worker.finished_ok.connect(self._apply, Qt.ConnectionType.UniqueConnection)
        self._worker.failed.connect(self._fail, Qt.ConnectionType.UniqueConnection)
        self._worker.start()

    def _apply(self, snap: UsageSnapshot) -> None:
        try:
            self.loading_label.hide()
            self._snap = snap
            self.global_error.hide()
            items = self._ordered_providers(snap.providers)
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
                tip = self.t("tray_lowest").format(name=_display_name(worst.name), n=low)
                more = [
                    f"{_display_name(p.name)} {v:.0f}%"
                    for p, v in ranked[1:4]
                ]
                if more:
                    tip = tip + "\n" + " · ".join(more)
                self.tray.setToolTip(tip)
            else:
                self.tray.setToolTip(self.t("title"))
            if self._page == "usage_detail":
                self._populate_usage_detail()
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
        self.loading_label.hide()
        key = message if isinstance(message, str) and message.startswith("error.") else "error.generic"
        self.global_error.setText(self.tx(key))
        self.global_error.show()

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
        while card["body"].count():
            item = card["body"].takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        card["rows"] = []
        usable = [m for m in meters if m.remaining_percent is not None or m.remaining_text]
        lowest = _provider_lowest(provider)
        critical = lowest is not None and lowest < self._crit_pct
        card["frame"].setProperty("critical", critical)
        card["frame"].style().unpolish(card["frame"])
        card["frame"].style().polish(card["frame"])
        if not meters and not provider.error:
            empty = QLabel(self.t("no_data"))
            empty.setObjectName("meterMeta")
            card["body"].addWidget(empty)
            return
        if usable:
            primary = usable[0]
            if primary.remaining_percent is not None:
                pct_text = self.t("left_short").format(n=primary.remaining_percent)
                tone = _tone_for(primary.remaining_percent, self._warn_pct, self._crit_pct)
            else:
                pct_text = self.tx(primary.remaining_text)
                tone = ""
            card["pct"].setText(pct_text)
            card["pct"].setProperty("tone", tone)
            card["pct"].style().unpolish(card["pct"])
            card["pct"].style().polish(card["pct"])
            card["pct"].setVisible(bool(pct_text))
        for i, meter in enumerate(usable):
            row = MeterRow(compact=True, hide_value=(i == 0))
            row.set_meter(meter, self.tx, self.t("left"))
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
            self.t("usage_hidden_hint").format(n=len(hidden)) + " · " + " · ".join(bits)
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


def _startup_cmd() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    pyw = Path(sys.executable).with_name("pythonw.exe")
    py = pyw if pyw.exists() else Path(sys.executable)
    return f'"{py}" "{ROOT / "overlay.py"}"'


def _startup_on() -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY)
        for name in (RUN_NAME, _RUN_LEGACY, "TokenTakip"):
            try:
                winreg.QueryValueEx(key, name)
                return True
            except OSError:
                continue
    except OSError:
        pass
    return False


def _set_startup(on: bool) -> None:
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY)
    if on:
        winreg.SetValueEx(key, RUN_NAME, 0, winreg.REG_SZ, _startup_cmd())
        try:
            winreg.DeleteValue(key, _RUN_LEGACY)
        except FileNotFoundError:
            pass
    else:
        for name in (RUN_NAME, _RUN_LEGACY, "TokenTakip"):
            try:
                winreg.DeleteValue(key, name)
            except FileNotFoundError:
                pass


def main() -> int:
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        except Exception:
            pass
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setOrganizationName(SETTINGS_ORG)
    app.setApplicationName(SETTINGS_ORG)
    app.setApplicationDisplayName(APP_NAME)
    app.setWindowIcon(make_icon())
    app.setFont(QFont("Segoe UI", 10))
    win = UsageOverlay()
    if not win._license_granted:
        return 1
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
