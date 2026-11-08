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
  table.vals { display: block; overflow-x: auto; max-width: 100%; border-collapse: collapse; margin: 1em 0; font-size: 0.92em; }
  table.vals th, table.vals td { padding: 4px 8px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
  table.vals th { font-weight: 600; } figure.f { margin: 1.2em 0; } figure.f svg { max-width: 100%; }
  figcaption { color: var(--muted); font-size: 0.9em; margin-top: 6px; max-width: 80ch; }
"""
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()

# (experiment 1) Hazel's side from the Firefox check, Fumola's from the laptop
import json, sys
sys.path.insert(0, HERE)
import treemap as TM
HX = json.load(open(os.path.join(HERE, "data", "hazel-exp1.json")))
FX = json.load(open(os.path.join(HERE, "data", "fumola-exp1.json")))
X = HX["experiment"]
P, A = X["picture"], X["all_converted"]
kb = lambda b: f"{b / 1000:,.1f}"
ms = lambda v: "" if v is None else (f"{v:.2f}" if v < 10 else f"{v:.1f}")


def exp1_table():
    def row(label, size, enc, dec, note=""):
        return (f"<tr><td>{label}</td><td>{size}</td><td>{enc}</td><td>{dec}</td><td>{note}</td></tr>")
    m = P["ms"]
    rows = [
        row("Hazel's term, by <code class=\"ml\">Marshal</code> (today)", kb(P["term_bytes"]), ms(m["term_encode"]), ms(m["term_decode"])),
        row("data, by <code class=\"ml\">Marshal</code>", kb(P["data_bytes"]), ms(m["data_encode"]), ms(m["data_decode"])),
        row("data, by <code class=\"ml\">Marshal</code> with no sharing table", kb(P["data_noshare_bytes"]), ms(m["data_noshare_encode"]), "",
            "larger: a string met twice is written twice"),
        row("data made plain JS values, by <code>structuredClone</code>", "", ms(m["to_js"]) + " (made JS) + " + ms(m["structured_clone"]) + " (the copy)", "",
            "what <code>postMessage</code> does with JS values"),
        row("data made plain JS values, as JSON", kb(P["json_bytes"]), ms(m["to_js"]) + " (made JS) + " + ms(m["json_encode"]), ms(m["json_decode"])),
        row("Fumola's <code class=\"ml\">Value</code>, from JSON (<code>json_in</code>)", kb(FX["json_bytes"]), "", ms(FX["ms"]["json_text_to_value"]),
            "native, on the laptop"),
        row("Fumola's <code class=\"ml\">Value</code>, through its serde derive (JSON)", kb(FX["serde_json_bytes"]), ms(FX["ms"]["value_to_serde_json"]),
            ms(FX["ms"]["serde_json_to_value"]), "native, on the laptop; tagged, so wordier"),
    ]
    return ('<table class="vals"><tr><th>The Witch\'s picture, sent as</th><th>KB</th><th>encode, ms</th><th>decode, ms</th><th></th></tr>'
            + "".join(rows) + "</table>")


def fig_treemap():
    if not X.get("picture_tree"):
        return "<p class=\"note\">(The treemaps come from the next run of the check.)</p>"
    if not X["picture_tree"]["parts"]:
        note = ("<p class=\"note\">For now the whole picture, split four ways; the next run splits each of its shapes "
                "(run 42494936942).</p>")
    else:
        note = ""
    return TM.figure(X["picture_tree"], "The Witch's picture, its bytes as Hazel's terms and as data, on one scale",
                     "Treemaps (Ben Shneiderman's, University of Maryland, 1991; the squarified layout of Bruls, Huijsing and van "
                     "Wijk, 2000): each rectangle's area is its bytes. Each outer rectangle is one of the picture's shapes, named where "
                     "it is large enough, and is split into what its bytes are; each amount a difference of exact <code>Marshal</code> "
                     "sizes (<code class=\"ml\">DataExperiment.split</code>). Firefox on GitHub's machines, run " + str(HX["run"])
                     + " (<code>" + HX["sha"] + "</code>). Hover a rectangle for its bytes.") + note

body = open(os.path.join(HERE, "body.html")).read().replace("{{updated}}", updated)
body = body.replace("{{exp1_table}}", exp1_table()).replace("{{fig_treemap}}", fig_treemap())
for k, v in {"x1_run": str(HX["run"]), "x1_sha": HX["sha"], "x1_nodes": f"{P['nodes']:,}", "x1_term": kb(P["term_bytes"]),
             "x1_data": kb(P["data_bytes"]), "x1_x": f"{P['term_bytes'] / P['data_bytes']:.1f}",
             "x1_trip_term": ms(P["ms"]["term_encode"] + P["ms"]["term_decode"]),
             "x1_trip_data": ms(P["ms"]["data_encode"] + P["ms"]["data_decode"]),
             "x1_trip_x": f"{(P['ms']['term_encode'] + P['ms']['term_decode']) / (P['ms']['data_encode'] + P['ms']['data_decode']):.1f}",
             "x1_of_term": ms(P["ms"]["of_term"]), "x1_json_rt": ms(P["ms"]["json_encode"] + P["ms"]["json_decode"]),
             "x1_to_js": ms(P["ms"]["to_js"]), "x1_clone": ms(P["ms"]["structured_clone"]),
             "x1_all_term": kb(A["term_bytes"]), "x1_all_data": kb(A["data_bytes"]), "x1_samples": str(X["samples"]),
             "x1_converted": str(X["converted"]), "fx_in": ms(FX["ms"]["json_text_to_value"]), "fx_out": ms(FX["ms"]["value_to_serde_json"]),
             "fx_back": ms(FX["ms"]["serde_json_to_value"]), "fx_json": kb(FX["json_bytes"]),
             **({} if not X.get("picture_tree") else (lambda w: {
                 "tm_ids": kb(w["term"] - w["shared_tags"]), "tm_ids_pct": f"{(w['term'] - w['shared_tags']) / w['term'] * 100:.0f}",
                 "tm_term": kb(w["shared_tags"] - w["data"]), "tm_dstruct": kb(w["data"] - w["atoms"]), "tm_data": kb(w["atoms"]),
                 "tm_total": kb(w["term"]), "tm_dtotal": kb(w["data"]),
                 "tm_payload_pct": f"{w['atoms'] / w['term'] * 100:.0f}"})(X["picture_tree"]["whole"]))}.items():
    body = body.replace("{{" + k + "}}", v)
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>First-Order Data in a Form of Its Own</title>\n"
        "<meta name=\"description\" content=\"A design note for dev: closed first-order values, with no holes and no closures, held and moved as data of their own, not as open terms; where it would pay, in what order, and what it costs.\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
print("wrote 047/index.html; updated", updated)
