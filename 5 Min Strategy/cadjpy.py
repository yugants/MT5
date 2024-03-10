
from Backtesting_5_Tradable import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

cadjpy = LiveTrade(['CADJPY', 6.69582, 50000, 200])

cadjpy.Caller('CADJPY')

