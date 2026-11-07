#!/usr/bin/env python3
"""^report(45), hazel-jit: writes 045/index.html from body.html, with the series' styles (035's) and figures drawn from
045/data/timings.json (each run's reading, from Test_HazelJit's timing tests). Placeholders in body.html: {{updated}},
{{fig_speed}}, {{fig_boundary}}, {{fig_how}}, and {{n:KEY}} for a number (see NUMS)."""
import json, os, subprocess, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
EXTRA = """
  ol.outline > li { margin: 4px 0; } .muted { color: var(--muted); }
  table.vals td:first-child { white-space: nowrap; }
  pre.code { background: color-mix(in srgb, var(--line) 35%, transparent); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px;
             overflow-x: auto; font-size: 0.84em; line-height: 1.45; max-width: 100%; }
  pre.code code { background: none; padding: 0; font-size: inherit; overflow-wrap: normal; white-space: pre; }
"""

T = json.load(open(os.path.join(HERE, "data", "timings.json")))
med = lambda xs: sorted(xs)[len(xs) // 2]   # (as the tests print it: the upper middle of the sorted runs)
runs = {r["name"]: r for r in T["runs"]}
poly = runs["the Polygons view through the boundary"]
petri = runs["the Petri net rule, four events"]
rsum = runs["a recursive sum of 1,000"]
pview = runs["the Polygons slide's view"]

def ms(x, d=None):
    if d is None:
        d = 1 if x >= 10 else 2 if x >= 0.1 else 3 if x >= 0.01 else 4
    return f"{x:.{d}f}"

NUMS = {
    "poly_interp": ms(med(poly["interpreter_ms"])),
    "poly_through": ms(med(poly["through_boundary_ms"])),
    "poly_call": ms(med(poly["call_alone_ms"])),
    "poly_cross": ms(med(poly["through_boundary_ms"]) - med(poly["call_alone_ms"])),
    "poly_cross_share": f"{100 * (med(poly['through_boundary_ms']) - med(poly['call_alone_ms'])) / med(poly['through_boundary_ms']):.0f}",
    "poly_x": f"{med(poly['interpreter_ms']) / med(poly['through_boundary_ms']):.0f}",
    "poly_call_x": f"{med(poly['interpreter_ms']) / med(poly['call_alone_ms']):.0f}",
    "poly_compile": ms(poly["compile_ms"][0]),
    "pview_interp": ms(med(pview["interpreter_ms"])),
    "pview_jit": ms(med(pview["compiled_ms"])),
    "pview_x": f"{med(pview['interpreter_ms']) / med(pview['compiled_ms']):.0f}",
    "petri_interp": ms(med(petri["interpreter_ms"])),
    "petri_jit": ms(med(petri["compiled_ms"])),
    "petri_x": f"{med(petri['interpreter_ms']) / med(petri['compiled_ms']):.0f}",
    "sum_interp": ms(med(rsum["interpreter_ms"])),
    "sum_jit": ms(med(rsum["compiled_ms"])),
    "sum_x": f"{med(rsum['interpreter_ms']) / med(rsum['compiled_ms']):,.0f}",
    "n": str(len(poly["interpreter_ms"])),
    # (Matthew, 2026-11-06: which trip costs more) each trip timed alone, and its share of a compiled render
    "poly_in": ms(med(poly["trip_in_ms"])),
    "poly_back": ms(med(poly["trip_back_ms"])),
    "poly_in_share": f"{100 * med(poly['trip_in_ms']) / med(poly['through_boundary_ms']):.0f}",
    "poly_back_share": f"{100 * med(poly['trip_back_ms']) / med(poly['through_boundary_ms']):.0f}",
    "poly_call_share": f"{100 * med(poly['call_alone_ms']) / med(poly['through_boundary_ms']):.0f}",
    "poly_back_x": f"{med(poly['trip_back_ms']) / med(poly['trip_in_ms']):.0f}",
    "poly_back_vs_call": f"{med(poly['trip_back_ms']) / med(poly['call_alone_ms']):.0f}",
    "poly_parts": ms(med(poly["trip_in_ms"]) + med(poly["call_alone_ms"]) + med(poly["trip_back_ms"])),
    # the first renders after compiling, before Node has optimized the way back
    "poly_first": ms(med(poly["through_boundary_first_ms"])),
    "poly_first_x": f"{med(poly['interpreter_ms']) / med(poly['through_boundary_first_ms']):.0f}",
    "poly_first_1": ms(poly["through_boundary_first_ms"][0]),
    "poly_first_last5": ms(med(poly["through_boundary_first_ms"][-5:])),
}
CENSUS = poly.get("census", {})
for side in ("model", "answer"):
    for k, v in CENSUS.get(side, {}).items():
        NUMS[f"{side}_{k}"] = f"{v:,}"
NUMS.update({
    "answer_x_model": f"{CENSUS['answer']['visits'] / CENSUS['model']['visits']:.1f}",
    "terms_made": f"{CENSUS['terms_made']:,}",
    "poly_ids": ms(med(poly["fresh_ids_ms"])),
    "poly_ids_share": f"{100 * med(poly['fresh_ids_ms']) / med(poly['trip_back_ms']):.0f}",
    "us_in": f"{1000 * med(poly['trip_in_ms']) / CENSUS['model']['visits']:.2f}",
    "us_back": f"{1000 * med(poly['trip_back_ms']) / CENSUS['answer']['visits']:.2f}",
    "us_id": f"{1000 * med(poly['fresh_ids_ms']) / CENSUS['terms_made']:.2f}",
})


def text(x, y, s, size=12, anchor="start", fill="var(--ink)", weight="400"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" '
            f'font-weight="{weight}">{s}</text>')


def fig_speed():
    """Each program's time per run, interpreter and compiled, on a log scale: one row per measure."""
    import math
    rows = [
        ("A Polygons render", [
            ("the interpreter", med(poly["interpreter_ms"]), "var(--muted)"),
            ("compiled, its first " + NUMS["n"] + " renders", med(poly["through_boundary_first_ms"]), "var(--accent2)"),
            ("compiled, with the trip in and out", med(poly["through_boundary_ms"]), "var(--accent2)"),
            ("the compiled call alone", med(poly["call_alone_ms"]), "var(--accent)"),
        ]),
        ("The Petri net rule, four events", [
            ("the interpreter", med(petri["interpreter_ms"]), "var(--muted)"),
            ("compiled", med(petri["compiled_ms"]), "var(--accent)"),
        ]),
        ("A recursive sum of 1,000", [
            ("the interpreter", med(rsum["interpreter_ms"]), "var(--muted)"),
            ("compiled", med(rsum["compiled_ms"]), "var(--accent)"),
        ]),
    ]
    W, left, right = 940, 250, 120
    lo, hi = math.log10(0.005), math.log10(100)
    xof = lambda v: left + (math.log10(v) - lo) / (hi - lo) * (W - left - right)
    out, y = [], 34
    nbars = sum(len(b) for _, b in rows)
    bottom = 26 + (nbars + 2) * 22 + len(rows) * 16
    out.append(text(16, 18, "Time per run, ms (a log scale: each step to the right is ten times as long)", 12.5, weight="700"))
    for tick in (0.01, 0.1, 1, 10, 100):
        x = xof(tick)
        out.append(f'<line x1="{x:.1f}" y1="26" x2="{x:.1f}" y2="{bottom:.0f}" stroke="var(--line)" stroke-width="1"/>')
        out.append(text(x, bottom + 14, f"{tick:g} ms", 11, "middle", "var(--muted)"))
    for title, bars in rows:
        y += 4
        out.append(text(16, y + 10, title, 12, weight="700"))
        y += 16
        for label, v, colour in bars:
            x = xof(v)
            out.append(text(left - 8, y + 12, label, 11.5, "end", "var(--muted)"))
            out.append(f'<rect x="{left}" y="{y + 2}" width="{max(2, x - left):.1f}" height="14" rx="3" fill="{colour}" opacity="0.85"/>')
            out.append(text(x + 6, y + 13, ms(v) + " ms", 11.5, "start", "var(--ink)", "700"))
            y += 22
    h = bottom + 24
    alt = ("Time per run on a log scale. A Polygons render: the interpreter " + NUMS["poly_interp"] + " ms, compiled, its first " + NUMS["n"]
           + " renders " + NUMS["poly_first"] + " ms, compiled once warm with the trip in and out "
           + NUMS["poly_through"] + " ms, the compiled call alone " + NUMS["poly_call"] + " ms. The Petri net rule: " + NUMS["petri_interp"] + " ms against "
           + NUMS["petri_jit"] + " ms. A recursive sum: " + NUMS["sum_interp"] + " ms against " + NUMS["sum_jit"] + " ms.")
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{alt}" '
            f'style="width:100%;height:auto;display:block">' + "".join(out) + "</svg><figcaption>Medians of "
            + NUMS["n"] + " runs each, in Node 22, from a development build of <code>trial/694-view-jit</code> (" + T["commit"]
            + "), on one laptop. The compiled times count the compiled code only; the Polygons render is also shown with the model carried in and its answer carried back: "
            "its first " + NUMS["n"] + " renders after compiling, and " + NUMS["n"] + " more once warm (after 10 untimed).</figcaption></figure></div>")


def fig_boundary():
    """The compiled path of a Polygons render, split three ways, each timed alone: the trip in, the call, the trip back.
    The three are drawn to scale against the whole render's median, so any time not in them shows as a gap at the end."""
    W = 940
    total = med(poly["through_boundary_ms"])
    parts = [("in", med(poly["trip_in_ms"]), "var(--accent2)", "0.55"),
             ("call", med(poly["call_alone_ms"]), "var(--accent)", "0.9"),
             ("back", med(poly["trip_back_ms"]), "var(--accent2)", "0.85")]
    scale = max(total, sum(p[1] for p in parts))
    left, width = 16, W - 32
    out = [text(16, 18, "One Polygons render, compiled: " + ms(total) + " ms in all, its three steps each timed alone", 12.5, weight="700")]
    x = left
    for name, v, colour, op in parts:
        w = width * v / scale
        out.append(f'<rect x="{x:.1f}" y="30" width="{max(w, 2):.1f}" height="34" rx="4" fill="{colour}" opacity="{op}"/>')
        x += w
    out.append(f'<rect x="{left}" y="30" width="{width * total / scale:.1f}" height="34" rx="4" fill="none" stroke="var(--ink)" stroke-width="1" stroke-dasharray="4 3"/>')
    out.append(text(left, 86, "the model into JS (to_js): " + NUMS["poly_in"] + " ms (" + NUMS["poly_in_share"] + "%)", 12, "start", "var(--ink)", "700"))
    out.append(text(left, 104, "the compiled view: " + NUMS["poly_call"] + " ms (" + NUMS["poly_call_share"] + "%)", 12, "start", "var(--ink)", "700"))
    out.append(text(left + width, 86, "the answer back as Hazel (of_js): " + NUMS["poly_back"] + " ms (" + NUMS["poly_back_share"] + "%)", 12, "end", "var(--ink)", "700"))
    out.append(text(left + width, 104, "dashed: the whole render, timed in one go", 11.5, "end", "var(--muted)"))
    alt = (f"One compiled Polygons render takes {ms(total)} ms. Timed alone, the model into JS takes {NUMS['poly_in']} ms, the compiled view "
           f"{NUMS['poly_call']} ms, and the answer back as a Hazel value {NUMS['poly_back']} ms.")
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} 116" role="img" aria-label="{alt}" '
            'style="width:100%;height:auto;display:block">' + "".join(out) + "</svg><figcaption>The same session as above, medians of "
            + NUMS["n"] + " runs each: the trip in on the slide's model, the call on that model already in JS, and the trip back on that call's "
            "answer. Percentages are of the whole render's median.</figcaption></figure></div>")


def box(x, y, w, h, title, sub, stroke="var(--line)"):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="var(--paper)" stroke="{stroke}" stroke-width="1.6"/>'
            + text(x + w / 2, y + h / 2 - 2, title, 12.5, "middle", "var(--ink)", "700")
            + text(x + w / 2, y + h / 2 + 14, sub, 11.5, "middle", "var(--muted)"))


def arrow(x1, y1, x2, y2, colour="var(--muted)"):
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - 8 * math.cos(a - 0.45), y2 - 8 * math.sin(a - 0.45))
    p2 = (x2 - 8 * math.cos(a + 0.45), y2 - 8 * math.sin(a + 0.45))
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colour}" stroke-width="1.8"/>'
            f'<path d="M{p1[0]:.1f} {p1[1]:.1f} L{x2} {y2} L{p2[0]:.1f} {p2[1]:.1f}" fill="none" stroke="{colour}" stroke-width="1.8" stroke-linejoin="round"/>')


def fig_how():
    """What runs where: compile once per definition; each render, the model in, the call, the answer back."""
    out = [text(16, 18, "A livelit's view with hazel-jit: compiled once, run on each model", 12.5, weight="700"),
           text(16, 46, "once per definition", 11.5, "start", "var(--accent2)", "700"),
           box(16, 54, 170, 56, "the definition", "elaborated Hazel"),
           box(226, 54, 210, 56, "HazelJit.compile_full", "Hazel to JS source text", "var(--accent2)"),
           box(476, 54, 200, 56, "a JS function", "new Function, cached", "var(--accent2)"),
           box(716, 54, 208, 56, "and what the way back reads", "constructor types, functions"),
           arrow(186, 82, 222, 82, "var(--accent2)"), arrow(436, 82, 472, 82, "var(--accent2)"), arrow(676, 82, 712, 82),
           text(16, 150, "each render", 11.5, "start", "var(--accent)", "700"),
           box(16, 158, 150, 56, "the model", "a Hazel value"),
           box(196, 158, 140, 56, "to_js", "into JS values", "var(--accent)"),
           box(366, 158, 140, 56, "view(model)", "the compiled call", "var(--accent)"),
           box(536, 158, 150, 56, "of_js", "back, by the types", "var(--accent)"),
           box(716, 158, 208, 56, "a ViewCmd, then Html", "ViewCmdRunner, as today"),
           arrow(166, 186, 192, 186, "var(--accent)"), arrow(336, 186, 362, 186, "var(--accent)"),
           arrow(506, 186, 532, 186, "var(--accent)"), arrow(686, 186, 712, 186),
           arrow(576, 110, 576, 154), arrow(820, 110, 650, 154),
           text(16, 240, "Anything hazel-jit cannot compile, or carry back, runs on the interpreter as before; the console says why, once.", 11.5, "start", "var(--muted)")]
    alt = ("Once per definition, HazelJit compiles the elaborated definition to JS source, made into a cached JS function, with the constructor "
           "types and function table the way back reads. Each render: the model goes into JS (to_js), the compiled view is called, the answer "
           "comes back as a Hazel value (of_js), and ViewCmdRunner draws it as today.")
    return ('<div class="figrow"><figure class="f wide"><svg viewBox="0 0 940 250" role="img" aria-label="' + alt
            + '" style="width:100%;height:auto;display:block">' + "".join(out) + "</svg><figcaption>What runs where, in "
            "<code>LivelitProj.eval_view</code> since " + T["commit"] + ".</figcaption></figure></div>")


updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
body = open(os.path.join(HERE, "body.html")).read()
body = body.replace("{{updated}}", updated).replace("{{fig_speed}}", fig_speed()).replace("{{fig_boundary}}", fig_boundary())
body = body.replace("{{fig_how}}", fig_how())
for k, v in NUMS.items():
    body = body.replace("{{n:" + k + "}}", v)
assert "{{" not in body, body[body.index("{{"):body.index("{{") + 40]
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>hazel-jit: Livelit Views Compiled to JavaScript</title>\n"
        "<meta name=\"description\" content=\"How much faster a livelit's view runs as JavaScript compiled from its Hazel: the compiler, the trip in and out, "
        "what it does in the app, and where the time goes now. Work in progress.\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
print("wrote 045/index.html; updated", updated)
