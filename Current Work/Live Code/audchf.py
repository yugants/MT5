from Strategy_Backtesting  import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")
# For Live
# audchf = LiveTrade(['AUDCHF', 11.19921, 50000, 200])
# For Backtesting
audchf = LiveTrade(['AUDCHF', 11.19921, 50000])

audchf.Caller('AUDCHF')

