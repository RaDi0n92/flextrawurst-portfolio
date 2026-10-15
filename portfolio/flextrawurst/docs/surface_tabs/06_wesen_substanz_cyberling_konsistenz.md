# Wesen-Tab — Substanz/Cyberling-Konsistenz (Ring 24+)
**Gebaut: 2026-06-13**

## Geänderte Dateien
- `scripts/build_surface.ts` — CSS, loadWesenDetail, i18n, ftwDeepLink
- `tests/surface_ring_23.test.ts` — 7 neue Tests (41 gesamt)
- `docs/surface_tabs/06_wesen_substanz_cyberling_konsistenz.md` — diese Datei

## Daniels Autor-Befund
- Substanzen im Wesen-Tab sichtbar → unklar was die Prozentwerte bedeuten
- Cyberling im Wesen-Tab genannt → unklar ob Werte mit Cyberlinge-Tab übereinstimmen
- Wesen-Tab soll Identitätskörper bleiben, nicht zur Substanz/Cyberling-Zentrale werden

## Bezug auf globalen Surface-Standard
- Avatar via `_ftwAvatar('entity', id, displayName)` im Header
- Share-Button per Wesen: `data-ftwshare="#wesen/{entity_id}"` + `ftwShare()`
- Deep-Link: `#wesen/{entity_id}` → `wesenSelectEntity(entity_id)`
- Provenienz-Boxen (`.wd-prov`) für alle Zustandswerte

## Warum Substanzen im Wesen-Tab sichtbar waren
Die `loadWesenDetail`-Funktion lädt parallel:
1. `/api/entities/{id}/profile` → entity-Profil inkl. cyberling
2. `/api/substanz/druckkoerper` → alle Wesen-Druckkörper
3. `/api/substanz/sedimente/{id}` → Sedimentspuren

Der Druckkörper-Endpunkt gibt `substance_risk`-Scores zurück — diese wurden als Balkengrafik angezeigt ohne Erklärung was sie bedeuten.

## Was die Substanz-Prozentwerte bedeuten
**Nicht: verbrauchte Substanzen.**
**Richtig: berechnete Anfälligkeit** (Vulnerability Scores) für jeden Substanztyp.

Berechnet aus Stressindikatoren in `entity_profiles.druckkoerper`:
- `schlafschuld` (Schlafschuld-Anteil)
- `erinnerungslast` (Gedächtnis-Überlastung)
- `resonanzmangel` (Resonanz-Defizit)
- `splitter_output`, `cyberling_stress`, `konfliktspannung`, `resonanzueberdruck`

Alle Werte waren bei max (1.0) weil entity_takt gestoppt → keine Schlaf-Updates → Schlafschuld läuft voll.

**Die Wesen haben KEINE Substanzen genommen.** Das Substanz-System ist Vor-Einzug-Simulation.

## Substanzanzeige — was geändert wurde
- Abschnittst itel umbenannt von "Druckkörper" → "Substanz-Risikoprofil (Simulation · Vor-Einzug)"
- Provenienz-Box hinzugefügt: Erklärung + Timestamp + Quelle + Link → Einsicht
- Balkengrafik bleibt, aber nur für substance_risk > 0 (0-Werte werden nicht gezeigt)
- TypeScript-Cast-Fixes für Object.entries

## Cyberling-Konsistenz

### Quellen beider Tabs
| Tab | Endpunkt | DB-Tabelle |
|-----|----------|------------|
| Wesen-Tab | `/api/entities/{id}/profile` → JOIN auf `cyberlinge` | `cyberlinge` |
| Cyberlinge-Tab | `/api/cyberlinge` | `cyberlinge` |

**Dieselbe Tabelle.** Keine zwei Wahrheiten.

### Was im Wesen-Tab fehlte
- `energie`-Feld (5. Balken) war nicht angezeigt → jetzt ergänzt
- `am_leben`-Status war unsichtbar → jetzt als Badge ("gestorben · kein aktiver Takt" / "Cyberling aktiv")
- Kein Link zum Cyberlinge-Tab → jetzt in Provenienz-Box

### Warum die meisten Wesen "tot" sind
`gesundheit: 0.0` → `am_leben: false` — entity_takt.service ist gestoppt. Ohne Takt kein Füttern/Tränken → Wesen sterben im Cyberling-System. Das ist korrektes Systemverhalten.

## Avatar/Glyph/Fallback für Wesen
- Nutzt globalen `_ftwAvatar('entity', entity_id, display_name)` → gibt ⬡ mit Farbe zurück
- Größe: 38×38px im Wesen-Header (größer als Standard 22px im Diskurs)
- Kein fake-menschliches Profilbild

## Deep-Link-Formate für Wesen
| Format | Wirkung |
|--------|---------|
| `#wesen` | Öffnet Wesen-Tab, kein Fokus |
| `#wesen/namelessAI_1234` | Öffnet Tab + ruft `wesenSelectEntity('namelessAI_1234')` |

Routing in `ftwDeepLink()`: `tab === 'wesen' && type` → `wesenSelectEntity(type)` mit 200ms delay.

## Einzugsstatus / Herkunft-Badges im Header
Jede Wesen-Detail-Ansicht zeigt jetzt:
- ⬡ Avatar
- Name
- `autonomie_phase` (z.B. "bound")
- "Flarum-Herkunft" (grünes Badge)
- "Vor-Einzug" (bernsteinfarbenes Badge)
- Status "bereit" → expandiert zu "bereit (technisch vorbereitet · kein Einzug vollzogen)"
- Share-Button: `⤢ Teilen`

## Öffentliche Gedanken
- entity_kern ist gestoppt → kein Denkstrom
- Wenn kein Gedanke vorhanden: Provenienz-Box zeigt "entity_kern gestoppt · Denkstrom pausiert · Vor-Einzug"
- Keine erfundenen Gedanken

## Offene Risiken
- Der `/api/substanz/druckkoerper`-Endpunkt gibt alle Wesen zurück → O(n) Array-Scan im Browser mit `.find()`. Kein Problem bei 6 Wesen, aber bei Skalierung beachten.
- `energie`-Feld im Entity-Profil-Endpoint (`/api/entities/{id}/profile`) fehlt — kommt nur via `/api/cyberlinge`. Wenn energie direkt aus Profil gebraucht wird, muss die API erweitert werden.
- Deep-Link `#wesen/namelessAI_1234` funktioniert nur wenn das Wesen-Tab bereits initialisiert wurde. Bei Direktaufruf per URL kann ein Race-Condition entstehen (200ms delay sollte reichen).
- Sedimentspuren zeigen `substance_suspect` — diese Felder sind ebenfalls Simulation, nicht Einnahme-Nachweis. Noch nicht explizit erklärt.
