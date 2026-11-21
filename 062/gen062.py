#!/usr/bin/env python3
"""^report(62): One Search Tree for Two Players. Matthew Hammer, 2026-11-21, after ^report(61): "is there a way to make a 'canonical
search space' that's not POV, so that each person's view of it matches each other persons?", "we want a memo policy that does not
match exactly, but instead uses a partial ordering", "a way of asking for a shallow depth, getting a full match, and then separately
asking for a deeper match that reuses that entire shallow match, without redoing it", "we need a way to treat the matches as
streams, whose heads can be reused ... tree-streams". "Yes, prototype it."

Writes 062/index.html from body.html and data/tree.json, data/tree-65.json (hazeljs-examples' tools/checkers-lab.mjs tree, 3 games,
6 ahead, on the laptop)."""
import html, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from design_fig import design_svg

s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
T = json.load(open(os.path.join(HERE, "data", "tree.json")))
T65 = json.load(open(os.path.join(HERE, "data", "tree-65.json")))
ROWS = T["rows"] + [r for r in T65["rows"] if r["how"] == "player"]
R = {(r["policy"], r["how"]): r for r in ROWS}
MOVES = T["moves"]
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
esc = lambda s: html.escape(str(s), quote=True)
num = lambda n: f"{round(n):,}"
pct = lambda a, b: f"{100 * a / b:.0f}%"

def side(r, who): return r["by"][str(who)]
def ms(r, who=None): return (side(r, 1)["ms"] + side(r, 2)["ms"]) / MOVES if who is None else side(r, who)["ms"] / side(r, who)["moves"]
def looked(r, who=None):
    if who is None: return sum(side(r, w)["interior"] + side(r, w)["leaves"] for w in (1, 2)) / MOVES
    S = side(r, who); return (S["interior"] + S["leaves"]) / S["moves"]
def worked(r, who=None):
    if who is None: return sum(side(r, w)["expanded"] for w in (1, 2)) / MOVES
    S = side(r, who); return S["expanded"] / S["moves"]
def answered(r): return sum(side(r, w)["hits"] for w in (1, 2)) / MOVES

NOW, E66, S66, TR66 = R["6/6", "plain"], R["6/6", "player"], R["6/6", "shared"], R["6/6", "tree"]
P67, E67, S67, TR67, TRO67, TRD67, TRP67 = (R["6/7", h] for h in ("plain", "player", "shared", "tree", "tree-hazel-order", "tree-deepen", "tree-deep"))
P65, E65, S65, TR65 = (R["6/5", h] for h in ("plain", "player", "shared", "tree"))
LABEL = {"plain": "no table", "player": "a table each", "shared": "one table, shared", "tree": "the shared tree",
         "tree-hazel-order": "the shared tree, the rules' order", "tree-deepen": "the shared tree, deepening", "tree-deep": "the shared tree, further answers"}
POL = {"6/6": "6 and 6", "6/7": "6 and 7", "6/5": "6 and 5"}
label = lambda r: ("Hazel now: " if r is NOW else "") + POL[r["policy"]] + ", " + LABEL[r["how"]]

EXTRA = """
  figure.chart svg { width: 100%; height: auto; display: block; }
  svg .lbl { fill: var(--ink); font: 13px system-ui, sans-serif; } svg .mut { fill: var(--muted); font: 12px system-ui, sans-serif; }
  svg .blk { fill: #1f2328; } svg .wht { fill: #f6f0e2; stroke: #8a7a5a; } svg .hi { fill: #eb6834; } svg .grid { stroke: var(--line); }
  svg .node { fill: var(--paper); stroke: #2a78d6; stroke-width: 2; } svg .cell { fill: var(--paper); stroke: var(--line); stroke-width: 1.5; }
  svg .cell.later { stroke-dasharray: 5 4; } svg .link { fill: none; stroke: var(--muted); stroke-width: 1.5; }
  svg .barb { fill: #2a78d6; } svg .barw { fill: #9ec5f0; } svg .arrowb { stroke: #1f2328; stroke-width: 3; } svg .arroww { stroke: #b8a57a; stroke-width: 3; }
  svg .finish { stroke: #eb6834; stroke-width: 2; stroke-dasharray: 4 3; }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) svg .blk { fill: #e8e6e3; } :root:not([data-theme="light"]) svg .arrowb { stroke: #e8e6e3; } }
  :root[data-theme="dark"] svg .blk { fill: #e8e6e3; } :root[data-theme="dark"] svg .arrowb { stroke: #e8e6e3; }
  table.nums td, table.nums th { text-align: right; font-variant-numeric: tabular-nums; } table.nums td:first-child, table.nums th:first-child { text-align: left; }
  .tw { overflow-x: auto; margin: 0.6em 0 1em; } .tw table { min-width: 720px; }
  .cards3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 0.8em 0 1.2em; }
  .cards3 .card { border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; background: var(--paper); }
  .cards3 .big { font-size: 1.9em; font-weight: 700; line-height: 1.1; font-variant-numeric: tabular-nums; } .cards3 .what { color: var(--muted); font-size: 0.88em; }
"""

def card(big, what): return f'<div class="card"><div class="big">{big}</div><div class="what">{esc(what)}</div></div>'

# ---- figure: whose searches end on the same move, under each way of setting how far each player looks
def pairs_svg():
    W, x0, sx = 600, 150, 46   # (move 10 at x0, a move every sx)
    X = lambda ply: x0 + (ply - 10) * sx
    out = [f'<text class="mut" x="{X(p)}" y="16" text-anchor="middle">{p}</text>' for p in range(10, 20)]
    out += [f'<line class="grid" x1="{X(p)}" y1="22" x2="{X(p)}" y2="300"/>' for p in range(10, 20)]
    rows = [("Hazel now", "6 and 6", {1: 6, 2: 6}), ("lined up", "6 and 7", {1: 6, 2: 7}), ("lined up", "6 and 5", {1: 6, 2: 5})]
    for i, (what, name, look) in enumerate(rows):
        y0 = 40 + i * 92
        out.append(f'<text class="lbl" x="8" y="{y0 + 22}">{esc(name)}</text><text class="mut" x="8" y="{y0 + 40}">{esc(what)}</text>')
        ends = {}
        for j, ply in enumerate((10, 11, 12)):
            who = 1 if ply % 2 == 0 else 2; end = ply + look[who]; y = y0 + 10 + j * 22
            ends.setdefault(end, []).append(y)
            out.append(f'<line class="{"arrowb" if who == 1 else "arroww"}" x1="{X(ply)}" y1="{y}" x2="{X(end)}" y2="{y}"/>' +
                       f'<circle class="{"blk" if who == 1 else "wht"}" cx="{X(ply)}" cy="{y}" r="6"/><circle class="hi" cx="{X(end)}" cy="{y}" r="3.5"/>')
        for end, ys in ends.items():
            if len(ys) > 1: out.append(f'<line class="finish" x1="{X(end) + 8}" y1="{min(ys) - 8}" x2="{X(end) + 8}" y2="{max(ys) + 8}"/>' +
                                       f'<text class="mut" x="{X(end) + 13}" y="{(min(ys) + max(ys)) / 2 + 4}">same finish</text>')
    out.append(f'<text class="mut" x="8" y="318">the move each search starts at (● black, ○ white), and the move it looks ahead to</text>')
    return f'<svg viewBox="0 0 {W} 326" role="img" aria-label="Which searches end on the same move: none in Hazel now; pairs when White looks one move more or less">' + "".join(out) + "</svg>"

# ---- figure: the time a move takes, black's and white's, each way
CHART = [NOW, E66, S66, TR66, E67, S67, TR67, E65, S65, TR65]
def ways_svg():
    W, x0, w = 600, 230, 300
    mx = max(max(ms(r, 1), ms(r, 2)) for r in CHART)
    out = []
    for i, r in enumerate(CHART):
        y = 14 + i * 40
        out.append(f'<text class="lbl" x="8" y="{y + 18}">{esc(label(r).replace("Hazel now: ", "now: "))}</text>')
        for k, who in enumerate((1, 2)):
            v = ms(r, who); bw = w * v / mx; yy = y + k * 15
            out.append(f'<rect class="{"barb" if who == 1 else "barw"}" x="{x0}" y="{yy}" width="{bw:.1f}" height="13"><title>{"black" if who == 1 else "white"}: {v:.1f} ms a move</title></rect>' +
                       f'<text class="mut" x="{x0 + bw + 5:.1f}" y="{yy + 11}">{v:.1f}</text>')
    h = 14 + len(CHART) * 40
    out.append(f'<rect class="barb" x="{x0}" y="{h}" width="12" height="10"/><text class="mut" x="{x0 + 16}" y="{h + 9}">black\'s moves</text>' +
               f'<rect class="barw" x="{x0 + 120}" y="{h}" width="12" height="10"/><text class="mut" x="{x0 + 136}" y="{h + 9}">white\'s moves, ms a move</text>')
    return f'<svg viewBox="0 0 {W} {h + 20}" role="img" aria-label="Milliseconds a move, black\'s and white\'s, each way">' + "".join(out) + "</svg>"

def all_table():
    body = "".join(f'<tr><td>{esc(label(r))}</td><td>{ms(r):.1f}</td><td>{ms(r, 1):.1f}</td><td>{ms(r, 2):.1f}</td><td>{num(looked(r))}</td><td>{num(worked(r))}</td>'
                   f'<td>{num(answered(r))}</td><td>{r["differ"]}</td><td>{num(r["kept"])}</td><td>{r["heapMB"]}</td></tr>' for r in ROWS)
    return ('<div class="tw"><table class="nums"><thead><tr><th>way</th><th>ms a move</th><th>black’s</th><th>white’s</th><th>positions looked at, a move</th>'
            '<th>moves worked out, a move</th><th>answered by the memo, a move</th><th>moves chosen differently</th><th>boards or entries kept, most</th><th>memory, MB</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')

f1 = lambda v: f"{v:.1f}"
FIGS = {
    "updated": updated, "moves": str(MOVES), "games": str(T["games"]),
    "design": design_svg(), "pairs": pairs_svg(), "ways": ways_svg(), "all_table": all_table(),
    "cards": '<div class="cards3">' +
             card("about half", "the work of the search that comes second in each pair, when the two players' searches end on the same move and share one table") +
             card(f"{pct(ms(NOW) - ms(S65), ms(NOW))} less", "time a move, black looking 6 ahead and white 5, sharing a table, against Hazel now (white sees one move less)") +
             card(f"{pct(worked(E66) - worked(TR66), worked(E66))} fewer", "moves worked out when the tree is kept, but no faster in JavaScript, and three to four times the memory") + "</div>",
    "now_ms": f1(ms(NOW)), "now_b": f1(ms(NOW, 1)), "now_w": f1(ms(NOW, 2)), "e66_ms": f1(ms(E66)), "s66_ms": f1(ms(S66)), "tr66_ms": f1(ms(TR66)),
    "e66_worked": num(worked(E66)), "tr66_worked": num(worked(TR66)), "tr66_worked_cut": pct(worked(E66) - worked(TR66), worked(E66)),
    "e66_looked": num(looked(E66)), "tr66_looked": num(looked(TR66)), "tr66_looked_cut": pct(looked(E66) - looked(TR66), looked(E66)),
    "e66_heap": str(E66["heapMB"]), "tr66_heap": str(TR66["heapMB"]), "tr67_heap": str(TR67["heapMB"]), "e67_heap": str(E67["heapMB"]),
    "b67_own_looked": num(looked(E67, 1)), "b67_sh_looked": num(looked(S67, 1)), "b67_own_ms": f1(ms(E67, 1)), "b67_sh_ms": f1(ms(S67, 1)),
    "b67_cut": pct(looked(E67, 1) - looked(S67, 1), looked(E67, 1)),
    "w65_own_looked": num(looked(E65, 2)), "w65_sh_looked": num(looked(S65, 2)), "w65_own_ms": f1(ms(E65, 2)), "w65_sh_ms": f1(ms(S65, 2)),
    "w65_cut": pct(looked(E65, 2) - looked(S65, 2), looked(E65, 2)),
    "p67_w": f1(ms(P67, 2)), "s67_ms": f1(ms(S67)), "s67_w": f1(ms(S67, 2)), "e67_ms": f1(ms(E67)), "s65_ms": f1(ms(S65)), "e65_ms": f1(ms(E65)),
    "s65_vs_now": pct(ms(NOW) - ms(S65), ms(NOW)), "s65_vs_e66": pct(ms(E66) - ms(S65), ms(E66)), "p65_ms": f1(ms(P65)),
    "tr67_ms": f1(ms(TR67)), "tro67_ms": f1(ms(TRO67)), "trd67_ms": f1(ms(TRD67)), "trp67_ms": f1(ms(TRP67)), "trp67_differ": str(TRP67["differ"]),
    "tro67_w_looked": num(looked(TRO67, 2)), "tr67_w_looked": num(looked(TR67, 2)), "tr67_order_cut": pct(looked(TRO67, 2) - looked(TR67, 2), looked(TRO67, 2)),
    "trd67_w_looked": num(looked(TRD67, 2)), "trd67_worked": num(worked(TRD67, 2)), "tr67_worked": num(worked(TR67, 2)),
    "trp67_cut": pct(ms(TR67) - ms(TRP67), ms(TR67)),
}
body = open(os.path.join(HERE, "body.html")).read()
for k, v in FIGS.items(): body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{(\w+)\}\}", body)
assert not left, left
TITLE = "One Search Tree for Two Players"
DESC = (f"A prototype of Matthew's tree-streams for Hazel's Checkers search: one tree of boards both players grow, answers kept as ranges "
        f"and found by a partial order. When the two players' searches end on the same move, the one that comes second does about half the "
        f"work; lining them up costs one player a move of look-ahead, and black 6 with white 5 runs {pct(ms(NOW) - ms(S65), ms(NOW))} faster than Hazel now. "
        f"Keeping the tree itself halves the moves worked out but saves no time in JavaScript, and deepening a step at a time saves nothing here.")
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{esc(DESC)}\">\n<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)

# the series card's thumbnail: the second search's work, own table against one shared, both ways round
def thumb(mode):
    base = ".h{fill:#1f2328;font:700 15px system-ui,sans-serif}.m{fill:#5b6470;font:10px system-ui,sans-serif}.k{fill:#1f2328;font:700 20px system-ui,sans-serif}.c1{fill:#9aa3ad}.c2{fill:#2a78d6}"
    dark = ".h{fill:#e8e6e3}.m{fill:#a2a9b3}.k{fill:#e8e6e3}.c1{fill:#6b737d}.c2{fill:#3987e5}"
    style = base + ("\n" + dark if mode == "dark" else "\n@media (prefers-color-scheme: dark) {" + dark + "}" if mode == "auto" else "")
    mx = max(looked(E67, 1), looked(E65, 2))
    bar = lambda y, v, c: f'<rect class="{c}" x="120" y="{y}" width="{180 * v / mx:.1f}" height="14"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" width="320" height="200">\n<style>{style}\n</style>\n'
            '<text class="h" x="16" y="26">One search for two players</text>\n<text class="m" x="16" y="43">the second search of a pair, positions looked at a move</text>\n'
            f'<text class="m" x="16" y="66">black (6 and 7)</text>{bar(55, looked(E67, 1), "c1")}{bar(72, looked(S67, 1), "c2")}'
            f'<text class="m" x="16" y="112">white (6 and 5)</text>{bar(101, looked(E65, 2), "c1")}{bar(118, looked(S65, 2), "c2")}'
            '<rect class="c1" x="16" y="146" width="8" height="8"/><text class="m" x="28" y="154">its own table</text>'
            '<rect class="c2" x="110" y="146" width="8" height="8"/><text class="m" x="122" y="154">one table, shared</text>'
            f'<text class="k" x="16" y="186">about half</text><text class="m" x="130" y="186">of the work, shared</text>\n</svg>\n')
os.makedirs(os.path.join(HERE, "img"), exist_ok=True)
for name, mode in [("thumb-light.svg", "light"), ("thumb-dark.svg", "dark"), ("thumb.svg", "auto")]: open(os.path.join(HERE, "img", name), "w").write(thumb(mode))
json.dump({"blurb": DESC, "title": TITLE}, open(os.path.join(HERE, "data", "meta.json"), "w"), indent=1)
print("wrote 062/index.html;", updated)
