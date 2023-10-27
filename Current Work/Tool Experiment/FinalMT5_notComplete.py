import MetaTrader5 as mt5
import pandas as pd
import datetime


if not mt5.initialize(
            login=114999529, server="Exness-MT5Trial6", password="Mypassword$1234"
        ):
            print("initialize() failed, error code =", mt5.last_error())
            quit()

login = 114999529
password = "Mypassword$1234"
server = "Exness-MT5Trial6"
print(mt5.login(login, password, server))


request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": "EURUSD",
    "volume": 0.01, 
    "type": mt5.ORDER_TYPE_BUY,
    "price": mt5.symbol_info_tick("EURUSD").ask,
    "sl": 0.0, 
    "tp": 0.0, 
    "deviation": 20, 
    "magic": 234000, 
    "comment": "python script open",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_FOK,  # Change the filling mode here
}

order = mt5.order_send(request)
print(order)


