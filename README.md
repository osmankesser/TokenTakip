# TokenTakip

[![Release](https://img.shields.io/github/v/release/osmankesser/TokenTakip?style=flat-square)](https://github.com/osmankesser/TokenTakip/releases)
[![License](https://img.shields.io/github/license/osmankesser/TokenTakip?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D4?style=flat-square)](https://github.com/osmankesser/TokenTakip/releases)

---

## Türkçe

### Tüm yapay zekâ kullanım haklarınızı tek ekranda görün

**TokenTakip**, Cursor, Codex, Claude, Gemini ve GitHub Copilot hesaplarınızdaki **kalan kullanım hakkını** Windows masaüstünde gösteren **ücretsiz ve açık kaynaklı** bir uygulamadır.

Verilerinizi geliştiriciye göndermez. Kota okuma ve sohbet analizi **siz açana kadar kapalıdır**.

<p align="center">
  <img src="docs/screenshots/usage-tr.png" alt="TokenTakip ana ekran — kalan kullanım" width="420">
</p>

<p align="center">
  <img src="docs/screenshots/demo.gif" alt="TokenTakip kısa demo" width="420">
</p>

### Nasıl çalışır?

1. **İndirin ve çalıştırın** — [Release](https://github.com/osmankesser/TokenTakip/releases/tag/v0.1.0) ZIP’ini açın, klasörün tamamını koruyun, `TokenTakip.exe`’yi başlatın.
2. **Lisansı kabul edin** — İlk açılışta lisans metni gelir. Bu adım kota veya sohbet iznini **açmaz**.
3. **İsterseniz Ayarlar’dan “Kota erişimi”ni açın** — Uygulama yalnızca bilgisayarınızdaki oturum dosyasını okur ve **ilgili hizmetin resmî API’sine** sorar. Sonuç ana ekranda görünür.

Kota kapalıyken hiçbir oturum dosyası okunmaz ve internete istek gitmez.

### Hangi serviste ne gösterilir?

API yanıtına göre değişir; aşağıdaki tablo uygulamanın **göstermeye çalıştığı** bilgilerdir:

| Servis | Ne okunur | Ekranda ne görünür |
|--------|-----------|-------------------|
| **Cursor** | Yerel Cursor oturumu → `api2.cursor.sh` | Plan adı; **kalan %** (toplam, otomatik, API); isteğe bağlı harcama limiti ($); **dönem yenilenme zamanı** |
| **Codex** | Yerel Codex oturumu veya `codex status --json` → `chatgpt.com` | Plan; **5 saat / günlük / haftalık** pencerelerde **kalan %**; varsa kredi bakiyesi ve **yenilenme zamanı** |
| **Claude** | Yerel `.claude` kimlik dosyası → `api.anthropic.com` | Plan; **5 saat** ve **haftalık** (Sonnet/Opus) **kalan %**; **yenilenme zamanı** |
| **Gemini** | Yerel Gemini OAuth → Google API | Model başına **kalan %**; **yenilenme zamanı** |
| **GitHub Copilot** | Yerel GitHub oturumu (`gh`) → `api.github.com` | Plan; Premium / Chat / Tamamlama için **kalan %**; **kota yenilenme tarihi** |

> İstek sayısı yalnızca sağlayıcı API’si verirse gösterilir; çoğu pencerede **yüzde + yenilenme** esas alınır. Oturum yoksa veya API yanıt vermezse “Kota yok” / hata mesajı görünür.

### İndirme (Windows)

1. **[Releases](https://github.com/osmankesser/TokenTakip/releases/tag/v0.1.0)** → `TokenTakip-0.1.0-win64.zip`
2. ZIP’i açın — **yalnız `.exe`’yi taşımayın** (Qt dosyaları klasörde kalmalı).
3. `TokenTakip.exe`’yi çalıştırın.

**SHA-256:** `20AD2D23510922E99F398671D19DCC9183057AE81115D505FAF5E4EBA66957F0`

### “Bilinmeyen yayıncı” uyarısı neden çıkar?

Bu sürüm **dijital imzalı değildir** (code signing sertifikası yok). Windows, imzasız `.exe` dosyalarında SmartScreen ile uyarı gösterebilir.

- Bu, virüs demek değildir — yayın henüz Microsoft’tan “tanınan yayıncı” onayı almamıştır.
- Kaynak kodu GitHub’da açık; ZIP SHA-256 ile doğrulanabilir.
- Yine de emin değilseniz yalnızca bu repodaki Release linkinden indirin.

### Gizlilik (kısa)

| Varsayılan | Açıklama |
|------------|----------|
| Kota erişimi | **Kapalı** — oturum okunmaz, API çağrısı yok |
| Sohbet analizi | **Kapalı** — yerel sohbet taranmaz |
| Geliştirici sunucusu | **Yok** — token/sohbet bize gitmez |

İletişim: **keseryazilim@gmail.com**

<details>
<summary><strong>İsteğe bağlı: Öneriler (Ideas) modu</strong></summary>

Ana ekrandan bağımsız, **ayrı bir izindir**. Açılırsa bilinen yerel sohbet klasörlerini yalnızca bu bilgisayarda okur; internete gönderilmez. Varsayılan **kapalıdır**.

</details>

---

## English

### See all your AI usage limits in one place

**TokenTakip** is a free, open-source Windows desktop app that shows **how much usage you have left** on Cursor, Codex, Claude, Gemini, and GitHub Copilot.

Nothing is sent to the developer. Quota and chat features stay **off until you enable them**.

<p align="center">
  <img src="docs/screenshots/settings-en.png" alt="TokenTakip settings — permissions" width="420">
</p>

### How it works

1. **Download & run** — Get the [release ZIP](https://github.com/osmankesser/TokenTakip/releases/tag/v0.1.0), extract the **whole folder**, run `TokenTakip.exe`.
2. **Accept the license** — Shown once on first launch. Does **not** enable quota or chat.
3. **Optionally turn on “Quota access” in Settings** — Reads your **local session file** on this PC, then asks only that provider’s **official API**. Results appear on the main screen.

With quota off: no session reads, no network requests.

### What each service shows

| Service | Local source | On screen |
|---------|--------------|-----------|
| **Cursor** | Cursor session → `api2.cursor.sh` | Plan; **remaining %** (total, auto, API); optional spend ($); **billing cycle reset** |
| **Codex** | Codex session / CLI → `chatgpt.com` | Plan; **5h / daily / weekly** **remaining %**; credit balance; **reset time** |
| **Claude** | `.claude` credentials → Anthropic API | Plan; **5h & weekly** **remaining %**; **reset time** |
| **Gemini** | Gemini OAuth → Google API | Per-model **remaining %**; **reset time** |
| **GitHub Copilot** | GitHub CLI session → GitHub API | Plan; Premium / Chat / Completions **remaining %**; **quota reset date** |

Request counts appear only when the provider API returns them; most views emphasize **percent left + reset time**.

### Download

Same ZIP as above. **SHA-256:** `20AD2D23510922E99F398671D19DCC9183057AE81115D505FAF5E4EBA66957F0`

### Why “Unknown publisher” on Windows?

This build is **not code-signed**. SmartScreen may warn on first run — that means Windows doesn’t recognize the publisher yet, **not** that the file is malicious. Source is on GitHub; verify the ZIP hash. Download only from this repo’s Releases page.

### Privacy (short)

Quota access and chat analysis are **off by default**. No telemetry. No developer server.

Contact: **keseryazilim@gmail.com**

<details>
<summary><strong>Optional: Ideas mode</strong></summary>

Separate permission. Scans known local chat folders on this PC only when enabled. Never uploaded to us. Off by default.

</details>

---

### Build from source

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-release.txt
python -m unittest test_privacy test_license
pyinstaller -y --distpath release_out --workpath build_out TokenTakip_onedir.spec
```

Python **3.14+** (x64), Windows.

### License

App source: **MIT** (`LICENSE`). Qt / PySide6: **LGPL** (see `licenses/` in the release ZIP).

TokenTakip is **not** affiliated with Cursor, OpenAI, Anthropic, Google, or GitHub.
