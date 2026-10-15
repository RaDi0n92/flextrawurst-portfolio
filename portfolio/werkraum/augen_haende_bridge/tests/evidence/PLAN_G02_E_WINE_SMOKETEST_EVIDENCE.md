# PLAN-G02 Zyklus E: Wine-Smoketest für Raute und Terminal — Evidence

Datum: 2026-09-25, direkte Fortsetzung von Zyklus D in derselben Sitzung.

## Ausgangslage: das wine-Paket fehlte

Der Wine-Baubereich aus G01 (`/config/wine-bridge-build/prefix`, Windows-Python 3.13.5, PyInstaller 6.14.2) lag
nach dem VD1-Absturz unverändert auf der Platte, aber `apt-cache policy wine` zeigte `Installed: (none)` — das
Systempaket selbst fehlte. Auf Daniels ausdrücklichen Auftrag („mach du das", die parallel geöffnete zweite Session
ist für etwas ganz anderes) mit `apt-get install wine` (Ubuntu-Paket, Version 10.0) neu installiert. Der bestehende
Prefix funktionierte sofort wieder (`wine 'C:\Python313\python.exe' --version` → `Python 3.13.5`).

`pip list` im Wine-Python zeigte bereits `opencv-python-headless`, `pyte`, `pyinstaller`, `websockets` (Reste aus
der früheren, mit BE03 verworfenen Codex-Bauzählung); `sounddevice` fehlte und wurde ergänzt.

## Warum kein Pixel-Screenshot

`probes/window_probe.py` (G01) ist schon einmal von Bildschirmaufnahmen auf reine `WindowFromPoint`-Trefferprüfung
umgestiegen, weil Xvfb ohne Compositor Layered- und geformte Fenster als bildschirmgroße, nicht wirklich
transparente/geformte X-Fenster darstellt — ein Screenshot davon wäre irreführend. Dieser Zyklus übernimmt dieselbe
Methode statt sie neu zu erfinden.

## Build-Schritt

`probes/koerper_smoketest.py` (neu): baut ein echtes `RauteFenster` und ein echtes `TerminalFenster` aus den in
Zyklus B/C gebauten `koerper/*.py`-Modulen unter Wine und liest zurück:

- `GetWindowRect`, `GetLayeredWindowAttributes`, `GetWindowRgnBox`, `WindowFromPoint` an fünf Punkten (Mitte und
  vier Quadratecken der Raute).

Zweimal ausgeführt, beide Male identisch (Rohausgabe in `PLAN_G02_E_WINE_SMOKETEST_OUTPUT.json`):

### Raute — PASS

- Fenster genau 48×48 Pixel an der angeforderten Position (`rect`: `[200, 200, 248, 248]`).
- Deckkraft-Alpha zurückgelesen: **87** — exakt `stil.deckkraft_alpha(34)`, also die in R031 geforderten 34 %
  Deckkraft / 66 % Transparenz.
- Fensterregion wirklich gesetzt (`region_gesetzt: true`); `WindowFromPoint` trifft an der Mitte die Raute, an
  allen vier Ecken des umschließenden Quadrats **nicht** — die Diamantform ist echt, kein nur gezeichnetes Viereck.
- Die Kürzel-Schrift wurde real über `CreateFontW`/`GetTextMetricsW` aufgebaut (`kuerzel_schrift_aufgebaut: true`).

### Terminal — PASS mit einer offenen Abweichung

- Reale Schriftauflösung: `Cascadia Mono`/`Consolas`/`Courier New` fehlen in diesem nackten Wine-Prefix, der
  Fallback in `_wahl_schrift()` griff korrekt und lieferte `Liberation Mono`; `Tahoma` (eine der bevorzugten
  Oberflächenschriften) traf direkt.
- Eingespeister Text (`ausgabe(b"hallo koerper\r\n")`) erscheint tatsächlich im Terminalmodell.
- **Abweichung:** `zeilen_spalten()` liefert nach echter Fenstererzeugung `(23, 79)` statt der angeforderten
  `(24, 80)`. Die Fenstergröße selbst stimmt exakt mit der Berechnung aus den echten Zellmaßen (`zell_b=10`,
  `zell_h=18`) überein; der Unterschied entsteht vermutlich, weil `GetClientRect` unter dieser
  Wine/Xvfb/openbox-Kombination nicht exakt der bei `CreateWindowExW` angeforderten Größe entspricht (ein
  Pixel-Unterschied reicht bei der Ganzzahldivision für eine Zeile/Spalte weniger). **Nicht korrigiert** — ob das
  ein Wine/openbox-Artefakt oder auch unter echtem Windows sichtbar ist, ist offen und wird nicht geraten.

## Was UNKNOWN bleibt

- Ein Wine-Lauf ist keine native Windows-Abnahme (siehe G01/G02: „Ein Wine-Test allein ist nicht Daniels native
  Windows-Abnahme"). Die obigen Ergebnisse gelten für dieses Wine 10.0 unter Xvfb/openbox, nicht für Daniels
  tatsächlichen Windows-Rechner.
- `cv2` stürzt zusammen mit `numpy 2.5.3` unter dieser Wine-Version beim Import ab
  (`wine: Call from ... to unimplemented function ucrtbase.dll.crealf, aborting`, startet automatisch `winedbg`
  und hängt, bis der Prozess hart beendet wird). `kamera.py` konnte deshalb in diesem Zyklus **nicht** unter Wine
  mitgeprüft werden — nur die Fake-Quelle-Tests aus Zyklus D und der reale cv2-Lauf direkt unter Linux (ohne Wine)
  gelten bisher. Ob ein Downgrade von `numpy`/`opencv-python-headless` das behebt, ist offen und nicht versucht.
- Das Terminal-Geometrie-Delta oben.
- Echte Aufnahme/Wiedergabe von Bild/Ton bleibt wie in Zyklus D UNKNOWN.

## Testergebnis (unverändert von Zyklus D)

```
PYTHONPATH=src:. python3 -m unittest discover -s tests -q
Ran 321 tests, FAILED (failures=2, errors=1) — dieselben drei vorbestehenden, umgebungsbedingten Fehlschläge.
```

Dieser Zyklus fügt keine neuen Unit-Tests hinzu (der Smoketest läuft nur unter Wine und ist keine
`unittest`-Testdatei); er hebt zwei bereits bestehende, zuvor rein logisch getestete Bausteine auf reale
native Evidence.

## Was als Nächstes offen ist

Wie in Zyklus C/D benannt: Banner/Ticker/Chat-Fensterarchitektur mit Daniel klären. Zusätzlich aus diesem Zyklus:
das Terminal-Geometrie-Delta untersuchen, cv2/numpy-Kompatibilität mit dieser Wine-Version klären, dann
Fensterscanner-Anbindung, PyInstaller-Paket, echter Wine-Start des ganzen ersten Körpers zusammen.
