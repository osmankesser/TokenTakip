"""Agent model detection."""

from __future__ import annotations

import unittest

from usage_client import ProviderUsage, _pretty_model, _cursor_selected_model, _codex_selected_model


class ModelDetectTests(unittest.TestCase):
    def test_pretty_aliases(self) -> None:
        self.assertEqual(_pretty_model("gpt-6-astra"), "GPT-6 Astra")
        self.assertEqual(_pretty_model("grok-4.6"), "Grok 4.6")

    def test_provider_model_field(self) -> None:
        self.assertEqual(ProviderUsage(name="CURSOR", model="Grok 4.6").model, "Grok 4.6")

    def test_local_reads_are_strings(self) -> None:
        self.assertIsInstance(_cursor_selected_model(), str)
        self.assertIsInstance(_codex_selected_model(), str)

    def test_codex_token_usage_format(self) -> None:
        from usage_client import _codex_token_usage, _fmt_count

        self.assertEqual(_fmt_count(6832927), "6.832.927")
        line = _codex_token_usage()
        self.assertIsInstance(line, str)
        if line:
            self.assertTrue(line.startswith("tokens_used"))



if __name__ == "__main__":
    unittest.main()
