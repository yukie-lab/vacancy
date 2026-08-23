#!/usr/bin/env python3
"""G3(ii) — Hephaistos I Table 1(100 pc)の計数再現(凍結文書 §5、Phase 3 実行指示 3.2)。

Hephaistos I(Suazo+22)Table 1、100 pc: N = 265,724 星、T_DS = 300 K で「DS と適合する(排除できない)星の割合」
  f(γ=0.1) = 6.6e-3、f(γ=0.5) = 1.9e-4、f(γ=0.9) = 1.8e-5。
本作の定義(凍結 §2、eps-v0.2)で同じ量を計数する:
  母集団 = GCNS(EDR3, ≤100 pc)のうち Hephaistos 主系列選択(式 8–9 + RUWE<1.4)を通り、WISE 測光(W3 または W4)を持つ星
         (= 台帳 status_W1 ∈ {ok, observed_insensitive, undecidable_candidate})。
  「適合(排除できない)」= T_DS = 300 K を含む区間で θ₃ = θ₄ = 0(DS があっても検出されなかったはず)、
                         または 既超過の検出候補(undecidable_candidate: 観測が DS 込みモデルと矛盾しない)。
  「排除」= 同区間で θ₃ または θ₄ = 1(DS があれば検出されたはずなのに不検出)。
合格 = 各 γ で 比(本作 f / 公刊 f)∈ [0.3, 3]。比が合格域でも要因分解(基盤差・選択差・検出定義差)を省略しない。
数字合わせ禁止: 閾値・選択・T 格子は凍結値のまま。
出力: data/phase3/g3_ii.json。再現: python3 scripts/g3_ii_hephaistos.py
"""
import os, sys, json, hashlib, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from vacancy import epsilon as E
P0 = os.path.join(ROOT, "data", "phase0"); P1 = os.path.join(ROOT, "data", "phase1"); P3 = os.path.join(ROOT, "data", "phase3"); os.makedirs(P3, exist_ok=True)

L = json.load(open(os.path.join(P1, "ledger_v0.json"))); S = L["stars"]
D = {k: v for k, v in np.load(os.path.join(P1, "ledger_v0_detail.npz")).items()}
g = {k: v for k, v in np.load(os.path.join(P0, "gcns_core.npz")).items()}
N = len(g["source_id"])
st = np.array(S["status_W1"][:N]); d50 = g["d50"]
# 300 K を含む T_DS 区間
jT = int(np.searchsorted(E.T_EDGES, 300.0) - 1); T_lo, T_hi = float(E.T_EDGES[jT]), float(E.T_EDGES[jT + 1])
# 母集団(本作): 主系列選択を通り WISE 測光を持つ星 = status が ok / observed_insensitive / undecidable_candidate。距離 ≤ 100 pc(dist_50)
in100 = d50 <= 100.0
sample = np.isin(st, ["ok", "observed_insensitive", "undecidable_candidate"]) & in100
published = {"N": 265724, "f": {"0.1": 6.6e-3, "0.5": 1.9e-4, "0.9": 1.8e-5}, "T_DS_K": 300, "basis": "Gaia DR2 + AllWISE(Suazo+22 Table 1, 100 pc)"}
rows = []; all_pass = True
for gm, key in ((0.1, "surv_W1_g01"), (0.5, "surv_W1_g05"), (0.9, "surv_W1_g09")):
    surv300 = D[key][:N, jT] >= 0.5                      # 1 = 不検出(排除できない)
    cand = st == "undecidable_candidate"
    compat = sample & (surv300 | cand)
    excluded = sample & ~compat
    n_s = int(sample.sum()); n_c = int(compat.sum()); f = n_c / n_s
    ratio = f / published["f"][str(gm)]
    ok = 0.3 <= ratio <= 3.0; all_pass &= ok
    # 内訳
    rows.append({"gamma": gm, "N_sample": n_s, "N_compatible": n_c, "N_compatible_candidates": int((sample & cand).sum()),
                 "N_compatible_undetected_ok": int((sample & surv300 & ~cand & (st == "ok")).sum()),
                 "N_compatible_insensitive": int((sample & (st == "observed_insensitive")).sum()),
                 "N_excluded": int(excluded.sum()), "f_ours": f, "f_published": published["f"][str(gm)], "ratio": ratio, "pass": bool(ok)})
# 要因分解の材料
ms_all = int(np.isin(st, ["ok", "observed_insensitive", "undecidable_candidate", "undecidable_no_phot"]).sum())
factors = {
  "population_basis": {"ours": "GCNS EDR3 ≤100 pc(dist_50)、主系列選択 式8–9 + RUWE<1.4、WISE 測光あり", "published": "Gaia DR2 ≤100 pc、主系列選択 式8–9 + 高 AEN 除外、Gaia–AllWISE best neighbour"},
  "counts": {"gcns_total": int(N), "gcns_le100pc": int(in100.sum()), "ms_selected_with_wise_le100": int(sample.sum()),
             "ms_selected_all_incl_no_wise": ms_all, "published_N": published["N"],
             "status_in_sample": {k: int(v) for k, v in zip(*np.unique(st[sample], return_counts=True))}},
  "detection_definition": {"ours": "G−W3 / G−W4 の主系列軌跡からの残差 ≥ k σ_tot(k=3、σ_tot² = σ_phot² + σ_locus²)、上限星は F_DS ≥ 3.5σ かつ色条件。W3 または W4 で検出 → 排除",
                           "published": "G−W1..W4 vs M_G の CMD で DS モデル(T, γ)の占める領域に観測点が入るか(4 図全てで)。非検出は S/N<2 上限で判定。RMSE 適合は Hephaistos II"},
  "T_DS_cell_used_K": [T_lo, T_hi], "note_T": "本作は対数格子 20 区間。300 K を含む区間の生存指標を用いる(凍結格子を変えない)",
  "candidate_definition": "本作の『検出候補』(既超過 ≥3σ)は Hephaistos の『DS 領域内の星』に対応するが、領域定義(kσ 残差 vs CMD 境界)が異なる",
}
out = {"item": "G3(ii)", "frozen_doi": "10.5281/zenodo.22067884", "published": published, "rows": rows, "all_pass": bool(all_pass), "factors": factors,
       "script_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest()}
json.dump(out, open(os.path.join(P3, "g3_ii.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
