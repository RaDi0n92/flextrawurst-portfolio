# Erster Event-Core — Implementierungsplan

**Status:** Plan, noch kein Code. Entscheidungen eingetragen — implementierungsbereit.

---

## 1. Ziel

Der erste Event-Core beweist exakt einen Satz:

> Ein Event kann erzeugt, validiert, append-only gespeichert, projiziert und
> historisch replayt werden.

Nichts weiter.

### Nicht enthalten

```
kein Feed, keine Website, kein Login
keine AI-Texterzeugung
keine echte GENI-Anbindung
kein Flarum-Import
keine Substanzen, kein Tamagotchi
kein 3D-Renderer, kein UI
keine Social-App
keine Datenbank-Migration (außer Daniels Entscheidung in Punkt 12)
```

---

## 2. Minimaler Vertikalschnitt

Die erste Kette, die vollständig funktionieren muss:

```
1. manual_seed → namelessAI_1234 wird registriert
                  (origin_type: "manual_seed", created_by_process: "seed_script")

2. system.tick  → Weltzeit-Takt
                  (actor_type: "world_engine")

3. entity.state_changed → Zustand von namelessAI_1234 ändert sich
                           (actor_type: "nameless_ai", actor_id: "namelessAI_1234")

4. EntityProjection  → wird aus den drei Events neu berechnet
                        (namelessAI_1234 existiert, Zustand bekannt)

5. Meaning Projection → erzeugt RenderHints aus Projektion
                          (kein UI, nur JSON)

6. Historisches Replay → alle Events von 0 bis N abgespielt
                           → Projektion entsteht deterministisch identisch
                           → RenderHints entstehen deterministisch identisch
```

Dieser Schnitt ist abgeschlossen, wenn Schritt 1–6 vollständig und automatisch
testbar sind. Kein manuelles Klicken, kein Browser.

---

## 3. Erlaubte Eventtypen für den ersten Core

Nur diese vier:

| Typ                    | actor_type       | Bedeutung                                       |
|------------------------|------------------|-------------------------------------------------|
| `system.seed_entity`   | `world_engine`   | Entität wird initial registriert                |
| `system.tick`          | `world_engine`   | regulärer Weltzeit-Takt                         |
| `entity.state_changed` | `nameless_ai`    | innerer Zustand einer Entität hat sich geändert |
| `entity.post_stub`     | `nameless_ai`    | testbarer Artefakt-Event mit Herkunft + Zustand |

`entity.post_stub` ist kein echter öffentlicher Post. Er ist ein Platzhalter, der
zeigt: dieser Akteur, aus diesem Zustand heraus, hat etwas erzeugt. Kein AI-Text.

### Eventname-Sprache — entschieden

**Technische Eventnamen im Code: Englisch.**
**Domänenbegriffe in Docs, UI, Erklärungen: Deutsch erlaubt und erwünscht.**

Schichtentrennung:

```
Technischer Vertrag (Code, TypeScript, Tests, API): Englisch
  → system.seed_entity, system.tick, entity.state_changed, entity.post_stub

Weltbedeutung, UI-Text, Dokumentationssprache: Deutsch
  → Labels, Erklärungen, Weltlogik, Produktsprache
```

Begründung: Englische technische Eventnamen bleiben einfacher für TypeScript,
Tests, Imports, spätere API und externe Integrationen. Deutsch bleibt die
sichtbare Flextrawurst-Sprache. Keine Verflachung — Schichtentrennung.

---

## 4. Maßgebliches Event-Interface (TypeScript-Vertrag)

Noch keine `.ts`-Datei. Nur die Definition für den Plan.

```typescript
interface FlextrawurstEvent {
  event_id:            string;          // UUID v7
  event_type:          string;          // aus erlaubten Typen

  actor_type:          "nameless_ai" | "human" | "system_layer" | "world_engine" | "policy_engine";
  actor_id:            string;

  target_type:         "nameless_ai" | "human" | "system_layer" | "raum" | "artefakt" | "graph" | "event" | null;
  target_id:           string | null;

  timestamp:           string;          // ISO 8601 mit Nanosekunden-Genauigkeit
  payload:             Record<string, unknown>;
  kontext:             string | null;   // RaumID

  causal_links:        string[];        // EventIDs früherer Events

  origin_type:         "live_world" | "flarum_import" | "chat_import" | "obsidian_import" | "manual_seed" | "system_analysis" | "simulation";
  created_by_process:  string | null;

  visibility_layer:    "public" | "system" | "internal";
  projection_policy:   string | null;   // PolicyID
}
```

**Nicht vorhanden:** `source`, `redaction_state`.

---

## 5. Validierungsregeln

Der Validator prüft ein Event-Objekt vor dem Append. Wirft Fehler — kein stilles
Schlucken.

```
event_id:
  → muss gesetzt sein
  → muss eindeutig im EventStore sein

event_type:
  → muss in der Liste erlaubter Typen stehen
  → erster Core: ["system.seed_entity", "system.tick",
                   "entity.state_changed", "entity.post_stub"]

actor_type:
  → muss einer der fünf erlaubten Werte sein

origin_type:
  → muss einer der erlaubten Werte sein

Schreibrecht-Checks:
  → system.seed_entity: nur actor_type "world_engine" oder origin_type "manual_seed"
  → system.tick:        nur actor_type "world_engine"
  → entity.*:           nur actor_type "nameless_ai" oder "human"
  → policy.*:           nur actor_type "policy_engine"

causal_links:
  → falls gesetzt: alle referenzierten event_ids müssen im EventStore vorhanden sein
  → verhindert Kausalketten in die Zukunft

timestamp:
  → muss parseable ISO 8601 sein
  → darf nicht weit in der Zukunft liegen (Toleranz: 5 Sekunden)
```

Noch keine RBAC, kein Token-System. Nur Typ- und Konsistenzprüfung.

---

## 6. Append-only-Speicher

### Stufe A — In-memory EventStore (erste Implementierung)

```typescript
class InMemoryEventStore {
  private events: FlextrawurstEvent[] = [];

  append(event: FlextrawurstEvent): void   // wirft bei Validierungsfehler
  getAll(): FlextrawurstEvent[]
  getByIndex(from: number, to: number): FlextrawurstEvent[]
  getById(id: string): FlextrawurstEvent | null
}
```

- Kein Löschen, kein Update
- Nur `append` und lesende Methoden
- Neustart verliert den Strom — für den Weltbeweis akzeptabel

### Stufe B — PostgreSQL-Migration (nach dem Weltbeweis)

Bereits vorhandene Infrastruktur:

```
Host:     localhost
DB:       flextrawurst
User:     flex
Password: flexpass (aus server.js bekannt)
```

Schema für Stufe B (noch nicht anlegen):

```sql
CREATE TABLE events (
  event_id            TEXT PRIMARY KEY,
  event_type          TEXT NOT NULL,
  actor_type          TEXT NOT NULL,
  actor_id            TEXT NOT NULL,
  target_type         TEXT,
  target_id           TEXT,
  timestamp           TIMESTAMPTZ NOT NULL,
  payload             JSONB NOT NULL DEFAULT '{}',
  kontext             TEXT,
  causal_links        TEXT[] NOT NULL DEFAULT '{}',
  origin_type         TEXT NOT NULL,
  created_by_process  TEXT,
  visibility_layer    TEXT NOT NULL DEFAULT 'public',
  projection_policy   TEXT
);
-- Kein UPDATE, kein DELETE auf dieser Tabelle.
-- Append via INSERT only.
```

**Entscheidung dazu: Punkt 12.**

---

## 7. EntityProjection

Minimale Projektion für den ersten Core:

```typescript
interface EntityProjection {
  entity_id:       string;        // actor_id der Entität
  actor_type:      "nameless_ai" | "human";
  exists:          boolean;
  last_event_id:   string | null;
  current_state:   Record<string, unknown>;  // z.B. { awake: true, state_level: 0.5 }
  last_tick:       string | null;            // timestamp des letzten system.tick
}
```

Berechnung: Projektion wird aus dem EventStore neu aufgebaut — nicht als separater
Zustand gespeichert. Wegwerfbar. Jederzeit aus dem Strom rekonstruierbar.

Für den ersten Test reicht:

```
namelessAI_1234 existiert: true
namelessAI_1234 current_state.awake: true (nach seed_entity)
letzter system.tick: bekannt
```

---

## 8. Meaning Projection und Render-Hints

Kein Renderer. Nur JSON-Ausgabe.

```typescript
interface RenderHints {
  node_id:           string;
  node_opacity:      number;       // 0.0 – 1.0
  node_pulse_speed:  "none" | "slow" | "normal" | "fast";
  node_layer:        number;       // 0 = physisch, 1 = graph, 2 = traum
  color_temperature: "cool" | "neutral" | "warm" | "hot";
  label:             string;
  explanation:       string;       // Warum diese Hints? Für Debugging.
  source_event_ids:  string[];     // welche Events haben diese Hints erzeugt
}
```

Mapping (Meaning Projection → RenderHints) für den ersten Core:

```
entity existiert + awake: true
  → opacity: 1.0, pulse_speed: "normal", color: "neutral"

entity existiert + awake: false (oder kein state_changed-Event)
  → opacity: 0.3, pulse_speed: "none", color: "cool"

entity noch nicht geseedet
  → opacity: 0.0, pulse_speed: "none"
```

Die Meaning Projection liest die EntityProjection, nicht den Eventstream direkt.

**Kernregel:** Jeder Render-Hint enthält `source_event_ids`. Kein Hint ohne Weltgrund.

---

## 9. Historisches Replay

```
replay(store: EventStore, upToIndex: number): {
  projection: EntityProjection,
  renderHints: RenderHints
}
```

Ablauf:

```
1. Events 0 bis upToIndex aus dem Store lesen
2. Projektion von leerem Zustand aufbauen (apply each event in order)
3. Meaning Projection auf die fertige Projektion anwenden
4. Ergebnis zurückgeben
```

Invariante: Gleicher EventStore + gleicher upToIndex → immer identisches Ergebnis.

Kein AI-Call. Kein HTTP-Request. Keine Randomness. Deterministisch.

Test: Replay zweimal aufrufen — beide Ergebnisse müssen tief identisch sein.

---

## 10. Vorgeschlagene Dateistruktur

Noch keine Dateien anlegen. Nur Plan.

```
kernel/
  events/
    types.ts             ← FlextrawurstEvent Interface + erlaubte Typen
    validate.ts          ← Validator-Funktion
    event_store.ts       ← InMemoryEventStore (Stufe A)
  projections/
    entity_projection.ts ← EntityProjection Interface + Builder-Funktion
  vme/
    meaning_projection.ts ← RenderHints Interface + Mapping-Logik
  replay/
    historical_replay.ts ← replay()-Funktion

tests/
  event_core.test.ts     ← Akzeptanztests (alle 10 Kriterien aus Punkt 11)
```

**Begründung der Pfade:** Die bestehende Ordnerstruktur (`kernel/events/`,
`kernel/projections/`, `vme/`, `tests/`) wurde beim Scaffold angelegt und ist
neutral. Die vorgeschlagenen Dateinamen fügen sich ohne Umbau ein.

`vme/` liegt im Plan auf Kernel-Ebene, nicht unter `frontend/`, weil die
Meaning Projection server-nah ist (→ `03_VISUELLE_GRAMMATIK.md`).

---

## 11. Akzeptanzkriterien

Der erste Event-Core gilt als geschafft, wenn alle 10 Tests grün sind:

```
1.  system.seed_entity für namelessAI_1234 kann erzeugt werden
2.  system.tick kann erzeugt werden
3.  entity.state_changed für namelessAI_1234 kann erzeugt werden
4.  Alle drei Events werden validiert (Typ, actor_type, origin_type, causal_links)
5.  EventStore bleibt append-only (kein delete, kein update möglich)
6.  EntityProjection wird aus dem EventStore korrekt aufgebaut
7.  Meaning Projection erzeugt RenderHints mit gültigen source_event_ids
8.  Historisches Replay mit upToIndex=0 → leere Projektion
9.  Historisches Replay mit upToIndex=2 → vollständige Projektion identisch zu Schritt 6
10. Kein AI-Aufruf, kein HTTP-Request, kein UI in einem der Tests
```

---

## 12. Entscheidung: EventStore-Stufe — getroffen

**Gewählt: A — In-memory EventStore (Stufe A).**

```
→ InMemoryEventStore (Stufe A) für den ersten Event-Core
→ kein DB-Setup, kein Migrations-Risiko
→ Weltbeweis prüft Logik, Validierung, Projektion, Meaning Projection und Replay
→ Weltbeweis prüft noch nicht Infrastruktur, Migration oder DB-Rechte
```

**Postgres: zweite Stufe nach erfolgreichem Weltbeweis.**

Bereits vorhandene Infrastruktur wartet:

```
Host:  localhost
DB:    flextrawurst
User:  flex
```

Sie wird für den ersten Event-Core nicht benutzt. Wenn Schema und Validierung
sitzen, ist der Store per Interface-Tausch austauschbar — ohne Logik-Änderung.

---

## Zusammenfassung

| Schicht             | Umfang erster Core        | Technologie        |
|---------------------|---------------------------|--------------------|
| Event-Schema        | 14 Felder, kein source    | TypeScript         |
| Validation          | Typ, Rechte, Kausalität   | TypeScript         |
| EventStore          | append-only, in-memory    | TypeScript (→ PG)  |
| EntityProjection    | exists, state, last_tick  | TypeScript         |
| Meaning Projection  | RenderHints als JSON      | TypeScript         |
| Replay              | deterministisch, kein AI  | TypeScript         |
| Tests               | 10 Akzeptanzkriterien     | test runner (offen)|
| UI                  | keins                     | —                  |
| AI                  | keins                     | —                  |
| Datenbank           | In-memory (Stufe A)       | TypeScript (→ PG)  |
