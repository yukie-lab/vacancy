#!/usr/bin/env python3
"""論文図の機械生成(裁定 #6・#9)。全て凍結成果物からの転記描画のみ(再計算・乱数なし)。
図 1 (§4.5): G3(iii) d–Λ(g3_iii.json)/ 図 2 (§5.1): 受信帯被覆と Λ の構成(radio_obs+lambda_ledger の実在組合せ)/
図 3 (§5.2): アトラス概観(sim_display_v1.json、シミュレータと同配色規律)/ 図 4 (§5.3): π 掃引(lambda_ledger)。
再現: python3 scripts/build_paper_figs.py → docs/phase5/paper/figs/*.png"""
import os, json, base64, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FIGS = os.path.join(ROOT, "docs/phase5/paper/figs"); os.makedirs(FIGS, exist_ok=True)
def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIGS, f"{name}.{ext}"), dpi=300)
    print(name, "written")
def expit(z): return 1 / (1 + np.exp(-z))
# シミュレータと同一の価値中立ランプ(vacancy-atlas js/atlas3d.js ramp() の移植)
def ramp(u):
    u = np.clip(u, 0, 1); r = 0.55 + 0.35 * u; g = 0.62 + 0.2 * u; b = 0.75 + 0.25 * u; k = 0.35 + 0.65 * u
    return np.stack([r * k + 0.15 * (1 - u), g * k + 0.15 * (1 - u), b * k + 0.2 * (1 - u)], -1)
def color_of(post):
    lo, hi = np.log10(1e-4), np.log10(1e-1)
    return ramp((np.log10(np.maximum(post, 1e-12)) - lo) / (hi - lo))

L = json.load(open(os.path.join(ROOT, "data/phase2/lambda_ledger.json"))); S = L["stars"]

# ---------------- 図 1: G3(iii) d–Λ
g3 = json.load(open(os.path.join(ROOT, "data/phase3/g3_iii.json")))
rows = g3["rows"]; d = [r["d_pc"] for r in rows]
fig, ax = plt.subplots(figsize=(6.2, 4.0))
ax.plot(d, [r["lambda_marginalized"] for r in rows], "-", color="#27496d", lw=1.6, label="marginalised over $f_{\\rm ill}$")
ax.plot(d, [r["lambda_f_ill_1e-2"] for r in rows], "--", color="#4a6f97", lw=1.4, label="$f_{\\rm ill}=10^{-2}$ (upper end)")
ax.plot(d, [r["lambda_extreme_fill1_fpipe1"] for r in rows], ":", color="#977a4a", lw=1.6, label="red-flag extreme ($f_{\\rm ill}=f_{\\rm pipe}=1$)")
for x, lab in [(5.24, "Parkes 10-cm limit"), (10.9, "GBT limit")]:
    ax.axvline(x, color="0.65", lw=0.8, ls="-."); ax.text(x, 0.55, " " + lab, rotation=90, fontsize=7, color="0.4", va="bottom")
ax.axhline(0.99, color="0.8", lw=0.7); ax.text(1.35, 0.99, "0.99 criterion", fontsize=7, color="0.4", va="bottom")
ax.set_xlabel("distance of the virtual Solar-System row  d [pc]"); ax.set_ylabel("$\\Lambda$ (T-R3)")
ax.set_ylim(0, 1.05); ax.grid(alpha=0.25); ax.legend(fontsize=8, loc="center right")
ax.set_title("G3(iii): Solar-System self-test (values from g3_iii.json)", fontsize=10)
# ズームインセット(裁定 #10-3): 合格 2 曲線と 0.99 基準線を判読可能に
axi = ax.inset_axes([0.13, 0.20, 0.46, 0.34])
axi.plot(d, [r["lambda_marginalized"] for r in rows], "-", color="#27496d", lw=1.4)
axi.plot(d, [r["lambda_f_ill_1e-2"] for r in rows], "--", color="#4a6f97", lw=1.2)
axi.axhline(0.99, color="0.7", lw=0.8)
axi.axvline(5.24, color="0.65", lw=0.6, ls="-.")
axi.set_ylim(0.985, 1.001); axi.set_xlim(min(d), max(d))
axi.tick_params(labelsize=6); axi.grid(alpha=0.25)
axi.set_title("zoom: [0.985, 1.001]", fontsize=6.5)
ax.indicate_inset_zoom(axi, edgecolor="0.6", lw=0.6)
fig.tight_layout(); save(fig, "fig1_g3iii_dlambda")

# ---------------- 図 2: 受信帯被覆 9 区間と Λ の構成(実在の観測組合せ)
R = json.load(open(os.path.join(ROOT, "data/phase1/radio_obs_v0.json")))
edges = R["nu_grid_GHz"]; cover = R["cover"]
by = collections.defaultdict(list)
for r in R["rows"]: by[r["star"]].append(r["inst"])
lamR1 = dict(zip(S["id"], S["lambda_R1"])); stR1 = dict(zip(S["id"], S["status_R1"]))
combo_stats = collections.Counter()
combo_lam = {}
for sid, insts in by.items():
    if stR1.get(sid) != "ok": continue
    key = tuple(sorted(insts)); combo_stats[key] += 1; combo_lam[key] = lamR1[sid]
top = [k for k, _ in combo_stats.most_common(6)]
top.sort(key=lambda k: -combo_lam[k])
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.6), height_ratios=[1, 1.5])
bands = {"GBT L-band": ("#27496d", [(1.10, 1.20), (1.34, 1.90)]), "GBT S-band": ("#4a6f97", [(1.80, 2.30), (2.36, 2.80)]), "Parkes 10-cm": ("#977a4a", [(2.60, 3.45)])}
for yi, (name, (col, spans)) in enumerate(bands.items()):
    for lo, hi in spans:
        a1.barh(yi, hi - lo, left=lo, height=0.55, color=col, alpha=0.85)
    a1.text(3.5, yi, " " + name, va="center", fontsize=8)
for e in edges: a1.axvline(e, color="0.75", lw=0.5)
a1.set_yticks([]); a1.set_xlim(1.0, 4.2); a1.set_xlabel("frequency $\\nu$ [GHz] (9 common intervals; gaps = notches)", fontsize=8)
a1.set_title("Receiver coverage of the declared window [1.10, 3.45] GHz", fontsize=9)
labels = []; vals = []; ns = []
short = {"GBT L-band": "L", "GBT S-band": "S", "Parkes 10-cm": "P"}
for k in top:
    labels.append("+".join(short[i] for i in k)); vals.append(combo_lam[k]); ns.append(combo_stats[k])
cols = color_of(expit(np.log(0.01 / 0.99) + np.log(np.array(vals))))   # 彩色 = π=1e-2 の事後(凍結式、シミュレータと同一規律)
a2.barh(range(len(vals)), vals, color=[c for c in cols], height=0.6)
for i, (v, n) in enumerate(zip(vals, ns)):
    a2.text(v + 0.01, i, f"$\\Lambda$ = {v:.4f}  ({n} stars)", va="center", fontsize=8)
a2.set_yticks(range(len(labels))); a2.set_yticklabels(labels, fontsize=8)
a2.set_xlim(0, 1.38); a2.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); a2.set_xlabel("merged $\\Lambda$ (T-R1) for observation-row combinations present in the ledger", fontsize=8)
a2.grid(alpha=0.25, axis="x")
fig.tight_layout(); save(fig, "fig2_coverage_lambda")

# ---------------- 図 3: アトラス概観(sim_display から。シミュレータと同配色)
D = json.load(open(os.path.join(os.path.expanduser("~"), "Desktop/test/vacancy-atlas/data/sim_display_v1.json")))
def b64f(s): return np.frombuffer(base64.b64decode(s), dtype=np.float32)
def b64u8(s): return np.frombuffer(base64.b64decode(s), dtype=np.uint8)
N = D["n_stars"]; pos = b64f(D["pos_pc_b64"]).reshape(N, 3); hasp = b64u8(D["has_pos_b64"]).astype(bool)
st1 = b64u8(D["status"]["R1"])
lam = np.full(N, np.nan, dtype=np.float32)
idx = np.array(D["lambda"]["R1"]["index"]); lam[idx] = b64f(D["lambda"]["R1"]["lambda_b64"])
emb_idx = np.array(D["embark"]["index"])
fig, ax = plt.subplots(figsize=(6.4, 6.2))
und = hasp & (st1 == 0)
sel = np.where(und)[0][::8]
ax.scatter(pos[sel, 0], pos[sel, 1], s=0.5, c="#4a5363", alpha=0.35, lw=0, rasterized=True)
er = emb_idx[hasp[emb_idx]]
ax.scatter(pos[er, 0], pos[er, 1], s=9, facecolors="none", edgecolors="#d9a441", lw=0.4, alpha=0.5, rasterized=True)
ok = np.where(hasp & (st1 == 1))[0]
post = expit(np.log(0.01 / 0.99) + np.log(np.maximum(lam[ok], 1e-12)))
ax.scatter(pos[ok, 0], pos[ok, 1], s=6, c=color_of(post), lw=0, zorder=3)
ax.scatter([0], [0], marker="*", s=60, c="#f4e0b0", edgecolors="0.3", lw=0.4, zorder=4)
ax.set_aspect("equal"); ax.set_xlim(-105, 105); ax.set_ylim(-105, 105)
ax.set_xlabel("Galactic X [pc]"); ax.set_ylabel("Galactic Y [pc]")
ax.set_title("Atlas overview (projection onto the Galactic plane; from sim_display_v1)", fontsize=9)
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([], [], marker="o", ls="", ms=4, mfc=ramp(np.array([0.6]))[0], mec="none", label="T-R1 bound (posterior colour, $\\pi=10^{-2}$)"),
                   Line2D([], [], marker="o", ls="", ms=4, mfc="#4a5363", mec="none", label="undecidable (grey, thinned 1/8)"),
                   Line2D([], [], marker="o", ls="", ms=5, mfc="none", mec="#d9a441", label="EMBARK-reachable (outline)"),
                   Line2D([], [], marker="*", ls="", ms=8, mfc="#f4e0b0", mec="0.3", label="Sun")], fontsize=7, loc="upper right")
fig.tight_layout(); save(fig, "fig3_atlas_overview")

# ---------------- 図 4: π 掃引(従来の図)
g = L["summary"]["pi_grid"]; pi = np.geomspace(g["min"], g["max"], g["n"])
curves = []
colors = {"R1": ["#27496d", "#4a6f97", "#7897b5"], "R3": ["#6d5327", "#977a4a", "#b59d78"]}
for b, style in [("R1", "-"), ("R3", "--")]:
    st = np.array(S[f"status_{b}"]); lamv = np.array(S[f"lambda_{b}"])[st == "ok"]
    for q, lab in [(0.0, "min"), (0.5, "median"), (1.0, "max")]:
        curves.append((b, lab, float(np.quantile(lamv, q)), style))
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for b, lab, v, style in curves:
    P = expit(np.log(pi / (1 - pi)) + np.log(v))
    ax.plot(pi, P, style, lw=1.4, color=colors[b][["min", "median", "max"].index(lab)], label=f"T-{b} {lab}: $\\Lambda$ = {v:.4f}")
ax.plot(pi, pi, ":", color="0.5", lw=1.0, label="prior ($P = \\pi$)")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("prior $\\pi$"); ax.set_ylabel("upper bound  $P(\\mathrm{occupied} \\mid D, T, \\pi)$")
ax.set_title("Upper-bound curves (frozen-ledger $\\Lambda$)", fontsize=11)
ax.grid(alpha=0.25, which="both"); ax.legend(fontsize=8, loc="upper left")
fig.tight_layout(); save(fig, "fig4_pi_sweep")
