# Binance'in herkese açık veri arşivinden TÜM USDT spot paritelerinin saatlik mumlarını indirir,
# sonradan borsadan silinen coinler dahil (hayatta kalan yanılgısını önlemek için).
# Çıktı: ~/kripto_bot/momentum/veri/<SEMBOL>.parquet

import io
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

KOK = "https://data.binance.vision"
LISTE = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
KLASOR = os.path.expanduser("~/kripto_bot/momentum/veri")
AYLAR = pd.period_range("2021-11", "2026-10", freq="M")   # 2022 öncesi 2 ay: göstergeler için ısınma
# Sabit/kaldıraçlı tokenler momentum testine uygun değil
DISLA = re.compile(r"^(USDC|BUSD|TUSD|FDUSD|USDP|DAI|PAX|EUR|GBP|AUD|TRY|BRL|UST|USTC|AEUR|EURI|USD1|XUSD|BFUSD|RLUSD|PYUSD)USDT$"
                   r"|(UP|DOWN|BULL|BEAR)USDT$")
NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
os.makedirs(KLASOR, exist_ok=True)


def semboller():
    sonuc, isaret = [], ""
    while True:
        url = f"{LISTE}?delimiter=/&prefix=data/spot/monthly/klines/&marker={isaret}"
        kok = ET.fromstring(urllib.request.urlopen(url, timeout=60).read())
        onekler = [p.find("s3:Prefix", NS).text for p in kok.findall("s3:CommonPrefixes", NS)]
        sonuc += [o.rstrip("/").split("/")[-1] for o in onekler]
        if kok.find("s3:IsTruncated", NS).text != "true":
            return sonuc
        isaret = onekler[-1]


def ay_indir(sembol, ay):
    s = urllib.parse.quote(sembol)
    url = f"{KOK}/data/spot/monthly/klines/{s}/1h/{s}-1h-{ay.strftime('%Y-%m')}.zip"
    try:
        veri = urllib.request.urlopen(url, timeout=60).read()
    except urllib.error.HTTPError:
        return None
    with zipfile.ZipFile(io.BytesIO(veri)) as z:
        df = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 1, 2, 3, 4, 7])
    df.columns = ["zaman", "open", "high", "low", "close", "hacim_usdt"]
    df = df[pd.to_numeric(df["zaman"], errors="coerce").notna()].astype(float)
    # 2025'ten itibaren zaman damgaları mikro saniye
    df["zaman"] = pd.to_datetime(df["zaman"].where(df["zaman"] < 1e14, df["zaman"] / 1000), unit="ms", utc=True)
    return df


def sembol_indir(sembol):
    yol = f"{KLASOR}/{sembol}.parquet"
    if os.path.exists(yol):
        return sembol, "var"
    parcalar = [p for p in (ay_indir(sembol, ay) for ay in AYLAR) if p is not None]
    if not parcalar:
        return sembol, "veri yok"
    pd.concat(parcalar).drop_duplicates("zaman").sort_values("zaman").to_parquet(yol, index=False)
    return sembol, len(parcalar)


tum = [s for s in semboller() if s.endswith("USDT") and not DISLA.search(s)]
print(f"{len(tum)} USDT paritesi bulundu", flush=True)
with ThreadPoolExecutor(12) as havuz:
    for i, (s, durum) in enumerate(havuz.map(sembol_indir, tum), 1):
        if i % 25 == 0 or durum == "veri yok":
            print(f"{i}/{len(tum)} {s}: {durum}", flush=True)
print("bitti", flush=True)
