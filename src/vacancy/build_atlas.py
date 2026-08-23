#!/usr/bin/env python3
"""Phase 4: 三軸アトラス v1(空き度 × 到達可能性 × 定住資源性)。全て輸入・結合のみ(再計算なし、第4条)。

空き度軸   = lambda_ledger.json(Phase 2)。主張帯 = 電波 3 帯(T-R1/R2/R3)。W1 は情報レイヤ(claim=false、裁定 #4)。
到達可能性 = EMBARK reachability atlas v1(embark_atlas_v1.json)を DR3 source_id で結合。不一致星は当該軸「判定不能」。
定住資源性 = GCNS 内蔵量(M_G, BP−RP, WDprob, RUWE)+ Mamajek 表の色→型区分(既製表の輸入)+ NASA Exoplanet Archive(gaia_dr3_id で結合)
             + HWC(Habitable Worlds Catalog、照合台のみ)。スライダー S1(狭義)〜S3(資源的広義)は「軸の関数」であり判定基準ではない。
交差表示   = 「行ける × 空いている(T 帯条件付き)」の計数表。積・加重和・単一スコアは作らない(第4条4項)。
出力: data/phase4/atlas_v1.json, data/phase4/atlas_v1_summary.json
"""
import os, sys, json, csv, base64, hashlib, datetime, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, ".."))
from vacancy import epsilon as E
ROOT = os.path.join(HERE, "..", ".."); P0 = os.path.join(ROOT, "data", "phase0"); P1 = os.path.join(ROOT, "data", "phase1"); P2 = os.path.join(ROOT, "data", "phase2")
P4 = os.path.join(ROOT, "data", "phase4"); RAW4 = os.path.join(ROOT, "data", "raw", "phase4"); os.makedirs(P4, exist_ok=True)
EMB = os.path.join(ROOT, "..", "embark", "data", "release", "embark_atlas_v1.json")
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

# ------------------------------------------------------------ 空き度軸(輸入)
L = json.load(open(os.path.join(P2, "lambda_ledger.json"))); S = L["stars"]; ids = S["id"]; NK = len(ids); idx = {s: k for k, s in enumerate(ids)}
g = {k: v for k, v in np.load(os.path.join(P0, "gcns_core.npz")).items()}; N = len(g["G"])
assert all(ids[k] == str(int(g["source_id"][k])) for k in (0, N // 2, N - 1))

# ------------------------------------------------------------ 到達可能性軸(EMBARK 輸入・結合)
emb = json.load(open(EMB)); es = emb["stars"]; e_ids = es["source_id_str"]; n_e = len(e_ids)
bands_e = emb["axes"]["bands"]; Ls_e = emb["axes"]["L"]; dv_e = emb["axes"]["dv_budget_kms"]
def decode(layer):
    v = es["layers"][layer]; raw = np.frombuffer(base64.b64decode(v["data_b64"]), dtype=np.uint8)
    nbytes = (v["bits_per_star"] + 7) // 8; bits = np.unpackbits(raw.reshape(n_e, nbytes), axis=1)[:, :v["bits_per_star"]]
    return bits.astype(bool)
lay = {k: decode(k) for k in es["layers"]}
e_index = {s: j for j, s in enumerate(e_ids)}
join = np.full(NK, -1, dtype=np.int64)
for k, s in enumerate(ids):
    j = e_index.get(s)
    if j is not None: join[k] = j
joined = join >= 0
reach_status = np.where(joined, "joined", "undecidable_not_in_embark").astype(object)
# 層別の星単位要約(帯 × 寿命 の 30 bit を文字列で保持。同行は予算別 4 × 30)
def bits_str(layer, j): return "".join("1" if b else "0" for b in lay[layer][j])
reach = {"flyby_single_t0": [], "flyby_single_any_tdep": [], "rendezvous_single_any_tdep": [], "rendezvous_multi_any_tdep": [], "intake_dr4_any_tdep": [], "sigma_pos_undecidable_t0": []}
any_flag = {k: np.zeros(NK, dtype=bool) for k in reach}
for k in range(NK):
    j = join[k]
    for layer in reach:
        if j >= 0:
            reach[layer].append(bits_str(layer, j)); any_flag[layer][k] = lay[layer][j].any()
        else:
            reach[layer].append(None)
emb_in_gcns = int(sum(1 for s in e_ids if s in idx))

# ------------------------------------------------------------ 定住資源性軸(輸入)
G, BP, RP, d50, ruwe, wd = g["G"], g["BP"], g["RP"], g["d50"], g["ruwe"], g["wdprob"]
bp_rp = BP - RP; MG = G + 5 - 5 * np.log10(d50)
giant = (MG < 4) & (MG < 7 * bp_rp - 3); wd_aen = MG > 3 * bp_rp + 5; ms = np.isfinite(bp_rp) & ~giant & ~wd_aen
# Mamajek 表(既製)から BP−RP → 型区分(主系列のみ有効)
def mamajek_bprp_spt(path):
    hdr = [l for l in open(path) if l.startswith("#SpT")][0].lstrip("#").split(); rows = []
    for l in open(path):
        if l.startswith("#") or not l.strip(): continue
        p = l.split()
        if len(p) < 31: continue
        d = dict(zip(hdr, p))
        try: rows.append((float(d["Bp-Rp"]), d["SpT"]))
        except ValueError: continue
    rows.sort(); return np.array([r[0] for r in rows]), [r[1] for r in rows]
mb, ms_spt = mamajek_bprp_spt(os.path.join(P1, "EEM_dwarf_colors_Teff.txt"))
def spt_class(c):
    if not np.isfinite(c): return None
    j = int(np.argmin(np.abs(mb - c))); return ms_spt[j]
spt = [spt_class(c) if (ms[k] and -0.5 < c < 5.5) else None for k, c in enumerate(bp_rp)]
letter = np.array([s[0] if s else "" for s in spt])
# スライダー(軸の関数。判定基準ではない)
S1 = ms & np.isin(letter, ["F", "G", "K"]) & (bp_rp >= 0.50) & (bp_rp <= 1.43)     # 狭義: FGK 主系列(F0–K5 相当)
S2 = ms                                                                             # 主系列全型(O–M)
S3 = np.ones(N, dtype=bool)                                                         # 資源的広義: 全恒星(WD・巨星含む)
# NASA Exoplanet Archive(gaia_dr3_id で直接結合)
nea = list(csv.DictReader(open(os.path.join(RAW4, "nea_pscomppars_lt120pc.csv"))))
planets = {}
for r in nea:
    gid = (r.get("gaia_dr3_id") or "").replace("Gaia DR3 ", "").strip()
    if gid and gid in idx:
        planets.setdefault(gid, []).append(r["pl_name"])
n_nea_hosts = len({r["hostname"] for r in nea}); n_nea_with_dr3 = len({r["hostname"] for r in nea if (r.get("gaia_dr3_id") or "").startswith("Gaia DR3")})
# HWC(照合台のみ): 惑星名 → NEA ホストの DR3 id で結合、無ければ位置(S_RA/S_DEC、5")
hwc = list(csv.DictReader(open(os.path.join(RAW4, "hwc.csv"))))
pl2host = {r["pl_name"]: (r.get("gaia_dr3_id") or "").replace("Gaia DR3 ", "").strip() for r in nea}
def unit(ra, de):
    ra = np.radians(ra); de = np.radians(de); return np.stack([np.cos(de) * np.cos(ra), np.cos(de) * np.sin(ra), np.sin(de)], -1)
U = unit(g["ra"], g["de"])
hwc_hab = {}; hwc_match = {"by_name": 0, "by_position": 0, "unmatched": 0, "total_habitable_rows": 0}
for r in hwc:
    if r.get("P_HABITABLE") not in ("1", "2"): continue
    hwc_match["total_habitable_rows"] += 1
    gid = pl2host.get(r["P_NAME"], "")
    how = "by_name" if gid in idx else None
    if how is None:
        try:
            v = unit(float(r["S_RA"]), float(r["S_DEC"])); j = int((U @ v).argmax()); sep = np.degrees(np.arccos(min(1.0, float(U[j] @ v)))) * 3600
            if sep <= 5.0: gid = ids[j]; how = "by_position"
        except (ValueError, KeyError): pass
    if how is None: hwc_match["unmatched"] += 1; continue
    hwc_match[how] += 1
    hwc_hab.setdefault(gid, []).append({"planet": r["P_NAME"], "class": "conservative" if r["P_HABITABLE"] == "1" else "optimistic", "ESI": r.get("P_ESI")})

# ------------------------------------------------------------ 交差表示(計数のみ)
def cross(layer, band_v, status_key, lam_key, post_key):
    """EMBARK 層の (帯, 寿命[, 予算]) セルごとに、到達星のうち空き度 ε 確定星の数と Λ の要約。"""
    bits = lay[layer]; nb = bits.shape[1]
    if nb == 30: labels = [(b, l) for b in bands_e for l in Ls_e]
    else: labels = [(dv, b, l) for dv in dv_e for b in bands_e for l in Ls_e]
    st = np.array(S[status_key]); lam = np.array(S[lam_key]); post = np.array(S[post_key])
    out = []
    for c, lab in enumerate(labels):
        reach_k = np.where(joined)[0][bits[join[joined], c]]
        n_reach = len(reach_k); okk = reach_k[st[reach_k] == "ok"]
        rec = {"cell": lab, "n_reachable_in_gcns": int(n_reach), "n_with_vacancy_bound": int(len(okk)),
               "n_reachable_vacancy_undecidable": int(n_reach - len(okk))}
        if len(okk):
            rec["lambda_min_med_max"] = [float(lam[okk].min()), float(np.median(lam[okk])), float(lam[okk].max())]
            rec["posterior_pi0.01_med"] = float(np.median(post[okk]))
            rec["star_ids_with_bound"] = [ids[k] for k in okk[:50]]
        if n_reach: out.append(rec)
    return out
cond = {"vacancy": "空き度上界は T 帯(T-R1: EIRP≥1e13 W / T-R2: ≥1e17 W / T-R3: 地球級レーダー型間欠)の設備に関して、サーベイ集合 S = {WS20 (GBT L, GBT S, Parkes 10-cm)} のもとでの条件付き量。π の関数(代表 π=1e-2 を表示)。測量であって証明ではない",
        "reachability": "EMBARK v1(会合 flyby / 同行 rendezvous、帯 T1–T4、稼働寿命 L、t_dep 任意、クリーングラフ安定到達)。カタログ 37,498 星の内部に限る",
        "forbidden": "三軸の積・加重和・単一スコア化は行わない。交差は計数表示のみ"}
crosses = {}
for band_v in ("R1", "R2", "R3"):
    crosses[band_v] = {"flyby_single_any_tdep": cross("flyby_single_any_tdep", band_v, f"status_{band_v}", f"lambda_{band_v}", f"post_{band_v}_pi0.01"),
                       "rendezvous_single_any_tdep": cross("rendezvous_single_any_tdep", band_v, f"status_{band_v}", f"lambda_{band_v}", f"post_{band_v}_pi0.01")}

# ------------------------------------------------------------ 判定不能会計(三軸)
undec = {
  "vacancy_radio_not_in_field": int(np.mean(np.array(S["status_R1"]) == "undecidable_not_in_field") * NK), "vacancy_radio_rate": float(np.mean(np.array(S["status_R1"]) == "undecidable_not_in_field")),
  "vacancy_W1": "拡張区画(情報レイヤ、claim=false、裁定 #4)— v1 では空き度を主張しない",
  "reachability_not_in_embark": int((~joined).sum()), "reachability_rate": float((~joined).mean()),
  "reachability_sigma_pos_undecidable_any_cell": int(any_flag["sigma_pos_undecidable_t0"].sum()),
  "settlement_no_color": int((~np.isfinite(bp_rp)).sum()) + (NK - N), "settlement_note": "missing 表 1,259 星は測光なし → 定住資源性 判定不能(S3 のみ該当可)",
}
# ------------------------------------------------------------ 出力
stars = {
  "id": ids, "basis": S["basis"], "d50_pc": S["d50_pc"],
  "vacancy": {b: {"status": S[f"status_{b}"], "lambda": S[f"lambda_{b}"], "post_pi0.001": S[f"post_{b}_pi0.001"], "post_pi0.01": S[f"post_{b}_pi0.01"], "post_pi0.1": S[f"post_{b}_pi0.1"],
                  "low_confidence": S[f"low_confidence_{b}"], "claim": True} for b in ("R1", "R2", "R3")},
  "vacancy_information_layer_W1": {"claim": False, "note": "アンカー未確立(G3(ii) 不合格、裁定 #4)。交差表示の条件節に用いない",
                                   "status": S["status_W1"], "lambda_g0.1": S["lambda_W1_g0.1"], "lambda_g0.5": S["lambda_W1_g0.5"], "lambda_g0.9": S["lambda_W1_g0.9"]},
  "reachability": {"status": reach_status.tolist(), "embark_index": join.tolist(),
                   "any_flyby_single_any_tdep": any_flag["flyby_single_any_tdep"].tolist(), "any_rendezvous_single_any_tdep": any_flag["rendezvous_single_any_tdep"].tolist(),
                   "any_rendezvous_multi_any_tdep": any_flag["rendezvous_multi_any_tdep"].tolist(), "any_intake_dr4": any_flag["intake_dr4_any_tdep"].tolist(),
                   "any_sigma_pos_undecidable_t0": any_flag["sigma_pos_undecidable_t0"].tolist(),
                   "bits": reach, "bit_order": {k: es["layers"][k]["bit_order"] for k in reach}, "axes": emb["axes"]},
  "settlement": {"M_G": np.round(np.concatenate([MG, np.full(NK - N, np.nan)]), 3).tolist(), "bp_rp": np.round(np.concatenate([bp_rp, np.full(NK - N, np.nan)]), 3).tolist(),
                 "wd_prob": np.round(np.concatenate([wd, np.full(NK - N, np.nan)]), 3).tolist(), "main_sequence": ms.tolist() + [None] * (NK - N),
                 "spt_mamajek": spt + [None] * (NK - N),
                 "slider": {"S1_narrow_FGK_MS": S1.tolist() + [False] * (NK - N), "S2_all_MS": S2.tolist() + [False] * (NK - N), "S3_resource_all_stars": [True] * NK},
                 "known_planets_nea": [planets.get(s) for s in ids], "hwc_habitable": [hwc_hab.get(s) for s in ids]},
}
summary = {
  "generated": datetime.datetime.now().isoformat(timespec="seconds"), "constitution": "CLAUDE.md v0.3 / 裁定 #1–#4 / 事前登録 (b) 10.5281/zenodo.22067884",
  "population": {"total": NK, "gcns": N, "missing": NK - N},
  "join_embark": {"embark_stars": n_e, "embark_in_gcns": emb_in_gcns, "gcns_joined": int(joined.sum()), "gcns_join_rate": float(joined.mean()),
                  "embark_outside_population": n_e - emb_in_gcns, "note": "EMBARK 37,498 星のうち GCNS(≤100 pc)内在 14,799 を再確認(Phase 0.5 と一致)"},
  "reachability_any_counts": {k: int(v.sum()) for k, v in any_flag.items()},
  "settlement": {"S1_narrow_FGK_MS": int(S1.sum()), "S2_all_MS": int(S2.sum()), "S3_all": NK, "spt_letters": {k: int(v) for k, v in zip(*np.unique(letter[letter != ""], return_counts=True))},
                 "nea_hosts_lt120pc": n_nea_hosts, "nea_hosts_with_dr3_id": n_nea_with_dr3, "nea_hosts_joined_gcns": len(planets), "nea_planets_joined": int(sum(len(v) for v in planets.values())),
                 "hwc": hwc_match, "hwc_hosts_joined": len(hwc_hab)},
  "undecidable": undec, "conditions": cond,
  "cross_examples": {},
  "provenance": {"lambda_ledger_sha256": sha(os.path.join(P2, "lambda_ledger.json")), "embark_atlas_sha256": sha(EMB), "gcns_core_sha256": sha(os.path.join(P0, "gcns_core.npz")),
                 "nea_csv_sha256": sha(os.path.join(RAW4, "nea_pscomppars_lt120pc.csv")), "hwc_csv_sha256": sha(os.path.join(RAW4, "hwc.csv")), "mamajek_sha256": sha(os.path.join(P1, "EEM_dwarf_colors_Teff.txt"))},
}
# 交差集計例
stR1 = np.array(S["status_R1"]) == "ok"
for layer in ("flyby_single_any_tdep", "rendezvous_single_any_tdep", "rendezvous_multi_any_tdep"):
    a = any_flag[layer]
    summary["cross_examples"][layer] = {"reachable_any_cell": int(a.sum()), "reachable_and_R1_bound": int((a & stR1).sum()),
                                        "reachable_and_R1_undecidable": int((a & ~stR1).sum()),
                                        "reachable_and_R3_bound": int((a & (np.array(S["status_R3"]) == "ok")).sum())}
summary["cross_examples"]["R1_bound_and_not_in_embark"] = int((stR1 & ~joined).sum())
summary["cross_examples"]["R1_bound_and_in_embark_but_unreachable_all_cells"] = int((stR1 & joined & ~any_flag["flyby_single_any_tdep"]).sum())
atlas = {"schema": "vacancy-atlas-v1", "disclaimer": L["disclaimer"], "not_a_permit": "空き度は入植許可証ではない。本成果物から占有の不在・入植の正当性を推論してはならない(第1条4項)",
         "bands": L["bands"], "conditions": cond, "cross_tables": crosses, "summary": summary, "stars": stars}
json.dump(atlas, open(os.path.join(P4, "atlas_v1.json"), "w"), ensure_ascii=False)
json.dump(summary | {"cross_tables_R1_flyby_nonempty_cells": len(crosses["R1"]["flyby_single_any_tdep"])}, open(os.path.join(P4, "atlas_v1_summary.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))
