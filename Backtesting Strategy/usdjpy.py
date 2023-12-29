from Trend_Backtest import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['USDJPY', 6.68275, 10000, 200])

eurusd.Caller('USDJPY')