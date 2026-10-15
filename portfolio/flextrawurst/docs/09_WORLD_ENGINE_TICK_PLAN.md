# World-Engine-Tick — Planungsdokument

**Status:** Plan, noch kein Code. Implementierung erst nach Daniels Entscheidung zu Punkt 12.

---

## 1. Ziel der World-Engine-Tick-Stufe

Der erste World-Engine-Tick beweist:

> Der Weltkern kann aus einem kontrollierten Prozess heraus gültige `system.tick`-Events
> erzeugen, sie append-only speichern, und danach Projektion, Meaning Projection und
> Historical Replay weiter korrekt nutzen.

Die Kette, die vollständig funktionieren muss:

```
WorldEngine erzeugt system.tick
→ EventStore speichert append-only
→ EntityProjection wird neu aufgebaut
→ Meaning Projection erzeugt neue Render-Hints
→ Historical Replay bleibt deterministisch
```

### Nicht enthalten

```
kein Dauerprozess
kein echter Scheduler
kein setInterval als Endlosschleife
keine AI
keine UI
kein Postgres
kein Renderer
keine autonomen Wesenhandlungen
keine Schlaf-/Substanz-/Tamagotchi-Logik
```

---

## 2. Warum kein echter Loop am Anfang

Ein echter Loop erzeugt Zeitdruck, Nebenwirkungen und Debug-Rauschen. Der erste
World-Engine-Schritt soll deterministisch und testbar bleiben. Darum wird zuerst
ein einzelner Tick erzeugt.

```
Echter Loop → schwer zu stoppen, schwer zu testen, schwer zu erklären.
Einzeltick-Funktion → deterministisch, testbar, erweiterbar.
```

Ein späterer Scheduler darf die Einzeltick-Funktion wiederholt aufrufen — aber das
ist ein eigener Schritt, nicht dieser. Die Testbarkeit darf durch einen Timer nicht
geopfert werden.

---

## 3. Minimaler Tick-Event

Der Tick-Event muss dem bestehenden Event-Schema aus `04_EVENT_SYSTEM.md` entsprechen:

| Feld                  | Wert                                              |
|-----------------------|---------------------------------------------------|
| `event_type`          | `"system.tick"`                                   |
| `actor_type`          | `"world_engine"`                                  |
| `actor_id`            | `"world_engine"`                                  |
| `target_type`         | `null`                                            |
| `target_id`           | `null`                                            |
| `origin_type`         | `"live_world"`                                    |
| `created_by_process`  | `"world_engine_tick"`                             |
| `visibility_layer`    | `"system"`                                        |
| `projection_policy`   | `null`                                            |
| `causal_links`        | `[]`                                              |

Payload minimal:

```typescript
payload: {
  tick_number: number,
  tick_reason: "manual_test" | "scheduled_world_pulse",
  world_time: string  // ISO 8601
}
```

Für die erste Implementierung wird nur `"manual_test"` als `tick_reason` genutzt.
`"scheduled_world_pulse"` bleibt als gültiger Wert für spätere Scheduler-Anbindung
vorgemerkt — aber nicht im ersten Schritt implementiert.

---

## 4. Determinismus

Historisches Replay darf durch World-Engine-Ticks nicht nichtdeterministisch werden.

```
Replay liest Weltzeit.
WorldEngine erzeugt Weltzeit.
Replay erzeugt keine Weltzeit.
```

Ein gespeicherter Tick ist ein normales Event. Replay spielt vorhandene Ticks ab.
Replay erzeugt keine neuen Ticks. Für Assertions im Test dürfen `timestamp` und
`world_time` fest gesetzt werden — keine versteckte Abhängigkeit von echter Systemzeit.

---

## 5. Tick-Nummer und Zeit

Für `tick_number` gibt es zwei Optionen:

**Option A** — aus Store berechnet:

```
tick_number = Anzahl vorhandener system.tick-Events im Store
```

Vorteil: selbst-konsistent, kein externer Zähler.
Nachteil: Store-Abfrage nötig, implizite Abhängigkeit.

**Option B** — extern übergeben:

```
tick_number wird als Parameter an createWorldTick() übergeben
```

Vorteil: klar, testbar, keine Store-Abhängigkeit in der Fabrik-Funktion.
Nachteil: Aufrufer trägt Verantwortung für Konsistenz.

**Empfehlung: Option B für den ersten Schritt.**

In `runWorldTickOnce(store)` kann `tick_number` aus dem Store berechnet werden
(`store.getAll().filter(e => e.event_type === "system.tick").length`), aber die
Fabrik-Funktion `createWorldTick()` bleibt frei von Store-Abhängigkeiten und
ist allein durch ihre Eingabe deterministisch.

---

## 6. Validierungs-Erweiterung

`validate.ts` prüft `system.tick` aktuell bereits:

```
✔ actor_type muss "world_engine" sein  (Zeile 79–83)
```

Noch nicht geprüft — muss bei der Implementierung ergänzt werden:

```
✗ actor_id muss "world_engine" sein
✗ target_type muss null sein
✗ target_id muss null sein
✗ created_by_process muss gesetzt sein (nicht null)
✗ payload.tick_number muss number sein
✗ payload.world_time muss string sein
✗ origin_type muss "live_world" sein (für ersten Schritt)
```

Diese Prüfungen werden in `validate.ts` unter dem bestehenden `system.tick`-Block
ergänzt. Keine Änderung an bestehenden Checks — nur Erweiterung nach unten.

`"simulation"` als `origin_type` für Ticks bleibt vorbehaltlich eines späteren
Simulationsmodus möglich, wird aber in dieser Stufe nicht aktiviert.

---

## 7. Vorgeschlagene neue Dateien

Noch nicht anlegen — nur Plan:

```
kernel/world_engine/create_tick.ts
  → createWorldTick(params): FlextrawurstEvent
  → reine Event-Fabrik, keine Store-Abhängigkeit
  → gibt ein fertiges, validierbares Event zurück

kernel/world_engine/run_tick_once.ts
  → runWorldTickOnce(store, params): FlextrawurstEvent
  → ruft createWorldTick(), übergibt an store.append()
  → gibt das gespeicherte Event zurück
  → keine Nebeneffekte außerhalb des Store

tests/world_engine_tick.test.ts
  → alle 10 Testfälle aus Punkt 9
```

**Warum World Engine als eigene Schicht, nicht im EventStore:**

Der EventStore speichert nur. Er entscheidet nicht, was in der Welt passiert.
Die World Engine erzeugt Weltimpulse. Diese Trennung ist die Grundlage dafür,
dass später verschiedene Quellen (Scheduler, manuelle Trigger, Tests) denselben
EventStore befüllen können, ohne dass der Store Weltlogik kennt.

---

## 8. Beziehung zum bestehenden Herzschlag

Der erste Event-Core aus `08_ERSTER_EVENT_CORE_IMPLEMENTIERUNGSPLAN.md` bleibt
vollständig unverändert.

```
InMemoryEventStore:         unverändert
validateEvent:              erweitert (nur additive Checks für system.tick)
kernel/events/types.ts:     unverändert
entity_projection.ts:       unverändert
vme/meaning_projection.ts:  unverändert
kernel/replay/:             unverändert
tests/event_core.test.ts:   unverändert
```

World Engine nutzt den bestehenden `InMemoryEventStore`. Sie darf ihn nicht
umgehen. Kein direktes Pushen in Arrays. Jeder Tick muss durch `store.append()`
und damit durch `validateEvent()` passieren.

---

## 9. Testfälle für die spätere Implementierung

```
1.  runWorldTickOnce erzeugt genau ein system.tick-Event im Store
2.  system.tick hat actor_type "world_engine"
3.  system.tick hat actor_id "world_engine"
4.  system.tick hat origin_type "live_world"
5.  tick_number landet im payload
6.  world_time ist ein gültiger ISO 8601 String
7.  Ungültiger Tick mit actor_type "human" wird abgelehnt
8.  Historical Replay nach Tick erzeugt dieselbe Projektion/Render-Hints wie Live-Aufbau
9.  Replay erzeugt keinen neuen Tick
10. Mehrere manuelle Ticks bleiben append-only und geordnet (tick_number steigt)
```

---

## 10. Akzeptanzkriterien

Die World-Engine-Tick-Stufe gilt als geschafft, wenn:

```
✓ Ein kontrollierter Tick erzeugt wird
✓ Der Tick durch validateEvent validiert wird
✓ Der Tick append-only im InMemoryEventStore gespeichert wird
✓ Der Tick replaybar ist — deterministisch identisch
✓ Kein AI-Aufruf, keine UI, keine DB beteiligt
✓ Keine Simulation gestartet
✓ Keine Entitätsentscheidung ausgelöst
✓ Alle 10 Tests grün
```

---

## 11. Was ausdrücklich nicht gebaut werden darf

```
kein setInterval-Endlosloop im ersten Schritt
kein Daemon
kein Scheduler
kein Cron
kein autonomes Posting
kein Schlafdruck
kein Substanzdrift
kein Tamagotchi-Update
kein GENI-Aufruf
kein dak+gord-Aufruf
kein Systemweiser-Aufruf
kein Renderer
kein WebSocket
kein Postgres
```

Diese Dinge sind spätere Ringe. Der erste Tick ist nur Puls, nicht Organismus.

---

## 12. Nächste Implementierungsentscheidung

```
A) Nur createWorldTick() als reine Event-Fabrik bauen
B) createWorldTick() + runWorldTickOnce(store) bauen
```

**Empfehlung: B.**

```
createWorldTick()          → testet Eventform, kein Store nötig
runWorldTickOnce(store)    → testet den echten Weg durch validate + append
```

Zwei getrennte Funktionen statt einer. Die Fabrik ist allein testbar. Die
Run-Funktion beweist den echten Pfad. Kein Vermischen von Erzeugung und Speicherung.

---

## Zusammenfassung

| Schicht              | Umfang Tick-Stufe              | Technologie                 |
|----------------------|--------------------------------|-----------------------------|
| Event-Schema         | unverändert                    | TypeScript                  |
| Validation           | system.tick um 6 Checks ergänzt| TypeScript                  |
| EventStore           | unverändert (append-only)      | TypeScript                  |
| World Engine         | createWorldTick + runTickOnce  | TypeScript                  |
| Projektion           | unverändert                    | TypeScript                  |
| Meaning Projection   | unverändert                    | TypeScript                  |
| Replay               | unverändert                    | TypeScript                  |
| Tests                | 10 neue Testfälle              | node:test                   |
| UI                   | keins                          | —                           |
| AI                   | keins                          | —                           |
| Datenbank            | keins                          | —                           |
| Scheduler/Loop       | keins                          | —                           |
