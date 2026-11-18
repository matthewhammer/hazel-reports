#!/usr/bin/env python3
"""^report(57): What the Livelits PR Compiles. Matthew Hammer, 2026-11-18: "to what extent is
https://github.com/hazelgrove/hazel/pull/2819 using hazel-jit, for livelit views only? for anything else?", then "please write
a new report with what you just told me, and sections with more details for each point. I want to talk to Cyrus today about
what features we are using for responsive livelit performance, and think about how to merge into dev. Another mergeathon
tomorrow."

Writes 057/index.html from body.html and the tables below, and 057/data/numbers.json. The ingredients and the increments are
report 052's (its gen052.py and index.html), with whether #2819's head holds each: an ingredient's builds are in #2819 when
each build's commit is an ancestor of c419e01559 (checked with git merge-base --is-ancestor on 2026-11-18)."""
import html, json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
EXTRA = """
  ol.outline > li { margin: 4px 0; } .muted { color: var(--muted); }
  table.vals { display: block; overflow-x: auto; max-width: 100%; border-collapse: collapse; margin: 0.6em 0 1em; font-size: 0.88em; }
  table.vals th, table.vals td { padding: 5px 8px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
  table.vals td.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; } table.vals th { font-weight: 600; }
  table.vals td:first-child { min-width: 3ch; }
  code { overflow-wrap: anywhere; }
  .yes { color: #15803d; font-weight: 600; } .no { color: #b91c1c; font-weight: 600; } .part { color: #b45309; font-weight: 600; }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .yes { color: #4ade80; } :root:not([data-theme="light"]) .no { color: #f87171; } :root:not([data-theme="light"]) .part { color: #fbbf24; } }
  :root[data-theme="dark"] .yes { color: #4ade80; } :root[data-theme="dark"] .no { color: #f87171; } :root[data-theme="dark"] .part { color: #fbbf24; }
"""
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
esc = lambda s: html.escape(s, quote=True)

PR = dict(n=2819, head="c419e01559", date="2026-11-09 10:11 MST", branch="livelits-x-jit", base="dev", ahead_of_dev=1680, behind_dev=18,
          behind_prototype=123, prototype="55e4757a4b")

# the builds quoted (the numbering of reports 050 to 056)
BUILDS = [
    ("12", "d9d63c13af", "2026-11-09", "the prototype when #2819 was cut: a drag's frames reuse each editor's decorations and probes' views; #2819's head is this and two commits (samples as data turned off, a formatting pass)"),
    ("38", "19ecb75694", "2026-11-10", "report 052's measurements: a step's picture 20 to 31 ms after the click, a drag 55.7 fps"),
    ("49", "0e56bdbd0a", "2026-11-17", "report 054's: the meeting's changes merged, all of CI green"),
    ("50", "55e4757a4b", "2026-11-18", "today's prototype, trial/694-view-jit (hazelgrove/hazel#2817): build 49 and the slides' builtins"),
]

# report 052's ten ingredients: id, name, hazel-jit's (yes, rides on it, or no), the gain it measured when it landed, and in #2819
RANKED = [
    ("A1", "Send the worker's answer without what the page does not read", "no", "2.84 to 4.81 s off a step (builds 2, 3); the answer 590 KB to 198 KB (build 20)", "part", "builds 2 and 3, not 20"),
    ("A2", "Compile the slide's whole run, each livelit's model a parameter", "yes", "1.09 to 1.50 s off a step (builds 4, 5): a step's picture 1.33 to 1.71 s, then 208 to 236 ms", "yes", "builds 4 and 5; not 18 (the first step like the others)"),
    ("A3", "Draw first; make the edit after the paint", "rides", "133 to 171 ms off a step (build 12): 152 to 195 ms, then 19 to 24", "yes", "build 12"),
    ("A4", "Compile each livelit's view", "yes", "84 ms off each render of the Witch's picture: 87 ms to 3.0", "yes", "before build 1"),
    ("A5", "A drag redraws only what changed", "rides", "80 to 85 ms off each frame of a drag: 9.8 fps (build 5) to 57.6 (build 12)", "yes", "builds 6, 7, 8 and 12"),
    ("B1", "Keep the livelits a change did not touch", "no", "190 to 400 ms off the page's work after a step (builds 15 to 39)", "no", "builds 15 to 39"),
    ("B2", "Build the outline on its own, and only what changed", "no", "128 to 201 ms off a step (builds 13 to 41)", "no", "builds 13 to 41"),
    ("B3", "Compile the run once; compare only what changed", "yes", "125 to 140 ms off a step: compiling again 126 to 141 ms (build 8), comparing 1 ms (build 17)", "part", "builds 9 and 10, not 17"),
    ("B4", "Save without a redraw, printing only what changed", "no", "77 to 96 ms off a step (builds 16, 23)", "no", "builds 16 and 23"),
    ("B5", "Draw the picture's probe row without rewriting its value", "no", "38 to 85 ms off each answer (builds 14, 26)", "no", "builds 14 and 26"),
]
JIT = {"yes": '<span class="yes">hazel-jit</span>', "rides": '<span class="part">needs the compiled run</span>', "no": "no compiler"}
HAS = {"yes": '<span class="yes">yes</span>', "part": '<span class="part">partly</span>', "no": '<span class="no">no</span>'}

# report 052's nine increments, with what has happened since and what each needs first
REDO = [
    ("0", "The ruler", "The Firefox check that drives the slides and times each step and drag, the page's timeline of marks, the worker's answer weighed by part. Nothing a user sees.", "nothing", "On the prototype; on #2819 as it was on 11-09."),
    ("1", "The worker's answer, smaller", "Ingredient A1: the worker and its messages only. Helps dev as much as livelits.", "nothing", "On the prototype; #2819 has its first two parts."),
    ("2", "Page work every edit pays", "B2, B4, B5: the outline on its own, the autosave without a redraw, the probe row. Each its own small PR.", "the outline and autosave: livelits; the probe row: dev", "On the prototype only."),
    ("3", "Livelits kept", "B1: a livelit's view, shape and applied definition kept, keyed on what it reads; one cache a PR, each with a test that it gives the same view.", "livelits", "On the prototype only."),
    ("4", "The compiler", "hazel-jit itself, a module at a time, and now its correctness (report 054): exact Int and Nat, SInt at 32 bits, invalid operations stopping, the rules for holes, type holes and type errors, and the consistency check in CI. Nothing a user sees.", "nothing", "On the prototype, build 50; its CI checks 313 evaluator programs and 129 slides both ways."),
    ("5", "Compiled views", "A4, with the step budget (ticket 763), since it runs compiled code on the page's thread.", "4, livelits", "#2819 has the views, without the budget; the prototype has both."),
    ("6", "The run compiled in the page", "A2 and B3: the slide's run compiled once, called at a slider's event, kept while only models change.", "4, 5", "#2819 has it as of 11-09; the prototype has it whole."),
    ("7", "Draw first, edit after the paint", "A3.", "6", "In both."),
    ("8", "The drag fast path", "A5: four changes, each its own PR.", "6", "In both."),
]


def builds_table():
    rows = ["<tr><th>Build</th><th>Commit</th><th>Date</th><th>What it is</th></tr>"]
    for b, c, d, w in BUILDS:
        rows.append(f"<tr><td><b>{b}</b></td><td><code>{c}</code></td><td>{d}</td><td>{esc(w)}</td></tr>")
    return '<table class="vals">' + "".join(rows) + "</table>"


def ranked_table():
    rows = ["<tr><th>#</th><th>Change</th><th>Compiler?</th><th>Measured when it landed (report 052)</th><th>In #2819</th></tr>"]
    for k, name, j, gain, has, which in RANKED:
        if k in ("A1", "B1"):
            rows.append(f'<tr><td colspan="5"><b>{"What a user waits for: a step&#x27;s picture, a drag&#x27;s frame" if k == "A1" else "The page&#x27;s work after the picture, which can make the next frame late"}</b></td></tr>')
        rows.append(f"<tr><td>{k}</td><td>{esc(name)}</td><td>{JIT[j]}</td><td>{esc(gain)}</td><td>{HAS[has]} <span class=\"muted\">({esc(which)})</span></td></tr>")
    return '<table class="vals">' + "".join(rows) + "</table>"


def redo_table():
    rows = ["<tr><th>Order</th><th>Increment</th><th>What it holds</th><th>Needs first</th><th>Where it is now</th></tr>"]
    for o, name, holds, needs, now in REDO:
        rows.append(f"<tr><td class=\"n\">{o}</td><td><b>{esc(name)}</b></td><td>{esc(holds)}</td><td>{esc(needs)}</td><td>{esc(now)}</td></tr>")
    return '<table class="vals">' + "".join(rows) + "</table>"


FIGS = {"updated": updated, "tab_builds": builds_table(), "tab_ranked": ranked_table(), "tab_redo": redo_table()}
body = open(os.path.join(HERE, "body.html")).read()
for k, v in FIGS.items():
    body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{(\w+)\}\}", body)
assert not left, left
TITLE = "What the Livelits PR Compiles"
DESC = ("hazelgrove/hazel#2819 uses hazel-jit for livelits only: their views, their updates, and each slide's whole run, to draw them sooner. "
        "What each use does, what makes livelits responsive, and how it reaches dev.")
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{esc(DESC)}\">\n<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
json.dump({"pr": PR, "builds": [dict(build=b, commit=c, date=d, what=w) for b, c, d, w in BUILDS],
           "ingredients": [dict(id=k, name=n, compiler=j, gain=g, in_2819=h, builds=w) for k, n, j, g, h, w in RANKED],
           "increments": [dict(order=o, name=n, holds=h, needs=ne, now=nw) for o, n, h, ne, nw in REDO],
           "today_build_50": {"run": 44319161252, "drag_on": {"fps": 54.3, "view_ms_frame": 6.5, "longest_ms": 34.2},
                              "drag_off": {"fps": 42.0, "view_ms_frame": 15.4, "longest_ms": 132.8},
                              "step_first_redraw_ms": [89, 30, 28, 27], "jit_run_ms": [11, 11, 5, 5]}},
          open(os.path.join(HERE, "data", "numbers.json"), "w"), indent=1)
print("wrote 057/index.html;", updated)
