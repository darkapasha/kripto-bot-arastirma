# Son backtest'in özetini çıkarır: kâr, işlem sayısı ve AÇIK pozisyonlar dahil gerçek en büyük düşüş.
# (Freqtrade'in kendi düşüş rakamı sadece kapanmış işlemlere bakar.)

import numpy as np
import pandas as pd

from freqtrade.data.btanalysis import load_backtest_data

BASLANGIC = 1000

t = load_backtest_data("/freqtrade/user_data/backtest_results")
fiyat = {p: pd.read_feather(f"/freqtrade/user_data/data/binance/{p.replace('/', '_')}-1h.feather")
         .set_index("date")["close"] for p in t["pair"].unique()}
saat = pd.date_range(t["open_date"].min().floor("h"), t["close_date"].max().floor("h"), freq="h", tz="UTC")
fiyat = {p: f.reindex(saat).ffill().to_numpy() for p, f in fiyat.items()}
nakit = np.zeros(len(saat))
deger = np.zeros(len(saat))
for r in t.itertuples():
    a, b = saat.searchsorted(r.open_date), saat.searchsorted(r.close_date)
    deger[a:b] += r.amount * fiyat[r.pair][a:b]
    nakit[a:] -= r.stake_amount
    nakit[b:] += r.stake_amount + r.profit_abs
v = pd.Series(BASLANGIC + nakit + deger, index=saat)
icerde = (t["close_date"] - t["open_date"]).dt.total_seconds().sum() / (saat[-1] - saat[0]).total_seconds()
print(f"kâr %{(v.iloc[-1] / BASLANGIC - 1) * 100:+.0f} | gerçek en büyük düşüş %{(v / v.cummax() - 1).min() * 100:.0f} | "
      f"işlem {len(t)} | kazanma %{(t['profit_abs'] > 0).mean() * 100:.0f} | piyasada kalma %{icerde * 100:.0f}")
for yil, g in t.groupby(t["close_date"].dt.year):
    print(f"  {yil}: {len(g)} işlem, kâr {g['profit_abs'].sum():+.0f} USDT")
