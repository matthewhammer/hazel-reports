#!/bin/sh
# ^report(53): the page from body.html and gen053.py, then the series tools in their order
set -e; cd "$(dirname "$0")/.."; P=053/index.html
python3 053/gen053.py
python3 tools/add_theme.py $P; python3 tools/add_listen.py $P; python3 tools/report_refs.py $P; python3 tools/link_prs.py $P
python3 tools/add_steps.py $P; python3 tools/report_data.py 053; python3 tools/add_anchors.py $P; python3 tools/draft_cards.py
