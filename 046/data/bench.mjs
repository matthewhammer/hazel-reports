// the ReScript-compiled rule and the example's hand-written jsHandler, on the same 2,000 events, in one process
import * as P from "./src/Petri.res.js";
import * as H from "./hazeljit-petri.js";
import * as M from "./src/PetriMelange.js";
function jsHandler(net, ev) {
  const t = net.transitions[ev.tag === "Fire" ? ev.value : 0];
  const ok = t && t.inputs.every(a => net.marking[a.place] >= a.weight);
  if (!ok) return { tag: "Say", value: ["(js) cannot fire", { tag: "Done" }] };
  let k = { tag: "Done" };
  for (const a of [...t.outputs].reverse()) k = { tag: "Put", value: [a.place, a.weight, k] };
  for (const a of [...t.inputs].reverse()) k = { tag: "Take", value: [a.place, a.weight, k] };
  return { tag: "Say", value: ["(js) " + t.name, k] };
}
function perform(cmd, marking) {
  const m = marking.slice();
  for (let c = cmd; c && c.tag !== "Done"; ) {
    const [a, b, rest] = Array.isArray(c.value) ? c.value : [c.value];
    if (c.tag === "Take") { m[a] -= b; c = rest; } else if (c.tag === "Put") { m[a] += b; c = rest; } else if (c.tag === "Say") { c = b; } else throw new Error(c.tag);
  }
  return m;
}
const performR = (cmd, marking) => {
  const m = marking.slice();
  for (let c = cmd; c !== "Done"; ) {
    if (c.TAG === "Take") { m[c._0] -= c._1; c = c._2; } else if (c.TAG === "Put") { m[c._0] += c._1; c = c._2; } else if (c.TAG === "Say") { c = c._1; } else throw new Error(String(c));
  }
  return m;
};
const array = l => { const out = []; for (; l !== 0; l = l.tl) out.push(l.hd); return out; };
const list = xs => xs.reduceRight((tl, hd) => ({ hd, tl }), 0);
const median = xs => xs.slice().sort((a, b) => a - b)[Math.floor(xs.length / 2)];
const transitionsJs = array(P.transitions).map(t => ({ name: t.name, inputs: array(t.inputs), outputs: array(t.outputs) }));
let mj = array(P.marking), tj = [];
for (let i = 0; i < 2000; i++) { const t0 = performance.now(); const cmd = jsHandler({ marking: mj, transitions: transitionsJs }, { tag: "Fire", value: i % 4 }); tj.push(performance.now() - t0); mj = perform(cmd, mj); }
let mr = array(P.marking), tr = [];
for (let i = 0; i < 2000; i++) {
  const n = { marking: list(mr), transitions: P.transitions, draw: 0.7 };
  const t0 = performance.now(); const cmd = P.on_event(n, { TAG: "Fire", _0: i % 4 }); tr.push(performance.now() - t0);
  mr = performR(cmd, mr);
}
// hazel-jit's: lists as {h, t} ending in null, tuples as arrays with their labels, constructors as {c, v}
const harray = l => { const out = []; for (; l !== null; l = l.t) out.push(l.h); return out; };
const hlist = xs => xs.reduceRight((t, h) => ({ h, t }), null);
const performH = (cmd, marking) => {
  const m = marking.slice();
  for (let c = cmd; c.c !== "Done"; ) {
    const [a, b, rest] = c.v;
    if (c.c === "Take") { m[a] -= b; c = rest; } else if (c.c === "Put") { m[a] += b; c = rest; } else if (c.c === "Say") { c = b; } else throw new Error(c.c);
  }
  return m;
};
let mh = harray(H.net.marking), th = [];
for (let i = 0; i < 2000; i++) {
  const n = [hlist(mh), H.net.transitions, 0.7]; n.marking = n[0]; n.transitions = n[1]; n.draw = n[2];
  const t0 = performance.now(); const cmd = H.on_event([n, { c: "Fire", v: i % 4 }]); th.push(performance.now() - t0);
  mh = performH(cmd, mh);
}
// Melange's: lists as {hd, tl} ending in 0, constructors as {TAG: n, _0, ...}, Done the number 0
const performM = (cmd, marking) => {
  const m = marking.slice();
  for (let c = cmd; c !== 0; ) {
    if (c.TAG === 0) { m[c._0] -= c._1; c = c._2; } else if (c.TAG === 1) { m[c._0] += c._1; c = c._2; } else if (c.TAG === 2) { c = c._1; } else throw new Error(String(c));
  }
  return m;
};
let mm = array(P.marking), tm = [];
for (let i = 0; i < 2000; i++) {
  const n = { marking: list(mm), transitions: M.transitions, draw: 0.7 };
  const t0 = performance.now(); const cmd = M.on_event(n, { TAG: 0, _0: i % 4 }); tm.push(performance.now() - t0);
  mm = performM(cmd, mm);
}
console.log(JSON.stringify({ melange_us: +(1000 * median(tm)).toFixed(3), melange_min_us: +(1000 * Math.min(...tm)).toFixed(3), melange_same: JSON.stringify(mm) === JSON.stringify(mj), hazeljit_us: +(1000 * median(th)).toFixed(3), hazeljit_min_us: +(1000 * Math.min(...th)).toFixed(3), hazeljit_same: JSON.stringify(mh) === JSON.stringify(mj), js_us: +(1000 * median(tj)).toFixed(3), js_min_us: +(1000 * Math.min(...tj)).toFixed(3),
  rescript_us: +(1000 * median(tr)).toFixed(3), rescript_min_us: +(1000 * Math.min(...tr)).toFixed(3), same: JSON.stringify(mj) === JSON.stringify(mr), marking: mr }));
