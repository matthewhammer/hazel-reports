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
RUNS = json.load(open(os.path.join(HERE, "data", "hazel-exp1-runs.json")))["runs"]
P, A = RUNS[-1]["picture"], RUNS[-1]["all_converted"]
kb = lambda b: f"{b / 1000:,.1f}"
ms = lambda v: "" if v is None else (f"{v:.2f}" if v < 10 else f"{v:.1f}")


def rng(f, runs=None):
    """a time over the runs, as lo to hi"""
    xs = [f(r) for r in (runs or RUNS)]
    lo, hi = min(xs), max(xs)
    return ms(lo) if ms(lo) == ms(hi) else f"{ms(lo)} to {ms(hi)}"


LINEAR = [r for r in RUNS if not r["note"]]
pm = lambda k: (lambda r: r["picture"]["ms"][k])


def exp1_table():
    def row(label, size, enc, dec, note=""):
        return (f"<tr><td>{label}</td><td>{size}</td><td>{enc}</td><td>{dec}</td><td>{note}</td></tr>")
    rows = [
        row("Hazel's term, by <code class=\"ml\">Marshal</code> (today)", kb(P["term_bytes"]), rng(pm("term_encode")), rng(pm("term_decode"))),
        row("data, by <code class=\"ml\">Marshal</code>", kb(P["data_bytes"]), rng(pm("data_encode")), rng(pm("data_decode"))),
        row("data, by <code class=\"ml\">Marshal</code> with no sharing table", kb(P["data_noshare_bytes"]), rng(pm("data_noshare_encode")), "",
            "larger: a string met twice is written twice"),
        row("data made plain JS values, by <code>structuredClone</code>", "", rng(pm("to_js"), LINEAR) + " (made JS) + " + rng(pm("structured_clone")) + " (the copy)", "",
            "what <code>postMessage</code> does with JS values"),
        row("data made plain JS values, as JSON", kb(P["json_bytes"]), rng(pm("to_js"), LINEAR) + " (made JS) + " + rng(pm("json_encode")), rng(pm("json_decode"))),
        row("Fumola's <code class=\"ml\">Value</code>, from JSON (<code>json_in</code>)", kb(FX["json_bytes"]), "", ms(FX["ms"]["json_text_to_value"]),
            "native, on the laptop"),
        row("Fumola's <code class=\"ml\">Value</code>, through its serde derive (JSON)", kb(FX["serde_json_bytes"]), ms(FX["ms"]["value_to_serde_json"]),
            ms(FX["ms"]["serde_json_to_value"]), "native, on the laptop; tagged, so wordier"),
    ]
    return ('<table class="vals"><tr><th>The Witch\'s picture, sent as</th><th>KB</th><th>encode, ms</th><th>decode, ms</th><th></th></tr>'
            + "".join(rows) + "</table><p class=\"muted\">Times in Firefox are ranges over the check's runs (" + ", ".join(str(r["run"]) for r in RUNS)
            + "); Firefox's clock there ticks in whole milliseconds, and each time is the median of five batches of at least 25 ms.</p>")


def TM_NUMS(tree):
    """the treemap's own totals, by kind, so the text says what the figure draws"""
    parts = TM.parts_with_rest(tree)
    tot = {k: sum(TM.kinds_of(sp, "term").get(k, 0) for _, sp in parts) for k in ("ids", "term", "dstruct", "data")}
    t = sum(tot.values())
    d = tot["dstruct"] + tot["data"]
    return {"tm_ids": kb(tot["ids"]), "tm_ids_pct": f"{tot['ids'] / t * 100:.0f}", "tm_term": kb(tot["term"]),
            "tm_dstruct": kb(tot["dstruct"]), "tm_data": kb(tot["data"]), "tm_total": kb(t), "tm_dtotal": kb(d),
            "tm_payload_pct": f"{tot['data'] / t * 100:.0f}", "tm_parts": str(len(tree["parts"]))}


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
                     "sizes, taken shape by shape as each adds to the shapes before it, so the shapes add up to the whole and what they "
                     "share (the types every constructor carries, a repeated string) is counted once, on the first shape that uses it "
                     "(<code class=\"ml\">DataExperiment.tree</code>). Firefox on GitHub's machines, run " + str(HX["run"])
                     + " (<code>" + HX["sha"] + "</code>). Hover a rectangle for its bytes.") + note

body = open(os.path.join(HERE, "body.html")).read().replace("{{updated}}", updated)
body = body.replace("{{exp1_table}}", exp1_table()).replace("{{fig_treemap}}", fig_treemap())
for k, v in {"x1_run": ", ".join(str(r["run"]) for r in RUNS), "x1_sha": RUNS[-1]["sha"], "x1_nodes": f"{P['nodes']:,}", "x1_term": kb(P["term_bytes"]),
             "x1_data": kb(P["data_bytes"]), "x1_x": f"{P['term_bytes'] / P['data_bytes']:.1f}",
             "x1_trip_term": rng(lambda r: r["picture"]["ms"]["term_encode"] + r["picture"]["ms"]["term_decode"]),
             "x1_trip_data": rng(lambda r: r["picture"]["ms"]["data_encode"] + r["picture"]["ms"]["data_decode"]),
             "x1_trip_x": (lambda xs: f"{min(xs):.1f} to {max(xs):.1f}")([(r["picture"]["ms"]["term_encode"] + r["picture"]["ms"]["term_decode"])
                                                                        / (r["picture"]["ms"]["data_encode"] + r["picture"]["ms"]["data_decode"]) for r in RUNS]),
             "x1_of_term": rng(pm("of_term"), LINEAR), "x1_json_rt": rng(lambda r: r["picture"]["ms"]["json_encode"] + r["picture"]["ms"]["json_decode"]),
             "x1_to_js": rng(pm("to_js"), LINEAR), "x1_clone": rng(pm("structured_clone")),
             "x1_all_term": kb(A["term_bytes"]), "x1_all_data": kb(A["data_bytes"]), "x1_samples": str(X["samples"]),
             "x1_converted": str(X["converted"]), "fx_in": ms(FX["ms"]["json_text_to_value"]), "fx_out": ms(FX["ms"]["value_to_serde_json"]),
             "fx_back": ms(FX["ms"]["serde_json_to_value"]), "fx_json": kb(FX["json_bytes"]),
             **({} if not X.get("picture_tree") else TM_NUMS(X["picture_tree"]))}.items():
    body = body.replace("{{" + k + "}}", v)
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>First-Order Data in a Form of Its Own</title>\n"
        "<meta name=\"description\" content=\"A design note for dev: closed first-order values, with no holes and no closures, held and moved as data of their own, not as open terms; where it would pay, in what order, and what it costs.\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
print("wrote 047/index.html; updated", updated)
