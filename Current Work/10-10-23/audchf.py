from Strategy import LiveTrade
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

audchf = LiveTrade(['AUDCHF', 10.92729, 50000])

audchf.Caller('AUDCHF')

