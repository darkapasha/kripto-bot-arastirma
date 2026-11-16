# Yapay Zekâ (LightGBM) Sonuçları: Deneme 1 (2026-11-02)

## Ne yapıldı?

- **Model:** LightGBM (FreqAI), BTC/USDT saatlik.
- **Soru:** "24 saat sonra fiyat yüzde kaç değişmiş olacak?"
- **Modelin gördüğü bilgiler:** BTC ve ETH'nin 1 saatlik, 4 saatlik ve günlük göstergeleri (RSI, MFI, ADX, momentum, ortalamaya uzaklık, oynaklık, hacim). Toplam yaklaşık 400 özellik.
- **Walk-forward:** Model her 30 günde bir, sadece önceki 365 günü görerek yeniden eğitildi. 2022–2026 arasında 59 ayrı model eğitildi. Hiçbir model test ettiği dönemi önceden görmedi.
- **Kurallar:** Tahmin eşiği geçerse al, tahmin eksiye dönünce sat. Komisyon %0,1.
- **Dosyalar:** `user_data/strategies/yapay_zeka.py`, `user_data/config_freqai.json`, `yz_backtest.sh`

## Sonuçlar (2022-01 → 2026-11, 1000 USDT ile)

| Strateji | Kâr | En büyük düşüş | İşlem |
|---|---|---|---|
| **Çıta: Trend günlük (yapay zekâ yok)** | **%+157** | **%−36** | 31 |
| Çıta: Al-tut | %+62 | %−67 | 1 |
| Yapay zekâ (eşik %1) | %+16 | %−45 | 312 |
| Yapay zekâ + trend filtresi | %+3 | %−31 | 137 |
| Yapay zekâ (eşik %0,5) | %−30 | %−46 | 507 |
| Yapay zekâ (eşik %2) | %+48 | %−42 | 147 |

**Hiçbir yapay zekâ varyantı ne trend kuralını ne de al-tut'u geçti.**

## Model gerçekten bir şey öğrendi mi?

`user_data/tahmin_kalitesi.py` ile 42.359 saatlik tahmin, gerçekte olanla karşılaştırıldı:

- **Tahmin ile gerçek arasındaki korelasyon: −0,01.** Yani sıfır, ilişki yok.
- **Yön isabeti: %50,6.** Yazı-tura ile aynı. Piyasa zaten saatlerin %51'inde yükselmiş.
- Yıllara göre korelasyon −0,07 ile +0,06 arasında gidip geliyor. Tutarlı bir yön yok.

**Anlamı:** Model, fiyat göstergelerinden 24 saat sonrasını tahmin edemiyor. Kâr eden varyantlar şans eseri kazandı. Örneğin eşik %2'nin kârının neredeyse tamamı 2024–2025'ten geliyor, 2022 ve 2026'da zarar etmiş.

**İyi haber:** Sonuçlar dürüst. Korelasyonun sıfır çıkması, modelin "kopya çekmediğini" (geleceği görmediğini) de gösteriyor. Sızıntı olsaydı korelasyon şüpheli derecede yüksek çıkardı.

## Neden işe yaramadı?

1. **Herkes aynı göstergelere bakıyor.** RSI, ortalama gibi bilgiler zaten fiyata yansımış durumda. Bunlardan ek bilgi çıkarmak çok zor.
2. **24 saat çok kısa.** Kısa vadeli hareketler büyük ölçüde rastgele. Trend kuralı ise aylarca süren hareketleri yakalıyor.
3. **Komisyon.** 300–500 işlem × %0,2 gidiş-dönüş, küçük avantajları siliyor.

## Deneme 2: "Trend kuralına ne zaman güvenmeyelim?" (2026-11-02)

Script: `user_data/deneme2.py`.

**Nasıl çalıştı:** Trend kuralı "içeride ol" dediği her gün model şunu tahmin etti: "Önümüzdeki 20 günde fiyat yükselecek mi?" Model "hayır" derse o gün trend kuralına uyulmadı.
- Eğitim verisi 10 coinden birlikte geldi.
- Model her ay yeniden eğitildi.
- Eğitimde, cevabı test başlangıcından önce kesinleşmemiş günler atıldı (22 günlük arındırma).
- Model ayarları önceden sabitlendi, sonuçlara göre değiştirilmedi.

**Başarı ölçütü (sonuçlardan önce yazıldı):** Trend kuralını hem kârda hem düşüşte geçmesi ve tüm coinlerde AUC > 0,55 olması.

AUC, modelin tahmin gücünü ölçen bir puan: 0,5 yazı-tura demek, 1,0 kusursuz tahmin.

| | Kâr | En büyük düşüş | İşlem | AUC (tüm coinler) | AUC (BTC) |
|---|---|---|---|---|---|
| **Çıta: Trend günlük** | **%+157** | %−36 | 31 | – | – |
| A: fiyat özellikleri | %+34 | %−27 | 79 | 0,475 | 0,357 |
| B: + Fear & Greed + fonlama oranı | %+23 | %−26 | 68 | 0,510 | 0,426 |

**Sonuç: iki deney de başarısız.**
- Düşüşü biraz azalttılar, ama kârın çoğunu da götürdüler.
- AUC yazı-tura seviyesinde, BTC'de ise altında. 2022'de 0,32–0,33'e kadar düştü.
- Bunun muhtemel sebebi şu: Model 2018–2021'in boğa piyasasında "trend devam eder" desenini öğrendi. 2022'de ise trend günlerinin çoğu düşüş piyasası içindeki geçici yükselişlerdi, yani öğrendiği desen tersine döndü.
- AUC'nin 0,5'in altında olması, "modelin tersini yaparsak kazanırız" anlamına gelmiyor. Bu, sonuca bakıp kural uydurmak olur.

**Genel sonuç (deneme 1 + 2):** Herkese açık fiyat, duygu ve fonlama verisiyle, bu sunucunun kaldırabileceği klasik modeller basit trend kuralını geçemedi. Daha büyük modeller (GPU) bu tabloyu değiştirir mi belirsiz. Araştırmalar da bunu desteklemiyor.

## Deneme 3 için kalan fikirler (yapılmadı)

Not: Çok fazla deneme yapmak da tehlikeli. 50 şey denersek biri şans eseri iyi çıkar. Bu yüzden denemeler önceden planlanmalı ve sayısı sınırlı tutulmalı.

- **Daha uzun ufuk:** Günlük veriyle "önümüzdeki 7–30 günde yükselir mi?" sorusu. Trend kuralının işe yaradığı zaman ölçeği bu.
- **Fiyat dışı bilgiler:** Fear & Greed endeksi, vadeli piyasa fonlama oranları (funding rate), haber duygu puanı.
- **Görev değiştirme:** "Ne zaman alayım?" yerine "trend kuralına ne zaman güvenmeyeyim?". Yani yapay zekâ, trend kuralının yanlış sinyallerini elemeye çalışır.
- ~~Hazır finans modeli (Kronos)~~ → deneme 3 olarak yapıldı, başarısız.

## Deneme 3: Kronos-small, sıfır eğitim (2026-11-02) — BAŞARISIZ

Hazır finans modeli Kronos-small, BTC günlük mumlarla (400 günlük geçmiş, 20 gün ileri, her 5 günde bir tahmin, 5 örnek ortalaması) 2022-01 → 2026-10 arasında 353 tahmin üretti. Sunucu CPU'sunda ~5,5 saat sürdü. Script'ler: `kronos_calis/`.

Önceden yazılan ölçütler: (1) AUC > 0,55, (2) Trend+Kronos trendi hem kârda hem düşüşte geçmeli, (3) Sadece Kronos al-tut'u geçmeli.

| Ölçüt | Sonuç | Durum |
|---|---|---|
| AUC (yön, tüm dönem) | 0,499 (korelasyon −0,06, isabet %48) | ✗ |
| Trend + Kronos | %−5 kâr / %−23 düşüş (trend: %+157 / %−36) | ✗ |
| Sadece Kronos | %−15 (al-tut: %+62) | ✗ |

| Strateji | Kâr | En büyük düşüş | İşlem |
|---|---|---|---|
| Al-tut | %+62 | %−67 | 0 |
| **Trend** | **%+157** | %−36 | 31 |
| Sadece Kronos | %−15 | %−62 | 24 |
| Trend + Kronos | %−5 | %−23 | 14 |

- İlginç ayrıntı: yıl yıl bakınca AUC 0,55–0,65 arasında, ama hepsi birlikte 0,50. Yani model "yılın içinde hangi dönem daha iyi" sırasını biraz tutturuyor, ama tahmin ettiği sayıların seviyesi yıldan yıla kayıyor. Sabit bir "yükseliş bekliyorsa al" eşiğiyle bu işe yaramıyor.
- Bunu düzeltmek için eşiği yıllara göre ayarlamak, sonuca bakıp kural uydurmak olur. Yapılmadı.

**Genel sonuç (deneme 1 + 2 + 3):** Üç farklı yapay zekâ yaklaşımı (kendi eğittiğimiz LightGBM, trende güven filtresi, hazır finans modeli) basit trend kuralını geçemedi. Canlı kağıt botta trend kuralı tek başına kalıyor.
