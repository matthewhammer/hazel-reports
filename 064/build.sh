#!/bin/sh
# ^report(64): the page from gen064.py and data/, then the series tools in their order (its data is embedded by gen064.py)
set -e; cd "$(dirname "$0")/.."; P=064/index.html
python3 064/gen064.py
python3 tools/add_theme.py $P; python3 tools/add_listen.py $P; python3 tools/report_refs.py $P; python3 tools/link_prs.py $P
python3 tools/add_steps.py $P; python3 tools/add_anchors.py $P; python3 tools/draft_cards.py
