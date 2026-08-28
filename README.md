# Token Tracker

[![Release](https://img.shields.io/github/v/release/osmankesser/TokenTakip?style=flat-square)](https://github.com/osmankesser/TokenTakip/releases)
[![License](https://img.shields.io/github/license/osmankesser/TokenTakip?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D4?style=flat-square)](https://github.com/osmankesser/TokenTakip/releases)

---

## Türkçe

### Tüm yapay zekâ kullanım haklarınızı tek ekranda görün

**Token Tracker**, Cursor, Codex, Claude, Gemini ve GitHub Copilot hesaplarınızdaki **kalan kullanım hakkını** Windows masaüstünde gösteren **ücretsiz ve açık kaynaklı** bir uygulamadır.

Verilerinizi geliştiriciye göndermez. İlk açılışta **tek bir onay** ile lisansı kabul eder, kota erişimini ve sohbet analizini birlikte açarsınız — isterseniz sonra Ayarlar’dan kapatabilirsiniz.

<p align="center">
  <img src="docs/screenshots/usage-tr.png" alt="Token Tracker — kalan kullanım" width="420">
</p>

<p align="center">
  <img src="docs/screenshots/demo.gif" alt="Token Tracker kısa demo" width="420">
</p>

### Nasıl çalışır?

1. **İndirin ve çalıştırın** — [Release](https://github.com/osmankesser/TokenTakip/releases/latest) ZIP’ini açın, klasörün tamamını koruyun, `TokenTracker.exe`’yi başlatın.
2. **Tek onay** — Lisans + kota + sohbet analizi birlikte sorulur. Kabul edince uygulama hazır; reddederseniz çıkar.
3. **Kota ekranı** — Bilgisayarınızdaki oturum dosyasını okur ve **ilgili hizmetin resmî API’sine** sorar. Kritik kartlar üstte, detay için karta tıklayın.

<p align="center">
  <img src="docs/screenshots/03-ideas.png" alt="Öneriler — sohbet analizi" width="420">
</p>

### Hangi serviste ne gösterilir?

| Servis | Ne okunur | Ekranda ne görünür |
|--------|-----------|-------------------|
| **Cursor** | Yerel Cursor oturumu → `api2.cursor.sh` | Plan; **kalan %**; **dönem yenilenme zamanı** |
| **Codex** | Yerel Codex oturumu → `chatgpt.com` | Plan; **5 saat / günlük / haftalık** **kalan %** |
| **Claude** | Yerel `.claude` kimlik dosyası → Anthropic API | Plan; **5 saat** ve **haftalık** **kalan %** |
| **Gemini** | Yerel Gemini OAuth → Google API | Model başına **kalan %** |
| **GitHub Copilot** | Yerel GitHub oturumu (`gh`) → GitHub API | Plan; Premium / Chat / Tamamlama **kalan %** |

### İndirme (Windows)

1. **[Releases](https://github.com/osmankesser/TokenTakip/releases/latest)** → `TokenTracker-0.1.3-win64.zip`
2. ZIP’i açın — **yalnız `.exe`’yi taşımayın** (`_internal` klasörü şart).
3. `TokenTracker.exe`’yi çalıştırın.

SHA-256: `release/TokenTracker-0.1.3-win64.sha256.txt` dosyasında.

### “Bilinmeyen yayıncı” uyarısı neden çıkar?

Bu sürüm **dijital imzalı değildir**. Windows SmartScreen imzasız `.exe` dosyalarında uyarı gösterebilir — bu virüs demek değildir. Kaynak kodu açık; ZIP hash’i ile doğrulayın.

### Gizlilik (kısa)

| | |
|---|---|
| Geliştirici sunucusu | **Yok** — token/sohbet bize gitmez |
| Kota | Yerel oturum → yalnızca resmî API |
| Sohbet analizi | Bilinen yerel klasörler; internete gönderilmez |
| İzinler | Tek açılış onayı; sonra Ayarlar’dan kapatılabilir |

İletişim: **keseryazilim@gmail.com**

---

## English

### See all your AI usage limits in one place

**Token Tracker** is a free, open-source Windows desktop app that shows **how much usage you have left** on Cursor, Codex, Claude, Gemini, and GitHub Copilot.

Nothing is sent to the developer. **One startup prompt** accepts the license and enables quota + chat analysis together — you can turn them off later in Settings.

<p align="center">
  <img src="docs/screenshots/settings-en.png" alt="Token Tracker settings" width="420">
</p>

### How it works

1. **Download & run** — Get the [latest release ZIP](https://github.com/osmankesser/TokenTakip/releases/latest), extract the **whole folder**, run `TokenTracker.exe`.
2. **One consent** — License, quota access, and chat analysis in a single dialog.
3. **Quota screen** — Reads your **local session**, asks only each provider’s **official API**. Critical cards float to the top.

### Download

Same ZIP as above. Verify with `TokenTracker-0.1.3-win64.sha256.txt`.

### Privacy

No telemetry. No developer server. Local session reads only; chat scan stays on your PC.

Contact: **keseryazilim@gmail.com**

---

### Build from source

```bat
cd /d "D:\token tracker"
python -m venv .venv
.venv\Scripts\pip install -r requirements-release.txt
.venv\Scripts\python.exe _build_deploy.py
```

### License

App source: **MIT** (`LICENSE`). Qt / PySide6: **LGPL**.

Token Tracker is **not** affiliated with Cursor, OpenAI, Anthropic, Google, or GitHub.
