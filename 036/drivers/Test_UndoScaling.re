/* (probe, ^ticket(665)) What an edit, an undo and a redo cost as the
   program grows: a chain of n lets, an edit in the middle one, each step
   through the app's loop (Test_UndoCaches.step) and then the statics
   refresh the typing debounce would run. Prints one line per size; asserts
   nothing. */

module Cells = Test_Undo.Cells;
module OM = Test_OpenMember;
module UC = Test_UndoCaches;

let src = (n: int): string => {
  let b = Stdlib.Buffer.create(n * 24);
  Stdlib.Buffer.add_string(b, "let v0 = 0 in\n");
  for (i in 1 to n - 1) {
    Stdlib.Buffer.add_string(
      b,
      Printf.sprintf("let v%d = v%d + %d in\n", i, i - 1, i),
    );
  };
  Stdlib.Buffer.add_string(b, Printf.sprintf("v%d", n - 1));
  Stdlib.Buffer.contents(b);
};

let ms = (f: unit => 'a): ('a, float) => {
  let t0 = Sys.time();
  let r = f();
  (r, (Sys.time() -. t0) *. 1000.);
};

/* [action] through the app's loop as Main runs it: each frame's calculate
   is told whether its update was an edit (Main: ~is_edited=updated.is_edit),
   then the frames it scheduled (Test_UndoCaches.frames passes true for all) */
let rec frames = (m: Web.History.Model.t, action: Web.Page.Update.t) => {
  let scheduled = ref([]);
  let schedule_action = a => scheduled := scheduled^ @ [a];
  let updated =
    Web.History.Update.update(
      ~import_log=_ => (),
      ~get_log_and=_ => (),
      ~schedule_action,
      action,
      m,
    );
  let m =
    Web.History.Update.calculate(
      ~schedule_action,
      ~is_edited=updated.is_edit,
      ~dynamics=false,
      updated.model,
    );
  List.fold_left(
    ((m, n), a) => {
      let (m, k) = frames(m, a);
      (m, n + k);
    },
    (m, 1),
    scheduled^,
  );
};

let step = (m: Web.History.Model.t, action: Web.Page.Update.t) => {
  let (p0, m0, c0) = (
    Haz3lcore.MakeTerm.Incr.full_analyzed^,
    Haz3lcore.Measured.Incr.built^,
    Haz3lcore.DefStatics.head_compares^,
  );
  let (m, n) = frames(m, action);
  (
    m,
    UC.{
      frames: n,
      parsed: Haz3lcore.MakeTerm.Incr.full_analyzed^ - p0,
      measured: Haz3lcore.Measured.Incr.built^ - m0,
      compared: Haz3lcore.DefStatics.head_compares^ - c0,
    },
  );
};

/* one step: the action's frames, then the refresh; times and work of each */
type sample = {
  step_ms: float,
  refresh_ms: float,
  work: UC.work,
  refresh_work: UC.work,
};

let sample = (m, action) => {
  let ((m, work), step_ms) = ms(() => step(m, action));
  let ((m, refresh_work), refresh_ms) =
    ms(() => step(m, Editors(Scratch(RefreshStatics))));
  (
    m,
    {
      step_ms,
      refresh_ms,
      work,
      refresh_work,
    },
  );
};

let show = (s: sample) =>
  Printf.sprintf(
    "%7.1f+%7.1f ms (p%d m%d c%d | p%d m%d c%d)",
    s.step_ms,
    s.refresh_ms,
    s.work.parsed,
    s.work.measured,
    s.work.compared,
    s.refresh_work.parsed,
    s.refresh_work.measured,
    s.refresh_work.compared,
  );

let run_size = (n: int) => {
  let text = src(n);
  let mid = n / 2;
  let ((m, _), build_ms) =
    ms(() => UC.step(OM.mk(~root=Exp, text), Refresh));
  let m = OM.refresh(m);
  let m =
    OM.refresh(
      Cells.run(
        m,
        Globals(
          ActiveEditor(
            Move(
              Point(
                OM.after(text, Printf.sprintf("v%d + %d", mid - 1, mid)),
                None,
              ),
            ),
          ),
        ),
      ),
    );
  let steps = (m, k, action) => {
    let rec go = (m, k, acc) =>
      k == 0
        ? (m, List.rev(acc))
        : {
          let (m, s) = sample(m, action);
          go(m, k - 1, [s, ...acc]);
        };
    go(m, k, []);
  };
  let (m, edits) = steps(m, 4, Test_Undo.insert("1"));
  let (m, undos) = steps(m, 4, Test_Undo.undo);
  let (_, redos) = steps(m, 4, Test_Undo.redo);
  let line = (what, ss) =>
    Printf.printf(
      "UNDOSCALE n=%d %s: %s\n",
      n,
      what,
      String.concat(" | ", List.map(show, ss)),
    );
  Printf.printf("UNDOSCALE n=%d build: %.1f ms\n", n, build_ms);
  /* what the analysis sees: how many items DefStatics' chain makes of the
     term, the last one's form, and the info map's size */
  let st = UC.editor(m).editor.statics;
  let items = Haz3lcore.DefStatics.chain(st.term);
  let last = List.nth(items, List.length(items) - 1);
  Printf.printf(
    "UNDOSCALE n=%d shape: %d chain items, last %s, info map %d, errors %d\n",
    n,
    List.length(items),
    switch (Haz3lcore.DefStatics.strip(last).term) {
    | Let(_) => "Let"
    | Var(_) => "Var"
    | Parens(_) => "Parens"
    | Projector(_) => "Projector"
    | EmptyHole => "EmptyHole"
    | MultiHole(_) => "MultiHole"
    | _ => "other"
    },
    Haz3lcore.Id.Map.cardinal(st.info_map),
    List.length(st.error_ids),
  );
  line("edit", edits);
  line("undo", undos);
  line("redo", redos);
};

/* without the runner's checks, which the app doesn't run: monolithic
   statics after every calc, up to 3000 infos (DefStaticsCheck.install),
   and the global remold after every edit (NormalizeCheck.install) */
let unchecked = (f: unit => unit) => {
  let (statics, normalize) = (
    Haz3lcore.DefStatics.after_calc^,
    Haz3lcore.Zipper.normalize_check^,
  );
  Haz3lcore.DefStatics.after_calc := None;
  Haz3lcore.Zipper.normalize_check := None;
  Fun.protect(
    ~finally=
      () => {
        Haz3lcore.DefStatics.after_calc := statics;
        Haz3lcore.Zipper.normalize_check := normalize;
      },
    f,
  );
};

let sizes = () =>
  switch (Sys.getenv_opt("UNDO_SIZES")) {
  | Some(s) => List.map(int_of_string, String.split_on_char(',', s))
  | None => [100, 200, 400, 800, 1600, 3200]
  };

let tests = (
  "UndoScaling",
  [
    Alcotest.test_case("edit, undo and redo against program size", `Slow, () =>
      unchecked(() => List.iter(run_size, sizes()))
    ),
  ],
);
