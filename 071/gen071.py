#!/usr/bin/env python3
"""^report(71): Lists as Arrays in hazel-jit. ^ticket(909) (Matthew, 2026-11-28): "we want arrays for lists, whenever possible";
"let's write a report about this issue (representing lists as arrays), including the current status and next steps".

Writes 071/index.html, 071/data/meta.json and 071/img/thumb*.svg from:
  data/pane.json              the browser pane on the laptop: Gnome world's Hazel calls, crossing and compiled work; the
                              integer experiment on Folk.bug (written by hand from the pane's answers)
  data/lists-bench-054.json   ^report(54)'s lists microbenchmark (054/drivers/lists-bench.mjs, 2026-11-23)"""
import html, json, math, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(HERE, "data")
s35 = open(os.path.join(ROOT, "035", "index.html")).read(); CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
E = lambda s: html.escape(str(s), quote=True)
P = json.load(open(os.path.join(DATA, "pane.json"))); LB = json.load(open(os.path.join(DATA, "lists-bench-054.json")))
SVGST = '<style>.l{fill:var(--ink);font:600 13px system-ui,sans-serif}.m{fill:var(--muted);font:12px system-ui,sans-serif}</style>'
C = P["crossing"]; ORDER = ["water_down", "water_across", "rivers_hold", "rivers_rain", "rivers_pump", "rivers_dry", "folk_walk", "folk_hawk", "folk_squirrel", "folk_bug", "way"]
pct = lambda k: 100 * C[k]["crossing_us"] / (C[k]["crossing_us"] + C[k]["compiled_us"])
def us(x): return f"{x:,.0f}" if x >= 100 else f"{x:.1f}" if x >= 10 else f"{x:.2f}"

def fig_cost():
    W, L, bw = 960, 330, 470; lo, hi = math.log10(0.05), math.log10(3000); X = lambda v: L + bw * (math.log10(max(v, 0.05)) - lo) / (hi - lo)
    rh = 40; Hh = 34 + rh * len(ORDER) + 28
    o = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="Each Hazel call in Gnome world: its crossing and its compiled work, microseconds, log scale">', SVGST]
    for t in [0.1, 1, 10, 100, 1000]:
        x = X(t); o.append(f'<line x1="{x:.1f}" y1="22" x2="{x:.1f}" y2="{Hh - 26}" stroke="var(--line)"/><text class="m" x="{x - 10:.1f}" y="16">{t:g} µs</text>')
    y = 28
    for k in ORDER:
        c = C[k]; o.append(f'<text class="m" x="8" y="{y + 15}">{E(c["what"])}</text><text class="m" x="8" y="{y + 29}">{c["elements"]:,} elements in</text>')
        o.append(f'<rect x="{L}" y="{y + 4}" width="{X(c["crossing_us"]) - L:.1f}" height="13" fill="var(--warn)"><title>crossing {c["crossing_us"]} µs</title></rect><text class="m" x="{X(c["crossing_us"]) + 5:.1f}" y="{y + 15}">{us(c["crossing_us"])} · {pct(k):.0f}%</text>')
        o.append(f'<rect x="{L}" y="{y + 19}" width="{X(c["compiled_us"]) - L:.1f}" height="13" fill="var(--accent)"><title>compiled {c["compiled_us"]} µs</title></rect><text class="m" x="{X(c["compiled_us"]) + 5:.1f}" y="{y + 30}">{us(c["compiled_us"])}</text>')
        y += rh
    o.append(f'<rect x="{L}" y="{Hh - 18}" width="12" height="10" fill="var(--warn)"/><text class="m" x="{L + 16}" y="{Hh - 9}">crossing (and its share of the call)</text><rect x="{L + 250}" y="{Hh - 18}" width="12" height="10" fill="var(--accent)"/><text class="m" x="{L + 266}" y="{Hh - 9}">compiled work</text></svg>')
    return "".join(o)
def t_cost():
    h = '<div class="wrap"><table class="nums"><thead><tr><th class="l">call</th><th>elements in, fresh</th><th>crossing</th><th>compiled work</th><th>crossing’s share</th></tr></thead><tbody>'
    for k in ORDER:
        c = C[k]; h += f'<tr><td class="l">{E(c["what"])}</td><td>{c["elements"]:,}</td><td>{us(c["crossing_us"])} µs</td><td>{us(c["compiled_us"])} µs</td><td>{pct(k):.0f}%</td></tr>'
    return h + "</tbody></table></div>"
def t_shapes():
    rows = [("a number, a boolean, a string", "the same", "the same", "a check of its kind"),
            ("a record of plain values", "an object", "the same object", "each field checked, nothing copied (^ticket(847))"),
            ("a record holding a list or a sum", "an object", "a new object", "its fields converted, remembered by a link"),
            ("a list", "an array", "cells <code>{$h, $t}</code>, <code>null</code> for <code>[]</code>", "<b>rebuilt both ways</b>; remembered when 16 elements or more"),
            ("a constructor", "<code>{tag, value}</code>", "<code>{$c, $v}</code>", "renamed both ways")]
    return ('<div class="wrap"><table class="nums"><thead><tr><th class="l">a value of type</th><th class="l">the page holds</th><th class="l">compiled code holds</th><th class="l">crossing</th></tr></thead><tbody>'
            + "".join(f'<tr><td class="l">{a}</td><td class="l">{b}</td><td class="l">{c}</td><td class="l">{d}</td></tr>' for a, b, c, d in rows) + "</tbody></table></div>")
I = P["ints"]
def t_ints():
    h = '<table class="nums"><thead><tr><th class="l">Folk.bug, compiled, an insect</th><th>as compiled</th><th>plain-number Ints</th><th>no fuel checks</th><th>both</th></tr></thead><tbody>'
    for k, n in [("drawing", "drawing its chances (most steps)"), ("quiet", "waiting, no chances drawn")]:
        r = I[k]; h += f'<tr><td class="l">{n}</td><td>{r["as compiled"]:.2f} µs</td><td>{r["plain-number Ints"]:.2f} µs</td><td>{r["no fuel checks"]:.2f} µs</td><td>{r["both"]:.2f} µs</td></tr>'
    return h + f'</tbody></table><p class="note">The page’s own JavaScript: about {I["js_twin_us"]} µs an insect. Plain-number Ints are for this measurement only: past 2<sup>53</sup> they are not exact.</p>'
def t_micro():
    rows = [r for r in LB["rows"] if r["n"] == 1000]
    h = '<div class="wrap"><table class="nums"><thead><tr><th class="l">a list of 1,000 Ints, compiled</th><th>cells (today)</th><th>arrays, copied by <code>::</code></th><th>the hybrid</th></tr></thead><tbody>'
    for r in rows: h += f'<tr><td class="l">{E(r["workload"])}</td><td>{us(r["cells"])} µs</td><td>{us(r["arrays"])} µs</td><td>{us(r["hybrid"])} µs</td></tr>'
    return h + f'</tbody></table></div><p class="note">^report(54), Node {E(LB["node"])} on the laptop, {E(LB["when"][:10])}; each the median of batches.</p>'

FIG = {"fig_cost": fig_cost(), "t_cost": t_cost(), "t_shapes": t_shapes(), "t_ints": t_ints(), "t_micro": t_micro()}
shares = sorted(pct(k) for k in ORDER)
N = {"x_lo": f"{shares[0]:.0f}%", "x_hi": f"{shares[-1]:.0f}%", "water_down_pct": f'{pct("water_down"):.0f}%', "hold_pct": f'{pct("rivers_hold"):.0f}%',
     "ints_before": f'{I["drawing"]["as compiled"]:.1f}', "ints_after": f'{I["drawing"]["plain-number Ints"]:.1f}',
     "quiet_before": f'{I["quiet"]["as compiled"]:.1f}', "quiet_after": f'{I["quiet"]["plain-number Ints"]:.1f}', "js_twin": I["js_twin_us"], "updated": updated}
FIG.update(N)
body = open(os.path.join(HERE, "body.html"), encoding="utf-8").read()
for k, v in FIG.items(): body = body.replace("{{" + k + "}}", str(v))
left = re.findall(r"\{\{(\w+)\}\}", body); assert not left, left
TITLE = "Lists as Arrays in hazel-jit"
DESC = (f"Compiled Hazel keeps a list as cells, so every call converts a page's arrays to cells and back: in Gnome world that is {N['x_lo']} to {N['x_hi']} of a Hazel call's time. "
        "A hybrid from 11-23 (cells for ::, array segments for a page's arrays) was not merged; since then crossing goes by declared type, and the lists are what is left. "
        f"Status and next steps; and the rest of the gap: exact Ints ({N['ints_before']} µs an insect, {N['ints_after']} with plain numbers), for JSNum.")
EXTRA = """
  figure.chart svg { width: 100%; height: auto; display: block; }
  table.nums td, table.nums th { text-align: right; font-variant-numeric: tabular-nums; } table.nums td.l, table.nums th.l { text-align: left; }
  .wrap { overflow-x: auto; } p.note { font-size: 0.9em; color: var(--muted); }
"""
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{E(DESC)}\">\n<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(head + body)

def thumb(mode):
    base = ".h{fill:#1f2328;font:700 15px system-ui,sans-serif}.m{fill:#5b6470;font:10px system-ui,sans-serif}.k{fill:#1f2328;font:700 11px system-ui,sans-serif}.c{fill:#b45309}.z{fill:#6d28d9}"
    dark = ".h{fill:#e8e6e3}.m{fill:#a2a9b3}.k{fill:#e8e6e3}.c{fill:#fbbf24}.z{fill:#c4b5fd}"
    style = base + ("\n" + dark if mode == "dark" else "\n@media (prefers-color-scheme: dark) {" + dark + "}" if mode == "auto" else "")
    rows = [("Water.down, a block", C["water_down"]), ("Rivers.hold, a river", C["rivers_hold"]), ("Rivers.dry, 897 columns", C["rivers_dry"])]
    out = []
    for i, (n, c) in enumerate(rows):
        y = 60 + i * 40; tot = c["crossing_us"] + c["compiled_us"]; wc = 240 * c["crossing_us"] / tot
        out.append(f'<text class="m" x="16" y="{y - 4}">{n}</text><rect class="c" x="16" y="{y}" width="{wc:.1f}" height="14"/><rect class="z" x="{16 + wc:.1f}" y="{y}" width="{240 - wc:.1f}" height="14"/><text class="k" x="262" y="{y + 11}">{100 * c["crossing_us"] / tot:.0f}%</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" width="320" height="200">\n<style>{style}\n</style>\n'
            '<text class="h" x="16" y="26">Lists as arrays in hazel-jit</text>\n<text class="m" x="16" y="42">a call’s time: crossing (amber) and compiled work</text>\n'
            + "".join(out) + '\n<text class="m" x="16" y="186">next: the hybrid of cells and array segments</text>\n</svg>\n')
for name, mode in [("thumb-light.svg", "light"), ("thumb-dark.svg", "dark"), ("thumb.svg", "auto")]: open(os.path.join(HERE, "img", name), "w").write(thumb(mode))
meta = {"title": TITLE, "blurb": DESC, "builds": {"Gnome world": "0.0.156 (hazeljs-examples 97fccb2)", "hazel-jit": "hazeljs branch 0f24cea171 (the page); trial/1126-night abf653a21d (the AOT file)", "hybrid": "hazel-jit-lists bba0a9c005, f4a3e3b082 (2026-11-23)"},
        "runs": {"pane": P["where"], "recorded": P["recorded"], "microbenchmark": "^report(54) lists-bench.mjs, " + LB["when"]},
        "measures": {"crossing": "the converters in and out around a stub that returns the compiled answer, a mean a call", "compiled work": "the compiled function alone with the converters' own arguments"},
        "files": ["data/pane.json", "data/lists-bench-054.json", "gen071.py"]}
json.dump(meta, open(os.path.join(DATA, "meta.json"), "w"), indent=1, ensure_ascii=False)
print("wrote 071/index.html;", updated)
for k in sorted(N): print(f"  {k}: {N[k]}")
