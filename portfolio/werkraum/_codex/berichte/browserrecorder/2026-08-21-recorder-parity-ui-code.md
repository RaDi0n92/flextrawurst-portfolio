# Recorder-Parity-Ebene · Code-Änderung

EVIDENCE_VERSION: 1
STAGE: code-change
BACKUP_COMMIT: a5bf78087
IMPLEMENTATION_COMMIT: 8fa5663bc

## Action

- `check_recorder_skill_gates.py contracts` lief vor dem Schreiben mit `ok: true`.
- In `collection_workspace.html` wurde eine neue sichtbare Parity-Schicht ergänzt.
- In `collection_workspace.js` wurden Provider-/Formatstatus, Snapshot-Auswahl sowie Alle/Questions/Answers/Keine/Invertieren ergänzt.

## Visible

- Provider sichtbar: ChatGPT, Grok, Claude, Gemini.
- Formate sichtbar: CSV, JSON, TEXT, MARKDOWN, PDF.
- Auswahlzeilen bleiben als `Snapshot` beschriftet; es werden keine Chat-Rollen erfunden.

## Readback

- `node --check refferenzen/AI-UI-RECORDER-v1.6.5-DIREKT-LADEN/collection_workspace.js` erfolgreich.
- DOM-Test mit zwei gemockten gespeicherten Snapshots: initial `2/2 Quellen ausgewählt · ChatGPT · MARKDOWN`.
- Derselbe Test las fünf Formatoptionen zurück: `CSV`, `JSON`, `TEXT`, `MARKDOWN`, `PDF`.

## Open / limitation

- Der Exportkern ist absichtlich noch deaktiviert (`Export vormerken · Kern folgt`). Diese Ebene zeigt zunächst nur die gleiche sichtbare Struktur und Möglichkeitenauswahl.
- `graphify update .` konnte nicht ausgeführt werden: `graphify: command not found`.

- REC-GATE-001: PASS — Vertrags-Gate vor der Änderung grün.
- REC-BACKUP-001: PASS — Sicherungspunkt `94247b7b0` vor der Implementierung und `a5bf78087` vor Evidence-Dateien.
- REC-DOC-001: PASS — Implementierung, Readback und Grenzen dokumentiert.

OUTCOME: PASS
