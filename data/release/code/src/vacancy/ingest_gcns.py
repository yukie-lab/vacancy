#!/usr/bin/env python3
"""Phase 0.1: GCNS(VizieR J/A+A/649/A6/table1c)取り込み + 照合率実測。
 (1) GCNS の W3/W4 充足率(T-W1 の Θ_det 見込み)
 (2) WS20(≤120 pc 行)の DR2 → EDR3 位置照合(固有運動で 2015.5→2016.0 補正、半径 1"、G 等級差 <0.5)
 (3) EMBARK アトラス source_id との結合率(0.5)
 (4) BL HIP 目標(HGCA 経由 DR3)の GCNS 内在率
"""
import os, json, numpy as np
HERE = os.path.dirname(__file__)
RAW = os.path.join(HERE, "..", "..", "data", "raw")
P0 = os.path.join(HERE, "..", "..", "data", "phase0")

def read_tsv(path):
    rows = []; hdr = None
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if hdr is None:
                hdr = [p.strip() for p in parts]; continue
            p0 = parts[0].strip()
            if p0 == "" or set(p0) <= set("-") or p0 in ("deg", "mas", "mag"):
                continue
            rows.append([p.strip() for p in parts])
    return hdr, rows

hdr, rows = read_tsv(os.path.join(RAW, "gcns_table1c.tsv"))
col = {h: i for i, h in enumerate(hdr)}
print("GCNS columns", hdr); print("rows", len(rows))
def num(name):
    i = col[name]; out = np.full(len(rows), np.nan)
    for k, r in enumerate(rows):
        v = r[i] if i < len(r) else ""
        if v:
            try: out[k] = float(v)
            except ValueError: pass
    return out
sid = np.array([int(r[col["GaiaEDR3"]]) for r in rows], dtype=np.int64)
ra = num("RA_ICRS"); de = num("DE_ICRS"); plx = num("Plx"); eplx = num("e_Plx"); pmra = num("pmRA"); pmde = num("pmDE")
G = num("Gmag"); BP = num("BPmag"); RP = num("RPmag"); ruwe = num("RUWE"); d50 = num("Dist50") * 1000.0
W1 = num("W1mag"); eW1 = num("e_W1mag"); W2 = num("W2mag"); eW2 = num("e_W2mag"); W3 = num("W3mag"); eW3 = num("e_W3mag"); W4 = num("W4mag"); eW4 = num("e_W4mag")
J = num("Jmag"); H = num("Hmag"); K = num("Ksmag"); eK = num("e_Ksmag"); wdp = num("WDprob")
np.savez_compressed(os.path.join(P0, "gcns_core.npz"), source_id=sid, ra=ra, de=de, plx=plx, eplx=eplx, pmra=pmra, pmde=pmde, G=G, BP=BP, RP=RP, ruwe=ruwe, d50=d50,
                    W1=W1, eW1=eW1, W2=W2, eW2=eW2, W3=W3, eW3=eW3, W4=W4, eW4=eW4, J=J, H=H, K=K, eK=eK, wdprob=wdp)
N = len(rows)
snr3 = 1.0857 / eW3; snr4 = 1.0857 / eW4   # mag 誤差 → S/N 近似
stats = {"n_gcns": N,
  "has_wise_name": int(np.isfinite(W1).sum()),
  "has_W3_mag": int(np.isfinite(W3).sum()), "has_W4_mag": int(np.isfinite(W4).sum()),
  "has_W3_err": int(np.isfinite(eW3).sum()), "has_W4_err": int(np.isfinite(eW4).sum()),
  "W3_snr_ge_3.5": int((snr3 >= 3.5).sum()), "W4_snr_ge_3.5": int((snr4 >= 3.5).sum()),
  "W3_and_W4_snr_ge_3.5": int(((snr3 >= 3.5) & (snr4 >= 3.5)).sum()),
  "has_BP_RP": int((np.isfinite(BP) & np.isfinite(RP)).sum()),
  "wdprob_gt_0.5": int((wdp > 0.5).sum()),
}
MG = G + 5 - 5 * np.log10(d50)
c = BP - RP
giant = (MG < 4) & (MG < 7 * c - 3)
wd_aen = MG > 3 * c + 5
ms = np.isfinite(c) & ~giant & ~wd_aen & (ruwe < 1.4)
stats["hephaistos_ms_selection"] = {"n_ms_ruwe_lt_1.4": int(ms.sum()), "n_giant_cut": int(giant.sum()), "n_wd_aen_cut": int(wd_aen.sum()),
                                    "n_ms_with_W3W4_snr3.5": int((ms & (snr3 >= 3.5) & (snr4 >= 3.5)).sum())}

# (2) WS20 DR2 → EDR3 位置照合
w = np.load(os.path.join(P0, "ws20_rows.npz"), allow_pickle=True)
sel = w["rest"] <= 120
dr2 = w["dr2"][sel]; wra = w["ra"][sel]; wde = w["de"][sel]; wpmra = w["pmra"][sel]; wpmde = w["pmde"][sel]; wG = w["gmag"][sel]
# 一意化
u, idx = np.unique(dr2, return_index=True)
wra, wde, wpmra, wpmde, wG = wra[idx], wde[idx], wpmra[idx], wpmde[idx], wG[idx]
# 2015.5 → 2016.0 (0.5 yr) 補正
dt = 0.5
wra2 = wra + dt * np.nan_to_num(wpmra) / 3.6e6 / np.cos(np.radians(wde))
wde2 = wde + dt * np.nan_to_num(wpmde) / 3.6e6
# GCNS 側を 3D 単位ベクトルで近傍探索(総当たりは 1.7k × 331k = 5.6e8 → 分割)
def unit(r, d):
    r = np.radians(r); d = np.radians(d)
    return np.stack([np.cos(d) * np.cos(r), np.cos(d) * np.sin(r), np.sin(d)], -1)
U = unit(ra, de); V = unit(wra2, wde2)
match = np.full(len(u), -1); sep = np.full(len(u), np.nan)
for a in range(0, len(u), 200):
    dots = V[a:a + 200] @ U.T
    j = dots.argmax(axis=1)
    s = np.degrees(np.arccos(np.clip(dots[np.arange(len(j)), j], -1, 1))) * 3600
    match[a:a + 200] = j; sep[a:a + 200] = s
ok = (sep <= 1.0) & (np.abs(wG - G[match]) < 0.5)
ok_pos_only = sep <= 1.0
stats["ws20_dr2_to_edr3"] = {"n_ws20_distinct_le120pc": int(len(u)), "matched_1arcsec_and_dG_lt_0.5": int(ok.sum()), "matched_1arcsec": int(ok_pos_only.sum()),
                             "rate": float(ok.mean()), "sep_median_arcsec": float(np.nanmedian(sep[ok]))}
json.dump({str(u[k]): int(sid[match[k]]) for k in range(len(u)) if ok[k]}, open(os.path.join(P0, "ws20_dr2_to_edr3.json"), "w"))

# (3) EMBARK 結合率
emb = json.load(open(os.path.join(HERE, "..", "..", "..", "embark", "data", "release", "embark_atlas_v1.json")))
esid = np.array([int(x) for x in emb["stars"]["source_id_str"]], dtype=np.int64)
gset = set(sid.tolist())
in_g = np.fromiter((x in gset for x in esid.tolist()), dtype=bool, count=len(esid))
stats["embark_join"] = {"n_embark_stars": int(len(esid)), "in_gcns": int(in_g.sum()), "rate": float(in_g.mean()),
                        "embark_schema": emb["schema_version"], "embark_layers_keys": list(emb["stars"]["layers"].keys())[:10] if isinstance(emb["stars"]["layers"], dict) else str(type(emb["stars"]["layers"]))}

# (4) BL HIP(HGCA)→ GCNS 内在率
hip = json.load(open(os.path.join(P0, "bl_hip_to_dr3_hgca.json")))
hsid = np.array(list(hip["map"].values()), dtype=np.int64)
in_g2 = np.fromiter((x in gset for x in hsid.tolist()), dtype=bool, count=len(hsid))
stats["bl_hip_in_gcns"] = {"n_hip_matched_dr3": int(len(hsid)), "in_gcns_100pc": int(in_g2.sum())}

print(json.dumps(stats, indent=1, ensure_ascii=False))
json.dump(stats, open(os.path.join(P0, "gcns_stats.json"), "w"), indent=1, ensure_ascii=False)
