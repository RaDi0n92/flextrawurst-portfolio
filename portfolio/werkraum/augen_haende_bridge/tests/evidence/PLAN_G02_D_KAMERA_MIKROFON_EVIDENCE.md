# PLAN-G02 Zyklus D: Kamera und Mikrofon — Evidence

Datum: 2026-09-24/25, direkte Fortsetzung von Zyklus C in derselben Sitzung (Backup-Commit vor diesem Zyklus:
`970ebda591`).

## Warum Kamera/Mikrofon jetzt, aber nur die "erste Fassung"

`PLAN.md` zählt Kamera und Mikrofon zum ersten Körper (G02/BE03); die volle Fassung mit Pro-Agent-Routing,
Push-to-talk **und** VAD, PiP-Layout und Aufnahme-Replay ist G07 und bleibt „G02 enthält die erste Fassung“
(Zeile 370). Anders als bei der Raute (Banner/Ticker/Chat) gibt es hier keine offene Architekturfrage zwischen
mehreren mit Daniel abzustimmenden Fensterlösungen — nur den Umfang, den G02 gegenüber G07 bewusst kleiner hält.
Deshalb wurde hier direkt gebaut statt erst rückgefragt.

`pruefe_koerper.py` (V04-MEDIEN-ATTRAPPE) verbietet ausdrücklich, Kamera/Mikrofon als bloße Ein/Aus-Booleans
nachzubauen — das war die Leitplanke für den Zuschnitt.

## Build-Schritt

- `src/augen_haende_bridge/koerper/kamera.py` (neu): `Kamera` mit injizierbarem `KameraQuelle`-Backend.
  `Cv2KameraQuelle` importiert `cv2` erst bei `oeffnen()`, nicht beim Modulimport. `frame_lesen()` liefert echte
  `KameraFrame`-Objekte mit fortlaufender Sequenz, Aufnahmezeit und Herkunft (`cv2:<index>`), kein Boolean.
- `src/augen_haende_bridge/koerper/mikrofon.py` (neu): `Mikrofon` mit injizierbarem `MikrofonQuelle`-Backend.
  `SounddeviceMikrofonQuelle` importiert `sounddevice` erst bei `oeffnen()`. Push-to-talk (Standardmodus) und ein
  offener Modus, Stummschaltung, echte `AudioBlock`-Objekte (Sequenz, Aufnahmezeit, Abtastrate, Kanäle, Herkunft).
- `pyproject.toml`: zwei Extras ergänzt — `terminal = ["pyte==0.8.2"]` (macht eine bereits bestehende, bisher
  undeklarierte Abhängigkeit von `terminal_modell.py` sichtbar; kein neues Verhalten) und
  `medien = ["opencv-python-headless", "sounddevice"]`.
- `tests/test_koerper_kamera.py`, `tests/test_koerper_mikrofon.py` (neu, 22 Tests): Zustandslogik über eine
  Fake-Quelle (Einschalten/Ausschalten, Sequenzierung, Fehlerpfade, Idempotenz, Push-to-talk/Stumm/offen-Modus),
  dazu je ein Test mit dem **echten** Backend gegen diesen Container.

## Echte Geräteproben in diesem Container

```
>>> import cv2; cv2.VideoCapture(0).isOpened()
[ WARN ...] can't open camera by index
False
>>> import sounddevice
OSError: PortAudio library not found
```

Beide Fehlschläge sind real (keine Kamera-Hardware, keine native PortAudio-Bibliothek in diesem Container) und
wurden nicht umgangen (kein `apt-get install libportaudio2`, keine Kamera angeschlossen) — sie sind Teil der
Evidence: `Cv2KameraQuelleTests.test_fehlende_kamera_hardware_wird_zu_einem_benannten_fehlschlag_statt_einer_ausnahme`
und `SounddeviceMikrofonQuelleTests.test_fehlende_portaudio_bibliothek_wird_zu_einem_benannten_fehlschlag` prüfen,
dass beide Fälle als `KameraFehler`/`MikrofonFehler` mit gesetztem `letzter_fehler` ankommen statt als unbehandelte
Ausnahme durchzuschlagen.

## Testergebnis

```
PYTHONPATH=src:. python3 -m unittest discover -s tests -q
Ran 321 tests (Ausgangsstand 299 nach Zyklus C)
FAILED (failures=2, errors=1)
```

Dieselben drei vorbestehenden, umgebungsbedingten Fehlschläge in `test_terminal_adapter.py` wie in den Zyklen B/C,
unverändert, kein Bezug zu Kamera/Mikrofon.

`python3 tests/pruefe_koerper.py` — PASS (0 von 4 beanstandeten Dingen), einschließlich V04
(Medien-Attrappe): weiterhin geprüft gegen den alten `client_windows/overlay_app.py`, nicht gegen `koerper/`.

## Was UNKNOWN bleibt

- Echte Aufnahme mit tatsächlicher Kamera-/Mikrofon-Hardware — hier gibt es keine; das bleibt Daniels native
  Abnahme auf Windows.
- PyInstaller-Bundling von `cv2`/`sounddevice` inklusive der nativen PortAudio-DLL für Windows — noch nicht
  versucht (kommt mit dem Paketierungsschritt).
- Pro-Agent-Routing, echtes VAD und Aufnahme-Replay — ausdrücklich G07, nicht Teil dieses Zyklus.
- Weiterleitung der Frames/Audioblöcke an das Relay/die Bridge-Runtime — hier nur als Callback-Anschlussstelle
  vorbereitet (`block_empfangen`, `frame_lesen()`), noch nicht verdrahtet.

## Was als Nächstes offen ist

Wie in Zyklus C benannt: Banner/Ticker/Chat-Fensterarchitektur mit Daniel klären. Unabhängig davon: Fensterscanner
ans Terminalfenster anschließen, PyInstaller-Paket bauen, einen echten Wine-Start des ersten Körpers versuchen.
