#!/usr/bin/env python3
"""^report(53): Fewer, Deeper Fixes. Matthew Hammer, 2026-11-10, sharing Matthew Keenan's reply of 2026-11-09 to
^report(48), A Thousand Cuts: "Let's write a report with this feedback, and our reasoned response to it." And:
"public WIP draft".

Writes 053/index.html from body.html, report 048's ledger (048/data/ledger.json: 196 costs, each with its root cause),
and the points below, each answered from the series' measurements."""
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
  table.vals td:first-child { min-width: 16ch; } table.points td:nth-child(2) { min-width: 30ch; } table.points td:nth-child(3) { min-width: 30ch; }
  blockquote.msg { margin: 1em 0; padding: 0.4em 1.1em; border-left: 4px solid var(--accent); background: color-mix(in srgb, var(--accent) 5%, transparent); border-radius: 0 6px 6px 0; }
  blockquote.msg li { margin: 0.45em 0; }
  figure.f { margin: 1.2em 0; } figure.f svg { max-width: 100%; }
  figcaption { color: var(--muted); font-size: 0.9em; margin-top: 6px; max-width: 80ch; }
  code { overflow-wrap: anywhere; }
"""
updated = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
esc = lambda s: html.escape(s, quote=True)

# ---------------------------------------------------------------- his message, as he wrote it (Slack, 2026-11-09)
INTRO = ("my thoughts on your cuts that you can feed into your agent in case you want to inject more prompting/data/"
         "opinions into it. lmk (or get your agent to lmk) if there’s any important facets I skipped over that need a "
         "gut opinion.")
CAVEAT = ("note these are all gut reactions, I haven’t spent too long thinking about any particular one, please "
          "don’t treat any of them as invariants")
OVERALL = ("Overall: I’m really really really scared of having an agent fix a thousand cuts it’s found. Especially "
           "I’m scared that it’ll fix them all separately. A lot of these can be fixed together. I’d say "
           "agent-generated prs, at least in 2026 still generally decrease the quality of the codebase rather than "
           "increasing it; a thousand independent fixes could go a long way to making the codebase harder to use; and I "
           "would think we could get more out in the long term if we do a few well-chosen well-implemented fixes and "
           "simplifications instead of a thousand things that only fix certain cases and plaster on special-case logic "
           "throughout the codebase")
BULLETS_HEAD = "Ids-on-every-term:"
BULLETS = [
    "Heavily in favor of any changes that are fully internal to Id.mk or id equality. The string thing sounds like it could be an easy, clean win. I’m pretty sure we’re still even using an old and possibly deprecated id library on ocaml.",
    "Evaluation already doesn’t (or shouldn’t) mint new ids during evaluation. Evaluation does give new ids to output expressions, this is to make sure that output expressions don’t mess up tylr because tylr needs unique ids. Any changes to that need to be really careful not to re-introduce weird selection bugs when the ids are no longer uniqified coming out of evaluation. My preference would be to not let the temp ids escape evaluation, otherwise we have to think harder..",
    "Ascriptions’ run-time checks look like they need a think-through. They shouldn’t be taking this long and if they are I worry Merklizaiton is just going to hide the problem, we probably want to make sure they’re not doing more checks than they should?.",
    "List walking being quadratic sounds familiar - I’m pretty sure I’ve fixed that before, curious to know why it’s back - are those different scenarios or is it the same one back again? I don’t get why it should be quadratic in the length of the list..",
    "ok after having seen a bunch of these being due to pushing list types, I’m thinking we should think seriously about bringing back something resembling the cast calculus, or at least find a way to remove casts/ascriptions in places where we know the types are safe. Could be a bit of a research question though. We removed casts originally because they were too confusing for maintainers; I suspect we can come up with something better..",
    "variable lookups don’t need to mint new ids; in fact the evaluator ids really don’t matter because they’re replaced once the evaluator is finished. We should make sure there’s no new minting and everything new is Id.temp. That feels like it would be a pretty easy and principled change.",
    "The evaluator shouldn’t be re-traversing anything that’s final and I’m not clear from your report where that’s coming from? It sounds like there could possibly be an issue where things coming out of the environment are getting evaluated - they shouldn’t (unless they’re a fixpoint), it should treat them as value, that’s what the final flag in transition is for.",
    "The worker-editor transition is a massive problem, which I’m seeing in a load of different problems, but I don’t see the correct full fix. We either need to be able to send stuff over quickly, or just leave more information on the webworker and treat it as a language server. Any attempts to make what we’re sending over smaller I think are putting the cart before the horse..",
    "Environments in probes is an interesting one: I kinda assumed that structure-sharing between environments would save most of the memory issues here, but I guess it doesn’t, worth now asking the quesiton then whether it’s fundamental: i.e. we are just storing that much memory because we want it on probes, or whether there’s a specific place hwere we’re leaking in terms of ocaml’s structure sharing..",
    "Iirc Andrew had a branch where he was incrementalizing or memoizing all the statics and maketerm and everything for big programs - idk how it works or how well it went.",
    "For lets, I wonder whether there’s a simpler version where we just always assume lets can be recursive, without having to do any of the fancy function checking or anything, might be more intuitive for the user to know they’re always recursive too. (Perhaps a warning if you just do let x = x, similar to the new type x = x warning).",
    "Re-running the whole of statics is the incrementalizing statics issue. I think we’re letting perfect be the enemy of the good here, like we don’t have to make implementing Thomas’s statics as part of the global world tree be the first pass here..",
    "Merkle hashing feels like a decently well-contained project (if engineered well) within grammar (or even just a ppx?) that could go a long way; especially on things like the expression comparisons in incremental, or type comparisons..",
    "Incremental evaluation doesn’t do anything inside functions - I think that’s what the ‘incremental evaluation doesn’t work on sliders’ on is complaining about. With incremental evaluation we have to decide on some limit for what we’re caching. I was thinking we could do something with caching values by callstack ids, not just top-level id, and that’s what I described and proved in my paper - I think a names-based approach could be simpler here too though. I was hoping whatever we do we can still make it intuitive to the user what’s being cached and what’s not..",
    "Undo keeping whole editor state is a known issue, I’d love to go bigger on using Bonsai to separate out the non-derived from derived information and only undoing non-derived information. I had a bonsaification branch a while ago which is probably archived now..",
    "Rendering is again something I think can be fixed with better bonsaification, I think it has ways to make stuff render-on-demand and a better fine-grained system for re-rendering only parts that have changed.",
]

# ---------------------------------------------------------------- Matthew Hammer's replies on Slack, as he sent them
REPLY_1109 = [
    "Thanks for the detailed feedback!",
    "Point taken about the relatively low quality of machine-generated, machine-architected code.  The way the machine talks about the code is also sub-par, in my opinion.  It started calling everything a \u201ccut\u201d when I originally meant \u201cdeath by a thousand cuts\u201dto refer to the relatively expensive way that Hazel operates.  It started calling each improvement a \u201ccut\u201d, which definitely isn\u2019t \u201cmy voice\u201d for writing anything to the agent.  I apologize for that.",
    "I\u2019m not sure which PR you\u2019re thinking about most, or maybe just in general, but I generally agree.",
    "I think of the main benefit of the agent-based code generation to be cheap prototyping, to check the viability or actual experience of an idea, and quick scientific inquiry into questions that would take days or weeks to answer otherwise.",
    "To be sure, I agree that the code it generates still lacks quality, generally.  I never meant to suggest otherwise.",
]
REPLY_1110 = [
    "In the expectation that we want to polish or even totally redo some agentic codegen in my PRs, I\u2019m asking the agent to review the prototype JIT system and other performance stuff for livelits, and rank the components/changes in order of what helped most.",
    "The code quality may be low, but I can now get a redrawn picture in 31ms instead of several seconds later.  Seems like there\u2019s a lot of value here, regardless of the code structure.",
]

# ---------------------------------------------------------------- the fixes we propose, each aimed at a family of costs
FIXES = [
    dict(key="merkle", n=1, name="Merkle hashes in the grammar", color="#0d9488",
         causes=["incremental reuse checks"],
         what="A hash on every term, type and value, kept on the node itself (in Grammar, or by a ppx), so that equality is a hash compare and a cache key is cheap. It retires the family of compares that walk two equal copies node by node.",
         first="Hashes on the node, not in a side table: the experiment of report 009 put them on values and the slowdown with the heap went away (2.3, 5.5, 6.3 s to 2.2, 2.5, 2.2 s).",
         ours="Our week on hazel-jit met the same family again and again: build 31's check, keyed on a livelit's definition, found a new copy at each lookup (a drag 15.1 ms a frame, from 8.2); build 33's shape cache compared a model's value at every frame (16.1 ms); and the view cache compares 104 sample values by value at each answer, 2 to 8 ms (report 051). Each got its own cache; a hash on each value would serve them all."),
    dict(key="ids", n=2, name="Ids: cheap to make, and temporary inside the evaluator", color="#2563eb",
         causes=["ids on every term"],
         what="Id.mk made cheap inside Id, its interface unchanged; and every id the evaluator makes an Id.temp, real ids given only to what leaves the evaluator, as Matthew Keenan proposes.",
         first="Port the trial line's Id.mk (one string concatenation an id, report 045) to dev; then audit the evaluator's mints (variable lookups 38%, environment frames 20%, ascriptions about 30%, report 009).",
         ours="hazel-jit's compiled run works on JavaScript values and makes ids only for what it gives back to Hazel as terms; making those took almost half of the way back until Id.mk was made cheap (report 045)."),
    dict(key="checks", n=3, name="Check a value's type once", color="#7c3aed",
         causes=["run-time type checks (ascriptions, casts)"],
         what="An ascription or annotation checks a value once, and a value known to have a type is not checked against it again: something resembling the cast calculus, or a mark on checked values. It retires the repeated checks, including the quadratic walk of an annotated recursive helper over the rest of its list.",
         first="Count the checks before caching them: for the World rule, how many times each list cell is checked against [Square] per move.",
         ours="Two of the open fixes cache the checks (#2661 hashes the types, #2681 memoizes them); as Matthew Keenan says, a cache can hide that the checks repeat."),
    dict(key="server", n=4, name="The worker as a language server", color="#b45309",
         causes=["the worker trip", "serialization (Marshal, sharing)"],
         what="The worker keeps the program, its statics and its run, and the page asks it for what it shows (a probe's samples, a livelit's answer) rather than receiving a whole answer after every run.",
         first="Write down which of the page's readers need the worker's answer at all, now that hazel-jit draws livelits from the page's own compiled run.",
         ours="Our changes to the answer (5.4 MB to 198 KB, reports 046 and 051) were the cart before the horse, in his words; with hazel-jit the picture no longer waits for the worker, and what is left of the trip is the page taking the answer in, 50 to 60 ms (report 052)."),
    dict(key="statics", n=5, name="Incremental statics, landed as it is", color="#15803d",
         causes=["re-analysis per edit (statics, parsing)"],
         what="Per-item statics (Andrew Blinn's DefStatics, on #2469) to dev first, as the good-enough first pass; finer grain later, by measurement.",
         first="Land #2469's per-item statics on dev.",
         ours="Ticket 721's patch for a livelit's literal (build 45) is the special case Matthew Keenan warns about: one kind of edit, patched by hand inside DefStatics. It measures what finer-grained statics would buy (12 to 28 ms a slider step on the Witch), but it should not land ahead of the general version."),
    dict(key="bonsai", n=6, name="Derived state and rendering through Bonsai", color="#b91c1c",
         causes=["the page's view and redraw", "undo and history"],
         what="Separate what is derived (syntax, statics, layout, views) from what is not, so undo keeps only the latter and rendering recomputes only what changed.",
         first="Find Matthew Keenan's bonsaification branch and measure it on one slide.",
         ours="Most of our week's caches (projector data, the view cache, the outline's memos) are hand-written incrementality of the kind Bonsai's model provides; each is one more place a key can go stale."),
]
LEDGER = json.load(open(os.path.join(ROOT, "048", "data", "ledger.json")))
CAUSES = {}
for c in LEDGER:
    CAUSES[c.get("root_cause", "other")] = CAUSES.get(c.get("root_cause", "other"), 0) + 1
FIX_OF = {cause: f for f in FIXES for cause in f["causes"]}
for f in FIXES:
    f["costs"] = sum(CAUSES.get(c, 0) for c in f["causes"])
COVERED = sum(f["costs"] for f in FIXES)
TRIP = CAUSES.get("the worker trip", 0) + CAUSES.get("serialization (Marshal, sharing)", 0)
FMT = dict(covered=COVERED, n_causes=len(CAUSES), trip=TRIP)

# ---------------------------------------------------------------- each of his points, and what the series measured
POINTS = [
    ("Overall: a few well-chosen fixes, not a thousand separate ones",
     "Our own last five days on hazel-jit (report 052): 120 commits on one branch, 9,200 lines added to src/, 6 of its 10 ingredients with no test of their own, 7 commits that only fixed the one before (and 3 more since), and caches keyed on object identity, two of which made a drag slower before they were fixed (builds 31 and 33).",
     "Agreed, and our record shows the risk he names. The 196 costs in report 048's ledger come down to {n_causes} root causes; six fixes would address the causes of {covered} of them (the figure below).", "all"),
    ("Ids: changes internal to Id.mk or id equality; the old id library",
     "Id.t is Uuidm.t (uuidm 0.9.8). On dev, Id.mk makes each id through Uuidm.v4's byte copy, about 20% of all time in a profile of a JS call into Hazel (report 025); on the hazel-jit line it builds the same 16 bytes from a counter by one string concatenation (report 045: 906 ids in 0.044 ms, from 0.29). The interpreter minted 461,422 ids for a 33,847-node picture (report 009).",
     "Agreed: the trial line's Id.mk is the internal change he describes, and can go to dev as it is. Replacing uuidm is possible behind Id's interface too, keeping the serialized form.", "ids"),
    ("Evaluation's ids: don't let temp ids escape",
     "Variable lookups make 38% of the ids the evaluator mints, environment frames 20%, ascriptions about 30% (report 009); fresh ids make the worker's requests 1.99 times larger and its results 11% (report 009). A local experiment with content-derived names removed 92 to 97% of them, at 11 to 31% more time.",
     "Agreed, and simpler than our content-derived names: Id.temp inside the evaluator, real ids only for what leaves it, so the editor (tylr) still sees unique ids.", "ids"),
    ("Ascriptions' run-time checks: more checks than they should?",
     "Ascribing a constructor application compared two copies of the Html type at every node of a view: 88% of a 15 to 17 s Polygons click (report 017). The same ascription re-checks inside the woods picture's view (14 to 16%, report 025).",
     "Agreed that the count is the problem: #2661 (Merkle-hashed types) and #2681 (a memo) make each check cheap but leave them repeating. Counting checks per value comes first.", "checks"),
    ("Quadratic list walking: the same one back again?",
     "This one comes from an annotation: a recursive function whose list parameter is annotated checks the whole rest of the list at every call, n calls over n cells: 205 ms at 400 elements (report 017), the World rule 144 ms at 16x16 against 18 ms unannotated (report 025).",
     "We cannot tell whether it is the case he fixed before; this one is quadratic because each recursive call re-checks its argument against its annotation, not because of how the list is walked.", "checks"),
    ("Something resembling the cast calculus",
     "Ten of the 196 costs are run-time type checks (ascriptions, casts), the quadratic one among them.",
     "Agreed as a direction, and a research question, as he says; it is the fix that removes the checks rather than caching them.", "checks"),
    ("Variable lookups needn't mint ids",
     "38% of the evaluator's ids (report 009).",
     "Agreed: Id.temp there is the cheapest principled change on the list.", "ids"),
    ("The evaluator re-traversing what is final",
     "Three costs: the evaluator visits values that are already final (a third of a loop's passes take no step, report 029); a value held in a closure is re-stepped when substituted into each call (report 025); a function Hazel's JS library returns has its environment substituted into its body, so a held list is re-evaluated at every call (report 029; fixed on trials, #2808 open).",
     "Consistent with his diagnosis: the cases we found come through substitution, on the library path, rather than through environment lookups. Checking that the final flag is set on those paths is the next step, before any fast path.", None),
    ("The worker-editor transition: send it fast, or a language server",
     "{trip} of the costs are the worker trip or the serialization across it. The answer went 5.4 MB, 0.42 MB, 198 KB (reports 046, 051); the request went whole whenever the page's statics did not match the per-item analysis (build 44, report 052).",
     "Agreed that shrinking is the cart before the horse. hazel-jit has taken the worker off the path to the picture for livelits, which makes the language-server design easier to try: the page asks for what it shows.", "server"),
    ("Environments in probes: fundamental, or a sharing leak?",
     "A probe's environment was written out whole: the Drawing module in the sample of a probe whose value is a few bytes, 4.14 MB of a 5.4 MB answer (report 046).",
     "Not fundamental: in memory the environments share, but each sample's environment was serialized on its own across the worker boundary, and the worker's sharing pass found almost nothing to share (1.4 to 1.6 s a result, dropped in build 3 of report 050). The leak is at the boundary.", "server"),
    ("Andrew's branch incrementalizing statics and MakeTerm",
     "That is #2469 (modular editors): per-item statics (DefStatics) and incremental MakeTerm. It works: #2597, without it, re-ran statics on the whole program at every livelit commit, 3.5 s of a 5.8 s profiled release; a release took 3.76 s there against about 0.35 s on #2635, which has it (report 001).",
     "It is the base of everything in reports 049 to 052, and not yet on dev.", "statics"),
    ("Lets always recursive",
     "Every let-bound function takes statics' recursive path, and the passes multiply with nesting, up to 4 to the depth: nested lets took 400 s (report 001; #2603, open, takes it to 0.6 s).",
     "Worth trying: always-recursive lets remove the multiplier at its source rather than special-casing it. A language decision for the team; we can measure it.", "statics"),
    ("Incremental statics: don't let perfect be the enemy of the good",
     "Re-analysis per edit is the largest family, 28 of the 196 costs.",
     "Agreed: land per-item statics first. Ticket 721's literal patch (build 45) is not that, and should wait for it.", "statics"),
    ("Merkle hashing in the grammar, or a ppx",
     "Reuse checks with a Merkle hash: 283 to 26 ms on #2635, 2,743 to 410 ms on dev (#2673, open). Types: 15 to 17 s to 2.0 to 2.2 s (#2661, open). But ValueHash keeps its hashes in a WeakMap side table that slowed as it grew (2.3, 5.5, 6.3 s; 98 MB of what four edits kept, reports 009, 014).",
     "Strongly agreed, with one lesson from the measurements: the hash belongs on the node, not in a side table.", "merkle"),
    ("Incremental evaluation inside functions",
     "Incremental evaluation saves nothing on a slider edit (Witch 754 against 701 ms from scratch, report 009); every slider edit re-evaluates 85 to 95% of the figure (report 011).",
     "Agreed that this is the root of 'it doesn't work on sliders'. hazel-jit sidesteps it for livelits by compiling the run (a step in 2 to 3 ms), but the worker still re-evaluates; caching by call-stack ids or names is the real fix.", None),
    ("Undo keeping whole editor state; Bonsai",
     "About 92 MB kept per edit, uncapped (report 014). Andrew Blinn's compaction held #2597 to 159 MB (report 020), but restoring a compacted entry rebuilds what is derived: a redo took 6.0 to 6.5 s there, against 2.7 to 3.1 s before (report 014).",
     "Agreed: undo should keep only what is not derived.", "bonsai"),
    ("Rendering through Bonsai",
     "The page's view and redraw are the second-largest family, 25 of the 196 costs.",
     "Agreed; our own caches this week are hand-written incrementality.", "bonsai"),
]


# ---------------------------------------------------------------- root causes no fix here addresses: a question each, for a gut opinion
SKIPPED = [
    ("interpretation itself", "The interpreter is slow at what any interpreter is slow at: a livelit's render 40 times slower than compiled with the trip in and out, a recursive sum of 1,000 1,152 times (report 045).",
     "Should a compiler like hazel-jit become a second way to run Hazel programs, beside the interpreter, and if so who keeps the two in step? Or should it stay a livelit's fast path?"),
    ("the JS boundary (js_of_ocaml)", "js_of_ocaml's generic calls (11.6% of self time), values converted from JS as syntax the evaluator steps back into a value (56% of a call's floor), Uuidm's byte copy (report 025).",
     "Is there a representation of values that crosses the boundary cheaply, so that a JS call into Hazel does not rebuild what it was given?"),
    ("environments and substitution", "A value held in a closure is substituted into each call and stepped again (report 025); environment lookups 7.2% of a loop (report 035).",
     "Substitution or environments for the evaluator's own steps: is the final flag he mentions enough, or is it time to evaluate with environments throughout?"),
    ("values are terms (open terms, holes, closures)", "The Witch's picture sent as terms: 142.2 KB and 24.0 ms to encode and decode, against 48.0 KB and 6.09 ms as plain data (report 047).",
     "Should closed, first-order values (numbers, strings, lists, records of them) have a representation of their own, apart from terms?"),
    ("persistent maps and allocation (GC)", "Garbage collection 18% of a JS call's floor, 19.8% of a plain walk's self time (report 025); a pause of 20 to 35 ms once a slider step (report 052).",
     "Which of the evaluator's maps and copies could be mutable and local, or shared?"),
    ("data representation (flat lists, no maps)", "Hazel has no map, so a rule walks a list to find a square: 254 ms at 64x64, against 0.54 ms for Fumola's HashMap (report 027).",
     "A map in Hazel's library, or in the language?"),
    ("parsing on load", "Opening a program parses it whole (report 048's five costs).", "Worth incremental parsing, or only a cache of parsed programs?"),
    ("trampolines and stack safety", "The evaluator's trampolines are part of a loop's per-pass cost (report 029).", "Is stack depth still the constraint that made them necessary?"),
    ("scheduling (worker slices, message cadence)", "How often the worker yields and sends (report 004: 5.8 to 6.2 s of a 10 s change idle between slices, fixed).", "Folded into the language-server design (fix 4)?"),
]


# ---------------------------------------------------------------- figure: the costs by root cause, each colored by the fix that addresses it


def fig_causes():
    rows = sorted(CAUSES.items(), key=lambda kv: -kv[1])
    W, L, R, top, rh = 900, 300, 60, 46, 21
    H = top + rh * len(rows) + 40
    mx = max(v for _, v in rows)
    X = lambda v: L + v / mx * (W - L - R)
    out = [f'<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">The 196 costs in report 048\'s ledger, by root cause</text>',
           f'<text x="16" y="34" font-size="11" fill="var(--muted)">colored by the fix proposed here that addresses the cause; grey: no single fix</text>']
    for i, (cause, n) in enumerate(rows):
        y = top + i * rh
        f = FIX_OF.get(cause)
        col = f["color"] if f else "#9ca3af"
        out.append(f'<text x="{L - 8}" y="{y + 14}" font-size="10.5" text-anchor="end" fill="var(--ink)">{esc(cause)}</text>')
        out.append(f'<rect x="{L}" y="{y + 4}" width="{X(n) - L:.1f}" height="13" rx="2" fill="{col}" opacity="0.85"/>')
        lab = f"{n}" + (f" · fix {f['n']}" if f else "")
        out.append(f'<text x="{X(n) + 6:.1f}" y="{y + 14}" font-size="10" fill="var(--muted)">{esc(lab)}</text>')
    cap = (f"Not a build of the app: report 048's ledger of the costs the series measured from report 001 to 047, each "
           f"filed under one root cause. The six fixes proposed here address the causes of {COVERED} of the 196 costs; the "
           f"rest (the interpreter itself, the JS boundary, environments and substitution, values held as terms, and "
           f"others) have no single fix on this list.")
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {H}" role="img" aria-label="Bars of the 196 costs '
            f'by root cause, colored by proposed fix" style="width:100%;height:auto;display:block">' + "".join(out) +
            f"</svg><figcaption>{cap}</figcaption></figure></div>")


def message_block():
    li = "".join(f"<li>{esc(b)}</li>" for b in BULLETS)
    return (f'<blockquote class="msg"><p>{esc(INTRO)}</p><p><i>{esc(CAVEAT)}</i></p><p>{esc(OVERALL)}</p>'
            f'<p><b>{esc(BULLETS_HEAD)}</b></p><ul>{li}</ul></blockquote>')


def replies_block():
    a = "".join(f"<p>{esc(x)}</p>" for x in REPLY_1109)
    b = "".join(f"<p>{esc(x)}</p>" for x in REPLY_1110)
    return (f'<p class="muted">On Slack, 2026-11-09, to the team and to Matthew Keenan:</p><blockquote class="msg">{a}</blockquote>'
            f'<p class="muted">And on 2026-11-10, with a link to <a href="../052/#now">report 052, where it stands</a>:</p>'
            f'<blockquote class="msg">{b}</blockquote>')


def skipped_table():
    rows = ["<tr><th>Root cause</th><th>Costs</th><th>What the series measured</th><th>The question</th></tr>"]
    for cause, ev, q in SKIPPED:
        rows.append(f"<tr><td><b>{esc(cause)}</b></td><td class=\"n\">{CAUSES.get(cause, 0)}</td><td>{esc(ev)}</td><td>{esc(q)}</td></tr>")
    return '<table class="vals">' + "".join(rows) + "</table>"


def points_table():
    rows = ["<tr><th>His point</th><th>What the series measured</th><th>Our read</th><th>Fix</th></tr>"]
    fx = {f["key"]: f for f in FIXES}
    for p, ev, read, k in POINTS:
        fix = "all six" if k == "all" else (f'{fx[k]["n"]} · {esc(fx[k]["name"])}' if k else "—")
        rows.append(f"<tr><td><b>{esc(p)}</b></td><td>{esc(ev.format(**FMT))}</td><td>{esc(read.format(**FMT))}</td><td>{fix}</td></tr>")
    return '<table class="vals points">' + "".join(rows) + "</table>"


def fixes_table():
    rows = ["<tr><th>Fix</th><th>What it is</th><th>Costs whose cause it addresses</th><th>First step</th><th>From our own work</th></tr>"]
    for f in FIXES:
        rows.append(f'<tr id="fix-{f["key"]}"><td><b>{f["n"]}. {esc(f["name"])}</b></td><td>{esc(f["what"])}</td>'
                    f'<td class="n">{f["costs"]} ({esc(", ".join(f["causes"]))})</td><td>{esc(f["first"])}</td><td>{esc(f["ours"])}</td></tr>')
    return '<table class="vals">' + "".join(rows) + "</table>"


NUMS = {"updated": updated, "covered": str(COVERED), "n_causes": str(len(CAUSES)), "n_fixes": str(len(FIXES)), "trip": str(TRIP)}
FIGS = {"fig_causes": fig_causes(), "msg": message_block(), "replies": replies_block(), "tab_skipped": skipped_table(), "tab_points": points_table(), "tab_fixes": fixes_table()}
body = open(os.path.join(HERE, "body.html")).read()
for k, v in {**NUMS, **FIGS}.items():
    body = body.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{(\w+)\}\}", body)
assert not left, left
TITLE = "Fewer, Deeper Fixes"
head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{TITLE}</title>\n"
        "<meta name=\"description\" content=\"Matthew Keenan's read of the costs in report 048's ledger, in his words, Matthew Hammer's replies, and our response point by point: what the series measured, where we agree, and six fixes that would address the causes of most of the costs.\">\n"
        "<style>" + CSS + EXTRA + "</style>\n</head>\n")
open(os.path.join(HERE, "index.html"), "w").write(head + body)
json.dump({"replies": {"from": "Matthew Hammer", "2026-11-09": REPLY_1109, "2026-11-10": REPLY_1110}, "message": {"from": "Matthew Keenan", "date": "2026-11-09", "intro": INTRO, "caveat": CAVEAT, "overall": OVERALL,
                       "ids_on_every_term": BULLETS},
           "points": [{"point": p, "measured": e.format(**FMT), "our_read": r.format(**FMT), "fix": k} for p, e, r, k in POINTS],
           "fixes": [{k: v for k, v in f.items() if k != "color"} for f in FIXES],
           "causes": CAUSES, "covered": COVERED, "skipped": [{"cause": c, "measured": e, "question": q} for c, e, q in SKIPPED]},
          open(os.path.join(HERE, "data", "numbers.json"), "w"), indent=1)
print("wrote 053/index.html;", updated, NUMS)
