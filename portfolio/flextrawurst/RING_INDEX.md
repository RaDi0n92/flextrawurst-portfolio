# RING_INDEX — Weltbetriebssystem

**Zweck:** Kompakter Einstiegspunkt nach `/clear` oder Accountwechsel.

---

## Aktueller Kopf

| | |
|---|---|
| HEAD | `459cf09` feat(governance): add global governance matrix and approval workflow |
| Branch | master |
| Remote | keines (kein git remote konfiguriert) |
| Tests | 1336/1336 grün (Stand: Ring 20 abgeschlossen) |
| Aktiver Ring | 21 — Build Discipline (Doku-Phase, kein Code) |

---

## Arbeitsregeln ab Ring 21

- Token sparen: nur relevante Dateien lesen, kein blindes Verzeichnis-Dump
- Keine 100-Test-Pflicht; Tests nach Risiko (Fundament: 40–80, Erweiterung: 10–30, Guard: 3–10, Doku: 0)
- Bestehende Tests immer laufen lassen
- Neue Tests nur für neue Verantwortung
- Keine langen Wiederholungsblöcke in Berichten

---

## Ring-Tabelle

| Ring | Name | Status | Kernzweck | Hauptartefakt(e) | Commit |
|---|---|---|---|---|---|
| 00–12 | Konzept- & Plandokumente | doku | Systemverfassung, Weltkern, Engine-Pläne | `docs/00_`–`docs/12_` | — |
| 1 | World Engine Core | implementiert | Erster Event-Core, Tick, Weltbewegung | `kernel/src/` | `3f94b9e`–`95ee64f` (mehrere) |
| 2 | Scenario Inspection | implementiert | Szenario-Inspektion, Konzept-Guard | `kernel/src/` | `2672f33` |
| 3 | World OS Spine | implementiert | OS-Spine, Slots, Provenance, Readiness | `kernel/src/` | `4d16a1f` |
| 4 | Import Console Convergence | doku/impl | Import-Konsole, Konvergenz | `docs/16_` | nicht eindeutig im Index ermittelt |
| 5 | Visual Meaning Engine | doku/impl | Visuelle Bedeutungsschicht | `docs/17_` | nicht eindeutig im Index ermittelt |
| 6 | Replay Explanation Provenance | doku/impl | Replay, Erklärung, Herkunft | `docs/18_` | nicht eindeutig im Index ermittelt |
| 7 | Worldview Graph Model | doku/impl | Weltbild-Graph | `docs/19_` | nicht eindeutig im Index ermittelt |
| 8 | Flarum Origin Archive | doku/impl | Flarum-Ursprungsarchiv | `docs/20_` | nicht eindeutig im Index ermittelt |
| 9 | Clean Start Decision Engine | doku/impl | Sauberer Neustart, Entscheidungsmaschine | `docs/21_` | nicht eindeutig im Index ermittelt |
| 10 | Memory Candidate Dossier | doku/impl | Gedächtnis-Kandidaten | `docs/22_` | nicht eindeutig im Index ermittelt |
| 11 | Entity Continuity Dossier | doku/impl | Wesen-Kontinuität | `docs/23_` | nicht eindeutig im Index ermittelt |
| 12 | World Start Readiness Pack | doku/impl | Startbereitschaft der Welt | `docs/24_` | nicht eindeutig im Index ermittelt |
| 13 | World Inspection Export | implementiert | Inspektion, Export, Navigation | `kernel/src/` | `2672f33` (gebündelt) |
| 14 | Static Worldview Preview | implementiert | Statische Weltbild-Vorschau | `kernel/src/` | `cb5c6b5` |
| 15 | First WorldBlick CLI | implementiert | WorldBlick CLI, erste Sichtfenster | `kernel/src/` | `cb5c6b5` |
| 16 | Organ Dock Blueprints | implementiert | Organ-Dock, Future-Blueprints, Registry | `kernel/src/` | `7825bb8` |
| 17 | Admin Feature Control | implementiert | Operator Control Plane, Feature Gates | `kernel/src/` | `76e4193` |
| 18 | Diskursarchäologische Suche | implementiert | Deep Search, Diskurs-Archäologie | `kernel/src/` | `d1e7fe8` |
| 19 | World Run Control Locks | implementiert | Run-Steuerung, Locks, Gates, Audit | `kernel/src/` | `66bae16` |
| 20 | Global Governance | implementiert | Governance-Matrix, Approval-Workflow | `kernel/src/` | `459cf09` |
| 21 | Build Discipline | doku (aktiv) | Ring-Index, Handoff, Teststrategie, Token-Disziplin | `docs/33_`, `RING_INDEX.md` | noch kein Commit |

---

## Aktuelle Sperren

- Keine Organe aktivieren
- Keine KompOase / Tamagotchi / Resonanzurlaub bauen
- Kein AI-Subsystem
- Kein Postgres
- Keine UI — außer spätere Erlebnis-/Prozesskamera (explizit geplant, noch nicht begonnen)
- FeatureSlots bleiben deaktiviert
- Governance / GlobalLock / Search / Admin sind Kontrollschichten, keine Runtime

---

## Nächste Planungsanker

1. **Ring 21 Doku abgeschlossen** — `HANDOFF_CAPSULE.md` vorhanden; nach `/clear`, Accountwechsel oder neuer Claude-Code-Session zuerst lesen
2. **Prozesskamera / Weltkamera** — nächster Erlebnisstrang nach Ring 21; alle Systemwesen (GENI, dak+gord, Systemweiser, namelessAI-Flarum-Wesen) als beobachtbare Prozesskörper
3. **Danach entscheiden:** Build-Disziplin-Code (ring-index.ts, ring_manifest.json) oder direkt Erlebnis-Preview

---

## Offene Entscheidungen (Ring 21)

| ID | Frage | Status |
|---|---|---|
| A | Ring 21 nur Doku oder auch Code? | **Entschieden: Doku zuerst** |
| B | Zentrale RING_INDEX.md? | **Entschieden: ja (diese Datei)** |
| C | Maschinenlesbare ring_manifest.json? | offen |
| D | HANDOFF_CAPSULE.md für Session-Einstieg? | **Entschieden: vorhanden** |
| E | package.json Testgruppen (test:core etc.)? | offen |
| F | Feste max. Berichtslänge (15 Zeilen)? | offen |
| G | Testbudget-Schätzung pro Ring? | offen |
| H | Build-Disziplin-Code oder Erlebnis zuerst? | **Entschieden: erst Doku fertig** |
