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
  "Since 0.0.107 the magic carpet's flight is Hazel's too, the cat tail's flight was written in Hazel from the start (0.0.116), since 0.0.134 Clover's ride, since 0.0.135 the boulders and since 0.0.136 picking things up, since 0.0.137 the wind, since 0.0.141 to 0.0.143 the minds of the wild bunnies, the frogs and the birds are Hazel's: pieces of a plan to move the logic over piece by piece, each checked against the JavaScript it replaces and timed (in Hazel each takes 3 to 8 times the JavaScript's time in Node, under 2.5 µs a step).")
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
<li><a href="#boulders">Piece 3: the boulders</a>: done in 0.0.135; a boulder’s wobble, fall, landing and hit, the same boulders and hearts at every step; 0.26 µs a boulder’s step in Hazel against 0.03 to 0.09 in JavaScript.</li>
<li><a href="#pickup">Piece 4: picking things up</a>: done in 0.0.136; which things and hearts the gnome takes and what each gives it, the same at every step; 2.22 µs a step in Hazel against 0.50, over half of it the world’s lists crossing.</li>
<li><a href="#wind">Piece 5: the wind</a>: done in 0.0.137; its aim and gusts, five random numbers a step given in by the page, the same wind at every step; 0.37 µs a step in Hazel against 0.095.</li>
<li><a href="#bunnies">Piece 6, first part: the wild bunnies</a>: done in 0.0.141; a bunny’s hop, its running from the gnome, its nibbling and wandering, six random numbers given in; the same at all 600,000 made-up steps and in the game’s own loop; 0.46 µs a bunny’s step in Hazel against 0.23.</li>
<li><a href="#frogs">Piece 6, second part: the frogs</a>: done in 0.0.142; a frog’s jumps, swimming, fleeing, croaking and catching bugs, its pads where the waves have them given in; the same at all 600,000 made-up steps and in the game’s own loop; 1.62 µs a frog’s step in Hazel against 0.67.</li>
<li><a href="#birds">Piece 6, third part: the birds</a>: done in 0.0.143; the songbirds on the ground, perched and flying between, and the ducks and swans, the hawks left to the page; the same at all 600,000 made-up steps of each and in the game’s own loop; 1.71 µs a songbird’s step in Hazel against 0.58, 0.39 a duck’s against 0.13. And a finding: with every animal drawing a fixed count of random numbers, the page’s randomness no longer follows its clock while the view stays put.</li>
<li><a href="#next">What next</a>, and <a href="#method">how this was put together</a>.</li>
</ol>
<p class="update"><b>Update, 2026-11-25.</b> Since this report first looked (at 0.0.103), seven pieces of Gnome world’s logic have become Hazel’s, the seventh but for the hawks: the magic carpet’s flight (0.0.107), the cat tail’s flight (written in Hazel from the start, 0.0.116), Clover’s ride (0.0.134), the boulders (0.0.135), picking things up (0.0.136), the wind (0.0.137), the wild bunnies’ minds (0.0.141), the frogs’ (0.0.142) and the birds’ (0.0.143), in a migration Matthew asked for, “More and more of gnome world’s game logic into hazel, from JS”, and went on with: “porting the gnome world JS into Hazel, module by module ... let’s profile the difference as we go”. This report is revised as the work goes (<a href="#migrate">the plan</a>, <a href="#fly">piece 1</a>, <a href="#ride">piece 2</a>, <a href="#boulders">piece 3</a>, <a href="#pickup">piece 4</a>, <a href="#wind">piece 5</a>, <a href="#bunnies">piece 6’s first part</a>, <a href="#frogs">its second</a>, <a href="#birds">its third</a>, <a href="#sofar">each piece so far</a>). The sections before them describe 0.0.103, as they did; since then the water has gone from 2.2 ms a step to about 0.6 (0.0.131, stepped only where it moves).</p>

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
<tr><td>3</td><td>The boulders: each one’s wobble, fall and landing, and a boulder on the gnome</td><td>a boulder, what is under it, whether it is wet, where the gnome is; the boulder and a hurt</td><td>a call a boulder a step, for the boulders that move</td><td><b>done</b>, 0.0.135 (<a href="#boulders">below</a>)</td></tr>
<tr><td>4</td><td>Picking things up: the gem, heart or thing the gnome touches</td><td>the gnome and the places near it; which it takes</td><td>a short list a step</td><td><b>done</b>, 0.0.136 (<a href="#pickup">below</a>)</td></tr>
<tr><td>5</td><td>The wind: its wandering aim, its gusts</td><td>the wind and a few random numbers from the page; the wind</td><td>random numbers given in</td><td><b>done</b>, 0.0.137 (<a href="#wind">below</a>)</td></tr>
<tr><td>6</td><td>The animals’ minds: the bunnies’ hops, the birds’ perches, the frogs’ jumps, as World.beaver decides the beavers’</td><td>an animal and what is near it; its next move</td><td>random numbers given in</td><td>the bunnies <a href="#bunnies">done</a>, 0.0.141; the frogs <a href="#frogs">done</a>, 0.0.142; the birds <a href="#birds">done</a>, 0.0.143; the hawks stay the page’s</td></tr>
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

<h2 id="boulders">Piece 3: the boulders</h2>
<p><b>Done in Gnome world 0.0.135: <code>Boulder.step</code> in Hazel gives the same answer as the page’s JavaScript for all 20,000 made-up boulders in Node, and the same boulders and hearts, step for step, in the page; a boulder’s step takes 0.26 µs in Hazel against 0.03 to 0.09 in JavaScript in Node (3 to 8 times, the JavaScript’s own time moving from run to run), 0.316 against 0.028 in the page (11.4 times). The boulder’s JavaScript is the shortest of the pieces, so against it Hazel’s cost shows the most; and it costs the least in a frame, since only a boulder that wobbles or falls is stepped.</b></p>
<ul>
<li><b>Rules/Boulder.hz</b>, one function, <code>Boulder.step(boulder, around)</code>, in Hazel’s editor on the page. The boulder: its tile, how far it has fallen into the tile below (a part of a tile), its wobble’s steps left, whether it falls. With open air under it, a still boulder begins to wobble, three quarters of a second (45 steps); then it falls, 0.11 of a tile a step in the air, 0.04 in the water, and lands where the tile under the next is not open; falling over the gnome (its feet within 0.8 of a tile across, its body under the boulder’s), it hits it. The answer: the boulder, and whether it began to wobble, landed or hit, for the page to sound and to hurt.</li>
<li><b>What stays in the page:</b> what is round each boulder (the tile under it open, no ground, no plank, no other boulder there; the tile under that; the water; the gnome’s feet), and the boulders themselves, a list the page keeps (the world’s tiles mark them too). The page skips a boulder that is still with ground under it, so a step calls Hazel only for the boulders that move.</li>
<li><b>The same answers.</b> In Node (<code>node/fly-check.mjs</code>, also in the world save check on GitHub with each push): 20,000 of 20,000 made-up boulders, still or wobbling or falling, wet or dry, ground under them or not, the gnome near or far (2,435 wobbles begun, 154 falls begun, 348 landings, 2,237 hits). In the page: a fresh world, the ground dug out three tiles deep under twelve of its boulders and the gnome under the first, 600 steps once with Hazel’s and once with the JavaScript and once more with Hazel’s: the boulders and the hearts the same at all 600 steps each time (121 states of the boulders along the way, one hit).</li>
<li><b>A bug the check found.</b> The first page check had Hazel’s run lose a heart and the JavaScript’s not, the boulders the same. It was the page, not either rule: a hit leaves the gnome unhurtable for a second and a half of the clock, and a world built within that time kept it, so the second run in a row dodged the hit, whichever went second. A new world now starts with that time past (0.0.135).</li>
<li><b>The time,</b> a boulder’s step, records in and out included: in Node on the laptop 0.261 µs in Hazel, 0.084 in JavaScript (the median of three runs, each the median of seven batches of the 20,000; hazel-lib.js of build.hazel.org, hazel-jit as of 2026-11-25). The JavaScript’s step is so short, a few comparisons and sums, that in Node it came out at about 0.035 µs in two of five runs and about 0.09 in the other three, as V8 compiled it; Hazel’s at 0.24 to 0.27 every time; in the page, in the app’s browser pane (Chromium 152), the 900 calls of the check’s run replayed 200 times each way, nine batches, the median: 0.316 µs and 0.028. Hazel’s 0.26 µs is the least of the pieces, as its records are the smallest; most of it is likely the crossing (two small records in, a record holding a record out), which the JavaScript does not pay. In the page’s run about one boulder and a half moved a step (1,906 calls in 1,200 steps): half a microsecond of a 16.7 ms frame.</li>
<li><b>The stack:</b> a module of its own, its records written out in its signature; the program builds in the same least stack, 968 KB in Node, and in the page.</li>
</ul>

<h2 id="pickup">Piece 4: picking things up</h2>
<p><b>Done in Gnome world 0.0.136: <code>Pickup.step</code> in Hazel gives the same answers as the page’s JavaScript at all 20,000 made-up steps close by and all 20,000 as in a world, in Node, and the same pickups, step for step, in the page; a step takes 2.22 µs in Hazel against 0.50 in JavaScript in Node (4.5 times), 1.42 against 0.15 in the page (9.5 times). It is the first piece that takes lists, and the lists are over half its cost: in the page about 0.54 µs a call with both lists empty, and about 18 ns more for each thing or heart in them.</b></p>
<ul>
<li><b>Rules/Pickup.hz</b>, one function, <code>Pickup.step(me, things, hearts)</code>, in Hazel’s editor on the page. The gnome (its feet in tiles, its hearts, what it has: the diving gear, its tool, its kit of shoes, flippers and climbing claws as one number, the climbing pack, its carrots), the world’s things (where each lies, what it is, whether it is taken) and its hearts. A thing is taken when the gnome’s middle, half a tile above its feet, comes within 0.8 of a tile of it across and 1 up or down, in the page’s order; it gives the climbing pack, the diving gear, a carrot, the shoes, flippers or claws, or a tool (the better kept). A heart, the same, only while the gnome has fewer than five, and no more than make five. The answer: the gnome with what it took, and which things and which hearts it took, by their places in the page’s lists.</li>
<li><b>What stays in the page:</b> the lists themselves (the page draws them, the speed run steers by them, a save keeps them), marking each taken, the sounds, the notes (the game paused while one is read), what only the page holds (the carpet and the cat tail as rides, the gem finder’s compass), a heart’s coming back once its place is out of view, and a gem lying loose in an open tile, a read of one tile.</li>
<li><b>The same answers.</b> In Node (<code>node/fly-check.mjs</code>, also in the world save check on GitHub with each push): 20,000 of 20,000 made-up steps close by, one to six things and up to four hearts within a few tiles of the gnome, the gnome with any hearts and anything (14,787 things and 6,706 hearts taken, at 13,098 steps); and 20,000 of 20,000 as in a world, the page’s twelve things and twenty-six hearts over 900 tiles (something taken at 10). In the page: a fresh world, two hearts left, the gnome put by each of its twelve things in turn and by six of its hearts, three steps each, then 120 steps more; once with Hazel’s, once with the JavaScript, once more with Hazel’s: the gnome, what it has, its hearts and every thing’s and heart’s state the same at all 174 steps (all twelve things taken, each giving what it gives; three hearts, to five, and no more).</li>
<li><b>The time,</b> a step of picking up with the world’s lists: in Node on the laptop 2.22 µs in Hazel, 0.50 in JavaScript (the median of three runs, each the median of seven batches of the 20,000; hazel-lib.js of build.hazel.org, hazel-jit as of 2026-11-25); in the page, in the app’s browser pane (Chromium 152), the world’s lists with the gnome at 900 places, 50 times each, nine batches, the median: 1.418 µs and 0.149. Taken apart, in the page: both lists empty, 0.54 µs in Hazel and 0.04 in JavaScript; the twelve things only, 0.78; the twenty-six hearts only, 1.10; both, 1.23. So each thing or heart costs Hazel about 18 ns a step, converted and walked, against JavaScript’s 3. Under ⏱ the part is 1.7 to 3.8 µs a step with Hazel, 0.33 with the JavaScript (the loose gem’s tile and the timing’s own cost in both): about a hundredth of a percent of a 16.7 ms frame.</li>
<li><b>What it says for the next pieces:</b> a list crosses whole, each step, whether or not anything in it is near. The page could hand over only the things within a few tiles (the plan’s “the places near it”), which would make the cost the call’s alone; at 0.7 µs a step to save, it was not worth a second rule for nearness in the page. The animals’ minds (piece 6) will take lists too, and there it may be.</li>
<li><b>The stack:</b> a module of its own, its records written out in its signature and in its helpers’; the program builds in the same least stack, 968 KB in Node, and in the page.</li>
</ul>

<h2 id="wind">Piece 5: the wind</h2>
<p><b>Done in Gnome world 0.0.137: <code>Wind.step</code> in Hazel gives the same answer as the page’s JavaScript at all 60,000 steps of a wind blowing in Node, and the same wind, step for step, in the page; a step takes 0.37 µs in Hazel against 0.095 in JavaScript in Node (3.9 times), 0.321 against 0.081 in the page (4.0 times). It is the first piece whose randomness comes in from the page, and the change that asked for is one to the game, not to its speed.</b></p>
<ul>
<li><b>Rules/Wind.hz</b>, one function, <code>Wind.step(wind, frame, r)</code>, in Hazel’s editor on the page. The wind: how strong it blows now, the strength it is turning toward (its aim), the step at which it picks a new aim, and a gust on top. A new aim every 6 to 16 seconds, now and then a strong one; the wind comes round to its aim slowly, 0.4% of the way a step; a gust comes now and then, more often the stronger the wind, its way the aim’s, and dies away, 2.5% a step. The answer: the wind, and how strong it blows this step (the wind and its gust, −1.4 to 1.4), which the leaves, the trees, the grass, the waves, the smoke, the rain, the clouds and the birds read.</li>
<li><b>Random numbers given in.</b> The page’s JavaScript drew from the world’s random stream as it went: three numbers when a new aim came, one each step for whether a gust came, one more for its size. A Hazel function has no stream to draw from, so the page draws five each step, whatever the wind uses, and gives them in (<code>r</code>: whether a new aim is strong, the aim, how long until the next, whether a gust comes, its size). The same draws go to Hazel’s and to the JavaScript, so either way a world blows the same; but the stream now moves five a step where it moved one or two, so for the same seed the weather, and every random thing after it in the step, goes differently from 0.0.136’s. The world’s plan, from Hazel and the seed, does not change.</li>
<li><b>What stays in the page:</b> the random stream, the leaves a strong wind blows off the trees (they read the wind; the trees are the page’s), and everything that sways or drifts with it.</li>
<li><b>The same answers.</b> In Node (<code>node/fly-check.mjs</code>, also in the world save check on GitHub with each push): a wind blowing from the page’s first wind for 60,000 steps, five made-up random numbers a step, each step’s answer compared and the JavaScript’s carried on: 60,000 of 60,000 (97 new aims, 300 gusts, at its strongest 1.40). In the page: a fresh world, 3,000 steps, once with Hazel’s, once with the JavaScript, once more with Hazel’s, the wind, its strength, the leaves and the gnome the same at all 3,000 steps each time (4 new aims, 18 gusts).</li>
<li><b>A finding along the way: the page’s randomness follows its clock.</b> The page check first parted at about step 1,100. It was not the wind: two runs both with Hazel’s wind parted too, at step 852, and two both with the JavaScript at the same step. Something in the page’s step draws from the random stream by the real clock (how many draws, or whether one is made, depends on <code>performance.now()</code>), so two runs from one world agree only while their timings do. One place the step reads the clock is the frogs on the lily pads, whose height is the waves’ at the clock’s time (the page’s <code>wildStep</code>); whether that is what moves the stream is still to be found. With the page’s clock tied to its steps, as the speed-run check already ties it (^report(65)), the runs agree at every step; the comparison above is so. The pieces before this one did not show it: they compared what does not read the stream.</li>
<li><b>The time,</b> a step of the wind: in Node on the laptop 0.37 µs in Hazel, 0.095 in JavaScript (the median of three runs, each the median of seven batches of the 60,000; hazel-lib.js of build.hazel.org, hazel-jit as of 2026-11-25); in the page, in the app’s browser pane (Chromium 152), 3,000 steps of a wind 30 times each way, nine batches, the median: 0.321 µs and 0.081. One call a step, small records: a few thousandths of a percent of a 16.7 ms frame.</li>
<li><b>The stack:</b> a module of its own, its records written out in its signature; the program builds in the same least stack, 968 KB in Node, and in the page.</li>
</ul>

<h2 id="bunnies">Piece 6, first part: the wild bunnies</h2>
<p><b>Done in Gnome world 0.0.141: <code>Bunny.step</code> in Hazel gives the same answer as the page’s JavaScript at all 600,000 steps of 20,000 made-up bunnies in Node, at all 87,000 steps of world 7’s own 29 bunnies on its own land in the page, and the same bunnies, step for step, in the game’s own loop; a bunny’s step takes 0.46 µs in Hazel against 0.23 in JavaScript in Node (2.0 times), and the same on GitHub. The animals’ minds are three kinds of animal; the bunnies came first, as the one whose mind reads only the land beside it, so the frogs and the birds, which read the waves and the trees, are the rest of the piece.</b></p>
<ul>
<li><b>Rules/Bunny.hz</b>, one function, <code>Bunny.step(bunny, gnome, land, r)</code>, in Hazel’s editor on the page. Each step, a wild bunny in view goes on along its hop, and at its end waits a moment (a step, if it was running away). Otherwise: the gnome within three and a half tiles, not riding Clover, and it runs, a long hop away; else it nibbles a while, or waits, or every so often hops a little way about, back toward its home when it has wandered more than five tiles from it. A hop never goes into a river, past the world’s edges, or up or down more than 1.3 tiles; one that would, it turns round and waits. Its ears prick up now and then. The answer: the bunny, its hop as a record (on or off; from, to, how far along, in how many steps, how high), which the page draws.</li>
<li><b>What the page gives it.</b> The bunny and the gnome as small records; the land’s height at seven columns round the bunny (three each side: no hop reaches further), the world’s width, and the rivers within four tiles (from where to where); and six random numbers from the page’s stream (the wait after a hop, the ears, whether to nibble, how long, which way to wander, how far to hop). As with the wind, the page now draws its six for each bunny it steps, where it drew one to four as it needed them, so for the same seed the bunnies, and every random thing after them, go differently from 0.0.140’s; the world as built does not change, and both levels still match <code>levels.json</code>’s record of them.</li>
<li><b>Two small changes so the two agree exactly.</b> The distance to the gnome is compared by its square (against 12.25) rather than through <code>Math.hypot</code>, which Hazel has no twin of; and a whole number is cut toward zero, as Hazel’s <code>int_of_float</code> cuts it (the page’s <code>Math.floor</code> differed only below zero, where no hop is taken).</li>
<li><b>What stays in the page:</b> which bunnies are stepped (those in view), drawing them, and Clover, whose own hops to dry land search the tiles round her.</li>
<li><b>The same answers.</b> In Node (<code>node/fly-check.mjs</code>, also in the world save check on GitHub with each push): 20,000 made-up bunnies on land of made-up heights with two rivers, each stepped 30 times with its answer carried on, the gnome near or far, riding or not: 600,000 of 600,000 (10,282 hops begun, 6,467 of them running away, 1,041 back toward home; 3,715 nibbles; at least 2,138 turned back at a river, an edge or a bank). In the page: world 7’s 29 bunnies, on its own land and rivers, 3,000 steps each, 87,000 of 87,000; and the game’s own loop from one fresh world, the page’s clock tied to its steps (<a href="#wind">as for the wind</a>), once with Hazel’s bunnies and once with the JavaScript’s, the gnome set down by a meadow: the same at every step, 1,200 steps by one meadow (9 hops, 2 running away) and 900 by another (15 hops, 4 running away, 6 nibbles). The test page’s fresh world keeps the step count, the wind, the leaves and the camera of the world before it, and only the animals in view are stepped, so each run compared sets those back first (the camera was found with the frogs: before it was set back, a first run after a load parted from the second at its first step).</li>
<li><b>The time,</b> a bunny’s step: in Node on the laptop 0.46 µs in Hazel, 0.23 in JavaScript (the median of three runs, each the median of seven batches of a sixth of the 600,000 steps; hazel-lib.js of hazelgrove/hazel <code>hazeljs</code> at <code>2c4a61560f</code>, as for the pieces before it): Hazel’s from 0.445 to 0.475 µs, the JavaScript’s from 0.231 to 0.246. On GitHub, with build.hazel.org’s library, 0.458 and 0.231. Three earlier runs that timed all 600,000 steps, on a busier laptop, moved far more, Hazel’s from 0.45 to 0.71 µs. In the page, in the app’s browser pane (hidden, so as a guide only), 0.365 µs and 0.172. Four records in (the land’s list of seven, the rivers’ list, usually empty), one out; only bunnies in view are stepped, a handful at a time: under 5 µs of a 16.7 ms frame.</li>
<li><b>The stack:</b> a module of its own, its records written out in its signature; the program builds at 965 KB of stack in Node, inside the margin the pieces before it left (975 KB).</li>
</ul>

<h2 id="frogs">Piece 6, second part: the frogs</h2>
<p><b>Done in Gnome world 0.0.142: <code>Frog.step</code> in Hazel gives the same answer as the page’s JavaScript at all 600,000 steps of 20,000 made-up frogs in Node, at all 18,000 steps of the world’s own six frogs on their own rivers in the page, and the same frogs, step for step, in the game’s own loop by two rivers; a frog’s step takes 1.62 µs in Hazel against 0.67 in JavaScript in Node (2.4 times). It is the dearest of the animals, as it takes the most in: its river’s lily pads and the bugs near it, two lists, each step.</b></p>
<ul>
<li><b>Rules/Frog.hz</b>, one function, <code>Frog.step(frog, gnome, river, r)</code>, in Hazel’s editor on the page. A frog sits on a lily pad, riding it on the waves, or on the bank; jumps along an arc; or swims. In a jump it goes on along the arc, and landing waits a moment. Swimming, it makes for the pad farthest from the gnome (or its bank, a river without pads), and once there, the gnome more than four tiles off and its wait run out, jumps up onto it. Sitting, the gnome within two and a half tiles (three and a half if the gnome is in the water), it jumps away into the river and swims; now and then it croaks; a bug just in front of it and its tongue ready, it eats the bug; its wait run out on a pad, it jumps to another pad near it. The answer: the frog, and whether it croaks, which bug it eats, and whether it lands in the water near the gnome; the page plays the croak and the plop, and marks the bug eaten.</li>
<li><b>What the page gives it,</b> besides the frog and the gnome: its river (the water’s level, where it starts and how wide it is), the land under the frog, its bank and the water there, each of the river’s pads where the waves have it now, the bugs within three tiles, and whether its tongue is ready (a second since it last ate); and five random numbers (the wait after a jump, how far it jumps away, whether it croaks, the wait on a pad, which pad it jumps to). The waves follow the page’s clock, so the page gives the pads’ heights in, read once a step (the JavaScript read the clock again at each pad). The frog’s pad is its place in the river’s list; its mode a number (sitting 0, jumping 1, swimming 2).</li>
<li><b>Two traps on the way.</b> π written out in full, <code>3.141592653589793</code>, sent Hazel’s parser to its slow path (the literal printed back as <code>3.141593</code> did not match the source), and the program took 33.5 s to build instead of 5.6; Hazel’s own <code>pi</code> does it. And the Node check ran out of the laptop’s memory (1.2 GB) keeping all 600,000 steps’ inputs of the bunny’s check and the frog’s for timing; it keeps a sixth of each now.</li>
<li><b>The same answers.</b> In Node: 20,000 made-up frogs, each on a made-up river (a level, ends, none to six pads riding made-up waves, or a bank), bugs about, the gnome near or far, in the water or not, each stepped 30 times with its answer carried on: 600,000 of 600,000 (8,608 jumps begun, 6,892 of them away into the water, 1,411 pad to pad; 154,679 steps swimming; 22,435 bugs eaten). In the page: the world’s six frogs on their own rivers, 3,000 steps each, 18,000 of 18,000; and the game’s own loop from one fresh world, the clock tied to its steps, the gnome set down by a frog and later moved off: by one river 600 steps the same (two jumps, 148 steps swimming, three croaks, a bug eaten), by another 700 (two jumps, 1,324 frog-steps swimming, a bug eaten).</li>
<li><b>The time,</b> a frog’s step: in Node on the laptop 1.62 µs in Hazel (1.59 to 1.64 over three runs), 0.67 in JavaScript (0.64 to 0.67), the same library and timing as the bunny’s. In the page (the pane hidden, so as a guide only), 0.79 µs and 0.20. Only frogs in view are stepped, a few at most: under 10 µs of a 16.7 ms frame.</li>
<li><b>The stack:</b> a module of its own again; the program builds at 965 KB of stack in Node with both new modules, as before them.</li>
</ul>

<h2 id="birds">Piece 6, third part: the birds</h2>
<p><b>Done in Gnome world 0.0.143: <code>Bird.step</code> (a songbird’s mind) and <code>Bird.swim</code> (a duck’s or a swan’s) in Hazel give the same answers as the page’s JavaScript at all 600,000 steps of 20,000 made-up birds each in Node, at all of the game’s own 5,081 calls in the page, and the same birds, step for step, in the game’s own loop; a songbird’s step takes 1.71 µs in Hazel against 0.58 in JavaScript in Node (2.9 times), a duck’s or a swan’s 0.39 against 0.13 (2.9 times). With them the animals’ minds are Hazel’s but for the two hawks, and the page’s random stream no longer follows its clock while the view stays put.</b></p>
<ul>
<li><b>Rules/Bird.hz</b>, two functions in one module. <code>Bird.step(bird, gnome, sees, r)</code>, the sparrows, the robins and the jays: flying, a bird goes on along its flight, easing in and out on an arc, and lands as the flight says; perched, it sits where the wind has its perch now, and scared (the gnome within three tiles, a jay’s 2.2) or its wait run out, it flies home to the ground, if it has a home and the gnome is not by it, or to another perch near it, now and then singing; its perch gone with a felled tree, it is on the ground; on the ground, scared, it flies up to one of the three perches nearest it, else hops about its home, pecks or waits. <code>Bird.swim</code>: the gnome near, a duck or a swan makes for the far side of its river, now and then quacking or honking; else, its wait run out, it picks a new place to swim to, a duck now and then dabbling. The answers: the bird, and whether it calls; the page plays the call.</li>
<li><b>Perches given only when they can matter.</b> A bird’s perch sways with its tree by the page’s clock, so the page gives the perch where it is now. The perches it could fly to, within 16 tiles, matter only on a step it may choose one (scared, or perched with its wait run out); working them all out for every bird every step, as the plan first had it, would cost far more than the bird (some 600 perches, each a sway). So the page gives them on those steps and none on the others, and the JavaScript twin gets the same, so the two still agree everywhere. The JavaScript before did the same, choosing only on those steps.</li>
<li><b>The hawks stay the page’s.</b> Their soaring circles over the gnome by an angle, and resting they pick the nearest great tree; Hazel has the angle (<code>atan2</code>, compiled to <code>Math.atan2</code>), so they could follow, but two hawks are not worth the stack (below).</li>
<li><b>Three slips on the way</b>, each caught before the page: two closing brackets missing (the build said only that <code>Bird.swim</code> was not found, the module having swallowed it); a module’s top-level definitions end in <code>;</code>, which <code>Bird.step</code> lacked; and <code>then</code> is a keyword, so a flight’s field for where it lands is <code>next</code>.</li>
<li><b>The same answers.</b> In Node: 20,000 made-up songbirds, on the ground, perched or flying, near perches that sway and sometimes go, the gnome near or far, 30 steps each: 600,000 of 600,000 (8,329 flights begun, 7,170 to a perch, 1,159 home; 1,384 perches lost; 1,673 hops; 1,542 pecks; 4,862 calls); 20,000 made-up ducks and swans on made-up rivers, 30 steps each: 600,000 of 600,000 (11,654 new places to swim to, 2,938 dabs). In the page: the game’s own loop from one fresh world, the clock tied to its steps, Hazel’s birds and the JavaScript’s the same at every step by a river with ducks (600 steps), by a flock of sparrows (600) and by a perched jay (900, with 12 flights from perch to perch); and the game’s own calls in 600 steps there, 3,566 songbird steps and 1,515 duck and swan steps, the same both ways.</li>
<li><b>The time:</b> in Node on the laptop, a songbird’s step 1.71 µs in Hazel (1.57 to 1.85 over three runs), 0.58 in JavaScript (0.54 to 0.63); a duck’s or a swan’s 0.39 (0.36 to 0.46) against 0.13 (0.09 to 0.13); the same library and timing as the bunny’s and the frog’s, with the laptop busier for these runs. In the page (the pane hidden, a guide only), on the game’s own calls, 0.85 µs and 0.23, and 0.25 and 0.03. A score of birds in view: some 30 µs of a 16.7 ms frame.</li>
<li><b>The stack:</b> the program builds at 970 KB of stack in Node, and no longer at 965 as it did before the birds: about 5 KB narrower, still within the 966 to 978 KB the pieces have sat at, and it builds in the browser pane. Two top-level definitions cost more stack than one, which is the case against moving the hawks for their own sake.</li>
<li><b>A finding: the page’s randomness and its clock.</b> Piece 5 found two runs of the page from one world parting unless its clock was tied to its steps. Now every animal draws a fixed count of random numbers each step it is stepped, so how many draws a step makes no longer depends on where the waves or the wind have a pad or a perch. Two runs with the clock running free, the gnome set down by a river: the random stream the same at every one of 400 steps, and of 608 by another river; set down 40 tiles on, of 500. It still parts once the view moves: the camera moves with each drawing, only the animals in view are stepped, and where a bird lands depends on where the wind has swayed its perch, by the clock, so which animals are in view, and so draw, can still follow the clock (the run by the second river parted eight steps after the gnome was moved 40 tiles). The frogs’ own moves follow the clock too (their pads ride the waves), but no longer anything else’s.</li>
</ul>

<h2 id="sofar">Each piece so far</h2>
<p><b>Each piece in Hazel takes about 3 to 6 times its JavaScript’s time (the boulders’ 3 to 8, as their JavaScript’s own time moves from run to run), and none more than 2.3 µs a step: together a few hundredths of a percent of a frame.</b> Timed the same way, in Node on the laptop, hazel-lib.js of build.hazel.org (hazel-jit as of 2026-11-25), each the median of three runs of <code>node/fly-check.mjs</code>, each run the median of seven batches of its 20,000 made-up steps:</p>
<table class="nums"><thead><tr><th class="l">Piece</th><th>In Gnome world</th><th>JavaScript, a step</th><th>Hazel, a step</th><th>Hazel’s time against the JavaScript’s</th></tr></thead><tbody>
<tr><td class="l">1, the magic carpet’s flight (<code>Fly.step</code>)</td><td>0.0.107</td><td>0.204 µs</td><td>1.264 µs</td><td>6.2×</td></tr>
<tr><td class="l">·, the cat tail’s flight (<code>Tail.step</code>)</td><td>0.0.116</td><td>0.123 µs</td><td>0.372 µs</td><td>3.0×</td></tr>
<tr><td class="l">2, Clover’s ride (<code>Ride.pre</code> and <code>Ride.post</code>)</td><td>0.0.134</td><td>0.283 µs</td><td>0.892 µs</td><td>3.2×</td></tr>
<tr><td class="l">3, the boulders (<code>Boulder.step</code>)</td><td>0.0.135</td><td>0.084 µs (0.03 to 0.10)</td><td>0.261 µs</td><td>3.1× (3 to 8)</td></tr>
<tr><td class="l">4, picking things up (<code>Pickup.step</code>), the world’s twelve things and twenty-six hearts</td><td>0.0.136</td><td>0.495 µs</td><td>2.224 µs</td><td>4.5×</td></tr>
<tr><td class="l">5, the wind (<code>Wind.step</code>)</td><td>0.0.137</td><td>0.095 µs</td><td>0.374 µs</td><td>3.9×</td></tr>
<tr><td class="l">6, first part, a wild bunny (<code>Bunny.step</code>)</td><td>0.0.141</td><td>0.231 µs</td><td>0.460 µs</td><td>2.0×</td></tr>
<tr><td class="l">6, second part, a frog (<code>Frog.step</code>)</td><td>0.0.142</td><td>0.667 µs</td><td>1.617 µs</td><td>2.4×</td></tr>
<tr><td class="l">6, third part, a songbird (<code>Bird.step</code>)</td><td>0.0.143</td><td>0.582 µs</td><td>1.712 µs</td><td>2.9×</td></tr>
<tr><td class="l">6, third part, a duck or a swan (<code>Bird.swim</code>)</td><td>0.0.143</td><td>0.131 µs</td><td>0.386 µs</td><td>2.9×</td></tr>
</tbody></table>
<p>Most of what Hazel’s time costs is the crossing (records converted in and out, ^report(65)’s <i>Conversion at the edges</i>): the carpet’s step takes four records in and gives two back, so it costs the most against its JavaScript; the tail and the ride, two or three small ones. The boulder’s step crosses the least, two small records in and one out, and is the cheapest in Hazel, 0.26 µs; its JavaScript is cheaper still, and the range in its row is its JavaScript’s, from run to run. Picking things up is the first piece to take lists, the world’s things and hearts, and they cross whole each step: about 18 ns an element in the page, so the thirty-eight make it the dearest piece in Node (in the page the carpet’s four records still cost more, 2.57 µs to 1.42). The wild bunny’s step takes two short lists (the land’s seven heights, the rivers near, usually none) and a few small records; the frog’s two more (its river’s pads, the bugs near), and costs the most of the animals; against their JavaScript both cost the least of the pieces, 2 to 2.4 times, likely as their JavaScript does more per call than the wind’s or a boulder’s, so the crossing is less of the whole (not measured apart). The animals’ rows are the median of three runs each timing a sixth of their 600,000 steps; the birds’ were run with the laptop busier. Under ⚡ (Gnome world 0.0.133) the page runs each piece’s JavaScript instead.</p>

<h2 id="next">What next</h2>
<ol>
<li><b>Each animal its own random numbers.</b> Piece 6 left the page’s randomness following its clock only through which animals are in view (<a href="#birds">the finding</a>). Drawing each animal’s numbers from the seed, its own name and the step, rather than from the one shared stream, would make nothing depend on which are stepped: two runs from one world would agree with the clock free, in the page as in the checks, and the hawks would follow suit.</li>
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
