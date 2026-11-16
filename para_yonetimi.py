# Para yönetimi (bahis büyüklüğü) algoritmalarını aynı oyunda karşılaştırır.
# Oyun: her tur, yatırılan tutar ya ikiye katlanır ya kaybedilir (kazanma ihtimali p). 1000 TL, 100 tur, 10.000 tekrar.

import random

TUR, TEKRAR = 100, 10000


def oyna(p, kural):
    para, bahis, kenar, aktif = 1000.0, 20.0, 500.0, 500.0
    for _ in range(TUR):
        if kural == "senin kuralın":
            if aktif < 1:
                break
            if random.random() < p:
                kenar += aktif
            else:
                aktif = kenar / 2
                kenar -= aktif
            continue
        if para < 1:
            break
        b = {"sabit tutar (20 TL)": min(20, para),
             "sabit %2": para * 0.02,
             "yarım Kelly": para * max(2 * p - 1, 0) / 2,
             "Kelly": para * max(2 * p - 1, 0),
             "aşırı (%50)": para * 0.5,
             "martingale (kaybedince 2x)": min(bahis, para),
             "ters martingale (kazanınca 2x)": min(bahis, para)}[kural]
        kazandi = random.random() < p
        para += b if kazandi else -b
        if kural.startswith("martingale"):
            bahis = 20 if kazandi else bahis * 2
        elif kural.startswith("ters"):
            bahis = bahis * 2 if kazandi and bahis < 160 else 20
    return kenar + aktif if kural == "senin kuralın" else para


KURALLAR = ["sabit tutar (20 TL)", "sabit %2", "yarım Kelly", "Kelly", "aşırı (%50)",
            "martingale (kaybedince 2x)", "ters martingale (kazanınca 2x)", "senin kuralın"]
for p in (0.55, 0.50, 0.45):
    print(f"\n--- her turu kazanma ihtimali %{p * 100:.0f}, {TUR} tur, 1000 TL ---")
    print(f"{'kural':<32}{'ortanca':>9}{'ortalama':>10}{'zararda %':>11}{'yarısını kaybeden %':>21}")
    for k in KURALLAR:
        random.seed(7)
        s = sorted(oyna(p, k) for _ in range(TEKRAR))
        print(f"{k:<32}{s[TEKRAR // 2]:>9.0f}{sum(s) / TEKRAR:>10.0f}"
              f"{sum(x < 1000 for x in s) / TEKRAR * 100:>11.0f}{sum(x < 500 for x in s) / TEKRAR * 100:>21.0f}")
