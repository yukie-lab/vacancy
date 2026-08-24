#!/usr/bin/env python3
"""論文 PDF 生成(EMBARK 系譜 build_paper_pdf の VACANCY 適応。XeLaTeX/tectonic)。
md(凍結源)→ tex はプログラム変換(手写しゼロ)。VACANCY 拡張:
 - 前付: 1 行目 = 題、著者行(**…**)、括弧書き(プレプリント行)、「脚注:」行、冒頭引用(> …)= 表紙の凡例二文
 - 脚注 [^id] → \\footnote{定義}(定義行は本文から除去)
 - ``` ブロック → quote+texttt(行単位)
 - 記号写像は実使用文字の全数(scripts 実行時に未知記号があれば FAIL)
実行: cd ~/Desktop/test/vacancy && python3 scripts/build_paper_pdf.py
出力: docs/phase5/paper/vacancy_{ja,en}.tex / .pdf + .buildlog
"""
import re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PDIR = ROOT / "docs/phase5/paper"

SUPD = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-"}
SUBD = {"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4"}
SYM = {"±": r"\(\pm\)", "·": r"\(\cdot\)", "×": r"\(\times\)", "Δ": r"\(\Delta\)", "θ": r"\(\theta\)", "σ": r"\(\sigma\)",
       "→": r"\(\rightarrow\)", "−": r"\(-\)", "≈": r"\(\approx\)", "≤": r"\(\leq\)", "≥": r"\(\geq\)", "⊂": r"\(\subset\)",
       "Λ": r"\(\Lambda\)", "π": r"\(\pi\)", "ε": r"\(\varepsilon\)", "γ": r"\(\gamma\)", "ν": r"\(\nu\)", "Θ": r"\(\Theta\)",
       "Π": r"\(\Pi\)", "Σ": r"\(\Sigma\)", "∈": r"\(\in\)", "∧": r"\(\wedge\)", "≲": r"\(\lesssim\)", "≳": r"\(\gtrsim\)",
       "∪": r"\(\cup\)", "δ": r"\(\delta\)", "∎": r"\(\blacksquare\)", "≪": r"\(\ll\)", "µ": r"\(\mu\)", "Ĝ": r"\^{G}",
       "…": r"\ldots{}", "§": r"\S{}"}
KNOWN = set(SUPD) | set(SUBD) | set(SYM) | set("—–")
CODE_SPLIT, CODE_LONG = 32, 48


def check_symbols(text):
    bad = set()
    for ch in text:
        o = ord(ch)
        if o < 128 or 0x3000 <= o <= 0x30FF or 0x4E00 <= o <= 0x9FFF or 0xFF00 <= o <= 0xFFEF:
            continue
        if ch not in KNOWN:
            bad.add(ch)
    if bad:
        sys.exit(f"未知記号(写像未定義): {sorted(bad)}")


def tex_text(s, en=False):
    urls = []
    def stash(m):
        urls.append(m.group(0).rstrip(")、。"))
        return f"\x00U{len(urls)-1}\x00" + m.group(0)[len(urls[-1]):]
    s = re.sub(r"(?:https?://|doi:10\.)[A-Za-z0-9./_\-#?=%~]+", stash, s)
    for c in "&%$#_{}":
        s = s.replace(c, "\\" + c)
    s = s.replace("~", r"\textasciitilde{}")
    s = re.sub(r"\^\\\{([^{}]{1,12})\\\}", lambda m: r"\(^{" + m.group(1).replace("\\_", "_") + r"}\)", s)   # 逐語 ^{…}(エスケープ後の \{ \})
    s = re.sub(r"\^(-?\d+)(?![\d}])", lambda m: r"\(^{" + m.group(1) + r"}\)", s)
    s = re.sub(r"\^([A-Za-z]+)", lambda m: r"\(^{\mathrm{" + m.group(1) + r"}}\)", s)   # ε^rad 等の語上付き
    s = re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+", lambda m: r"\(^{" + "".join(SUPD[c] for c in m.group(0)) + r"}\)", s)
    s = re.sub(r"[₀₁₂₃₄]+", lambda m: r"\(_{" + "".join(SUBD[c] for c in m.group(0)) + r"}\)", s)
    for k, v in SYM.items():
        s = s.replace(k, v)
    if en:
        s = s.replace("—", "---").replace("–", "--")
    for i, u in enumerate(urls):
        s = s.replace(f"\x00U{i}\x00", r"\url{" + u + "}")
    return s


def code_tex(body):
    body = body.replace("\\", r"\textbackslash{}")
    for c in "&%$#_{}":
        body = body.replace(c, "\\" + c)
    if len(body) > CODE_LONG:
        return r"\texttt{" + body[:CODE_SPLIT] + r"}\allowbreak\texttt{" + body[CODE_SPLIT:] + "}"
    return r"\texttt{" + body + "}"


def tex_inline(s, en=False):
    parts = re.split(r"(\*\*.+?\*\*|`[^`]+`)", s)
    out = []
    for p in parts:
        if p.startswith("**"):
            out.append(r"\textbf{" + tex_text(p[2:-2], en) + "}")
        elif p.startswith("`"):
            out.append(code_tex(p[1:-1]))
        else:
            out.append(tex_text(p, en))
    return "".join(out)


def convert(md_path, en=False):
    raw = md_path.read_text()
    check_symbols(raw)
    # 脚注定義の収集と除去
    fdefs = dict(re.findall(r"^\[\^(\w+)\]: (.*)$", raw, flags=re.M))
    raw = re.sub(r"^\[\^(\w+)\]: .*\n?", "", raw, flags=re.M)
    lines = raw.splitlines()
    title = tex_inline(lines[0].lstrip("# "), en)
    ai = next(k for k, l in enumerate(lines[1:10], 1) if l.startswith("**"))
    author_line = lines[ai]; affil_line = lines[ai + 1]; orcid_line = lines[ai + 2]
    preprint = next(l for l in lines[1:8] if l.startswith("(") or l.startswith("("))
    footmeta = next(l for l in lines[1:8] if l.startswith("脚注:") or l.startswith("Footnote:"))
    quotes = [l[2:].strip() for l in lines[1:12] if l.startswith("> ")]
    # 本文開始 = 最初の "## "
    start = next(k for k, ln in enumerate(lines) if ln.startswith("## "))
    heads = [ln for ln in lines if ln.startswith("## ") or ln.startswith("### ")]
    body = []
    in_items = False
    toc = [r"\section*{" + ("Contents" if en else "目次") + "}", r"\begin{itemize}\setlength{\itemsep}{0pt}"]
    for h in heads:
        ind = r"\hspace{1.2em}" if h.startswith("### ") else ""
        toc.append(r"\item[] " + ind + tex_inline(re.sub(r"\[\^\w+\]", "", h.lstrip("#").strip()), en))
    toc.append(r"\end{itemize}")

    def inline_full(s):
        s = re.sub(r"\[\^(\w+)\]", lambda m: "\x00F" + m.group(1) + "\x00", s)
        out = tex_inline(s, en)
        return re.sub("\x00F(\\w+)\x00", lambda m: r"\footnote{" + tex_inline(fdefs.get(m.group(1), ""), en) + "}", out)

    def close_items():
        nonlocal in_items
        if in_items:
            body.append(r"\end{itemize}")
            in_items = False

    L = lines[start:]
    i = 0
    while i < len(L):
        ln = L[i]
        if ln.startswith("```"):
            close_items()
            body.append(r"\begin{quote}\small")
            i += 1
            while i < len(L) and not L[i].startswith("```"):
                body.append(code_tex(L[i].rstrip()) + r"\\*" if L[i].strip() else r"\smallskip")
                i += 1
        elif ln.startswith("### "):
            close_items(); body.append(r"\subsection*{" + inline_full(ln[4:]) + "}")
        elif ln.startswith("## "):
            close_items(); body.append(r"\section*{" + inline_full(ln[3:]) + "}")
        elif ln.startswith("[FIG] "):
            close_items()
            path, cap = ln[6:].split(" | ", 1)
            body.append(r"\begin{figure}[H]\centering")
            body.append(r"\includegraphics[width=.9\linewidth]{" + path + "}")
            body.append(r"\par\smallskip{\small " + inline_full(cap) + r"}")
            body.append(r"\end{figure}")
        elif ln.startswith("> "):
            close_items()
            body.append(r"\begin{quote}\textbf{" + inline_full(ln[2:].strip()) + r"}\end{quote}")
        elif ln.startswith("|"):
            close_items()
            rows = []
            while i < len(L) and L[i].startswith("|"):
                rows.append(L[i]); i += 1
            i -= 1
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows if not set(r.replace("|", "").strip()) <= set("-: ")]
            ncol = max(len(r) for r in cells)
            widths = [max((len(r[j]) if j < len(r) else 0) for r in cells) for j in range(ncol)]
            if sum(widths) > 90:
                tot = sum(max(w, 4) for w in widths)
                colspec = "".join(">{\\raggedright\\arraybackslash}p{%.3f\\linewidth}" % (0.92 * max(w, 4) / tot) for w in widths)
                pre = r"{\scriptsize\setlength{\tabcolsep}{2.5pt}\hyphenpenalty=50 \exhyphenpenalty=50 "
            else:
                colspec = "l" * ncol
                pre = r"{\footnotesize\setlength{\tabcolsep}{3.5pt}"
            body.append(pre + r"\begin{center}\begin{tabular}{" + colspec + "}")
            for k, r in enumerate(cells):
                body.append(" & ".join(inline_full(c) for c in r) + r" \\")
                if k == 0:
                    body.append(r"\hline")
            body.append(r"\end{tabular}\end{center}}")
        elif ln.startswith("- "):
            if not in_items:
                body.append(r"\begin{itemize}\setlength{\itemsep}{1pt}"); in_items = True
            body.append(r"\item " + inline_full(ln[2:]))
        elif re.match(r"^\d+\. ", ln):
            close_items()
            body.append(r"\noindent " + inline_full(ln) + r"\par\smallskip")
        elif not ln.strip():
            close_items(); body.append("")
        else:
            close_items(); body.append(r"\noindent " + inline_full(ln) + r"\par\smallskip")
        i += 1
        if i <= len(L) - 1 and body and body[-1] == r"\smallskip" and L[i - 1].startswith("```"):
            body.append(r"\end{quote}")
    close_items()
    # (8) 要旨(第 1 セクション)を先頭に置き、目次は第 2 セクション直前に挿入
    sec_idx = [k for k, b in enumerate(body) if b.startswith(r"\section*")]
    if len(sec_idx) >= 2:
        body = body[:sec_idx[1]] + toc + body[sec_idx[1]:]
    else:
        body = toc + body
    tex_body = "\n".join(body)
    opens = tex_body.count(r"\begin{quote}\small"); closes_needed = opens - tex_body.count(r"\end{quote}") + tex_body.count(r"\begin{quote}\textbf")
    cjk = "" if en else ("\\usepackage{xeCJK}\n\\setCJKmainfont{Hiragino Mincho ProN}\n")
    hyph = "\\hyphenpenalty=10000 \\exhyphenpenalty=10000 \\sloppy\n" if en else ""
    quote_block = "\n".join(r"\begin{center}\textbf{" + tex_inline(q.strip("*"), en) + r"}\end{center}" for q in quotes)
    return ("\\documentclass[11pt]{article}\n\\usepackage[margin=2.7cm]{geometry}\n\\usepackage{amsmath,amssymb}\n"
            "\\usepackage{graphicx}\n\\usepackage{url}\n\\usepackage{array}\n\\usepackage{float}\n" + cjk + hyph +
            "\\pagestyle{plain}\n"
            "\\title{" + title + r" \\[1ex] {\large " + tex_inline(preprint.strip("()()"), en) + "}}\n"
            "\\author{" + tex_inline(author_line.replace("**", ""), en) + r" \\ " + tex_inline(affil_line, en) + r" \\ " + tex_inline(orcid_line, en) + r"\thanks{" + tex_inline(footmeta.split(":", 1)[1].strip() if ":" in footmeta else footmeta, en) + "}}\n"
            "\\date{}\n\\begin{document}\n\\maketitle\n" + quote_block + "\n" + tex_body + "\n\\end{document}\n")


def main():
    ok = True
    for stem, en in [("vacancy_ja", False), ("vacancy_en", True)]:
        tex = convert(PDIR / f"{stem}.md", en)
        (PDIR / f"{stem}.tex").write_text(tex)
        r = subprocess.run(["tectonic", f"{stem}.tex"], cwd=PDIR, capture_output=True, text=True)
        (PDIR / f"{stem}.buildlog").write_text(r.stdout + r.stderr)
        print(stem, "->", "OK" if r.returncode == 0 else "FAIL", (PDIR / f"{stem}.pdf").exists() and (PDIR / f"{stem}.pdf").stat().st_size)
        ok &= r.returncode == 0
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
