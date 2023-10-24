from Strategy_20 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['EURAUD', 6.3561, 24000])

eurusd.Caller('EURAUD')