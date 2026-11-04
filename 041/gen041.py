#!/usr/bin/env python3
"""^report(41), A Grammar Livelit: writes 041/index.html from body.html.

{{name}} in body.html is a value from V. Then the series tools run over the page (build.sh)."""
import html, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from codehl import hazel_hl, HL_CSS   # (2026-11-04, Matthew: "please use high contrast / dark theme Hazel for the code")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
V = {"updated": subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()}
BODY = open(os.path.join(HERE, "body.html")).read()
BODY = re.sub(r"\{\{(\w+)\}\}", lambda m: V[m.group(1)], BODY)
# IMP's rules, as a grammar in the same palette: a nonterminal pink, every terminal (while, do, if, :=, ;, ...) cyan,
# the grammar's own ::= and | yellow, <ids> purple. Hazel's own highlighter would colour only Hazel's keywords
# (if, then, else) and leave IMP's (while, do) plain (Matthew, 2026-11-04: "Yes, fix it").
def grammar_hl(t):
    out = []
    for m in re.finditer(r"(::=)|(\|)|(<ids>)|([A-Z][A-Za-z0-9_]*)|([a-z_][A-Za-z0-9_]*|:=|\S)|(\s+)", t):
        g = m.group(0)
        cls = "ho" if m.group(1) or m.group(2) else "hn" if m.group(3) else "hC" if m.group(4) else "hk" if m.group(5) else None
        out.append(f'<span class="{cls}">{html.escape(g)}</span>' if cls else g)
    return "".join(out)
BODY = re.sub(r'<pre class="grammar">([\s\S]*?)</pre>', lambda m: '<pre class="hz">' + grammar_hl(html.unescape(m.group(1))) + "</pre>", BODY)
# every code block, in the series' high-contrast Hazel colours (bright on black), as ^report(30) and ^report(33)
BODY = re.sub(r'<pre class="bnf">([\s\S]*?)</pre>', lambda m: '<pre class="hz">' + hazel_hl(html.unescape(m.group(1))) + "</pre>", BODY)
HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>A Grammar Livelit</title>
<meta name="description" content="A livelit whose model is a grammar: production rules, in order, edited in Hazel; the first prototype, on IMP's rules, and what comes next (a parser at run time, and programs in the language as tiles).">
<style>""" + CSS + """
  .muted { color: var(--muted); font-size: 0.9em; }
  pre.hz { font-size: 0.92em; }
""" + HL_CSS + """
</style>
</head>
"""
open(os.path.join(HERE, "index.html"), "w").write(HEAD + BODY)
print("wrote 041/index.html; updated", V["updated"])
