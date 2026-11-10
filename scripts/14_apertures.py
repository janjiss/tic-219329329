"""Depth vs photometric aperture and vs detrending; spatial profile of the dip; sector 105 timing."""
import sys, os, glob, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from scipy.optimize import least_squares
from common import *
root, cutdir, out = sys.argv[1], sys.argv[2], sys.argv[3]
best = np.load(os.path.join(out, "best_prior.npy")); T0, P, k, b = best[0], best[1], best[2], best[3]; a = aRs(np.exp(best[4]), P); u = (best[5], best[6])
shape = lambda tt: 1 - tmodel(tt, T0, P, k, b, a, u)
D0 = shape(np.array([T0]))[0]; T14 = 2.11 / 24
xx = np.linspace(-0.3 * T14, 0.3 * T14, 201); G = shape(T0 + xx).mean() / D0
print("template mid-transit depth %.0f ppm ; mean depth over the in-transit window = %.3f x mid depth" % (D0 * 1e6, G))
RA, DEC = 335.349583800419, -55.837437814740497
def measure(t, f, sector, win=1.0, trim=0.3):
    lc = dict(t=t, f=f, sector=sector)
    tt, ff, ss, tr = detrend(lc, P, T0, win=win, trim=trim)
    ph = ((tt - T0 + 0.5 * P) % P) - 0.5 * P
    oot = np.abs(ph) > 0.15; sig = 1.4826 * np.nanmedian(np.abs(ff[oot] - np.nanmedian(ff[oot])))
    kk = np.isfinite(ff) & (ff < 1 + 5 * sig) & (ff > 1 - 12 * sig); tt, ff, ph = tt[kk], ff[kk], ph[kk]
    A, sA = amp_fit(tt, ff, np.full(len(tt), sig), shape, np.abs(ph) < 0.3)
    return A * D0 * 1e6, sA * D0 * 1e6, tt, ff, sig
def wmean(v):
    v = np.array(v); wm = np.sum(v[:, 0] / v[:, 1] ** 2) / np.sum(1 / v[:, 1] ** 2); return wm, 1 / np.sqrt(np.sum(1 / v[:, 1] ** 2)), np.sum(((v[:, 0] - wm) / v[:, 1]) ** 2)

print("=== A. depth vs aperture, own photometry on FFI cutouts (sky = per-frame median of faint pixels; pipeline-good cadences only) ===")
aps = ["2x2 core", "3x3", "5x5"]
tab = {n: [] for n in aps}; s105 = None; own = []; aprows = []; detrows = []
qlp_files, _, _ = find_files(root)
for fn in sorted(glob.glob(os.path.join(cutdir, "tess-s*_astrocut.fits"))):
    with fits.open(fn) as h:
        d = h[1].data; t = np.array(d["TIME"], float); flux = np.array(d["FLUX"], float); q = np.array(d["QUALITY"], int); sector = h[0].header["SECTOR"]; w = WCS(h[2].header)
    if sector == 1: continue
    ok = np.isfinite(t) & (q == 0) & np.isfinite(flux).all(axis=(1, 2)); t, flux = t[ok], flux[ok]; n0 = len(t)
    qf = [p_ for p_ in qlp_files if "s%04d" % sector in p_]
    if qf:
        g = load_qlp(qf[0], "sap")["t"]; j = np.clip(np.searchsorted(g, t), 1, len(g) - 1)
        near = np.where(np.abs(t - g[j]) < np.abs(t - g[j - 1]), g[j], g[j - 1])
        # cutout time stamps carry the CCD-centre barycentric correction (off by up to ~1.5 min here);
        # keep pipeline-good cadences and adopt the pipeline's target-specific time stamps
        keep = np.abs(t - near) < 1.6 / 1440.; t, flux = near[keep], flux[keep]
    med = np.nanmedian(flux, axis=0); faint = med < np.percentile(med, 30)
    fsub = flux - np.nanmedian(flux[:, faint], axis=1)[:, None, None]
    px, py = [float(v) for v in w.all_world2pix(RA, DEC, 0)]; xi, yi = int(round(px)), int(round(py))
    def box(h_): m = np.zeros(med.shape, bool); m[yi - h_:yi + h_ + 1, xi - h_:xi + h_ + 1] = True; return m
    x2 = xi if px >= xi else xi - 1; y2 = yi if py >= yi else yi - 1
    core = np.zeros(med.shape, bool); core[y2:y2 + 2, x2:x2 + 2] = True
    masks = {"2x2 core": core, "3x3": box(1), "5x5": box(2)}
    line = "S%d (%d of %d frames):" % (sector, len(t), n0)
    for n in aps:
        lcf = fsub[:, masks[n]].sum(axis=1)
        dpt, err, tt, ff, sig = measure(t, lcf, sector); tab[n].append((dpt, err)); line += "  %s %.0f±%.0f (net %.0f e/s)" % (n, dpt, err, np.median(lcf))
        aprows.append(dict(sector=int(sector), aperture=n, depth_ppm=float(dpt), err_ppm=float(err), net_flux_e_s=float(np.median(lcf))))
        if sector == 105 and n == "3x3": s105 = (tt, ff, sig)
        if n == "3x3": own.append((tt, ff, np.full(len(tt), sig), np.full(len(tt), sector)))
    print(line)
np.savez(os.path.join(out, "lc_own3x3.npz"), t=np.concatenate([o[0] for o in own]), f=np.concatenate([o[1] for o in own]), e=np.concatenate([o[2] for o in own]), s=np.concatenate([o[3] for o in own]))
print("weighted means over 6 sectors:")
for n in aps:
    wm, we, c2 = wmean(tab[n]); print("   %-10s %.0f ± %.0f ppm  chi2=%.1f/5" % (n, wm, we, c2))

print("=== B. sector 105 (not used in the fit): transit times vs prediction ===")
tt, ff, sig = s105
ep = np.round((tt - T0) / P).astype(int); ph = ((tt - T0 + 0.5 * P) % P) - 0.5 * P; ocs = []
for n in np.unique(ep):
    m = (ep == n) & (np.abs(ph) < 0.3)
    if (np.abs(ph[m]) < 0.03).sum() < 15 or m.sum() < 150: continue
    rr = lambda th: (ff[m] - (1 - th[1] * (1 - tmodel(tt[m], T0 + n * P + th[0], P, k, b, a, u)))) / sig
    qf = least_squares(rr, [0.0, 1.0], x_scale=[1e-3, 0.1]); cov = np.linalg.inv(qf.jac.T @ qf.jac); sd = np.sqrt(np.diag(cov))
    ocs.append((n, qf.x[0] * 1440, sd[0] * 1440))
    print("   epoch %+d  BTJD %.4f  O-C = %+.1f ± %.1f min   depth = %.0f ± %.0f ppm" % (n, T0 + n * P + qf.x[0], qf.x[0] * 1440, sd[0] * 1440, qf.x[1] * D0 * 1e6, sd[1] * D0 * 1e6))
oc = np.array(ocs); wm = np.sum(oc[:, 1] / oc[:, 2] ** 2) / np.sum(1 / oc[:, 2] ** 2)
print("   S105 mean O-C = %+.1f ± %.1f min (N=%d)" % (wm, 1 / np.sqrt(np.sum(1 / oc[:, 2] ** 2)), len(oc)))

print("=== C. depth vs detrending / pipeline (mission light curves) ===")
qlp, spoc, tpf = find_files(root)
def run(lcs, win, label):
    vals = []
    for lc in lcs:
        dpt, err, *_ = measure(lc["t"], lc["f"], lc["sector"], win=win, trim=0.0 if lc["src"] == "SPOC" else 0.3); vals.append((dpt, err))
    wm, we, c2 = wmean(vals)
    print("   %-44s %.0f ± %.0f ppm   per sector: %s" % (label, wm, we, " ".join("%.0f" % x[0] for x in vals)))
    detrows.append(dict(label=label, depth_ppm=float(wm), err_ppm=float(we), per_sector=[float(x[0]) for x in vals]))
base = [load_spoc(spoc[0])] + [load_qlp(p, "sap") for p in qlp if "s0068" not in p]
for win in (0.5, 1.0, 2.0, 3.0): run(base, win, "SPOC S68 + QLP SAP, biweight %.1f d" % win)
run([load_qlp(p, "sap") for p in qlp], 1.0, "QLP SAP only (incl. S68)")
run([load_qlp(p, "det") for p in qlp], 1.0, "QLP DET_FLUX (pipeline detrended)")
run([load_spoc(spoc[0], "SAP_FLUX")], 1.0, "SPOC S68 SAP")
run([load_spoc(spoc[0])], 1.0, "SPOC S68 PDCSAP")
for col in ("DET_FLUX_SML", "DET_FLUX_LAG"):
    vals = []
    for p in qlp:
        with fits.open(p) as h:
            d = h[1].data; t = np.array(d["TIME"], float); q = np.array(d["QUALITY"], int); f = np.array(d[col], float); sec = h[0].header["SECTOR"]
        ok = np.isfinite(t) & np.isfinite(f) & (q == 0)
        dpt, err, *_ = measure(t[ok], f[ok], sec); vals.append((dpt, err))
    wm, we, c2 = wmean(vals)
    print("   %-44s %.0f ± %.0f ppm   per sector: %s" % ("QLP " + col, wm, we, " ".join("%.0f" % x[0] for x in vals)))
    detrows.append(dict(label="QLP " + col + (" (small aperture)" if col.endswith("SML") else " (large aperture)"), depth_ppm=float(wm), err_ppm=float(we), per_sector=[float(x[0]) for x in vals]))
# SPOC TPF (SPOC background model) with different apertures
with fits.open(tpf[0]) as h:
    d = h[1].data; t = np.array(d["TIME"], float); fl = np.array(d["FLUX"], float); q = np.array(d["QUALITY"], int)
ok = np.isfinite(t) & (q == 0) & np.isfinite(fl[:, 3:8, 3:8]).all(axis=(1, 2)); t, fl = t[ok], fl[ok]
m = np.nanmedian(fl, axis=0); yi, xi = np.unravel_index(np.nanargmax(m[3:8, 3:8]), (5, 5)); yi += 3; xi += 3
for hw, lab in ((1, "3x3"), (2, "5x5")):
    lcf = fl[:, yi - hw:yi + hw + 1, xi - hw:xi + hw + 1].sum(axis=(1, 2))
    dpt, err, *_ = measure(t, lcf, 68, trim=0.0); print("   %-44s %.0f ± %.0f ppm" % ("SPOC S68 pixel file, own %s aperture" % lab, dpt, err))
    detrows.append(dict(label="SPOC S68 pixel file, own %s aperture" % lab, depth_ppm=float(dpt), err_ppm=float(err), per_sector=[float(dpt)]))
import json
json.dump(dict(apertures=aprows, detrending=detrows), open(os.path.join(out, "aperture_depths.json"), "w"), indent=1)
