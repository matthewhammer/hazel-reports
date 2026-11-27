#!/bin/sh
# ^report(66), the agenda for 2026-11-27: its page from data/agenda.json. Local only until Matthew publishes it (then: python3 tools/publish_agenda.py 66 "what changed").
set -e; cd "$(dirname "$0")/.."; P=066/index.html
python3 066/drivers/gen066.py
python3 tools/report_refs.py $P; python3 tools/link_prs.py $P; python3 tools/add_theme.py $P; python3 tools/add_anchors.py $P; python3 tools/add_highlights.py $P
python3 tools/theme_variants.py 066/img/thumb.svg
