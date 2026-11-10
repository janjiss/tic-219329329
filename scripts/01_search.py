import warnings; warnings.filterwarnings("ignore")
import lightkurve as lk
from astroquery.mast import Tesscut
from astropy.coordinates import SkyCoord
import astropy.units as u

tic = "TIC 219329329"
sr = lk.search_lightcurve(tic)
print("=== light curves ===")
print(sr.table["mission","year","author","exptime","target_name","distance"].to_pandas().to_string() if len(sr) else "none")
tp = lk.search_targetpixelfile(tic)
print("=== TPFs ===")
print(tp.table["mission","year","author","exptime","target_name","distance"].to_pandas().to_string() if len(tp) else "none")
c = SkyCoord(335.349583800419, -55.837437814740497, unit="deg")
print("=== FFI sectors (TESScut) ===")
print(Tesscut.get_sectors(coordinates=c).to_pandas().to_string())
