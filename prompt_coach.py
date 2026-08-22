"""Yerel AI sohbetlerinden (Cursor, Codex, Copilot, Claude, Continue) prompt israfı ve yardımcı önerisi."""

from __future__ import annotations

import json
import os
import re
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

HOME = Path.home()
APPDATA = Path(os.environ.get("APPDATA", ""))
CODEX_DAYS = 14
CHAT_LIMIT = 40
MAX_FILE_BYTES = 8_000_000
MAX_TOTAL_BYTES = 32_000_000
MAX_SCAN_SEC = 8.0
QUERY_RE = re.compile(r"<user_query>\s*(.*?)\s*</user_query>", re.S)
SKIP_HEAD = (
    "<recommended_plugins>",
    "<environment_context>",
    "<user_info>",
    "<mcp_instructions>",
    "<agent_skills>",
    "<system_reminder>",
)
VAGUE = re.compile(
    r"^(yap|düzelt|bak|hata|fix|help|neden|bozuk|çalışmıyor|pls|lütfen)[\s.!]*$",
    re.I,
)
REWRITE = re.compile(r"\b(hepsini|baştan|yeniden yaz|rewrite (all|everything)|from scratch)\b", re.I)
SPLIT = re.compile(r"\b(bir de|birde|ayrıca|also|and then|hem de)\b", re.I)
CODEY = re.compile(r"(bug|hata|fonksiyon|function|class|ekle|sil|fix|refactor|dosya)", re.I)
PATHY = re.compile(r"[\\/][\w.\-]+|\w+\.(py|ts|js|tsx|json|md)\b")
REBUILD = re.compile(r"\b(exe|pyinstaller|derle|rebuild)\b", re.I)
HINTS = (
    (("github", "pull request", "pr ", "issue"), ("github",)),
    (("sonar", "sonarqube", "kalite kapısı"), ("sonarqube",)),
    (("nerede tanımlı", "codebase", "mimari", "hangi dosya"), ("codebase-memory-mcp",)),
    (("ponytail", "sadeleştir", "over-engineer", "bloat"), ("ponytail", "ponytail-review")),
    (("güvenlik", "security review"), ("review-security",)),
    (("canvas", "tablo", "grafik"), ("canvas",)),
)

_scan_started = 0.0
_scan_files = 0
_scan_bytes = 0
_scan_stop = False


@dataclass
class ChatBurn:
    source: str
    title: str
    users: int
    tools: int
    chars: int
    top_tools: str


@dataclass
class Finding:
    code: str
    source: str
    snippet: str
    helpers: list[str] = field(default_factory=list)


@dataclass
class CoachReport:
    chats: int
    chars: int
    tools: int
    burns: list[ChatBurn] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    mcps: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    error: str = ""


def build_report(*, allow_chat: bool = False) -> CoachReport:
    if not allow_chat:
        return CoachReport(chats=0, chars=0, tools=0)
    global _scan_started, _scan_files, _scan_bytes, _scan_stop
    _scan_started = time.monotonic()
    _scan_files = 0
    _scan_bytes = 0
    _scan_stop = False
    mcps = _mcp_names()
    skills = _skill_names()
    have = set(mcps) | set(skills)
    chats: list[tuple[ChatBurn, list[str]]] = []
    for loader in (
        _cursor_chats,
        _claude_chats,
        _codex_chats,
        _copilot_chats,
        _continue_chats,
    ):
        if _scan_stop:
            break
        try:
            chats += loader()
        except OSError:
            continue
    burns = sorted((c for c, _ in chats), key=lambda b: b.chars + b.tools * 180, reverse=True)
    findings: list[Finding] = []
    seen: set[tuple[str, str]] = set()
    for burn, prompts in chats:
        prev = ""
        for text in prompts:
            for code, helpers in _issues(text, prev, have):
                key = (code, text[:80])
                if key in seen:
                    continue
                seen.add(key)
                findings.append(Finding(code, burn.source, _clip(text), helpers))
            prev = text
    findings = findings[:12]
    return CoachReport(
        chats=len(chats),
        chars=sum(b.chars for b in burns),
        tools=sum(b.tools for b in burns),
        burns=burns[:8],
        findings=findings,
        mcps=mcps,
        skills=skills[:16],
    )


def _issues(text: str, prev: str, have: set[str]) -> list[tuple[str, list[str]]]:
    out: list[tuple[str, list[str]]] = []
    low = text.lower()
    helpers = [name for keys, names in HINTS if any(k in low for k in keys) for name in names if name in have]
    if len(text) > 3500 or text.count("```") >= 2:
        out.append(("paste", helpers))
    if len(text) < 40 and VAGUE.search(text.strip()):
        out.append(("vague", helpers))
    if REWRITE.search(text):
        out.append(("rewrite", helpers))
    if SPLIT.search(text) and len(text) > 120:
        out.append(("split", helpers))
    if CODEY.search(text) and not PATHY.search(text) and len(text) < 800:
        out.append(("nofile", helpers))
    if REBUILD.search(text) and len(text) < 200:
        out.append(("rebuild", helpers))
    if prev and prev[:90] == text[:90] and len(text) > 20:
        out.append(("dup", helpers))
    if helpers and not out:
        out.append(("helper", helpers))
    return out


def _budget_ok() -> bool:
    global _scan_stop
    if _scan_stop:
        return False
    if _scan_files >= CHAT_LIMIT:
        _scan_stop = True
        return False
    if _scan_bytes >= MAX_TOTAL_BYTES:
        _scan_stop = True
        return False
    if _scan_started and time.monotonic() - _scan_started > MAX_SCAN_SEC:
        _scan_stop = True
        return False
    return True


def _resolve_root(root: Path) -> Path | None:
    try:
        if not root.is_dir():
            return None
        return root.resolve()
    except OSError:
        return None


def _under(root: Path, path: Path) -> bool:
    try:
        resolved = path.resolve()
    except OSError:
        return False
    return resolved == root or root in resolved.parents


def _collect_files(root: Path, pattern: str) -> list[Path]:
    resolved = _resolve_root(root)
    if resolved is None:
        return []
    out: list[Path] = []
    try:
        candidates = sorted(resolved.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    except OSError:
        return []
    for path in candidates:
        if not _budget_ok():
            break
        if not _under(resolved, path):
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > MAX_FILE_BYTES:
            continue
        out.append(path)
    return out


def _cursor_chats() -> list[tuple[ChatBurn, list[str]]]:
    return _transcript_chats("Cursor", HOME / ".cursor" / "projects", "*/agent-transcripts/*/*.jsonl")


def _claude_chats() -> list[tuple[ChatBurn, list[str]]]:
    return _transcript_chats("Claude", HOME / ".claude" / "projects", "*/*.jsonl", skip_subagents=False)


def _transcript_chats(
    label: str,
    root: Path,
    pattern: str,
    *,
    skip_subagents: bool = True,
) -> list[tuple[ChatBurn, list[str]]]:
    out = []
    for path in _collect_files(root, pattern):
        if skip_subagents and "subagents" in path.parts:
            continue
        if not _take_file(path):
            break
        burn, prompts = _parse_transcript(path, label)
        if prompts or burn.tools:
            out.append((burn, prompts))
    return out


def _take_file(path: Path) -> bool:
    global _scan_files, _scan_bytes, _scan_stop
    if not _budget_ok():
        return False
    try:
        size = path.stat().st_size
    except OSError:
        return False
    if size > MAX_FILE_BYTES or _scan_bytes + size > MAX_TOTAL_BYTES:
        if _scan_bytes + size > MAX_TOTAL_BYTES:
            _scan_stop = True
        return False
    _scan_files += 1
    _scan_bytes += size
    return True


def _parse_transcript(path: Path, label: str) -> tuple[ChatBurn, list[str]]:
    prompts: list[str] = []
    tools: Counter[str] = Counter()
    chars = 0
    users = 0
    for obj in _jsonl(path):
        role = obj.get("role")
        msg = obj.get("message") or {}
        if role == "user" and isinstance(msg, str):
            blob = msg
            chars += len(blob)
            text = _user_text(blob)
            if text:
                prompts.append(text)
                users += 1
            continue
        for part in msg.get("content") or []:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "text":
                blob = str(part.get("text") or "")
                chars += len(blob)
                if role == "user":
                    text = _user_text(blob)
                    if text:
                        prompts.append(text)
                        users += 1
            elif part.get("type") == "tool_use":
                tools[str(part.get("name") or "tool")] += 1
        if obj.get("type") == "user" and not role:
            blob = _join_parts(obj.get("content") or obj.get("message"))
            chars += len(blob)
            text = _user_text(blob)
            if text:
                prompts.append(text)
                users += 1
    top = ", ".join(f"{n}×{c}" for n, c in tools.most_common(3)) or "—"
    title = path.stem[:8] if path.suffix else path.parent.name[:8]
    return ChatBurn(label, title, users, sum(tools.values()), chars, top), prompts


def _codex_chats() -> list[tuple[ChatBurn, list[str]]]:
    root = HOME / ".codex"
    resolved = _resolve_root(root)
    if resolved is None:
        return []
    cutoff = datetime.now() - timedelta(days=CODEX_DAYS)
    files: list[Path] = []
    for pattern in ("sessions/*/*/*/rollout-*.jsonl", "archived_sessions/rollout-*.jsonl"):
        for path in _collect_files(resolved, pattern):
            try:
                if datetime.fromtimestamp(path.stat().st_mtime) < cutoff:
                    continue
            except OSError:
                continue
            files.append(path)
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    out = []
    for path in files:
        if not _take_file(path):
            break
        burn, prompts = _parse_codex(path)
        if prompts or burn.tools:
            out.append((burn, prompts))
    return out


def _copilot_chats() -> list[tuple[ChatBurn, list[str]]]:
    if not APPDATA.is_dir():
        return []
    out: list[tuple[ChatBurn, list[str]]] = []
    seen: set[Path] = set()
    for ide in ("Code", "Cursor", "Windsurf", "Trae", "VSCodium"):
        base = APPDATA / ide / "User" / "workspaceStorage"
        resolved = _resolve_root(base)
        if resolved is None:
            continue
        label = "Copilot" if ide == "Code" else f"Copilot ({ide})"
        files: list[Path] = []
        files.extend(_collect_files(resolved, "*/GitHub.copilot-chat/transcripts/*.jsonl"))
        files.extend(_collect_files(resolved, "*/chatSessions/*.jsonl"))
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        for path in files:
            if path in seen:
                continue
            seen.add(path)
            if not _take_file(path):
                return out
            if "transcripts" in path.parts:
                burn, prompts = _parse_copilot_transcript(path, label)
            else:
                burn, prompts = _parse_copilot_session(path, label)
            if prompts or burn.tools:
                out.append((burn, prompts))
    return out


def _parse_copilot_transcript(path: Path, label: str) -> tuple[ChatBurn, list[str]]:
    prompts: list[str] = []
    tools: Counter[str] = Counter()
    chars = 0
    users = 0
    for obj in _jsonl(path):
        typ = obj.get("type")
        data = obj.get("data") or {}
        if typ == "user.message":
            blob = str(data.get("content") or "")
            chars += len(blob)
            text = _user_text(blob)
            if text:
                prompts.append(text)
                users += 1
        elif typ == "assistant.message":
            blob = str(data.get("content") or "")
            chars += len(blob)
            for tr in data.get("toolRequests") or []:
                if isinstance(tr, dict):
                    tools[str(tr.get("name") or tr.get("toolName") or "tool")] += 1
    top = ", ".join(f"{n}×{c}" for n, c in tools.most_common(3)) or "—"
    return ChatBurn(label, path.stem[:8], users, sum(tools.values()), chars, top), prompts


def _parse_copilot_session(path: Path, label: str) -> tuple[ChatBurn, list[str]]:
    prompts: list[str] = []
    tools: Counter[str] = Counter()
    chars = 0
    users = 0
    state: dict | None = None
    for obj in _jsonl(path):
        kind = obj.get("kind")
        if kind == 0:
            state = obj.get("v") if isinstance(obj.get("v"), dict) else state
        elif kind == 2 and obj.get("k") == ["requests"]:
            if state is None:
                state = {}
            state["requests"] = obj.get("v") or []
    for req in (state or {}).get("requests") or []:
        if not isinstance(req, dict):
            continue
        msg = req.get("message") or {}
        blob = str(msg.get("text") or msg.get("content") or "")
        chars += len(blob)
        text = _user_text(blob)
        if text:
            prompts.append(text)
            users += 1
        for block in req.get("response") or []:
            if not isinstance(block, dict):
                continue
            val = block.get("value")
            if isinstance(val, str):
                chars += len(val)
            for tr in block.get("toolRequests") or []:
                if isinstance(tr, dict):
                    tools[str(tr.get("name") or "tool")] += 1
    top = ", ".join(f"{n}×{c}" for n, c in tools.most_common(3)) or "—"
    return ChatBurn(label, path.stem[:8], users, sum(tools.values()), chars, top), prompts


def _continue_chats() -> list[tuple[ChatBurn, list[str]]]:
    root = HOME / ".continue" / "sessions"
    out = []
    for path in _collect_files(root, "*.json"):
        if not _take_file(path):
            break
        burn, prompts = _parse_continue(path)
        if prompts:
            out.append((burn, prompts))
    return out


def _parse_continue(path: Path) -> tuple[ChatBurn, list[str]]:
    prompts: list[str] = []
    chars = 0
    users = 0
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return ChatBurn("Continue", path.stem[:8], 0, 0, 0, "—"), []
    history = data.get("history") if isinstance(data, dict) else data
    if not isinstance(history, list):
        return ChatBurn("Continue", path.stem[:8], 0, 0, 0, "—"), []
    for turn in history:
        if not isinstance(turn, dict) or turn.get("role") != "user":
            continue
        blob = _join_parts(turn.get("content"))
        chars += len(blob)
        text = _user_text(blob)
        if text:
            prompts.append(text)
            users += 1
    return ChatBurn("Continue", path.stem[:8], users, 0, chars, "—"), prompts


def _parse_codex(path: Path) -> tuple[ChatBurn, list[str]]:
    prompts: list[str] = []
    tools: Counter[str] = Counter()
    chars = 0
    users = 0
    for obj in _jsonl(path):
        if obj.get("type") != "response_item":
            continue
        pl = obj.get("payload") or {}
        kind = pl.get("type")
        if kind == "message":
            blob = _join_parts(pl.get("content"))
            chars += len(blob)
            if pl.get("role") == "user":
                text = _user_text(blob)
                if text:
                    prompts.append(text)
                    users += 1
        elif kind in ("function_call", "custom_tool_call"):
            tools[str(pl.get("name") or kind)] += 1
    top = ", ".join(f"{n}×{c}" for n, c in tools.most_common(3)) or "—"
    return ChatBurn("Codex", path.stem[8:27], users, sum(tools.values()), chars, top), prompts


def _jsonl(path: Path):
    # ponytail: skip huge logs; full parse if we need older turns
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return
        with path.open(encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh):
                if i > 4000:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


def _join_parts(content) -> str:
    if isinstance(content, str):
        return content
    bits = []
    for part in content or []:
        if isinstance(part, str):
            bits.append(part)
        elif isinstance(part, dict):
            bits.append(str(part.get("text") or part.get("input_text") or ""))
    return "\n".join(bits)


def _user_text(blob: str) -> str:
    if not blob:
        return ""
    hit = QUERY_RE.search(blob)
    if hit:
        return hit.group(1).strip()
    head = blob.lstrip()
    if any(head.startswith(tag) for tag in SKIP_HEAD):
        return ""
    if len(blob) > 2500 and head.startswith("<"):
        return ""
    return blob.strip()


def _clip(text: str, n: int = 140) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1] + "…"


def _mcp_names() -> list[str]:
    names: set[str] = set()
    for path in (HOME / ".cursor" / "mcp.json", APPDATA / "Code" / "User" / "mcp.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        servers = data.get("mcpServers") or {}
        names.update(servers)
    return sorted(names)


def _skill_names() -> list[str]:
    names: list[str] = []
    for root in (HOME / ".cursor" / "skills", HOME / ".cursor" / "skills-cursor", HOME / ".codex" / "skills"):
        if not root.is_dir():
            continue
        for skill in root.glob("*/SKILL.md"):
            if ".system" in skill.parts:
                continue
            names.append(_skill_label(skill))
    return sorted(set(names))


def _skill_label(path: Path) -> str:
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:800]
    except OSError:
        return path.parent.name
    hit = re.search(r"^name:\s*([^\n]+)", head, re.M)
    return (hit.group(1).strip() if hit else path.parent.name)


def _demo() -> None:
    assert build_report(allow_chat=False).chats == 0
    assert isinstance(build_report(allow_chat=False), CoachReport)
    assert _user_text("<user_query>\nfoo bar\n</user_query>") == "foo bar"
    assert _user_text("<recommended_plugins>\nnope") == ""
    assert any(c == "vague" for c, _ in _issues("düzelt", "", set()))
    assert any(c == "nofile" for c, _ in _issues("bu fonksiyondaki hatayı düzelt", "", set()))
    assert not any(c == "nofile" for c, _ in _issues("overlay.py içindeki hatayı düzelt", "", set()))
    print("coach-ok")


if __name__ == "__main__":
    _demo()
