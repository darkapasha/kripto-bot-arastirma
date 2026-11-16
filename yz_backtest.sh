#!/bin/bash
# Yapay zekâ stratejilerini 2022-2026 arasında walk-forward ile test eder.
# İlk strateji modelleri eğitir (her 30 günde bir); diğerleri aynı modelleri yeniden kullanır.
cd ~/kripto_bot && mkdir -p loglar
DONEM=${DONEM:-20220101-20261101}
for S in ${@:-YapayZeka YapayZekaTrend YapayZekaEsik05 YapayZekaEsik02}; do
  echo "===== $S ($DONEM) ====="
  rm -f user_data/backtest_results/*
  docker compose run --rm freqtrade backtesting \
    --config user_data/config.json --config user_data/config_freqai.json \
    --strategy "$S" --freqaimodel LightGBMRegressor --timerange "$DONEM" \
    --fee 0.001 --cache none --pairs BTC/USDT --export trades > "loglar/$S.log" 2>&1 \
    || { echo "HATA, son satırlar:"; tail -20 "loglar/$S.log"; continue; }
  docker compose run --rm --entrypoint python freqtrade user_data/ozet.py 2>/dev/null
done
