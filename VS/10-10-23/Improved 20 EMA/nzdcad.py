from Strategy_20 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['NZDCAD', 7.31374, 24000])

eurusd.Caller('NZDCAD')