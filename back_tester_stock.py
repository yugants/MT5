'''Libraries'''

# import cufflinks as cf
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# import datetime
import talib
import yfinance as yf
# import plotly.graph_objects as go

'''No Holding period yet decided'''
class BackTest:
    
    def __init__(self, instrument):
        '''Downloading data'''
        try:
            '''start_date 2 years back for 200 EMA'''
            print('Given Date: ', instrument['startDate'])
            self.start_date = instrument['startDate']
            date = instrument['startDate'].split('-')
            year = int(date[0]) - 2
            new_date = f'{year}-{date[1]}-{date[2]}'
            print('New Date: ',new_date)
            self.df = pd.DataFrame(yf.download(instrument['stock'], start= new_date , end =instrument['endDate']))
            
            self.analyse = pd.DataFrame(columns=['TOTAL TRADES', 'WINS', 'LOSSES', 'PERFORMANCE', 'WIN RATE', 
                                'WINNING STREAK', 'LOSING STREAK', 'MAX DRAWDOWN', 'AVG GAIN', 'AVG LOSS'])
        
            '''Renaming columns and deleting unnecessary columns'''

            self.df.set_axis([ 'open', 'high', 'low', 'close', 'adj', 'volume'], axis='columns', inplace=True)
            self.df.insert(0,'date', self.df.index)
            self.df.set_index(np.arange(len(self.df)), inplace = True)
            self.df = self.df.drop(['volume', 'adj'], axis='columns')
#           df.head()

        except:
            print('Wrong Symbol! ')
            return('Check Symbol !')

    def display(self):

        # self.result.to_excel('ResultStock.xlsx')
        # self.analyse.to_excel('Analysis.xlsx')
        analyze = self.analyse.to_json(orient = 'records')
        
        #  Fixing Date
        self.result['ENTRY DATE'] = self.result.apply(lambda x : str(x['ENTRY DATE']).split()[0], axis=1)

        self.result['EXIT DATE'] = self.result.apply(lambda x : str(x['EXIT DATE']).split()[0], axis=1)

        # print('From Class: ', self.result['ENTRY DATE'])

        # self.result.to_excel('TCS.xlsx')

        result = self.result.to_json(orient = 'records')
        # print(self.result.head())

        return (analyze, result)
            
    def in_squeeze(self, df):
        return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']
    
    
    def get_trend(self, i=0):
        
        length = len(self.df)
        while(i + 15 < length):

            # print('In Trend !!')

            prev_high = self.df.loc[self.df.index[i : i+15], 'high'].max()
            prev_low = self.df.loc[self.df.index[i : i+15], 'low'].min()
            
            i += 15
            
            current_high = self.df.loc[self.df.index[i : i+15], 'high'].max()
            current_low = self.df.loc[self.df.index[i : i+15], 'low'].min()
            
    #         Uptrend
            if current_high > prev_high and current_low > prev_low:
    #           Find point at which current sample 
    #           crossed prev high

                stream = self.df.loc[self.df.index[i : i+15], 'high']
                up_candle_index = stream.loc[stream > prev_high].index[0]
                
    #             if df.loc[i+15, 'high'] > prev_high:
                    
                self.df.loc[up_candle_index : i+15, 'trend'] = 'up'

                if self.df.loc[i-1, 'trend'] == 'up':
                    self.df.loc[i: up_candle_index, 'trend'] = 'up'

                else:
                    self.df.loc[i: up_candle_index, 'trend'] = 'no trend'


    #         Downtrend
            elif (current_high < prev_high) and (current_low < prev_low):
    #           Find point at which current sample 
    #           crossed prev low

                stream = self.df.loc[self.df.index[i : i+15], 'low']
                down_candle_index = stream.loc[stream < prev_low,].index[0]

            #   Downtrend only below EMA_50
                if (self.df.loc[down_candle_index, 'close'] < self.df.loc[down_candle_index, 'EMA_50']):

                    self.df.loc[down_candle_index : i+15, 'trend'] = 'down'
                    
                    if self.df.loc[i-1, 'trend'] == 'down':
                        self.df.loc[i: down_candle_index, 'trend'] = 'down'
                        
                    else:
                        self.df.loc[i: down_candle_index, 'trend'] = 'no trend'

                else:
                    self.df.loc[i : i+15, 'trend'] = 'no trend'

                    
            else:
                self.df.loc[i : i+15, 'trend'] = 'no trend'



    def indicators(self):
        '''Adding EMAs, BB, Keltner Channel and RSI'''

        # self.df["EMA_5"] = self.df.close.ewm(span = 5, min_periods = 5).mean() 

#         EMA 20 cluster

        # self.df["EMA_19"] = self.df.close.ewm(span = 19, min_periods = 19).mean()
        # self.df["EMA_20"] = self.df.close.ewm(span = 20, min_periods = 20).mean()
        # self.df["EMA_21"] = self.df.close.ewm(span = 21, min_periods = 21).mean()
        
#        EMA 50 cluster

        # self.df["EMA_49"] = self.df.close.ewm(span = 49, min_periods = 49).mean()
        # self.df["EMA_50"] = self.df.close.ewm(span = 50, min_periods = 50).mean()
        # self.df["EMA_51"] = self.df.close.ewm(span = 51, min_periods = 51).mean()
        
#        EMA 200 cluster

        # self.df["EMA_199"] = self.df.close.ewm(span = 199, min_periods = 199).mean()
        # self.df["EMA_200"] = self.df.close.ewm(span = 200, min_periods = 200).mean()
        # self.df["EMA_201"] = self.df.close.ewm(span = 201, min_periods = 201).mean()
        
        
        # With talib
        # df['EMA_5'] = talib.EMA(df['close'], timeperiod=5)
        # df['EMA_20'] = talib.EMA(df['close'], timeperiod=20)

        self.df['EMA_5'] = talib.EMA(self.df['close'], timeperiod=5)

        # EMA 20 group
        self.df['EMA_18'] = talib.EMA(self.df['close'], timeperiod=18)
        self.df['EMA_20'] = talib.EMA(self.df['close'], timeperiod=20)
        self.df['EMA_22'] = talib.EMA(self.df['close'], timeperiod=22)
        # EMA 50 group
        self.df['EMA_48'] = talib.EMA(self.df['close'], timeperiod=48)
        self.df['EMA_50'] = talib.EMA(self.df['close'], timeperiod=50)
        self.df['EMA_52'] = talib.EMA(self.df['close'], timeperiod=52)
        # EMA 200 group
        self.df['EMA_198'] = talib.EMA(self.df['close'], timeperiod=198)
        self.df['EMA_200'] = talib.EMA(self.df['close'], timeperiod=200)
        self.df['EMA_202'] = talib.EMA(self.df['close'], timeperiod=202)

        self.df['RSI'] = talib.RSI(self.df['close'], timeperiod=14)
        self.df = self.df.dropna()

        self.df.set_index(np.arange(len(self.df)), inplace = True)
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

        
        '''Showing only asked results'''
        self.df = self.df.loc[self.df['date'] >= self.start_date]

        self.df.set_index(np.arange(len(self.df)), inplace = True)

        self.df.index.name='sn'
        # print('Updated DF: ',self.df.head())

        

    def candle(self, df):
        '''Return candle colour'''

        if df['close'] - df['open'] > 0:
            return 'G'

        else:
            return 'R'

    def check_body(self, df):
    #     Calculate 1.5 % of entry price
        one_percent = df['open']/100 
        percent = one_percent * 1.5

    #     Calculate candle size close-open
        candle_size = df['close'] - df['open']

        upper_wick = df['high'] - df['close']
        lower_wick = df['open'] - df['low']

    #     check for entry candle size and Max candle size 4.5 %
        if (candle_size >= percent) and candle_size <= (4.5 * one_percent) and (candle_size > upper_wick) and (candle_size > lower_wick):
            return 1

    #     condition for hammmer
    #     lower wick is atleast 50 % of total size 
        elif (df['open'] - df['low']) >= ((df['high'] - df['low']) * 0.5) and (candle_size >= one_percent) and (candle_size > upper_wick):
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
    #     How to check for the 1st candle?
        return 0
    
    def set_sl(self, df):
        '''Set SL 1% below to entry candle'''
        
        if df['pos_trade'] == '1':
            candle_size = df['high'] - df['low']

            sl = df['low'] - (candle_size/100)
            return sl
        
        else:
            return 0
    
    
    def mark_emas(self):
        '''Marking candles with colour'''
        
        self.df['candle'] = self.df.apply(self.candle, axis=1)
        
        '''Marking candles on emas'''

#         self.df['pos_trade'] = self.df.apply(lambda x: '1' if  ((x['low'] <= x['EMA_20'] and x['EMA_20'] < x['close']) or
#                                 (x['low'] <= x['EMA_21'] and x['EMA_21'] < x['close']) or
#                                 (x['low'] <= x['EMA_19'] and x['EMA_19'] < x['close']))
#                                  else '0', axis=1)
#         self.df['pos_trade'] = self.df.apply(lambda x: '1' if  (
#                                 (x['low'] <= x['EMA_19'] and x['EMA_19'] < x['close']) or
#                                 (x['low'] <= x['EMA_20'] and x['EMA_20'] < x['close']) or
#                                 (x['low'] <= x['EMA_21'] and x['EMA_21'] < x['close']))
#                                 else '0', axis=1)
    
        self.df['pos_trade'] = self.df.apply(lambda x: '1' if  (
                                (x['low'] <= x['EMA_18'] and x['EMA_18'] < x['close']) or

                                (x['low'] <= x['EMA_20'] and x['EMA_20'] < x['close']) or

                                (x['low'] <= x['EMA_22'] and x['EMA_22'] < x['close']) or

                                (x['low'] <= x['EMA_48'] and x['EMA_48'] < x['close']) or

                                (x['low'] <= x['EMA_50'] and x['EMA_50'] < x['close']) or

                                (x['low'] <= x['EMA_52'] and x['EMA_52'] < x['close']) or

                                (x['low'] <= x['EMA_198'] and x['EMA_198'] < x['close']) or

                                (x['low'] <= x['EMA_200'] and x['EMA_200'] < x['close']) or

                                (x['low'] <= x['EMA_202'] and x['EMA_202'] < x['close'])
                                )
                                else '0', axis=1)

        # self.df['pos_trade'] = self.df.apply(lambda x: '1' if  (
                               
        #                         (x['low'] <= x['EMA_20'] and x['EMA_20'] < x['close']) or
                                
        #                         (x['low'] <= x['EMA_50'] and x['EMA_50'] < x['close']) or
                               
        #                         (x['low'] <= x['EMA_200'] and x['EMA_200'] < x['close'])
        #                         )
        #                         else '0', axis=1)
        
#         Calculating SL
        
        self.df['sl'] = self.df.apply(self.set_sl, axis=1)
        
        
        self.squeeze = self.df.loc[(self.df['squeeze_on'] == False) & (self.df['pos_trade'] == '1') & (self.df['candle'] == 'G') & (self.df['trend'] != 'down')]
        # self.squeeze.to_excel('to_check_ema.xlsx')
#          Check candle size
        self.squeeze['candle_size'] = self.squeeze.apply(self.check_body, axis=1)

        self.squeeze = self.squeeze.loc[self.squeeze['candle_size'] == 1]
        
        #  Check with prev candle
        self.squeeze['prev_candle'] = self.squeeze.apply(self.check_prev_candle, axis=1)
        
        self.squeeze = self.squeeze.loc[self.squeeze['prev_candle'] == 1]
        
#         self.df = self.df.drop(['candle_size', 'prev_candle'],axis=1)
        
#         Check for RSI < 68
        # self.squeeze = self.squeeze.loc[(self.squeeze['RSI'] > 59) | (self.squeeze['RSI'] < 40) ]
        # self.squeeze = self.squeeze.loc[(self.squeeze['RSI'] > 59) ]
        self.squeeze = self.squeeze.loc[(self.squeeze['RSI'] < 68) ]
        # print('Columns: ',self.squeeze.columns)
#        Check for EMA 20 > EMA 50

        self.squeeze  = self.squeeze.loc[(self.squeeze['EMA_20'] > self.squeeze['EMA_50']) |
                                         (self.squeeze['EMA_20'] > self.squeeze['EMA_200']) | 
                                         ((self.squeeze['EMA_50'] > self.squeeze['EMA_200']) &
                                         (self.squeeze['close'] > self.squeeze['EMA_200']))]
    
        
#         Write to an excel

#         self.squeeze.to_excel('./Result/daybacktest.xlsx')
    
    
    def calc_exit(self, index : int, count):
        '''Calculating Exit, TRG and P/L'''
        
#         trade = df.loc[index]['pos_trade']
        sl = round(self.df.loc[index]['sl'], 2)
        f = 1
        trail_sl = False
#         entry_candle = self.df.loc[index]['candle']
    #     print('entry_candle: ', entry_candle)
        base_candle_index = index
    #     print('Entry candle: ', entry_candle)
    #     print('SL: ', sl)
    #     print('Trade: ', trade)

        self.doji_count = 0

        # Target 1:2
        target = round(self.df.loc[index]['close'] + 2 * (self.df.loc[index]['close'] - self.df.loc[index]['sl']), 2)
        breakeven = round(self.df.loc[index]['close'] + 1.5 * (self.df.loc[index]['close'] - self.df.loc[index]['sl']), 2)
    #         print('Trg: ', target)

        doji_counter = 0
        doji_flag = False
        
        # chart 0.7 %
        chart = self.df.loc[index]['open']/100 * 0.7

        while f == 1:
            
            if index >= (len(self.df)-1):
                break



    #     Calculate candle size close-open
    #     If body is less than .7% consider it doji
            prev_candle_size = abs(self.df.loc[index]['close'] - self.df.loc[index]['open'])

            # First encounter with doji
            if (prev_candle_size <= chart) and (doji_flag == False):
                doji_counter = 1
                doji_flag = True
                upper_limit = self.df.loc[index]['high']
                lower_limit = self.df.loc[index]['low']

#           Current candle check
            index += 1

            #  For Doji Check
            current_candle_high = self.df.loc[index]['high']
            current_candle_low = self.df.loc[index]['low']

            # if next is also doji
            if (doji_flag == True) and (current_candle_high <= upper_limit and current_candle_low >= lower_limit):
                # Exit on 3 doji's in a row
                if doji_counter > 2:
                    self.result.loc[count, 'EXIT'] = round(self.df.loc[index]['close'], 2)
                    self.result.loc[count ,'EXIT DATE'] = self.df.loc[index]['date']
                    self.result.loc[count, 'REASON'] = 'DOJI EXIT'
                    f = 0
                doji_counter += 1

            # For a non doji candle after doji
            else:
                doji_flag = False
                doji_counter = 0
                upper_limit = None
                lower_limit = None
            
            
       

            current_candle = self.df.loc[index]['candle']
    #         print('Current Candle: ', current_candle)        

            if current_candle == 'G':
                # TRG  and Trail SL condition

                if self.df.loc[index]['high'] >= target:
                    # TRG

                    self.result.loc[count, 'EXIT'] = target
                    self.result.loc[count ,'EXIT DATE'] = self.df.loc[index]['date']
                    self.result.loc[count, 'REASON'] = 'TRG'
    #                 print('Exit: ', result.loc[count]['EXIT'])
                    f = 0

                # For Breakeven
                elif self.df.loc[index]['high'] >= breakeven:
                    sl = round(min(self.df.loc[base_candle_index]['close'], self.df.loc[index]['EMA_5']), 2)
                    trail_sl = True
                    

#               For Gap Down exit
                elif sl >= self.df.loc[index]['open']:

                    self.result.loc[count, 'EXIT'] =  round(self.df.loc[index]['open'], 2)
                    self.result.loc[count, 'EXIT DATE'] = self.df.loc[index]['date']
                    if trail_sl:
                        self.result.loc[count, 'REASON'] = 'TRAIL_SL'
                        f = 0

                    self.result.loc[count, 'REASON'] = 'SL'
                    f = 0
                
                # Green candle low hits SL 
                elif sl >= self.df.loc[index]['low']:

                    self.result.loc[count, 'EXIT'] =  sl
                    self.result.loc[count, 'EXIT DATE'] = self.df.loc[index]['date']
                    if trail_sl:
                        self.result.loc[count, 'REASON'] = 'TRAIL_SL'
                        f = 0

                    self.result.loc[count, 'REASON'] = 'SL'
                    f = 0

            elif current_candle == 'R':
            # SL condition
            
#                 For Gap down
                if sl >= self.df.loc[index]['open']:

                    self.result.loc[count, 'EXIT'] =  round(self.df.loc[index]['open'], 2)
                    self.result.loc[count, 'EXIT DATE'] = self.df.loc[index]['date']
                    if trail_sl:
                        self.result.loc[count, 'REASON'] = 'TRAIL_SL'
                        f = 0
                    self.result.loc[count, 'REASON'] = 'SL'
                    f = 0
                
#                 For SL
                elif sl >= self.df.loc[index]['low']:

                    self.result.loc[count, 'EXIT'] = sl
                    self.result.loc[count, 'EXIT DATE'] = self.df.loc[index]['date']
                    if trail_sl:
                        self.result.loc[count, 'REASON'] = 'TRAIL_SL'
                        f = 0
                    self.result.loc[count, 'REASON'] = 'SL'
    #                 print('Exit: ', result.loc[count]['EXIT'])
                    f = 0

        #  Max wait period 11 Days till breakeven 
        # or current candle closed above 1% to last
        # else exit the trade
            prev_close_one_percent = (self.df.loc[index - 1]['close'])/100
            
            if (index > (base_candle_index + 10)) and (self.df.loc[index]['close'] < breakeven) and (self.df.loc[index]['close'] <  (self.df.loc[index - 1]['close']) + prev_close_one_percent):
                # print('------------------------------------------------')
                # print('LATE: ', index)
                # print('--------------------------------------------------------')
                self.result.loc[count, 'EXIT'] = round(self.df.loc[index]['close'], 2)
                self.result.loc[count ,'EXIT DATE'] = self.df.loc[index]['date']
                self.result.loc[count, 'REASON'] = 'NO MOVE'
                f= 0
         
        # Account value = 10 Lacs
        self.account = 1000000
        #  Risk per trade = 2 %
        self.rpt = (2 *  self.account) / 100

        if index < len(self.df):
            self.result.loc[count, 'P/L'] = self.result.loc[count]['EXIT'] - self.result.loc[count]['ENTRY']

            quantity = int(self.rpt / (self.result.loc[count]['ENTRY'] - self.result.loc[count]['S/L']))

            self.result.loc[count, 'QUANTITY'] = quantity
            
            self.result.loc[count, 'REAL_VAL'] = quantity * round(float(self.result.loc[count]['P/L']), 2)
    
           
            
    def record_trades(self):
        '''Recording Trades in a csv
        Without overlapping trades'''

        self.result = pd.DataFrame(columns=['ENTRY DATE', 'ENTRY', 'TRADE','QUANTITY', 'EXIT', 'EXIT DATE', 'REASON', 'P/L', 'REAL_VAL' ,'S/L' ])

        self.result["EXIT DATE"] = pd.to_datetime(self.result["EXIT DATE"]) 

        for i in self.squeeze.index:
            count = len(self.result)

            #     print(position.loc[i]['time'])


            if count == 0 or (self.squeeze.loc[i]['date'] > self.result.loc[count-1]['EXIT DATE']):

            #     print(position.loc[i,'time'])
                self.result.loc[count, 'ENTRY DATE'] = self.squeeze.loc[i,'date']
            #     print('Time: ', position.loc[i]['time'])

                self.result.loc[count, 'TRADE'] = self.squeeze.loc[i]['pos_trade']
            #     print('Position: ',  position.loc[i]['pos_trade'])``

                self.result.loc[count, 'ENTRY'] = round(self.squeeze.loc[i]['close'], 2)
            #     print('Close: ', position.loc[i]['close'])

                self.result.loc[count, 'S/L'] = round(self.squeeze.loc[i]['sl'], 2)
            #     print('SL: ', position.loc[i]['sl'])

                # for Exit & P/L 
                self.calc_exit(i, count)
                
    
    def streak(self):
        '''For max profit and loss streak'''

        positive_counter = 0 
        negative_counter = 0
        max_score = 1
        min_score = 1

        for ele in self.result['P/L']:
            if ele > 0:

                if(negative_counter > 0):
                    min_score = max(min_score, negative_counter)

                positive_counter += 1
                negative_counter = 0

            elif ele < 0:

                if(positive_counter > 0):
                    max_score = max(max_score, positive_counter)

                positive_counter = 0
                negative_counter += 1 


        self.analyse.loc[0,'WINNING STREAK'] = max_score
        self.analyse.loc[0,'LOSING STREAK']= min_score

        self.analyse.loc[0, 'MAX DRAWDOWN'] = str(float(2 * self.analyse.loc[0,'LOSING STREAK']) ) + '% [2% Risk/Trade]'
    
    def calc_avg(self):
    
        '''Avg gain and loss'''

        self.analyse.loc[0,'AVG GAIN'] = round(float(self.result.loc[self.result['P/L'] > 0]['P/L'].sum() /  self.analyse['WINS']), 2)

        self.analyse.loc[0,'AVG LOSS'] = round(float(self.result.loc[self.result['P/L'] < 0]['P/L'].sum() / self.analyse['LOSSES']), 2)

    # def performance(self):
    #     # Account value = 10 Lacs
    #     account = 1000000
    #     #  Risk per trade = 2 %
    #     rpt = (2 *  account) / 100

    #     for i in self.result.index:
        
    #         quantity = int(rpt / (self.result.loc[i]['ENTRY'] - self.result.loc[i]['S/L']))
    #         print('===========================================')

    #         self.result.loc[i, 'QUANTITY'] = quantity
    #         print('Quantity: ',quantity)
    #         print('===========================================')
    #         self.result.loc[i, 'REAL_VAL'] = quantity * float(self.result.loc[i]['P/L'])
    #         print('Real Value: ', self.result.loc[i]['REAL_VAL'])
    #         print('===========================================')

    #     print('Sum: ', self.result['REAL_VAL'].sum())
    #     self.analyse.loc[0,'PERFORMANCE'] = self.result['REAL_VAL'].sum() / account * 100

    #     print('After ================================================= After')
    
    def calc_result(self):
        '''Make Stats'''
        
        self.analyse.loc[0,'TOTAL TRADES'] = len(self.result)
        self.analyse.loc[0,'WINS'] = int(len(self.result.loc[self.result['P/L'] > 0]))
        self.analyse.loc[0,'LOSSES'] = int(len(self.result.loc[self.result['P/L'] < 0]))
        # Performance :- ((P/L)/ ENTRY) * 100
        # self.analyse.loc[0,'PERFORMANCE'] = str(float(( 4 * self.analyse.loc[0,'WINS']) - (2 * self.analyse.loc[0,'LOSSES']))) + '%'
        self.analyse.loc[0,'WIN RATE'] = str(round(float((self.analyse['WINS'] / self.analyse['TOTAL TRADES']) * 100), 2)) + '%'
        performance = round((self.result['REAL_VAL'].sum() / self.account) * 100, 2)
        self.analyse.loc[0,'PERFORMANCE'] = str( performance ) + ' %' 

        '''Avg gain and loss'''
        self.calc_avg()

        '''Max streaks calculation'''
        self.streak()

        #   Calc performance
        # self.performance()

        print(self.analyse)



# instrument = ["TCS.NS", '2010-01-01', '2023-05-05' ]

# stock = BackTest(instrument)

# 'Applying indicators on chart'
# stock.indicators()

# 'Adding candle colour'
# stock.mark_emas()

# stock.record_trades()

# stock.calc_result()

# stock.display()