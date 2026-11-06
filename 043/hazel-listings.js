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
// Limits, today: the frame comes from a branch build of Hazel (embed-editable) and takes messages only from its own origin and
// the sites in its list (matthewhammer.org, localhost), so another site hosts its own copy (data-frame, above) or asks to be
// added to the list; a go to definition
// starts only in an editable cell, so listings are editable (data-editable="false" makes one read-only, a place to reveal
// into, not to start from); undo is the page's (^ticket(702)).
(() => {
  "use strict";
  // Where Hazel's editor comes from: build.hazel.org's embed-editable build by default, or the page's own copy, named on
  // the script tag (<script src="hazel-listings.js" data-frame="/hazel/index.html#embed">). The frame takes messages from its
  // own origin, so a page served beside its own copy of the editor needs no site list (^report(44), "Your own site").
  const ME = document.currentScript;
  const FRAME = new URL((ME && ME.dataset.frame) || "https://build.hazel.org/embed-editable/index.html#embed", location.href).href;
  const ORIGIN = new URL(FRAME).origin;
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
    // a module's own name: its listing
    const mod = P.modules.find(L => L.module === name);
    if (mod) return [mod, null];
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
    if (name === null) { L.holder.scrollIntoView({ block: "start", behavior: "smooth" }); return; }   // (a module itself: its listing)
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
      // (Matthew, 2026-11-06: "introduced error, fixed it, and the other panels did not refresh") A preamble's frame holds
      // the preamble alone, ending in `in` with nothing after it: an empty hole, which the frame writes as `?`. Taken as it
      // was, any edit to the preamble left `in?` before the modules, the whole program broken, and every listing showing it
      // however the edit was undone. The preamble is its text without that hole.
      const text = L.module ? String(m.text || "") : String(m.text || "").replace(/\s+$/, "").replace(/\bin\s*\?$/, "in");
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
    } else if (m.type === "status") {
      // what Hazel says of the program, under each listing: its errors, holes and unfinished brackets. The newest report
      // of the whole program, from whichever frame sent it: a frame that was just edited reports again only when the page
      // sends it the program, which it does not do for its own edit, so the others' reports are the fresh ones (Matthew,
      // 2026-11-06: an error typed into Scene was reported by Geometry's frame and shown nowhere). A preamble's frame holds
      // the preamble alone, so its report is used only when the program has no modules.
      if (L.module || !P.modules.length) {
        P.status = m;
        for (const X of [P.preamble, ...P.modules]) if (X) showStatus(X);
      }
    } else if (m.type === "crash" && !L.ready) {
      fail(L, "Hazel's editor stopped");
    }
  }
  // (Matthew, 2026-11-06, of an error he typed into a listing: "can't see the error") Hazel's editor marks where an error
  // is, but its message is in the app's own bar, which the frame does not have; the frame posts each program's errors to the
  // page ({type: "status"}), and here they are, under the listing they are in: a module's under its module, the preamble's
  // (module null) under the preamble. Type errors said as a person reads them, as Messed Up Dress Up says them.
  function errorText(message) {
    const nums = t => t.replace(/\b(\d+)\.(\d*?)0+\b/g, "$1.$2");   // (Hazel prints 0. as 0.000000)
    const short = t => { t = nums(t.trim().replace(/\s+/g, " ")); return t.length > 60 ? t.slice(0, 57) + "…" : t; };
    // (Matthew, 2026-11-06, of `total¤(¤shapes)`: "why all of the holes?") Two pieces side by side with nothing joining
    // them: the editor marks the gap with ¤ (grout), and Hazel calls the whole a broken expression
    const b = String(message).match(/^Error in term:\s*\n\s*([\s\S]*?)\nNature of error: Broken expression\s*$/);
    if (b) return `${short(b[1])}: pieces side by side with nothing joining them (the ¤ marks the gap). Join them, with an operator or a comma, or delete one`;
    const m = String(message).match(/^Error in term:\s*\n\s*([\s\S]*?)\nNature of error: Expecting type ([\s\S]*?) but got inconsistent type ([\s\S]*)$/);
    if (!m) return nums(String(message).replace(/\s+/g, " ").replace(/^Error in term: /, ""));
    const ty = t => { t = t.trim().replace(/\s+/g, " "); return /,/.test(t) && !/^\(.*\)$/.test(t) ? `(${t})` : t; };
    const a = t => (/^[AEIOU]/.test(ty(t)) ? "an " : "a ") + ty(t);
    return `${short(m[1])}: ${a(m[2])} is wanted here, but this is ${a(m[3])}`;
  }
  function showStatus(L) {
    const st = programs.get(L.program).status || {};
    const mine = e => L.module ? e.module === L.module : (e.module === null || e.module === undefined);
    const lines = (st.errors || []).filter(mine).map(e => "⚠️ " + errorText(e.message));
    if (L.module) {
      const h = (st.holes || {})[L.module] || 0, u = (st.incomplete || {})[L.module] || 0;
      if (h) lines.push(`${h} hole${h > 1 ? "s" : ""} to fill`);
      if (u) lines.push(`${u} bracket${u > 1 ? "s or keywords" : " or keyword"} without ${u > 1 ? "their partners" : "its partner"}`);
    }
    if (!L.statusEl) { L.statusEl = document.createElement("ul"); L.statusEl.className = "hazel-listing-status"; L.holder.append(L.statusEl); }
    L.statusEl.replaceChildren(...lines.map(t => { const li = document.createElement("li"); li.textContent = t; return li; }));
    L.statusEl.hidden = !lines.length;
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
    // (a page needs no stylesheet of its own for the listings: these defaults, the text hidden once the editor shows, have no
    // weight, by :where(), so any rule of the page's wins; for hazeljs's copy, loaded from npm, Matthew 2026-11-06: "it would
    // be best to have that public package reflect what we do, overall, including documentation")
    if (!document.getElementById("hazel-listings-defaults")) {
      const st = document.createElement("style");
      st.id = "hazel-listings-defaults";
      st.textContent = ':where(.hazel-listing[data-state="loading"], .hazel-listing[data-state="tiles"]) > :where(pre.hazel) { display: none; }\n'
        + ":where(.hazel-listing-frame) { border: 0; }\n"
        + ":where(.hazel-listing-status) { margin: 4px 0 0; padding-left: 1.2em; color: #b45309; }\n"
        + ":where(.hazel-listing-status[hidden]) { display: none; }\n";
      document.head.prepend(st);
    }
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
