# Abnahme: ACK- und Queue-Integrität

Datum: 2026-08-15 14:40 +0200  
Stufe: `ack-queue`  
EVIDENCE_VERSION: 1

## Aktion

Der unmittelbare Versand validiert jetzt jedes ACK für genau die erwartete
`event_id`. Die langlebige IndexedDB-Queue dedupliziert stabil nach
`event_id`, setzt `maxQueueSize` tatsächlich durch, hält Retry- und
Dead-Letter-Zustände, begrenzt Versuche und Alter, plant Backoff mit Jitter und
bricht HTTP-Versand per `AbortController` ab.

## Sichtbar

Der isolierte Chromium-Worker wurde unter `xvfb-run` gestartet. Sein
Terminalbeleg meldete `ok: true`: zwei Queue-Einträge trotz erneutem gleichen
Ereignis, Queue-Überlauf mit `Queue-Limit erreicht`, ein Dead Letter, drei
absichtlich fehlerhafte ACK-Antworten, ein gültiger ACK und ein
`VPS-ACK-Timeout nach 1000ms`. Der Harness meldete dabei keinen produktiven
Workspace und keinen echten Benutzerklick.

## Rücklese

Vorher/Nachher aus dem echten IndexedDB-Worker:

- vor Fehlerstatus: `total=2`, `pending=2`, `dead=0`;
- nach einem Dead Letter: `total=2`, `pending=1`, `dead=1`, sichtbare Queue nur
  noch `queue-limit-2`;
- nach geplanter Verzögerung: `pending=1`, aber `peek()` leer, weil der Retry
  noch nicht fällig ist — der Eintrag bleibt trotzdem gezählt;
- der gültige Transport-ACK enthielt exakt `post-contract-1`;
- der Timeout wurde als Fehler zurückgelesen, nicht als Lieferung markiert.

Der Test liegt in `_codex/tools/test_recorder_ack_queue_live.js`. Zusätzlich
blieben der Extension-Regressionslauf, der Universal-Collection-Live-Test und
der isolierte Receiver-Test erfolgreich.

## Offen / unbekannt

Der ACK-Harness benutzt einen isolierten lokalen Receiver und eine temporäre
Extension-Kopie. Damit ist die Transportlogik bewiesen, aber noch nicht die
Fehlerdarstellung im echten `virtuellerdesktop2`-Workspace mit einem realen
VPS-Ausfall. Der Server-Dedupepfad wurde separat isoliert geprüft; eine
produktive Ereignisübertragung wurde nicht ausgelöst.

- REC-GATE-001: PASS — `check_recorder_skill_gates.py evidence --stage ack-queue` liest diesen Bericht
- REC-ACK-001: PASS — isolierter Worker beweist Dedupe, ACK-Mismatch, Limit, Dead Letter, Retry-Planung und Abort-Timeout
- REC-DOC-001: PASS — Aktion, Sichtbar, Rücklese und Offen/Unbekannt stehen getrennt in diesem Bericht

OUTCOME: PASS
