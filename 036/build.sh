#!/bin/sh
# ^report(36): the page from body.html and gen036.py (figures from data/), then the series tools in their order
set -e; cd "$(dirname "$0")/.."; P=036/index.html
python3 036/drivers/medians.py > /dev/null
python3 036/gen036.py
python3 tools/add_theme.py $P; python3 tools/add_listen.py $P; python3 tools/report_refs.py $P; python3 tools/link_prs.py $P
python3 tools/add_steps.py $P; python3 tools/report_data.py 036; python3 tools/add_anchors.py $P; python3 tools/draft_cards.py
