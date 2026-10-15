---
stage: G05
date: 2026-09-20
author: codex bei Daniels VPS
scope: windows-exe-package-and-wine-smoke
---

# G05 — Windows-EXE-Paket und isolierter Start-Smoke

EVIDENCE_VERSION: 1

## FocusContract

- Ziel: Aus dem aktuellen Greenfield-Einstieg ein vollständiges Windows-
  `--onedir`-Paket mit Tcl/Tk erzeugen und den Start des gebündelten
  Programms isoliert prüfen.
- Erhaltungsanker: der bestehende Codepfad bleibt unverändert; kein alter
  Prototyp, keine alte Proof-Surface und kein öffentlicher Relay-Endpunkt.
- Nicht Teil dieses Steins: native Abnahme auf Daniels Windows, Win32-Capture,
  Fensterscanner-Livebeweis, Fokus-/DPI-Beweis, Terminaleingabe oder Remote-
  VPS-Tunnel.

## Build

- Buildumgebung: isolierter Wine-Prefix unter `/tmp/augen-haende-winbuild.ieRV30/`.
- Windows-Python: 3.13.5, vollständiger Installer mit Tk 8.6.
- PyInstaller: 6.14.2.
- websockets: 16.1.1.
- PyInstaller-Modus: `--onedir --windowed`.
- Produktpfad:
  `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge/`.
- EXE:
  `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge/AugenUndHaendeBridge.exe`.
- SHA256:
  `573f58992eb859c347d50965edb9f605f7b4dab9367ebbcf579e5edd6e7c8e0f`.

## Belege

- PACKAGE-05: PASS — `file` meldet ein x86-64-PE32+-GUI-Programm für
  Microsoft Windows.
- TK-05: PASS — das Bundle enthält `tcl86t.dll`, `tk86t.dll`,
  `_tkinter.pyd`, `_tcl_data` und `_tk_data`.
- WINE-05: PASS — die EXE lief unter Wine acht Sekunden ohne vorzeitigen
  Prozessabbruch; `xwininfo` las das Fenster `Augen & Hände Bridge` mit
  `1180x680+138+60` zurück.
- CORE-05: PASS — `PYTHONPATH=src:. python3 -m unittest discover -s tests -q`
  meldete 97 Tests OK.
- PW-05-01: PASS —
  `PYTHONPATH=src:. python3 tests/transport_playwright_proof.py` lief mit
  einem echten Chromium-Testpeer und produktivem Inventory-Provider durch.
- PW-05-02: PASS —
  `PYTHONPATH=src:. python3 tests/reference_surface_proof.py` lief mit
  Exit-Code 0 durch.
- NATIVE-WINDOWS-05: UNKNOWN — Wine liefert keinen Beleg für den nativen
  Windows-Desktop, Win32-Capture oder Daniels tatsächliche Fensterwelt.
- REMOTE-VPS-05: NOT_CLAIMED — der aktuelle Transport bleibt Loopback-only.

## Ergebnis

OUTCOME: PARTIAL

Das EXE-Bundle ist real gebaut, vollständig und startet im isolierten Smoke.
Der nächste noch offene Plattformbeleg ist der Start auf echtem Windows mit
anschließender nativer Ziel-/Fensterrücklese. Aus diesem Paket-Smoke wird kein
Windows-Native-PASS abgeleitet.
