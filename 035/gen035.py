#!/usr/bin/env python3
"""^report(35), Paying Only for What Is Watched: writes 035/index.html.

The figures come from ^report(29)'s profiles (029/data/prof_*.json) and its
fast-path table (029/data/tables.json), so the numbers here are the ones
measured there. Then the series tools run over the page (see build.sh)."""
import html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
R29 = os.path.join(ROOT, "029", "data")

# the stylesheet is ^report(34)'s, so the series reads as one
s34 = open(os.path.join(ROOT, "034", "index.html")).read()
CSS = s34[s34.index("<style>") + 7: s34.index("</style>")]

prof = {k: json.load(open(os.path.join(R29, f"prof_{k}.json"))) for k in ("count_5000", "h_ref_3000", "sumbuild_1000")}

# each profile group: a short name, a colour, and which ideas aim at it
GROUPS = [
    ("the evaluator's stages", "stages", "var(--accent)", "1 2 3 6"),
    ("trampolines", "trampolines", "var(--accent2)", "1 2 3 4"),
    ("garbage collection", "garbage collection", "var(--warn)", "4"),
    ("fresh ids", "fresh ids", "var(--bad)", "5"),
    ("pushing types", "pushing types", "#a16207", ""),
    ("terms and their ids", "terms", "#64748b", ""),
    ("environments", "environments", "#0f766e", ""),
    ("the step's rule", "the rule", "var(--good)", ""),
    ("everything else", "else", "var(--cx)", ""),
]


def share(p, key):
    for g in p["groups"]:
        if g["group"].startswith(key):
            return g["share"]
    return 0.0


def bars():
    rows = [("count_5000", "count(5000), a loop"), ("sumbuild_1000", "sumbuild(1000), a list built and summed"),
            ("h_ref_3000", "h_ref, one reference to a held list of 3,000")]
    W, X0, BH, GAP = 900, 0, 34, 30
    out = [f'<svg viewBox="0 0 {W} {len(rows) * (BH + GAP) + 50}" width="100%" role="img" aria-label="Three stacked bars, where each program\'s time goes">']
    y = 18
    for key, label in rows:
        p = prof[key]
        out.append(f'<text x="0" y="{y - 5}" font-size="13" fill="var(--ink)">{html.escape(label)} · {p["total_ms"]:,.0f} ms profiled</text>')
        x = X0
        for gk, short, col, _ in GROUPS:
            w = share(p, gk) * W
            if w <= 0:
                continue
            out.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{BH}" fill="{col}" opacity="0.85"><title>{short}: {share(p, gk) * 100:.1f}%</title></rect>')
            if w > 7.2 * len(short) + 8:
                out.append(f'<text x="{x + 5:.1f}" y="{y + 15}" font-size="11.5" fill="#fff">{short}</text>'
                           f'<text x="{x + 5:.1f}" y="{y + 29}" font-size="11.5" font-weight="600" fill="#fff">{share(p, gk) * 100:.0f}%</text>')
            elif w > 26:
                out.append(f'<text x="{x + 3:.1f}" y="{y + 22}" font-size="11" font-weight="600" fill="#fff">{share(p, gk) * 100:.0f}</text>')
            x += w
        y += BH + GAP
    # the key: each group's colour, and which ideas aim at it
    kx, ky = 0, y - 6
    for gk, short, col, ideas in GROUPS[:4]:
        out.append(f'<rect x="{kx}" y="{ky}" width="12" height="12" fill="{col}" opacity="0.85"/>'
                   f'<text x="{kx + 17}" y="{ky + 11}" font-size="12" fill="var(--ink)">{short}: idea{"s" if " " in ideas else ""} {ideas.replace(" ", ", ")}</text>')
        kx += 225
    out.append("</svg>")
    return "\n".join(out)


def loop_mini():
    # count(5000) in four parts, big enough to read at the short answers' width
    p = prof["count_5000"]
    sg = lambda *ks: sum(share(p, k) for k in ks)
    parts = [("the rule", sg("the step's rule"), "var(--good)"), ("stages + trampolines", sg("the evaluator's stages", "trampolines"), "var(--accent)"),
             ("garbage", sg("garbage collection"), "var(--warn)")]
    parts.append(("the rest", 1 - sum(v for _, v, _ in parts), "var(--cx)"))
    W, out, x = 300, [], 0
    out.append(f'<svg viewBox="0 0 {W} 92" width="100%" role="img" aria-label="A loop: the rule 7%, stages and trampolines 37%, garbage collection 36%, the rest 20%">')
    out.append('<text x="0" y="12" font-size="12" fill="var(--ink)">count(5000), a loop: where a call\'s time goes</text>')
    for i, (name, v, col) in enumerate(parts):
        w = v * W
        out.append(f'<rect x="{x:.1f}" y="20" width="{w:.1f}" height="30" fill="{col}" opacity="0.85"/>')
        if w >= 30:
            out.append(f'<text x="{x + 3:.1f}" y="40" font-size="13" font-weight="700" fill="#fff">{v * 100:.0f}%</text>')
        ty = 66 if i % 2 == 0 else 84
        out.append(f'<text x="{x + 2:.1f}" y="{ty}" font-size="11.5" fill="var(--ink)">{name}{"" if w >= 30 else f" {v * 100:.0f}%"}</text>')
        x += w
    out.append("</svg>")
    return "\n".join(out)


def fastpath_mini():
    # ^report(29) #fix-fast-path's table: count(1000) and h_ref(3000), passes and ms, before and after
    pts = [("count(1000) passes", 14009, 9007, ""), ("count(1000) ms", 39.2, 36.2, " ms"), ("h_ref(3,000) ms", 3.9, 0.122, " ms")]
    W, out, y = 300, [], 6
    out.append(f'<svg viewBox="0 0 {W} 150" width="100%" role="img" aria-label="Before and after the fast path">')
    for name, a, b, u in pts:
        out.append(f'<text x="0" y="{y + 10}" font-size="11.5" fill="var(--ink)">{name}</text>')
        fa = lambda v: f"{v:,.0f}" if v >= 100 else (f"{v:g}")
        out.append(f'<rect x="0" y="{y + 15}" width="{W - 70}" height="10" fill="var(--cx)"/><text x="{W - 64}" y="{y + 24}" font-size="11" fill="var(--muted)">{fa(a)}{u}</text>')
        out.append(f'<rect x="0" y="{y + 28}" width="{max(2, (W - 70) * b / a):.1f}" height="10" fill="var(--good)"/><text x="{max(2, (W - 70) * b / a) + 6:.1f}" y="{y + 37}" font-size="11" font-weight="600" fill="var(--good)">{fa(b)}{u}</text>')
        y += 48
    out.append("</svg>")
    return "\n".join(out)


BODY = open(os.path.join(HERE, "body.html")).read().replace("{{FIG_BARS}}", bars()).replace("{{FIG_FAST}}", fastpath_mini()).replace("{{FIG_LOOP}}", loop_mini())
HEAD = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Paying Only for What Is Watched</title>
<meta name="description" content="Hazel's evaluator pays for its live features (probes, the stepper, results kept across edits) on every pass, even where none is in use. Eight ways to stop paying for them there, each with what it saves, what it would cost the features, and how much code it touches.">
<style>{CSS}
  table.ideas td:first-child {{ font-weight: 600; white-space: nowrap; }}
  .meas {{ color: var(--good); font-weight: 600; }} .est {{ color: var(--warn); font-weight: 600; }}
</style>
</head>
"""
open(os.path.join(HERE, "index.html"), "w").write(HEAD + BODY)
print("wrote 035/index.html")
