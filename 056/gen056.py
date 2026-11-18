#!/usr/bin/env python3
"""^report(56): What Still Falls Back. Matthew Hammer, 2026-11-18: "I'd like to create report 56 as focused on this status:
https://matthewhammer.org/hazel/reports/054/#consistency", with sections on the limitations to lift, the open decisions
(carried over from reports 054 and 055), compiled code with open holes (John's project, kept apart), and compiled code
with stuck terms (later, Matthew's); "please repeat the log scatter plot at the start"; "in the section of limitations to
lift, please summarize the test cases for evaluation that we currently cannot handle in compiled code, a re list from
report 54"; and a section on the two uses, views and mixed mode, and how step counts and their limits answer Cyrus's
concern about programs that diverge.

Writes 056/index.html from body.html and the numbers below, each from a CI log named beside it, and 056/data/numbers.json."""
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
  details.names { margin: 0.4em 0 1em; } details.names li { margin: 2px 0; } details.names code { font-size: 0.92em; }
"""
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
esc = lambda s: html.escape(s, quote=True)

# ---------------------------------------------------------------- build 50: trial/694-view-jit since 2026-11-18
BUILD = dict(b="50", commit="55e4757a4b", branch="trial/694-view-jit", pr="hazelgrove/hazel#2817",
             run=44319161267, fast_job=134853196883, branch_run=44211080673, branch_full_job=134489286397,
             note="build 49 and the slides' builtins; CI passed on trial/761-slide-builtins at this commit (run 44211080673), then the prototype "
                  "branch was fast-forwarded to it, and its own CI (run 44319161267) is the one quoted, apart from the slides")

# the sweep, the fast checks of CI run 44319161267 (data/sweep-build-50.txt); the same counts in run 44211080673
SWEEP = dict(checks=313, compiled=260, agreed=235, values=233, both_stuck=2, differ=0, threw=0, not_a_value=25)
NOT_COMPILED = [  # (reason as the sweep prints it, programs, kind)
    ("a hole", 15, "hole"), ("a type hole", 10, "hole"),
    ("the free variable y", 13, "free"), ("the free variable s2", 6, "free"), ("the free variable x", 2, "free"),
    ("the free variable b2", 2, "free"), ("the free variable a", 1, "free"),
    ("a recursive definition by a pattern that is not a name or a tuple of names", 3, "fix"),
    ("a recursive definition of more than one name whose part that is not a function names one of them", 1, "fix"),  # fix () -> [], a tuple of no names
]
NC = sum(n for _, n, _ in NOT_COMPILED)
assert SWEEP["checks"] == SWEEP["compiled"] + NC
assert SWEEP["compiled"] == SWEEP["agreed"] + SWEEP["not_a_value"]
assert SWEEP["agreed"] == SWEEP["values"] + SWEEP["both_stuck"]
BOTH_STUCK = ["(true) . a == (true) . a", "((true) . a): Int == ((true) . a): Int"]
NOT_A_VALUE = [l.strip() for l in open(os.path.join(HERE, "data", "not-a-value.txt")) if l.strip()]
assert len(NOT_A_VALUE) == SWEEP["not_a_value"], len(NOT_A_VALUE)

# each program not compiled, by name: the sweep prints them since 8d7694d9ff (trial/756-sweep-names), "  NOT COMPILED  test: reason"
NAMES = dict(commit="8d7694d9ff", branch="trial/756-sweep-names", run=None, job=134862413770, file=os.path.join(HERE, "data", "not-compiled.tsv"))
NC_NAMES = []
if os.path.exists(NAMES["file"]):
    for l in open(NAMES["file"]):
        if "\t" in l:
            t, r = l.rstrip("\n").split("\t", 1)
            NC_NAMES.append((t, r))
    m = re.search(r"run (\d+)", open(os.path.join(HERE, "data", "not-compiled.run")).read()) if os.path.exists(os.path.join(HERE, "data", "not-compiled.run")) else None
    NAMES["run"] = int(m.group(1)) if m else None

# the slides, the full tests of CI run 44211080673 (the slides' branch at build 50's commit): one reason a slide, the first met
SLIDES = dict(programs=129, compiled=20, agreed=20)
SLIDES_NOT = [("a static error (the page compiles no program with one)", 21, "decision 8"), ("a type hole", 29, "holes"), ("a hole", 28, "holes"),
              ("a test, <code>test ... end</code>", 28, "limit"), ("this kind of pattern (a splice)", 1, "limit"),
              ("the builtin <code>group_by_label</code>", 1, "limit"), ("a closure with its own environment", 1, "limit")]
assert SLIDES["programs"] == SLIDES["compiled"] + sum(n for _, n, _ in SLIDES_NOT)

# mixed mode on build 50 (the fast checks of CI run 44319161267): (program, the interpreter alone ms, mixed ms)
MIXED = [("fib(16), all compiled", 66.5, 0.1), ("the Petri net rule, whole types declared, 100 events", 170.1, 19.0),
         ("the I Ching's rules, 200 readings", 1028.0, 197.1), ("500 calls of a one-line function (sq) from an interpreted loop", 20.6, 21.8)]
MIXED_SWEEP = dict(programs=6, functions=7, agreed=6, calls=16843, fell=2, undeclared=29)


# ---------------------------------------------------------------- the timings: "hazel-jit time" lines of the same fast checks
def timing_rows():
    rows = []
    for line in open(os.path.join(HERE, "data", "timing.tsv")):
        p = line.rstrip("\n").split("\t")
        if len(p) < 10 or p[0] != "hazel-jit time":
            continue
        rows.append(dict(interp1=float(p[1]), interp=float(p[2]), interp_n=int(p[3]), compile=float(p[4]), parse=float(p[5]),
                         run1=float(p[6]), run=float(p[7]), run_n=int(p[8]), test=p[9]))
    return rows


TROWS = timing_rows()
assert len(TROWS) == SWEEP["values"], len(TROWS)


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


ratio = lambda r: r["interp"] / max(r["run"], 1e-6)
first = lambda r: r["parse"] + r["run1"]
TN = dict(n=len(TROWS), interp=sum(r["interp"] for r in TROWS), run=sum(r["run"] for r in TROWS),
          med=median([ratio(r) for r in TROWS]), lo=min(ratio(r) for r in TROWS), hi=max(ratio(r) for r in TROWS),
          med_interp=median([r["interp"] for r in TROWS]), med_run=median([r["run"] for r in TROWS]),
          med_c=median([r["interp1"] / max(r["compile"] + first(r), 1e-3) for r in TROWS]),
          slower1=sum(1 for r in TROWS if r["compile"] + first(r) > r["interp1"]),
          min_n=min(r["interp_n"] for r in TROWS), max_n=max(r["interp_n"] for r in TROWS))


def slow_note():
    slow = [r for r in TROWS if ratio(r) < 1]
    fast = sorted(ratio(r) for r in TROWS if ratio(r) >= 1)
    if not slow:
        return f"every one is faster, from {fast[0]:.1f} to {fast[-1]:,.0f} times."
    notes = []
    for r in slow:
        o = OTHER_RUN.get(r["test"])
        notes.append(f"<code>{esc(r['test'])}</code> at {ratio(r):.2f} times" + (f", {o[0]} times as fast in build 50's other CI run ({o[1]})" if o else ""))
    return (f"all but {'one' if len(slow) == 1 else len(slow)} are faster, from {fast[0]:.1f} to {fast[-1]:,.0f} times. The exception, " + "; ".join(notes) +
            ", is most likely a pause during its repeats: each of the two runs has one such program, a different one, and each is fast in the other.")


def fig_timing():
    W, L, R, T, B, H = 700, 70, 20, 44, 52, 430
    xs = [max(r["interp"], 1e-5) for r in TROWS]
    ys = [max(r["run"], 1e-5) for r in TROWS]
    lo = math.floor(math.log10(min(min(xs), min(ys))))
    hi = math.ceil(math.log10(max(max(xs), max(ys))))
    sx = lambda v: L + (math.log10(v) - lo) / (hi - lo) * (W - L - R)
    sy = lambda v: H - B - (math.log10(v) - lo) / (hi - lo) * (H - T - B)
    out = [f'<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">Build {BUILD["b"]}: the evaluator\'s {len(TROWS)} compiled programs, a run\'s time each way</text>',
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
    cap = (f"Build {BUILD['b']} (<code>{BUILD['commit']}</code>, CI run {BUILD['run']}, the fast checks, Node on GitHub's machines; "
           f"report 054's <a href=\"../054/#timed\">figure</a> is the same plot for build 49). Each program's interpreter runs repeated until they "
           f"added to 20 ms ({TN['min_n']} to {TN['max_n']} times), its compiled JS's until they added to 5 ms; each dot is a run's time, "
           "the total over the repeats. Below the line marked \"as fast\", compiled code was faster. One run; the dot above the line is "
           "discussed in the text. Not a build of the app.")
    return (f'<figure class="f"><svg viewBox="0 0 {W} {H}" role="img" aria-label="A scatter of {len(TROWS)} programs on log scales, '
            f'the interpreter\'s time a run across and the compiled JS\'s up; every program below the line where both are as fast" '
            f'style="width:100%;height:auto;display:block">' + "".join(out) + f"</svg><figcaption>{cap}</figcaption></figure>")


# one program a run measured slower compiled, a different one in each of build 50's two runs, and each faster in the other run:
# (test, its ratio in the other run, that run)
OTHER_RUN = {"{} == {}": (202, 44211080673), "{ let m = { let y = 1 } } == { let m = { let y = 1 } }": (109, 44319161267)}


def timing_lead():
    return (f"Where hazel-jit compiles a program, it gives the interpreter's answer, and fast: run again and again, the median of the "
            f"evaluator's {TN['n']} such programs is {TN['med']:,.0f} times as fast compiled ({TN['med_interp'] * 1000:.0f} µs against "
            f"{TN['med_run'] * 1000:.2f} µs), and {slow_note()} Run once, compiling "
            f"included, the median is {TN['med_c']:.1f} times as fast, and {TN['slower1']} are slower: programs of a few microseconds, "
            f"where compiling is the cost.")


# ---------------------------------------------------------------- the sweep, as a bar
def fig_sweep():
    W, L, R = 700, 16, 16
    by_rule = sum(n for _, n, k in NOT_COMPILED if k in ("hole", "free"))
    by_limit = sum(n for _, n, k in NOT_COMPILED if k == "fix")
    parts = [("the same value", SWEEP["values"], "#15803d"), ("both stop, stuck", SWEEP["both_stuck"], "#0e7490"),
             ("ill-typed: nothing to compare", SWEEP["not_a_value"], "#b45309"), ("not compiled: holes, unbound names", by_rule, "#9ca3af"),
             ("not compiled: a limit", by_limit, "#7c3aed")]
    tot = SWEEP["checks"]
    x, y, h = L, 50, 30
    out = [f'<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">Build {BUILD["b"]}: the evaluator\'s {tot} test programs, run both ways</text>',
           f'<text x="16" y="34" font-size="11" fill="var(--muted)">{SWEEP["differ"]} differ: every compiled program gave the interpreter\'s answer, or is a known ill-typed test</text>']
    for name, n, c in parts:
        w = n / tot * (W - L - R)
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" fill="{c}" opacity="0.88"/>')
        if w > 34:
            out.append(f'<text x="{x + w / 2:.1f}" y="{y + 20}" font-size="12" font-weight="700" text-anchor="middle" fill="#fff">{n}</text>')
        x += w
    lx, ly = L, y + h + 14
    for name, n, c in parts:
        lab = f"{name} ({n})"
        wl = 16 + 6.0 * len(lab) + 14
        if lx + wl > W - R:
            lx, ly = L, ly + 18
        out.append(f'<rect x="{lx}" y="{ly}" width="11" height="11" fill="{c}"/>')
        out.append(f'<text x="{lx + 16}" y="{ly + 10}" font-size="10.5" fill="var(--ink)">{esc(lab)}</text>')
        lx += wl
    H = ly + 24
    cap = (f"Build {BUILD['b']} (<code>{BUILD['commit']}</code>), the sweep in the fast checks of CI run {BUILD['run']}. Each of the evaluator's "
           "test programs also goes to hazel-jit, compiled and run in JavaScript, and its answer is compared with the interpreter's. "
           "\"Both stop, stuck\": a projection the interpreter leaves stuck, where the compiled run stops and the interpreter's answer is shown. "
           "\"Ill-typed\": the interpreter stops at a failed run-time check, which compiled code, its types erased, runs past; the page compiles "
           "no program with a static error. Report 054's <a href=\"../054/#consistency\">bar</a> is build 49's.")
    return (f'<figure class="f"><svg viewBox="0 0 {W} {H}" role="img" aria-label="A bar of {tot} programs: {SWEEP["values"]} the same value, '
            f'{SWEEP["both_stuck"]} both stuck, {SWEEP["not_a_value"]} ill-typed, {by_rule} not compiled for holes or unbound names, {by_limit} for a limit" '
            f'style="width:100%;height:auto;display:block">' + "".join(out) + f"</svg><figcaption>{cap}</figcaption></figure>")


# ---------------------------------------------------------------- the re-list: every evaluator program compiled code does not handle
SEC = {"holes": '<a href="#holes">holes</a>', "stuck": '<a href="#stuck">stuck terms</a>', "limits": '<a href="#limits-eval">a limit</a>',
       "q8": '<a href="#d-8">decision 8</a>', "q12": '<a href="#d-12">decision 12</a>'}
EVAL = [  # (what the program meets, programs, what happens today, where its lifting is discussed)
    ("an expression hole, a multihole, or a tuple label that is a hole", 15, "not compiled, by rule (2026-11-13)", f"{SEC['holes']}: the rule stands"),
    ("a type hole, <code>?</code> in a type", 10, "not compiled, by rule", f"{SEC['holes']}: the rule stands"),
    ("a free variable: the test's own unbound name (<code>y</code> 13, <code>s2</code> 6, <code>x</code> 2, <code>b2</code> 2, <code>a</code> 1)", 24,
     "not compiled: a static error; the interpreter's answer holds the variable, stuck", f"{SEC['stuck']}; {SEC['q8']}"),
    ("a fixpoint over a pattern that is not a name: <code>fix _ : ()</code>, <code>fix (_ : Bool)</code>, <code>fix 0</code> and <code>fix ()</code>", 4,
     "not compiled, a limit; ill-typed tests, left so on purpose", f"{SEC['limits']}: none planned"),
    ("an ill-typed program: the interpreter stops at a failed run-time check", 25,
     "compiled by the sweep; compiled code runs past the check, so there is nothing to compare; the page compiles none of these", f"{SEC['stuck']}; {SEC['q8']}, {SEC['q12']}"),
    ("a projection the interpreter leaves stuck: <code>(true).a</code>, and the same with an ascription", 2,
     "compiled; the run stops, and the interpreter's answer is shown: agreeing, by falling back", SEC["stuck"]),
]
assert sum(n for _, n, _, _ in EVAL) == SWEEP["checks"] - SWEEP["values"]


def eval_table():
    rows = ["<tr><th>The program meets</th><th>Programs</th><th>Today</th><th>Discussed under</th></tr>"]
    for what, n, today, where in EVAL:
        rows.append(f'<tr><td>{what}</td><td class="n">{n}</td><td>{today}</td><td>{where}</td></tr>')
    rows.append(f'<tr><td><b>Not handled in compiled code</b></td><td class="n"><b>{sum(n for _, n, _, _ in EVAL)}</b></td>'
                f'<td>of {SWEEP["checks"]}; the other {SWEEP["values"]} compile and give the interpreter\'s value</td><td></td></tr>')
    return '<table class="vals">' + "".join(rows) + "</table>"


def eval_names():
    li = lambda xs: "".join(f"<li><code>{esc(x)}</code></li>" for x in xs)
    out = []
    if NC_NAMES:
        by = {}
        for t, r in NC_NAMES:
            by.setdefault(r, []).append(t)
        parts = "".join(f"<li>{esc(r)} ({len(ts)}):<ul>{li(ts)}</ul></li>" for r, ts in sorted(by.items(), key=lambda kv: -len(kv[1])))
        src = f"the sweep on <code>{NAMES['commit']}</code> (build {BUILD['b']} and one line that prints them, <code>{NAMES['branch']}</code>" + (f", CI run {NAMES['run']}" if NAMES["run"] else "") + ")"
        out.append(f'<details class="names"><summary>The {len(NC_NAMES)} programs not compiled, by the test that evaluates each, as {src}</summary><ul>{parts}</ul></details>')
    else:
        out.append('<p class="muted">The 53 programs not compiled, by name: CI prints them on <code>trial/756-sweep-names</code> (build 50 and one line '
                   'that prints each program the sweep does not compile); its run is going, and they go here.</p>')
    out.append(f'<details class="names"><summary>The {len(NOT_A_VALUE)} ill-typed programs, by test (the sweep\'s known list)</summary><ul>{li(NOT_A_VALUE)}</ul></details>')
    out.append(f'<details class="names"><summary>The {len(BOTH_STUCK)} stuck projections</summary><ul>{li(BOTH_STUCK)}</ul></details>')
    return "".join(out)


def slides_table():
    rows = ["<tr><th>The slide's program meets, first</th><th>Slides</th><th>Discussed under</th></tr>"]
    for what, n, k in SLIDES_NOT:
        where = {"holes": SEC["holes"], "limit": '<a href="#limits-forms">a limit</a>', "decision 8": SEC["q8"]}[k]
        rows.append(f'<tr><td>{what}</td><td class="n">{n}</td><td>{where}</td></tr>')
    rows.append(f'<tr><td>compiled, and agreeing</td><td class="n">{SLIDES["compiled"]}</td><td></td></tr>')
    return '<table class="vals">' + "".join(rows) + "</table>"


def mixed_table():
    rows = ["<tr><th>Program (in Node, build 50)</th><th>The interpreter alone</th><th>Mixed</th><th>As fast, times</th></tr>"]
    for p, a, m in MIXED:
        rows.append(f'<tr><td>{esc(p)}</td><td class="n">{a:,.1f} ms</td><td class="n">{m:,.1f} ms</td><td class="n">{a / m:,.1f}</td></tr>')
    return '<table class="vals">' + "".join(rows) + "</table>"


# ---------------------------------------------------------------- the open decisions, carried over
# (n, question, lean, from, status, group)
OPEN = "asked for 2026-11-17; the answer not yet written down"
DECISIONS = [
    (1, "SInt at 32 bits, and overflow an error (hazelgrove/hazel#2828): agreed?", "Yes; wrapping would be cheaper compiled, but silent.", "054 q1", "PR waiting on a review", "same"),
    (2, "Who reviews the fix for modulo by zero (hazelgrove/hazel#2825)?", "Anyone who knows the evaluator; it is small.", "054 q2", "PR waiting on a review", "same"),
    (10, "String length in graphemes: intended?", "Keep it; compiled code counts as the interpreter does.", "054 q10", OPEN, "same"),
    (11, "Labeled tuples as JavaScript arrays carrying their labels: fine?", "Fine inside compiled code; the boundary converts.", "054 q11", OPEN, "same"),
    (12, "The evaluator's ill-typed tests (25 on build 50, 27 on build 49): keep them on a known list?", "Keep them: they test the interpreter's casts, and the page compiles no program with a type error.", "054 q12", OPEN, "same"),
    (18, "The check counts a compiled run that stops where the interpreter's answer is stuck as agreeing (an invalid operation, <code>undefined</code>, a stuck projection). Keep that?", "Keep it while compiled code makes no stuck terms; compare the terms themselves once it does (<a href=\"#stuck\">stuck terms</a>).", "new", "open", "same"),
    (3, "Which functions does mixed mode compile?", "Let-bound, complete, whole type declared, no probe.", "054 q3", OPEN, "mixed"),
    (4, "What does the stepper show for a compiled call?", "Mixed mode off while the stepper is open.", "054 q4", "partly answered 2026-11-13: it counts the steps it would have taken", "mixed"),
    (5, "Probes in compiled code?", "Until step counts land, a probe takes its function out of the compiled set.", "054 q5", "answered 2026-11-13: count the interpreter's steps, and make its samples", "mixed"),
    (6, "Main thread or worker?", "Mixed mode in the worker; livelit views on the main thread, under a budget.", "054 q6", OPEN, "mixed"),
    (7, "Falling back runs a call again from the start: safe for good?", "Yes while evaluation has no effects.", "054 q7", OPEN, "mixed"),
    (8, "A program with a type error elsewhere: compile its sound functions?", "Yes, per function; a value that does not fit is caught where it crosses.", "054 q8", OPEN, "mixed"),
    (9, "One step budget or two?", "One, in the interpreter's steps.", "054 q9", "answered 2026-11-13: one, which compiled code will count exactly", "steps"),
    (19, "Count every step, or only those that interpret the program?", "Every step: probe samples' spans are in every step today.", "054 <a href=\"../054/#steps\">steps</a>", "open", "steps"),
    (20, "On the main thread, a step limit alone, or steps and a clock?", "Both: the steps make the same answer as the interpreter's, the clock keeps a frame (<a href=\"#uses-diverge\">below</a>).", "new", "open", "steps"),
    (21, "Stuck terms: should compiled code make them, instead of stopping?", "Not yet: stopping is correct, and rare in finished programs. Begin with overflow, after the limits, when the holes work needs it (<a href=\"#stuck\">below</a>).", "new", "open", "steps"),
    (22, "Does the holes work live on the prototype branch?", "Design and measure there; it lands on dev with mixed mode.", "055 q1", "open; settle before John starts", "holes"),
    (23, "Which values are opaque: empty holes only, or every indeterminate term?", "Every value <code>to_js</code> cannot represent.", "055 q2", "open", "holes"),
    (24, "Must a hole keep its identity through compiled code?", "Yes; the table gives back the very term that went in.", "055 q3", "open", "holes"),
    (25, "The checked version: compiled up front, or the first time a hole arrives?", "The first time.", "055 q4", "open", "holes"),
    (13, "How does hazel-jit reach dev?", "Small PRs (report 053): the two fixes; the compiler with the check in CI and nothing a user sees; mixed mode behind a setting; then livelit views.", "054 q13", OPEN, "landing"),
    (14, "Should hazeljs ship the compiler?", "No: a build-time tool; pages get only the runtime (about 17 kB).", "054 q14", OPEN, "landing"),
    (15, "Undeclared result types cost a step 5 to 7 times (ticket 762): fix in elaboration?", "Yes, with an owner who knows elaboration.", "054 q15", OPEN, "landing"),
    (16, "An answer that is a function grows past gigabytes (hazelgrove/hazel#2832): fix <code>Evaluator.finish</code>?", "Yes: leave a closure in the answer as a closure.", "054 q16", OPEN, "landing"),
    (17, "Float literals print with six decimals (hazelgrove/hazel#2831): print them so they read back?", "Yes, the shortest form that reads back; a warm-up PR for John (report 055).", "054 q17", OPEN, "landing"),
]
GROUPS = [("same", "What compiled code must match"), ("mixed", "Mixed mode"), ("steps", "Steps, budgets and stuck terms"),
          ("holes", "Holes (report 055)"), ("landing", "Landing, and the interpreter's side")]


def decisions_table():
    rows = ["<tr><th>#</th><th>Decision</th><th>Our lean</th><th>From</th><th>Where it stands</th></tr>"]
    for g, title in GROUPS:
        rows.append(f'<tr><td colspan="5"><b>{esc(title)}</b></td></tr>')
        for n, q, lean, src, st, gg in DECISIONS:
            if gg == g:
                rows.append(f'<tr id="d-{n}"><td class="n">{n}</td><td>{q}</td><td>{lean}</td><td>{src}</td><td>{st}</td></tr>')
    return '<table class="vals">' + "".join(rows) + "</table>"


# ---------------------------------------------------------------- where compiled code stops today for a stuck term (HazelJit.re, build 50)
STOPS = [
    ("divide or modulo by zero, a negative power", "<code>DivideByZero</code>, <code>NegativeExponent</code>", "<code>$R.invalid</code> (ticket 759)"),
    ("an SInt result past 32 bits", "<code>IntegerOverflow</code>", "<code>$R.s32</code>, <code>$R.invalid</code> (ticket 758)"),
    ("a number that does not fit its type, text that is not a number", "<code>IntegerTooBig</code>, and the others the builtins raise", "<code>$R.invalid</code> (ticket 759)"),
    ("<code>undefined</code>, where a run reaches it", "a stuck <code>undefined</code>", "<code>$R.indet</code> (ticket 761)"),
    ("a projection of something that is not a tuple or a list", "a stuck projection", "<code>$R.indet</code>, in <code>$R.dot</code> (build 50)"),
    ("a run past its budget", "none: the interpreter runs to its own limits", "<code>$R.out</code> (ticket 763)"),
]


def stops_table():
    rows = ["<tr><th>Where the compiled run meets</th><th>The interpreter's answer holds</th><th>Compiled code stops at</th></tr>"]
    for a, b, c in STOPS:
        rows.append(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>")
    return '<table class="vals">' + "".join(rows) + "</table>"


NUMS = {"updated": updated, "timing_lead": timing_lead(), "med": f"{TN['med']:,.0f}", "n_values": str(SWEEP["values"]),
        "not_handled": str(SWEEP["checks"] - SWEEP["values"]), "n_names": str(len(NC_NAMES)) if NC_NAMES else "53"}
FIGS = {"fig_timing": fig_timing(), "fig_sweep": fig_sweep(), "tab_eval": eval_table(), "eval_names": eval_names(),
        "tab_slides": slides_table(), "tab_mixed": mixed_table(), "tab_decisions": decisions_table(), "tab_stops": stops_table()}
body = open(os.path.join(HERE, "body.html")).read()
for k, v in {**NUMS, **FIGS}.items():
    body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{(\w+)\}\}", body)
assert not left, left
TITLE = "What Still Falls Back"
DESC = ("Where hazel-jit's same-answers check stands on build 50, and every case where the interpreter still does the work: "
        "the limits to lift, the open decisions, holes (John's project, kept apart) and stuck terms (later).")
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{esc(DESC)}\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
json.dump({"build": BUILD, "sweep": {**SWEEP, "not_compiled": [{"reason": r, "programs": n, "kind": k} for r, n, k in NOT_COMPILED],
                                     "not_a_value": NOT_A_VALUE, "both_stuck": BOTH_STUCK,
                                     "not_compiled_by_name": [{"test": t, "reason": r} for t, r in NC_NAMES], "names_from": NAMES},
           "slides": {**SLIDES, "not_compiled": [{"reason": re.sub("<[^>]+>", "", r), "slides": n} for r, n, _ in SLIDES_NOT]},
           "mixed": {"measured": [{"program": p, "interpreter_ms": a, "mixed_ms": m} for p, a, m in MIXED], "sweep": MIXED_SWEEP},
           "timing": {k: v for k, v in TN.items()},
           "decisions": [{"n": n, "question": re.sub("<[^>]+>", "", q), "lean": re.sub("<[^>]+>", "", l), "from": re.sub("<[^>]+>", "", s), "status": st, "group": g}
                         for n, q, l, s, st, g in DECISIONS]},
          open(os.path.join(HERE, "data", "numbers.json"), "w"), indent=1)
print("wrote 056/index.html;", updated, f"median {TN['med']:.0f}x over {TN['n']}", "names:", len(NC_NAMES))
