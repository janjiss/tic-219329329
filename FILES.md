# File list

Every data product, log, figure and script in this folder. Paths are relative to the site root.

## Data behind the charts

| File | What it is | Size |
|---|---|---|
| [data/aperture_depths.csv](data/aperture_depths.csv) | Transit depth per sector and aperture size (E6) | 571 B |
| [data/bls_periodogram.csv](data/bls_periodogram.csv) | Box-least-squares period search, sectors 102-104 (chart E3) | 467 kB |
| [data/centroid_offsets.csv](data/centroid_offsets.csv) | Difference-image centroid offsets per sector (E4) | 328 B |
| [data/depth_vs_reduction.csv](data/depth_vs_reduction.csv) | Transit depth for each pipeline product and detrending window (E7) | 905 B |
| [data/difference_images.json](data/difference_images.json) | Out-of-transit and difference images per sector, 15x15 pixels (E4) | 21 kB |
| [data/folded_transit_binned.csv](data/folded_transit_binned.csv) | Folded transit, 10-minute bins (chart E1) | 2 kB |
| [data/full_orbit_binned.csv](data/full_orbit_binned.csv) | Brightness against orbital phase with the transit removed (E10) | 2 kB |
| [data/gaia_neighbours.csv](data/gaia_neighbours.csv) | Gaia DR3 sources within 150 arcsec with flux ratios (E5) | 2 kB |
| [data/lightcurve_own_photometry.csv](data/lightcurve_own_photometry.csv) | Own 3x3 pixel photometry, detrended, all six sectors, 51,810 points | 1.8 MB |
| [data/lightcurve_pipeline.csv](data/lightcurve_pipeline.csv) | TESS-SPOC (sector 68) and QLP (sectors 95-104) light curves, detrended, 42,709 points | 1.5 MB |
| [data/odd_even_binned.csv](data/odd_even_binned.csv) | Odd and even transits, 15-minute bins (E9) | 2 kB |
| [data/parameters.csv](data/parameters.csv) | Posterior medians and 68% intervals for both fits | 1 kB |
| [data/transit_model.csv](data/transit_model.csv) | Best-fit transit model curve (chart E1) | 8 kB |
| [data/transit_times.csv](data/transit_times.csv) | Individual mid-transit times, residuals and depths for 34 transits (E12) | 2 kB |
| [data/triceratops_runs.csv](data/triceratops_runs.csv) | False-positive probability of every TRICERATOPS run (E15) | 1 kB |
| [data/triceratops_scenarios.csv](data/triceratops_scenarios.csv) | Mean probability of each TRICERATOPS scenario (E15) | 1 kB |

## Report

| File | What it is | Size |
|---|---|---|
| [evidence/vetting_report.md](evidence/vetting_report.md) | Written vetting report with all results in one document | 7 kB |

## Diagnostic plots

| File | What it is | Size |
|---|---|---|
| [evidence/figures/01_raw_lightcurves.png](evidence/figures/01_raw_lightcurves.png) | Diagnostic plot: pipeline light curves per sector before detrending | 278 kB |
| [evidence/figures/02_bls.png](evidence/figures/02_bls.png) | Diagnostic plot: period search and first folded transit | 200 kB |
| [evidence/figures/03_vetting_lc.png](evidence/figures/03_vetting_lc.png) | Diagnostic plot: odd/even, secondary scan, per-transit depth and timing (pipeline light curves) | 161 kB |
| [evidence/figures/04_centroid.png](evidence/figures/04_centroid.png) | Diagnostic plot: out-of-transit and difference images | 93 kB |
| [evidence/figures/05_extra_signals.png](evidence/figures/05_extra_signals.png) | Diagnostic plot: residual period search and stellar variability | 114 kB |
| [evidence/figures/06_independent_photometry.png](evidence/figures/06_independent_photometry.png) | Diagnostic plot: own photometry folded, odd/even, timing, full orbit | 132 kB |

## Script output

| File | What it is | Size |
|---|---|---|
| [evidence/logs/08_vet_lc.txt](evidence/logs/08_vet_lc.txt) | Output of 08_vet_lc.py: odd/even, per-sector depth, secondary scan (pipeline light curves) | 793 B |
| [evidence/logs/09_phasecurve.txt](evidence/logs/09_phasecurve.txt) | Output of 09_phasecurve.py: ellipsoidal amplitude and mass limit (E11) | 762 B |
| [evidence/logs/10_centroid.txt](evidence/logs/10_centroid.txt) | Output of 10_centroid.py: centroid offsets (E4) | 1 kB |
| [evidence/logs/11_sector102_and_sector1.txt](evidence/logs/11_sector102_and_sector1.txt) | Output of 11_s102_and_s1.py: sector 102 corner source and sector 1 coverage | 794 B |
| [evidence/logs/14_apertures.txt](evidence/logs/14_apertures.txt) | Output of 14_apertures.py: depth vs aperture, sector 105 timing, depth vs reduction (E6, E7, E12) | 3 kB |
| [evidence/logs/15_extra_signals.txt](evidence/logs/15_extra_signals.txt) | Output of 15_extra_signals.py: residual search and variability (E13) | 2 kB |
| [evidence/logs/17_own_checks.txt](evidence/logs/17_own_checks.txt) | Output of 17_own_checks.py: odd/even, secondary and timing on own photometry (E9, E10, E12) | 486 B |
| [evidence/logs/fit_free.txt](evidence/logs/fit_free.txt) | MCMC transit fit, pipeline light curves, stellar density free | 927 B |
| [evidence/logs/fit_free_own.txt](evidence/logs/fit_free_own.txt) | MCMC transit fit, own photometry, stellar density free | 942 B |
| [evidence/logs/fit_prior.txt](evidence/logs/fit_prior.txt) | MCMC transit fit, pipeline light curves, stellar density prior | 921 B |
| [evidence/logs/fit_prior_own.txt](evidence/logs/fit_prior_own.txt) | MCMC transit fit, own photometry, stellar density prior | 929 B |
| [evidence/logs/triceratops_mission.txt](evidence/logs/triceratops_mission.txt) | TRICERATOPS output, 12 runs of 10^6 samples (not converged) | 6 kB |

## Catalogue records

| File | What it is | Size |
|---|---|---|
| [evidence/catalogues/crossmatch_results.csv](evidence/catalogues/crossmatch_results.csv) | Result of each catalogue cross-match (E14) | 2 kB |
| [evidence/catalogues/exofop_target.json](evidence/catalogues/exofop_target.json) | ExoFOP-TESS record of the target (no TOI or CTOI) | 7 kB |
| [evidence/catalogues/gaia_neighbors.csv](evidence/catalogues/gaia_neighbors.csv) | Gaia DR3 query result, all columns, 150 arcsec cone | 8 kB |
| [evidence/catalogues/gaia_target.json](evidence/catalogues/gaia_target.json) | Gaia DR3 record of the target star | 1 kB |
| [evidence/catalogues/mast_products.json](evidence/catalogues/mast_products.json) | MAST archive identifiers of the pipeline products used | 2 kB |
| [evidence/catalogues/triceratops_probs_mission1e7.csv](evidence/catalogues/triceratops_probs_mission1e7.csv) | TRICERATOPS best-fit parameters per scenario, pipeline light curve | 3 kB |
| [evidence/catalogues/triceratops_probs_own1e7.csv](evidence/catalogues/triceratops_probs_own1e7.csv) | TRICERATOPS best-fit parameters per scenario, own photometry | 3 kB |

## Posterior samples

| File | What it is | Size |
|---|---|---|
| [evidence/posteriors/chain_free.npy](evidence/posteriors/chain_free.npy) | Posterior samples (NumPy), pipeline light curves, density free. Columns: T0, P, Rp/Rs, b, ln(density), u1, u2 | 1.6 MB |
| [evidence/posteriors/chain_free_own.npy](evidence/posteriors/chain_free_own.npy) | Posterior samples (NumPy), own photometry, density free | 1.6 MB |
| [evidence/posteriors/chain_prior.npy](evidence/posteriors/chain_prior.npy) | Posterior samples (NumPy), pipeline light curves, density prior | 1.6 MB |
| [evidence/posteriors/chain_prior_own.npy](evidence/posteriors/chain_prior_own.npy) | Posterior samples (NumPy), own photometry, density prior | 1.6 MB |

## Pipeline light curves as downloaded

| File | What it is | Size |
|---|---|---|
| [evidence/raw/hlsp_qlp_tess_ffi_s0068-0000000219329329_tess_v01_llc.fits](evidence/raw/hlsp_qlp_tess_ffi_s0068-0000000219329329_tess_v01_llc.fits) | QLP light curve as downloaded from MAST, sector 68 (FITS) | 708 kB |
| [evidence/raw/hlsp_qlp_tess_ffi_s0095-0000000219329329_tess_v01_llc.fits](evidence/raw/hlsp_qlp_tess_ffi_s0095-0000000219329329_tess_v01_llc.fits) | QLP light curve as downloaded from MAST, sector 95 (FITS) | 648 kB |
| [evidence/raw/hlsp_qlp_tess_ffi_s0102-0000000219329329_tess_v01_llc.fits](evidence/raw/hlsp_qlp_tess_ffi_s0102-0000000219329329_tess_v01_llc.fits) | QLP light curve as downloaded from MAST, sector 102 (FITS) | 634 kB |
| [evidence/raw/hlsp_qlp_tess_ffi_s0103-0000000219329329_tess_v01_llc.fits](evidence/raw/hlsp_qlp_tess_ffi_s0103-0000000219329329_tess_v01_llc.fits) | QLP light curve as downloaded from MAST, sector 103 (FITS) | 668 kB |
| [evidence/raw/hlsp_qlp_tess_ffi_s0104-0000000219329329_tess_v01_llc.fits](evidence/raw/hlsp_qlp_tess_ffi_s0104-0000000219329329_tess_v01_llc.fits) | QLP light curve as downloaded from MAST, sector 104 (FITS) | 683 kB |
| [evidence/raw/hlsp_tess-spoc_tess_phot_0000000219329329-s0068_tess_v1_lc.fits](evidence/raw/hlsp_tess-spoc_tess_phot_0000000219329329-s0068_tess_v1_lc.fits) | TESS-SPOC light curve as downloaded from MAST, sector 68 (FITS) | 1.2 MB |

## Analysis scripts

| File | What it is | Size |
|---|---|---|
| [scripts/01_search.py](scripts/01_search.py) | List TESS data available at MAST | 739 B |
| [scripts/02_download.py](scripts/02_download.py) | Download pipeline light curves and the pixel file | 693 B |
| [scripts/03_firstlook.py](scripts/03_firstlook.py) | Plot raw light curves | 1 kB |
| [scripts/04_search.py](scripts/04_search.py) | Detrend and run the period search | 4 kB |
| [scripts/05_gaia.py](scripts/05_gaia.py) | Gaia DR3 query for the target and neighbours | 3 kB |
| [scripts/06_fit.py](scripts/06_fit.py) | MCMC transit fit | 4 kB |
| [scripts/07_tesscut.py](scripts/07_tesscut.py) | Download full-frame image cutouts | 503 B |
| [scripts/08_vet_lc.py](scripts/08_vet_lc.py) | Odd/even, secondary and per-transit tests on pipeline light curves | 7 kB |
| [scripts/09_phasecurve.py](scripts/09_phasecurve.py) | Out-of-transit phase variations and mass limit | 3 kB |
| [scripts/10_centroid.py](scripts/10_centroid.py) | Difference-image centroid test | 5 kB |
| [scripts/11_s102_and_s1.py](scripts/11_s102_and_s1.py) | Sector 102 corner source and sector 1 coverage | 3 kB |
| [scripts/12_prep_tri.py](scripts/12_prep_tri.py) | Prepare inputs for TRICERATOPS | 1 kB |
| [scripts/13_triceratops.py](scripts/13_triceratops.py) | Run TRICERATOPS | 3 kB |
| [scripts/14_apertures.py](scripts/14_apertures.py) | Own photometry, depth vs aperture and reduction, sector 105 timing | 8 kB |
| [scripts/15_extra_signals.py](scripts/15_extra_signals.py) | Search for other signals and stellar variability | 5 kB |
| [scripts/16_catalogues.py](scripts/16_catalogues.py) | SIMBAD and VizieR cross-matches | 4 kB |
| [scripts/17_own_checks.py](scripts/17_own_checks.py) | Odd/even, secondary and timing on own photometry | 6 kB |
| [scripts/18_export_site.py](scripts/18_export_site.py) | Export the data shown on this site | 14 kB |
| [scripts/19_site_manifest.py](scripts/19_site_manifest.py) | Write this file list and the folder index pages | 14 kB |
| [scripts/common.py](scripts/common.py) | Shared loaders, detrending and transit model | 5 kB |
