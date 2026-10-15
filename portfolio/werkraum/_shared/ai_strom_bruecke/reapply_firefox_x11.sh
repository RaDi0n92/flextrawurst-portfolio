#!/usr/bin/env bash
set -euo pipefail

container_name="${AI_STROM_BRUECKE_CONTAINER:-virtuellerdesktop2}"
root_dir="$(dirname "$0")"

docker cp "$root_dir/firefox-x11" "${container_name}:/config/firefox-x11"
docker cp "$root_dir/firefox-x11" "${container_name}:/usr/local/bin/firefox-x11"
docker cp "$root_dir/firefox-x11" "${container_name}:/usr/local/bin/firefox"
docker exec "$container_name" sh -lc \
  "sed -i 's/^Exec=firefox %u$/Exec=firefox-x11 %u/; s/^Exec=firefox -new-window$/Exec=firefox-x11 -new-window/; s/^Exec=firefox -private-window$/Exec=firefox-x11 -private-window/' /usr/share/applications/firefox.desktop"
echo "AI-Strom-Brücke: Firefox-X11-Startpfad in ${container_name} re-applied."
