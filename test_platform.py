"""platform_util birim testleri."""

from __future__ import annotations

import unittest

from platform_util import _startup_approved_blob, platform_ok, roaming


class PlatformUtilTests(unittest.TestCase):
    def test_platform_ok(self) -> None:
        ok, msg = platform_ok()
        if not ok:
            self.assertIn("64-bit", msg)

    def test_roaming_cursor(self) -> None:
        path = roaming("Cursor", "User")
        self.assertEqual(path.name, "User")
        self.assertEqual(path.parent.name, "Cursor")

    def test_enabled_blob(self) -> None:
        blob = _startup_approved_blob(True)
        self.assertEqual(blob[0], 0x02)
        self.assertEqual(len(blob), 12)

    def test_disabled_blob(self) -> None:
        blob = _startup_approved_blob(False)
        self.assertEqual(blob[0], 0x03)


if __name__ == "__main__":
    unittest.main()
