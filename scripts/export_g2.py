#!/usr/bin/env python3
"""G2(二経路合成)用エクスポート — 裁定 #2 第7項。
台帳から、参謀が対数和で Λ を独立再計算するのに必要な最小情報を 1 ファイル(JSON)に出す:
  - 共通 ν 区間(境界・重み)、受信帯 × 区間の被覆行列、f_ill 格子と重み、T_DS 区間境界と重み
  - 電波: 星ごとの観測行 [(受信帯, ε_R1, ε_R2, Θ_R3)]
  - 廃熱: 星ごとの θ₃(T), θ₄(T)(γ = 0.1/0.5/0.9)は detail npz からビット列で
  - 台帳側の併合値 Λ は**含めない**(参謀の再計算が Code の Λ を見てから始まる形を避ける — 実行指示 手順3-1)
Phase 2 冒頭で実行(python3 scripts/export_g2.py)。出力: data/phase2/g2_export_v0.json
"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from vacancy import epsilon as E
P1 = os.path.join(ROOT, "data", "phase1"); P2 = os.path.join(ROOT, "data", "phase2"); os.makedirs(P2, exist_ok=True)
L = json.load(open(os.path.join(P1, "ledger_v0.json"))); S = L["stars"]
R = json.load(open(os.path.join(P1, "radio_obs_v0.json")))
D = {k: v for k, v in np.load(os.path.join(P1, "ledger_v0_detail.npz")).items()}   # npz 遅延ロード回避(一括展開)
insts, M = E.cover_matrix()
rows_by_star = {}
for r in R["rows"]:
    rows_by_star.setdefault(r["star"], []).append([r["inst"], r["eps_in_band"]["R1"], r["eps_in_band"]["R2"], r["theta_R3"]])
ids = S["id"]
radio = {sid: {"rows": rows_by_star[sid]} for k, sid in enumerate(ids) if sid in rows_by_star}   # Λ(併合 ε)は含めない(実行指示 手順3-1)
# 廃熱: ok 星のみ、θ は生存確率 (1−θ3)(1−θ4) の区間列(0/1)をそのまま
okW = [k for k, st in enumerate(S["status_W1"]) if st == "ok"]
S01 = D["surv_W1_g01"].astype(int).astype(str); S05 = D["surv_W1_g05"].astype(int).astype(str); S09 = D["surv_W1_g09"].astype(int).astype(str)
mir = {"gamma_levels": list(E.GAMMA_LEVELS), "n_T": len(E.T_CENTERS),
       "encoding": "surv_* は T_DS 20 区間の生存指標 (1−θ3)(1−θ4) ∈ {0,1} を区間順に並べた 20 桁の文字列",
       "stars": {ids[k]: {"surv_g0.1": "".join(S01[k]), "surv_g0.5": "".join(S05[k]), "surv_g0.9": "".join(S09[k])} for k in okW}}
out = {"schema": "vacancy-g2-export-v0", "eps_formula_version": L["eps_formula_version"],
       "note": "Λ 列なし。参謀は本ファイルのみから Λ を再計算し、Code の lambda_ledger.json と突合する", "formula": {"radio_R1R2": "1-eps = sum_c w_c prod_s (1 - eps_s * cover[inst_s][c])",
                   "radio_R3": "1-eps = sum_f w_f sum_c w_c prod_s (1 - theta_s * 0.5 * f * cover[inst_s][c])",
                   "mir": "1-eps = (1/n_T) sum_T surv[T]", "tolerance": "|Δlog10 Λ| ≤ 1e-6"},
       "nu_edges_GHz": E.NU_EDGES.tolist(), "nu_weight": E.NU_WEIGHT.tolist(), "cover": {i: M[a].astype(int).tolist() for a, i in enumerate(insts)},
       "f_ill_grid": E.F_ILL_GRID.tolist(), "f_ill_weight": E.F_ILL_WEIGHT.tolist(), "f_pipe": E.F_PIPE,
       "T_edges_K": E.T_EDGES.tolist(), "T_weight": E.T_WEIGHT.tolist(),
       "radio": radio, "mir": mir}
json.dump(out, open(os.path.join(P2, "g2_export_v0.json"), "w"), ensure_ascii=False)
print("radio stars", len(radio), "mir ok stars", len(okW), "->", os.path.join(P2, "g2_export_v0.json"))
