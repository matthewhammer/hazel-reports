// ^report(54), ^ticket(847): run from hazeljs-examples' root (66cbf53, the games' rules as of 0.0.74), node <this file>
// each game's state as a page holds it, its nodes counted by kind: records (objects without a tag), constructors ({tag, value}),
// arrays (lists, or tuples without labels: the page cannot tell), and the scalars inside
import { readFileSync } from "node:fs";
const load = g => { const b = { exports: {} }; new Function("module", "window", readFileSync(`${g}/compiled.js`, "utf8"))(b, undefined); return b.exports; };
const count = (v, c = { rec: 0, recFields: 0, ctor: 0, arr: 0, arrEls: 0, scalar: 0 }) => {
  if (v === null || typeof v !== "object") { c.scalar++; return c; }
  if (Array.isArray(v)) { c.arr++; c.arrEls += v.length; v.forEach(x => count(x, c)); return c; }
  if ("tag" in v && Object.keys(v).every(k => k === "tag" || k === "value")) { c.ctor++; if ("value" in v) count(v.value, c); return c; }
  c.rec++; for (const k in v) { c.recFields++; count(v[k], c); } return c;
};
const S = {
  checkers: C => C.start, go: C => { let g = C.fresh(9); for (const p of [40, 20, 60, 30, 50]) g = C.play(g, p); return g; },
  minesweeper: C => { const us = Array.from({ length: 480 }, (_, i) => ((i * 7919) % 1000) / 1000); return C.reveal(C.lay(16, 30, 99, us, 8, 15), 8, 15); },
  mahjong: C => C.start(Array.from({ length: 136 }, (_, i) => (i * 7919) % 1000003)), solitaire: C => C.deal(Array.from({ length: 52 }, (_, i) => ((i * 7919) % 1000) / 1000), 1),
  "mahjong-solitaire": C => C.deal(0, 31337), pinball: C => C.start(0), downhill: C => C.start(9, true), bricks: C => C.start(0, false),
  snake: C => C.start(5, false), trails: C => C.start(0), starwave: C => C.start(42), bugs: C => C.start(42), dig: C => C.start(42),
};
for (const [g, f] of Object.entries(S)) {
  const c = count(f(load(g))), nodes = c.rec + c.ctor + c.arr;
  console.log(JSON.stringify({ game: g, ...c, recShare: +(c.rec / nodes).toFixed(2), recFieldShare: +(c.recFields / (c.recFields + c.arrEls)).toFixed(2) }));
}
