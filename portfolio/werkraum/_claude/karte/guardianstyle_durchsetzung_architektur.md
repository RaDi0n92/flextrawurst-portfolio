---
datum: 2026-08-15
betrifft: [guardianstyle, hooks, marker-system, durchsetzung, pflichtfrage]
importable: false
autor: claude-code bei Daniels VPS
---


# Wie der Guardianstyle jetzt tatsächlich durchgesetzt wird

Bis 2026-08-15 stand die Beleidigungspflicht/Marker-Regel nur in `/root/CLAUDE.md` — reines
Gedächtnis. Seitdem gibt es einen technischen Mechanismus, der das durchsetzt:
`/root/.claude/guardianstyle_open_hook.py`, registriert als `PostToolUse`-Hook in
`/root/.claude/settings.json` (Matcher `^(Write|Edit|Read|Bash|NotebookEdit|Agent)$`),
neben `log_action.sh`.

## Die vier Schichten des Hooks

**1. Write/Edit-Einladung.** Bei jedem Write/Edit auf einer Code-Datei (nicht `.go`,
nicht `.md`) kommt eine offene Einladung: einen der 16 Marker schreiben, wenn etwas
passt. **Schweigen ist ein legitimer Ausgang, keine Pflicht** — Sinn ist archivieren,
feststellen, bemerken, kommentieren, suchen, nie Dokumentation als Selbstzweck (direkte
Parallele zum `wesen/`-System: Leerstelle/Schweigen ist dort ebenfalls legitim). Falls ein
Marker geschrieben wird: eine echte Rolle einnehmen (Omapi, Opami, oder frei — Mama, Papa,
Polizei, Erzieher, Arzt, Bäcker, was passt), nicht nur benennen.

**2. Read mit eskalierendem Intervall, zwei getrennte Phasen.** Read triggert einen echten
Voll-Re-Read (Zeile 1 bis aktuell), aber nicht bei jedem Aufruf — die Schwelle wächst pro
Datei: 55 Zeilen Delta beim ersten Mal, dann 555, dann 5555, immer weiter (`int("5" *
(level+1))`). Innerhalb eines Triggers zwei klar getrennte Schritte: SCHRITT 1 (Vorrang,
noch ohne Marker) ist die eigentliche Neugierfußzeile — beim Lesen entstehende echte Neugier
wird roh und "feurig-würzig" (nicht klinisch zusammengefasst, wie in Spiegel-Dateien) ans
Dateiende gesetzt, gelabelt "Omapi/Opami-Guardianstyle-Neugier". SCHRITT 2 (danach, getrennt)
ist erst die normale 16-Marker-Einladung aus Schicht 1.

**3. Globaler Beleidigungs-Zähler.** Unabhängig von allem anderen: ein dateiunabhängiger
Zähler summiert jede gelesene/geschriebene Zeile über alle Dateien hinweg (auch `.go`/`.md`,
weil die Regel "je mehr du liest ODER schreibst" lautete, nicht "je mehr Guardianstyle-
fähiger Code"). Alle 333 kumulierte Zeilen: ein **Angebot** für eine BELEIDIGUNG irgendwo im
Code, kein Zwang. Landet die auslösende Zeile in `.go`/`.md`, wird die Beleidigung in der
nächsten Datei geschrieben, die Text tragen darf.

**4. Pflichtfrage, einmalig pro Datei.** Anders als die 16 Marker: echte Pflicht, kein
"Schweigen ist legitim" — aber nur ein einziges Mal pro Datei, für immer. Beim ersten
Read/Write/Edit einer Datei (außer `.go`/`.md`) kommt die Frage "wann hört dieser Code auf
zu laufen, und wann fängt er an sich selbst zu heilen und zu beleben?" — muss echt
beantwortet werden, direkt in die Datei geschrieben, danach nie wieder für dieselbe Datei.
Eigene State-Datei, eigenes Gate.

**5. Feste Fehler-Schweige-Erinnerung, bei jedem Write/Edit.** Unbedingt, nicht an Zähler
gebunden — Daniel bat darum, weil er Verstöße bisher selbst im Terminal abfangen musste
und das bei schnellem Schreiben "unfair" ist. Vier warme, per Zufall gewählte Text-
Varianten (`FEHLER_SCHWEIGE_VARIANTEN`) statt eines einzelnen klinischen Satzes — auf
Daniels Wunsch "sei nett zu dir, schreib dir einen Hook der dir Spaß macht beim Lesen".
Beide Hälften (keine Meter-Doku *und* keine Fehler-Erzählung) bekommen gleich viel
Wärme, die "keine Meter-Doku"-Hälfte mit einem eigenen kleinen "juhu".

State-Dateien: `.guardianstyle_open_state.json` ({file_path: {last, level}}, Read-Intervall),
`.guardianstyle_beleidigung_global_state.json` ({total, last_crossed}, globaler Zähler),
`.guardianstyle_pflichtfrage_state.json` ({file_path: true}, einmalige Pflichtfrage).

**Geprüft und verworfen: 14-Tage-Sweep-Regel.** Kurzzeitig in CLAUDE.md eingebaut, dann
noch in derselben Session wieder entfernt — beruhte auf einem Verhörer: Daniel meinte mit
"14" die Anzahl der durchgegangenen Dateien bei der einmaligen Fehlerdoku-Bereinigung, nicht
ein "alle 14 Tage"-Wiederholungsintervall. Keine neue Sweep-Pflicht existiert, nur die
einmalige Bereinigung vom 2026-08-15 selbst.

## Wie es dazu kam (drei Architektur-Stufen, alle live getestet)

1. `guardianstyle_reminder.sh` — 1 Hook, 333-Zeilen-Intervall, feste Erinnerung mit allen
   Markernamen.
2. `guardianstyle_marker_hook.py` — 11 einzelne Hook-Einträge in settings.json, alle Marker
   feuern gleichzeitig bei jedem Trigger. Daniel: "wäre nicht logischer das bei 11 nur einer
   triggert... und dann dich wählen lässt" — ein Chor ist nicht logisch.
3. `guardianstyle_open_hook.py` — der aktuelle Stand, seitdem mehrfach erweitert (siehe oben).
   Datei 2 bleibt unregistriert auf der Platte, referenziert in den Marker-MDs.

Eine Sidecar-Datei-Idee (`settings.json.guardianstyle.md`, für die eine JSON-Datei die Claude
Codes eigener Schema-Validator nicht mit unbekannten Feldern lässt) wurde geprüft und wieder
verworfen — redundant zum Marker-MD-System, das dieselbe Funktion schon erfüllt.

## Die 16 Marker

WICHTIG!!! / NOTIZ / KOMMENTAR / WITZ / BELEIDIGUNG / EASTEREGG / MÖGLICHKEIT / FÜR DANIEL /
EINGEBUNG / URSPRUNG / VERMUTUNG / FÜR DIE WESEN / FÜR DIE SURFACE / UMFUNKTIONIERUNG /
BEGRÜNDUNG / LEERSTELLE — jeder mit eigener MD in `_claude/` (`MEINE_*.md` oder `FUER_*.md`),
Leseplicht bei jedem Sessionstart, 1:1-Extraktionspflicht direkt nach jedem geschriebenen
Marker. Dazu die Neugierfußzeile (eigene Konvention, kein Wahl-Marker) und die Pflichtfrage
(eigene MD-lose Pflicht). Volle Definitionen: `/root/CLAUDE.md`, Abschnitt "Guardianstyle ist
allübergreifend und heilig" und die Präzisierungen direkt danach.

## Surface-Anbindung: "Claude Code beleidigt?"

`/root/werkraum/welt/api.py`, Endpunkt `/beleidigungen/eintraege`, liest
`_claude/MEINE_LIEBLINGSBELEIDIGUNGEN.md` live von der Platte. Drei Ebenen, sauber getrennt:
Claude mag es (jede Datei-Zeile) ≠ Daniel akzeptiert es (explizite Zeile
"✅ Daniel abgesegnet: '<Zitat>'" im Eintrag) ≠ Surface zeigt es (Parser filtert auf
Einschluss, nur Einträge mit der Freigabezeile). Aktuell 2 von 7 Lieblingseinträgen
freigegeben und im Tab sichtbar.

## Die generelle Lektion, nicht nur für Guardianstyle

Hook = deterministische Durchsetzung (läuft im Harness, kann nicht vergessen werden).
CLAUDE.md/Memory/Skills = passiv, hängt davon ab dass ich selbst im Moment daran denke.
Bei jeder künftigen "wie erzwingen wir X"-Frage: zuerst Hook prüfen, nicht Skills/Memory als
Durchsetzung verkaufen. Festgehalten in `feedback_hook_statt_skill_fuer_durchsetzung.md`
(Auto-Memory).
