# Recorder-Parity · explizite Provider-Rollen

EVIDENCE_VERSION: 1
STAGE: live-click
BACKUP_COMMIT: c2da98f39
IMPLEMENTATION_COMMIT: fb1e6121d

## Action

- Isolierter sichtbarer Workspace-Lauf mit einem Capture, dessen HTML zwei explizite `data-message-author-role`-Knoten enthält.
- Vorher-Screenshot: [2026-08-21-recorder-provider-roles-before.png](/root/werkraum/_codex/berichte/browserrecorder/2026-08-21-recorder-provider-roles-before.png)
- Genau eine sichtbare Aktion: Klick auf `Questions`.
- Danach-Screenshot: [2026-08-21-recorder-provider-roles-after-questions.png](/root/werkraum/_codex/berichte/browserrecorder/2026-08-21-recorder-provider-roles-after-questions.png)

## Visible

- Vorher wurden zwei getrennte Quellen sichtbar: eine `user`-Nachricht und eine `assistant`-Nachricht.
- Beide Einträge behielten Snapshot-ID, URL und Capture-Status.

## Readback

- Vorher: `2/2 Quellen ausgewählt · ChatGPT · MARKDOWN`.
- Nach dem Questions-Klick: `1/2 Quellen ausgewählt · ChatGPT · MARKDOWN`.
- Status-Rücklese: `Questions-Filter: 1 explizit belegte Nachrichten. Quellen ohne Provider-Rollen bleiben ausgeschlossen.`

## Open / limitation

- Rollen werden nur aus expliziten Provider-DOM-Markern gelesen. Fließtext, Reihenfolge oder Sprachmuster erzeugen keine Rolle.
- Ohne solche Marker bleibt der Eintrag `snapshot`; Questions/Answers wählen ihn nicht aus.

- REC-GATE-001: PASS — Vertrags-Gate vor dem Bau grün.
- REC-EYE-001: PASS — Vorher-/Nachher-Screenshot und exakt eine sichtbare Aktion dokumentiert.
- REC-DOC-001: PASS — Adapterquelle, DOM-Rücklese und Grenzen dokumentiert.

OUTCOME: PASS
