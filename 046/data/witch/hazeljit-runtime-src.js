{
  append(a, b) { if (a === null) return b; const xs = []; for (let p = a; p !== null; p = p.t) xs.push(p.h);
    let r = b; for (let i = xs.length - 1; i >= 0; i--) r = {h: xs[i], t: r}; return r; },
  tup(vs, ls) { for (let i = 0; i < ls.length; i++) if (ls[i] !== null) vs[ls[i]] = vs[i]; return vs; },
  eq(a, b) {
    if (a === b) return true;
    if (a === null || b === null || typeof a !== "object" || typeof b !== "object") return false;
    if (Array.isArray(a)) { if (!Array.isArray(b) || a.length !== b.length) return false;
      for (let i = 0; i < a.length; i++) if (!this.eq(a[i], b[i])) return false; return true; }
    if ("c" in a) return ("c" in b) && a.c === b.c && this.eq(a.v, b.v);
    let p = a, q = b;
    while (p !== null && q !== null) { if (!this.eq(p.h, q.h)) return false; p = p.t; q = q.t; }
    return p === q;
  },
  nomatch(where) { throw new Error("hazel-jit: no pattern matched in " + where); },
  missing(why) { const f = () => { throw new Error("hazel-jit: not compiled: " + why); }; f.$missing = why; return f; },
  fn(f, k, e) { f.$k = k; f.$e = e; return f; },
  b: {
    string_of_int: n => String(n), string_of_sint: n => String(n), string_of_nat: n => String(n),
    string_of_bool: b => String(b),
    float_of_int: n => n, float_of_sint: n => n, float_of_nat: n => n,
    int_of_float: f => Math.trunc(f), sint_of_float: f => Math.trunc(f),
    int_of_sint: n => n, sint_of_int: n => n,
    int_of_string: s => { const n = Number(s); if (!Number.isInteger(n)) throw new Error("int_of_string"); return n; },
    float_of_string: s => Number(s),
    string_length: s => s.length, string_uppercase: s => s.toUpperCase(), string_lowercase: s => s.toLowerCase(),
    string_trim: s => s.trim(),
    abs: Math.abs, abs_float: Math.abs, ceil: Math.ceil, floor: Math.floor, round: Math.round,
    sqrt: Math.sqrt, exp: Math.exp, log: Math.log, log10: Math.log10,
    sin: Math.sin, cos: Math.cos, tan: Math.tan, asin: Math.asin, acos: Math.acos, atan: Math.atan,
    atan2: ([y, x]) => Math.atan2(y, x),
    float_min: ([a, b]) => Math.min(a, b), float_max: ([a, b]) => Math.max(a, b),
    int_mod: ([a, b]) => a % b, sint_mod: ([a, b]) => a % b, float_mod: ([a, b]) => a % b,
    to_fixed: ([x, n]) => x.toFixed(Math.min(Math.max(n, 0), 20)),
    fst: p => p[0], snd: p => p[1],
    is_nan: Number.isNaN, is_finite: Number.isFinite,
    pi: Math.PI, infinity: Infinity, neg_infinity: -Infinity, nan: NaN
  }
}