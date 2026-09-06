"""auto_translate — çevrimdışı / mock duman testi."""

from __future__ import annotations

import json
import unittest
from unittest import mock

import auto_translate as at
from github_live import LiveProject, build_guide, localize_blurb, localize_guide


class AutoTranslateTests(unittest.TestCase):
    def setUp(self) -> None:
        at.FORCE_OFFLINE = False
        at.clear_memory_cache()
        at._DISK = {}

    def tearDown(self) -> None:
        at.FORCE_OFFLINE = False

    def test_offline_passthrough(self) -> None:
        at.FORCE_OFFLINE = True
        self.assertEqual(at.translate("Hello world", "tr"), "Hello world")

    def test_gtx_mock(self) -> None:
        payload = json.dumps([[["Merhaba dünya", "Hello world", None, None]]], ensure_ascii=False)

        class _Resp:
            def read(self) -> bytes:
                return payload.encode("utf-8")

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        with mock.patch("auto_translate.urllib.request.urlopen", return_value=_Resp()):
            with mock.patch.object(at, "_save_cache"):
                out = at.translate("Hello world", "tr")
        self.assertEqual(out, "Merhaba dünya")

    def test_localize_guide_preserves_terminal(self) -> None:
        at.FORCE_OFFLINE = True
        proj = LiveProject(
            rank=1,
            repo="acme/demo",
            title="Demo",
            cat="tools",
            description="A cool agent toolkit",
            stars=10,
            language="Python",
        )
        g = build_guide(proj, lang="en")
        loc = localize_guide(g, "de")
        self.assertEqual(loc.terminal, g.terminal)
        self.assertEqual(loc.download, g.download)

    def test_localize_blurb_offline(self) -> None:
        at.FORCE_OFFLINE = True
        self.assertEqual(localize_blurb("Open source MCP", "tr"), "Open source MCP")


if __name__ == "__main__":
    unittest.main()
