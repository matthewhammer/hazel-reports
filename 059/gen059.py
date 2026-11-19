#!/usr/bin/env python3
"""^report(59): An Open Font for Hazel's Interface. Matthew Hammer, 2026-11-19, after hazelgrove/hazel#2837 (Hazel ships no
copy of Helvetica Neue): "Let's look for an open font for the interface, shipped with Hazel, so it looks the same everywhere
(Inter, for example, under the SIL Open Font License). A choice for the team.", then "Make the page".

Writes 059/index.html from body.html and data/fonts.json (drivers/measure059.py). The candidates' fonts load from Fontsource
on jsDelivr, at pinned versions, under names of their own (so a copy installed on the reader's machine is not used instead);
Helvetica Neue is shown only from the reader's machine, if it has one."""
import html, json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
D = json.load(open(os.path.join(HERE, "data", "fonts.json")))
C = D["candidates"]
HN = D["helvetica_neue"]
CODE = "https://cdn.jsdelivr.net/npm/@fontsource/source-code-pro@5.3.1/files/source-code-pro-latin-400-normal.woff2"
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
esc = lambda s: html.escape(s, quote=True)
fam = lambda c: "c-" + c["fontsource"]

FACES = "".join(
    f'@font-face {{ font-family: "{fam(c)}"; font-weight: 400; font-display: swap; src: url("{c["url_400"]}") format("woff2"); }}\n'
    f'@font-face {{ font-family: "{fam(c)}"; font-weight: 700; font-display: swap; src: url("{c["url_700"]}") format("woff2"); }}\n'
    for c in C) + f'@font-face {{ font-family: "c-code"; font-weight: 400; font-display: swap; src: url("{CODE}") format("woff2"); }}\n'

EXTRA = """
  ol.outline > li { margin: 4px 0; } .muted { color: var(--muted); }
  table.vals { display: block; overflow-x: auto; max-width: 100%; border-collapse: collapse; margin: 0.6em 0 1em; font-size: 0.88em; }
  table.vals th, table.vals td { padding: 5px 8px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
  table.vals td.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; } table.vals th { font-weight: 600; }
  .controls { display: flex; flex-wrap: wrap; gap: 10px 18px; align-items: center; margin: 10px 0 14px; font-size: 0.9em; }
  .controls input[type=text] { font: inherit; padding: 4px 8px; border: 1px solid var(--line); border-radius: 6px; background: var(--paper); color: var(--ink); min-width: 16em; }
  .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(330px, 1fr)); gap: 14px; }
  .card { border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px 12px; background: var(--paper); }
  .card.today { border-style: dashed; }
  .card h3 { margin: 0 0 2px; font-size: 1em; } .card .meta { color: var(--muted); font-size: 0.8em; margin-bottom: 8px; }
  .ui { font-size: var(--sample, 17px); line-height: 1.35; display: grid; grid-template-columns: auto 1fr; gap: 10px; align-items: start; }
  .ui .menu { border: 1px solid var(--line); border-radius: 6px; padding: 4px 0; min-width: 9.5em; box-shadow: 0 1px 3px rgb(0 0 0 / 0.08); }
  .ui .menu div { padding: 2px 10px; white-space: nowrap; } .ui .menu div.on { background: color-mix(in srgb, var(--accent) 16%, transparent); }
  .ui .menu hr { border: 0; border-top: 1px solid var(--line); margin: 3px 0; }
  .ui .panel h4 { margin: 0 0 3px; font-size: 1em; font-weight: 700; } .ui .panel p { margin: 0 0 6px; }
  .ui .err { color: var(--bad); } .ui code, .ui .code { font-family: "c-code", "Source Code Pro", monospace; font-size: 0.92em; }
  .ui .btns { display: flex; gap: 6px; flex-wrap: wrap; } .ui button { font: inherit; font-size: 0.85em; padding: 2px 9px; border-radius: 6px; border: 1px solid var(--line); background: transparent; color: var(--ink); }
  .ui button.primary { font-weight: 700; border-color: var(--accent); }
  .ui .nums { font-variant-numeric: tabular-nums; color: var(--muted); font-size: 0.85em; }
  .ui .code { grid-column: 1 / -1; padding: 4px 8px; border-radius: 6px; background: color-mix(in srgb, var(--line) 40%, transparent); }
  figure.chart { margin: 1em 0; } figure.chart svg { width: 100%; height: auto; max-width: 680px; display: block; }
  figure.chart figcaption { color: var(--muted); font-size: 0.88em; }
  svg .pt { fill: var(--accent); } svg .pt.hn { fill: var(--ink); } svg .lbl { fill: var(--ink); font: 12px system-ui, sans-serif; }
  svg .ax { stroke: var(--line); } svg .axl { fill: var(--muted); font: 11px system-ui, sans-serif; } svg .band { fill: color-mix(in srgb, var(--good) 12%, transparent); }
  .ui .tell { grid-column: 1 / -1; font-size: 2.1em; line-height: 1.1; letter-spacing: 0.01em; }
  .ui .probe { position: absolute; left: 0; top: 0; visibility: hidden; white-space: nowrap; font-size: 40px; letter-spacing: 0; font-weight: 400;
    font-kerning: none; font-variant-ligatures: none; font-feature-settings: "kern" 0, "liga" 0, "calt" 0; }
  .card .ui button, .card .ui button.primary { font-family: inherit; }
  .card { position: relative; } .card.fallback { border-style: dotted; }
  .proof { font: 0.78em/1.45 ui-monospace, "Source Code Pro", monospace; color: var(--muted); margin: 8px 0 0; padding-top: 6px; border-top: 1px solid var(--line); overflow-wrap: anywhere; }
  .proof b { color: var(--ink); } .proof .yes { color: var(--good); font-weight: 700; } .proof .no { color: var(--bad); font-weight: 700; }
"""


def sample(family_css):
    return (f'<div class="ui" style="font-family: {family_css}">'
            '<div class="menu"><div class="on">Goto definition</div><div>Goto first use</div><div>Explain this</div><hr><div>Copy</div><div>Paste</div></div>'
            '<div class="panel"><h4>Settings</h4><p class="free">Show each step of the evaluation, and keep the probes’ samples.</p>'
            '<p class="err">Expected <code>Int</code> but found <code>Bool</code></p>'
            '<div class="btns"><button>Show as text</button><button class="primary">Edit in Hazel</button></div>'
            '<p class="nums">12 samples · 3.5 ms · 1,024 steps</p></div>'
            '<div class="tell">Rag 1Il Qy G&amp;t</div>'
            '<div class="code">let area : Shape -&gt; Float = fun s -&gt; ...</div>'
            f'<span class="probe" aria-hidden="true">{esc(D["sample"])}</span></div>')


def cards():
    out = ['<div class="cards">',
           '<div class="card today"><h3>Helvetica Neue, from your machine <span class="muted" id="hn-here"></span></h3>'
           '<div class="meta">What Hazel showed until #2837, where it shipped the file; a Mac has its own copy. Without one, this card falls back to Helvetica, Arial or sans-serif.</div>'
           + sample("'Helvetica Neue', Helvetica, Arial, sans-serif")
           + f'<p class="proof" data-font="Helvetica Neue" data-family="Helvetica Neue" data-em="{HN["width_em"]:.4f}">measuring… (needs JavaScript)</p></div>',
           '<div class="card fallback" id="font-fallback"><h3>The fallback alone: <code>sans-serif</code></h3>'
           '<div class="meta">What a card would show if its font had not loaded: your browser\u2019s default sans-serif. Every candidate below should look, and measure, unlike it.</div>'
           + sample("sans-serif") + '<p class="proof" data-font="" data-family="" data-em="">measuring… (needs JavaScript)</p></div>']
    for c in C:
        out.append(f'<div class="card" id="font-{c["fontsource"]}"><h3 style="font-family: \'{fam(c)}\', sans-serif">{esc(c["name"])}</h3>'
                   f'<div class="meta">{esc(c["what"])} · SIL OFL 1.1 · width {c["width_vs_hn"]:.2f}, x-height {c["x_vs_hn"]:.2f} · {c["bytes_400_700"] / 1024:.0f} KB</div>'
                   + sample(f"'{fam(c)}', sans-serif")
                   + f'<p class="proof" data-font="{esc(c["name"])}" data-family="{fam(c)}" data-em="{c["width_em"]:.4f}" data-src="@fontsource/{c["fontsource"]}@{c["version"]}">measuring… (needs JavaScript)</p></div>')
    out.append("</div>")
    return "".join(out)


def table():
    rows = ["<tr><th>Font</th><th>Width</th><th>x-height</th><th>Cap height</th><th>Regular and bold, Latin</th><th>License</th><th>Version</th><th>What it is</th></tr>",
            f'<tr><td>Helvetica Neue (until #2837)</td><td class="n">1.00</td><td class="n">1.00</td><td class="n">{HN["cap_height"] / HN["cap_height"]:.2f}</td>'
            f'<td class="n">{HN["bytes_400_700"] / 1024:.0f} KB, whole font</td><td>commercial; no license on record</td><td>10.0d40e1</td><td>Linotype’s</td></tr>']
    for c in sorted(C, key=lambda c: abs(c["width_vs_hn"] - 1) + abs(c["x_vs_hn"] - 1)):
        rows.append(f'<tr><td><a href="#font-{c["fontsource"]}">{esc(c["name"])}</a></td><td class="n">{c["width_vs_hn"]:.2f}</td><td class="n">{c["x_vs_hn"]:.2f}</td>'
                    f'<td class="n">{c["cap_height"] / HN["cap_height"]:.2f}</td><td class="n">{c["bytes_400_700"] / 1024:.0f} KB</td><td>SIL OFL 1.1</td>'
                    f'<td><code>@fontsource/{c["fontsource"]}@{c["version"]}</code></td><td>{esc(c["what"])}</td></tr>')
    return '<table class="vals">' + "".join(rows) + "</table>"


def chart():
    W, H, L, B, T, R = 680, 330, 56, 40, 14, 20
    xs, ys = (0.90, 1.13), (0.92, 1.08)
    px = lambda v: L + (v - xs[0]) / (xs[1] - xs[0]) * (W - L - R)
    py = lambda v: T + (ys[1] - v) / (ys[1] - ys[0]) * (H - T - B)
    g = [f'<rect class="band" x="{px(0.98):.1f}" y="{py(1.02):.1f}" width="{px(1.02) - px(0.98):.1f}" height="{py(0.98) - py(1.02):.1f}"/>']
    for v in (0.92, 0.96, 1.00, 1.04, 1.08, 1.12):
        g.append(f'<line class="ax" x1="{px(v):.1f}" y1="{T}" x2="{px(v):.1f}" y2="{H - B}"/><text class="axl" x="{px(v):.1f}" y="{H - B + 15}" text-anchor="middle">{v:.2f}</text>')
    for v in (0.94, 0.98, 1.02, 1.06):
        g.append(f'<line class="ax" x1="{L}" y1="{py(v):.1f}" x2="{W - R}" y2="{py(v):.1f}"/><text class="axl" x="{L - 6}" y="{py(v) + 4:.1f}" text-anchor="end">{v:.2f}</text>')
    g.append(f'<text class="axl" x="{(L + W - R) / 2:.0f}" y="{H - 6}" text-anchor="middle">width of Hazel’s interface words, against Helvetica Neue’s</text>')
    g.append(f'<text class="axl" transform="translate(14 {(T + H - B) / 2:.0f}) rotate(-90)" text-anchor="middle">x-height, against Helvetica Neue’s</text>')
    g.append(f'<circle class="pt hn" cx="{px(1):.1f}" cy="{py(1):.1f}" r="5"/><text class="lbl" x="{px(1) + 8:.1f}" y="{py(1) - 8:.1f}">Helvetica Neue</text>')
    nudge = {"arimo": (8, 14), "ibm-plex-sans": (8, -6), "roboto": (-8, 14), "figtree": (8, 4), "geist-sans": (8, 14), "inter": (8, 4), "noto-sans": (-8, -8),
             "public-sans": (8, -6), "atkinson-hyperlegible": (-8, 4), "source-sans-3": (8, 4), "work-sans": (-8, 4)}
    for c in C:
        x, y = px(c["width_vs_hn"]), py(c["x_vs_hn"])
        dx, dy = nudge.get(c["fontsource"], (8, 4))
        g.append(f'<circle class="pt" cx="{x:.1f}" cy="{y:.1f}" r="4"/><text class="lbl" x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{"end" if dx < 0 else "start"}">{esc(c["name"])}</text>')
    return (f'<figure class="chart"><svg viewBox="0 0 {W} {H}" role="img" aria-label="Each candidate font, placed by the width it sets Hazel’s interface words at and its x-height, both against Helvetica Neue’s.">'
            + "".join(g) + "</svg><figcaption>Each candidate, by the width it sets a sample of Hazel’s interface words at (across) and its x-height, how tall its small letters are (up), both against Helvetica Neue’s. The green band is within 2% of Helvetica Neue in both: the fonts there would change the interface’s layout least.</figcaption></figure>")


SCRIPT = """
<script>
(() => {
  const root = document.documentElement;
  const size = document.getElementById("sample-size"), out = document.getElementById("sample-size-out"), say = document.getElementById("sample-text");
  if (size) size.addEventListener("input", () => { root.style.setProperty("--sample", size.value + "px"); out.textContent = size.value + " px"; });
  if (say) say.addEventListener("input", () => { const t = say.value || say.placeholder; document.querySelectorAll(".ui .free").forEach(p => { p.textContent = t; }); });
  // (each card's proof: what its CSS asks for, whether its font's files loaded, and how wide a hidden line of Hazel's
  // words, drawn by the card's own CSS at 40 px with no kerning or ligatures, really is, against the width the font's own
  // advance widths predict and against the fallback's. A browser does not say which font drew a text; widths do.)
  const prove = () => {
    for (const p of document.querySelectorAll(".proof")) {
      const card = p.closest(".card"), ui = card.querySelector(".ui"), probe = ui.querySelector(".probe");
      const asked = getComputedStyle(ui).fontFamily, family = p.dataset.family, name = p.dataset.font, em = parseFloat(p.dataset.em);
      const w = probe.getBoundingClientRect().width;
      const fb = probe.cloneNode(true); fb.style.fontFamily = "sans-serif"; ui.append(fb); const wf = fb.getBoundingClientRect().width; fb.remove();
      const faces = family ? [...document.fonts].filter(f => f.family.replace(/["']/g, "") === family) : [];
      const files = !family ? "none: the browser's default sans-serif"
        : faces.length ? faces.map(f => `${f.weight} ${f.status}`).join(", ") + (p.dataset.src ? ` (from cdn.jsdelivr.net, ${p.dataset.src})` : "")
        : "none declared: from your machine, if it has it";
      const pred = em ? em * 40 : NaN, near = em ? Math.abs(w - pred) / pred : NaN, likeFallback = Math.abs(w - wf) / wf < 0.002;
      const px = v => v.toFixed(1) + " px";
      const verdict = !family ? `<span class="yes">the fallback</span>: every other card should measure unlike ${px(w)}`
        : near < 0.006 && likeFallback ? `<span class="yes">\u2713 measures as ${name}</span>, but so would the fallback here, within 0.2%: width cannot tell them apart in this browser; the large letters, or the browser's own font panel, can`
        : near < 0.006 ? `<span class="yes">\u2713 drawn in ${name}</span>: within ${(near * 100).toFixed(1)}% of its metrics, and ${(Math.abs(w - wf) / wf * 100).toFixed(1)}% from the fallback`
        : likeFallback ? `<span class="no">\u2717 not ${name}</span>: this box measures like the fallback`
        : `<span class="no">? not clearly ${name}</span>: ${(near * 100).toFixed(1)}% from its metrics`;
      p.innerHTML = `CSS asks for: <b>${asked.replace(/</g, "&lt;")}</b><br>Font files: ${files}<br>` +
        `Hazel's sample words at 40 px: this box <b>${px(w)}</b>` + (em ? ` \u00b7 ${name}'s own metrics ${px(pred)}` : "") + ` \u00b7 the fallback ${px(wf)}<br>${verdict}`;
    }
  };
  document.fonts.ready.then(() => setTimeout(prove, 300));
  // (is Helvetica Neue on this machine? a text measured in it and in a fallback differs in width when it is)
  const c = document.createElement("canvas").getContext("2d"), probe = "Hamburgefonstiv 0123456789";
  const w = f => { c.font = "40px " + f; return c.measureText(probe).width; };
  const here = w('"Helvetica Neue", monospace') !== w("monospace");
  const mark = document.getElementById("hn-here"); if (mark) mark.textContent = here ? "(found here)" : "(not on this machine: what you see is a fallback)";
})();
</script>
"""

FIGS = {"updated": updated, "cards": cards(), "table": table(), "chart": chart(), "n": str(len(C)), "hn_kb": f"{HN['bytes_400_700'] / 1024:.0f}"}
body = open(os.path.join(HERE, "body.html")).read()
for k, v in FIGS.items():
    body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{(\w+)\}\}", body)
assert not left, left
TITLE = "An Open Font for Hazel’s Interface"
DESC = ("Since hazelgrove/hazel#2837, Hazel ships no copy of Helvetica Neue. Eleven open fonts, under the SIL Open Font License, "
        "side by side in Hazel's interface and measured against Helvetica Neue, for the team to choose one Hazel can ship.")
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{esc(DESC)}\">\n<style>" + CSS + EXTRA + FACES + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body.replace("</main>", "</main>\n" + SCRIPT, 1))
print("wrote 059/index.html;", updated)
