"""Yerel AI sohbetlerinden (Cursor, Claude, Codex, Gemini, Copilot, Continue) prompt israfı ve yardımcı önerisi."""

from __future__ import annotations

import json
import os
import re
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from platform_util import home, roaming
CODEX_DAYS = 14
CODEX_TAIL_BYTES = 4_000_000  # ponytail: rollout logs grow unbounded; read tail only, upgrade path: session_index cursors
CHAT_LIMIT = 40
SOURCE_CAP = 8  # ponytail: global limit; each loader gets a slice so Cursor cannot starve Codex/Claude/etc.
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
    when: str = ""
    path: str = ""


@dataclass
class Finding:
    code: str
    source: str
    snippet: str
    helpers: list[str] = field(default_factory=list)
    path: str = ""
    when: str = ""
    count: int = 1


@dataclass
class TokenTip:
    code: str
    helpers: list[str] = field(default_factory=list)
    weight: int = 0
    detail: str = ""


@dataclass
class CoachReport:
    chats: int
    chars: int
    tools: int
    burns: list[ChatBurn] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    tips: list[TokenTip] = field(default_factory=list)
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
        _gemini_chats,
        _continue_chats,
    ):
        if _scan_stop:
            break
        try:
            chats += loader(SOURCE_CAP)
        except OSError:
            continue
    burns = sorted((c for c, _ in chats), key=lambda b: b.chars + b.tools * 180, reverse=True)
    by_source: dict[str, list[Finding]] = {}
    seen: set[tuple[str, str, str]] = set()
    counts: Counter[tuple[str, str]] = Counter()
    for burn, prompts in chats:
        prev = ""
        for text in prompts:
            for code, helpers in _issues(text, prev, have):
                counts[(burn.source, code)] += 1
                key = (burn.source, code, text[:80])
                if key in seen:
                    continue
                seen.add(key)
                by_source.setdefault(burn.source, []).append(
                    Finding(code, burn.source, _clip(text), helpers, burn.path, burn.when)
                )
            prev = text
    findings = _merge_findings(by_source, 12)
    for item in findings:
        item.count = counts[(item.source, item.code)]
    tips = _build_token_tips(burns, findings, mcps, skills)
    return CoachReport(
        chats=len(chats),
        chars=sum(b.chars for b in burns),
        tools=sum(b.tools for b in burns),
        burns=burns[:8],
        findings=findings,
        tips=tips,
        mcps=mcps,
        skills=skills[:16],
    )


def _tool_counts(burns: list[ChatBurn]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for burn in burns:
        blob = (burn.top_tools or "").replace("—", "")
        for part in blob.split(","):
            part = part.strip()
            if not part:
                continue
            name = part.split("×")[0].split("x")[0].strip()
            if not name:
                continue
            try:
                n = int(part.rsplit("×", 1)[1]) if "×" in part else 1
            except (ValueError, IndexError):
                n = 1
            counts[name] += max(1, n)
    return counts


def _build_token_tips(
    burns: list[ChatBurn],
    findings: list[Finding],
    mcps: list[str],
    skills: list[str],
) -> list[TokenTip]:
    tips: list[TokenTip] = []
    codes = Counter({f.code: f.count for f in findings})
    for f in findings:
        codes[f.code] = max(codes[f.code], f.count)
    helper_hits: Counter[str] = Counter()
    for item in findings:
        for name in item.helpers:
            helper_hits[name] += max(1, item.count)
    tools = _tool_counts(burns)
    top_tools = [name for name, _ in tools.most_common(4)]

    if codes.get("paste", 0) >= 1:
        tips.append(TokenTip("tip_paste", weight=100 + codes["paste"] * 10))
    if codes.get("vague", 0) >= 1:
        tips.append(TokenTip("tip_vague", weight=80 + codes["vague"] * 8))
    if codes.get("dup", 0) >= 1:
        tips.append(TokenTip("tip_dup", weight=70 + codes["dup"] * 8))
    if codes.get("split", 0) >= 1 or codes.get("rewrite", 0) >= 1:
        tips.append(TokenTip("tip_focus", weight=65 + codes.get("split", 0) * 5 + codes.get("rewrite", 0) * 5))
    if codes.get("rebuild", 0) >= 1:
        tips.append(TokenTip("tip_rebuild", weight=60 + codes["rebuild"] * 5))
    if any(t for t in top_tools if t.lower() in ("read_file", "read", "grep", "shell", "bash", "run_terminal_cmd")):
        tips.append(TokenTip("tip_path", helpers=top_tools[:3], weight=55 + sum(tools[t] for t in top_tools[:3])))
    if burns and max((b.chars for b in burns), default=0) > 80_000:
        tips.append(TokenTip("tip_session", weight=50))

    # Prefer MCP/skills that already match chat issues, else installed ones
    ranked_helpers = [n for n, _ in helper_hits.most_common(6)]
    for name in ranked_helpers:
        if name in mcps:
            tips.append(TokenTip("tip_mcp", helpers=[name], weight=90 + helper_hits[name] * 12, detail=name))
        elif name in skills:
            tips.append(TokenTip("tip_skill", helpers=[name], weight=85 + helper_hits[name] * 12, detail=name))
    for name in mcps:
        if name in helper_hits:
            continue
        tips.append(TokenTip("tip_mcp", helpers=[name], weight=40, detail=name))
        if sum(1 for t in tips if t.code == "tip_mcp") >= 3:
            break
    for name in skills[:4]:
        if name in helper_hits:
            continue
        tips.append(TokenTip("tip_skill", helpers=[name], weight=35, detail=name))
        if sum(1 for t in tips if t.code == "tip_skill") >= 2:
            break

    tips.append(TokenTip("tip_baseline", weight=10))
    tips.sort(key=lambda t: t.weight, reverse=True)
    # dedupe by code+detail
    seen: set[tuple[str, str]] = set()
    out: list[TokenTip] = []
    for tip in tips:
        key = (tip.code, tip.detail)
        if key in seen:
            continue
        seen.add(key)
        out.append(tip)
        if len(out) >= 8:
            break
    return out


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


def _merge_findings(by_source: dict[str, list[Finding]], limit: int) -> list[Finding]:
    if not by_source:
        return []
    per = max(2, limit // max(1, len(by_source)))
    buckets = {src: list(items) for src, items in by_source.items()}
    out: list[Finding] = []
    while len(out) < limit and any(buckets.values()):
        for src in sorted(buckets):
            if not buckets[src]:
                continue
            if sum(1 for f in out if f.source == src) >= per:
                continue
            out.append(buckets[src].pop(0))
            if len(out) >= limit:
                break
        if all(not buckets[src] or sum(1 for f in out if f.source == src) >= per for src in buckets):
            for src in sorted(buckets):
                while buckets[src] and len(out) < limit:
                    out.append(buckets[src].pop(0))
            break
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


def _collect_files(root: Path, pattern: str, *, allow_large: bool = False) -> list[Path]:
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
        if not allow_large and size > MAX_FILE_BYTES:
            continue
        out.append(path)
    return out


def _cursor_chats(limit: int | None = None) -> list[tuple[ChatBurn, list[str]]]:
    return _transcript_chats("Cursor", home(".cursor", "projects"), "*/agent-transcripts/*/*.jsonl", limit=limit)


def _claude_chats(limit: int | None = None) -> list[tuple[ChatBurn, list[str]]]:
    return _transcript_chats(
        "Claude", home(".claude", "projects"), "*/*.jsonl", skip_subagents=False, limit=limit
    )


def _transcript_chats(
    label: str,
    root: Path,
    pattern: str,
    *,
    skip_subagents: bool = True,
    limit: int | None = None,
) -> list[tuple[ChatBurn, list[str]]]:
    out = []
    for path in _collect_files(root, pattern):
        if limit is not None and len(out) >= limit:
            break
        if skip_subagents and "subagents" in path.parts:
            continue
        if not _take_file(path):
            break
        burn, prompts = _parse_transcript(path, label)
        if prompts or burn.tools:
            out.append((burn, prompts))
    return out


def _take_file(path: Path, *, charge: int | None = None) -> bool:
    global _scan_files, _scan_bytes, _scan_stop
    if not _budget_ok():
        return False
    try:
        size = path.stat().st_size
    except OSError:
        return False
    bill = charge if charge is not None else size
    if charge is None and size > MAX_FILE_BYTES:
        return False
    if bill > MAX_FILE_BYTES or _scan_bytes + bill > MAX_TOTAL_BYTES:
        if _scan_bytes + bill > MAX_TOTAL_BYTES:
            _scan_stop = True
        return False
    _scan_files += 1
    _scan_bytes += bill
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
    return ChatBurn(label, title, users, sum(tools.values()), chars, top, _when(path), str(path)), prompts


def _codex_chats(limit: int | None = None) -> list[tuple[ChatBurn, list[str]]]:
    root = home(".codex")
    resolved = _resolve_root(root)
    if resolved is None:
        return []
    titles = _codex_session_titles()
    cutoff = datetime.now() - timedelta(days=CODEX_DAYS)
    files: list[Path] = []
    for pattern in ("sessions/**/rollout-*.jsonl", "archived_sessions/rollout-*.jsonl"):
        for path in _collect_files(resolved, pattern, allow_large=True):
            try:
                if datetime.fromtimestamp(path.stat().st_mtime) < cutoff:
                    continue
            except OSError:
                continue
            files.append(path)
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    out = []
    for path in files:
        if limit is not None and len(out) >= limit:
            break
        try:
            size = path.stat().st_size
        except OSError:
            continue
        bill = min(size, CODEX_TAIL_BYTES) if size > MAX_FILE_BYTES else size
        if not _take_file(path, charge=bill):
            break
        burn, prompts = _parse_codex(path, titles)
        if prompts or burn.tools:
            out.append((burn, prompts))
    return out


def _codex_session_titles() -> dict[str, str]:
    names: dict[str, str] = {}
    for obj in _jsonl(home(".codex", "session_index.jsonl")):
        sid = str(obj.get("id") or "")
        if sid:
            names[sid] = str(obj.get("thread_name") or sid[:8])
    return names


def _codex_title(path: Path, titles: dict[str, str]) -> str:
    hit = re.search(
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$",
        path.stem,
        re.I,
    )
    if hit:
        return titles.get(hit.group(1), hit.group(1)[:8])
    return path.stem[8:27] if len(path.stem) > 27 else path.stem[:20]


def _copilot_chats(limit: int | None = None) -> list[tuple[ChatBurn, list[str]]]:
    if not roaming().is_dir():
        return []
    out: list[tuple[ChatBurn, list[str]]] = []
    seen: set[Path] = set()
    for ide in ("Code", "Cursor", "Windsurf", "Trae", "VSCodium"):
        base = roaming(ide, "User", "workspaceStorage")
        resolved = _resolve_root(base)
        if resolved is None:
            continue
        label = "Copilot" if ide == "Code" else f"Copilot ({ide})"
        files: list[Path] = []
        files.extend(_collect_files(resolved, "*/GitHub.copilot-chat/transcripts/*.jsonl"))
        files.extend(_collect_files(resolved, "*/chatSessions/*.jsonl"))
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        for path in files:
            if limit is not None and len(out) >= limit:
                return out
            if path in seen:
                continue
            seen.add(path)
            if not _take_file(path):
                return out
            if "transcripts" in path.parts:
                burn, prompts = _parse_copilot_transcript(path, label)
            else:
                burn, prompts = _parse_copilot_session(path, label)
            if not prompts:
                burn, prompts = _parse_transcript(path, label)
            if prompts or burn.tools:
                out.append((burn, prompts))
    return out


def _gemini_chats(limit: int | None = None) -> list[tuple[ChatBurn, list[str]]]:
    root = home(".gemini", "tmp")
    out: list[tuple[ChatBurn, list[str]]] = []
    files: list[Path] = []
    seen: set[Path] = set()
    for pattern in ("**/chats/*.jsonl", "**/chats/*.json"):
        for path in _collect_files(root, pattern):
            if path in seen:
                continue
            seen.add(path)
            files.append(path)
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    for path in files:
        if limit is not None and len(out) >= limit:
            break
        if not _take_file(path):
            break
        if path.suffix == ".json":
            burn, prompts = _parse_gemini_json(path)
        else:
            burn, prompts = _parse_gemini_jsonl(path)
        if prompts or burn.tools:
            out.append((burn, prompts))
    return out


def _parse_gemini_jsonl(path: Path) -> tuple[ChatBurn, list[str]]:
    prompts: list[str] = []
    tools: Counter[str] = Counter()
    chars = 0
    users = 0
    for obj in _jsonl(path):
        typ = obj.get("type")
        if typ == "user":
            blob = _join_parts(obj.get("content"))
            chars += len(blob)
            text = _user_text(blob) or blob.strip()
            if text:
                prompts.append(text)
                users += 1
        elif typ == "gemini":
            blob = _join_parts(obj.get("content"))
            chars += len(blob)
            for tr in obj.get("toolCalls") or []:
                if isinstance(tr, dict):
                    tools[str(tr.get("name") or tr.get("toolName") or "tool")] += 1
    top = ", ".join(f"{n}×{c}" for n, c in tools.most_common(3)) or "—"
    return ChatBurn("Gemini", path.stem[:8], users, sum(tools.values()), chars, top, _when(path), str(path)), prompts


def _parse_gemini_json(path: Path) -> tuple[ChatBurn, list[str]]:
    prompts: list[str] = []
    tools: Counter[str] = Counter()
    chars = 0
    users = 0
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return ChatBurn("Gemini", path.stem[:8], 0, 0, 0, "—", _when(path), str(path)), []
    messages = data.get("messages") if isinstance(data, dict) else None
    if not isinstance(messages, list):
        return ChatBurn("Gemini", path.stem[:8], 0, 0, 0, "—", _when(path), str(path)), []
    for msg in messages:
        if not isinstance(msg, dict) or msg.get("type") != "user":
            continue
        blob = _join_parts(msg.get("content"))
        chars += len(blob)
        text = _user_text(blob) or blob.strip()
        if text:
            prompts.append(text)
            users += 1
    top = ", ".join(f"{n}×{c}" for n, c in tools.most_common(3)) or "—"
    return ChatBurn("Gemini", path.stem[:8], users, sum(tools.values()), chars, top, _when(path), str(path)), prompts


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
    return ChatBurn(label, path.stem[:8], users, sum(tools.values()), chars, top, _when(path), str(path)), prompts


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
    return ChatBurn(label, path.stem[:8], users, sum(tools.values()), chars, top, _when(path), str(path)), prompts


def _continue_chats(limit: int | None = None) -> list[tuple[ChatBurn, list[str]]]:
    root = home(".continue", "sessions")
    out = []
    for path in _collect_files(root, "*.json"):
        if limit is not None and len(out) >= limit:
            break
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
        return ChatBurn("Continue", path.stem[:8], 0, 0, 0, "—", _when(path), str(path)), []
    history = data.get("history") if isinstance(data, dict) else data
    if not isinstance(history, list):
        return ChatBurn("Continue", path.stem[:8], 0, 0, 0, "—", _when(path), str(path)), []
    for turn in history:
        if not isinstance(turn, dict) or turn.get("role") != "user":
            continue
        blob = _join_parts(turn.get("content"))
        chars += len(blob)
        text = _user_text(blob)
        if text:
            prompts.append(text)
            users += 1
    return ChatBurn("Continue", path.stem[:8], users, 0, chars, "—", _when(path), str(path)), prompts


def _parse_codex(path: Path, titles: dict[str, str] | None = None) -> tuple[ChatBurn, list[str]]:
    titles = titles or {}
    prompts: list[str] = []
    tools: Counter[str] = Counter()
    chars = 0
    users = 0
    for obj in _iter_jsonl(path):
        if obj.get("type") != "response_item":
            continue
        pl = obj.get("payload") or {}
        kind = pl.get("type")
        if kind == "message":
            blob = _join_parts(pl.get("content"))
            chars += len(blob)
            if pl.get("role") == "user":
                text = _user_text(blob) or blob.strip()
                if text:
                    prompts.append(text)
                    users += 1
        elif kind in ("function_call", "custom_tool_call"):
            tools[str(pl.get("name") or kind)] += 1
    top = ", ".join(f"{n}×{c}" for n, c in tools.most_common(3)) or "—"
    return ChatBurn("Codex", _codex_title(path, titles), users, sum(tools.values()), chars, top, _when(path), str(path)), prompts


def _iter_jsonl(path: Path, *, max_lines: int = 6000):
    try:
        size = path.stat().st_size
    except OSError:
        return
    if size <= MAX_FILE_BYTES:
        yield from _jsonl(path, max_lines=max_lines)
        return
    yield from _jsonl_tail(path, max_lines=max_lines)


def _jsonl(path: Path, *, max_lines: int = 4000):
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return
        with path.open(encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh):
                if i >= max_lines:
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


def _jsonl_tail(path: Path, *, tail_bytes: int = CODEX_TAIL_BYTES, max_lines: int = 6000):
    try:
        size = path.stat().st_size
        with path.open("rb") as fh:
            start = max(0, size - tail_bytes)
            fh.seek(start)
            raw = fh.read().decode("utf-8", errors="replace")
    except OSError:
        return
    if start > 0:
        cut = raw.find("\n")
        if cut >= 0:
            raw = raw[cut + 1 :]
    seen = 0
    for line in raw.splitlines():
        if seen >= max_lines:
            break
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            yield json.loads(line)
            seen += 1
        except json.JSONDecodeError:
            continue


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


def _when(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).strftime("%d.%m %H:%M")
    except OSError:
        return ""


def _clip(text: str, n: int = 140) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1] + "…"


def _mcp_names() -> list[str]:
    names: set[str] = set()
    for path in (home(".cursor", "mcp.json"), roaming("Code", "User", "mcp.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        servers = data.get("mcpServers") or {}
        names.update(servers)
    return sorted(names)


def _skill_names() -> list[str]:
    names: list[str] = []
    for root in (home(".cursor", "skills"), home(".cursor", "skills-cursor"), home(".codex", "skills")):
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
    merged = _merge_findings(
        {
            "Cursor": [Finding("vague", "Cursor", "a"), Finding("vague", "Cursor", "b")],
            "Codex": [Finding("paste", "Codex", "c")],
        },
        3,
    )
    assert {f.source for f in merged} == {"Codex", "Cursor"}
    assert _when(Path(__file__))  # smoke: mtime format
    print("coach-ok")


if __name__ == "__main__":
    _demo()
