"""^report(46)'s second program: the Witch slide's ^picture view, compiled by hazel-jit, ReScript, Melange and
js_of_ocaml, and written by hand (Matthew, 2026-11-07: "measure the most complex view function of our livelits slide
deck ... and compare"). gen046.py imports this: the numbers ({{w:NAME}}), the figures, the drawings, and one page per
compiler's output in 046/witch/ ("separate into distinct pages, one per output"). Every number is from
046/data/witch/timings.json; a view's time is given with its frames a second in parens, as if updating the state were
free, against 60 fps, a 16.7 ms frame, as the floor (Matthew, 2026-11-07)."""
import html, json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
DW = lambda name: open(os.path.join(HERE, "data", "witch", name)).read()
WT = json.loads(DW("timings.json"))
NODE = WT["node_medians_ms"]
APP = WT["app"]
FRAME_60 = 1000 / 60


def fps(ms):
    """frames a second, to two figures: a timing's third figure is noise"""
    f = 1000 / ms
    if f >= 1000:
        return f"{round(f, -2):,.0f}"
    return f"{round(f, -1):,.0f}" if f >= 100 else f"{f:.0f}"


def ms(x):
    return f"{x:.2f}" if x < 10 else f"{x:.0f}"


# the rows of the view's own work, one Node process: name, ms, colour
ROWS = [("hand-written JS", NODE["hand-written JS"], "var(--muted)"),
        ("Melange", NODE["Melange"], "var(--accent)"),
        ("ReScript", NODE["ReScript"], "var(--accent)"),
        ("js_of_ocaml, toFixed", WT["jsoo_tofixed_ms"], "var(--accent2)"),
        ("hazel-jit", NODE["hazel-jit"], "var(--accent2)"),
        ("js_of_ocaml, Printf", WT["jsoo_printf_ms"], "var(--warn, #b45309)")]

WNUMS = {
    "hj": f"{NODE['hazel-jit']:.2f}", "res": f"{NODE['ReScript']:.2f}", "mel": f"{NODE['Melange']:.2f}",
    "hand": f"{NODE['hand-written JS']:.2f}", "jsoo_tf": f"{WT['jsoo_tofixed_ms']:.2f}", "jsoo_pf": f"{WT['jsoo_printf_ms']:.2f}",
    "hj_fps": fps(NODE["hazel-jit"]), "res_fps": fps(NODE["ReScript"]), "mel_fps": fps(NODE["Melange"]),
    "hand_fps": fps(NODE["hand-written JS"]), "jsoo_tf_fps": fps(WT["jsoo_tofixed_ms"]), "jsoo_pf_fps": fps(WT["jsoo_printf_ms"]),
    "hj_x_hand": f"{(NODE['hazel-jit'] / NODE['hand-written JS'] - 1) * 100:.0f}",
    "hj_x_res": f"{(NODE['hazel-jit'] / NODE['ReScript'] - 1) * 100:.0f}",
    "pf_x_tf": f"{WT['jsoo_printf_ms'] / WT['jsoo_tofixed_ms']:.1f}",
    "tofixed": f"{WT['toFixed_alone_ms']:.2f}", "tofixed_calls": f"{WT['toFixed_calls']:,}",
    "tofixed_share": f"{WT['toFixed_alone_ms'] / NODE['hand-written JS'] * 100:.0f}",
    "interp": ms(APP["interpreter_view_ms"]), "interp_fps": fps(APP["interpreter_view_ms"]),
    "interp_eval": f"{APP['interpreter_eval_ms']:.1f}",
    "frame": f"{APP['frame_ms']:.1f}", "frame_fps": fps(APP["frame_ms"]),
    "app_view": f"{APP['view_work_ms']:.2f}", "app_view_fps": fps(APP["view_work_ms"]),
    "trip_in": f"{APP['trip_in_ms']:.2f}", "direct": f"{APP['direct_draw_ms']:.2f}", "draw_only": f"{APP['draw_only_ms']:.2f}",
    "interp_x_frame": f"{APP['interpreter_view_ms'] / APP['frame_ms']:.0f}",
    "interp_x_app_view": f"{APP['interpreter_view_ms'] / APP['view_work_ms']:.0f}",
    "frames_late": f"{APP['interpreter_view_ms'] / FRAME_60:.0f}",
    "frame_left": f"{FRAME_60 - APP['frame_ms']:.0f}",
    "compile": f"{APP['compile_ms']:.1f}",
    "app_over_node": f"{APP['view_work_ms'] / NODE['hazel-jit']:.0f}",
    "shapes": "133", "points": "924", "svg_chars": f"{WT['picture']['svg_chars']:,}",
}


def fig_witch():
    """the view's own work, each compiler, one Node process, to scale; the time toFixed alone takes, dashed"""
    W, left, right = 940, 190, 210
    hi = 1.1
    xof = lambda v: left + v / hi * (W - left - right)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">The Witch\'s picture: the view\'s own work, ms '
           '(and frames a second, as if updating the state were free)</text>']
    y = 34
    for name, v, colour in ROWS:
        out.append(f'<text x="{left - 10}" y="{y + 15}" font-size="12" text-anchor="end" fill="var(--ink)" font-weight="700">{html.escape(name)}</text>')
        out.append(f'<rect x="{left}" y="{y + 3}" width="{xof(v) - left:.1f}" height="16" rx="3" fill="{colour}" opacity="0.85"><title>{html.escape(name)}: {v:.3f} ms</title></rect>')
        out.append(f'<text x="{xof(v) + 8:.1f}" y="{y + 15}" font-size="11.5" fill="var(--ink)" font-weight="700">{v:.2f} ms ({fps(v)} fps)</text>')
        y += 28
    tf = xof(WT["toFixed_alone_ms"])
    out.append(f'<line x1="{tf:.1f}" y1="30" x2="{tf:.1f}" y2="{y + 2}" stroke="var(--ink)" stroke-width="1.4" stroke-dasharray="4 3"/>')
    out.append(f'<text x="{tf + 4:.1f}" y="{y + 14}" font-size="11" fill="var(--ink)">toFixed alone, {WT["toFixed_calls"]:,} calls: {WT["toFixed_alone_ms"]:.2f} ms</text>')
    for t in (0, 0.25, 0.5, 0.75, 1.0):
        out.append(f'<text x="{xof(t):.1f}" y="{y + 32}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{t:g}</text>')
    h = y + 42
    alt = "; ".join(f"{n} {v:.2f} ms ({fps(v)} fps)" for n, v, _ in ROWS) + f"; toFixed alone {WT['toFixed_alone_ms']:.2f} ms"
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{alt}" style="width:100%;height:auto;display:block">'
            + "".join(out) + "</svg><figcaption>Node 22.23.2, one laptop: from the picture, as each language holds it, to the Html the view "
            "returns, as each holds it. Each bar the median of three runs, each run the median of five rounds of 200 calls; "
            "js_of_ocaml's in a process of its own, five runs. The dashed line is the same 1,985 numbers formatted with "
            "<code>toFixed(1)</code> and nothing else.</figcaption></figure></div>")


def fig_witch_frame():
    """(Matthew, 2026-11-07: 60 fps "as the 'min floor' we want to achieve") one frame of the Witch's picture in the app's
    terms, on a log scale, against a 60 fps frame"""
    rows = [("the interpreter", "its view, command and drawing", APP["interpreter_view_ms"], "var(--warn, #b45309)"),
            ("hazel-jit, the app", "model in, view, drawing", APP["frame_ms"], "var(--accent2)"),
            ("hazel-jit's view", "in the app's process", APP["view_work_ms"], "var(--accent2)"),
            ("hazel-jit's view", "in a Node process alone", NODE["hazel-jit"], "var(--accent)")]
    W, left, right = 940, 200, 150
    lo, hi = math.log10(0.1), math.log10(300)
    xof = lambda v: left + (math.log10(v) - lo) / (hi - lo) * (W - left - right)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">One frame of the Witch\'s picture, ms on a log scale, '
           'against a 60 fps frame (16.7 ms)</text>']
    top, step = 34, 34
    bottom = top + len(rows) * step
    for t in (0.1, 1, 10, 100):
        x = xof(t)
        out.append(f'<line x1="{x:.1f}" y1="28" x2="{x:.1f}" y2="{bottom:.0f}" stroke="var(--line)" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{bottom + 14}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{t:g} ms</text>')
    x60 = xof(FRAME_60)
    out.append(f'<rect x="{left}" y="28" width="{x60 - left:.1f}" height="{bottom - 28:.0f}" fill="var(--good, #2e7d32)" opacity="0.07"/>')
    out.append(f'<line x1="{x60:.1f}" y1="26" x2="{x60:.1f}" y2="{bottom + 2:.0f}" stroke="var(--good, #2e7d32)" stroke-width="2"/>')
    out.append(f'<text x="{x60 + 5:.1f}" y="{bottom + 14}" font-size="11" fill="var(--good, #2e7d32)" font-weight="700">60 fps, 16.7 ms</text>')
    y = top
    for name, sub, v, colour in rows:
        out.append(f'<text x="{left - 10}" y="{y + 11}" font-size="12" text-anchor="end" fill="var(--ink)" font-weight="700">{html.escape(name)}</text>')
        out.append(f'<text x="{left - 10}" y="{y + 24}" font-size="10.5" text-anchor="end" fill="var(--muted)">{html.escape(sub)}</text>')
        out.append(f'<rect x="{left}" y="{y + 4}" width="{xof(v) - left:.1f}" height="16" rx="3" fill="{colour}" opacity="0.85"><title>{name}, {sub}: {v:.2f} ms</title></rect>')
        out.append(f'<text x="{xof(v) + 8:.1f}" y="{y + 16}" font-size="11.5" fill="var(--ink)" font-weight="700">{ms(v)} ms ({fps(v)} fps)</text>')
        y += step
    h = bottom + 24
    alt = "Against a 60 fps frame of 16.7 ms: " + "; ".join(f"{n}, {s}, {ms(v)} ms ({fps(v)} fps)" for n, s, v, _ in rows)
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{alt}" style="width:100%;height:auto;display:block">'
            + "".join(out) + "</svg><figcaption>The first three in the Hazel test's process (<code>Test_HazelJit</code>'s "
            "<code>witch_view_run</code>, a dev build, Node; two runs of 15, pooled medians), the last in the benchmark's own process. "
            "Shaded: inside one frame at 60 fps. The frames a second are each time alone, as if updating the state were free.</figcaption></figure></div>")


SVGS = [("hazel-jit", "hazel-jit", NODE["hazel-jit"]), ("rescript", "ReScript", NODE["ReScript"]),
        ("melange", "Melange", NODE["Melange"]), ("js_of_ocaml", "js_of_ocaml", WT["jsoo_printf_ms"]),
        ("by-hand", "by hand", NODE["hand-written JS"])]


def fig_witch_svgs(prefix="witch/"):
    """each compiler's own drawing, as the markup its Html came to (all five the same, byte for byte)"""
    cells = "".join(
        f'<figure class="f witchcell"><a href="{prefix}{slug}.html"><img src="{prefix}svg/{slug}.svg" width="160" height="220" '
        f'alt="The Witch, as {html.escape(name)}\'s view drew her"></a>'
        f'<figcaption><b>{html.escape(name)}</b><br>{v:.2f} ms ({fps(v)} fps)</figcaption></figure>' for slug, name, v in SVGS)
    return ('<div class="witchrow">' + cells + "</div>")


# ---- one page per output

PAGES = [
    ("hazel", "Hazel, the source", "hazel", None),
    ("hazel-jit", "hazel-jit's output", "js", "hazel-jit"),
    ("rescript", "ReScript 12.3.1's output", "js", "rescript"),
    ("melange", "Melange 5.0.0's output", "js", "melange"),
    ("js_of_ocaml", "js_of_ocaml 5.9.1's output", "js", "js_of_ocaml"),
    ("by-hand", "JavaScript by hand", "js", "by-hand"),
]


def hand_source():
    s = DW("witch-bench.mjs")
    i = s.index("// by hand:")
    j = s.index("const views = {")
    return s[i:j].rstrip()


def jsoo_source():
    core = DW("witch-core.ml")
    return ("(* for js_of_ocaml: a number formatted as OCaml formats one *)\nlet fixed1 (x : float) = Printf.sprintf \"%.1f\" x\n\n"
            + core.rstrip())


def page_parts(slug):
    """the page's listings: [(heading, language, source)] and a paragraph that says what to look for"""
    hz = DW("picture.hz").rstrip()
    if slug == "hazel":
        return ([("The livelit, as the Witch slide defines it (<code>witch.hz</code>, <code>Drawing.^picture</code>)", "hazel", hz)],
                "<p>The view the other pages compile. Its model is one splice, the slide's code for the picture; <code class=\"hz\">view</code> "
                "asks for that splice's value (<code class=\"hz\">eval_splice</code>) and turns the picture's shapes into an SVG: a "
                "<code>viewBox</code> that fits every point, then one <code>polygon</code> or <code>polyline</code> per shape, each "
                "point's coordinates formatted with <code class=\"hz\">to_fixed</code>. The other languages' versions start where "
                "the splice's value arrives: <code class=\"hz\">case r | Some(Val(pic)) =&gt; …</code>.</p>")
    if slug == "hazel-jit":
        return ([("hazel-jit's JavaScript for the livelit's module, formatted by esbuild (its runtime is <code>$R</code>)", "js", DW("hazeljit-witch-pretty.js").rstrip())],
                "<p>What hazel-jit wrote for the module, as the app compiles it once per definition (in "
                f"{WNUMS['compile']} ms). Look for <code>coords$</code>: each number goes through <code>$R.b.to_fixed([x, 1])</code>, "
                "a builtin that takes its arguments as one array and clamps the digits; each list is walked by a recursive "
                "call, <code>grow_all</code> and <code>bounds</code> included, where the other compilers loop; each "
                "<code class=\"hz\">case</code> becomes a chain of conditional expressions with a <code>$R.nomatch</code> at its end.</p>")
    if slug == "rescript":
        return ([("ReScript source (<code>Witch.res</code>, the view as the Hazel is written)", "rescript", DW("Witch.res").rstrip()),
                 ("ReScript 12.3.1's JavaScript (<code>Witch.res.js</code>)", "js", DW("Witch.res.js").rstrip())],
                "<p>ReScript calls <code>toFixed</code> directly, turns <code>grow_all</code>, <code>bounds</code> and "
                "<code>framing</code> into <code>while</code> loops, reads a vertex's point as <code>v.at</code>, and makes each "
                "Html node an object with a string tag, <code>{TAG: \"Node\", _0, _1, _2}</code>. Since both of the shape's "
                "constructors carry <code>points</code> in the same place, <code>verticesOf</code> is just <code>s.points</code>.</p>")
    if slug == "melange":
        return ([("OCaml source (<code>witch-melange.ml</code>)", "ocaml", DW("witch-melange.ml").rstrip()),
                 ("Melange 5.0.0's JavaScript (from its playground)", "js", DW("witch-melange.js").rstrip())],
                "<p>Melange's output is ReScript's with numbers for tags (<code>TAG: /* Node */ 0</code>). Its string "
                "concatenation is nested to the right, as OCaml's <code>^</code> associates, and higher-order calls in the "
                "markup helpers go through <code>Curry._1</code> (a stub here: the view itself makes none).</p>")
    if slug == "js_of_ocaml":
        return ([("OCaml source (<code>witch-jsoo.ml</code>, without the picture's literal and the timing loop)", "ocaml", jsoo_source()),
                 ("js_of_ocaml 5.9.1's JavaScript, <code>--pretty</code>: the view's constants and functions", "js", DW("jsoo-excerpt.js").rstrip())],
                "<p>js_of_ocaml compiles the whole program, OCaml's runtime with it (115 KB here), and renames everything. "
                "The view is <code>_dv_</code>: <code>framing</code>, <code>bounds</code> and <code>grow_all</code> inlined "
                "into it as nested <code>for</code> loops, every tuple an array with its tag first. Each number is "
                "<code>_dc_</code>, OCaml's <code>Printf.sprintf \"%.1f\"</code>, which interprets the format at run time "
                f"before it calls <code>toFixed</code>: {WNUMS['jsoo_pf']} ms against {WNUMS['jsoo_tf']} ms when "
                "<code>fixed1</code> calls JS's <code>toFixed</code> instead (<code>witch-jsoo-tofixed.ml</code>).</p>")
    return ([("By hand: the view on the picture as JSON (arrays, plain objects)", "js", hand_source())],
            "<p>What a JavaScript programmer might write: arrays and <code>for…of</code>, the bounds in four variables "
            "instead of a tuple remade per point, attributes as pairs. The fastest of the five here, by a little.</p>")


def write_pages(CSS, HL, HL_CSS, HL_INLINE_CSS, inline, updated):
    os.makedirs(os.path.join(HERE, "witch"), exist_ok=True)
    nav = " · ".join(f'<a href="{s}.html">{html.escape(t.split(",")[0].replace(" the source", ""))}</a>' for s, t, _, _ in PAGES)
    for slug, title, _, svg in PAGES:
        listings, intro = page_parts(slug)
        body = [f'<body><main>\n<p class="series"><a href="../../">Hazel reports</a> · <a href="../">report 046</a> · '
                f'<a href="../#witch">the Witch\'s picture</a> · one page per output · updated {updated} MST</p>',
                f"<h1>The Witch's picture view: {html.escape(title)}</h1>",
                f'<p class="sub">One of six pages, one per version of the Witch slide\'s <code class="hz">^picture</code> view '
                f'(report 046, <a href="../#witch">a view</a>): {nav}.</p>', inline(intro)]
        if svg:
            v = dict((s, x) for s, _, x in SVGS)[svg]
            body.append(f'<figure class="f witchone"><img src="svg/{svg}.svg" width="240" height="330" alt="The Witch, as this output drew her">'
                        f"<figcaption>This output's drawing, written out as markup: {WNUMS['svg_chars']} characters, the same as "
                        f"the other four's and hazel-jit's in the app, byte for byte. Its view's work: {v:.2f} ms ({fps(v)} fps), "
                        "the median in one Node process.</figcaption></figure>")
        for head, lang, src in listings:
            hl, cls = HL[lang]
            body.append(f"<h2>{head}</h2>")
            body.append(f'<pre class="code {cls}">' + hl(src) + "</pre>")
        files = sorted(os.listdir(os.path.join(HERE, "data", "witch")))
        body.append('<p class="muted">The files, in 046/data/witch (sources, outputs, the benchmark, the timings): '
                    + ", ".join(f'<a href="../data/witch/{f}">{f}</a>' for f in files) + '.</p>\n</main></body>')
        head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
                f"<title>The Witch's picture view: {html.escape(title)}</title>\n"
                f"<meta name=\"description\" content=\"Report 046: the Witch slide's ^picture view, {html.escape(title)}.\">\n"
                "<style>" + CSS + HL_CSS + HL_INLINE_CSS + "\n  figure.witchone img { display: block; max-width: 100%; height: auto; }</style>\n</head>\n")
        open(os.path.join(HERE, "witch", slug + ".html"), "w").write(head + "\n".join(body) + "\n")
    return [os.path.join("046", "witch", s + ".html") for s, _, _, _ in PAGES]
