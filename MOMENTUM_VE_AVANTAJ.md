# Momentum Testi ve Trend Botunun Avantaj Testi (2026-11-02)

## A. Momentum: "ani yükselen coine atla, yükseliş bitince in"

**Veri:** Binance'teki tüm USDT spot pariteleri. Toplam **691 coin**, sonradan borsadan silinenler dahil. Saatlik mumlar, 2022-01 → 2026-10. Script'ler `momentum/` klasöründe.

**Kurallar** (önceden sabitlendi, `momentum/momentum_test.py` başında yazılı):
- **Filtre:** Son 24 saatlik hacim ≥ 500 bin $ ve en az 7 günlük geçmiş.
- **Sinyal:** Son L saatte en az %X yükseliş ve son saatin hacmi normalin en az V katı.
- **Çıkış:** Zirveden %Z düşüşte ya da en fazla H saat sonra.
- **Pozisyon:** En fazla 5 pozisyon, her biri paranın beşte biri.
- **Maliyet:** Her alış ve satışta %0,1 komisyon + %0,2 kayma.

### 1) Strateji sonucu (V1: 4 saatte ≥%8, hacim 5 kat, zirveden %5 düşüşte sat)

| İşlem | Kazanan | Ort. kazanç | Ort. kayıp | Kâr faktörü | Sonuç |
|---|---|---|---|---|---|
| 21.739 | %24 | %+10,9 | %−6,4 | 0,32 | **Para sıfırlandı (her yıl)** |

Üç varyantın hepsi aynı sonuca vardı, kayma sıfır kabul edilse bile:

| Varyant | İşlem | Kazanan | Ort. kazanç / kayıp | Sonuç (kayma %0,2) | Sonuç (kayma 0) |
|---|---|---|---|---|---|
| V1 orta (4 saatte ≥%8) | 21.739 | %24 | +10,9 / −6,4 | %−100 | %−100 |
| V2 hızlı (1 saatte ≥%5) | 30.634 | %22 | +8,8 / −5,1 | %−100 | %−100 |
| V3 yavaş (24 saatte ≥%15) | 9.421 | %23 | +17,7 / −9,6 | %−100 | %−100 |

Rastgele coin alan kontrol botları da sıfırlandı. Küçük coinlerde sıkı stopla sık işlem yapmak tek başına bile yıkıcı. Ani yükseliş sinyali ise bunu düzeltmiyor, tersine olay analizine göre daha da kötüleştiriyor.

İşlem başına ortalama sonuç yaklaşık **%−2,3**. "200 kaybet, 300 kazan" mantığı tersine işliyor: kayıpların toplamı, kazançların toplamının yaklaşık 3 katı.

### 2) Olay analizi: Ani yükselişten SONRA fiyat ne yapıyor? (komisyonsuz)

Script: `momentum/olay_analizi.py`. Parantez içindeki değer, aynı saatlerde tüm coinlerin ortalaması.

| Sinyal | Sayı | 1 saat | 24 saat | 7 gün | 7 gün medyan | 24 saat sonra yükselmiş olan |
|---|---|---|---|---|---|---|
| V1: 4 saatte ≥%8 | 76.750 | %−0,49 (+0,02) | %−2,20 (+0,07) | %−3,87 (0,00) | **%−8,6** | %30 |
| V2: 1 saatte ≥%5 | 48.162 | %−0,72 (+0,05) | %−2,52 (+0,09) | %−3,97 (+0,20) | **%−8,0** | %30 |
| V3: 24 saatte ≥%15 | 159.236 | %−0,25 (0,00) | %−2,00 (+0,14) | %−2,96 (+0,14) | **%−8,5** | %31 |

**Sonuç:** Ani yükselen coin, komisyon hiç olmasa bile **ortalamada düşüyor.**
- 1 saat sonra bile ortalama eksi.
- 1 hafta sonra tipik bir coin %8 aşağıda.
- 24 saat sonra her 10 coinden sadece 3'ü yükselişini sürdürüyor.

Bot sinyali fark ettiğinde yükseliş büyük ölçüde bitmiş oluyor ve fiyat geri veriliyor. Bu, akademik çalışmalardaki "kısa vadeli geri dönüş (reversal)" bulgusuyla ve pompa-boşalt araştırmalarıyla uyumlu.

**Bilerek yapılmayan:** Bu sonuçtan "tersini yap, yükselene açığa sat (short)" çıkarmak cazip görünüyor. Ama bu, sonuca bakıp kural uydurmak olur. Ayrıca küçük coinlerde açığa satış vadeli işlem gerektiriyor ve büyük riskler taşıyor: ani sıkışma (short squeeze), fonlama ücreti, likidasyon. Denenecekse ayrı ve önceden planlanmış bir test olmalı.

## B. Trend botunun avantajı gerçek mi?

Script: `avantaj_testi.py`.

### 1) Komisyon kârı yiyor mu?

| Dönem | Komisyonsuz | %0,1 (gerçek) | %0,5 (5 kat) | Al-tut | İşlem |
|---|---|---|---|---|---|
| 2018–2026 | %+1639 | **%+1447** | %+868 | %+465 | 58 |
| 2022–2026 | %+174 | **%+158** | %+100 | %+68 | 31 |

**Komisyon kârın küçük bir kısmını yiyor**, çünkü bot yılda sadece ~6 işlem yapıyor. Komisyon 5 katına çıksa bile al-tut'un üstünde kalıyor. Videodaki botla en büyük fark burada: o bot günde onlarca işlem yapıyordu.

### 2) Şans mı?

Gerçek bot, 5000 sahte botla karşılaştırıldı. Sahte botlar piyasada aynı sürelerle kalıyor ama giriş-çıkış zamanları rastgele karıştırılmış.

| Dönem | Gerçek bot | Sahte botların ortancası | Gerçek bot, sahtelerin şu kadarından iyi |
|---|---|---|---|
| 2018–2026 | %+1447 | %+140 | **%95,5** (p = 0,045) |
| 2022–2026 | %+158 | %+26 | %87,1 (p = 0,129) |

- 2018–2026'da avantaj istatistiksel olarak anlamlı (sınırda).
- 2022–2026 tek başına anlamlı değil, çünkü bu kadar kısa dönemde ancak ~30 işlem var.
- Yani **avantaj muhtemelen gerçek, ama kesin değil.**

### 3) Sağlamlık: ortalama uzunluğunu değiştirince ne oluyor?

| Dönem | 50 gün | 75 | **100** | 150 | 200 | Al-tut |
|---|---|---|---|---|---|---|
| 2018–2026 | %+2397 | %+1081 | %+1447 | %+1265 | %+626 | %+465 |
| 2022–2026 | %+155 | %+121 | %+158 | %+228 | %+227 | %+68 |

Her uzunluk al-tut'u geçiyor. Yani sonuç "100 sayısına özel bir şans" değil, genel bir trend etkisi. İyi bir işaret.

### 4) Aylık büyüme ve doğru pozisyon büyüklüğü (Kelly)

- **Yıllık bileşik büyüme:** %36 (dolar bazında, 2018–2026). Bu, aylık ortalama **%2,6** demek.
- **Takvim ayları:** Ayların %38'i zararlı. Ortanca ay %0, çünkü bot sık sık nakitte bekliyor. En iyi ay %+61, en kötü ay %−18.
- **Kelly** paranın ~2,1 katı pozisyon diyor, yani kaldıraç. Yarım Kelly ≈ 1 kat, yani kaldıraçsız.

| Pozisyon | Toplam (2018–26) | En büyük düşüş |
|---|---|---|
| Paranın yarısı | %+391 | %−35 |
| **Paranın tamamı (şu anki bot)** | %+1488 | %−60 |
| 2 kat (kaldıraç) | %+4572 | %−87 |
| 3 kat (kaldıraç) | %+2248 | **%−97** |

**Kaldıraç önerilmez.** 2 kat kaldıraç geçmişte kârı artırırdı, ama %87'lik bir düşüşü psikolojik olarak kimse taşıyamaz. Üstelik avantaj tahmini kesin değil. 3 katta kâr bile azalıyor.
