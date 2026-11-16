# Hisse çıta testi: al-tut ve günlük trend kuralı (kapanış > 100 günlük ortalama), kriptodakiyle aynı kural.
# Veri: Yahoo Finance (yfinance), temettü ve bölünmelere göre düzeltilmiş fiyatlar. Komisyon %0,1.
# BIST sonuçları hem TL hem dolar bazında verilir (TL'deki enflasyon yanılgısını görmek için).
# Kullanım: python hisse_cita.py [--indir]

import os
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")
KLASOR = os.path.expanduser("~/kripto_bot/hisse")
BIST = ["XU100.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "AKBNK.IS", "BIMAS.IS",
        "KCHOL.IS", "SAHOL.IS", "TUPRS.IS", "EREGL.IS", "SISE.IS"]
ABD = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "JPM"]
KUR = "USDTRY=X"
KOMISYON = 0.001
DONEMLER = [("2010-01-01", "2026-11-01"), ("2018-01-01", "2026-11-01"), ("2022-01-01", "2026-11-01")]

if "--indir" in sys.argv or not os.path.exists(f"{KLASOR}/acilis.parquet"):
    import yfinance as yf
    v = yf.download(BIST + ABD + [KUR], start="2009-01-01", end="2026-11-02", auto_adjust=True, progress=False)
    v["Open"].to_parquet(f"{KLASOR}/acilis.parquet")
    v["Close"].to_parquet(f"{KLASOR}/kapanis.parquet")
acilis = pd.read_parquet(f"{KLASOR}/acilis.parquet")
kapanis = pd.read_parquet(f"{KLASOR}/kapanis.parquet")
kur = kapanis[KUR].ffill()

# Veri kontrolü: tek günde %40'tan büyük hareket varsa (ör. endeks sıfır atma) uyar
for t in BIST + ABD:
    sicrama = kapanis[t].dropna().pct_change().abs()
    if sicrama.max() > 0.4:
        print(f"UYARI {t}: {sicrama.idxmax().date()} tarihinde %{sicrama.max() * 100:.0f} hareket")


def sim(t, sinyal, bas, bit, dolar=False):
    o = acilis[t].dropna()
    if dolar:
        o = o / kur.reindex(o.index).ffill()
    m = (o.index >= bas) & (o.index < bit)
    o, pos = o[m], sinyal.reindex(o.index)[m].fillna(0).shift(1).fillna(0)
    if o.empty:
        return None
    getiri = (o.shift(-1) / o - 1).fillna(0)
    deger = (1 + pos * getiri - pos.diff().abs().fillna(pos.iloc[0]) * KOMISYON).cumprod()
    return (deger.iloc[-1] - 1) * 100, (deger / deger.cummax() - 1).min() * 100, int(pos.diff().abs().sum() / 2), o.index[0]


for bas, bit in DONEMLER:
    print(f"\n=== {bas} → {bit}   (kâr % / en büyük düşüş % / işlem) ===")
    for grup, liste, dolar_da in (("BIST", BIST, True), ("ABD", ABD, False)):
        baslik = f"{'':<10}{'Al-tut':>16}{'Trend':>22}"
        if dolar_da:
            baslik += f"{'Al-tut ($)':>18}{'Trend ($)':>22}"
        print(f"-- {grup}\n{baslik}")
        for t in liste:
            c = kapanis[t].dropna()
            trend = (c > c.rolling(100).mean()).astype(int)
            hep = pd.Series(1, index=c.index)
            satir = f"{t.replace('.IS', ''):<10}"
            for dolar in ((False, True) if dolar_da else (False,)):
                a, tr = sim(t, hep, bas, bit, dolar), sim(t, trend, bas, bit, dolar)
                if a is None:
                    satir += "   veri yok"
                    break
                satir += f"{a[0]:+10.0f} /{a[1]:4.0f}{tr[0]:+12.0f} /{tr[1]:4.0f} /{tr[2]:3}"
            print(satir)
    print(f"-- Dolar/TL kuru bu dönemde: %{(kur[kur.index < bit].iloc[-1] / kur[kur.index >= bas].iloc[0] - 1) * 100:+.0f}")
