# Modelin test dönemlerindeki tahminlerini gerçekte olanla karşılaştırır.
# Çok yüksek bir isabet (korelasyon > ~0,3) "kopya çekme" (veri sızıntısı) şüphesi doğurur;
# piyasada gerçekçi tahmin gücü genelde 0 ile 0,1 arasındadır.

import glob
import sys

import pandas as pd

KIMLIK = sys.argv[1] if len(sys.argv) > 1 else "lgbm_v1"
dosyalar = sorted(glob.glob(f"/freqtrade/user_data/models/{KIMLIK}/backtesting_predictions/*_prediction.feather"))
tahmin = pd.concat([pd.read_feather(f) for f in dosyalar], ignore_index=True)
tahmin = tahmin.drop_duplicates("date", keep="last").set_index("date")

fiyat = pd.read_feather("/freqtrade/user_data/data/binance/BTC_USDT-1h.feather").set_index("date")["close"]
gercek = (fiyat.shift(-24) / fiyat - 1).rename("gercek")
d = tahmin[["&-getiri"]].join(gercek, how="inner").dropna()

print(f"{len(dosyalar)} model, {len(d)} saatlik tahmin")
print(f"korelasyon (tahmin ~ gerçek): {d['&-getiri'].corr(d['gercek']):+.3f}")
print(f"yön isabeti (ikisi de aynı yönde): %{((d['&-getiri'] > 0) == (d['gercek'] > 0)).mean() * 100:.1f}")
print(f"piyasanın yükseldiği saatlerin oranı: %{(d['gercek'] > 0).mean() * 100:.1f}")
al = d[d["&-getiri"] > 0.01]
print(f"tahmin > %1 olan saatler: {len(al)}, bu saatlerde gerçek ortalama getiri %{al['gercek'].mean() * 100:+.2f} "
      f"(tüm saatlerde %{d['gercek'].mean() * 100:+.2f})")
for yil, g in d.groupby(d.index.year):
    print(f"  {yil}: korelasyon {g['&-getiri'].corr(g['gercek']):+.3f}")
