#!/bin/sh
# ^report(37), the agenda: its page from data/agenda.json. After a change, to republish: python3 tools/publish_agenda.py 37 "what changed"
set -e; cd "$(dirname "$0")/.."; P=037/index.html
python3 037/drivers/gen037.py
python3 tools/report_refs.py $P; python3 tools/link_prs.py $P; python3 tools/add_theme.py $P; python3 tools/add_anchors.py $P
python3 tools/theme_variants.py 037/img/thumb.svg
