"""Ajan-kullanici bag ozeti: ilk gorulme, tahmini token, siklik, araclar.

ponytail: ajan basina en fazla STORY_PARSE dosya okunur; tum tarihce degil.
Token ~ chars/4 (yerel transcript tahmini; fatura API'si degil).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import time

from platform_util import home, roaming
from prompt_coach import (
    ChatBurn,
    _claude_chats,
    _codex_chats,
    _collect_files,
    _continue_chats,
    _copilot_chats,
    _cursor_chats,
    _gemini_chats,
)
import prompt_coach as pc

STORY_PARSE = 48  # ponytail: ceiling; upgrade = background index

_PROVIDER_SOURCE = {
    "CURSOR": "Cursor",
    "CODEX": "Codex",
    "CHATGPT": "Codex",
    "CLAUDE": "Claude",
    "GEMINI": "Gemini",
    "COPILOT": "Copilot",
    "GITHUB COPILOT": "Copilot",
    "CONTINUE": "Continue",
}

_SOURCE_ROOTS: dict[str, list[tuple[Path, str]]] = {
    "Cursor": [(home(".cursor", "projects"), "*/agent-transcripts/*/*.jsonl")],
    "Claude": [(home(".claude", "projects"), "*/*.jsonl")],
    "Codex": [(home(".codex", "sessions"), "**/*.jsonl")],
    "Gemini": [(home(".gemini", "tmp"), "**/*.jsonl")],
    "Copilot": [(home(".config", "gh"), "**/*.json")],
    "Continue": [(home(".continue", "sessions"), "**/*")],
}

_SOURCE_HOME: dict[str, list[Path]] = {
    "Cursor": [home(".cursor"), roaming("Cursor")],
    "Claude": [home(".claude")],
    "Codex": [home(".codex")],
    "Gemini": [home(".gemini")],
    "Copilot": [home(".config", "gh"), roaming("GitHub Copilot")],
    "Continue": [home(".continue")],
}


@dataclass
class AgentStory:
    source: str
    provider: str
    first_seen: str = ""
    first_ts: float = 0.0
    sessions: int = 0
    user_msgs: int = 0
    tool_calls: int = 0
    approx_tokens: int = 0
    days_active: int = 0
    per_week: float = 0.0
    top_tools: list[tuple[str, int]] = field(default_factory=list)
    recent: list[str] = field(default_factory=list)
    note: str = ""


def source_for_provider(name: str) -> str | None:
    return _PROVIDER_SOURCE.get(str(name).strip().upper())


def build_agent_story(provider_name: str, *, allow_chat: bool) -> AgentStory:
    source = source_for_provider(provider_name) or str(provider_name).title()
    story = AgentStory(source=source, provider=provider_name)
    first = _first_seen(source)
    if first:
        story.first_ts = first
        story.first_seen = datetime.fromtimestamp(first).strftime("%d.%m.%Y")
    if not allow_chat:
        story.note = "need_chat"
        return story
    burns = _load_burns(source)
    if not burns and not story.first_seen:
        story.note = "empty_data"
        return story
    if len(burns) >= STORY_PARSE:
        story.note = "truncated"
    _fill_from_burns(story, burns)
    return story


def _load_burns(source: str) -> list[ChatBurn]:
    loaders = {
        "Cursor": _cursor_chats,
        "Claude": _claude_chats,
        "Codex": _codex_chats,
        "Gemini": _gemini_chats,
        "Copilot": _copilot_chats,
        "Continue": _continue_chats,
    }
    loader = loaders.get(source)
    if not loader:
        return []
    pc._scan_started = time.monotonic()
    pc._scan_files = 0
    pc._scan_bytes = 0
    pc._scan_stop = False
    old_total = pc.MAX_TOTAL_BYTES
    try:
        pc.MAX_TOTAL_BYTES = min(old_total * 3, 24_000_000)
        pairs = loader(STORY_PARSE)
    finally:
        pc.MAX_TOTAL_BYTES = old_total
    return [b for b, _ in pairs]


def _fill_from_burns(story: AgentStory, burns: list[ChatBurn]) -> None:
    if not burns:
        return
    story.sessions = len(burns)
    story.user_msgs = sum(b.users for b in burns)
    story.tool_calls = sum(b.tools for b in burns)
    chars = sum(b.chars for b in burns)
    story.approx_tokens = max(0, chars // 4)
    tools: Counter[str] = Counter()
    days: set[str] = set()
    oldest = story.first_ts
    for b in burns:
        for name, n in _parse_tool_blob(b.top_tools):
            tools[name] += n
        ts = _path_mtime(b.path)
        if ts:
            days.add(datetime.fromtimestamp(ts).strftime("%Y-%m-%d"))
            if not oldest or ts < oldest:
                oldest = ts
    if oldest and (not story.first_ts or oldest < story.first_ts):
        story.first_ts = oldest
        story.first_seen = datetime.fromtimestamp(oldest).strftime("%d.%m.%Y")
    story.days_active = len(days)
    story.top_tools = tools.most_common(5)
    story.recent = [b.title for b in burns if b.title][:6]
    if story.first_ts:
        weeks = max((datetime.now().timestamp() - story.first_ts) / (7 * 86400), 1 / 7)
        story.per_week = round(story.sessions / weeks, 1)


def _parse_tool_blob(blob: str) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    if not blob or blob == "—":
        return out
    for part in blob.replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        if "×" in part:
            name, _, n = part.partition("×")
            try:
                out.append((name.strip() or "?", int(n.strip())))
                continue
            except ValueError:
                pass
        out.append((part, 1))
    return out


def _path_mtime(path: str) -> float:
    if not path:
        return 0.0
    try:
        return Path(path).stat().st_mtime
    except OSError:
        return 0.0


def _first_seen(source: str) -> float:
    best = 0.0
    for root, pattern in _SOURCE_ROOTS.get(source, []):
        best = _min_mtime(root, pattern, best)
    if best:
        return best
    for root in _SOURCE_HOME.get(source, []):
        try:
            if root.exists():
                st = root.stat()
                ts = float(getattr(st, "st_ctime", None) or st.st_mtime)
                if not best or ts < best:
                    best = ts
        except OSError:
            continue
    return best


def _min_mtime(root: Path, pattern: str, best: float) -> float:
    try:
        paths = list(_collect_files(root, pattern))[:200]
    except Exception:
        return best
    for path in paths:
        try:
            ts = path.stat().st_mtime
        except OSError:
            continue
        if not best or ts < best:
            best = ts
    return best
