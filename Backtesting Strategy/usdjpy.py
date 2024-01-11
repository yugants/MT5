from Backtest_for_time import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['USDJPY', 6.68275, 50000, 50])

eurusd.Caller('USDJPY')