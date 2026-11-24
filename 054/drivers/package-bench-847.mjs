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
//   node node/package-bench.mjs <game> <hazeljs package dir> [out.json] [--quick] [--runs]
//
// (ticket 795, 2026-11-24) --runs times a game's own run of states in place of the single operations: see "a game's own run
// of states" below.
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { execSync } from "node:child_process";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

const QUICK = process.argv.includes("--quick"), RUNS = process.argv.includes("--runs") || process.argv.includes("--count-tuples"), COUNT = process.argv.includes("--count-tuples");
// (ticket 847, idea A against build 6) --aot-as-is: the ahead-of-time way is the game's own compiled.js as the site ships it,
// not the package's compileProgram in it (a package whose records are objects breaks the page's own converters, written for
// arrays); --no-interp: the interpreter not built nor timed
const AOT_AS_IS = process.argv.includes("--aot-as-is"), NO_INTERP = process.argv.includes("--no-interp");
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
// (--count-tuples, ticket 847: how many tuples the compiled rules make with every entry labeled, with some, as each game plays its run)
if (COUNT) { const at = ours.indexOf("tup(vs, ls) {"); if (at < 0) { console.log("no tup in the runtime"); process.exit(1); }
  ours = ours.slice(0, at) + 'tup(vs, ls) { const C = globalThis.$TC || (globalThis.$TC = { all: 0, some: 0 }); C[ls.every(l => l !== null) ? "all" : "some"]++;' + ours.slice(at + "tup(vs, ls) {".length); }
once.wrappedBytes = ours.length; once.pageCompiledFrom = pageMade;
t = now(); const C = script(AOT_AS_IS ? page : ours); once.compiledLoadMs = now() - t; once.aotAsIs = AOT_AS_IS;
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
if (RUNS) {
  // (--runs: the single operations are not timed; their runs are, below)
} else if (GAME === "i-ching") {
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

// ---- (ticket 795, 2026-11-24) a game's own run of states. The timings above call one operation again and again on one
// position, so from the second call on the jit's memos find that position already converted (the converted-closed invariant:
// a node met again was converted whole) and its crossing costs next to nothing. Here each way plays one run instead, from the
// same start, every call given what that way's previous call answered, as a page does. The run is recorded once by the
// compiled rules (the robot's choices with a press of chance now and then, or random legal moves), so every way makes the
// same calls with the same inputs, and every way's last state is compared with the compiled one's.
//
//   jit, fresh copies   the same run through the jit, every argument copied (structuredClone, off the clock) before each
//                       call, so no memo finds it and every call converts its arguments whole: a page that builds its own
//                       state each frame, and the most a crossing can cost
//
// The clock: each call timed alone (performance.now() before and after), summed over the run. The interpreter plays the run
// once; the others once to warm up, then again until at least 5 runs and 0.3 s (at most 50), and the median run is taken.
const runs = [];
const REC = n => QUICK ? Math.min(n, 40) : n;
const clockNs = (() => { const n = 100000, t0 = now(); for (let i = 0; i < n; i++) now(); return (now() - t0) / n * 1e6; })();
function player(e, fresh) {
  const p = { ms: 0, calls: 0 };
  p.call = (f, ...xs) => {
    if (fresh) xs = xs.map(x => x !== null && typeof x === "object" ? structuredClone(x) : x);
    const t0 = now(); const r = e[f](...xs); p.ms += now() - t0; p.calls++; return r;
  };
  return p;
}
function run(name, rec, replay) {
  if (COUNT) { const C = globalThis.$TC || { all: 0, some: 0 }; console.log(`tuples, ${GAME}, ${name}: every entry labeled ${C.all}, some labeled ${C.some}`); runs.push({ name, tuples: { ...C } }); return; }
  const row = { name, steps: rec.inputs.length, ways: {} };
  const want = replay(player(C, false).call, rec);
  const ways = WAYS.flatMap(w => w[0] === "jit" ? [w, ["jit, fresh copies", jitted.value, true]] : [w]);
  for (const [way, impl, fresh] of ways) {
    try {
      const play = () => { const p = player(impl, !!fresh); const end = replay(p.call, rec); return { end, ms: p.ms, calls: p.calls }; };
      const first = play(), per = [];
      if (way === "interpreted") per.push(first.ms);
      else { const t0 = now(), reps = QUICK ? 2 : 5, minMs = QUICK ? 30 : 300; while (per.length < 50 && (per.length < reps || now() - t0 < minMs)) per.push(play().ms); }
      const ms = median(per);
      row.ways[way] = { ms, usPerCall: ms / first.calls * 1000, calls: first.calls, reps: per.length, min: Math.min(...per), same: !differs(first.end, want) };
    } catch (e) { row.ways[way] = { error: String(e && e.message || e).slice(0, 300) }; }
  }
  runs.push(row);
  const show = w => { const r = row.ways[w]; return r == null ? "-" : r.error ? "error: " + r.error.slice(0, 80) : `${r.ms.toFixed(r.ms < 10 ? 3 : 0)} ms (${r.usPerCall < 10 ? r.usPerCall.toFixed(2) : r.usPerCall.toFixed(0)} us a call)` + (r.same ? "" : " (DIFFERS)"); };
  console.log(`run, ${name}: ${Object.keys(row.ways).map(w => `${w} ${show(w)}`).join("; ")}`);
}
// the real-time games: a frame a step, at most 600 frames (ten seconds at 60 frames a second)
const frames = (start, choose, step) => {
  const inputs = []; let g = start;
  for (let k = 0; k < REC(600) && !g.over; k++) { const x = choose(g); inputs.push(x); g = step(C, g, x); }
  return { start, inputs, replay: (call, r) => { let g = r.start; for (const x of r.inputs) g = step({ step: (...a) => call("step", ...a) }, g, x); return g; } };
};
const frameRun = (what, f) => run(`${f.inputs.length} frames${what}`, f, f.replay);
if (RUNS && GAME === "checkers") {
  const start = C.start, inputs = []; let g = start;
  for (let i = 0; i < REC(160) && !g.over; i++) { const ms = C.moves(g); if (!ms.length) break; const k = Math.floor(draw() * ms.length); inputs.push(k); g = C.apply(g, ms[k]); }
  run(`a game of ${inputs.length} moves (each: the moves, then one made)`, { start, inputs }, (call, r) => { let g = r.start; for (const k of r.inputs) { const ms = call("moves", g); g = call("apply", g, ms[k]); } return g; });
} else if (RUNS && GAME === "go") {
  const start = C.fresh(9), inputs = []; let g = start;
  for (let i = 0; i < REC(120) && !g.over; i++) { const w = C.choose(g, ints(81, 20)); inputs.push(w); g = w < 0 ? C.pass(g) : C.play(g, w); }
  run(`a game on 9 by 9, ${inputs.length} turns (each: a move played, or a pass)`, { start, inputs }, (call, r) => { let g = r.start; for (const w of r.inputs) g = w < 0 ? call("pass", g) : call("play", g, w); return g; });
} else if (RUNS && GAME === "minesweeper") {
  const rows = 16, cols = 30, us = Array.from({ length: rows * cols }, draw);
  const start = C.reveal(C.lay(rows, cols, 99, us, 8, 15), 8, 15), inputs = []; let g = start;
  for (let i = 0; i < REC(400) && !g.over; i++) {
    const m = C.sure(g); let r, c, flagIt = false;
    if (m.kind) { r = Math.floor(m.at / cols); c = m.at % cols; flagIt = m.kind === 2 || m.kind === 3; }
    else { const cl = []; g.grid.forEach((row, a) => row.forEach((x, b) => { if (!x.open && !x.flag && !x.mine) cl.push([a, b]); })); if (!cl.length) break; [r, c] = cl[Math.floor(draw() * cl.length)]; }
    inputs.push([flagIt, r, c]); g = flagIt ? C.flag(g, r, c) : C.reveal(g, r, c);
  }
  run(`16 by 30, ${inputs.length} taps (each: a cell opened or flagged)`, { start, inputs }, (call, r) => { let g = r.start; for (const [f, a, b] of r.inputs) g = call(f ? "flag" : "reveal", g, a, b); return g; });
} else if (RUNS && GAME === "mahjong") {
  const NONE = { kind: 0, tile: -1 }, waiting = o => !!o && (o.discard || o.win || o.pung || o.kong || o.chows.length > 0 || o.kongs.length > 0);
  const start = C.start(ints(136, 1e6)), inputs = []; let g = start;
  for (let i = 0; i < REC(400) && g.phase !== 3; i++) {
    const o = C.options(g), hand = g.seats[0].hand, x = draw();
    const a = o.discard ? (o.win && x < 0.6 ? { kind: 2, tile: -1 } : { kind: 1, tile: hand[Math.floor(draw() * hand.length)] })
      : o.win && x < 0.7 ? { kind: 8, tile: g.tile } : o.pung && x < 0.4 ? { kind: 6, tile: g.tile } : waiting(o) ? { kind: 4, tile: -1 } : NONE;
    inputs.push(a); g = C.step(g, a);
  }
  run(`a hand of ${inputs.length} steps (each: your options, then a step)`, { start, inputs }, (call, r) => { let g = r.start; for (const a of r.inputs) { call("options", g); g = call("step", g, a); } return g; });
} else if (RUNS && GAME === "solitaire") {
  const start = C.deal(Array.from({ length: 52 }, draw), 1), inputs = []; let g = start;
  for (let i = 0; i < REC(200); i++) { const ms = C.moves(g); if (!ms.length || C.won(g)) break; const k = Math.floor(draw() * ms.length); inputs.push(k); g = C.apply(g, ms[k]); }
  run(`a deal, ${inputs.length} moves (each: the moves, whether it is won, then one made)`, { start, inputs }, (call, r) => { let g = r.start; for (const k of r.inputs) { const ms = call("moves", g); call("won", g); g = call("apply", g, ms[k]); } return g; });
} else if (RUNS && GAME === "mahjong-solitaire") {
  const start = C.deal(0, 31337), inputs = []; let g = start;
  for (let i = 0; i < REC(80) && !C.won(g); i++) { const p = C.best(g); if (!p || p.a < 0) break; inputs.push([p.a, p.b]); g = C.take(g, p.a, p.b); }
  run(`a deal, ${inputs.length} pairs taken (each: the free places, then a pair taken)`, { start, inputs }, (call, r) => { let g = r.start; for (const [a, b] of r.inputs) { call("frees", g); g = call("take", g, a, b); } return g; });
} else if (RUNS && GAME === "pinball") {
  frameRun(" (the flippers at random, the plunger when the ball waits)", frames(C.start(0),
    g => [draw() < 0.2, draw() < 0.2, g.vx === 0 && g.vy === 0 && g.x > 540000 ? 1 + Math.floor(draw() * 100) : 0],
    (e, g, [l, r, launch]) => e.step(0, g, l, r, launch)));
} else if (RUNS && GAME === "downhill") {
  frameRun(" (the robot's turns and crouches, a press of chance now and then)", frames(C.start(9, true),
    g => { const c = C.robot(g); return [draw() < 0.05 ? (draw() < 0.5 ? -1 : 1) : c.turn, draw() < 0.1 ? !c.tuck : c.tuck]; },
    (e, g, [turn, tuck]) => e.step(g, turn, tuck)));
} else if (RUNS && GAME === "bricks") {
  frameRun(" (the robot's paddle, sent elsewhere now and then)", frames(C.start(0, false),
    g => { const c = C.robot(g); return [draw() < 0.05 ? Math.floor(draw() * 600) : c.target, c.launch]; },
    (e, g, [target, launch]) => e.step(g, target, launch)));
} else if (RUNS && GAME === "snake") {
  frameRun(" (the robot's turns, one of chance now and then)", frames(C.start(5, false),
    g => draw() < 0.05 ? Math.floor(draw() * 4) : C.robot(g),
    (e, g, d) => e.step(g, d)));
} else if (RUNS && GAME === "trails") {
  const luck = () => Math.floor(draw() * 100);
  frameRun(" (both robot riders)", frames(C.start(0),
    g => [C.robot(g, 1, 6, 12, luck()), C.robot(g, 2, 150, 0, luck())],
    (e, g, [a, b]) => e.step(g, a, b)));
} else if (RUNS && GAME === "starwave") {
  frameRun(" (the robot's moves and shots, one of chance now and then)", frames(C.start(42),
    g => { const c = C.robot(g); return [draw() < 0.05 ? Math.floor(draw() * 3) - 1 : c.move, draw() < 0.05 ? !c.fire : c.fire]; },
    (e, g, [move, fire]) => e.step(g, move, fire)));
} else if (RUNS && GAME === "bugs") {
  frameRun(" (the robot's moves and shots, one of chance now and then)", frames(C.start(42),
    g => { const c = C.robot(g); return [draw() < 0.05 ? Math.floor(draw() * 3) - 1 : c.mx, c.my, draw() < 0.05 ? !c.fire : c.fire]; },
    (e, g, [mx, my, fire]) => e.step(g, mx, my, fire)));
} else if (RUNS && GAME === "dig") {
  frameRun(" (the robot's ways, flashes and blasts, one of chance now and then)", frames(C.start(42),
    g => { const c = C.robot(g); return [draw() < 0.05 ? Math.floor(draw() * 5) - 1 : c.dir, draw() < 0.02 ? true : c.flash, draw() < 0.02 ? true : c.blast]; },
    (e, g, [dir, flash, blast]) => e.step(g, dir, flash, blast)));
} else if (RUNS) console.log(`${GAME}: no run of states (each call stands alone), nothing to time with --runs`);

let machine = {};
try { machine = { cpus: os.cpus().length, model: os.cpus()[0].model, node: process.version, platform: `${os.platform()} ${os.release()}` }; } catch (e) { /* */ }
const out = {
  game: GAME, when: new Date().toISOString(), quick: QUICK, machine,
  package: { name: pkgJson.name, version: pkgJson.version, hazel: pkgJson.hazel || null, build: Hazel.build },
  examples: (() => { try { return execSync("git rev-parse HEAD", { cwd: new URL("..", import.meta.url) }).toString().trim(); } catch (e) { return null; } })(),
  once, ops, runs, clockNs,
};
console.log(`once: ${JSON.stringify(once)}`);
if (OUT) writeFileSync(OUT, JSON.stringify(out, null, 1));
const bad = [...ops, ...runs].flatMap(o => Object.entries(o.ways).filter(([, r]) => r && (r.error || !r.same)).map(([w]) => `${o.name} (${w})`));
if (bad.length) { console.log("NOT THE SAME: " + bad.join("; ")); process.exit(1); }
