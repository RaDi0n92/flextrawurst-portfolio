# Recorder-Parity-Ebene · sichtbarer UI-Beleg

EVIDENCE_VERSION: 1
STAGE: live-click

## Action

- Isolierter sichtbarer Browserlauf mit `collection_workspace.html` und einem transparent gemockten `chrome.runtime`-Status für zwei bereits gespeicherte Snapshots.
- Vorher-Screenshot: [2026-08-21-recorder-parity-before.png](/root/werkraum/_codex/berichte/browserrecorder/2026-08-21-recorder-parity-before.png)
- Danach genau eine sichtbare Aktion: Klick auf `Questions`.
- Danach-Screenshot: [2026-08-21-recorder-parity-after-questions.png](/root/werkraum/_codex/berichte/browserrecorder/2026-08-21-recorder-parity-after-questions.png)

## Visible

- Vorher waren zwei Snapshot-Zeilen sichtbar und der Status lautete `2/2 Quellen ausgewählt · ChatGPT · MARKDOWN`.
- Provider- und Formatfelder sowie die fünf Filteraktionen waren sichtbar.

## Readback

- Nach dem einen Klick las der DOM exakt `0/2 Quellen ausgewählt · ChatGPT · MARKDOWN` zurück.
- Der aktive Filter hatte danach die Klasse `parity-filter-active`.
- Die Statusnotiz las zurück: `Recorder-Snapshots tragen noch keine Provider-Rollen; Questions-Filter zeigt deshalb 0 Quellen ...`.

## Open / limitation

- Dieser Lauf prüft die Recorder-Workspace-Ebene isoliert; er öffnet keinen Provider-Chat und führt keinen Export/Download aus.
- Die sichtbare Auswahl ist für gespeicherte Snapshots strukturell; Question/Answer-Semantik folgt erst mit der späteren Adapter-/Exportkern-Stufe.

- REC-GATE-001: PASS — Vertrags-Gate vor der Änderung grün.
- REC-EYE-001: PASS — Vorher-/Nachher-Screenshot und eine einzelne sichtbare Aktion dokumentiert.
- REC-DOC-001: PASS — DOM-Rücklese und offene Grenze festgehalten.

OUTCOME: PASS
