#!/usr/bin/env python3
"""^report(68): reads a log of hazeljs-examples' 'world speed run, frame by frame' job (node/world-frames.mjs) into JSON:
each setup's frames (gap quantiles, counts over 16.7/33/50/100/200 ms), steps, drawing, parts, the sampled thread, and the
worst frames. The logs are read with `gh run view --log` (no artifact downloaded).  python3 parse_frames.py RUN"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
def num(x): return float(x.replace(",", ""))
def parts(s):   # "a 1.2% · b 3%" -> {a: 1.2, b: 3}
    out = {}
    for it in s.split(" · "):
        m = re.match(r"(.+?) ([\d.]+)%$", it.strip())
        if m: out[m.group(1)] = float(m.group(2))
    return out
def parse(path):
    setups, cur = {}, None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        m = re.match(r"== ([\w.\-]+): (\d+)×(\d+) CSS px at (\d)x \(canvas (\d+)×(\d+), a tile (\d+) px\)(.*)", line)
        if m:
            cur = {"name": m.group(1), "css": [int(m.group(2)), int(m.group(3))], "dpr": int(m.group(4)), "canvas": [int(m.group(5)), int(m.group(6))], "tile": int(m.group(7)), "head": m.group(8).strip(), "worst": [], "phases": {}}
            c = re.search(r"CPU (\d)x", line); cur["cpu"] = int(c.group(1)) if c else 1
            setups[cur["name"]] = cur; continue
        if not cur: continue
        L = line.strip()
        if m := re.match(r"[\w.\-]+: (\d+) frames recorded; the run: things (\S+), tree parts (\S+), gems (\S+), at phase ([^;\s]+)(?:; its time (\S+), real ([\d.]+) s)?", L):
            cur.update(frames=int(m.group(1)), things=m.group(2), parts=m.group(3), gems=m.group(4), atPhase=m.group(5), runTime=m.group(6), realS=float(m.group(7)) if m.group(7) else None)
        elif m := re.match(r"frame gap: median ([\d.]+) ms \(([\d.]+) fps\), p90 ([\d.]+), p99 ([\d.]+), worst ([\d.]+); over 16.7 ms (\d+) of (\d+), over 33 (\d+), over 50 (\d+), over 100 (\d+), over 200 (\d+)", L):
            g = [float(m.group(i)) for i in range(1, 6)]; o = [int(m.group(i)) for i in range(6, 12)]
            cur["gap"] = {"median": g[0], "fps": g[1], "p90": g[2], "p99": g[3], "worst": g[4]}; cur["over"] = {"16.7": o[0], "n": o[1], "33": o[2], "50": o[3], "100": o[4], "200": o[5]}
        elif m := re.match(r"the steps' budget a frame: (?:median ([\d.]+) ms, from ([\d.]+) to ([\d.]+)|fixed.*?); pictures painted (\d+), put off to a later frame (\d+)", L):
            cur["budget"] = {"median": float(m.group(1)), "min": float(m.group(2)), "max": float(m.group(3))} if m.group(1) else None
            cur["painted"] = int(m.group(4)); cur["putOff"] = int(m.group(5))
        elif m := re.match(r"a frame's steps: median ([\d.]+) ms \((\d+) steps\), the slowest step in a frame: median ([\d.]+) ms, p99 ([\d.]+), worst ([\d.]+); drawing: median ([\d.]+) ms, p99 ([\d.]+), worst ([\d.]+)", L):
            v = [float(m.group(i)) for i in range(1, 9)]
            cur["steps"] = {"median": v[0], "n": v[1], "slowestMedian": v[2], "slowestP99": v[3], "slowestWorst": v[4]}; cur["drawing"] = {"median": v[5], "p99": v[6], "worst": v[7]}
        elif m := re.match(r"phase (\S+): (\d+) frames, gap median ([\d.]+) ms, p99 ([\d.]+), worst ([\d.]+); steps a frame (\d+), drawing median ([\d.]+) ms", L):
            cur["phases"][m.group(1)] = {"frames": int(m.group(2)), "median": float(m.group(3)), "p99": float(m.group(4)), "worst": float(m.group(5)), "steps": int(m.group(6)), "drawing": float(m.group(7))}
        elif m := re.match(r"the steps' time by part \(⏱, whole run, ([\d.]+) s\): (.*)", L): cur["stepsS"] = float(m.group(1)); cur["stepParts"] = parts(m.group(2))
        elif m := re.match(r"the drawing by part \(whole run, ([\d.]+) s\): (.*)", L): cur["drawS"] = float(m.group(1)); cur["drawParts"] = parts(m.group(2))
        elif m := re.match(r"the page's thread, sampled \(([\d.]+) s busy; idle left out\): (.*)", L): cur["busyS"] = float(m.group(1)); cur["kinds"] = parts(m.group(2))
        elif m := re.match(r"its top functions, self time: (.*)", L): cur["top"] = parts(m.group(1))
        elif m := re.match(r"([\d.]+) ms at ([\d.]+) s, (\S+): (\d+) steps ([\d.]+) \(slowest ([\d.]+)(?:: ([^)]*))?\); drawing ([\d.]+)(?: \(([^)]*)\))?(?:; sampled: (.*))?$", L):
            def kv(s):   # "birds, frogs, bugs 0.1, water 0.5" -> {"birds, frogs, bugs": 0.1, "water": 0.5}: names may hold ", "
                out, acc = {}, []
                for tok in (s.split(", ") if s else []):
                    acc.append(tok); mm = re.match(r"(.*) ([\d.]+)$", tok)
                    if mm: out[", ".join(acc[:-1] + [mm.group(1)])] = float(mm.group(2)); acc = []
                return out
            cur["worst"].append({"span": float(m.group(1)), "at": float(m.group(2)), "phase": m.group(3), "steps": int(m.group(4)), "stepsMs": float(m.group(5)), "slowest": float(m.group(6)), "slowestParts": kv(m.group(7)),
                                 "draw": float(m.group(8)), "drawParts": kv(m.group(9)), "sampled": m.group(10) or ""})
        elif m := re.match(r"([\d.]+) ms at ([\d.]+) s(?:: (.*))?$", L):
            cur["worst"].append({"span": float(m.group(1)), "at": float(m.group(2)), "sampled": m.group(3) or ""})
    return setups
if __name__ == "__main__":
    run = sys.argv[1]; S = parse(os.path.join(HERE, "data", f"frames-{run}.log"))
    json.dump({"run": run, "setups": S}, open(os.path.join(HERE, "data", f"frames-{run}.json"), "w"), indent=1, ensure_ascii=False)
    for k, v in S.items(): print(k, v.get("gap"), v.get("over"), v.get("steps"), v.get("drawing"), len(v["worst"]))
