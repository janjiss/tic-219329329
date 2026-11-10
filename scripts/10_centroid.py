"""Difference-image centroid test on TESScut FFI cutouts (and the SPOC TPF)."""
import sys, os, glob, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from scipy.optimize import least_squares
cutdir, out = sys.argv[1], sys.argv[2]
T0, P, k, b, a = np.load(os.path.join(out, "lsq.npy"))
RA, DEC = 335.349583800419, -55.837437814740497
T14 = 2.11 / 24
files = sorted(glob.glob(os.path.join(cutdir, "tess-s*_astrocut.fits")))

def gauss(p, X, Y):
    A, x0, y0, s, c = p
    return A * np.exp(-((X - x0) ** 2 + (Y - y0) ** 2) / (2 * s ** 2)) + c
def fitpsf(img, x0, y0, hw=3):
    xi, yi = int(round(x0)), int(round(y0))
    sub = img[yi - hw:yi + hw + 1, xi - hw:xi + hw + 1]
    Y, X = np.mgrid[yi - hw:yi + hw + 1, xi - hw:xi + hw + 1]
    r = least_squares(lambda p: (gauss(p, X, Y) - sub).ravel(), [sub.max(), x0, y0, 0.9, np.median(sub)])
    return r.x[1], r.x[2]

fig, axs = plt.subplots(2, len(files), figsize=(3.3 * len(files), 6.6))
allres = []; dump = []
for col, fn in enumerate(files):
    with fits.open(fn) as h:
        d = h[1].data; t = np.array(d["TIME"], float); flux = np.array(d["FLUX"], float); q = np.array(d["QUALITY"], int)
        sector = h[0].header["SECTOR"]
        w = WCS(h[2].header)
    ok = np.isfinite(t) & (q == 0) & np.isfinite(flux).all(axis=(1, 2))
    t, flux = t[ok], flux[ok]
    # per-frame background: median of the faintest 30% pixels (ranked on the median image)
    med = np.nanmedian(flux, axis=0); faint = med < np.percentile(med, 30)
    flux = flux - np.nanmedian(flux[:, faint], axis=1)[:, None, None]
    px, py = [float(v) for v in w.all_world2pix(RA, DEC, 0)]
    ph = ((t - T0 + 0.5 * P) % P) - 0.5 * P; ep = np.round((t - T0) / P).astype(int)
    diffs, oots = [], []
    for n in np.unique(ep):
        m = ep == n
        inn = m & (np.abs(ph) < 0.3 * T14)
        o1 = m & (ph < -0.7 * T14) & (ph > -2.2 * T14); o2 = m & (ph > 0.7 * T14) & (ph < 2.2 * T14)
        nmin = 2 if sector < 27 else 6
        if inn.sum() < nmin or o1.sum() < nmin or o2.sum() < nmin: continue
        oot = 0.5 * (flux[o1].mean(axis=0) + flux[o2].mean(axis=0))
        diffs.append(oot - flux[inn].mean(axis=0)); oots.append(oot)
    diffs = np.array(diffs); oots = np.array(oots)
    if len(diffs) < 2:
        print('S%d: only %d usable transits, skipped' % (sector, len(diffs))); continue
    D = diffs.mean(axis=0); O = oots.mean(axis=0); Derr = diffs.std(axis=0) / np.sqrt(len(diffs))
    ox, oy = fitpsf(O, px, py); dx, dy = fitpsf(D, px, py)
    # bootstrap over transits
    rng = np.random.default_rng(5); bs = []
    for _ in range(300):
        idx = rng.integers(0, len(diffs), len(diffs))
        try:
            bx, by = fitpsf(diffs[idx].mean(axis=0), px, py); bs.append((bx, by))
        except Exception: pass
    bs = np.array(bs); ex, ey = bs.std(axis=0)
    offx, offy = (dx - ox) * 21, (dy - oy) * 21
    off = np.hypot(offx, offy); offe = np.hypot(ex, ey) * 21
    yi, xi = int(round(py)), int(round(px))
    snr_peak = D[yi, xi] / Derr[yi, xi]
    peak = np.unravel_index(np.argmax(D), D.shape)
    # depth in a 3x3 aperture on target
    ap = (slice(yi - 1, yi + 2), slice(xi - 1, xi + 2))
    depth = D[ap].sum() / O[ap].sum()
    print("S%d: N transits=%d  target pix=(%.2f,%.2f)  OOT centroid=(%.2f,%.2f)  DIFF centroid=(%.2f,%.2f)  offset=%.1f ± %.1f arcsec (%.1f sigma)  brightest diff pixel=(%d,%d)  3x3 depth=%.0f ppm  peak-pixel S/N=%.1f" % (sector, len(diffs), px, py, ox, oy, dx, dy, off, offe, off / offe, peak[1], peak[0], depth * 1e6, snr_peak))
    allres.append((sector, offx, offy, ex * 21, ey * 21, len(diffs)))
    dump.append(dict(sector=int(sector), n_transits=int(len(diffs)), target_px=[px, py], oot_centroid=[float(ox), float(oy)], diff_centroid=[float(dx), float(dy)], offset_arcsec=float(off), offset_err_arcsec=float(offe), depth_3x3_inwindow_ppm=float(depth * 1e6), oot=np.round(O, 2).tolist(), diff=np.round(D, 3).tolist()))
    a0, a1 = axs[0, col], axs[1, col]
    a0.imshow(O, origin="lower", cmap="viridis"); a0.plot(px, py, "r+", ms=12); a0.set_title(f"S{sector} out-of-transit", fontsize=9)
    v = np.nanmax(np.abs(D)); a1.imshow(D, origin="lower", cmap="RdBu_r", vmin=-v, vmax=v); a1.plot(px, py, "k+", ms=12); a1.plot(dx, dy, "gx", ms=9)
    a1.set_title(f"S{sector} difference (OOT-in)\noffset {off:.1f}±{offe:.1f}\"", fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(out, "04_centroid.png"), dpi=85)
import json
json.dump(dump, open(os.path.join(out, "centroid_results.json"), "w"))
r = np.array(allres)
wx = np.sum(r[:, 1] / r[:, 3] ** 2) / np.sum(1 / r[:, 3] ** 2); wy = np.sum(r[:, 2] / r[:, 4] ** 2) / np.sum(1 / r[:, 4] ** 2)
sx = 1 / np.sqrt(np.sum(1 / r[:, 3] ** 2)); sy = 1 / np.sqrt(np.sum(1 / r[:, 4] ** 2))
print("COMBINED offset (pixel axes differ per sector, so combine magnitudes conservatively):")
print("   mean |offset| = %.1f arcsec ; per-sector errors ~%.1f arcsec ; 3-sigma localisation radius ~ %.1f arcsec" % (np.mean(np.hypot(r[:, 1], r[:, 2])), np.median(np.hypot(r[:, 3], r[:, 4])), 3 * np.median(np.hypot(r[:, 3], r[:, 4])) / np.sqrt(len(r))))
