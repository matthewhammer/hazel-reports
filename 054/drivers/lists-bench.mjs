// ^ticket(795) / ^report(54): three ways compiled code could hold a Hazel list, timed on the workloads hazel-jit's games run.
//   cells   today: null for [], {h, t} for x :: xs
//   arrays  an immutable JS array: x :: xs copies, a pattern's tail is a slice
//   hybrid  null, a cell {h, t}, or an array segment {a, i} (a suffix of a JS array, shared): a literal or a page's array
//           is a segment with no copy; x :: xs is a cell; a pattern on a segment gives a[i] and the segment from i + 1
// node lists-bench.mjs [out.json]
import { writeFileSync } from "node:fs";
const now = () => performance.now();
const median = xs => { const s = [...xs].sort((a, b) => a - b); return s[s.length >> 1]; };
function clock(f) {
  let batch = 1; for (let w = 0; w < 5; w++) f();
  for (;;) { const t = now(); for (let i = 0; i < batch; i++) f(); if (now() - t >= 2 || batch >= 1 << 20) break; batch *= 2; }
  const per = []; const start = now();
  while (per.length < 15 || (now() - start < 200 && per.length < 200)) { const t = now(); for (let i = 0; i < batch; i++) f(); per.push((now() - t) / batch); }
  return median(per);
}
const R = {
  cells: {
    nil: null, isNil: l => l === null, cons: (x, l) => ({ h: x, t: l }), head: l => l.h, tail: l => l.t,
    of: xs => { let r = null; for (let i = xs.length - 1; i >= 0; i--) r = { h: xs[i], t: r }; return r; },
    to: l => { const a = []; for (let p = l; p !== null; p = p.t) a.push(p.h); return a; },
    length: l => { let n = 0; for (let p = l; p !== null; p = p.t) n++; return n; },
    nth: (l, i) => { let p = l; while (i-- > 0) p = p.t; return p.h; },
  },
  arrays: {
    nil: [], isNil: l => l.length === 0, cons: (x, l) => { const r = new Array(l.length + 1); r[0] = x; for (let i = 0; i < l.length; i++) r[i + 1] = l[i]; return r; },
    head: l => l[0], tail: l => l.slice(1), of: xs => xs, to: l => l, length: l => l.length, nth: (l, i) => l[i],
  },
  hybrid: {
    nil: null, isNil: l => l === null, cons: (x, l) => ({ h: x, t: l }),
    head: l => l.a === undefined ? l.h : l.a[l.i],
    tail: l => l.a === undefined ? l.t : (l.i + 1 < l.a.length ? { a: l.a, i: l.i + 1 } : null),
    of: xs => xs.length ? { a: xs, i: 0 } : null,
    to: l => { if (l !== null && l.a !== undefined && l.i === 0) return l.a; const a = [];
      for (let p = l; p !== null;) { if (p.a !== undefined) { for (let i = p.i; i < p.a.length; i++) a.push(p.a[i]); break; } a.push(p.h); p = p.t; } return a; },
    length: l => { let n = 0; for (let p = l; p !== null;) { if (p.a !== undefined) return n + p.a.length - p.i; n++; p = p.t; } return n; },
    nth: (l, i) => { let p = l; while (p.a === undefined) { if (i === 0) return p.h; i--; p = p.t; } return p.a[p.i + i]; },
  },
};
// the workloads, each as compiled code would run it: recursion through patterns, cells built by ::
const W = {
  "sum by recursion over x :: rest": (L, l) => { const go = l => L.isNil(l) ? 0 : L.head(l) + go(L.tail(l)); return go(l); },
  "map, f(x) :: map(rest)": (L, l) => { const go = l => L.isNil(l) ? L.nil : L.cons(L.head(l) * 2, go(L.tail(l))); return go(l); },
  "build with an accumulator, then reverse": (L, l) => { let acc = L.nil; for (let p = l; !L.isNil(p); p = L.tail(p)) acc = L.cons(L.head(p), acc);
    let r = L.nil; for (let p = acc; !L.isNil(p); p = L.tail(p)) r = L.cons(L.head(p), r); return r; },
  "length (a builtin)": (L, l) => L.length(l),
  "nth, the middle (a builtin)": (L, l, n) => L.nth(l, n >> 1),
  "nth, the middle, by recursion": (L, l, n) => { const go = (l, i) => i === 0 ? L.head(l) : go(L.tail(l), i - 1); return go(l, n >> 1); },
  "a page's array in and back out": (L, l, n, xs) => L.to(L.of(xs)),
  "a page's array in, mapped, back out": (L, l, n, xs) => { const go = l => L.isNil(l) ? L.nil : L.cons(L.head(l) + 1, go(L.tail(l))); return L.to(go(L.of(xs))); },
};
const out = { node: process.version, when: new Date().toISOString(), rows: [] };
for (const n of [10, 100, 1000]) {
  const xs = Array.from({ length: n }, (_, i) => i);
  for (const [w, f] of Object.entries(W)) {
    const row = { n, workload: w };
    for (const [name, L] of Object.entries(R)) { const l = L.of(xs.slice()); const r = f(L, l, n, xs); row[name] = clock(() => f(L, l, n, xs)) * 1000; row[name + "_check"] = JSON.stringify(Array.isArray(r) || typeof r !== "object" || r === null ? r : L.to(r)).length; }
    out.rows.push(row);
    console.log(`n=${String(n).padStart(4)}  ${w.padEnd(42)} cells ${row.cells.toFixed(3).padStart(9)} us  arrays ${row.arrays.toFixed(3).padStart(9)} us  hybrid ${row.hybrid.toFixed(3).padStart(9)} us`);
  }
}
if (process.argv[2]) writeFileSync(process.argv[2], JSON.stringify(out, null, 1));
