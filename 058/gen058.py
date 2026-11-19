#!/usr/bin/env python3
"""^report(58): What Could Merge Today. Matthew Hammer, 2026-11-19: "today is another hazel team merge-a-thon, where we are
going to try to review and merge a lot of stuff, if possible. To prep, Let's look at hazel dev, and let's look at our open PRs
that are small and self-contained (not livelits, but everything else could be a candidate today). Please create a report with
whatever PRs the team could consider."

Writes 058/index.html from body.html, data/prs.json (drivers/prep058.py: GitHub's view of each PR, and a trial merge of each
into dev) and the reading of each PR below (its description, its reviews and comments), and data/tiers.json."""
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
  table.vals td:first-child { white-space: nowrap; }
  code { overflow-wrap: anywhere; }
  .tier { font-weight: 600; white-space: nowrap; }
  .ready { color: var(--good); } .conflict { color: var(--warn); } .decide { color: var(--accent); } .later { color: var(--muted); }
  figure.chart { margin: 1em 0; } figure.chart svg { width: 100%; height: auto; max-width: 760px; display: block; }
  figure.chart figcaption { color: var(--muted); font-size: 0.88em; margin-top: 4px; }
  svg .lbl { fill: var(--ink); font: 11.5px system-ui, sans-serif; } svg .val { fill: var(--muted); font: 10.5px system-ui, sans-serif; }
  svg .grp { fill: var(--ink); font: 600 12px system-ui, sans-serif; } svg .ax { stroke: var(--line); stroke-width: 1; }
  svg .b-ready { fill: var(--good); } svg .b-conflict { fill: var(--warn); } svg .b-decide { fill: var(--accent); } svg .b-later { fill: var(--cx); }
  svg .b-out { fill: none; stroke: var(--cx); stroke-dasharray: 3 2; }
  svg .cnt { fill: var(--paper); font: 700 13px system-ui, sans-serif; } svg .cnt.dk { fill: var(--ink); }
  ol.queue > li { margin: 6px 0; }
"""
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
esc = lambda s: html.escape(s, quote=True)
D = json.load(open(os.path.join(HERE, "data", "prs.json")))
P = D["prs"]
WHO = {"cyrus-": "Cyrus", "7h3kk1d": "Alexander", "disconcision": "Andrew", "Negabinary": "Matt Keenan", "thomasporter522": "Thomas"}

# Each PR: number, a short name, its tier, what it is, and what it needs before it merges. Read 2026-11-19 from each PR's
# description, reviews and comments. Tiers: ready (merges cleanly into today's dev, CI green, nothing asked of it but a
# review), conflict (one conflict with today's dev to resolve first), decide (a question for the team first), later (not today).
PRS = [
    # ready
    (2812, "README: link the hazeljs npm package", "ready",
     "A short README section pointing to the experimental hazeljs package, saying it is a 0.0.x prototype that does not track dev yet.",
     "An approval."),
    (2825, "Modulo by zero: an error, not a crash", "ready",
     "<code>int_mod(7, 0)</code>, and the SInt, Nat and Float modulos, crashed the interpreter: they named a builtin, <code>mod</code>, that does not exist. Now each gives Divide by Zero, as <code>7 / 0</code> does.",
     "An approval."),
    (2818, "A frame-rate HUD, with ?hud", "ready",
     "Frames a second and frame times, in a corner, only when the address has <code>?hud</code>. One file, <code>index.html</code>.",
     "An approval."),
    (2816, "Ids minted and compared as strings", "ready",
     "An id is built by joining one-byte strings and compared as a string, not through Uuidm's buffer: evaluation about 13% faster on the heaviest programs (the PR's own measurement). On the livelits branch since 2026-10-10.",
     "An approval."),
    (2652, "The eval worker in Firefox, started at load", "ready",
     "Firefox showed Evaluation timed out for answers the worker could give at once, when the page's thread was busy: the worker now starts at load, and a reply waiting in the queue is not timed out. Finding 8 on #2609.",
     "An approval."),
    (2671, "MapPiece keeps unchanged pieces", "ready",
     "A projector update away from the caret copied the whole program; now every piece with nothing changed under it stays the same object. 3.12 to 1.92 ms an update on a 2,000-let program (its benchmark).",
     "An approval."),
    (2675, "Incremental evaluation around a recursive let", "ready",
     "Fixes the free variables statics reports for a recursive let, so an expression with one inside (a module with a recursive member, a function with a recursive helper) is reused, not run again.",
     "An approval. Alexander noted on 10-29 that #2431 (Matt Keenan's property tests, open) changes this code too: review them side by side."),
    (2651, "A module binding analyzes its definition once", "ready",
     "Statics analyzed a module's definition twice, once as a let and once directly; now it reads back the elaboration the let recorded. Finding 7 on #2609.",
     "An approval. Alexander's review of 10-21 is answered, in three commits that day. #2717, below, is an optional follow-up."),
    (2815, "Goto first use, Goto next use", "ready",
     "Two moves in the context menu, the reverse of Goto definition: to a definition's first use, and from each use to the next. With tests.",
     "An approval."),
    (2603, "Statics: a let analyzed once unless it refers to itself", "ready",
     "Four statics and completion speedups, found by profiling the livelits branch, each its own commit with tests. The big one: a let-bound function no longer takes the recursive path's four passes, which multiplied with nesting. Byte-identical <code>hazel analyze -W</code> output on dev's 72 programs when it was made.",
     "An approval. Its CI ran on 09-26, 462 commits of dev ago; the merge queue runs it again on today's dev."),
    (2697, "Test: the nodes an evaluation builds, held to budgets", "ready",
     "Counts the terms an evaluation builds, beside its steps, so copies like those #2679 removed cannot come back unseen. A draft only because it waited on #2678 and #2679, both merged (10-29, 10-19); its own commit is 118 lines added and 29 removed, in 2 files.",
     "Merge dev in, so its diff is its own commit, and mark it ready."),
    # one conflict first
    (2613, "Colors: every var() is one the theme defines", "conflict",
     "Eleven <code>var()</code> names that nothing defined, so those colors ignored the Colors slide, dark mode and high contrast; each now reads a theme role, and a lint keeps it so. <b>Approved by Alexander on 11-07.</b>",
     "dev deleted <code>assistant.css</code> (#2438, dead stylesheets) after this PR edited it: drop that edit, and the file's entry in the lint's list. Alexander left one visible change, the probe stack's focus pill, as Andrew's call."),
    (2606, "Keep the incremental cache in the eval worker", "conflict",
     "The worker's answer carried its whole incremental cache to the page, and the next request carried it back, on every run; now the worker keeps it.",
     "<code>test/Test_WorkerServer.re</code>: #2660 (Matt Keenan's, keep incremental evaluation for expensive small programs, merged 11-05) added tests beside these; keep both. Both change the worker's incremental path, so Matt Keenan is the natural reviewer."),
    (2661, "Types get a Merkle hash", "conflict",
     "The evaluator asks <code>is_consistent</code> once per pair of types, not once per copy of them, keyed by a hash kept for each type object.",
     "<code>Ascriptions.re</code>, against #2734 (Typ.unroll, Alexander's, merged 11-03). #2681 builds on this PR."),
    # a decision first
    (2828, "SInt at 32 bits everywhere; overflow an error", "decide",
     "<code>use SInt in 2147483647 + 1</code> was -2147483648 in the browser and 2147483648 natively; now it is an error, everywhere. Small, clean and green, but it changes what programs mean.",
     "Cyrus: is SInt overflow an error, or a wrap at 32 bits everywhere?"),
    (2793, "Fewer trampoline bounces", "decide",
     "Two small changes to the evaluator's trampoline: half the steps on the PerfBudgets program (206,834 to 96,438), and its budgets lowered to match.",
     "Matt Keenan, 11-03: 15% faster and 4% less memory, a little less readable, and “ambivalent”. Take it, or close it."),
    (2592, "Report each error once, not once per wrapper", "decide",
     "An error inside parentheses was listed once for each layer: <code>(((y)))</code> made four rows in the problems sidebar. A draft.",
     "How it goes with issue #2561 (a type mismatch reported on every enclosing form): first, after, or folded in."),
    (2614, "Load text about 2.5× faster", "decide",
     "The recovering parser (<code>MarkerParse.of_text</code>, for a text FastParse rejects) inserted the text a character at a time, re-grouting each time: now whole tokens, and one re-grout.",
     "It and #2610 both rewrite that parser's path and conflict with each other in <code>MarkerParse.re</code>; each merges into dev alone. Which first, or one only?"),
    (2610, "The load fallback through the segmented parser", "decide",
     "The same fallback through <code>Parser.to_segment</code>, which splits the text at safe points to avoid the quadratic cost, keeping projectors.",
     "See #2614."),
    (2717, "A module binding is a non-recursive let", "decide",
     "A draft follow-up to #2651: it tells the let up front that a module is not recursive, instead of #2651's check afterwards.",
     "Take it after #2651, or close it. It conflicts with #2603 in <code>Statics.re</code>."),
    (2608, "Elaborations without the source's whitespace and comments", "decide",
     "Elaborations, sent to the worker with every request, carried each node's whitespace and comments.",
     "Alexander requested changes on 10-21, not yet answered: 13.5% of it is left (types through <code>Typ.normalize</code>, labels, builtins), and he offered two fixes: cover those paths, with a test over the docs corpus, or strip once at the worker's boundary (17.7 ms over the whole corpus). Pick one."),
    (2729, "A module's sum types usable after it", "decide",
     "A sum type declared in a module can be built and matched outside it, not only inside. It came up in Messed Up Dress Up's scripts. #2749 adds tests at its edges, into this branch.",
     "Alexander said on 10-30 he would review it once his #2493 (Modules II, part 1) merges. Wait for #2493, or review it now."),
    (2749, "Tests: a module's sum types at the edges", "decide",
     "Tests only, for #2729: a signature that leaves the sum out, shadowing, nesting. Into #2729's branch.",
     "With #2729."),
    # later
    (2673, "Incremental evaluation: an unchanged expression by its hash", "later", "The largest of the evaluator changes (832 lines).", "Conflicts with #2660 in <code>IncrEval.re</code>."),
    (2681, "A value known to have a type is not walked again", "later", "Builds on #2661.", "Alexander, 10-19: still thinking about it."),
    (2676, "The cursor inspector shows a long type whole", "later", "A panel over the inspector's bar (issue #2674). #2698 is stacked on it.", "Conflicts with four of Alexander's commits in <code>Statics.re</code> and <code>CursorInspector.re</code>; a change to try in the app."),
    (2698, "Gamma's long types", "later", "Stacked on #2676.", "With #2676."),
    (2689, "Test: statics within a budget", "later", "Counts statics' passes, held to budgets.", "After #2603 and #2651."),
    (2690, "Test: a re-run beside a recursive library", "later", "A step budget for an edit beside a library with recursive members.", "After #2675."),
    (2691, "Test: the worker's bytes within a budget", "later", "Byte budgets for what the page sends the worker and gets back.", "After #2606 and #2608."),
    (2583, "Deep links", "later", "The address says which slide, panel and caret.", "Cyrus deferred it on 10-29, until modular editors and the “world tree” change."),
    (2577, "Serve the web build from an Internet Computer canister", "later", "A second deploy target. A draft.", "A decision for the team, not a merge."),
    (2711, "Hazel as a JS library", "later", "hazeljs's source; stacked on it, #2719, #2807, #2808, #2809 and #2814.", "A new public surface, drafts, with its own review."),
    (2719, "Hazel in another page's frame", "later", "Stacked on #2711.", "With #2711."),
    (2807, "Library calls bind their argument", "later", "Stacked on #2719.", "With #2711."),
    (2808, "A function the library hands back keeps its closure", "later", "Stacked on #2807.", "With #2711."),
    (2809, "Hazel.value: a JS value converted once", "later", "Stacked on #2808.", "With #2711."),
    (2814, "Embed mode: editable cells", "later", "Stacked on #2719.", "With #2711."),
    (2490, "Spike: the evaluator through wasm_of_ocaml", "later", "A benchmark.", "Not for merging."),
]
LIVELITS = [2536, 2597, 2616, 2635, 2650, 2806, 2810, 2817, 2819]
QUEUE = [
    ([2812, 2825, 2818, 2816, 2652], "The five smallest, 9 to 108 lines, in files no other candidate touches."),
    ([2671, 2675, 2651, 2815, 2603], "The rest of the ready ones. #2651 and #2675 both touch <code>Statics.re</code>, as #2603 does, without conflicting."),
    ([2697, 2613, 2606, 2661], "#2697 once ready, and the three with a conflict once resolved. #2661 and #2671 both add to the tests' list, <code>test/haz3ltest.re</code>: merge dev into #2661 after the second group."),
]
TIERS = [("ready", "Ready for a review now"), ("conflict", "One conflict to resolve first"), ("decide", "A decision first"), ("later", "Not today")]
by = {t: [p for p in PRS if p[2] == t] for t, _ in TIERS}
assert len(PRS) + len(LIVELITS) == 48, len(PRS) + len(LIVELITS)
size = lambda n: P[str(n)]["add"] + P[str(n)]["del"] if str(n) in P else None


def authors(n):
    a = P.get(str(n), {}).get("recent_authors") or []
    return ", ".join(f"{WHO.get(k, k)} {c}" for k, c in a[:2]) or "—"


def review_state(n):
    p = P[str(n)]
    last = {}
    for r in p["reviews"]:
        last[r["by"]] = (r["state"], r["on"])
    s = [f"{WHO.get(b, b)}: {st.replace('_', ' ').lower()} {on[5:]}" for b, (st, on) in last.items() if st != "COMMENTED"]
    c = [WHO.get(b, b) for b, (st, on) in last.items() if st == "COMMENTED"]
    out = "; ".join(s + ([f"comments by {', '.join(c)}"] if c else []))
    return out or "none yet"


def table(tier):
    rows = ["<tr><th>PR</th><th>What it is</th><th>Size</th><th>Into today's dev</th><th>Reviews</th><th>Before it merges</th><th>Its files, lately</th></tr>"]
    for n, name, t, what, need in by[tier]:
        p = P[str(n)]
        into = p.get("into_dev")
        intocell = ("merges cleanly" if into == "clean" else "conflicts: " + ", ".join(f"<code>{esc(os.path.basename(f))}</code>" for f in p["conflicts"])) if into else f"into <code>{esc(p['base'])}</code>"
        ci = "CI green" if p["checks_green"] else "CI: " + ", ".join(k for k, v in p["checks"].items() if v not in ("SUCCESS", "SKIPPED", "NEUTRAL")) + " failed"
        draft = " <span class=\"muted\">(draft)</span>" if p["draft"] else ""
        rows.append(f"<tr><td>#{n}{draft}</td><td><b>{esc(name)}.</b> {what}</td><td class=\"n\">+{p['add']} −{p['del']}<br><span class=\"muted\">{p['nfiles']} files</span></td>"
                    f"<td>{intocell}; {ci} at its head{(', ' + p['head_date'][5:]) if p.get('head_date') else ''}</td><td>{esc(review_state(n))}</td><td>{need}</td><td>{esc(authors(n))}</td></tr>")
    return '<table class="vals">' + "".join(rows) + "</table>"


def later_table():
    rows = ["<tr><th>PR</th><th>What it is</th><th>Size</th><th>Why not today</th></tr>"]
    for n, name, t, what, need in by["later"]:
        p = P.get(str(n))
        sz = f"+{p['add']} −{p['del']}" if p else "—"
        draft = " <span class=\"muted\">(draft)</span>" if p and p["draft"] else ""
        rows.append(f"<tr><td>#{n}{draft}</td><td><b>{esc(name)}.</b> {what}</td><td class=\"n\">{sz}</td><td>{need}</td></tr>")
    return '<table class="vals">' + "".join(rows) + "</table>"


def fig_counts():
    """the 48, by tier: one stacked bar"""
    parts = [(t, len(by[t]), lab) for t, lab in TIERS] + [("out", len(LIVELITS), "Livelits, left out")]
    W, x0, x1 = 760, 10, 750
    unit = (x1 - x0) / 48
    g, x = [], x0
    for t, k, lab in parts:
        w = k * unit
        g.append(f'<rect class="b-{t}" x="{x:.1f}" y="10" width="{w - 2:.1f}" height="34" rx="4"/>')
        g.append(f'<text class="cnt{" dk" if t in ("later", "out") else ""}" x="{x + w / 2 - 1:.1f}" y="32" text-anchor="middle">{k}</text>')
        g.append(f'<text class="lbl" x="{x + 2:.1f}" y="62">{esc(lab)}</text>' if w > 110 else f'<text class="lbl" x="{x + 2:.1f}" y="62">{esc(lab.split(",")[0].split(" ")[0])}</text>')
        x += w
    return (f'<figure class="chart"><svg viewBox="0 0 {W} 72" role="img" aria-label="Our 48 open PRs: 11 ready for a review, 3 with a conflict to resolve, 9 waiting on a decision, 16 not for today, and 9 livelits PRs left out.">'
            + "".join(g) + "</svg><figcaption>Our 48 open PRs on hazelgrove/hazel, by what each needs before it can merge into dev, on the morning of 2026-11-19.</figcaption></figure>")


def fig_sizes():
    """each candidate of the first three tiers, its lines changed on a log scale"""
    rows = [(t, p) for t, _ in TIERS[:3] for p in by[t]]
    W, LX, BX, BW, RH = 760, 8, 330, 360, 19
    lo, hi = math.log10(5), math.log10(1500)
    sx = lambda v: BX + (math.log10(max(v, 5)) - lo) / (hi - lo) * BW
    g, y = [], 8
    for t, lab in TIERS[:3]:
        g.append(f'<text class="grp" x="{LX}" y="{y + 12}">{esc(lab)}</text>')
        y += RH
        for n, name, _, _, _ in by[t]:
            p = P[str(n)]
            v = p["add"] + p["del"]
            g.append(f'<text class="lbl" x="{LX + 10}" y="{y + 12}">#{n} {esc(name if len(name) < 44 else name[:42] + "…")}</text>')
            g.append(f'<rect class="b-{t}" x="{BX}" y="{y + 3}" width="{sx(v) - BX:.1f}" height="12" rx="2"/>')
            g.append(f'<text class="val" x="{sx(v) + 5:.1f}" y="{y + 13}">{v}</text>')
            y += RH
        y += 6
    for v in (10, 100, 1000):
        g.insert(0, f'<line class="ax" x1="{sx(v):.1f}" y1="4" x2="{sx(v):.1f}" y2="{y - 4}"/><text class="val" x="{sx(v):.1f}" y="{y + 8}" text-anchor="middle">{v} lines</text>')
    return (f'<figure class="chart"><svg viewBox="0 0 {W} {y + 14}" role="img" aria-label="The 23 candidates for today, each with the lines it adds and removes, on a log scale, from 9 lines for the README change to 1,038 for the largest decision.">'
            + "".join(g) + "</svg><figcaption>The candidates for today, each bar the lines its PR adds and removes on GitHub, on a log scale. Most of the ready ones are under 200 lines. A stacked PR's count includes the PRs under it until those merge.</figcaption></figure>")


def queue_list():
    out = ['<ol class="queue">']
    for i, (ns, why) in enumerate(QUEUE, 1):
        tot = sum(size(n) for n in ns)
        out.append(f"<li><b>Group {i}:</b> {', '.join('#' + str(n) for n in ns)} ({tot:,} lines in all). {why}</li>")
    out.append("<li><b>Then,</b> as the team decides: #2828, #2793, #2614 and #2610 in the chosen order, #2717, #2592; and each test PR once the fixes it holds to budgets are in (#2689 after #2603 and #2651, #2690 after #2675, #2691 after #2606 and #2608).</li></ol>")
    return "".join(out)


# dated updates since the first version, newest last, each shown under the outline (the tables stay as gathered that morning)
UPDATES = [
    ("2026-11-19 08:16 MST",
     "the three conflicts are resolved, each by merging dev into its branch, and CI is green on all three, full tests included. "
     "#2613 (colors) drops its edit to the deleted <code>assistant.css</code>, and its lint list keeps only <code>font-mono</code>; it is still approved, "
     "and can go into the merge queue now. #2606 (the worker keeps its cache) keeps both sets of tests, and #2660's test requests carry the two fields it adds; "
     "the cost gate still sees the previous run's steps, since the worker resolves the kept cache before it asks. #2661 (types get a Merkle hash) "
     "remembers dev's new unrolled check by hash. #2697 has dev merged in, so its diff is its own commit (2 files), its CI is green, "
     "and it is marked ready. So 14 PRs now need only an approval, one of them already approved (#2613). The tables below are as gathered at 07:35."),
]
updates_html = "".join(f'<p class="note"><b>Update, {esc(when)}:</b> {text}</p>\n' for when, text in UPDATES)
ready_lines = sum(size(p[0]) for p in by["ready"])
FIGS = {"updated": updated, "updates": updates_html,"fig_counts": fig_counts(), "fig_sizes": fig_sizes(), "tab_ready": table("ready"), "tab_conflict": table("conflict"),
        "tab_decide": table("decide"), "tab_later": later_table(), "queue": queue_list(), "ready_lines": f"{ready_lines:,}",
        "n_ready": str(len(by["ready"])), "n_conflict": str(len(by["conflict"])), "n_decide": str(len(by["decide"])), "n_later": str(len(by["later"])),
        "livelits": ", ".join("#" + str(n) for n in LIVELITS), "dev_commit": D["dev"]["commit"]}
body = open(os.path.join(HERE, "body.html")).read()
for k, v in FIGS.items():
    body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{(\w+)\}\}", body)
assert not left, left
TITLE = "What Could Merge Today"
DESC = ("For the Hazel team's merge-a-thon of 2026-11-19: our 39 open PRs that are not livelits, sorted by what each needs. "
        "Eleven merge cleanly into today's dev with CI green and need only a review; three need one conflict resolved; nine need a decision first.")
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{esc(DESC)}\">\n<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
json.dump({"dev": D["dev"], "tiers": {t: [dict(pr=n, name=nm, what=re.sub("<[^>]+>", "", w), before_merge=re.sub("<[^>]+>", "", nd)) for n, nm, _, w, nd in by[t]] for t, _ in TIERS},
           "livelits_left_out": LIVELITS, "updates": [dict(when=w, text=re.sub("<[^>]+>", "", t)) for w, t in UPDATES], "queue": [dict(group=i, prs=ns, why=re.sub("<[^>]+>", "", w)) for i, (ns, w) in enumerate(QUEUE, 1)]},
          open(os.path.join(HERE, "data", "tiers.json"), "w"), indent=1)
print("wrote 058/index.html;", updated, {t: len(by[t]) for t, _ in TIERS}, "ready lines", ready_lines)
