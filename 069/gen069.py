#!/usr/bin/env python3
"""^report(69): Gnome World's Water and Way, in Hazel. ^ticket(904) and ^ticket(905), from ^report(68)'s What next, steps 4 and 5
(Matthew, 2026-11-27): "Make the water cheaper, so a step is less and the run faster at the same frame rate ... and let's also
have a hazel version of water, off by default, that we can turn on to profile and measure for reports. create a report with the
outcome." And: "Find the run's way by A* rather than by searching the whole world from the gnome outward ... let's do both. in
Hazel."

Writes 069/index.html, 069/data/meta.json and 069/img/thumb*.svg from:
  data/pane.json                 the browser pane on the laptop: the water's blocks and moves, the passes three ways, the
                                 threshold, the search's windows, Hazel's way split (written by hand from the pane's answers)
  data/frames-RUN.json           hazeljs-examples' 'world speed run, frame by frame' job, its log parsed (parse_frames.py):
                                 FIRST 46102840841 and FINAL 46103505251, five setups each on one runner
  data/save-check-RUN.log        the world save check's lines on the twins (46102840887, 46103505212)"""
import html, json, math, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(HERE, "data")
s35 = open(os.path.join(ROOT, "035", "index.html")).read(); CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
E = lambda s: html.escape(str(s), quote=True)
FIRST, FINAL = "46102840841", "46103505251"
def load(r): return json.load(open(os.path.join(DATA, f"frames-{r}.json")))["setups"]
def machine(r):
    p = os.path.join(DATA, f"machine-{r}.txt"); return open(p).read().strip() if os.path.exists(p) else "?"
PANE = json.load(open(os.path.join(DATA, "pane.json")))
F, F1 = load(FINAL), load(FIRST)
SAVE = {r: open(os.path.join(DATA, f"save-check-{r}.log")).read() for r in ("46102840887", "46103505212") if os.path.exists(os.path.join(DATA, f"save-check-{r}.log"))}
f1 = lambda x: f"{x:.1f}"; f2 = lambda x: f"{x:.2f}"
NAME = {"0.0.149": "0.0.149, as it was", "0.0.150": "0.0.150", "water-hazel": "0.0.150, 💧 the water in Hazel", "way-hazel": "0.0.150, 🧭 the way in Hazel", "wateps-1e-3": "0.0.150, the water's threshold at 1e-3"}
ORDER = ["0.0.149", "0.0.150", "way-hazel", "water-hazel", "wateps-1e-3"]
part = lambda S, k: S.get("stepParts", {}).get(k, 0.0)
def search_s(S): return S["stepsS"] * part(S, "its path search") / 100
SVGST = '<style>.l{fill:var(--ink);font:600 13px system-ui,sans-serif}.m{fill:var(--muted);font:12px system-ui,sans-serif}.w{fill:#fff;font:600 11px system-ui,sans-serif}</style>'

# ================= figure 1: how much water moves, block by block =================
def fig_moves():
    H = PANE["largest_move_in_block"]; bins = [("under a millionth", H["under_1e-6"]), ("to a hundred-thousandth", H["1e-6_to_1e-5"]), ("to a ten-thousandth", H["1e-5_to_1e-4"]),
                                              ("to a thousandth", H["1e-4_to_1e-3"]), ("to a hundredth", H["1e-3_to_1e-2"]), ("more", H["over_1e-2"])]
    W, L, bw, rh = 960, 230, 560, 30; top = max(v for _, v in bins); Hh = 40 + rh * len(bins) + 34
    o = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="The water blocks changing in a step, by the largest move in each: most move less than a thousandth of a tile">', SVGST]
    o.append(f'<text class="m" x="8" y="18">the largest move in a block in one step (a share of a tile’s water); blocks a step, of about {H["blocks_changing_a_step"]} changing</text>')
    y = 30
    for k, (n, v) in enumerate(bins):
        w = bw * v / top; c = "var(--accent2)" if k < 4 else "var(--warn)"
        o.append(f'<text class="m" x="8" y="{y + 18}">{E(n)}</text><rect x="{L}" y="{y + 4}" width="{max(w, 1):.1f}" height="{rh - 10}" fill="{c}"><title>{v} blocks</title></rect><text class="m" x="{L + w + 6:.1f}" y="{y + 18}">{v}</text>')
        y += rh
    o.append(f'<text class="m" x="8" y="{Hh - 10}">The browser pane on the laptop, 10 steps of the speed run from step 6,000; a move, the change in a tile’s water times its pores.</text></svg>')
    return "".join(o)

# ================= figure 2: a step's water and a search, three ways (log scale) =================
def fig_costs():
    P = PANE; r = P["passes"]["rounds"]; old = sum(x["old_ms"] for x in r) / len(r); new = sum(x["new_ms"] for x in r) / len(r); hz = sum(x["hazel_ms"] for x in r) / len(r)
    Wy = P["hazel_way"]; nh = sum(Wy["near"]["hazel_ms_all"]) / len(Wy["near"]["hazel_ms_all"]) / Wy["near"]["n"]; nj = sum(Wy["near"]["js_ms_all"]) / len(Wy["near"]["js_ms_all"]) / Wy["near"]["n"]; no = sum(Wy["near"]["old_ms_all"]) / len(Wy["near"]["old_ms_all"]) / Wy["near"]["n"]
    fh = Wy["far"]["hazel_ms_all"] / Wy["far"]["n"]; fj = Wy["far"]["js_ms_all"] / Wy["far"]["n"]; fo = Wy["far"]["old_ms_all"] / Wy["far"]["n"]
    rows = [("the water, a step", [("0.0.149’s passes", old, "#6b737d"), ("0.0.150’s passes", new, "var(--accent2)"), ("Water.hz", hz, "var(--accent)")]),
            ("the way to a nearby gem", [("0.0.149’s search", no, "#6b737d"), ("A*, wayJS", nj, "var(--accent2)"), ("A*, Path.hz", nh, "var(--accent)")]),
            ("the way to a thing far off", [("0.0.149’s search", fo, "#6b737d"), ("A*, wayJS", fj, "var(--accent2)"), ("A*, Path.hz", fh, "var(--accent)")])]
    W, L, bw = 960, 300, 520; lo, hi = math.log10(0.1), math.log10(200); X = lambda v: L + bw * (math.log10(max(v, 0.1)) - lo) / (hi - lo)
    Hh = 30 + sum(26 * (len(b) + 1) for _, b in rows) + 30
    o = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="A step of the water and a search for the way, by 0.0.149, by 0.0.150 and by Hazel: milliseconds, on a log scale">', SVGST]
    for t in [0.1, 1, 10, 100]: x = X(t); o.append(f'<line x1="{x:.1f}" y1="20" x2="{x:.1f}" y2="{Hh - 28}" stroke="var(--line)"/><text class="m" x="{x - 8:.1f}" y="16">{t:g} ms</text>')
    y = 26
    for title, bars in rows:
        o.append(f'<text class="l" x="8" y="{y + 16}">{E(title)}</text>'); y += 24
        for n, v, c in bars:
            o.append(f'<text class="m" x="24" y="{y + 15}">{E(n)}</text><rect x="{L}" y="{y + 3}" width="{X(v) - L:.1f}" height="16" fill="{c}"/><text class="m" x="{X(v) + 6:.1f}" y="{y + 15}">{v:.2f} ms</text>')
            y += 26
    o.append(f'<text class="m" x="8" y="{Hh - 10}">The browser pane on the laptop: the water over 60 steps, twice; the way to the 30 gems nearest the gnome and to the 8 things left, 2,000 steps into the run.</text></svg>')
    return "".join(o), {"water_old": old, "water_new": new, "water_hz": hz, "near_old": no, "near_js": nj, "near_hz": nh, "far_old": fo, "far_js": fj, "far_hz": fh}

# ================= figure 3: the speed run five ways, on one runner =================
def fig_runs():
    W, L, bw, rh = 960, 300, 380, 34; Hh = 44 + rh * len(ORDER) + 30
    real = {k: F[k].get("realS") for k in ORDER}; top = 130
    o = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="The speed run&#39;s real time, five ways, on one runner">', SVGST,
         f'<text class="m" x="{L}" y="18">the speed run’s real time, from 🏃 to its dig (seconds; a bar to the edge did not get there in the job’s two minutes)</text>']
    y = 30
    for k in ORDER:
        S = F[k]; v = real[k]; w = bw * min(v if v else top, top) / top; c = "var(--warn)" if not v else "var(--accent2)" if k != "wateps-1e-3" else "var(--good)"
        o.append(f'<text class="m" x="8" y="{y + 19}">{E(NAME[k])}</text><rect x="{L}" y="{y + 5}" width="{w:.1f}" height="{rh - 12}" fill="{c}"/>')
        o.append(f'<text class="m" x="{L + w + 6:.1f}" y="{y + 19}">{f"{v:.1f} s" if v else "not there in 120 s"} · {S["steps"]["n"]:.0f} steps a frame · median {1000 / S["gap"]["median"]:.0f} fps</text>')
        y += rh
    o.append(f'<text class="m" x="8" y="{Hh - 10}">hazeljs-examples’ frames job, run {FINAL}, one GitHub runner ({E(machine(FINAL))}), headless Chrome at 1280×800, each setup in turn.</text></svg>')
    return "".join(o)

# ================= figure 4: the threshold: the water's time and the flooded tiles =================
def fig_threshold():
    T = PANE["threshold"]; steps = T["steps"]; a, b = T["eps_1e-4"], T["eps_1e-3"]
    W, Hh = 960, 260; panels = [("the water, ms a step", "water_ms", 0.8), ("open tiles flooded (half full or more)", "flooded", 1700)]
    o = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="The water&#39;s waking threshold at a ten-thousandth and at a thousandth: its time a step, and the flooded tiles, over 10,000 steps of the speed run">', SVGST]
    for p, (title, key, top) in enumerate(panels):
        x0, y0, pw, ph = 60 + p * 470, 30, 380, 170
        o.append(f'<text class="l" x="{x0}" y="20">{E(title)}</text><line x1="{x0}" y1="{y0 + ph}" x2="{x0 + pw}" y2="{y0 + ph}" stroke="var(--line)"/>')
        for t in (0, top / 2, top): yy = y0 + ph - ph * t / top; o.append(f'<text class="m" x="{x0 - 6}" y="{yy + 4:.1f}" text-anchor="end">{t:g}</text><line x1="{x0}" y1="{yy:.1f}" x2="{x0 + pw}" y2="{yy:.1f}" stroke="var(--line)" stroke-dasharray="2 3"/>')
        for vals, c, lab in [(a[key], "var(--accent2)", "1e-4 (the game’s)"), (b[key], "var(--good)", "1e-3")]:
            pts = " ".join(f"{x0 + pw * (s - 0) / 10000:.1f},{y0 + ph - ph * v / top:.1f}" for s, v in zip(steps, vals))
            o.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2.5"/>')
            lx, ly = x0 + pw * steps[-1] / 10000, y0 + ph - ph * vals[-1] / top
            o.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="3.5" fill="{c}"/><text class="m" x="{lx - 4:.1f}" y="{ly - 8:.1f}" text-anchor="end">{lab}: {vals[-1]:g}</text>')
        for s in (0, 5000, 10000): o.append(f'<text class="m" x="{x0 + pw * s / 10000:.1f}" y="{y0 + ph + 16}" text-anchor="middle">{s:,}</text>')
    o.append(f'<text class="m" x="8" y="{Hh - 8}">The browser pane on the laptop, the speed run from a fresh world, steps (no drawing); each point the 2,000 steps before it. The game keeps 1e-4.</text></svg>')
    return "".join(o)

# ================= the tables =================
def t_runs():
    rows = []
    for k in ORDER:
        S = F[k]; real = f'{S["realS"]:.1f} s' if S.get("realS") else "not there in 120 s"
        rows.append(f'<tr><td class="l">{E(NAME[k])}</td><td>{real}</td><td>{S["steps"]["n"]:.0f}</td><td>{S["gap"]["median"]} ms</td><td>{100 * S["over"]["16.7"] / S["over"]["n"]:.0f}%</td><td>{S["gap"]["worst"]:.0f} ms</td>'
                    f'<td>{S["steps"]["slowestWorst"]:.0f} ms</td><td>{part(S, "water"):.0f}%</td><td>{part(S, "its path search"):.1f}%</td><td>{S["kinds"].get("the rules compiled from Hazel", 0):.1f}%</td></tr>')
    return ('<div class="wrap"><table class="nums"><thead><tr><th class="l">setup</th><th>the run’s real time</th><th>steps a frame</th><th>median frame</th><th>frames missing a refresh</th><th>worst frame</th>'
            '<th>slowest step</th><th>the steps: water</th><th>the steps: the way</th><th>the thread: Hazel</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")
def t_margins():
    W = PANE["windows"]; rows = []
    for m in ["16", "32", "64", "128", "world"]:
        a, b = W["near_by_margin"][m], W["far_by_margin"][m]
        rows.append(f'<tr><td class="l">{"the whole world" if m == "world" else m + " tiles"}</td><td>{a["found"]}</td><td>{a["search_ms"]} ms</td><td>{a["codes_ms"]} ms</td><td>{b["found"]}</td><td>{b["search_ms"]} ms</td><td>{b["codes_ms"]} ms</td></tr>')
    rows.append(f'<tr><td class="l">0.0.149’s search (the whole world, from the gnome outward)</td><td>30/30</td><td>{W["near_by_margin"]["old_ms"]} ms</td><td>—</td><td>8/8</td><td>{W["far_by_margin"]["old_ms"]} ms</td><td>—</td></tr>')
    return ('<table class="nums"><thead><tr><th class="l">window: the gnome’s tile and the target’s, and this much more each way</th><th>nearby gems reached</th><th>A*, a search</th><th>the window’s tiles worked out</th>'
            '<th>things far off reached</th><th>A*, a search</th><th>the window’s tiles</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>")
def t_builds():
    rows = [("1", "0.0.149", "Gnome world 0.0.149 (matthewhammer/hazeljs-examples <code>ea6b603</code>), ^report(68)’s fixes: the water’s passes and the run’s search as they had been"),
            ("2", "0.0.150", "build 1 with the water’s passes in locals, the run’s way by A* (wayJS), and Water.hz and Path.hz, off by default: perf/902-904 <code>1849ca5</code>, released as 0.0.150"),
            ("2, options", "💧, 🧭, threshold", "build 2 with <code>?water=hazel</code> (the water by Water.hz), <code>?way=hazel</code> (the way by Path.hz), or <code>?wateps=0.001</code> (the water’s waking threshold a thousandth, not the game’s)")]
    return ('<table class="nums"><thead><tr><th>build</th><th class="l">name</th><th class="l">what</th></tr></thead><tbody>' + "".join(f'<tr><td>{a}</td><td class="l">{b}</td><td class="l">{c}</td></tr>' for a, b, c in rows) + "</tbody></table>")

FIG = {"moves": fig_moves(), "runs": fig_runs(), "threshold": fig_threshold(), "t_runs": t_runs(), "t_margins": t_margins(), "t_builds": t_builds()}
FIG["costs"], C = fig_costs()
A, B, WH, WY, EP = F["0.0.149"], F["0.0.150"], F["water-hazel"], F["way-hazel"], F["wateps-1e-3"]
P = PANE; TH = P["threshold"]
N = {
    "a_real": f'{A["realS"]:.1f} s', "b_real": f'{B["realS"]:.1f} s', "ep_real": f'{EP["realS"]:.1f} s', "wy_real": f'{WY["realS"]:.1f} s' if WY.get("realS") else "over 120 s",
    "run_gain": f'{100 * (1 - B["realS"] / A["realS"]):.0f}%', "ep_x": f'{B["realS"] / EP["realS"]:.1f} times',
    "a_steps": f'{A["steps"]["n"]:.0f}', "b_steps": f'{B["steps"]["n"]:.0f}', "wh_steps": f'{WH["steps"]["n"]:.0f}', "ep_steps": f'{EP["steps"]["n"]:.0f}',
    "a_way": f'{part(A, "its path search"):.1f}%', "b_way": f'{part(B, "its path search"):.1f}%', "wy_way": f'{part(WY, "its path search"):.1f}%',
    "a_way_s": f'{search_s(A):.2f} s', "b_way_s": f'{search_s(B):.2f} s', "wy_way_s": f'{search_s(WY):.2f} s',
    "a_water": f'{part(A, "water"):.0f}%', "b_water": f'{part(B, "water"):.0f}%', "wh_water": f'{part(WH, "water"):.1f}%', "ep_water": f'{part(EP, "water"):.0f}%',
    "wh_hz": f'{WH["kinds"].get("the rules compiled from Hazel", 0):.0f}%', "wh_gc": f'{WH["kinds"].get("garbage collection", 0):.1f}%', "wy_hz": f'{WY["kinds"].get("the rules compiled from Hazel", 0):.1f}%',
    "wh_slow": f'{WH["steps"]["slowestWorst"]:.0f} ms', "wy_slow": f'{WY["steps"]["slowestWorst"]:.0f} ms', "b_slow": f'{B["steps"]["slowestWorst"]:.0f} ms', "wh_parts": WH.get("parts", "?"),
    "wy_worst": f'{WY["gap"]["worst"]:.0f} ms', "wh_worst": f'{WH["gap"]["worst"]:.0f} ms', "b_worst": f'{B["gap"]["worst"]:.0f} ms',
    "w_old": f2(C["water_old"]), "w_new": f2(C["water_new"]), "w_hz": f1(C["water_hz"]), "w_hz_x": f'{C["water_hz"] / C["water_new"]:.0f} times', "w_gain": f'{100 * (1 - C["water_new"] / C["water_old"]):.0f}%',
    "n_old": f2(C["near_old"]), "n_js": f2(C["near_js"]), "n_hz": f1(C["near_hz"]), "f_old": f1(C["far_old"]), "f_js": f1(C["far_js"]), "f_hz": f1(C["far_hz"]),
    "way_x": f'{(C["near_hz"] / C["near_js"] + C["far_hz"] / C["far_js"]) / 2:.0f} times',
    "awake": P["active"]["awake_avg"], "moving": P["active"]["moving_avg"], "moving_pct": f'{100 * P["active"]["moving_avg"] / P["active"]["awake_avg"]:.0f}%',
    "tiny": P["largest_move_in_block"]["under_1e-6"] + P["largest_move_in_block"]["1e-6_to_1e-5"] + P["largest_move_in_block"]["1e-5_to_1e-4"] + P["largest_move_in_block"]["1e-4_to_1e-3"],
    "changing": P["largest_move_in_block"]["blocks_changing_a_step"], "big": P["largest_move_in_block"]["1e-3_to_1e-2"],
    "th_w4": TH["eps_1e-4"]["water_ms"][-1], "th_w3": TH["eps_1e-3"]["water_ms"][-1], "th_a4": TH["eps_1e-4"]["awake"][-1], "th_a3": TH["eps_1e-3"]["awake"][-1],
    "th_f4": f'{TH["eps_1e-4"]["flooded"][-1]:,}', "th_f3": f'{TH["eps_1e-3"]["flooded"][-1]:,}', "th_fpct": f'{100 * (1 - TH["eps_1e-3"]["flooded"][-1] / TH["eps_1e-4"]["flooded"][-1]):.0f}%',
    "th_x": f'{TH["eps_1e-4"]["water_ms"][-1] / TH["eps_1e-3"]["water_ms"][-1]:.1f} times', "th_tpct": f'{100 * (1 - TH["eps_1e-3"]["total"][-1] / TH["eps_1e-4"]["total"][-1]):.1f}%',
    "calls": f'{P["hazel_water_calls"]["calls_a_step"]:,}', "down_us": P["hazel_water_calls"]["down_us"], "across_us": P["hazel_water_calls"]["across_us"], "dry_us": P["hazel_water_calls"]["down_dry_us"],
    "sp10_build": P["hazel_way"]["split"]["10000"]["handover_build_ms"], "sp10_search": P["hazel_way"]["split"]["10000"]["search_ms"], "sp10_js": P["hazel_way"]["split"]["10000"]["js_ms"],
    "sp40_build": P["hazel_way"]["split"]["40000"]["handover_build_ms"], "first_way": f'{part(F1["0.0.150"], "its path search"):.1f}%', "first_way149": f'{part(F1["0.0.149"], "its path search"):.1f}%',
    "wh_things": WH.get("things", "?"),
    "run_f": FINAL, "run_1": FIRST, "m_f": E(machine(FINAL)), "updated": updated,
}
FIG.update(N)
body = open(os.path.join(HERE, "body.html"), encoding="utf-8").read()
for k, v in FIG.items(): body = body.replace("{{" + k + "}}", str(v))
left = re.findall(r"\{\{(\w+)\}\}", body); assert not left, left
TITLE = "Gnome World’s Water and Way, in Hazel"
DESC = (f"The water and the speed run's way, made cheaper in Gnome world 0.0.150 and written in Hazel too, each Hazel version off by default and the same as the page's JavaScript to the bit. "
        f"The speed run takes {N['b_real']} where it took {N['a_real']}. The water in Hazel takes {N['w_hz_x']} the time of the page's, and the way in Hazel {N['way_x']}: the same answers, but Hazel has no arrays, so a block of tiles crosses as a list and a search keeps its best costs in a tree. "
        f"Most of the water's work is seepage of under a thousandth of a tile a step; letting that sleep makes the run {N['ep_x']} as fast, and floods {N['th_fpct']} fewer tiles: a decision for Matthew.")
EXTRA = """
  figure.chart svg { width: 100%; height: auto; display: block; }
  table.nums td, table.nums th { text-align: right; font-variant-numeric: tabular-nums; } table.nums td.l, table.nums th.l { text-align: left; }
  .wrap { overflow-x: auto; }
"""
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{E(DESC)}\">\n<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(head + body)

def thumb(mode):
    base = ".h{fill:#1f2328;font:700 15px system-ui,sans-serif}.m{fill:#5b6470;font:10px system-ui,sans-serif}.k{fill:#1f2328;font:700 11px system-ui,sans-serif}.j{fill:#0e7490}.z{fill:#6d28d9}"
    dark = ".h{fill:#e8e6e3}.m{fill:#a2a9b3}.k{fill:#e8e6e3}.j{fill:#67e8f9}.z{fill:#c4b5fd}"
    style = base + ("\n" + dark if mode == "dark" else "\n@media (prefers-color-scheme: dark) {" + dark + "}" if mode == "auto" else "")
    X = lambda v: 16 + 240 * (math.log10(max(v, 0.1)) + 1) / 3.3
    rows = [("water, a step", C["water_new"], C["water_hz"]), ("the way, a search", C["near_js"], C["near_hz"])]
    out = []
    for i, (n, js, hz) in enumerate(rows):
        y = 66 + i * 52
        out.append(f'<text class="m" x="16" y="{y - 4}">{n}: JavaScript and Hazel (log)</text><rect class="j" x="16" y="{y}" width="{X(js) - 16:.1f}" height="12"/><text class="k" x="{X(js) + 4:.1f}" y="{y + 10}">{js:.2f} ms</text>'
                   f'<rect class="z" x="16" y="{y + 16}" width="{X(hz) - 16:.1f}" height="12"/><text class="k" x="{X(hz) + 4:.1f}" y="{y + 26}">{hz:.1f} ms</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" width="320" height="200">\n<style>{style}\n</style>\n'
            '<text class="h" x="16" y="26">Water and way, in Hazel</text>\n<text class="m" x="16" y="42">the same answers to the bit; Hazel has no arrays</text>\n'
            + "".join(out) + f'\n<text class="m" x="16" y="186">the speed run: {N["a_real"]} → {N["b_real"]} (0.0.150)</text>\n</svg>\n')
os.makedirs(os.path.join(HERE, "img"), exist_ok=True)
for name, mode in [("thumb-light.svg", "light"), ("thumb-dark.svg", "dark"), ("thumb.svg", "auto")]: open(os.path.join(HERE, "img", name), "w").write(thumb(mode))
meta = {"title": TITLE, "blurb": DESC,
        "builds": {"1 (0.0.149)": "matthewhammer/hazeljs-examples ea6b603", "2 (0.0.150)": "perf/902-904 1849ca5, released as 0.0.150; options ?water=hazel, ?way=hazel, ?wateps=0.001"},
        "runs": {"pane": PANE["where"], "frames": f"hazeljs-examples 'world speed run, frame by frame' runs {FIRST} and {FINAL} (one GitHub runner each: {machine(FIRST)}; {machine(FINAL)}), headless Chrome at 1280×800, each setup in turn up to two minutes",
                 "save check": "hazeljs-examples 'world save check' runs 46102840887 and 46103505212: the twins from the tour's world, the water 20 steps, the way to 20 gems"},
        "measures": {"water ms": "a step of the water's two passes, the mean over the steps run", "search ms": "one search for the way, the mean over the targets",
                     "real time": "wall-clock seconds from pressing 🏃 to the run's dig", "steps parts": "⏱'s parts of every step, as shares of the steps' time"},
        "files": ["data/pane.json", "data/frames-*.log", "data/frames-*.json", "data/save-check-*.log", "parse_frames.py", "gen069.py"]}
json.dump(meta, open(os.path.join(DATA, "meta.json"), "w"), indent=1, ensure_ascii=False)
print("wrote 069/index.html;", updated)
for k in sorted(N): print(f"  {k}: {N[k]}")
