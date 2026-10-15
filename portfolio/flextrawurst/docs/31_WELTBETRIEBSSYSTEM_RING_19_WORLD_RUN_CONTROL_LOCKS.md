# Ring 19 — World Run Control + System Locks + Freeze/Pause/Stop

Ring 19 baut World Run Control.
Keine echte Runtime-Ausführung.
Kein Scheduler.
Kein Daemon.
Kein setInterval.
Keine UI.
Keine AI.
Kein Postgres.

Ring 19 definiert:
- Laufzustände (WorldRunStatus)
- Kontrollbefehle (WorldRunTransitionType)
- Freeze/Pause/Stop/Lock-Semantik
- Approval-Anforderungen über bestehende AdminActor/Permissions
- Auditierbarkeit (WorldRunAudit, append-only)
- Suchbarkeit (Search Integration worldrun_state/audit/snapshot)

## Schutzsatz

Pause-Modell ≠ laufender Prozess.
Freeze-Modell ≠ echter Daemon-Stopp.
Stop-Modell ≠ Datenlöschung.
Lock-Modell ≠ Feature-Implementierung.
Control Snapshot ≠ UI.

## Laufzustände

not_started → running → paused → running (resume)
running → frozen
paused → frozen
frozen → stopped (kein direktes resume aus frozen)
running → stopped
paused → stopped
locked blockiert start/resume

## Gates

- pause → worldrun.pause
- resume → worldrun.resume
- freeze → worldrun.freeze
- stop → worldrun.stop
- start → worldrun.resume
- lock → worldrun.freeze
- unlock → worldrun.resume

observer: nur worldrun.view, keine Kontrolle
daniel_root: alle Kontrollen
system_process: nur worldrun.view, keine Kontrolle

## Komponenten

- worldrun_state.ts — Zustandsdaten
- worldrun_transition.ts — Übergänge deterministisch
- worldrun_gate.ts — Permission-Prüfung
- worldrun_command_handler.ts — CommandIntent-Handler
- worldrun_control_snapshot.ts — Read-only Snapshot
- worldrun_audit.ts — Append-only Audit
