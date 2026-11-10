import sys, os, glob, warnings; warnings.filterwarnings("ignore")
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
cutdir, out = sys.argv[1], sys.argv[2]
T0, P, k, b, a = np.load(os.path.join(out, "lsq.npy"))
RA, DEC = 335.349583800419, -55.837437814740497
T14 = 2.11 / 24
# ---- Sector 102: what is the bright corner source, and does it dip at the transit ephemeris?
fn = glob.glob(os.path.join(cutdir, "tess-s0102*"))[0]
with fits.open(fn) as h:
    d = h[1].data; t = np.array(d["TIME"], float); flux = np.array(d["FLUX"], float); q = np.array(d["QUALITY"], int); w = WCS(h[2].header)
ok = np.isfinite(t) & (q == 0) & np.isfinite(flux).all(axis=(1, 2)); t, flux = t[ok], flux[ok]
med = np.nanmedian(flux, axis=0); faint = med < np.percentile(med, 30)
flux = flux - np.nanmedian(flux[:, faint], axis=1)[:, None, None]
ra_c, dec_c = w.all_pix2world(14, 0, 0)
print("S102 corner pixel (14,0) sky position: RA=%.5f Dec=%.5f ; median flux there=%.0f e/s vs target peak=%.0f e/s" % (ra_c, dec_c, med[0, 14] - np.median(med[faint]), med[8, 7] - np.median(med[faint])))
ph = ((t - T0 + 0.5 * P) % P) - 0.5 * P; ep = np.round((t - T0) / P).astype(int)
def depth_series(ap):
    lc = flux[:, ap[0], ap[1]].sum(axis=(1, 2)) if isinstance(ap[0], slice) else flux[:, ap[0], ap[1]]
    ds = []
    for n in np.unique(ep):
        m = ep == n; inn = m & (np.abs(ph) < 0.3 * T14)
        o1 = m & (ph < -0.7 * T14) & (ph > -2.2 * T14); o2 = m & (ph > 0.7 * T14) & (ph < 2.2 * T14)
        if inn.sum() < 6 or o1.sum() < 6 or o2.sum() < 6: continue
        oot = 0.5 * (lc[o1].mean() + lc[o2].mean()); ds.append((oot - lc[inn].mean(), oot))
    ds = np.array(ds); return ds
for name, ap in (("target 3x3", (slice(7, 10), slice(6, 9))), ("corner 2x2 (bright star wing)", (slice(0, 2), slice(13, 15)))):
    ds = depth_series(ap)
    dmean = ds[:, 0].mean(); derr = ds[:, 0].std() / np.sqrt(len(ds))
    print("  %-30s  dip = %.1f ± %.1f e/s  (%.1f sigma) ; fractional = %.0f ± %.0f ppm ; per-transit dips: %s" % (name, dmean, derr, dmean / derr, dmean / ds[:, 1].mean() * 1e6, derr / ds[:, 1].mean() * 1e6, np.round(ds[:, 0], 1)))
# ---- Sector 1
fn = glob.glob(os.path.join(cutdir, "tess-s0001*"))[0]
with fits.open(fn) as h:
    d = h[1].data; t = np.array(d["TIME"], float); flux = np.array(d["FLUX"], float); q = np.array(d["QUALITY"], int); w1 = WCS(h[2].header)
    print("S1 header: camera/ccd", h[0].header.get("CAMERA"), h[0].header.get("CCD"), "frames", len(t))
print("S1: finite time %d, quality==0 %d, all-finite frames %d, fraction NaN pixels %.2f" % (np.isfinite(t).sum(), (q == 0).sum(), np.isfinite(flux).all(axis=(1, 2)).sum(), np.mean(~np.isfinite(flux))))
print("S1: time range %.2f-%.2f, median cadence %.1f min" % (np.nanmin(t), np.nanmax(t), np.nanmedian(np.diff(t)) * 1440))
px, py = [float(v) for v in w1.all_world2pix(RA, DEC, 0)]
print("S1 target pixel in cutout: (%.2f, %.2f) ; median image row sums:" % (px, py))
m1 = np.nanmedian(flux, axis=0); print(np.round(m1[5:10, 5:10], 0))
print("S1 quality flag values:", np.unique(q)[:10])
