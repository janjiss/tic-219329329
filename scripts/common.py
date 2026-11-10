"""Shared loaders for TIC 219329329 light curves."""
import glob, os, numpy as np
from astropy.io import fits

def load_qlp(path, flux="sap"):
    with fits.open(path) as h:
        d = h[1].data; hdr = h[0].header
        t = np.array(d["TIME"], float)
        q = np.array(d["QUALITY"], int)
        col = {"sap": "SAP_FLUX", "det": "DET_FLUX", "kspsap": "KSPSAP_FLUX"}[flux]
        f = np.array(d[col], float)
        try: e = np.array(d["DET_FLUX_ERR"], float)
        except Exception: e = np.full_like(f, np.nan)
        bkg = np.array(d["SAP_BKG"], float)
        x = np.array(d["SAP_X"], float); y = np.array(d["SAP_Y"], float)
        sector = hdr.get("SECTOR")
    ok = np.isfinite(t) & np.isfinite(f) & (q == 0)
    return dict(t=t[ok], f=f[ok], e=e[ok], bkg=bkg[ok], x=x[ok], y=y[ok], sector=sector, src="QLP")

def load_spoc(path, flux="PDCSAP_FLUX"):
    with fits.open(path) as h:
        d = h[1].data; hdr = h[0].header
        t = np.array(d["TIME"], float); q = np.array(d["QUALITY"], int)
        f = np.array(d[flux], float); e = np.array(d[flux + "_ERR"], float)
        bkg = np.array(d["SAP_BKG"], float)
        x = np.array(d["MOM_CENTR1"], float); y = np.array(d["MOM_CENTR2"], float)
        sector = hdr.get("SECTOR")
    ok = np.isfinite(t) & np.isfinite(f) & (q == 0)
    med = np.nanmedian(f[ok])
    return dict(t=t[ok], f=f[ok] / med, e=e[ok] / med, bkg=bkg[ok], x=x[ok], y=y[ok], sector=sector, src="SPOC")

def find_files(root):
    qlp = sorted(glob.glob(os.path.join(root, "**", "hlsp_qlp_*_llc.fits"), recursive=True))
    spoc = sorted(glob.glob(os.path.join(root, "**", "hlsp_tess-spoc_*_lc.fits"), recursive=True))
    tpf = sorted(glob.glob(os.path.join(root, "**", "hlsp_tess-spoc_*_tp.fits"), recursive=True))
    return qlp, spoc, tpf

# ---------- detrending ----------
def segs(t, gap=0.5):
    idx = np.where(np.diff(t) > gap)[0] + 1
    return np.split(np.arange(len(t)), idx)

def detrend(lc, P=None, T0=None, half_mask=0.11, win=1.0, trim=0.0, key="f"):
    """Biweight detrend per contiguous segment, in-transit cadences excluded from the trend."""
    from wotan import flatten
    t, f = lc["t"], lc[key] / np.nanmedian(lc[key])
    T, F, S, TR = [], [], [], []
    for s in segs(t):
        tt, ff = t[s], f[s]
        if len(tt) < 50: continue
        if trim > 0:
            k = tt > tt[0] + trim; tt, ff = tt[k], ff[k]
            if len(tt) < 50: continue
        ff2 = ff.copy()
        if P is not None:
            ph = ((tt - T0 + 0.5 * P) % P) - 0.5 * P
            ff2[np.abs(ph) < half_mask] = np.nan
        fl, tr = flatten(tt, ff2, method="biweight", window_length=win, edge_cutoff=0.0, return_trend=True)
        good = np.isfinite(tr)
        if good.sum() < 10: continue
        tr = np.interp(tt, tt[good], tr[good])
        T.append(tt); F.append(ff / tr); S.append(np.full(len(tt), lc["sector"])); TR.append(tr)
    return np.concatenate(T), np.concatenate(F), np.concatenate(S), np.concatenate(TR)

def build(root, P, T0, win=1.0, qlp_key="sap", spoc68=True):
    qlp, spoc, tpf = find_files(root)
    lcs = ([load_spoc(spoc[0])] if spoc68 else []) + [load_qlp(p, qlp_key) for p in qlp if not (spoc68 and "s0068" in p)]
    T, F, S, E = [], [], [], []
    for lc in lcs:
        t, f, s, tr = detrend(lc, P, T0, win=win, trim=0.0 if lc["src"] == "SPOC" else 0.3)
        ph = ((t - T0 + 0.5 * P) % P) - 0.5 * P
        oot = np.abs(ph) > 0.15
        sig = 1.4826 * np.nanmedian(np.abs(f[oot] - np.nanmedian(f[oot])))
        k = np.isfinite(f) & (f < 1 + 5 * sig) & (f > 1 - 12 * sig)
        T.append(t[k]); F.append(f[k]); S.append(s[k]); E.append(np.full(k.sum(), sig))
    return np.concatenate(T), np.concatenate(F), np.concatenate(E), np.concatenate(S)

def aRs(rho, P):
    return 4.2075 * rho ** (1 / 3.0) * P ** (2 / 3.0)

# ---------- transit template ----------
def tmodel(tt, T0_, P_, k, b, a, u=(0.32, 0.25), exp=200 / 86400., ss=3):
    import batman
    pm = batman.TransitParams(); pm.ecc, pm.w, pm.limb_dark, pm.u = 0., 90., "quadratic", list(u)
    pm.t0, pm.per, pm.rp, pm.a = T0_, P_, k, a
    pm.inc = np.degrees(np.arccos(min(b / a, 1.0)))
    return batman.TransitModel(pm, np.ascontiguousarray(tt, dtype=float), supersample_factor=ss, exp_time=exp).light_curve(pm)

def amp_fit(t, f, e, shape, mask=None):
    """Linear amplitude of a positive dip template `shape(t)`; returns (A, sigma_A)."""
    if mask is None: mask = np.ones(len(t), bool)
    x = shape(t[mask]); y = 1 - f[mask]; w = 1 / e[mask] ** 2
    return np.sum(w * x * y) / np.sum(w * x * x), 1 / np.sqrt(np.sum(w * x * x))
