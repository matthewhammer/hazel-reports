#!/usr/bin/env python3
"""^report(48), Why Hazel Is Slow: A Thousand Cuts: writes 048/index.html from body.html and data/ledger.json (the series'
measured costs, one object each), with the series' styles (035's). Matthew, 2026-11-08: "Cyrus wants to know why Hazel
is slow, and I say: death by a thousand cuts. I'd like more substance behind that idea." """
import html, json, os, re, subprocess, sys, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "047"))
import treemap as TM  # (the squarified layout, ^report(47))

s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
EXTRA = """
  ol.outline > li { margin: 4px 0; } .muted { color: var(--muted); }
  table.vals { display: block; overflow-x: auto; max-width: 100%; border-collapse: collapse; margin: 0.6em 0 1em; font-size: 0.88em; }
  table.vals th, table.vals td { padding: 4px 8px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
  table.vals th { font-weight: 600; } figure.f { margin: 1.2em 0; } figure.f svg { max-width: 100%; }
  figcaption { color: var(--muted); font-size: 0.9em; margin-top: 6px; max-width: 80ch; }
  details.ledger > summary { cursor: pointer; font-weight: 600; margin: 0.5em 0; }
"""
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
L = json.load(open(os.path.join(HERE, "data", "ledger.json")))

# each root cause in one of four families of design choice, each applied everywhere
FAMILIES = [
    ("terms", "Values held as terms", "#ea580c",
     ["ids on every term", "values are terms (open terms, holes, closures)", "environments and substitution", "probes and samples",
      "run-time type checks (ascriptions, casts)"]),
    ("whole", "Whole-program work on every edit", "#2563eb",
     ["re-analysis per edit (statics, parsing)", "parsing on load", "incremental reuse checks", "the page's view and redraw", "undo and history"]),
    ("moving", "Values moved as terms across boundaries", "#9333ea",
     ["serialization (Marshal, sharing)", "the worker trip", "the JS boundary (js_of_ocaml)", "scheduling (worker slices, message cadence)"]),
    ("machine", "An interpreter that pays for the editor at every step", "#0d9488",
     ["interpretation itself", "persistent maps and allocation (GC)", "trampolines and stack safety", "data representation (flat lists, no maps)"]),
    ("other", "Other", "#6b7280", ["other"]),
]
FAM_OF = {c: f for f, _, _, cs in FAMILIES for c in cs}


def status_of(s):
    """fixed, mitigated, a fix in an open PR, open, or other"""
    t = s.lower()
    if t.startswith("fixed"):
        return "fixed"
    if t.startswith("mitigated") or "mitigated" in t[:40] or t.startswith("mostly avoided") or t.startswith("avoided"):
        return "mitigated"
    if re.match(r"(fix |pr )#\d+.*open", t) or (t.startswith("fix #") and "open" in t[:30]) or t.startswith("fix #2661") or t.startswith("fix #2681"):
        return "open PR"
    if t.startswith("open"):
        return "open"
    return "other"


STATUS = [("fixed", "fixed (on some branch)", "#15803d"), ("mitigated", "mitigated", "#86efac"),
          ("open PR", "a fix in an open PR", "#facc15"), ("open", "open", "#f87171"), ("other", "unknown, bounded or n/a", "#d1d5db")]
for x in L:
    x["_status"] = status_of(x["status"])
    x["_family"] = FAM_OF.get(x["root_cause"], "other")
COUNT = {k: sum(1 for x in L if x["_status"] == k) for k, _, _ in STATUS}
FCOUNT = {f: sum(1 for x in L if x["_family"] == f) for f, _, _, _ in FAMILIES}
CCOUNT = {}
for x in L:
    CCOUNT[x["root_cause"]] = CCOUNT.get(x["root_cause"], 0) + 1
REPORTS = sorted({x["report"][:3] for x in L if re.match(r"\d{3}", x["report"])})


def link(rep):
    m = re.match(r"(\d{3})(#[\w-]+)?", rep)
    if not m:
        return html.escape(rep)
    return f'<a href="../{m.group(1)}/{m.group(2) or ""}">{html.escape(rep)}</a>'


SHORT_FAM = {"terms": "Values held as terms", "whole": "Whole-program work on every edit", "moving": "Values moved across boundaries",
             "machine": "Paying for the editor every step", "other": "Other"}
SHORT_CAUSE = {"environments and substitution": "environments", "trampolines and stack safety": "trampolines",
               "data representation (flat lists, no maps)": "data layout", "persistent maps and allocation (GC)": "allocation, GC",
               "values are terms (open terms, holes, closures)": "values are terms", "run-time type checks (ascriptions, casts)": "type checks at run time",
               "scheduling (worker slices, message cadence)": "scheduling", "re-analysis per edit (statics, parsing)": "re-analysis per edit"}


def fig_cuts():
    """every measured cut, one equal rectangle each, grouped by family and then by root cause; coloured by status"""
    W, H = 940, 520
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">' + f"{len(L)} measured cuts, from {len(REPORTS)} reports: "
           'one rectangle each, grouped by what they come from, coloured by where they stand</text>']
    fams = sorted([(f, FCOUNT[f]) for f, _, _, _ in FAMILIES if FCOUNT[f]], key=lambda kv: -kv[1])
    for f, fx, fy, fw, fh in TM.squarify(fams, 16, 30, W - 32, H):
        name, colour = next((n, c) for ff, n, c, _ in FAMILIES if ff == f)
        name = SHORT_FAM.get(f, name)
        causes = sorted([(c, CCOUNT.get(c, 0)) for c in next(cs for ff, _, _, cs in FAMILIES if ff == f) if CCOUNT.get(c)], key=lambda kv: -kv[1])
        for c, cx, cy, cw, ch in TM.squarify(causes, fx + 2, fy + 18, fw - 4, fh - 20):
            cuts = sorted([x for x in L if x["root_cause"] == c], key=lambda x: [k for k, _, _ in STATUS].index(x["_status"]))
            for i, kx, ky, kw, kh in TM.squarify([(i, 1) for i in range(len(cuts))], cx + 1, cy + 13, cw - 2, ch - 14):
                x = cuts[i]
                col = next(cc for k, _, cc in STATUS if k == x["_status"])
                out.append(f'<rect x="{kx:.1f}" y="{ky:.1f}" width="{max(0.5, kw - 1):.1f}" height="{max(0.5, kh - 1):.1f}" fill="{col}" rx="1.5">'
                           f'<title>{html.escape(x["cut"])}: {html.escape(x["cost"][:220])} ({html.escape(x["report"])}; {html.escape(x["_status"])})</title></rect>')
            out.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cw:.1f}" height="{ch:.1f}" fill="none" stroke="{colour}" stroke-width="1"/>')
            label = SHORT_CAUSE.get(c, c.split(" (")[0])
            out.append(f'<text x="{cx + 3:.1f}" y="{cy + 10:.1f}" font-size="9" fill="var(--ink)">{html.escape(label[:int(cw / 4.8)])} ({len(cuts)})</text>')
        out.append(f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{fw:.1f}" height="{fh:.1f}" fill="none" stroke="{colour}" stroke-width="2.5" rx="3"/>')
        out.append(f'<text x="{fx + 4:.1f}" y="{fy + 13:.1f}" font-size="11" font-weight="700" fill="{colour}">{html.escape(name[:int(fw / 6.2)])} ({FCOUNT[f]})</text>')
    ly = 30 + H + 18
    x = 16
    for k, label, col in STATUS:
        out.append(f'<rect x="{x}" y="{ly - 10}" width="12" height="12" fill="{col}" rx="1.5"/>')
        out.append(f'<text x="{x + 16}" y="{ly}" font-size="11" fill="var(--muted)">{label}: {COUNT[k]}</text>')
        x += 16 + 6.0 * len(label) + 52
    h = ly + 12
    alt = "; ".join(f"{n}: {FCOUNT[f]} cuts" for f, n, _, _ in FAMILIES) + "; " + "; ".join(f"{l}: {COUNT[k]}" for k, l, _ in STATUS)
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{html.escape(alt)}" '
            f'style="width:100%;height:auto;display:block">' + "".join(out) + "</svg><figcaption>A treemap (Ben Shneiderman's; laid out as in "
            "^report(47)): every rectangle is one cost a report measured, all the same size, so the area of a group is how many cuts it "
            "holds. Hover a rectangle for the cut, its number and its report. The measurements differ in workload and units, so the "
            "rectangles count cuts; they do not weigh them.</figcaption></figure></div>")


# (the Witch's small edit, cut by cut: ^report(46)'s readings)
sys.path.insert(0, os.path.join(ROOT, "046"))
_cwd = os.getcwd()
os.chdir(os.path.join(ROOT, "046"))
import witch046 as W46
os.chdir(_cwd)
STEPS = [("before the cuts", [r["pic"] for r in W46.TR], W46.FA["run"]),
         ("a module kept out of a probe's environment, the trace cleared", [r["pic"] for r in W46.TC], W46.FC["run"]),
         ("the worker's answers unshared", [r["pic"] for r in W46.TN], W46.FN["run"])]
GOAL_MS = 1000 / 60


def fig_witch():
    """the small edit's time at each step, on a log scale, against the goal"""
    import math
    W, left, right = 940, 330, 30
    lo, hi = math.log10(10), math.log10(10000)
    xof = lambda ms: left + (math.log10(ms) - lo) / (hi - lo) * (W - left - right)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">A slider\'s step on the Witch slide, from the edit '
           'to the picture showing it, in Firefox: each cut so far, and the goal (a log scale)</text>']
    y = 40
    for label, xs, run in STEPS + [("the goal: 60 fps", [GOAL_MS], None)]:
        a, b = min(xs), max(xs)
        out.append(f'<text x="{left - 10}" y="{y + 14}" font-size="11.5" text-anchor="end" fill="var(--ink)">{html.escape(label)}</text>')
        if run is None:
            out.append(f'<line x1="{xof(GOAL_MS):.1f}" y1="{y}" x2="{xof(GOAL_MS):.1f}" y2="{y + 20}" stroke="#15803d" stroke-width="3"/>')
            out.append(f'<text x="{xof(GOAL_MS) + 8:.1f}" y="{y + 14}" font-size="11" fill="#15803d" font-weight="700">16.7 ms a step</text>')
        else:
            out.append(f'<rect x="{xof(a):.1f}" y="{y + 2}" width="{max(3, xof(b) - xof(a)):.1f}" height="16" fill="var(--accent)" opacity="0.85">'
                       f'<title>{label}: {a / 1000:.1f} to {b / 1000:.1f} s (run {run})</title></rect>')
            out.append(f'<text x="{xof(a) - 8:.1f}" y="{y + 14}" font-size="11" text-anchor="end" fill="var(--ink)">{a / 1000:.1f} to {b / 1000:.1f} s, '
                       f'{a / GOAL_MS:.0f} to {b / GOAL_MS:.0f} times the goal</text>')
        y += 30
    for ms in (10, 100, 1000, 10000):
        x = xof(ms)
        out.append(f'<line x1="{x:.1f}" y1="34" x2="{x:.1f}" y2="{y}" stroke="var(--line)" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{y + 14}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{ms / 1000:g} s</text>')
    h = y + 22
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="the Witch\'s small edit at each cut, and the goal" '
            f'style="width:100%;height:auto;display:block">' + "".join(out) + "</svg><figcaption>The same eight edits each time (two sliders, "
            "both ways, compiled views on and off), Firefox on GitHub's machines, ^report(46)'s runs: "
            + ", ".join(str(r) for _, _, r in STEPS) + ".</figcaption></figure></div>")


def fig_now():
    """where the small edit's time goes now: a treemap of its parts, the median edit"""
    rows = sorted(W46.TN, key=lambda r: r["pic"])
    r = rows[len(rows) // 2]
    parts = [("the worker's evaluator", r["eval"], "#2563eb"), ("the page, after the answer (views drawn again)", r["after"], "#93c5fd"),
             ("the page, before the request (update, view, statics)", r["post"], "#bfdbfe"), ("the worker's other work", max(0, r["wother"]), "#9ca3af"),
             ("the answer encoded", r["encode"] + r["send"], "#ea580c"), ("the answer decoded", r["decode"], "#f59e0b")]
    W, H = 940, 300
    out = [f'<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">Where a small edit\'s {r["pic"] / 1000:.2f} s goes now '
           f'({html.escape(r["label"])} {r["from"]} to {r["to"]}, views {r["mode"]}), against the goal\'s 16.7 ms</text>']
    total = sum(v for _, v, _ in parts)
    gw = W - 32
    scale = gw * H / total
    goal_side = (GOAL_MS * scale) ** 0.5
    for k, x, y, w, h in TM.squarify(sorted([(i, v) for i, (_, v, _) in enumerate(parts)], key=lambda kv: -kv[1]), 16, 30, gw - goal_side - 30, H):
        name, v, col = parts[k]
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{col}" stroke="var(--paper, #fff)" stroke-width="2">'
                   f'<title>{html.escape(name)}: {v:.0f} ms</title></rect>')
        if w > 70 and h > 30:
            out.append(f'<text x="{x + 6:.1f}" y="{y + 16:.1f}" font-size="11" font-weight="700" fill="#111">{v:.0f} ms</text>')
            out.append(f'<text x="{x + 6:.1f}" y="{y + 30:.1f}" font-size="10" fill="#111">{html.escape(name[:int(w / 5.4)])}</text>')
    gx = W - 16 - goal_side
    out.append(f'<rect x="{gx:.1f}" y="30" width="{goal_side:.1f}" height="{goal_side:.1f}" fill="#15803d"><title>the goal: 16.7 ms</title></rect>')
    out.append(f'<text x="{W - 16:.1f}" y="{30 + goal_side + 14:.1f}" font-size="10.5" text-anchor="end" fill="#15803d" font-weight="700">the goal,</text>')
    out.append(f'<text x="{W - 16:.1f}" y="{30 + goal_side + 27:.1f}" font-size="10.5" text-anchor="end" fill="#15803d" font-weight="700">16.7 ms,</text>')
    out.append(f'<text x="{W - 16:.1f}" y="{30 + goal_side + 40:.1f}" font-size="10.5" text-anchor="end" fill="#15803d" font-weight="700">same scale</text>')
    h = 30 + H + 10
    alt = "; ".join(f"{n}: {v:.0f} ms" for n, v, _ in parts)
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{html.escape(alt)}" '
            f'style="width:100%;height:auto;display:block">' + "".join(out) + f"</svg><figcaption>The median of the eight edits after the "
            f"cuts (run {W46.FN['run']}), laid end to end as ^report(46) does (the page's and the worker's timelines), drawn as a treemap: "
            "each rectangle's area is its time, and the green square is the goal's 16.7 ms on the same scale.</figcaption></figure></div>")


def ledger_tables():
    out = []
    for f, name, colour, causes in FAMILIES:
        for c in sorted(causes, key=lambda c: -CCOUNT.get(c, 0)):
            cuts = [x for x in L if x["root_cause"] == c]
            if not cuts:
                continue
            rows = "".join(f"<tr><td>{html.escape(x['cut'])}</td><td>{html.escape(x['cost'])}</td><td>{html.escape(x['workload'])}</td>"
                           f"<td>{link(x['report'])}</td><td>{html.escape(x['status'])}</td></tr>" for x in cuts)
            out.append(f'<details class="ledger"><summary>{html.escape(name)}: {html.escape(c)} ({len(cuts)})</summary>'
                       '<table class="vals"><tr><th>the cut</th><th>what it costs</th><th>measured on</th><th>report</th><th>where it stands</th></tr>'
                       + rows + "</table></details>")
    return "\n".join(out)


NUMS = {"n_cuts": str(len(L)), "n_reports": str(len(REPORTS)), "n_fixed": str(COUNT["fixed"]), "n_mitigated": str(COUNT["mitigated"]),
        "n_openpr": str(COUNT["open PR"]), "n_open": str(COUNT["open"]), "n_other": str(COUNT["other"])}
for f, _, _, _ in FAMILIES:
    NUMS["f_" + f] = str(FCOUNT[f])
for k, (label, xs, run) in zip(("w0", "w1", "w2"), STEPS):
    NUMS[k + "_lo"], NUMS[k + "_hi"] = f"{min(xs) / 1000:.1f}", f"{max(xs) / 1000:.1f}"
NUMS["w2_x_lo"], NUMS["w2_x_hi"] = f"{min(STEPS[2][1]) / GOAL_MS:.0f}", f"{max(STEPS[2][1]) / GOAL_MS:.0f}"

body = open(os.path.join(HERE, "body.html")).read().replace("{{updated}}", updated)
FIGS = {"cuts": fig_cuts(), "witch": fig_witch(), "now": fig_now()}
# (the agenda, ^report(42), draws a report's figures on an item's card: each <svg> kept as 048/figs/NAME.html)
os.makedirs(os.path.join(HERE, "figs"), exist_ok=True)
for name, fig in FIGS.items():
    open(os.path.join(HERE, "figs", name + ".html"), "w").write(re.search(r"<svg.*?</svg>", fig, re.S).group(0) + "\n")
body = body.replace("{{fig_cuts}}", FIGS["cuts"]).replace("{{fig_witch}}", FIGS["witch"]).replace("{{fig_now}}", FIGS["now"])
body = body.replace("{{ledger}}", ledger_tables())
for k, v in NUMS.items():
    body = body.replace("{{" + k + "}}", v)
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>Why Hazel Is Slow: A Thousand Cuts</title>\n"
        "<meta name=\"description\" content=\"For Cyrus: the costs the report series has measured in Hazel, side by side, each with its number, where it was measured, whether it is fixed, and the design choice it comes from.\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
print("wrote 048/index.html; updated", updated, NUMS)
