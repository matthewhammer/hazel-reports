#!/usr/bin/env python3
"""^report(65): hazel-jit's PR, Described. Matthew Hammer, 2026-11-25, on the new description drafted for
hazelgrove/hazel#2859: "for 2859 --- let's create a new WIP report and iterate on the content of the PR description
there. The point of the report is to iterate on the details within the PR description, esp the executive and
engineering summaries." And: "in this new report, let's have a section that compares the other Ocaml to JS compilation
strategies we reported on before to one, in terms of representations. We can compare performance too, for the new set
of benchmarks (hazel activities), which we largely didn't have before."

One source for the description: pr-2859.md, the text for GitHub, in GitHub's Markdown. This script renders its
sections into the report (each marked "in the PR") between the report's own sections (body.html), and puts the
Markdown itself in the page, to copy. data/*.json hold the numbers the text quotes."""
import html, json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
esc = lambda s: html.escape(str(s), quote=True)

# ---- the Markdown GitHub's descriptions use here: ## headings, paragraphs, - lists, tables, `code`, **bold**, [links](url)
def inline(s):
    out, parts = [], re.split(r"(`[^`]*`)", s)
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) >= 2:
            out.append("<code>" + esc(p[1:-1]) + "</code>")
            continue
        p = esc(p)
        p = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", p)
        p = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', p)
        out.append(p)
    return "".join(out)

def blocks(md):
    """the Markdown of one section as HTML"""
    lines, out, i = md.strip("\n").split("\n"), [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], [r for r in rows[2:]]
            out.append('<div class="tw"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table></div>")
        elif ln.startswith("- "):
            items = []
            while i < len(lines) and (lines[i].startswith("- ") or (lines[i].startswith("  ") and items)):
                if lines[i].startswith("- "): items.append(lines[i][2:])
                else: items[-1] += " " + lines[i].strip()
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(t)}</li>" for t in items) + "</ul>")
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("|", "- ", "## ")):
                para.append(lines[i]); i += 1
            out.append("<p>" + inline(" ".join(para)) + "</p>")
    return "\n".join(out)

MD = open(os.path.join(HERE, "pr-2859.md"), encoding="utf-8").read()
chunks = re.split(r"^## (.+)$", MD, flags=re.M)
PREAMBLE, SECTIONS = chunks[0], list(zip(chunks[1::2], chunks[2::2]))
IDS = {"Executive summary": "exec", "Engineering summary": "eng", "What it holds": "holds", "How compiled values look": "values",
       "Beside other compilers to JavaScript": "beside", "Where it comes from": "origin",
       "Where it differs from the interpreter on `dev`": "differs", "Next, on this branch": "pr-next"}
assert [h for h, _ in SECTIONS] == list(IDS), [h for h, _ in SECTIONS]
# the closing line (the Claude Code credit) stays in the Markdown to copy, not in the report's sections
last_h, last_md = SECTIONS[-1]
CREDIT = "🤖 Generated with [Claude Code](https://claude.com/claude-code)"
assert last_md.rstrip().endswith(CREDIT)
SECTIONS[-1] = (last_h, last_md.rstrip()[: -len(CREDIT)])

def pr_section(h, md):
    return (f'<section class="inpr"><h2 id="{IDS[h]}">{inline(h)}</h2>\n<p class="tag">In the PR’s description</p>\n{blocks(md)}\n</section>')

FIGS = {"updated": updated, "pr_preamble": f'<section class="inpr"><p class="tag">In the PR’s description: its opening line</p>\n{blocks(PREAMBLE)}\n</section>',
        "pr_md": MD.replace("</", "<\\/"), "pr_md_shown": esc(MD), "pr_words": f"{len(re.findall(r'[A-Za-z0-9]+', MD)):,}"}
for h, md in SECTIONS: FIGS["pr_" + IDS[h].replace("-", "_")] = pr_section(h, md)

SWEEP = json.load(open(os.path.join(DATA, "sweep.json")))
FIGS.update({"sw_checks": str(SWEEP["checks"]), "sw_compiled": str(SWEEP["compiled"]), "sw_agreed": str(SWEEP["agreed"]),
             "sw_not_value": str(SWEEP["not_a_value"]), "sw_run": str(SWEEP["run"])})
REP = json.load(open(os.path.join(DATA, "representations.json")))
def rep_table():
    cols = REP["columns"]
    head = "".join(f"<th>{esc(c)}</th>" for c in ["Value"] + cols)
    prev = {"hazel-jit now": "hazel-jit 2026-11-07"}
    rows = "".join("<tr><td>" + esc(r["value"]) + "</td>" + "".join(f'<td class="{"chg" if c in prev and r[c] != r[prev[c]] else ""}"><code>{esc(r[c])}</code></td>' for c in cols) + "</tr>" for r in REP["rows"])
    return f'<div class="tw"><table class="rep"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
def sugg_list():
    return "<ol class=\"sugg\">" + "".join(f'<li><span class="st {s["status"]}">{esc(s["status_text"])}</span> <b>{esc(s["what"])}</b> {esc(s["now"])}</li>' for s in REP["suggestions"]) + "</ol>"
FIGS.update({"rep_table": rep_table(), "sugg_list": sugg_list()})
PETRI = json.load(open(os.path.join(DATA, "petri-046.json")))
def petri_table():
    num = lambda v: "" if v is None else (f"{v:,.0f}" if v >= 100 else f"{v:.2f}")
    rows = "".join(f'<tr><td class="l">{esc(r["who"])}</td><td>{num(r["median_us"])}</td><td>{num(r.get("fastest_us"))}</td></tr>' for r in PETRI["rows"])
    return f'<div class="tw"><table class="nums"><thead><tr><th class="l">Compiler</th><th>µs a call, median</th><th>the fastest call</th></tr></thead><tbody>{rows}</tbody></table></div>'
FIGS["petri_table"] = petri_table()

# (ticket 853) today's two changes, timed: report 046's Petri rule on this laptop, and each game's own run on GitHub
import math
gm = lambda xs: math.exp(sum(map(math.log, xs)) / len(xs))
P853 = json.load(open(os.path.join(DATA, "petri-853.json")))
def petri853_table():
    num = lambda v: f"{v:.2f}"
    rows = "".join(f'<tr><td class="l">{esc(r["who"])}</td><td>{num(r["median_us"])}</td><td>{num(r["fastest_us"])}</td></tr>' for r in P853["rows"])
    return f'<div class="tw"><table class="nums"><thead><tr><th class="l">Code</th><th>µs a call, median</th><th>the fastest call</th></tr></thead><tbody>{rows}</tbody></table></div>'
pv = {(r["way"], r["key"]): r["median_us"] for r in P853["rows"]}
GAMES = ["checkers", "go", "minesweeper", "mahjong", "solitaire", "mahjong-solitaire", "pinball", "downhill", "bricks", "snake", "trails", "starwave", "bugs", "dig"]
GNAME = {"checkers": "Checkers", "go": "Go", "minesweeper": "Minesweeper", "mahjong": "Mahjong", "solitaire": "Solitaire", "mahjong-solitaire": "Mahjong solitaire",
         "pinball": "Pinball", "downhill": "Downhill", "bricks": "Bricks", "snake": "Snake", "trails": "Light trails", "starwave": "Star wave", "bugs": "Butterfly garden", "dig": "Gnome dig"}
def run_of(g, k):
    d = json.load(open(os.path.join(DATA, "games-853", f"b853-{g}", f"{g}-{k}.json")))
    r = d["runs"][0]
    assert all(v is None or v.get("same") for v in r["ways"].values()), (g, k)
    return r["name"], r["steps"], {w: v["usPerCall"] for w, v in r["ways"].items() if v}
G853 = []
for g in GAMES:
    nm, steps, b = run_of(g, "base"); _, _, t = run_of(g, "trial"); _, _, b2 = run_of(g, "base2")
    base = (b["jit"] + b2["jit"]) / 2
    G853.append({"game": g, "run": nm, "steps": steps, "base": base, "base1": b["jit"], "base2": b2["jit"], "trial": t["jit"], "ratio": t["jit"] / base,
                 "aot_ratio": t["compiled"] / ((b["compiled"] + b2["compiled"]) / 2), "noise": b2["jit"] / b["jit"]})
def t_us(us):
    return f"{us:.1f} µs" if us >= 10 else f"{us:.2f} µs"
def games853_svg():
    rows = sorted(G853, key=lambda r: r["ratio"])
    W, L, top, bh, gap = 720, 150, 30, 18, 6
    x = lambda v: L + v * (W - L - 70)
    h = top + len(rows) * (bh + gap) + 34
    bars = "".join(f'<text class="lbl" x="{L - 8}" y="{top + i * (bh + gap) + 13}" text-anchor="end">{esc(GNAME[r["game"]])}</text>'
                   f'<rect class="bar" x="{L}" y="{top + i * (bh + gap)}" width="{x(r["ratio"]) - L:.1f}" height="{bh}" rx="2"/>'
                   f'<text class="val" x="{x(r["ratio"]) + 6:.1f}" y="{top + i * (bh + gap) + 13}">{r["ratio"]:.2f}</text>' for i, r in enumerate(rows))
    one = x(1.0)
    return (f'<svg viewBox="0 0 {W} {h}" role="img" aria-labelledby="g853t"><title id="g853t">Each game\'s time a call through the jit with loops and JS arguments, as a share of the base\'s</title>'
            f'<text class="mut" x="{L}" y="16">share of the base’s time a call (shorter is faster); the line is the base</text>{bars}'
            f'<line class="one" x1="{one:.1f}" y1="{top - 6}" x2="{one:.1f}" y2="{h - 28}"/><text class="mut" x="{one:.1f}" y="{h - 12}" text-anchor="middle">1.0</text></svg>')
def games853_table():
    rows = "".join(f'<tr><td class="l">{esc(GNAME[r["game"]])}</td><td>{r["steps"]:,}</td><td>{t_us(r["base1"])}</td><td>{t_us(r["base2"])}</td><td>{t_us(r["trial"])}</td><td>{r["ratio"]:.2f}</td><td>{r["aot_ratio"]:.2f}</td></tr>' for r in G853)
    return ('<div class="tw"><table class="nums"><thead><tr><th class="l">Game</th><th>calls in its run</th><th>base</th><th>base, again</th><th>loops and JS arguments</th>'
            f'<th>share of the base’s mean</th><th>its own compiled.js, same file</th></tr></thead><tbody>{rows}</tbody></table></div>')
rs = sorted(G853, key=lambda r: r["ratio"])
# (bench/853-split, run 45641693384) the two changes apart, on one runner a game: the base, loops alone, both
SPL = []
for g in GAMES:
    def get(k):
        r = json.load(open(os.path.join(DATA, "games-853-split", f"b853s-{g}", f"{g}-{k}.json")))["runs"][0]
        assert all(v is None or v.get("same") for v in r["ways"].values()), (g, k)
        return {w: v["usPerCall"] for w, v in r["ways"].items() if v}
    b, l, t = get("base"), get("loops"), get("trial")
    SPL.append({"game": g, "base": b["jit"], "loops": l["jit"], "both": t["jit"], "aot_l": l["compiled"] / b["compiled"], "aot_b": t["compiled"] / b["compiled"]})
def split_table():
    rows = "".join(f'<tr><td class="l">{esc(GNAME[r["game"]])}</td><td>{t_us(r["base"])}</td><td>{t_us(r["loops"])}</td><td>{r["loops"] / r["base"]:.2f}</td><td>{t_us(r["both"])}</td><td>{r["both"] / r["base"]:.2f}</td></tr>' for r in SPL)
    return ('<div class="tw"><table class="nums"><thead><tr><th class="l">Game</th><th>base</th><th>loops alone</th><th>share</th><th>both</th><th>share</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')
# (bench/853-more, run 45645748545) the next wave, one build after another on one runner a game: the base (loops and JS
# arguments, as merged), constructors made once (c1), modules by name (c2), === against a literal (c3), and on top of c3
# Ints as plain numbers (noint) and no step counted (nostep), both bench builds only
MW = ["base", "c1", "c2", "c3", "noint", "nostep"]
MORE = {}
for g in GAMES:
    MORE[g] = {}
    for w in MW:
        r = json.load(open(os.path.join(DATA, "games-853-more", f"b853m-{g}", f"{g}-{w}.json")))["runs"][0]
        assert all(v is None or v.get("same") for v in r["ways"].values()), (g, w)
        MORE[g][w] = {k: v["usPerCall"] for k, v in r["ways"].items() if v}
mr = lambda a, b, g, k="jit": MORE[g][a][k] / MORE[g][b][k]
def more_table():
    head = "".join(f"<th>{h}</th>" for h in ["base", "constructors once", "modules by name", "=== too", "Ints plain", "no steps"])
    rows = "".join(f'<tr><td class="l">{esc(GNAME[g])}</td><td>{t_us(MORE[g]["base"]["jit"])}</td>' + "".join(f'<td>{mr(w, "base", g):.2f}</td>' for w in MW[1:]) + "</tr>" for g in GAMES)
    foot = '<tr class="gm"><td class="l">geometric mean</td><td></td>' + "".join(f'<td>{gm([mr(w, "base", g) for g in GAMES]):.2f}</td>' for w in MW[1:]) + "</tr>"
    return f'<div class="tw"><table class="nums"><thead><tr><th class="l">Game</th>{head}</tr></thead><tbody>{rows}{foot}</tbody></table></div>'
PM = [json.loads(l) for l in open(os.path.join(DATA, "petri-more-runs.jsonl"))]
pmm = lambda w: sorted(r["r"]["hazel"]["median_us"] for r in PM if r["way"] == w)[2]
FIGS.update({"more_table": more_table(),
             "mw_c1": f'{gm([mr("c1", "base", g) for g in GAMES]):.2f}', "mw_c2": f'{gm([mr("c2", "c1", g) for g in GAMES]):.2f}', "mw_c3": f'{gm([mr("c3", "c2", g) for g in GAMES]):.2f}',
             "mw_all": f'{gm([mr("c3", "base", g) for g in GAMES]):.2f}',
             "mw_noint": f'{gm([mr("noint", "c3", g) for g in GAMES]):.2f}', "mw_nostep": f'{gm([mr("nostep", "c3", g) for g in GAMES]):.2f}',
             "mw_int_cost": f'{100 * (1 / gm([mr("noint", "c3", g) for g in GAMES]) - 1):.0f}%', "mw_step_cost": f'{100 * (1 / gm([mr("nostep", "c3", g) for g in GAMES]) - 1):.0f}%',
             "mw_aot": f'{gm([mr("c3", "base", g, "compiled") for g in GAMES]):.2f}',
             "mw_int_top": ", ".join(f'{GNAME[g]} {mr("noint", "c3", g):.2f}' for g in sorted(GAMES, key=lambda g: mr("noint", "c3", g))[:3]),
             "mw_step_top": ", ".join(f'{GNAME[g]} {mr("nostep", "c3", g):.2f}' for g in sorted(GAMES, key=lambda g: mr("nostep", "c3", g))[:3]),
             "pm_base": f'{pmm("base"):.2f}', "pm_c1": f'{pmm("c1"):.2f}', "pm_c2": f'{pmm("c2"):.2f}', "pm_c3": f'{pmm("c3"):.2f}', "pm_noint": f'{pmm("noint"):.2f}', "pm_nostep": f'{pmm("nostep"):.2f}'})
# (#crossing) conversion at the edges over time, and the Petri rule's call direct against through the jit
TL = json.load(open(os.path.join(DATA, "crossing-timeline.json")))
def timeline_svg():
    rows = [r for r in TL["rows"] if r["measure"] == "runs"]
    W, L, top, bh, gap = 720, 300, 30, 20, 8
    x = lambda v: L + v * (W - L - 60)
    h = top + len(rows) * (bh + gap) + 30
    bars = "".join(f'<text class="lbl" x="{L - 8}" y="{top + i * (bh + gap) + 14}" text-anchor="end">{esc(r["date"][5:])} · {esc(r["build"])}</text>'
                   f'<rect class="bar" x="{L}" y="{top + i * (bh + gap)}" width="{x(r["ratio"]) - L:.1f}" height="{bh}" rx="2"/>'
                   f'<text class="val" x="{x(r["ratio"]) + 6:.1f}" y="{top + i * (bh + gap) + 14}">{r["ratio"]:.2f}</text>' for i, r in enumerate(rows))
    one = x(1.0)
    return (f'<svg viewBox="0 0 {W} {h}" role="img" aria-labelledby="tlt"><title id="tlt">The jit\'s time a call as a share of the games\' own compiled.js, build by build</title>'
            f'<text class="mut" x="{L}" y="16">the jit’s time a call, as a share of the games’ own compiled.js (the line)</text>{bars}'
            f'<line class="one" x1="{one:.1f}" y1="{top - 6}" x2="{one:.1f}" y2="{h - 24}"/><text class="mut" x="{one:.1f}" y="{h - 8}" text-anchor="middle">1.0</text></svg>')
def timeline_table():
    rows = "".join(f'<tr><td class="l">{esc(r["date"])}</td><td class="l">{esc(r["build"])}</td><td class="l">{esc(r["change"])}</td><td>{r["ratio"]:.2f}</td></tr>' for r in TL["rows"])
    return ('<div class="tw"><table class="nums"><thead><tr><th class="l">When</th><th class="l">Build</th><th class="l">What changed at the edge</th><th>the jit / compiled.js</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')
PX = [json.loads(l) for l in open(os.path.join(DATA, "petri-crossing-runs.jsonl"))]
pxm = lambda b, m: sorted(r["r"]["hazel" if m == "hazel" else "jit"]["median_us"] for r in PX if r["build"] == b and r["mode"] == m)[2]
def petri_cross_svg():
    W, L, top, bh, gap = 720, 230, 34, 26, 14
    rows = [("hazeljs 0.0.13", "base"), ("today’s, with ===", "c3")]
    mx = max(pxm(b, "jit") for _, b in rows)
    x = lambda v: L + v / mx * (W - L - 200)
    out = []
    for i, (name, b) in enumerate(rows):
        y = top + i * (bh + gap); d = pxm(b, "hazel"); j = pxm(b, "jit")
        out.append(f'<text class="lbl" x="{L - 8}" y="{y + 17}" text-anchor="end">{esc(name)}</text>'
                   f'<rect class="code" x="{L}" y="{y}" width="{x(d) - L:.1f}" height="{bh}"/>'
                   f'<rect class="cross" x="{x(d):.1f}" y="{y}" width="{x(j) - x(d):.1f}" height="{bh}"/>'
                   f'<text class="val" x="{x(j) + 6:.1f}" y="{y + 17}">{j:.1f} µs, {100 * (j - d) / j:.0f}% converting</text>')
    h = top + len(rows) * (bh + gap) + 10
    return (f'<svg viewBox="0 0 {W} {h}" role="img" aria-labelledby="pxt"><title id="pxt">The Petri rule\'s call through the jit: the compiled code, and converting in and out</title>'
            f'<rect class="code" x="{L}" y="8" width="12" height="12"/><text class="mut" x="{L + 18}" y="18">the compiled code</text>'
            f'<rect class="cross" x="{L + 160}" y="8" width="12" height="12"/><text class="mut" x="{L + 178}" y="18">converting the values in and out</text>{"".join(out)}</svg>')
FIGS.update({"timeline_svg": timeline_svg(), "timeline_table": timeline_table(), "petri_cross_svg": petri_cross_svg(),
             "px_base_d": f'{pxm("base", "hazel"):.2f}', "px_base_j": f'{pxm("base", "jit"):.2f}', "px_c3_d": f'{pxm("c3", "hazel"):.2f}', "px_c3_j": f'{pxm("c3", "jit"):.2f}',
             "px_base_x": f'{pxm("base", "jit") - pxm("base", "hazel"):.1f}', "px_c3_x": f'{pxm("c3", "jit") - pxm("c3", "hazel"):.1f}',
             "px_base_share": f'{100 * (1 - pxm("base", "hazel") / pxm("base", "jit")):.0f}%', "px_c3_share": f'{100 * (1 - pxm("c3", "hazel") / pxm("c3", "jit")):.0f}%'})
# (#fourway) four ways on each game's own run (bench/4way, run 45650465391): the interpreter, hazel-jit as of 2026-11-19 (each
# game's own compiled.js), hazel-jit now (Hazel.jitProgram, hazeljs 2c4a61560f), plain JS (five games)
FW = {}
FWSTEPS = {}
for g in GAMES:
    r = json.load(open(os.path.join(DATA, "games-4way", f"b4way-{g}", f"{g}-4way.json")))["runs"][0]
    assert all(v is None or v.get("same") for v in r["ways"].values()), g
    FW[g] = {k: v["usPerCall"] for k, v in r["ways"].items() if v}
    FWSTEPS[g] = r["steps"]
WAYS4 = [("interpreted", "the interpreter", "mi"), ("compiled", "hazel-jit, 2026-11-19", "mc"), ("jit", "hazel-jit now", "mj"), ("plain JS", "plain JS", "mp")]
PLAIN = [g for g in GAMES if "plain JS" in FW[g]]
def fw_svg():
    import math as _m
    W, L, top, rh = 720, 150, 44, 22
    lo, hi = 0.3, 300000.0
    x = lambda v: L + (_m.log10(v) - _m.log10(lo)) / (_m.log10(hi) - _m.log10(lo)) * (W - L - 20)
    h = top + len(GAMES) * rh + 40
    ticks = "".join(f'<line class="grid" x1="{x(t):.1f}" y1="{top - 8}" x2="{x(t):.1f}" y2="{top + len(GAMES) * rh}"/><text class="mut" x="{x(t):.1f}" y="{top + len(GAMES) * rh + 16}" text-anchor="middle">{lab}</text>'
                    for t, lab in [(1, "1 µs"), (10, "10 µs"), (100, "100 µs"), (1000, "1 ms"), (10000, "10 ms"), (100000, "100 ms")])
    legend = "".join(f'<circle class="{c}" cx="{L + i * 145 + 6}" cy="16" r="5"/><text class="mut" x="{L + i * 145 + 16}" y="20">{esc(n)}</text>' for i, (_, n, c) in enumerate(WAYS4))
    rows = ""
    for i, g in enumerate(GAMES):
        y = top + i * rh + rh / 2
        vals = [FW[g][k] for k, _, _ in WAYS4 if k in FW[g]]
        rows += f'<text class="lbl" x="{L - 8}" y="{y + 4:.1f}" text-anchor="end">{esc(GNAME[g])}</text><line class="span" x1="{x(min(vals)):.1f}" y1="{y:.1f}" x2="{x(max(vals)):.1f}" y2="{y:.1f}"/>'
        rows += "".join(f'<circle class="{c}" cx="{x(FW[g][k]):.1f}" cy="{y:.1f}" r="5"><title>{esc(n)}: {t_us(FW[g][k]) if FW[g][k] < 1000 else f"{FW[g][k] / 1000:.1f} ms"}</title></circle>' for k, n, c in WAYS4 if k in FW[g])
    return (f'<svg viewBox="0 0 {W} {h}" role="img" aria-labelledby="fwt"><title id="fwt">Each game\'s time a call, four ways, on a log scale</title>{legend}{ticks}{rows}</svg>')
def fmt_us(v):
    return f"{v / 1000:,.1f} ms" if v >= 1000 else t_us(v)
def fw_table():
    head = "".join(f"<th>{esc(n)}</th>" for _, n, _ in WAYS4)
    rows = "".join(f'<tr><td class="l">{esc(GNAME[g])}</td><td>{FWSTEPS[g]:,}</td>' + "".join(f'<td>{fmt_us(FW[g][k]) if k in FW[g] else "–"}</td>' for k, _, _ in WAYS4) + f'<td>{FW[g]["interpreted"] / FW[g]["jit"]:,.0f}×</td><td>{FW[g]["compiled"] / FW[g]["jit"]:.1f}×</td></tr>' for g in GAMES)
    return (f'<div class="tw"><table class="nums"><thead><tr><th class="l">Game</th><th>calls in its run</th>{head}<th>now against the interpreter</th><th>now against 11-19</th></tr></thead><tbody>{rows}</tbody></table></div>')
gm4 = lambda k, gs: gm([FW[g][k] for g in gs])
FIGS.update({"fw_svg": fw_svg(), "fw_table": fw_table(),
             "fw_ij": f'{gm([FW[g]["interpreted"] / FW[g]["jit"] for g in GAMES]):,.0f}', "fw_ic": f'{gm([FW[g]["interpreted"] / FW[g]["compiled"] for g in GAMES]):,.0f}',
             "fw_cj": f'{gm([FW[g]["compiled"] / FW[g]["jit"] for g in GAMES]):.1f}',
             "fw_jp": f'{gm([FW[g]["jit"] / FW[g]["plain JS"] for g in PLAIN]):.1f}', "fw_cp": f'{gm([FW[g]["compiled"] / FW[g]["plain JS"] for g in PLAIN]):.1f}',
             "fw_ip": f'{gm([FW[g]["interpreted"] / FW[g]["plain JS"] for g in PLAIN]):,.0f}',
             "fw5_i": fmt_us(gm4("interpreted", PLAIN)), "fw5_c": fmt_us(gm4("compiled", PLAIN)), "fw5_j": fmt_us(gm4("jit", PLAIN)), "fw5_p": fmt_us(gm4("plain JS", PLAIN)),
             "fw_plain": ", ".join(GNAME[g] for g in PLAIN), "fw_n": str(len(GAMES)), "fw_steps": f'{sum(FWSTEPS.values()):,}',
             "fw_best": ", ".join(f'{GNAME[g]} {FW[g]["compiled"] / FW[g]["jit"]:.1f}×' for g in sorted(GAMES, key=lambda g: -FW[g]["compiled"] / FW[g]["jit"])[:3]),
             "fw_least": ", ".join(f'{GNAME[g]} {FW[g]["compiled"] / FW[g]["jit"]:.1f}×' for g in sorted(GAMES, key=lambda g: FW[g]["compiled"] / FW[g]["jit"])[:3])})
PS = [json.loads(l) for l in open(os.path.join(DATA, "petri-split-runs.jsonl"))]
pmed = lambda w: sorted(r["r"]["hazel"]["median_us"] for r in PS if r["way"] == w)[2]
FIGS.update({"split_table": split_table(), "sp_loops": f'{gm([r["loops"] / r["base"] for r in SPL]):.2f}', "sp_both": f'{gm([r["both"] / r["base"] for r in SPL]):.2f}',
             "sp_lo": f'{min(r["loops"] / r["base"] for r in SPL):.2f}', "sp_hi": f'{max(r["loops"] / r["base"] for r in SPL):.2f}',
             "sp_aot": f'{gm([r["aot_l"] for r in SPL]):.2f} and {gm([r["aot_b"] for r in SPL]):.2f}',
             "ps_base": f'{pmed("base"):.2f}', "ps_loops": f'{pmed("loops"):.2f}', "ps_both": f'{pmed("trial"):.2f}'})
FIGS.update({"petri853_table": petri853_table(), "games853_svg": games853_svg(), "games853_table": games853_table(),
             "g853_gm": f'{gm([r["ratio"] for r in G853]):.2f}', "g853_n": str(len(G853)),
             "g853_best": ", ".join(f'{GNAME[r["game"]]} {r["ratio"]:.2f}' for r in rs[:4]),
             "g853_least": ", ".join(f'{GNAME[r["game"]]} {r["ratio"]:.2f}' for r in rs[-3:][::-1]),
             "g853_noise": f'{gm([r["noise"] for r in G853]):.2f}', "g853_noise_lo": f'{min(r["noise"] for r in G853):.2f}', "g853_noise_hi": f'{max(r["noise"] for r in G853):.2f}',
             "g853_aot": f'{gm([r["aot_ratio"] for r in G853]):.2f}',
             "p853_res": f'{pv[("others", "rescript")]:.2f}', "p853_mel": f'{pv[("others", "melange")]:.2f}', "p853_js": f'{pv[("others", "js")]:.2f}',
             "p853_base": f'{pv[("base", "hazel")]:.2f}', "p853_trial": f'{pv[("trial", "hazel")]:.2f}',
             "p853_ratio": f'{pv[("trial", "hazel")] / pv[("base", "hazel")]:.2f}', "p853_vs_res": f'{pv[("trial", "hazel")] / pv[("others", "rescript")]:.1f}',
             "p853_base_vs_res": f'{pv[("base", "hazel")] / pv[("others", "rescript")]:.1f}'})

EXTRA = """
  section.inpr { border-left: 3px solid var(--accent, #2a78d6); padding-left: 14px; margin-left: -17px; }
  section.inpr p.tag { color: var(--muted); font-size: 0.82em; margin: -0.4em 0 0.6em; text-transform: uppercase; letter-spacing: 0.04em; }
  p.tag.own { color: var(--muted); font-size: 0.82em; margin: -0.4em 0 0.6em; text-transform: uppercase; letter-spacing: 0.04em; }
  .tw { overflow-x: auto; margin: 0.6em 0 1em; }
  svg .mi { fill: #6b737d; } svg .mc { fill: #2a78d6; } svg .mj { fill: #eb6834; } svg .mp { fill: #2e9e5b; } svg .grid { stroke: var(--line); } svg .span { stroke: var(--line); stroke-width: 2; }
  svg .code { fill: #2a78d6; } svg .cross { fill: #eb6834; }
  table.nums tr.gm td { font-weight: 700; border-top: 2px solid var(--line); }
  .tw table.rep { min-width: 820px; } table.rep code { word-break: normal; overflow-wrap: break-word; }
  table.rep td.chg { background: color-mix(in srgb, var(--good, #2e9e5b) 14%, transparent); }
  table.nums td, table.nums th { text-align: right; font-variant-numeric: tabular-nums; } table.nums td.l, table.nums th.l { text-align: left; }
  ol.sugg li { margin-bottom: 0.5em; } .st { display: inline-block; padding: 0 7px; border-radius: 999px; font-size: 0.8em; font-weight: 600; color: #fff; }
  .st.done { background: #2e9e5b; } .st.part { background: #b07d10; } .st.open { background: #6b737d; }
  figure.chart svg { width: 100%; height: auto; display: block; }
  svg .lbl { fill: var(--ink); font: 13px system-ui, sans-serif; } svg .mut { fill: var(--muted); font: 12px system-ui, sans-serif; }
  svg .val { fill: var(--ink); font: 600 12px system-ui, sans-serif; } svg .bar { fill: #eb6834; } svg .one { stroke: var(--muted); stroke-dasharray: 3 3; }
  pre.code { font-size: 0.8em; overflow-x: auto; }
  pre.md { white-space: pre-wrap; font-size: 0.85em; max-height: 32em; overflow: auto; }
  button.copy-md { font: inherit; padding: 4px 12px; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
"""
body = open(os.path.join(HERE, "body.html"), encoding="utf-8").read()
for k, v in FIGS.items(): body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{(\w+)\}\}", body)
assert not left, left
TITLE = "hazel-jit’s PR, Described"
DESC = ("A working draft of the description for hazelgrove/hazel#2859, hazel-jit for dev, to iterate on before it goes on GitHub: "
        "an executive summary for whoever decides, an engineering summary for whoever reviews, then the details. "
        f"Every evaluator test also runs compiled where it compiles: {SWEEP['compiled']} of {SWEEP['checks']} do, and none differs from the interpreter. "
        "Beside ReScript, Melange and js_of_ocaml, hazel-jit now lays out records as they do, as plain objects. "
        f"Four ways on the games of hazeljs-examples: hazel-jit now runs their rules {FIGS['fw_ij']} times as fast as the interpreter and {FIGS['fw_cj']} times as fast as on 2026-11-19, and takes {FIGS['fw_jp']} times the time of the same game written by hand in JavaScript, where it took {FIGS['fw_cp']} times. "
        "With the day's changes merged: tail calls as loops, a named function's tuple parts as JS arguments, constructors without arguments made once, a module's members by name; and where conversion at the edges still costs, and how to bring it down.")
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{esc(DESC)}\">\n<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(head + body)

# the series card's thumbnail: the description's two summaries, and the sweep
def thumb(mode):
    base = (".h{fill:#1f2328;font:700 15px system-ui,sans-serif}.m{fill:#5b6470;font:11px system-ui,sans-serif}.k{fill:#1f2328;font:700 12px system-ui,sans-serif}"
            ".b{fill:none;stroke:#2a78d6;stroke-width:2}.g{fill:#2e9e5b}.c{fill:#1f2328;font:12px ui-monospace,monospace}")
    dark = ".h{fill:#e8e6e3}.m{fill:#a2a9b3}.k{fill:#e8e6e3}.c{fill:#e8e6e3}.b{stroke:#5a9be6}"
    style = base + ("\n" + dark if mode == "dark" else "\n@media (prefers-color-scheme: dark) {" + dark + "}" if mode == "auto" else "")
    frac = SWEEP["agreed"] / SWEEP["checks"]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" width="320" height="200">\n<style>{style}\n</style>\n'
            '<text class="h" x="16" y="26">hazel-jit for dev, described</text>\n'
            '<line class="b" x1="16" y1="42" x2="16" y2="112"/>'
            '<text class="k" x="26" y="54">Executive summary</text><text class="m" x="26" y="70">what, why, what it changes, who uses it</text>'
            '<text class="k" x="26" y="92">Engineering summary</text><text class="m" x="26" y="108">in and out, values, what the interpreter keeps</text>\n'
            '<text class="c" x="16" y="136">{x: 1}  {$h, $t}  {$c, $v}</text>\n'
            f'<rect x="16" y="152" width="288" height="12" fill="none" stroke="#8b939d"/><rect class="g" x="16" y="152" width="{288 * frac:.1f}" height="12"/>'
            f'<text class="m" x="16" y="184">{SWEEP["compiled"]} of {SWEEP["checks"]} evaluator checks compile; none differs</text>\n</svg>\n')
os.makedirs(os.path.join(HERE, "img"), exist_ok=True)
for name, mode in [("thumb-light.svg", "light"), ("thumb-dark.svg", "dark"), ("thumb.svg", "auto")]:
    open(os.path.join(HERE, "img", name), "w").write(thumb(mode))
meta = {"title": TITLE, "blurb": DESC,
        "source": "065/pr-2859.md: the description for hazelgrove/hazel#2859, in GitHub's Markdown; the page renders it and carries it to copy",
        "builds": {"hazel-jit": "hazelgrove/hazel hazel-jit at 9ec865976d (#2859), on dev at 21da4ae66b",
                   "sweep": f"hazelgrove/hazel CI run {SWEEP['run']}, job {SWEEP['job']} (Fast checks), the sweep's summary line",
                   "package": "hazeljs 0.0.13 (hazelgrove/hazeljs editor-in-package 3a4a1cd, built from hazelgrove/hazel 20febee548), Node 22, one laptop: Gnome dig's step",
                   "games": "report 063 (GitHub run 45247119864, hazeljs 0.0.11) and report 054 (GitHub run 45532448010, trial/847-records-objects f311f4e408)",
                   "others": "report 046 (2026-11-07): ReScript 12.3.1, Melange 5.0.0, js_of_ocaml 5.9.1, hazel-jit of that day, Node 22.23.2, one laptop"},
        "ticket_853": {"what": "2026-11-25: hazel-jit with self tail calls as loops and named functions' tuple parts as JS arguments (trial/853-jit-loops-args 50b70d5a40 and 43828037c9), against the base (hazel-jit as on #2859, 9ec865976d, in hazeljs 0.0.13)",
                       "games": "matthewhammer/hazeljs-examples bench/853, GitHub run 45640411958: each game's own run of states (node/package-bench.mjs --runs --aot-as-is --no-interp), one runner a game, the base, the trial (hazelgrove/hazel trial/853-pkg 6d041e9769, hazeljs with the trial merged), the base again; usPerCall: microseconds a call, the run's calls summed over their number; every answer the same as the games' own compiled.js",
                       "petri": "065/drivers/petri/petri-bench.mjs on this laptop, one way per process, five rounds (data/petri-runs.jsonl)"},
        "ticket_853_split": "matthewhammer/hazeljs-examples bench/853-split, GitHub run 45641693384: the base, loops alone (hazelgrove/hazel trial/853-pkg-loops, db27761a79: hazeljs with 50b70d5a40 merged), both (trial/853-pkg, 6d041e9769), one after another on one runner a game; and the Petri rule on the laptop the same three ways, five rounds (data/petri-split-runs.jsonl)",
        "ticket_853_more": "matthewhammer/hazeljs-examples bench/853-more, GitHub run 45645748545: six builds one after another on one runner a game: the base (hazelgrove/hazel trial/853-pkg 6d041e9769, loops and JS arguments, as merged), c1 (trial/853-pkg-c1 a14e698ec8: constructors without arguments made once), c2 (trial/853-pkg-c2 bc9d98db6b: a module's members by name), c3 (trial/853-pkg-c3 f111bb00ac: == against a literal as ===), noint (b471f761fb: c3 with Ints as plain JS numbers, a bench build only) and nostep (ae9611d03f: c3 with no step counted, a bench build only); and the Petri rule on the laptop the same six ways, five rounds (data/petri-more-runs.jsonl)",
        "crossing": "#crossing: data/crossing-timeline.json (the jit against the games' own compiled.js, build by build, from reports 063 and 054 and today's runs); data/petri-crossing-runs.jsonl (the Petri rule direct into compiled code, petri-bench.mjs hazel, and through Hazel.jitProgram as a page calls it, petri-bench.mjs jit; hazeljs 0.0.13 and trial/853-pkg-c3; five rounds on the laptop)",
        "options_bench": "data/petri-opt-runs.jsonl: the Petri rule on the laptop, seven rounds, trial/853-pkg-c3 (f111bb00ac) against trial/853-pkg-opt (bee76969b5, a bench build only: options unboxed in compiled code)",
        "fourway": "matthewhammer/hazeljs-examples bench/4way, GitHub run 45650465391: each game's own run of states (node/package-bench.mjs --runs --aot-as-is, the interpreter included), one runner a game, with the library of hazelgrove/hazel hazeljs at 2c4a61560f: interpreted (Hazel.runProgram), jit (Hazel.jitProgram: hazel-jit now), compiled (each game's own compiled.js, compiled ahead of time by hazel-jit on trial/794-games-aot between 11-20 and 11-23, whose compiler, HazelJit.re, last changed on 11-17 and its value boundary on 11-18: hazel-jit as of Thursday 11-19), and plain JS (<game>/plain.js, five games); every answer the same",
        "files": ["pr-2859.md", "data/games-4way/", "img/gnome-world.jpg", "data/petri-opt-runs.jsonl", "data/crossing-timeline.json", "data/petri-crossing-runs.jsonl", "data/games-853-more/", "data/petri-more-runs.jsonl", "data/sweep.json", "data/representations.json", "data/petri-046.json", "data/petri-853.json", "data/petri-runs.jsonl", "data/petri-split-runs.jsonl", "data/games-853/", "data/games-853-split/", "drivers/petri/"]}
json.dump(meta, open(os.path.join(DATA, "meta.json"), "w"), indent=1, ensure_ascii=False)
print("wrote 065/index.html;", updated)
