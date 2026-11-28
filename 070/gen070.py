#!/usr/bin/env python3
"""^report(70): Gnome World's Planning, Rivers and Folk, in Hazel. ^ticket(907) (Matthew, 2026-11-28): "let's focus on these
next, opt-in for Hazel (default off): * the villagers walking, the squirrels, the hawks and insects; * the rivers held at their
level, the pumps and the rain; * the speed run's planning (the order of things, its targets, the dig's chunks)."

Writes 070/index.html, 070/data/meta.json and 070/img/thumb*.svg from:
  data/pane.json                 the browser pane on the laptop: planSame, riversSame, folkSame and Folk.bug alone (by hand)
  data/frames-RUN.json           hazeljs-examples' 'world speed run, frame by frame' job, its log parsed (parse_frames.py)
  data/save-check-RUN.log        the world save check's lines on the twins
  data/sizes-0.0.15x.json        sizes.py (^report(68)'s) at 0.0.152 and 0.0.156"""
import html, json, math, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(HERE, "data")
s35 = open(os.path.join(ROOT, "035", "index.html")).read(); CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
E = lambda s: html.escape(str(s), quote=True)
FINAL = "46167931157"; SAVES = ["46167673024", "46167928740"]
P = json.load(open(os.path.join(DATA, "pane.json")))
F = json.load(open(os.path.join(DATA, f"frames-{FINAL}.json")))["setups"]
def machine(r):
    p = os.path.join(DATA, f"machine-{r}.txt")
    if not os.path.exists(p): return "?"
    L = [x.strip() for x in open(p).read().splitlines() if x.strip()]
    cpu = next((x.split(":", 1)[1].strip() for x in L if x.startswith("model name")), "?")
    return f"{L[0]} CPUs, {cpu}; Node {next((x for x in L if x.startswith('v')), '?')}; {next((x for x in L if x.startswith('Google Chrome')), '?')}"
Z0, Z1 = (json.load(open(os.path.join(DATA, f"sizes-{v}.json"))) for v in ("0.0.152", "0.0.156"))
SVGST = '<style>.l{fill:var(--ink);font:600 13px system-ui,sans-serif}.m{fill:var(--muted);font:12px system-ui,sans-serif}.w{fill:#fff;font:600 11px system-ui,sans-serif}</style>'
f2 = lambda x: f"{x:.2f}"; f3 = lambda x: f"{x:.3f}"
mean = lambda xs: sum(xs) / len(xs)

# ================= the pieces' costs =================
F6 = P["folk_0156"]; F5 = P["folk_0155"]["rounds"]
folk_js = sum(F6["js"].values()); folk_hz = sum(F6["hazel"].values())
rv_js = mean([mean([r["dry"]["js"], r["rainy"]["js"]]) for r in P["rivers"]]); rv_hz = mean([mean([r["dry"]["hazel"], r["rainy"]["hazel"]]) for r in P["rivers"]])
PL = P["plan"]
PIECES = [("the order of the 12 things (once)", PL["order"]["js_ms"], PL["order"]["hazel_ms"]),
          ("the great trees’ 64 parts (once)", PL["trees"]["js_ms"], PL["trees"]["hazel_ms"]),
          ("336 gems, nearest first", PL["nearest"]["js_ms"], PL["nearest"]["hazel_ms"]),
          ("the rivers, pumps, rain, a step", rv_js, rv_hz),
          ("80 villagers, a step", F6["js"]["walk"], F6["hazel"]["walk"]),
          ("14 squirrels, a step", F6["js"]["squirrels"], F6["hazel"]["squirrels"]),
          ("70 insects, a step", F6["js"]["bugs"], F6["hazel"]["bugs"]),
          ("2 hawks, a step", F6["js"]["hawks"], F6["hazel"]["hawks"])]
def fig_costs():
    W, L, bw = 960, 290, 540; lo, hi = math.log10(0.001), math.log10(200); X = lambda v: L + bw * (math.log10(max(v, 0.001)) - lo) / (hi - lo)
    rh = 46; Hh = 40 + rh * len(PIECES) + 26
    o = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="Each piece in JavaScript and in Hazel, milliseconds on a log scale: Hazel takes 4 to 40 times as long">', SVGST]
    for t in [0.001, 0.01, 0.1, 1, 10, 100]:
        x = X(t); o.append(f'<line x1="{x:.1f}" y1="24" x2="{x:.1f}" y2="{Hh - 22}" stroke="var(--line)"/><text class="m" x="{x - 10:.1f}" y="18">{t:g} ms</text>')
    y = 32
    for n, js, hz in PIECES:
        o.append(f'<text class="m" x="8" y="{y + 20}">{E(n)}</text>')
        o.append(f'<rect x="{L}" y="{y + 4}" width="{X(js) - L:.1f}" height="14" fill="var(--accent2)"><title>JavaScript {js:g} ms</title></rect><text class="m" x="{X(js) + 5:.1f}" y="{y + 16}">{js:g}</text>')
        o.append(f'<rect x="{L}" y="{y + 21}" width="{X(hz) - L:.1f}" height="14" fill="var(--accent)"><title>Hazel {hz:g} ms</title></rect><text class="m" x="{X(hz) + 5:.1f}" y="{y + 33}">{hz:.3g} · {hz / js:.0f}×</text>')
        y += rh
    o.append(f'<rect x="{L}" y="{Hh - 16}" width="12" height="10" fill="var(--accent2)"/><text class="m" x="{L + 16}" y="{Hh - 7}">JavaScript</text><rect x="{L + 110}" y="{Hh - 16}" width="12" height="10" fill="var(--accent)"/><text class="m" x="{L + 126}" y="{Hh - 7}">Hazel (and how many times the JavaScript)</text></svg>')
    return "".join(o)

# ================= the speed run, five ways =================
ORDER = ["js", "plan-hazel", "rivers-hazel", "folk-hazel", "all-hazel"]
NAME = {"js": "the page’s JavaScript", "plan-hazel": "🗺️ the planning in Hazel", "rivers-hazel": "🌧️ the rivers in Hazel", "folk-hazel": "🐿️ the creatures in Hazel",
        "all-hazel": "all five Hazel options (🗺️ 🌧️ 🐿️ 💧 🧭)"}
def real(S): return S.get("realS")
def fig_runs():
    W, L, bw = 960, 300, 520; rows = [k for k in ORDER if k in F]; top = max((real(F[k]) or 120) for k in rows) * 1.1
    rh = 40; Hh = 40 + rh * len(rows) + 24
    o = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="The speed run’s real time, five ways">', SVGST,
         f'<text class="m" x="8" y="18">the speed run’s real time, from 🏃 to the dig (seconds), and its frames</text>']
    y = 30
    for k in rows:
        S = F[k]; r = real(S); w = bw * (r or 120) / top; c = "var(--accent2)" if k == "js" else "var(--accent)"
        lab = f'{r:.1f} s' if r else "not done in 120 s"
        o.append(f'<text class="m" x="8" y="{y + 18}">{E(NAME[k])}</text><rect x="{L}" y="{y + 5}" width="{w:.1f}" height="18" fill="{c}"/>'
                 f'<text class="m" x="{L + w + 6:.1f}" y="{y + 18}">{lab} · {S["gap"]["fps"]:.0f} fps median · {S["steps"]["n"]:.0f} steps a frame</text>')
        y += rh
    o.append(f'<text class="m" x="8" y="{Hh - 8}">One GitHub runner, headless Chrome at 1280×800, each setup a fresh page in turn.</text></svg>')
    return "".join(o)
def t_runs():
    h = ('<div class="wrap"><table class="nums"><thead><tr><th class="l">setup</th><th>real time</th><th>frame gap, median</th><th>p99</th><th>over 16.7 ms</th><th>steps a frame</th>'
         '<th>a step, median</th><th>Hazel’s share of the busy time</th><th>garbage collection</th></tr></thead><tbody>')
    for k in [k for k in ORDER if k in F]:
        S = F[k]; r = real(S)
        h += (f'<tr><td class="l">{E(NAME[k])}</td><td>{f"{r:.1f} s" if r else "over 120 s"}</td><td>{S["gap"]["median"]:.1f} ms ({S["gap"]["fps"]:.0f} fps)</td><td>{S["gap"]["p99"]:.1f} ms</td>'
              f'<td>{100 * S["over"]["16.7"] / S["over"]["n"]:.0f}%</td><td>{S["steps"]["n"]:.0f}</td><td>{S["steps"]["median"]:.1f} ms</td>'
              f'<td>{S["kinds"].get("the rules compiled from Hazel", 0):.1f}%</td><td>{S["kinds"].get("garbage collection", 0):.1f}%</td></tr>')
    return h + "</tbody></table></div>"

# ================= the tables =================
def t_builds():
    rows = [("1", "0.0.152", "Gnome world 0.0.152 (hazeljs-examples <code>5631853</code>): the flying level’s changes; the code counted in Matthew’s question"),
            ("2", "0.0.153", "build 1 with Plan.hz, the speed run’s planning, off unless <code>?plan=hazel</code> or 🗺️ (<code>50826bd</code>)"),
            ("3", "0.0.154", "build 2 with Rivers.hz, the rivers, pumps, rain and drying, off unless <code>?rivers=hazel</code> or 🌧️ (<code>aa7801e</code>)"),
            ("4", "0.0.155", "build 3 with Folk.hz, the villagers, squirrels, insects and hawks, off unless <code>?folk=hazel</code> or 🐿️ (<code>92ccd28</code>)"),
            ("5", "0.0.156", "build 4 with Folk.hz’s random numbers about four times as cheap (<code>97fccb2</code>); the frames job’s two more setups")]
    return ('<table class="nums"><thead><tr><th>build</th><th class="l">version</th><th class="l">what</th></tr></thead><tbody>' + "".join(f'<tr><td>{a}</td><td class="l">{b}</td><td class="l">{c}</td></tr>' for a, b, c in rows) + "</tbody></table>")
def share(Z, nd=False): hz, app = Z["hz_total"], Z["app_js"]; return 100 * hz / (hz + app - (Z["app_by"]["drawing"] if nd else 0))
def t_share():
    rows = [("Hazel’s rules (characters, comments left out)", f'{Z0["hz_total"]:,}', f'{Z1["hz_total"]:,}'),
            ("their lines", f'{Z0["hz_lines"]:,}', f'{Z1["hz_lines"]:,}'),
            ("<code>app.js</code> (characters)", f'{Z0["app_js"]:,}', f'{Z1["app_js"]:,}'),
            ("of which the drawing", f'{Z0["app_by"]["drawing"]:,}', f'{Z1["app_by"]["drawing"]:,}'),
            ("Hazel’s share of the game’s own code", f'{share(Z0):.1f}%', f'{share(Z1):.1f}%'),
            ("Hazel’s share of the code that is not drawing", f'{share(Z0, True):.1f}%', f'{share(Z1, True):.1f}%')]
    return ('<table class="nums"><thead><tr><th class="l"></th><th>0.0.152</th><th>0.0.156</th></tr></thead><tbody>' + "".join(f'<tr><td class="l">{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in rows) + "</tbody></table>")

def save_lines():
    p = os.path.join(DATA, f"save-check-{SAVES[-1]}.log")
    if not os.path.exists(p): p = os.path.join(DATA, f"save-check-{SAVES[0]}.log")
    out = []
    for line in open(p, encoding="utf-8"):
        m = re.search(r"Z (.+)$", line.strip())
        if m and m.group(1).startswith(("🗺", "🌧", "🐿")): out.append(m.group(1))
    return E("\n".join(out))

J, A = F.get("js"), F.get("all-hazel")
def fps(S): return f'{S["gap"]["fps"]:.0f} frames a second' if S else "?"
def rl(k): S = F.get(k); r = S and real(S); return f"{r:.1f} s" if r else "over 120 s"
note = ""
if J and A:
    note = (f'The frames come at {J["gap"]["median"]:.1f} ms ({J["gap"]["fps"]:.0f} fps) median either way, but with every Hazel option on a frame gets through {A["steps"]["n"]:.0f} of the game’s steps where it got through {J["steps"]["n"]:.0f}. '
            f'With every option on, the compiled Hazel is {A["kinds"].get("the rules compiled from Hazel", 0):.0f}% of the page’s busy time and garbage collection {A["kinds"].get("garbage collection", 0):.1f}%; '
            f'^report(69) found the water in Hazel alone at about half the busy time, so the water is most of it. The three new modules alone cost little: '
            + f'compiled Hazel is {F["plan-hazel"]["kinds"].get("the rules compiled from Hazel", 0):.1f}% of the busy time with the planning in Hazel, {F["rivers-hazel"]["kinds"].get("the rules compiled from Hazel", 0):.1f}% with the rivers and {F["folk-hazel"]["kinds"].get("the rules compiled from Hazel", 0):.1f}% with the creatures, '
            f'against {J["kinds"].get("the rules compiled from Hazel", 0):.1f}% with none of them on (the gnome’s step and the other rules that were Hazel already).')
FIG = {"costs": fig_costs(), "runs": fig_runs(), "t_runs": t_runs(), "t_builds": t_builds(), "t_share": t_share(), "save_lines": save_lines()}
N = {"order_js": f'{PL["order"]["js_ms"]:.1f}', "order_hz": f'{PL["order"]["hazel_ms"]:.0f}', "rv_js": f3(rv_js), "rv_hz": f3(rv_hz), "folk_js": f3(folk_js), "folk_hz": f2(folk_hz),
     "rand_old": f'{(P["bug_call_us"]["0.0.155"]["dragonfly, three draws"] - P["bug_call_us"]["0.0.155"]["dragonfly, no draw"]) / 3:.1f}',
     "rand_new": f'{(P["bug_call_us"]["0.0.156"]["dragonfly, three draws"] - P["bug_call_us"]["0.0.156"]["dragonfly, no draw"]) / 3:.1f}',
     "bugs_old": f2(mean([r["hazel"]["bugs"] for r in F5])), "bugs_new": f2(F6["hazel"]["bugs"]),
     "flee": P["folk_0155"]["flee_steps"], "hawk_steps": ", ".join(f"{k} {v}" for k, v in P["folk_0155"]["hawk_steps"].items()),
     "js_real": rl("js"), "all_real": rl("all-hazel"), "plan_real": rl("plan-hazel"), "rivers_real": rl("rivers-hazel"), "folk_real": rl("folk-hazel"),
     "js_fps": fps(J), "all_fps": fps(A), "runs_note": note, "plan_worst": f'{F["plan-hazel"]["gap"]["worst"]:.0f}', "js_worst": f'{J["gap"]["worst"]:.0f}',
     "all_where": f'after two minutes it had found all {A["things"].split("/")[1]} things, all {A["parts"].split("/")[1]} tree parts and {A["gems"].split("/")[0]} of {A["gems"].split("/")[1]} gems' if A else "?",
     "share_old": f"{share(Z0):.0f}%", "share_new": f"{share(Z1):.0f}%", "share_nd_old": f"{share(Z0, True):.0f}%", "share_nd_new": f"{share(Z1, True):.0f}%",
     "hz_lines": f'{Z1["hz_lines"]:,}', "hz_modules": len([k for k in Z1["hz"] if k != "preamble"]), "app_kb": f'{Z1["app_js"] / 1000:.0f}', "draw_kb": f'{Z1["app_by"]["drawing"] / 1000:.0f}',
     "run_f": FINAL, "m_f": E(machine(FINAL)), "save_runs": " and ".join(SAVES), "updated": updated}
R = sorted(((hz / js, n) for n, js, hz in PIECES))
N.update({"x_lo_name": "the " + R[0][1].split(",")[0], "x_hi": f"{R[-1][0]:.0f}", "x_hi_name": R[-1][1].replace(" (once)", ", worked out once"),
          "step_ms": f'{J["steps"]["median"] / J["steps"]["n"]:.1f}' if J else "?"})
FIG.update(N)
body = open(os.path.join(HERE, "body.html"), encoding="utf-8").read()
for k, v in FIG.items(): body = body.replace("{{" + k + "}}", str(v))
left = re.findall(r"\{\{(\w+)\}\}", body); assert not left, left
TITLE = "Gnome World’s Planning, Rivers and Folk, in Hazel"
DESC = (f"Three more Hazel modules in Gnome world, each off by default and held by the save check to give the same answers as the page's JavaScript: the speed run's planning, the rivers, pumps and rain, and the villagers, squirrels, insects and hawks, with the page's own random numbers worked out in Hazel. "
        f"Each piece takes from about as long to {N['x_hi']} times as long in Hazel, and is small: with one on, the speed run takes about what it did ({N['js_real']}); with every Hazel option on, the water among them, it does not finish in two minutes. "
        f"Hazel is now {N['share_new']} of the game's code; the drawing, 44% of app.js, is next.")
EXTRA = """
  figure.chart svg { width: 100%; height: auto; display: block; }
  table.nums td, table.nums th { text-align: right; font-variant-numeric: tabular-nums; } table.nums td.l, table.nums th.l { text-align: left; }
  .wrap { overflow-x: auto; }
  pre.log { white-space: pre-wrap; word-break: break-word; font-size: 12px; }
"""
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{E(DESC)}\">\n<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(head + body)

def thumb(mode):
    base = ".h{fill:#1f2328;font:700 15px system-ui,sans-serif}.m{fill:#5b6470;font:10px system-ui,sans-serif}.k{fill:#1f2328;font:700 11px system-ui,sans-serif}.j{fill:#0e7490}.z{fill:#6d28d9}"
    dark = ".h{fill:#e8e6e3}.m{fill:#a2a9b3}.k{fill:#e8e6e3}.j{fill:#67e8f9}.z{fill:#c4b5fd}"
    style = base + ("\n" + dark if mode == "dark" else "\n@media (prefers-color-scheme: dark) {" + dark + "}" if mode == "auto" else "")
    X = lambda v: 16 + 240 * (math.log10(max(v, 0.001)) + 3) / 5.3
    rows = [("the creatures, a step", folk_js, folk_hz), ("the order of the things, once", PL["order"]["js_ms"], PL["order"]["hazel_ms"])]
    out = []
    for i, (n, js, hz) in enumerate(rows):
        y = 66 + i * 52
        out.append(f'<text class="m" x="16" y="{y - 4}">{n}: JavaScript and Hazel (log)</text><rect class="j" x="16" y="{y}" width="{X(js) - 16:.1f}" height="12"/><text class="k" x="{X(js) + 4:.1f}" y="{y + 10}">{js:g} ms</text>'
                   f'<rect class="z" x="16" y="{y + 16}" width="{X(hz) - 16:.1f}" height="12"/><text class="k" x="{X(hz) + 4:.1f}" y="{y + 26}">{hz:g} ms</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" width="320" height="200">\n<style>{style}\n</style>\n'
            '<text class="h" x="16" y="26">Planning, rivers, folk, in Hazel</text>\n<text class="m" x="16" y="42">the same answers as the page’s, its random numbers too</text>\n'
            + "".join(out) + f'\n<text class="m" x="16" y="186">Hazel: {N["share_old"]} → {N["share_new"]} of the code; drawing next</text>\n</svg>\n')
os.makedirs(os.path.join(HERE, "img"), exist_ok=True)
for name, mode in [("thumb-light.svg", "light"), ("thumb-dark.svg", "dark"), ("thumb.svg", "auto")]: open(os.path.join(HERE, "img", name), "w").write(thumb(mode))
meta = {"title": TITLE, "blurb": DESC,
        "builds": {"1 (0.0.152)": "hazeljs-examples 5631853", "2 (0.0.153)": "50826bd, Plan.hz", "3 (0.0.154)": "aa7801e, Rivers.hz", "4 (0.0.155)": "92ccd28, Folk.hz", "5 (0.0.156)": "97fccb2, Folk.hz's rand cheaper"},
        "runs": {"pane": P["where"], "frames": f"hazeljs-examples 'world speed run, frame by frame' run {FINAL} ({machine(FINAL)}), headless Chrome at 1280×800, each setup in turn up to two minutes",
                 "save check": "hazeljs-examples 'world save check' runs " + ", ".join(SAVES)},
        "measures": {"a piece's ms": "the mean over the steps run (planning: one call)", "real time": "wall-clock seconds from pressing 🏃 to the run's dig",
                     "share of the code": "characters, comments left out of the Hazel (sizes.py)"},
        "files": ["data/pane.json", "data/frames-*.log", "data/frames-*.json", "data/save-check-*.log", "data/sizes-*.json", "parse_frames.py", "sizes.py", "gen070.py"]}
json.dump(meta, open(os.path.join(DATA, "meta.json"), "w"), indent=1, ensure_ascii=False)
print("wrote 070/index.html;", updated)
for k in sorted(N): print(f"  {k}: {N[k]}")
