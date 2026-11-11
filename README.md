# TIC 219329329.01 — evidence for a hot-Jupiter candidate

A static website that presents the vetting evidence for a planet candidate found in public TESS data.

**Status: likely planet, not validated.** The transit is real and on the target star, and it passes every false-positive test run so far. The TRICERATOPS false-positive probability is about 6% from the transit alone and about 3–4% with whole-orbit limits added (validation needs under 1.5%), and the companion's mass has not been measured.

Independent analysis of public data, prepared with AI assistance. Not peer reviewed.

## What is here

| Path | Contents |
|---|---|
| `index.html` | The page. Every piece of evidence has its own anchor, for example `#centroid` or `#fpp` |
| `assets/` | Styles, the chart code, and the data bundle the page reads (`data.js`, `files.js`) |
| `data/` | CSV and JSON files behind every chart and table |
| `evidence/` | Written report, diagnostic plots, script output, catalogue records, posterior samples, pipeline light curves |
| `scripts/` | The analysis code, numbered in the order it was run |
| `FILES.md` | A list of every file with a one-line description |

There is no build step. Any static file server can host the folder as it is. All links are relative, so it also works under a sub-path.

To look at it locally:

```bash
python3 -m http.server 8765
```

Then open `http://localhost:8765`.

## Evidence anchors

| ID | Anchor | Evidence |
|---|---|---|
| E1 | `#transit` | Folded transit |
| E2 | `#light-curves` | Transits in every sector |
| E3 | `#period-search` | Period search |
| E4 | `#centroid` | Difference images |
| E5 | `#neighbours` | Neighbouring stars |
| E6 | `#aperture` | Depth against aperture size |
| E7 | `#reduction` | Depth against reduction choices |
| E8 | `#density` | Stellar density from the transit shape |
| E9 | `#odd-even` | Odd against even transits |
| E10 | `#secondary` | No secondary eclipse |
| E11 | `#ellipsoidal` | Tidal distortion and mass limit |
| E12 | `#timing` | Timing and the held-out sector |
| E13 | `#other-signals` | No other signals |
| E14 | `#catalogues` | Catalogue checks |
| E15 | `#fpp` | False-positive probability |
| E16 | `#asassn` | Independent detection in ASAS-SN ground-based photometry |
| E17 | `#fpp-phase` | False-positive probability with whole-orbit limits |
| E18 | `#archival-spectra` | Archival spectra search |

Other anchors: `#summary`, `#further-checks`, `#parameters`, `#open-issues`, `#follow-up`, `#files`, `#sources`.

## Regenerating the data

The scripts expect Python 3.11 with numpy, scipy, astropy, astroquery, lightkurve, batman-package, emcee, wotan, pandas and matplotlib. TRICERATOPS 1.1.0 needs its own environment with numpy below 1.24 and setuptools below 81.

1. `01`–`07` download the TESS products and query Gaia.
2. `04`, `06`, `08`–`17` run the search, the fits and each test.
3. `18_export_site.py` and `19_site_manifest.py` rebuild `data/`, `evidence/`, `assets/data.js`, `assets/files.js` and `FILES.md`.

Each script lists its arguments at the top or takes the folders as positional arguments.

## Data credits

TESS mission data from the MAST archive (TESS-SPOC and QLP light curves, TESScut full-frame cutouts). Gaia DR3 from the ESA Gaia archive. ASAS-SN Sky Patrol ground-based photometry. Software: TRICERATOPS, lightkurve, astropy, astroquery, batman, emcee, wotan.
