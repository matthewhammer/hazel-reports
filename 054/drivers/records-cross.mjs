// ^report(54), ^ticket(847), decision 1: a page's list of records (x = Int, y = Int) through Hazel.jit, idea A (a record a
// plain object in compiled code, trial/847-records-objects) against idea C (an array carrying its labels, hazeljs 0.0.12),
// one package per run (the converters' memo is the page's, shared by every copy of the library, so the two never share a
// process). At each size, 1 to 1,000,000:
//
//   fresh     a new list of new records each call (made off the clock), into the compiled identity and out: no memo helps
//   again     the same list handed back, as a page hands back what it got: the memo's way
//   sum       the x of every record summed in compiled code (the list made once): reading a field, an object's or an array's
//
//   node records-cross.mjs <hazeljs package dir> <out.json> <label>
import { writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";
const [PKG, OUT, LABEL] = process.argv.slice(2);
const Hazel = (await import(pathToFileURL(path.resolve(PKG, "index.mjs")).href)).default;
const now = () => performance.now();
const median = xs => { const s = [...xs].sort((a, b) => a - b); return s[s.length >> 1]; };
// ms a call: the median of at least 5 calls and 200 ms (a call over 2 s: three calls); `fresh` makes the input off the clock
function clock(f, make) {
  const per = [], start = now(); let one = 0;
  while (per.length < 3 || (per.length < 5 || now() - start < 200) && per.length < 200 && !(one > 2000)) { const x = make(); const t = now(); f(x); one = now() - t; per.push(one); }
  return median(per);
}
const T = "[(x = Int, y = Int)]";
const same = Hazel.jit(`let same : ${T} -> ${T} = fun xs -> xs in same`), sum = Hazel.jit(`let sum : ${T} -> Int = fun xs -> case xs | [] => 0 | p :: rest => p.x + sum(rest) end in sum`);
if (!same.compiled || !sum.compiled) { console.log("not compiled", same.reason, sum.reason); process.exit(1); }
const rec = i => ({ x: i, y: 2 * i });
const rows = [];
for (const n of [1, 10, 100, 1000, 10000, 100000, 1000000]) {
  const base = Array.from({ length: n }, (_, i) => rec(i));
  const fresh = clock(xs => same.value(xs), () => base.map(r => ({ x: r.x, y: r.y })));
  const again = clock(xs => same.value(xs), () => base);
  // (the sum recurses once an element: past 10,000 it overruns the process's stack)
  let s = null; try { s = n <= 10000 ? clock(xs => sum.value(xs), () => base) : null; } catch (e) { s = "threw: " + (e && e.message || e); }
  const back = same.value(base.map(r => ({ x: r.x, y: r.y })));
  const ok = back.length === n && (n === 0 || (back[n - 1].x === n - 1 && back[n - 1].y === 2 * (n - 1)));
  rows.push({ n, fresh, again, sum: s, ok, sameObjects: n > 0 && back[0] !== undefined ? null : null });
  console.log(`${LABEL} ${n.toLocaleString()}: fresh ${fresh.toFixed(4)} ms, again ${again.toFixed(4)} ms, sum ${typeof s === "number" ? s.toFixed(4) + " ms" : s}, answers ${ok ? "right" : "WRONG"}`);
}
// does a fresh record come back as the page's own object (idea A) or a copy (idea C)?
const one = [rec(1)], got = same.value(one);
const pageOwn = got[0] === one[0];
console.log(`${LABEL}: a record comes back as the page's own object: ${pageOwn}`);
let machine = {}; try { machine = { model: os.cpus()[0].model, node: process.version }; } catch (e) { /* */ }
writeFileSync(OUT, JSON.stringify({ label: LABEL, build: String(Hazel.build || ""), when: new Date().toISOString(), machine, pageOwn, rows }, null, 1));
