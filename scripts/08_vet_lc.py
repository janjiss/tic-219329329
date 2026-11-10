"""Light-curve based vetting: odd/even, per-sector depth, per-transit times, secondary, phase curve, apertures."""
import sys, os, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, batman, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from astropy.io import fits
from common import *
root, out = sys.argv[1], sys.argv[2]
P, T0, D = np.load(os.path.join(out, "bls_ephem.npy"))
t, f, e, s = build(root, P, T0)
ph = ((t - T0 + 0.5 * P) % P) - 0.5 * P
ep = np.round((t - T0) / P).astype(int)

pm = batman.TransitParams(); pm.ecc, pm.w, pm.limb_dark, pm.u = 0., 90., "quadratic", [0.32, 0.25]
def tmodel(tt, T0_, P_, k, b, a):
    pm.t0, pm.per, pm.rp, pm.a = T0_, P_, k, a
    pm.inc = np.degrees(np.arccos(min(b / a, 1.0)))
    return batman.TransitModel(pm, tt, supersample_factor=3, exp_time=200 / 86400.).light_curve(pm)
# global LSQ fit for shape template
near = np.abs(ph) < 0.3
def res(th): return (f[near] - tmodel(t[near], *th)) / e[near]
r = least_squares(res, [T0, P, 0.11, 0.85, 8.2], x_scale=[1e-3, 1e-5, 0.01, 0.05, 0.5])
T0f, Pf, kf, bf, af = r.x
print("LSQ: T0=%.5f P=%.6f k=%.4f b=%.3f a/Rs=%.2f  chi2red=%.3f" % (T0f, Pf, kf, bf, af, np.sum(r.fun**2) / (near.sum() - 5)))
ph = ((t - T0f + 0.5 * Pf) % Pf) - 0.5 * Pf; ep = np.round((t - T0f) / Pf).astype(int)
tmpl = lambda tt, T0_=T0f: 1 - tmodel(tt, T0_, Pf, kf, bf, af)   # positive dip template
full_depth = tmpl(np.array([T0f]))[0]
print("model mid-transit depth: %.0f ppm" % (full_depth * 1e6))

def scale_fit(mask):
    """linear amplitude of the template (1 = global depth) with error"""
    x = tmpl(t[mask]); y = 1 - f[mask]; w = 1 / e[mask] ** 2
    A = np.sum(w * x * y) / np.sum(w * x * x); sA = 1 / np.sqrt(np.sum(w * x * x)); return A, sA
win = np.abs(ph) < 0.3
# --- odd / even
Ao, so = scale_fit(win & (ep % 2 != 0)); Ae, se = scale_fit(win & (ep % 2 == 0))
print("ODD/EVEN depth: odd=%.0f±%.0f ppm  even=%.0f±%.0f ppm  diff=%.1f sigma" % (Ao*full_depth*1e6, so*full_depth*1e6, Ae*full_depth*1e6, se*full_depth*1e6, (Ao-Ae)/np.hypot(so, se)))
# --- per sector
print("PER-SECTOR depth:")
secd = {}
for sec in np.unique(s):
    A, sA = scale_fit(win & (s == sec)); secd[int(sec)] = (A*full_depth*1e6, sA*full_depth*1e6)
    print("   S%d: %.0f ± %.0f ppm  (N transits=%d)" % (sec, A*full_depth*1e6, sA*full_depth*1e6, len(np.unique(ep[win & (s == sec) & (np.abs(ph) < 0.04)]))))
vals = np.array([v[0] for v in secd.values()]); errs = np.array([v[1] for v in secd.values()])
wm = np.sum(vals / errs**2) / np.sum(1 / errs**2); chi2 = np.sum(((vals - wm) / errs) ** 2)
print("   weighted mean %.0f ppm; chi2=%.1f for %d dof" % (wm, chi2, len(vals) - 1))
# --- per-transit depth and timing
print("PER-TRANSIT:")
rows = []
for n in np.unique(ep):
    m = (ep == n) & (np.abs(ph) < 0.3)
    if (np.abs(ph[m]) < 0.03).sum() < 15 or m.sum() < 150: continue
    def rr(th): return (f[m] - (1 - th[1] * tmpl(t[m], T0f + n * Pf + th[0]) )) / e[m]
    q = least_squares(rr, [0.0, 1.0], x_scale=[1e-3, 0.1])
    J = q.jac; cov = np.linalg.inv(J.T @ J); sd = np.sqrt(np.diag(cov))
    rows.append((n, T0f + n * Pf + q.x[0], q.x[0] * 1440, sd[0] * 1440, q.x[1] * full_depth * 1e6, sd[1] * full_depth * 1e6, int(np.median(s[m]))))
rows = np.array(rows)
print("   N transits fit: %d ; depth rms %.0f ppm, median err %.0f ppm ; O-C rms %.1f min, median err %.1f min" % (len(rows), np.std(rows[:, 4]), np.median(rows[:, 5]), np.std(rows[:, 2]), np.median(rows[:, 3])))
print("   depth chi2 = %.1f / %d ; timing chi2 = %.1f / %d" % (np.sum(((rows[:, 4] - np.average(rows[:, 4], weights=1/rows[:, 5]**2)) / rows[:, 5])**2), len(rows) - 1, np.sum((rows[:, 2] / rows[:, 3])**2), len(rows) - 2))
np.save(os.path.join(out, "per_transit.npy"), rows)
# --- secondary eclipse scan: box of transit duration at every phase
dur = 2.2 / 24
phases = np.linspace(0.1, 0.9, 321); dep = []; sig = []
phi = ((t - T0f) % Pf) / Pf
for p0 in phases:
    inb = np.abs(phi - p0) < dur / Pf / 2
    oob = (np.abs(phi - p0) > dur / Pf / 2 * 1.5) & (np.abs(phi - p0) < dur / Pf / 2 * 6)
    d = np.mean(f[oob]) - np.mean(f[inb]); sd = np.sqrt(np.var(f[inb]) / inb.sum() + np.var(f[oob]) / oob.sum())
    dep.append(d); sig.append(sd)
dep = np.array(dep); sig = np.array(sig)
i05 = np.argmin(np.abs(phases - 0.5))
print("SECONDARY @0.5: depth = %.0f ± %.0f ppm (%.1f sigma); 3-sigma upper limit %.0f ppm" % (dep[i05]*1e6, sig[i05]*1e6, dep[i05]/sig[i05], 3*sig[i05]*1e6))
j = np.argmax(dep / sig)
print("   most significant dip elsewhere: phase %.3f depth %.0f ± %.0f ppm (%.1f sigma); scan rms of S/N = %.2f" % (phases[j], dep[j]*1e6, sig[j]*1e6, dep[j]/sig[j], np.std(dep/sig)))
# also test double the period: are alternate events consistent (done by odd/even). Half period: any dip at phase 0.5 (done).

# --- plots
fig, ax = plt.subplots(2, 3, figsize=(17, 9))
def binned(x, y, nb, lo, hi):
    edges = np.linspace(lo, hi, nb + 1); c = 0.5 * (edges[1:] + edges[:-1]); idx = np.digitize(x, edges) - 1
    m = np.array([np.mean(y[idx == i]) if (idx == i).sum() > 3 else np.nan for i in range(nb)])
    sd = np.array([np.std(y[idx == i]) / np.sqrt((idx == i).sum()) if (idx == i).sum() > 3 else np.nan for i in range(nb)]); return c, m, sd
a = ax[0, 0]; h = ph * 24
a.plot(h, f, ".", ms=1, color="0.75"); c, m, sd = binned(h, f, 64, -8, 8); a.errorbar(c, m, sd, fmt="o", ms=3, color="k")
tt = np.linspace(-0.34, 0.34, 800); a.plot(tt * 24, tmodel(T0f + tt, T0f, Pf, kf, bf, af), "r-", lw=1.5)
a.set_xlim(-8, 8); a.set_ylim(0.985, 1.006); a.set_title("All transits folded, P=%.5f d" % Pf); a.set_xlabel("hours")
a = ax[0, 1]
for par, col, lab in ((1, "C3", "odd"), (0, "C0", "even")):
    mk = (ep % 2 == par) if par == 0 else (ep % 2 != 0)
    c, m, sd = binned(h[mk], f[mk], 40, -5, 5); a.errorbar(c, m, sd, fmt="o", ms=3, color=col, label=lab)
a.legend(); a.set_title("Odd vs even: %.0f±%.0f vs %.0f±%.0f ppm" % (Ao*full_depth*1e6, so*full_depth*1e6, Ae*full_depth*1e6, se*full_depth*1e6)); a.set_xlabel("hours")
a = ax[0, 2]
c, m, sd = binned(phi, f, 100, 0, 1); a.errorbar(c, (m - 1) * 1e6, sd * 1e6, fmt="o", ms=3, color="k"); a.set_ylim(-1200, 1200); a.axvline(0.5, color="r", ls=":")
a.set_title("Full phase (binned), secondary @0.5: %.0f±%.0f ppm" % (dep[i05]*1e6, sig[i05]*1e6)); a.set_xlabel("phase"); a.set_ylabel("ppm")
a = ax[1, 0]; a.errorbar(rows[:, 1], rows[:, 4], rows[:, 5], fmt="o", ms=3, color="k"); a.axhline(full_depth * 1e6, color="r"); a.set_title("Per-transit depth [ppm]"); a.set_xlabel("BTJD")
a = ax[1, 1]; a.errorbar(rows[:, 1], rows[:, 2], rows[:, 3], fmt="o", ms=3, color="k"); a.axhline(0, color="r"); a.set_title("Per-transit O-C [min]"); a.set_xlabel("BTJD")
a = ax[1, 2]; a.plot(phases, dep / sig, "k-"); a.axhline(3, color="r", ls=":"); a.axhline(-3, color="r", ls=":"); a.set_title("Box-dip S/N vs phase (secondary scan)"); a.set_xlabel("phase")
plt.tight_layout(); plt.savefig(os.path.join(out, "03_vetting_lc.png"), dpi=90)
np.save(os.path.join(out, "lsq.npy"), r.x)
