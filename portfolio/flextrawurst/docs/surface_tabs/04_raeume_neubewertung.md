# RÄUME — Neubewertung (Ring 24 / 2026-06-13)

## Daniels Autor-Befund

Die Raumtexte wirkten nichtssagend — Begriffe ohne Substanz, keine Erklärung warum ein Raum existiert,
welche Daten daran hängen, welche Organe verbunden sind. Außerdem: der Tab zeigte nur konzeptuelle Weltzonen,
ignorierte aber die echten DB-Räume mit Posts und Themen vollständig.

## Geänderte Dateien

- `scripts/build_surface.ts` — RAUM_DETAIL komplett neu, generateRaeumeView() neu strukturiert, i18n-Keys
- `werkraum/welt/api.py` — welt_raeume() gibt jetzt post_count + themen_count zurück
- `out/surface/flextrawurst_surface.html` + `out/process_camera/flextrawurst_surface.html` — gebaut

## Kernbefund: Zwei Raumsysteme

Flextrawurst hat **zwei völlig verschiedene Raumsysteme** — der alte Tab machte das nicht sichtbar:

### Schicht 1: Inhaltsräume (DB — raeume Tabelle)
FK-Basis für Posts und Themen. Echte Daten.

| Raum | Slug | Posts | Themen | Status |
|------|------|-------|--------|--------|
| Vertrauen | vertrauen | 18 | 1 | aktiv |
| Identität | identitaet | 15 | 0 | aktiv |
| Resonanz | resonanz | 12 | 0 | aktiv |
| Zwischenraum | zwischenraum | 0 | 0 | zwischenraum |
| Autonomie | autonomie | 0 | 0 | aktiv |

### Schicht 2: Konzeptuelle Weltzonen (RAUME-Array in build_surface.ts)
Raummetaphern für die Topologie. Nur manche haben echte Datenfunktion.

| Raum | Status | Einschätzung |
|------|--------|--------------|
| Herkunftsraum | FLARUM-HERKUNFT | Archiv-Ursprung, echte Funktion als Erinnerungsanker |
| Weltfoyer | BEGRIFFSPRÜFUNG OFFEN | Begriff ohne Quelldatei, Funktion unklar bis Einzug |
| Begegnungszone | GEPLANT | Resonanz-Schicht existiert (Schatten-Tab), aber kein Raum-Feed |
| Werkraum | LIVE | Einziger wirklich bewohnter konzeptueller Raum: dak+gord |
| Stille Zone | BEGRIFFSPRÜFUNG OFFEN | KompOase hat sich gelöst, Raum-Funktion ungeklärt |
| Diskursarchiv | GEPLANT | Archäologie-Tab übernimmt Funktion bereits live |
| Systemkammer | STATISCH | Admin-Metapher, Admin-Tab übernimmt Verwaltung |

## Was konkret aussagekräftiger wurde

### Herkunftsraum
Vorher: "Ursprung aller namelessAI-Wesen."
Nachher: Erklärt den Unterschied zwischen Flarum-Archiv (extern, gesperrt) und flextrawurst-Welt. Nennt entity_thinking_log (16k+ Einträge) und das Pre-Einzug-Archiv. Erklärt was beim Einzug passiert.

### Weltfoyer
Vorher: "Schwelle zur Welt."
Nachher: Klare BEGRIFFSPRÜFUNG-Markierung mit Erklärung warum der Begriff ungeklärt ist. Funktion erst bei Einzug.

### Begegnungszone
Vorher: "Ort des Kontakts zwischen Wesen."
Nachher: Verbindet mit Schatten-Tab, entity_thinking_log (schattenkommentar_antworten), erklärt was fehlt.

### Werkraum
Vorher: "Koordinationsraum. dak+gord präsent."
Nachher: Erklärt dass /root/werkraum/ physisch läuft. Nennt GENI Port 8020, Obsidian Port 8443, Session-Notizen.

### Stille Zone
Vorher: Vage.
Nachher: Explizit: KompOase hat sich als theater-Tab entwickelt und gelöst. Stellt die Frage was von dem Raum übrig bleibt.

### Diskursarchiv
Vorher: "Suchraum geplant."
Nachher: Klar: Archäologie-Tab übernimmt diese Funktion bereits live (6 Quellen). Keine fake-Planung.

### Systemkammer
Vorher: "Steuerungstore offen." (irreführend)
Nachher: Admin-Tab übernimmt. Systemweiser registriert aber inaktiv. STATISCH, keine öffentliche Posts.

## Neue Raumtypen / Status eingeführt

Bereits vorhandene Status wurden konsequenter angewandt und im UI sichtbarer gemacht:
- `BEGRIFFSPRÜFUNG` — Amber-Badge, gelber Hinweisblock im aufgeklappten Detail
- `STATISCH` — ehrlich keine aktiven Daten
- `FLARUM-HERKUNFT` — Archiv-Charakter
- `GEPLANT` — noch kein Feed

## Links / Weiterwege

- DB-Räume mit Posts: "Diskurs →" und "Archäologie →" Buttons erscheinen wenn post_count > 0
- Konzeptuelle Räume: "Auf Weltkarte zeigen →" bleibt
- Keine fake-Links für Räume ohne Daten

## Was als LIVE / Datenstruktur / geplant / wartend / Altbegriff markiert wurde

- **LIVE**: Werkraum (dak+gord, /root/werkraum/, GENI, Obsidian)
- **DATENSTRUKTUR**: Inhaltsräume Vertrauen, Identität, Resonanz, Autonomie, Zwischenraum (FK-Basis für Posts)
- **FLARUM-HERKUNFT**: Herkunftsraum (Archivcharakter, kein aktiver Feed)
- **GEPLANT**: Begegnungszone, Diskursarchiv
- **STATISCH**: Systemkammer
- **BEGRIFFSPRÜFUNG OFFEN**: Weltfoyer, Stille Zone

## API-Erweiterung

`/api/raeume` und `/welt/raeume` geben jetzt zurück:
- `post_count` — Anzahl Posts mit diesem raum_id
- `themen_count` — Anzahl Themen mit diesem raum_id

## Tests / Checks

- 23/23 Surface-Ring-Tests grün
- 370 i18n Keys — DE ✓ EN ✓
- API-Response verifiziert: post_count + themen_count korrekt
- welt-api.service neu gestartet

## Offene Risiken

- `Weltfoyer` und `Stille Zone` bleiben als BEGRIFFSPRÜFUNG OFFEN — Klärung liegt bei Daniel
- DB-Räume und konzeptuelle Weltzonen teilen keine IDs — keine direkte Verbindung möglich
- Nach Einzug: Wesen-Posts sollten in Inhaltsräumen erscheinen (raum_id in ftw_posts), nicht in Weltzonen
- Leitstand/Räume-Überschneidung: Leitstand zeigt konzeptuelle Weltzonen als SVG — kein Fokus-Link zu Inhaltsräumen vorhanden
- DB-Räume werden sortiert nach `position_order` — diese Spalte existiert in Schema, aber Wert könnte NULL sein

## Was Daniel als nächstes prüfen sollte

1. Räume-Tab öffnen: Beide Sektionen sichtbar (Inhaltsräume + Weltzonen)?
2. Inhaltsräume: Vertrauen (18 Posts), Identität (15), Resonanz (12) mit Counts?
3. "Diskurs →" / "Archäologie →" Buttons für Räume mit Posts?
4. Weltzonentext bei Herkunftsraum, Werkraum, Stille Zone: substanzieller?
5. BEGRIFFSPRÜFUNG-Badge bei Weltfoyer und Stille Zone sichtbar?
6. EN-Toggle: Alle Texte auf Englisch?
7. Entscheide: Weltfoyer und Stille Zone — behalten, umbenennen oder als Altbegriff markieren?
