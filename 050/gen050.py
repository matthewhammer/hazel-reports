#!/usr/bin/env python3
"""^report(50): toward a 60 fps floor for small edits, reports 045 to 049 together. Writes 050/index.html from body.html,
the earlier reports' data (046's Witch runs, 049's Firefox runs) and the drag run in data/runs/, with the series' styles
(035's). Matthew, 2026-11-08: "a report about the last 6 or so reports, all about jit, and performance. With plots that
summarize. With graphics of what we are drawing (the witch?) With next steps."; "it's important for screenshots of hazel
actually running"; "and to encourage the reader to try it"; "Report now, honestly"."""
import html, json, math, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
EXTRA = """
  ol.outline > li { margin: 4px 0; } .muted { color: var(--muted); }
  table.vals { display: block; overflow-x: auto; max-width: 100%; border-collapse: collapse; margin: 0.6em 0 1em; font-size: 0.88em; }
  table.vals th, table.vals td { padding: 4px 8px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
  table.vals td.n { text-align: right; font-variant-numeric: tabular-nums; } table.vals th { font-weight: 600; }
  figure.f { margin: 1.2em 0; } figure.f svg { max-width: 100%; }
  figcaption { color: var(--muted); font-size: 0.9em; margin-top: 6px; max-width: 80ch; }
  .shots { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin: 1em 0; }
  .shots figure { margin: 0; } .shots img { width: 100%; height: auto; border: 1px solid var(--line); border-radius: 4px; background: #fff; }
  .witch { display: grid; grid-template-columns: minmax(180px, 260px) 1fr; gap: 16px; align-items: start; margin: 1em 0; }
  @media (max-width: 640px) { .witch { grid-template-columns: 1fr; } }
  .witch img { width: 100%; height: auto; border: 1px solid var(--line); border-radius: 4px; background: #fafafa; }
  .try { border: 2px solid var(--accent); border-radius: 8px; padding: 10px 14px; margin: 1em 0; }
  .try a { font-weight: 600; }
"""
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
GOAL = 1000 / 60

# --- the Witch's step, report by report (046's runs, as 048 reads them; 049's runs) ---
sys.path.insert(0, os.path.join(ROOT, "046"))
_cwd = os.getcwd()
os.chdir(os.path.join(ROOT, "046"))
import witch046 as W46  # noqa: E402
os.chdir(_cwd)


def run49(run):
    d = json.load(open(os.path.join(ROOT, "049", "data", "runs", run, "jit.json")))
    w = next(s for s in d["slides"] if s.get("slide") == "Witch")
    on = []
    for e in w["edits"]["on"]:
        done = [t for t, st in e["dynamics"] if st == "ok"][-1]
        runs = sorted([m for m in e["marks"] if m["what"] == "hazel-jit: the run" and m["at"] >= 0], key=lambda m: m["at"])
        comp = [m["ms"] for m in e["marks"] if m["what"] == "hazel-jit: the run compiled" and m["at"] >= 0]
        on.append({"pic": e["picture_changed_ms"], "early": e["picture_changed_ms"] < done, "runs": [m["ms"] for m in runs], "recompile": comp})
    off = [e["picture_changed_ms"] for e in w["edits"]["off"]]
    return on, off


R4_ON, R4_OFF = run49("42551267058")
R5_ON, R5_OFF = run49("42554043524")
ROAD = [
    ("before the cuts", [r["pic"] for r in W46.TR], W46.FA["run"], "046"),
    ("a module kept out of a probe, the trace cleared", [r["pic"] for r in W46.TC], W46.FC["run"], "046"),
    ("the worker's answers unshared", [r["pic"] for r in W46.TN], W46.FN["run"], "046"),
    ("the run compiled in the page: steps away", [x["pic"] for x in R4_ON if x["early"]], "42551267058", "049"),
    ("and the steps back, fixed", [x["pic"] for x in R5_ON], "42554043524", "049"),
]

# --- the drag (this report's own run) ---
DRAG_RUN = "42556616487"
DRAG = {}
_dp = os.path.join(HERE, "data", "runs", DRAG_RUN, "jit.json")
if os.path.exists(_dp):
    _d = json.load(open(_dp))
    _w = next(s for s in _d["slides"] if s.get("slide") == "Witch")
    for mode in ("on", "off"):
        rows = [r for r in (_w.get("drags") or {}).get(mode, []) if r.get("frames")]
        if rows:
            DRAG[mode] = rows[0]
    DRAG_PROBLEMS = len(_d["problems"])
    DRAG_STEPS = {m: [e["picture_changed_ms"] for e in _w["edits"][m]] for m in ("on", "off")}

rng = lambda xs, f="{:.0f}": (f.format(min(xs)) if f.format(min(xs)) == f.format(max(xs)) else f"{f.format(min(xs))} to {f.format(max(xs))}")
srng = lambda xs: rng([x / 1000 for x in xs], "{:.2f}")


def log_axis(out, xof, y0, y1, ticks, unit):
    for v, label in ticks:
        x = xof(v)
        out.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y1}" stroke="var(--line)" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{y1 + 14}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{label}</text>')


def svg_fig(W, h, out, alt, caption):
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{html.escape(alt)}" '
            f'style="width:100%;height:auto;display:block">' + "".join(out) + f"</svg><figcaption>{caption}</figcaption></figure></div>")


def fig_road():
    W, left, right = 940, 330, 20
    lo, hi = math.log10(10), math.log10(10000)
    xof = lambda ms: left + (math.log10(ms) - lo) / (hi - lo) * (W - left - right)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">One step of a slider on the Witch slide, '
           'from the step to the picture showing it, in Firefox: each change so far (a log scale)</text>']
    y = 40
    for label, xs, run, rep in ROAD:
        a, b = min(xs), max(xs)
        col = "#9ca3af" if rep == "046" else "#2563eb"
        out.append(f'<text x="{left - 10}" y="{y + 14}" font-size="11.5" text-anchor="end" fill="var(--ink)">{html.escape(label)} ({rep})</text>')
        out.append(f'<rect x="{xof(a):.1f}" y="{y + 3}" width="{max(4, xof(b) - xof(a)):.1f}" height="14" rx="2" fill="{col}">'
                   f'<title>{html.escape(label)}: {a:g} to {b:g} ms, run {run}</title></rect>')
        txt = f"{a / 1000:.2f} to {b / 1000:.2f} s, {a / GOAL:.0f} to {b / GOAL:.0f} frames"
        if xof(b) + 8 + 5.6 * len(txt) > W - 4:
            out.append(f'<text x="{xof(a) - 8:.1f}" y="{y + 14}" font-size="11" text-anchor="end" fill="var(--ink)">{txt}</text>')
        else:
            out.append(f'<text x="{xof(b) + 8:.1f}" y="{y + 14}" font-size="11" fill="var(--ink)">{txt}</text>')
        y += 28
    gx = xof(GOAL)
    out.append(f'<line x1="{gx:.1f}" y1="32" x2="{gx:.1f}" y2="{y}" stroke="#15803d" stroke-width="2.5"/>')
    out.append(f'<text x="{gx + 5:.1f}" y="{y + 28}" font-size="11" fill="#15803d" font-weight="700">16.7 ms: one 60 fps frame</text>')
    log_axis(out, xof, 32, y, [(10, "10 ms"), (100, "0.1 s"), (1000, "1 s"), (10000, "10 s")], "")
    return svg_fig(W, y + 40, out, "; ".join(f"{l}: {min(x):g} to {max(x):g} ms" for l, x, _, _ in ROAD),
                   "Each bar is the same small edits, from the fastest to the slowest: the neck and arms sliders stepped and "
                   "stepped back, with compiled views (049's bars: four steps; 046's: those four both ways). Firefox on GitHub's "
                   "machines, a release build each time; runs " + ", ".join(str(r) for _, _, r, _ in ROAD) + ". Grey: the cuts of "
                   "^report(46); blue: the run compiled in the page, ^report(49).")


# (interpreter against compiled, as each report gives them: ms, as (low, high))
PAIRS = [
    ("a recursive sum of 1,000 numbers (Node)", (47.9, 47.9), (0.042, 0.042), "045#speed"),
    ("the Petri net rule, four events (Node)", (7.19, 7.19), (0.011, 0.011), "045#speed"),
    ("the Polygons view, a render with its trip (Node)", (13.7, 13.7), (0.34, 0.34), "045#speed"),
    ("the Witch's polygon editors' views (Firefox)", (26, 29), (0.29, 0.45), "046#witch-firefox"),
    ("the Witch's picture view (Firefox)", (87, 87), (3.0, 3.0), "046#witch-firefox"),
    ("the Witch's whole run (Node)", (502, 529), (4.2, 5.0), "045#run"),
]


def fig_compiled():
    W, left, right = 940, 330, 20
    lo, hi = math.log10(0.005), math.log10(2000)
    xof = lambda ms: left + (math.log10(ms) - lo) / (hi - lo) * (W - left - right)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">Hazel\'s interpreter (grey) against hazel-jit\'s '
           'JavaScript (teal), each as its report measured it (a log scale)</text>']
    y = 40
    for label, (ia, ib), (ca, cb), rep in PAIRS:
        out.append(f'<text x="{left - 10}" y="{y + 13}" font-size="11.5" text-anchor="end" fill="var(--ink)">{html.escape(label)}</text>')
        xi, xc = xof((ia * ib) ** 0.5), xof((ca * cb) ** 0.5)
        out.append(f'<line x1="{xc:.1f}" y1="{y + 9}" x2="{xi:.1f}" y2="{y + 9}" stroke="var(--line)" stroke-width="3"/>')
        for (a, b), col in (((ia, ib), "#9ca3af"), ((ca, cb), "#0d9488")):
            out.append(f'<rect x="{xof(a) - 4:.1f}" y="{y + 3}" width="{max(8, xof(b) - xof(a) + 8):.1f}" height="12" rx="6" fill="{col}">'
                       f'<title>{html.escape(label)}: {a:g} to {b:g} ms</title></rect>')
        x = round(((ia * ib) ** 0.5) / ((ca * cb) ** 0.5))
        out.append(f'<text x="{xi + 10:.1f}" y="{y + 13}" font-size="11" fill="var(--ink)">about {x:,} times ({rep.split("#")[0]})</text>')
        y += 26
    gx = xof(GOAL)
    out.append(f'<line x1="{gx:.1f}" y1="32" x2="{gx:.1f}" y2="{y}" stroke="#15803d" stroke-width="2.5"/>')
    out.append(f'<text x="{gx + 5:.1f}" y="{y + 28}" font-size="11" fill="#15803d" font-weight="700">16.7 ms</text>')
    log_axis(out, xof, 32, y, [(0.01, "10 µs"), (0.1, "0.1 ms"), (1, "1 ms"), (10, "10 ms"), (100, "0.1 s"), (1000, "1 s")], "")
    return svg_fig(W, y + 40, out, "; ".join(f"{l}: {a[0]:g} ms on the interpreter, {c[0]:g} ms compiled" for l, a, c, _ in PAIRS),
                   "Times as reports 045 and 046 give them: medians in Node 22 on the laptop (045), and renders in Firefox in the "
                   "app (046). A render's time is its view's work alone, as if the state's update were free. The ratio is of the "
                   "middles of the ranges.")


COMPILERS = [("Melange", 0.46), ("ReScript", 0.55), ("js_of_ocaml (a best case)", 0.71), ("JS written by hand", 0.90),
             ("hazel-jit", 1.59), ("Hazel's interpreter", 358)]


def fig_compilers():
    W, left, right = 940, 250, 20
    lo, hi = math.log10(0.1), math.log10(1000)
    xof = lambda us: left + (math.log10(us) - lo) / (hi - lo) * (W - left - right)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">One call of report 043\'s Petri net rule, '
           'median µs, in Node (report 046; a log scale)</text>']
    y = 36
    for label, us in COMPILERS:
        col = "#0d9488" if label == "hazel-jit" else "#9ca3af" if "interpreter" in label else "#93c5fd"
        out.append(f'<text x="{left - 10}" y="{y + 12}" font-size="11.5" text-anchor="end" fill="var(--ink)">{html.escape(label)}</text>')
        out.append(f'<rect x="{left}" y="{y + 2}" width="{xof(us) - left:.1f}" height="13" rx="2" fill="{col}"><title>{label}: {us:g} µs</title></rect>')
        out.append(f'<text x="{xof(us) + 6:.1f}" y="{y + 12}" font-size="11" fill="var(--ink)">{us:g} µs</text>')
        y += 22
    log_axis(out, xof, 30, y, [(0.1, "0.1 µs"), (1, "1 µs"), (10, "10 µs"), (100, "100 µs"), (1000, "1 ms")], "")
    return svg_fig(W, y + 30, out, "; ".join(f"{l}: {u:g} µs" for l, u in COMPILERS),
                   "Each answers the same 2,000 events and ends on the same marking (^report(46), how fast). js_of_ocaml's is a best "
                   "case: it inlined the rule into the timing loop.")


def fig_data():
    """^report(47)'s experiment 1: the Witch's picture as Hazel's terms and as data"""
    W = 940
    rows = [("its size, KB", 142.2, 48.0, None, None), ("its trip by Marshal, encoded and decoded, ms", 15.0, 4.38, 25.7, 7.28)]
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">The Witch\'s picture as Hazel\'s terms (grey) '
           'and as data (blue): report 047, experiment 1</text>']
    y = 38
    for label, t, dd, t2, d2 in rows:
        top = max(t, t2 or 0)
        sc = lambda v: v / top * (W - 330)
        out.append(f'<text x="16" y="{y + 12}" font-size="11.5" fill="var(--ink)">{label}</text>')
        for i, (a, b, col, name) in enumerate(((t, t2, "#9ca3af", "terms"), (dd, d2, "#2563eb", "data"))):
            yy = y + 18 + i * 18
            out.append(f'<rect x="300" y="{yy}" width="{sc(b or a):.1f}" height="13" rx="2" fill="{col}" opacity="{0.5 if b else 1}"/>')
            out.append(f'<rect x="300" y="{yy}" width="{sc(a):.1f}" height="13" rx="2" fill="{col}"><title>{name}: {a:g}{f" to {b:g}" if b else ""}</title></rect>')
            out.append(f'<text x="290" y="{yy + 11}" font-size="11" text-anchor="end" fill="var(--muted)">{name}</text>')
            out.append(f'<text x="{300 + sc(b or a) + 6:.1f}" y="{yy + 11}" font-size="11" fill="var(--ink)">{a:g}{f" to {b:g}" if b else ""}</text>')
        y += 62
    return svg_fig(W, y, out, "the picture: 142.2 KB as terms, 48.0 KB as data; trip 15.0 to 25.7 ms as terms, 4.38 to 7.28 ms as data",
                   "As data, no ids, no sharing to find, numbers packed (^report(47)); the lighter bar is the slowest of the readings.")


def fig_drag():
    """every frame of a 3 s drag, both ways: one tick a frame on a log scale, against one 60 fps frame"""
    if not DRAG:
        return "<p class=\"note\">The drag's run is not in yet.</p>"
    W, left, right = 940, 250, 20
    lo, hi = math.log10(5), math.log10(3000)
    xof = lambda ms: left + (math.log10(max(ms, 5)) - lo) / (hi - lo) * (W - left - right)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">Every frame of a 3-second drag of the Witch\'s '
           'neck slider, in Firefox: one tick a frame (a log scale)</text>']
    y = 40
    for mode, name in (("on", "views and run compiled"), ("off", "nothing compiled")):
        if mode not in DRAG:
            continue
        r = DRAG[mode]
        st = r["stats"]
        out.append(f'<text x="{left - 10}" y="{y + 16}" font-size="11.5" text-anchor="end" fill="var(--ink)">{name}</text>')
        for f in r["frames"]:
            x = xof(f)
            col = "#15803d" if f <= GOAL * 1.05 else "#d97706" if f <= 2 * GOAL else "#dc2626"
            out.append(f'<line x1="{x:.1f}" y1="{y + 2}" x2="{x:.1f}" y2="{y + 22}" stroke="{col}" stroke-width="1.5" opacity="0.7"/>')
        out.append(f'<text x="{left}" y="{y + 38}" font-size="11" fill="var(--ink)">{st["frames"]} frames in {r["ms"] / 1000:.1f} s: '
                   f'{st["fps"]:g} fps; median {st["median_ms"]:g} ms, 90th percentile {st["p90_ms"]:g} ms, longest {st["max_ms"]:g} ms; '
                   f'{st["within_16_7"]} of {st["frames"]} within a 60 fps frame</text>')
        y += 56
    gx = xof(GOAL)
    out.append(f'<line x1="{gx:.1f}" y1="32" x2="{gx:.1f}" y2="{y}" stroke="#15803d" stroke-width="2"/>')
    log_axis(out, xof, 32, y, [(10, "10 ms"), (16.7, "16.7"), (100, "100 ms"), (1000, "1 s")], "")
    return svg_fig(W, y + 30, out, "; ".join(f"{m}: {DRAG[m]['stats']['fps']} fps" for m in DRAG),
                   f"One `input` event a frame as the slider sweeps, then one `change` at the end, as a browser delivers a drag; "
                   f"each frame timed by requestAnimationFrame, as the HUD times it. Firefox on GitHub's machines, a release "
                   f"build of <code>trial/694-view-jit</code> at bb88edfd12, run {DRAG_RUN}. One drag each way.")


# (the drag fast path, 11-08 late: each cut's run, the same drag)
CUTS = [("before (this report's run)", "42556616487", "bb88edfd12"),
        ("cut A: a drag's inputs, no editor action", "42560502616", "9fca635226"),
        ("cut B: only the livelits that changed drawn", "42562102280", "38d4e4d0f8")]
CUT_DRAGS = []
for _label, _run, _commit in CUTS:
    _p = os.path.join(HERE, "data", "runs", _run, "jit.json")
    if not os.path.exists(_p):
        continue
    _w = next(s for s in json.load(open(_p))["slides"] if s.get("slide") == "Witch")
    _dr = {m: next((r for r in (_w.get("drags") or {}).get(m, []) if r.get("frames")), None) for m in ("on", "off")}
    CUT_DRAGS.append((_label, _run, _commit, _dr))


def fig_cuts():
    W, left, right = 940, 330, 20
    top = 60
    xof = lambda fps: left + fps / top * (W - left - right)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">A 3-second drag of the Witch\'s neck slider, '
           'frames a second, cut by cut: compiled (teal) and nothing compiled (grey)</text>']
    y = 38
    for label, run, commit, dr in CUT_DRAGS:
        out.append(f'<text x="{left - 10}" y="{y + 22}" font-size="11.5" text-anchor="end" fill="var(--ink)">{html.escape(label)}</text>')
        for i, (m, col) in enumerate((("on", "#0d9488"), ("off", "#9ca3af"))):
            r = dr.get(m)
            if not r:
                continue
            f = r["stats"]["fps"]
            yy = y + 4 + i * 18
            out.append(f'<rect x="{left}" y="{yy}" width="{xof(f) - left:.1f}" height="14" rx="2" fill="{col}">'
                       f'<title>{html.escape(label)}: {f:g} fps, median frame {r["stats"]["median_ms"]:g} ms (run {run}, {commit})</title></rect>')
            out.append(f'<text x="{xof(f) + 6:.1f}" y="{yy + 11}" font-size="11" fill="var(--ink)">{f:g} fps, median frame {r["stats"]["median_ms"]:g} ms</text>')
        y += 48
    gx = xof(60)
    out.append(f'<line x1="{gx:.1f}" y1="32" x2="{gx:.1f}" y2="{y}" stroke="#15803d" stroke-width="2.5"/>')
    out.append(f'<text x="{gx - 4:.1f}" y="{y + 14}" font-size="11" text-anchor="end" fill="#15803d" font-weight="700">60 fps</text>')
    for v in (0, 15, 30, 45):
        x = xof(v)
        out.append(f'<line x1="{x:.1f}" y1="32" x2="{x:.1f}" y2="{y}" stroke="var(--line)" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{y + 14}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{v}</text>')
    return svg_fig(W, y + 24, out, "; ".join(f"{l}: {d['on']['stats']['fps'] if d.get('on') else '-'} fps compiled" for l, _, _, d in CUT_DRAGS),
                   "The same drag each time (one input event a frame, a change at the end), Firefox on GitHub's machines, one "
                   "drag each way per run: " + ", ".join(f"{c} (run {r})" for _, r, c, _ in CUT_DRAGS) + ".")


def fig_frame():
    """after cut B, a compiled drag's median frame, from the page's own timeline over the drag, per frame"""
    if not CUT_DRAGS or not CUT_DRAGS[-1][3].get("on"):
        return ""
    r = CUT_DRAGS[-1][3]["on"]
    n = r["stats"]["frames"]
    marks = r.get("marks") or {}
    per = lambda k: marks.get(k, {"ms": 0})["ms"] / n
    parts = [("the page's view", per("view"), "#2563eb"), ("the slide's run, compiled", per("hazel-jit: the run"), "#0d9488"),
             ("after display", per("after display"), "#93c5fd"), ("update", per("update"), "#bfdbfe")]
    med = r["stats"]["median_ms"]
    rest = max(0.0, med - sum(v for _, v, _ in parts))
    parts.append(("the rest: the browser's diff, layout and paint (not timed)", rest, "#d1d5db"))
    W, left, right = 940, 16, 20
    sc = (W - left - right) / max(med, GOAL) * 0.95
    out = [f'<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">After cut B, a compiled drag\'s median frame, {med:g} ms: '
           'where it goes (the page\'s own timeline, per frame)</text>']
    x = left
    for name, v, col in parts:
        w = v * sc
        out.append(f'<rect x="{x:.1f}" y="34" width="{max(1, w):.1f}" height="26" fill="{col}" stroke="var(--paper, #fff)" stroke-width="1"><title>{html.escape(name)}: {v:.1f} ms</title></rect>')
        x += w
    y = 82
    for name, v, col in parts:
        out.append(f'<rect x="{left}" y="{y - 10}" width="12" height="12" fill="{col}"/>')
        out.append(f'<text x="{left + 16}" y="{y}" font-size="11" fill="var(--ink)">{html.escape(name)}: {v:.1f} ms</text>')
        y += 18
    gx = left + GOAL * sc
    out.append(f'<line x1="{gx:.1f}" y1="28" x2="{gx:.1f}" y2="66" stroke="#15803d" stroke-width="2.5"/>')
    out.append(f'<text x="{gx + 4:.1f}" y="30" font-size="11" fill="#15803d" font-weight="700">16.7 ms</text>')
    return svg_fig(W, y + 4, out, "; ".join(f"{nm}: {v:.1f} ms" for nm, v, _ in parts),
                   f"The page's timeline (Util.BenchMarks) summed over the drag and divided by its {n} frames; the rest of the "
                   f"median frame is the browser's own work after the view, which the timeline does not time (run {CUT_DRAGS[-1][1]}).")


def kept(nnn, name):
    return open(os.path.join(ROOT, nnn, "figs", name + ".html")).read().strip()


def kept_fig(nnn, name, caption):
    return (f'<div class="figrow"><figure class="f wide">{kept(nnn, name)}<figcaption>{caption}</figcaption></figure></div>')


REPORTS = [
    ("045", "hazel-jit: Livelit Views Compiled to JavaScript",
     "A livelit's view compiled to JS runs 40 to 1,150 times faster than on the interpreter; in Firefox, compiled views draw what the interpreter draws; the Witch's whole run, compiled, 4.2 to 5.0 ms in Node."),
    ("046", "BuckleScript, ReScript and Melange, beside hazel-jit",
     "hazel-jit's code is about 2.9 times ReScript's and 1.8 times hand-written JS on the Petri rule; on the Witch's picture all five are within 15%; a small edit took 5.3 to 8.8 s, and two cuts brought it to 1.3 to 1.7 s."),
    ("047", "First-Order Data in a Form of Its Own",
     "As data, the Witch's picture is 3 times smaller and 2.5 to 4.3 times quicker to send; building values as data saves the evaluator a couple of percent at most, so the run itself has to be compiled."),
    ("048", "Why Hazel Is Slow: A Thousand Cuts",
     "196 measured costs from 33 reports, from four design choices applied everywhere; remove the largest and the next is there."),
    ("049", "The Witch’s Run, Compiled, in the Page",
     "The slide's whole run, compiled and run in the page at a slider's step: 8 to 21 ms; the picture at the page's first redraw, 286 to 386 ms, against 1.35 to 1.74 s."),
]


def reports_table():
    rows = "".join(f'<tr><td><a href="../{n}/">report {n}</a></td><td>{html.escape(t)}</td><td>{html.escape(a)}</td></tr>' for n, t, a in REPORTS)
    return '<table class="vals"><tr><th>report</th><th>title</th><th>its answer</th></tr>' + rows + "</table>"


NUMS = {
    "r5_pic": rng([x["pic"] for x in R5_ON]), "r5_off": srng(R5_OFF), "r5_first": rng([x["runs"][0] for x in R5_ON]),
    "r5_second": rng([x["runs"][1] for x in R5_ON if len(x["runs"]) > 1]),
    "r0": srng(ROAD[0][1]), "r2": srng(ROAD[2][1]), "drag_run": DRAG_RUN,
    "r5_recompile": rng([v for x in R5_ON for v in x["recompile"]]),
    "r5_frames": f"{min(x['pic'] for x in R5_ON) / GOAL:.0f} to {max(x['pic'] for x in R5_ON) / GOAL:.0f}",
    "r0_x": f"{min(ROAD[0][1]) / max(x['pic'] for x in R5_ON):.0f} to {max(ROAD[0][1]) / min(x['pic'] for x in R5_ON):.0f}",
}
for mode in ("on", "off"):
    if mode in DRAG:
        st = DRAG[mode]["stats"]
        for k in ("fps", "median_ms", "p90_ms", "max_ms", "within_16_7", "frames"):
            NUMS[f"d_{mode}_{k}"] = f"{st[k]:g}"
        NUMS[f"d_{mode}_inputs"] = str(DRAG[mode]["inputs"])
        NUMS[f"d_{mode}_pct"] = f"{100 * st['within_16_7'] / st['frames']:.0f}"

for _i, (_l, _r, _c, _d) in enumerate(CUT_DRAGS):
    for _m in ("on", "off"):
        if _d.get(_m):
            NUMS[f"c{_i}_{_m}_fps"] = f"{_d[_m]['stats']['fps']:g}"
            NUMS[f"c{_i}_{_m}_med"] = f"{_d[_m]['stats']['median_ms']:g}"
if CUT_DRAGS and CUT_DRAGS[-1][3].get("on"):
    _r = CUT_DRAGS[-1][3]["on"]
    _mk = _r.get("marks") or {}
    NUMS["cb_view"] = f"{_mk.get('view', {'ms': 0})['ms'] / _r['stats']['frames']:.1f}"
    NUMS["cb_run"] = f"{_mk.get('hazel-jit: the run', {'ms': 0})['ms'] / _r['stats']['frames']:.1f}"
body = open(os.path.join(HERE, "body.html")).read().replace("{{updated}}", updated)
FIGS = {"road": fig_road(), "compiled": fig_compiled(), "compilers": fig_compilers(), "data": fig_data(), "drag": fig_drag(),
        "cuts": fig_cuts(), "frame": fig_frame()}
os.makedirs(os.path.join(HERE, "figs"), exist_ok=True)
for name, fig in FIGS.items():
    m = re.search(r"<svg.*?</svg>", fig, re.S)
    if m:
        open(os.path.join(HERE, "figs", name + ".html"), "w").write(m.group(0) + "\n")
for k, v in FIGS.items():
    body = body.replace("{{fig_" + k + "}}", v)
body = body.replace("{{fig_edit49}}", kept_fig("049", "edit", "One slider step on the Witch, compiled, on a timeline: the compiled run at the start, the page's own work to its first redraw (the slider and the picture), the program compiled again, and the worker, which still runs (^report(49), run 42554043524)."))
body = body.replace("{{fig_cuts48}}", kept_fig("048", "cuts", "Every cost the series has measured in Hazel, one rectangle each, grouped by the design choice it comes from and coloured by where it stands (^report(48)). Hover a rectangle for the cut."))
body = body.replace("{{reports_table}}", reports_table())
for k, v in NUMS.items():
    body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{[a-z_0-9]+\}\}", body)
if left:
    sys.exit(f"unfilled: {sorted(set(left))}")
TITLE = "Toward 60 fps: hazel-jit So Far"
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n"
        "<meta name=\"description\" content=\"Reports 045 to 049 together: livelit views and a slide's whole run compiled to JavaScript, the Witch slide's slider step from seconds to a third of a second, where it stands against a 60 fps floor, and what is next. Try it yourself.\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
print("wrote 050/index.html; updated", updated, NUMS)
