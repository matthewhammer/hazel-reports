#!/usr/bin/env python3
"""^report(36), What an Undo Costs: writes 036/index.html from body.html.

Every figure is drawn from 036/data: steps.json (drivers/medians.py over the
probe's runs in data/runs/) and profile_3200.json (the two profiles, read
with drivers/prof.py). {{name}} in body.html is a figure or a number from
them. Then the series tools run over the page (see build.sh)."""
import html, json, math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")

s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]

steps = json.load(open(os.path.join(DATA, "steps.json")))
prof = json.load(open(os.path.join(DATA, "profile_3200.json")))
MED = {(r["build"], r["n"], r["kind"]): r for r in steps}
SIZES = sorted({r["n"] for r in steps})
KINDS = [("edit", "an edit", "var(--accent2)"), ("undo", "an undo", "var(--accent)"), ("redo", "a redo", "var(--warn)")]
COL = {k: c for k, _, c in KINDS}


def med(b, n, k):
    return MED[(b, n, k)]["step_median_ms"]


def stat(b, n):
    # the statics refresh after a step: the median over all three kinds' samples
    xs = sorted(s["refresh_ms"] for k, _, _ in KINDS for s in MED[(b, n, k)]["samples"])
    m = len(xs)
    return (xs[m // 2] + xs[(m - 1) // 2]) / 2


def fmt(v):
    return f"{v:,.0f}" if v >= 20 else f"{v:.1f}".rstrip("0").rstrip(".")


def slope(b, k, lo, hi):
    return math.log(med(b, hi, k) / med(b, lo, k)) / math.log(hi / lo)


def esc(s):
    return html.escape(s, quote=True)


# --- Figure 1: three panels, log-log, before (grey, dashed) and after (coloured) ---

def scale_panel(k, label, col, x0, W=290, H=250, mini=False):
    L, R, T, B = 44, 12, 26, 36
    ymin, ymax = 5, 600
    X = lambda n: x0 + L + (math.log2(n / SIZES[0]) / math.log2(SIZES[-1] / SIZES[0])) * (W - L - R)
    Y = lambda v: T + (1 - (math.log10(v / ymin) / math.log10(ymax / ymin))) * (H - T - B)
    o = [f'<text x="{x0 + L}" y="14" font-size="13" font-weight="700" fill="{col}">{label}</text>']
    for v in (10, 30, 100, 300):
        o.append(f'<line x1="{x0 + L}" x2="{x0 + W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="var(--line)"/>'
                 f'<text x="{x0 + L - 5}" y="{Y(v) + 4:.1f}" font-size="10.5" text-anchor="end" fill="var(--muted)">{v} ms</text>')
    for n in SIZES:
        o.append(f'<text x="{X(n):.1f}" y="{H - B + 15}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{n:,}</text>')
    o.append(f'<text x="{x0 + L + (W - L - R) / 2:.1f}" y="{H - 4}" font-size="10.5" text-anchor="middle" fill="var(--muted)">definitions in the program</text>')
    # what O(log n) would look like from the first point: a guide, not a measurement
    a0 = med("B", SIZES[0], k)
    guide = " ".join(f"{X(n):.1f},{Y(a0 * math.log(n) / math.log(SIZES[0])):.1f}" for n in SIZES)
    o.append(f'<polyline points="{guide}" fill="none" stroke="var(--good)" stroke-width="1.5" stroke-dasharray="2 4"/>'
             f'<text x="{X(SIZES[-1]) - 2:.1f}" y="{Y(a0 * math.log(SIZES[-1]) / math.log(SIZES[0])) + 14:.1f}" font-size="10.5" text-anchor="end" fill="var(--good)">if it grew as log n</text>')
    for b, c, dash, w in (("A", "var(--muted)", ' stroke-dasharray="5 4"', 1.6), ("B", col, "", 2.6)):
        pts = " ".join(f"{X(n):.1f},{Y(med(b, n, k)):.1f}" for n in SIZES)
        o.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="{w}"{dash}/>')
        for n in SIZES:
            v = med(b, n, k)
            o.append(f'<circle cx="{X(n):.1f}" cy="{Y(v):.1f}" r="{3.2 if b == "B" else 2.6}" fill="{c}"><title>{"before" if b == "A" else "after"} the fixes, {n:,} definitions: {fmt(v)} ms</title></circle>')
            if not mini:
                dy = -7 if b == "A" else 15
                fw = ' font-weight="700"' if b == "B" else ""
                o.append(f'<text x="{X(n):.1f}" y="{Y(v) + dy:.1f}" font-size="{10 if b == "A" else 11}" text-anchor="middle" '
                         f'fill="{c}"{fw}>{fmt(v)}</text>')
    return "\n".join(o)


def fig_scale():
    W = 900
    o = [f'<svg viewBox="0 0 {W} 272" width="100%" role="img" aria-label="Three log-log plots, edit, undo and redo time against program size from 400 to 6,400 definitions, before and after the fixes; every line rises in proportion to the program">']
    for i, (k, label, col) in enumerate(KINDS):
        o.append(scale_panel(k, label, col, i * 300))
    o.append(f'<line x1="44" x2="70" y1="266" y2="266" stroke="var(--muted)" stroke-width="1.6" stroke-dasharray="5 4"/><text x="76" y="270" font-size="11" fill="var(--muted)">before the fixes (2cab658ef1)</text>'
             f'<line x1="260" x2="286" y1="266" y2="266" stroke="var(--ink)" stroke-width="2.6"/><text x="292" y="270" font-size="11" fill="var(--ink)">after (bfa36a6ede)</text>')
    o.append("</svg>")
    return "\n".join(o)


def mini_scale():
    # the three "after" lines on one plot, at the short answers' width
    W, H, L, R, T, B = 300, 168, 40, 52, 10, 30
    ymin, ymax = 5, 600
    X = lambda n: L + (math.log2(n / SIZES[0]) / math.log2(SIZES[-1] / SIZES[0])) * (W - L - R)
    Y = lambda v: T + (1 - (math.log10(v / ymin) / math.log10(ymax / ymin))) * (H - T - B)
    o = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="After the fixes: edit, undo and redo time rise in proportion to the program, 400 to 6,400 definitions">']
    for v in (10, 100):
        o.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="var(--line)"/><text x="{L - 4}" y="{Y(v) + 4:.1f}" font-size="10" text-anchor="end" fill="var(--muted)">{v} ms</text>')
    for n in (SIZES[0], SIZES[-1]):
        o.append(f'<text x="{X(n):.1f}" y="{H - B + 14}" font-size="10" text-anchor="middle" fill="var(--muted)">{n:,}</text>')
    o.append(f'<text x="{(L + W - R) / 2:.1f}" y="{H - 3}" font-size="10" text-anchor="middle" fill="var(--muted)">definitions</text>')
    for k, label, col in KINDS:
        pts = " ".join(f"{X(n):.1f},{Y(med('B', n, k)):.1f}" for n in SIZES)
        v = med("B", SIZES[-1], k)
        o.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.4"/>' +
                 "".join(f'<circle cx="{X(n):.1f}" cy="{Y(med("B", n, k)):.1f}" r="2.6" fill="{col}"/>' for n in SIZES) +
                 f'<text x="{X(SIZES[-1]) + 6:.1f}" y="{Y(v) + {"undo": 2, "redo": 1, "edit": 9}[k]:.1f}" font-size="10.5" font-weight="700" fill="{col}">{k} {fmt(v)}</text>')
    o.append("</svg>")
    return "\n".join(o)


# --- Figure 3: where the time goes, two stacked bars ---

GROUPS = [("term", "the top-level term", "var(--accent2)"), ("statics", "statics' chain", "var(--accent)"),
          ("outline", "the outline", "var(--warn)"), ("root", "auto-probe root", "var(--bad)"),
          ("tydi", "completions", "#a16207"), ("rest", "the rest", "var(--cx)")]


def parts(which):
    tot = prof["total_ms"][which]
    g = {x["key"]: x[f"{which}_ms"] for x in prof["groups"]}
    g["rest"] = tot - sum(g.values())
    return tot, [(k, lab, col, g[k]) for k, lab, col in GROUPS]


def fig_where():
    W, BH = 900, 40
    o = [f'<svg viewBox="0 0 {W} 210" width="100%" role="img" aria-label="Two stacked bars of profiled time at 3,200 definitions, before and after the fixes: the auto-probe root and completions are gone after; the top-level term, statics, the outline and the rest remain">']
    full = prof["total_ms"]["before"]
    y = 20
    for which, title in (("before", "before the fixes"), ("after", "after")):
        tot, ps = parts(which)
        o.append(f'<text x="0" y="{y - 6}" font-size="13" fill="var(--ink)">{title} · {tot:,} ms profiled, 12 steps and their statics</text>')
        x = 0.0
        for k, lab, col, ms in ps:
            w = ms / full * W
            if w <= 0:
                continue
            o.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{BH}" fill="{col}" opacity="0.88"><title>{lab}: {ms:,} ms, {ms / tot * 100:.0f}%</title></rect>')
            fg = "var(--ink)" if k == "rest" else "#fff"
            if w > 7 * len(lab) + 10:
                o.append(f'<text x="{x + 5:.1f}" y="{y + 16}" font-size="11.5" fill="{fg}">{lab}</text>'
                         f'<text x="{x + 5:.1f}" y="{y + 32}" font-size="11.5" font-weight="700" fill="{fg}">{ms:,} ms · {ms / tot * 100:.0f}%</text>')
            elif w > 30:
                o.append(f'<text x="{x + 4:.1f}" y="{y + 25}" font-size="11" font-weight="700" fill="{fg}">{ms / tot * 100:.0f}%</text>')
            x += w
        y += BH + 44
    kx = 0
    for k, lab, col in GROUPS:
        o.append(f'<rect x="{kx}" y="{y - 22}" width="12" height="12" fill="{col}" opacity="0.88"/><text x="{kx + 17}" y="{y - 12}" font-size="11.5" fill="var(--ink)">{lab}</text>')
        kx += 17 + 7.2 * len(lab) + 22
    o.append("</svg>")
    return "\n".join(o)


def mini_where():
    tot, ps = parts("after")
    W = 300
    o = [f'<svg viewBox="0 0 {W} 96" width="100%" role="img" aria-label="After the fixes, at 3,200 definitions: top-level term 38%, statics 20%, the outline 15%, the rest 27%">',
         '<text x="0" y="12" font-size="11.5" fill="var(--ink)">3,200 definitions: where a step\'s time goes</text>']
    x, i = 0.0, 0
    for k, lab, col, ms in ps:
        if ms <= 0:
            continue
        w = ms / tot * W
        o.append(f'<rect x="{x:.1f}" y="20" width="{w:.1f}" height="30" fill="{col}" opacity="0.88"/>')
        if w > 30:
            o.append(f'<text x="{x + 3:.1f}" y="40" font-size="12.5" font-weight="700" fill="{"var(--ink)" if k == "rest" else "#fff"}">{ms / tot * 100:.0f}%</text>')
        o.append(f'<text x="{x + 2:.1f}" y="{66 if i % 2 == 0 else 84}" font-size="11" fill="var(--ink)">{lab}</text>')
        x += w
        i += 1
    o.append("</svg>")
    return "\n".join(o)


# --- Figure 4: an edit, a redo and an undo at one size, the outline's share marked ---

def outline_ms():
    # the outline's profiled time per undo or redo step at 3,200 (8 of the 12 steps build it)
    return prof["groups"][[g["key"] for g in prof["groups"]].index("outline")]["after_ms"] / 8


def bars_twice(W=300, n=3200, big=False):
    rows = [("edit", "an edit"), ("redo", "a redo"), ("undo", "an undo")]
    top = max(med("B", n, k) + stat("B", n) for k, _ in rows)
    L, BW = (70, 26) if big else (58, 20)
    span = W - L - 60
    o = [f'<svg viewBox="0 0 {W} {len(rows) * (BW + 14) + 34}" width="100%" role="img" aria-label="At {n:,} definitions after the fixes: an edit, a redo and an undo, each with its statics refresh; the outline is part of the redo and the undo">']
    y = 6
    om = outline_ms()
    for k, lab in rows:
        v, st = med("B", n, k), stat("B", n)
        w = v / top * span
        o.append(f'<text x="{L - 6}" y="{y + BW / 2 + 4:.1f}" font-size="{12 if big else 11}" text-anchor="end" fill="var(--ink)">{lab}</text>'
                 f'<rect x="{L}" y="{y}" width="{w:.1f}" height="{BW}" fill="{COL[k]}" opacity="0.9"/>')
        if k != "edit":
            ow = om / top * span
            o.append(f'<rect x="{L + w - ow:.1f}" y="{y}" width="{ow:.1f}" height="{BW}" fill="none" stroke="var(--ink)" stroke-width="1.2" stroke-dasharray="3 2"/>')
        o.append(f'<rect x="{L + w:.1f}" y="{y}" width="{st / top * span:.1f}" height="{BW}" fill="var(--cx)"/>'
                 f'<text x="{L + w + st / top * span + 5:.1f}" y="{y + BW / 2 + 4:.1f}" font-size="{11.5 if big else 10.5}" fill="var(--ink)"><tspan font-weight="700">{fmt(v)}</tspan> + {fmt(st)} ms</text>')
        y += BW + 14
    o.append(f'<rect x="{L}" y="{y + 2}" width="10" height="10" fill="none" stroke="var(--ink)" stroke-dasharray="3 2"/><text x="{L + 14}" y="{y + 11}" font-size="10.5" fill="var(--muted)">the outline, about {om:.0f} ms</text>'
             f'<rect x="{L + 150}" y="{y + 2}" width="10" height="10" fill="var(--cx)"/><text x="{L + 164}" y="{y + 11}" font-size="10.5" fill="var(--muted)">statics after it</text>')
    o.append("</svg>")
    return "\n".join(o)


# --- the fixes: before and after at the largest size ---

def mini_fixes(n=None):
    n = n or SIZES[-1]
    W, o, y = 300, [], 4
    top = max(med("A", n, k) for k, _, _ in KINDS)
    o.append(f'<svg viewBox="0 0 {W} 150" width="100%" role="img" aria-label="Before and after the two fixes at {n:,} definitions, for an edit, an undo and a redo">')
    for k, label, col in KINDS:
        a, b = med("A", n, k), med("B", n, k)
        o.append(f'<text x="0" y="{y + 10}" font-size="11.5" fill="var(--ink)">{label}, {n:,} definitions</text>')
        o.append(f'<rect x="0" y="{y + 15}" width="{(W - 80) * a / top:.1f}" height="10" fill="var(--cx)"/><text x="{(W - 80) * a / top + 5:.1f}" y="{y + 24}" font-size="11" fill="var(--muted)">{fmt(a)} ms</text>')
        o.append(f'<rect x="0" y="{y + 28}" width="{(W - 80) * b / top:.1f}" height="10" fill="{col}"/><text x="{(W - 80) * b / top + 5:.1f}" y="{y + 37}" font-size="11" font-weight="700" fill="{col}">{fmt(b)} ms, {100 * (1 - b / a):.0f}% less</text>')
        y += 48
    o.append("</svg>")
    return "\n".join(o)


# --- Figure 2: what an edit and an undo run ---

def fig_pipeline():
    W = 940
    C1, CN = "var(--good)", "var(--bad)"
    def box(x, y, w, h, title, lines, cls):
        col = C1 if cls == "1" else CN if cls == "n" else "var(--muted)"
        tag = {"1": "O(1)", "n": "O(n)", "": ""}[cls]
        o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="var(--paper)" stroke="{col}" stroke-width="{2 if cls else 1.2}"/>',
             f'<text x="{x + 8}" y="{y + 17}" font-size="12" font-weight="700" fill="var(--ink)">{esc(title)}</text>']
        if tag:
            o.append(f'<text x="{x + w - 8}" y="{y + 17}" font-size="11.5" font-weight="700" text-anchor="end" fill="{col}">{tag}</text>')
        for i, l in enumerate(lines):
            o.append(f'<text x="{x + 8}" y="{y + 34 + i * 14}" font-size="11" fill="var(--muted)">{esc(l)}</text>')
        return "\n".join(o)
    def arrow(x1, x2, y):
        return f'<line x1="{x1}" x2="{x2 - 4}" y1="{y}" y2="{y}" stroke="var(--muted)" stroke-width="1.4"/><path d="M{x2 - 6},{y - 4} L{x2},{y} L{x2 - 6},{y + 4}" fill="none" stroke="var(--muted)" stroke-width="1.4"/>'
    o = [f'<svg viewBox="0 0 {W} 330" width="100%" role="img" aria-label="What an edit and an undo run, box by box: the parts that touch only the changed definition are O(1), green; the passes over every definition are O(n), red. An undo adds a second frame that rebuilds the outline.">']
    BW, BH, G = 140, 74, 18
    rows = [
        ("An edit", 30, [("the keystroke", ["the zipper edited at", "the caret"], "1"),
                         ("parse", ["the changed definition", "parsed again: 1"], "1"),
                         ("the top-level term", ["rebuilt from every", "definition"], "n"),
                         ("layout", ["1 chunk measured; the", "walk over the rest"], "n"),
                         ("statics, debounced", ["2 heads compared;", "the chain walked"], "n")]),
        ("An undo", 176, [("pop a snapshot", ["the stack's head; it", "holds zippers, no caches"], "1"),
                          ("parse", ["against the live caches:", "2 definitions again"], "1"),
                          ("the top-level term", ["rebuilt from every", "definition"], "n"),
                          ("layout", ["1 or 2 chunks; the", "walk over the rest"], "n"),
                          ("statics, debounced", ["2 heads compared;", "the chain walked"], "n")]),
    ]
    for label, y, bs in rows:
        o.append(f'<text x="0" y="{y - 10}" font-size="13" font-weight="700" fill="var(--ink)">{label}</text>')
        x = 0
        for i, (t, ls, c) in enumerate(bs):
            o.append(box(x, y, BW, BH, t, ls, c))
            if i < len(bs) - 1:
                o.append(arrow(x + BW, x + BW + G, y + BH / 2))
            x += BW + G
        if label == "An undo":
            # the second frame the restore schedules
            o.append(box(x, y, BW + 6, BH, "frame 2: the outline", ["RealizeView: rebuilt", "from scratch (a miss)"], "n"))
    o.append(f'<line x1="{5 * (BW + G) - G}" x2="{5 * (BW + G)}" y1="{176 + BH / 2}" y2="{176 + BH / 2}" stroke="var(--muted)" stroke-width="1.4" stroke-dasharray="3 3"/>')
    o.append(f'<text x="0" y="292" font-size="11.5" fill="var(--muted)">Green, O(1): touches only the changed definition, whatever the size of the program. Red, O(n): a pass over every definition.</text>'
             f'<text x="0" y="310" font-size="11.5" fill="var(--muted)">The statics refresh runs after the typing debounce, for an edit and an undo alike; it is timed separately below.</text>')
    o.append("</svg>")
    return "\n".join(o)


# --- Figure 5: a chain of lets against a balanced tree of definitions ---

def fig_tree(W=900, mini=False):
    N, hit = 16, 9
    o = [f'<svg viewBox="0 0 {W} {150 if mini else 300}" width="100%" role="img" aria-label="Left: the top level as a chain of nested lets; changing definition 9 rebuilds the 9 lets around it. Right: the same 16 definitions in a balanced tree; changing definition 9 rebuilds the 4 nodes on its path, and the old root still shares every other node.">']
    if mini:
        # the tree alone, small
        lw, y0 = W / N, 120
        nodes = {}
        for lvl in range(5):
            cnt = N >> lvl
            for i in range(cnt):
                x = (i + 0.5) * (W / cnt)
                y = y0 - lvl * 26
                nodes[(lvl, i)] = (x, y)
        for (lvl, i), (x, y) in nodes.items():
            if lvl < 4:
                px, py = nodes[(lvl + 1, i // 2)]
                on = (hit >> lvl) == i
                o.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{px:.1f}" y2="{py:.1f}" stroke="{"var(--accent)" if on else "var(--line)"}" stroke-width="{2.4 if on else 1.2}"/>')
        for (lvl, i), (x, y) in nodes.items():
            on = (hit >> lvl) == i
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5 if lvl else 6}" fill="{"var(--accent)" if on else "var(--paper)"}" stroke="{"var(--accent)" if on else "var(--muted)"}" stroke-width="1.4"/>')
        o.append(f'<text x="0" y="146" font-size="11" fill="var(--muted)">16 definitions: an edit to one rebuilds its path, 4 nodes + 1</text>')
        o.append("</svg>")
        return "\n".join(o)
    # left: the chain
    o.append('<text x="0" y="16" font-size="13" font-weight="700" fill="var(--ink)">Today: a chain of nested lets</text>')
    for i in range(N):
        x, y = 8 + i * 22, 40 + i * 14
        on = i <= hit
        o.append(f'<rect x="{x}" y="{y}" width="58" height="18" rx="4" fill="{"var(--bad)" if on else "var(--paper)"}" opacity="{0.85 if on else 1}" stroke="{"var(--bad)" if on else "var(--muted)"}"/>'
                 f'<text x="{x + 6}" y="{y + 13}" font-size="10.5" fill="{"#fff" if on else "var(--muted)"}">let v{i}</text>')
    o.append(f'<text x="0" y="292" font-size="11.5" fill="var(--muted)">Changing v{hit} rebuilds every let around it: {hit + 1} of {N}, n/2 on average.</text>')
    # right: the tree
    X0, TW, y0 = 430, W - 430, 250
    o.append(f'<text x="{X0}" y="16" font-size="13" font-weight="700" fill="var(--ink)">A balanced tree of definitions</text>')
    nodes = {}
    for lvl in range(5):
        cnt = N >> lvl
        for i in range(cnt):
            nodes[(lvl, i)] = (X0 + (i + 0.5) * (TW / cnt), y0 - lvl * 48)
    for (lvl, i), (x, y) in nodes.items():
        if lvl < 4:
            px, py = nodes[(lvl + 1, i // 2)]
            on = (hit >> lvl) == i
            o.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{px:.1f}" y2="{py:.1f}" stroke="{"var(--accent)" if on else "var(--line)"}" stroke-width="{2.6 if on else 1.2}"/>')
    # the old path, beside the new one: the previous version's root and its path, sharing the rest
    for lvl in range(1, 5):
        x, y = nodes[(lvl, hit >> lvl)]
        o.append(f'<circle cx="{x + 16:.1f}" cy="{y - 8:.1f}" r="6" fill="none" stroke="var(--muted)" stroke-dasharray="2 2"/>')
    for (lvl, i), (x, y) in nodes.items():
        on = (hit >> lvl) == i
        r = 7 if lvl else 8
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{"var(--accent)" if on else "var(--paper)"}" stroke="{"var(--accent)" if on else "var(--muted)"}" stroke-width="1.5"/>')
        if lvl == 0:
            o.append(f'<text x="{x:.1f}" y="{y + 22:.1f}" font-size="9.5" text-anchor="middle" fill="var(--muted)">v{i}</text>')
    rx, ry = nodes[(4, 0)]
    o.append(f'<text x="{rx + 28:.1f}" y="{ry - 4:.1f}" font-size="11" fill="var(--muted)">the old root (dashed) keeps the old path</text>'
             f'<text x="{rx + 28:.1f}" y="{ry + 10:.1f}" font-size="11" fill="var(--muted)">and shares every other node</text>')
    o.append(f'<text x="{X0}" y="292" font-size="11.5" fill="var(--muted)">Changing v{hit} rebuilds its path: log2 n nodes, here 4, each with its summary.</text>')
    o.append("</svg>")
    return "\n".join(o)


# --- the tables ---

def table_scale():
    r = ['<div class="scroll"><table>', '<tr><th>definitions</th>' + "".join(f'<th class="n">{lab}, before</th><th class="n">after</th>' for _, lab, _ in KINDS) + '<th class="n">statics, after</th><th class="n">building the program</th></tr>']
    for n in SIZES:
        build = next(float(m.group(1)) for m in (re.match(rf"UNDOSCALE n={n} build: ([\d.]+) ms", l) for l in open(os.path.join(DATA, "runs", "B1.out"))) if m)
        r.append(f'<tr><td class="n">{n:,}</td>' + "".join(
            f'<td class="n">{fmt(med("A", n, k))}</td><td class="n"><b>{fmt(med("B", n, k))}</b> <span class="note">({MED[("B", n, k)]["step_min_ms"]:.0f}–{MED[("B", n, k)]["step_max_ms"]:.0f})</span></td>'
            for k, _, _ in KINDS) + f'<td class="n">{fmt(stat("B", n))}</td><td class="n">{build:,.0f}</td></tr>')
    r.append("</table></div>")
    return "\n".join(r)


def table_where():
    r = ['<div class="scroll"><table>', '<tr><th>part of the time</th><th>where</th><th class="n">before</th><th class="n">after</th></tr>']
    tb, ta = prof["total_ms"]["before"], prof["total_ms"]["after"]
    for g in prof["groups"]:
        a = g["after_ms"]
        r.append(f'<tr><td>{esc(g["label"])}</td><td><code>{esc(g["function"])}</code></td><td class="n">{g["before_ms"]:,} ms · {g["before_ms"] / tb * 100:.0f}%</td>'
                 f'<td class="n">{"under 78 ms" if a == 0 else f"{a:,} ms · {a / ta * 100:.0f}%"}</td></tr>')
    rb = tb - sum(g["before_ms"] for g in prof["groups"])
    ra = ta - sum(g["after_ms"] for g in prof["groups"])
    r.append(f'<tr><td>the rest</td><td>garbage collection, the probe\'s own frames, and everything below the list</td><td class="n">{rb:,} ms · {rb / tb * 100:.0f}%</td><td class="n">{ra:,} ms · {ra / ta * 100:.0f}%</td></tr>')
    r.append(f'<tr><td><b>total</b></td><td></td><td class="n"><b>{tb:,} ms</b></td><td class="n"><b>{ta:,} ms</b></td></tr>')
    r.append("</table></div>")
    r.append('<p class="note">Inside those parts, after the fixes:</p><div class="scroll"><table><tr><th>function</th><th class="n">share</th></tr>' +
             "".join(f'<tr><td><code>{esc(d["function"])}</code></td><td class="n">{d["ms"]:,} ms · {d["share"] * 100:.0f}%</td></tr>' for d in prof["after_detail"]) + "</table></div>")
    return "\n".join(r)


# --- numbers for the prose ---

V = {}
for b in "AB":
    for n in SIZES:
        for k, _, _ in KINDS:
            V[f"{k}_{b}_{n}"] = fmt(med(b, n, k))
        V[f"st_{b}_{n}"] = fmt(stat(b, n))
big = SIZES[-1]
lo, hi = SIZES[1], SIZES[-1]
sl = [slope("B", k, lo, hi) for k, _, _ in KINDS]
V["slope_lo"], V["slope_hi"] = f"{min(sl):.2f}", f"{max(sl):.2f}"
V["dbl_lo"], V["dbl_hi"] = f"{2 ** min(sl):.1f}", f"{2 ** max(sl):.1f}"
V["n_lo"], V["n_hi"] = f"{lo:,}", f"{hi:,}"
cut = [100 * (1 - med("B", n, k) / med("A", n, k)) for n in SIZES[-2:] for k, _, _ in KINDS]
V["cut_lo"], V["cut_hi"] = f"{min(cut):.0f}", f"{max(cut):.0f}"
ratio = [med("B", n, "undo") / med("B", n, "edit") for n in SIZES[1:]]
V["undo_x_lo"], V["undo_x_hi"] = f"{min(ratio):.1f}", f"{max(ratio):.1f}"
rratio = [med("B", n, "redo") / med("B", n, "edit") for n in SIZES[1:]]
V["redo_x_lo"], V["redo_x_hi"] = f"{min(rratio):.1f}", f"{max(rratio):.1f}"
V["outline_ms"] = f"{outline_ms():.0f}"
V["gap_undo_3200"] = fmt(med("B", 3200, "undo") - med("B", 3200, "edit"))
V["gap_redo_3200"] = fmt(med("B", 3200, "redo") - med("B", 3200, "edit"))
_, pa = parts("after")
PA = {k: ms for k, _, _, ms in pa}
ta = prof["total_ms"]["after"]
for k in ("term", "statics", "outline"):
    V[f"share_{k}"] = f"{PA[k] / ta * 100:.0f}"
tb = prof["total_ms"]["before"]
for g in prof["groups"]:
    V[f"before_share_{g['key']}"] = f"{g['before_ms'] / tb * 100:.0f}"

FIGS = {"FIG_SCALE": fig_scale(), "FIG_SCALE_MINI": mini_scale(), "FIG_WHERE": fig_where(), "FIG_WHERE_MINI": mini_where(),
        "FIG_TWICE": bars_twice(W=640, big=True), "FIG_TWICE_MINI": bars_twice(), "FIG_FIXES_MINI": mini_fixes(),
        "FIG_PIPELINE": fig_pipeline(), "FIG_TREE": fig_tree(), "FIG_TREE_MINI": fig_tree(W=300, mini=True),
        "TABLE_SCALE": table_scale(), "TABLE_WHERE": table_where()}
BODY = open(os.path.join(HERE, "body.html")).read()
BODY = re.sub(r"\{\{(\w+)\}\}", lambda m: FIGS.get(m.group(1)) or V[m.group(1)], BODY)
HEAD = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>What an Undo Costs</title>
<meta name="description" content="How an edit, an undo and a redo in Hazel grow with the program: in proportion to it, about {V['slope_lo']} to {V['slope_hi']} on a log-log plot, from {V['n_lo']} to {V['n_hi']} definitions. Where the time goes, two fixes on #2635, why an undo costs more than an edit, and what O(log n) would take.">
<style>{CSS}
  .o1 {{ color: var(--good); font-weight: 600; }} .on {{ color: var(--bad); font-weight: 600; }}
</style>
</head>
"""
open(os.path.join(HERE, "index.html"), "w").write(HEAD + BODY)
print("wrote 036/index.html;", ", ".join(f"{k}={v}" for k, v in V.items() if not k[0].isupper() and "_A_" not in k and "_B_" not in k))
