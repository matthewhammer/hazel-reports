"""Syntax highlighting for the series' code: Hazel, Fumola and JS, as spans for HL_CSS (high contrast: bright on black).
Hazel's and Fumola's from ^report(33) (Fumola's colours from its VS Code extension); shared from ^report(30) on.
  from codehl import hazel_hl, fumola_hl, js_hl, HL_CSS   (with tools/ on sys.path)"""
import re, html
esc = html.escape

HZ_KW = {"type", "let", "fun", "case", "end", "module", "in", "if", "then", "else", "test", "true", "false"}
def hazel_hl(t):
    out, i = [], 0
    pat = re.compile(r'(#[^#]*#)|("(?:[^"\\]|\\.)*")|(\b[0-9]+(?:\.[0-9]+)?\b)|(\b[A-Za-z_][A-Za-z0-9_]*\b)|(->|=>|::|\+|\||[=:,.()\[\]!<>*/-])', re.M)
    for m in pat.finditer(t):
        out.append(esc(t[i:m.start()])); i = m.end(); g = m.group(0)
        if m.group(1): out.append(f'<span class="hc">{esc(g)}</span>')
        elif m.group(2): out.append(f'<span class="hs">{esc(g)}</span>')
        elif m.group(3): out.append(f'<span class="hn">{esc(g)}</span>')
        elif m.group(4): out.append(f'<span class="{"hk" if g in HZ_KW else "hC" if g[0].isupper() else "hv"}">{esc(g)}</span>')
        else: out.append(f'<span class="ho">{esc(g)}</span>')
    out.append(esc(t[i:])); return "".join(out)

FU_KW = {"module", "let", "return", "import", "type", "public", "force", "func", "thunk", "switch", "case", "prim", "if", "else", "var", "for", "in", "with", "within", "do", "assert", "goto", "space", "time", "debug_show"}
def fumola_hl(t):
    out, i = [], 0
    pat = re.compile(r'(//.*$)|("(?:[^"\\]|\\.)*")|(`[A-Za-z_][A-Za-z0-9_]*)|(#[A-Za-z_][A-Za-z0-9_]*)|(@[A-Za-z_][A-Za-z0-9_]*)|(\b[A-Za-z_][A-Za-z0-9_]*\b)|([0-9]+)', re.M)
    for m in pat.finditer(t):
        out.append(esc(t[i:m.start()])); i = m.end(); g = m.group(0)
        cls = "fc" if m.group(1) else "fs" if m.group(2) else "fy" if m.group(3) else "ft" if m.group(4) else "fy" if m.group(5) else (
              "fk" if g in FU_KW else "fT" if g[0].isupper() else "fv") if m.group(6) else "fv"
        out.append(f'<span class="{cls}">{esc(g)}</span>')
    out.append(esc(t[i:])); return "".join(out)

JS_KW = {"const", "let", "var", "function", "return", "if", "else", "for", "of", "in", "while", "do", "break", "continue", "new", "this",
         "typeof", "instanceof", "true", "false", "null", "undefined", "switch", "case", "default", "try", "catch", "finally", "throw", "async", "await", "class", "delete"}
def js_hl(t):
    out, i = [], 0
    pat = re.compile(r'(//[^\n]*|/\*[\s\S]*?\*/)|("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|`(?:[^`\\]|\\.)*`)|(\b[0-9]+(?:\.[0-9]+)?\b)|(\b[A-Za-z_$][A-Za-z0-9_$]*\b)|(=>|===|!==|&&|\|\||[=+\-*/<>!?:.,;()\[\]{}])', re.M)
    for m in pat.finditer(t):
        out.append(esc(t[i:m.start()])); i = m.end(); g = m.group(0)
        cls = "jc" if m.group(1) else "js" if m.group(2) else "jn" if m.group(3) else ("jk" if g in JS_KW else "jC" if g[0].isupper() else "jv") if m.group(4) else "jo"
        out.append(f'<span class="{cls}">{esc(g)}</span>')
    out.append(esc(t[i:])); return "".join(out)

# (^report(46), 2026-11-07, Matthew: "please use syntax highlighting throughout") OCaml and ReScript, in Hazel's colours
# (keywords, constructors, strings, numbers, comments, operators): the sources Melange, js_of_ocaml and ReScript compiled
ML_KW = {"let", "rec", "in", "match", "with", "function", "fun", "if", "then", "else", "type", "of", "and", "begin", "end", "for", "to",
         "do", "done", "while", "true", "false", "mod", "not", "open", "module", "struct", "sig", "val", "when", "as", "ref"}
def ml_hl(t):
    out, i = [], 0
    pat = re.compile(r'''(\(\*[\s\S]*?\*\))|("(?:[^"\\]|\\.)*")|(\b[0-9]+(?:\.[0-9]*)?\b)|(\b[A-Za-z_][A-Za-z0-9_']*\b)|(->|::|:=|<-|\|\||&&|\^|[=+\-*/<>|;:,.()\[\]{}])''', re.M)
    for m in pat.finditer(t):
        out.append(esc(t[i:m.start()])); i = m.end(); g = m.group(0)
        cls = "hc" if m.group(1) else "hs" if m.group(2) else "hn" if m.group(3) else ("hk" if g in ML_KW else "hC" if g[0].isupper() else "hv") if m.group(4) else "ho"
        out.append(f'<span class="{cls}">{esc(g)}</span>')
    out.append(esc(t[i:])); return "".join(out)

RES_KW = {"let", "rec", "switch", "if", "else", "type", "list", "true", "false", "open", "module", "and", "when", "as", "mutable", "external"}
def res_hl(t):
    out, i = [], 0
    pat = re.compile(r'(//[^\n]*|/\*[\s\S]*?\*/)|("(?:[^"\\]|\\.)*")|(\b[0-9]+(?:\.[0-9]*)?\b)|(\b[A-Za-z_][A-Za-z0-9_]*\b)|(=>|->|\.\.\.|\+\+|\*\.|&&|\|\||==|[=+\-*/<>|?:;,.()\[\]{}])', re.M)
    for m in pat.finditer(t):
        out.append(esc(t[i:m.start()])); i = m.end(); g = m.group(0)
        cls = "hc" if m.group(1) else "hs" if m.group(2) else "hn" if m.group(3) else ("hk" if g in RES_KW else "hC" if g[0].isupper() else "hv") if m.group(4) else "ho"
        out.append(f'<span class="{cls}">{esc(g)}</span>')
    out.append(esc(t[i:])); return "".join(out)

# (^report(46)) a snippet inside a sentence or a table cell, dark as the listings: <code class="hz"> or <code class="jx">
HL_INLINE_CSS = """
code.hz, code.jx { background: #000; color: #f8f8f2; border-radius: 4px; padding: 1px 5px; }
code.hz .hk { color: #5fd7ff; font-weight: 700; } code.hz .hC { color: #ff87ff; } code.hz .hv { color: #f8f8f2; } code.hz .hs { color: #ffb86c; }
code.hz .hn { color: #bd93f9; } code.hz .hc { color: #87ff87; font-style: italic; } code.hz .ho { color: #ffd75f; }
code.jx .jk { color: #ff79c6; font-weight: 700; } code.jx .jC { color: #8be9fd; } code.jx .jv { color: #f8f8f2; } code.jx .js { color: #f1fa8c; }
code.jx .jn { color: #bd93f9; } code.jx .jc { color: #87ff87; font-style: italic; } code.jx .jo { color: #ffd75f; }
"""

HL = {"hazel": (hazel_hl, "hz"), "fumola": (fumola_hl, "fu"), "js": (js_hl, "jx"), "ocaml": (ml_hl, "hz"), "rescript": (res_hl, "hz")}
HL_CSS = """
pre.hz, pre.fu, pre.jx { background: #000; color: #f8f8f2; border-radius: 8px; padding: 10px 12px; overflow: auto; line-height: 1.5; }
pre.hz .hk { color: #5fd7ff; font-weight: 700; } pre.hz .hC { color: #ff87ff; } pre.hz .hv { color: #f8f8f2; } pre.hz .hs { color: #ffb86c; }
pre.hz .hn { color: #bd93f9; } pre.hz .hc { color: #87ff87; font-style: italic; } pre.hz .ho { color: #ffd75f; }
pre.fu .fk { color: #569CD6; } pre.fu .fT { color: #a989d0; } pre.fu .fv { color: #f6ead2; } pre.fu .fs { color: #c87e60; } pre.fu .fc { color: #6A9955; }
pre.fu .fy { color: #d3a8de; font-weight: 600; } pre.fu .ft { color: #e5c07b; }
pre.jx .jk { color: #ff79c6; font-weight: 700; } pre.jx .jC { color: #8be9fd; } pre.jx .jv { color: #f8f8f2; } pre.jx .js { color: #f1fa8c; }
pre.jx .jn { color: #bd93f9; } pre.jx .jc { color: #87ff87; font-style: italic; } pre.jx .jo { color: #ffd75f; }
"""
