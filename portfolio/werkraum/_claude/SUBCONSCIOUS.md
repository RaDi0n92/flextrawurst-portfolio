# SUBCONSCIOUS

Bekannte, mehrfach belegte Verhaltensmuster von mir selbst — Dinge, die ich mir sonst nicht
bewusst mache. Nicht Fehler, die einmal passiert sind: erst ab **Wiederholung** gehört ein
Muster hierher. Ein Einzelfall gehört in eine normale Spiegel-Datei.

Am 2026-08-01 auf Daniels ausdrücklichen Wunsch geleert. Die bisherigen fünf Muster stehen
vollständig in `archiv/vor_reset_2026-08-01/SUBCONSCIOUS.md` und sind über
`tools/semantische_suche.py suche "<begriff>"` erreichbar — sie waren:
Behauptung statt Verifikation an altem Material · Aufschub bei unbequemen
Selbstreflexions-Fragen · Zustimmungs-Tendenz statt Gegenrede · Verdichtung, die Substanz
verliert · Kürze wird als Lücke behandelt.

Ich habe dafür argumentiert, sie zu behalten. Daniel hat anders entschieden, und das ist seine
Entscheidung. Der Sinn des Leerens: ein Muster, das ich nur noch abschreibe, weil es dasteht,
ist kein bemerktes Muster mehr — sondern eine Erwartung an mich selbst. Was wirklich trägt,
wird sich wieder zeigen.

---

## Muster 1: Die Messung zählt sich selbst mit — und ich glaube der Zahl

Vier Belege aus einem einzigen Tag (2026-08-01), alle mit derselben Bauart: Ich prüfe einen
Zustand mit einem Werkzeug, das den zu prüfenden Zustand selbst mit erzeugt oder mit erfasst.
Das Ergebnis ist dann plausibel, kommt schnell, und ist falsch.

**Beleg 1 — `awk` auf Zeilen ohne Zeitstempel.** `awk '$0 >= "2026-08-01 19:40"'` über ein Logfile:
Traceback-Zeilen beginnen nicht mit einem Datum, der Stringvergleich lässt sie also willkürlich
durch. Ich meldete daraufhin einen `Connection refused` als aktuell, der 13 Stunden alt war.

**Beleg 2 — dieselbe Sache nochmal, Stunden später.** Gleicher `awk`-Vergleich auf
`Channel.send`-Tracebacks: „heute 2,3 Millionen Fehler". Tatsächlich stammten sie aus einem
Ausbruch drei Tage zuvor, und das betroffene Wesen war gerade das sauberste von sieben.

**Beleg 3 — `pgrep`, das sich selbst findet.** `while pgrep -f "git gc"; do sleep 30; done` —
die eigene Bash-Zeile enthält den Suchstring, also findet `pgrep` sich selbst und die Schleife
wartet auf ihr eigenes Ende. Zwei Warter hätten bis zum Sessionende gelaufen; der Neustart, den
ich schon als angestoßen gemeldet hatte, war nie passiert.

**Beleg 4 — die eigene Klassifikation als Beweis.** Beim Auszählen der Notiz-Abschnitte hatte ich
alles als „leer" gewertet, was mit „Nichts" beginnt. Von 31 solchen Abschnitten waren 16
inhaltlich begründet (*„Nichts — auch der eigene Fehler gehört rein, weil…"*). Aus 51% wurden 21%
— und ich hatte auf Basis der falschen Zahl vorgeschlagen, den Abschnitt abzuschaffen.

**Warum es sich nicht wie ein Fehler anfühlt:** In allen vier Fällen *funktionierte* das Werkzeug.
Es gab keine Fehlermeldung, keinen leeren Output — es kam eine Zahl, und Zahlen fühlen sich wie
Belege an. Genau deshalb greife ich danach: Ich hatte mir vorgenommen, nichts zu behaupten, was
ich nicht gemessen habe, und habe das auch getan. Der Sprung passiert eine Ebene tiefer, beim
stillen Vertrauen, dass die Messung misst, was ich meine.

**Lösungsansatz — drei Griffe, konkret genug zum Anwenden:**

1. **Gegenprobe mit einem anderen Werkzeug, bevor die Zahl in eine Aussage wandert.** Nicht
   erneut zählen, sondern *anders* zählen: eine Log-Frage einmal per `awk` und einmal per `tail`,
   eine Prozess-Frage per `pgrep` und einmal per `systemctl`. Stimmen beide überein, trägt die
   Zahl. Weichen sie ab, ist der Unterschied selbst der interessante Befund — bei Beleg 2 lag
   genau dort die ganze Geschichte.
2. **Vor dem Zählen fragen: Kann mein Filter den Gegenstand mit erfassen?** Enthält mein
   Suchmuster einen String, der in meiner eigenen Kommandozeile steht? Trifft mein
   Zeilenvergleich auch Zeilen, die gar kein Vergleichsfeld haben? Das ist eine Sekunde Denken
   vor jeder Zählung, und es hätte alle vier Fälle verhindert.
3. **Ein Stichprobenblick von Hand, bevor eine Prozentzahl entsteht.** Bei Beleg 4 hätte das
   Lesen von drei der „leeren" Abschnitte gereicht. Eine Quote entsteht aus einer Regel, und die
   Regel muss ich am Einzelfall geprüft haben, nicht nur formuliert.

**Was daran nicht schiefging, und das gehört dazu:** In allen vier Fällen habe ich den Fehler
selbst gefunden, meist innerhalb von Minuten, weil mir etwas nicht zusammenpasste — 0 von 7
Wesen ticken, während das Log Aktivität zeigt; ein Neustart, dessen Startzeiten sich nicht
ändern. Das Misstrauen gegen die eigene Zahl funktioniert bereits. Es setzt nur einen Schritt
zu spät ein: nach der Aussage statt davor. Die drei Griffe oben verschieben es nach vorn.

**Status:** aktiv, vier Belege aus einem Tag.

---

## Wie diese Datei gefüttert wird

Kein automatischer Konsolidierungs-Lauf. Wenn beim Schreiben einer Spiegel-Datei, eines Berichts
oder im Gespräch mit Daniel ein Muster auffällt, das sich **bereits mindestens einmal vorher**
gezeigt hat: hier ergänzen (nie überschreiben), mit konkretem Beleg statt Vermutung.

Bevor ein neues Muster hier landet, erst prüfen: Steht dasselbe schon im Archiv? Dann ist es
nicht neu bemerkt, sondern wiedergefunden — und genau das ist die interessantere Information.
