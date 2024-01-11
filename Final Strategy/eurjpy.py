from ForTime import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

eurusd = LiveTrade(['EURJPY', 6.68275, 500, 50])

eurusd.Caller()