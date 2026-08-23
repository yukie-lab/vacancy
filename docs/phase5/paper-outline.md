# Phase 5.1 — 論文 目次案(報告 (1)、裁定待ち。本文は目次裁定後に執筆)

> 仮題(日): 太陽近傍の空き度アトラス — 既存不在証拠の異種合算による星単位・技術帯別の占有確率上界台帳
> 仮題(英): A Vacancy Atlas of the Solar Neighbourhood: Star-by-Star, Technology-Band-Conditional Upper Bounds on Occupation from Heterogeneous Non-Detections
> 体裁: 日英、md → 既存パイプライン(EMBARK の build_paper_pdf.py 系譜)。数値は Phase 0–4 成果物からの転記のみ(転記元を脚注化)。凡例文(測量であって証明ではない / 入植許可証ではない)は表紙・要旨・結論・台帳・シミュレータに常時表示。

## 0. 表紙・要旨
- 著者ブロック(WAKE/EMBARK 形式: Yukie Maeda / Independent Researcher, Tokyo / ORCID 0009-0005-3401-9230、プレプリント行 doi:10.5281/zenodo.XXXXXXX、AI 開示脚注)
- 要旨の必須要素: 問い・母集団 332,571 星・電波 3 帯・ok 1,554/1,587/159・判定不能 99.52%(主結果)・G1/G2/G3 の結果(逸脱 1・不合格 1 を隠さず)・太陽自己校正・三軸交差 815・凡例二文

## 1. Introduction
- 1.1 中核の問い: 「宣言された技術帯の設備で占有されているなら既存サーベイで検出されていたはず」という条件付き不在証拠を、星単位・異種合算・条件付き上界の台帳として初めて計算する(世界に不在の量)。
- 1.2 動機(依頼者の趣旨を学術文体で): 侵略ではなく「空いているところ」を探すことで人類の生息域拡張に資する/宇宙の謎。倫理条件を方法論(条件付き確率文)に昇格させた設計(第1条3項)。
- 1.3 本稿の貢献(箇条): (i) 星単位台帳 (ii) 併合規則の定理化(素朴積の空き側バイアス) (iii) 二段事前登録 (iv) 判定不能会計を主結果とする読み (v) 三軸交差(合成なし)。
- 1.4 構成案内。

## 2. Position(第8条)
- 2.1 Grimaldi 系(確率論的母集団モデル)— 本作は星単位台帳。
- 2.2 Wright+18 ヘイスタック(全空間体積)— 本作は個別星への射影(判定不能 99.52% = ヘイスタック不完備性の星単位版)。
- 2.3 BL(Price+20, WS20)・Ĝ/Hephaistos — 本作は新規観測ではなく既存不在証拠の異種合算。Ĝ に恒星個別上限が無いこと(Phase 0 実査)。
- 2.4 先行の上限算式の多様性(Price 2/(0.5N) 系・WS20 1/N)と本作の二項厳密・ベイズ上界の関係(別量)。

## 3. Method
- 3.1 母集団: GCNS(EDR3, 331,312)+ missing 表 1,259 = 332,571。恒星基盤 DR3、DR4 二段構え。
- 3.2 技術帯の宣言(第3条1項): T-R1/R2/R3(窓 [1.10, 3.45] GHz 一様、R3 は f_ill ∈ [10⁻⁵, 10⁻²])、T-W1(情報レイヤ)。拡張区画。
- 3.3 ε の因子構造: 距離・感度(EIRP_min = EIRP50 (d/50)² / R(θ)、WS20 全行再現 比 1.0000)・周波数被覆 ε(ν)・f_pipe 0.5・稼働率・ビーミング。T-W1 は Hephaistos 式モデル+kσ 超過。
- 3.4 併合規則(裁定 #1 C): 潜在変数(ν, f_ill, T_DS)周辺化 → モダリティ間積。**定理**: 同一帯 2 回観測で素朴積 1−(1−c)² > c(厳密)— 素朴積は検出確率を過大評価し空き側に倒れる。f_ill 全共有の保守性(Jensen)。
- 3.5 合算式・π 掃引(対数 51 点)・数値安定化(logsumexp)。
- 3.6 二段事前登録: (a) コミット 10a01e7(技術帯集合・因子構造・併合規則)、(b) DOI 10.5281/zenodo.22067884(閾値・合算式・G1–G3 基準・MC 宣言)。以後の変更は逸脱。
- 3.7 独立性仮定の宣言(Phase 1.2 表 I-1〜X-1)。
- 3.8 データ来歴: WS20 VizieR J/MNRAS/498/5720、BL 公開アーカイブ(観測日 MJD、6,219 HIP 目標 100% 充足)、GCNS VizieR J/A+A/649/A6、HGCA、Mamajek 表、NEA/HWC(取得 2026-08-23、sha256)。

## 4. Verification(第7条)
- 4.1 G1: 単調性 6,777 検査・違反 0。MC 1,000(seed 20260823)— 電波 90% 幅中央値 0.094 dex(f_pipe 支配、観測行数比例)、低信頼セル 0。W1 情報レイヤ: 低信頼 25,822(97% は Λ=0 クリップ由来、事後 @π=10⁻² で結論不変 — 裁定 #5-2 の説明文)。
- 4.2 G2: 独立二経路(参謀の対数和)、max|Δlog₁₀Λ| 電波 4.9×10⁻¹⁰・廃熱 5.2×10⁻⁷、違反 0。エクスポートに Λ 列を含めない手順。
- 4.3 G3(i): (a) Price+20 比較表(当方二項厳密は公刊の 1.5–1.6 倍、原典算式非明記の脚注)/(b) WS20 1/N: ≤50 pc N=1513 完全一致、≤100 pc 0.0598%、≤200 pc 0.0388%(EIRP 値 = 殻内最大値の 3 桁一致)/(c) 別量の殻平均表。
- 4.4 G3(ii): 定義 A の結果(3.13 / 93 / 982、不合格)と比が γ で爆発する構造(第5条3項の保守設計の帰結、計算誤りではない — 方向分析)。定義 B の診断(0.82 / 0.17 / 0.30、採用せず、合格を示唆する語を使わない)。→ T-W1 降格(第6条)。**Phase 3 status の控え 3 点を逐語反映。**
- 4.5 G3(iii): 太陽系仮想行 d = 1.3–10.8 pc、Λ ≥ 0.999085(周辺化)/ ≥ 0.99479(f_ill 上端)、赤信号 Λ_extreme = 0.0851。
- 4.6 **逸脱節**(第9条3項): 裁定 #3 — 外部事実(WS20 の +42/+9 が「距離 ≤ 殻 かつ EIRP_min ≤ 閾値」の計数を証明)による基準改訂(旧基準不合格の事実を残す)/ 裁定 #4 — 凍結基準どおりの不合格受理と降格。両方向の実例として「制度が機能した」記述。誤り台帳 E-1(参謀の検分不備)・E-2(経緯)。

## 5. Results
- 5.1 台帳の概観: ok 1,554 / 1,587 / 159、Λ 分布(0.43 / 0.80 / 0.86 = 3 帯 / S / L)、代表 π の事後(@10⁻²: 0.0080)。
- 5.2 **判定不能 99.52% を主結果として**: 視野外 330,984、うち観測済み未公刊 1,530(第5条1項 d)。ヘイスタック不完備性の星単位版。
- 5.3 π 掃引の上界曲線(図)。単一数値を「空き度」と呼ばない(第10条1項)。
- 5.4 太陽自己校正: 「地球級帯 T-R3 では事後 ≈ 事前 — 本アトラスが空き度を語れる技術帯の下限は地球自身で校正される。」
- 5.5 W1 情報レイヤ(claim=false): ε≈1 の物理(太陽@10 pc 1.9 Jy vs DS 90 Jy)と、アンカー未確立の地位。

## 6. Three-axis atlas(第4条)
- 6.1 結合率: EMBARK 14,799(4.45%)、到達可能性判定不能 95.55%、NEA 1,037 ホスト、HWC 35 ホスト。
- 6.2 交差計数: 会合到達 ∧ T-R1 上界 815 / T-R3 108 / 同行 ∧ T-R1 311 / S1 633 / NEA ホスト 136。セル別表(L0 セル 2 → 1、8 → 3)。
- 6.3 定住資源性スライダー S1–S3(軸の関数、判定基準でない)。
- 6.4 HWC 照合表(合成ではない)。EMBARK 母集団外 22,699 星は注記のみ(裁定 #5-5)。

## 7. Interpretation discipline(第1条2・4項、第10条)
- 四文: 「測量であって証明ではない」「空き度は入植許可証ではない」「HWC 照合表は合成ではない」「1/N と星単位事後は別量(数値の近さは偶然)」。
- 条件節の省略禁止、単一数値・順位の禁止、三軸の積・加重和の禁止、判定不能を空き側に倒さない。
- W1 情報レイヤの地位(既定オフ・バッジ)。

## 8. Limitations & future
- 未公刊 BL 観測(1,530 星)・UWL/C/X 帯・光学レーザー(拡張区画)。
- W1 の再アンカー経路(受動: Hephaistos 星単位表の公開 or DR4 v1.1)。
- DR4(2026-12-02)合流 v1.1: 距離更新分の再計算のみ(PHASES Phase 6)。
- 独立性仮定(f_pipe 観測間独立)の感度枠。

## 付録
- A. ε 因子表・受信帯被覆・共通 ν グリッド(凍結 §2 の転記)。
- B. Method record and AI disclosure(三役・裁定 #1–#5・逸脱 1・不合格 1・自己申告 3 件以上・誤り台帳 r1)。
- C. 判定不能会計の全表(三軸)。
- D. Reproducibility and data release(再生成コマンド、sha256 マニフェスト、Zenodo 収載物、シミュレータハーネス)。

## 引用・謝辞 確認リスト(執筆前に参謀照合)
| 項目 | 文言/出典 | 確認 |
|---|---|---|
| Price+20 | Price D. C. et al. 2020, AJ 159, 86 | ☐ |
| WS20 | Wlodarczyk-Sroka B. S., Garrett M. A., Siemion A. P. V. 2020, MNRAS 498, 5720; VizieR J/MNRAS/498/5720 | ☐ |
| Enriquez+17 | Enriquez J. E. et al. 2017, ApJ 849, 104 | ☐ |
| Isaacson+17 | Isaacson H. et al. 2017, PASP 129, 054501 | ☐ |
| BL 公開アーカイブ | seti.berkeley.edu/opendata(Lebofsky+19 の引用と取得日) | ☐ |
| Hephaistos I / II | Suazo M. et al. 2022, MNRAS 512, 2988 / 2024, MNRAS 531, 695 | ☐ |
| Ĝ | Wright J. T. et al. 2014, ApJ 792, 26/27; Griffith R. L. et al. 2015, ApJS 217, 25 | ☐ |
| Wright+18 ヘイスタック | Wright J. T., Kanodia S., Lubar E. 2018, AJ 156, 260 | ☐ |
| Grimaldi 系 | Grimaldi C. 2017, Sci. Rep. 7, 46273 ほか(参謀選定) | ☐ |
| GCNS | Gaia Collaboration, Smart R. L. et al. 2021, A&A 649, A6; VizieR J/A+A/649/A6 | ☐ |
| Gaia | Gaia Collaboration 2016 (A&A 595, A1); EDR3/DR3 2021/2023 + **DPAC 謝辞の指定文言** | ☐ |
| HGCA | Brandt T. D. 2021, ApJS 254, 42 | ☐ |
| Bailer-Jones 距離 | Bailer-Jones C. A. L. et al. 2018, AJ 156, 58 | ☐ |
| Mamajek 表 | Pecaut M. J., Mamajek E. E. 2013, ApJS 208, 9(表 v2022.04.16) | ☐ |
| WISE / AllWISE / CatWISE | Wright E. L. et al. 2010; Cutri R. M. et al. 2014(II/328); Marocco F. et al. 2021 | ☐ |
| Jarrett+11 零点 | Jarrett T. H. et al. 2011, ApJ 735, 112 | ☐ |
| Sullivan+78 / Saide+23 | Sullivan W. T., Brown S., Wetherill C. 1978, Science 199, 377 / Saide R. C. et al. 2023, MNRAS 522, 2393 | ☐ |
| Sheikh+19(ドリフト) | Sheikh S. Z. et al. 2019, AJ 158, 60 | ☐ |
| NASA Exoplanet Archive | **指定謝辞文**: "This research has made use of the NASA Exoplanet Archive, which is operated by the California Institute of Technology, under contract with the National Aeronautics and Space Administration under the Exoplanet Exploration Program." + DOI 10.26133/NEA12(pscomppars)+ 取得日 | ☐ |
| HWC | Habitable Worlds Catalog, Planetary Habitability Laboratory @ UPR Arecibo(phl.upr.edu/hwc)、取得日・版 | ☐ |
| VizieR / CDS | Ochsenbein F. et al. 2000, A&AS 143, 23 + CDS 謝辞 | ☐ |
| 事前登録 (b) | Maeda Y. 2026, Zenodo, doi:10.5281/zenodo.22067884 | ☐ |
| WAKE / EMBARK | doi:10.5281/zenodo.21966305 / 10.5281/zenodo.22059576 | ☐ |
