import warnings, sys, os; warnings.filterwarnings("ignore")
from astroquery.mast import Tesscut
from astropy.coordinates import SkyCoord
out = sys.argv[1]
c = SkyCoord(335.349583800419, -55.837437814740497, unit="deg")
for sec in (1, 68, 95, 102, 103, 104, 105):
    try:
        m = Tesscut.download_cutouts(coordinates=c, size=15, sector=sec, path=out, inflate=True)
        print(sec, list(m["Local Path"]), flush=True)
    except Exception as e:
        print(sec, "ERR", repr(e)[:300], flush=True)
