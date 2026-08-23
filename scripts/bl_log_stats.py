#!/usr/bin/env python3
"""Phase 0.1(c): BL 公開アーカイブ観測ログの欄充足率を集計し、01 実査文書の §4 追記欄を更新する。"""
import json, glob, collections, os, re, datetime
HERE = os.path.dirname(__file__)
RAW = os.path.join(HERE, "..", "data", "raw", "bl_opendata")
DOC = os.path.join(HERE, "..", "docs", "phase0", "01-machine-readability-survey.md")
OUT = os.path.join(HERE, "..", "data", "phase0", "bl_log_stats.json")

def band(tel, f):
    if tel == "GBT":
        if 1100 <= f <= 1900: return "GBT L(名目)"
        if 1900 < f <= 2800: return "GBT S(名目)"
        if 4000 <= f <= 7800: return "GBT C"
        if 7800 < f <= 12300: return "GBT X"
        return "GBT その他サブバンド"
    if tel == "Parkes":
        if 2600 <= f <= 3450: return "Parkes 10-cm(名目)"
        return "Parkes その他サブバンド"
    return tel

files = sorted(glob.glob(os.path.join(RAW, "*.json")))
hip = [f for f in files if re.match(r"HIP\d+\.json$", os.path.basename(f))]
st = collections.Counter(); bands = collections.Counter(); tel = collections.Counter(); years = collections.Counter()
n_files = 0
for fn in hip:
    d = json.load(open(fn))["data"]
    if not d:
        st["no_files"] += 1; continue
    st["has_files"] += 1
    st["has_mjd"] += all(x.get("mjd") is not None for x in d)
    st["has_freq"] += all(x.get("center_freq") is not None for x in d)
    st["has_radec"] += all(x.get("ra") is not None and x.get("decl") is not None for x in d)
    bs = set()
    for x in d:
        n_files += 1
        if x["file_type"] in ("HDF5", "filterbank"):
            tel[x["telescope"]] += 1; bs.add(band(x["telescope"], x["center_freq"]))
            m = re.search(r"\b(\d{4})\b", str(x["utc"])); years[m.group(1) if m else "?"] += 1
    for b in bs: bands[b] += 1
failed = open(os.path.join(RAW, "_failed.txt")).read().strip().splitlines() if os.path.exists(os.path.join(RAW, "_failed.txt")) else []
res = {"generated": datetime.date.today().isoformat(), "n_hip_targets_fetched": len(hip), "n_files_total": n_files, "status": dict(st),
       "targets_by_nominal_band": dict(bands), "files_by_telescope": dict(tel), "files_by_year": dict(sorted(years.items())), "n_failed": len(failed)}
json.dump(res, open(OUT, "w"), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))

sec = ["## 4. 追記欄(BL 全目標取得完了後に更新)",
       f"- 更新 {res['generated']}: HIP 目標 {len(hip)} 件取得(失敗 {len(failed)})、観測ファイル {n_files:,} 件。",
       f"- 欄充足率: 観測ファイルあり {st['has_files']}/{len(hip)}、MJD {st['has_mjd']}/{st['has_files']}、中心周波数 {st['has_freq']}/{st['has_files']}、座標 {st['has_radec']}/{st['has_files']}。",
       "- 名目帯ごとの目標数(ファイル中心周波数による暫定帰属): " + ", ".join(f"{k} {v}" for k, v in sorted(bands.items())) + "。",
       "- 年別ファイル数: " + ", ".join(f"{k}: {v}" for k, v in sorted(years.items())) + "。",
       "- 再現: `python3 scripts/bl_log_stats.py`(集計 JSON: `data/phase0/bl_log_stats.json`)。", ""]
txt = open(DOC).read()
txt = re.sub(r"## 4\. 追記欄.*\Z", "\n".join(sec), txt, flags=re.S)
open(DOC, "w").write(txt)
print("doc updated")
