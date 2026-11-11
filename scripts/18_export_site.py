"""Export every data product the evidence website shows, plus CSV/JSON twins for download.

usage: 18_export_site.py <out_dir> <site_dir> <scripts_dir> <mast_dir> <report.md>
"""
import sys, os, json, csv, glob, shutil, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from astropy.timeseries import BoxLeastSquares
from common import *

out, site, scripts_dir, mast_dir, report = sys.argv[1:6]
D = os.path.join(site, "data"); os.makedirs(D, exist_ok=True)
os.makedirs(os.path.join(site, "assets"), exist_ok=True)
E = {}

def wcsv(name, header, rows):
    with open(os.path.join(D, name), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(header); w.writerows(rows)
def R(x, n=4):
    return None if x is None or not np.isfinite(x) else round(float(x), n)
def binned(x, y, e, edges):
    idx = np.digitize(x, edges) - 1; rows = []
    for i in range(len(edges) - 1):
        m = idx == i
        if m.sum() < 5: continue
        w = 1 / e[m] ** 2
        rows.append((0.5 * (edges[i] + edges[i + 1]), np.sum(w * y[m]) / np.sum(w), 1 / np.sqrt(np.sum(w)), int(m.sum())))
    return rows

# ---------------------------------------------------------------- ephemerides and models
bo = np.load(os.path.join(out, "best_free_own.npy")); T0o, Po, ko, bbo = bo[:4]; ao = aRs(np.exp(bo[4]), Po); uo = (bo[5], bo[6])
bm = np.load(os.path.join(out, "best_prior.npy")); T0m, Pm = bm[0], bm[1]
ch_own = np.load(os.path.join(out, "chain_free_own.npy")); ch_pipe = np.load(os.path.join(out, "chain_free.npy"))
def summarise(ch, seed=2):
    T0c, Pc, kc, bc, lr = ch[:, 0], ch[:, 1], ch[:, 2], ch[:, 3], ch[:, 4]
    rho = np.exp(lr); a = aRs(rho, Pc); inc = np.degrees(np.arccos(bc / a))
    t14 = Pc / np.pi * np.arcsin(np.clip(np.sqrt(np.clip((1 + kc) ** 2 - bc ** 2, 0, None)) / (a * np.sin(np.radians(inc))), 0, 1)) * 24
    rs = np.random.default_rng(seed).normal(1.21, 0.06, len(kc)); rp = kc * rs * 9.7318
    o = {}
    for n, x in (("T0_btjd", T0c), ("period_d", Pc), ("rp_over_rs", kc), ("impact_parameter", bc), ("stellar_density_solar", rho), ("a_over_rs", a), ("inclination_deg", inc), ("t14_hours", t14), ("radius_rjup", rp)):
        lo, md, hi = np.percentile(x, [16, 50, 84]); o[n] = dict(median=float(md), minus=float(md - lo), plus=float(hi - md))
    return o
E["params"] = dict(own=summarise(ch_own), pipeline=summarise(ch_pipe))
wcsv("parameters.csv", ["parameter", "own_median", "own_minus", "own_plus", "pipeline_median", "pipeline_minus", "pipeline_plus"],
     [[k, *[repr(E["params"]["own"][k][q]) for q in ("median", "minus", "plus")], *[repr(E["params"]["pipeline"][k][q]) for q in ("median", "minus", "plus")]] for k in E["params"]["own"]])
T0 = E["params"]["own"]["T0_btjd"]["median"]; P = E["params"]["own"]["period_d"]["median"]
E["ephemeris"] = dict(T0_bjd=2457000 + T0, T0_err=E["params"]["own"]["T0_btjd"]["plus"], P=P, P_err=E["params"]["own"]["period_d"]["plus"], t14_hours=E["params"]["own"]["t14_hours"]["median"])
shape = lambda tt: 1 - tmodel(tt, T0o, Po, ko, bbo, ao, uo)
D0 = float(shape(np.array([T0o]))[0])

# ---------------------------------------------------------------- light curves
d = np.load(os.path.join(out, "lc_own3x3.npz")); t, f, e, s = d["t"], d["f"], d["e"], d["s"]
wcsv("lightcurve_own_photometry.csv", ["btjd", "relative_flux", "flux_err", "sector"], [[f"{a:.6f}", f"{b:.6f}", f"{c:.6f}", int(g)] for a, b, c, g in zip(t, f, e, s)])
dp = np.load(os.path.join(out, "lc_final.npz"))
wcsv("lightcurve_pipeline.csv", ["btjd", "relative_flux", "flux_err", "sector"], [[f"{a:.6f}", f"{b:.6f}", f"{c:.6f}", int(g)] for a, b, c, g in zip(dp["t"], dp["f"], dp["e"], dp["s"])])
ph = ((t - T0o + 0.5 * Po) % Po) - 0.5 * Po; hrs = ph * 24; ep = np.round((t - T0o) / Po).astype(int)

# 1. folded transit
rows = binned(hrs, f, e, np.linspace(-5, 5, 61))
xx = np.linspace(-5, 5, 601)
rng = np.random.default_rng(11); near = np.where((np.abs(hrs) < 5) & (np.abs(f - 1) < 0.012))[0]; pick = rng.choice(near, 2600, replace=False)
E["folded"] = dict(bins=[[R(a, 3), R((b - 1) * 100, 4), R(c * 100, 4)] for a, b, c, n in rows],
                   model=[[R(a, 3), R(-v * 100, 4)] for a, v in zip(xx, shape(T0o + xx / 24))],
                   cloud=[[R(hrs[i], 3), R((f[i] - 1) * 100, 3)] for i in pick], n_points=int(len(t)), n_transits=int(len(np.unique(ep[np.abs(hrs) < 0.5]))), depth_pct=R(D0 * 100, 3))
wcsv("folded_transit_binned.csv", ["hours_from_midtransit", "flux_change_percent", "err_percent", "n_points"], [[R(a, 4), R((b - 1) * 100, 5), R(c * 100, 5), n] for a, b, c, n in rows])
wcsv("transit_model.csv", ["hours_from_midtransit", "flux_change_percent"], E["folded"]["model"])

# 2. odd / even
win = np.abs(ph) < 0.3; odd = ep % 2 != 0
Ao, so = amp_fit(t, f, e, shape, win & odd); Ae, se = amp_fit(t, f, e, shape, win & ~odd)
ro = binned(hrs[odd], f[odd], e[odd], np.linspace(-4, 4, 33)); re_ = binned(hrs[~odd], f[~odd], e[~odd], np.linspace(-4, 4, 33))
E["oddeven"] = dict(odd=[[R(a, 3), R((b - 1) * 100, 4), R(c * 100, 4)] for a, b, c, n in ro], even=[[R(a, 3), R((b - 1) * 100, 4), R(c * 100, 4)] for a, b, c, n in re_],
                    odd_depth_ppm=R(Ao * D0 * 1e6, 0), odd_err=R(so * D0 * 1e6, 0), even_depth_ppm=R(Ae * D0 * 1e6, 0), even_err=R(se * D0 * 1e6, 0), sigma=R(abs(Ao - Ae) / np.hypot(so, se), 2))
wcsv("odd_even_binned.csv", ["parity", "hours_from_midtransit", "flux_change_percent", "err_percent", "n_points"],
     [["odd", R(a, 4), R((b - 1) * 100, 5), R(c * 100, 5), n] for a, b, c, n in ro] + [["even", R(a, 4), R((b - 1) * 100, 5), R(c * 100, 5), n] for a, b, c, n in re_])

# 3. full orbit (transit removed)
phi = ((t - T0o) % Po) / Po; oot = np.abs(hrs) > 1.3
rp_ = binned(phi[oot], f[oot], e[oot], np.linspace(0, 1, 81))
E["phase"] = [[R(a, 4), R((b - 1) * 1e6, 1), R(c * 1e6, 1)] for a, b, c, n in rp_]
wcsv("full_orbit_binned.csv", ["orbital_phase", "flux_change_ppm", "err_ppm", "n_points"], [[R(a, 5), R((b - 1) * 1e6, 2), R(c * 1e6, 2), n] for a, b, c, n in rp_])

# 4. transit times against the ephemeris fitted WITHOUT sector 105 (pipeline light curves, sectors 68-104)
pt = np.load(os.path.join(out, "per_transit_own.npy"))
trows = []
for i, r in enumerate(pt):
    n = int(round((r[1] - T0m) / Pm)); oc = (r[1] - (T0m + n * Pm)) * 1440
    trows.append([i + 1, int(r[6]), R(r[1], 5), R(oc, 2), R(r[3], 2), R(r[4], 0), R(r[5], 0)])
E["timing"] = dict(rows=trows, ref_T0=R(T0m, 5), ref_P=R(Pm, 6))
wcsv("transit_times.csv", ["transit_index", "sector", "midtransit_btjd", "o_minus_c_min", "err_min", "depth_ppm", "depth_err_ppm"], trows)

# 5. per-sector 30-minute light curves
lcs = []
for sec in np.unique(s):
    m = s == sec; tt = t[m]; ff = f[m]
    edges = np.arange(tt.min(), tt.max() + 0.0209, 1 / 48.0); idx = np.digitize(tt, edges) - 1
    pts = [[R(edges[i] + 1 / 96.0, 3), R((ff[idx == i].mean() - 1) * 100, 3)] for i in np.unique(idx) if (idx == i).sum() >= 4]
    n0 = int(np.ceil((tt.min() - T0o) / Po)); n1 = int(np.floor((tt.max() - T0o) / Po))
    lcs.append(dict(sector=int(sec), points=pts, transits=[R(T0o + n * Po, 3) for n in range(n0, n1 + 1)], t0=R(tt.min(), 2), t1=R(tt.max(), 2)))
E["lightcurves"] = lcs

# 6. period search (contiguous sectors 102-104 of the pipeline light curves)
mk = dp["s"] >= 102
bls = BoxLeastSquares(dp["t"][mk], dp["f"][mk], dp["e"][mk]); periods = np.exp(np.linspace(np.log(0.5), np.log(30), 30000))
res = bls.power(periods, [0.04, 0.06, 0.08, 0.1, 0.13, 0.16, 0.2], objective="snr")
ip = int(np.argmax(res.power)); nb = 900; edges = np.linspace(0, len(periods), nb + 1).astype(int)
pool = [[R(periods[a + int(np.argmax(res.power[a:b]))], 4), R(res.power[a:b].max(), 2)] for a, b in zip(edges[:-1], edges[1:])]
E["bls"] = dict(points=pool, peak_period=R(res.period[ip], 4), peak_snr=R(res.power[ip], 1))
wcsv("bls_periodogram.csv", ["period_days", "box_fit_signal_to_noise"], [[f"{a:.5f}", f"{b:.3f}"] for a, b in zip(periods, res.power)])

# 7. apertures, detrending, centroids
ad = json.load(open(os.path.join(out, "aperture_depths.json")))
E["apertures"] = [dict(sector=a["sector"], aperture=a["aperture"].replace(" core", ""), depth=R(a["depth_ppm"], 0), err=R(a["err_ppm"], 0), net=R(a["net_flux_e_s"], 0)) for a in ad["apertures"]]
E["detrending"] = [dict(label=x["label"], depth=R(x["depth_ppm"], 0), err=R(x["err_ppm"], 0), per_sector=[R(v, 0) for v in x["per_sector"]]) for x in ad["detrending"]]
wcsv("aperture_depths.csv", ["sector", "aperture", "depth_ppm", "err_ppm", "net_flux_e_per_s"], [[a["sector"], a["aperture"], a["depth"], a["err"], a["net"]] for a in E["apertures"]])
wcsv("depth_vs_reduction.csv", ["reduction", "depth_ppm", "err_ppm", "per_sector_ppm"], [[x["label"], x["depth"], x["err"], " ".join(str(v) for v in x["per_sector"])] for x in E["detrending"]])
cr = json.load(open(os.path.join(out, "centroid_results.json")))
E["centroid"] = [dict(sector=c["sector"], n=c["n_transits"], target=[R(v, 2) for v in c["target_px"]], diffc=[R(v, 2) for v in c["diff_centroid"]], off=R(c["offset_arcsec"], 1), err=R(c["offset_err_arcsec"], 1),
                      oot=[[R(v, 0) for v in row] for row in c["oot"]], diff=[[R(v, 1) for v in row] for row in c["diff"]]) for c in cr]
wcsv("centroid_offsets.csv", ["sector", "n_transits", "target_x_px", "target_y_px", "difference_centroid_x_px", "difference_centroid_y_px", "offset_arcsec", "offset_err_arcsec"],
     [[c["sector"], c["n"], *c["target"], *c["diffc"], c["off"], c["err"]] for c in E["centroid"]])
json.dump(cr, open(os.path.join(D, "difference_images.json"), "w"))

# 8. Gaia neighbours
import pandas as pd
g = pd.read_csv(os.path.join(out, "gaia_neighbors.csv"))
def tmag(G, c):
    return G - 0.00522555 * c ** 3 + 0.0891337 * c ** 2 - 0.633923 * c + 0.0324473 if np.isfinite(c) else G - 0.430
g["T"] = [tmag(a, b) for a, b in zip(g.phot_g_mean_mag, g.bp_rp)]; g["flux_ratio"] = 10 ** (-0.4 * (g["T"] - g["T"].iloc[0]))
ra0, de0 = g.ra.iloc[0], g.dec.iloc[0]
g["dra"] = (g.ra - ra0) * np.cos(np.radians(de0)) * 3600; g["ddec"] = (g.dec - de0) * 3600
E["neighbours"] = [dict(id=str(int(r.source_id)), dx=R(r.dra, 1), dy=R(r.ddec, 1), sep=R(r.sep_arcsec, 1), G=R(r.phot_g_mean_mag, 2), T=R(r["T"], 2), fr=R(r.flux_ratio, 5)) for _, r in g.iterrows()]
wcsv("gaia_neighbours.csv", ["gaia_dr3_source_id", "separation_arcsec", "delta_ra_arcsec", "delta_dec_arcsec", "G_mag", "T_mag_estimate", "flux_ratio_to_target"],
     [[n["id"], n["sep"], n["dx"], n["dy"], n["G"], n["T"], n["fr"]] for n in E["neighbours"]])

# 9. TRICERATOPS
tri = {}
for tag, label in (("mission1e7", "Pipeline light curve, 10^7 samples"), ("own1e7", "Own photometry, 10^7 samples"), ("mission", "Pipeline light curve, 10^6 samples (not converged)"),
                   ("mission1e7_phase", "Pipeline light curve, 10^7 samples, with whole-orbit limits"), ("own1e7_phase", "Own photometry, 10^7 samples, with whole-orbit limits")):
    runs = np.atleast_2d(np.loadtxt(os.path.join(out, f"triceratops_runs_{tag}.txt")))
    tri[tag] = dict(label=label, fpp=[R(v, 5) for v in runs[:, 0]], nfpp=[R(v, 6) for v in runs[:, 1]])
    sc = os.path.join(out, f"triceratops_scenarios_{tag}.csv")
    if os.path.exists(sc):
        m = pd.read_csv(sc).mean().sort_values(ascending=False); tri[tag]["scenarios"] = {k: R(v, 5) for k, v in m.items()}
E["triceratops"] = tri
wcsv("triceratops_runs.csv", ["light_curve", "run", "false_positive_probability", "nearby_false_positive_probability"], [[v["label"], i + 1, a, b] for v in tri.values() for i, (a, b) in enumerate(zip(v["fpp"], v["nfpp"]))])
wcsv("triceratops_scenarios.csv", ["light_curve", "scenario", "mean_probability"], [[v["label"], k, p] for v in tri.values() if "scenarios" in v for k, p in v["scenarios"].items()])

# 10. ASAS-SN ground-based photometry (scripts/20_asassn.py, 22_asassn_fold.py)
asn = os.path.join(out, "asassn_site.json")
if os.path.exists(asn):
    E["asassn"] = json.load(open(asn))
    wcsv("asassn_folded_binned.csv", ["band", "hours_from_predicted_midtransit", "flux_change_percent", "err_percent", "n_points"], [[b_, *row] for b_, v in E["asassn"]["bands"].items() for row in v["bins"]])
    wcsv("asassn_phase_scan.csv", ["phase_offset_fraction_of_period", "depth_over_empirical_error"], E["asassn"]["scan"])
    shutil.copy(os.path.join(out, "asassn_detrended.csv"), os.path.join(D, "asassn_detrended.csv"))
    raw = os.path.join(os.path.dirname(os.path.abspath(out)), "data", "asassn", "asassn_lightcurve.csv")
    if os.path.exists(raw): shutil.copy(raw, os.path.join(D, "asassn_lightcurve.csv"))

# ---------------------------------------------------------------- copy evidence files
ev = os.path.join(site, "evidence")
for sub in ("figures", "logs", "raw", "posteriors", "catalogues"): os.makedirs(os.path.join(ev, sub), exist_ok=True)
for p in sorted(glob.glob(os.path.join(out, "0*.png"))): shutil.copy(p, os.path.join(ev, "figures"))
def clean_log(src, dst):
    keep = []; skip = False
    for line in open(src, errors="replace"):
        if "/Users/" in line or line.startswith(("Traceback", "During handling", "The above exception")): skip = line.lstrip().startswith("File"); continue
        if skip and line.startswith("    "): skip = False; continue
        skip = False
        if line.strip() == "" and keep and keep[-1].strip() == "": continue
        keep.append(line)
    open(dst, "w").write("".join(keep))
for name in ("fit_free.log", "fit_prior.log", "fit_free_own.log", "fit_prior_own.log", "triceratops_mission.log"):
    if os.path.exists(os.path.join(out, name)): clean_log(os.path.join(out, name), os.path.join(ev, "logs", name.replace(".log", ".txt")))
for name in ("chain_free.npy", "chain_prior.npy", "chain_free_own.npy", "chain_prior_own.npy"): shutil.copy(os.path.join(out, name), os.path.join(ev, "posteriors"))
for name in ("gaia_neighbors.csv", "mast_products.json", "triceratops_probs_mission1e7.csv", "triceratops_probs_own1e7.csv", "triceratops_probs_mission1e7_phase.csv", "triceratops_probs_own1e7_phase.csv"):
    if os.path.exists(os.path.join(out, name)): shutil.copy(os.path.join(out, name), os.path.join(ev, "catalogues"))
for p in glob.glob(os.path.join(mast_dir, "**", "*_lc.fits"), recursive=True) + glob.glob(os.path.join(mast_dir, "**", "*_llc.fits"), recursive=True): shutil.copy(p, os.path.join(ev, "raw"))
shutil.copy(report, os.path.join(ev, "vetting_report.md"))
sd = os.path.join(site, "scripts"); os.makedirs(sd, exist_ok=True)
for p in sorted(glob.glob(os.path.join(scripts_dir, "*.py"))): shutil.copy(p, sd)

E["mast"] = json.load(open(os.path.join(out, "mast_products.json")))
E["generated"] = "2026-11-10"
with open(os.path.join(site, "assets", "data.js"), "w") as fh:
    fh.write("window.EVIDENCE = " + json.dumps(E, separators=(",", ":")) + ";\n")
print("bundle: %.0f kB" % (os.path.getsize(os.path.join(site, "assets", "data.js")) / 1e3))
print("ephemeris:", E["ephemeris"]); print("odd/even:", {k: v for k, v in E["oddeven"].items() if not isinstance(v, list)})
print("bls peak:", E["bls"]["peak_period"], E["bls"]["peak_snr"], "| folded:", E["folded"]["n_points"], E["folded"]["n_transits"], E["folded"]["depth_pct"])
for k in ("own", "pipeline"): print(k, {a: (round(b["median"], 5), round(b["minus"], 5), round(b["plus"], 5)) for a, b in E["params"][k].items()})
