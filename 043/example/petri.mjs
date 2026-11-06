// ^report(43)'s worked example: a Petri net simulator whose firing rule is written in Hazel, run through hazeljs.
// The pattern is Messed Up Dress Up's (its js/25-scripting.js): the app keeps the state and draws it; on each event it hands
// a typed view of the state and the event to a Hazel function, and acts out the command it answers.
//
//   npm install hazeljs@0.0.4 && node petri.mjs        (prints what the report quotes, and writes run.json beside it)
import Hazel from "hazeljs";
import { writeFileSync } from "node:fs";

// ---- 1. The vocabulary, declared once: what the rule is told (Net), what happened (Event), what it may say (Cmd).
const PREAMBLE = `type Arc = (place = Int, weight = Int) in
type Transition = (name = String, inputs = [Arc], outputs = [Arc]) in
type Net = (marking = [Int], transitions = [Transition], draw = Float) in
type Event = + Fire(Int) + Step in
type Cmd = + Done + Take(Int, Int, Cmd) + Put(Int, Int, Cmd) + Say(String, Cmd) in`;

// ---- 2. The rules, as a user would write them in the app's editors: a module of helpers, and the module with on_event.
const COMMON = `# the i-th of a list of Ints, 0 past its end #
let nth = fun (xs, i) : ([Int], Int) -> case xs | [] => 0 | x :: rest => if i == 0 then x else nth(rest, i - 1) end;
let len = fun xs : [Int] -> case xs | [] => 0 | _ :: rest => 1 + len(rest) end;
# the i-th transition, if there is one #
let pick = fun (ts, i) : ([Transition], Int) -> case ts | [] => None | t :: rest => if i == 0 then Some(t) else pick(rest, i - 1) end;
# every input place holds at least its arc's weight #
let has = fun (m, arcs) : ([Int], [Arc]) -> case arcs | [] => true | a :: rest => nth(m, a.place) >= a.weight && has(m, rest) end;
let enabled = fun (m, t) : ([Int], Transition) -> has(m, t.inputs);
# the indices of the transitions that can fire #
let ready = fun (m, ts, i) : ([Int], [Transition], Int) -> case ts | [] => [] | t :: rest => if enabled(m, t) then i :: ready(m, rest, i + 1) else ready(m, rest, i + 1) end;
# firing: take each input's tokens, then put each output's #
let takes = fun (arcs, k) : ([Arc], Cmd) -> case arcs | [] => k | a :: rest => Take(a.place, a.weight, takes(rest, k)) end;
let puts = fun (arcs, k) : ([Arc], Cmd) -> case arcs | [] => k | a :: rest => Put(a.place, a.weight, puts(rest, k)) end;
let fire = fun t : Transition -> Say(t.name, takes(t.inputs, puts(t.outputs, Done)))`;

const RULES = `# Fire(i): fire transition i if it can. Step: fire one of those that can, chosen by the app's random draw. #
let fire_at = fun (n, i) : (Net, Int) ->
  case Common.pick(n.transitions, i)
  | None => Say("there is no transition " ++ string_of_int(i), Done)
  | Some(t) => if Common.enabled(n.marking, t) then Common.fire(t) else Say(t.name ++ " cannot fire now", Done)
  end;
let on_event = fun (n, e) : (Net, Event) ->
  case e
  | Fire(i) => fire_at(n, i)
  | Step =>
    let r = Common.ready(n.marking, n.transitions, 0) in
    let k = Common.len(r) in
    if k == 0 then Say("deadlock: nothing can fire", Done)
    else fire_at(n, Common.nth(r, int_of_float(n.draw *. float_of_int(k))))
  end`;

const spec = rules => ({ preamble: PREAMBLE, modules: [{ name: "Common", text: COMMON }, { name: "Rules", text: rules }],
  tail: "(Rules.on_event : (Net, Event) -> Cmd)" });

// ---- 3. The app's own state: two processes sharing one lock (mutual exclusion), the classic small net.
const PLACES = ["idle1", "busy1", "idle2", "busy2", "lock"];
const arc = (place, weight = 1) => ({ place: PLACES.indexOf(place), weight });
const NET = {
  marking: [1, 0, 1, 0, 1],
  transitions: [
    { name: "enter1", inputs: [arc("idle1"), arc("lock")], outputs: [arc("busy1")] },
    { name: "leave1", inputs: [arc("busy1")], outputs: [arc("idle1"), arc("lock")] },
    { name: "enter2", inputs: [arc("idle2"), arc("lock")], outputs: [arc("busy2")] },
    { name: "leave2", inputs: [arc("busy2")], outputs: [arc("idle2"), arc("lock")] },
  ],
};

// ---- 4. The app acts out a command: a chain, each command with the rest after it. Hazel never touches the state itself.
function perform(cmd, marking, log) {
  const m = marking.slice();
  for (let c = cmd; c && c.tag !== "Done"; ) {
    const [a, b, rest] = Array.isArray(c.value) ? c.value : [c.value];
    if (c.tag === "Take") { m[a] -= b; c = rest; }
    else if (c.tag === "Put") { m[a] += b; c = rest; }
    else if (c.tag === "Say") { log.push(a); c = b; }
    else throw new Error("a command this app does not know: " + c.tag);
  }
  return m;
}

// ---- 5. The app's own JS handler, for while the Hazel rules are not ready (errors, holes, unfinished brackets).
function jsHandler(net, ev) {
  const t = net.transitions[ev.tag === "Fire" ? ev.value : 0];
  const ok = t && t.inputs.every(a => net.marking[a.place] >= a.weight);
  if (!ok) return { tag: "Say", value: ["(js) cannot fire", { tag: "Done" }] };
  let k = { tag: "Done" };
  for (const a of [...t.outputs].reverse()) k = { tag: "Put", value: [a.place, a.weight, k] };
  for (const a of [...t.inputs].reverse()) k = { tag: "Take", value: [a.place, a.weight, k] };
  return { tag: "Say", value: ["(js) " + t.name, k] };
}

// ---- 6. Build the program once per text (Hazel remembers the modules' texts), and use it only when it is ok.
function build(rules) {
  const r = Hazel.runProgram(spec(rules));
  return { ok: r.ok, errors: r.errors.map(e => `${e.module ?? "the program"}: ${e.message.replace(/\s+/g, " ")}`),
           holes: r.holes, incomplete: r.incomplete, ms: r.ms, handler: r.ok ? r.value : null };
}
const handlerOf = b => b.ok ? b.handler : jsHandler;

const out = { hazeljs: Hazel.version, build: Hazel.build, node: process.version, runs: {} };

// (a) the rules as written: ok; a few events by hand, then 2,000 random steps
const built = build(RULES);
out.built = { ok: built.ok, errors: built.errors, holes: built.holes, ms: +built.ms.toFixed(1) };
console.log("built:", JSON.stringify(out.built));
let marking = NET.marking.slice(), said = [];
const on = handlerOf(built);
const by_hand = [{ tag: "Fire", value: 0 }, { tag: "Fire", value: 2 }, { tag: "Fire", value: 1 }, { tag: "Fire", value: 2 }];
out.by_hand = [];
for (const ev of by_hand) {
  const cmd = on({ ...NET, marking, draw: 0 }, ev);
  said = []; marking = perform(cmd, marking, said);
  out.by_hand.push({ event: ev, said: said.join("; "), marking: marking.slice(), cmd });
  console.log(JSON.stringify(ev), "->", said.join("; "), "->", JSON.stringify(marking));
}
// a deterministic stream of draws, so the run can be repeated
let seed = 7; const draw = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
marking = NET.marking.slice();
const counts = {}, times = [];
let both_busy = 0;
for (let i = 0; i < 2000; i++) {
  const t0 = performance.now();
  const cmd = on({ ...NET, marking, draw: draw() }, { tag: "Step" });
  times.push(performance.now() - t0);
  said = []; marking = perform(cmd, marking, said);
  counts[said[0]] = (counts[said[0]] || 0) + 1;
  if (marking[1] && marking[3]) both_busy++;
}
times.sort((a, b) => a - b);
const q = p => +times[Math.floor(p * (times.length - 1))].toFixed(3);
out.steps = { n: 2000, fired: counts, both_busy, final: marking, call_ms: { min: q(0), median: q(0.5), p90: q(0.9), max: q(1) } };
console.log("2,000 steps:", JSON.stringify(out.steps));
// the same 2,000 calls to the app's own JS handler (Fire of the transition Hazel's step would pick is not needed: a Fire(0) each time)
{ const tj = []; let mj = NET.marking.slice();
  for (let i = 0; i < 2000; i++) { const t0 = performance.now(); const cmd = jsHandler({ ...NET, marking: mj }, { tag: "Fire", value: i % 4 }); tj.push(performance.now() - t0); mj = perform(cmd, mj, []); }
  tj.sort((a, b) => a - b); out.js_call_ms = { median: +tj[1000].toFixed(4), p90: +tj[1800].toFixed(4) };
  console.log("JS handler:", JSON.stringify(out.js_call_ms)); }

// (b) a mistake in the rules: a name for a number. Hazel says where, by module; the app keeps using its JS handler
const wrong = RULES.replace("fire_at(n, i)", "fire_at(n, \"one\")");
const b2 = build(wrong);
out.with_error = { ok: b2.ok, errors: b2.errors, holes: b2.holes, incomplete: b2.incomplete,
  answered_by: handlerOf(b2) === jsHandler ? "the app's JS" : "Hazel",
  answer: perform(handlerOf(b2)({ ...NET, marking: NET.marking, draw: 0 }, { tag: "Fire", value: 0 }), NET.marking, said = []) && said.join("; ") };
console.log("with an error:", JSON.stringify(out.with_error));

// (c) a rule still being written: a hole where the Step case's answer goes. No error, but not ok
const unfinished = RULES.replace(/\| Step =>[\s\S]*end$/, "| Step => ?\n  end");
const b3 = build(unfinished);
out.unfinished = { ok: b3.ok, errors: b3.errors, holes: b3.holes, incomplete: b3.incomplete };
console.log("unfinished:", JSON.stringify(out.unfinished));

// (d) building again after one module changed, and again unchanged
const t1 = performance.now(); build(RULES + "\n"); const again = performance.now() - t1;
const t2 = performance.now(); build(RULES + "\n"); const same = performance.now() - t2;
out.rebuild_ms = { one_module_changed: +again.toFixed(1), unchanged: +same.toFixed(1) };
console.log("rebuild:", JSON.stringify(out.rebuild_ms));

// (e) the same 2,000 steps with the tail unannotated: ^report(25) found a call into Hazel re-checks a function's annotation
// at run time (the cast around it), which #2681 removes; hazeljs 0.0.4 is built from before it
{ const r = Hazel.runProgram({ ...spec(RULES), tail: "Rules.on_event" });
  let m = NET.marking.slice(); seed = 7; const ts = [];
  for (let i = 0; i < 2000; i++) { const t0 = performance.now(); const cmd = r.value({ ...NET, marking: m, draw: draw() }, { tag: "Step" }); ts.push(performance.now() - t0); m = perform(cmd, m, []); }
  ts.sort((a, b) => a - b); out.unannotated_tail_call_ms = { ok: r.ok, median: +ts[1000].toFixed(3), p90: +ts[1800].toFixed(3), final: m };
  console.log("tail unannotated:", JSON.stringify(out.unannotated_tail_call_ms)); }

writeFileSync(new URL("./run.json", import.meta.url), JSON.stringify(out, null, 1));
