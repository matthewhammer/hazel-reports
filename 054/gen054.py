#!/usr/bin/env python3
"""^report(54): Same Answers as the Interpreter. Matthew Hammer, 2026-11-16: "please draft a WIP report for me, and
publish it, with the changes we've planned for hazel-jit, and our status on those changes thus far."

The plan is Matthew and Cyrus's meeting of 2026-11-13 (Matthew's summary in chat, 2026-11-15), as dashboard tickets
756 to 763, and two found along the way (762, 764). Writes 054/index.html from body.html and the numbers below, each
from a CI log or a jit.yml run named beside it, and 054/data/numbers.json."""
import html, json, os, re, subprocess

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
         status="On the branch: every evaluator test program also runs compiled, and any difference fails CI. Left: the slides' own programs."),
    dict(t=757, short="Int and Nat exact", name="Int and Nat exact, as the interpreter's", sec="numbers", stage=4, st="done",
         status="On the branch: a JS number while it is a safe integer, a BigInt past that. Measured on the Witch."),
    dict(t=758, short="overflow: a stuck term", name="Overflow stops at a stuck term", sec="overflow", stage=1, st="wait",
         status="Waits on a decision: SInt has three widths today. Recommended: 32 bits everywhere, each operation checked."),
    dict(t=759, short="divide by zero: a stuck term", name="Divide by zero stops at a stuck term", sec="errors", stage=4, st="done",
         status="On the branch: the compiled run stops, and the interpreter makes the stuck term."),
    dict(t=760, short="holes, the stepper: the interpreter's", name="Holes and the stepper stay with the interpreter", sec="rules", stage=4, st="done",
         status="On the branch, with two rules the sweep found: no program with type errors, and no type hole. Left: a check in the browser."),
    dict(t=761, short="the other limits, one at a time", name="The other limits, one at a time", sec="limits", stage=3, st="part",
         status="Three of the list on the branch (17 builtins, partial application, mutual recursion); undefined in CI; probes not begun."),
    dict(t=763, short="a step budget", name="A step budget for compiled code", sec="budget", stage=4, st="done",
         status="On the branch: 50 ms or 50M calls a run, then the interpreter. Left: a cheaper counter."),
    dict(t=764, short="found: modulo by zero crashed", name="Found: modulo by zero crashed the interpreter", sec="found", stage=4, st="pr",
         status="Fixed on a PR to dev, hazelgrove/hazel#2825, waiting for review."),
    dict(t=762, short="found: undeclared result types", name="Found: an undeclared result type costs a step 5 to 7 times", sec="found", stage=1, st="wait",
         status="Measured in Hazel's interpreter; the cause is where the ascriptions go. The fix is not begun."),
]
STAGES = ["designed", "written", "CI green", "on the branch"]

# ---------------------------------------------------------------- the sweep: the fast checks' report on f4f969588b (job 133371195383)
SWEEP = dict(commit="f4f969588b", job=133371195383, run=43887985051, checks=313, compiled=243, agreed=216, differ=0, threw=0, not_a_value=27)
NOT_COMPILED = [  # reason, count, rule or limit
    ("a hole", 14, "rule"), ("a type hole", 10, "rule"),
    ("a free variable (the tests' own unbound names: y 13, s2 6, x 2, b2 2, a 1)", 24, "rule"),
    ("undefined", 7, "limit"), ("'this kind of term' (forms with no case of their own)", 6, "limit"),
    ("a fixpoint over a pattern that is not a name or a tuple of names (fix _, fix (), fix 0)", 3, "limit"),
    ("a tuple label that is not a name", 2, "limit"), ("the builtin string_sub", 1, "limit"),
    ("an expression as a module member", 1, "limit"), ("a reverse application (|>)", 1, "limit"),
    ("a recursive definition of more than one name, not a tuple of functions", 1, "limit"),
]
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
    dict(b="47", name="a type hole is a hole", commit="f4f969588b", run=43898636577, when="11-16", adds="Build 46 and the type-hole rule (ticket 760); trial/694-view-jit since 11-16 07:4x MST.",
         step=None, view=None, jit=None, fps=None, draws=None),
]
SLIDES_760 = [("Full Body", 30, 30), ("Hands", 30, 30), ("Scenes", 36, 36), ("Witch", 30, 28)]

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
    sx = lambda i: L + 30 + i * 110
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">The plan, ticket by ticket, on 2026-11-16</text>',
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
    cap = ("Tickets 756 to 763 are the meeting's items; 762 and 764 were found on the way. Green: done on "
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
    out = [f'<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">Build 47: the {tot} evaluator test programs, run both ways</text>',
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
    cap = (f"Build 47 (<code>{SWEEP['commit']}</code>), the fast checks' sweep (CI run {SWEEP['run']}). Each of the evaluator's "
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
    cap = ("Builds 45 to 46, the Witch slide in Firefox on GitHub's machines (jit.yml), dragging the neck slider for 3 s with "
           "compiled views on: the page's view per frame, and hazel-jit's compiled run per frame within it. One run each: "
           "the spread between them (5.4 to 7.3 ms) is as large as any difference, so these say no build is measurably slower "
           "than build 45, not which is fastest. Build 47 is being measured.")
    return (f'<figure class="f"><svg viewBox="0 0 {W} {H}" role="img" aria-label="Bars of the Witch view time per frame for builds 45 to 46, all under 8 ms, '
            f'against a 16.7 ms line" style="width:100%;height:auto;display:block">' + "".join(out) + f"</svg><figcaption>{cap}</figcaption></figure>")


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
    rows = ["<tr><th>Slide</th><th>Livelits drawn from the compiled run, build 45</th><th>With the type-error rule (45 + 760)</th></tr>"]
    for s, a, b in SLIDES_760:
        rows.append(f"<tr><td>{s}</td><td class=\"n\">{a}</td><td class=\"n\">{b}</td></tr>")
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


def summary_block():
    li = "".join(f"<li>{esc(s)}</li>" for s in SUMMARY)
    return f'<blockquote class="msg"><ul>{li}</ul></blockquote>'


NUMS = {"updated": updated, "checks": str(SWEEP["checks"]), "compiled": str(SWEEP["compiled"]), "agreed": str(SWEEP["agreed"]),
        "not_a_value": str(SWEEP["not_a_value"]), "by_rule": str(BY_RULE), "by_limit": str(BY_LIMIT), "cyrus": esc(CYRUS)}
FIGS = {"fig_board": fig_board(), "fig_sweep": fig_sweep(), "fig_witch": fig_witch(), "tab_plan": plan_table(), "tab_sweep": sweep_table(),
        "tab_sint": sint_table(), "tab_slides": slides_table(), "tab_builds": builds_table(), "summary": summary_block()}
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
           "sweep": {**SWEEP, "not_compiled": [{"reason": r, "programs": n, "kind": k} for r, n, k in NOT_COMPILED], "by_rule": BY_RULE, "by_limit": BY_LIMIT,
                     "first_sweep": FIRST_SWEEP},
           "witch_builds": {"what": "jit.yml (scripts/jit_slides.py), Firefox on GitHub's machines, the Witch slide; one run each. view and jit: ms a frame over a 3 s drag of the neck slider, compiled views on; step: hazel-jit's run before the first redraw at each of four slider steps (two calls each), ms; draws: livelits drawn from the compiled run since load.",
                            "builds": BUILDS},
           "slides_with_type_error_rule": [{"slide": s, "build_45": a, "build_45_plus_760": b} for s, a, b in SLIDES_760],
           "sint_today": [{"program": p, "browser_interpreter": a, "native_build": b, "hazel_jit": c} for p, a, b, c in SINT]},
          open(os.path.join(HERE, "data", "numbers.json"), "w"), indent=1)
print("wrote 054/index.html;", updated, NUMS["checks"], BY_RULE, BY_LIMIT)
