"""ε 導出式・併合規則の単体テスト(Phase 1)。python3 -m pytest tests/ または python3 -m unittest。"""
import os, sys, json, unittest, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from vacancy import epsilon as E
ROOT = os.path.join(os.path.dirname(__file__), "..")


class TestRadio(unittest.TestCase):
    def test_nu_grid_partition(self):
        self.assertAlmostEqual(E.NU_WIDTH.sum(), 2.35, places=9)
        self.assertAlmostEqual(E.NU_WEIGHT.sum(), 1.0, places=12)

    def test_cover_matrix(self):
        insts, M = E.cover_matrix()
        # 被覆幅: L = 0.10+0.46+0.10 = 0.66, S = 0.10+0.40+0.24+0.20 = 0.94, P = 0.20+0.65 = 0.85 GHz
        w = {i: float(E.NU_WIDTH[M[a]].sum()) for a, i in enumerate(insts)}
        self.assertAlmostEqual(w["GBT L-band"], 0.66, places=9)
        self.assertAlmostEqual(w["GBT S-band"], 0.94, places=9)
        self.assertAlmostEqual(w["Parkes 10-cm"], 0.85, places=9)
        # ノッチ区間(1.20–1.34, 2.30–2.36)はどの帯も被覆しない
        self.assertFalse(M[:, 1].any()); self.assertFalse(M[:, 5].any())

    def test_eirp_min_reproduces_ws20(self):
        w = np.load(os.path.join(ROOT, "data", "phase0", "ws20_rows.npz"), allow_pickle=True)
        inst = w["inst"]; calc = np.array([E.eirp_min(str(i), d, r) for i, d, r in zip(inst[:5000], w["rest"][:5000], w["resp"][:5000])])
        ratio = calc / w["eirp"][:5000]
        self.assertLess(np.abs(ratio - 1).max(), 1e-6)

    def test_merge_rule_same_band_twice(self):
        """裁定 #1 C の検算: 同一帯 2 回観測(被覆率 c、帯内 ε=1)→ 併合 ε = c(素朴積なら 1−(1−c)²)。"""
        insts, M = E.cover_matrix()
        c = float(E.NU_WIDTH[M[0]].sum() / E.NU_WIDTH.sum())          # GBT L の被覆率
        surv, em = E.merge_radio(["GBT L-band", "GBT L-band"], [1.0, 1.0], insts, M)
        self.assertAlmostEqual(em, c, places=12)
        self.assertGreater(1 - (1 - c) ** 2, c)                           # 素朴積は過大
        # f_pipe=0.5 の 2 回観測: 帯内生存 0.25 → ε = c·0.75
        surv, em = E.merge_radio(["GBT L-band", "GBT L-band"], [0.5, 0.5], insts, M)
        self.assertAlmostEqual(em, c * 0.75, places=12)

    def test_merge_union_three_bands(self):
        insts, M = E.cover_matrix()
        surv, em = E.merge_radio(insts, [1.0, 1.0, 1.0], insts, M)
        # 合成被覆 = 窓 − ノッチ(0.14 + 0.06) = 2.15 / 2.35
        self.assertAlmostEqual(em, 2.15 / 2.35, places=12)

    def test_monotone_nonincreasing(self):
        insts, M = E.cover_matrix()
        rng = np.random.default_rng(1)
        for _ in range(200):
            n = rng.integers(1, 8); rows = [str(insts[k]) for k in rng.integers(0, 3, n)]; eps = rng.random(n)
            prev = 1.0
            for j in range(1, n + 1):
                surv, em = E.merge_radio(rows[:j], eps[:j], insts, M)
                self.assertLessEqual(1 - em, prev + 1e-15); prev = 1 - em

    def test_r3_marginalization(self):
        """裁定 #2 修正 1: f_ill は星単位潜在変数。L 帯 1 行 Θ=1 → ε = c_L · f_pipe · mean(f_ill 格子)。
        2 行(同一帯)なら Π の中で同じ f を共有する(観測行ごとに独立に引かない)。"""
        insts, M = E.cover_matrix(); c = float(E.NU_WIDTH[M[0]].sum() / E.NU_WIDTH.sum())
        surv, em = E.merge_radio_r3(["GBT L-band"], [1.0], insts, M)
        self.assertAlmostEqual(em, c * 0.5 * E.F_ILL_GRID.mean(), places=15)
        surv, em2 = E.merge_radio_r3(["GBT L-band", "GBT L-band"], [1.0, 1.0], insts, M)
        shared = c * float(np.mean(1 - (1 - 0.5 * E.F_ILL_GRID) ** 2))           # f を共有した厳密値
        indep = c * float(1 - (1 - 0.5 * E.F_ILL_GRID.mean()) ** 2)              # 行ごと独立(禁止)の近似
        self.assertAlmostEqual(em2, shared, places=15)
        self.assertLess(em2, indep)                                               # 独立扱いは空き側に過大
        surv, em0 = E.merge_radio_r3(["GBT L-band"], [0.0], insts, M)
        self.assertLess(abs(em0), 1e-12)

    def test_r3_factor(self):
        self.assertAlmostEqual(E.F_ILL_R3_CENTRAL, 10 ** -3.5, places=15)
        self.assertEqual(float(E.eps_radio_row("R3", 1e12)), 0.0)        # EIRP_min > 1e11 → 感度外
        self.assertAlmostEqual(float(E.eps_radio_row("R3", 1e10)), 0.5 * 10 ** -3.5)
        self.assertAlmostEqual(float(E.eps_radio_row("R3", 1e10, f_ill=1e-2)), 0.5e-2)


class TestWasteHeat(unittest.TestCase):
    def test_ds_flux_physics(self):
        """L_DS = γL★ の黒体球の半径 R = sqrt(L/(4πσT⁴)) を使った直接計算 F = π B_ν (R/d)² と一致。"""
        for T in (100, 300, 700):
            L = 0.1 * E.L_SUN; R = np.sqrt(L / (4 * np.pi * E.SIGMA_SB * T ** 4)); d = 10 * E.PC
            direct = np.pi * E.planck_nu(T, E.WISE_LAMBDA_UM["W3"]) * (R / d) ** 2 / 1e-26
            self.assertAlmostEqual(E.ds_flux_jy(0.1, T, E.L_SUN, 10.0, "W3") / direct, 1.0, places=10)

    def test_sun_photosphere_vs_ds(self):
        """太陽@10 pc: 光球 W3 ≈ 1.9 Jy(RJ 則)に対し γ=0.1, 300 K の DS は ~90 Jy。"""
        nu = E.C_LIGHT / 11.5608e-6
        F_ph = np.pi * 2 * nu ** 2 * E.K_B * 5772 / E.C_LIGHT ** 2 * (6.957e8 / (10 * E.PC)) ** 2 / 1e-26
        self.assertTrue(1.5 < F_ph < 2.5)
        self.assertTrue(60 < E.ds_flux_jy(0.1, 300, E.L_SUN, 10.0, "W3") < 120)

    def test_model_mag_limits(self):
        self.assertAlmostEqual(float(E.model_mag(5.0, 0.0, 0.0, "W3")), 5.0, places=12)     # γ=0, DS なし → 不変
        self.assertGreater(float(E.model_mag(5.0, 0.5, 0.0, "W3")), 5.0)                   # 減光のみ → 暗くなる
        self.assertLess(float(E.model_mag(5.0, 0.5, 100.0, "W3")), 5.0)                    # 大きな DS → 明るくなる

    def test_vector_matches_scalar(self):
        locus = json.load(open(os.path.join(ROOT, "data", "phase1", "ms_locus_v0.json")))
        g = np.load(os.path.join(ROOT, "data", "phase0", "gcns_core.npz"))
        fn, _ = E.logL_interp_table(os.path.join(ROOT, "data", "phase1", "EEM_dwarf_colors_Teff.txt"))
        rng = np.random.default_rng(7); idx = rng.choice(len(g["G"]), 400, replace=False)
        G = g["G"][idx]; bp = g["BP"][idx] - g["RP"][idx]; d = g["d50"][idx]
        L = 10 ** fn(G + 5 - 5 * np.log10(d)) * E.L_SUN
        for band, key in (("W3", "G-W3"), ("W4", "G-W4")):
            wm = g[band][idx]; ws = g["e" + band][idx]
            tv, sv, rv = E.eps_w1_vector(G, bp, d, wm, ws, L, locus[key], 0.1, band=band)
            for k in range(len(idx)):
                ts, info = E.eps_w1_star(G[k], bp[k], d[k], wm[k], ws[k], L[k], locus[key], 0.1, band=band)
                self.assertEqual(info["status"], sv[k])
                np.testing.assert_array_equal(ts, tv[k])

    def test_gamma_monotone(self):
        """γ を上げると各 T_DS 区間の検出指標は非減少(候補化しない範囲で)。"""
        locus = json.load(open(os.path.join(ROOT, "data", "phase1", "ms_locus_v0.json")))
        G, bp, d = 8.0, 1.0, 30.0; wm, ws = 6.0, 0.03; L = 0.3 * E.L_SUN
        prev = np.zeros(len(E.T_CENTERS))
        for gm in (0.001, 0.01, 0.1, 0.5):
            th, info = E.eps_w1_star(G, bp, d, wm, ws, L, locus["G-W3"], gm, band="W3")
            self.assertTrue(np.all(th >= prev)); prev = th

    def test_merge_mir(self):
        t3 = np.zeros(len(E.T_CENTERS)); t4 = np.zeros(len(E.T_CENTERS)); t3[:5] = 1; t4[3:8] = 1
        surv, em = E.merge_mir(t3, t4)
        self.assertAlmostEqual(float(em), 8 / len(E.T_CENTERS), places=12)


if __name__ == "__main__":
    unittest.main()
