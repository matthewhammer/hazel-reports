// hazeljs-examples: every game's rules timed four ways with the hazeljs package at one build (ticket 795, for the Hazel
// reports' report 63, "The hazeljs package, and what to decide next"):
//
//   interpreted  the package's interpreter: Hazel.runProgram builds the rules and its functions run them
//   jit          the package's compiler, run in the page: Hazel.jitProgram compiles the rules to JavaScript and runs them;
//                every call's arguments and answer cross through Hazel's own values (the library's way across)
//   compiled     the same compiler's JavaScript, ahead of time: Hazel.compileProgram's program and runtime, wrapped the way
//                the page wraps them (<game>/compiled.js, with its hand-written converters for the game's values)
//   plain JS     the same game written by hand in JavaScript (<game>/plain.js; five games have one)
//
// Each operation is timed on positions made by the compiled rules from a seeded game, and every way's answer is compared
// with the compiled one. The clock is node/three-way.mjs's (report 60): a call too fast for the clock is timed in batches
// (as many calls as take at least a millisecond), and the median of the batches taken, per call; the interpreter at least
// 3 times and for at least 1.5 s, the others at least 30 times and for at least 0.3 s.
//
//   node node/package-bench.mjs <game> <hazeljs package dir> [out.json] [--quick]
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { execSync } from "node:child_process";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

const QUICK = process.argv.includes("--quick");
// (^report(54)) --no-interpreted: the jit and the compiled ways only, for a second build of the same package on the same
// machine (its interpreter is the first build's)
const NO_INTERP = process.argv.includes("--no-interpreted");
const args = process.argv.slice(2).filter(a => !a.startsWith("--"));
const [GAME, PKG, OUT] = args;
if (!GAME || !PKG) { console.log("usage: node node/package-bench.mjs <game> <hazeljs package dir> [out.json] [--quick]"); process.exit(2); }
const Hazel = (await import(pathToFileURL(path.resolve(PKG, "index.mjs")).href)).default;
const pkgJson = JSON.parse(readFileSync(path.resolve(PKG, "package.json"), "utf8"));

const SETUP = {
  "i-ching": { modules: ["Lines", "Casting", "Book", "Reading"], tail: "(cast = Casting.cast, reading = Reading.reading)" },
  "tarot": { modules: ["Deck", "Spreads", "Reading"], tail: "(deal = Reading.deal)" },
  "astrology": { modules: ["Zodiac", "Aspects", "Chart", "Orbit", "MoonOrbit", "Planets", "Outer", "PlutoOrbit", "Sky", "Wheel", "Reading"], tail: "(reading = Reading.reading)" },
  "checkers": { modules: ["Checkers"], tail: "(start = Checkers.start, moves = Checkers.moves, apply = Checkers.apply, choose = Checkers.choose)" },
  "go": { modules: ["Go"], tail: "(fresh = Go.fresh, play = Go.play, pass = Go.pass, score = Go.score, choose = Go.choose)" },
  "minesweeper": { modules: ["Board", "Play", "Hint", "Guess"], tail: "(fresh = Board.fresh, lay = Board.lay_mines, reveal = Play.reveal, flag = Play.flag, chord = Play.chord, flags = Play.flags, sure = Hint.sure, pick = Guess.pick)" },
  "mahjong": { modules: ["Mahjong"], tail: "(start = Mahjong.start, step = Mahjong.step, options = Mahjong.options, next_hand = Mahjong.next_hand)" },
  "solitaire": { modules: ["Cards", "Deal", "Moves"], tail: "(deal = Deal.deal, moves = Moves.moves, moves_from = Moves.moves_from, apply = Moves.apply, won = Moves.won)" },
  "mahjong-solitaire": { modules: ["MahjongSolitaire"], tail: "(deal = MahjongSolitaire.deal, take = MahjongSolitaire.take, frees = MahjongSolitaire.free_places, pairs = MahjongSolitaire.pairs, best = MahjongSolitaire.best, shuffle = MahjongSolitaire.shuffle, places = MahjongSolitaire.layout, won = MahjongSolitaire.won)" },
  "pinball": { modules: ["Pinball"], tail: "(start = Pinball.start, step = Pinball.step, board = Pinball.board)" },
  "downhill": { modules: ["Downhill"], tail: "(start = Downhill.start, step = Downhill.step, course = Downhill.course, robot = Downhill.robot)" },
  "bricks": { modules: ["Bricks"], tail: "(start = Bricks.start, step = Bricks.step, layout = Bricks.layout, robot = Bricks.robot)" },
  "snake": { modules: ["Snake"], tail: "(start = Snake.start, step = Snake.step, robot = Snake.robot)" },
  "trails": { modules: ["Trails"], tail: "(start = Trails.start, step = Trails.step, robot = Trails.robot)" },
  "starwave": { modules: ["StarWave"], tail: "(start = StarWave.start, step = StarWave.step, robot = StarWave.robot)" },
  "bugs": { modules: ["Bugs"], tail: "(start = Bugs.start, step = Bugs.step, robot = Bugs.robot)" },
  "dig": { modules: ["Dig", "Scene"], tail: "(start = Dig.start, step = Dig.step, robot = Dig.robot, scene = Scene.scene, landing = Scene.landing)" },
}[GAME];
if (!SETUP) { console.log("no such game: " + GAME); process.exit(2); }

const file = f => readFileSync(new URL(`../${GAME}/${f}`, import.meta.url), "utf8");
const read = m => file(`rules/${m}.hz`).replace(/\s+$/, "");
const spec = { preamble: read("preamble"), modules: SETUP.modules.map(name => ({ name, text: read(name) })), tail: SETUP.tail };
const script = text => { const b = { exports: {} }; new Function("module", "window", text)(b, undefined); return b.exports; };
const now = () => performance.now();

// astrology: the interpreter's way is the page's, the whole program built with a reading as its tail (built with its function
// as the answer, that answer grows past gigabytes, hazelgrove/hazel#2832); the jit and the compiled ways call reading
const six = x => Number((x < 0 ? "-" : "") + Math.abs(x).toFixed(6));
const BIRTH = { year: 2026, month: 11, day: 17, hour: six(18 + 3 / 60 + 51 / 3600) }, DAY = { year: 2026, month: 11, day: 18, hour: 12 };
const SITE = { latitude: 40.046313, longitude: -105.286695 };
const lit = m => `(year = ${m.year}, month = ${m.month}, day = ${m.day}, hour = ${m.hour.toFixed(6)})`;
const ONE_READING = `Reading.reading(${lit(BIRTH)}, (latitude = ${SITE.latitude.toFixed(6)}, longitude = ${SITE.longitude.toFixed(6)}), ${lit(DAY)})`;
const runSpec = GAME === "astrology" ? { ...spec, tail: ONE_READING } : spec;

// ---- the one-time costs, and the four ways
const once = {};
let t = now(); const built = NO_INTERP ? { ok: true, value: null } : Hazel.runProgram(runSpec); once.interpretedBuildMs = NO_INTERP ? null : now() - t;
if (!built.ok) { console.log("the interpreter did not build the rules", JSON.stringify(built.errors).slice(0, 500)); process.exit(1); }
t = now(); const jitted = Hazel.jitProgram(spec); once.jitBuildMs = now() - t;
once.jitCompiled = jitted.compiled; once.jitReason = jitted.reason || null;
t = now(); const comp = Hazel.compileProgram(spec); once.compileMs = now() - t;
if (!comp.compiled) { console.log("compileProgram did not compile the rules: " + comp.reason); process.exit(1); }
once.compiledJsBytes = comp.js.length; once.runtimeBytes = comp.runtime.length;
// the page's compiled.js, its program and runtime replaced by the package's: the converters are the page's own
const page = file("compiled.js");
const RT = "  const $R = (", PROG = "  const P = (function ($R) {\n", END = "\n  })($R);\n  // ---- values across";
const a = page.indexOf(RT), b = page.indexOf(PROG), c = page.indexOf(END);
if (a < 0 || b < a || c < b) { console.log("compiled.js is not as expected"); process.exit(1); }
const pageMade = (page.match(/hazelgrove\/hazel ([0-9a-f]{7,40})/) || [])[1] || null;
let ours = page.slice(0, a) + RT + comp.runtime + ");\n" + PROG + comp.js + page.slice(c);
// (^report(54)) a runtime whose lists may be segments of arrays: the page's two list converters as segments (a copy of
// the page's array, which the page may change later; a slice is one native copy, no cells)
const SEGMENTS = comp.runtime.includes("seg(a)");
once.listShape = SEGMENTS ? "hybrid" : "cells";
if (SEGMENTS) {
  const L = "  const list = xs => { let r = null; for (let i = xs.length - 1; i >= 0; i--) r = { h: xs[i], t: r }; return r; };";
  const A = "  const array = l => { const out = []; for (let p = l; p !== null; p = p.t) out.push(p.h); return out; };";
  if (!ours.includes(L) || !ours.includes(A)) { console.log("compiled.js's list converters are not as expected"); process.exit(1); }
  ours = ours.replace(L, "  const list = xs => $R.seg(xs.slice());").replace(A, "  const array = l => $R.arr(l).slice();");
}
once.wrappedBytes = ours.length; once.pageCompiledFrom = pageMade;
t = now(); const C = script(ours); once.compiledLoadMs = now() - t;
const P = existsSync(new URL(`../${GAME}/plain.js`, import.meta.url)) ? script(file("plain.js")) : null;
const WAYS = [...(NO_INTERP ? [] : [["interpreted", built.value]]), ["jit", jitted.value], ["compiled", C], ...(P ? [["plain JS", P]] : [])];

// ---- the clock (node/three-way.mjs's)
const median = xs => { const s = [...xs].sort((x, y) => x - y); return s.length % 2 ? s[(s.length - 1) / 2] : (s[s.length / 2 - 1] + s[s.length / 2]) / 2; };
function clock(f, slow) {
  const minMs = (slow ? 1500 : 300) * (QUICK ? 0.1 : 1), minReps = QUICK ? 2 : slow ? 3 : 30, maxReps = slow ? 15 : 100000;
  let batch = 1;
  for (let w = 0; w < (slow ? 1 : 20); w++) f();
  if (!slow) for (;;) { const t0 = now(); for (let i = 0; i < batch; i++) f(); if (now() - t0 >= 1 || batch >= 1 << 20) break; batch *= 2; }
  const per = [];
  const start = now();
  while (per.length < maxReps && (per.length < minReps || now() - start < minMs)) {
    const t0 = now(); for (let i = 0; i < batch; i++) f(); per.push((now() - t0) / batch);
  }
  return { ms: median(per), min: Math.min(...per), reps: per.length, batch };
}
// answers: numbers to a relative 1e-9 (astrology's floats), everything else exactly
const differs = (x, y) => {
  if (typeof x === "number" && typeof y === "number") return Math.abs(x - y) / Math.max(1, Math.abs(x)) > 1e-9;
  if (Array.isArray(x) && Array.isArray(y)) return x.length !== y.length || x.some((v, i) => differs(v, y[i]));
  if (x && y && typeof x === "object" && typeof y === "object") { const ks = Object.keys(x).sort(), ls = Object.keys(y).sort(); return ks.join() !== ls.join() || ks.some(k => differs(x[k], y[k])); }
  return x !== y;
};
let seed = 7; const draw = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const ints = (n, k) => Array.from({ length: n }, () => Math.floor(draw() * k));

const ops = [];
// an operation, timed each way; `skip` names ways not timed (too slow to time, or not there)
function op(name, call, opts = {}) {
  const row = { name, ways: {} };
  const want = call(C);
  for (const [way, impl] of WAYS) {
    if ((opts.skip || []).includes(way)) { row.ways[way] = null; continue; }
    try {
      const got = call(impl);
      const r = clock(() => call(impl), way === "interpreted");
      r.same = !differs(got, want);
      row.ways[way] = r;
    } catch (e) { row.ways[way] = { error: String(e && e.message || e).slice(0, 300) }; }
  }
  ops.push(row);
  const show = w => { const r = row.ways[w]; return r == null ? "-" : r.error ? "error" : (r.ms < 0.01 ? (r.ms * 1000).toFixed(2) + " us" : r.ms.toFixed(r.ms < 1 ? 4 : 1) + " ms") + (r.same ? "" : " (DIFFERS)"); };
  console.log(`${name}: ${WAYS.map(([w]) => `${w} ${show(w)}`).join(", ")}`);
}

// ---- each game's operations (compare-compiled.mjs's timed ones), on positions the compiled rules make
if (GAME === "i-ching") {
  const TAGS = ["YoungYin", "YoungYang", "OldYin", "OldYang"], six = [0, 1, 2, 3, 4, 5].map(i => ({ tag: TAGS[i % 4] }));
  op("a cast by coins", e => e.cast({ tag: "Coins" }, 0.3, 0.6, 0.1));
  op("a cast by yarrow", e => e.cast({ tag: "Yarrow" }, 0.3, 0.6, 0.1));
  op("a reading", e => e.reading(six));
} else if (GAME === "tarot") {
  const us = Array.from({ length: 40 }, draw);
  for (const s of [{ tag: "One" }, { tag: "CelticCross" }, { tag: "YearAhead", value: { start: 10, theme: true } }])
    op(`a deal, ${s.tag}`, e => e.deal(s, us, true));
} else if (GAME === "astrology") {
  if (!NO_INTERP) WAYS[0][1] = { reading: () => { const r = Hazel.runProgram(runSpec); if (!r.ok) throw new Error("not built"); return r.value; } };
  op("a chart (interpreted: the whole program built each time)", e => e.reading(BIRTH, SITE, DAY));
} else if (GAME === "checkers") {
  let g = C.start; for (let i = 0; i < 8; i++) { const ms = C.moves(g); g = C.apply(g, ms[Math.floor(draw() * ms.length)]); }
  const rs = ints(48, 1000);
  op("the moves", e => e.moves(g));
  for (const d of [1, 2, 3, 4]) op(`Hazel's move, looking ${d} ahead`, e => e.choose(g, d, rs));
} else if (GAME === "go") {
  let g = C.fresh(9); for (const p of [40, 20, 60]) { g = C.play(g, p); const w = C.choose(g, Array(81).fill(3)); g = w < 0 ? C.pass(g) : C.play(g, w); }
  const rs = ints(81, 20);
  op("a move played", e => e.play(g, 30));
  op("Hazel's choice of move", e => e.choose(g, rs));
  op("the score", e => e.score(g));
} else if (GAME === "minesweeper") {
  for (const [rows, cols, mines] of [[9, 9, 10], [16, 30, 99]]) {
    const us = Array.from({ length: rows * cols }, draw), r0 = Math.floor(rows / 2), c0 = Math.floor(cols / 2);
    const g = C.reveal(C.lay(rows, cols, mines, us, r0, c0), r0, c0);
    op(`${rows} by ${cols}: the mines laid`, e => e.lay(rows, cols, mines, us, r0, c0));
    op(`${rows} by ${cols}: a cell opened`, e => e.reveal(g, 0, 0));
    op(`${rows} by ${cols}: the hint (a sure move)`, e => e.sure(g));
  }
} else if (GAME === "mahjong") {
  const NONE = { kind: 0, tile: -1 }, r = ints(136, 1e6);
  let g = C.start(r); for (let i = 0; i < 12; i++) g = C.step(g, NONE);
  op("a hand dealt", e => e.start(r));
  op("a step", e => e.step(g, NONE));
  op("your options", e => e.options(g));
} else if (GAME === "solitaire") {
  const us = Array.from({ length: 52 }, draw), g = C.deal(us, 1), m = C.moves(g)[0];
  op("a deal", e => e.deal(us, 1));
  op("every legal move", e => e.moves(g));
  op("a move made", e => e.apply(g, m));
} else if (GAME === "mahjong-solitaire") {
  const g = C.deal(0, 31337);
  op("a deal", e => e.deal(0, 31337));
  op("Hazel's choice of pair", e => e.best(g));
} else if (GAME === "pinball") {
  const g = C.step(0, C.start(0), false, false, 60);
  op("a step", e => e.step(0, g, true, false, 0));
  op("a board", e => e.board(4));
} else if (GAME === "downhill") {
  const g = C.start(9, true);
  op("a step", e => e.step(g, 1, false));
  op("the robot's choice", e => e.robot(g));
} else if (GAME === "bricks") {
  const g = C.start(0, false);
  op("a step", e => e.step(g, 200, true));
  op("the robot's choice", e => e.robot(g));
} else if (GAME === "snake") {
  let g = C.start(5, false); for (let k = 0; k < 200 && !g.over; k++) g = C.step(g, C.robot(g));
  op("a step", e => e.step(g, 1));
  op(`the robot's choice (${g.body.length} long)`, e => e.robot(g));
} else if (GAME === "trails") {
  const g = C.start(0);
  op("a step", e => e.step(g, 1, 3));
  op("the robot's choice, looking 150", e => e.robot(g, 2, 150, 0, 50));
} else if (GAME === "starwave") {
  const g = C.start(7);
  op("a step", e => e.step(g, 1, true));
  op("the robot's choice", e => e.robot(g));
} else if (GAME === "bugs") {
  const g = C.start(7);
  op("a step", e => e.step(g, 1, 0, true));
  op("the robot's choice", e => e.robot(g));
} else if (GAME === "dig") {
  const g = C.start(7);
  op("a step", e => e.step(g, 2, false, false));
  op("the robot's choice", e => e.robot(g));
}

let machine = {};
try { machine = { cpus: os.cpus().length, model: os.cpus()[0].model, node: process.version, platform: `${os.platform()} ${os.release()}` }; } catch (e) { /* */ }
const out = {
  game: GAME, when: new Date().toISOString(), quick: QUICK, machine,
  package: { name: pkgJson.name, version: pkgJson.version, hazel: pkgJson.hazel || null, build: Hazel.build },
  examples: (() => { try { return execSync("git rev-parse HEAD", { cwd: new URL("..", import.meta.url) }).toString().trim(); } catch (e) { return null; } })(),
  once, ops,
};
console.log(`once: ${JSON.stringify(once)}`);
if (OUT) writeFileSync(OUT, JSON.stringify(out, null, 1));
const bad = ops.flatMap(o => Object.entries(o.ways).filter(([, r]) => r && (r.error || !r.same)).map(([w]) => `${o.name} (${w})`));
if (bad.length) { console.log("NOT THE SAME: " + bad.join("; ")); process.exit(1); }
