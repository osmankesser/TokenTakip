# TokenTakip

Windows masaüstü uygulaması: yerel AI araçlarının kota / kullanım bilgisini gösterir.

- Ücretsiz, kapalı kaynak dağıtım modeli
- Kota ve sohbet analizi varsayılan kapalı
- PySide6 onedir paketi ile yayınlanır

## Geliştirme

Python 3.14+, ayrı yayın ortamı önerilir (`.venv_release`).

```text
pip install -r requirements-release.txt
python -m unittest test_privacy test_license
python test_buttons.py
pyinstaller -y --distpath release_staging_6112 --workpath build_release_staging_6112 TokenTakip_onedir.spec
```

## Güvenlik notu

`remote_server.py` ve `live.py` yayın paketine girmez; geliştirme yardımcılarıdır.

## İletişim

keseryazilim@gmail.com
