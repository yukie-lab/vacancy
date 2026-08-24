# カバーレター・Data availability 文案(手順 F'-3、日英併記。裁定者確認用ドラフト — 投稿操作は裁定者のみ)

## カバーレター案(EN)

Dear Editors,

Please consider the enclosed manuscript, "A Vacancy Atlas of the Solar Neighbourhood: Star-by-Star, Technology-Band-Conditional Upper Bounds on Occupation from Heterogeneous Non-Detections", for publication in Astronomy & Astrophysics (suggested section: [Numerical methods and codes / Catalogs and data — 参謀判断で一方を選択]).

The paper aggregates existing SETI non-detections into a star-by-star, technology-band-conditional upper bound on occupation for the 332,571 stars of the Gaia Catalogue of Nearby Stars — to our knowledge, the first ledger of this quantity. It is a direct star-level extension of Wlodarczyk-Sroka et al. (2020, MNRAS 498, 5720): their population-level 1/N limits are reproduced exactly as an anchor, and their observation rows are re-projected onto individual stars with full provenance. The main result is deliberately conservative: 99.52% of the population is undecidable, and the accounting of that fraction — star by star, band by band — is presented as the star-level version of haystack incompleteness.

Methodological safeguards may be of interest to referees: thresholds and pass criteria were pre-registered on Zenodo before aggregation (doi:10.5281/zenodo.22067884); all data, code, and the error ledger are public (doi:10.5281/zenodo.22081202); one verification anchor (a waste-heat count reproduction) failed and the corresponding band was demoted rather than re-fitted, with the failure reported in the paper. The verification protocol, including the roles of AI systems, is disclosed in Appendix B; this internal verification is not a substitute for peer review.

The full dataset (430 MB, 55 files with SHA-256 manifest) is archived on Zenodo. We are glad to deposit the per-star table at the CDS in VizieR-ready form if the journal prefers.

This manuscript is not under consideration elsewhere. [MNRAS 版ファイルが Zenodo レコードに含まれる件の一文が必要かは参謀判断: The Zenodo record contains a file formatted for another journal, prepared before the venue decision; it has not been submitted.]

Yours sincerely,
Yukie Maeda (ORCID 0009-0005-3401-9230)
Independent Researcher, Tokyo

## カバーレター要旨(JA、裁定者確認用)

- 投稿先セクション候補は 2 つ(数値手法・コード / カタログ・データ)— 参謀が A&A のセクション一覧と照合して選択。
- 本作の性格: 星単位・帯条件付き上界台帳の初提示(to our knowledge 形)。WS20 の直接の星単位拡張(1/N をアンカーとして厳密再現)。
- 主結果 = 判定不能 99.52% の会計(ヘイスタック不完備性の星単位版)。
- 独立検証構造: 二段事前登録(DOI 22067884)・全公開(DOI 22081202)・アンカー不合格 1 件は再適合でなく降格+誌面報告・AI の役割は付録 B 開示・内部検証は査読の代替ではない。
- CDS/VizieR 寄託の用意がある旨を明記(A&A のデータ方針対応)。
- 「他誌へ非係属」宣言。Zenodo レコード内の mnras 版ファイルへの言及要否は参謀判断。

## Data availability 文案(原稿 §Data availability に挿入済みの文面)

EN: All data, code, and the pre-registration are openly available at Zenodo: doi:10.5281/zenodo.22081202 (data and code) and doi:10.5281/zenodo.22067884 (pre-registration). An interactive simulator is available at https://yukie-lab.github.io/vacancy-atlas/.

JA(参考訳): 全データ・コード・事前登録は Zenodo で公開(doi:10.5281/zenodo.22081202 = データ・コード、doi:10.5281/zenodo.22067884 = 事前登録)。対話シミュレータは https://yukie-lab.github.io/vacancy-atlas/ 。
