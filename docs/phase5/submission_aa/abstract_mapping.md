# 構造化要旨 変換対応表(機械生成: scripts/build_aa_version.py)

md 正本の要旨 12 文の全数を A&A 構造化要旨に再割当(欠落・追加なしを機械検査)。

| md 文番号 | A&A 段落 | 処置 |
|---|---|---|
| 2 | Context | 接続修正: 「this quantity」→「the star-by-star, band-conditional upper bound on occupation」(指示語解決) |
| 1 | Aims | 逐語 |
| 3 | Methods | 逐語 / 脚注 [^pop] は除去(A&A 要旨は脚注不可。同一脚注が本文 §3.1 に既出のため情報欠落なし) |
| 4 | Methods | 逐語 |
| 5 | Methods | 逐語 |
| 6 | Methods | 逐語 |
| 7 | Results | 逐語 |
| 8 | Results | 逐語 |
| 9 | Results | 逐語 |
| 10 | Results | 逐語 |
| 11 | Results | 逐語 |
| 12 | Results | 逐語 |

その他の体裁変換: 図キャプションの「Figure N: 」接頭辞除去(自動番号と重複)+先頭 1 文字の大文字化 /
前付の (Preprint, …) 行は投稿版に不掲載(データ DOI は Data availability 節に記載)/
見出しの明示番号 → aa.cls 自動番号 / 付録 A–D は A&A 慣行により参考文献の後 /
参考文献 31 項目 → BibTeX(vacancy_refs.bib、aa.bst author-year)。本文引用は md の名前・年表記を逐語保持。
