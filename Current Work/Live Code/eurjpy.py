from LiveCode2 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['EURJPY', 6.68275, 50000, 50])

eurusd.Caller()