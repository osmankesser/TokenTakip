# Token Tracker 0.1.5 — Agents, GitHub discovery, and a new navigation experience

Token Tracker 0.1.5 is the largest update so far. It expands the app from a quota viewer into a compact workspace for understanding your AI usage, discovering local agents, and exploring useful GitHub projects — while keeping the privacy-first local workflow.

<p align="center">
  <img src="https://raw.githubusercontent.com/osmankesser/TokenTakip/master/docs/screenshots/01-overview.png" alt="Token Tracker 0.1.5 quota overview" width="420">
</p>

## Highlights

### New floating pill navigation

The bottom navigation has been rebuilt with a modern floating design:

- Theme-aware active colors
- Smooth lift/fade transitions
- Soft shadows and a compact home indicator
- Consistent icon sizing and hover feedback
- Five focused sections: **Quota, Ideas, Agents, GitHub, and Settings**

### New Agents page

Token Tracker now automatically presents the AI agents detected on your computer. Select an agent logo to open one consistent detail view containing the relevant quota context, usage history, rules, extensions, skills, MCP integrations, and agent-specific advice when available.

<p align="center">
  <img src="https://raw.githubusercontent.com/osmankesser/TokenTakip/master/docs/screenshots/03-agents.png" alt="Detected AI agents" width="420">
</p>

### GitHub Top 100

Explore useful open-source projects without leaving the app:

- Live GitHub project data with a six-hour cache
- Offline catalog fallback
- MCP, IDE, Terminal, Rules, Tools, and Learn filters
- In-app project details
- Download instructions, terminal commands, and MCP setup guidance
- The browser opens only when **Open on the web** is selected

<p align="center">
  <img src="https://raw.githubusercontent.com/osmankesser/TokenTakip/master/docs/screenshots/04-github.png" alt="GitHub Top 100" width="420">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/osmankesser/TokenTakip/master/docs/screenshots/05-github-detail.png" alt="GitHub project details" width="420">
</p>

### Automatic translation for GitHub descriptions

When a non-English interface language is selected, public GitHub repository descriptions are translated automatically:

- Translation runs in the background
- Results are cached locally
- Code and terminal commands are preserved
- Network or translation failures safely fall back to the original text

Translation uses Google Translate (`translate.googleapis.com`) and sends only public repository descriptions — never credentials, tokens, private chats, or local files.

### Interface and quality improvements

- Expanded localization coverage across 21 languages
- Improved quota card behavior and visual consistency
- Better theme support for Night, Frost, Aurora, and Ember
- Faster, flicker-free navigation animation
- Correct initial rendering of all navigation icons
- Additional automated coverage for navigation, agents, GitHub data, translation, and button flows

## More screenshots

<p align="center">
  <img src="https://raw.githubusercontent.com/osmankesser/TokenTakip/master/docs/screenshots/02-ideas.png" alt="Usage ideas" width="390">
  <img src="https://raw.githubusercontent.com/osmankesser/TokenTakip/master/docs/screenshots/06-settings.png" alt="Aurora settings" width="390">
</p>

## Installation

1. Download **`TokenTracker-0.1.5-win64.zip`** below.
2. Extract the entire archive.
3. Keep `TokenTracker.exe` and `_internal` together.
4. Run `TokenTracker.exe`.

> The Windows executable is not digitally signed. SmartScreen may display an **Unknown publisher** warning. Verify the checksum before running the app.

## SHA-256

```text
4e147659fb188fa7e7719fa74ba0a96185903e3a9fab9627dcfb2d4ea982a2ec
```

## Privacy summary

- No developer telemetry server
- Quota checks use local sessions and provider APIs
- Optional chat analysis remains local
- Automatic translation receives public GitHub descriptions only
- Access features can be disabled in Settings

## Supported providers

Cursor · OpenAI Codex · Anthropic Claude · Google Gemini · GitHub Copilot

---

Questions or feedback: **keseryazilim@gmail.com**
