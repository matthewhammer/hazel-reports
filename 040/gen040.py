#!/usr/bin/env python3
"""^report(40), Converting JS Values Directly: writes 040/index.html from body.html.

The numbers are 040/data/boundary.json: hazeljs's Boundary benchmark (bench/boundary.mjs),
run on GitHub, two rounds of four builds. Tables and Figure 1 are drawn here; {{name}} in
body.html is a figure, a table or a value. Then the series tools run over the page (build.sh)."""
import html, json, math, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
D = json.load(open(os.path.join(HERE, "data", "boundary.json")))
R = {(r["build"], r["kind"], r["n"]): r for r in D["rows"]}
SIZES = sorted({r["n"] for r in D["rows"]})


def esc(s):
    return html.escape(s, quote=True)


def ms(b, k, n):
    return R[(b, k, n)]["ms_mean"]


def mb(b, k, n):
    return R[(b, k, n)]["bytes_mean"] / 1e6


def f_ms(x):
    return f"{x:.3f}" if x < 0.1 else f"{x:.2f}" if x < 10 else f"{x:.1f}"


def f_mb(x):
    return f"{x * 1000:.0f} KB" if x < 1 else f"{x:.1f} MB"


def pct(a, b):
    return f"{(b - a) / a * 100:+.0f}%"


NAMES = {"base": "the package's build", "floor": "lib-floor", "closures": "lib-closures", "handles": "the handles trial"}


def table_time():
    o = ['<div class="scroll"><table>', "<tr><th>Cells</th><th>Call</th><th>The package's build</th><th>lib-floor</th><th>Change</th><th>lib-closures</th></tr>"]
    for n in SIZES:
        for k in ("typed", "untyped"):
            a, b, c = ms("base", k, n), ms("floor", k, n), ms("closures", k, n)
            o.append(f'<tr><td class="n">{n * n:,}</td><td>{k}</td><td class="n">{f_ms(a)} ms</td><td class="n">{f_ms(b)} ms</td>'
                     f'<td class="n"><b>{pct(a, b)}</b></td><td class="n">{f_ms(c)} ms</td></tr>')
    o.append("</table></div>")
    return "\n".join(o)


def table_space():
    o = ['<div class="scroll"><table>', "<tr><th>Cells</th><th>Call</th><th>The package's build</th><th>lib-floor</th><th>Change</th></tr>"]
    for n in SIZES:
        if n == 64:
            continue   # (the package's build allocates more than the young generation holds: a collection runs during the call)
        for k in ("typed", "untyped"):
            a, b = mb("base", k, n), mb("floor", k, n)
            o.append(f'<tr><td class="n">{n * n:,}</td><td>{k}</td><td class="n">{f_mb(a)}</td><td class="n">{f_mb(b)}</td><td class="n"><b>{pct(a, b)}</b></td></tr>')
    o.append("</table></div>")
    return "\n".join(o)


def table_held():
    o = ['<div class="scroll"><table>', "<tr><th>Numbers held</th>" + "".join(f"<th>{NAMES[b]}</th>" for b in ("base", "floor", "closures")) + "</tr>"]
    for n in SIZES:
        cells = "".join(f'<td class="n">{f_ms(ms(b, "held", n))} ms<br><span class="muted">{f_mb(mb(b, "held", n))}</span></td>' for b in ("base", "floor", "closures"))
        o.append(f'<tr><td class="n">{n * n:,}</td>{cells}</tr>')
    o.append("</table></div>")
    return "\n".join(o)


def table_handles():
    o = ['<div class="scroll"><table>', "<tr><th>Cells</th><th>Typed, converted each call</th><th>Typed, given a handle</th></tr>"]
    for n in SIZES:
        o.append(f'<tr><td class="n">{n * n:,}</td><td class="n">{f_ms(ms("handles", "typed", n))} ms</td><td class="n"><b>{f_ms(ms("handles", "typed, a handle", n))} ms</b></td></tr>')
    o.append("</table></div>")
    return "\n".join(o)


def fig_time():
    """ms a call against cells, both axes logarithmic: the package's build and lib-floor, typed and untyped"""
    W, H, L, B, T = 640, 300, 56, 40, 14
    xs = [n * n for n in SIZES]
    x0, x1 = math.log10(xs[0]) - 0.1, math.log10(xs[-1]) + 0.1
    y0, y1 = -1, math.log10(200)
    X = lambda v: L + (math.log10(v) - x0) / (x1 - x0) * (W - L - 150)
    Y = lambda v: T + (1 - (math.log10(v) - y0) / (y1 - y0)) * (H - T - B)
    o = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Milliseconds a call against the number of cells passed, on log scales: the package&#39;s build and lib-floor, each typed and untyped. lib-floor is below the package&#39;s build at every size.">']
    for v in (0.1, 1, 10, 100):
        o.append(f'<line x1="{L}" x2="{W - 150}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="var(--line)" stroke-width="1"/>'
                 f'<text x="{L - 6}" y="{Y(v) + 4:.1f}" font-size="11" text-anchor="end" fill="var(--muted)">{v:g} ms</text>')
    for v in xs:
        o.append(f'<text x="{X(v):.1f}" y="{H - B + 18}" font-size="11" text-anchor="middle" fill="var(--muted)">{v:,}</text>')
    o.append(f'<text x="{(L + W - 150) / 2:.0f}" y="{H - 6}" font-size="11.5" text-anchor="middle" fill="var(--muted)">cells passed from JavaScript</text>')
    series = [("base", "typed", "var(--accent2)", ""), ("base", "untyped", "var(--accent2)", "5 4"),
              ("floor", "typed", "var(--good)", ""), ("floor", "untyped", "var(--good)", "5 4")]
    for b, k, col, dash in series:
        pts = [(X(n * n), Y(ms(b, k, n))) for n in SIZES]
        o.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="2.2"'
                 + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")
        for x, y in pts:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{col}"/>')
        lx, ly = pts[-1]
        o.append(f'<text x="{lx + 8:.1f}" y="{ly + 4:.1f}" font-size="11.5" fill="{col}">{esc(NAMES[b])}, {k}</text>')
    o.append("</svg>")
    return "\n".join(o)


n64, n32 = SIZES[-1], 32
V = {"updated": subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip(),
     "t_typed_64": f_ms(ms("base", "typed", n64)), "f_typed_64": f_ms(ms("floor", "typed", n64)),
     "t_untyped_64": f_ms(ms("base", "untyped", n64)), "f_untyped_64": f_ms(ms("floor", "untyped", n64)),
     "p_typed_64": pct(ms("base", "typed", n64), ms("floor", "typed", n64)), "p_untyped_64": pct(ms("base", "untyped", n64), ms("floor", "untyped", n64)),
     "a_typed_32": f_mb(mb("base", "typed", n32)), "af_typed_32": f_mb(mb("floor", "typed", n32)),
     "a_untyped_32": f_mb(mb("base", "untyped", n32)), "af_untyped_32": f_mb(mb("floor", "untyped", n32)),
     "h_base_64": f_ms(ms("base", "held", n64)), "h_base_mb_64": f_mb(mb("base", "held", n64)),
     "h_clo_64": f_ms(ms("closures", "held", n64)), "h_clo_mb_64": f_mb(mb("closures", "held", n64)),
     "h_ratio": f'{ms("base", "held", n64) / ms("closures", "held", n64):.0f}',
     "hd_64": f_ms(ms("handles", "typed, a handle", n64)), "hd_conv_64": f_ms(ms("handles", "typed", n64)),
     "ratio_typed": f'{ms("floor", "typed", n64) / ms("floor", "untyped", n64):.1f}',
     "cells_64": f"{n64 * n64:,}"}
FIGS = {"FIG_TIME": fig_time(), "TABLE_TIME": table_time(), "TABLE_SPACE": table_space(), "TABLE_HELD": table_held(), "TABLE_HANDLES": table_handles()}
BODY = open(os.path.join(HERE, "body.html")).read()
BODY = re.sub(r"\{\{(\w+)\}\}", lambda m: FIGS.get(m.group(1)) or V[m.group(1)], BODY)
HEAD = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Converting JS Values Directly</title>
<meta name="description" content="What converting JavaScript values directly into Hazel values saves at the call boundary of Hazel's JS library, in time and in space: the package's build against the lib-floor, lib-closures and handles trials, measured on GitHub.">
<style>{CSS}
  .muted {{ color: var(--muted); font-size: 0.9em; }}
</style>
</head>
"""
open(os.path.join(HERE, "index.html"), "w").write(HEAD + BODY)
print("wrote 040/index.html;", ", ".join(f"{k}={v}" for k, v in V.items() if k in ("updated", "p_typed_64", "p_untyped_64", "h_ratio")))
