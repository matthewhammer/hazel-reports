#!/usr/bin/env python3
"""^report(63): Hazel as an npm Package: What to Decide Next. Matthew Hammer, 2026-11-23: "let's produce a WIP report about the new
npm package. PRs involved. difference with dev. open questions before merging into dev. Performance of jit compared to interpreter,
and plain JS, for all hazel examples we've created in that repo. next steps for performance improvement, based on current
situation." And: "The audience for this report is myself and Cyrus, to understand the design space, and what decisions to consider
next."

Writes 063/index.html from body.html and data/*.json: one file per game from hazeljs-examples' node/package-bench.mjs (GitHub run
45247119864), data/diff.json (the hazeljs branch against dev) and data/prs.json (the PRs, as GitHub had them)."""
import html, json, math, os, re, subprocess, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
esc = lambda s: html.escape(str(s), quote=True)

GROUPS = [("Oracles", ["i-ching", "tarot", "astrology"]),
          ("Board and card games, each with a plain JavaScript version", ["checkers", "go", "minesweeper", "mahjong", "solitaire"]),
          ("A puzzle", ["mahjong-solitaire"]),
          ("Arcade games, a step at a time", ["pinball", "downhill", "bricks", "snake", "trails", "starwave", "bugs", "dig"])]
NAME = {"i-ching": "I Ching", "tarot": "Tarot", "astrology": "Astrology", "checkers": "Checkers", "go": "Go", "minesweeper": "Minesweeper",
        "mahjong": "Mahjong", "solitaire": "Solitaire", "mahjong-solitaire": "Mahjong solitaire", "pinball": "Pinball", "downhill": "Downhill",
        "bricks": "Bricks", "snake": "Snake", "trails": "Light trails", "starwave": "Star wave", "bugs": "Butterfly garden", "dig": "Gnome dig"}
ORDER = [g for _, gs in GROUPS for g in gs]
G = {g: json.load(open(os.path.join(DATA, f"{g}.json"))) for g in ORDER}
WAYS = ["interpreted", "jit", "compiled", "plain JS"]
OPS = []   # (game, op name, {way: ms})
for g in ORDER:
    for o in G[g]["ops"]:
        assert all(r is None or (r.get("same") and "ms" in r) for r in o["ways"].values()), (g, o["name"])
        OPS.append((g, o["name"], {w: r["ms"] for w, r in o["ways"].items() if r}))
gm = lambda xs: math.exp(sum(map(math.log, xs)) / len(xs))
ratio = lambda a, b: [o[2][a] / o[2][b] for o in OPS if a in o[2] and b in o[2]]
share = lambda o: max(0.0, (o[2]["jit"] - o[2]["compiled"]) / o[2]["jit"])   # the jit's time not spent in compiled code
HEAVY = [o for o in OPS if share(o) < 0.5]
# (2026-11-24) build 5: the same package with #2857's library at a97b6f7465 (converters by declared type), GitHub run 45424324608
CV = {g: json.load(open(os.path.join(DATA, "conv", f"{g}.json"))) for g in ORDER}
CONV = []   # (game, op name, {way: ms} the day before, {way: ms} with the converters)
for g in ORDER:
    old = {o["name"]: {w: r["ms"] for w, r in o["ways"].items() if r} for o in G[g]["ops"]}
    for o in CV[g]["ops"]:
        assert all(r is None or r.get("same") for r in o["ways"].values()), (g, o["name"])
        CONV.append((g, o["name"], old[o["name"]], {w: r["ms"] for w, r in o["ways"].items() if r}))
cvr = lambda k: [n[k] / o[k] for _, _, o, n in CONV]
LIGHT = [o for o in OPS if share(o) >= 0.5]

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
def legend(items, x, y):
    """a figure's key in a row: each mark and its words, the next placed after the words' width (about 7.2 px a character at the
    figures' size, wide enough for the widest system font), not at a fixed step, so that no two overlap"""
    out = []
    for words, cls in items:
        out.append(f'<circle class="{cls}" cx="{x + 4:.1f}" cy="{y}" r="4.2"/><text class="mut" x="{x + 12:.1f}" y="{y + 4}">{esc(words)}</text>')
        x += 12 + 7.2 * len(words) + 22
    return out
kb = lambda b: f"{b / 1024:.0f} kB"

# ---- figure: the package's ways to run Hazel from a page
def paths_svg():
    W = 640
    boxes = [("interpreted", "hazel-lib.js, 2.9 MB", "Hazel.run, runProgram: the interpreter runs the program", "every game: 0.5 to 6 s to build, then each call interpreted"),
             ("jit", "hazel-lib.js, the same file", "Hazel.jit, jitProgram: compiled to JavaScript in the page", "each call's values cross through Hazel's own, both ways"),
             ("compiled", "compiled.js, 32 to 124 kB", "Hazel.compileProgram, once, ahead of time: no Hazel in the page", "the game's values converted by converters written by hand"),
             ("editor", "editor/, 68 files, 11 MB", "Hazel's own editor, framed by hazel-listings.js", "offline: its fonts and icons in the package")]
    out = ['<rect class="pbox" x="8" y="118" width="120" height="70" rx="8"/><text class="lbl" x="68" y="150" text-anchor="middle">a page</text>'
           '<text class="mut" x="68" y="168" text-anchor="middle">import "hazeljs"</text>']
    for i, (k, f, what, note) in enumerate(boxes):
        y = 10 + i * 76
        out.append(f'<path class="arrow" d="M128 153 C 170 153, 170 {y + 32}, 208 {y + 32}"/>'
                   f'<rect class="pbox {k}" x="210" y="{y}" width="420" height="64" rx="8"/>'
                   f'<text class="lbl" x="222" y="{y + 20}">{esc(f)}</text><text class="mut" x="222" y="{y + 38}">{esc(what)}</text>'
                   f'<text class="mut" x="222" y="{y + 55}">{esc(note)}</text>')
    return f'<svg viewBox="0 0 {W} 316" role="img" aria-label="Four ways a page uses the hazeljs package: the interpreter, the jit, code compiled ahead of time, and the editor">' + "".join(out) + "</svg>"

# ---- figure: every operation, four ways, on one log scale
def ways_svg():
    W, x0, x1 = 640, 262, 628
    lo, hi = -5, 5                      # 10^-5 ms (10 ns) to 10^5 ms (100 s)
    X = lambda ms: x0 + (math.log10(ms) - lo) / (hi - lo) * (x1 - x0)
    out, y = [], 26
    ticks = [(-5, "10 ns"), (-3, "1 µs"), (-1, "0.1 ms"), (1, "10 ms"), (3, "1 s"), (5, "100 s")]
    for e, lab in ticks: out.append(f'<text class="mut" x="{X(10 ** e):.1f}" y="14" text-anchor="{"end" if e == hi else "middle"}">{lab}</text>')
    rows = []
    for title, gs in GROUPS:
        rows.append(("group", title))
        for g in gs:
            for o in [o for o in OPS if o[0] == g]: rows.append(("op", o))
    top = y
    for kind, r in rows:
        if kind == "group":
            y += 6; out.append(f'<text class="grp" x="8" y="{y + 12}">{esc(r)}</text>'); y += 18; continue
        g, name, ms = r
        lab = f"{NAME[g]}: {name}"
        lab = lab if len(lab) <= 44 else lab[:42] + "…"
        vs = [ms[w] for w in WAYS if w in ms]
        out.append(f'<text class="lbl small" x="8" y="{y + 10}">{esc(lab)}</text>'
                   f'<line class="span" x1="{X(min(vs)):.1f}" y1="{y + 6}" x2="{X(max(vs)):.1f}" y2="{y + 6}"/>')
        for w, cls in (("interpreted", "mi"), ("jit", "mj"), ("compiled", "mc"), ("plain JS", "mp")):
            if w in ms:
                out.append(f'<circle class="{cls}" cx="{X(ms[w]):.1f}" cy="{y + 6}" r="4.2"><title>{esc(NAME[g])}, {esc(name)}: {w} {t(ms[w])}</title></circle>')
        y += 15
    for e, _ in ticks: out.insert(0, f'<line class="grid" x1="{X(10 ** e):.1f}" y1="{top - 6}" x2="{X(10 ** e):.1f}" y2="{y}"/>')
    y += 10
    out += legend([("interpreted", "mi"), ("jit", "mj"), ("compiled ahead of time", "mc"), ("plain JS", "mp")], 12, y)
    return f'<svg viewBox="0 0 {W} {y + 12}" role="img" aria-label="Every operation of the 17 games, timed four ways, on a log scale from 10 nanoseconds to 100 seconds">' + "".join(out) + "</svg>"

# ---- figure: where the jit's time goes: in compiled code, or crossing
def cross_svg():
    W, x0, w = 640, 262, 200
    rows = sorted(OPS, key=share, reverse=True)
    out, y = [], 6
    for g, name, ms in rows:
        s = share((g, name, ms)); lab = f"{NAME[g]}: {name}"; lab = lab if len(lab) <= 44 else lab[:42] + "…"
        out.append(f'<text class="lbl small" x="8" y="{y + 10}">{esc(lab)}</text>'
                   f'<rect class="mc" x="{x0}" y="{y}" width="{w * (1 - s):.1f}" height="11"/>'
                   f'<rect class="mj" x="{x0 + w * (1 - s):.1f}" y="{y}" width="{w * s:.1f}" height="11"><title>{s * 100:.0f}% crossing</title></rect>'
                   f'<text class="mut small" x="{x0 + w + 6}" y="{y + 10}">jit {t(ms["jit"])}, ahead of time {t(ms["compiled"])}</text>')
        y += 14
    y += 8
    out.append(f'<line class="grid" x1="{x0 + w / 2}" y1="0" x2="{x0 + w / 2}" y2="{y - 6}"/>'
               f'<rect class="mc" x="{x0}" y="{y}" width="10" height="10"/><text class="mut" x="{x0 + 14}" y="{y + 9}">the compiled code’s own work</text>'
               f'<rect class="mj" x="{x0 + 200}" y="{y}" width="10" height="10"/><text class="mut" x="{x0 + 214}" y="{y + 9}">crossing: the values in and out</text>')
    return f'<svg viewBox="0 0 {W} {y + 16}" role="img" aria-label="Each operation\'s jit time split into the compiled code\'s own work and the crossing, sorted by the crossing\'s share">' + "".join(out) + "</svg>"


# ---- figure (2026-11-24): each operation's jit time over its time ahead of time, the day before and with the converters
def conv_svg():
    W, x0, w = 640, 262, 300
    lo, hi = math.log10(0.01), math.log10(3000)
    X = lambda r: x0 + w * (math.log10(min(max(r, 0.01), 3000)) - lo) / (hi - lo)
    rows = sorted(CONV, key=lambda c: c[2]["jit"] / c[2]["compiled"], reverse=True)
    out, y = [], 18
    for k, v in enumerate([0.01, 0.1, 1, 10, 100, 1000]):
        out.append(f'<line class="grid" x1="{X(v):.1f}" y1="12" x2="{X(v):.1f}" y2="{18 + 14 * len(rows)}"/><text class="mut small" x="{X(v):.1f}" y="9" text-anchor="middle">{v:g}×</text>')
    for g, name, o, n in rows:
        a, b = o["jit"] / o["compiled"], n["jit"] / n["compiled"]; lab = f"{NAME[g]}: {name}"; lab = lab if len(lab) <= 44 else lab[:42] + "…"
        out.append(f'<text class="lbl small" x="8" y="{y + 9}">{esc(lab)}</text><line x1="{X(a):.1f}" y1="{y + 5}" x2="{X(b):.1f}" y2="{y + 5}" stroke="var(--muted)" stroke-width="1"/>'
                   f'<circle class="cvo" cx="{X(a):.1f}" cy="{y + 5}" r="3.6"><title>the day before: jit {t(o["jit"])}, ahead of time {t(o["compiled"])}</title></circle>'
                   f'<circle class="cvn" cx="{X(b):.1f}" cy="{y + 5}" r="3.6"><title>with the converters: jit {t(n["jit"])}, ahead of time {t(n["compiled"])}</title></circle>'
                   f'<text class="mut small" x="{x0 + w + 8}" y="{y + 9}">{t(o["jit"])} → {t(n["jit"])}</text>')
        y += 14
    out.append(f'<line x1="{X(1):.1f}" y1="12" x2="{X(1):.1f}" y2="{y}" stroke="var(--ink)" stroke-width="1.2"/>')
    y += 10
    out += legend([("the day before (build 2)", "cvo"), ("with the converters (build 5)", "cvn")], 12, y + 5)
    return f'<svg viewBox="0 0 {W} {y + 20}" role="img" aria-label="Each operation\'s time through the jit as a multiple of its time ahead of time, the day before and with the converters">' + "".join(out) + "</svg>"

# ---- figure: building a game's rules: interpreted, jit; and the ahead-of-time file's size
def once_svg():
    W, x0, w = 640, 150, 330
    mx = max(G[g]["once"]["interpretedBuildMs"] for g in ORDER)
    out, y = [], 6
    for g in sorted(ORDER, key=lambda g: -G[g]["once"]["interpretedBuildMs"]):
        o = G[g]["once"]
        out.append(f'<text class="lbl small" x="8" y="{y + 15}">{esc(NAME[g])}</text>')
        for k, (v, cls) in enumerate(((o["interpretedBuildMs"], "mi"), (o["jitBuildMs"], "mj"))):
            out.append(f'<rect class="{cls}" x="{x0}" y="{y + k * 11}" width="{w * v / mx:.1f}" height="10"/>'
                       f'<text class="mut small" x="{x0 + w * v / mx + 4:.1f}" y="{y + k * 11 + 9}">{t(v)}</text>')
        out.append(f'<text class="mut small" x="{W - 8}" y="{y + 15}" text-anchor="end">{kb(o["wrappedBytes"])}</text>')
        y += 27
    out.append(f'<text class="mut small" x="{W - 8}" y="{y + 8}" text-anchor="end">ahead of time: the file</text>'
               f'<rect class="mi" x="{x0}" y="{y}" width="10" height="10"/><text class="mut" x="{x0 + 14}" y="{y + 9}">interpreted: build</text>'
               f'<rect class="mj" x="{x0 + 130}" y="{y}" width="10" height="10"/><text class="mut" x="{x0 + 144}" y="{y + 9}">jit: build and compile</text>')
    return f'<svg viewBox="0 0 {W} {y + 16}" role="img" aria-label="Milliseconds to build each game\'s rules interpreted and with the jit, and the size of its ahead-of-time file">' + "".join(out) + "</svg>"

# ---- the branch against dev, by part
DIFF = json.load(open(os.path.join(DATA, "diff.json")))
def part(p):
    if "HazelJit" in p: return "hazel-jit"
    if p.startswith("test/"): return "tests"
    if "HazelLib" in p or p.startswith("docs/") or p == "src/web/www/dune": return "the library"
    if "ModuleProgram" in p: return "programs of modules"
    if "/embed/" in p or "embed.css" in p or p.endswith(("Main.re", "CodeEditable.re", "ContextMenu.re", "ContextMenu.rei", "Menu.re", "JsUtil.re")): return "embed mode"
    if p.startswith("licenses/") or "/fonts" in p or p.endswith(("variables.css", "index.html", "style.css")): return "fonts, icons, licenses"
    if p == "src/web/dune": return "the library"
    return "changes to dev’s own code"
PARTS = ["hazel-jit", "the library", "programs of modules", "embed mode", "fonts, icons, licenses", "changes to dev’s own code", "tests"]
BYPART = {k: {"added": 0, "deleted": 0, "files": 0} for k in PARTS}
for f in DIFF["files"]:
    b = BYPART[part(f["path"])]; b["files"] += 1; b["added"] += f["added"] or 0; b["deleted"] += f["deleted"] or 0
ADDED = sum(b["added"] for b in BYPART.values()); DELETED = sum(b["deleted"] for b in BYPART.values())
def diff_svg():
    W, x0, w = 640, 190, 330
    mx = max(b["added"] for b in BYPART.values())
    out, y = [], 6
    for k in PARTS:
        b = BYPART[k]
        out.append(f'<text class="lbl small" x="8" y="{y + 11}">{esc(k)}</text><rect class="mc" x="{x0}" y="{y}" width="{w * b["added"] / mx:.1f}" height="13"/>'
                   f'<text class="mut small" x="{x0 + w * b["added"] / mx + 5:.1f}" y="{y + 11}">{b["added"]:,} lines, {b["files"]} files</text>')
        y += 20
    return f'<svg viewBox="0 0 {W} {y + 4}" role="img" aria-label="Lines the hazeljs branch adds over dev, by part">' + "".join(out) + "</svg>"
def diff_table():
    rows = "".join(f'<tr><td>{esc(k)}</td><td>{BYPART[k]["files"]}</td><td>{BYPART[k]["added"]:,}</td><td>{BYPART[k]["deleted"]:,}</td></tr>' for k in PARTS)
    return (f'<table class="nums"><thead><tr><th>part</th><th>files</th><th>lines added</th><th>lines removed</th></tr></thead><tbody>{rows}'
            f'<tr><td><b>all</b></td><td><b>{len(DIFF["files"])}</b></td><td><b>{ADDED:,}</b></td><td><b>{DELETED}</b></td></tr></tbody></table>')

# ---- the PRs
PRS = {p["number"]: p for p in json.load(open(os.path.join(DATA, "prs.json")))["prs"] if "headRefName" in p}
GIVES = {2857: "The one PR: everything below that the package uses, merged with dev and ported to Jane Street Core, plus hazel-jit's compiler and the code font's license.",
         2711: "The library, first version: <code>Hazel.analyze</code> and <code>Hazel.run</code> from any page.",
         2719: "Programs of named modules (<code>analyzeProgram</code>, <code>runProgram</code>), and Hazel in another page's frame.",
         2814: "Embed mode: editable cells, one module at a time, go to definition across cells.",
         2837: "IBM Plex Sans as the interface font, in place of a Helvetica Neue that Hazel had no license to ship.",
         2842: "Material Icons shipped with Hazel, so nothing loads from Google.",
         2817: "hazel-jit on the livelits line: livelit views compiled. #2857's compiler is this one's, from <code>trial/794-games-aot</code>, with the livelit-only forms taken out.",
         2828: "SInt with 64 bits everywhere, overflow an error. Not in #2857 yet."}
def pr_table():
    rows = []
    for n in [2857, 2711, 2719, 2814, 2837, 2842, 2817, 2828]:
        p = PRS[n]
        state = ("draft" if p["isDraft"] else "open") if p["state"] == "OPEN" else p["state"].lower()
        rows.append(f'<tr><td>#{n}</td><td><code>{esc(p["headRefName"])}</code> into <code>{esc(p["baseRefName"])}</code></td><td>{state}</td>'
                    f'<td>+{p["additions"]:,} / −{p["deletions"]:,}</td><td class="l">{GIVES[n]}</td></tr>')
    return ('<div class="tw"><table class="nums"><thead><tr><th>PR</th><th>branch</th><th>state</th><th>lines</th><th class="l">what it gives the package</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')

# ---- the numbers, game by game
def ops_table():
    rows = []
    for title, gs in GROUPS:
        rows.append(f'<tr class="grp"><td colspan="7">{esc(title)}</td></tr>')
        for g in gs:
            for _, name, ms in [o for o in OPS if o[0] == g]:
                cell = lambda w: t(ms[w]) if w in ms else "–"
                rows.append(f'<tr><td>{esc(NAME[g])}: {esc(name)}</td>' + "".join(f"<td>{cell(w)}</td>" for w in WAYS) +
                            f'<td>{x_(ms["interpreted"] / ms["jit"])}</td><td>{x_(ms["jit"] / ms["compiled"])}</td></tr>')
    return ('<div class="tw"><table class="nums"><thead><tr><th>operation</th><th>interpreted</th><th>jit</th><th>ahead of time</th><th>plain JS</th>'
            f'<th>jit over interpreted</th><th>ahead of time over jit</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
def once_table():
    rows = "".join(f'<tr><td>{esc(NAME[g])}</td><td>{t(G[g]["once"]["interpretedBuildMs"])}</td><td>{t(G[g]["once"]["jitBuildMs"])}</td>'
                   f'<td>{t(G[g]["once"]["compileMs"])}</td><td>{kb(G[g]["once"]["compiledJsBytes"])}</td><td>{kb(G[g]["once"]["wrappedBytes"])}</td>'
                   f'<td class="l">{esc(G[g]["machine"]["model"])}</td></tr>' for g in ORDER)
    return ('<div class="tw"><table class="nums"><thead><tr><th>game</th><th>interpreted: build</th><th>jit: build and compile</th><th>compileProgram</th>'
            f'<th>compiled program</th><th>ahead-of-time file</th><th class="l">the runner’s processor</th></tr></thead><tbody>{rows}</tbody></table></div>')

IJ, JC, IC, CP, IP = ratio("interpreted", "jit"), ratio("jit", "compiled"), ratio("interpreted", "compiled"), ratio("compiled", "plain JS"), ratio("interpreted", "plain JS")
worst = max(LIGHT, key=lambda o: o[2]["jit"] - o[2]["compiled"])
ms30 = next(o for o in OPS if o[0] == "minesweeper" and o[1] == "16 by 30: a cell opened")
dig = {o[1]: o[2] for o in OPS if o[0] == "dig"}
B = lambda k: [G[g]["once"][k] for g in ORDER]
plain_games = [g for g in ORDER if any("plain JS" in o[2] for o in OPS if o[0] == g)]
models = sorted({G[g]["machine"]["model"] for g in ORDER})
EXTRA = """
  .cvo { fill: var(--warn); } .cvn { fill: var(--good); }
  figure.chart svg { width: 100%; height: auto; display: block; }
  svg .lbl { fill: var(--ink); font: 13px system-ui, sans-serif; } svg .mut { fill: var(--muted); font: 12px system-ui, sans-serif; }
  svg .small { font-size: 11px; } svg .grp { fill: var(--ink); font: 700 12px system-ui, sans-serif; }
  svg .grid { stroke: var(--line); } svg .span { stroke: var(--line); stroke-width: 2; }
  svg .mi { fill: #6b737d; } svg .mj { fill: #eb6834; } svg .mc { fill: #2a78d6; } svg .mp { fill: #2e9e5b; }
  svg .pbox { fill: var(--paper); stroke: var(--line); stroke-width: 1.5; } svg .pbox.interpreted { stroke: #6b737d; } svg .pbox.jit { stroke: #eb6834; }
  svg .pbox.compiled { stroke: #2a78d6; } svg .pbox.editor { stroke: #2e9e5b; } svg .arrow { fill: none; stroke: var(--muted); stroke-width: 1.5; }
  table.nums td, table.nums th { text-align: right; font-variant-numeric: tabular-nums; } table.nums td:first-child, table.nums th:first-child { text-align: left; }
  table.nums td.l, table.nums th.l { text-align: left; } table.nums tr.grp td { font-weight: 700; padding-top: 0.8em; }
  .tw { overflow-x: auto; margin: 0.6em 0 1em; } .tw table { min-width: 720px; }
  ol.decide > li { margin-bottom: 0.9em; }
"""
FIGS = {
    "updated": updated, "games": str(len(ORDER)), "ops": str(len(OPS)), "paths": paths_svg(), "ways": ways_svg(), "cross": cross_svg(), "once": once_svg(),
    "diff": diff_svg(), "diff_table": diff_table(), "pr_table": pr_table(), "ops_table": ops_table(), "once_table": once_table(),
    "added": f"{ADDED:,}", "deleted": str(DELETED), "files": str(len(DIFF["files"])), "ahead": str(DIFF["commits_ahead"]), "behind": str(DIFF["commits_behind"]),
    "jit_lines": f'{BYPART["hazel-jit"]["added"]:,}', "test_lines": f'{BYPART["tests"]["added"]:,}', "own_lines": f'{BYPART["changes to dev’s own code"]["added"]:,}',
    "ij_gm": x_(gm(IJ)), "ij_min": x_(min(IJ)), "ij_max": x_(max(IJ)), "ic_gm": x_(gm(IC)), "ic_min": x_(min(IC)), "ic_max": x_(max(IC)),
    "jc_gm": x_(gm(JC)), "jc_max": x_(max(JC)), "cp_gm": x_(gm(CP)), "cp_min": x_(min(CP)), "cp_max": x_(max(CP)), "cp_n": str(len(CP)),
    "ip_gm": x_(gm(IP)), "plain_games": str(len(plain_games)),
    "heavy_n": str(len(HEAVY)), "heavy_min": x_(min(o[2]["interpreted"] / o[2]["jit"] for o in HEAVY)), "heavy_max": x_(max(o[2]["interpreted"] / o[2]["jit"] for o in HEAVY)),
    "heavy_jc": x_(max(o[2]["jit"] / o[2]["compiled"] for o in HEAVY)),
    "light_n": str(len(LIGHT)), "light_min": x_(min(o[2]["interpreted"] / o[2]["jit"] for o in LIGHT)), "light_max": x_(max(o[2]["interpreted"] / o[2]["jit"] for o in LIGHT)),
    "worst_name": f"{NAME[worst[0]]}, {worst[1]}", "worst_j": t(worst[2]["jit"]), "worst_c": t(worst[2]["compiled"]),
    "ms30_i": t(ms30[2]["interpreted"]), "ms30_j": t(ms30[2]["jit"]), "ms30_c": t(ms30[2]["compiled"]), "ms30_p": t(ms30[2]["plain JS"]),
    "dig_step_i": t(dig["a step"]["interpreted"]), "dig_step_j": t(dig["a step"]["jit"]), "dig_step_c": t(dig["a step"]["compiled"]),
    "dig_robot_i": t(dig["the robot's choice"]["interpreted"]), "dig_robot_j": t(dig["the robot's choice"]["jit"]), "dig_robot_c": t(dig["the robot's choice"]["compiled"]),
    "bi_min": t(min(B("interpretedBuildMs"))), "bi_max": t(max(B("interpretedBuildMs"))), "bj_min": t(min(B("jitBuildMs"))), "bj_max": t(max(B("jitBuildMs"))),
    "bj_share_min": f'{min(G[g]["once"]["jitBuildMs"] / G[g]["once"]["interpretedBuildMs"] for g in ORDER) * 100:.0f}%',
    "bj_share_max": f'{max(G[g]["once"]["jitBuildMs"] / G[g]["once"]["interpretedBuildMs"] for g in ORDER) * 100:.0f}%',
    "aot_min": kb(min(B("wrappedBytes"))), "aot_max": kb(max(B("wrappedBytes"))), "runtime_kb": kb(G["dig"]["once"]["runtimeBytes"]),
    "dig_bi": t(G["dig"]["once"]["interpretedBuildMs"]), "dig_bj": t(G["dig"]["once"]["jitBuildMs"]),
    "n_models": str(len(models)), "node": G["dig"]["machine"]["node"],
    "conv": conv_svg(), "cv_gm": x_(1 / gm(cvr("jit"))), "cv_old_ja": x_(gm([o["jit"] / o["compiled"] for _, _, o, n in CONV])), "cv_new_ja": f'{gm([n["jit"] / n["compiled"] for _, _, o, n in CONV]):.1f}×',
    "cv_near": str(sum(1 for _, _, o, n in CONV if n["jit"] / n["compiled"] <= 1.5)),
    "cv_i": f'{gm(cvr("interpreted")):.2f}×', "cv_c": f'{gm(cvr("compiled")):.2f}×', "cv_c_min": f'{min(cvr("compiled")):.2f}×', "cv_c_max": f'{max(cvr("compiled")):.2f}×',
    "cv_pin_old": t(next(o["jit"] for g, nm, o, n in CONV if g == "pinball" and nm == "a board")), "cv_pin_new": t(next(n["jit"] for g, nm, o, n in CONV if g == "pinball" and nm == "a board")),
    "cv_ms30_j": t(next(n["jit"] for g, nm, o, n in CONV if g == "minesweeper" and nm.startswith("16 by 30: a cell"))),
    "cv_b_worst": ", ".join(f'{NAME[g]} {t(G[g]["once"]["jitBuildMs"])} → {t(CV[g]["once"]["jitBuildMs"])}' for g in sorted(ORDER, key=lambda g: -CV[g]["once"]["jitBuildMs"] / G[g]["once"]["jitBuildMs"])[:3]),
}
body = open(os.path.join(HERE, "body.html")).read()
for k, v in FIGS.items(): body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{(\w+)\}\}", body)
assert not left, left
TITLE = "Hazel as an npm Package: What to Decide Next"
DESC = (f"Where the hazeljs package stands at 0.0.11, for Matthew and Cyrus: one PR (#2857) that it is built from, how that branch differs "
        f"from dev, and every game in hazeljs-examples timed four ways. The package's jit runs the games {x_(gm(IJ))} as fast as its interpreter "
        f"(geometric mean over {len(OPS)} operations), from {x_(min(IJ))} to {x_(max(IJ))}: on searches it is as fast as code compiled ahead of time, "
        f"but on light calls with a large state most of its time goes to converting values in and out. Compiled ahead of time, the games run "
        f"{x_(gm(IC))} as fast as interpreted, and the five written by hand in JavaScript about {x_(gm(CP))} faster again. A day later, with #2857's converters by declared type, "
        f"the jit ran them {x_(1 / gm(cvr('jit')))} as fast again on the benchmark's repeated positions, about even with code compiled ahead of time. Then the decisions before it merges into dev.")
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{esc(DESC)}\">\n<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)

# the series card's thumbnail: the four ways' speed against the interpreter, on a log scale
def thumb(mode):
    base = ".h{fill:#1f2328;font:700 15px system-ui,sans-serif}.m{fill:#5b6470;font:10px system-ui,sans-serif}.k{fill:#1f2328;font:700 12px system-ui,sans-serif}.i{fill:#6b737d}.j{fill:#eb6834}.c{fill:#2a78d6}.p{fill:#2e9e5b}"
    dark = ".h{fill:#e8e6e3}.m{fill:#a2a9b3}.k{fill:#e8e6e3}.i{fill:#8b939d}"
    style = base + ("\n" + dark if mode == "dark" else "\n@media (prefers-color-scheme: dark) {" + dark + "}" if mode == "auto" else "")
    vals = [("interpreted", 1, "i"), ("jit", gm(IJ), "j"), ("ahead of time", gm(IC), "c"), ("plain JS", gm(IP), "p")]
    top = math.log10(max(v for _, v, _ in vals))
    bars = "".join(f'<text class="m" x="16" y="{70 + i * 26}">{n}</text><rect class="{c}" x="100" y="{60 + i * 26}" width="{max(3, 160 * math.log10(v) / top):.1f}" height="13"/>'
                   f'<text class="k" x="{106 + max(3, 160 * math.log10(v) / top):.1f}" y="{71 + i * 26}">{x_(v)}</text>' for i, (n, v, c) in enumerate(vals))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" width="320" height="200">\n<style>{style}\n</style>\n'
            '<text class="h" x="16" y="26">The hazeljs package</text>\n<text class="m" x="16" y="43">17 games: how many times as fast as the interpreter</text>\n'
            f'{bars}<text class="m" x="16" y="186">geometric means; log scale; plain JS: 5 games</text>\n</svg>\n')
os.makedirs(os.path.join(HERE, "img"), exist_ok=True)
for name, mode in [("thumb-light.svg", "light"), ("thumb-dark.svg", "dark"), ("thumb.svg", "auto")]: open(os.path.join(HERE, "img", name), "w").write(thumb(mode))
meta = {"title": TITLE, "blurb": DESC,
        "builds": {"package": "hazeljs 0.0.11 (hazelgrove/hazeljs editor-in-package b149ed58f2), not on npm",
                   "hazel": "hazelgrove/hazel 98c482395d (branch hazeljs, #2857): hazel-lib.js, byte for byte the deploy's",
                   "examples": "matthewhammer/hazeljs-examples a4a0a88 (bench/package-0.0.11): the games' rules, compiled.js converters and plain.js as of 0.0.74 (d3e8d79), and node/package-bench.mjs",
                   "run": "GitHub Actions run 45247119864 (workflow package bench), 2026-11-23, one runner per game, Node " + G["dig"]["machine"]["node"]},
        "measures": {"ms": "milliseconds a call: the median of batches (as many calls as take at least 1 ms), the interpreter at least 3 batches and 1.5 s, the others at least 30 and 0.3 s",
                     "interpretedBuildMs": "Hazel.runProgram on the game's rules, once", "jitBuildMs": "Hazel.jitProgram on the same, once (analysis, compiling, running the compiled modules)",
                     "compileMs": "Hazel.compileProgram on the same, once", "wrappedBytes": "the ahead-of-time file: the runtime, the compiled program and the page's converters",
                     "same": "the way's answer equals the ahead-of-time code's (numbers to a relative 1e-9); every one is true"},
        "ways": {"interpreted": "Hazel.runProgram's value", "jit": "Hazel.jitProgram's value", "compiled": "Hazel.compileProgram's program and runtime in the page's compiled.js, its converters",
                 "plain JS": "<game>/plain.js, five games"}}
json.dump(meta, open(os.path.join(DATA, "meta.json"), "w"), indent=1, ensure_ascii=False)
print("wrote 063/index.html;", updated)
