// hazel-listings.js: Hazel listings in an article, in Hazel's own tile editor, with go to definition between them.
// (^report(43), and the how-to, ^report(44); Matthew, 2026-11-06: "hazel listings as plain text", "goto definition does not work
// in the listings", "can we also write about how to do this, generally, so a blog post or 'article' like this could have
// listings where goto def works?")
//
// Write each listing as plain text, so a page without JavaScript still reads:
//   <pre class="hazel" data-program="petri">type Net = ... in</pre>                 the program's preamble (its types)
//   <pre class="hazel" data-program="petri" data-module="Common">let nth = ...</pre> a module's body
// Listings with one data-program are one program, in order: the preamble, then each module, as Hazel.runProgram takes it.
// Each listing becomes a frame of Hazel's app in embed mode (Messed Up Dress Up's), showing that part alone, read in the context
// of the whole program, so its types, errors and holes are the program's. A go to definition (Ctrl+click, or F12) on a name
// defined in another listing goes there: the frame asks the page, the page finds the listing that defines the name and asks
// that frame to reveal it, then scrolls to its caret. An edit in a listing reaches the other listings of its program, and
// HazelListings.onChange(program, fn) tells the page.
//
// Limits, today: the frame comes from a branch build of Hazel (embed-editable) and takes messages only from the sites in its
// allowlist (matthewhammer.org, localhost), so another site needs its origin added there (^ticket(701)); a go to definition
// starts only in an editable cell, so listings are editable (data-editable="false" makes one read-only, a place to reveal
// into, not to start from); undo is the page's (^ticket(702)).
(() => {
  "use strict";
  const FRAME = "https://build.hazel.org/embed-editable/index.html#embed";
  const ORIGIN = "https://build.hazel.org";
  const WAIT_MS = 45000;
  const programs = new Map();      // name -> {name, preamble: listing|null, modules: [listing], tail, listeners: []}
  const listings = [];             // in document order
  const queue = [];                // listings waiting for their frame, made one at a time
  let making = null;

  const pageDark = () => { const t = document.documentElement.getAttribute("data-theme"); return t === "dark" || (t !== "light" && !!(window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches)); };
  const post = (L, msg) => L.frame && L.frame.contentWindow && L.frame.contentWindow.postMessage(msg, ORIGIN);

  // what one listing's frame is sent: a module's listing gets the whole program, focused on its module; the preamble's, the
  // preamble alone (an empty tail shows nothing after its last "in")
  function specOf(P) {
    return { preamble: P.preamble ? P.preamble.text : "", modules: P.modules.map(L => ({ name: L.module, text: L.text })), tail: P.tail || "" };
  }
  function frameSpec(L) {
    const P = programs.get(L.program);
    return L.module ? specOf(P) : { preamble: L.text, modules: [], tail: "" };
  }
  function send(L, force) {
    if (!L.ready) return;
    const sp = frameSpec(L), key = JSON.stringify(sp);
    if (key === L.sent && !force) return;
    L.sent = key;
    post(L, { type: "set", ...sp });
  }
  function sendAll(P, except) { for (const L of [P.preamble, ...P.modules]) if (L && L !== except) send(L); }

  // ---- making frames: in document order, one at a time, the next when the last says ready (or gives up)
  function make(L) {
    if (L.frame || L.failed) return;
    L.frame = document.createElement("iframe");
    L.frame.className = "hazel-listing-frame";
    L.frame.title = L.module ? `Hazel's editor: the module ${L.module}` : "Hazel's editor: the program's types";
    L.frame.src = FRAME;
    // (in the text's place, visible, as tall as the text, while Hazel starts: a frame kept invisible meanwhile is not drawn by the
    // browser, so Hazel never measures its code and says its height is 0)
    L.frame.style.cssText = "width:100%;height:" + Math.max(40, L.pre.offsetHeight) + "px;display:block";
    L.holder.dataset.state = "loading";
    L.holder.append(L.frame);
    making = L;
    L.timer = setTimeout(() => { if (!L.ready) fail(L, "Hazel's editor did not start"); }, WAIT_MS);
  }
  function pump() {
    if (making && !making.ready && !making.failed) return;
    making = null;
    const next = queue.shift();
    if (next) make(next);
  }
  function fail(L, why) {
    L.failed = true;
    if (L.frame) L.frame.remove();
    L.frame = null;
    L.holder.dataset.state = "text";
    L.pre.title = why + "; here is the text";
    if (making === L) pump();
  }

  // ---- go to definition: a name the frame could not find in its own cell
  function definer(P, name) {
    const parts = String(name).split(".");
    if (parts.length > 1) {
      const M = P.modules.find(L => L.module === parts[0]);
      return M ? [M, parts[parts.length - 1]] : null;
    }
    const word = s => new RegExp("(^|\\n)\\s*(let|type)\\s+" + name.replace(/[^\w]/g, "") + "\\b").test(s);
    if (P.preamble) {
      if (word(P.preamble.text)) return [P.preamble, name];
      // a constructor: its type's definition
      const owner = P.preamble.text.split("\n").find(l => /^\s*type\s+\w+\s*=/.test(l) && new RegExp("\\+\\s*" + name + "\\b").test(l));
      if (owner) return [P.preamble, owner.match(/type\s+(\w+)/)[1]];
    }
    const M = P.modules.find(L => word(L.text));
    return M ? [M, name] : null;
  }
  function reveal(L, name) {
    if (!L.ready) { L.reveal = name; if (!L.frame) { const i = queue.indexOf(L); if (i >= 0) queue.splice(i, 1); queue.unshift(L); pump(); } return; }
    L.holder.scrollIntoView({ block: "nearest" });
    post(L, { type: "reveal", name });
  }

  // ---- what the frames say
  function onMessage(e) {
    if (e.origin !== ORIGIN) return;
    const L = listings.find(x => x.frame && x.frame.contentWindow === e.source);
    if (!L) return;
    const m = e.data || {}, P = programs.get(L.program);
    if (m.type === "ready") {
      L.ready = true; L.sent = null; clearTimeout(L.timer);
      L.holder.dataset.state = "tiles";
      const dark = pageDark();
      post(L, { type: "theme", dark, contrast: dark });
      if (L.editable) post(L, { type: "editable", on: true });
      post(L, { type: "font", size: L.fontSize });
      if (L.module) post(L, { type: "focus", module: L.module });
      send(L, true);
      if (L.reveal) { const n = L.reveal; L.reveal = null; setTimeout(() => post(L, { type: "reveal", name: n }), 300); }
      pump();
    } else if (m.type === "size") {
      // (0 from a frame not drawn yet, off the screen, where browsers do not draw another site's frame: its height kept until it is)
      if (+m.height > 0) L.frame.style.height = Math.ceil(+m.height) + "px";
    } else if (m.type === "caret") {
      // after a reveal or a goto, where the caret is in the frame: scrolled to, as the frame is as tall as its code
      const top = L.frame.getBoundingClientRect().top + (+m.top || 0);
      if (top < 60 || top > innerHeight - 60) window.scrollBy({ top: top - innerHeight / 3, behavior: "smooth" });
    } else if (m.type === "goto") {
      const d = definer(P, String(m.name || ""));
      if (d) reveal(d[0], d[1]);
    } else if (m.type === "edit") {
      const text = L.module ? String(m.text || "") : String(m.text || "").replace(/\s+$/, "");
      if (text === L.text) return;
      L.undo.push(L.text); L.redo = [];
      L.text = text;
      L.sent = JSON.stringify(frameSpec(L));   // (this frame has it: not posted back, its caret stays)
      sendAll(P, L);
      changed(P);
    } else if (m.type === "history") {
      const from = m.redo ? L.redo : L.undo, to = m.redo ? L.undo : L.redo;
      if (!from.length) return;
      to.push(L.text); L.text = from.pop();
      L.sent = null; send(L); sendAll(P, L);
      changed(P);
    } else if (m.type === "crash" && !L.ready) {
      fail(L, "Hazel's editor stopped");
    }
  }
  function changed(P) { for (const fn of P.listeners) try { fn(specOf(P)); } catch (e) { console.error(e); } }

  // ---- the page's listings, found and started once the first is near the screen
  function init() {
    for (const pre of document.querySelectorAll("pre.hazel")) {
      const program = pre.dataset.program || "page";
      if (!programs.has(program)) programs.set(program, { name: program, preamble: null, modules: [], tail: "", listeners: [] });
      const P = programs.get(program);
      const holder = document.createElement("div");
      holder.className = "hazel-listing";
      holder.dataset.state = "waiting";
      pre.replaceWith(holder);
      holder.append(pre);
      const L = { pre, holder, program, module: pre.dataset.module || null, text: pre.textContent.replace(/\s+$/, ""),
                  editable: pre.dataset.editable !== "false", fontSize: Math.round(parseFloat(getComputedStyle(pre).fontSize) || 13),
                  frame: null, ready: false, sent: null, undo: [], redo: [], original: null };
      L.original = L.text;
      if (L.module) P.modules.push(L); else P.preamble = L;
      listings.push(L);
      queue.push(L);
    }
    if (!listings.length) return;
    window.addEventListener("message", onMessage);
    const again = () => { const dark = pageDark(); for (const L of listings) if (L.ready) post(L, { type: "theme", dark, contrast: dark }); };
    new MutationObserver(again).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    if (window.matchMedia) matchMedia("(prefers-color-scheme: dark)").addEventListener("change", again);
    // (polled, not an IntersectionObserver: in a page in the background those never called back)
    let started = false;
    const near = () => listings.some(L => { const r = L.holder.getBoundingClientRect(); return r.top < innerHeight + 800 && r.bottom > -800; });
    const check = () => { if (!started && near()) { started = true; clearInterval(poll); removeEventListener("scroll", check); pump(); } };
    const poll = setInterval(check, 1000);
    addEventListener("scroll", check, { passive: true });
    check();
  }

  window.HazelListings = {
    // fn(spec) after each change to the program's text, spec as Hazel.runProgram takes it (the page adds its tail)
    onChange(program, fn) { const P = programs.get(program); if (P) P.listeners.push(fn); },
    spec(program, tail) { const P = programs.get(program); return P ? { ...specOf(P), tail: tail || "" } : null; },
    tail(program, tail) { const P = programs.get(program); if (P) { P.tail = tail; sendAll(P); } },
    // go to name's definition, as a go to definition in a listing does (a dotted Module.name, a type or constructor of the
    // preamble, or a module's let): true when a listing defines it
    goto(program, name) { const P = programs.get(program), d = P && definer(P, String(name)); if (d) reveal(d[0], d[1]); return !!d; },
    // every listing of the program back to the text the page was written with
    reset(program) {
      const P = programs.get(program); if (!P) return;
      for (const L of [P.preamble, ...P.modules]) if (L && L.text !== L.original) { L.undo.push(L.text); L.text = L.original; L.sent = null; }
      sendAll(P); changed(P);
    },
  };
  // (run where it is loaded: at the end of the body, every listing is already in the page)
  init();
})();
