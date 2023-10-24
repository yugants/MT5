from Strategy_20 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['GBPUSD', 10, 24000])

eurusd.Caller('GBPUSD')