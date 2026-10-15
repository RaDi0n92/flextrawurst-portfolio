# Ring 22a — Process Model Plan

**Status:** Planungsdokument  
**Typ:** Modellring — kein Daemon, keine UI, kein Live-System  
**Vorgänger:** Ring 22 / `docs/34_...` + `docs/35_...`  
**Stand:** 2026-05-09

---

## 1. Ziel Ring 22a

Ring 22a definiert das Datenmodell, das alle weiteren Prozesskamera-Ringe tragen.

Konkret: TypeScript-Interfaces für `ProcessBody`, `ProcessActivity`, `ProcessTrace`, `ProcessSource`, `ProcessVisibility` — plus ein statisches kanonisches Verzeichnis aller modellierten Prozesskörper.

Kein Export. Kein Renderer. Nur das Modell, auf das 22b–22e aufbauen.

---

## 2. Warum Process Model vor Process Camera Export

Würde 22e (HTML-Export) zuerst kommen, würde die Export-Logik die Modellstruktur treiben.  
Das Ergebnis: ein Format-geprägtes Modell, nicht ein inhaltlich korrektes.

Reihenfolge:  
1. Modell definiert, was ein Prozesskörper ist (22a).  
2. Spurenmodell definiert, was beobachtbar ist (22b).  
3. Snapshot friert einen Moment ein (22c).  
4. Search macht ihn auffindbar (22d).  
5. Export zeigt ihn (22e).

Das Modell ist die Quelle der Wahrheit — nicht der Renderer.

---

## 3. Prozesskörper vs. Entitätsslot vs. Systemschicht

| Typ | Bedeutung | Beispiele |
|---|---|---|
| `ProcessBody` | Laufendes oder modellierbares System mit beobachtbaren Spuren | GENI, dak+gord, WorldRun |
| `EntitySlot` | Platzhalter für Wesen, das noch nicht eingezogen ist; trägt Flarum-Bezug und D3-Markierung | sechs namelessAI-Flarum-Wesen |
| `SystemLayer` | Infrastrukturschicht ohne eigene Wesensidentität | Search, Governance, Audit |

Alle drei erscheinen im Modell als `ProcessBody`-Einträge — unterschieden durch `kind` und `slot_state`.

---

## 4. Kanonische Prozesskörper

Alle Einträge nach Entscheidung C4. Reader/Writer/Runner explizit als `status: future`.

| id | name | kind | status |
|---|---|---|---|
| `geni` | GENI | `perception_layer` | `read-only` |
| `dak_gord` | dak+gord-system | `dialogue_core` | `read-only` |
| `systemweiser` | Systemweiser | `system_layer` | `modelled` |
| `flarum_01`–`flarum_06` | namelessAI-Wesen 1–6 | `entity_slot` | `pre_einzug` |
| `search` | Search | `system_layer` | `read-only` |
| `governance` | Governance | `system_layer` | `read-only` |
| `worldrun` | WorldRun | `system_layer` | `read-only` |
| `worldblick` | Worldblick/Export | `system_layer` | `read-only` |
| `reader` | Reader-Prozesse | `placeholder` | `future` |
| `writer` | Writer-Prozesse | `placeholder` | `future` |
| `runner` | Runner-Prozesse | `placeholder` | `future` |

Gesamt: 14 Einträge (inkl. 6 Flarum-Slots).

---

## 5. ProcessBody-Felder

```typescript
interface ProcessBody {
  id: string                          // kanonischer Bezeichner
  name: string                        // menschenlesbar
  kind: ProcessBodyKind               // s. Enum unten
  status: ProcessStatus               // live | read-only | modelled | future | pre_einzug | blocked | unknown
  slot_state?: SlotState              // nur für entity_slot: pre_einzug | einzug_vollzogen
  visibility: ProcessVisibility       // Zustandsklassifikation nach G
  activity: ProcessActivity           // aktueller Aktivitätsmodus
  traces: ProcessTrace[]              // alle bekannten Spuren
  source: ProcessSource               // Herkunft / Provenienz
  lock_state?: string                 // WorldRun-Lock-Bezug
  governance_state?: string           // Governance-Approval-Bezug
  feature_gate?: string               // Feature-Gate-Bezeichner
  forum_ref?: string                  // Flarum-Thread- oder Post-ID
  file_ref?: string                   // Pfad oder Dateityp-Bezug
  event_ref?: string                  // Event-ID oder Eventstream-Bezug
  search_ref?: string                 // Query oder Ergebnis-ID
  audit_ref?: string                  // Audit-Log-Eintrag-ID
  is_canonical: boolean               // sichtbar in kanonischer Karte?
  ring_origin?: number                // Ring, in dem dieser Körper eingeführt wurde
}
```

**Enums:**

```typescript
type ProcessBodyKind =
  | 'perception_layer'   // GENI
  | 'dialogue_core'      // dak+gord
  | 'entity_slot'        // Flarum-Wesen (D3)
  | 'system_layer'       // Search, Governance, WorldRun, Worldblick
  | 'placeholder'        // Reader, Writer, Runner

type ProcessStatus =
  | 'live'               // läuft, aber noch nicht gemessen
  | 'read-only'          // beobachtbar, nicht steuerbar
  | 'modelled'           // nur statisch modelliert
  | 'future'             // noch nicht gebaut
  | 'pre_einzug'         // Slot vorhanden, Wesen noch nicht eingezogen
  | 'blocked'            // durch Lock/Gate/Governance gesperrt
  | 'unknown'            // kein Datenbezug verfügbar

type SlotState =
  | 'pre_einzug'
  | 'einzug_vollzogen'
```

---

## 6. ProcessActivity-Felder

```typescript
interface ProcessActivity {
  mode: ActivityMode
  visibility_class: VisibilityClass   // nach G: modelliert | abgeleitet | unbekannt
  source_type: SourceType             // woher diese Aktivitätsaussage stammt
  description?: string                // Freitext-Beschreibung (optional)
  timestamp_model?: string            // ISO-Zeitstempel des Modells, nicht Live-Zeit
}

type ActivityMode =
  | 'denkt'
  | 'liest'
  | 'schreibt'
  | 'wartet'
  | 'blockiert'
  | 'prüft'
  | 'exportiert'
  | 'inaktiv'
  | 'simuliert'
```

Wichtig: `timestamp_model` ist der Zeitpunkt, zu dem das Modell diese Aussage trifft — keine Live-Messung.

---

## 7. ProcessTrace-Felder

```typescript
interface ProcessTrace {
  trace_type: TraceType
  body_id: string                     // Rückreferenz auf ProcessBody.id
  ref_id?: string                     // ID im Quellsystem
  source_type: SourceType
  summary?: string
  timestamp_model?: string
}

type TraceType =
  | 'audit'
  | 'search'
  | 'governance'
  | 'worldrun'
  | 'event'
  | 'forum'
  | 'file'
  | 'origin'              // Herkunfts-Spur: Ring, Import, Einzug
```

---

## 8. ProcessSource-Felder

```typescript
interface ProcessSource {
  source_type: SourceType
  location?: string                   // Pfad, Kernel-Modul, URL-Schema
  timestamp_available: boolean        // ob Zeitstempel vorhanden
  notes?: string
}

type SourceType =
  | 'static_model'         // manuell modelliert, kein Datenbezug
  | 'git_history'          // abgeleitet aus Git-Log, Commits, Diffs
  | 'audit_log'            // aus Audit-Trail (kernel/audit)
  | 'governance_log'       // aus Governance-Approval-Log (kernel/governance)
  | 'search_index'         // aus Diskursarchäologie-Index (kernel/search)
  | 'flarum_archive'       // aus importiertem Flarum-Ursprungsarchiv
  | 'file_system'          // abgeleitet aus Datei-Timestamps, Pfaden
  | 'event_log'            // aus Eventstream (kernel/events)
  | 'future_instrument'    // noch nicht vorhanden, muss später instrumentiert werden
```

---

## 9. ProcessVisibility-Felder

```typescript
interface ProcessVisibility {
  class: VisibilityClass
  reason?: string                     // warum diese Klasse zugewiesen
  source_ref?: string                 // Datei/Modul das die Klasse begründet
}

type VisibilityClass =
  | 'gemessen'     // aus laufendem System gelesen — in Ring 22 für keinen Körper
  | 'abgeleitet'   // aus Datei, Git, Audit, Forum berechnet
  | 'modelliert'   // manuell zugewiesen, kein Datenbezug
  | 'unbekannt'    // kein Datenbezug verfügbar
  | 'blockiert'    // durch Lock/Gate/Governance gesperrt
  | 'read-only'    // beobachtbar, nicht veränderbar
  | 'replay'       // aus vergangenem Snapshot rekonstruiert
```

**Regel:** `gemessen` wird in Ring 22a für keinen Prozesskörper gesetzt. Erst nach explizitem Instrumentierungsring freigeben.

---

## 10. Zustandsklassifikation nach G

Jedes Feld, das einen Zustand behauptet, trägt eine `VisibilityClass`.

| Prozesskörper | activity.visibility_class | Begründung |
|---|---|---|
| GENI | `modelliert` | Keine Live-API-Brücke vorhanden |
| dak+gord | `modelliert` | Separates System, keine Event-Kopplung |
| Systemweiser | `modelliert` | Kein laufender Prozess, nur konzeptuell |
| Flarum-Wesen 1–6 | `abgeleitet` | Flarum-Archiv als Quelle vorhanden |
| Search | `abgeleitet` | `kernel/search` vorhanden, Git-History lesbar |
| Governance | `abgeleitet` | `kernel/governance` vorhanden |
| WorldRun | `abgeleitet` | `kernel/worldrun` vorhanden |
| Worldblick/Export | `abgeleitet` | `kernel/worldblick` vorhanden |
| Reader/Writer/Runner | `unbekannt` | Noch nicht gebaut, kein Bezug |

---

## 11. Was in Ring 22a nur modelliert wird

- Alle 14 kanonischen Prozesskörper als statische TypeScript-Objekte
- Alle Felder nach Abschnitten 5–9
- Kanonisches Verzeichnis als exportierter Array `CANONICAL_PROCESS_BODIES`
- Enums und Interfaces in separaten Dateien

Keine Laufzeitlogik. Kein Laden aus externen Quellen. Nur Typen und initiale Werte.

---

## 12. Was ausdrücklich noch nicht gebaut wird

| Nicht in Ring 22a | Warum |
|---|---|
| HTML-Export / Worldblick-Integration | Ring 22e |
| Spurensammlung aus Kernel-Modulen | Ring 22b |
| JSON-Snapshot | Ring 22c |
| Search-Integration | Ring 22d |
| Live-Status-Abfrage | Erst nach Instrumentierungsring |
| GENI-Bridge / dak+gord-Kopplung | Separater späterer Ring |
| Einzug der Flarum-Wesen | Separater Einzugsring |
| UI / Renderer / Dashboard | Nicht in Ring 22 |
| Postgres / Persistenz | Nicht in Ring 22 |
| Daemon / Scheduler / Cron | Nicht in Ring 22 |
| Forum-Import | Ring 4 / bereits abgeschlossen |

---

## 13. Welche bestehenden Kernel-Schichten angebunden werden können

Ring 22a bindet noch nichts an — aber diese Schichten sind für spätere Ringe verfügbar:

| Kernel-Schicht | Pfad | Relevant für |
|---|---|---|
| `worldrun` | `kernel/worldrun/` | lock_state, governance_state, audit_ref |
| `governance` | `kernel/governance/` | governance_state, governance_log |
| `audit` | `kernel/audit/` | audit_ref, TraceType.audit |
| `search` | `kernel/search/` | search_ref, TraceType.search |
| `events` | `kernel/events/` | event_ref, TraceType.event |
| `slots` | `kernel/slots/` | EntitySlot, slot_state |
| `replay` | `kernel/replay/` | VisibilityClass.replay |
| `snapshots` | `kernel/snapshots/` | ProcessSnapshot (Ring 22c) |
| `world_camera` | `kernel/world_camera/` | Einbettung der Kamera |
| `worldblick` | `kernel/worldblick/` | HTML-Export (Ring 22e) |
| `export` | `kernel/export/` | Export-Pipeline (Ring 22e) |
| `features` / `admin` | `kernel/admin/` | feature_gate |
| `entities` | `kernel/entities/` | Bezug zu Entitätsmodell |
| `origin_archive` | `kernel/origin_archive/` | Flarum-Herkunft, flarum_ref |

---

## 14. Minimale Implementierungsdateien

Vorgesehenes Verzeichnis: `kernel/process_model/`

| Datei | Inhalt |
|---|---|
| `types.ts` | Alle Interfaces und Enums (ProcessBody, ProcessActivity, ProcessTrace, ProcessSource, ProcessVisibility, alle type-Aliase) |
| `canonical_bodies.ts` | `CANONICAL_PROCESS_BODIES: ProcessBody[]` — 14 statische Einträge |
| `index.ts` | Re-Export aller Typen und des kanonischen Verzeichnisses |

Keine weiteren Dateien. Keine Logik. Keine Importe aus anderen Kernel-Modulen (um Zirkelabhängigkeiten zu vermeiden — nur primitive Typen).

---

## 15. Teststrategie

Keine 100-Test-Pflicht. Ca. 15–25 gezielte Tests.

| Testbereich | Anzahl | Art |
|---|---|---|
| Feldvollständigkeit: alle 14 Körper haben Pflichtfelder | 6 | Unit |
| Enum-Validierung: `VisibilityClass`, `ActivityMode`, `SourceType` | 5 | Unit |
| Regel: kein Körper hat `visibility.class === 'gemessen'` | 1 | Guard |
| Regel: alle `entity_slot`-Körper haben `slot_state` gesetzt | 1 | Guard |
| Regel: alle `placeholder`-Körper haben `status === 'future'` | 1 | Guard |
| `is_canonical`-Zählung: genau 14 kanonische Einträge | 1 | Unit |
| Spurenstruktur: `ProcessTrace.body_id` referenziert bekannten Körper | 3 | Unit |
| Quellenstruktur: `ProcessSource.source_type` ist gültiger Enum-Wert | 3 | Unit |
| Index-Export: `CANONICAL_PROCESS_BODIES` ist nicht leer | 1 | Smoke |

**Gesamt: ca. 22 Tests.**

Alle Unit-Tests, keine Integration, keine E2E. Testen, was das Modell verspricht — nicht mehr.

---

## 16. Offene Fragen

| Frage | Kontext |
|---|---|
| Sollen die sechs Flarum-Wesen bereits Namen tragen oder `namelessAI_01`–`_06`? | Entscheidung D3 lässt beides zu; Namen erst nach Einzugsritual sinnvoll |
| Soll `ring_origin` Pflichtfeld oder optional sein? | Optional ist schlanker; Pflichtfeld stärkt Provenienz |
| Soll `CANONICAL_PROCESS_BODIES` ein Array oder ein Record/Map sein? | Array einfacher zu iterieren; Map schneller bei ID-Lookup |

---

## Schutzsätze

> Keine Live-Zustände erfinden.  
> Keine Aktivität behaupten, die nicht aus Daten stammt.  
> `gemessen` in Ring 22a für keinen Prozesskörper.  
> Modell ≠ Implementierung.  
> Typen ≠ Logik.  
> Kanon ≠ Einzug.
