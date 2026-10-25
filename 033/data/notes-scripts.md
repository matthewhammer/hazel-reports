(research notes, 2026-10-25: the scripting side, from kids-choice-games main eee9446; S = dress-up/js/25-scripting.js, F = 25-fumola.js)
See the session record; key facts:
- Hazel type Globals (S:102), 16 fields; JS scriptNoGlobals (S:634) 17 (out_room folded into Out by scriptTypedGlobals S:75-83).
- Thing (S:100), Cell (S:101), sums Dir Side Wiring Out Place Room Exit (S:65-69).
- Cmd/Event (S:98-99). SCRIPT_ROOMS S:36-42; SCRIPT_ACTS S:636-690 (here/globals/act/done).
- TrapRoom fills lever_L/R wiring draws pits_on covered; TreeRoom only hatch (hatchHouse/hatchKey 26:592-593); Square only things (at = index in background.things); World at_col at_row cols rows cells; Castle rooms exits out out_room.
- Call path scriptEvent S:760, scriptEventRun S:770-809, scriptCmdApply S:617-632, scriptRun S:600-610; three snapshots.
- Guide ^du_report(17) ch11 says pits_on = which pits are open: wrong, it is "pit exists" (01:281,324); "17 fields" counts JS.

(cross-references, read 2026-10-25)
- Fumola, fumola.org #names-are-values: symbols are first-order data; `id, numbers, application nests (`adapton(`settings)); Symbol enum: Nat Int Id Call Dot BinOp UnOp QuotedAst (crates/fumola_semantics/src/lib/value.rs:106).
- fumola.org #space-and-time: a cell `x put in region `region is `region(`x): subcomputations name freely without colliding; time = revision; Adapton.here()/now()/space().
- fumola docs/cache-naming.md: content-derived vs identity-derived keys; identity keeps the node across change (Adapton, Fumola names).
- docs/fumola-for-haskell-folks.md: position-derived names multiply repair (139 vs 23-25): an address survives only as long as the shape it addresses -> the game's index ids (things' `at`, pits [0]/[1], castle room n, house n) are position-derived; diff with four outcomes equal/notEqual/onlyLeft/onlyRight needs names.
