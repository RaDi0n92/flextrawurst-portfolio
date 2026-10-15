#!/usr/bin/env bash
set -euo pipefail

container_name="${AI_STROM_BRUECKE_CONTAINER:-virtuellerdesktop2}"
target="/lsiopy/lib/python3.14/site-packages/selkies/selkies.py"
temporary_dir="$(mktemp -d /tmp/ai-strom-bruecke-selkies.XXXXXX)"
trap 'rm -rf "$temporary_dir"' EXIT

docker cp "${container_name}:${target}" "$temporary_dir/selkies.py"
patch -d "$temporary_dir" -p0 < "$(dirname "$0")/selkies_input_mirror.patch"
python3 -m py_compile "$temporary_dir/selkies.py"
docker cp "$temporary_dir/selkies.py" "${container_name}:${target}"
docker exec "$container_name" s6-svc -r /run/service/svc-selkies
echo "AI-Strom-Brücke: Selkies-Mirror in ${container_name} re-applied."
