#!/usr/bin/env python3
"""^report(51): Hazel-JIT Status Report. Matthew, 2026-11-09: "I'd also like to prepare a report for my colleagues to
read (or have their agents read). Title: Hazel-JIT Status Report: expected gains (speedup of compiled versus
interpreted), and expected costs (time to compile on average); how to use hazel-jit today in their own PRs, if they
want more speed; extra features so far (what other modifications have we done since establishing the initial jit
implementation?); limitations, and plans for next steps (ongoing now)." And: "publish the status report as WIP
whenever you have a draft."

Writes 051/index.html from body.html, report 050's runs and figures, the branch's history (git, in ~/hazel-694-jit)
and today's runs in data/runs/ (when there)."""
import html, json, math, os, re, statistics as st, subprocess

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
  table.next td:nth-child(2) { min-width: 30ch; } table.next td:nth-child(3) { min-width: 26ch; } table.next td:nth-child(4) { min-width: 16ch; }
  table.vals tr.now td { background: color-mix(in srgb, var(--accent) 8%, transparent); }
  figure.f { margin: 1.2em 0; } figure.f svg { max-width: 100%; }
  figcaption { color: var(--muted); font-size: 0.9em; margin-top: 6px; max-width: 80ch; }
  figcaption b.build { color: var(--ink); }
  .try { border: 2px solid var(--accent); border-radius: 8px; padding: 10px 14px; margin: 1em 0; }
  .try a { font-weight: 600; }
  code { overflow-wrap: anywhere; }
"""
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
GOAL = 1000 / 60
TEAL, GREY, SLATE, GREEN, AMBER, VIOLET = "#0d9488", "#9ca3af", "#64748b", "#15803d", "#b45309", "#7c3aed"
B8 = "61f3f01a15"
B8_RUN = os.path.join(ROOT, "050", "data", "runs", "42566328043", "jit.json")


def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True).stdout.strip()


def svg_fig(W, h, out, alt, caption):
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{html.escape(alt)}" '
            f'style="width:100%;height:auto;display:block">' + "".join(out) + f"</svg><figcaption>{caption}</figcaption></figure></div>")


def title(out, text):
    out.append(f'<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">{html.escape(text)}</text>')


def log_axis(out, xof, y0, y1, ticks):
    for v, label in ticks:
        x = xof(v)
        out.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y1}" stroke="var(--line)" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{y1 + 14}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{label}</text>')


def kept_fig(nnn, name, caption):
    fig = open(os.path.join(ROOT, nnn, "figs", name + ".html")).read().strip()
    return f'<div class="figrow"><figure class="f wide">{fig}<figcaption>{caption}</figcaption></figure></div>'


# --- build 8 (report 050's latest build): each view the page drew, timed both ways in the page ---
b8 = json.load(open(B8_RUN))
w8 = next(s for s in b8["slides"] if s["slide"] == "Witch")
bench = [(k, v["interpreted"]["median"], v["compiled"]["median"]) for k, v in w8["bench"].items()
         if v.get("compiled", {}).get("said") == "compiled" and v.get("interpreted", {}).get("said") == "on the interpreter"]
pic = [b for b in bench if b[0].startswith("Drawing.picture")]
polys = [b for b in bench if b[0].startswith("Drawing.polygons")]
LOADS = [(s["slide"], s["on"]["livelits"], s["on"]["load_s"], s["off"]["load_s"]) for s in b8["slides"]]

# (label, interpreter ms (lo, hi), compiled ms (lo, hi), where: a build or "not a build")
PAIRS = [
    ("A recursive sum of 1,000 numbers", (47.9, 47.9), (0.042, 0.042), "Node, report 045"),
    ("The Petri net rule, four events", (7.19, 7.19), (0.011, 0.011), "Node, report 045"),
    ("The Witch's whole run", (502, 529), (4.2, 5.0), "Node, report 045"),
    ("A Polygons render, warm, with its trip", (13.7, 13.7), (0.34, 0.34), "Node, report 045"),
    ("A Polygons render, its first 30 calls", (13.7, 13.7), (1.03, 1.03), "Node, report 045"),
    ("The Witch's polygon editors' views, drawn", (min(b[1] for b in polys), max(b[1] for b in polys)),
     (min(b[2] for b in polys), max(b[2] for b in polys)), "Firefox, build 8"),
    ("The Witch's picture view, drawn", (pic[0][1], pic[0][1]), (pic[0][2], pic[0][2]), "Firefox, build 8"),
]
mid = lambda ab: (ab[0] * ab[1]) ** 0.5
RATIOS = [mid(i) / mid(c) for _, i, c, _ in PAIRS]


def fig_gains():
    W, left, right = 940, 360, 20
    lo, hi = math.log10(0.005), math.log10(2000)
    xof = lambda ms: left + (math.log10(ms) - lo) / (hi - lo) * (W - left - right)
    out = []
    title(out, "The same Hazel code on Hazel's interpreter (grey) and as hazel-jit's JavaScript (teal); a log scale")
    y = 40
    gx = xof(GOAL)
    out.append(f'<line x1="{gx:.1f}" y1="32" x2="{gx:.1f}" y2="{40 + 32 * len(PAIRS)}" stroke="{GREEN}" stroke-width="2.5"/>')
    for (label, (ia, ib), (ca, cb), where), x in zip(PAIRS, RATIOS):
        out.append(f'<text x="{left - 10}" y="{y + 9}" font-size="11.5" text-anchor="end" fill="var(--ink)">{html.escape(label)}</text>')
        out.append(f'<text x="{left - 10}" y="{y + 21}" font-size="10" text-anchor="end" fill="var(--muted)">{html.escape(where)}</text>')
        xi, xc = xof(mid((ia, ib))), xof(mid((ca, cb)))
        out.append(f'<line x1="{xc:.1f}" y1="{y + 9}" x2="{xi:.1f}" y2="{y + 9}" stroke="var(--line)" stroke-width="3"/>')
        for (a, b), col in (((ia, ib), GREY), ((ca, cb), TEAL)):
            out.append(f'<rect x="{xof(a) - 4:.1f}" y="{y + 3}" width="{max(8, xof(b) - xof(a) + 8):.1f}" height="12" rx="6" fill="{col}">'
                       f'<title>{html.escape(label)}: {a:g} to {b:g} ms</title></rect>')
        lab = f"about {x:,.0f} times"
        halo = 'stroke="var(--paper)" stroke-width="4" paint-order="stroke"'
        xe = xof(ib) + 8
        if xe + 6 * len(lab) > W - 4:
            out.append(f'<text x="{xof(ca) - 10:.1f}" y="{y + 13}" font-size="11" text-anchor="end" fill="var(--ink)" {halo}>{lab}</text>')
        else:
            out.append(f'<text x="{xe:.1f}" y="{y + 13}" font-size="11" fill="var(--ink)" {halo}>{lab}</text>')
        y += 32
    out.append(f'<text x="{gx + 5:.1f}" y="{y + 28}" font-size="11" fill="{GREEN}" font-weight="700">16.7 ms, a 60 fps frame</text>')
    log_axis(out, xof, 32, y, [(0.01, "10 µs"), (0.1, "0.1 ms"), (1, "1 ms"), (10, "10 ms"), (100, "0.1 s"), (1000, "1 s")])
    return svg_fig(W, y + 40, out, "; ".join(f"{l}: {a[0]:g} ms on the interpreter, {c[0]:g} ms compiled" for l, a, c, _ in PAIRS),
                   "Each row is one piece of Hazel code run two ways. The rows marked Node are not builds of the app: medians "
                   "of 30 runs in Node 22 on a laptop, from report 045. The rows marked <b class=\"build\">build 8</b> "
                   f"({B8}, run 42566328043) are in Firefox in the app: each view as the page runs it, the model in, the "
                   "call and its drawing, against the interpreter's evaluation and drawing, timed again in the page "
                   "(<code>globalThis.hazelJit.bench</code>, medians of 15). A drawn view's time is as if updating the "
                   "state were free. The ratio is of the middles of the ranges.")


def fig_loads():
    W, left, right = 940, 210, 60
    top = max(max(a, b) for _, _, a, b in LOADS)
    xof = lambda s: left + s / (top * 1.05) * (W - left - right)
    out = []
    title(out, "Build 8: each polygon slide loaded fresh, Compiled views on (teal) and off (grey), in seconds")
    y = 34
    for name, n, on, off in LOADS:
        out.append(f'<text x="{left - 10}" y="{y + 15}" font-size="11.5" text-anchor="end" fill="var(--ink)">{html.escape(name)} ({n} livelit{"s" if n != 1 else ""})</text>')
        for i, (v, col) in enumerate(((on, TEAL), (off, GREY))):
            out.append(f'<rect x="{left}" y="{y + i * 11}" width="{xof(v) - left:.1f}" height="9" rx="2" fill="{col}"><title>{name}, {"on" if i == 0 else "off"}: {v:g} s</title></rect>')
            out.append(f'<text x="{xof(v) + 5:.1f}" y="{y + i * 11 + 8}" font-size="10" fill="var(--ink)">{v:g} s</text>')
        y += 30
    return svg_fig(W, y + 10, out, "; ".join(f"{n}: {a:g} s on, {b:g} s off" for n, _, a, b in LOADS),
                   f"<b class=\"build\">Build 8</b> ({B8}, run 42566328043): one load of each slide each way, in Firefox on "
                   "GitHub's machines, from the address to every livelit drawn; the time includes compiling each livelit's "
                   "definition and the slide's run. One run each: the small slides' differences (0.1 to 0.3 s) are within a "
                   "run's noise.")


KINDS = [("compiler", "the compiler", VIOLET), ("app", "livelits in the app", TEAL), ("run", "a slide's run compiled", AMBER),
         ("drag", "a drag's fast path", SLATE), ("answer", "the worker's answer", "#0369a1"), ("measure", "measuring it", GREY)]


# each commit's kind, read from its message by hand (2026-11-09); a commit not listed is "measure"
KIND_OF = {
    "8c5cd80a29": "compiler", "79fe5bbebf": "compiler", "97ba46706b": "app", "567c8d9620": "compiler",
    "7a7151443c": "app", "889271cfbb": "app", "4c0ed173f1": "app", "bcec455abc": "app", "cb560ebb86": "app",
    "0926a80c74": "run", "ab4a41e587": "run", "1d445a24cc": "run", "932fbdcc63": "run", "6d71c427bf": "run",
    "a51dc778dd": "run", "7f5add1519": "run",
    "9fca635226": "drag", "38d4e4d0f8": "drag", "bdecaec5d9": "drag", "61f3f01a15": "drag",
    "20a3067c18": "answer", "4747a4120d": "answer",
}


def kind_of(c):
    return KIND_OF.get(c["h"], "measure")


def history():
    lines = git("log", "--reverse", "--format=%h|%at|%s", "8c5cd80a29^..HEAD").splitlines()
    return [dict(zip(("h", "t", "s"), l.split("|", 2))) for l in lines]


def fig_history(cs):
    W, left, right = 940, 190, 20
    t0, t1 = int(cs[0]["t"]), int(cs[-1]["t"])
    xof = lambda t: left + (t - t0) / max(1, t1 - t0) * (W - left - right)
    out = []
    title(out, f"The branch's {len(cs)} commits since hazel-jit's first, by when and by what they did")
    y = 34
    for k, label, col in KINDS:
        out.append(f'<text x="{left - 10}" y="{y + 10}" font-size="11.5" text-anchor="end" fill="var(--ink)">{label}</text>')
        out.append(f'<line x1="{left}" y1="{y + 6}" x2="{W - right}" y2="{y + 6}" stroke="var(--line)"/>')
        for c in cs:
            if kind_of(c) == k:
                out.append(f'<circle cx="{xof(int(c["t"])):.1f}" cy="{y + 6}" r="5" fill="{col}" stroke="var(--paper)" stroke-width="1.5">'
                           f'<title>{c["h"]}: {html.escape(c["s"])}</title></circle>')
        y += 24
    # the days
    import datetime
    d = datetime.datetime.fromtimestamp(t0).replace(hour=0, minute=0, second=0)
    while d.timestamp() <= t1:
        for hh, lab in ((0, d.strftime("%b %-d")), (12, "noon")):
            t = d.timestamp() + hh * 3600
            if t0 <= t <= t1:
                x = xof(t)
                out.append(f'<line x1="{x:.1f}" y1="28" x2="{x:.1f}" y2="{y}" stroke="var(--line)" stroke-dasharray="{"" if hh == 0 else "2 3"}"/>')
                out.append(f'<text x="{x:.1f}" y="{y + 14}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{lab}</text>')
        d += datetime.timedelta(days=1)
    return svg_fig(W, y + 26, out, f"{len(cs)} commits from {cs[0]['h']} to {cs[-1]['h']}",
                   "Not a build: the commits of <code>trial/694-view-jit</code> from hazel-jit's first (8c5cd80a29, "
                   "2026-11-06 11:48 MST) to today's, each a dot (hover for its message), in a row by what it does (read from "
                   "its message by hand). Measuring it includes the tests, the Firefox check, the timelines and report 047's "
                   "experiments on values as data. Mountain time.")


# --- today's runs, when there: the compile times, and steps 3 and 4 ---
RUNS = os.path.join(HERE, "data", "runs")


def todays():
    out = {}
    if os.path.isdir(RUNS):
        for r in sorted(os.listdir(RUNS)):
            p = os.path.join(RUNS, r, "jit.json")
            if os.path.exists(p):
                out[r] = json.load(open(p))
    return out


TODAY = todays()
compiles = []
_crun = (json.load(open(os.path.join(HERE, "data", "today.json"))).get("compile") or {}).get("run") if os.path.exists(os.path.join(HERE, "data", "today.json")) else None
for r, d in TODAY.items():
    if _crun and r != _crun:
        continue
    for s in d["slides"]:
        for c in ((s.get("on") or {}).get("jit") or {}).get("compiles") or []:
            compiles.append(dict(c, slide=s["slide"], run=r))
defs = [c for c in compiles if c["what"] == "a livelit's definition"]
runs_c = [c for c in compiles if c["what"] == "a slide's whole run"]


def fig_costs():
    if not compiles:
        return fig_loads()
    W, left, right, bottom = 940, 70, 30, 40
    xs = [c["nodes"] for c in compiles]
    ys = [c["to_js_ms"] + c["js_ms"] for c in compiles]
    xlo, xhi = math.log10(max(1, min(xs)) / 1.3), math.log10(max(xs) * 1.3)
    ylo, yhi = math.log10(max(0.05, min(ys)) / 1.5), math.log10(max(ys) * 1.5)
    H = 300
    xof = lambda n: left + (math.log10(n) - xlo) / (xhi - xlo) * (W - left - right)
    yof = lambda ms: 30 + (yhi - math.log10(max(ms, 0.05))) / (yhi - ylo) * (H - 30 - bottom)
    out = []
    title(out, "Each compilation the page made, its time against the size of the term compiled (both log scales)")
    for v, lab in ((0.05, "read 0"), (1, "1 ms"), (10, "10 ms"), (100, "100 ms"), (1000, "1 s")):
        if ylo <= math.log10(v) <= yhi:
            y = yof(v)
            out.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="var(--line)"{" stroke-dasharray=\"3 3\"" if v < 1 else ""}/>')
            out.append(f'<text x="{left - 6}" y="{y + 4:.1f}" font-size="10.5" text-anchor="end" fill="var(--muted)">{lab}</text>')
    for v in (100, 1000, 10000, 100000, 1000000):
        if xlo <= math.log10(v) <= xhi:
            x = xof(v)
            out.append(f'<line x1="{x:.1f}" y1="30" x2="{x:.1f}" y2="{H - bottom}" stroke="var(--line)"/>')
            out.append(f'<text x="{x:.1f}" y="{H - bottom + 14}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{v:,} nodes</text>')
    for c in compiles:
        col = AMBER if c["what"] == "a slide's whole run" else TEAL
        ms = c["to_js_ms"] + c["js_ms"]
        out.append(f'<circle cx="{xof(c["nodes"]):.1f}" cy="{yof(ms):.1f}" r="{6 if col == AMBER else 4}" fill="{col}" fill-opacity="0.75" stroke="var(--paper)">'
                   f'<title>{c["slide"]}, {c["what"]}: {c["to_js_ms"]:.1f} ms to JS + {c["js_ms"]:.1f} ms in the browser; {int(c["nodes"]):,} nodes, {int(c["chars"]):,} characters of JS</title></circle>')
    out.append(f'<circle cx="{W - 250}" cy="{H - 8}" r="4" fill="{TEAL}"/><text x="{W - 242}" y="{H - 4}" font-size="11" fill="var(--ink)">a livelit\'s definition</text>')
    out.append(f'<circle cx="{W - 120}" cy="{H - 8}" r="6" fill="{AMBER}"/><text x="{W - 110}" y="{H - 4}" font-size="11" fill="var(--ink)">a slide\'s whole run</text>')
    return svg_fig(W, H + 6, out, f"{len(defs)} definitions and {len(runs_c)} whole runs compiled",
                   f"<b class=\"build\">{BT['name']}</b> ({BT['commit']}, run {BT['run']}): every compilation the page made "
                   "while each polygon slide loaded and its livelits were clicked, in Firefox on GitHub's machines "
                   "(<code>globalThis.hazelJit.compiles</code>). Its time is hazel-jit's part, the term to JS source, and the "
                   "browser's, <code>new Function</code> and, for a definition, running its module; its size is the "
                   "elaborated term's nodes (expressions, patterns and types). Firefox's clock reads whole milliseconds "
                   "here: the dashed row is the compilations that read 0 ms, under one.")


def costs_table():
    if not compiles:
        return ('<table class="vals"><tr><th>What was compiled</th><th>Where, which build</th><th>Time</th></tr>'
                '<tr><td>The Polygons livelit\'s definition</td><td>Node, not a build of the app (report 045)</td><td class="n">4.46 ms</td></tr>'
                f'<tr><td>The Witch\'s whole program (2,222 lines, 53 livelits), at each of four steps</td><td>Firefox, build 8 ({B8})</td><td class="n">{C_RUN8}</td></tr>'
                '</table>')
    rows = []
    for what, cs in (("a livelit's definition", defs), ("a slide's whole run", runs_c)):
        if not cs:
            continue
        tot = [c["to_js_ms"] + c["js_ms"] for c in cs]
        tj = [c["to_js_ms"] for c in cs]
        jj = [c["js_ms"] for c in cs]
        nn = [c["nodes"] for c in cs]
        rows.append(f"<tr><td>{what}</td><td class=\"n\">{len(cs)}</td><td class=\"n\">{st.median(tot):.1f} ms</td>"
                    f"<td class=\"n\">{min(tot):.1f} to {max(tot):.1f} ms</td><td class=\"n\">{st.median(tj):.1f} + {st.median(jj):.1f} ms</td>"
                    f"<td class=\"n\">{st.median(nn):,.0f}</td><td class=\"n\">{1000 * sum(tot) / sum(nn):.2f} ms</td></tr>")
    return ('<table class="vals"><tr><th>What was compiled</th><th>How many</th><th>Median</th><th>Range</th>'
            '<th>Median parts: to JS + in the browser</th><th>Median size, nodes</th><th>Per 1,000 nodes</th></tr>'
            + "".join(rows) + "</table>"
            f'<p class="muted">{BT["name"]} ({BT["commit"]}, run {BT["run"]}), in Firefox, every compilation the page made '
            "on the six polygon slides. Report 045 measured the Polygons definition at 4.46 ms in Node.</p>")


# --- today's builds, numbered on from report 050's eight (each the one before plus one change) ---
TODAY_BUILDS = [
    {"n": 8, "name": "cut C (report 050's last)", "commit": "61f3f01a15", "run": "42566328043", "path": "050/data/runs/42566328043/jit.json",
     "adds": "Report 050's build 8, for comparison."},
    {"n": 9, "name": "steps 3 and 4", "commit": "7f5add1519", "run": "42651798712", "path": "051/data/runs/42651798712/jit.json",
     "adds": "The slide's run compiled once and kept when only models change; its answers kept when the worker catches up; the worker's request held after a compiled step."},
    {"n": 10, "name": "the comparison after the paint", "commit": "3e51af567f", "run": "42654708022", "path": "051/data/runs/42654708022/jit.json",
     "adds": "The program compared after the paint, not in the view; every compilation timed."},
    {"n": 11, "name": "samples as data", "commit": "1524e96da3", "run": "42657604986", "path": "051/data/runs/42657604986/jit.json",
     "adds": "Probe samples' first-order values sent from the worker as data (step 7's first slice; it made the answer larger, and is off since 22cd278106)."},
    {"n": 12, "name": "steps 2 and 1", "commit": "d9d63c13af", "run": "42658981172", "path": "051/data/runs/42658981172/jit.json",
     "adds": "A step's edit made after the paint, once the compiled run has drawn it (b37d2e6df1); each editor's decorations and probes' views reused across a drag's frames."},
    {"n": 13, "name": "the outline on its own", "commit": "8bf44f23cf", "run": "42670654733", "path": "051/data/runs/42670654733/jit.json",
     "adds": "The sidebar's outline built on its own after the paint, not in the page's view (bfbd88a1ae, 8bf44f23cf; Matthew: \"no memoization, but isolation, instead\"). Also samples as data off again (22cd278106), as on the team's hosted build. Its other run (42668742255) landed on a machine 20 to 40% slower on work this change does not touch, and read slower throughout."},
    {"n": 14, "name": "the page after a step", "commit": "b310a58b67", "run": "42690151014", "path": "051/data/runs/42690151014/jit.json",
     "adds": "A probe's row abbreviates its value without rewriting all of it first (e1bb06d115, 99542e86e3); after a compiled answer, the worker's reuse plan and streams wait for its result and come with it as one action (a65a9e5f52); each projector drawn and each update named on the check's timeline (d1ef274c10, af099c780d, b310a58b67). Its machine was slower than build 13's (the worker's encode 70 to 82 ms, against 52): the fair comparison is build 13 with the same timing marks on a machine like it (af099c780d, run 42685958876, encode 68 to 86), see the text."},
    {"n": 15, "name": "livelits kept across an edit", "commit": "1da80a8022", "run": "42697957029", "path": "051/data/runs/42697957029/jit.json",
     "adds": "A livelit's cached view keyed on its own statics record, not the whole statics map and elaborated term (d35f2f2619, a1b43cba46): after an edit only the edited livelit is drawn again, not all 53; a probe's value check remembered per value (515813903a). Plotted: a run of a1b43cba46 with the autosave's parts timed (1da80a8022, nothing else changed), on a machine like build 13's (the worker's encode 56 to 72 ms, against 52). Its other run (a1b43cba46, run 42696123420) was on a machine like build 14's."},
    {"n": 16, "name": "the autosave on its own", "commit": "f4bcd64cf7", "run": "42699757678", "path": "051/data/runs/42699757678/jit.json",
     "adds": "The autosave writes the page's model without going through the update (Main.apply), so the very same model comes back and nothing is drawn again: after each autosave, no calculate, whole view or outline (about 60 ms on build 15's run). On a machine like build 14's (the worker's encode 73 to 109 ms), so its steps and drag read slower than build 15's run."},
]
VIEW_PER_FRAME = {8: (10.1, 8.3), 9: (8.6, 7.1), 10: (9.8, 7.9), 11: (8.2, 6.8), 12: (6.1, 4.5), 13: (4.9, 3.9), 14: (7.5, 5.9), 15: (4.4, 3.4), 16: (7.4, 5.9)}  # from each run's log
for b in TODAY_BUILDS:
    w = next(x for x in json.load(open(os.path.join(ROOT, b["path"])))["slides"] if x["slide"] == "Witch")
    b["steps"] = [e["picture_changed_ms"] for e in w["edits"]["on"]]
    dr = next((r for r in (w.get("drags") or {}).get("on", []) if r.get("frames")), None)
    b["drag"] = dr["stats"] if dr else None
    b["view"], b["editors"] = VIEW_PER_FRAME[b["n"]]


def fig_today():
    W, left, right = 940, 250, 20
    mid_x = 610
    lo, hi = math.log10(10), math.log10(1000)
    xof = lambda ms: left + (math.log10(ms) - lo) / (hi - lo) * (mid_x - 40 - left)
    vx = lambda ms: mid_x + ms / 12 * (W - right - mid_x - 130)
    out = []
    title(out, "The Witch, builds 8 to 16: a step, from the click to the picture (left, log scale), and a drag's frame, the page's view (right)")
    y = 40
    for b in TODAY_BUILDS:
        out.append(f'<text x="{left - 10}" y="{y + 12}" font-size="11.5" text-anchor="end" fill="var(--ink)">{b["n"]} · {html.escape(b["name"])}</text>')
        out.append(f'<line x1="{left}" y1="{y + 8}" x2="{mid_x - 40}" y2="{y + 8}" stroke="var(--line)"/>')
        for t in b["steps"]:
            out.append(f'<circle cx="{xof(t):.1f}" cy="{y + 8}" r="5" fill="{TEAL}" fill-opacity="0.8" stroke="var(--paper)"><title>build {b["n"]}: a step, {t:g} ms</title></circle>')
        out.append(f'<rect x="{mid_x}" y="{y + 2}" width="{vx(b["editors"]) - mid_x:.1f}" height="12" rx="2" fill="{SLATE}"><title>the editors: {b["editors"]} ms</title></rect>')
        out.append(f'<rect x="{vx(b["editors"]):.1f}" y="{y + 2}" width="{vx(b["view"]) - vx(b["editors"]):.1f}" height="12" rx="2" fill="{GREY}"><title>the rest of the view: {b["view"] - b["editors"]:.1f} ms</title></rect>')
        d = b["drag"]
        out.append(f'<text x="{vx(b["view"]) + 6:.1f}" y="{y + 12}" font-size="10.5" fill="var(--ink)">{b["view"]} ms · {d["fps"]} fps</text>')
        y += 26
    gx = xof(GOAL)
    out.append(f'<line x1="{gx:.1f}" y1="32" x2="{gx:.1f}" y2="{y}" stroke="{GREEN}" stroke-width="2.5"/>')
    out.append(f'<text x="{gx + 4:.1f}" y="{y + 26}" font-size="10.5" fill="{GREEN}" font-weight="700">16.7 ms</text>')
    for v, lab in ((10, "10 ms"), (100, "0.1 s"), (1000, "1 s")):
        x = xof(v)
        out.append(f'<text x="{x:.1f}" y="{y + 14}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{lab}</text>')
    for v in (0, 4, 8, 12):
        x = vx(v)
        out.append(f'<line x1="{x:.1f}" y1="34" x2="{x:.1f}" y2="{y}" stroke="var(--line)" stroke-dasharray="2 3"/>')
        out.append(f'<text x="{x:.1f}" y="{y + 14}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{v} ms</text>')
    return svg_fig(W, y + 34, out, "; ".join(f"build {b['n']}: steps {b['steps']} ms; a drag's view {b['view']} ms a frame, {b['drag']['fps']} fps" for b in TODAY_BUILDS),
                   "<b class=\"build\">Builds 8 to 16</b> of <code>trial/694-view-jit</code> (the table below), each one run of the "
                   "Firefox check on GitHub's machines. Left: each of the four steps of the neck and arms sliders, from the click to "
                   "the picture changing; from build 12 the page draws the compiled run's answers first and makes the edit after "
                   "the paint, and from build 13 the sidebar's outline is built after the paint, not in the view. Build 14's run "
                   "was on a slower machine (the worker's encode 70 to 82 ms, against 52 on build 13's), so its drag's view "
                   "(7.5 ms a frame) is to be read against build 13 on a machine like it: 7.7. Build 15's run plotted was on a machine "
                   "like build 13's, and build 16's on one like build 14's. Right: a 3-second compiled drag of the neck slider, the page's view per frame (dark: the editors; "
                   "light: the rest), with the drag's frames a second. The frames a second vary from run to run more than the "
                   "builds differ (builds 9 to 11 changed nothing a drag does and gave 54.3, 47.8 and 56.3); the view's time per "
                   "frame is steadier.")


def today_table():
    rows = "".join(
        f'<tr><td>{b["n"]} · {html.escape(b["name"])}<br><span class="muted">{b["commit"]}, run {b["run"]}</span></td>'
        f'<td>{b["adds"]}</td><td class="n">{min(b["steps"]):g} to {max(b["steps"]):g} ms</td>'
        f'<td class="n">{b["drag"]["fps"]} fps<br><span class="muted">view {b["view"]} ms a frame</span></td></tr>'
        for b in TODAY_BUILDS)
    return ('<table class="vals"><tr><th>Build</th><th>What it adds to the one above</th><th>A step, to the picture</th>'
            '<th>A compiled drag</th></tr>' + rows + "</table>")


# --- the numbers the text quotes ---
C_RUN8 = "126 to 141 ms"   # build 8, the four steps' "hazel-jit: the run compiled" (050's run 42566328043)
BT = {"name": "today's build", "commit": "", "run": ""}
meta_today = json.load(open(os.path.join(HERE, "data", "today.json"))) if os.path.exists(os.path.join(HERE, "data", "today.json")) else {}
if meta_today.get("compile"):
    BT = meta_today["compile"]

cs = history()
lines = {k: int(subprocess.run(["wc", "-l", os.path.join(REPO, p)], capture_output=True, text=True).stdout.split()[0])
         for k, p in (("l_jit", "src/language/dynamics/HazelJit.re"), ("l_value", "src/language/dynamics/HazelJitValue.re"),
                      ("l_run", "src/language/dynamics/HazelJitRun.re"), ("l_dom", "src/haz3lcore/projectors/HazelJitDOM.re"))}
NUMS = {
    "updated": updated, "b8": B8, "head": git("rev-parse", "--short=10", "HEAD"),
    "g_lo": f"{min(RATIOS):,.0f}", "g_hi": f"{max(RATIOS):,.0f}", "g_petri": f"{RATIOS[1]:,.0f}",
    "b1_step": "4.17 to 6.52 s", "b8_step": "176 to 290 ms", "b8_fps": "48.4", "b5_fps": "9.8",
    "b12_step": "19 to 24 ms", "b12_fps": "57.6", "b12_within": "171 of its 173", "b12_view": "6.1",
    "b13_view": "4.9", "b13_fps": "57.6", "b13_msgview": "45 to 63 ms", "b12_msgview": "88 to 130 ms", "b13_outline": "36 to 60 ms",
    "b12_after": "0.48 to 0.72 s", "b13_after": "0.43 to 0.60 s",
    "b15_after": "0.35 to 0.46 s", "b15_ll": "2 to 3 ms", "b14_ll": "9 to 14 ms",
    "b15f_after": "0.24 to 0.30 s", "b13f_after": "0.43 to 0.60 s", "b15f_step": "16 to 20 ms", "b15f_fps": "58.6", "b15f_within": "173 of its 177", "b15f_view": "4.4",
    "b14_after": "0.37 to 0.52 s", "b13s_after": "0.56 to 0.92 s", "b14_row": "8 to 21 ms", "b13s_row": "44 to 91 ms",
    "now_view": "10.1", "now_run": "2.2",
    "v_pic_i": f"{pic[0][1]:g}", "v_pic_c": f"{pic[0][2]:.1f}",
    "v_poly_i": f"{min(b[1] for b in polys):g} to {max(b[1] for b in polys):g}",
    "v_poly_c": f"{min(b[2] for b in polys):.2f} to {max(b[2] for b in polys):.2f}",
    "n_commits": str(len(cs) - 1),
    "c_run": (f"{min(c['to_js_ms'] + c['js_ms'] for c in runs_c):.0f} to {max(c['to_js_ms'] + c['js_ms'] for c in runs_c):.0f} ms "
              f"(median {st.median([c['to_js_ms'] + c['js_ms'] for c in runs_c]):.0f})" if runs_c else C_RUN8),
    "c_def": ("about a millisecond, the largest about 20 ms" if defs
              else "about 4.5 ms (in Node; Firefox's numbers are being measured)"),
    "c_note": meta_today.get("c_note", "The compile times of each definition in Firefox are being measured now; until they are in, the figure shows what compiling does to a slide's load."),
    "c_kept": meta_today.get("c_kept", "what the comparison that replaces it costs is being measured now."),
    "c_commit": meta_today.get("c_commit", "(today)"),
    "next_note": meta_today.get("next_note", "Steps 3 and 4 were committed this morning (7f5add1519) and are in the Firefox check now; this report will carry their numbers when they come."),
    "unsupported": ("holes (in expressions, patterns and modules), tests, quotations, stepper filters, partial "
                    "application, reverse application (<code>|&gt;</code>), a recursive definition of more than one name, a "
                    "closure with its own environment, <code>undefined</code>, and a few rarer shapes of patterns, labels "
                    "and module members"),
    **{k: f"{v:,}" for k, v in lines.items()},
    "l_total": f"{sum(lines.values()):,}",
}
NEXT = meta_today.get("next_rows") or [
    ["3", "Compile the program once, not again after a step that changed only a livelit's model: keep the compiled program, and give it the new models.",
     "126 to 141 ms of the page's thread after each step.", "done today (7f5add1519); being measured"],
    ["4", "Leave the worker out when the compiled run has answered: keep the run's answers when the worker catches up, and hold the worker's request until the steps stop.",
     "The page drawing every livelit again from the worker's answer, to the same picture; the worker's run for each step of a quick series.", "done today (7f5add1519); being measured"],
    ["7", "Send values as data where they cross: the worker's answer and its probe samples without ids, holes or closures.",
     "The answer is 590 KB, encoded in 70 ms in the worker and decoded in 13 ms in the page; the Witch's picture is 3 times smaller as data (report 047).", "started: the first slice, the samples' values on the way to the page (^ticket(718))"],
    ["1", "Draw only the livelits a drag changes: make the editors' and projectors' views incremental.",
     "Most of the page's view, 10.1 ms of a 17.1 ms median frame of a drag.", "next"],
    ["2", "Handle a slider's change event without an edit of the program, as cut A did for its input events, or do the edit's work after the paint.",
     "Statics and syntax (32 ms) and the whole slide's view (91 ms), all before the paint at 176 ms.", "next, after 1 (^ticket(721))"],
]
NUMS["next_rows"] = "\n".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in NEXT)

FIGS = {
    "fig_gains": fig_gains(),
    "fig_road": kept_fig("050", "road", "A slider's step on the Witch, build by build (report 050's eight builds of "
                         "<code>trial/694-view-jit</code>, each the one before plus one change; Firefox on GitHub's machines): "
                         "each dot one step, from the click to the picture changing. <b class=\"build\">Builds 1 to 3</b> waited for "
                         "the worker's answer; from <b class=\"build\">build 4</b> on, the page's compiled run draws the picture first."),
    "fig_drags": kept_fig("050", "drags", "A 3-second drag of the Witch's neck slider, frames a second, compiled (teal) and "
                          "with nothing compiled (grey), on <b class=\"build\">builds 5 to 8</b> of report 050. With nothing "
                          "compiled the picture does not move until the drag ends."),
    "fig_costs": fig_costs(),
    "fig_loads": fig_loads() if compiles else "",
    "tab_costs": costs_table(),
    "fig_history": fig_history(cs),
    "fig_today": fig_today(),
    "tab_today": today_table(),
    "fig_shot": ('<div class="figrow"><figure class="f wide"><img src="img/drag-b12-on.png" alt="The Witch slide during a compiled '
                 'drag of the neck slider on build 12, the frame-rate overlay at top right reading 59 fps" style="width:100%;height:auto;'
                 'border:1px solid var(--line);border-radius:4px;background:#fff"><figcaption><b class="build">Build 12</b> '
                 '(d9d63c13af, run 42658981172): the Witch slide at the end of the check\'s 3-second compiled drag of the neck '
                 'slider, in Firefox on GitHub\'s machines, with the overlay (<code>?hud</code>) at top right: 59 frames in the '
                 'last second, the longest 33 ms.</figcaption></figure></div>'),
}
body = open(os.path.join(HERE, "body.html")).read()
for k, v in {**NUMS, **FIGS}.items():
    body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{(\w+)\}\}", body)
assert not left, left
TITLE = "Hazel-JIT Status Report"
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n"
        "<meta name=\"description\" content=\"hazel-jit, Hazel compiled to JavaScript: what it gains and costs, how to use it in your own PR, what has been added since its first version, its limits and the next steps under way. For colleagues and their agents.\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
json.dump({"pairs": [{"what": l, "interpreter_ms": i, "compiled_ms": c, "where": w} for l, i, c, w in PAIRS],
           "loads_build8": [{"slide": n, "livelits": k, "on_s": a, "off_s": b} for n, k, a, b in LOADS],
           "compiles": compiles, "commits": cs, "next": NEXT},
          open(os.path.join(HERE, "data", "numbers.json"), "w"), indent=1)
print("wrote 051/index.html;", updated, {k: NUMS[k] for k in ("g_lo", "g_hi", "c_def", "n_commits")})
