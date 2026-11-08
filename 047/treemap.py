"""^report(47): treemaps (Matthew, 2026-11-08: "tree maps ... for showing relative space consumption ... as figures (2d,
not 1d) ... before and after the first-order representation is applied"). A squarified layout (Bruls, Huijsing and
van Wijk, 2000): each rectangle's area is its bytes; a value's parts are the outer rectangles, and each part is
split into what its bytes are."""
import html

# what a part's bytes are, the costliest first; each a difference of exact Marshal sizes (DataExperiment.split)
KINDS = [("ids", "ids and tags", "#ea580c"), ("term", "term structure", "#9ca3af"),
         ("dstruct", "data structure", "#60a5fa"), ("data", "the data itself", "#16a34a")]


def kinds_of(split, form):
    """a part's bytes by kind: as a term (all four), or as data (its structure and the data itself)"""
    t, s, d, p = split["term"], split["shared_tags"], split["data"], split["atoms"]
    p = min(p, d)
    out = {"dstruct": max(0, d - p), "data": max(0, p)}
    if form == "term":
        out["ids"] = max(0, t - s)
        out["term"] = max(0, s - d)
    return out


def squarify(items, x, y, w, h):
    """[(key, size)], largest first, laid out in the rectangle; [(key, x, y, w, h)]"""
    items = [(k, v) for k, v in items if v > 0]
    total = sum(v for _, v in items)
    out = []
    if total <= 0 or w <= 0 or h <= 0:
        return out
    rest = [(k, v * w * h / total) for k, v in items]
    while rest:
        short = min(w, h)

        def worst(row):
            s = sum(a for _, a in row)
            return max(max(short * short * a / (s * s), (s * s) / (short * short * a)) for _, a in row)

        row = [rest.pop(0)]
        while rest and worst(row + [rest[0]]) <= worst(row):
            row.append(rest.pop(0))
        s = sum(a for _, a in row)
        if w >= h:
            cw = s / h
            yy = y
            for k, a in row:
                out.append((k, x, yy, cw, a / cw))
                yy += a / cw
            x, w = x + cw, w - cw
        else:
            rh = s / w
            xx = x
            for k, a in row:
                out.append((k, xx, y, a / rh, rh))
                xx += a / rh
            y, h = y + rh, h - rh
    return out


def parts_with_rest(tree):
    """the parts, and what the whole has beyond them (the list itself) as one more"""
    parts = [(p["name"], p["split"]) for p in tree["parts"]]
    whole = tree["whole"]
    if not parts:
        return [("the whole picture", whole)]
    rest = {k: whole[k] - sum(s[k] for _, s in parts) for k in ("term", "shared_tags", "data", "atoms")}
    if any(v > 0 for v in rest.values()):
        parts.append(("(the list itself)", {k: max(0, v) for k, v in rest.items()}))
    return parts


def treemap_svg(tree, form, x0, y0, w, h, label_min=46):
    """one value as one form: its parts, each split by kind"""
    out = []
    parts = parts_with_rest(tree)
    sized = sorted(((i, sum(kinds_of(s, form).values())) for i, (_, s) in enumerate(parts)), key=lambda kv: -kv[1])
    for i, px, py, pw, ph in squarify(sized, x0, y0, w, h):
        name, split = parts[i]
        ks = kinds_of(split, form)
        inner = sorted(((k, ks.get(k, 0)) for k, _, _ in KINDS), key=lambda kv: -kv[1])
        for k, kx, ky, kw, kh in squarify(inner, px, py, pw, ph):
            colour = next(c for kk, _, c in KINDS if kk == k)
            label = next(l for kk, l, _ in KINDS if kk == k)
            out.append(f'<rect x="{kx:.2f}" y="{ky:.2f}" width="{kw:.2f}" height="{kh:.2f}" fill="{colour}">'
                       f'<title>{html.escape(name)}: {label}, {ks[k]:,} bytes</title></rect>')
        out.append(f'<rect x="{px:.2f}" y="{py:.2f}" width="{pw:.2f}" height="{ph:.2f}" fill="none" stroke="var(--paper, #fff)" '
                   f'stroke-width="1.2"><title>{html.escape(name)}: {sum(ks.values()):,} bytes</title></rect>')
        if pw >= label_min and ph >= 13:
            out.append(f'<text x="{px + 3:.1f}" y="{py + 11:.1f}" font-size="9.5" fill="#111" font-weight="700" '
                       f'style="paint-order:stroke;stroke:#fff;stroke-width:2.5px">{html.escape(name[:int(pw / 5.6)])}</text>')
    return out


def figure(tree, title, caption, W=940):
    """the value as terms and as data, side by side on one scale: each rectangle's area its bytes"""
    whole = tree["whole"]
    t_total = sum(sum(kinds_of(s, "term").values()) for _, s in parts_with_rest(tree))
    d_total = sum(sum(kinds_of(s, "data").values()) for _, s in parts_with_rest(tree))
    H = 420
    tw = 560
    scale = tw * H / t_total  # px² a byte
    side = (d_total * scale) ** 0.5
    dw = dh = side
    out = [f'<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">{html.escape(title)}</text>']
    top = 52
    out.append(f'<text x="16" y="{top - 8}" font-size="11.5" fill="var(--ink)">As Hazel terms, today: {t_total / 1000:,.1f} KB</text>')
    out += treemap_svg(tree, "term", 16, top, tw, H)
    dx = 16 + tw + 40
    out.append(f'<text x="{dx}" y="{top - 8}" font-size="11.5" fill="var(--ink)">As data: {d_total / 1000:,.1f} KB, '
               f'{t_total / d_total:.1f} times smaller</text>')
    out += treemap_svg(tree, "data", dx, top, dw, dh, label_min=60)
    ly = top + H + 18
    x = 16
    for k, label, colour in KINDS:
        out.append(f'<rect x="{x}" y="{ly - 10}" width="12" height="12" fill="{colour}"/>')
        out.append(f'<text x="{x + 16}" y="{ly}" font-size="11" fill="var(--muted)">{label}</text>')
        x += 16 + 6.2 * len(label) + 22
    h = ly + 14
    alt = (f"{title}: as terms {t_total:,} bytes, as data {d_total:,} bytes; " +
           "; ".join(f"{label}: {sum(kinds_of(s, 'term').get(k, 0) for _, s in parts_with_rest(tree)):,} bytes as terms"
                     for k, label, _ in KINDS))
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{html.escape(alt)}" '
            f'style="width:100%;height:auto;display:block">' + "".join(out) + f"</svg><figcaption>{caption}</figcaption></figure></div>")
