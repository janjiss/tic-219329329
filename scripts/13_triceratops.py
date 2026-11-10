import sys, os, warnings, time as _t; warnings.filterwarnings("ignore")
import numpy as np
from triceratops import triceratops as tr
out, nrun, N, tpf_path = sys.argv[1], int(sys.argv[2]), int(float(sys.argv[3])), sys.argv[4]
folded = sys.argv[5] if len(sys.argv) > 5 else "tri_folded.txt"; tdepth = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0087; tag = sys.argv[7] if len(sys.argv) > 7 else "mission"
ph, fb, eb = np.loadtxt(os.path.join(out, folded)).T
ap = np.loadtxt(os.path.join(out, "tri_aperture_s68.txt")).astype(int)
P = 3.481585
tg = tr.target(ID=219329329, sectors=np.array([68]), search_radius=10)
print(tg.stars[["ID", "Tmag", "ra", "dec", "mass", "rad", "Teff", "plx", "sep (arcsec)", "PA (E of N)"]].head(12).to_string(), flush=True)
# TESScut no longer ships the FFI pixel-origin keywords TRICERATOPS reads, so place the stars on the
# detector with the SPOC pixel file's WCS and its physical pixel origin instead.
from astropy.io import fits
from astropy.wcs import WCS
with fits.open(tpf_path) as h:
    w = WCS(h[2].header); c0, r0 = h[2].header["CRVAL1P"], h[2].header["CRVAL2P"]
xy = np.array(w.all_world2pix(np.c_[tg.stars["ra"].values, tg.stars["dec"].values], 0))
tg.pix_coords = [np.c_[xy[:, 0] + c0, xy[:, 1] + r0]]
print("target FFI pixel (col,row): %.2f, %.2f ; aperture pixels:" % tuple(tg.pix_coords[0][0]), ap.tolist(), flush=True)
tg.calc_depths(tdepth=tdepth, all_ap_pixels=[ap])
print(tg.stars[["ID", "Tmag", "sep (arcsec)", "fluxratio", "tdepth"]].head(12).to_string(), flush=True)
res = []; allp = []
for i in range(nrun):
    t0 = _t.time()
    tg.calc_probs(time=ph, flux_0=fb, flux_err_0=float(np.median(eb)), P_orb=P, N=N, exptime=0.4 / 120, nsamples=5, verbose=0, parallel=True)
    res.append((tg.FPP, tg.NFPP))
    pp = tg.probs.sort_values("prob", ascending=False)
    allp.append(dict(zip(tg.probs["scenario"], tg.probs["prob"])))
    print("run %2d: FPP=%.5f NFPP=%.1e (%.0f s) | " % (i + 1, tg.FPP, tg.NFPP, _t.time() - t0) + "  ".join("%s=%.4f" % (a, b) for a, b in zip(pp["scenario"], pp["prob"]) if b > 5e-4), flush=True)
    if i == 0:
        pr = tg.probs.copy(); cols = [c for c in ["ID", "scenario", "M_s", "R_s", "P_orb", "inc", "b", "ecc", "R_p", "M_EB", "R_EB", "prob"] if c in pr.columns]
        print(pr[cols].sort_values("prob", ascending=False).to_string(), flush=True)
        pr.to_csv(os.path.join(out, "triceratops_probs_%s.csv" % tag), index=False)
r = np.array(res)
np.savetxt(os.path.join(out, "triceratops_runs_%s.txt" % tag), r)
import pandas as pd
dfp = pd.DataFrame(allp); dfp.to_csv(os.path.join(out, "triceratops_scenarios_%s.csv" % tag), index=False)
print("mean scenario probabilities over runs:"); print((dfp.mean().sort_values(ascending=False)).round(5).to_string())
print("median FPP = %.5f ; 16-84%% = %.5f - %.5f" % (np.median(r[:, 0]), *np.percentile(r[:, 0], [16, 84])))
print("FPP = %.5f ± %.5f ; NFPP = %.2e ± %.2e over %d runs" % (r[:, 0].mean(), r[:, 0].std(), r[:, 1].mean(), r[:, 1].std(), len(r)))
