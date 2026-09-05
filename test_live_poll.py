"""Live poll helpers."""

from __future__ import annotations

import sys
import unittest

from PySide6.QtWidgets import QApplication

from overlay import INTERVALS, UsageOverlay, _pct_drop


class LivePollTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_intervals_include_live(self) -> None:
        self.assertEqual(INTERVALS, (5, 30, 60, 300))

    def test_pct_drop_only_on_decrease(self) -> None:
        store: dict[str, float] = {}
        self.assertIsNone(_pct_drop(store, "c", 50.0))
        self.assertIsNone(_pct_drop(store, "c", 50.0))
        self.assertAlmostEqual(_pct_drop(store, "c", 49.5) or 0.0, 0.5)
        self.assertIsNone(_pct_drop(store, "c", 60.0))

    def test_live_glyphs(self) -> None:
        from PySide6.QtGui import QColor
        from overlay import _glyph

        ok = _glyph("live_ok", QColor("#22c55e"), 14)
        err = _glyph("live_err", QColor("#ef4444"), 14)
        self.assertFalse(ok.isNull())
        self.assertFalse(err.isNull())

    def test_live_icon_next_to_version(self) -> None:
        win = UsageOverlay(auto_fetch=False, for_test=True)
        win._quota_access = True
        win._set_live_state("live")
        self.assertFalse(win.live_icon.isHidden())
        self.assertEqual(win._live_state, "live")
        self.assertTrue(win._live_pulse.isActive())
        win._set_live_state("idle")
        self.app.processEvents()
        self.assertFalse(win._live_pulse.isActive())
        win._set_live_state("err")
        self.assertTrue(win._live_pulse.isActive())
        self.assertFalse(win.live_icon.pixmap().isNull())
        win.close()

    def test_live_interval_applies_when_shown(self) -> None:
        win = UsageOverlay(auto_fetch=False, for_test=True)
        win._quota_access = True
        win._auto_fetch = True
        win.set_interval(5)
        self.assertEqual(win._interval, 5)
        self.assertEqual(win.timer.interval(), 30_000)
        win.show()
        self.app.processEvents()
        self.assertEqual(win._poll_seconds(), 5)
        self.assertEqual(win.timer.interval(), 5_000)
        win.hide()
        self.app.processEvents()
        self.assertEqual(win.timer.interval(), 30_000)
        win.close()


if __name__ == "__main__":
    unittest.main()
