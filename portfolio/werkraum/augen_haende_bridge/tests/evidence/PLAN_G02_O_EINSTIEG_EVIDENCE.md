# PLAN-G02 Zyklus O: Einstiegspunkt der exe und Körper-Tor — Evidence

Datum: 2026-09-30. Sicherheitspunkt: `0300d4bc4c` (Zyklus N).

## Build

- `koerper/haupt.py`: setzt Anwendung, Not-Aus-Hook (F12), Medien, `KoerperAnwendung`, Regieleiste zusammen und läuft,
  bis die Bridge beendet wird. `BRIDGE_URL`/`BRIDGE_TOKEN` aus der Umgebung; ohne sie sichtbar offline. Fehler und
  jede Zustandsänderung gehen nach `%LOCALAPPDATA%\AugenUndHaendeBridge\bridge.log`; bei Abbruch ein Meldungsfenster.
  `--version` gibt die Version aus. Prüfhaken nur über ausdrückliche Umgebungsvariablen (`BRIDGE_TEST_*`).
- `client_windows/koerper_app.py`: dünner Einstieg für PyInstaller.
- Regieleiste steht schon vor dem ersten Agenten; ihr Menü hat die Regiesprüche (nur bei laufender Sitzung), die
  Startliste (BE02, nur verbunden und ohne Not-Aus) und „Bridge beenden“. Wieder aufgenommene, bereits laufende
  Sitzungen zeigen „läuft“.
- `tests/pruefe_koerper.py` prüft jetzt das Paket `koerper/` statt des alten `overlay_app.py`: 0 von 4 beanstandeten
  Dingen. Die Muster blieben unverändert; die Beschriftungen in `medien.py` wurden umformuliert, weil V04 auf die
  Textstellen „Kamera: “/„Mikrofon: “ anschlägt (dahinter hängt echte Aufnahme).

## Ergebnis

Core: 476 Tests, grün bis auf die drei bekannten, umgebungsbedingten Fehlschläge in `test_terminal_adapter.py`.
Wine, aus dem Quellstand (`PLAN_G02_O_EINSTIEG_WINE_OUTPUT.json`): Programm startet ohne Verbindungsdaten sichtbar
offline; mit echtem Relay (`client_vps/bridge_server.py`, Starter mit PTY, `cat`) verbindet es, holt die Startliste,
startet über die start_id eine echte Sitzung, tippt „hallo welt“ und die Rückgabe steht im Terminalpuffer; F12-Hook
installiert.

## UNKNOWN / offen

- Native Windows UNKNOWN. Die gebaute exe (PyInstaller) ist in diesem Zyklus noch nicht getestet.
- „Bridge beenden“ lässt die VPS-Sitzungen laufen (Neuverbinden nimmt sie wieder auf, im Lauf gesehen); Scrollback wird
  bei der Wiederaufnahme nicht nachgeliefert. Ob Beenden die Sitzungen schließen soll, ist Daniels Entscheidung.
- Harness: bewusst `running` vor `skill_prebuild_read`.
