// ^report(54), Matthew 2026-11-23: "a page's array in and back out --- show me the data at various scales. Different array
// scales. This performance factor is a huge reason why we want arrays, and no conversion on the edges."
//
// A page hands Hazel code a list and gets it back (the identity function), at sizes 1 to 1,000,000, five ways:
//   arrays, no conversion     compiled code takes the page's array as its list and gives it back: nothing done at the edges
//   arrays, copied            one native copy each way (xs.slice()), in case the page changes its array later
//   cells, converted          today's ahead-of-time converters: the array made into {h, t} cells, and back into an array
//   through Hazel's values    today's jit through the hazeljs package (Hazel.jit): page -> Hazel values -> cells -> Hazel
//                             values -> page
//   the interpreter           Hazel.run: page -> Hazel values -> the interpreter's run -> page
// and, for scale, one pass over the list in compiled code (a map adding 1, cells), what a function might do with it.
// Each with a list of Ints, and of records (x = Int, y = Int), which compiled code holds as arrays carrying their labels
// and a page as objects: an array of records is no conversion only if the records' shape is the page's too.
//
//   node crossing-bench.mjs <hazeljs package dir> <out.json>
import { writeFileSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
const Hazel = (await import(pathToFileURL(path.resolve(process.argv[2], "index.mjs")).href)).default;
const OUT = process.argv[3];
const now = () => performance.now();
const median = xs => { const s = [...xs].sort((a, b) => a - b); return s[s.length >> 1]; };
// the median of batches (as many calls as take at least 2 ms), at least 7 batches and 150 ms; one call over 3 s: that one alone
function clock(f) {
  const t0 = now(); f(); const first = now() - t0;
  if (first > 3000) return { ms: first, reps: 1, batch: 1 };
  let batch = 1; while (batch < 1 << 20) { const t = now(); for (let i = 0; i < batch; i++) f(); if (now() - t >= 2) break; batch *= 2; }
  const per = [], start = now();
  while (per.length < 7 || (now() - start < 150 && per.length < 60)) { const t = now(); for (let i = 0; i < batch; i++) f(); per.push((now() - t) / batch); }
  return { ms: median(per), reps: per.length, batch };
}
// compiled code's shapes, as hazel-jit's runtime and the pages' converters have them
const toCells = (xs, f) => { let r = null; for (let i = xs.length - 1; i >= 0; i--) r = { h: f(xs[i]), t: r }; return r; };
const toArray = (l, f) => { const a = []; for (let p = l; p !== null; p = p.t) a.push(f(p.h)); return a; };
const recIn = o => { const a = [o.x, o.y]; a.x = a[0]; a.y = a[1]; return a; };   // a labeled tuple: an array carrying its labels
const recOut = a => ({ x: a[0], y: a[1] });
const id = x => x;
const mapCells = (l, f) => l === null ? null : { h: f(l.h), t: mapCells(l.t, f) };
const KINDS = {
  ints: { native: true, make: n => Array.from({ length: n }, (_, i) => i), elIn: id, elOut: id, hazelType: "[Int]", inc: x => x + 1 },
  records: { native: false, make: n => Array.from({ length: n }, (_, i) => ({ x: i, y: -i })), elIn: recIn, elOut: recOut, hazelType: "[(x = Int, y = Int)]",
    inc: r => { const a = [r[0] + 1, r[1]]; a.x = a[0]; a.y = a[1]; return a; } },
};
const SIZES = [1, 10, 100, 1000, 10000, 100000, 1000000];
const rows = [];
for (const [kind, K] of Object.entries(KINDS)) {
  const jitted = Hazel.jit(`fun (xs : ${K.hazelType}) -> xs`), run = Hazel.run(`fun (xs : ${K.hazelType}) -> xs`);
  if (!jitted.compiled) throw new Error("not compiled: " + jitted.reason);
  const J = jitted.value, I = run.value, gaveUp = new Set();
  // (Matthew: "the round trip of going from the outer JS main thread, into the JIT code, and back again, for each
  // representation") hazel-jit's own compiled identity, from the package's compile, called as a page calls it
  const comp = Hazel.compile(`fun (xs : ${K.hazelType}) -> xs`);
  if (!comp.compiled) throw new Error("not compiled: " + comp.reason);
  const R = new Function("return (" + comp.runtime + ")")();
  const F = new Function("$R", comp.js)(R);
  if (typeof F !== "function") throw new Error("the compiled value is not a function");
  for (const n of SIZES) {
    const xs = K.make(n), same = y => y.length === n && JSON.stringify(y[n >> 1]) === JSON.stringify(xs[n >> 1]);
    const ways = {
      "arrays, no conversion": () => F(xs),
      "arrays, copied": () => F(xs.slice()).slice(),
      "hybrid (cells + array segments)": () => { const l = F(n ? { a: K.native ? xs : xs.map(K.elIn), i: 0 } : null); return l === null ? [] : K.native ? l.a : l.a.map(K.elOut); },
      "cells, converted": () => toArray(F(toCells(xs, K.elIn)), K.elOut),
      "through Hazel's values (the jit)": () => J(xs),
      "the interpreter (Hazel.run)": () => I(xs),
    };
    if (kind === "records") ways["arrays of records, each converted"] = () => F(xs.map(K.elIn)).map(K.elOut);
    const row = { kind, n };
    for (const [w, f] of Object.entries(ways)) {
      if (gaveUp.has(w)) { row[w] = null; continue; }
      // (a million records through Hazel's values ran the heap past 2.5 GB, out of memory, on the first try)
      if (kind === "records" && n > 100000 && /Hazel|interpreter/.test(w)) { row[w] = null; row[w + " (skipped)"] = "past 2.5 GB of heap, out of memory"; continue; }
      try { const y = f(); if (!same(y)) throw new Error("not the same list back"); const r = clock(f); row[w] = r.ms; if (r.ms > 3000) gaveUp.add(w); }
      catch (e) { row[w] = null; row[w + " (error)"] = String(e.message || e).slice(0, 120); gaveUp.add(w); }
    }
    const cells = toCells(xs, K.elIn);
    const deep = n <= 10000;   // (the map is recursive, as compiled Hazel's is: much past 10,000 it overflows a stack)
    row["one pass in compiled code (a map, cells)"] = deep ? clock(() => mapCells(cells, K.inc)).ms : null;
    rows.push(row);
    writeFileSync(OUT, JSON.stringify({ when: new Date().toISOString(), node: process.version, package: { build: Hazel.build }, cpu: (await import("node:os")).cpus()[0].model, rows }, null, 1));
    const fmt = v => v == null ? "      -" : v < 0.001 ? `${(v * 1e6).toFixed(0)} ns` : v < 1 ? `${(v * 1000).toFixed(1)} us` : `${v.toFixed(1)} ms`;
    console.log(`${kind.padEnd(8)} n=${String(n).padStart(7)}  ` + Object.entries(row).filter(([k]) => !["kind", "n"].includes(k) && !k.endsWith("(error)") && !k.endsWith("(skipped)")).map(([k, v]) => `${k.split(" (")[0].split(",")[0]}${k.includes("copied") ? " copied" : k.includes("each") ? " each" : ""}: ${fmt(v)}`).join(" | "));
  }
}
writeFileSync(OUT, JSON.stringify({ when: new Date().toISOString(), node: process.version, package: { build: Hazel.build }, cpu: (await import("node:os")).cpus()[0].model, rows }, null, 1));
