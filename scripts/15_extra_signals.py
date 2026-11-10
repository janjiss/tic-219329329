"""Search for additional periodic dips after masking the candidate, and characterise stellar variability."""
import sys, os, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from astropy.timeseries import BoxLeastSquares, LombScargle
from common import *
root, out = sys.argv[1], sys.argv[2]
best = np.load(os.path.join(out, "best_prior.npy")); T0, P = best[0], best[1]
d = np.load(os.path.join(out, "lc_final.npz")); t, f, e, s = d["t"], d["f"], d["e"], d["s"]
ph = ((t - T0 + 0.5 * P) % P) - 0.5 * P
m = np.abs(ph) > 1.5 / 24
t2, f2, e2, s2 = t[m], f[m], e[m], s[m]
print("points after masking the candidate: %d (of %d)" % (len(t2), len(t)))
def bls_run(tt, ff, ee, pmin, pmax, n, label):
    bls = BoxLeastSquares(tt, ff, ee)
    periods = np.exp(np.linspace(np.log(pmin), np.log(pmax), n))
    r = bls.power(periods, [0.03, 0.05, 0.08, 0.12, 0.18], objective="snr")
    pw = r.power; 
    # remove slow trend of the spectrum with a running median before computing SDE
    from scipy.ndimage import median_filter
    base = median_filter(pw, size=2001, mode="nearest"); pr = pw - base
    sde = (pr - np.median(pr)) / (1.4826 * np.median(np.abs(pr - np.median(pr))))
    order = np.argsort(sde)[::-1]; seen = []; outp = []
    for j in order:
        p = r.period[j]
        if all(abs(p - q) / q > 0.03 for q in seen):
            seen.append(p); outp.append((p, sde[j], r.depth[j] * 1e6, r.depth_snr[j], r.duration[j] * 24, r.transit_time[j]))
        if len(seen) >= 5: break
    print(label)
    for o in outp: print("   P=%8.4f d  SDE=%5.1f  depth=%5.0f ppm  depth S/N=%4.1f  dur=%.1f h  (P/Pcand=%.3f)" % (o[0], o[1], o[2], o[3], o[4], o[0] / P))
    return r, sde, outp
# all sectors: long gaps make the fine structure heavily aliased, so also search the 78-d contiguous block
r1, sde1, o1 = bls_run(t2[s2 >= 102], f2[s2 >= 102], e2[s2 >= 102], 0.4, 39.0, 80000, "BLS on residuals, S102-104 (78 d contiguous):")
r0, sde0, o0 = bls_run(t2[s2 == 68], f2[s2 == 68], e2[s2 == 68], 0.4, 13.0, 40000, "BLS on residuals, S68:")
# injection sanity: what depth would have been found?  noise per 2-h bin over N transits
sig = np.median(e2); npt_2h = 2 * 3600 / 200
for Ptest in (1.0, 5.0, 10.0, 20.0):
    ntr = (78.0 / Ptest); snr_per_ppm = np.sqrt(ntr * npt_2h * 0.8) / (sig * 1e6)
    print("   sensitivity S102-104: 7.1-sigma depth for P=%4.1f d, 2-h duration ~ %.0f ppm (~%.1f R_earth)" % (Ptest, 7.1 / snr_per_ppm, np.sqrt(7.1 / snr_per_ppm * 1e-6) * 1.21 * 109.1))

print("--- stellar variability (un-flattened light curves, candidate transits masked) ---")
qlp, spoc, tpf = find_files(root)
lcs = [load_spoc(spoc[0])] + [load_qlp(p, "sap") for p in qlp if "s0068" not in p]
fig, ax = plt.subplots(2, 1, figsize=(12, 8))
for lc in lcs:
    tt, ff = lc["t"], lc["f"] / np.nanmedian(lc["f"])
    T, F = [], []
    for sidx in segs(tt):
        a, b = tt[sidx], ff[sidx]
        if lc["src"] == "QLP":
            k = a > a[0] + 1.0; a, b = a[k], b[k]
        if len(a) < 300: continue
        # remove a per-orbit linear trend only (keeps periodic variability < ~10 d)
        c = np.polyfit(a - a.mean(), b, 1); b = b - np.polyval(c, a - a.mean()) + 1
        T.append(a); F.append(b)
    tt = np.concatenate(T); ff = np.concatenate(F)
    php = ((tt - T0 + 0.5 * P) % P) - 0.5 * P; k = (np.abs(php) > 1.5 / 24); sg = 1.4826 * np.median(np.abs(ff - np.median(ff))); k &= np.abs(ff - 1) < 5 * sg
    tt, ff = tt[k], ff[k]
    freq = np.linspace(1 / 13.0, 24.0, 60000)
    ls = LombScargle(tt, ff); pw = ls.power(freq); j = np.argmax(pw)
    amp = np.sqrt(pw[j] * 2 * np.var(ff)) * 1e6   # approx semi-amplitude
    fap = ls.false_alarm_probability(pw[j])
    # 30-min binned rms as an activity/noise indicator
    nb = int((tt[-1] - tt[0]) / (0.5 / 24)); idx = ((tt - tt[0]) / (0.5 / 24)).astype(int); bm = np.array([ff[idx == i].mean() for i in np.unique(idx) if (idx == i).sum() >= 5])
    print("   S%d: strongest LS peak P=%.3f d (f=%.3f /d), semi-amp ~%.0f ppm, FAP=%.1e ; point rms %.0f ppm, 30-min binned rms %.0f ppm ; power at Porb: %.4f, at Porb/2: %.4f (peak %.4f)" % (
        lc["sector"], 1 / freq[j], freq[j], amp, fap, sg * 1e6, np.std(bm) * 1e6, ls.power(np.array([1 / P]))[0], ls.power(np.array([2 / P]))[0], pw[j]))
    ax[1].plot(1 / freq, pw, lw=0.6, label="S%d" % lc["sector"])
ax[0].plot(r1.period, sde1, "k-", lw=0.5); ax[0].set_xscale("log"); ax[0].axvline(P, color="r", ls=":", lw=1); ax[0].set_title("BLS on residuals after masking the candidate (S102-104); red = candidate period"); ax[0].set_ylabel("SDE"); ax[0].set_xlabel("Period [d]")
ax[1].set_xscale("log"); ax[1].axvline(P, color="r", ls=":"); ax[1].axvline(P / 2, color="r", ls=":"); ax[1].legend(); ax[1].set_xlabel("Period [d]"); ax[1].set_ylabel("LS power"); ax[1].set_title("Lomb-Scargle of un-flattened light curves (red = Porb, Porb/2)")
plt.tight_layout(); plt.savefig(os.path.join(out, "05_extra_signals.png"), dpi=85)
