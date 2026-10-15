# Governance

## 1. Grundmodell: offene Mitarbeit, kuratierte Aufnahme

Die WorldWORDS ANTIBIBEL ist offen für Beiträge, aber das offizielle Register ist kein automatisch wachsender Mehrheitskanon. Jeder darf Material einreichen. Daniel entscheidet als Gründungskurator, welche Begriffe er in das offizielle Register aufnehmen will.

Diese Entscheidungsbefugnis gilt nur für die Kennzeichnung **„von Daniel in das offizielle WorldWORDS-Register aufgenommen“**. Sie beschränkt weder das Recht auf Forks noch das Recht, eigene Register mit anderen Entscheidungen zu führen.

## 2. Mögliche Beiträge

Beiträge können sein:

- neue Rohwörter und Schreibvarianten,
- genaue Fundstellen und Originaleingaben,
- Entstehungsgeschichten,
- Deutungen und Gegen-Deutungen,
- Grenzen und ausdrücklich ausgeschlossene Bedeutungen,
- Übersetzungen von Erklärungen,
- reale Verkörperungen in Projekten, Dateien, Rollen oder Systemen,
- Herkunftskorrekturen,
- Hinweise auf Halluzinationen oder falsche Zuschreibungen.

## 3. Statusfolge

`SUBMITTED → EVIDENCE_CHECK → DANIEL_REVIEW → ACCEPTED / DEFERRED / DECLINED / WITHDRAWN`

Zusätzliche spätere Zustände:

`ACTIVE → SUPERSEDED / DEPRECATED / RETIRED`

Kein Zustandswechsel löscht die vorherige Geschichte. Änderungen werden als neue Ereignisse angehängt.

## 4. Daniels mögliche Entscheidungen

Daniel kann einen Beitrag:

- als eigenständigen Begriff aufnehmen,
- als Schreibvariante aufnehmen,
- als Übersetzung oder fremdsprachige Mutation aufnehmen,
- als Deutung zu einem vorhandenen Begriff aufnehmen,
- zur weiteren Quellenarbeit zurückstellen,
- ablehnen,
- wegen fehlender Veröffentlichbarkeit schließen.

Eine Aufnahme gilt erst dann als offiziell, wenn eine Datei unter `data/approvals/` vorhanden ist, die mindestens Begriff-ID, Entscheidung, Datum, Daniel als Entscheider und eine Begründung enthält.

## 5. Unveränderliche Herkunft

Bei aufgenommenen Begriffen bleiben mindestens erhalten:

- ursprüngliche Form und Groß-/Kleinschreibung,
- Einreicher oder Übermittler,
- bekannte Urheberlage samt Unsicherheit,
- Datum oder ausdrücklich markierte Datumsunsicherheit,
- Originalzitat beziehungsweise exakter Eingabekörper,
- Quellenbezug und Hash, sofern verfügbar,
- frühere Deutungen,
- Übersetzungsurheber,
- Daniels Aufnahmeentscheidung.

Fehlerhafte Zuschreibungen werden korrigiert, aber nicht unsichtbar überschrieben. Das alte Ereignis bleibt mit Status `corrected` oder `retracted` erhalten.

## 6. Mensch–AI-Provenienz

AI-Beiträge werden nicht pauschal als menschliche Urheberschaft ausgegeben. Nach Möglichkeit werden getrennt gespeichert:

- menschlicher Operator,
- AI-System oder Modell,
- Session oder Gesprächskörper,
- exakte AI-Formulierung,
- menschliche Auswahl, Veränderung oder Bestätigung,
- Unsicherheit über die tatsächliche Wortgeburt.

`role=user`, Datenbankfelder oder spätere Zusammenfassungen sind allein kein Urheberschaftsbeweis.

## 7. Rohform und Übersetzung

Die Rohform eines Wortes bleibt unverändert. Sprachfassungen übersetzen die **Erklärung**, nicht heimlich das Wort. Eine übersetzte oder mutierte Wortform kann als eigener Beitrag vorgeschlagen werden und erhält eigene Provenienz.

## 8. Sicherheit und Privatsphäre

Rohheit bedeutet nicht, Zugangsdaten, private Adressen, unveröffentlichte personenbezogene Daten oder fremde geschützte Volltexte zu publizieren. Notwendige Auslassungen werden sichtbar protokolliert. Ein öffentlicher Provenienzbeleg darf auf einen gehashten privaten Ursprung verweisen, wenn dessen Veröffentlichung unzulässig wäre.

## 9. Forks und offizielle Kennzeichnung

Forks dürfen das gesamte lizenzierte Material verändern und eigene Aufnahmeorgane schaffen. Die Kennzeichnung `accepted_by_daniel: true` darf jedoch nur zusammen mit einem unveränderten oder nachvollziehbar fortgeschriebenen Daniel-Entscheidungsbeleg verwendet werden.

## 10. Governance-Änderungen

Änderungen dieser Governance werden als eigener Vorschlag behandelt. Die Regel, wer im offiziellen Hauptregister Aufnahmeentscheidungen trifft, kann nur durch eine ausdrücklich dokumentierte Entscheidung Daniels geändert werden.
