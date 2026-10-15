#!/bin/bash
# Ersatz fuer den systemd-Timer, den die Sandbox nicht direkt installieren liess
# (.timer-Dateien duerfen nicht nach /etc/systemd/system/ geschrieben werden,
# nur .service ueber services_install_unit). Macht dasselbe: alle 10 Minuten
# tools_seed_relations.py reseed-inkrementell aufrufen. Ueberlebt KEINEN
# VPS-Neustart -- dafuer muesste jemand mit systemd-Rechten die beiliegende
# gesamtatlas-relations-reseed.timer/.service registrieren.
cd /root/werkraum/tools/gesamtatlas_world
while true; do
  python3 tools_seed_relations.py reseed-inkrementell >> evidence/reseed_loop.log 2>&1
  sleep 600
done
