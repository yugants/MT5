from Strategy import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurjpy = LiveTrade(['GBPUSD', 10, 50000])

eurjpy.Caller('GBPUSD')

