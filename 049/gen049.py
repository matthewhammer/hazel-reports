#!/usr/bin/env python3
"""^report(49): the Witch slide's whole run, compiled by hazel-jit, at a slider's step in the app, in Firefox. Writes
049/index.html from body.html and the Firefox runs in data/runs/ (scripts/jit_slides.py's jit.json, one folder a run),
with the series' styles (035's). ^ticket(722); the Node numbers it follows are ^report(45)'s #run."""
import html, json, math, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "047"))
import treemap as TM  # noqa: F401  (kept for parity with 048's generator)

s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
EXTRA = """
  ol.outline > li { margin: 4px 0; } .muted { color: var(--muted); }
  table.vals { display: block; overflow-x: auto; max-width: 100%; border-collapse: collapse; margin: 0.6em 0 1em; font-size: 0.88em; }
  table.vals th, table.vals td { padding: 4px 8px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
  table.vals td.n { text-align: right; font-variant-numeric: tabular-nums; }
  table.vals th { font-weight: 600; } figure.f { margin: 1.2em 0; } figure.f svg { max-width: 100%; }
  figcaption { color: var(--muted); font-size: 0.9em; margin-top: 6px; max-width: 80ch; }
  .pair { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px; margin: 0.8em 0; }
  .pair pre { margin: 0; font-size: 0.8em; white-space: pre-wrap; overflow-wrap: anywhere; }
  .pair .cap { font-size: 0.85em; color: var(--muted); margin: 0 0 4px; }
  .big { font-size: 1.05em; }
"""
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
GOAL = 1000 / 60

# The runs, in the order they were made: each a push to trial/694-view-jit and its "hazel-jit in Firefox" run
# (.github/workflows/jit.yml: a release build served, scripts/jit_slides.py in Firefox, every polygon slide loaded with
# compiled views on and off, the Witch's four slider steps each way).
RUNS = [
    {"run": "42547578825", "commit": "1d445a24cc", "only": "Witch",
     "what": "the app wired: at a livelit's event, the slide's compiled run is called with the new model",
     "showed": "never used: the page compiled the program after each edit, but no event ran it, and the reason went only to the console"},
    {"run": "42548426910", "commit": "06a3880c01", "only": "",
     "what": "every event, answer and reason not to run counted in the page, for the check to read",
     "showed": "on every slide and event: none of the program's livelit uses has a model parameter"},
    {"run": "42549941977", "commit": "932fbdcc63", "only": "",
     "what": "each livelit use's view folded into the compiled run, as Statics folds a probed use's",
     "showed": "the run fires at every event, 1 to 7 ms; 52 of the Witch's 53 uses folded; the picture, a macro livelit, not"},
    {"run": "42551267058", "commit": "6d71c427bf", "only": "",
     "what": "a macro livelit's view folded too, from the definition the page notes as it draws the use",
     "showed": "all 53 folded; the picture drawn from the compiled run at the page's first redraw in 2 of 4 steps, the steps away from a slider's starting value"},
    {"run": "42554043524", "commit": "a51dc778dd", "only": "",
     "what": "a step back to a slider's starting value no longer taken for an undo; the answers kept until the worker's sample of the model catches up",
     "showed": None},
]
RUNS = [r for r in RUNS if os.path.exists(os.path.join(HERE, "data", "runs", r["run"], "jit.json"))]
for r in RUNS:
    r["d"] = json.load(open(os.path.join(HERE, "data", "runs", r["run"], "jit.json")))


def witch(d):
    return next(s for s in d["slides"] if s.get("slide") == "Witch")


def counts(s, mode="on"):
    return ((s[mode] or {}).get("jit") or {}).get("counts") or {}


def whys(s, mode="on"):
    return ((s[mode] or {}).get("jit") or {}).get("why") or {}


def edit_row(e, mode):
    ms = e["marks"]
    runs = sorted([m for m in ms if m["what"] == "hazel-jit: the run" and m["at"] >= 0], key=lambda m: m["at"])
    comp = [m for m in ms if m["what"] == "hazel-jit: the run compiled" and m["at"] >= 0]
    done = [t for t, s in e["dynamics"] if s == "ok"][-1]
    return {"label": e["label"], "from": e["from"], "to": e["to"], "mode": mode, "own": e["own_first_ms"],
            "pic": e["picture_changed_ms"], "done": done, "early": e["picture_changed_ms"] < done,
            "runs": [m["ms"] for m in runs], "recompile": [m["ms"] for m in comp],
            "drawn_total": (e.get("jit") or {}).get("drawn from the compiled run", 0)}


for r in RUNS:
    w = witch(r["d"])
    r["edits"] = [edit_row(e, m) for m in ("on", "off") for e in w["edits"][m]]
    prev = 0
    for x in r["edits"]:
        if x["mode"] == "on":
            x["drawn_from_run"], prev = x["drawn_total"] - prev, x["drawn_total"]
        else:
            x["drawn_from_run"] = 0

FIRES = [r for r in RUNS if any(x["runs"] for x in r["edits"])]
MAIN = FIRES[-1] if FIRES else RUNS[-1]          # the latest run in which the compiled run fired
ON = [x for x in MAIN["edits"] if x["mode"] == "on"]
OFF = [x for x in MAIN["edits"] if x["mode"] == "off"]
first = [x["runs"][0] for x in ON if x["runs"]]
second = [x["runs"][1] for x in ON if len(x["runs"]) > 1]
rng = lambda xs, f="{:.0f}": (f.format(min(xs)) if f.format(min(xs)) == f.format(max(xs)) else f"{f.format(min(xs))} to {f.format(max(xs))}")
srng = lambda xs: rng([x / 1000 for x in xs], "{:.2f}")
fps = lambda ms: f"{1000 / ms:,.0f}"


def fig_step():
    """the headline: each part of a slider's step, a log scale, against the goal"""
    W, left, right = 940, 360, 30
    lo, hi = math.log10(0.5), math.log10(5000)
    xof = lambda ms: left + (math.log10(ms) - lo) / (hi - lo) * (W - left - right)
    rows = [
        ("the slide's run, compiled: a step's first event", first, "#0d9488"),
        ("the same, the step's next event (a drag)", second, "#0d9488"),
        ("the picture, drawn from the compiled run", PIC_FROM_RUN, "#2563eb"),
        ("the slider's own livelit redrawn", [x["own"] for x in ON], "#2563eb"),
        ("the picture, after the worker (steps back)", PIC_LATE, "#9ca3af"),
        ("the picture, nothing compiled", [x["pic"] for x in OFF], "#9ca3af"),
    ]
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">One step of a slider on the Witch slide, '
           'in Firefox: each part, from the slider\'s event (a log scale)</text>']
    y = 40
    for label, xs, col in rows:
        if not xs:
            continue
        a, b = min(xs), max(xs)
        out.append(f'<text x="{left - 10}" y="{y + 14}" font-size="11.5" text-anchor="end" fill="var(--ink)">{html.escape(label)}</text>')
        out.append(f'<rect x="{xof(a):.1f}" y="{y + 3}" width="{max(4, xof(b) - xof(a)):.1f}" height="14" fill="{col}" rx="2">'
                   f'<title>{html.escape(label)}: {a:g} to {b:g} ms ({len(xs)} readings, run {MAIN["run"]})</title></rect>')
        txt = (f"{rng(xs)} ms" if b < 1000 else f"{srng(xs)} s") + (f", about {fps(b)} to {fps(a)} fps" if b < 100 else f", {a / GOAL:.0f} to {b / GOAL:.0f} frames")
        if xof(b) + 8 + 5.6 * len(txt) > W - 4:
            out.append(f'<text x="{xof(a) - 8:.1f}" y="{y + 14}" font-size="11" text-anchor="end" fill="var(--ink)">{txt}</text>')
        else:
            out.append(f'<text x="{xof(b) + 8:.1f}" y="{y + 14}" font-size="11" fill="var(--ink)">{txt}</text>')
        y += 28
    gx = xof(GOAL)
    out.append(f'<line x1="{gx:.1f}" y1="32" x2="{gx:.1f}" y2="{y}" stroke="#15803d" stroke-width="2.5"/>')
    out.append(f'<text x="{gx + 5:.1f}" y="{y + 13}" font-size="11" fill="#15803d" font-weight="700">16.7 ms: 60 fps, the floor</text>')
    for ms in (1, 10, 100, 1000):
        x = xof(ms)
        out.append(f'<line x1="{x:.1f}" y1="32" x2="{x:.1f}" y2="{y}" stroke="var(--line)" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{y + 28}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{ms:g} ms</text>')
    h = y + 36
    alt = "; ".join(f"{l}: {min(xs):g} to {max(xs):g} ms" for l, xs, _ in rows if xs)
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{html.escape(alt)}" '
            f'style="width:100%;height:auto;display:block">' + "".join(out) + "</svg><figcaption>Four steps of two sliders (neck 28 to 30 "
            "and back, arms 55 to 65 and back), each bar from the fastest to the slowest of them; the grey bars with nothing "
            f"compiled are the same four steps after a fresh load. Firefox on GitHub's machines, a release build of "
            f"<code>trial/694-view-jit</code> at {MAIN['commit']}, run {MAIN['run']}. A step is two events (the slider's input, "
            "then its change), so the compiled run is called twice; the second is warm. The frames assume nothing else in "
            "the frame costs anything.</figcaption></figure></div>")


# (one edit's timeline: the page's marks and the worker's, laid on one time axis from the slider's event)
LANES = [
    ("the slide's run, compiled", lambda w: w == "hazel-jit: the run", "#0d9488"),
    ("the page: update, statics, view", lambda w: w in ("update", "syntax", "calculate", "statics", "view", "after display", "cursor info", "color map"), "#2563eb"),
    ("the edited program compiled again", lambda w: w == "hazel-jit: the run compiled", "#ea580c"),
    ("the worker: its run", lambda w: w.startswith("worker: ") and w not in ("worker: encode result",), "#9ca3af"),
    ("the answer: encoded, decoded", lambda w: w in ("worker: encode result", "worker message decoded"), "#f59e0b"),
]


def fig_edit():
    w = witch(MAIN["d"])
    es = w["edits"]["on"]
    # (the fastest step whose picture came from the compiled run; the axis runs on to the worker's answer)
    e = min((x for x in es if x["picture_changed_ms"] < [t for t, s in x["dynamics"] if s == "ok"][-1]),
            key=lambda x: x["picture_changed_ms"], default=es[0])
    done = [t for t, s in e["dynamics"] if s == "ok"][-1]
    end = max(done, e["picture_changed_ms"])
    W, left, right = 940, 250, 20
    xof = lambda t: left + t / (end * 1.04) * (W - left - right)
    out = [f'<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">One step ({html.escape(e["label"])} '
           f'{e["from"]} to {e["to"]}, views compiled): the picture at {e["picture_changed_ms"]:g} ms, the worker\'s answer at {done / 1000:.2f} s</text>']
    y = 38
    for name, pred, col in LANES:
        out.append(f'<text x="{left - 10}" y="{y + 13}" font-size="11.5" text-anchor="end" fill="var(--ink)">{html.escape(name)}</text>')
        for m in e["marks"]:
            if pred(m["what"]) and "ms" in m and m["at"] >= 0 and m["at"] <= end:
                x0, x1 = xof(m["at"]), xof(m["at"] + m["ms"])
                out.append(f'<rect x="{x0:.1f}" y="{y + 2}" width="{max(1.5, x1 - x0):.1f}" height="14" fill="{col}">'
                           f'<title>{html.escape(m["what"])}: {m["ms"]:g} ms at {m["at"]:g} ms</title></rect>')
        y += 24
    marks = [(e["picture_changed_ms"], f"the slider and the picture redrawn, {e['picture_changed_ms']:g} ms", "var(--ink)"),
             (done, f"the worker's answer, {done:g} ms", "var(--muted)"), (GOAL, "16.7 ms", "#15803d")]
    if e["own_first_ms"] != e["picture_changed_ms"]:
        marks.insert(0, (e["own_first_ms"], f"the slider redrawn, {e['own_first_ms']:g} ms", "var(--ink)"))
    for i, (t, label, col) in enumerate(marks):
        x = xof(t)
        out.append(f'<line x1="{x:.1f}" y1="32" x2="{x:.1f}" y2="{y}" stroke="{col}" stroke-width="{2 if col == "#15803d" else 1}" stroke-dasharray="{"" if col == "#15803d" else "3 3"}"/>')
        anchor = "start" if t < end * 0.8 else "end"
        out.append(f'<text x="{x + (4 if anchor == "start" else -4):.1f}" y="{y + 13 + 13 * i}" font-size="10.5" text-anchor="{anchor}" fill="{col}">{html.escape(label)}</text>')
    h = y + 22 + 13 * len(marks)
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="timeline of one slider step" '
            f'style="width:100%;height:auto;display:block">' + "".join(out) + "</svg><figcaption>The quickest of the steps whose picture came from the compiled run, from "
            "the page's own timeline and the worker's (<code>Util.BenchMarks</code>), each block a measured piece of work at the "
            "time it started; the worker's pieces are on its own thread, the rest on the page's. The green line is one 60 fps "
            f"frame. Run {MAIN['run']}.</figcaption></figure></div>")


def slides_table():
    rows = []
    for s in MAIN["d"]["slides"]:
        c = counts(s)
        rows.append(f"<tr><td>{html.escape(s['slide'])}</td><td class=n>{s['on']['livelits']}</td>"
                    f"<td class=n>{c.get('the slide' + chr(39) + 's run answered', 0)}</td><td class=n>{c.get('drawn from the compiled run', 0)}</td>"
                    f"<td class=n>{c.get('view compiled', 0)}</td><td class=n>{c.get('view on the interpreter', 0)}</td></tr>")
    return ('<table class="vals"><tr><th>slide</th><th>livelits</th><th>events the compiled run answered</th>'
            '<th>livelits drawn from its answers</th><th>views compiled (drawn by the page)</th><th>views on the interpreter</th></tr>'
            + "".join(rows) + "</table>")


def runs_table():
    rows = []
    for r in RUNS:
        w = witch(r["d"])
        folded = next((k for k in whys(w) if k.startswith("the slide's run compiled:")), "")
        m = re.search(r"(\d+) livelit uses", folded)
        rows.append(f"<tr><td>{r['commit']}</td><td>{html.escape(r['what'])}</td><td><a href=\"https://github.com/hazelgrove/hazel/actions/runs/{r['run']}\">{r['run']}</a></td>"
                    f"<td class=n>{m.group(1) if m else '0'} of {w['on']['livelits']}</td><td>{html.escape(r['showed'] or SHOWED4)}</td></tr>")
    return ('<table class="vals"><tr><th>commit</th><th>what it changed</th><th>Firefox run</th><th>the Witch\'s uses folded in</th>'
            '<th>what the run showed</th></tr>' + "".join(rows) + "</table>")


def steps_table():
    rows = []
    for x in MAIN["edits"]:
        rows.append(f"<tr><td>{x['mode']}</td><td>{html.escape(x['label'])} {x['from']} to {x['to']}</td>"
                    f"<td class=n>{', '.join(f'{v:g}' for v in x['runs']) or '-'}</td><td class=n>{', '.join(f'{v:g}' for v in x['recompile']) or '-'}</td>"
                    f"<td class=n>{x['own']:g}</td><td class=n>{x['pic']:g}</td></tr>")
    return ('<table class="vals"><tr><th>views compiled</th><th>the step</th><th>the compiled run, each event (ms)</th>'
            '<th>compiled again after (ms)</th><th>the slider redrawn (ms)</th><th>the picture (ms)</th></tr>' + "".join(rows) + "</table>")


# (the picture drawn before the worker's run came back: from the compiled run's answers)
PIC_FROM_RUN = [x["pic"] for x in ON if x["early"]]
PIC_LATE = [x["pic"] for x in ON if not x["early"]]
EARLY = [x for x in ON if x["early"]]
LATE = [x for x in ON if not x["early"]]
SHOWED4 = (f"all {witch(RUNS[-1]['d'])['on']['livelits']} folded; the picture drawn from the compiled run at the page's first "
           f"redraw in {len(EARLY)} of {len(ON)} steps")

NUMS = {
    "first": rng(first), "second": rng(second), "first_fps": f"{fps(max(first))} to {fps(min(first))}",
    "own": rng([x["own"] for x in ON]), "pic_on": srng([x["pic"] for x in ON]), "pic_off": srng([x["pic"] for x in OFF]),
    "recompile": rng([v for x in ON for v in x["recompile"]]), "main_run": MAIN["run"], "main_commit": MAIN["commit"],
    "n_steps": str(len(ON)),
    "n_early": str(len(EARLY)), "pic_early": (" and ".join(f"{v:g}" for v in sorted(PIC_FROM_RUN)) if len(PIC_FROM_RUN) <= 2 else rng(PIC_FROM_RUN)) or "-",
    "pic_late": srng(PIC_LATE) if PIC_LATE else "-", "done_on": srng([x["done"] for x in ON]),
    "drawn_early": rng([x["drawn_from_run"] for x in EARLY]) if EARLY else "-",
    "drawn_late": rng([x["drawn_from_run"] for x in LATE]) if LATE else "-",
    "late_first": rng([x["runs"][0] for x in LATE]) if LATE else "-",
}
PAGE = ("update", "syntax", "calculate", "statics", "view", "after display", "cursor info", "color map")
def before_first(e, names):
    return sum(m["ms"] for m in e["marks"] if m["what"] in names and "ms" in m and 0 <= m["at"] < e["own_first_ms"])
_won = witch(MAIN["d"])["edits"]["on"]
NUMS["page_before"] = rng([before_first(e, PAGE) for e in _won])
NUMS["view_before"] = rng([before_first(e, ("view",)) for e in _won])
NUMS["calc_before"] = rng([before_first(e, ("calculate",)) for e in _won])
NUMS["statics_before"] = rng([before_first(e, ("statics", "syntax")) for e in _won])
NUMS["worker_slices"] = srng([sum(m["ms"] for m in e["marks"] if m["what"] == "worker: slices" and m["at"] > 0) for e in _won])
NUMS["views_after"] = rng([sum(m["ms"] for m in e["marks"] if m["what"] == "view" and m["at"] >= e["picture_changed_ms"]) for e in _won if e["picture_changed_ms"] < [t for t, s in e["dynamics"] if s == "ok"][-1]])
NUMS["first_fps"] = f"{fps(max(first))} to {fps(min(first))}"
NUMS["second_fps"] = f"{fps(max(second))} to {fps(min(second))}"
NUMS["frames_early"] = (" and ".join(f"{v / GOAL:.0f}" for v in sorted(PIC_FROM_RUN)) if len(PIC_FROM_RUN) <= 2
                        else f"{min(PIC_FROM_RUN) / GOAL:.0f} to {max(PIC_FROM_RUN) / GOAL:.0f}")
NUMS["off_frames"] = f"{min(x['pic'] for x in OFF) / GOAL:.0f} to {max(x['pic'] for x in OFF) / GOAL:.0f}"
w = witch(MAIN["d"])
NUMS["w_livelits"] = str(w["on"]["livelits"])
NUMS["w_drawn"] = str(counts(w).get("drawn from the compiled run", 0))
fold = next((k for k in whys(w) if k.startswith("the slide's run compiled:")), "")
NUMS["w_folded"] = (re.search(r"(\d+) livelit", fold) or [None, "?"])[1]
NUMS["n_slides"] = str(len(MAIN["d"]["slides"]))
NUMS["n_problems"] = str(len(MAIN["d"]["problems"]))
NUMS["n_drawn_all"] = str(sum(counts(s).get("drawn from the compiled run", 0) for s in MAIN["d"]["slides"]))

body = open(os.path.join(HERE, "body.html")).read().replace("{{updated}}", updated)
FIGS = {"step": fig_step(), "edit": fig_edit()}
os.makedirs(os.path.join(HERE, "figs"), exist_ok=True)
for name, fig in FIGS.items():
    open(os.path.join(HERE, "figs", name + ".html"), "w").write(re.search(r"<svg.*?</svg>", fig, re.S).group(0) + "\n")
for k, v in FIGS.items():
    body = body.replace("{{fig_" + k + "}}", v)
body = body.replace("{{slides_table}}", slides_table()).replace("{{runs_table}}", runs_table()).replace("{{steps_table}}", steps_table())
for k, v in NUMS.items():
    body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{[a-z_0-9]+\}\}", body)
if left:
    sys.exit(f"unfilled: {left}")
TITLE = 'The Witch’s Run, Compiled, in the Page'
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE if 'TITLE' in dir() else 'The Slide’s Run, Compiled, in the App'}</title>\n"
        "<meta name=\"description\" content=\"The Witch slide's whole program, compiled to JavaScript by hazel-jit and run in the page at a slider's step: 1 to 7 ms in Firefox, against the worker's second and more.\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
print("wrote 049/index.html; updated", updated, NUMS)
