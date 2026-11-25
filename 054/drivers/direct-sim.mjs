// (ticket 847, 2026-11-24) today's jit (idea C) with direct field reads, simulated: node --import ./node/direct-sim.mjs ...
// rewrites $R.dot(NAME, "k") in the text of each function made by Function(...) as hazelgrove/hazel e2529357f0 compiles e.k
// (only where the record is a JS name, so it understates what the compiler does). The games' own compiled.js is rewritten
// too, so a run under this has no ahead-of-time reference of its own.
const PROTO = new Set(["constructor", "hasOwnProperty", "isPrototypeOf", "propertyIsEnumerable", "toLocaleString", "toString", "valueOf", "__defineGetter__", "__defineSetter__", "__lookupGetter__", "__lookupSetter__"]);
let n = 0;
const rw = src => src.replace(/\$R\.dot\(([A-Za-z_$][\w$]*), ("[^"\\]*")\)/g, (m, v, k) => { if (PROTO.has(JSON.parse(k))) return m; n++;
  return `(${v} !== null && typeof ${v} === "object" && ${v}[${k}] !== undefined && (${v}.h === undefined || ${v}.t === undefined) ? ${v}[${k}] : $R.dot(${v}, ${k}))`; });
const F = globalThis.Function;
const fix = args => { if (args.length) args[args.length - 1] = rw(String(args[args.length - 1])); return args; };
globalThis.Function = new Proxy(F, { construct: (t, args) => Reflect.construct(t, fix(args)), apply: (t, th, args) => Reflect.apply(t, th, fix(args)) });
process.on("exit", () => console.log(`(direct reads simulated: ${n} field reads rewritten)`));
