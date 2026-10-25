#!/bin/sh
# Regenerate ^report(33) and run the series tools on it, in order.
set -e
cd "$(dirname "$0")/../.."
python3 033/drivers/gen033.py
python3 tools/report_refs.py 033/index.html
python3 tools/link_prs.py 033/index.html
python3 tools/add_theme.py 033/index.html
python3 tools/add_listen.py 033/index.html
python3 tools/add_steps.py 033/index.html
python3 tools/report_data.py 033
python3 tools/add_anchors.py 033/index.html
