# LEITSTAND — Neubewertung (Ring 24 / 2026-06-13)

## Was gebaut wurde

Der LEITSTAND-Tab wurde von einer verblassten Weltkarte zu einer ehrlichen, lesbaren Weltstatuskarte umgebaut.

## Neue Status-Typen

| Typ | Bedeutung |
|-----|-----------|
| `VOR-EINZUG` | System existiert, aber kein echter Einzug vollzogen |
| `FLARUM-HERKUNFT` | Raum/Objekt stammt aus der Flarum-Vorwelt |
| `STATISCH` | Erklärender Kanon — keine Daten, kein Datenfeed |
| `BEGRIFFSPRÜFUNG` | Begriff nicht ausreichend begründet, Quelle fehlt |
| `WARTET` | System vorhanden, UI zeigt noch Leerzustand |

## Räume und ihre ehrlichen Status

| Raum | Status | Begründung |
|------|--------|------------|
| Herkunftsraum | `FLARUM-HERKUNFT` | 6 Wesen registriert, kein Einzug vollzogen |
| Weltfoyer | `BEGRIFFSPRÜFUNG` | Begriff nicht begründet, keine Quelldatei |
| Begegnungszone | `GEPLANT` | Kein Datenfeed, kein aktiver Slot |
| Werkraum | `LIVE` | dak+gord aktiv, Koordination läuft |
| Stille Zone | `BEGRIFFSPRÜFUNG` | Begriff nicht begründet, keine Quelldatei |
| Diskursarchiv | `GEPLANT` | Konzept, kein Bau |
| Systemkammer | `STATISCH` | 7 Grundgesetze, kein Datenfeed |

## BEGRIFFSPRÜFUNG-Räume

Weltfoyer und Stille Zone sind als `BEGRIFFSPRÜFUNG` markiert. Das bedeutet:
- Der Begriff taucht im System auf (in `RAEUME`-Array), hat aber keine weitere Begründung
- Keine Quelldatei, keine Konzept-Datei die den Begriff einführt
- Funktion unklar solange kein Wesen-Einzug läuft

Konsequenz: Diese Räume werden nicht gelöscht (kein falsches LIVE, aber auch kein Löschen).
Sie bleiben als Konzept-Platzhalter mit ehrlichem Status.

## Weltorgane (neue Sektion in linker Rail)

21 Surface-Tabs sind jetzt als Weltorgane in der linken Rail sichtbar, mit ehrlichem Status.
Jedes Organ ist anklickbar und öffnet den zugehörigen Tab über `selectWeltorgan()`.

Aktuelle Organ-Status:
- `LIVE`: Weltstrom, Diskurs, Schlaf, Cyberlinge, Einsicht, KompOase, Blasen, Archäologie, Schatten, Wissen, Räume, Menschen, Systeme
- `VOR-EINZUG`: Wesen, Gruppen
- `WARTET`: Denken, Screens, Splitter
- `STATISCH`: Gesetze, Forschung, Partner

## SVG Zoom/Pan

Neue Interaktionsmöglichkeiten auf der Weltkarte:
- Mausrad: Zoom rein/raus
- Alt + Drag: Karte verschieben
- Touch: Pinch zum Zoomen, Ein-Finger-Drag zum Verschieben
- `+`/`−`/`↺` Buttons oben links im Karten-Bereich

Implementierung als IIFE über `<g id="wzg">` Wrapper-Group in SVG.

## Inspector-Erweiterungen

- `quelle`-Feld: zeigt Datei/API-Quelle des Raums
- `begriffsstatus`-Feld: bei `BEGRIFFSPRÜFUNG`-Räumen als Warnblock (amber) mit `⚠` Icon
- Weltorgan-Inspector: Status, Typ, aktueller Stand, `→ Tab öffnen` Button

## Nicht gelöscht

Leere oder wartende Räume wurden nicht entfernt. Grundprinzip: ehrlich beschriften, nicht verstecken.
Der Bau-Zustand ist dokumentiert — auch "wartet" ist ein gültiger Zustand.

## Tests

- 23/23 Surface-Ring-Tests grün (`npx tsx --test tests/surface_ring_23.test.ts`)
- Build: `npx tsx scripts/build_surface.ts` ohne Fehler
- i18n: alle neuen Keys in DE und EN vorhanden
- JS-Syntax: kein `missing ) after argument list` — `data-view`-Pattern statt inline-Quotes
