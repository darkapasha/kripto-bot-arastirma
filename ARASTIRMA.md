# Kripto Bot — Araştırma Notu (2026-11-02)

## 1. Sunucu (oracle-sunucum)

| | |
|---|---|
| İşlemci | 4 çekirdek ARM (Neoverse-N1, aarch64) |
| RAM | 24 GB (~21 GB kullanılabilir) |
| GPU | **Yok** |
| Disk | 45 GB, 23 GB boş |
| Yazılım | Ubuntu 24.04, Python 3.12, Docker 29, Ollama (gemma3:4b, qwen2.5) |

Erişim testi sunucudan yapıldı, hepsi HTTP 200 döndü: Binance veri arşivi, Binance API, BtcTurk API, Fear & Greed API.

Not: Her sabah 08:00 ve 08:10'da radyo için Ollama CPU'yu birkaç dakika tamamen kullanıyor. Ağır eğitim işleri bu saatlere denk getirilmemeli.

## 2. Açık veri kaynakları

| Kaynak | Ne verir | Not |
|---|---|---|
| **Binance Public Data** (data.binance.vision) | 2017'den bugüne mum verisi (1 dk–1 gün), tüm işlemler, vadeli piyasa verisi | Ücretsiz, kayıt gerekmiyor, aylık/günlük zip. **Ana eğitim verisi olarak bunu öneriyorum.** |
| **BtcTurk API** | BTC/TRY canlı fiyat, emir defteri, işlem geçmişi | TL paritesiyle gerçek işlem yapılacaksa lazım |
| **CryptoDataDownload** | Birçok borsadan CSV (günlük/saatlik/dakikalık) | Lisansı CC BY-NC-SA, yani ticari kullanım yok. Kişisel bot için sorun değil |
| **Alternative.me Fear & Greed** | Günlük "korku/açgözlülük" endeksi, 2018'den beri | Ücretsiz, anahtar gerekmiyor |
| **Haberler** | MMA/F1 botundaki RSS + Gemini/Ollama altyapısı | Kripto haberlerinden duygu puanı çıkarmak için yeniden kullanılabilir |
| On-chain (Santiment, CryptoQuant, Glassnode) | Balina hareketleri, borsa giriş-çıkışları | Ücretsiz katmanlar çok kısıtlı. İlk aşamada gerek yok |

## 3. Bu tür projelerde kullanılan algoritmalar

### a) Kural tabanlı (yapay zekâ yok)
DCA, grid, hareketli ortalama kesişimi, RSI ile ortalamaya dönüş. Basit, hızlı test edilir, **her yapay zekâ modelinin geçmesi gereken çıta** bunlardır.

### b) Klasik makine öğrenmesi: XGBoost / LightGBM
Teknik göstergelerden (RSI, MACD, hacim, volatilite…) "sonraki X saatte yükselir mi?" tahmini yapılır. En çok kullanılan ve CPU'da en verimli yöntem bu.
- 2026 tarihli bir çalışma ~70.000 saatlik BTC verisiyle XGBoost, LSTM ve iTransformer'ı karşılaştırmış. Bulgular:
  - Saf "tahmin yukarıysa al" stratejileri %0,1 komisyonla **zarara geçiyor**.
  - "Beklenen kazanç komisyonu geçmiyorsa işlem yapma" filtresi eklenince bazı ayarlar kâra dönüyor.
  - İkincil bir yorum, modellerin birbirine üstünlüğünün ve al-tut'a karşı üstünlüğün istatistiksel olarak kanıtlanamadığını söylüyor (doğrulayamadım).

### c) Derin öğrenme: LSTM / Transformer
Makalelerde yüksek "doğruluk" (R², RMSE) raporlanıyor. Ama fiyatı tahmin etmek, para kazanmakla aynı şey değil. Komisyon ve ileriye dönük (walk-forward) testlerde avantaj genelde eriyor.

### d) Pekiştirmeli öğrenme (RL): FinRL
Ajan, deneme-yanılmayla al/sat/bekle kararı vermeyi öğreniyor.
- Bir topluluk (ensemble) çalışmasında yıllık getiriler şöyle: ensemble ~%93, FinRL ~%63, al-tut ~%76. Yükseliş piyasasında iyi, çöküşlerde koruması zayıf.
- Başka bir çalışma, yayınlanan RL sonuçlarının çoğunun aşırı uyumla şişirildiğini gösteriyor.
- Sonuç: en kırılgan ve en zor test edilen yöntem bu.

### e) Hazır finans "temel modelleri" (foundation models)
Önceden milyonlarca fiyat serisiyle eğitilmiş modeller. Eğitmeden tahmin yapabiliyorlar, istenirse ince ayar (fine-tune) yapılabiliyor.
- **Kronos** (MIT lisans): mum verisi için özel eğitilmiş. Boyutlar: mini 4,1 milyon, small 24,7 milyon, base 102 milyon parametre.
- **Chronos-Bolt / Chronos-2** (Amazon): genel zaman serisi modeli, CPU'da çalışabiliyor.
- Kripto üzerinde bağımsız kanıt zayıf. Çoğu sonuç modeli yapanların kendi makalesinden geliyor.

### f) LLM ile haber/duygu analizi
LLM haberleri okuyup bir puan verir, bu puan diğer modele **ek sinyal** olur. LLM'in doğrudan al/sat kararı vermesi önerilmiyor.

## 4. Sunucuda ne çalışır?

| Model | Eğitim | Tahmin (canlı) |
|---|---|---|
| LightGBM / XGBoost | ✅ Rahat (dakikalar) | ✅ Anında |
| Küçük LSTM | ⚠️ Olur ama yavaş (saatler) | ✅ |
| FinRL (RL) | ⚠️ Yavaş, küçük ölçekte olur | ✅ |
| Kronos-mini/small, Chronos-Bolt | ⚠️ İnce ayar yavaş ama mümkün | ✅ CPU'da yeterli |
| Kronos-base | ❌ İnce ayar pratik değil | ⚠️ Yavaş |
| LLM (gemma3:4b) | ❌ GPU olmadan eğitilemez | ✅ Zaten çalışıyor (haber puanı için) |

GPU olmadığı için "büyük yapay zekâ eğitmek" seçenek değil. Bu iş için zaten en iyi sonuç veren yöntemler (LightGBM + iyi özellikler + komisyon filtresi) CPU'da rahat çalışıyor.

## 5. Hazır açık kaynak çatılar (framework)

- **Freqtrade + FreqAI** (GPL-3): en popüler seçenek. Backtest, paper trading, Telegram kontrolü ve LightGBM/XGBoost/PyTorch desteği hazır geliyor. Docker'la kurulur. ARM imajı ve BtcTurk desteği kurulumdan önce kontrol edilmeli (BtcTurk resmi destek listesinde olmayabilir).
- **Jesse**: araştırma ve backtest odaklı, ML desteği daha hafif.
- **Hummingbot**: piyasa yapıcılığı (market making) için; bizim hedefimize uygun değil.

## 6. Önerilen yol

1. Binance'ten BTC/USDT 1 saatlik verisini (2017–bugün) sunucuya indir.
2. Freqtrade'i Docker'la kur. Kural tabanlı stratejileri (al-tut, DCA, MA, grid) %0,1+ komisyonla backtest et. Bunlar çıta olacak.
3. FreqAI + LightGBM modelini walk-forward yöntemiyle eğit (sürekli yeniden eğitilen, sadece geçmişi gören test). Komisyon filtresini ekle.
4. Ek sinyaller dene: Fear & Greed, haber duygu puanı, Kronos-small tahmini. Her biri gerçekten fayda sağlıyor mu, ayrı ayrı ölç.
5. Sadece çıtayı **anlamlı biçimde** geçen bir şey çıkarsa: Telegram bildirimli paper trading (birkaç hafta).
6. Ancak bundan sonra, kullanıcı karar verirse küçük gerçek para (SPK listesindeki bir borsa, sadece işlem izinli API anahtarı).

## Kaynaklar
- Binance Public Data: https://github.com/binance/binance-public-data
- CryptoDataDownload: https://www.cryptodatadownload.com/data/
- Freqtrade / Jesse / Hummingbot karşılaştırma: https://www.pistack.xyz/posts/2026-04-27-freqtrade-vs-jesse-vs-hummingbot-self-hosted-algorithmic-trading-guide-2026/
- XGBoost walk-forward yorum: https://dev.to/shaktitiwari/bitcoin-trading-with-xgboost-what-70000-hours-of-data-actually-prove-2026-walk-forward-evidence-ihh
- LSTM+XGBoost: https://arxiv.org/abs/2506.22055v1
- RL ensemble: https://arxiv.org/abs/2309.00626v1
- RL aşırı uyum: https://ar5iv.labs.arxiv.org/html/2209.05559
- Kronos: https://arxiv.org/pdf/2508.02739
- Chronos: https://arxiv.org/pdf/2403.07815
- Chronos AutoGluon: https://auto.gluon.ai/1.1.0/tutorials/timeseries/forecasting-chronos.html
- FinCast: https://arxiv.org/pdf/2508.19609
