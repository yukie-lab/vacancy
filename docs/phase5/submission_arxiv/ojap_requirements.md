# OJAp(The Open Journal of Astrophysics)投稿要件表(2026-08-25 実査)

出典(全て公式・ブラウザ実閲覧): [For Authors](https://astro.theoj.org/for-authors) / [About](https://astro.theoj.org/about)。運営 = Maynooth Academic Publishing、ISSN 2565-6120、Free Journal Network 加盟。

| # | 項目 | 公式記載 | 出典 |
|---|---|---|---|
| 1 | 投稿方式 | **arXiv オーバーレイ誌**。手順: (1) 先に arXiv へ投稿(公式は CC-BY 選択を案内するが、制限的ライセンスでも可・出版版で変更可と明記。**本作は非独占ライセンスで投稿(裁定済み)、CC BY は採録後の掲載版で扱う** — 裁定 #14 補正 (1))→ (2) arXiv 掲載後に「Submit a manuscript」ボタン(https://app.scholasticahq.com/submissions/oja/new)から「very short submission process」→ (3) 困難な場合は編集者へメールで代行入力可。直接投稿も受けるが arXiv 先行を強く推奨 | For Authors |
| 2 | 対象カテゴリ | 「astro-ph に適するなら本誌に適する」が唯一の基準。6 区分を列挙し **astro-ph.IM(Instrumentation and Methods)を明示的に含む**。誌面にも専用セクション有(/section/1192-instrumentation-and-methods-for-astrophysics) | For Authors |
| 3 | テンプレート | **必須ではない**。「initial submissions can be made in any format acceptable to the arXiv」。最終版は同誌スタイル(openjournal.cls: http://www.thphys.nuim.ie/staff/pcoles/openjournal.cls)での組版を「推奨」。既刊論文の arXiv ソースをテンプレートとして利用可 | For Authors |
| 4 | 査読形態 | 通常の編集委員会+レフェリー制(「conventional Editorial Board and refereeing process」)。基準 = scientific quality / originality / relevance / comprehensibility。Managing Editor の初期スクリーニング → 担当編集者 → レフェリー 1 名以上。投稿の事実は非公開扱い。コピーエディットなし(著者校正責任、必要時は有償の Scitext Cambridge を紹介) | For Authors |
| 5 | 所要期間 | **公称なし**(For Authors・About のいずれにも査読期間の数値記載なし) | — |
| 6 | 費用 | **明文でゼロ**: 「entirely free of charge both to authors and to readers」(For Authors)/「submitted … free of charge, refereed free of charge and are published (online only) free of charge」(About) | 両頁 |
| 7 | 出版形態 | 受理後、メタデータ(article ID・受理日)を付した受理版を arXiv に再投稿 → **CROSSREF DOI 付与** → 誌面はアブストラクト+メタデータ+arXiv リンクのオーバーレイ。CC-BY・永続無料公開・著作権は著者保持 | For Authors |
| 8 | **生成 AI 方針** | 全面禁止ではないが、(i) **使用したら謝辞(acknowledgments)節で申告必須**、(ii) 計算・解析・可視化に使用した場合は**検証手順の説明を含めること**、(iii) 幻覚参照文献やプロンプト残存など直接証拠があれば不受理 | For Authors |
| 9 | 多重投稿 | 他誌で公開済み・審査中の論文は不可(→ 本作は MNRAS 未投稿・A&A 中止のため適合) | For Authors |
| 10 | データ公開 | 「Best Practices for Data Publication in the Astronomical Literature」(Chen+2022, ApJS 260, 5)の参照を推奨 | For Authors |

## 本作の適合評価

- **スコープ**: 基準は「astro-ph に適するか」のみ。本作は astro-ph.IM(データ解析・統計手法・データベース設計)を想定しており **適合**。誌面にも IM セクションが存在。エンドースを経て arXiv に載れば OJAp のスコープ関門は実質通過。
- **費用**: 明文でゼロ(裁定 #13 の経路選定の前提が公式記載で裏付けられた)。
- **手順との整合**: 経路 Zenodo(済)→ arXiv → OJAp は同誌の推奨手順(arXiv 先行)と一致。**arXiv 投稿時は非独占ライセンス(裁定済み)** — CC BY は OJAp 採録後の掲載版の論点として保留(公式ページも「より制限的なライセンスでも大きな問題はない。出版版で変更可」と明記。裁定 #14 補正 (1))。
- **AI 方針への対応(起票)**: 本作の AI 開示は付録 B(全開示)+検証は G1–G3・二経路・機械ゲートで、方針 (ii) の「検証手順の説明」は充足。ただし **(i) は「謝辞節での申告」を明文で要求**しており、現行の謝辞節に AI への言及がない(付録 B にのみ記載)。→ **謝辞への一文追加(例: "AI systems (Anthropic Claude) were used throughout under the protocol disclosed in Appendix B.")が必要 — md 正本の文面変更のため裁定事項**。
- **テンプレート**: 初回投稿は現行 arXiv 版(article クラス)で可。受理後の最終版で openjournal.cls への組替えを想定(build_ojap_version は受理後に新設すれば足りる)。
- 残る非公称事項(査読期間)は実測になる。
