# ₿ Kripto Bot Araştırması

"Yapay zekâ BTC alıp satarak para kazanabilir mi?" sorusuna dürüst bir deney. Freqtrade (Docker) ile
2018–2026 verisinde onlarca strateji, üç yapay zekâ denemesi ve iki hafta kâğıt üzerinde (gerçek parasız) canlı deneme.

**Kısa cevap:** En iyisi en basit kural çıktı. Yapay zekâ denemelerinin hiçbiri onu geçemedi.
Bot 2026-11-17'de durduruldu; bu depo sonuçları saklamak için.

## Sonuçlar

| Deneme | Sonuç (2022–2026) | Not |
|---|---|---|
| **Trend kuralı** (günlük kapanış > 100 günlük ortalama ise elde tut) | **+156 %**, en kötü düşüş −36 % | Karıştırılmış rastgele botların %95,5'ini geçiyor; SMA 50–200 arası hep çalışıyor |
| Saatlik RSI 30/70 | −94 % | Komisyon ve gürültü yiyor |
| 10 coin trend sepeti | +26 %, −58 % | BTC tek başına daha iyi |
| YZ 1: FreqAI LightGBM | en iyi +48 % | Tahmin ile gerçek arasında ilişki yok (korelasyon −0.01) |
| YZ 2: "trende güvenilir mi?" meta modeli | +34 % | Önceden belirlenen başarı ölçütünü geçemedi |
| YZ 3: Kronos (finans temel modeli) | trend + Kronos −5 % | AUC 0.499 ≈ yazı tura |
| Ani yükselişi alma (691 coin) | sıfıra gitti | Yükselişten sonra fiyat ortalama düşüyor |

Raporlar: [ARASTIRMA](ARASTIRMA.md) · [Çıta sonuçları](CITA_SONUCLARI.md) · [YZ sonuçları](YZ_SONUCLARI.md) ·
[Momentum ve avantaj testi](MOMENTUM_VE_AVANTAJ.md) · [Hisse senetleri](HISSE_SONUCLARI.md) · [Canlı deneme](CANLI_DENEME.md)

⚠️ Yatırım tavsiyesi değildir. Geçmişte işleyen bir kural gelecekte de işleyeceği anlamına gelmez.

---
Claude Code ile birlikte geliştirildi.
