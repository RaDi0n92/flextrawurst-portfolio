# Tab 09 — KOMPOASE: Splitter-Provenienz, Theater AN/AUS, Aufnahme

## Geänderte Dateien

- `flextrawurst/scripts/build_surface.ts` — Theater-Toggle, koShowInfo, koToggleTheater, ftwDeepLink, Menschenprofil, archivShowDetail, i18n DE+EN
- `flextrawurst/tests/surface_ring_23.test.ts` — 15 neue KOMPOASE-Tests + 1 angepasster Leitstand-Test
- `flextrawurst/out/surface/flextrawurst_surface.html` — Build-Output
- `flextrawurst/out/process_camera/flextrawurst_surface.html` — Process-Camera-Output

## Daniels Autor-Befund

KompOase bleibt als schwebender Splitter-Ort. Grundform erhalten. Kernphysik nicht angefasst.
Ziel: Theater AN/AUS sauber trennbar, Splitter nachvollziehbar, anklickbar, aufnehmbar.

## Erhaltene KompOase-Grundform

- Schwebende Splitter (Canvas-Physics vollständig erhalten)
- Visuelle Partikelphysik (Materialitäten, Materialfelder, Sternenstaub-Hintergrund)
- Gärraum-Panel (Keimkörper, Splitter-Knoten)
- Splitter-Archiv (rechte Seitenleiste, Filterchips)
- Hover-Energieaufladung
- Zoom-Slider
- Verbindungslinien zwischen thematisch ähnlichen Splittern

## Nicht berührte Kernphysik

Bewusst unverändert:

- `koVerschmelze()` — Verschmelzungslogik zweier Splitter zu einem neuen
- `koExplodiere()` — Explosionslogik (Splitter bricht in mehrere)
- `koPhysikUpdate()` — Kollisions- und Energie-Engine
- `koRenderVerbindungen()` — Linien zwischen ähnlichen Splittern
- `Splitter` Klasse — vollständig unverändert
- `koGeneriereTheaterSplitter()` — Theater-Texte (50 vordefinierte Texte)
- `koLaden()` / `koFetchSplitter()` — Datenquellen-Auswahl

## Theater AN — was es jetzt bedeutet

**Vor dem Fix:** Button war versteckt (`display:none`). Theater-Modus war immer aktiv, nicht umschaltbar.

**Nach dem Fix:**

- `ko-theater-wrap` ist sichtbar
- Button zeigt `THEATER: AN` mit i18n-Key `komp.theater.on`
- Erklärungs-Text darunter: `"Theatermaterial · 50 vorbereitete Texte · keine DB-Splitter"`
- `koTheatre=true` → `koFetchSplitter()` ruft `koGeneriereTheaterSplitter(50)` auf
- Splitter haben `synthetisch=true`, kein `db_id`
- Info-Panel zeigt THEATER-Badge (orange) und keinen Aufnahme-Button

## Theater AUS — was es jetzt bedeutet

- Button zeigt `THEATER: AUS` nach Toggle
- Erklärungs-Text: `"Realmodus · nur datenbelegte Splitter aus der Datenbank"`
- `koTheatre=false` → `koFetchSplitter()` fetcht `/zwischenraum/splitter?limit=80&status=aktiv`
- Splitter haben `db_id` (echte UUID aus der Datenbank)
- Info-Panel zeigt LIVE-DB-Badge (grün) und Aufnahme-Button (wenn `db_id` vorhanden)

## Splitterquellen

Aus der Repo-Inventur:

| Quelle | origin_type | Tabelle | Status |
|--------|-------------|---------|--------|
| Gedankenblasen | `human_gedanke` | `splitter` | LIVE |
| Tagebuch | `mw_tagebuch` | `splitter` | LIVE (Flag: splitter_erzeugt) |
| Notizen | `mw_notiz` | `splitter` | LIVE (Flag: splitter_erzeugt) |
| Traumtagebuch | `mw_traumtagebuch` | `splitter` | LIVE (Flag: splitter_erzeugt) |
| Kalender | `mw_kalender` | `splitter` | LIVE (Flag: splitter_erzeugt) |
| Claude-Spiegel | `claude_spiegel` | `splitter` | LIVE |
| Claude-Abwurf | `claude_abwurf` | `splitter` | LIVE |
| Events | `event` | `splitter` | LIVE |
| Theater | (synthetisch) | — | Theater-Modus |

Felder in der `splitter`-Tabelle: `id`, `essenz`, `origin_type`, `materialitaet`, `energie`, `aufnahmen`, `status`, `created_at`, `pos_x`, `pos_y`, `vel_x`, `vel_y`, `substanzspur`, `traumspur`, `resonanzspur`, `human_id` (bei menschlichen Quellen).

## Provenienz im Info-Panel (koShowInfo)

Angezeigt wird jetzt:
- **Herkunft/Theater-Herkunft** mit Farbe (quelle_id oder herkunft)
- **Badge**: THEATER (orange) bei synthetischen Splittern, LIVE-DB (grün) bei DB-Splittern
- **Materialität** (Name)
- **Energie** (Prozent)
- **Erstellt** (Timestamp, nur bei echten Splittern)
- **Aufnahmen**: immer sichtbar — `Nx aufgenommen` oder `noch keine Aufnahmen` (Leer-State)
- **Aufnahme-Button**: nur bei echten DB-Splittern mit `db_id`
- **Share**: Link kopieren (verlinkt auf `/#theater`)
- **Verbindungen**: wenn Kollisionen vorhanden
- **Spur**: wenn echter DB-Splitter (über `/api/kompoase/splitter/<id>/spur`)

## Herkunft und Anonymität

- `darfAnonym = herkunft === 'mensch' && !quelle_sichtbar` → zeigt `mensch (anonym)` statt echter ID
- Theater-Splitter haben `quelle_sichtbar=true`, sind aber als THEATER markiert — kein echter Mensch dahinter
- Deanonymisierung nicht möglich — quelle_sichtbar-Flag wird weiterhin beachtet

## Splitter aufnehmen (Menschen)

- Bereits implementiert: `koAufnehmen(splitterId, dbId)` → POST `/api/kompoase/splitter/<db_id>/aufnehmen`
- Aufnahme-Button wird nur angezeigt wenn: nicht Theater + db_id vorhanden
- Aufnahme persistiert in `splitter_aufnahmen`-Tabelle mit `aufnehmer_type=human`
- `splitter.aufnahmen` counter wird erhöht, UI zeigt aktuellen Stand

## Splitter aufnehmen (Wesen)

- Basis vorhanden: `splitter_aufnahmen`-Tabelle, `aufnehmer_type` kann `entity` sein
- `wesen.splitter.aufgesammelt` zeigt Zahl (via `/api/wesen/<id>`)
- Echter Wesen-Aufnahme-Button in KompOase: **nicht gebaut** — Wesen sind noch im Vor-Einzug
- Datenmodell trägt es: `aufnehmer_type='entity'`, `aufnehmer_id=entity_id`
- Wird aktiv wenn Wesen-Einzug vollzogen

## Aufnahmezähler

- `splitter.aufnahmen` — persistente Zahl in der DB (via `aufnehmen`-Endpoint)
- Angezeigt in: Info-Panel (immer), Archiv-Liste (`↓N`)
- Bei hochem Zoom (>2) auch direkt am Splitter-Kreis als Text

## Aufgenommene Splitter im Menschenprofil

**Aktuell:** Menschenprofil zeigt `spl.gesamt` (von diesem Menschen freigegebene Splitter).
Im Abschnitt "Aufgenommene Splitter" steht ein WARTET-Placeholder:

> Aufnahme-Protokoll geplant — API-Filter per Mensch noch nicht implementiert.

**Was fehlt:** `/api/splitter-aufnahmen` hat keinen Filter nach `aufnehmer_id`. Wenn dieser Filter gebaut wird, kann die Sektion live geschaltet werden.

**Was schon existiert:**
- `splitter_aufnahmen`-Tabelle: splitter_id, aufnehmer_type, aufnehmer_id, aufgenommen_at
- `/api/splitter-aufnahmen` (global, ohne Filter)

## Deep-Links und Share

| Format | Verhalten |
|--------|-----------|
| `#theater` | KompOase-Tab öffnen |
| Share-Button im Info-Panel | Kopiert `location.origin + '/#theater'` |
| Share-Button im Archiv-Detail | Kopiert `location.origin + '/#theater'` |

Hinweis: Kein per-Splitter-Deep-Link — Splitter-IDs im Theater-Modus sind In-Memory. Echte DB-Splitter haben UUIDs, aber kein URL-Routing per Splitter implementiert.

## Archivfilter

| Filter | Bedeutung |
|--------|-----------|
| Alle | Alle Splitter (ohne Status-Filter) |
| aktiv | status='aktiv' |
| aufgenommen | status='aufgenommen' |
| verarbeitet | status='verarbeitet' |

Die Filter sind an echte Daten angeschlossen (`/api/kompoase/splitter?status=<filter>`).

## Eventstrom / Archäologie

- Aufnahmen werden als Event gespeichert: `splitter.aufgenommen` in der `events`-Tabelle
- Archäologie-Suche kann Splitter finden (via `/api/archaeologie` mit Typ `splitter`)
- KompOase-Betreten wird als `kompoase.betreten` Event gespeichert

## Offene Risiken

1. **Per-Mensch Aufnahme-Protokoll**: `/api/splitter-aufnahmen` ohne Nutzer-Filter → WARTET im Profil
2. **Wesen-Aufnahme-Button**: Noch nicht in KompOase gebaut (Wesen-Einzug ausstehend)
3. **Keine per-Splitter Deep-Links**: Theater-Splitter sind In-Memory, keine stabilen URLs
4. **Zeitstempel im Theater-Modus**: `created_at` ist Date.now() beim Objekt-Erstellen, kein persistierter Wert
5. **Mobil**: CSS-Responsive nicht explizit getestet, aber grundlegende Struktur sollte funktionieren

## Was Daniel als nächstes prüfen sollte

1. KompOase öffnen — ist der Theater-Toggle oben rechts sichtbar?
2. Theater-Button klicken — ändert sich der Erklärungstext darunter?
3. Splitter anklicken — zeigt das Info-Panel Theater-Badge (orange) oder LIVE-DB (grün)?
4. Info-Panel: Ist `noch keine Aufnahmen` als Leer-State sichtbar?
5. Info-Panel: Erscheint `aufnehmen`-Button nur bei Theater AUS + echtem DB-Splitter?
6. Share-Button: Kopiert er den richtigen Link?
7. Menschenprofil öffnen — ist `Aufgenommene Splitter WARTET`-Sektion sichtbar?
8. `#theater` in URL tippen — öffnet KompOase?
