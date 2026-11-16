# DCA çıtası: her pazartesi sabit tutarda BTC al, hiç satma. Freqtrade dışında, indirilen veriden hesaplanır.
# Kullanım: python dca.py 2018-01-01 2026-11-01

import sys

import pandas as pd

HAFTALIK = 10.0     # USDT
KOMISYON = 0.001    # %0,1

df = pd.read_feather("/freqtrade/user_data/data/binance/BTC_USDT-1d.feather")
df["date"] = pd.to_datetime(df["date"], utc=True)
bas, bit = (pd.Timestamp(t, tz="UTC") for t in sys.argv[1:3])
df = df[(df["date"] >= bas) & (df["date"] < bit)]

alimlar = df[df["date"].dt.dayofweek == 0]
yatirilan = HAFTALIK * len(alimlar)
btc = (HAFTALIK * (1 - KOMISYON) / alimlar["open"]).sum()

# Portföy değerinin zirveden en büyük düşüşü
adet = (HAFTALIK * (1 - KOMISYON) / df["open"]).where(df["date"].dt.dayofweek == 0, 0).cumsum()
yatirim = (df["date"].dt.dayofweek == 0).cumsum() * HAFTALIK
kar_orani = adet * df["close"] / yatirim.where(yatirim > 0)
deger = adet * df["close"]
dusus = (deger / deger.cummax() - 1).min()

son = btc * df["close"].iloc[-1]
print(f"DCA {bas.date()} → {bit.date()}: {len(alimlar)} alım, yatırılan {yatirilan:.0f} USDT, "
      f"son değer {son:.0f} USDT, kâr %{(son / yatirilan - 1) * 100:.1f}, "
      f"portföyün en büyük düşüşü %{dusus * 100:.1f}, en kötü anda kâr/zarar %{(kar_orani.min() - 1) * 100:.1f}")
