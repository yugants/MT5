from Strategy_Backtesting import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['EURUSD', 10, 50000, 200])

eurusd.Caller('EURUSDNOTREND')

