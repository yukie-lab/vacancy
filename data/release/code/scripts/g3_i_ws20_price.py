#!/usr/bin/env python3
"""G3(i) — WS20 / Price+20 系アンカー(凍結文書 §5、Phase 3 実行指示 3.1)。

(a) 報告義務(合否なし): Price+20 §5.3 公刊値 0.45% / 0.37% / 2.0%(GBT L / GBT S / Parkes、N = 882 / 1005 / 189)と
    当方算式 f = [1 − 0.05^(1/N)] / P(二項厳密 95% 上限、P = f_pipe = 0.5)の比較表。
(b) ハードゲート: WS20 表(VizieR J/MNRAS/498/5720)の `rest` 距離(DR2 基盤、Bailer-Jones+18)**のみ**で再計数。
    ≤50 pc: N = 1513(完全一致要件)。≤100 pc / ≤200 pc: 1/N が公刊 0.061% / 0.039% の ±1% 以内。
    EDR3/GCNS 距離は使用しない(実装上も GCNS ファイルを一切読まない)。
(c) 本作のベイズ周辺化(同じ殻での mean Λ_i、Σ_i P(占有|D,π)/N)を併記(一致は強要しない)。

=== EIRP 条件の適用方法(逐語コメント、実行指示 3.1(b)) ===
WS20 §3.1 の「≤100 pc(EIRP ≳ 6.5×10¹³ W)」「≤200 pc(≳ 2.5×10¹⁴ W)」の EIRP 値は、距離殻 rest ≤ 100 / 200 pc に
含まれる星の EIRP_min の**最大値**(本再計数で 6.49×10¹³ / 2.49×10¹⁴ W と 3 桁一致)であり、殻の**感度限界の記述**である。
よって殻の計数は「rest ≤ 距離上限」のみで行い、EIRP による追加の絞り込みは行わない。
検算として「rest ≤ 上限 かつ EIRP_min ≤ 当該 EIRP」でも計数し、同数であること(絞り込みが計数に影響しないこと)を出力する。
星の計数単位は Gaia DR2 source_id の distinct(同一星の複数ポインティング行は 1 星)。
===============================================================
出力: data/phase3/g3_i.json。再現: python3 scripts/g3_i_ws20_price.py
"""
import os, sys, json, hashlib, collections, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
P0 = os.path.join(ROOT, "data", "phase0"); P2 = os.path.join(ROOT, "data", "phase2"); P3 = os.path.join(ROOT, "data", "phase3"); os.makedirs(P3, exist_ok=True)
out = {"item": "G3(i)", "frozen_doi": "10.5281/zenodo.22067884"}

# ---------------------------------------------------------------- (a) 報告義務
P = 0.5
pub = {"GBT L-band": (882, 0.45), "GBT S-band": (1005, 0.37), "Parkes 10-cm": (189, 2.0)}
rows_a = []
for k, (N, fpub) in pub.items():
    f_binom = (1 - 0.05 ** (1.0 / N)) / P * 100
    f_4N = 4.0 / N * 100; f_pois = 2.9957 / (P * N) * 100
    rows_a.append({"band": k, "N": N, "published_pct": fpub, "ours_binomial95_pct": round(f_binom, 4),
                   "ratio_ours_over_pub": round(f_binom / fpub, 3), "ref_4_over_N_pct": round(f_4N, 4), "ref_poisson95_pct": round(f_pois, 4),
                   "implied_fN_from_pub": round(fpub / 100 * N, 2)})
out["a_price_report"] = {"formula": "f = [1 − 0.05^(1/N)] / P, P = f_pipe = 0.5(二項厳密 95% 上限)", "rows": rows_a, "verdict": "報告義務(合否判定なし)",
    "footnote": "原典 Price+20 §5.3 の算式は本文に明記されていない(P = 0.5、各星を試行、95% 信頼のみ)。公刊三値から逆算した f·N = 3.97 / 3.74 / 3.78 はばらつき、単一の標準式(4/N、ポアソン 2.996/(0.5N)、二項厳密)では三値を同時に再現できない(参謀照合済み、裁定 #2)。"}

# ---------------------------------------------------------------- (b) ハードゲート(WS20 rest のみ)
w = {k: v for k, v in np.load(os.path.join(P0, "ws20_rows.npz"), allow_pickle=True).items()}
dr2 = w["dr2"]; rest = w["rest"]; eirp = w["eirp"]
def distinct(mask): return len(set(dr2[mask].tolist()))
shells = [(50, 1.0e13, 0.0660, "exact_N_1513"), (100, 6.5e13, 0.061, "pm1pct"), (200, 2.5e14, 0.039, "pm1pct")]
rows_b = []; all_pass = True
for lim, E, fpub, rule in shells:
    m = rest <= lim
    N = distinct(m); N_e = distinct(m & (eirp <= E)); emax = float(eirp[m].max())
    inv = 100.0 / N
    if rule == "exact_N_1513":
        ok = (N == 1513)
    else:
        ok = abs(inv - fpub) / fpub <= 0.01
    all_pass &= ok
    rows_b.append({"shell_pc": lim, "N_rest_only": N, "N_with_eirp_cut": N_e, "eirp_cut_changes_count": N != N_e,
                   "max_eirp_min_in_shell_W": emax, "quoted_eirp_W": E, "inv_N_pct": round(inv, 5), "published_pct": fpub,
                   "rel_diff_pct": round((inv - fpub) / fpub * 100, 2), "N_implied_by_published": round(100 / fpub, 1), "rule": rule, "pass": bool(ok)})
out["b_ws20_hardgate"] = {"distance_basis": "WS20 rest(DR2, Bailer-Jones+18)のみ。EDR3/GCNS 不使用", "rows": rows_b, "all_pass": bool(all_pass)}

# ---------------------------------------------------------------- (c) 本作のベイズ周辺化(参考、一致は強要しない)
L = json.load(open(os.path.join(P2, "lambda_ledger.json"))); S = L["stars"]
d2e = json.load(open(os.path.join(P0, "ws20_dr2_to_edr3.json")))
idx = {s: k for k, s in enumerate(S["id"])}
best_rest = collections.defaultdict(lambda: 1e99)
for s, r in zip(dr2.tolist(), rest.tolist()):
    best_rest[s] = min(best_rest[s], r)
rows_c = []
for lim, E, fpub, rule in shells:
    members = [s for s, r in best_rest.items() if r <= lim]
    ks = [idx[str(d2e[s])] for s in members if s in d2e and str(d2e[s]) in idx]
    for band in ("R1", "R2"):
        lam = np.array([S[f"lambda_{band}"][k] for k in ks]); st = np.array([S[f"status_{band}"][k] for k in ks])
        okm = st == "ok"
        rec = {"shell_pc": lim, "band": band, "N_shell_ws20": len(members), "N_joined_edr3_ledger": len(ks), "N_status_ok": int(okm.sum()),
               "mean_lambda_ok": float(lam[okm].mean()) if okm.any() else None}
        for pi in (1e-3, 1e-2, 1e-1):
            post = np.array([S[f"post_{band}_pi{pi:g}"][k] for k in ks])
            rec[f"mean_posterior_pi{pi:g}"] = float(post[okm].mean()) if okm.any() else None
        rec["published_1_over_N_pct"] = fpub
        rows_c.append(rec)
out["c_bayes_marginalization"] = {"note": "別量: 1/N(頻度論・不検出試行の計数)と、星単位の事後 P(占有|D,T,π) の殻平均。一致を強要しない(第7条 G3(i))。ok 以外(感度外)の星は除外して平均", "rows": rows_c}
out["script_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
json.dump(out, open(os.path.join(P3, "g3_i.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
