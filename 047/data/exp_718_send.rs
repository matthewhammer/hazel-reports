//! ^ticket(718), ^report(47), experiment 1 (temporary, not to be committed): the Witch's picture as a Fumola
//! value, in from JSON and out through Value's own serde derive, timed in a native release build.
use fumola_semantics::value::Value;
use fumola_wasm::json_in::{value_of_json, value_of_json_text};
use std::time::Instant;

/// ms per call: batches of at least 25 ms, the median of five
fn per_op<F: FnMut()>(mut f: F) -> f64 {
    let mut xs = vec![];
    for _ in 0..5 {
        let t0 = Instant::now();
        let mut n = 0u64;
        while t0.elapsed().as_secs_f64() < 0.025 || n < 3 {
            f();
            n += 1;
        }
        xs.push(t0.elapsed().as_secs_f64() * 1000.0 / n as f64);
    }
    xs.sort_by(|a, b| a.partial_cmp(b).unwrap());
    xs[2]
}

#[test]
fn exp_718_send() {
    let path = std::env::var("PICTURE").expect("PICTURE: the picture's JSON file");
    let text = std::fs::read_to_string(path).unwrap();
    let v = value_of_json_text(&text).unwrap();
    let serde_out = serde_json::to_string(&*v).unwrap();
    let back: Value = serde_json::from_str(&serde_out).unwrap();
    assert!(back == *v, "the value read back is not the value written");
    let j: serde_json::Value = serde_json::from_str(&text).unwrap();
    let a = per_op(|| {
        let _ = value_of_json_text(&text).unwrap();
    });
    let b = per_op(|| {
        let _ = value_of_json(&j).unwrap();
    });
    let c = per_op(|| {
        let _ = serde_json::to_string(&*v).unwrap();
    });
    let d = per_op(|| {
        let _: Value = serde_json::from_str(&serde_out).unwrap();
    });
    println!(
        "EXP718 {{\"json_bytes\": {}, \"serde_json_bytes\": {}, \"ms\": {{\"json_text_to_value\": {:.4}, \"json_parsed_to_value\": {:.4}, \"value_to_serde_json\": {:.4}, \"serde_json_to_value\": {:.4}}}}}",
        text.len(), serde_out.len(), a, b, c, d
    );
}
