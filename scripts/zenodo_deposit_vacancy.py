#!/usr/bin/env python3
"""VACANCY v1 — Zenodo デポジット(裁定 #11。publish は実行しない — 人間ゲート)。

トークン: 環境変数 ZENODO_TOKEN を優先、無ければ ~/.zenodo_token(chmod 600、WAKE/EMBARK 規律)。
いずれも Authorization ヘッダのみで送信し、出力・ログ・コミットに一切残さない。

手順(冪等 — 状態は data/zenodo_deposit_vacancy.json に保存。トークンは保存しない):
 1. 下書き deposit 作成 + prereserve_doi で DOI 予約(再開: 状態ファイル or ZENODO_DEPOSIT_ID)
 2. 論文 md(日英・mnras)の XXXXXXX を予約 DOI に置換 → PDF 再生成 → gate 再 PASS
    → release 複製更新 → MANIFEST 最終再生成 → v1.0 確定コミット+タグ
 3. メタデータ PUT(Dataset / CC-BY-4.0 / 日英タイトル / Related works / v1.0)
 4. data/release の全ファイルをパス付きキーで bucket に PUT。重複・部分アップロードは
    削除してから再送。リトライ 3 回・指数バックオフ。API 返却 checksum(md5)を
    ローカル md5 と、ローカル sha256 を MANIFEST と全数突合して一覧出力
 5. ドラフト URL を表示して終了(publish は幸枝さんの手で)

実行: cd ~/Desktop/test/vacancy && python3 scripts/zenodo_deposit_vacancy.py
"""
import hashlib, json, os, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path

API = "https://zenodo.org/api"
ROOT = Path(__file__).resolve().parents[1]
PDIR = ROOT / "docs/phase5/paper"
REL = ROOT / "data/release"
STATE = ROOT / "data/zenodo_deposit_vacancy.json"


def token():
    t = os.environ.get("ZENODO_TOKEN")
    if t:
        return t.strip()
    p = Path.home() / ".zenodo_token"
    if p.exists():
        return p.read_text().strip()
    sys.exit("ZENODO_TOKEN も ~/.zenodo_token も無い")


def req(method, url, tok, data=None, ctype="application/json", raw=False, timeout=1800):
    headers = {"Authorization": f"Bearer {tok}"}
    body = None
    if data is not None:
        body = data if raw else json.dumps(data).encode()
        headers["Content-Type"] = ctype
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        txt = resp.read().decode()
        return json.loads(txt) if txt else {}


def retry(fn, what, n=3):
    for a in range(n):
        try:
            return fn()
        except Exception as e:
            msg = getattr(e, "reason", None) or e
            print(f"    retry {a+1}/{n} {what}: {type(e).__name__} {msg}")
            if a == n - 1:
                raise
            time.sleep(2 ** (a + 1) * 5)


def sh(*cmd, cwd=ROOT):
    print("  $", " ".join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], cwd=cwd, check=True)


def main():
    tok = token()
    # ---- 1. 作成 or 再開
    st = json.loads(STATE.read_text()) if STATE.exists() else {}
    dep_id = os.environ.get("ZENODO_DEPOSIT_ID") or st.get("deposit_id")
    if dep_id:
        dep = retry(lambda: req("GET", f"{API}/deposit/depositions/{dep_id}", tok), "GET deposit")
        print(f"[1] 既存ドラフト {dep_id} 再開")
    else:
        dep = retry(lambda: req("POST", f"{API}/deposit/depositions", tok, {}), "POST deposit")
        dep_id = dep["id"]
        print(f"[1] デポジット {dep_id} 作成")
    doi = dep["metadata"]["prereserve_doi"]["doi"]
    bucket = dep["links"]["bucket"]
    STATE.write_text(json.dumps({"deposit_id": dep_id, "prereserved_doi": doi,
                                 "draft_url": f"https://zenodo.org/uploads/{dep_id}"}, indent=1))
    print(f"    予約 DOI: {doi}")

    # ---- 2. DOI 置換 → PDF → gate → release 複製 → MANIFEST → コミット+タグ
    changed = False
    for stem in ("vacancy_ja.md", "vacancy_en.md", "vacancy_en_mnras.md"):
        p = PDIR / stem
        s = p.read_text()
        if "zenodo.XXXXXXX" in s:
            p.write_text(s.replace("10.5281/zenodo.XXXXXXX", doi))
            changed = True
    print(f"[2] DOI 置換: {'実施' if changed else 'スキップ(済み)'}")
    if changed:
        sh("python3", "scripts/build_mnras_version.py")
        # mnras 再生成は en.md から作るので DOI は引き継がれる。ja/en の PDF を再生成
        sh("python3", "scripts/build_paper_pdf.py")
    r = subprocess.run(["python3", "scripts/gate_check_paper.py"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-600:]); sys.exit("gate_check FAIL — 停止")
    print("    gate_check PASS")
    # release 複製 + MANIFEST 最終再生成
    import shutil
    for f in ("vacancy_ja.md", "vacancy_en.md", "vacancy_en_mnras.md", "vacancy_ja.pdf", "vacancy_en.pdf"):
        shutil.copyfile(PDIR / f, REL / "paper" / f)
    files = {}
    for root, dirs, fs in os.walk(REL):
        for f in sorted(fs):
            if f in ("MANIFEST.json", ".DS_Store"):
                continue
            p = Path(root) / f
            rel = str(p.relative_to(REL))
            b = p.read_bytes()
            files[rel] = {"sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)}
    bundle = hashlib.sha256("".join(f"{k} {files[k]['sha256']}\n" for k in sorted(files)).encode()).hexdigest()
    man = {"release": f"vacancy-data-v1.0(doi:{doi})", "generated": "2026-08-24",
           "zenodo_filename_rule": "Zenodo 収載時のファイル名 = 本 MANIFEST のパスの '/' を '__' に置換したもの(バケットの制約)",
           "constitution": "CLAUDE.md v0.3 / 裁定 #1–#11",
           "preregistration_a_commit": "10a01e710854b69344651ed6ba016ab303c9d124",
           "preregistration_b_doi": "10.5281/zenodo.22067884",
           "n_files": len(files), "total_bytes": sum(v["bytes"] for v in files.values()),
           "bundle_sha256_of_file_list": bundle, "files": dict(sorted(files.items()))}
    (REL / "MANIFEST.json").write_text(json.dumps(man, ensure_ascii=False, indent=1))
    print(f"    MANIFEST 再生成: {len(files)} ファイル, bundle {bundle[:16]}…")
    sh("git", "add", "-A")
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode != 0:
        sh("git", "-c", "user.name=Claude Code", "-c", "user.email=noreply@anthropic.com",
           "commit", "-q", "-m", f"release: v1.0 確定(doi:{doi} 埋め込み・MANIFEST 最終)\n\nCo-Authored-By: Claude Fable 5 <noreply@anthropic.com>")
    subprocess.run(["git", "tag", "-f", "v1.0"], cwd=ROOT, check=True)
    print("    v1.0 確定コミット+タグ")

    # ---- 3. メタデータ PUT
    en = (PDIR / "vacancy_en.md").read_text(); ja = (PDIR / "vacancy_ja.md").read_text()
    abs_en = en.split("## Abstract\n", 1)[1].split("\n## ", 1)[0].strip()
    abs_ja = ja.split("## 要旨\n", 1)[1].split("\n## ", 1)[0].strip()
    import re
    strip_fn = lambda t: re.sub(r"\[\^\w+\]", "", t)
    para = lambda t: "".join(f"<p>{p.strip()}</p>" for p in t.split("\n\n") if p.strip())
    desc = ("<p><b>Abstract (English)</b></p>" + para(strip_fn(abs_en))
            + "<p><b>要旨(日本語)</b></p>" + para(strip_fn(abs_ja))
            + "<p><b>Files.</b> Papers in Japanese and English (PDF + markdown sources, and an MNRAS-format variant), "
            "the ε ledger (ledger_v0.json, formula eps-v0.2), the Λ ledger (lambda_ledger.json), the three-axis atlas "
            "(atlas_v1.json), radio observation-row provenance (radio_obs_v0.json), the G1/G2/G3 verification reports, "
            "frozen copies of the NASA Exoplanet Archive / HWC / Mamajek-table inputs (retrieved 2026-08-23), all scripts "
            "and unit tests, the public error ledger r1 (E-1..E-8), and MANIFEST.json with per-file SHA-256. "
            f"Bundle SHA-256 of the file list: {bundle}.</p>"
            "<p><b>Pre-registration.</b> Thresholds, the aggregation rule, and the G1&ndash;G3 pass criteria were frozen and "
            "publicly registered before aggregation: doi:10.5281/zenodo.22067884.</p>"
            "<p><b>Discipline.</b> This is a survey, not a proof; evidence of absence is limited and does not prove the absence "
            "of occupation. A vacancy bound is not a settlement permit.</p>"
            "<p><b>Sister projects.</b> WAKE doi:10.5281/zenodo.21966305; EMBARK doi:10.5281/zenodo.22059576. "
            "Browser simulator: vacancy-atlas (GitHub Pages, published after this record).</p>")
    md = {"metadata": {
        "upload_type": "dataset",
        "publication_date": "2026-08-24",
        "title": ("Project VACANCY: A Vacancy Atlas of the Solar Neighbourhood — Star-by-Star, "
                  "Technology-Band-Conditional Upper Bounds on Occupation / 太陽近傍の空き度アトラス: "
                  "既存不在証拠の異種合算による星単位・技術帯別の占有確率上界台帳(v1.0 論文・台帳・コード)"),
        "creators": [{"name": "Maeda, Yukie", "orcid": "0009-0005-3401-9230",
                      "affiliation": "Independent Researcher, Tokyo"}],
        "license": "cc-by-4.0",
        "version": "v1.0",
        "language": "eng",
        "keywords": ["SETI", "technosignatures", "Gaia DR3", "GCNS", "Breakthrough Listen",
                     "upper limits", "solar neighbourhood", "preregistration", "vacancy atlas"],
        "related_identifiers": [
            {"relation": "references", "identifier": "10.5281/zenodo.22067884"},
        ],
        "prereserve_doi": True,
        "description": desc,
    }}
    for rel_try in ("isRelatedTo", "references"):
        md["metadata"]["related_identifiers"] = ([{"relation": "references", "identifier": "10.5281/zenodo.22067884"}]
            + [{"relation": rel_try, "identifier": d} for d in ("10.5281/zenodo.21966305", "10.5281/zenodo.22059576")])
        try:
            retry(lambda: req("PUT", f"{API}/deposit/depositions/{dep_id}", tok, md), "PUT metadata", n=1)
            print(f"[3] メタデータ PUT(WAKE/EMBARK relation = {rel_try})")
            break
        except Exception as e:
            if rel_try == "references":
                raise
            print(f"    relation {rel_try} は拒否 → references にフォールバック")

    # ---- 4. アップロード + 全数突合
    existing = retry(lambda: req("GET", f"{API}/deposit/depositions/{dep_id}/files", tok), "GET files")
    exist_by_name = {f["filename"]: f for f in existing}
    results = []
    upload_list = sorted(files) + ["MANIFEST.json"]
    for relname in upload_list:
        p = REL / relname
        data = p.read_bytes()
        md5 = hashlib.md5(data).hexdigest()
        prev = exist_by_name.get(relname.replace("/", "__"))
        if prev and prev.get("checksum", "").split(":")[-1] == md5:
            results.append((relname, len(data), md5, "既存一致(再送不要)", True))
            continue
        if prev:   # 重複/部分アップロードは削除してから再送(裁定 #11)
            retry(lambda: req("DELETE", prev["links"]["self"], tok), f"DELETE {relname}")
            print(f"    旧 {relname} を削除(不一致/部分)")
        key = relname.replace("/", "__")            # バケットはスラッシュ不可 → 命名則: パスの / を __ に(MANIFEST に注記)
        r = retry(lambda: req("PUT", f"{bucket}/{key}", tok, data, ctype="application/octet-stream", raw=True),
                  f"PUT {relname}")
        api_md5 = r.get("checksum", "").split(":")[-1]
        ok = api_md5 == md5
        sha_ok = relname == "MANIFEST.json" or hashlib.sha256(data).hexdigest() == files[relname]["sha256"]
        results.append((relname, len(data), api_md5, "アップロード", ok and sha_ok))
        print(f"    {relname}: {len(data)/1e6:.1f} MB {'✓' if ok and sha_ok else '⚠不一致'}")
    n_ok = sum(1 for r in results if r[4])
    print(f"[4] 突合: {n_ok}/{len(results)} 一致(md5=API 返却、sha256=MANIFEST)")
    (ROOT / "data/zenodo_upload_report.json").write_text(json.dumps(
        [{"file": a, "bytes": b, "md5": c, "action": d, "ok": e} for a, b, c, d, e in results], ensure_ascii=False, indent=1))
    if n_ok != len(results):
        sys.exit("突合不一致あり — 停止")
    print(f"\n[5] 完了(publish 未実行 — 人間ゲート)")
    print(f"    予約 DOI: {doi}")
    print(f"    ドラフト: https://zenodo.org/uploads/{dep_id}")


if __name__ == "__main__":
    main()
