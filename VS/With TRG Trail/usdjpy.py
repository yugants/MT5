from Strategy import LiveTrade
import warnings

# Ignore all warnings (not recommended, use with caution)
warnings.filterwarnings("ignore")

usdjpy = LiveTrade(['USDJPY', 6.69582, 24000])

usdjpy.Caller('USDJPY')

