#!/bin/sh
# ^report(46): the page from body.html, gen046.py and data/timings.json, then the series tools in their order
set -e; cd "$(dirname "$0")/.."; P=046/index.html
python3 046/gen046.py
# the Witch view's pages, one per compiled output (witch046.py), in the series' theme too
for W in 046/witch/*.html; do python3 tools/add_theme.py $W; python3 tools/report_refs.py $W; done
python3 tools/add_theme.py $P; python3 tools/add_listen.py $P; python3 tools/report_refs.py $P; python3 tools/link_prs.py $P
python3 tools/add_steps.py $P; python3 tools/report_data.py 046; python3 tools/add_anchors.py $P; python3 tools/draft_cards.py
# (Matthew, 2026-11-07: "syntax highlighting throughout") the snippets the series' tools add after the generator (the data line), highlighted too
python3 - <<'PY'
import html, re, sys
sys.path.insert(0, "tools")
from codehl import js_hl
p = "046/index.html"; s = open(p).read()
s = re.sub(r"<code>(.*?)</code>", lambda m: '<code class="jx">' + js_hl(html.unescape(m.group(1))) + "</code>", s)
open(p, "w").write(s)
PY
