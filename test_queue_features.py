"""Queue features 3–7 smoke checks."""

from __future__ import annotations

import sys
import unittest
from datetime import date

from PySide6.QtWidgets import QApplication

from agent_catalog import discover_agent_kits
from agent_story import build_agent_story
from overlay import UsageOverlay
from usage_client import _detect_claude
from weekly_projects import featured_projects


class QueueFeaturesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_claude_local_detect(self) -> None:
        # Machine has Local/Claude; detector must see it.
        self.assertTrue(_detect_claude())

    def test_weekly_rotate(self) -> None:
        a = featured_projects(user_agents={"cursor"}, when=date(2026, 1, 5), count=3)
        b = featured_projects(user_agents={"cursor"}, when=date(2026, 6, 1), count=3)
        self.assertEqual(len(a), 3)
        self.assertNotEqual([x.project.id for x in a], [x.project.id for b in [b] for x in b])

    def test_grouped_categories(self) -> None:
        from weekly_projects import CATALOG, grouped_projects, ranked_projects
        from github_live import build_guide, projects_instant

        self.assertEqual(len(CATALOG), 100)
        top = ranked_projects(user_agents={"cursor"})
        self.assertEqual(len(top), 100)
        instant = projects_instant()
        self.assertGreaterEqual(len(instant), 20)
        g = build_guide(instant[0], lang="tr")
        self.assertTrue(g.terminal)
        self.assertTrue(g.download)
        groups = grouped_projects(user_agents={"cursor"})
        self.assertGreaterEqual(len(groups), 4)
        self.assertIn("mcp", [c for c, _ in groups])

    def test_agent_story_need_chat(self) -> None:
        s = build_agent_story("CURSOR", allow_chat=False)
        self.assertEqual(s.note, "need_chat")

    def test_catalog_nonempty(self) -> None:
        kits = discover_agent_kits()
        self.assertTrue(any(k.agent == "Cursor" for k in kits))

    def test_brand_icons_have_ink(self) -> None:
        from overlay import _ICON_MEM, _brand_pix, _pix_has_ink, provider_pix

        _ICON_MEM.clear()
        for name in ("CLAUDE", "CODEX", "CHATGPT", "MANUS", "OLLAMA", "COPILOT"):
            pix = provider_pix(name, 32)
            self.assertFalse(pix.isNull(), name)
            self.assertTrue(_pix_has_ink(pix), name)
            self.assertTrue(_pix_has_ink(_brand_pix(name, 32)), name)

    def test_ui_pages(self) -> None:
        win = UsageOverlay(auto_fetch=False, for_test=True)
        win._quota_access = True
        win._chat_analysis = False
        win.goto("github")
        self.assertGreater(win.github_layout.count(), 1)
        self.assertEqual(win.t("github_nav"), "GitHub")
        win.goto("agents")
        self.assertGreater(win.agents_layout.count(), 1)
        win.close()


if __name__ == "__main__":
    unittest.main()
