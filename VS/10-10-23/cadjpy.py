from Strategy import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

cadjpy = LiveTrade(['CADJPY', 6.69582, 50000])

cadjpy.Caller('CADJPY')

