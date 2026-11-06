#!/bin/sh
# ^report(43): the page from body.html and gen043.py (the numbers from data/runs/, the code from example/petri.mjs), then the series tools in their order
set -e; cd "$(dirname "$0")/.."; P=043/index.html
python3 043/gen043.py
python3 tools/add_theme.py $P; python3 tools/add_listen.py $P; python3 tools/report_refs.py $P; python3 tools/link_prs.py $P
python3 tools/add_steps.py $P; python3 tools/report_data.py 043; python3 tools/add_anchors.py $P; python3 tools/draft_cards.py
