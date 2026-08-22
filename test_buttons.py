"""Ana düğmeler ve sayfa geçişi."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt, QSettings
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from overlay import LANGS, TEXTS, VERSION, UsageOverlay, _fetch_flags_sync, _flag_cache_path, _flag_pix, _letter_pix, _logo_pix, _username, provider_pix  # noqa: E402


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
    QSettings("TokenTakip", "ui").setValue("license_accepted_ver", "1")

    pix = _letter_pix("CURSOR", 24)
    check("Harf simge", not pix.isNull() and pix.width() == 24)
    check("Sağlayıcı simge", not provider_pix("CURSOR", 36).isNull())
    logo = _logo_pix(64)
    check("Logo yüklendi", not logo.isNull())
    img = logo.toImage()
    check("Logo arka plan şeffaf", img.pixelColor(0, 0).alpha() == 0)
    check("Logo simge görünür", img.pixelColor(img.width() // 2, img.height() // 2).alpha() > 0)

    win = UsageOverlay(auto_fetch=False, for_test=True)
    win.show()
    app.processEvents()

    check("Pencere açıldı", win.isVisible())
    check("Hoş geldin", _username() in win.title.text() and "," in win.title.text(), win.title.text())
    check("Sürüm", VERSION == "0.1.0" and "v0.1.0" in win.subtitle.text())
    check("Pin başlangıçta açık", win._pinned and bool(win.windowFlags() & Qt.WindowStaysOnTopHint))

    win.pin_btn.click()
    app.processEvents()
    check("Pin bırakınca üstte tut kapanır", (not win._pinned) and not (win.windowFlags() & Qt.WindowStaysOnTopHint))
    win.pin_btn.click()
    app.processEvents()
    check("Pin tekrar üstte tutar", win._pinned and bool(win.windowFlags() & Qt.WindowStaysOnTopHint))

    win.ideas_btn.click()
    app.processEvents()
    check("Öneriler sayfası", win._page == "ideas")
    win.settings_btn.click()
    app.processEvents()
    check("Ayarlar sayfası", win._page == "settings")
    check("21 dil seçeneği", len(LANGS) == 21 and win.lang_combo.count() == 21)
    check("Dil paketi es", TEXTS["es"]["settings"] == "Ajustes")
    _fetch_flags_sync(["tr", "en", "de"])
    win._refresh_lang_flag_icons()
    tr_pix = _flag_pix("tr")
    letter = _letter_pix("TR", 24)
    check("Bayrak png", _flag_cache_path("tr").is_file())
    check("Bayrak harf değil", tr_pix.toImage().pixel(0, 0) != letter.toImage().pixel(0, 0))
    win.set_lang("en")
    check("Dil değiştir", win._lang == "en" and win.lang_combo.currentData() == "en")
    check("Arayüz İngilizce", win.settings_btn.text.text() == "Settings")
    check("Kota metni EN", win.tx("detail.local_no_internet") == "Local model, no internet quota")
    check("Kota etiket EN", win.tx("meter.total") == "Total")
    check("Yerel plan EN", win.tx("plan.local") == "Local")
    from overlay import _glyph
    from PySide6.QtGui import QColor
    check("Tepsi simgesi", not _glyph("tray_token", QColor("#334155"), 20).isNull())
    check("X simgesi net", not _glyph("close", QColor("#334155"), 20, 1.0).isNull())
    win.set_lang("es")
    check("Arayüz İspanyolca", win.t("usage") == "Cuota")
    win.set_lang("tr")
    win.set_lang("tr")
    win.theme_btns[1].click()
    app.processEvents()
    check("Tema frost", win._theme == "frost")
    check("Tema stil uygulanır", '[theme="frost"]' in win.styleSheet())
    win.set_theme("night")
    check("Tema gece", win.panel.property("theme") == "night")
    check("Gece hoş geldin görünür", "#f8fafc".lower() in win.title.styleSheet().lower())
    win.set_theme("frost")
    win.home_btn.click()
    app.processEvents()
    check("Ana sayfa kota", win._page == "usage")

    win.stamp.setText("eski")
    win._quota_access = True
    from unittest import mock

    with mock.patch("overlay.FetchWorker") as FW:
        worker = mock.Mock()
        worker.isRunning.return_value = False
        FW.return_value = worker
        win.tray_refresh_action.trigger()
        app.processEvents()
        check("Yenile damgayı bozmaz", win.stamp.text() == "eski")
        check("Yenile işi başlar", FW.called and win._worker is worker)

    win.close_btn.click()
    app.processEvents()
    check("X düğmesi tepsiye küçültür", not win.isVisible())
    win.show_action.trigger()
    app.processEvents()
    check("Tepsi Göster geri açar", win.isVisible())

    win.tray_btn.click()
    app.processEvents()
    check("Tepsi düğmesi küçültür", not win.isVisible())
    win.show_action.trigger()
    app.processEvents()
    check("Tepsiden geri açılır", win.isVisible())

    if win._worker and win._worker.isRunning():
        win._worker.wait(4000)

    closed = {"ok": False}
    app.aboutToQuit.connect(lambda: closed.__setitem__("ok", True))
    win.quit_action.trigger()
    app.processEvents()
    check("Çık uygulamayı durdurur", closed["ok"] or not win.isVisible())
    print("TUM DUGMELER CALISIYOR", flush=True)
    os._exit(0)


if __name__ == "__main__":
    raise SystemExit(main())
