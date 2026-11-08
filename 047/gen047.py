#!/usr/bin/env python3
"""^report(47), First-Order Data in a Form of Its Own: writes 047/index.html from body.html ({{updated}} filled in), with the series'
styles (035's). A design note for ^ticket(718)."""
import os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
EXTRA = """
  pre.code { background: color-mix(in srgb, var(--line) 35%, transparent); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px;
             overflow-x: auto; font-size: 0.84em; line-height: 1.45; max-width: 100%; }
  pre.code code { background: none; padding: 0; font-size: inherit; overflow-wrap: normal; white-space: pre; }
  ol.outline > li { margin: 4px 0; } ol.steps > li { margin: 10px 0; } .muted { color: var(--muted); }
"""
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
body = open(os.path.join(HERE, "body.html")).read().replace("{{updated}}", updated)
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>First-Order Data in a Form of Its Own</title>\n"
        "<meta name=\"description\" content=\"A design note for dev: closed first-order values, with no holes and no closures, held and moved as data of their own, not as open terms; where it would pay, in what order, and what it costs.\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
print("wrote 047/index.html; updated", updated)
