import warnings, sys, os; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from astroquery.gaia import Gaia
out = sys.argv[1]
ra, dec = 335.349583800419, -55.837437814740497
q = f"""
SELECT g.source_id, g.ra, g.dec, g.parallax, g.parallax_error, g.pmra, g.pmdec,
       g.phot_g_mean_mag, g.phot_bp_mean_mag, g.phot_rp_mean_mag, g.bp_rp,
       g.ruwe, g.astrometric_excess_noise, g.astrometric_excess_noise_sig,
       g.ipd_frac_multi_peak, g.ipd_gof_harmonic_amplitude, g.duplicated_source,
       g.radial_velocity, g.radial_velocity_error, g.rv_nb_transits, g.rv_amplitude_robust,
       g.rv_chisq_pvalue, g.rv_renormalised_gof,
       g.non_single_star, g.phot_variable_flag, g.teff_gspphot, g.logg_gspphot, g.mh_gspphot,
       g.distance_gspphot, g.ag_gspphot, g.visibility_periods_used,
       DISTANCE(POINT(g.ra, g.dec), POINT({ra}, {dec}))*3600 AS sep_arcsec
FROM gaiadr3.gaia_source AS g
WHERE 1 = CONTAINS(POINT(g.ra, g.dec), CIRCLE({ra}, {dec}, {150/3600.}))
ORDER BY sep_arcsec
"""
df = Gaia.launch_job(q).get_results().to_pandas()
df.to_csv(os.path.join(out, "gaia_neighbors.csv"), index=False)
t = df.iloc[0]
print("=== target ===")
for c in df.columns: print(f"  {c:32s} {t[c]}")
# approximate T mag from G, BP-RP (Stassun+2019)
def tmag(G, bprp):
    if np.isfinite(bprp):
        return G - 0.00522555*bprp**3 + 0.0891337*bprp**2 - 0.633923*bprp + 0.0324473
    return G - 0.430
df["T"] = [tmag(g, c) for g, c in zip(df.phot_g_mean_mag, df.bp_rp)]
df["dT"] = df["T"] - df["T"].iloc[0]
df["flux_ratio"] = 10**(-0.4*df["dT"])
pd.set_option("display.width", 250)
print("=== neighbours within 150 arcsec: N =", len(df)-1)
print(df[["source_id","sep_arcsec","phot_g_mean_mag","bp_rp","T","dT","flux_ratio","parallax","pmra","pmdec","ruwe"]].head(40).to_string())
print("sum flux ratio within 21\":", df[(df.sep_arcsec>0.01)&(df.sep_arcsec<21)].flux_ratio.sum())
print("sum flux ratio within 63\":", df[(df.sep_arcsec>0.01)&(df.sep_arcsec<63)].flux_ratio.sum())
# astrophysical params
q2 = f"""SELECT source_id, teff_gspphot, logg_gspphot, mh_gspphot, radius_gspphot, radius_flame, lum_flame, mass_flame, age_flame,
 teff_gspspec, logg_gspspec, mh_gspspec, classprob_dsc_combmod_star, evolstage_flame, flags_flame
 FROM gaiadr3.astrophysical_parameters WHERE source_id = {int(t.source_id)}"""
ap = Gaia.launch_job(q2).get_results().to_pandas()
print("=== astrophysical_parameters ==="); print(ap.T.to_string())
for tab in ("nss_two_body_orbit","nss_acceleration_astro","nss_non_linear_spectro","vari_summary"):
    try:
        r = Gaia.launch_job(f"SELECT * FROM gaiadr3.{tab} WHERE source_id = {int(t.source_id)}").get_results()
        print(tab, "rows:", len(r))
    except Exception as e:
        print(tab, "ERR", str(e)[:100])
