# Trend botunun (BTC günlük kapanış > N günlük ortalama) avantajı gerçek mi?
#   1) Komisyon etkisi: komisyonsuz / %0,1 / %0,5 (5 kat)
#   2) Rastgele kontrol: aynı "içeride / dışarıda" süre parçaları rastgele sıralanmış 5000 sahte bot
#   3) Sağlamlık: ortalama uzunluğu 50 / 75 / 100 / 150 / 200 gün
#   4) Aylık büyüme ve Kelly'ye göre doğru pozisyon büyüklüğü
# Kullanım: python avantaj_testi.py

import os

import numpy as np
import pandas as pd

VERI = os.path.expanduser("~/kripto_bot/user_data/data/binance/BTC_USDT-1d.feather")
d = pd.read_feather(VERI).set_index("date")
getiri = (d["open"].shift(-1) / d["open"] - 1).fillna(0)


def deger(icerde, komisyon, bas, bit):
    m = (d.index >= bas) & (d.index < bit)
    pos = icerde.astype(int).shift(1).fillna(0)[m]
    return (1 + pos * getiri[m] - pos.diff().abs().fillna(pos.iloc[0]) * komisyon).cumprod(), pos


def trend(n):
    return d["close"] > d["close"].rolling(n).mean()


DONEMLER = [("2018-01-01", "2026-11-01"), ("2022-01-01", "2026-11-01")]

print("1) KOMİSYON ETKİSİ (trend 100)")
for bas, bit in DONEMLER:
    satir = f"   {bas[:4]}–{bit[:4]}: "
    for k in (0, 0.001, 0.005):
        v, pos = deger(trend(100), k, bas, bit)
        satir += f"komisyon %{k * 100:.1f} → %{(v.iloc[-1] - 1) * 100:+.0f}   "
    al_tut = deger(pd.Series(True, index=d.index), 0.001, bas, bit)[0].iloc[-1]
    print(satir + f"(al-tut %{(al_tut - 1) * 100:+.0f}, işlem {int(pos.diff().abs().sum() / 2)})")

print("\n2) ŞANS MI? Aynı içeride/dışarıda süre parçaları rastgele sıralanmış 5000 sahte bot")
rng = np.random.default_rng(42)
for bas, bit in DONEMLER:
    v, pos = deger(trend(100), 0.001, bas, bit)
    gercek = v.iloc[-1]
    # pozisyonu "parçalara" böl (ör. 40 gün içeride, 25 gün dışarıda, ...), parçaları karıştır
    p = pos.to_numpy().astype(int)
    sinir = np.flatnonzero(np.diff(p)) + 1
    parcalar = np.split(p, sinir)
    r = getiri[(d.index >= bas) & (d.index < bit)].to_numpy()
    sonuclar = []
    for _ in range(5000):
        sira = rng.permutation(len(parcalar))
        q = np.concatenate([parcalar[i] for i in sira])
        degisim = np.abs(np.diff(np.concatenate([[0], q])))
        sonuclar.append(np.prod(1 + q * r - degisim * 0.001))
    sonuclar = np.array(sonuclar)
    print(f"   {bas[:4]}–{bit[:4]}: gerçek bot %{(gercek - 1) * 100:+.0f} | sahte botların ortancası %{(np.median(sonuclar) - 1) * 100:+.0f} | "
          f"gerçek bot sahtelerin %{(sonuclar < gercek).mean() * 100:.1f}'inden iyi (p = {(sonuclar >= gercek).mean():.3f})")

print("\n3) SAĞLAMLIK: ortalama uzunluğu (komisyon %0,1)")
for bas, bit in DONEMLER:
    print(f"   {bas[:4]}–{bit[:4]}: " + "  ".join(
        f"{n}g %{(deger(trend(n), 0.001, bas, bit)[0].iloc[-1] - 1) * 100:+.0f}" for n in (50, 75, 100, 150, 200)))

print("\n4) AYLIK BÜYÜME ve KELLY (trend 100, 2018–2026, dolar bazında)")
v, pos = deger(trend(100), 0.001, "2018-01-01", "2026-11-01")
gunluk = v.pct_change().dropna()
yil = len(v) / 365
print(f"   yıllık bileşik büyüme %{(v.iloc[-1] ** (1 / yil) - 1) * 100:.1f} → aylık ortalama %{(v.iloc[-1] ** (1 / (yil * 12)) - 1) * 100:.2f}")
aylik = v.resample("ME").last().pct_change().dropna()
print(f"   takvim ayları: {len(aylik)} ay, zarar eden %{(aylik < 0).mean() * 100:.0f}, ortanca %{aylik.median() * 100:+.1f}, "
      f"en iyi %{aylik.max() * 100:+.0f}, en kötü %{aylik.min() * 100:+.0f}")
# Sürekli getiri için Kelly oranı ≈ ortalama / varyans (paranın kaç katı pozisyon)
kelly = gunluk.mean() / gunluk.var()
print(f"   Kelly pozisyon büyüklüğü ≈ paranın {kelly:.2f} katı (yarım Kelly ≈ {kelly / 2:.2f} katı)")
for kat in (0.5, 1.0, 2.0, 3.0):
    vv = (1 + kat * gunluk).cumprod()
    print(f"   paranın {kat:.1f} katı pozisyon: toplam %{(vv.iloc[-1] - 1) * 100:+.0f}, en büyük düşüş %{(vv / vv.cummax() - 1).min() * 100:.0f}"
          + ("  (kaldıraç!)" if kat > 1 else ""))
