# B0/B1 — Greenfield-Baseline und Domänen-/Policyvertrag

**Datum:** 2026-09-19  
**Neubaupfad:** `/root/werkraum/augen_haende_bridge/`  
**Referenzpfad, unverändert:** `/root/werkraum/_gemini/windows_bridge/`  
**Sichtbare Bridge-Surface:** `surface:windows:bridge`

## Scope

Dieser Beleg gilt nur für den ersten Greenfield-Baustein:

- explizite Agenten,
- explizite Windows- und Linux-Ziele,
- Linux-KDE-Desktop und Original-Terminal als Targets, nicht als neue Bridge-Surfaces,
- Bindung Agent → Target → sichtbare Windows-Surface,
- Capability-Prüfung,
- Lease-Prüfung für Terminalaktionen,
- Not-Aus-Prüfung,
- serialisierbare Action-Requests.

Noch nicht enthalten sind WebSocket-Transport, Windows-Input, Linux-Dispatch, MCP, HUD, Webcam, WorldDOM oder reale Terminalaktionen.

## Ausgeführter Test

```text
cd /root/werkraum/augen_haende_bridge
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Ergebnis: **6 Tests, 6 bestanden, 0 Fehler.**

## Nachgewiesene Fälle

- Ein Agent kann mit `surface:windows:bridge` auf ein Linux-KDE-Desktop-Target gebunden werden.
- Ein nicht gebundenes Target fällt nicht auf ein anderes Windows- oder Linux-Target durch.
- Ein abgelaufener Terminal-Lease wird abgewiesen.
- Ein aktiver Not-Aus weist auch eine ansonsten gültige Anfrage ab.
- Ein Overlay-Target auf dem Windows-Desktop kann ohne Input-Lease angenommen werden.
- Eine Aktion trägt `surface_id` und `target_id` explizit in ihrer serialisierten Anfrage.

## Zusatzprüfung

Der vorgeschriebene Projektgraph-Schritt `graphify update .` wurde versucht. Das Kommando ist in der aktuellen Umgebung nicht installiert bzw. nicht im `PATH` (`graphify: command not found`). Deshalb wurde kein Graphify-Update behauptet oder fingiert.

## Gate

**B0/B1-Core-Gate: PASS**

**B0/B1-Playwright-Gate: PASS — `/root/werkraum/augen_haende_bridge/tests/evidence/B0_B4_PLAYWRIGHT_EVIDENCE.md`**

**Graphify-Postschritt: BLOCKED — Umgebungswerkzeug fehlt**

**B0/B1 vollständig geschlossen:** Core und sichtbarer Playwright-Beweis sind grün.
