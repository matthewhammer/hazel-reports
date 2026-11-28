#!/usr/bin/env python3
"""^report(68): the sizes of Gnome world's code, Hazel's against JavaScript's, at a commit of hazeljs-examples.
Hazel: world/rules/*.hz, characters with comments (# ... #) taken out, and lines that are not blank or comment only.
JavaScript: world/app.js's top-level definitions (two spaces in, inside its one function), grouped by name; world/plain.js
(the ⚡ twin of the rules); the shared scripts the page loads. Writes data/sizes.json."""
import json, os, re, subprocess, sys
REPO = os.path.expanduser("~/hazeljs-examples"); HERE = os.path.dirname(os.path.abspath(__file__))
rev = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
def show(p): return subprocess.run(["git", "-C", REPO, "show", f"{rev}:{p}"], capture_output=True, text=True, check=True).stdout
def ls(d): return subprocess.run(["git", "-C", REPO, "ls-tree", "--name-only", f"{rev}", d + "/"], capture_output=True, text=True, check=True).stdout.split()
sha = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", rev], capture_output=True, text=True).stdout.strip()
def strip_hz(t):
    out, i, n = [], 0, len(t)
    in_str = False
    while i < n:
        ch = t[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n: out.append(t[i + 1]); i += 2; continue
            if ch == '"': in_str = False
            i += 1; continue
        if ch == '"': in_str = True; out.append(ch); i += 1; continue
        if ch == "#":
            j = t.find("#", i + 1); nl = t.find("\n", i + 1)
            # a comment runs to its closing # on the same line, or to the line's end
            end = j if (j != -1 and (nl == -1 or j < nl)) else (nl if nl != -1 else n)
            i = end + 1 if end == j else end; continue
        out.append(ch); i += 1
    return "".join(out)
hz = {}
for p in ls("world/rules"):
    if not p.endswith(".hz"): continue
    t = show(p); s = strip_hz(t)
    code = "\n".join(l.rstrip() for l in s.splitlines() if l.strip())
    hz[os.path.basename(p)[:-3]] = {"chars": len(code), "lines": len(code.splitlines()), "raw": len(t)}
app = show("world/app.js")
# top-level definitions of app.js: lines at two spaces in that begin a function, const, let or class
starts = [m.start() for m in re.finditer(r"(?m)^  (?:async )?(?:function\*? |const |let |class )", app)] + [len(app)]
defs = []
for a, b in zip(starts, starts[1:]):
    chunk = app[a:b]; m = re.match(r"  (?:async )?(?:function\*? |const |let |class )\s*\{?\s*([A-Za-z_$][\w$]*)", chunk)
    defs.append((m.group(1) if m else "?", len(chunk)))
head = starts[0]
def cat(name):
    if re.search(r"JS$", name) or name in ("pickupJS",): return "JavaScript twins of Hazel's pieces"
    if re.match(r"(bot|dig(Chunk|Count|Rand|Can|_C)|DIG_|BOT|KIT|ITEM|runTime|timeSpeedRun|tp[A-Z])", name): return "the speed run"
    if re.match(r"(draw|paint|sprite|Sprite|SPRITE|strip|layer|minimap|map|lineCtx|lineScene|cloud|sky|SKY|RAINBOW|PARTY|LEAF|COLOR|MAPCOL|leafy|bush|bird[A-Z]|BIRD|gnome|squirrelBody|rabbit|RABBIT|tile|Tile|HEADTOP|gemCompass|darkCv|darkData|cv$|realCtx|T$|VW|VH|light|glow|shade|CANVAS|newCanvas|dropCanvas|purge|root(Chunks|Chunk)|RCH|dirtyRoots|spray|rainbowBurst|popWord|PERF|pmark|timedDraw|frame$|acc$)", name): return "drawing"
    if re.match(r"(save|load|keep|kept|snapshot|restore|digest|readSave|mergeText|b64|resume|KEEP|gzip|pack|unpack)", name, re.I): return "save and load"
    if re.match(r"(build|plan|hand|lowered|place|village|house|lodge|tree[A-Z]|grow|shapeSurface|landY|surf|topOf|carve|cave|pod|coins?$)", name): return "building the world"
    if re.match(r"(tick|.*Step$|step|water|wake|near|code|digOut|digSteps|dropStones|hurt|pickups|catHead|gemFound|gemAim|powerNote|BOTH|CAT_TAIL|TP$|tmark|vortex|travel|ride|carpet|tail|jelly|fly|use(Ride)?|mount|clover|music|song|swim)", name, re.I): return "simulation"
    return "rules, input, sound, setup and the rest"
by = {}
for n, c in defs: k = cat(n); by[k] = by.get(k, 0) + c
by["rules, input, sound, setup and the rest"] = by.get("rules, input, sound, setup and the rest", 0) + head
shared = {}
for p in ["world/plain.js", "dig/sound.js", "shared/chip.js", "shared/fullscreen.js", "shared/advanced.js", "shared/offline.js", "shared/pause.js", "shared/divider.js", "shared/volume.js"]:
    try: shared[p] = len(show(p))
    except subprocess.CalledProcessError: pass
out = {"at": sha, "hz": hz, "hz_total": sum(v["chars"] for v in hz.values()), "hz_lines": sum(v["lines"] for v in hz.values()),
       "app_js": len(app), "app_js_lines": app.count("\n"), "app_defs": len(defs), "app_by": dict(sorted(by.items(), key=lambda kv: -kv[1])), "shared": shared,
       "twins": {n: c for n, c in defs if cat(n) == "JavaScript twins of Hazel's pieces"}}
json.dump(out, open(os.path.join(HERE, "data/sizes.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ("at", "hz_total", "hz_lines", "app_js", "app_js_lines", "app_defs", "app_by")}, indent=1))
print("hz:", {k: v["chars"] for k, v in hz.items()})
print("twins:", out["twins"]); print("shared:", shared)
