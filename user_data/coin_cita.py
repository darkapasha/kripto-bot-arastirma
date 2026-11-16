# Her coin için çıta stratejilerini hızlıca hesaplar (Freqtrade'in sonucuyla BTC'de birebir tuttu).
# Sinyal mumun kapanışında oluşur, işlem bir sonraki mumun açılışında yapılır. Komisyon %0,1.
# Kullanım: python coin_cita.py 2022-01-01 2026-11-01

import sys

import pandas as pd

COINLER = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "AVAX", "LINK", "LTC"]
KOMISYON = 0.001
VERI = "/freqtrade/user_data/data/binance/{}_USDT-{}.feather"


def oku(coin, tf, bas, bit):
    df = pd.read_feather(VERI.format(coin, tf))
    return df, (df["date"] >= bas) & (df["date"] < bit)


def sim(df, sinyal, maske):
    """sinyal: 1 = içeride ol. Göstergeler tüm veriden hesaplanır, getiriler sadece dönem içinden."""
    x = df[maske]
    pos = sinyal[maske].shift(1).fillna(0)
    getiri = (x["open"].shift(-1) / x["open"] - 1).fillna(0)
    komisyon = pos.diff().abs().fillna(pos.iloc[0]) * KOMISYON
    deger = (1 + pos * getiri - komisyon).cumprod()
    return (deger.iloc[-1] - 1) * 100, (deger / deger.cummax() - 1).min() * 100, int(pos.diff().abs().sum() / 2)


bas, bit = (pd.Timestamp(t, tz="UTC") for t in sys.argv[1:3])
print(f"Dönem {bas.date()} → {bit.date()}  (kâr % / en büyük düşüş % / işlem sayısı)")
print(f"{'Coin':<6}{'Başlangıç':<12}{'Al-tut':>18}{'Trend günlük':>24}{'EMA saatlik':>24}")
for coin in COINLER:
    g, mg = oku(coin, "1d", bas, bit)
    s, ms = oku(coin, "1h", bas, bit)
    # Çok yeni coinlerde trend göstergesi için 100 gün beklenir
    ilk = g.loc[mg, "date"].iloc[0]
    altut = sim(g, pd.Series(1, index=g.index), mg)
    trend = sim(g, (g["close"] > g["close"].rolling(100).mean()).astype(int), mg)
    ema = sim(s, (s["close"].ewm(span=50, adjust=False).mean()
                  > s["close"].ewm(span=200, adjust=False).mean()).astype(int), ms)
    f = lambda r: f"{r[0]:+8.0f} / {r[1]:4.0f} / {r[2]:>3}"
    print(f"{coin:<6}{str(ilk.date()):<12}{altut[0]:+10.0f} / {altut[1]:4.0f}{f(trend):>24}{f(ema):>24}")
