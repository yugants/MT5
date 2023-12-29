import talib
import pandas as pd
import numpy as np
from datetime import datetime
import datetime
import MetaTrader5 as mt5
import pandas_ta as ta
from scipy.signal import savgol_filter, find_peaks


class LiveTrade:
    def __init__(self, instrument):
        #         self.df = pd.DataFrame(yf.download(tickers=instrument, start = '2022-10-01', end = '2023-06-01', interval='1h'))
        if not mt5.initialize(
            login=114999529, server="Exness-MT5Trial6", password="Mypassword$1234"
        ):
            print("initialize() failed, error code =", mt5.last_error())
            quit()

        login = 114999529
        password = "Mypassword$1234"
        server = "Exness-MT5Trial6"
        mt5.login(login, password, server)

        rate = mt5.copy_rates_from(
            instrument[0], mt5.TIMEFRAME_M15, datetime.datetime.now(), instrument[2]
        )
        nf = pd.DataFrame(rate)

        nf["date"] = pd.to_datetime(nf["time"], unit="s")

        nf.set_index(np.arange(len(nf)), inplace=True)
        nf = nf.drop(["spread", "real_volume", "tick_volume", "time"], axis="columns")

        self.df = nf.iloc[:500]  # First half
        self.df2 = nf.iloc[500:]  # Second half

        #         self.account = 10000

        self.prev_high, self.prev_low, self.current_high, self.current_low = (
            float(),
            float(),
            float(),
            float(),
        )

        #         For EURUSD
        self.one_pip_value = instrument[1]

        # For Big Candle Pause

        self.big_candle = False
        self.big_candle_count = 0

        #     For Doji Condition

        self.doji_counter = 0
        self.doji_flag = False

        # Longer EMA
        self.ema_value = instrument[3]

        #     For counting 20 candles after climax

        self.buy_flag = True
        self.sell_flag = True
        self.green_count = 0
        self.red_count = 0

        self.df["tradable"] = 0
        #         self.df.at[length, 'tradable'] = 0

        self.result = pd.DataFrame(
            columns=[
                "ENTRY DATE",
                "ENTRY",
                "QUANTITY",
                "TRADE",
                "EXIT",
                "EXIT DATE",
                "P/L",
                "REAL P/L",
                "S/L",
                "SET_TRG",
                "SET_BRK",
            ]
        )

        self.trade_on = None

        self.buy_on = False
        self.sell_on = False


    def trend(self):

        if len(self.peaks_idx) > 2 and len(self.troughs_idx) > 2:

            length = len(self.df)-1
        
            if (
                # Current Price > EMA 
                self.df.loc[length, 'close'] > self.df.loc[length,'EMA_200'] and 
                # Current price > Current Low
                self.df.loc[self.troughs_idx[-1], 'close'] <= self.df.loc[length,'close'] and
                # Current Low > Prev Low
                self.df.loc[self.troughs_idx[-2], 'close'] <= self.df.loc[self.troughs_idx[-1], 'close'] and
                # Current High > Prev High
                self.df.loc[self.peaks_idx[-1], 'close'] > self.df.loc[self.peaks_idx[-2], 'close']
            ):
                self.df.loc[length, 'trend'] = 'up'

            elif (
                # Current Price < EMA
                self.df.loc[length,'close'] < self.df.loc[length,'EMA_200'] and
                # Current price < Current High
                self.df.loc[length,'close'] <= self.df.loc[self.peaks_idx[-1], 'close'] and
                # Current High < Prev High
                self.df.loc[self.peaks_idx[-1], 'close'] < self.df.loc[self.peaks_idx[-2], 'close'] and
                # Current Low < Prev Low
                self.df.loc[self.troughs_idx[-1], 'close'] < self.df.loc[self.troughs_idx[-2], 'close']
            ):
                self.df.loc[length, 'trend'] = 'down'

            
            else:

                self.df.loc[length, 'trend'] = 'no trend'


    def candle(self, df):
        """Return candle colour"""

        if df["close"] - df["open"] > 0:
            return "G"

        else:
            return "R"

    def get_kc(self, high, low, close, kc_lookback, multiplier, atr_lookback):
        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift()))
        tr3 = pd.DataFrame(abs(low - close.shift()))

        # Calculate True Range as the element-wise maximum of the three components
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.ewm(alpha=1 / atr_lookback).mean()

        kc_middle = close.ewm(span=kc_lookback).mean()
        kc_upper = kc_middle + multiplier * atr
        kc_lower = kc_middle - multiplier * atr

        return kc_middle.iloc[-1], kc_upper.iloc[-1], kc_lower.iloc[-1]

    def calculate_indicators(self):
        #         print('calc_indicator')
        length = len(self.df) - 1

        self.df.loc[length, "EMA_200"] = talib.EMA(
            self.df["close"], timeperiod=self.ema_value
        ).iloc[-1]

        self.df.loc[length, "EMA_15"] = talib.EMA(
            self.df["close"], timeperiod=15
        ).iloc[-1]
        

        self.df.loc[length, "candle"] = self.candle(self.df.iloc[-1])

        (
            self.df.loc[length, "EMA_20"],
            self.df.loc[length, "upper_keltner"],
            self.df.loc[length, "lower_keltner"],
        ) = self.get_kc(
            self.df["high"],
            self.df["low"],
            self.df["close"],
            kc_lookback=20,
            multiplier=2.25,
            atr_lookback=10,
        )

        # For Peaks and Troughs

        self.df["atr"] = ta.atr(high=self.df.high, low=self.df.low, close=self.df.close)

        self.df["atr"] = self.df.atr.rolling(window=30).mean()

        self.df["close_smooth"] = savgol_filter(self.df.close, 30, 10)

        # Find peaks and troughs

        atr = self.df.atr.iloc[-1]
        self.peaks_idx, _ = find_peaks(
            self.df.close_smooth, distance=10, width=5, prominence=atr
        )
        self.troughs_idx, _ = find_peaks(
            -1 * self.df.close_smooth, distance=10, width=5, prominence=atr
        )

        self.trend()

        # Small Savgol

        self.small_peaks_idx,_ = find_peaks(self.df.close_smooth, distance = 10, width = 2, prominence= atr/10)

        self.small_troughs_idx,_ = find_peaks(-1*self.df.close_smooth, distance = 10, width = 2, prominence=atr/10)


    def check_body(self, df):
        one_percent = df["open"] / 100
        percent = one_percent * 0.05

        #     Calculate candle size close-open
        if df["candle"] == "G":
            candle_size = df["close"] - df["open"]
            upper_wick = df["high"] - df["close"]
            lower_wick = df["open"] - df["low"]

        else:
            candle_size = abs(df["close"] - df["open"])
            upper_wick = df["high"] - df["open"]
            lower_wick = df["close"] - df["low"]

        upper_wick_per = upper_wick / one_percent
        lower_wick_per = lower_wick / one_percent

        #     check for entry candle size and Max candle size 0.12 %
        if (candle_size > percent) and candle_size <= (0.12 * one_percent):
            if df["candle"] == "G" and upper_wick_per < 0.04:
                return 1

            elif df["candle"] == "R" and lower_wick_per < 0.04:
                return 1

            else:
                return 0

        else:
            return 0


    #   SL Method

    def set_sl(self, df):
        """Set SL 1% above/below to entry candle"""

        candle_size = df["high"] - df["low"]

        if df["candle"] == "G":
            sl = df["low"] - (candle_size / 100)

        elif df["candle"] == "R":
            sl = df["high"] + (candle_size / 100)

        #         print('SL: ', sl)

        return sl
    


    # To mark trades as Buy/ Sell

    def check_trade(self, df):
        if df["candle"] == "G":
            return "B"

        else:
            return "S"

    #     Check candle for climax condition
    def check_tradable(self, row):
        one_percent = row["open"] / 100

        length = len(self.df) - 1

        # Pause after Big candle

        large_per = (abs(row["close"] - row["open"]) / row["open"]) * 100

        if row["candle"] == "G":
            up_wick = (abs(row["close"] - row["high"]) / row["open"]) * 100
            low_wick = (abs(row["open"] - row["low"]) / row["open"]) * 100

        else:
            up_wick = (abs(row["open"] - row["high"]) / row["open"]) * 100
            low_wick = (abs(row["close"] - row["low"]) / row["open"]) * 100

        if large_per > 0.19 or up_wick > 0.19 or low_wick > 0.19:
            self.big_candle = True
            self.big_candle_count = 0
            self.df.loc[self.df["date"] == row["date"], "tradable"] = "Big"

        elif self.big_candle == True and self.big_candle_count < 10:
            self.big_candle_count += 1
            self.df.loc[self.df["date"] == row["date"], "tradable"] = "Big Range"

        elif self.big_candle_count == 9:
            self.big_candle = False
            self.big_candle_count = 0
            self.df.loc[self.df["date"] == row["date"], "tradable"] = 0

        # When green candle goes outside channel
        elif (
            (
                (row["candle"] == "G" and row["open"] > row["upper_keltner"])
                or (row["candle"] == "R" and row["close"] > row["upper_keltner"])
            )
            and self.sell_flag == True
            and (abs(row["close"] - row["upper_keltner"]) / one_percent) >= 0.07
        ):
            self.buy_flag = False
            self.green_count = 0
            self.df.at[length, "tradable"] = "First G Break"

        # When price remains outside after green breakout
        elif (
            row["close"] > row["upper_keltner"]
            and self.sell_flag == True
            and self.buy_flag == False
            and self.green_count == 0
        ):
            self.df.at[length, "tradable"] = "Outside after G Break"

        # Any candle in 20 count closes outside the channel, restart the count
        elif (
            row["close"] > row["upper_keltner"]
            and self.buy_flag == True
            and self.green_count > 0
        ):
            self.green_count = 0
            self.buy_flag = False
            self.df.at[length, "tradable"] = "Outside after G Break"

        # When the price returns inside the channel after a buy breakout
        elif row["close"] < row["upper_keltner"] and self.buy_flag == False:
            self.buy_flag = True
            self.green_count = 1
            self.df.at[length, "tradable"] = "G count 1"

        # Counting 20 candles when green breakout moves inside the channel
        elif 0 < self.green_count < 19 and row["close"] < row["upper_keltner"]:
            self.green_count += 1
            self.df.at[length, "tradable"] = "Counting after G Break"

        # When 20 candles after climax are over
        elif (
            self.green_count == 19
            and row["close"] < row["upper_keltner"]
            and self.red_count == 0
        ):
            self.green_count = 0
            self.df.at[length, "tradable"] = 0

        # When red candle goes outside the channel
        if (
            (
                (row["candle"] == "R" and row["open"] < row["lower_keltner"])
                or (row["candle"] == "G" and row["close"] < row["lower_keltner"])
            )
            and self.buy_flag == True
            and (abs(row["lower_keltner"] - row["close"]) / one_percent) >= 0.07
        ):
            self.sell_flag = False
            self.red_count = 0
            self.df.at[length, "tradable"] = "Red Breakout"

        # When the price remains outside the channel after a red breakout
        elif (
            row["close"] < row["lower_keltner"]
            and self.buy_flag == True
            and self.sell_flag == False
        ):
            self.df.at[length, "tradable"] = "Outside after Red Breakout"

        # Any candle in 20 count closes outside the channel, restart the count
        elif (
            row["close"] < row["lower_keltner"]
            and self.sell_flag == True
            and self.red_count > 0
        ):
            self.red_count = 0
            self.sell_flag = False
            self.df.at[length, "tradable"] = "Outside after R Break"

        # When the price returns inside the channel after a sell breakout
        elif row["close"] > row["lower_keltner"] and self.sell_flag == False:
            self.sell_flag = True
            self.red_count = 1
            self.df.at[length, "tradable"] = "Sell count 1"

        # Counting 20 candles when red breakout moves inside the channel
        elif 0 < self.red_count < 19 and row["close"] > row["lower_keltner"]:
            self.red_count += 1
            self.df.at[length, "tradable"] = "Counting after sell breakout"

        # When 20 candles after climax are over
        elif (
            self.red_count == 19
            and row["close"] > row["lower_keltner"]
            and self.green_count == 0
        ):
            self.red_count = 0
            self.df.at[length, "tradable"] = 0

        #         When Its a normal candle
        else:
            self.df.at[length, "tradable"] = 0

    #   Check if candle inside Keltner's Channel

    def check_candle(self, x):

        if x["candle"] == "G":

            if ( ( x['close'] > x['EMA_200'] ) and
                ((x["low"] < x["EMA_20"] and x["close"] >= x["EMA_20"]) or (
                x["low"] < x["EMA_15"] and x["close"] >= x["EMA_15"])) and
                ( x['high'] < x['upper_keltner'] ) and
                 ( x['close'] > self.df.close.iloc[self.small_peaks_idx[-1]] ) and
                 (x['trend'] == 'up')):
                
                return 1

            else:
                return 0

        elif x["candle"] == "R":

            if ( ( x['close'] < x['EMA_200'] ) and
                ((x["high"] > x["EMA_20"] and x["close"] <= x["EMA_20"]) or (
                x["high"] > x["EMA_15"] and x["close"] <= x["EMA_15"] )) and
                ( x['low'] > x['lower_keltner'] ) and
                 ( x['close'] < self.df.close.iloc[self.small_troughs_idx[-1]] ) and
                 (x['trend'] == 'down')):
                
                return 1

            else:
                return 0

        else:
            return 0

    #   Apply all the conditions on current candle

    def check_conditions(self):
        length = len(self.df) - 1

        #         Checking all entry conditions

        self.df.loc[length, "pos"] = self.check_candle(self.df.iloc[-1])

        self.df.loc[length, "candle_size"] = self.check_body(self.df.iloc[-1])

        self.df.loc[length, "trade"] = self.check_trade(self.df.iloc[-1])

        self.check_tradable(self.df.iloc[-1])

        self.chart = self.df.loc[length]["open"] / 100 * 0.04

        if (
            (self.df.loc[length, "pos"] == 1)
            and (self.df.loc[length, "candle_size"] == 1)
            and (self.df.loc[length, "tradable"] == 0)
        ):
            
            #             Set SL for ever entry
            self.df.loc[length, "sl"] = self.set_sl(self.df.iloc[-1])

            self.result_len = len(self.result)

            self.result.loc[self.result_len, "ENTRY DATE"] = self.df.loc[length, "date"]
            self.result.loc[self.result_len, "ENTRY"] = self.df.loc[length, "close"]
            self.result.loc[self.result_len, "TRADE"] = self.df.loc[length, "trade"]
            self.result.loc[self.result_len, "S/L"] = self.df.loc[length, "sl"]

            print('Entry candle: ', self.result.loc[len(self.result)-1, "ENTRY DATE"])




    def Caller(self, instrument):
        # Initialize an empty DataFrame to store the past data that gets dropped
        # self.past_df = pd.DataFrame()

        #         Loop for taking the live data
        for index, row in self.df2.iterrows():
            # Add live data to the df DataFrame
            self.df = self.df.append(row, ignore_index=True)
            # self.df = pd.concat([self.df, row], ignore_index=True)

            # Delete the first row if the DataFrame has more than 202 rows
            if len(self.df) > 500:
                # Save the dropped row in past_df
                # self.past_df = self.past_df.append(self.df.iloc[0], ignore_index=True)
                # self.past_df = pd.concat([self.past_df, self.df.iloc[0]], ignore_index=True)
                self.df = self.df.iloc[1:].reset_index(drop=True)

            # Calculate indicators for the current state of df
            self.calculate_indicators()

            # if self.buy_on == True:
            #     self.manage_buy()

            # elif self.sell_on == True:
            #     self.manage_sell()

            # else:
                #             Apply all entry conditions
            self.check_conditions()

        # Concatenate past_df and df to get the full dataset
        # self.result_df = pd.concat([self.past_df, self.df], ignore_index=True)

        # Save the result_df to an Excel file
        #         self.result_df.to_excel('combined.xlsx')

        self.result.to_excel(f"{instrument}.xlsx")



