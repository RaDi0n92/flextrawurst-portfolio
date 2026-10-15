#!/bin/bash
# virtuellerdesktop1: VLC + Chromium als root lauffaehig machen (Wiedereinspiel-Skript).
# Grund: VLC verweigert root ("VLC is not supposed to be run as root"). Der Container laeuft
# als root, deshalb wird der geteuid-Aufruf durch getppid (gleich lang, nie 0) ersetzt.
# Daniel hat das am 2026-09-30 ausdruecklich mit Risiko erlaubt. Geht bei Neuaufsetzen des
# Containers oder VLC-Update verloren -- dann dieses Skript erneut auf dem Host ausfuehren:
#   bash /root/werkraum/scripts/vd1_vlc_root_patch.sh
# Rueckgaengig: cp /usr/bin/vlc.orig-vor-root-patch /usr/bin/vlc (im Container)
set -e
C=virtuellerdesktop1

docker exec "$C" bash -c '
  set -e
  [ -x /usr/bin/vlc ] || { echo "FEHLER: /usr/bin/vlc fehlt im Container"; exit 1; }
  if ! grep -q geteuid /usr/bin/vlc; then
    echo "Nichts zu tun: kein geteuid mehr in /usr/bin/vlc (schon gepatcht oder andere Version)."
    exit 0
  fi
  cp --update=none /usr/bin/vlc /usr/bin/vlc.orig-vor-root-patch
  sed -i s/geteuid/getppid/ /usr/bin/vlc
  echo "VLC gepatcht."
  vlc --version 2>&1 | head -1
'

# --- Chromium (2026-09-30, Daniel: "erlaubnis mit risiko auch fuer chronium") ---
# wrapped-chromium haengt --no-sandbox nur an, wenn der Container Seccomp-Filter hat. Der
# Container laeuft mit seccomp=unconfined, also fehlte es und Chromium brach als root ab.
# Fix: bei root immer --no-sandbox. Rueckgaengig: cp wrapped-chromium.orig-vor-root-fix zurueck.
docker exec "$C" bash -c '
  set -e
  W=/usr/local/bin/wrapped-chromium
  [ -f "$W" ] || { echo "FEHLER: $W fehlt"; exit 1; }
  if grep -q "id -u" "$W"; then echo "Chromium: schon gepatcht."; exit 0; fi
  cp --update=none "$W" "$W.orig-vor-root-fix"
  sed -i "s/^if grep -q .Seccomp:.0. \/proc\/1\/status; then/if [ \"\$(id -u)\" != 0 ] \&\& grep -q \"Seccomp:.0\" \/proc\/1\/status; then/" "$W"
  grep -q "id -u" "$W" && echo "Chromium gepatcht." || { echo "FEHLER: Muster nicht gefunden, nichts geaendert"; exit 1; }
'

# --- Nachtrag 2026-09-30: die Desktop-Symbole starten /usr/bin/chromium und /usr/bin/google-chrome
# direkt, nicht wrapped-chromium. Daniel: "bitte auch chrome fix" (Risiko bekannt).
docker exec "$C" bash -c '
  set -e
  # /usr/bin/chromium: gleiche falsche Seccomp-Bedingung wie im Wrapper oben
  W=/usr/bin/chromium
  if [ -f "$W" ] && ! grep -q "id -u" "$W"; then
    cp --update=none "$W" "$W.orig-vor-root-fix"
    sed -i "s/^if grep -q .Seccomp:.0. \/proc\/1\/status; then/if [ \"\$(id -u)\" != 0 ] \&\& grep -q \"Seccomp:.0\" \/proc\/1\/status; then/" "$W"
    grep -q "id -u" "$W" && echo "/usr/bin/chromium gepatcht." || echo "FEHLER: Muster in $W nicht gefunden"
  else echo "/usr/bin/chromium: schon gepatcht."; fi
  # Google Chrome: --no-sandbox im letzten exec des Startskripts
  G=/opt/google/chrome/google-chrome
  if [ -f "$G" ] && ! grep -q -- "--no-sandbox" "$G"; then
    cp --update=none "$G" "$G.orig-vor-root-fix"
    sed -i "s|^exec -a \"\$0\" \"\$HERE/chrome\" \"\$@\"|exec -a \"\$0\" \"\$HERE/chrome\" --no-sandbox \"\$@\"|" "$G"
    grep -q -- "--no-sandbox" "$G" && echo "Chrome gepatcht." || echo "FEHLER: Muster in $G nicht gefunden"
  else echo "Chrome: schon gepatcht."; fi
'
