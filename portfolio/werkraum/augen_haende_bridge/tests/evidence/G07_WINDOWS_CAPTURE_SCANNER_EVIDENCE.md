---
stage: G07
date: 2026-09-20
author: codex bei Daniels VPS
scope: windows-gdi-capture-and-win32-window-inventory
---

# G07 — Windows-GDI-Frame und Win32-Fensterscanner unter Wine

EVIDENCE_VERSION: 1

## FocusContract

- Ziel: Ein aktueller virtueller Desktop-Frame wird read-only aufgenommen,
  gehasht und mit einem Win32-Fensterinventar gekoppelt.
- Erhaltungsanker: Frame und strukturierter Scan bleiben getrennte Zeugen;
  der Scanner behauptet nur `inventory`; kein Binding, keine Eingabe, kein
  Remote-Inspect und keine öffentliche Verbindung.
- Nicht Teil dieses Steins: echter Windows-Host, virtuelle Windows-Desktops,
  DPI-/Fokusabnahme, UI-Automation oder Input.

## Implementierung

- Capture:
  `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/windows_capture.py`.
- Scanner:
  `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/windows_scanner.py`.
- GUI:
  `/root/werkraum/augen_haende_bridge/client_windows/overlay_app.py`.
- Paket:
  `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge/AugenUndHaendeBridge.exe`.
- EXE-SHA256:
  `68f55707dedf08ace0cf9de515015df25918996c88fbb236d842a7bad0e0418d`.

## Belegkette

- CORE-07: PASS — 99 Unittests; Fake-Capture prüft exakte Dimensionen,
  Frame-Hash und Referenzbildung; Linux-Default bleibt fail-closed
  `unavailable`.
- FRAME-07: PASS — der gebündelte Windows-Prozess erzeugt unter Wine einen
  virtuellen Desktop-Frame mit Dimensionen, Zeitstempel und SHA256.
- INVENTORY-07: PASS — derselbe Lauf liefert `windows:desktop` plus sichtbare
  Top-Level-Fenster aus Win32-EnumWindows; der Scan erhält den frischen
  `frame_ref`/`frame_hash`.
- RENDER-07: PASS — externes `xwininfo` liest
  `Augen & Hände Bridge · scan-received:2` zurück.
- PW-07: PASS — der browserbedienbare Transport-/Inventory-Witness und die
  Referenzregression liefen nach dem Paket-Rebuild durch.
- NATIVE-WINDOWS-07: UNKNOWN — Wine ersetzt Daniels echten Windows-Desktop
  nicht und beweist keine native Win32-Abnahme.

## Ergebnis

OUTCOME: PARTIAL

Der neue Augenpfad ist im gebündelten Programm real ausführbar und koppelt
Frame-/Inventarzeugen korrekt. Native Windows bleibt offen; aus diesem Lauf
wird keine Fähigkeit zu Binding, UI-Automation oder Input abgeleitet.
