"""^report(66)'s figures, drawn at the top of each item's card by gen066.py (FIGS[item id] = [(html, caption, wide)]).
Inline SVG in the series' colours (CSS variables, so both themes), with figs037's helpers. Every number is from the
source its caption names: ^report(65)'s tables, the dashboard's tickets, npm, GitHub, or a file in 066/data/."""
import datetime as dt
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "037", "drivers"))
from figs037 import svg, text, logx  # noqa: E402

DATA = os.path.join(HERE, "..", "data")
R065 = os.path.join(HERE, "..", "..", "065", "data", "tables.json")
NOW, THEN, PLAIN = "var(--accent)", "var(--muted)", "var(--good)"


def legend(x, y, items):
    o = []
    for col, lab, hollow in items:
        o.append(f'<circle cx="{x + 5}" cy="{y - 4}" r="5" fill="{"var(--paper)" if hollow else col}" stroke="{col}" stroke-width="2"/>')
        o.append(text(x + 14, y, lab, 11.5, "start", "var(--ink)"))
        x += 22 + 6.4 * len(lab)
    return o


# ---------------------------------------------------------------- 1. hazel-jit

def fig_fourway():
    """^report(65) #fourway: each game's time a call, hazel-jit of 11-19 and now, as a multiple of plain JS's"""
    t = next(t for t in json.load(open(R065)) if t["section_id"] == "fourway")
    us = lambda s: float(s.split()[0].replace(",", ""))
    rows = [(r[0], us(r[3]) / us(r[5]), us(r[4]) / us(r[5])) for r in t["rows"]]
    rows.sort(key=lambda r: -r[1])
    W, L, R, T, rh = 640, 140, 70, 40, 22
    H = T + rh * len(rows) + 34
    X = logx(1, 120, L, W - R)
    o = [text(8, 16, "Each game's call, as a multiple of its plain JS (1× = as fast as JS), a log scale", 12, "start", "var(--muted)")]
    o += legend(L, 32, ((THEN, "hazel-jit, 11-19", True), (NOW, "hazel-jit now", False)))
    for v in (1, 2, 5, 10, 20, 50, 100):
        o.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{H - 28}" stroke="var(--line)"/>')
        o.append(text(X(v), H - 12, f"{v}×", 11, "middle", "var(--muted)"))
    for i, (g, a, b) in enumerate(rows):
        y = T + 10 + i * rh
        o.append(text(L - 10, y + 4, g, 12, "end", "var(--ink)"))
        o.append(f'<line x1="{X(b):.1f}" x2="{X(a):.1f}" y1="{y}" y2="{y}" stroke="var(--line)" stroke-width="3"/>')
        o.append(f'<circle cx="{X(a):.1f}" cy="{y}" r="5" fill="var(--paper)" stroke="{THEN}" stroke-width="2"><title>{g}, 11-19: {a:.1f}× plain JS</title></circle>')
        o.append(f'<circle cx="{X(b):.1f}" cy="{y}" r="5" fill="{NOW}"><title>{g}, now: {b:.1f}× plain JS</title></circle>')
        o.append(text(X(a) + 9, y + 4, f"{a:.1f}× → {b:.1f}×", 11, "start", "var(--muted)"))
    return svg(W, H, "Each game's call as a multiple of plain JS, hazel-jit of 11-19 against now: 11.9 times overall on 11-19, 3.8 now", o)


def fig_trials():
    """^ticket(890)'s timing of trial/1126-night against hazeljs (GitHub, one runner each, every answer the same)"""
    rows = (("World.step, the whole", (3.78, 4.06), (2.33, 2.48)),
            ("a bunny", (2.75, 2.79), (0.57, 0.63)),
            ("a frog", (3.83, 3.91), (0.94, 0.97)),
            ("a songbird", (4.23, 4.31), (1.54, 1.58)),
            ("a pickup", (5.69, 5.81), (3.78, 4.10)),
            ("the carpet", (1.32, 1.35), (0.83, 0.90)),
            ("the wind", (0.39, 0.41), (0.22, 0.24)))
    W, L, R, T, rh = 640, 170, 20, 40, 30
    H = T + rh * len(rows) + 34
    X = lambda v: L + v / 8.0 * (W - L - R)
    o = [text(8, 16, "Gnome world's rules, µs a call on fresh inputs, before and after the five trials", 12, "start", "var(--muted)")]
    o += legend(L, 32, ((THEN, "hazeljs (#2857), b1b4e19286", False), (NOW, "trial/1126-night, abf653a21d", False)))
    for v in range(0, 9, 2):
        o.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{H - 28}" stroke="var(--line)"/>')
        o.append(text(X(v), H - 12, f"{v} µs", 11, "middle", "var(--muted)"))
    for i, (lab, a, b) in enumerate(rows):
        y = T + 6 + i * rh
        o.append(text(L - 10, y + 15, lab, 12, "end", "var(--ink)", 700 if i == 0 else None))
        for j, ((lo, hi), col) in enumerate(((a, THEN), (b, NOW))):
            yy = y + j * 11
            o.append(f'<rect x="{L}" y="{yy}" width="{X(hi) - L:.1f}" height="9" rx="2" fill="{col}" opacity="{0.55 if j == 0 else 1}">'
                     f'<title>{lab}: {lo}-{hi} µs</title></rect>')
        o.append(text(X(a[1]) + 6, y + 10, f"{a[0]:.2f}–{a[1]:.2f} → {b[0]:.2f}–{b[1]:.2f}", 11, "start", "var(--muted)"))
    return svg(W, H, "Gnome world's World.step on fresh inputs, 3.78-4.06 µs on hazeljs, 2.33-2.48 with tonight's trials merged; each animal faster", o)


def fig_build():
    """^ticket(890)'s timing: building Gnome world's rules, first build and warm, hazeljs against trial/1126-night"""
    rows = (("first build", (5.06, 5.17), (4.74, 4.82)), ("warm, again", (3.85, 3.98), (3.57, 3.60)))
    W, L, R, T, rh = 460, 100, 120, 40, 34
    H = T + rh * len(rows) + 30
    X = lambda v: L + v / 6.0 * (W - L - R)
    o = [text(8, 16, "Building Gnome world's rules, seconds, in Node on GitHub", 12, "start", "var(--muted)")]
    o += legend(L, 32, ((THEN, "hazeljs", False), (NOW, "trial/1126-night", False)))
    for v in range(0, 7, 2):
        o.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{H - 24}" stroke="var(--line)"/>')
        o.append(text(X(v), H - 8, f"{v} s", 11, "middle", "var(--muted)"))
    for i, (lab, a, b) in enumerate(rows):
        y = T + 6 + i * rh
        o.append(text(L - 10, y + 15, lab, 12, "end", "var(--ink)"))
        for j, ((lo, hi), col) in enumerate(((a, THEN), (b, NOW))):
            o.append(f'<rect x="{L}" y="{y + j * 12}" width="{X(hi) - L:.1f}" height="10" rx="2" fill="{col}" opacity="{0.55 if j == 0 else 1}"/>')
        o.append(text(X(a[1]) + 6, y + 13, f"{a[0]:.2f}–{a[1]:.2f} → {b[0]:.2f}–{b[1]:.2f}", 11, "start", "var(--muted)"))
    return svg(W, H, "Building Gnome world's rules: first build 5.06-5.17 s to 4.74-4.82; warm 3.85-3.98 to 3.57-3.60 (about 8%)", o)


# ---------------------------------------------------------------- 2. hazeljs on npm

# the package repository's own version commits (hazelgrove/hazeljs, editor-in-package) that npm does not list
REPO_ONLY = (("0.0.9", "2026-11-19"), ("0.0.10", "2026-11-23"), ("0.0.11", "2026-11-23"), ("0.0.12", "2026-11-24"), ("0.0.13", "2026-11-25"))


def fig_npm():
    """npm view hazeljs time --json (066/data/npm-time.json), and the repo's version commits npm does not list"""
    t = json.load(open(os.path.join(DATA, "npm-time.json")))
    pub = [(v, d[:10]) for v, d in t.items() if v[0].isdigit() and "stage" not in v]
    d0 = dt.date(2026, 10, 31)
    day = lambda s: (dt.date.fromisoformat(s) - d0).days
    W, L, R, T = 760, 20, 30, 30
    H = 230
    X = lambda n: L + (n - 1) / 26 * (W - L - R)
    o = [text(8, 16, "hazeljs versions by day: on npm (filled), and made in its repository but not published (hollow)", 12, "start", "var(--muted)")]
    base = 160
    o.append(f'<line x1="{L}" x2="{W - R}" y1="{base}" y2="{base}" stroke="var(--muted)"/>')
    for n in range(1, 28, 2):
        o.append(f'<line x1="{X(n):.1f}" x2="{X(n):.1f}" y1="{base}" y2="{base + 5}" stroke="var(--muted)"/>')
        o.append(text(X(n), base + 18, f"11-{n:02d}", 10, "middle", "var(--muted)"))
    for n, lab in ((13, "last meeting, 11-13"), (20, "last week, 11-20"), (27, "today")):
        o.append(f'<line x1="{X(n):.1f}" x2="{X(n):.1f}" y1="{T + 8}" y2="{base}" stroke="var(--warn)" stroke-dasharray="4 3"/>')
        o.append(text(X(n), T + 2, lab, 10.5, "middle", "var(--warn)"))
    stack = {}
    for v, d, hollow in sorted([(v, d, False) for v, d in pub] + [(v, d, True) for v, d in REPO_ONLY], key=lambda r: (r[1], [int(x) for x in r[0].split(".")])):
        k = day(d)
        stack[k] = stack.get(k, 0) + 1
        y = base - 10 - (stack[k] - 1) * 26
        col = "var(--accent)"
        o.append(f'<circle cx="{X(k):.1f}" cy="{y}" r="6" fill="{"var(--paper)" if hollow else col}" stroke="{col}" stroke-width="2"><title>{v}, {d}{" (not on npm)" if hollow else ""}</title></circle>')
        o.append(text(X(k), y - 9, v.replace("0.0.", "."), 10, "middle", "var(--ink)"))
    o.append(text(L, base + 44, "Labels drop the leading 0.0: “.14” is 0.0.14. On 11-20 npm's latest was 0.0.8 (11-17); today it is 0.0.14 (11-25).", 11, "start", "var(--muted)"))
    return svg(W, H, "hazeljs versions: 0.0.1 to 0.0.8 published by 11-17; 0.0.9 to 0.0.13 made but not published; 0.0.14 published 11-25", o)


def fig_branch_commits():
    """git log --first-parent origin/hazeljs and origin/hazel-jit, commits a day since 11-13 (hazelgrove/hazel, fetched 11-27)"""
    days = [f"2026-11-{d:02d}" for d in range(13, 28)]
    hz = {"2026-11-19": 2, "2026-11-23": 19, "2026-11-24": 5, "2026-11-25": 2, "2026-11-26": 1}
    W, L, R, T, B = 640, 40, 20, 34, 30
    H = 170
    top = 20
    Y = lambda v: (H - B) - v / top * (H - B - T)
    bw = (W - L - R) / len(days)
    o = [text(8, 16, "Commits a day on the hazeljs branch (#2857), first parent: its own commits and its merges of hazel-jit", 12, "start", "var(--muted)")]
    for v in (0, 10, 20):
        o.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="var(--line)"/>')
        o.append(text(L - 6, Y(v) + 4, str(v), 10.5, "end", "var(--muted)"))
    for i, d in enumerate(days):
        x = L + i * bw
        v = hz.get(d, 0)
        if v:
            o.append(f'<rect x="{x + 3:.1f}" y="{Y(v):.1f}" width="{bw - 6:.1f}" height="{Y(0) - Y(v):.1f}" rx="2" fill="var(--accent2)"><title>{d}: {v}</title></rect>')
            o.append(text(x + bw / 2, Y(v) - 4, str(v), 10.5, "middle", "var(--ink)"))
        o.append(text(x + bw / 2, H - B + 14, d[8:], 10, "middle", "var(--muted)"))
    return svg(W, H, "Commits a day on the hazeljs branch since 11-13: 2 on 11-19, 19 on 11-23, 5 on 11-24, 2 on 11-25, 1 on 11-26", o)


# ---------------------------------------------------------------- 3. the back burner

def kind(p):
    if p["number"] in (2857, 2859): return "the two jit PRs"
    if p["baseRefName"] != "dev": return "into another branch"
    return "draft, to dev" if p["isDraft"] else "ready, to dev"


KINDS = (("ready, to dev", "var(--good)"), ("draft, to dev", "var(--warn)"), ("into another branch", "var(--muted)"), ("the two jit PRs", "var(--accent)"))


def fig_open_prs():
    """gh pr list -R hazelgrove/hazel --author @me --state open (066/data/open-prs.json, 11-27): by the week each was opened"""
    prs = json.load(open(os.path.join(DATA, "open-prs.json")))
    wk0 = dt.date(2026, 9, 7)  # a Monday
    weeks = {}
    for p in prs:
        w = (dt.date.fromisoformat(p["createdAt"][:10]) - wk0).days // 7
        weeks.setdefault(w, {}).setdefault(kind(p), []).append(p["number"])
    nw = max(weeks) + 1
    W, L, R, T, B = 640, 40, 20, 50, 44
    H = 260
    top = 12
    Y = lambda v: (H - B) - v / top * (H - B - T)
    bw = (W - L - R) / nw
    o = [text(8, 16, f"Matthew's {len(prs)} open PRs on hazelgrove/hazel, by the week each was opened (Mondays)", 12, "start", "var(--muted)")]
    x = L
    for lab, col in KINDS:
        n = sum(1 for p in prs if kind(p) == lab)
        o.append(f'<rect x="{x}" y="26" width="11" height="11" rx="2" fill="{col}"/>')
        s = f"{lab} ({n})"
        o.append(text(x + 15, 36, s, 11.5, "start", "var(--ink)"))
        x += 30 + 6.3 * len(s)
    for v in (0, 4, 8, 12):
        o.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="var(--line)"/>')
        o.append(text(L - 6, Y(v) + 4, str(v), 10.5, "end", "var(--muted)"))
    for w in range(nw):
        x = L + w * bw
        acc = 0
        for lab, col in KINDS:
            ns = weeks.get(w, {}).get(lab, [])
            if not ns: continue
            o.append(f'<rect x="{x + 4:.1f}" y="{Y(acc + len(ns)):.1f}" width="{bw - 8:.1f}" height="{Y(acc) - Y(acc + len(ns)):.1f}" fill="{col}">'
                     f'<title>{lab}: ' + ", ".join(f"#{n}" for n in sorted(ns)) + '</title></rect>')
            acc += len(ns)
        if acc: o.append(text(x + bw / 2, Y(acc) - 4, str(acc), 10.5, "middle", "var(--ink)"))
        d = wk0 + dt.timedelta(days=7 * w)
        o.append(text(x + bw / 2, H - B + 14, d.strftime("%m-%d"), 10, "middle", "var(--muted)"))
    oldest = min(p["createdAt"][:10] for p in prs)
    o.append(text(L, H - 8, f"Hover a block for its PR numbers. The oldest open one was opened {oldest[5:]}.", 11, "start", "var(--muted)"))
    return svg(W, H, f"{len(prs)} open PRs by the week opened, coloured ready to dev, draft to dev, into another branch, and the two jit PRs", o)


# ---------------------------------------------------------------- 5. the demo

def fig_releases():
    """hazeljs-examples VERSIONS.md (066/data/examples-releases.json): versions a day, and those whose notes name each Gnome game"""
    E = json.load(open(os.path.join(DATA, "examples-releases.json")))
    days = sorted({r["date"] for r in E["rows"]})
    per = {d: [r for r in E["rows"] if r["date"] == d] for d in days}
    W, L, R, T, B = 640, 40, 20, 50, 34
    H = 230
    top = 35
    Y = lambda v: (H - B) - v / top * (H - B - T)
    bw = (W - L - R) / len(days)
    o = [text(8, 16, "hazeljs-examples versions a day, 0.0.1 to 0.0.146, by the Gnome game their notes name", 12, "start", "var(--muted)")]
    cols = (("Gnome world", "var(--accent)"), ("Gnome dig only", "var(--accent2)"), ("other games", "var(--line)"))
    x = L
    for lab, col in cols:
        o.append(f'<rect x="{x}" y="26" width="11" height="11" rx="2" fill="{col}"/>')
        o.append(text(x + 15, 36, lab, 11.5, "start", "var(--ink)"))
        x += 30 + 6.3 * len(lab)
    for v in (0, 10, 20, 30):
        o.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="var(--line)"/>')
        o.append(text(L - 6, Y(v) + 4, str(v), 10.5, "end", "var(--muted)"))
    for i, d in enumerate(days):
        x = L + i * bw
        rs = per[d]
        parts = (sum(r["gnome_world"] for r in rs), sum(r["gnome_dig"] and not r["gnome_world"] for r in rs))
        parts = (parts[0], parts[1], len(rs) - parts[0] - parts[1])
        acc = 0
        for (lab, col), n in zip(cols, parts):
            if not n: continue
            o.append(f'<rect x="{x + 4:.1f}" y="{Y(acc + n):.1f}" width="{bw - 8:.1f}" height="{Y(acc) - Y(acc + n):.1f}" fill="{col}"><title>{d}, {lab}: {n}</title></rect>')
            acc += n
        o.append(text(x + bw / 2, Y(acc) - 4, str(acc), 10.5, "middle", "var(--ink)"))
        o.append(text(x + bw / 2, H - B + 14, d[5:], 10, "middle", "var(--muted)"))
    return svg(W, H, "hazeljs-examples versions a day from 11-15 to 11-27; Gnome dig from 11-22, Gnome world from 11-23", o)


def fig_rules():
    """Gnome world's rules in Hazel (world/rules/*.hz, preamble.hz aside), each module by the day its file was added
    (git log --diff-filter=A, hazeljs-examples main b3ecda4)"""
    adds = (("11-23", ["World"]), ("11-25", ["Fly", "Tail", "Ride", "Boulder", "Pickup", "Wind"]), ("11-26", ["Bunny", "Frog", "Bird"]), ("11-27", ["Jelly"]))
    W, L, T = 700, 20, 30
    H = 150
    o = [text(8, 16, "Gnome world's rules in Hazel, module by module, by the day each was added", 12, "start", "var(--muted)")]
    x, total = L, 0
    for d, mods in adds:
        o.append(text(x, T + 18, d, 11.5, "start", "var(--muted)", 700))
        total += len(mods)
        for j, m in enumerate(mods):
            col, row = j % 3, j // 3
            bx, by = x + col * 62, T + 28 + row * 30
            o.append(f'<rect x="{bx}" y="{by}" width="56" height="24" rx="5" fill="var(--paper)" stroke="var(--accent)" stroke-width="1.6"/>')
            o.append(text(bx + 28, by + 16, m, 11.5, "middle", "var(--ink)"))
        o.append(text(x, T + 104, f"{total} in all", 11, "start", "var(--muted)"))
        x += 62 * min(3, len(mods)) + 30
    return svg(W, H, "Gnome world's Hazel modules: World on 11-23; Fly, Tail, Ride, Boulder, Pickup, Wind on 11-25; Bunny, Frog, Bird on 11-26; Jelly on 11-27", o)


def fig_speedrun():
    """^report(65) #speedrun: Gnome world's speed run, three ways"""
    rows = (("plain JS", 24.7, PLAIN), ("hazel-jit", 25.5, NOW), ("the interpreter", 227.6, THEN))
    W, L, R, T, rh = 460, 120, 70, 30, 30
    H = T + rh * 3 + 40
    X = lambda v: L + v / 240 * (W - L - R)
    o = [text(8, 16, "Gnome world's speed run, its steps' time in seconds", 12, "start", "var(--muted)")]
    for v in (0, 60, 120, 180, 240):
        o.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{H - 34}" stroke="var(--line)"/>')
        o.append(text(X(v), H - 20, f"{v} s", 11, "middle", "var(--muted)"))
    for i, (lab, v, col) in enumerate(rows):
        y = T + 4 + i * rh
        o.append(text(L - 10, y + 14, lab, 12, "end", "var(--ink)"))
        o.append(f'<rect x="{L}" y="{y}" width="{X(v) - L:.1f}" height="18" rx="3" fill="{col}"/>')
        o.append(text(X(v) + 6, y + 14, f"{v} s", 12, "start", "var(--ink)", 700))
    o.append(text(L, H - 4, "The interpreter's row ran 42,000 of the 44,933 steps.", 11, "start", "var(--muted)"))
    return svg(W, H, "Gnome world's speed run: plain JS 24.7 s, hazel-jit 25.5 s, the interpreter about 228 s", o)


JELLY = ('<img src="img/jellyfish-three.png" width="650" height="232" alt="The flying jellyfish in Gnome world 0.0.146, three poses: hovering, mid-pulse, and glowing in rainbow colours" '
         'style="width:100%;max-width:650px;height:auto;display:block;border-radius:6px">')

FIGS = {
    "jit": [(fig_fourway(), "Last week against this week, on the 14 games of hazeljs-examples: hazel-jit as of Thursday 11-19 (each game's compiled.js, from trial/794-games-aot) and hazel-jit now (hazeljs at 2c4a61560f), each game's time a call divided by its plain JS's. GitHub run 45666570615, every answer the same four ways; ^report(65) #fourway.", True),
            (fig_trials(), "The five trials of the night of 11-26, merged: trial/1126-night (abf653a21d), against the hazeljs branch (b1b4e19286): Gnome world's rules on fresh inputs, the range of three rounds on one GitHub runner, every answer the same (^ticket(890)'s timing, 11-26 22:4x).", True),
 ],
    "npm": [(fig_npm(), "hazeljs on npm: <code>npm view hazeljs time</code>, read 2026-11-27 (066/data/npm-time.json). The hollow versions are commits in hazelgrove/hazeljs (branch editor-in-package) that name a version npm does not list: 0.0.9 (99e28ca), 0.0.10 (581ae27), 0.0.11 (b149ed5), 0.0.12 (41c6cb0, “not published”), 0.0.13 (3a4a1cd).", True),
            (fig_build(), "trial/1126-night (abf653a21d) against the hazeljs branch (b1b4e19286): the time to build Gnome world's rules, in Node on one GitHub runner (^ticket(890), 11-26 22:4x): about 8% faster warm. A CPU profile puts 70% of a build in Hazel's statics and 28% in garbage collection, the compiler 0.5% (^report(64)).", False),
            (fig_branch_commits(), "The hazeljs branch of hazelgrove/hazel (#2857), <code>git log --first-parent --since=2026-11-13</code>, fetched 2026-11-27: 29 commits, all from 11-19 on; 11-23 is the move onto dev's Jane Street Core and the first merge of hazel-jit.", True)],
    "back-burner": [(fig_open_prs(), "Matthew's open PRs on hazelgrove/hazel, <code>gh pr list --author @me --state open</code>, read 2026-11-27 (066/data/open-prs.json): 46, of which 24 are drafts. “Into another branch” are stacked PRs (livelits, the JS library).", True)],
    "demo": [(JELLY, "Gnome world 0.0.146 (hazeljs-examples 2026142, live 11-27 07:09): the flying jellyfish, N's ask, hovering, mid-pulse, and glowing after a rainbow cloud. Its flight is Hazel's new Jelly.step, with a JS twin.", True),
             (fig_releases(), "matthewhammer/hazeljs-examples, VERSIONS.md at 2026142 (066/data/examples-releases.json): a version counts for a game if its notes name it. On 11-20, last week, the repo was at 0.0.40, before either Gnome game.", True),
             (fig_rules(), "Gnome world's rules written in Hazel (world/rules/*.hz on main, b3ecda4, preamble.hz aside), each module on the day its file was added: World.hz (6c5db0f), Fly.hz (11ae1ac, 0.0.107) to Wind.hz (ed4a6ab), Bunny.hz (b62c09b, 0.0.141), Frog.hz (0574305, 0.0.142), Bird.hz (7c8f22a, 0.0.143), Jelly.hz (2026142, 0.0.146).", True),
             (fig_speedrun(), "Gnome world's speed run, 44,933 steps, three ways, every answer the same: plain JS, hazel-jit (hazeljs 2c4a61560f) and the interpreter (^report(65) #speedrun). With hazel-jit the rules are 1.3% of the run.", False)],
}
