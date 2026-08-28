"""Lisans kabul kapısı — gerçek token, sohbet veya dış ağ yok."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

import usage_client as usage
from overlay import LICENSE_DOC_VER, UsageOverlay, read_license_text


def _app() -> QApplication:
    app = QApplication.instance()
    return app or QApplication([])


class LicenseGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _app()

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self._root = Path(self._tmp.name)
        QSettings.setDefaultFormat(QSettings.IniFormat)
        QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, self._tmp.name)
        self._settings = QSettings("TokenTracker", "ui")
        self._settings.clear()
        self._settings.sync()

    def _lic(self, body: str = "Token Tracker test license body.\n") -> Path:
        path = self._root / "LISANS-SOZLESMESI.txt"
        path.write_text(body, encoding="utf-8")
        return path

    def test_needs_prompt_when_missing_ver(self) -> None:
        path = self._lic()
        prompts: list[str] = []

        def prompt(text: str) -> bool:
            prompts.append(text)
            return True

        win = UsageOverlay(auto_fetch=False, for_test=True, license_path=path, license_prompt=prompt)
        self.addCleanup(win.close)
        self.assertTrue(win._license_granted)
        self.assertEqual(len(prompts), 1)

    def test_skips_prompt_when_current_ver(self) -> None:
        path = self._lic()
        self._settings.setValue("license_accepted_ver", LICENSE_DOC_VER)
        prompt = mock.Mock(return_value=True)
        win = UsageOverlay(auto_fetch=False, for_test=True, license_path=path, license_prompt=prompt)
        self.addCleanup(win.close)
        self.assertTrue(win._license_granted)
        prompt.assert_not_called()

    def test_old_ver_skips_prompt(self) -> None:
        path = self._lic()
        self._settings.setValue("license_accepted_ver", "0")
        self._settings.sync()
        prompt = mock.Mock(return_value=True)
        win = UsageOverlay(auto_fetch=False, for_test=True, license_path=path, license_prompt=prompt)
        self.addCleanup(win.close)
        self.assertTrue(win._license_granted)
        prompt.assert_not_called()

    def test_license_accept_flag_skips_prompt(self) -> None:
        path = self._lic()
        self._settings.setValue("license_accepted", True)
        self._settings.sync()
        prompt = mock.Mock(return_value=True)
        win = UsageOverlay(auto_fetch=False, for_test=True, license_path=path, license_prompt=prompt)
        self.addCleanup(win.close)
        self.assertTrue(win._license_granted)
        prompt.assert_not_called()

    def test_accept_grants_license_and_features(self) -> None:
        path = self._lic()
        win = UsageOverlay(
            auto_fetch=False,
            for_test=True,
            license_path=path,
            license_prompt=lambda _t: True,
        )
        self.addCleanup(win.close)
        self.assertEqual(self._settings.value("license_accepted_ver"), LICENSE_DOC_VER)
        self.assertTrue(self._settings.value("license_accepted", False, type=bool))
        self.assertTrue(self._settings.value("quota_access", False, type=bool))
        self.assertTrue(self._settings.value("chat_analysis", False, type=bool))
        self.assertTrue(self._settings.value("consent_seen", False, type=bool))
        self.assertTrue(win._quota_access)
        self.assertTrue(win._chat_analysis)

    def test_reject_no_io_and_no_permission_write(self) -> None:
        path = self._lic()
        with (
            mock.patch.object(usage, "fetch_snapshot") as fetch,
            mock.patch("overlay.build_report") as report,
            mock.patch("overlay.FetchWorker") as FW,
            mock.patch("overlay.CoachWorker") as CW,
            mock.patch.object(usage.subprocess, "run") as run,
        ):
            win = UsageOverlay(
                auto_fetch=True,
                for_test=True,
                license_path=path,
                license_prompt=lambda _t: False,
            )
            self.addCleanup(win.close)
            self.assertFalse(win._license_granted)
            win.refresh()
            win.goto("ideas")
            fetch.assert_not_called()
            report.assert_not_called()
            FW.assert_not_called()
            CW.assert_not_called()
            run.assert_not_called()
        self.assertFalse(bool(self._settings.value("license_accepted_ver", "")))
        self.assertFalse(self._settings.value("quota_access", False, type=bool))
        self.assertFalse(self._settings.value("chat_analysis", False, type=bool))
        self.assertFalse(self._settings.value("consent_seen", False, type=bool))

    def test_close_same_as_reject(self) -> None:
        path = self._lic()
        text = path.read_text(encoding="utf-8")
        with mock.patch.object(UsageOverlay, "_show_startup_dialog", return_value=False) as dlg:
            win = UsageOverlay(auto_fetch=False, for_test=True, license_path=path)
            self.addCleanup(win.close)
            self.assertFalse(win._license_granted)
            dlg.assert_called_once_with(text)
        self.assertFalse(bool(self._settings.value("license_accepted_ver", "")))

    def test_missing_file_blocks_accept(self) -> None:
        missing = self._root / "no_license.txt"
        with mock.patch.object(UsageOverlay, "_show_license_load_error") as err:
            prompt = mock.Mock(return_value=True)
            win = UsageOverlay(
                auto_fetch=False,
                for_test=True,
                license_path=missing,
                license_prompt=prompt,
            )
            self.addCleanup(win.close)
            self.assertFalse(win._license_granted)
            err.assert_called_once()
            prompt.assert_not_called()
        self.assertFalse(bool(self._settings.value("license_accepted_ver", "")))

    def test_empty_file_not_acceptable(self) -> None:
        path = self._lic("   \n  ")
        text, err = read_license_text(path)
        self.assertIsNone(text)
        self.assertEqual(err, "empty")
        with mock.patch.object(UsageOverlay, "_show_license_load_error") as show_err:
            prompt = mock.Mock(return_value=True)
            win = UsageOverlay(
                auto_fetch=False,
                for_test=True,
                license_path=path,
                license_prompt=prompt,
            )
            self.addCleanup(win.close)
            self.assertFalse(win._license_granted)
            show_err.assert_called_once()
            prompt.assert_not_called()

    def test_unreadable_shows_safe_error(self) -> None:
        path = self._lic()
        with (
            mock.patch("overlay.read_license_text", return_value=(None, "unreadable")),
            mock.patch.object(UsageOverlay, "_show_license_load_error") as show_err,
        ):
            win = UsageOverlay(
                auto_fetch=False,
                for_test=True,
                license_path=path,
                license_prompt=lambda _t: True,
            )
            self.addCleanup(win.close)
            self.assertFalse(win._license_granted)
            show_err.assert_called_once_with("unreadable")

    def test_license_ver_is_string(self) -> None:
        path = self._lic()
        win = UsageOverlay(
            auto_fetch=False,
            for_test=True,
            license_path=path,
            license_prompt=lambda _t: True,
        )
        self.addCleanup(win.close)
        raw = self._settings.value("license_accepted_ver")
        self.assertIsInstance(raw, str)
        self.assertEqual(raw, "1")


if __name__ == "__main__":
    unittest.main()
