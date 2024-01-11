import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pytz


if not mt5.initialize(
                    login=114999529, server="Exness-MT5Trial6", password="Mypassword$1234"
                ):
                    print("initialize() failed, error code =", mt5.last_error())
                    quit()

login = 114999529
password = "Mypassword$1234"
server = "Exness-MT5Trial6"
mt5.login(login, password, server)


# # Get the current UTC time
# utc_now = datetime.utcnow()

# # Add UTC timezone informationS
# utc_now = utc_now.replace(tzinfo=pytz.utc)

# print(datetime.now())

ob = mt5.copy_rates_from('EURUSD', mt5.TIMEFRAME_M15, datetime.now(), 1)
# print(ob)
new_candle = pd.DataFrame()
new_candle['date'] = pd.to_datetime(ob['time'].copy(), unit='s')

print(new_candle)

# new_candle['date'] += timedelta(minutes=15)

print('=======================')
# print('After Candle: ', new_candle["date"])

# from datetime import datetime
# import pytz

# # Get the current UTC time
# utc_now = datetime.utcnow()

# # Add UTC timezone information
# utc_now = utc_now.replace(tzinfo=pytz.utc)

# # Format and print the UTC time
# print("Current UTC Time:", utc_now.strftime('%Y-%m-%d %H:%M:%S %Z'))
