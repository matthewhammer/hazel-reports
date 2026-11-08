// ^report(46): a small edit to the Witch's picture, and what report 45's sharing would save on it. In one Node
// process, with hazel-jit's compiled ^picture (data/witch/hazeljit-witch-src.js) and its runtime:
//   today:   the new picture, fresh from the trip in, through the whole compiled view;
//   shared:  the new picture first merged with the last one (every part equal to the last one's IS the last one's:
//            report 45's diff, run the other way), then the view with its per-shape work kept by the shape it was
//            given (a memo on shape_node and on shape_nodes' tail, by object identity).
// Checks that both give the same Html as markup. Prints JSON.
//   node edit-share.mjs data/witch witch/svg   (from 046/)
import { readFileSync } from "node:fs";

const dir = process.argv[2], svgdir = process.argv[3];
const shapes0 = JSON.parse(readFileSync(dir + "/picture.json", "utf8")).shapes;
// (the report wrote its SVG files with the namespace added)
const expected = readFileSync(svgdir + "/hazel-jit.svg", "utf8").trim().replace(' xmlns="http://www.w3.org/2000/svg"', "");
const R = (0, eval)("(" + readFileSync(dir + "/hazeljit-runtime-src.js", "utf8") + ")");
const src = readFileSync(dir + "/hazeljit-witch-src.js", "utf8");
const CALL = "{h: (shape_node$40)(s$46), t: (shape_nodes$42)(tl$47)}";
if (!src.includes(CALL)) throw new Error("the compiled shape_nodes is not where it was");
const srcMemo = src.replace(CALL, "{h: $MEMO(shape_node$40, s$46), t: $MEMO_LIST(shape_nodes$42, tl$47)}");
const P0 = new Function("$R", src)(R);
let memo = new WeakMap(), listMemo = new WeakMap(), misses = 0;
const MEMO = (f, s) => { let r = memo.get(s); if (r === undefined) { misses++; r = f(s); memo.set(s, r); } return r; };
const MEMO_LIST = (f, l) => { if (l === null) return f(l); let r = listMemo.get(l); if (r === undefined) { r = f(l); listMemo.set(l, r); } return r; };
const P1 = new Function("$R", "$MEMO", "$MEMO_LIST", srcMemo)(R, MEMO, MEMO_LIST);

// the model as HazelJitValue.to_js makes it (as witch-bench.mjs does): fresh objects every time, as a run's new value
const tup = (vs, ls) => { const a = vs.slice(); ls.forEach((l, i) => { if (l) a[l] = vs[i]; }); return a; };
const list = xs => xs.reduceRight((t, h) => ({ h, t }), null);
const toJs = shapes => tup([{ c: "SpliceRef", v: ["witch", list(shapes.map(s => {
  const pts = list(s.points.map(([x, y, l]) => tup([[x, y], l ? { c: "Anchor", v: l } : { c: "Plain" }], ["at", "label"])));
  const stroke = tup([s.stroke.width, s.stroke.color], ["width", "color"]);
  return s.kind === "Polygon"
    ? { c: "Polygon", v: tup([s.name, pts, stroke, s.fill], ["name", "points", "stroke", "fill"]) }
    : { c: "Path", v: tup([s.name, pts, stroke], ["name", "points", "stroke"]) };
}))] }], ["picture"]);
const run = cmd => {
  const b = cmd.v;
  switch (cmd.c) {
    case "Pure": return b;
    case "Bind": return run(b[1](run(b[0])));
    case "EvalSplice": return run(b[1]({ c: "Some", v: { c: "Val", v: b[0].v[1] } }));
    default: throw new Error("not in this view: " + cmd.c);
  }
};
const items = l => { const out = []; for (; l !== null; l = l.t) out.push(l.h); return out; };
const hjAttr = a => a.c === "Style" ? ` style="${items(a.v).map(([k, v]) => k + ": " + v).join(";")}"`
  : a.c === "Create" ? ` ${a.v[0]}="${a.v[1]}"` : ` ${a.c.toLowerCase()}="${a.v}"`;
const markup = h => h.c === "Text" ? h.v
  : `<${h.v[0]}${items(h.v[1]).map(hjAttr).join("")}>${items(h.v[2]).map(markup).join("")}</${h.v[0]}>`;

// share(a, b): b, with every part equal to a's part replaced by a's own (b is fresh: changed in place); a itself
// when all of b equals a. A labeled tuple is an array whose labels alias its indices: merged once, by index.
let visits = 0;
function share(a, b) {
  visits++;
  if (a === b) return a;
  if (typeof b !== "object" || b === null || typeof a !== "object" || a === null) return b;
  if (Array.isArray(b)) {
    // a tuple: its components by index; its labels (aliases of components) moved only when something changed
    const n = b.length;
    if (!Array.isArray(a) || a.length !== n) return b;
    let same = true, orig = null;
    for (let i = 0; i < n; i++) {
      const x = b[i], y = share(a[i], x);
      if (y !== x) { if (orig === null) orig = b.slice(); b[i] = y; }
      if (y !== a[i]) same = false;
    }
    if (same) return a;
    if (orig !== null) for (const k of Object.keys(b).slice(n)) { const i = orig.indexOf(b[k]); if (i >= 0) b[k] = b[i]; }
    return b;
  }
  if ("h" in b) {
    // a list, along its cells (not recursively: a long list would run out of stack); the shared suffix is a's own
    const cells = [];
    let x = a, y = b;
    while (y !== null && x !== null && y !== x && typeof y === "object" && "h" in y && typeof x === "object" && "h" in x) {
      cells.push([x, y]); x = x.t; y = y.t;
    }
    let tail = (y === null && x === null) || y === x ? x : y, same = tail === x;
    for (let j = cells.length - 1; j >= 0; j--) {
      const [p, q] = cells[j], h = share(p.h, q.h);
      if (same && h === p.h) { tail = p; } else { q.h = h; q.t = tail; tail = q; same = false; }
      visits++;
    }
    return tail;
  }
  if ("c" in b) {
    if (a.c !== b.c) return b;
    if (!("v" in b)) return "v" in a ? b : a;
    const v = share(a.v, b.v);
    if (v === a.v) return a;
    b.v = v;
    return b;
  }
  let same = true;
  for (const k in b) { b[k] = share(a[k], b[k]); if (b[k] !== a[k]) same = false; }
  if (same) for (const k in a) if (!(k in b)) same = false;
  return same ? a : b;
}

// an edit of k shapes: each one's first vertex moved down 1 unit, the shapes spread through the picture
const edited = k => {
  const s = JSON.parse(JSON.stringify(shapes0));
  const n = s.length, picked = [];
  for (let j = 0; j < k; j++) picked.push(1 + Math.floor(j * (n - 1) / k));
  for (const i of picked) s[i].points[0][1] += 1;
  return s;
};

const now = () => performance.now();
const median = xs => { const s = xs.slice().sort((a, b) => a - b); return s[Math.floor(s.length / 2)]; };
const time = (f, reps) => { const xs = []; for (let r = 0; r < reps; r++) { const t = now(); f(); xs.push(now() - t); } return xs; };

const view0 = m => run(P0.view(m)), view1 = m => run(P1.view(m));
// sanity: the compiled view's markup is the drawing the report shows
{ const m = markup(view0(toJs(shapes0))); if (m !== expected) { let i = 0; while (m[i] === expected[i]) i++; throw new Error("differs at " + i + ": " + JSON.stringify(m.slice(i - 60, i + 60)) + " vs " + JSON.stringify(expected.slice(i - 60, i + 60)) + " lengths " + m.length + " " + expected.length); } }

const RUNS = +(process.env.RUNS || 300);
const out = { shapes: shapes0.length, points: shapes0.reduce((n, s) => n + s.points.length, 0), runs: RUNS, rows: [] };
// warm both paths
for (let i = 0; i < 200; i++) { view0(toJs(shapes0)); const m = toJs(shapes0); share(toJs(shapes0), m); view1(m); }
for (const k of [0, 1, 5, 17, 30, 60, shapes0.length]) {
  const after = edited(k);
  const today = [], merge = [], kept = [], tripJs = [];
  let ok = true, missesSeen = 0, visitsSeen = 0;
  for (let r = 0; r < RUNS; r++) {
    // the last picture, drawn once with the memo (the state before the edit)
    memo = new WeakMap(); listMemo = new WeakMap();
    const last = toJs(shapes0);
    view1(last);
    // the trip in, as plain JS (not jsoo's: only to keep the new model fresh)
    let t = now(); const fresh = toJs(after); tripJs.push(now() - t);
    const fresh2 = toJs(after);
    t = now(); const h0 = view0(fresh2); today.push(now() - t);
    visits = 0; t = now(); const merged = share(last, fresh); merge.push(now() - t); visitsSeen = visits;
    misses = 0; t = now(); const h1 = view1(merged); kept.push(now() - t); missesSeen = misses;
    if (r === 0) ok = markup(h0) === markup(h1);
  }
  out.rows.push({ k, same_markup: ok, shape_node_calls: missesSeen, share_visits: visitsSeen,
    today_view_ms: +median(today).toFixed(4), share_ms: +median(merge).toFixed(4), kept_view_ms: +median(kept).toFixed(4),
    js_trip_in_ms: +median(tripJs).toFixed(4) });
}
console.log(JSON.stringify(out, null, 1));
