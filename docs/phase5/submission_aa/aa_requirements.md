# A&A 投稿要件表(手順 F'-2、2026-08-24 実査。参謀突合用)

出所の階層: (A) aa.cls v9.4 実物・公式配布例 aa_example.tex(機械確認)/(B) A&A 公式ページ(aanda.org — **bot 遮断のため本文未取得**、検索スニペットのみ)/(C) 二次情報。**(B)(C) 由来の行は参謀がブラウザで公式ページと突合すること。**

| # | 項目 | 要件 | 出所 | 本稿の状態 |
|---|---|---|---|---|
| 1 | LaTeX クラス | aa.cls(A&A 公式マクロ v9.4, 2025/11/27) | A(実物 sha256 79bc49e0…) | 適用済み |
| 2 | マクロ入手元 | EDP Sciences ftp.edpsciences.org/pub/aa/aa-package.zip | B | **公式サーバが 503(2026-08-24 終日)**。GitHub 上の独立 3 リポジトリの byte 同一コピー(sha256 一致)で代替取得。**復旧後に公式 zip と sha256 照合すること(起票)** |
| 3 | 構造化要旨 | Context(任意)/Aims(必須)/Methods(必須)/Results(必須)/Conclusions(任意)。\abstract の 5 引数 | A + B | 4 段落構成(Conclusions 空)、292 語 |
| 4 | 要旨の長さ | 300 語以内・自己完結(参照・脚注なし) | B(aa.cls 内部定数 300 とも整合) | 292 語・脚注 [^pop] は除去(同一脚注が §3.1 に既出) |
| 5 | 引用書式 | author-year(natbib、aa.bst) | A | \bibliographystyle{aa} + vacancy_refs.bib 31 項目。本文引用は md 正本の名前・年表記を逐語保持(\citep 化しない — 数値トークン保存優先。参謀が可否を確認) |
| 6 | 付録の位置 | 参考文献の後(\appendix) | A(aa_example)+ B | 準拠(A–D) |
| 7 | 謝辞 | acknowledgements 環境、参考文献の前 | A | 準拠 |
| 8 | Data availability | Zenodo/CDS 等への言及。表データは CDS 寄託が原則(不備は校正段で保留) | B | 節を挿入済み(裁定 #12 の基本形)。**CDS 寄託の要否(本作は Zenodo 収載 430 MB)は投稿時に編集部へ明示すべき事項 — カバーレター案に記載** |
| 9 | 図 | PDF/EPS、列幅 \hsize / 全幅 \textwidth | A | 4 図 PDF 同梱(fig3 のみ全幅) |
| 10 | 表 | caption 必須(通常) | C | **2 表とも caption 未付与**(md 正本に無いため無断追加せず)。**裁定者承認用の提案文を別添** |
| 11 | 走り書き | \titlerunning / \authorrunning | A(aa.cls 警告) | 設定済み |
| 12 | フォント | txfonts 推奨 | A(aa_example) | **ローカル無効**(tectonic バンドルが t1xsl 未配信・403)。tex 内にコメントで明示。MMS 側コンパイルで有効化可 |
| 13 | 投稿システム | MMS(Manuscript Management System、aanda.org から) | B/C | 操作は裁定者のみ(裁定 #12) |
| 14 | カバーレター | 天文学的意義・希望セクションを記載 | C | 案を別添(セクション候補: *Numerical methods and codes* または *Catalogs and data* — 参謀判断) |
| 15 | ORCID | 投稿時に corresponding author の ORCID | B/C | 0009-0005-3401-9230(原稿 institute 行にも記載) |
| 16 | 言語 | 英語(language edit は受理後段階) | B | md 正本(裁定 #7 検分済み)を逐語変換 |

## 起票(裁定・確認待ち)

1. **aa.cls/aa.bst の出所**: 公式 EDP サーバ 503 のため GitHub ミラー 3 点一致で代替(aa.cls)。aa.bst は 2 系統存在し LSST texmf 保守版を採用 — **公式復旧後に照合、差分があれば差替え**。
2. **キーワード**(新規メタデータ、md 正本に無い): `extraterrestrial intelligence – astrobiology – solar neighborhood – catalogs – surveys – methods: statistical` を仮置き。**A&A 公式キーワードリストとの照合と採否は参謀・裁定者**。
3. **表 caption 2 件の提案**(承認まで tex は caption 無し):
   - 表 1(§4.3 の G3 集計表)案: "G3(i) anchor recounts against WS20 (frozen criteria)." ※実表の内容確認の上で参謀が確定
   - 表 2(付録 C)案: "Undecidable accounting across the three axes."
4. **Appendix B の運用記録が「8 rulings」のまま**(裁定 #9・#10 が計数外 — v1.0 凍結時点の記載)。md 正本の文面のため無断変更せず。A&A 版で更新するか否かは裁定事項(更新する場合は #9〜#12 を含む記録に改訂 → 誤り台帳登録の要否も併せて裁定)。
