from LiveCode2 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['USDJPY', 6.68275, 1000, 200])

eurusd.Caller()