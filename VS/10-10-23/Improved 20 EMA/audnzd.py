from Strategy_20 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['AUDNZD', 5.8553, 24000])

eurusd.Caller('AUDNZD')