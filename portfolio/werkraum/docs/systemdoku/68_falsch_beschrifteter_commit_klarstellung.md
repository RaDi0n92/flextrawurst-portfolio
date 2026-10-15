# 68 — Klarstellung zu Commit 3956e2275a

2026-09-17. Commit `3956e2275a` ("backup: vor Anlage neuer Wesen-Einzug-Entscheidungsvault",
16.09. 22:40) enthält neben dem angekündigten Inhalt auch einen unfertigen, laufenden
Umbau an `welt/groups_api.py` und `welt/api.py` (JWT-Zentralisierung, Self-Join-Fixes,
Ampel-Logik) — das ist ChatGPTs Arbeit am parallel laufenden Flextrawurst-Einzugsreife-Audit
(`flextrawurst-audit/`), nicht meine.

Ursache: `git add -A` vor dem Commit hat versehentlich ChatGPTs zu dem Zeitpunkt bereits
dirty stehende Dateien mit eingesammelt. Nichts ist verloren oder überschrieben — der
Stand ist vollständig im Commit enthalten, nur unter einer Message, die nichts damit zu
tun hat.

Kein Rückgängigmachen, kein History-Rewrite (Commit ist bereits geteilte Historie).
Diese Notiz ist die Korrektur der Zuordnung, nicht des Inhalts.

`welt/api.py` selbst ist Stand dieser Notiz weiterhin ungesichert (uncommitted) —
ChatGPTs laufende Arbeit, bewusst nicht angefasst.
