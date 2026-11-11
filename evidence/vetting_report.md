# TIC 219329329 — planet-candidate vetting report

Date: 2026-11-10, updated 2026-11-11 with three further desk checks (see "Additional checks"). Data: TESS sectors 68, 95, 102, 103, 104, 105 (200 s full-frame images); ASAS-SN V and g photometry, 2014–2025.

## Verdict

**Likely planet, not validated.** The signal is real, sits on the target star, and passes every false-positive test run here.
It falls short of validation for two reasons:

1. The TRICERATOPS false-positive probability is about 6% as published, and about 3–4% once the missing secondary eclipse and tidal distortion are folded in (see "Additional checks"). The usual validation threshold is 1.5%.
2. The companion is about 1.2 Jupiter radii. Planets, brown dwarfs and the smallest stars all have that radius, so only a mass measurement can confirm a planet. The light curve limits the mass to below about 87 Jupiter masses (3σ).

The target is not a TOI or CTOI on ExoFOP and has no SIMBAD entry.

## Host star

| Quantity | Value | Source |
|---|---|---|
| Position (J2000) | RA 335.34958°, Dec −55.83744° | Gaia DR3 6507925182103208960 |
| Brightness | T = 12.41, G = 12.79, V ≈ 12.9 | TIC 8.2, Gaia DR3 |
| Teff | 5920–6090 K | Gaia GSP-Phot, TIC |
| Radius | 1.21 ± 0.06 R_Sun | TIC (Gaia FLAME: 1.23) |
| Mass | 1.05–1.14 M_Sun | Gaia FLAME, TIC |
| Distance | 552 pc | Gaia DR3 parallax 1.811 ± 0.018 mas |
| RUWE | 1.27 | Gaia DR3 |

## Candidate parameters

Two independent reductions were fitted (circular orbit, quadratic limb darkening, stellar density left free).

| Parameter | Pipeline light curves (5 sectors) | Own FFI photometry (6 sectors) |
|---|---|---|
| Period (d) | 3.481585 ± 0.000003 | 3.481584 ± 0.000003 |
| Mid-transit (BTJD) | 4135.85703 ± 0.00042 | 4156.74624 ± 0.00039 |
| Rp/Rs | 0.1011 (+0.0043 / −0.0027) | 0.1047 (+0.0025 / −0.0021) |
| Impact parameter | 0.892 (+0.019 / −0.022) | 0.870 ± 0.016 |
| a/Rs | 8.18 (+0.44 / −0.38) | 8.70 (+0.38 / −0.34) |
| Inclination (deg) | 83.7 ± 0.5 | 84.3 ± 0.3 |
| Duration T14 (h) | 2.11 ± 0.05 | 2.09 ± 0.05 |
| Mid-transit depth (ppm) | ≈ 8700 | ≈ 9750 |
| Stellar density from transit (solar) | 0.61 (+0.10 / −0.08) | 0.73 (+0.10 / −0.08) |
| Companion radius (R_Jup) | 1.20 (+0.08 / −0.07) | 1.24 ± 0.07 |

Pipeline light curves: TESS-SPOC (sector 68) and QLP (sectors 95, 102, 103, 104).
The QLP light curves give transits about 10% shallower than SPOC and than direct aperture photometry, so the own-photometry column is preferred.
Derived: a ≈ 0.047 AU, equilibrium temperature ≈ 1420–1460 K (zero albedo).
BTJD = BJD_TDB − 2457000.

## Tests

| Test | Result | Outcome |
|---|---|---|
| Odd vs even transit depth | Pipeline: 8648 ± 155 vs 8797 ± 159 ppm (0.7σ). Own: 9787 ± 170 vs 9600 ± 174 ppm (0.8σ) | Pass |
| Secondary eclipse at phase 0.5 | Pipeline: −214 ± 84 ppm. Own: −196 ± 130 ppm. 3σ upper limit ≈ 390 ppm | Pass (does not exclude a very cool companion) |
| Stellar density from transit shape | 0.61–0.73 solar vs 0.56–0.65 from catalogues | Pass |
| Difference-image centroid | On target within ~1″ in 5 of 6 sectors; sector 102 off by 7.8 ± 4.1″ (1.9σ) | Pass |
| Sector 102 corner feature | Wing of a G = 7.7 star 263″ away; its "dip" is one event (1.2σ), not periodic | Explained |
| Depth vs aperture (own photometry) | 2×2: 9753 ± 121, 3×3: 9784 ± 123, 5×5: 9752 ± 156 ppm | Pass |
| Depth vs detrending window | 8692–8777 ppm for 0.5–3 d windows | Pass |
| Neighbouring stars (Gaia DR3) | None within 22″; total flux within 63″ is 0.28% of the target | Pass |
| Ellipsoidal variation | 5 ± 54 ppm → companion < 87 M_Jup (3σ) | Pass (stars excluded, brown dwarfs not) |
| Other periodic dips | None above SDE 6 once data-gap edges are removed | Pass |
| Stellar variability | No power at the orbital period or its half; sector 68 flat to ~200 ppm | Pass |
| Prediction test, sector 105 | Six transits arrive −0.7 ± 1.3 min from prediction | Pass |
| Transit timing, 34 transits | χ² = 38.7 for 32 degrees of freedom | Linear ephemeris holds |
| Catalogue cross-match | Not in VSX, Gaia DR3 variables or eclipsing binaries, ASAS-SN, TESS EB catalogue, WDS or TOI list | No prior flag |
| Gaia multiplicity indicators | No non-single-star solution, no double-peaked scans; RUWE 1.27 is mildly elevated | Inconclusive |

## Statistical false-positive probability (TRICERATOPS 1.1.0)

| Light curve | Runs | FPP | NFPP |
|---|---|---|---|
| Pipeline, 10⁷ samples | 6 | median 0.057, mean 0.080 ± 0.056, range 0.037–0.202 | 0 |
| Pipeline, 10⁶ samples | 12 | mean 0.146 ± 0.132, range 0.005–0.47 (not converged) | 0 |
| Own photometry, 10⁷ samples | 6 | median 0.057, mean 0.057 ± 0.016, range 0.034–0.084 | 0 |

Mean scenario probabilities (pipeline, 10⁷ samples): planet on target 0.73; planet on target with an unresolved bound companion 0.19; eclipsing binary on target with an unresolved companion 0.044; planet on an unresolved bound companion 0.024; eclipsing binary on an unresolved bound companion 0.009.
The own-photometry runs give the same ranking (0.77, 0.17, 0.038, 0.017, 0.001).

- NFPP is zero because no known neighbour is bright enough to cause the dip.
- The remaining false-positive weight is entirely in scenarios that need an unresolved bound companion. High-resolution imaging would constrain those directly.
- TRICERATOPS classes: FPP < 0.015 and NFPP < 0.001 is "validated"; FPP < 0.5 and NFPP < 0.001 is "likely planet". This candidate is in the second class.
- TRICERATOPS does not model brown dwarfs, so the FPP says nothing about that alternative.

## Additional checks (2026-11-11)

### 1. False-positive probability with the rest of the orbit included

TRICERATOPS fits only the light curve around the transit. For scenarios where a star does the eclipsing, two measurements from the rest of the orbit were added as Gaussian terms to each sampled binary (`scripts/21_triceratops_phase.py`):

- No secondary eclipse, used as 0 ± 130 ppm (the measured −196 ppm is not credited).
- No ellipsoidal variation, 5 ± 54 ppm, with the predicted amplitude deliberately under-estimated (coefficient 1.0 instead of about 1.2–1.3).

Planet scenarios are untouched. Twelve runs of 10⁷ samples (six per light curve):

| | Before | With the two limits |
|---|---|---|
| FPP, mean ± standard error | 0.068 ± 0.013 | 0.037 ± 0.008 |
| FPP, median | 0.057 | 0.031 |
| FPP, range | 0.035–0.202 | 0.006–0.091 |
| Runs below 0.015 | 0 of 12 | 3 of 12 |
| Eclipsing binary on target with a hidden companion (PEB) | 0.041 | 0.0016 |
| Eclipsing binary on a hidden bound companion (SEB) | 0.005 | 0.0003 |
| Planet on a hidden bound companion (STP) | 0.021 | 0.034 |
| NFPP | 0 | 0 |

- The eclipsing-binary scenarios drop by factors of roughly 15 to 25. Typical well-fitting binaries predict a secondary eclipse of 400–600 ppm and an ellipsoidal amplitude of 90–160 ppm, neither of which is seen.
- What remains is almost entirely STP, a planet transiting an unseen companion star bound to the target. The two limits do not touch it, and its estimate is noisy from run to run (0.001–0.088), so the two STP values above are the same within sampling error.
- The result is still above the 0.015 validation threshold. This is also not the standard TRICERATOPS procedure, so it should be quoted as "TRICERATOPS plus phase-curve limits".
- Summed over all scenarios, the probability that a planet-size body transits a star in this system (TP + PTP + DTP + STP) is about 0.997. The open questions are which star it orbits and its mass.

### 2. Archival ground-based photometry

| Archive | Result |
|---|---|
| ASAS-SN Sky Patrol v2 | 3385 measurements, 2883 good (V: 2014–2018, g: 2017–2025), 76 in transit |
| SuperWASP public archive (DR1) | Not covered: public coverage in this tile stops at Dec −55.1°; the star is at −55.8° |
| ATLAS forced photometry | Not checked: needs an account |

ASAS-SN, folded on the TESS ephemeris (`scripts/22_asassn_fold.py`, `out/07_asassn.png`):

| Band | Depth (ppm) | Significance | Expected for a planet on the target (ppm) |
|---|---|---|---|
| g | 7645 ± 2041 | 3.7σ | 9027 |
| V | 9863 ± 4922 | 2.0σ | 9349 |
| V + g | 8072 ± 1928 | 4.2σ | 9027 |

- Errors are empirical, from the same template fitted at 500 random phases.
- Sliding the template around the whole orbit gives one feature above 3σ: a 5.0σ dip at −0.004 of a period from the predicted phase (one scan step).
- The ratio of measured to expected depth is 0.89 ± 0.21, so the blue-band depth agrees with the TESS depth. The test is too weak to exclude a moderately redder host.
- ASAS-SN apertures are 16″ in radius, smaller than a TESS pixel, and this is a different instrument.
- The period holds back to 2014, 1258 orbits before the TESS reference epoch.

### 3. Archival spectra

None exist. Checked: ESO archive (no raw or reduced spectra within 30″; only VISTA VHS near-infrared images), GALAH DR4 (no star within 1° of the target), APOGEE DR17 (field not observed), SDSS-V DR19 (the star is only in the targeting database as a potential calibration standard; no APOGEE or BOSS spectra), RAVE DR6 and GALAH DR3 (checked earlier).

## Not done or not resolved

- No mass measurement, no spectroscopy (none in any archive checked), no high-resolution imaging, no multi-colour transit of useful precision.
- Sector 1 (2018) has no usable data: the star fell in the gap between two CCDs.
- The QLP small-aperture light curves give a much shallower and sector-dependent depth (3100–7200 ppm). Direct photometry in a 2×2 pixel aperture does not reproduce this, so it is probably a pipeline normalisation effect, but that was not confirmed.
- The cutout time stamps for sector 105 carry a systematic error of up to about 1.5 min (CCD-centre barycentric correction).
- The Gaia radial velocity (−1.65 ± 1.12 km/s, 34 transits) comes from a stacked cross-correlation and is only a weak constraint on orbital motion.
- The all-catalogue VizieR search failed (server errors); only the targeted catalogues listed above were checked.

## Recommended follow-up

1. Two or three reconnaissance spectra near quadrature. A brown dwarf or M dwarf would show several km/s; a planet would show about 126 m/s per Jupiter mass.
2. High-resolution imaging (speckle or adaptive optics) to rule out close companions and lower the FPP.
3. Ground-based transit photometry in a second band: the event is about 1% deep and lasts 2.1 h.
4. Submit as a CTOI on ExoFOP so follow-up groups can pick it up.

Upcoming mid-transit times (BJD_TDB, ±0.6 min): 2461358.6781, 2461362.1597, 2461365.6413, 2461369.1229, 2461372.6044.

## Files

- `out/01_raw_lightcurves.png` — pipeline light curves per sector
- `out/02_bls.png` — period search and folded transit
- `out/03_vetting_lc.png` — odd/even, secondary, per-transit depth and timing (pipeline light curves)
- `out/04_centroid.png` — out-of-transit and difference images per sector
- `out/05_extra_signals.png` — residual period search and stellar variability
- `out/06_independent_photometry.png` — own photometry: folded transit, odd/even, timing, full orbit
- `out/07_asassn.png` — ASAS-SN g and V folded on the TESS ephemeris, and the phase scan
- `out/asassn_results.json`, `out/asassn_detrended.csv`, `data/asassn/asassn_lightcurve.csv` — ASAS-SN results and data
- `out/logs/21_triceratops_phase_own.txt`, `out/logs/21_triceratops_phase_pipeline.txt` — false-positive runs with the phase-curve limits
- `out/triceratops_runs_*_phase.txt`, `out/triceratops_scenarios_*_phase.csv` — per-run probabilities for those runs
- `scripts/` — analysis code, numbered in the order it was run
