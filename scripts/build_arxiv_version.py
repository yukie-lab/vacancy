#!/usr/bin/env python3
"""裁定 #13-(4): md 正本(docs/phase5/paper/vacancy_en.md)から arXiv 投稿版を機械生成。
 - 標準 article クラス(build_paper_pdf の変換系をそのまま使用 — 内容同一原則)
 - 参考文献を author-year(アルファベット順・番号なし)に変換(build_mnras_version と同一変換)
 - 図 4 点は PDF 版を同梱(md の .png 参照を .pdf に置換 — 体裁変換)
 - 派生 md と md 正本の同一性を機械検査(差分 = 参考文献ブロックと図拡張子のみ、それ以外で FAIL)
 - pdflatex 互換のため \\ifdefined\\pdfoutput\\pdfoutput=1\\fi を付加(arXiv AutoTeX 対応)
出力: docs/phase5/submission_arxiv/{vacancy_arxiv.md,tex,pdf, figs/}
実行: cd ~/Desktop/test/vacancy && python3 scripts/build_arxiv_version.py
gate: scripts/gate_check_paper.py の arXiv 節が md 正本との数値トークン全数一致を検査
"""
import re, shutil, subprocess, sys
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
PDIR = ROOT / "docs/phase5/paper"
XDIR = ROOT / "docs/phase5/submission_arxiv"
spec = importlib.util.spec_from_file_location("bpp", ROOT / "scripts/build_paper_pdf.py")
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)


def derive_md(src):
    """参考文献 author-year 化(build_mnras_version.py と同一)+ [FIG] .png → .pdf。"""
    a = src.index("## References")
    refs_block = src[a:]
    entries = [re.sub(r"^\[\d+\]\s+", "", l).strip().rstrip(".") for l in refs_block.splitlines()[1:] if re.match(r"^\[\d+\]\s", l)]
    entries = sorted(set(e for e in entries if e), key=lambda x: x.lower())
    refs = "## References\n\n" + "\n".join(f"- {e}." for e in entries) + "\n"
    out = src[:a] + refs
    out = re.sub(r"^(\[FIG\] figs/fig\d[\w]*)\.png ", r"\1.pdf ", out, flags=re.M)
    return out, len(entries)


def check_identity(src, drv):
    """派生 md が md 正本と(参考文献ブロック・図拡張子を除き)同一であることの機械検査。"""
    cut = lambda t: re.sub(r"^(\[FIG\] figs/fig\d[\w]*)\.(?:png|pdf) ", r"\1 ", t[:t.index("## References")], flags=re.M)
    if cut(src) != cut(drv):
        sys.exit("派生 md が md 正本と一致しない(参考文献・図拡張子以外の差分)")


def main():
    XDIR.mkdir(exist_ok=True)
    (XDIR / "figs").mkdir(exist_ok=True)
    for f in (PDIR / "figs").glob("fig*.pdf"):
        shutil.copy2(f, XDIR / "figs" / f.name)
    src = (PDIR / "vacancy_en.md").read_text()
    drv, n_refs = derive_md(src)
    check_identity(src, drv)
    drv = "<!-- arXiv 版: scripts/build_arxiv_version.py で md 正本から機械生成(裁定 #13)。本文・数値は md 正本と同一(参考文献 author-year 化・図 PDF 参照のみ)。 -->\n" + drv
    (XDIR / "vacancy_arxiv.md").write_text(drv)
    tmp = XDIR / ".convert_tmp.md"                      # 変換は先頭コメント無し版で(convert は 1 行目を題と読む)
    tmp.write_text(drv.split("-->\n", 1)[1])
    tex = B.convert(tmp, en=True)
    tmp.unlink()
    tex = tex.replace("\\documentclass[11pt]{article}\n",
                      "\\documentclass[11pt]{article}\n\\ifdefined\\pdfoutput\\pdfoutput=1\\fi\n", 1)
    (XDIR / "vacancy_arxiv.tex").write_text(tex)
    r = subprocess.run(["tectonic", "vacancy_arxiv.tex"], cwd=XDIR, capture_output=True, text=True)
    (XDIR / "vacancy_arxiv.buildlog").write_text(r.stdout + r.stderr)
    ok = r.returncode == 0 and (XDIR / "vacancy_arxiv.pdf").exists()
    print(f"arXiv version: {'OK' if ok else 'FAIL'}", (XDIR / 'vacancy_arxiv.pdf').stat().st_size if ok else "", f"refs={n_refs}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
