#!/usr/bin/env python3
"""^report(60): How Fast Is Hazel? Five Games, Three Ways. Matthew Hammer, 2026-11-20 (^ticket(797)): "let's write a report
to help answer a question from Cyrus about the speed of hazel, versus hazeljit, versus plain JS. For each game, let's have a
plain JS version ... equivalent in terms of game def, logic, and strategy. Please create a report that does a 3-way time
comparison for each game", then "let's document the role of randomness in the report we do for each strategy, and also,
the source of the cost of the strategy (search tree depth, or whatever)".

Writes 060/index.html from body.html and data/<game>.json (hazeljs-examples' node/three-way.mjs, run by its workflow
'three-way timing' on one GitHub runner; data/machine.txt says which)."""
import html, json, math, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
GAMES = ["solitaire", "minesweeper", "go", "checkers", "mahjong"]
NAMES = {"solitaire": "Solitaire", "minesweeper": "Minesweeper", "go": "Go", "checkers": "Checkers", "mahjong": "Mahjong"}
DATA = os.environ.get("DATA060", os.path.join(HERE, "data"))
D = {g: json.load(open(os.path.join(DATA, g + ".json"))) for g in GAMES}
META = json.load(open(os.path.join(DATA, "meta.json")))
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
esc = lambda s: html.escape(str(s), quote=True)

HZ, JIT, NB, NUM, JS = "hazeljs", "hazel-jit", "hazel-jit, no step budget", "hazel-jit, no budget, plain numbers", "plain JS"
THREE = [(HZ, "s1", "circle"), (JIT, "s2", "square"), (JS, "s3", "diamond")]

def fmt(ms):
    if ms is None: return "—"
    if ms >= 1000: return f"{ms / 1000:.2f} s" if ms < 10000 else f"{ms / 1000:.1f} s"
    if ms >= 10: return f"{ms:.0f} ms"
    if ms >= 1: return f"{ms:.1f} ms"
    if ms >= 0.01: return f"{ms:.3f} ms"
    if ms >= 0.001: return f"{ms * 1000:.2f} µs"
    return f"{ms * 1000:.3f} µs"
def times(x): return "—" if x is None else f"{x:,.0f}×" if x >= 100 else f"{x:.0f}×" if x >= 10 else f"{x:.1f}×"
def ms_of(row, way):
    v = row.get(way)
    return v["ms"] if v else None
def geo(xs):
    xs = [x for x in xs if x and x > 0]
    return math.exp(sum(math.log(x) for x in xs) / len(xs)) if xs else None

def ops_of(g): return [r for r in D[g]["ops"] if not r.get("boundary")]
def bounds_of(g): return [r for r in D[g]["ops"] if r.get("boundary")]

# ---- per game: speed-ups, as geometric means over the operations timed both ways
SUM = {}
for g in GAMES:
    rows = ops_of(g)
    hj = [ms_of(r, HZ) / ms_of(r, JIT) for r in rows if ms_of(r, HZ) and ms_of(r, JIT)]
    jp = [ms_of(r, JIT) / ms_of(r, JS) for r in rows if ms_of(r, JIT) and ms_of(r, JS)]
    hp = [ms_of(r, HZ) / ms_of(r, JS) for r in rows if ms_of(r, HZ) and ms_of(r, JS)]
    nb = [ms_of(r, NB) / ms_of(r, JIT) for r in rows if ms_of(r, NB) and ms_of(r, JIT)]
    nu = [ms_of(r, NUM) / ms_of(r, JIT) for r in rows if ms_of(r, NUM) and ms_of(r, JIT)]
    SUM[g] = {"hz_jit": geo(hj), "hz_jit_range": [min(hj), max(hj)] if hj else None, "jit_js": geo(jp), "jit_js_range": [min(jp), max(jp)] if jp else None,
              "hz_js": geo(hp), "nb": geo(nb), "num": geo(nu), "n": len(rows), "same": all(r.get("same", True) for r in D[g]["ops"]) and all(w.get("same", True) for w in D[g]["games"])}
ALL = {"hz_jit": geo([SUM[g]["hz_jit"] for g in GAMES]), "jit_js": geo([SUM[g]["jit_js"] for g in GAMES]), "hz_js": geo([SUM[g]["hz_js"] for g in GAMES])}

# ---- figure 1: every operation, the three ways, on one log scale
def dots():
    rows = []
    for g in GAMES:
        rows.append(("head", NAMES[g], None))
        for r in ops_of(g): rows.append(("op", f"{r['name']} · {r['where']}", r))
    lo, hi = -4, 5  # 0.1 µs to 100 s, in ms
    W, L, R, top, rh = 780, 360, 14, 34, 17
    pw = W - L - R
    x = lambda ms: L + (math.log10(ms) - lo) / (hi - lo) * pw
    H = top + rh * len(rows) + 16
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="f1t"><title id="f1t">Every operation of the five games, timed three ways: hazeljs, hazel-jit, plain JavaScript; a log scale from 0.1 microseconds to 100 seconds</title>']
    for d in range(lo, hi + 1):
        xx = x(10 ** d)
        lab = {-4: "0.1 µs", -3: "1 µs", -2: "10 µs", -1: "0.1 ms", 0: "1 ms", 1: "10 ms", 2: "0.1 s", 3: "1 s", 4: "10 s", 5: "100 s"}[d]
        out.append(f'<line class="ax" x1="{xx:.1f}" x2="{xx:.1f}" y1="{top - 6}" y2="{H - 12}"/><text class="axl" x="{xx:.1f}" y="{top - 12}" text-anchor="middle">{lab}</text>')
    y = top
    for kind, label, r in rows:
        if kind == "head":
            out.append(f'<text class="gh" x="4" y="{y + 12}">{esc(label)}</text>'); y += rh; continue
        out.append(f'<text class="lbl" x="{L - 8}" y="{y + 12}" text-anchor="end">{esc(label)}</text>')
        out.append(f'<line class="row" x1="{L}" x2="{W - R}" y1="{y + 8.5}" y2="{y + 8.5}"/>')
        for way, cls, shape in THREE:
            ms = ms_of(r, way)
            if ms is None: continue
            cx, cy = x(ms), y + 8.5
            mark = (f'<circle class="{cls}" cx="{cx:.1f}" cy="{cy}" r="4.5"/>' if shape == "circle"
                    else f'<rect class="{cls}" x="{cx - 4:.1f}" y="{cy - 4}" width="8" height="8" rx="1"/>' if shape == "square"
                    else f'<path class="{cls}" d="M{cx:.1f} {cy - 5.5}l5.5 5.5l-5.5 5.5l-5.5 -5.5z"/>')
            out.append(f'<g class="mk"><title>{esc(label)}: {way} {fmt(ms)}</title>{mark}<circle class="hit" cx="{cx:.1f}" cy="{cy}" r="9"/></g>')
        y += rh
    out.append("</svg>")
    return "".join(out)

def legend():
    sw = {"circle": '<svg width="12" height="12"><circle class="s1" cx="6" cy="6" r="4.5"/></svg>', "square": '<svg width="12" height="12"><rect class="s2" x="2" y="2" width="8" height="8" rx="1"/></svg>',
          "diamond": '<svg width="12" height="12"><path class="s3" d="M6 0.5l5.5 5.5l-5.5 5.5l-5.5 -5.5z"/></svg>'}
    names = {HZ: "hazeljs, interpreting the Hazel (build 1)", JIT: "hazel-jit, the Hazel compiled (build 2)", JS: "plain JavaScript (build 3)"}
    return '<p class="legend">' + " ".join(f'<span>{sw[shape]} {names[way]}</span>' for way, _, shape in THREE) + "</p>"

# ---- figure 2: the speed-ups per game (geometric means), bars on a log scale
def speedups():
    W, L, top, bh, gap = 760, 120, 26, 15, 22
    lo, hi = 0, 4  # 1x to 10,000x
    pw = W - L - 110
    x = lambda v: L + (math.log10(v) - lo) / (hi - lo) * pw
    H = top + len(GAMES) * (2 * bh + 4 + gap) + 4
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="f2t"><title id="f2t">Per game, how many times faster: hazel-jit than hazeljs, and plain JavaScript than hazel-jit (geometric means over the game\'s operations)</title>']
    for d in range(lo, hi + 1):
        xx = x(10 ** d)
        out.append(f'<line class="ax" x1="{xx:.1f}" x2="{xx:.1f}" y1="{top - 6}" y2="{H - 4}"/><text class="axl" x="{xx:.1f}" y="{top - 10}" text-anchor="middle">{10 ** d:,}×</text>')
    y = top
    for g in GAMES:
        out.append(f'<text class="gh" x="4" y="{y + bh + 4}">{NAMES[g]}</text>')
        for k, cls, what in (("hz_jit", "s2", "hazel-jit over hazeljs"), ("jit_js", "s3", "plain JS over hazel-jit")):
            v = SUM[g][k]
            if v:
                w = max(2, x(v) - L)
                out.append(f'<g class="mk"><title>{NAMES[g]}: {what}, {times(v)}</title><rect class="{cls}" x="{L}" y="{y}" width="{w:.1f}" height="{bh}" rx="3"/></g>'
                           f'<text class="lbl" x="{L + w + 6:.1f}" y="{y + bh - 3}">{times(v)} {what}</text>')
            y += bh + 4
        y += gap
    out.append("</svg>")
    return "".join(out)

# ---- figure 3: where hazel-jit's time goes: the two variants, relative to hazel-jit (1.0), per game
def variants():
    W, L, top, bh, gap = 760, 120, 26, 15, 22
    lo, hi = 0.0, 1.4
    pw = W - L - 150
    x = lambda v: L + (v - lo) / (hi - lo) * pw
    H = top + len(GAMES) * (2 * bh + 4 + gap) + 4
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="f3t"><title id="f3t">hazel-jit\'s time with its step budget taken out, and with plain-number arithmetic too, as a share of hazel-jit\'s own time (1.0), per game</title>']
    for v in (0, 0.25, 0.5, 0.75, 1.0, 1.25):
        xx = x(v)
        out.append(f'<line class="ax{" one" if v == 1.0 else ""}" x1="{xx:.1f}" x2="{xx:.1f}" y1="{top - 6}" y2="{H - 4}"/><text class="axl" x="{xx:.1f}" y="{top - 10}" text-anchor="middle">{v:g}</text>')
    y = top
    for g in GAMES:
        out.append(f'<text class="gh" x="4" y="{y + bh + 4}">{NAMES[g]}</text>')
        for k, cls, what in (("nb", "s4", "no step budget"), ("num", "s5", "and plain numbers")):
            v = SUM[g][k]
            if v:
                w = max(2, x(v) - L)
                out.append(f'<g class="mk"><title>{NAMES[g]}: {what}, {v:.2f} of hazel-jit\'s time</title><rect class="{cls}" x="{L}" y="{y}" width="{w:.1f}" height="{bh}" rx="3"/></g>'
                           f'<text class="lbl" x="{L + w + 6:.1f}" y="{y + bh - 3}">{v:.2f} · {what}</text>')
            y += bh + 4
        y += gap
    out.append("</svg>")
    return "".join(out)

# ---- per game: the table of operations, and of whole games
def table(g):
    head = "<tr><th>Operation</th><th>Position</th><th>hazeljs</th><th>hazel-jit</th><th>no step budget</th><th>and plain numbers</th><th>plain JS</th><th>hazeljs ÷ hazel-jit</th><th>hazel-jit ÷ plain JS</th></tr>"
    body = []
    for r in ops_of(g):
        h, j, n1, n2, p = (ms_of(r, w) for w in (HZ, JIT, NB, NUM, JS))
        body.append(f"<tr><td>{esc(r['name'])}</td><td>{esc(r['where'])}</td>" + "".join(f'<td class="n">{fmt(v)}</td>' for v in (h, j, n1, n2, p)) +
                    f'<td class="n">{times(h / j) if h and j else "—"}</td><td class="n">{times(j / p) if j and p else "—"}</td></tr>')
    for r in bounds_of(g):
        body.append(f'<tr class="bound"><td>{esc(r["name"])}</td><td>{esc(r["where"])}</td><td class="n">—</td><td class="n">{fmt(ms_of(r, JIT))}</td><td class="n" colspan="5">hazel-jit only: the game from hazeljs\'s shapes into hazel-jit\'s and back, which every call through the page\'s functions pays</td></tr>')
    return f'<div class="scroll"><table class="vals"><thead>{head}</thead><tbody>{"".join(body)}</tbody></table></div>'

def wholes(g):
    rows = D[g]["games"]
    if not rows: return ""
    head = "<tr><th>Whole game</th><th>Moves</th><th>hazeljs</th><th>hazel-jit</th><th>no step budget</th><th>and plain numbers</th><th>plain JS</th><th>Same end</th></tr>"
    body = []
    for r in rows:
        moves = next((r[w]["moves"] for w in (JIT, JS, HZ) if r.get(w)), "")
        body.append(f"<tr><td>{esc(r['name'])}</td><td class=\"n\">{moves}</td>" + "".join(f'<td class="n">{fmt(r[w]["ms"]) if r.get(w) else "—"}</td>' for w in (HZ, JIT, NB, NUM, JS)) +
                    f'<td>{"yes" if r.get("same") else "NO"}</td></tr>')
    return f'<div class="scroll"><table class="vals"><thead>{head}</thead><tbody>{"".join(body)}</tbody></table></div>'

def builds():
    b = D["checkers"]["builds"]
    jits = ", ".join(f'{NAMES[g]} <code>{esc(D[g]["builds"][JIT])}</code>' for g in GAMES)
    return ("<div class=\"scroll\"><table class=\"vals\"><thead><tr><th>Build</th><th>What runs the rules</th><th>From</th></tr></thead><tbody>"
            f"<tr><td>1 · hazeljs</td><td>Hazel’s interpreter, as the pages ran their rules until 0.0.34: the game’s <code>rules/*.hz</code> built by <code>Hazel.runProgram</code></td><td>hazeljs {esc(b[HZ])} from npm</td></tr>"
            f"<tr><td>2 · hazel-jit</td><td>The same Hazel compiled ahead of time to JavaScript by hazel-jit, wrapped by <code>tools/make-compiled.py</code> with adapters for the page’s values (<code>compiled.js</code>)</td><td>hazelgrove/hazel <code>trial/794-games-aot</code>: {jits}</td></tr>"
            f"<tr><td>2a · no step budget</td><td>Build 2 with the step budget’s check taken out of every compiled function</td><td>made from build 2 by <code>node/three-way.mjs</code>, for timing only</td></tr>"
            f"<tr><td>2b · and plain numbers</td><td>Build 2a with Hazel’s exact-integer <code>+ - * /</code> replaced by plain number arithmetic</td><td>made from build 2a likewise</td></tr>"
            f"<tr><td>3 · plain JS</td><td>The same game, rules and strategy written in plain JavaScript (<code>plain.js</code>)</td><td>hazeljs-examples <code>{esc(b['examples'])}</code></td></tr>"
            "</tbody></table></div>")

EXTRA = """
  ol.outline > li { margin: 4px 0; } .muted { color: var(--muted); }
  :root { --s1: #2a78d6; --s2: #eb6834; --s3: #1baf7a; --s4: #8a63d2; --s5: #c06a9a; }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #9b7be0; --s5: #cf7aa9; } }
  :root[data-theme="dark"] { --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #9b7be0; --s5: #cf7aa9; }
  .scroll { overflow-x: auto; max-width: 100%; }
  table.vals { border-collapse: collapse; margin: 0.6em 0 1em; font-size: 0.86em; }
  table.vals th, table.vals td { padding: 4px 8px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
  table.vals td.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; } table.vals th { font-weight: 600; }
  table.vals tr.bound td { color: var(--muted); font-size: 0.95em; }
  figure.chart { margin: 1em 0 1.4em; } figure.chart svg { width: 100%; height: auto; display: block; }
  figure.chart figcaption { color: var(--muted); font-size: 0.88em; margin-top: 4px; }
  svg .s1 { fill: var(--s1); } svg .s2 { fill: var(--s2); } svg .s3 { fill: var(--s3); } svg .s4 { fill: var(--s4); } svg .s5 { fill: var(--s5); }
  svg circle.s1, svg rect.s2, svg path.s3 { stroke: var(--bg); stroke-width: 1.5; }
  svg .hit { fill: transparent; } svg .mk:hover > :not(.hit) { stroke: var(--ink); stroke-width: 1.5; }
  svg .lbl { fill: var(--ink); font: 11.5px system-ui, sans-serif; } svg .gh { fill: var(--ink); font: 600 12.5px system-ui, sans-serif; }
  svg .ax { stroke: var(--line); } svg .ax.one { stroke: var(--muted); stroke-dasharray: 3 3; } svg .axl { fill: var(--muted); font: 11px system-ui, sans-serif; }
  svg .row { stroke: var(--line); stroke-opacity: 0.5; }
  figure.chart p.legend svg { width: 12px; height: 12px; display: inline-block; flex: none; }
  p.legend { display: flex; flex-wrap: wrap; gap: 4px 18px; font-size: 0.88em; margin: 0.4em 0; } p.legend span { display: inline-flex; gap: 6px; align-items: center; }
  .cards3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 0.8em 0 1.2em; }
  .cards3 .card { border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; background: var(--paper); }
  .cards3 .big { font-size: 1.9em; font-weight: 700; line-height: 1.1; font-variant-numeric: tabular-nums; } .cards3 .what { color: var(--muted); font-size: 0.88em; }
"""

def card(v, what): return f'<div class="card"><div class="big">{times(v)}</div><div class="what">{what}</div></div>'
FIGS = {
  "updated": updated, "dots": dots(), "legend": legend(), "speedups": speedups(), "variants": variants(), "builds": builds(),
  "cards": '<div class="cards3">' + card(ALL["hz_jit"], "hazel-jit over hazeljs: the compiled Hazel against the interpreter") +
           card(ALL["jit_js"], "plain JavaScript over hazel-jit: the same game written in JavaScript") +
           card(ALL["hz_js"], "plain JavaScript over hazeljs") + "</div>",
  "machine": esc(META["machine"]), "run": META["run"], "run_url": META["run_url"], "when": esc(META["when"]),
  "n_ops": str(sum(SUM[g]["n"] for g in GAMES)),
  "all_hz_jit": times(ALL["hz_jit"]), "all_jit_js": times(ALL["jit_js"]), "all_hz_js": times(ALL["hz_js"]),
}
for g in GAMES:
    FIGS[f"table_{g}"] = table(g); FIGS[f"whole_{g}"] = wholes(g)
    S = SUM[g]
    FIGS[f"hz_jit_{g}"] = times(S["hz_jit"]); FIGS[f"jit_js_{g}"] = times(S["jit_js"]); FIGS[f"hz_js_{g}"] = times(S["hz_js"])
    FIGS[f"nb_{g}"] = f"{S['nb']:.2f}" if S["nb"] else "—"; FIGS[f"num_{g}"] = f"{S['num']:.2f}" if S["num"] else "—"
for k, v in META.get("numbers", {}).items(): FIGS[k] = v

body = open(os.path.join(HERE, "body.html")).read()
for k, v in FIGS.items():
    body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{(\w+)\}\}", body)
assert not left, left
TITLE = "How Fast Is Hazel? Five Games, Three Ways"
DESC = META["blurb"]
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{esc(DESC)}\">\n<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
json.dump({"summary": SUM, "all": ALL}, open(os.path.join(DATA, "summary.json"), "w"), indent=1, default=list)
print("wrote 060/index.html;", updated, {g: (round(SUM[g]["hz_jit"] or 0), round(SUM[g]["jit_js"] or 0, 1)) for g in GAMES})
