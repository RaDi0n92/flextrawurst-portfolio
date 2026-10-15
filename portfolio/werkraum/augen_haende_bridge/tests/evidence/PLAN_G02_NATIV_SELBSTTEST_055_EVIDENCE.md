# Nativer Selbsttest 0.5.5-g02 auf Daniels Windows (2026-10-01)

Ausgeführt über den dokumentierten SSH-Tunnel als geplante Aufgabe im interaktiven Benutzerkontext,
Paket in `C:\Bridge\test055` und `C:\Bridge\test055b` (die laufende Bridge in `C:\Bridge\neu` blieb unberührt).

Erster Lauf (test055): 10 ok, 1 Warnung, 1 Fehler, 1 unbekannt.

- Kamera nativ ok (Index 1 und 2 liefern 640x480, Index 0 fehlt), 6,4 s im eigenen Prozess.
- Mikrofon: alle fünf Eingabegeräte liefern digitale Stille (WO Mic, DroidCam Audio, Internes Mikrofon Conexant,
  Steam Streaming, Sound Mapper). Das ist kein Gerätewahlproblem mehr, sondern ein Befund an Daniels Rechner
  (Stummschaltung, Gerätepegel oder niemand spricht/kein Ton am Gerät) — offen, braucht Daniel.
- Durchklicken schlug einmal fehl: schon vor dem Test trafen die Klicks die Fenster, als wären Strg/Alt gedrückt.
  [status: offen] Ursache nicht bewiesen; wahrscheinlich Daniels eigene Tastatureingabe während des Laufs.
  Gegenmaßnahme: Prüfung wartet bis zu 3 s auf losgelassene Tasten und meldet sonst „unbekannt“ statt „Fehler“.
  Nach dem Nachbau (test055b) dreimal hintereinander ok.

Änderungen in 0.5.5: Kamera öffnet im Faden (Zustand „startet“, Abbrechen während des Öffnens getestet),
Selbsttest-Geräteprüfung mit 90-s-Timeouts und Zwischenständen, höchstens 8 Mikrofone, Kamera-Index 0 bis 3.
ZIP SHA256 `5f875fead4a97cf170bf1f216257b3db909590b47cb7305645f066bc2ae21fbd`.
Tests: 811 gesamt, nur die drei bekannten `test_terminal_adapter.py`-Fehlschläge.
