#!/usr/bin/env python3
"""^report(67): Hazel as an npm Package, Then and Now. Asked 2026-11-27: "the same questions and charts as ^report(63), reflecting
the current JIT technology". ^report(63)'s structure, generator and figures (063/gen063.py), each chart redrawn with today's data
next to 063's.

Writes 067/index.html from body.html and:
  then: ../063/data (063's own runs: package bench 45247119864, 45424324608, 45452623490, 45459402709; diff.json; prs.json)
  now:  data/threeway.json  hazeljs-examples' three-way timing, run 46013126145 (parsed from its log; no artifact downloaded)
        ../065/data/games-4way  ^report(65)'s four ways on each game's own run (bench/4way, run 45666570615, library 2c4a61560f)
        ../065/data/tables.json ^report(65)'s crossing over time (the jit against compiled.js, build by build)
        data/world.json       Gnome world: build timing 46023240545, World.step 46025727949, speed run 46027689744, ^report(64) #fresh
        ../064/data/now.json  Gnome world's pieces against their JavaScript twins (^report(64))
        data/diff.json, data/prs.json  the hazeljs branch against dev, and the PRs, as git and GitHub had them on 2026-11-27"""
import html, json, math, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")
THEN = os.path.join(ROOT, "063", "data")
R65 = os.path.join(ROOT, "065", "data")
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
esc = lambda s: html.escape(str(s), quote=True)
gm = lambda xs: math.exp(sum(map(math.log, xs)) / len(xs))

GROUPS = [("Oracles", ["i-ching", "tarot", "astrology"]),
          ("Board and card games, each with a plain JavaScript version", ["checkers", "go", "minesweeper", "mahjong", "solitaire"]),
          ("A puzzle", ["mahjong-solitaire"]),
          ("Arcade games, a step at a time", ["pinball", "downhill", "bricks", "snake", "trails", "starwave", "bugs", "dig"])]
NAME = {"i-ching": "I Ching", "tarot": "Tarot", "astrology": "Astrology", "checkers": "Checkers", "go": "Go", "minesweeper": "Minesweeper",
        "mahjong": "Mahjong", "solitaire": "Solitaire", "mahjong-solitaire": "Mahjong solitaire", "pinball": "Pinball", "downhill": "Downhill",
        "bricks": "Bricks", "snake": "Snake", "trails": "Light trails", "starwave": "Star wave", "bugs": "Butterfly garden", "dig": "Gnome dig"}
ORDER = [g for _, gs in GROUPS for g in gs]

# ================= then: ^report(63)'s data, as 063/gen063.py reads it =================
G = {g: json.load(open(os.path.join(THEN, f"{g}.json"))) for g in ORDER}
WAYS = ["interpreted", "jit", "compiled", "plain JS"]
OPS = []   # (game, op name, {way: ms}) build 1 to 4
for g in ORDER:
    for o in G[g]["ops"]:
        assert all(r is None or (r.get("same") and "ms" in r) for r in o["ways"].values()), (g, o["name"])
        OPS.append((g, o["name"], {w: r["ms"] for w, r in o["ways"].items() if r}))
ratio = lambda a, b: [o[2][a] / o[2][b] for o in OPS if a in o[2] and b in o[2]]
share = lambda o: max(0.0, (o[2]["jit"] - o[2]["compiled"]) / o[2]["jit"])
LIGHT = [o for o in OPS if share(o) >= 0.5]
CV = {g: json.load(open(os.path.join(THEN, "conv", f"{g}.json"))) for g in ORDER}
CONV = []
for g in ORDER:
    old = {o["name"]: {w: r["ms"] for w, r in o["ways"].items() if r} for o in G[g]["ops"]}
    for o in CV[g]["ops"]:
        CONV.append((g, o["name"], old[o["name"]], {w: r["ms"] for w, r in o["ways"].items() if r}))
RUNS5 = {}   # game -> (run name, steps, {way: record}) build 5, run 45452623490
for g in ORDER:
    f = os.path.join(THEN, "runs", f"{g}-runs.json")
    if os.path.exists(f):
        r = json.load(open(f))["runs"][0]; RUNS5[g] = (r["name"], r["steps"], {w: v for w, v in r["ways"].items() if v})
RUNS6 = {g: {w: v for w, v in json.load(open(os.path.join(THEN, "runs-links", f"{g}-runs.json")))["runs"][0]["ways"].items() if v}
         for g in ORDER if os.path.exists(os.path.join(THEN, "runs-links", f"{g}-runs.json"))}
RG = [g for g in ORDER if g in RUNS5]   # the 14 games with runs
ja5 = {g: RUNS5[g][2]["jit"]["usPerCall"] / RUNS5[g][2]["compiled"]["usPerCall"] for g in RG}
ja6 = {g: RUNS6[g]["jit"]["usPerCall"] / RUNS6[g]["compiled"]["usPerCall"] for g in RG}

# ================= now =================
# ^report(65)'s four ways (hazeljs-examples bench/4way, run 45666570615, 2026-11-25): the library of hazelgrove/hazel 2c4a61560f,
# the very build hazeljs 0.0.14 ships; each game's own run of states; "compiled" is the game's own compiled.js as it ships
F4 = {}
for g in RG:
    d = json.load(open(os.path.join(R65, "games-4way", f"b4way-{g}", f"{g}-4way.json")))
    r = d["runs"][0]
    assert all(v is None or v.get("same") for v in r["ways"].values()), g
    assert d["package"]["build"].startswith("2c4a61560f"), g
    F4[g] = {"name": r["name"], "steps": r["steps"], "ways": {w: v for w, v in r["ways"].items() if v}, "once": d["once"], "machine": d["machine"]}
jan = {g: F4[g]["ways"]["jit"]["usPerCall"] / F4[g]["ways"]["compiled"]["usPerCall"] for g in RG}
fw = lambda g, w: F4[g]["ways"][w]["usPerCall"]
# ^report(65)'s crossing over time: the jit's time a call over compiled.js's, geometric mean over the 14 games' runs
CT = next(s for s in json.load(open(os.path.join(R65, "tables.json"))) if s["section_id"] == "crossing-time")["rows"]
# the three-way job (run 46013126145): five games, every operation, hazeljs 0.0.4 interpreting, each game's compiled.js, plain.js
TW = json.load(open(os.path.join(DATA, "threeway.json")))
TWG = {d["game"]: d for d in TW["games"]}
TW_ORDER = ["checkers", "go", "minesweeper", "mahjong", "solitaire"]
TOPS = [(g, o["name"], o["ways"]) for g in TW_ORDER for o in TWG[g]["ops"]]
TWHOLE = [(g, o["name"], o["ways"], o.get("moves")) for g in TW_ORDER for o in TWG[g]["whole"]]
HJ, NB, PN, HZ, PJ = "hazel-jit", "hazel-jit, no step budget", "hazel-jit, no budget, plain numbers", "hazeljs", "plain JS"
tr = lambda a, b, rows=TOPS: [w[a] / w[b] for _, _, w, *_ in rows if w.get(a) and w.get(b)]
W = json.load(open(os.path.join(DATA, "world.json")))
N64 = json.load(open(os.path.join(ROOT, "064", "data", "now.json")))
# the branch against dev, then and now
D63, D67 = json.load(open(os.path.join(THEN, "diff.json"))), json.load(open(os.path.join(DATA, "diff.json")))
P63 = {p["number"]: p for p in json.load(open(os.path.join(THEN, "prs.json")))["prs"] if "headRefName" in p}
P67 = {p["number"]: p for p in json.load(open(os.path.join(DATA, "prs.json")))["prs"]}

def t(ms):
    """a time as people read it"""
    if ms >= 1000: return f"{ms / 1000:.1f} s"
    if ms >= 10: return f"{ms:.0f} ms"
    if ms >= 1: return f"{ms:.1f} ms"
    if ms >= 0.1: return f"{ms:.2f} ms"
    us = ms * 1000
    if us >= 10: return f"{us:.0f} µs"
    if us >= 1: return f"{us:.1f} µs"
    return f"{us * 1000:.0f} ns"
def x_(r): return f"{r:,.0f}×" if r >= 10 else f"{r:.1f}×"
def x2(r): return f"{r:.2f}×"
def rng(a, b, f="{:.2f}"):
    a, b = a + 1e-9, b + 1e-9   # half up, as the logs print them (2.465 is 2.47)
    return f.format(a) if f.format(a) == f.format(b) else f"{f.format(a)}–{f.format(b)}"
def fps(ms): return f"{t(ms)} (about {1000 / ms:,.0f} fps)"
def legend(items, x, y):
    out = []
    for words, cls in items:
        out.append(f'<circle class="{cls}" cx="{x + 4:.1f}" cy="{y}" r="4.2"/><text class="mut" x="{x + 12:.1f}" y="{y + 4}">{esc(words)}</text>')
        x += 12 + 7.2 * len(words) + 22
    return out
def bar_key(items, x, y):
    out = []
    for words, cls in items:
        out.append(f'<rect class="{cls}" x="{x}" y="{y - 5}" width="10" height="10"/><text class="mut" x="{x + 14}" y="{y + 4}">{esc(words)}</text>')
        x += 14 + 7.2 * len(words) + 18
    return out
kb = lambda b: f"{b / 1024:.0f} kB"
cut = lambda s, n=44: s if len(s) <= n else s[:n - 2] + "…"

# ---- figure: the package's ways to run Hazel from a page, 0.0.14
def paths_svg():
    W_ = 640
    boxes = [("interpreted", "hazel-lib.js, 2.9 MB (2,904,682 bytes)", "Hazel.run, runProgram: the interpreter runs the program", "the interpreter as in 0.0.11; a fix at its boundary waits (ticket 896)"),
             ("jit", "hazel-lib.js, the same file", "Hazel.jit, jitProgram: compiled to JavaScript in the page", "since 0.0.11: converters by type, records as objects, loops"),
             ("compiled", "compiled.js, or Gnome world's rules-aot.json", "Hazel.compileProgram, once, ahead of time: no build in the page", "Gnome world 0.0.147: its rules made from text in 188 ms"),
             ("editor", "editor/, 11 MB", "Hazel's own editor, framed by hazel-listings.js", "offline: its fonts and icons in the package")]
    out = ['<rect class="pbox" x="8" y="118" width="120" height="70" rx="8"/><text class="lbl" x="68" y="150" text-anchor="middle">a page</text>'
           '<text class="mut" x="68" y="168" text-anchor="middle">import "hazeljs"</text>']
    for i, (k, f, what, note) in enumerate(boxes):
        y = 10 + i * 76
        out.append(f'<path class="arrow" d="M128 153 C 170 153, 170 {y + 32}, 208 {y + 32}"/>'
                   f'<rect class="pbox {k}" x="210" y="{y}" width="420" height="64" rx="8"/>'
                   f'<text class="lbl" x="222" y="{y + 20}">{esc(f)}</text><text class="mut" x="222" y="{y + 38}">{esc(what)}</text>'
                   f'<text class="mut" x="222" y="{y + 55}">{esc(note)}</text>')
    return f'<svg viewBox="0 0 {W_} 316" role="img" aria-label="Four ways a page uses hazeljs 0.0.14: the interpreter, the jit, code compiled ahead of time, and the editor">' + "".join(out) + "</svg>"

# ---- figure (then, 063's): every operation, four ways, on one log scale
def ways_then_svg():
    W_, x0, x1 = 640, 262, 628
    lo, hi = -5, 5
    X = lambda ms: x0 + (math.log10(ms) - lo) / (hi - lo) * (x1 - x0)
    out, y = [], 26
    ticks = [(-5, "10 ns"), (-3, "1 µs"), (-1, "0.1 ms"), (1, "10 ms"), (3, "1 s"), (5, "100 s")]
    for e, lab in ticks: out.append(f'<text class="mut" x="{X(10 ** e):.1f}" y="14" text-anchor="{"end" if e == hi else "middle"}">{lab}</text>')
    top = y
    for title, gs in GROUPS:
        y += 6; out.append(f'<text class="grp" x="8" y="{y + 12}">{esc(title)}</text>'); y += 18
        for g, name, ms in [o for o in OPS if o[0] in gs]:
            vs = [ms[w] for w in WAYS if w in ms]
            out.append(f'<text class="lbl small" x="8" y="{y + 10}">{esc(cut(f"{NAME[g]}: {name}"))}</text>'
                       f'<line class="span" x1="{X(min(vs)):.1f}" y1="{y + 6}" x2="{X(max(vs)):.1f}" y2="{y + 6}"/>')
            for w, cls in (("interpreted", "mi"), ("jit", "mj"), ("compiled", "mc"), ("plain JS", "mp")):
                if w in ms:
                    out.append(f'<circle class="{cls}" cx="{X(ms[w]):.1f}" cy="{y + 6}" r="4.2"><title>{esc(NAME[g])}, {esc(name)}: {w} {t(ms[w])}</title></circle>')
            y += 15
    for e, _ in ticks: out.insert(0, f'<line class="grid" x1="{X(10 ** e):.1f}" y1="{top - 6}" x2="{X(10 ** e):.1f}" y2="{y}"/>')
    y += 10
    out += legend([("interpreted", "mi"), ("jit", "mj"), ("compiled ahead of time", "mc"), ("plain JS", "mp")], 12, y)
    return f'<svg viewBox="0 0 {W_} {y + 12}" role="img" aria-label="Then: every operation of the 17 games, timed four ways on 2026-11-23">' + "".join(out) + "</svg>"

# ---- figure (now): the three-way job's operations and whole games, five games
def ways_now_svg():
    W_, x0, x1 = 640, 262, 628
    lo, hi = -5, 5
    X = lambda ms: x0 + (math.log10(ms) - lo) / (hi - lo) * (x1 - x0)
    out, y = [], 26
    ticks = [(-5, "10 ns"), (-3, "1 µs"), (-1, "0.1 ms"), (1, "10 ms"), (3, "1 s"), (5, "100 s")]
    for e, lab in ticks: out.append(f'<text class="mut" x="{X(10 ** e):.1f}" y="14" text-anchor="{"end" if e == hi else "middle"}">{lab}</text>')
    top = y
    marks = ((HZ, "mi", "hazeljs 0.0.4"), (HJ, "mc", "compiled.js"), (PN, "mcn", "compiled.js, no budget, plain numbers"), (PJ, "mp", "plain JS"))
    for g in TW_ORDER:
        y += 6; out.append(f'<text class="grp" x="8" y="{y + 12}">{esc(NAME[g])} (compiled by hazel-jit {TWG[g]["compiledBy"]})</text>'); y += 18
        rows = [(n, w, None) for gg, n, w in TOPS if gg == g] + [(f"whole: {n}", w, m) for gg, n, w, m in TWHOLE if gg == g]
        for name, ms, moves in rows:
            vs = [ms[k] for k, _, _ in marks if ms.get(k)]
            out.append(f'<text class="lbl small{" wh" if moves else ""}" x="8" y="{y + 10}">{esc(cut(name))}</text>'
                       f'<line class="span" x1="{X(min(vs)):.1f}" y1="{y + 6}" x2="{X(max(vs)):.1f}" y2="{y + 6}"/>')
            for k, cls, words in marks:
                if ms.get(k):
                    out.append(f'<circle class="{cls}" cx="{X(ms[k]):.1f}" cy="{y + 6}" r="4.2"><title>{esc(NAME[g])}, {esc(name)}: {words} {t(ms[k])}{f", {moves} moves" if moves else ""}</title></circle>')
            y += 15
    for e, _ in ticks: out.insert(0, f'<line class="grid" x1="{X(10 ** e):.1f}" y1="{top - 6}" x2="{X(10 ** e):.1f}" y2="{y}"/>')
    y += 10
    out += legend([(w, c) for _, c, w in marks[:2]], 12, y)
    out += legend([(w, c) for _, c, w in marks[2:]], 12, y + 18)
    return f'<svg viewBox="0 0 {W_} {y + 30}" role="img" aria-label="Now: the three-way job, every operation and whole game of five games, on a log scale">' + "".join(out) + "</svg>"

# ---- figure (then, 063's): where the jit's time went, build 2
def cross_then_svg():
    W_, x0, w = 640, 262, 200
    rows = sorted(OPS, key=share, reverse=True)
    out, y = [], 6
    for g, name, ms in rows:
        s = share((g, name, ms))
        out.append(f'<text class="lbl small" x="8" y="{y + 10}">{esc(cut(f"{NAME[g]}: {name}"))}</text>'
                   f'<rect class="mc" x="{x0}" y="{y}" width="{w * (1 - s):.1f}" height="11"/>'
                   f'<rect class="mj" x="{x0 + w * (1 - s):.1f}" y="{y}" width="{w * s:.1f}" height="11"><title>{s * 100:.0f}% crossing</title></rect>'
                   f'<text class="mut small" x="{x0 + w + 6}" y="{y + 10}">jit {t(ms["jit"])}, ahead of time {t(ms["compiled"])}</text>')
        y += 14
    y += 8
    out += bar_key([("the compiled code’s own work", "mc"), ("crossing: the values in and out", "mj")], x0 - 120, y + 5)
    return f'<svg viewBox="0 0 {W_} {y + 16}" role="img" aria-label="Then: each operation\'s jit time split into the compiled code\'s own work and the crossing">' + "".join(out) + "</svg>"

# ---- figure (now): the crossing on Gnome world's list-taking pieces, fresh inputs (^report(64) #fresh)
FR = W["fresh"]["rows"]
mid = lambda r: (r[0] + r[1]) / 2
def cross_now_svg():
    W_, x0, w = 640, 150, 360
    mx = max(r["hazel"][1] for r in FR)
    out, y = [], 6
    for r in FR:
        h, c, j, a = mid(r["hazel"]), mid(r["crossing"]), mid(r["js"]), mid(r["again"])
        out.append(f'<text class="lbl small" x="8" y="{y + 10}">{esc(r["piece"])}</text>'
                   f'<rect class="mj" x="{x0}" y="{y}" width="{w * c / mx:.1f}" height="11"><title>the crossing alone: {rng(*r["crossing"])} µs</title></rect>'
                   f'<rect class="mc" x="{x0 + w * c / mx:.1f}" y="{y}" width="{w * (h - c) / mx:.1f}" height="11"><title>the rest of a call on fresh inputs</title></rect>'
                   f'<text class="mut small" x="{x0 + w * h / mx + 5:.1f}" y="{y + 10}">{rng(*r["hazel"])} µs fresh</text>'
                   f'<rect class="mt" x="{x0}" y="{y + 13}" width="{w * a / mx:.1f}" height="6"><title>the same inputs again: {rng(*r["again"])} µs</title></rect>'
                   f'<rect class="mp" x="{x0}" y="{y + 21}" width="{w * j / mx:.1f}" height="6"><title>its JavaScript twin, fresh: {rng(*r["js"])} µs</title></rect>'
                   f'<text class="mut small" x="{x0 + w * max(a, j) / mx + 5:.1f}" y="{y + 26}">again {rng(*r["again"])} µs · JS {rng(*r["js"])} µs</text>')
        y += 38
    out += bar_key([("crossing, fresh", "mj"), ("the rest, fresh", "mc"), ("same inputs again", "mt"), ("JavaScript twin", "mp")], 8, y + 6)
    return f'<svg viewBox="0 0 {W_} {y + 18}" role="img" aria-label="Now: Gnome world\'s list-taking pieces on fresh inputs, the crossing alone against the rest, beside the same inputs again and the JavaScript twin">' + "".join(out) + "</svg>"

# ---- figure (then, 063's): each operation's jit time over its time ahead of time, build 2 and build 5
def conv_then_svg():
    W_, x0, w = 640, 262, 300
    lo, hi = math.log10(0.01), math.log10(3000)
    X = lambda r: x0 + w * (math.log10(min(max(r, 0.01), 3000)) - lo) / (hi - lo)
    rows = sorted(CONV, key=lambda c: c[2]["jit"] / c[2]["compiled"], reverse=True)
    out, y = [], 18
    for v in [0.01, 0.1, 1, 10, 100, 1000]:
        out.append(f'<line class="grid" x1="{X(v):.1f}" y1="12" x2="{X(v):.1f}" y2="{18 + 14 * len(rows)}"/><text class="mut small" x="{X(v):.1f}" y="9" text-anchor="middle">{v:g}×</text>')
    for g, name, o, n in rows:
        a, b = o["jit"] / o["compiled"], n["jit"] / n["compiled"]
        out.append(f'<text class="lbl small" x="8" y="{y + 9}">{esc(cut(f"{NAME[g]}: {name}"))}</text><line x1="{X(a):.1f}" y1="{y + 5}" x2="{X(b):.1f}" y2="{y + 5}" stroke="var(--muted)" stroke-width="1"/>'
                   f'<circle class="cvo" cx="{X(a):.1f}" cy="{y + 5}" r="3.6"><title>build 2: jit {t(o["jit"])}, ahead of time {t(o["compiled"])}</title></circle>'
                   f'<circle class="cvn" cx="{X(b):.1f}" cy="{y + 5}" r="3.6"><title>build 5: jit {t(n["jit"])}, ahead of time {t(n["compiled"])}</title></circle>'
                   f'<text class="mut small" x="{x0 + w + 8}" y="{y + 9}">{t(o["jit"])} → {t(n["jit"])}</text>')
        y += 14
    out.append(f'<line x1="{X(1):.1f}" y1="12" x2="{X(1):.1f}" y2="{y}" stroke="var(--ink)" stroke-width="1.2"/>')
    y += 10
    out += legend([("build 2, 11-23", "cvo"), ("build 5, converters, 11-24", "cvn")], 12, y + 5)
    return f'<svg viewBox="0 0 {W_} {y + 20}" role="img" aria-label="Then: each operation\'s jit time over its time ahead of time, before and with the converters">' + "".join(out) + "</svg>"

CT_SHORT = ["0.0.11 (build 2), on operations", "build 5: converters by type", "build 6: memos as links", "records as objects", "hazeljs 0.0.13", "loops and JS arguments", "0.0.14’s library, 2c4a61560f"]
assert len(CT_SHORT) == len(CT)
# ---- figure (now): the jit's time over compiled.js's, build by build (^report(65)'s table), the 14 games' runs
def conv_now_svg():
    W_, x0, w = 640, 300, 250
    lo, hi = math.log10(0.2), math.log10(10)
    X = lambda r: x0 + w * (math.log10(r) - lo) / (hi - lo)
    out, y = [], 18
    for v in [0.2, 0.5, 1, 2, 5, 10]:
        out.append(f'<line class="grid" x1="{X(v):.1f}" y1="12" x2="{X(v):.1f}" y2="{18 + 22 * len(CT)}"/><text class="mut small" x="{X(v):.1f}" y="9" text-anchor="middle">{v:g}×</text>')
    for i, (when, build, what, r) in enumerate(CT):
        r = float(r); cls = "cvo" if i == 0 else ("cvn" if i == len(CT) - 1 else "mt")
        b = CT_SHORT[i]
        out.append(f'<text class="lbl small" x="8" y="{y + 9}">{esc(when[5:])} · {esc(cut(b, 36))}</text>'
                   f'<rect class="{cls}" x="{X(0.2):.1f}" y="{y}" width="{X(r) - X(0.2):.1f}" height="12"><title>{esc(build)}: {esc(what)}</title></rect>'
                   f'<text class="mut small" x="{X(r) + 5:.1f}" y="{y + 10}">{r:.2f}×</text>')
        y += 22
    out.append(f'<line x1="{X(1):.1f}" y1="12" x2="{X(1):.1f}" y2="{y}" stroke="var(--ink)" stroke-width="1.2"/>')
    return f'<svg viewBox="0 0 {W_} {y + 8}" role="img" aria-label="Now: the jit\'s time a call over the ahead-of-time code\'s, build by build from 2026-11-23 to 11-25">' + "".join(out) + "</svg>"

# ---- figure: each game's own run, the time a call each way, then (build 5, 11-24) and now (0.0.14's library, 11-25)
def run_short(g, name):
    m = re.match(r"(\d+ frames|a game of \d+ moves|a game on 9 by 9, \d+ turns|16 by 30, \d+ taps|a hand of \d+ steps|a deal, \d+ moves|a deal, \d+ pairs taken)", name)
    return f"{NAME[g]}: {m.group(1) if m else name}"
def runs_svg():
    W_, x0, x1 = 640, 262, 628
    lo, hi = -1, 6
    X = lambda us: x0 + (math.log10(us) - lo) / (hi - lo) * (x1 - x0)
    out, y = [], 26
    ticks = [(-1, "0.1 µs"), (0, "1 µs"), (1, "10 µs"), (2, "0.1 ms"), (3, "1 ms"), (4, "10 ms"), (5, "0.1 s"), (6, "1 s")]
    for e, lab in ticks: out.append(f'<text class="mut" x="{X(10 ** e):.1f}" y="14" text-anchor="{"end" if e == hi else "middle"}">{lab}</text>')
    top = y
    for title, gs in GROUPS:
        rs = [g for g in RG if g in gs]
        if not rs: continue
        y += 6; out.append(f'<text class="grp" x="8" y="{y + 12}">{esc(title)}</text>'); y += 18
        for g in rs:
            now, then = F4[g]["ways"], RUNS5[g][2]
            pts = [("interpreted", "mi", now["interpreted"]["usPerCall"], "interpreted, 11-25"), ("jit then", "mjt", then["jit"]["usPerCall"], "jit, build 5, 11-24"),
                   ("jit now", "mj", now["jit"]["usPerCall"], "jit, 0.0.14's library, 11-25"), ("compiled", "mc", now["compiled"]["usPerCall"], "the game's own compiled.js, 11-25"),
                   ("plain JS", "mp", now["plain JS"]["usPerCall"], "plain JS, 11-25")]
            vs = [p[2] for p in pts]
            out.append(f'<text class="lbl small" x="8" y="{y + 10}">{esc(run_short(g, F4[g]["name"]))}</text>'
                       f'<line class="span" x1="{X(min(vs)):.1f}" y1="{y + 6}" x2="{X(max(vs)):.1f}" y2="{y + 6}"/>')
            for _, cls, us, words in pts:
                out.append(f'<circle class="{cls}" cx="{X(us):.1f}" cy="{y + 6}" r="4.2"><title>{esc(NAME[g])}: {words}, {t(us / 1000)} a call</title></circle>')
            y += 15
    for e, _ in ticks: out.insert(0, f'<line class="grid" x1="{X(10 ** e):.1f}" y1="{top - 6}" x2="{X(10 ** e):.1f}" y2="{y}"/>')
    y += 10
    out += legend([("interpreted", "mi"), ("jit, 11-24 (then)", "mjt"), ("jit, 0.0.14 (now)", "mj")], 12, y)
    out += legend([("the game’s compiled.js", "mc"), ("plain JS", "mp")], 12, y + 18)
    return f'<svg viewBox="0 0 {W_} {y + 30}" role="img" aria-label="Each game\'s own run, the time a call: interpreted, the jit then and now, compiled.js and plain JS, on a log scale">' + "".join(out) + "</svg>"

# ---- figure: each game's run, the jit's time over compiled.js's: build 5, build 6 (063) and now
def runs_cmp_svg():
    W_, x0, w = 640, 150, 310
    lo, hi = math.log10(0.05), math.log10(3)
    X = lambda r: x0 + w * (math.log10(min(max(r, 0.05), 3)) - lo) / (hi - lo)
    gs = sorted(RG, key=lambda g: -ja5[g])
    out, y = [], 18
    for v in [0.05, 0.1, 0.2, 0.5, 1, 2]:
        out.append(f'<line class="grid" x1="{X(v):.1f}" y1="12" x2="{X(v):.1f}" y2="{18 + 15 * len(gs)}"/><text class="mut small" x="{X(v):.1f}" y="9" text-anchor="middle">{v:g}×</text>')
    for g in gs:
        a, b, c = ja5[g], ja6[g], jan[g]
        out.append(f'<text class="lbl small" x="8" y="{y + 9}">{esc(NAME[g])}</text><line x1="{X(max(a, b, c)):.1f}" y1="{y + 5}" x2="{X(min(a, b, c)):.1f}" y2="{y + 5}" stroke="var(--muted)" stroke-width="1"/>'
                   f'<circle class="cvo" cx="{X(a):.1f}" cy="{y + 5}" r="3.6"><title>{esc(NAME[g])}, build 5 (11-24): {a:.2f}×</title></circle>'
                   f'<circle class="mt" cx="{X(b):.1f}" cy="{y + 5}" r="3.6"><title>{esc(NAME[g])}, build 6 (11-24): {b:.2f}×</title></circle>'
                   f'<circle class="cvn" cx="{X(c):.1f}" cy="{y + 5}" r="3.6"><title>{esc(NAME[g])}, 0.0.14\'s library (11-25): {c:.2f}×</title></circle>'
                   f'<text class="mut small" x="{x0 + w + 8}" y="{y + 9}">{a:.2f}× → {b:.2f}× → {c:.2f}×</text>')
        y += 15
    out.append(f'<line x1="{X(1):.1f}" y1="12" x2="{X(1):.1f}" y2="{y}" stroke="var(--ink)" stroke-width="1.2"/>')
    y += 10
    out += legend([("build 5, 11-24", "cvo"), ("build 6, 11-24", "mt"), ("0.0.14’s library, 11-25", "cvn")], 12, y + 5)
    return f'<svg viewBox="0 0 {W_} {y + 20}" role="img" aria-label="Each game\'s run: the jit\'s time over compiled.js\'s, builds 5 and 6 and now">' + "".join(out) + "</svg>"

# ---- figure: building each game's rules, interpreted and with the jit: now as bars, then as ticks
def once_svg():
    W_, x0, w = 640, 150, 360
    mx = max(max(F4[g]["once"]["interpretedBuildMs"], G[g]["once"]["interpretedBuildMs"]) for g in RG)
    out, y = [], 6
    for g in sorted(RG, key=lambda g: -F4[g]["once"]["interpretedBuildMs"]):
        o, p = F4[g]["once"], G[g]["once"]
        out.append(f'<text class="lbl small" x="8" y="{y + 15}">{esc(NAME[g])}</text>')
        for k, (v, v0, cls) in enumerate(((o["interpretedBuildMs"], p["interpretedBuildMs"], "mi"), (o["jitBuildMs"], p["jitBuildMs"], "mj"))):
            out.append(f'<rect class="{cls}" x="{x0}" y="{y + k * 11}" width="{w * v / mx:.1f}" height="10"><title>now: {t(v)}</title></rect>'
                       f'<line class="tick" x1="{x0 + w * v0 / mx:.1f}" y1="{y + k * 11 - 1}" x2="{x0 + w * v0 / mx:.1f}" y2="{y + k * 11 + 11}"><title>then (063): {t(v0)}</title></line>'
                       f'<text class="mut small" x="{x0 + w * max(v, v0) / mx + 5:.1f}" y="{y + k * 11 + 9}">{t(v0)} → {t(v)}</text>')
        y += 27
    out += bar_key([("interpreted: build", "mi"), ("jit: build and compile", "mj")], x0, y + 5)
    out.append(f'<line class="tick" x1="{x0 + 330}" y1="{y}" x2="{x0 + 330}" y2="{y + 11}"/><text class="mut" x="{x0 + 336}" y="{y + 9}">then (report 063)</text>')
    return f'<svg viewBox="0 0 {W_} {y + 18}" role="img" aria-label="Milliseconds to build each game\'s rules interpreted and with the jit, now as bars and then as ticks">' + "".join(out) + "</svg>"

# ---- figure: Gnome world's rules, built by three libraries on one runner; and made from text
def world_build_svg():
    W_, x0, w = 640, 200, 330
    mx = 5.5
    out, y = [], 6
    for L in W["build"]["libs"]:
        out.append(f'<text class="lbl small" x="8" y="{y + 15}">{esc(L["name"])}</text>')
        for k, (vs, cls, words) in enumerate(((L["first"], "mi", "first"), (L["warm"], "mj", "warm"))):
            a, b = min(vs), max(vs)
            out.append(f'<rect class="{cls}" x="{x0}" y="{y + k * 11}" width="{w * a / mx:.1f}" height="10"/>'
                       f'<rect class="{cls} faint" x="{x0 + w * a / mx:.1f}" y="{y + k * 11}" width="{max(1, w * (b - a) / mx):.1f}" height="10"/>'
                       f'<text class="mut small" x="{x0 + w * b / mx + 5:.1f}" y="{y + k * 11 + 9}">{words} {rng(a, b)} s</text>')
        y += 27
    a = W["aot"]["makeMs"] / 1000
    out.append(f'<text class="lbl small" x="8" y="{y + 10}">ahead of time (0.0.147)</text><rect class="mc" x="{x0}" y="{y + 1}" width="{max(2, w * a / mx):.1f}" height="10"/>'
               f'<text class="mut small" x="{x0 + w * a / mx + 5:.1f}" y="{y + 10}">made from text, {W["aot"]["makeMs"]} ms (in the browser pane, on the laptop)</text>')
    y += 22
    out += bar_key([("the first build", "mi"), ("warm: the median of five", "mj")], x0, y + 5)
    return f'<svg viewBox="0 0 {W_} {y + 18}" role="img" aria-label="Seconds to build Gnome world\'s rules with three libraries, first and warm, and to make them from text">' + "".join(out) + "</svg>"

# ---- figure: World.step and Gnome world's pieces, Hazel against plain JavaScript
def step_svg():
    W_, x0, w = 640, 230, 220
    S = W["step"]["libs"]
    mx = 5.0
    out, y = [], 6
    for L in S:
        for key, pk, words in (("same", "plainSame", "same inputs again"), ("fresh", "plainFresh", "fresh inputs")):
            h, p = L[key], L[pk]
            out.append(f'<text class="lbl small" x="8" y="{y + 10}">{esc(L["name"].replace("the night’s trials", "night’s trials").replace("the night's trials", "night's trials"))}, {words}</text>'
                       f'<rect class="mj" x="{x0}" y="{y}" width="{w * min(h) / mx:.1f}" height="9"/><rect class="mj faint" x="{x0 + w * min(h) / mx:.1f}" y="{y}" width="{max(1, w * (max(h) - min(h)) / mx):.1f}" height="9"/>'
                       f'<text class="mut small" x="{x0 + w * max(h) / mx + 5:.1f}" y="{y + 8}">{rng(min(h), max(h))} µs, {min(h) / max(p):.1f}–{max(h) / min(p):.1f}× JS</text>'
                       f'<rect class="mp" x="{x0}" y="{y + 10}" width="{w * min(p) / mx:.1f}" height="6"/>'
                       f'<text class="mut small" x="{x0 + w * max(p) / mx + 5:.1f}" y="{y + 17}">plain JS {rng(min(p), max(p))} µs</text>')
            y += 31
    out += bar_key([("World.step in Hazel, through jitProgram", "mj"), ("world/plain.js", "mp")], 8, y + 6)
    return f'<svg viewBox="0 0 {W_} {y + 18}" role="img" aria-label="World.step\'s time a call in Hazel and in plain JavaScript, the package\'s library and the night\'s trials">' + "".join(out) + "</svg>"

PIECES = N64["pieces"]["rows"]   # [what, function, version, js us, hazel us, same]
def pieces_svg():
    W_, x0, w = 640, 170, 240
    mx = max(r[4] for r in PIECES)
    out, y = [], 6
    for what, fn, ver, js, hz, same in sorted(PIECES, key=lambda r: -r[4] / r[3]):
        out.append(f'<text class="lbl small" x="8" y="{y + 10}">{esc(fn)}</text>'
                   f'<rect class="mj" x="{x0}" y="{y}" width="{w * hz / mx:.1f}" height="9"><title>{esc(what)}: Hazel {hz} µs</title></rect>'
                   f'<rect class="mp" x="{x0}" y="{y + 10}" width="{w * js / mx:.1f}" height="6"><title>{esc(what)}: JavaScript {js} µs</title></rect>'
                   f'<text class="mut small" x="{x0 + w * hz / mx + 5:.1f}" y="{y + 10}">{hz:.2f} µs against {js:.2f} ({hz / js:.1f}×)</text>')
        y += 21
    out += bar_key([("the piece in Hazel", "mj"), ("its JavaScript twin", "mp")], 8, y + 6)
    return f'<svg viewBox="0 0 {W_} {y + 18}" role="img" aria-label="Gnome world\'s pieces, each in Hazel against its JavaScript twin, µs a call">' + "".join(out) + "</svg>"

# ---- the branch against dev, by part, then and now
def part(p):
    if p.startswith("test/"): return "tests"   # (067: before hazel-jit, so that hazel-jit's own tests count as tests, as 063's had none)
    if "HazelJit" in p: return "hazel-jit"
    if "HazelLib" in p or p.startswith("docs/") or p == "src/web/www/dune": return "the library"
    if "ModuleProgram" in p: return "programs of modules"
    if "/embed/" in p or "embed.css" in p or p.endswith(("Main.re", "CodeEditable.re", "ContextMenu.re", "ContextMenu.rei", "Menu.re", "JsUtil.re")): return "embed mode"
    if p.startswith("licenses/") or "/fonts" in p or p.endswith(("variables.css", "index.html", "style.css")): return "fonts, icons, licenses"
    if p == "src/web/dune": return "the library"
    return "changes to dev’s own code"
PARTS = ["hazel-jit", "the library", "programs of modules", "embed mode", "fonts, icons, licenses", "changes to dev’s own code", "tests"]
def bypart(D):
    B = {k: {"added": 0, "deleted": 0, "files": 0} for k in PARTS}
    for f in D["files"]:
        b = B[part(f["path"])]; b["files"] += 1; b["added"] += f["added"] or 0; b["deleted"] += f["deleted"] or 0
    return B
B63, B67 = bypart(D63), bypart(D67)
A63, A67 = sum(b["added"] for b in B63.values()), sum(b["added"] for b in B67.values())
DEL67 = sum(b["deleted"] for b in B67.values())
def diff_svg():
    W_, x0, w = 640, 190, 300
    mx = max(b["added"] for b in list(B63.values()) + list(B67.values()))
    out, y = [], 6
    for k in PARTS:
        a, b = B63[k], B67[k]
        out.append(f'<text class="lbl small" x="8" y="{y + 12}">{esc(k)}</text>'
                   f'<rect class="mt" x="{x0}" y="{y}" width="{max(1, w * a["added"] / mx):.1f}" height="8"/>'
                   f'<rect class="mc" x="{x0}" y="{y + 9}" width="{max(1, w * b["added"] / mx):.1f}" height="9"/>'
                   f'<text class="mut small" x="{x0 + w * max(a["added"], b["added"]) / mx + 5:.1f}" y="{y + 14}">{a["added"]:,} → {b["added"]:,} lines</text>')
        y += 24
    out += bar_key([("then: 98c482395d, 11-23", "mt"), ("now: b1b4e19286, 11-26", "mc")], 8, y + 6)
    return f'<svg viewBox="0 0 {W_} {y + 18}" role="img" aria-label="Lines the hazeljs branch adds over dev, by part, then and now">' + "".join(out) + "</svg>"
def diff_table():
    rows = "".join(f'<tr><td>{esc(k)}</td><td>{B63[k]["files"]} → {B67[k]["files"]}</td><td>{B63[k]["added"]:,} → {B67[k]["added"]:,}</td><td>{B63[k]["deleted"]:,} → {B67[k]["deleted"]:,}</td></tr>' for k in PARTS)
    return (f'<table class="nums"><thead><tr><th>part</th><th>files</th><th>lines added</th><th>lines removed</th></tr></thead><tbody>{rows}'
            f'<tr><td><b>all</b></td><td><b>{len(D63["files"])} → {len(D67["files"])}</b></td><td><b>{A63:,} → {A67:,}</b></td><td><b>{sum(b["deleted"] for b in B63.values())} → {DEL67}</b></td></tr></tbody></table>')

# ---- the PRs, then and now
GIVES = {2859: "hazel-jit on its own, from <code>dev</code>: the compiler, the values across, mixed mode and holes in it, the agreement tests. New since report 063, which had the jit inside #2857.",
         2857: "The package: everything below that it uses, merged with <code>dev</code> and ported to Jane Street Core; hazel-jit now arrives by merging #2859.",
         2711: "The library, first version: <code>Hazel.analyze</code> and <code>Hazel.run</code> from any page.",
         2719: "Programs of named modules (<code>analyzeProgram</code>, <code>runProgram</code>), and Hazel in another page’s frame.",
         2814: "Embed mode: editable cells, one module at a time, go to definition across cells.",
         2837: "IBM Plex Sans as the interface font, in place of a Helvetica Neue that Hazel had no license to ship.",
         2842: "Material Icons shipped with Hazel, so nothing loads from Google.",
         2817: "hazel-jit on the livelits line: livelit views compiled.",
         2828: "SInt with 64 bits everywhere, overflow an error. Not in #2859 or #2857 yet.",
         2603: "Statics: a let analyzed once unless it refers to itself. Not in the package; tried under it today (^ticket(894)).",
         2717: "Statics: a module binding as a non-recursive let. The same experiment."}
def state(p): return ("draft" if p["isDraft"] else "open") if p["state"] == "OPEN" else p["state"].lower()
def pr_table():
    rows = []
    for n in [2859, 2857, 2711, 2719, 2814, 2837, 2842, 2817, 2828, 2603, 2717]:
        p, q = P67[n], P63.get(n)
        then = f'+{q["additions"]:,} / −{q["deletions"]:,}' if q else "–"
        rows.append(f'<tr><td>#{n}</td><td><code>{esc(p["headRefName"])}</code> into <code>{esc(p["baseRefName"])}</code></td><td>{state(p)}</td>'
                    f'<td>{then}</td><td>+{p["additions"]:,} / −{p["deletions"]:,}</td><td class="l">{GIVES[n]}</td></tr>')
    return ('<div class="tw"><table class="nums"><thead><tr><th>PR</th><th>branch</th><th>state now</th><th>lines, 11-23</th><th>lines, 11-27</th><th class="l">what it gives the package</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')

# ---- the three-way job's numbers, every operation
def ops_table():
    rows = []
    for g in TW_ORDER:
        rows.append(f'<tr class="grp"><td colspan="7">{esc(NAME[g])}: compiled.js by hazel-jit {TWG[g]["compiledBy"]}; hazeljs built the rules in {t(TWG[g]["hazeljsBuildMs"])}</td></tr>')
        for gg, name, w, *m in [r for r in TOPS if r[0] == g] + [(gg, f"whole: {n}", w, mv) for gg, n, w, mv in TWHOLE if gg == g]:
            c = lambda k: t(w[k]) if w.get(k) else "–"
            rows.append(f'<tr><td>{esc(name)}</td>' + "".join(f"<td>{c(k)}</td>" for k in (HZ, HJ, NB, PN, PJ)) +
                        f'<td>{x_(w[HJ] / w[PJ])}</td></tr>')
    return ('<div class="tw"><table class="nums"><thead><tr><th>operation</th><th>hazeljs 0.0.4</th><th>compiled.js</th><th>no step budget</th><th>no budget, plain numbers</th><th>plain JS</th>'
            f'<th>compiled.js over plain JS</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
def once_table():
    rows = "".join(f'<tr><td>{esc(NAME[g])}</td><td>{t(G[g]["once"]["interpretedBuildMs"])}</td><td>{t(F4[g]["once"]["interpretedBuildMs"])}</td>'
                   f'<td>{t(G[g]["once"]["jitBuildMs"])}</td><td>{t(F4[g]["once"]["jitBuildMs"])}</td><td>{kb(F4[g]["once"]["wrappedBytes"])}</td>'
                   f'<td class="l">{esc(G[g]["machine"]["model"])}; {esc(F4[g]["machine"]["model"])}</td></tr>' for g in RG)
    return ('<div class="tw"><table class="nums"><thead><tr><th>game</th><th>interpreted, 11-23</th><th>interpreted, 11-25</th><th>jit, 11-23</th><th>jit, 11-25</th>'
            f'<th>compiled.js file</th><th class="l">the runners’ processors, then; now</th></tr></thead><tbody>{rows}</tbody></table></div>')

# ---- numbers for the text
IJ63, IC63, CP63 = ratio("interpreted", "jit"), ratio("interpreted", "compiled"), ratio("compiled", "plain JS")
cp63_5 = [o[2]["compiled"] / o[2]["plain JS"] for o in OPS if "plain JS" in o[2]]
TW_IH = tr(HZ, HJ); TW_HP = tr(HJ, PJ); TW_NP = tr(PN, HJ); TW_BH = tr(NB, HJ)
TW_WHP = tr(HJ, PJ, TWHOLE); TW_WIH = tr(HZ, HJ, TWHOLE)
rn_ij = gm([fw(g, "interpreted") / fw(g, "jit") for g in RG]); rn_jp = gm([fw(g, "jit") / fw(g, "plain JS") for g in RG])
rn5_ij = gm([RUNS5[g][2]["interpreted"]["usPerCall"] / RUNS5[g][2]["jit"]["usPerCall"] for g in RG])
rn_fresh = gm([fw(g, "jit, fresh copies") / fw(g, "jit") for g in RG])
rn5_fresh = gm([RUNS5[g][2]["jit, fresh copies"]["usPerCall"] / RUNS5[g][2]["jit"]["usPerCall"] for g in RG])
rn5_jp = gm([RUNS5[g][2]["jit"]["usPerCall"] / RUNS5[g][2]["plain JS"]["usPerCall"] for g in RG if "plain JS" in RUNS5[g][2]])
rn_jp5 = gm([fw(g, "jit") / fw(g, "plain JS") for g in RG if "plain JS" in RUNS5[g][2]])
slowest = max(RG, key=lambda g: fw(g, "jit"))
frame_ok = [g for g in RG if fw(g, "interpreted") <= 16_700]
Bw = W["build"]["libs"]; SP = W["speedrun"]; ST = W["step"]["libs"]
once_ratio = gm([F4[g]["once"]["jitBuildMs"] / G[g]["once"]["jitBuildMs"] for g in RG])
once_i_ratio = gm([F4[g]["once"]["interpretedBuildMs"] / G[g]["once"]["interpretedBuildMs"] for g in RG])
bjn = [F4[g]["once"]["jitBuildMs"] for g in RG]; bin_ = [F4[g]["once"]["interpretedBuildMs"] for g in RG]
ms30 = next(o for o in OPS if o[0] == "minesweeper" and o[1] == "16 by 30: a cell opened")
tw_ms30 = next(w for g, n, w in TOPS if g == "minesweeper" and n == "a cell opened (expert, 16 by 30)")
tw_bound = {g: TWG[g]["boundary"] for g in TW_ORDER}
pieces_r = [r[4] / r[3] for r in PIECES]
ct = {r[1]: float(r[3]) for r in CT}

EXTRA = """
  .cvo { fill: var(--warn); } .cvn { fill: var(--good); }
  figure.chart svg { width: 100%; height: auto; display: block; }
  svg .lbl { fill: var(--ink); font: 13px system-ui, sans-serif; } svg .mut { fill: var(--muted); font: 12px system-ui, sans-serif; }
  svg .small { font-size: 11px; } svg .grp { fill: var(--ink); font: 700 12px system-ui, sans-serif; } svg .wh { font-style: italic; }
  svg .grid { stroke: var(--line); } svg .span { stroke: var(--line); stroke-width: 2; } svg .tick { stroke: var(--ink); stroke-width: 2; }
  svg .mi { fill: #6b737d; } svg .mj { fill: #eb6834; } svg .mc { fill: #2a78d6; } svg .mp { fill: #2e9e5b; } svg .mf { fill: var(--paper); stroke: #eb6834; stroke-width: 2; }
  svg .mjt { fill: var(--paper); stroke: #eb6834; stroke-width: 2; } svg .mcn { fill: var(--paper); stroke: #2a78d6; stroke-width: 2; }
  svg .mt { fill: #b9a6e0; } svg .faint { opacity: 0.45; }
  svg .pbox { fill: var(--paper); stroke: var(--line); stroke-width: 1.5; } svg .pbox.interpreted { stroke: #6b737d; } svg .pbox.jit { stroke: #eb6834; }
  svg .pbox.compiled { stroke: #2a78d6; } svg .pbox.editor { stroke: #2e9e5b; } svg .arrow { fill: none; stroke: var(--muted); stroke-width: 1.5; }
  table.nums td, table.nums th { text-align: right; font-variant-numeric: tabular-nums; } table.nums td:first-child, table.nums th:first-child { text-align: left; }
  table.nums td.l, table.nums th.l { text-align: left; } table.nums tr.grp td { font-weight: 700; padding-top: 0.8em; }
  .tw { overflow-x: auto; margin: 0.6em 0 1em; } .tw table { min-width: 720px; }
  ol.decide > li { margin-bottom: 0.9em; }
  .then-now { font-size: 0.92em; color: var(--muted); margin: -0.3em 0 0.8em; }
  figure.then { opacity: 0.92; } figure.then figcaption::before { content: "Then. "; font-weight: 700; } figure.now figcaption::before { content: "Now. "; font-weight: 700; }
  .summary { border: 1px solid var(--line); border-radius: 8px; padding: 0.6em 1em; margin: 1em 0; background: var(--paper); }
  .summary p { margin: 0.4em 0; }
"""
FIGS = {
    "updated": updated,
    "paths": paths_svg(), "ways_then": ways_then_svg(), "ways_now": ways_now_svg(), "cross_then": cross_then_svg(), "cross_now": cross_now_svg(),
    "conv_then": conv_then_svg(), "conv_now": conv_now_svg(), "runs": runs_svg(), "runs_cmp": runs_cmp_svg(), "once": once_svg(),
    "world_build": world_build_svg(), "step": step_svg(), "pieces": pieces_svg(),
    "diff": diff_svg(), "diff_table": diff_table(), "pr_table": pr_table(), "ops_table": ops_table(), "once_table": once_table(),
    # the branch
    "added63": f"{A63:,}", "added": f"{A67:,}", "deleted": str(DEL67), "files63": str(len(D63["files"])), "files": str(len(D67["files"])),
    "ahead63": str(D63["commits_ahead"]), "ahead": str(D67["commits_ahead"]), "behind": str(D67["commits_behind"]),
    "jit63": f'{B63["hazel-jit"]["added"]:,}', "jit_lines": f'{B67["hazel-jit"]["added"]:,}', "test63": f'{B63["tests"]["added"]:,}', "lib63": f'{B63["the library"]["added"]:,}', "lib_lines": f'{B67["the library"]["added"]:,}', "test_lines": f'{B67["tests"]["added"]:,}',
    "own63": f'{B63["changes to dev’s own code"]["added"]:,}', "own_lines": f'{B67["changes to dev’s own code"]["added"]:,}',
    "pr2859_add": f'{P67[2859]["additions"]:,}', "pr2857_add": f'{P67[2857]["additions"]:,}', "pr2857_add63": f'{P63[2857]["additions"]:,}',
    # every game, then
    "games63": str(len(ORDER)), "light63": str(len(LIGHT)), "cv_c_rng": f'{min(n["compiled"] / o["compiled"] for _, _, o, n in CONV):.1f} to {max(n["compiled"] / o["compiled"] for _, _, o, n in CONV):.1f}', "ops63": str(len(OPS)), "ij63": x_(gm(IJ63)), "ic63": x_(gm(IC63)), "cp63": x_(gm(cp63_5)), "cp63_n": str(len(cp63_5)),
    # the three-way job, now
    "tw_ops": str(len(TOPS)), "tw_whole": str(len(TWHOLE)), "tw_ih": x_(gm(TW_IH)), "tw_ih_n": str(len(TW_IH)), "tw_ih_min": x_(min(TW_IH)), "tw_ih_max": x_(max(TW_IH)),
    "tw_hp": x_(gm(TW_HP)), "tw_hp_min": x_(min(TW_HP)), "tw_hp_max": x_(max(TW_HP)), "tw_np": f"{gm(TW_NP):.2f}", "tw_bh": f"{gm(TW_BH):.2f}",
    "tw_whp": x_(gm(TW_WHP)), "tw_whp_min": x_(min(TW_WHP)), "tw_whp_max": x_(max(TW_WHP)), "tw_wih": x_(gm(TW_WIH)),
    "tw_machine": TW["machine"], "tw_ms30_j": t(tw_ms30[HJ]), "tw_ms30_p": t(tw_ms30[PJ]), "tw_ms30_i": t(tw_ms30[HZ]),
    "tw_ms30_b": t(next(b["ms"] for b in tw_bound["minesweeper"] if "16 by 30" in b["at"])),
    "ms30_i": t(ms30[2]["interpreted"]), "ms30_j": t(ms30[2]["jit"]), "ms30_c": t(ms30[2]["compiled"]), "ms30_p": t(ms30[2]["plain JS"]),
    # runs, then and now
    "rn_n": str(len(RG)), "rn_calls": f'{sum(F4[g]["steps"] for g in RG):,}', "rn_ja5": x2(gm(list(ja5.values()))), "rn_ja6": x2(gm(list(ja6.values()))), "rn_jan": x2(gm(list(jan.values()))),
    "rn_ij": x_(rn_ij), "rn5_ij": x_(rn5_ij), "rn_jp": x_(rn_jp), "rn5_jp": x_(rn5_jp), "rn_jp5": x_(rn_jp5), "rn_fresh": f"{rn_fresh:.1f}×", "rn5_fresh": f"{rn5_fresh:.1f}×",
    "rn_slowest": f'{NAME[slowest]}, {t(fw(slowest, "jit") / 1000)} a call', "rn_frame_ok": str(len(frame_ok)),
    "rn_best": ", ".join(f'{NAME[g]} {jan[g]:.2f}×' for g in sorted(RG, key=lambda g: jan[g])[:3]),
    "rn_worst": ", ".join(f'{NAME[g]} {jan[g]:.2f}×' for g in sorted(RG, key=lambda g: -jan[g])[:3]),
    "rn_jit_gain": x_(gm([RUNS5[g][2]["jit"]["usPerCall"] / fw(g, "jit") for g in RG])),
    "rn_dig": f'{t(RUNS5["dig"][2]["jit"]["usPerCall"] / 1000)} → {t(fw("dig", "jit") / 1000)}', "rn_ms": f'{t(RUNS5["mahjong-solitaire"][2]["jit"]["usPerCall"] / 1000)} → {t(fw("mahjong-solitaire", "jit") / 1000)}',
    # converters timeline
    "ct_first": f'{float(CT[0][3]):.2f}×', "ct_last": f'{float(CT[-1][3]):.2f}×', "ct_013": f'{next(float(r[3]) for r in CT if "0.0.13" in r[1]):.2f}×',
    # build
    "b_i_min": t(min(bin_)), "b_i_max": t(max(bin_)), "b_j_min": t(min(bjn)), "b_j_max": t(max(bjn)),
    "b_j_share": f'{min(F4[g]["once"]["jitBuildMs"] / F4[g]["once"]["interpretedBuildMs"] for g in RG) * 100:.0f}% to {max(F4[g]["once"]["jitBuildMs"] / F4[g]["once"]["interpretedBuildMs"] for g in RG) * 100:.0f}%',
    "b_ratio": f"{once_ratio:.2f}×", "b_i_ratio": f"{once_i_ratio:.2f}×",
    "dig_b63": t(G["dig"]["once"]["jitBuildMs"]), "dig_bn": t(F4["dig"]["once"]["jitBuildMs"]), "dig_bi63": t(G["dig"]["once"]["interpretedBuildMs"]), "dig_bin": t(F4["dig"]["once"]["interpretedBuildMs"]),
    "wb_h_first": rng(min(Bw[0]["first"]), max(Bw[0]["first"])), "wb_h_warm": rng(min(Bw[0]["warm"]), max(Bw[0]["warm"])),
    "wb_n_first": rng(min(Bw[1]["first"]), max(Bw[1]["first"])), "wb_n_warm": rng(min(Bw[1]["warm"]), max(Bw[1]["warm"])),
    "wb_s_first": rng(min(Bw[2]["first"]), max(Bw[2]["first"])), "wb_s_warm": rng(min(Bw[2]["warm"]), max(Bw[2]["warm"])),
    "wb_gain": f'{min(Bw[0]["warm"]) / max(Bw[2]["warm"]):.0f} to {max(Bw[0]["warm"]) / min(Bw[2]["warm"]):.0f} times',
    # plain JS, World.step, pieces, speed run
    "ws_h": rng(min(ST[0]["same"]), max(ST[0]["same"])), "ws_hp": rng(min(ST[0]["plainSame"]), max(ST[0]["plainSame"])),
    "ws_n": rng(min(ST[1]["same"]), max(ST[1]["same"])), "ws_np": rng(min(ST[1]["plainSame"]), max(ST[1]["plainSame"])),
    "ws_hf": rng(min(ST[0]["fresh"]), max(ST[0]["fresh"])), "ws_hfp": rng(min(ST[0]["plainFresh"]), max(ST[0]["plainFresh"])),
    "ws_nf": rng(min(ST[1]["fresh"]), max(ST[1]["fresh"])), "ws_nfp": rng(min(ST[1]["plainFresh"]), max(ST[1]["plainFresh"])),
    "ws_hx": f'{gm([a / b for a, b in zip(ST[0]["same"], ST[0]["plainSame"])]):.1f}×', "ws_nx": f'{gm([a / b for a, b in zip(ST[1]["same"], ST[1]["plainSame"])]):.1f}×',
    "ws_hfx": f'{gm([a / b for a, b in zip(ST[0]["fresh"], ST[0]["plainFresh"])]):.1f}×', "ws_nfx": f'{gm([a / b for a, b in zip(ST[1]["fresh"], ST[1]["plainFresh"])]):.1f}×',
    "ws_gain": f'{1 - gm(ST[1]["same"]) / gm(ST[0]["same"]):.0%}', "ws_gainf": f'{1 - gm(ST[1]["fresh"]) / gm(ST[0]["fresh"]):.0%}',
    "pc_n": str(len(PIECES)), "pc_min": x_(min(pieces_r)), "pc_max": x_(max(pieces_r)), "pc_gm": x_(gm(pieces_r)),
    "sr_h": f'{SP["hazelS"]:.1f} s', "sr_p": f'{SP["plainS"]:.1f} s', "sr_steps": f'{SP["steps"]:,}', "sr_pct": f'{SP["hazelS"] / SP["plainS"] - 1:.0%}',
    "sr_hus": f'{SP["hazelUsStep"]:.0f} µs', "sr_pus": f'{SP["plainUsStep"]:.0f} µs', "sr_rules": f'{SP["inRulesHazelS"]:.2f} s', "sr_rules_pct": f'{SP["inRulesHazelS"] / SP["hazelS"]:.1%}',
    "sr_fps_h": fps(SP["hazelUsStep"] / 1000), "sr_fps_p": fps(SP["plainUsStep"] / 1000),
}
body = open(os.path.join(HERE, "body.html")).read()
for k, v in FIGS.items(): body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{(\w+)\}\}", body)
assert not left, left
TITLE = "Hazel as an npm Package, Then and Now"
DESC = (f"Report 063's questions and charts, asked again four days later of hazeljs 0.0.14, the first version on npm with hazel-jit. "
        f"On each game's own run of states, the package's jit now takes {gm(list(jan.values())):.2f} of the time of each game's compiled.js, where it took {gm(list(ja5.values())):.2f} on 11-24 and, on 11-23's repeated operations, 7.50 times, "
        f"and runs {rn_ij:,.0f} times as fast as the interpreter. Gnome world's whole speed run takes {SP['hazelS'] / SP['plainS'] - 1:.0%} longer with every piece Hazel's than with every piece in JavaScript; "
        f"World.step alone {gm([a / b for a, b in zip(ST[0]['same'], ST[0]['plainSame'])]):.1f} times plain JavaScript's time, {gm([a / b for a, b in zip(ST[1]['same'], ST[1]['plainSame'])]):.1f} with the night's trials. "
        f"Building the rules is still seconds, nearly all Hazel's type checker: two open statics PRs bring Gnome world's warm build from about 3.2 s to 0.33 s, and its rules now ship compiled ahead of time. "
        f"Then the decisions before dev, as the 11-27 meeting left them.")
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{esc(DESC)}\">\n<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)

# the series card's thumbnail: the jit's time over compiled.js's, then and now; and World.step over plain JS
def thumb(mode):
    base = ".h{fill:#1f2328;font:700 15px system-ui,sans-serif}.m{fill:#5b6470;font:10px system-ui,sans-serif}.k{fill:#1f2328;font:700 12px system-ui,sans-serif}.o{fill:#eb6834}.g{fill:#2e9e5b}.b{fill:#2a78d6}"
    dark = ".h{fill:#e8e6e3}.m{fill:#a2a9b3}.k{fill:#e8e6e3}"
    style = base + ("\n" + dark if mode == "dark" else "\n@media (prefers-color-scheme: dark) {" + dark + "}" if mode == "auto" else "")
    vals = [("jit, 0.0.11 (11-23)", float(CT[0][3]), "o"), ("jit, 11-24", gm(list(ja5.values())), "o"), ("jit, 0.0.14", gm(list(jan.values())), "g")]
    X = lambda v: 120 + 150 * (math.log10(v) - math.log10(0.2)) / (math.log10(10) - math.log10(0.2))
    bars = "".join(f'<text class="m" x="16" y="{78 + i * 26}">{n}</text><rect class="{c}" x="120" y="{68 + i * 26}" width="{X(v) - 120:.1f}" height="13"/>'
                   f'<text class="k" x="{X(v) + 6:.1f}" y="{79 + i * 26}">{v:.2f}×</text>' for i, (n, v, c) in enumerate(vals))
    one = f'<line x1="{X(1):.1f}" y1="60" x2="{X(1):.1f}" y2="{68 + 3 * 26}" stroke="#5b6470" stroke-width="1"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" width="320" height="200">\n<style>{style}\n</style>\n'
            '<text class="h" x="16" y="26">hazeljs, then and now</text>\n<text class="m" x="16" y="43">the jit’s time over the ahead-of-time code’s</text>\n'
            f'{one}{bars}<text class="m" x="16" y="172">geometric means, log scale; 11-23 on operations, then on runs</text>\n'
            f'<text class="m" x="16" y="188">World.step: {gm([a / b for a, b in zip(ST[0]["same"], ST[0]["plainSame"])]):.1f}× plain JS; night’s trials {gm([a / b for a, b in zip(ST[1]["same"], ST[1]["plainSame"])]):.1f}×</text>\n</svg>\n')
os.makedirs(os.path.join(HERE, "img"), exist_ok=True)
for name, mode in [("thumb-light.svg", "light"), ("thumb-dark.svg", "dark"), ("thumb.svg", "auto")]: open(os.path.join(HERE, "img", name), "w").write(thumb(mode))
meta = {"title": TITLE, "blurb": DESC,
        "builds": {"package": "hazeljs 0.0.14 (hazelgrove/hazeljs f56faf9), on npm since 2026-11-25 22:18 UTC, its hazel-lib.js from hazelgrove/hazel 2c4a61560f (branch hazeljs, #2857)",
                   "hazeljs branch": "hazelgrove/hazel b1b4e19286 (2026-11-26): 0.0.14's build plus holes in mixed mode (#2859, ticket 769); build.hazel.org/hazeljs",
                   "night": "trial/1126-night abf653a21d (tickets 792, 681, 890, 891, 791), not merged",
                   "statics": "trial/1127-statics ba32db7481 (#2603 and #2717 on the night's trials; ticket 894), not to merge",
                   "then": "^report(63)'s builds 1 to 6 (hazeljs 0.0.11, hazelgrove/hazel 98c482395d, a97b6f7465, ca851b422d), its data in 063/data"},
        "runs": {"three-way": "hazeljs-examples three-way timing, run 46013126145 (commit 2026142, 2026-11-27), one runner, " + TW["machine"] + ": hazeljs 0.0.4 interpreting, each game's compiled.js (hazel-jit 5405a2e87d, f2cc549b3a, 70d0178872, d15466c7b1 on trial/794-games-aot, 2026-11-20), plain.js",
                 "four ways on runs": "^report(65): hazeljs-examples bench/4way, run 45666570615 (2026-11-25), one runner a game, Hazel.jitProgram with the library of 2c4a61560f",
                 "build timing": W["build"]["source"], "World.step": W["step"]["source"], "speed run": SP["source"], "fresh": W["fresh"]["source"]},
        "measures": {"usPerCall": "µs a call on a game's own run of states: the run's calls timed and summed, over the number of calls",
                     "ms": "the three-way job: ms a call, the median of batches (as many calls as take at least 1 ms); a whole game: its total"}}
json.dump(meta, open(os.path.join(DATA, "meta.json"), "w"), indent=1, ensure_ascii=False)
print("wrote 067/index.html;", updated)
for k in ["rn_ja5", "rn_ja6", "rn_jan", "rn_ij", "rn5_ij", "rn_jp", "rn5_jp", "rn_jp5", "rn_fresh", "rn5_fresh", "rn_jit_gain", "tw_ih", "tw_hp", "tw_np", "tw_bh", "tw_whp", "tw_wih",
          "cp63", "ij63", "ic63", "b_ratio", "b_i_ratio", "ws_hx", "ws_nx", "ws_hfx", "ws_nfx", "ws_gain", "ws_gainf", "pc_gm", "pc_min", "pc_max", "sr_pct", "rn_best", "rn_worst",
          "rn_slowest", "rn_frame_ok", "b_j_share", "b_i_min", "b_i_max", "b_j_min", "b_j_max", "added", "ahead", "behind", "jit_lines", "test_lines", "own_lines", "rn_dig", "rn_ms"]:
    print(f"  {k}: {FIGS[k]}")
