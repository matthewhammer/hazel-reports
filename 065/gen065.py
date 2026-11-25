#!/usr/bin/env python3
"""^report(65): hazel-jit's PR, Described. Matthew Hammer, 2026-11-25, on the new description drafted for
hazelgrove/hazel#2859: "for 2859 --- let's create a new WIP report and iterate on the content of the PR description
there. The point of the report is to iterate on the details within the PR description, esp the executive and
engineering summaries." And: "in this new report, let's have a section that compares the other Ocaml to JS compilation
strategies we reported on before to one, in terms of representations. We can compare performance too, for the new set
of benchmarks (hazel activities), which we largely didn't have before."

One source for the description: pr-2859.md, the text for GitHub, in GitHub's Markdown. This script renders its
sections into the report (each marked "in the PR") between the report's own sections (body.html), and puts the
Markdown itself in the page, to copy. data/*.json hold the numbers the text quotes."""
import html, json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
esc = lambda s: html.escape(str(s), quote=True)

# ---- the Markdown GitHub's descriptions use here: ## headings, paragraphs, - lists, tables, `code`, **bold**, [links](url)
def inline(s):
    out, parts = [], re.split(r"(`[^`]*`)", s)
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) >= 2:
            out.append("<code>" + esc(p[1:-1]) + "</code>")
            continue
        p = esc(p)
        p = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", p)
        p = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', p)
        out.append(p)
    return "".join(out)

def blocks(md):
    """the Markdown of one section as HTML"""
    lines, out, i = md.strip("\n").split("\n"), [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], [r for r in rows[2:]]
            out.append('<div class="tw"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table></div>")
        elif ln.startswith("- "):
            items = []
            while i < len(lines) and (lines[i].startswith("- ") or (lines[i].startswith("  ") and items)):
                if lines[i].startswith("- "): items.append(lines[i][2:])
                else: items[-1] += " " + lines[i].strip()
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(t)}</li>" for t in items) + "</ul>")
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("|", "- ", "## ")):
                para.append(lines[i]); i += 1
            out.append("<p>" + inline(" ".join(para)) + "</p>")
    return "\n".join(out)

MD = open(os.path.join(HERE, "pr-2859.md"), encoding="utf-8").read()
chunks = re.split(r"^## (.+)$", MD, flags=re.M)
PREAMBLE, SECTIONS = chunks[0], list(zip(chunks[1::2], chunks[2::2]))
IDS = {"Executive summary": "exec", "Engineering summary": "eng", "What it holds": "holds", "How compiled values look": "values",
       "Beside other compilers to JavaScript": "beside", "Where it comes from": "origin",
       "Where it differs from the interpreter on `dev`": "differs", "Next, on this branch": "pr-next"}
assert [h for h, _ in SECTIONS] == list(IDS), [h for h, _ in SECTIONS]
# the closing line (the Claude Code credit) stays in the Markdown to copy, not in the report's sections
last_h, last_md = SECTIONS[-1]
CREDIT = "🤖 Generated with [Claude Code](https://claude.com/claude-code)"
assert last_md.rstrip().endswith(CREDIT)
SECTIONS[-1] = (last_h, last_md.rstrip()[: -len(CREDIT)])

def pr_section(h, md):
    return (f'<section class="inpr"><h2 id="{IDS[h]}">{inline(h)}</h2>\n<p class="tag">In the PR’s description</p>\n{blocks(md)}\n</section>')

FIGS = {"updated": updated, "pr_preamble": f'<section class="inpr"><p class="tag">In the PR’s description: its opening line</p>\n{blocks(PREAMBLE)}\n</section>',
        "pr_md": MD.replace("</", "<\\/"), "pr_md_shown": esc(MD), "pr_words": f"{len(re.findall(r'[A-Za-z0-9]+', MD)):,}"}
for h, md in SECTIONS: FIGS["pr_" + IDS[h].replace("-", "_")] = pr_section(h, md)

SWEEP = json.load(open(os.path.join(DATA, "sweep.json")))
FIGS.update({"sw_checks": str(SWEEP["checks"]), "sw_compiled": str(SWEEP["compiled"]), "sw_agreed": str(SWEEP["agreed"]),
             "sw_not_value": str(SWEEP["not_a_value"]), "sw_run": str(SWEEP["run"])})
REP = json.load(open(os.path.join(DATA, "representations.json")))
def rep_table():
    cols = REP["columns"]
    head = "".join(f"<th>{esc(c)}</th>" for c in ["Value"] + cols)
    rows = "".join("<tr><td>" + esc(r["value"]) + "</td>" + "".join(f'<td class="{"chg" if c == "hazel-jit now" and r["hazel-jit now"] != r["hazel-jit 2026-11-07"] else ""}"><code>{esc(r[c])}</code></td>' for c in cols) + "</tr>" for r in REP["rows"])
    return f'<div class="tw"><table class="rep"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
def sugg_list():
    return "<ol class=\"sugg\">" + "".join(f'<li><span class="st {s["status"]}">{esc(s["status_text"])}</span> <b>{esc(s["what"])}</b> {esc(s["now"])}</li>' for s in REP["suggestions"]) + "</ol>"
FIGS.update({"rep_table": rep_table(), "sugg_list": sugg_list()})
PETRI = json.load(open(os.path.join(DATA, "petri-046.json")))
def petri_table():
    num = lambda v: "" if v is None else (f"{v:,.0f}" if v >= 100 else f"{v:.2f}")
    rows = "".join(f'<tr><td class="l">{esc(r["who"])}</td><td>{num(r["median_us"])}</td><td>{num(r.get("fastest_us"))}</td></tr>' for r in PETRI["rows"])
    return f'<div class="tw"><table class="nums"><thead><tr><th class="l">Compiler</th><th>µs a call, median</th><th>the fastest call</th></tr></thead><tbody>{rows}</tbody></table></div>'
FIGS["petri_table"] = petri_table()

EXTRA = """
  section.inpr { border-left: 3px solid var(--accent, #2a78d6); padding-left: 14px; margin-left: -17px; }
  section.inpr p.tag { color: var(--muted); font-size: 0.82em; margin: -0.4em 0 0.6em; text-transform: uppercase; letter-spacing: 0.04em; }
  p.tag.own { color: var(--muted); font-size: 0.82em; margin: -0.4em 0 0.6em; text-transform: uppercase; letter-spacing: 0.04em; }
  .tw { overflow-x: auto; margin: 0.6em 0 1em; }
  table.rep td.chg { background: color-mix(in srgb, var(--good, #2e9e5b) 14%, transparent); }
  table.nums td, table.nums th { text-align: right; font-variant-numeric: tabular-nums; } table.nums td.l, table.nums th.l { text-align: left; }
  ol.sugg li { margin-bottom: 0.5em; } .st { display: inline-block; padding: 0 7px; border-radius: 999px; font-size: 0.8em; font-weight: 600; color: #fff; }
  .st.done { background: #2e9e5b; } .st.part { background: #b07d10; } .st.open { background: #6b737d; }
  pre.md { white-space: pre-wrap; font-size: 0.85em; max-height: 32em; overflow: auto; }
  button.copy-md { font: inherit; padding: 4px 12px; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
"""
body = open(os.path.join(HERE, "body.html"), encoding="utf-8").read()
for k, v in FIGS.items(): body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{(\w+)\}\}", body)
assert not left, left
TITLE = "hazel-jit’s PR, Described"
DESC = ("A working draft of the description for hazelgrove/hazel#2859, hazel-jit for dev, to iterate on before it goes on GitHub: "
        "an executive summary for whoever decides, an engineering summary for whoever reviews, then the details. "
        f"Every evaluator test also runs compiled where it compiles: {SWEEP['compiled']} of {SWEEP['checks']} do, and none differs from the interpreter. "
        "Beside ReScript, Melange and js_of_ocaml, hazel-jit now lays out records as they do, as plain objects; its constructors, options, calls and tail calls not yet. "
        "Their speed on the games of hazeljs-examples is still to measure.")
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{esc(DESC)}\">\n<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(head + body)

# the series card's thumbnail: the description's two summaries, and the sweep
def thumb(mode):
    base = (".h{fill:#1f2328;font:700 15px system-ui,sans-serif}.m{fill:#5b6470;font:11px system-ui,sans-serif}.k{fill:#1f2328;font:700 12px system-ui,sans-serif}"
            ".b{fill:none;stroke:#2a78d6;stroke-width:2}.g{fill:#2e9e5b}.c{fill:#1f2328;font:12px ui-monospace,monospace}")
    dark = ".h{fill:#e8e6e3}.m{fill:#a2a9b3}.k{fill:#e8e6e3}.c{fill:#e8e6e3}.b{stroke:#5a9be6}"
    style = base + ("\n" + dark if mode == "dark" else "\n@media (prefers-color-scheme: dark) {" + dark + "}" if mode == "auto" else "")
    frac = SWEEP["agreed"] / SWEEP["checks"]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" width="320" height="200">\n<style>{style}\n</style>\n'
            '<text class="h" x="16" y="26">hazel-jit for dev, described</text>\n'
            '<line class="b" x1="16" y1="42" x2="16" y2="112"/>'
            '<text class="k" x="26" y="54">Executive summary</text><text class="m" x="26" y="70">what, why, what it changes, who uses it</text>'
            '<text class="k" x="26" y="92">Engineering summary</text><text class="m" x="26" y="108">in and out, values, what the interpreter keeps</text>\n'
            '<text class="c" x="16" y="136">{x: 1}  {$h, $t}  {$c, $v}</text>\n'
            f'<rect x="16" y="152" width="288" height="12" fill="none" stroke="#8b939d"/><rect class="g" x="16" y="152" width="{288 * frac:.1f}" height="12"/>'
            f'<text class="m" x="16" y="184">{SWEEP["compiled"]} of {SWEEP["checks"]} evaluator checks compile; none differs</text>\n</svg>\n')
os.makedirs(os.path.join(HERE, "img"), exist_ok=True)
for name, mode in [("thumb-light.svg", "light"), ("thumb-dark.svg", "dark"), ("thumb.svg", "auto")]:
    open(os.path.join(HERE, "img", name), "w").write(thumb(mode))
meta = {"title": TITLE, "blurb": DESC,
        "source": "065/pr-2859.md: the description for hazelgrove/hazel#2859, in GitHub's Markdown; the page renders it and carries it to copy",
        "builds": {"hazel-jit": "hazelgrove/hazel hazel-jit at 9ec865976d (#2859), on dev at 21da4ae66b",
                   "sweep": f"hazelgrove/hazel CI run {SWEEP['run']}, job {SWEEP['job']} (Fast checks), the sweep's summary line",
                   "package": "hazeljs 0.0.13 (hazelgrove/hazeljs editor-in-package 3a4a1cd, built from hazelgrove/hazel 20febee548), Node 22, one laptop: Gnome dig's step",
                   "games": "report 063 (GitHub run 45247119864, hazeljs 0.0.11) and report 054 (GitHub run 45532448010, trial/847-records-objects f311f4e408)",
                   "others": "report 046 (2026-11-07): ReScript 12.3.1, Melange 5.0.0, js_of_ocaml 5.9.1, hazel-jit of that day, Node 22.23.2, one laptop"},
        "files": ["pr-2859.md", "data/sweep.json", "data/representations.json", "data/petri-046.json"]}
json.dump(meta, open(os.path.join(DATA, "meta.json"), "w"), indent=1, ensure_ascii=False)
print("wrote 065/index.html;", updated)
