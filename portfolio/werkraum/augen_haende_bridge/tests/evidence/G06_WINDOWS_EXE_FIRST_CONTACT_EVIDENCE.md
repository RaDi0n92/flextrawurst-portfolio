---
stage: G06
date: 2026-09-20
author: codex bei Daniels VPS
scope: packaged-windows-exe-first-contact
---

# G06 — Gebündelter Windows-Erstkontakt unter Wine

EVIDENCE_VERSION: 1

## FocusContract

- Ziel: Der reale gebündelte Windows-Prozess verbindet sich mit dem lokalen
  Relay, verarbeitet den read-only Inventar-Rundlauf und rendert eine echte
  empfangene Nachricht sichtbar.
- Erhaltungsanker: Produktpfad bleibt der aktuelle `--onedir`-Stand; Relay
  bleibt loopback-only; keine Shell-, Terminal- oder Delete-Aktion.
- Nicht Teil dieses Steins: native Windows-Abnahme, öffentlicher VPS-Tunnel,
  Win32-Capture, echte Windows-Fensterliste, DPI/Fokus oder Eingabe.

## Ausgeführter Lauf

- Runner:
  `/root/werkraum/augen_haende_bridge/tests/windows_exe_wine_first_contact.py`.
- EXE:
  `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge/AugenUndHaendeBridge.exe`.
- SHA256:
  `e011b27ecb6500cd00ec9274f92f5eb2a3a790284e15a54244a7656c7a6dcca9`.
- Umgebung: isolierter Wine-Prefix, `DISPLAY=:1`, lokaler Relay auf
  `127.0.0.1`.

## Belegkette

- PACKAGE-06: PASS — die gebündelte Datei ist ein x86-64-PE32+-GUI-
  Programm und enthält den Tkinter/Tcl/Tk-Bestand.
- CONNECT-06: PASS — der gestartete EXE-Prozess authentifiziert sich beim
  Relay als `desktop`.
- INVENTORY-06: PASS — die EXE fordert `target_inventory_request` an; ein
  Relay-Agent liefert ein validiertes read-only Zielinventar; die EXE bestätigt
  den Empfang.
- SAY-06: PASS — der Agent sendet `G06 packaged first contact`; der Relay
  liefert das Ereignis an die gebündelte EXE; das Journal attestiert die
  empfangene Quittung.
- RENDER-06: PASS — `xwininfo` liest das sichtbare Fenster
  `Augen & Hände Bridge · say-received` zurück.
- CORE-06: PASS — die vorherige vollständige Suite meldete 97 Tests OK.
- PW-06: PASS — der Chromium-Transport-/Inventory-Proof lief nach dem
  Rebuild erneut durch; er bleibt ein Browser-/Relay-Beleg.
- NATIVE-WINDOWS-06: UNKNOWN — Wine ist kein Beleg für Daniels echtes
  Windows und keine native Win32-Fensterwelt.

## Ergebnis

OUTCOME: PARTIAL

Der aktuelle EXE-Prozess ist nicht mehr nur ein startendes Paket: Er nimmt
einen echten lokalen Relay-Rundlauf an und zeigt die empfangene Nachricht
sichtbar. Die native Windows-Grenze bleibt bewusst offen.
