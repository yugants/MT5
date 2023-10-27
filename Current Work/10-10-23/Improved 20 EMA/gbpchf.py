from Strategy_20 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['GBPCHF', 11.22624, 24000])

eurusd.Caller('GBPCHF')