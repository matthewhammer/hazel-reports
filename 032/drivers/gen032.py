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
svg.chart .bar.js {{ fill: #b45309; }} svg.chart .bar.fumola {{ fill: #0e7490; }} svg.chart .bar.hazel {{ fill: #7c3aed; }}
</style></head>
<body><main>
<p class="series"><a href="../">Hazel reports</a> · <code class="ref"><b>^report(</b>32<b>)</b></code> · Messed Up Dress Up's scripts · 2026-10-23 · <span class="wip">work in progress</span></p>
<h1>Scripting, Three Ways, Timed</h1>
<p class="sub">Matthew: <q>please do a report about loading the game with fumola as default, scrolling to check each script as a speed run; hazel, same speed run</q>, and <q>Oh, and JS as default too.</q> (<code class="ref"><b>^ticket(</b>588<b>)</b></code>)</p>
<div class="headline"><p><b>Short answers.</b></p><ol class="ans">{answers}</ol></div>
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
<h2 id="next">What next</h2>
<ol>{nxt}</ol>
<h2 id="method">How this was put together</h2>
<p>The check <code>tools/checks/scriptspeed588.mjs</code> (kids-choice-games), run on GitHub's computers (no test browsers run on the laptop) on a branch carrying only it: <code>diag-588</code>, the game at <code>{esc(RUN.get('game'))}</code> (the script-boxes-566 branch, with the tiles made one at a time), run <a href="{esc(RUN.get('url'))}">{esc(RUN.get('id'))}</a>, {esc(RUN.get('runner', 'an ubuntu-latest runner'))}. Hazel's tiles came from <code>hazel.org/build/embed-editable/</code> as it was then (<code>{esc(RUN.get('hazel', ''))}</code>); the levers' Hazel from <code>js-library-embed</code>.</p>
<p>Each round: a fresh page; the game's state reset; every room's default set to one engine (Hazel's boxes in tiles); the 📜 Scripting tab opened; the time until Common's box is there, until the engine is ready, and, with Hazel, until each box's tiles say ready; then each script box scrolled into view in turn, 600 ms each; then each box opened at max size from the outline, 600 ms each. The game's animation-frame gaps are recorded for each phase, and the long tasks (over 50 ms) throughout. Rounds in the order JS, Fumola, Hazel, three times. A single runner, so the noise between rounds is the range shown; the runner is not the laptop, and a phone is slower again.</p>
</main></body></html>
"""
open(os.path.join(R, "index.html"), "w").write(PAGE); print("032/index.html", len(PAGE), "rounds", len(RUNS))
