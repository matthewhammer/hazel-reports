#!/usr/bin/env python3
"""Writes 066/data/agenda.json (^report(66), the agenda for 2026-11-27). Kept as Python only so the long HTML strings
need no JSON escaping by hand; agenda.json is what gen066.py reads, and it can be edited directly from now on."""
import json, os

R = lambda n: f'<code class="ref"><b>^report(</b>{n}<b>)</b></code>'
RL = lambda n: f'<a href="../{n:03d}/">{R(n)}</a>'
T = lambda n: f'<code class="ref"><b>^ticket(</b>{n}<b>)</b></code>'
UPDATED = "2026-11-27 07:11 MST"
AS_OF = "2026-11-27 07:05 MST (git, gh, npm and the dashboard read then)"

jit = {
    "id": "jit",
    "title": "hazel-jit: last week against this week",
    "asked": "Matthew (his list, item 1)",
    "ticket": None,
    "status": "one PR from dev since 11-23 (#2859, CI green); the games now 3.8× plain JS's time, from 11.9× on 11-19; a division trial green, waiting on Matthew's word",
    "tone": "accent",
    "as_of": AS_OF,
    "body": (
        f"<p><b>Last week, as of Friday 11-20:</b> hazel-jit lived on the livelits line's trial branches, none of them from dev: #2817 (trial/694-view-jit: livelit views and a slide's whole run), trial/794-games-aot (the games compiled ahead of time) and trial/758-sint64-jit. The npm package did not have it (hazeljs 0.0.8 ran the interpreter only). On the games of hazeljs-examples it took <b>11.9 times</b> the time of each game's plain JS ({RL(65)}).</p>"
        f"<p><b>This week:</b></p><ul>"
        f"<li><b>One home, from dev (11-23).</b> #2859, branch <code>hazel-jit</code>, a draft from dev at 21da4ae66b, after dev's move to Jane Street Core: the compiler, the values across, and <i>mixed mode</i>, where the interpreter calls a program's fully typed functions compiled. 25 commits, 5,704 lines added and 4 removed; CI green. Of the 289 evaluator checks, 234 compile and 211 of those give the interpreter's answer, none differs (the other 23 end in something that is not a value; CI run 45540053889). Nothing in the app turns it on yet. By Matthew's rule of 11-23, the jit lives in this PR and in the package's, #2857, which merges it.</li>"
        f"<li><b>Its output now reads like ReScript's and Melange's (11-24, 11-25):</b> records as plain JS objects, a named function's tuple parts as JS arguments, a function's tail calls of itself as loops, constructors without arguments made once, a module's members by name, <code>===</code> against a literal ({T(847)}, {T(853)}). On the 14 games: <b>3.8 times plain JS</b>, from 11.9 on 11-19, and 4,148 times as fast as the interpreter (GitHub run 45666570615, every answer the same four ways; the figure).</li>"
        f"<li><b>Holes (merged 11-26 on Matthew's word):</b> in mixed mode an argument's hole crosses into compiled code unopened, and code with holes compiles; only a call that looks inside a hole falls back ({T(769)}). John (johnya) is on probes now, so holes are ours.</li>"
        f"<li><b>The night of 11-26:</b> trial/891-idiv (off <code>hazel-jit</code>, 664c49c49a, CI green): Int division as <code>Math.trunc(a / b) + 0</code>, and Int arithmetic on numbers written out folded at compile time. Gnome world's World.step about 40% faster on fresh inputs (5.15–5.25 µs to 3.02–3.19, one GitHub runner, three rounds), and a −0 the interpreter never gives is gone ({T(891)}). With the four package trials (item 2), all five merged on trial/1126-night (abf653a21d, CI green, run 45943307054, 5,227 tests): World.step about 39% faster than the hazeljs branch (3.78–4.06 µs to 2.33–2.48; the figure).</li>"
        f"<li><b>The livelits line:</b> #2817 has a one-line fix to LivelitProj's view memo (1a8afab5ae, CI green, {T(887)}): the Witch's neck drag with compiling off now draws its view in 6.4 ms a frame (about 156 fps), compiled 5.0 ms (about 200 fps), one run in Firefox.</li>"
        f"</ul>"
    ),
    "meeting": "Merge trial/891-idiv into <code>hazel-jit</code> (#2859), and so into hazeljs (#2857)? What does #2859 need before it leaves draft for dev: which reviewer, and is the agreement sweep (211 agree, none differs) the right gate? SInt is 64 bits (settled 11-19), but dev still wraps a 32-bit SInt, so #2859 holds its SInt tests back until #2828 lands (item 3).",
}

npm = {
    "id": "npm",
    "title": "hazeljs, the npm package: last week against this week",
    "asked": "Matthew (his list, item 2)",
    "ticket": 890,
    "status": "0.0.14 on npm since 11-25, the first with hazel-jit; #2857 CI green; four trials green, waiting on Matthew's word",
    "tone": "accent2",
    "as_of": AS_OF,
    "body": (
        f"<p><b>Last week, as of Friday 11-20:</b> npm's latest was <b>0.0.8</b> (11-17): hazel-lib.js built from #2719's branch, the interpreter only, and hazel-listings.js. On 11-19 Cyrus asked the team to review the package's API and packaging ({T(773)}); that day the editor moved into the package, loading nothing from elsewhere (0.0.9, not published), with a font and icons of its own (#2837, #2842).</p>"
        f"<p><b>This week:</b></p><ul>"
        f"<li><b>One branch for the package (11-23):</b> #2857, branch <code>hazeljs</code>, a draft against dev, holds what the package is built from: the library (#2711, #2719), the editable embed (#2814), the font and icons, dev on Core, and hazel-jit by merging #2859, never by copying. 91 commits, 13,049 lines added; CI green. <code>Hazel.jit</code> and <code>Hazel.compile</code> are in the library.</li>"
        f"<li><b>The JS boundary:</b> values converted by the declared type, straight into compiled code's shapes; what was converted remembered by links on the objects (Mahjong solitaire's run 2.5 times as fast, ca851b422d). {RL(64)} was corrected: on fresh inputs, as a game gives them, the pieces that take lists cost 7 to 9 times their JS, not 2 to 4; the earlier timings reused the same objects, which the converters remember.</li>"
        f"<li><b>npm: 0.0.14 (11-25)</b>, published from Matthew's sign-in, the first since 0.0.8: hazel-jit's loops, JS arguments, constructors made once. 0.0.9 to 0.0.13 were made in the repository but not published (the figure).</li>"
        f"<li><b>The night of 11-26, four trials off <code>hazeljs</code>, each CI green on its own:</b>"
        f"<ul><li>{T(890)} trial/890-saved-program: <code>Hazel.jitProgramSaved</code> lets a page keep its compiled rules. Gnome world, with this trial library, has its rules ready 0.68 to 0.70 s after a reload, against 13.6 to 14.4 s for a cold build (one browser).</li>"
        f"<li>{T(681)} trial/681-memo-big: the converters stop remembering small conversions. On fresh copies, Solitaire 30 to 8.6 ms and Mahjong solitaire 33 to 12; on the same objects again most within 5%, a few slower (Solitaire 3.32 to 3.79 ms), and Minesweeper slower on fresh copies (13 to 16 ms).</li>"
        f"<li>{T(792)} trial/792-big-ints: an Int past 2^31 from JS arrives whole (a safe whole number to 2^53, a BigInt past it).</li>"
        f"<li>{T(791)} trial/791-labels-linear: two quadratic labeled-tuple helpers in Hazel's statics made linear; a build about 9% faster (warm 4.10–4.20 s to 3.77–3.79). LabeledTuple.re is shared Hazel code.</li></ul></li>"
        f"<li><b>Finding:</b> building a page's rules is Hazel's statics, not the jit. A CPU profile of Gnome world's build puts 70% of it in Statics.re and 28% in garbage collection; hazel-jit's compiling is 0.5% ({RL(64)}). Together the trials make the build about 8% faster (the figure).</li>"
        f"</ul>"
    ),
    "meeting": "Take the four trials into hazeljs (#2857) and publish 0.0.15? <code>jitProgramSaved</code> is an addition to the package's API. Should 791 go to dev as a small PR of its own, since LabeledTuple is shared code? And who on the team reviews the package's API and packaging, as Cyrus asked on 11-19?",
}

backburner = {
    "id": "back-burner",
    "title": "The back burner: the other open PRs",
    "asked": "Matthew (his list, item 3)",
    "ticket": None,
    "status": "46 open, 24 of them drafts; 3 merged at the 11-19 merge-a-thon; a few to settle",
    "tone": "warn",
    "as_of": AS_OF,
    "body": (
        f"<p><b>Since the last agenda:</b> at the merge-a-thon of 11-19 ({RL(58)}, which found 14 of 48 ready for only an approval) three merged: #2613 (every color a stylesheet reads, the theme defines), #2652 (the eval worker starts at load) and #2816 (ids as strings, evaluation about 13% faster on the heaviest programs); #2490, the wasm_of_ocaml spike, was closed. That evening dev moved to Jane Street Core (#2470 and the PRs stacked on it), after most of these PRs were written.</p>"
        f"<p><b>Worth a word today:</b></p><ul>"
        f"<li><b>#2828, SInt has 64 bits everywhere, and overflow is an error</b> (draft, CI green, no review yet, last changed 11-19). The width is settled (Cyrus 11-18, Matthew 11-19: 64 bits). Until it lands, dev wraps a 32-bit SInt where hazel-jit stops at an overflow, so #2859 holds those tests back.</li>"
        f"<li><b>#2812, Hazel's README links to hazeljs</b> (from {RL(42)}; a draft, review asked of Cyrus and the hazel-core team, none yet; CI green). The package has changed since: 0.0.14, with hazel-jit.</li>"
        f"<li><b>#2837, IBM Plex Sans in place of Helvetica Neue, and #2842, Material Icons shipped</b> (11-19, ready, against dev): the team's font question of 11-19. Both are already inside #2857.</li>"
        f"<li><b>The JS library's stack, #2711, #2719 and #2814:</b> #2857 is built from them. Keep them open, or close them in favor of #2857?</li>"
        f"<li><b>The livelits line,</b> #2597, #2635, #2817 and #2819: kept for now (Matthew, 11-23), no longer the only critical path (11-25).</li>"
        f"<li><b>The performance PRs to dev</b> (#2603, #2606, #2661, #2671, #2673, #2675, #2681 and others, 09-26 to 10-13): written before dev's move to Core; whether each still merges cleanly is not checked here.</li>"
        f"</ul>"
    ),
    "meeting": "Which of these should move this week: #2828 (so #2859's SInt tests return), #2812, or #2837 and #2842? Close the JS library's stack in favor of #2857? And the older performance PRs: rebase them onto Core, or park them?",
}

carroll = {
    "id": "carroll",
    "title": "Advice on an email from Max Carroll",
    "asked": "Matthew (his list, item 4, if there is time)",
    "ticket": None,
    "status": "Matthew brings the email",
    "tone": "muted",
    "as_of": "2026-11-27 07:05 MST",
    "body": "<p>Matthew has an email from Max Carroll (MaxCarroll0 on GitHub), a colleague, and would like Cyrus's advice on it. Matthew brings it to the meeting; this agenda does not summarize it.</p>",
    "meeting": "Cyrus's advice on the email.",
}

demo = {
    "id": "demo",
    "title": "A demo: Gnome dig and Gnome world",
    "asked": "Matthew (his list, item 5, if there is time)",
    "ticket": None,
    "status": "Gnome world 0.0.146 live 11-27 07:09: the flying jellyfish; its checks green",
    "tone": "good",
    "as_of": "2026-11-27 07:11 MST (0.0.146 live 07:09)",
    "body": (
        "<p><b>Two games in <a href=\"https://matthewhammer.org/hazeljs-examples/\">hazeljs-examples</a></b> whose rules are written in Hazel and run in the page through hazeljs and hazel-jit, each with a twin in plain JS for checks: <a href=\"https://matthewhammer.org/hazeljs-examples/dig/\">Gnome dig</a> and <a href=\"https://matthewhammer.org/hazeljs-examples/world/\">Gnome world</a>. Cyrus endorsed such game workloads as a corpus of Hazel code that is organically demanded (Matthew, 11-25).</p>"
        "<p><b>Last week, as of 11-20,</b> the repository was at 0.0.40, before either game: its VERSIONS.md first names Gnome dig at 0.0.61 (11-22) and Gnome world at 0.0.76 (11-23).</p>"
        "<p><b>This week:</b> Gnome world's rules are eleven Hazel modules (the figure), from World.hz on 11-23 to the animals on 11-26 and the jellyfish on 11-27. In 0.0.141 to 0.0.143 the bunnies', frogs' and birds' minds became Hazel, each checked against its JS twin on 600,000 of 600,000 steps in Node. N's level, 🌈 The rainbow sky, is 0.0.140. In 0.0.144 and 0.0.145 a page keeps its built rules between loads, but only with the trial library (<code>?libat=trial/890-saved-program</code>); with the shipped library each load still builds them (item 2). Its speed run of 44,933 steps takes 25.5 s with hazel-jit against 24.7 s in plain JS; the interpreter took 227.6 s for 42,000 of them ({R65}). With the five trials of 11-26 (trial/1126-night) a whole step in the page takes 1.92–2.05 ms with Hazel against 1.77–1.86 plain, well inside a 60 fps frame of 16.7 ms. </p><p><b>New this morning, 0.0.146</b> (commit 2026142, pushed 07:07, live 07:09; its world save check is green, GitHub run 46013126230, and it ran Jelly.step against its JS twin again there: the same at 40,000 of 40,000 steps): <b>the flying jellyfish</b>, N's ask. Hold ↑ and press J: it hovers, each ↑ is a pulse that shoots it up like a rocket, and it bursts rainbow clouds for points and glows in their colours. Its flight is Hazel's new module, <code>Jelly.step</code>, with a JS twin; the Node check, run on the laptop with the hazeljs library of 11-25, gives the same answer at 40,000 of 40,000 steps, 1.7 µs a step through the jit against 0.45 µs in JS. With it, the rules compiled in the page in 16.5 s.</p>"
    ).replace("{R65}", RL(65)),
    "meeting": "A five-minute look at both games on Matthew's screen. What would Cyrus want measured, or written up, from this corpus?",
}

A = {
    "report": 66,
    "kind": "agenda",
    "meeting": "2026-11-27",
    "meeting_time": "09:00 MST (about 9 a.m. in Boulder, Colorado)",
    "started": "2026-11-27",
    "updated": UPDATED,
    "page_title": "Agenda for November 27",
    "title": "Agenda: Matthew and Cyrus, Friday 2026-11-27, 09:00 Mountain",
    "sub": (
        f"The topics Matthew brings to his meeting with Cyrus on Friday 2026-11-27 at about 09:00 Mountain time (MST). "
        f"The last agenda was for their meeting of Friday 2026-11-13 ({RL(42)}). Since then the team met on 11-17 ({RL(54)}), Cyrus confirmed SInt's 64 bits on 11-18, and the team held a merge-a-thon on 11-19 ({RL(58)}). "
        f"<b>“Last week”</b> below is the state as of Friday 2026-11-20, just after those; <b>“this week”</b> is now, after the night of 11-26. "
        f"<b>A work in progress:</b> each item says where it stands, as of when, and what it needs from the meeting."
    ),
    "short": [
        "<b>The two PRs:</b> hazel-jit (#2859) and the package (#2857) both build on dev now; the games run at 3.8× plain JS, from 11.9×; five green trials wait.",
        "<b>The back burner:</b> 46 open PRs, 24 drafts; three merged at the merge-a-thon; SInt's 64 bits (#2828), the README (#2812) and the font and icons wait.",
        "<b>If there is time:</b> Cyrus's advice on an email from Max Carroll, which Matthew brings; and a demo of Gnome dig and Gnome world 0.0.146, with N's flying jellyfish.",
    ],
    "sections": [
        {"id": "two-prs", "title": "1. The two PRs: hazel-jit and the hazeljs package",
         "intro": "Matthew's focus, agreed with Cyrus: the npm package and hazel-jit (his words, 11-25). By his rule of 11-23, hazel-jit lives in at most two PRs, both for dev: its own, #2859, and the package's, #2857, which merges it. Each item compares last week (11-20) with now.",
         "items": [jit, npm],
         "next": [
             "On Matthew's word: trial/891-idiv into <code>hazel-jit</code> (#2859); the four package trials into <code>hazeljs</code> (#2857); then hazeljs 0.0.15.",
             "791's two commits as a small PR to dev, if agreed.",
             "#2859 out of draft, with the reviewer the meeting names."]},
        {"id": "back", "title": "2. The back burner",
         "intro": "Matthew's other open PRs on hazelgrove/hazel, the ones worth a word today.",
         "items": [backburner]},
        {"id": "if-time-items", "title": "3. If there is time",
         "intro": "Two items for the end of the meeting.",
         "items": [carroll, demo]},
    ],
    "if_time": [],
    "method": [
        f"Started 2026-11-27 from Matthew's list for the meeting, in his order. Built locally; not published until Matthew has read it.",
        "Every number names its source: a ticket on the work dashboard, a report in this series, a GitHub run, a commit, or <code>npm view</code>. PRs are hazelgrove/hazel's unless named otherwise.",
        "<b>Each item has a <i>copy item</i> chip:</b> it copies the item's number, its id (which stays when items are reordered), its title and its link.",
    ],
    "decided": [],
}
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agenda.json")
json.dump(A, open(out, "w"), ensure_ascii=False, indent=1)
print("wrote", out)
