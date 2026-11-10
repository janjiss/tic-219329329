"""Repeat odd/even, secondary-eclipse and timing tests on the independent FFI photometry (6 sectors) and plot it."""
import sys, os, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from common import *
out = sys.argv[1]
best = np.load(os.path.join(out, "best_prior_own.npy")); T0, P, k, b = best[:4]; a = aRs(np.exp(best[4]), P); u = (best[5], best[6])
d = np.load(os.path.join(out, "lc_own3x3.npz")); t, f, e, s = d["t"], d["f"], d["e"], d["s"]
shape = lambda tt, T0_=T0: 1 - tmodel(tt, T0_, P, k, b, a, u); D0 = shape(np.array([T0]))[0]
ph = ((t - T0 + 0.5 * P) % P) - 0.5 * P; ep = np.round((t - T0) / P).astype(int); win = np.abs(ph) < 0.3
Ao, so = amp_fit(t, f, e, shape, win & (ep % 2 != 0)); Ae, se = amp_fit(t, f, e, shape, win & (ep % 2 == 0))
print("own photometry, %d points, 6 sectors; model mid-transit depth %.0f ppm" % (len(t), D0 * 1e6))
print("ODD/EVEN: odd=%.0f±%.0f  even=%.0f±%.0f ppm  -> %.1f sigma" % (Ao * D0 * 1e6, so * D0 * 1e6, Ae * D0 * 1e6, se * D0 * 1e6, (Ao - Ae) / np.hypot(so, se)))
dur = 2.1 / 24; phi = ((t - T0) % P) / P; phases = np.linspace(0.1, 0.9, 321); dep = []; sig = []
for p0 in phases:
    inb = np.abs(phi - p0) < dur / P / 2; oob = (np.abs(phi - p0) > dur / P / 2 * 1.5) & (np.abs(phi - p0) < dur / P / 2 * 6)
    dep.append(np.mean(f[oob]) - np.mean(f[inb])); sig.append(np.sqrt(np.var(f[inb]) / inb.sum() + np.var(f[oob]) / oob.sum()))
dep = np.array(dep); sig = np.array(sig); i05 = np.argmin(np.abs(phases - 0.5)); rn = np.std(dep / sig)
print("SECONDARY @0.5: %.0f ± %.0f ppm (white) ; red-noise factor %.2f -> %.0f ± %.0f ppm ; 3-sigma upper limit %.0f ppm" % (dep[i05] * 1e6, sig[i05] * 1e6, rn, dep[i05] * 1e6, sig[i05] * rn * 1e6, max(dep[i05], 0) * 1e6 + 3 * sig[i05] * rn * 1e6))
rows = []
for n in np.unique(ep):
    m = (ep == n) & (np.abs(ph) < 0.3)
    if (np.abs(ph[m]) < 0.03).sum() < 15 or m.sum() < 150: continue
    q = least_squares(lambda th: (f[m] - (1 - th[1] * shape(t[m], T0 + n * P + th[0]))) / e[m], [0.0, 1.0], x_scale=[1e-3, 0.1])
    cov = np.linalg.inv(q.jac.T @ q.jac); sd = np.sqrt(np.diag(cov)); rows.append((n, T0 + n * P + q.x[0], q.x[0] * 1440, sd[0] * 1440, q.x[1] * D0 * 1e6, sd[1] * D0 * 1e6, np.median(s[m])))
rows = np.array(rows)
# linear ephemeris from individual times (weighted)
w = 1 / rows[:, 3] ** 2; A = np.c_[np.ones(len(rows)), rows[:, 0]]; cov = np.linalg.inv(A.T @ (A * w[:, None])); coef = cov @ (A.T @ (w * rows[:, 1]))
res = (rows[:, 1] - A @ coef) * 1440; chi2 = np.sum((res / rows[:, 3]) ** 2)
print("PER-TRANSIT: %d transits over %.0f d ; linear ephemeris from individual times: T0=%.5f±%.5f  P=%.7f±%.7f ; timing chi2=%.1f/%d ; rms %.1f min (median err %.1f)" % (len(rows), rows[-1, 1] - rows[0, 1], coef[0], np.sqrt(cov[0, 0]) / 1440, coef[1], np.sqrt(cov[1, 1]) / 1440, chi2, len(rows) - 2, np.std(res), np.median(rows[:, 3])))
dw = np.average(rows[:, 4], weights=1 / rows[:, 5] ** 2); print("             depth chi2=%.1f/%d ; rms %.0f ppm (median err %.0f)" % (np.sum(((rows[:, 4] - dw) / rows[:, 5]) ** 2), len(rows) - 1, np.std(rows[:, 4]), np.median(rows[:, 5])))
np.save(os.path.join(out, "per_transit_own.npy"), rows)

fig, ax = plt.subplots(2, 2, figsize=(13, 8.5))
h = ph * 24; a0 = ax[0, 0]
a0.plot(h, f, ".", ms=1, color="0.8")
edges = np.linspace(-6, 6, 73); c = 0.5 * (edges[1:] + edges[:-1]); idx = np.digitize(h, edges) - 1
bm = np.array([f[idx == i].mean() for i in range(72)]); be = np.array([f[idx == i].std() / np.sqrt((idx == i).sum()) for i in range(72)])
a0.errorbar(c, bm, be, fmt="o", ms=3, color="k", label="10-min bins"); xx = np.linspace(-0.25, 0.25, 600); a0.plot(xx * 24, 1 - shape(T0 + xx), "r-", lw=1.5, label="model (Rp/Rs=%.3f, b=%.2f)" % (k, b))
a0.set_xlim(-6, 6); a0.set_ylim(0.985, 1.006); a0.set_xlabel("Hours from mid-transit"); a0.set_ylabel("Relative flux"); a0.set_title("Independent FFI photometry, 6 sectors (S68-S105), P=%.6f d" % P); a0.legend(loc="lower left", fontsize=8)
a1 = ax[0, 1]
for par, col, lab in ((1, "C3", "odd epochs"), (0, "C0", "even epochs")):
    mk = (ep % 2 != 0) if par else (ep % 2 == 0); idx2 = np.digitize(h[mk], np.linspace(-4, 4, 41)) - 1
    a1.errorbar(np.linspace(-3.9, 3.9, 40), [f[mk][idx2 == i].mean() for i in range(40)], [f[mk][idx2 == i].std() / np.sqrt((idx2 == i).sum()) for i in range(40)], fmt="o", ms=3, color=col, label=lab)
a1.legend(fontsize=8); a1.set_title("Odd vs even: %.0f±%.0f vs %.0f±%.0f ppm" % (Ao * D0 * 1e6, so * D0 * 1e6, Ae * D0 * 1e6, se * D0 * 1e6)); a1.set_xlabel("Hours from mid-transit")
a2 = ax[1, 0]
for sec, col in zip(np.unique(rows[:, 6]), ["C0", "C1", "C2", "C3", "C4", "C5"]):
    mk = rows[:, 6] == sec; a2.errorbar(rows[mk, 0], res[mk], rows[mk, 3], fmt="o", ms=3, color=col, label="S%d" % sec)
a2.axhline(0, color="k", lw=0.8); a2.set_xlabel("Transit epoch"); a2.set_ylabel("O - C [min]"); a2.set_title("Transit timing residuals (chi2 = %.0f for %d dof)" % (chi2, len(rows) - 2)); a2.legend(fontsize=7, ncol=3)
a3 = ax[1, 1]
idx3 = np.digitize(phi, np.linspace(0, 1, 101)) - 1; pm_ = np.array([f[idx3 == i].mean() for i in range(100)]); pe_ = np.array([f[idx3 == i].std() / np.sqrt((idx3 == i).sum()) for i in range(100)])
a3.errorbar(np.linspace(0.005, 0.995, 100), (pm_ - 1) * 1e6, pe_ * 1e6, fmt="o", ms=3, color="k"); a3.set_ylim(-1500, 1500); a3.axvline(0.5, color="r", ls=":")
a3.set_xlabel("Orbital phase"); a3.set_ylabel("ppm"); a3.set_title("Full orbit: no secondary eclipse at phase 0.5")
plt.tight_layout(); plt.savefig(os.path.join(out, "06_independent_photometry.png"), dpi=90)
