# per size and run: profile time under the probe's `sample`, in disjoint parts, and the run's own step times
import json, re, glob, os, statistics
# run from the folder holding bundle-dev/ (the dev-profile test bundle), prof3-N-R/ (profiles) and out3-N-R.txt
S = os.path.dirname(os.path.abspath(__file__))
JS = open(os.path.join(S, "bundle-dev/haz3ltest.bc.js")).read().split("\n")
mark = re.compile(r"/\*<<((?:src|test)/[^:]+:\d+):\d+>>\*/")
cache = {}
def src_of(line):
    if line not in cache:
        cache[line] = next((m.group(1) for l in JS[line:line + 40] for m in [mark.search(l)] if m), "")
    return cache[line]
GROUPS = [("outline", "of_source", "src/haz3lcore/tiles/Outline.re:290"),
          ("term", "go_incr", "src/haz3lcore/lang/MakeTerm.re:3382"),
          ("statics", "calc", "src/haz3lcore/derived/DefStatics.re:1934"),
          ("layout", "of_segment", "src/haz3lcore/tiles/Measured.re:1568")]
res = []
for n in (400, 800, 1600, 3200, 6400):
    for r in (1, 2):
        p = json.load(open(glob.glob(os.path.join(S, f"prof3-{n}-{r}/*.cpuprofile"))[0]))
        nodes = {x["id"]: x for x in p["nodes"]}
        parent = {c: x["id"] for x in p["nodes"] for c in x.get("children", [])}
        def nm(x):
            cf = x["callFrame"]
            return (cf["functionName"], src_of(cf["lineNumber"]) if cf["url"].endswith("haz3ltest.bc.js") else "")
        sc = {}
        def stack(k):
            if k not in sc:
                s, j = [], k
                while j in nodes: s.append(nm(nodes[j])); j = parent.get(j)
                sc[k] = s
            return sc[k]
        tot, g = 0.0, {k: 0.0 for k, _, _ in GROUPS}
        d = p["timeDeltas"]
        for i, sid in enumerate(p["samples"]):
            dt = d[i + 1] / 1000 if i + 1 < len(d) else 0
            s = stack(sid)
            if not any(fn == "sample" and src == "" for fn, src in s): continue
            tot += dt
            for k, fn0, src0 in GROUPS:
                if any(fn == fn0 and src == src0 for fn, src in s): g[k] += dt
        txt = open(os.path.join(S, f"out3-{n}-{r}.txt")).read()
        kinds = {k: [(float(a), float(b)) for a, b in re.findall(r"([\d.]+)\+\s*([\d.]+) ms", re.search(rf"UNDOSCALE n={n} {k}: (.*)", txt).group(1))]
                 for k in ("edit", "undo", "redo")}
        measured = sum(a + b for xs in kinds.values() for a, b in xs)
        ud = sum(a for k in ("undo", "redo") for a, b in kinds[k])
        row = {"n": n, "run": r, "profile_ms": round(tot), "parts_ms": {k: round(v) for k, v in g.items()}, "measured_ms": measured,
               "steps_ms": {k: [a for a, b in xs] for k, xs in kinds.items()}, "refresh_ms": {k: [b for a, b in xs] for k, xs in kinds.items()},
               "outline_share_of_undo_redo": round(g["outline"] * measured / tot / ud, 4) if tot else None}
        res.append(row)
        print(n, r, "prof", row["profile_ms"], "meas", measured, row["parts_ms"], "ol share of undo+redo steps %.3f" % row["outline_share_of_undo_redo"],
              "med e/u/r", [statistics.median(row["steps_ms"][k]) for k in ("edit", "undo", "redo")])
json.dump(res, open(os.path.join(S, "split3.json"), "w"), indent=1)
