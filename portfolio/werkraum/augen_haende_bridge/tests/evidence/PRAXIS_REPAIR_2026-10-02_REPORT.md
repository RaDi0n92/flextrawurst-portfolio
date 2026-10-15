# Praxis-Reparatur: Abschlussbelege, 2026-10-02

## Umfang

Code und zwei Skills im Bridge-Repository repariert, auf ausdrücklichen Auftrag
von Daniel. Die Claude-Lesekopie bleibt unverändert. Keine Dienständerung, kein
Windows-Build und kein synthetischer UI-PASS.

## Tatsächlich ausgeführte Prüfungen

- Gezielte unittest-Suite: 172 Tests; vollständige Ausgabe in
  [PRAXIS_REPAIR_2026-10-02_TEST_RUN.txt](PRAXIS_REPAIR_2026-10-02_TEST_RUN.txt).
- `python3 tests/pruefe_koerper.py`: Exit 0, vier Quellmuster sauber.
- Beide `skill_pruefen.py`-Läufe: 0 Fehler, 0 Hinweise.
- Beide `quick_validate.py`-Läufe: Skill is valid.
- Claude-Paket: 25/25 SHA-256 MATCH, siehe
  [Integritätsdaten](PRAXIS_REPAIR_2026-10-02_PACKET_INTEGRITY.json).
- `graphify update .`: nicht verfügbar (command not found); kein Update behauptet.

Die untrusted-Origin-Handshake-Fehlermeldung in der Testausgabe gehört zur
absichtlich abgewiesenen Transport-Gegenprobe; die Testsuite meldet OK.

Ein Zwischenlauf scheiterte an genau einer zu langen Skill-Zeile nach der
letzten Formulierungsänderung. Die Zeile wurde umbrochen; der vollständige
172-Test-Lauf danach besteht. Die Zwischenlauf-Ausgabe bleibt als
`PRAXIS_REPAIR_2026-10-02_TEST_RUN_LONG_LINE_FAIL.txt` erhalten.

## Beweisgrenzen

Die Körpertests injizieren den Eingabebackend und beweisen ACK-Reihenfolge,
Fehlerquittung und Korrelationsvertrag. Sie sind keine native Desktop-Probe.
Temporäre Kapsel-/Seed-/Loop-Dienste beweisen Ressourcenidentität, Zustellung,
Fixture-Freigabe und Loop-Budget. Diese Freigaben sind keine Owner-Entscheidungen.
Drei Terminal-Discovery-Befunde aus der früheren Gesamtsuite bleiben ungeklärt.
Eine vollständige grüne Regression oder native Produktabnahme wird nicht behauptet.

## Wiederaufnahme

Für den nativen Prüfschritt braucht es einen aktualisierten Relay, Starter und
Körper mit dem neuen ACK-Protokoll sowie zwei reale verbundene Agenten. Alte
Körper ohne ACK blockieren den Schritt ausdrücklich. Installation und Neustart
wurden in diesem Reparaturpass nicht vorgenommen.
