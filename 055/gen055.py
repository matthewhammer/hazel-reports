#!/usr/bin/env python3
"""^report(55): Holes Across the Boundary. A starter project for hazel-jit, written for John, on the Hazel team, who
offered on 2026-11-17 to look into holes and hazel-jit after the team's meeting that day; Matthew Hammer, 2026-11-17:
"Yes, write the brief". Writes 055/index.html from body.html, and 055/data/meta.json and brief.json."""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
EXTRA = """
  ol.outline > li { margin: 4px 0; } .muted { color: var(--muted); }
  table.vals { display: block; overflow-x: auto; max-width: 100%; border-collapse: collapse; margin: 0.6em 0 1em; font-size: 0.88em; }
  table.vals th, table.vals td { padding: 5px 8px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
  table.vals th { font-weight: 600; } table.vals td:first-child { min-width: 14ch; }
  figure.f { margin: 1.2em 0; } figure.f svg { max-width: 100%; height: auto; }
  figcaption { color: var(--muted); font-size: 0.9em; margin-top: 6px; max-width: 80ch; }
  code { overflow-wrap: anywhere; }
  .fig-box { fill: var(--paper); stroke: var(--line); stroke-width: 1.5; } .fig-ink { fill: var(--ink); } .fig-mute { fill: var(--muted); }
  .fig-arrow { stroke: var(--ink); stroke-width: 1.6; fill: none; } .fig-stop { stroke: var(--bad); stroke-width: 1.6; fill: none; stroke-dasharray: 5 4; }
  .fig-hole { fill: var(--paper); stroke: var(--accent); stroke-width: 2; stroke-dasharray: 3 2; } .fig-acc { fill: var(--accent); } .fig-bad { fill: var(--bad); }
"""
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()

FIG_IDEA = """<figure class="f" id="fig-idea">
<svg viewBox="0 0 760 250" role="img" aria-labelledby="fig-idea-cap" font-family="ui-sans-serif, system-ui, sans-serif" font-size="13">
<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="fig-ink"/></marker>
<marker id="ahb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="fig-bad"/></marker></defs>
<rect x="10" y="30" width="210" height="170" rx="10" class="fig-box"/>
<text x="115" y="54" text-anchor="middle" class="fig-ink" font-weight="600">The interpreter</text>
<text x="115" y="96" text-anchor="middle" class="fig-ink" font-family="ui-monospace, monospace">swap((1, ?))</text>
<text x="115" y="170" text-anchor="middle" class="fig-ink" font-family="ui-monospace, monospace">(?, 1)</text>
<text x="115" y="188" text-anchor="middle" class="fig-mute" font-size="11">the same hole, its id and environment</text>
<rect x="540" y="30" width="210" height="170" rx="10" class="fig-box"/>
<text x="645" y="54" text-anchor="middle" class="fig-ink" font-weight="600">Compiled swap</text>
<text x="645" y="96" text-anchor="middle" class="fig-ink" font-family="ui-monospace, monospace">[1, {$opaque: 0}]</text>
<text x="645" y="170" text-anchor="middle" class="fig-ink" font-family="ui-monospace, monospace">[{$opaque: 0}, 1]</text>
<text x="645" y="133" text-anchor="middle" class="fig-mute" font-size="11">moves it, never opens it</text>
<circle cx="380" cy="128" r="30" class="fig-hole"/>
<text x="380" y="134" text-anchor="middle" class="fig-acc" font-weight="700" font-size="18">?</text>
<text x="420" y="66" text-anchor="middle" class="fig-mute" font-size="11">the table keeps the term: 0 &#8594; ?</text>
<path d="M222,92 L536,92" class="fig-arrow" marker-end="url(#ah)"/>
<text x="300" y="86" text-anchor="middle" class="fig-ink" font-family="ui-monospace, monospace" font-size="12">to_js</text>
<path d="M536,166 L224,166" class="fig-arrow" marker-end="url(#ah)"/>
<text x="460" y="160" text-anchor="middle" class="fig-ink" font-family="ui-monospace, monospace" font-size="12">of_js</text>
<path d="M600,202 C560,240 200,240 150,204" class="fig-stop" marker-end="url(#ahb)"/>
<text x="380" y="244" text-anchor="middle" class="fig-bad" font-size="12">an operation that would open it (x + 1, a match): the run stops, and the call falls back</text>
</svg>
<figcaption id="fig-idea-cap">A hole crossing the boundary in mixed mode, as proposed. Going in, <code>to_js</code> turns the hole into an opaque object and keeps the Hazel term in a table; the compiled function moves the object without opening it; coming out, <code>of_js</code> gives back the very term that went in. An operation that would open it stops the compiled run, and the interpreter answers that call, as every call that cannot cross does today.</figcaption>
</figure>"""

EXAMPLES = [
    {"program": "let swap : (Int, Int) -> (Int, Int) = fun (a, b) -> (b, a) in swap(1, ?)", "today": "falls back; the interpreter answers (?, 1)", "proposed": "compiled; (?, 1), the same hole"},
    {"program": "let len : [Int] -> Int = fun xs -> case xs | [] => 0 | _ :: rest => 1 + len(rest) end in len([1, ?, 3])", "today": "falls back", "proposed": "compiled; 3"},
    {"program": "let inc : Int -> Int = fun x -> x + 1 in inc(?)", "today": "falls back; ? + 1", "proposed": "still falls back: + looks inside"},
    {"program": "type Shape = + Circle(Float) + Square(Float) in let round : Shape -> Bool = fun s -> case s | Circle(_) => true | _ => false end in round(?)", "today": "falls back; the interpreter's match is stuck", "proposed": "still falls back, by a check"},
]
FILES = [
    {"file": "src/language/dynamics/HazelJit.re", "lines": "1-60", "what": "what hazel-jit leaves to the interpreter, and why"},
    {"file": "src/language/dynamics/HazelJit.re", "lines": "60-250", "what": "the runtime: invalid, indet, limit"},
    {"file": "src/language/dynamics/HazelJit.re", "lines": "480-590", "what": "patterns compiled to tests; holes refused at 483 and 585; constructor test at 577, empty list at 529"},
    {"file": "src/language/dynamics/HazelJitValue.re", "lines": "192, 300", "what": "to_js and of_js"},
    {"file": "src/language/dynamics/HazelJitMixed.re", "lines": "136, 157, 183", "what": "fall_back, call, rewrite"},
    {"file": "test/Test_HazelJit.re", "lines": "1960-, 1989", "what": "the mixed-mode tests; a hole in the argument"},
    {"file": "test/Test_HazelJit_Agree.re", "lines": "73, 294, 317", "what": "agree, same_value, mixed_sweep"},
    {"file": "src/language/term/Atom.re (dev)", "lines": "30-32, 208", "what": "the six-decimal float equality and to_literal (hazelgrove/hazel#2831)"},
]
body = open(os.path.join(HERE, "body.html")).read().replace("{{updated}}", updated).replace("{{fig_idea}}", FIG_IDEA)
assert "{{" not in body
TITLE = "Holes Across the Boundary"
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n"
        "<meta name=\"description\" content=\"Holes in hazel-jit: in mixed mode a hole crosses into compiled code unopened and code with a hole compiles, with the interpreter's answers, casts and all; on the Witch, a hole the slide's run reaches no longer sends each edit to the interpreter.\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
json.dump({"title": TITLE, "date": "2026-11-17", "kind": "hazel-jit: a design brief (2026-11-17), then done (2026-11-25): holes in mixed mode, checked in CI and timed; merged into hazel-jit 2026-11-26; the Witch with a hole, before and after, on the prototype (2026-11-26)",
           "status": "work in progress",
           "question": "In mixed mode, can a value with a hole in it cross into compiled code and out again unopened, instead of sending the whole call back to the interpreter, and what do the checks that keep it unopened cost? From John, on the Hazel team, 2026-11-17, offering to look into holes and hazel-jit; Matthew Hammer: \"Yes, write the brief\".",
           "measurements": "Timings, one run each on GitHub's machines (the tests' mixed measured lines): hazel-jit as it was (trial/769-baseline, CI run 45722346547) against trial/769-jit-holes-2 (25c106f545, CI run 45722309881); mixed mode's time against the interpreter's in the same run. The Witch (2026-11-26): Firefox on GitHub's machines, scripts/jit_slides.py, one run each: trial/885-witch-holes-before (d0456b286f, run 45855978300) against trial/885-witch-holes (5782738954, run 45856238834).",
           "builds": [{"build": "49", "branch": "trial/694-view-jit", "pr": "hazelgrove/hazel#2817", "commit": "0e56bdbd0a", "date": "2026-11-17 10:30 MST"}, {"build": "holes", "branch": "trial/769-jit-holes-2", "pr": "off hazelgrove/hazel#2859", "commit": "25c106f545", "date": "2026-11-25"}, {"build": "before", "branch": "trial/769-baseline", "pr": "off hazelgrove/hazel#2859", "commit": "be700192ff", "date": "2026-11-25"}, {"build": "Witch 1, before", "branch": "trial/885-witch-holes-before", "pr": "off hazelgrove/hazel#2817", "commit": "d0456b286f", "date": "2026-11-26"}, {"build": "Witch 2, after", "branch": "trial/885-witch-holes", "pr": "off hazelgrove/hazel#2817", "commit": "5782738954", "date": "2026-11-26"}],
           "files": ["brief.json"]}, open(os.path.join(HERE, "data", "meta.json"), "w"), indent=1)
json.dump({"examples": EXAMPLES, "files_to_read": FILES,
           "rule_2026_11_13": "for the output of hazel-jit, we should continue to avoid translating code with holes (Matthew Hammer and Cyrus Omar's meeting)"},
          open(os.path.join(HERE, "data", "brief.json"), "w"), indent=1)
print("wrote 055/index.html", updated)
