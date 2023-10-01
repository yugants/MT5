from Strategy import LiveTrade
import warnings

# Ignore all warnings (not recommended, use with caution)
warnings.filterwarnings("ignore")

audchf = LiveTrade(['AUDCHF', 10.92729, 24000])

audchf.Caller('AUDCHF')

