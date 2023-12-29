from LiveCode2 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['USDJPY', 6.68275, 500, 200])

eurusd.Caller()