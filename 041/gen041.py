#!/usr/bin/env python3
"""^report(41), A Grammar Livelit: writes 041/index.html from body.html.

{{name}} in body.html is a value from V. Then the series tools run over the page (build.sh)."""
import os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
V = {"updated": subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()}
BODY = open(os.path.join(HERE, "body.html")).read()
BODY = re.sub(r"\{\{(\w+)\}\}", lambda m: V[m.group(1)], BODY)
HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>A Grammar Livelit</title>
<meta name="description" content="A livelit whose model is a grammar: production rules, in order, edited in Hazel; the first prototype, on IMP's rules, and what comes next (a parser at run time, and programs in the language as tiles).">
<style>""" + CSS + """
  .muted { color: var(--muted); font-size: 0.9em; }
  pre.bnf { font-size: 0.92em; }
</style>
</head>
"""
open(os.path.join(HERE, "index.html"), "w").write(HEAD + BODY)
print("wrote 041/index.html; updated", V["updated"])
