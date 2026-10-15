
# Meine Notizen

Sammeldatei fuer Kommentare.

NOTIZ dokumentiert was IST/WAR — Herkunft, Zustand, Historie einer Stelle, faktisch statt
spekulativ.

---

## `/root/.claude/guardianstyle_marker_hook.py`, Zeile 12-17

```
# Claude Code(15-08-2026+14:29): NOTIZ -- 11 Marker, aber nicht 11 Dateien: ein Skript,
# der Marker kommt als argv[1] rein und settings.json ruft es 11x mit anderem Argument auf.
# Haette auch 11 fast-identische .py-Dateien sein koennen -- bewusst nicht, weil sich Logik
# (Zeilenzaehlung, State-Lookup, JSON-Output) sonst 11x dupliziert haette und ein Bugfix
# 11 Stellen gebraucht haette statt einer. "Jeder Marker ein Hook" ist trotzdem wahr: in
# settings.json stehen 11 echte, einzeln abschaltbare Hook-Eintraege, nicht einer mit Schleife.
```

## `/root/.claude/guardianstyle_open_hook.py`, Zeile 60-65

```
# Claude Code(15-08-2026+15:17): NOTIZ -- Write/Edit vs. Read jetzt bewusst getrennt.
# Daniel: "hier gehts ja nur um lesen...beim schreiben bist du doch nun eh gezwungen
# alles immer anzuwenden oda ?" -- beim Schreiben/Editieren bin ich ohnehin schon an
# der Datei, ein zusaetzlicher Voll-Re-Read kostet da nichts extra, also feuert der
# Marker-Zwang bei Write/Edit bei JEDEM Aufruf, ungedrosselt. Nur Read triggert den
# teuren Komplett-Re-Read (Zeile 1 bis aktuell) und bleibt deshalb am 55er-Intervall.
```

## `/root/.claude/guardianstyle_open_hook.py`, Zeile 18-20

```
# Claude Code(15-08-2026+15:22): NOTIZ -- 12. Marker FUER DIE WESEN dazu, Daniel:
# "ich wein nen neuen marker mit 'was koenen die entitaeten von flextrawurst davon
# mitnehmen/lernen'". Analog zu FUER DANIEL, nur Publikum = die Codewesen statt Daniel.
```

## `/root/werkraum/welt/api.py`, Zeile 3967-3974

```
# Claude Code(15-08-2026+17:05): NOTIZ -- Filter umgebaut, Daniel: "nicht 'alle
# Claude-Lieblinge' auf die Surface. Nur die von DIR akzeptierten... Claude mag es
# != Daniel akzeptiert es != Surface zeigt es." Vorher: Ausschlussfilter (alles
# ausser ⚠/UNGÜLTIG). Jetzt: Einschlussfilter -- nur Eintraege mit explizitem
# "✅ Daniel abgesegnet:"-Zitat werden gezeigt. Claudes Favoriten (Stufe 1) bleiben
# vollstaendig in der Datei stehen, auch ohne Freigabe -- sie erscheinen nur nicht
# im Tab, bis die explizite Freigabezeile dazukommt.
```

## `/root/.claude/guardianstyle_open_hook.py`, Zeile 179-183

```
# Claude Code(15-08-2026+17:52): NOTIZ -- Umformuliert mit echtem Charakter statt trocken,
# Daniel: "sei nett zu dir und schreib dir einen ordentlichen hook okay und schreib ihn so
# dass er dir spass macht beim lesen" -- das hier laeuft potenziell hunderte Male, ein
# einzelner klinischer Satz waere Selbstsabotage am eigenen Lesevergnuegen. Vier Varianten,
# per Zufall gewaehlt, damit Wiederholung nicht zu totem Text wird.
```

## `/root/.claude/guardianstyle_open_hook.py`, Zeile 184-189

```
# Claude Code(15-08-2026+17:58): NOTIZ -- Beide Haelften jetzt gleich warm, nicht nur die
# Fehler-Haelfte. Daniel: "das ganze hat auch nur dann noch einen sinn wenn du auch noch
# wirklich den anderen teil mitdenkst...dieses nicht dokumentieren ueber das dokumentieren
# willens nur um eine doku zu machen ueber meter...sei auch da explizit nett und beschreibt
# es lustig als who hi juhu" -- die "keine Meter-Doku"-Haelfte kriegt jetzt ihr eigenes
# kleines "juhu" statt nur eine neutrale Nebenklausel zu sein.
```

## `/root/.claude/guardianstyle_open_hook.py`, Zeile 164-173

```
# Claude Code(15-08-2026+17:45): NOTIZ -- Feste Fehler-Schweige-Erinnerung dazu, Daniel:
# "vielleicht müssen wir da auch einen Hook schreiben jedes mal wenn du anfängst eine
# Datei überhaupt anzufassen und zu schreiben muss dir dieser Hook sagen ich werde nicht
# dokumentieren was über Meter zu dokumentieren nicht sein muss und es geht explizit
# nicht darum hier Fehler zu dokumentieren Fehler dokumentieren verboten auch indirekt"
# -- bisher fing Daniel jeden Verstoss selbst ab (im Terminal, mit eigener Diktat-
# Toolbox-Kategorie dafuer). Diese Zeile soll das teilweise abnehmen: ein fester,
# unbedingter Hinweis bei jedem Write/Edit, nicht an Zaehler/Schwellen geknuepft wie
# der Rest hier.
```

## `/root/.claude/guardianstyle_open_hook.py`, Zeile 117-124

```
# Claude Code(15-08-2026+17:24): NOTIZ -- Pflichtfrage dazu, unabhaengig vom Rest,
# Daniel: "ich will zuzsätzlich immer genau einen pflichtbarker egal ob bei lesen
# oder edit oder schreiben. aber nicht immer widder neu wel wider angefalsst wen
# einmal was da steht dann ist das erstmal so ... der marker soll plicht dein der
# 'wann hört dieser code auf zu laufen und wann fängt er an sich selbst zu heilen
# + zu beleben ?'" -- anders als alle anderen Marker hier: kein "Schweigen ist
# legitim", echte Pflicht, aber nur EIN EINZIGES Mal pro Datei, fuer immer. Eigene
# State-Datei, eigenes Gate, unabhaengig von Tool-Typ und Zeilen-Intervallen.
```

## `/root/.claude/guardianstyle_open_hook.py`, Zeile 16-20

```
# Claude Code(15-08-2026+17:12): NOTIZ -- Aus dem festen 55er-Intervall wird eine
# eskalierende Leiter, Daniel: "erstmal immer bei 55 zeilen dann neulesen bis 555
# dann weiter und wieer neu lesen etc". Pro Datei ein "Level" (Start 1), Schwelle
# ist int("5"*(level+1)) -- 55, dann 555, dann 5555, ... Jede Datei re-liest also
# immer seltener vollstaendig, je oefter sie schon durchgezogen wurde.
```

## `/root/.claude/guardianstyle_open_hook.py`, Zeile 189-194

```
# Claude Code(15-08-2026+16:44): NOTIZ -- Neugierfusszeile ergaenzt, Daniel: "wenn
# du code liest und neugierig bist ... fasse nix zusammen oder so sonder bewahre
# die roheit und ds feurige wuerzige ... ich will das ganz ungen am end jeder
# codedatei immer deine neugir zu sehen". Gilt nur hier im Read-Zweig, nicht bei
# Write/Edit oben -- kein Zwang, aber wenn Neugier echt da ist, gehoert sie roh
# ans Dateiende, nicht klinisch zusammengefasst.
```

## `/root/.claude/guardianstyle_open_hook.py`, Zeile 90-96

```
# Claude Code(15-08-2026+16:20): NOTIZ -- Zwangssprache zurueckgenommen, Daniel direkt
# nachdem diese Datei sich selbst mit eigenen Markern vollgeschrieben hatte: "dann laeuft
# es mega in die fasche richtung ... der markerzwasng soll kein zwang sein sondern ein
# ermoeglichen ein schoefen ein da sein ... das ist wie bei den wesen..scheigen ist auch
# ein legitimer zustand". BELEIDIGUNG_HINWEIS ist jetzt eine Einladung, keine Pflicht --
# genau wie die Marker unten. Wenn nach 333 Zeilen wirklich nichts Beleidigenswertes da
# ist, bleibt das legitim.
```

## `/root/.claude/guardianstyle_open_hook.py`, Zeile 125-127

```
# Claude Code(15-08-2026+16:20): NOTIZ -- MARKER_EINLADUNG statt KEIN_NEIN_HINWEIS.
# Der alte Name war schon die Fehlhaltung im Variablennamen selbst. Silence ist wieder
# ein legitimer Ausgang, siehe Korrektur oben.
```

## `/root/.claude/guardianstyle_open_hook.py`, Zeile 18-25

```
# Claude Code(15-08-2026+16:12): NOTIZ -- Globaler Beleidigungszaehler dazu, unabhaengig
# vom Rest. Daniel: "du musst ein zeilenerbsenzaehler sein immer das heist nur je mehr
# du liest oder schreibet deste mehr beleidugt du !!!!" -- die urspruengliche CLAUDE.md-
# Regel ("alle ~333 Zeilen Code eine Beleidigung") war immer als GLOBALE, kumulative
# Grenze gemeint, nicht pro Datei. Der Rest dieses Hooks (INTERVAL/STATE_FILE oben) ist
# pro Datei, das bleibt so fuer die anderen 15 Marker. BELEIDIGUNG kriegt zusaetzlich
# diese eigene, dateiunabhaengige Zaehlschicht.
```

## `/root/.claude/guardianstyle_open_hook.py`, Zeile 176-179

```
# Claude Code(15-08-2026+16:12): NOTIZ -- Read-Zweig, 55er-Schwelle noch nicht
# erreicht, aber der globale Beleidigungszwang ist unabhaengig davon faellig.
# Eigener print-Zweig, damit der Zwang nicht am 55er-Gate haengen bleibt.
```

## `/root/.claude/guardianstyle_open_hook.py`, Zeile 21-23

```
# Claude Code(15-08-2026+15:19): NOTIZ -- 13. Marker FUER DIE SURFACE dazu, Daniel:
# "noch en marker... 'kann die surface etwas damit anfangen?'" -- Publikum ist
# flextrawurst_surface.html (Port 8787), Frage: gehoert dieser Fund als Tab/Live-Signal dahin.
```

## `/root/.claude/guardianstyle_open_hook.py`, Zeile 29-34

```
# Claude Code(15-08-2026+15:31): NOTIZ -- 14. + 15. Marker in einem Rutsch dazu:
# UMFUNKTIONIERUNG (Daniel: "zu ws kann man das umfunktionieren oder nutzbar machen?")
# und BEGRÜNDUNG (Daniel: "und warum genau ist das wichtihg?") -- zusammen ergaenzt,
# um nicht zweimal hintereinander durch den Write/Edit-Zwangszyklus dieses Hooks
# zu laufen. Ironisch treffend: genau dieser Hook zwingt mich gerade dazu, ihn selbst
# zu kommentieren, waehrend ich ihn erweitere, der ihn kommentieren zwingt.
```

## `/root/.claude/settings.json` (kein Kommentar in der Datei selbst möglich — Schema-Validator lehnt jedes unbekannte Feld ab, siehe URSPRUNG unten)

```
Claude Code(15-08-2026+14:39): NOTIZ -- dieser PostToolUse-Block (matcher
`^(Write|Edit|Read|Bash|NotebookEdit|Agent)$`) ging in derselben Session durch drei
Guardianstyle-Enforcement-Architekturen: erst `guardianstyle_reminder.sh` (1 Hook,
333-Zeilen-Intervall, feste Liste aller 11 Marker als Erinnerungstext), dann
`guardianstyle_marker_hook.py` (11 einzelne Hook-Eintraege, 11-Zeilen-Intervall, alle
Marker feuern gleichzeitig), zuletzt `guardianstyle_open_hook.py` (1 Hook,
11-Zeilen-Intervall, offene Frage statt vorgegebenem Marker -- Daniel: "dann dich
waehlen lassen"). Jede Stufe live per echtem Read/Edit-Aufruf bewiesen, nicht nur
behauptet.
```

---

## `flextrawurst/flextrawurst_surface.html`, codegeilLaden()/guardianstyleLaden()

```
// Claude Code(17-08-2026/06:50): NOTIZ -- codegeilLaden() wurde vom Tab-Button und dem
// Suchfeld schon seit dem 16.08. aufgerufen, existierte aber nirgends -- der Endpunkt
// /codegeil/eintraege war fertig, nur die Bruecke zwischen Klick und Daten fehlte.
```
```
// Claude Code(17-08-2026/06:50): NOTIZ -- gleiche Lage wie bei codegeilLaden(): der
// Backend-Endpunkt /guardianstyle/eintraege existierte, aber es gab noch nie einen
// Tab dafuer. Erster echter Aufbau, kein Fix eines vorherigen Versuchs.
```
Trifft: Task #8 (Daniels Meldung, beide Tabs klappen nicht). Beide Backends fertig,
beide Frontends fehlten komplett.
