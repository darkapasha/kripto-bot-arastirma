# Momentum ("ani yükselen coine atla, yükseliş bitince in") testi.
#
# ÖNCEDEN BELİRLENEN KURALLAR (sonuçlar görülmeden yazıldı, sonradan değiştirilmeyecek):
#   Evren   : Binance'teki TÜM USDT spot pariteleri, sonradan silinenler dahil (stabil/kaldıraçlı tokenler hariç)
#   Filtre  : son 24 saatlik işlem hacmi >= 500.000 $ ve en az 7 günlük geçmiş
#   Sinyal  : son L saatte getiri >= X  VE  son saatin hacmi, önceki 7 günün saatlik medyan hacminin >= V katı
#   Giriş   : sinyal saatinin kapanışında karar, bir sonraki saatin açılışında alım
#   Çıkış   : kapanış, giriş sonrası zirveden %Z düştüğünde (iz süren stop) ya da en fazla H saat sonra
#   Para    : en fazla 5 pozisyon, her biri o anki toplam değerin 1/5'i; aynı anda çok sinyal varsa en güçlüsü
#   Maliyet : işlem başına (alış ve satış ayrı) %0,1 komisyon + %0,2 kayma (küçük coinlerde gerçekçi)
#   Silinen coin: veri bittiği an son kapanıştan satılmış sayılır (iyimser; gerçekte daha kötü olur)
#
#   V1 (orta) : L=4,  X=%8,  V=5, Z=%5,  H=48
#   V2 (hızlı): L=1,  X=%5,  V=5, Z=%3,  H=12
#   V3 (yavaş): L=24, X=%15, V=3, Z=%10, H=168
#
# KONTROL: Aynı anlarda, aynı çıkış kurallarıyla ama RASTGELE seçilmiş (filtreyi geçen) bir coine giren bot (20 tekrar).
# BAŞARI ÖLÇÜTÜ: 2022-01 → 2026-10 net kâr > 0, BTC trend kuralını kârda geçmeli, en büyük düşüş < %50
#                VE rastgele girişlerin en az %95'inden iyi olmalı.

import glob
import os
import sys

import numpy as np
import pandas as pd

KLASOR = os.path.expanduser("~/kripto_bot/momentum")
BAS, BIT = pd.Timestamp("2022-01-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
KOMISYON, KAYMA = 0.001, float(os.environ.get("KAYMA", 0.002))
SLOT, MIN_HACIM_24S = 5, 500_000
VARYANTLAR = {"V1 orta": (4, 0.08, 5, 0.05, 48), "V2 hızlı": (1, 0.05, 5, 0.03, 12), "V3 yavaş": (24, 0.15, 3, 0.10, 168)}
RASTGELE_TEKRAR = 20

# --- Veri: geniş tablolar (satır = saat, sütun = coin) ---
cache = f"{KLASOR}/genis.npz"
if os.path.exists(cache):
    z = np.load(cache, allow_pickle=True)
    zaman, coinler = pd.DatetimeIndex(z["zaman"]).tz_localize("UTC"), list(z["coinler"])
    O, C, Hc = z["O"], z["C"], z["Hc"]
else:
    parcalar = {}
    for yol in sorted(glob.glob(f"{KLASOR}/veri/*.parquet")):
        d = pd.read_parquet(yol).set_index("zaman")
        parcalar[os.path.basename(yol)[:-8]] = d
    zaman = pd.date_range(pd.Timestamp("2021-11-01", tz="UTC"), BIT, freq="h", inclusive="left")
    coinler = list(parcalar)
    O = np.column_stack([parcalar[c]["open"].reindex(zaman).to_numpy() for c in coinler])
    C = np.column_stack([parcalar[c]["close"].reindex(zaman).to_numpy() for c in coinler])
    Hc = np.column_stack([parcalar[c]["hacim_usdt"].reindex(zaman).to_numpy() for c in coinler])
    np.savez(cache, zaman=zaman.tz_localize(None).to_numpy(), coinler=np.array(coinler), O=O, C=C, Hc=Hc)
print(f"{len(coinler)} coin, {len(zaman)} saat", flush=True)

Cdf, Hdf = pd.DataFrame(C), pd.DataFrame(Hc)
uygun = ((Hdf.rolling(24, min_periods=24).sum() >= MIN_HACIM_24S) & (Cdf.notna().cumsum() >= 168)).to_numpy()
medyan_hacim = Hdf.rolling(168, min_periods=100).median().shift(1).to_numpy()
test_bas = zaman.searchsorted(BAS)
# Bir coinin verisinin bittiği son saat (silinme / veri sonu)
son_saat = np.array([np.where(~np.isnan(C[:, j]))[0].max() if (~np.isnan(C[:, j])).any() else -1
                     for j in range(len(coinler))])


def sinyaller(L, X, V):
    getiri = (Cdf / Cdf.shift(L) - 1).to_numpy()
    with np.errstate(invalid="ignore", divide="ignore"):
        sinyal = uygun & (getiri >= X) & (Hc / medyan_hacim >= V)
    return sinyal, getiri


def simule(sinyal, guc, Z, H, rng=None):
    nakit, pozlar, kayit, deger = 1.0, {}, [], np.empty(len(zaman) - test_bas)
    alis_k, satis_k = 1 + KOMISYON + KAYMA, 1 - KOMISYON - KAYMA
    silinen = 0
    for i in range(test_bas, len(zaman) - 1):
        # 1) çıkışlar (kapanışta karar, sonraki açılışta işlem)
        for j in list(pozlar):
            p = pozlar[j]
            c = C[i, j]
            if np.isnan(c) or i >= son_saat[j]:          # veri bitti: son kapanıştan çık
                fiyat = C[son_saat[j], j] if np.isnan(c) else c
                silinen += i >= son_saat[j]
            else:
                p["zirve"] = max(p["zirve"], c)
                if c > p["zirve"] * (1 - Z) and i - p["giris_i"] < H:
                    continue
                fiyat = O[i + 1, j] if not np.isnan(O[i + 1, j]) else c
            nakit += p["adet"] * fiyat * satis_k
            kayit.append((zaman[p["giris_i"]], coinler[j], p["maliyet"], p["adet"] * fiyat * satis_k))
            del pozlar[j]
        # 2) toplam değer (kapanış fiyatlarıyla)
        toplam = nakit + sum(p["adet"] * (C[i, j] if not np.isnan(C[i, j]) else p["son"]) for j, p in pozlar.items())
        for j, p in pozlar.items():
            if not np.isnan(C[i, j]):
                p["son"] = C[i, j]
        deger[i - test_bas] = toplam
        # 3) girişler
        bos = SLOT - len(pozlar)
        if bos <= 0:
            continue
        adaylar = np.where(sinyal[i])[0]
        adaylar = [j for j in adaylar if j not in pozlar and not np.isnan(O[i + 1, j])]
        if not adaylar:
            continue
        if rng is None:
            adaylar = sorted(adaylar, key=lambda j: -guc[i, j])[:bos]
        else:   # kontrol: aynı sayıda, filtreyi geçen rastgele coin
            havuz = [j for j in np.where(uygun[i])[0] if j not in pozlar and not np.isnan(O[i + 1, j])]
            adaylar = list(rng.choice(havuz, size=min(len(adaylar), bos, len(havuz)), replace=False))
        for j in adaylar:
            tutar = min(toplam / SLOT, nakit)
            if tutar <= 0:
                break
            fiyat = O[i + 1, j] * alis_k
            pozlar[j] = {"adet": tutar / fiyat, "maliyet": tutar, "zirve": O[i + 1, j], "giris_i": i + 1, "son": O[i + 1, j]}
            nakit -= tutar
    deger[-1] = deger[-2]
    return pd.Series(deger, index=zaman[test_bas:]), pd.DataFrame(kayit, columns=["giris", "coin", "maliyet", "donus"]), silinen


def ozet(deger, islemler):
    kar = islemler["donus"] - islemler["maliyet"]
    kazanc, kayip = kar[kar > 0], kar[kar <= 0]
    yillik = " ".join(f"{y}:%{(g.iloc[-1] / g.iloc[0] - 1) * 100:+.0f}" for y, g in deger.groupby(deger.index.year))
    return (f"kâr %{(deger.iloc[-1] - 1) * 100:+.0f} | düşüş %{(deger / deger.cummax() - 1).min() * 100:.0f} | "
            f"işlem {len(islemler)} | kazanan %{len(kazanc) / max(len(kar), 1) * 100:.0f} | "
            f"ort. kazanç %{(kazanc / islemler.loc[kazanc.index, 'maliyet']).mean() * 100:+.1f} / "
            f"ort. kayıp %{(kayip / islemler.loc[kayip.index, 'maliyet']).mean() * 100:+.1f} | "
            f"kâr faktörü {kazanc.sum() / max(-kayip.sum(), 1e-9):.2f}\n      {yillik}")


print(f"Dönem {BAS.date()} → {BIT.date()}, komisyon %{KOMISYON * 100:.1f} + kayma %{KAYMA * 100:.1f} (işlem başına)\n")
for ad, (L, X, V, Z, H) in VARYANTLAR.items():
    sinyal, guc = sinyaller(L, X, V)
    deger, islemler, silinen = simule(sinyal, guc, Z, H)
    print(f"{ad}: {ozet(deger, islemler)}")
    print(f"      silinme anında kapatılan pozisyon: {silinen} | en çok işlem: "
          + ", ".join(f"{k}({v})" for k, v in islemler["coin"].value_counts().head(5).items()))
    if "--kontrolsuz" not in sys.argv:
        sonuclar = [simule(sinyal, guc, Z, H, np.random.default_rng(t))[0].iloc[-1] for t in range(RASTGELE_TEKRAR)]
        print(f"      KONTROL (rastgele coin, {RASTGELE_TEKRAR} tekrar): kâr medyanı %{(np.median(sonuclar) - 1) * 100:+.0f}, "
              f"aralık %{(min(sonuclar) - 1) * 100:+.0f} … %{(max(sonuclar) - 1) * 100:+.0f} | "
              f"strateji rastgelelerin %{np.mean(np.array(sonuclar) < deger.iloc[-1]) * 100:.0f}'inden iyi")
    print(flush=True)
