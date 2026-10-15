#!/usr/bin/env bash
# Erzeugt die zwoelf Systemkarte-Diagramme (6 x DE, 6 x EN) neu und legt sie in public/ ab.
#
# Voraussetzung: Archify (MIT) als Ordner, in dem bin/archify.mjs liegt:
#   git clone https://github.com/tt-a1i/archify   (verwendet wurde Stand d5a1333, Ordner archify/archify)
#   ARCHIFY_DIR=/pfad/zu/archify/archify ./regenerate.sh
#
# Optional: TARGET_ROOT (Standard: der flextrawurst-Ordner dieses Repos) -- zum Probelauf in einer Kopie.
# Danach den Tab neu bauen:  cd <TARGET_ROOT> && npx tsx scripts/build_surface.ts
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TARGET_ROOT="${TARGET_ROOT:-$(cd "$HERE/../.." && pwd)}"
ARCHIFY_DIR="${ARCHIFY_DIR:?ARCHIFY_DIR setzen (Ordner mit bin/archify.mjs, siehe Kopfkommentar)}"
export ARCHIFY_UPDATE_CHECK_DISABLED=1   # kein Netz-Check beim Erzeugen

WORK="$(mktemp -d)"
cp "$HERE/build_i18n.py" "$WORK/"
cd "$WORK"
for L in de en; do python3 build_i18n.py "$L"; done

SLUGS="gesamtbild selbstbild langgraph-weltbild datenbank-rag vaults werkzeuge"
for L in de en; do
  for k in $SLUGS; do
    ( cd "cand/$L/$k" && mkdir -p run \
      && node "$ARCHIFY_DIR/bin/archify.mjs" finalize architecture candidate.json \
           "systemkarte-$k-$L.html" --quality showcase --out-dir run --json > run/finalize.json ) \
      || { echo "FEHLER: finalize $L/$k"; exit 1; }
    python3 - "cand/$L/$k/run/finalize.json" "$L/$k" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
if d.get("status") != "pass":
    sys.exit(f"{sys.argv[2]}: Status {d.get('status')} {d.get('gates')}")
print(sys.argv[2], "pass")
PY
    cp "cand/$L/$k/systemkarte-$k-$L.html" "$TARGET_ROOT/public/"
  done
done

python3 "$HERE/merge_manifest.py" "$WORK/cand" "$TARGET_ROOT/i18n/systemkarte.json"
echo "Fertig (Arbeitsordner: $WORK)."
echo "Naechster Schritt: cd $TARGET_ROOT && npx tsx scripts/build_surface.ts && npx tsx --test tests/surface_ring_23.test.ts"
