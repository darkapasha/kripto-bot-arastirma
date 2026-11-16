# Çıta (baseline) stratejileri: yapay zekâ modellerinin geçmesi gereken basit kurallar.
# Hepsi sadece spot, kaldıraçsız, tek pozisyon (tüm bakiye) çalışır.

import talib.abstract as ta
from pandas import DataFrame

from freqtrade.strategy import IStrategy


class _Temel(IStrategy):
    INTERFACE_VERSION = 3
    can_short = False
    minimal_roi = {"0": 100}      # kâr hedefiyle çıkış yok, sadece sinyalle
    stoploss = -0.99              # zarar kesme yok (ayrıca belirtilmedikçe)
    use_exit_signal = True
    process_only_new_candles = True
    startup_candle_count = 0

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        return df

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        return df


class AlTut(_Temel):
    """İlk mumda al, hiç satma."""
    timeframe = "1d"

    def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df["enter_long"] = 1
        return df


class TrendGunluk(_Temel):
    """Günlük kapanış 100 günlük ortalamanın üstündeyse BTC'de kal, altına inerse nakite geç."""
    timeframe = "1d"
    startup_candle_count = 100

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        df["sma100"] = ta.SMA(df, timeperiod=100)
        return df

    def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df.loc[df["close"] > df["sma100"], "enter_long"] = 1
        return df

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df.loc[df["close"] < df["sma100"], "exit_long"] = 1
        return df


class EmaKesisim(_Temel):
    """Saatlik EMA50, EMA200'ü yukarı keserse al, aşağı keserse sat."""
    timeframe = "1h"
    startup_candle_count = 200

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        df["ema50"] = ta.EMA(df, timeperiod=50)
        df["ema200"] = ta.EMA(df, timeperiod=200)
        return df

    def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df.loc[df["ema50"] > df["ema200"], "enter_long"] = 1
        return df

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df.loc[df["ema50"] < df["ema200"], "exit_long"] = 1
        return df


class RsiDonus(_Temel):
    """Saatlik RSI 30'un altına düşünce al, 70'in üstüne çıkınca sat. %10 zarar kesme."""
    timeframe = "1h"
    startup_candle_count = 30
    stoploss = -0.10

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        df["rsi"] = ta.RSI(df, timeperiod=14)
        return df

    def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df.loc[df["rsi"] < 30, "enter_long"] = 1
        return df

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df.loc[df["rsi"] > 70, "exit_long"] = 1
        return df
