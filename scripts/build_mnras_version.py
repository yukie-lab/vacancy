#!/usr/bin/env python3
"""裁定 #7: MNRAS 版(英語)を md 版から機械生成する。
 - 参考文献を author-year(アルファベット順・番号なし)に変換
 - §7 Interpretation discipline と §8 Limitations を「7. Discussion」に統合(md 版は現状維持)
数値・本文は一切変更しない(構成と文献体裁のみ)。出力: docs/phase5/paper/vacancy_en_mnras.md"""
import os, re
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "phase5", "paper")
s = open(os.path.join(P, "vacancy_en.md")).read()
# --- §7 統合は裁定 #8 で md 版に反映済み(本スクリプトでは参考文献の author-year 化のみ)
# --- 参考文献 author-year
a = s.index("## References")
refs_block = s[a:]
entries = [re.sub(r"^\[\d+\]\s+", "", l).strip().rstrip(".") for l in refs_block.splitlines()[1:] if re.match(r"^\[\d+\]\s", l)]
entries = sorted(set(e for e in entries if e), key=lambda x: x.lower())
refs = "## References\n\n" + "\n".join(f"- {e}." for e in entries) + "\n"
s = s[:a] + refs
s = s.replace("# A Vacancy Atlas of the Solar Neighbourhood", "# A Vacancy Atlas of the Solar Neighbourhood", 1)
s = "<!-- MNRAS 版: scripts/build_mnras_version.py で md 版から機械生成(裁定 #7)。本文・数値は md 版と同一。 -->\n" + s
open(os.path.join(P, "vacancy_en_mnras.md"), "w").write(s)
print("mnras version written;", len(entries), "reference entries")
