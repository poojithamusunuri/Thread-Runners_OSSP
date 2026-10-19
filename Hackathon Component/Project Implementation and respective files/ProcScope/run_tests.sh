#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 -m py_compile server.py proc_collector.py timeline_tracker.py lab_manager.py event_collector.py verify_tree.py
python3 -m unittest discover -s tests -v
if command -v node >/dev/null 2>&1; then node --check static/app.js; else echo "Node not installed; skipped optional JavaScript syntax check."; fi
