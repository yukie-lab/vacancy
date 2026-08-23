#!/usr/bin/env python3
"""論文 md の機械ゲート(Phase 5.1)。
1. 日英の数値トークン集合が一致(転記漏れ・片側修正の検出)
2. numbers.json の主要値が日英本文に現れる(転記元との一致)
3. 必須文(四文+禁止語)の検査: 四文の存在、「部分アンカー / partial anchor」等の合格示唆語の不在
4. 凍結値の逐語: 事前登録 DOI、(a) コミット、凍結 sha256 先頭
"""
import os, re, json, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."); P = os.path.join(ROOT, "docs", "phase5", "paper")
ja = open(os.path.join(P, "vacancy_ja.md")).read(); en = open(os.path.join(P, "vacancy_en.md")).read()
N = json.load(open(os.path.join(P, "numbers.json")))
def norm(t):
    t = re.sub(r"SHA-256|sha256|§ ?9\.3|Art\. 9\.3|第9条3項", " ", t)
    t = t.replace("−", "-").replace("×", "x").replace("⁻", "^-")
    for a, b in zip("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789"): t = t.replace(a, b)
    return t
tok = re.compile(r"(?<![A-Za-z_/])\d[\d,]*(?:\.\d+)?(?:\s?(?:x|×)\s?10\^?[-−]?\d+|e[-−]?\d+)?(?![A-Za-z_])")
def nums(t): return set(m.group(0).replace(" ", "").replace(",", "") for m in tok.finditer(norm(t)))
sj, se = nums(ja), nums(en)
fails = []
only_ja = sorted(sj - se); only_en = sorted(se - sj)
# 引用番号・章番号などは両方にあるはず。差分を報告
if only_ja or only_en:
    fails.append(f"数値トークン不一致: JAのみ {only_ja[:30]} / ENのみ {only_en[:30]}")
# numbers.json 主要値
def fmts(v):
    if isinstance(v, int): return {f"{v:,}", str(v)}
    return {str(v)}
keys = ["pop_total", "ok_R1", "ok_R2", "ok_R3", "undec_radio", "g1_checks", "ws20_rows", "ws20_stars", "cross_flyby_R1", "cross_flyby_R3", "cross_rdv_R1",
        "embark_in_gcns", "nea_hosts", "hwc_hosts", "w1_candidate", "w1_ok", "S1_narrow_FGK_MS", "S2_all_MS", "bl_unpublished_gcns", "bl_files", "bl_hip"]
for k in keys:
    vs = fmts(N[k]["value"])
    for name, txt in (("JA", ja), ("EN", en)):
        if not any(v in txt for v in vs): fails.append(f"numbers.json {k}={vs} が {name} に無い")
for v in ["0.4266", "0.8596", "0.0080", "0.999085", "0.99479", "0.0851", "99.52", "95.55", "2.48", "4.45", "6,777", "4.9 × 10⁻¹⁰", "5.2 × 10⁻⁷", "3.13", "0.82", "0.17", "0.30", "1513", "1671", "2576", "0.0598", "0.0388", "0.0661"]:
    for name, txt in (("JA", ja), ("EN", en)):
        if v not in txt: fails.append(f"固定値 {v} が {name} に無い")
# 四文
req_ja = ["測量であって証明ではない", "入植許可証ではない", "合成ではない", "別量"]
req_en = ["survey, not a proof", "not a settlement permit", "not a composition", "different quantities"]
for r in req_ja:
    if r not in ja: fails.append(f"必須文 JA: {r}")
for r in req_en:
    if r not in en: fails.append(f"必須文 EN: {r}")
for bad in ["部分アンカー", "partial anchor", "partially pass", "部分合格", "W1 合格", "ランキング"]:
    if bad in ja or bad.lower() in en.lower(): fails.append(f"禁止語: {bad}")
for v in ["10.5281/zenodo.22067884", "10a01e71", "88eb7809"]:
    for name, txt in (("JA", ja), ("EN", en)):
        if v not in txt: fails.append(f"凍結値 {v} が {name} に無い")
print("JA tokens", len(sj), "EN tokens", len(se))
print("PASS" if not fails else "FAIL"); [print(" -", f) for f in fails]
sys.exit(1 if fails else 0)
