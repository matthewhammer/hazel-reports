#!/bin/sh
# ^report(67): the page from body.html, data/*.json (and 063's, 064's and 065's data) and gen067.py, then the series tools in their order
set -e; cd "$(dirname "$0")/.."; P=067/index.html
python3 067/gen067.py
python3 tools/add_theme.py $P; python3 tools/add_listen.py $P; python3 tools/report_refs.py $P; python3 tools/link_prs.py $P
python3 tools/add_steps.py $P; python3 tools/report_data.py 067; python3 tools/add_anchors.py $P; python3 tools/add_highlights.py $P; python3 tools/draft_cards.py
