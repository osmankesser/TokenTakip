"""Per-agent token advice smoke tests."""

from __future__ import annotations

import unittest

from agent_advice import build_agent_advice
from usage_client import Meter, ProviderUsage


class AgentAdviceTests(unittest.TestCase):
    def test_cursor_crit_is_personal(self) -> None:
        p = ProviderUsage(
            name="CURSOR",
            plan="Pro",
            meters=[Meter("fast", remaining_percent=8.0)],
        )
        a = build_agent_advice(p, warn_pct=40, crit_pct=15)
        self.assertEqual(a.kind, "danger")
        keys = [x.key for x in a.lines]
        self.assertIn("adv_cursor_crit", keys)
        self.assertTrue(any(k.startswith("adv_band_") for k in keys))

    def test_ollama_ok_family(self) -> None:
        p = ProviderUsage(name="OLLAMA", meters=[Meter("ctx", remaining_percent=90.0)])
        a = build_agent_advice(p)
        self.assertEqual(a.kind, "info")
        self.assertTrue(any(x.key == "adv_local_ok" for x in a.lines))


if __name__ == "__main__":
    unittest.main()
