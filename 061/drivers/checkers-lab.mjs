// hazeljs-examples, Checkers' search in a lab (ticket 811): Hazel's own rules (checkers/rules/Checkers.hz) mirrored step for step in
// JavaScript (the moves in the same order, the same values, the same alpha-beta walk and the same tie-break), so that Hazel playing
// itself can be watched as it searches: every position it looks at, and where it looks at the same one again.
//
//   node tools/checkers-lab.mjs check [games, 4] [depth, 6]   the mirror against the compiled rules (checkers/compiled.js), move for move
//   node tools/checkers-lab.mjs count [games, 4] [depth, 6]   the positions searched, and how many were searched before: within a
//                                                              move, across a player's own moves, across the two players
//   node tools/checkers-lab.mjs share [games, 4] [depth, 6]   a memo table of positions searched (a transposition table), kept for one
//                                                              move, for one player's whole game, or shared by both: the work saved,
//                                                              and whether every move chosen stays the same
//
// A position is the pieces (black's, white's, which are kings) and whose turn; searched with d moves still to look ahead. Hazel's
// search: negamax with alpha-beta (walk), every root move with the whole window (pick), so the root's values are exact.
import { readFileSync } from "node:fs";

// ---- the rules, as Checkers.hz has them ----
const bit = k => 2 ** k;
const has = (b, k) => Math.floor(b / bit(k)) % 2 === 1;
const add = (b, k) => has(b, k) ? b : b + bit(k);
const drop = (b, k) => has(b, k) ? b - bit(k) : b;
const dropAll = (b, ks) => ks.reduce(drop, b);
const squares = b => { const out = []; for (let k = 0; b > 0; k++, b = Math.floor(b / 2)) if (b % 2 === 1) out.push(k); return out; };
const step = (s, dr, dc) => { const r = Math.floor(s / 4), c = 2 * (s - r * 4) + (r % 2 === 0 ? 1 : 0), r2 = r + dr, c2 = c + dc;
  return r2 < 0 || r2 > 7 || c2 < 0 || c2 > 7 ? -1 : r2 * 4 + Math.floor(c2 / 2); };
const dirs = (who, king) => king ? [[-1, -1], [-1, 1], [1, -1], [1, 1]] : who === 1 ? [[-1, -1], [-1, 1]] : [[1, -1], [1, 1]];
const side = (g, who) => who === 1 ? g.black : g.white;
const crowns = (who, s) => who === 1 ? s < 4 : s >= 28;
function jumpsIn(who, king, all, them, s, took, ds) {
  const out = [];
  // (Hazel builds the list from the last direction back: the others first, then this one's in front of them)
  for (let i = ds.length - 1; i >= 0; i--) {
    const [dr, dc] = ds[i], over = step(s, dr, dc), land = step(s, dr + dr, dc + dc);
    if (over >= 0 && land >= 0 && has(them, over) && !took.includes(over) && !has(all, land)) {
      const more = !king && crowns(who, land) ? [] : jumpsIn(who, king, all, them, land, [over, ...took], dirs(who, king));
      const mine = more.length ? more.map(([ls, ts]) => [[land, ...ls], [over, ...ts]]) : [[[land], [over]]];
      out.unshift(...mine);
    }
  }
  return out;
}
function legal(g) {
  if (g.over) return [];
  const who = g.turn, all = g.black + g.white, ss = squares(side(g, who)), them = side(g, 3 - who), caps = [];
  for (const s of ss) { const k = has(g.kings, s); for (const [ls, ts] of jumpsIn(who, k, drop(all, s), them, s, [], dirs(who, k))) caps.push({ from: s, path: ls, took: ts }); }
  if (caps.length) return caps;
  const steps = [];
  for (const s of ss) for (const [dr, dc] of dirs(who, has(g.kings, s))) { const t = step(s, dr, dc); if (t >= 0 && !has(all, t)) steps.push({ from: s, path: [t], took: [] }); }
  return steps;
}
function after(g, m) {
  const who = g.turn, dest = m.path.length ? m.path[m.path.length - 1] : m.from, king = has(g.kings, m.from);
  const mine = add(drop(side(g, who), m.from), dest), theirs = dropAll(side(g, 3 - who), m.took), ks = dropAll(drop(g.kings, m.from), m.took);
  const quiet = m.took.length ? 0 : king ? g.quiet + 1 : 0;
  return { black: who === 1 ? mine : theirs, white: who === 1 ? theirs : mine, kings: king || crowns(who, dest) ? add(ks, dest) : ks, turn: 3 - who, quiet, over: false, winner: 0, last: [m.from, ...m.path] };
}
function apply(g, m) {
  const c = after(g, m), end = w => ({ ...c, over: true, winner: w });
  if (c.quiet >= 80) return end(0);
  return legal(c).length ? c : end(g.turn);
}
const START = { black: 4293918720, white: 4095, kings: 0, turn: 1, quiet: 0, over: false, winner: 0, last: [] };
const worth = (who, kings, ss) => ss.reduce((a, s) => a + (has(kings, s) ? 160 : 100 + 2 * (who === 1 ? 7 - Math.floor(s / 4) : Math.floor(s / 4))), 0);
const value = g => worth(g.turn, g.kings, squares(side(g, g.turn))) - worth(3 - g.turn, g.kings, squares(side(g, 3 - g.turn)));

// ---- the search, as Checkers.hz has it, with a watcher (seen) and, for `share`, a table (tt) ----
// seen(key, d): a position looked at with d moves still to look ahead (d = 0: only its value read). tt: a Map from (key, d) to
// { lo, hi }, the bounds the searches so far put on its value; consulted before a position with d >= 1 is searched.
const keyOf = g => `${g.black},${g.white},${g.kings},${g.turn}`;
let seen = null, tt = null, ttHits = 0, interior = 0, leaves = 0, DEEPER = false;
// (DEEPER: a position searched further ahead answers for one that needs less, as chess programs' tables do: no longer Hazel's
// own answers, so its moves may change; the table then keeps, for each position, its furthest-ahead search)
function child(c, d, alpha, beta) {
  // the value to the side that moved into c (Hazel: v = 0 - value(c), or 10000 + depth, or 0 - walk(c, ...)), d = depth - 1
  if (seen) seen(keyOf(c), d);
  if (d <= 0) { leaves++; return -value(c); }
  const cms = legal(c);
  if (!cms.length) return 10000 + d + 1;
  interior++;
  const k = tt ? (DEEPER ? keyOf(c) : keyOf(c) + "|" + d) : null;
  if (tt) { const e = tt.get(k);
    if (e && e.d >= d) { // (bounds on the value to the side to move at c; the window it is searched in is (-beta, -alpha))
      const a = -beta, b = -alpha;
      if (e.lo === e.hi) { ttHits++; return -e.lo; }
      if (e.lo >= b) { ttHits++; return -e.lo; }
      if (e.hi <= a) { ttHits++; return -a; }
    } }
  const r = walk(c, cms, d, -beta, -alpha);
  if (tt) { const a = -beta, b = -alpha, old = tt.get(k), e = old && old.d === d ? old : { d, lo: -Infinity, hi: Infinity };
    if (!old || old.d <= d) {
      if (r <= a) e.hi = Math.min(e.hi, a); else if (r >= b) e.lo = Math.max(e.lo, r); else { e.lo = r; e.hi = r; }
      tt.set(k, e); } }
  return -r;
}
function walk(g, ms, depth, alpha, beta) {
  for (const m of ms) {
    const v = child(after(g, m), depth - 1, alpha, beta);
    const a = v > alpha ? v : alpha;
    if (a >= beta) return a;
    alpha = a;
  }
  return alpha;
}
function choose(g, depth, rs) {
  let best = { from: -1, path: [], took: [] }, bv = -1000000, br = -1;
  legal(g).forEach((m, i) => {
    const r = i < rs.length ? rs[i] : 0;
    const v = child(after(g, m), depth - 1, -1000000, 1000000);
    if (v > bv || (v === bv && r > br)) { best = m; bv = v; br = r; }
  });
  return best;
}

// ---- self-play: Hazel against itself, its tie-breaks from a seeded stream (the page's are Math.random) ----
let seed = Number(process.env.SEED || 5);
const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const rsFor = () => Array.from({ length: 48 }, () => Math.floor(rnd() * 1000));
function game(depth, onMove) {
  let g = START, n = 0;
  while (!g.over && n < 400) { const rs = rsFor(), m = choose(g, depth, rs); onMove && onMove(g, m, rs, n); g = apply(g, m); n++; }
  return { g, moves: n };
}
const same = (a, b) => a.from === b.from && a.path.join() === b.path.join();
const mode = process.argv[2] || "count", GAMES = Number(process.argv[3] || 4), DEPTH = Number(process.argv[4] || 6);
const say = (...a) => console.log(...a);
const pct = (a, b) => (100 * a / Math.max(1, b)).toFixed(1) + "%";

if (mode === "check") {
  // the compiled rules: the same move as the mirror's from every position of each game, the same game afterwards
  const box = { exports: {} }; new Function("module", "window", readFileSync(new URL("../checkers/compiled.js", import.meta.url), "utf8"))(box, undefined);
  const C = box.exports; let bad = 0, moves = 0, msJ = 0, msC = 0;
  for (let i = 0; i < GAMES; i++) {
    const r = game(DEPTH, (g, m, rs) => {
      moves++;
      let t = performance.now(); const cm = C.choose({ ...g }, DEPTH, rs); msC += performance.now() - t;
      if (!same(cm, m)) { bad++; if (bad < 5) say("DIFFERENT at", JSON.stringify(g), "mirror", JSON.stringify(m), "compiled", JSON.stringify(cm)); }
      const cl = C.moves({ ...g }), jl = legal(g);
      if (cl.length !== jl.length || cl.some((x, k) => !same(x, jl[k]))) { bad++; if (bad < 5) say("MOVES DIFFER at", JSON.stringify(g)); }
    });
    say(`game ${i + 1}: ${r.moves} moves, ${r.g.winner === 0 ? "a draw" : r.g.winner === 1 ? "black won" : "white won"}`);
  }
  t0: { const t = performance.now(); game(DEPTH); msJ = performance.now() - t; }
  say(`${moves} positions: ${bad} different; the compiled rules ${(msC / moves).toFixed(1)} ms a move (the mirror, one game again: ${msJ.toFixed(0)} ms)`);
  process.exitCode = bad ? 1 : 0;
}

if (mode === "count") {
  // each position looked at (with d to look ahead), and whether it was looked at before, with the same d: in this move's search,
  // in this player's earlier searches, or only in the other player's
  const T = { all: 0, inMove: 0, ownBefore: 0, otherOnly: 0, leaves: 0, leafRepeat: 0, pInMove: 0, pOwn: 0, pOther: 0 }, byDepth = {};
  let distinctGame = 0, distinctPos = 0; const perGame = [];
  for (let i = 0; i < GAMES; i++) {
    const firstBy = new Map(); // key|d -> the player who looked at it first
    const posSeen = new Set(), posFirst = new Map();
    let player = 1, cur = null, curPos = null;
    seed = Number(process.env.SEED || 5) + i * 7919;
    let g = START, n = 0;
    seen = (k, d) => {
      const kd = k + "|" + d, f = firstBy.get(kd);
      T.all++; (byDepth[d] = byDepth[d] || { all: 0, repeat: 0 }).all++;
      if (d === 0) T.leaves++;
      posSeen.add(k);
      // (by position alone, any look-ahead: seen in this search, or first by this player, or only by the other)
      if (curPos.has(k)) T.pInMove++; else { curPos.add(k); const pf = posFirst.get(k); if (pf === undefined) posFirst.set(k, player); else if (pf === player) T.pOwn++; else T.pOther++; }
      if (cur.has(kd)) { T.inMove++; byDepth[d].repeat++; if (d === 0) T.leafRepeat++; return; }
      cur.add(kd);
      if (f === undefined) { firstBy.set(kd, player); return; }
      byDepth[d].repeat++; if (d === 0) T.leafRepeat++;
      if (f === player) T.ownBefore++; else T.otherOnly++;
    };
    while (!g.over && n < 400) { player = g.turn; cur = new Set(); curPos = new Set(); const rs = rsFor(), m = choose(g, DEPTH, rs); g = apply(g, m); n++; }
    distinctGame += firstBy.size; distinctPos += posSeen.size; perGame.push({ moves: n, winner: g.winner, lookedAt: T.all });
    say(`game ${i + 1}: ${n} moves, ${g.winner === 0 ? "a draw" : g.winner === 1 ? "black won" : "white won"}; looked at ${T.all} so far`);
    seen = null;
  }
  const rep = T.inMove + T.ownBefore + T.otherOnly;
  say(`\n${GAMES} games of Hazel against itself, ${DEPTH} moves ahead: ${T.all} positions looked at (${T.leaves} only valued, at the search's edge)`);
  say(`seen before, with as far to look: ${rep} (${pct(rep, T.all)}): in the same move's search ${T.inMove} (${pct(T.inMove, T.all)}), in the same player's earlier moves ${T.ownBefore} (${pct(T.ownBefore, T.all)}), only in the other player's ${T.otherOnly} (${pct(T.otherOnly, T.all)})`);
  say(`by position alone, any look-ahead: seen before ${pct(T.pInMove + T.pOwn + T.pOther, T.all)}: in the same move's search ${pct(T.pInMove, T.all)}, in the same player's earlier moves ${pct(T.pOwn, T.all)}, only in the other player's ${pct(T.pOther, T.all)}`);
  say(`distinct (position, look-ahead): ${distinctGame} (${pct(distinctGame, T.all)} of those looked at); distinct positions, any look-ahead: ${distinctPos}`);
  for (const d of Object.keys(byDepth).sort()) say(`  ${d} still to look: ${byDepth[d].all} looked at, ${pct(byDepth[d].repeat, byDepth[d].all)} seen before`);
  if (process.env.OUT) (await import("node:fs")).writeFileSync(process.env.OUT, JSON.stringify({ games: GAMES, depth: DEPTH, ...T, distinct: distinctGame, distinctPos, byDepth, perGame }, null, 1));
}

if (mode === "share") {
  // Hazel's own games first (no table): each position met and its tie-break numbers. Then those same positions, in the same order,
  // searched again with a table: one for each move's search (cleared after it); one for each player, kept from move to move; one
  // both players share; and, for the last two, one where a position searched further ahead answers for one that needs less (as
  // chess programs' tables do: then the values are no longer Hazel's own, and a move chosen may differ). For each: the positions
  // searched past the edge (walk called) and valued at it, the table's answers, the time, and the moves chosen differently
  const games = [];
  interior = 0; leaves = 0; let t0 = performance.now();
  for (let i = 0; i < GAMES; i++) {
    seed = Number(process.env.SEED || 5) + i * 7919;
    const steps = []; let g = START, n = 0;
    while (!g.over && n < 400) { const rs = rsFor(), m = choose(g, DEPTH, rs); steps.push({ g, rs, m }); g = apply(g, m); n++; }
    games.push(steps);
  }
  const moves = games.reduce((a, s) => a + s.length, 0);
  const row = (name, ms, differ, size) => {
    say(`${name.padEnd(28)}: searched ${String(interior).padStart(9)} past the edge (${(interior / moves).toFixed(0)} a move), valued ${String(leaves).padStart(10)} at it (${(leaves / moves).toFixed(0)} a move); table answers ${String(ttHits).padStart(7)}; ${(ms / moves).toFixed(2)} ms a move; ${differ} of ${moves} moves chosen differently; table size at most ${size}`);
    return { name, interior, leaves, hits: ttHits, msPerMove: ms / moves, differ, moves, size };
  };
  const out = [row("none (Hazel now)", performance.now() - t0, 0, 0)];
  const ways = [["each move", "move", false], ["each player", "player", false], ["shared", "shared", false],
                ["each player, deeper answers", "player", true], ["shared, deeper answers", "shared", true]];
  for (const [name, scope, deeper] of ways) {
    DEEPER = deeper; interior = 0; leaves = 0; ttHits = 0; let differ = 0, size = 0; t0 = performance.now();
    for (const steps of games) {
      const tabs = { 1: new Map(), 2: new Map() }, shared = new Map();
      for (const { g, rs, m } of steps) {
        tt = scope === "move" ? new Map() : scope === "player" ? tabs[g.turn] : shared;
        const c = choose(g, DEPTH, rs);
        size = Math.max(size, tt.size);
        if (!same(c, m)) differ++;
      }
    }
    tt = null; DEEPER = false;
    out.push(row(name, performance.now() - t0, differ, size));
  }
  if (process.env.OUT) (await import("node:fs")).writeFileSync(process.env.OUT, JSON.stringify({ games: GAMES, depth: DEPTH, moves, rows: out }, null, 1));
}
