#!/bin/sh
# ^report(40): the page from body.html and gen040.py (tables and Figure 1 from data/boundary.json), then the series tools in their order
set -e; cd "$(dirname "$0")/.."; P=040/index.html
python3 040/gen040.py
python3 tools/add_theme.py $P; python3 tools/add_listen.py $P; python3 tools/report_refs.py $P; python3 tools/link_prs.py $P
python3 tools/add_steps.py $P; python3 tools/report_data.py 040; python3 tools/add_anchors.py $P; python3 tools/draft_cards.py
