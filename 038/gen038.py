#!/usr/bin/env python3
"""^report(38), Undo, in Time and Space: writes 038/index.html from body.html.

The space figures come from ^report(14)'s update (data/space.json), the step
times from ^report(36)'s probe (036/data/steps.json, its release build, after
the fixes), and the outline's part of each undo and redo from those times by
position and from new profiles (data/outline_kinds.json, by drivers/kinds.py). {{name}} in body.html is a
figure or a number from them. Then the series tools run over the page (see
build.sh)."""
import html, json, os, re, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")

s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]

space = json.load(open(os.path.join(DATA, "space.json")))
kinds = json.load(open(os.path.join(DATA, "outline_kinds.json")))["sizes"]
steps = json.load(open(os.path.join(ROOT, "036", "data", "steps.json")))
MED = {(r["n"], r["kind"]): r["step_median_ms"] for r in steps if r["build"] == "B"}
REC = {(r["n"], r["kind"]): r for r in steps if r["build"] == "B"}
SIZES = sorted({r["n"] for r in steps})


def fmt(v):
    return f"{v:,.0f}" if v >= 20 else f"{v:.1f}".rstrip("0").rstrip(".")


def esc(s):
    return html.escape(s, quote=True)


def at(n, kind, idx):
    # ^report(36)'s step times (after the fixes, release build) at these positions in each run of 4
    return [x["step_ms"] for x in REC[(n, kind)]["samples"] if x["index"] in idx]


# An undo rebuilds the outline every time. A redo finds it in the outline's memo of the last four programs, which
# the undos just filled, except the last redo, which restores the program from after the edits: no undo built that
# one. So the outline's rebuild is what an undo costs beyond a redo that finds its outline.
ROWS = []
for n in SIZES:
    e, u = MED[(n, "edit")], MED[(n, "undo")]
    hit = statistics.median(at(n, "redo", (1, 2, 3)))
    last = statistics.median(at(n, "redo", (4,)))
    o = u - hit
    k = kinds[str(n)]
    ROWS.append({"n": n, "edit": e, "undo": u, "redo": MED[(n, "redo")], "hit": hit, "last": last, "outline": o,
                 "share": o / u, "prof_share": k["undo"]["outline_ms"] / k["undo"]["step_ms"],
                 "prof_share_redo": k["redo"]["outline_ms"] / k["redo"]["step_ms"],
                 "hit_x": hit / e, "undo_x": u / e, "last_extra": last - hit})
BY = {x["n"]: x for x in ROWS}

# --- Figure 1: what the undo history kept after 12 edits, per build ---

SPACE_COL = {"asbuilt": "var(--bad)", "cap2": "var(--muted)", "compact": "var(--good)", "newest": "var(--accent)", "2635": "var(--accent2)"}


def fig_space(W=760, mini=False):
    rows = space["kept"]
    L, R, T, rh = (8, 70, 8, 30) if mini else (250, 90, 10, 40)
    H = T + rh * len(rows) + 22
    mx = 1100
    X = lambda v: L + v / mx * (W - L - R)
    o = []
    for v in ([0, 500, 1000] if mini else [0, 250, 500, 750, 1000]):
        o.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{H - 20}" stroke="var(--line)"/>'
                 f'<text x="{X(v):.1f}" y="{H - 6}" font-size="{11 if mini else 11.5}" text-anchor="middle" fill="var(--muted)">{v:,} MB</text>')
    for i, row in enumerate(rows):
        y = T + i * rh
        c = SPACE_COL[row["key"]]
        bh = rh - (12 if mini else 14)
        o.append(f'<rect x="{L}" y="{y + 4}" width="{X(row["kept_mb"]) - L:.1f}" height="{bh}" rx="3" fill="{c}"><title>{esc(row["build"])}: {row["kept_mb"]:,} MB kept after 12 edits, {row["growth_mb"]} MB more per edit</title></rect>'
                 f'<text x="{X(row["kept_mb"]) + 6:.1f}" y="{y + 4 + bh / 2 + 4:.1f}" font-size="{12 if mini else 13}" font-weight="700" fill="{c}">{row["kept_mb"]:,}</text>')
        if not mini:
            g = row["growth_mb"]
            o.append(f'<text x="{L - 10}" y="{y + 4 + bh / 2 - 2:.1f}" font-size="13" text-anchor="end" fill="var(--ink)">{esc(row["build"])}</text>'
                     f'<text x="{L - 10}" y="{y + 4 + bh / 2 + 12:.1f}" font-size="11" text-anchor="end" fill="var(--muted)">{"+" if g >= 0 else "&minus;"}{abs(g)} MB per edit</text>')
    lab = "MB kept after 12 edits on Full Body, by build" if not mini else ""
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{lab or "MB kept after 12 edits, five builds"}" style="width:100%;height:auto">'
            + "".join(o) + "</svg>")


# --- Figure 2: each step at each size, the undo's and redo's outline part marked ---

def fig_split(W=900, mini=False, sizes=None):
    sizes = sizes or SIZES
    pw = W / len(sizes)
    H = 240 if not mini else 180
    T, B = 30, 44
    KIND = (("edit", "edit", "var(--accent2)"), ("undo", "undo", "var(--accent)"),
            ("hit", "redo", "var(--warn)"), ("last", "last redo", "var(--warn)"))
    o = []
    for j, n in enumerate(sizes):
        x0 = j * pw
        row = BY[n]
        top = max(row["undo"], row["last"], row["edit"]) * 1.14
        Y = lambda v: T + (1 - v / top) * (H - T - B)
        o.append(f'<text x="{x0 + pw / 2:.1f}" y="16" font-size="{12.5 if not mini else 13}" font-weight="700" text-anchor="middle" fill="var(--ink)">{n:,} definitions</text>')
        o.append(f'<line x1="{x0 + 8:.1f}" x2="{x0 + pw - 8:.1f}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" stroke="var(--line)"/>')
        bw = (pw - 24) / 4 - 5
        for i, (key, lab, col) in enumerate(KIND):
            bx = x0 + 12 + i * (bw + 6)
            v = row[key]
            ol = min(row["outline"], v) if key in ("undo", "last") else 0
            rest = v - ol
            o.append(f'<rect x="{bx:.1f}" y="{Y(rest):.1f}" width="{bw:.1f}" height="{Y(0) - Y(rest):.1f}" fill="{col}" rx="2"><title>{n:,} definitions, {lab}: {fmt(v)} ms</title></rect>')
            if ol:
                o.append(f'<rect x="{bx:.1f}" y="{Y(v):.1f}" width="{bw:.1f}" height="{Y(rest) - Y(v):.1f}" fill="none" stroke="{col}" stroke-width="1.5" stroke-dasharray="3 2" rx="2"><title>the outline, rebuilt: about {fmt(row["outline"])} ms</title></rect>')
            o.append(f'<text x="{bx + bw / 2:.1f}" y="{Y(v) - 4:.1f}" font-size="{10.5 if not mini else 12}" text-anchor="middle" fill="var(--ink)">{fmt(v)}</text>')
            for t, line in enumerate(lab.split(" ")):
                o.append(f'<text x="{bx + bw / 2:.1f}" y="{H - B + 14 + t * 12}" font-size="{10.5 if not mini else 12}" text-anchor="middle" fill="var(--muted)">{line}</text>')
    o.append(f'<text x="{W / 2:.1f}" y="{H - 4}" font-size="11.5" text-anchor="middle" fill="var(--muted)">ms per step, each size on its own scale; the dashed top is the outline\'s rebuild</text>')
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="An edit, an undo, a redo and the last redo at each size, the outline\'s rebuild marked" style="width:100%;height:auto">' + "".join(o) + "</svg>"


# --- the tables ---

def table_space():
    h = "<table><thead><tr><th>Build</th><th>What it changes</th><th>Runs</th><th>Kept after 12 edits, MB</th><th>Growth per edit, edits 4–12, MB</th></tr></thead><tbody>"
    for r in space["kept"]:
        c = f' ({r["commit"]})' if r["commit"] else ""
        kept = "284 and 284" if r["key"] == "cap2" else f'{r["kept_mb"]:,}'
        g = "4.4 and 4.2" if r["key"] == "cap2" else f'{r["growth_mb"]}'
        h += f'<tr><td>{esc(r["build"])}{c}</td><td>{esc(r["what"])}</td><td>{r["runs"]}</td><td>{kept}</td><td>{g}</td></tr>'
    return h + "</tbody></table>"


def table_times():
    h = "<table><thead><tr><th>Build</th><th>Edit, s</th><th>Undo, s</th><th>Redo, s</th></tr></thead><tbody>"
    for r in space["times_s"]["rows"]:
        h += f'<tr><td>{esc(r["build"])}</td><td>{r["edit"].replace("-", "–")}</td><td>{r["undo"].replace("-", "–")}</td><td>{r["redo"].replace("-", "–")}</td></tr>'
    return h + "</tbody></table>"


def table_split():
    h = ("<table><thead><tr><th>definitions</th><th>an edit</th><th>an undo</th><th>a redo that finds its outline (the first three)</th>"
         "<th>the last redo</th><th>the outline: undo minus redo</th><th>its share of an undo</th><th>the profile's share of an undo (2 runs)</th>"
         "<th>a redo that finds its outline, in edits</th></tr></thead><tbody>")
    for x in ROWS:
        h += (f'<tr><td>{x["n"]:,}</td><td>{fmt(x["edit"])}</td><td>{fmt(x["undo"])}</td><td>{fmt(x["hit"])}</td><td>{fmt(x["last"])}</td>'
              f'<td>{fmt(x["outline"])}</td><td>{x["share"] * 100:.0f}%</td><td>{x["prof_share"] * 100:.0f}%</td><td>{x["hit_x"]:.1f}</td></tr>')
    return h + "</tbody></table>"


# --- numbers for the prose ---

V = {}
k = {r["key"]: r for r in space["kept"]}
for key, r in k.items():
    V[f"kept_{key}"] = f'{r["kept_mb"]:,}'
    V[f"grow_{key}"] = f'{r["growth_mb"]}'
V["kept_ratio"] = f'{k["asbuilt"]["kept_mb"] / k["compact"]["kept_mb"]:.1f}'
for n in SIZES:
    x = BY[n]
    for f in ("edit", "undo", "redo", "hit", "last", "outline"):
        V[f"{f}_{n}"] = fmt(x[f])
    V[f"hit_x_{n}"] = f'{x["hit_x"]:.1f}'
    V[f"undo_x_{n}"] = f'{x["undo_x"]:.1f}'
big = [n for n in SIZES if n >= 1600]
V["share_lo"], V["share_hi"] = f'{min(BY[n]["share"] for n in big) * 100:.0f}', f'{max(BY[n]["share"] for n in big) * 100:.0f}'
V["pshare_lo"], V["pshare_hi"] = f'{min(x["prof_share"] for x in ROWS) * 100:.0f}', f'{max(x["prof_share"] for x in ROWS) * 100:.0f}'
V["pshare_redo_lo"], V["pshare_redo_hi"] = f'{min(x["prof_share_redo"] for x in ROWS) * 100:.0f}', f'{max(x["prof_share_redo"] for x in ROWS) * 100:.0f}'
V["hitx_lo"], V["hitx_hi"] = f'{min(BY[n]["hit_x"] for n in big):.1f}', f'{max(BY[n]["hit_x"] for n in big):.1f}'
SYN = json.load(open(os.path.join(DATA, "outline_kinds.json")))["syntax_ms"]
V["redo_syn_3200"], V["edit_syn_3200"] = f'{SYN["3200"]["redo"]:,}', f'{SYN["3200"]["edit"]:,}'
FIGS = {"FIG_SPACE": fig_space(), "FIG_SPACE_MINI": fig_space(W=300, mini=True),
        "FIG_SPLIT": fig_split(), "FIG_SPLIT_MINI": fig_split(W=300, mini=True, sizes=[3200]),
        "TABLE_SPACE": table_space(), "TABLE_TIMES": table_times(), "TABLE_SPLIT": table_split()}
BODY = open(os.path.join(HERE, "body.html")).read()
BODY = re.sub(r"\{\{(\w+)\}\}", lambda m: FIGS.get(m.group(1)) or V[m.group(1)], BODY)
HEAD = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Undo, in Time and Space</title>
<meta name="description" content="What undo costs in Hazel's editor. Space: an uncapped history of whole editor states kept {V['kept_asbuilt']} MB after 12 edits on #2597, {V['kept_compact']} with Andrew Blinn's compaction; how that was found. Time: every step linear in the program; an undo is a redo plus a rebuild of the modular editors' outline, a third of the undo. Where it stands and what is next.">
<style>{CSS}
</style>
</head>
"""
open(os.path.join(HERE, "index.html"), "w").write(HEAD + BODY)
print("wrote 038/index.html;", ", ".join(f"{k}={v}" for k, v in V.items() if not k.startswith(("edit_", "undo_", "redo_", "outline_"))))
