#!/usr/bin/env python3
"""裁定 #12 手順 F'-1: md 正本(docs/phase5/paper/vacancy_en.md)から A&A 投稿版を機械生成。
原則 = mnras 版と同一: 内容同一・体裁のみ変換・md 正本が唯一の編集対象。
 - aa.cls v9.4(2025/11/27, sha256 79bc49e0…)+ aa.bst(natbib author-year)
 - 要旨を A&A 構造化形式(Context/Aims/Methods/Results、Conclusions 空)に再編:
   文の並べ替えのみ。全 12 文の全数使用を機械検査(欠落・追加があれば FAIL)。
   唯一の接続修正 = Context 文の指示語解決(下記 EDITS)。対応表を自動生成。
 - 参考文献 31 項目を BibTeX 化(vacancy_refs.bib)、\\bibliographystyle{aa}
 - 本文引用は md 正本の名前・年表記を逐語保持(数値トークン保存のため \\citep 化しない)
 - 付録 A–D は A&A 慣行どおり参考文献の後(\\appendix)
 - 図 4 点は PDF 版(fig3 のみ全幅 figure*)。キャプションの「Figure N: 」接頭辞は
   自動番号と重複するため除去(体裁変換、対応表に記録)
 - 要旨脚注 [^pop] は A&A 要旨の脚注禁止に伴い、本文初出の「332,571 stars」に移設
出力: docs/phase5/submission_aa/{vacancy_aa.tex,pdf, vacancy_refs.bib, abstract_mapping.md}
実行: cd ~/Desktop/test/vacancy && python3 scripts/build_aa_version.py
"""
import re, shutil, subprocess, sys
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
PDIR = ROOT / "docs/phase5/paper"
ADIR = ROOT / "docs/phase5/submission_aa"
spec = importlib.util.spec_from_file_location("bpp", ROOT / "scripts/build_paper_pdf.py")
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)

# ---------- 構造化要旨(文リテラルは md から逐語。EDITS のみ許可された接続修正) ----------
S = [
 'For each star in the solar neighbourhood we aggregate conditional non-detections ("facilities of band T at this star would have been detected by survey set S") into a star-by-star, band-conditional upper bound on occupation, P(occupied | D, T, π), as a function of the prior π.',
 'To our knowledge no star-level ledger of this quantity exists.',
 'The population is 332,571 stars within 100 pc (Gaia EDR3 GCNS basis)[^pop].',
 'The claimed bands are three radio bands (T-R1: EIRP ≥ 10¹³ W; T-R2: ≥ 10¹⁷ W; T-R3: Earth-level radar-type intermittent leakage) within [1.10, 3.45] GHz.',
 'Detection probabilities are imported from the 356,616 observation rows of Wlodarczyk-Sroka et al. (2020); observations within one modality are merged by marginalising shared latent variables, and we prove that the naive likelihood product tilts toward "vacancy".',
 'Thresholds and pass criteria were pre-registered before aggregation (doi:10.5281/zenodo.22067884).',
 'Verification: G1 monotonicity, 6,777 checks, 0 violations; G2 independent implementations agree to 4.9 × 10⁻¹⁰ dex; G3: the WS20 1/N limit is reproduced exactly at ≤50 pc (N = 1513), the Hephaistos I count fails (the waste-heat band is demoted), and the Solar-System self-test passes.',
 'Stars with a bound number 1,554 (T-R1), 1,587 (T-R2) and 159 (T-R3); 330,984 stars (99.52%) are undecidable — a main result.',
 'In T-R3 posterior ≈ prior (Λ ≥ 0.998): the lowest band the atlas can speak about is calibrated by Earth itself.',
 'Joined with reachability and settlement resources, 815 stars are flyby-reachable with a T-R1 bound.',
 'At the Gaia DR4 release (2026-12-02) only the distance-dependent part of the ledger is recomputed (v1.1).',
 'These bounds are survey quantities, not proofs of absence, and license no inference about settlement (§7.1).',
]
# 割当(0 始まり index)
ASSIGN = {"Context": [1], "Aims": [0], "Methods": [2, 3, 4, 5], "Results": [6, 7, 8, 9, 10, 11]}
# 許可された接続修正(裁定 #12「最小限の接続修正」): 指示語の解決のみ。数値・主張の変更なし。
EDITS = {1: ('this quantity', 'the star-by-star, band-conditional upper bound on occupation')}


def build_abstract(md_abs):
    # 全数使用検査: 12 文を順に取り除くと空白のみが残ること
    rest = md_abs
    for k, s in enumerate(S):
        if s not in rest:
            sys.exit(f"要旨文 {k+1} が md に逐語一致しない: {s[:60]}…")
        rest = rest.replace(s, "", 1)
    if rest.strip():
        sys.exit(f"要旨に未割当のテキストが残存: {rest.strip()[:120]!r}")
    paras, mapping = {}, []
    for head, idxs in ASSIGN.items():
        parts = []
        for k in idxs:
            t = S[k]
            note = "逐語"
            if k in EDITS:
                a, b = EDITS[k]
                t = t.replace(a, b, 1)
                note = f"接続修正: 「{a}」→「{b}」(指示語解決)"
            if k == 2:
                t = t.replace("[^pop]", "")     # A&A 要旨は脚注不可 → 本文へ移設
                note += " / 脚注 [^pop] は除去(A&A 要旨は脚注不可。同一脚注が本文 §3.1 に既出のため情報欠落なし)"
            parts.append(t)
            mapping.append((k + 1, head, note))
        paras[head] = " ".join(parts)
    return paras, mapping


# ---------- BibTeX(31 項目) ----------
def make_bib(ref_lines):
    ents = []
    CORP = {27: ("{NASA Exoplanet Archive}", "Planetary Systems Composite Parameters, doi:10.26133/NEA12 (retrieved 2026-08-23)", "2026"),
            28: ("{Habitable Worlds Catalog (PHL @ UPR Arecibo)}", "Habitable Worlds Catalog (retrieved 2026-08-23)", "2026")}
    for ln in ref_lines:
        m = re.match(r"\[(\d+)\]\s+(.*?)\.\s*$", ln)
        if not m:
            continue
        n, body = int(m.group(1)), m.group(2)
        key = f"r{n:02d}"
        if n in CORP:
            au, how, yr = CORP[n]
            dm = re.search(r"doi:(10\.\S+?)(?:\s|$)", body)
            doi = f",\n  doi = {{{dm.group(1).rstrip('.,)')}}}" if dm else ""
            ents.append(f"@MISC{{{key},\n  author = {{{au}}},\n  year = {{{yr}}},\n  howpublished = {{{how.replace('&', chr(92)+'&')}}}{doi}\n}}")
            continue
        ym = re.search(r"\b((?:19|20)\d\d[abc]?)\b", body)
        year = ym.group(1) if ym else ""
        pre, post = body[:ym.start()].rstrip(" ,"), body[ym.end():].lstrip(" ,") if ym else ("", body)
        def authors_bib(a):
            a = a.replace("Gaia Collaboration", "{Gaia Collaboration}")
            parts = [p.strip() for p in a.split(",") if p.strip()]
            out = []
            for p in parts:
                if p == "et al.":
                    out.append("others"); continue
                p = re.sub(r"\s+et al\.$", "", p)
                w = p.split()
                if p.startswith("{"):
                    out.append(p)
                elif len(w) >= 2 and all(len(x.rstrip(".")) <= 2 for x in w[-1:]):
                    out.append(" ".join(w))
                else:
                    out.append(" ".join(w))
                if "et al." in p:
                    out.append("others")
            s = " and ".join(out)
            if a.rstrip().endswith("et al.") and not s.endswith("others"):
                s += " and others"
            return s
        # 姓+イニシャル形式 "Price D. C. et al." → "Price, D. C. and others"
        def authors_std(a):
            a = re.sub(r"\s+", " ", a).strip().rstrip(",")
            chunks = [c.strip() for c in a.split(",")]
            names = []
            for c in chunks:
                if not c:
                    continue
                if c == "et al.":
                    names.append("others"); continue
                trail_etal = c.endswith("et al.")
                c2 = re.sub(r"\s*et al\.$", "", c)
                if c2 == "Gaia Collaboration":
                    names.append("{Gaia Collaboration}")
                else:
                    w = c2.split()
                    if len(w) >= 2:
                        names.append(w[0] + ", " + " ".join(w[1:]))
                    else:
                        names.append(c2)
                if trail_etal:
                    names.append("others")
            return " and ".join(names)
        au = authors_std(pre) if pre else ""
        jm = re.match(r"([A-Za-z&.\s]+?)\s+(\d+[A-Za-z]?),\s*([A-Za-z]?\d+)$", post)
        esc = lambda s: s.replace("&", r"\&")
        if jm:
            ents.append(f"@ARTICLE{{{key},\n  author = {{{au}}},\n  year = {{{year.rstrip('abc')}}},\n"
                        f"  journal = {{{esc(jm.group(1).strip())}}},\n  volume = {{{jm.group(2)}}},\n  pages = {{{jm.group(3)}}}\n}}")
        else:
            note = esc(post) if post else esc(body)
            title = ""
            dm = re.search(r"doi:(10\.\S+?)(?:\s|$)", body)
            doi = f",\n  doi = {{{dm.group(1).rstrip('.,')}}}" if dm else ""
            ents.append(f"@MISC{{{key},\n  author = {{{au if au else esc(pre or body.split(',')[0])}}},\n  year = {{{year.rstrip('abc')}}},\n"
                        f"  howpublished = {{{note}}}{doi}\n}}")
    return "\n\n".join(ents) + "\n"


# ---------- 本文変換 ----------
def convert():
    raw = (PDIR / "vacancy_en.md").read_text()
    B.check_symbols(raw)
    fdefs = dict(re.findall(r"^\[\^(\w+)\]: (.*)$", raw, flags=re.M))
    raw = re.sub(r"^\[\^(\w+)\]: .*\n?", "", raw, flags=re.M)
    lines = raw.splitlines()
    title = B.tex_inline(lines[0].lstrip("# "), True)
    footmeta = next(l for l in lines[1:8] if l.startswith("Footnote:"))
    # 要旨
    ai = lines.index("## Abstract")
    bi = next(k for k in range(ai + 1, len(lines)) if lines[k].startswith("## "))
    md_abs = " ".join(l for l in lines[ai + 1:bi] if l.strip())
    paras, mapping = build_abstract(md_abs)
    # 参考文献
    ri = lines.index("## References")
    ref_lines = [l for l in lines[ri + 1:] if re.match(r"^\[\d+\]\s", l)]
    assert len(ref_lines) == 31, f"参考文献 {len(ref_lines)} ≠ 31"
    bib = make_bib(ref_lines)

    def inline_full(s):
        s = re.sub(r"\[\^(\w+)\]", lambda m: "\x00F" + m.group(1) + "\x00", s)
        out = B.tex_inline(s, True)
        return re.sub("\x00F(\\w+)\x00", lambda m: r"\footnote{" + B.tex_inline(fdefs.get(m.group(1), ""), True) + "}", out)

    body, appendix, ack = [], [], []
    target = body
    in_items = [False]

    def close_items():
        if in_items[0]:
            target.append(r"\end{itemize}")
            in_items[0] = False

    L = lines[bi:ri]
    # 脚注 [^pop] は本文 §3.1 に既出(md で 2 回参照)→ 要旨からの除去のみで情報欠落なし
    assert any("[^pop]" in ln for ln in L), "[^pop] が本文に無い(要旨からの除去で情報が失われる)"
    i = 0
    while i < len(L):
        ln = L[i]
        if ln.startswith("## Acknowledgements"):
            target = ack; in_items[0] = False
        elif ln.startswith("## Appendix"):
            target = appendix; in_items[0] = False
            h = re.sub(r"^Appendix [A-D]\s*—\s*", "", ln[3:])
            target.append(r"\section{" + inline_full(h) + "}")
        elif ln.startswith("### "):
            close_items()
            h = re.sub(r"^\d+\.\d+\s+", "", ln[4:])
            target.append(r"\subsection{" + inline_full(h) + "}")
        elif ln.startswith("## "):
            close_items()
            h = re.sub(r"^\d+\.\s+", "", ln[3:])
            target.append(r"\section{" + inline_full(h) + "}")
        elif ln.startswith("[FIG] "):
            close_items()
            path, cap = ln[6:].split(" | ", 1)
            cap = re.sub(r"^Figure \d+:\s*", "", cap)
            cap = cap[:1].upper() + cap[1:]   # 接頭辞除去後の先頭を大文字化(体裁変換、対応表に記録)
            pdf = path.replace(".png", ".pdf")
            env = "figure*" if "fig3" in path else "figure"
            wid = r"\textwidth" if env == "figure*" else r"\hsize"
            target.append(rf"\begin{{{env}}}\centering")
            target.append(rf"\includegraphics[width={wid}]{{{pdf}}}")
            target.append(r"\caption{" + inline_full(cap) + "}")
            target.append(rf"\end{{{env}}}")
        elif ln.startswith("> "):
            close_items()
            target.append(r"\begin{quote}\textbf{" + inline_full(ln[2:].strip()) + r"}\end{quote}")
        elif ln.startswith("```"):
            close_items()
            target.append(r"\begin{quote}\small")
            i += 1
            while i < len(L) and not L[i].startswith("```"):
                target.append(B.code_tex(L[i].rstrip()) + r"\\*" if L[i].strip() else r"\smallskip")
                i += 1
            target.append(r"\end{quote}")
        elif ln.startswith("|"):
            close_items()
            rows = []
            while i < len(L) and L[i].startswith("|"):
                rows.append(L[i]); i += 1
            i -= 1
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows if not set(r.replace("|", "").strip()) <= set("-: ")]
            ncol = max(len(r) for r in cells)
            widths = [max((len(r[j]) if j < len(r) else 0) for r in cells) for j in range(ncol)]
            wide = sum(widths) > 42
            if wide:
                tot = sum(max(w, 4) for w in widths)
                colspec = "".join(">{\\raggedright\\arraybackslash}p{%.3f\\textwidth}" % (0.94 * max(w, 4) / tot) for w in widths)
                target.append(r"\begin{table*}\centering{\scriptsize\setlength{\tabcolsep}{2.5pt}")
                target.append(r"\begin{tabular}{" + colspec + "}")
            else:
                target.append(r"{\footnotesize\setlength{\tabcolsep}{3pt}\begin{center}\begin{tabular}{" + "l" * ncol + "}")
            for k, r in enumerate(cells):
                target.append(" & ".join(inline_full(c) for c in r) + r" \\")
                if k == 0:
                    target.append(r"\hline")
            target.append(r"\end{tabular}}\end{table*}" if wide else r"\end{tabular}\end{center}}")
        elif ln.startswith("- "):
            if not in_items[0]:
                target.append(r"\begin{itemize}\setlength{\itemsep}{1pt}"); in_items[0] = True
            target.append(r"\item " + inline_full(ln[2:]))
        elif not ln.strip():
            close_items(); target.append("")
        else:
            close_items(); target.append(r"\noindent " + inline_full(ln) + r"\par\smallskip")
        i += 1
    close_items()

    dataav = ("All data, code, and the pre-registration are openly available at Zenodo: "
              r"\url{doi:10.5281/zenodo.22081202} (data and code) and \url{doi:10.5281/zenodo.22067884} (pre-registration). "
              r"An interactive simulator is available at \url{https://yukie-lab.github.io/vacancy-atlas/}.")
    abs_tex = lambda t: re.sub(r"\\url\{([^}]*)\}", r"\1", B.tex_inline(t, True))   # 要旨(moving arg)では \url 不可 → 素のテキスト
    tex = "\n".join([
        r"\documentclass{aa}",
        r"\usepackage{graphicx}", r"% \usepackage{txfonts}  % A&A 推奨。tectonic のフォントバンドルが t1xsl を配信せず(403)ローカルでは無効化。MMS 側コンパイルでは有効化可", r"\usepackage{array}", r"\usepackage{url}",
        r"\graphicspath{{figs/}}",
        r"\begin{document}",
        r"\title{" + title + "}",
        r"\titlerunning{A vacancy atlas of the solar neighbourhood}",
        r"\authorrunning{Y. Maeda}",
        r"\author{Yukie Maeda\thanks{" + B.tex_inline(footmeta.split(":", 1)[1].strip(), True) + "}}",
        r"\institute{Independent Researcher, Tokyo (ORCID: 0009-0005-3401-9230)}",
        r"\date{Received --; accepted --}",
        r"\abstract{" + abs_tex(paras["Context"]) + "}{" + abs_tex(paras["Aims"]) + "}{"
            + abs_tex(paras["Methods"]) + "}{" + abs_tex(paras["Results"]) + "}{}",
        r"\keywords{extraterrestrial intelligence -- astrobiology -- solar neighborhood -- catalogs -- surveys -- methods: statistical}",
        r"\maketitle",
        "\n".join(body),
        r"\section*{Data availability}", dataav,
        r"\begin{acknowledgements}", "\n".join(ack).strip(), r"\end{acknowledgements}",
        r"\nocite{*}", r"\bibliographystyle{aa}", r"\bibliography{vacancy_refs}",
        r"\appendix",
        "\n".join(appendix),
        r"\end{document}", ""])
    return tex, bib, mapping


def main():
    ADIR.mkdir(exist_ok=True)
    (ADIR / "figs").mkdir(exist_ok=True)
    for f in (PDIR / "figs").glob("fig*.pdf"):
        shutil.copy2(f, ADIR / "figs" / f.name)
    for f in ("aa.cls", "aa.bst", "linenoaa.sty", "lineno.sty"):
        shutil.copy2(ADIR / "aa-macro" / f, ADIR / f)
    tex, bib, mapping = convert()
    (ADIR / "vacancy_aa.tex").write_text(tex)
    (ADIR / "vacancy_refs.bib").write_text(bib)
    rows = ["# 構造化要旨 変換対応表(機械生成: scripts/build_aa_version.py)", "",
            "md 正本の要旨 12 文の全数を A&A 構造化要旨に再割当(欠落・追加なしを機械検査)。", "",
            "| md 文番号 | A&A 段落 | 処置 |", "|---|---|---|"]
    rows += [f"| {n} | {h} | {note} |" for n, h, note in mapping]
    rows += ["", "その他の体裁変換: 図キャプションの「Figure N: 」接頭辞除去(自動番号と重複)+先頭 1 文字の大文字化 /",
             "前付の (Preprint, …) 行は投稿版に不掲載(データ DOI は Data availability 節に記載)/",
             "見出しの明示番号 → aa.cls 自動番号 / 付録 A–D は A&A 慣行により参考文献の後 /",
             "参考文献 31 項目 → BibTeX(vacancy_refs.bib、aa.bst author-year)。本文引用は md の名前・年表記を逐語保持。"]
    (ADIR / "abstract_mapping.md").write_text("\n".join(rows) + "\n")
    r = subprocess.run(["tectonic", "vacancy_aa.tex"], cwd=ADIR, capture_output=True, text=True)
    (ADIR / "vacancy_aa.buildlog").write_text(r.stdout + r.stderr)
    ok = r.returncode == 0 and (ADIR / "vacancy_aa.pdf").exists()
    print("aa version:", "OK" if ok else "FAIL", (ADIR / "vacancy_aa.pdf").stat().st_size if ok else "")
    sys.exit(0 if not r.returncode else 1)


if __name__ == "__main__":
    main()
