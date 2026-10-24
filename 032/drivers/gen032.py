#!/usr/bin/env python3
"""^report(32): the 📜 Scripting tab's speed run with JS, Fumola and Hazel as every room's default (^ticket(588)).
Reads data/runs.json: the RESULT lines of tools/checks/scriptspeed588.mjs (kids-choice-games), one per round and mode, from a run on
GitHub's computers; and data/run.json: which run, game commit and Hazel build. Every number shown is a median over the rounds, with
the rounds' range beside it."""
import os, json, html, statistics
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLE = open(os.path.join(R, "..", "025", "drivers", "style.css")).read()
RUNS = json.load(open(os.path.join(R, "data", "runs.json")))
RUN = json.load(open(os.path.join(R, "data", "run.json")))
FIND = json.load(open(os.path.join(R, "data", "findings.json")))
def opt(name):
    f = os.path.join(R, "data", name)
    return json.load(open(f)) if os.path.exists(f) else None
SCALE = opt("scale.json") or []
TRAP = opt("trap-code.json")
CORRECT = opt("correct.json")
esc = lambda s: html.escape(str(s if s is not None else ""))
MODES = [("js", "JS"), ("fumola", "Fumola"), ("hazel", "Hazel")]
MODS = ["Common", "TrapRoom", "TreeRoom", "Square", "World", "Castle"]

def get(r, path):
    for k in path.split("."):
        if not isinstance(r, dict) or k not in r: return None
        r = r[k]
    return r
def vals(mode, path): return [v for v in (get(r, path) for r in RUNS if r["mode"] == mode) if isinstance(v, (int, float))]
def med(mode, path):
    v = vals(mode, path)
    return statistics.median(v) if v else None
def cell(mode, path, unit="ms", digits=0):
    v = vals(mode, path)
    if not v: return "<td class=n>–</td>"
    m = statistics.median(v)
    fmt = (lambda x: f"{x:.{digits}f}") if digits else (lambda x: f"{round(x):,}")
    rng = f" <span class=rng>({fmt(min(v))}–{fmt(max(v))})</span>" if len(v) > 1 and min(v) != max(v) else ""
    return f"<td class=n>{fmt(m)}{(' ' + unit) if unit else ''}{rng}</td>"
def fmt_s(ms): return "–" if ms is None else (f"{ms / 1000:.1f} s" if ms >= 1000 else f"{round(ms)} ms")

rows = [("tab open to Common's box", "tab", "ms", 0), ("engine ready", "engine", "ms", 0)]
rows += [(f"{m}'s tiles ready", f"tiles.{m}", "ms", 0) for m in MODS]
rows += [("loading: median frame", "loadFrames.median", "ms", 1), ("loading: 95th percentile frame", "loadFrames.p95", "ms", 1),
         ("loading: longest frame", "loadFrames.max", "ms", 0), ("loading: frames over 50 ms", "loadFrames.over50", "", 0), ("loading: frames a second", "loadFrames.fps", "", 1),
         ("scrolling each box into view: median frame", "scroll.median", "ms", 1), ("scrolling: 95th percentile", "scroll.p95", "ms", 1), ("scrolling: longest frame", "scroll.max", "ms", 0),
         ("scrolling: frames over 50 ms", "scroll.over50", "", 0), ("scrolling: frames a second", "scroll.fps", "", 1),
         ("visiting each box at max size: median frame", "visit.median", "ms", 1), ("visiting: 95th percentile", "visit.p95", "ms", 1), ("visiting: longest frame", "visit.max", "ms", 0),
         ("visiting: frames over 50 ms", "visit.over50", "", 0), ("visiting: frames a second", "visit.fps", "", 1),
         ("events: the game's call into the script function (median)", "events.script.median", "ms", 3), ("events: the script function, 95th percentile", "events.script.p95", "ms", 3),
         ("events: the script function, longest", "events.script.max", "ms", 3), ("events: the commands it gave, run by the game (median)", "events.commands.median", "ms", 3),
         ("events: the whole event, engine to commands done (median)", "events.whole.median", "ms", 3), ("events: the whole event, longest", "events.whole.max", "ms", 3),
         ("events: a lever pull, at the game's entry point (median)", "events.entry.median", "ms", 3), ("events: a lever pull, longest", "events.entry.max", "ms", 3),
         ("long tasks (over 50 ms), all phases", "long.n", "", 0), ("long tasks' total time", "long.ms", "ms", 0), ("the whole run, tab to end", "total", "ms", 0)]
table = "".join(f"<tr><td>{esc(label)}</td>" + "".join(cell(m, p, u, d) for m, _ in MODES) + "</tr>" for label, p, u, d in rows)

# the picture: time to ready, per engine; Hazel's tiles one bar each
bars = [("JS: tab open", med("js", "tab"), "js"), ("Fumola: engine ready", med("fumola", "engine"), "fumola"), ("Hazel: engine ready", med("hazel", "engine"), "hazel")]
bars += [(f"Hazel: {m}'s tiles", med("hazel", f"tiles.{m}"), "hazel") for m in MODS]
mx = max([b[1] for b in bars if b[1]] or [1])
W, H, L = 640, 26 * len(bars) + 30, 190
svg = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Time from the tab opened to each engine, and each of Hazel\'s tiles, ready (median of the rounds)">']
for i, (lab, v, k) in enumerate(bars):
    y = 10 + i * 26
    w = 0 if not v else max(2, (W - L - 80) * v / mx)
    svg.append(f'<text x="{L - 8}" y="{y + 15}" text-anchor="end" class="lab">{esc(lab)}</text><rect x="{L}" y="{y + 3}" width="{w:.1f}" height="16" rx="3" class="bar {k}"/>'
               f'<text x="{L + w + 6:.1f}" y="{y + 15}" class="val">{esc(fmt_s(v))}</text>')
svg.append("</svg>")

# the second picture: one event, by engine: the script function, and the whole event (median)
ev = [(n, med(m, "events.script.median" if m != "js" else "events.whole.median"), med(m, "events.whole.median"), m) for m, n in MODES]
emx = max([x for e in ev for x in e[1:3] if x] or [1])
EH = 38 * len(ev) + 30
es = [f'<svg class="chart" viewBox="0 0 {W} {EH}" role="img" aria-label="One lever pull: the script function and the whole event, by engine (median)">']
for i, (n, a, b, k) in enumerate(ev):
    y = 10 + i * 38
    EL = 70
    wa = 0 if not a else max(2, (W - EL - 230) * a / emx); wb = 0 if not b else max(2, (W - EL - 230) * b / emx)
    fa = "–" if a is None else f"{a:.1f}"; fb = "–" if b is None else f"{b:.1f}"
    es.append(f'<text x="{EL - 8}" y="{y + 16}" text-anchor="end" class="lab">{esc(n)}</text>'
              f'<rect x="{EL}" y="{y + 2}" width="{wb:.1f}" height="11" rx="2" class="bar {k}" opacity="0.4"/>'
              f'<rect x="{EL}" y="{y + 15}" width="{wa:.1f}" height="11" rx="2" class="bar {k}"/>'
              f'<text x="{EL + max(wa, wb) + 8:.1f}" y="{y + 12}" class="val">event {fb} ms</text>'
              f'<text x="{EL + max(wa, wb) + 8:.1f}" y="{y + 26}" class="val">{"the game\'s own" if k == "js" else "script " + fa + " ms"}</text>')
es.append("</svg>")
EVENTS_SVG = "".join(es)
# ---- as the code grows: time against the program's lines, for each measure (a line per measure, a dot per size) ----
def scale_svg():
    if not SCALE: return "<p class=note>(the run's data is not in yet)</p>"
    series = [("Hazel: an edit, until ready", "hazel", lambda r: (r.get("edit") or {}).get("median"), "#7c3aed", ""),
              ("Fumola: an edit, until ready", "fumola", lambda r: (r.get("edit") or {}).get("median"), "#0e7490", ""),
              ("Hazel: the whole program analyzed (the tiles' work)", "hazel", lambda r: (statistics.median(r["analyze"]) if r.get("analyze") else None), "#a78bfa", "6 4"),
              ("Hazel: the script function, one event", "hazel", lambda r: (r.get("script") or {}).get("median"), "#7c3aed", "2 3"),
              ("Fumola: the script function, one event", "fumola", lambda r: (r.get("script") or {}).get("median"), "#0e7490", "2 3")]
    pts = [(lab, col, dash, [(r["lines"], f(r)) for r in SCALE if r.get("eng") == eng and isinstance(f(r), (int, float))]) for lab, eng, f, col, dash in series]
    xs = [x for _, _, _, ps in pts for x, _ in ps]; ys = [y for _, _, _, ps in pts for _, y in ps]
    if not xs: return ""
    import math
    W2, H2, l, b, t, rgt = 680, 340, 60, 40, 14, 20
    x0, x1 = 0, max(xs) * 1.05
    y1 = max(ys) * 1.1
    X = lambda x: l + (W2 - l - rgt) * (x - x0) / (x1 - x0)
    Y = lambda y: H2 - b - (H2 - b - t) * y / y1
    g = [f'<svg class="chart" viewBox="0 0 {W2} {H2 + 22 * len(pts)}" role="img" aria-label="Time against the program\'s size, for an edit until ready, Hazel\'s analysis, and one event">']
    for i in range(6):
        yv = y1 * i / 5; g.append(f'<line x1="{l}" x2="{W2 - rgt}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="currentColor" opacity="0.12"/><text x="{l - 6}" y="{Y(yv) + 4:.1f}" text-anchor="end" class="val">{yv:.0f}</text>')
    for xv in sorted(set(xs)):
        g.append(f'<text x="{X(xv):.1f}" y="{H2 - b + 16}" text-anchor="middle" class="val">{xv}</text>')
    g.append(f'<text x="{(l + W2 - rgt) / 2}" y="{H2 - 4}" text-anchor="middle" class="lab">the program\'s lines (Common at 1, 2, 4, 8, 16 times its size)</text><text x="12" y="{t + 4}" class="lab">ms</text>')
    for i, (lab, col, dash, ps) in enumerate(pts):
        ps = sorted(ps)
        if ps:
            g.append(f'<polyline fill="none" stroke="{col}" stroke-width="2" stroke-dasharray="{dash}" points="{" ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in ps)}"/>')
            g += [f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3" fill="{col}"/>' for x, y in ps]
        ly = H2 + 14 + 22 * i
        g.append(f'<line x1="{l}" x2="{l + 30}" y1="{ly - 4}" y2="{ly - 4}" stroke="{col}" stroke-width="2" stroke-dasharray="{dash}"/><text x="{l + 38}" y="{ly}" class="lab">{esc(lab)}</text>')
    g.append("</svg>")
    return "".join(g)
def scale_table():
    if not SCALE: return ""
    def row(r):
        if r.get("error"):
            return f"<tr><td>{esc(r['eng'])}</td><td class=n>{r['k']}×</td><td class=n>{r['lines']}</td><td colspan=4><b>{esc(r['error'])}</b>: <code>{esc(r.get('why', ''))}</code></td></tr>"
        return None
    rows = "".join(row(r) or (f"<tr><td>{esc(r['eng'])}</td><td class=n>{r['k']}×</td><td class=n>{r['lines']}</td><td class=n>{r.get('first', '–')} ms</td>"
                   f"<td class=n>{(r.get('edit') or {}).get('median', '–')} ms <span class=rng>({(r.get('edit') or {}).get('min', '')}–{(r.get('edit') or {}).get('max', '')})</span></td>"
                   f"<td class=n>{(str(round(statistics.median(r['analyze']))) + ' ms') if r.get('analyze') else '–'}</td><td class=n>{(r.get('script') or {}).get('median', '–')} ms</td></tr>") for r in SCALE)
    return f"<div class=scroll><table><tr><th>engine</th><th>size</th><th>lines</th><th>first compile</th><th>an edit, until ready (median of 5)</th><th>Hazel's analysis</th><th>script function, one event</th></tr>{rows}</table></div>"
SCALE_SVG, SCALE_TABLE = scale_svg(), scale_table()
# ---- the pit room: pictures and its three scripts ----
# (Matthew, 2026-10-23: "syntax highlighting for each please") each rule's words coloured as the game's own boxes colour them
# (scriptTokens, 25-scripting.js; the same classes and colours): keywords, constructors, strings, numbers, comments, operators
KEYWORDS = {
    "js": "function const let var return if else for of in new true false null undefined typeof switch case break default while do".split(),
    "hazel": "let in fun if then else case end type module true false".split(),
    "fumola": "func let var public private module object type switch case if else return true false null do while for in import actor".split(),
}
import re
def highlight(text, lang):
    kw = set(KEYWORDS.get(lang, []))
    com = r"#[^#\n]*#?" if lang == "hazel" else r"//[^\n]*|/\*[\s\S]*?\*/"
    tok = re.compile("(?P<c>" + com + r")|(?P<s>\"(?:[^\"\\\n]|\\.)*\"|'(?:[^'\\\n]|\\.)*')|(?P<n>\b\d+(?:\.\d+)?\b)|(?P<w>#?[A-Za-z_]\w*)|(?P<o>=>|->|::|\+\+|[|=<>!+\-*/%:&^~?]+)|(?P<x>[\s\S])")
    out = []
    for m in tok.finditer(text or ""):
        k, w = m.lastgroup, m.group()
        if k == "w":
            k = "k" if w in kw else "C" if re.match(r"#?[A-Z]", w) or (lang == "fumola" and w.startswith("#")) else ""
        elif k == "x":
            k = ""
        out.append(f'<span class="tk-{k}">{esc(w)}</span>' if k else esc(w))
    return "".join(out)
# (Matthew, 2026-10-23: "what can we say about our CI tests for 3-way functional correctness in this doc? please create a new
# subsection") the game's two node checks, run on every push, their groups and counts from data/correct.json (a run on the laptop
# of the commit CI ran: no browser, node only)
def correct_html():
    C = CORRECT
    if not C: return ""
    num = lambda v: "" if v is None else f"{v:,}"
    # (Matthew, 2026-10-24: "I don't understand the final table of numbers yet") each row's cases, and the comparisons they make: a
    # Hazel case is one call; a Fumola case one call in each of the page's two Fumola modes, but Common's helpers one call; then the
    # checks that are not calls, and the totals, so the rows add up to the numbers in the text
    rows = "".join(f"<tr><td>{esc(g)}</td><td class=n>{num(h) or '&mdash;'}</td><td class=n>{num(f)}</td><td class=n>{'&times; ' + str(m) + ' = ' + num(f * m) if f else ''}</td><td>{esc(src)}</td></tr>" for g, h, f, m, src in C["groups"])
    rows += "".join(f"<tr><td>{esc(w)}</td><td class=n>{n}</td><td class=n></td><td></td><td>not a call: checked once</td></tr>" for w, n in C["hazel_extra"])
    rows += "".join(f"<tr><td>{esc(w)}</td><td class=n></td><td class=n></td><td class=n>{n}</td><td>not a call: checked once</td></tr>" for w, n in C["fumola_extra"])
    rows += f"<tr class=total><td><b>comparisons in all</b></td><td class=n><b>{C['hazel_total']:,}</b></td><td></td><td class=n><b>{C['fumola_total']:,}</b></td><td></td></tr>"
    return f'''<h2 id="correct">The same answers, three ways</h2>
<p>Matthew: <q>what can we say about our CI tests for 3-way functional correctness in this doc?</q> Speed means nothing if the
rules disagree, so the game holds Hazel's and Fumola's rules to its own JS on every push. Its test workflow has a step
<i>The rules three ways, JS = Hazel = Fumola</i> (<code class="ref"><b>^ticket(</b>567<b>)</b></code>), with no browser, node
only, and two checks:</p>
<ul>
<li><b>Hazel against the JS:</b> <code>tools/hazelrules531.mjs</code> loads the Hazel library the game loads
(<a href="{esc(C["hazel_lib"])}">js-library-embed</a>, build <code>{esc(C["hazel_build"])}</code>) and the game's own
<code>25-scripting.js</code>, and builds the program as the page does. It gives every room's <code>on_event</code> every case the
game can give that room, and compares the commands that come back with what the game's JS does in the same case:
<b>{C["hazel_total"]:,} comparisons</b>.</li>
<li><b>Fumola against the same expectations:</b> <code>tools/fumola_rules_check.mjs</code> loads the game's pinned Fumola wasm
build (<code>{esc(C["fumola_build"])}</code>, the one the page loads) and the page's own <code>25-fumola.js</code>. It feeds the
handlers the cases from the same case makers, and holds the answers to the expectations Hazel is held to, so Fumola must also give
Hazel's answers. It runs in both of the page's Fumola modes (the World map held in Fumola, and passed in), adds edge cases written
out one by one, and calls Common's helpers alone: <b>{C["fumola_total"]:,} comparisons</b>.</li>
</ul>
<p><b>Reading the table.</b> A case is one situation a room can be in (its globals) and one event; a comparison is one answer
checked against the JS's answer for that case. Each Hazel case is one call, so its cases and its comparisons are the same number.
Fumola's page has two modes (the World map held in Fumola, or passed in with each event), and every Fumola case is asked in both, so
it makes two comparisons; Common's helpers are called once, outside either mode. A few checks are not calls at all (the program
compiles; the boundary refuses what it cannot write), and count one each. The last row adds each column up to the totals in the
text above.</p>
<table><thead><tr><th>what is compared</th><th>Hazel: cases (= comparisons)</th><th>Fumola: cases</th><th>Fumola: comparisons (cases &times; modes)</th><th>the JS's answer comes from</th></tr></thead><tbody>{rows}</tbody></table>
<p>Where the game's JS can run in node, the expected answer is that code itself, not a copy of it: the wiring
(<code>trapWiring</code>), the placed levers (<code>leverPull</code>), the ways out (<code>wayOutOf</code>), the world's ways
(<code>worldMeets</code>). Only the red, blue and hatch levers' outcomes are restated in the check, from their few lines of JS.
The step is allowed to fail so that the rest of the run still goes ahead, and a last step then fails the run if the rules
disagreed. A difference shows as a red run on the branch, after the pictures and the other checks have run.</p>
<p>In the browser, two more checks play the same events in real pages and compare the game's state afterwards:
<code>tools/checks/hazellogic531.mjs</code> (<code>?logic=js</code> against <code>?logic=hazel</code>) and
<code>tools/checks/fumola542.mjs</code> (against <code>?logic=fumola</code> and <code>?logic=fumola-list</code>). They cover the
trap room wired at random, the hatches, a room of placed levers, the pits under four lever settings, the dungeons' ladders, and a
world walked as a player walks it. They run with the branch's other checks on GitHub.</p>
<p><b>Where it stands:</b> at the game's <code>{esc(C["game"])}</code>, the three-way step passed on GitHub
(run <a href="{esc(C["ci_url"])}">{esc(C["ci_run"])}</a>), and both checks print <i>all ok</i> when run in node on the laptop at
the same commit (their output beside this report: <a href="data/rules-hazel.txt">Hazel</a>, <a href="data/rules-fumola.txt">Fumola</a>).
Earlier runs on the branch were cancelled by the pushes that followed them, so this is the first one to reach that step since the
outline work.</p>
<p><b>What it does not cover:</b></p>
<ul>
<li>It checks the rules as the game ships them, not a box someone has edited. An edit is checked only by the game running it.</li>
<li>Fumola's check has fewer ways-out cases than Hazel's (3,978 against 26,478), on purpose. {esc(C["wayout_reason"])}</li>
<li>Its times are node's, kept only to show the order of things; the speeds in this report are the browser runs above.</li>
<li>It does not reach the sizes where Hazel overflows its stack (<a href="#scale">As the code grows</a>).</li>
</ul>
<p>The same cases are the seed for unit tests in Hazel's library itself (<a href="https://github.com/hazelgrove/hazel/pull/2711">hazelgrove/hazel#2711</a>,
<code class="ref"><b>^ticket(</b>591<b>)</b></code>), so that the library keeps giving these answers, not just this game.</p>'''
def code_box(title, text, cls):
    return f'<div class="code3 {cls}"><div class="code3-h">{title}</div><pre>{highlight(text, cls)}</pre></div>'
ROOM = ""
if TRAP:
    pics = "".join(f'<figure><img src="img/{f}" alt="{esc(a)}" loading="lazy"><figcaption>{esc(a)}</figcaption></figure>' for f, a in
                   [("trap-game.jpg", "The trap room in the game: its two red levers, the pits they open, the boulders' blue levers."),
                    ("trap-tiles.jpg", "Its rule at max size, in Hazel's tiles, with the outline of every box at the left."),
                    ("common-tiles.jpg", "📚 Common at max size, in its tiles: the definitions every room calls, each function's type at the left as Hazel infers it, then the program's types with their kinds and cases.")]
                   if os.path.exists(os.path.join(R, "img", f)))
    ROOM = (f'<div class="pics">{pics}</div>'
            '<p>Its rule, three ways: the game\'s own JS (the functions the game runs, shown read-only), the Hazel rule and the Fumola rule, each from the run\'s page, as the game ships them. The Hazel and Fumola rules call Common\'s helpers (<code>Common.wire</code>, <code>Common.pits_open</code>, <code>Common.pit_moves</code>), and give back commands (<code>Flip</code>, <code>SetPit</code>, <code>LiftBoulder</code>, <code>DropBoulder</code>), which the game then runs, as its JS does directly.</p>'
            f'<div class="code3s">{code_box("JS (the game&#39;s own)", TRAP.get("js"), "js")}{code_box("Hazel", TRAP.get("hazel"), "hazel")}{code_box("Fumola", TRAP.get("fumola"), "fumola")}</div>')
CORRECT_HTML = correct_html()
answers = "".join(f"<li>{a}</li>" for a in FIND.get("answers", []))
notes = "".join(f"<li>{a}</li>" for a in FIND.get("notes", []))
nxt = "".join(f"<li>{a}</li>" for a in FIND.get("next", []))
PAGE = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scripting, Three Ways, Timed</title>
<meta name="description" content="Messed Up Dress Up's 📜 Scripting tab, timed with JS, Fumola and Hazel as every room's default: the tab opened, each engine ready, Hazel's tiles ready box by box, then each script scrolled into view and visited at max size, with the game's frame times throughout; three rounds each, on GitHub's computers.">
<style>{STYLE}
td.n {{ text-align: right; white-space: nowrap; }} .rng {{ color: var(--muted); font-size: 0.85em; }}
svg.chart {{ width: 100%; max-width: 760px; height: auto; }} svg.chart .lab, svg.chart .val {{ font: 12px system-ui, sans-serif; fill: var(--ink, currentColor); }}
.pics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }} .pics img {{ width: 100%; border-radius: 8px; border: 1px solid var(--line); }} .pics figcaption {{ font-size: 0.85em; color: var(--muted); }}
.code3s {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 10px; }} .code3 pre {{ font-size: 0.78em; max-height: 34em; overflow: auto; margin: 0; padding: 8px; border-radius: 6px; background: var(--paper); white-space: pre-wrap; }}
.tk-k {{ color: #7c3aed; font-weight: 600; }} .tk-C {{ color: #0e7490; }} .tk-s {{ color: #b45309; }} .tk-n {{ color: #15803d; }} .tk-c {{ color: #6b7280; font-style: italic; }} .tk-o {{ color: #be185d; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) .tk-k {{ color: #c4b5fd; }} :root:not([data-theme="light"]) .tk-C {{ color: #67e8f9; }} :root:not([data-theme="light"]) .tk-s {{ color: #fcd34d; }} :root:not([data-theme="light"]) .tk-n {{ color: #86efac; }} :root:not([data-theme="light"]) .tk-c {{ color: #9ca3af; }} :root:not([data-theme="light"]) .tk-o {{ color: #f9a8d4; }} }}
:root[data-theme="dark"] .tk-k {{ color: #c4b5fd; }} :root[data-theme="dark"] .tk-C {{ color: #67e8f9; }} :root[data-theme="dark"] .tk-s {{ color: #fcd34d; }} :root[data-theme="dark"] .tk-n {{ color: #86efac; }} :root[data-theme="dark"] .tk-c {{ color: #9ca3af; }} :root[data-theme="dark"] .tk-o {{ color: #f9a8d4; }}
.code3-h {{ font-weight: 700; margin: 4px 0; }} tr.total td {{ border-top: 2px solid var(--line); }} .code3.js .code3-h {{ color: #b45309; }} .code3.hazel .code3-h {{ color: #7c3aed; }} .code3.fumola .code3-h {{ color: #0e7490; }}
svg.chart .bar.js {{ fill: #b45309; }} svg.chart .bar.fumola {{ fill: #0e7490; }} svg.chart .bar.hazel {{ fill: #7c3aed; }}
</style></head>
<body><main>
<p class="series"><a href="../">Hazel reports</a> · <code class="ref"><b>^report(</b>32<b>)</b></code> · Messed Up Dress Up's scripts · 2026-10-23 · <span class="wip">work in progress</span></p>
<h1>Scripting, Three Ways, Timed</h1>
<p class="sub">Matthew: <q>please do a report about loading the game with fumola as default, scrolling to check each script as a speed run; hazel, same speed run</q>, and <q>Oh, and JS as default too.</q> (<code class="ref"><b>^ticket(</b>588<b>)</b></code>)</p>
<div class="headline"><p><b>Short answers.</b></p><ol class="ans">{answers}</ol></div>
<h2 id="try">Try it</h2>
<ul>
<li><b>Play the branch measured here:</b> <a href="https://matthewhammer.org/hazel/mudu-preview/script-boxes-566/">a preview of Messed Up Dress Up's <code>script-boxes-566</code></a> (kids-choice-games at <code>2c93e37</code>). Open the 📜 Scripting tab, choose JS, Hazel or Fumola for every room (or room by room), open ⛶ max size, and walk into the trap room to pull its levers: the rule you chose runs them. Hazel's boxes show Hazel's tiles, which take edits.</li>
<li><b>The game:</b> <a href="https://matthewhammer.org/kids-choice-games/dress-up/">Messed Up Dress Up</a>, as published (its <code>main</code>). The 📜 Scripting tab measured here is not in it yet: it is on the pull requests below.</li>
<li><b>The game's pull requests,</b> stacked, in <a href="https://github.com/matthewhammer/kids-choice-games">matthewhammer/kids-choice-games</a>: <a href="https://github.com/matthewhammer/kids-choice-games/pull/1">#1</a> (the Scripting panel, the trap room's levers through a Hazel rule), <a href="https://github.com/matthewhammer/kids-choice-games/pull/2">#2</a> (more of the rooms' rules in Hazel, against plain JS), <a href="https://github.com/matthewhammer/kids-choice-games/pull/4">#4</a> (the same rules in Fumola, wasm); the three-way boxes, the outline and the tiles in each box are on the branch <a href="https://github.com/matthewhammer/kids-choice-games/tree/script-boxes-566"><code>script-boxes-566</code></a>, on top of them.</li>
<li><b>Hazel's side:</b> <a href="https://github.com/hazelgrove/hazel/pull/2711">hazelgrove/hazel#2711</a> (Hazel as a JS library: analyze and run programs from any page) and <a href="https://github.com/hazelgrove/hazel/pull/2719">#2719</a> (Hazel in another page's frame, stacked on it); the tiles that take edits, one module each, are the branch <code>embed-editable</code>, built at <a href="https://hazel.org/build/embed-editable/">hazel.org/build/embed-editable/</a> (its <code>#embed</code> page takes a program only from a page that frames it).</li>
<li><b>Fumola:</b> <a href="https://fumola.org">fumola.org</a>; the game pins a build of <a href="https://github.com/Adapton/fumola">Adapton/fumola</a> with the semantics fixes of <a href="https://github.com/Adapton/fumola/pull/151">Adapton/fumola#151</a>.</li>
</ul>
<h2 id="ready">From the tab opened to ready</h2>
<p>The median of {RUN.get('rounds', 3)} rounds, each from a fresh page. JS has nothing to load: its boxes show the game's own code at once. Fumola loads its wasm build and defines the rules; Hazel loads its JS library and compiles the program, and then, with the boxes in tiles (the default), makes one frame of Hazel's own app per box, one at a time.</p>
{''.join(svg)}
<h2 id="table">Every measure</h2>
<p>Each a median over the rounds, with the rounds' range in brackets. Times from the tab opened; frame times are the game's own (the gaps between its animation frames), so a frame over 50 ms is one a player can feel.</p>
<div class="scroll"><table><tr><th>measure</th>{''.join(f'<th>{n} as default</th>' for _, n in MODES)}</tr>{table}</table></div>
<h2 id="events">The game calling into a script</h2>
<p>Matthew: <q>let's include timing for event "event handler", or Game Engine ---calls-into-script---&gt; Script Function</q>. In each round, after the tab's runs, the trap room's red levers are pulled 20 times, left and right in turn, each through the game's own entry point (<code>roomLeverPull</code>), which hands the event to the room's rule when one runs it (<code>scriptEvent</code>), and to the game's JS when not. The game times each hop itself (<code>hzCounters</code>, 25-scripting.js): the script function alone (the event in, the commands out), the commands then run by the game, the whole event; and, for JS, its own handler. The table's rows starting "events" are these, in milliseconds to the thousandth.</p>
{EVENTS_SVG}
<p class="note">Each engine: the pale bar the whole event (the game's call to the commands done), the dark bar the script function alone (the event in, the rule's answer out). JS's handler is the game's own code, so it has the whole event only. Medians of 60 pulls (three rounds of 20).</p>
<h2 id="notes">What the numbers say</h2>
<ul>{notes}</ul>
<h2 id="scale">As the code grows, and as we edit</h2>
<p>Matthew: <q>Can we project what will happen if the code gets bigger? ... what happens as we edit? Let's measure and plot response to edits that are valid logic edits (how long does the program take to complete the edit and be ready to be responsive)?</q> Common, made 1, 2, 4, 8 and 16 times its size with renamed copies of its functions, in Hazel and in Fumola. At each size, five edits, each a definition added to Common (a valid logic edit: the program changes, and stays fine), each timed from the change to the rules compiled and ready to answer the next event (the game waits 600 ms after typing stops before it starts this); Hazel's analysis of the whole program, the work its tiles redo after an edit; and one event's script function.</p>
{SCALE_SVG}
{SCALE_TABLE}
<ul>{"".join(f"<li>{a}</li>" for a in FIND.get("scale", []))}</ul>
<h2 id="room">The pit room's rule, three ways</h2>
<p>Matthew: <q>let's also show each room with an interesting script, and an example of the three scripts for that room: pit room? include screenshot in report.</q> The trap room over the castle's dungeons, whose rule has the most to it: a red lever flips, and the pits wired to it open or shut; a blue lever gives a pit its boulder or takes it away.</p>
{ROOM}
{CORRECT_HTML}
<h2 id="next">What next</h2>
<ol>{nxt}</ol>
<h2 id="method">How this was put together</h2>
<p>The check <code>tools/checks/scriptspeed588.mjs</code> (kids-choice-games), run on GitHub's computers (no test browsers run on the laptop) on a branch carrying only it: <code>diag-588</code>, the game at <code>{esc(RUN.get('game'))}</code> (the script-boxes-566 branch, with the tiles made one at a time), run <a href="{esc(RUN.get('url'))}">{esc(RUN.get('id'))}</a>, {esc(RUN.get('runner', 'an ubuntu-latest runner'))}. Hazel's tiles came from <code>hazel.org/build/embed-editable/</code> as it was then (<code>{esc(RUN.get('hazel', ''))}</code>); the levers' Hazel from <code>js-library-embed</code>.</p>
<p>Each round: a fresh page; the game's state reset; every room's default set to one engine (Hazel's boxes in tiles); the 📜 Scripting tab opened; the time until Common's box is there, until the engine is ready, and, with Hazel, until each box's tiles say ready; then each script box scrolled into view in turn, 600 ms each; then each box opened at max size from the outline, 600 ms each. The game's animation-frame gaps are recorded for each phase, and the long tasks (over 50 ms) throughout. Rounds in the order JS, Fumola, Hazel, three times. A single runner, so the noise between rounds is the range shown; the runner is not the laptop, and a phone is slower again.</p>
</main></body></html>
"""
open(os.path.join(R, "index.html"), "w").write(PAGE); print("032/index.html", len(PAGE), "rounds", len(RUNS))
