#!/usr/bin/env python3
"""^report(44), Hazel Listings in an Article: writes 044/index.html from body.html ({{updated}} filled in), with the series'
styles (035's) and the listings' own (as ^report(43)'s). The page loads ../043/hazel-listings.js, the script it describes."""
import os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
EXTRA = """
  pre.code { background: color-mix(in srgb, var(--line) 35%, transparent); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px;
             overflow-x: auto; font-size: 0.84em; line-height: 1.45; max-width: 100%; }
  pre.code code { background: none; padding: 0; font-size: inherit; overflow-wrap: normal; white-space: pre; }
  ol.steps > li { margin: 10px 0; } .muted { color: var(--muted); }
  ol.outline > li { margin: 4px 0; }
  table.gotos td:first-child { white-space: nowrap; }
  /* Hazel listings (hazel-listings.js): the text until Hazel's editor starts, then the editor */
  .hazel-listing { position: relative; margin: 10px 0; }
  .hazel-listing iframe { border: 1px solid var(--line); border-radius: 8px; background: var(--paper); }
  .hazel-listing[data-state="loading"] pre, .hazel-listing[data-state="tiles"] pre { display: none; }
  .hazel-listing pre.hazel { margin: 0; }
  /* what Hazel says of the program, under the listing it is in (hazel-listings.js) */
  .hazel-listing-status { list-style: none; margin: 6px 0 0; padding: 6px 10px; border-left: 3px solid var(--warn); background: color-mix(in srgb, var(--warn) 8%, transparent); border-radius: 0 6px 6px 0; color: var(--ink); font-size: 0.9em; }
  .hazel-listing-status li { margin: 2px 0; }
"""
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
body = open(os.path.join(HERE, "body.html")).read().replace("{{updated}}", updated)
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>Hazel Listings in an Article</title>\n"
        "<meta name=\"description\" content=\"How a blog post or an article can show its Hazel code in Hazel's own editor, with go to definition from one listing to another: a small script, hazel-listings.js, what it does, and its limits today.\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
print("wrote 044/index.html; updated", updated)
