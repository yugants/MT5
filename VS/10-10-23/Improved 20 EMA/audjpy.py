from Strategy_20 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

audjpy = LiveTrade(['AUDJPY', 6.69582, 24000])

audjpy.Caller('AUDJPY')

