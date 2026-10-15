#!/usr/bin/env bash
set -euo pipefail
set -a
source /etc/chatgpt-browser-recorder.env
set +a
exec /usr/bin/python3 -m uvicorn app:app --host 127.0.0.1 --port "${CHATGPT_BROWSER_RECORDER_PORT:-18107}" --workers 1
