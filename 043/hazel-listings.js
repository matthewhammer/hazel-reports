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

  // ---- long lines broken to fit the listing's width (^ticket(707), hazelgrove/hazeljs#1; Matthew, 2026-11-06: "adjust to
  // resize --- like we do in MUDU, to linewrap dynamically on LHS (or any code listing)"). Messed Up Dress Up's way, from its
  // js/25-scripting.js at 15181ee0 (scriptTokens, scriptFlowPieces, scriptFlow, scriptTileCols), Hazel's half of it: a line
  // longer than the listing is laid out as a pretty-printer would, broken at the outermost places the code allows (a case's
  // arms, a let's body, a list's items...), each piece 2 deeper; only spaces and line breaks change, never inside a string or
  // a comment, so the program means what it meant. The frame is sent that copy; the page keeps its own text, so a wider
  // listing gets the long lines back.
  const KEYWORDS = new Set("let in fun case end if then else type module test rec and or".split(" "));
  function tokens(text) {
    const rules = [["c", /#[^#\n]*#?/y], ["s", /"(\\.|[^"\\\n])*"?/y], ["n", /\d+(\.\d+)?/y],
      ["w", /[A-Za-z_]\w*/y], ["o", /=>|->|\+\+|[|=<>!+\-*\/%:;,.?#@&^~]+/y], ["t", /\s+|./y]];
    const out = [];
    for (let i = 0; i < text.length;) {
      for (const [k, re] of rules) {
        re.lastIndex = i; const m = re.exec(text);
        if (!m || !m[0]) continue;
        const w = m[0];
        out.push([k === "w" ? (KEYWORDS.has(w) ? "k" : /^[A-Z]/.test(w) ? "C" : "") : k === "t" ? "" : k, w]);
        i += w.length; break;
      }
    }
    return out;
  }
  // the places a line may break, best first: before a case's | ; before a sum's + ; before then and else ; after ; and before
  // a closing } ; after , and { and in ; after => and -> ; before || and && ; after a let's =. (Since 707, a string's ++ breaks
  // where a sum's + does: the game's never did, and a long message in a Say(...) stayed wider than the listing)
  const BREAKS = [[["|"], []], [["+", "++"], []], [["then", "else"], []], [["}"], [";"]], [[], [",", "{", "in"]], [[], ["=>", "->"]], [["||", "&&"], []], [[], ["="]]];
  function flowPieces(toks, indent, cols, out) {
    const text = toks.map(([, w]) => w).join("").trim();
    if (indent + text.length <= cols) { out.push(" ".repeat(indent) + text); return; }
    // a comment alone, too long: several comments, its words shared out, each # ... # closed
    const real = toks.filter(([, w]) => w.trim());
    if (real.length === 1 && real[0][0] === "c") {
      const words = text.replace(/^#\s*/, "").replace(/\s*#$/, "").split(/\s+/);
      const room = Math.max(12, cols - indent - 4);
      let cur = "";
      const flush = () => { if (cur) out.push(" ".repeat(indent) + "# " + cur + " #"); cur = ""; };
      for (const w of words) { if (cur && cur.length + 1 + w.length > room) flush(); cur = cur ? cur + " " + w : w; }
      flush(); return;
    }
    // each place: the token index the next piece starts at, the bracket depth there, how good a place it is, and how deeply
    // it sits inside an open let, fun, case or if (a then, else, in, -> or => belongs to its own one, so a line cuts at its
    // outermost first, and an inner one that fits stays whole)
    const places = [], open = [];
    let depth = 0;
    toks.forEach(([k, w], i) => {
      const code = k === "o" || k === "k" || (k === "" && /^[()[\]{}]$/.test(w));
      const here = () => open.filter(o => o.depth === depth), top = () => here().pop();
      const owner = kind => here().some(o => o.kind === kind && !o.done);
      const upTo = kind => { while (!(top().kind === kind && !top().done)) open.pop(); top().done = true; };
      let part = false;
      if (k === "k" && ["if", "let", "fun", "case"].includes(w)) open.push({ kind: w, depth, done: false });
      else if (k === "k" && w === "then") part = true;
      else if (k === "k" && w === "else") { if (owner("if")) upTo("if"); part = true; }
      else if (k === "k" && w === "in" && owner("let")) { upTo("let"); part = true; }
      else if (k === "o" && w === "->" && owner("fun")) { upTo("fun"); part = true; }
      else if (k === "o" && w === "=>" && owner("arm")) { upTo("arm"); part = true; }
      else if (k === "o" && w === "|" && owner("case")) { while (top().kind !== "case") open.pop(); part = true; }
      else if (k === "k" && w === "end" && owner("case")) { while (top().kind !== "case") open.pop(); open.pop(); }
      else if ((k === "o" && ["|", ",", ";"].includes(w)) || (k === "k" && w === "in")) while (top()) open.pop();
      const nest = part ? Math.max(0, here().length - 1) : here().length, d0 = depth;
      if (k === "o" && w === "|") open.push({ kind: "arm", depth, done: false });
      if (k === "c" && i > 0) places.push({ at: i, depth, rank: -1, nest: 0 });   // (a comment after code: first to its own line)
      if (code && i > 0) BREAKS.forEach(([before], rank) => { if (before.includes(w)) places.push({ at: i, depth, rank, nest }); });
      if (k === "" || k === "o") for (const ch of w) depth += "([{".includes(ch) ? 1 : ")]}".includes(ch) ? -1 : 0;
      while (open.length && open[open.length - 1].depth > depth) open.pop();
      if (code && i + 1 < toks.length) BREAKS.forEach(([, after], rank) => { if (after.includes(w)) places.push({ at: i + 1, depth, rank, after: w, nest: depth === d0 ? nest : 0 }); });
    });
    if (!places.length) { out.push(" ".repeat(indent) + text); return; }
    const low = Math.min(...places.map(p => p.depth));
    const atDepth = places.filter(p => p.depth === low), least = Math.min(...atDepth.map(p => p.nest)), atLow = atDepth.filter(p => p.nest === least);
    const best = Math.min(...atLow.map(p => p.rank));
    const chosen = atLow.filter(p => p.rank === best || (best === 3 && p.after === "{"));
    const cuts = [...new Set(chosen.map(p => p.at))].sort((x, y) => x - y);
    // members cut apart at the line's own level (after ; , or in) are siblings, each at the line's indent; so are an if's then
    // and else, and a case's arms, when the piece begins with that if or case
    const sibling = new Set(low === 0 ? chosen.filter(p => [";", ",", "in"].includes(p.after)).map(p => p.at) : []);
    const lead = toks.filter(([, w]) => w.trim()).slice(0, 2).map(([, w]) => w).join(" ");
    if (low === 0 && (lead === "else if" || lead.startsWith("if "))) chosen.filter(p => !p.after && ["then", "else"].includes(toks[p.at][1])).forEach(p => sibling.add(p.at));
    if (low === 0 && lead.startsWith("case ")) chosen.filter(p => !p.after && toks[p.at][1] === "|").forEach(p => sibling.add(p.at));
    let from = 0;
    for (const c of [...cuts, toks.length]) {
      const piece = toks.slice(from, c);
      if (piece.some(([, w]) => w.trim())) {
        const first = piece.filter(([, w]) => w.trim())[0][1];
        const ind = from === 0 || sibling.has(from) ? indent : indent + 2 * (/^[)\]}]/.test(first) ? Math.max(0, low - 1) : Math.max(1, low));
        flowPieces(piece, ind, cols, out);
      }
      from = c;
    }
  }
  function flow(text, cols) {
    if (!(cols > 20) || cols === Infinity) return text;
    return text.split("\n").flatMap(line => {
      if (line.length <= cols) return [line];
      const base = line.match(/^ */)[0].length, out = [];
      flowPieces(tokens(line.slice(base)), base, cols, out);
      return out;
    }).join("\n");
  }
  // the listing's width in characters, measured in the font the frame is sent (the page's own for its code), less the
  // editor's margins; Infinity while it has no width (not drawn yet), so nothing is broken
  const GUTTER = 3;
  let measure = null;
  function cols(L) {
    const w = L.holder.clientWidth;
    if (!(w > 0)) return Infinity;
    measure = measure || document.createElement("canvas").getContext("2d");
    measure.font = L.fontSize + "px " + L.fontFamily;
    const ch = measure.measureText("0123456789").width / 10 || 0.6 * L.fontSize;
    return Math.max(20, Math.floor(w / ch) - GUTTER);
  }

  // (since ^ticket(707)) the listing's own text broken to fit it; the others' as they are (the frame shows its own alone)
  function frameSpec(L) {
    const P = programs.get(L.program), c = cols(L);
    if (!L.module) return { preamble: flow(L.text, c), modules: [], tail: "" };
    const sp = specOf(P);
    return { ...sp, modules: sp.modules.map(m => m.name === L.module ? { ...m, text: flow(m.text, c) } : m) };
  }
  // what the frame shows of the listing's own text, as last sent: an edit message carrying it back is no edit
  function shownOf(sp, L) {
    return L.module ? (sp.modules.find(m => m.name === L.module) || {}).text : sp.preamble;
  }
  function send(L, force) {
    if (!L.ready) return;
    const sp = frameSpec(L), key = JSON.stringify(sp);
    if (key === L.sent && !force) return;
    L.sent = key;
    L.shown = shownOf(sp, L);
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
      post(L, { type: "font", size: L.fontSize, family: L.fontFamily });   // (the family, so cols() measures what it shows)
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
      if (text === L.text || text === L.shown) return;
      L.undo.push(L.text); L.redo = [];
      L.text = text;
      L.shown = text;
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
                  fontFamily: getComputedStyle(pre).fontFamily || "ui-monospace, Menlo, Consolas, monospace", shown: null,
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
    // broken to fit again when a listing's width changes (the window, a divider, full screen): each frame whose columns
    // changed is sent its text anew, 300 ms after the last change (send() sends nothing when nothing changed)
    let reflowTimer = null;
    const reflowSoon = () => { clearTimeout(reflowTimer); reflowTimer = setTimeout(() => { for (const L of listings) send(L); }, 300); };
    if (window.ResizeObserver) { const ro = new ResizeObserver(reflowSoon); for (const L of listings) ro.observe(L.holder); }
    window.addEventListener("resize", reflowSoon);
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
