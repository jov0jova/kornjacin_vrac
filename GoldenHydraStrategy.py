from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class GoldenHydraStrategy(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'
    minimal_roi = {
        "0": 0.015
    }
    stoploss = -0.012
    trailing_stop = False
    trailing_stop_positive = 0.0
    trailing_stop_positive_offset = 0.0
    trailing_only_offset_is_reached = False
    use_custom_stoploss = False
    process_only_new_candles = True
    startup_candle_count: int = 50

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['ema20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['macd'], dataframe['macdsignal'], dataframe['macdhist'] = ta.MACD(dataframe)
        dataframe['bollinger_upper'], dataframe['bollinger_middle'], dataframe['bollinger_lower'] = ta.BBANDS(dataframe)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] < 30) &  # Oversold
                (dataframe['ema20'] > dataframe['ema50']) &  # EMA 20 above EMA 50
                (dataframe['close'] > dataframe['ema20']) &  # Price above EMA 20
                (dataframe['macd'] > dataframe['macdsignal'])  # MACD bullish
            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] > 70) |  # Overbought
                (dataframe['close'] < dataframe['ema20']) |  # Price below EMA 20
                (dataframe['close'] < dataframe['ema50']) |  # Price below EMA 50
                (dataframe['macd'] < dataframe['macdsignal'])  # MACD bearish
            ),
            'sell'] = 1
        return dataframe
