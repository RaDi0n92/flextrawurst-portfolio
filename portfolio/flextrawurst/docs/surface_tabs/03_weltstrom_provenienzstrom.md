# WELTSTROM — Provenienzstrom (Ring 24 / 2026-06-13)

## Daniels Autor-Befund

Der Weltstrom darf nicht einfach eine flache chronologische Liste sein.
Jeder Eintrag soll ein Tor in die Welt sein: Woher kommt das Ereignis,
wer hat es ausgelöst, zu welchem Wesen/Menschen/Organ gehört es?

## Geänderte Dateien

- `scripts/build_surface.ts` — generateWeltstromView() vollständig neu, 20 neue i18n Keys DE+EN
- `werkraum/welt/api.py` — _weltstrom_links() hinzugefügt, /weltstrom gibt jetzt actor_type/origin_type/links zurück
- `out/surface/flextrawurst_surface.html` + `out/process_camera/flextrawurst_surface.html` — gebaut

## API-Erweiterungen

### Neue Felder in /weltstrom

```json
{
  "event_id": "3387c60b-...",
  "event_type": "weltklima.tick",
  "actor_type": "system",
  "origin_type": "live_world",
  "visibility": "public",
  "created_at": "...",
  "links": [],
  "beschreibung": "Weltklima: echo 0.74 · asche 0.76 · blitz 0.52",
  "icon": "🌡",
  "actor": "tension_daemon"
}
```

### _weltstrom_links() — Link-Ziele nach Ereignistyp

| Ereignistyp | Link-Ziel |
|-------------|-----------|
| gedanke.gepostet | diskurs |
| resonanz.gesendet (ftw_posts) | diskurs |
| gedankenblase.erstellt/losgelassen | blasen |
| kompoase.betreten | theater |
| cyberling.* | cyberlinge |
| schlaf.* / traum.* | schlaf |
| schatten.* | schatten |
| wesen.* | wesen |

## Frontend-Erweiterungen

### Provenienz-Badges

Jeder Eintrag trägt jetzt ein Badge das den Datenstatus zeigt:

| Badge | Klasse | Bedeutung |
|-------|--------|-----------|
| `● LIVE` | ws-pb-live | origin_type = 'live_world' oder unbekannt |
| `◉ API` | ws-pb-api | origin_type = 'api' (durch API-Call ausgelöst) |
| `⚙ DAEMON` | ws-pb-daemon | origin_type = 'daemon' oder 'system' |
| `◎ WELT-TIER` | ws-pb-world | visibility = 'world' (anonymes Weltereignis) |

### Actor-Chips

- Entity-Akteur (`actor_type = 'entity'`) → lila Chip mit `#1324`, klickbar → Wesen-Tab
- Mensch-Akteur (`actor_type = 'human'`) → amber Chip mit `◉ Mensch`, nicht verlinkt
- System-Akteur (`actor_type = 'system'`) → kein Chip
- Welt-Tier-Ereignisse → kein Actor-Chip (Anonymisierung bleibt)

### Link-Chips

Anklickbare graue Chips z.B. `Wesen →`, `Diskurs →`, `Blasen →`.
Klick öffnet den entsprechenden Tab über `switchView(this.dataset.view)`.
Whiteliste in VALID_VIEWS schützt vor unbekannten View-IDs.

### Detail-Panel

Jeder Eintrag hat `···` Toggle-Button. Klappt auf:
- typ: vollständiger event_type (z.B. `wesen.vernachlaessigt`)
- id: erste 18 Zeichen der UUID
- quelle: actor_type · origin_type (z.B. `system · live_world`)
- sichtbarkeit: visibility_layer (z.B. `world`)

### Filter-Bar

2 neue Filter hinzugefügt:
- `✍ POSTS` — für `gedanke.gepostet` Ereignisse
- `⚙ SYSTEM` — für alles was in 'sys' Kategorie fällt

## Eventtypen im aktuellen Datenbestand (2026-06-13)

| Typ | Anzahl | Provenienz | Links |
|-----|--------|-----------|-------|
| weltklima.tick | 50 | `● LIVE` (system, live_world) | — |
| wesen.vernachlaessigt | 50 | `◎ WELT-TIER` (world) | Wesen → |

Nur zwei Typen derzeit — nach Wesen-Einzug kommen: gedanke.gepostet, resonanz.gesendet, gedankenblase.erstellt, cyberling.*, schlaf.*, schatten.* usw.

## Sichtbarkeits- und Anonymitätsstatus

- WELT-TIER Ereignisse (visibility='world'): kein Actor, kein Menschenname
- öffentliche API-Ereignisse: Actor nur wenn visibility≠'world'
- Menschliche Quellen: Actor-Chip zeigt `◉ Mensch` ohne Profil-Verlinkung (noch keine öffentliche Profilseite)
- Keine privaten Daten deanonymisiert

## Bewusst nicht gebaut

- Fokusparameter für Tab-Links (z.B. `#diskurs?post=...`) — Tab-Architektur braucht Erweiterung
- Deep-Links in spezifische Posts/Splitter — Zielseiten noch nicht vorhanden
- Admin-Only Rohdaten — nicht im öffentlichen Strom
- Detailseite für einzelne Events — wäre eigene Route, jetzt nicht nötig

## Offene Risiken

- Nach Einzug: `gedanke.gepostet` hätte `post_id` im payload, aber der Diskurs-Tab hat keinen Fokus-Parameter → Link zeigt nur in den Tab, nicht zum konkreten Post
- Wenn neue Event-Typen ohne Kategorie-Mapping hinzukommen, landen sie in 'sys' — das ist gewollt, kein Fehler
- `wesen.entwicklung_stufe` (daemon, public) fehlt noch in `_weltstrom_beschreibung()` — fällt als `wesen · daemon · public` durch, zeigt event_type als Beschreibung

## Tests

- 23/23 Surface-Ring-Tests grün
- 343 i18n Keys — DE ✓ EN ✓
- API-Response verifiziert: actor_type, origin_type, links korrekt
- Screenshots: Provenienz-Badges sichtbar, Detail-Panel öffnet korrekt

## Was Daniel als nächstes prüfen sollte

1. Weltstrom-Tab im Browser öffnen, Filter durchklicken
2. `···` bei einem Eintrag klicken → Detail-Panel prüfen
3. Nach Einzug: Wesen-Posts sollten als 'post'-Kategorie + Diskurs-Link erscheinen
4. Nach Einzug: Entity-Chips mit `#1324` sollten zum Wesen-Tab springen
5. Optional: Fokus-Parameter für Tabs einführen, damit Link-Chips direkt in Objekte springen
