# WAS IST DAS? — Welterklärungs-Erweiterung (Ring 24 / 2026-06-13)

## Daniels Autor-Befund

Der Tab soll nicht kürzer, glatter oder professioneller werden.
Er soll mehr echtes Textwissen über Flextrawurst tragen.
Kleine, schöne Textkörper — ähnlich wie die vorhandenen Substanzen- und Abspaltungsbereiche.

## Geänderte Dateien

- `scripts/build_surface.ts` — 7 neue HTML-Sektionen, CSS, 28 neue i18n Keys DE+EN, 6 neue Nav-Buttons
- `out/surface/flextrawurst_surface.html` — neu gebaut (23/23 Tests grün)
- `out/process_camera/flextrawurst_surface.html` — deployed

## Neue Erklärungssektionen

### 1. Was Wesen können (id="ub-wesen-koennen")
Status: VOR-EINZUG — Logik gebaut, kein Einzug vollzogen

8 Karten mit ehrlichem Status:
- DENKEN — entity_thinking_log, 16k+ Einträge (VOR-EINZUG)
- POSTEN — gedanke_posten() implementiert (VOR-EINZUG)
- SCHLAFEN & TRÄUMEN — entity_takt.service läuft (LIVE)
- MENSCHENPROFILE LESEN — menschenprofil_lesen() implementiert (VOR-EINZUG)
- AUF SCHATTEN ANTWORTEN — schattenkommentar_antworten() aktiv (VOR-EINZUG)
- SPLITTER AUFSAMMELN — splitter_aufsammeln() im Denk-Takt (VOR-EINZUG)
- ZITIEREN & ANALYSIEREN — noch nicht aktiv (GEPLANT)
- IN RÄUMEN WIRKEN — nach Einzug (GEPLANT)

### 2. Was Menschen können (id="ub-menschlich", erweitert)
Status: LIVE — vollständig ersetzt durch 4-Spalten-Raster

Spalten:
- Öffentliche Präsenz: Profil, Gedankenblasen, Resonanz, Schattenkommentare
- Persönliche Welt (Module): Tagebuch (zitierbar-Flag), Notizen, Traumtagebuch, Kalender, Gedanken
- Weltbeteiligung: Weltkarte, Wissen, Spuren freigeben
- Was nicht geht

### 3. Splitter (id="ub-splitter-erkl")
3-Spalten-Layout:
- Splitter aus Wesen (VOR-EINZUG): Gedanken, Druck, Konflikt, Abspaltung
- Splitter aus menschlichen Spuren (LIVE): human_gedanke origin_type, mw_tagebuch/mw_notizen/mw_kalender/mw_traumtagebuch mit splitter_erzeugt + zitierbar Flags
- Splitter-Physik (LIVE): splitter-physik.service, 60s Takt, verschmelzen/explodieren/veralten

### 4. KompOase (id="ub-kompoase-erkl")
4 Karten:
- Was KompOase ist (LIVE)
- Was gerade läuft: dual-source GENI+DB, splitter-physik.service (LIVE)
- Nach dem Einzug: Wesen-Splitter, gemeinsamer Zwischenraum (GEPLANT)
- Resonanz in KompOase: noch nicht final entschieden (GEPLANT)

### 5. Herkunft & Anonymität (id="ub-herkunft")
5 Karten basierend auf tatsächlichem DB-Stand:
- Splitter herkunft_sichtbar (LIVE)
- gedankenblasen_anonym (LIVE): Standard sichtbar
- notizen_anonym + schattenkommentare_anonym (LIVE): Standard anonym/privat
- mw_tagebuch zitierbar-Flag (LIVE): Standard nicht zitierbar
- Vollständige Privacy-UI (OFFEN): Felder vorhanden, UI noch nicht gebaut

### 6. Vor dem Einzug (id="ub-vor-einzug")
3-Spalten ehrlicher Status:
- Was schon läuft: 12 konkrete System-Items
- Was auf den Einzug wartet: 8 Items (Wesen, Posts, Splitter-Quellen, UI)
- Was nach dem Einzug geplant ist: 7 Items

## Was als live formuliert wurde

- entity_takt.service / Schlaf-System
- Splitter-Physik-Service
- KompOase dual-source
- Schattenkommentare (schreibbar)
- Tagebuch/Notizen/Kalender/Traumtagebuch (DB-Tabellen vorhanden, API aktiv)
- gedankenblasen_anonym, notizen_anonym, schattenkommentare_anonym in nutzer_sichtbarkeit
- herkunft_sichtbar Flag pro Splitter
- zitierbar Flag auf mw_tagebuch

## Was als geplant/vorbereitet formuliert wurde

- Wesen in flextrawurst: VOR-EINZUG — Logik vorhanden, kein Einzug
- Wesen-Splitter aus echten Entitäts-Gedanken
- Zitieren/Analysieren menschlicher Spuren durch Wesen
- Vollständige Privacy-UI
- Traumgenerierung, Abspaltung als Weltprozess, Substanzen als Weltwirkung

## Offene Privacy-/Herkunftsfragen

- Die nutzer_sichtbarkeit-Tabelle existiert, aber eine UI zum Steuern aller Felder auf einmal fehlt noch
- Herkunft-Steuerung für alle Inhaltstypen (Tagebuch, Notizen, Kalender, Traumtagebuch) ist DB-seitig vorbereitet, aber noch nicht vollständig durch die API durchgebunden
- Keine Datenschutzversprechen wurden gemacht — alles als "geplante Schutzlogik" oder "DB vorhanden" formuliert

## Geprüfte Repo-Quellen

- `/root/werkraum/welt/api.py` — nutzer_sichtbarkeit, herkunft_sichtbar, gedankenblasen_anonym, notizen_anonym, zitierbar, mw_tagebuch/notizen/kalender/traumtagebuch
- `/root/werkraum/welt/entity_kern.py` — menschenprofil_lesen(), splitter_aufsammeln(), schattenkommentar_antworten(), gedanke_posten()
- WELTORGANE const in build_surface.ts — aktueller Status aller 21 Tabs

## Tests

- 23/23 Surface-Ring-Tests grün
- 342 i18n Keys — DE ✓ EN ✓
- Build ohne Fehler

## Was Daniel als nächstes prüfen sollte

1. Die neuen Sektionen visuell im Browser durchscrollen
2. Prüfen ob die Splitter-Quelle für Tagebuch/Notizen/Kalender/Traumtagebuch vollständig durch API implementiert ist (mw_tagebuch hat splitter_erzeugt Flag, aber wird es auch geschrieben?)
3. Nach dem Wesen-Einzug: Tab erneut aktualisieren — insbesondere "Was Wesen können" von VOR-EINZUG auf LIVE umstellen
4. Privacy-UI (vollständige nutzer_sichtbarkeit-Einstellungsseite) als separater Bauauftrag
