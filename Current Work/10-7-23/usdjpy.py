from Strategy import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

usdjpy = LiveTrade(['USDJPY', 6.69582, 50000])

usdjpy.Caller('USDJPY')

