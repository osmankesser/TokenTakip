"""Son kullanıcı turu — UI durumu ve gerçek veri kontrolü."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lang_packs import REQUIRED, TEXTS, validate_langs  # noqa: E402
from overlay import LANGS, THEMES, UsageOverlay  # noqa: E402
from usage_client import fetch_snapshot  # noqa: E402

FINDINGS: list[str] = []


def note(severity: str, area: str, msg: str) -> None:
    FINDINGS.append(f"[{severity}] {area}: {msg}")
    print(f"[{severity}] {area}: {msg}", flush=True)


def audit_langs() -> None:
    codes = {c for c, _ in LANGS}
    try:
        validate_langs(codes)
    except AssertionError as exc:
        note("HATA", "Dil", f"Eksik çeviri anahtarı: {exc}")
    dead_chat = {"chat", "send", "stop", "chat_ph", "target_auto", "chat_empty"}
    for code in codes:
        pack = TEXTS[code]
        orphan = dead_chat & set(pack)
        if orphan and code not in ("tr", "en"):
            note("DÜŞÜK", "Dil", f"{code} paketinde kullanılmayan sohbet anahtarları: {sorted(orphan)[:4]}…")
    for key in REQUIRED:
        if key not in TEXTS["tr"]:
            note("HATA", "Dil", f"TR eksik: {key}")


def audit_interval_i18n(win: UsageOverlay) -> None:
    win.set_lang("en")
    labels = [btn.text() for _, btn in win.interval_btns]
    if any("sn" in lb or "dk" in lb for lb in labels):
        note("ORTA", "Ayarlar", f"İngilizce seçiliyken aralık düğmeleri Türkçe: {labels}")
    win.set_lang("tr")


def audit_header_buttons(win: UsageOverlay) -> None:
    if win.tray_btn.toolTip() == win.close_btn.toolTip():
        note("ORTA", "Üst çubuk", "Tepsi ve X aynı ipucu metni")


def audit_pages(win: UsageOverlay, app: QApplication) -> None:
    if win.pages.count() != 3:
        note("HATA", "Nav", f"Beklenen 3 sayfa, bulunan {win.pages.count()}")
    for page, btn in (("usage", win.home_btn), ("ideas", win.ideas_btn), ("settings", win.settings_btn)):
        btn.click()
        app.processEvents()
        if win._page != page:
            note("HATA", "Nav", f"{page} sekmesi açılmadı")
    win.settings_title.isVisible() and note("DÜŞÜK", "Ayarlar", "settings_title gizli — başlık yok")


def audit_fetch(app: QApplication, win: UsageOverlay) -> None:
    done = {"ok": False, "err": ""}

    def on_ok(snap):
        done["ok"] = True
        n = len(snap.providers)
        errs = [f"{p.name}: {p.error}" for p in snap.providers if p.error]
        note("BİLGİ", "Kota", f"{n} sağlayıcı, {len(errs)} hata")
        for e in errs[:8]:
            note("ORTA", "Kota", e)
        empty = [p.name for p in snap.providers if not p.meters and not p.error]
        for name in empty[:6]:
            note("DÜŞÜK", "Kota", f"{name}: veri yok (meter boş)")

    def on_fail(msg):
        done["err"] = msg

    win._worker = None
    win.show()
    app.processEvents()
    win.refresh()
    for _ in range(240):
        app.processEvents()
        if win._snap is not None:
            on_ok(win._snap)
            break
        if win.global_error.isVisible():
            on_fail(win.global_error.text())
            break
    if not done["ok"] and done["err"]:
        note("HATA", "Kota", f"Yükleme hatası: {done['err']}")
    elif not done["ok"]:
        note("ORTA", "Kota", "12 sn içinde kota gelmedi (ağ veya oturum)")


def audit_ideas(app: QApplication, win: UsageOverlay) -> None:
    win.goto("ideas")
    for _ in range(80):
        app.processEvents()
        if win._coach is not None:
            break
    if win._coach and win._coach.error:
        note("ORTA", "Öneriler", f"Coach hatası kullanıcıya gösterilmiyor olabilir: {win._coach.error}")
    wait = win.t("ideas_wait")
    if win.stat_chats.num.text() == "—":
        note("BİLGİ", "Öneriler", f"Analiz bitene kadar '{wait}' gösteriliyor")


def audit_themes(win: UsageOverlay) -> None:
    for theme in THEMES:
        win.set_theme(theme)
        if f'theme="{theme}"' not in win.styleSheet():
            note("HATA", "Tema", f"{theme} stili uygulanmadı")


def main() -> int:
    audit_langs()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    win = UsageOverlay(auto_fetch=False, for_test=True)
    audit_pages(win, app)
    audit_interval_i18n(win)
    audit_header_buttons(win)
    audit_themes(win)
    audit_ideas(app, win)
    audit_fetch(app, win)
    print("\n=== ÖZET ===", flush=True)
    for sev in ("HATA", "ORTA", "DÜŞÜK", "BİLGİ"):
        items = [f for f in FINDINGS if f.startswith(f"[{sev}]")]
        if items:
            print(f"\n{sev} ({len(items)}):", flush=True)
            for it in items:
                print(f"  {it}", flush=True)
    return 1 if any(f.startswith("[HATA]") for f in FINDINGS) else 0


if __name__ == "__main__":
    raise SystemExit(main())
