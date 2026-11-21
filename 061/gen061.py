#!/usr/bin/env python3
"""^report(61): Does Hazel Repeat Itself? Checkers, Six Moves Ahead. Matthew Hammer, 2026-11-21 (^ticket(811)): "For checkers (to start,
but also Go eventually): if we use a deep, 6-move-ahead strategy and play the entire game with two AIs, how much computation is being
repeated across those two AIs, across all of their 'moves'". Hypothesis: "Many, many 'sub worlds' are shared between players and
across the game's progression ... AI's that share their strategy search state could explore this emergent space faster than those
that try to remain private to each other".

Writes 061/index.html from body.html and data/count.json, data/share.json (hazeljs-examples' tools/checkers-lab.mjs: count and share,
3 games of self-play, depth 6, on the laptop)."""
import html, json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
C = json.load(open(os.path.join(HERE, "data", "count.json")))
S = json.load(open(os.path.join(HERE, "data", "share.json")))
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
esc = lambda s: html.escape(str(s), quote=True)
pct = lambda a, b: f"{100 * a / b:.0f}%" if b else "—"
pct1 = lambda a, b: f"{100 * a / b:.1f}%" if b else "—"
num = lambda n: f"{n:,}"

ALL = C["all"]; FIRST = C["distinct"]; IN_MOVE = C["inMove"]; OWN = C["ownBefore"]; OTHER = C["otherOnly"]
REP = IN_MOVE + OWN + OTHER
ROWS = {r["name"]: r for r in S["rows"]}
NONE, MOVE, PLAYER, SHARED = ROWS["none (Hazel now)"], ROWS["each move"], ROWS["each player"], ROWS["shared"]
PD, SD = ROWS["each player, deeper answers"], ROWS["shared, deeper answers"]

EXTRA = """
  figure.chart svg { width: 100%; height: auto; display: block; }
  svg .lbl { fill: var(--ink); font: 13px system-ui, sans-serif; } svg .mut { fill: var(--muted); font: 12px system-ui, sans-serif; }
  svg .seg1 { fill: #9aa3ad; } svg .seg2 { fill: #2a78d6; } svg .seg3 { fill: #1baf7a; } svg .seg4 { fill: #eb6834; }
  svg .blk { fill: #1f2328; stroke: #9aa3ad; stroke-width: 1.5; } svg .wht { fill: #f6f0e2; stroke: #8a7a5a; } svg .edge { stroke: var(--line); fill: none; }
  svg .hi { fill: none; stroke: #eb6834; stroke-width: 3; stroke-dasharray: 5 4; }
  .tw { overflow-x: auto; margin: 0.6em 0 1em; } .tw table { min-width: 640px; }
  table.nums td, table.nums th { text-align: right; font-variant-numeric: tabular-nums; } table.nums td:first-child, table.nums th:first-child { text-align: left; }
  .cards3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 0.8em 0 1.2em; }
  .cards3 .card { border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; background: var(--paper); }
  .cards3 .big { font-size: 1.9em; font-weight: 700; line-height: 1.1; font-variant-numeric: tabular-nums; } .cards3 .what { color: var(--muted); font-size: 0.88em; }
"""

def card(big, what): return f'<div class="card"><div class="big">{big}</div><div class="what">{esc(what)}</div></div>'

# ---- figure 1: every position looked at, by whether it was looked at before (with as far to look), and where
def where_bar():
    W, x0, w = 600, 10, 580
    segs = [("first time", FIRST, "seg1"), ("again, in the same move's search", IN_MOVE, "seg2"),
            ("again, in the same player's earlier moves", OWN, "seg3"), ("again, only in the other player's", OTHER, "seg4")]
    out, x = [f'<text class="lbl" x="{x0}" y="18">{num(ALL)} positions looked at</text>'], x0
    for name, n, cls in segs:
        bw = w * n / ALL
        if bw > 0: out.append(f'<rect class="{cls}" x="{x:.1f}" y="28" width="{bw:.1f}" height="34"><title>{esc(name)}: {num(n)} ({pct1(n, ALL)})</title></rect>')
        x += bw
    for i, (name, n, cls) in enumerate(segs):
        cy = 90 + i * 22
        out.append(f'<rect class="{cls}" x="{x0}" y="{cy - 11}" width="12" height="12"/><text class="mut" x="{x0 + 18}" y="{cy}">{esc(name)}: {pct1(n, ALL)}</text>')
    return f'<svg viewBox="0 0 {W} 166" role="img" aria-label="Where the positions looked at come from">' + "".join(out) + "</svg>"

# ---- figure 2: why the two players never meet: whose turn at each depth, in black's search and in white's
def parity():
    W = 560
    def col(x, title, first):
        out = [f'<text class="lbl" x="{x}" y="22">{esc(title)}</text>']
        for d in range(6, -1, -1):
            y = 44 + (6 - d) * 30; who = first if (6 - d) % 2 == 0 else ("white" if first == "black" else "black")
            hi = who == "black"
            out.append(f'<circle class="{"blk" if who == "black" else "wht"}" cx="{x + 12}" cy="{y}" r="9"/>' +
                       f'<text class="mut" x="{x + 30}" y="{y + 4}">{who} to move, {d} still to look</text>' +
                       (f'<rect class="hi" x="{x - 2}" y="{y - 13}" width="250" height="26" rx="6"/>' if hi else ""))
        return "".join(out)
    return (f'<svg viewBox="0 0 {W} 250" role="img" aria-label="In black\'s searches black is to move with 6, 4, 2 or 0 still to look; in white\'s, with 5, 3 or 1">'
            + col(10, "black's search (its move)", "black") + col(295, "white's search (the next move)", "white") + "</svg>")

# ---- figure 3: what each table saves: positions searched past the edge and valued at it, per move, and the time a move takes
def tables_fig():
    rows = [("none (Hazel now)", NONE), ("a table each move", MOVE), ("each player's, kept", PLAYER), ("one table, shared", SHARED),
            ("each player's, deeper answers", PD), ("shared, deeper answers", SD)]
    W, x0, w, mx = 600, 200, 330, NONE["msPerMove"]
    out = []
    for i, (name, r) in enumerate(rows):
        y = 18 + i * 34; bw = w * r["msPerMove"] / mx
        out.append(f'<text class="lbl" x="10" y="{y + 15}">{esc(name)}</text><rect class="{"seg1" if i == 0 else "seg2" if i < 4 else "seg4"}" x="{x0}" y="{y}" width="{bw:.1f}" height="22"><title>{r["msPerMove"]:.1f} ms a move</title></rect>' +
                   f'<text class="mut" x="{x0 + bw + 6:.1f}" y="{y + 15}">{r["msPerMove"]:.1f} ms</text>')
    return f'<svg viewBox="0 0 {W} {18 + len(rows) * 34}" role="img" aria-label="Time a move takes, with each kind of table">' + "".join(out) + "</svg>"

def depth_table():
    rows = "".join(f'<tr><td>{d}</td><td>{num(v["all"])}</td><td>{pct(v["repeat"], v["all"])}</td></tr>' for d, v in sorted(C["byDepth"].items(), key=lambda kv: -int(kv[0])))
    return f'<table class="nums"><thead><tr><th>moves still to look</th><th>looked at</th><th>looked at before</th></tr></thead><tbody>{rows}</tbody></table>'

def share_table():
    rows = [("none (Hazel now)", NONE), ("a table each move, cleared after it", MOVE), ("each player's own, kept move to move", PLAYER), ("one table both players share", SHARED),
            ("each player's own, deeper answers allowed", PD), ("one shared, deeper answers allowed", SD)]
    body = "".join(f'<tr><td>{esc(n)}</td><td>{num(r["interior"])}</td><td>{num(r["leaves"])}</td><td>{num(r["hits"])}</td><td>{r["msPerMove"]:.1f}</td><td>{r["differ"]} of {r["moves"]}</td><td>{num(r["size"])}</td></tr>' for n, r in rows)
    return ('<div class="tw"><table class="nums"><thead><tr><th>table</th><th>searched past the edge</th><th>valued at the edge</th><th>table answers</th><th>ms a move</th><th>moves chosen differently</th><th>table size, most</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')

games = C["perGame"]; moves = sum(g["moves"] for g in games)
FIGS = {
    "updated": updated, "where": where_bar(), "parity": parity(), "tables": tables_fig(), "depth_table": depth_table(), "share_table": share_table(),
    "cards": '<div class="cards3">' + card(pct(REP, ALL), "of the positions searched had been searched before, with as far to look") +
             card("0", "of them only in the other player's search: the two never meet at the same look-ahead") +
             card(f"{100 * (1 - PLAYER['msPerMove'] / NONE['msPerMove']):.0f}% less", "time a move, with a table of its own kept by each player; a shared one saves nothing more") + "</div>",
    "all": num(ALL), "games": str(C["games"]), "moves": str(moves), "rep": pct(REP, ALL), "in_move": pct(IN_MOVE, ALL), "own": pct1(OWN, ALL), "other": pct1(OTHER, ALL),
    "p_other": pct1(C["pOther"], ALL), "p_own": pct1(C["pOwn"], ALL), "p_in": pct(C["pInMove"], ALL), "p_rep": pct(C["pInMove"] + C["pOwn"] + C["pOther"], ALL),
    "distinct": num(FIRST), "distinct_pos": num(C["distinctPos"]), "leaves": num(C["leaves"]), "leaves_pct": pct(C["leaves"], ALL),
    "none_ms": f'{NONE["msPerMove"]:.1f}', "move_ms": f'{MOVE["msPerMove"]:.1f}', "player_ms": f'{PLAYER["msPerMove"]:.1f}', "shared_ms": f'{SHARED["msPerMove"]:.1f}',
    "move_cut": pct(NONE["msPerMove"] - MOVE["msPerMove"], NONE["msPerMove"]), "player_cut": pct(NONE["msPerMove"] - PLAYER["msPerMove"], NONE["msPerMove"]),
    "pd_differ": str(PD["differ"]), "sd_differ": str(SD["differ"]), "pd_ms": f'{PD["msPerMove"]:.1f}', "sd_ms": f'{SD["msPerMove"]:.1f}',
    "player_size": num(PLAYER["size"]), "shared_size": num(SHARED["size"]),
    # (Matthew 2026-11-21: "the 69% as the top level number ---- is that predicting that a memo table will save 69% of AI search
    # calls?" No: what repeats, not what a table saves. What it saves, and why less: the edge's repeats it cannot answer for, and
    # the bounds alpha-beta leaves that do not settle a later question)
    "calls_none": num(NONE["interior"] + NONE["leaves"]), "calls_player": num(PLAYER["interior"] + PLAYER["leaves"]),
    "calls_cut": pct(NONE["interior"] + NONE["leaves"] - PLAYER["interior"] - PLAYER["leaves"], NONE["interior"] + NONE["leaves"]),
    "repeats": num(REP), "repeats_gone": pct(NONE["interior"] + NONE["leaves"] - PLAYER["interior"] - PLAYER["leaves"], REP),
    "edge_left": num(PLAYER["leaves"] - (C["leaves"] - C["leafRepeat"])),
    "inner_left": f'{round((PLAYER["interior"] - (FIRST - (C["leaves"] - C["leafRepeat"]))) / 1000):,},000',
    "player_hits": num(PLAYER["hits"]),
    "g1": str(games[0]["moves"]), "g2": str(games[1]["moves"]), "g3": str(games[2]["moves"]),
}
body = open(os.path.join(HERE, "body.html")).read()
for k, v in FIGS.items(): body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{(\w+)\}\}", body)
assert not left, left
TITLE = "Does Hazel Repeat Itself? Checkers, Six Moves Ahead"
DESC = ("Hazel playing Checkers against itself, looking six moves ahead: two thirds of what it searches it has searched before, nearly all "
        "within the same move's search, never at the same look-ahead in the other player's. A memo table each would save a third of its time; "
        "sharing one between the players saves nothing more.")
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{esc(DESC)}\">\n<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
# the series card's thumbnail (light, dark, and one that follows the reader's scheme): the bar of figure 1, and the two numbers
def thumb(mode):
    base = ".h{fill:#1f2328;font:700 15px system-ui,sans-serif}.m{fill:#5b6470;font:10px system-ui,sans-serif}.k{fill:#1f2328;font:700 22px system-ui,sans-serif}.c0{fill:#9aa3ad}.c1{fill:#2a78d6}.c2{fill:#1baf7a}.c3{fill:#eb6834}"
    dark = ".h{fill:#e8e6e3}.m{fill:#a2a9b3}.k{fill:#e8e6e3}.c0{fill:#6b737d}.c1{fill:#3987e5}.c2{fill:#199e70}.c3{fill:#d95926}"
    style = base + ("\n" + dark if mode == "dark" else "\n@media (prefers-color-scheme: dark) {" + dark + "}" if mode == "auto" else "")
    x, w, out = 16, 288, []
    for n, c in [(FIRST, "c0"), (IN_MOVE, "c1"), (OWN, "c2"), (OTHER, "c3")]:
        bw = w * n / ALL
        if bw > 0: out.append(f'<rect class="{c}" x="{x:.1f}" y="58" width="{bw:.1f}" height="26"/>')
        x += bw
    legend = [("c0", "first time"), ("c1", "same move"), ("c2", "own earlier moves"), ("c3", "other player")]
    for i, (c, t) in enumerate(legend):
        xx, yy = 16 + 150 * (i % 2), 100 + 15 * (i // 2)
        out.append(f'<rect class="{c}" x="{xx}" y="{yy - 8}" width="8" height="8" rx="1"/><text class="m" x="{xx + 11}" y="{yy}">{t}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" width="320" height="200">\n<style>{style}\n</style>\n'
            f'<text class="h" x="16" y="26">Does Hazel repeat itself?</text>\n<text class="m" x="16" y="44">Checkers, six moves ahead: {num(ALL)} positions searched</text>\n'
            + "".join(out) +
            f'\n<text class="k" x="16" y="160">{pct(REP, ALL)}</text><text class="m" x="16" y="176">searched before</text>'
            f'<text class="k" x="112" y="160">{pct1(OTHER, ALL)}</text><text class="m" x="112" y="176">in the other player\'s</text>'
            f'<text class="k" x="222" y="160">\u2212{100 - PLAYER["msPerMove"] / NONE["msPerMove"] * 100:.0f}%</text><text class="m" x="222" y="176">time, a table each</text>\n</svg>\n')
os.makedirs(os.path.join(HERE, "img"), exist_ok=True)
for name, mode in [("thumb-light.svg", "light"), ("thumb-dark.svg", "dark"), ("thumb.svg", "auto")]: open(os.path.join(HERE, "img", name), "w").write(thumb(mode))
json.dump({"blurb": DESC, "title": TITLE}, open(os.path.join(HERE, "data", "meta.json"), "w"), indent=1)
print("wrote 061/index.html;", updated, {"rep": pct(REP, ALL), "other": OTHER, "player_ms": PLAYER["msPerMove"]})
