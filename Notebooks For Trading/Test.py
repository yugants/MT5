import talib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import datetime
import MetaTrader5 as mt5


class LiveTrade:
    
    def __init__(self):
        
#         self.df = pd.DataFrame(yf.download(tickers=instrument, start = '2022-10-01', end = '2023-06-01', interval='1h'))
        if not mt5.initialize(login=114781990, server="Exness-MT5Trial6",password="Mypassword$1234"):
            print("initialize() failed, error code =",mt5.last_error())
            quit()
        
        login = 114781990
        password = 'Mypassword$1234'
        server = 'Exness-MT5Trial6'

        print('hello')

        mt5.login(login, password, server)
        
        rate = mt5.copy_rates_from('GBPUSDm', mt5.TIMEFRAME_M15, datetime.datetime.now(), 24000)
        nf = pd.DataFrame(rate)
#         print('getting data')

        nf['date']=pd.to_datetime(nf['time'], unit='s')

        nf.set_index(np.arange(len(nf)), inplace = True)
        nf = nf.drop(['spread', 'real_volume', 'tick_volume', 'time'], axis='columns')


        self.df = nf.iloc[:500]  # First half
        self.df2 = nf.iloc[500:]  # Second half
        self.df.loc[:, 'squeeze_on'] = False
        
#         self.account = 10000
        
        self.prev_high, self.prev_low, self.current_high, self.current_low = float(), float(), float(), float()
        
#         For EURUSD
        self.one_pip_value = 10
        self.trend_date  = None
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
        
        self.df['tradable'] = 0
#         self.df.at[length, 'tradable'] = 0
        
        self.result = pd.DataFrame(columns=['ENTRY DATE', 'ENTRY', 'QUANTITY', 'TRADE', 'EXIT', 'EXIT DATE', 'P/L', 'REAL P/L', 'S/L' ])
        
        self.trade_on = None
        
        self.buy_on = False
        self.sell_on = False
        
#         self.past_trend()
        
    
#     def past_trend(self):
        
# #         print('past data')
#         length = len(self.df)

#         # Calculate max and min high values
#         self.prev_high = self.df.iloc[length - 42 : length - 21]['high'].max()
#         self.prev_low = self.df.iloc[length - 42 : length - 21]['low'].min()

#         self.current_high = self.df.iloc[length - 21 : length]['high'].max()
#         self.current_low = self.df.iloc[length - 21 : length]['low'].min()

#         # Up condition
#         if self.current_high > self.prev_high and self.current_low > self.prev_low:
#             self.df.loc[length - 21 : length, 'trend'] = 'up'
#         # Down condition
#         elif self.current_high < self.prev_high and self.current_low < self.prev_low:
#             self.df.loc[length - 21 : length, 'trend'] = 'down'
#         else:
#             self.df.loc[length - 21 : length, 'trend'] = 'no trend'

#         self.prev_high = self.current_high
#         self.prev_low = self.current_low
#         self.trend_date = self.df['date'].iloc[-1]
#         print('Date in past check: ', self.trend_date)
#         self.prev_trend = self.df['trend'].iloc[-1]
    
    
#     def test_current_trend(self, high, low, l):
        
# #         print('test_current_trend')
        
#         if self.prev_trend == 'up' and self.bull_no_trend is False:
            
#             if low > self.prev_low:
#                 self.df.loc[l, 'trend'] = 'up'
                
#             else:
#                 self.df.loc[l, 'trend'] = 'no trend bull'
#                 self.bull_no_trend = True
        
#         elif self.prev_trend == 'up' and self.bull_no_trend is True:
#             self.df.loc[l, 'trend'] = 'no trend bull 1'
        
#         elif self.prev_trend == 'down' and self.bear_no_trend is False:
            
#             if high < self.prev_high:
#                 self.df.loc[l, 'trend'] = 'down'
            
#             else:
#                 self.df.loc[l, 'trend'] = 'no trend bear'
#                 self.bear_no_trend = True
        
#         elif self.prev_trend == 'down' and self.bear_no_trend is True:
#             self.df.loc[l, 'trend'] = 'no trend bear1'
        
#         elif self.prev_trend == 'no trend' and self.no_trend_up is False and self.no_trend_down is False:
            
#             if high > self.prev_high:
#                 self.df.loc[l, 'trend'] = 'up'
#                 self.no_trend_up = True
            
#             elif low < self.prev_low:
#                 self.df.loc[l, 'trend'] = 'down'
#                 self.no_trend_down = True
            
#             else:
#                 self.df.loc[l, 'trend'] = 'no trend'
        
#         elif self.prev_trend == 'no trend' and self.no_trend_up is True:
            
#             if low > self.prev_low:
#                 self.df.loc[l, 'trend'] = 'up'
            
#             else:
#                 self.df.loc[l, 'trend'] = 'no trend'
#                 self.no_trend_up = False
        
#         elif self.prev_trend == 'no trend' and self.no_trend_down is True:
            
#             if high < self.prev_high:
#                 self.df.loc[l, 'trend'] = 'down'
            
#             else:
#                 self.df.loc[l, 'trend'] = 'no trend'
#                 self.no_trend_down = False

#     def calculate_current_trend(self, position_index, days=21):
#         l = len(self.df) - 1
        
# #         print('calculate current trend')

#         if position_index + days > l:
# #             print('big slot')
# #             print('position_index: ', position_index)
# #             print('Len: ', l)
#             self.test_current_trend(self.df.iloc[l]['high'], self.df.iloc[l]['low'], l)
        
#         elif position_index + days == l:
# #             print('correct slot')
#             current_high = self.df.loc[self.df.index[position_index: l + 1], 'high'].max()
#             current_low = self.df.loc[self.df.index[position_index: l + 1], 'low'].min()
            
#             if current_high > self.prev_high and current_low > self.prev_low:
#                 self.df.loc[l, 'trend'] = 'up'
            
#             elif current_high < self.prev_high and current_low < self.prev_low:
#                 self.df.loc[l, 'trend'] = 'down'
            
#             else:
#                 self.df.loc[l, 'trend'] = 'no trend'

#             self.trend_date = self.df['date'].iloc[-1]
# #             print('changing date: ', self.trend_date)
#             self.prev_high = current_high
#             self.prev_low = current_low
#             self.prev_trend = self.df['trend'].iloc[-1]
#             self.bull_no_trend, self.bear_no_trend, self.no_trend_up, self.no_trend_down = [False] * 4
            
            
            
    
    def candle(self, df):
        '''Return candle colour'''

        if df['close'] - df['open'] > 0:
            return 'G'

        else:
            return 'R'
    
    def get_kc(self, high, low, close, kc_lookback, multiplier, atr_lookback):
        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift()))
        tr3 = pd.DataFrame(abs(low - close.shift()))

        # Calculate True Range as the element-wise maximum of the three components
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.ewm(alpha=1/atr_lookback).mean()

        kc_middle = close.ewm(span=kc_lookback).mean()
        kc_upper = kc_middle + multiplier * atr
        kc_lower = kc_middle - multiplier * atr

        return kc_middle.iloc[-1], kc_upper.iloc[-1], kc_lower.iloc[-1]

    def calculate_indicators(self):
        
#         print('calc_indicator')
        length = len(self.df) - 1

        self.df.loc[length, 'EMA_8'] = talib.EMA(self.df['close'], timeperiod=8).iloc[-1]
        self.df.loc[length, 'EMA_15'] = talib.EMA(self.df['close'], timeperiod=15).iloc[-1]
        self.df.loc[length, 'EMA_200'] = talib.EMA(self.df['close'], timeperiod=200).iloc[-1]
        self.df.loc[length, 'RSI'] = talib.RSI(self.df['close'], timeperiod=21).iloc[-1]

        sma = self.df['close'].rolling(window=20).mean()
        stddev = self.df['close'].rolling(window=20).std()
        lower_band = sma - (2 * stddev)
        upper_band = sma + (2 * stddev)

        self.df.loc[length, 'candle'] = self.candle(self.df.iloc[-1])
        
        kc_middle, kc_upper, kc_lower = self.get_kc(self.df['high'], self.df['low'], self.df['close'], kc_lookback=20, multiplier=1.2, atr_lookback=10)

        if (lower_band.iloc[-1] > kc_lower) and (upper_band.iloc[-1] < kc_upper):
            self.df.loc[length, 'squeeze_on'] = True
        else:
            self.df.loc[length, 'squeeze_on'] = False

        self.df.loc[length, 'EMA_20'], self.df.loc[length, 'upper_keltner'], self.df.loc[length, 'lower_keltner'] = self.get_kc(self.df['high'], self.df['low'], self.df['close'], kc_lookback=20, multiplier=2.25, atr_lookback=10)

    
 
    

    def check_body(self, df):
        #     Calculate 0.7 % of entry price
    #     fOR 1H FOREX
            one_percent = df['open']/100 
            percent = one_percent * 0.06
            hammer_per = one_percent * 0.06


        #     Calculate candle size close-open
            if df['candle'] == 'G':
                candle_size = df['close'] - df['open']
                upper_wick = df['high'] - df['close']
                lower_wick = df['open'] - df['low']

            else:
                candle_size = abs(df['close'] - df['open'])
                upper_wick = df['high'] - df['open']
                lower_wick = df['close'] - df['low']

            upper_wick_per = (upper_wick/one_percent) 
            lower_wick_per = (lower_wick/one_percent) 



        #     check for entry candle size and Max candle size 0.12 %
            if ((candle_size >= percent) and candle_size <= (0.12 * one_percent) and
             (candle_size > upper_wick) and (candle_size > lower_wick) and
            (upper_wick_per < 0.06) and (lower_wick_per < 0.06)):
                
                if df['candle'] == 'G' and df['high'] < df['upper_keltner'] :

                    return 1
                
                elif df['candle'] == 'R' and df['low'] > df['lower_keltner'] :

                    return 1
                
                else:
                    
                    return 0

        #     condition for hammmer
        #     lower wick is atleast 50 % of total size 
        #     Green Hammer 
        # need to add max wick of opposite dir
            elif ( (df['candle'] == 'G') and (df['open'] - df['low']) >= ((df['high'] - df['low']) * 0.5) and
                  (candle_size >= hammer_per) and (candle_size > upper_wick)and
                  candle_size <= (0.12 * one_percent) and ((upper_wick_per < 0.06))  
                 and df['high'] < df['upper_keltner']):

                return 1


    #     For Red Hammer
    # need to add max wick of opposite dir
            elif ( (df['candle'] == 'R') and (df['high'] - df['open']) >= (abs(df['high'] - df['low']) * 0.5) and 
                  (candle_size >= hammer_per) and (candle_size > lower_wick)and candle_size <= (0.12 * one_percent) and 
                  ((lower_wick_per < 0.06)) and df['low'] > df['lower_keltner'] ):

                return 1


            else:
                return 0

        
    
    def check_last(self, entry_candle, entry_index, entry_candle_size):
    
#     entry_index = df[df['date'] == entry_candle['date']].index[0]
    
#     entry_candle_size = abs(entry_candle['open'] - entry_candle['close'])

        prev_index = entry_index - 1 

        prev_candle = self.df.iloc[prev_index]

        prev_candle_size = abs(prev_candle['open'] - prev_candle['close'])

        if entry_candle['candle'] == 'G':

    #       If last candle Red then entry candle must close above last candle open
            if (prev_candle['candle'] == 'R' and entry_candle['close'] >= prev_candle[ 'open'] and
               prev_candle_size >= 0.6 * entry_candle_size):

                return True

            else:
                return False

        elif entry_candle['candle'] == 'R':

    #       If last candle Red then entry candle must close below last candle open
            if (prev_candle['candle'] == 'G' and entry_candle['close'] <= prev_candle[ 'open'] and
               prev_candle_size >= 0.6 * entry_candle_size):

                return True

            else:
                return False

        return False



    def check_prev_candle(self,entry_candle):    

        entry_index = self.df[self.df['date'] == entry_candle['date']].index[0]
        entry_candle_size = abs(entry_candle['open'] - entry_candle['close'])


    #     For 2 candle entry
        if self.check_last(entry_candle, entry_index, entry_candle_size) == True:

            return True

        else:

            if entry_candle['candle'] == 'G':
                for i in range(entry_index - 1, max(-1, entry_index - 11), -1):
                    current_candle = self.df.iloc[i]
                    current_candle_size = abs(current_candle['open'] - current_candle['close'])

                    if current_candle['candle'] == 'R':
                        # Calculate the overlap range between the two candles
                        overlap_percentage = ((min(current_candle['open'], entry_candle['close']) - max(current_candle['close'], entry_candle['open'])) /current_candle_size) * 100


                        if (current_candle['candle'] == 'R' and
                            current_candle['open'] <= entry_candle['close'] and
                            current_candle_size >= 0.5 * entry_candle_size and 
                            current_candle_size <= 1.2 * entry_candle_size and
                            overlap_percentage >= 30 ):

                            for j in range(i + 1, entry_index):
                                intermediate_candle = self.df.iloc[j]
        #                          If intermediate candle goes below 0.02% of red candle no trade
                                if (max(intermediate_candle['open'], intermediate_candle['close']) < current_candle['open'] and
                                    j < entry_index - 1 and (current_candle['close'] - current_candle['close']/100 * 0.02) < intermediate_candle['close']):
                                    continue

                                elif j == entry_index - 1:
                                    return True

                                else:
                                    return False
                            break

            elif entry_candle['candle'] == 'R':
        #         print('Testing R candle')
                for i in range(entry_index - 1, max(-1, entry_index - 11), -1):
                    current_candle = self.df.iloc[i]
                    current_candle_size = abs(current_candle['open'] - current_candle['close'])

                    if current_candle['candle'] == 'G':
                    # Calculate the overlap range between the two candles
                        overlap_percentage = ((min(current_candle['open'], entry_candle['close']) - max(current_candle['close'], entry_candle['open'])) /current_candle_size) * 100

        #                     30 % overlap is decided between entry and big opposite candle
                        if ( current_candle['open'] >= entry_candle['close'] and
                            current_candle_size >= 0.5 * entry_candle_size and 
                            current_candle_size <= 1.2 * entry_candle_size and
                            overlap_percentage >= 30):
            #                 print('R in IF')
                            for j in range(i + 1, entry_index):
                                intermediate_candle = self.df.iloc[j]

                                if (min(intermediate_candle['open'], intermediate_candle['close']) > current_candle['open'] and
                                    j < entry_index - 1 and (current_candle['close'] + current_candle['close']/100 * 0.02) > intermediate_candle['close']):
                                    continue

                                elif j == entry_index - 1:
                                    return True

                                else:
                                    return False

                            break

        return False

    
#   SL Method

    def set_sl(self, df):
        '''Set SL 1% above/below to entry candle'''
            
        candle_size = df['high'] - df['low']

        if df['candle'] == 'G':

            sl = df['low'] - (candle_size/100)

        elif df['candle'] == 'R':

            sl = df['high'] + (candle_size/100)
        
#         print('SL: ', sl)

        return sl
        

        
    
    def check_rsi(self, df):
        '''To check RSI and EMAs'''
        
#         ONLY TRADE WHEN 20 EMA IN FAVOUR

        if (df['candle'] == 'G' and df['RSI'] < 70 and df['close'] > df['EMA_20'] and df['EMA_20'] > df['EMA_200']):
            
                return 1
            
            
        elif (df['candle'] == 'R' and df['RSI'] > 30 and df['close'] < df['EMA_20'] and df['EMA_20'] < df['EMA_200']):
        
                return 1
        
 
        else:
            
            return 0
            
            
# To mark trades as Buy/ Sell

    def check_trade(self, df):
        
        if df['candle'] == 'G':
            
            return 'B'
        
        else:
            
            return 'S'
    
    
#     Check candle for climax condition
    def check_tradable(self, row):
        one_percent = row['open'] / 100
        
        length = len(self.df) -1

        # When green candle goes outside channel
        if (((row['candle'] == 'G' and row['open'] > row['upper_keltner']) or
             (row['candle'] == 'R' and row['close'] > row['upper_keltner'])) and
                self.sell_flag == True and
                (abs(row['close'] - row['upper_keltner']) / one_percent) >= 0.07):
            self.buy_flag = False
            self.green_count = 0
            self.df.at[length, 'tradable'] = 'First G Break'

        # When price remains outside after green breakout
        elif (row['close'] > row['upper_keltner'] and self.sell_flag == True and
              self.buy_flag == False and self.green_count == 0):
            self.df.at[length, 'tradable'] = 'Outside after G Break'

        # Any candle in 20 count closes outside the channel, restart the count
        elif row['close'] > row['upper_keltner'] and self.buy_flag == True and self.green_count > 0:
            self.green_count = 0
            self.buy_flag = False
            self.df.at[length, 'tradable'] = 'Outside after G Break'

        # When the price returns inside the channel after a buy breakout
        elif row['close'] < row['upper_keltner'] and self.buy_flag == False:
            self.buy_flag = True
            self.green_count = 1
            self.df.at[length, 'tradable'] = 'G count 1'

        # Counting 20 candles when green breakout moves inside the channel
        elif 0 < self.green_count < 19 and row['close'] < row['upper_keltner']:
            self.green_count += 1
            self.df.at[length, 'tradable'] = 'Counting after G Break'

        # When 20 candles after climax are over
        elif self.green_count == 19 and row['close'] < row['upper_keltner'] and self.red_count == 0:
            self.green_count = 0
            self.df.at[length, 'tradable'] = 0

        # When red candle goes outside the channel
        if (((row['candle'] == 'R' and row['open'] < row['lower_keltner']) or
             (row['candle'] == 'G' and row['close'] < row['lower_keltner'])) and
                self.buy_flag == True and
                (abs(row['lower_keltner'] - row['close']) / one_percent) >= 0.07):
            self.sell_flag = False
            self.red_count = 0
            self.df.at[length, 'tradable'] = 'Red Breakout'

        # When the price remains outside the channel after a red breakout
        elif row['close'] < row['lower_keltner'] and self.buy_flag == True and self.sell_flag == False:
            self.df.at[length, 'tradable'] = 'Outside after Red Breakout'

        # Any candle in 20 count closes outside the channel, restart the count
        elif row['close'] < row['lower_keltner'] and self.sell_flag == True and self.red_count > 0:
            self.red_count = 0
            self.sell_flag = False
            self.df.at[length, 'tradable'] = 'Outside after R Break'

        # When the price returns inside the channel after a sell breakout
        elif row['close'] > row['lower_keltner'] and self.sell_flag == False:
            self.sell_flag = True
            self.red_count = 1
            self.df.at[length, 'tradable'] = 'Sell count 1'

        # Counting 20 candles when red breakout moves inside the channel
        elif 0 < self.red_count < 19 and row['close'] > row['lower_keltner']:
            self.red_count += 1
            self.df.at[length, 'tradable'] = 'Counting after sell breakout'

        # When 20 candles after climax are over
        elif self.red_count == 19 and row['close'] > row['lower_keltner'] and self.green_count == 0:
            self.red_count = 0
            self.df.at[length, 'tradable'] = 0
            
#         When Its a normal candle
        else:
            
            self.df.at[length, 'tradable'] = 0

#   Check if candle inside Keltner's Channel
    
    def check_inside_kt(self, x):
        
        if  ( x['high'] < x['upper_keltner'] and x['low'] > x['lower_keltner'] and
             ( x['high'] >= x['EMA_20'] and x['EMA_20']> x['close']) or
            
            (x['low'] <= x['EMA_20'] and x['EMA_20'] < x['close']) or
            
            ( x['high'] >= x['EMA_15'] and x['EMA_15']> x['close']) or
                                
            (x['low'] <= x['EMA_15'] and x['EMA_15'] < x['close']) ):
            return 1
        
        else:
            return 0
        
#     def entries(self):
        
# #         Check for possible trades
        
#         length = len(self.df) - 1
        
#         self.df.loc[length, 'pos'] = self.check_inside_kt(self.df.iloc[-1])
        
#         self.df.loc[length, 'candle_size'] = self.check_body(self.df.iloc[-1])

#         self.df.loc[length, 'prev_candle'] = self.check_prev_candle(self.df.iloc[-1])
        
#         self.df.loc[length, 'trade'] = self.check_trade(self.df.iloc[-1])
        
#         self.check_tradable(self.df.iloc[-1])
        
        
        
#   Apply all the conditions on current candle

    def check_conditions(self):
        
        length = len(self.df) - 1
        
#         Checking all entry conditions
        
        self.df.loc[length, 'pos'] = self.check_inside_kt(self.df.iloc[-1])
        
        self.df.loc[length, 'candle_size'] = self.check_body(self.df.iloc[-1])

        self.df.loc[length, 'prev_candle'] = self.check_prev_candle(self.df.iloc[-1])
        
        self.df.loc[length, 'trade'] = self.check_trade(self.df.iloc[-1])
        
        self.check_tradable(self.df.iloc[-1])
        
        self.chart = self.df.loc[length]['open']/100 * 0.04
        
#         print('Check Condition')
#         print('Pos: ', self.df.loc[length, 'pos'])
#         print('Prev: ', self.df.loc[length, 'prev_candle'])
#         print('Candle size:',self.df.loc[length, 'candle_size'] )
#         print('Tradable: ', self.df.loc[length, 'tradable'])
#         print('Check RSI: ', self.check_rsi(self.df.iloc[-1]))
        
        if ( (self.df.loc[length, 'pos'] == 1) and (self.df.loc[length, 'candle_size'] == 1) and
           (self.df.loc[length, 'prev_candle'] == True) and (self.df.loc[length, 'tradable'] == 0) and
           (self.check_rsi(self.df.iloc[-1]) == 1) and (self.df.loc[length, 'squeeze_on'] == False) ):
            
#             print('Entry candle')
#             Set SL for ever entry
            self.df.loc[length, 'sl'] = self.set_sl(self.df.iloc[-1])
            
            self.result_len = len(self.result)

            self.result.loc[self.result_len, 'ENTRY DATE'] = self.df.loc[length, 'date']
            self.result.loc[self.result_len, 'ENTRY'] = self.df.loc[length, 'close']
            self.result.loc[self.result_len, 'TRADE'] = self.df.loc[length, 'trade']
            self.result.loc[self.result_len, 'S/L'] = self.df.loc[length, 'sl']

            self.calculations()


#     elif self.buy_on == True:
# #             print('Buy trade on')
#         self.manage_buy()

# #             If in sell trade
#     elif self.sell_on == True:

#         self.manage_sell()

    def pip_calc(self, close, sl):
#         Calculate pips between Entry & SL
        
        if str(close).index('.') >= 3:  # JPY pair
            multiplier = 0.01
        
        else:
            multiplier = 0.0001

        pips = round(abs(sl - close) / multiplier)
        return int(pips)
    
    
    def result_pip_calc(self, close, value):
#         Calculate pip value from currency price 
        
        if str(close).index('.') >= 3:  # JPY pair
            multiplier = 100
        
        else:
            multiplier = 10000
            
        pip = value * multiplier
        
        return float(pip)
    
    
    def calc_quantity(self, pips):
#         To find the number of lots to trade

        lots = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8,
                1.9, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
#       Risk per trade 2%  of 10K $ account
        rpt = 200
    
#         print('Pips in calc_quantity: ', pips)

#         sl = 76

        quantity = []

        for i in lots:

            if (i * pips * self.one_pip_value) <= rpt:
                quantity.append(i)
        
        if quantity:

            return max(quantity)
        
        else:
            return 0
        
        
        
    
    def calculations(self):
        
        l = len(self.df) - 1 
        self.sl = self.result.loc[self.result_len, 'S/L']
        self.trail_sl = False

        self.base_candle_index = self.df.index[-1]


        self.doji_count = 0

        pips = self.pip_calc(self.result.loc[self.result_len, 'ENTRY'], self.result.loc[self.result_len, 'S/L'])

#         print('Pips: ', pips)
        self.quantity = self.calc_quantity(pips)
        

        self.result.loc[self.result_len,'QUANTITY'] = self.quantity

        self.candles_size = abs(self.df.loc[l,'high'] - self.df.loc[l,'low'])

        if (self.result.loc[self.result_len, 'TRADE']) =='B':
            
#             print('Buy Trade')

            self.buy_on = True

            self.target = self.result.loc[self.result_len, 'ENTRY'] + 2 * (self.result.loc[self.result_len, 'ENTRY'] - self.result.loc[self.result_len, 'S/L'])

            self.breakeven = self.result.loc[self.result_len, 'ENTRY'] + self.candles_size

            # Call MT5 with order for Buying in quantity as lot size, and SL TRG 
            # Pass everything from result, we have everything there, just target will be different    


        elif (self.result.loc[self.result_len, 'TRADE']) =='S':

            self.sell_on = True

            self.target = self.result.loc[self.result_len, 'ENTRY'] - 2 * abs(self.result.loc[self.result_len, 'ENTRY'] - self.result.loc[self.result_len, 'S/L'])

            self.breakeven = self.result.loc[self.result_len, 'ENTRY'] - self.candles_size
            
            # Call MT5 with order for Selling in quantity as lot size, and SL TRG


    
    def manage_buy(self):
        

        print('In Buy')

        length = len(self.df) - 1

#             current_candle = self.df.loc[length,'candle']

        current_candle = self.df.loc[length]['candle']

#         print(current_candle)

        if current_candle == 'G':
            # TRG and Trail SL condition

            print('In a green candle')

            if self.df.loc[length]['high'] >= self.target:
                # TRG
                print('In TRG exit condition')
#                 print(self.df.loc[length,'date'])
                self.result.loc[self.result_len, 'EXIT'] = self.target
                self.result.loc[self.result_len, 'EXIT DATE'] = self.df.loc[length]['date']
                self.result.loc[self.result_len, 'REASON'] = 'TRG'
                self.buy_on = False

            # For Breakeven
            elif self.df.loc[length]['high'] >= self.breakeven:
                self.sl = min(self.df.loc[self.base_candle_index]['close'], self.df.loc[self.base_candle_index]['EMA_8'])
                self.trail_sl = True
                

        # For Gap Down exit
            elif self.sl >= self.df.loc[length]['open']:

                print('In SL Condition')
#                 print(self.df.loc[length,'date'])
                self.result.loc[self.result_len, 'EXIT'] = self.df.loc[length]['open']
                self.result.loc[self.result_len, 'EXIT DATE'] = self.df.loc[length]['date']
                if self.trail_sl:
                    self.trail_sl = False
                    self.result.loc[self.result_len, 'REASON'] = 'TRAIL_SL'
                  

                else:
                    self.result.loc[self.result_len, 'REASON'] = 'SL'
                self.buy_on = False
               

            # Green candle low hits SL 
            elif self.sl >= self.df.loc[length]['low']:
                print('In SL Condition')
#                 print(self.df.loc[length,'date'])
                self.result.loc[self.result_len, 'EXIT'] = self.sl
                self.result.loc[self.result_len, 'EXIT DATE'] = self.df.loc[length]['date']
                if self.trail_sl:
                    self.result.loc[self.result_len, 'REASON'] = 'TRAIL_SL'
                    self.trail_sl = False

                else:
                    self.result.loc[self.result_len, 'REASON'] = 'SL'

                self.buy_on = False

        elif current_candle == 'R':
            # SL condition
            print('In red candle')
            
            # For Gap down
            if self.sl >= self.df.loc[length]['open']:
                print('In SL Condition')
#                 print(self.df.loc[length,'date'])

                self.result.loc[self.result_len, 'EXIT'] = self.df.loc[length]['open']
                self.result.loc[self.result_len, 'EXIT DATE'] = self.df.loc[length]['date']
                
                if self.trail_sl:
                    self.result.loc[self.result_len, 'REASON'] = 'TRAIL_SL'
                    self.trail_sl = False
                    self.buy_on = False
                
                else:
                    self.result.loc[self.result_len, 'REASON'] = 'SL'
                
                self.buy_on = False

            # For SL
            elif self.sl >= self.df.loc[length]['low']:
                print('In SL Condition')
#                 print(self.df.loc[length,'date'])
                self.result.loc[self.result_len, 'EXIT'] = self.sl
                self.result.loc[self.result_len, 'EXIT DATE'] = self.df.loc[length]['date']
                
                if self.trail_sl:
                    self.result.loc[self.result_len, 'REASON'] = 'TRAIL_SL'
                    self.trail_sl = False

                
                else:
                    self.result.loc[self.result_len, 'REASON'] = 'SL'
                self.buy_on = False

        # Max wait period 11 Days till breakeven 
        # or current candle closed above 1% to last
        # else exit the trade
        prev_close_one_percent = (self.df.loc[length - 1]['close']) / 100

        if ((length > (self.base_candle_index + 10)) and (self.df.loc[length]['close'] < self.breakeven) and 
        (self.df.loc[length]['close'] < (self.df.loc[length - 1]['close']) + prev_close_one_percent)):
            self.result.loc[self.result_len, 'EXIT'] = self.df.loc[length]['close']
            self.result.loc[self.result_len, 'EXIT DATE'] = self.df.loc[length]['date']
            self.result.loc[self.result_len, 'REASON'] = 'NO MOVE'
            self.buy_on = False
            self.trail_sl = False
        
        if self.buy_on == False:
            
            self.result.loc[self.result_len, 'P/L'] = self.result.loc[self.result_len]['EXIT'] - self.result.loc[self.result_len]['ENTRY']

            self.result.loc[self.result_len, 'REAL P/L'] = (
            self.quantity * self.one_pip_value * self.result_pip_calc(
            self.result.loc[self.result_len]['ENTRY'],
            self.result.loc[self.result_len, 'P/L']
                )
            )


    
    def manage_sell(self):
            
        print('In Sell')

        length = len(self.df) - 1


        current_candle = self.df.loc[length]['candle']

        if current_candle == 'R':
            # TRG  and Trail SL condition

            if self.df.loc[length]['low'] <= self.target:
                # TRG

                self.result.loc[self.result_len, 'EXIT'] = self.target
                self.result.loc[self.result_len ,'EXIT DATE'] = self.df.loc[length]['date']
                self.result.loc[self.result_len, 'REASON'] = 'TRG'
                self.sell_on = False
                self.trail_sl = False



            # For Breakeven
            elif self.df.loc[length]['low'] <= self.breakeven:
                self.sl = min(self.df.loc[self.base_candle_index]['close'], self.df.loc[length]['EMA_8'])
                self.trail_sl = True


        #               For Gap Up exit
            elif self.sl <= self.df.loc[length]['open']:

                self.result.loc[self.result_len, 'EXIT'] =  self.df.loc[length]['open']
                self.result.loc[self.result_len, 'EXIT DATE'] = self.df.loc[length]['date']

                if self.trail_sl:
                    self.result.loc[self.result_len, 'REASON'] = 'TRAIL_SL'
                    self.trail_sl = False

                else:
                    self.result.loc[self.result_len, 'REASON'] == 'SL'

                self.sell_on = False


            # Red candle High hits SL 
            elif self.sl <= self.df.loc[length]['high']:

                self.result.loc[self.result_len, 'EXIT'] =  self.sl
                self.result.loc[self.result_len, 'EXIT DATE'] = self.df.loc[length]['date']

                if self.trail_sl:
                    self.result.loc[self.result_len, 'REASON'] = 'TRAIL_SL'
                    self.trail_sl = False

                else:
                    self.result.loc[self.result_len, 'REASON'] = 'SL'

                self.sell_on = False


        elif current_candle == 'G':
        # SL condition

        #                 For Gap UP
            if self.sl <= self.df.loc[length]['open']:

                self.result.loc[self.result_len, 'EXIT'] =  self.df.loc[length]['open']
                self.result.loc[self.result_len, 'EXIT DATE'] = self.df.loc[length]['date']

                if self.trail_sl:
                    self.result.loc[self.result_len, 'REASON'] = 'TRAIL_SL'
                    self.trail_sl = False

                else:
                    self.result.loc[self.result_len, 'REASON'] = 'SL'

                self.sell_on = False

        #                 For SL
            elif self.sl <= self.df.loc[length]['high']:

                self.result.loc[self.result_len, 'EXIT'] = self.sl
                self.result.loc[self.result_len, 'EXIT DATE'] = self.df.loc[length]['date']
                if self.trail_sl:
                    self.result.loc[self.result_len, 'REASON'] = 'TRAIL_SL'
                    self.trail_sl = False

                else:
                    self.result.loc[self.result_len, 'REASON'] = 'SL'

                self.sell_on = False


        #  Max wait period 11 Days till breakeven 
        # or current candle closed above 1% to last
        # else exit the trade
        prev_close_one_percent = (self.df.loc[length - 1]['close'])/100

        if ((length > (self.base_candle_index + 10)) and (self.df.loc[length]['close'] > self.breakeven) and
            (self.df.loc[length]['close'] >  (self.df.loc[length - 1]['close']) - prev_close_one_percent)):

            self.result.loc[self.result_len, 'EXIT'] = self.df.loc[length]['close']
            self.result.loc[self.result_len ,'EXIT DATE'] = self.df.loc[length]['date']
            self.result.loc[self.result_len, 'REASON'] = 'NO MOVE'
            self.sell_on = False
            self.trail_sl = False

        if self.sell_on == False:
        
            self.result.loc[self.result_len, 'P/L'] = self.result.loc[self.result_len]['ENTRY'] - self.result.loc[self.result_len]['EXIT']


            self.result.loc[self.result_len, 'REAL P/L'] = (
            self.quantity * self.one_pip_value * self.result_pip_calc(
            self.result.loc[self.result_len]['ENTRY'],
            self.result.loc[self.result_len, 'P/L']
                )
            )
        
    
    def Caller(self):
        # Initialize an empty DataFrame to store the past data that gets dropped
        self.past_df = pd.DataFrame()
        
#         Loop for taking the live data
        for index, row in self.df2.iterrows():
            # Add live data to the df DataFrame
            self.df = self.df.append(row, ignore_index=True)
#             self.df = pd.concat([self.df, row], ignore_index=True)

            # Delete the first row if the DataFrame has more than 202 rows
            if len(self.df) > 500:
                # Save the dropped row in past_df
                self.past_df = self.past_df.append(self.df.iloc[0], ignore_index=True)
                self.df = self.df.iloc[1:].reset_index(drop=True)
            

#             position_index = self.df[self.df['date'] == self.trend_date].index[0]
    
# #           Check trend
#             self.calculate_current_trend(position_index)
            
            # Calculate indicators for the current state of df
            self.calculate_indicators()
            
#             self.entries()

            if self.buy_on == True:
                
                self.manage_buy()
                                    
            elif self.sell_on == True:
                                    
                self.manage_sell()
                
            else:
            
    #             Apply all entry conditions
                self.check_conditions()

        # Concatenate past_df and df to get the full dataset
        self.result_df = pd.concat([self.past_df, self.df], ignore_index=True)

        # Save the result_df to an Excel file
        self.result_df.to_excel('combined.xlsx')
        
        self.result.to_excel('Record_trades.xlsx')


ob = LiveTrade()

ob.Caller()