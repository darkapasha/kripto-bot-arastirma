# Olay analizi: "ani yükseliş" sinyalinden SONRA fiyat ortalama ne yapıyor? (komisyonsuz, saf sinyal gücü)
# Her sinyal için: sonraki saatin açılışından itibaren 1s / 4s / 12s / 24s / 48s / 7g sonraki getiri.
# Karşılaştırma: aynı saatlerde filtreyi geçen TÜM coinlerin ortalama getirisi (piyasa genel hareketini çıkarmak için).
# Sinyal kuralları momentum_test.py ile aynı (V1/V2/V3). genis.npz önbelleğini kullanır.

import os

import numpy as np
import pandas as pd

KLASOR = os.path.expanduser("~/kripto_bot/momentum")
z = np.load(f"{KLASOR}/genis.npz", allow_pickle=True)
zaman = pd.DatetimeIndex(z["zaman"]).tz_localize("UTC")
O, C, Hc = z["O"], z["C"], z["Hc"]
Cdf, Hdf = pd.DataFrame(C), pd.DataFrame(Hc)
uygun = ((Hdf.rolling(24, min_periods=24).sum() >= 500_000) & (Cdf.notna().cumsum() >= 168)).to_numpy()
medyan_hacim = Hdf.rolling(168, min_periods=100).median().shift(1).to_numpy()
test = zaman >= pd.Timestamp("2022-01-01", tz="UTC")
UFUKLAR = {"1s": 1, "4s": 4, "12s": 12, "24s": 24, "48s": 48, "7g": 168}

ileri = {}
for ad, h in UFUKLAR.items():
    with np.errstate(invalid="ignore", divide="ignore"):
        ileri[ad] = np.roll(O, -(1 + h), axis=0) / np.roll(O, -1, axis=0) - 1   # giriş: sonraki açılış
        ileri[ad][-(1 + h):] = np.nan

print("Ani yükselişten sonraki ortalama getiri (komisyonsuz). Parantez içinde: aynı saatlerde tüm uygun coinlerin ortalaması.")
print("Fark eksi ise: yükselen coin, sıradan bir coinden daha KÖTÜ gidiyor (yükseliş geri veriliyor).\n")
for ad, (L, X, V) in {"V1 (4s ≥%8)": (4, 0.08, 5), "V2 (1s ≥%5)": (1, 0.05, 5), "V3 (24s ≥%15)": (24, 0.15, 3)}.items():
    with np.errstate(invalid="ignore", divide="ignore"):
        sinyal = uygun & ((Cdf / Cdf.shift(L) - 1).to_numpy() >= X) & (Hc / medyan_hacim >= V) & test[:, None]
    satirlar, sayi = [], sinyal.sum()
    for u, f in ileri.items():
        s = f[sinyal]
        piyasa = np.where(uygun & test[:, None], f, np.nan)
        piyasa_satir = np.nanmean(piyasa, axis=1)                       # her saat tüm coinlerin ortalaması
        k = np.broadcast_to(piyasa_satir[:, None], f.shape)[sinyal]
        gecerli = ~np.isnan(s) & ~np.isnan(k)
        satirlar.append(f"{u}: %{np.mean(s[gecerli]) * 100:+.2f} (%{np.mean(k[gecerli]) * 100:+.2f}) "
                        f"[medyan %{np.median(s[gecerli]) * 100:+.2f}, yükselen %{(s[gecerli] > 0).mean() * 100:.0f}]")
    print(f"{ad}: {sayi} sinyal")
    for sat in satirlar:
        print("   " + sat)
