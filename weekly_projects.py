"""Ajan GitHub Top 100 — çevrimdışı seçilmiş katalog.

ponytail: canlı trending yok; ağ yok. Sıra elle; sürümle güncellenir.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


AGENT_LABEL = {
    "cursor": "Cursor",
    "claude": "Claude",
    "codex": "Codex",
    "copilot": "Copilot",
    "gemini": "Gemini",
    "vscode": "VS Code",
    "aider": "Aider",
    "cli": "CLI",
    "jetbrains": "JetBrains",
    "docker": "Docker",
}

_PROVIDER_AGENT = {
    "CURSOR": "cursor",
    "CODEX": "codex",
    "CLAUDE": "claude",
    "GEMINI": "gemini",
    "GITHUB COPILOT": "copilot",
    "COPILOT": "copilot",
}

CAT_ORDER: tuple[str, ...] = ("mcp", "ide", "cli", "rules", "tools", "learn")


@dataclass(frozen=True)
class ProjectText:
    what: str
    pros: str = ""
    cons: str = ""


@dataclass(frozen=True)
class WeeklyProject:
    id: str
    repo: str
    title: str
    agents: tuple[str, ...]
    texts: dict[str, ProjectText]
    cat: str = "tools"
    rank: int = 0
    mcp_tags: tuple[str, ...] = ()
    skill_tags: tuple[str, ...] = ()

    @property
    def url(self) -> str:
        return f"https://github.com/{self.repo}"

    def text(self, lang: str) -> ProjectText:
        return self.texts.get(lang) or self.texts["en"]


@dataclass
class ProjectFit:
    project: WeeklyProject
    score: int
    matched_agents: list[str] = field(default_factory=list)
    missing_agents: list[str] = field(default_factory=list)
    matched_helpers: list[str] = field(default_factory=list)
    kind: str = "gap"  # fit | partial | gap


def _t(tr_what: str, en_what: str) -> dict[str, ProjectText]:
    return {"tr": ProjectText(tr_what), "en": ProjectText(en_what)}


def _p(
    repo: str,
    title: str,
    cat: str,
    tr: str,
    en: str,
    agents: tuple[str, ...] = ("cursor", "claude", "codex"),
    *,
    mcp: tuple[str, ...] = (),
    skill: tuple[str, ...] = (),
) -> tuple:
    return (repo, title, cat, tr, en, agents, mcp, skill)


# repo, title, cat, tr, en, agents, mcp, skill — sıra = Top 100 rank
_TOP_ROWS: tuple[tuple, ...] = (
    _p("modelcontextprotocol/servers", "MCP Servers", "mcp",
       "Resmi MCP sunucu örnekleri — dosya, git, web araçları.",
       "Official MCP server examples — file, git, web tools.",
       ("cursor", "claude", "codex", "vscode"), mcp=("filesystem", "github")),
    _p("punkpeye/awesome-mcp-servers", "Awesome MCP Servers", "mcp",
       "Topluluk MCP listesi — ihtiyacına uygun sunucu keşfi.",
       "Community MCP catalog — discover useful servers.",
       ("cursor", "claude", "codex", "vscode"), mcp=("mcp",)),
    _p("continuedev/continue", "Continue", "ide",
       "Açık kaynak IDE asistanı — kendi modelinle sohbet/autocomplete.",
       "Open-source IDE assistant — chat and autocomplete.",
       ("vscode", "cursor", "jetbrains")),
    _p("Aider-AI/aider", "Aider", "cli",
       "Terminalde git-aware kod ajanı — diff ve commit.",
       "Git-aware terminal coding agent — diffs and commits.",
       ("aider", "cli", "codex", "claude")),
    _p("All-Hands-AI/OpenHands", "OpenHands", "cli",
       "Sandbox’ta adım adım görev yürüten yazılım ajanı.",
       "Software agent that runs tasks step-by-step in a sandbox.",
       ("cli", "docker", "claude", "codex")),
    _p("anthropics/anthropic-cookbook", "Anthropic Cookbook", "learn",
       "Claude için resmi örnekler — tool use, RAG, ajan kalıpları.",
       "Official Claude examples — tools, RAG, agent patterns.",
       ("claude", "cursor", "codex")),
    _p("PatrickJS/awesome-cursorrules", "Awesome Cursor Rules", "rules",
       "Hazır .cursorrules örnekleri — proje kuralları.",
       "Ready-made .cursorrules — project rules for agents.",
       ("cursor",), skill=("create-rule",)),
    _p("browser-use/browser-use", "Browser Use", "tools",
       "Ajanın tarayıcıyı kullanmasını sağlar.",
       "Lets agents drive a browser for forms and scraping.",
       ("cli", "claude", "codex", "cursor"), mcp=("browser",)),
    _p("google-gemini/gemini-cli", "Gemini CLI", "cli",
       "Google’ın terminal Gemini aracı.",
       "Google’s terminal Gemini tool for code and files.",
       ("gemini", "cli")),
    _p("github/copilot-sdk", "GitHub Copilot SDK", "tools",
       "Copilot’u araçlarına gömmek için SDK.",
       "SDK to embed Copilot into your own tools.",
       ("copilot", "vscode", "cli")),
    _p("charmbracelet/crush", "Crush", "cli",
       "TUI’li çoklu model kod ajanı.",
       "Polished TUI coding agent — multi-model chat.",
       ("cli", "codex", "claude")),
    _p("yamadashy/repomix", "Repomix", "tools",
       "Repoyu tek dosyada paketler — kontrollü ajan bağlamı.",
       "Packs a repo into one file for agent context.",
       ("cursor", "claude", "codex", "copilot", "cli")),
    _p("langchain-ai/langchain", "LangChain", "tools",
       "LLM uygulama çerçevesi — zincir, araç, bellek.",
       "LLM app framework — chains, tools, memory.",
       ("cli", "claude", "codex", "cursor")),
    _p("langchain-ai/langgraph", "LangGraph", "tools",
       "Durumlu ajan grafikleri — LangChain üstü.",
       "Stateful agent graphs on top of LangChain.",
       ("cli", "claude", "codex")),
    _p("run-llama/llama_index", "LlamaIndex", "tools",
       "RAG ve veri ajanları için indeksleme.",
       "Indexing framework for RAG and data agents.",
       ("cli", "claude", "cursor")),
    _p("openai/openai-agents-python", "OpenAI Agents", "tools",
       "OpenAI’nin Python ajan SDK’sı.",
       "OpenAI’s Python agents SDK.",
       ("codex", "cli", "cursor")),
    _p("openai/swarm", "Swarm", "learn",
       "Hafif çoklu ajan orkestrasyon örneği.",
       "Lightweight multi-agent orchestration examples.",
       ("codex", "cli", "claude")),
    _p("microsoft/autogen", "AutoGen", "tools",
       "Microsoft çoklu ajan konuşma çerçevesi.",
       "Microsoft multi-agent conversation framework.",
       ("cli", "copilot", "codex")),
    _p("crewAIInc/crewAI", "CrewAI", "tools",
       "Rol tabanlı ajan ekipleri.",
       "Role-playing autonomous agent crews.",
       ("cli", "claude", "codex")),
    _p("Significant-Gravitas/AutoGPT", "AutoGPT", "cli",
       "Otonom hedef peşinde koşan ajan deneyleri.",
       "Autonomous goal-driven agent experiments.",
       ("cli", "docker", "codex")),
    _p("geekan/MetaGPT", "MetaGPT", "cli",
       "Yazılım şirketi simülasyonu — çoklu ajan.",
       "Multi-agent software company simulation.",
       ("cli", "claude", "codex")),
    _p("OpenBMB/ChatDev", "ChatDev", "learn",
       "Sohbetle yazılım üreten ajan ekibi.",
       "Chat-powered multi-agent software company.",
       ("cli", "claude", "codex")),
    _p("BerriAI/litellm", "LiteLLM", "tools",
       "100+ LLM’i tek API’de birleştirir.",
       "One API for 100+ LLM providers.",
       ("cli", "cursor", "codex", "claude")),
    _p("ollama/ollama", "Ollama", "cli",
       "Yerel modelleri kolay çalıştır.",
       "Run local models easily.",
       ("cli", "cursor", "vscode")),
    _p("ggerganov/llama.cpp", "llama.cpp", "cli",
       "CPU/GPU’da hızlı yerel LLM çıkarımı.",
       "Fast local LLM inference on CPU/GPU.",
       ("cli",)),
    _p("huggingface/transformers", "Transformers", "learn",
       "HF model ve pipeline ekosistemi.",
       "Hugging Face models and pipelines.",
       ("cli", "cursor", "codex")),
    _p("huggingface/smolagents", "smolagents", "tools",
       "Küçük, sade ajan kütüphanesi.",
       "Tiny, simple agent library from HF.",
       ("cli", "claude", "codex")),
    _p("instructor-ai/instructor", "Instructor", "tools",
       "Yapılandırılmış LLM çıktısı (Pydantic).",
       "Structured LLM outputs with Pydantic.",
       ("cli", "codex", "claude", "cursor")),
    _p("pydantic/pydantic-ai", "PydanticAI", "tools",
       "Tip güvenli ajan ve araç çağrıları.",
       "Type-safe agents and tool calling.",
       ("cli", "codex", "claude")),
    _p("dspy-ai/dspy", "DSPy", "learn",
       "Prompt’u programla — derle, optimize et.",
       "Program prompts — compile and optimize.",
       ("cli", "cursor", "codex")),
    _p("microsoft/semantic-kernel", "Semantic Kernel", "tools",
       "Microsoft AI orkestrasyon SDK’sı.",
       "Microsoft AI orchestration SDK.",
       ("cli", "copilot", "codex")),
    _p("vercel/ai", "Vercel AI SDK", "tools",
       "Web uygulamaları için AI SDK.",
       "AI SDK for web apps and streaming UI.",
       ("cli", "cursor", "copilot")),
    _p("openai/openai-python", "OpenAI Python", "learn",
       "Resmi OpenAI Python istemcisi.",
       "Official OpenAI Python client.",
       ("codex", "cli", "cursor")),
    _p("anthropics/anthropic-sdk-python", "Anthropic SDK", "learn",
       "Resmi Anthropic Python SDK.",
       "Official Anthropic Python SDK.",
       ("claude", "cli", "cursor")),
    _p("google/adk-python", "Google ADK", "tools",
       "Google Agent Development Kit.",
       "Google Agent Development Kit for Python.",
       ("gemini", "cli", "codex")),
    _p("lastmile-ai/mcp-agent", "mcp-agent", "mcp",
       "MCP odaklı ajan oluşturma.",
       "Build agents centered on MCP.",
       ("cursor", "claude", "codex"), mcp=("mcp",)),
    _p("mark3labs/mcp-go", "MCP Go", "mcp",
       "Go ile MCP sunucu/istemci.",
       "MCP servers and clients in Go.",
       ("cli", "cursor", "codex"), mcp=("mcp",)),
    _p("modelcontextprotocol/python-sdk", "MCP Python SDK", "mcp",
       "Resmi MCP Python SDK.",
       "Official MCP Python SDK.",
       ("cursor", "claude", "codex", "cli"), mcp=("mcp",)),
    _p("modelcontextprotocol/typescript-sdk", "MCP TypeScript SDK", "mcp",
       "Resmi MCP TypeScript SDK.",
       "Official MCP TypeScript SDK.",
       ("cursor", "vscode", "cli"), mcp=("mcp",)),
    _p("getzep/graphiti", "Graphiti", "tools",
       "Zaman-farkında bilgi grafiği bellek.",
       "Temporal knowledge-graph memory for agents.",
       ("cli", "claude", "codex")),
    _p("mem0ai/mem0", "Mem0", "tools",
       "Ajanlar için bellek katmanı.",
       "Memory layer for AI agents.",
       ("cli", "claude", "codex", "cursor")),
    _p("Chroma-Core/chroma", "Chroma", "tools",
       "Gömme vektör veritabanı — RAG.",
       "Embedding vector database for RAG.",
       ("cli", "cursor", "claude")),
    _p("qdrant/qdrant", "Qdrant", "tools",
       "Yüksek performanslı vektör arama.",
       "High-performance vector search engine.",
       ("cli", "docker", "cursor")),
    _p("weaviate/weaviate", "Weaviate", "tools",
       "Vektör + hibrit arama veritabanı.",
       "Vector and hybrid search database.",
       ("cli", "docker", "cursor")),
    _p("milvus-io/milvus", "Milvus", "tools",
       "Ölçeklenebilir vektör veritabanı.",
       "Scalable open-source vector database.",
       ("cli", "docker")),
    _p("infiniflow/ragflow", "RAGFlow", "tools",
       "RAG motoru — belge anlama odaklı.",
       "RAG engine focused on document understanding.",
       ("cli", "docker", "cursor")),
    _p("danswer-ai/danswer", "Onyx (Danswer)", "tools",
       "Kurumsal arama + sohbet.",
       "Open-source enterprise QA and chat.",
       ("cli", "docker", "copilot")),
    _p("nomic-ai/gpt4all", "GPT4All", "cli",
       "Yerel masaüstü LLM uygulaması.",
       "Local desktop LLM chat app.",
       ("cli", "vscode")),
    _p("oobabooga/text-generation-webui", "Text Gen WebUI", "cli",
       "Yerel LLM web arayüzü.",
       "Local LLM web UI with many backends.",
       ("cli",)),
    _p("comfyanonymous/ComfyUI", "ComfyUI", "tools",
       "Node tabanlı görüntü üretim arayüzü.",
       "Node-based UI for generative image workflows.",
       ("cli", "cursor")),
    _p("AUTOMATIC1111/stable-diffusion-webui", "SD WebUI", "tools",
       "Klasik Stable Diffusion web UI.",
       "Classic Stable Diffusion web UI.",
       ("cli",)),
    _p("guidance-ai/guidance", "Guidance", "learn",
       "Kontrollü dil modeli programlama.",
       "Control language model generation with programs.",
       ("cli", "codex", "claude")),
    _p("outlines-dev/outlines", "Outlines", "tools",
       "Yapılandırılmış üretim — JSON/regex.",
       "Structured generation — JSON and regex.",
       ("cli", "codex", "claude")),
    _p("PrefectHQ/marvin", "Marvin", "tools",
       "AI fonksiyonları ve sınıflandırıcılar.",
       "AI functions, classifiers, and bots.",
       ("cli", "cursor", "codex")),
    _p("assafelovic/gpt-researcher", "GPT Researcher", "cli",
       "Derin araştırma ajanı.",
       "Autonomous deep research agent.",
       ("cli", "claude", "codex")),
    _p("bytedance/UI-TARS", "UI-TARS", "tools",
       "GUI ajanı — ekranı anla ve tıkla.",
       "GUI agent — understand and act on screens.",
       ("cli", "claude", "cursor")),
    _p("xlang-ai/OSWorld", "OSWorld", "learn",
       "Bilgisayar kullanım ajanları değerlendirme.",
       "Benchmark for computer-use agents.",
       ("cli", "claude", "codex")),
    _p("web-arena-x/webarena", "WebArena", "learn",
       "Web ajanı değerlendirme ortamı.",
       "Web agent evaluation environment.",
       ("cli", "claude", "codex")),
    _p("princeton-nlp/SWE-agent", "SWE-agent", "cli",
       "GitHub issue çözen yazılım ajanı.",
       "Software engineering agent for GitHub issues.",
       ("cli", "codex", "claude")),
    _p("Codium-ai/Cover-Agent", "Cover Agent", "cli",
       "Test kapsamı üreten ajan.",
       "Agent that generates unit test coverage.",
       ("cli", "codex", "copilot", "cursor")),
    _p("voideditor/void", "Void", "ide",
       "Açık kaynak Cursor benzeri editör.",
       "Open-source Cursor-like editor.",
       ("vscode", "cursor", "cli")),
    _p("zed-industries/zed", "Zed", "ide",
       "Hızlı işbirlikçi kod editörü.",
       "High-performance collaborative code editor.",
       ("cli", "cursor")),
    _p("microsoft/vscode", "VS Code", "ide",
       "Eklenti ekosisteminin temeli.",
       "Foundation of the extension ecosystem.",
       ("vscode", "copilot", "cursor")),
    _p("TabbyML/tabby", "Tabby", "ide",
       "Kendi barındırdığın kod tamamlama.",
       "Self-hosted coding assistant / completions.",
       ("vscode", "cli", "jetbrains")),
    _p("sourcegraph/cody", "Cody", "ide",
       "Sourcegraph kod AI asistanı.",
       "Sourcegraph code AI assistant.",
       ("vscode", "jetbrains", "cli")),
    _p("cline/cline", "Cline", "ide",
       "VS Code’da otonom kod ajanı eklentisi.",
       "Autonomous coding agent extension for VS Code.",
       ("vscode", "cursor", "claude")),
    _p("RooCodeInc/Roo-Code", "Roo Code", "ide",
       "VS Code ajan eklentisi (Cline ailesi).",
       "VS Code agent extension in the Cline family.",
       ("vscode", "claude", "cursor")),
    _p("anthropics/claude-code", "Claude Code", "cli",
       "Anthropic’in terminal kod ajanı.",
       "Anthropic’s terminal coding agent.",
       ("claude", "cli")),
    _p("openai/codex", "Codex CLI", "cli",
       "OpenAI Codex komut satırı ajanı.",
       "OpenAI Codex command-line agent.",
       ("codex", "cli")),
    _p("google-gemini/cookbook", "Gemini Cookbook", "learn",
       "Gemini resmi örnek defteri.",
       "Official Gemini cookbook examples.",
       ("gemini", "cli", "cursor")),
    _p("microsoft/generative-ai-for-beginners", "GenAI Beginners", "learn",
       "Üretken AI başlangıç kursu.",
       "Beginner course for generative AI.",
       ("copilot", "cli", "cursor")),
    _p("dair-ai/Prompt-Engineering-Guide", "Prompt Guide", "learn",
       "Prompt mühendisliği rehberi.",
       "Prompt engineering guide and papers.",
       ("cursor", "claude", "codex", "copilot")),
    _p("f/awesome-chatgpt-prompts", "Awesome ChatGPT Prompts", "rules",
       "Hazır prompt koleksiyonu.",
       "Curated ChatGPT prompt collection.",
       ("codex", "cursor", "claude")),
    _p("awesome-cursorrules/awesome-cursorrules", "Cursor Rules Hub", "rules",
       "Cursor kural listeleri derlemesi.",
       "Hub of Cursor rules collections.",
       ("cursor",), skill=("create-rule",)),
    _p("snwfdhmp/awesome-gpt-prompt-engineering", "Awesome Prompt Eng", "rules",
       "Prompt mühendisliği bağlantıları.",
       "Awesome list for prompt engineering.",
       ("cursor", "claude", "codex")),
    _p("langchain-ai/opengpts", "OpenGPTs", "learn",
       "LangChain GPT benzeri uygulama örnekleri.",
       "LangChain GPT-like app examples.",
       ("cli", "codex", "claude")),
    _p("FlowiseAI/Flowise", "Flowise", "tools",
       "Sürükle-bırak LLM akış oluşturucu.",
       "Drag-and-drop LLM flow builder.",
       ("cli", "docker", "cursor")),
    _p("langgenius/dify", "Dify", "tools",
       "LLM uygulama platformu — RAG + ajan.",
       "LLM app platform — RAG and agents.",
       ("cli", "docker", "cursor")),
    _p("n8n-io/n8n", "n8n", "tools",
       "İş akışı otomasyonu — AI düğümleri.",
       "Workflow automation with AI nodes.",
       ("cli", "docker", "copilot")),
    _p("Activepieces/activepieces", "Activepieces", "tools",
       "Açık kaynak otomasyon / AI parçaları.",
       "Open-source automation with AI pieces.",
       ("cli", "docker")),
    _p("composiohq/composio", "Composio", "mcp",
       "Ajanlara 100+ araç bağlama.",
       "Connect agents to 100+ tools.",
       ("cursor", "claude", "codex", "cli"), mcp=("composio",)),
    _p("zapier/zapier-mcp", "Zapier MCP", "mcp",
       "Zapier eylemlerini MCP olarak sunar.",
       "Expose Zapier actions as MCP tools.",
       ("cursor", "claude", "codex"), mcp=("zapier",)),
    _p("supabase/mcp", "Supabase MCP", "mcp",
       "Supabase için MCP sunucusu.",
       "MCP server for Supabase.",
       ("cursor", "claude", "vscode"), mcp=("supabase",)),
    _p("github/github-mcp-server", "GitHub MCP", "mcp",
       "GitHub işlemleri için MCP.",
       "MCP server for GitHub operations.",
       ("cursor", "copilot", "codex"), mcp=("github",)),
    _p("microsoft/playwright-mcp", "Playwright MCP", "mcp",
       "Tarayıcı otomasyonu MCP.",
       "Browser automation via MCP.",
       ("cursor", "claude", "codex"), mcp=("playwright", "browser")),
    _p("anthropics/courses", "Anthropic Courses", "learn",
       "Anthropic eğitim kursları.",
       "Anthropic educational courses.",
       ("claude", "cursor")),
    _p("openai/openai-cookbook", "OpenAI Cookbook", "learn",
       "OpenAI resmi örnekler.",
       "Official OpenAI cookbook examples.",
       ("codex", "cli", "cursor")),
    _p("microsoft/ai-agents-for-beginners", "AI Agents Beginners", "learn",
       "Ajanlara giriş dersleri.",
       "Beginner lessons on AI agents.",
       ("copilot", "cli", "cursor")),
    _p("e2b-dev/E2B", "E2B", "tools",
       "Ajanlar için güvenli kod sandbox’ı.",
       "Secure code sandboxes for AI agents.",
       ("cli", "claude", "codex", "cursor")),
    _p("modal-labs/modal-examples", "Modal Examples", "learn",
       "Bulutta ajan/LLM çalıştırma örnekleri.",
       "Cloud examples for running LLMs and agents.",
       ("cli", "codex", "cursor")),
    _p("vllm-project/vllm", "vLLM", "cli",
       "Yüksek hızlı LLM sunucusu.",
       "High-throughput LLM serving engine.",
       ("cli", "docker")),
    _p("sgl-project/sglang", "SGLang", "cli",
       "Hızlı yapılandırılmış LLM serving.",
       "Fast structured LLM serving runtime.",
       ("cli", "docker")),
    _p("unslothai/unsloth", "Unsloth", "learn",
       "Hızlı LoRA / fine-tune.",
       "Fast LoRA fine-tuning toolkit.",
       ("cli", "cursor")),
    _p("axolotl-ai-cloud/axolotl", "Axolotl", "learn",
       "LLM fine-tune yapılandırmaları.",
       "LLM fine-tuning configurations.",
       ("cli", "cursor")),
    _p("EleutherAI/lm-evaluation-harness", "LM Eval Harness", "learn",
       "Model değerlendirme standardı.",
       "Standard harness for evaluating LMs.",
       ("cli", "codex")),
    _p("confident-ai/deepeval", "DeepEval", "learn",
       "LLM test / değerlendirme çerçevesi.",
       "LLM testing and evaluation framework.",
       ("cli", "cursor", "codex")),
    _p("braintrustdata/autoevals", "Autoevals", "learn",
       "LLM çıktı skorlayıcıları.",
       "Scorers for LLM outputs.",
       ("cli", "codex", "claude")),
    _p("promptfoo/promptfoo", "Promptfoo", "tools",
       "Prompt test ve red-team.",
       "Prompt testing and red-teaming.",
       ("cli", "cursor", "codex")),
    _p("langfuse/langfuse", "Langfuse", "tools",
       "LLM gözlemlenebilirlik / izleme.",
       "LLM observability and tracing.",
       ("cli", "docker", "cursor")),
    _p("traceloop/openllmetry", "OpenLLMetry", "tools",
       "OpenTelemetry ile LLM izleme.",
       "OpenTelemetry-based LLM observability.",
       ("cli", "cursor", "codex")),
)


def _build_catalog() -> tuple[WeeklyProject, ...]:
    out: list[WeeklyProject] = []
    for i, row in enumerate(_TOP_ROWS, start=1):
        repo, title, cat, tr, en, agents, mcp, skill = row
        out.append(
            WeeklyProject(
                id=f"top{i:03d}",
                repo=repo,
                title=title,
                cat=cat,
                rank=i,
                agents=agents,
                mcp_tags=mcp,
                skill_tags=skill,
                texts=_t(tr, en),
            )
        )
    return tuple(out)


CATALOG: tuple[WeeklyProject, ...] = _build_catalog()


def agents_from_providers(names: list[str] | None) -> set[str]:
    out: set[str] = set()
    for raw in names or []:
        key = str(raw).strip().upper()
        if key in _PROVIDER_AGENT:
            out.add(_PROVIDER_AGENT[key])
        else:
            for token, agent in _PROVIDER_AGENT.items():
                if token in key:
                    out.add(agent)
    return out


def detect_local_agents() -> set[str]:
    """Kurulu araç izleri (klasör) — sohbet izni gerekmez."""
    home = Path.home()
    found: set[str] = set()
    if (home / ".cursor").exists() or (home / "AppData" / "Roaming" / "Cursor").exists():
        found.add("cursor")
    if (home / ".claude").exists():
        found.add("claude")
    if (home / ".codex").exists():
        found.add("codex")
    if (home / ".gemini").exists():
        found.add("gemini")
    if (home / ".config" / "gh").exists() or (home / "AppData" / "Roaming" / "GitHub CLI").exists():
        found.add("copilot")
    return found


def _norm_helper(name: str) -> str:
    return name.lower().replace("user-", "").replace("_", "-")


def score_project(
    project: WeeklyProject,
    user_agents: set[str],
    mcps: list[str] | None = None,
    skills: list[str] | None = None,
) -> ProjectFit:
    matched_a = [a for a in project.agents if a in user_agents]
    missing_a = [a for a in project.agents if a not in user_agents]
    helpers = {_norm_helper(x) for x in (mcps or []) + (skills or [])}
    tags = tuple(_norm_helper(t) for t in project.mcp_tags + project.skill_tags)
    matched_h = [t for t in tags if any(t in h or h in t for h in helpers)]
    score = len(matched_a) * 10 + len(matched_h) * 6
    # Üst sıra hafif bonus — Top 100 kimliği
    if project.rank and project.rank <= 20:
        score += 2
    if matched_a and not missing_a:
        kind = "fit"
        score += 20
    elif matched_a or matched_h:
        kind = "partial"
        score += 8
    else:
        kind = "gap"
    return ProjectFit(
        project=project,
        score=score,
        matched_agents=matched_a,
        missing_agents=missing_a,
        matched_helpers=matched_h,
        kind=kind,
    )


def featured_projects(
    *,
    user_agents: set[str] | None = None,
    mcps: list[str] | None = None,
    skills: list[str] | None = None,
    when: date | None = None,
    count: int = 3,
) -> list[ProjectFit]:
    """ISO haftaya göre katalogdan dilim; kullanıcı uyumuna göre sırala."""
    day = when or date.today()
    week = day.isocalendar()[1]
    year = day.isocalendar()[0]
    start = (year * 53 + week * 3) % len(CATALOG)
    slice_ids = [(start + i) % len(CATALOG) for i in range(min(count, len(CATALOG)))]
    agents = set(user_agents or ())
    fits = [score_project(CATALOG[i], agents, mcps, skills) for i in slice_ids]
    fits.sort(key=lambda f: (-f.score, f.project.rank or 999, f.project.title))
    return fits


def ranked_projects(
    *,
    user_agents: set[str] | None = None,
    mcps: list[str] | None = None,
    skills: list[str] | None = None,
    cat: str | None = None,
) -> list[ProjectFit]:
    """Top 100 sırası (rank); isteğe bağlı kategori filtresi."""
    agents = set(user_agents or ())
    fits = [score_project(p, agents, mcps, skills) for p in CATALOG]
    if cat and cat != "all":
        fits = [f for f in fits if f.project.cat == cat]
    fits.sort(key=lambda f: (f.project.rank or 999, f.project.title))
    return fits


def grouped_projects(
    *,
    user_agents: set[str] | None = None,
    mcps: list[str] | None = None,
    skills: list[str] | None = None,
    when: date | None = None,
) -> list[tuple[str, list[ProjectFit]]]:
    """Kategorilere göre Top 100 dilimleri (rank sırası)."""
    del when  # API uyumu; Top 100 sabit sıra
    agents = set(user_agents or ())
    by_cat: dict[str, list[ProjectFit]] = {c: [] for c in CAT_ORDER}
    for proj in CATALOG:
        fit = score_project(proj, agents, mcps, skills)
        cat = proj.cat if proj.cat in by_cat else "tools"
        by_cat[cat].append(fit)
    out: list[tuple[str, list[ProjectFit]]] = []
    for cat in CAT_ORDER:
        rows = by_cat[cat]
        if not rows:
            continue
        rows.sort(key=lambda f: (f.project.rank or 999, f.project.title))
        out.append((cat, rows))
    return out


def agent_label(agent: str) -> str:
    return AGENT_LABEL.get(agent, agent)
