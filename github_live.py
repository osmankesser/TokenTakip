"""GitHub Top 100 — api.github.com’dan çek, önbelleğe yaz; kurulum rehberi üret.

ponytail: unauthenticated search (60/saat). Ağ yoksa weekly_projects yedek.
Kurulum metinleri README scrape değil; dil/kategori sezgisel şablon.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from platform_util import app_cache_dir
from usage_client import _SafeError, _json_get

CACHE_NAME = "github_top100.json"
CACHE_TTL_SEC = 6 * 3600  # 6 saat
TOP_N = 100

# Arama dilimleri — çeşitlilik; birleşince yıldız sırası
_SEARCH_QUERIES: tuple[str, ...] = (
    "topic:mcp stars:>30",
    "mcp-server stars:>50",
    "topic:ai-agents stars:>200",
    "topic:llm-agent stars:>100",
    "topic:langchain stars:>500",
    "cursorrules OR continue.dev stars:>100",
    "topic:rag stars:>500 language:Python",
    "topic:ollama stars:>200",
)


@dataclass
class LiveProject:
    rank: int
    repo: str
    title: str
    cat: str
    description: str
    stars: int = 0
    language: str = ""
    topics: tuple[str, ...] = ()
    source: str = "live"  # live | cache | fallback
    agents: tuple[str, ...] = ()
    mcp_tags: tuple[str, ...] = ()
    skill_tags: tuple[str, ...] = ()

    @property
    def url(self) -> str:
        return f"https://github.com/{self.repo}"

    @property
    def id(self) -> str:
        return self.repo.lower()


@dataclass
class ProjectGuide:
    what: str
    advantages: list[str]
    download: str
    terminal: str
    mcp: str
    extras: str = ""


def _cache_path() -> Path:
    return app_cache_dir() / CACHE_NAME


def _guess_cat(name: str, desc: str, topics: list[str]) -> str:
    blob = f"{name} {desc} {' '.join(topics)}".lower()
    if any(x in blob for x in ("mcp", "model-context-protocol", "modelcontextprotocol")):
        return "mcp"
    if any(x in blob for x in ("cursorrules", "prompt", "rule", "system-prompt")):
        return "rules"
    if any(x in blob for x in ("vscode", "ide", "extension", "continue", "cody", "tabby", "zed")):
        return "ide"
    if any(x in blob for x in ("cookbook", "course", "tutorial", "guide", "learn", "example", "eval")):
        return "learn"
    if any(x in blob for x in ("cli", "terminal", "aider", "ollama", "llama.cpp", "vllm", "shell")):
        return "cli"
    return "tools"


def _folder(repo: str) -> str:
    return repo.split("/")[-1] if "/" in repo else repo


def build_guide(proj: LiveProject, *, lang: str = "tr") -> ProjectGuide:
    """Kurulum / avantaj metinleri — TR veya EN."""
    folder = _folder(proj.repo)
    desc = (proj.description or "").strip()
    lang_l = (proj.language or "").lower()
    tr = lang.startswith("tr")

    if tr:
        what = desc or f"{proj.title} — GitHub’da açık kaynak ajan/AI aracı."
        advantages = [
            f"Topluluk yıldızı: {proj.stars:,}".replace(",", "."),
            f"Dil: {proj.language or 'çoklu'}",
            f"Kategori: {proj.cat}",
        ]
        if proj.topics:
            advantages.append("Konular: " + ", ".join(proj.topics[:6]))
        download = (
            f"1) Tarayıcıda kodu indir (ZIP) veya:\n"
            f"   git clone {proj.url}.git\n"
            f"2) Klasöre gir: cd {folder}\n"
            f"3) README’deki bağımlılıkları kur."
        )
        if lang_l == "python":
            terminal = (
                f"git clone {proj.url}.git\n"
                f"cd {folder}\n"
                f"python -m venv .venv\n"
                f".venv\\Scripts\\activate    # Windows\n"
                f"pip install -e .\n"
                f"# veya: pip install git+{proj.url}.git"
            )
        elif lang_l in ("typescript", "javascript"):
            terminal = (
                f"git clone {proj.url}.git\n"
                f"cd {folder}\n"
                f"npm install\n"
                f"npm run build   # varsa\n"
                f"# bazı paketler: npx -y {folder}"
            )
        elif lang_l == "go":
            terminal = (
                f"git clone {proj.url}.git\n"
                f"cd {folder}\n"
                f"go build ./...\n"
                f"# veya: go install {proj.repo}@latest"
            )
        elif lang_l == "rust":
            terminal = (
                f"git clone {proj.url}.git\n"
                f"cd {folder}\n"
                f"cargo build --release"
            )
        else:
            terminal = (
                f"git clone {proj.url}.git\n"
                f"cd {folder}\n"
                f"# README’deki kurulum komutlarını çalıştır"
            )
        if proj.cat == "mcp":
            mcp = (
                f"Cursor / Claude Desktop mcp.json örneği:\n"
                f'{{\n'
                f'  "mcpServers": {{\n'
                f'    "{folder}": {{\n'
                f'      "command": "npx",\n'
                f'      "args": ["-y", "{proj.repo}"]\n'
                f'    }}\n'
                f'  }}\n'
                f'}}\n'
                f"# Python MCP ise command: python, args: [\"path/to/server.py\"]\n"
                f"# Doğru komut için repo README’sine bak."
            )
            extras = "MCP: ayarı kaydet → ajanı yeniden başlat → araçları listede gör."
        else:
            mcp = "Bu proje MCP sunucusu değil — gerekmez. İstersen araç olarak CLI/SDK ile bağla."
            extras = ""
        if proj.cat == "ide":
            extras = (extras + "\n" if extras else "") + "IDE: VS Code/Cursor eklenti marketinden veya VSIX ile kur."
        if proj.cat == "rules":
            extras = (extras + "\n" if extras else "") + "Kurallar: uygun dosyayı .cursorrules veya .cursor/rules/ altına kopyala."
    else:
        what = desc or f"{proj.title} — open-source agent/AI tool on GitHub."
        advantages = [
            f"Community stars: {proj.stars:,}",
            f"Language: {proj.language or 'mixed'}",
            f"Category: {proj.cat}",
        ]
        if proj.topics:
            advantages.append("Topics: " + ", ".join(proj.topics[:6]))
        download = (
            f"1) Download ZIP in the browser, or:\n"
            f"   git clone {proj.url}.git\n"
            f"2) Enter folder: cd {folder}\n"
            f"3) Install deps from the README."
        )
        if lang_l == "python":
            terminal = (
                f"git clone {proj.url}.git\n"
                f"cd {folder}\n"
                f"python -m venv .venv && source .venv/bin/activate\n"
                f"pip install -e .\n"
                f"# or: pip install git+{proj.url}.git"
            )
        elif lang_l in ("typescript", "javascript"):
            terminal = (
                f"git clone {proj.url}.git\n"
                f"cd {folder}\n"
                f"npm install && npm run build\n"
                f"# some packages: npx -y {folder}"
            )
        elif lang_l == "go":
            terminal = f"git clone {proj.url}.git && cd {folder} && go build ./..."
        elif lang_l == "rust":
            terminal = f"git clone {proj.url}.git && cd {folder} && cargo build --release"
        else:
            terminal = f"git clone {proj.url}.git\ncd {folder}\n# follow README install steps"
        if proj.cat == "mcp":
            mcp = (
                f"Example mcp.json for Cursor / Claude Desktop:\n"
                f'{{\n  "mcpServers": {{\n    "{folder}": {{\n'
                f'      "command": "npx",\n      "args": ["-y", "{proj.repo}"]\n'
                f"    }}\n  }}\n}}\n"
                f"# Check README for the real command."
            )
            extras = "Save MCP config → restart agent → confirm tools appear."
        else:
            mcp = "Not an MCP server — skip mcp.json; use as CLI/SDK instead."
            extras = ""

    return ProjectGuide(
        what=what,
        advantages=advantages,
        download=download,
        terminal=terminal,
        mcp=mcp,
        extras=extras,
    )


def _search(q: str, *, per_page: int = 30) -> list[dict[str, Any]]:
    url = (
        "https://api.github.com/search/repositories"
        f"?q={quote_plus(q)}&sort=stars&order=desc&per_page={per_page}"
    )
    data = _json_get(url, {"Accept": "application/vnd.github+json", "User-Agent": "TokenTracker"})
    items = data.get("items") if isinstance(data, dict) else None
    return [x for x in (items or []) if isinstance(x, dict)]


def _item_to_proj(item: dict[str, Any], rank: int, source: str) -> LiveProject | None:
    full = str(item.get("full_name") or "").strip()
    if "/" not in full:
        return None
    topics = [str(t) for t in (item.get("topics") or []) if t][:12]
    desc = str(item.get("description") or "").strip()
    name = str(item.get("name") or full.split("/")[-1])
    cat = _guess_cat(name, desc, topics)
    stars = int(item.get("stargazers_count") or 0)
    language = str(item.get("language") or "")
    return LiveProject(
        rank=rank,
        repo=full,
        title=name,
        cat=cat,
        description=desc,
        stars=stars,
        language=language,
        topics=tuple(topics),
        source=source,
        agents=("cursor", "claude", "codex"),
        mcp_tags=("mcp",) if cat == "mcp" else (),
    )


def _fallback_from_catalog() -> list[LiveProject]:
    from weekly_projects import CATALOG

    out: list[LiveProject] = []
    for p in CATALOG[:TOP_N]:
        text = p.text("en")
        out.append(
            LiveProject(
                rank=p.rank or (len(out) + 1),
                repo=p.repo,
                title=p.title,
                cat=p.cat,
                description=text.what,
                stars=0,
                language="",
                topics=(),
                source="fallback",
                agents=p.agents,
                mcp_tags=p.mcp_tags,
                skill_tags=p.skill_tags,
            )
        )
    return out


def _save_cache(projects: list[LiveProject]) -> None:
    path = _cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "items": [
            {
                "rank": p.rank,
                "repo": p.repo,
                "title": p.title,
                "cat": p.cat,
                "description": p.description,
                "stars": p.stars,
                "language": p.language,
                "topics": list(p.topics),
            }
            for p in projects
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _load_cache(*, max_age: float | None = CACHE_TTL_SEC) -> list[LiveProject] | None:
    path = _cache_path()
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        fetched = raw.get("fetched_at") or ""
        if max_age is not None and fetched:
            ts = datetime.fromisoformat(fetched.replace("Z", "+00:00")).timestamp()
            if time.time() - ts > max_age:
                return None
        items = raw.get("items") or []
        out: list[LiveProject] = []
        for i, it in enumerate(items, start=1):
            if not isinstance(it, dict):
                continue
            out.append(
                LiveProject(
                    rank=int(it.get("rank") or i),
                    repo=str(it["repo"]),
                    title=str(it.get("title") or it["repo"].split("/")[-1]),
                    cat=str(it.get("cat") or "tools"),
                    description=str(it.get("description") or ""),
                    stars=int(it.get("stars") or 0),
                    language=str(it.get("language") or ""),
                    topics=tuple(it.get("topics") or ()),
                    source="cache",
                )
            )
        return out[:TOP_N] if out else None
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def projects_instant() -> list[LiveProject]:
    """UI için anında: önbellek (süresi dolmuş olsa da) veya sabit yedek — ağ yok."""
    return _load_cache(max_age=None) or _fallback_from_catalog()


def fetch_top_projects(*, force: bool = False) -> list[LiveProject]:
    """Canlı ara; başarısızsa önbellek / sabit katalog."""
    if not force:
        cached = _load_cache()
        if cached:
            return cached
    by_repo: dict[str, dict[str, Any]] = {}
    try:
        for q in _SEARCH_QUERIES:
            for item in _search(q, per_page=25):
                full = str(item.get("full_name") or "")
                if not full or full in by_repo:
                    continue
                by_repo[full] = item
            time.sleep(0.35)  # nazik rate limit
    except _SafeError:
        stale = _load_cache(max_age=None)
        return stale if stale else _fallback_from_catalog()
    except Exception:
        stale = _load_cache(max_age=None)
        return stale if stale else _fallback_from_catalog()

    ranked = sorted(
        by_repo.values(),
        key=lambda x: int(x.get("stargazers_count") or 0),
        reverse=True,
    )[:TOP_N]
    projects: list[LiveProject] = []
    for i, item in enumerate(ranked, start=1):
        p = _item_to_proj(item, i, "live")
        if p:
            projects.append(p)
    if len(projects) < 20:
        # Zayıf sonuç — yedekle doldur
        have = {p.repo.lower() for p in projects}
        for fb in _fallback_from_catalog():
            if fb.repo.lower() in have:
                continue
            projects.append(
                LiveProject(
                    rank=0,
                    repo=fb.repo,
                    title=fb.title,
                    cat=fb.cat,
                    description=fb.description,
                    stars=fb.stars,
                    language=fb.language,
                    topics=fb.topics,
                    source="fallback",
                    agents=fb.agents,
                    mcp_tags=fb.mcp_tags,
                    skill_tags=fb.skill_tags,
                )
            )
            if len(projects) >= TOP_N:
                break
        for i, p in enumerate(projects[:TOP_N], start=1):
            projects[i - 1] = replace(p, rank=i)
        projects = projects[:TOP_N]
    if projects:
        try:
            _save_cache(projects)
        except OSError:
            pass
    return projects or _fallback_from_catalog()


def ranked_live(
    projects: list[LiveProject] | None,
    *,
    cat: str | None = None,
) -> list[LiveProject]:
    rows = list(projects or [])
    if cat and cat != "all":
        rows = [p for p in rows if p.cat == cat]
    rows.sort(key=lambda p: (p.rank or 9999, -p.stars, p.title))
    return rows


def get_project(projects: list[LiveProject], repo: str) -> LiveProject | None:
    key = repo.lower()
    for p in projects:
        if p.repo.lower() == key or p.id == key:
            return p
    return None


def localize_blurb(text: str, lang: str) -> str:
    """GitHub açıklamasını UI diline çevir (önbellekli; ağ yoksa orijinal)."""
    from auto_translate import normalize_lang, translate

    raw = (text or "").strip()
    if not raw:
        return ""
    dest = normalize_lang(lang)
    if dest == "en":
        return raw
    return translate(raw, dest)


def localize_guide(guide: ProjectGuide, lang: str) -> ProjectGuide:
    """Rehber düzyazısını UI diline çevir; terminal/indir komutlarını koru."""
    from auto_translate import normalize_lang, translate

    dest = normalize_lang(lang)
    if dest == "en":
        return guide
    # TR şablonları zaten TR — sadece what hâlâ EN API metni olabilir
    if dest == "tr":
        return ProjectGuide(
            what=translate(guide.what, "tr"),
            advantages=guide.advantages,
            download=guide.download,
            terminal=guide.terminal,
            mcp=guide.mcp,
            extras=guide.extras,
        )
    return ProjectGuide(
        what=translate(guide.what, dest),
        advantages=[translate(a, dest) for a in guide.advantages],
        download=guide.download,
        terminal=guide.terminal,
        mcp=guide.mcp,
        extras=translate(guide.extras, dest) if guide.extras else "",
    )
