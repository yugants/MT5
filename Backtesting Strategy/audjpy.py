from Trend_Backtest import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

# Live
audjpy = LiveTrade(['AUDJPY', 6.69582, 10000, 200])

# Backtest
# audjpy = LiveTrade(['AUDJPY', 6.69582, 1000, 200])

audjpy.Caller('AUDJPY')

