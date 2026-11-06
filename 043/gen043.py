#!/usr/bin/env python3
"""^report(43), Scripting a JavaScript App in Hazel: writes 043/index.html from body.html.

{{name}} in body.html is a figure, a table or a value made here. The numbers come from the worked example's three runs
(043/data/runs/run*.json, made by 043/example/petri.mjs); the Hazel and JS shown are cut from that file, so the report
shows exactly what ran. Then the series tools run over the page (see build.sh)."""
import html, json, math, os, re, statistics, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "042", "drivers"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from codehl import hazel_hl, js_hl, HL_CSS  # noqa: E402  (Matthew, 2026-11-04: "high contrast / dark theme Hazel for the code"; 2026-11-06: every listing highlighted)
import figs042  # noqa: E402  (its fig_js_app, the pattern, drawn for ^report(42)'s item 5)
from figs037 import svg, text, arrow  # noqa: E402

s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
RUNS = [json.load(open(os.path.join(HERE, "data", "runs", f"run{i}.json"))) for i in (1, 2, 3)]
SRC = open(os.path.join(HERE, "example", "petri.mjs")).read()
# the example's net, as petri.mjs's NET has it (places by name; arcs by place index, weight 1)
NET = {"places": ["idle1", "busy1", "idle2", "busy2", "lock"], "marking": [1, 0, 1, 0, 1]}
_a = lambda p: {"place": NET["places"].index(p), "weight": 1}
NET["transitions"] = [
    {"name": "enter1", "inputs": [_a("idle1"), _a("lock")], "outputs": [_a("busy1")]},
    {"name": "leave1", "inputs": [_a("busy1")], "outputs": [_a("idle1"), _a("lock")]},
    {"name": "enter2", "inputs": [_a("idle2"), _a("lock")], "outputs": [_a("busy2")]},
    {"name": "leave2", "inputs": [_a("busy2")], "outputs": [_a("idle2"), _a("lock")]}]
assert all(f'name: "{t["name"]}"' in SRC for t in NET["transitions"]) and '[1, 0, 1, 0, 1]' in SRC
esc = lambda s: html.escape(s, quote=False)


def between(name):
    """a template literal of petri.mjs, by its const name, as it ran"""
    m = re.search(r"const " + name + r" = `(.*?)`;", SRC, re.S)
    return m.group(1)


def js_block(start, end):
    """the lines of petri.mjs from the one starting with start up to the one starting with end (exclusive)"""
    lines = SRC.splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith(start))
    j = next(k for k, l in enumerate(lines) if k > i and l.startswith(end))
    return "\n".join(lines[i:j]).rstrip()


# --- Figure 2: the net, two processes and one lock ---

def fig_net():
    W, H = 700, 330
    o = []
    # (ids for live.js, which keeps the tokens and the transitions that can fire up to date: places and transitions numbered
    # as in petri.mjs's NET)
    PI = {p: i for i, p in enumerate(NET["places"])}
    TI = {t["name"]: i for i, t in enumerate(NET["transitions"])}
    place = lambda x, y, name, tok: (f'<circle cx="{x}" cy="{y}" r="24" fill="var(--paper)" stroke="var(--ink)" stroke-width="1.8"><title>{name}</title></circle>'
                                     + f'<circle id="live-tok-{PI[name]}" cx="{x}" cy="{y}" r="6" fill="var(--ink)"{"" if tok == 1 else " style=\"display:none\""}/>'
                                     + f'<text id="live-cnt-{PI[name]}" x="{x}" y="{y + 5}" font-size="15" text-anchor="middle" fill="var(--ink)" font-weight="700" style="display:none"></text>'
                                     + text(x, y + 42, name, 12.5, "middle", "var(--ink)", 700))
    trans = lambda x, y, name, side: (f'<rect id="live-tr-{TI[name]}" class="live-tr" x="{x - 6}" y="{y - 24}" width="12" height="48" rx="2" fill="var(--accent)"><title>transition {name}</title></rect>'
                                      + text(x + (16 if side == "r" else -16), y + 4, name, 12, "start" if side == "r" else "end", "var(--accent)", 700))

    def curve(x1, y1, cx1, cy1, cx2, cy2, x2, y2, col="var(--muted)"):
        a = math.atan2(y2 - cy2, x2 - cx2)
        hx = f"M{x2 - 9 * math.cos(a - 0.45):.1f} {y2 - 9 * math.sin(a - 0.45):.1f} L{x2:.1f} {y2:.1f} L{x2 - 9 * math.cos(a + 0.45):.1f} {y2 - 9 * math.sin(a + 0.45):.1f}"
        return (f'<path d="M{x1} {y1} C {cx1} {cy1}, {cx2} {cy2}, {x2} {y2}" fill="none" stroke="{col}" stroke-width="1.8"/>'
                f'<path d="{hx}" fill="none" stroke="{col}" stroke-width="1.8" stroke-linejoin="round"/>')
    # process 1 (left), the lock (middle), process 2 (right, mirrored)
    for (px, enter_x, leave_x, n, side_e, side_l) in ((150, 238, 62, 1, "l", "l"), (550, 462, 638, 2, "r", "r")):
        o.append(curve(px + (18 if n == 1 else -18), 66, enter_x, 80, enter_x, 100, enter_x, 124))        # idle -> enter
        o.append(curve(enter_x, 176, enter_x, 200, enter_x, 220, px + (18 if n == 1 else -18), 236))     # enter -> busy
        o.append(curve(px - (18 if n == 1 else -18), 236, leave_x, 220, leave_x, 200, leave_x, 176))     # busy -> leave
        o.append(curve(leave_x, 124, leave_x, 100, leave_x, 80, px - (18 if n == 1 else -18), 66))       # leave -> idle
        o.append(arrow(326 if n == 1 else 374, 150, enter_x + (8 if n == 1 else -8), 150))              # lock -> enter
        o.append(curve(leave_x, 176, leave_x, 320, 350, 320, 350 - (6 if n == 1 else -6), 175))           # leave -> lock
        o.append(place(px, 50, f"idle{n}", 1))
        o.append(place(px, 250, f"busy{n}", 0))
        o.append(trans(enter_x, 150, f"enter{n}", side_e))
        o.append(trans(leave_x, 150, f"leave{n}", side_l))
    o.append(place(350, 150, "lock", 1))
    return svg(W, H, "The example's Petri net: two processes, each idle or busy, and one lock; entering takes the lock and leaving gives it back. idle1, idle2 and the lock start with one token each.", o)


# --- Figure 3: what each thing costs, log scale ---

def med(f):
    return statistics.median(f(r) for r in RUNS)


COST = [("your app's own JS handler, one call", med(lambda r: r["js_call_ms"]["median"]), "var(--accent2)"),
        ("the Hazel rule, one call", med(lambda r: r["steps"]["call_ms"]["median"]), "var(--accent)"),
        ("rebuilding the program after an edit", med(lambda r: r["rebuild_ms"]["one_module_changed"]), "var(--warn)"),
        ("the first build of the program", med(lambda r: r["built"]["ms"]), "var(--warn)")]


def fmt_ms(v):
    return f"{v * 1000:.1f} µs" if v < 0.01 else f"{v:.1f} ms" if v < 20 else f"{v:,.0f} ms"


def fig_cost():
    W, H, L, R, T = 760, 196, 270, 80, 30
    lo, hi = 0.0001, 1000
    X = lambda v: L + (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (W - L - R)
    o = [text(8, 14, "Milliseconds, logarithmic scale (medians of three runs)", 11.5, "start", "var(--muted)")]
    for v, lab in ((0.001, "1 µs"), (0.01, "10 µs"), (0.1, "0.1 ms"), (1, "1 ms"), (10, "10 ms"), (100, "100 ms"), (1000, "1 s")):
        o.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{H - 24}" stroke="var(--line)"/>')
        o.append(text(X(v), H - 10, lab, 11, "middle", "var(--muted)"))
    o.append(f'<line x1="{X(16.7):.1f}" x2="{X(16.7):.1f}" y1="{T - 6}" y2="{H - 24}" stroke="var(--bad)" stroke-dasharray="4 3"/>')
    o.append(text(X(16.7) + 4, T - 8, "one frame at 60 fps", 10.5, "start", "var(--bad)"))
    for i, (lab, v, col) in enumerate(COST):
        y = T + 6 + i * 34
        o.append(text(L - 10, y + 15, lab, 12.5, "end", "var(--ink)"))
        o.append(f'<rect x="{L}" y="{y}" width="{max(2, X(v) - L):.1f}" height="20" rx="3" fill="{col}"><title>{lab}: {fmt_ms(v)}</title></rect>')
        o.append(text(X(v) + 6, y + 15, fmt_ms(v), 12.5, "start", "var(--ink)", 700))
    return svg(W, H, "Costs: " + "; ".join(f"{lab}, {fmt_ms(v)}" for lab, v, _ in COST), o)


# --- tables ---

def table_by_hand():
    o = ['<div class="scroll"><table>', "<tr><th>Event</th><th>The rule's answer, as the app logs it</th><th>Marking after (idle1, busy1, idle2, busy2, lock)</th></tr>"]
    for x in RUNS[0]["by_hand"]:
        ev = f'{x["event"]["tag"]}({x["event"]["value"]})'
        o.append(f'<tr><td><code>{ev}</code></td><td>{esc(x["said"])}</td><td class="n"><code>{x["marking"]}</code></td></tr>')
    o.append("</table></div>")
    return "\n".join(o)


def table_cost():
    o = ['<div class="scroll"><table>', "<tr><th>Run</th><th>First build</th><th>Hazel call, median (p90)</th><th>Same, tail unannotated</th>"
         "<th>JS handler call, median</th><th>Rebuild: one module changed / unchanged</th></tr>"]
    for i, r in enumerate(RUNS, 1):
        s, u = r["steps"]["call_ms"], r["unannotated_tail_call_ms"]
        o.append(f'<tr><td class="n">{i}</td><td class="n">{r["built"]["ms"]:.0f} ms</td><td class="n">{s["median"]:.2f} ms ({s["p90"]:.2f})</td>'
                 f'<td class="n">{u["median"]:.2f} ms ({u["p90"]:.2f})</td><td class="n">{r["js_call_ms"]["median"] * 1000:.1f} µs</td>'
                 f'<td class="n">{r["rebuild_ms"]["one_module_changed"]:.0f} / {r["rebuild_ms"]["unchanged"]:.0f} ms</td></tr>')
    o.append("</table></div>")
    return "\n".join(o)


fired = RUNS[0]["steps"]["fired"]
V = {"updated": subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip(),
     "call_med": f'{med(lambda r: r["steps"]["call_ms"]["median"]):.1f}',
     "call_lo": f'{min(r["steps"]["call_ms"]["median"] for r in RUNS):.1f}', "call_hi": f'{max(r["steps"]["call_ms"]["median"] for r in RUNS):.1f}',
     "js_us": f'{med(lambda r: r["js_call_ms"]["median"]) * 1000:.1f}',
     "build_lo": f'{min(r["built"]["ms"] for r in RUNS):.0f}', "build_hi": f'{max(r["built"]["ms"] for r in RUNS):.0f}',
     "rebuild_lo": f'{min(min(r["rebuild_ms"].values()) for r in RUNS):.0f}', "rebuild_hi": f'{max(max(r["rebuild_ms"].values()) for r in RUNS):.0f}',
     "fired": ", ".join(f"{k} {v}" for k, v in fired.items()), "both_busy": str(RUNS[0]["steps"]["both_busy"]),
     "err1": esc(RUNS[0]["with_error"]["errors"][0]), "err2": esc(RUNS[0]["with_error"]["errors"][1]),
     "hazeljs": RUNS[0]["hazeljs"], "node": RUNS[0]["node"],
     "PREAMBLE": hazel_hl(between("PREAMBLE")), "COMMON": hazel_hl(between("COMMON")), "RULES": hazel_hl(between("RULES")),
     "JS_PERFORM": js_hl(js_block("function perform", "// ---- 5.")), "JS_BUILD": js_hl(js_block("function build", "const handlerOf")),
     "JS_FALLBACK": js_hl(js_block("function jsHandler", "// ---- 6.") + "\nconst handlerOf = b => b.ok ? b.handler : jsHandler;")}
def live_editor(mod, intro):
    # (a listing hazel-listings.js makes into Hazel's editor; plain text until then, and for a page without JavaScript)
    return (f'<div class="live-ed" id="live-ed-{mod}"><div class="live-ed-head"><b>{mod}</b> <span class="muted">{intro}</span></div>'
            f'<pre class="code hazel hz" data-program="petri" data-module="{mod}">{hazel_hl(between(mod.upper()))}</pre></div>')


def live_data():
    tail = re.search(r'tail: "([^"]*)"', SRC).group(1)
    d = {"preamble": between("PREAMBLE"), "tail": tail,
         "modules": [{"name": "Common", "text": between("COMMON")}, {"name": "Rules", "text": between("RULES")}],
         "places": NET["places"], "transitions": NET["transitions"], "marking": NET["marking"]}
    return '<script type="application/json" id="live-data">' + json.dumps(d, ensure_ascii=False).replace("</", "<\\/") + "</script>"


FIGS = {"FIG_PATTERN": figs042.fig_js_app(), "FIG_NET": fig_net(), "FIG_COST": fig_cost(),
        "LIVE_COMMON": live_editor("Common", "helpers the rules use"), "LIVE_RULES": live_editor("Rules", "the handler, on_event"),
        "LIVE_DATA": live_data(),
        "TABLE_BY_HAND": table_by_hand(), "TABLE_COST": table_cost()}
BODY = open(os.path.join(HERE, "body.html")).read()
BODY = re.sub(r"\{\{(\w+)\}\}", lambda m: FIGS.get(m.group(1)) or V[m.group(1)], BODY)
HEAD = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scripting a JavaScript App in Hazel</title>
<meta name="description" content="How Messed Up Dress Up lets its players script the game's rooms in Hazel through hazeljs, and how another JavaScript developer can do the same: the pattern, six steps, a worked Petri net example run in Node, and what it costs today.">
<style>{CSS}
  pre.code {{ background: color-mix(in srgb, var(--line) 35%, transparent); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px;
             overflow-x: auto; font-size: 0.84em; line-height: 1.45; max-width: 100%; }}
  pre.code code {{ background: none; padding: 0; font-size: inherit; overflow-wrap: normal; white-space: pre; }}
  ol.steps > li {{ margin: 10px 0; }}
  ol.outline > li {{ margin: 4px 0; }}
  /* the game's pieces: names whole, one to a line, the code column as wide as its longest name */
  table.pieces td:first-child {{ width: 8.5em; }} table.pieces td:last-child {{ white-space: nowrap; }}
  table.pieces td:last-child code {{ overflow-wrap: normal; }}
  /* the live example (live.js) */
  /* (within the page's column: the nav beside it makes any width from the window wrong) two columns when the column is wide */
  .live {{ container-type: inline-size; }}
  .live-grid {{ display: grid; grid-template-columns: minmax(0, 1fr); gap: 18px; align-items: start; }}
  @container (min-width: 880px) {{ .live-grid {{ grid-template-columns: minmax(0, 4fr) minmax(0, 6fr); }} .live-left {{ position: sticky; top: 8px; }} }}
  .live-left, .live-right {{ min-width: 0; }}
  .live-panel {{ background: var(--paper); border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; }}
  /* ⛶ the example full screen (live.js): the browser's, or, without one, the window */
  .live:fullscreen, .live.live-max {{ background: var(--bg); color: var(--ink); padding: 16px; overflow: auto; box-sizing: border-box; }}
  .live.live-max {{ position: fixed; inset: 0; z-index: 10000; }}
  html.live-max-on, html.live-max-on body {{ overflow: hidden; }}
  html.live-max-on #cnav, html.live-max-on #cnav-grip, html.live-max-on #cnav-hide {{ display: none; }}  /* (the site's nav column, stacked over everything: hidden while the example fills the window) */
  .live:fullscreen .script-log .log-list, .live.live-max .script-log .log-list {{ max-height: 45vh; }}
  .live-controls {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0; }}
  .live-controls button, .live-toggle {{ font: inherit; font-size: 0.9em; padding: 3px 10px; border: 1px solid var(--line); border-radius: 6px;
    background: var(--bg); color: var(--ink); cursor: pointer; }}
  .live-controls button:hover, .live-toggle:hover {{ border-color: var(--accent); }}
  .live-controls button:disabled {{ opacity: 0.5; cursor: default; }}
  .live:not(.on) .live-controls, .live:not(.on) #live-log {{ display: none; }}
  .live:not(.on) .live-nojs {{ display: block; }} .live-nojs {{ display: none; }}
  #live-net .live-tr {{ cursor: pointer; }} #live-net .live-tr.off {{ fill: var(--muted); opacity: 0.45; }}
  #live-net .live-tr:focus {{ outline: none; stroke: var(--ink); stroke-width: 2; }}
  .live-marking {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.85em; color: var(--muted); }}
  .live-status {{ border-left: 4px solid var(--line); padding: 6px 10px; margin: 8px 0; border-radius: 6px; background: var(--bg); font-size: 0.92em; }}
  .live-status.ok {{ border-left-color: var(--good); }} .live-status.no {{ border-left-color: var(--warn); }}
  .live-status ul {{ margin: 4px 0 0; padding-left: 1.2em; }}
  .live-ed {{ margin: 0 0 14px; }}
  .live-ed-head {{ margin: 0 0 4px; font-size: 0.92em; }} .live-ed-head .muted, .muted {{ color: var(--muted); }}
  /* Hazel listings (hazel-listings.js): the text until Hazel's editor says ready, then the editor */
  .hazel-listing {{ position: relative; margin: 10px 0; }}
  .hazel-listing iframe {{ border: 1px solid var(--line); border-radius: 8px; background: var(--paper); }}
  .hazel-listing[data-state="loading"] pre, .hazel-listing[data-state="tiles"] pre {{ display: none; }}
  .hazel-listing pre.hazel {{ margin: 0; }}
  /* 🪵 the event log, as Messed Up Dress Up's (its style.css, ticket 592): a line an event, opened for the answer acted out */
  .script-log {{ margin-top: 10px; font-size: 0.92em; }}
  .script-log .log-head {{ display: flex; align-items: baseline; gap: 8px; margin: 4px 0; }}
  .script-log .log-count {{ color: var(--muted); font-size: 0.9em; }}
  .script-log .log-head button {{ margin-left: auto; font: inherit; font-size: 0.85em; padding: 2px 10px; border: 1px solid var(--line); border-radius: 6px; background: var(--bg); color: var(--ink); cursor: pointer; }}
  .script-log .log-list {{ display: flex; flex-direction: column; gap: 2px; max-height: 70vh; overflow: auto; }}
  .script-log .log-entry > summary {{ cursor: pointer; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 1px 0; }}
  /* (Matthew, 2026-11-06: the event log "has ellipses that never expand") an entry opened shows its whole line, wrapped */
  .script-log .log-entry[open] > summary {{ white-space: normal; overflow: visible; }}
  .script-log .log-entry[open] > summary .log-chip {{ margin: 2px 0; }}
  .script-log .log-entry > summary code {{ background: none; padding: 0; }}
  .script-log .log-n, .script-log .log-at, .script-log .log-ms, .script-log .log-diff {{ color: var(--muted); font-variant-numeric: tabular-nums; }}
  .script-log .log-eng {{ padding: 0 5px; border-radius: 4px; font-size: 0.85em; background: color-mix(in srgb, currentColor 12%, transparent); }}
  .script-log .log-hazel {{ color: var(--accent); }} .script-log .log-js {{ color: var(--warn); }} .script-log .log-mixed {{ color: var(--muted); }}
  .script-log .log-grid {{ display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: 3px 12px; align-items: baseline; margin: 4px 0 4px 14px; }}
  .script-log .log-grid > .log-effect {{ grid-column: 1 / -1; display: grid; grid-template-columns: subgrid; gap: 3px 12px; align-items: baseline; margin: 2px 0; }}
  .script-log .log-effect {{ background: color-mix(in srgb, #f59e0b 14%, transparent); border: 1px solid color-mix(in srgb, #f59e0b 45%, transparent); border-radius: 8px; padding: 4px 10px 6px; }}
  .script-log .log-k {{ color: var(--muted); font-size: 0.85em; white-space: nowrap; text-align: right; }}
  .script-log .log-v {{ min-width: 0; }}
  .script-log .log-json {{ overflow-x: auto; font-size: 0.85em; margin: 0; display: block; white-space: pre-wrap; overflow-wrap: anywhere; }}
  .script-log .log-chips {{ display: flex; flex-wrap: wrap; gap: 4px 6px; margin: 3px 0 2px; }}
  .script-log .log-chip {{ display: inline-block; padding: 3px 9px; border-radius: 12px; border: 2px solid var(--line); background: var(--paper); color: var(--ink); white-space: nowrap; font-size: 0.92em; line-height: 1.45; }}
  .script-log .log-chip:has(> .log-field) {{ padding-left: 4px; }}
  .script-log summary .log-chip {{ font-size: 0.85em; padding: 1px 7px; }} .script-log summary .log-chip:has(> .log-field) {{ padding-left: 2px; }}
  .script-log .log-field {{ display: inline-block; padding: 0 6px; line-height: 1.3; margin-right: 1px; border-radius: 8px; background: color-mix(in srgb, #14b8a6 26%, transparent); border: 1px solid color-mix(in srgb, #14b8a6 60%, transparent); }}
  .script-log .log-eq {{ margin: 0 0.35em; opacity: 0.8; }}
  .script-log .log-goto {{ font: inherit; padding: 0; border: 0; background: none; color: var(--link); text-decoration: underline; text-underline-offset: 2px; cursor: pointer; }}
  .script-log .log-quiet {{ color: var(--muted); border-style: dashed; }}
  .script-log .log-bad {{ color: var(--bad); }} .script-log .log-chip.log-bad {{ border-color: var(--bad); }}
  .script-log .log-globals {{ margin: 0 0 6px 14px; }} .script-log .log-globals > summary {{ cursor: pointer; color: var(--muted); font-size: 0.9em; }}
  .script-log .log-sides {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
  .script-log .hint {{ color: var(--muted); font-size: 0.9em; }}
""" + HL_CSS + """
</style>
</head>
"""
open(os.path.join(HERE, "index.html"), "w").write(HEAD + BODY)
print("wrote 043/index.html;", ", ".join(f"{k}={v}" for k, v in V.items() if len(v) < 40))
