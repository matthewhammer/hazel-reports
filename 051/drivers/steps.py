#!/usr/bin/env python3
"""^report(51): a Firefox check run's Witch steps and compilations, as numbers.

  python3 051/drivers/steps.py RUN_DIR...

For each run (a folder holding the check's jit.json): each of the Witch's four steps, compiled, with the picture's
time, the worker's answer, the page's own work before and after the picture, the comparison or the compile of the
slide's run, and the held request; the counts of what the slide's run did; and every compilation the page made."""
import json, os, statistics as st, sys

TOP = ("view", "calculate", "hazel-jit: the run compiled", "worker message decoded", "update",
       "samples' values made terms", "outline, on its own")  # the last from build 13: the outline out of the view


def witch(p):
    return next(s for s in json.load(open(p))["slides"] if s["slide"] == "Witch")


def steps(p):
    w = witch(p)
    out = []
    for e in w["edits"]["on"]:
        done = [t for t, s in e["dynamics"] if s == "ok"][-1]
        pic = e["picture_changed_ms"]
        marks = e["marks"]
        top = lambda m: m["what"] in TOP or m["what"].startswith("hazel-jit: the program compared")
        tot = lambda a, b: sum(m.get("ms", 0) for m in marks if top(m) and a <= m["at"] < b)
        out.append({
            "step": f"{e['label']} {e['from']} to {e['to']}", "picture_ms": pic, "worker_answer_ms": done,
            "page_before_picture_ms": round(tot(-1e9, pic)), "page_after_picture_ms": round(tot(pic, done + 500)),
            "compared": [(m["at"], m.get("ms")) for m in marks if m["what"].startswith("hazel-jit: the program compared")],
            "compared_parts": [(m["what"].split(": ")[-1], m.get("ms")) for m in marks if m["what"].startswith("hazel-jit: the comparison")],
            "compiled": [(m["at"], m.get("ms")) for m in marks if m["what"] == "hazel-jit: the run compiled"],
            "held_at": [m["at"] for m in marks if "held" in m["what"]],
            "as_data": [(m["what"], m.get("ms"), {k: v for k, v in m.items() if k not in ("what", "at", "ms")})
                        for m in marks if "as data" in m["what"] or "made terms" in m["what"]],
            "decoded": [m.get("ms") for m in marks if m["what"] == "worker message decoded"],
            "encoded": [(m["what"], m.get("ms"), m.get("bytes")) for m in marks if m["what"].startswith("worker: encode")],
        })
    return out


def compiles(p):
    out = []
    for s in json.load(open(p))["slides"]:
        for c in ((s.get("on") or {}).get("jit") or {}).get("compiles") or []:
            out.append(dict(c, slide=s["slide"]))
    return out


if __name__ == "__main__":
    for d in sys.argv[1:]:
        p = os.path.join(d, "jit.json")
        print("==", d)
        for s in steps(p):
            print(json.dumps(s))
        cs = compiles(p)
        for what in ("a livelit's definition", "a slide's whole run"):
            xs = [c for c in cs if c["what"] == what]
            if xs:
                tot = [c["to_js_ms"] + c["js_ms"] for c in xs]
                print(f"{what}: {len(xs)}, median {st.median(tot):.1f} ms, range {min(tot):.1f} to {max(tot):.1f}, "
                      f"to JS median {st.median([c['to_js_ms'] for c in xs]):.1f}, in the browser {st.median([c['js_ms'] for c in xs]):.1f}, "
                      f"nodes median {st.median([c['nodes'] for c in xs]):.0f}")
