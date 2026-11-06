#!/bin/sh
# ^report(45): the page from body.html, gen045.py and data/timings.json, then the series tools in their order
set -e; cd "$(dirname "$0")/.."; P=045/index.html
python3 045/gen045.py
python3 tools/add_theme.py $P; python3 tools/add_listen.py $P; python3 tools/report_refs.py $P; python3 tools/link_prs.py $P
python3 tools/add_steps.py $P; python3 tools/report_data.py 045; python3 tools/add_anchors.py $P; python3 tools/draft_cards.py
