function program($R) {
  "use strict";
  let let$1, Common$73, let$74, Rules$95, let$96, Main$113;
  return let$1 = (() => {
    let def$2, nth$10, def$11, len$17, def$18, pick$26, def$27, has$35, def$36, enabled$40, def$41, ready$50, def$51, takes$59, def$60, puts$68, def$69, fire$72;
    return def$2 = (() => {
      let nth$3;
      return nth$3 = $R.fn((a$4) => {
        let xs$5, i$6, m$7, x$8, rest$9;
        return xs$5 = a$4[0], i$6 = a$4[1], m$7 = xs$5, m$7 === null ? 0 : m$7 !== null ? (x$8 = m$7.h, rest$9 = m$7.t, $R.eq(i$6, 0) ? x$8 : nth$3([rest$9, i$6 - 1])) : $R.nomatch("case");
      }, 0, [nth$3]), nth$3;
    })(), nth$10 = def$2, def$11 = (() => {
      let len$12;
      return len$12 = $R.fn((a$13) => {
        let xs$14, m$15, rest$16;
        return xs$14 = a$13, m$15 = xs$14, m$15 === null ? 0 : m$15 !== null ? (rest$16 = m$15.t, 1 + len$12(rest$16)) : $R.nomatch("case");
      }, 1, [len$12]), len$12;
    })(), len$17 = def$11, def$18 = (() => {
      let pick$19;
      return pick$19 = $R.fn((a$20) => {
        let ts$21, i$22, m$23, t$24, rest$25;
        return ts$21 = a$20[0], i$22 = a$20[1], m$23 = ts$21, m$23 === null ? { c: "None" } : m$23 !== null ? (t$24 = m$23.h, rest$25 = m$23.t, $R.eq(i$22, 0) ? { c: "Some", v: t$24 } : pick$19([rest$25, i$22 - 1])) : $R.nomatch("case");
      }, 2, [pick$19]), pick$19;
    })(), pick$26 = def$18, def$27 = (() => {
      let has$28;
      return has$28 = $R.fn((a$29) => {
        let m$30, arcs$31, m$32, a$33, rest$34;
        return m$30 = a$29[0], arcs$31 = a$29[1], m$32 = arcs$31, m$32 === null ? true : m$32 !== null ? (a$33 = m$32.h, rest$34 = m$32.t, nth$10([m$30, a$33["place"]]) >= a$33["weight"] && has$28([m$30, rest$34])) : $R.nomatch("case");
      }, 3, [has$28, nth$10]), has$28;
    })(), has$35 = def$27, def$36 = $R.fn((a$37) => {
      let m$38, t$39;
      return m$38 = a$37[0], t$39 = a$37[1], has$35([m$38, t$39["inputs"]]);
    }, 4, [has$35]), enabled$40 = def$36, def$41 = (() => {
      let ready$42;
      return ready$42 = $R.fn((a$43) => {
        let m$44, ts$45, i$46, m$47, t$48, rest$49;
        return m$44 = a$43[0], ts$45 = a$43[1], i$46 = a$43[2], m$47 = ts$45, m$47 === null ? null : m$47 !== null ? (t$48 = m$47.h, rest$49 = m$47.t, enabled$40([m$44, t$48]) ? { h: i$46, t: ready$42([m$44, rest$49, i$46 + 1]) } : ready$42([m$44, rest$49, i$46 + 1])) : $R.nomatch("case");
      }, 5, [ready$42, enabled$40]), ready$42;
    })(), ready$50 = def$41, def$51 = (() => {
      let takes$52;
      return takes$52 = $R.fn((a$53) => {
        let arcs$54, k$55, m$56, a$57, rest$58;
        return arcs$54 = a$53[0], k$55 = a$53[1], m$56 = arcs$54, m$56 === null ? k$55 : m$56 !== null ? (a$57 = m$56.h, rest$58 = m$56.t, { c: "Take", v: [a$57["place"], a$57["weight"], takes$52([rest$58, k$55])] }) : $R.nomatch("case");
      }, 6, [takes$52]), takes$52;
    })(), takes$59 = def$51, def$60 = (() => {
      let puts$61;
      return puts$61 = $R.fn((a$62) => {
        let arcs$63, k$64, m$65, a$66, rest$67;
        return arcs$63 = a$62[0], k$64 = a$62[1], m$65 = arcs$63, m$65 === null ? k$64 : m$65 !== null ? (a$66 = m$65.h, rest$67 = m$65.t, { c: "Put", v: [a$66["place"], a$66["weight"], puts$61([rest$67, k$64])] }) : $R.nomatch("case");
      }, 7, [puts$61]), puts$61;
    })(), puts$68 = def$60, def$69 = $R.fn((a$70) => {
      let t$71;
      return t$71 = a$70, { c: "Say", v: [t$71["name"], takes$59([t$71["inputs"], puts$68([t$71["outputs"], { c: "Done" }])])] };
    }, 8, [puts$68, takes$59]), fire$72 = def$69, $R.tup([nth$10, len$17, pick$26, has$35, enabled$40, ready$50, takes$59, puts$68, fire$72], ["nth", "len", "pick", "has", "enabled", "ready", "takes", "puts", "fire"]);
  })(), Common$73 = let$1, let$74 = (() => {
    let def$75, fire_at$81, def$82, on_event$94;
    return def$75 = $R.fn((a$76) => {
      let n$77, i$78, m$79, t$80;
      return n$77 = a$76[0], i$78 = a$76[1], m$79 = Common$73["pick"]([n$77["transitions"], i$78]), m$79.c === "None" ? { c: "Say", v: ["there is no transition " + $R.b.string_of_int(i$78), { c: "Done" }] } : m$79.c === "Some" ? (t$80 = m$79.v, Common$73["enabled"]([n$77["marking"], t$80]) ? Common$73["fire"](t$80) : { c: "Say", v: [t$80["name"] + " cannot fire now", { c: "Done" }] }) : $R.nomatch("case");
    }, 9, [Common$73]), fire_at$81 = def$75, def$82 = $R.fn((a$83) => {
      let n$84, e$85, m$86, let$87, r$88, let$89, k$90, let$91, j$92, i$93;
      return n$84 = a$83[0], e$85 = a$83[1], m$86 = e$85, m$86.c === "Fire" ? (i$93 = m$86.v, fire_at$81([n$84, i$93])) : m$86.c === "Step" ? (let$87 = Common$73["ready"]([n$84["marking"], n$84["transitions"], 0]), r$88 = let$87, let$89 = Common$73["len"](r$88), k$90 = let$89, $R.eq(k$90, 0) ? { c: "Say", v: ["deadlock: nothing can fire", { c: "Done" }] } : (let$91 = $R.b.int_of_float(n$84["draw"] * $R.b.float_of_int(k$90)), j$92 = let$91, fire_at$81([n$84, Common$73["nth"]([r$88, j$92])]))) : $R.nomatch("case");
    }, 10, [Common$73, fire_at$81]), on_event$94 = def$82, $R.tup([fire_at$81, on_event$94], ["fire_at", "on_event"]);
  })(), Rules$95 = let$74, let$96 = (() => {
    let def$97, places$98, def$99, arc$102, def$103, transitions$104, def$105, marking$106, def$107, place_at$108, def$109, transition_at$110, def$111, on_event$112;
    return def$97 = { h: "idle1", t: { h: "busy1", t: { h: "idle2", t: { h: "busy2", t: { h: "lock", t: null } } } } }, places$98 = def$97, def$99 = $R.fn((a$100) => {
      let p$101;
      return p$101 = a$100, $R.tup([p$101, 1], ["place", "weight"]);
    }, 11, null), arc$102 = def$99, def$103 = { h: $R.tup(["enter1", { h: arc$102(0), t: { h: arc$102(4), t: null } }, { h: arc$102(1), t: null }], ["name", "inputs", "outputs"]), t: { h: $R.tup(["leave1", { h: arc$102(1), t: null }, { h: arc$102(0), t: { h: arc$102(4), t: null } }], ["name", "inputs", "outputs"]), t: { h: $R.tup(["enter2", { h: arc$102(2), t: { h: arc$102(4), t: null } }, { h: arc$102(3), t: null }], ["name", "inputs", "outputs"]), t: { h: $R.tup(["leave2", { h: arc$102(3), t: null }, { h: arc$102(2), t: { h: arc$102(4), t: null } }], ["name", "inputs", "outputs"]), t: null } } } }, transitions$104 = def$103, def$105 = { h: 1, t: { h: 0, t: { h: 1, t: { h: 0, t: { h: 1, t: null } } } } }, marking$106 = def$105, def$107 = { h: $R.tup([150, 50], ["x", "y"]), t: { h: $R.tup([150, 250], ["x", "y"]), t: { h: $R.tup([550, 50], ["x", "y"]), t: { h: $R.tup([550, 250], ["x", "y"]), t: { h: $R.tup([350, 150], ["x", "y"]), t: null } } } } }, place_at$108 = def$107, def$109 = { h: $R.tup([238, 150], ["x", "y"]), t: { h: $R.tup([62, 150], ["x", "y"]), t: { h: $R.tup([462, 150], ["x", "y"]), t: { h: $R.tup([638, 150], ["x", "y"]), t: null } } } }, transition_at$110 = def$109, def$111 = Rules$95["on_event"], on_event$112 = def$111, $R.tup([places$98, arc$102, transitions$104, marking$106, place_at$108, transition_at$110, on_event$112], ["places", "arc", "transitions", "marking", "place_at", "transition_at", "on_event"]);
  })(), Main$113 = let$96, [Main$113["on_event"], $R.tup([Main$113["marking"], Main$113["transitions"], 0.7], ["marking", "transitions", "draw"])];
}
