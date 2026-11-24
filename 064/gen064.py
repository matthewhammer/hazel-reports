#!/usr/bin/env python3
"""^report(64): Gnome World, which parts are Hazel. Builds 064/index.html from 063's look, the measured data
(data/measured.json: Hazel calls timed in the page, the roots World.roots grew for an oak) and the sizes of the code."""
import json, re, html, os
HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(HERE, "data/measured.json")))
head063 = open(os.path.join(HERE, "../063/index.html"), encoding="utf-8").read()
style = head063[head063.index("<style>"):head063.index("</style>") + len("</style>")]
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
data_json = json.dumps(DATA, indent=1).replace("</", "<\\/")
BLURB = ("Which parts of Gnome world are Hazel and which JavaScript, asked of event handling, physics, the world's state and the "
  "drawing. Hazel decides what the world is and how the gnome moves: the plan from a seed, the gnome's step 60 times a second "
  "(0.016 ms a call, compiled by hazel-jit), the beavers' minds, the villagers' words, the roots. JavaScript holds all the state "
  "(nine arrays of 186,368 tiles), takes the input, runs everything else that moves (the water is 2.2 ms of a 2.4 ms step) and "
  "draws it all: 92% of the code, 70% of it drawing. Clover the rabbit is Hazel's gnome step with JavaScript around it.")
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
<p class="series"><a href="../">Hazel reports</a> · <code class="ref"><b>^report(</b>64<b>)</b></code> · Gnome world · 2026-11-24 · <span class="wip">work in progress</span> · after <a href="../063/"><code class="ref"><b>^report(</b>63<b>)</b></code></a></p>
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
<li><a href="#next">What next</a>, and <a href="#method">how this was put together</a>.</li>
</ol>

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

<h2 id="next">What next</h2>
<ol>
<li><b>Clover’s ride in Hazel.</b> A Ride module of its own, calling nothing in World: the hop, the leap, and what she may climb or swim, from the same window of tiles.</li>
<li><b>The animals’ minds in Hazel, as the beavers’.</b> A bird’s or a bunny’s next move from a small record: where it is, how far the gnome is, the perches near.</li>
<li><b>The water in Hazel, once Hazel has arrays.</b> With ^ticket(846)’s sequences, a row at a time, timed against the JavaScript’s 2.2 ms.</li>
<li><b>Tree shapes as Hazel geometry, like the roots.</b> World.limbs already plans a great tree’s limbs; the drawn limbs could come back from Hazel as lines.</li>
<li><b>Time the crossing.</b> Gnome, Near and Pad go in and a Gnome comes out 60 times a second; with the converters by declared type (#2857), measure what that costs.</li>
</ol>

<h2 id="method">How this was put together</h2>
<p>Read World.hz, preamble.hz and app.js at matthewhammer/hazeljs-examples <code>02b73ab</code> (0.0.103). Sizes: each Hazel top-level definition’s code with its comments taken out; the JavaScript’s top-level functions grouped by name (drawing: <code>draw*</code>, <code>paint*</code>, sprites, the gnome, birds, rabbits, trees, the HUD; simulation: <code>tick</code> and the steps it calls, the ride; building the world: <code>build</code> and its helpers; the speed run: <code>bot*</code>; save and load; the rest). Times: in the page with <code>?test=1</code>, on the laptop, in the app’s browser pane (Chromium), the rules compiled by hazel-jit from build.hazel.org’s hazeljs build; each Hazel function called the stated number of times and averaged, once (one run is not a trend). The step’s 2.4 ms and the water’s 2.2 ms come from timing added for a while during 0.0.102’s development. The roots are World.roots’ and World.threads’ own output for the first oak of world 7.</p>
<script type="application/json" id="report-data">{data_json}</script>
</main></body></html>
'''
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(page)
json.dump({"title": "Gnome World: Which Parts Are Hazel", "blurb": BLURB}, open(os.path.join(HERE, "data/card.json"), "w"), indent=1)
print("ok", len(page), "roots", nR, nT)
