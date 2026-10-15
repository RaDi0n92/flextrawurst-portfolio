#!/bin/bash
# Baut das Windows-Paket des ersten Koerpers unter Wine und legt ZIP + Pruefsumme nach dist/.
# Alles, was ins Paket kommt, steht im Repo (client_windows/); nichts haengt an einem temporaeren Ordner.
# Aufruf aus dem Repo-Verzeichnis augen_haende_bridge/:  ./build_paket.sh
set -euo pipefail
cd "$(dirname "$0")"

VERSION=$(python3 - << 'PY'
import re
print(re.search(r'^VERSION = "([^"]+)"', open("src/augen_haende_bridge/koerper/haupt.py", encoding="utf-8").read(), re.M).group(1))
PY
)
WORK=/tmp/g02build
STAGE=/tmp/pkgstage
export WINEPREFIX=${WINEPREFIX:-/config/wine-bridge-build/prefix} WINEARCH=win64 WINEDEBUG=-all WINEDLLOVERRIDES="mscoree,mshtml="
export BRIDGE_NUMPY_CV2_STAGING='Z:\config\wine-bridge-build\staging-numpy-cv2'
unset PYTHONPATH

echo "== Version $VERSION: PyInstaller unter Wine"
rm -rf "$WORK" "$STAGE"; mkdir -p "$WORK" "$STAGE/client_windows"
timeout 550 xvfb-run -a wine 'C:\Python313\python.exe' -m PyInstaller --noconfirm --clean \
    --workpath Z:/tmp/g02build/work --distpath Z:/tmp/g02build/dist AugenUndHaendeBridgeKoerper.spec > "$WORK/log.txt" 2>&1 \
    || { tail -20 "$WORK/log.txt"; echo "PyInstaller fehlgeschlagen"; exit 1; }
[ -f "$WORK/dist/AugenUndHaendeBridge-G02/AugenUndHaendeBridge.exe" ] || { echo "exe fehlt"; exit 1; }

echo "== Paket zusammenstellen"
cp -r "$WORK/dist/AugenUndHaendeBridge-G02" "$STAGE/AugenUndHaendeBridge"
cp client_windows/start_bridge.bat client_windows/start_with_ssh_tunnel.ps1 "$STAGE/client_windows/"
cp client_windows/selbsttest.bat "$STAGE/"
sed "s/@VERSION@/$VERSION/g" client_windows/START_ANLEITUNG.txt > "$STAGE/START_ANLEITUNG.txt"
DEPS=$(timeout 120 xvfb-run -a wine 'C:\Python313\python.exe' -m pip list --format=freeze 2>/dev/null | tr -d '\r' \
    | grep -i -E '^(websockets|pyte|pillow|sounddevice|cffi|numpy|opencv-python-headless|pyinstaller)==' | tr '\n' ' ' || true)
{
  echo "AugenUndHaendeBridge $VERSION (PLAN-G02, erster Koerper)"
  echo "Gebaut: $(date +%F) unter Wine $(wine --version 2>/dev/null | tr -d '\r') (--onedir, unsigniert)"
  echo "Abhaengigkeiten (aus dem Build-Prefix): ${DEPS:-nicht ermittelt}"
  echo "numpy und opencv (als Dateien beigelegt, Staging): $(ls /config/wine-bridge-build/staging-numpy-cv2 | grep -E 'dist-info$' | sed 's/\.dist-info//' | grep -i -E '^(numpy|opencv)' | tr '\n' ' ')"
  echo "Quellstand: git rev-parse HEAD = $(git rev-parse --short HEAD 2>/dev/null || echo unbekannt) (augen_haende_bridge/)"
} > "$STAGE/VERSION.txt"
(cd "$STAGE" && find . -type f ! -name PAKET_SHA256.txt -print0 | sort -z | xargs -0 sha256sum > PAKET_SHA256.txt)

echo "== ZIP und Pruefsumme"
rm -f dist/AugenUndHaendeBridge-G02-win64.zip
python3 - << 'PY'
import os, zipfile
src = "/tmp/pkgstage"
with zipfile.ZipFile("dist/AugenUndHaendeBridge-G02-win64.zip", "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, _, files in os.walk(src):
        for f in sorted(files):
            p = os.path.join(root, f)
            z.write(p, os.path.relpath(p, src))
PY
(cd dist && sha256sum AugenUndHaendeBridge-G02-win64.zip | tee AugenUndHaendeBridge-G02-win64.zip.sha256)
echo "== fertig: dist/AugenUndHaendeBridge-G02-win64.zip ($VERSION)"
