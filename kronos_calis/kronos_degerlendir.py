# Kronos tahminlerini değerlendirir.
#
# ÖNCEDEN BELİRLENEN BAŞARI ÖLÇÜTÜ (tahminler bitmeden yazıldı):
#   1. Yön tahmininde AUC > 0,55 (20 günlük getiri yukarı mı?)
#   2. "Trend + Kronos" (trend içeride VE Kronos yükseliş bekliyor) trend kuralını HEM kârda HEM düşüşte geçmeli
#   3. "Sadece Kronos" (Kronos yükseliş bekliyorsa içeride) al-tut'u kârda geçmeli
# 1 ve 2 tutmazsa Kronos trend botuna eklenmez.
#
# Her tahmin bir sonraki tahmine kadar (5 gün) geçerli sayılır. Karar gün kapanışında, işlem ertesi açılışta.

import os
import sys

import pandas as pd
from sklearn.metrics import roc_auc_score

coin = sys.argv[1] if len(sys.argv) > 1 else "BTC"
UFUK, KOMISYON = 20, 0.001
t = pd.read_csv(os.path.expanduser(f"~/kripto_bot/kronos_calis/tahmin_{coin}.csv"), parse_dates=["date"]).set_index("date")
d = pd.read_feather(os.path.expanduser(f"~/kripto_bot/user_data/data/binance/{coin}_USDT-1d.feather")).set_index("date")
d["trend"] = d["close"] > d["close"].rolling(100).mean()
d["gercek"] = d["open"].shift(-(UFUK + 1)) / d["open"].shift(-1) - 1
d = d[(d.index >= t.index.min()) & (d.index < pd.Timestamp("2026-11-01", tz="UTC"))]

e = t.join(d[["gercek", "trend"]]).dropna(subset=["gercek"])
print(f"{coin}: {len(t)} tahmin ({t.index.min().date()} → {t.index.max().date()}), etiketi belli olan {len(e)}")
print(f"  AUC (yön): {roc_auc_score(e['gercek'] > 0, e['tahmin_getiri']):.3f} | "
      f"korelasyon: {e['tahmin_getiri'].corr(e['gercek']):+.3f} | "
      f"yön isabeti %{((e['tahmin_getiri'] > 0) == (e['gercek'] > 0)).mean() * 100:.1f} "
      f"(piyasa %{(e['gercek'] > 0).mean() * 100:.0f} oranında yükselmiş)")
print(f"  Kronos'un yükseliş beklediği tahmin oranı: %{(t['tahmin_getiri'] > 0).mean() * 100:.0f}")
print("  AUC yıllara göre: " + " ".join(f"{y}:{roc_auc_score(g['gercek'] > 0, g['tahmin_getiri']):.2f}"
                                      for y, g in e.groupby(e.index.year) if (g["gercek"] > 0).nunique() > 1))
te = e[e["trend"].astype(bool)]
if (te["gercek"] > 0).nunique() > 1:
    print(f"  Sadece trend günlerinde AUC: {roc_auc_score(te['gercek'] > 0, te['tahmin_getiri']):.3f} ({len(te)} tahmin)")

kronos_yukari = (t["tahmin_getiri"] > 0).reindex(d.index, method="ffill").fillna(False)


def sim(icerde):
    pos = icerde.astype(int).shift(1).fillna(0)
    getiri = (d["open"].shift(-1) / d["open"] - 1).fillna(0)
    deger = (1 + pos * getiri - pos.diff().abs().fillna(pos.iloc[0]) * KOMISYON).cumprod()
    islem = int(pos.diff().abs().sum() / 2)
    print(f"  {'':2}kâr %{(deger.iloc[-1] - 1) * 100:+6.0f} | düşüş %{(deger / deger.cummax() - 1).min() * 100:4.0f} | işlem {islem:>3}", end="")


for ad, icerde in (("Al-tut", pd.Series(True, index=d.index)), ("Trend", d["trend"]),
                   ("Sadece Kronos", kronos_yukari), ("Trend + Kronos", d["trend"] & kronos_yukari)):
    print(f"\n{ad:<15}", end="")
    sim(icerde)
print()
