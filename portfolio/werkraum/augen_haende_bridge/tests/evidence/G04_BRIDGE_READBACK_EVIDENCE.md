---
stage: G04
date: 2026-09-20
author: codex bei Daniels VPS
scope: bridge-readback-refresh
---

# G04 — Bridge-Readback-Refresh

EVIDENCE_VERSION: 1

## FocusContract

- Ziel: Ein Windows-Overlay kann über den bestehenden lokalen Bridge-Relay ein
  read-only Terminalinventar vom VPS anfordern und atomar übernehmen.
- Erhaltungsanker: Loopback-only Relay, getrennte Session-/Epoch-Prüfung,
  keine Shell-/Input-/Write-/Delete-Fähigkeit, getrennte lokale und remote
  Target-IDs, Playwright bleibt äußerer Zeuge und kein Windows-Ersatz.
- Nicht Teil dieses Steins: native Windows-Capture-Abnahme, Terminaleingabe,
  Remote-Inspect und fertige Endoberfläche.

## Implementierte Kette

`desktop target_inventory_request`
→ Relay-Capability-/Payload-Prüfung
→ Agent-`BridgeRuntime` mit `TargetRegistry.bridge_inventory()`
→ `target_inventory` mit Request-ID, Zeitstempel und Identitäten
→ Relay-Receipt
→ Overlay-Korrelation/Freshness-Prüfung
→ `TargetRegistry.apply_remote_inventory()`
→ atomarer, namespaced Read-only-Zielbestand.

Remote-Ziele erhalten auf dem Client IDs wie `bridge-agent:terminal-1` und
bleiben bis zum späteren Remote-Inspect-Adapter `unavailable`. Ein vom VPS
gemeldetes `available` wird nicht als lokale Verfügbarkeit ausgegeben.

## Belege

- CORE-97: PASS — `PYTHONPATH=src:. python3 -m unittest discover -s tests -q`.
- PYCOMPILE-04: PASS — Transport, Runtime, Registry und Windows-Overlay
  kompilieren ohne Fehler.
- PW-G04-01: PASS —
  `PYTHONPATH=src python3 tests/transport_playwright_proof.py` beendet sich mit
  `status: PASS`; ein echter Chromium-Testpeer fordert Inventar an, ein
  Produktions-Registry-Provider erzeugt es, der Relay liefert es zurück und
  ein zweiter Registry-Consumer übernimmt es.
- PW-G04-02: PASS — `PYTHONPATH=src python3 tests/reference_surface_proof.py`
  beendet sich mit Exit-Code 0.
- IDLE-04: PASS — BridgeRuntime behandelt Anwendungssilenz nicht mehr als
  Disconnect; der Test läuft mit wiederholtem kurzem Receive-Timeout weiter.
- RECEIPT-04: PASS — Request und Response unterscheiden `forwarded` und
  `received`; die Playwright-Evidence enthält die Nachrichtensequenzen.
- NATIVE-WINDOWS-04: UNKNOWN — der Linux-VPS kann keinen echten Windows-
  Overlay-Lauf und keinen Win32-Capture-Beleg ersetzen.
- CHATGPT-REVIEW-04: NOT_CLAIMED — keine gebundene C2C-Projektsession.

## Reviewer

- Claude Opus: Der Read-only-Kern war tragfähig, fand aber einen echten
  60-Sekunden-Idle-Disconnect sowie Readback-Grenzen. Idle-Verhalten,
  Verfügbarkeits-Clamping, Request-Korrelation/Freshness, Namespacing,
  Provider-/Consumer-Proof, Längen-/Duplikatprüfung und sichere Message-ID-
  Kürzung wurden eingearbeitet.
- Der produktive VPS-Einstieg
  `/root/werkraum/augen_haende_bridge/client_vps/bridge_agent.py` verdrahtet
  `TargetRegistry.bridge_inventory` mit `BridgeRuntime`; der Provider ist
  damit nicht mehr nur eine Test-Lambda.
- Gemini/Antigravity: Für diesen Abschluss liegt kein verwertbarer neuer
  Bericht vor; es wird kein Gemini-PASS behauptet.

OUTCOME: PARTIAL

Der Bridge-/Registry-Stein ist reproduzierbar belegt. Der native
Windows-Erstkontakt und die Windows-Capture-Evidence bleiben der nächste
Plattformstein; daraus wird kein falscher G04-Windows-PASS abgeleitet.
