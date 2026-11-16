#!/bin/bash
# Tüm çıta stratejilerini üç dönemde, %0,1 komisyonla test eder.
# Freqtrade tek seferde tek zaman dilimi kabul ettiği için her strateji ayrı çalıştırılır.
cd ~/kripto_bot
DONEMLER="20180101-20261101 20180101-20220101 20220101-20261101"
STRATEJILER="AlTut:1d TrendGunluk:1d EmaKesisim:1h RsiDonus:1h"
for D in $DONEMLER; do
  echo "===== DÖNEM $D ====="
  printf "%-12s %7s %12s %12s %10s\n" Strateji İşlem "Kâr %" "Max düşüş" Kazanma%
  for S in $STRATEJILER; do
    AD=${S%%:*}; TF=${S##*:}
    docker compose run --rm freqtrade backtesting --config user_data/config.json \
      --strategy "$AD" --timeframe "$TF" --timerange "$D" --fee 0.001 --cache none 2>/dev/null \
      | sed -n '/STRATEGY SUMMARY/,/^$/p' | grep "│ *$AD *│" \
      | awk -F'│' -v ad="$AD" '{gsub(/ +/," "); n=split($8,w," "); printf "%-12s %7s %12s %12s %10s\n", ad, $3, $6, $9, w[n]}'
  done
  docker compose run --rm --entrypoint python freqtrade user_data/dca.py \
    "${D:0:4}-${D:4:2}-${D:6:2}" "${D:9:4}-${D:13:2}-${D:15:2}" 2>/dev/null
done
