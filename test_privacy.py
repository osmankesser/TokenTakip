"""Gizlilik / izin birim testleri — gerçek token, sohbet veya dış ağ yok."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

import prompt_coach as coach
import usage_client as usage
from overlay import UsageOverlay


def _app() -> QApplication:
    app = QApplication.instance()
    return app or QApplication([])


class PrivacyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _app()

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        QSettings.setDefaultFormat(QSettings.IniFormat)
        QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, self._tmp.name)
        s = QSettings("TokenTracker", "ui")
        s.clear()
        s.setValue("license_accepted_ver", "1")
        s.sync()

    def test_defaults(self) -> None:
        s = QSettings("TokenTracker", "ui")
        self.assertFalse(s.value("quota_access", False, type=bool))
        self.assertFalse(s.value("chat_analysis", False, type=bool))
        self.assertFalse(s.value("consent_seen", False, type=bool))
        win = UsageOverlay(auto_fetch=False, for_test=True)
        self.addCleanup(win.close)
        self.assertTrue(win._license_granted)
        self.assertFalse(win._quota_access)
        self.assertFalse(win._chat_analysis)
        s.setValue("lang", "en")
        s.setValue("theme", "frost")
        s.setValue("interval", 60)
        s2 = QSettings("TokenTracker", "ui")
        self.assertEqual(str(s2.value("lang")), "en")
        self.assertFalse(s2.value("quota_access", False, type=bool))

    def test_fetch_snapshot_off_no_io(self) -> None:
        with (
            mock.patch.object(usage, "_cursor_auth_values") as auth,
            mock.patch.object(usage, "_github_token") as gh,
            mock.patch.object(usage, "_json_get") as jg,
            mock.patch.object(usage, "_json_post") as jp,
            mock.patch.object(usage.subprocess, "run") as run,
            mock.patch.object(usage, "_PROVIDER_LOADERS", []),
        ):
            snap = usage.fetch_snapshot(allow_quota=False)
            self.assertEqual(snap.providers, [])
            auth.assert_not_called()
            gh.assert_not_called()
            jg.assert_not_called()
            jp.assert_not_called()
            run.assert_not_called()

    def test_build_report_off_no_scan(self) -> None:
        with (
            mock.patch.object(coach, "_cursor_chats") as c,
            mock.patch.object(coach, "_mcp_names") as m,
        ):
            rep = coach.build_report(allow_chat=False)
            self.assertEqual(rep.chats, 0)
            c.assert_not_called()
            m.assert_not_called()

    def test_no_documents_rglob(self) -> None:
        self.assertFalse(hasattr(coach, "_aider_chats"))
        src = Path(coach.__file__).read_text(encoding="utf-8")
        self.assertNotIn("Documents", src)
        self.assertNotIn(".rglob(", src)
        self.assertNotIn("D:/cursor", src)

    def test_path_escape_blocked(self) -> None:
        root = Path(self._tmp.name).resolve()
        outside = Path(tempfile.gettempdir()).resolve() / "tokentakip_escape_test.jsonl"
        self.assertFalse(coach._under(root, outside))

    def test_scan_limits(self) -> None:
        coach._scan_started = 0.0
        coach._scan_files = coach.CHAT_LIMIT
        coach._scan_bytes = 0
        coach._scan_stop = False
        self.assertFalse(coach._budget_ok())

    def test_safe_url_rules(self) -> None:
        with self.assertRaises(usage._SafeError) as ctx:
            usage._assert_api_url("http://api.github.com/x")
        self.assertEqual(ctx.exception.safe_code, "error.network")
        with self.assertRaises(usage._SafeError):
            usage._assert_api_url("https://evil.example/x")
        with self.assertRaises(usage._SafeError):
            usage._assert_api_url("https://api.github.com/x?access_token=SECRET")
        with self.assertRaises(usage._SafeError):
            usage._assert_api_url("https://user:pass@api.github.com/x")
        usage._assert_api_url("https://api.github.com/copilot_internal/user")

    def test_http_error_has_no_body(self) -> None:
        import io

        req = usage.urllib.request.Request("https://api.github.com/x")
        fp = io.BytesIO(b'{"token":"ghp_LEAKEDSECRET123"}')
        err = usage.urllib.error.HTTPError("https://api.github.com/x", 500, "err", {}, fp)
        with mock.patch.object(usage._API_OPENER, "open", side_effect=err):
            with self.assertRaises(usage._SafeError) as ctx:
                usage._read_json(req)
            self.assertEqual(ctx.exception.safe_code, "error.http")
            self.assertNotIn("LEAK", str(ctx.exception))

    def test_temp_db_cleaned(self) -> None:
        appdata = Path(self._tmp.name)
        cursor_db = appdata / "Cursor" / "User" / "globalStorage" / "state.vscdb"
        cursor_db.parent.mkdir(parents=True, exist_ok=True)
        cursor_db.write_bytes(b"x" * 32)
        tracked: list[Path] = []
        real_td = tempfile.TemporaryDirectory

        class TrackingTD:
            def __enter__(self_inner):
                self_inner._ctx = real_td()
                path = Path(self_inner._ctx.__enter__())
                tracked.append(path)
                return str(path)

            def __exit__(self_inner, *args):
                return self_inner._ctx.__exit__(*args)

        calls = {"n": 0}

        def kv(path, keys):
            calls["n"] += 1
            if calls["n"] == 1:
                raise usage.sqlite3.Error("locked")
            return {"cursorAuth/accessToken": "x"}

        with (
            mock.patch.object(usage.tempfile, "TemporaryDirectory", TrackingTD),
            mock.patch.object(usage, "_read_sqlite_kv", side_effect=kv),
            mock.patch.dict(usage.os.environ, {"APPDATA": str(appdata)}),
        ):
            usage._cursor_auth_values()
        self.assertTrue(tracked)
        self.assertFalse(tracked[0].exists())

    def test_no_external_icon_urls(self) -> None:
        text = Path(__file__).with_name("overlay.py").read_text(encoding="utf-8")
        self.assertNotIn("flagcdn.com", text)
        self.assertNotIn("google.com/s2/favicons", text)
        self.assertNotIn("urllib.request", text)

    def test_spec_onedir(self) -> None:
        spec = Path(__file__).with_name("TokenTracker_onedir.spec").read_text(encoding="utf-8")
        self.assertIn("exclude_binaries=True", spec)
        self.assertIn("COLLECT", spec)
        self.assertIn('name="TokenTracker"', spec)

    def test_refresh_quota_off_skips_fetch(self) -> None:
        win = UsageOverlay(auto_fetch=False, for_test=True)
        self.addCleanup(win.close)
        with mock.patch("overlay.FetchWorker") as FW:
            win.refresh()
            FW.assert_not_called()

    def test_codex_large_tail(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "rollout-2026-01-01T00-00-00-deadbeef-dead-beef-dead-beefdeadbeef.jsonl"
            user_line = json.dumps(
                {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "düzelt"}],
                    },
                }
            )
            pad_len = coach.MAX_FILE_BYTES + 1_000_000
            path.write_bytes(b"x" * pad_len + b"\n" + user_line.encode() + b"\n")
            burn, prompts = coach._parse_codex(path)
            self.assertEqual(prompts, ["düzelt"])
            self.assertEqual(burn.users, 1)

    def test_merge_findings_per_source(self) -> None:
        merged = coach._merge_findings(
            {
                "Cursor": [coach.Finding("vague", "Cursor", "a"), coach.Finding("vague", "Cursor", "b")],
                "Codex": [coach.Finding("paste", "Codex", "c")],
            },
            3,
        )
        self.assertEqual({f.source for f in merged}, {"Codex", "Cursor"})

    def test_coach_off_in_ideas(self) -> None:
        win = UsageOverlay(auto_fetch=False, for_test=True)
        self.addCleanup(win.close)
        with mock.patch("overlay.CoachWorker") as CW:
            win.goto("ideas")
            CW.assert_not_called()
            self.assertIn(win.t("ideas_need_chat"), win.ideas_layout.itemAt(0).widget().text())

    def test_copilot_unpurchased_not_percent(self) -> None:
        none = usage._copilot_meter("Premium", {"entitlement": 0, "percent_remaining": 0, "unlimited": False}, "")
        self.assertIsNone(none)
        free = usage._copilot_meter("Chat", {"entitlement": 0, "percent_remaining": 100, "unlimited": True}, "")
        self.assertEqual(free.remaining_percent, 100)
        spent = usage._copilot_meter("Premium", {"entitlement": 300, "percent_remaining": 0, "unlimited": False}, "")
        self.assertEqual(spent.remaining_percent, 0)


if __name__ == "__main__":
    unittest.main()
