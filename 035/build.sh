#!/bin/sh
# ^report(35): the page from body.html and gen035.py, then the series tools in their order
set -e; cd "$(dirname "$0")/.."; P=035/index.html
python3 035/gen035.py
python3 tools/add_theme.py $P; python3 tools/add_listen.py $P; python3 tools/report_refs.py $P; python3 tools/link_prs.py $P
python3 tools/add_steps.py $P; python3 tools/report_data.py 035; python3 tools/add_anchors.py $P; python3 tools/draft_cards.py
