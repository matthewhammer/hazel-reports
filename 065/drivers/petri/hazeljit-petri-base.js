"use strict";
 let let$1, let$2, nth$10, let$11, len$17, let$18, pick$26, let$27, has$35, let$36, enabled$40, let$41, ready$50, let$51, takes$59, let$60, puts$68, let$69, fire$72, Common$73, let$74, let$75, fire_at$81, let$82, on_event$94, Rules$95, let$96, let$97, places$98, let$99, arc$102, let$103, transitions$104, let$105, marking$106, let$107, place_at$108, let$109, transition_at$110, let$111, on_event$112, Main$113;
return (let$1 = (let$2 = (() => {
let nth$3;
return (nth$3 = $R.fn((a$4) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let xs$5, i$6, m$7, x$8, rest$9;
return (((Array.isArray(a$4) ? (a$4[$R.L] === undefined || $R.nolab(a$4, [0, 1])) : $R.indet("a pattern by position against a labeled entry"))) || $R.nomatch("fun"), xs$5 = a$4[0], i$6 = a$4[1], (m$7 = xs$5, ((m$7 === null) ? (0) : ((m$7 !== null) ? (x$8 = m$7.$h, rest$9 = m$7.$t, ($R.eq(i$6, 0) ? x$8 : (nth$3)([rest$9, $R.isub(i$6, 1)]))) : $R.nomatch("case")))));
}, 0, [nth$3]), nth$3);
})(), nth$10 = let$2, (let$11 = (() => {
let len$12;
return (len$12 = $R.fn((a$13) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let xs$14, m$15, rest$16;
return (xs$14 = a$13, (m$15 = xs$14, ((m$15 === null) ? (0) : ((m$15 !== null) ? (rest$16 = m$15.$t, $R.iadd(1, (len$12)(rest$16))) : $R.nomatch("case")))));
}, 1, [len$12]), len$12);
})(), len$17 = let$11, (let$18 = (() => {
let pick$19;
return (pick$19 = $R.fn((a$20) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let ts$21, i$22, m$23, t$24, rest$25;
return (((Array.isArray(a$20) ? (a$20[$R.L] === undefined || $R.nolab(a$20, [0, 1])) : $R.indet("a pattern by position against a labeled entry"))) || $R.nomatch("fun"), ts$21 = a$20[0], i$22 = a$20[1], (m$23 = ts$21, ((m$23 === null) ? ({$c: "None"}) : ((m$23 !== null) ? (t$24 = m$23.$h, rest$25 = m$23.$t, ($R.eq(i$22, 0) ? {$c: "Some", $v: t$24} : (pick$19)([rest$25, $R.isub(i$22, 1)]))) : $R.nomatch("case")))));
}, 2, [pick$19]), pick$19);
})(), pick$26 = let$18, (let$27 = (() => {
let has$28;
return (has$28 = $R.fn((a$29) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let m$30, arcs$31, m$32, a$33, rest$34;
return (((Array.isArray(a$29) ? (a$29[$R.L] === undefined || $R.nolab(a$29, [0, 1])) : $R.indet("a pattern by position against a labeled entry"))) || $R.nomatch("fun"), m$30 = a$29[0], arcs$31 = a$29[1], (m$32 = arcs$31, ((m$32 === null) ? (true) : ((m$32 !== null) ? (a$33 = m$32.$h, rest$34 = m$32.$t, (((nth$10)([m$30, (a$33 !== null && typeof a$33 === "object" && a$33["place"] !== undefined && a$33.$t === undefined ? a$33["place"] : $R.dot(a$33, "place"))]) >= (a$33 !== null && typeof a$33 === "object" && a$33["weight"] !== undefined && a$33.$t === undefined ? a$33["weight"] : $R.dot(a$33, "weight"))) && (has$28)([m$30, rest$34]))) : $R.nomatch("case")))));
}, 3, [has$28, nth$10]), has$28);
})(), has$35 = let$27, (let$36 = $R.fn((a$37) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let m$38, t$39;
return (((Array.isArray(a$37) ? (a$37[$R.L] === undefined || $R.nolab(a$37, [0, 1])) : $R.indet("a pattern by position against a labeled entry"))) || $R.nomatch("fun"), m$38 = a$37[0], t$39 = a$37[1], (has$35)([m$38, (t$39 !== null && typeof t$39 === "object" && t$39["inputs"] !== undefined && t$39.$t === undefined ? t$39["inputs"] : $R.dot(t$39, "inputs"))]));
}, 4, [has$35]), enabled$40 = let$36, (let$41 = (() => {
let ready$42;
return (ready$42 = $R.fn((a$43) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let m$44, ts$45, i$46, m$47, t$48, rest$49;
return (((Array.isArray(a$43) ? (a$43[$R.L] === undefined || $R.nolab(a$43, [0, 1, 2])) : $R.indet("a pattern by position against a labeled entry"))) || $R.nomatch("fun"), m$44 = a$43[0], ts$45 = a$43[1], i$46 = a$43[2], (m$47 = ts$45, ((m$47 === null) ? (null) : ((m$47 !== null) ? (t$48 = m$47.$h, rest$49 = m$47.$t, ((enabled$40)([m$44, t$48]) ? {$h: i$46, $t: (ready$42)([m$44, rest$49, $R.iadd(i$46, 1)])} : (ready$42)([m$44, rest$49, $R.iadd(i$46, 1)]))) : $R.nomatch("case")))));
}, 5, [ready$42, enabled$40]), ready$42);
})(), ready$50 = let$41, (let$51 = (() => {
let takes$52;
return (takes$52 = $R.fn((a$53) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let arcs$54, k$55, m$56, a$57, rest$58;
return (((Array.isArray(a$53) ? (a$53[$R.L] === undefined || $R.nolab(a$53, [0, 1])) : $R.indet("a pattern by position against a labeled entry"))) || $R.nomatch("fun"), arcs$54 = a$53[0], k$55 = a$53[1], (m$56 = arcs$54, ((m$56 === null) ? (k$55) : ((m$56 !== null) ? (a$57 = m$56.$h, rest$58 = m$56.$t, {$c: "Take", $v: [(a$57 !== null && typeof a$57 === "object" && a$57["place"] !== undefined && a$57.$t === undefined ? a$57["place"] : $R.dot(a$57, "place")), (a$57 !== null && typeof a$57 === "object" && a$57["weight"] !== undefined && a$57.$t === undefined ? a$57["weight"] : $R.dot(a$57, "weight")), (takes$52)([rest$58, k$55])]}) : $R.nomatch("case")))));
}, 6, [takes$52]), takes$52);
})(), takes$59 = let$51, (let$60 = (() => {
let puts$61;
return (puts$61 = $R.fn((a$62) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let arcs$63, k$64, m$65, a$66, rest$67;
return (((Array.isArray(a$62) ? (a$62[$R.L] === undefined || $R.nolab(a$62, [0, 1])) : $R.indet("a pattern by position against a labeled entry"))) || $R.nomatch("fun"), arcs$63 = a$62[0], k$64 = a$62[1], (m$65 = arcs$63, ((m$65 === null) ? (k$64) : ((m$65 !== null) ? (a$66 = m$65.$h, rest$67 = m$65.$t, {$c: "Put", $v: [(a$66 !== null && typeof a$66 === "object" && a$66["place"] !== undefined && a$66.$t === undefined ? a$66["place"] : $R.dot(a$66, "place")), (a$66 !== null && typeof a$66 === "object" && a$66["weight"] !== undefined && a$66.$t === undefined ? a$66["weight"] : $R.dot(a$66, "weight")), (puts$61)([rest$67, k$64])]}) : $R.nomatch("case")))));
}, 7, [puts$61]), puts$61);
})(), puts$68 = let$60, (let$69 = $R.fn((a$70) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let t$71;
return (t$71 = a$70, {$c: "Say", $v: [(t$71 !== null && typeof t$71 === "object" && t$71["name"] !== undefined && t$71.$t === undefined ? t$71["name"] : $R.dot(t$71, "name")), (takes$59)([(t$71 !== null && typeof t$71 === "object" && t$71["inputs"] !== undefined && t$71.$t === undefined ? t$71["inputs"] : $R.dot(t$71, "inputs")), (puts$68)([(t$71 !== null && typeof t$71 === "object" && t$71["outputs"] !== undefined && t$71.$t === undefined ? t$71["outputs"] : $R.dot(t$71, "outputs")), {$c: "Done"}])])]});
}, 8, [puts$68, takes$59]), fire$72 = let$69, ({"nth": nth$10, "len": len$17, "pick": pick$26, "has": has$35, "enabled": enabled$40, "ready": ready$50, "takes": takes$59, "puts": puts$68, "fire": fire$72})))))))))), Common$73 = let$1, (let$74 = (let$75 = $R.fn((a$76) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let n$77, i$78, m$79, t$80;
return (((Array.isArray(a$76) ? (a$76[$R.L] === undefined || $R.nolab(a$76, [0, 1])) : $R.indet("a pattern by position against a labeled entry"))) || $R.nomatch("fun"), n$77 = a$76[0], i$78 = a$76[1], (m$79 = ((Common$73 !== null && typeof Common$73 === "object" && Common$73["pick"] !== undefined && Common$73.$t === undefined ? Common$73["pick"] : $R.dot(Common$73, "pick")))([(n$77 !== null && typeof n$77 === "object" && n$77["transitions"] !== undefined && n$77.$t === undefined ? n$77["transitions"] : $R.dot(n$77, "transitions")), i$78]), ((m$79.$c === "None") ? ({$c: "Say", $v: [("there is no transition " + ($R.b["string_of_int"])(i$78)), {$c: "Done"}]}) : ((m$79.$c === "Some") ? (t$80 = m$79.$v, (((Common$73 !== null && typeof Common$73 === "object" && Common$73["enabled"] !== undefined && Common$73.$t === undefined ? Common$73["enabled"] : $R.dot(Common$73, "enabled")))([(n$77 !== null && typeof n$77 === "object" && n$77["marking"] !== undefined && n$77.$t === undefined ? n$77["marking"] : $R.dot(n$77, "marking")), t$80]) ? ((Common$73 !== null && typeof Common$73 === "object" && Common$73["fire"] !== undefined && Common$73.$t === undefined ? Common$73["fire"] : $R.dot(Common$73, "fire")))(t$80) : {$c: "Say", $v: [((t$80 !== null && typeof t$80 === "object" && t$80["name"] !== undefined && t$80.$t === undefined ? t$80["name"] : $R.dot(t$80, "name")) + " cannot fire now"), {$c: "Done"}]})) : $R.nomatch("case")))));
}, 9, [Common$73]), fire_at$81 = let$75, (let$82 = $R.fn((a$83) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let n$84, e$85, m$86, let$87, r$88, let$89, k$90, let$91, j$92, i$93;
return (((Array.isArray(a$83) ? (a$83[$R.L] === undefined || $R.nolab(a$83, [0, 1])) : $R.indet("a pattern by position against a labeled entry"))) || $R.nomatch("fun"), n$84 = a$83[0], e$85 = a$83[1], (m$86 = e$85, ((m$86.$c === "Fire") ? (i$93 = m$86.$v, (fire_at$81)([n$84, i$93])) : ((m$86.$c === "Step") ? ((let$87 = ((Common$73 !== null && typeof Common$73 === "object" && Common$73["ready"] !== undefined && Common$73.$t === undefined ? Common$73["ready"] : $R.dot(Common$73, "ready")))([(n$84 !== null && typeof n$84 === "object" && n$84["marking"] !== undefined && n$84.$t === undefined ? n$84["marking"] : $R.dot(n$84, "marking")), (n$84 !== null && typeof n$84 === "object" && n$84["transitions"] !== undefined && n$84.$t === undefined ? n$84["transitions"] : $R.dot(n$84, "transitions")), 0]), r$88 = let$87, (let$89 = ((Common$73 !== null && typeof Common$73 === "object" && Common$73["len"] !== undefined && Common$73.$t === undefined ? Common$73["len"] : $R.dot(Common$73, "len")))(r$88), k$90 = let$89, ($R.eq(k$90, 0) ? {$c: "Say", $v: ["deadlock: nothing can fire", {$c: "Done"}]} : (let$91 = ($R.b["int_of_float"])(((n$84 !== null && typeof n$84 === "object" && n$84["draw"] !== undefined && n$84.$t === undefined ? n$84["draw"] : $R.dot(n$84, "draw")) * ($R.b["float_of_int"])(k$90))), j$92 = let$91, (fire_at$81)([n$84, ((Common$73 !== null && typeof Common$73 === "object" && Common$73["nth"] !== undefined && Common$73.$t === undefined ? Common$73["nth"] : $R.dot(Common$73, "nth")))([r$88, j$92])])))))) : $R.nomatch("case")))));
}, 10, [Common$73, fire_at$81]), on_event$94 = let$82, ({"fire_at": fire_at$81, "on_event": on_event$94}))), Rules$95 = let$74, (let$96 = (let$97 = {$h: "idle1", $t: {$h: "busy1", $t: {$h: "idle2", $t: {$h: "busy2", $t: {$h: "lock", $t: null}}}}}, places$98 = let$97, (let$99 = $R.fn((a$100) => {
if (--$R.fuel < 0 || (($R.fuel & 16383) === 0 && performance.now() > $R.deadline)) $R.out();
let p$101;
return (p$101 = a$100, ({"place": p$101, "weight": 1}));
}, 11, null), arc$102 = let$99, (let$103 = {$h: ({"name": "enter1", "inputs": {$h: (arc$102)(0), $t: {$h: (arc$102)(4), $t: null}}, "outputs": {$h: (arc$102)(1), $t: null}}), $t: {$h: ({"name": "leave1", "inputs": {$h: (arc$102)(1), $t: null}, "outputs": {$h: (arc$102)(0), $t: {$h: (arc$102)(4), $t: null}}}), $t: {$h: ({"name": "enter2", "inputs": {$h: (arc$102)(2), $t: {$h: (arc$102)(4), $t: null}}, "outputs": {$h: (arc$102)(3), $t: null}}), $t: {$h: ({"name": "leave2", "inputs": {$h: (arc$102)(3), $t: null}, "outputs": {$h: (arc$102)(2), $t: {$h: (arc$102)(4), $t: null}}}), $t: null}}}}, transitions$104 = let$103, (let$105 = {$h: 1, $t: {$h: 0, $t: {$h: 1, $t: {$h: 0, $t: {$h: 1, $t: null}}}}}, marking$106 = let$105, (let$107 = {$h: ({"x": 150, "y": 50}), $t: {$h: ({"x": 150, "y": 250}), $t: {$h: ({"x": 550, "y": 50}), $t: {$h: ({"x": 550, "y": 250}), $t: {$h: ({"x": 350, "y": 150}), $t: null}}}}}, place_at$108 = let$107, (let$109 = {$h: ({"x": 238, "y": 150}), $t: {$h: ({"x": 62, "y": 150}), $t: {$h: ({"x": 462, "y": 150}), $t: {$h: ({"x": 638, "y": 150}), $t: null}}}}, transition_at$110 = let$109, (let$111 = (Rules$95 !== null && typeof Rules$95 === "object" && Rules$95["on_event"] !== undefined && Rules$95.$t === undefined ? Rules$95["on_event"] : $R.dot(Rules$95, "on_event")), on_event$112 = let$111, ({"places": places$98, "arc": arc$102, "transitions": transitions$104, "marking": marking$106, "place_at": place_at$108, "transition_at": transition_at$110, "on_event": on_event$112})))))))), Main$113 = let$96, ({"transitions": (Main$113 !== null && typeof Main$113 === "object" && Main$113["transitions"] !== undefined && Main$113.$t === undefined ? Main$113["transitions"] : $R.dot(Main$113, "transitions")), "marking": (Main$113 !== null && typeof Main$113 === "object" && Main$113["marking"] !== undefined && Main$113.$t === undefined ? Main$113["marking"] : $R.dot(Main$113, "marking")), "on_event": (Main$113 !== null && typeof Main$113 === "object" && Main$113["on_event"] !== undefined && Main$113.$t === undefined ? Main$113["on_event"] : $R.dot(Main$113, "on_event"))}))));