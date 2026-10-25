#!/usr/bin/env python3
"""^report(33): writing Messed Up Dress Up's game rules in Hazel: what a rule sees today (Event, Cmd, Globals), why Globals is a
per-rule view, and a proposal: one address for every place, thing and person, and Globals, RuleState and Cmd built on it
(^ticket(609)). Reads data/places.json (the default world and the game's place tables, read from the game in node at
kids-choice-games eee9446). Every figure is drawn here. The appendix lists every address of the default world as text; a click
shows its picture from the dress-up-pictures archive (no copy is kept here).
  python3 033/drivers/gen033.py   (from the repository's root; 033/drivers/build.sh runs it with the series tools)"""
import os, json, html
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLE = open(os.path.join(R, "..", "025", "drivers", "style.css")).read()
P = json.load(open(os.path.join(R, "data", "places.json")))
esc = html.escape

import re
HZ_KW = {"type", "let", "fun", "case", "end", "module", "in", "if", "then", "else", "test", "true", "false"}
def hazel_hl(t):
    out, i = [], 0
    pat = re.compile(r'(#[^#]*#)|("(?:[^"\\]|\\.)*")|(\b[0-9]+(?:\.[0-9]+)?\b)|(\b[A-Za-z_][A-Za-z0-9_]*\b)|(->|=>|::|\+|\||[=:,.()\[\]!<>*/-])', re.M)
    for m in pat.finditer(t):
        out.append(esc(t[i:m.start()])); i = m.end(); g = m.group(0)
        if m.group(1): out.append(f'<span class="hc">{esc(g)}</span>')
        elif m.group(2): out.append(f'<span class="hs">{esc(g)}</span>')
        elif m.group(3): out.append(f'<span class="hn">{esc(g)}</span>')
        elif m.group(4): out.append(f'<span class="{"hk" if g in HZ_KW else "hC" if g[0].isupper() else "hv"}">{esc(g)}</span>')
        else: out.append(f'<span class="ho">{esc(g)}</span>')
    out.append(esc(t[i:])); return "".join(out)
FU_KW = {"module", "let", "return", "import", "type", "public", "force", "func", "thunk", "switch", "case", "prim", "if", "else", "var", "for", "in", "with", "within", "do", "assert", "goto", "space", "time", "debug_show"}
def fumola_hl(t):
    out, i = [], 0
    pat = re.compile(r'(//.*$)|("(?:[^"\\]|\\.)*")|(`[A-Za-z_][A-Za-z0-9_]*)|(#[A-Za-z_][A-Za-z0-9_]*)|(@[A-Za-z_][A-Za-z0-9_]*)|(\b[A-Za-z_][A-Za-z0-9_]*\b)|([0-9]+)', re.M)
    for m in pat.finditer(t):
        out.append(esc(t[i:m.start()])); i = m.end(); g = m.group(0)
        cls = "fc" if m.group(1) else "fs" if m.group(2) else "fy" if m.group(3) else "ft" if m.group(4) else "fy" if m.group(5) else (
              "fk" if g in FU_KW else "fT" if g[0].isupper() else "fv") if m.group(6) else "fv"
        out.append(f'<span class="{cls}">{esc(g)}</span>')
    out.append(esc(t[i:])); return "".join(out)
GAME = "eee9446"
PICS = "https://matthewhammer.org/dress-up-pictures/pictures/"
KCG = "https://github.com/matthewhammer/kids-choice-games/blob/" + GAME + "/dress-up/js/"
def src(f, line, text=None):
    return f'<a class="src" href="{KCG}{f}#L{line}"><code>{esc(text or f"{f}:{line}")}</code></a>'
def code(t): return f"<code>{esc(t)}</code>"

# ---------------------------------------------------------------- the figures
def fig(svg, cap, fid):
    return f'<figure id="{fid}">{svg}<figcaption>{cap}</figcaption></figure>'
FIGCSS = """
svg.fig { width: 100%; height: auto; max-width: 900px; display: block; margin: 0 auto; }
svg.fig text { font: 13px system-ui, sans-serif; fill: var(--ink); }
svg.fig .mono { font: 12.5px ui-monospace, monospace; }
svg.fig .small { font-size: 11px; fill: var(--muted); }
svg.fig .box { fill: var(--paper); stroke: var(--line); stroke-width: 1.5; }
svg.fig .hz { fill: color-mix(in srgb, var(--accent) 14%, var(--paper)); stroke: var(--accent); stroke-width: 1.5; }
svg.fig .game { fill: color-mix(in srgb, var(--warn) 14%, var(--paper)); stroke: var(--warn); stroke-width: 1.5; }
svg.fig .snap { fill: color-mix(in srgb, var(--accent2) 16%, var(--paper)); stroke: var(--accent2); stroke-width: 1.2; }
svg.fig .arrow { stroke: var(--muted); stroke-width: 1.6; fill: none; marker-end: url(#ah); }
svg.fig .ahead { fill: var(--muted); }
svg.fig .on { fill: var(--accent); } svg.fig .off { fill: var(--line); }
svg.fig .kindtxt { font-size: 10.5px; }
figure { margin: 1.6em 0; } figcaption { color: var(--muted); font-size: 0.9em; max-width: 52em; margin: 0.5em auto 0; }
pre.hz, pre.fu { background: #000; color: #f8f8f2; border-radius: 8px; padding: 10px 12px; overflow: auto; font-size: 0.86em; line-height: 1.5; }
pre.wrap { white-space: pre-wrap; overflow-wrap: anywhere; }
pre.hz .hk { color: #5fd7ff; font-weight: 700; } pre.hz .hC { color: #ff87ff; } pre.hz .hv { color: #f8f8f2; } pre.hz .hs { color: #ffb86c; }
pre.hz .hn { color: #bd93f9; } pre.hz .hc { color: #87ff87; font-style: italic; } pre.hz .ho { color: #ffd75f; }
pre.fu .fk { color: #569CD6; } pre.fu .fT { color: #a989d0; } pre.fu .fv { color: #f6ead2; } pre.fu .fs { color: #c87e60; } pre.fu .fc { color: #6A9955; }
pre.fu .fy { color: #d3a8de; font-weight: 600; } pre.fu .ft { color: #e5c07b; }
p.part { font: 700 1.5em system-ui, sans-serif; margin: 2.2em 0 0.1em; padding-top: 0.6em; border-top: 3px solid var(--accent); }
p.part span { color: var(--accent); margin-right: 0.4em; } p.partsub { color: var(--muted); margin: 0 0 1em; font-style: italic; }
nav.outline { border: 1px solid var(--line); border-radius: 10px; padding: 8px 18px; margin: 1em 0; background: var(--paper); }
nav.outline ol.parts > li { margin: 0.35em 0; } nav.outline ol ol { margin: 0.1em 0 0.3em; font-size: 0.93em; } p.intro { font-size: 1.05em; }
code.hzi { background: #000; color: #f8f8f2; padding: 1px 6px; border-radius: 5px; font-size: 0.88em; }
code.hzi .hk { color: #5fd7ff; font-weight: 700; } code.hzi .hC { color: #ff87ff; } code.hzi .hv { color: #f8f8f2; } code.hzi .hs { color: #ffb86c; }
code.hzi .hn { color: #bd93f9; } code.hzi .ho { color: #ffd75f; }
.codecap { color: var(--muted); font-size: 0.85em; margin: 0.6em 0 0.2em; }
a.src code { font-size: 0.85em; }
table.t { border-collapse: collapse; font-size: 0.9em; } table.t td, table.t th { border-bottom: 1px solid var(--line); padding: 4px 8px; text-align: left; vertical-align: top; }
.addr { font: 0.86em ui-monospace, monospace; }
details[data-pic] { border-bottom: 1px solid var(--line); padding: 2px 0; }
details[data-pic] summary { cursor: pointer; list-style: none; display: flex; gap: 10px; align-items: baseline; }
details[data-pic] summary::-webkit-details-marker { display: none; }
details[data-pic] summary .addr { color: var(--accent); }
details[data-pic] summary .what { color: var(--muted); font-size: 0.85em; }
details[data-pic] .pic { margin: 6px 0 14px; } details[data-pic] .pic .main { display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end; }
details[data-pic] .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; }
details[data-pic] .gallery figure.small img { width: 100%; max-height: none; } details[data-pic] .gallery figcaption { font-size: 0.72em; line-height: 1.25; }
button.copylink { margin-left: auto; font-size: 0.75em; padding: 1px 8px; border-radius: 999px; border: 1px solid var(--line); background: var(--paper); color: var(--muted); cursor: pointer; } details[data-pic] .pic figure { margin: 0; } details[data-pic] .pic figcaption { margin: 2px 0 0; font-size: 0.8em; } details[data-pic] .pic img { max-height: 280px; max-width: min(100%, 560px); border: 1px solid var(--line); border-radius: 6px; background: #fff; }
h3.grp { margin-top: 1.2em; }
"""
DEFS = '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="ahead" d="M0 0 L10 5 L0 10 z"/></marker></defs>'

def svg_call():
    # a rule's call, end to end: the game builds the rule's view, Hazel's on_event answers a Cmd, the game acts; the log's three snapshots
    W, H = 900, 250
    b = []
    def box(x, y, w, h, cls, title, lines):
        b.append(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>')
        b.append(f'<text x="{x + 12}" y="{y + 22}" font-weight="700">{esc(title)}</text>')
        for i, l in enumerate(lines): b.append(f'<text class="mono small" x="{x + 12}" y="{y + 42 + 16 * i}">{esc(l)}</text>')
    box(10, 20, 200, 120, "game", "the game (JS)", ["a lever pulled, a door,", "a way off the square", "→ Event", "PullHatch(1)"])
    box(250, 20, 190, 120, "game", "the room's view", ["SCRIPT_ACTS[room].globals()", "16 fields, most at", "defaults; for the tree", "room: hatch only"])
    box(480, 20, 190, 120, "hz", "the rule (Hazel)", ["TreeRoom.on_event", "  : (Globals, Event)", "      -> Cmd", "SetHatch(1, false, Done)"])
    box(710, 20, 180, 120, "game", "the game acts", ["act.SetHatch(n, shut)", "hatchSet(...)", "swings, walks, waits", "then the event ends"])
    for x1, x2 in [(210, 250), (440, 480), (670, 710)]: b.append(f'<path class="arrow" d="M{x1} 80 L{x2 - 2} 80"/>')
    for x, t in [(250, "1 pre event"), (480, "2 post rule"), (710, "3 post event")]:
        b.append(f'<rect class="snap" x="{x}" y="175" width="180" height="40" rx="8"/><text x="{x + 12}" y="200">🪵 {esc(t)}</text>')
        b.append(f'<path class="arrow" d="M{x + 90} 140 L{x + 90} 173"/>')
    b.append(f'<text class="small" x="10" y="240">the log keeps the view three times: built before the call, with the answer applied to a copy, rebuilt when the event is over</text>')
    return f'<svg class="fig" viewBox="0 0 {W} {H}" role="img" aria-label="A rule\'s call: the game, the room\'s view, the Hazel rule, the game acting, and the log\'s three snapshots">{DEFS}{"".join(b)}</svg>'

FIELDS = ["lever_L", "lever_R", "wiring", "draws", "pits_on", "covered", "hatch", "things", "rooms", "exits", "out", "at_col", "at_row", "cols", "rows", "cells"]
FILLS = {"TrapRoom": ["lever_L", "lever_R", "wiring", "draws", "pits_on", "covered"], "TreeRoom": ["hatch"], "Square": ["things"],
         "World": ["at_col", "at_row", "cols", "rows", "cells"], "Castle": ["rooms", "exits", "out"]}
def svg_grid():
    rooms = list(FILLS)
    L, T, cw, ch = 110, 90, 46, 34
    W, H = L + cw * len(FIELDS) + 20, T + ch * len(rooms) + 40
    b = []
    for j, f in enumerate(FIELDS):
        x = L + cw * j + cw / 2
        b.append(f'<text class="mono" transform="translate({x + 4},{T - 8}) rotate(-50)">{f}</text>')
    for i, r in enumerate(rooms):
        y = T + ch * i
        b.append(f'<text x="{L - 10}" y="{y + 22}" text-anchor="end" font-weight="600">{r}</text>')
        for j, f in enumerate(FIELDS):
            on = f in FILLS[r]
            b.append(f'<rect class="{"on" if on else "off"}" x="{L + cw * j + 6}" y="{y + 6}" width="{cw - 12}" height="{ch - 12}" rx="5" opacity="{1 if on else 0.55}"/>')
    n = sum(len(v) for v in FILLS.values())
    b.append(f'<text class="small" x="{L}" y="{H - 12}">filled from the game: {n} of {len(FIELDS) * len(rooms)} cells; every other field is scriptNoGlobals\' default (false, 0, [], "auto")</text>')
    return f'<svg class="fig" viewBox="0 0 {W} {H}" role="img" aria-label="Which of Globals\' 16 fields each of the five rooms fills">{"".join(b)}</svg>'

KIND_COLOR = {"deepsea": "#1e3a8a", "sea": "#3b82f6", "lake": "#60a5fa", "waterfall": "#38bdf8", "beach": "#fcd34d", "forest": "#15803d", "woodpath": "#4d7c0f",
              "fairyforest": "#a3e635", "crossing": "#a8a29e", "clearing": "#86efac", "mountains": "#78716c", "witch": "#7c3aed", "castle": "#e11d48",
              "treehouse": "#b45309", "house": "#f97316", "campsite": "#ea580c", "cemetery": "#6b7280"}
def svg_world():
    cols, rows = P["cols"], P["rows"]
    s, L, T = 82, 30, 30
    W, H = L + s * cols + 250, T + s * rows + 20
    b = []
    letters = "ABCDEFGHIJKL"
    for c in range(cols): b.append(f'<text x="{L + s * c + s / 2}" y="{T - 10}" text-anchor="middle" class="small">{letters[c]}</text>')
    for r in range(rows): b.append(f'<text x="{L - 12}" y="{T + s * r + s / 2 + 4}" text-anchor="middle" class="small">{r + 1}</text>')
    d = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0), "NE": (1, -1), "NW": (-1, -1), "SE": (1, 1), "SW": (-1, 1)}
    for t in P["squares"]:
        c, r = map(int, t["key"].split(","))
        cx, cy = L + s * c + s / 2, T + s * r + s / 2
        for w in t["ways"]:
            dx, dy = d.get(w, (0, 0))
            b.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + dx * s * 0.5}" y2="{cy + dy * s * 0.5}" stroke="var(--muted)" stroke-width="1.2" opacity="0.6"/>')
    def count(xs): return sum(1 + count(x[2]) for x in xs)
    for t in P["squares"]:
        c, r = map(int, t["key"].split(","))
        x, y = L + s * c + 8, T + s * r + 8
        col = KIND_COLOR.get(t["kind"], "#999")
        b.append(f'<rect x="{x}" y="{y}" width="{s - 16}" height="{s - 16}" rx="8" fill="{col}" opacity="0.85"/>')
        b.append(f'<text x="{x + (s - 16) / 2}" y="{y + 25}" text-anchor="middle" class="kindtxt" style="fill:#fff;font-weight:700">{t["square"]}</text>')
        b.append(f'<text x="{x + (s - 16) / 2}" y="{y + 40}" text-anchor="middle" class="kindtxt" style="fill:#fff">{esc(t["kind"])}</text>')
        n = count(t["insides"])
        if n: b.append(f'<text x="{x + (s - 16) / 2}" y="{y + 55}" text-anchor="middle" class="kindtxt" style="fill:#fff">+{n} inside</text>')
    lx = L + s * cols + 24
    b.append(f'<text x="{lx}" y="{T + 10}" font-weight="700">the default world, "start"</text>')
    for i, line in enumerate([f"{len(P['squares'])} squares on a {cols} × {rows} grid", f"{P['square_ways']} ways between them (lines)",
                              f"{P['addresses_in_world']} places counting the insides", f"+ {len(P['elsewhere'])} off the grid: {', '.join(P['elsewhere'])}",
                              f"start: {P['start']}"]):
        b.append(f'<text x="{lx}" y="{T + 34 + 20 * i}" class="small">{esc(line)}</text>')
    return f'<svg class="fig" viewBox="0 0 {W} {H}" role="img" aria-label="The default world: 31 squares, their kinds, their ways, and how many places are inside each">{"".join(b)}</svg>'

def svg_tree():
    # one square's places as a tree, the castle at E4 and the tree house at E2, with today's keys beside the proposed address
    rows = [(0, "world(start)", "state.world (id w1, name \"start\")"),
            (1, "(square(E4))", "W.cells[\"4,3\"], kind castle"),
            (2, "(castle(N))", "B.castle = \"N\" (from the square's own settings)"),
            (3, "(room(3))", "B.castleRoom = 3, style castleRoom3N = \"trap\""),
            (4, "(lever(L))", "B.castleLeverL_3N (no id: a key spelled from parts)"),
            (4, "(pit(1))", "B.castlePitOn0_3N, the left pit: 0 in code, 1 here"),
            (1, "(square(E2))", "W.cells[\"4,1\"], kind treehouse"),
            (2, "(house(1))", "B.inside = 1 (treeroom), room1 = its furnishing"),
            (3, "(hatch)", "B.hatchShut1 (the script sees hatch = Bool)"),
            (2, "(top)", "kind treetop; hatchShutTop; PullHatch(0)")]
    W, H = 900, 34 + 28 * len(rows)
    b = []
    for i, (lvl, a, today) in enumerate(rows):
        y = 26 + 28 * i
        x = 14 + 26 * lvl
        if lvl: b.append(f'<path d="M{x - 16} {y - 22} L{x - 16} {y - 4} L{x - 4} {y - 4}" stroke="var(--line)" stroke-width="1.5" fill="none"/>')
        b.append(f'<text class="mono" x="{x}" y="{y}" style="fill:var(--accent);font-weight:600">{esc(a)}</text>')
        b.append(f'<text class="small" x="430" y="{y}">{esc(today)}</text>')
    b.append(f'<text class="small" x="430" y="12" style="font-weight:700">where it lives in the game today</text>')
    return f'<svg class="fig" viewBox="0 0 {W} {H}" role="img" aria-label="Two squares\' places as a tree of addresses, each with its key in the game today">{"".join(b)}</svg>'

def svg_address():
    # world(start)(square(E4))(castle(N)) as Fumola's binary call: each Call node an owner applied to what it owns, each leaf text or a number
    W, H = 900, 300
    b = []
    def node(x, y, label, cls):
        w = 14 + 8.2 * len(label)
        b.append(f'<rect class="{cls}" x="{x - w / 2}" y="{y - 15}" width="{w}" height="30" rx="15"/><text class="mono" x="{x}" y="{y + 5}" text-anchor="middle">{esc(label)}</text>')
    def edge(x1, y1, x2, y2): b.append(f'<line x1="{x1}" y1="{y1 + 15}" x2="{x2}" y2="{y2 - 15}" stroke="var(--muted)" stroke-width="1.4"/>')
    # Call(Call(Call(world(start)), ...)): the spine down the left, each argument a small Call(kind, name)
    spine = [("Call", 470, 30), ("Call", 330, 95), ("Call", 190, 160)]
    args = [("castle(N)", 620, 95), ("square(E4)", 470, 160), ("world(start)", 110, 225), ]
    for (lab, x, y) in spine: node(x, y, lab, "box")
    edge(470, 30, 330, 95); edge(470, 30, 620, 95); edge(330, 95, 190, 160); edge(330, 95, 470, 160); edge(190, 160, 110, 225)
    for (lab, x, y) in args: node(x, y, lab, "hz")
    # one argument opened up: castle(N) = Call(Text("castle"), Text("N"))
    node(620, 160, "Call", "box"); edge(620, 95, 620, 160)
    node(560, 225, 'Text("castle")', "snap"); node(690, 225, 'Text("N")', "snap"); edge(620, 160, 560, 225); edge(620, 160, 690, 225)
    b.append(f'<text class="small" x="10" y="282">world(start)(square(E4))(castle(N)): one binary form, Call(S1, S2), makes both a step (castle(N)) and the path (an owner applied to what it owns)</text>')
    return f'<svg class="fig" viewBox="0 0 {W} {H}" role="img" aria-label="A game symbol as a tree of binary calls">{"".join(b)}</svg>'

def svg_life():
    W, H = 900, 200
    b = []
    nodes = [(20, "box", "template", ["a kind, placed nowhere:", "lever, `ninja, room(trap)"]),
             (320, "hz", "placed", ["owned by a place:", "...room(3).lever(L)"]),
             (620, "snap", "set aside", ["in the world's buffer,", "still itself, no owner"])]
    for x, cls, t, ls in nodes:
        b.append(f'<rect class="{cls}" x="{x}" y="30" width="250" height="80" rx="12"/><text x="{x + 14}" y="55" font-weight="700">{t}</text>')
        for i, l in enumerate(ls): b.append(f'<text class="small" x="{x + 14}" y="{75 + 16 * i}">{esc(l)}</text>')
    b.append('<path class="arrow" d="M270 70 L318 70"/><text class="small" x="276" y="62">make</text>')
    b.append('<path class="arrow" d="M570 60 L618 60"/><text class="small" x="572" y="52">take out</text>')
    b.append('<path class="arrow" d="M618 90 L572 90"/><text class="small" x="574" y="104">put back</text>')
    b.append('<path class="arrow" d="M445 110 C445 170 460 170 445 112"/><text class="small" x="470" y="160">move: a new owner, the same name</text>')
    b.append('<text class="small" x="20" y="190">a thing keeps the name it was made with; where it is (owner, or the buffer) is a field that changes</text>')
    return f'<svg class="fig" viewBox="0 0 {W} {H}" role="img" aria-label="A thing\'s life: a template, made and placed, moved, set aside and put back, keeping its name">{DEFS}{"".join(b)}</svg>'

def svg_words():
    # the words as they grew: each wave's word, and what it means now
    waves = [("10-09", "background", "state.background.kind: the picture behind the friend"),
             ("10-12", "kind / scene", "SCENES, backgroundSvg; a 'kind of place' in the picker"),
             ("10-14", "castle, room", "castleRoom n; ROOM_KINDS styles; 'room' for 6 more things"),
             ("10-15", "tree house n", "B.inside = the house; hatchShut{n}"),
             ("10-17", "world, square", "state.world, W.cells[\"c,r\"], D4 in the UI; cells in code"),
             ("10-18", "inside, off the grid", "INSIDES, ELSEWHERE, W.off[placeKey]"),
             ("10-19", "place", "PLACES, placeKey, person.place: in code, never in the UI's words"),
             ("10-21", "Room (scripts)", "SCRIPT_ROOMS: TrapRoom, TreeRoom, Square, World, Castle")]
    W, H = 900, 40 + 30 * len(waves)
    b = [f'<line x1="70" y1="20" x2="70" y2="{H - 14}" stroke="var(--line)" stroke-width="2"/>']
    for i, (d, w, m) in enumerate(waves):
        y = 36 + 30 * i
        b.append(f'<circle cx="70" cy="{y - 5}" r="5" class="on"/><text class="small" x="10" y="{y}">{d}</text>')
        b.append(f'<text x="88" y="{y}" font-weight="700">{esc(w)}</text><text class="small" x="300" y="{y}">{esc(m)}</text>')
    return f'<svg class="fig" viewBox="0 0 {W} {H}" role="img" aria-label="The game\'s words for where, as they came in">{"".join(b)}</svg>'

def svg_store():
    W, H = 900, 190
    b = []
    b.append('<rect class="box" x="20" y="20" width="400" height="150" rx="12"/><text x="36" y="44" font-weight="700">Fumola\'s store</text>')
    b.append('<text class="small" x="36" y="66">a cell is named by space and by time, both nesting symbols:</text>')
    b.append('<text class="mono small" x="36" y="90">space  `region(`x)   (a callee names freely)</text>')
    b.append('<text class="mono small" x="36" y="110">time   a revision: a read answers the greatest</text>')
    b.append('<text class="mono small" x="36" y="126">       comparable earlier write</text>')
    b.append('<text class="small" x="36" y="152">so one name carries a history, not one value</text>')
    b.append('<rect class="hz" x="470" y="20" width="410" height="150" rx="12"/><text x="486" y="44" font-weight="700">MUDU\'s state, as proposed</text>')
    b.append('<text class="small" x="486" y="66">the space half only: every place, thing and person</text>')
    b.append('<text class="small" x="486" y="84">at a nested address, world(start)(square(E4))...</text>')
    b.append('<text class="small" x="486" y="106">no symbolic time, for now: one current state; the</text>')
    b.append('<text class="small" x="486" y="124">log\'s three snapshots per event are the nearest</text>')
    b.append('<text class="small" x="486" y="142">thing to time, and where it would come in</text>')
    return f'<svg class="fig" viewBox="0 0 {W} {H}" role="img" aria-label="Fumola\'s store by space and time, beside MUDU\'s state by space only">{"".join(b)}</svg>'

# ---------------------------------------------------------------- the appendix: every address of the default world
def picture_of(kind, castle_style=None):
    if castle_style: return f"backgrounds/castleroom--{castle_style}.svg"
    return f"backgrounds/{kind}.svg"
INSIDE_KIND = {"livingroom": "livingroom", "witchroom": "witchroom", "healerroom": "healerroom", "underwater": "underwater", "hutroom": "hutroom",
               "tent": "tent", "top": "treetop", "house": "treeroom", "cave": "cave"}
def appendix_rows():
    rows = []   # (group, address, what, picture)
    N = P["castles"]["N"]
    counts = {}
    for t in P["squares"]:
        sq = f"world(start)(square({t['square']}))"
        rows.append(("places", sq, f"a square: {t['kind']}" + (f", named {t['name']}" if t["name"] else ""), picture_of(t["kind"])))
        k = t["kind"]
        for (ik, which, kids) in t["insides"]:
            if k == "castle":
                style = N[which - 1]
                a = f"{sq}(castle(N))(room({which}))"
                rows.append(("places", a, f"N's castle, room {which}: {style}", picture_of("castleroom", style)))
            elif k == "waterfall":
                a = f"{sq}(cave)"; rows.append(("places", a, "the cave behind the falls", picture_of("cave")))
                rows.append(("places", a + "(room)", "the cave's room", picture_of("caveroom")))
            else:
                a = f"{sq}(" + ik + (f"({which})" if which is not None else "") + ")"
                rows.append(("places", a, {"house": f"tree house {which}'s room", "top": "the round room at the top", "tent": f"tent {which}"}.get(ik, ik), picture_of(INSIDE_KIND.get(ik, ik))))
                for (kk, _, _) in kids:
                    pass
        for th in t["things"]:
            counts.setdefault((sq, th), 0); counts[(sq, th)] += 1
            n = counts[(sq, th)]
            rows.append(("things", f"{sq}({th}({n}))", f"a {th}, the {n}{'st' if n == 1 else 'nd' if n == 2 else 'rd' if n == 3 else 'th'} placed here", f"things/{th}.svg"))
    for e in P["elsewhere"]:
        rows.append(("places", f"world(start)(elsewhere({e}))", "off the grid", picture_of(e)))
    for kind, label in P["places"]:
        if kind == "none": continue
        rows.append(("templates: places", f"place({kind})", label, picture_of(kind)))
    for st, v in P["room_kinds"].items():
        rows.append(("templates: places", f"place(castleroom)(style({st}))", (v.get("label") or st) + f", exits: {v['exits']}", picture_of("castleroom", st)))
    COST = ["tiger", "cat", "lion", "bear", "falcon", "raccoon", "bobcat", "leopard", "eagle", "cheetah", "jaguar", "moth", "falconsuit", "eaglesuit", "wolf", "deer",
            "dragon", "sasquatch", "witch", "fairy", "ghost", "gnome", "wizard", "monk", "robin", "knight", "queen", "king", "robot", "cowgirl", "cowboy", "ninja",
            "giraffe", "scuba", "diver"]
    rows.append(("templates: people", "person(friend)", "the friend at the defaults, no costume", "body/_default.svg"))
    for c in COST: rows.append(("templates: people", f"person(costume({c}))", f"a person in the {c} costume", f"costume/kind--{c}.svg"))
    return rows

# ---------------------------------------------------------------- the words
ABSTRACT = ("This is a case study of game scripts written in Hazel. Messed Up Dress Up, a game made with M and N, lets five of its rooms hand their "
 "events to Hazel rules, each a function <code>on_event : (Globals, Event) -&gt; Cmd</code>. The case shows what such a rule meets: its "
 "<code>Globals</code> is not the game's state but a view the game builds fresh for each room, that room's few fields filled and the rest at defaults, "
 "with which castle, house or lever is meant decided by context, out of the rule's sight. No one designed it so; it is what waves of features left, each "
 "added the day the kids asked, each with its own words and numbers for <i>where</i> (a background, a square, a room, an inside, a list index), none "
 "reworked after.</p><p>From these experiences, we (Matthew, Claude, and M and N) reflect, and now present a more holistic model: every place, thing and person gets one readable name, a <code>Symbol</code> of names, "
 "numbers and Fumola's binary call, like <code>world(start)(square(E4))(castle(N))(room(3))</code>; a thing keeps its name as it moves or is set aside, "
 "as Adapton's names keep their identity; and the rules' types, a <code>RuleState</code> per room, a whole-game <code>Globals</code> and a "
 "<code>Cmd</code> that names what it acts on, are built on those names. An appendix lists every name in the game's first world, with its settings as "
 "a Hazel record and every picture the game's archive has of it.")

TODAY_TYPES = """type Event =
  + Pull(Side) + PullBoulder(Side) + PullHatch(Int) + PullThing(Int)
  + FallPit(Int) + WayOut(Int) + Way(Dir)

type Cmd =
  + Done + Flip(Side, Cmd) + Say(String, Cmd) + SetPit(Int, Bool, Cmd)
  + DropBoulder(Int, Cmd) + LiftBoulder(Int, Cmd) + SetHatch(Int, Bool, Cmd)
  + OpenDoor(Int, Bool, Cmd) + DropRock(Int, Bool, Cmd) + Wait(Int, Cmd)
  + GoRoom(Int, Cmd) + GoSquare(Int, Int, Dir, Cmd)

type Thing = (at = Int, uid = String, kind = String, on = Bool, works = [String],
              does = String, open = Bool, boulder = Bool)
type Cell = (col = Int, row = Int, kind = Place, ways = [Dir])

type Globals = (lever_L = Bool, lever_R = Bool, wiring = Wiring, draws = [Float],
                pits_on = [Bool], covered = [Bool], hatch = Bool, things = [Thing],
                rooms = [Room], exits = [Exit], out = Out, at_col = Int,
                at_row = Int, cols = Int, rows = Int, cells = [Cell])

# the tree room's rule, whole #
module TreeRoom = {
  let on_event = fun (g : Globals, e : Event) : Cmd ->
    case e
    | PullHatch(n) => SetHatch(n, !g.hatch, Done)
    | _ => Done
    end
}"""

PROPOSED_ADDR = """# a game symbol, as Fumola's: text, a number, or one applied to another #
type Symbol = + Text(String) + Num(Int) + Call(Symbol, Symbol)

# supposed: Hazel parses a symbol from its text and prints it back, so
   rules, saves and logs write world(start)(square(E4)) #
# parse_sym : String -> Symbol    "a(b)(c)" is Call(Call(a, b), c) #
# print_sym : Symbol -> String    print_sym(parse_sym(t)) == t #

# lever(L) is Call(Text("lever"), Text("L"));
   world(start)(square(E4)) is Call(world(start), square(E4)):
   an owner applied to what it owns, as Fumola's `region(`x) #

type Where = + Placed(Symbol) + SetAside + Carried(Symbol)

type Setting = + B(Bool) + I(Int) + F(Float) + S(String) + A(Symbol)

# a placed thing or person: its name for good, its template, where it is now #
type Instance = (id = Symbol, template = String, where = Where,
                 settings = [(String, Setting)])

# a place: its address, its template, its ways, and what it owns #
type Way = (dir = Dir, to = Symbol, via = + Open + Door(Symbol) + Shut(Symbol))
type PlaceState = (id = Symbol, template = String, ways = [Way], owns = [Symbol])"""

PROPOSED_GLOBALS = """# the whole game, as any rule may read it #
type Globals = (
  friend = (id = Symbol, at = Symbol),      # the person being played, and where #
  places = [PlaceState],
  instances = [Instance],               # every thing and person made #
  set_aside = [Symbol],                   # the world's buffer, re-placeable #
  random_numbers = [Float]              # the event's random numbers (today's draws) #
)

# what each room's rule is about: its own, named, typed #
type TrapRoomState = (here = Symbol,
  levers = [(id = Symbol, up = Bool)], wiring = Wiring,
  pits = [(id = Symbol, there = Bool, covered = Bool)])
type TreeRoomState = (here = Symbol, hatch = (id = Symbol, shut = Bool))
type SquareState = (here = Symbol, levers = [Instance], doors = [Instance])
type WorldState = (here = Symbol, squares = [PlaceState])
type CastleState = (here = Symbol, rooms = [PlaceState], out = Out)

type RuleState =
  + Trap(TrapRoomState) + Tree(TreeRoomState) + Square(SquareState)
  + World(WorldState) + Castle(CastleState)

# the event names what happened to, by address #
type Event = + Pull(Symbol) + Fall(Symbol) + Leave(Symbol, Dir) + Arrive(Symbol)

# commands name what they act on, by address #
type Cmd =
  + Done + Say(String, Cmd) + Wait(Int, Cmd)
  + Flip(Symbol, Cmd)                     # a lever #
  + Swing(Symbol, Bool, Cmd)              # a hatch, a pit's lid, a door: open? #
  + Set(Symbol, String, Setting, Cmd)     # any setting of any instance #
  + Move(Symbol, Where, Cmd)              # an instance to a new owner, or aside #
  + Go(Symbol, Cmd)                       # the friend, to a place #

# a rule: its room's state, the whole game to read, the event #
let on_event : (RuleState, Globals, Event) -> Cmd"""

MAPPING = [("PullHatch(1)", "Pull(world(start)(square(E2))(house(1))(hatch))"),
           ("SetHatch(1, false, Done)", "Swing(…house(1).hatch, true, Done)"),
           ("Pull(L) in the trap room", "Pull(world(start)(square(E4))(castle(N))(room(3))(lever(L)))"),
           ("Flip(L, Done)", "Flip(…room(3).lever(L), Done)"),
           ("SetPit(0, true, …)", "Swing(…room(3).pit(1), true, …)"),
           ("PullThing(4)   (the 5th thing in the list)", "Pull(…square(B6).lever(2))   (a name kept when the list changes)"),
           ("OpenDoor(7, true, …)", "Swing(…square(B6).trapdoor(1), true, …)"),
           ("GoRoom(0, …)   (0 = out of the castle)", "Go(world(start)(square(E4)), …)"),
           ("GoSquare(3, 3, S, …)", "Go(world(start)(square(D4)), …)"),
           ("(none: a rule cannot move a thing)", "Move(…lever(2), SetAside, …)")]

def mapping_table():
    return "<div class=scroll><table class=t><tr><th>today</th><th>proposed</th></tr>" + "".join(f"<tr><td class=addr>{esc(a)}</td><td class=addr>{esc(b)}</td></tr>" for a, b in MAPPING) + "</table></div>"

VOCAB = [("background", "state.background (the place and the friend's spot in it), backgroundSvg", "🏞️ Background tab"),
         ("kind", "B.kind and cell.kind (a place); ROOM_KINDS (castle room styles); thing.kind", "\"kind of place\" (a group)"),
         ("place", "PLACES, placeKey, objPlace, person.place; castlePlaces (table seats)", "\"🗺️ the place\", \"not in any place\""),
         ("scene", "SCENES, *Scene functions, SCENE (stage geometry)", "hardly"),
         ("square / cell", "squareName, Square (script), GoSquare / W.cells, cellKeys", "square, D4 / never \"cell\""),
         ("room", "castle rooms; treeroom; ROOMS (furnishing); NORTH_ROOMS (indoor); hutRooms (huts); SCRIPT_ROOMS (modules)", "\"🚪 room n is\", \"🦇 cave room\""),
         ("inside", "INSIDES; B.inside (= the tree house's number)", "\"inside the castle\", \"🚪 off the grid\""),
         ("house", "B.houses, data-house (tree houses); kind \"house\" (the family's)", "\"🏡 house n\" vs \"🏠 house and yard\""),
         ("home", "worldHome, passageHome", "\"🏠 home\" (a group of places)"),
         ("world", "state.world (one grid), worldsAway", "🗺️ World design, \"🌍 world N\"")]

def vocab_table():
    return "<div class=scroll><table class=t><tr><th>word</th><th>in the code</th><th>in the game's UI</th></tr>" + "".join(f"<tr><td><b>{esc(w)}</b></td><td>{esc(c)}</td><td>{esc(u)}</td></tr>" for w, c, u in VOCAB) + "</table></div>"

ROOMS_TABLE = [("TrapRoom", "Pull(L|R), PullBoulder(side)", "Flip, SetPit, DropBoulder, LiftBoulder", "lever_L, lever_R, wiring, draws, pits_on, covered", "the trap room of the castle shown, room n"),
               ("TreeRoom", "PullHatch(n)", "SetHatch(n, shut)", "hatch", "the house the friend is in: hatchHouse(), 0 for the top"),
               ("Square", "PullThing(i)", "OpenDoor(at, open), DropRock(at, down)", "things", "this place's levers and trap doors, at = index in its list"),
               ("World", "Way(d)", "GoSquare(col, row, side)", "at_col, at_row, cols, rows, cells", "the world shown, every square"),
               ("Castle", "FallPit(0|1), WayOut(n)", "GoRoom(r)", "rooms, exits, out", "the castle shown, room n's way out")]
def rooms_table():
    return ("<div class=scroll><table class=t><tr><th>module</th><th>its events</th><th>its commands</th><th>Globals fields it fills</th><th>which instance</th></tr>" +
            "".join(f"<tr><td><b>{a}</b></td><td class=addr>{esc(b)}</td><td class=addr>{esc(c)}</td><td class=addr>{esc(d)}</td><td>{esc(e)}</td></tr>" for a, b, c, d, e in ROOMS_TABLE) + "</table></div>")

PARAMS = json.load(open(os.path.join(R, "data", "params.json")))
ARCH = os.path.expanduser("~/dress-up-pictures/pictures")
def ctor(v):
    c = re.sub(r"[^A-Za-z0-9]+", " ", str(v)).title().replace(" ", "")
    return ("V" + c) if not c or c[0].isdigit() else c
def hz_field(r):
    t = r["t"]
    if "bool" in t: ty = "Bool"
    elif "range" in t: ty = "Int"
    elif "color" in t: ty = "String"
    elif "choice" in t and t["choice"]:
        cs = list(dict.fromkeys(ctor(v) for v in t["choice"]))
        ty = "(" + " ".join("+ " + c for c in cs) + ")"
    else: ty = "String"
    lab = re.sub(r"[^\w ,'()-]", "", r.get("label") or "").strip()
    return f"  {r['key']} = {ty}" + (f",  # {lab} #" if lab else ",")
def hz_record(name, rows):
    if not rows: return ""
    body = "\n".join(hz_field(r) for r in rows)
    body = body[:body.rfind(",")] + body[body.rfind(",") + 1:] if body.endswith(",") else re.sub(r",(  #[^#]*#)$", r"\1", body)
    return f"type {name} = (\n{body}\n)"
def tname(k): return ctor(k)
def place_type(k): return hz_record(tname(k) + "Place", PARAMS["places"].get(k, []))
def costume_type(k): return hz_record(tname(k) + "Costume", PARAMS["costumes"].get(k, []))
def thing_type(k): return hz_record(tname(k), PARAMS["things"].get(k, []))
# every picture the archive has of a place, a costume or a thing: from its manifest, and each menu picture's saved settings
GAL = {}
def gal(key, e):
    if e.get("svg"): GAL.setdefault(key, []).append([e["svg"], e.get("thumb") or "", e.get("label") or e["name"]])
if os.path.exists(os.path.join(ARCH, "manifest.json")):
    for e in json.load(open(os.path.join(ARCH, "manifest.json"))):
        fo, nm = e["folder"], e["name"]
        if not e.get("svg"): continue
        if fo.startswith("backgrounds"): gal("place:" + nm, e)
        elif fo == "seats" or fo == "moves": gal("place:" + nm.split("--")[1], e)
        elif fo in ("things", "things-alone"): gal("thing:" + nm, e)
        elif fo in ("background-menus", "costume") and e.get("settings"):
            try: st = json.load(open(os.path.join(ARCH, e["settings"])))
            except Exception: continue
            st = st.get("state", st)
            if fo == "background-menus":
                b = st.get("background", {}); k = b.get("kind")
                if k == "castleroom":
                    n = b.get("castleRoom", 1); style = b.get(f"castleRoom{n}{b.get('castle', 'N')}")
                    if style: gal("place:castleroom--" + style, e)
                if k and k != "none": gal("place:" + k, e)
            else:
                k = st.get("costume", {}).get("kind")
                if k and k != "none": gal("costume:" + k, e)
def anchor(a): return "a-" + re.sub(r"[^A-Za-z0-9]+", "-", a).strip("-")

APX = appendix_rows()
def gal_key(pic):
    m = re.match(r"backgrounds/(.+)\.svg$", pic)
    if m: return "place:" + m.group(1)
    m = re.match(r"things/(.+)\.svg$", pic)
    if m: return "thing:" + m.group(1)
    m = re.match(r"costume/kind--(.+)\.svg$", pic)
    if m: return "costume:" + m.group(1)
    return ""
def type_of(key):
    kind, _, k = key.partition(":")
    if kind == "place": return place_type(k.split("--")[0])
    if kind == "thing": return thing_type(k)
    if kind == "costume": return costume_type(k)
    return ""
def appendix_html():
    groups, out, keys = [], [], set()
    for g, a, w, pic in APX:
        if g not in groups: groups.append(g)
    for g in groups:
        rows = [(a, w, pic) for gg, a, w, pic in APX if gg == g]
        out.append(f'<h3 class="grp" id="apx-{re.sub(r"[^a-z]+", "-", g)}">{esc(g)} <span class="what">({len(rows)})</span></h3>')
        for a, w, pic in rows:
            k = gal_key(pic); keys.add(k)
            alone = pic.replace("things/", "things-alone/") if pic.startswith("things/") else ""
            out.append(f'<details id="{anchor(a)}" data-pic="{esc(PICS + pic)}"' + (f' data-alone="{esc(PICS + alone)}"' if alone else "") + f' data-key="{esc(k)}">'
                       f'<summary><span class="addr">{esc(a)}</span><span class="what">{esc(w)}</span><button type="button" class="copylink" title="copy a link to this entry">copy link</button></summary><div class="pic"></div></details>')
    data = {}
    for k in sorted(x for x in keys if x):
        t = type_of(k)
        data[k] = {"type": hazel_hl(t) if t else "", "pics": GAL.get(k, [])}
    blob = json.dumps({"base": PICS, "entries": data}, ensure_ascii=False).replace("</", "<\\/")
    out.append(f'<script type="application/json" id="apx-data">{blob}</script>')
    return "\n".join(out)
APX_JS = """<script>
// (the appendix: names and links load with the page; a row's record type and its pictures only when it is opened)
const APX = JSON.parse(document.getElementById('apx-data').textContent);
const pic = (u, cap, cls) => { const f = document.createElement('figure'), a = document.createElement('a'), i = document.createElement('img');
  i.src = u; i.alt = cap; i.onerror = () => { f.textContent = 'not in the archive yet: ' + u; }; if (cls) f.className = cls;
  a.href = u.replace('/thumbs/', '/').replace(/\\.webp$/, '.svg'); a.append(i); f.append(a);
  if (cap) { const c = document.createElement('figcaption'); c.textContent = cap; f.append(c); } return f; };
function fill(d) {
  const box = d.querySelector('.pic'); if (box.firstChild) return;
  const main = document.createElement('div'); main.className = 'main';
  for (const [u, cap] of (d.dataset.alone ? [[d.dataset.alone, 'alone'], [d.dataset.pic, 'in the empty room, for its size']] : [[d.dataset.pic, '']])) main.append(pic(u, cap));
  box.append(main);
  const e = APX.entries[d.dataset.key];
  if (e && e.type) { const p = document.createElement('pre'); p.className = 'hz'; p.innerHTML = e.type; const c = document.createElement('p'); c.className = 'codecap'; c.textContent = 'its settings, as a Hazel record type (from the game\\'s own menus):'; box.append(c, p); }
  const more = e ? e.pics.filter(p => APX.base + p[0] !== d.dataset.pic && APX.base + p[0] !== d.dataset.alone) : [];
  if (more.length) { const c = document.createElement('p'); c.className = 'codecap'; c.textContent = more.length + ' more pictures of it in the archive (each a setting changed, an overlay, a seat or a climb):'; const g = document.createElement('div'); g.className = 'gallery';
    for (const [svg, th, lab] of more) g.append(pic(APX.base + (th || svg), lab, 'small')); box.append(c, g); }
}
for (const d of document.querySelectorAll('details[data-pic]')) d.addEventListener('toggle', () => { if (d.open) fill(d); });
for (const b of document.querySelectorAll('button.copylink')) b.addEventListener('click', ev => {
  ev.preventDefault(); ev.stopPropagation();
  const id = b.closest('details').id, u = location.origin + location.pathname + '#' + id;
  navigator.clipboard.writeText(u).then(() => { b.textContent = 'copied'; setTimeout(() => b.textContent = 'copy link', 1500); });
});
const openHash = () => { const d = location.hash && document.getElementById(location.hash.slice(1)); if (d && d.matches('details[data-pic]')) { d.open = true; fill(d); d.scrollIntoView(); } };
openHash(); addEventListener('hashchange', openHash);
</script>"""

nthings = sum(len(t["things"]) for t in P["squares"])
PAGE = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Game Scripts in Hazel, a Case Study</title>
<meta name="description" content="Writing Messed Up Dress Up's game rules in Hazel: what a rule sees today (Event, Cmd, Globals), why Globals is a per-rule view, and a proposal: one address for every place, thing and person, with Globals, RuleState and Cmd built on it.">
<style>{STYLE}{FIGCSS}</style></head>
<body><main>
<p class="series"><a href="../">Hazel reports</a> · <code class="ref"><b>^report(</b>33<b>)</b></code> · Messed Up Dress Up's scripts · 2026-10-25 · <span class="wip">work in progress</span></p>
<h1>Game Scripts in Hazel, a Case Study</h1>

<div class="headline abstract"><p><b>Abstract.</b> {re.sub(r"<code>(.*?)</code>", lambda m: "<code class=hzi>" + hazel_hl(html.unescape(m.group(1))) + "</code>", ABSTRACT)}</p></div>
<nav class="outline" id="outline"><p><b>Outline</b></p>
<ol class="parts">
<li><a href="#part-1"><b>How it works today</b></a>: piecemeal, each part on its own terms
<ol><li><a href="#call">A rule, today</a>: <code>Event</code>, <code>Cmd</code> and <code>Globals</code>, and one event end to end</li>
<li><a href="#not-global">Globals is a per-rule view</a>: each room fills its own fields; the game picks which hatch</li>
<li><a href="#where-today">Where, today</a>: the default world, eleven words, and numbers for names</li></ol></li>
<li><a href="#part-2"><b>How it got this way</b></a>
<ol><li><a href="#waves">Waves of features</a>: dressing up, doors, castles, tree houses, a world, things, rules</li></ol></li>
<li><a href="#part-3"><b>A more holistic approach</b></a>
<ol><li><a href="#roomstate">RuleState, and a real Globals</a></li>
<li><a href="#paths">Every place, as a path</a></li>
<li><a href="#ids">Names that can't collide</a>: addresses, Fumola's symbols, Adapton's identity names, templates, the set-aside buffer</li>
<li><a href="#types">Globals, RuleState and Cmd, proposed</a>, in Hazel, with today's commands beside them</li></ol></li>
<li><a href="#next">What next</a> · <a href="#how">How this was put together</a> · <a href="#appendix">Appendix: every address</a></li>
</ol></nav>

<p class="intro">This is written for readers who know Hazel and want to see what writing a game's rules in it involves. Part 1 shows the rules and their
types as they run today, in <a href="https://matthewhammer.org/kids-choice-games/dress-up/">the game</a> at <code>{GAME}</code> (0.0.429); Part 2 tells how
they came to be that way; Part 3 proposes what to change, in Hazel. The game's own guide for its young players is
<a href="https://matthewhammer.org/kids-choice-games/dress-up/reports/017/">a different document</a>.</p>

<p class="part" id="part-1"><span>Part 1</span> How it works today</p>
<p class="partsub">Piecemeal: each part works on its own terms, and they do not yet share a model.</p>
<h2 id="call">A rule, today</h2>
<p>The game is plain JS. Five of its rooms can hand an event to a rule written in Hazel (or Fumola, or left to the game's own JS), chosen room by room in
its 📜 Scripting tab. The Hazel program is one file of modules: <code>Common</code> (shared helpers) and one module per room, each with an
<code>on_event</code>. The game loads Hazel's JS library (<a href="https://github.com/hazelgrove/hazel/pull/2711">hazelgrove/hazel#2711</a>), builds the
program once per edit, and calls a room's function when its event happens ({src("25-scripting.js", 760, "scriptEvent")}).</p>
{fig(svg_call(), "Figure 1. One event, end to end. The game builds the room's view of its state, the Hazel rule answers a <code>Cmd</code>, and the game acts it out, one command at a time. The event log keeps the view three times, which is how the 📜 tab shows what an event changed.", "fig-call")}
<p>The types, as the game declares them at the top of the program ({src("25-scripting.js", 98, "25-scripting.js:98-102")}), and one room's whole rule:</p>
<pre class="hz">{hazel_hl(TODAY_TYPES)}</pre>
<p>A few things a Hazel reader should know about how these meet the game:</p>
<ul>
<li><b>A <code>Cmd</code> is a list spelled as a sum:</b> every command carries the rest, ending in <code>Done</code>. The game walks it
({src("25-scripting.js", 600, "scriptRun")}); <code>Wait(ms, rest)</code> holds the rest for later, so a rule can describe a timed sequence without a clock
of its own. An unknown command stops the walk.</li>
<li><b>The boundary is typed both ways.</b> The game's state is JS text and numbers; {src("25-scripting.js", 75, "scriptTypedGlobals")} turns strings into
the sums (<code>Wiring</code>, <code>Room</code>, <code>Out</code>, <code>Place</code>, <code>Dir</code>), and {src("25-scripting.js", 85, "scriptUntypedCmd")}
turns commands back. So the JS object has 17 fields and the rule sees 16: <code>out</code> and <code>out_room</code> become one <code>Out</code>.</li>
<li><b>A rule has no randomness or clock:</b> the trap room's two random draws come in as <code>draws</code>, drawn by the game from a seed it keeps.</li>
<li><b>One error anywhere sends every Hazel room back to the JS</b> (the program must be whole to run), and a rule that throws is said in the game and skipped.</li>
</ul>

<h2 id="not-global">Globals is a per-rule view</h2>
<p>Each room registers three functions ({src("25-scripting.js", 636, "SCRIPT_ACTS")}): <code>here</code> (is this event mine?), <code>globals</code>
(build my view) and <code>act</code> (how my commands change the game). The view is a <code>Globals</code> with the room's own fields filled from the game
and every other field at a default ({src("25-scripting.js", 634, "scriptNoGlobals")}):</p>
{fig(svg_grid(), "Figure 2. Which of the 16 fields each room fills. Purple: filled from the game for that room; grey: a default the rule should not read. No field is filled for two rooms.", "fig-grid")}
{rooms_table()}
<p><b>The tree room shows it best.</b> A tree has up to six houses and a round room at the top, each with its own trap door
(<code>hatchShut1</code> to <code>hatchShut6</code>, <code>hatchShutTop</code>). The rule gets one <code>hatch : Bool</code>: the door of the house the
friend is in, picked by the game ({src("26-drags-and-start.js", 592, "hatchHouse")}). The event carries the house's number, <code>PullHatch(1)</code>, and the
command repeats it, <code>SetHatch(1, false, Done)</code>, but the state does not: the game checks the number matches and refuses the command if not.
So the rule's <code>hatch</code> is "this hatch", resolved by context, and a rule cannot ask about any other.</p>
<p>The other rooms work the same way. The trap room's levers are the trap room of the castle shown; the square's things are the list of the place the friend is in,
each known by its index in that list (<code>at</code>); the castle's <code>out</code> is the way out of the room the friend is in. Nothing in
<code>Globals</code> says which castle, square or house: the game knows, and the rule is written as if there were only one.</p>
<p class="note">Two things the game's own guide says otherwise: <code>pits_on</code> is whether each pit is there at all, not whether it is open (that the
rule works out from the levers and the wiring), and "17 fields" counts the JS object, not what the rule sees.</p>

<h2 id="where-today">Where, today: eleven words, and numbers for names</h2>
<p>Read from the game itself (its default world and its tables of insides, castles and room styles, in node at <code>{GAME}</code>), with every trap door,
hatch and passage open:</p>
{fig(svg_world(), f"Figure 3. The default world. Each square is a place of some kind; {P['square_ways']} ways lead between squares (the lines); "
 f"{P['addresses_in_world'] - len(P['squares'])} more places are inside squares: castle rooms, tree houses, tents, the cave, the living room and the rest. "
 "The world can grow to 12 × 12 and hold more worlds; this is the one a new game starts in.", "fig-world")}
{vocab_table()}
<p><b>"Place" is the code's word and never the UI's;</b> the UI says background, square and room. And the ids are positions: a placed thing is its index in
its place's list (and only a trap door or a cave passage has a uid, a random string); a pit is 0 or 1; a house is 1 to 6; a castle room 1 to 13; a
square is <code>"c,r"</code> in code and <code>D4</code> on screen. A <code>1</code> in a command can be a house, a pit, a room or a list index, depending on
the command. Several keys already work like addresses, spelled differently each time: <code>placeKey</code> is <code>castleroom:N:3</code>,
<code>worldHome</code> is <code>off:w1:tent:2</code>, a person's place is <code>{{world, key}}</code> with no room part, and a setting's key spells its owner
into its name (<code>castleLeverL_3N</code>).</p>

<p class="part" id="part-2"><span>Part 2</span> How it got this way</p>
<p class="partsub">Waves of features and game experiences, each with its own words and keys.</p>
<h2 id="waves">Waves of features</h2>
<p>Messed Up Dress Up was made with M and N, a feature at a time, each released the day it worked, as they asked for it (the game's own rule: features
first, released at once). Each wave brought its own experience and, with it, its own way to say where the friend is, and none went back to rework the ones before:</p>
<ol>
<li><b>Dressing up, in front of a picture.</b> The first game was a friend to dress; <code>state.background.kind</code> was the picture behind them, one of a list
(<code>PLACES</code>, its group chips <q>kind of place</q>). A place was a picture, and a picture had no inside.</li>
<li><b>Places you can walk into.</b> Doors came next, each door a <code>data-to</code> naming a kind: the house's living room, the witch's room, the cave. An inside
was just another kind, reached by a door; "back" was a stack of where you had been (<code>trips</code>).</li>
<li><b>Castles and their rooms</b>, for N's and M's castle designs: three castles by whose they are, rooms by number (1 to 13) with styles
(<code>ROOM_KINDS</code>), and each room's settings spelled into its keys (<code>castleLeverL_3N</code>). The trap room's levers and pits came with them, numbered 0 and 1.</li>
<li><b>Tree houses</b>: up to six houses by number, a round room on top, bridges, ladders and hatches; <code>B.inside</code> became "which house".</li>
<li><b>A world to walk:</b> a grid of squares, each a place kind (<code>W.cells["c,r"]</code>, <code>D4</code> on screen), ways between squares, then other
worlds, insides kept "off the grid", cave passages that link any two places, and people placed in squares (<code>person.place {{world, key}}</code>, no room).</li>
<li><b>Things placed in places:</b> rocks, levers, trap doors, each an entry in its place's list, known by its index; a trap door and a passage got a random uid
so a lever and its twin could find them.</li>
<li><b>Rules in Hazel and Fumola</b>, for five rooms: each rule needed some of the game's state, and the simplest thing that worked was one record type with
every room's fields, filled per room. That is <code>Globals</code>.</li>
</ol>
{fig(svg_words(), "Figure 4. The words for where, roughly as they came in (October 2026), and what each means now in the code.", "fig-words")}
<p>Each step was the right size for its day, and the game kept working. The cost is what <a href="#where-today">Part 1</a> shows: eleven overlapping
words, ids that are positions, and a rule's state that is shaped for the game's convenience rather than the rule's. Nothing in it is wrong for one room; it
does not add up for a game that a rule, a log, or a second game should be able to read as a whole.</p>
<p class="part" id="part-3"><span>Part 3</span> A more holistic approach</p>
<p class="partsub">One model of where everything is, and rule types built on it.</p>
<h2 id="roomstate">RuleState, and a real Globals</h2>
<p>The fix the view asks for is to say what it is. <b>Each room's rule takes its own state type</b>, named for it: the tree room a hatch, the trap room its
levers and pits, the world its squares. No default fields, nothing for a rule to misread, and a rule's type says what it depends on. Matthew's name for
the sum of them is <code>RuleState</code>.</p>
<p><b>A real <code>Globals</code> is then the whole game,</b> read-only to rules. For a rule that wants to look further (is the other castle's trap set?
where is the friend?), for diagnostics, and for the log: the same addresses in every rule's state and in <code>Globals</code> let a tool show a change
anywhere. Rules still change the game only through commands, so the game stays the one place state changes.</p>
<p>Both need a way to say <i>which</i> hatch, lever or room, in one keyspace. That is the next three sections.</p>

<h2 id="paths">Every place, as a path</h2>
<p>Every move between places the game allows is a move along this tree or across it: the ways between squares; a door to an inside and back; a ladder, bridge
or hatch between tree houses; a pit from the trap room to a dungeon; a cave passage, which may lead to any place in any world; a picture you step into.
Each lands in exactly one node, so one path from the world down names any place a walk can reach:</p>
{fig(svg_tree(), "Figure 5. Two squares' places as addresses, each beside where the game keeps it today.", "fig-tree")}

<h2 id="ids">Names that can't collide</h2>
{fig(svg_address(), "Figure 6. A game symbol is text, a number, or one symbol applied to another, <code>S1(S2)</code>. A step is a call (<code>castle(N)</code>), and so is a path: the owner applied to what it owns, left to right.", "fig-addr")}
<p class="codecap">In Fumola, the same symbol, as it stands (its <code>Call</code>):</p>
<pre class="fu wrap">{fumola_hl("`world(`start)(`square(`E4))(`castle(`N))(`room(3))(`lever(`L))")}</pre>
<p class="codecap">In Hazel, a symbol is written as that text and parsed to the tree: parentheses, names and numbers, nothing else, and no constructor names in a rule:</p>
<pre class="hz wrap">{hazel_hl('let lever_L = parse_sym("world(start)(square(E4))(castle(N))(room(3))(lever(L))") in' + chr(10) + 'let room_3 = parse_sym("world(start)(square(E4))(castle(N))(room(3))") in' + chr(10) + 'print_sym(lever_L) == "world(start)(square(E4))(castle(N))(room(3))(lever(L))"')}</pre>
<p><b>Human readable:</b> as text, each step is a word and a name a player would use (<code>square(E4)</code>, <code>castle(N)</code>, <code>lever(L)</code>).
<b>Unambiguous:</b> the kind is part of every step (the first half of its call), and a name only has to be unique among its owner's children of that kind, so places, things and people
share one keyspace with no global counter.</p>
<p><b>This is Fumola's symbol, as it stands.</b> In <a href="https://fumola.org/#names-are-values">Fumola, names are values</a>: an identifier is a
symbol, a number is a symbol, and symbols compose by application and nest, <code>`adapton(`settings)</code>; Fumola's <code>Symbol</code> has exactly these
cases (<code>Id</code>, <code>Nat</code>, <code>Call</code>, and others besides); a game symbol needs only those three: names, numbers and parentheses. And its <a href="https://fumola.org/#space-and-time">space</a> is the same move
an address makes: a cell <code>`x</code> named inside the region <code>`region</code> is <code>`region(`x)</code>, so a callee names freely without colliding
with its caller, as a room names its levers without knowing which castle it is in.</p>
<p><b>Identity, not position.</b> <a href="https://adapton.org">Adapton</a> names a node so it keeps its name when its contents change; the alternative,
naming by content, cannot say "same node, new value" (Fumola's notes, <i>What is a cache key a function of?</i>). Names derived from position are worse
than either: an address survives only as long as the shape it addresses, which in Fumola's mergeSort measurements turned a repair of 23 to 25 nodes into
139. The game's list indexes are such names: delete the first thing in a place and every <code>PullThing(i)</code> after it means a different thing. So:</p>
<ul>
<li><b>Places are named by where they are,</b> and do not move: <code>world(start)(square(E4))(castle(N))(room(3))</code>.</li>
<li><b>A thing or person is named once, when it is made,</b> by its owner and a name unique there (<code>lever(L)</code>, or the next free
<code>shell(10)</code>), and keeps that name for good: it is an id, not a location.</li>
<li><b>Where it is now is a field:</b> <code>Placed(owner)</code>, <code>SetAside</code> (the world's buffer of things taken out, to be put back as
themselves), or <code>Carried(person)</code>.</li>
<li><b>A template is a kind,</b> placed nowhere: <code>place(castleroom).style(trap)</code>, <code>lever</code>, <code>person(costume(ninja))</code>.
Making an instance from it mints a name; putting a set-aside one back does not.</li>
</ul>
{fig(svg_life(), "Figure 7. An instance's life. It is made from a template and placed, may move to another owner, and may be set aside and put back, with the same name throughout. The game does this for people today (<code>state.peopleAway</code>, each with an optional place); a thing taken out of a place is simply gone.", "fig-life")}
{fig(svg_store(), "Figure 8. Fumola has a store whose cells are named by space and by time, each a nesting symbol. The game's state would use the space half: the current state, at nested addresses. It needs no symbolic time yet; the event log's three snapshots per event are where time would come in.", "fig-store")}

<h2 id="types">Globals, RuleState and Cmd, proposed</h2>
<p>In Hazel. First the addresses and what they name:</p>
<pre class="hz">{hazel_hl(PROPOSED_ADDR)}</pre>
<p>Then the whole game, each room's own state, and commands and events by address:</p>
<pre class="hz">{hazel_hl(PROPOSED_GLOBALS)}</pre>
<p>The commands get fewer and more general: one <code>Swing</code> for every hatch, lid and door, one <code>Set</code> for any setting, and
<code>Move</code>, which today's rules cannot do at all. Each names its target, so the game's <code>act</code> no longer has to check that a number means what
the rule meant. Today's, beside them:</p>
{mapping_table()}
<p>The tree room's rule becomes <code>| Pull(h) =&gt; Swing(h, !s.hatch.shut, Done)</code> with <code>s : TreeRoomState</code>: the same one line, now
saying which hatch.</p>

<h2 id="next">What next</h2>
<ul>
<li><b>Decide the symbol syntax</b> (calls, <code>world(start)(square(E4))</code>, as above) and the list of kinds, from the vocabulary table: one word each for a world,
a square, an inside, a room.</li>
<li><b>Give every placed thing a name</b> when it is placed (and the default world's {nthings} things one each), and keep it through moves; a thing's index stops
being its id.</li>
<li><b>Write <code>RuleState</code> for the tree room first,</b> the smallest, with the game building it from addresses, beside today's
<code>Globals</code>; then the trap room.</li>
<li><b>Add the world's buffer</b> of set-aside things, as <code>peopleAway</code> is for people.</li>
<li><b>Parse and print symbols in Hazel</b> (<code>parse_sym</code>, <code>print_sym</code>, supposed here): a rule writes <code>parse_sym("world(start)(square(E4))")</code> and gets the tree, with no constructor names.</li>
<li><b>Later, if strings and helper calls wear thin: symbol literals in Hazel,</b> as Fumola has today (<code>`world(`start)(`square(`E4))</code>): the parser reads the tree directly, so <code>parse_sym("...")</code> becomes a literal, checked when the program is, with its names highlighted in the tiles.</li>
<li><b>Show addresses in the event log,</b> so a change reads <code>…house(1).hatch: shut → open</code>.</li>
</ul>

<h2 id="how">How this was put together</h2>
<p>Written on 2026-10-25 by Claude, for Matthew, from <code class="ref"><b>^ticket(</b>609<b>)</b></code>. The game was read at
<code>{GAME}</code> (Messed Up Dress Up 0.0.429). The default world, the insides, castles and room styles were read from the game's own tables, run in node
(<code>data/places.json</code>); Figure 4 and the appendix are drawn from that file. The rooms' fields and types were read from
<code>dress-up/js/25-scripting.js</code> and <code>25-fumola.js</code>. The pictures in the appendix are the game's own drawings, from the
<a href="https://matthewhammer.org/dress-up-pictures/">dress-up-pictures</a> archive's newest run; things got a folder of their own there for this report.</p>

<h2 id="appendix">Appendix: every address</h2>
<p>Every place and placed thing of the default world, then the templates: places, castle room styles and people. Open a row to see the game's drawing of it
(fetched from the archive only then). A thing's number here is its order among its kind in that place, as a name would be minted; the game today knows it only
by its index in the place's list.</p>
{appendix_html()}
</main>
{APX_JS}
</body></html>"""
open(os.path.join(R, "index.html"), "w", encoding="utf-8").write(PAGE)
print(f"wrote 033/index.html: {len(PAGE):,} bytes; appendix {len(APX)} rows")
