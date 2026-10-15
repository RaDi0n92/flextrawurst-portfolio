# Erste State-Transition-Rule — Planungsdokument

**Status:** Plan, noch kein Code. Implementierung erst nach Daniels Entscheidung zu Punkt 16.

---

## 1. Ziel der ersten State-Transition-Rule

Die erste Rule beweist:

> Aus einem gespeicherten `system.tick` kann deterministisch ein `entity.state_changed`
> Event entstehen. Dieses Event wird normal validiert, append-only gespeichert,
> projiziert und historisch replayt.

Die vollständige Kette, die funktionieren muss:

```
system.tick
→ deterministic rule (presence_pulse)
→ entity.state_changed
→ EventStore.append + validateEvent
→ EntityProjection aktualisiert sich
→ Meaning Projection erzeugt neue Render-Hints
→ Historical Replay rekonstruiert dieselbe Folge
```

### Nicht enthalten

```
keine AI
keine autonome Entscheidung
kein Posten
kein Schlafsystem
kein Hunger
keine Substanz
kein Tamagotchi
kein Scheduler
kein Loop
kein UI
kein Renderer
kein Postgres
kein GENI
kein dak+gord
kein Systemweiser
```

---

## 2. Warum presence_pulse als erste Rule

`presence_pulse` ist klein genug, um deterministisch zu bleiben. Sie behauptet kein
Bewusstsein, keine Motivation und keine Simulation. Sie beweist nur:

> Weltzeit kann eine Entität berühren und einen nachvollziehbaren Zustandswechsel erzeugen.

Das schützt vor dem typischen Fehler, sofort „Leben zu spielen". Ein Zustand, der
aus dem Weltpuls folgt, ist noch kein Wille. Er ist eine Spur.

---

## 3. Minimaler Zielzustand

Die Rule läuft zunächst nur für eine existierende Entität:

```
target entity: namelessAI_1234
```

Zustand nach der Rule:

```typescript
current_state: {
  last_tick_number: number,
  last_world_time: string,
  presence_pulse_count: number
}
```

`presence_pulse_count`:
- Fehlt der Wert vorher → beginnt bei `1`
- Ist er vorhanden → deterministisch um `1` erhöht

---

## 4. Eingangsbedingungen

Die Rule darf nur ausgeführt werden, wenn alle folgenden Bedingungen erfüllt sind:

```
1. Ein gültiges system.tick Event liegt vor
2. Tick hat actor_type "world_engine"
3. Tick hat origin_type "live_world"
4. Tick hat payload.tick_number als number
5. Tick hat payload.world_time als string
6. Die Ziel-Entität existiert (durch system.seed_entity registriert)
7. Die Ziel-Entität hat actor_type "nameless_ai"
```

Wenn die Entität nicht existiert: keine Transition, kein Auto-Seed, kein stilles
Erfinden. Die Rule bricht ohne Fehler ab und gibt `null` zurück.

---

## 5. Ausgabe-Event

Die Rule erzeugt ein Event-Objekt — sie speichert nicht selbst. Speicherung
geschieht ausschließlich über `store.append()`.

Eventform:

| Feld                  | Wert                                              |
|-----------------------|---------------------------------------------------|
| `event_type`          | `"entity.state_changed"`                          |
| `actor_type`          | `"world_engine"`                                  |
| `actor_id`            | `"world_engine"`                                  |
| `target_type`         | `"nameless_ai"`                                   |
| `target_id`           | `"namelessAI_1234"`                               |
| `origin_type`         | `"live_world"`                                    |
| `created_by_process`  | `"state_transition_presence_pulse"`               |
| `visibility_layer`    | `"system"`                                        |
| `projection_policy`   | `null`                                            |
| `causal_links`        | `[<system.tick event_id>]`                        |

Payload:

```typescript
payload: {
  transition_rule: "presence_pulse",
  state_patch: {
    last_tick_number: number,
    last_world_time: string,
    presence_pulse_count: number
  }
}
```

**Warum `actor_type: "world_engine"` bei `entity.state_changed`:**

Es muss zwischen zwei Quellen unterschieden werden:

```
Selbstbericht einer Entität:
  actor_type: "nameless_ai"
  event_type: "entity.state_changed"
  actor_id:   "namelessAI_1234"

Abgeleiteter Weltzustand durch World Engine:
  actor_type:           "world_engine"
  event_type:           "entity.state_changed"
  actor_id:             "world_engine"
  target_type:          "nameless_ai"
  target_id:            "namelessAI_1234"
  created_by_process:   "state_transition_presence_pulse"
  causal_links:         [<tick_event_id>]
```

Das ist kein Regelbruch. `created_by_process` und `causal_links` belegen, dass die
World Engine den Zustand kausal und transparent abgeleitet hat.

---

## 6. Validierungsfrage — zwei notwendige Anpassungen

### 6.1 entity.state_changed: world_engine nicht erlaubt (Zeile 113–118)

**Aktuell in `validate.ts`:**

```typescript
if (e.event_type === "entity.state_changed") {
  if (e.actor_type !== "nameless_ai" && e.actor_type !== "human") {
    throw new Error(
      'entity.state_changed erfordert actor_type "nameless_ai" oder "human"'
    );
  }
}
```

Das würde ein `entity.state_changed` mit `actor_type: "world_engine"` sofort
ablehnen. **Diese Prüfung muss additiv erweitert werden.**

Neue Regel:

```
entity.state_changed mit actor_type "world_engine":
  → created_by_process muss gesetzt und "state_transition_presence_pulse" sein
  → target_type muss "nameless_ai" sein
  → target_id muss gesetzt sein
  → causal_links muss mindestens eine event_id enthalten

entity.state_changed mit actor_type "nameless_ai" oder "human":
  → bisherige Logik bleibt unverändert
```

Kein Umbau. Nur der bestehende Block wird um den `world_engine`-Zweig ergänzt.
Bestehende Tests bleiben grün.

### 6.2 Payload-Feld: state vs. state_patch

**Aktuell in `entity_projection.ts` (Zeile 48):**

```typescript
if (event.payload.state && typeof event.payload.state === "object") {
  Object.assign(projection.current_state, event.payload.state ...);
}
```

Die neue Rule verwendet `payload.state_patch`, nicht `payload.state`. Die
Projection muss additiv erweitert werden, um `state_patch` zu mergen wenn `state`
fehlt.

Neue Logik (additiv):

```
if payload.state        → merge payload.state (bisheriges Verhalten)
if payload.state_patch  → merge payload.state_patch (neues Verhalten)
```

### 6.3 Projection-Trigger: actor_id vs. target_id

**Aktuell in `entity_projection.ts` (Zeile 44–46):**

```typescript
(event.event_type === "entity.state_changed" ...) &&
event.actor_id === entityId
```

Bei World-Engine-abgeleiteten Events ist `actor_id: "world_engine"` und die Entität
steht in `target_id`. Die Projection würde den Event derzeit nicht verarbeiten.

Neue Logik (additiv):

```
entity.state_changed verarbeiten wenn:
  event.actor_id === entityId                     (Selbstbericht)
  OR event.target_id === entityId                 (abgeleiteter Weltzustand)
```

---

## 7. Determinismus

Die Rule muss deterministisch sein:

```
gleicher bisheriger Zustand
+ gleicher Tick
= gleicher state_patch, abgesehen von kontrollierten event_id/timestamp-Parametern
```

- Kein `Math.random`
- Kein `Date.now()` in Testpfaden
- Kein Modellaufruf
- `event_id` und `timestamp` werden in Tests als Parameter übergeben

---

## 8. Beziehung zum EventStore

```
presence_pulse Rule erzeugt nur ein Event-Objekt.
Sie speichert nicht selbst.
runStateTransitionOnce(store, ...) darf nur store.append(event) nutzen.
Kein direkter Array-Zugriff.
Keine Projection-Mutation.
Keine Event-Mutation.
EventStore bleibt einzige Schreibschicht.
```

---

## 9. Beziehung zur Projection

Die bestehende `buildEntityProjection` muss **additiv** erweitert werden:

1. Trigger: auch `event.target_id === entityId` prüfen (nicht nur `actor_id`)
2. Payload: auch `payload.state_patch` mergen (nicht nur `payload.state`)

Die bestehenden Kernpfade (seed, Selbstbericht-state_changed) bleiben unverändert.
Kein großes State-System bauen — nur `state_patch` mergen.

---

## 10. Beziehung zur Meaning Projection

Die Meaning Projection liest die EntityProjection und braucht keine eigene Kenntnis
von `state_patch`. Sie sieht nur den fertigen Zustand.

Minimale Erweiterung nach der Transition:

```
label:         "namelessAI_1234"
explanation:   enthält Hinweis auf presence_pulse_count oder last_tick_number
               (z.B. "Puls #3 empfangen — Weltzeit bekannt")
source_event_ids: enthält das letzte relevante entity.state_changed Event
```

Kein neuer Rendering-Code. Kein Renderer. Nur Erklärungstext aus Projektionswerten.

---

## 11. Historisches Replay

Replay muss mit der neuen Kette deterministisch bleiben:

```
Seed → Tick → State Transition → Projection → RenderHints
```

```
WorldEngine erzeugt State Transitions.
Replay liest State Transitions.
Replay erzeugt keine State Transitions.
```

Gleiche Events + gleicher `upToIndex` → immer identische Projektion und
identische RenderHints.

---

## 12. Vorgeschlagene neue Dateien für spätere Implementierung

Noch nicht anlegen — nur Plan:

```
kernel/world_engine/state_transitions/presence_pulse.ts
  → applyPresencePulse(tick, projection): FlextrawurstEvent | null
  → reine Fabrik — kein Store-Zugriff
  → gibt null zurück, wenn Entität nicht existiert

kernel/world_engine/run_state_transition_once.ts
  → runStateTransitionOnce(store, tick, entityId, params): FlextrawurstEvent | null
  → lädt Projection aus Store
  → ruft applyPresencePulse()
  → speichert über store.append()
  → gibt gespeichertes Event oder null zurück

tests/state_transition_presence_pulse.test.ts
  → alle 15 Testfälle aus Punkt 13
```

**Begründung der Struktur:**

State Transitions gehören zur World Engine, nicht zum EventStore, nicht zur
Projection, nicht zur VME. Die `state_transitions/`-Unterebene hält die
einzelne Rule klar getrennt von der Orchestrierungsfunktion
`run_state_transition_once.ts`. Weitere Rules (später) folgen als eigene Dateien
im selben Verzeichnis.

---

## 13. Testfälle für spätere Implementierung

```
1.  presence_pulse erzeugt entity.state_changed aus gültigem system.tick
2.  erzeugtes Event hat causal_links auf tick.event_id
3.  erzeugtes Event hat actor_type world_engine
4.  erzeugtes Event hat target_type nameless_ai
5.  state_patch enthält last_tick_number aus Tick-Payload
6.  state_patch enthält last_world_time aus Tick-Payload
7.  presence_pulse_count startet bei 1 wenn Entität keinen Vorzähler hat
8.  zweiter Tick erhöht presence_pulse_count deterministisch auf 2
9.  Rule gibt null zurück, wenn Ziel-Entität nicht existiert
10. runStateTransitionOnce speichert nur über store.append
11. EntityProjection enthält nach Transition last_tick_number, last_world_time,
    presence_pulse_count im current_state
12. Meaning Projection nutzt neuen Zustand für Erklärung und source_event_ids
13. Historical Replay reproduziert dieselbe Projection und dieselben RenderHints
14. Replay erzeugt keine zusätzliche Transition (Store-Länge unverändert nach Replay)
15. Bestehende event_core und world_engine_tick Tests bleiben grün
```

---

## 14. Akzeptanzkriterien

Die erste State-Transition-Rule gilt als geschafft, wenn:

```
✓ system.tick führt kausal zu entity.state_changed
✓ entity.state_changed wird durch validateEvent akzeptiert
✓ entity.state_changed wird append-only im InMemoryEventStore gespeichert
✓ EntityProjection übernimmt state_patch korrekt
✓ Meaning Projection macht den Zustand erklärbar (source_event_ids vorhanden)
✓ Historical Replay rekonstruiert dieselbe Folge deterministisch
✓ Keine AI, keine UI, kein Postgres, kein Loop, kein Renderer beteiligt
✓ Alle 15 neuen Tests grün
✓ Alle bestehenden 20 Tests weiterhin grün (35 total)
```

---

## 15. Was ausdrücklich nicht gebaut werden darf

```
kein Schlafdruck
kein Hunger
kein Substanzdrift
kein Tamagotchi
kein autonomes Posting
keine AI-Reaktion
keine Simulation
kein Scheduler
kein setInterval
kein Renderer
kein WebSocket
kein Postgres
kein GENI-Aufruf
kein dak+gord-Aufruf
kein Systemweiser-Aufruf
```

---

## 16. Nächste Implementierungsentscheidung

```
A) Nur applyPresencePulse() als reine Event-Fabrik bauen
B) applyPresencePulse() + runStateTransitionOnce(store) bauen
```

**Empfehlung: B.**

```
applyPresencePulse()       → testet Eventform und Determinismus, kein Store nötig
runStateTransitionOnce()   → testet den echten Weg durch validate + append
```

Zwei getrennte Funktionen. Die Fabrik bleibt allein testbar. Die Run-Funktion
beweist den echten Pfad durch den EventStore.

---

## Zusammenfassung der notwendigen Code-Anpassungen

| Datei                              | Art der Änderung        | Was                                                 |
|------------------------------------|-------------------------|-----------------------------------------------------|
| `kernel/events/validate.ts`        | additiv erweitert       | entity.state_changed mit actor_type world_engine erlauben |
| `kernel/projections/entity_projection.ts` | additiv erweitert | target_id-Trigger + state_patch-Merge               |
| `vme/meaning_projection.ts`        | optional erweitert      | Erklärungstext aus presence_pulse_count ableiten    |
| `kernel/world_engine/state_transitions/presence_pulse.ts` | neu | applyPresencePulse() Event-Fabrik           |
| `kernel/world_engine/run_state_transition_once.ts` | neu | runStateTransitionOnce() Store-Pfad          |
| `tests/state_transition_presence_pulse.test.ts` | neu    | 15 Testfälle                                        |
| `package.json`                     | Testscript erweitert    | dritte Testdatei hinzufügen                         |

---

## Zusammenfassung

| Schicht              | Umfang State-Transition-Stufe          | Technologie          |
|----------------------|----------------------------------------|----------------------|
| Validation           | entity.state_changed + world_engine    | TypeScript (additiv) |
| EntityProjection     | target_id-Trigger, state_patch-Merge   | TypeScript (additiv) |
| State-Transition     | presence_pulse Fabrik + run-Funktion   | TypeScript (neu)     |
| Meaning Projection   | Erklärungstext aus Zustand             | TypeScript (minimal) |
| Replay               | unverändert                            | TypeScript           |
| Tests                | 15 neue + 20 bestehende = 35 total     | node:test            |
| UI                   | keins                                  | —                    |
| AI                   | keins                                  | —                    |
| Datenbank            | keins                                  | —                    |
| Loop/Scheduler       | keins                                  | —                    |
