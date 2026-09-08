"""Güvenli GitHub kurulum ön kontrolü ve terminal/ajan başlatma.

ponytail: yalnız kök manifest tarifleri; README scrape yok.
Süreç başlatma testlerde mocklanır — gerçek kurulum yalnız kullanıcı onayıyla.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

REPO_RE = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?/"
    r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$"
)
_CONTROL = re.compile(r"[\x00-\x1f\x7f]")
_UNSAFE_ARG = re.compile(r"[\"'`$;&|<>()]")

_TOOL_BINS = {
    "git": ("git",),
    "python": ("python", "python3"),
    "npm": ("npm",),
    "go": ("go",),
    "cargo": ("cargo",),
}


@dataclass(frozen=True)
class InstallRecipe:
    kind: str
    runtime: str
    commands: tuple[tuple[str, ...], ...]
    manifests: tuple[str, ...]


@dataclass(frozen=True)
class AgentCli:
    key: str
    label: str
    binary: str
    prefix: tuple[str, ...]


@dataclass(frozen=True)
class InstallPreflight:
    repo: str
    url: str
    recipe: InstallRecipe | None
    missing_tools: tuple[str, ...]
    available_agents: tuple[AgentCli, ...]
    can_terminal: bool
    can_agent: bool
    status_key: str


AGENT_CLIS: tuple[AgentCli, ...] = (
    AgentCli("cursor", "Cursor Agent", "agent", ("agent",)),
    AgentCli("claude", "Claude Code", "claude", ("claude",)),
    AgentCli(
        "codex",
        "Codex",
        "codex",
        ("codex", "--sandbox", "workspace-write", "--ask-for-approval", "on-request"),
    ),
    AgentCli("gemini", "Gemini CLI", "gemini", ("gemini", "-i")),
)

_FORBIDDEN_FLAGS = frozenset(
    {
        "--yolo",
        "--dangerously-skip-permissions",
        "--dangerously-bypass-approvals-and-sandbox",
    }
)


class InstallError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def assert_repo(repo: str) -> str:
    text = (repo or "").strip()
    if not REPO_RE.fullmatch(text) or ".." in text or text.count("/") != 1:
        raise InstallError("install_bad_repo")
    return text


def github_https_url(repo: str) -> str:
    return f"https://github.com/{assert_repo(repo)}"


def assert_safe_arg(value: str, *, code: str = "install_bad_arg") -> str:
    text = value if isinstance(value, str) else ""
    if not text or _CONTROL.search(text) or _UNSAFE_ARG.search(text):
        raise InstallError(code)
    return text


def folder_name(repo: str) -> str:
    return assert_repo(repo).split("/", 1)[1]


def recipe_for_manifests(names: Iterable[str]) -> InstallRecipe | None:
    have = {str(n).strip() for n in names if str(n).strip()}
    if "package.json" in have:
        if "package-lock.json" in have:
            return InstallRecipe(
                "npm",
                "npm",
                (("npm", "ci"),),
                ("package.json", "package-lock.json"),
            )
        return InstallRecipe("npm", "npm", (("npm", "install"),), ("package.json",))
    if "pyproject.toml" in have or "setup.py" in have:
        manifest = "pyproject.toml" if "pyproject.toml" in have else "setup.py"
        return InstallRecipe(
            "python",
            "python",
            (
                ("python", "-m", "venv", ".venv"),
                (".venv\\Scripts\\python.exe", "-m", "pip", "install", "-e", "."),
            ),
            (manifest,),
        )
    if "requirements.txt" in have:
        return InstallRecipe(
            "python",
            "python",
            (
                ("python", "-m", "venv", ".venv"),
                (".venv\\Scripts\\python.exe", "-m", "pip", "install", "-r", "requirements.txt"),
            ),
            ("requirements.txt",),
        )
    if "go.mod" in have:
        return InstallRecipe("go", "go", (("go", "build", "./..."),), ("go.mod",))
    if "Cargo.toml" in have:
        args = ("cargo", "build", "--release", "--locked") if "Cargo.lock" in have else (
            "cargo",
            "build",
            "--release",
        )
        manifests = ("Cargo.toml", "Cargo.lock") if "Cargo.lock" in have else ("Cargo.toml",)
        return InstallRecipe("cargo", "cargo", (args,), manifests)
    return None


def tool_present(name: str, *, which=shutil.which) -> bool:
    return any(which(b) for b in _TOOL_BINS.get(name, (name,)))


def detect_tools(*, which=shutil.which) -> frozenset[str]:
    return frozenset(n for n in _TOOL_BINS if tool_present(n, which=which))


def detect_agent_clis(*, which=shutil.which) -> tuple[AgentCli, ...]:
    return tuple(a for a in AGENT_CLIS if which(a.binary))


def evaluate_install(
    repo: str,
    root_names: Iterable[str],
    *,
    tools: Iterable[str] | None = None,
    agents: Iterable[AgentCli] | None = None,
) -> InstallPreflight:
    clean = assert_repo(repo)
    url = github_https_url(clean)
    recipe = recipe_for_manifests(root_names)
    present = frozenset(tools) if tools is not None else detect_tools()
    found_agents = tuple(agents) if agents is not None else detect_agent_clis()

    missing: list[str] = []
    if "git" not in present:
        missing.append("git")
    if recipe is not None and recipe.runtime not in present:
        missing.append(recipe.runtime)

    can_terminal = recipe is not None and not missing
    can_agent = (not can_terminal) and bool(found_agents)

    if can_terminal:
        status = "install_ready_terminal"
    elif recipe is not None and missing and not can_agent:
        status = "install_missing_tools"
    elif recipe is None and can_agent:
        status = "install_need_agent"
    elif can_agent:
        status = "install_need_agent"
    elif recipe is not None and missing:
        status = "install_missing_tools"
    else:
        status = "install_no_option"

    return InstallPreflight(
        repo=clean,
        url=url,
        recipe=recipe,
        missing_tools=tuple(missing),
        available_agents=found_agents,
        can_terminal=can_terminal,
        can_agent=can_agent,
        status_key=status,
    )


def probe_repo(repo: str) -> InstallPreflight:
    from github_live import fetch_root_manifests

    return evaluate_install(repo, fetch_root_manifests(repo))


def resolve_clone_target(parent: Path | str, repo: str) -> Path:
    name = folder_name(repo)
    assert_safe_arg(name, code="install_bad_repo")
    base = Path(parent).expanduser().resolve()
    if not base.is_dir():
        raise InstallError("install_bad_folder")
    target = (base / name).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise InstallError("install_bad_folder") from exc
    if target.exists():
        raise InstallError("install_target_exists")
    return target


def _ps_quote(value: str) -> str:
    text = value if isinstance(value, str) else ""
    if not text or _CONTROL.search(text):
        raise InstallError("install_bad_arg")
    return "'" + text.replace("'", "''") + "'"


def _ps_command(args: Iterable[str]) -> str:
    parts = [str(part) for part in args]
    if not parts:
        raise InstallError("install_bad_arg")
    return "& " + " ".join(_ps_quote(part) for part in parts) + (
        "; if ($LASTEXITCODE -ne 0) { throw 'Command failed' }"
    )


def terminal_plan(preflight: InstallPreflight, parent: Path | str) -> tuple[Path, list[str]]:
    if not preflight.can_terminal or preflight.recipe is None:
        raise InstallError("install_no_terminal")
    target = resolve_clone_target(parent, preflight.repo)
    parent_r = Path(parent).expanduser().resolve()
    url = assert_safe_arg(preflight.url + ".git", code="install_bad_repo")
    folder = assert_safe_arg(folder_name(preflight.repo), code="install_bad_repo")
    lines = [
        "$ErrorActionPreference = 'Stop'",
        f"Set-Location -LiteralPath {_ps_quote(str(parent_r))}",
        _ps_command(("git", "clone", "--", url, folder)),
        f"Set-Location -LiteralPath {_ps_quote(str(target))}",
    ]
    for cmd in preflight.recipe.commands:
        lines.append(_ps_command(cmd))
    lines.append("Write-Host 'Token Tracker: install commands finished — check output above.'")
    return target, lines


def agent_prompt(preflight: InstallPreflight, parent: Path | str) -> str:
    target = resolve_clone_target(parent, preflight.repo)
    parent_r = Path(parent).expanduser().resolve()
    return (
        f"Install the GitHub repository {preflight.repo} safely. "
        f"Work only under {parent_r}. "
        f"Clone https://github.com/{preflight.repo}.git into {target.name} "
        f"without overwriting an existing folder. "
        f"Inspect root manifests and install with the matching package manager. "
        f"Ask before destructive actions. Do not use --yolo or disable approvals."
    )


def agent_argv(agent: AgentCli, prompt: str) -> list[str]:
    if any(flag in agent.prefix for flag in _FORBIDDEN_FLAGS):
        raise InstallError("install_bad_agent")
    text = (prompt or "").strip()
    if not text or "\x00" in text:
        raise InstallError("install_bad_arg")
    return list(agent.prefix) + [text]


def _visible_console_flags() -> int:
    if sys.platform != "win32":
        return 0
    return int(subprocess.CREATE_NEW_CONSOLE)  # type: ignore[attr-defined]


def launch_powershell_lines(lines: list[str], *, popen=subprocess.Popen) -> None:
    if not lines:
        raise InstallError("install_launch_failed")
    script = "; ".join(lines)
    popen(
        ["powershell.exe", "-NoExit", "-NoProfile", "-Command", script],
        creationflags=_visible_console_flags(),
    )


def launch_terminal_install(
    preflight: InstallPreflight,
    parent: Path | str,
    *,
    popen=subprocess.Popen,
) -> Path:
    target, lines = terminal_plan(preflight, parent)
    launch_powershell_lines(lines, popen=popen)
    return target


def launch_agent_install(
    preflight: InstallPreflight,
    parent: Path | str,
    agent: AgentCli,
    *,
    popen=subprocess.Popen,
) -> Path:
    available = {a.key for a in preflight.available_agents}
    match = next((a for a in AGENT_CLIS if a.key == agent.key and a.key in available), None)
    if match is None:
        raise InstallError("install_bad_agent")
    target = resolve_clone_target(parent, preflight.repo)
    argv = agent_argv(match, agent_prompt(preflight, parent))
    parent_r = Path(parent).expanduser().resolve()
    lines = [
        f"Set-Location -LiteralPath {_ps_quote(str(parent_r))}",
        _ps_command(argv),
    ]
    launch_powershell_lines(lines, popen=popen)
    return target


def parse_github_repo_url(url: str) -> str:
    raw = (url or "").strip()
    parsed = urlparse(raw)
    if parsed.scheme != "https" or (parsed.hostname or "").lower() != "github.com":
        raise InstallError("install_bad_repo")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise InstallError("install_bad_repo")
    parts = [p for p in (parsed.path or "").strip("/").split("/") if p]
    if len(parts) != 2:
        raise InstallError("install_bad_repo")
    owner, name = parts[0], parts[1][:-4] if parts[1].endswith(".git") else parts[1]
    return assert_repo(f"{owner}/{name}")
