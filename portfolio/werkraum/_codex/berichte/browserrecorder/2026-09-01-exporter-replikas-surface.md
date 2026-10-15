EVIDENCE_VERSION: 1

# Exporter-Replikas — Surface-Abnahme

## Aktion

Die neue Surface-Ansicht `EXPORTER` wurde in `/root/werkraum/flextrawurst/flextrawurst_surface.html` ergänzt und anschließend mit echten lokalen Original-JSON-Daten aus den vorhandenen Abnahmeordnern gespeist. Sie projiziert ChatGPT, Grok, Claude und Gemini mit CSV, JSON, TEXT, MARKDOWN und PDF als sichtbaren Formatgesten.

## Sichtbar

- Screenshot: `/tmp/flextrawurst-exporter-real-data.png`
- Surface-Zustand: aktiver Tab `exporter`, vier Provider-Schaltflächen, fünf Format-Schaltflächen.
- Sichtbare Interaktion: Gemini ausgewählt, PDF ausgewählt, echter Originalausschnitt und Sonderfläche `Unterhaltungslink · Bilder` eingeblendet.
- Sichtbare Originalzählungen: ChatGPT `10`, Grok `60`, Claude `188`, Gemini `66` Nachrichten.
- Sichtbare Grenze: `REPLICA · OFFLINE`, `KEIN LIVE-FETCH`, `keine Datei geschrieben`.

## Rücklese

- DOM-Rücklese nach dem normalen Tab-Klick: `display=flex`, View-Rechteck `[0,120,1440,780]`, `providers=4`, `formats=5`.
- Interaktions-Rücklese: Anbieterwechsel auf Gemini, Formatwechsel auf PDF, Quellen-Schalter aktiv, Status `Bereit für lokale Projektion · gespraech-export.pdf · keine Datei geschrieben`.
- Original-JSON-Dateien wurden gelesen und per SHA-256 rückgelesen:
  - ChatGPT: `8fa449ce4cb905fd912a36168b988a16720e7c647b7e534f02404b7fccf899d2`
  - Claude: `f58c9699da619dae528015c33c137210cdd8e6c1423f142eb07fefae5003e777`
  - Gemini: `79b06defa0cc4fbd16b841086bea7346c4d6df7510cb2855abd4d8fd248a8fe2`
  - Grok: `5e5eb61bb73663003141f5611fa05228fa9efc1dcf03a512f5d4c6e32e8371fa`
- Die vier ZIP-Referenzkörper bleiben zusätzlich über ihre bisherigen Archiv-Hashes verknüpft.
- Inline-JavaScript-Prüfung: 16 JavaScript-Skripte, 0 Parse-Fehler.

## Offen / Unbekannt

- Die Replika behauptet keine Pixelgleichheit und erzeugt bewusst keine Exportdatei.
- Kein Live-Provider-Fetch und keine Authentifizierung wurden hinzugefügt.
- Ein echter Browser-Download mit Fertigmeldung ist daher nicht Teil dieser Abnahme; die vorhandenen Original-JSON-Dateien sind die gelesenen Datenkörper, die ZIPs bleiben die geprüften Exporter-Referenzen.
- Die bestehende Surface meldet weiterhin `scvStoppeAlleGridLive is not defined`; dieser Altfehler liegt außerhalb der Replika und wurde nicht verändert.

- REC-GATE-001: PASS — Vertragsprüfung mit 10 Markern und 10 Skills grün.
- REC-REPLICA-001: PASS — vier Provider, fünf Formate, echte Original-JSON-Ausschnitte, getrennte Roh-/Projektionsebene und sichtbare Provenienzgrenze vorhanden.
- REC-DOWNLOAD-001: PASS — vier vorhandene Original-JSON-Dateien und vier Referenz-ZIPs gelesen und per SHA-256 rückgelesen; die Replika macht keinen falschen Fertig-Download-Claim.
- REC-FETCH-001: PASS — hinzugefügte Replika enthält keinen Live-Fetch und zeigt `KEIN LIVE-FETCH` sichtbar.
- REC-DOC-001: PASS — Aktion, Sichtbar, Rücklese und Offen/Unbekannt dokumentiert.

OUTCOME: PASS
