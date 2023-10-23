from Strategy import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurjpy = LiveTrade(['EURJPY', 6.69582, 24000])

eurjpy.Caller('EURJPY')

