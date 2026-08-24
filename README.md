# Project VACANCY — 太陽近傍・空き度アトラス

**A Vacancy Atlas of the Solar Neighbourhood — star-by-star, technology-band-conditional upper bounds on occupation**

前田幸枝 / Yukie Maeda ([ORCID 0009-0005-3401-9230](https://orcid.org/0009-0005-3401-9230)) — Independent Researcher, Tokyo

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22081202.svg)](https://doi.org/10.5281/zenodo.22081202)

既存 SETI サーベイの不検出を、宣言した技術帯 T の条件付きで星単位に合算し、太陽近傍 332,571 星(GCNS)の占有確率上界曲線(空き度、事前確率 π の関数)を初めて計算した測量。判定不能 330,984 星(99.52%)自体が主結果(ヘイスタック不完備性の星単位版)。

## 解釈規律(四文)

1. 測量であって証明ではない。不在の証拠は限定的であり、占有の不在を証明しない。
2. 空き度は入植許可証ではない。
3. HWC 照合表は合成ではない。
4. 1/N と星単位事後は別量(数値の近さは偶然)。

## 成果物

- **論文**: `docs/phase5/paper/vacancy_ja.pdf`(日本語)/ `vacancy_en.pdf`(英語)/ `vacancy_en_mnras.md`(MNRAS 投稿用変種)
- **データ正本 = Zenodo**: [doi:10.5281/zenodo.22081202](https://doi.org/10.5281/zenodo.22081202)(v1.0、55 ファイル 430 MB、CC BY 4.0)。**本リポジトリは大容量台帳(ledger_v0.json 62 MB・lambda_ledger.json 151 MB・atlas_v1.json 142 MB ほか)を含まない**(.gitignore で除外)。完全なファイル一覧と sha256 は `data/release/MANIFEST.json`。
- **シミュレータ**: https://yukie-lab.github.io/vacancy-atlas/(リポジトリ [yukie-lab/vacancy-atlas](https://github.com/yukie-lab/vacancy-atlas)。入口 = 検証ハーネス)
- **事前登録**: (a) コミット `10a01e71`(Phase 0 凍結)/ (b) [doi:10.5281/zenodo.22067884](https://doi.org/10.5281/zenodo.22067884)(凍結版 sha256 は MANIFEST 参照)
- **誤り台帳**: `data/release/error-ledger-public-r1.md`(E-1〜E-8、全て公開)

## 統治と再現

- 憲法: `CLAUDE.md`(v0.3)/ 工程: `PHASES.md` / **裁定ログ(全 11 裁定+実行記録)**: `docs/rulings/裁定ログ.md`
- 三役: 裁定者(人間)・参謀(独立検算)・実行(Claude Code)。凍結後の変更は全て逸脱起票 → 裁定。
- ゲート: G1 単調性(6,777 検査・違反 0)/ G2 独立二経路(≤5.2e-7 dex)/ G3 外部アンカー(WS20 完全一致・Hephaistos 不合格 → T-W1 降格・太陽自己検定合格)
- 環境: `environment.yml` / テスト: `python3 -m unittest discover tests`
- `data/raw/` は git 管理外(取得スクリプトは `scripts/`)

## 姉妹プロジェクト

[WAKE](https://doi.org/10.5281/zenodo.21966305)(到来統計)→ [EMBARK](https://doi.org/10.5281/zenodo.22059576)(地球発到達可能圏)→ VACANCY(空き度)

## ライセンス

二層(`LICENSE` 参照): コード = MIT / データ・論文 = CC BY 4.0。
