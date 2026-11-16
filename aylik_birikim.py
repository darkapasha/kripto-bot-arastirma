# Her ay 1000 TL eklenen trend botu: 12 ay sonra ne olur?
# 2018'den bugüne her olası başlangıç gününden 12 aylık birikim simüle edilir (TL bazında, komisyon %0,1).
# Karşılaştırma: aynı parayı her ay dolar almak, her ay BTC alıp tutmak.

import os

import numpy as np
import pandas as pd

d = pd.read_feather(os.path.expanduser("~/kripto_bot/user_data/data/binance/BTC_USDT-1d.feather")).set_index("date")
kur = pd.read_parquet(os.path.expanduser("~/kripto_bot/hisse/kapanis.parquet"))["USDTRY=X"].ffill()
if kur.index.tz is None:
    kur.index = kur.index.tz_localize("UTC")
d = d[d.index >= "2017-12-01"]
k = kur.reindex(d.index).ffill().bfill()

pos = (d["close"] > d["close"].rolling(100).mean()).astype(int).shift(1).fillna(0)
r = (d["open"].shift(-1) / d["open"] - 1).fillna(0)
egriler = {
    "Trend botu": ((1 + pos * r - pos.diff().abs().fillna(0) * 0.001).cumprod() * k).to_numpy(),
    "Her ay BTC al-tut": ((1 + r).cumprod() * k).to_numpy(),
    "Her ay dolar al": k.to_numpy(),
}
gun = d.index
baslangiclar = [i for i in range(len(gun)) if gun[i] >= pd.Timestamp("2018-01-01", tz="UTC") and i + 365 < len(gun)]

print("Her ay 1000 TL, 12 ay (toplam 12.000 TL yatırılır). 2018'den bu yana her başlangıç günü için yıl sonu değeri:\n")
print(f"{'':<20}{'en kötü':>9}{'kötü %10':>10}{'kötü %25':>10}{'ortanca':>9}{'iyi %25':>9}{'iyi %10':>9}{'en iyi':>9}{'zararda':>9}")
for ad, e in egriler.items():
    sonuc = []
    for b in baslangiclar:
        yatirim_gunleri = [b + 30 * m for m in range(12)]
        bitis = b + 365
        sonuc.append(sum(1000 * e[bitis] / e[t] for t in yatirim_gunleri))
    s = np.array(sonuc)
    print(f"{ad:<20}{s.min():>9.0f}{np.percentile(s, 10):>10.0f}{np.percentile(s, 25):>10.0f}{np.median(s):>9.0f}"
          f"{np.percentile(s, 75):>9.0f}{np.percentile(s, 90):>9.0f}{s.max():>9.0f}{(s < 12000).mean() * 100:>8.0f}%")

print("\nYıllara göre (o yılın 1 Ocak'ında başlayan 12 aylık birikim, trend botu):")
e = egriler["Trend botu"]
for yil in range(2018, 2026):
    b = gun.searchsorted(pd.Timestamp(f"{yil}-01-01", tz="UTC"))
    print(f"   {yil}: {sum(1000 * e[b + 365] / e[b + 30 * m] for m in range(12)):,.0f} TL")
