# Hisse Çıta Sonuçları (2026-11-02)

- **Veri:** Yahoo Finance. Fiyatlar temettü ve bölünmelere göre düzeltildi, yani temettüler dahil.
- **Komisyon:** %0,1.
- **Kural:** Kriptodaki trend kuralının aynısı. Günlük kapanış 100 günlük ortalamanın üstündeyse içeride kal, altına inerse nakite geç.
- **Script:** `hisse/hisse_cita.py` (sunucuda `~/kripto_bot/hisse/`)

## 2022-01 → 2026-11 (kâr % / en büyük düşüş %)

### Borsa İstanbul

| | Al-tut (TL) | Trend (TL) | **Al-tut ($)** | **Trend ($)** |
|---|---|---|---|---|
| XU100 (endeks) | +471 / −27 | +266 / −32 | **+49 / −35** | +23 / −41 |
| THYAO | +1072 | +488 | +207 | +106 |
| ASELS | +3178 | +1169 | +757 | +409 |
| GARAN | +1260 | +564 | +256 | +108 |
| BIMAS | +1131 | +697 | +222 | +154 |
| TUPRS | +2246 | +1348 | +514 | +468 |
| EREGL | +148 | −3 | −35 | −55 |
| SISE | +157 | +52 | −33 | −34 |

Bu dönemde dolar/TL kuru %+274 arttı.

### ABD

| | Al-tut | Trend |
|---|---|---|
| SPY (S&P 500 endeksi) | +69 / −26 | +49 / −18 |
| QQQ (Nasdaq 100 endeksi) | +78 / −36 | +33 / −24 |
| NVDA | +592 / −64 | +328 / −40 |
| TSLA | −1 / −74 | −48 / −55 |
| AMZN | +36 / −51 | −19 / −50 |
| META | +82 / −74 | +154 / −46 |

### Uzun dönem (2010–2026), endeksler

| | Al-tut | Trend |
|---|---|---|
| XU100, TL | +1969 / −34 | +286 / −55 |
| **XU100, dolar** | **−39 / −76** | −63 / −80 |
| SPY | +802 / −32 | +297 / −20 |

## Çıkarımlar

1. **Trend kuralı hisselerde neredeyse her yerde al-tut'tan daha az kazandırdı.** Bitcoin'deki kadar işe yaramıyor. Hisseler uzun vadede yavaş ve istikrarlı yükseldiği için kural sık sık "çık-gir" yapıp yükselişleri kaçırıyor. Tek faydası endekslerde düşüşü azaltması (SPY'de %−32 yerine %−20). Bunun bedeli de kârın yaklaşık üçte ikisi.
2. **BIST'in TL getirileri büyük ölçüde enflasyon yanılgısı.** XU100, 2010'dan bu yana TL bazında %1969 kazandırmış gibi görünüyor. Dolar bazında ise **%39 kaybettirmiş**. Gerçek kazancı ölçmek için dolar sütunlarına bakmak gerekiyor.
3. **Hayatta kalan yanılgısı burada da var.** NVDA, ASELS, TUPRS gibi hisseleri bugün büyük oldukları için seçtik. 2010'da kimse bunların bu kadar yükseleceğini bilemezdi. Tek tek hisse sonuçları bu yüzden olduğundan iyi görünüyor. Endeks sonuçları (XU100, SPY, QQQ) daha dürüst bir ölçü.
4. **Bot açısından:** Hisselerde basit bir otomatik al-sat kuralı, endeksi alıp tutmayı geçemedi. Hisselerde bot yapmak istiyorsak, al-tut'u geçen bir şey bulmamız gerekiyor. Kriptodaki deneyimimiz bunun zor olduğunu gösteriyor.

Not: Bu bir yatırım tavsiyesi değil. Geçmiş verinin ne gösterdiğinin özeti.
