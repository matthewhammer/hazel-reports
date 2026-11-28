#!/bin/sh
# ^report(68): the page from body.html, data/*.json (parse_frames.py from the job's logs; sizes.py) and gen068.py, then the series tools in their order
set -e; cd "$(dirname "$0")/.."; P=068/index.html
python3 068/gen068.py
python3 tools/add_theme.py $P; python3 tools/add_listen.py $P; python3 tools/report_refs.py $P; python3 tools/link_prs.py $P
python3 tools/add_steps.py $P; python3 tools/report_data.py 068; python3 tools/add_anchors.py $P; python3 tools/add_highlights.py $P; python3 tools/draft_cards.py
