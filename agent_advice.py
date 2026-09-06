"""Ajan başına token tasarrufu — kota + ajan tipine göre şahsi yorum.

ponytail: kural tablosu; LLM yok. Chat hikâyesi varsa ek sinyal.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from usage_client import ProviderUsage


def _lowest(provider: ProviderUsage) -> float | None:
    vals = [m.remaining_percent for m in provider.meters if m.remaining_percent is not None]
    return min(vals) if vals else None


@dataclass
class AdviceLine:
    key: str
    args: dict = field(default_factory=dict)


@dataclass
class AgentAdvice:
    name: str
    kind: str  # danger | warn | info
    status_key: str
    lines: list[AdviceLine]


def _family(name: str) -> str:
    key = name.upper()
    if key == "CURSOR":
        return "cursor"
    if key in ("CODEX", "CHATGPT"):
        return "codex"
    if key == "CLAUDE":
        return "claude"
    if key in ("COPILOT", "GITHUB COPILOT", "VS CODE"):
        return "copilot"
    if key == "GEMINI":
        return "gemini"
    if key in ("OLLAMA", "LM STUDIO"):
        return "local"
    if key == "MANUS":
        return "manus"
    return "generic"


def build_agent_advice(
    provider: ProviderUsage,
    *,
    warn_pct: float = 40,
    crit_pct: float = 15,
    story=None,
    kit=None,
) -> AgentAdvice:
    """Duruma göre 2–4 satırlık ajan özel tavsiye."""
    low = _lowest(provider)
    if low is not None and low < crit_pct:
        kind, status = "danger", "adv_status_crit"
    elif low is not None and low < warn_pct:
        kind, status = "warn", "adv_status_warn"
    elif provider.error:
        kind, status = "warn", "adv_status_err"
    else:
        kind, status = "info", "adv_status_ok"

    fam = _family(provider.name)
    lines: list[AdviceLine] = []

    if provider.error:
        lines.append(AdviceLine("adv_err_session"))
    if low is not None:
        lines.append(AdviceLine(f"adv_band_{kind}", {"pct": f"{low:.0f}"}))

    if kind == "danger":
        lines.append(AdviceLine(f"adv_{fam}_crit"))
    elif kind == "warn":
        lines.append(AdviceLine(f"adv_{fam}_warn"))
    else:
        lines.append(AdviceLine(f"adv_{fam}_ok"))

    if provider.plan:
        lines.append(AdviceLine("adv_plan", {"plan": provider.plan}))

    if kit is not None and getattr(kit, "addons", None):
        mcps = kit.by_kind("mcp") if hasattr(kit, "by_kind") else []
        rules = kit.by_kind("rule") if hasattr(kit, "by_kind") else []
        if len(mcps) >= 4:
            lines.append(AdviceLine(f"adv_{fam}_mcp_many", {"n": len(mcps)}))
        elif mcps and fam in ("cursor", "claude", "codex"):
            lines.append(AdviceLine(f"adv_{fam}_mcp_use", {"name": mcps[0].name}))
        if len(rules) >= 3 and fam == "cursor":
            lines.append(AdviceLine("adv_cursor_rules_trim", {"n": len(rules)}))

    if story is not None and getattr(story, "note", "") not in ("need_chat", "empty_data"):
        if getattr(story, "approx_tokens", 0) >= 200_000:
            lines.append(
                AdviceLine("adv_story_tokens", {"n": f"{story.approx_tokens:,}".replace(",", ".")})
            )
        if getattr(story, "user_msgs", 0) >= 40:
            lines.append(AdviceLine(f"adv_{fam}_long_chat"))
        tools = getattr(story, "top_tools", None) or []
        if tools:
            lines.append(AdviceLine(f"adv_{fam}_tool", {"tool": tools[0][0]}))

    seen: set[str] = set()
    uniq: list[AdviceLine] = []
    for line in lines:
        if line.key in seen:
            continue
        seen.add(line.key)
        uniq.append(line)
    return AgentAdvice(name=provider.name, kind=kind, status_key=status, lines=uniq[:4])
