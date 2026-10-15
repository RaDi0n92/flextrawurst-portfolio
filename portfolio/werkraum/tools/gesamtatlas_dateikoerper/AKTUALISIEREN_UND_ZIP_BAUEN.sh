#!/usr/bin/env bash
set -euo pipefail
cd /root/werkraum/tools/gesamtatlas_dateikoerper
exec /usr/bin/python3 build.py --force --verify-sections
