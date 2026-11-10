#!/bin/sh
# ^report(52): the page from body.html and gen052.py, then the series tools in their order
set -e; cd "$(dirname "$0")/.."; P=052/index.html
python3 052/gen052.py
python3 tools/add_theme.py $P; python3 tools/add_listen.py $P; python3 tools/report_refs.py $P; python3 tools/link_prs.py $P
python3 tools/add_steps.py $P; python3 tools/report_data.py 052; python3 tools/add_anchors.py $P; python3 tools/draft_cards.py
