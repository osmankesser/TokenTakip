"""Assert token-saving tips rank MCP/skills and waste patterns."""

from __future__ import annotations

import unittest

from prompt_coach import ChatBurn, Finding, TokenTip, _build_token_tips


class TokenTipsTests(unittest.TestCase):
    def test_baseline_always_present(self) -> None:
        tips = _build_token_tips([], [], [], [])
        self.assertEqual([t.code for t in tips], ["tip_baseline"])

    def test_paste_and_mcp_rank_high(self) -> None:
        findings = [
            Finding("paste", "Cursor", "x" * 100, count=3),
            Finding("helper", "Cursor", "use github", helpers=["user-github"], count=2),
        ]
        tips = _build_token_tips(
            [ChatBurn("Cursor", "", 1, 2, 1000, "Read×5")],
            findings,
            ["user-github", "cursor-ide-browser"],
            ["create-rule"],
        )
        codes = [t.code for t in tips]
        self.assertIn("tip_paste", codes)
        self.assertIn("tip_mcp", codes)
        mcp = next(t for t in tips if t.code == "tip_mcp")
        self.assertEqual(mcp.detail, "user-github")
        self.assertLess(codes.index("tip_paste"), codes.index("tip_baseline"))
        self.assertIsInstance(tips[0], TokenTip)

    def test_path_tip_uses_top_tools(self) -> None:
        burns = [ChatBurn("Cursor", "", 1, 10, 2000, "Read×8, Grep×4")]
        tips = _build_token_tips(burns, [], [], [])
        path = next(t for t in tips if t.code == "tip_path")
        self.assertTrue(any("Read" in h or "Grep" in h for h in path.helpers))


if __name__ == "__main__":
    unittest.main()
