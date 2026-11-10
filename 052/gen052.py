#!/usr/bin/env python3
"""^report(52): What Mattered, Ranked. Matthew, 2026-11-10: "I'd like to have a new report that summarizes our work
over the last several days, with plots of the current status, and the more significant ingredients --- not every
single thing we tried in order. Rank them by how much they ended up helping. There's a feeling on the team that we
need to redo some of this work by hand, to avoid the tech debt of using machine generated code for all of it, in
small increments."

Writes 052/index.html from body.html, the runs of reports 050 and 051 (each build's jit.json and jit.log), and the
branch's history (git, in ~/hazel-694-jit). Numbers a figure or table shows are computed here from those runs;
the before-and-after numbers of each ingredient are the ones reports 045 to 051 measured, cited by build."""
import html, json, os, re, statistics as st, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = os.path.expanduser("~/hazel-694-jit")
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
EXTRA = """
  ol.outline > li { margin: 4px 0; } .muted { color: var(--muted); }
  table.vals { display: block; overflow-x: auto; max-width: 100%; border-collapse: collapse; margin: 0.6em 0 1em; font-size: 0.88em; }
  table.vals th, table.vals td { padding: 4px 8px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
  table.vals td.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; } table.vals th { font-weight: 600; }
  table.vals td.rank { font-weight: 700; text-align: right; }
  table.vals tr.group td { background: color-mix(in srgb, var(--accent) 8%, transparent); font-weight: 600; }
  figure.f { margin: 1.2em 0; } figure.f svg { max-width: 100%; }
  figcaption { color: var(--muted); font-size: 0.9em; margin-top: 6px; max-width: 80ch; }
  figcaption b.build { color: var(--ink); }
  code { overflow-wrap: anywhere; }
"""
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
GOAL = 1000 / 60
TEAL, GREY, SLATE, GREEN, AMBER, VIOLET, RED, BLUE = "#0d9488", "#9ca3af", "#64748b", "#15803d", "#b45309", "#7c3aed", "#b91c1c", "#2563eb"


def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True).stdout.strip()


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- the builds (numbered as in reports 050 and 051)
def builds_of(gen):
    s = open(gen).read()
    return [dict(n=int(m.group(1)), name=m.group(2).replace("\\'", "'").replace('\\"', '"'), commit=m.group(3), run=m.group(4))
            for m in re.finditer(r'\{"n": (\d+), "name": "((?:[^"\\]|\\.)*)", "commit": "([0-9a-f]+)", "run": "(\d+)"', s)]


BUILDS = {}
for b in builds_of(os.path.join(ROOT, "050", "gen050.py")) + builds_of(os.path.join(ROOT, "051", "gen051.py")):
    BUILDS.setdefault(b["n"], b)
BUILDS[38]["run2"] = "42817304210"   # build 38's second run, on a machine like build 37's (its first was slower throughout)
BUILDS[40] = dict(n=40, name="the outline mark timed", commit="f5b7a65cf2", run="42820611040")
BUILDS[41] = dict(n=41, name="the outline mark stands", commit="a02025f5dc", run="42822587416")
# builds 1 to 3 waited for the worker: their steps are report 050's (from report 046's runs), click to picture
PRE = {1: (4170, 6520), 2: (1850, 2380), 3: (1330, 1710)}


def run_dir(run):
    for rep in ("051", "050", "049", "046"):
        p = os.path.join(ROOT, rep, "data", "runs", run)
        if os.path.exists(os.path.join(p, "jit.json")):
            return p
    return None


TOP = ("view", "calculate", "hazel-jit: the run compiled", "worker message decoded", "update",
       "samples' values made terms", "outline, on its own")


def measure(run):
    p = run_dir(run)
    if not p:
        return None
    d = json.load(open(os.path.join(p, "jit.json")))
    w = next(s for s in d["slides"] if s.get("slide") == "Witch")
    pics, after = [], []
    for e in w["edits"]["on"]:
        pics.append(e["picture_changed_ms"])
        marks = e.get("marks", [])
        res = next((m["at"] for m in marks if m["what"] == "worker message handled" and m.get("kind") == "result"), None)
        if res is None:
            after.append(None)
            continue
        after.append(round(sum(m.get("ms", 0) for m in marks
                               if (m["what"] in TOP or m["what"].startswith("hazel-jit: the program compared"))
                               and e["picture_changed_ms"] <= m["at"] < res + 500)))
    log = open(os.path.join(p, "jit.log")).read()
    fps = re.findall(r"drag, compiled on: '\w+' for \d+ ms: (\d+) frames, ([\d.]+) fps", log)
    vpf = re.findall(r"timeline over the drag: view \d+ ms x\d+ \(([\d.]+) each\)", log)
    run_ms = re.findall(r"a slide's whole run: \d+, median ([\d.]+) ms", log)
    return dict(pics=pics, after=after, fps=float(fps[0][1]) if fps else None, view=float(vpf[0]) if vpf else None,
                slide_run=float(run_ms[0]) if run_ms else None, json=os.path.join(p, "jit.json"))


for n, b in BUILDS.items():
    b["m"] = measure(b.get("run2", b["run"]))

# ---------------------------------------------------------------- the ingredients, as reports 045 to 051 measured them
# kind A: what a user waits for (a step's picture, a drag's frame); kind B: the page's own work after the picture.
# lo, hi: the time it took off, ms, on the measure it changed, when it landed (builds as named).
ING = [
    dict(key="answer", kind="A", lo=2840, hi=4810, per="a step",
         name="Send the worker's answer without what the page does not read",
         what="The worker ran the whole program on the interpreter and sent back every probe sample with its environment, "
              "closures and all, and a trace, about 5 MB of terms; the picture waited for it. Two cuts (no function-holding "
              "values in the samples' environments, no trace), then no sharing between answers. Later the answer went "
              "without a stream the page dropped on arrival, and its first-order values as data (590 KB to 198 KB).",
         measured="A step's picture 4.17 to 6.52 s on build 1, 1.85 to 2.38 s on build 2, 1.33 to 1.71 s on build 3 "
                  "(report 046). The answer 590 KB to 198 KB on build 20; the worker's encode 72 to 107 ms to 21 to 29, "
                  "the page's decode 24 to 31 ms to 7 to 8.",
         today="The picture no longer waits for the worker. Its answer still comes 1.5 to 2.4 s after a step, and costs "
               "the page 7 to 10 ms to decode.",
         builds=[2, 3, 20], commits=["20a3067c18", "4747a4120d", "01a5e8ecb0", "66b999aae3", "f432751f99"],
         needs="nothing: the worker and its messages, on any branch"),
    dict(key="run", kind="A", lo=1090, hi=1500, per="a step",
         name="Compile the slide's whole run to JavaScript, each livelit's model a parameter",
         what="hazel-jit compiles the slide's elaborated program once into a JavaScript function whose parameters are "
              "the livelits' models. A slider's event calls it with the new model, and every livelit draws from its "
              "answers at the page's next redraw, before the worker has answered.",
         measured="A step's picture 1.33 to 1.71 s on build 3, 208 to 236 ms on build 5 (steps 2 to 4; report 049). "
                  "In Node, a slider's step 684 ms on the interpreter, 2.3 to 2.5 ms compiled (report 045).",
         today="It is why a step shows in about 20 ms: the run answers in 2 to 3 ms (5 to 12 for a step's first event).",
         builds=[4, 5, 18], commits=["RANGE:4747a4120d..6d71c427bf", "a51dc778dd", "f125a69a7b"],
         needs="the compiler (below), and livelits"),
    dict(key="paint", kind="A", lo=133, hi=171, per="a step",
         name="Draw first; make the edit after the paint",
         what="When the compiled run has answered a slider's event, the page draws at once and writes the new model "
              "into the program (the edit: update, statics, syntax and the whole view) only after the browser has "
              "painted, at the next animation frame.",
         measured="A step's picture 152 to 195 ms on build 11, 19 to 24 ms on build 12 (steps 2 to 4; report 051).",
         today="The edit still runs after the paint: 75 to 90 ms, the largest single piece of a step's work left. "
               "Ticket 721 takes on most of it.",
         builds=[12], commits=["b37d2e6df1"], needs="the compiled run"),
    dict(key="drag", kind="A", lo=80, hi=85, per="each frame of a drag",
         name="A drag redraws only what changed",
         what="Four cuts to a drag's frame: its input goes to the page as a request to draw again, not to the editor as "
              "an edit (cut A); only the livelits whose answers changed are drawn again (cut B); the projectors' data "
              "and finished views are kept while nothing they read changed (cut C); and each editor's decorations and "
              "probes' views are kept across frames.",
         measured="A 3-second drag of the Witch's neck slider: 9.8 fps on build 5, 22.5 on build 6 (cut A), 26.4 on "
                  "build 7, 48.4 on build 8, 57.6 on build 12: a frame from 102 ms to 17.4 (reports 050 and 051).",
         today="A drag runs at 55 to 58 fps, its view 5 to 7 ms a frame.",
         builds=[6, 7, 8, 12], commits=["9fca635226", "38d4e4d0f8", "bdecaec5d9", "61f3f01a15", "d9d63c13af"],
         needs="the compiled run, for the picture to follow the drag"),
    dict(key="views", kind="A", lo=84, hi=84, per="each render of the picture",
         name="Compile each livelit's view",
         what="A livelit's view, a Hazel function from its model to HTML, compiled by hazel-jit and drawn straight "
              "from its JavaScript, not stepped through by the interpreter.",
         measured="The Witch's picture view in the app, in Firefox: 87 ms a render on the interpreter, 3.0 ms compiled "
                  "(report 046). A Polygons render in Node, 14.1 ms to 0.38 (report 045).",
         today="In a drag, a livelit drawn from JS takes about 1 ms, against 4.6 ms with nothing compiled (builds 30 "
               "to 39).",
         builds=[], commits=["VIEWS"], needs="the compiler, and livelits"),
    dict(key="kept", kind="B", lo=190, hi=400, per="a step",
         name="Keep the livelits a change did not touch",
         what="A livelit's finished view is kept, keyed on what it reads (its own statics record, its own samples and "
              "those it looked up, compared by value) rather than on the whole statics map and the whole run. So after "
              "an edit only the edited livelit is drawn again, and after the worker's answer only those whose samples "
              "changed. The same for its shape, its applied definition and its wrapper, for the probes and the "
              "sidebar's problem list.",
         measured="The page's work after a step 0.43 to 0.60 s on build 13, 0.24 to 0.30 s on build 15 (machines alike; "
                  "report 051). After an answer 4 projectors drawn, not 56 (build 19); at the answer the projectors' "
                  "views 16 to 41 ms on build 26, 11 to 16 on build 31; after an edit the probes' views 4 to 13 ms on "
                  "build 35, 1 to 3 on build 37.",
         today="Of the 53 livelits, 51 keep their views at each answer and after each edit.",
         builds=[15, 19, 29, 30, 31, 32, 33, 34, 37, 38, 39],
         commits=["d35f2f2619", "a1b43cba46", "515813903a", "bd24b35aaa", "5fdb0d3004", "a3ba9f6474", "1d485cc0ad",
                  "3f8ccae8b6", "285968fd06", "1d53e66e27", "c1476f1244", "3e3118f380", "19ecb75694", "9a5a3e7a64"],
         needs="livelits"),
    dict(key="outline", kind="B", lo=128, hi=201, per="a step",
         name="Build the outline on its own, and only what changed",
         what="The sidebar's outline of the slide's program was built inside the page's view, after every edit and every "
              "message from the worker. It is now built on its own after the paint; it redraws the page only when it "
              "changed; it keys the run's test results by each test's status; and its search for rows that open no "
              "cell walks only the top-level tiles an edit changed.",
         measured="The views after each worker message 88 to 130 ms on build 12, 45 to 63 on build 13 (two messages a "
                  "step); after an answer the outline's 59 to 82 ms gone (build 19); the outline after an edit 42 to 53 "
                  "ms on build 21, 18 on build 36; its mark in the view 5 to 14 ms on build 40, 0 on build 41.",
         today="The outline after an edit, 18 to 42 ms, runs as a task of its own.",
         builds=[13, 19, 22, 24, 36, 41],
         commits=["bfbd88a1ae", "8bf44f23cf", "1dc99165ba", "854b40ee7d", "2b88bf18bf", "a1ab2e52d4", "62a517d8b4",
                  "a02025f5dc"],
         needs="the slide's outline (livelits branch)"),
    dict(key="once", kind="B", lo=125, hi=140, per="a step",
         name="Compile the run once; compare only what changed",
         what="The slide's run was compiled again after every step. Now it is kept while only models change: the new "
              "program is compared with the compiled one, models left out, and the comparison erases only the nodes a "
              "step changed.",
         measured="126 to 141 ms of compiling after each step on build 8; 29 to 51 ms of comparing on build 9; 1 ms on "
                  "build 17 (reports 050 and 051).",
         today="The comparison takes about 1 ms a step; the run is kept at every step.",
         builds=[9, 10, 17], commits=["7f5add1519", "3e51af567f", "c016370918", "b195b09088"],
         needs="the compiled run"),
    dict(key="autosave", kind="B", lo=77, hi=96, per="a step",
         name="Save without a redraw, printing only what changed",
         what="The autosave went through the page's update, so each save was followed by a calculate, a whole view and "
              "an outline. It now writes the model directly, and prints again only the top-level pieces a step changed.",
         measured="About 60 ms gone after each autosave (build 16); the autosave itself 38 to 67 ms on build 21, 21 to "
                  "31 on build 23.",
         today="The autosave takes 16 to 31 ms, about a second after a step.",
         builds=[16, 23], commits=["f4bcd64cf7", "263ecc3e84", "d68bd6400b"],
         needs="the slide's autosave (livelits branch)"),
    dict(key="probe", kind="B", lo=38, hi=85, per="each answer",
         name="Draw the picture's probe row without rewriting its value",
         what="The probe on the picture abbreviated its value by rewriting all of it first, and checked whether each "
              "sample was a value by running the evaluator's step rules over the whole value. It now abbreviates in "
              "one pass, and answers plain data by its shape.",
         measured="The probe row after each answer 44 to 91 ms on build 13, 8 to 21 on build 14; 15 to 35 ms on build "
                  "24, 3 to 6 on build 26.",
         today="The probe row takes 3 to 6 ms at each answer.",
         builds=[14, 26], commits=["e1bb06d115", "99542e86e3", "3615e5ebb6"], needs="probes (on dev)"),
]
for i in ING:
    i["mid"] = (i["lo"] + i["hi"]) / 2
RANKED = {k: sorted([i for i in ING if i["kind"] == k], key=lambda i: -i["mid"]) for k in ("A", "B")}
for k in ("A", "B"):
    for r, i in enumerate(RANKED[k], 1):
        i["label"] = f"{k}{r}"


# ---------------------------------------------------------------- each ingredient's size, from git
def numstat(spec):
    out = git("diff", "--numstat", spec[6:].split("..")[0], spec[6:].split("..")[1]) if spec.startswith("RANGE:") \
        else git("show", "--numstat", "--format=", spec)
    rows = []
    for line in out.splitlines():
        p = line.split("\t")
        if len(p) == 3 and p[0].isdigit():
            rows.append((int(p[0]), int(p[1]), p[2]))
    return rows


JIT_FILES = ("HazelJit.re", "HazelJitValue.re", "HazelJitRun.re", "HazelJitDOM.re")
VIEW_FILES = ("HazelJit.re", "HazelJitValue.re", "HazelJitRun.re", "HazelJitDOM.re", "LivelitProj.re", "HazelDOM.re",
              "web/Settings.re", "web/DeepLink.re")


def size_of(commits):
    if commits == ["VIEWS"]:
        # the compiler's first days (8c5cd80a29 to build 1): the views' wiring only; the measuring (AnswerParts,
        # the worker's marks, BenchMarks) is the ruler, counted apart
        rows = []
        for c in git("rev-list", "--reverse", "8c5cd80a29^..dfa3fcdffe").split():
            rows += [r for r in numstat(c) if r[2].endswith(VIEW_FILES) or r[2].startswith("test/")]
    else:
        rows = [r for c in commits for r in numstat(c)]
    src = [r for r in rows if r[2].startswith("src/") and not r[2].endswith(JIT_FILES)]
    jit = [r for r in rows if r[2].endswith(JIT_FILES)]
    test = [r for r in rows if r[2].startswith("test/")]
    return dict(src_add=sum(r[0] for r in src), src_del=sum(r[1] for r in src), src_files=len({r[2] for r in src}),
                jit_add=sum(r[0] for r in jit), test_add=sum(r[0] for r in test))


for i in ING:
    i["size"] = size_of(i["commits"])
JIT_LINES = {f: int(subprocess.run(["wc", "-l", os.path.join(REPO, p)], capture_output=True, text=True).stdout.split()[0])
             for f, p in [("HazelJit.re", "src/language/dynamics/HazelJit.re"),
                          ("HazelJitValue.re", "src/language/dynamics/HazelJitValue.re"),
                          ("HazelJitRun.re", "src/language/dynamics/HazelJitRun.re"),
                          ("HazelJitDOM.re", "src/haz3lcore/projectors/HazelJitDOM.re")]}
JIT_TEST = int(subprocess.run(["wc", "-l", os.path.join(REPO, "test/Test_HazelJit.re")], capture_output=True, text=True).stdout.split()[0])
BASE = git("merge-base", "a02025f5dc", "origin/integration/livelits-modular-editors")


def shortstat(path):
    out = git("diff", "--shortstat", BASE, "a02025f5dc", "--", *path)
    f = re.search(r"(\d+) files?", out); a = re.search(r"(\d+) insertion", out); d = re.search(r"(\d+) deletion", out)
    return (int(f.group(1)) if f else 0, int(a.group(1)) if a else 0, int(d.group(1)) if d else 0)


BR = dict(commits=int(git("rev-list", "--count", f"{BASE}..a02025f5dc")), src=shortstat(["src"]), test=shortstat(["test"]),
          scripts=shortstat(["scripts", ".github"]))
RULER = {f: int(subprocess.run(["wc", "-l", os.path.join(REPO, p)], capture_output=True, text=True).stdout.split()[0])
         for f, p in [("BenchMarks.re", "src/util/BenchMarks.re"), ("AnswerParts.re", "src/web/util/AnswerParts.re")]}
FIXUPS = ["96a5031217", "b195b09088", "99542e86e3", "8bf44f23cf", "d8c2bbb671"]
TIMERS_ONLY = [21, 25, 27, 28, 35, 40]


# ---------------------------------------------------------------- figures
def svg_fig(W, h, out, alt, caption):
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{esc(alt)}" '
            f'style="width:100%;height:auto;display:block">' + "".join(out) + f"</svg><figcaption>{caption}</figcaption></figure></div>")


def text(out, x, y, s, size=11, anchor="start", fill="var(--ink)", weight="400"):
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}">{esc(s)}</text>')


def fmt_ms(v):
    return f"{v / 1000:.2f} s" if v >= 1000 else f"{v:.0f} ms"


def rng(xs, f="{:.0f}"):
    lo, hi = f.format(min(xs)), f.format(max(xs))
    return lo if lo == hi else f"{lo} to {hi}"


NOW = BUILDS[38]          # its second run: the newest on a machine like build 37's (see the builds table)
NOWW = json.load(open(NOW["m"]["json"]))
NOW_STEP = next(s for s in NOWW["slides"] if s.get("slide") == "Witch")["edits"]["on"][1]


def fig_now():
    """one step on build 38, from the click: what runs, on the page's thread, and when"""
    e = NOW_STEP
    marks = e["marks"]
    pic = e["picture_changed_ms"]
    res = next(m["at"] for m in marks if m["what"] == "worker message handled" and m.get("kind") == "result")
    rows = [("the compiled run", TEAL), ("drawing the picture", GREEN), ("the edit, after the paint", AMBER),
            ("the outline, on its own", VIOLET), ("the autosave", SLATE), ("the worker's answer", BLUE)]
    blocks = {r: [] for r, _ in rows}
    calc_after = [m for m in marks if m["what"] == "calculate" and pic <= m["at"] < res - 100]
    for m in marks:
        w, at, ms = m["what"], m["at"], m.get("ms", 0)
        if w == "hazel-jit: the run" and at < pic:
            blocks["the compiled run"].append((at, ms, "run"))
        elif w == "view" and at < pic:
            blocks["drawing the picture"].append((at, ms, "view"))
        elif w == "update" and pic <= at < res - 100:
            blocks["the edit, after the paint"].append((at, ms, "update"))
        elif w == "statics" and pic <= at < res - 100:
            blocks["the edit, after the paint"].append((at, ms, "statics"))
        elif w == "syntax" and pic <= at < res - 100 and calc_after:
            blocks["the edit, after the paint"].append((at, ms, "syntax"))
        elif w == "view" and pic <= at < res - 100 and calc_after and at >= calc_after[0]["at"] and ms >= 10:
            blocks["the edit, after the paint"].append((at, ms, "view"))
        elif w == "outline, on its own" and at < res:
            blocks["the outline, on its own"].append((at, ms, "outline"))
        elif w == "autosave":
            blocks["the autosave"].append((at, ms, "autosave"))
        elif w in ("worker message decoded", "samples' values made terms") and at >= res - 60:
            blocks["the worker's answer"].append((at, ms, "decode" if w.startswith("worker") else "terms"))
        elif w in ("calculate", "view") and at >= res:
            blocks["the worker's answer"].append((at, ms, w))
    edit_end = max(a + ms for r in ("the edit, after the paint", "the outline, on its own") for a, ms, _ in blocks[r])
    w1 = (0, edit_end + 12)
    w2lo = min([a for a, _, _ in blocks["the autosave"]] + [a for a, _, _ in blocks["the worker's answer"]]) - 15
    w2 = (w2lo, max(a + ms for a, ms, _ in blocks["the worker's answer"]) + 12)
    W, LX, GAP = 900, 168, 28
    px = (W - LX - 16 - GAP) / ((w1[1] - w1[0]) + (w2[1] - w2[0]))

    def X(t):
        return LX + (t - w1[0]) * px if t <= w1[1] else LX + (w1[1] - w1[0]) * px + GAP + (t - w2[0]) * px
    top, rh = 66, 30
    H = top + rh * len(rows) + 52
    out = []
    text(out, 16, 18, "Build 38: one step of the Witch's neck slider, from the click, on the page's thread", 12.5, weight="700")
    text(out, 16, 34, f"the picture changes at {pic} ms; the worker's answer arrives at {res / 1000:.2f} s", 11, fill="var(--muted)")
    # frame grid in the first window
    t = 0.0
    while t <= w1[1]:
        out.append(f'<line x1="{X(t):.1f}" y1="{top - 4}" x2="{X(t):.1f}" y2="{top + rh * len(rows)}" stroke="var(--line)" stroke-width="0.6"/>')
        t += GOAL
    xb = LX + (w1[1] - w1[0]) * px + GAP / 2
    out.append(f'<line x1="{xb - 6:.1f}" y1="{top - 6}" x2="{xb + 2:.1f}" y2="{top + rh * len(rows) + 6}" stroke="var(--muted)" stroke-width="1.2"/>')
    out.append(f'<line x1="{xb - 2:.1f}" y1="{top - 6}" x2="{xb + 6:.1f}" y2="{top + rh * len(rows) + 6}" stroke="var(--muted)" stroke-width="1.2"/>')
    for k, (name, col) in enumerate(rows):
        y = top + k * rh
        text(out, LX - 8, y + rh / 2 + 4, name, 11, "end")
        for a, ms, lab in blocks[name]:
            x0, x1 = X(a), X(a + max(ms, 0.8))
            out.append(f'<rect x="{x0:.1f}" y="{y + 6}" width="{max(x1 - x0, 1.6):.1f}" height="{rh - 12}" rx="2" fill="{col}" opacity="0.85"/>')
            if x1 - x0 > 26:
                text(out, (x0 + x1) / 2, y + rh / 2 + 4, f"{lab} {ms:.0f}", 9.5, "middle", "#fff", "600")
    xp = X(pic)
    out.append(f'<line x1="{xp:.1f}" y1="{top - 8}" x2="{xp:.1f}" y2="{top + rh * len(rows) + 4}" stroke="{RED}" stroke-width="1.6"/>')
    text(out, xp + 4, top - 10, f"the picture changes, {pic} ms", 10.5, fill=RED, weight="600")
    yb = top + rh * len(rows) + 18
    for v in range(0, int(w1[1]) + 1, 50):
        text(out, X(v), yb, f"{v}", 9.5, "middle", "var(--muted)")
    v = (int(w2[0]) // 50 + 1) * 50
    while v <= w2[1]:
        text(out, X(v), yb, f"{v / 1000:.2f} s", 9.5, "middle", "var(--muted)")
        v += 50
    text(out, LX, yb + 18, "ms after the click; thin lines are 60 fps frames (16.7 ms); the break hides about a second in which the worker runs and the page is idle",
         10, fill="var(--muted)")
    total_after = sum(ms for r in rows[2:] for _, ms, _ in blocks[r[0]])
    cap = (f'<b class="build">Build 38</b> ({NOW["commit"]}, run {NOW["run2"]}; Firefox on GitHub\'s machines): the second of '
           f"the check's four steps, the neck slider from {NOW_STEP['from']} to {NOW_STEP['to']}. Each bar is one piece of "
           f"the page's work, timed on its own timeline; the page is idle between them. Before the picture: the compiled "
           f"run and two small draws. After it: the edit (update, statics, syntax and the view), the outline, the autosave, "
           f"and the worker's answer, {total_after:.0f} ms in all. The answer's view of 60 ms (about 17 fps, as if the "
           f"update were free) includes a pause that lands somewhere else at every step, most likely the browser "
           f"collecting the answer's garbage.")
    return svg_fig(W, H + 10, out, "A timeline of one slider step on build 38: the picture changes at 31 ms, then the edit, outline, autosave and the worker's answer", cap), blocks, pic, res


def fig_trend(key, title_, unit, floor, logy, caption, ylabel):
    pts = []
    for n in sorted(BUILDS):
        b = BUILDS[n]
        if n in PRE and key == "pics":
            pts.append((n, PRE[n][0], PRE[n][1], (PRE[n][0] + PRE[n][1]) / 2))
            continue
        m = b.get("m")
        if not m:
            continue
        if key == "pics":
            xs = [v for v in m["pics"][1:4] if v is not None]
        elif key == "after":
            # from build 5: build 4's steps back waited for the worker, so their pictures came with its answer
            xs = [v for v in m["after"][1:4] if v] if n >= 5 else []
        else:
            xs = [m["fps"]] if m["fps"] else []
        if xs:
            pts.append((n, min(xs), max(xs), st.median(xs)))
    W, H, L, R, T, B = 900, 300, 64, 16, 40, 44
    xs_ = [p[0] for p in pts]
    nlo, nhi = 0.5, max(xs_) + 0.5

    def X(n):
        return L + (n - nlo) / (nhi - nlo) * (W - L - R)
    import math
    if logy:
        ylo, yhi = logy

        def Y(v):
            return T + (math.log10(yhi) - math.log10(max(v, ylo))) / (math.log10(yhi) - math.log10(ylo)) * (H - T - B)
        ticks = [t for t in (10, 20, 50, 100, 200, 500, 1000, 2000, 5000) if ylo <= t <= yhi]
    else:
        ylo, yhi = 0, max(max(p[2] for p in pts) * 1.1, floor * 1.15 if floor else 0)

        def Y(v):
            return T + (yhi - v) / (yhi - ylo) * (H - T - B)
        step = 10 if yhi <= 80 else 100
        ticks = list(range(0, int(yhi) + 1, step))
    out = []
    text(out, 16, 18, title_, 12.5, weight="700")
    for t in ticks:
        out.append(f'<line x1="{L}" y1="{Y(t):.1f}" x2="{W - R}" y2="{Y(t):.1f}" stroke="var(--line)" stroke-width="1"/>')
        text(out, L - 6, Y(t) + 3.5, (f"{t / 1000:g} s" if t >= 1000 else f"{t:g}"), 10, "end", "var(--muted)")
    text(out, 14, T - 8, ylabel, 10, fill="var(--muted)")
    if floor:
        out.append(f'<line x1="{L}" y1="{Y(floor):.1f}" x2="{W - R}" y2="{Y(floor):.1f}" stroke="{RED}" stroke-width="1.4" stroke-dasharray="5 4"/>')
        if unit == "fps":
            text(out, W - R - 4, Y(floor) - 5, "60 fps", 10.5, "end", RED, "600")
        else:
            text(out, L + 6, Y(floor) + 13, "16.7 ms, one 60 fps frame", 10.5, "start", RED, "600")
    for n, lo, hi, med in pts:
        x = X(n)
        out.append(f'<line x1="{x:.1f}" y1="{Y(lo):.1f}" x2="{x:.1f}" y2="{Y(hi):.1f}" stroke="{TEAL}" stroke-width="2" opacity="0.55"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{Y(med):.1f}" r="3.2" fill="{TEAL if n not in PRE else GREY}"/>')
    for n in range(1, int(nhi) + 1):
        if n in (1, 5, 10, 15, 20, 25, 30, 35, 40) or n == max(xs_):
            text(out, X(n), H - B + 16, str(n), 10, "middle", "var(--muted)")
    text(out, (L + W - R) / 2, H - 8, "build", 10.5, "middle", "var(--muted)")
    for n, lab in MILESTONES.get(key, []):
        p = next((p for p in pts if p[0] == n), None)
        if not p:
            continue
        x, y = X(n), Y(p[3])
        text(out, x + 6, y - 7, lab, 10, fill="var(--ink)")
    return svg_fig(W, H, out, title_, caption), pts


MILESTONES = {
    "pics": [(2, "the answer cut"), (5, "the run compiled"), (12, "the edit after the paint")],
    "fps": [(6, "cut A"), (8, "cut C"), (31, "a regression, fixed by build 32")],
    "after": [(15, "livelits kept"), (20, "the answer as data"), (37, "probes kept")],
}


def fig_ranked():
    import math
    W, L, R = 900, 330, 120
    rowh, top = 26, 52
    rows = [("A", None)] + [("A", i) for i in RANKED["A"]] + [("B", None)] + [("B", i) for i in RANKED["B"]]
    H = top + rowh * len(rows) + 36
    lo_, hi_ = 10, 10000

    def X(v):
        return L + (math.log10(v) - math.log10(lo_)) / (math.log10(hi_) - math.log10(lo_)) * (W - L - R)
    out = []
    text(out, 16, 18, "The ingredients, ranked by the time each took off when it landed", 12.5, weight="700")
    text(out, 16, 34, "log scale; a bar runs from the low to the high end of what was measured, a dot at the middle", 11, fill="var(--muted)")
    for t in (10, 30, 100, 300, 1000, 3000, 10000):
        out.append(f'<line x1="{X(t):.1f}" y1="{top - 6}" x2="{X(t):.1f}" y2="{top + rowh * len(rows)}" stroke="var(--line)" stroke-width="1"/>')
        text(out, X(t), top + rowh * len(rows) + 14, (f"{t / 1000:g} s" if t >= 1000 else f"{t} ms"), 10, "middle", "var(--muted)")
    k = 0
    rank = {"A": 0, "B": 0}
    for kind, i in rows:
        y = top + k * rowh
        if i is None:
            text(out, 16, y + 17, "What you wait for: a step's picture, a drag's frame" if kind == "A"
                 else "The page's own work after the picture: what can make a frame late", 11.5, weight="700",
                 fill=TEAL if kind == "A" else AMBER)
        else:
            rank[kind] += 1
            col = TEAL if kind == "A" else AMBER
            text(out, 16, y + 17, f"{i['label']}. {i['name']}", 10.5)
            x0, x1 = X(max(i["lo"], lo_)), X(i["hi"])
            out.append(f'<rect x="{x0:.1f}" y="{y + 8}" width="{max(x1 - x0, 3):.1f}" height="11" rx="3" fill="{col}" opacity="0.35"/>')
            out.append(f'<circle cx="{X(i["mid"]):.1f}" cy="{y + 13.5}" r="4" fill="{col}"/>')
            lab = (f"{fmt_ms(i['lo'])} to {fmt_ms(i['hi'])}" if i["lo"] != i["hi"] else fmt_ms(i["lo"])) + " " + i["per"]
            text(out, x1 + 6, y + 17, lab, 9.5, fill="var(--muted)")
        k += 1
    cap = ("Each ingredient's gain as reports 045 to 051 measured it when it landed, in Firefox on GitHub's machines "
           "unless the table says Node, on the builds the table names. Teal: the time a user waits for, a slider "
           "step's picture or a drag's frame. Amber: the page's work after the picture is up, which delays the next frame "
           "when it runs long. The two are not added together, and a gain measured in one place can shrink once another "
           "lands: the first, the worker's answer, no longer stands between a step and its picture.")
    return svg_fig(W, H, out, "Ranked bars: the ten ingredients by time saved, in two groups", cap)


FIG_NOW, NOW_BLOCKS, NOW_PIC, NOW_RES = fig_now()
FIG_STEPS, P_STEPS = fig_trend("pics", "A slider's step, build by build: click to picture (steps 2 to 4)", "ms", GOAL, (10, 8000),
                               '<b class="build">Builds 1 to 41</b> of <code>trial/694-view-jit</code> (reports 050 and 051), one '
                               "run each, Firefox on GitHub's machines: the Witch's steps 2 to 4 (the first step of a slide pays "
                               "first-call costs), a dot at the median, a line over the range. Builds 1 to 3 (grey) waited for the "
                               "worker's answer; their ranges are over all four steps. Machines differ by up to a third from run "
                               "to run, so neighbouring builds' small differences are noise.",
                               "ms, log scale")
FIG_DRAGS, P_DRAGS = fig_trend("fps", "A drag, build by build: frames a second, compiled", "fps", 60, None,
                               '<b class="build">Builds 5 to 41</b>: a 3-second drag of the Witch\'s neck slider in the Firefox '
                               "check, one run each. Builds 31 and 33 slowed the drag (a shape check compared equal copies, then "
                               "model values, at every frame); builds 32 and 34 fixed them (report 051).",
                               "frames a second")
FIG_AFTER, P_AFTER = fig_trend("after", "The page's own work after a step's picture, build by build", "ms", None, None,
                               '<b class="build">Builds 5 to 41</b>: the page\'s top-level work from the picture to half a second '
                               "after the worker's answer (the edit, the outline, the comparison, the answer's decode and "
                               "view), steps 2 to 4. Machines differ: build 13's run read 20 to 40% slow throughout, build 38's "
                               "first run too (its second, on a machine like build 37's, is plotted).",
                               "ms")
FIG_RANKED = fig_ranked()

# ---------------------------------------------------------------- tables


def builds_cell(ns):
    return ", ".join(str(n) for n in ns) if ns else "before build 1"


def ranked_table():
    rows = ['<tr><th>#</th><th>Ingredient</th><th>Measured</th><th>What it does today</th><th>Builds</th>'
            '<th>Code (src, lines added / removed, files)</th><th>Tests</th></tr>']
    for kind, label in (("A", "What you wait for"), ("B", "The page's own work after the picture")):
        rows.append(f'<tr class="group"><td colspan="7">{label}</td></tr>')
        for r, i in enumerate(RANKED[kind], 1):
            s = i["size"]
            code = f'+{s["src_add"]:,} / −{s["src_del"]:,} in {s["src_files"]}'
            if s["jit_add"]:
                code += f'; and +{s["jit_add"]:,} in hazel-jit\'s own modules'
            rows.append(f'<tr id="ing-{i["key"]}"><td class="rank">{i["label"]}</td><td><b>{esc(i["name"])}</b>. {esc(i["what"])}</td>'
                        f'<td>{esc(i["measured"])} <b>{esc((fmt_ms(i["lo"]) + " to " + fmt_ms(i["hi"])) if i["lo"] != i["hi"] else fmt_ms(i["lo"]))} off {esc(i["per"])}.</b></td>'
                        f'<td>{esc(i["today"])}</td><td>{builds_cell(i["builds"])}</td><td class="n">{code}</td>'
                        f'<td class="n">{("+" + format(s["test_add"], ",")) if s["test_add"] else "none"}</td></tr>')
    return '<table class="vals ranked">' + "".join(rows) + "</table>"


I = {i["key"]: i for i in ING}


def n_(k):
    return f'{I[k]["size"]["src_add"]:,}'


REDO = [
    ("0", "The ruler", "The Firefox check that drives the Witch slide and times each step and drag (<code>scripts/jit_slides.py</code>, "
     "<code>.github/workflows/jit.yml</code>), the page's timeline of marks (<code>Util.BenchMarks</code>) and the worker's answer "
     "weighed by part (<code>AnswerParts</code>). It changes nothing a user sees; with it, each later increment is measured the way "
     "this report's builds were.",
     f'{BR["scripts"][1]:,} in scripts and CI; {RULER["BenchMarks.re"]:,} and {RULER["AnswerParts.re"]:,} in the two modules', "nothing"),
    ("1", "The worker's answer, smaller", f"Ingredient {I['answer']['label']}. The worker and its messages only; it helps <code>dev</code> as much as "
     "the livelits branch.", n_("answer"), "nothing"),
    ("2", "Page work every edit pays", f"The ingredients that need no hazel-jit: the outline on its own ({I['outline']['label']}), the autosave "
     f"without a redraw ({I['autosave']['label']}), the probe row ({I['probe']['label']}). Each its own small PR.",
     f'{n_("outline")}, {n_("autosave")} and {n_("probe")}', "the outline and autosave: the livelits branch; the probe row: dev"),
    ("3", "Livelits kept", f"Ingredient {I['kept']['label']}: a livelit's view, shape and applied definition keyed on what it reads. Several small "
     "PRs, one cache each, each with a test that the cache gives the same view.", n_("kept"), "livelits"),
    ("4", "The compiler", f"hazel-jit itself: {sum(JIT_LINES.values()):,} lines in four modules (the values' bridge, the "
     f"compiler, the DOM, the run), with {JIT_TEST:,} lines of tests that each compiled program agrees with the interpreter. "
     "The largest piece, and the one that most needs review by hand; it can land a module at a time.",
     f"{sum(JIT_LINES.values()):,}, and {JIT_TEST:,} of tests", "nothing"),
    ("5", "Compiled views", f"Ingredient {I['views']['label']}: livelit views drawn from compiled JS.", n_("views") + " outside the compiler", "4, livelits"),
    ("6", "The run compiled in the page", f"Ingredients {I['run']['label']} and {I['once']['label']}: the slide's run, compiled once, called at a slider's event, "
     "kept while only models change.", f'{n_("run")} and {n_("once")}', "4, 5"),
    ("7", "Draw first, edit after the paint", f"Ingredient {I['paint']['label']}.", n_("paint"), "6"),
    ("8", "The drag fast path", f"Ingredient {I['drag']['label']}: four cuts, each its own PR.", n_("drag"), "6"),
]


def redo_table():
    rows = ['<tr><th>Order</th><th>Increment</th><th>What it holds</th><th>Size (lines)</th><th>Needs first</th></tr>']
    for o, name, what, size, needs in REDO:
        rows.append(f"<tr><td class=\"rank\">{o}</td><td><b>{name}</b></td><td>{what}</td><td class=\"n\">{size}</td><td>{needs}</td></tr>")
    return '<table class="vals">' + "".join(rows) + "</table>"


def builds_table():
    cited = sorted({n for i in ING for n in i["builds"]} | {1, 3, 5, 8, 11, 12, 13, 38, 41})
    rows = ["<tr><th>Build</th><th>Commit</th><th>Firefox run</th><th>A step: click to picture, steps 2 to 4</th>"
            "<th>A drag</th><th>The page's work after the picture</th></tr>"]
    for n in cited:
        b = BUILDS[n]
        m = b.get("m")
        if n in PRE:
            pic = f"{PRE[n][0] / 1000:.2f} to {PRE[n][1] / 1000:.2f} s (all steps)"
            drag = after = "not measured"
        elif m:
            pic = rng([v for v in m["pics"][1:4]]) + " ms"
            drag = f'{m["fps"]:.1f} fps' if m["fps"] else "not measured"
            a = [v for v in m["after"][1:4] if v is not None]
            after = (rng(a) + " ms") if a else "not measured"
        else:
            pic = drag = after = "not measured"
        run = b.get("run2", b["run"])
        rows.append(f'<tr><td>{n} · {esc(b["name"])}</td><td>{b["commit"]}</td><td>{run}</td><td class="n">{pic}</td>'
                    f'<td class="n">{drag}</td><td class="n">{after}</td></tr>')
    return '<table class="vals">' + "".join(rows) + "</table>"


# ---------------------------------------------------------------- the numbers the prose quotes
b38, b41 = BUILDS[38]["m"], BUILDS[41]["m"]
blk = {r: sum(ms for _, ms, _ in v) for r, v in NOW_BLOCKS.items()}
NUMS = {
    "updated": updated,
    "now_pic": rng(b38["pics"][1:4]),
    "now_first": f'{b38["pics"][0]:.0f}',
    "now_fps": f'{b38["fps"]:.1f}',
    "now_view": f'{b38["view"]:.1f}',
    "now_after": rng([v for v in b38["after"][1:4] if v is not None]),
    "b41_pic": rng(b41["pics"][1:4]),
    "b41_fps": f'{b41["fps"]:.1f}',
    "b41_after": rng([v for v in b41["after"][1:4] if v is not None]),
    "edit_ms": f'{blk["the edit, after the paint"]:.0f}',
    "outline_ms": f'{blk["the outline, on its own"]:.0f}',
    "answer_ms": f'{blk["the worker\'s answer"]:.0f}',
    "res_s": f"{NOW_RES / 1000:.2f}",
    "n_commits": f'{BR["commits"]}',
    "src_add": f'{BR["src"][1]:,}', "src_del": f'{BR["src"][2]:,}', "src_files": f'{BR["src"][0]}',
    "test_add": f'{BR["test"][1]:,}', "scripts_add": f'{BR["scripts"][1]:,}',
    "jit_lines": f"{sum(JIT_LINES.values()):,}", "jit_test": f"{JIT_TEST:,}",
    "n_fixups": str(len(FIXUPS)),
    "untested": str(sum(1 for i in ING if not i["size"]["test_add"])),
    "a1": RANKED["A"][0]["name"], "b1": RANKED["B"][0]["name"],
}
FIGS = {"fig_now": FIG_NOW, "fig_steps": FIG_STEPS, "fig_drags": FIG_DRAGS, "fig_after": FIG_AFTER,
        "fig_ranked": FIG_RANKED, "tab_ranked": ranked_table(), "tab_redo": redo_table(), "tab_builds": builds_table()}
body = open(os.path.join(HERE, "body.html")).read()
for k, v in {**NUMS, **FIGS}.items():
    body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{(\w+)\}\}", body)
assert not left, left
TITLE = "What Mattered, Ranked"
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n"
        "<meta name=\"description\" content=\"Five days of making a livelit's slider in Hazel fast, summarized: where a slider step and a drag stand now, the ten changes that mattered ranked by how much each helped, and an order for redoing them by hand in small increments.\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
json.dump({"builds": {n: {k: v for k, v in b.items() if k != "m"} | ({"measured": {k: v for k, v in b["m"].items() if k != "json"}} if b.get("m") else {})
                      for n, b in sorted(BUILDS.items())},
           "pre_builds_step_ms": PRE,
           "ingredients": [{k: v for k, v in i.items()} for i in ING],
           "now_step": {"build": 38, "run": NOW["run2"], "picture_ms": NOW_PIC, "answer_ms": NOW_RES,
                        "blocks": {r: [{"at": a, "ms": ms, "what": w} for a, ms, w in v] for r, v in NOW_BLOCKS.items()}},
           "branch": {"base": BASE, "head": "a02025f5dc", **{k: v for k, v in BR.items()}, "fixups": FIXUPS,
                      "timers_only_builds": TIMERS_ONLY, "jit_modules_lines": JIT_LINES, "jit_test_lines": JIT_TEST}},
          open(os.path.join(HERE, "data", "numbers.json"), "w"), indent=1, default=str)
print("wrote 052/index.html;", updated, {k: NUMS[k] for k in ("now_pic", "now_fps", "now_after", "edit_ms", "n_commits")})
