"""Ajan kurallari + eklentiler — salt okunur kesif (dosya degistirmez)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from platform_util import home, roaming

_EXT_VER = re.compile(r"^(?P<id>.+)-(?P<ver>\d+\.\d+\.\d+.*)$")
_MAX_PER = 40  # ponytail: UI tavan; upgrade = filtre/arama


@dataclass(frozen=True)
class Addon:
    kind: str  # rule | extension | skill | mcp | plugin
    name: str
    path: str = ""
    detail: str = ""


@dataclass
class AgentKit:
    agent: str
    addons: list[Addon] = field(default_factory=list)

    def by_kind(self, kind: str) -> list[Addon]:
        return [a for a in self.addons if a.kind == kind]


def discover_agent_kits() -> list[AgentKit]:
    kits = [
        _cursor_kit(),
        _vscode_kit(),
        _codex_kit(),
        _claude_kit(),
        _copilot_kit(),
        _agents_home_kit(),
    ]
    return [k for k in kits if k.addons]


def _cursor_kit() -> AgentKit:
    kit = AgentKit("Cursor")
    kit.addons.extend(_vscode_like_extensions(home(".cursor", "extensions")))
    kit.addons.extend(_skill_dirs(home(".cursor", "skills"), "skill"))
    kit.addons.extend(_skill_dirs(home(".cursor", "skills-cursor"), "skill"))
    kit.addons.extend(_rule_files(home(".cursor", "rules")))
    kit.addons.extend(_mcp_from(home(".cursor", "mcp.json")))
    # open project rules (cwd if under a workspace with markers)
    for root in _nearby_project_roots():
        kit.addons.extend(_project_rules(root, agent="Cursor"))
    return _dedupe(kit)


def _vscode_kit() -> AgentKit:
    kit = AgentKit("VS Code")
    kit.addons.extend(_vscode_like_extensions(home(".vscode", "extensions")))
    kit.addons.extend(_mcp_from(roaming("Code", "User", "mcp.json")))
    return _dedupe(kit)


def _codex_kit() -> AgentKit:
    kit = AgentKit("Codex")
    for path in (home(".codex", "AGENTS.md"), home(".codex", "instructions.md")):
        if path.is_file():
            kit.addons.append(Addon("rule", path.name, str(path), "user"))
    kit.addons.extend(_skill_dirs(home(".codex", "skills"), "skill"))
    kit.addons.extend(_codex_plugins(home(".codex", "plugins")))
    for root in _nearby_project_roots():
        p = root / "AGENTS.md"
        if p.is_file():
            kit.addons.append(Addon("rule", "AGENTS.md", str(p), root.name))
    return _dedupe(kit)


def _claude_kit() -> AgentKit:
    kit = AgentKit("Claude")
    for path in (home(".claude", "CLAUDE.md"), home(".claude", "rules")):
        if path.is_file():
            kit.addons.append(Addon("rule", path.name, str(path), "user"))
        elif path.is_dir():
            kit.addons.extend(_rule_files(path))
    for root in _nearby_project_roots():
        for name in ("CLAUDE.md", ".claude/CLAUDE.md"):
            p = root / name
            if p.is_file():
                kit.addons.append(Addon("rule", p.name, str(p), root.name))
    return _dedupe(kit)


def _copilot_kit() -> AgentKit:
    kit = AgentKit("Copilot")
    for root in _nearby_project_roots():
        for rel in (
            ".github/copilot-instructions.md",
            ".github/instructions",
        ):
            p = root / rel
            if p.is_file():
                kit.addons.append(Addon("rule", p.name, str(p), root.name))
            elif p.is_dir():
                for f in sorted(p.glob("*.md"))[:_MAX_PER]:
                    kit.addons.append(Addon("rule", f.name, str(f), root.name))
    ide = home(".copilot", "ide")
    if ide.is_dir():
        kit.addons.append(Addon("extension", "copilot-ide", str(ide), "local"))
    return _dedupe(kit)


def _agents_home_kit() -> AgentKit:
    """Cursor/Codex paylasimli .agents klasoru."""
    kit = AgentKit("Agents (.agents)")
    kit.addons.extend(_skill_dirs(home(".agents", "skills"), "skill"))
    mp = home(".agents", "plugins", "marketplace.json")
    if mp.is_file():
        try:
            data = json.loads(mp.read_text(encoding="utf-8"))
            plugins = data.get("plugins") if isinstance(data, dict) else None
            if isinstance(plugins, list):
                for item in plugins[:_MAX_PER]:
                    if isinstance(item, dict):
                        name = str(item.get("name") or item.get("id") or "plugin")
                    else:
                        name = str(item)
                    kit.addons.append(Addon("plugin", name, str(mp), "marketplace"))
            elif isinstance(plugins, dict):
                for name in list(plugins)[:_MAX_PER]:
                    kit.addons.append(Addon("plugin", str(name), str(mp), "marketplace"))
        except (OSError, json.JSONDecodeError):
            pass
    return _dedupe(kit)


def _vscode_like_extensions(root: Path) -> list[Addon]:
    out: list[Addon] = []
    if not root.is_dir():
        return out
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        name = child.name
        ver = ""
        m = _EXT_VER.match(name)
        if m:
            name, ver = m.group("id"), m.group("ver")
        out.append(Addon("extension", name, str(child), ver))
        if len(out) >= _MAX_PER:
            break
    return out


def _skill_dirs(root: Path, kind: str) -> list[Addon]:
    out: list[Addon] = []
    if not root.is_dir():
        return out
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        out.append(Addon(kind, child.name, str(child)))
        if len(out) >= _MAX_PER:
            break
    return out


def _rule_files(root: Path) -> list[Addon]:
    out: list[Addon] = []
    if not root.is_dir():
        return out
    for path in sorted(root.glob("*")):
        if path.suffix.lower() in {".md", ".mdc", ".txt"} and path.is_file():
            out.append(Addon("rule", path.name, str(path)))
        if len(out) >= _MAX_PER:
            break
    return out


def _project_rules(root: Path, *, agent: str) -> list[Addon]:
    out: list[Addon] = []
    for rel in (".cursorrules", "AGENTS.md", ".cursor/rules"):
        p = root / rel
        if p.is_file():
            out.append(Addon("rule", p.name, str(p), root.name))
        elif p.is_dir():
            for f in _rule_files(p):
                out.append(Addon("rule", f.name, f.path, root.name))
    return out[:_MAX_PER]


def _mcp_from(path: Path) -> list[Addon]:
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    servers = data.get("mcpServers") or {}
    if not isinstance(servers, dict):
        return []
    return [Addon("mcp", str(name), str(path)) for name in list(servers)[:_MAX_PER]]


def _codex_plugins(root: Path) -> list[Addon]:
    out: list[Addon] = []
    cache = root / "cache"
    if not cache.is_dir():
        return out
    for vendor in sorted(cache.iterdir()):
        if not vendor.is_dir() or vendor.name.startswith("."):
            continue
        for plugin in sorted(vendor.iterdir()):
            if plugin.is_dir() and not plugin.name.startswith("."):
                out.append(Addon("plugin", f"{vendor.name}/{plugin.name}", str(plugin)))
            if len(out) >= _MAX_PER:
                return out
    return out


def _nearby_project_roots() -> list[Path]:
    """Acik proje kokleri — Token Tracker klasoru + birkaç Cursor project decode."""
    roots: list[Path] = []
    here = Path(__file__).resolve().parent
    if (here / "AGENTS.md").exists() or (here / ".cursor").exists():
        roots.append(here)
    proj = home(".cursor", "projects")
    if proj.is_dir():
        for d in sorted(proj.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)[:12]:
            decoded = _decode_cursor_project(d.name)
            if decoded and decoded.is_dir():
                roots.append(decoded)
    # unique preserve order
    seen: set[str] = set()
    out: list[Path] = []
    for r in roots:
        key = str(r).lower()
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out[:8]


def _decode_cursor_project(name: str) -> Path | None:
    # Cursor encodes paths like c-Users-KESER-Documents-...
    if not name or name.startswith("."):
        return None
    text = name
    if text.startswith("c-Users-") or text.startswith("C-Users-"):
        text = "C:/Users/" + text.split("-Users-", 1)[1].replace("-", "/")
        # fragile; also try dash-as-space recovery for known roots
    # Better: read project.json if present
    meta = home(".cursor", "projects", name)
    for cand in ("project.json", "workspace.json", ".workspace.json"):
        p = meta / cand
        if p.is_file():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            for key in ("rootPath", "path", "folder", "workspacePath"):
                val = data.get(key) if isinstance(data, dict) else None
                if isinstance(val, str) and Path(val).is_dir():
                    return Path(val)
    return None


def _dedupe(kit: AgentKit) -> AgentKit:
    seen: set[tuple[str, str]] = set()
    out: list[Addon] = []
    for a in kit.addons:
        key = (a.kind, a.name.lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(a)
    kit.addons = out
    return kit
