#!/usr/bin/env python3
"""^report(46), BuckleScript, ReScript and Melange, beside hazel-jit (^ticket(698)): writes 046/index.html from body.html,
with the series' styles (035's), the timings drawn from 046/data/timings.json, and the code listings cut from the
compilers' own output in 046/data. Placeholders in body.html: {{updated}}, {{fig_speed}}, {{code:NAME}} (see CODE)."""
import html, json, os, re, statistics, subprocess

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


CODE = {
    "hazel": ("hazel", hazel_rules()),
    "hazeljit": ("js", hazeljit_rules()),
    "rescript": ("js", js_function(D("Petri.res.js"), "fire_at") + "\n\n" + js_function(D("Petri.res.js"), "on_event")),
    "melange": ("js", js_function(D("petri-melange.js"), "fire_at") + "\n\n" + js_function(D("petri-melange.js"), "on_event")),
    "jsoo": ("js", jsoo_excerpt()),
    "hand": ("js", js_function(D("bench.mjs"), "jsHandler")),
}
os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
with open(os.path.join(HERE, "data", "jsoo-excerpt.js"), "w") as f:
    f.write(CODE["jsoo"][1] + "\n")


def code(name):
    _, src = CODE[name]
    return '<pre class="code"><code>' + html.escape(src) + "</code></pre>"


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


NUMS = {k: f"{v:.2f}" for k, v in T["medians_us"].items()}
NUMS.update({"interp": f"{T['interpreter']['us']:.0f}",
             "hj_x_res": f"{T['medians_us']['hazel-jit'] / T['medians_us']['ReScript']:.1f}",
             "hj_x_hand": f"{T['medians_us']['hazel-jit'] / T['medians_us']['hand-written JS']:.1f}",
             "interp_x_hj": f"{T['interpreter']['us'] / T['medians_us']['hazel-jit']:.0f}"})

updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
body = open(os.path.join(HERE, "body.html")).read().replace("{{updated}}", updated).replace("{{fig_speed}}", fig_speed())
for k in CODE:
    body = body.replace("{{code:" + k + "}}", code(k))
for k, v in NUMS.items():
    body = body.replace("{{n:" + k + "}}", v)
assert "{{" not in body, body[body.index("{{"):body.index("{{") + 40]
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>BuckleScript, ReScript and Melange, beside hazel-jit</title>\n"
        "<meta name=\"description\" content=\"One small program, report 043's Petri net rule, compiled to JavaScript by ReScript, Melange, js_of_ocaml and hazel-jit: "
        "what each makes, how fast it runs, and what that suggests for hazel-jit.\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
print("wrote 046/index.html; updated", updated)
