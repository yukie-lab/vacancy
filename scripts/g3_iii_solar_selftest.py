#!/usr/bin/env python3
"""G3(iii) — 太陽系自己検定(T-R3、凍結文書 §5、Phase 3 実行指示 3.3)。

仮想行: 太陽系を d = 1.3〜10.8 pc の格子(1.3 / 2 / 4 / 6 / 8 / 10.8 pc を含む)に置き、GBT L + GBT S + Parkes 10-cm の
3 受信帯・軸上(応答 1)・各 1 観測行として T-R3 に通す。ε は凍結式(eps-v0.2)をそのまま使用(閾値・格子不変)。
判定(凍結 §5): f_ill 区間上端 10⁻² で Λ ≥ 0.99、周辺化値で Λ ≥ 0.999(全 d で)。
赤信号動作確認(合格条件ではない): f_ill = f_pipe = 1 の極で Λ = 1 − 2.15/2.35 ≈ 0.085 < 0.5 → 「検出される」。
出力: data/phase3/g3_iii.json。再現: python3 scripts/g3_iii_solar_selftest.py
"""
import os, sys, json, hashlib, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from vacancy import epsilon as E
P3 = os.path.join(ROOT, "data", "phase3"); os.makedirs(P3, exist_ok=True)
insts, M = E.cover_matrix()
D_GRID = sorted(set([1.3, 2.0, 4.0, 6.0, 8.0, 10.8] + list(np.round(np.linspace(1.3, 10.8, 20), 3))))
rows = []; all_pass = True
for d in D_GRID:
    eirp = {i: float(E.eirp_min(i, d, 1.0)) for i in insts}                  # 軸上
    theta = {i: float(eirp[i] <= E.EIRP_T["R3"]) for i in insts}             # EIRP_peak = 1e11 W(クラス上端)
    # 周辺化値(台帳と同じ式)
    surv, eps_marg = E.merge_radio_r3(insts, [theta[i] for i in insts], insts, M)
    # f_ill 上端 1e-2 固定
    surv_u, eps_upper = E.merge_radio(insts, [theta[i] * E.F_PIPE * E.F_ILL_R3_RANGE[1] for i in insts], insts, M)
    # 赤信号の極: f_ill = f_pipe = 1
    surv_x, eps_extreme = E.merge_radio(insts, [theta[i] * 1.0 * 1.0 for i in insts], insts, M)
    lam_marg, lam_upper, lam_extreme = 1 - eps_marg, 1 - eps_upper, 1 - eps_extreme
    ok = (lam_upper >= 0.99) and (lam_marg >= 0.999)
    all_pass &= ok
    rows.append({"d_pc": d, "eirp_min_W": eirp, "theta_sens": theta, "lambda_marginalized": lam_marg, "lambda_f_ill_1e-2": lam_upper,
                 "lambda_extreme_fill1_fpipe1": lam_extreme, "posterior_pi0.01_marg": 0.01 * lam_marg / (0.01 * lam_marg + 0.99), "pass": bool(ok)})
# 代表 d での赤信号確認(全 3 帯で Θ=1 の最近傍)
extreme_expected = 1 - 2.15 / 2.35
red = [r for r in rows if all(v == 1.0 for v in r["theta_sens"].values())]
out = {"item": "G3(iii)", "frozen_doi": "10.5281/zenodo.22067884", "band": "T-R3", "virtual_row": "太陽系、3 受信帯(GBT L, GBT S, Parkes 10-cm)、軸上、各 1 観測行、EIRP_peak = 1e11 W",
       "criteria": {"lambda_f_ill_upper_1e-2": ">= 0.99", "lambda_marginalized": ">= 0.999"}, "rows": rows, "all_pass": bool(all_pass),
       "red_flag_check": {"expected_lambda_extreme": extreme_expected, "observed_at_d_with_all_theta_1": [(r["d_pc"], r["lambda_extreme_fill1_fpipe1"]) for r in red][:3],
                          "interpretation": "f_ill = f_pipe = 1 の極では Λ ≈ 0.085 < 0.5 → 地球は「検出される」。検出器(ε)が生きていることの動作確認であり合格条件ではない"},
       "d_range_all_theta_1_pc": [min(r["d_pc"] for r in red), max(r["d_pc"] for r in red)] if red else None,
       "interpretation_seed": "地球級帯 T-R3 では事後 ≈ 事前 — 本アトラスが空き度を語れる技術帯の下限は地球自身で校正される。",
       "script_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest()}
json.dump(out, open(os.path.join(P3, "g3_iii.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, ensure_ascii=False, indent=1))
for r in rows:
    print(f'd={r["d_pc"]:6.3f} pc  Θ={tuple(int(v) for v in r["theta_sens"].values())}  Λ_marg={r["lambda_marginalized"]:.6f}  Λ(f=1e-2)={r["lambda_f_ill_1e-2"]:.5f}  Λ_extreme={r["lambda_extreme_fill1_fpipe1"]:.4f}  pass={r["pass"]}')
