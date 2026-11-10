import sys, os, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from astropy.io import fits
from common import *
root, out = sys.argv[1], sys.argv[2]
best = np.load(os.path.join(out, "best_prior.npy")); T0, P = best[0], best[1]
d = np.load(os.path.join(out, "lc_final.npz")); t, f, e, s = d["t"], d["f"], d["e"], d["s"]
ph = ((t - T0 + 0.5 * P) % P) - 0.5 * P
k = np.abs(ph) < 0.2
edges = np.linspace(-0.2, 0.2, 121); c = 0.5 * (edges[1:] + edges[:-1]); idx = np.digitize(ph[k], edges) - 1
w = 1 / e[k] ** 2
fb = np.array([np.sum(w[idx == i] * f[k][idx == i]) / np.sum(w[idx == i]) for i in range(120)])
eb = np.array([1 / np.sqrt(np.sum(w[idx == i])) for i in range(120)])
np.savetxt(os.path.join(out, "tri_folded.txt"), np.c_[c, fb, eb])
print("binned points 120, bin width %.2f min, median err %.0f ppm, T0=%.5f P=%.6f" % (0.4 / 120 * 1440, np.median(eb) * 1e6, T0, P))
qlp, spoc, tpf = find_files(root)
with fits.open(tpf[0]) as h:
    ap = h[2].data; hd = h[2].header
    c0, r0 = hd["CRVAL1P"], hd["CRVAL2P"]
    ys, xs = np.where((ap & 2) > 0)
    pix = np.c_[xs + c0, ys + r0]
    print("SPOC S68 optimal aperture: %d pixels; FFI col,row:" % len(pix)); print(pix.tolist())
np.savetxt(os.path.join(out, "tri_aperture_s68.txt"), pix, fmt="%d")
