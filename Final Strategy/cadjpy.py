
from ForTime import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

cadjpy = LiveTrade(['CADJPY', 6.69582, 500, 200])

cadjpy.Caller()

