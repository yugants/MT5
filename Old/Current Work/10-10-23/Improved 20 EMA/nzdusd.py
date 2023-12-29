from Strategy_20 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['NZDUSD', 10, 24000])

eurusd.Caller('NZDUSD')