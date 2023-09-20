# Condition Check

checker = pd.DataFrame()

def check_conditions():

    global df, checker
    length = len(df) - 1

#         Checking all entry conditions

    df.loc[length, 'candle'] = candle(df.iloc[-1])
    
    df.loc[length, 'pos'] = check_inside_kt(df.iloc[-1])

    df.loc[length, 'candle_size'] = check_body(df.iloc[-1])
    
#     print('Candle: ',df.loc[length, 'candle'] )
#     print('KT: ', df.loc[length, 'pos'])
#     print('Size: ', df.loc[length, 'candle_size'])

    df.loc[length, 'prev_candle'] = check_prev_candle(df.iloc[-1])
    
#     print('Prev candle: ', df.loc[length, 'prev_candle'])
    
    if (df.loc[length, 'candle'] == 'G' and df.loc[length, 'pos'] == 1 and 
        df.loc[length, 'candle_size'] == 1 and df.loc[length, 'prev_candle'] == True):
        pass