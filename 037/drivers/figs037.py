"""^report(37)'s figures (Matthew, 2026-11-05 07:1x: "plots/graphs, where appropriate in section 1 for performance",
"screenshots for items like showing types in Gamma", and "some graphics for each item without having to click").
FIGS[item id] is a list of figures, each (html, caption, wide), drawn at the top of that item's card by gen037.py.
The charts are inline SVG in the series' colours (CSS variables, so both themes), each mark with a <title> for its
value on hover. Every number is from the item's own text or the report it cites; the source is in each caption."""
import math

esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(W, H, label, body):
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(label)}" style="width:100%;height:auto;display:block">'
            + "".join(body) + "</svg>")


def text(x, y, s, size=12, anchor="start", fill="var(--ink)", weight=None, italic=False):
    w = f' font-weight="{weight}"' if weight else ""
    it = ' font-style="italic"' if italic else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{w}{it}>{s}</text>'


def fmt(v):
    if v >= 1000: return f"{v:,.0f}"
    if v >= 20: return f"{v:.0f}"
    return f"{v:.1f}".rstrip("0").rstrip(".")


def logx(lo, hi, x0, x1):
    a, b = math.log10(lo), math.log10(hi)
    return lambda v: x0 + (math.log10(v) - a) / (b - a) * (x1 - x0)


EDIT, UNDO, REDO = "var(--accent2)", "var(--accent)", "var(--warn)"

# ---------------------------------------------------------------- 1. undo

# ^report(36)'s probe (036/data/steps.json): medians of 12, release build; A before the first two fixes, B after
STEPS = {
    "A": {"edit": [14.0, 16.5, 34.0, 72.5, 163.0], "undo": [23.0, 38.0, 79.5, 176.0, 421.5], "redo": [16.0, 29.5, 63.0, 130.0, 340.0]},
    "B": {"edit": [10.5, 10.0, 22.0, 43.0, 106.5], "undo": [18.5, 29.5, 61.0, 120.0, 292.5], "redo": [13.0, 16.5, 41.0, 85.0, 183.5]},
}
SIZES = [400, 800, 1600, 3200, 6400]


def fig_undo_growth():
    W, H, L, R, T, B = 460, 270, 46, 78, 14, 40
    X = logx(300, 7600, L, W - R)
    Y0 = logx(7, 600, H - B, T)
    o = []
    for v in (10, 30, 100, 300):
        o.append(f'<line x1="{L}" x2="{W - R}" y1="{Y0(v):.1f}" y2="{Y0(v):.1f}" stroke="var(--line)"/>')
        o.append(text(L - 6, Y0(v) + 4, f"{v}", 11, "end", "var(--muted)"))
    for n in SIZES:
        o.append(text(X(n), H - B + 16, f"{n:,}", 11, "middle", "var(--muted)"))
    o.append(text((L + W - R) / 2, H - 6, "definitions in the program (log scale)", 11.5, "middle", "var(--muted)"))
    o.append(text(L - 36, T + 2, "ms", 11, "start", "var(--muted)"))
    # a slope-1 guide: what linear growth looks like on these scales
    o.append(f'<line x1="{X(400):.1f}" y1="{Y0(9):.1f}" x2="{X(6400):.1f}" y2="{Y0(144):.1f}" stroke="var(--muted)" stroke-dasharray="1 4" stroke-width="1.5"/>')
    o.append(text(X(1131), Y0(16) + 16, "linear", 10.5, "start", "var(--muted)", italic=True))
    for kind, col in (("undo", UNDO), ("redo", REDO), ("edit", EDIT)):
        for build in ("A", "B"):
            pts = [(X(n), Y0(v)) for n, v in zip(SIZES, STEPS[build][kind])]
            d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
            if build == "A":
                o.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.55"/>')
            else:
                o.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2"/>')
                for (x, y), n, v, va in zip(pts, SIZES, STEPS["B"][kind], STEPS["A"][kind]):
                    o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{col}" stroke="var(--paper)" stroke-width="2">'
                             f'<title>{kind} at {n:,} definitions: {fmt(v)} ms after the first two fixes ({fmt(va)} before)</title></circle>')
        v = STEPS["B"][kind][-1]
        dy = {"undo": 0, "redo": 0, "edit": 2}[kind]
        o.append(text(X(6400) + 8, Y0(v) + 4 + dy, f"{kind} {fmt(v)}", 12, "start", "var(--ink)", 700))
    o.append(f'<line x1="{L + 4}" x2="{L + 24}" y1="{T + 6}" y2="{T + 6}" stroke="var(--ink)" stroke-width="2"/>')
    o.append(text(L + 28, T + 10, "after the first two fixes", 11, "start", "var(--muted)"))
    o.append(f'<line x1="{L + 4}" x2="{L + 24}" y1="{T + 22}" y2="{T + 22}" stroke="var(--ink)" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.55"/>')
    o.append(text(L + 28, T + 26, "before", 11, "start", "var(--muted)"))
    return svg(W, H, "An edit, an undo and a redo against program size, log-log: all three grow in proportion to the program", o)


def fig_undo_fix():
    # 038/data/realize_fix.json via the item's text: 3,200 definitions, dev build, one run, medians of four steps
    W, H, L, R, T = 460, 176, 70, 56, 30
    rows = (("undo", 141, 85, UNDO), ("redo", 96, 41, REDO))
    X = lambda v: L + v / 160 * (W - L - R)
    o = []
    for v in (0, 50, 100, 150):
        o.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{H - 34}" stroke="var(--line)"/>')
        o.append(text(X(v), H - 20, f"{v}", 11, "middle", "var(--muted)"))
    for i, (k, a, b, col) in enumerate(rows):
        y = T + 8 + i * 56
        o.append(text(L - 10, y + 22, k, 13, "end", "var(--ink)", 700))
        o.append(f'<rect x="{L}" y="{y}" width="{X(a) - L:.1f}" height="14" rx="3" fill="var(--muted)" opacity="0.45"><title>{k} before the fix: {a} ms</title></rect>')
        o.append(text(X(a) + 6, y + 11, f"{a} before", 11.5, "start", "var(--muted)"))
        o.append(f'<rect x="{L}" y="{y + 18}" width="{X(b) - L:.1f}" height="14" rx="3" fill="{col}"><title>{k} after the fix: {b} ms</title></rect>')
        o.append(text(X(b) + 6, y + 29, f"{b} after", 11.5, "start", "var(--ink)", 700))
    o.append(f'<line x1="{X(46):.1f}" x2="{X(46):.1f}" y1="{T - 22}" y2="{H - 34}" stroke="{EDIT}" stroke-width="2" stroke-dasharray="5 3"><title>an edit: about 46 ms</title></line>')
    o.append(text(X(46) + 5, T - 12, "an edit: 46 ms", 11.5, "start", EDIT, 700))
    o.append(text((L + W - R) / 2, H - 4, "ms per step at 3,200 definitions", 11, "middle", "var(--muted)"))
    return svg(W, H, "The undo fix at 3,200 definitions: an undo from 141 to 85 ms, a redo from 96 to 41, against an edit's 46", o)


def fig_undo_space():
    # 038/data/space.json: MB the history keeps after 12 slider edits on Full Body
    W, H, L, R, T = 460, 176, 150, 60, 26
    rows = (("#2597 as built", 1048, "+89 MB per edit", "var(--bad)"),
            ("with the compaction", 159, "level after 3 edits", "var(--good)"),
            ("#2635 (has it)", 52, "+1.6 MB per edit", "var(--accent2)"))
    X = lambda v: L + v / 1100 * (W - L - R)
    o = [text(8, 14, "MB the undo history keeps after 12 edits, Full Body", 11.5, "start", "var(--muted)")]
    for v in (0, 500, 1000):
        o.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{H - 26}" stroke="var(--line)"/>')
        o.append(text(X(v), H - 12, f"{v:,}", 11, "middle", "var(--muted)"))
    for i, (lab, v, sub, col) in enumerate(rows):
        y = T + 6 + i * 40
        o.append(text(L - 10, y + 10, lab, 12.5, "end", "var(--ink)"))
        o.append(text(L - 10, y + 24, sub, 10.5, "end", "var(--muted)"))
        o.append(f'<rect x="{L}" y="{y}" width="{max(3, X(v) - L):.1f}" height="20" rx="3" fill="{col}"><title>{lab}: {v:,} MB</title></rect>')
        o.append(text(X(v) + 6, y + 15, f"{v:,}", 13, "start", "var(--ink)", 700))
    return svg(W, H, "MB kept after 12 edits: 1,048 on #2597 as built, 159 with Andrew Blinn's compaction, 52 on #2635", o)


# ---------------------------------------------------------------- 2. the worker

def dumbbell(W, rows, lo, hi, ticks, unit, title, label, L=170, rh=34):
    """rows: (label, before, after, after_label_or_None); log scale; before an open ring, after a filled dot"""
    R, T = 60, 30
    H = T + rh * len(rows) + 30
    X = logx(lo, hi, L, W - R)
    o = [text(8, 14, title, 11.5, "start", "var(--muted)")]
    for v, lab in ticks:
        o.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T - 4}" y2="{H - 26}" stroke="var(--line)"/>')
        o.append(text(X(v), H - 12, lab, 11, "middle", "var(--muted)"))
    for i, (lab, a, b, note) in enumerate(rows):
        y = T + 10 + i * rh
        o.append(text(L - 12, y + 4, lab, 12, "end", "var(--ink)"))
        if b is None:
            o.append(f'<circle cx="{X(a):.1f}" cy="{y}" r="6" fill="var(--paper)" stroke="var(--warn)" stroke-width="2.5"><title>{esc(lab)}: {fmt(a)} {unit}, {esc(note)}</title></circle>')
            o.append(text(X(a) + 11, y + 4, note, 11.5, "start", "var(--warn)", 700))
            continue
        o.append(f'<line x1="{X(b):.1f}" x2="{X(a):.1f}" y1="{y}" y2="{y}" stroke="var(--muted)" stroke-width="2" opacity="0.6"/>')
        o.append(f'<circle cx="{X(a):.1f}" cy="{y}" r="5.5" fill="var(--paper)" stroke="var(--muted)" stroke-width="2"><title>{esc(lab)}, before: {fmt(a)} {unit}</title></circle>')
        o.append(f'<circle cx="{X(b):.1f}" cy="{y}" r="6" fill="var(--accent2)" stroke="var(--paper)" stroke-width="2"><title>{esc(lab)}, now: {fmt(b)} {unit}</title></circle>')
        o.append(text(X(a) + 10, y + 4, fmt(a), 11, "start", "var(--muted)"))
        o.append(text(X(b) - 10, y + 4, fmt(b), 12, "end", "var(--ink)", 700))
    return svg(W, H, label, o)


def fig_worker_bytes():
    rows = (("Full Body", 1950, 26.8, None), ("Kids' Choice", 494, 52, None), ("Emotion", 38, 4, None))
    return dumbbell(460, rows, 2, 4000, ((3, "3 KB"), (30, "30 KB"), (300, "300 KB"), (3000, "3 MB")), "KB",
                    "KB to the worker after one edit (log scale): ○ the whole program, ● shared",
                    "KB sent to the worker after one edit, whole against shared, on three slides", L=104)


def fig_worker_time():
    rows = (("Full Body, again", 36.2, 0.8, None), ("Kids' Choice, again", 9.3, 0.1, None),
            ("Full Body, an undo", 40.3, 0.7, None), ("Full Body, a redo", 42.2, 0.6, None),
            ("Kids' Choice, an undo", 15.8, None, "still a miss"))
    return dumbbell(460, rows, 0.025, 90, ((0.1, "0.1"), (1, "1"), (10, "10 ms")), "ms",
                    "The worker taking a request in, ms (log scale): ○ before its memo, ● now",
                    "The worker's time to take a request in, before and after it keeps what it composed", L=150, rh=30)


def box(x, y, w, h, lines, stroke="var(--line)", fill="var(--paper)", size=12, bold_first=True, dash=None, color="var(--ink)"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.6"{d}/>']
    n = len(lines)
    lh = size + 4
    y0 = y + h / 2 - (n - 1) * lh / 2 + size * 0.36
    for i, s in enumerate(lines):
        o.append(text(x + w / 2, y0 + i * lh, s, size if i or not bold_first else size + 0.5, "middle",
                      color if (i == 0 and bold_first) else "var(--muted)" if i else color, 700 if (i == 0 and bold_first) else None))
    return "".join(o)


def arrow(x1, y1, x2, y2, col="var(--muted)", dash=None, w=1.8):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    ang = math.atan2(y2 - y1, x2 - x1)
    a1, a2 = ang + 2.6, ang - 2.6
    hx = f"M{x2 + 8 * math.cos(a1):.1f} {y2 + 8 * math.sin(a1):.1f} L{x2:.1f} {y2:.1f} L{x2 + 8 * math.cos(a2):.1f} {y2 + 8 * math.sin(a2):.1f}"
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}"{d}/>'
            f'<path d="{hx}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="round"/>')


def fig_worker_path():
    W, H = 940, 220
    o = []
    o.append(f'<rect x="4" y="22" width="436" height="128" rx="10" fill="none" stroke="var(--line)" stroke-dasharray="4 4"/>')
    o.append(text(16, 16, "the page (main thread)", 12, "start", "var(--muted)", 700))
    o.append(f'<rect x="480" y="22" width="456" height="128" rx="10" fill="none" stroke="var(--line)" stroke-dasharray="4 4"/>')
    o.append(text(492, 16, "the eval worker", 12, "start", "var(--muted)", 700))
    o.append(box(18, 48, 128, 76, ["statics", "analyzes the", "program"]))
    o.append(box(166, 48, 128, 76, ["pieces", "one per definition,", "each hashed"], stroke="var(--accent)"))
    o.append(box(314, 48, 112, 76, ["sharing", "sends what the", "worker lacks"]))
    o.append(box(496, 48, 196, 76, ["compose", "keeps the last 4 programs,", "by their pieces' hashes"], stroke="var(--accent2)"))
    o.append(box(712, 48, 108, 76, ["evaluate", "the program"]))
    o.append(box(836, 48, 90, 76, ["reply", "the result"]))
    o.append(arrow(146, 86, 162, 86)); o.append(arrow(294, 86, 310, 86)); o.append(arrow(426, 86, 492, 86, "var(--ink)", w=2.2))
    o.append(arrow(692, 86, 708, 86)); o.append(arrow(820, 86, 832, 86))
    o.append(text(459, 78, "request", 11, "middle", "var(--muted)"))
    # the finding: fresh ids made the same item a new piece
    o.append(f'<path d="M230 124 C 230 168, 594 168, 594 124" fill="none" stroke="var(--good)" stroke-width="1.8"/>')
    o.append(text(412, 176, "fixed 11-05: an item's holes and a livelit use's expansion took fresh ids on every analysis,", 12, "middle", "var(--ink)"))
    o.append(text(412, 192, "so the same program hashed as new pieces and an undo missed the memo; now their ids are derived", 12, "middle", "var(--ink)"))
    o.append(text(704, 212, "open: a livelit definition's run, re-id'd by the evaluator", 12, "middle", "var(--warn)", 700))
    return svg(W, H, "How a request travels: statics, pieces, sharing, then in the worker composing (with a memo of four), evaluating, replying", o)


# ---------------------------------------------------------------- 3. half the steps

def fig_steps():
    W, H, L, R, T = 460, 214, 156, 70, 26
    rows = (("dev", 206834, "budget 227,000", 227000, "var(--muted)"),
            ("#2635, d0c56fb090 out", 152746, "", None, "var(--accent)"),
            ("#2635", 96438, "", None, "var(--accent)"),
            ("dev with #2793", 96438, "budget 106,000", 106000, "var(--accent2)"))
    X = lambda v: L + v / 240000 * (W - L - R)
    o = [text(8, 14, "Trampoline steps on the PerfBudgets program (cold)", 11.5, "start", "var(--muted)")]
    for v in (0, 100000, 200000):
        o.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{H - 26}" stroke="var(--line)"/>')
        o.append(text(X(v), H - 12, f"{v // 1000}k", 11, "middle", "var(--muted)"))
    for i, (lab, v, blab, bud, col) in enumerate(rows):
        y = T + 6 + i * 40
        o.append(text(L - 10, y + 15, lab, 12.5, "end", "var(--ink)"))
        o.append(f'<rect x="{L}" y="{y}" width="{X(v) - L:.1f}" height="20" rx="3" fill="{col}"><title>{esc(lab)}: {v:,} steps</title></rect>')
        o.append(text(X(v) - 6, y + 15, f"{v:,}", 12.5, "end", "var(--paper)", 700))
        if bud:
            o.append(f'<line x1="{X(bud):.1f}" x2="{X(bud):.1f}" y1="{y - 3}" y2="{y + 23}" stroke="var(--ink)" stroke-width="2"><title>{blab}</title></line>')
            o.append(text(X(bud), y + 34, blab, 10.5, "middle", "var(--muted)"))
    return svg(W, H, "Steps: dev 206,834; #2635 with d0c56fb090 reverted 152,746; #2635 96,438; dev with #2793 96,438", o)


def fig_small_programs():
    W, H, L, R, T = 460, 214, 92, 110, 26
    rows = (("fib(10)", 37922, 17722), ("map", 3765, 1771), ("sum of 10", 2235, 1035), ("the literal 1", 12, 0))
    X = lambda v: L + v / 100 * (W - L - R)
    o = [text(8, 14, "#2635's steps as a share of dev's, small programs", 11.5, "start", "var(--muted)")]
    for v in (0, 50, 100):
        o.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{H - 26}" stroke="var(--line)"' + (' stroke-dasharray="3 3"' if v == 50 else "") + "/>")
        o.append(text(X(v), H - 12, f"{v}%", 11, "middle", "var(--muted)"))
    for i, (lab, dev, ours) in enumerate(rows):
        y = T + 6 + i * 40
        p = 100 * ours / dev
        o.append(text(L - 10, y + 15, lab, 12.5, "end", "var(--ink)"))
        o.append(f'<rect x="{L}" y="{y}" width="{X(100) - L:.1f}" height="20" rx="3" fill="var(--muted)" opacity="0.18"/>')
        o.append(f'<rect x="{L}" y="{y}" width="{max(2, X(p) - L):.1f}" height="20" rx="3" fill="var(--accent)"><title>{lab}: {ours:,} steps on #2635 against {dev:,} on dev</title></rect>')
        o.append(text(X(100) + 6, y + 15, f"{ours:,} of {dev:,}", 11.5, "start", "var(--ink)"))
    return svg(W, H, "On #2635 each small program takes under half dev's steps: fib(10), map, sum of 10, and 0 of 12 for a literal", o)


# ---------------------------------------------------------------- 4. #2635 and dev

def fig_branches():
    W, H = 940, 236
    lanes = {"dev": 46, "2469": 112, "2635": 178}
    X0, X1 = 210, 900
    days = ["10-27", "10-29", "11-02", "11-03", "11-05"]
    DX = {"10-27": X0 + 30, "10-29": X0 + 180, "11-02": X0 + 350, "11-03": X0 + 510, "11-05": X0 + 660}
    o = []
    for k, lab, sub in (("dev", "dev", ""), ("2469", "#2469", "modular editors"), ("2635", "#2635", "livelits × modular editors")):
        y = lanes[k]
        o.append(f'<line x1="{X0}" x2="{X1}" y1="{y}" y2="{y}" stroke="var(--line)" stroke-width="4" stroke-linecap="round"/>')
        o.append(text(X0 - 12, y + 1, lab, 13.5, "end", "var(--ink)", 700))
        if sub: o.append(text(X0 - 12, y + 16, sub, 10.5, "end", "var(--muted)"))
    for d in days:
        o.append(text(DX[d], H - 8, d, 11, "middle", "var(--muted)"))
    # into #2635
    o.append(arrow(DX["10-27"], lanes["2469"] + 7, DX["10-27"], lanes["2635"] - 9, "var(--accent)"))
    o.append(text(DX["10-27"] + 8, lanes["2469"] + 34, "m41–m44", 11, "start", "var(--muted)"))
    o.append(f'<circle cx="{DX["10-29"]}" cy="{lanes["dev"]}" r="7" fill="var(--accent2)"><title>dev\'s merge day, 10-29: 149 commits</title></circle>')
    o.append(text(DX["10-29"], lanes["dev"] - 14, "merge day, 149 commits", 11.5, "middle", "var(--ink)"))
    o.append(f'<path d="M{DX["10-29"] + 6} {lanes["dev"] + 5} C {DX["10-29"] + 120} {lanes["dev"] + 40}, {DX["11-02"] - 60} {lanes["2635"] - 70}, {DX["11-02"] - 4} {lanes["2635"] - 9}" fill="none" stroke="var(--accent2)" stroke-width="1.8"/>')
    o.append(arrow(DX["11-02"] - 10, lanes["2635"] - 16, DX["11-02"] - 4, lanes["2635"] - 9, "var(--accent2)"))
    pts = (("10-27", "547b9cfa8b", "#2469's 23"), ("11-02", "2cab658ef1", "dev merged"), ("11-03", "243874eecd", "deck reset"),
           ("11-05", "ab7273c984", "worker memo, ids"))
    for d, sha, lab in pts:
        x = DX[d]
        o.append(f'<circle cx="{x}" cy="{lanes["2635"]}" r="7" fill="var(--accent)" stroke="var(--paper)" stroke-width="2"><title>{sha}: {lab}</title></circle>')
        o.append(text(x, lanes["2635"] + 22, lab, 11.5, "middle", "var(--ink)"))
        o.append(text(x, lanes["2635"] + 36, sha, 10, "middle", "var(--muted)"))
    # the question: the landing order
    o.append(arrow(X1 - 20, lanes["2469"] - 8, X1 - 20, lanes["dev"] + 9, "var(--warn)", "5 4"))
    o.append(text(X1 - 28, lanes["2469"] - 18, "1. #2469 lands?", 11.5, "end", "var(--warn)", 700))
    o.append(f'<path d="M{X1 + 4} {lanes["2635"] - 8} C {X1 + 26} {lanes["2635"] - 60}, {X1 + 26} {lanes["dev"] + 50}, {X1 + 6} {lanes["dev"] + 8}" fill="none" stroke="var(--warn)" stroke-width="1.8" stroke-dasharray="5 4"/>')
    o.append(arrow(X1 + 12, lanes["dev"] + 16, X1 + 6, lanes["dev"] + 8, "var(--warn)"))
    o.append(text(X1 + 30, lanes["2469"] + 28, "2. then", 11.5, "start", "var(--warn)", 700))
    o.append(text(X1 + 30, lanes["2469"] + 42, "#2635?", 11.5, "start", "var(--warn)", 700))
    return svg(W + 60, H, "#2635 took #2469's m41-m44 on 10-27 and dev's merge day on 11-02; the question is the landing order to dev", o)


# ---------------------------------------------------------------- the other sections

def img(src, alt, w=None):
    return f'<img src="{src}" alt="{esc(alt)}" loading="lazy" style="width:100%;height:auto;display:block;border-radius:6px;border:1px solid var(--line)">'


def fig_hazlet():
    W, H = 940, 210
    o = []
    o.append(box(16, 40, 170, 84, ["the game (JS)", "draws, takes taps,", "keeps the state"], stroke="var(--accent2)"))
    o.append(box(300, 40, 190, 84, ["a Hazel function", "on_event(g, e)", "the room's rule"], stroke="var(--accent)"))
    o.append(f'<path d="M186 66 L296 66" stroke="var(--ink)" stroke-width="2"/>' + arrow(280, 66, 296, 66, "var(--ink)", w=2))
    o.append(text(241, 58, "an event", 11.5, "middle", "var(--muted)"))
    o.append(text(241, 82, "Pull(L)", 10.5, "middle", "var(--muted)"))
    o.append(f'<path d="M300 104 L190 104" stroke="var(--ink)" stroke-width="2"/>' + arrow(206, 104, 190, 104, "var(--ink)", w=2))
    o.append(text(245, 122, "a command back", 11.5, "middle", "var(--muted)"))
    o.append(text(245, 138, "Flip(side, …), Done", 10.5, "middle", "var(--muted)"))
    o.append(text(16, 24, "A Hazlet: some of a JS program's event handlers are Hazel functions", 12.5, "start", "var(--ink)", 700))
    # the library's parts
    o.append(text(560, 24, "The library (#2711, #2719), if made official", 12.5, "start", "var(--ink)", 700))
    o.append(box(560, 40, 366, 58, ["stable core, proposed", "analyze · run · the value mapping"], stroke="var(--good)"))
    o.append(box(560, 108, 366, 58, ["experimental", "the embed frame · outlineProgram (^ticket 587)"], stroke="var(--warn)", dash="5 4"))
    o.append(text(743, 190, "two outline walkers today: the library's, over its ModuleProgram,", 11.5, "middle", "var(--muted)"))
    o.append(text(743, 205, "and #2469's OutlineTree in the editor's sidebar", 11.5, "middle", "var(--muted)"))
    return svg(W, H, "A Hazlet: the game sends an event to a Hazel function and acts on the command it returns; the library's proposed stable core and experimental parts", o)


def fig_npm():
    W, H = 940, 168
    o = []
    vs = (("0.0.1", "11-02 11:03", ["first publish: hazel-lib.js,", "require, import, script tag,", ".d.ts, README; 648.5 kB"]),
          ("0.0.2", "11-03", ["source at hazelgrove/hazeljs;", "examples; an install check", "on Node 18, 20, 22"]),
          ("0.0.3", "11-03", ["a tagline; README: errors,", "holes, unfinished code;", "checking hazel-lib.js's commit"]),
          ("0.0.4", "11-03", ["#2719 at 1ba138ef28, ms", "measured; the same bytes", "as Hazel's own deploy"]))
    x0, dx = 70, 232
    o.append(f'<line x1="{x0}" x2="{x0 + 3 * dx}" y1="36" y2="36" stroke="var(--line)" stroke-width="4" stroke-linecap="round"/>')
    for i, (v, d, lines) in enumerate(vs):
        x = x0 + i * dx
        o.append(f'<circle cx="{x}" cy="36" r="9" fill="var(--accent)" stroke="var(--paper)" stroke-width="2"><title>hazeljs {v}, {d}</title></circle>')
        o.append(text(x + 16, 30, v, 14, "start", "var(--ink)", 700))
        o.append(text(x + 16, 46, d, 11, "start", "var(--muted)"))
        for j, s in enumerate(lines):
            o.append(text(x - 50, 72 + j * 16, s, 11.5, "start", "var(--ink)" if j == 0 else "var(--muted)"))
    o.append(f'<rect x="20" y="126" width="210" height="30" rx="6" fill="color-mix(in srgb, var(--line) 50%, transparent)"/>')
    o.append(f'<text x="34" y="146" font-size="13" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" fill="var(--ink)">$ npm install hazeljs</text>')
    o.append(text(250, 146, "MUDU loads its Hazel from the package (jsDelivr) since Dress Up 0.0.476", 12, "start", "var(--muted)"))
    return svg(W, H, "hazeljs versions 0.0.1 to 0.0.4, and npm install hazeljs", o)


def fig_grammar_flow():
    W, H = 460, 300
    o = [text(8, 16, "From a grammar to a language's tiles", 12, "start", "var(--ink)", 700)]
    steps = ((["a grammar, a Hazel value", "the rules, in order (IMP's first)"], "built", "var(--good)"),
             (["a parser for it", "Earley at run time, or Menhir ahead"], "not yet", "var(--warn)"),
             (["a tile editor", "programs in the language as tiles"], "not yet", "var(--warn)"),
             (["the expansion, a Hazel value", "today the grammar itself; then a parse tree"], "in part", "var(--accent2)"))
    for i, (lines, st, col) in enumerate(steps):
        y = 30 + i * 66
        o.append(box(12, y, 340, 50, lines, stroke=col, dash=None if st == "built" else "5 4"))
        o.append(f'<rect x="364" y="{y + 15}" width="84" height="22" rx="11" fill="none" stroke="{col}" stroke-width="1.5"/>')
        o.append(text(406, y + 30, st, 11.5, "middle", col, 700))
        if i < 3: o.append(arrow(182, y + 50, 182, y + 64))
    return svg(W, H, "A grammar livelit's parts: the grammar (built), a parser and a tile editor (not yet), the expansion (in part)", o)


def fig_type_prs():
    W, H = 460, 150
    o = [text(8, 16, "The PRs, and where each change is", 12, "start", "var(--ink)", 700)]
    o.append(box(12, 30, 92, 44, ["dev"], stroke="var(--muted)"))
    o.append(box(150, 30, 136, 44, ["#2676", "cursor inspector"], stroke="var(--accent)"))
    o.append(box(326, 30, 124, 44, ["#2698 (draft)", "Γ, stacked"], stroke="var(--accent)", dash="5 4"))
    o.append(arrow(150, 52, 108, 52, "var(--ink)")); o.append(arrow(326, 52, 290, 52, "var(--ink)"))
    o.append(text(128, 92, "green, mergeable, not reviewed; 174 commits behind dev", 11, "start", "var(--muted)"))
    o.append(box(12, 102, 438, 40, ["#2635 and #2597 carry both, and ^unfold (always · on hover · right-click)"], stroke="var(--line)", size=11.5))
    return svg(W, H, "#2676 into dev, #2698 stacked on it; #2635 and #2597 carry both and the unfold setting", o)


def fig_unfold_ways():
    W, H = 460, 120
    o = [text(8, 16, "^unfold: three ways to offer it (the pick that waits)", 12, "start", "var(--ink)", 700)]
    for i, (a, b) in enumerate((("always", "a ▸ on every long entry"), ("on hover", "the ▸ shows under the mouse"), ("right-click", "a menu on the entry"))):
        x = 12 + i * 150
        o.append(box(x, 30, 140, 76, [a, b[:18], b[18:]] if len(b) > 18 else [a, b], stroke="var(--accent)"))
    return svg(W, H, "Three ways to offer unfolding: always, on hover, by right-click", o)


FIGS = {
    "undo": [(fig_undo_growth(), "Each step against program size, both scales logarithmic: a line parallel to the dotted guide grows in proportion to the program. Solid: after the first two fixes; dashed: before. Release build, medians of 12 (^report(36)).", False),
             (fig_undo_fix(), "The third fix (9df1b2601e): an undo had rebuilt the syntax twice. At 3,200 definitions, dev build, one run, medians of four steps (^report(38)).", False),
             (fig_undo_space(), "Space: what the undo history keeps after 12 slider edits on Full Body. Andrew Blinn's compaction (6010128b7d, on #2469); dev does not have it yet (^report(38)).", False)],
    "worker-sharing": [(fig_worker_path(), "Where a request goes, and where the undo's misses were. The memo keeps the last four programs the worker composed, keyed by their pieces' hashes.", True),
                       (fig_worker_bytes(), "After one edit, the bytes posted to the worker with sharing against the whole program (^ticket(666)'s probe, Node, GitHub's machines).", False),
                       (fig_worker_time(), "The worker taking a request in, before its memo and now (probe runs 41933123707 and 41995647179). Kids' Choice's undo, 15.8 ms in the 01:15 run, still misses on its livelit definition.", False)],
    "half-steps": [(fig_steps(), "The PerfBudgets program's steps. Reverting d0c56fb090 alone gives back half the gap; #2793 brings both commits to dev, with budgets to match.", False),
                   (fig_small_programs(), "Every form alike: ^ticket(667)'s probe of 16 small programs; four shown. Fewer bounces per reduction, not fewer reductions.", False)],
    "dev-merge": [(fig_branches(), "#2635 since 10-27: #2469's m41 to m44, then dev's merge day, the deck's fixes, and the worker's memo with the derived ids (11-05). Dashed: the question, which lands on dev first.", True)],
    "mudu-demo": [(img("img/trap-game.jpg", "The trap room in the game: its two red levers, the pits they open, the boulders' blue levers."), "The trap room, the game's demo room for scripts (^report(32)).", False),
                  (img("img/trap-tiles.jpg", "The trap room's rule at max size, in Hazel's tiles, with the outline of every box at the left."), "Its rule in the Scripting tab, in Hazel's tiles: on_event takes the room's state and an event, and gives back a command.", False)],
    "library": [(fig_hazlet(), "What a Hazlet is, and the split ^report(34) proposes for the library.", True)],
    "npm": [(fig_npm(), "hazeljs on npm: four versions in two days (npmjs.com/package/hazeljs).", True)],
    "type-expansion": [(fig_type_prs(), "The two PRs toward dev, and the branches that already carry them.", False)],
    "gamma-types": [(fig_unfold_ways(), "The three ways to offer unfolding in Γ, each a setting on #2635's Colors slide (^ticket(468)).", False)],
    "dsl-livelit": [(img("img/grammar-imp-opens.jpg", "The grammar livelit as it opens: three rules, Var, Cmd and Exp, each alternative a text box with its chips beside it"), "The prototype on draft #2806: IMP's rules, each alternative drawn as chips coloured by rule (^report(41)).", False),
                    (fig_grammar_flow(), "What a DSL livelit needs, and what the prototype has.", False)],
}
