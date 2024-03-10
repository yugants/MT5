from Backtesting_5_Tradable import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['USDJPY', 6.68275, 50000, 200])

eurusd.Caller('USDJPY')