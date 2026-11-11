"""TRICERATOPS with two extra measurements folded into every eclipsing-binary scenario.

TRICERATOPS only fits the light curve around the transit. For scenarios where a star (not a planet)
does the eclipsing, the rest of the orbit carries more information that was measured separately:

  1. No secondary eclipse.  Measured -196 +/- 130 ppm at phase 0.5 (own photometry, red-noise scaled).
     Used conservatively as 0 +/- 130 ppm, i.e. no credit is taken for the negative value.
     For eccentric orbits whose secondary eclipse falls away from phase 0.5 the all-phase scan is
     used instead, as 0 +/- 180 ppm. Orbits whose secondary falls outside phases 0.1-0.9 get no penalty.
     The predicted box-averaged depth is taken as 0.6 x TRICERATOPS' maximum secondary depth.
  2. No ellipsoidal (tidal) variation.  Measured 5 +/- 54 ppm (scripts/09_phasecurve.py).
     Predicted semi-amplitude = ALPHA * (M_EB / M_host) * (R_host / a)^3 * sin(i)^2 * (host share of the light),
     with ALPHA = 1.0 (theory gives about 1.2-1.3 for these stars, so this under-predicts on purpose).

Both enter as Gaussian terms added to the light-curve chi-square of each sampled binary.
Planet scenarios are untouched: a planet predicts essentially zero for both.
Scenarios at twice the period (twins) are also untouched.

usage: 21_triceratops_phase.py <out_dir> <n_runs> <N> <tpf.fits> <folded.txt> <tdepth> <tag>
"""
import sys, os, warnings, time as _t; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from triceratops import triceratops as tr
import triceratops.marginal_likelihoods as ml
import triceratops.likelihoods as lk

out, nrun, N, tpf_path, folded, tdepth, tag = sys.argv[1], int(sys.argv[2]), int(float(sys.argv[3])), sys.argv[4], sys.argv[5], float(sys.argv[6]), sys.argv[7]
SIG_SEC_05, SIG_SEC_SCAN, BOX_FRACTION = 130e-6, 180e-6, 0.6
A_OBS, SIG_A, ALPHA = 5e-6, 54e-6, 1.0
HALF_BOX_PHASE = 0.0125
G_, MSUN, RSUN = ml.G, ml.Msun, ml.Rsun
diag = {}

def lnL_EB_p_plus(time, flux, sigma, R_EB, EB_fluxratio, P_orb, inc, a, R_s, u1, u2, ecc, argp,
                  companion_fluxratio, companion_is_host=False, exptime=0.00139, nsamples=20):
    caller = sys._getframe(1); name = caller.f_code.co_name.replace("lnZ_", "")
    inc_deg = np.array(inc, dtype=float)          # the simulator converts `inc` to radians in place
    model, secdepth = lk.simulate_EB_transit_p(time, R_EB, EB_fluxratio, P_orb, inc, a, R_s, u1, u2, ecc, argp,
                                               companion_fluxratio, companion_is_host, exptime, nsamples)
    sec = secdepth[:, 0]
    n = R_EB.shape[0]
    res = np.full(n, np.inf)
    ok = sec < 1.5 * sigma                          # TRICERATOPS' own hard cut, kept
    chi = 0.5 * np.sum((flux - model[ok]) ** 2 / sigma ** 2, axis=1)
    # --- secondary eclipse term
    dphi = np.abs(2 / np.pi * ecc[ok] * np.cos(np.radians(argp[ok])))
    sig_sec = np.where(dphi <= HALF_BOX_PHASE, SIG_SEC_05, SIG_SEC_SCAN)
    pen_sec = 0.5 * (BOX_FRACTION * sec[ok] / sig_sec) ** 2
    pen_sec[dphi > 0.4] = 0.0
    # --- ellipsoidal term
    m_eb = None
    loc = caller.f_locals
    if "masses" in loc and "mask" in loc and np.count_nonzero(loc["mask"]) == n:
        m_eb = np.asarray(loc["masses"])[loc["mask"]][ok]
    pen_ell = np.zeros(ok.sum())
    if m_eb is not None:
        m_tot = 4 * np.pi ** 2 * a[ok] ** 3 / (G_ * (P_orb[ok] * 86400.0) ** 2) / MSUN
        m_host = np.clip(m_tot - m_eb, 0.05, None)
        f_comp = companion_fluxratio[ok] / (1 - companion_fluxratio[ok]); f_eb = EB_fluxratio[ok] / (1 - EB_fluxratio[ok])
        share = (f_comp if companion_is_host else 1.0) / (1.0 + f_comp + f_eb)
        a_pred = ALPHA * (m_eb / m_host) * (R_s[ok] * RSUN / a[ok]) ** 3 * np.sin(np.radians(inc_deg[ok])) ** 2 * share
        pen_ell = 0.5 * ((a_pred - A_OBS) / SIG_A) ** 2 - 0.5 * (A_OBS / SIG_A) ** 2
    res[ok] = chi + pen_sec + pen_ell
    # diagnostics: likelihood-weighted effect of the extra terms on this scenario's evidence
    if ok.sum():
        w = np.exp(-(chi - chi.min()))
        d = diag.setdefault(name, dict(calls=0, factor=[], sec=[], ell=[], had_mass=m_eb is not None))
        d["calls"] += 1; d["factor"].append(float(np.sum(w * np.exp(-(pen_sec + pen_ell))) / np.sum(w)))
        d["sec"].append(float(np.sum(w * sec[ok]) / np.sum(w) * 1e6))
        if m_eb is not None: d["ell"].append(float(np.sum(w * a_pred) / np.sum(w) * 1e6))
    return res

ml.lnL_EB_p = lnL_EB_p_plus

ph, fb, eb = np.loadtxt(os.path.join(out, folded)).T
ap = np.loadtxt(os.path.join(out, "tri_aperture_s68.txt")).astype(int)
P = 3.481585
tg = tr.target(ID=219329329, sectors=np.array([68]), search_radius=10)
from astropy.io import fits
from astropy.wcs import WCS
with fits.open(tpf_path) as h:
    w = WCS(h[2].header); c0, r0 = h[2].header["CRVAL1P"], h[2].header["CRVAL2P"]
xy = np.array(w.all_world2pix(np.c_[tg.stars["ra"].values, tg.stars["dec"].values], 0))
tg.pix_coords = [np.c_[xy[:, 0] + c0, xy[:, 1] + r0]]
tg.calc_depths(tdepth=tdepth, all_ap_pixels=[ap])
res = []; allp = []
for i in range(nrun):
    t0 = _t.time()
    tg.calc_probs(time=ph, flux_0=fb, flux_err_0=float(np.median(eb)), P_orb=P, N=N, exptime=0.4 / 120, nsamples=5, verbose=0, parallel=True)
    res.append((tg.FPP, tg.NFPP)); pp = tg.probs.sort_values("prob", ascending=False)
    allp.append(dict(zip(tg.probs["scenario"], tg.probs["prob"])))
    print("run %2d: FPP=%.5f NFPP=%.1e (%.0f s) | " % (i + 1, tg.FPP, tg.NFPP, _t.time() - t0) + "  ".join("%s=%.4f" % (a_, b_) for a_, b_ in zip(pp["scenario"], pp["prob"]) if b_ > 5e-4), flush=True)
    if i == 0: tg.probs.to_csv(os.path.join(out, "triceratops_probs_%s.csv" % tag), index=False)
r = np.array(res)
np.savetxt(os.path.join(out, "triceratops_runs_%s.txt" % tag), r)
dfp = pd.DataFrame(allp); dfp.to_csv(os.path.join(out, "triceratops_scenarios_%s.csv" % tag), index=False)
print("mean scenario probabilities over runs:"); print(dfp.mean().sort_values(ascending=False).round(5).to_string())
print("effect of the extra terms per eclipsing-binary scenario (likelihood-weighted):")
for k, d in diag.items():
    print("   %-4s evidence multiplied by %.3g ; typical predicted secondary depth %.0f ppm%s" % (k, np.mean(d["factor"]), np.mean(d["sec"]), (" ; ellipsoidal %.0f ppm" % np.mean(d["ell"])) if d["ell"] else " ; ellipsoidal term not applied"))
print("median FPP = %.5f ; 16-84%% = %.5f - %.5f ; mean = %.5f +/- %.5f ; NFPP = %.1e" % (np.median(r[:, 0]), *np.percentile(r[:, 0], [16, 84]), r[:, 0].mean(), r[:, 0].std(), r[:, 1].mean()))
