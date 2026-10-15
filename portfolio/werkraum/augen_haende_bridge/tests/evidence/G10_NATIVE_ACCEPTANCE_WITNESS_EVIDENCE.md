# G10 — nativer Windows-Acceptance-Witness

Datum: 2026-09-20
Scope: `/root/werkraum/augen_haende_bridge/client_windows/`
Status: `PARTIAL` — der Windows-seitige Witness ist gebaut und statisch
geprüft; er wurde in dieser VPS-Umgebung noch nicht auf Daniels Windows
ausgeführt.

## Contract

- `/root/werkraum/augen_haende_bridge/client_windows/native_acceptance_witness.ps1`
  startet den vorhandenen SSH-Launcher mit dem expliziten
  `BRIDGE_NATIVE_SCAN_ON_START=1`-Testschalter.
- Der Witness liest den EXE-Fenstertitel, HWND, Sichtbarkeit und Rechteck
  über `user32.dll` zurück.
- Er speichert einen nativen Bildschirm-Screenshot sowie eine JSON-Evidence
  mit `input_exercised: false`.
- Er benutzt keinen zweiten Tunnel und übergibt das Desktop-Token nicht als
  Prozessargument; es kommt aus der Umgebungsvariablen.
- Er umgeht keine PowerShell-Execution-Policy; ein blockierter Scriptstart
  bleibt ein sichtbarer Setupfehler.
- Die Aufzeichnung endet nach dem Scanmarker und schließt nur den eigenen
  Bridge-/Launcher-Prozess.

## Evidence

- `G10-CONTRACT-01: PASS` — fünf statische Launcher-/Witness-Tests in
  `/root/werkraum/augen_haende_bridge/tests/test_ssh_tunnel_contract.py`.
- `G10-CONTRACT-02: PASS` — `GetWindowText`, `GetWindowRect`,
  `Save-NativeScreenEvidence` und JSON-Ausgabe sind im Witness vorhanden.
- `G10-SAFETY-01: PASS` — kein `SendInput`, kein `PostMessage`, kein
  `Stop-Process -Name ssh`.
- `G10-NATIVE-RUN: UNKNOWN` — kein Windows-Host in dieser Umgebung.
- `G10-NATIVE-SCREENSHOT: UNKNOWN` — Screenshot und JSON entstehen erst beim
  Lauf auf Daniels Windows.
- `G10-BINDING: NOT_EXERCISED` — der Witness prüft zunächst den nativen
  Erstkontakt/Scanmarker; die eigentliche Zielauswahl und G09-Rücklese folgen
  als separater Schritt.

## Windows command

```powershell
$env:BRIDGE_DESKTOP_TOKEN = '<gleiches Desktop-Token wie auf dem VPS>'
& .\native_acceptance_witness.ps1 -VpsHost '<VPS-DNS-oder-IP>' -VpsUser 'root'
```

Der Token-Platzhalter ist Dokumentation und darf nicht durch einen echten
Token in Git oder einer Evidence-Datei ersetzt werden.

## Handoff archive

- `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge-G10-win64-handoff.zip`
- SHA256: `4730f1ec4786090d5fa70ea01c0cccdb94bcffa81b494816ff42d9e96a35c129`
- Enthält das vollständige `AugenUndHaendeBridge/`-Bundle inklusive
  `_internal` sowie Launcher, Witness und Anleitung.
