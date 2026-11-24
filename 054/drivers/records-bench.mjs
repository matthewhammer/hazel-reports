// ^report(54), ^ticket(847): records the page's way. hazel-jit's compiled code holds a labeled tuple, (x = 1, y = 2), as an
// array carrying its labels ([1, 2] with .x and .y), and a page holds an object, {x: 1, y: 2}. This times the ways a record
// could be held, in JavaScript alone (no Hazel build): each operation as hazel-jit's code does it today, and as it would with
// a record held as the page's object.
//
//   make      a record of four fields: today $R.tup([..], [labels]) (the runtime's tup, which adds each label to the array),
//             against an object literal
//   read      one field by label, r.vx, summed over 1,000 records
//   position  one field by position (a pattern (a, b, c, d) against a record): today r[2]; an object has no index, so
//             Object.values(r)[2], or the label at that position when the type gives it (r.vx)
//   update    a record with one field changed, as compiled code builds it from the old one's fields
//   equal     two equal records compared: today's $R.eq (arrays) against one that compares an object's own keys
//   cross     a page's array of 1,000,000 records into compiled code and back: today each record converted both ways;
//             held as the page's, nothing to do, or one pass checking each field's type (an Int a whole number) and no copy
//   cells     telling a list's cells and a constructor from a record, if a record is a plain object: today a cell is
//             {h, t}, and a record with fields h and t would look the same; with cells made by a class, instanceof tells
//             them apart; or with a cell's fields named $h and $t (a label beginning with $ is already kept under "$" ++ label,
//             so no record has such a key), a plain literal still. A list of 1,000 built and walked, each way.
//
//   node records-bench.mjs <out.json>
import { writeFileSync } from "node:fs";
import os from "node:os";
const OUT = process.argv[2];
const now = () => performance.now();
const median = xs => { const s = [...xs].sort((a, b) => a - b); return s[s.length >> 1]; };
// the median of batches (as many calls as take at least 2 ms), at least 9 batches and 200 ms; ns a call
function clock(f) {
  for (let i = 0; i < 50; i++) f();
  let batch = 1; while (batch < 1 << 22) { const t = now(); for (let i = 0; i < batch; i++) f(); if (now() - t >= 2) break; batch *= 2; }
  const per = [], start = now();
  while (per.length < 9 || (now() - start < 200 && per.length < 80)) { const t = now(); for (let i = 0; i < batch; i++) f(); per.push((now() - t) / batch * 1e6); }
  return median(per);
}
let sink = 0;
const keep = x => { sink = (sink + (typeof x === "number" ? x : x ? 1 : 0)) | 0; };

// ---- hazel-jit's runtime, as it is (HazelJit.Runtime.source on hazeljs a97b6f7465)
const R = {
  tup(vs, ls) { for (let i = 0; i < ls.length; i++) if (ls[i] !== null) vs[ls[i]] = vs[i]; return vs; },
  eq(a, b) {
    if (a === b) return true;
    if (a === null || b === null || typeof a !== "object" || typeof b !== "object") return false;
    if (Array.isArray(a)) { if (!Array.isArray(b) || a.length !== b.length) return false;
      for (let i = 0; i < a.length; i++) if (!this.eq(a[i], b[i])) return false; return true; }
    if ("c" in a) return ("c" in b) && a.c === b.c && this.eq(a.v, b.v);
    let p = a, q = b;
    while (p !== null && q !== null) { if (!this.eq(p.h, q.h)) return false; p = p.t; q = q.t; }
    return p === q;
  },
};
// ---- the same, with records as objects: cells and constructors made by classes, so a plain object is a record
class Cell { constructor(h, t) { this.h = h; this.t = t; } }
class Ctor { constructor(c, v) { this.c = c; this.v = v; } }
const O = {
  eq(a, b) {
    if (a === b) return true;
    if (a === null || b === null || typeof a !== "object" || typeof b !== "object") return false;
    if (Array.isArray(a)) { if (!Array.isArray(b) || a.length !== b.length) return false;
      for (let i = 0; i < a.length; i++) if (!this.eq(a[i], b[i])) return false; return true; }
    if (a instanceof Ctor) return b instanceof Ctor && a.c === b.c && this.eq(a.v, b.v);
    if (a instanceof Cell) { let p = a, q = b;
      while (p instanceof Cell && q instanceof Cell) { if (!this.eq(p.h, q.h)) return false; p = p.t; q = q.t; }
      return p === q; }
    for (const k in a) if (!(k in b) || !this.eq(a[k], b[k])) return false;   // a record: the same type, so the same keys
    return true;
  },
  at(r, i) { return Object.values(r)[i]; },
};
const L = ["x", "y", "vx", "vy"];
const N = 1000;
const nums = Array.from({ length: N * 4 }, (_, i) => (i * 7919) % 1000);
const asTup = Array.from({ length: N }, (_, i) => R.tup([nums[4 * i], nums[4 * i + 1], nums[4 * i + 2], nums[4 * i + 3]], L.slice()));
const asObj = Array.from({ length: N }, (_, i) => ({ x: nums[4 * i], y: nums[4 * i + 1], vx: nums[4 * i + 2], vy: nums[4 * i + 3] }));
let j = 0;
const rows = [];
const row = (name, today, objects, extra = {}) => {
  const r = { name, today: clock(today), objects: clock(objects) };
  for (const [k, f] of Object.entries(extra)) r[k] = clock(f);
  rows.push(r);
  console.log(`${name}: today ${r.today.toFixed(1)} ns, as objects ${r.objects.toFixed(1)} ns` + Object.keys(extra).map(k => `, ${k} ${r[k].toFixed(1)} ns`).join(""));
};
row("make a record of four fields",
  () => { j = (j + 1) & 1023; keep(R.tup([nums[j], nums[j + 1], nums[j + 2], nums[j + 3]], ["x", "y", "vx", "vy"]).length); },
  () => { j = (j + 1) & 1023; keep(({ x: nums[j], y: nums[j + 1], vx: nums[j + 2], vy: nums[j + 3] }).x); });
row("read a field by label, 1,000 records",
  () => { let s = 0; for (let i = 0; i < N; i++) s += asTup[i].vx; keep(s); },
  () => { let s = 0; for (let i = 0; i < N; i++) s += asObj[i].vx; keep(s); });
row("read a field by position, 1,000 records",
  () => { let s = 0; for (let i = 0; i < N; i++) s += asTup[i][2]; keep(s); },
  () => { let s = 0; for (let i = 0; i < N; i++) s += O.at(asObj[i], 2); keep(s); },
  { "as objects, the label from the type": () => { let s = 0; for (let i = 0; i < N; i++) s += asObj[i].vx; keep(s); } });
row("update one field",
  () => { j = (j + 1) % N; const r = asTup[j]; keep(R.tup([r.x + 1, r.y, r.vx, r.vy], ["x", "y", "vx", "vy"]).length); },
  () => { j = (j + 1) % N; const r = asObj[j]; keep(({ x: r.x + 1, y: r.y, vx: r.vx, vy: r.vy }).x); },
  { "as objects, by spread": () => { j = (j + 1) % N; const r = asObj[j]; keep(({ ...r, x: r.x + 1 }).x); } });
const tupB = asTup.map(r => R.tup([r[0], r[1], r[2], r[3]], L.slice())), objB = asObj.map(r => ({ ...r }));
const eqRec = (a, b) => a === b || (a.x === b.x && a.y === b.y && a.vx === b.vx && a.vy === b.vy);   // made from the type: (x: Int, y: Int, vx: Int, vy: Int)
row("compare two equal records",
  () => { j = (j + 1) % N; keep(R.eq(asTup[j], tupB[j])); },
  () => { j = (j + 1) % N; keep(O.eq(asObj[j], objB[j])); },
  { "as objects, compared by the type's fields": () => { j = (j + 1) % N; keep(eqRec(asObj[j], objB[j])); } });

// ---- a page's array of a million records, in and back out (the identity), ms
const M = 1000000;
const page = Array.from({ length: M }, (_, i) => ({ x: i, y: i + 1, vx: i & 7, vy: i & 3 }));
const once = f => { const ts = []; for (let k = 0; k < 5; k++) { const t = now(); keep(f().length); ts.push(now() - t); } return median(ts); };
const recIn = o => R.tup([o.x, o.y, o.vx, o.vy], ["x", "y", "vx", "vy"]), recOut = a => ({ x: a[0], y: a[1], vx: a[2], vy: a[3] });
const isInt = x => typeof x === "number" ? Number.isSafeInteger(x) : typeof x === "bigint";
const check = o => { if (!isInt(o.x) || !isInt(o.y) || !isInt(o.vx) || !isInt(o.vy)) throw new Error("not a record of Ints"); return o; };
const cross = {
  "today: each record converted both ways": once(() => page.map(recIn).map(recOut)),
  "as objects: nothing done": once(() => page),
  "as objects: each field's type checked going in, no copy": once(() => { for (let i = 0; i < M; i++) check(page[i]); return page; }),
};
for (const [k, v] of Object.entries(cross)) console.log(`a million records in and out, ${k}: ${v.toFixed(2)} ms`);

// ---- cells: literals against class instances, a list of 1,000 built and walked; and telling one from a record
const build = mk => () => { let l = null; for (let i = 0; i < N; i++) l = mk(i, l); keep(l.h); };
const walk = (l, test) => () => { let s = 0; for (let p = l; test(p); p = p.t) s += p.h; keep(s); };
const CellP = {};
let litL = null, clsL = null, dolL = null; for (let i = 0; i < N; i++) { litL = { h: i, t: litL }; clsL = new Cell(i, clsL); dolL = { $h: i, $t: dolL }; }
const walkD = (l, test) => () => { let s = 0; for (let p = l; test(p); p = p.$t) s += p.$h; keep(s); };
const CELLS = {
  "build, literals {h, t}": () => clock(build((h, t) => ({ h, t }))),
  "build, class instances": () => clock(build((h, t) => new Cell(h, t))),
  "walk, literals, p !== null": () => clock(walk(litL, p => p !== null)),
  "walk, class instances, p !== null": () => clock(walk(clsL, p => p !== null)),
  "walk, class instances, p instanceof Cell": () => clock(walk(clsL, p => p instanceof Cell)),
  "build, literals {$h, $t}": () => clock(build((h, t) => ({ $h: h, $t: t }))),
  "walk, literals {$h, $t}, p !== null": () => clock(walkD(dolL, p => p !== null)),
  "build, literals with a prototype {__proto__, h, t}": () => clock(build((h, t) => ({ __proto__: CellP, h, t }))),
};
// (the variants in a different order each round, five rounds, the median: one after another, the later ones ran under more
// of the collector's work and came out slower whatever they were)
const cells = {}; { const names = Object.keys(CELLS), got = Object.fromEntries(names.map(k => [k, []]));
  for (let round = 0; round < 5; round++) for (let k = 0; k < names.length; k++) { const n = names[(k + round * 3) % names.length]; got[n].push(CELLS[n]()); }
  for (const n of names) cells[n] = median(got[n]); }
for (const [k, v] of Object.entries(cells)) console.log(`a list of 1,000, ${k}: ${(v / 1000).toFixed(2)} µs`);

let machine = {}; try { machine = { cpus: os.cpus().length, model: os.cpus()[0].model, node: process.version }; } catch (e) { /* */ }
if (OUT) writeFileSync(OUT, JSON.stringify({ when: new Date().toISOString(), machine, rows, crossMs: cross, cellsNs: cells, sink }, null, 1));
