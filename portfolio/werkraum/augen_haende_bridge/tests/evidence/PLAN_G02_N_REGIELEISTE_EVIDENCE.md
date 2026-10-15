# PLAN-G02 Zyklus N: Regie- und Medienleiste — Evidence

Datum: 2026-09-30. Sicherheitspunkt: `1737e988ea` (Zyklus M).

## Build

- `koerper/regie_fenster.py`: kleines schwebendes Fenster unten links (kein Overlay, R118): Agentenname (Klick wechselt
  den Agenten), vier Kreisknöpfe Mik, Cam, Regie, STOP. Klick zählt erst beim Loslassen über demselben Knopf.
- `koerper/medien.py`: Kamera und Mikrofon je Agent, nur auf ausdrückliches Einschalten; Kamera liest im Takt
  (1 s) einen echten Frame in eigenem Faden; fehlendes Gerät bleibt sichtbar „fehler“ mit Grund; Not-Aus stoppt alles.
- `koerper/bild.py`: `bgr_zu_jpeg` für Kameraframes. `koerper/anwendung.py`: Auswahl des Agenten, Regiesprüche
  (14, R029) als getippter Gesprächswunsch über den bestehenden Eingabeweg (Not-Aus-Sperre gilt), Kamerabild als
  `frame` mit `terminal_id`, Beenden stoppt Medien.

## Ergebnis

Core: 471 Tests, grün bis auf die drei bekannten, umgebungsbedingten Fehlschläge in `test_terminal_adapter.py`.
Wine (`PLAN_G02_N_REGIELEISTE_WINE_OUTPUT.json`, Probe `probes/regie_smoketest.py`): Größe stimmt, topmost,
Toolwindow, nicht klickdurchlässig, Deckkraft 230; `WindowFromPoint` trifft jeden Knopf; echte Mausnachrichten lösen
genau den jeweiligen Rückruf aus; Runterdrücken/Loslassen auf verschiedenen Knöpfen löst nichts aus.

## UNKNOWN / offen

- **Mikrofon-Audio verlässt den Rechner nicht:** das Relay kennt keine Nachrichtenart dafür (Protokolländerung wäre
  eine Architekturentscheidung für Daniel). Erfasst und gezählt wird real (sounddevice), `Medien.audio_uebertragung`
  bleibt `False`.
- Kamera/Mikrofon mit echter Hardware: nicht getestet (Container ohne Geräte); cv2 unter Wine stürzt ab.
- Kamerabild geht mit `source: "capture"` (das Relay kennt nur capture/file/synthetic).
- Regie-Menü (Popup) unter Wine nicht ausgelöst; native Windows UNKNOWN.
- Harness: bewusst `running` vor `skill_prebuild_read` (keine eigene Skill-Lesung unmittelbar vor dem Bau).
