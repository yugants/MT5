from Strategy_20 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['CADCHF', 11.22624, 24000])

eurusd.Caller('CADCHF')