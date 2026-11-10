"""Out-of-transit phase variations (ellipsoidal / beaming / reflection) -> limit on companion mass."""
import sys, os, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common import *
root, out = sys.argv[1], sys.argv[2]
T0, P, k, b, a = np.load(os.path.join(out, "lsq.npy"))
qlp, spoc, tpf = find_files(root)
lcs = [load_spoc(spoc[0])] + [load_qlp(p, "sap") for p in qlp if "s0068" not in p]
T, F, G = [], [], []; g = 0
for lc in lcs:
    t, f = lc["t"], lc["f"] / np.nanmedian(lc["f"])
    for sidx in segs(t):
        tt, ff = t[sidx], f[sidx]
        if lc["src"] == "QLP":
            kk = tt > tt[0] + 1.0; tt, ff = tt[kk], ff[kk]
        if len(tt) < 500: continue
        sig = 1.4826 * np.median(np.abs(ff - np.median(ff))); kk = np.abs(ff - np.median(ff)) < 6 * sig
        T.append(tt[kk]); F.append(ff[kk]); G.append(np.full(kk.sum(), g)); g += 1
t = np.concatenate(T); f = np.concatenate(F); grp = np.concatenate(G)
print("segments:", g, "points:", len(t))

def fit(Ptry, order=3, T0_=T0):
    phi = ((t - T0_) / Ptry) % 1.0
    oot = np.abs(((t - T0 + 0.5 * P) % P) - 0.5 * P) > 0.08   # always mask the real transits
    cols = []
    for gi in range(g):
        m = grp == gi; x = np.zeros(len(t)); tm = (t - t[m].mean()) / 5.0
        for o in range(order + 1):
            c = np.zeros(len(t)); c[m] = tm[m] ** o; cols.append(c)
    npoly = len(cols)
    cols += [np.cos(2 * np.pi * phi), np.sin(2 * np.pi * phi), np.cos(4 * np.pi * phi), np.sin(4 * np.pi * phi)]
    A = np.array(cols).T[oot]; y = f[oot]
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ coef; s2 = np.var(r)
    cov = s2 * np.linalg.inv(A.T @ A)
    return coef[npoly:] * 1e6, np.sqrt(np.diag(cov))[npoly:] * 1e6, np.sqrt(s2) * 1e6
for order in (2, 3, 4):
    c, e, rms = fit(P, order)
    print("order %d: cos1=%.0f±%.0f  sin1(beaming)=%.0f±%.0f  cos2(-ellipsoidal)=%.0f±%.0f  sin2=%.0f±%.0f ppm (white-noise errors; rms=%.0f)" % (order, c[0], e[0], c[1], e[1], c[2], e[2], c[3], e[3], rms))
c, e, rms = fit(P, 3)
rng = np.random.default_rng(3); trial = []
for Ptry in rng.uniform(2.3, 5.0, 400):
    if abs(Ptry / P - 1) < 0.03 or abs(Ptry / (P/2) - 1) < 0.03: continue
    cc, _, _ = fit(Ptry, 3, T0_=T0 + rng.uniform(0, Ptry)); trial.append(cc)
trial = np.array(trial); emp = trial.std(axis=0)
print("empirical (red-noise) 1-sigma from %d random periods: cos1=%.0f sin1=%.0f cos2=%.0f sin2=%.0f ppm" % (len(trial), *emp))
ell, ell_e = -c[2], emp[2]; beam, beam_e = c[1], emp[1]
print("ELLIPSOIDAL semi-amp = %.0f ± %.0f ppm ; BEAMING semi-amp = %.0f ± %.0f ppm" % (ell, ell_e, beam, beam_e))
# mass limits (M*=1.10, a/Rs from fit, sin i ~ 1)
Ms = 1.10; alpha_ell = 0.15 * (15 + 0.5) * (1 + 0.3) / (3 - 0.5)
ell_per_q = alpha_ell * (1 / a) ** 3 * 1e6
up_ell = max(ell, 0) + 3 * ell_e
q_ell = up_ell / ell_per_q
print("  ellipsoidal: %.0f ppm per unit mass ratio -> 3-sigma upper limit %.0f ppm -> q < %.3f -> M_c < %.3f Msun = %.0f Mjup" % (ell_per_q, up_ell, q_ell, q_ell * Ms, q_ell * Ms * 1047.6))
up_b = max(beam, 0) + 3 * beam_e
K = up_b * 1e-6 * 2.998e5 / (4 * 0.9)   # km/s, alpha_beam ~0.9
# K = 28.4329 m/s * (m sin i / Mjup) * ((M*+m)/Msun)^(-2/3) * (P/yr)^(-1/3)
mj = K * 1e3 / (28.4329 * Ms ** (-2 / 3) * (P / 365.25) ** (-1 / 3))
print("  beaming: 3-sigma upper limit %.0f ppm -> K < %.1f km/s -> M_c < ~%.0f Mjup (%.3f Msun)" % (up_b, K, mj, mj / 1047.6))
