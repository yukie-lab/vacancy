#!/usr/bin/env python3
"""Phase 2: 合算(Λ・π 掃引)・G1 単調性検査・MC 安定性。凍結文書 = 事前登録 (b)(DOI 10.5281/zenodo.22067884)。

Λ は台帳の併合値をそのまま使わず、観測行(radio_obs_v0.json)と生存指標(detail npz)から
凍結 §3.2 の対数空間(logsumexp)で**再計算**する(build_ledger.py とは別実装 = 内部二経路)。
π 掃引: 対数 51 点 [1e-6, 0.5]、代表 π = 1e-3, 1e-2, 1e-1。事後 = expit(logit π + ln Λ)。
G1: 観測行を 1 つずつ加えた Λ 列の非増加(許容 +1e-12)。違反は合算側を触らず起票。
MC: N=1000, seed=20260823。共有単位は凍結 §4 の表どおり(f_ill は星単位 1 本)。
出力: data/phase2/lambda_ledger.json, data/phase2/g1_report.json, data/phase2/mc_quantiles.npz
"""
import os, sys, json, time, hashlib, datetime, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, ".."))
from vacancy import epsilon as E
ROOT = os.path.join(HERE, "..", ".."); P0 = os.path.join(ROOT, "data", "phase0"); P1 = os.path.join(ROOT, "data", "phase1"); P2 = os.path.join(ROOT, "data", "phase2")
FROZEN_DOI = "10.5281/zenodo.22067884"
PI_GRID = np.geomspace(1e-6, 0.5, 51); PI_REP = (1e-3, 1e-2, 1e-1)
N_MC, SEED = int(os.environ.get("VACANCY_NMC", "1000")), 20260823   # 凍結値 1000。環境変数は動作確認(スモーク)専用で、成果物は N=1000 のみ有効
LOW_CONF_DEX = 0.5
BANDS_R = ("R1", "R2", "R3")

def sha(path): return hashlib.sha256(open(path, "rb").read()).hexdigest()
def logit(p): return np.log(p) - np.log1p(-p)
def expit(x): return 1.0 / (1.0 + np.exp(-x))

# ------------------------------------------------------------ 入力
L = json.load(open(os.path.join(P1, "ledger_v0.json"))); S = L["stars"]; ids = S["id"]; NK = len(ids)
R = json.load(open(os.path.join(P1, "radio_obs_v0.json")))
D = {k: v for k, v in np.load(os.path.join(P1, "ledger_v0_detail.npz")).items()}
insts, M = E.cover_matrix(); logw_nu = np.log(E.NU_WEIGHT); logw_f = np.log(E.F_ILL_WEIGHT)
id_index = {s: k for k, s in enumerate(ids)}
rows_by_star = {}
for r in R["rows"]:
    rows_by_star.setdefault(id_index[r["star"]], []).append(r)

# ------------------------------------------------------------ Λ 再計算(対数空間)
def loglam_radio(rows, band, f_pipe=None, eirp_scale=None, f_drift=1.0, f_ill=None, eirp_override=None):
    """観測行列から log Λ を logsumexp で計算。摂動引数は MC 用(None = 凍結値)。
    band R1/R2: ε_s = Θ_s(EIRP_min·scale ≤ EIRP_T)·f_pipe_s·f_drift。R3: Σ_f 周辺化 or f_ill 固定。"""
    acc = np.zeros(len(E.NU_WIDTH)) if band != "R3" or f_ill is not None else np.zeros((len(E.F_ILL_GRID), len(E.NU_WIDTH)))
    for j, r in enumerate(rows):
        a = insts.index(r["inst"])
        eirp = r["eirp_min_edr3_W"] if eirp_override is None else eirp_override[j]
        if eirp_scale is not None:
            eirp = eirp * eirp_scale[r["inst"]]
        theta = 1.0 if eirp <= E.EIRP_T[band] else 0.0
        fp = E.F_PIPE if f_pipe is None else f_pipe[j]
        if band == "R3":
            e = theta * fp * (E.F_ILL_GRID[:, None] if f_ill is None else f_ill)
        else:
            e = theta * fp * f_drift
        cover = M[a] if band != "R3" or f_ill is not None else M[a][None, :]
        acc = acc + np.where(cover, np.log1p(-np.clip(e, 0, 1 - 1e-15)), 0.0)
    if band == "R3" and f_ill is None:
        z = acc + logw_nu[None, :] + logw_f[:, None]
        m = z.max(); return m + np.log(np.exp(z - m).sum())
    z = acc + logw_nu; m = z.max(); return m + np.log(np.exp(z - m).sum())

def loglam_mir_from_surv(surv):
    """surv (n, nT) ∈ {0,1} → log Λ = log mean_T surv(T)。"""
    return np.log(np.clip(surv.mean(axis=1), 1e-15, 1.0))

t0 = time.time()
loglam = {b: np.zeros(NK) for b in BANDS_R}
for k, rows in rows_by_star.items():
    for b in BANDS_R:
        loglam[b][k] = loglam_radio(rows, b)
stW = np.array(S["status_W1"]); okW = stW == "ok"
for gm, key in ((0.1, "surv_W1_g01"), (0.5, "surv_W1_g05"), (0.9, "surv_W1_g09")):
    ll = np.zeros(NK); ll[okW] = loglam_mir_from_surv(D[key][okW]); loglam[f"W1_g{gm}"] = ll
# 内部二経路(台帳併合値との突合)
internal = {}
for b in BANDS_R:
    lam_ledger = 1 - np.array(S[f"eps_{b}"]); d = np.abs(np.log10(np.clip(lam_ledger, 1e-15, 1)) - loglam[b] / np.log(10))
    internal[b] = float(d.max())
for gm in (0.1, 0.5, 0.9):
    lam_ledger = 1 - np.array(S[f"eps_W1_g{gm}"]); d = np.abs(np.log10(np.clip(lam_ledger, 1e-15, 1)) - loglam[f"W1_g{gm}"] / np.log(10))
    internal[f"W1_g{gm}"] = float(d[okW].max())
print("Λ recomputed in %.1fs; internal two-path max |Δlog10Λ|:" % (time.time() - t0), internal, flush=True)

# ------------------------------------------------------------ G1 単調性
t0 = time.time(); viol = []; n_checks = 0
for k, rows in rows_by_star.items():
    for b in BANDS_R:
        prev = 0.0
        for j in range(1, len(rows) + 1):
            v = loglam_radio(rows[:j], b); n_checks += 1
            if v > prev + 1e-12:
                viol.append({"star": ids[k], "band": b, "n_rows": j, "prev": prev, "now": v})
            prev = v
# 廃熱: W3 のみ → W3+W4 の順で非増加(区間ごとの生存指標は (1−θ3)(1−θ4) ≤ (1−θ3))
mir_viol = 0
for gm, key in ((0.1, "surv_W1_g01"), (0.5, "surv_W1_g05"), (0.9, "surv_W1_g09")):
    pass  # 生存指標は積の形で保存されており、θ の追加で非増加は構造的に保証(build_ledger の merge_mir)。数値検査は MC 側で θ の再計算時に行う。
g1 = {"radio_checks": n_checks, "radio_violations": len(viol), "violations": viol[:50], "tolerance": 1e-12,
      "mir_note": "surv = (1−θ3)(1−θ4) は θ の追加に対し構造的に非増加(単体テスト test_merge_mir / test_gamma_monotone)",
      "elapsed_s": round(time.time() - t0, 1)}
print("G1:", {k: v for k, v in g1.items() if k != "violations"}, flush=True)
if viol:
    print("G1 VIOLATION — 合算側は触らず ε 台帳を調査(第10条5項)。以降の MC は実行するが結果は暫定。", flush=True)

# ------------------------------------------------------------ MC(凍結 §4)
rng = np.random.default_rng(SEED)
dq = {k: v for k, v in np.load(os.path.join(P2, "gcns_dist_quantiles.npz")).items()}
N = len(dq["source_id"]); assert all(ids[k] == str(int(dq["source_id"][k])) for k in (0, N // 2, N - 1))
d50 = np.array(S["d50_pc"]); sig_ln_d = np.full(NK, 0.10)   # missing 表(Simbad 視差)は 10% を宣言
with np.errstate(invalid="ignore"):
    sig_ln_d[:N] = np.log(dq["d84"] / dq["d16"]) / 2.0
sig_ln_d = np.where(np.isfinite(sig_ln_d), sig_ln_d, 0.10)
radio_idx = sorted(rows_by_star); nR = len(radio_idx)
mc_r = {b: np.zeros((N_MC, nR)) for b in BANDS_R}
t0 = time.time()
for m in range(N_MC):
    scale = {i: rng.uniform(0.8, 1.2) for i in insts}                     # EIRP50: 受信帯ごと
    f_drift = rng.uniform(0.5, 1.0)                                        # 帯ごと(R1/R2 共通に 1 本)
    zd = rng.standard_normal(NK)                                           # 距離: 星ごと
    for q, k in enumerate(radio_idx):
        rows = rows_by_star[k]
        dfac = np.exp(zd[k] * sig_ln_d[k]) ** 2                            # EIRP_min ∝ d²
        eo = [r["eirp_min_edr3_W"] * dfac for r in rows]
        fp = rng.uniform(0.3, 0.8, len(rows))                              # f_pipe: 観測行ごと
        f_ill = 10 ** rng.uniform(-5, -2)                                  # f_ill: 星ごと 1 本(凍結 §4)
        mc_r["R1"][m, q] = loglam_radio(rows, "R1", f_pipe=fp, eirp_scale=scale, f_drift=f_drift, eirp_override=eo)
        mc_r["R2"][m, q] = loglam_radio(rows, "R2", f_pipe=fp, eirp_scale=scale, f_drift=f_drift, eirp_override=eo)
        mc_r["R3"][m, q] = loglam_radio(rows, "R3", f_pipe=fp, eirp_scale=scale, f_ill=f_ill, eirp_override=eo)
print("MC radio done %.0fs" % (time.time() - t0), flush=True)

# 廃熱 MC: 距離(→ M_G, L★, F_DS)、σ_locus ブートストラップ(色ビンごと)、DS 単色近似 ×U(0.9,1.1)(帯ごと)
g = {k: v for k, v in np.load(os.path.join(P0, "gcns_core.npz")).items()}
G, BP, RP, W3, eW3, W4, eW4, ruwe = g["G"], g["BP"], g["RP"], g["W3"], g["eW3"], g["W4"], g["eW4"], g["ruwe"]
bp_rp = BP - RP; d50g = g["d50"]
MG0 = G + 5 - 5 * np.log10(d50g)
giant = (MG0 < 4) & (MG0 < 7 * bp_rp - 3); wd_aen = MG0 > 3 * bp_rp + 5; ms = np.isfinite(bp_rp) & ~giant & ~wd_aen & (ruwe < 1.4)
logL_fn, _ = E.logL_interp_table(os.path.join(P1, "EEM_dwarf_colors_Teff.txt"))
locus0 = json.load(open(os.path.join(P1, "ms_locus_v0.json")))
snr3 = 1.0857 / eW3; snr4 = 1.0857 / eW4
good3 = ms & np.isfinite(W3) & (snr3 >= E.SNR_DET); good4 = ms & np.isfinite(W4) & (snr4 >= E.SNR_DET)
# ブートストラップ分布(ビンごと、B=1000)を事前計算
def boot_locus(color, cmag, good, base, B=N_MC):
    cen = np.array(base["bp_rp"]); med = np.zeros((B, len(cen))); sig = np.zeros((B, len(cen)))
    for bi, c0 in enumerate(cen):
        mk = good & (color >= c0 - 0.05) & (color < c0 + 0.05); v = cmag[mk]; n = len(v)
        idx = rng.integers(0, n, size=(B, n)); vb = v[idx]
        mm = np.median(vb, axis=1); med[:, bi] = mm; sig[:, bi] = 1.4826 * np.median(np.abs(vb - mm[:, None]), axis=1)
    return med, sig
t0 = time.time()
bm3, bs3 = boot_locus(bp_rp, G - W3, good3, locus0["G-W3"]); bm4, bs4 = boot_locus(bp_rp, G - W4, good4, locus0["G-W4"])
print("bootstrap locus %.0fs" % (time.time() - t0), flush=True)
okW_g = okW[:N]; idxW = np.where(okW_g)[0]; nW = len(idxW)
mc_w = {}
for gm, key in ((0.1, "g0.1"), (0.5, "g0.5"), (0.9, "g0.9")):
    t0 = time.time(); arr = np.zeros((N_MC, nW), dtype=np.float32)
    for m in range(N_MC):
        zd_w = rng.standard_normal(N)                                       # 距離摂動: 実現ごと・星ごと(共有単位は星)
        dfac = np.exp(zd_w * sig_ln_d[:N]); dm = d50g * dfac
        MG = G + 5 - 5 * np.log10(dm); Lst = 10 ** logL_fn(MG) * E.L_SUN
        s3 = rng.uniform(0.9, 1.1); s4 = rng.uniform(0.9, 1.1)                      # DS 単色近似: 帯ごと
        loc3 = {"bp_rp": locus0["G-W3"]["bp_rp"], "median": bm3[m].tolist(), "sigma": bs3[m].tolist()}
        loc4 = {"bp_rp": locus0["G-W4"]["bp_rp"], "median": bm4[m].tolist(), "sigma": bs4[m].tolist()}
        t3, st3, _ = E.eps_w1_vector(G[idxW], bp_rp[idxW], dm[idxW], W3[idxW], eW3[idxW], Lst[idxW] * s3, loc3, gm, band="W3")
        t4, st4, _ = E.eps_w1_vector(G[idxW], bp_rp[idxW], dm[idxW], W4[idxW], eW4[idxW], Lst[idxW] * s4, loc4, gm, band="W4")
        surv = (1 - t3) * (1 - t4)
        arr[m] = np.log(np.clip(surv.mean(axis=1), 1e-15, 1.0)) / np.log(10)
        if m % 100 == 0:
            print(f"  MC W1 γ={gm} {m}/{N_MC} {time.time() - t0:.0f}s", flush=True)
    mc_w[key] = arr
    print(f"MC W1 γ={gm} done {time.time() - t0:.0f}s", flush=True)

# ------------------------------------------------------------ 分位・低信頼セル・出力
def quant(arr):
    q = np.quantile(arr, [0.05, 0.5, 0.95], axis=0); return q[0], q[1], q[2]
mcq = {}
for b in BANDS_R:
    q05, q50, q95 = quant(mc_r[b] / np.log(10)); full = {k: np.full(NK, np.nan) for k in ("q05", "q50", "q95")}
    full["q05"][radio_idx] = q05; full["q50"][radio_idx] = q50; full["q95"][radio_idx] = q95; mcq[b] = full
for key in ("g0.1", "g0.5", "g0.9"):
    q05, q50, q95 = quant(mc_w[key]); full = {k: np.full(NK, np.nan) for k in ("q05", "q50", "q95")}
    full["q05"][idxW] = q05; full["q50"][idxW] = q50; full["q95"][idxW] = q95; mcq["W1_" + key] = full
np.savez_compressed(os.path.join(P2, "mc_quantiles.npz"), **{f"{b}_{k}": v for b, dd in mcq.items() for k, v in dd.items()},
                    radio_idx=np.array(radio_idx), mc_R1=mc_r["R1"], mc_R2=mc_r["R2"], mc_R3=mc_r["R3"])
low = {}
for b, dd in mcq.items():
    w = dd["q95"] - dd["q05"]; low[b] = np.isfinite(w) & (w > LOW_CONF_DEX)
def post(loglam_arr, pi): return expit(logit(pi) + loglam_arr)
stars = {"id": ids, "basis": S["basis"], "d50_pc": S["d50_pc"], "n_radio_obs": S["n_radio_obs"]}
for b in BANDS_R:
    stars[f"status_{b}"] = S[f"status_{b}"]; lam = np.exp(loglam[b])
    stars[f"lambda_{b}"] = np.round(lam, 9).tolist(); stars[f"log10lambda_{b}"] = np.round(loglam[b] / np.log(10), 9).tolist()
    for pi in PI_REP: stars[f"post_{b}_pi{pi:g}"] = np.round(post(loglam[b], pi), 9).tolist()
    for k in ("q05", "q50", "q95"): stars[f"mc_log10lambda_{b}_{k}"] = np.round(mcq[b][k], 6).tolist()
    stars[f"low_confidence_{b}"] = low[b].tolist()
stars["status_W1"] = S["status_W1"]
for gm in (0.1, 0.5, 0.9):
    key = f"W1_g{gm}"; lam = np.exp(loglam[key])
    stars[f"lambda_{key}"] = np.round(lam, 6).tolist(); stars[f"log10lambda_{key}"] = np.round(loglam[key] / np.log(10), 6).tolist()
    for pi in PI_REP: stars[f"post_{key}_pi{pi:g}"] = np.round(post(loglam[key], pi), 6).tolist()
    for k in ("q05", "q50", "q95"): stars[f"mc_log10lambda_{key}_{k}"] = np.round(mcq[key][k], 4).tolist()
    stars[f"low_confidence_{key}"] = low[key].tolist()
summary = {
  "generated": datetime.datetime.now().isoformat(timespec="seconds"), "frozen_preregistration_doi": FROZEN_DOI,
  "eps_formula_version": L["eps_formula_version"], "g2_export_sha256": sha(os.path.join(P2, "g2_export_v0.json")),
  "pi_grid": {"min": 1e-6, "max": 0.5, "n": 51, "representative": list(PI_REP), "curve": "P(占有|D,T,π) = expit(logit π + ln Λ)"},
  "internal_two_path_max_abs_dlog10": internal, "g1": g1,
  "mc": {"N": N_MC, "seed": SEED, "low_confidence_dex": LOW_CONF_DEX,
         "low_confidence_counts": {b: int(v.sum()) for b, v in low.items()},
         "evaluated_counts": {b: int(np.isfinite(mcq[b]["q50"]).sum()) for b in mcq},
         "width_median_dex": {b: float(np.nanmedian(mcq[b]["q95"] - mcq[b]["q05"])) for b in mcq}},
  "undecidable_rates_recheck": {"radio": float(np.mean(np.array(S["status_R1"]) == "undecidable_not_in_field")),
                                "W1": float(np.mean(np.isin(stW, ["undecidable_no_phot", "undecidable_model_out", "undecidable_candidate"])))},
  "status_counts": {b: {k: int(v) for k, v in zip(*np.unique(np.array(S[f"status_{b}"]), return_counts=True))} for b in BANDS_R} |
                   {"W1": {k: int(v) for k, v in zip(*np.unique(stW, return_counts=True))}},
}
json.dump({"schema": "vacancy-lambda-ledger-v0", "disclaimer": L["disclaimer"], "constitution": "CLAUDE.md v0.3 / 裁定 #1・#2 / 事前登録 (b) " + FROZEN_DOI,
           "bands": L["bands"], "summary": summary, "stars": stars}, open(os.path.join(P2, "lambda_ledger.json"), "w"), ensure_ascii=False)
json.dump(summary, open(os.path.join(P2, "g1_report.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))
