import warnings, sys, time; warnings.filterwarnings("ignore")
from astropy.coordinates import SkyCoord
import astropy.units as u
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier
c = SkyCoord(335.349583800419, -55.837437814740497, unit="deg")
print("=== SIMBAD (10 arcsec, Harvard mirror) ===")
try:
    sb = Simbad(); sb.server = "simbad.harvard.edu"; r = sb.query_region(c, radius=10 * u.arcsec)
    print("no SIMBAD object" if r is None or len(r) == 0 else r)
except Exception as e: print("SIMBAD ERR", repr(e)[:200])
V = lambda: Vizier(row_limit=3, vizier_server="vizier.cfa.harvard.edu", columns=["*", "+_r"])
fixed = {
 "B/vsx/vsx": ("AAVSO Variable Star Index (aggregates ASAS-SN, Gaia, TESS, WASP... variables)", 10),
 "I/358/vclassre": ("Gaia DR3 variability classification", 3), "I/358/veb": ("Gaia DR3 eclipsing binaries", 3),
 "II/366/catalog": ("ASAS-SN variable stars", 10), "J/ApJS/258/16": ("TESS eclipsing binaries (Prsa+ 2022)", 10),
 "B/wds/wds": ("Washington Double Star catalogue", 10), "III/283/ravedr6": ("RAVE DR6 spectroscopy", 3),
 "J/MNRAS/506/150": ("GALAH DR3 spectroscopy", 3), "IX/47/2rxs": ("ROSAT 2RXS X-ray sources", 40),
 "II/335/galex_ais": ("GALEX UV", 4), "J/ApJS/254/39": ("TESS Objects of Interest (Guerrero+ 2021)", 10),
 "IV/39/tic82": ("TESS Input Catalog 8.2", 3),
}
print("=== VizieR targeted catalogues ===")
for cat, (desc, rad) in fixed.items():
    for attempt in range(3):
        try:
            res = V().query_region(c, radius=rad * u.arcsec, catalog=cat)
            n = sum(len(t) for t in res)
            print("  %-18s %-78s r<%2d\": %s" % (cat, desc, rad, "NO MATCH" if n == 0 else "%d row(s)" % n))
            if n and cat != "IV/39/tic82":
                for t in res: print("       ", {k: str(t[0][k])[:24] for k in t.colnames[:16]})
            if n and cat == "IV/39/tic82":
                t = res[0]; print("       ", {k: str(t[0][k])[:24] for k in t.colnames if k in ("TIC", "Tmag", "Teff", "logg", "Rad", "Mass", "rho", "Lum", "Dist", "Disp", "LClass", "RUWE", "NumCont", "ContRatio", "[M/H]", "EBV")})
            break
        except Exception as e:
            if attempt == 2: print("  %-18s ERR %s" % (cat, type(e).__name__))
            time.sleep(3)
print("=== VizieR catalogues found by keyword (TESS/ground-based transit candidates, eclipsing binaries) ===")
found = {}
for kw in ("TESS planet candidates", "TESS transit candidates full frame", "TESS eclipsing binaries", "transiting planet candidates WASP", "HATSouth candidates", "NGTS candidates", "TESS variable stars southern"):
    for attempt in range(3):
        try:
            cl = Vizier(vizier_server="vizier.cfa.harvard.edu").find_catalogs(kw, max_catalogs=60)
            for k, v in cl.items(): found[k] = " ".join(str(v.description).split())[:80]
            break
        except Exception as e:
            time.sleep(3)
print("  catalogues to check:", len(found))
hits = 0; errs = 0; keys = list(found)
for i in range(0, len(keys), 25):
    chunk = keys[i:i + 25]
    for attempt in range(3):
        try:
            res = V().query_region(c, radius=5 * u.arcsec, catalog=chunk)
            for t in res:
                hits += 1; print("  MATCH", t.meta.get("name"), "|", " ".join(str(t.meta.get("description", "")).split())[:90]); print("       ", {k: str(t[0][k])[:24] for k in t.colnames[:14]})
            break
        except Exception as e:
            if attempt == 2: errs += 1
            time.sleep(3)
print("  matches within 5 arcsec: %d ; failed chunks: %d" % (hits, errs))
