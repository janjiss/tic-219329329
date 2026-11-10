import warnings, sys; warnings.filterwarnings("ignore")
import lightkurve as lk, numpy as np
out = sys.argv[1]
tic = "TIC 219329329"
sr = lk.search_lightcurve(tic)
for i in range(len(sr)):
    r = sr[i]
    lc = r.download(download_dir=out, quality_bitmask="default")
    f = lc.flux.value; t = lc.time.value
    ok = np.isfinite(f)
    print(r.mission[0], r.author[0], "N=%d"%ok.sum(), "t=%.2f-%.2f"%(np.nanmin(t), np.nanmax(t)),
          "cols:", [c for c in lc.colnames][:14], "| file:", lc.meta.get("FILENAME"))
tp = lk.search_targetpixelfile(tic)
for i in range(len(tp)):
    tpf = tp[i].download(download_dir=out)
    print("TPF", tp[i].mission[0], tpf.shape, tpf.meta.get("FILENAME"))
