#!/usr/bin/env python3
"""Phase 1.1: ε 台帳 v0 の構築(星 × モダリティ × 帯、来歴付き)。

入力: data/phase0/gcns_core.npz(GCNS 331,312 星)、data/raw/gcns_missing.tsv、data/phase0/ws20_rows.npz、
      data/phase0/ws20_dr2_to_edr3.json、data/raw/bl_opendata/*.json(観測日)、data/phase1/EEM_dwarf_colors_Teff.txt
出力: data/phase1/ledger_v0.json(星単位・列指向)、data/phase1/radio_obs_v0.json(電波観測行・来歴)、
      data/phase1/ledger_v0_detail.npz(ν 区間・T_DS 区間ごとの生存確率)、data/phase1/ledger_v0_summary.json(計数)
"""
import os, sys, json, glob, re, hashlib, datetime, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from vacancy import epsilon as E

ROOT = os.path.join(HERE, "..", "..")
P0 = os.path.join(ROOT, "data", "phase0"); P1 = os.path.join(ROOT, "data", "phase1"); RAW = os.path.join(ROOT, "data", "raw")
os.makedirs(P1, exist_ok=True)

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

# ------------------------------------------------------------ 恒星基盤
g = np.load(os.path.join(P0, "gcns_core.npz"))
sid = g["source_id"]; N = len(sid)
G, BP, RP, d50, ruwe = g["G"], g["BP"], g["RP"], g["d50"], g["ruwe"]
W3, eW3, W4, eW4 = g["W3"], g["eW3"], g["W4"], g["eW4"]
bp_rp = BP - RP
MG = G + 5 - 5 * np.log10(d50)
giant = (MG < 4) & (MG < 7 * bp_rp - 3)
wd_aen = MG > 3 * bp_rp + 5
ms = np.isfinite(bp_rp) & ~giant & ~wd_aen & (ruwe < 1.4)       # Hephaistos 主系列選択(式 8–9 + RUWE)

# missing 表(EDR3 欠落の明るい星)
mrows = [l.rstrip("\n").split("\t") for l in open(os.path.join(RAW, "gcns_missing.tsv")) if not l.startswith("#") and l.strip()]
mdata = [r for r in mrows[3:] if r[0].strip().isdigit()]
m_name = np.array([r[1].strip() for r in mdata]); m_ra = np.array([float(r[2]) for r in mdata]); m_de = np.array([float(r[3]) for r in mdata])
m_plx = np.array([float(r[4]) if r[4].strip() else np.nan for r in mdata])
NM = len(mdata)

# ------------------------------------------------------------ 電波観測行(WS20)
w = {k: v for k, v in np.load(os.path.join(P0, "ws20_rows.npz"), allow_pickle=True).items()}   # npz の遅延ロードを避けて一括展開
dr2map = json.load(open(os.path.join(P0, "ws20_dr2_to_edr3.json")))
sid_index = {int(s): k for k, s in enumerate(sid.tolist())}
insts, M = E.cover_matrix()

def unit(r, d):
    r = np.radians(r); d = np.radians(d)
    return np.stack([np.cos(d) * np.cos(r), np.cos(d) * np.sin(r), np.sin(d)], -1)
Um = unit(m_ra, m_de)

# BL アーカイブの観測日(目標名 × 名目帯)
def bl_dates(target):
    fn = os.path.join(RAW, "bl_opendata", target + ".json")
    if not os.path.exists(fn):
        return {}
    out = {}
    for x in json.load(open(fn))["data"]:
        if x["file_type"] not in ("HDF5", "filterbank"):
            continue
        f = x["center_freq"]; tel = x["telescope"]
        b = None
        if tel == "GBT" and 1100 <= f <= 1900: b = "GBT L-band"
        elif tel == "GBT" and 1900 < f <= 2800: b = "GBT S-band"
        elif tel == "Parkes" and 2600 <= f <= 3450: b = "Parkes 10-cm"
        if b:
            out.setdefault(b, []).append(x["mjd"])
    return {b: {"n_files": len(v), "mjd_min": min(v), "mjd_max": max(v)} for b, v in out.items()}

radio_rows = []           # 来歴付き観測行
star_rows = {}            # 星キー → 行 index 列
n_unmatched_rows = 0; n_missing_matched = 0
bl_cache = {}
for k in np.where(w["rest"] <= 120)[0]:
    dr2 = str(w["dr2"][k]); inst = str(w["inst"][k])
    key = None
    if dr2 in dr2map:
        key = ("gcns", sid_index[int(dr2map[dr2])])
    else:
        # missing 表との位置照合(30", |Δplx| < 3 mas)
        v = unit(w["ra"][k], w["de"][k]); dots = Um @ v; j = int(dots.argmax())
        sep = np.degrees(np.arccos(min(1.0, dots[j]))) * 3600
        if sep <= 30 and np.isfinite(m_plx[j]) and abs(w["plx"][k] - m_plx[j]) < 3:
            key = ("missing", j); n_missing_matched += 1
    if key is None:
        n_unmatched_rows += 1
        continue
    if key[0] == "gcns":
        d_edr3 = float(d50[key[1]]); sid_str = str(int(sid[key[1]]))
    else:
        d_edr3 = float(1000.0 / m_plx[key[1]]); sid_str = "MISSING:" + m_name[key[1]]
    eirp_edr3 = float(E.eirp_min(inst, d_edr3, w["resp"][k]))
    tgt = str(w["target"][k])
    if tgt not in bl_cache:
        bl_cache[tgt] = bl_dates(tgt)
    row = {"row_id": len(radio_rows), "star": sid_str, "basis": key[0], "inst": inst, "ws20_recno_index": int(k),
           "target_field": tgt, "offset_arcmin": float(w["off"][k]), "response": float(w["resp"][k]),
           "d_ws20_pc": float(w["rest"][k]), "d_edr3_pc": d_edr3,
           "eirp_min_ws20_W": float(w["eirp"][k]), "eirp_min_edr3_W": eirp_edr3,
           "price_target": str(w["price"][k]) == "true",
           "bl_archive_dates": bl_cache[tgt].get(inst),
           "eps_in_band": {b: float(E.eps_radio_row(b, eirp_edr3)) for b in ("R1", "R2")},
           "theta_R3": float(eirp_edr3 <= E.EIRP_T["R3"]),     # R3 は f_ill を星単位で周辺化するため Θ のみ保持(裁定 #2)
           "provenance": "WS20 J/MNRAS/498/5720/catalog; EIRP50 Price+20 §5.2; f_pipe Price+20 §5.3; " + E.EPS_FORMULA_VERSION}
    radio_rows.append(row); star_rows.setdefault(key, []).append(row["row_id"])

# ------------------------------------------------------------ 電波帯 ε(星単位、併合)
NK = N + NM
keys = [("gcns", i) for i in range(N)] + [("missing", j) for j in range(NM)]
eps_rad = {b: np.zeros(NK) for b in ("R1", "R2", "R3")}
surv_rad = {b: np.ones((NK, len(E.NU_WIDTH)), dtype=np.float32) for b in ("R1", "R2")}
surv_rad["R3"] = np.ones((NK, len(E.F_ILL_GRID), len(E.NU_WIDTH)), dtype=np.float32)
status_rad = np.full(NK, "undecidable_not_in_field", dtype=object)
n_obs = np.zeros(NK, dtype=np.int32)
for key, ids in star_rows.items():
    idx = key[1] if key[0] == "gcns" else N + key[1]
    n_obs[idx] = len(ids)
    rows = [radio_rows[r] for r in ids]
    for b in ("R1", "R2"):
        surv, em = E.merge_radio([r["inst"] for r in rows], [r["eps_in_band"][b] for r in rows], insts, M)
        surv_rad[b][idx] = surv; eps_rad[b][idx] = em
    surv3, em3 = E.merge_radio_r3([r["inst"] for r in rows], [r["theta_R3"] for r in rows], insts, M)
    surv_rad["R3"][idx] = surv3; eps_rad["R3"][idx] = em3
    status_rad[idx] = "ok" if any(r["eps_in_band"]["R2"] > 0 for r in rows) else "observed_insensitive"
# 帯ごとの細分: 観測あり・当該帯で感度ゼロ
status_band = {}
for b in ("R1", "R2", "R3"):
    eps_rad[b][eps_rad[b] < 1e-12] = 0.0          # 周辺化重みの丸め(Σw = 1 − 1e-16)による擬似正値を 0 に戻す
    s = status_rad.copy()
    s[(status_rad != "undecidable_not_in_field") & (eps_rad[b] == 0)] = "observed_insensitive"
    s[(status_rad != "undecidable_not_in_field") & (eps_rad[b] > 0)] = "ok"
    status_band[b] = s

# ------------------------------------------------------------ 廃熱帯 ε
logL_fn, logL_range = E.logL_interp_table(os.path.join(P1, "EEM_dwarf_colors_Teff.txt"))
L_star = 10 ** logL_fn(MG) * E.L_SUN
snr3 = 1.0857 / eW3; snr4 = 1.0857 / eW4
good3 = ms & np.isfinite(W3) & (snr3 >= E.SNR_DET); good4 = ms & np.isfinite(W4) & (snr4 >= E.SNR_DET)
locus3 = E.build_locus(bp_rp, G - W3, good3); locus4 = E.build_locus(bp_rp, G - W4, good4)
json.dump({"G-W3": locus3, "G-W4": locus4, "selection": "Hephaistos MS (eq.8-9, RUWE<1.4) & S/N>=3.5", "bin": 0.1, "sigma": "1.4826*MAD"},
          open(os.path.join(P1, "ms_locus_v0.json"), "w"), indent=1)

GAMMAS = tuple(E.GAMMA_LEVELS) + (E.GAMMA_INFO,)          # 末尾は情報列(帯定義外)
eps_mir = {gm: np.zeros(NK) for gm in GAMMAS}
surv_mir = {gm: np.ones((NK, len(E.T_CENTERS)), dtype=np.float32) for gm in GAMMAS}
status_mir = np.full(NK, "undecidable_no_phot", dtype=object)
r_obs3 = np.full(NK, np.nan); r_obs4 = np.full(NK, np.nan)
has_wise = np.isfinite(W3) | np.isfinite(W4)
for gm in GAMMAS:
    t3, s3, r3 = E.eps_w1_vector(G, bp_rp, d50, W3, eW3, L_star, locus3, gm, band="W3")
    t4, s4, r4 = E.eps_w1_vector(G, bp_rp, d50, W4, eW4, L_star, locus4, gm, band="W4")
    surv, em = E.merge_mir(t3, t4)
    surv_mir[gm][:N] = surv; eps_mir[gm][:N] = em
    if gm == E.GAMMA_LEVELS[0]:
        r_obs3[:N] = r3; r_obs4[:N] = r4
        st = np.full(N, "ok", dtype=object)
        cand = (s3 == "candidate") | (s4 == "candidate")
        both_np = np.isin(s3, ["no_phot", "model_out"]) & np.isin(s4, ["no_phot", "model_out"])
        st[both_np & ((s3 == "model_out") | (s4 == "model_out"))] = "undecidable_model_out"
        st[both_np & ~((s3 == "model_out") | (s4 == "model_out"))] = "undecidable_no_phot"
        st[cand] = "undecidable_candidate"
        st[~has_wise] = "undecidable_no_phot"
        st[has_wise & ~ms] = "undecidable_model_out"
        status_mir[:N] = st
ok_mask = status_mir == "ok"
for gm in GAMMAS:                  # 判定不能星の ε は定義しない(0 に固定、status で区別)
    eps_mir[gm][~ok_mask] = 0.0; surv_mir[gm][~ok_mask] = 1.0
insens = ok_mask & np.all([eps_mir[gm] == 0 for gm in E.GAMMA_LEVELS], axis=0)
status_mir[insens] = "observed_insensitive"
# missing 表の星は光度測定なし → no_phot のまま

# ------------------------------------------------------------ 出力
def cnt(arr):
    u, c = np.unique(arr.astype(str), return_counts=True); return {k: int(v) for k, v in zip(u, c)}
summary = {
  "generated": datetime.date.today().isoformat(), "eps_formula_version": E.EPS_FORMULA_VERSION,
  "population": {"gcns": int(N), "missing_table": int(NM), "total": int(NK)},
  "radio": {"n_rows_ws20_le120pc_used": len(radio_rows), "n_rows_unmatched_dropped": n_unmatched_rows, "n_rows_matched_missing_table": n_missing_matched,
            "stars_with_obs": int((n_obs > 0).sum()),
            "status_by_band": {b: cnt(status_band[b]) for b in ("R1", "R2", "R3")},
            "eirp_edr3_over_ws20_median": float(np.median([r["eirp_min_edr3_W"] / r["eirp_min_ws20_W"] for r in radio_rows])),
            "rows_with_bl_dates": int(sum(1 for r in radio_rows if r["bl_archive_dates"]))},
  "mir": {"status": cnt(status_mir), "locus_bins": {"G-W3": len(locus3["bp_rp"]), "G-W4": len(locus4["bp_rp"])},
          "eps_gt0_by_gamma": {str(gm): int((eps_mir[gm] > 0).sum()) for gm in GAMMAS},
          "eps_median_ok_by_gamma": {str(gm): float(np.median(eps_mir[gm][status_mir == "ok"])) if (status_mir == "ok").any() else None for gm in GAMMAS},
          "info_column_note": "gamma=0.01 は帯定義外の情報列(裁定 #2 修正 4)。空き度の主張には用いない"},
  "undecidable_rate": {b: float(np.mean(status_band[b] == "undecidable_not_in_field")) for b in ("R1", "R2", "R3")} |
                      {"W1": float(np.mean(np.isin(status_mir, ["undecidable_no_phot", "undecidable_model_out", "undecidable_candidate"])))},
  "inputs_sha256": {"gcns_core.npz": sha(os.path.join(P0, "gcns_core.npz")), "ws20_rows.npz": sha(os.path.join(P0, "ws20_rows.npz")),
                    "EEM_dwarf_colors_Teff.txt": sha(os.path.join(P1, "EEM_dwarf_colors_Teff.txt"))},
}
ledger = {
  "schema": "vacancy-ledger-v0", "generated": summary["generated"], "eps_formula_version": E.EPS_FORMULA_VERSION,
  "constitution": "CLAUDE.md v0.3 / 裁定 #1", "disclaimer": "空き度は測量であって証明ではない。不在の証拠は限定的であり、占有の不在を証明しない。",
  "bands": {"R1": {"EIRP_W": E.EIRP_T["R1"], "window_GHz": [1.10, 3.45]}, "R2": {"EIRP_W": E.EIRP_T["R2"], "window_GHz": [1.10, 3.45]},
            "R3": {"EIRP_W": E.EIRP_T["R3"], "f_ill_range": list(E.F_ILL_R3_RANGE), "f_ill_grid": E.F_ILL_GRID.tolist(), "f_ill_rule": "星単位の潜在変数として対数一様事前で周辺化(裁定 #2 修正 1)"},
            "W1": {"gamma_levels": list(E.GAMMA_LEVELS), "gamma_info_column": E.GAMMA_INFO, "T_DS_K": [100, 700], "k_sigma": E.K_SIGMA, "snr_det": E.SNR_DET}},
  "nu_grid_GHz": E.NU_EDGES.tolist(), "nu_weight": E.NU_WEIGHT.tolist(), "T_grid_K": E.T_EDGES.tolist(),
  "stars": {"id": [str(int(s)) for s in sid] + ["MISSING:" + n for n in m_name],
            "basis": ["gcns"] * N + ["missing"] * NM,
            "d50_pc": np.round(np.concatenate([d50, 1000.0 / m_plx]), 3).tolist(),
            "n_radio_obs": n_obs.tolist(),
            "status_R1": status_band["R1"].tolist(), "status_R2": status_band["R2"].tolist(), "status_R3": status_band["R3"].tolist(),
            "eps_R1": np.round(eps_rad["R1"], 6).tolist(), "eps_R2": np.round(eps_rad["R2"], 6).tolist(), "eps_R3": np.round(eps_rad["R3"], 9).tolist(),
            "status_W1": status_mir.tolist(),
            "eps_W1_g0.1": np.round(eps_mir[0.1], 6).tolist(), "eps_W1_g0.5": np.round(eps_mir[0.5], 6).tolist(), "eps_W1_g0.9": np.round(eps_mir[0.9], 6).tolist(),
            "info_eps_W1_g0.01": np.round(eps_mir[0.01], 6).tolist(),
            "r_obs_GW3": np.round(np.concatenate([r_obs3[:N], np.full(NM, np.nan)]), 4).tolist(), "r_obs_GW4": np.round(np.concatenate([r_obs4[:N], np.full(NM, np.nan)]), 4).tolist()},
  "summary": summary,
}
json.dump(ledger, open(os.path.join(P1, "ledger_v0.json"), "w"), ensure_ascii=False)
json.dump({"schema": "vacancy-radio-obs-v0", "rows": radio_rows, "nu_grid_GHz": E.NU_EDGES.tolist(), "cover": {i: M[a].tolist() for a, i in enumerate(insts)}},
          open(os.path.join(P1, "radio_obs_v0.json"), "w"), ensure_ascii=False, indent=None)
np.savez_compressed(os.path.join(P1, "ledger_v0_detail.npz"), surv_R1=surv_rad["R1"], surv_R2=surv_rad["R2"], surv_R3=surv_rad["R3"],
                    surv_W1_g01=surv_mir[0.1], surv_W1_g05=surv_mir[0.5], surv_W1_g09=surv_mir[0.9], info_surv_W1_g001=surv_mir[0.01])
json.dump(summary, open(os.path.join(P1, "ledger_v0_summary.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))
