from Strategy_20 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['AUDUSD', 10, 24000])

eurusd.Caller('AUDUSD')