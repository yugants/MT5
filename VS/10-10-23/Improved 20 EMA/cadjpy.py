from Strategy_20 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

cadjpy = LiveTrade(['CADJPY', 6.69582, 24000])

cadjpy.Caller('CADJPY')

