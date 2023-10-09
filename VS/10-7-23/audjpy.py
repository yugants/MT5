from Strategy import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

audjpy = LiveTrade(['AUDJPY', 6.69582, 50000])

audjpy.Caller('AUDJPY')

