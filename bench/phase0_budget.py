#!/usr/bin/env python3
"""Phase 0.4 計算予算実測 — 合算数理(02 設計書 §3)の本番同等の形を合成 ε で走らせる。

形: 星 N × 帯 B × 観測 S_max(疎) × 潜在区間 C × MC 実現 M
  log Λ_{i,T,mc} = logsumexp_c( log w_c + Σ_s log1p(−ε_{s,i,c,T,mc}) )
ε の数値に科学的意味はない(一様乱数)。計算コストの形のみ本番同等。
"""
import time, json, sys, os, numpy as np

def run(N, B=4, S=8, C=6, M=1000, seed=20260823, chunk=20000):
    rng = np.random.default_rng(seed)
    t0 = time.time()
    # 観測の疎性: 星ごとに観測数 0..S(実データは多くの星で 0)
    n_obs = rng.integers(0, S + 1, size=N)
    w = np.full(C, 1.0 / C)
    logw = np.log(w)
    out = np.empty((N, B, 3))  # 5/50/95 分位の log Λ
    for a in range(0, N, chunk):
        b = min(N, a + chunk); n = b - a
        # ε: (n, B, S, C, M) を一度に作ると巨大なので M をループ
        acc = np.zeros((M, n, B, C))
        for s in range(S):
            active = (n_obs[a:b] > s)[None, :, None, None]
            eps = rng.random((M, n, B, C)) * 0.9
            acc += np.where(active, np.log1p(-eps), 0.0)
        # logsumexp over C
        mx = acc.max(axis=-1, keepdims=True)
        logL = (mx[..., 0] + np.log(np.exp(acc - mx).sum(axis=-1) * w[0]))  # w 一様
        q = np.quantile(logL, [0.05, 0.5, 0.95], axis=0)  # (3, n, B)
        out[a:b] = np.moveaxis(q, 0, -1)
    dt = time.time() - t0
    return dt, out

if __name__ == "__main__":
    res = {}
    for N, M in [(2000, 1000), (20000, 1000), (331312, 20), (331312, 100)]:
        dt, out = run(N, M=M)
        res[f"N={N},M={M}"] = {"seconds": round(dt, 2), "per_star_band_ms": round(1000 * dt / (N * 4), 4)}
        print(N, M, f"{dt:.2f}s", flush=True)
    # 外挿: 本番 N=331,312, M=1000
    base = res["N=331312,M=100"]["seconds"]
    res["extrapolated_N=331312,M=1000"] = {"seconds": round(base * 10, 1)}
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data", "phase0"), exist_ok=True)
    json.dump(res, open(os.path.join(os.path.dirname(__file__), "..", "data", "phase0", "budget_results.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
