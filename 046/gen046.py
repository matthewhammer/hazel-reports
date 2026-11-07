#!/usr/bin/env python3
"""^report(46), BuckleScript, ReScript and Melange, beside hazel-jit (^ticket(698)): writes 046/index.html from body.html,
with the series' styles (035's), the timings drawn from 046/data/timings.json, and the code listings cut from the
compilers' own output in 046/data. Placeholders in body.html: {{updated}}, {{fig_speed}}, {{code:NAME}} (see CODE)."""
import html, json, os, re, statistics, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
from codehl import hazel_hl, js_hl, ml_hl, res_hl, HL_CSS, HL_INLINE_CSS  # noqa: E402  (Matthew, 2026-11-07: "syntax highlighting throughout")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
EXTRA = """
  ol.outline > li { margin: 4px 0; } .muted { color: var(--muted); }
  table.vals td:first-child { white-space: nowrap; }
  pre.code { background: color-mix(in srgb, var(--line) 35%, transparent); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px;
             overflow-x: auto; font-size: 0.8em; line-height: 1.45; max-width: 100%; }
  pre.code code { background: none; padding: 0; font-size: inherit; overflow-wrap: normal; white-space: pre; }
  .pair { display: grid; grid-template-columns: 1fr; gap: 10px; }
  .pair h4 { margin: 10px 0 2px; font-size: 0.95em; }
  table.vals.wrap1 td:first-child { white-space: normal; min-width: 9em; }
  /* (a narrow window: a wide table scrolls in its own box, not the page) */
  table.vals { display: block; overflow-x: auto; max-width: 100%; }
  .witchrow { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; margin: 12px 0; }
  .witchrow figure.witchcell { margin: 0; text-align: center; }
  .witchrow img { width: 100%; height: auto; display: block; border-radius: 6px; }
  .witchrow figcaption { font-size: 0.85em; }
"""
D = lambda name: open(os.path.join(HERE, "data", name)).read()
T = json.loads(D("timings.json"))


def js_function(src, name):
    """`function name(...) { ... }`, by its braces"""
    i = src.index(f"function {name}(")
    j = src.index("{", i)
    depth = 0
    for k in range(j, len(src)):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[i:k + 1]
    raise ValueError(name)


def hazel_rules():
    p = os.path.join(os.path.expanduser("~/hazel-694-jit"), "test", "petri", "Rules.hz")
    return open(p).read().strip()


def hazeljit_rules():
    src = D("hazeljit-petri.js")
    i = src.index("return def$75 = $R.fn(")
    j = src.index("on_event$94 = def$82")
    return "    " + src[i:j].strip().rstrip(",")


def jsoo_excerpt():
    p = "/tmp/claude-1000/-home-matthew-hazel/cd3317bd-52fb-4bc4-88e3-8887bfffd4ee/scratchpad/jsoo698/petri-g.js"
    lines = open(p).read().split("\n")
    k = next(i for i, l in enumerate(lines) if "cannot fire now" in l)
    return "\n".join(lines[k - 38: k + 6])


def between(src, start, stop=None):
    i = src.index(start)
    j = src.index(stop, i) if stop else len(src)
    return src[i:j].rstrip()


CODE = {
    "hazel": ("hazel", hazel_rules()),
    "res_src": ("rescript", between(D("Petri.res"), "let fire_at", "// the net")),
    "ml_src": ("ocaml", between(D("petri.ml"), "let fire_at", "let arc p")),
    "hazeljit": ("js", hazeljit_rules()),
    "rescript": ("js", js_function(D("Petri.res.js"), "fire_at") + "\n\n" + js_function(D("Petri.res.js"), "on_event")),
    "melange": ("js", js_function(D("petri-melange.js"), "fire_at") + "\n\n" + js_function(D("petri-melange.js"), "on_event")),
    "jsoo": ("js", jsoo_excerpt()),
    "hand": ("js", js_function(D("bench.mjs"), "jsHandler")),
}
os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
with open(os.path.join(HERE, "data", "jsoo-excerpt.js"), "w") as f:
    f.write(CODE["jsoo"][1] + "\n")


HL = {"hazel": (hazel_hl, "hz"), "ocaml": (ml_hl, "hz"), "rescript": (res_hl, "hz"), "js": (js_hl, "jx")}


def code(name):
    lang, src = CODE[name]
    hl, cls = HL[lang]
    return f'<pre class="code {cls}">' + hl(src) + "</pre>"


def inline(body):
    """every <code> in the text highlighted: as JS, or as Hazel (class hz) or OCaml (class ml), dark like the listings"""
    def one(m):
        cls, text = m.group(1) or "", html.unescape(m.group(2))
        if cls == "hz":
            return '<code class="hz">' + hazel_hl(text) + "</code>"
        if cls == "ml":
            return '<code class="hz">' + ml_hl(text) + "</code>"
        return '<code class="jx">' + js_hl(text) + "</code>"
    return re.sub(r'<code(?: class="(hz|ml|js)")?>(.*?)</code>', one, body)


def fig_speed():
    rows = [("Melange", "var(--accent)"), ("ReScript", "var(--accent)"), ("js_of_ocaml", "var(--accent2)"),
            ("hand-written JS", "var(--muted)"), ("hazel-jit", "var(--accent2)")]
    W, left, right = 940, 170, 150
    hi = 2.0
    xof = lambda v: left + v / hi * (W - left - right)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">One call of the Petri rule, µs: the median of 2,000 calls (the median of five runs), and the fastest</text>']
    y = 34
    for name, colour in rows:
        m, f = T["medians_us"][name], T["fastest_us"][name]
        out.append(f'<text x="{left - 10}" y="{y + 15}" font-size="12" text-anchor="end" fill="var(--ink)" font-weight="700">{html.escape(name)}</text>')
        out.append(f'<rect x="{left}" y="{y + 3}" width="{xof(m) - left:.1f}" height="16" rx="3" fill="{colour}" opacity="0.85"/>')
        out.append(f'<line x1="{xof(f):.1f}" y1="{y}" x2="{xof(f):.1f}" y2="{y + 22}" stroke="var(--ink)" stroke-width="1.6"/>')
        out.append(f'<text x="{xof(m) + 8:.1f}" y="{y + 15}" font-size="11.5" fill="var(--ink)" font-weight="700">{m:.2f} µs (fastest {f:.2f})</text>')
        y += 28
    for t in (0, 0.5, 1.0, 1.5, 2.0):
        out.append(f'<text x="{xof(t):.1f}" y="{y + 12}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{t:g}</text>')
    out.append(f'<text x="16" y="{y + 32}" font-size="11.5" fill="var(--muted)">Hazel\'s interpreter, on the same rule: {T["interpreter"]["us"]:.0f} µs a call, off this scale.</text>')
    h = y + 42
    alt = "; ".join(f"{n} {T['medians_us'][n]:.2f} µs a call" for n, _ in rows) + f"; the interpreter {T['interpreter']['us']:.0f} µs"
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{alt}" style="width:100%;height:auto;display:block">'
            + "".join(out) + "</svg><figcaption>Node 22.23.2, one laptop; each bar the median of five runs' medians, each tick the fastest single call. "
            "js_of_ocaml's in a process of its own, the rest in one.</figcaption></figure></div>")


def fig_speed_log():
    """(Matthew, 2026-11-07: "a second plot, where it's included, and we use a log scale horizontally") the same calls with
    Hazel's interpreter among them, on a log scale: each step to the right ten times as long"""
    import math
    rows = [("Melange", "var(--accent)"), ("ReScript", "var(--accent)"), ("js_of_ocaml", "var(--accent2)"),
            ("hand-written JS", "var(--muted)"), ("hazel-jit", "var(--accent2)"), ("the interpreter", "var(--warn, #b45309)")]
    W, left, right = 940, 170, 130
    lo, hi = math.log10(0.1), math.log10(1000)
    xof = lambda v: left + (math.log10(v) - lo) / (hi - lo) * (W - left - right)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">The same calls with Hazel\'s interpreter among them, µs a call, a log scale (each step to the right is ten times as long)</text>']
    y = 34
    bottom = 34 + len(rows) * 28
    for t in (0.1, 1, 10, 100, 1000):
        x = xof(t)
        out.append(f'<line x1="{x:.1f}" y1="28" x2="{x:.1f}" y2="{bottom:.0f}" stroke="var(--line)" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{bottom + 14}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{t:g} µs</text>')
    for name, colour in rows:
        m = T["medians_us"][name]
        out.append(f'<text x="{left - 10}" y="{y + 15}" font-size="12" text-anchor="end" fill="var(--ink)" font-weight="700">{html.escape(name)}</text>')
        out.append(f'<rect x="{left}" y="{y + 3}" width="{xof(m) - left:.1f}" height="16" rx="3" fill="{colour}" opacity="0.85"/>')
        out.append(f'<text x="{xof(m) + 8:.1f}" y="{y + 15}" font-size="11.5" fill="var(--ink)" font-weight="700">{m:.2f} µs</text>' if m < 100 else
                   f'<text x="{xof(m) + 8:.1f}" y="{y + 15}" font-size="11.5" fill="var(--ink)" font-weight="700">{m:.0f} µs</text>')
        y += 28
    h = bottom + 24
    alt = "On a log scale: " + "; ".join(f"{n} {T['medians_us'][n]:.2f} µs a call" for n, _ in rows)
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{alt}" style="width:100%;height:auto;display:block">'
            + "".join(out) + "</svg><figcaption>The medians of the chart above, and the interpreter's (" + f"{T['interpreter']['us']:.0f}"
            + " µs a call, Evaluator.evaluate_open, 200 calls). On this scale the compilers' bars differ by less than one step; the interpreter's is "
            "more than two steps longer than hazel-jit's.</figcaption></figure></div>")


NUMS = {k: f"{v:.2f}" for k, v in T["medians_us"].items()}
NUMS.update({"interp": f"{T['interpreter']['us']:.0f}",
             "hj_x_res": f"{T['medians_us']['hazel-jit'] / T['medians_us']['ReScript']:.1f}",
             "hj_x_hand": f"{T['medians_us']['hazel-jit'] / T['medians_us']['hand-written JS']:.1f}",
             "interp_x_hj": f"{T['interpreter']['us'] / T['medians_us']['hazel-jit']:.0f}"})


def keep(name, fig_html):
    """(Matthew, 2026-11-07: the agenda, ^report(42), shows the reports' plots) the figure's <svg>, kept as NNN/figs/NAME.html
    for 042/drivers/figs042.py to draw on an item's card; it uses the series' colour variables, so it is only for inlining"""
    m = re.search(r"<svg.*?</svg>", fig_html, re.S)
    os.makedirs(os.path.join(HERE, "figs"), exist_ok=True)
    open(os.path.join(HERE, "figs", name + ".html"), "w").write(m.group(0) + "\n")
    return fig_html

updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
body = open(os.path.join(HERE, "body.html")).read().replace("{{updated}}", updated).replace("{{fig_speed}}", keep("speed", fig_speed()))
body = body.replace("{{fig_speed_log}}", keep("speed-log", fig_speed_log()))
# the second program, the Witch slide's ^picture view (witch046.py): its figures, its drawings, its numbers
import witch046 as W  # noqa: E402
body = body.replace("{{fig_witch}}", keep("witch", W.fig_witch())).replace("{{fig_witch_frame}}", keep("witch-frame", W.fig_witch_frame()))
body = body.replace("{{witch_svgs}}", W.fig_witch_svgs())
body = body.replace("{{fig_witch_firefox}}", keep("witch-firefox", W.fig_witch_firefox()))
for k, v in W.WNUMS.items():
    body = body.replace("{{w:" + k + "}}", v)
WF = dict(W.WT["node_fastest_ms"], jsoo_tofixed=W.WT["jsoo_tofixed_fastest_ms"], jsoo_printf=W.WT["jsoo_printf_fastest_ms"])
for k, v in WF.items():
    body = body.replace("{{wf:" + k + "}}", f"{v:.2f}")
body = inline(body)
for k in CODE:
    body = body.replace("{{code:" + k + "}}", code(k))
for k, v in NUMS.items():
    body = body.replace("{{n:" + k + "}}", v)
assert "{{" not in body, body[body.index("{{"):body.index("{{") + 40]
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>BuckleScript, ReScript and Melange, beside hazel-jit</title>\n"
        "<meta name=\"description\" content=\"Two Hazel programs, report 043's Petri net rule and the Witch slide's picture view, compiled to JavaScript by ReScript, Melange, js_of_ocaml and hazel-jit: "
        "what each makes, how fast it runs, and what that suggests for hazel-jit.\">\n"
        "<style>" + CSS + EXTRA + HL_CSS + HL_INLINE_CSS + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
# (Matthew, 2026-11-07: the view's listings "separate into distinct pages, one per output") 046/witch/*.html
pages = W.write_pages(CSS + EXTRA, HL, HL_CSS, HL_INLINE_CSS, inline, updated)
print("wrote", len(pages), "pages in 046/witch")
print("wrote 046/index.html; updated", updated)
