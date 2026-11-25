#!/bin/sh
# ^report(65): the page from body.html, data/*.json and gen065.py, then the series tools in their order
set -e; cd "$(dirname "$0")/.."; P=065/index.html
python3 065/gen065.py
python3 tools/add_theme.py $P; python3 tools/add_listen.py $P; python3 tools/report_refs.py $P; python3 tools/link_prs.py $P
python3 tools/add_steps.py $P; python3 tools/report_data.py 065; python3 tools/add_anchors.py $P; python3 tools/draft_cards.py
