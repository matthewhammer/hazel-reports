#!/bin/sh
# ^report(38): the page from body.html and gen038.py (figures from data/ and 036/data/), then the series tools in their order
set -e; cd "$(dirname "$0")/.."; P=038/index.html
python3 038/gen038.py
python3 tools/add_theme.py $P; python3 tools/add_listen.py $P; python3 tools/report_refs.py $P; python3 tools/link_prs.py $P
python3 tools/add_steps.py $P; python3 tools/report_data.py 038; python3 tools/add_anchors.py $P; python3 tools/draft_cards.py
