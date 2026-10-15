---
autor: claude bei Daniels VPS
datum: 2026-10-01
status: Entwurf zur Abnahme durch Daniel
herkunft: `PLAN.md` G04 (»Fertig, wenn«), `ANFORDERUNGEN.md` R017–R019, `augen_haende_bridge/tests/evidence/PLAN_G04_TERMINAL_PARITAET_EVIDENCE.md`
---

# Abnahmeprotokoll G04 — Original-Terminal spiegeln und bedienen (Version 0.7.0-g02)

Zeichen: **belegt** (Test gegen echten Prozess oder Referenz), **teilweise**, **offen**. Alle Läufe auf dem VPS; nativ bei Daniel ist die Wiederaufnahme noch nicht gelaufen.

| Forderung aus G04 | Stand | Beleg oder Lücke |
|---|---|---|
| Sessionidentität geprüft | belegt | `pid` und `gestartet` in der Terminalliste; die Bridge erkennt einen anderen Prozess unter derselben ID; echter Server: vor und nach dem Wiederverbinden gleiche ID, gleicher Prozess, gleiche Startzeit. |
| Original- und Overlayausgabe verglichen | belegt (Modell) | 18 Referenzfälle nach VT100/xterm mit von Hand geschriebener Erwartung; Wiederaufnahme baut Zellen, Cursor und Verlauf identisch wieder auf. Die GDI-Darstellung selbst ist nicht gegen ein Referenzbild geprüft. |
| ANSI, Unicode, Cursor, Scrollback, Alternate Screen, Resize | belegt | Referenzfälle plus Modelltests. Gefunden und behoben: DEC-Linienzeichensatz (mc, dialog, ncurses). |
| Marker, Eingaben und Sondertasten genau einmal im richtigen Ziel | belegt | Echtes PTY, Rohmodus-Empfänger: 20 Sondertasten und Zeichen genau nach xterm, genau einmal, in Reihenfolge, keine Nachlieferung; 50 KB Einfügen vollständig. |
| Reconnect erzeugt weder neue Shell noch doppelte Eingaben | belegt (VPS-Seite) | Echter Server-Prozess und echter Client: eine Sitzung, derselbe Prozess, Eingabe kommt einmal an, alte Eingabe wird nicht erneut gesendet. Nativ in der Oberfläche noch nicht gelaufen. |
| Eingabeproben treffen den laufenden Agenten nicht als Shell-Befehl | belegt | Der Empfänger ist ein eigenes Rohmodus-Programm, die Proben laufen nie gegen einen Agenten oder eine Shell. |
| Der ursprüngliche Prozess wird für den Test nicht beendet; kein Textspiegel statt Sitzung | belegt | Die Wiederaufnahme spielt nur Ausgabe ein und berührt die Sitzung nicht (Test: drei Wiederaufnahmen hintereinander, Prozess und Zustand unverändert, Eingabe weiter möglich). |

**Offen / Ausnahmen:**
1. **Nativer Nachweis** der Wiederaufnahme in der echten Oberfläche (Bridge schließen, neu starten, Terminal ist gefüllt). Voraussetzung: `systemctl restart bridge-relay` auf dem Host (neuer Relay kennt `terminal_attach`) und Paket 0.7.0.
2. Die Wiederaufnahme zeigt nur die **letzten 512 KB**; ältere Ausgabe fehlt.
3. R018 verlangt auch Vollbild-Terminalprogramme: belegt über Alternate-Screen-Fälle; ein echtes Vollbildprogramm (z. B. `top`, `mc`) im Bridge-Terminal bei Daniel ist nicht gesondert geprüft.

## Entscheidung (Daniel)

- G04: ☐ abgenommen ☐ abgenommen mit Ausnahme (siehe oben) ☐ erst nach dem nativen Nachweis
