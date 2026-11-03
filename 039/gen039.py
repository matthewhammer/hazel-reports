#!/usr/bin/env python3
"""^report(39), Hazlets, So Far: writes 039/index.html from body.html.

The status table is drawn from 039/data/status.json (written by hand, each
row with its as-of time); Figure 1 is drawn here. {{name}} in body.html is
a figure, the table or a value below. Then the series tools run over the
page (see build.sh)."""
import html, json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")

s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]

status = json.load(open(os.path.join(DATA, "status.json")))


def esc(s):
    return html.escape(s, quote=True)


# --- Figure 1: one event, and one edit, in the first Hazlet; each box's border is where it comes from ---

SRC = {"game": ("var(--accent2)", "the game's own JS"), "lib": ("var(--accent)", "the library (#2711, #2719)"),
       "rule": ("var(--good)", "the room's rule, in Hazel"), "tiles": ("var(--warn)", "the tiles' branch (embed-editable)")}


def fig_path():
    W = 940
    def box(x, y, w, h, title, lines, src, mono=()):
        col = SRC[src][0]
        o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="var(--paper)" stroke="{col}" stroke-width="2"/>',
             f'<text x="{x + 8}" y="{y + 17}" font-size="12" font-weight="700" fill="var(--ink)">{esc(title)}</text>']
        for i, l in enumerate(lines):
            fam = ' font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"' if i in mono else ""
            o.append(f'<text x="{x + 8}" y="{y + 34 + i * 14}" font-size="11"{fam} fill="var(--muted)">{esc(l)}</text>')
        return "\n".join(o)
    def arrow(x1, x2, y, back=False):
        o = [f'<line x1="{x1 + (4 if back else 0)}" x2="{x2 - 4}" y1="{y}" y2="{y}" stroke="var(--muted)" stroke-width="1.4"/>',
             f'<path d="M{x2 - 6},{y - 4} L{x2},{y} L{x2 - 6},{y + 4}" fill="none" stroke="var(--muted)" stroke-width="1.4"/>']
        if back:
            o.append(f'<path d="M{x1 + 6},{y - 4} L{x1},{y} L{x1 + 6},{y + 4}" fill="none" stroke="var(--muted)" stroke-width="1.4"/>')
        return "\n".join(o)
    o = [f'<svg viewBox="0 0 {W} 330" width="100%" role="img" aria-label="One event in Messed Up Dress Up: a lever pulled, the room&#39;s view and the event handed through the library to the room&#39;s Hazel rule, which answers commands the game acts out. One edit: a module&#39;s box and its tiles, Hazel.runProgram building the program, and the rooms running their JS while it is not ready.">']
    BH, G = 74, 18
    rows = [
        ("One event", 30, [(160, "the game (JS)", ["a red lever pulled:", "Pull(L)"], "game", (1,)),
                           (160, "the room's view", ["Globals: the levers,", "the wiring, the draws"], "game", ()),
                           (160, "the library", ["calls TrapRoom.on_event;", "values converted both ways"], "lib", ()),
                           (214, "the rule (Hazel)", ["answers a Cmd:", "Flip(L, SetPit(0, true, Done))"], "rule", (1,)),
                           (160, "the game acts", ["each command, as its own", "code would: lever, pit"], "game", ())]),
        ("One edit", 176, [(176, "the tiles, in a frame", ["Hazel's app: the module", "in tiles, error marks"], "tiles", ()),
                           (176, "📜 the module's box", ["Common, or one room;", "an edit from either side"], "game", ()),
                           (190, "Hazel.runProgram", ["the one program, built;", "errors, holes per module"], "lib", ()),
                           (206, "ready?", ["yes: each room's on_event", "no: the rooms run their JS"], "game", ())]),
    ]
    for label, y, bs in rows:
        o.append(f'<text x="0" y="{y - 10}" font-size="13" font-weight="700" fill="var(--ink)">{label}</text>')
        x = 0
        for i, (w, t, ls, src, mono) in enumerate(bs):
            o.append(box(x, y, w, BH, t, ls, src, mono))
            if i < len(bs) - 1:
                o.append(arrow(x + w, x + w + G, y + BH / 2, back=(label == "One edit" and i == 0)))
            x += w + G
    # the edit's handlers are what the next event calls
    o.append(f'<path d="M{176 + G + 176 + G + 190 + G + 103},{176} V{136} H{160 + G + 160 + G + 80} V{30 + BH + 4}" fill="none" stroke="var(--muted)" stroke-width="1.2" stroke-dasharray="4 3"/>'
             f'<path d="M{160 + G + 160 + G + 76},{30 + BH + 10} L{160 + G + 160 + G + 80},{30 + BH + 4} L{160 + G + 160 + G + 84},{30 + BH + 10}" fill="none" stroke="var(--muted)" stroke-width="1.2"/>'
             f'<text x="{160 + G + 160 + G + 88}" y="{130}" font-size="10.5" fill="var(--muted)">the handlers the next event calls</text>')
    x = 0
    for src in ("game", "lib", "rule", "tiles"):
        col, lab = SRC[src]
        o.append(f'<rect x="{x}" y="282" width="14" height="12" rx="3" fill="var(--paper)" stroke="{col}" stroke-width="2"/>'
                 f'<text x="{x + 20}" y="292" font-size="11.5" fill="var(--muted)">{esc(lab)}</text>')
        x += 22 + len(lab) * 6.4 + 18
    o.append('<text x="0" y="316" font-size="11.5" fill="var(--muted)">The trap room\'s rule, as the game ships it (0.0.474); Pull(L) with the pits wired normally.</text>')
    o.append("</svg>")
    return "\n".join(o)


def table_status():
    o = ['<div class="scroll"><table>', "<tr><th>Piece</th><th>State</th><th>As of</th><th>Ticket or PR</th></tr>"]
    for r in status["rows"]:
        o.append(f'<tr><td>{r["piece"]}</td><td><span class="st st-{r["tone"]}">●</span> {r["state"]}</td>'
                 f'<td class="n">{r["as_of"]}</td><td>{r["refs"]}</td></tr>')
    o.append("</table></div>")
    return "\n".join(o)


V = {"updated": subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip(),
     "status_as_of": status["as_of"]}
FIGS = {"FIG_PATH": fig_path(), "TABLE_STATUS": table_status()}
BODY = open(os.path.join(HERE, "body.html")).read()
BODY = re.sub(r"\{\{(\w+)\}\}", lambda m: FIGS.get(m.group(1)) or V[m.group(1)], BODY)
HEAD = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hazlets, So Far</title>
<meta name="description" content="A Hazlet is a JavaScript program whose event handlers are written in Hazel; Messed Up Dress Up is the first. What has been built since 2026-10-20 (the library on #2711 and #2719, tiles in a frame, the game's Scripting tab, hazeljs 0.0.1 on npm), where each piece stands, and what comes next.">
<style>{CSS}
  .st {{ font-size: 0.85em; }} .st-good {{ color: var(--good); }} .st-warn {{ color: var(--warn); }} .st-muted {{ color: var(--muted); }}
</style>
</head>
"""
open(os.path.join(HERE, "index.html"), "w").write(HEAD + BODY)
print("wrote 039/index.html;", ", ".join(f"{k}={v}" for k, v in V.items()))
