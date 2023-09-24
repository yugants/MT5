import pandas as pd
import talib
import numpy as np
import MetaTrader5 as mt5
import datetime

class Trend:
    
    def __init__(self):
        
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

        
        # print(self.df.head())
        
    def display(self):
        self.df.to_excel('data.xlsx')
        
        
    def define_trend(self, current_high, current_low, prev_high, prev_low, days, i):
        #       Uptrend
            if current_high > prev_high and current_low > prev_low:
    #           Find point at which current sample
    #           crossed prev high

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
                self.df.loc[i : i+days, 'trend'] = 'no trend'

    
    def get_trend(self, i=0):
        
        length = len(self.df)

        # print('Length: ', length)
        
        days = 21

        prev_high = self.df.loc[self.df.index[i : i+days], 'high'].max()
        
        prev_low = self.df.loc[self.df.index[i : i+days], 'low'].min()

        while(i + days  < length):

            # print('In Trend !!')
        
            i += days
            
            current_high = self.df.loc[self.df.index[i : i+days], 'high'].max()
            current_low = self.df.loc[self.df.index[i : i+days], 'low'].min()
            
            self.define_trend(current_high, current_low, prev_high, prev_low, days, i)
            
            prev_high = current_high
            prev_low = current_low
            
                    
                
        if i < length-1:
            prev_high = self.df.loc[self.df.index[i-days:i], 'high'].max()
            prev_low = self.df.loc[self.df.index[i-days:i], 'low'].min()
            
            current_high = self.df.loc[self.df.index[i : length], 'high'].max()
            current_low = self.df.loc[self.df.index[i : length], 'low'].min()
            
            days = length-i
            
            self.define_trend(current_high, current_low, prev_high, prev_low, days, i)


    def in_squeeze(self, df):
        return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']


    def indicators(self):
        '''Adding EMAs, BB, Keltner Channel and RSI'''

        self.df['EMA_7'] = talib.EMA(self.df['close'], timeperiod=7)

        self.df['EMA_21'] = talib.EMA(self.df['close'], timeperiod=21)
        
        self.df['EMA_50'] = talib.EMA(self.df['close'], timeperiod=50)

        self.df['EMA_200'] = talib.EMA(self.df['close'], timeperiod=200)

        self.df['RSI'] = talib.RSI(self.df['close'], timeperiod=21)

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

        # self.df.to_excel('test.xlsx')


    def candle(self, df):
        '''Return candle colour'''

        if df['close'] - df['open'] > 0:
            return 'G'

        else:
            return 'R'

    def check_body(self, df):
    #     Calculate 0.7 % of entry price
#     fOR 1H FOREX
        one_percent = df['open']/100 
        percent = one_percent * 0.07
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
            
    #     check for entry candle size and Max candle size 4.5 %
        if (candle_size >= percent) and candle_size <= (4.5 * one_percent) and (candle_size > upper_wick) and (candle_size > lower_wick):
            return 1

    #     condition for hammmer
    #     lower wick is atleast 50 % of total size 
        elif (df['open'] - df['low']) >= ((df['high'] - df['low']) * 0.5) and (candle_size >= hammer_per) and (candle_size > upper_wick):
            return 1

        else:
            return 0
        


    def check_prev_candle(self, element):

        current_index = self.df.loc[self.df.date ==  element.date].index[0]
        current_close = element.close



        if current_index > 0:
            prev_index = current_index - 1 

            prev_candle = self.df.iloc[prev_index]['candle']


            if prev_candle == 'G':
                prev_close = self.df.iloc[prev_index][ 'close']

            else:
                prev_close = self.df.iloc[prev_index][ 'open']

            if current_close >= prev_close:
                return 1

            else:
                return 0

        return 0
    

    '''Get last candle price
    For Two candle entry method!'''

    def get_last_candle_price(data, entry_candle_colour : str):
        global df
        
        prev = df.loc[df['time'] == data].index[0]-1
        
        # Colour
        candle = df.iloc[prev][-2]
        
    #     print('Prev candle: ', candle, ' ', df.iloc[prev][0])
        
        
        if candle == 'G' and entry_candle_colour == 'R':
            # Open of prev green to see
            # entry red has closed below or not
            price = df.iloc[prev][1]
            return [price, candle]
            
        elif candle == 'R' and entry_candle_colour == 'G':
            # Open of red candle for checking entry with green has 
            # closing above or not
            price = df.iloc[prev][1]
            return [price, candle]
        
        else:
            return 'valid_trade'


    def mark_emas(self):
        '''Marking candles with colour'''
        
        self.df['candle'] = self.df.apply(self.candle, axis=1)
        
        '''Marking candles on emas'''

        self.df['pos_trade'] = self.df.apply (lambda x: '1' if (x['open'] <= x['EMA_50'] and x['EMA_50'] <= x['close']) or ( x['open'] >=
                             x['EMA_50'] and x['EMA_50']>= x['close'])  
                             or  (x['open'] <= x['EMA_21'] and x['EMA_21'] <= x['close']) or ( x['open'] >=
                             x['EMA_21'] and x['EMA_21']>= x['close'])  
                             or (x['open'] <= x['EMA_200'] and x['EMA_200'] <= x['close']) or ( x['open'] >=
                             x['EMA_200'] and x['EMA_200']>= x['close']) else '0', axis=1)

        
        # Get all possible entries in squeeze

        self.squeeze = self.df.loc[(self.df['squeeze_on'] == False) & (self.df['pos_trade'] == '1') & (self.df['trend'] != 'no trend')]

        # Check prev candle 
        '''Checking 2 Candle entry 
        valid RSI with OB and OS
        21-50 in position'''

        for i in self.squeeze.index:
            
            current_colour =  self.df.loc[i, "candle"]
            response = self.get_last_candle_price(self.df.loc[i, "time"], current_colour)
            
            if response == 'valid_trade':
                continue
                
            elif current_colour == 'G' and response[1] == 'R':
                if self.df.loc[i, 'close'] < response[0] or self.df.loc[i, 'RSI'] <= 50 or self.df.loc[i, 'RSI'] >= 70 or self.df.loc[i, 'EMA_21'] < self.df.loc[i, 'EMA_50']:
                    self.df.loc[i, 'pos_trade'] = '0'
                    
            elif current_colour == 'R' and response[1] == 'G':
                # Red needs to close below green
                if self.df.loc[i, 'close'] > response[0] or self.df.loc[i, 'RSI'] >= 50 or self.df.loc[i, 'RSI'] <= 30 or self.df.loc[i, 'EMA_21'] > self.df.loc[i, 'EMA_50']:
                    self.df.loc[i, 'pos_trade'] = '0'


        

ob = Trend()
ob.get_trend()
ob.indicators()
ob.display()            
            