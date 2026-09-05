"""Windows baslangic kaydi blob testleri."""

from __future__ import annotations

import unittest

from platform_util import _startup_approved_blob


class StartupBlobTests(unittest.TestCase):
    def test_enabled_blob(self) -> None:
        blob = _startup_approved_blob(True)
        self.assertEqual(len(blob), 12)
        self.assertEqual(blob[0], 0x02)

    def test_disabled_blob(self) -> None:
        blob = _startup_approved_blob(False)
        self.assertEqual(len(blob), 12)
        self.assertEqual(blob[0], 0x03)


if __name__ == "__main__":
    unittest.main()
