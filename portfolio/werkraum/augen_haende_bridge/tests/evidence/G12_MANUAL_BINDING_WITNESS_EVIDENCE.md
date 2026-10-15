# G12 — manueller nativer Binding-Witness

Datum: 2026-09-20
Scope: `/root/werkraum/augen_haende_bridge/client_windows/`
Status: `PARTIAL` — der Witness wartet jetzt auf Daniels echten Klick; ein
solcher Windows-Lauf wurde in dieser VPS-Umgebung noch nicht ausgeführt.

## Contract

- `-WaitForManualBinding` startet den bestehenden read-only Scan und pausiert
  danach sichtbar mit einer Handlungsanweisung.
- Daniel klickt selbst einen nativen Eintrag im Zielrail.
- Das Skript führt keinen Klick aus, sondern liest nur den
  `binding-readback`-Fenstermarker sowie Screenshot und JSON zurück.
- Ohne den Schalter bleibt der bisherige automatische Scanmarker-Test
  unverändert; es gibt keine implizite Auswahl.

## Evidence

- `G12-CONTRACT-01: PASS` — sechs statische Launcher-/Witness-Tests in
  `/root/werkraum/augen_haende_bridge/tests/test_ssh_tunnel_contract.py`.
- `G12-SAFETY-01: PASS` — kein `SendInput`, kein `PostMessage`, kein
  automatischer Mausklick und keine globale Prozessbeendigung.
- `G12-VALIDATOR-01: PASS` — vier read-only Tests prüfen die Witness-JSON,
  Marker, native Fensterwerte und eine explizit gelieferte PNG.
- `G12-NATIVE-RUN: UNKNOWN` — echter Windows-Lauf mit manuellem Klick fehlt.
- `G12-MANUAL-READBACK: UNKNOWN` — Screenshot/JSON mit
  `target_selection=manual_click` entstehen erst auf Daniels Windows.

## Windows command

```powershell
$env:BRIDGE_DESKTOP_TOKEN = '<gleiches Desktop-Token wie auf dem VPS>'
& .\native_acceptance_witness.ps1 -VpsHost '<VPS-DNS-oder-IP>' -VpsUser 'root' -WaitForManualBinding
```

Nach der Scanmeldung im Zielrail selbst einen nativen Eintrag anklicken. Der
Witness beendet sich nach erfolgreicher Rücklese und schreibt JSON plus PNG.

## Handoff archive

- `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge-G12-win64-handoff.zip`
- SHA256: `f7c6e42695af367261703bd01a62aa7d908af85781059a3f5d882850b89c047a`
- Enthält das vollständige EXE-`onedir`-Bundle, Launcher, Witness und
  Anleitung.
