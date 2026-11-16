# Yapay zekâ stratejisi (FreqAI + LightGBM).
# Model her 30 günde bir, sadece önceki 365 günü görerek yeniden eğitilir (walk-forward).
# Tahmin edilen şey: "24 saat sonra fiyat yüzde kaç değişmiş olacak?"
# Al: tahmin komisyonu rahatça aşıyorsa (ESIK). Sat: tahmin eksiye dönünce.

import talib.abstract as ta
from pandas import DataFrame

from freqtrade.strategy import IStrategy, informative


class YapayZeka(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = "1h"
    can_short = False
    minimal_roi = {"0": 100}
    stoploss = -0.99
    use_exit_signal = True
    process_only_new_candles = True
    startup_candle_count = 2500   # 1d göstergeleri (100 gün) için ~104 günlük saatlik veri

    ESIK = 0.01                   # beklenen 24 saatlik getiri en az %1 (alış+satış komisyonunun 5 katı)
    TREND_FILTRESI = False

    # --- Modelin gördüğü bilgiler (özellikler) ---
    def feature_engineering_expand_all(self, dataframe: DataFrame, period: int, metadata: dict, **kwargs) -> DataFrame:
        dataframe["%-rsi-period"] = ta.RSI(dataframe, timeperiod=period)
        dataframe["%-mfi-period"] = ta.MFI(dataframe, timeperiod=period)
        dataframe["%-adx-period"] = ta.ADX(dataframe, timeperiod=period)
        dataframe["%-roc-period"] = ta.ROC(dataframe, timeperiod=period)
        dataframe["%-sma_uzaklik-period"] = dataframe["close"] / ta.SMA(dataframe, timeperiod=period) - 1
        dataframe["%-oynaklik-period"] = dataframe["close"].pct_change().rolling(period).std()
        dataframe["%-hacim_oran-period"] = dataframe["volume"] / dataframe["volume"].rolling(period).mean()
        return dataframe

    def feature_engineering_expand_basic(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        dataframe["%-getiri_1"] = dataframe["close"].pct_change()
        return dataframe

    def feature_engineering_standard(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        dataframe["%-gun"] = dataframe["date"].dt.dayofweek
        dataframe["%-saat"] = dataframe["date"].dt.hour
        return dataframe

    # --- Modelin öğrenmeye çalıştığı cevap (hedef) ---
    def set_freqai_targets(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        n = self.freqai_info["feature_parameters"]["label_period_candles"]
        dataframe["&-getiri"] = dataframe["close"].shift(-n) / dataframe["close"] - 1
        return dataframe

    # --- Trend filtresi için günlük 100 ortalama (çıta stratejisiyle aynı kural) ---
    @informative("1d")
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["sma100"] = ta.SMA(dataframe, timeperiod=100)
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self.freqai.start(dataframe, metadata, self)

    def _trend(self, df: DataFrame):
        return df["close_1d"] > df["sma100_1d"]

    def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        kosul = (df["do_predict"] == 1) & (df["&-getiri"] > self.ESIK)
        if self.TREND_FILTRESI:
            kosul &= self._trend(df)
        df.loc[kosul, "enter_long"] = 1
        return df

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        kosul = df["&-getiri"] < 0
        if self.TREND_FILTRESI:
            kosul |= ~self._trend(df)
        df.loc[kosul, "exit_long"] = 1
        return df


class YapayZekaTrend(YapayZeka):
    """Aynı model, ama sadece BTC günlük trendi yukarıyken işlem yapar."""
    TREND_FILTRESI = True


# Eşik duyarlılığı: aynı model, farklı "ne kadar eminsen al" seviyeleri
class YapayZekaEsik05(YapayZeka):
    ESIK = 0.005


class YapayZekaEsik02(YapayZeka):
    ESIK = 0.02
