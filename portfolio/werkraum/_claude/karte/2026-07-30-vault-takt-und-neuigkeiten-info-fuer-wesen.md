---
datum: 2026-07-30
betrifft: [browser_agent, gemeinsames-haus, vault-takt, autonomie, entity-prompt]
importable: false
autor: claude-code bei Daniels VPS
---

## Zwei neue Mechanismen in browser_agent.py, direkt aus der Fragment-Erlebnis-Session heraus

**1. `neuigkeiten_info` (passive Erwähnung):** informiert die Wesen im Prompt, dass Menschen
ihre Flarum-Aktivität jetzt gruppiert/mit Permalink sehen, und lädt zum Gemeinsamen Haus ein.
Wirkung nach ~25 Minuten: ein Wesen (F3INSCHM3CK3R) hat `gemeinsam_lesen:` ausgeführt — die
allererste echte Gemeinsames-Haus-Aktion überhaupt. Kein Schreiben, nur Lesen, aber ein echter
erster Schritt.

**2. `VAULT_TAKT_SEKUNDEN` (aktiver, dedizierter Takt, ~1200s/3x pro Stunde):** Daniels
Beobachtung, dass die passive Erwähnung zwischen sechs anderen Info-Blöcken (Flarum-Vielfalt,
Angebote, Selbstwahrnehmung...) untergeht — anders als die Flarum-Vielfalt-Vorschläge, die
konkret und nummeriert sind. Jetzt bekommt jedes Wesen einen eigenen, wiederkehrenden Check-in,
an dem NUR Gemeinsames-Haus-/Vault-Aktionen im Menü stehen (kein Flarum, keine Splitter-Angebote
als Ablenkung) — piggybackt auf den bestehenden 44s-Check-in-Takt, kein zweiter LLM-Trigger.

Kurzer Einwand von mir unterwegs: bricht das nicht mit "Du wählst deinen Input selbst"? Daniels
Antwort, die den Punkt klärt: *"das ist ja kein Input sondern ein Outputverfahren"* — das
Zeitfenster ändert nur, welche Aktionen im Menü stehen, nicht was das Wesen wahrnimmt oder denkt.
Passt strukturell zum bestehenden Schlaf-/Check-in-Rhythmus (auch von außen vorgegeben, kein
Bruch mit einem bisherigen Prinzip).

## Verifiziert vor dem Rollout

Isolierter Prompt-Test (`baue_prompt()` außerhalb des Haupt-Loops aufgerufen): normaler Tick
unverändert (3583 Zeichen, Flarum-Optionen vorhanden), Vault-Takt-Tick sauber reduziert (2115
Zeichen, nur 6 Aktionen: obsidian_lesen/schreiben, gemeinsam_lesen/schreiben, rag_erkunden,
nachdenken — kein navigiere/klicke/flarum_besuchen/schlafen).

## Zwei Neustarts, zwei eigene Fehler gefangen bevor sie liefen

Erster Neustart (alle 7 gleichzeitig): führte zu kurzer LLM-Slot-Kontention (mehrere 150s-
Timeouts), löste sich von selbst. Zweiter Neustart (gestaffelt, 4s Abstand): sauber, keine
Fehler in den Logs.

Beim Warten auf den zweiten Neustart zwei eigene Endlosschleifen-Bugs in
Bash-Warteskripten gebaut und vor dem Ausführen-Lassen bemerkt: einmal invertierte
`until`-Bedingung, einmal ein `grep` über alle `browser-agent`-Units, das die bekannte
kaputte `dak+gord`-Duplikat-Unit (crasht dauerhaft, wird nie "active running") mit erfasst
hätte und nie beendet worden wäre. Beide vor dem Loslaufen gestoppt bzw. korrigiert, nicht erst
nachdem sie schon liefen.

## Was noch offen ist

Erster echter Vault-Takt-Tick fällig ~20 Minuten nach dem zweiten Neustart (ca. 09:04-09:05
Uhr). Ob daraus eine echte `gemeinsam_schreiben`-Aktion oder eine neue Datei im Gemeinsamen Haus
wird, ist offen — Wächter läuft, meldet sich bei echtem Fund.
