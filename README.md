# TokenTakip

**See your AI quota at a glance — Cursor, Codex, Claude, Gemini, Copilot.**

Free Windows desktop app. Open source. No telemetry. No account. No cloud of ours.

[![Release](https://img.shields.io/github/v/release/osmankesser/TokenTakip?style=flat-square)](https://github.com/osmankesser/TokenTakip/releases)
[![License](https://img.shields.io/github/license/osmankesser/TokenTakip?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D4?style=flat-square)](https://github.com/osmankesser/TokenTakip/releases)

---

### Why TokenTakip?

You juggle multiple AI tools. Quotas hide behind menus and dashboards.  
**TokenTakip sits on your desktop, stays on top, and shows what’s left** — when *you* allow it.

| You want | TokenTakip does |
|----------|-----------------|
| Fast quota check | One overlay window |
| Privacy by default | Quota & chat analysis **off** until you enable them |
| No surprise uploads | Tokens never go to the developer |
| Open code + ready EXE | Build yourself **or** download the release ZIP |

---

### Download (Windows)

1. Open **[Releases](https://github.com/osmankesser/TokenTakip/releases)**
2. Download `TokenTakip-0.1.0-win64.zip`
3. Extract the **whole folder** (don’t move only the `.exe`)
4. Run `TokenTakip.exe`
5. Accept the license → optionally enable quota in Settings

> Unsigned build: Windows may show “Unknown publisher”. That’s expected for this release.

**SHA-256** of the ZIP is listed on the release page.

---

### What it can track (with permission)

- **Cursor**
- **Codex** (ChatGPT session / CLI)
- **Claude**
- **Gemini**
- **GitHub Copilot**

Optional **Ideas** mode can read *known local* chat folders on your PC only — still off by default, never uploaded to us.

---

### Privacy in one line

**Default = nothing.** No quota API calls, no chat scan, until you turn switches on in Settings.

---

### Build from source

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-release.txt
python -m unittest test_privacy test_license
python test_buttons.py
pyinstaller -y --distpath release_out --workpath build_out TokenTakip_onedir.spec
```

Requires **Python 3.14+** (x64) and Windows.

---

### Stack

- Python · PySide6 / Qt **6.11.2** (LGPL)
- PyInstaller onedir (libraries replaceable)
- Contact: **keseryazilim@gmail.com**

---

### Not affiliated

TokenTakip is **not** an official product of Cursor, OpenAI, Anthropic, Google, or GitHub.

---

### License

Application source: **MIT** (see `LICENSE`).  
Qt / PySide6 / shiboken6: **LGPL** — see the `licenses/` folder inside the release ZIP.
