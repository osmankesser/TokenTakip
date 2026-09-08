"""Sağlayıcı başına yalnız yerel konuşma dosyası sayısını bulur."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from platform_util import home, roaming

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
    "Codex": [
        (home(".codex", "sessions"), "**/rollout-*.jsonl"),
        (home(".codex", "archived_sessions"), "rollout-*.jsonl"),
    ],
    "Gemini": [
        (home(".gemini", "tmp"), "**/chats/*.jsonl"),
        (home(".gemini", "tmp"), "**/chats/*.json"),
    ],
    "Continue": [(home(".continue", "sessions"), "*.json")],
}
for _ide in ("Code", "Cursor", "Windsurf", "Trae", "VSCodium"):
    _copilot_root = roaming(_ide, "User", "workspaceStorage")
    _SOURCE_ROOTS.setdefault("Copilot", []).extend(
        [
            (_copilot_root, "*/GitHub.copilot-chat/transcripts/*.jsonl"),
            (_copilot_root, "*/chatSessions/*.jsonl"),
        ]
    )


@dataclass
class AgentStory:
    source: str
    provider: str
    sessions: int = 0
    note: str = ""


def source_for_provider(name: str) -> str | None:
    return _PROVIDER_SOURCE.get(str(name).strip().upper())


def build_agent_story(provider_name: str, *, allow_chat: bool) -> AgentStory:
    """Konuşma içeriklerini açmadan yerel oturum dosyalarını say."""
    del allow_chat  # Eski çağrılarla uyumluluk; sayaç içerik izni gerektirmez.
    source = source_for_provider(provider_name) or str(provider_name).title()
    story = AgentStory(source=source, provider=provider_name)
    story.sessions = _session_count(source)
    if not story.sessions:
        story.note = "empty_data"
    return story


def _session_count(source: str) -> int:
    files: set[Path] = set()
    for root, pattern in _SOURCE_ROOTS.get(source, []):
        try:
            files.update(path.resolve() for path in root.glob(pattern) if path.is_file())
        except OSError:
            continue
    return len(files)
