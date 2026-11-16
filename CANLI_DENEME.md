# Sahte Parayla Canlı Deneme

**Başlangıç:** 2026-11-02, 14:55 UTC

**Strateji:** TrendGunluk. Bitcoin'in günlük kapanışı 100 günlük ortalamasının üstündeyse BTC'de kalır, altına inerse nakite geçer.

**Sanal bakiye:** 1000 USDT

**İlk işlem:** 2026-11-02'de 77.827$'dan 0,01272 BTC alındı (990 USDT).

**Gerçek para:** Yok. API anahtarı yok, emirler borsaya gitmiyor.

## Sunucuda

- Servis: `kripto_trend_canli` (Docker, `restart: unless-stopped`; sunucu yeniden başlasa da kendiliğinden açılır)
- İşlem kaydı: `~/kripto_bot/user_data/trend_canli.sqlite`
- Log: `~/kripto_bot/user_data/logs/trend_canli.log`
- Karar saati: Her gün 00:00 UTC (Türkiye saatiyle 03:00), günlük mum kapanınca.

## Telegram ✅ (2026-11-02 15:17 UTC'den beri açık)

Bot **@plidya_bot**, bildirimler Salim'in özel sohbetine gidiyor. Kullanılabilecek komutlar: `/status`, `/profit`, `/balance`, `/daily`, `/help`.

Uyarı: Token'ı başka bir programda (`getUpdates` ile) kullanma. Telegram'da aynı botu iki program aynı anda dinleyemez.

## Telegram'ı sıfırdan kurmak (ileride gerekirse)

1. Telegram'da **@BotFather**'a `/newbot` yaz, yeni bir bot oluştur ve verdiği **token**'ı kopyala.
   - Mevcut MMA/F1 botlarını kullanma. Aynı token'ı iki program aynı anda dinleyemez.
2. Yeni botuna bir mesaj at. Sonra **@userinfobot**'a yazıp kendi **chat_id**'ni öğren.
3. Sunucuda `~/kripto_bot/gizli/telegram.json` dosyasını aç (VS Code Remote-SSH ile):
   - `"enabled": false` değerini `true` yap.
   - Token'ı ve chat_id'yi yerlerine yapıştır.
4. Botu yeniden başlat:

```bash
cd ~/kripto_bot && docker compose up -d --force-recreate trend_canli
```

Bundan sonra Telegram'dan `/status`, `/profit`, `/balance`, `/daily` komutlarıyla durumu görebilirsin. Her alım ve satımda bildirim gelir.

## Telegram olmadan durumu görmek

```bash
cd ~/kripto_bot && grep -E "Long signal|Exit|exit_fill" user_data/logs/trend_canli.log | tail
```

## Ne zaman değerlendireceğiz?

Bu strateji yılda ~6 işlem yapıyor. Birkaç hafta içinde belki hiç işlem görmeyeceğiz. Canlı denemenin asıl amacı şunları doğrulamak:
1. Botun aylarca kesintisiz çalıştığını,
2. Kararları backtest'le aynı anda ve aynı şekilde verdiğini.

Kârlılığı ölçmek için haftalar değil, yıllar gerekiyor. Onun cevabını backtest veriyor.
