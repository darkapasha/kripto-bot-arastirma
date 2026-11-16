# ₿ Yapay Zekâ Bitcoin'de Para Kazanabilir mi?

### Bir araştırma raporu · Kasım 2026

> **Özet:** Bitcoin'i otomatik alıp satan bir bot için dokuz yıllık veride beş kural tabanlı strateji, üç ayrı
> yapay zekâ yaklaşımı ve 691 coinlik bir momentum testi denendi; ardından en iyisi sahte parayla canlıya
> alındı. **Kazanan en basit kural oldu:** *"Günlük kapanış 100 günlük ortalamanın üstündeyse elde tut, altındaysa
> nakite geç."* Hiçbir yapay zekâ modeli bu kuralı geçemedi. Proje 17 Kasım 2026'da kapatıldı.

⚠️ *Bu bir merak projesidir, yatırım tavsiyesi değildir. Geçmişte işleyen bir kural gelecekte de işleyecek demek değildir.*

---

## 1. Soru ve yöntem

**Soru:** Kendi sunucumda çalışan bir bot, Bitcoin'i alıp satarak "al ve unut"tan daha fazla kazandırabilir mi?
Yapay zekâ bunu daha iyi yapabilir mi?

**Kurallar (hepsi testlerde aynı):**
- Binance BTC/USDT verisi, 2017-08 → 2026-11
- Başlangıç 1.000 USDT, kaldıraç yok, her işlemde tüm bakiye
- Her alış ve satışta **%0,1 komisyon**
- "En büyük düşüş": portföyün zirveden dibe en büyük kaybı (günlük değerle)
- Yapay zekâ modelleri **walk-forward** eğitildi: model her seferinde yalnızca geçmişi gördü, test ettiği dönemi asla görmedi
- Başarı ölçütü testten **önce** yazıldı (sonradan hedef kaydırmamak için)

**Araçlar:** [Freqtrade](https://www.freqtrade.io) (Docker, ARM sunucu), FreqAI + LightGBM, Kronos (finans temel modeli), Python.

## 2. Çıta: kural tabanlı stratejiler

| Strateji | 2018–2026 | 2022–2026 | En büyük düşüş (2022–26) | İşlem |
|---|---|---|---|---|
| Al-tut | +474 % | +62 % | −67 % | 1 |
| **Trend günlük** (kapanış > SMA100) | **+1466 %** | **+156 %** | **−36 %** | 59 |
| EMA kesişimi (saatlik 50/200) | +406 % | +47 % | −44 % | 230 |
| RSI dönüşü (saatlik 30/70) | **−94 %** | −74 % | — | 384 |
| Haftalık 10 $ birikim (DCA) | +376 % | +82 % | −49 % | 461 alım |

**Okuma:**
- **Sık işlem yapan strateji komisyona yenildi.** RSI stratejisi işlemlerin %57'sini kazandı ama paranın %94'ünü kaybetti.
- **Yavaş trend kuralı**, zamanın yaklaşık yarısında nakitte bekleyerek 2018 ve 2022 çöküşlerinin büyük kısmından kaçtı.
- Bu, yapay zekânın geçmesi gereken çıtayı belirledi: **2022–2026'da +156 % kâr, en fazla −36 % düşüş.**

### Diğer coinler
Aynı kurallar en büyük 10 coinde (ETH, BNB, SOL, XRP, ADA, DOGE, AVAX, LINK, LTC) denendi. **Hiçbir kural hepsinde işlemedi.**
Trend kuralı BTC'de +157 % yaparken ETH'de +30 %, XRP'de −46 %, LTC'de −73 % yaptı. 10 coinlik trend sepeti
+26 % kâr ve −58 % düşüşle **BTC'nin tek başına gerisinde** kaldı.

## 3. Yapay zekâ denemeleri

| # | Yaklaşım | Sonuç | Neden olmadı |
|---|---|---|---|
| 1 | **LightGBM** (FreqAI): ~400 gösterge, "24 saat sonra fiyat ne olacak?", 59 model | En iyi varyant +48 % | 42.359 tahminde tahmin–gerçek korelasyonu **−0,01**; yön isabeti %50,6 (yazı tura) |
| 2 | **Meta model**: "Trend kuralına bu sefer güvenilir mi?" 20 günlük ufuk, 10 coin, korku-açgözlülük endeksi, funding | +34 % / +23 % | AUC 0,475 / 0,510; önceden yazılan ölçütü geçemedi |
| 3 | **Kronos-small** (finans için önceden eğitilmiş zaman serisi modeli) | Trend + Kronos −5 % | AUC 0,499; bazı yıllarda 0,55–0,65 görünse de seviye kayıyor, güvenilmez |

**Ortak ders:** Herkesin baktığı göstergeler zaten fiyata yansımış. Kısa vadeli hareket büyük ölçüde rastgele.
Trend kuralı ise aylarca süren büyük hareketleri yakalıyor; yapay zekânın oraya ekleyebileceği bir şey bulunamadı.
İyi tarafı: korelasyonun sıfır çıkması, testlerin dürüst olduğunu (modelin geleceği "görmediğini") da gösteriyor.

## 4. "Ani yükselen coini al" fikri

691 Binance coini (borsadan çıkarılanlar dahil, hayatta kalma yanılgısını önlemek için) tarandı.
**Sert bir yükselişten sonra fiyat ortalama düşüyor** (7 günlük medyan −8 %). Bu kuralla kurulan bot sıfıra gitti.

## 5. Trend kuralı gerçekten iyi mi, yoksa şans mı?

| Test | Sonuç |
|---|---|
| Giriş-çıkış zamanları karıştırılmış 5.000 sahte botla kıyas | 2018–26: %95,5'ini geçiyor (p ≈ 0,045) · 2022–26: %87,1 (p ≈ 0,13, zayıf) |
| SMA uzunluğu 50 → 200 arası | Hepsinde çalışıyor, tek bir "sihirli sayı"ya bağlı değil |
| Komisyon 5 katına (%0,5) çıksa | 2022–26 hâlâ +100 % (yılda ~6 işlem yaptığı için) |
| Kelly ölçütü | ≈ 2,1 → yarım Kelly = kaldıraçsız tam pozisyon |
| Aylık dağılım | Ortalama ~%2,6/ay, ama ayların **%38'i eksi** |

Yani bir avantaj var gibi görünüyor ama zayıf, ve sabır istiyor: kötü aylar sık.

## 6. Sahte parayla canlı deneme

| | |
|---|---|
| Başlangıç | 2 Kasım 2026, 1.000 sanal USDT |
| Alış | 77.827 $'dan 0,01272 BTC |
| Satış | 6 Kasım 00:00 UTC, fiyat 100 günlük ortalamanın altına inince: 76.098 $ |
| Sonuç | **−2,4 %** (−24 $) |
| Sonrası | BTC 17 Kasım'da ~65.000 $; elde tutsaydı kayıp ~−16 % olacaktı |

Kural yapması gerekeni yaptı: düşüş başlayınca çıktı ve büyük kaybı önledi. Ama bu tek bir işlem; bir şey kanıtlamaz.

## 7. Sonuç

1. **Basit, yavaş bir trend kuralı** bu veride hem al-tut'tan hem de denenen tüm yapay zekâ modellerinden iyiydi.
2. **Yapay zekâ kendi başına sihir değil.** Herkesin elindeki fiyat verisinden kısa vadeli tahmin, yazı turadan iyi çıkmadı.
3. **Sık işlem ve "hızlı zengin olma"** stratejileri (RSI, yükseleni kovalama, martingale) uzun vadede para kaybettirdi.
4. Proje gerçek parayla hiç çalışmadı ve kapatıldı.

## Dosyalar

| Rapor | İçerik |
|---|---|
| [ARASTIRMA.md](ARASTIRMA.md) | Başlangıç araştırması: borsalar, yasal durum, araçlar, plan |
| [CITA_SONUCLARI.md](CITA_SONUCLARI.md) | Kural tabanlı stratejiler, 10 coin |
| [YZ_SONUCLARI.md](YZ_SONUCLARI.md) | Üç yapay zekâ denemesinin ayrıntıları |
| [MOMENTUM_VE_AVANTAJ.md](MOMENTUM_VE_AVANTAJ.md) | 691 coin momentum testi, trend kuralının istatistiksel testi |
| [HISSE_SONUCLARI.md](HISSE_SONUCLARI.md) | Aynı kuralların BIST ve ABD hisselerinde denenmesi |
| [CANLI_DENEME.md](CANLI_DENEME.md) | Sahte parayla canlı denemenin kurulumu |
| `user_data/strategies/` | Freqtrade stratejileri |
| `para_yonetimi.py` | Martingale ve Kelly simülasyonları |

---

Claude ile birlikte, vibe coding ile yapıldı 🎧
