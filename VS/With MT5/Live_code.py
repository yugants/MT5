import talib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random, time
import MetaTrader5 as mt5
import pandas_ta as ta
from scipy.signal import savgol_filter, find_peaks


class LiveTrade:
    def __init__(self, instrument):
        
        try:
            if not mt5.initialize(
                login=114999529, server="Exness-MT5Trial6", password="Mypassword$1234"
            ):
                print("initialize() failed, error code =", mt5.last_error())
                quit()

            login = 114999529
            password = "Mypassword$1234"
            server = "Exness-MT5Trial6"
            mt5.login(login, password, server)

            self.df = pd.DataFrame(mt5.copy_rates_from(
                instrument[0], mt5.TIMEFRAME_M15, datetime.now(), instrument[2]
            ))

            self.df["date"] = pd.to_datetime(self.df["time"], unit="s")

            self.df.set_index(np.arange(len(self.df)), inplace=True)
            self.df = self.df.drop(["spread", "real_volume", "tick_volume", "time"], axis="columns")


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

            # Pair name

            self.pair = instrument[0]

            # Account object

            self.account_info = mt5.account_info()

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

        except Exception as e:
            print(f"An error occurred: {e}")
    




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

        self.df.loc[length, "EMA_8"] = talib.EMA(self.df["close"], timeperiod=8).iloc[
            -1
        ]
        self.df.loc[length, "EMA_15"] = talib.EMA(self.df["close"], timeperiod=15).iloc[
            -1
        ]
        self.df.loc[length, "EMA_200"] = talib.EMA(
            self.df["close"], timeperiod=200
        ).iloc[-1]
        self.df.loc[length, "RSI"] = talib.RSI(self.df["close"], timeperiod=21).iloc[-1]

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

        # EMA angle

        self.df['EMA_Diff'] = self.df['EMA_20'].diff()
        self.df['Angle'] = np.degrees((np.arctan(self.df['EMA_Diff'] / 20)) * 100000)


        # For Peaks and Troughs

        self.df["atr"] = ta.atr(high=self.df.high, low=self.df.low, close=self.df.close)

        self.df["atr"] = self.df.atr.rolling(window=30).mean()

        self.df["close_smooth"] = savgol_filter(self.df.close, 11, 10)

        # Find peaks and troughs
        atr = self.df.atr.iloc[-1]
        self.peaks_idx, _ = find_peaks(
            self.df.close_smooth, distance=10, width=1, prominence=0.2 * atr
        )
        self.troughs_idx, _ = find_peaks(
            -1 * self.df.close_smooth, distance=10, width=1, prominence=0.2 * atr
        )

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

    def check_last(self, entry_candle, entry_index, entry_candle_size):
        prev_index = entry_index - 1

        prev_candle = self.df.iloc[prev_index]

        prev_candle_size = abs(prev_candle["open"] - prev_candle["close"])

        if entry_candle["candle"] == "G":
            #       If last candle Red then entry candle must close above last candle open

            if (
                prev_candle["candle"] == "R"
                and entry_candle["close"] >= prev_candle["open"]
                and prev_candle_size >= 0.5 * entry_candle_size
            ):
                return True

            else:
                return False

        elif entry_candle["candle"] == "R":
            #       If last candle Red then entry candle must close below last candle open
            if (
                prev_candle["candle"] == "G"
                and entry_candle["close"] <= prev_candle["open"]
                and prev_candle_size >= 0.5 * entry_candle_size
            ):
                return True

            else:
                return False

        return False

    def check_prev_candle(self, entry_candle):
        entry_index = self.df[self.df["date"] == entry_candle["date"]].index[0]
        entry_candle_size = abs(entry_candle["open"] - entry_candle["close"])

        #     For 2 candle entry
        if self.check_last(entry_candle, entry_index, entry_candle_size) == True:
            return True

        else:
            # self.df.loc[length, 'Two Candle'] = False
            if entry_candle["candle"] == "G":
                for i in range(entry_index - 1, max(-1, entry_index - 11), -1):
                    current_candle = self.df.iloc[i]
                    current_candle_size = abs(
                        current_candle["open"] - current_candle["close"]
                    )

                    current_candle_size_percentage = (
                        current_candle_size / current_candle["open"]
                    ) * 100

                    if (
                        current_candle["candle"] == "R"
                        and current_candle_size >= 0.5 * entry_candle_size
                        and entry_candle["close"] >= current_candle["open"]
                        and current_candle_size_percentage <= 0.12
                    ):
                        # Calculate the overlap range between the two candles

                        overlap_size = min(
                            current_candle["open"], entry_candle["close"]
                        ) - max(current_candle["close"], entry_candle["open"])

                        if overlap_size > 0:
                            overlap_percentage = (
                                overlap_size / current_candle_size
                            ) * 100

                            if overlap_percentage >= 30:
                                return True

                    elif (
                        current_candle["candle"] == "G"
                        and (current_candle_size_percentage > 0.04 or
                            ((abs(current_candle['open'] - entry_candle["open"]) / entry_candle["open"]) * 100) > 0.05 )
                    ):
                        return False
                    
                    elif (
                         current_candle["candle"] == "R"
                        and (((abs(current_candle['close'] - entry_candle["open"]) / entry_candle["open"]) * 100) > 0.05 )
                    ):
                        return False

            elif entry_candle["candle"] == "R":
                for i in range(entry_index - 1, max(-1, entry_index - 11), -1):
                    current_candle = self.df.iloc[i]
                    current_candle_size = abs(
                        current_candle["open"] - current_candle["close"]
                    )

                    current_candle_size_percentage = (
                        current_candle_size / current_candle["open"]
                    ) * 100

                    if (
                        current_candle["candle"] == "G"
                        and current_candle_size >= 0.5 * entry_candle_size
                        and entry_candle["close"] <= current_candle["open"]
                        and current_candle_size_percentage <= 0.12
                    ):
                        # Calculate the overlap range between the two candles

                        overlap_size = min(
                            current_candle["close"], entry_candle["open"]
                        ) - max(current_candle["open"], entry_candle["close"])

                        if overlap_size > 0:
                            overlap_percentage = (
                                overlap_size / current_candle_size
                            ) * 100

                            # 30 % overlap is decided between entry and big opposite candle
                            if overlap_percentage >= 30:
                                return True

                    elif (
                        current_candle["candle"] == "R"
                        and (current_candle_size_percentage > 0.04 or
                            (((current_candle['open'] - entry_candle["open"]) / entry_candle["open"]) * 100) > 0.05 )
                    ):
                        return False
                    

                    elif (
                         current_candle["candle"] == "G"
                        and (((abs(current_candle['close'] - entry_candle["open"]) / entry_candle["open"]) * 100) > 0.05 )
                    ):
                        return False
             

        return False

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

    def check_rsi(self, df):
        """To check RSI and EMAs"""

        #         ONLY TRADE WHEN 20 EMA IN FAVOUR

        if (
            df["candle"] == "G"
            and df["RSI"] < 70
            and df["close"] > df["EMA_20"]
            and df["EMA_20"] > df["EMA_200"]
            and df['Angle'] > 10
        ):
            return 1

        elif (
            df["candle"] == "R"
            and df["RSI"] > 30
            and df["close"] < df["EMA_20"]
            and df["EMA_20"] < df["EMA_200"]
            and df['Angle'] < -10
        ):
            return 1

        else:
            return 0

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

    def check_ema(self, x):
        if x["candle"] == "G":
            if (x["low"] < x["EMA_20"] and x["close"] >= x["EMA_20"]) or (
                x["low"] < x["EMA_15"] and x["close"] >= x["EMA_15"]
            ):
                return 1

            else:
                return 0

        elif x["candle"] == "R":
            if (x["high"] > x["EMA_20"] and x["close"] <= x["EMA_20"]) or (
                x["high"] > x["EMA_15"] and x["close"] <= x["EMA_15"]
            ):
                return 1

            else:
                return 0

        else:
            return 0

    #   Apply all the conditions on current candle

    def check_conditions(self):
        length = len(self.df) - 1

        #         Checking all entry conditions

        self.df.loc[length, "pos"] = self.check_ema(self.df.iloc[-1])

        self.df.loc[length, "candle_size"] = self.check_body(self.df.iloc[-1])

        self.df.loc[length, "prev_candle"] = self.check_prev_candle(self.df.iloc[-1])

        self.df.loc[length, "trade"] = self.check_trade(self.df.iloc[-1])

        self.check_tradable(self.df.iloc[-1])

        self.chart = self.df.loc[length]["open"] / 100 * 0.04

        if (
            (self.df.loc[length, "pos"] == 1)
            and (self.df.loc[length, "candle_size"] == 1)
            and (self.df.loc[length, "prev_candle"] == True)
            and (self.df.loc[length, "tradable"] == 0)
            and (self.check_rsi(self.df.iloc[-1]) == 1)
        ):
            #             print('Entry candle')
            #             Set SL for ever entry
            self.df.loc[length, "sl"] = self.set_sl(self.df.iloc[-1])

            self.result_len = len(self.result)

            self.result.loc[self.result_len, "ENTRY DATE"] = self.df.loc[length, "date"]
            self.result.loc[self.result_len, "ENTRY"] = self.df.loc[length, "close"]
            self.result.loc[self.result_len, "TRADE"] = self.df.loc[length, "trade"]
            self.result.loc[self.result_len, "S/L"] = self.df.loc[length, "sl"]

            self.calculations()

    def pip_calc(self, close, sl):
        #         Calculate pips between Entry & SL

        if str(close).index(".") >= 2:  # JPY pair
            multiplier = 0.01

        else:
            multiplier = 0.0001

        pips = round(abs(sl - close) / multiplier)
        return int(pips)

    def result_pip_calc(self, close, value):
        #         Calculate pip value from currency price

        if str(close).index(".") >= 2:  # JPY pair
            multiplier = 100

        else:
            multiplier = 10000

        pip = value * multiplier

        print("PIP: ", pip)

        return float(pip)

    def calc_quantity(self, pips):
        #         To find the number of lots to trade

        lots = [
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
            0.7,
            0.8,
            0.9,
            1,
            1.1,
            1.2,
            1.3,
            1.4,
            1.5,
            1.6,
            1.7,
            1.8,
            1.9,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
        ]

        #       Risk per trade 2%  of account
        self.account = self.account_info.equity

        rpt = int(self.account * 0.02)


        quantity = []

        for i in lots:
            if (i * pips * self.one_pip_value) <= rpt:
                quantity.append(i)

        if quantity:
            return max(quantity)

        else:
            return 0

    def calc_target(self):
        self.target = 0
        self.breakeven = 0

        if (self.result.loc[self.result_len, "TRADE"]) == "B":
            one_is_two_point_five = self.result.loc[self.result_len, "ENTRY"] + 2.2 * (
                self.result.loc[self.result_len, "ENTRY"]
                - self.result.loc[self.result_len, "S/L"]
            )

            one_is_point_five = self.result.loc[self.result_len, "ENTRY"] + 1.5 * (
                self.result.loc[self.result_len, "ENTRY"]
                - self.result.loc[self.result_len, "S/L"]
            )

            one_is_one = self.result.loc[self.result_len, "ENTRY"] + (
                self.result.loc[self.result_len, "ENTRY"]
                - self.result.loc[self.result_len, "S/L"]
            )

            self.buy_on = True

            for i in range(-2, -11, -1):
                # breakeven 1 - 1.5

                if (
                    one_is_one
                    <= self.df.close.iloc[self.troughs_idx[i]]
                    <= one_is_point_five
                    and self.breakeven < self.df.close.iloc[self.troughs_idx[i]]
                ):
                    self.breakeven = self.df.close.iloc[self.troughs_idx[i]]
          

                elif (
                    one_is_one
                    <= self.df.close.iloc[self.peaks_idx[i]]
                    <= one_is_point_five
                    and self.breakeven < self.df.close.iloc[self.troughs_idx[i]]
                ):
                    self.breakeven = self.df.close.iloc[self.peaks_idx[i]]
                    

                # For trg 1.5 to 2.5
                elif (
                    one_is_point_five
                    <= self.df.close.iloc[self.peaks_idx[i]]
                    <= one_is_two_point_five
                    and self.target < self.df.close.iloc[self.peaks_idx[i]]
                ):
                    self.target = self.df.close.iloc[self.peaks_idx[i]]


                elif (
                    one_is_point_five
                    <= self.df.close.iloc[self.troughs_idx[i]]
                    <= one_is_two_point_five
                    and self.target < self.df.close.iloc[self.peaks_idx[i]]
                ):
                    self.target = self.df.close.iloc[self.troughs_idx[i]]


            if self.target == 0:
                # If no Pivots then TRG 1:2
                self.target = self.result.loc[self.result_len, "ENTRY"] + 2 * (
                    self.result.loc[self.result_len, "ENTRY"]
                    - self.result.loc[self.result_len, "S/L"]
                )

            if self.breakeven == 0:
                # If no Pivots Breakeven = 1:1
                self.breakeven = self.result.loc[self.result_len, "ENTRY"] + (
                    self.result.loc[self.result_len, "ENTRY"]
                    - self.result.loc[self.result_len, "S/L"]
                )

        elif self.result.loc[self.result_len, "TRADE"] == "S":
            one_is_two_point_five = self.result.loc[self.result_len, "ENTRY"] - 2.2 * (
                self.result.loc[self.result_len, "S/L"]
                - self.result.loc[self.result_len, "ENTRY"]
            )

            one_is_point_five = self.result.loc[self.result_len, "ENTRY"] - 1.5 * (
                self.result.loc[self.result_len, "S/L"]
                - self.result.loc[self.result_len, "ENTRY"]
            )

            one_is_one = self.result.loc[self.result_len, "ENTRY"] - (
                self.result.loc[self.result_len, "S/L"]
                - self.result.loc[self.result_len, "ENTRY"]
            )

            self.sell_on = True

            for i in range(-2, -11, -1):
                # breakeven 1 - 1.5

                if (
                    one_is_point_five
                    <= self.df.close.iloc[self.troughs_idx[i]]
                    <= one_is_one
                    and self.breakeven > self.df.close.iloc[self.troughs_idx[i]]
                ):
                    self.breakeven = self.df.close.iloc[self.troughs_idx[i]]
                    

                elif (
                    one_is_point_five
                    <= self.df.close.iloc[self.peaks_idx[i]]
                    <= one_is_one
                    and self.breakeven > self.df.close.iloc[self.troughs_idx[i]]
                ):
                    self.breakeven = self.df.close.iloc[self.peaks_idx[i]]

                # For trg 1.5 to 2.5
                elif (
                    one_is_two_point_five
                    <= self.df.close.iloc[self.peaks_idx[i]]
                    <= one_is_one
                    and self.target > self.df.close.iloc[self.peaks_idx[i]]
                ):
                    self.target = self.df.close.iloc[self.peaks_idx[i]]


                elif (
                    one_is_two_point_five
                    <= self.df.close.iloc[self.troughs_idx[i]]
                    <= one_is_one
                    and self.target > self.df.close.iloc[self.peaks_idx[i]]
                ):
                    self.target = self.df.close.iloc[self.troughs_idx[i]]


            if self.target == 0:
                # If no Pivots then TRG 1:2
                self.target = self.result.loc[self.result_len, "ENTRY"] - 2 * (
                    self.result.loc[self.result_len, "S/L"]
                    - self.result.loc[self.result_len, "ENTRY"]
                )

            if self.breakeven == 0:
                # If no Pivots Breakeven = 1:1
                self.breakeven = self.result.loc[self.result_len, "ENTRY"] - (
                    self.result.loc[self.result_len, "S/L"]
                    - self.result.loc[self.result_len, "ENTRY"]
                )

        self.result.loc[self.result_len, "SET_TRG"] = self.target

        self.result.loc[self.result_len, "SET_BRK"] = self.breakeven

    def place_trade(self):

        # Place trade in MT5

        try:
        
            self.magic = random.randint(10000, 999999)

            if self.result.loc[self.result_len, "TRADE"] == 'B':

                # Buy
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.pair,
                    "volume": self.result.loc[self.result_len, "QUANTITY"], 
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": mt5.symbol_info_tick(self.pair).ask,
                    "sl": self.result.loc[self.result_len, "S/L"], 
                    "tp": self.result.loc[self.result_len, "SET_TRG"], 
                    "deviation": 20, 
                    "magic": self.magic, 
                    "comment": "python script buy",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_FOK,  # Change the filling mode here
                }

            elif self.result.loc[self.result_len, "TRADE"] == 'S':
                
                # Sell
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.pair,
                    "volume": self.result.loc[self.result_len, "QUANTITY"], 
                    "type": mt5.ORDER_TYPE_SELL,
                    "price": mt5.symbol_info_tick(self.pair).ask,
                    "sl": self.result.loc[self.result_len, "S/L"], 
                    "tp": self.result.loc[self.result_len, "SET_TRG"], 
                    "deviation": 20, 
                    "magic": self.magic, 
                    "comment": "python script sell",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_FOK,  # Change the filling mode here
                }

            self.order = mt5.order_send(request)

        except Exception as e:
            print(f"An error in sending order: {e}")


    def calculations(self):
        self.sl = self.result.loc[self.result_len, "S/L"]
        self.trail_sl = False

        self.base_candle_index = self.df.iloc[-1]["date"]

        self.doji_count = 0

        pips = self.pip_calc(
            self.result.loc[self.result_len, "ENTRY"],
            self.result.loc[self.result_len, "S/L"],
        )

        #         print('Pips: ', pips)
        self.quantity = self.calc_quantity(pips)

        self.result.loc[self.result_len, "QUANTITY"] = self.quantity

        self.calc_target()

        # Call MT5 with order for Buying in quantity as lot size, and SL TRG

        self.place_trade()


    def update_order(self):

        request = {
        'action' : mt5.TRADE_ACTION_SLTP,  # Type of trade operation
        'position' : self.order.order, # Ticket of the position
        'symbol' : self.pair,  # Symbol
        'sl' : self.sl,  # Stop Loss of the position
        'tp' : self.result.loc[self.result_len, "SET_TRG"],  # Take Profit of the position
        'magic' : self.magic  # MagicNumber of the position
        }

        # Send the request
        try:
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print("OrderSend error %d" % result.retcode)


        except Exception as e:
            print(f"MetaTrader5Error: {e}")

    def manage_buy(self):
        
        # Manage Buy Trade

        length = len(self.df) - 1

        current_candle = self.df.loc[length]["candle"]

        base_index = self.df[self.df["date"] == self.base_candle_index].index[0]

        if ((length > (base_index + 12)) and self.trail_sl == False and
            self.df.loc[length]["high"] < self.breakeven):
            # print(self.df.iloc[base_index])
            self.result.loc[self.result_len, "EXIT"] = self.df.loc[length]["close"]
            self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length]["date"]
            self.result.loc[self.result_len, "REASON"] = "NO MOVE"
            self.buy_on = False

            # Closing the order
            mt5.Close(self.pair,ticket=self.order.order)
            


        if current_candle == "G" and self.buy_on == True:
            # TRG and Trail SL condition

            if self.df.loc[length]["high"] >= self.target:
                # TRG
                
                self.result.loc[self.result_len, "EXIT"] = self.target
                self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length][
                    "date"
                ]
                self.result.loc[self.result_len, "REASON"] = "TRG"
                self.buy_on = False

            # For Breakeven
            elif (
                self.df.loc[length]["high"] >= self.breakeven and self.trail_sl == False
            ):
                self.sl = self.df.loc[length]["EMA_8"]
                self.trail_sl = True

                # Calling to update the order
                self.update_order()

            # For trailing after Big Green Candle in breakeven

            elif (
                self.trail_sl == True
                and (
                    (self.df.loc[length]["close"] - self.df.loc[length]["open"])
                    / self.df.loc[length]["close"]
                )
                * 100
                >= 0.04
            ):
                self.sl = self.df.loc[length]["EMA_8"]

                # Calling to update the order
                self.update_order()

            # For Gap Down exit
            elif self.sl >= self.df.loc[length]["open"]:
                # print('In SL Condition')
                #                 print(self.df.loc[length,'date'])
                self.result.loc[self.result_len, "EXIT"] = self.df.loc[length]["open"]
                self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length][
                    "date"
                ]
                if self.trail_sl:
                    self.trail_sl = False
                    self.result.loc[self.result_len, "REASON"] = "TRAIL_SL"

                else:
                    self.result.loc[self.result_len, "REASON"] = "SL"
                
                self.buy_on = False

            # Green candle low hits SL
            elif self.sl >= self.df.loc[length]["low"]:
                self.result.loc[self.result_len, "EXIT"] = self.sl
                self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length][
                    "date"
                ]
                if self.trail_sl:
                    self.result.loc[self.result_len, "REASON"] = "TRAIL_SL"
                    self.trail_sl = False

                else:
                    self.result.loc[self.result_len, "REASON"] = "SL"

                self.buy_on = False

        elif current_candle == "R" and self.buy_on == True:
            # SL condition
            # print('In red candle')

            # For Gap down
            if self.sl >= self.df.loc[length]["open"]:

                self.result.loc[self.result_len, "EXIT"] = self.df.loc[length]["open"]
                self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length][
                    "date"
                ]

                if self.trail_sl:
                    self.result.loc[self.result_len, "REASON"] = "TRAIL_SL"
                    self.trail_sl = False
                    self.buy_on = False

                else:
                    self.result.loc[self.result_len, "REASON"] = "SL"

                self.buy_on = False

            # Closing below 20 EMA
            elif (self.df.loc[length]["close"] < self.df.loc[length]["EMA_20"] and
                length > (base_index + 5)):
                self.result.loc[self.result_len, "EXIT"] = self.df.loc[length]["close"]
                self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length][
                    "date"
                ]
                self.result.loc[self.result_len, "REASON"] = "EMA_20"
                
                # Closing the order
                mt5.Close(self.pair,ticket=self.order.order)

                self.trail_sl = False
                self.sell_on = False

            # For Breakeven
            elif (
                self.df.loc[length]["high"] >= self.breakeven and self.trail_sl == False
            ):
                self.sl = self.df.loc[length]["EMA_8"]
                self.trail_sl = True

                self.update_order()

            # High of Red touches TRG

            elif self.df.loc[length]["high"] > self.target:
                self.result.loc[self.result_len, "EXIT"] = self.target
                self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length][
                    "date"
                ]
                self.result.loc[self.result_len, "REASON"] = "TRG"
                self.buy_on = False
                self.trail_sl = False

            # For SL
            elif self.sl >= self.df.loc[length]["low"]:
                self.result.loc[self.result_len, "EXIT"] = self.sl
                self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length][
                    "date"
                ]

                if self.trail_sl:
                    self.result.loc[self.result_len, "REASON"] = "TRAIL_SL"
                    self.trail_sl = False

                else:
                    self.result.loc[self.result_len, "REASON"] = "SL"
                self.buy_on = False

        if self.buy_on == False:
            self.result.loc[self.result_len, "P/L"] = (
                self.result.loc[self.result_len]["EXIT"]
                - self.result.loc[self.result_len]["ENTRY"]
            )

            self.result.loc[self.result_len, "REAL P/L"] = (
                self.quantity
                * self.one_pip_value
                * self.result_pip_calc(
                    self.result.loc[self.result_len]["ENTRY"],
                    self.result.loc[self.result_len, "P/L"],
                )
            )

    def manage_sell(self):
        # print('In Sell')

        length = len(self.df) - 1

        current_candle = self.df.loc[length]["candle"]

        base_index = self.df[self.df["date"] == self.base_candle_index].index[0]

        # print('Base Index: ',base_index)

        if ((length > (base_index + 12)) and (self.trail_sl == False) and
            self.df.loc[length]["low"] > self.breakeven):

            self.result.loc[self.result_len, "EXIT"] = self.df.loc[length]["close"]
            self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length]["date"]
            self.result.loc[self.result_len, "REASON"] = "NO MOVE"
            self.sell_on = False

            # Closing the order
            mt5.Close(self.pair,ticket=self.order.order)

        if current_candle == "R":
            # TRG  and Trail SL condition

            if self.df.loc[length]["low"] <= self.target:
                # TRG

                self.result.loc[self.result_len, "EXIT"] = self.target
                self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length][
                    "date"
                ]
                self.result.loc[self.result_len, "REASON"] = "TRG"
                self.sell_on = False
                self.trail_sl = False

            # For Breakeven
            elif self.df.loc[length]["low"] <= self.breakeven:
                self.sl = self.df.loc[length]["EMA_8"]
                self.trail_sl = True

                # Update the order
                self.update_order()

            # For trailing after Big Red Candle in breakeven

            elif (
                self.trail_sl == True
                and (
                    (self.df.loc[length]["open"] - self.df.loc[length]["close"])
                    / self.df.loc[length]["close"]
                )
                * 100
                >= 0.04
            ):
                self.sl = self.df.loc[length]["EMA_8"]

                # Update the order
                self.update_order()

            #               For Gap Up exit
            elif self.sl <= self.df.loc[length]["open"]:
                self.result.loc[self.result_len, "EXIT"] = self.df.loc[length]["open"]
                self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length][
                    "date"
                ]

                if self.trail_sl:
                    self.result.loc[self.result_len, "REASON"] = "TRAIL_SL"
                    self.trail_sl = False

                else:
                    self.result.loc[self.result_len, "REASON"] == "SL"

                self.sell_on = False

            # Red candle High hits SL
            elif self.sl <= self.df.loc[length]["high"]:
                self.result.loc[self.result_len, "EXIT"] = self.sl
                self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length][
                    "date"
                ]

                if self.trail_sl:
                    self.result.loc[self.result_len, "REASON"] = "TRAIL_SL"
                    self.trail_sl = False

                else:
                    self.result.loc[self.result_len, "REASON"] = "SL"

                self.sell_on = False

        elif current_candle == "G":
            # SL condition

            #                 For Gap UP
            if self.sl <= self.df.loc[length]["open"]:
                self.result.loc[self.result_len, "EXIT"] = self.df.loc[length]["open"]
                self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length][
                    "date"
                ]

                if self.trail_sl:
                    self.result.loc[self.result_len, "REASON"] = "TRAIL_SL"
                    self.trail_sl = False

                else:
                    self.result.loc[self.result_len, "REASON"] = "SL"

                self.sell_on = False


            elif (self.df.loc[length]["close"] > self.df.loc[length]["EMA_20"] and
                length > (base_index + 5)):
                self.result.loc[self.result_len, "EXIT"] = self.df.loc[length]["close"]
                self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length][
                    "date"
                ]
                self.result.loc[self.result_len, "REASON"] = "EMA_20"
                self.trail_sl = False
                self.sell_on = False

                # Closing the order
                mt5.Close(self.pair,ticket=self.order.order)


            # Green candle low touches trg
            elif self.target >= self.df.loc[length]["low"]:
                self.result.loc[self.result_len, "EXIT"] = self.target
                self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length][
                    "date"
                ]
                self.result.loc[self.result_len, "REASON"] = "TRG"
                self.sell_on = False
                self.trail_sl = False

            #                 For SL
            elif self.sl <= self.df.loc[length]["high"]:
                self.result.loc[self.result_len, "EXIT"] = self.sl
                self.result.loc[self.result_len, "EXIT DATE"] = self.df.loc[length][
                    "date"
                ]
                if self.trail_sl:
                    self.result.loc[self.result_len, "REASON"] = "TRAIL_SL"
                    self.trail_sl = False

                else:
                    self.result.loc[self.result_len, "REASON"] = "SL"

                self.sell_on = False

        if self.sell_on == False:
            self.result.loc[self.result_len, "P/L"] = (
                self.result.loc[self.result_len]["ENTRY"]
                - self.result.loc[self.result_len]["EXIT"]
            )

            self.result.loc[self.result_len, "REAL P/L"] = (
                self.quantity
                * self.one_pip_value
                * self.result_pip_calc(
                    self.result.loc[self.result_len]["ENTRY"],
                    self.result.loc[self.result_len, "P/L"],
                )
            )

    def Caller(self):
        # Initialize an empty DataFrame to store the past data that gets dropped
        try:
            
            while True:

                # Current candle time
                time = self.df.iloc[-1]['date']

                if self.sell_on == False and self.buy_on == False:
                    # Add 15 minutes to the time
                    new_time = (time + timedelta(minutes=15))

                else:
                    # Subtract 20 seconds from the time
                    new_time = (time + timedelta(minutes=15) - timedelta(seconds=20))

                # Calculate the time difference in seconds
                current_datetime = datetime.utcnow()
                target_datetime = datetime(new_time.year, new_time.month, new_time.day, new_time.hour, new_time.minute, new_time.second)
                time_difference = (target_datetime - current_datetime).total_seconds()

                if time_difference > 10:
                    # Calculate the wake-up time
                    wake_up_time = current_datetime + timedelta(seconds=time_difference)
                    print(f"Will wake up at: {wake_up_time}")

                    time.sleep(time_difference)
                # ==================================================================
                
                new_candle = pd.DataFrame( mt5.copy_rates_from('EURUSD', mt5.TIMEFRAME_M15, datetime.now(), 1))

                new_candle['date'] = pd.to_datetime(new_candle['time'], unit='s')

                new_candle = new_candle.drop(["spread", "real_volume", "tick_volume", "time"], axis="columns")

                print('Candle: ', new_candle)
                    # Save the dropped row in past_df
                self.df = self.df.append(new_candle, ignore_index=True)

                # self.past_df = pd.concat([self.past_df, self.df.iloc[0]], ignore_index=True)
                self.df = self.df.iloc[1:].reset_index(drop=True)

                # Calculate indicators for the current state of df
                self.calculate_indicators()

                if self.buy_on == True:
                    self.manage_buy()

                elif self.sell_on == True:
                    self.manage_sell()

                else:
                # Apply all entry conditions
                    self.check_conditions()

        except Exception as e:
            print(f"An error occurred in Caller: {e}")
