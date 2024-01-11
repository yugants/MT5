from ForTime import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

# Live
audjpy = LiveTrade(['AUDJPY', 6.69582, 500, 200])

# Backtest
# audjpy = LiveTrade(['AUDJPY', 6.69582, 1000, 200])

audjpy.Caller()

