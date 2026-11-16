# Yapay zekâ deneme 2: "Trend kuralına ne zaman güvenmeyelim?"
#
# Trend kuralı (günlük kapanış > 100 günlük ortalama) "içeride ol" dediği her gün için model,
# "önümüzdeki 20 günde fiyat yükselecek mi?" olasılığını tahmin eder. Olasılık %50'nin altındaysa
# o gün trend kuralına uyulmaz, nakitte beklenir.
#
# ÖNCEDEN BELİRLENEN BAŞARI ÖLÇÜTÜ (sonuçları görmeden yazıldı):
#   2022-01 → 2026-10 arasında BTC'de trend kuralını HEM kârda HEM en büyük düşüşte geçmeli
#   VE tüm coinlerdeki test tahminlerinde AUC > 0,55 olmalı. Biri bile tutmazsa deneme başarısız.
#
# Deneyler (sadece bu ikisi, ayar denemesi yok):
#   A: sadece fiyat/hacim özellikleri
#   B: A + Fear & Greed endeksi + vadeli fonlama oranı
#
# Walk-forward: her ay başında model, o tarihten en az 22 gün önce etiketi kesinleşmiş verilerle
# (10 coinin hepsi) yeniden eğitilir. Kullanım: python deneme2.py

import json

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

COINLER = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "AVAX", "LINK", "LTC"]
VERI = "/freqtrade/user_data/data/binance"
UFUK = 20          # gün
ARINDIRMA = UFUK + 2
KOMISYON = 0.001
TEST_BAS, TEST_BIT = pd.Timestamp("2022-01-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
PARAMS = dict(n_estimators=200, learning_rate=0.03, num_leaves=15, min_child_samples=50,
              subsample=0.8, subsample_freq=1, colsample_bytree=0.8, random_state=42, verbose=-1)


def rsi(close, n=14):
    fark = close.diff()
    kazanc = fark.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    kayip = (-fark.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + kazanc / kayip)


fng = pd.DataFrame(json.load(open("/freqtrade/user_data/ekveri/fng.json"))["data"])
fng = pd.Series(fng["value"].astype(float).values,
                index=pd.to_datetime(fng["timestamp"].astype(int), unit="s", utc=True)).sort_index()

btc = pd.read_feather(f"{VERI}/BTC_USDT-1d.feather").set_index("date")
btc_r20 = np.log(btc["close"]).diff(20)
btc_sma = btc["close"] / btc["close"].rolling(100).mean() - 1

parcalar = []
for coin in COINLER:
    d = pd.read_feather(f"{VERI}/{coin}_USDT-1d.feather").set_index("date")
    c, lc = d["close"], np.log(d["close"])
    f = pd.DataFrame(index=d.index)
    for n in (1, 5, 20, 60):
        f[f"r{n}"] = lc.diff(n)
    for n in (20, 50, 100, 200):
        f[f"sma{n}"] = c / c.rolling(n).mean() - 1
    f["vol20"] = lc.diff().rolling(20).std()
    f["vol60"] = lc.diff().rolling(60).std()
    f["hacim"] = d["volume"] / d["volume"].rolling(20).mean()
    f["rsi"] = rsi(c)
    f["dd90"] = c / c.rolling(90).max() - 1
    trend = c > c.rolling(100).mean()
    f["trend_gun"] = trend.groupby((~trend).cumsum()).cumsum().clip(upper=365)
    f["btc_r20"] = btc_r20.reindex(f.index)
    f["btc_sma100"] = btc_sma.reindex(f.index)
    # Ek veri (deney B)
    f["fng"] = fng.reindex(f.index)
    f["fng_7"] = f["fng"].diff(7)
    try:
        fr = pd.read_feather(f"{VERI}/futures/{coin}_USDT_USDT-1h-funding_rate.feather").set_index("date")["funding_rate"]
        fr = fr.resample("1D").mean()
        f["fon7"] = fr.rolling(7).mean().reindex(f.index)
        f["fon30"] = fr.rolling(30).mean().reindex(f.index)
    except FileNotFoundError:
        f["fon7"] = f["fon30"] = np.nan
    f["trend"] = trend
    f["etiket"] = (d["open"].shift(-(UFUK + 1)) / d["open"].shift(-1) - 1 > 0).astype(float)
    f.loc[d["open"].shift(-(UFUK + 1)).isna(), "etiket"] = np.nan
    f["coin"] = coin
    f["open"] = d["open"]
    parcalar.append(f.iloc[200:])
veri = pd.concat(parcalar)

OZ_A = ["r1", "r5", "r20", "r60", "sma20", "sma50", "sma100", "sma200", "vol20", "vol60",
        "hacim", "rsi", "dd90", "trend_gun", "btc_r20", "btc_sma100"]
OZ_B = OZ_A + ["fng", "fng_7", "fon7", "fon30"]


def walk_forward(ozellikler):
    tahminler = []
    for ay in pd.date_range(TEST_BAS, TEST_BIT, freq="MS", inclusive="left"):
        egitim = veri[(veri.index <= ay - pd.Timedelta(days=ARINDIRMA)) & veri["trend"] & veri["etiket"].notna()]
        test = veri[(veri.index >= ay) & (veri.index < ay + pd.offsets.MonthBegin(1)) & veri["trend"]]
        if test.empty:
            continue
        model = lgb.LGBMClassifier(**PARAMS).fit(egitim[ozellikler], egitim["etiket"])
        tahminler.append(test.assign(olasilik=model.predict_proba(test[ozellikler])[:, 1]))
    return pd.concat(tahminler)


def sim(gunler, icerde):
    """Freqtrade'le birebir tutan basit simülasyon: dünkü karar bugün açılışta uygulanır."""
    pos = icerde.astype(int).shift(1).fillna(0)
    getiri = (gunler["open"].shift(-1) / gunler["open"] - 1).fillna(0)
    komisyon = pos.diff().abs().fillna(pos.iloc[0]) * KOMISYON
    deger = (1 + pos * getiri - komisyon).cumprod()
    return deger


def rapor(ad, deger, islem):
    print(f"  {ad:<22} kâr %{(deger.iloc[-1] - 1) * 100:+6.0f} | en büyük düşüş %{(deger / deger.cummax() - 1).min() * 100:4.0f}"
          f" | işlem {islem:>3} | " + " ".join(f"{y}:%{(g.iloc[-1] / g.iloc[0] - 1) * 100:+.0f}"
                                            for y, g in deger.groupby(deger.index.year)))


btc_gun = veri[(veri["coin"] == "BTC") & (veri.index >= TEST_BAS) & (veri.index < TEST_BIT)]
taban = sim(btc_gun, btc_gun["trend"])
print(f"Test dönemi {TEST_BAS.date()} → {TEST_BIT.date()}, ufuk {UFUK} gün\n")
print("ÇITA")
rapor("Trend günlük", taban, int(btc_gun["trend"].astype(int).diff().abs().sum() / 2))

for ad, oz in (("A (fiyat)", OZ_A), ("B (fiyat+F&G+fonlama)", OZ_B)):
    t = walk_forward(oz)
    tum = t.dropna(subset=["etiket"])
    b = tum[tum["coin"] == "BTC"]
    print(f"\nDENEY {ad}")
    print(f"  AUC tüm coinler: {roc_auc_score(tum['etiket'], tum['olasilik']):.3f} ({len(tum)} tahmin) | "
          f"AUC BTC: {roc_auc_score(b['etiket'], b['olasilik']):.3f} ({len(b)} tahmin)")
    print("  AUC yıllara göre (tüm coinler): " + " ".join(
        f"{y}:{roc_auc_score(g['etiket'], g['olasilik']):.2f}" for y, g in tum.groupby(tum.index.year)
        if g["etiket"].nunique() > 1))
    olas = t[t["coin"] == "BTC"]["olasilik"].reindex(btc_gun.index)
    icerde = btc_gun["trend"] & (olas > 0.5)
    print(f"  Trend 'içeride' dediği BTC günlerinin %{(olas[btc_gun['trend']] <= 0.5).mean() * 100:.0f}'inde model 'güvenme' dedi")
    rapor("Trend + model", sim(btc_gun, icerde), int(icerde.astype(int).diff().abs().sum() / 2))
