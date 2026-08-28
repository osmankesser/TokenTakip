# Token Tracker

Windows masaustu uygulamasi: Cursor, Codex, Claude, Gemini ve GitHub Copilot kalan kota bilgisi.

**Surum:** 0.1.2

## Indirme (kullanici)

`release/TokenTracker-0.1.2-win64.zip` dosyasini acin. Klasorun tamamini koruyun (`TokenTracker.exe` + `_internal`).

SHA256: `release/TokenTracker-0.1.2-win64.sha256.txt`

## Gelistirme

```bat
cd /d "D:\token tracker"
python -m venv .venv
.venv\Scripts\pip install -r requirements-release.txt
.venv\Scripts\python.exe _build_deploy.py
```

Cikti: `TokenTracker.exe`, `release/TokenTracker-0.1.2-win64.zip`

## Calistirma

`TokenTracker.exe` veya `baslat.bat`
