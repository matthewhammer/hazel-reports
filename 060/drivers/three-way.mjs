// hazeljs-examples: each game's rules timed three ways (ticket 797, for a report in the Hazel reports series): hazeljs
// interpreting the Hazel (rules/*.hz), the same Hazel compiled ahead of time by hazel-jit (compiled.js), and the same game
// written in plain JavaScript (plain.js). The three give the same answers (node/compare-compiled.mjs, with and without
// --plain); here each of a game's operations is timed on fixed positions from a seeded game, and Hazel plays whole seeded
// games against itself (the 🤖 switch's work), each way, and the final states are checked to be the same.
//
//   node node/three-way.mjs <game> [out.json] [--quick]
//
// A call too fast for the clock is timed in batches (as many calls as take at least a millisecond), and the median of the
// batches taken, per call. hazeljs is timed at least 3 times and for at least 1.5 s; the others at least 30 times and for at
// least 0.3 s. --quick: a fraction of that, to try the script out.
import Hazel from "hazeljs";
import { readFileSync, writeFileSync } from "node:fs";
import { execSync } from "node:child_process";
import os from "node:os";

const QUICK = process.argv.includes("--quick");
// (--no-hazeljs: the compiled and plain ways only, for a quick look on a laptop)
const NOHAZEL = process.argv.includes("--no-hazeljs");
const args = process.argv.slice(2).filter(a => !a.startsWith("--"));
const GAME = args[0], OUT = args[1];
const SETUP = {
  checkers: { modules: ["Checkers"], tail: "(start = Checkers.start, moves = Checkers.moves, apply = Checkers.apply, choose = Checkers.choose)" },
  go: { modules: ["Go"], tail: "(fresh = Go.fresh, play = Go.play, pass = Go.pass, score = Go.score, choose = Go.choose)" },
  minesweeper: { modules: ["Board", "Play", "Hint"], tail: "(fresh = Board.fresh, lay = Board.lay_mines, reveal = Play.reveal, flag = Play.flag, chord = Play.chord, flags = Play.flags, sure = Hint.sure)" },
  mahjong: { modules: ["Mahjong"], tail: "(start = Mahjong.start, step = Mahjong.step, options = Mahjong.options, next_hand = Mahjong.next_hand)" },
  solitaire: { modules: ["Cards", "Deal", "Moves"], tail: "(deal = Deal.deal, moves = Moves.moves, moves_from = Moves.moves_from, apply = Moves.apply, won = Moves.won)" },
}[GAME];
if (!SETUP) { console.log("usage: node node/three-way.mjs checkers|go|minesweeper|mahjong|solitaire [out.json] [--quick]"); process.exit(2); }

// ---- the three: hazeljs builds the rules as the page does; compiled.js and plain.js are classic scripts, run as modules
const file = f => readFileSync(new URL(`../${GAME}/${f}`, import.meta.url), "utf8");
const run = text => { const b = { exports: {} }; new Function("module", "window", text)(b, undefined); return b.exports; };
const script = f => run(file(f));
// (where hazel-jit's time goes: two variants of compiled.js, for timing only. The step budget: every compiled function
// starts by counting a step and, every 16384 steps, reading the clock, so a run can be stopped as the interpreter's is.
// Exact integers: every +, -, * and / goes through the runtime, which keeps Hazel's Ints exact past 2^53 (a BigInt there);
// these games' numbers never get near it, so plain number arithmetic gives the same answers here, as each row checks)
const BUDGET = /if \(--\$R\.fuel < 0 \|\| \(\(\$R\.fuel & 16383\) === 0 && performance\.now\(\) > \$R\.deadline\)\) \$R\.out\(\); /g;
const jitText = file("compiled.js"), budgets = (jitText.match(BUDGET) || []).length;
const noBudget = jitText.replace(BUDGET, "");
const ANCHOR = "  const P = (function ($R) {";
if (!budgets || !noBudget.includes(ANCHOR)) { console.log("compiled.js is not as expected: the variants cannot be made"); process.exit(1); }
const numbers = noBudget.replace(ANCHOR, "  $R.iadd = (a, b) => a + b; $R.isub = (a, b) => a - b; $R.imul = (a, b) => a * b; $R.idiv = (a, b) => (a - a % b) / b; $R.ineg = a => -a;\n" + ANCHOR);
const read = m => file(`rules/${m}.hz`).replace(/\s+$/, "");
const t0 = performance.now();
const built = Hazel.runProgram({ preamble: read("preamble"), modules: SETUP.modules.map(name => ({ name, text: read(name) })), tail: SETUP.tail });
const buildMs = performance.now() - t0;
if (!built.ok) { console.log("hazeljs did not build the rules", built.errors); process.exit(1); }
const WAYS = [["hazeljs", built.value], ["hazel-jit", script("compiled.js")], ["hazel-jit, no step budget", run(noBudget)],
              ["hazel-jit, no budget, plain numbers", run(numbers)], ["plain JS", script("plain.js")]];
const [H, C] = WAYS.map(([, v]) => v);

// ---- the clock
const median = xs => { const s = [...xs].sort((a, b) => a - b); return s.length % 2 ? s[(s.length - 1) / 2] : (s[s.length / 2 - 1] + s[s.length / 2]) / 2; };
function clock(f, slow) {
  const minMs = (slow ? 1500 : 300) * (QUICK ? 0.1 : 1), minReps = QUICK ? 2 : slow ? 3 : 30, maxReps = slow ? 15 : 100000;
  // (warm up, and find the batch: calls enough to take a millisecond)
  let batch = 1;
  for (let w = 0; w < (slow ? 1 : 20); w++) f();
  if (!slow) for (;;) { const t = performance.now(); for (let i = 0; i < batch; i++) f(); if (performance.now() - t >= 1 || batch >= 1 << 20) break; batch *= 2; }
  const per = [];
  const start = performance.now();
  while (per.length < maxReps && (per.length < minReps || performance.now() - start < minMs)) {
    const t = performance.now(); for (let i = 0; i < batch; i++) f(); per.push((performance.now() - t) / batch);
  }
  return { ms: median(per), min: Math.min(...per), reps: per.length, batch };
}
let seed = 20261120; const draw = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const ints = (n, k) => Array.from({ length: n }, () => Math.floor(draw() * k));
const same = (x, y) => JSON.stringify(x) === JSON.stringify(y);

// ---- each game: operations on positions (C makes the positions; all three answer the same), and whole games
const ops = [], games = [];
function op(name, where, call, opts = {}) {
  const row = { name, where };
  const answers = [];
  for (const [way, impl] of WAYS) {
    if (way === "hazeljs" && (opts.skipHazel || NOHAZEL)) { row[way] = null; continue; }
    answers.push(call(impl));
    row[way] = clock(() => call(impl), way === "hazeljs");
  }
  row.same = answers.every(a => same(a, answers[0]));
  ops.push(row);
  const f = x => x ? (x.ms < 0.01 ? x.ms.toFixed(5) : x.ms < 1 ? x.ms.toFixed(4) : x.ms.toFixed(1)) + " ms" : "not timed";
  console.log(`${name} (${where}): ` + WAYS.map(([w]) => `${w} ${f(row[w])}`).join(", ") + (row.same ? "" : "  ANSWERS DIFFER"));
}
// the page boundary by itself: hazel-jit's game converted from hazeljs's shapes into its own and back (compiled.js's
// $convert), which every call through the page's functions pays; hazeljs pays its own, inside its times
function edge(where, g) {
  const cv = C.$convert; if (!cv) return;
  const row = { name: "the page boundary: the game in and out", where, "hazel-jit": clock(() => cv.gameOut(cv.gameIn(g)), false), same: true, boundary: true };
  ops.push(row);
  console.log(`${row.name} (${where}): hazel-jit ${row["hazel-jit"].ms.toFixed(5)} ms`);
}
function whole(name, play, opts = {}) {
  const row = { name };
  const ends = [];
  for (const [way, impl] of WAYS) {
    if (way === "hazeljs" && (opts.skipHazel || NOHAZEL)) { row[way] = null; continue; }
    // (the same seeded game each time; hazeljs once, the others 5 times, the median kept: a first run is cold)
    const runs = []; let r;
    for (let k = 0; k < (way === "hazeljs" || QUICK ? 1 : 5); k++) { const s0 = seed; const t = performance.now(); r = play(impl); runs.push(performance.now() - t); seed = s0; }
    ends.push(r.end); row[way] = { ms: median(runs), runs, moves: r.moves };
  }
  // (each way played from the same seed: the same game, so the same end)
  row.same = ends.every(e => same(e, ends[0]));
  games.push(row);
  const f = x => x ? `${x.ms < 1000 ? x.ms.toFixed(1) + " ms" : (x.ms / 1000).toFixed(2) + " s"} (${x.moves} moves)` : "not played";
  console.log(`whole: ${name}: ` + WAYS.map(([w]) => `${w} ${f(row[w])}`).join(", ") + (row.same ? "" : "  ENDS DIFFER"));
}

if (GAME === "checkers") {
  // positions: the start, and 8 and 30 seeded moves in (Hazel looking 2 ahead on both sides)
  const P = [["the start", C.start]];
  let g = C.start;
  for (let i = 1; i <= 30 && !g.over; i++) { g = C.apply(g, C.choose(g, 2, ints(48, 1000))); if (i === 8) P.push(["8 moves in", g]); if (i === 30) P.push(["30 moves in", g]); }
  const rs = ints(48, 1000);
  for (const [where, p] of P) { op("the moves", where, x => x.moves(p)); edge(where, p); }
  for (const d of [1, 2, 3, 4, 5, 6]) for (const [where, p] of P.slice(1)) op(`Hazel's move, looking ${d} ahead`, where, x => x.choose(p, d, rs), { skipHazel: d > 4 || (d === 4 && where !== "8 moves in") });
  const selfPlay = (d, cap) => x => { let g = x.start, n = 0; while (!g.over && n < cap) { g = x.apply(g, x.choose(g, d, ints(48, 1000))); n++; } return { end: g, moves: n }; };
  whole("Hazel against Hazel, looking 2 ahead (to 60 moves)", selfPlay(2, 60));
  whole("Hazel against Hazel, looking 4 ahead (a whole game)", selfPlay(4, 400), { skipHazel: true });
  whole("Hazel against Hazel, looking 6 ahead (a whole game)", selfPlay(6, 400), { skipHazel: true });
} else if (GAME === "go") {
  // positions on 9 by 9: 6 and 40 seeded moves in (Hazel on both sides, the page's default noise, 0 to 2 points)
  const P = [];
  let g = C.fresh(9);
  for (let i = 1; i <= 40 && !g.over; i++) { const w = C.choose(g, ints(81, 21)); g = w < 0 ? C.pass(g) : C.play(g, w); if (i === 6) P.push(["6 moves in", g]); if (i === 40) P.push(["40 moves in", g]); }
  const rs = ints(81, 21);
  for (const [where, p] of P) {
    const w = C.choose(p, rs);
    op("a move played", where, x => x.play(p, w < 0 ? 40 : w));
    op("Hazel's choice of move", where, x => x.choose(p, rs));
    op("the score", where, x => x.score(p));
    edge(where, p);
  }
  const selfPlay = n => x => { let g = x.fresh(n), k = 0; while (!g.over && k < 4 * n * n) { const w = x.choose(g, ints(n * n, 21)); g = w < 0 ? x.pass(g) : x.play(g, w); k++; } return { end: { g, score: x.score(g) }, moves: k }; };
  whole("Hazel against Hazel on 7 by 7", selfPlay(7));
  whole("Hazel against Hazel on 9 by 9", selfPlay(9));
} else if (GAME === "minesweeper") {
  // positions: each level's board after its first tap in the middle (the mines from seeded numbers)
  const LEVELS = [["beginner, 9 by 9", 9, 9, 10], ["intermediate, 16 by 16", 16, 16, 40], ["expert, 16 by 30", 16, 30, 99]];
  for (const [where, rows, cols, mines] of LEVELS) {
    const us = Array.from({ length: rows * cols }, draw), r0 = rows >> 1, c0 = cols >> 1;
    op("the mines laid", where, x => x.lay(rows, cols, mines, us, r0, c0));
    const g = C.reveal(C.lay(rows, cols, mines, us, r0, c0), r0, c0);
    const m = C.sure(g);
    const cell = m.kind === 1 ? m.at : g.grid.flat().findIndex(x => !x.open && !x.mine);
    op("a cell opened", where, x => x.reveal(g, Math.floor(cell / cols), cell % cols));
    op("the hint (a sure move)", where, x => x.sure(g));
    edge(where, g);
  }
  // whole boards as 🤖 plays them: the first tap in the middle, sure moves, a seeded guess when there is none
  const sweep = (rows, cols, mines) => x => {
    const us = Array.from({ length: rows * cols }, draw), r0 = rows >> 1, c0 = cols >> 1;
    let g = x.reveal(x.lay(rows, cols, mines, us, r0, c0), r0, c0), k = 1;
    while (!g.over && k < 2000) {
      const m = x.sure(g);
      if (m.kind) g = m.kind === 1 ? x.reveal(g, Math.floor(m.at / cols), m.at % cols) : x.flag(g, Math.floor(m.at / cols), m.at % cols);
      else { const closed = []; g.grid.forEach((row, r) => row.forEach((y, c) => { if (!y.open && !y.flag) closed.push([r, c]); })); const [r, c] = closed[Math.floor(draw() * closed.length)]; g = x.reveal(g, r, c); }
      k++;
    }
    return { end: g, moves: k };
  };
  // (hazeljs's expert board would take minutes: a hint there is about a second)
  for (const [where, rows, cols, mines] of LEVELS) whole(`Hazel sweeping a board, ${where}`, sweep(rows, cols, mines), { skipHazel: rows * cols > 300 });
} else if (GAME === "mahjong") {
  const NONE = { kind: 0, tile: -1 }, AUTO = { kind: 9, tile: -1 };
  const r0 = ints(136, 1e6);
  op("a hand dealt", "the first hand", x => x.start(r0));
  // positions: a Hazel player's turn, your turn (the options), and claims on a discard, from a seeded hand Hazel plays
  let g = C.start(r0); const P = {};
  for (let i = 0; i < 200 && g.phase !== 3 && Object.keys(P).length < 3; i++) {
    if (!P.turn && g.phase === 1 && g.turn !== 0) P.turn = g;
    if (!P.yours && g.phase === 1 && g.turn === 0) P.yours = g;
    if (!P.claims && g.phase === 2 && g.from !== 0) P.claims = g;
    g = C.step(g, AUTO);
  }
  op("a Hazel player's turn (a step)", "early in the hand", x => x.step(P.turn, NONE));
  edge("early in the hand", P.turn);
  op("your options", "your turn", x => x.options(P.yours));
  op("your turn, played by Hazel (a step)", "your turn", x => x.step(P.yours, AUTO));
  op("the claims on a discard (a step)", "another's discard", x => x.step(P.claims, AUTO));
  const hands = n => x => { let g = x.start(ints(136, 1e6)), k = 0; for (let h = 0; h < n; h++) { while (g.phase !== 3 && k < 5000) { g = x.step(g, AUTO); k++; } if (h + 1 < n) g = x.next_hand(g, ints(136, 1e6)); } return { end: g, moves: k }; };
  whole("Hazel playing all four seats, one hand", hands(1));
  whole("Hazel playing all four seats, eight hands", hands(8));
} else if (GAME === "solitaire") {
  const us = Array.from({ length: 52 }, draw);
  op("a deal", "a new game", x => x.deal(us, 1));
  let g = C.deal(us, 1);
  for (let i = 0; i < 25; i++) { const ms = C.moves(g); g = C.apply(g, ms[Math.floor(draw() * ms.length)]); }
  op("every legal move", "25 moves in", x => x.moves(g));
  edge("25 moves in", g);
  const ms = C.moves(g), m = ms.find(m => m.tag === "Shift") || ms[0];
  op("a move made", "25 moves in", x => x.apply(g, m));
  op("the moves from a pile", "25 moves in", x => x.moves_from(g, { tag: "FromPile", value: { pile: 6, count: 1 } }));
  // (Solitaire has no opponent: a game is random moves, here 300 of them)
  whole("300 random moves", x => { let g = x.deal(us, 1), k = 0; for (; k < 300; k++) { const ms = x.moves(g); if (!ms.length) break; g = x.apply(g, ms[Math.floor(draw() * ms.length)]); } return { end: g, moves: k }; });
}

// ---- what was measured, and where
const git = c => { try { return execSync(c, { cwd: new URL("..", import.meta.url).pathname, encoding: "utf8" }).trim(); } catch (e) { return ""; } };
const result = {
  game: GAME, when: new Date().toISOString(), quick: QUICK,
  machine: { cpu: (os.cpus()[0] || {}).model, cpus: os.cpus().length, node: process.version, platform: `${os.platform()} ${os.release()}`, runner: process.env.RUNNER_NAME || null, ci: !!process.env.GITHUB_ACTIONS },
  builds: { "hazeljs": JSON.parse(readFileSync(new URL("../node_modules/hazeljs/package.json", import.meta.url), "utf8")).version,
            "hazel-jit": C.made, "plain JS": git("git log -1 --format=%h -- " + GAME + "/plain.js"), examples: git("git rev-parse --short HEAD") },
  ways: WAYS.map(([w]) => w), budgetChecks: budgets, hazeljsBuildMs: buildMs, ops, games,
};
console.log(`hazeljs built the rules in ${buildMs.toFixed(0)} ms; hazel-jit ${result.builds["hazel-jit"]}; node ${process.version} on ${result.machine.cpu}`);
if (OUT) writeFileSync(OUT, JSON.stringify(result, null, 1));
