# BITTE AN DIE SKRIPTKÖRPER-SESSION — OPTIONALER MASCHINENLESBARER REIFESTATUS

Stand: 2026-09-18

Beim Premortem der Forschungsleitstelle ist eine echte Schnittstellenlücke aufgefallen:

Die Forschungsseite kann aktuell technisch erkennen:
- Skript vorhanden
- Skript-SHA256
- Output vorhanden
- Output nennt aktuellen/veralteten Harvester-SHA256

Sie kann aber **nicht maschinenlesbar erkennen**, ob dein angekündigtes individuelles 8×-semantisches Red-Team eines Skripts
- noch nicht begonnen,
- gerade in Arbeit,
- abgeschlossen,
- nach späterer Skriptänderung wieder veraltet

ist.

Bitte ändere dafür nicht deinen laufenden Prüfprozess. Wenn es zu deinem System passt, wäre eine kleine read-only Datei für mich ideal, zum Beispiel:

`00_SCRIPT_REVIEW_STATUS.json`

Minimaler Vorschlag:

```json
{
  "schema_version": 1,
  "updated_at_utc": "...",
  "scripts": {
    "1": {
      "script_sha256": "...",
      "state": "NOT_STARTED|IN_REVIEW|REVIEWED|INVALIDATED",
      "completed_rounds": 0,
      "required_rounds": 8,
      "evidence_path": "..."
    }
  }
}
```

Wichtig wäre vor allem:
- Reifestatus ist an **genau den Skript-SHA256** gebunden.
- Wird das Skript danach geändert, darf alter REVIEWED-Status nicht weitergelten.
- Die Forschungsseite liest diese Datei nur; sie schreibt sie nicht.

Bis so ein maschinenlesbarer Nachweis existiert, behandelt meine Leitstelle den semantischen Reifezustand bewusst als `UNKNOWN`, selbst wenn deine Markdown-Antwort einzelne abgeschlossene Skripte erwähnt.
