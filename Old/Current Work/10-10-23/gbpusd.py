from Strategy_20 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurjpy = LiveTrade(['GBPUSD', 10, 24000])

eurjpy.Caller('GBPUSD')

