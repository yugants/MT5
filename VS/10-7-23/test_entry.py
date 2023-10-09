import talib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
# import datetime
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
            instrument[0], mt5.TIMEFRAME_M15, datetime.now(), instrument[2]
        )
        nf = pd.DataFrame(rate)

        nf["date"] = pd.to_datetime(nf["time"], unit="s")

        nf.set_index(np.arange(len(nf)), inplace=True)
        nf = nf.drop(["spread", "real_volume", "tick_volume", "time"], axis="columns")

        # self.df = nf.iloc[:500]  # First half
        # self.df2 = nf.iloc[500:]  # Second half
        self.df = nf.copy()

        #         self.account = 10000

        self.prev_high, self.prev_low, self.current_high, self.current_low = (
            float(),
            float(),
            float(),
            float(),
        )

        #         For EURUSD
        self.one_pip_value = instrument[1]
        self.trend_date = None
        self.prev_trend = None

        self.bull_no_trend = False
        self.bear_no_trend = False

        self.no_trend_up = False
        self.no_trend_down = False

        #     For Doji Condition

        self.doji_counter = 0
        self.doji_flag = False

        #     For counting 20 candles after climax

        self.buy_flag = True
        self.sell_flag = True
        self.green_count = 0
        self.red_count = 0

        # self.df["tradable"] = 0
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

    def check_body(self, df):
        #     Calculate 0.7 % of entry price
        #     fOR 1H FOREX
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
            # self.df.loc[length, 'Two Candle'] = True
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
                        and entry_candle['close'] >= current_candle['open']
                        and current_candle_size_percentage <= 0.12
                    ):
                        # Calculate the overlap range between the two candles

                        # self.df.loc[length, 'Prev_Found'] = True
                        overlap_size = min(
                            current_candle["open"], entry_candle["close"]
                        ) - max(current_candle["close"], entry_candle["open"])

                        self.df.loc[entry_index, "overlap"] = overlap_size

                        if overlap_size > 0:
                            overlap_percentage = (
                                overlap_size / current_candle_size
                            ) * 100

                            self.df.loc[entry_index, "overlap_per"] = overlap_percentage

                            if (
                                overlap_percentage >= 30
                            ):
                                return True
                                # for j in range(i + 1, entry_index):
                                #     intermediate_candle = self.df.iloc[j]

                                #     intermediate_candle_size = (
                                #         (abs(
                                #             intermediate_candle["open"]
                                #             - intermediate_candle["close"]
                                #         )
                                #         / intermediate_candle["close"])
                                #         * 100
                                #     )
                                #     #                          If intermediate candle goes below 0.02% of red candle no trade
                                #     if (
                                #         max(
                                #             intermediate_candle["open"],
                                #             intermediate_candle["close"],
                                #         )
                                #         < current_candle["open"]
                                #         and intermediate_candle_size < 0.04
                                #         and j < entry_index - 1
                                #         and (
                                #             current_candle["close"]
                                #             - current_candle["close"] / 100 * 0.02
                                #         )
                                #         < intermediate_candle["close"]
                                #     ):
                                #         continue

                                #     elif j == entry_index - 1:
                                #         return True

                                #     else:
                                #         self.df.loc[length, 'Middle'] = intermediate_candle['date']
                                #         return False
                                # break

                    elif (
                        current_candle["candle"] == "G"
                        and current_candle_size_percentage > 0.04
                    ):
                        self.df.loc[entry_index, "green_ind"] = current_candle["date"]
                        return False

            elif entry_candle["candle"] == "R":
                #         print('Testing R candle')
                for i in range(entry_index - 1, max(-1, entry_index - 11), -1):
                    current_candle = self.df.iloc[i]
                    current_candle_size = abs(
                        current_candle["open"] - current_candle["close"]
                    )

                    current_candle_size_percentage = (
                        current_candle_size / current_candle["open"]
                    ) * 100

                    # self.df.loc[entry_index, 'size'] = current_candle_size_percentage
                    if (
                        current_candle["candle"] == "G"
                        and current_candle_size >= 0.5 * entry_candle_size and
                        entry_candle['close'] <= current_candle['open'] and 
                        current_candle_size_percentage <= 0.12
                    ):
                        # Calculate the overlap range between the two candles

                        self.df.loc[
                            entry_index, "green_size"
                        ] = current_candle_size_percentage

                        # self.df.loc[length, 'Prev_Found'] = True
                        overlap_size = min(
                            current_candle["close"], entry_candle["open"]
                        ) - max(current_candle["open"], entry_candle["close"])

                        # if entry_candle['EMA_20'] == 0.581831336:
                        # print("Candle: ", entry_candle["date"])
                        # print("Overlap: ", overlap_size)

                        if overlap_size > 0:
                            overlap_percentage = (
                                overlap_size / current_candle_size
                            ) * 100

                            self.df.loc[entry_index, "overlap_per"] = overlap_percentage

                            self.df.loc[entry_index, "this_candle"] = current_candle['date']

                            #                     30 % overlap is decided between entry and big opposite candle
                            if (
                                overlap_percentage >= 30
                            ):
                                return True
                                #                 print('R in IF')
                                # for j in range(i + 1, entry_index):
                                #     intermediate_candle = self.df.iloc[j]

                                #     intermediate_candle_size = (
                                #         (abs(
                                #             intermediate_candle["open"]
                                #             - intermediate_candle["close"]
                                #         )
                                #         / intermediate_candle["close"])
                                #         * 100
                                #     )

                                #     if (
                                #         min(
                                #             intermediate_candle["open"],
                                #             intermediate_candle["close"],
                                #         )
                                #         > current_candle["open"]
                                #         and j < entry_index - 1
                                #         and intermediate_candle_size < 0.04
                                #         and (
                                #             current_candle["close"]
                                #             + current_candle["close"] / 100 * 0.02
                                #         )
                                #         > intermediate_candle["close"]
                                #     ):
                                #         continue

                                #     elif j == entry_index - 1:
                                #         return True

                                #     else:
                                #         self.df.loc[length, 'Middle'] = intermediate_candle['date']
                                #         return False

                                # break

                    elif (
                        current_candle["candle"] == "R"
                        and current_candle_size_percentage > 0.04
                    ):
                        self.df.loc[entry_index, "red_ind"] = current_candle["date"]

                        return False

        return False

    def candle(self, df):
        """Return candle colour"""

        if df["close"] - df["open"] > 0:
            return "G"

        else:
            return "R"

    def check_ema(self, x):
        if x["candle"] == "G":
            if x["low"] < x["EMA_20"] and x["close"] >= x["EMA_20"]:
                return 1

            else:
                return 0

        elif x["candle"] == "R":
            if x["high"] > x["EMA_20"] and x["close"] <= x["EMA_20"]:
                return 1

            else:
                return 0

        else:
            return 0

    def check_conditions(self):
        # length = len(self.df) - 1

        #         Checking all entry conditions

        # self.df.loc[length, "pos"] = self.check_inside_kt(self.df.iloc[-1])

        self.df["EMA_20"] = talib.EMA(self.df["close"], timeperiod=20)

        self.df["candle"] = self.df.apply(self.candle, axis=1)

        self.df["check_ema"] = self.df.apply(self.check_ema, axis=1)

        self.df["candle_size"] = self.df.apply(self.check_body, axis=1)

        self.df["prev_candle"] = self.df.apply(self.check_prev_candle, axis=1)

        # self.df[ "prev_candle"] = self.df.apply(self.check_last, axis=1)

        self.df.to_excel("test.xlsx")


audchf = LiveTrade(["AUDCHF", 10.92729, 6000])
audchf.check_conditions()
