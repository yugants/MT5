from Trend_Backtest import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['EURUSD', 10, 10000, 200])

eurusd.Caller('EURUSD')

