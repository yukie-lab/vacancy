#!/usr/bin/env python3
"""VACANCY ε 導出式の実装(憲法 v0.3 第3条、02 設計書 §2–3)。

- 電波帯 T-R1/R2/R3: WS20 行(星 × ポインティング × 受信帯)ごとの ε_row(ν) と、
  共通 ν グリッド(モダリティ全体で 1 本)上での併合(裁定 #1 C)。
- 廃熱帯 T-W1: Hephaistos 式モデル(星 + 灰色吸収・黒体再放射の部分ダイソン球)で
  G−W3 / G−W4 の色超過を予測し、主系列軌跡からの k σ 超過で検出を判定。T_DS グリッド上で併合。

全因子は本モジュール内で閉じ、合算側(aggregate.py)は ε と潜在区間重みのみを受け取る。
EPS_FORMULA_VERSION を台帳の来歴に記録する。
"""
import numpy as np

EPS_FORMULA_VERSION = "eps-v0.2 (2026-08-23, 憲法 v0.3 / 裁定 #1・#2: f_ill を星単位潜在変数として周辺化、γ=0.01 情報列)"

# ---------------------------------------------------------------- 電波帯
# 共通 ν グリッド(GHz)。窓 [1.10, 3.45] を受信帯境界・ノッチ境界で分割した 9 区間(モダリティ全体で共通)。
NU_EDGES = np.array([1.10, 1.20, 1.34, 1.80, 1.90, 2.30, 2.36, 2.60, 2.80, 3.45])
NU_WIDTH = np.diff(NU_EDGES)
NU_WEIGHT = NU_WIDTH / NU_WIDTH.sum()          # ν は窓内一様(憲法第3条1項)
# 受信帯の被覆(ノッチ除外): Price+20 §2.3–2.4
BAND_COVER = {
    "GBT L-band": [(1.10, 1.20), (1.34, 1.90)],
    "GBT S-band": [(1.80, 2.30), (2.36, 2.80)],
    "Parkes 10-cm": [(2.60, 3.45)],
}
EIRP50 = {"GBT L-band": 2.1e12, "GBT S-band": 2.1e12, "Parkes 10-cm": 9.1e12}   # W @ 50 pc, 軸上(Price+20 §5.2)
F_PIPE = 0.5                                    # Price+20 §5.3(RFI 遮蔽込みの 1 観測あたり検出確率)
EIRP_T = {"R1": 1.0e13, "R2": 1.0e17, "R3": 1.0e11}   # クラス閾値(R3 は上端で評価 = 厳しい自己検定)
F_ILL_R3_RANGE = (1e-5, 1e-2)                   # 裁定 #1 F: 照射因子の宣言区間(対数一様で MC 掃引)
F_ILL_R3_CENTRAL = float(np.sqrt(F_ILL_R3_RANGE[0] * F_ILL_R3_RANGE[1]))   # 対数中点 10^-3.5(参考値。台帳は周辺化値を用いる)
# 裁定 #2 修正 1: f_ill は送信機側の幾何 → 星単位の潜在変数。対数一様事前を 13 点グリッドで周辺化(観測行ごとに独立に引かない)
F_ILL_GRID = np.geomspace(F_ILL_R3_RANGE[0], F_ILL_R3_RANGE[1], 13)
F_ILL_WEIGHT = np.full(len(F_ILL_GRID), 1.0 / len(F_ILL_GRID))


def cover_matrix():
    """受信帯 × ν 区間 の被覆行列(bool)。区間は被覆区間に完全に含まれる場合のみ True(区間境界は帯境界に一致)。"""
    insts = list(BAND_COVER)
    M = np.zeros((len(insts), len(NU_WIDTH)), dtype=bool)
    for a, inst in enumerate(insts):
        for c in range(len(NU_WIDTH)):
            lo, hi = NU_EDGES[c], NU_EDGES[c + 1]
            M[a, c] = any(l <= lo + 1e-12 and hi <= h + 1e-12 for l, h in BAND_COVER[inst])
    return insts, M


def eirp_min(inst, d_pc, resp):
    """EIRP_min = EIRP50 × (d/50)² / R(θ)。R はガウスビーム応答(WS20 §3)。"""
    return EIRP50[inst] * (np.asarray(d_pc) / 50.0) ** 2 / np.asarray(resp)


def eps_radio_row(band, eirp_min_w, f_pipe=F_PIPE, f_ill=None):
    """1 観測行の周波数内 ε(ν ∈ 受信帯のとき)。= Θ_sens · f_pipe · f_duty · f_drift · f_beam。
    R1/R2: f_duty = f_drift = f_beam = 1(クラス宣言)。R3: f_ill = f_duty·f_beam(裁定 #1 F)。"""
    theta = (np.asarray(eirp_min_w) <= EIRP_T[band]).astype(float)
    if band == "R3":
        fi = F_ILL_R3_CENTRAL if f_ill is None else f_ill
        return theta * f_pipe * fi
    return theta * f_pipe


def merge_radio_r3(rows_inst, rows_theta, insts, M, f_pipe=F_PIPE):
    """T-R3 の併合(裁定 #2 修正 1): 潜在変数 (ν 区間 c, 星単位 f_ill) で周辺化。
    rows_theta = 各観測行の Θ_sens(EIRP_min ≤ 1e11 W)。
    1 − ε = Σ_f w_f Σ_c w_c Π_s [1 − Θ_s f_pipe f · 1[c ⊂ B_s]]。
    返り値: (surv[n_f, 9], eps_merged)"""
    surv = np.ones((len(F_ILL_GRID), len(NU_WIDTH)))
    for inst, th in zip(rows_inst, rows_theta):
        a = insts.index(inst)
        e = th * f_pipe * F_ILL_GRID[:, None]                       # (n_f, 1)
        surv = surv * np.where(M[a][None, :], 1.0 - e, 1.0)
    return surv, 1.0 - float(F_ILL_WEIGHT @ surv @ NU_WEIGHT)


def merge_radio(rows_inst, rows_eps, insts, M):
    """星 1 つ分の観測行(受信帯名, ε_row)を共通 ν グリッド上で併合。
    返り値: (cell_surv[9] = Π_s(1−ε_s·1[ν∈B_s]) 各区間, eps_merged = 1 − Σ_c w_c cell_surv_c)"""
    surv = np.ones(len(NU_WIDTH))
    for inst, e in zip(rows_inst, rows_eps):
        a = insts.index(inst)
        surv = surv * np.where(M[a], 1.0 - e, 1.0)
    return surv, 1.0 - float(np.dot(NU_WEIGHT, surv))


# ---------------------------------------------------------------- 廃熱帯
H_PLANCK, K_B, C_LIGHT, SIGMA_SB = 6.62607015e-34, 1.380649e-23, 2.99792458e8, 5.670374419e-8
L_SUN, PC = 3.828e26, 3.0856775814913673e16
# WISE 等方波長と Vega 零点(Jarrett+2011, Table 1; Wright+2010): 単色近似
WISE_LAMBDA_UM = {"W3": 11.5608, "W4": 22.0883}
WISE_ZP_JY = {"W3": 31.674, "W4": 8.363}
# T_DS 潜在グリッド: [100, 700] K 対数一様 20 区間(Hephaistos II の格子域)
T_EDGES = np.geomspace(100.0, 700.0, 21)
T_CENTERS = np.sqrt(T_EDGES[:-1] * T_EDGES[1:])
T_WEIGHT = np.full(len(T_CENTERS), 1.0 / len(T_CENTERS))
GAMMA_LEVELS = (0.1, 0.5, 0.9)   # 帯閾値 γ0 = 0.1(最弱成員)、0.5/0.9 は感度枠・G3(ii) 用
GAMMA_INFO = 0.01                # 裁定 #2 修正 4: 情報列(帯定義外。空き度の主張には用いない)
K_SIGMA = 3.0                    # 超過判定の閾値(感度枠 5)
SNR_DET = 3.5                    # Hephaistos II §2.6


def planck_nu(T, lam_um):
    nu = C_LIGHT / (lam_um * 1e-6)
    x = H_PLANCK * nu / (K_B * T)
    return 2 * H_PLANCK * nu ** 3 / C_LIGHT ** 2 / np.expm1(x)    # W m^-2 Hz^-1 sr^-1


def ds_flux_jy(gamma, T, L_star_w, d_pc, band):
    """被覆率 γ・温度 T の黒体 DS(L_DS = γ L★)の地球での流束密度 [Jy]。
    F_ν = L_DS · π B_ν(T) / (σ T⁴) / (4π d²)。"""
    L_ds = gamma * L_star_w
    Fnu = L_ds * np.pi * planck_nu(T, WISE_LAMBDA_UM[band]) / (SIGMA_SB * T ** 4) / (4 * np.pi * (d_pc * PC) ** 2)
    return Fnu / 1e-26


def model_mag(m_star, gamma, F_ds_jy, band):
    """Hephaistos 式 1,3: 星は灰色吸収で (1−γ) 倍に減光、DS 流束を加算。m_star が NaN なら DS のみ。"""
    zp = WISE_ZP_JY[band]
    F_star = np.where(np.isfinite(m_star), zp * 10 ** (-0.4 * np.nan_to_num(m_star)), 0.0)
    return -2.5 * np.log10(((1 - gamma) * F_star + F_ds_jy) / zp)


def logL_interp_table(path):
    """Mamajek 表(EEM_dwarf_colors_Teff.txt)から (M_G → logL) の主系列補間関数を作る。"""
    hdr = [l for l in open(path) if l.startswith("#SpT")][0].lstrip("#").split()
    mg, ll = [], []
    for l in open(path):
        if l.startswith("#") or not l.strip():
            continue
        p = l.split()
        if len(p) < 31:
            continue
        d = dict(zip(hdr, p))
        try:
            mg.append(float(d["M_G"])); ll.append(float(d["logL"]))
        except ValueError:
            continue
    mg = np.array(mg); ll = np.array(ll)
    o = np.argsort(mg); mg, ll = mg[o], ll[o]
    # 単調化(同一 M_G の重複は平均)
    u, inv = np.unique(mg, return_inverse=True)
    lu = np.array([ll[inv == k].mean() for k in range(len(u))])
    return lambda MG: np.interp(np.clip(MG, u.min(), u.max()), u, lu), (float(u.min()), float(u.max()))


def build_locus(color, cmag, good, edges=np.arange(-0.6, 5.61, 0.1), min_n=30):
    """主系列軌跡: BP−RP ビンごとの (G−Wx) 中央値と MAD σ。good = 使用可能星マスク。"""
    cen, med, sig, n = [], [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = good & (color >= lo) & (color < hi)
        if m.sum() >= min_n:
            v = cmag[m]; mm = np.median(v)
            cen.append(0.5 * (lo + hi)); med.append(mm); sig.append(1.4826 * np.median(np.abs(v - mm))); n.append(int(m.sum()))
    return {"bp_rp": cen, "median": med, "sigma": sig, "n": n}


def locus_eval(locus, color):
    c = np.array(locus["bp_rp"]); m = np.array(locus["median"]); s = np.array(locus["sigma"])
    inside = (color >= c.min()) & (color <= c.max())
    med = np.where(inside, np.interp(color, c, m), np.nan)
    sig = np.where(inside, np.interp(color, c, s), np.nan)
    return med, sig


def eps_w1_star(G, bp_rp, d_pc, wmag, wsig, L_star_w, locus, gamma, k_sigma=K_SIGMA, band="W3"):
    """星 1 つ・1 帯(W3 or W4)・γ 固定で、T_DS グリッド各区間の検出指標 Θ(T) と診断値を返す。
    返り値: theta[T] (0/1), info dict(status, r_obs, detected)。
    規約:
      - wsig 有限 → 検出星。r_obs = (G−W) − locus(BP−RP)。既に r_obs ≥ kσ なら status='candidate'(判定不能)。
      - wsig NaN かつ wmag 有限 → 2σ 上限値。検出には F_model ≥ 1.75 F_2σ(= 3.5σ)が必要。
      - wmag NaN → status='no_phot'(判定不能)。
    """
    theta = np.zeros(len(T_CENTERS))
    if not np.isfinite(wmag) or not np.isfinite(G) or not np.isfinite(bp_rp):
        return theta, {"status": "no_phot", "r_obs": np.nan}
    med, sig_loc = locus_eval(locus, np.array([bp_rp]))
    med, sig_loc = float(med[0]), float(sig_loc[0])
    if not np.isfinite(med):
        return theta, {"status": "model_out", "r_obs": np.nan}
    zp = WISE_ZP_JY[band]
    G_model = G - 2.5 * np.log10(1 - gamma)
    detected = bool(np.isfinite(wsig))
    if detected:
        r_obs = (G - wmag) - med
        sig_tot = float(np.hypot(wsig, sig_loc))
        if r_obs >= k_sigma * sig_tot:
            return theta, {"status": "candidate", "r_obs": r_obs}
        for j, T in enumerate(T_CENTERS):
            Fds = ds_flux_jy(gamma, T, L_star_w, d_pc, band)
            w_model = model_mag(wmag, gamma, Fds, band)
            r_model = (G_model - w_model) - med
            theta[j] = 1.0 if r_model >= k_sigma * sig_tot else 0.0
        return theta, {"status": "ok", "r_obs": r_obs}
    # 非検出(2σ 上限)
    F_2s = zp * 10 ** (-0.4 * wmag)
    sig_flux = F_2s / 2.0
    for j, T in enumerate(T_CENTERS):
        Fds = ds_flux_jy(gamma, T, L_star_w, d_pc, band)
        F_model = Fds                      # 光球は上限以下なので保守的に DS 流束のみで判定
        if F_model < SNR_DET * sig_flux:
            continue
        w_model = -2.5 * np.log10(F_model / zp)
        sig_w = 1.0857 * sig_flux / F_model
        r_model = (G_model - w_model) - med
        theta[j] = 1.0 if r_model >= k_sigma * float(np.hypot(sig_w, sig_loc)) else 0.0
    return theta, {"status": "ok_upperlimit", "r_obs": np.nan}


def eps_w1_vector(G, bp_rp, d_pc, wmag, wsig, L_star_w, locus, gamma, k_sigma=K_SIGMA, band="W3"):
    """eps_w1_star のベクトル版(星数 N)。返り値: theta (N, nT) 0/1、status (N,) 文字列、r_obs (N,)。
    規約は eps_w1_star と同一(単体テストで逐一一致を確認する)。"""
    N = len(G); nT = len(T_CENTERS)
    theta = np.zeros((N, nT)); status = np.full(N, "no_phot", dtype=object); r_obs = np.full(N, np.nan)
    has = np.isfinite(wmag) & np.isfinite(G) & np.isfinite(bp_rp)
    med, sig_loc = locus_eval(locus, np.where(np.isfinite(bp_rp), bp_rp, 0.0))
    med = np.where(has, med, np.nan)
    model_out = has & ~np.isfinite(med)
    status[model_out] = "model_out"
    use = has & np.isfinite(med)
    zp = WISE_ZP_JY[band]
    G_model = G - 2.5 * np.log10(1 - gamma)
    det = use & np.isfinite(wsig)
    # --- 検出星
    r = (G - wmag) - med
    sig_tot = np.hypot(np.nan_to_num(wsig), sig_loc)
    cand = det & (r >= k_sigma * sig_tot)
    status[cand] = "candidate"; r_obs[det] = r[det]
    ok = det & ~cand
    status[ok] = "ok"
    idx = np.where(ok)[0]
    if len(idx):
        T = T_CENTERS[None, :]
        Fds = ds_flux_jy(gamma, T, L_star_w[idx, None], d_pc[idx, None], band)          # (n, nT)
        F_star = zp * 10 ** (-0.4 * wmag[idx, None])
        w_model = -2.5 * np.log10(((1 - gamma) * F_star + Fds) / zp)
        r_model = (G_model[idx, None] - w_model) - med[idx, None]
        theta[idx] = (r_model >= k_sigma * sig_tot[idx, None]).astype(float)
    # --- 非検出(2σ 上限)
    ul = use & ~np.isfinite(wsig)
    status[ul] = "ok_upperlimit"
    idx = np.where(ul)[0]
    if len(idx):
        T = T_CENTERS[None, :]
        Fds = ds_flux_jy(gamma, T, L_star_w[idx, None], d_pc[idx, None], band)
        F_2s = zp * 10 ** (-0.4 * wmag[idx, None]); sig_flux = F_2s / 2.0
        detectable = Fds >= SNR_DET * sig_flux
        with np.errstate(divide="ignore", invalid="ignore"):
            w_model = -2.5 * np.log10(Fds / zp)
            sig_w = 1.0857 * sig_flux / Fds
            r_model = (G_model[idx, None] - w_model) - med[idx, None]
            th = (r_model >= k_sigma * np.hypot(sig_w, sig_loc[idx, None]))
        theta[idx] = (detectable & th).astype(float)
    return theta, status, r_obs


def merge_mir(theta_w3, theta_w4):
    """W3 または W4 で検出 → 区間ごとの ε_T = 1 − (1−θ3)(1−θ4)。T_DS 上で併合。"""
    surv = (1 - theta_w3) * (1 - theta_w4)
    return surv, 1.0 - (surv @ T_WEIGHT)
