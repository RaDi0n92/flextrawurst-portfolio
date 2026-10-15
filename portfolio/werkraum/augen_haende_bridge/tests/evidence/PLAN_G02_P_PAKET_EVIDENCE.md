# PLAN-G02 Zyklus P: PyInstaller-onedir-Paket, Übergabe — Evidence

Datum: 2026-09-30. Sicherheitspunkt: `7b44156fa8` (Zyklus O).

## Lieferung

`/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge-G02-win64.zip` (74 MB, `--onedir`, unsigniert)
SHA256 des ZIP: `8b31455a03d054f34e2254f643ec70d0df4644eb92c54215de1a1c652e0b0c7a`
(auch in `AugenUndHaendeBridge-G02-win64.zip.sha256`). SHA256 der exe:
`771c94f62bddf8cb371e824ea04275e43255a701b5cf0378a3900f0ce38171a3`. Im ZIP: `AugenUndHaendeBridge/` (exe und
`_internal`), `client_windows/start_with_ssh_tunnel.ps1`, `START_ANLEITUNG.txt`, `VERSION.txt`, `PAKET_SHA256.txt`
(1449 Dateien; nach dem Entpacken alle Prüfsummen bestätigt). Versionsinfo in der exe: 0.2.0-g02, PE32+ x64, GUI-Subsystem
(per pefile gelesen). Build: `AugenUndHaendeBridgeKoerper.spec`, nativ reproduzierbar mit
`client_windows/build_exe_koerper.bat` (feste Versionen).

## Wine-Nachweise (Windows-Python nur zum Bauen, der Lauf ist die gebaute exe)

- exe aus dem Build-Ordner und aus dem entpackten ZIP: ohne Verbindungsdaten sichtbar offline (F12-Hook installiert);
  mit echtem Relay verbunden, Startliste, echte Sitzung gestartet, „hallo aus der exe“ getippt und aus dem PTY zurückgelesen.
  Ausgaben: `PLAN_G02_P_PAKET_EXE_WINE_OUTPUT.json`, `PLAN_G02_P_PAKET_ZIP_WINE_OUTPUT.json`.
- Playwright zuletzt (`tests/transport_playwright_proof.py`, Playwright 1.63 im Scratch-venv): PASS
  (`PLAN_G02_P_PLAYWRIGHT_OUTPUT.json`). Das ist ein lokaler Transportbeleg mit dem Browser als Testteilnehmer; Playwright
  kann die Windows-Oberfläche nicht bedienen und ist kein Nativbeweis.
- Core-Tests: 476, drei bekannte, umgebungsbedingte Fehlschläge; Körper-Tor `pruefe_koerper.py`: 0 von 4.

## Umweg beim Bau (ehrlich)

Unter dieser Wine-Version bricht `import numpy` ab (`ucrtbase.crealf` fehlt), und PyInstaller importiert numpy schon
beim Entdecken der Hook-Verzeichnisse. Deshalb wurden numpy 2.2.6 und opencv-python-headless 4.11.0.86 aus dem
Build-Python entfernt und **unverändert als Dateien** (`datas`) ins Bundle gelegt, nicht analysiert. Ob `import cv2`
aus dem Bundle auf echtem Windows funktioniert, ist **UNKNOWN**; der native Build mit `build_exe_koerper.bat` nutzt den
normalen Weg. Unter Wine würde ein Klick auf „Cam“ den Prozess abbrechen (dieselbe fehlende Funktion) — dort nicht getestet.

## UNKNOWN / offen (Übergabe)

- **Native Windows: UNKNOWN** — Fenster, DPI, Mehrmonitor, echte Tastatur/F12, Layered/klickdurchlässige Raute,
  SmartScreen, Kamera, Mikrofon, Scanner gegen echte Fremdfenster. Daniel muss die exe dort starten; das ist eine offene Übergabe.
- Mikrofon-Audio ohne Relay-Nachrichtenart; „Bridge beenden“ schließt VPS-Sitzungen nicht; eigene Bridge-Fenster stehen
  im Scanner-Inventar; Terminal-Geometrie unter Wine (23,79).
- Harness: bewusst `running` vor `skill_prebuild_read`.
