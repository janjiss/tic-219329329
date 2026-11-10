import sys, os, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from astropy.timeseries import BoxLeastSquares
from wotan import flatten
from common import *
root, out = sys.argv[1], sys.argv[2]
qlp, spoc, tpf = find_files(root)
lcs = [load_spoc(spoc[0])] + [load_qlp(p, "sap") for p in qlp if "s0068" not in p]

def segs(t, gap=0.5):
    idx = np.where(np.diff(t) > gap)[0] + 1
    return np.split(np.arange(len(t)), idx)

def detrend(lc, mask=None, win=1.0, trim=0.0):
    t, f = lc["t"], lc["f"] / np.nanmedian(lc["f"])
    T, F, S = [], [], []
    for s in segs(t):
        tt, ff = t[s], f[s]
        if len(tt) < 50: continue
        if trim > 0:
            k = tt > tt[0] + trim
            tt, ff = tt[k], ff[k]
        ff2 = ff.copy()
        if mask is not None:
            m = mask(tt); ff2[m] = np.nan   # exclude in-transit from the trend
        fl, tr = flatten(tt, ff2, method="biweight", window_length=win, edge_cutoff=0.0, return_trend=True)
        # interpolate trend across masked cadences
        good = np.isfinite(tr)
        tr = np.interp(tt, tt[good], tr[good])
        T.append(tt); F.append(ff / tr); S.append(np.full(len(tt), lc["sector"]))
    return np.concatenate(T), np.concatenate(F), np.concatenate(S)

# pass 1: no mask; ramps trimmed 0.3 d at each segment start for QLP sectors
T, F, S = [], [], []
for lc in lcs:
    t, f, s = detrend(lc, win=1.0, trim=0.0 if lc["src"] == "SPOC" else 0.3)
    T.append(t); F.append(f); S.append(s)
t = np.concatenate(T); f = np.concatenate(F); s = np.concatenate(S)
# clip upward outliers only
sig = 1.4826 * np.nanmedian(np.abs(f - np.nanmedian(f)))
k = np.isfinite(f) & (f < 1 + 5 * sig)
t, f, s = t[k], f[k], s[k]
print("N points", len(t), "scatter ppm", sig * 1e6)

# BLS on the contiguous S102-104 block to get an unaliased period
kk = s >= 102
bls = BoxLeastSquares(t[kk], f[kk])
periods = np.exp(np.linspace(np.log(0.4), np.log(30), 60000))
durs = np.array([0.04, 0.06, 0.08, 0.1, 0.13, 0.16, 0.2])
res = bls.power(periods, durs, objective="snr")
i = np.argmax(res.power)
P0, T00, D0, dep0 = res.period[i], res.transit_time[i], res.duration[i], res.depth[i]
print("BLS (S102-104): P=%.5f d  T0=%.4f  dur=%.2f h  depth=%.0f ppm  SNR=%.1f" % (P0, T00, D0 * 24, dep0 * 1e6, res.depth_snr[i]))
# top peaks
order = np.argsort(res.power)[::-1]
seen = []
for j in order:
    p = res.period[j]
    if all(abs(p - q) / q > 0.02 for q in seen):
        seen.append(p); print("  peak P=%.4f  power=%.1f  depth=%.0f ppm" % (p, res.power[j], res.depth[j] * 1e6))
    if len(seen) >= 8: break

# refine with all sectors (fine grid around P0; baseline ~1050 d)
bls2 = BoxLeastSquares(t, f)
pf = np.linspace(P0 * (1 - 3e-3), P0 * (1 + 3e-3), 40001)
r2 = bls2.power(pf, [D0 * 0.8, D0, D0 * 1.2], objective="likelihood")
i2 = np.argmax(r2.power)
P1, T01, D1 = r2.period[i2], r2.transit_time[i2], r2.duration[i2]
print("BLS (all): P=%.6f d  T0=%.5f  dur=%.2f h  depth=%.0f ppm  SNR=%.1f" % (P1, T01, D1 * 24, r2.depth[i2] * 1e6, r2.depth_snr[i2]))
np.save(os.path.join(out, "bls_ephem.npy"), np.array([P1, T01, D1]))

fig, ax = plt.subplots(3, 1, figsize=(13, 11))
ax[0].plot(res.period, res.power, lw=0.6, color="k"); ax[0].set_xscale("log"); ax[0].set_xlabel("Period [d]"); ax[0].set_ylabel("BLS SNR"); ax[0].set_title("BLS, S102-104")
ax[1].plot(r2.period, r2.power, lw=0.6, color="k"); ax[1].set_xlabel("Period [d]"); ax[1].set_title("BLS fine grid, all sectors (alias comb)")
ph = ((t - T01 + 0.5 * P1) % P1) / P1 - 0.5
for sec, c in zip(np.unique(s), ["C0", "C1", "C2", "C3", "C4"]):
    m = s == sec; ax[2].plot(ph[m] * P1 * 24, f[m], ".", ms=2, color=c, alpha=0.5, label=f"S{int(sec)}")
ax[2].set_xlim(-8, 8); ax[2].set_ylim(0.982, 1.008); ax[2].legend(markerscale=5); ax[2].set_xlabel("Hours from mid-transit")
plt.tight_layout(); plt.savefig(os.path.join(out, "02_bls.png"), dpi=90)
np.savez(os.path.join(out, "lc_pass1.npz"), t=t, f=f, s=s)
