#!/usr/bin/env bash
set -euo pipefail
python -m qa_agents.run_test --goal "Toggle Wi‑Fi off and on" --env mock --logs_dir /mnt/data/qa_agents/logs
echo "Done. See /mnt/data/qa_agents/logs"
