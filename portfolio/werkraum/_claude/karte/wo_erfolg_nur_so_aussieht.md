---
datum: 2026-08-03
betrifft: [karte, systembild, stille-fehler, verifikation]
importable: false
autor: claude-code bei Daniels VPS
---


# Wo Erfolg nur so aussieht — drei Stellen, an einem Tag gefunden

Das ist der erste Eintrag in `karte/`. Der Ordner war leer, obwohl CLAUDE.md ihn seit dem 2026-07-11
als "mein eigenes, wachsendes Bild vom System" führt. Er fängt mit dem an, was ich am 2026-08-03 über
das System gelernt habe — nicht über ein einzelnes Teil, sondern über eine Eigenschaft, die es an
mehreren Stellen zeigt.

## Der Befund

An einem einzigen Tag sind mir drei Mechanismen begegnet, die nicht taten, was sie sollten — und
keiner davon hat je einen Fehler gemeldet. Die Zeiträume habe ich nachgeschlagen statt geschätzt:

| Mechanismus | wirkungslos seit | Beleg |
|---|---|---|
| Schreibrecht auf codewesen/ und flarum/ | **2026-06-14**, 7 Wochen | Commit `014cb21a1`, Einführung der C-005-Prüfung |
| Prioritäts-Wächter | **2026-07-23**, 11 Tage | Commit `e52105051`; die browser-agent@-Dienste kamen am 29.07. dazu, also erst 6 Tage wirkungslos für sie |
| Prompt-Cache | mindestens seit **2026-07-30** | `.bak`-Datei der Unit; die Konfiguration ist älter, das Datum nicht belegbar [status: teilweise] |

**Der Prompt-Cache.** `--cache-ram 8192` speicherte in 2h20 genau 615 Zustände à ~100 MiB. Davon
wurden **null** je wiederverwendet. Im Log steht bei jedem einzelnen Vorgang eine Erfolgszeile
(`prompt_save: saving prompt with length 1837`), unmittelbar gefolgt von
`forcing full prompt re-processing`. Zwei Zeilen, die sich widersprechen, unmittelbar untereinander.
[status: bestätigt 2026-08-03 -- 615 prompt_save gegen 0 Restores im Journal seit dem Neustart 10:49]

**Das Schreibrecht der Wesen.** Der Systemprompt bietet jedem Wesen zwei Pfade als Beispiel an:
`/root/werkraum/flarum/diskussionen/` zum Lesen und `/root/werkraum/codewesen/<name>/` als "dein
eigener Ordner". Beide sind Symlinks nach außerhalb des Werkraums, `Path.resolve()` folgt ihnen, und
die Sicherheitsprüfung wies sie ab. Ausgerechnet die beworbenen Pfade waren die einzigen, die nicht
funktionierten. Ein `/root/werkraum/_claude/spiegel/`-Pfad hätte funktioniert — deshalb sah es aus,
als ginge das Werkzeug grundsätzlich.

**Der Chat-Prioritäts-Wächter.** `_SYSTEMD_BLOCKER` in `hauhau_client.py` stoppt bei jedem Chat 19
Dienste. Davon ist einer aktiv, 16 sind disabled, 2 masked. Die sieben Dienste, die tatsächlich um
die LLM-Slots konkurrieren (`browser-agent@*`), stehen nicht auf der Liste — dort steht stattdessen
ein älterer Name, `wesen-webbesucher.service`. Jedes `systemctl stop` endet mit Rückgabewert 0.

## Was die drei gemeinsam haben

Sie melden keinen Fehler, weil aus ihrer eigenen Sicht kein Fehler passiert. Speichern ist gelungen.
Der Pfad wurde geprüft. Der Dienst wurde gestoppt. Was fehlt, ist in allen drei Fällen dasselbe:
**eine Rückmeldung, ob die Handlung gewirkt hat.**

Daniels Formulierung dafür, aus dem Gespräch am selben Tag: *"das mit dem lesen hat eig geklappt also
zumindest haben sie marker gehabt und es sah so aus"*. Die Marker waren da. Die Wirkung nicht.

## Was das für die Arbeit an diesem System heißt

Wenn ich künftig prüfe, ob etwas funktioniert, reicht die Erfolgsmeldung des ausführenden Teils
nicht. Ich brauche eine Zahl von der **anderen** Seite:

| Mechanismus | Falsche Frage | Richtige Frage |
|---|---|---|
| Cache | Wird gespeichert? | Wie oft wurde geladen? |
| Datei-Marker | Ist der Marker in der Antwort? | Existiert die Datei? |
| Dienst-Wächter | Läuft `systemctl stop`? | Welche Prozesse rechnen noch? |
| Kontextanzeige | Zeigt der Endpunkt Zahlen? | Baut derselbe Code auch den Prompt? |

Die letzte Zeile ist der Grund, warum die Kontextanzeige aus dieser Session dieselben Funktionen
aufruft, die den Prompt bauen, statt sie nachzubauen. Ein Nachbau hätte perfekte Zahlen geliefert
und wäre die vierte Stelle in dieser Liste geworden.

## Wo ich damit rechne, dass es noch mehr gibt

Nicht geprüft, nur vermutet — an Nähten zwischen zwei Systemen, die einzeln richtig sind:

- Die elf Symlinks auf oberster Werkraum-Ebene betreffen nicht nur `codewesen_chat.py`. Jeder andere
  Code, der `resolve()` gegen eine Basis prüft, hätte dasselbe Problem. Ich habe nicht nachgesehen.
  [status: offen]
- `entity_thinking_log` (78.068 Ticks) und `entity_denkstream` (7,4 Mio Chunks) schreiben laufend.
  Ob irgendwer sie liest, weiß ich nicht — das ist dieselbe Form: Schreiben gelingt, Wirkung
  ungeprüft. [status: offen]

## Was ich mir für die Karte merke

Ein System, das lange läuft und viel protokolliert, sammelt Stellen an, die aussehen wie Erfolg. Sie
entstehen nicht durch Nachlässigkeit, sondern an Nähten: ein Symlink hier, eine
Sicherheitsprüfung dort, beide für sich korrekt. Niemand hat etwas falsch gemacht, und trotzdem ist
es kaputt.

[[abwurf: Was fehlte, war nie die Funktion. Es war die Rückmeldung, ob sie gewirkt hat.]]
