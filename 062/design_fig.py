"""^report(62)'s design figure: one board's node in the shared tree, its two streams (its moves, made as each is first visited; its
answers, one range a look-ahead), and the two players' searches reaching it with the same question. Imported by gen062.py."""

def design_svg():
    W, H = 600, 330
    out = []
    t = lambda x, y, s, cls="lbl", anchor="start": f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{s}</text>'
    # the board's node
    out.append('<rect class="node" x="20" y="120" width="150" height="96" rx="10"/>')
    out.append(t(95, 146, "a board", "lbl", "middle"))
    out.append(t(95, 166, "(the pieces,", "mut", "middle"))
    out.append(t(95, 182, "whose turn)", "mut", "middle"))
    out.append(t(95, 202, "the same for both", "mut", "middle"))
    # its moves stream
    out.append(t(200, 40, "its moves: worked out once, each child made when first visited", "mut"))
    for i, (label, made) in enumerate([("move 1", True), ("move 2", True), ("move 3", False), ("move 4", False)]):
        x = 200 + i * 96
        out.append(f'<rect class="{"cell" if made else "cell later"}" x="{x}" y="52" width="86" height="34" rx="6"/>')
        out.append(t(x + 43, 74, label + ("" if made else " …"), "lbl" if made else "mut", "middle"))
    out.append('<path class="link" d="M170 150 C185 110 190 80 200 70"/>')
    # its answers stream
    out.append(t(200, 250, "its answers: for each look-ahead, a range (at least, at most)", "mut"))
    for i, (d, rng, shown) in enumerate([("1", "= 12", True), ("3", "≥ 4", True), ("5", "4 … 9", True), ("7", "?", False)]):
        x = 200 + i * 96
        out.append(f'<rect class="{"cell" if shown else "cell later"}" x="{x}" y="262" width="86" height="40" rx="6"/>')
        out.append(t(x + 43, 279, f"{d} ahead", "mut", "middle"))
        out.append(t(x + 43, 296, rng, "lbl" if shown else "mut", "middle"))
    out.append('<path class="link" d="M170 190 C185 230 190 260 200 275"/>')
    # the question, answered by the partial order
    out.append(t(200, 150, "a question: “5 ahead: is it more than 3?”", "lbl"))
    out.append(t(200, 170, "answered by any entry that settles it: “4 … 9” does,", "mut"))
    out.append(t(200, 188, "whichever player's search left it there", "mut"))
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="A board in the shared tree: its moves, made as they are first visited, and its '
            f'answers, a range for each look-ahead; a question answered by any entry that settles it">' + "".join(out) + "</svg>")
