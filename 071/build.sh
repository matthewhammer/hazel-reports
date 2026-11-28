#!/bin/sh
# ^report(71): the page from body.html, data/*.json (parse_frames.py from the jobs' logs; pane.json) and gen071.py, then the series tools in their order
set -e; cd "$(dirname "$0")/.."; P=071/index.html
python3 071/gen071.py
python3 tools/add_theme.py $P; python3 tools/add_listen.py $P; python3 tools/report_refs.py $P; python3 tools/link_prs.py $P
python3 tools/add_steps.py $P; python3 tools/report_data.py 071; python3 tools/add_anchors.py $P; python3 tools/add_highlights.py $P; python3 tools/draft_cards.py
