#!/usr/bin/env python3
"""^report(36): data/runs/*.out (the probe's UNDOSCALE lines) -> data/steps.json.

Each file is one run of Test_UndoScaling: per size, the build, the program's
shape, and four samples each of edit, undo and redo, every sample the step's
ms + the statics refresh's ms, with the work each did
(p: top-level items parsed in full, m: chunks re-measured, c: item heads
compared structurally; before the bar the step's, after it the refresh's).
Files named A* are the build before the two fixes, B* after."""
import json, os, re, statistics, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(HERE, "data", "runs")
SAMPLE = re.compile(r"([\d.]+)\+\s*([\d.]+) ms \(p(\d+) m(\d+) c(\d+) \| p(\d+) m(\d+) c(\d+)\)")
raw = defaultdict(lambda: defaultdict(list))
for f in sorted(os.listdir(RUNS)):
    if not f.endswith(".out"):
        continue
    build = f[0]
    for l in open(os.path.join(RUNS, f)):
        m = re.match(r"UNDOSCALE n=(\d+) (edit|undo|redo): (.*)", l)
        if not m:
            continue
        for i, s in enumerate(SAMPLE.findall(m.group(3))):
            raw[(build, int(m.group(1)), m.group(2))]["samples"].append({
                "run": f, "index": i + 1, "step_ms": float(s[0]), "refresh_ms": float(s[1]),
                "step_work": {"parsed": int(s[2]), "measured": int(s[3]), "compared": int(s[4])},
                "refresh_work": {"parsed": int(s[5]), "measured": int(s[6]), "compared": int(s[7])}})
out = []
for (build, n, kind), v in sorted(raw.items()):
    st = [s["step_ms"] for s in v["samples"]]
    rf = [s["refresh_ms"] for s in v["samples"]]
    out.append({"build": build, "n": n, "kind": kind, "samples_n": len(st),
                "step_median_ms": statistics.median(st), "step_min_ms": min(st), "step_max_ms": max(st),
                "refresh_median_ms": statistics.median(rf),
                "samples": v["samples"]})
json.dump(out, open(os.path.join(HERE, "data", "steps.json"), "w"), indent=1)
for r in out:
    print(f'{r["build"]} n={r["n"]:5d} {r["kind"]}: {r["step_median_ms"]:6.1f} ms (min {r["step_min_ms"]:.0f}, max {r["step_max_ms"]:.0f}) + statics {r["refresh_median_ms"]:.1f}  [{r["samples_n"]}]')

# every raw reading, compactly, into meta.json too, so the page's embedded data
# (tools/report_data.py embeds meta.json) carries them as well as the files do
META = os.path.join(HERE, "data", "meta.json")
meta = json.load(open(META))
meta["readings"] = {f'{r["build"]} {r["n"]} {r["kind"]}': {"step_ms": [s["step_ms"] for s in r["samples"]],
                                                           "refresh_ms": [s["refresh_ms"] for s in r["samples"]],
                                                           "step_work": r["samples"][0]["step_work"]} for r in out}
meta["readings_note"] = "Keys: build (A before the fixes, B after), definitions, step kind. Readings in run order (3 runs x 4 steps); step_work is the first sample's (top-level items parsed in full, layout chunks measured, heads compared)."
meta["profile_3200"] = json.load(open(os.path.join(HERE, "data", "profile_3200.json")))
json.dump(meta, open(META, "w"), indent=1)
