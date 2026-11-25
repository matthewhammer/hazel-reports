#!/usr/bin/env python3
"""^report(64): Gnome World, which parts are Hazel. Builds 064/index.html from 063's look, the measured data
(data/measured.json: Hazel calls timed in the page, the roots World.roots grew for an oak) and the sizes of the code."""
import json, re, html, os
HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(HERE, "data/measured.json")))
head063 = open(os.path.join(HERE, "../063/index.html"), encoding="utf-8").read()
style = head063[head063.index("<style>"):head063.index("</style>") + len("</style>")]
style = style.replace("</style>", "  table.nums td, table.nums th { text-align: right; font-variant-numeric: tabular-nums; } table.nums td.l, table.nums th.l { text-align: left; }\n</style>")   # (the table of each piece so far)
E = html.escape
HZ, JS = "var(--accent)", "var(--accent2)"
T = M["times"]
# ---- the sizes of the code (characters, comments left out of the Hazel), measured at 02b73ab
hz_parts = [("the world's plan", 13835, "plan, its helpers, the villages, the houses, the kinds of ground"), ("the villagers' words", 11107, "greet"),
            ("the gnome's step", 8825, "step, finish, slope_at, slide_vx, dig_ahead, tile"), ("the beavers and their dams", 3378, "beaver, water_row"),
            ("roots and mycelium", 2541, "grow, roots, threads"), ("arithmetic", 526, "md, next, absi, hash, cat, has")]
js_parts = [("drawing", 311422), ("simulation", 49885), ("building the world", 37253), ("rules, input, setup", 20972), ("save and load", 10852), ("the speed run", 10344)]
HZ_TOT, JS_TOT = 40213, 443696
def fmt(n): return f"{n:,}"
# ---- figure 1: who owns what, by size
def fig_split():
    W, x0, bw = 900, 150, 720; sc = bw / JS_TOT; out = [f'<svg viewBox="0 0 {W} 250" role="img" aria-label="The code by size: Hazel 40 KB, JavaScript 444 KB">']
    out.append('<style>.l{fill:var(--ink);font:600 14px system-ui,sans-serif}.s{fill:var(--muted);font:12px system-ui,sans-serif}.w{fill:#fff;font:600 11px system-ui,sans-serif}</style>')
    y = 40; out.append(f'<text class="l" x="10" y="{y + 18}">Hazel</text><text class="s" x="10" y="{y + 34}">World.hz, 32 functions</text>')
    x = x0; shades = [1, 0.85, 0.7, 0.55, 0.42, 0.3]
    for (name, n, _), op in zip(hz_parts, shades): w = n * sc; out.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="28" fill="{HZ}" opacity="{op}"><title>{E(name)}: {fmt(n)} characters</title></rect>'); x += w
    out.append(f'<text class="l" x="{x + 8:.1f}" y="{y + 19}">{fmt(HZ_TOT)} characters (8% of the code)</text>')
    ly = y + 50
    for i, (name, n, _) in enumerate(hz_parts): cx = x0 + (i % 3) * 240; cy = ly + (i // 3) * 18; out.append(f'<rect x="{cx}" y="{cy - 10}" width="11" height="11" fill="{HZ}" opacity="{shades[i]}"/><text class="s" x="{cx + 16}" y="{cy}">{E(name)} {fmt(n)}</text>')
    y = 150; out.append(f'<text class="l" x="10" y="{y + 18}">JavaScript</text><text class="s" x="10" y="{y + 34}">app.js, 160 functions</text>')
    x = x0
    for (name, n), op in zip(js_parts, shades):
        w = n * sc; out.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="28" fill="{JS}" opacity="{op}"><title>{E(name)}: {fmt(n)} characters</title></rect>')
        if w > 70: out.append(f'<text class="w" x="{x + 6:.1f}" y="{y + 18}">{E(name)}</text>')
        x += w
    ly = y + 50
    for i, (name, n) in enumerate(js_parts): cx = x0 + (i % 3) * 240; cy = ly + (i // 3) * 18; out.append(f'<rect x="{cx}" y="{cy - 10}" width="11" height="11" fill="{JS}" opacity="{shades[i]}"/><text class="s" x="{cx + 16}" y="{cy}">{E(name)} {fmt(n)} ({100 * n / JS_TOT:.0f}%)</text>')
    out.append('</svg>'); return "".join(out)
# ---- figure 2: one step of the world, animated: a playhead over the step's parts, Hazel's on the top lane
def fig_step():
    parts = [("keys → Pad", "js", "S.keys packed into a Pad record"), ("World.step", "hz", "the gnome: 0.016 ms"), ("events", "js", "digOut, sounds, hearts"),
             ("boulders", "js", ""), ("water", "js", "2.2 ms: every wet tile"), ("World.beaver ×5", "hz", "every 6th step"), ("wind, squirrels", "js", "smoke, leaves too"),
             ("villagers", "js", "they walk in JS"), ("wildlife", "js", "birds, frogs, insects"), ("bunnies · Clover", "js", ""), ("music", "js", "every 15th step"), ("draw", "js", "the frame: canvas")]
    W, H = 960, 300; n = len(parts); bw = (W - 40) / n
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="One step of the world, in order: Hazel is called for the gnome and, every sixth step, for each beaver; the rest is JavaScript">']
    out.append('<style>.t{font:600 11.5px system-ui,sans-serif;fill:var(--ink)}.n{font:10.5px system-ui,sans-serif;fill:var(--muted)}.lane{font:600 12px system-ui,sans-serif;fill:var(--muted)}</style>')
    out.append(f'<text class="lane" x="20" y="22">Hazel (compiled by hazel-jit)</text><text class="lane" x="20" y="136">JavaScript</text>')
    for i, (name, who, note) in enumerate(parts):
        x = 20 + i * bw; y = 32 if who == "hz" else 146; col = HZ if who == "hz" else JS
        out.append(f'<rect x="{x + 3:.1f}" y="{y}" width="{bw - 6:.1f}" height="54" rx="8" fill="{col}" fill-opacity="0.2" stroke="{col}" stroke-width="1.5"/>')
        words = name.split(" ")
        lines = [" ".join(words[:2]), " ".join(words[2:])] if len(name) > 14 else [name]
        for k, ln in enumerate(lines): out.append(f'<text class="t" x="{x + bw / 2:.1f}" y="{y + 22 + k * 14}" text-anchor="middle">{E(ln)}</text>')
        if note:
            nw = note.split(" "); l1 = " ".join(nw[:2]); l2 = " ".join(nw[2:])
            out.append(f'<text class="n" x="{x + bw / 2:.1f}" y="{y + 68}" text-anchor="middle">{E(l1)}</text>')
            if l2: out.append(f'<text class="n" x="{x + bw / 2:.1f}" y="{y + 81}" text-anchor="middle">{E(l2)}</text>')
    out.append(f'<line x1="20" y1="122" x2="{W - 20}" y2="122" stroke="var(--line)"/>')
    out.append(f'<rect x="20" y="28" width="4" height="176" fill="var(--warn)" rx="2"><animate attributeName="x" values="20;{W - 24};{W - 24}" keyTimes="0;0.9;1" dur="6s" repeatCount="indefinite"/></rect>')
    out.append(f'<text class="n" x="20" y="{H - 30}">To scale, the step itself (2.4 ms, before drawing): </text>')
    tot = 2.4; sx = 330; tw = W - sx - 20
    out.append(f'<rect x="{sx}" y="{H - 44}" width="{tw * 2.2 / tot:.1f}" height="16" fill="{JS}" opacity="0.7"><title>the water: 2.2 ms</title></rect>')
    out.append(f'<rect x="{sx + tw * 2.2 / tot:.1f}" y="{H - 44}" width="{tw * 0.18 / tot:.1f}" height="16" fill="{JS}" opacity="0.35"><title>the rest of the JavaScript: about 0.2 ms</title></rect>')
    out.append(f'<rect x="{sx + tw * 2.38 / tot:.1f}" y="{H - 44}" width="{max(1.5, tw * 0.016 / tot):.1f}" height="16" fill="{HZ}"><title>World.step: 0.016 ms</title></rect>')
    out.append(f'<text class="n" x="{sx}" y="{H - 10}">water 2.2 ms · other JavaScript ≈ 0.2 ms · Hazel 0.016 ms (the thin purple line at the end)</text></svg>')
    return "".join(out)
# ---- figure 3: an event's way, a dot travelling from the key to the effect
def fig_events():
    W, H = 960, 230
    nodes = [(70, 70, "keydown ←→↑↓ X", "js"), (230, 70, "S.keys", "js"), (390, 70, "Pad record", "js"), (560, 70, "World.step", "hz"), (730, 70, "Gnome record, ev", "hz"), (890, 70, "effects", "js")]
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="How a key press reaches Hazel and comes back">']
    out.append('<style>.t{font:600 12px system-ui,sans-serif;fill:var(--ink)}.n{font:11px system-ui,sans-serif;fill:var(--muted)}</style>')
    for i, (x, y, name, who) in enumerate(nodes):
        col = HZ if who == "hz" else JS; out.append(f'<rect x="{x - 66}" y="{y - 22}" width="132" height="44" rx="10" fill="{col}" opacity="0.15" stroke="{col}"/><text class="t" x="{x}" y="{y + 4}" text-anchor="middle">{E(name)}</text>')
        if i: out.append(f'<line x1="{nodes[i - 1][0] + 66}" y1="{y}" x2="{x - 66}" y2="{y}" stroke="var(--muted)" stroke-width="1.5" marker-end="url(#ah3)"/>')
    out.append('<defs><marker id="ah3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="var(--muted)"/></marker></defs>')
    notes = [(70, "a listener sets a key"), (230, "held keys, in the page"), (390, "dx, up, down, jump, dig"), (560, "with Gnome and Near: 3 records in"), (730, "ev: 0 nothing, 1 dug, 2 jump, 3 splash, 4 no breath, 5 dive"), (890, "digOut, a sound, a heart")]
    for x, t in notes:
        words = t.split(" "); lines = []; cur = ""
        for w in words:
            if len(cur) + len(w) > 22: lines.append(cur); cur = w
            else: cur = (cur + " " + w).strip()
        lines.append(cur)
        for k, ln in enumerate(lines): out.append(f'<text class="n" x="{x}" y="{112 + k * 14}" text-anchor="middle">{E(ln)}</text>')
    out.append(f'<circle r="7" fill="var(--warn)"><animateMotion dur="4s" repeatCount="indefinite" path="M70,70 L890,70" keyPoints="0;1;1" keyTimes="0;0.8;1" calcMode="linear"/></circle>')
    out.append(f'<text class="n" x="20" y="{H - 34}">JavaScript only, never through Hazel: B (build a plank, a bridge, a ladder), R (ride Clover), M (the map), 💾 📂 🔄, and 🏃 the speed run,</text>')
    out.append(f'<text class="n" x="20" y="{H - 16}">which steers the gnome by pressing the same keys a player would (it plans its way over the tiles in JavaScript).</text></svg>')
    return "".join(out)
# ---- figure 4: what World.step sees: the window of tiles, packed; on Clover, without the pack and the gear, the page changes it
def fig_near():
    W, H = 960, 330; cs = 46
    grid = [["air", "air", "air"], ["air", "air", "ladder"], ["air", "air", "ladder"], ["air", "gnome", "water"], ["soil", "soil", "water"]]
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="The three by five tiles round the gnome, as World.step sees them, on foot and on Clover">']
    out.append('<style>.t{font:600 12px system-ui,sans-serif;fill:var(--ink)}.n{font:11px system-ui,sans-serif;fill:var(--muted)}.c{font:600 11px ui-monospace,monospace;fill:var(--ink)}</style>')
    def panel(ox, title, rabbit):
        o = [f'<text class="t" x="{ox}" y="22">{E(title)}</text>']
        codes = []
        for r, row in enumerate(grid):
            rc = []
            for c, k in enumerate(row):
                x, y = ox + c * cs, 36 + r * cs
                if k == "soil": fill, code = "#8b5e3c", 1
                elif k == "water": fill, code = "#3b82f6", 16
                elif k == "ladder": fill, code = "#d4a35a", 32
                else: fill, code = "none", 0
                changed = rabbit and (k == "ladder" or (k == "water" and r <= 3))
                if rabbit and k == "ladder": code = 0
                if rabbit and k == "water" and r <= 3: fill, code = "#6b7280", 10
                o.append(f'<rect x="{x}" y="{y}" width="{cs - 2}" height="{cs - 2}" fill="{fill}" opacity="{0.55 if fill != "none" else 0}" stroke="var(--line)"/>')
                if k == "ladder" and not rabbit: o.append(f'<path d="M{x + 12},{y + 2}V{y + cs - 4}M{x + cs - 14},{y + 2}V{y + cs - 4}M{x + 12},{y + 14}H{x + cs - 14}M{x + 12},{y + 30}H{x + cs - 14}" stroke="#7a4a26" stroke-width="2.5"/>')
                if k == "gnome": o.append(f'<text x="{x + cs / 2 - 1}" y="{y + 31}" text-anchor="middle" font-size="24">{"🐇" if rabbit else "🧑‍🌾"}</text>')
                o.append(f'<text class="c" x="{x + 3}" y="{y + cs - 6}">{code}</text>')
                if changed: o.append(f'<rect x="{x - 1}" y="{y - 1}" width="{cs}" height="{cs}" fill="none" stroke="var(--warn)" stroke-width="3"><animate attributeName="stroke-opacity" values="1;0.15;1" dur="1.6s" repeatCount="indefinite"/></rect>')
                rc.append(code)
            codes.append(rc)
        for r, rc in enumerate(codes):
            v = rc[0] + 512 * rc[1] + 262144 * rc[2]
            o.append(f'<text class="c" x="{ox + 3 * cs + 14}" y="{36 + r * cs + 27}">r{r} = {rc[0]} + 512·{rc[1]} + 262144·{rc[2]} = {fmt(v)}</text>')
        return "".join(o)
    out.append(panel(20, "On foot: what the page packs (Near: r0 to r4)", False))
    out.append(panel(500, "On Clover, without the pack or the gear (pulsing: changed)", True))
    out.append(f'<text class="n" x="20" y="{H - 34}">A tile: 0 to 11 what is there (1 to 7 ground, 10 a boulder, 11 a platform), +16 water, +32 climbable, +64·shape for a slope. On Clover the page clears +32 (no ladder, no tree, no tunnel</text>')
    out.append(f'<text class="n" x="20" y="{H - 16}">to climb without the pack) and makes the water ahead a wall (10) outside a leap, so World.step, unchanged, stops her at the water’s edge.</text></svg>')
    return "".join(out)
# ---- figure 5: where the state lives
def fig_state():
    W, H = 960, 360
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="All the world\'s state is in JavaScript; each Hazel function takes what it needs in a record and gives a record back">']
    out.append('<style>.t{font:600 12.5px system-ui,sans-serif;fill:var(--ink)}.n{font:11px system-ui,sans-serif;fill:var(--muted)}.h{font:700 14px system-ui,sans-serif;fill:var(--ink)}</style>')
    out.append(f'<rect x="20" y="20" width="400" height="320" rx="14" fill="{JS}" opacity="0.10" stroke="{JS}"/><text class="h" x="36" y="46">JavaScript: all the state</text>')
    items = ["S: the gnome, the hero, hearts, gems found", "rivers and dams, beavers, fallen trees, piles of logs", "trees (alive, growing), villagers, the weather, wind", "birds, frogs, insects, squirrels, bunnies, Clover", "the camera, the speed run, the music's place",
             "tiles: 9 arrays × 186,368 (896 × 208)", "  what is there, its water, behind, on it,", "  gems, stones, slopes, roots; the top of each column", "≈ 2.05 MB; a save gzips them, with S's parts"]
    for i, t in enumerate(items): out.append(f'<text class="n" x="40" y="{76 + i * 26}">{E(t)}</text>')
    fns = [("World.plan", "seed → the plan (500 places)", "once a world"), ("World.step", "Gnome, Near, Pad → Gnome", "60 a second"), ("World.beaver", "Beaver, trees, piles → Beaver", "50 a second"), ("World.water_row", "the river, its bank, the logs → a row", "a dam changed"), ("World.greet", "who, where, … → Talk", "stopping by"), ("World.roots", "a tree → [Line]", "first in view")]
    for i, (n, sig, when) in enumerate(fns):
        y = 30 + i * 52; out.append(f'<rect x="560" y="{y}" width="380" height="42" rx="10" fill="{HZ}" opacity="0.13" stroke="{HZ}"/><text class="t" x="574" y="{y + 18}">{E(n)}</text><text class="n" x="574" y="{y + 33}">{E(sig)}</text><text class="n" x="926" y="{y + 18}" text-anchor="end">{E(when)}</text>')
        d = f"M420,180C490,180 490,{y + 21} 560,{y + 21}"
        out.append(f'<path d="{d}" fill="none" stroke="var(--muted)" stroke-width="1.2" opacity="0.7"/>')
        dur = [6, 1.2, 2, 5, 4, 3][i]
        out.append(f'<circle r="4" fill="var(--warn)"><animateMotion dur="{dur}s" repeatCount="indefinite" path="{d}" keyPoints="0;1;0" keyTimes="0;0.5;1" calcMode="linear"/></circle>')
    out.append(f'<text class="n" x="560" y="{H - 8}">Hazel keeps nothing between calls: every record comes in, and goes back out.</text></svg>')
    return "".join(out)
# ---- figure 6: an oak's roots and mycelium, as World.roots and World.threads grew them, drawing themselves line by line
def fig_roots():
    R, Th = M["roots"], M["threads"]
    xs = [v for l in R + Th for v in (l[0], l[2])]; ys = [v for l in R + Th for v in (l[1], l[3])]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys); pad = 60; W = 960
    sc = (W - 2 * pad) / (x1 - x0); H = int((y1 - y0) * sc + 2 * pad + 40)
    tx = lambda x: pad + (x - x0) * sc; ty = lambda y: pad + 30 + (y - y0) * sc
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="The roots of an oak, 29 tiles tall, as Hazel grew them: {len(R)} lines of root and {len(Th)} of mycelium">']
    out.append('<style>.n{font:11px system-ui,sans-serif;fill:var(--muted)}.ln{opacity:0}.go .ln{animation:rg .5s ease-out both}@keyframes rg{from{opacity:0}to{opacity:1}}@media (prefers-reduced-motion: reduce){.ln{opacity:1}.go .ln{animation:none}}</style>')
    out.append(f'<line x1="0" y1="{ty(0):.1f}" x2="{W}" y2="{ty(0):.1f}" stroke="var(--good)" stroke-width="3" opacity="0.6"/><text class="n" x="10" y="{ty(0) - 8:.1f}">the ground’s surface; the oak’s foot at the middle</text>')
    near = lambda l: min((l[0] ** 2 + l[1] ** 2) ** 0.5, (l[2] ** 2 + l[3] ** 2) ** 0.5)   # (grown outward: each line in the order of its nearer end's distance from the foot)
    dmax = max(near(l) for l in R + Th) or 1
    for l in R:
        out.append(f'<line class="ln" style="animation-delay:{5 * near(l) / dmax:.2f}s" x1="{tx(l[0]):.1f}" y1="{ty(l[1]):.1f}" x2="{tx(l[2]):.1f}" y2="{ty(l[3]):.1f}" stroke="#a0683a" stroke-width="{max(0.8, l[4] * sc * 0.75):.2f}" stroke-linecap="round"/>')
    for l in Th:
        out.append(f'<line class="ln" style="animation-delay:{5 * near(l) / dmax:.2f}s" x1="{tx(l[0]):.1f}" y1="{ty(l[1]):.1f}" x2="{tx(l[2]):.1f}" y2="{ty(l[3]):.1f}" stroke="var(--muted)" stroke-width="0.9"/>')
    out.append(f'<text class="n" x="10" y="{H - 10}">{len(R)} lines of root, {len(Th)} of mycelium (grey), as Hazel returned them, grown outward from the foot; widths to scale. World.roots took {M["times"]["roots"]:.1f} ms for a tree this size.</text></svg>')
    return "".join(out), len(R), len(Th)
F1, F2, F3, F4, F5 = fig_split(), fig_step(), fig_events(), fig_near(), fig_state()
F6, nR, nT = fig_roots()
def fig(id_, svg, cap, extra=""): return f'<figure class="fig" id="{id_}"><div class="figscroll">{svg}</div><figcaption>{cap}{extra}</figcaption></figure>'
ms = lambda v: f"{v:.4f}" if v < 0.01 else f"{v:.3f}" if v < 0.1 else f"{v:.2f}" if v < 10 else f"{v:.0f}"
table_rows = [("World.plan", "the world from its seed: the land, the layers of rock, the water table, the rivers, the beavers' lodges and dams, the villages, the great trees, the trees, bushes, flowers and mushrooms, and the places under the ground (500 places)", "once a world, and at Restart and Load", ms(T["plan"])),
  ("World.step (with finish, slope_at, slide_vx, dig_ahead, tile)", "the gnome's step: running, jumping, falling, climbing, swimming, the slopes, digging", "every step: 60 a second", ms(T["step"])),
  ("World.beaver", "a beaver's next job: rest, go to a tree, gnaw it, cut a log, drag it to the dam, lay it", "every sixth step, for each of five beavers: 50 a second", ms(T["beaver"])),
  ("World.water_row", "how high a dam holds its river, by its logs", "when a dam's logs change", ms(T["water_row"])),
  ("World.greet", "a villager's words: 768 greetings, from 166 lines, none said by two villagers", "when the gnome stops by a villager", ms(T["greet"])),
  ("World.roots, World.threads", "a tree's roots and its mycelium, as lines", "the first time a tree is in view", ms(T["roots"])),
  ("World.ground, World.dig_steps", "each kind of ground: its pores, how water flows through it, its color, the steps to dig it with each digger", "once a world (90 digging steps kept)", "—"),
  ("World.village, World.furnish, World.limbs, World.styles", "a village's rooms and their things; a great tree's limbs and what is on each; the sixteen styles of tree house", "once a world", "—")]
tbl = '<div class="scroll"><table><thead><tr><th>Hazel function</th><th>what it decides</th><th>when the page calls it</th><th>ms a call</th></tr></thead><tbody>' + "".join(f"<tr><td><code>{E(a)}</code></td><td>{E(b)}</td><td>{E(c)}</td><td class=\"n\">{E(d)}</td></tr>" for a, b, c, d in table_rows) + "</tbody></table></div>"
DATA = {"build": M["build"], "sizes": {"hazel": {"total": HZ_TOT, "parts": {n: c for n, c, _ in hz_parts}}, "javascript": {"total": JS_TOT, "parts": dict(js_parts)}},
        "callMs": T, "stepMs": {"total": 2.4, "water": 2.2, "note": "measured during 0.0.102's development with temporary timing, after the water and perch fixes"},
        "tiles": {"columns": 896, "rows": 208, "arrays": 9, "bytes": 2051840}, "roots": {"tree": M["tree"], "lines": nR, "threads": nT}}
# (2026-11-25, ^ticket(861)) the first piece moved: the magic carpet's flight, Fly.step against the page's JavaScript of it
FLY = json.load(open(os.path.join(HERE, "data/fly-check.json")))
FLY_PAGE = {"usJS": 0.333, "usHazel": 2.567, "steps": 3000, "same": 3000, "where": "the page, ?test=1, the app's browser pane (Chromium) on the laptop, 7 batches of 3,000 recorded steps, the median"}
DATA["migration"] = {"plan": "the pieces in order, in #migrate", "fly": {"node": FLY, "page": FLY_PAGE, "stack": "the least --stack-size the program builds at in Node: 975 KB with Fly and without (data/stack-margin.txt)"}}
def fig_fly():
    rows = [("Node, the laptop", FLY["usJS"], FLY["usHazel"]), ("the page (Chromium)", FLY_PAGE["usJS"], FLY_PAGE["usHazel"])]
    W, L, bh = 760, 190, 20; mx = max(r[2] for r in rows); x = lambda v: L + v / mx * (W - L - 150)
    out = [f'<svg viewBox="0 0 {W} 150" role="img" aria-label="The carpet\'s step: the page\'s JavaScript against Hazel\'s Fly.step through the jit, microseconds a step">',
           '<style>.l{fill:var(--ink);font:600 13px system-ui,sans-serif}.s{fill:var(--muted);font:12px system-ui,sans-serif}</style>']
    for i, (name, js, hz) in enumerate(rows):
        y = 18 + i * 64
        out.append(f'<text class="l" x="{L - 10}" y="{y + 15}" text-anchor="end">{E(name)}</text>')
        out.append(f'<rect x="{L}" y="{y}" width="{x(js) - L:.1f}" height="{bh}" fill="{JS}"/><text class="s" x="{x(js) + 6:.1f}" y="{y + 15}">JavaScript {js:.2f} µs</text>')
        out.append(f'<rect x="{L}" y="{y + bh + 4}" width="{x(hz) - L:.1f}" height="{bh}" fill="{HZ}"/><text class="s" x="{x(hz) + 6:.1f}" y="{y + bh + 19}">Hazel, Fly.step {hz:.2f} µs</text>')
    out.append('</svg>'); return "".join(out)
F7 = fig_fly()
data_json = json.dumps(DATA, indent=1).replace("</", "<\\/")
BLURB = ("Which parts of Gnome world are Hazel and which JavaScript, asked of event handling, physics, the world's state and the "
  "drawing. Hazel decides what the world is and how the gnome moves: the plan from a seed, the gnome's step 60 times a second "
  "(0.016 ms a call, compiled by hazel-jit), the beavers' minds, the villagers' words, the roots. JavaScript holds all the state "
  "(nine arrays of 186,368 tiles), takes the input, runs everything else that moves (the water is 2.2 ms of a 2.4 ms step) and "
  "draws it all: 92% of the code, 70% of it drawing. Clover the rabbit is Hazel's gnome step with JavaScript around it. "
  "Since 0.0.107 the magic carpet's flight is Hazel's too, the cat tail's flight was written in Hazel from the start (0.0.116), and since 0.0.134 Clover's ride is Hazel's: pieces of a plan to move the logic over piece by piece, each checked against the JavaScript it replaces and timed (in Hazel each takes 3 to 6 times the JavaScript's time, under 1.3 µs a step).")
page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gnome World: Which Parts Are Hazel</title>
<meta name="description" content="{E(BLURB)}">
{style}
<style>
  ol.outline li {{ margin: 4px 0; }}
  .wip {{ color: var(--warn); font-weight: 600; }}
  figure.fig svg {{ width: 100%; height: auto; min-width: 640px; display: block; }}
</style>
</head>
<body><main>
<p class="series"><a href="../">Hazel reports</a> · <code class="ref"><b>^report(</b>64<b>)</b></code> · Gnome world · 2026-11-24, revised 2026-11-25 · <span class="wip">work in progress</span> · after <a href="../063/"><code class="ref"><b>^report(</b>63<b>)</b></code></a></p>
<h1>Gnome World: Which Parts Are Hazel</h1>
<p class="sub">Matthew asked, on 2026-11-24: “what parts of gnome world logic are expressed in JS vs Hazel? event handling? physics? global game world state? procedural rendering of trees, and other elements?” This report answers for <a href="https://matthewhammer.org/hazeljs-examples/world/">Gnome world</a> 0.0.103 (matthewhammer/hazeljs-examples <code>02b73ab</code>), its rules compiled in the page by hazel-jit from the hazeljs branch’s build (#2857).</p>

<h2 id="outline">Outline</h2>
<ol class="outline">
<li><a href="#split">The split</a>: Hazel decides what the world is and how the gnome moves; JavaScript keeps the state, takes the input, moves everything else and draws.</li>
<li><a href="#step">One step of the world</a>: Hazel is called once for the gnome and, every sixth step, once a beaver; its share of the step’s time is under 1%.</li>
<li><a href="#events">Event handling</a>: every input is JavaScript’s; Hazel sees one record a step and answers with one.</li>
<li><a href="#physics">Physics</a>: the gnome’s movement is Hazel; the water, the boulders, the animals and the rabbit’s rules around it are JavaScript.</li>
<li><a href="#state">The world’s state</a>: all of it in JavaScript; Hazel keeps nothing between calls.</li>
<li><a href="#drawing">Procedural drawing</a>: Hazel plans where things are and grows the roots; JavaScript draws everything.</li>
<li><a href="#why">Why the line falls there</a>: what Hazel in a page can and cannot do well today.</li>
<li><a href="#migrate">Moving the logic into Hazel, piece by piece</a>: the plan, eight pieces in order, each its own module calling nothing in World, each checked against the JavaScript it replaces and timed.</li>
<li><a href="#fly">Piece 1: the magic carpet’s flight</a>: done in 0.0.107; the same answer at every step, and 1.5 µs a step in Hazel against 0.27 in JavaScript, a ten-thousandth of a frame.</li>
<li><a href="#ride">Piece 2: Clover’s ride</a>: done in 0.0.134; two functions round the gnome’s step, the same ride at every step, 0.89 µs a step in Hazel against 0.28 in JavaScript; and <a href="#sofar">each piece so far</a>, timed the same way.</li>
<li><a href="#next">What next</a>, and <a href="#method">how this was put together</a>.</li>
</ol>
<p class="update"><b>Update, 2026-11-25.</b> Since this report first looked (at 0.0.103), three pieces of Gnome world’s logic have become Hazel’s: the magic carpet’s flight (0.0.107), the cat tail’s flight (written in Hazel from the start, 0.0.116), and Clover’s ride (0.0.134), in a migration Matthew asked for, “More and more of gnome world’s game logic into hazel, from JS”, and went on with: “porting the gnome world JS into Hazel, module by module ... let’s profile the difference as we go”. This report is revised as the work goes (<a href="#migrate">the plan</a>, <a href="#fly">piece 1</a>, <a href="#ride">piece 2</a>, <a href="#sofar">each piece so far</a>). The sections before them describe 0.0.103, as they did; since then the water has gone from 2.2 ms a step to about 0.6 (0.0.131, stepped only where it moves).</p>

<h2 id="split">The split</h2>
<p><b>Hazel decides what the world is and how the gnome moves; JavaScript does everything that touches the tiles, the screen or the clock.</b> By size, the Hazel is 40,213 characters of code in 32 functions (World.hz, comments left out), and the JavaScript 443,696 in 160 functions (app.js): 92% of the code, 70% of it drawing.</p>
{fig("fig-split", F1, "Not a build of the app: the code of 0.0.103 (02b73ab) by size, in characters. Hazel by what each function decides; JavaScript by what each function does, grouped by name (the grouping is in How this was put together). Hover a part for its size.")}
<p>The Hazel is a set of pure functions the page calls. Each takes small records and returns one:</p>
{tbl}
<p>The times are each function compiled by hazel-jit, called in the page 2,000 times (the plan 5, the roots 20) and averaged, once, on the laptop.</p>

<h2 id="step">One step of the world</h2>
<p><b>In a step (a sixtieth of a second), the page calls Hazel once, for the gnome, and every sixth step once for each of the five beavers; everything else in the step is JavaScript.</b> World.step takes 0.016 ms of a step of about 2.4 ms before drawing; the water alone takes 2.2 ms. Then the frame is drawn, all of it in JavaScript.</p>
{fig("fig-step", F2, "Gnome world 0.0.103, one step in the order <code>tick</code> runs it (the yellow bar sweeps across it), then the drawing; Hazel’s parts on the top lane. Below, the step to scale: the water, the rest of the JavaScript, and World.step, a line too thin to see. The step’s times were measured during 0.0.102’s development, after its fixes, with temporary timing; the Hazel call’s, at 0.0.103.")}

<h2 id="events">Event handling</h2>
<p><b>Every input is JavaScript’s; Hazel sees one record a step and answers with one.</b> Listeners for keys and for the pad’s buttons set <code>S.keys</code>. Each step the page packs the held keys into a <code>Pad</code> record (<code>dx</code>, <code>up</code>, <code>down</code>, <code>jump</code>, <code>dig</code>) and calls <code>World.step(gnome, near, pad)</code>. The step answers with the gnome as it is now, its <code>ev</code> saying what happened, and the page makes the effects: the dug tile taken out of the arrays (<code>digOut</code>), a sound, a heart lost.</p>
{fig("fig-events", F3, "Gnome world 0.0.103: a key press’s way into Hazel and back; JavaScript’s boxes teal, Hazel’s purple. The Gnome record has 16 fields; Near, the tiles round the gnome, 7; Pad 5.")}
<p>Building (<code>B</code>), riding (<code>R</code>), the map, saving, loading and restarting never pass through Hazel. Nor does the speed run’s planning: it finds its way over the tiles in JavaScript and then presses the keys, so the gnome it drives still moves by World.step.</p>

<h2 id="physics">Physics</h2>
<p><b>The gnome’s movement is Hazel; every other thing that moves is JavaScript.</b> World.step moves a box 0.66 tiles wide and 0.88 tall in thousandths of a tile: running at 92 a step, eased; falling 11 faster a step, to 267 at most; a jump of −208 cut short when up is let go; climbing at 70; floating, swimming and diving; walking on the diagonals of sloped banks and sliding down them; digging the tile pushed into. It sees the world only as the 3 by 5 tiles round the gnome, packed into five whole numbers.</p>
{fig("fig-near", F4, "Gnome world 0.0.103: the window World.step sees (Near), each row of three tiles one number, 512 apart. Right, the same window as the page gives it when Clover carries the gnome without the climbing pack or the diving gear; the pulsing tiles are the ones it changed: the ladder’s +32 gone, the water ahead a wall.")}
<p>JavaScript moves the rest, each step: the water seeping through the ground (every wet tile, down and then across), the boulders falling, the pebbles, the wind and its gusts, the leaves, the birds’ flights, the squirrels along the branches, the frogs’ jumps, the bunnies’ hops, the villagers walking and a felled tree falling. The beavers are both: World.beaver decides each one’s job, and JavaScript eases its body toward where Hazel put it.</p>
<p><b>Clover the rabbit is Hazel’s gnome step with JavaScript rules around it.</b> The page changes what the step sees (the window above), what it is asked (twice as fast: <code>dx</code> 2) and what comes back: a hop’s or a leap’s speed set after the jump, the digging’s progress tripled, a landing in the water undone. It went in JavaScript because World.hz is full: one more top-level definition overflowed the browser’s stack building the module on 2026-11-23.</p>

<h2 id="state">The world’s state</h2>
<p><b>All of it lives in JavaScript; Hazel keeps nothing between calls.</b> One object, <code>S</code>, holds the gnome, the rivers and dams, the trees, the beavers, the villagers, the animals, Clover, the weather, the camera and the speed run; nine arrays hold the 186,368 tiles (896 by 208): what is there, its water, what is behind and on it, gems, stones, slopes and roots, and the top of each column, about 2.05 MB.</p>
{fig("fig-state", F5, "Gnome world 0.0.103: the state in JavaScript, and the Hazel functions it is passed to, each with the records it takes and gives back, and how often.")}
<p>So saving is JavaScript’s: a save file is the seed and a snapshot of <code>S</code> and the tiles, and the GitHub check hashes its 36 parts before a save and after a load. The plan is never saved: Hazel makes it again from the seed.</p>

<h2 id="drawing">Procedural drawing</h2>
<p><b>Hazel plans where things are and grows the roots; JavaScript draws everything, 311,422 characters of canvas code.</b></p>
<ul>
<li><b>Trees.</b> World.plan puts each tree down with its kind and height. JavaScript grows its limbs (<code>growLimbs</code>: forking from seeded random numbers), puts leaf pads from eight shapes at their tips, and paints the tree once into a picture, in strips eight tiles tall for the biggest.</li>
<li><b>Great trees.</b> Hazel gives each limb (<code>World.limbs</code>: how high, which side, how long, the house on it); JavaScript grows the drawn crown to reach them.</li>
<li><b>Roots and mycelium.</b> Here Hazel draws too: <code>World.roots</code> and <code>World.threads</code> grow each tree’s roots and threads as lines, as Gnome dig grows them, and JavaScript strokes the lines.</li>
<li><b>Everything else</b>, the gnomes, birds, rabbits, houses, rivers and sky, is JavaScript.</li>
</ul>
{fig("fig-roots", F6, f"Gnome world 0.0.103: an oak 29 tiles tall, its roots ({nR} lines) and mycelium ({nT}) as World.roots and World.threads returned them, grown outward from its foot when the figure comes into view.", ' <button type="button" id="regrow">▶ grow again</button>')}
<script>(() => {{ const f = document.getElementById("fig-roots"), svg = f.querySelector("svg"), go = () => {{ svg.classList.remove("go"); void svg.getBoundingClientRect(); svg.classList.add("go"); }};
  new IntersectionObserver((es, o) => {{ if (es.some(e => e.isIntersecting)) {{ go(); o.disconnect(); }} }}, {{ threshold: 0.25 }}).observe(f); document.getElementById("regrow").addEventListener("click", go); }})();</script>

<h2 id="why">Why the line falls there</h2>
<p><b>Hazel takes what is a function of small records; JavaScript keeps what is big, changing or drawn.</b> What Hazel in a page cannot do well today decides most of the rest:</p>
<ul>
<li>No arrays: 186,368 tiles a step is a loop over typed arrays in JavaScript.</li>
<li>One module’s size: World.hz is at the browser’s limit for building one module (32 top-level definitions), and a module that calls another costs the build seconds.</li>
<li>The page’s edge: whole numbers past 2³¹ from JavaScript arrive cut to 32 bits; tuples do not cross, records do; every crossing converts values.</li>
<li>Speed: compiled by hazel-jit, a step is 0.016 ms; interpreted (hazeljs 0.0.4 from npm), the page’s own note says about 4 ms, too slow for 60 steps a second with drawing.</li>
</ul>

<h2 id="migrate">Moving the logic into Hazel, piece by piece</h2>
<p><b>The plan: eight pieces, in order, each the move of one part of the step from the page’s JavaScript into a Hazel module of its own, each done when its Hazel gives the same answers as the JavaScript it replaces and is timed against it.</b> Matthew asked on 2026-11-25: “More and more of gnome world’s game logic into hazel, from JS. Suggest a migration plan, where we work piece by piece. We have a report about this topic already. Let’s revise and amend that document as we work. Suggest the first piece to migrate, and without waiting for me, do it, and measure the performance difference pre/post migration.” The order puts first what fits Hazel as it is today (a function of small records, called each step), then what needs more of it.</p>
<table><thead><tr><th>Piece</th><th>What moves</th><th>In and out</th><th>Needs</th><th>State</th></tr></thead><tbody>
<tr><td>1</td><td>The magic carpet’s flight</td><td>the gnome, its window of tiles, the keys, the carpet; the gnome and the carpet</td><td>nothing new</td><td><b>done</b>, 0.0.107 (<a href="#fly">below</a>)</td></tr>
<tr><td>·</td><td>The cat tail’s flight (not in the plan: N’s, new)</td><td>the gnome, the keys, the tail; the gnome, the keys and the tail</td><td>nothing new</td><td><b>done</b>, written in Hazel from the start, 0.0.116</td></tr>
<tr><td>2</td><td>Clover’s ride: her hop and leap, her digging, the bank she goes back to</td><td>the keys and her state before World.step, and its answer after it; the keys to give it, then the gnome and her state</td><td>two functions round World.step</td><td><b>done</b>, 0.0.134 (<a href="#ride">below</a>)</td></tr>
<tr><td>3</td><td>The boulders: each one’s wobble, fall and landing, and a boulder on the gnome</td><td>a boulder, what is under it, whether it is wet, where the gnome is; the boulder and a hurt</td><td>a call a boulder a step (a few dozen)</td><td>next</td></tr>
<tr><td>4</td><td>Picking things up: the gem, heart or thing the gnome touches</td><td>the gnome and the places near it; which it takes</td><td>a short list a step</td><td></td></tr>
<tr><td>5</td><td>The wind: its wandering aim, its gusts</td><td>the wind and a few random numbers from the page; the wind</td><td>random numbers given in</td><td></td></tr>
<tr><td>6</td><td>The animals’ minds: the bunnies’ hops, the birds’ perches, the frogs’ jumps, as World.beaver decides the beavers’</td><td>an animal and what is near it; its next move</td><td>random numbers given in</td><td></td></tr>
<tr><td>7</td><td>The water seeping through the ground</td><td>a row of tiles at a time</td><td>arrays, or sequences (^ticket(846))</td><td>waits</td></tr>
<tr><td>8</td><td>The trees’ shapes, as lines, like the roots</td><td>a tree; its limbs as lines</td><td>nothing new, but large answers</td><td></td></tr>
</tbody></table>
<p>Every piece works under the same rules, learned on the first:</p>
<ul>
<li><b>A module of its own, calling nothing in World.</b> World.hz is at the browser’s limit for one module’s definitions, and a module that calls another costs the build seconds. The new module reads the same window of tiles World.step reads, and its own helpers (a remainder, the window’s tiles) live inside its one function.</li>
<li><b>No new names in the preamble.</b> The program as a whole sits at the browser’s stack for building it: two record types added to the preamble overflowed it (<code>Stack_overflow</code>, in the page) where the same types written out in the function’s signature did not. The least stack the program builds in, in Node, is 975 KB with the new module and without it.</li>
<li><b>The JavaScript stays beside it, made to agree.</b> The JavaScript is rewritten as a pure function of the same records, giving the same answer (the page’s own while the rules build, or if an edit breaks them; and a switch in the page to use it), and a check in Node, also run on GitHub, takes the JavaScript from the page’s own file and compares the two at every step of a long random run.</li>
<li><b>Timed before and after</b>, a step of each in Node and in the page, and the step’s share of a frame.</li>
</ul>

<h2 id="fly">Piece 1: the magic carpet’s flight</h2>
<p><b>Done in Gnome world 0.0.107: <code>Fly.step</code> in Hazel gives the same answer as the page’s JavaScript at every one of 20,000 steps, and takes 1.5 µs a step to the JavaScript’s 0.27, in Node; 0.009% of a frame.</b> N’s magic carpet came in 0.0.106, its flight written in JavaScript: it floats where it is until an arrow is held, its speed comes up in a few steps and stops as quickly, fast across, through open air and not through ground, rock, a boulder or into the water. It was the first piece because it is a function of small records called each step, it reads only the window World.step reads, and it was new, so the JavaScript it replaced was known exactly.</p>
{fig("fig-fly", F7, "The carpet’s step, before the move (the page’s JavaScript, flyJS) and after it (Hazel’s Fly.step through hazel-jit, its records converted in and out included), in microseconds. Node: node/fly-check.mjs, 20,000 steps of random flight in a made-up world, seven batches, the median, on the laptop, with the library of hazelgrove/hazel hazeljs at 2c4a61560f. The page: 3,000 recorded steps of flight in world 7, seven batches, the median, in the app’s browser pane (Chromium).")}
<ul>
<li><b>Rules/Fly.hz</b>, one function, <code>Fly.step(gnome, near, pad, carpet)</code>, in Hazel’s editor beside World on the page: the speed eased toward the keys’ (233 thousandths of a tile a step across, 150 up or down), each axis moved if the box (0.76 tiles across, from 0.92 above the feet to 0.28 below them) meets nothing there, the gnome and the carpet given back.</li>
<li><b>The same answer:</b> 20,000 of 20,000 steps in Node (the flight moved at 16,689 of them and was held back by something at 2,572), and 3,000 of 3,000 in the page in world 7. The check runs in the world save check on GitHub with each push.</li>
<li><b>The time:</b> 5.6 times the JavaScript’s in Node on the laptop, 5.8 times on GitHub’s runner (0.21 µs against 1.25, the world save check of 0.0.107), 7.7 times in the page, and either way thousandths of a millisecond in a frame of 16.7. Most of Hazel’s time is the crossing: four records converted in and two out, each step, where the JavaScript reads them where they are (^report(65), Conversion at the edges).</li>
</ul>

<h2 id="ride">Piece 2: Clover’s ride</h2>
<p><b>Done in Gnome world 0.0.134: <code>Ride.pre</code> and <code>Ride.post</code> in Hazel give the same answers as the page’s JavaScript at all 20,000 made-up steps in Node, and the same ride, step for step, in the page; her ride takes 0.89 µs a step in Hazel against 0.28 in JavaScript in Node (3.2 times), 3.97 against 0.83 in the page (4.8 times): a few thousandths of a percent of a frame.</b> Matthew, after the first piece and the cat tail: “I’m inspired by going further with porting the gnome world JS into Hazel, module by module. please keep going, and let’s profile the difference as we go.”</p>
<ul>
<li><b>Rules/Ride.hz</b>, two functions round the gnome’s own step, World.step, in Hazel’s editor beside World on the page. <code>Ride.pre(gnome, keys, clover)</code>: the keys as the page holds them and her state (a press of up kept for when she lands, whether she leapt with up still held, in the air from a hop or a leap, her last safe place) give the keys World.step gets (across twice as fast, but not digging; up held while she rises, so a hop or a leap is not cut short), whether this step leaps, and her state. <code>Ride.post(gnome, keys, clover, leap, wet)</code>: World.step’s gnome becomes hers: a jump taken is her leap (360 thousandths of a tile a step) or her hop (165); she digs three times as fast; in the water without the diving gear, not climbing, back to her last safe place; standing dry, a new safe place.</li>
<li><b>What stays in the page:</b> her window of tiles, built from the world (where water walls her in, what she may climb: dug earth, ladders, stairs, hatches), as the gnome’s own window is, and whether the water has reached her safe place (the page holds the water; it says so to <code>Ride.post</code> as one Bool). Her state is the record the page saved before, so a save is unchanged.</li>
<li><b>The same answers.</b> In Node (<code>node/fly-check.mjs</code>, also in the world save check on GitHub with each push): 20,000 of 20,000 made-up steps, the gnome on the ground or in the air, climbing or in the water, a jump just taken or not, a safe place or none, wet or dry (4,732 leaps, 2,698 hops, 934 times back to a safe place, 3,307 new safe places). In the page: the same scripted ride of 3,000 steps from the same fresh world, once with Hazel’s and once with the JavaScript (running, digging down, leaping, hopping), the gnome and her state the same at all 3,000 steps (2,806 places along the way, 42 leaps, 2 hops).</li>
<li><b>The time,</b> her ride’s own part a step, pre and post together, records in and out included: in Node on the laptop, 0.892 µs in Hazel, 0.283 in JavaScript (the median of three runs, each the median of seven batches of the 20,000; hazel-lib.js of build.hazel.org, hazel-jit as of 2026-11-25); in the page, in the app’s browser pane (Chromium 152), 3.97 µs and 0.83 (the median of three rides each way, each timed call by call, the timing’s own cost in both). The ride’s step, World.step included, is 1 to 1.7 ms either way, as the world is new: the water settling, not her ride.</li>
<li><b>The stack:</b> a module of its own again, its record written out in its signature; the program builds in the same least stack in Node, 968 KB, and in the page.</li>
</ul>

<h2 id="sofar">Each piece so far</h2>
<p><b>Each piece in Hazel takes 3 to 6 times its JavaScript’s time, and none more than 1.3 µs a step: together under a thousandth of a frame.</b> Timed the same way, in Node on the laptop, hazel-lib.js of build.hazel.org (hazel-jit as of 2026-11-25), each the median of three runs of <code>node/fly-check.mjs</code>, each run the median of seven batches of its 20,000 made-up steps:</p>
<table class="nums"><thead><tr><th class="l">Piece</th><th>In Gnome world</th><th>JavaScript, a step</th><th>Hazel, a step</th><th>Hazel’s time against the JavaScript’s</th></tr></thead><tbody>
<tr><td class="l">1, the magic carpet’s flight (<code>Fly.step</code>)</td><td>0.0.107</td><td>0.204 µs</td><td>1.264 µs</td><td>6.2×</td></tr>
<tr><td class="l">·, the cat tail’s flight (<code>Tail.step</code>)</td><td>0.0.116</td><td>0.123 µs</td><td>0.372 µs</td><td>3.0×</td></tr>
<tr><td class="l">2, Clover’s ride (<code>Ride.pre</code> and <code>Ride.post</code>)</td><td>0.0.134</td><td>0.283 µs</td><td>0.892 µs</td><td>3.2×</td></tr>
</tbody></table>
<p>Most of what Hazel’s time costs is the crossing (records converted in and out, ^report(65)’s <i>Conversion at the edges</i>): the carpet’s step takes four records in and gives two back, so it costs the most against its JavaScript; the tail and the ride, two or three small ones. Under ⚡ (Gnome world 0.0.133) the page runs each piece’s JavaScript instead.</p>

<h2 id="next">What next</h2>
<ol>
<li><b>Piece 3, the boulders in Hazel</b> (<a href="#migrate">the plan</a>). A Boulder module: a boulder’s wobble, fall and landing, and a boulder on the gnome, from the boulder and what is under it; a call a boulder a step, a few dozen.</li>
<li><b>The animals’ minds in Hazel, as the beavers’.</b> A bird’s or a bunny’s next move from a small record: where it is, how far the gnome is, the perches near.</li>
<li><b>The water in Hazel, once Hazel has arrays.</b> With ^ticket(846)’s sequences, a row at a time, timed against the JavaScript’s 2.2 ms.</li>
<li><b>Tree shapes as Hazel geometry, like the roots.</b> World.limbs already plans a great tree’s limbs; the drawn limbs could come back from Hazel as lines.</li>
<li><b>Time the crossing.</b> Gnome, Near and Pad go in and a Gnome comes out 60 times a second; with the converters by declared type (#2857), measure what that costs. The first piece’s numbers say most of a Hazel call is the crossing.</li>
</ol>

<h2 id="method">How this was put together</h2>
<p>Read World.hz, preamble.hz and app.js at matthewhammer/hazeljs-examples <code>02b73ab</code> (0.0.103). Sizes: each Hazel top-level definition’s code with its comments taken out; the JavaScript’s top-level functions grouped by name (drawing: <code>draw*</code>, <code>paint*</code>, sprites, the gnome, birds, rabbits, trees, the HUD; simulation: <code>tick</code> and the steps it calls, the ride; building the world: <code>build</code> and its helpers; the speed run: <code>bot*</code>; save and load; the rest). Times: in the page with <code>?test=1</code>, on the laptop, in the app’s browser pane (Chromium), the rules compiled by hazel-jit from build.hazel.org’s hazeljs build; each Hazel function called the stated number of times and averaged, once (one run is not a trend). The step’s 2.4 ms and the water’s 2.2 ms come from timing added for a while during 0.0.102’s development. The roots are World.roots’ and World.threads’ own output for the first oak of world 7. The migration’s first piece (2026-11-25): matthewhammer/hazeljs-examples 0.0.107 (<code>11ae1ac</code>), <code>node/fly-check.mjs</code> in Node 22 on the laptop with the library of hazelgrove/hazel <code>hazeljs</code> at 2c4a61560f (data/fly-check.json), the least stack it builds in found by halving (data/stack-margin.txt), and the page’s numbers in the browser pane with <code>?test=1</code>.</p>
<script type="application/json" id="report-data">{data_json}</script>
</main></body></html>
'''
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(page)
json.dump({"title": "Gnome World: Which Parts Are Hazel", "blurb": BLURB}, open(os.path.join(HERE, "data/card.json"), "w"), indent=1)
print("ok", len(page), "roots", nR, nT)
