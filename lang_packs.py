"""Pulse arayüz çevirileri — LANGS ile bire bir."""

from __future__ import annotations

from lang_packs_data import PACKS
from meter_texts import METER

REQUIRED = (
    "title", "hello", "version", "version_long", "error", "empty", "no_data",
    "refresh", "close", "hide_tray", "ideas", "usage", "settings",
    "lang_label", "theme_label", "interval_label", "pin_label", "pin_hint",
    "boot_label", "boot_hint", "quota_label", "quota_hint", "chat_label", "chat_hint",
    "consent_title", "consent_body", "consent_enable", "consent_later",
    "license_title", "license_body", "license_view", "license_accept", "license_reject",
    "license_missing",
    "usage_need_quota", "ideas_need_chat",
    "show", "quit", "tray_hide",
    "ideas_wait", "ideas_none", "ideas_prompt", "ideas_fix", "ideas_all",
    "ideas_warn", "ideas_danger", "ideas_info", "ideas_look", "loading",
    "stat_chats", "stat_tok", "stat_tools", "stat_l_chat", "stat_l_tok", "stat_l_tools",
    "left",
    "issue_paste_p", "issue_paste_f", "issue_vague_p", "issue_vague_f",
    "issue_rewrite_p", "issue_rewrite_f", "issue_split_p", "issue_split_f",
    "issue_nofile_p", "issue_nofile_f", "issue_rebuild_p", "issue_rebuild_f",
    "issue_dup_p", "issue_dup_f", "issue_helper_p", "issue_helper_f",
    "theme_night", "theme_frost", "theme_aurora", "theme_ember",
    "interval_30", "interval_60", "interval_300",
)


def validate_langs(codes: set[str]) -> None:
    for code in codes:
        assert code in TEXTS, code
        missing = set(REQUIRED) - set(TEXTS[code])
        assert not missing, (code, missing)


def _finish(pack: dict[str, str]) -> dict[str, str]:
    pack.setdefault("title", "Pulse")
    pack.setdefault("version", "v{v}")
    pack.setdefault("error", "error")
    pack.setdefault("loading", "Loading…")
    pack.setdefault("ideas_danger", "Critical")
    pack.setdefault("quota_label", TEXTS_FALLBACK_EN["quota_label"])
    pack.setdefault("quota_hint", TEXTS_FALLBACK_EN["quota_hint"])
    pack.setdefault("chat_label", TEXTS_FALLBACK_EN["chat_label"])
    pack.setdefault("chat_hint", TEXTS_FALLBACK_EN["chat_hint"])
    pack.setdefault("consent_title", TEXTS_FALLBACK_EN["consent_title"])
    pack.setdefault("consent_body", TEXTS_FALLBACK_EN["consent_body"])
    pack.setdefault("consent_enable", TEXTS_FALLBACK_EN["consent_enable"])
    pack.setdefault("consent_later", TEXTS_FALLBACK_EN["consent_later"])
    pack.setdefault("license_title", TEXTS_FALLBACK_EN["license_title"])
    pack.setdefault("license_body", TEXTS_FALLBACK_EN["license_body"])
    pack.setdefault("license_view", TEXTS_FALLBACK_EN["license_view"])
    pack.setdefault("license_accept", TEXTS_FALLBACK_EN["license_accept"])
    pack.setdefault("license_reject", TEXTS_FALLBACK_EN["license_reject"])
    pack.setdefault("license_missing", TEXTS_FALLBACK_EN["license_missing"])
    pack.setdefault("usage_need_quota", TEXTS_FALLBACK_EN["usage_need_quota"])
    pack.setdefault("ideas_need_chat", TEXTS_FALLBACK_EN["ideas_need_chat"])
    return pack


TEXTS_FALLBACK_EN = {
    "quota_label": "Quota access",
    "quota_hint": "Reads local sessions and asks only that service’s official quota API. Tokens are not stored or sent to the developer.",
    "chat_label": "Chat analysis for Ideas",
    "chat_hint": "Scans known local chat folders on this PC only. Nothing is uploaded. Documents and whole disks are not scanned.",
    "consent_title": "About quota access",
    "consent_body": (
        "TokenTakip can read local Cursor, Codex, Claude, Gemini, and GitHub Copilot session data "
        "and send it only to each service’s official quota API to show remaining usage.\n\n"
        "Tokens are not sent to the developer and are not stored by this app.\n\n"
        "While quota access is off, no session files are read and no quota requests are made. "
        "You can change this later in Settings.\n\n"
        "Ideas can analyze chat history separately; that stays off until you enable it in Settings."
    ),
    "consent_enable": "Enable quota access",
    "consent_later": "Keep disabled for now",
    "license_title": "Software license",
    "license_body": (
        "Before using TokenTakip you must review and accept the Software License Agreement. "
        "Accepting the license does not enable quota access or chat analysis. "
        "Those permissions are separate and off by default."
    ),
    "license_view": "View license text",
    "license_accept": "I accept the license",
    "license_reject": "I do not accept — exit",
    "license_missing": "License text was not found, so the application cannot start.",
    "usage_need_quota": "Quota access is off. Enable it in Settings.",
    "ideas_need_chat": "Chat analysis is off. You can enable it in Settings.",
}

TEXTS: dict[str, dict[str, str]] = {
    "tr": _finish({
        "title": "Pulse", "hello": "Hoş geldin, {name}", "version": "v{v}", "version_long": "Sürüm {v}",
        "error": "hata", "empty": "Kurulu yapay zeka yok", "no_data": "Veri yok", "refresh": "Yenile",
        "close": "Kapat", "hide_tray": "Tepsiye küçült", "ideas": "Öneriler", "usage": "Kota",
        "settings": "Ayarlar", "lang_label": "Dil",
        "theme_label": "Tema", "interval_label": "Yenileme sıklığı", "pin_label": "Üstte tut",
        "pin_hint": "Pencereyi diğer pencerelerin üstünde tutar", "boot_label": "Başlangıçta aç",
        "boot_hint": "Uygulama Windows ile birlikte açılsın",
        "quota_label": "Kota erişimi",
        "quota_hint": "Yerel oturumu okuyup yalnızca ilgili hizmetin resmî kota API’sine sorar. Token saklanmaz, geliştiriciye gitmez.",
        "chat_label": "Öneriler için sohbet analizi",
        "chat_hint": "Bilinen yerel sohbet klasörlerini yalnızca bu bilgisayarda tarar. İnternete gönderilmez. Documents veya tüm disk taranmaz.",
        "consent_title": "Kota erişimi hakkında",
        "consent_body": (
            "TokenTakip, bilgisayarınızdaki Cursor, Codex, Claude, Gemini ve GitHub Copilot oturum bilgilerini "
            "okuyarak yalnızca bu hizmetlerin resmî kota API’lerine istek atar ve kalan kullanımı gösterir.\n\n"
            "Token’lar geliştiriciye veya başka bir sunucuya gönderilmez; uygulama bunları kalıcı saklamaz.\n\n"
            "Kota erişimi kapalıyken hiçbir oturum dosyası okunmaz ve hiçbir kota isteği yapılmaz. "
            "İzni istediğiniz zaman Ayarlar’dan açıp kapatabilirsiniz.\n\n"
            "Öneriler için sohbet analizi ayrı bir izindir; varsayılan olarak kapalıdır ve yalnızca Ayarlar’dan açılır."
        ),
        "consent_enable": "Kota erişimini aç",
        "consent_later": "Şimdilik kapalı bırak",
        "license_title": "Yazılım lisansı",
        "license_body": (
            "TokenTakip’i kullanmadan önce Yazılım Kullanım Lisansı’nı inceleyip kabul etmeniz gerekir. "
            "Lisans kabulü, kota erişimini veya sohbet analizini açmaz. "
            "Bu izinler ayrıca ve varsayılan olarak kapalıdır."
        ),
        "license_view": "Lisans metnini görüntüle",
        "license_accept": "Lisansı kabul ediyorum",
        "license_reject": "Kabul etmiyorum ve çık",
        "license_missing": "Lisans metni bulunamadığı için uygulama başlatılamıyor.",
        "usage_need_quota": "Kota erişimi kapalı. Ayarlar’dan açınca kullanım bilgisi gelir.",
        "ideas_need_chat": "Sohbet analizi kapalı. Ayarlar’dan açabilirsiniz.",
        "show": "Göster", "quit": "Çık",
        "tray_hide": "Tepside. Göster için tıkla.", "ideas_wait": "Bakılıyor", "ideas_none": "Kayıt yok",
        "ideas_prompt": "Yanlış prompt", "ideas_fix": "Doğrusu", "ideas_all": "Tümü", "ideas_warn": "Uyarı",
        "ideas_info": "Bilgi", "ideas_danger": "Kritik", "ideas_look": "İncele", "loading": "Yükleniyor…",
        "stat_chats": "{n} oturum", "stat_tok": "{n} token",
        "stat_tools": "{n} araç", "stat_l_chat": "Oturum", "stat_l_tok": "Token", "stat_l_tools": "Araç",
        "left": "%{n:.0f} kaldı", "issue_paste_p": "Büyük yapıştırma token yer.",
        "issue_paste_f": "Yol ver, içeriği yapıştırma.", "issue_vague_p": "İstek belirsiz.",
        "issue_vague_f": "Dosya + hata + beklenen sonuç.", "issue_rewrite_p": "Baştan yazdırmak pahalı.",
        "issue_rewrite_f": "Tek dosya iste.", "issue_split_p": "Birden fazla iş.", "issue_split_f": "Ayır.",
        "issue_nofile_p": "Dosya yolu yok.", "issue_nofile_f": "Dosyayı yaz.",
        "issue_rebuild_p": "Her adımda exe.", "issue_rebuild_f": "Bitince bir kez derle.",
        "issue_dup_p": "Aynı prompt.", "issue_dup_f": "Sadece farkı yaz.", "issue_helper_p": "Yardımcı var.",
        "issue_helper_f": "Adını söyle: {helpers}", "theme_night": "Gece", "theme_frost": "Buz",
        "theme_aurora": "Aurora", "theme_ember": "Kor", "interval_30": "30 sn", "interval_60": "1 dk",
        "interval_300": "5 dk",
    }),
    "en": _finish({
        "title": "Pulse", "hello": "Welcome, {name}", "version": "v{v}", "version_long": "Version {v}",
        "error": "error", "empty": "No AI found", "no_data": "No data", "refresh": "Refresh", "close": "Close",
        "hide_tray": "Minimize to tray", "ideas": "Ideas", "usage": "Quota",         "settings": "Settings", "lang_label": "Language", "theme_label": "Theme",
        "interval_label": "Refresh interval", "pin_label": "Stay on top",
        "pin_hint": "Keep the window above others", "boot_label": "Open at startup",
        "boot_hint": "Start with Windows",
        "quota_label": "Quota access",
        "quota_hint": "Reads local sessions and asks only that service’s official quota API. Tokens are not stored or sent to the developer.",
        "chat_label": "Chat analysis for Ideas",
        "chat_hint": "Scans known local chat folders on this PC only. Nothing is uploaded. Documents and whole disks are not scanned.",
        "consent_title": "About quota access",
        "consent_body": (
            "TokenTakip can read local Cursor, Codex, Claude, Gemini, and GitHub Copilot session data "
            "and send it only to each service’s official quota API to show remaining usage.\n\n"
            "Tokens are not sent to the developer and are not stored by this app.\n\n"
            "While quota access is off, no session files are read and no quota requests are made. "
            "You can change this later in Settings.\n\n"
            "Ideas can analyze chat history separately; that stays off until you enable it in Settings."
        ),
        "consent_enable": "Enable quota access",
        "consent_later": "Keep disabled for now",
        "license_title": "Software license",
        "license_body": (
            "Before using TokenTakip you must review and accept the Software License Agreement. "
            "Accepting the license does not enable quota access or chat analysis. "
            "Those permissions are separate and off by default."
        ),
        "license_view": "View license text",
        "license_accept": "I accept the license",
        "license_reject": "I do not accept — exit",
        "license_missing": "License text was not found, so the application cannot start.",
        "usage_need_quota": "Quota access is off. Enable it in Settings.",
        "ideas_need_chat": "Chat analysis is off. You can enable it in Settings.",
        "show": "Show", "quit": "Quit",
        "tray_hide": "In tray. Click to show.", "ideas_wait": "Reading", "ideas_none": "No items",
        "ideas_prompt": "Weak prompt", "ideas_fix": "Better", "ideas_all": "All", "ideas_warn": "Warning",
        "ideas_info": "Info", "ideas_danger": "Critical", "ideas_look": "Inspect", "loading": "Loading…",
        "stat_chats": "{n} sessions", "stat_tok": "{n} tokens",
        "stat_tools": "{n} tools", "stat_l_chat": "Sessions", "stat_l_tok": "Tokens", "stat_l_tools": "Tools",
        "left": "{n:.0f}% left",
        "issue_paste_p": "Huge paste burns tokens.", "issue_paste_f": "Give a path.",
        "issue_vague_p": "Ask is vague.", "issue_vague_f": "File + bug + expected.",
        "issue_rewrite_p": "Rewrite-all is costly.", "issue_rewrite_f": "One file.",
        "issue_split_p": "Several jobs.", "issue_split_f": "Split.", "issue_nofile_p": "No file path.",
        "issue_nofile_f": "Name the file.", "issue_rebuild_p": "Exe every step.",
        "issue_rebuild_f": "Build once at the end.", "issue_dup_p": "Same prompt.",
        "issue_dup_f": "Send the delta.", "issue_helper_p": "A helper exists.",
        "issue_helper_f": "Name it: {helpers}", "theme_night": "Night", "theme_frost": "Frost",
        "theme_aurora": "Aurora", "theme_ember": "Ember", "interval_30": "30s", "interval_60": "1 min",
        "interval_300": "5 min",
    }),
}
for code, pack in PACKS.items():
    TEXTS[code] = _finish(pack)
for code in TEXTS:
    TEXTS[code].update(METER.get(code, METER["en"]))
