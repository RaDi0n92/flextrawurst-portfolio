# Wegweiser: `flextrawurst/` — Weltkern, Ringe, Surface

Quelle: `flextrawurst/docs/*.md`, `RING_INDEX.md`, `HANDOFF_CAPSULE.md`, Kopfzeilen der Skripte. Keine Deutung.

## Was der Ordner enthält

| Ordner/Datei | Inhalt |
|---|---|
| `docs/00_SYSTEMVERFASSUNG.md` … `43_FLEXTRAWURST_FEATURE_IDEA_INVENTORY.md` | nummerierte Planungs-/Umsetzungsdokumente. Beginnt bei Systemverfassung/Weltkern/Event-System/Tech-Stack, geht über "Weltbetriebssystem Ring 1–22" bis Prozesskamera und KompOase-Vorform. `43_…` = Ideen-Inventar aus Daniels 490-Punkte-Liste |
| `docs/surface/`, `docs/surface_tabs/` | Dokumente zu Deep-Link/Share/Provenienz (Ring 24) und je ein Dokument pro Surface-Tab 01–11 |
| `kernel/` | TypeScript-Module je Ring: `events/`, `entities/`, `governance/`, `features/`, `import_gate/`, `origin_archive/`, `continuity/`, `memory_candidates/`, `organ_dock/`, `future_concepts/`, `process_camera/`, `process_model/`, `landscape/`, `os_spine/`, `console/`, `export/`, `projections/`, `provenance/` u. a. |
| `scripts/build_surface.ts` | baut die Surface (Single-Page-HTML mit Tabs, Zweisprachigkeit DE/EN, Live-Kanal). ~19.000 Zeilen. **Im Paket ohne den ursprünglichen "Beleidigungs"-Tab** (siehe README der Repo-Wurzel) |
| `scripts/serve_process_camera_preview.ts` | Preview-Server der Prozesskamera |
| `scripts/build_*.ts`, `export_*.ts` | weitere Builder (Werkraum-Karte/Explorer, Worldblick, KompOase) |
| `tests/` | Tests je Ring (`world_os_ring_*`), Surface-Ring-23-Tests, Event-Core, Tick, State-Transition |
| `i18n/` | Übersetzungs-/Wissens-Seeds |
| `ops/` | systemd-Unit für die Preview; `systemkarte/` = Quellen der zwölf Diagramme im Tab SYSTEMKARTE |
| `RING_INDEX.md`, `HANDOFF_CAPSULE.md` | Ringindex bzw. Übergabekapsel |
| `vme/` | `meaning_projection.ts`, `world_meaning_projection.ts` (Visual Meaning Engine laut `docs/03_VISUELLE_GRAMMATIK.md`: übersetzt Weltzustände in sichtbare Formen) |
| `graphify-out/GRAPH_REPORT.md` | generierter Graphbericht |

## Lesereihenfolge laut Docs

1. `docs/00_SYSTEMVERFASSUNG.md` — "Weltbetriebssystem, kein soziales Netzwerk …"
2. `docs/01_WELTKERN.md`, `04_EVENT_SYSTEM.md` ("Der Eventstrom ist die einzige Wahrheit")
3. `RING_INDEX.md`, dann `docs/13_…` ff. (Ringe)
4. `docs/surface_tabs/` für die einzelnen Tabs, `inventur/` (Paketwurzel) für den Ist-Zustand je Tab
5. `scripts/build_surface.ts`

## Zusammenhang mit anderen Teilen

- Surface liest Daten von der Welt-API (Port 8030) → `welt_api_und_datenbank.md`
- Live-Aktualisierung über `/events/stream` (SSE)
- Der Ordner `kernel/` ist eigenständiger Code (TypeScript), getrennt vom Python-Teil in `werkraum/`
