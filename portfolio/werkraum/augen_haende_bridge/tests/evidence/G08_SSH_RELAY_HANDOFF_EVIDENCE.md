# G08 — aktueller VPS-Relay und SSH-LocalForward-Hand-off

Datum: 2026-09-20
Scope: `/root/werkraum/augen_haende_bridge/`
Status: `PARTIAL` — der aktuelle Relay-/Agent-Pfad ist lokal bewiesen; ein
echter Windows-Rechner und ein realer SSH-Login von Daniels Windows waren in
diesem Lauf nicht verfügbar.

## Contract

- Der aktuelle Einstieg ist
  `/root/werkraum/augen_haende_bridge/client_vps/bridge_server.py`.
- Der Standardport ist `19880`, Bindung ausschließlich `127.0.0.1`.
- `BRIDGE_DESKTOP_TOKEN` und `BRIDGE_AGENT_TOKEN` sind getrennt, mindestens
  32 Zeichen lang und werden nicht ausgegeben.
- Der alte historische Port `9880` wird von G08 nicht verwendet.
- Der Windows-Launcher liegt unter
  `/root/werkraum/augen_haende_bridge/client_windows/start_with_ssh_tunnel.ps1`.
  Beide Tunnelenden bleiben Loopback; Host-Key-Prüfung wird nicht abgeschaltet.

## Evidence

- `G08-CORE-01: PASS` — `test_bridge_server.py`, fünf Contract-Tests.
- `G08-CORE-02: PASS` — `test_ssh_tunnel_contract.py`, drei PowerShell-
  Vertragsprüfungen.
- `G08-LIVE-01: PASS` —
  `/root/werkraum/augen_haende_bridge/tests/bridge_server_smoke.py` startete
  den aktuellen Entry-Point auf einem ephemeren Loopback-Port.
- `G08-LIVE-02: PASS` — der eingebaute VPS-Inventory-Agent verband sich über
  den aktuellen Relay; ein Desktop-Client empfing und bestätigte
  `target_inventory` mit vier Targets.
- `G08-SECURITY-01: PASS` — kein öffentlicher Bind, kein Token in Prozess-
  Argumenten, kein `StrictHostKeyChecking=no`, kein globales SSH-Killen.
- `G08-NATIVE-WINDOWS: UNKNOWN` — der Launcher wurde statisch geprüft, aber
  nicht auf Daniels echtem Windows ausgeführt.
- `G08-SSH-E2E: UNKNOWN` — ein realer SSH-Login und die native EXE über den
  Forward müssen noch auf Daniels Windows rückgelesen werden.

## Boundary

G08 beweist den sicheren Transport-Hand-off und den aktuellen read-only
VPS-Agenten. Es beweist weder native Windows-Capture noch Zielauswahl,
Binding, Terminal-Input oder eine öffentliche VPS-Erreichbarkeit.
