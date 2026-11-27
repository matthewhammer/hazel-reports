#!/usr/bin/env python3
"""Sentence highlights on a report (Matthew, 2026-11-27: "a 'highlight sentence' feature to the latest report, and all reports
going forward"). Each sentence of the report's text takes a click, and cycles through three states:
  not highlighted (as it starts);
  pre discussion: to discuss, a bright background and dark text;
  post discussion: discussed, a dim background and bright text.
What is highlighted stays so after a reload: kept in this browser's storage (localStorage), for this report's address. At the
end of the report, one list of every sentence highlighted, in the order they appear, each marked pre or post discussion; a
click on one there goes to it. A sentence is known by its words (a hash of them), so a highlight lasts as long as the sentence
is unchanged; one the report no longer has stays in the list, marked so.

The sentences are found in the browser, in the report's paragraphs, list items, captions and table cells (not headings, code
blocks, figures' drawings or buttons), split after . ! ? or … where the next word starts with a capital, a digit or a quote;
a sentence that runs through a link or a code chip is one sentence, and a link in it still opens on a click.

Idempotent (between markers).  python3 tools/add_highlights.py page.html ..."""
import sys

B, E = "<!-- highlights: begin -->", "<!-- highlights: end -->"
BLOCK = B + r'''
<style>
  .hl-s { border-radius: 3px; -webkit-box-decoration-break: clone; box-decoration-break: clone; transition: background-color .15s, color .15s; }
  @media (hover: hover) { .hl-s:not([data-hl]):hover { background: color-mix(in srgb, #facc15 22%, transparent); cursor: pointer; } .hl-s[data-hl]:hover { cursor: pointer; } }
  .hl-s[data-hl="1"], .hl-chip[data-hl="1"] { background: #fde047; color: #111827; }
  .hl-s[data-hl="2"], .hl-chip[data-hl="2"] { background: #475569; color: #f1f5f9; }
  .hl-s[data-hl] code { background: transparent; color: inherit; }
  .hl-s.hl-flash { outline: 3px solid var(--accent, #6d28d9); outline-offset: 2px; }
  #highlights h2 { margin-top: 56px; }
  #highlights .hl-help { color: var(--muted, GrayText); }
  #highlights ol { padding-left: 1.6em; }
  #highlights li { margin: .5em 0; cursor: pointer; }
  #highlights li:hover .hl-text { text-decoration: underline; text-decoration-color: var(--line, #ccc); }
  .hl-chip { display: inline-block; font: 600 0.78em system-ui, sans-serif; padding: 1px 8px; border-radius: 999px; margin-right: 6px; white-space: nowrap; vertical-align: 1px; }
  .hl-gone { color: var(--muted, GrayText); font-style: italic; }
  .hl-tools button { font: inherit; font-size: 0.9em; padding: 4px 12px; border-radius: 8px; border: 1px solid var(--line, #ccc); background: var(--paper, Canvas); color: var(--ink, CanvasText); cursor: pointer; margin-right: 6px; }
  .hl-badge { position: fixed; right: 14px; bottom: 14px; z-index: 40; padding: 6px 12px; border-radius: 999px; font: 600 13px system-ui, sans-serif;
    text-decoration: none; background: var(--paper, Canvas); color: var(--ink, CanvasText); border: 1px solid var(--line, #ccc); box-shadow: 0 2px 10px rgba(0,0,0,.18); }
  .hl-badge[hidden] { display: none; }
  @media print { .hl-badge, .hl-tools { display: none; } .hl-s:not([data-hl]) { background: none; } }
</style>
<script>
/* Sentence highlights (tools/add_highlights.py): a click on a sentence cycles it through not highlighted, pre discussion and
   post discussion; kept in this browser for this report; one list of them at the end, in the order they appear. */
(() => {
  "use strict";
  const KEY = "hazel-reports/highlights:" + location.pathname.replace(/index\.html$/, "");
  const main = document.querySelector("main") || document.body;
  const SKIP = "script,style,pre,svg,math,button,input,textarea,select,nav,h1,h2,h3,h4,h5,h6,.series,.hl-skip,#highlights,.hl-badge,.theme-toggle";
  const BLOCKS = "p,li,figcaption,td,th,dd,dt,blockquote";
  const NAMES = { 1: "pre discussion", 2: "post discussion" };
  const load = () => { try { const m = JSON.parse(localStorage.getItem(KEY)); return m && typeof m === "object" ? m : {}; } catch (e) { return {}; } };
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(marks)); } catch (e) { /* this visit only */ } };
  const hash = t => { let x = 0x811c9dc5; for (let i = 0; i < t.length; i++) { x ^= t.charCodeAt(i); x = Math.imul(x, 0x01000193); } return (x >>> 0).toString(36); };
  const norm = t => t.replace(/\s+/g, " ").trim();
  // 1. the text, block by block: each paragraph, item, caption or cell's own text nodes, in order
  const groups = new Map(), walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT);
  for (let n; (n = walker.nextNode()); ) {
    const el = n.parentElement; if (!el || !n.data.trim() || el.closest(SKIP)) continue;
    const b = el.closest(BLOCKS); if (!b || !main.contains(b)) continue;
    if (!groups.has(b)) groups.set(b, []); groups.get(b).push(n);
  }
  // 2. each block's sentences: a cut after . ! ? or …, and closing quotes or brackets, where the next word starts with a capital,
  // a digit, a quote or an opening bracket; each sentence known by its words, a second of the same words numbered
  const END = /[.!?…]+["”’)\]]*(?=\s+["“‘(\[]*[\p{Lu}\d^¹²³\p{Extended_Pictographic}])/gu;
  const TEXT = new Map(), ORDER = [], seen = new Map();
  for (const [b, nodes] of groups) {
    const full = nodes.map(n => n.data).join(""), cuts = [0];
    END.lastIndex = 0; for (let m; (m = END.exec(full)); ) cuts.push(m.index + m[0].length);
    cuts.push(full.length);
    const sents = [];
    for (let i = 0; i + 1 < cuts.length; i++) {
      let a = cuts[i], z = cuts[i + 1]; while (a < z && /\s/.test(full[a])) a++; while (z > a && /\s/.test(full[z - 1])) z--;
      const t = norm(full.slice(a, z)); if (!/[\p{L}\d]/u.test(t)) continue;
      const h = hash(t), k = seen.get(h) || 0; seen.set(h, k + 1);
      const id = h + (k ? "-" + k : ""); sents.push({ a, z, id }); TEXT.set(id, t); ORDER.push(id);
    }
    // 3. each text node's parts that lie in a sentence, wrapped: a sentence through a link or a chip is several spans, one id
    let off = 0;
    for (const n of nodes) {
      const s0 = off, s1 = off + n.data.length; off = s1;
      const parts = sents.filter(S => S.a < s1 && S.z > s0); if (!parts.length) continue;
      const frag = document.createDocumentFragment(); let p = s0;
      for (const S of parts) {
        const a = Math.max(S.a, s0), z = Math.min(S.z, s1);
        if (a > p) frag.append(n.data.slice(p - s0, a - s0));
        const sp = document.createElement("span"); sp.className = "hl-s"; sp.dataset.s = S.id; sp.textContent = n.data.slice(a - s0, z - s0);
        frag.append(sp); p = z;
      }
      if (p < s1) frag.append(n.data.slice(p - s0));
      n.replaceWith(frag);
    }
  }
  const rank = new Map(ORDER.map((id, i) => [id, i]));
  let marks = load();
  // 4. the list at the end, and a badge that goes to it
  const sec = document.createElement("section"); sec.id = "highlights";
  sec.innerHTML = '<h2>Highlighted sentences</h2><p class="hl-help">Click any sentence above to mark it <span class="hl-chip" data-hl="1">pre discussion</span>; ' +
    'again, <span class="hl-chip" data-hl="2">post discussion</span>; again, not highlighted. Kept in this browser, for this report.</p>' +
    '<div class="hl-list"></div><p class="hl-tools"><button type="button" class="hl-copy">📋 Copy the list</button><button type="button" class="hl-clear">Clear all</button></p>';
  const dataEl = main.querySelector('script[type="application/json"]');
  if (dataEl && dataEl.parentElement === main) main.insertBefore(sec, dataEl); else main.append(sec);
  const badge = document.createElement("a"); badge.className = "hl-badge"; badge.href = "#highlights"; badge.hidden = true; document.body.append(badge);
  const esc = t => t.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const listed = () => Object.keys(marks).filter(id => marks[id] && (marks[id].s === 1 || marks[id].s === 2))
    .sort((a, b) => (rank.has(a) ? rank.get(a) : 1e9) - (rank.has(b) ? rank.get(b) : 1e9) || String(marks[a].at).localeCompare(String(marks[b].at)));
  function paint() {
    for (const el of main.querySelectorAll(".hl-s")) { const m = marks[el.dataset.s]; if (m && m.s) el.dataset.hl = m.s; else delete el.dataset.hl; }
    const ids = listed(), box = sec.querySelector(".hl-list");
    box.innerHTML = ids.length ? "<ol>" + ids.map(id => { const m = marks[id], gone = !rank.has(id);
      return `<li data-id="${esc(id)}"><span class="hl-chip" data-hl="${m.s}">${NAMES[m.s]}</span><span class="hl-text">${esc(TEXT.get(id) || m.t || "")}</span>${gone ? ' <span class="hl-gone">(no longer in this report)</span>' : ""}</li>`; }).join("") + "</ol>"
      : '<p class="hl-gone">None yet.</p>';
    const pre = ids.filter(id => marks[id].s === 1).length, post = ids.length - pre;
    badge.hidden = !ids.length; badge.textContent = `🖍 ${pre} pre · ${post} post discussion`;
  }
  // 5. a click on a sentence cycles it; a link, a button or a selection of text is left alone
  main.addEventListener("click", e => {
    if (e.target.closest("a,button,input,select,textarea,summary,label,svg,#highlights")) return;
    const sel = window.getSelection ? String(window.getSelection()) : ""; if (sel.trim()) return;
    const sp = e.target.closest(".hl-s"); if (!sp) return;
    const id = sp.dataset.s, cur = (marks[id] && marks[id].s) | 0, nx = (cur + 1) % 3;
    if (nx) marks[id] = { s: nx, t: TEXT.get(id) || sp.textContent, at: (marks[id] && marks[id].at) || new Date().toISOString() }; else delete marks[id];
    save(); paint();
  });
  sec.addEventListener("click", e => {
    if (e.target.closest(".hl-copy")) {
      const lines = listed().map(id => `- [${NAMES[marks[id].s]}] ${TEXT.get(id) || marks[id].t}`), text = (document.title + "\n" + location.href.split("#")[0] + "\n\n" + lines.join("\n")).trim();
      const b = e.target.closest(".hl-copy"), done = () => { b.textContent = "📋 Copied"; setTimeout(() => { b.textContent = "📋 Copy the list"; }, 1500); };
      try { navigator.clipboard.writeText(text).then(done, () => {}); } catch (err) { /* no clipboard here */ }
      return;
    }
    if (e.target.closest(".hl-clear")) { const n = listed().length; if (n && confirm(`Clear all ${n} highlighted sentences in this report?`)) { marks = {}; save(); paint(); } return; }
    const li = e.target.closest("li[data-id]"); if (!li) return;
    const first = main.querySelector(`.hl-s[data-s="${CSS.escape(li.dataset.id)}"]`); if (!first) return;
    first.scrollIntoView({ behavior: "smooth", block: "center" });
    const all = main.querySelectorAll(`.hl-s[data-s="${CSS.escape(li.dataset.id)}"]`); all.forEach(el => el.classList.add("hl-flash"));
    setTimeout(() => all.forEach(el => el.classList.remove("hl-flash")), 1400);
  });
  addEventListener("storage", e => { if (e.key === KEY) { marks = load(); paint(); } });   // (another tab of this report)
  paint();
})();
</script>
''' + E


def add(path):
    s = open(path, encoding="utf-8").read()
    if B in s:
        s = s[:s.index(B)] + s[s.index(E) + len(E):]
    i = s.rindex("</body>")
    s = s[:i] + BLOCK + "\n" + s[i:]
    open(path, "w", encoding="utf-8").write(s)
    print("highlights:", path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        add(p)
