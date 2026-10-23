#!/bin/sh
# Regenerate ^report(32) and run the series tools on it, in order.
set -e
cd "$(dirname "$0")/../.."
python3 032/drivers/gen032.py
python3 tools/report_refs.py 032/index.html
python3 tools/link_prs.py 032/index.html
python3 tools/add_theme.py 032/index.html
python3 tools/add_listen.py 032/index.html
python3 tools/report_data.py 032
python3 tools/add_anchors.py 032/index.html
