// ^report(43)'s worked example, live on the page (Matthew, 2026-11-06: "can we use the npm package itself on this page, and have
// real hazel editors, not just listings of hazel?"). The same pattern as Messed Up Dress Up's scripts (its js/25-scripting.js):
//   - the page keeps the Petri net's marking and draws it (#live-net, drawn first by gen043.py, then kept up to date here);
//   - its two modules of rules are edited in Hazel's own editor: Hazel's app in a frame, one per module, from Hazel's
//     embed-editable build (embed mode, protocol 1, plus {type: "editable"} and {type: "focus", module}), each edit posted back;
//   - each change of text is built by hazeljs from npm (Hazel.runProgram), and while the build is ok, Hazel's on_event answers each
//     event; while it is not (an error, a hole, an unfinished bracket), the page's own JS handler answers, and the log says which.
(() => {
  "use strict";
  const LIB = "https://cdn.jsdelivr.net/npm/hazeljs@0.0.4/hazel-lib.js";
  const FRAME = "https://build.hazel.org/embed-editable/index.html#embed";
  const ORIGIN = "https://build.hazel.org";
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

  // ---- the state the page keeps
  const S = {
    texts: Object.fromEntries(D.modules.map(m => [m.name, m.text])),
    undo: Object.fromEntries(D.modules.map(m => [m.name, []])),
    redo: Object.fromEntries(D.modules.map(m => [m.name, []])),
    marking: D.marking.slice(),
    built: null,        // {key, ok, errors, holes, incomplete, ms, handler}
    log: [],
    n: 0,
  };
  const spec = () => ({ preamble: D.preamble, modules: D.modules.map(m => ({ name: m.name, text: S.texts[m.name] })), tail: D.tail });

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

  // ---- events
  function event(ev, quiet) {
    const view = { marking: S.marking.slice(), transitions: D.transitions, draw: Math.random() };
    const hazel = !!(S.built && S.built.ok && S.built.handler);
    let cmd, threw = "";
    const t0 = performance.now();
    try { cmd = hazel ? S.built.handler(view, ev) : jsHandler(view, ev); }
    catch (e) { threw = String(e && e.message || e); cmd = jsHandler(view, ev); }
    const ms = performance.now() - t0;
    const r = perform(cmd);
    const entry = { n: ++S.n, ev, by: hazel && !threw ? "Hazel" : "the page's JS", said: r.said.join("; "), note: threw ? "Hazel threw: " + threw : r.note, cmd, ms };
    if (!quiet) { S.log.unshift(entry); S.log.length = Math.min(S.log.length, 12); }
    return entry;
  }
  function runMany(n) {
    const counts = {}, t0 = performance.now();
    let by = new Set(), last = null;
    for (let i = 0; i < n; i++) { last = event({ tag: "Step" }, true); by.add(last.by); counts[last.said || last.note || "?"] = (counts[last.said || last.note || "?"] || 0) + 1; }
    const ms = performance.now() - t0;
    S.log.unshift({ n: ++S.n, ev: { tag: "Step", value: undefined, times: n }, by: [...by].join(", "),
      said: Object.entries(counts).map(([k, v]) => `${k} ×${v}`).join(", "), note: "", cmd: null, ms });
    S.log.length = Math.min(S.log.length, 12);
  }

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
  function drawLog() {
    const tb = $("#live-log tbody");
    tb.replaceChildren();
    for (const e of S.log) {
      const ev = e.ev.times ? `Step ×${e.ev.times}` : e.ev.tag + (e.ev.value === undefined ? "" : `(${e.ev.value})`);
      const tr = el("tr", {}, [el("td", { class: "n", text: String(e.n) }), el("td", {}, [el("code", { text: ev })]), el("td", { text: e.by }),
        el("td", {}, [e.said || "", e.note ? el("span", { class: "warn", text: (e.said ? " · " : "") + e.note }) : ""]),
        el("td", {}, e.cmd ? [el("code", { class: "cmd", text: hz(e.cmd) })] : []), el("td", { class: "n", text: e.ms < 1 ? e.ms.toFixed(2) : e.ms.toFixed(1) })]);
      tb.append(tr);
    }
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

  // ---- the editors: Hazel's tiles in a frame per module, with a text box behind each (shown when asked, or when the frame fails)
  const pageDark = () => { const t = document.documentElement.getAttribute("data-theme"); return t === "dark" || (t !== "light" && !!(window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches)); };
  const editors = D.modules.map(m => ({ mod: m.name, frame: null, ready: false, sent: null, mode: "tiles", timer: 0 }));
  const post = (E, msg) => E.frame && E.frame.contentWindow && E.frame.contentWindow.postMessage(msg, ORIGIN);
  function sendProgram(E, force) {
    if (!E.ready || E.mode !== "tiles") return;
    const key = JSON.stringify(spec());
    if (key === E.sent && !force) return;
    E.sent = key;
    post(E, { type: "set", ...spec() });
  }
  function changed(mod, text, from) {
    if (S.texts[mod] === text) return;
    S.undo[mod].push(S.texts[mod]); S.redo[mod] = [];
    if (S.undo[mod].length > 200) S.undo[mod].shift();
    S.texts[mod] = text;
    afterChange(mod, from);
  }
  function afterChange(mod, from) {
    const E = editors.find(x => x.mod === mod);
    const box = root.querySelector(`#live-text-${mod}`);
    if (box && from !== box) box.value = S.texts[mod];
    for (const X of editors) {
      if (X === E && from === "frame") X.sent = JSON.stringify(spec());   // (this frame has it already: not posted back, its caret stays)
      else sendProgram(X);
    }
    buildSoon();
  }
  function history(mod, redo) {
    const from = redo ? S.redo[mod] : S.undo[mod], to = redo ? S.undo[mod] : S.redo[mod];
    if (!from.length) return;
    to.push(S.texts[mod]); S.texts[mod] = from.pop();
    const E = editors.find(x => x.mod === mod);
    if (E) E.sent = null;
    afterChange(mod, null);
  }
  function setMode(E, mode, why) {
    E.mode = mode;
    const wrap = root.querySelector(`#live-ed-${E.mod}`);
    wrap.dataset.mode = mode;
    wrap.querySelector(".live-why").textContent = why || "";
    wrap.querySelector(".live-toggle").textContent = mode === "tiles" ? "edit as text" : "edit in Hazel's tiles";
    if (mode === "tiles") { if (!E.frame) mount(E); else { E.sent = null; sendProgram(E); } }
  }
  function mount(E) {
    if (E.frame) return;
    const holder = root.querySelector(`#live-ed-${E.mod} .live-frame`);
    E.frame = el("iframe", { src: FRAME, title: `Hazel's editor: the module ${E.mod}`, loading: "eager" });
    holder.replaceChildren(E.frame);
    // a frame that never says ready (blocked, offline, too slow) gives way to the text box
    E.timer = setTimeout(() => { if (!E.ready) setMode(E, "text", "Hazel's editor did not start, so here is the text."); }, 45000);
  }
  function onMessage(e) {
    if (e.origin !== ORIGIN) return;
    const E = editors.find(x => x.frame && x.frame.contentWindow === e.source);
    if (!E) return;
    const m = e.data || {};
    if (m.type === "ready") {
      E.ready = true; E.sent = null; clearTimeout(E.timer);
      root.querySelector(`#live-ed-${E.mod}`).dataset.ready = "1";
      const dark = pageDark();
      post(E, { type: "theme", dark, contrast: dark });
      post(E, { type: "editable", on: true });
      post(E, { type: "font", size: 13 });   // (the page's own code size, so a module fits its column)
      post(E, { type: "focus", module: E.mod });
      sendProgram(E, true);
      // the next frame once this one is up, so two copies of Hazel do not start at once
      const next = editors.find(x => !x.frame && x.mode === "tiles");
      if (next) mount(next);
    } else if (m.type === "size") {
      E.frame.style.height = Math.max(40, Math.ceil(+m.height || 0)) + "px";   // (no cap: the frame does not scroll itself, so a cap would hide the end of a module)
    } else if (m.type === "edit") {
      changed(E.mod, String(m.text || ""), "frame");
    } else if (m.type === "history") {
      history(E.mod, !!m.redo);
    } else if (m.type === "crash" && !E.ready) {
      setMode(E, "text", "Hazel's editor stopped (" + String(m.message || "").slice(0, 80) + "), so here is the text.");
    }
  }

  // ---- the page's parts, wired
  function wire() {
    window.addEventListener("message", onMessage);
    for (const E of editors) {
      const wrap = root.querySelector(`#live-ed-${E.mod}`);
      const box = wrap.querySelector("textarea");
      box.value = S.texts[E.mod];
      box.addEventListener("input", () => changed(E.mod, box.value, box));
      wrap.querySelector(".live-toggle").addEventListener("click", () => setMode(E, E.mode === "tiles" ? "text" : "tiles"));
    }
    const again = () => { for (const E of editors) if (E.ready) { const dark = pageDark(); post(E, { type: "theme", dark, contrast: dark }); } };
    new MutationObserver(again).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    if (window.matchMedia) matchMedia("(prefers-color-scheme: dark)").addEventListener("change", again);
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
    $("#live-rules").addEventListener("click", () => {
      for (const m of D.modules) if (S.texts[m.name] !== m.text) { S.undo[m.name].push(S.texts[m.name]); S.texts[m.name] = m.text; afterChange(m.name, null); }
      for (const E of editors) { E.sent = null; sendProgram(E); }
    });
    root.classList.add("on");
    drawAll();
    // Hazel (the library, then the editors) only once the section is near the screen: about 650 kB, then Hazel's app per frame
    const start = () => { loadLib(); if (!editors.some(x => x.frame)) mount(editors[0]); };
    // (looked for on load, on scroll and every second, not by an IntersectionObserver: in a page in the background those never
    // called back, and Messed Up Dress Up's panel found the same)
    let started = false;
    const near = () => { const r = root.getBoundingClientRect(); return r.top < innerHeight + 600 && r.bottom > -600; };
    const check = () => { if (!started && near()) { started = true; removeEventListener("scroll", check); clearInterval(poll); start(); } };
    addEventListener("scroll", check, { passive: true });
    const poll = setInterval(check, 1000);
    check();
  }
  wire();
})();
