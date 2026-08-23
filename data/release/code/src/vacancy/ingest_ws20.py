#!/usr/bin/env python3
"""Phase 0.1: Wlodarczyk-Sroka+2020 (VizieR J/MNRAS/498/5720/catalog) の TSV を読み、
機械可読性実査用の統計と、Phase 1 台帳用の中間 npz を出す。"""
import sys, os, json, numpy as np
RAW = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
src = os.path.join(RAW, "ws20_catalog.tsv")
rows = []
with open(src) as f:
    hdr = None
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.rstrip("\n").split("\t")
        if hdr is None:
            hdr = [p.strip() for p in parts]; continue
        if parts[0].strip() in ("", "deg", "---") or set(parts[0].strip()) <= set("-"):
            continue
        rows.append([p.strip() for p in parts])
print("header", hdr)
print("rows", len(rows))
col = {h: i for i, h in enumerate(hdr)}
def num(name):
    i = col[name]; out = np.full(len(rows), np.nan)
    for k, r in enumerate(rows):
        v = r[i] if i < len(r) else ""
        if v not in ("", "---"):
            try: out[k] = float(v)
            except ValueError: pass
    return out
def strcol(name):
    i = col[name]; return np.array([(r[i] if i < len(r) else "") for r in rows])
dr2 = strcol("GaiaDR2"); target = strcol("Target"); inst = strcol("InstS"); price = strcol("Price-target?")
eirp = num("min-detec-EIRP"); rest = num("rest"); plx = num("Plx"); fwhm = num("FWHM"); off = num("Offset-arcmin"); resp = num("TelResGaus")
gmag = num("Gmag"); ra = num("RA_ICRS"); de = num("DE_ICRS"); pmra = num("pmRA"); pmde = num("pmDE"); bprp = num("BP-RP")
stats = {
  "n_rows": len(rows), "n_distinct_dr2": int(len(set(dr2))),
  "n_rows_price_target": int((price == "true").sum()), "n_distinct_price_targets": int(len(set(dr2[price == "true"]))),
  "n_distinct_targets_field": int(len(set(target))),
  "inst_counts": {k: int((inst == k).sum()) for k in sorted(set(inst))},
  "null_rates": {k: float(np.isnan(v).mean()) for k, v in [("min-detec-EIRP", eirp), ("rest", rest), ("Plx", plx), ("FWHM", fwhm), ("Offset-arcmin", off), ("TelResGaus", resp), ("Gmag", gmag), ("pmRA", pmra), ("BP-RP", bprp)]},
  "rest_le_100pc_rows": int((rest <= 100).sum()), "rest_le_100pc_distinct": int(len(set(dr2[rest <= 100]))),
  "rest_le_50pc_distinct": int(len(set(dr2[rest <= 50]))),
  "eirp_quantiles_W": {q: float(np.nanquantile(eirp, float(q))) for q in ["0.01", "0.1", "0.5", "0.9", "0.99"]},
  "eirp_le_1e13_distinct": int(len(set(dr2[eirp <= 1e13]))), "eirp_le_1e17_distinct": int(len(set(dr2[eirp <= 1e17]))),
}
# EIRP 再計算検査: EIRP = EIRP50(inst) * (d/50)^2 / resp  (Gaussian 応答 resp = exp(-4 ln2 (off/FWHM)^2))
e50 = np.where(np.char.startswith(inst.astype(str), "Parkes"), 9.1e12, 2.1e12)
resp_calc = np.exp(-4 * np.log(2) * (off / fwhm) ** 2)
eirp_calc = e50 * (rest / 50.0) ** 2 / resp_calc
ok = np.isfinite(eirp) & np.isfinite(eirp_calc) & (eirp > 0)
ratio = eirp_calc[ok] / eirp[ok]
stats["eirp_recalc_check"] = {"n": int(ok.sum()), "median_ratio": float(np.median(ratio)), "p05": float(np.quantile(ratio, .05)), "p95": float(np.quantile(ratio, .95)),
                              "resp_median_abs_diff": float(np.nanmedian(np.abs(resp_calc - resp)))}
print(json.dumps(stats, indent=1, ensure_ascii=False))
json.dump(stats, open(os.path.join(RAW, "..", "phase0", "ws20_stats.json"), "w"), indent=1, ensure_ascii=False)
np.savez_compressed(os.path.join(RAW, "..", "phase0", "ws20_rows.npz"), dr2=dr2, target=target, inst=inst, price=price, eirp=eirp, rest=rest, plx=plx, fwhm=fwhm, off=off, resp=resp, gmag=gmag, ra=ra, de=de, pmra=pmra, pmde=pmde, bprp=bprp)
