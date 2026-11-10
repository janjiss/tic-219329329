import sys, os, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, batman, emcee
from common import *
root, out, mode = sys.argv[1], sys.argv[2], sys.argv[3]   # mode: free | prior
P0, T00, D0 = np.load(os.path.join(out, "bls_ephem.npy"))
tag = mode
if len(sys.argv) > 4:      # fit a pre-built light curve instead of the mission products
    d = np.load(sys.argv[4]); t, f, e, s = d["t"], d["f"], d["e"], d["s"]; tag = mode + "_" + sys.argv[5]
else:
    t, f, e, s = build(root, P0, T00)
    np.savez(os.path.join(out, "lc_final.npz"), t=t, f=f, e=e, s=s)
ph = ((t - T00 + 0.5 * P0) % P0) - 0.5 * P0
k = np.abs(ph) < 0.3
t, f, e, s = t[k], f[k], e[k], s[k]
print("fit points:", len(t), "per-sector sigma ppm:", {int(x): round(float(e[s == x][0] * 1e6)) for x in np.unique(s)})
tref = T00 + round((np.median(t) - T00) / P0) * P0   # epoch near data centre to decorrelate P,T0
RHO, RHO_E = 0.62, 0.15

pm = batman.TransitParams()
pm.ecc, pm.w, pm.limb_dark = 0.0, 90.0, "quadratic"
def model(th, tt):
    T0, P, k_, b, lrho, u1, u2 = th
    a = aRs(np.exp(lrho), P)
    pm.t0, pm.per, pm.rp, pm.a = T0, P, k_, a
    pm.inc = np.degrees(np.arccos(min(b / a, 1.0))); pm.u = [u1, u2]
    m = batman.TransitModel(pm, tt, supersample_factor=3, exp_time=200 / 86400.0)
    return m.light_curve(pm)
def lnp(th):
    T0, P, k_, b, lrho, u1, u2 = th
    if not (0.01 < k_ < 1.0 and 0 <= b < 1 + k_ and np.log(0.01) < lrho < np.log(30) and 0 < u1 < 1 and -0.3 < u2 < 1 and u1 + u2 < 1): return -np.inf
    if abs(P - P0) > 0.01 or abs(T0 - tref) > 0.05: return -np.inf
    lp = -0.5 * ((u1 - 0.32) / 0.1) ** 2 - 0.5 * ((u2 - 0.25) / 0.1) ** 2
    if mode == "prior":
        rho = np.exp(lrho); lp += -0.5 * ((rho - RHO) / RHO_E) ** 2 + lrho  # Gaussian in rho (Jacobian for sampling in ln rho)
    return lp
def lnl(th):
    lp = lnp(th)
    if not np.isfinite(lp): return -np.inf
    m = model(th, t)
    return lp - 0.5 * np.sum(((f - m) / e) ** 2)
nd, nw = 7, 40
p0 = np.array([tref, P0, 0.11, 0.85, np.log(0.6), 0.32, 0.25])
pos = p0 + np.array([1e-4, 1e-6, 5e-3, 2e-2, 0.05, 0.03, 0.03]) * np.random.default_rng(1).normal(size=(nw, nd))
sam = emcee.EnsembleSampler(nw, nd, lnl)
sam.run_mcmc(pos, 6000, progress=False)
ch = sam.get_chain(discard=2500, thin=5, flat=True)
lnlk = sam.get_log_prob(discard=2500, thin=5, flat=True)
np.save(os.path.join(out, f"chain_{tag}.npy"), ch)
try: print("autocorr:", np.round(sam.get_autocorr_time(tol=0), 0))
except Exception as ex: print("acorr err", ex)
names = ["T0", "P", "k", "b", "lnrho", "u1", "u2"]
def q(x): 
    a, b_, c = np.percentile(x, [16, 50, 84]); return b_, b_ - a, c - b_
print(f"=== mode={tag}  tref={tref:.5f} ===")
for i, n in enumerate(names):
    print("  %-6s %.6f -%.6f +%.6f" % ((n,) + q(ch[:, i])))
T0c, Pc, kc, bc, lr = ch[:, 0], ch[:, 1], ch[:, 2], ch[:, 3], ch[:, 4]
rho = np.exp(lr); a = aRs(rho, Pc)
rs = np.random.default_rng(2).normal(1.21, 0.06, len(kc))
rp_j = kc * rs * 9.7318   # R_sun -> R_jup (nominal equatorial)
inc = np.degrees(np.arccos(bc / a))
t14 = Pc / np.pi * np.arcsin(np.clip(np.sqrt(np.clip((1 + kc) ** 2 - bc ** 2, 0, None)) / (a * np.sin(np.radians(inc))), 0, 1)) * 24
graz = np.mean(bc > 1 - kc)
for n, x in [("rho*", rho), ("a/Rs", a), ("inc", inc), ("T14_h", t14), ("Rp_Rjup", rp_j), ("depth_ppm(k^2)", kc ** 2 * 1e6)]:
    print("  %-14s %.4f -%.4f +%.4f" % ((n,) + q(x)))
print("  Rp 95%% upper: %.2f Rjup ; 99.7%%: %.2f ; P(grazing)=%.3f ; P(Rp>2 Rjup)=%.4f" % (np.percentile(rp_j, 95), np.percentile(rp_j, 99.7), graz, np.mean(rp_j > 2.0)))
best = ch[np.argmax(lnlk)]
m = model(best, t); chi2 = np.sum(((f - m) / e) ** 2)
print("  best:", np.round(best, 6), "chi2=%.1f N=%d red=%.3f" % (chi2, len(t), chi2 / (len(t) - nd)))
np.save(os.path.join(out, f"best_{tag}.npy"), np.append(best, tref))
