#!/bin/bash
# NOTIZ (Omapi, 2026-08-15): Wird automatisch von code-archaeologie-rebuild.path ausgeloest,
# sobald sich eine der vier docs/code_archaeologie_*.md-Dateien aendert -- Daniel: "was denkst
# du werden diese mds im nachhinein nochmal veraendert? ... waere es besser sie wuerden sich
# aktualisieren". Baut die komplette flextrawurst-Surface neu (npm run surface baut alles,
# nicht nur den Code-Archaeologie-Teil -- kein separates Teil-Build vorhanden) und deployt sie
# nach out/process_camera/, damit der server-seitig gebackene Crawler/LLM-Inhalt
# (generateCodeArchaeologieFeedSSR in scripts/build_surface.ts) nie veraltet, ohne dass jemand
# manuell an den Rebuild denken muss.
set -euo pipefail
cd /root/flextrawurst
npm run surface
cp out/surface/flextrawurst_surface.html out/process_camera/flextrawurst_surface.html
echo "$(date -Is) code-archaeologie-rebuild: deployed" >> /var/log/code-archaeologie-rebuild.log
