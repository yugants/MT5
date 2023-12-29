from Trend_Backtest  import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")
# For Live
audchf = LiveTrade(['AUDCHF', 11.19921, 50000, 200])
# For Backtesting
# audchf = LiveTrade(['AUDCHF', 11.19921, 100, 200])

# audchf.Caller('AUDCHF')
# For Live
audchf.Caller('AUDCHF')
