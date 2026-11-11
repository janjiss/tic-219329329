"""Finish the site folder: copy script logs and catalogue records, then write the file manifest and folder index pages.

usage: 19_site_manifest.py <out_dir> <site_dir> <exofop_target.json>
"""
import sys, os, json, csv, glob, html, shutil
import pandas as pd

out, site, exofop = sys.argv[1:4]
ev = os.path.join(site, "evidence")

# ---- logs from the vetting scripts (local paths stripped)
def clean_log(src, dst):
    keep = []
    for line in open(src, errors="replace"):
        if "/Users/" in line or "RuntimeWarning" in line: continue
        keep.append(line)
    open(dst, "w").write("".join(keep))
for p in sorted(glob.glob(os.path.join(out, "logs", "*.txt"))): clean_log(p, os.path.join(ev, "logs", os.path.basename(p)))

# ---- catalogue records
if os.path.abspath(exofop) != os.path.abspath(os.path.join(ev, "catalogues", "exofop_target.json")): shutil.copy(exofop, os.path.join(ev, "catalogues", "exofop_target.json"))
g = pd.read_csv(os.path.join(out, "gaia_neighbors.csv")).iloc[0].to_dict()
g = {k: (None if isinstance(v, float) and v != v else (v.item() if hasattr(v, "item") else v)) for k, v in g.items()}
g["source_id"] = str(int(g["source_id"]))
g.update({"_note": "Gaia DR3 gaia_source row for the target (queried 2026-11-10), plus selected astrophysical_parameters and radial-velocity fields.",
          "radius_gspphot": 1.1651, "radius_flame": 1.234771, "lum_flame": 1.674899, "mass_flame": 1.052862, "age_flame": 6.6391,
          "grvs_mag": 12.158114, "rv_method_used": 2, "rv_expected_sig_to_noise": 24.694508, "rv_template_teff": 6000.0,
          "nss_two_body_orbit_rows": 0, "nss_acceleration_astro_rows": 0, "nss_non_linear_spectro_rows": 0, "vari_summary_rows": 0})
json.dump(g, open(os.path.join(ev, "catalogues", "gaia_target.json"), "w"), indent=1)
rows = [
 ("ExoFOP-TESS", "TOIs and community candidates (CTOIs)", "by TIC ID", "no TOI, no CTOI", "exofop.ipac.caltech.edu"),
 ("SIMBAD", "object lookup", "10 arcsec", "no object", "simbad.harvard.edu mirror"),
 ("B/vsx/vsx", "AAVSO Variable Star Index", "10 arcsec", "no match", "vizier.cfa.harvard.edu mirror"),
 ("I/358/vclassre", "Gaia DR3 variability classification", "3 arcsec", "no match", "vizier.cfa.harvard.edu mirror"),
 ("I/358/veb", "Gaia DR3 eclipsing binaries", "3 arcsec", "no match", "vizier.cfa.harvard.edu mirror"),
 ("II/366/catalog", "ASAS-SN variable stars", "10 arcsec", "no match", "vizier.cfa.harvard.edu mirror"),
 ("J/ApJS/258/16", "TESS eclipsing binaries (Prsa+ 2022)", "10 arcsec", "no match", "vizier.cfa.harvard.edu mirror"),
 ("B/wds/wds", "Washington Double Star catalogue", "10 arcsec", "no match", "vizier.cfa.harvard.edu mirror"),
 ("III/283/ravedr6", "RAVE DR6 spectroscopy", "3 arcsec", "no match", "vizier.cfa.harvard.edu mirror"),
 ("J/MNRAS/506/150", "GALAH DR3 spectroscopy", "3 arcsec", "no match", "vizier.cfa.harvard.edu mirror"),
 ("IX/47/2rxs", "ROSAT 2RXS X-ray sources", "40 arcsec", "no match", "vizier.cfa.harvard.edu mirror"),
 ("II/335/galex_ais", "GALEX ultraviolet sources", "4 arcsec", "no match", "vizier.cfa.harvard.edu mirror"),
 ("J/ApJS/254/39", "TESS Objects of Interest (Guerrero+ 2021)", "10 arcsec", "no match", "vizier.cfa.harvard.edu mirror"),
 ("IV/39/tic82", "TESS Input Catalog 8.2", "3 arcsec", "1 row (the target)", "vizier.cfa.harvard.edu mirror"),
 ("gaiadr3.nss_*", "Gaia DR3 non-single-star tables", "by source ID", "0 rows", "gea.esac.esa.int"),
 ("VizieR (all catalogues)", "positional search of every catalogue", "3 arcsec", "FAILED: server errors, not completed", "vizier.cfa.harvard.edu mirror"),
]
with open(os.path.join(ev, "catalogues", "crossmatch_results.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["catalogue", "description", "search_radius", "result", "service"]); w.writerows(rows)

spec = [
 ("ESO Science Archive, reduced products", "30 arcsec box", "no spectra; only VISTA VHS near-infrared images and catalogue entries", "archive.eso.org/tap_obs (ivoa.ObsCore)"),
 ("ESO Science Archive, raw frames", "30 arcsec box", "none from any instrument", "archive.eso.org/tap_obs (dbo.raw)"),
 ("GALAH DR4", "Gaia DR3 source ID, and 10 arcsec box", "no match; no GALAH DR4 star within 1 degree", "datacentral.org.au/vo/tap (galah_dr4.mainstartable)"),
 ("GALAH DR3", "3 arcsec", "no match", "VizieR J/MNRAS/506/150"),
 ("APOGEE DR17", "5 arcsec, and 1 degree", "no match; field not observed", "VizieR III/286 and SDSS SkyServer DR17 (apogeeStar)"),
 ("SDSS-V DR19 Milky Way Mapper, APOGEE and BOSS", "5 arcsec box", "no spectra; star is in the targeting database only (ops_std_boss, ops_gaia_brightneighbors)", "SDSS SkyServer DR19 (mwm_apogee_allvisit, mwm_boss_allvisit, apogee_drp_allvisit, mos_target)"),
 ("RAVE DR6", "3 arcsec", "no match", "VizieR III/283"),
 ("Gaia DR3 radial velocity", "by source ID", "-1.65 +/- 1.12 km/s from 34 visits, stacked cross-correlation; weak constraint", "gea.esac.esa.int"),
]
with open(os.path.join(ev, "catalogues", "archival_spectra_search.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["archive", "search", "result", "service"]); w.writerows(spec)

# ---- manifest
DESC = {
 "data/folded_transit_binned.csv": "Folded transit, 10-minute bins (chart E1)",
 "data/transit_model.csv": "Best-fit transit model curve (chart E1)",
 "data/lightcurve_own_photometry.csv": "Own 3x3 pixel photometry, detrended, all six sectors, 51,810 points",
 "data/lightcurve_pipeline.csv": "TESS-SPOC (sector 68) and QLP (sectors 95-104) light curves, detrended, 42,709 points",
 "data/bls_periodogram.csv": "Box-least-squares period search, sectors 102-104 (chart E3)",
 "data/centroid_offsets.csv": "Difference-image centroid offsets per sector (E4)",
 "data/difference_images.json": "Out-of-transit and difference images per sector, 15x15 pixels (E4)",
 "data/gaia_neighbours.csv": "Gaia DR3 sources within 150 arcsec with flux ratios (E5)",
 "data/aperture_depths.csv": "Transit depth per sector and aperture size (E6)",
 "data/depth_vs_reduction.csv": "Transit depth for each pipeline product and detrending window (E7)",
 "data/parameters.csv": "Posterior medians and 68% intervals for both fits",
 "data/odd_even_binned.csv": "Odd and even transits, 15-minute bins (E9)",
 "data/full_orbit_binned.csv": "Brightness against orbital phase with the transit removed (E10)",
 "data/transit_times.csv": "Individual mid-transit times, residuals and depths for 34 transits (E12)",
 "data/triceratops_runs.csv": "False-positive probability of every TRICERATOPS run (E15)",
 "data/triceratops_scenarios.csv": "Mean probability of each TRICERATOPS scenario (E15)",
 "evidence/vetting_report.md": "Written vetting report with all results in one document",
 "data/asassn_folded_binned.csv": "ASAS-SN g and V photometry folded on the TESS ephemeris, half-hour bins (chart E16)",
 "data/asassn_phase_scan.csv": "Transit template slid around the orbit in ASAS-SN data (chart E16)",
 "data/asassn_detrended.csv": "ASAS-SN photometry after per-camera normalisation, with orbital phase",
 "data/asassn_lightcurve.csv": "ASAS-SN Sky Patrol v2 light curve as downloaded, 3385 measurements, 2014-2025",
 "evidence/figures/07_asassn.png": "Diagnostic plot: ASAS-SN g and V folded, and the phase scan",
 "evidence/logs/21_triceratops_phase_own.txt": "TRICERATOPS with whole-orbit limits, own photometry, 6 runs of 10^7 samples (E17)",
 "evidence/logs/21_triceratops_phase_pipeline.txt": "TRICERATOPS with whole-orbit limits, pipeline light curve, 6 runs of 10^7 samples (E17)",
 "evidence/logs/22_asassn_fold.txt": "Output of 22_asassn_fold.py: ASAS-SN depths, significance and phase scan (E16)",
 "evidence/catalogues/archival_spectra_search.csv": "Result of each archival spectra search (E18)",
 "evidence/catalogues/triceratops_probs_own1e7_phase.csv": "TRICERATOPS best-fit parameters per scenario with whole-orbit limits, own photometry",
 "evidence/catalogues/triceratops_probs_mission1e7_phase.csv": "TRICERATOPS best-fit parameters per scenario with whole-orbit limits, pipeline light curve",
 "scripts/20_asassn.py": "Download the ASAS-SN light curve",
 "scripts/21_triceratops_phase.py": "TRICERATOPS with the secondary-eclipse and ellipsoidal limits added",
 "scripts/22_asassn_fold.py": "Fold ASAS-SN photometry on the TESS ephemeris and measure the depth",
 "evidence/figures/01_raw_lightcurves.png": "Diagnostic plot: pipeline light curves per sector before detrending",
 "evidence/figures/02_bls.png": "Diagnostic plot: period search and first folded transit",
 "evidence/figures/03_vetting_lc.png": "Diagnostic plot: odd/even, secondary scan, per-transit depth and timing (pipeline light curves)",
 "evidence/figures/04_centroid.png": "Diagnostic plot: out-of-transit and difference images",
 "evidence/figures/05_extra_signals.png": "Diagnostic plot: residual period search and stellar variability",
 "evidence/figures/06_independent_photometry.png": "Diagnostic plot: own photometry folded, odd/even, timing, full orbit",
 "evidence/logs/fit_free.txt": "MCMC transit fit, pipeline light curves, stellar density free",
 "evidence/logs/fit_prior.txt": "MCMC transit fit, pipeline light curves, stellar density prior",
 "evidence/logs/fit_free_own.txt": "MCMC transit fit, own photometry, stellar density free",
 "evidence/logs/fit_prior_own.txt": "MCMC transit fit, own photometry, stellar density prior",
 "evidence/logs/triceratops_mission.txt": "TRICERATOPS output, 12 runs of 10^6 samples (not converged)",
 "evidence/logs/08_vet_lc.txt": "Output of 08_vet_lc.py: odd/even, per-sector depth, secondary scan (pipeline light curves)",
 "evidence/logs/09_phasecurve.txt": "Output of 09_phasecurve.py: ellipsoidal amplitude and mass limit (E11)",
 "evidence/logs/10_centroid.txt": "Output of 10_centroid.py: centroid offsets (E4)",
 "evidence/logs/11_sector102_and_sector1.txt": "Output of 11_s102_and_s1.py: sector 102 corner source and sector 1 coverage",
 "evidence/logs/14_apertures.txt": "Output of 14_apertures.py: depth vs aperture, sector 105 timing, depth vs reduction (E6, E7, E12)",
 "evidence/logs/15_extra_signals.txt": "Output of 15_extra_signals.py: residual search and variability (E13)",
 "evidence/logs/17_own_checks.txt": "Output of 17_own_checks.py: odd/even, secondary and timing on own photometry (E9, E10, E12)",
 "evidence/posteriors/chain_free.npy": "Posterior samples (NumPy), pipeline light curves, density free. Columns: T0, P, Rp/Rs, b, ln(density), u1, u2",
 "evidence/posteriors/chain_prior.npy": "Posterior samples (NumPy), pipeline light curves, density prior",
 "evidence/posteriors/chain_free_own.npy": "Posterior samples (NumPy), own photometry, density free",
 "evidence/posteriors/chain_prior_own.npy": "Posterior samples (NumPy), own photometry, density prior",
 "evidence/catalogues/gaia_neighbors.csv": "Gaia DR3 query result, all columns, 150 arcsec cone",
 "evidence/catalogues/gaia_target.json": "Gaia DR3 record of the target star",
 "evidence/catalogues/exofop_target.json": "ExoFOP-TESS record of the target (no TOI or CTOI)",
 "evidence/catalogues/crossmatch_results.csv": "Result of each catalogue cross-match (E14)",
 "evidence/catalogues/mast_products.json": "MAST archive identifiers of the pipeline products used",
 "evidence/catalogues/triceratops_probs_mission1e7.csv": "TRICERATOPS best-fit parameters per scenario, pipeline light curve",
 "evidence/catalogues/triceratops_probs_own1e7.csv": "TRICERATOPS best-fit parameters per scenario, own photometry",
 "scripts/common.py": "Shared loaders, detrending and transit model",
 "scripts/01_search.py": "List TESS data available at MAST",
 "scripts/02_download.py": "Download pipeline light curves and the pixel file",
 "scripts/03_firstlook.py": "Plot raw light curves",
 "scripts/04_search.py": "Detrend and run the period search",
 "scripts/05_gaia.py": "Gaia DR3 query for the target and neighbours",
 "scripts/06_fit.py": "MCMC transit fit",
 "scripts/07_tesscut.py": "Download full-frame image cutouts",
 "scripts/08_vet_lc.py": "Odd/even, secondary and per-transit tests on pipeline light curves",
 "scripts/09_phasecurve.py": "Out-of-transit phase variations and mass limit",
 "scripts/10_centroid.py": "Difference-image centroid test",
 "scripts/11_s102_and_s1.py": "Sector 102 corner source and sector 1 coverage",
 "scripts/12_prep_tri.py": "Prepare inputs for TRICERATOPS",
 "scripts/13_triceratops.py": "Run TRICERATOPS",
 "scripts/14_apertures.py": "Own photometry, depth vs aperture and reduction, sector 105 timing",
 "scripts/15_extra_signals.py": "Search for other signals and stellar variability",
 "scripts/16_catalogues.py": "SIMBAD and VizieR cross-matches",
 "scripts/17_own_checks.py": "Odd/even, secondary and timing on own photometry",
 "scripts/18_export_site.py": "Export the data shown on this site",
 "scripts/19_site_manifest.py": "Write this file list and the folder index pages",
}
GROUPS = [("data/", "Data behind the charts"), ("evidence/vetting_report.md", "Report"), ("evidence/figures/", "Diagnostic plots"), ("evidence/logs/", "Script output"),
          ("evidence/catalogues/", "Catalogue records"), ("evidence/posteriors/", "Posterior samples"), ("evidence/raw/", "Pipeline light curves as downloaded"), ("scripts/", "Analysis scripts")]
def size(n):
    return "%d B" % n if n < 1000 else "%.0f kB" % (n / 1e3) if n < 1e6 else "%.1f MB" % (n / 1e6)
for p in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "*.py"))): shutil.copy(p, os.path.join(site, "scripts"))
files = []
for root in ("data", "evidence", "scripts"):
    for dp, dn, fn in os.walk(os.path.join(site, root)):
        for f in sorted(fn):
            if f == "index.html" or f.startswith("."): continue
            rel = os.path.relpath(os.path.join(dp, f), site).replace(os.sep, "/")
            d = DESC.get(rel)
            if d is None and rel.startswith("evidence/raw/"):
                sec = int(f.split("s00")[1][:2]) if "s00" in f else int(f.split("s0")[1][:3])
                d = ("TESS-SPOC" if "tess-spoc" in f else "QLP") + " light curve as downloaded from MAST, sector %d (FITS)" % sec
            grp = next(label for prefix, label in GROUPS if rel.startswith(prefix))
            files.append(dict(path=rel, desc=d or "", size=size(os.path.getsize(os.path.join(dp, f))), group=grp))
order = [label for _, label in GROUPS]
files.sort(key=lambda x: (order.index(x["group"]), x["path"]))
missing = [f["path"] for f in files if not f["desc"]]
with open(os.path.join(site, "assets", "files.js"), "w") as fh: fh.write("window.FILES = " + json.dumps(files, separators=(",", ":")) + ";\n")
with open(os.path.join(site, "FILES.md"), "w") as fh:
    fh.write("# File list\n\nEvery data product, log, figure and script in this folder. Paths are relative to the site root.\n")
    for label in order:
        fh.write("\n## %s\n\n| File | What it is | Size |\n|---|---|---|\n" % label)
        for f in files:
            if f["group"] == label: fh.write("| [%s](%s) | %s | %s |\n" % (f["path"], f["path"], f["desc"], f["size"]))

# ---- folder index pages, so links to a folder work on any static host
dirs = sorted({os.path.dirname(f["path"]) for f in files} | {"evidence"})
for d in dirs:
    up = "../" * (d.count("/") + 1)
    here = [f for f in files if os.path.dirname(f["path"]) == d]
    subs = sorted(x for x in dirs if os.path.dirname(x) == d)
    rows = "".join('<tr><td><a href="%s/">%s/</a></td><td>Folder</td><td class="num"></td></tr>' % (os.path.basename(s), os.path.basename(s)) for s in subs)
    rows += "".join('<tr><td><a href="%s">%s</a></td><td>%s</td><td class="num">%s</td></tr>' % (html.escape(os.path.basename(f["path"])), html.escape(os.path.basename(f["path"])), html.escape(f["desc"]), f["size"]) for f in here)
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>%s — TIC 219329329.01</title>'
            '<meta name="color-scheme" content="light dark"><link rel="stylesheet" href="%sassets/style.css"></head><body><main class="wrap" style="padding-top:32px;padding-bottom:48px">'
            '<p class="kicker"><a href="%sindex.html#files">TIC 219329329.01 evidence</a></p><h2 class="mono">%s/</h2><div class="card"><div class="table-wrap"><table class="data-table">'
            '<thead><tr><th scope="col">File</th><th scope="col">What it is</th><th scope="col" class="num">Size</th></tr></thead><tbody>%s</tbody></table></div></div></main></body></html>\n') % (d, up, up, d, rows)
    open(os.path.join(site, d, "index.html"), "w").write(page)
print("files listed: %d ; folder index pages: %d ; without description: %s" % (len(files), len(dirs), missing))
