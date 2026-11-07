(* report 043's Petri net rule, in OCaml as the Hazel is written, for Melange *)
type arc = { place : int; weight : int }
type transition = { name : string; inputs : arc list; outputs : arc list }
type net = { marking : int list; transitions : transition list; draw : float }
type event = Fire of int | Step
type cmd = Done | Take of int * int * cmd | Put of int * int * cmd | Say of string * cmd

let rec nth xs i = match xs with [] -> 0 | x :: rest -> if i = 0 then x else nth rest (i - 1)
let rec len xs = match xs with [] -> 0 | _ :: rest -> 1 + len rest
let rec pick ts i = match ts with [] -> None | t :: rest -> if i = 0 then Some t else pick rest (i - 1)
let rec has m arcs = match arcs with [] -> true | a :: rest -> nth m a.place >= a.weight && has m rest
let enabled m t = has m t.inputs
let rec ready m ts i =
  match ts with [] -> [] | t :: rest -> if enabled m t then i :: ready m rest (i + 1) else ready m rest (i + 1)
let rec takes arcs k = match arcs with [] -> k | a :: rest -> Take (a.place, a.weight, takes rest k)
let rec puts arcs k = match arcs with [] -> k | a :: rest -> Put (a.place, a.weight, puts rest k)
let fire t = Say (t.name, takes t.inputs (puts t.outputs Done))
let fire_at n i =
  match pick n.transitions i with
  | None -> Say ("there is no transition " ^ string_of_int i, Done)
  | Some t -> if enabled n.marking t then fire t else Say (t.name ^ " cannot fire now", Done)
let on_event n e =
  match e with
  | Fire i -> fire_at n i
  | Step ->
    let r = ready n.marking n.transitions 0 in
    let k = len r in
    if k = 0 then Say ("deadlock: nothing can fire", Done)
    else fire_at n (nth r (int_of_float (n.draw *. float_of_int k)))

let arc p = { place = p; weight = 1 }
let transitions = [
  { name = "enter1"; inputs = [ arc 0; arc 4 ]; outputs = [ arc 1 ] };
  { name = "leave1"; inputs = [ arc 1 ]; outputs = [ arc 0; arc 4 ] };
  { name = "enter2"; inputs = [ arc 2; arc 4 ]; outputs = [ arc 3 ] };
  { name = "leave2"; inputs = [ arc 3 ]; outputs = [ arc 2; arc 4 ] } ]

