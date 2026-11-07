// ^report(46): the Witch slide's ^picture view, compiled by hazel-jit, ReScript and Melange, on the same picture, in one
// Node process. Each view is timed from the picture (as each language holds it) to the Html it returns (as each
// language holds it): the view's own work, not the trip in or the drawing. Each Html is then written out as markup and
// compared with the SVG the Hazel test drew (Test_HazelJit's witch_view_run, the same as the interpreter's).
//   node witch-bench.mjs ../witch698
import { readFileSync, writeFileSync } from "node:fs";
import * as W from "./src/Witch.res.js";
import * as M from "./src/WitchMelange.js";

const dir = process.argv[2] || "../witch698";
const shapes = JSON.parse(readFileSync(dir + "/picture.json", "utf8")).shapes;
const expected = readFileSync(dir + "/hazeljit.svg", "utf8").trim();

// hazel-jit: the definition's module as the test compiled it, run with the runtime it printed
const R = (0, eval)("(" + readFileSync(dir + "/hazeljit-runtime-src.js", "utf8") + ")");
const P = new Function("$R", readFileSync(dir + "/hazeljit-witch-src.js", "utf8"))(R);
// the model as HazelJitValue.to_js makes it: tuples as arrays with their labels as properties, lists {h, t}
const tup = (vs, ls) => { const a = vs.slice(); ls.forEach((l, i) => { if (l) a[l] = vs[i]; }); return a; };
const list = xs => xs.reduceRight((t, h) => ({ h, t }), null);
const picJs = list(shapes.map(s => {
  const pts = list(s.points.map(([x, y, l]) => tup([[x, y], l ? { c: "Anchor", v: l } : { c: "Plain" }], ["at", "label"])));
  const stroke = tup([s.stroke.width, s.stroke.color], ["width", "color"]);
  return s.kind === "Polygon"
    ? { c: "Polygon", v: tup([s.name, pts, stroke, s.fill], ["name", "points", "stroke", "fill"]) }
    : { c: "Path", v: tup([s.name, pts, stroke], ["name", "points", "stroke"]) };
}));
const model = tup([{ c: "SpliceRef", v: ["witch", picJs] }], ["picture"]);
// the view's command run down to its Html, as HazelJitDOM.run does (EvalSplice hands on Some(Val(the splice's value)))
const run = cmd => {
  const b = cmd.v;
  switch (cmd.c) {
    case "Pure": return b;
    case "Bind": return run(b[1](run(b[0])));
    case "EvalSplice": return run(b[1]({ c: "Some", v: { c: "Val", v: b[0].v[1] } }));
    default: throw new Error("not in this view: " + cmd.c);
  }
};
const hazeljitView = () => run(P.view(model));

// ReScript and Melange: the picture in each one's own values, made once, untimed
const picRes = W.pictureOf(shapes);
const picMel = M.picture_of(shapes);

// markup, to compare: hazel-jit's Html ({c, v}), and each OCaml-family Html through its own markup function
const items = l => { const out = []; for (; l !== null; l = l.t) out.push(l.h); return out; };
const hjAttr = a => a.c === "Style" ? ` style="${items(a.v).map(([k, v]) => k + ": " + v).join(";")}"`
  : a.c === "Create" ? ` ${a.v[0]}="${a.v[1]}"` : ` ${a.c.toLowerCase()}="${a.v}"`;
const hjMarkup = h => h.c === "Text" ? h.v
  : `<${h.v[0]}${items(h.v[1]).map(hjAttr).join("")}>${items(h.v[2]).map(hjMarkup).join("")}</${h.v[0]}>`;

// by hand: the view as a JS programmer might write it, on the picture as JSON (arrays, plain objects)
function handView(pic) {
  const coords = pts => { let s = ""; for (const p of pts) s += p[0].toFixed(1) + "," + p[1].toFixed(1) + " "; return s; };
  const frame = pic.find(s => s.kind === "Path" && s.name === "frame");
  const boxed = frame ? [frame] : pic;
  const first = boxed.length && boxed[0].points.length ? boxed[0].points[0] : [0, 0];
  let x0 = first[0], y0 = first[1], x1 = first[0], y1 = first[1];
  if (!(boxed.length && boxed[0].points.length)) x0 = y0 = x1 = y1 = 0;
  for (const s of boxed) for (const [x, y] of s.points) {
    if (x - 12 < x0) x0 = x - 12; if (y - 12 < y0) y0 = y - 12; if (x + 12 > x1) x1 = x + 12; if (y + 12 > y1) y1 = y + 12;
  }
  const w = x1 - x0, h = y1 - y0;
  const [w2, h2] = w * 440 > h * 320 ? [w, w * 440 / 320] : [h * 320 / 440, h];
  const viewBox = (x0 - (w2 - w) / 2).toFixed(1) + " " + (y0 - (h2 - h) / 2).toFixed(1) + " " + w2.toFixed(1) + " " + h2.toFixed(1);
  const kids = pic.map(s => s.kind === "Polygon"
    ? { tag: "polygon", attrs: [["points", coords(s.points)], ["fill", s.fill], ["stroke", s.stroke.color], ["stroke-width", s.stroke.width.toFixed(1)], ["stroke-linejoin", "round"]], kids: [] }
    : { tag: "polyline", attrs: [["points", coords(s.points)], ["fill", "none"], ["stroke", s.stroke.color], ["stroke-width", s.stroke.width.toFixed(1)], ["stroke-linejoin", "round"], ["stroke-linecap", "round"]], kids: [] });
  return { tag: "svg", attrs: [["viewBox", viewBox], ["width", "320"], ["height", "440"], ["style", "border: 1px solid #ccc;background: #fafafa"]], kids };
}
const handMarkup = h => `<${h.tag}${h.attrs.map(([k, v]) => ` ${k}="${v}"`).join("")}>${h.kids.map(handMarkup).join("")}</${h.tag}>`;

const views = {
  "hazel-jit": [hazeljitView, () => hjMarkup(hazeljitView())],
  "ReScript": [() => W.view(picRes), () => W.markup(W.view(picRes))],
  "Melange": [() => M.view(picMel), () => M.markup(M.view(picMel))],
  "hand-written JS": [() => handView(shapes), () => handMarkup(handView(shapes))],
};

const now = () => performance.now();
const runs = +(process.env.RUNS || 5), n = +(process.env.N || 200);
const out = { runs, n, medians_ms: {}, fastest_ms: {}, same: {} };
for (const [name, [view, markup]] of Object.entries(views)) {
  const m = markup();
  out.same[name] = m === expected ? "same" : `differs at ${[...m].findIndex((c, i) => c !== expected[i])} (${m.length} against ${expected.length} chars)`;
  if (process.env.WRITE) writeFileSync(`${dir}/${name}.svg`, m);
}
const meds = Object.fromEntries(Object.keys(views).map(k => [k, []])), fast = Object.fromEntries(Object.keys(views).map(k => [k, Infinity]));
for (let r = 0; r < runs; r++) {
  for (const [name, [view]] of Object.entries(views)) {
    for (let i = 0; i < 20; i++) view();
    const ts = [];
    for (let i = 0; i < n; i++) { const t0 = now(); view(); ts.push(now() - t0); }
    ts.sort((a, b) => a - b);
    meds[name].push(ts[n >> 1]);
    fast[name] = Math.min(fast[name], ts[0]);
  }
}
for (const k of Object.keys(views)) {
  const s = meds[k].slice().sort((a, b) => a - b);
  out.medians_ms[k] = +s[s.length >> 1].toFixed(4);
  out.fastest_ms[k] = +fast[k].toFixed(4);
}
console.log(JSON.stringify(out));
