#!/usr/bin/env python3
"""図 1(π 掃引の上界曲線)の機械生成。数値は lambda_ledger.json の凍結値のみ(ハードコード禁止)。
再現: python3 scripts/build_paper_figs.py → docs/phase5/paper/figs/fig1_pi_sweep.png/.pdf"""
import os, json, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
L = json.load(open(os.path.join(ROOT, "data/phase2/lambda_ledger.json")))
S = L["stars"]; g = L["summary"]["pi_grid"]
pi = np.geomspace(g["min"], g["max"], g["n"])
def expit(z): return 1 / (1 + np.exp(-z))
curves = []
colors = {"R1": ["#27496d", "#4a6f97", "#7897b5"], "R3": ["#6d5327", "#977a4a", "#b59d78"]}
for b, style in [("R1", "-"), ("R3", "--")]:
    st = np.array(S[f"status_{b}"]); lam = np.array(S[f"lambda_{b}"])[st == "ok"]
    for q, lab in [(0.0, "min"), (0.5, "median"), (1.0, "max")]:
        v = float(np.quantile(lam, q))
        curves.append((b, lab, v, style))
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for b, lab, v, style in curves:
    P = expit(np.log(pi / (1 - pi)) + np.log(v))
    ax.plot(pi, P, style, lw=1.4, color=colors[b][["min", "median", "max"].index(lab)], label=f"T-{b} {lab}: $\\Lambda$ = {v:.4f}")
ax.plot(pi, pi, ":", color="0.5", lw=1.0, label="prior ($P = \\pi$)")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("prior $\\pi$"); ax.set_ylabel("upper bound  $P(\\mathrm{occupied} \\mid D, T, \\pi)$")
ax.set_title("Upper-bound curves (frozen-ledger $\\Lambda$)", fontsize=11)
ax.grid(alpha=0.25, which="both"); ax.legend(fontsize=8, loc="upper left")
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(ROOT, "docs/phase5/paper/figs", f"fig1_pi_sweep.{ext}"), dpi=300)
print("fig1 written; curves:", [(b, lab, round(v, 4)) for b, lab, v, _ in curves])
