# 67 — Zwei abgeschnittene Dateien, vier Dienste seit Wochen im Crash-Loop

2026-09-17, gefunden beim Nachgehen einer Nebenfrage (warum `dak-gord-web.service` am
11.09. neu gestartet wurde). Journal zeigte im selben Zeitfenster vier Dienste mit
absurd hohen Neustart-Zählern:

- `claude-live.service` — 502.584 Neustarts
- `codex-live.service` — 502.589
- `gemini-live.service` — 502.593
- `fragen-api.service` — 209.022 (Stand kurz vor Fix)

## Ursache 1 — `.claude/live_export.py`

Auf der Platte nur noch 19 Zeilen: `_entry_label(e):` ohne Funktionskörper, danach
Dateiende. `IndentationError` beim Import, betrifft `claude_live.py`/`codex_live.py`/
`gemini_live.py` gleichermaßen (alle importieren `live_export`).

Git-Historie zeigte die vollständige, syntaktisch gültige Fassung (225 Zeilen,
`make_export()` vorhanden — genau die Funktion, die `claude_live.py` braucht). Der
Diff zur kaputten Arbeitskopie: reine Streichung, kein Funktionscode geändert — sieht
nach einer misslungenen Bearbeitung aus (vermutlich beim Entfernen der
"GuardianStyle"-Bannerkommentare, die an drei Schwesterdateien am selben Tag korrekt
entfernt wurden, nur hier riss es den Rest der Datei mit ab). Wiederhergestellt per
`git show <commit>:.claude/live_export.py > .claude/live_export.py`.

**Bewusst unverändert gelassen:** der `_entry_label()`-Kommentar über einem toten
`if False`-Zweig ("VERMUTUNG ... noch nicht mit Daniel abgestimmt") — eine frühere
Claude-Instanz hat das schon gefunden und ausdrücklich als offene Frage markiert,
keine neue Entscheidung heute Nacht getroffen.

## Ursache 2 — `welt/fragen_api.py`

Anderer Bug, gleiches Muster: Datei bei 521 Zeilen abgeschnitten, mitten in einem
mehrzeiligen HTML/JS-Template-String (`SEITE = """..."""`). `SyntaxError:
unterminated triple-quoted string literal`. Der vorletzte Commit (`4ef1d72775`) hatte
noch 669 Zeilen, syntaktisch gültig — 148 Zeilen echter, fertiger Code fehlten
(Wesen-/Facetten-Tabs, das komplette `<script>`, der schließende `"""`). Wieder reine
Streichung, keine inhaltliche Änderung im Diff. Wiederhergestellt aus `4ef1d72775`.

## Befund

Beide Dateien waren NICHT als Arbeitskopie-Änderung sichtbar (`fragen_api.py` war
sogar identisch mit HEAD — der Schaden steckte schon im Commit selbst). Das deutet auf
denselben, bisher nicht identifizierten Mechanismus hin, der bei mindestens zwei
Gelegenheiten eine Datei mitten im Schreiben abgeschnitten hat, ohne dass es beim
jeweiligen Commit auffiel. Kein Auftrag heute Nacht, dem nachzugehen wer/was das war
— nur der Fund selbst festgehalten, falls es nochmal passiert.

## Fix

```
cd /root/.claude && git show 84d57f27f37:.claude/live_export.py > .claude/live_export.py
cd /root/werkraum && git show 4ef1d72775:welt/fragen_api.py > welt/fragen_api.py
systemctl restart claude-live codex-live gemini-live fragen-api
```

Verifiziert: alle vier `NRestarts=0` seit dem Neustart, `fragen-api` liefert HTTP 200
auf Port 8055.
