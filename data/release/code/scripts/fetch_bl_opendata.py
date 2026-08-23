#!/usr/bin/env python3
"""Phase 0.1(a): Breakthrough Listen 公開アーカイブ(seti.berkeley.edu/opendata)の
観測ファイルメタデータを HIP 目標ごとに取得し、data/raw/bl_opendata/<target>.json に保存する。
取得欄: target, telescope, center_freq(MHz), mjd, utc, ra, decl, file_type, quality, url, size, md5sum。
並列 8(Phase 0 当初 4、裁定 #1 執行時に増速)、失敗は 3 回まで再試行し、失敗リストを data/raw/bl_opendata/_failed.txt に残す。
"""
import json, os, re, sys, time, urllib.request, urllib.parse, concurrent.futures as cf

API = "http://seti.berkeley.edu/opendata/api/query-files?limit=2000&target={}"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "bl_opendata")
os.makedirs(OUT, exist_ok=True)

def fetch(target):
    path = os.path.join(OUT, target + ".json")
    if os.path.exists(path):
        return target, "cached"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(API.format(urllib.parse.quote(target)), timeout=120) as r:
                d = json.loads(r.read().decode())
            if d.get("result") == "error":
                return target, "error:" + d.get("message", "")
            json.dump(d, open(path, "w"))
            return target, "ok:%d" % len(d.get("data", []))
        except Exception as e:
            err = repr(e); time.sleep(3 * (attempt + 1))
    return target, "fail:" + err

if __name__ == "__main__":
    targets = json.load(open(os.path.join(OUT, "..", "bl_targets.json")))
    pat = re.compile(r"^(HIP\d+|GJ[0-9A-Za-z]+|LHS\d+|LTT\d+|TIC\d+|HD\d+|TRAPPIST.*|PROXIMA.*|ALPHACEN.*|BARNARD.*|WOLF\d+|ROSS\d+|TOI\d+)$", re.I)
    sel = [t for t in targets if pat.match(t)]
    print("selected", len(sel), "of", len(targets), flush=True)
    failed = []
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for i, (t, st) in enumerate(ex.map(fetch, sel)):
            if st.startswith("fail") or st.startswith("error"):
                failed.append(t + "\t" + st)
            if i % 200 == 0:
                print(i, t, st, "%.0fs" % (time.time() - t0), flush=True)
    open(os.path.join(OUT, "_failed.txt"), "w").write("\n".join(failed))
    print("done; failed", len(failed), "%.0fs" % (time.time() - t0))
