# per kind of step (edit, undo, redo): profile time in the step itself (not its statics refresh), by source function
import json, re, glob, os, sys, collections
S = os.path.dirname(os.path.abspath(__file__))
JS = open(os.path.join(S, "bundle-kinds.bc.js")).read().split("\n")
mark = re.compile(r"/\*<<((?:src|test)/[^:]+:\d+):\d+>>\*/")
cache = {}
def src_of(line):
    if line not in cache:
        cache[line] = next((m.group(1) for l in JS[line:line + 40] for m in [mark.search(l)] if m), "")
    return cache[line]
res = {}
for n in (400, 800, 1600, 3200, 6400):
  for r in (1, 2):
    p = json.load(open(glob.glob(os.path.join(S, f"prof4-{n}-{r}/*.cpuprofile"))[0]))
    nodes = {x["id"]: x for x in p["nodes"]}
    parent = {c: x["id"] for x in p["nodes"] for c in x.get("children", [])}
    def nm(x):
        cf = x["callFrame"]; s = src_of(cf["lineNumber"]) if cf["url"].endswith(".bc.js") else ""
        return f'{cf["functionName"] or "(anon)"} @{s}' if s else cf["functionName"] or "(anon)"
    sc = {}
    def stack(k):
        if k not in sc:
            s, j = [], k
            while j in nodes: s.append(nm(nodes[j])); j = parent.get(j)
            sc[k] = s
        return sc[k]
    d = p["timeDeltas"]
    tot = collections.Counter(); incl = {k: collections.Counter() for k in ("edit", "undo", "redo")}
    for i, sid in enumerate(p["samples"]):
        dt = d[i + 1] / 1000 if i + 1 < len(d) else 0
        st = stack(sid)
        kind = next((f[7:] for f in st if f in ("sample_edit", "sample_undo", "sample_redo")), None)
        if not kind or "refresh" in st: continue
        tot[kind] += dt
        for f in set(st):
            if "@src/" in f: incl[kind][f] += dt
    res[(n, r)] = (tot, incl)
    print(n, r, {k: round(v) for k, v in tot.items()})

OL = "of_source @src/haz3lcore/tiles/Outline.re:290"
import json
summary = {}
for n in (400, 800, 1600, 3200, 6400):
    T = collections.Counter(); I = {k: collections.Counter() for k in ("edit", "undo", "redo")}
    for r in (1, 2):
        tot, incl = res[(n, r)]; T.update(tot)
        for k in I: I[k].update(incl[k])
    summary[n] = {k: {"step_ms": round(T[k]), "outline_ms": round(I[k][OL])} for k in I}
    print(n, summary[n], "outline share of undo %.3f, of redo %.3f" % (I["undo"][OL] / T["undo"], I["redo"][OL] / T["redo"]))
    if n in (3200, 6400):
        R = I["redo"].copy(); E = I["edit"]
        diff = sorted(((R[f] - E[f], f, R[f], E[f]) for f in set(R) | set(E) if "Outline.re" not in f and "EntryPath" not in f), reverse=True)
        print("  redo minus edit, outline aside: total redo %.0f edit %.0f" % (T["redo"] - I["redo"][OL], T["edit"]))
        for dd, f, a, b in diff[:14]: print(f"  {dd:7.0f} redo {a:6.0f} edit {b:6.0f}  {f}")
json.dump(summary, open(os.path.join(S, "kinds_summary.json"), "w"), indent=1)
