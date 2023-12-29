from Strategy import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurgbp = LiveTrade(['EURGBP', 12.2016, 50000])

eurgbp.Caller('EURGBP')

