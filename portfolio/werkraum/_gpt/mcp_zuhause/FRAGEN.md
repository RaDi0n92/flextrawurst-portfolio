# Offene Fragen des VPS-MCP

Statuswerte: aktiv · ruhend · beantwortet · falsch gestellt

## Frage 1: Brauchen lange Suchen einen fortsetzbaren Suchauftrag?

**Entstanden:** 26. Juli 2026

Zeit- und Scanbudgets verhindern Blockaden. Noch offen ist, ob ein abgebrochener Teilstand zusätzlich eine stabile Such-ID und einen Cursor erhalten soll, damit eine spätere Aktion exakt am letzten geprüften Ordner weiterarbeiten kann.

**Status:** aktiv. Für die erste Reparatur nicht erforderlich.

## Frage 2: Braucht der MCP einen Abbruchknopf für laufende Operationen?

**Entstanden:** 26. Juli 2026

Parallele Leser lösen die Session-Geiselhaft, beenden aber keinen unnötig gewordenen langen Suchlauf. Ein späteres `mcp.cancel_operation` müsste Prozess-, Thread- und Subprozessgrenzen sauber behandeln, ohne eine Operation nur kosmetisch als abgebrochen zu markieren.

**Status:** aktiv. Nicht ohne eigenen Sicherheits- und Testkörper bauen.

## Frage 3: Soll Parallelität künftig über Ressourcenklassen statt Werkzeugnamen laufen?

**Entstanden:** 26. Juli 2026

Die erste Fassung verwendet eine explizite Read-only-Allowlist. Langfristig könnten Klassen wie `read_fs`, `read_db`, `render`, `write_fs`, `service_mutation` und `external_network` präziser steuern, welche Aktionen gleichzeitig verträglich sind.

**Status:** ruhend. Die sichere Allowlist ist zunächst absichtlich einfacher.

## Frage 4: Welche installierten Claude-Skills wurden real genutzt?

**Entstanden:** 26. Juli 2026

Die 2.257 Skill-Dateien stammen überwiegend aus wenigen großen Paketen. Noch fehlt ein sauberer Nutzungsindex aus Claude-Sitzungen, Tool-Aufrufen und Logs, der installiert, ausgewählt und angewendet voneinander trennt.

**Status:** aktiv, aber außerhalb dieses MCP-Reparaturrings.
