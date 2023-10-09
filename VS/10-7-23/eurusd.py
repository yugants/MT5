from Strategy import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['EURUSD', 10, 50000])

eurusd.Caller('EURUSD')

