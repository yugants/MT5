from Strategy_20 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['GBPJPY', 6.68275, 24000])

eurusd.Caller('GBPJPY')