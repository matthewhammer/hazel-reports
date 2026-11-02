# rank a node .cpuprofile's functions by self and inclusive time, optionally only
# within samples whose stack passes through a function matching --under
#   python3 prof.py <file.cpuprofile> [--under REGEX] [--top N]
import json, re, sys
from collections import defaultdict

path = sys.argv[1]
under = re.compile(sys.argv[sys.argv.index("--under") + 1]) if "--under" in sys.argv else None
top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 40
p = json.load(open(path))
nodes = {n["id"]: n for n in p["nodes"]}
parent = {}
for n in p["nodes"]:
    for c in n.get("children", []):
        parent[c] = n["id"]

import os
JS = os.environ.get("BCJS")
js_lines = open(JS).read().split("\n") if JS else None
mark = re.compile(r"/\*<<((?:src|test)/[^:]+:\d+):\d+>>\*/")
src_cache = {}
def src_of(line):
    if js_lines is None: return None
    if line in src_cache: return src_cache[line]
    r = None
    for l in js_lines[line:line + 40]:
        m = mark.search(l)
        if m: r = m.group(1); break
    src_cache[line] = r
    return r
def name(n):
    cf = n["callFrame"]
    f = cf["functionName"] or "(anon)"
    if cf["url"].endswith("haz3ltest.bc.js"):
        s = src_of(cf["lineNumber"])
        if s: return f"{f} @{s}"
    return f"{f} {cf['url'].rsplit('/', 1)[-1]}:{cf['lineNumber'] + 1}"

stack_cache = {}
def stack(nid):
    if nid in stack_cache:
        return stack_cache[nid]
    s, k = [], nid
    while k in nodes:
        s.append(name(nodes[k]))
        k = parent.get(k)
    stack_cache[nid] = s
    return s

self_t, incl_t = defaultdict(float), defaultdict(float)
total = 0.0
deltas = p["timeDeltas"]
for i, sid in enumerate(p["samples"]):
    dt = deltas[i + 1] / 1000 if i + 1 < len(deltas) else 0
    st = stack(sid)
    if under and not any(under.search(f) for f in st):
        continue
    total += dt
    self_t[st[0]] += dt
    for f in set(st):
        incl_t[f] += dt
print(f"total {total:.0f} ms" + (f" under /{under.pattern}/" if under else ""))
print("-- inclusive")
for f, t in sorted(((f, t) for f, t in incl_t.items() if "@src/" in f and "caml_call" not in f), key=lambda x: -x[1])[:top]:
    print(f"{t:9.0f} ms {100 * t / total:5.1f}%  {f}")
print("-- self")
for f, t in sorted(self_t.items(), key=lambda x: -x[1])[:top]:
    print(f"{t:9.0f} ms {100 * t / total:5.1f}%  {f}")
