"""Güvenli kurulum ön kontrolü — enjeksiyon reddi, tarif eşleşmesi, süreç yok."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import project_installer as pi


class ProjectInstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from PySide6.QtWidgets import QApplication

        cls.app = QApplication.instance() or QApplication([])

    def test_repo_and_url_injection_rejected(self) -> None:
        bad = (
            "owner/repo;rm -rf /",
            "owner/repo && calc",
            "../evil/repo",
            "owner/repo/extra",
            "owner/repo`id`",
            "https://evil.com/owner/repo",
            "http://github.com/owner/repo",
            "https://github.com/owner/repo?token=x",
            "https://user:pass@github.com/owner/repo",
            "https://github.com/owner/repo#frag",
        )
        for item in bad:
            with self.subTest(item=item):
                with self.assertRaises(pi.InstallError):
                    if item.startswith("http"):
                        pi.parse_github_repo_url(item)
                    else:
                        pi.assert_repo(item)

    def test_parse_safe_github_url(self) -> None:
        self.assertEqual(pi.parse_github_repo_url("https://github.com/Owner/Repo.git"), "Owner/Repo")
        self.assertEqual(pi.github_https_url("Owner/Repo"), "https://github.com/Owner/Repo")

    def test_manifest_recipe_match(self) -> None:
        npm = pi.recipe_for_manifests({"README.md", "package.json", "package-lock.json"})
        self.assertIsNotNone(npm)
        assert npm is not None
        self.assertEqual(npm.runtime, "npm")
        self.assertEqual(npm.commands[0][:2], ("npm", "ci"))

        py = pi.recipe_for_manifests({"pyproject.toml"})
        self.assertIsNotNone(py)
        assert py is not None
        self.assertEqual(py.runtime, "python")

        self.assertIsNone(pi.recipe_for_manifests({"README.md", "LICENSE"}))
        alone = pi.recipe_for_manifests({"package.json"})
        self.assertIsNotNone(alone)
        assert alone is not None
        self.assertEqual(alone.commands[0], ("npm", "install"))
        self.assertIsNone(pi.recipe_for_manifests({"package-lock.json"}))

    def test_github_probe_reads_root_names_only(self) -> None:
        import github_live

        payload = [
            {"type": "file", "name": "pyproject.toml", "content": "ignored"},
            {"type": "file", "name": "README.md"},
            {"type": "dir", "name": "package.json"},
        ]
        with mock.patch.object(github_live, "_github_json", return_value=payload):
            names = github_live.fetch_root_manifests("owner/demo")
        self.assertEqual(names, {"pyproject.toml"})

    def test_missing_tools_hides_terminal(self) -> None:
        pf = pi.evaluate_install(
            "owner/demo",
            {"package.json", "package-lock.json"},
            tools=frozenset({"git"}),
            agents=(),
        )
        self.assertFalse(pf.can_terminal)
        self.assertFalse(pf.can_agent)
        self.assertIn("npm", pf.missing_tools)
        self.assertEqual(pf.status_key, "install_missing_tools")

    def test_agent_when_no_recipe(self) -> None:
        agent = pi.AGENT_CLIS[0]
        pf = pi.evaluate_install(
            "owner/demo",
            {"README.md"},
            tools=frozenset({"git", "python"}),
            agents=(agent,),
        )
        self.assertFalse(pf.can_terminal)
        self.assertTrue(pf.can_agent)
        self.assertEqual(pf.status_key, "install_need_agent")

    def test_terminal_when_recipe_and_tools(self) -> None:
        pf = pi.evaluate_install(
            "owner/demo",
            {"requirements.txt"},
            tools=frozenset({"git", "python"}),
            agents=(),
        )
        self.assertTrue(pf.can_terminal)
        self.assertFalse(pf.can_agent)

    def test_existing_target_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            (parent / "demo").mkdir()
            with self.assertRaises(pi.InstallError) as ctx:
                pi.resolve_clone_target(parent, "owner/demo")
            self.assertEqual(ctx.exception.code, "install_target_exists")

    def test_cli_detection(self) -> None:
        which = lambda name: r"C:\bin\git.exe" if name == "git" else None
        self.assertTrue(pi.tool_present("git", which=which))
        self.assertFalse(pi.tool_present("npm", which=which))
        agents = pi.detect_agent_clis(which=lambda n: "x" if n == "claude" else None)
        self.assertEqual([a.key for a in agents], ["claude"])

    def test_agent_argv_no_yolo(self) -> None:
        agent = pi.AGENT_CLIS[2]
        argv = pi.agent_argv(agent, "Install owner/demo safely")
        self.assertEqual(argv[0], "codex")
        self.assertIn("--ask-for-approval", argv)
        self.assertNotIn("--yolo", argv)
        self.assertNotIn("--dangerously-skip-permissions", " ".join(argv))

    def test_launch_never_runs_real_process(self) -> None:
        calls: list[object] = []

        def fake_popen(*_a, **_k):
            calls.append((_a, _k))
            raise AssertionError("tests must not start real processes")

        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp) / "Osman's Projects"
            parent.mkdir()
            pf = pi.evaluate_install(
                "owner/demo",
                {"package.json", "package-lock.json"},
                tools=frozenset({"git", "npm"}),
                agents=(),
            )
            with self.assertRaises(AssertionError):
                pi.launch_terminal_install(pf, parent, popen=fake_popen)
            self.assertEqual(len(calls), 1)
            args = calls[0][0][0]
            self.assertEqual(args[0], "powershell.exe")
            self.assertIn("& 'git' 'clone'", args[-1])
            self.assertNotIn("$(", args[-1])
            self.assertNotIn("-ExecutionPolicy", args)
            self.assertIn("Osman''s Projects", args[-1])

    def test_unsafe_arg_rejected(self) -> None:
        with self.assertRaises(pi.InstallError):
            pi.assert_safe_arg("foo; bar")
        with self.assertRaises(pi.InstallError):
            pi.assert_safe_arg("$(calc)")

    def test_detail_button_matches_preflight(self) -> None:
        from github_live import LiveProject
        from overlay import UsageOverlay

        win = UsageOverlay(auto_fetch=False, for_test=True, license_prompt=lambda _text: True)
        self.addCleanup(win.close)
        win._gh_projects = [
            LiveProject(1, "owner/demo", "Demo", "tools", "Demo project", language="JavaScript")
        ]
        win._open_github_detail("owner/demo")
        self.assertEqual(win._page, "github_detail")
        preflight = pi.evaluate_install(
            "owner/demo",
            {"package.json", "package-lock.json"},
            tools={"git", "npm"},
            agents=(),
        )
        win._apply_install_probe("owner/demo", preflight)
        self.assertFalse(win.gd_install_term.isHidden())
        self.assertTrue(win.gd_install_agent.isHidden())


if __name__ == "__main__":
    unittest.main()
