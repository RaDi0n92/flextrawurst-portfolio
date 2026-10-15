# Recorder-Parity · erste echte Projektion

EVIDENCE_VERSION: 1
STAGE: download
BACKUP_COMMIT: 1f4dc2073
IMPLEMENTATION_COMMIT: 7896780b7

## Action

- Isolierter sichtbarer Workspace-Lauf mit zwei gespeicherten Snapshot-Fixtures und transparent gemocktem `chrome.runtime`-Readback.
- Vorher-Screenshot: [2026-08-21-recorder-parity-export-before.png](/root/werkraum/_codex/berichte/browserrecorder/2026-08-21-recorder-parity-export-before.png)
- Genau eine sichtbare Aktion: `MARKDOWN exportieren`.
- Danach-Screenshot: [2026-08-21-recorder-parity-export-after.png](/root/werkraum/_codex/berichte/browserrecorder/2026-08-21-recorder-parity-export-after.png)

## Visible

- Vorher: `2/2 Quellen ausgewählt · ChatGPT · MARKDOWN`, Exportbutton aktiv.
- Der Browser meldete einen echten Download mit Dateiname `parity-demo-export.md`.

## Readback

- Downloadinhalt begann mit `# Seitensammlung: Export Demo` und enthielt beide Snapshot-Projektionen.
- Status-Rücklese: `MARKDOWN-Projektion erzeugt · 2/2 Snapshots · 2279 Bytes`.
- SHA-256 des erzeugten Inhalts: `3bda2c8d4a3e6fbcc2c601bf6897347e9bed20e4250eaa53520c57e5ce86b57b`.

## Open / limitation

- JSON, CSV und TEXT verwenden denselben ausgewählten Snapshot-Satz und werden lokal als Projektion erzeugt; PDF nutzt den bestehenden Chromium-Sammlungsdruckpfad und unterstützt in v0 nur „alle Snapshots“.
- Provider ist ein sichtbares Ziel-Feld. Die Daten bleiben `role: snapshot`; keine Question/Answer-Rollen werden erfunden.
- Der Test war ein isolierter Workspace-Lauf, kein Provider-Chat und kein Netzwerk-Fetch.

- REC-GATE-001: PASS — Vertrags-Gate vor dem Bau grün.
- REC-DOWNLOAD-001: PASS — Playwright las Downloadereignis, Dateiname, Inhalt, Bytes und SHA-256 zurück.
- REC-FETCH-001: PASS — Quelle war der bestehende Workspace-Runtime-Readback; kein neuer Netzwerk-Fetch.
- REC-SEC-001: PASS — Dateiname wird über `safeFilename` begrenzt; Inhalt stammt ausschließlich aus ausgewählten gespeicherten Snapshots.
- REC-DOC-001: PASS — Aktion, sichtbare Zustände, Rücklese und Grenzen dokumentiert.

OUTCOME: PASS
