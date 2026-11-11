"""Look for the transit in ASAS-SN ground-based photometry (V and g bands, 2014-2025).

usage: 22_asassn_fold.py <asassn_lightcurve.csv> <out_dir>
"""
import sys, os, json, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from common import tmodel, aRs

src, out = sys.argv[1], sys.argv[2]
best = np.load(os.path.join(out, "best_free_own.npy")); T0b, P, k, b = best[:4]; a = aRs(np.exp(best[4]), P)
T0 = 2457000.0 + T0b
LD = {"TESS": (best[5], best[6]), "V": (0.47, 0.24), "g": (0.60, 0.18)}     # Claret-like quadratic coefficients for ~6000 K, log g 4.3
d = pd.read_csv(src)
print("rows:", len(d), "| quality flags:", d["quality"].value_counts().to_dict())
d = d[(d["quality"] == "G") & np.isfinite(d["mag"]) & (d["mag_err"] < 0.05) & (d["mag"] > 11.5) & (d["mag"] < 14.5)].copy()
star = SkyCoord(335.349583800419, -55.837437814740497, unit="deg")
tt = Time(d["jd"].values, format="jd", scale="utc", location=EarthLocation.from_geocentric(0, 0, 0, unit=u.m))
d["bjd"] = (tt.tdb + tt.light_travel_time(star, "barycentric")).jd
norb = (d["bjd"].min() - T0) / P
print("good rows:", len(d), "| span %.0f-%.0f (BJD-2450000) | ephemeris extrapolated up to %.0f orbits: timing uncertainty %.1f min" % (d.bjd.min() - 2450000, d.bjd.max() - 2450000, abs(norb), np.hypot(0.00039, abs(norb) * 3.4e-6) * 1440))
d["ph"] = ((d["bjd"] - T0 + 0.5 * P) % P) - 0.5 * P
# per-camera normalisation with a slow running median (in-transit points excluded from the trend)
d["f"] = np.nan; d["e"] = np.nan
for cam, g in d.groupby("camera"):
    g = g.sort_values("bjd"); t = g["bjd"].values; m = g["mag"].values; oot = np.abs(g["ph"].values) > 0.08
    trend = np.array([np.median(m[oot & (np.abs(t - ti) < 30)]) if (oot & (np.abs(t - ti) < 30)).sum() >= 8 else np.median(m[oot]) for ti in t])
    f = 10 ** (-0.4 * (m - trend)); sig = 1.4826 * np.median(np.abs(f[oot] - np.median(f[oot])))
    keep = np.abs(f - 1) < 4 * sig
    d.loc[g.index[keep], "f"] = f[keep]; d.loc[g.index[keep], "e"] = sig
    print("   camera %s (%s): %4d points, scatter %.2f%%" % (cam, g["phot_filter"].iloc[0], keep.sum(), sig * 100))
d = d[np.isfinite(d["f"])]

def shape_for(band):
    return lambda t_: 1 - tmodel(t_, T0, P, k, b, a, LD[band], exp=90 / 86400., ss=1)
depth_T = shape_for("TESS")(np.array([T0]))[0]
res = {}
rng = np.random.default_rng(4)
def amp(t_, f_, e_, shp, shift=0.0):
    x = shp(t_ - shift); w = 1 / e_ ** 2; s = np.sum(w * x * x)
    return (np.sum(w * x * (1 - f_)) / s, 1 / np.sqrt(s)) if s > 0 else (np.nan, np.nan)
print("expected mid-transit depth for a planet on the target: TESS %.0f ppm" % (depth_T * 1e6))
for band, sel in (("V", d["phot_filter"] == "V"), ("g", d["phot_filter"] == "g"), ("V+g", np.ones(len(d), bool))):
    g = d[sel]; shp = shape_for("g" if band != "V" else "V"); D = shp(np.array([T0]))[0]
    A, sA = amp(g["bjd"].values, g["f"].values, g["e"].values, shp)
    null = np.array([amp(g["bjd"].values, g["f"].values, g["e"].values, shp, s)[0] for s in rng.uniform(0.12 * P, 0.88 * P, 500)])
    semp = np.nanstd(null); nin = int((np.abs(g["ph"]) < 0.044).sum())
    res[band] = dict(n=int(len(g)), n_in_transit=nin, expected_depth_ppm=float(D * 1e6), measured_depth_ppm=float(A * D * 1e6), err_formal_ppm=float(sA * D * 1e6), err_empirical_ppm=float(semp * D * 1e6),
                     significance=float(A / semp), ratio_to_expected=float(A), ratio_err=float(semp), null_mean_ppm=float(np.nanmean(null) * D * 1e6))
    print("%-4s %4d points (%3d in transit): depth %5.0f +/- %4.0f ppm (formal +/- %.0f) = %.1f sigma ; expected for a planet on target %.0f ppm ; ratio %.2f +/- %.2f" % (
        band, len(g), nin, A * D * 1e6, semp * D * 1e6, sA * D * 1e6, A / semp, D * 1e6, A, semp))
# where in phase is the best dip? (amplitude of the same template slid around the orbit)
shp = shape_for("g"); shifts = np.linspace(-0.5 * P, 0.5 * P, 241)
curve = np.array([amp(d["bjd"].values, d["f"].values, d["e"].values, shp, s) for s in shifts]); snr = curve[:, 0] / res["V+g"]["ratio_err"]
i = int(np.nanargmax(snr)); print("deepest template fit anywhere in the orbit: phase offset %+.3f of a period (%.1f sigma); at the predicted phase: %.1f sigma" % (shifts[i] / P, snr[i], res["V+g"]["significance"]))
res["scan_best_phase"] = float(shifts[i] / P); res["scan_best_sigma"] = float(snr[i])
json.dump(res, open(os.path.join(out, "asassn_results.json"), "w"), indent=1)
# arrays for the website: half-hour bins per band, the model curves, and the phase scan
site = dict(results=res, scan=[[round(float(x_ / P), 4), round(float(y_), 3)] for x_, y_ in zip(shifts, snr)], bands={})
for band in ("g", "V"):
    gb = d[d["phot_filter"] == band]; hb = gb["ph"].values * 24; edges_ = np.linspace(-8, 8, 33); idx_ = np.digitize(hb, edges_) - 1; rows_ = []
    for j in range(32):
        mk = idx_ == j
        if mk.sum() > 3: rows_.append([round(float(0.5 * (edges_[j] + edges_[j + 1])), 3), round(float((gb["f"].values[mk].mean() - 1) * 100), 4), round(float(gb["f"].values[mk].std() / np.sqrt(mk.sum()) * 100), 4), int(mk.sum())])
    xx_ = np.linspace(-8, 8, 321)
    site["bands"][band] = dict(bins=rows_, model=[[round(float(a_), 3), round(float(-v_ * 100), 4)] for a_, v_ in zip(xx_, shape_for(band)(T0 + xx_ / 24))])
json.dump(site, open(os.path.join(out, "asassn_site.json"), "w"))
d[["bjd", "f", "e", "phot_filter", "camera", "ph"]].to_csv(os.path.join(out, "asassn_detrended.csv"), index=False)

fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
for a_, (band, col) in zip(ax[:2], (("g", "C0"), ("V", "C2"))):
    g = d[d["phot_filter"] == band]; h = g["ph"].values * 24
    a_.plot(h, g["f"], ".", ms=2, color="0.75")
    edges = np.linspace(-8, 8, 33); c = 0.5 * (edges[1:] + edges[:-1]); idx = np.digitize(h, edges) - 1
    bm = np.array([g["f"].values[idx == j].mean() if (idx == j).sum() > 3 else np.nan for j in range(32)]); be = np.array([g["f"].values[idx == j].std() / np.sqrt((idx == j).sum()) if (idx == j).sum() > 3 else np.nan for j in range(32)])
    a_.errorbar(c, bm, be, fmt="o", ms=4, color=col); xx = np.linspace(-8, 8, 400); a_.plot(xx, 1 - shape_for(band)(T0 + xx / 24), "r-", lw=1.3)
    a_.set_xlim(-8, 8); a_.set_ylim(0.975, 1.02); a_.set_xlabel("Hours from predicted mid-transit"); a_.set_title("ASAS-SN %s band: %.0f +/- %.0f ppm (%.1f sigma)" % (band, res[band]["measured_depth_ppm"], res[band]["err_empirical_ppm"], res[band]["significance"]))
ax[2].plot(shifts / P, snr, "k-"); ax[2].axvline(0, color="r", ls=":"); ax[2].set_xlabel("Phase offset of the template (fraction of a period)"); ax[2].set_ylabel("Depth / empirical error"); ax[2].set_title("Same template slid around the orbit (V+g)")
plt.tight_layout(); plt.savefig(os.path.join(out, "07_asassn.png"), dpi=90)
