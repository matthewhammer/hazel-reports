// report 043's Petri net rule (matthewhammer/hazeljs-petri-example, rules/), written in ReScript as the Hazel is written
type arc = {place: int, weight: int}
type transition = {name: string, inputs: list<arc>, outputs: list<arc>}
type net = {marking: list<int>, transitions: list<transition>, draw: float}
type event = Fire(int) | Step
type rec cmd = Done | Take(int, int, cmd) | Put(int, int, cmd) | Say(string, cmd)

let rec nth = (xs, i) =>
  switch xs {
  | list{} => 0
  | list{x, ...rest} => i == 0 ? x : nth(rest, i - 1)
  }
let rec len = xs =>
  switch xs {
  | list{} => 0
  | list{_, ...rest} => 1 + len(rest)
  }
let rec pick = (ts, i) =>
  switch ts {
  | list{} => None
  | list{t, ...rest} => i == 0 ? Some(t) : pick(rest, i - 1)
  }
let rec has = (m, arcs) =>
  switch arcs {
  | list{} => true
  | list{a, ...rest} => nth(m, a.place) >= a.weight && has(m, rest)
  }
let enabled = (m, t) => has(m, t.inputs)
let rec ready = (m, ts, i) =>
  switch ts {
  | list{} => list{}
  | list{t, ...rest} => enabled(m, t) ? list{i, ...ready(m, rest, i + 1)} : ready(m, rest, i + 1)
  }
let rec takes = (arcs, k) =>
  switch arcs {
  | list{} => k
  | list{a, ...rest} => Take(a.place, a.weight, takes(rest, k))
  }
let rec puts = (arcs, k) =>
  switch arcs {
  | list{} => k
  | list{a, ...rest} => Put(a.place, a.weight, puts(rest, k))
  }
let fire = t => Say(t.name, takes(t.inputs, puts(t.outputs, Done)))

let fire_at = (n, i) =>
  switch pick(n.transitions, i) {
  | None => Say("there is no transition " ++ Int.toString(i), Done)
  | Some(t) => enabled(n.marking, t) ? fire(t) : Say(t.name ++ " cannot fire now", Done)
  }
let on_event = (n, e) =>
  switch e {
  | Fire(i) => fire_at(n, i)
  | Step =>
    let r = ready(n.marking, n.transitions, 0)
    let k = len(r)
    if k == 0 {
      Say("deadlock: nothing can fire", Done)
    } else {
      let j = Float.toInt(n.draw *. Int.toFloat(k))
      fire_at(n, nth(r, j))
    }
  }

// the net, as rules/Main.hz has it
let arc = p => {place: p, weight: 1}
let transitions = list{
  {name: "enter1", inputs: list{arc(0), arc(4)}, outputs: list{arc(1)}},
  {name: "leave1", inputs: list{arc(1)}, outputs: list{arc(0), arc(4)}},
  {name: "enter2", inputs: list{arc(2), arc(4)}, outputs: list{arc(3)}},
  {name: "leave2", inputs: list{arc(3)}, outputs: list{arc(2), arc(4)}},
}
let marking = list{1, 0, 1, 0, 1}
