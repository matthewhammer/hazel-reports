#!/usr/bin/env python3
"""^report(68): Gnome World's Speed Run, Frame by Frame. Asked 2026-11-27 (^ticket(902)): "when I was demoing gnome world (while
using zoom), I used the 'speed run' button and I noticed that the frame rate was very poor, and the 'worst time' reported in the
HUD was hundreds of ms, well above 16.7 ms. can we do a deep analysis of the current performance of a speed run, and determine
what costs are showing up and how to mitigate them? please make a new WIP report, and fix whatever you can without me. second, in
the same report, let's also document the current proportion of hazel vs js code, and whether that's contributing to the slower
speedruns --- or is it some other design decisions we made recently?"

Writes 068/index.html, 068/data/meta.json and 068/img/thumb*.svg from:
  data/frames-RUN.json  hazeljs-examples' 'world speed run, frame by frame' job (node/world-frames.mjs), its log parsed by
                        parse_frames.py (no artifact downloaded):
                          46093539386  the diagnosis: build 1 (0.0.148) four ways, each frame recorded and the thread sampled
                          FINAL        builds 1, 2 and 3 in turn on one runner (before, after, then)
  data/sizes.json       sizes.py: the code's sizes at matthewhammer/hazeljs-examples b085172 (0.0.148)"""
import html, json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(HERE, "data")
s35 = open(os.path.join(ROOT, "035", "index.html")).read(); CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
E = lambda s: html.escape(str(s), quote=True)
RUN_D, RUN_F = "46093539386", open(os.path.join(DATA, "final-run.txt")).read().strip()
def load(r): return json.load(open(os.path.join(DATA, f"frames-{r}.json")))["setups"]
def machine(r):
    p = os.path.join(DATA, f"machine-{r}.txt"); return open(p).read().strip() if os.path.exists(p) else "?"
D, F = load(RUN_D), load(RUN_F)
SZ = json.load(open(os.path.join(DATA, "sizes.json")))
f1 = lambda x: f"{x:.1f}"; f0 = lambda x: f"{x:,.0f}"
fps = lambda ms: f"{1000 / ms:.0f} fps"
pct = lambda a, b: f"{100 * a / b:.0f}%"
missed = lambda S: S["over"]["16.7"] / S["over"]["n"]   # (frames of two refreshes or more: the gaps fall on whole refreshes)

# ================= the builds, numbered (one table; every figure names its build) =================
BUILDS = [
    ("1", "before", "Gnome world 0.0.148 (matthewhammer/hazeljs-examples b085172, 2026-11-27) with a record of each frame for tests, nothing else changed: perf/902-frames <code>5e3734e</code>"),
    ("2", "after", "build 1 with this report’s changes, to be released as 0.0.149: perf/902-frames <code>afb95f3</code>"),
    ("3", "then", "Gnome world 0.0.103 (<code>02b73ab</code>, 2026-11-24), ^report(64)’s “then”: the world planned by Hazel, the gnome’s step and the beavers’ Hazel’s, every other piece JavaScript; its rules built at load by today’s library"),
]
# ================= figure 1: how many frames made the screen's sixtieth of a second =================
ROWS = [("1280×800", [("3", "then-0.0.103"), ("1", "before"), ("2", "after")]),
        ("1920×1080 at 2×", [("1", "before-2x-full"), ("2", "after-2x-full")]),
        ("CPU 4× slower", [("1", "before-cpu4"), ("2", "after-cpu4")])]
def fig_frames():
    W, L, bw, rh = 960, 200, 480, 30; rows = sum(len(r) for _, r in ROWS); H = 60 + rows * rh + len(ROWS) * 26 + 40
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Each setup&#39;s frames, before and after: the share that made one refresh of the screen, two, or three and more">',
         '<style>.l{fill:var(--ink);font:600 13px system-ui,sans-serif}.m{fill:var(--muted);font:12px system-ui,sans-serif}.w{fill:#fff;font:600 11px system-ui,sans-serif}</style>']
    cols = [("one refresh (16.7 ms, 60 fps)", "var(--good)"), ("two (33 ms)", "var(--warn)"), ("three or more (50 ms and over)", "var(--bad)")]
    for k, (t, c) in enumerate(cols): o.append(f'<rect x="{L + k * 200}" y="12" width="12" height="12" fill="{c}"/><text class="m" x="{L + 18 + k * 200}" y="22">{E(t)}</text>')
    y = 44
    for title, rs in ROWS:
        o.append(f'<text class="l" x="8" y="{y + 14}">{E(title)}</text>'); y += 22
        for b, key in rs:
            S = F[key]; n = S["over"]["n"]; two = S["over"]["16.7"] - S["over"]["33"]; three = S["over"]["33"]; one = n - two - three
            name = {"1": "build 1, before", "2": "build 2, after", "3": "build 3, then (0.0.103)"}[b]
            o.append(f'<text class="m" x="22" y="{y + 17}">{E(name)}</text>')
            x = L
            for v, (_, c) in zip([one, two, three], cols):
                w = bw * v / n
                o.append(f'<rect x="{x:.1f}" y="{y + 3}" width="{max(w, 0.5):.1f}" height="{rh - 8}" fill="{c}"><title>{v:,} of {n:,} frames</title></rect>')
                if w > 44: o.append(f'<text class="w" x="{x + 5:.1f}" y="{y + 17}">{100 * v / n:.0f}%</text>')
                x += w
            o.append(f'<text class="m" x="{L + bw + 8}" y="{y + 17}">median {fps(S["gap"]["median"])} · worst {f0(S["gap"]["worst"])} ms</text>')
            y += rh
        y += 4
    o.append(f'<text class="m" x="8" y="{H - 12}">Build 1 (0.0.148), 2 (0.0.149) and 3 (0.0.103) in turn on one GitHub runner ({E(machine(RUN_F))}), run {RUN_F}; each frame’s gap from the one before.</text>')
    o.append('</svg>'); return "".join(o)

# ================= figure 2: one frame of the speed run, its steps and its drawing, against the screen's refresh =================
def fig_budget():
    W, L, sc = 960, 250, 18; H = 230
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="A typical frame of the speed run: its steps and its drawing, before and after, against the screen&#39;s 16.7 ms">',
         '<style>.l{fill:var(--ink);font:600 13px system-ui,sans-serif}.m{fill:var(--muted);font:12px system-ui,sans-serif}.w{fill:#fff;font:600 11px system-ui,sans-serif}</style>']
    rows = [("1280×800, build 1", F["before"]), ("1280×800, build 2", F["after"]), ("1920×1080 at 2×, build 1", F["before-2x-full"]), ("1920×1080 at 2×, build 2", F["after-2x-full"])]
    for k, t in enumerate([16.7, 33.3]):
        x = L + t * sc; o.append(f'<line x1="{x:.1f}" y1="20" x2="{x:.1f}" y2="{H - 34}" stroke="var(--muted)" stroke-dasharray="4 3"/><text class="m" x="{x + 4:.1f}" y="30">{t} ms</text>')
    y = 40
    for name, S in rows:
        st, dr = S["steps"]["median"], S["drawing"]["median"]
        o.append(f'<text class="m" x="8" y="{y + 16}">{E(name)}</text>')
        o.append(f'<rect x="{L}" y="{y + 2}" width="{st * sc:.1f}" height="20" fill="var(--accent2)"><title>steps {st} ms ({S["steps"]["n"]:.0f})</title></rect>')
        if st * sc > 90: o.append(f'<text class="w" x="{L + 6}" y="{y + 16}">steps {st} ms ({S["steps"]["n"]:.0f})</text>')
        o.append(f'<rect x="{L + st * sc:.1f}" y="{y + 2}" width="{dr * sc:.1f}" height="20" fill="var(--warn)"><title>drawing {dr} ms</title></rect>')
        o.append(f'<text class="m" x="{L + (st + dr) * sc + 6:.1f}" y="{y + 16}">drawing {dr} ms → the frame’s median {S["gap"]["median"]} ms</text>')
        y += 36
    o.append(f'<text class="m" x="8" y="{H - 12}">Medians of each frame’s steps and drawing, run {RUN_F}; JavaScript’s work only, before the browser puts the frame on the screen.</text>')
    o.append('</svg>'); return "".join(o)

# ================= figure 3: where a step goes, and where the drawing goes =================
def fig_parts():
    S = D["hazel"]; T = D["hazel-2x-full"]
    W, L, bw = 960, 250, 600; H = 230
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Where the speed run&#39;s steps and drawing spend their time, build 1">',
         '<style>.l{fill:var(--ink);font:600 13px system-ui,sans-serif}.m{fill:var(--muted);font:12px system-ui,sans-serif}.w{fill:#fff;font:600 11px system-ui,sans-serif}</style>']
    pal = ["var(--accent2)", "var(--accent)", "var(--warn)", "var(--good)", "var(--bad)", "#6b737d", "#8b5cf6", "#0ea5e9"]
    rows = [("the steps, 1280×800", S["stepParts"]), ("the drawing, 1280×800", S["drawParts"]), ("the drawing, 1920×1080 at 2×", T["drawParts"])]
    y = 20
    for name, P in rows:
        items = sorted(P.items(), key=lambda kv: -kv[1]); top = items[:6]; rest = 100 - sum(v for _, v in top)
        o.append(f'<text class="l" x="8" y="{y + 18}">{E(name)}</text>'); x = L
        for k, (n, v) in enumerate(top + [("the rest", rest)]):
            w = bw * v / 100; c = pal[k % len(pal)] if n != "the rest" else "var(--line)"
            o.append(f'<rect x="{x:.1f}" y="{y + 4}" width="{max(w, 0.5):.1f}" height="22" fill="{c}"><title>{E(n)} {v:.1f}%</title></rect>')
            if w > 70: o.append(f'<text class="w" x="{x + 5:.1f}" y="{y + 19}">{E(n)} {v:.0f}%</text>')
            x += w
        small = [f"{n} {v:.1f}%" for n, v in top if bw * v / 100 <= 70]
        if small: o.append(f'<text class="m" x="{L}" y="{y + 42}">{E(" · ".join(small))}</text>')
        y += 64
    o.append(f'<text class="m" x="8" y="{H - 12}">Build 1, run {RUN_D} ({E(machine(RUN_D))}): ⏱’s parts of every step, and the drawing’s parts, over the whole recorded run.</text>')
    o.append('</svg>'); return "".join(o)

# ================= figure 4: Hazel's share, by size and by time =================
def fig_share():
    W, L, bw = 960, 250, 620; H = 250
    app, hz = SZ["app_js"], SZ["hz_total"]; shared = sum(SZ["shared"].values())
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Hazel&#39;s share of Gnome world: by the size of its code, and by the time the page&#39;s thread spends in it">',
         '<style>.l{fill:var(--ink);font:600 13px system-ui,sans-serif}.m{fill:var(--muted);font:12px system-ui,sans-serif}.w{fill:#fff;font:600 11px system-ui,sans-serif}</style>']
    y = 16
    tot = hz + app + shared
    o.append(f'<text class="l" x="8" y="{y + 18}">the code, by size</text><text class="m" x="8" y="{y + 34}">characters</text>'); x = L
    for n, v, c in [("Hazel’s rules", hz, "var(--accent)"), ("app.js", app, "var(--accent2)"), ("plain.js and the shared scripts", shared, "var(--line)")]:
        w = bw * v / tot; o.append(f'<rect x="{x:.1f}" y="{y + 4}" width="{w:.1f}" height="22" fill="{c}"><title>{E(n)}: {v:,}</title></rect>')
        if w > 80: o.append(f'<text class="w" x="{x + 5:.1f}" y="{y + 19}">{E(n)} {100 * v / tot:.0f}%</text>')
        x += w
    o.append(f'<text class="m" x="{L}" y="{y + 44}">Hazel {hz:,} characters (comments left out) in {len(SZ["hz"])} modules; app.js {app:,}; the rest {shared:,}</text>')
    y += 70
    for name, key, R in [("the thread, 1280×800", "after", F), ("the thread, 1920×1080 at 2×", "after-2x-full", F), ("then: 0.0.103, 1280×800", "then-0.0.103", F)]:
        K = R[key]["kinds"]; o.append(f'<text class="l" x="8" y="{y + 18}">{E(name)}</text>'); x = L
        parts = [("the rules compiled from Hazel", "var(--accent)"), ("the page (app.js)", "var(--accent2)"), ("native (canvas, DOM, builtins)", "var(--warn)"), ("(program)", "#6b737d"), ("garbage collection", "var(--bad)")]
        for n, c in parts:
            v = K.get(n, 0); w = bw * v / 100; o.append(f'<rect x="{x:.1f}" y="{y + 4}" width="{max(w, 0.8):.1f}" height="22" fill="{c}"><title>{E(n)} {v:.1f}%</title></rect>')
            lab = {"the rules compiled from Hazel": "Hazel", "the page (app.js)": "app.js", "native (canvas, DOM, builtins)": "canvas, DOM", "(program)": "the browser", "garbage collection": "GC"}[n]
            if w > 62: o.append(f'<text class="w" x="{x + 5:.1f}" y="{y + 19}">{lab} {v:.0f}%</text>')
            x += w
        o.append(f'<text class="m" x="{L + bw + 6}" y="{y + 19}">Hazel {K.get("the rules compiled from Hazel", 0):.1f}%</text>')
        y += 40
    o.append(f'<text class="m" x="8" y="{H - 12}">Sizes at b085172 (0.0.148). The thread: run {RUN_F}, builds 2 and 3, V8’s profiler every 0.5 ms, idle left out; “the browser” is time V8 gives no function (much of it rasterizing).</text>')
    o.append('</svg>'); return "".join(o)

# ================= the tables =================
def t_frames():
    hd = ("<table class=\"nums\"><thead><tr><th class=\"l\">setup</th><th>build</th><th>median frame</th><th>frames missing a refresh</th>"
          "<th>50 ms and over</th><th>worst</th><th>steps a frame</th><th>drawing, median</th><th>the speed run’s real time</th></tr></thead><tbody>")
    rows = []
    for title, rs in ROWS:
        for b, key in rs:
            S = F[key]; run = f'{S["realS"]:.1f} s' if S.get("realS") else ("not finished in 120 s" if key != "then-0.0.103" else "—")
            st = f'{S["steps"]["n"]:.0f}' if S.get("steps") else "—"; dr = f'{S["drawing"]["median"]} ms' if S.get("drawing") else "—"
            rows.append(f'<tr><td class="l">{E(title)}</td><td>{b}</td><td>{S["gap"]["median"]} ms ({fps(S["gap"]["median"])})</td><td>{pct(S["over"]["16.7"], S["over"]["n"])}</td>'
                        f'<td>{S["over"]["33"]:,} of {S["over"]["n"]:,}</td><td>{f0(S["gap"]["worst"])} ms</td><td>{st}</td><td>{dr}</td><td>{run}</td></tr>')
    return hd + "".join(rows) + "</tbody></table>"
def t_worst():
    rows = []
    for key, title in [("hazel", "1280×800"), ("hazel-2x-full", "1920×1080 at 2×"), ("hazel-cpu4", "CPU 4× slower")]:
        for w in D[key]["worst"][:4]:
            dp = sorted(w.get("drawParts", {}).items(), key=lambda kv: -kv[1])[:2]; sp = sorted(w.get("slowestParts", {}).items(), key=lambda kv: -kv[1])[:1]
            rows.append(f'<tr><td class="l">{E(title)}</td><td>{f0(w["span"])} ms</td><td class="l">{E(w.get("phase", ""))}</td><td>{w["stepsMs"]} ms ({w["steps"]})</td>'
                        f'<td>{w["draw"]} ms</td><td class="l">{E(", ".join(f"{k} {v}" for k, v in dp))}</td><td class="l">{E(w["sampled"].split(", ")[0] if w["sampled"] else "")}</td></tr>')
    return ("<table class=\"nums\"><thead><tr><th class=\"l\">setup</th><th>the frame</th><th class=\"l\">phase</th><th>its steps</th><th>its drawing</th>"
            "<th class=\"l\">the drawing’s largest parts (ms)</th><th class=\"l\">sampled most (ms)</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>")
def t_builds():
    return ("<table class=\"nums\"><thead><tr><th>build</th><th class=\"l\">name</th><th class=\"l\">what</th></tr></thead><tbody>" +
            "".join(f'<tr><td>{n}</td><td class="l">{E(k)}</td><td class="l">{v}</td></tr>' for n, k, v in BUILDS) + "</tbody></table>")
def t_sizes():
    rows = "".join(f'<tr><td class="l">{E(k)}</td><td>{v:,}</td><td>{100 * v / SZ["app_js"]:.0f}%</td></tr>' for k, v in SZ["app_by"].items())
    hz = "".join(f'<tr><td class="l">{E(k)}.hz</td><td>{v["chars"]:,}</td><td>{v["lines"]:,}</td></tr>' for k, v in sorted(SZ["hz"].items(), key=lambda kv: -kv[1]["chars"]))
    return ('<div class="two"><table class="nums"><thead><tr><th class="l">app.js, by what its top-level definitions do</th><th>characters</th><th>share</th></tr></thead><tbody>' + rows +
            f'<tr><td class="l"><b>app.js</b></td><td><b>{SZ["app_js"]:,}</b></td><td>100%</td></tr></tbody></table>'
            '<table class="nums"><thead><tr><th class="l">Hazel’s rules</th><th>characters</th><th>lines</th></tr></thead><tbody>' + hz +
            f'<tr><td class="l"><b>all</b></td><td><b>{SZ["hz_total"]:,}</b></td><td>{SZ["hz_lines"]:,}</td></tr></tbody></table></div>')

# ================= the numbers the prose uses =================
B, A, B2, A2, B4, A4, T3, AP = F["before"], F["after"], F["before-2x-full"], F["after-2x-full"], F["before-cpu4"], F["after-cpu4"], F["then-0.0.103"], F["after-plain"]
kz = lambda S: S["kinds"].get("the rules compiled from Hazel", 0)
water = lambda S: S["stepParts"].get("water", 0)
N = {
    "b_missed": pct(B["over"]["16.7"], B["over"]["n"]), "a_missed": pct(A["over"]["16.7"], A["over"]["n"]),
    "b2_med": fps(B2["gap"]["median"]), "a2_med": fps(A2["gap"]["median"]), "b2_missed": pct(B2["over"]["16.7"], B2["over"]["n"]), "a2_missed": pct(A2["over"]["16.7"], A2["over"]["n"]),
    "b4_med": fps(B4["gap"]["median"]), "a4_med": fps(A4["gap"]["median"]), "b4_50": f'{B4["over"]["33"]:,}', "a4_50": f'{A4["over"]["33"]:,}', "b4_n": f'{B4["over"]["n"]:,}', "a4_n": f'{A4["over"]["n"]:,}',
    "b_worst": f0(B["gap"]["worst"]), "a_worst": f0(A["gap"]["worst"]), "b2_worst": f0(B2["gap"]["worst"]), "a2_worst": f0(A2["gap"]["worst"]), "b4_worst": f0(B4["gap"]["worst"]), "a4_worst": f0(A4["gap"]["worst"]),
    "d_worst": f0(max(F[k]["gap"]["worst"] for k in ("before", "before-2x-full", "before-cpu4"))),
    "hz_b": f'{kz(B):.1f}%', "b_hud": f'{B["drawParts"].get("hud", 0):.0f}%', "b_roots": f'{B["drawParts"].get("roots", 0):.0f}%', "then_missed": pct(T3["over"]["16.7"], T3["over"]["n"]), "then_worst": f0(T3["gap"]["worst"]),
    "hz_d": f'{min(kz(D[k]) for k in ("hazel", "hazel-2x-full", "hazel-cpu4")):.1f}% to {max(kz(D[k]) for k in ("hazel", "hazel-2x-full", "hazel-cpu4")):.1f}%',
    "hz_t": f'{kz(T3):.1f}%', "water_d": f'{min(water(D[k]) for k in D):.0f}% to {max(water(D[k]) for k in D):.0f}%',
    "hz_size": pct(SZ["hz_total"], SZ["hz_total"] + SZ["app_js"]), "hz_chars": f'{SZ["hz_total"]:,}', "app_chars": f'{SZ["app_js"]:,}',
    "draw_app": pct(SZ["app_by"]["drawing"], SZ["app_js"]),
    "b_real": f'{B["realS"]:.1f} s' if B.get("realS") else "?", "a_real": f'{A["realS"]:.1f} s' if A.get("realS") else "?",
    "b2_real": f'{B2["realS"]:.1f} s' if B2.get("realS") else "?", "a2_real": f'{A2["realS"]:.1f} s' if A2.get("realS") else "over 120 s (still in its gems when the job’s two minutes ended)",
    "b_steps": f'{B["steps"]["n"]:.0f}', "a_steps": f'{A["steps"]["n"]:.0f}', "b2_steps": f'{B2["steps"]["n"]:.0f}', "a2_steps": f'{A2["steps"]["n"]:.0f}',
    "b_draw": f'{B["drawing"]["median"]} ms', "b2_draw": f'{B2["drawing"]["median"]} ms', "a2_draw": f'{A2["drawing"]["median"]} ms',
    "ap_med": fps(AP["gap"]["median"]), "ap_missed": pct(AP["over"]["16.7"], AP["over"]["n"]), "dplain_missed": pct(D["plain"]["over"]["16.7"], D["plain"]["over"]["n"]), "dhazel_missed": pct(D["hazel"]["over"]["16.7"], D["hazel"]["over"]["n"]),
    "a_put": f'{A.get("putOff", 0):,}', "a2_put": f'{A2.get("putOff", 0):,}', "a2_painted": f'{A2.get("painted", 0):,}',
}
FIG = {"frames": fig_frames(), "budget": fig_budget(), "parts": fig_parts(), "share": fig_share(), "t_frames": t_frames(), "t_worst": t_worst(), "t_builds": t_builds(), "t_sizes": t_sizes()}
assert not set(N) & set(FIG), set(N) & set(FIG)   # (a number named as a figure or table would replace it)
FIG.update(N)
FIG["updated"] = updated; FIG["run_f"] = RUN_F; FIG["run_d"] = RUN_D; FIG["m_f"] = E(machine(RUN_F)); FIG["m_d"] = E(machine(RUN_D))

body = open(os.path.join(HERE, "body.html"), encoding="utf-8").read()
for k, v in FIG.items(): body = body.replace("{{" + k + "}}", str(v))
import re
left = re.findall(r"\{\{(\w+)\}\}", body); assert not left, left
TITLE = "Gnome World’s Speed Run, Frame by Frame"
DESC = (f"Why Gnome world's speed run played at a poor frame rate, with frames of hundreds of milliseconds on a busy laptop, and what 0.0.149 changes. "
        f"Not Hazel: its compiled rules are {N['hz_d']} of the page's busy time, and with every piece in plain JavaScript the frames are the same. "
        f"The run gave its steps a fixed 12 ms of every frame, so any drawing over 4.7 ms missed the screen's refresh; and each picture coming into view was painted in the frame that showed it, several at once. "
        f"Now the steps take what the frame leaves, and a frame paints 4 ms of new pictures: in a 1920×1080 window at 2×, {N['b2_med']} becomes {N['a2_med']}. "
        f"Hazel is {N['hz_size']} of the code.")
EXTRA = """
  figure.chart svg { width: 100%; height: auto; display: block; }
  table.nums td, table.nums th { text-align: right; font-variant-numeric: tabular-nums; } table.nums td.l, table.nums th.l { text-align: left; }
  .two { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; } @media (max-width: 760px) { .two { grid-template-columns: 1fr; } }
  .wrap { overflow-x: auto; }
"""
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{E(DESC)}\">\n<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(head + body)

def thumb(mode):
    base = ".h{fill:#1f2328;font:700 15px system-ui,sans-serif}.m{fill:#5b6470;font:10px system-ui,sans-serif}.k{fill:#1f2328;font:700 12px system-ui,sans-serif}.g{fill:#15803d}.a{fill:#b45309}.r{fill:#b91c1c}"
    dark = ".h{fill:#e8e6e3}.m{fill:#a2a9b3}.k{fill:#e8e6e3}.g{fill:#4ade80}.a{fill:#fbbf24}.r{fill:#f87171}"
    style = base + ("\n" + dark if mode == "dark" else "\n@media (prefers-color-scheme: dark) {" + dark + "}" if mode == "auto" else "")
    bars = []
    for i, (name, S) in enumerate([("1920×1080 at 2×, 0.0.148", B2), ("1920×1080 at 2×, 0.0.149", A2)]):
        n = S["over"]["n"]; two = S["over"]["16.7"] - S["over"]["33"]; three = S["over"]["33"]; one = n - two - three; x = 16; y = 66 + i * 44
        bars.append(f'<text class="m" x="16" y="{y - 4}">{name}: median {fps(S["gap"]["median"])}</text>')
        for v, c in [(one, "g"), (two, "a"), (three, "r")]:
            w = 288 * v / n; bars.append(f'<rect class="{c}" x="{x:.1f}" y="{y}" width="{w:.1f}" height="16"/>'); x += w
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" width="320" height="200">\n<style>{style}\n</style>\n'
            '<text class="h" x="16" y="26">Gnome world’s speed run</text>\n<text class="m" x="16" y="42">frames at one refresh, two, three or more</text>\n'
            + "".join(bars) + f'\n<text class="m" x="16" y="168">Hazel’s compiled rules: {N["hz_d"]} of the time</text>\n'
            '<text class="m" x="16" y="184">the cost: a fixed 12 ms of steps, and pictures painted at once</text>\n</svg>\n')
os.makedirs(os.path.join(HERE, "img"), exist_ok=True)
for name, mode in [("thumb-light.svg", "light"), ("thumb-dark.svg", "dark"), ("thumb.svg", "auto")]: open(os.path.join(HERE, "img", name), "w").write(thumb(mode))
meta = {"title": TITLE, "blurb": DESC,
        "builds": {f"build {n} ({k})": re.sub("<[^>]+>", "", v) for n, k, v in BUILDS},
        "runs": {"diagnosis": f"matthewhammer/hazeljs-examples 'world speed run, frame by frame' run {RUN_D} (perf/902-frames 5e3734e), one GitHub runner ({machine(RUN_D)}), headless Chrome: build 1 four ways (Hazel's rules at 1280×800; ⚡ plain JavaScript at 1280×800; Hazel's rules full screen at 1920×1080 CSS px on a 2× display; Hazel's rules with the CPU 4× slower)",
                 "before and after": f"the same job, run {RUN_F} (perf/902-frames afb95f3), one GitHub runner ({machine(RUN_F)}): builds 1 and 2 in turn, the same setups, and build 3 at 1280×800",
                 "sizes": "068/sizes.py at matthewhammer/hazeljs-examples b085172 (0.0.148)"},
        "measures": {"gap": "the time from one frame to the next, as requestAnimationFrame gives it (ms); it falls on whole refreshes of the screen, 16.7, 33.3, 50.0 ms",
                     "steps": "the time a frame spends stepping the world (ms), and how many steps", "drawing": "the time a frame spends drawing (ms)",
                     "parts": "⏱'s parts of each step and the drawing's parts, summed over the run, as shares",
                     "thread": "V8's CPU profiler, a sample each 0.5 ms, idle left out: each sample's function, grouped by its script; '(program)' is time V8 gives no function"},
        "files": ["data/frames-*.log", "data/frames-*.json", "data/sizes.json", "parse_frames.py", "sizes.py", "gen068.py"]}
json.dump(meta, open(os.path.join(DATA, "meta.json"), "w"), indent=1, ensure_ascii=False)
print("wrote 068/index.html;", updated)
for k in N: print(f"  {k}: {N[k]}")
