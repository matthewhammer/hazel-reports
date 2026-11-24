#!/usr/bin/env python3
"""^report(54): Same Answers as the Interpreter. Matthew Hammer, 2026-11-16: "please draft a WIP report for me, and
publish it, with the changes we've planned for hazel-jit, and our status on those changes thus far."

The plan is Matthew and Cyrus's meeting of 2026-11-13 (Matthew's summary in chat, 2026-11-15), as dashboard tickets
756 to 763, and two found along the way (762, 764). Writes 054/index.html from body.html and the numbers below, each
from a CI log or a jit.yml run named beside it, and 054/data/numbers.json."""
import html, json, math, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s35 = open(os.path.join(ROOT, "035", "index.html")).read()
CSS = s35[s35.index("<style>") + 7: s35.index("</style>")]
EXTRA = """
  ol.outline > li { margin: 4px 0; } .muted { color: var(--muted); }
  table.vals { display: block; overflow-x: auto; max-width: 100%; border-collapse: collapse; margin: 0.6em 0 1em; font-size: 0.88em; }
  table.vals th, table.vals td { padding: 5px 8px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
  table.vals td.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; } table.vals th { font-weight: 600; }
  table.vals td:first-child { min-width: 14ch; }
  blockquote.msg { margin: 1em 0; padding: 0.4em 1.1em; border-left: 4px solid var(--accent); background: color-mix(in srgb, var(--accent) 5%, transparent); border-radius: 0 6px 6px 0; }
  figure.f { margin: 1.2em 0; } figure.f svg { max-width: 100%; }
  figcaption { color: var(--muted); font-size: 0.9em; margin-top: 6px; max-width: 80ch; }
  code { overflow-wrap: anywhere; }
  .st-done { color: #15803d; font-weight: 600; } .st-part { color: #b45309; font-weight: 600; } .st-wait { color: #6b7280; font-weight: 600; } .st-pr { color: #2563eb; font-weight: 600; }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .st-done { color: #4ade80; } :root:not([data-theme="light"]) .st-part { color: #fbbf24; } :root:not([data-theme="light"]) .st-wait { color: #9ca3af; } :root:not([data-theme="light"]) .st-pr { color: #93c5fd; } }
  :root[data-theme="dark"] .st-done { color: #4ade80; } :root[data-theme="dark"] .st-part { color: #fbbf24; } :root[data-theme="dark"] .st-wait { color: #9ca3af; } :root[data-theme="dark"] .st-pr { color: #93c5fd; }
"""
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
esc = lambda s: html.escape(s, quote=True)

# ---------------------------------------------------------------- the meeting, as Matthew summarized it (chat, 2026-11-15)
SUMMARY = [
    "we want semantic consistency with Hazel the interpreter, and to ensure that with CI, and our design decisions.",
    "arb precision Ints and Nats --- we want to use bignum in the output if we can, or something comparable, not native JS numbers for Ints and Nats.",
    "when we hit an overflow for any times where that is possible -- we should check each time for non-arb precision numbers --- we should create an indet term / stuck term with that error -- look at existing interpreter cases for inspiration.",
    "similar for divide by zero",
    "for the output of hazel-jit, we should continue to avoid translating code with holes, and we should exclude \"stepper functions\" (don't know what that is myself, please explain later).",
    "probes, step budgets, and all other limitations we should work to overcome in the coming days.",
]
CYRUS = ("We need a way to limit compiled hazel functions that diverge --- we need a step limit. esp if we continue to "
         "optimize by including certain jit-compiled hazel functions into the main thread")

# ---------------------------------------------------------------- the plan, one row a ticket; stage: how far along
# stages: 1 designed, 2 written, 3 CI green, 4 on trial/694-view-jit (or, for 764, a PR to dev)
PLAN = [
    dict(t=756, short="the same answers, checked in CI", name="Consistency with the interpreter, checked in CI", sec="consistency", stage=4, st="done",
         status="On build 49: every evaluator test program also runs compiled, and any difference fails CI; so do the slides' own programs (129: 15 compile, all agree); each program timed both ways."),
    dict(t=757, short="Int and Nat exact", name="Int and Nat exact, as the interpreter's", sec="numbers", stage=4, st="done",
         status="On the branch: a JS number while it is a safe integer, a BigInt past that. Measured on the Witch."),
    dict(t=758, short="overflow: a stuck term", name="Overflow stops at a stuck term", sec="overflow", stage=4, st="done",
         status="On the branch: SInt is 32 bits everywhere, each result checked in the interpreter and hazel-jit (decided 11-16). The interpreter's half is on a PR to dev, hazelgrove/hazel#2828: CI green, its tests reaching 96% of the changed lines; waiting on review."),
    dict(t=759, short="divide by zero: a stuck term", name="Divide by zero stops at a stuck term", sec="errors", stage=4, st="done",
         status="On the branch: the compiled run stops, and the interpreter makes the stuck term."),
    dict(t=760, short="holes, the stepper: the interpreter's", name="Holes and the stepper stay with the interpreter", sec="rules", stage=4, st="done",
         status="On the branch, with two rules the sweep found: no program with type errors, and no type hole. Left: a check in the browser."),
    dict(t=761, short="the other limits, one at a time", name="The other limits, one at a time", sec="limits", stage=4, st="part",
         status="On the branch: 20 builtins, partial application, mutual recursion, undefined, tuple extension and labels, strings in graphemes, reverse application. On their own branch, CI green 11-17: an unlabeled entry, from_lvs, a module member that is an expression, a value in a recursive definition; four programs of 313 still meet a limit, all four ill-typed tests. Probes not begun."),
    dict(t=763, short="a step budget", name="A step budget for compiled code", sec="budget", stage=4, st="done",
         status="On the branch: 50 ms or 50M calls a run, then the interpreter. Left: a cheaper counter."),
    dict(t=764, short="found: modulo by zero crashed", name="Found: modulo by zero crashed the interpreter", sec="found", stage=4, st="pr",
         status="Fixed on a PR to dev, hazelgrove/hazel#2825, waiting for review."),
    dict(t=762, short="found: undeclared result types", name="Found: an undeclared result type costs a step 5 to 7 times", sec="found", stage=1, st="wait",
         status="Measured in Hazel's interpreter; the cause is where the ascriptions go. The fix is not begun."),
    dict(t=765, short="found: slow on an older phone", name="Found: the oracles were slow on an older phone; compiled ahead of time", sec="ahead", stage=4, st="done",
         status="The I Ching and the Tarot run compiled by default (hazeljs-oracles 0.0.13), each checked against hazeljs over thousands of answers: on the phone, ready in 0.8 s, not 3.7 s. Astrology too since 0.0.16 (11-18): a chart in about 1 ms, not 1.4 s, the same as hazeljs on 40 charts. Left: the compiler inside hazeljs."),
    dict(t=766, short="next: mixed mode", name="Chosen after the meeting: mixed mode", sec="mixed", stage=1, st="part",
         status="A first step is written, on its own branch, CI green 11-17: the interpreter runs the program and calls its functions with declared types, top-level and in modules, compiled, as builtins. The Petri net rule 22 times as fast, the I Ching's 4."),
    dict(t=767, short="next: steps and probes", name="Asked 11-13: the interpreter's step counts in compiled code, then probes", sec="steps", stage=1, st="part",
         status="Designed: yes to both, with care for casts and a check in CI (below). The interpreter's counts for 57 small programs measured; the counter in compiled code not begun."),
]
STAGES = ["designed", "written", "CI green", "on the branch"]

# ---------------------------------------------------------------- the sweep: the fast checks' report on f4f969588b (job 133371195383)
SWEEP = dict(build="49", commit="0e56bdbd0a", job=134231714506, run=44137711359, checks=313, compiled=260, agreed=233, differ=0, threw=0, not_a_value=27)
NOT_COMPILED = [  # reason, count, rule or limit
    ("a hole (a label that is a hole among them)", 15, "rule"), ("a type hole", 10, "rule"),
    ("a free variable (the tests' own unbound names: y 13, s2 6, x 2, b2 2, a 1)", 24, "rule"),
    ("a fixpoint over a pattern that is not a name or a tuple of names (fix _ : (), fix (_ : Bool), fix 0; ill-typed tests)", 3, "limit"),
    ("a fixpoint over (), a tuple of no names, whose body is not a function (fix () -> []; an ill-typed test; corrected 11-18, once CI named it)", 1, "limit"),
]
SWEEP_47 = dict(build="47", commit="f4f969588b", run=43887985051, checks=313, compiled=243, agreed=216, not_a_value=27)
BY_RULE = sum(n for _, n, k in NOT_COMPILED if k == "rule")
BY_LIMIT = sum(n for _, n, k in NOT_COMPILED if k == "limit")
assert SWEEP["compiled"] == SWEEP["agreed"] + SWEEP["not_a_value"]
assert SWEEP["checks"] == SWEEP["compiled"] + BY_RULE + BY_LIMIT
FIRST_SWEEP = dict(commit="4b17e3b0ba", run=43754503317, suite="full tests", checks=316, compiled=237, agreed=207, not_a_value=30, not_compiled=79)

# ---------------------------------------------------------------- the builds measured on the Witch (jit.yml, Firefox, GitHub's machines, one run each)
BUILDS = [
    dict(b="45", name="the base", commit="fc1103900d", run=42888678269, when="11-10", adds="Report 052's last build: the slide's whole run compiled, on trial/694-view-jit.",
         step=[8, 4, 5, 4], view=5.8, jit=1.3, fps=57.0, draws=30),
    dict(b="45 + 757", name="exact integers", commit="b908b4ed2e", run=43763443448, when="11-15", adds="Int and Nat exact (ticket 757), on build 45 and ticket 756's first step.",
         step=[9, 6, 5, 4], view=6.6, jit=1.7, fps=50.7, draws=30),
    dict(b="45 + 763", name="a step budget", commit="b81b39f8d4", run=43763439842, when="11-15", adds="A counter in every compiled function, and a budget around each run (ticket 763), on build 45.",
         step=[10, 7, 5, 5], view=7.3, jit=1.5, fps=52.0, draws=30),
    dict(b="45 + 760", name="no type errors", commit="1b89af31c5", run=43765797166, when="11-15", adds="No program with type errors compiled (ticket 760), on build 45.",
         step=[5, 6, 6, 3], view=7.0, jit=1.5, fps=53.0, draws=28),
    dict(b="46", name="the six together", commit="59f28470c3", run=43792878754, when="11-15", adds="Tickets 756, 757, 759, 760, 761 and 763 merged on build 45.",
         step=[7, 10, 5, 5], view=5.4, jit=1.1, fps=59.0, draws=30),
    dict(b="47", name="a type hole is a hole", commit="f4f969588b", run=43898636577, when="11-16", adds="Build 46 and the type-hole rule (ticket 760).",
         step=[10, 7, 4, 5], view=7.2, jit=1.6, fps=49.0, draws=30),
    dict(b="48", name="the limits, SInt, label keys", commit="30a131a046", run=43949420309, when="11-16", adds="Build 47 and undefined, tuple extension and the label builtins, strings in graphemes, reverse application (761), SInt at 32 bits (758), and labels named length (765); trial/694-view-jit since 11-16.",
         step=[11, 5, 5, 11], view=6.1, jit=1.6, fps=52.6, draws=30),
    dict(b="49", name="this morning's branches", commit="0e56bdbd0a", run=44137800916, when="11-17", adds="Build 48 and the last limits (761), mixed mode's first step (766), the timing and the slides' check (756), the step calibration (767); trial/694-view-jit since 11-17, all of CI green.",
         step=[8, 12, 5, 4], view=6.8, jit=1.5, fps=53.7, draws=30),
    dict(b="50", name="the slides' builtins", commit="55e4757a4b", run=44319161252, when="11-18", adds="Build 49 and operators passed as functions, to_lvs, a projection through a list as the interpreter's, and the checks' trail (761, 756); trial/694-view-jit since 11-18.",
         step=[11, 11, 5, 5], view=6.5, jit=1.7, fps=54.3, draws=30),
]
SLIDES_760 = [("Full Body", 30, 30, 30, 30), ("Hands", 30, 30, 28, 28), ("Scenes", 36, 36, 36, 36), ("Witch", 30, 28, 30, 30)]

# ---------------------------------------------------------------- SInt today (hazeljs 0.0.6, Hazel under js_of_ocaml as in the browser)
SINT = [
    ("use SInt in 2147483647 + 1", "-2147483648", "2147483648", "2147483648"),
    ("use SInt in 65536 * 65536", "0", "4294967296", "4294967296"),
    ("use SInt in 1000000 * 1000000", "-727379968", "1000000000000", "1000000000000"),
    ("use SInt in 2 ** 31", "-2147483648", "2147483648", "2147483648"),
]

# ---------------------------------------------------------------- figures


def fig_board():
    W, L, top, rh = 700, 270, 52, 28
    H = top + rh * len(PLAN) + 14
    cols = {"done": "#15803d", "part": "#b45309", "wait": "#9ca3af", "pr": "#2563eb"}
    sx = lambda i: L + 20 + i * 108
    out = [f'<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">The plan, ticket by ticket, on {updated[:10]}</text>',
           '<text x="16" y="34" font-size="11" fill="var(--muted)">each dot a stage reached; for ticket 764 the last stage is a PR to dev, not the branch</text>']
    for i, s in enumerate(STAGES):
        out.append(f'<text x="{sx(i)}" y="{top - 6}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{esc(s)}</text>')
    for r, p in enumerate(PLAN):
        y = top + r * rh
        c = cols[p["st"]]
        out.append(f'<text x="{L - 10}" y="{y + 15}" font-size="12" text-anchor="end" fill="var(--ink)"><tspan font-weight="700">{p["t"]}</tspan> {esc(p["short"])}</text>')
        out.append(f'<line x1="{sx(0)}" y1="{y + 11}" x2="{sx(3)}" y2="{y + 11}" stroke="var(--line)" stroke-width="2"/>')
        for i in range(4):
            if i < p["stage"]:
                out.append(f'<circle cx="{sx(i)}" cy="{y + 11}" r="7" fill="{c}"/>')
            else:
                out.append(f'<circle cx="{sx(i)}" cy="{y + 11}" r="6" fill="none" stroke="{c}" stroke-width="1.6"/>')
    cap = ("Tickets 756 to 763 are the meeting's items; 762, 764 and 765 were found on the way, and 766 is the direction chosen "
           "after the meeting; 767 is the meeting's answer on steps and probes. For 765 the last stage is the oracles' pages running compiled code. Green: done on "
           "<code>trial/694-view-jit</code> (hazelgrove/hazel#2817, the hazel-jit prototype); amber: in progress; grey: "
           "waiting on a decision or not begun; blue: on a PR to dev. Not a build of the app: a status chart.")
    return (f'<figure class="f"><svg viewBox="0 0 {W} {H}" role="img" aria-label="Each ticket of the plan as a row of four stages, '
            f'filled up to the stage it has reached" style="width:100%;height:auto;display:block">' + "".join(out) +
            f"</svg><figcaption>{cap}</figcaption></figure>")


def fig_sweep():
    W, L, R = 700, 16, 16
    parts = [("agreed", SWEEP["agreed"], "#15803d"), ("not a value: ill-typed, known", SWEEP["not_a_value"], "#b45309"),
             ("not compiled, by rule", BY_RULE, "#9ca3af"), ("not compiled, a limit", BY_LIMIT, "#7c3aed")]
    tot = SWEEP["checks"]
    x, y, h = L, 50, 30
    out = [f'<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">Build {SWEEP["build"]}: the {tot} evaluator test programs, run both ways</text>',
           f'<text x="16" y="34" font-size="11" fill="var(--muted)">{SWEEP["differ"]} differ, {SWEEP["threw"]} threw: every compiled program gave the interpreter\'s answer, or is a known ill-typed test</text>']
    for name, n, c in parts:
        w = n / tot * (W - L - R)
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" fill="{c}" opacity="0.88"/>')
        if w > 34:
            out.append(f'<text x="{x + w / 2:.1f}" y="{y + 20}" font-size="12" font-weight="700" text-anchor="middle" fill="#fff">{n}</text>')
        x += w
    lx = L
    for name, n, c in parts:
        out.append(f'<rect x="{lx}" y="{y + h + 14}" width="11" height="11" fill="{c}"/>')
        out.append(f'<text x="{lx + 16}" y="{y + h + 24}" font-size="10.5" fill="var(--ink)">{esc(name)} ({n})</text>')
        lx += 16 + 6.2 * len(f"{name} ({n})") + 16
    H = y + h + 40
    cap = (f"Build {SWEEP['build']} (<code>{SWEEP['commit']}</code>), the fast checks' sweep (CI run {SWEEP['run']}). Each of the evaluator's "
           f"test programs also goes to hazel-jit: compiled and run in JavaScript, its answer compared with the interpreter's. "
           f"\"Not a value\": the interpreter stops at a failed run-time type check in an ill-typed test (4 : String, ...), which "
           f"compiled code, its types erased, would run past; the page never compiles such a program (ticket 760). By rule: "
           f"holes, type holes, and the tests' unbound names. A limit: a form hazel-jit does not compile yet (ticket 761).")
    return (f'<figure class="f"><svg viewBox="0 0 {W} {H}" role="img" aria-label="A bar of {tot} programs: {SWEEP["agreed"]} agreed, '
            f'{SWEEP["not_a_value"]} known ill-typed, {BY_RULE} not compiled by rule, {BY_LIMIT} not compiled for a limit" '
            f'style="width:100%;height:auto;display:block">' + "".join(out) + f"</svg><figcaption>{cap}</figcaption></figure>")


def fig_witch():
    rows = [b for b in BUILDS if b["view"] is not None]
    W, L, R, top, rh = 700, 170, 20, 48, 34
    H = top + rh * len(rows) + 44
    mx = 18.0
    X = lambda v: L + v / mx * (W - L - R)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">The Witch: the page\'s view a frame over a 3 s drag, by build</text>',
           '<text x="16" y="34" font-size="11" fill="var(--muted)">the view\'s time with its frame rate as if updating were free; the darker bar, hazel-jit\'s compiled run within it; one run each</text>']
    fl = X(16.7)
    out.append(f'<line x1="{fl:.1f}" y1="{top - 6}" x2="{fl:.1f}" y2="{top + rh * len(rows)}" stroke="#dc2626" stroke-width="1.6" stroke-dasharray="5 3"/>')
    out.append(f'<text x="{fl + 4:.1f}" y="{top + rh * len(rows) + 16}" font-size="10.5" text-anchor="end" fill="#dc2626">16.7 ms: a 60 fps frame</text>')
    for i, b in enumerate(rows):
        y = top + i * rh
        out.append(f'<text x="{L - 8}" y="{y + 16}" font-size="11" text-anchor="end" fill="var(--ink)">{esc(b["b"])} · {esc(b["name"])}</text>')
        out.append(f'<rect x="{L}" y="{y + 4}" width="{X(b["view"]) - L:.1f}" height="17" rx="2" fill="#0e7490" opacity="0.55"/>')
        out.append(f'<rect x="{L}" y="{y + 4}" width="{X(b["jit"]) - L:.1f}" height="17" rx="2" fill="#0e7490"/>')
        out.append(f'<text x="{X(b["view"]) + 6:.1f}" y="{y + 16}" font-size="10.5" fill="var(--muted)">{b["view"]} ms (about {round(1000 / b["view"])} fps); run {b["jit"]} ms</text>')
    cap = ("Builds 45 to 48, the Witch slide in Firefox on GitHub's machines (jit.yml), dragging the neck slider for 3 s with "
           "compiled views on: the page's view per frame, and hazel-jit's compiled run per frame within it. One run each: "
           "the spread between them (5.4 to 7.3 ms) is as large as any difference, so these say no build is measurably slower "
           "than build 45, not which is fastest.")
    return (f'<figure class="f"><svg viewBox="0 0 {W} {H}" role="img" aria-label="Bars of the Witch view time per frame for builds 45 to 48, all under 8 ms, '
            f'against a 16.7 ms line" style="width:100%;height:auto;display:block">' + "".join(out) + f"</svg><figcaption>{cap}</figcaption></figure>")


def fig_mixed():
    W, H = 720, 300
    o = ['<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--ink)"/></marker>'
         '<marker id="ahm" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#b45309"/></marker></defs>',
         '<text x="16" y="20" font-size="12.5" font-weight="700" fill="var(--ink)">Mixed mode: the interpreter calls compiled functions, as it calls a builtin</text>',
         '<text x="16" y="36" font-size="11" fill="var(--muted)">a design sketch, not built yet</text>',
         '<rect x="16" y="52" width="330" height="230" rx="8" fill="none" stroke="var(--line)" stroke-width="1.5"/>',
         '<text x="30" y="74" font-size="12" font-weight="700" fill="var(--ink)">Hazel\'s interpreter, in the worker</text>',
         '<text x="30" y="92" font-size="10.5" fill="var(--muted)">evaluates the program, around its holes, with its probes</text>']
    code = [("let rule : (Net, Int) -> Net = ...", "#15803d", "complete, typed: compiled"),
            ("let view = fun n -> ... ? ...", "#6b7280", "a hole: the interpreter's"),
            ("let total = fun xs -> ... probe ...", "#6b7280", "a probe: the interpreter's"),
            ("... rule(net, 2) ...", "var(--ink)", "a call")]
    for i, (c, col, note) in enumerate(code):
        y = 122 + i * 40
        o.append(f'<text x="30" y="{y}" font-size="11" font-family="ui-monospace,monospace" fill="{col}">{esc(c)}</text>')
        o.append(f'<text x="30" y="{y + 15}" font-size="10" fill="var(--muted)">{esc(note)}</text>')
    o += ['<rect x="474" y="96" width="230" height="120" rx="8" fill="none" stroke="#15803d" stroke-width="1.5"/>',
          '<text x="488" y="118" font-size="12" font-weight="700" fill="#15803d">Compiled functions (JS)</text>',
          '<text x="488" y="140" font-size="11" font-family="ui-monospace,monospace" fill="var(--ink)">rule</text>',
          '<text x="488" y="160" font-size="10" fill="var(--muted)">call each other directly;</text>',
          '<text x="488" y="174" font-size="10" fill="var(--muted)">each call under the step budget</text>',
          '<line x1="200" y1="240" x2="472" y2="140" stroke="var(--ink)" stroke-width="1.4" marker-end="url(#ah)"/>',
          '<text x="352" y="170" font-size="10" fill="var(--ink)" text-anchor="middle" transform="rotate(-20 352 170)">the argument, to JS once</text>',
          '<line x1="474" y1="176" x2="230" y2="252" stroke="var(--ink)" stroke-width="1.4" marker-end="url(#ah)"/>',
          '<text x="380" y="228" font-size="10" fill="var(--ink)" text-anchor="middle" transform="rotate(-17 380 228)">the answer, by its declared type</text>',
          '<path d="M 500 216 C 500 292, 300 298, 250 264" fill="none" stroke="#b45309" stroke-width="1.4" stroke-dasharray="5 3" marker-end="url(#ahm)"/>',
          '<text x="704" y="236" font-size="10.5" text-anchor="end" fill="#b45309">a stop (the budget, an invalid</text>',
          '<text x="704" y="250" font-size="10.5" text-anchor="end" fill="#b45309">operation, a value that will</text>',
          '<text x="704" y="264" font-size="10.5" text-anchor="end" fill="#b45309">not convert): the Hazel</text>',
          '<text x="704" y="278" font-size="10.5" text-anchor="end" fill="#b45309">function runs instead</text>']
    cap = ("Not a build of the app: a design sketch. The interpreter keeps running the program, with its holes and probes; "
           "a function whose body is complete, has its whole type declared and holds no probe is compiled once, and the "
           "interpreter calls it as it calls a builtin. Any stop falls back for that one call, to the same Hazel function.")
    return (f'<figure class="f"><svg viewBox="0 0 {W} {H}" role="img" aria-label="The interpreter, running a program with a hole and a probe, '
            f'calls a compiled function in JS, converting the argument in and the answer back, and falls back to the Hazel function on a stop" '
            f'style="width:100%;height:auto;display:block">' + "".join(o) + f"</svg><figcaption>{cap}</figcaption></figure>")


# ---------------------------------------------------------------- tables


def plan_table():
    cls = {"done": "st-done", "part": "st-part", "wait": "st-wait", "pr": "st-pr"}
    word = {"done": "done", "part": "in progress", "wait": "waiting", "pr": "on a PR"}
    rows = ["<tr><th>Ticket</th><th>The change</th><th>Where it stands</th><th></th></tr>"]
    for p in PLAN:
        rows.append(f'<tr><td>ticket {p["t"]}</td><td><a href="#{p["sec"]}">{esc(p["name"])}</a></td><td>{esc(p["status"])}</td>'
                    f'<td class="{cls[p["st"]]}">{word[p["st"]]}</td></tr>')
    return '<table class="vals">' + "".join(rows) + "</table>"


def sweep_table():
    rows = ["<tr><th>Not compiled because</th><th>Programs</th><th>Rule or limit</th></tr>"]
    for r, n, k in NOT_COMPILED:
        rows.append(f"<tr><td>{esc(r)}</td><td class=\"n\">{n}</td><td>{'rule' if k == 'rule' else 'a limit (ticket 761)'}</td></tr>")
    return '<table class="vals">' + "".join(rows) + "</table>"


def sint_table():
    rows = ["<tr><th>Program</th><th>The browser's interpreter (32 bits, wraps)</th><th>A native build (OCaml's 63-bit int)</th><th>hazel-jit (a JS number)</th></tr>"]
    for p, a, b, c in SINT:
        rows.append(f"<tr><td><code>{esc(p)}</code></td><td class=\"n\">{a}</td><td class=\"n\">{b}</td><td class=\"n\">{c}</td></tr>")
    return '<table class="vals">' + "".join(rows) + "</table>"


def slides_table():
    rows = ["<tr><th>Slide</th><th>Livelits drawn from the compiled run, build 45</th><th>With the type-error rule (45 + 760)</th><th>Build 47, with the type-hole rule</th><th>Build 48</th></tr>"]
    for s, a, b, c, e in SLIDES_760:
        rows.append(f"<tr><td>{s}</td><td class=\"n\">{a}</td><td class=\"n\">{b}</td><td class=\"n\">{c}</td><td class=\"n\">{e}</td></tr>")
    return '<table class="vals">' + "".join(rows) + "</table>"


def builds_table():
    rows = ["<tr><th>Build</th><th>Commit</th><th>Run</th><th>When</th><th>What it adds</th><th>View a frame (drag)</th><th>Compiled run a frame</th><th>Compiled run at a step</th><th>Drawn from the compiled run</th></tr>"]
    for b in BUILDS:
        if b["view"] is None:
            m = ['<td class="n" colspan="4">being measured</td>']
        else:
            m = [f'<td class="n">{b["view"]} ms (about {round(1000 / b["view"])} fps)</td>', f'<td class="n">{b["jit"]} ms</td>',
                 f'<td class="n">{min(b["step"])} to {max(b["step"])} ms</td>', f'<td class="n">{b["draws"]}</td>']
        rows.append(f'<tr><td><b>{esc(b["b"])}</b> · {esc(b["name"])}</td><td><code>{b["commit"]}</code></td><td>{b["run"]}</td><td>{b["when"]}</td>'
                    f'<td>{esc(b["adds"])}</td>' + "".join(m) + "</tr>")
    return '<table class="vals">' + "".join(rows) + "</table>"


# ---------------------------------------------------------------- mixed mode's first step (ticket 766): CI's report on its branch
# measured: (program, the interpreter alone ms, mixed ms, rewrite and compile ms, functions compiled, calls compiled, fell back)
MIXED = dict(branch="trial/694-build-49", commit="0e56bdbd0a", run=44137711359,
             sweep=dict(programs=6, functions=7, agreed=6, differ=0, failed=0, calls=16843, fell=2, undeclared=29),
             measured=[("fib(16), all compiled", 72.6, 0.1, 0.5, 1, 1, 0),
                       ("the Petri net rule of report 043, whole types declared, 100 events from an interpreted loop", 120.8, 16.8, 5.5, 12, 112, 0),
                       ("the I Ching of hazeljs-oracles, 200 readings from an interpreted loop", 1117.5, 235.0, 3.7, 13, 7800, 0),
                       ("500 calls of a one-line function (sq) from an interpreted loop", 22.4, 27.9, 0.2, 1, 500, 0)])


def mixed_status():
    if MIXED["commit"] is None:
        return "Its CI is running; what it finds goes here."
    sw = MIXED["sweep"]
    return (f"On <code>{MIXED['commit']}</code> (CI run {MIXED['run']}, green), the consistency check found {sw['programs']} evaluator programs "
            f"with a function to compile ({sw['functions']} functions), and all {sw['agreed']} gave the interpreter's answer; "
            f"{sw['undeclared']} other functions were left to the interpreter because their whole type is not declared, which bears on the "
            f"question of which functions to compile. Measured on larger programs (below): a recursion compiled whole runs hundreds of times "
            f"as fast; the Petri net rule 7 times (22 times on the branch's own run, where the interpreter took 463 ms rather than 121: these are single runs, and noisy); the I Ching 5 times, since only 13 of its functions compile so far (its readings call "
            f"other modules' members, Lines.becomes, which the rewrite does not see yet); and a one-line function called 500 times from "
            f"interpreted code is slower than not compiling it, each call's crossing costing more than its work.")


def mixed_table():
    if not MIXED["measured"]:
        return ""
    rows = ["<tr><th>Program</th><th>The interpreter alone</th><th>Mixed</th><th>Rewrite and compile, once</th><th>Functions compiled</th><th>Calls compiled</th><th>Fell back</th></tr>"]
    for name, a, b, c, f, k, fb in MIXED["measured"]:
        rows.append(f'<tr><td>{esc(name)}</td><td class="n">{a:.1f} ms</td><td class="n">{b:.1f} ms</td><td class="n">{c:.1f} ms</td>'
                    f'<td class="n">{f}</td><td class="n">{k}</td><td class="n">{fb}</td></tr>')
    cap = (f"Build 49 (<code>{MIXED['commit']}</code>, CI run {MIXED['run']}, Node on GitHub's machines), each program once after a first run, not repeated as the evaluator's programs are; "
           "the same answer both ways checked. Not a build of the app.")
    return '<table class="vals">' + "".join(rows) + f'</table><p class="muted">{cap}</p>'


# ---------------------------------------------------------------- the evaluator's programs timed both ways (Matthew, 2026-11-17: "please
# time the tests in interpreter vs jit and present those results in report 54"): the sweep's timing lines, from CI's log
TIMING = dict(commit="0e56bdbd0a", run=44137711359, file=os.path.join(HERE, "data", "timing.tsv"))


def timing_rows():
    if not os.path.exists(TIMING["file"]):
        return []
    rows = []
    for line in open(TIMING["file"]):
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 10 or parts[0] != "hazel-jit time":
            continue
        rows.append(dict(interp1=float(parts[1]), interp=float(parts[2]), interp_n=int(parts[3]), compile=float(parts[4]),
                         parse=float(parts[5]), run1=float(parts[6]), run=float(parts[7]), run_n=int(parts[8]), test=parts[9]))
    return rows


TROWS = timing_rows()


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def timing_numbers():
    if not TROWS:
        return {}
    tot = lambda k: sum(r[k] for r in TROWS)
    ratio = lambda r: r["interp"] / max(r["run"], 1e-6)
    first = lambda r: r["parse"] + r["run1"]
    return dict(n=len(TROWS), interp=tot("interp"), run=tot("run"), interp1=tot("interp1"), compile=tot("compile"),
                first=sum(first(r) for r in TROWS), med_interp=median([r["interp"] for r in TROWS]), med_run=median([r["run"] for r in TROWS]),
                med_ratio=median([ratio(r) for r in TROWS]), lo_ratio=min(ratio(r) for r in TROWS), hi_ratio=max(ratio(r) for r in TROWS),
                med_ratio1=median([r["interp1"] / max(first(r), 1e-3) for r in TROWS]),
                med_ratio_c=median([r["interp1"] / max(r["compile"] + first(r), 1e-3) for r in TROWS]),
                slower1=sum(1 for r in TROWS if r["compile"] + first(r) > r["interp1"]),
                min_n=min(r["interp_n"] for r in TROWS), max_n=max(r["interp_n"] for r in TROWS))


TN = timing_numbers()


def fig_timing():
    if not TROWS:
        return '<p class="muted">The timings are being measured; they go here.</p>'
    import math
    W, L, R, T, B = 700, 70, 20, 44, 52
    H = 430
    xs = [max(r["interp"], 1e-5) for r in TROWS]
    ys = [max(r["run"], 1e-5) for r in TROWS]
    lo = math.floor(math.log10(min(min(xs), min(ys))))
    hi = math.ceil(math.log10(max(max(xs), max(ys))))
    sx = lambda v: L + (math.log10(v) - lo) / (hi - lo) * (W - L - R)
    sy = lambda v: H - B - (math.log10(v) - lo) / (hi - lo) * (H - T - B)
    out = [f'<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">The evaluator\'s {len(TROWS)} programs, a run\'s time each way</text>',
           '<text x="16" y="34" font-size="11" fill="var(--muted)">each dot a program, each time a run\'s, over its repeats: across, the interpreter; up, the compiled JS</text>']
    for e in range(lo, hi + 1):
        v = 10 ** e
        lab = f"{v:g} ms" if v >= 0.001 else f"{v * 1000:g} µs"
        out.append(f'<line x1="{sx(v):.1f}" y1="{T}" x2="{sx(v):.1f}" y2="{H - B}" stroke="var(--line)" stroke-width="0.6"/>')
        out.append(f'<line x1="{L}" y1="{sy(v):.1f}" x2="{W - R}" y2="{sy(v):.1f}" stroke="var(--line)" stroke-width="0.6"/>')
        out.append(f'<text x="{sx(v):.1f}" y="{H - B + 14}" font-size="10" text-anchor="middle" fill="var(--muted)">{lab}</text>')
        out.append(f'<text x="{L - 6}" y="{sy(v) + 3:.1f}" font-size="10" text-anchor="end" fill="var(--muted)">{lab}</text>')
    a, b = 10 ** lo, 10 ** hi
    for k, name in [(1, "as fast"), (100, "100 times as fast"), (10000, "10,000 times")]:
        x1 = max(a, a * k)
        if x1 >= b:
            continue
        out.append(f'<line x1="{sx(x1):.1f}" y1="{sy(x1 / k):.1f}" x2="{sx(b):.1f}" y2="{sy(b / k):.1f}" stroke="var(--muted)" stroke-width="1" stroke-dasharray="4 3"/>')
        out.append(f'<text x="{sx(b) - 4:.1f}" y="{sy(b / k) - 5:.1f}" font-size="10" text-anchor="end" fill="var(--muted)">{name}</text>')
    for x, y in zip(xs, ys):
        out.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="3" fill="#2563eb" fill-opacity="0.55"/>')
    out.append(f'<text x="{(L + W - R) / 2:.0f}" y="{H - 14}" font-size="11" text-anchor="middle" fill="var(--ink)">the interpreter, a run</text>')
    out.append(f'<text x="14" y="{(T + H - B) / 2:.0f}" font-size="11" text-anchor="middle" fill="var(--ink)" transform="rotate(-90 14 {(T + H - B) / 2:.0f})">compiled JS, a run</text>')
    cap = (f"Build 49 (<code>{TIMING['commit']}</code>, CI run {TIMING['run']}, the fast checks, "
           f"Node on GitHub's machines). Each program's interpreter runs repeated until they added to 20 ms ({TN['min_n']} to {TN['max_n']} times), "
           "and its compiled JS's until they added to 5 ms; each dot is a run's time, the total over the repeats. Below the line marked "
           "\"as fast\", compiled code was faster. Not a build of the app.")
    return (f'<figure class="f"><svg viewBox="0 0 {W} {H}" role="img" aria-label="A scatter of {len(TROWS)} programs on log scales, '
            f'the interpreter\'s time a run across and the compiled JS\'s up" style="width:100%;height:auto;display:block">' + "".join(out) +
            f"</svg><figcaption>{cap}</figcaption></figure>")


def timing_table():
    if not TROWS:
        return ""
    top = sorted(TROWS, key=lambda r: -r["interp"])[:12]
    def f(v):
        return f"{v:.1f} ms" if v >= 10 else f"{v:.2f} ms" if v >= 0.1 else f"{v * 1000:.1f} µs" if v >= 0.001 else f"{v * 1000:.2f} µs"
    rows = ["<tr><th>Program (the evaluator's test)</th><th>The interpreter, a run</th><th>Compiled JS, a run</th><th>As fast, times</th>"
            "<th>First runs: the interpreter</th><th>hazel-jit's compile</th><th>The JS parsed and run</th></tr>"]
    for r in top:
        name = r["test"] if len(r["test"]) <= 64 else r["test"][:61] + "..."
        rows.append(f'<tr><td><code>{esc(name)}</code></td><td class="n">{f(r["interp"])} <span class="muted">×{r["interp_n"]}</span></td>'
                    f'<td class="n">{f(r["run"])} <span class="muted">×{r["run_n"]}</span></td><td class="n">{r["interp"] / max(r["run"], 1e-6):,.0f}</td>'
                    f'<td class="n">{f(r["interp1"])}</td><td class="n">{f(r["compile"])}</td><td class="n">{f(r["parse"] + r["run1"])}</td></tr>')
    return '<table class="vals">' + "".join(rows) + "</table>"


def timing_summary():
    if not TN:
        return "Measuring; the numbers go here."
    big = [r for r in TROWS if r["interp"] >= 0.1]
    big_med = median([r["interp"] / max(r["run"], 1e-6) for r in big]) if big else 0
    return (f"Run again and again, the {TN['n']} evaluator programs that compile and give the interpreter's value took the interpreter "
            f"{TN['interp']:.0f} ms a run in all, and compiled code {TN['run']:.2f} ms. The median program is {TN['med_ratio']:,.0f} times as fast "
            f"compiled ({TN['med_interp'] * 1000:.0f} µs against {TN['med_run'] * 1000:.2f} µs), and every one is faster, from {TN['lo_ratio']:.1f} "
            f"to {TN['hi_ratio']:,.0f} times; the {len(big)} that take the interpreter 0.1 ms or more, a median {big_med:,.0f} times. Run once, "
            f"compiling included, as a page that compiles before its first run would, the median program is {TN['med_ratio_c']:.1f} times as fast, "
            f"and {TN['slower1']} of the {TN['n']} are slower: programs of a few microseconds, where compiling is the cost.")


# the slides' programs, timed the same way (the slides' check, Test_HazelJit, on build 49): "hazel-jit slide time" lines
SLIDES_T = dict(file=os.path.join(HERE, "data", "slide-timing.tsv"),
                summary="of the 129 programs under hazel-programs, 21 have a static error and stay with the interpreter, as do those with a hole (27), a type hole (25) or a test (25); 10 call to_lvs and 4 int_plus, builtins hazel-jit lacks; ")


def slide_rows():
    if not os.path.exists(SLIDES_T["file"]):
        return []
    rows = []
    for line in open(SLIDES_T["file"]):
        p = line.rstrip("\n").split("\t")
        if len(p) < 9 or p[0] != "hazel-jit slide time":
            continue
        rows.append(dict(interp1=float(p[1]), interp=float(p[2]), interp_n=int(p[3]), parse=float(p[4]), run1=float(p[5]),
                         run=float(p[6]), run_n=int(p[7]), path=p[8]))
    return rows


SROWS = slide_rows()


def slide_table():
    if not SROWS:
        return ""
    def f(v):
        return f"{v:.1f} ms" if v >= 10 else f"{v:.2f} ms" if v >= 0.1 else f"{v * 1000:.1f} µs" if v >= 0.001 else f"{v * 1000:.2f} µs"
    rows = ["<tr><th>Program (hazel-programs/)</th><th>The interpreter, a run</th><th>Compiled JS, a run</th><th>As fast, times</th>"
            "<th>First runs: the interpreter</th><th>The JS parsed and run</th></tr>"]
    for r in sorted(SROWS, key=lambda r: -r["interp"]):
        name = r["path"].replace("hazel-programs/", "").replace("../", "")
        rows.append(f'<tr><td><code>{esc(name)}</code></td><td class="n">{f(r["interp"])} <span class="muted">×{r["interp_n"]}</span></td>'
                    f'<td class="n">{f(r["run"])} <span class="muted">×{r["run_n"]}</span></td><td class="n">{r["interp"] / max(r["run"], 1e-6):,.0f}</td>'
                    f'<td class="n">{f(r["interp1"])}</td><td class="n">{f(r["parse"] + r["run1"])}</td></tr>')
    return '<table class="vals">' + "".join(rows) + "</table>"


def slide_summary():
    if not SROWS:
        return "The slides' own programs are being timed the same way, on build 49; they go here."
    tot = lambda k: sum(r[k] for r in SROWS)
    ratios = sorted(r["interp"] / max(r["run"], 1e-6) for r in SROWS)
    med = ratios[len(ratios) // 2]
    head = SLIDES_T["summary"] or ""
    return (f"The slides' own programs, timed the same way on build 49: {head}the {len(SROWS)} that compile and give the interpreter's "
            f"value took the interpreter {tot('interp'):.1f} ms a run in all and compiled code {tot('run'):.3f} ms, the median program "
            f"{med:,.0f} times as fast.")


# ---------------------------------------------------------------- (ticket 767) the interpreter's step counts for small programs, each a
# construct apart from the last (Test_HazelJit's calibration, CI run 44131334098, on trial/767-steps df87481567)
CALIB = dict(commit="df87481567", run=44131334098)
CROWS = [(int(l.split("\t", 1)[0]), l.rstrip("\n").split("\t", 1)[1]) for l in open(os.path.join(HERE, "data", "steps.tsv")) if "\t" in l]
# the pairs that show one construct's own cost: (what, the program with it, the program without)
CPAIRS = [
    ("a literal", "1", None),
    ("an operator", "1 + 2", "1"),
    ("parentheses", "(1)", "1"),
    ("a let (binding, its pattern, closing its closure), less its parts", "let x = 1 in 2", None),
    ("a call of a named function", "let f = fun x -> x in f(f(1))", "let f = fun x -> x in f(1)"),
    ("a level of recursion, if n == 0 then 0 else f(n - 1)", "let f = fun n -> if n == 0 then 0 else f(n - 1) in f(1)", "let f = fun n -> if n == 0 then 0 else f(n - 1) in f(0)"),
    ("a declared Int -> Int, a call", "let f : Int -> Int = fun x -> x in f(f(1))", "let f = fun x -> x in f(f(1))"),
]


def calib_table():
    rows = ["<tr><th>Program</th><th>Steps</th></tr>"]
    for n, src in CROWS:
        rows.append(f'<tr><td><code>{esc(src)}</code></td><td class="n">{n}</td></tr>')
    return '<table class="vals">' + "".join(rows) + "</table>"


def summary_block():
    li = "".join(f"<li>{esc(s)}</li>" for s in SUMMARY)
    return f'<blockquote class="msg"><ul>{li}</ul></blockquote>'


# ---- lists as JS arrays: the microbenchmark (^ticket(795), 2026-11-23)
LB = json.load(open(os.path.join(HERE, "data", "lists-bench.json")))
def us(v): return f"{v:.3f} µs" if v < 1 else (f"{v:.1f} µs" if v < 100 else f"{v:,.0f} µs")
def fig_lists():
    rows = [r for r in LB["rows"] if r["n"] == 1000]
    W, x0, x1 = 720, 300, 700
    lo, hi = -3, 4
    X = lambda v: x0 + (math.log10(max(v, 10 ** lo)) - lo) / (hi - lo) * (x1 - x0)
    o = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">A list of 1,000 Ints, three ways in compiled code: microseconds, log scale</text>']
    for e, lab in [(-3, "1 ns"), (-1, "0.1 µs"), (1, "10 µs"), (3, "1 ms")]:
        o.append(f'<line x1="{X(10 ** e):.1f}" y1="28" x2="{X(10 ** e):.1f}" y2="{40 + len(rows) * 40}" stroke="var(--line)"/>'
                 f'<text x="{X(10 ** e):.1f}" y="{52 + len(rows) * 40}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{lab}</text>')
    for i, r in enumerate(rows):
        y = 34 + i * 40
        o.append(f'<text x="16" y="{y + 20}" font-size="11.5" fill="var(--ink)">{esc(r["workload"])}</text>')
        for k, (w, col) in enumerate((("cells", "#6b7280"), ("arrays", "#c2410c"), ("hybrid", "#2a78d6"))):
            v = r[w]; yy = y + 2 + k * 11
            o.append(f'<rect x="{x0}" y="{yy}" width="{X(v) - x0:.1f}" height="9" fill="{col}"><title>{w}: {us(v)}</title></rect>'
                     f'<text x="{X(v) + 4:.1f}" y="{yy + 8}" font-size="9.5" fill="var(--muted)">{us(v)}</text>')
    y = 62 + len(rows) * 40
    for k, (w, col, what) in enumerate((("cells", "#6b7280", "cells {h, t}, today"), ("arrays", "#c2410c", "arrays, copied by ::"), ("hybrid", "#2a78d6", "cells, a tail an array segment"))):
        o.append(f'<rect x="{16 + k * 230}" y="{y}" width="10" height="10" fill="{col}"/><text x="{30 + k * 230}" y="{y + 9}" font-size="11" fill="var(--muted)">{what}</text>')
    return f'<svg viewBox="0 0 {W} {y + 18}" role="img" aria-label="Microseconds for eight list workloads on 1,000 elements, cells, arrays and the hybrid">' + "".join(o) + "</svg>"
def lists_table():
    body = "".join(f'<tr><td>{r["n"]:,}</td><td>{esc(r["workload"])}</td><td>{us(r["cells"])}</td><td>{us(r["arrays"])}</td><td>{us(r["hybrid"])}</td></tr>' for r in LB["rows"])
    return ('<table class="nums"><thead><tr><th>elements</th><th>workload</th><th>cells (today)</th><th>arrays</th><th>hybrid</th></tr></thead>'
            f'<tbody>{body}</tbody></table>')

# ---- lists as JavaScript arrays, on the games: cells (build hazeljs 3f1d825455) against the hybrid (hazeljs-lists 46b42696f6),
# the same runner for both, one runner a game (hazeljs-examples bench/lists-hybrid, run 45258983579)
LG_NAME = {"i-ching": "I Ching", "tarot": "Tarot", "astrology": "Astrology", "checkers": "Checkers", "go": "Go", "minesweeper": "Minesweeper",
           "mahjong": "Mahjong", "solitaire": "Solitaire", "mahjong-solitaire": "Mahjong solitaire", "pinball": "Pinball", "downhill": "Downhill",
           "bricks": "Bricks", "snake": "Snake", "trails": "Light trails", "starwave": "Star wave", "bugs": "Butterfly garden", "dig": "Gnome dig"}
LG = []
for g in LG_NAME:
    a = json.load(open(os.path.join(HERE, "data", "lists-games", f"{g}-cells.json")))
    b = json.load(open(os.path.join(HERE, "data", "lists-games", f"{g}-hybrid.json")))
    for oa, ob in zip(a["ops"], b["ops"]):
        assert oa["name"] == ob["name"] and all(w is None or w.get("same") for w in list(oa["ways"].values()) + list(ob["ways"].values()))
        LG.append({"game": g, "op": oa["name"], "cells_jit": oa["ways"]["jit"]["ms"], "hybrid_jit": ob["ways"]["jit"]["ms"],
                   "cells_aot": oa["ways"]["compiled"]["ms"], "hybrid_aot": ob["ways"]["compiled"]["ms"], "cpu": a["machine"]["model"]})
LG_GM = lambda k1, k2: math.exp(sum(math.log(r[k2] / r[k1]) for r in LG) / len(LG))
def fig_lists_games():
    W, x0, x1 = 720, 330, 700
    lo, hi = math.log10(0.5), math.log10(2)
    X = lambda v: x0 + (math.log10(v) - lo) / (hi - lo) * (x1 - x0)
    o = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">The hybrid lists against cells, every game: time with the hybrid ÷ time with cells</text>']
    rows = sorted(LG, key=lambda r: r["hybrid_aot"] / r["cells_aot"])
    top, step = 40, 15
    for v, lab in [(0.5, "½ the time"), (1, "the same"), (2, "twice")]:
        sw = "2" if v == 1 else "1"
        o.append(f'<line x1="{X(v):.1f}" y1="{top - 8}" x2="{X(v):.1f}" y2="{top + len(rows) * step}" stroke="var(--line)" stroke-width="{sw}"/>'
                 f'<text x="{X(v):.1f}" y="{top - 12}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{lab}</text>')
    for i, r in enumerate(rows):
        y = top + i * step
        lab = f'{LG_NAME[r["game"]]}: {r["op"]}'; lab = lab if len(lab) <= 48 else lab[:46] + "…"
        a, j = r["hybrid_aot"] / r["cells_aot"], r["hybrid_jit"] / r["cells_jit"]
        o.append(f'<text x="16" y="{y + 9}" font-size="10.5" fill="var(--ink)">{esc(lab)}</text>'
                 f'<circle cx="{X(j):.1f}" cy="{y + 5}" r="3.6" fill="#eb6834"><title>jit: {j:.2f}×</title></circle>'
                 f'<circle cx="{X(a):.1f}" cy="{y + 5}" r="3.6" fill="#2a78d6"><title>ahead of time: {a:.2f}×</title></circle>')
    y = top + len(rows) * step + 14
    o.append(f'<circle cx="22" cy="{y}" r="4" fill="#2a78d6"/><text x="30" y="{y + 4}" font-size="11" fill="var(--muted)">compiled ahead of time</text>'
             f'<circle cx="202" cy="{y}" r="4" fill="#eb6834"/><text x="210" y="{y + 4}" font-size="11" fill="var(--muted)">through the jit (values crossing through Hazel’s)</text>')
    return f'<svg viewBox="0 0 {W} {y + 14}" role="img" aria-label="For each of 45 operations of 17 games, the time with hybrid lists divided by the time with cells, compiled and through the jit">' + "".join(o) + "</svg>"
def lists_games_table():
    body = "".join(f'<tr><td>{esc(LG_NAME[r["game"]])}: {esc(r["op"])}</td><td>{us(r["cells_aot"] * 1000)}</td><td>{us(r["hybrid_aot"] * 1000)}</td><td>{r["hybrid_aot"] / r["cells_aot"]:.2f}</td>'
                   f'<td>{us(r["cells_jit"] * 1000)}</td><td>{us(r["hybrid_jit"] * 1000)}</td><td>{r["hybrid_jit"] / r["cells_jit"]:.2f}</td></tr>' for r in LG)
    return ('<div style="overflow-x:auto"><table class="nums"><thead><tr><th>operation</th><th>ahead of time, cells</th><th>ahead of time, hybrid</th><th>ratio</th>'
            f'<th>jit, cells</th><th>jit, hybrid</th><th>ratio</th></tr></thead><tbody>{body}</tbody></table></div>')

# ---- a page's list in and back out, through hazel-jit's compiled identity, at every size (^report(54); Matthew, 2026-11-23:
# "the round trip of going from the outer JS main thread, into the JIT code, and back again, for each representation, at
# different sizes ... plots where sequence size is the X axis, and Y axis is time cost ... maybe both log and linear scale
# for each plot, and let me decide which is more informative")
CR = json.load(open(os.path.join(HERE, "data", "crossing.json")))
CR_WAYS = [("arrays, no conversion", "#15803d", "arrays, no conversion"),
           ("hybrid (cells + array segments)", "#2a78d6", "hybrid: cells + array segments"),
           ("arrays, copied", "#7c3aed", "arrays, copied each way"),
           ("arrays of records, each converted", "#a16207", "arrays, each record converted"),
           ("cells, converted", "#6b7280", "cells (today, ahead of time)"),
           ("through Hazel's values (the jit)", "#eb6834", "Hazel's values (today's jit)"),
           ("the interpreter (Hazel.run)", "#b91c1c", "the interpreter")]
def cr_series(kind):
    rows = [r for r in CR["rows"] if r["kind"] == kind]
    return [(lab, col, [(r["n"], r[k]) for r in rows if r.get(k) is not None]) for k, col, lab in CR_WAYS if any(r.get(k) is not None for r in rows)]
def fmt_ms(v):
    if v == 0: return "0"
    if v >= 1000: return f"{v / 1000:g} s"
    if v >= 1: return f"{v:g} ms"
    if v >= 0.001: return f"{v * 1000:g} µs"
    return f"{v * 1e6:g} ns"
def fig_crossing(kind, log):
    ser = cr_series(kind)
    W, H, x0, x1, y0, y1 = 720, 330, 70, 520, 296, 24
    xs = [n for _, _, pts in ser for n, _ in pts]; ys = [v for _, _, pts in ser for _, v in pts]
    if log:
        lx0, lx1 = 0, 6
        ly0, ly1 = math.floor(math.log10(min(ys))), math.ceil(math.log10(max(ys)))
        X = lambda n: x0 + (math.log10(n) - lx0) / (lx1 - lx0) * (x1 - x0)
        Y = lambda v: y0 - (math.log10(v) - ly0) / (ly1 - ly0) * (y0 - y1)
        xt = [(10 ** e, f"{10 ** e:,}") for e in range(0, 7)]
        yt = [(10 ** e, fmt_ms(10 ** e)) for e in range(ly0, ly1 + 1)]
    else:
        mx, my = max(xs), max(ys)
        X = lambda n: x0 + n / mx * (x1 - x0)
        Y = lambda v: y0 - v / my * (y0 - y1)
        xt = [(k * mx / 4, f"{int(k * mx / 4):,}") for k in range(0, 5)]
        raw = my / 5; base = 10 ** math.floor(math.log10(raw)); step = next(m * base for m in (1, 2, 5, 10) if m * base >= raw)
        yt = [(k * step, fmt_ms(k * step)) for k in range(0, int(my / step) + 1)]
    o = []
    for v, lab in yt:
        o.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="var(--line)"/><text x="{x0 - 6}" y="{Y(v) + 3.5:.1f}" font-size="10" text-anchor="end" fill="var(--muted)">{lab}</text>')
    for v, lab in xt:
        o.append(f'<line x1="{X(v):.1f}" y1="{y0}" x2="{X(v):.1f}" y2="{y0 + 4}" stroke="var(--muted)"/><text x="{X(v):.1f}" y="{y0 + 16}" font-size="10" text-anchor="middle" fill="var(--muted)">{lab}</text>')
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="var(--muted)"/><line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="var(--muted)"/>'
             f'<text x="{(x0 + x1) / 2}" y="{y0 + 32}" font-size="11" text-anchor="middle" fill="var(--ink)">elements in the list{" (log scale)" if log else ""}</text>'
             f'<text x="14" y="{(y0 + y1) / 2}" font-size="11" text-anchor="middle" fill="var(--ink)" transform="rotate(-90 14 {(y0 + y1) / 2})">time, in and back out{" (log)" if log else ""}</text>')
    for i, (lab, col, pts) in enumerate(ser):
        d = " ".join(f"{'M' if j == 0 else 'L'}{X(n):.1f},{Y(v):.1f}" for j, (n, v) in enumerate(pts))
        o.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2"/>' + "".join(
            f'<circle cx="{X(n):.1f}" cy="{Y(v):.1f}" r="3" fill="{col}"><title>{esc(lab)}, {n:,} elements: {fmt_ms(round(v, 6 if v < 1 else 2))}</title></circle>' for n, v in pts))
        ly = 34 + i * 20
        o.append(f'<line x1="532" y1="{ly}" x2="552" y2="{ly}" stroke="{col}" stroke-width="2.5"/><text x="557" y="{ly + 4}" font-size="10.5" fill="var(--ink)">{esc(lab)}</text>')
    what = "Ints" if kind == "ints" else "records (x = Int, y = Int)"
    o.insert(0, f'<text x="{x0}" y="14" font-size="12.5" font-weight="700" fill="var(--ink)">A list of {what}, into compiled code and back out: {"log-log" if log else "linear"}</text>')
    return f'<svg viewBox="0 0 {W} {H + 16}" role="img" aria-label="Time to pass a list of {what} into hazel-jit\'s compiled identity and back, against its size, {"log-log" if log else "linear"} scales, one line a representation">' + "".join(o) + "</svg>"
def crossing_table():
    keys = [k for k, _, _ in CR_WAYS]
    head = "".join(f"<th>{esc(lab)}</th>" for _, _, lab in CR_WAYS)
    body = "".join(f'<tr><td>{"Ints" if r["kind"] == "ints" else "records"}</td><td>{r["n"]:,}</td>' + "".join(
        f'<td>{fmt_ms(round(r[k], 6 if r[k] < 1 else 2)) if r.get(k) is not None else "–"}</td>' for k in keys) + "</tr>" for r in CR["rows"])
    return f'<div style="overflow-x:auto"><table class="nums"><thead><tr><th>list of</th><th>elements</th>{head}</tr></thead><tbody>{body}</tbody></table></div>'

# ---- (^ticket(847), 2026-11-24) records the page's way: the shapes timed in JavaScript alone (054/drivers/records-bench.mjs),
# and how much of each game's state is records (054/drivers/game-shapes.mjs)
RB = json.load(open(os.path.join(HERE, "data", "records.json")))
GS = json.load(open(os.path.join(HERE, "data", "game-shapes.json")))["games"]
RBR = {r["name"]: r for r in RB["rows"]}
K_CHECK, K_EQ = "as objects: each field's type checked going in, no copy", "as objects, compared by the type's fields"
GNAME = {"checkers": "Checkers", "go": "Go", "minesweeper": "Minesweeper", "mahjong": "Mahjong", "solitaire": "Solitaire", "mahjong-solitaire": "Mahjong solitaire",
         "pinball": "Pinball", "downhill": "Downhill", "bricks": "Bricks", "snake": "Snake", "trails": "Light trails", "starwave": "Star wave", "bugs": "Butterfly garden", "dig": "Gnome dig"}
def ns(v): return f"{v:.1f} ns" if v < 100 else (f"{v:,.0f} ns" if v < 1000 else f"{v / 1000:.1f} µs")
def records_table():
    per = lambda name, k, n=1: RBR[name][k] / n
    C = RB["cellsNs"]; X = RB["crossMs"]
    rows = [
        ("make a record of four fields", ns(per("make a record of four fields", "today")), ns(per("make a record of four fields", "objects")), "an object literal, against the runtime’s <code>tup</code> adding each label to an array"),
        ("a new record with one field changed", ns(per("update one field", "today")), ns(per("update one field", "objects")), f'as a literal; {ns(per("update one field", "as objects, by spread"))} by spread, <code>{{...r, x}}</code>'),
        ("read a field by its label", ns(per("read a field by label, 1,000 records", "today", 1000)), ns(per("read a field by label, 1,000 records", "objects", 1000)), "the same"),
        ("read a field by its position", ns(per("read a field by position, 1,000 records", "today", 1000)), ns(per("read a field by position, 1,000 records", "objects", 1000)), f'through <code>Object.values</code>; {ns(per("read a field by position, 1,000 records", "as objects, the label from the type", 1000))} with the label at that position from the type'),
        ("compare two equal records", ns(per("compare two equal records", "today")), ns(per("compare two equal records", "objects")), f'by their own keys; {ns(per("compare two equal records", K_EQ))} by the type’s fields, a comparison made from the type'),
        ("a million records into compiled code and back", f'{X["today: each record converted both ways"]:.0f} ms', "nothing", f'{X[K_CHECK]:.1f} ms with each field’s type checked, no copy'),
        ("a list of 1,000 cells built", f'{C["build, literals {h, t}"] / 1000:.1f} µs', f'{C["build, class instances"] / 1000:.1f} µs', f'cells made by a class, so a plain object is a record; {C["build, literals {$h, $t}"] / 1000:.1f} µs as literals <code>{{$h, $t}}</code>, {C["build, literals with a prototype {__proto__, h, t}"] / 1000:.0f} µs as literals with a prototype'),
        ("the same list walked", f'{C["walk, literals, p !== null"] / 1000:.1f} µs', f'{C["walk, class instances, p !== null"] / 1000:.1f} µs', f'{C["walk, class instances, p instanceof Cell"] / 1000:.1f} µs testing <code>instanceof</code> at each cell; {C["walk, literals {$h, $t}, p !== null"] / 1000:.1f} µs as <code>{{$h, $t}}</code>'),
    ]
    body = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td class=\"l\">{d}</td></tr>" for a, b, c, d in rows)
    return ('<div style="overflow-x:auto"><table class="nums"><thead><tr><th>in compiled code</th><th>today: an array carrying its labels</th><th>the page’s object</th><th class="l">how</th></tr></thead>'
            f"<tbody>{body}</tbody></table></div>")
def shapes_table():
    body = "".join(f'<tr><td>{GNAME[g["game"]]}</td><td>{g["rec"]:,}</td><td>{g["ctor"]:,}</td><td>{g["arr"]:,}</td><td>{g["recShare"] * 100:.0f}%</td></tr>'
                   for g in sorted(GS, key=lambda g: -g["recShare"]))
    return ('<div style="overflow-x:auto"><table class="nums"><thead><tr><th>a state of</th><th>records</th><th>constructors</th><th>arrays (lists, or tuples without labels)</th><th>records, of these nodes</th></tr></thead>'
            f"<tbody>{body}</tbody></table></div>")

# ---- (^ticket(846), 2026-11-24) a sequence beside List: a treap over array views against arrays, cells and the hybrid, all
# persistent, timed in JavaScript alone (054/drivers/seq-bench.mjs)
SQ = json.load(open(os.path.join(HERE, "data", "seq.json")))
SQW = [("seq: a treap over array views", "a treap over array views"), ("array, copied", "an array, copied"), ("cells", "cells, today"), ("hybrid", "the hybrid"), ("Immutable.js List", "Immutable.js’s List")]
def sqt(ns): return f"{ns:.0f} ns" if ns < 1000 else (f"{ns / 1000:.1f} µs" if ns < 1e6 else f"{ns / 1e6:.1f} ms")
def sq(n, way, k): return next(r[k] for r in SQ["rows"] if r["n"] == n and r["way"] == way)
def seq_table():
    ops = [("insert", "insert one, anywhere"), ("append", "append one"), ("get", "read one, anywhere"), ("sum", "walk them all"), ("inOut", "a page’s array in and out")]
    head = "".join(f"<th>{lab}</th>" for _, lab in ops)
    body = ""
    for n in sorted({r["n"] for r in SQ["rows"]}):
        body += f'<tr class="grp"><td colspan="{len(ops) + 1}">{n:,} elements</td></tr>'
        for way, lab in SQW:
            r = next((r for r in SQ["rows"] if r["n"] == n and r["way"] == way), None)
            if r is None: continue
            note = f' ({r["leaves"]:,} leaves, depth {r["depth"]})' if "leaves" in r else (" (one segment)" if way == "hybrid" and not r.get("editedFirst", True) else "")
            body += f"<tr><td>{lab}{note}</td>" + "".join(f"<td>{sqt(r[k])}</td>" for k, _ in ops) + "</tr>"
    return f'<div style="overflow-x:auto"><table class="nums"><thead><tr><th>held as</th>{head}</tr></thead><tbody>{body}</tbody></table></div>'

NUMS = {"updated": updated, "jit_pr": "2859", "checks": str(SWEEP["checks"]), "compiled": str(SWEEP["compiled"]), "agreed": str(SWEEP["agreed"]),
        "not_a_value": str(SWEEP["not_a_value"]), "by_rule": str(BY_RULE), "by_limit": str(BY_LIMIT), "cyrus": esc(CYRUS)}
FIGS = {"fig_mixed": fig_mixed(), "fig_board": fig_board(), "fig_sweep": fig_sweep(), "fig_witch": fig_witch(), "tab_plan": plan_table(), "tab_sweep": sweep_table(),
        "tab_sint": sint_table(), "tab_slides": slides_table(), "tab_builds": builds_table(), "summary": summary_block(),
        "mixed_status": mixed_status(), "tab_mixed": mixed_table(), "fig_timing": fig_timing(), "tab_timing": timing_table(),
        "timing_summary": timing_summary(), "tab_calib": calib_table(), "tab_slide_timing": slide_table(),
        "slide_summary": slide_summary(), "fig_lists": fig_lists(), "tab_lists": lists_table(), "fig_lists_games": fig_lists_games(), "tab_lists_games": lists_games_table(),
        "lg_aot": f"{(LG_GM('cells_aot', 'hybrid_aot') - 1) * 100:.0f}%", "lg_jit": f"{(LG_GM('cells_jit', 'hybrid_jit') - 1) * 100:.0f}%", "lg_n": str(len(LG)),
        "fig_cross_ints_log": fig_crossing("ints", True), "fig_cross_ints_lin": fig_crossing("ints", False), "fig_cross_rec_log": fig_crossing("records", True),
        "fig_cross_rec_lin": fig_crossing("records", False), "tab_crossing": crossing_table(), "cr_cpu": esc(CR["cpu"]), "cr_node": CR["node"],
        "tab_records": records_table(), "tab_shapes": shapes_table(), "rb_node": RB["machine"]["node"], "rb_cpu": esc(RB["machine"]["model"]),
        "rb_make_x": f'{RBR["make a record of four fields"]["today"] / RBR["make a record of four fields"]["objects"]:.0f} times',
        "rb_eq_x": f'{RBR["compare two equal records"]["today"] / RBR["compare two equal records"][K_EQ]:.1f} times',
        "rb_cross": f'{RB["crossMs"]["today: each record converted both ways"]:.0f} ms', "rb_check": f'{RB["crossMs"][K_CHECK]:.1f} ms',
        "rb_pos": ns(RBR["read a field by position, 1,000 records"]["objects"] / 1000), "rb_pos_today": ns(RBR["read a field by position, 1,000 records"]["today"] / 1000),
        "rb_eq_type": ns(RBR["compare two equal records"][K_EQ]), "rb_eq_today": ns(RBR["compare two equal records"]["today"]),
        "rb_cell": f'{(RB["cellsNs"]["build, class instances"] - RB["cellsNs"]["build, literals {h, t}"]) / 1000:.1f} ns',
        "gs_ms": f'{next(g["recShare"] for g in GS if g["game"] == "minesweeper") * 100:.0f}%', "gs_bugs": f'{next(g["recShare"] for g in GS if g["game"] == "bugs") * 100:.0f}%',
        "tab_seq": seq_table(), "sq_b": str(SQ["B"]), "sq_node": SQ["machine"]["node"],
        "sq_ins_lo": sqt(min(sq(n, SQW[0][0], "insert") for n in (1000, 1000000))), "sq_ins_hi": sqt(sq(1000000, SQW[0][0], "insert")),
        "sq_app": sqt(max(r["append"] for r in SQ["rows"] if r["way"] == SQW[0][0])), "sq_get_hi": sqt(sq(1000000, SQW[0][0], "get")),
        "sq_arr_ins": sqt(sq(1000000, "array, copied", "insert")), "sq_cell_ins": sqt(sq(1000000, "cells", "insert")),
        "sq_walk": sqt(sq(1000000, SQW[0][0], "sum")), "sq_walk_arr": sqt(sq(1000000, "array, copied", "sum")), "sq_walk_cells": sqt(sq(1000000, "cells", "sum")),
        "sq_im_ins": sqt(sq(1000000, "Immutable.js List", "insert")), "sq_im_ins_lo": sqt(sq(1000, "Immutable.js List", "insert")), "sq_im_get": sqt(sq(1000000, "Immutable.js List", "get")),
        "sq_im_walk": sqt(sq(1000000, "Immutable.js List", "sum")), "sq_im_inout": sqt(sq(1000000, "Immutable.js List", "inOut")), "sq_im_app": sqt(sq(1000000, "Immutable.js List", "append")),
        "sq_im_v": next(l["version"] for l in SQ["libs"] if l["name"] == "Immutable.js List"), "sq_fl_v": next(l["version"] for l in SQ["libs"] if l["name"] == "@funkia/list"),
        "sq_fl_fail": esc(next(l["failed"] for l in SQ["libs"] if l["name"] == "@funkia/list") or "no failure"),
        "sq_leaves": f'{sq(1000000, SQW[0][0], "leaves"):,}', "sq_depth": str(sq(1000000, SQW[0][0], "depth")),
        "gs_mjs": f'{next(g["recShare"] for g in GS if g["game"] == "mahjong-solitaire") * 100:.0f}%'}
body = open(os.path.join(HERE, "body.html")).read()
for k, v in {**NUMS, **FIGS}.items():
    body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{(\w+)\}\}", body)
assert not left, left
TITLE = "Same Answers as the Interpreter"
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n"
        "<meta name=\"description\" content=\"Work in progress on hazel-jit after Matthew and Cyrus's meeting of 2026-11-13: the changes planned, and where each stands.\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
json.dump({"meeting": {"date": "2026-11-13", "who": "Matthew Hammer and Cyrus Omar", "summary_by_matthew_2026_11_15": SUMMARY, "cyrus_step_limit": CYRUS},
           "plan": [{**p, "stages_reached": STAGES[:p["stage"]]} for p in PLAN],
           "sweep": {**SWEEP, "build_47": SWEEP_47, "not_compiled": [{"reason": r, "programs": n, "kind": k} for r, n, k in NOT_COMPILED], "by_rule": BY_RULE, "by_limit": BY_LIMIT,
                     "first_sweep": FIRST_SWEEP},
           "witch_builds": {"what": "jit.yml (scripts/jit_slides.py), Firefox on GitHub's machines, the Witch slide; one run each. view and jit: ms a frame over a 3 s drag of the neck slider, compiled views on; step: hazel-jit's run before the first redraw at each of four slider steps (two calls each), ms; draws: livelits drawn from the compiled run since load.",
                            "builds": BUILDS},
           "slides_drawn_from_compiled_run": [{"slide": s, "build_45": a, "build_45_plus_760": b, "build_47": c, "build_48": e} for s, a, b, c, e in SLIDES_760],
           "sint_today": [{"program": p, "browser_interpreter": a, "native_build": b, "hazel_jit": c} for p, a, b, c in SINT]},
          open(os.path.join(HERE, "data", "numbers.json"), "w"), indent=1)
print("wrote 054/index.html;", updated, NUMS["checks"], BY_RULE, BY_LIMIT)
