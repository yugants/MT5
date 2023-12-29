from Trend_Backtest import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['EURJPY', 6.68275, 10000, 50])

eurusd.Caller('EURJPY')