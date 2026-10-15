# Deterministische Welt Runtime Pipeline — Planungsdokument

**Status:** Plan + Implementierung in einem Durchlauf (Commit 0ff6658 als Basis).

---

## Ziel

Der Weltkern kann mehrere deterministische Ticks als kontrollierte Laufsequenz ausführen.
Jeder Tick erzeugt für alle existierenden kanonischen Entitäten genau eine presence_pulse-Spur.
Nach jedem Zyklus kann ein WorldSnapshot erzeugt werden.
Historical Replay kann diese Sequenz als ReplayFrames rekonstruieren.

## Kanonische Eventzahlen (6 Entitäten, 3 Cycles)

```
6 system.seed_entity
3 system.tick
18 entity.state_changed (presence_pulse)
= 27 Events
```

## Neue Bausteine

```
kernel/snapshots/world_snapshot.ts         → WorldSnapshot + buildWorldSnapshot
kernel/world_engine/run_world_cycle.ts     → runWorldCycle (ein deterministischer Cycle)
kernel/world_engine/run_world_cycles.ts    → runWorldCycles (mehrere Cycles, kein Scheduler)
kernel/replay/world_replay_frames.ts       → WorldReplayFrame + buildWorldReplayFrames
tests/world_runtime_pipeline.test.ts       → 20+ Tests für den gesamten Ring
```

## Schutzgrenzen

Keine AI. Kein UI. Kein Postgres. Kein Renderer. Kein Scheduler. Kein setInterval.
Kein Daemon. Kein autonomes Posting. Kein while(true). Kein Tamagotchi. Kein GENI.

WorldEngine schreibt Weltzeit.
Replay rekonstruiert Weltzeit.
Replay erzeugt keine Weltzeit.

Snapshot ist abgeleitet, wegwerfbar und aus Events rekonstruierbar.
Snapshot schreibt keine Events.
