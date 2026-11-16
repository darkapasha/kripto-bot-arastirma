# Çıta Backtest Sonuçları (2026-11-02)

Ayarlar: BTC/USDT (Binance), spot, kaldıraç yok, 1000 USDT başlangıç, her işlemde tüm bakiye, **%0,1 komisyon** (alışta ve satışta ayrı ayrı). Veri 2017-08 → 2026-11.

"Max düşüş", portföy değerinin zirveden dibe en büyük kaybı. Günlük değerden hesaplandı. Freqtrade'in kendi tablosu sadece kapanmış işlemlere baktığı için düşüşü daha küçük gösteriyor.

## Toplam kâr

| Strateji | 2018–2026 | 2018–2021 | 2022–2026 | İşlem sayısı (2018–26) |
|---|---|---|---|---|
| **Al-tut** | %+474 | %+242 | %+62 | 1 |
| **TrendGünlük** (kapanış > 100 günlük ortalama) | **%+1466** | **%+512** | **%+156** | 59 |
| EmaKesişim (saatlik EMA50/200) | %+406 | %+246 | %+47 | 230 |
| RsiDönüş (saatlik RSI 30/70) | **%−94** | %−79 | %−74 | 384 |
| DCA (haftada 10 USDT)* | %+376 | %+395 | %+82 | 461 alım |

\*DCA'da para zamana yayılarak yatırıldığı için yüzdesi diğerleriyle doğrudan kıyaslanamaz.

## Gerçek en büyük düşüş

| | 2018–2026 | 2022–2026 |
|---|---|---|
| Al-tut | %−81 | %−67 |
| TrendGünlük | %−60 | %−36 |
| DCA | %−75 | %−49 |

## Çıkarımlar

1. **Sık işlem yapan basit stratejiler komisyona yeniliyor.** RsiDönüş işlemlerin %57'sini kazanmasına rağmen paranın %94'ünü kaybetti: küçük kazançlar, komisyon ve büyük zararlarla eridi.
2. **Yavaş trend filtresi en iyisi çıktı.** TrendGünlük zamanın yarısında nakitte bekleyerek 2018 ve 2022 düşüş yıllarını büyük ölçüde atladı. Geleceği görme (lookahead) hatası olmadığı freqtrade'in kendi aracıyla doğrulandı.
   - **Uyarı:** 100 günlük ortalama, BTC'de geçmişte işe yaradığı bilinen bir kural. Gelecekte de aynı şekilde çalışacağının garantisi yok. %−60'lık düşüş de hâlâ çok sert.
3. **Yapay zekânın geçmesi gereken çıta:** 2022–2026 döneminde **%+156 kâr ve en fazla %−36 düşüş** (TrendGünlük). Bunu geçemeyen bir model gereksiz karmaşıklık demek.

## Sunucudaki düzen

- `~/kripto_bot/docker-compose.yml`: Freqtrade 2026.10 (Docker, arm64)
- `~/kripto_bot/user_data/config.json`: sadece dry-run, API anahtarı yok, Telegram kapalı
- `~/kripto_bot/user_data/strategies/cita_stratejileri.py`: AlTut, TrendGunluk, EmaKesisim, RsiDonus
- `~/kripto_bot/user_data/dca.py`: DCA hesabı
- `~/kripto_bot/cita_backtest.sh`: hepsini üç dönemde yeniden çalıştırır
- Veri: `user_data/data/binance/BTC_USDT-{1h,4h,1d}.feather`. Güncellemek için `download-data` tekrar çalıştırılır.

## Diğer coinler (eklendi 2026-11-02)

Bugünün en büyük 10 coini test edildi: BTC, ETH, BNB, SOL, XRP, ADA, DOGE, AVAX, LINK, LTC. Script: `user_data/coin_cita.py`. Bu script BTC'de Freqtrade'le aynı sonucu veriyor.

### 2022–2026, coin bazında (kâr % / en büyük düşüş %)

| Coin | Al-tut | Trend günlük | EMA saatlik |
|---|---|---|---|
| BTC | +62 / −67 | **+157 / −36** | +46 / −44 |
| ETH | −40 / −74 | +30 / −52 | 0 / −53 |
| BNB | +33 / −63 | +84 / −53 | +31 / −51 |
| SOL | −46 / −95 | −17 / −80 | +375 / −65 |
| XRP | +48 / −72 | −46 / −78 | −19 / −74 |
| ADA | −86 / −91 | −36 / −70 | −1 / −81 |
| DOGE | −56 / −85 | −17 / −70 | +87 / −64 |
| AVAX | −93 / −95 | −13 / −74 | −30 / −90 |
| LINK | −45 / −82 | −28 / −74 | +38 / −77 |
| LTC | −63 / −73 | −73 / −78 | −87 / −91 |

### 10 coinlik sepet (Freqtrade, para 10'a bölünür)

| | 2018–2026 | 2022–2026 |
|---|---|---|
| Sepet al-tut | %+2212, düşüş %−75 | %−28, düşüş %−70 |
| Sepet trend günlük | %+4694, düşüş %−66 | %+26, düşüş %−58 |
| *Sadece BTC trend (karşılaştırma)* | *%+1466, düşüş %−60* | ***%+157, düşüş %−36*** |

### Çıkarımlar

1. **Hiçbir kural her coinde işe yaramıyor.** Trend, BTC'de en iyisi ama XRP'de en kötüsü. EMA SOL'da çok iyi, LTC'de felaket. Tek bir coindeki parlak sonuç büyük ihtimalle şans.
2. **2022'den beri coinlerin çoğu al-tut'la zarar ettirdi.** ADA ve AVAX %86–93 eridi. Trend kuralı bu zararları küçülttü ama çoğunu kâra çeviremedi.
3. **Coin eklemek son dönemde riski azaltmadı, artırdı.** Sepet, sadece BTC'den hem daha az kazandırdı hem daha çok düşüş yaşattı. Sebebi: coinler hep birlikte iniyor ve küçük coinler daha sert düşüyor.
4. **2018–2026 sepet sonucu yanıltıcı.** Bugün ilk 10'da olan coinleri seçtik, yani hayatta kalanları. 2018'in ilk 10'unda olup sonradan çöken coinler (EOS, BCH, IOTA gibi) bu testte yok. Buna "hayatta kalan yanılgısı" (survivorship bias) deniyor. Gerçekte o dönem bu kadar iyi olmazdı.
5. **Yapay zekâ için anlamı:** Çıta değişmedi, hâlâ BTC trend (2022–26: %+157 / %−36). Diğer coinler modele **daha fazla eğitim örneği** olarak faydalı olabilir, ama kendi başlarına bir avantaj sağlamadılar.

## Sıradaki adım

FreqAI + LightGBM: saatlik veriden özellikler üretilir, model walk-forward yöntemiyle (her ay sadece geçmişi görerek yeniden) eğitilir, komisyon filtresi eklenir ve sonuç TrendGünlük çıtasıyla 2022–2026'da karşılaştırılır.
