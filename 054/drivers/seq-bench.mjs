// ^report(54), ^ticket(846): a sequence type beside List. Matthew: "a balanced representation that needs no rebalancing, the
// levels fixing the shape so an edit never rotates", with JS arrays at its leaves; caching from a content-determined shape
// matters less, so a gap's level may come from any well-spread source. This times, in JavaScript alone, one such Seq against
// the ways a Hazel list could be held, every one persistent (an edit gives a new sequence and leaves the old one whole, as a
// Hazel value must):
//
//   array    a frozen JS array: an edit copies it (slice, splice); a page's array crosses as it is
//   cells    null or {h, t}, hazel-jit's list today: an edit at position i copies the i cells before it
//   hybrid   cells, or a segment {a, i} (a's elements from index i on, shared): report 054's hybrid
//   seq      a treap over array views: a leaf is {a, s, e} (a's elements s to e - 1, never changed, shared), an inner node
//            {l, r, p, n} (its two sides, the gap's priority, the count below); the shape is the one the gaps' priorities
//            determine, so split and join never rotate; a small leaf meeting another sequence goes into the leaf at its edge
//            when the two fit in B elements (a copy of at most B, no new gap), so leaves stay full. A page's
//            array is one leaf over it, no copy.
//
// Each operation at sizes 1,000 to 1,000,000: insert one element at a random position, append one at the end, read the
// element at a random position, walk every element (a sum), and a page's array in and back out.
//
//   immutable  Immutable.js's List (5.0.3): a trie of 32-element arrays, its own insert; a page's array copied into it
//   funkia     @funkia/list (0.1.0): a relaxed radix-balanced tree; an insert is its splitAt, append and concat (it has no
//              insert of its own); a page's array copied into it
// (both installed from npm, with Matthew's OK of 2026-11-24, into a folder given as the second argument)
//
//   node seq-bench.mjs <out.json> [the folder holding node_modules/immutable and node_modules/@funkia/list]
import { writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import os from "node:os";
const OUT = process.argv[2], LIBS = process.argv[3];
const now = () => performance.now();
const median = xs => { const s = [...xs].sort((a, b) => a - b); return s[s.length >> 1]; };
// ns a call: the median of batches (as many calls as take at least 2 ms), at least 7 batches and 150 ms; a call over 1 s alone
function clock(f) {
  const t0 = now(); f(); const first = now() - t0;
  if (first > 1000) return first * 1e6;
  let batch = 1; while (batch < 1 << 22) { const t = now(); for (let i = 0; i < batch; i++) f(); if (now() - t >= 2) break; batch *= 2; }
  const per = [], start = now();
  while (per.length < 7 || (now() - start < 150 && per.length < 60)) { const t = now(); for (let i = 0; i < batch; i++) f(); per.push((now() - t) / batch * 1e6); }
  return median(per);
}
let sink = 0;
const keep = x => { sink = (sink + (typeof x === "number" ? x : 1)) | 0; };
let seed = 12345; const rnd = n => { seed = (seed * 16807) % 2147483647; return seed % n; };

// ---- array: frozen, copied on every edit
const A = {
  name: "array, copied",
  from: arr => arr,
  insert: (a, i, x) => { const b = a.slice(0, i); b.push(x); for (let k = i; k < a.length; k++) b.push(a[k]); return b; },
  append: (a, x) => { const b = a.slice(); b.push(x); return b; },
  get: (a, i) => a[i],
  sum: a => { let s = 0; for (let k = 0; k < a.length; k++) s += a[k]; return s; },
  out: a => a,
};
// ---- cells
const fromCells = arr => { let r = null; for (let i = arr.length - 1; i >= 0; i--) r = { h: arr[i], t: r }; return r; };
const L = {
  name: "cells",
  from: fromCells,
  insert: (l, i, x) => { const pre = []; let p = l; for (let k = 0; k < i; k++) { pre.push(p.h); p = p.t; } let r = { h: x, t: p }; for (let k = pre.length - 1; k >= 0; k--) r = { h: pre[k], t: r }; return r; },
  append: (l, x) => L.insert(l, L.len(l), x),
  len: l => { let n = 0; for (let p = l; p !== null; p = p.t) n++; return n; },
  get: (l, i) => { let p = l; for (let k = 0; k < i; k++) p = p.t; return p.h; },
  sum: l => { let s = 0; for (let p = l; p !== null; p = p.t) s += p.h; return s; },
  out: l => { const a = []; for (let p = l; p !== null; p = p.t) a.push(p.h); return a; },
};
// ---- hybrid: null | {h, t} | {a, i}
const H = {
  name: "hybrid",
  from: arr => arr.length ? { a: arr, i: 0 } : null,
  // walk to position i, copying what is before it as cells, then x, then the rest as it was
  insert: (l, i, x) => {
    const pre = []; let p = l, k = 0;
    while (k < i) { if ("h" in p) { pre.push(p.h); p = p.t; k++; } else { const take = Math.min(i - k, p.a.length - p.i); for (let j = 0; j < take; j++) pre.push(p.a[p.i + j]); k += take; p = p.i + take < p.a.length ? { a: p.a, i: p.i + take } : null; } }
    let r = { h: x, t: p }; for (let j = pre.length - 1; j >= 0; j--) r = { h: pre[j], t: r }; return r;
  },
  len: l => { let n = 0; for (let p = l; p !== null;) { if ("h" in p) { n++; p = p.t; } else { n += p.a.length - p.i; p = null; } } return n; },
  append: (l, x) => H.insert(l, H.len(l), x),
  get: (l, i) => { let p = l, k = 0; for (;;) { if ("h" in p) { if (k === i) return p.h; p = p.t; k++; } else return p.a[p.i + i - k]; } },
  sum: l => { let s = 0; for (let p = l; p !== null;) { if ("h" in p) { s += p.h; p = p.t; } else { for (let j = p.i; j < p.a.length; j++) s += p.a[j]; p = null; } } return s; },
  out: l => { if (l !== null && !("h" in l) && l.i === 0) return l.a; const a = []; for (let p = l; p !== null;) { if ("h" in p) { a.push(p.h); p = p.t; } else { for (let j = p.i; j < p.a.length; j++) a.push(p.a[j]); p = null; } } return a; },
};
// ---- seq: a treap over array views
const B = 32;
let gaps = 0;
const prio = () => { let x = (++gaps * 0x9e3779b1) | 0; x ^= x >>> 16; x = Math.imul(x, 0x85ebca6b); x ^= x >>> 13; x = Math.imul(x, 0xc2b2ae35); x ^= x >>> 16; return x >>> 0; };
const leaf = (a, s, e) => ({ a, s, e, n: e - s });
const isLeaf = t => t.a !== undefined;
const node = (l, r, p) => ({ l, r, p, n: l.n + r.n });
// join two sequences at a gap of priority p: the higher priority roots (no rotation: the shape is the priorities'); two leaves
// that meet with B or fewer elements between them become one
const fuse = (a, b) => { const c = new Array(a.n + b.n); let k = 0; for (let i = a.s; i < a.e; i++) c[k++] = a.a[i]; for (let i = b.s; i < b.e; i++) c[k++] = b.a[i]; return leaf(c, 0, c.length); };
const lastLeaf = t => { while (!isLeaf(t)) t = t.r; return t; };
const firstLeaf = t => { while (!isLeaf(t)) t = t.l; return t; };
// a small leaf put into the leaf at the other's edge, when there is room: a copy of at most B elements and the path to it, no
// new gap, so the shape the priorities determine is unchanged
const intoLast = (t, b) => isLeaf(t) ? fuse(t, b) : node(t.l, intoLast(t.r, b), t.p);
const intoFirst = (a, t) => isLeaf(t) ? fuse(a, t) : node(intoFirst(a, t.l), t.r, t.p);
function join(a, b, p) {
  if (a === null) return b; if (b === null) return a;
  if (isLeaf(b) && b.n < B && lastLeaf(a).n + b.n <= B) return intoLast(a, b);
  if (isLeaf(a) && a.n < B && firstLeaf(b).n + a.n <= B) return intoFirst(a, b);
  if (isLeaf(a) && isLeaf(b)) return node(a, b, p);
  if (!isLeaf(a) && (isLeaf(b) || a.p >= b.p) && a.p >= p) return node(a.l, join(a.r, b, p), a.p);
  if (!isLeaf(b) && (isLeaf(a) || b.p > a.p) && b.p > p) return node(join(a, b.l, p), b.r, b.p);
  return node(a, b, p);
}
// split at position i: [the first i elements, the rest]; a leaf splits into two views of its array, no copy
function split(t, i) {
  if (t === null) return [null, null];
  if (isLeaf(t)) { if (i <= 0) return [null, t]; if (i >= t.n) return [t, null]; return [leaf(t.a, t.s, t.s + i), leaf(t.a, t.s + i, t.e)]; }
  if (i <= t.l.n) { const [a, b] = split(t.l, i); return [a, b === null ? t.r : t.r === null ? b : node(b, t.r, t.p)]; }
  const [a, b] = split(t.r, i - t.l.n); return [a === null ? t.l : node(t.l, a, t.p), b];
}
const S = {
  name: "seq: a treap over array views",
  from: arr => arr.length ? leaf(arr, 0, arr.length) : null,
  insert: (t, i, x) => { const [a, b] = split(t, i); return join(join(a, leaf([x], 0, 1), prio()), b, prio()); },
  append: (t, x) => join(t, leaf([x], 0, 1), prio()),
  get: (t, i) => { for (;;) { if (isLeaf(t)) return t.a[t.s + i]; if (i < t.l.n) t = t.l; else { i -= t.l.n; t = t.r; } } },
  // (a walk with a stack of its own, the left side taken at once: half the calls of a recursive walk)
  sum: t => { let s = 0; if (t === null) return s; const st = []; for (;;) { while (!isLeaf(t)) { st.push(t.r); t = t.l; } const a = t.a; for (let i = t.s; i < t.e; i++) s += a[i]; if (!st.length) return s; t = st.pop(); } },
  out: t => { if (t === null) return []; if (isLeaf(t) && t.s === 0 && t.e === t.a.length) return t.a; const a = new Array(t.n); let k = 0; const go = t => { if (isLeaf(t)) { for (let i = t.s; i < t.e; i++) a[k++] = t.a[i]; } else { go(t.l); go(t.r); } }; go(t); return a; },
  depth: t => t === null || isLeaf(t) ? 1 : 1 + Math.max(S.depth(t.l), S.depth(t.r)),
  leaves: t => t === null ? 0 : isLeaf(t) ? 1 : S.leaves(t.l) + S.leaves(t.r),
};

// ---- the libraries, when given
const LIBWAYS = [];
if (LIBS) {
  const req = createRequire(path.resolve(LIBS, "package.json"));
  const Im = req("immutable"), F = req("@funkia/list");
  LIBWAYS.push({
    name: "Immutable.js List", version: req("immutable/package.json").version,
    from: arr => Im.List(arr), insert: (l, i, x) => l.insert(i, x), append: (l, x) => l.push(x), get: (l, i) => l.get(i),
    sum: l => l.reduce((s, x) => s + x, 0), out: l => l.toArray(),
  }, {
    name: "@funkia/list", version: req("@funkia/list/package.json").version,
    from: arr => F.fromArray(arr), insert: (l, i, x) => { const [a, b] = F.splitAt(i, l); return F.concat(F.append(x, a), b); }, append: (l, x) => F.append(x, l), get: (l, i) => F.nth(i, l),
    sum: l => F.foldl((s, x) => s + x, 0, l), out: l => F.toArray(l),
  });
}
const WAYS = [A, L, H, S, ...LIBWAYS];

// ---- correctness first: every way, the same edits, the same sequence
{
  const base = Array.from({ length: 500 }, (_, i) => i);
  const vs = WAYS.map(w => w.from(base));
  const ref = base.slice();
  for (let k = 0; k < 2000; k++) {
    const i = rnd(ref.length + 1), x = 10000 + k, app = k % 7 === 0;
    if (app) ref.push(x); else ref.splice(i, 0, x);
    // (a library that throws is left out of the timings, and the run says so)
    WAYS.forEach((w, j) => { if (w.failed) return; try { vs[j] = app ? w.append(vs[j], x) : w.insert(vs[j], i, x); } catch (e) { w.failed = `after ${k} edits: ${e && e.message || e}`; console.log(`${w.name}: left out, it threw ${w.failed}`); } });
  }
  WAYS.forEach((w, j) => { if (w.failed) return; const got = w.out(vs[j]); if (got.length !== ref.length || got.some((v, k) => v !== ref[k])) throw new Error(w.name + " differs"); });
  const old = S.from(base); S.insert(old, 3, -1); if (S.out(old).length !== 500) throw new Error("seq changed in place");
  console.log(`the same sequence every way after 2,000 edits; the seq: ${vs[3].n} elements, ${S.leaves(vs[3])} leaves, depth ${S.depth(vs[3])}`);
}

// ---- the timings
const SIZES = [1000, 10000, 100000, 1000000];
const rows = [];
for (const n of SIZES) {
  const page = Array.from({ length: n }, (_, i) => i);
  // a sequence that has been edited: the page's array, then n / 10 inserts at random places (so the seq has many leaves)
  const edited = w => { let v = w.from(page.slice()); for (let k = 0; k < Math.min(n / 10, 20000); k++) v = w.insert(v, rnd(n), -k); return v; };
  for (const w of WAYS.filter(w => !w.failed)) {
    // (an array and cells have one shape however they were made, so they are not edited first; the hybrid is, up to 10,000,
    // beyond which its edits cost minutes, so it is timed at its best there: one segment, the page's array)
    const fresh = w === A || w === L || (w === H && n > 10000);
    const v = fresh ? w.from(page) : edited(w);
    const r = { n, way: w.name };
    r.insert = clock(() => keep(w.insert(v, rnd(n), 7)));
    r.append = clock(() => keep(w.append(v, 7)));
    r.get = clock(() => keep(w.get(v, rnd(n))));
    r.sum = clock(() => keep(w.sum(v)));
    r.inOut = clock(() => keep(w.out(w.from(page)).length));
    if (w === S) { r.leaves = S.leaves(v); r.depth = S.depth(v); }
    rows.push(r);
    console.log(`${n.toLocaleString()} ${w.name}: insert ${fmt(r.insert)}, append ${fmt(r.append)}, get ${fmt(r.get)}, walk ${fmt(r.sum)}, page in and out ${fmt(r.inOut)}` + (w === S ? ` (${r.leaves} leaves, depth ${r.depth})` : "") + (w === H && fresh ? " (one segment, not edited first)" : ""));
    r.editedFirst = !fresh;
  }
}
function fmt(ns) { return ns < 1000 ? `${ns.toFixed(0)} ns` : ns < 1e6 ? `${(ns / 1000).toFixed(1)} µs` : `${(ns / 1e6).toFixed(1)} ms`; }
let machine = {}; try { machine = { cpus: os.cpus().length, model: os.cpus()[0].model, node: process.version }; } catch (e) { /* */ }
if (OUT) writeFileSync(OUT, JSON.stringify({ when: new Date().toISOString(), machine, B, libs: LIBWAYS.map(w => ({ name: w.name, version: w.version, failed: w.failed || null })), rows, sink }, null, 1));
