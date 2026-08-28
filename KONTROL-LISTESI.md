# Token Tracker — dosya kontrol listesi

Proje kökü: `D:\token tracker`

## Gerekli — tut

| Dosya / klasör | Amaç |
|----------------|------|
| `overlay.py` | Ana uygulama (UI) |
| `usage_client.py` | Kota okuma |
| `prompt_coach.py` | Öneriler |
| `lang_packs.py`, `lang_packs_data.py` | Çeviriler |
| `meter_texts.py` | Kota metinleri |
| `version.py` | Sürüm (0.1.2) |
| `assets/flags/*.png` | Dil bayrakları (21 adet) |
| `logo.png`, `logo.ico` | Uygulama simgesi |
| `LISANS-SOZLESMESI.txt`, `LICENSE` | Lisans |
| `SURUM-NOTLARI.txt` | Yayın notları |
| `TokenTracker_onedir.spec` | PyInstaller |
| `requirements-release.txt` | Bağımlılıklar |
| `_build_deploy.py` | Test + derleme + ZIP |
| `_deploy_root.py`, `_pack_release.py` | Deploy + yayın paketi |
| `_fetch_flag_assets.py`, `_prune_exes.py`, `_purge_legacy.py` | Bakım |
| `test_*.py` | Testler |
| `TokenTracker.exe` + `_internal/` | Çalışan program |
| `release/TokenTracker-0.1.2-win64.zip` | İnternet yayını |
| `baslat.bat`, `README.md`, `AGENTS.md` | Kullanım |

## Gereksiz — silinir / üretilmez

| Öğe | Durum |
|-----|--------|
| `D:\cursor\token takip programı\` | Silindi (`_purge_legacy.py`) |
| `%LOCALAPPDATA%\Pulse\` | Silindi |
| `build_out/`, `release_out/` | Derleme ara çıktı |
| Eski `TokenTakip.exe` | Kaldırıldı |

## Yayın

```bat
.venv\Scripts\python.exe _build_deploy.py
```

Yüklenecek dosya: `release\TokenTracker-0.1.2-win64.zip`
