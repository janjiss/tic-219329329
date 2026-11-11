"""Fetch the ASAS-SN Sky Patrol v2 light curve of the target and save it.  usage: 20_asassn.py <out_csv>"""
import sys, warnings; warnings.filterwarnings("ignore")

def main():
    from pyasassn.client import SkyPatrolClient
    client = SkyPatrolClient(verbose=False)
    res = client.cone_search(ra_deg=335.349584, dec_deg=-55.837438, radius=8, units="arcsec", catalog="master_list", download=False)
    print(res.to_string() if len(res) else "no ASAS-SN source within 8 arcsec")
    if not len(res): return
    lcs = client.cone_search(ra_deg=335.349584, dec_deg=-55.837438, radius=8, units="arcsec", catalog="master_list", download=True, threads=1)
    df = lcs.data
    print("columns:", list(df.columns)); print("rows:", len(df))
    df.to_csv(sys.argv[1], index=False)
    print(df.groupby("phot_filter").agg(n=("jd", "size"), jd_min=("jd", "min"), jd_max=("jd", "max"), mag_med=("mag", "median"), err_med=("mag_err", "median")).to_string())
    print("cameras:", sorted(df["camera"].unique()))

if __name__ == "__main__":      # the client starts worker processes, which re-import this file on macOS
    main()
