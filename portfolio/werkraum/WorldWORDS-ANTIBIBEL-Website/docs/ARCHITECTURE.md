# Architektur

## Schichten

1. **Nginx** beendet TLS, schützt Login-/Registrierungs-POSTs durch Rate Limiting und stellt gehashte statische Dateien sowie moderierbare Medien bereit.
2. **Gunicorn** betreibt die Django-Anwendung ausschließlich lokal.
3. **Django** liefert öffentliche Sammlung, Konten, Diskussionen, Kuratorium, API und Export.
4. **PostgreSQL** ist der kanonische Live-Arbeitsstand.
5. **Open-Source-Körper** ist Ursprung und öffentliches Langzeitgedächtnis. Er wird idempotent importiert; der Live-Stand erzeugt personenbezogen bereinigte Snapshots zurück.

## Zentrale Domänenobjekte

- `Term`: unveränderliche Rohform, Status, Erklärungen, Herkunft, Varianten, Verkörperungen und Aufnahmezustand
- `ProvenanceEvent`: append-only Zeitspur; wird nie gelöscht oder still überschrieben
- `ModerationDecision`: datierte kuratorische Entscheidung mit Begründung und Belegstellen
- `Comment` + `CommentRevision`: öffentliche Diskussion und erhaltene frühere Fassungen
- `ContributionProposal`: benannte Ergänzung, die geprüft und übernommen oder nicht übernommen wird
- `WordClass`, `Tag`, `Collection`, `TermRelation`: nichtchronologische Erkundungswege durch denselben Bestand
- `Notification`, `Follow`, `Reaction`, `Report`, `ContactMessage`: Gesprächs- und Moderationsorgane

## Aufnahmeinvariante

Eine öffentliche Einreichung ist kein offizieller Registereintrag. Offiziell aufgenommen ist ein Begriff erst durch eine sichtbare kuratorische Entscheidung. Der Statuswechsel verändert weder Rohform noch ursprüngliche Eingabe noch frühere Diskussionen.

## URL- und Identitätsvertrag

- kanonischer Außenpfad: `/WORLDwordsANTIbibel/`
- Sprachpfade: `/de/`, `/en/`, `/es/`
- permanente Begriffsadresse: `/<sprache>/term/<slug>/`
- API: `/api/v1/terms/`
- statische Dateien und Sitzungs-Cookies bleiben auf den Websitepfad begrenzt

## Sicherheitsgrenzen

- Dienstnutzer ohne Shell und ohne globale PostgreSQL-Erstellrechte
- Produktions- und Testdatenbank getrennt
- keine externen Fonts, Tracker oder CDN-Abhängigkeiten
- öffentlicher CSP ohne Inline-Skripte
- private Ansichten mit `no-store`
- Uploadgrenze 5 MB im Modell und 6 MB am Proxy
- öffentliche Markdown-Ausgabe wird mit Bleach bereinigt
