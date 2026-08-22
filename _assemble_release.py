# Assemble TokenTakip release folder + ZIP. Not a legal opinion.
from __future__ import annotations

import hashlib
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "release_staging_6112" / "TokenTakip"
OUT = ROOT / "release_publish" / "TokenTakip-0.1.0-win64"
ZIP = ROOT / "release_publish" / "TokenTakip-0.1.0-win64.zip"
LIC_SRC = ROOT / "release_docs_staging" / "licenses"
VER = "0.1.0"
# Placeholders only — do not invent personal/legal facts
PH = {
    "SÜRÜM": VER,
    "YAYIN TARİHİ": "22.08.2026",
    "GELİŞTİRİCİ": "TokenTakip",
    "EMAIL": "keseryazilim@gmail.com",
    "ADRES": "[TEBLİGAT/İLETİŞİM ADRESİ]",
    "URL": "[RESMÎ İNDİRME SAYFASI]",
    "MAHKEME": "[YETKİLİ MAHKEME VE İCRA DAİRELERİ]",
    "SHA": "[YAYINCI TARAFINDAN DOLDURULACAK — ZIP SHA-256]",
}

LISANS = f"""TokenTakip — Yazılım Kullanım Lisansı (Taslak)

Yazılım: TokenTakip
Sürüm: {PH['SÜRÜM']}
Yürürlük / yayın tarihi: {PH['YAYIN TARİHİ']}
Hak sahibi / yayıncı: {PH['GELİŞTİRİCİ']}
İletişim: {PH['EMAIL']}
Adres: {PH['ADRES']}
Resmî indirme: {PH['URL']}

ÖNEMLİ: Bu metin hukuki bir taslaktır. Yayınlanmadan önce yetkin bir hukukçu tarafından incelenmeli ve gerekirse uyarlanmalıdır. Bu metin hukuki tavsiye değildir.

1. Konu ve kabul
Bu sözleşme, TokenTakip adlı Windows uygulamasının (bundan sonra “Yazılım”) ücretsiz kullanım koşullarını düzenler.
Yazılım, ilk çalıştırmada bu lisans metnini gösterir. Kullanım için uygulama içindeki “Lisansı kabul ediyorum” seçeneğini onaylamanız gerekir.
Yalnızca indirmiş, kurmuş veya çalıştırmış olmanız tek başına bu sözleşmenin kabulü sayılmaz.
Kabul etmiyorsanız “Kabul etmiyorum ve çık” seçeneğini kullanın veya Yazılımı cihazınızdan kaldırın.
Lisans kabulü; kota erişimini veya sohbet analizini açmaz. Bu izinler ayrıdır ve varsayılan olarak kapalıdır.

2. Fikrî haklar
Yazılımın özgün kodu, arayüzü, derlenmiş çıktısı ve bunlara ilişkin özgün içerikler üzerindeki fikrî ve sınai haklar, yürürlükteki mevzuat çerçevesinde {PH['GELİŞTİRİCİ']}’e aittir. Üçüncü taraf bileşenlere ilişkin haklar ilgili hak sahiplerine aittir; bu haklar saklıdır.

3. Kullanım izni
Hak sahibi size, ücretsiz, kişisel, sınırlı, münhasır olmayan ve devredilemez bir kullanım izni verir. Bu izin, Yazılımı kendi bilgisayarınızda çalıştırmanız içindir. Yazılımın mülkiyeti size devredilmez; yalnızca kullanım hakkı verilir.

4. Yasaklar
Aşağıdakiler, yazılı izin veya kanunun açıkça izin verdiği hâller saklı kalmak üzere yasaktır:
a) Yazılımı satmak, kiralamak, ücret karşılığı hizmet olarak sunmak;
b) Yazılımı geliştirici adına veya geliştiriciyi yanıltacak biçimde değiştirilmiş kopya olarak dağıtmak;
c) Yazılımı başka bir indirme sitesinde veya platformda yeniden yayımlamak (yazılı izin gerekir);
d) Yazılımı kötüye kullanarak başkalarının hesaplarına, oturumlarına veya sistemlerine yetkisiz erişim sağlamak.

5. Tersine mühendislik ve LGPL istisnası
Kanunen vazgeçilemeyecek haklarınız saklıdır.
Ayrıca, GNU Lesser General Public License (LGPL) kapsamındaki PySide6, shiboken6, Qt ve diğer LGPL bileşenleri bakımından aşağıdaki işlemler bu sözleşmenin genel tersine mühendislik / değiştirme sınırlarının açık istisnasıdır ve engellenmez:
a) Bu LGPL bileşenlerini değiştirmek;
b) Değiştirilmiş, arayüzle uyumlu LGPL kütüphaneleriyle Yazılımı çalıştırmak;
c) Bu değişikliklerde hata ayıklamak için gerekli tersine mühendislik;
d) Kanunen izin verilen birlikte çalışabilirlik işlemleri.
Yazılım, bu LGPL kütüphanelerini şifreleyerek, kilitleyerek veya bütünlük kontrolüyle değiştirilmesini engelleyecek biçimde paketlemez (onedir dağıtım).
TokenTakip’in kendi özgün kapalı kaynak kodu LGPL kapsamına girmez; LGPL zorunlu kılmadığı sürece kaynak kod paylaşılmaz.
Ayrıntılar: UCUNCU-TARAF-BILDIRIMLERI.txt, LGPL-NASIL-DEGISTIRILIR.txt, licenses/, SOURCES.txt.

6. Üçüncü taraf bileşenler
Yazılım, üçüncü taraf kütüphaneler içerir. Bunların lisansları kendi metinlerinde belirtilir; özet “UCUNCU-TARAF-BILDIRIMLERI.txt”, tam metinler “licenses/” klasöründedir. Bu bileşenlerin lisansları saklıdır ve bu sözleşme onları geçersiz kılmaz.
LicenseRef-Qt-Commercial.txt ticari Qt lisans referansıdır; bu Community/LGPL dağıtımının ana lisansı değildir.

7. “Olduğu gibi” sunum ve garanti sınırları
Yazılım “olduğu gibi” ve “mevcut hâliyle” sunulur. Hak sahibi; kesintisiz, hatasız, güvenli veya tüm yapay zekâ sağlayıcılarıyla sürekli uyumlu çalışma konusunda açık veya zımnî bir garanti vermez. Harici uygulama, API, oturum biçimi veya sağlayıcı politika değişiklikleri nedeniyle kota okuma veya diğer özellikler bozulabilir, kısıtlanabilir veya çalışmayı durdurabilir.

8. Kullanıcı sorumlulukları
Hesaplarınızın, oturum dosyalarınızın, yedeklerinizin ve cihazınızın güvenliğinden siz sorumlusunuz. Yazılımı kullanmadan önce gerekli yedekleri almanız önerilir. Sağlayıcıların kullanım şartlarına ve yürürlükteki hukuka uymak sizin sorumluluğunuzdadır.

9. Sorumluluğun sınırlandırılması
Kanunun izin verdiği ölçüde hak sahibi; dolaylı zarar, kâr kaybı, iş kesintisi, veri kaybı veya üçüncü taraf taleplerinden doğan zararlardan sorumlu tutulamaz. Kanunen sınırlandırılamayan sorumluluklar, kasıt, ağır kusur ve emredici tüketici hükümleri saklıdır. “Hiçbir durumda hiçbir sorumluluk yoktur” şeklinde mutlak bir feragat ileri sürülmez.

10. Destek ve güncelleme
Sürekli teknik destek, belirli bir yanıt süresi veya otomatik güncelleme taahhüdü yoktur. Güncelleme yayımlanırsa koşullar ayrıca belirtilebilir.

11. Bağımsızlık bildirimi
TokenTakip; Cursor, OpenAI, ChatGPT, Codex, Anthropic, Claude, Google, Gemini, GitHub veya Copilot’un resmî ürünü değildir. Bu kuruluşlarla ortaklık, sponsorluk veya onay ilişkisi iddia edilmez. Anılan adlar yalnızca uyumluluk ve açıklama amacıyla kullanılabilir ve ilgili sahiplerinin markaları olabilir.

12. Sona erme
Bu lisansın esaslı ihlali hâlinde kullanım izniniz kendiliğinden sona erebilir. Sona ermede Yazılımı kullanmayı bırakmalı ve kopyalarını silmelisiniz. Kanunen saklı haklar etkilenmez.

13. Uygulanacak hukuk ve yetki
Bu sözleşme Türkiye Cumhuriyeti hukukuna tâbidir. Uyuşmazlıklarda {PH['MAHKEME']} yetkilidir; emredici tüketici hükümleri saklıdır.

14. İletişim
Sorularınız için: {PH['EMAIL']}
"""

GIZLILIK = f"""TokenTakip — Gizlilik Bilgilendirmesi ve Aydınlatma Metni (Taslak)

Sürüm: {PH['SÜRÜM']}
Tarih: {PH['YAYIN TARİHİ']}
Veri sorumlusu / yayıncı: {PH['GELİŞTİRİCİ']}
İletişim: {PH['EMAIL']}
Adres: {PH['ADRES']}

ÖNEMLİ:
- Bu metin hukuki taslaktır; KVKK ve ilgili mevzuata uygunluk için hukukçu incelemesi gerekir.
- “Veri sorumlusu” ifadesi ve KVKK hukuki sebepleri hukukçu tarafından kesinleştirilmeden yayıma hazır sayılmamalıdır.
- Aydınlatma ile uygulama içi izin (onay) aynı şey değildir. Uygulama, kota ve sohbet için ayrı teknik izinler ister; bu metin bilgilendirme amaçlıdır.
- Aşağıdaki “hukuki sebep” alanları yer tutucudur; uydurma sebep yazılmamıştır.
- Yurt dışındaki sağlayıcı API’lerine token gönderilmesi KVKK bakımından ayrıca değerlendirilmelidir.

A) Veri akışı tablosu

1) Cursor oturum bilgileri
- Nereden: Yerel Cursor oturum / kimlik verisi (ör. state.vscdb içindeki ilgili anahtarlar)
- Nereye: Yalnızca api2.cursor.sh üzerindeki resmî kota/kullanım uçları (izin açıkken)
- Amaç: Kalan kota / kullanım bilgisini göstermek
- İşleme: Cihazda okuma + harici sağlayıcı API’sine istek
- Kalıcı saklama (uygulama tarafından): Hayır (token kalıcı yazılmaz)
- Kontrol: Ayarlar → Kota erişimi (varsayılan kapalı)

2) Codex / ChatGPT oturum bilgileri
- Nereden: Yerel Codex oturum dosyası (ör. .codex/auth.json); gerekirse yerel `codex status --json` CLI çıktısı
- Nereye: chatgpt.com üzerindeki resmî kullanım uçları (izin açıkken)
- Amaç: Kota / kullanım göstermek
- İşleme: Yerel + harici API
- Kalıcı saklama: Hayır
- Kontrol: Kota erişimi

3) Claude oturum bilgileri
- Nereden: Yerel Claude kimlik/oturum dosyası
- Nereye: api.anthropic.com resmî kullanım ucu (izin açıkken)
- Amaç: Kota / kullanım
- İşleme: Yerel + harici API
- Kalıcı saklama: Hayır
- Kontrol: Kota erişimi

4) Gemini oturum bilgileri
- Nereden: Yerel Gemini OAuth kimlik dosyası
- Nereye: cloudcode-pa.googleapis.com resmî kota ucu (izin açıkken)
- Amaç: Kota / kullanım
- İşleme: Yerel + harici API
- Kalıcı saklama: Hayır
- Kontrol: Kota erişimi

5) GitHub Copilot oturum bilgileri
- Nereden: Yerel GitHub CLI / hosts veya ortam değişkeni yoluyla erişilen oturum token’ı
- Nereye: api.github.com ilgili Copilot kullanıcı ucu (izin açıkken)
- Amaç: Kota / kullanım
- İşleme: Yerel + harici API
- Kalıcı saklama: Hayır
- Kontrol: Kota erişimi

6) Yerel sohbet geçmişleri
- Nereden (kesin liste): Cursor; Claude; Codex; GitHub Copilot / VS Code ailesi (Code, Cursor, Windsurf, Trae, VSCodium workspaceStorage); Continue
- Nereye: Hiçbir harici sunucuya gönderilmez
- Amaç: Öneriler ekranında yerel prompt analizi
- İşleme: Yalnızca bu cihazda
- Kalıcı saklama: Sohbet içeriği uygulama tarafından kalıcı saklanmaz; analiz sonucu oturum süresince arayüzde gösterilebilir
- Kontrol: Ayarlar → Öneriler için sohbet analizi (varsayılan kapalı; kota izninden bağımsız)

7) Dil, tema, yenileme aralığı, izin ve lisans kabul tercihleri
- Nereden: Kullanıcı seçimleri
- Nereye: Yerel QSettings (tipik konum: Windows Kayıt Defteri HKCU\\Software\\TokenTakip\\ui)
- Amaç: Arayüz tercihlerini ve lisans kabul sürümünü hatırlamak
- İşleme: Yerel
- Kalıcı saklama: Evet (tercih kaydı)
- Kontrol: Ayarlar; kayıt silinerek sıfırlanabilir

8) Windows başlangıç tercihi
- Nereden: Kullanıcının Ayarlar’daki seçimi
- Nereye: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run (değer adı: PulseTokenTakip)
- Amaç: İsteğe bağlı otomatik başlatma
- İşleme: Yerel
- Kalıcı saklama: Evet (kullanıcı açarsa)
- Kontrol: Öncelikle Ayarlar’dan “Başlangıçta aç”ı kapatın

9) Yerel ikon / önbellek dosyaları
- Nereden: Yerel üretilen veya daha önce kaydedilmiş ikon/bayrak görselleri
- Nereye: %LOCALAPPDATA%\\Pulse\\cache\\
- Amaç: Arayüz görselleri
- İşleme: Yerel
- Kalıcı saklama: Evet (önbellek dosyaları)
- Not: Bu sürüm dışarıdan ikon/bayrak indirmez. Önceki sürümlerden kalan önbellek dosyaları diskte kalmış olabilir.
- Kontrol: İsteğe bağlı olarak klasörü silerek temizlenebilir

10) Panoya kopyalanan metin
- Nereden: Yerel öneri/prompt metni
- Nereye: Sistem panosu (yalnızca kullanıcı “İncele”ye basarsa)
- Amaç: Kullanıcının metni yapıştırması
- İşleme: Yerel / işletim sistemi panosu
- Kalıcı saklama: Uygulama panoyu yönetmez; işletim sistemi davranışı geçerlidir
- Kontrol: Düğmeye basmamak; panoyu temizlemek

B) Geliştirici sunucusu ve sağlayıcılar
- Token’lar ve sohbet içerikleri, geliştiricinin kontrolündeki bir sunucuya gönderilmez.
- Kota izni açıkken ilgili sağlayıcı API’sine bağlanıldığında IP adresi ve standart bağlantı meta verileri ilgili sağlayıcı tarafından görülebilir; o sağlayıcının kendi gizlilik koşulları geçerli olabilir.
- Kullanıcı, ilgili sağlayıcı hesaplarının kullanım şartlarına aykırı davranmamalıdır.
- TokenTakip bu sağlayıcıların resmî ürünü değildir.

C) İzinler
- Kota erişimi ve sohbet analizi birbirinden bağımsızdır; ikisi de varsayılan kapalıdır.
- Lisans kabulü bu izinleri açmaz.
- İzinler Ayarlar’dan geri alınabilir.
- İzin kapatıldıktan sonra daha önce başlamış bir işlem kısa süre içinde doğal olarak tamamlanabilir; ardından yeni işlem başlatılmaz.

D) Yapılmayanlar
- Telemetri, reklam, geliştirici analitiği yok.
- Çökme raporlama servisi yok.
- Lisans aktivasyonu / çevrimiçi lisans sunucusu yok (kabul yereldir).
- Otomatik güncelleme yok.
- Dışarıdan ikon/bayrak indirme yok.

E) Verileri kaldırma
1) Uygulamayı kapatın.
2) Öncelikle Ayarlar’dan kota erişimini, sohbet analizini ve “Başlangıçta aç”ı kapatın.
3) TokenTakip klasörünün tamamını silin (yalnız EXE değil).
4) İsteğe bağlı ileri düzey temizlik (zorunlu değildir):
   - HKCU\\Software\\TokenTakip
   - HKCU\\...\\Run → PulseTokenTakip
   - %LOCALAPPDATA%\\Pulse\\cache
Not: Cursor/Codex/Claude vb. kendi oturum dosyaları TokenTakip’e ait değildir.

F) KVKK kapsamında aydınlatma iskeleti (hukukçu dolduracak)

1. Veri sorumlusunun kimliği
{PH['GELİŞTİRİCİ']}, {PH['ADRES']}, {PH['EMAIL']}

2. İşleme amaçları
Yukarıdaki tabloda belirtilen amaçlarla sınırlıdır.

3. İşlenen kişisel veri kategorileri
[HUKUKÇU TARAFINDAN BELİRLENECEK]

4. Toplama yöntemi
Yerel dosya/kayıt defteri okuma; kullanıcı açtığı takdirde HTTPS ile sağlayıcı API çağrısı.

5. Hukuki sebepler
[HUKUKÇU TARAFINDAN BELİRLENECEK — açık rıza / diğer KVKK md. 5-6 sebepleri uydurulmamıştır]

6. Aktarım
Geliştirici sunucusuna aktarım yok. Kullanıcı izniyle ilgili AI sağlayıcılarının yurt içi/yurt dışı sunucularına bağlantı olabilir; [HUKUKÇU: yurt dışı aktarım değerlendirmesi].

7. Saklama süresi
Token kalıcı saklanmaz. Tercih ve önbellek, kullanıcı silene veya uygulamayı kaldırana kadar durabilir.

8. İlgili kişi hakları
KVKK md. 11 kapsamındaki haklar için başvuru: {PH['EMAIL']}
[HUKUKÇU: başvuru usulü, süre, kimlik doğrulama]

9. Açık rıza
Uygulama içi teknik izinler, bu aydınlatmanın yerine geçmez. Açık rıza gerekip gerekmediği [HUKUKÇU KARARI].
"""

UCUNCU = f"""TokenTakip — Üçüncü Taraf Bildirimleri (Taslak)

Sürüm: {PH['SÜRÜM']}
Tarih: {PH['YAYIN TARİHİ']}

Bu dosya özet niteliğindedir. Tam lisans metinleri “licenses/” klasöründedir.
LicenseRef-Qt-Commercial bu Community/LGPL dağıtımının ana lisansı değildir.

A) Çalışma zamanı (onedir paketi)

1) PySide6_Essentials
- Sürüm (bu paket build): 6.11.2
- Lisans (METADATA): LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
- Rol: Arayüz (QtCore / QtGui / QtWidgets)
- Tam metinler: licenses/LGPL-3.0.txt, licenses/GPL-3.0.txt, licenses/GPL-2.0.txt

2) shiboken6
- Sürüm: 6.11.2
- Lisans: PySide6 ile aynı LGPL/GPL seçenekleri
- Rol: PySide6 bağlama katmanı

3) Qt 6.11.2 (PySide6_Essentials ile gelen runtime DLL/pluginler)
- Örnek: Qt6Core, Qt6Gui, Qt6Widgets, Qt6Network, Qt6Svg; platforms, imageformats, styles, tls, iconengines
- Dağıtım: onedir; DLL’ler ayrı dosya; LGPL değiştirme yolu için LGPL-NASIL-DEGISTIRILIR.txt

4) Python çalıştırma ortamı (PyInstaller ile gömülü)
- Bu paket build’inde kullanılan sürüm: 3.14.5
- Lisans: licenses/PSF-Python-LICENSE.txt

B) Derleme araçları / bootloader

5) PyInstaller 6.22.2
- GPLv2-or-later + bootloader istisnası: licenses/PyInstaller-COPYING.txt

6) pyinstaller-hooks-contrib 2026.6
- licenses/pyinstaller-hooks-contrib-LICENSE.txt

7) altgraph 0.17.5 — MIT — licenses/altgraph-LICENSE.txt
8) pefile 2024.8.26 — MIT — licenses/pefile-LICENSE.txt
9) pywin32-ctypes 0.2.3 — BSD-3-Clause — licenses/pywin32-ctypes-LICENSE.txt

C) Marka bildirimi
Cursor, OpenAI, ChatGPT, Codex, Anthropic, Claude, Google, Gemini, GitHub ve Copilot adları ilgili sahiplerinin markaları olabilir. TokenTakip bu kuruluşların resmi ürünü değildir.
"""

GUVENLIK = f"""TokenTakip — Güvenlik Bildirimi (Taslak)

Sürüm: {PH['SÜRÜM']}
Tarih: {PH['YAYIN TARİHİ']}
Yayıncı: {PH['GELİŞTİRİCİ']}
Güvenlik iletişim: {PH['EMAIL']}
Resmî indirme: {PH['URL']}

1. Kapsam
Bu belge, TokenTakip yazılımındaki olası güvenlik açıklarının sorumlu bildirimi içindir.

2. Bildirimde istenen bilgiler
- Etkilenen sürüm
- İşletim sistemi
- Açığın kısa tanımı ve yeniden üretme adımları (mümkünse)
- Etki tahmini
- İletişim e-postanız

3. Göndermemeniz gerekenler
- Gerçek erişim token’ı, parola, oturum çerezi
- Başkalarına ait kişisel veri veya sohbet dökümleri
- Zararlı yükün çalışır hâli

4. Süreç
Lütfen açığı herkese açık yerlerde duyurmadan önce makul bir süre yayıncıya bildirin. Bu, ödüllü bir bug bounty programı değildir.

5. Desteklenen sürüm
Öncelik güncel halka açık sürümdedir: {PH['SÜRÜM']}

6. Dosya bütünlüğü
Yalnızca {PH['URL']} üzerinden indirin.
Yayımlanan ZIP için SHA-256: {PH['SHA']}
Örnek (PowerShell): Get-FileHash .\\TokenTakip-0.1.0-win64.zip -Algorithm SHA256

7. Kod imzası
Bu paket şu anda dijital olarak imzalanmamıştır; Windows “bilinmeyen yayıncı” uyarısı gösterebilir.
"""

README = f"""TokenTakip {PH['SÜRÜM']}
{PH['YAYIN TARİHİ']}

1. Nedir?
TokenTakip, Windows’ta bilgisayarınızdaki yapay zekâ araçlarının kalan kota / kullanım bilgisini gösteren ücretsiz bir masaüstü uygulamasıdır. Kaynak kod paylaşılmaz (kapalı kaynak).

2. Desteklenen kota sağlayıcıları (izin açılırsa)
Cursor, Codex (ChatGPT oturumu), Claude, Gemini, GitHub Copilot.

3. Sistem gereksinimleri
- Windows için geliştirilmiştir; test edilen sürümler: [TEST EDİLEN WINDOWS SÜRÜMLERİ — YAYINCI DOLDURACAK]
- İnternet: yalnızca kota izni açıkken ilgili sağlayıcı API’leri için
- Yönetici yetkisi gerekmez

4. Kurulum / çalıştırma (onedir / klasör dağıtımı)
1) ZIP’i açın.
2) TokenTakip klasörünün tamamını koruyun; yalnız TokenTakip.exe’yi başka yere taşımayın (Qt DLL/plugin dosyaları klasörde olmalıdır).
3) TokenTakip.exe dosyasını çalıştırın.
4) İlk açılışta Yazılım Kullanım Lisansı’nı inceleyip kabul edin (kabul kota/sohbeti açmaz).
5) Ardından isteğe bağlı kota bilgilendirmesini okuyun.

5. İzinler (varsayılan: kapalı)
- Kota erişimi ve sohbet analizi ayrıdır; ikisi de varsayılan kapalıdır.
- İzinleri Ayarlar’dan istediğiniz zaman kapatabilirsiniz.

6. Kaldırma
Otomatik kaldırıcı programı yoktur.
1) Uygulamayı kapatın.
2) TokenTakip klasörünün tamamını silin.
3) İsteğe bağlı ileri düzey temizlik: Ayarlar’dan başlangıcı kapatın; gerekirse HKCU\\Software\\TokenTakip, Run anahtarı PulseTokenTakip, %LOCALAPPDATA%\\Pulse\\cache

7. LGPL kütüphaneleri
PySide6 / shiboken6 / Qt LGPL kapsamında ayrı dosyalar olarak gelir.
Değiştirme: LGPL-NASIL-DEGISTIRILIR.txt
Lisans metinleri: licenses/
Kaynak bilgisi: SOURCES.txt

8. Resmî indirme
{PH['URL']}
ZIP SHA-256: {PH['SHA']}
Dijital imza: Yok (bu pakette).

9. Bilinen sınırlamalar
- Sağlayıcı API veya oturum biçimi değişince özellik bozulabilir.
- İzin kapatılınca süren bir işlem kısa süre devam edebilir.
- Otomatik güncelleme yoktur.

10. Belgeler
LISANS-SOZLESMESI.txt, GIZLILIK-VE-AYDINLATMA.txt, UCUNCU-TARAF-BILDIRIMLERI.txt,
GUVENLIK-BILDIRIMI.txt, SURUM-NOTLARI.txt, LGPL-NASIL-DEGISTIRILIR.txt, SOURCES.txt, licenses/

İletişim: {PH['EMAIL']}
"""

SURUM = f"""TokenTakip — Sürüm Notları

Sürüm: {PH['SÜRÜM']}
Tarih: {PH['YAYIN TARİHİ']}
Yayıncı: {PH['GELİŞTİRİCİ']}

- Onedir (klasör) dağıtım; PySide6/Qt 6.11.2; Python 3.14.5; PyInstaller 6.22.2
- Kota erişimi ve sohbet analizi varsayılan kapalı; lisans kabulünden ayrıdır
- LGPL istisnası ve licenses/ tam metinleri eklendi
- Telemetri, reklam, otomatik güncelleme ve çevrimiçi lisans aktivasyonu yoktur
- Dijital imza yoktur

Güncelleme: {PH['URL']}
"""

LGPL_HOW = f"""TokenTakip — LGPL kütüphanelerini değiştirme (kısa bilgi)

Bu paket PySide6 6.11.2, shiboken6 6.11.2 ve Qt 6.11.2 bileşenlerini onedir klasöründe ayrı dosyalar olarak sunar.

1) TokenTakip klasörünün tamamını koruyun.
2) Değiştirdiğiniz uyumlu DLL/.pyd dosyalarını orijinaliyle aynı göreli yollara koyun
   (genelde _internal\\PySide6, _internal\\shiboken6, _internal\\PySide6\\plugins\\...).
3) ABI/sürüm uyumuna dikkat edin (bu paket: 6.11.2).
4) Uygulama, LGPL kütüphanelerini engellemek için hash/bütünlük kilidi kullanmaz.
5) Kaynak bilgisi: SOURCES.txt
6) Tam lisans metinleri: licenses\\LGPL-3.0.txt ve licenses\\GPL-3.0.txt

TokenTakip’in kendi kodu kapalı kaynaktır; LGPL yalnızca belirtilen kütüphaneleri kapsar.
"""

SOURCES = f"""TokenTakip — LGPL/GPL karşılık gelen kaynak bilgisi (taslak)

Paket runtime sürümleri (bu build):
- PySide6_Essentials / PySide6: 6.11.2
- shiboken6: 6.11.2
- Qt: 6.11.2 (qVersion)
- Python: 3.14.5
- PyInstaller: 6.22.2

Resmî kaynak adayları (indirme / barındırma hukuku için hukukçu onayı gerekir):
- Qt for Python / pyside-setup: https://code.qt.io/cgit/pyside/pyside-setup.git/
  ve https://download.qt.io/official_releases/QtForPython/
- Qt 6.11.2: https://download.qt.io/official_releases/qt/6.11/6.11.2/
- Python 3.14.5: https://www.python.org/downloads/release/python-3145/

Yalnızca bağlantı vermenin LGPL §4 / GPLv3 bakımından yeterliliği hukuken kesin kabul edilmemelidir.
Yayıncı seçenekleri: aynı indirme sayfasında kaynak arşivi barındırma veya yazılı kaynak sağlama teklifi.
TokenTakip özgün kapalı kaynak kodu, LGPL zorunlu kılmadığı sürece bu kaynak paketine dahil edilmez.

İletişim (kaynak talebi): {PH['EMAIL']}
Resmî sayfa: {PH['URL']}
"""

PLACEHOLDERS = f"""TokenTakip — Doldurulmamış alanlar (uydurulmadı)

Aşağıdaki yer tutucuları yayıncı / hukukçu doldurmalıdır:

[GELİŞTİRİCİNİN VEYA YAYINCININ TAM ADI]
[İLETİŞİM E-POSTASI]
[TEBLİGAT/İLETİŞİM ADRESİ]
[RESMÎ İNDİRME SAYFASI]
[YAYIN TARİHİ]
[YETKİLİ MAHKEME VE İCRA DAİRELERİ]
[TEST EDİLEN WINDOWS SÜRÜMLERİ — YAYINCI DOLDURACAK]
[HUKUKÇU TARAFINDAN BELİRLENECEK] (KVKK veri kategorileri)
[HUKUKÇU TARAFINDAN BELİRLENECEK — açık rıza / diğer KVKK md. 5-6 sebepleri uydurulmamıştır]
[HUKUKÇU: yurt dışı aktarım değerlendirmesi]
[HUKUKÇU: başvuru usulü, süre, kimlik doğrulama]
[HUKUKÇU KARARI] (aydınlatma vs açık rıza)
[YAYINCI TARAFINDAN DOLDURULACAK — ZIP SHA-256] (GUVENLIK/README içinde; ZIP üretildikten sonra güncellenebilir)

Not: Bu paket hukuki inceleme tamamlanmadan “hukuken kesinleşmiş” sayılmamalıdır.
"""


def main() -> None:
    assert BUILD.is_dir(), BUILD
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(BUILD, OUT)

    docs = {
        "LISANS-SOZLESMESI.txt": LISANS,
        "GIZLILIK-VE-AYDINLATMA.txt": GIZLILIK,
        "UCUNCU-TARAF-BILDIRIMLERI.txt": UCUNCU,
        "GUVENLIK-BILDIRIMI.txt": GUVENLIK,
        "README.txt": README,
        "SURUM-NOTLARI.txt": SURUM,
        "LGPL-NASIL-DEGISTIRILIR.txt": LGPL_HOW,
        "SOURCES.txt": SOURCES,
        "DOLDURULACAK-ALANLAR.txt": PLACEHOLDERS,
    }
    for name, text in docs.items():
        (OUT / name).write_text(text.replace("\n", "\r\n"), encoding="utf-8")

    lic_dst = OUT / "licenses"
    lic_dst.mkdir(exist_ok=True)
    for f in LIC_SRC.iterdir():
        if f.is_file():
            shutil.copy2(f, lic_dst / f.name)

    assert (OUT / "LISANS-SOZLESMESI.txt").is_file()

    py_files = [str(p.relative_to(OUT)) for p in OUT.rglob("*.py")]
    if py_files:
        raise SystemExit(f"open py in package: {py_files}")

    secret_re = re.compile(
        r"(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|"
        r"-----BEGIN (RSA |OPENSSH )?PRIVATE KEY-----)",
        re.I,
    )
    for p in OUT.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() in {".dll", ".pyd", ".exe", ".png", ".ico", ".qml", ".pak"}:
            continue
        if p.stat().st_size > 2_000_000:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if secret_re.search(text):
            raise SystemExit(f"possible secret in {p}")

    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(OUT.rglob("*")):
            if p.is_file():
                zf.write(p, arcname=str(Path("TokenTakip-0.1.0-win64") / p.relative_to(OUT)))

    digest = hashlib.sha256(ZIP.read_bytes()).hexdigest().upper()
    (OUT.parent / "TokenTakip-0.1.0-win64.sha256.txt").write_text(
        f"{digest}  TokenTakip-0.1.0-win64.zip\n", encoding="utf-8"
    )
    (OUT.parent / "SHA256-VE-DOLDURULACAK.txt").write_text(
        f"ZIP: {ZIP}\nSHA-256: {digest}\n\n"
        f"ZIP içindeki GUVENLIK/README alanına isterseniz bu SHA-256 değerini yazın "
        f"(içeriği değiştirirseniz SHA yeniden hesaplanmalıdır).\n"
        f"Kişisel/hukuki yer tutucular: TokenTakip-0.1.0-win64\\DOLDURULACAK-ALANLAR.txt\n"
        f"Belgeler hukuki taslaktır; hukukçu onayı şarttır.\n",
        encoding="utf-8",
    )
    print("OUT", OUT)
    print("ZIP", ZIP)
    print("SHA256", digest)
    print("files", sum(1 for _ in OUT.rglob("*") if _.is_file()))


if __name__ == "__main__":
    main()
