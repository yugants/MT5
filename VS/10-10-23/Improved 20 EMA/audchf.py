from Strategy_20 import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

audchf = LiveTrade(['AUDCHF', 10.92729, 24000])

audchf.Caller('AUDCHF')

