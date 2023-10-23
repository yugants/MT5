from Strategy_20 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurgbp = LiveTrade(['EURGBP', 12.2016, 24000])

eurgbp.Caller('EURGBP')

