from Strategy_20 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['USDJPY', 6.68275, 24000])

eurusd.Caller('USDJPY')