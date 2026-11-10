import sys, os, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from astropy.io import fits
from common import *
root, out = sys.argv[1], sys.argv[2]
qlp, spoc, tpf = find_files(root)
with fits.open(qlp[0]) as h:
    print(h[1].columns.names)
    for k in ("SECTOR","CAMERA","CCD","TESSMAG","RADIUS","TEFF","BESTAP","VERSION"):
        print(k, h[0].header.get(k), h[1].header.get(k))
with fits.open(spoc[0]) as h:
    for k in ("SECTOR","CAMERA","CCD","TESSMAG","CROWDSAP","FLFRCSAP","CDPP0_5","CDPP1_0","CDPP2_0","PDCMETHD","NUMBAND"):
        print("SPOC", k, h[0].header.get(k), h[1].header.get(k))
lcs = [load_spoc(spoc[0])] + [load_qlp(p, "sap") for p in qlp] 
fig, axs = plt.subplots(len(lcs), 1, figsize=(14, 2.6*len(lcs)))
for ax, lc in zip(axs, lcs):
    f = lc["f"]/np.nanmedian(lc["f"])
    ax.plot(lc["t"], f, ".", ms=1.5, color="k")
    lo, hi = np.nanpercentile(f, [0.2, 99.8]); ax.set_ylim(lo-0.002, hi+0.002)
    ax.set_title(f"S{lc['sector']} {lc['src']}  N={len(f)}  rms={np.nanstd(f)*1e6:.0f} ppm  MAD-rms={1.4826*np.nanmedian(np.abs(f-np.nanmedian(f)))*1e6:.0f} ppm", fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(out, "01_raw_lightcurves.png"), dpi=90)
