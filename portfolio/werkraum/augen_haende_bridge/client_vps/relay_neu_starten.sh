#!/bin/bash
# Startet den Bridge-Relay neu, damit er neuen Code und neue Zugangsdaten lädt. Ein Befehl statt drei.
# Aufruf auf dem Host:  bash /root/werkraum/augen_haende_bridge/client_vps/relay_neu_starten.sh
set -u
echo "1/3 Dienstdateien neu einlesen ..."
systemctl daemon-reload || { echo "FEHLER: daemon-reload ging nicht. Bitte als root ausführen."; exit 1; }
echo "2/3 Relay neu starten ..."
systemctl restart bridge-relay || { echo "FEHLER: bridge-relay ließ sich nicht neu starten."; exit 1; }
sleep 2
echo "3/3 Prüfen ..."
if [ "$(systemctl is-active bridge-relay)" = "active" ]; then
  echo "FERTIG: Der Relay läuft."
else
  echo "FEHLER: Der Relay läuft nicht. Details: journalctl -u bridge-relay -n 30"
  exit 1
fi
