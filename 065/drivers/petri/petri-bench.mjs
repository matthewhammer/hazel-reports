// ^report(65) (ticket 853): report 046's Petri net rule again, 2,000 events (Fire(i mod 4), each command performed on the
// marking), as 046 timed it: µs a call, the median and the fastest. One way per process:
//
//   node petri-bench.mjs others                  ReScript's and Melange's code (046's outputs) and the hand-written handler
//   node petri-bench.mjs hazel <hazel-lib.js>    hazel-jit's code for the example's rules, from that build's compileProgram,
//                                                called as a page calls it: on_event with the pair (net, event)
//
// Prints one JSON line. The rules are hazeljs-examples' petri-net/rules (the same rule 046 compiled).
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

const median = xs => xs.slice().sort((a, b) => a - b)[Math.floor(xs.length / 2)];
const us = ts => ({ median_us: +(1000 * median(ts)).toFixed(3), fastest_us: +(1000 * Math.min(...ts)).toFixed(3) });
const N = 2000;
const mode = process.argv[2];

// the hand-written handler's shapes, and the end it must reach
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

if (mode === "others") {
  const P = await import("./Petri.res.js");
  const M = await import("./petri-melange.js");
  const array = l => { const out = []; for (; l !== 0; l = l.tl) out.push(l.hd); return out; };
  const list = xs => xs.reduceRight((tl, hd) => ({ hd, tl }), 0);
  const transitionsJs = array(P.transitions).map(t => ({ name: t.name, inputs: array(t.inputs), outputs: array(t.outputs) }));
  let mj = array(P.marking), tj = [];
  for (let i = 0; i < N; i++) { const t0 = performance.now(); const cmd = jsHandler({ marking: mj, transitions: transitionsJs }, { tag: "Fire", value: i % 4 }); tj.push(performance.now() - t0); mj = perform(cmd, mj); }
  const performR = (cmd, marking) => {
    const m = marking.slice();
    for (let c = cmd; c !== "Done"; ) {
      if (c.TAG === "Take") { m[c._0] -= c._1; c = c._2; } else if (c.TAG === "Put") { m[c._0] += c._1; c = c._2; } else if (c.TAG === "Say") { c = c._1; } else throw new Error(String(c));
    }
    return m;
  };
  let mr = array(P.marking), tr = [];
  for (let i = 0; i < N; i++) {
    const n = { marking: list(mr), transitions: P.transitions, draw: 0.7 };
    const t0 = performance.now(); const cmd = P.on_event(n, { TAG: "Fire", _0: i % 4 }); tr.push(performance.now() - t0);
    mr = performR(cmd, mr);
  }
  const performM = (cmd, marking) => {
    const m = marking.slice();
    for (let c = cmd; c !== 0; ) {
      if (c.TAG === 0) { m[c._0] -= c._1; c = c._2; } else if (c.TAG === 1) { m[c._0] += c._1; c = c._2; } else if (c.TAG === 2) { c = c._1; } else throw new Error(String(c));
    }
    return m;
  };
  let mm = array(P.marking), tm = [];
  for (let i = 0; i < N; i++) {
    const n = { marking: list(mm), transitions: M.transitions, draw: 0.7 };
    const t0 = performance.now(); const cmd = M.on_event(n, { TAG: 0, _0: i % 4 }); tm.push(performance.now() - t0);
    mm = performM(cmd, mm);
  }
  const end = JSON.stringify(mj);
  console.log(JSON.stringify({ js: { ...us(tj), end: mj }, rescript: { ...us(tr), same: JSON.stringify(mr) === end }, melange: { ...us(tm), same: JSON.stringify(mm) === end } }));
} else if (mode === "hazel") {
  await import(pathToFileURL(process.argv[3]).href);
  const Hazel = globalThis.Hazel;
  const read = f => readFileSync(new URL("../../../../hazeljs-examples/petri-net/rules/" + f, import.meta.url), "utf8").replace(/\s+$/, "");
  const spec = { preamble: read("preamble.hz"), modules: [{ name: "Common", text: read("Common.hz") }, { name: "Rules", text: read("Rules.hz") }, { name: "Main", text: read("Main.hz") }],
                 tail: "(transitions = Main.transitions, marking = Main.marking, on_event = Main.on_event)" };
  const c = Hazel.compileProgram(spec);
  if (!c.compiled) throw new Error("not compiled: " + c.reason);
  const V = new Function("$R", c.js)(eval("(" + c.runtime + ")"));
  // hazel-jit's shapes since ticket 847: a record a plain object, a list {$h, $t} ending in null, a constructor {$c, $v}
  const harray = l => { const out = []; for (; l !== null; l = l.$t) out.push(l.$h); return out; };
  const hlist = xs => xs.reduceRight(($t, $h) => ({ $h, $t }), null);
  const performH = (cmd, marking) => {
    const m = marking.slice();
    for (let c = cmd; c.$c !== "Done"; ) {
      const [a, b, rest] = c.$v;
      if (c.$c === "Take") { m[a] -= b; c = rest; } else if (c.$c === "Put") { m[a] += b; c = rest; } else if (c.$c === "Say") { c = b; } else throw new Error(c.$c);
    }
    return m;
  };
  let mh = harray(V.marking), th = [];
  for (let i = 0; i < N; i++) {
    const n = { marking: hlist(mh), transitions: V.transitions, draw: 0.7 };
    const t0 = performance.now(); const cmd = V.on_event([n, { $c: "Fire", $v: i % 4 }]); th.push(performance.now() - t0);
    mh = performH(cmd, mh);
  }
  console.log(JSON.stringify({ hazel: { ...us(th), end: mh, build: Hazel.build, direct: typeof V.on_event.$d === "function" } }));
} else throw new Error("usage: petri-bench.mjs others | hazel <hazel-lib.js>");
