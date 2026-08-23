#!/usr/bin/env python3
"""Phase 0.1(b): BL 公開アーカイブの HIP 目標を gaiadr3.hipparcos2_best_neighbour で DR3 source_id に照合。"""
import json, re, os, urllib.request, urllib.parse, time
RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
targets = json.load(open(os.path.join(RAW, "bl_targets.json")))
hips = sorted({int(t[3:]) for t in targets if re.match(r"^HIP\d+$", t)})
print("HIP targets", len(hips))
out = {}
TAP = "https://gea.esac.esa.int/tap-server/tap/sync"
for i in range(0, len(hips), 400):
    chunk = hips[i:i+400]
    q = ("SELECT original_ext_source_id AS hip, source_id, angular_distance, number_of_neighbours, xm_flag "
         "FROM gaiadr3.hipparcos2_best_neighbour WHERE original_ext_source_id IN (%s)" % ",".join(map(str, chunk)))
    for attempt in range(3):
        try:
            data = urllib.parse.urlencode({"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": q}).encode()
            with urllib.request.urlopen(TAP, data=data, timeout=180) as r:
                txt = r.read().decode()
            break
        except Exception as e:
            print("retry", i, e); time.sleep(5)
    lines = txt.strip().splitlines()[1:]
    for ln in lines:
        hip, sid, ang, nn, flag = ln.split(",")
        out[int(hip)] = {"source_id": int(sid), "angular_distance": float(ang), "n_neighbours": int(nn), "xm_flag": int(flag)}
    print(i, len(out), flush=True)
json.dump({"n_hip_targets": len(hips), "n_matched": len(out), "map": out}, open(os.path.join(RAW, "..", "phase0", "bl_hip_to_dr3.json"), "w"))
print("matched", len(out), "of", len(hips), "=%.2f%%" % (100 * len(out) / len(hips)))
