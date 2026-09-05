"""Percent decimal setting + 20-char clamp."""

from __future__ import annotations

import sys
import unittest

from PySide6.QtWidgets import QApplication

from lang_packs import TEXTS
from overlay import PCT_DECIMALS, PCT_TEXT_MAX, UsageOverlay


class PctDecimalsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_lang_key_and_plain_n(self) -> None:
        self.assertIn("pct_decimals_label", TEXTS["tr"])
        self.assertIn("{n}", TEXTS["tr"]["left_short"])
        self.assertNotIn("{n:.4f}", TEXTS["tr"]["left"])
        self.assertNotIn("{n:.4f}", TEXTS["en"]["usage_drop"])

    def test_set_and_clamp(self) -> None:
        win = UsageOverlay(auto_fetch=False, for_test=True)
        self.assertEqual(PCT_DECIMALS, (0, 2, 4, 6, 8, 12))
        win.set_pct_decimals(12)
        self.assertEqual(win._pct_decimals, 12)
        num = win._pct_num(12.3456789012345)
        self.assertLessEqual(len(win.t("left_short").format(n=num)), PCT_TEXT_MAX)
        win.set_pct_decimals(0)
        self.assertEqual(win._pct_num(12.4), "12")
        win.set_pct_decimals(4)
        self.assertEqual(win._pct_num(12.34567), "12.3457")
        win.close()


if __name__ == "__main__":
    unittest.main()
