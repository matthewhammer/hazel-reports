#!/bin/sh
# ^report(46): the page from body.html, gen046.py and data/timings.json, then the series tools in their order
set -e; cd "$(dirname "$0")/.."; P=046/index.html
python3 046/gen046.py
python3 tools/add_theme.py $P; python3 tools/add_listen.py $P; python3 tools/report_refs.py $P; python3 tools/link_prs.py $P
python3 tools/add_steps.py $P; python3 tools/report_data.py 046; python3 tools/add_anchors.py $P; python3 tools/draft_cards.py
