// ^ticket(718), ^report(47), experiment 5, Fumola's side: the Witch's picture into a Fumola instance and back out
// to JS values, through fumola_wasm's own doors, in Node on the laptop.
//   in:  fumola_define_json(id, "pic", text)   JSON text -> a Fumola Value (json_in)
//   out: fumola_eval_top(id, "pic")            the Value -> the tagged JSON the Hazel side decodes (value_to_json),
//        then JSON.parse of that text           -> JS values
// Usage: node exp_718_fumola_js.js <dir of wasm-bindgen --target nodejs output> <picture.json>
const path = require("path");
const fs = require("fs");
const [dir, picture] = process.argv.slice(2);
const w = require(path.resolve(dir, "fumola_wasm.js"));
const text = fs.readFileSync(picture, "utf8");

// ms per call: batches of at least 25 ms, the median of five (as DataExperiment.per_op and exp_718_send.rs)
function perOp(f) {
  const xs = [];
  for (let b = 0; b < 5; b++) {
    const t0 = performance.now();
    let n = 0;
    while (performance.now() - t0 < 25 || n < 3) { f(); n++; }
    xs.push((performance.now() - t0) / n);
  }
  xs.sort((a, b) => a - b);
  return xs[2];
}

const id = w.fumola_create();
const def = JSON.parse(w.fumola_define_json(id, "pic", text));
if (!def.ok) throw new Error("define_json: " + JSON.stringify(def));
const outText = w.fumola_eval_top(id, "pic");
const out = JSON.parse(outText);
if (!out.ok) throw new Error("eval_top: " + outText.slice(0, 300));

const r = {
  about: "^report(47), experiment 5, Fumola's side: the Witch's picture (046/data/witch/picture.json) into a Fumola instance by " +
    "fumola_define_json, and out to JS values by fumola_eval_top (value_to_json, the tagged JSON the Hazel side decodes) then " +
    "JSON.parse. wasm32 release build, wasm-bindgen --target nodejs, Node " + process.version + " on the laptop; ms per call, the " +
    "median of five batches of at least 25 ms. This script is exp_718_fumola_js.js beside this file.",
  picture_bytes: Buffer.byteLength(text),
  out_bytes: Buffer.byteLength(outText),
  ms: {
    in_define_json: perOp(() => w.fumola_define_json(id, "pic", text)),
    out_eval_top: perOp(() => w.fumola_eval_top(id, "pic")),
    // the control: the same call on a constant, so what is left of out_eval_top is the value's translation and its text
    eval_top_constant: perOp(() => w.fumola_eval_top(id, "0")),
    out_json_parse: perOp(() => JSON.parse(outText)),
    plain_json_parse: perOp(() => JSON.parse(text)),
  },
};
r.ms.out_total = r.ms.out_eval_top + r.ms.out_json_parse;
r.ms.out_translate = r.ms.out_eval_top - r.ms.eval_top_constant;
console.log(JSON.stringify(r, null, 1));
