# Kronos ile eğitimsiz (zero-shot) tahmin: her test günü için son BAGLAM günlük mumu verip
# sonraki UFUK günü tahmin ettirir. Sonuç: tahmini getiri = tahmini kapanış(t+UFUK) / kapanış(t) - 1.
# Yarıda kalırsa kaldığı yerden devam eder (çıktı dosyasındaki günleri atlar).
#
# Kullanım: python kronos_tahmin.py BTC [başlangıç] [bitiş] [--hiz]

import os
import sys
import time

import pandas as pd
import torch

sys.path.insert(0, os.path.expanduser("~/kripto_bot/kronos"))
from model import Kronos, KronosPredictor, KronosTokenizer  # noqa: E402

MODEL, TOKENIZER = "NeoQuasar/Kronos-small", "NeoQuasar/Kronos-Tokenizer-base"
BAGLAM, UFUK, ORNEK, PARTI = 400, 20, 5, 16
ADIM = 5   # her 5. gün tahmin edilir (CPU'da gün başına ~32 sn sürüyor)
VERI = os.path.expanduser("~/kripto_bot/user_data/data/binance/{}_USDT-1d.feather")

hiz_testi = "--hiz" in sys.argv
argumanlar = [a for a in sys.argv[1:] if a != "--hiz"]
coin = argumanlar[0]
bas = pd.Timestamp(argumanlar[1] if len(argumanlar) > 1 else "2022-01-01", tz="UTC")
bit = pd.Timestamp(argumanlar[2] if len(argumanlar) > 2 else "2026-11-01", tz="UTC")
cikti = os.path.expanduser(f"~/kripto_bot/kronos_calis/tahmin_{coin}.csv")

torch.manual_seed(42)
torch.set_num_threads(4)
predictor = KronosPredictor(Kronos.from_pretrained(MODEL), KronosTokenizer.from_pretrained(TOKENIZER),
                            device="cpu", max_context=512)

df = pd.read_feather(VERI.format(coin))
df["amount"] = df["volume"] * df[["open", "high", "low", "close"]].mean(axis=1)
gunler = [i for i in df.index[(df["date"] >= bas) & (df["date"] < bit)] if i >= BAGLAM][::ADIM]
if os.path.exists(cikti) and not hiz_testi:
    bitmis = set(pd.read_csv(cikti, parse_dates=["date"])["date"])
    gunler = [i for i in gunler if df.at[i, "date"] not in bitmis]
if hiz_testi:
    gunler = gunler[:PARTI]
print(f"{coin}: {len(gunler)} gün tahmin edilecek", flush=True)

for p in range(0, len(gunler), PARTI):
    parti = gunler[p:p + PARTI]
    t0 = time.time()
    x_list, xt_list, yt_list = [], [], []
    for i in parti:
        x = df.iloc[i - BAGLAM + 1:i + 1]
        x_list.append(x[["open", "high", "low", "close", "volume", "amount"]].reset_index(drop=True))
        xt_list.append(x["date"].dt.tz_localize(None).reset_index(drop=True))
        yt_list.append(pd.Series(pd.date_range(x["date"].iloc[-1].tz_localize(None) + pd.Timedelta(days=1),
                                               periods=UFUK, freq="D")))
    tahminler = predictor.predict_batch(x_list, xt_list, yt_list, pred_len=UFUK, T=1.0, top_p=0.9,
                                        sample_count=ORNEK, verbose=False)
    satirlar = [{"date": df.at[i, "date"], "close": df.at[i, "close"],
                 "tahmin_getiri": t["close"].iloc[-1] / df.at[i, "close"] - 1,
                 "tahmin_getiri_5": t["close"].iloc[4] / df.at[i, "close"] - 1}
                for i, t in zip(parti, tahminler)]
    if hiz_testi:
        print(pd.DataFrame(satirlar).to_string(), f"\n{len(parti)} gün {time.time() - t0:.1f} sn")
        break
    pd.DataFrame(satirlar).to_csv(cikti, mode="a", header=not os.path.exists(cikti), index=False)
    print(f"{p + len(parti)}/{len(gunler)} ({time.time() - t0:.0f} sn/parti)", flush=True)
