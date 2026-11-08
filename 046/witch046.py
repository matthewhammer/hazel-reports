"""^report(46)'s second program: the Witch slide's ^picture view, compiled by hazel-jit, ReScript, Melange and
js_of_ocaml, and written by hand (Matthew, 2026-11-07: "measure the most complex view function of our livelits slide
deck ... and compare"). gen046.py imports this: the numbers ({{w:NAME}}), the figures, the drawings, and one page per
compiler's output in 046/witch/ ("separate into distinct pages, one per output"). Every number is from
046/data/witch/timings.json; a view's time is given with its frames a second in parens, as if updating the state were
free, against 60 fps, a 16.7 ms frame, as the floor (Matthew, 2026-11-07)."""
import html, json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
DW = lambda name: open(os.path.join(HERE, "data", "witch", name)).read()
WT = json.loads(DW("timings.json"))
NODE = WT["node_medians_ms"]
APP = WT["app"]
FRAME_60 = 1000 / 60


def fps(ms):
    """frames a second, to two figures: a timing's third figure is noise"""
    f = 1000 / ms
    if f >= 1000:
        return f"{round(f, -2):,.0f}"
    return f"{round(f, -1):,.0f}" if f >= 100 else f"{f:.0f}"


def ms(x):
    return f"{x:.2f}" if x < 10 else f"{x:.0f}"


# the rows of the view's own work, one Node process: name, ms, colour
ROWS = [("hand-written JS", NODE["hand-written JS"], "var(--muted)"),
        ("Melange", NODE["Melange"], "var(--accent)"),
        ("ReScript", NODE["ReScript"], "var(--accent)"),
        ("js_of_ocaml, toFixed", WT["jsoo_tofixed_ms"], "var(--accent2)"),
        ("hazel-jit", NODE["hazel-jit"], "var(--accent2)"),
        ("js_of_ocaml, Printf", WT["jsoo_printf_ms"], "var(--warn, #b45309)")]

WNUMS = {
    "hj": f"{NODE['hazel-jit']:.2f}", "res": f"{NODE['ReScript']:.2f}", "mel": f"{NODE['Melange']:.2f}",
    "hand": f"{NODE['hand-written JS']:.2f}", "jsoo_tf": f"{WT['jsoo_tofixed_ms']:.2f}", "jsoo_pf": f"{WT['jsoo_printf_ms']:.2f}",
    "hj_fps": fps(NODE["hazel-jit"]), "res_fps": fps(NODE["ReScript"]), "mel_fps": fps(NODE["Melange"]),
    "hand_fps": fps(NODE["hand-written JS"]), "jsoo_tf_fps": fps(WT["jsoo_tofixed_ms"]), "jsoo_pf_fps": fps(WT["jsoo_printf_ms"]),
    "hj_x_hand": f"{(NODE['hazel-jit'] / NODE['hand-written JS'] - 1) * 100:.0f}",
    "hj_x_res": f"{(NODE['hazel-jit'] / NODE['ReScript'] - 1) * 100:.0f}",
    "pf_x_tf": f"{WT['jsoo_printf_ms'] / WT['jsoo_tofixed_ms']:.1f}",
    "tofixed": f"{WT['toFixed_alone_ms']:.2f}", "tofixed_calls": f"{WT['toFixed_calls']:,}",
    "tofixed_share": f"{WT['toFixed_alone_ms'] / NODE['hand-written JS'] * 100:.0f}",
    "interp": ms(APP["interpreter_view_ms"]), "interp_fps": fps(APP["interpreter_view_ms"]),
    "interp_eval": f"{APP['interpreter_eval_ms']:.1f}",
    "frame": f"{APP['frame_ms']:.1f}", "frame_fps": fps(APP["frame_ms"]),
    "app_view": f"{APP['view_work_ms']:.2f}", "app_view_fps": fps(APP["view_work_ms"]),
    "trip_in": f"{APP['trip_in_ms']:.2f}", "direct": f"{APP['direct_draw_ms']:.2f}", "draw_only": f"{APP['draw_only_ms']:.2f}",
    "interp_x_frame": f"{APP['interpreter_view_ms'] / APP['frame_ms']:.0f}",
    "interp_x_app_view": f"{APP['interpreter_view_ms'] / APP['view_work_ms']:.0f}",
    "frames_late": f"{APP['interpreter_view_ms'] / FRAME_60:.0f}",
    "frame_left": f"{FRAME_60 - APP['frame_ms']:.0f}",
    "compile": f"{APP['compile_ms']:.1f}",
    "app_over_node": f"{APP['view_work_ms'] / NODE['hazel-jit']:.0f}",
    "shapes": "133", "points": "924", "svg_chars": f"{WT['picture']['svg_chars']:,}",
}


def fig_witch():
    """the view's own work, each compiler, one Node process, to scale; the time toFixed alone takes, dashed"""
    W, left, right = 940, 190, 210
    hi = 1.1
    xof = lambda v: left + v / hi * (W - left - right)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">The Witch\'s picture: the view\'s own work, ms '
           '(and frames a second, as if updating the state were free)</text>']
    y = 34
    for name, v, colour in ROWS:
        out.append(f'<text x="{left - 10}" y="{y + 15}" font-size="12" text-anchor="end" fill="var(--ink)" font-weight="700">{html.escape(name)}</text>')
        out.append(f'<rect x="{left}" y="{y + 3}" width="{xof(v) - left:.1f}" height="16" rx="3" fill="{colour}" opacity="0.85"><title>{html.escape(name)}: {v:.3f} ms</title></rect>')
        out.append(f'<text x="{xof(v) + 8:.1f}" y="{y + 15}" font-size="11.5" fill="var(--ink)" font-weight="700">{v:.2f} ms ({fps(v)} fps)</text>')
        y += 28
    tf = xof(WT["toFixed_alone_ms"])
    out.append(f'<line x1="{tf:.1f}" y1="30" x2="{tf:.1f}" y2="{y + 2}" stroke="var(--ink)" stroke-width="1.4" stroke-dasharray="4 3"/>')
    out.append(f'<text x="{tf + 4:.1f}" y="{y + 14}" font-size="11" fill="var(--ink)">toFixed alone, {WT["toFixed_calls"]:,} calls: {WT["toFixed_alone_ms"]:.2f} ms</text>')
    for t in (0, 0.25, 0.5, 0.75, 1.0):
        out.append(f'<text x="{xof(t):.1f}" y="{y + 32}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{t:g}</text>')
    h = y + 42
    alt = "; ".join(f"{n} {v:.2f} ms ({fps(v)} fps)" for n, v, _ in ROWS) + f"; toFixed alone {WT['toFixed_alone_ms']:.2f} ms"
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{alt}" style="width:100%;height:auto;display:block">'
            + "".join(out) + "</svg><figcaption>Node 22.23.2, one laptop: from the picture, as each language holds it, to the Html the view "
            "returns, as each holds it. Each bar the median of three runs, each run the median of five rounds of 200 calls; "
            "js_of_ocaml's in a process of its own, five runs. The dashed line is the same 1,985 numbers formatted with "
            "<code>toFixed(1)</code> and nothing else.</figcaption></figure></div>")


def fig_witch_frame():
    """(Matthew, 2026-11-07: 60 fps "as the 'min floor' we want to achieve") one frame of the Witch's picture in the app's
    terms, on a log scale, against a 60 fps frame"""
    rows = [("the interpreter", "its view, command and drawing", APP["interpreter_view_ms"], "var(--warn, #b45309)"),
            ("hazel-jit, the app", "model in, view, drawing", APP["frame_ms"], "var(--accent2)"),
            ("hazel-jit's view", "in the app's process", APP["view_work_ms"], "var(--accent2)"),
            ("hazel-jit's view", "in a Node process alone", NODE["hazel-jit"], "var(--accent)")]
    W, left, right = 940, 200, 150
    lo, hi = math.log10(0.1), math.log10(300)
    xof = lambda v: left + (math.log10(v) - lo) / (hi - lo) * (W - left - right)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">One frame of the Witch\'s picture, ms on a log scale, '
           'against a 60 fps frame (16.7 ms)</text>']
    top, step = 34, 34
    bottom = top + len(rows) * step
    for t in (0.1, 1, 10, 100):
        x = xof(t)
        out.append(f'<line x1="{x:.1f}" y1="28" x2="{x:.1f}" y2="{bottom:.0f}" stroke="var(--line)" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{bottom + 14}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{t:g} ms</text>')
    x60 = xof(FRAME_60)
    out.append(f'<rect x="{left}" y="28" width="{x60 - left:.1f}" height="{bottom - 28:.0f}" fill="var(--good, #2e7d32)" opacity="0.07"/>')
    out.append(f'<line x1="{x60:.1f}" y1="26" x2="{x60:.1f}" y2="{bottom + 2:.0f}" stroke="var(--good, #2e7d32)" stroke-width="2"/>')
    out.append(f'<text x="{x60 + 5:.1f}" y="{bottom + 14}" font-size="11" fill="var(--good, #2e7d32)" font-weight="700">60 fps, 16.7 ms</text>')
    y = top
    for name, sub, v, colour in rows:
        out.append(f'<text x="{left - 10}" y="{y + 11}" font-size="12" text-anchor="end" fill="var(--ink)" font-weight="700">{html.escape(name)}</text>')
        out.append(f'<text x="{left - 10}" y="{y + 24}" font-size="10.5" text-anchor="end" fill="var(--muted)">{html.escape(sub)}</text>')
        out.append(f'<rect x="{left}" y="{y + 4}" width="{xof(v) - left:.1f}" height="16" rx="3" fill="{colour}" opacity="0.85"><title>{name}, {sub}: {v:.2f} ms</title></rect>')
        out.append(f'<text x="{xof(v) + 8:.1f}" y="{y + 16}" font-size="11.5" fill="var(--ink)" font-weight="700">{ms(v)} ms ({fps(v)} fps)</text>')
        y += step
    h = bottom + 24
    alt = "Against a 60 fps frame of 16.7 ms: " + "; ".join(f"{n}, {s}, {ms(v)} ms ({fps(v)} fps)" for n, s, v, _ in rows)
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{alt}" style="width:100%;height:auto;display:block">'
            + "".join(out) + "</svg><figcaption>The first three in the Hazel test's process (<code>Test_HazelJit</code>'s "
            "<code>witch_view_run</code>, a dev build, Node; two runs of 15, pooled medians), the last in the benchmark's own process. "
            "Shaded: inside one frame at 60 fps. The frames a second are each time alone, as if updating the state were free.</figcaption></figure></div>")


# (Matthew, 2026-11-07: "Yes, in Firefox") the slide's views timed again in the page, in Firefox on GitHub's machines
FF = json.loads(DW("firefox.json"))
# (the same check before cb560ebb86: the picture's definition given up by a refusal before the program's run)
FFB = json.loads(DW("firefox-before.json"))
FFB_PIC = next(v for k, v in FFB["views"].items() if k.startswith("Drawing.picture") and "before the run" not in k)
FFV = {k: v for k, v in FF["views"].items() if "before the run" not in k}
FF_PIC = next(v for k, v in FFV.items() if k.startswith("Drawing.picture"))
FF_POLY = [v for k, v in FFV.items() if k.startswith("Drawing.polygons")]
_pc = sorted(v["compiled"]["median"] for v in FF_POLY)
_pi = sorted(v["interpreted"]["median"] for v in FF_POLY)
_px = sorted(v["interpreted"]["median"] / v["compiled"]["median"] for v in FF_POLY)
WNUMS.update({
    "ff_pic": f"{FF_PIC['interpreted']['median']:.0f}", "ff_pic_fps": fps(FF_PIC["interpreted"]["median"]),
    "ff_pic_app": f"{FF_PIC['compiled']['median']:.1f}", "ff_pic_app_fps": fps(FF_PIC["compiled"]["median"]),
    "ff_pic_view": f"{FF_PIC['view_only']['median']:.1f}", "ff_pic_view_fps": fps(FF_PIC["view_only"]["median"]),
    "ff_pic_x": f"{FF_PIC['interpreted']['median'] / FF_PIC['compiled']['median']:.0f}",
    "ff_pic_late": f"{FF_PIC['interpreted']['median'] / FRAME_60:.0f}",
    "ff_pic_left": f"{FRAME_60 - FF_PIC['compiled']['median']:.0f}",
    "ffb_pic": f"{FFB_PIC['compiled']['median']:.0f}", "ffb_pic_fps": fps(FFB_PIC["compiled"]["median"]),
    "ffb_run": str(FFB["run"]), "ffb_sha": FFB["sha"],
    "ff_poly_lo": f"{_pc[0]:.2f}", "ff_poly_hi": f"{_pc[-1]:.2f}", "ff_poly_fps_lo": fps(_pc[-1]), "ff_poly_fps_hi": fps(_pc[0]),
    "ff_polyi_lo": f"{_pi[0]:.0f}", "ff_polyi_hi": f"{_pi[-1]:.0f}", "ff_polyi_fps_lo": fps(_pi[-1]), "ff_polyi_fps_hi": fps(_pi[0]),
    "ff_polyx_lo": f"{_px[0]:.0f}", "ff_polyx_hi": f"{_px[-1]:.0f}", "ff_run": str(FF["run"]), "ff_sha": FF["sha"],
})


# (Matthew, 2026-11-07: "we should measure the cost of a small edit") one slider step on the Witch slide, in Firefox,
# both ways; and, in Node, what report 45's sharing would save on the picture's view after such an edit
FE = json.loads(DW("firefox-edit.json"))
SH = json.loads(DW("edit-share.json"))
SHK = {r["k"]: r for r in SH["rows"]}


def upper_middle(xs):
    s = sorted(xs)
    return s[len(s) // 2]


_eon = [e["picture_changed_ms"] for e in FE["edits"]["on"]]
_eoff = [e["picture_changed_ms"] for e in FE["edits"]["off"]]
_eall = _eon + _eoff
_own = [e["own_first_ms"] for m in ("on", "off") for e in FE["edits"][m]]
_runend = [e["dynamics"][-1][0] for m in ("on", "off") for e in FE["edits"][m]]
_changed = {e["label"]: e["shapes_changed"] for e in FE["edits"]["on"]}
E_PIC = upper_middle(_eon)
WNUMS.update({
    "e_pic_lo": f"{min(_eall) / 1000:.1f}", "e_pic_hi": f"{max(_eall) / 1000:.1f}",
    "e_pic_on": f"{E_PIC / 1000:.1f}", "e_pic_off": f"{upper_middle(_eoff) / 1000:.1f}",
    "e_pic_on_lo": f"{min(_eon) / 1000:.1f}", "e_pic_on_hi": f"{max(_eon) / 1000:.1f}",
    "e_pic_off_lo": f"{min(_eoff) / 1000:.1f}", "e_pic_off_hi": f"{max(_eoff) / 1000:.1f}",
    "e_pic_frames": f"{E_PIC / FRAME_60:,.0f}",
    "e_own_lo": f"{min(_own) / 1000:.2f}", "e_own_hi": f"{max(_own) / 1000:.2f}",
    "e_own_frames_lo": f"{min(_own) / FRAME_60:.0f}", "e_own_frames_hi": f"{max(_own) / FRAME_60:.0f}",
    "e_run_lo": f"{min(_runend) / 1000:.1f}", "e_run_hi": f"{max(_runend) / 1000:.1f}",
    "e_neck": str(_changed["neck"]), "e_arms": str(_changed["arms (up / down)"]), "e_shapes": str(FE["edits"]["on"][0]["shapes"]),
    "e_view_share": f"{FF_PIC['compiled']['median'] / E_PIC * 100:.2f}",
    "e_interp_share": f"{FF_PIC['interpreted']['median'] / E_PIC * 100:.1f}",
    "e_run_id": str(FE["run"]), "e_sha": FE["sha"],
    "sh_today": f"{SHK[1]['today_view_ms']:.2f}", "sh_share": f"{SHK[1]['share_ms']:.2f}",
    "sh_kept1": f"{SHK[1]['kept_view_ms']:.3f}", "sh_kept17": f"{SHK[17]['kept_view_ms']:.3f}", "sh_kept30": f"{SHK[30]['kept_view_ms']:.3f}",
    "sh_x1": f"{SHK[1]['today_view_ms'] / SHK[1]['kept_view_ms']:.0f}",
    "sh_x17": f"{SHK[17]['today_view_ms'] / SHK[17]['kept_view_ms']:.0f}",
    "sh_x30": f"{SHK[30]['today_view_ms'] / SHK[30]['kept_view_ms']:.0f}",
    "sh_js_in": f"{SHK[1]['js_trip_in_ms']:.2f}", "sh_jsoo_x": f"{APP['trip_in_ms'] / SHK[1]['js_trip_in_ms']:.0f}",
    "sh_runs": f"{SH['runs']:,}", "sh_visits": f"{SHK[1]['share_visits']:,}",
    "e_saved": f"{FF_PIC['interpreted']['median'] - FF_PIC['compiled']['median']:.0f}",
})
# (the page's counts are since its load: each edit's own, from the second on, as the difference from the one before)
_cnt = [e["jit"] for e in FE["edits"]["on"]]
_draws = [b["drawn from JS"] - a["drawn from JS"] for a, b in zip(_cnt, _cnt[1:])]
_calls = sorted({b["view compiled"] - a["view compiled"] for a, b in zip(_cnt, _cnt[1:])})
WNUMS.update({"e_draws_lo": str(min(_draws)), "e_draws_hi": str(max(_draws)),
              "e_calls": " or ".join(map(str, _calls))})


def table_share():
    """the sharing prototype's rows: k shapes changed, the whole view, the merge, the kept view"""
    rows = []
    for k in (1, 5, 17, 30, 60):
        r = SHK[k]
        rows.append(f"<tr><td>{k}</td><td>{r['today_view_ms']:.3f}</td><td>{r['share_ms']:.3f}</td><td>{r['kept_view_ms']:.3f}</td>"
                    f"<td>{r['today_view_ms'] / r['kept_view_ms']:.0f}</td><td>{'yes' if r['same_markup'] else 'NO'}</td></tr>")
    return ('<table class="vals"><tr><th>shapes changed, of ' + str(SH["shapes"]) + '</th><th>the whole view, ms (today)</th>'
            '<th>the merge with the last picture, ms</th><th>the kept view on the merged picture, ms</th>'
            '<th>the whole view over the kept one, times</th><th>the same markup</th></tr>' + "".join(rows) + "</table>")


# (Matthew, 2026-11-07: "Yes, break it down") the same edits with the page's own timeline on (Util.BenchMarks)
FT = json.loads(DW("firefox-timeline.json"))
_TOPK = {"update", "calculate", "view", "after display", "worker message decoded", "worker message handled"}


def edit_parts(e, mode):
    """one edit's split: the main thread before its request, the worker until the message that carried the picture,
    that message decoded, and the page's work after it"""
    ms, pic = e["marks"], e["picture_changed_ms"]
    post = next(m for m in ms if m["what"] == "post to worker")
    big = [m for m in ms if m["what"] == "worker message decoded" and m.get("bytes", 0) > 1e6]
    carry = max((m for m in big if m["at"] < pic), key=lambda m: m["at"])
    res_dec = max(big, key=lambda m: m["at"])
    result = next(m for m in ms if m.get("kind") == "result")
    views = [m["ms"] for m in ms if m["what"] == "view" and m["at"] <= pic]
    return {"label": e["label"], "from": e["from"], "to": e["to"], "mode": mode, "post": post["at"], "req": post["bytes"],
            "worker": carry["at"] - post["at"], "carry_bytes": carry["bytes"], "carry_is_result": carry is res_dec,
            "decode": carry["ms"], "eval": result["eval_ms"], "pic": pic, "own": e["own_first_ms"],
            "busy": sum(m["ms"] for m in ms if m["what"] in _TOPK and m["at"] <= pic), "views": views,
            "res_bytes": res_dec["bytes"], "res_decode": res_dec["ms"], "res_at": res_dec["at"],
            "after": pic - (carry["at"] + carry["ms"]), "marks": ms}


TL = [edit_parts(e, m) for m in ("on", "off") for e in FT["edits"][m]]
_neck = [r for r in TL if r["carry_is_result"]]
_allviews = [v for r in TL for v in r["views"]]
WNUMS.update({
    "tl_run": str(FT["run"]), "tl_sha": FT["sha"],
    "tl_pic_lo": f"{min(r['pic'] for r in TL) / 1000:.1f}", "tl_pic_hi": f"{max(r['pic'] for r in TL) / 1000:.1f}",
    "tl_post_lo": f"{min(r['post'] for r in TL) / 1000:.2f}", "tl_post_hi": f"{max(r['post'] for r in TL) / 1000:.2f}",
    "tl_req": f"{upper_middle([r['req'] for r in TL]) / 1000:.0f}",
    "tl_ans_lo": f"{min(r['carry_bytes'] for r in TL) / 1e6:.1f}", "tl_ans_hi": f"{max(r['res_bytes'] for r in TL) / 1e6:.1f}",
    "tl_ratio": f"{max(r['res_bytes'] for r in TL) / upper_middle([r['req'] for r in TL]):,.0f}",
    "tl_eval_lo": f"{min(r['eval'] for r in TL) / 1000:.1f}", "tl_eval_hi": f"{max(r['eval'] for r in TL) / 1000:.1f}",
    "tl_wout_lo": f"{min(r['worker'] - r['eval'] for r in _neck) / 1000:.1f}",
    "tl_wout_hi": f"{max(r['worker'] - r['eval'] for r in _neck) / 1000:.1f}",
    "tl_wneck_lo": f"{min(r['worker'] for r in _neck) / 1000:.1f}", "tl_wneck_hi": f"{max(r['worker'] for r in _neck) / 1000:.1f}",
    "tl_dres_lo": f"{min(r['res_decode'] for r in TL) / 1000:.1f}", "tl_dres_hi": f"{max(r['res_decode'] for r in TL) / 1000:.1f}",
    "tl_dstr_lo": f"{min(r['decode'] for r in TL if not r['carry_is_result']) / 1000:.1f}",
    "tl_dstr_hi": f"{max(r['decode'] for r in TL if not r['carry_is_result']) / 1000:.1f}",
    "tl_dres_frames": f"{min(r['res_decode'] for r in TL) / FRAME_60:.0f}",
    "tl_busy_lo": f"{min(r['busy'] for r in TL) / 1000:.1f}", "tl_busy_hi": f"{max(r['busy'] for r in TL) / 1000:.1f}",
    "tl_view_lo": f"{min(_allviews):.0f}", "tl_view_hi": f"{max(_allviews):.0f}",
    "tl_view_med": f"{upper_middle(_allviews):.0f}",
    "tl_views_lo": f"{min(sum(r['views']) for r in TL) / 1000:.1f}", "tl_views_hi": f"{max(sum(r['views']) for r in TL) / 1000:.1f}",
    "tl_after_lo": f"{min(r['after'] for r in TL) / 1000:.2f}", "tl_after_hi": f"{max(r['after'] for r in TL) / 1000:.2f}",
})
# (Matthew, 2026-11-08: the view's ms are a small part of an edit's seconds) both runs of the small edits together
_both = _eall + [r["pic"] for r in TL]
WNUMS.update({
    "both_pic_lo": f"{min(_both) / 1000:.1f}", "both_pic_hi": f"{max(_both) / 1000:.1f}",
    "both_frames_lo": f"{min(_both) / FRAME_60:,.0f}", "both_frames_hi": f"{max(_both) / FRAME_60:,.0f}",
})


def table_timeline():
    """every edit's split, in seconds from the edit"""
    rows = []
    for r in TL:
        rows.append(
            f"<tr><td>{html.escape(r['label'])} {r['from']} to {r['to']}</td><td>{r['mode']}</td><td>{r['post'] / 1000:.2f}</td>"
            f"<td>{r['worker'] / 1000:.1f}</td><td>{r['eval'] / 1000:.1f}</td>"
            f"<td>{'the result' if r['carry_is_result'] else 'a stream'}, {r['carry_bytes'] / 1e6:.1f} MB</td>"
            f"<td>{r['decode'] / 1000:.1f}</td><td>{r['after'] / 1000:.2f}</td><td><b>{r['pic'] / 1000:.1f}</b></td>"
            f"<td>{r['busy'] / 1000:.1f}</td></tr>")
    return ('<table class="vals"><tr><th>the edit</th><th>compiled views</th><th>its request posted, s</th>'
            '<th>the worker, from the request to the message that carries the picture, s</th><th>of which its evaluator (the whole run), s</th>'
            '<th>that message</th><th>decoding it on the main thread, s</th><th>then the page, to the picture, s</th>'
            '<th>the picture shows the edit, s</th><th>the main thread busy until then, s</th></tr>' + "".join(rows) + "</table>")


def fig_witch_edit_timeline():
    """two edits on a time line, two lanes each: what the main thread did (the page's own work, and decoding the
    worker's messages), and the worker from the request to the picture's message"""
    picks = [r for r in TL if r["mode"] == "on" and r["from"] in ("28", "55")]
    W, left, right = 940, 150, 20
    span = 11000
    xof = lambda t: left + t / span * (W - left - right)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">Two small edits on the Witch slide, in Firefox: '
           'where the time goes, seconds from the edit</text>']
    y = 40
    for r in picks:
        out.append(f'<text x="16" y="{y + 4}" font-size="12" font-weight="700" fill="var(--ink)">{html.escape(r["label"])}, {r["from"]} to {r["to"]}</text>')
        y += 12
        # the main thread
        out.append(f'<text x="{left - 10}" y="{y + 13}" font-size="11" text-anchor="end" fill="var(--muted)">main thread</text>')
        out.append(f'<rect x="{left}" y="{y + 2}" width="{W - left - right}" height="16" fill="var(--line)" opacity="0.35"/>')
        for m in r["marks"]:
            if m["what"] not in _TOPK or m.get("ms", 0) < 2 or m["at"] > span:
                continue
            dec = m["what"] == "worker message decoded"
            colour = "var(--warn, #b45309)" if dec else "var(--accent)"
            out.append(f'<rect x="{xof(m["at"]):.1f}" y="{y + 2}" width="{max(1.2, xof(m["at"] + m["ms"]) - xof(m["at"])):.1f}" height="16" '
                       f'fill="{colour}" opacity="0.9"><title>{html.escape(m["what"])}: {m["ms"]:.0f} ms at {m["at"] / 1000:.2f} s'
                       f'{", " + format(m["bytes"] / 1e6, ".1f") + " MB" if dec and m.get("bytes", 0) > 1e5 else ""}</title></rect>')
            if dec and m.get("bytes", 0) > 1e6:
                out.append(f'<text x="{(xof(m["at"]) + xof(m["at"] + m["ms"])) / 2:.1f}" y="{y + 14}" font-size="10.5" text-anchor="middle" '
                           f'fill="#fff" font-weight="700">decode {m["bytes"] / 1e6:.1f} MB, {m["ms"] / 1000:.1f} s</text>')
        y += 22
        # the worker
        out.append(f'<text x="{left - 10}" y="{y + 13}" font-size="11" text-anchor="end" fill="var(--muted)">worker</text>')
        end = r["res_at"]
        out.append(f'<rect x="{xof(r["post"]):.1f}" y="{y + 2}" width="{xof(end) - xof(r["post"]):.1f}" height="16" fill="var(--muted)" opacity="0.55">'
                   f'<title>the worker, from the request to its result: {(end - r["post"]) / 1000:.1f} s, of which its evaluator {r["eval"] / 1000:.1f} s</title></rect>')
        out.append(f'<text x="{xof(r["post"]) + 6:.1f}" y="{y + 14}" font-size="10.5" fill="var(--ink)">request {r["req"] / 1000:.0f} KB; '
                   f'its evaluator {r["eval"] / 1000:.1f} s in all; the rest, making and sending {r["res_bytes"] / 1e6:.1f} MB back</text>')
        y += 22
        # the moments
        for t, label, colour in ((r["own"], "first redraw", "var(--muted)"), (r["pic"], "the picture", "var(--accent2)")):
            x = xof(t)
            out.append(f'<line x1="{x:.1f}" y1="{y - 46}" x2="{x:.1f}" y2="{y + 2}" stroke="{colour}" stroke-width="2"/>')
            out.append(f'<text x="{x + 4:.1f}" y="{y + 12}" font-size="10.5" fill="{colour}" font-weight="700">{label}, {t / 1000:.1f} s</text>')
        y += 30
    for t in range(0, span + 1, 1000):
        x = xof(t)
        out.append(f'<line x1="{x:.1f}" y1="{y - 6}" x2="{x:.1f}" y2="{y}" stroke="var(--muted)" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{y + 12}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{t // 1000} s</text>')
    h = y + 22
    alt = "; ".join(f"{r['label']} {r['from']} to {r['to']}: request at {r['post'] / 1000:.2f} s, the picture's message after "
                    f"{r['worker'] / 1000:.1f} s in the worker, decoded in {r['decode'] / 1000:.1f} s, the picture at {r['pic'] / 1000:.1f} s" for r in picks)
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{html.escape(alt)}" style="width:100%;height:auto;display:block">'
            + "".join(out) + f"</svg><figcaption>Firefox on GitHub's machines, a release build ({FT['sha']}, run {FT['run']}), Compiled views on, "
            "the page's own timeline (<code>Util.BenchMarks</code>). Main thread, blue: the page's own work (each update, calculate and view); "
            "orange: decoding a message from the worker. Worker, grey: from the request to its result; when within that its evaluator ran is "
            "not recorded, only its total.</figcaption></figure></div>")


# (Matthew, 2026-11-08: "let's presume that the worker-main-thread communication cost dominates (preparing result,
# sending, decoding); let's confirm that") the same edits, with the worker's own timeline and each answer broken down
FA = json.loads(DW("firefox-answer.json"))


def trip_parts(e, mode):
    """one edit's split, from the page's timeline and the worker's: the evaluator (the result's eval_ms), the answer
    shared, encoded and posted in the worker, and decoded on the main thread; the page's own work before and after"""
    ms = e["marks"]
    post = next(m for m in ms if m["what"] == "post to worker")
    res = [m for m in ms if m.get("kind") == "result"][-1]
    dec = sorted([m for m in ms if m["what"] == "worker message decoded" and m.get("bytes", 0) > 1e6], key=lambda m: m["at"])
    rdec = dec[-1]
    sdec = [m for m in dec if m is not rdec]

    def w(name):
        # (after the edit: a run of slices that posted the last edit's result shows in this edit's marks, before it)
        return sum(m["ms"] for m in ms if m["what"] == "worker: " + name and m["at"] > 0)

    pic = e["picture_changed_ms"]
    done = [d for d in e["dynamics"] if d[1] == "ok"][-1][0]
    r = {"label": e["label"], "from": e["from"], "to": e["to"], "mode": mode, "pic": pic, "done": done,
         "post": post["at"], "eval": res["eval_ms"],
         "share": w("share result"), "encode": w("encode result"), "send": w("post result") + w("make result"),
         "decode": rdec["ms"], "dec_at": rdec["at"], "res_bytes": rdec["bytes"],
         "s_share": w("share stream"), "s_encode": w("encode stream"),
         "s_decode": sum(m["ms"] for m in sdec), "s_at": sdec[0]["at"] if sdec else None,
         "s_bytes": sdec[0]["bytes"] if sdec else 0, "via_stream": bool(sdec) and sdec[0]["at"] < pic,
         "parts": e.get("answer_parts") or []}
    r["trip"] = r["share"] + r["encode"] + r["send"] + r["decode"]
    r["after"] = pic - (rdec["at"] + rdec["ms"])
    r["wother"] = rdec["at"] - post["at"] - r["eval"] - r["share"] - r["encode"] - r["send"]
    r["s_trip"] = r["s_share"] + r["s_encode"] + r["s_decode"]
    return r


TR = [trip_parts(e, m) for m in ("on", "off") for e in FA["edits"][m]]
_nk = [r for r in TR if not r["via_stream"]]
_ar = [r for r in TR if r["via_stream"]]


def _ans(r, kind):
    return next(p for p in r["parts"] if p.get("kind") == kind)


def _part(p, name):
    return next((x["bytes"] for x in p["parts"] if x["part"] == name), 0)


_res = [_ans(r, "result") for r in TR]
_str = [_ans(r, "stream") for r in _ar]
_lohi = lambda xs, f=lambda x: x: (min(f(x) for x in xs), max(f(x) for x in xs))
s1 = lambda x: f"{x / 1000:.1f}"
mb = lambda b: f"{b / 1e6:.1f}"
mb2 = lambda b: f"{b / 1e6:.2f}"


def _rng(key, xs, f, fmt=s1):
    lo, hi = _lohi(xs, f)
    WNUMS[key + "_lo"], WNUMS[key + "_hi"] = fmt(lo), fmt(hi)


WNUMS.update({"an_run": str(FA["run"]), "an_sha": FA["sha"], "an_n": str(len(TR))})
_rng("an_pic", _nk, lambda r: r["pic"])
_rng("an_eval", _nk, lambda r: r["eval"])
_rng("an_share", _nk, lambda r: r["share"])
_rng("an_enc", _nk, lambda r: r["encode"])
_rng("an_dec", _nk, lambda r: r["decode"])
_rng("an_trip", _nk, lambda r: r["trip"])
_rng("an_trip_pct", _nk, lambda r: r["trip"] / r["pic"] * 100, lambda x: f"{x:.0f}")
_rng("an_eval_pct", _nk, lambda r: r["eval"] / r["pic"] * 100, lambda x: f"{x:.0f}")
_rng("an_page", _nk, lambda r: r["post"] + r["after"], lambda x: f"{x / 1000:.2f}")
_rng("an_wother", _nk, lambda r: r["wother"], lambda x: f"{x / 1000:.2f}")
_rng("an_trip_x", _nk, lambda r: r["trip"] / r["eval"], lambda x: f"{x:.1f}")
_rng("an_apic", _ar, lambda r: r["pic"])
_rng("an_adone", _ar, lambda r: r["done"])
_rng("an_aeval", _ar, lambda r: r["eval"])
_rng("an_strip", _ar, lambda r: r["s_trip"])
_rng("an_rtrip", _ar, lambda r: r["trip"])
_rng("an_ashare", _ar, lambda r: r["s_share"] + r["share"])
_rng("an_share_all", TR, lambda r: r["share"] + r["s_share"])
_rng("an_rbytes", _res, lambda p: p["bytes"], mb)
_rng("an_sbytes", _str, lambda p: p["bytes"], mb)
_rng("an_env", _res, lambda p: p["probes"]["env"], mb)
_rng("an_env_pct", _res, lambda p: p["probes"]["env"] / p["bytes"] * 100, lambda x: f"{x:.0f}")
_rng("an_val", _res, lambda p: p["probes"]["value"], mb2)
_rng("an_trace", _res, lambda p: _part(p, "result.state.obs_trace"), mb)
_rng("an_tenv", _res, lambda p: p["trace"]["span_close_envs"], mb)
_rng("an_rvalue", _res, lambda p: _part(p, "result.value"), lambda b: f"{b / 1000:.0f}")
_rng("an_senv", _str, lambda p: p["probes"]["env"], mb)
_rng("an_held", [p for p in _res if p["held_refs"]], lambda p: p["held_refs"], lambda x: f"{x:.0f}")
_rng("an_parts_s", [{"s": e["answer_parts_s"]} for m in ("on", "off") for e in FA["edits"][m]], lambda x: x["s"], lambda x: f"{x:.0f}")
WNUMS.update({
    "an_probes": str(_res[0]["probes"]["count"]),
    "an_events": str(sum(ev["n"] for ev in _res[0]["trace"]["events"])),
    "an_closes": str(next(ev["n"] for ev in _res[0]["trace"]["events"] if ev["kind"] == "span close")),
    "an_entries_lo": str(min(_part_n for _part_n in [next(x["n"] for x in p["parts"] if x["part"] == "final stream.completed entry.value") for p in _res])),
    "an_entries_hi": str(max(_part_n for _part_n in [next(x["n"] for x in p["parts"] if x["part"] == "final stream.completed entry.value") for p in _res])),
    "an_arms_held": str(max(p["held_refs"] for r, p in zip(TR, _res) if r["via_stream"])),
})


# (the speculation's estimate: report 45's whole programs, and the picture's view in Firefox, compiled against the interpreter)
_ev_all = [r["eval"] for r in TR]
_x_min = float(WNUMS["ff_pic_x"].replace(",", ""))
WNUMS.update({
    "an_evall_lo": s1(min(_ev_all)), "an_evall_hi": s1(max(_ev_all)),
    "r45_whole_lo": "284", "r45_whole_hi": "1,152",  # (report 45's speed table: the Polygons view's whole program, a recursive sum)
    "jr_run_lo": f"{min(_ev_all) / _x_min:.0f}", "jr_run_hi": f"{max(_ev_all) / _x_min:.0f}",
    "e_livelits": "53",  # (the check's count of livelits on the slide, as loaded)
    "an_enc_rate": f"{sum(r['encode'] for r in _nk) / sum(r['res_bytes'] for r in _nk) * 1e3:.2f}",
    "an_dec_rate": f"{sum(r['decode'] for r in _nk) / sum(r['res_bytes'] for r in _nk) * 1e3:.2f}",
})


# (the next run) the largest probe's first sample: its environment's bindings
FP = json.loads(DW("firefox-answer-probes.json"))
_big = [(a, a["top"][0]["first"]) for a in FP["answers"]]
_dr = [(a, next(e for e in f["env"] if e["name"] == "Drawing")) for a, f in _big]
_drr = [(a, e) for a, e in _dr if a["kind"] == "result"]
WNUMS.update({
    "dr_run": str(FP["run"]), "dr_sha": FP["sha"],
    "dr_lo": mb(min(e["bytes"] for _, e in _dr)), "dr_hi": mb(max(e["bytes"] for _, e in _dr)),
    "dr_pct": f"{max(e['bytes'] / a['bytes'] for a, e in _drr) * 100:.0f}",
    "dr_env_lo": mb(min(f["env_bytes"] for _, f in _big)), "dr_env_hi": mb(max(f["env_bytes"] for _, f in _big)),
    "dr_drawn": mb2(max(next(e["bytes"] for e in f["env"] if e["name"] == "drawn") for _, f in _big)),
})


def table_trip():
    """every edit: the picture's time, and the worker's and the page's parts of it"""
    rows = []
    for r in TR:
        via = (f"a stream, {mb(r['s_bytes'])} MB: shared {s1(r['s_share'])}, encoded {s1(r['s_encode'])}, decoded {s1(r['s_decode'])}"
               if r["via_stream"] else "the result")
        rows.append(
            f"<tr><td>{html.escape(r['label'])} {r['from']} to {r['to']}</td><td>{r['mode']}</td><td><b>{s1(r['pic'])}</b></td>"
            f"<td>{s1(r['eval'])}</td><td>{s1(r['share'])}</td><td>{s1(r['encode'])}</td><td>{s1(r['decode'])}</td>"
            f"<td><b>{s1(r['trip'])}</b></td><td>{via}</td><td>{s1(r['done'])}</td></tr>")
    return ('<table class="vals"><tr><th>the edit</th><th>compiled views</th><th>the picture shows it, s</th>'
            '<th>the worker\'s evaluator, s</th><th>the result shared (in the worker), s</th><th>encoded (in the worker), s</th>'
            '<th>decoded (on the main thread), s</th><th>the result\'s trip, s</th><th>the picture came with</th>'
            '<th>the run done, the result handled, s</th></tr>' + "".join(rows) + "</table>")


def table_answer():
    """what the result holds, as it crossed, on one neck edit and one arms edit"""
    picks = [next(r for r in TR if not r["via_stream"]), next(r for r in TR if r["via_stream"])]
    names = [("the whole result", lambda p: p["bytes"]),
             ("the probes' samples: their environments", lambda p: p["probes"]["env"]),
             ("the probes' samples: their values", lambda p: p["probes"]["value"]),
             ("the probes' samples: call stacks, arguments and frames",
              lambda p: p["probes"]["call_stack"] + p["probes"]["args"] + p["probes"]["frame"]),
             ("the observation trace (the final state's <code>obs_trace</code>)", lambda p: _part(p, "result.state.obs_trace")),
             ("of it, the environments of its span-close events", lambda p: p["trace"]["span_close_envs"]),
             ("the program's value", lambda p: _part(p, "result.value")),
             ("the final stream's entries, besides their states", lambda p: _part(p, "final stream.completed entry.value") + _part(p, "final stream.completed entry.prev_elab"))]
    rows = []
    for label, f in names:
        cells = "".join(f"<td>{f(_ans(r, 'result')) / 1e6:.2f}</td>" if f(_ans(r, 'result')) >= 5e3 else "<td>&lt; 0.01</td>" for r in picks)
        rows.append(f"<tr><td>{label}</td>{cells}</tr>")
    head = "".join(f"<th>{html.escape(r['label'])} {r['from']} to {r['to']}, MB</th>" for r in picks)
    return '<table class="vals"><tr><th>the result, as it crossed</th>' + head + "</tr>" + "".join(rows) + "</table>"


def fig_witch_trip():
    """the neck edits, each a bar from the edit to the picture: the page before the request, the worker's evaluator and
    its other work, the result shared and encoded in the worker, decoded on the main thread, and the page after"""
    W, left, right = 940, 190, 20
    span = max(r["pic"] for r in _nk)
    xof = lambda t: left + t / span * (W - left - right)
    segs = [("the page, before the request", "post", "var(--line)"),
            ("the worker's evaluator", "eval", "var(--accent)"),
            ("the worker's other work", "wother", "var(--muted)"),
            ("the result shared (worker)", "share", "#c2410c"),
            ("encoded (worker)", "encode", "#ea580c"),
            ("decoded (main thread)", "decode", "#f59e0b"),
            ("the page, to the picture", "after", "var(--line)")]
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">A small edit on the Witch slide, in Firefox: '
           'the trip between the worker and the page (orange) against the evaluator (blue)</text>']
    y = 36
    for r in _nk:
        out.append(f'<text x="{left - 10}" y="{y + 14}" font-size="11.5" text-anchor="end" fill="var(--ink)">{html.escape(r["label"])} '
                   f'{r["from"]} to {r["to"]}, views {r["mode"]}</text>')
        t = 0
        for name, key, colour in segs:
            d = max(0, r[key] if key != "send" else 0)
            if key == "encode":
                d += r["send"]
            x0, x1 = xof(t), xof(t + d)
            out.append(f'<rect x="{x0:.1f}" y="{y}" width="{max(0.8, x1 - x0):.1f}" height="20" fill="{colour}" opacity="0.92">'
                       f'<title>{name}: {d / 1000:.2f} s</title></rect>')
            if x1 - x0 > 44:
                out.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{y + 14}" font-size="10.5" text-anchor="middle" '
                           f'fill="{"var(--ink)" if colour in ("var(--line)", "var(--muted)") else "#fff"}" font-weight="700">{d / 1000:.1f} s</text>')
            t += d
        y += 28
    # the legend
    x = left
    for name, colour in (("evaluator (worker)", "var(--accent)"), ("other (worker)", "var(--muted)"), ("shared (worker)", "#c2410c"),
                         ("encoded (worker)", "#ea580c"), ("decoded (page)", "#f59e0b"), ("the page's own work", "var(--line)")):
        out.append(f'<rect x="{x}" y="{y + 4}" width="12" height="12" fill="{colour}"/>')
        out.append(f'<text x="{x + 16}" y="{y + 14}" font-size="10.5" fill="var(--muted)">{name}</text>')
        x += 16 + 5.4 * len(name) + 14
    y += 22
    for t in range(0, int(span) + 1, 1000):
        xx = xof(t)
        out.append(f'<line x1="{xx:.1f}" y1="{y}" x2="{xx:.1f}" y2="{y + 6}" stroke="var(--muted)" stroke-width="1"/>')
        out.append(f'<text x="{xx:.1f}" y="{y + 18}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{t // 1000} s</text>')
    h = y + 26
    alt = "; ".join(f"{r['label']} {r['from']} to {r['to']}, views {r['mode']}: the picture at {s1(r['pic'])} s; evaluator {s1(r['eval'])} s; "
                    f"result shared {s1(r['share'])} s, encoded {s1(r['encode'])} s, decoded {s1(r['decode'])} s" for r in _nk)
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{html.escape(alt)}" '
            f'style="width:100%;height:auto;display:block">' + "".join(out) +
            f"</svg><figcaption>Firefox on GitHub's machines, a release build (<code>{FA['sha']}</code>, run {FA['run']}), the neck "
            "edits, whose picture comes with the run's result. Each bar runs from the edit to the picture showing it, its parts laid end "
            "to end. The worker's parts come from its own timeline (new here); the worker's other work is what is left of its time "
            "after the evaluator, sharing and encoding (the reuse plan, composing the request, the waits between slices).</figcaption>"
            "</figure></div>")


def fig_witch_edit():
    """a small edit on the Witch slide, in Firefox, from the edit to the picture's change, on a log scale, against a
    60 fps frame: the slider's own first redraw, the picture showing the edit, and within it the picture's view"""
    rows = [("the slider, redrawn", "the page's first change, after the edit's own work", upper_middle(_own), "var(--muted)"),
            ("the picture shows the edit", "compiled views on (median of 4)", E_PIC, "var(--accent2)"),
            ("", "compiled views off (median of 4)", upper_middle(_eoff), "var(--warn, #b45309)"),
            ("of which, the picture's view", "on the interpreter", FF_PIC["interpreted"]["median"], "var(--warn, #b45309)"),
            ("", "compiled", FF_PIC["compiled"]["median"], "var(--accent2)")]
    W, left, right = 940, 330, 150
    lo, hi = math.log10(1), math.log10(20000)
    xof = lambda v: left + (math.log10(v) - lo) / (hi - lo) * (W - left - right)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">A small edit on the Witch slide, in Firefox: '
           'time from the edit, on a log scale, against a 60 fps frame (16.7 ms)</text>']
    top, step = 34, 30
    bottom = top + len(rows) * step
    for t in (1, 10, 100, 1000, 10000):
        x = xof(t)
        tick = f"{t / 1000:g} s" if t >= 1000 else f"{t:g} ms"
        out.append(f'<line x1="{x:.1f}" y1="28" x2="{x:.1f}" y2="{bottom:.0f}" stroke="var(--line)" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{bottom + 14}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{tick}</text>')
    x60 = xof(FRAME_60)
    out.append(f'<rect x="{left}" y="28" width="{x60 - left:.1f}" height="{bottom - 28:.0f}" fill="var(--good, #2e7d32)" opacity="0.07"/>')
    out.append(f'<line x1="{x60:.1f}" y1="26" x2="{x60:.1f}" y2="{bottom + 2:.0f}" stroke="var(--good, #2e7d32)" stroke-width="2"/>')
    out.append(f'<text x="{x60 + 5:.1f}" y="{bottom + 14}" font-size="11" fill="var(--good, #2e7d32)" font-weight="700">60 fps</text>')
    y = top
    for name, sub, v, colour in rows:
        if name:
            out.append(f'<text x="{left - 10}" y="{y + 11}" font-size="12" text-anchor="end" fill="var(--ink)" font-weight="700">{html.escape(name)}</text>')
            out.append(f'<text x="{left - 10}" y="{y + 24}" font-size="10.5" text-anchor="end" fill="var(--muted)">{html.escape(sub)}</text>')
        else:
            out.append(f'<text x="{left - 10}" y="{y + 17}" font-size="10.5" text-anchor="end" fill="var(--muted)">{html.escape(sub)}</text>')
        out.append(f'<rect x="{left}" y="{y + 5}" width="{max(2, xof(v) - left):.1f}" height="16" rx="3" fill="{colour}" opacity="0.85"><title>{html.escape(name or "")} {sub}: {v:.1f} ms</title></rect>')
        if v >= 1000:
            label = f"{v / 1000:.1f} s ({v / FRAME_60:,.0f} frames)"
        elif v >= 100:
            label = f"{v / 1000:.2f} s ({v / FRAME_60:.0f} frames)"
        else:
            label = f"{ms(v)} ms ({fps(v)} fps)"
        out.append(f'<text x="{xof(v) + 8:.1f}" y="{y + 17}" font-size="11.5" fill="var(--ink)" font-weight="700">{label}</text>')
        y += step
    h = bottom + 24
    alt = "A small edit, against a 60 fps frame: " + "; ".join(f"{n or 'the same'}, {s}, {v:.0f} ms" for n, s, v, _ in rows)
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{alt}" style="width:100%;height:auto;display:block">'
            + "".join(out) + f"</svg><figcaption>Firefox on GitHub's machines, a release build ({FE['sha']}, run {FE['run']}): four edits each "
            "way (the neck slider 2 steps, there and back; the arms slider 10, there and back), each from the edit to the first change of "
            "the page under the slider, and to the picture's first new drawing. Frames are counted at 60 fps. The picture's view is the "
            f"bench of <a href=\"#witch-firefox\">in Firefox</a> ({FF['sha']}, run {FF['run']}), one render alone.</figcaption></figure></div>")


def fig_witch_firefox():
    """the Witch slide's views in Firefox, in the app, against a 60 fps frame: the picture on the interpreter (its
    compiled path refused), and the slide's four polygon editors both ways"""
    rows = [("Drawing.picture", "before the fix: interpreter", FFB_PIC["compiled"]["median"], "var(--muted)"),
            ("Drawing.picture", "interpreter", FF_PIC["interpreted"]["median"], "var(--warn, #b45309)"),
            ("", "compiled", FF_PIC["compiled"]["median"], "var(--accent2)")]
    for i, v in enumerate(sorted(FF_POLY, key=lambda v: v["interpreted"]["median"])):
        rows.append((f"Drawing.polygons {i + 1}", "interpreter", v["interpreted"]["median"], "var(--warn, #b45309)"))
        rows.append(("", "compiled", v["compiled"]["median"], "var(--accent2)"))
    W, left, right = 940, 330, 120
    lo, hi = math.log10(0.1), math.log10(300)
    xof = lambda v: left + (math.log10(v) - lo) / (hi - lo) * (W - left - right)
    out = ['<text x="16" y="18" font-size="12.5" font-weight="700" fill="var(--ink)">The Witch slide\'s views in Firefox, in the app, '
           'ms a render on a log scale, against a 60 fps frame (16.7 ms)</text>']
    top, step = 34, 24
    bottom = top + len(rows) * step
    for t in (0.1, 1, 10, 100):
        x = xof(t)
        out.append(f'<line x1="{x:.1f}" y1="28" x2="{x:.1f}" y2="{bottom:.0f}" stroke="var(--line)" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{bottom + 14}" font-size="10.5" text-anchor="middle" fill="var(--muted)">{t:g} ms</text>')
    x60 = xof(FRAME_60)
    out.append(f'<rect x="{left}" y="28" width="{x60 - left:.1f}" height="{bottom - 28:.0f}" fill="var(--good, #2e7d32)" opacity="0.07"/>')
    out.append(f'<line x1="{x60:.1f}" y1="26" x2="{x60:.1f}" y2="{bottom + 2:.0f}" stroke="var(--good, #2e7d32)" stroke-width="2"/>')
    out.append(f'<text x="{x60 + 5:.1f}" y="{bottom + 14}" font-size="11" fill="var(--good, #2e7d32)" font-weight="700">60 fps, 16.7 ms</text>')
    y = top
    for name, sub, v, colour in rows:
        label = (html.escape(name) + ", " if name else "") + html.escape(sub)
        out.append(f'<text x="{left - 10}" y="{y + 13}" font-size="12" text-anchor="end" fill="var(--ink)"{" font-weight=\"700\"" if name else ""}>{label}</text>')
        out.append(f'<rect x="{left}" y="{y + 3}" width="{max(2, xof(v) - left):.1f}" height="14" rx="3" fill="{colour}" opacity="0.85"><title>{html.escape(name or "")} {sub}: {v:.3f} ms</title></rect>')
        out.append(f'<text x="{max(xof(v), left + 2) + 8:.1f}" y="{y + 14}" font-size="11" fill="var(--ink)">{ms(v)} ms ({fps(v)} fps)</text>')
        y += step
    h = bottom + 24
    alt = "In Firefox, against 16.7 ms: " + "; ".join(f"{n or 'the same'}, {s}, {ms(v)} ms" for n, s, v, _ in rows)
    return (f'<div class="figrow"><figure class="f wide"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{alt}" style="width:100%;height:auto;display:block">'
            + "".join(out) + f"</svg><figcaption>Firefox on GitHub's machines, a release build ({FF['sha']}, run {FF['run']}; the first bar from "
            f"{FFB['sha']}, run {FFB['run']}, before the fix): each view "
            "run again on its last model, bypassing the app's memo, 15 samples, each a loop of calls at least 25 ms long. The frames a "
            "second are each time alone, as if updating the state were free.</figcaption></figure></div>")


SVGS = [("hazel-jit", "hazel-jit", NODE["hazel-jit"]), ("rescript", "ReScript", NODE["ReScript"]),
        ("melange", "Melange", NODE["Melange"]), ("js_of_ocaml", "js_of_ocaml", WT["jsoo_printf_ms"]),
        ("by-hand", "by hand", NODE["hand-written JS"])]


def fig_witch_svgs(prefix="witch/"):
    """each compiler's own drawing, as the markup its Html came to (all five the same, byte for byte)"""
    cells = "".join(
        f'<figure class="f witchcell"><a href="{prefix}{slug}.html"><img src="{prefix}svg/{slug}.svg" width="160" height="220" '
        f'alt="The Witch, as {html.escape(name)}\'s view drew her"></a>'
        f'<figcaption><b>{html.escape(name)}</b><br>{v:.2f} ms ({fps(v)} fps)</figcaption></figure>' for slug, name, v in SVGS)
    return ('<div class="witchrow">' + cells + "</div>")


# ---- one page per output

PAGES = [
    ("hazel", "Hazel, the source", "hazel", None),
    ("hazel-jit", "hazel-jit's output", "js", "hazel-jit"),
    ("rescript", "ReScript 12.3.1's output", "js", "rescript"),
    ("melange", "Melange 5.0.0's output", "js", "melange"),
    ("js_of_ocaml", "js_of_ocaml 5.9.1's output", "js", "js_of_ocaml"),
    ("by-hand", "JavaScript by hand", "js", "by-hand"),
]


def hand_source():
    s = DW("witch-bench.mjs")
    i = s.index("// by hand:")
    j = s.index("const views = {")
    return s[i:j].rstrip()


def jsoo_source():
    core = DW("witch-core.ml")
    return ("(* for js_of_ocaml: a number formatted as OCaml formats one *)\nlet fixed1 (x : float) = Printf.sprintf \"%.1f\" x\n\n"
            + core.rstrip())


def page_parts(slug):
    """the page's listings: [(heading, language, source)] and a paragraph that says what to look for"""
    hz = DW("picture.hz").rstrip()
    if slug == "hazel":
        return ([("The livelit, as the Witch slide defines it (<code>witch.hz</code>, <code>Drawing.^picture</code>)", "hazel", hz)],
                "<p>The view the other pages compile. Its model is one splice, the slide's code for the picture; <code class=\"hz\">view</code> "
                "asks for that splice's value (<code class=\"hz\">eval_splice</code>) and turns the picture's shapes into an SVG: a "
                "<code>viewBox</code> that fits every point, then one <code>polygon</code> or <code>polyline</code> per shape, each "
                "point's coordinates formatted with <code class=\"hz\">to_fixed</code>. The other languages' versions start where "
                "the splice's value arrives: <code class=\"hz\">case r | Some(Val(pic)) =&gt; …</code>.</p>")
    if slug == "hazel-jit":
        return ([("hazel-jit's JavaScript for the livelit's module, formatted by esbuild (its runtime is <code>$R</code>)", "js", DW("hazeljit-witch-pretty.js").rstrip())],
                "<p>What hazel-jit wrote for the module, as the app compiles it once per definition (in "
                f"{WNUMS['compile']} ms). Look for <code>coords$</code>: each number goes through <code>$R.b.to_fixed([x, 1])</code>, "
                "a builtin that takes its arguments as one array and clamps the digits; each list is walked by a recursive "
                "call, <code>grow_all</code> and <code>bounds</code> included, where the other compilers loop; each "
                "<code class=\"hz\">case</code> becomes a chain of conditional expressions with a <code>$R.nomatch</code> at its end.</p>")
    if slug == "rescript":
        return ([("ReScript source (<code>Witch.res</code>, the view as the Hazel is written)", "rescript", DW("Witch.res").rstrip()),
                 ("ReScript 12.3.1's JavaScript (<code>Witch.res.js</code>)", "js", DW("Witch.res.js").rstrip())],
                "<p>ReScript calls <code>toFixed</code> directly, turns <code>grow_all</code>, <code>bounds</code> and "
                "<code>framing</code> into <code>while</code> loops, reads a vertex's point as <code>v.at</code>, and makes each "
                "Html node an object with a string tag, <code>{TAG: \"Node\", _0, _1, _2}</code>. Since both of the shape's "
                "constructors carry <code>points</code> in the same place, <code>verticesOf</code> is just <code>s.points</code>.</p>")
    if slug == "melange":
        return ([("OCaml source (<code>witch-melange.ml</code>)", "ocaml", DW("witch-melange.ml").rstrip()),
                 ("Melange 5.0.0's JavaScript (from its playground)", "js", DW("witch-melange.js").rstrip())],
                "<p>Melange's output is ReScript's with numbers for tags (<code>TAG: /* Node */ 0</code>). Its string "
                "concatenation is nested to the right, as OCaml's <code>^</code> associates, and higher-order calls in the "
                "markup helpers go through <code>Curry._1</code> (a stub here: the view itself makes none).</p>")
    if slug == "js_of_ocaml":
        return ([("OCaml source (<code>witch-jsoo.ml</code>, without the picture's literal and the timing loop)", "ocaml", jsoo_source()),
                 ("js_of_ocaml 5.9.1's JavaScript, <code>--pretty</code>: the view's constants and functions", "js", DW("jsoo-excerpt.js").rstrip())],
                "<p>js_of_ocaml compiles the whole program, OCaml's runtime with it (115 KB here), and renames everything. "
                "The view is <code>_dv_</code>: <code>framing</code>, <code>bounds</code> and <code>grow_all</code> inlined "
                "into it as nested <code>for</code> loops, every tuple an array with its tag first. Each number is "
                "<code>_dc_</code>, OCaml's <code>Printf.sprintf \"%.1f\"</code>, which interprets the format at run time "
                f"before it calls <code>toFixed</code>: {WNUMS['jsoo_pf']} ms against {WNUMS['jsoo_tf']} ms when "
                "<code>fixed1</code> calls JS's <code>toFixed</code> instead (<code>witch-jsoo-tofixed.ml</code>).</p>")
    return ([("By hand: the view on the picture as JSON (arrays, plain objects)", "js", hand_source())],
            "<p>What a JavaScript programmer might write: arrays and <code>for…of</code>, the bounds in four variables "
            "instead of a tuple remade per point, attributes as pairs. The fastest of the five here, by a little.</p>")


def write_pages(CSS, HL, HL_CSS, HL_INLINE_CSS, inline, updated):
    os.makedirs(os.path.join(HERE, "witch"), exist_ok=True)
    nav = " · ".join(f'<a href="{s}.html">{html.escape(t.split(",")[0].replace(" the source", ""))}</a>' for s, t, _, _ in PAGES)
    for slug, title, _, svg in PAGES:
        listings, intro = page_parts(slug)
        body = [f'<body><main>\n<p class="series"><a href="../../">Hazel reports</a> · <a href="../">report 046</a> · '
                f'<a href="../#witch">the Witch\'s picture</a> · one page per output · updated {updated} MST</p>',
                f"<h1>The Witch's picture view: {html.escape(title)}</h1>",
                f'<p class="sub">One of six pages, one per version of the Witch slide\'s <code class="hz">^picture</code> view '
                f'(report 046, <a href="../#witch">a view</a>): {nav}.</p>', inline(intro)]
        if svg:
            v = dict((s, x) for s, _, x in SVGS)[svg]
            body.append(f'<figure class="f witchone"><img src="svg/{svg}.svg" width="240" height="330" alt="The Witch, as this output drew her">'
                        f"<figcaption>This output's drawing, written out as markup: {WNUMS['svg_chars']} characters, the same as "
                        f"the other four's and hazel-jit's in the app, byte for byte. Its view's work: {v:.2f} ms ({fps(v)} fps), "
                        "the median in one Node process.</figcaption></figure>")
        for head, lang, src in listings:
            hl, cls = HL[lang]
            body.append(f"<h2>{head}</h2>")
            body.append(f'<pre class="code {cls}">' + hl(src) + "</pre>")
        files = sorted(os.listdir(os.path.join(HERE, "data", "witch")))
        body.append('<p class="muted">The files, in 046/data/witch (sources, outputs, the benchmark, the timings): '
                    + ", ".join(f'<a href="../data/witch/{f}">{f}</a>' for f in files) + '.</p>\n</main></body>')
        head = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
                f"<title>The Witch's picture view: {html.escape(title)}</title>\n"
                f"<meta name=\"description\" content=\"Report 046: the Witch slide's ^picture view, {html.escape(title)}.\">\n"
                "<style>" + CSS + HL_CSS + HL_INLINE_CSS + "\n  figure.witchone img { display: block; max-width: 100%; height: auto; }</style>\n</head>\n")
        open(os.path.join(HERE, "witch", slug + ".html"), "w").write(head + "\n".join(body) + "\n")
    return [os.path.join("046", "witch", s + ".html") for s, _, _, _ in PAGES]
