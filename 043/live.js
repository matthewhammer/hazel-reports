// ^report(43)'s worked example, live on the page (its Hazel listings are hazel-listings.js's; Matthew, 2026-11-06: "can we use the npm package itself on this page, and have
// real hazel editors, not just listings of hazel?"). The same pattern as Messed Up Dress Up's scripts (its js/25-scripting.js):
//   - the page keeps the Petri net's marking and draws it (#live-net, drawn first by gen043.py, then kept up to date here);
//   - its two modules of rules are edited in Hazel's own editor: Hazel's app in a frame, one per module, from Hazel's
//     embed-editable build (embed mode, protocol 1, plus {type: "editable"} and {type: "focus", module}), each edit posted back;
//   - each change of text is built by hazeljs from npm (Hazel.runProgram), and while the build is ok, Hazel's on_event answers each
//     event; while it is not (an error, a hole, an unfinished bracket), the page's own JS handler answers, and the log says which.
(() => {
  "use strict";
  const LIB = "https://cdn.jsdelivr.net/npm/hazeljs@0.0.4/hazel-lib.js";
  const root = document.getElementById("live");
  const dataEl = document.getElementById("live-data");
  if (!root || !dataEl) return;
  const D = JSON.parse(dataEl.textContent);   // {preamble, tail, modules: [{name, text}], places, transitions, marking}
  const $ = sel => root.querySelector(sel);
  const el = (tag, attrs = {}, kids = []) => {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) if (k === "text") e.textContent = v; else e.setAttribute(k, v);
    for (const k of [].concat(kids)) e.append(k);
    return e;
  };

  // ---- the state the page keeps (the rules' texts are the listings', hazel-listings.js)
  const L = window.HazelListings;
  const PROGRAM = "petri";
  const S = { marking: D.marking.slice(), built: null, log: [], n: 0 };
  if (L) L.tail(PROGRAM, D.tail);
  const spec = () => L ? L.spec(PROGRAM, D.tail) : { preamble: D.preamble, modules: D.modules, tail: D.tail };

  // ---- the page's own JS handler: what answers while the Hazel rules are not ready (as petri.mjs's jsHandler)
  function jsHandler(net, ev) {
    const enabled = t => t.inputs.every(a => net.marking[a.place] >= a.weight);
    let i = ev.tag === "Fire" ? ev.value : -1;
    if (ev.tag === "Step") {
      const r = net.transitions.map((t, k) => enabled(t) ? k : -1).filter(k => k >= 0);
      if (!r.length) return { tag: "Say", value: ["(js) deadlock: nothing can fire", { tag: "Done" }] };
      i = r[Math.floor(net.draw * r.length)];
    }
    const t = net.transitions[i];
    if (!t || !enabled(t)) return { tag: "Say", value: [`(js) ${t ? t.name : "transition " + i} cannot fire now`, { tag: "Done" }] };
    let k = { tag: "Done" };
    for (const a of [...t.outputs].reverse()) k = { tag: "Put", value: [a.place, a.weight, k] };
    for (const a of [...t.inputs].reverse()) k = { tag: "Take", value: [a.place, a.weight, k] };
    return { tag: "Say", value: ["(js) " + t.name, k] };
  }

  // ---- the page acts out a command: a chain, each command with the rest after it. It keeps control: a Take that would leave a
  // place below zero is refused, and so is a command it does not know
  function perform(cmd) {
    const m = S.marking.slice(), said = [];
    let note = "";
    for (let c = cmd, steps = 0; c && c.tag !== "Done"; steps++) {
      if (steps > 500) { note = "stopped: more than 500 commands"; break; }
      const v = Array.isArray(c.value) ? c.value : [c.value];
      if (c.tag === "Take" && v.length === 3) {
        if (!(v[0] in m)) { note = `refused: there is no place ${v[0]}`; break; }
        if (m[v[0]] - v[1] < 0) { note = `refused: ${D.places[v[0]]} would go below zero`; break; }
        m[v[0]] -= v[1]; c = v[2];
      } else if (c.tag === "Put" && v.length === 3) {
        if (!(v[0] in m)) { note = `refused: there is no place ${v[0]}`; break; }
        m[v[0]] += v[1]; c = v[2];
      } else if (c.tag === "Say" && v.length === 2) { said.push(String(v[0])); c = v[1]; }
      else { note = `refused: a command this page does not know (${c.tag || (c.hazel ? "not a value" : "?")})`; break; }
    }
    if (!note) S.marking = m;
    return { said, note };
  }

  // a value as Hazel writes it: Say("enter1", Take(0, 1, Done))
  const hz = v => v === null || v === undefined ? "()" : typeof v === "string" ? JSON.stringify(v) : typeof v !== "object" ? String(v)
    : Array.isArray(v) ? "[" + v.map(hz).join(", ") + "]" : v.tag ? v.tag + (v.value === undefined ? "" : "(" + (Array.isArray(v.value) ? v.value.map(hz).join(", ") : hz(v.value)) + ")")
    : typeof v.hazel === "string" ? "‹not a value›" : "(" + Object.entries(v).map(([k, x]) => `${k} = ${hz(x)}`).join(", ") + ")";

  // ---- events, each kept for the 🪵 event log (as Messed Up Dress Up's: the engine that answered, the answer, what it did)
  const LOG_KEEP = 50;
  function event(ev, quiet) {
    const before = S.marking.slice();
    const view = { marking: before.slice(), transitions: D.transitions, draw: Math.random() };
    const hazel = !!(S.built && S.built.ok && S.built.handler);
    let cmd, threw = "";
    const t0 = performance.now();
    try { cmd = hazel ? S.built.handler(view, ev) : jsHandler(view, ev); }
    catch (e) { threw = String(e && e.message || e); cmd = jsHandler(view, ev); }
    const ms = performance.now() - t0;
    const r = perform(cmd);
    const entry = { n: ++S.n, at: new Date(), ev, eng: hazel && !threw ? "hazel" : "js", said: r.said, note: threw ? "Hazel threw: " + threw : r.note,
                    cmd, ms, before, after: S.marking.slice() };
    if (!quiet) keep(entry);
    return entry;
  }
  function runMany(n) {
    const before = S.marking.slice(), counts = {}, engs = new Set(), t0 = performance.now();
    let notes = 0;
    for (let i = 0; i < n; i++) {
      const e = event({ tag: "Step" }, true);
      engs.add(e.eng); if (e.note) notes++;
      const k = e.said[0] || e.note || "?"; counts[k] = (counts[k] || 0) + 1;
    }
    keep({ n: ++S.n, at: new Date(), ev: { tag: "Step" }, times: n, eng: engs.size === 1 ? [...engs][0] : "mixed", counts, notes,
           ms: performance.now() - t0, before, after: S.marking.slice() });
  }
  function keep(entry) { S.log.unshift(entry); if (S.log.length > LOG_KEEP) S.log.length = LOG_KEEP; }

  // ---- drawing: the net's tokens and which transitions can fire, the status, the log
  function drawNet() {
    S.marking.forEach((k, i) => {
      const dot = root.querySelector(`#live-tok-${i}`), cnt = root.querySelector(`#live-cnt-${i}`);
      if (dot) dot.style.display = k === 1 ? "" : "none";
      if (cnt) { cnt.style.display = k === 1 || k === 0 ? "none" : ""; cnt.textContent = String(k); }
    });
    D.transitions.forEach((t, i) => {
      const r = root.querySelector(`#live-tr-${i}`);
      if (r) r.classList.toggle("off", !t.inputs.every(a => S.marking[a.place] >= a.weight));
    });
    $("#live-marking").textContent = D.places.map((p, i) => `${p} ${S.marking[i]}`).join(" · ");
  }
  function errorText(message) {
    const m = String(message).match(/^Error in term:\s*\n\s*([\s\S]*?)\nNature of error: Expecting type ([\s\S]*?) but got inconsistent type ([\s\S]*)$/);
    if (!m) return String(message).replace(/\s+/g, " ");
    // (a type with a comma at its top, a pair, in parentheses: "a (Net, Int)", not "a Net, Int")
    const ty = t => { t = t.trim().replace(/\s+/g, " "); return /,/.test(t) && !/^\(.*\)$/.test(t) ? `(${t})` : t; };
    const a = t => (/^[AEIOU]/.test(ty(t)) ? "an " : "a ") + ty(t);
    const term = m[1].trim().replace(/\s+/g, " ");
    return `${term.length > 60 ? term.slice(0, 57) + "…" : term}: ${a(m[2])} is wanted here, but this is ${a(m[3])}`;
  }
  function drawStatus() {
    const st = $("#live-status");
    st.replaceChildren();
    if (!window.Hazel) { st.className = "live-status wait"; st.append(S.libFailed ? "Hazel did not load from jsDelivr; the page's own JS answers events." : "⏳ Loading Hazel (hazeljs 0.0.4 from jsDelivr, about 650 kB); until then the page's own JS answers events."); return; }
    const b = S.built;
    if (!b) return;
    if (b.ok) { st.className = "live-status ok"; st.append(`✓ The rules are ready: Hazel answers each event. Built by hazeljs in ${b.ms.toFixed(0)} ms.`); return; }
    st.className = "live-status no";
    st.append(el("b", { text: "Not ready, so the page's own JS answers events." }));
    const ul = el("ul");
    for (const e of b.errors) ul.append(el("li", { text: `${e.module || "the program"}: ${errorText(e.message)}` }));
    for (const m of Object.keys(b.holes || {})) if (b.holes[m]) ul.append(el("li", { text: `${m}: ${b.holes[m]} hole${b.holes[m] > 1 ? "s" : ""} to fill` }));
    for (const m of Object.keys(b.incomplete || {})) if (b.incomplete[m]) ul.append(el("li", { text: `${m}: ${b.incomplete[m]} bracket or keyword without its partner` }));
    if (b.threw) ul.append(el("li", { text: "hazeljs: " + b.threw }));
    st.append(ul);
  }
  // the 🪵 event log, drawn as Messed Up Dress Up's: one line an event (its number, time, engine, call, time taken, and what changed),
  // opened for the event and the answer, the answer acted out, the time, and the marking before and after in full
  const opened = new Set();
  const span = (cls, kids) => el("span", { class: cls }, [].concat(kids));
  const clock = d => d.toTimeString().slice(0, 8) + "." + String(d.getMilliseconds()).padStart(3, "0");
  const fmtMs = ms => ms < 1 ? ms.toFixed(2) + " ms" : ms < 100 ? ms.toFixed(1) + " ms" : Math.round(ms) + " ms";
  const evText = e => e.times ? `Step ×${e.times}` : e.ev.tag + (e.ev.value === undefined ? "" : `(${hz(e.ev.value)})`);
  // a place that changed, as a chip: its name (a field chip, as the game's globals' fields) and its tokens before and after
  function changes(e) {
    const ch = D.places.map((p, i) => [p, e.before[i], e.after[i]]).filter(([, b, a]) => b !== a);
    if (!ch.length) return [span("log-chip log-quiet", "no change")];
    return ch.map(([p, b, a]) => span("log-chip", [span("log-field", p), span("log-eq", "="), `${b} ⟶ ${a}`]));
  }
  // the answer's commands, each as a chip, the places by name
  function commands(cmd) {
    const out = [];
    for (let c = cmd, k = 0; c && c.tag !== "Done" && k < 60; k++) {
      const v = Array.isArray(c.value) ? c.value : [c.value];
      if ((c.tag === "Take" || c.tag === "Put") && v.length === 3) { out.push(span("log-chip", [span("log-field", D.places[v[0]] ?? String(v[0])), ` ${c.tag === "Take" ? "−" : "+"}${v[1]}`])); c = v[2]; }
      else if (c.tag === "Say" && v.length === 2) { out.push(span("log-chip", `Say(${JSON.stringify(String(v[0]))})`)); c = v[1]; }
      else { out.push(span("log-chip log-bad", hz(c))); break; }
    }
    return out.length ? out : [span("log-chip log-quiet", "Done")];
  }
  const row = (k, v) => [span("log-k", k), el("div", { class: "log-v" }, [].concat(v))];
  function body(e) {
    const grid = el("div", { class: "log-grid" });
    if (e.times) {
      grid.append(...row("fired", el("div", { class: "log-chips" }, Object.entries(e.counts).map(([k, v]) => span("log-chip", `${k} ×${v}`)))));
      if (e.notes) grid.append(...row("", el("div", { class: "log-bad" }, `${e.notes} of the ${e.times} answers refused by the page`)));
    } else {
      grid.append(...row("event", el("code", { class: "log-json", text: hz(e.ev) })));
      grid.append(...row("answer", el("code", { class: "log-json", text: hz(e.cmd) })));
      const fx = el("div", { class: "log-effect" }, [
        ...row("the answer, acted out", el("div", { class: "log-chips" }, commands(e.cmd))),
        ...row("the marking", el("div", { class: "log-chips" }, changes(e))),
        ...(e.note ? row("", el("div", { class: "log-bad", text: "⚠️ " + e.note })) : [])]);
      grid.append(fx);
    }
    grid.append(...row("time", span("log-diff", e.times ? `${fmtMs(e.ms)} for ${e.times} steps, ${fmtMs(e.ms / e.times)} each` : `rule ${fmtMs(e.ms)}`)));
    const side = (title, m) => el("div", {}, [el("div", { class: "log-k", style: "text-align:left", text: title }),
      el("pre", { class: "log-json", text: D.places.map((p, i) => `${p.padEnd(6)} ${m[i]}`).join("\n") })]);
    const whole = el("details", { class: "log-globals" }, [el("summary", { text: "the marking before and after, in full" }),
      el("div", { class: "log-sides" }, [side("before", e.before), side("after", e.after)])]);
    return [grid, whole];
  }
  // (as the game's log: the handler's name goes to its definition, in its listing)
  function goLink(name) {
    const b = el("button", { type: "button", class: "log-goto", title: `go to ${name}'s definition`, text: name });
    b.addEventListener("click", ev => { ev.preventDefault(); ev.stopPropagation(); if (L) L.goto(PROGRAM, name); });
    return b;
  }
  function drawLog() {
    const list = $("#live-log .log-list"), count = $("#live-log .log-count");
    count.textContent = S.log.length ? `${S.n} event${S.n === 1 ? "" : "s"}${S.n > LOG_KEEP ? ` (the most recent ${LOG_KEEP})` : ""}` : "";
    if (!S.log.length) { list.replaceChildren(el("div", { class: "hint", text: "no events yet: click a transition, or Step; every event the page hands to a rule is kept here, whichever answers it (Hazel or the page's JS)" })); return; }
    list.replaceChildren(...S.log.map(e => {
      const eng = e.eng === "hazel" ? "Hazel" : e.eng === "js" ? "JS" : "both";
      const head = el("summary", {}, [span("log-n", "#" + e.n), " ", span("log-at", clock(e.at)), " ",
        span(`log-eng log-${e.eng}`, eng), " ",
        e.times ? el("code", { text: evText(e) }) : el("code", {}, [goLink("Rules.on_event"), `(${evText(e)})`]), " ", span("log-ms", fmtMs(e.ms)), " ",
        ...(e.note ? [span("log-chip log-bad", "refused")]
          : e.times ? Object.entries(e.counts).map(([k, v]) => span("log-chip", `${k} ×${v}`))
          : e.before.some((b, i) => b !== e.after[i]) ? changes(e) : [span("log-chip log-quiet", e.said[0] || "no change")])]);
      const det = el("details", { class: "log-entry" }, [head]);
      det.addEventListener("toggle", () => { if (det.open) { opened.add(e.n); if (det.children.length === 1) det.append(...body(e)); } else opened.delete(e.n); });
      if (opened.has(e.n)) { det.append(...body(e)); det.open = true; }   // (an entry opened stays open as new ones come in)
      return det;
    }));
  }
  const drawAll = () => { drawNet(); drawStatus(); drawLog(); };

  // ---- building: once per change of text, a moment after typing stops
  let buildTimer = 0;
  function buildSoon(delay = 350) { clearTimeout(buildTimer); buildTimer = setTimeout(build, delay); }
  function build() {
    if (!window.Hazel) return;
    const sp = spec(), key = JSON.stringify(sp);
    if (S.built && S.built.key === key) return;
    let r, threw = "";
    const t0 = performance.now();
    try { r = window.Hazel.runProgram(sp); } catch (e) { threw = String(e && e.message || e); r = { ok: false, errors: [] }; }
    S.built = { key, ok: !!r.ok, errors: r.errors || [], holes: r.holes, incomplete: r.incomplete, ms: performance.now() - t0, threw,
                handler: r.ok && typeof r.value === "function" ? r.value : null };
    if (S.built.ok && !S.built.handler) S.built.ok = false;
    drawStatus();
  }
  function loadLib() {
    if (window.Hazel || S.libLoading) return;
    S.libLoading = true;
    const s = el("script", { src: LIB, async: "" });
    s.onload = () => { drawStatus(); build(); };
    s.onerror = () => { S.libFailed = true; drawStatus(); };
    document.head.append(s);
  }

  // ---- the page's parts, wired
  function wire() {
    if (L) L.onChange(PROGRAM, () => buildSoon());
    D.transitions.forEach((t, i) => {
      const r = root.querySelector(`#live-tr-${i}`);
      if (!r) return;
      r.setAttribute("tabindex", "0"); r.setAttribute("role", "button"); r.setAttribute("aria-label", `Fire ${t.name}`);
      const go = () => { event({ tag: "Fire", value: i }); drawAll(); };
      r.addEventListener("click", go);
      r.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
    });
    $("#live-step").addEventListener("click", () => { event({ tag: "Step" }); drawAll(); });
    $("#live-run").addEventListener("click", () => { runMany(100); drawAll(); });
    $("#live-reset").addEventListener("click", () => { S.marking = D.marking.slice(); drawAll(); });
    $("#live-log-clear").addEventListener("click", () => { S.log = []; opened.clear(); drawLog(); });
    $("#live-rules").addEventListener("click", () => { if (L) L.reset(PROGRAM); buildSoon(0); });
    root.classList.add("on");
    drawAll();
    // Hazel's library only once the section is near the screen, about 650 kB (the editors start on their own: hazel-listings.js)
    // (looked for on load, on scroll and every second, not by an IntersectionObserver: in a page in the background those never
    // called back, and Messed Up Dress Up's panel found the same)
    let started = false;
    const near = () => { const r = root.getBoundingClientRect(); return r.top < innerHeight + 600 && r.bottom > -600; };
    const check = () => { if (!started && near()) { started = true; removeEventListener("scroll", check); clearInterval(poll); loadLib(); } };
    addEventListener("scroll", check, { passive: true });
    const poll = setInterval(check, 1000);
    check();
  }
  wire();
})();
