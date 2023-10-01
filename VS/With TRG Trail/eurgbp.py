from Strategy import LiveTrade
import warnings

# Ignore all warnings (not recommended, use with caution)
warnings.filterwarnings("ignore")


eurgbp = LiveTrade(['EURGBP', 12.2016, 24000])

eurgbp.Caller('EURGBP')

