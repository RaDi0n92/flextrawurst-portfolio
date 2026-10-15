# Weltbetriebssystem Ring 1 — Planungsdokument

**Status:** Plan + Implementierung in einem Durchlauf (Commit 95ee64f als Basis).

---

## Ziel

Der Weltkern erhält eine erste Integritäts-, Zeitlinien-, Query- und Weltkamera-Datenschicht.
Diese Schicht erzeugt keine Weltbewegung, sondern macht vorhandene Weltbewegung prüfbar und später erlebbar.

Welt läuft
→ Welt kann sich rekonstruieren
→ Welt kann sich prüfen
→ Welt kann sich als Kamera-Modell vorbereiten

## Neue Bausteine

```
kernel/integrity/world_integrity.ts     → WorldIntegrityReport + checkWorldIntegrity
kernel/timeline/world_timeline.ts       → WorldTimeline + buildWorldTimeline
kernel/queries/event_queries.ts         → findEventsByType, findEntityTrace, findCausalChildren, …
kernel/world_camera/world_camera_model.ts → WorldCameraModel + buildWorldCameraModel
kernel/audit/world_audit.ts             → WorldAudit + buildWorldAudit
tests/world_operating_system_ring_1.test.ts
```

## Schutzgrenzen

Keine AI. Kein UI. Kein Renderer. Kein Postgres. Kein Scheduler. Kein setInterval.
Kein Daemon. Keine WebSockets. Keine API.

Integrity liest nur. Keine Mutation. Keine Reparaturautomatik.
Timeline ist kein UI. Nur Datenmodell.
CameraModel ist kein Renderer. Nur renderer-offenes Datenmodell.
WorldAudit schreibt keine Events.
