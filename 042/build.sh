#!/bin/sh
# ^report(42), the agenda: its page from data/agenda.json. After a change, to republish: python3 tools/publish_agenda.py 42 "what changed"
set -e; cd "$(dirname "$0")/.."; P=042/index.html
python3 042/drivers/gen042.py
python3 tools/report_refs.py $P; python3 tools/link_prs.py $P; python3 tools/add_theme.py $P; python3 tools/add_anchors.py $P
python3 tools/theme_variants.py 042/img/thumb.svg
