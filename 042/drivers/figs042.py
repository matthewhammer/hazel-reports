"""^report(42)'s figures, drawn at the top of each item's card by gen042.py (FIGS[item id] = [(html, caption, wide)]).
Two are ^report(37)'s, reused as drawn there (037/drivers/figs037.py); the rest are new and use its helpers.
Inline SVG in the series' colours (CSS variables, so both themes); every number is from the source in its caption."""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "037", "drivers"))
import figs037 as F  # noqa: E402
from figs037 import svg, text, box, arrow  # noqa: E402


def fig_space_per_entry():
    # ^ticket(665), 2026-11-03 11:42: test/Test_UndoSpace.re on trial/665-space, GitHub run 41695584813, dev build, one run:
    # the live heap each undo entry adds, from the 10th entry to the 100th
    sizes = ((400, 0.011, 0.55), (1600, 0.009, 1.9), (6400, 0.0, 6.9))
    W, H, L, R, T = 460, 200, 110, 56, 30
    X = lambda v: L + v / 7.5 * (W - L - R)
    o = [text(8, 14, "MB of heap each undo entry adds, by program size", 11.5, "start", "var(--muted)")]
    for v in (0, 2, 4, 6):
        o.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{H - 26}" stroke="var(--line)"/>')
        o.append(text(X(v), H - 12, str(v), 11, "middle", "var(--muted)"))
    for i, (n, comp, whole) in enumerate(sizes):
        y = T + 4 + i * 50
        o.append(text(L - 10, y + 18, f"{n:,} defs", 12.5, "end", "var(--ink)"))
        o.append(f'<rect x="{L}" y="{y}" width="{max(2, X(whole) - L):.1f}" height="16" rx="3" fill="var(--warn)">'
                 f'<title>{n:,} definitions, an entry kept whole: {whole} MB</title></rect>')
        o.append(text(X(whole) + 6, y + 13, f"{whole} whole", 12, "start", "var(--ink)", 700))
        o.append(f'<rect x="{L}" y="{y + 20}" width="2.5" height="16" rx="1" fill="var(--good)">'
                 f'<title>{n:,} definitions, compacted: about {comp} MB</title></rect>')
        o.append(text(L + 8, y + 33, f"about {comp or 0} compacted" if comp else "about 0 compacted", 12, "start", "var(--good)", 700))
    return svg(W, H, "Heap per undo entry: about 0.01 MB compacted at every size; kept whole 0.55, 1.9 and 6.9 MB at 400, 1,600 and 6,400 definitions", o)


def fig_where_linear():
    # ^ticket(665), 2026-11-02: profile at 3,200 definitions after the two cheap fixes (394552d5d0, bfa36a6ede)
    rows = (("MakeTerm's top-level pass", 38, "record_top_frame, the items' spans"),
            ("DefStatics' chain walk", 20, "step_chain, calc_chain"),
            ("the outline, rebuilt", 15, "on an undo or redo (#2469's sidebar)"),
            ("Measured's walk", 6, "positions of the top level"),
            ("everything else", 21, "the edited definition itself, GC, ..."))
    W, H, L, R, T = 460, 214, 190, 50, 28
    X = lambda v: L + v / 40 * (W - L - R)
    o = [text(8, 14, "Where an edit, undo and redo spend their time (% of the profile)", 11.5, "start", "var(--muted)")]
    for i, (lab, pct, sub) in enumerate(rows):
        y = T + i * 36
        col = "var(--muted)" if i == 4 else "var(--accent)"
        o.append(text(L - 10, y + 12, lab, 12.5, "end", "var(--ink)"))
        o.append(text(L - 10, y + 26, sub, 10.5, "end", "var(--muted)"))
        o.append(f'<rect x="{L}" y="{y + 2}" width="{X(pct) - L:.1f}" height="18" rx="3" fill="{col}"><title>{lab}: {pct}%</title></rect>')
        o.append(text(X(pct) + 6, y + 16, f"{pct}%", 12.5, "start", "var(--ink)", 700))
    return svg(W, H, "Profile at 3,200 definitions: MakeTerm's top-level pass 38%, DefStatics' chain walk 20%, the outline 15%, Measured 6%, the rest 21%", o)


def fig_jit():
    # ^ticket(694)'s design (2026-11-05 12:27), with Matthew's name for the component (2026-11-06): hazel-jit
    W, H = 940, 236
    o = [text(16, 18, "A livelit's view, today and with hazel-jit", 12.5, "start", "var(--ink)", 700)]
    o.append(box(16, 92, 150, 64, ["view(model)", "a Hazel function", "on the slide"], stroke="var(--accent)"))
    # today
    o.append(text(200, 44, "today", 11.5, "start", "var(--muted)", 700))
    o.append(box(200, 52, 230, 56, ["the interpreter", "step by step, CallMemo shared"], stroke="var(--line)"))
    # hazel-jit
    o.append(text(200, 146, "with hazel-jit (jit_views on)", 11.5, "start", "var(--accent2)", 700))
    o.append(box(200, 154, 230, 56, ["hazel-jit compiles once", "elaborated term to JS source"], stroke="var(--accent2)"))
    o.append(box(450, 154, 170, 56, ["a JS function", "new Function(...)"], stroke="var(--accent2)"))
    o.append(arrow(166, 112, 196, 82)); o.append(arrow(166, 136, 196, 180, "var(--accent2)"))
    o.append(arrow(430, 182, 446, 182, "var(--accent2)"))
    # both end in the same command tree
    o.append(box(660, 100, 130, 60, ["a ViewCmd", "a Hazel value"], stroke="var(--line)"))
    o.append(box(810, 100, 116, 60, ["Html", "drawn as today"], stroke="var(--line)"))
    o.append(arrow(430, 80, 656, 118)); o.append(arrow(620, 182, 656, 144, "var(--accent2)"))
    o.append(arrow(790, 130, 806, 130))
    o.append(text(16, 228, "Not compiled: update, init, expand and the program; a view with holes, tests or projectors stays on the interpreter, and says why.", 11.5, "start", "var(--muted)"))
    return svg(W, H, "A livelit's view runs on the interpreter today; with hazel-jit it is compiled once to a JS function, and both give the same ViewCmd, drawn as Html", o)


def fig_js_app():
    # the pattern ^report(39) describes, drawn for a JS developer's own program (^ticket(697))
    W, H = 940, 200
    o = [text(16, 18, "Your app, with some of its handlers in Hazel (hazeljs)", 12.5, "start", "var(--ink)", 700)]
    o.append(box(16, 44, 180, 92, ["your JS app", "keeps the state,", "draws, takes input"], stroke="var(--accent2)"))
    o.append(box(300, 30, 210, 56, ["a view of the state", "a typed Hazel record"], stroke="var(--line)"))
    o.append(box(300, 96, 210, 56, ["the event", "a Hazel constructor"], stroke="var(--line)"))
    o.append(box(600, 44, 160, 92, ["on_event", "a Hazel function,", "type-checked as typed"], stroke="var(--accent)"))
    o.append(box(796, 44, 130, 92, ["a command", "data your app", "acts out"], stroke="var(--line)"))
    o.append(arrow(196, 70, 296, 58)); o.append(arrow(196, 110, 296, 124))
    o.append(arrow(510, 58, 596, 78)); o.append(arrow(510, 124, 596, 104))
    o.append(arrow(760, 90, 792, 90))
    o.append(f'<path d="M861 136 C 861 186, 106 186, 106 140" fill="none" stroke="var(--muted)" stroke-width="1.6" stroke-dasharray="5 4"/>')
    o.append(text(480, 194, "the app performs the command; while the Hazel program is unfinished or has errors, your own JS handler answers instead", 11.5, "middle", "var(--muted)"))
    return svg(W, H, "Your JS app hands a typed view of its state and an event to a Hazel function, and acts out the command it returns", o)


def kept(nnn, name):
    """(Matthew, 2026-11-07: the agenda "should have plots in the report once we have them elsewhere") a figure as its
    report drew it, kept by that report's generator as NNN/figs/NAME.html (its <svg>, in the series' colour variables)"""
    return open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", nnn, "figs", name + ".html")).read().strip()


FIGS = {
    "undo": [(fig_where_linear(), "Time: what is linear is a few passes over every top-level definition, not the undo history. Profile at 3,200 definitions after the first two fixes (^ticket(665), 2026-11-02).", False),
             (fig_space_per_entry(), "Space: a compacted entry costs about nothing at every size; the entry kept whole for a fast undo grows with the program, about 1.1 KB a definition (GitHub run 41695584813, one run).", False),
             (F.fig_undo_growth(), "Each step against program size, both scales logarithmic: parallel to the dotted guide means in proportion to the program. Release build, medians of 12 (^report(36)).", False),
             (F.fig_undo_fix(), "The third fix (9df1b2601e, on #2635): a redo now costs an edit; an undo, an edit and the outline (^report(38)).", False)],
    "hazel-jit": [(kept("045", "speed"), "Each program's time per run, the interpreter against compiled, a log scale: medians of 30, Node 22, a dev build (^report(45)).", True),
                  (kept("046", "witch-firefox"), "The Witch slide's views in Firefox, in the app, against a 60 fps frame: the picture not compiled yet, the polygon editors compiled; fps as if updating the state were free (^report(46)).", True),
                  (kept("046", "witch-frame"), "One frame of the Witch slide's picture in the Hazel test, the picture handed over already evaluated, against a 60 fps frame; fps as if updating the state were free (^report(46)).", True),
                  (kept("045", "routes"), "A Polygons render from the model to the page's virtual DOM: through Hazel, or straight from the compiled view's JS answer, to scale (^report(45)).", True)],
    "bucklescript": [(kept("046", "witch"), "The Witch slide's picture view, compiled five ways: the view's own work in one Node process, and the time toFixed alone takes, dashed (^report(46)).", True),
                     (kept("046", "speed-log"), "Report 043's Petri rule, one call, compiled five ways and on the interpreter, a log scale: medians of five runs of 2,000 calls, Node 22 (^report(46)).", True)],
    "readme-pr": [(F.fig_npm(), "hazeljs on npm, as of 2026-11-03: four versions, 0.0.4 the latest (npmjs.com/package/hazeljs). ^report(37)'s figure.", True)],
    "js-dev-report": [(fig_js_app(), "The pattern the report would teach, the one Messed Up Dress Up's rooms use (^report(39)).", True)],
}
