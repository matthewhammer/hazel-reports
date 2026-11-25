"use strict";
const k$None$26 = {$c: "None"};
const k$Done$73 = {$c: "Done"};
let let$1, let$2, nth$10, let$11, len$17, let$18, pick$27, let$28, has$36, let$37, enabled$41, let$42, ready$51, let$52, takes$60, let$61, puts$69, let$70, fire$74, Common$75, let$76, let$77, fire_at$83, let$84, on_event$96, Rules$97, let$98, let$99, places$100, let$101, arc$104, let$105, transitions$106, let$107, marking$108, let$109, place_at$110, let$111, transition_at$112, let$113, on_event$114, Main$115;
return (let$1 = (let$2 = (() => {
let nth$3;
return (nth$3 = $R.fn(function w$4(a$4) {
(Array.isArray(a$4) ? (a$4[$R.L] === undefined || $R.nolab(a$4, [0, 1])) : $R.indet("a pattern by position against a labeled entry")) || $R.nomatch("fun");
return w$4.$d(a$4[0], a$4[1]);
}, 0, [nth$3], (a$4_0, a$4_1) => {
for (;;) {
let xs$5, i$6, m$7, x$8, rest$9;
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
xs$5 = a$4_0;
i$6 = a$4_1;
m$7 = xs$5;
if ((m$7 === null)) {
return 0;
} else {
if ((m$7 !== null)) {
x$8 = m$7.$h;
rest$9 = m$7.$t;
if ((i$6 === 0)) {
return x$8;
} else {
a$4_0 = rest$9;
a$4_1 = $R.isub(i$6, 1);
continue;
} } else {
return $R.nomatch("case");
} } } }), nth$3);
})(), nth$10 = let$2, (let$11 = (() => {
let len$12;
return (len$12 = $R.fn((a$13) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let xs$14, m$15, rest$16;
xs$14 = a$13;
m$15 = xs$14;
if ((m$15 === null)) {
return 0;
} else {
if ((m$15 !== null)) {
rest$16 = m$15.$t;
return $R.iadd(1, (len$12)(rest$16));
} else {
return $R.nomatch("case");
} } }, 1, [len$12]), len$12);
})(), len$17 = let$11, (let$18 = (() => {
let pick$19;
return (pick$19 = $R.fn(function w$20(a$20) {
(Array.isArray(a$20) ? (a$20[$R.L] === undefined || $R.nolab(a$20, [0, 1])) : $R.indet("a pattern by position against a labeled entry")) || $R.nomatch("fun");
return w$20.$d(a$20[0], a$20[1]);
}, 2, [pick$19], (a$20_0, a$20_1) => {
for (;;) {
let ts$21, i$22, m$23, t$24, rest$25;
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
ts$21 = a$20_0;
i$22 = a$20_1;
m$23 = ts$21;
if ((m$23 === null)) {
return k$None$26;
} else {
if ((m$23 !== null)) {
t$24 = m$23.$h;
rest$25 = m$23.$t;
if ((i$22 === 0)) {
return {$c: "Some", $v: t$24};
} else {
a$20_0 = rest$25;
a$20_1 = $R.isub(i$22, 1);
continue;
} } else {
return $R.nomatch("case");
} } } }), pick$19);
})(), pick$27 = let$18, (let$28 = (() => {
let has$29;
return (has$29 = $R.fn(function w$30(a$30) {
(Array.isArray(a$30) ? (a$30[$R.L] === undefined || $R.nolab(a$30, [0, 1])) : $R.indet("a pattern by position against a labeled entry")) || $R.nomatch("fun");
return w$30.$d(a$30[0], a$30[1]);
}, 3, [has$29, nth$10], (a$30_0, a$30_1) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let m$31, arcs$32, m$33, a$34, rest$35;
m$31 = a$30_0;
arcs$32 = a$30_1;
m$33 = arcs$32;
if ((m$33 === null)) {
return true;
} else {
if ((m$33 !== null)) {
a$34 = m$33.$h;
rest$35 = m$33.$t;
return ((nth$10.$d(m$31, (a$34 !== null && typeof a$34 === "object" && a$34["place"] !== undefined && a$34.$t === undefined ? a$34["place"] : $R.dot(a$34, "place"))) >= (a$34 !== null && typeof a$34 === "object" && a$34["weight"] !== undefined && a$34.$t === undefined ? a$34["weight"] : $R.dot(a$34, "weight"))) && has$29.$d(m$31, rest$35));
} else {
return $R.nomatch("case");
} } }), has$29);
})(), has$36 = let$28, (let$37 = $R.fn(function w$38(a$38) {
(Array.isArray(a$38) ? (a$38[$R.L] === undefined || $R.nolab(a$38, [0, 1])) : $R.indet("a pattern by position against a labeled entry")) || $R.nomatch("fun");
return w$38.$d(a$38[0], a$38[1]);
}, 4, [has$36], (a$38_0, a$38_1) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let m$39, t$40;
return (m$39 = a$38_0, t$40 = a$38_1, has$36.$d(m$39, (t$40 !== null && typeof t$40 === "object" && t$40["inputs"] !== undefined && t$40.$t === undefined ? t$40["inputs"] : $R.dot(t$40, "inputs"))));
}), enabled$41 = let$37, (let$42 = (() => {
let ready$43;
return (ready$43 = $R.fn(function w$44(a$44) {
(Array.isArray(a$44) ? (a$44[$R.L] === undefined || $R.nolab(a$44, [0, 1, 2])) : $R.indet("a pattern by position against a labeled entry")) || $R.nomatch("fun");
return w$44.$d(a$44[0], a$44[1], a$44[2]);
}, 5, [ready$43, enabled$41], (a$44_0, a$44_1, a$44_2) => {
for (;;) {
let m$45, ts$46, i$47, m$48, t$49, rest$50;
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
m$45 = a$44_0;
ts$46 = a$44_1;
i$47 = a$44_2;
m$48 = ts$46;
if ((m$48 === null)) {
return null;
} else {
if ((m$48 !== null)) {
t$49 = m$48.$h;
rest$50 = m$48.$t;
if (enabled$41.$d(m$45, t$49)) {
return {$h: i$47, $t: ready$43.$d(m$45, rest$50, $R.iadd(i$47, 1))};
} else {
a$44_0 = m$45;
a$44_1 = rest$50;
a$44_2 = $R.iadd(i$47, 1);
continue;
} } else {
return $R.nomatch("case");
} } } }), ready$43);
})(), ready$51 = let$42, (let$52 = (() => {
let takes$53;
return (takes$53 = $R.fn(function w$54(a$54) {
(Array.isArray(a$54) ? (a$54[$R.L] === undefined || $R.nolab(a$54, [0, 1])) : $R.indet("a pattern by position against a labeled entry")) || $R.nomatch("fun");
return w$54.$d(a$54[0], a$54[1]);
}, 6, [takes$53], (a$54_0, a$54_1) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let arcs$55, k$56, m$57, a$58, rest$59;
arcs$55 = a$54_0;
k$56 = a$54_1;
m$57 = arcs$55;
if ((m$57 === null)) {
return k$56;
} else {
if ((m$57 !== null)) {
a$58 = m$57.$h;
rest$59 = m$57.$t;
return {$c: "Take", $v: [(a$58 !== null && typeof a$58 === "object" && a$58["place"] !== undefined && a$58.$t === undefined ? a$58["place"] : $R.dot(a$58, "place")), (a$58 !== null && typeof a$58 === "object" && a$58["weight"] !== undefined && a$58.$t === undefined ? a$58["weight"] : $R.dot(a$58, "weight")), takes$53.$d(rest$59, k$56)]};
} else {
return $R.nomatch("case");
} } }), takes$53);
})(), takes$60 = let$52, (let$61 = (() => {
let puts$62;
return (puts$62 = $R.fn(function w$63(a$63) {
(Array.isArray(a$63) ? (a$63[$R.L] === undefined || $R.nolab(a$63, [0, 1])) : $R.indet("a pattern by position against a labeled entry")) || $R.nomatch("fun");
return w$63.$d(a$63[0], a$63[1]);
}, 7, [puts$62], (a$63_0, a$63_1) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let arcs$64, k$65, m$66, a$67, rest$68;
arcs$64 = a$63_0;
k$65 = a$63_1;
m$66 = arcs$64;
if ((m$66 === null)) {
return k$65;
} else {
if ((m$66 !== null)) {
a$67 = m$66.$h;
rest$68 = m$66.$t;
return {$c: "Put", $v: [(a$67 !== null && typeof a$67 === "object" && a$67["place"] !== undefined && a$67.$t === undefined ? a$67["place"] : $R.dot(a$67, "place")), (a$67 !== null && typeof a$67 === "object" && a$67["weight"] !== undefined && a$67.$t === undefined ? a$67["weight"] : $R.dot(a$67, "weight")), puts$62.$d(rest$68, k$65)]};
} else {
return $R.nomatch("case");
} } }), puts$62);
})(), puts$69 = let$61, (let$70 = $R.fn((a$71) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let t$72;
return (t$72 = a$71, {$c: "Say", $v: [(t$72 !== null && typeof t$72 === "object" && t$72["name"] !== undefined && t$72.$t === undefined ? t$72["name"] : $R.dot(t$72, "name")), takes$60.$d((t$72 !== null && typeof t$72 === "object" && t$72["inputs"] !== undefined && t$72.$t === undefined ? t$72["inputs"] : $R.dot(t$72, "inputs")), puts$69.$d((t$72 !== null && typeof t$72 === "object" && t$72["outputs"] !== undefined && t$72.$t === undefined ? t$72["outputs"] : $R.dot(t$72, "outputs")), k$Done$73))]});
}, 8, [takes$60, puts$69]), fire$74 = let$70, ({"nth": nth$10, "len": len$17, "pick": pick$27, "has": has$36, "enabled": enabled$41, "ready": ready$51, "takes": takes$60, "puts": puts$69, "fire": fire$74})))))))))), Common$75 = let$1, (let$76 = (let$77 = $R.fn(function w$78(a$78) {
(Array.isArray(a$78) ? (a$78[$R.L] === undefined || $R.nolab(a$78, [0, 1])) : $R.indet("a pattern by position against a labeled entry")) || $R.nomatch("fun");
return w$78.$d(a$78[0], a$78[1]);
}, 9, [Common$75], (a$78_0, a$78_1) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let n$79, i$80, m$81, t$82;
return (n$79 = a$78_0, i$80 = a$78_1, (m$81 = pick$27.$d((n$79 !== null && typeof n$79 === "object" && n$79["transitions"] !== undefined && n$79.$t === undefined ? n$79["transitions"] : $R.dot(n$79, "transitions")), i$80), ((m$81.$c === "None") ? ({$c: "Say", $v: [("there is no transition " + ($R.b["string_of_int"])(i$80)), k$Done$73]}) : ((m$81.$c === "Some") ? (t$82 = m$81.$v, (enabled$41.$d((n$79 !== null && typeof n$79 === "object" && n$79["marking"] !== undefined && n$79.$t === undefined ? n$79["marking"] : $R.dot(n$79, "marking")), t$82) ? (fire$74)(t$82) : {$c: "Say", $v: [((t$82 !== null && typeof t$82 === "object" && t$82["name"] !== undefined && t$82.$t === undefined ? t$82["name"] : $R.dot(t$82, "name")) + " cannot fire now"), k$Done$73]})) : $R.nomatch("case")))));
}), fire_at$83 = let$77, (let$84 = $R.fn(function w$85(a$85) {
(Array.isArray(a$85) ? (a$85[$R.L] === undefined || $R.nolab(a$85, [0, 1])) : $R.indet("a pattern by position against a labeled entry")) || $R.nomatch("fun");
return w$85.$d(a$85[0], a$85[1]);
}, 10, [Common$75, fire_at$83], (a$85_0, a$85_1) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let n$86, e$87, m$88, let$89, r$90, let$91, k$92, let$93, j$94, i$95;
return (n$86 = a$85_0, e$87 = a$85_1, (m$88 = e$87, ((m$88.$c === "Fire") ? (i$95 = m$88.$v, fire_at$83.$d(n$86, i$95)) : ((m$88.$c === "Step") ? ((let$89 = ready$51.$d((n$86 !== null && typeof n$86 === "object" && n$86["marking"] !== undefined && n$86.$t === undefined ? n$86["marking"] : $R.dot(n$86, "marking")), (n$86 !== null && typeof n$86 === "object" && n$86["transitions"] !== undefined && n$86.$t === undefined ? n$86["transitions"] : $R.dot(n$86, "transitions")), 0), r$90 = let$89, (let$91 = (len$17)(r$90), k$92 = let$91, ((k$92 === 0) ? {$c: "Say", $v: ["deadlock: nothing can fire", k$Done$73]} : (let$93 = ($R.b["int_of_float"])(((n$86 !== null && typeof n$86 === "object" && n$86["draw"] !== undefined && n$86.$t === undefined ? n$86["draw"] : $R.dot(n$86, "draw")) * ($R.b["float_of_int"])(k$92))), j$94 = let$93, fire_at$83.$d(n$86, nth$10.$d(r$90, j$94))))))) : $R.nomatch("case")))));
}), on_event$96 = let$84, ({"fire_at": fire_at$83, "on_event": on_event$96}))), Rules$97 = let$76, (let$98 = (let$99 = {$h: "idle1", $t: {$h: "busy1", $t: {$h: "idle2", $t: {$h: "busy2", $t: {$h: "lock", $t: null}}}}}, places$100 = let$99, (let$101 = $R.fn((a$102) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let p$103;
return (p$103 = a$102, ({"place": p$103, "weight": 1}));
}, 11, null), arc$104 = let$101, (let$105 = {$h: ({"name": "enter1", "inputs": {$h: (arc$104)(0), $t: {$h: (arc$104)(4), $t: null}}, "outputs": {$h: (arc$104)(1), $t: null}}), $t: {$h: ({"name": "leave1", "inputs": {$h: (arc$104)(1), $t: null}, "outputs": {$h: (arc$104)(0), $t: {$h: (arc$104)(4), $t: null}}}), $t: {$h: ({"name": "enter2", "inputs": {$h: (arc$104)(2), $t: {$h: (arc$104)(4), $t: null}}, "outputs": {$h: (arc$104)(3), $t: null}}), $t: {$h: ({"name": "leave2", "inputs": {$h: (arc$104)(3), $t: null}, "outputs": {$h: (arc$104)(2), $t: {$h: (arc$104)(4), $t: null}}}), $t: null}}}}, transitions$106 = let$105, (let$107 = {$h: 1, $t: {$h: 0, $t: {$h: 1, $t: {$h: 0, $t: {$h: 1, $t: null}}}}}, marking$108 = let$107, (let$109 = {$h: ({"x": 150, "y": 50}), $t: {$h: ({"x": 150, "y": 250}), $t: {$h: ({"x": 550, "y": 50}), $t: {$h: ({"x": 550, "y": 250}), $t: {$h: ({"x": 350, "y": 150}), $t: null}}}}}, place_at$110 = let$109, (let$111 = {$h: ({"x": 238, "y": 150}), $t: {$h: ({"x": 62, "y": 150}), $t: {$h: ({"x": 462, "y": 150}), $t: {$h: ({"x": 638, "y": 150}), $t: null}}}}, transition_at$112 = let$111, (let$113 = on_event$96, on_event$114 = let$113, ({"places": places$100, "arc": arc$104, "transitions": transitions$106, "marking": marking$108, "place_at": place_at$110, "transition_at": transition_at$112, "on_event": on_event$114})))))))), Main$115 = let$98, ({"transitions": transitions$106, "marking": marking$108, "on_event": on_event$114}))));