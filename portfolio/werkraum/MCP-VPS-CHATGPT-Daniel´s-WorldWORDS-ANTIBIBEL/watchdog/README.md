
# Lokaler ANTIBIBEL-Watchdog

## Status

`AVAILABLE_NOT_INSTALLED`

Der Watchdog ist als Polling-Körper vorgesehen. Er soll Änderungen an Primärquellen erkennen und anschließend `tools/rebuild_all.py` ausführen. Er wird in dieser Gründungsrunde **nicht** als systemd-Dienst installiert.

## Warum Polling?

Der Hauptprojekt-Watchdog stieß zeitweise an das globale Inotify-Instanzlimit. Seine spätere Polling-Variante zeigte, dass ein robuster Fallback nötig ist. Die ANTIBIBEL beginnt deshalb ohne neue Inotify-Instanzen.

## Geschützte Trennung

Beobachtet werden Primärbereiche wie `01_HERKUNFT/`, `02_WORTKOERPER/`, `03_KONZEPTE/`, `04_PROPAGANDA/`, `05_SAMMELBECKEN/`, `06_GESPRAECHE/`, `08_MUTATIONEN/`, `09_QUELLEN/`, `sessions/` und `coordination/`.

Ignoriert werden generierte Ansichten wie `Verweise/`, `Zeitstrom/`, `MOC/`, `truth_engine/runtime/`, `truth_engine/generations/`, `validation/` und Root-Ausgaben. Dadurch soll der Watchdog nicht seine eigenen Ergebnisse endlos erneut triggern.

## Manuell

- einmaliger Neuaufbau: `python3 tools/rebuild_all.py`
- Watchdog-Selbsttest: `python3 watchdog/watchdog_service.py --self-test`
- foreground polling: `python3 watchdog/watchdog_service.py`
