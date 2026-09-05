"""Token Tracker arayüz çevirileri — LANGS ile bire bir."""

from __future__ import annotations

import re

from lang_packs_data import PACKS
from meter_texts import METER

_PCT_N = re.compile(r"\{n:\.\d+f\}")


def _plain_pct_n(text: str) -> str:
    return _PCT_N.sub("{n}", text)


REQUIRED = (
    "title", "hello", "version", "version_long", "error", "empty", "no_data",
    "refresh", "close", "hide_tray", "ideas", "tips_nav", "usage", "settings",
    "lang_label", "theme_label", "interval_label", "pin_label", "pin_hint",
    "boot_label", "boot_hint", "quota_label", "quota_hint", "chat_label", "chat_hint",
    "consent_title", "consent_body", "consent_enable", "consent_later",
    "license_title", "license_body", "license_view", "license_accept", "license_reject",
    "license_missing",
    "usage_need_quota", "ideas_need_chat", "usage_summary", "usage_order_hint",
    "usage_order_up", "usage_order_down", "usage_crit_first", "usage_hide", "usage_hide_menu", "usage_unhide",
    "usage_hidden_hint", "usage_checked", "tray_lowest", "warn_label", "crit_label", "pct_decimals_label",
    "left_short", "model_label", "tokens_used", "tokens_used_turn", "spend_used", "spend_only",
    "show", "quit", "tray_hide",
    "ideas_wait", "ideas_none", "ideas_prompt", "ideas_fix", "ideas_all",
    "ideas_warn", "ideas_danger", "ideas_info", "ideas_look", "ideas_copied", "ideas_opened", "loading",
    "ideas_detail_title", "ideas_detail_back", "ideas_detail_problem", "ideas_detail_cause",
    "ideas_detail_solution", "ideas_detail_example", "ideas_detail_info_cause", "ideas_detail_info_solution",
    "ideas_detail_suggest", "ideas_detail_copy", "ideas_count", "ideas_clear", "ideas_filter_empty",
    "tips_title", "tips_hint", "tips_card_title", "tips_card_source", "tips_findings_title", "tips_detail_cause",
    "tip_paste_p", "tip_paste_f", "tip_vague_p", "tip_vague_f", "tip_dup_p", "tip_dup_f",
    "tip_focus_p", "tip_focus_f", "tip_rebuild_p", "tip_rebuild_f", "tip_path_p", "tip_path_f",
    "tip_session_p", "tip_session_f", "tip_mcp_p", "tip_mcp_f", "tip_skill_p", "tip_skill_f",
    "tip_baseline_p", "tip_baseline_f",
    "suggest_paste", "suggest_vague", "suggest_nofile", "suggest_rewrite", "suggest_split",
    "suggest_rebuild", "suggest_dup", "suggest_helper",
    "stat_chats", "stat_tok", "stat_tools", "stat_l_chat", "stat_l_tok", "stat_l_tools",
    "left",
    "issue_paste_p", "issue_paste_f", "issue_paste_c", "issue_vague_p", "issue_vague_f", "issue_vague_c",
    "issue_rewrite_p", "issue_rewrite_f", "issue_rewrite_c", "issue_split_p", "issue_split_f", "issue_split_c",
    "issue_nofile_p", "issue_nofile_f", "issue_nofile_c", "issue_rebuild_p", "issue_rebuild_f", "issue_rebuild_c",
    "issue_dup_p", "issue_dup_f", "issue_dup_c", "issue_helper_p", "issue_helper_f", "issue_helper_c",
    "theme_night", "theme_frost", "theme_aurora", "theme_ember",
    "interval_5", "interval_30", "interval_60", "interval_300",
    "usage_drop",
    "live_tip_on", "live_tip_busy", "live_tip_idle", "live_tip_err",
)


def validate_langs(codes: set[str]) -> None:
    for code in codes:
        assert code in TEXTS, code
        missing = set(REQUIRED) - set(TEXTS[code])
        assert not missing, (code, missing)


def _finish(pack: dict[str, str]) -> dict[str, str]:
    pack.setdefault("title", "Token Tracker")
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
    pack.setdefault("usage_summary", TEXTS_FALLBACK_EN["usage_summary"])
    pack.setdefault("usage_order_hint", TEXTS_FALLBACK_EN["usage_order_hint"])
    pack.setdefault("usage_order_up", TEXTS_FALLBACK_EN["usage_order_up"])
    pack.setdefault("usage_order_down", TEXTS_FALLBACK_EN["usage_order_down"])
    pack.setdefault("usage_crit_first", TEXTS_FALLBACK_EN["usage_crit_first"])
    pack.setdefault("usage_hide", TEXTS_FALLBACK_EN["usage_hide"])
    pack.setdefault("usage_hide_menu", TEXTS_FALLBACK_EN["usage_hide_menu"])
    pack.setdefault("usage_unhide", TEXTS_FALLBACK_EN["usage_unhide"])
    pack.setdefault("usage_hidden_hint", TEXTS_FALLBACK_EN["usage_hidden_hint"])
    pack.setdefault("usage_checked", TEXTS_FALLBACK_EN["usage_checked"])
    pack.setdefault("tray_lowest", TEXTS_FALLBACK_EN["tray_lowest"])
    pack.setdefault("warn_label", TEXTS_FALLBACK_EN["warn_label"])
    pack.setdefault("crit_label", TEXTS_FALLBACK_EN["crit_label"])
    pack.setdefault("pct_decimals_label", TEXTS_FALLBACK_EN["pct_decimals_label"])
    pack.setdefault("left_short", TEXTS_FALLBACK_EN["left_short"])
    pack.setdefault("model_label", TEXTS_FALLBACK_EN["model_label"])
    pack.setdefault("tokens_used", TEXTS_FALLBACK_EN["tokens_used"])
    pack.setdefault("tokens_used_turn", TEXTS_FALLBACK_EN["tokens_used_turn"])
    pack.setdefault("spend_used", TEXTS_FALLBACK_EN["spend_used"])
    pack.setdefault("spend_only", TEXTS_FALLBACK_EN["spend_only"])
    pack.setdefault("ideas_copied", TEXTS_FALLBACK_EN["ideas_copied"])
    pack.setdefault("ideas_opened", TEXTS_FALLBACK_EN["ideas_opened"])
    pack.setdefault("ideas_detail_title", TEXTS_FALLBACK_EN["ideas_detail_title"])
    pack.setdefault("ideas_detail_back", TEXTS_FALLBACK_EN["ideas_detail_back"])
    pack.setdefault("ideas_detail_problem", TEXTS_FALLBACK_EN["ideas_detail_problem"])
    pack.setdefault("ideas_detail_cause", TEXTS_FALLBACK_EN["ideas_detail_cause"])
    pack.setdefault("ideas_detail_solution", TEXTS_FALLBACK_EN["ideas_detail_solution"])
    pack.setdefault("ideas_detail_example", TEXTS_FALLBACK_EN["ideas_detail_example"])
    pack.setdefault("ideas_detail_info_cause", TEXTS_FALLBACK_EN["ideas_detail_info_cause"])
    pack.setdefault("ideas_detail_info_solution", TEXTS_FALLBACK_EN["ideas_detail_info_solution"])
    pack.setdefault("ideas_detail_suggest", TEXTS_FALLBACK_EN["ideas_detail_suggest"])
    pack.setdefault("ideas_detail_copy", TEXTS_FALLBACK_EN["ideas_detail_copy"])
    pack.setdefault("ideas_count", TEXTS_FALLBACK_EN["ideas_count"])
    pack.setdefault("ideas_clear", TEXTS_FALLBACK_EN["ideas_clear"])
    pack.setdefault("ideas_filter_empty", TEXTS_FALLBACK_EN["ideas_filter_empty"])
    pack.setdefault("tips_nav", TEXTS_FALLBACK_EN["tips_nav"])
    pack.setdefault("interval_5", TEXTS_FALLBACK_EN["interval_5"])
    pack.setdefault("usage_drop", TEXTS_FALLBACK_EN["usage_drop"])
    pack.setdefault("live_tip_on", TEXTS_FALLBACK_EN["live_tip_on"])
    pack.setdefault("live_tip_busy", TEXTS_FALLBACK_EN["live_tip_busy"])
    pack.setdefault("live_tip_idle", TEXTS_FALLBACK_EN["live_tip_idle"])
    pack.setdefault("live_tip_err", TEXTS_FALLBACK_EN["live_tip_err"])
    for key in (
        "tips_title", "tips_hint", "tips_card_title", "tips_card_source", "tips_findings_title", "tips_detail_cause",
        "tip_paste_p", "tip_paste_f", "tip_vague_p", "tip_vague_f", "tip_dup_p", "tip_dup_f",
        "tip_focus_p", "tip_focus_f", "tip_rebuild_p", "tip_rebuild_f", "tip_path_p", "tip_path_f",
        "tip_session_p", "tip_session_f", "tip_mcp_p", "tip_mcp_f", "tip_skill_p", "tip_skill_f",
        "tip_baseline_p", "tip_baseline_f",
    ):
        pack.setdefault(key, TEXTS_FALLBACK_EN[key])
    for stem in ("paste", "vague", "nofile", "rewrite", "split", "rebuild", "dup", "helper"):
        pack.setdefault(f"suggest_{stem}", TEXTS_FALLBACK_EN[f"suggest_{stem}"])
    for stem in (
        "paste", "vague", "rewrite", "split", "nofile", "rebuild", "dup", "helper",
    ):
        for sfx in ("p", "f", "c"):
            pack.setdefault(f"issue_{stem}_{sfx}", TEXTS_FALLBACK_EN[f"issue_{stem}_{sfx}"])
    for key in ("left", "left_short", "tray_lowest", "usage_drop"):
        if key in pack:
            pack[key] = _plain_pct_n(pack[key])
    return pack


TEXTS_FALLBACK_EN = {
    "quota_label": "Quota access",
    "quota_hint": "Reads local sessions and asks only that service’s official quota API. Tokens are not stored or sent to the developer.",
    "chat_label": "Chat analysis for Ideas",
    "chat_hint": "Scans known local chat folders on this PC only. Nothing is uploaded. Documents and whole disks are not scanned.",
    "consent_title": "Before you start",
    "consent_body": (
        "Token Tracker needs your permission to read local session and chat data on this PC.\n\n"
        "Quota: reads Cursor, Codex, Claude, Gemini, and GitHub Copilot session data and asks only "
        "each service’s official quota API. Tokens are not sent to the developer and are not stored.\n\n"
        "Ideas: scans known local chat folders on this PC only. Nothing is uploaded.\n\n"
        "You can turn these off later in Settings."
    ),
    "consent_enable": "Accept and enable",
    "consent_later": "Keep disabled for now",
    "license_title": "Before you start",
    "license_body": (
        "Before using Token Tracker, review and accept the Software License Agreement and allow "
        "local quota access and chat analysis.\n\n"
        "Quota: reads local session data and asks only each service’s official quota API. "
        "Tokens are not sent to the developer and are not stored.\n\n"
        "Ideas: scans known local chat folders on this PC only. Nothing is uploaded.\n\n"
        "You can turn these off later in Settings."
    ),
    "license_view": "View license text",
    "license_accept": "Accept and continue",
    "license_reject": "I do not accept — exit",
    "license_missing": "License text was not found, so the application cannot start.",
    "usage_need_quota": "Quota access is off. Enable it in Settings.",
    "ideas_need_chat": "Chat analysis is off. You can enable it in Settings.",
    "usage_summary": "{crit} critical · {ok} ok",
    "usage_order_hint": "Critical cards rise automatically. Drag to reorder (gap follows the pointer) · right-click to hide · tap for details.",
    "usage_order_up": "Move up",
    "usage_order_down": "Move down",
    "usage_crit_first": "Critical first",
    "usage_hide": "Hide",
    "usage_hide_menu": "Hide from list",
    "usage_unhide": "restore",
    "usage_hidden_hint": "{n} hidden — tap a name to restore",
    "usage_checked": "checked {t}",
    "tray_lowest": "{name}: {n}% left",
    "warn_label": "Warn below",
    "crit_label": "Critical below",
    "pct_decimals_label": "Percent decimals (X.YYYY)",
    "left_short": "{n}%",
    "model_label": "Model: {name}",
    "tokens_used": "Used: {used} tokens",
    "tokens_used_turn": "Used: {used} tokens · last turn {last}",
    "spend_used": "Spent: {used} · included {limit}",
    "spend_only": "Spent: {used}",
    "usage_drop": " (-{n})",
    "live_tip_on": "Live refresh on",
    "live_tip_busy": "Updating…",
    "live_tip_idle": "Waiting for next refresh",
    "live_tip_err": "Update failed",
    "ideas_copied": "Copied",
    "ideas_opened": "File opened",
    "ideas_detail_title": "Review",
    "ideas_detail_back": "Back",
    "ideas_detail_problem": "Problem",
    "ideas_detail_cause": "Why it happens",
    "ideas_detail_solution": "Solution",
    "ideas_detail_example": "Example from your chat",
    "ideas_detail_info_cause": "Detected from local chat analysis.",
    "ideas_detail_info_solution": "No action needed; this is informational.",
    "ideas_detail_suggest": "Suggested prompt",
    "ideas_detail_copy": "Copy",
    "ideas_count": "{n}×",
    "ideas_clear": "No notable issues. Scanned {chats} sessions, ~{tokens} tokens.",
    "ideas_filter_empty": "No items match this filter.",
    "tips_nav": "Cut tokens",
    "tips_title": "How to use fewer tokens",
    "tips_hint": "Ranked from your chats, installed MCP/skills, and common waste patterns. Follow these first.",
    "tips_card_title": "Token tip",
    "tips_card_source": "Saving tip",
    "tips_findings_title": "From your chats",
    "tips_detail_cause": "These habits cut repeated context and tool loops — the main token burn.",
    "tip_paste_p": "Stop pasting large files into chat.",
    "tip_paste_f": "Give a path; ask the agent to read only the needed lines.",
    "tip_vague_p": "Vague asks force long search loops.",
    "tip_vague_f": "Name file + error + expected result in one short message.",
    "tip_dup_p": "Repeating the same prompt reloads unchanged context.",
    "tip_dup_f": "Send only what changed since the last message.",
    "tip_focus_p": "Multi-job or rewrite-all prompts waste tokens.",
    "tip_focus_f": "One task per message; one file when possible.",
    "tip_rebuild_p": "Build/deploy on every step burns quota.",
    "tip_rebuild_f": "Change the code first; build once when finished.",
    "tip_path_p": "Broad Read/Grep/Shell loops showed up often.",
    "tip_path_f": "Point to the exact file; avoid repeating {tools}.",
    "tip_session_p": "A chat session grew very long.",
    "tip_session_f": "Start a fresh chat for a new task so old context is not reloaded.",
    "tip_mcp_p": "MCP “{name}” is available — call it by name.",
    "tip_mcp_f": "Write: use {name} MCP for … (skip a long manual search).",
    "tip_skill_p": "Skill “{name}” can short-circuit this work.",
    "tip_skill_f": "Write: follow the {name} skill.",
    "tip_baseline_p": "Keep prompts short and single-purpose.",
    "tip_baseline_f": "Path + one change + expected result. No full pastes, no “redo everything”.",
    "suggest_paste": "File path: `{path}` — read the relevant lines from disk; do not paste the full content.",
    "suggest_vague": "File: … — Error: … — Expected: …\n(Context: {snippet})",
    "suggest_nofile": "In `{path}`: {snippet}",
    "suggest_rewrite": "Change only `{path}`: describe one focused edit.",
    "suggest_split": "First task only: … (I will send the rest in a separate message.)",
    "suggest_rebuild": "Make the code change; run build/deploy once at the end.",
    "suggest_dup": "Since my last message, only this changed: …",
    "suggest_helper": "Use the {helper} skill: {snippet}",
    "issue_paste_p": "Huge paste burns tokens.",
    "issue_paste_f": "Give a file path; do not paste the whole content.",
    "issue_paste_c": "Large pasted text makes the model re-process every token.",
    "issue_vague_p": "The request is vague.",
    "issue_vague_f": "Name the file, the error, and the expected result.",
    "issue_vague_c": "Without file, error, or expected outcome the model guesses wrong.",
    "issue_rewrite_p": "Rewrite-all is costly.",
    "issue_rewrite_f": "Ask for one file or one focused change.",
    "issue_rewrite_c": "Broad rewrite requests touch many files at once.",
    "issue_split_p": "Several jobs in one message.",
    "issue_split_f": "Split into separate prompts.",
    "issue_split_c": "Multiple tasks in one prompt mix contexts and waste tokens.",
    "issue_nofile_p": "No file path in the request.",
    "issue_nofile_f": "Name the file or folder you mean.",
    "issue_nofile_c": "Code questions without a path force the model to search blindly.",
    "issue_rebuild_p": "Build requested at every step.",
    "issue_rebuild_f": "Build once when the work is finished.",
    "issue_rebuild_c": "Repeated build/deploy requests add slow loops to each reply.",
    "issue_dup_p": "Same prompt sent again.",
    "issue_dup_f": "Send only what changed since last time.",
    "issue_dup_c": "Repeating the same message re-processes unchanged context.",
    "issue_helper_p": "A helper skill could do this.",
    "issue_helper_f": "Name it: {helpers}",
    "issue_helper_c": "A matching skill or MCP exists but was not invoked.",
    "interval_5": "Live",
}

TEXTS: dict[str, dict[str, str]] = {
    "tr": _finish({
        "title": "Token Tracker", "hello": "Hoş geldin, {name}", "version": "v{v}", "version_long": "Sürüm {v}",
        "error": "hata", "empty": "Kurulu yapay zeka yok", "no_data": "Veri yok", "refresh": "Yenile",
        "close": "Kapat", "hide_tray": "Tepsiye küçült", "ideas": "Öneriler", "tips_nav": "Token düşürme",
        "usage": "Kota",
        "settings": "Ayarlar", "lang_label": "Dil",
        "theme_label": "Tema", "interval_label": "Yenileme sıklığı", "pin_label": "Üstte tut",
        "pin_hint": "Pencereyi diğer pencerelerin üstünde tutar", "boot_label": "Başlangıçta aç",
        "boot_hint": "Windows, macOS veya Linux başlangıç listesinde görünür",
        "quota_label": "Kota erişimi",
        "quota_hint": "Yerel oturumu okuyup yalnızca ilgili hizmetin resmî kota API’sine sorar. Token saklanmaz, geliştiriciye gitmez.",
        "chat_label": "Öneriler için sohbet analizi",
        "chat_hint": "Bilinen yerel sohbet klasörlerini yalnızca bu bilgisayarda tarar. İnternete gönderilmez. Documents veya tüm disk taranmaz.",
        "consent_title": "Başlamadan önce",
        "consent_body": (
            "Token Tracker, bu bilgisayardaki yerel oturum ve sohbet verilerini okumak için izninize ihtiyaç duyar.\n\n"
            "Kota: Cursor, Codex, Claude, Gemini ve GitHub Copilot oturumlarını okuyup yalnızca resmî kota API’lerine sorar. "
            "Token’lar geliştiriciye gitmez ve saklanmaz.\n\n"
            "Öneriler: bilinen yerel sohbet klasörlerini yalnızca bu bilgisayarda tarar. İnternete gönderilmez.\n\n"
            "Bunları istediğiniz zaman Ayarlar’dan kapatabilirsiniz."
        ),
        "consent_enable": "Kabul et ve aç",
        "consent_later": "Şimdilik kapalı bırak",
        "license_title": "Başlamadan önce",
        "license_body": (
            "Token Tracker’i kullanmadan önce Yazılım Kullanım Lisansı’nı inceleyip kabul edin; "
            "yerel kota erişimi ve sohbet analizine izin verin.\n\n"
            "Kota: yerel oturum verisini okuyup yalnızca ilgili hizmetin resmî kota API’sine sorar. "
            "Token’lar geliştiriciye gitmez ve saklanmaz.\n\n"
            "Öneriler: bilinen yerel sohbet klasörlerini yalnızca bu bilgisayarda tarar. İnternete gönderilmez.\n\n"
            "Bunları istediğiniz zaman Ayarlar’dan kapatabilirsiniz."
        ),
        "license_view": "Lisans metnini görüntüle",
        "license_accept": "Kabul et ve devam et",
        "license_reject": "Kabul etmiyorum ve çık",
        "license_missing": "Lisans metni bulunamadığı için uygulama başlatılamıyor.",
        "usage_need_quota": "Kota erişimi kapalı. Ayarlar’dan açınca kullanım bilgisi gelir.",
        "ideas_need_chat": "Sohbet analizi kapalı. Ayarlar’dan açabilirsiniz.",
        "usage_summary": "{crit} kritik · {ok} normal",
        "usage_order_hint": "Kritikler otomatik üste. Sürükle: boşluk fareyi izler · sağ tık Gizliye al · detay için tıkla.",
        "usage_order_up": "Yukarı taşı",
        "usage_order_down": "Aşağı taşı",
        "usage_crit_first": "Kritikler önce",
        "usage_hide": "Gizle",
        "usage_hide_menu": "Gizliye al",
        "usage_unhide": "geri al",
        "usage_hidden_hint": "{n} gizli — adını tıkla, geri gelsin",
        "usage_checked": "kontrol {t}",
        "tray_lowest": "{name}: %{n} kaldı",
        "warn_label": "Uyarı eşiği",
        "crit_label": "Kritik eşik",
        "pct_decimals_label": "Yüzde ondalık (X.YYYY)",
        "left_short": "%{n}",
        "model_label": "Model: {name}",
        "tokens_used": "Tüketilen: {used} token",
        "tokens_used_turn": "Tüketilen: {used} token · son tur {last}",
        "spend_used": "Harcanan: {used} · dahil {limit}",
        "spend_only": "Harcanan: {used}",
        "usage_drop": " (-{n})",
        "live_tip_on": "Canlı yenileme açık",
        "live_tip_busy": "Güncelleniyor…",
        "live_tip_idle": "Sonraki yenilemeyi bekliyor",
        "live_tip_err": "Güncelleme başarısız",
        "show": "Göster", "quit": "Çık",
        "tray_hide": "Tepside. Göster için tıkla.", "ideas_wait": "Bakılıyor", "ideas_none": "Kayıt yok",
        "ideas_prompt": "Yanlış prompt", "ideas_fix": "Doğrusu", "ideas_all": "Tümü", "ideas_warn": "Uyarı",
        "ideas_info": "Bilgi", "ideas_danger": "Kritik", "ideas_look": "İncele",
        "ideas_copied": "Kopyalandı", "ideas_opened": "Dosya açıldı",
        "ideas_detail_title": "İnceleme", "ideas_detail_back": "Geri",
        "ideas_detail_problem": "Problem", "ideas_detail_cause": "Neden oluyor",
        "ideas_detail_solution": "Çözüm", "ideas_detail_example": "Sohbetten örnek",
        "ideas_detail_info_cause": "Yerel sohbet analizinden tespit edildi.",
        "ideas_detail_info_solution": "Bilgi amaçlı; ek işlem gerekmez.",
        "ideas_detail_suggest": "Önerilen prompt", "ideas_detail_copy": "Kopyala",
        "ideas_count": "{n} kez",
        "ideas_clear": "Belirgin sorun yok. {chats} oturum, ~{tokens} token incelendi.",
        "ideas_filter_empty": "Bu filtrede kayıt yok.",
        "tips_title": "Token nasıl azaltılır",
        "tips_hint": "Sohbetlerin, kurulu MCP/skill’lerin ve sık israf kalıplarına göre sıralandı. Önce bunlara uy.",
        "tips_card_title": "Token ipucu",
        "tips_card_source": "Tasarruf ipucu",
        "tips_findings_title": "Sohbetlerinden",
        "tips_detail_cause": "Bu alışkanlıklar tekrarlayan bağlamı ve araç döngülerini keser — asıl token yakan budur.",
        "tip_paste_p": "Büyük dosyaları sohbete yapıştırma.",
        "tip_paste_f": "Yol ver; ajanın yalnız gereken satırları okumasını iste.",
        "tip_vague_p": "Belirsiz istek uzun arama döngüsü yaratır.",
        "tip_vague_f": "Dosya + hata + beklenen sonucu kısa yaz.",
        "tip_dup_p": "Aynı prompt’u tekrarlamak değişmeyen bağlamı yeniden yükler.",
        "tip_dup_f": "Son mesajdan beri yalnızca farkı yaz.",
        "tip_focus_p": "Çok iş veya baştan yazdırma token yer.",
        "tip_focus_f": "Mesaj başına bir iş; mümkünse tek dosya.",
        "tip_rebuild_p": "Her adımda derleme/deploy kota yer.",
        "tip_rebuild_f": "Önce kodu bitir; derlemeyi sonda bir kez çalıştır.",
        "tip_path_p": "Geniş Read/Grep/Shell döngüleri sık görünüyor.",
        "tip_path_f": "Tam dosya yolunu ver; {tools} tekrarından kaçın.",
        "tip_session_p": "Sohbet oturumu çok uzamış.",
        "tip_session_f": "Yeni iş için yeni sohbet aç; eski bağlam yeniden yüklenmesin.",
        "tip_mcp_p": "“{name}” MCP’n var — adıyla çağır.",
        "tip_mcp_f": "Yaz: {name} MCP ile … (uzun elle aramayı atla).",
        "tip_skill_p": "“{name}” skill’i bu işi kısaltabilir.",
        "tip_skill_f": "Yaz: {name} skill’ini takip et.",
        "tip_baseline_p": "Prompt’ları kısa ve tek amaçlı tut.",
        "tip_baseline_f": "Yol + bir değişiklik + beklenen sonuç. Tam yapıştırma ve “her şeyi yeniden yap” yok.",
        "suggest_paste": "Dosya yolu: `{path}` — ilgili satırları diskten oku, tüm içeriği yapıştırma.",
        "suggest_vague": "Dosya: … — Hata: … — Beklenen: …\n(Bağlam: {snippet})",
        "suggest_nofile": "`{path}` içinde: {snippet}",
        "suggest_rewrite": "Yalnızca `{path}` dosyasında şu değişikliği yap: …",
        "suggest_split": "İlk iş: … (devamını ayrı mesajda göndereceğim.)",
        "suggest_rebuild": "Kodu değiştir; derlemeyi en sonda bir kez çalıştır.",
        "suggest_dup": "Son mesajımdan beri yalnızca şu değişti: …",
        "suggest_helper": "{helper} skill'ini kullan: {snippet}",
        "loading": "Yükleniyor…",
        "stat_chats": "{n} oturum", "stat_tok": "{n} token",
        "stat_tools": "{n} araç", "stat_l_chat": "Oturum", "stat_l_tok": "Token", "stat_l_tools": "Araç",
        "left": "%{n} kaldı",
        "issue_paste_p": "Büyük yapıştırma token yer.",
        "issue_paste_f": "Yol ver, içeriği yapıştırma.",
        "issue_paste_c": "Uzun metin yapıştırınca model tüm içeriği yeniden işler.",
        "issue_vague_p": "İstek belirsiz.",
        "issue_vague_f": "Dosya + hata + beklenen sonuç.",
        "issue_vague_c": "Dosya, hata veya hedef yoksa model yanlış varsayım yapar.",
        "issue_rewrite_p": "Baştan yazdırmak pahalı.",
        "issue_rewrite_f": "Tek dosya veya odaklı değişiklik iste.",
        "issue_rewrite_c": "Geniş kapsamlı yeniden yazım bir seferde çok dosyayı etkiler.",
        "issue_split_p": "Birden fazla iş.",
        "issue_split_f": "Ayrı promptlara böl.",
        "issue_split_c": "Aynı mesajda birden fazla görev bağlamı karıştırır.",
        "issue_nofile_p": "Dosya yolu yok.",
        "issue_nofile_f": "Dosyayı veya klasörü adını yaz.",
        "issue_nofile_c": "Dosya adı verilmeden kod sorusu kör aramaya iter.",
        "issue_rebuild_p": "Her adımda exe.",
        "issue_rebuild_f": "Bitince bir kez derle.",
        "issue_rebuild_c": "Her küçük adımda derleme yavaş döngü ekler.",
        "issue_dup_p": "Aynı prompt.",
        "issue_dup_f": "Sadece farkı yaz.",
        "issue_dup_c": "Aynı mesajın tekrarı değişmeyen bağlamı yeniden yükler.",
        "issue_helper_p": "Yardımcı var.",
        "issue_helper_f": "Adını söyle: {helpers}",
        "issue_helper_c": "Uygun skill/MCP varken genel prompt yazılmış.",
        "theme_night": "Gece", "theme_frost": "Buz",
        "theme_aurora": "Aurora", "theme_ember": "Kor", "interval_5": "Canlı",
        "interval_30": "30 sn", "interval_60": "1 dk",
        "interval_300": "5 dk",
    }),
    "en": _finish({
        "title": "Token Tracker", "hello": "Welcome, {name}", "version": "v{v}", "version_long": "Version {v}",
        "error": "error", "empty": "No AI found", "no_data": "No data", "refresh": "Refresh", "close": "Close",
        "hide_tray": "Minimize to tray", "ideas": "Ideas", "tips_nav": "Cut tokens",
        "usage": "Quota", "settings": "Settings", "lang_label": "Language", "theme_label": "Theme",
        "interval_label": "Refresh interval", "pin_label": "Stay on top",
        "pin_hint": "Keep the window above others", "boot_label": "Open at startup",
        "boot_hint": "Shows in OS startup apps (Windows, macOS, Linux)",
        "quota_label": "Quota access",
        "quota_hint": "Reads local sessions and asks only that service’s official quota API. Tokens are not stored or sent to the developer.",
        "chat_label": "Chat analysis for Ideas",
        "chat_hint": "Scans known local chat folders on this PC only. Nothing is uploaded. Documents and whole disks are not scanned.",
        "consent_title": "Before you start",
        "consent_body": (
            "Token Tracker needs your permission to read local session and chat data on this PC.\n\n"
            "Quota: reads Cursor, Codex, Claude, Gemini, and GitHub Copilot session data and asks only "
            "each service’s official quota API. Tokens are not sent to the developer and are not stored.\n\n"
            "Ideas: scans known local chat folders on this PC only. Nothing is uploaded.\n\n"
            "You can turn these off later in Settings."
        ),
        "consent_enable": "Accept and enable",
        "consent_later": "Keep disabled for now",
        "license_title": "Before you start",
        "license_body": (
            "Before using Token Tracker, review and accept the Software License Agreement and allow "
            "local quota access and chat analysis.\n\n"
            "Quota: reads local session data and asks only each service’s official quota API. "
            "Tokens are not sent to the developer and are not stored.\n\n"
            "Ideas: scans known local chat folders on this PC only. Nothing is uploaded.\n\n"
            "You can turn these off later in Settings."
        ),
        "license_view": "View license text",
        "license_accept": "Accept and continue",
        "license_reject": "I do not accept — exit",
        "license_missing": "License text was not found, so the application cannot start.",
        "usage_need_quota": "Quota access is off. Enable it in Settings.",
        "ideas_need_chat": "Chat analysis is off. You can enable it in Settings.",
        "usage_summary": "{crit} critical · {ok} ok",
        "usage_order_hint": "Critical cards rise automatically. Drag to reorder (gap follows the pointer) · right-click to hide · tap for details.",
        "usage_order_up": "Move up",
        "usage_order_down": "Move down",
        "usage_crit_first": "Critical first",
        "usage_hide": "Hide",
        "usage_hide_menu": "Hide from list",
        "usage_unhide": "restore",
        "usage_hidden_hint": "{n} hidden — tap a name to restore",
        "usage_checked": "checked {t}",
        "tray_lowest": "{name}: {n}% left",
        "warn_label": "Warn below",
        "crit_label": "Critical below",
        "pct_decimals_label": "Percent decimals (X.YYYY)",
        "left_short": "{n}%",
        "model_label": "Model: {name}",
        "tokens_used": "Used: {used} tokens",
        "tokens_used_turn": "Used: {used} tokens · last turn {last}",
        "spend_used": "Spent: {used} · included {limit}",
        "spend_only": "Spent: {used}",
        "usage_drop": " (-{n})",
        "live_tip_on": "Live refresh on",
        "live_tip_busy": "Updating…",
        "live_tip_idle": "Waiting for next refresh",
        "live_tip_err": "Update failed",
        "show": "Show", "quit": "Quit",
        "tray_hide": "In tray. Click to show.", "ideas_wait": "Reading", "ideas_none": "No items",
        "ideas_prompt": "Weak prompt", "ideas_fix": "Better", "ideas_all": "All", "ideas_warn": "Warning",
        "ideas_info": "Info", "ideas_danger": "Critical", "ideas_look": "Inspect",
        "ideas_copied": "Copied", "ideas_opened": "File opened",
        "ideas_detail_title": "Review", "ideas_detail_back": "Back",
        "ideas_detail_problem": "Problem", "ideas_detail_cause": "Why it happens",
        "ideas_detail_solution": "Solution", "ideas_detail_example": "Example from your chat",
        "ideas_detail_info_cause": "Detected from local chat analysis.",
        "ideas_detail_info_solution": "No action needed; this is informational.",
        "ideas_detail_suggest": "Suggested prompt", "ideas_detail_copy": "Copy",
        "ideas_count": "{n}×",
        "ideas_clear": "No notable issues. Scanned {chats} sessions, ~{tokens} tokens.",
        "ideas_filter_empty": "No items match this filter.",
        "tips_title": "How to use fewer tokens",
        "tips_hint": "Ranked from your chats, installed MCP/skills, and common waste patterns. Follow these first.",
        "tips_card_title": "Token tip",
        "tips_card_source": "Saving tip",
        "tips_findings_title": "From your chats",
        "tips_detail_cause": "These habits cut repeated context and tool loops — the main token burn.",
        "tip_paste_p": "Stop pasting large files into chat.",
        "tip_paste_f": "Give a path; ask the agent to read only the needed lines.",
        "tip_vague_p": "Vague asks force long search loops.",
        "tip_vague_f": "Name file + error + expected result in one short message.",
        "tip_dup_p": "Repeating the same prompt reloads unchanged context.",
        "tip_dup_f": "Send only what changed since the last message.",
        "tip_focus_p": "Multi-job or rewrite-all prompts waste tokens.",
        "tip_focus_f": "One task per message; one file when possible.",
        "tip_rebuild_p": "Build/deploy on every step burns quota.",
        "tip_rebuild_f": "Change the code first; build once when finished.",
        "tip_path_p": "Broad Read/Grep/Shell loops showed up often.",
        "tip_path_f": "Point to the exact file; avoid repeating {tools}.",
        "tip_session_p": "A chat session grew very long.",
        "tip_session_f": "Start a fresh chat for a new task so old context is not reloaded.",
        "tip_mcp_p": "MCP “{name}” is available — call it by name.",
        "tip_mcp_f": "Write: use {name} MCP for … (skip a long manual search).",
        "tip_skill_p": "Skill “{name}” can short-circuit this work.",
        "tip_skill_f": "Write: follow the {name} skill.",
        "tip_baseline_p": "Keep prompts short and single-purpose.",
        "tip_baseline_f": "Path + one change + expected result. No full pastes, no “redo everything”.",
        "suggest_paste": "File path: `{path}` — read from disk; do not paste the full content.",
        "suggest_vague": "File: … — Error: … — Expected: …\n(Context: {snippet})",
        "suggest_nofile": "In `{path}`: {snippet}",
        "suggest_rewrite": "Change only `{path}`: one focused edit.",
        "suggest_split": "First task: … (rest in a separate message.)",
        "suggest_rebuild": "Apply the change; build once at the end.",
        "suggest_dup": "Since last message, only this changed: …",
        "suggest_helper": "Use {helper} skill: {snippet}",
        "loading": "Loading…",
        "stat_chats": "{n} sessions", "stat_tok": "{n} tokens",
        "stat_tools": "{n} tools", "stat_l_chat": "Sessions", "stat_l_tok": "Tokens", "stat_l_tools": "Tools",
        "left": "{n}% left",
        "issue_paste_p": "Huge paste burns tokens.", "issue_paste_f": "Give a path.",
        "issue_vague_p": "Ask is vague.", "issue_vague_f": "File + bug + expected.",
        "issue_rewrite_p": "Rewrite-all is costly.", "issue_rewrite_f": "One file.",
        "issue_split_p": "Several jobs.", "issue_split_f": "Split.", "issue_nofile_p": "No file path.",
        "issue_nofile_f": "Name the file.", "issue_rebuild_p": "Exe every step.",
        "issue_rebuild_f": "Build once at the end.", "issue_dup_p": "Same prompt.",
        "issue_dup_f": "Send the delta.", "issue_helper_p": "A helper exists.",
        "issue_helper_f": "Name it: {helpers}", "theme_night": "Night", "theme_frost": "Frost",
        "theme_aurora": "Aurora", "theme_ember": "Ember", "interval_5": "Live",
        "interval_30": "30s", "interval_60": "1 min",
        "interval_300": "5 min",
    }),
}
for code, pack in PACKS.items():
    TEXTS[code] = _finish(pack)
for code in TEXTS:
    TEXTS[code].update(METER.get(code, METER["en"]))
