from Backtesting_5_Tradable  import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")
# For Live
audchf = LiveTrade(['AUDCHF', 11.19921, 10000, 200])
# For Backtesting
# audchf = LiveTrade(['AUDCHF', 11.19921, 100, 200])

audchf.Caller('AUDCHF')
# For Live
# audchf.Caller()
