# TIC 219329329 — planet-candidate vetting report

Date: 2026-11-10. Data: TESS sectors 68, 95, 102, 103, 104, 105 (200 s full-frame images).

## Verdict

**Likely planet, not validated.** The signal is real, sits on the target star, and passes every false-positive test run here.
It falls short of validation for two reasons:

1. The TRICERATOPS false-positive probability is about 6% (see below). The usual validation threshold is 1.5%.
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

## Not done or not resolved

- No mass measurement, no spectroscopy, no high-resolution imaging, no ground-based or multi-colour photometry.
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
- `scripts/` — analysis code, numbered in the order it was run
