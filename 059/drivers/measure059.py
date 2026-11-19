#!/usr/bin/env python3
"""^report(59): each candidate interface font, measured against the Helvetica Neue Hazel shipped until hazelgrove/hazel#2837.

  PYTHONPATH=<fontTools> python3 059/drivers/measure059.py HELVETICA_NEUE_REGULAR.woff2

Fetches each candidate's Latin regular (400) and bold (700) woff2 from Fontsource on jsDelivr, at the version named below,
and reads, with fontTools: its x-height and cap height (OS/2, per em); the width it sets a sample of Hazel's own interface
words at (the advance widths, per em, summed), against Helvetica Neue's; and the two files' bytes. The license is the
npm package's own (`npm view @fontsource/<name> license`). Writes 059/data/fonts.json. Helvetica Neue's file is read
locally and not kept: it is the file Hazel stops shipping."""
import json, os, sys, urllib.request
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = ("Settings Show as text Edit in Hazel Goto definition Goto first use Problems Explain this Probe Type Expected Int "
         "but found Bool Undo Redo Copy Paste Find Action The type of this expression Livelit Slide Tutorial Exercise Run Step "
         "Result Evaluation")
CANDIDATES = [  # (fontsource name, shown name, version, what it is)
    ("inter", "Inter", "5.3.0", "designed for screens and interfaces (Rasmus Andersson)"),
    ("roboto", "Roboto", "5.3.0", "Android's interface font (Christian Robertson, Google)"),
    ("ibm-plex-sans", "IBM Plex Sans", "5.3.0", "IBM's grotesque (Mike Abbink, Bold Monday)"),
    ("arimo", "Arimo", "5.3.0", "set to Arial's widths (Steve Matteson)"),
    ("public-sans", "Public Sans", "5.3.0", "the US Web Design System's font, after Libre Franklin"),
    ("figtree", "Figtree", "5.3.0", "friendly, geometric (Erik Kennedy)"),
    ("noto-sans", "Noto Sans", "5.3.0", "Google's, for nearly every writing system"),
    ("geist-sans", "Geist", "5.3.0", "Swiss in style (Vercel)"),
    ("atkinson-hyperlegible", "Atkinson Hyperlegible", "5.3.0", "for readers with low vision (Braille Institute)"),
    ("source-sans-3", "Source Sans 3", "5.3.1", "Adobe's companion to Source Code Pro, Hazel's code font (Paul D. Hunt)"),
    ("work-sans", "Work Sans", "5.3.0", "wide, for display (Wei Huang)"),
]
CACHE = os.environ.get("FONT_CACHE", "/tmp/font-survey")


def url(name, ver, w):
    return f"https://cdn.jsdelivr.net/npm/@fontsource/{name}@{ver}/files/{name}-latin-{w}-normal.woff2"


def fetch(name, ver, w):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, f"{name}@{ver}-{w}.woff2")
    if not os.path.exists(p):
        req = urllib.request.Request(url(name, ver, w), headers={"User-Agent": "hazel-report-059"})
        open(p, "wb").write(urllib.request.urlopen(req, timeout=60).read())
    return p


def measure(path):
    f = TTFont(path)
    upm, os2, cmap, hmtx = f["head"].unitsPerEm, f["OS/2"], f.getBestCmap(), f["hmtx"]
    width = sum(hmtx[cmap[ord(c)]][0] for c in WORDS if ord(c) in cmap) / upm
    return {"x_height": os2.sxHeight / upm, "cap_height": os2.sCapHeight / upm, "width_em": width, "glyphs": len(f.getGlyphOrder())}


hn = measure(sys.argv[1])
out = {"sample": WORDS, "helvetica_neue": {**hn, "bytes_400_700": os.path.getsize(sys.argv[1]) + os.path.getsize(sys.argv[1].replace("Regular", "Bold"))},
       "candidates": []}
for name, shown, ver, what in CANDIDATES:
    r, b = fetch(name, ver, 400), fetch(name, ver, 700)
    m = measure(r)
    out["candidates"].append({"fontsource": name, "name": shown, "version": ver, "what": what, "license": "OFL-1.1",
                              "url_400": url(name, ver, 400), "url_700": url(name, ver, 700),
                              "bytes_400_700": os.path.getsize(r) + os.path.getsize(b), **m,
                              "width_vs_hn": round(m["width_em"] / hn["width_em"], 3), "x_vs_hn": round(m["x_height"] / hn["x_height"], 3)})
json.dump(out, open(os.path.join(HERE, "..", "data", "fonts.json"), "w"), indent=1)
for c in out["candidates"]:
    print(f"{c['name']:22} width {c['width_vs_hn']:.2f}  x {c['x_vs_hn']:.2f}  {c['bytes_400_700']/1024:.0f} KB")
