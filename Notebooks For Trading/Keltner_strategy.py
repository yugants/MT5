import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
import datetime
import MetaTrader5 as mt5
import talib
import yfinance as yf
# import plotly.graph_objects as go

'''No Holding period yet decided'''
class BackTest:
    
    def __init__(self, instrument):
        '''Downloading data'''
        try:

            if not mt5.initialize(login=114781990, server="Exness-MT5Trial6",password="Mypassword$1234"):
                print("initialize() failed, error code =",mt5.last_error())
                quit()
            
            login = 114781990
            password = 'Mypassword$1234'
            server = 'Exness-MT5Trial6'

            mt5.login(login, password, server)

            rate = mt5.copy_rates_from('EURUSDm', mt5.TIMEFRAME_M15, datetime.datetime.now(), 10000)
            self.df = pd.DataFrame(rate)

            self.df['time']=pd.to_datetime(self.df['time'], unit='s')
            
            self.analyse = pd.DataFrame(columns=['TOTAL TRADES', 'WINS', 'LOSSES', 'PERFORMANCE', 'WIN RATE', 
                                'WINNING STREAK', 'LOSING STREAK', 'MAX DRAWDOWN', 'AVG GAIN', 'AVG LOSS'])
        
            self.df.set_index(np.arange(len(self.df)), inplace = True)
            self.df = self.df.drop(['spread', 'real_volume', 'tick_volume'], axis='columns')

            self.df.to_excel('data.xlsx')
            # print(self.df.head())
         

        except:
            print('Wrong Symbol! ')
            return('Check Symbol !')
        

    def in_squeeze(self, df):
        return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']
    
    
    def define_trend(self, current_high, current_low, prev_high, prev_low, days, i):
        #       Uptrend
            if current_high > prev_high and current_low > prev_low:
    #           Find point at which current sample
    #           crossed prev high

                # print('Up Case')

                stream = self.df.loc[self.df.index[i : i+days], 'high']
                up_candle_index = stream.loc[stream > prev_high].index[0]
                
    #             if df.loc[i+15, 'high'] > prev_high:
                    
                self.df.loc[up_candle_index : i+days, 'trend'] = 'up'

            
                if self.df.iloc[i-1]['trend'] == 'up':
                    self.df.loc[i: up_candle_index, 'trend'] = 'up'

                else:
                    self.df.loc[i: up_candle_index, 'trend'] = 'no trend'


    #         Downtrend
            elif (current_high < prev_high) and (current_low < prev_low):
    #           Find point at which current sample 
    #           crossed prev low
                # print('Down Case')
                stream = self.df.loc[self.df.index[i : i+days], 'low']
                down_candle_index = stream.loc[stream < prev_low,].index[0]
               
#                 print('DownCandleIndex: ', down_candle_index)
#                 print('Days Callee: ', days)
                
                self.df.loc[down_candle_index : i+days, 'trend'] = 'down'

                if self.df.iloc[i-1]['trend'] == 'down':
                    self.df.loc[i: down_candle_index, 'trend'] = 'down'

                else:
                    self.df.loc[i: down_candle_index, 'trend'] = 'no trend'


                    
            else:
                self.df.loc[i : i+15, 'trend'] = 'no trend'

    
    def get_trend(self, i=0):
        
        length = len(self.df)

        # print('Length: ', length)

        self.df['trend'] = 'no trend' 
        
        days = 21

        while(i + (2 * days)  < length):

            # print('In Trend !!')

            prev_high = self.df.loc[self.df.index[i : i+days], 'high'].max()
            prev_low = self.df.loc[self.df.index[i : i+days], 'low'].min()
        
            i += days
            
            current_high = self.df.loc[self.df.index[i : i+days], 'high'].max()
            current_low = self.df.loc[self.df.index[i : i+days], 'low'].min()
            
            self.define_trend(current_high, current_low, prev_high, prev_low, days, i)
            
                    
                
        if i < length-1:
            prev_high = self.df.loc[self.df.index[i-days:i], 'high'].max()
            prev_low = self.df.loc[self.df.index[i-days:i], 'low'].min()
            
            current_high = self.df.loc[self.df.index[i : length], 'high'].max()
            current_low = self.df.loc[self.df.index[i : length], 'low'].min()
            
            days = length-i
            
            self.define_trend(current_high, current_low, prev_high, prev_low, days, i)

            print(self.df.head())
            
        self.df.to_excel('trendd.xlsx')


    def indicators(self):
        '''Adding EMAs, BB, Keltner Channel and RSI'''

        self.df['EMA_5'] = talib.EMA(self.df['close'], timeperiod=5)

        self.df['EMA_50'] = talib.EMA(self.df['close'], timeperiod=50)

        self.df['EMA_200'] = talib.EMA(self.df['close'], timeperiod=200)
        self.df = self.df.dropna()

        # Identify trend on 15 days highs & lows
        self.get_trend()

    #     df.head()

        '''Bollinger Band'''
        self.df['20sma'] = self.df['close'].rolling(window=20).mean()
        self.df['stddev'] = self.df['close'].rolling(window=20).std()
        self.df['lower_band'] = self.df['20sma'] - (2 * self.df['stddev'])
        self.df['upper_band'] = self.df['20sma'] + (2 * self.df['stddev'])

        '''Keltners Channel'''
        self.df['TR'] = abs(self.df['high'] - self.df['low'])
        self.df['ATR'] = self.df['TR'].rolling(window=20).mean()

        self.df['lower_keltner'] = self.df['20sma'] - (self.df['ATR'] * 1.2)
        self.df['upper_keltner'] = self.df['20sma'] + (self.df['ATR'] * 1.2)
        
        
        self.df['squeeze_on'] = self.df.apply(self.in_squeeze, axis=1)

        self.df = self.df.drop(['stddev', 'lower_band', 'upper_band', '20sma', 'TR', 'ATR', 'lower_keltner', 'upper_keltner'],axis=1)

        self.df = self.df.dropna()

        self.df.set_index(np.arange(len(self.df)), inplace = True)

        self.df.index.name='sn'

        self.df.to_excel('test.xlsx')
        

a = BackTest('EURUSDm')
a.indicators()