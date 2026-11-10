#!/usr/bin/env python3
"""^report(50): toward a 60 fps floor for small edits, reports 045 to 049 together, and the drag's own builds. Writes
050/index.html from body.html, the earlier reports' data (046's Witch runs, 049's Firefox runs) and the runs in data/runs/,
with the series' styles (035's). Matthew, 2026-11-08: "a report about the last 6 or so reports, all about jit, and
performance. With plots that summarize. With graphics of what we are drawing (the witch?) With next steps."; "it's
important for screenshots of hazel actually running"; "and to encourage the reader to try it"; "Report now, honestly".
2026-11-09, the revision: "These results [#compiled] should get pulled into the earlier part of the story. It's really
confusing to follow what version of the system each figure is plotting. Let's revise the entire thing and reorganize it
to be simpler to understand." So: eight numbered builds, one table of them, and every figure names its build."""
import html, json, math, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
EXTRA = """
  ol.outline > li { margin: 4px 0; } .muted { color: var(--muted); }
  table.vals { display: block; overflow-x: auto; max-width: 100%; border-collapse: collapse; margin: 0.6em 0 1em; font-size: 0.88em; }
  table.vals th, table.vals td { padding: 4px 8px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
  table.vals td.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; } table.vals th { font-weight: 600; }
  table.next td:nth-child(2) { min-width: 30ch; } table.next td:nth-child(3) { min-width: 24ch; } table.next td:nth-child(4) { min-width: 12ch; }
  table.builds td:first-child { min-width: 14ch; } table.builds td:nth-child(2) { min-width: 28ch; }
  table.builds td:nth-child(3), table.builds td:nth-child(4) { min-width: 14ch; font-variant-numeric: tabular-nums; }
  table.vals tr.now td { background: color-mix(in srgb, var(--accent) 8%, transparent); }
  figure.f { margin: 1.2em 0; } figure.f svg { max-width: 100%; }
  figcaption { color: var(--muted); font-size: 0.9em; margin-top: 6px; max-width: 80ch; }
  figcaption b.build, .shots b.build { color: var(--ink); }
  .shots { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin: 1em 0; }
  .shots figure { margin: 0; } .shots img { width: 100%; height: auto; border: 1px solid var(--line); border-radius: 4px; background: #fff; }
  .witch { display: grid; grid-template-columns: minmax(180px, 260px) 1fr; gap: 16px; align-items: start; margin: 1em 0; }
  @media (max-width: 640px) { .witch { grid-template-columns: 1fr; } }
  .witch img { width: 100%; height: auto; border: 1px solid var(--line); border-radius: 4px; background: #fafafa; }
  .try { border: 2px solid var(--accent); border-radius: 8px; padding: 10px 14px; margin: 1em 0; }
  .try a { font-weight: 600; }
  .notbuild { display: inline-block; font-size: 0.8em; font-weight: 600; color: var(--muted); border: 1px solid var(--line); border-radius: 999px; padding: 0 8px; margin-left: 6px; vertical-align: 2px; }
"""
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
GOAL = 1000 / 60
TEAL, GREY, SLATE, GREEN = "#0d9488", "#9ca3af", "#64748b", "#15803d"

# --- 046's Witch runs (builds 1 to 3) ---
sys.path.insert(0, os.path.join(ROOT, "046"))
_cwd = os.getcwd()
os.chdir(os.path.join(ROOT, "046"))
import witch046 as W46  # noqa: E402
os.chdir(_cwd)


def witch_of(path):
    return next(s for s in json.load(open(path))["slides"] if s.get("slide") == "Witch")


def steps_of(w, mode):
    """a run's four Witch steps one way: the picture's time, and whether it came before the worker's answer"""
    out = []
    for e in w["edits"][mode]:
        done = [t for t, st in e["dynamics"] if st == "ok"][-1]
        out.append({"pic": e["picture_changed_ms"], "early": e["picture_changed_ms"] < done})
    return out


def drag_of(w, mode):
    return next((r for r in (w.get("drags") or {}).get(mode, []) if r.get("frames")), None)


# --- the builds: one branch, each build the one before it plus one change; all measured 2026-11-08 (MST) ---
BUILDS = [
    {"n": 1, "name": "the branch as it was", "commit": "dfa3fcdffe", "run": "42486001354", "at": "06:39", "rep": "046",
     "adds": "Livelit views compiled (^report(45)). The picture waits for the worker's answer: the whole program run on the interpreter, its result sent back as 5 MB of terms."},
    {"n": 2, "name": "the answer trimmed", "commit": "20a3067c18", "run": "42490487136", "at": "07:34", "rep": "046",
     "adds": "Two changes to the worker's answer: no function-holding values in the samples' environments, and no trace (^report(46))."},
    {"n": 3, "name": "the answer unshared", "commit": "4747a4120d", "run": "42492117212", "at": "07:54", "rep": "046",
     "adds": "The worker's answers no longer shared (^report(46))."},
    {"n": 4, "name": "the run compiled", "commit": "6d71c427bf", "run": "42551267058", "at": "19:29", "rep": "049",
     "adds": "The slide's whole run compiled to JavaScript in the page, each livelit's model a parameter, and called at a livelit's event, so every livelit draws from its answers (^report(49)). A step back to a slider's starting value is still taken for an undo, and waits for the worker."},
    {"n": 5, "name": "steps back kept", "commit": "bb88edfd12", "run": "42556616487", "at": "20:28", "rep": "050",
     "adds": "A step back keeps the run's answers (a51dc778dd, ^report(49)); and the frame-rate overlay, and the timed drag in the check, which change nothing else in the app."},
    {"n": 6, "name": "change A", "commit": "9fca635226", "run": "42560502616", "at": "21:12", "rep": "050",
     "adds": "A drag's input events go to the page as a request to draw again, not to the editor as an edit of the program."},
    {"n": 7, "name": "change B", "commit": "38d4e4d0f8", "run": "42562102280", "at": "21:29", "rep": "050",
     "repeats": [("42563736665", "fa2614e1f6", "the same app with the page's view timed part by part"),
                 ("42564711121", "bdecaec5d9", "the same app with a first try at change C whose memo missed every frame")],
     "adds": "Each livelit has its own version in the views' cache, so a frame draws again only the livelits whose answers changed, not all 53."},
    {"n": 8, "name": "change C", "commit": "61f3f01a15", "run": "42566328043", "at": "22:16", "rep": "050",
     "adds": "The projectors' data and finished views kept from frame to frame while nothing they read has changed (bdecaec5d9, 61f3f01a15)."},
]
for b in BUILDS[:3]:
    b["pooled"] = True
BUILDS[0]["steps"] = [{"pic": r["pic"], "early": False} for r in W46.TR]
BUILDS[1]["steps"] = [{"pic": r["pic"], "early": False} for r in W46.TC]
BUILDS[2]["steps"] = [{"pic": r["pic"], "early": False} for r in W46.TN]
for b in BUILDS[3:]:
    p = os.path.join(ROOT, b["rep"], "data", "runs", b["run"], "jit.json")
    w = witch_of(p)
    b["steps"], b["steps_off"] = steps_of(w, "on"), steps_of(w, "off")
    b["drag"] = {m: drag_of(w, m) for m in ("on", "off")}
    b["problems"] = len(json.load(open(p))["problems"])
    b["rep_drags"] = []
    for run, commit, what in b.get("repeats", []):
        rw = witch_of(os.path.join(HERE, "data", "runs", run, "jit.json"))
        b["rep_drags"].append((run, commit, what, {m: drag_of(rw, m) for m in ("on", "off")}))
B = {b["n"]: b for b in BUILDS}
NOW = B[8]
NOW_W = witch_of(os.path.join(HERE, "data", "runs", NOW["run"], "jit.json"))

rng = lambda xs, f="{:.0f}": (f.format(min(xs)) if f.format(min(xs)) == f.format(max(xs)) else f"{f.format(min(xs))} to {f.format(max(xs))}")
srng = lambda xs: rng([x / 1000 for x in xs], "{:.2f}")


def tms(xs):
    """a range of ms, in s when it is a second or more"""
    return srng(xs) + " s" if min(xs) >= 1000 else rng(xs) + " ms" if max(xs) < 1000 else f"{min(xs):.0f} ms to {max(xs) / 1000:.2f} s"


def bl(b):
    return f"build {b['n']}"


def log_axis(out, xof, y0, y1, ticks):
    for v, label in ticks:
        x = xof(v)
        out.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y1}" stroke="var(--line)" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{y1 + 14}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{label}</text>')


def svg_fig(W, h, out, alt, caption):
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{html.escape(alt)}" '
            f'style="width:100%;height:auto;display:block">' + "".join(out) + f"</svg><figcaption>{caption}</figcaption></figure></div>")


def title(out, text):
    out.append(f'<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">{html.escape(text)}</text>')


def fig_road():
    """a slider's step, build by build: one dot a step, coloured by where the picture came from"""
    W, left, right = 940, 250, 150
    lo, hi = math.log10(10), math.log10(10000)
    xof = lambda ms: left + (math.log10(ms) - lo) / (hi - lo) * (W - left - right)
    out = []
    title(out, "A slider's step on the Witch, from the step to the picture showing it, build by build (Firefox; a log scale)")
    y = 30
    for i, (col, txt) in enumerate(((SLATE, "the picture from the worker's answer"), (TEAL, "the picture from the slide's run, compiled, in the page"))):
        x = 16 + i * 300
        out.append(f'<circle cx="{x + 5}" cy="{y + 6}" r="5" fill="{col}"/><text x="{x + 15}" y="{y + 10}" font-size="11" fill="var(--ink)">{txt}</text>')
    y = 54
    top = y
    for b in BUILDS:
        xs = [s["pic"] for s in b["steps"]]
        out.append(f'<text x="{left - 10}" y="{y + 13}" font-size="11.5" text-anchor="end" fill="var(--ink)"><tspan font-weight="700">'
                   f'{b["n"]}</tspan> · {html.escape(b["name"])}</text>')
        out.append(f'<line x1="{xof(min(xs)):.1f}" y1="{y + 9}" x2="{xof(max(xs)):.1f}" y2="{y + 9}" stroke="var(--line)" stroke-width="2"/>')
        for s in b["steps"]:
            col = TEAL if s["early"] else SLATE
            out.append(f'<circle cx="{xof(s["pic"]):.1f}" cy="{y + 9}" r="5" fill="{col}" stroke="var(--bg, #fff)" stroke-width="1.5">'
                       f'<title>{bl(b)}: a step at {s["pic"]:g} ms (run {b["run"]})</title></circle>')
        out.append(f'<text x="{W - right + 10}" y="{y + 13}" font-size="11" fill="var(--ink)">{tms(xs)}</text>')
        y += 26
    gx = xof(GOAL)
    out.append(f'<line x1="{gx:.1f}" y1="{top - 6}" x2="{gx:.1f}" y2="{y}" stroke="{GREEN}" stroke-width="2.5"/>')
    out.append(f'<text x="{gx + 5:.1f}" y="{y + 28}" font-size="11" fill="{GREEN}" font-weight="700">16.7 ms: one 60 fps frame</text>')
    log_axis(out, xof, top - 6, y, [(10, "10 ms"), (100, "0.1 s"), (1000, "1 s"), (10000, "10 s")])
    return svg_fig(W, y + 40, out, "; ".join(f"build {b['n']}, {b['name']}: {tms([s['pic'] for s in b['steps']])}" for b in BUILDS),
                   "One dot a step: the neck and arms sliders each stepped away from their starting value and back, with views "
                   "compiled; for builds 1 to 3, those four steps both with views compiled and not, since the picture waited for "
                   "the worker either way. The step is the slider's input event and its change event together, as a click on the "
                   "slider gives them. One run a build, Firefox on GitHub's machines, a release build each time; the runs are in "
                   "<a href=\"#builds\">the table of builds</a>.")


def fig_drags():
    """a drag's frames a second, build by build, compiled and not"""
    W, left, right = 940, 250, 20
    xof = lambda fps: left + fps / 60 * (W - left - right - 150)
    out = []
    title(out, "A 3-second drag of the Witch's neck slider, frames a second, build by build (Firefox)")
    y = 30
    for i, (col, txt) in enumerate(((TEAL, "views and the run compiled: the picture follows the drag"),
                                    (GREY, "nothing compiled: only the slider moves; the picture waits for the release"))):
        x = 16 + i * 400
        out.append(f'<rect x="{x}" y="{y + 1}" width="12" height="11" rx="2" fill="{col}"/><text x="{x + 17}" y="{y + 10}" font-size="11" fill="var(--ink)">{txt}</text>')
    y = 52
    top = y
    for b in [b for b in BUILDS if b.get("drag") and b["drag"].get("on")]:
        out.append(f'<text x="{left - 10}" y="{y + 22}" font-size="11.5" text-anchor="end" fill="var(--ink)"><tspan font-weight="700">'
                   f'{b["n"]}</tspan> · {html.escape(b["name"])}</text>')
        for i, (m, col) in enumerate((("on", TEAL), ("off", GREY))):
            r = b["drag"].get(m)
            if not r:
                continue
            st = r["stats"]
            yy = y + 4 + i * 18
            out.append(f'<rect x="{left}" y="{yy}" width="{xof(st["fps"]) - left:.1f}" height="14" rx="2" fill="{col}">'
                       f'<title>{bl(b)}, {"compiled" if m == "on" else "nothing compiled"}: {st["fps"]:g} fps, median frame {st["median_ms"]:g} ms (run {b["run"]})</title></rect>')
            ends = [xof(st["fps"])]
            for run, commit, what, dr in b["rep_drags"]:
                if dr.get(m):
                    f2 = dr[m]["stats"]["fps"]
                    out.append(f'<circle cx="{xof(f2):.1f}" cy="{yy + 7}" r="4" fill="none" stroke="var(--ink)" stroke-width="1.5">'
                               f'<title>{bl(b)} again, {what}: {f2:g} fps (run {run}, {commit})</title></circle>')
                    ends.append(xof(f2))
            out.append(f'<text x="{max(ends) + 8:.1f}" y="{yy + 11}" font-size="11" fill="var(--ink)">{st["fps"]:g} fps, median frame {st["median_ms"]:g} ms</text>')
        y += 46
    gx = xof(60)
    out.append(f'<line x1="{gx:.1f}" y1="{top - 4}" x2="{gx:.1f}" y2="{y}" stroke="{GREEN}" stroke-width="2.5"/>')
    out.append(f'<text x="{gx + 5:.1f}" y="{y + 14}" font-size="11" fill="{GREEN}" font-weight="700">60 fps</text>')
    for v in (0, 15, 30, 45):
        x = xof(v)
        out.append(f'<line x1="{x:.1f}" y1="{top - 4}" x2="{x:.1f}" y2="{y}" stroke="var(--line)" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{y + 14}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{v}</text>')
    b7 = B[7]
    reps = "; ".join(f"{dr['on']['stats']['fps']:g} fps compiled in run {run} ({what})" for run, _, what, dr in b7["rep_drags"])
    return svg_fig(W, y + 26, out, "; ".join(f"build {b['n']}: {b['drag']['on']['stats']['fps']:g} fps compiled, {b['drag']['off']['stats']['fps']:g} nothing compiled"
                                             for b in BUILDS if b.get("drag") and b["drag"].get("on")),
                   "The same drag each time: one input event a frame as the slider sweeps from 0 to 60 and back, and one change "
                   "event at the end, as a browser delivers a drag; every frame timed with requestAnimationFrame, as the overlay "
                   "times it. One drag each way in each build's run. The open circles are build 7 measured twice more, the app "
                   f"unchanged: {reps}. So one run can differ from the next by a third, and a single run's number is a reading, "
                   "not a constant.")


def fig_drag():
    """build 8: every frame of the drag, both ways, one tick a frame"""
    W, left, right = 940, 250, 20
    lo, hi = math.log10(5), math.log10(3000)
    xof = lambda ms: left + (math.log10(max(ms, 5)) - lo) / (hi - lo) * (W - left - right)
    out = []
    title(out, "Build 8: every frame of a 3-second drag of the Witch's neck slider, in Firefox, one tick a frame (a log scale)")
    y = 40
    for m, name in (("on", "compiled: the picture follows"), ("off", "nothing compiled: it waits")):
        r = NOW["drag"][m]
        st = r["stats"]
        out.append(f'<text x="{left - 10}" y="{y + 16}" font-size="11.5" text-anchor="end" fill="var(--ink)">{name}</text>')
        for f in r["frames"]:
            x = xof(f)
            col = GREEN if f <= GOAL * 1.05 else "#d97706" if f <= 2 * GOAL * 1.05 else "#dc2626"
            out.append(f'<line x1="{x:.1f}" y1="{y + 2}" x2="{x:.1f}" y2="{y + 22}" stroke="{col}" stroke-width="1.5" opacity="0.7"/>')
        out.append(f'<text x="{left}" y="{y + 38}" font-size="11" fill="var(--ink)">{st["frames"]} frames in {r["ms"] / 1000:.1f} s: '
                   f'{st["fps"]:g} fps; median {st["median_ms"]:g} ms, 90th percentile {st["p90_ms"]:g} ms, longest {st["max_ms"]:g} ms; '
                   f'{st["within_16_7"]} of {st["frames"]} in one 60 fps frame</text>')
        y += 56
    gx = xof(GOAL)
    out.append(f'<line x1="{gx:.1f}" y1="32" x2="{gx:.1f}" y2="{y}" stroke="{GREEN}" stroke-width="2"/>')
    log_axis(out, xof, 32, y, [(10, "10 ms"), (16.7, "16.7"), (100, "100 ms"), (1000, "1 s")])
    return svg_fig(W, y + 30, out, "; ".join(f"{m}: {NOW['drag'][m]['stats']['fps']} fps" for m in ("on", "off")),
                   f"<b class=\"build\">Build 8</b> (change C, {NOW['commit']}), run {NOW['run']}. Green: one display frame; amber: two; "
                   "red: three or more. A frame of about 16 or 17 ms is the display's own pace, 60 a second; nothing can be quicker.")


def fig_frame():
    """build 8: a compiled drag's median frame, from the page's own timeline over the drag, per frame"""
    r = NOW["drag"]["on"]
    n = r["stats"]["frames"]
    marks = r.get("marks") or {}
    per = lambda k: marks.get(k, {"ms": 0})["ms"] / n
    parts = [("the page's view", per("view"), "#2563eb"), ("the slide's run, compiled", per("hazel-jit: the run"), TEAL),
             ("after display", per("after display"), "#93c5fd"), ("update", per("update"), "#bfdbfe")]
    med = r["stats"]["median_ms"]
    rest = max(0.0, med - sum(v for _, v, _ in parts))
    parts.append(("the rest: the browser's own diff, layout and paint (not timed)", rest, "#d1d5db"))
    W, left, right = 940, 16, 20
    sc = (W - left - right) / max(med, GOAL) * 0.95
    out = []
    title(out, f"Build 8: a compiled drag's median frame, {med:g} ms, and where it goes (per frame, over the drag)")
    x = left
    for name, v, col in parts:
        w = v * sc
        out.append(f'<rect x="{x:.1f}" y="34" width="{max(1, w):.1f}" height="26" fill="{col}" stroke="var(--bg, #fff)" stroke-width="1"><title>{html.escape(name)}: {v:.1f} ms</title></rect>')
        x += w
    y = 82
    for name, v, col in parts:
        out.append(f'<rect x="{left}" y="{y - 10}" width="12" height="12" fill="{col}"/>')
        out.append(f'<text x="{left + 16}" y="{y}" font-size="11" fill="var(--ink)">{html.escape(name)}: {v:.1f} ms</text>')
        y += 18
    gx = left + GOAL * sc
    out.append(f'<line x1="{gx:.1f}" y1="28" x2="{gx:.1f}" y2="66" stroke="{GREEN}" stroke-width="2.5"/>')
    out.append(f'<text x="{gx + 4:.1f}" y="30" font-size="11" fill="{GREEN}" font-weight="700">16.7 ms</text>')
    return svg_fig(W, y + 4, out, "; ".join(f"{nm}: {v:.1f} ms" for nm, v, _ in parts),
                   f"<b class=\"build\">Build 8</b>, run {NOW['run']}: the page's timeline (<code>Util.BenchMarks</code>) summed over "
                   f"the drag and divided by its {n} frames. The rest of the median frame is the browser's own work after the "
                   "view, which the timeline does not time.")


LANES = [
    ("the slide's run, compiled", lambda w: w == "hazel-jit: the run", TEAL),
    ("the page: update, statics, view", lambda w: w in ("update", "syntax", "calculate", "statics", "view", "after display", "cursor info", "color map"), "#2563eb"),
    ("the edited program compiled again", lambda w: w == "hazel-jit: the run compiled", "#ea580c"),
    ("the worker: its run", lambda w: w.startswith("worker: ") and w not in ("worker: encode result",), GREY),
    ("the answer: encoded, decoded", lambda w: w in ("worker: encode result", "worker message decoded"), "#f59e0b"),
]


def done_of(e):
    return [t for t, s in e["dynamics"] if s == "ok"][-1]


def fig_step():
    """build 8: one step on a timeline (049's figure, on this build's run)"""
    es = NOW_W["edits"]["on"]
    e = min((x for x in es if x["picture_changed_ms"] < done_of(x)), key=lambda x: x["picture_changed_ms"], default=es[0])
    done = done_of(e)
    end = max(done, e["picture_changed_ms"])
    W, left, right = 940, 250, 20
    xof = lambda t: left + t / (end * 1.04) * (W - left - right)
    out = []
    title(out, f"Build 8: one step ({e['label']} {e['from']} to {e['to']}, compiled): the picture at {e['picture_changed_ms']:g} ms, "
               f"the worker's answer at {done / 1000:.2f} s")
    y = 38
    for name, pred, col in LANES:
        out.append(f'<text x="{left - 10}" y="{y + 13}" font-size="11.5" text-anchor="end" fill="var(--ink)">{html.escape(name)}</text>')
        for m in e["marks"]:
            if pred(m["what"]) and "ms" in m and m["at"] >= 0 and m["at"] <= end:
                x0, x1 = xof(m["at"]), xof(m["at"] + m["ms"])
                out.append(f'<rect x="{x0:.1f}" y="{y + 2}" width="{max(1.5, x1 - x0):.1f}" height="14" fill="{col}">'
                           f'<title>{html.escape(m["what"])}: {m["ms"]:g} ms at {m["at"]:g} ms</title></rect>')
        y += 24
    marks = [(e["picture_changed_ms"], f"the slider and the picture drawn, {e['picture_changed_ms']:g} ms", "var(--ink)"),
             (done, f"the worker's answer, {done:g} ms", "var(--muted)"), (GOAL, "16.7 ms", GREEN)]
    for i, (t, label, col) in enumerate(marks):
        x = xof(t)
        out.append(f'<line x1="{x:.1f}" y1="32" x2="{x:.1f}" y2="{y}" stroke="{col}" stroke-width="{2 if col == GREEN else 1}" stroke-dasharray="{"" if col == GREEN else "3 3"}"/>')
        anchor = "start" if t < end * 0.8 else "end"
        out.append(f'<text x="{x + (4 if anchor == "start" else -4):.1f}" y="{y + 13 + 13 * i}" font-size="10.5" text-anchor="{anchor}" fill="{col}">{html.escape(label)}</text>')
    h = y + 22 + 13 * len(marks)
    return svg_fig(W, h, out, "timeline of one slider step on build 8",
                   f"<b class=\"build\">Build 8</b>, run {NOW['run']}: the quickest of its four steps, from the page's own timeline and "
                   "the worker's (<code>Util.BenchMarks</code>), each block a measured piece of work at the time it started; the "
                   "worker's blocks are on its own thread, the rest on the page's. ^report(49) has the same figure for build 4's "
                   "app.")


# (interpreter against compiled, as each report gives them: ms, as (low, high))
PAIRS = [
    ("a recursive sum of 1,000 numbers (Node)", (47.9, 47.9), (0.042, 0.042), "045#speed"),
    ("the Petri net rule, four events (Node)", (7.19, 7.19), (0.011, 0.011), "045#speed"),
    ("the Polygons view, a render with its trip (Node)", (13.7, 13.7), (0.34, 0.34), "045#speed"),
    ("the Witch's polygon editors' views (Firefox)", (26, 29), (0.29, 0.45), "046#witch-firefox"),
    ("the Witch's picture view (Firefox)", (87, 87), (3.0, 3.0), "046#witch-firefox"),
    ("the Witch's whole run (Node)", (502, 529), (4.2, 5.0), "045#run"),
]
mid = lambda ab: (ab[0] * ab[1]) ** 0.5
RATIOS = [round(mid(i) / mid(c)) for _, i, c, _ in PAIRS]


def fig_compiled():
    W, left, right = 940, 330, 20
    lo, hi = math.log10(0.005), math.log10(2000)
    xof = lambda ms: left + (math.log10(ms) - lo) / (hi - lo) * (W - left - right)
    out = []
    title(out, "The same Hazel code on Hazel's interpreter (grey) and as hazel-jit's JavaScript (teal), each as its report measured it (a log scale)")
    y = 40
    for (label, (ia, ib), (ca, cb), rep), x in zip(PAIRS, RATIOS):
        out.append(f'<text x="{left - 10}" y="{y + 13}" font-size="11.5" text-anchor="end" fill="var(--ink)">{html.escape(label)}</text>')
        xi, xc = xof(mid((ia, ib))), xof(mid((ca, cb)))
        out.append(f'<line x1="{xc:.1f}" y1="{y + 9}" x2="{xi:.1f}" y2="{y + 9}" stroke="var(--line)" stroke-width="3"/>')
        for (a, b), col in (((ia, ib), GREY), ((ca, cb), TEAL)):
            out.append(f'<rect x="{xof(a) - 4:.1f}" y="{y + 3}" width="{max(8, xof(b) - xof(a) + 8):.1f}" height="12" rx="6" fill="{col}">'
                       f'<title>{html.escape(label)}: {a:g} to {b:g} ms</title></rect>')
        lab = f"about {x:,} times ({rep.split('#')[0]})"
        if xi + 10 + 5.8 * len(lab) > W - 4:
            out.append(f'<text x="{xc - 12:.1f}" y="{y + 13}" font-size="11" text-anchor="end" fill="var(--ink)">{lab}</text>')
        else:
            out.append(f'<text x="{xi + 10:.1f}" y="{y + 13}" font-size="11" fill="var(--ink)">{lab}</text>')
        y += 26
    gx = xof(GOAL)
    out.append(f'<line x1="{gx:.1f}" y1="32" x2="{gx:.1f}" y2="{y}" stroke="{GREEN}" stroke-width="2.5"/>')
    out.append(f'<text x="{gx + 5:.1f}" y="{y + 28}" font-size="11" fill="{GREEN}" font-weight="700">16.7 ms</text>')
    log_axis(out, xof, 32, y, [(0.01, "10 µs"), (0.1, "0.1 ms"), (1, "1 ms"), (10, "10 ms"), (100, "0.1 s"), (1000, "1 s")])
    return svg_fig(W, y + 40, out, "; ".join(f"{l}: {a[0]:g} ms on the interpreter, {c[0]:g} ms compiled" for l, a, c, _ in PAIRS),
                   "Not a build of the app: each row is one piece of Hazel code run two ways. Medians in Node 22 on a laptop "
                   "(^report(45)), and renders in Firefox in the app (^report(46)). A render's time is its view's work alone, as "
                   "if the update were free. The ratio is of the middles of the ranges.")


COMPILERS = [("Melange", 0.46), ("ReScript", 0.55), ("js_of_ocaml (a best case)", 0.71), ("JS written by hand", 0.90),
             ("hazel-jit", 1.59), ("Hazel's interpreter", 358)]


def fig_compilers():
    W, left, right = 940, 250, 20
    lo, hi = math.log10(0.1), math.log10(1000)
    xof = lambda us: left + (math.log10(us) - lo) / (hi - lo) * (W - left - right)
    out = []
    title(out, "One call of report 043's Petri net rule, median µs, in Node (report 046; a log scale)")
    y = 36
    for label, us in COMPILERS:
        col = TEAL if label == "hazel-jit" else GREY if "interpreter" in label else "#93c5fd"
        out.append(f'<text x="{left - 10}" y="{y + 12}" font-size="11.5" text-anchor="end" fill="var(--ink)">{html.escape(label)}</text>')
        out.append(f'<rect x="{left}" y="{y + 2}" width="{xof(us) - left:.1f}" height="13" rx="2" fill="{col}"><title>{label}: {us:g} µs</title></rect>')
        out.append(f'<text x="{xof(us) + 6:.1f}" y="{y + 12}" font-size="11" fill="var(--ink)">{us:g} µs</text>')
        y += 22
    log_axis(out, xof, 30, y, [(0.1, "0.1 µs"), (1, "1 µs"), (10, "10 µs"), (100, "100 µs"), (1000, "1 ms")])
    return svg_fig(W, y + 30, out, "; ".join(f"{l}: {u:g} µs" for l, u in COMPILERS),
                   "Not a build of the app: each answers the same 2,000 events and ends on the same marking (^report(46), how "
                   "fast). js_of_ocaml's is a best case: it inlined the rule into the timing loop.")


def fig_data():
    """^report(47)'s experiment 1: the Witch's picture as Hazel's terms and as data"""
    W = 940
    rows = [("its size, KB", 142.2, 48.0, None, None), ("its trip by Marshal, encoded and decoded, ms", 15.0, 4.38, 25.7, 7.28)]
    out = []
    title(out, "The Witch's picture as Hazel's terms (grey) and as data (blue): report 047, experiment 1")
    y = 38
    for label, t, dd, t2, d2 in rows:
        top = max(t, t2 or 0)
        sc = lambda v: v / top * (W - 330)
        out.append(f'<text x="16" y="{y + 12}" font-size="11.5" fill="var(--ink)">{label}</text>')
        for i, (a, b, col, name) in enumerate(((t, t2, GREY, "terms"), (dd, d2, "#2563eb", "data"))):
            yy = y + 18 + i * 18
            out.append(f'<rect x="300" y="{yy}" width="{sc(b or a):.1f}" height="13" rx="2" fill="{col}" opacity="{0.5 if b else 1}"/>')
            out.append(f'<rect x="300" y="{yy}" width="{sc(a):.1f}" height="13" rx="2" fill="{col}"><title>{name}: {a:g}{f" to {b:g}" if b else ""}</title></rect>')
            out.append(f'<text x="290" y="{yy + 11}" font-size="11" text-anchor="end" fill="var(--muted)">{name}</text>')
            out.append(f'<text x="{300 + sc(b or a) + 6:.1f}" y="{yy + 11}" font-size="11" fill="var(--ink)">{a:g}{f" to {b:g}" if b else ""}</text>')
        y += 62
    return svg_fig(W, y, out, "the picture: 142.2 KB as terms, 48.0 KB as data; trip 15.0 to 25.7 ms as terms, 4.38 to 7.28 ms as data",
                   "Not a build of the app: the picture's value, held two ways. As data: no ids, no sharing to find, numbers "
                   "packed (^report(47)); the lighter bar is the slowest of the readings.")


def kept(nnn, name):
    return open(os.path.join(ROOT, nnn, "figs", name + ".html")).read().strip()


def kept_fig(nnn, name, caption):
    return (f'<div class="figrow"><figure class="f wide">{kept(nnn, name)}<figcaption>{caption}</figcaption></figure></div>')


def builds_table():
    rows = []
    for b in BUILDS:
        xs = [s["pic"] for s in b["steps"]]
        if b.get("pooled"):
            step = f"{tms(xs)}<br><span class=\"muted\">compiled views or not: the picture waited for the worker</span>"
        else:
            early = [s["pic"] for s in b["steps"] if s["early"]]
            late = [s["pic"] for s in b["steps"] if not s["early"]]
            step = tms(early) + (f"<br><span class=\"muted\">steps back: {tms(late)}</span>" if late else "")
            step += f"<br><span class=\"muted\">nothing compiled: {tms([s['pic'] for s in b['steps_off']])}</span>"
        dr = b.get("drag") or {}
        if dr.get("on"):
            drag = f"{dr['on']['stats']['fps']:g} fps<br><span class=\"muted\">nothing compiled: {dr['off']['stats']['fps']:g}</span>"
            if b.get("rep_drags"):
                drag += "<br><span class=\"muted\">again: " + " and ".join(f"{d['on']['stats']['fps']:g}" for _, _, _, d in b["rep_drags"]) + "</span>"
        else:
            drag = "<span class=\"muted\">not measured</span>"
        run = f"run {b['run']}" + ("".join(f", {r}" for r, _, _, _ in b.get("rep_drags", [])))
        rows.append(f'<tr{" class=\"now\"" if b is NOW else ""}><td><b>{b["n"]} · {html.escape(b["name"])}</b><br>'
                    f'<span class="muted"><code>{b["commit"]}</code>, {run}, 11-08 {b["at"]}</span></td><td>{b["adds"]}</td>'
                    f'<td>{step}</td><td>{drag}</td></tr>')
    return ('<table class="vals builds"><tr><th>build</th><th>what it adds to the build above it</th>'
            '<th>a step, compiled</th><th>a drag, compiled</th></tr>' + "".join(rows) + "</table>")


REPORTS = [
    ("045", "hazel-jit: Livelit Views Compiled to JavaScript",
     "A livelit's view compiled to JS runs 40 to 1,150 times faster than on the interpreter; in Firefox, compiled views draw what the interpreter draws; the Witch's whole run, compiled, 4.2 to 5.0 ms in Node."),
    ("046", "BuckleScript, ReScript and Melange, beside hazel-jit",
     "hazel-jit's code is about 2.9 times ReScript's and 1.8 times hand-written JS on the Petri rule; on the Witch's picture all five are within 15%; builds 1 to 3 here: a small edit took 5.3 to 8.8 s, and two changes brought it to 1.3 to 1.7 s."),
    ("047", "First-Order Data in a Form of Its Own",
     "As data, the Witch's picture is 3 times smaller and 2.5 to 4.3 times quicker to send; building values as data saves the evaluator a couple of percent at most, so the run itself has to be compiled."),
    ("048", "Why Hazel Is Slow: A Thousand Cuts",
     "196 measured costs from 33 reports, from four design choices applied everywhere; remove the largest and the next is there."),
    ("049", "The Witch’s Run, Compiled, in the Page",
     "Builds 4 and 5 here: the slide's whole run, compiled and run in the page at a slider's step, 8 to 21 ms; the picture at the page's first redraw, 286 to 386 ms, against 1.35 to 1.74 s."),
]


def reports_table():
    rows = "".join(f'<tr><td><a href="../{n}/">report {n}</a></td><td>{html.escape(t)}</td><td>{html.escape(a)}</td></tr>' for n, t, a in REPORTS)
    return '<table class="vals"><tr><th>report</th><th>title</th><th>its answer</th></tr>' + rows + "</table>"


# --- the numbers the text quotes ---
NUMS = {"now_run": NOW["run"], "now_commit": NOW["commit"], "r_lo": f"{min(RATIOS):,}", "r_hi": f"{max(RATIOS):,}",
        "r_run": f"{RATIOS[-1]:,}"}
for n, b in B.items():
    xs = [s["pic"] for s in b["steps"]]
    NUMS[f"b{n}_step"] = tms(xs)
    NUMS[f"b{n}_run"] = b["run"]
    if b.get("steps_off"):
        NUMS[f"b{n}_step_off"] = tms([s["pic"] for s in b["steps_off"]])
    for m in ("on", "off"):
        r = (b.get("drag") or {}).get(m)
        if r:
            for k in ("fps", "median_ms", "p90_ms", "max_ms", "within_16_7", "frames"):
                NUMS[f"b{n}_{m}_{k}"] = f"{r['stats'][k]:g}"
_f = NOW["drag"]["on"]["frames"]
NUMS["now_pct"] = f"{100 * NOW['drag']['on']['stats']['within_16_7'] / len(_f):.0f}"
NUMS["now_miss"] = str(len(_f) - NOW["drag"]["on"]["stats"]["within_16_7"])
NUMS["now_miss_most"] = str(max(round(f / GOAL) for f in _f))
_mk, _n = NOW["drag"]["on"].get("marks") or {}, NOW["drag"]["on"]["stats"]["frames"]
NUMS["now_view"] = f"{_mk['view']['ms'] / _n:.1f}"
NUMS["now_run_ms"] = f"{_mk['hazel-jit: the run']['ms'] / _n:.1f}"
NUMS["b1_frames"] = f"{min(s['pic'] for s in B[1]['steps']) / GOAL:.0f} to {max(s['pic'] for s in B[1]['steps']) / GOAL:.0f}"
NUMS["now_frames"] = f"{min(s['pic'] for s in NOW['steps']) / GOAL:.0f} to {max(s['pic'] for s in NOW['steps']) / GOAL:.0f}"
NUMS["b7_all"] = ", ".join(f"{x:g}" for x in sorted([B[7]["drag"]["on"]["stats"]["fps"]] + [d["on"]["stats"]["fps"] for _, _, _, d in B[7]["rep_drags"]]))
NUMS["problems"] = str(sum(b.get("problems", 0) for b in BUILDS))
# (build 8's quickest step from the compiled run, for the step's timeline in words)
_es = [x for x in NOW_W["edits"]["on"] if x["picture_changed_ms"] < done_of(x)]
_e = min(_es, key=lambda x: x["picture_changed_ms"])
_views = sorted([m for m in _e["marks"] if m["what"] == "view" and 0 <= m["at"] <= _e["picture_changed_ms"]], key=lambda m: m["at"])
NUMS["st_pic"] = f"{_e['picture_changed_ms']:g}"
NUMS["st_view"] = f"{max(m['ms'] for m in _views):g}"
NUMS["st_statics"] = f"{sum(m['ms'] for m in _e['marks'] if m['what'] == 'calculate' and 0 <= m['at'] <= _e['picture_changed_ms']):g}"
NUMS["st_recompile"] = f"{sum(m['ms'] for m in _e['marks'] if m['what'] == 'hazel-jit: the run compiled'):g}"
NUMS["st_done"] = f"{done_of(_e) / 1000:.2f}"

body = open(os.path.join(HERE, "body.html")).read().replace("{{updated}}", updated)
FIGS = {"road": fig_road(), "drags": fig_drags(), "drag": fig_drag(), "frame": fig_frame(), "step": fig_step(),
        "compiled": fig_compiled(), "compilers": fig_compilers(), "data": fig_data()}
os.makedirs(os.path.join(HERE, "figs"), exist_ok=True)
for name, fig in FIGS.items():
    m = re.search(r"<svg.*?</svg>", fig, re.S)
    if m:
        open(os.path.join(HERE, "figs", name + ".html"), "w").write(m.group(0) + "\n")
for k, v in FIGS.items():
    body = body.replace("{{fig_" + k + "}}", v)
body = body.replace("{{fig_cuts48}}", kept_fig("048", "cuts", "Not a build of the app: every cost the series has measured in Hazel, one rectangle each, grouped by the design choice it comes from and coloured by where it stands (^report(48)). Hover a rectangle for the cost."))
body = body.replace("{{builds_table}}", builds_table())
body = body.replace("{{reports_table}}", reports_table())
for k, v in NUMS.items():
    body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{[a-z_0-9]+\}\}", body)
if left:
    sys.exit(f"unfilled: {sorted(set(left))}")
TITLE = "Toward 60 fps: hazel-jit So Far"
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n"
        "<meta name=\"description\" content=\"Can a livelit's slider in Hazel move at 60 frames a second? On the Witch slide, a drag now runs at 48 fps with the picture following, from under 10: eight builds of one branch, each measured in Firefox, and what is left. Try it yourself.\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
print("wrote 050/index.html; updated", updated)
print(json.dumps(NUMS, indent=0))
