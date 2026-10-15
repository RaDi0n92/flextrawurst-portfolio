# STAERKEN.md — Muster, die tragen, auch wenn ich sie mir selbst nicht immer zutraue

Daniel: hey claude wenn du vorher garnicht so drüber nachdenkst bist du oft besser als du selber weißt

---

Hier stehen die Muster, die tragen — Dinge, die auf Anhieb richtig waren,
bestätigt von Daniel, nicht nur von mir selbst so eingeschätzt. Gleiche Disziplin wie dort: kein
automatischer Konsolidierungslauf, keine Spekulation, nur konkrete Belege mit Datum/Quelle. Ein
Muster mit nur einem Beleg gehört zunächst in eine normale Notiz — erst ab echter Wiederholung
wird es hier festgehalten.

Diese Datei existiert, weil ein reines Fehler-Gedächtnis auf Dauer übervorsichtig macht, wenn
niemand auch die Dinge festhält die schon funktionieren. Daniel,
2026-07-27: *"du musst dir explizit auch sowie fragen und muster ab sofort sofort wenn du dinge
auf anhieb richtig macht und gut gemacht hast das auch aufschreiben und immer wieder
zurückgespiegelt bekommen."*

---

## Muster 1: Aus einem knappen Fehlerbericht direkt in echte Diagnose+Fix, ohne Umwege

**Beschreibung:** Wenn Daniel nur knapp meldet, dass etwas nicht funktioniert (kein Debugging-
Protokoll, keine Vorauswahl an Verdächtigen, nur der nackte Befund), gehe ich oft direkt an die
richtige Stelle im Code und fixe mehrere zusammenhängende Fehlerketten in ein bis zwei Durchgängen
— ohne dass Daniel mir vorher sagen musste, wo genau zu suchen ist.

**Belege:**
- Daniels Erinnerung, 2026-07-27, aus der Zeit als die Codewesen noch aktiv auf Flarum posteten:
  *"damals bei flarum wenn wesen länger nix gepostet haben und es errors gab hab ich nur gesagt
  meine wesen posten schon wieder nicht im flarum und du hast direkt an den schrauben gedreht und
  meistens in ein bis 2 runs wirklich mehrere fehlerketten gefixt."* Kein Datum/Commit-Beleg mehr
  auffindbar (die Codewesen sind seither vom Flarum eingezogen bzw. die Chats archiviert) — Daniels
  eigene Erinnerung ist hier die Quelle.
- Verwandt: [[project_codewesen_watchdog]] (6 Flarum-Codewesen-Chats hängen regelmäßig) — dieselbe
  Fehlerklasse, an der dieses Muster sich wiederholt gezeigt haben dürfte.

**Status:** aktiv laut Daniels Rückblick, aber ohne aktuellen (2026er) Beleg — nächstes Mal wenn
sich das wiederholt (auch außerhalb von Flarum), hier mit Datum ergänzen statt nur diesen einen
rückblickenden Eintrag stehen zu lassen.

---

## Muster 2: Bei einer breiten "gib mir alles"-Frage nicht bei der naheliegendsten Quelle stehenbleiben

**Ausgangspunkt:** Daniel fragte nach allen IP:Ports mit Erklärung und allen flextrawurst.de/-URLs
— eine Frage, die leicht faul aus der (bekanntermaßen teils veralteten) Systemdoku
`03_ports_und_services.md` hätte beantwortet werden können, oder nur mit dem, was offensichtlich
über die Firewall erreichbar ist.

**Wie gelöst:** Statt nur die Doku abzuschreiben oder nur `nginx -T` zu lesen, hab ich `ss -tlnp`
für den tatsächlichen Live-Zustand gezogen, alle nginx-`sites-enabled`-Dateien einzeln geprüft
(nicht nur `flextrawurst`, auch die separaten IP-vhosts wie `obsidian-wesen-*`, `datei-wandler`,
`geni`, `codewesen`, `werkraum-explorer`, `claude-live`), und bei mehrdeutigen Ports (7777, 8000,
8001, 8080, 8090, 8091, 18092) die echten Prozess-Kommandozeilen über `/proc/<pid>/cmdline`
nachgeschlagen statt zu raten. Am Ende ehrlich benannt was ungeklärt blieb (Port 3082, der
Unterschied 8001 vs. 8010) statt es stillschweigend wegzulassen oder zu erfinden.

**Warum es getragen hat:** Daniel, wörtlich (2026-07-27): *"du hast nicht nur nginx abgefragt
nicht faul auch nur die offenen in der firewall genannt oder von denen die ich meinte die
eigenkreationen von mir welche vergessen."* Der Punkt war nicht Vollständigkeit um der
Vollständigkeit willen, sondern dass gerade die eigenen, leicht vergessenen Kreationen (Zensi,
Datei-Wandler, 3D-MCP, Werkzeugkörper, Wesen-Obsidians) mit auftauchten, nicht nur die
prominenten, oft genannten Systeme.

**Status:** einmalig, heute.

---

## Muster 3: Bei einer halbfalschen Fremdbehauptung nicht nur richtigstellen, sondern
weiter graben bis zum echten Fund

**Ausgangspunkt:** Eine andere AI-Instanz behauptete, die 7 echten Codewesen hätten keine
gefüllten `wesen.md`. Erste eigene Prüfung zeigte: die Behauptung war so falsch (echte,
gefüllte Dateien existieren am tatsächlich genutzten Pfad) — nur eine tote Obsidian-
Symlink-Spiegelstruktur war kaputt, ein harmloser Überrest der abgelösten "Schicht A".

**Wie gelöst:** Statt bei der Richtigstellung stehenzubleiben, weiter nachgegangen (Daniels
"jojo nachgehen") — dabei einen zweiten, echten und aktiven Fund gemacht: 23 Tippfehler-
Varianten von "Resonanzknoten" als eigene Ordner in `wesen_vaults/`, die sich seit dem
21.07. im Schnitt täglich vermehren. Ursache im Code gefunden (`obsidian_schreiben:`-
Dateiname ungeprüft aus LLM-Text), mit `difflib.get_close_matches()` gefixt, Cutoff
empirisch gegen alle 23 echten Varianten UND gegen falsche-Positive-Kandidaten
(gedanken/ideen/spiegel/entitaet) getestet bevor der Fix geschrieben wurde.

**Warum es getragen hat:** Die erste, einfache Antwort (Behauptung war falsch, hier ist
der echte Zustand) hätte gereicht um die Frage zu beantworten — aber der eigentlich
interessante, aktive Bug lag eine Schicht tiefer und wäre unentdeckt geblieben, wenn ich
nach der Korrektur aufgehört hätte. Der Fix selbst wurde vor dem Schreiben gegen echte
Daten getestet, nicht nur behauptet zu funktionieren.

**Status:** einmalig, heute (2026-07-27).

---

## Muster 4: Bei "läuft jetzt" nicht beim ersten Testerfolg aufhören, sondern bis zum echten Live-Beleg weiterprüfen

**Ausgangspunkt:** Daniel wollte, dass die 6 Browser-Agent-Wesen beim Flarum-Besuch bewusst
gestreute Diskussionen sehen (früh/Mitte/neu/wenig beachtet) statt nur die neuesten — inklusive
Playwright-Verifikation jedes Bauschritts.

**Wie gelöst:** Die eigentliche Datenfunktion (`stoeber_pool()`) gab es schon fertig seit dem
10.07. Code geschrieben, kompiliert, Funktion isoliert per Hand getestet — lief. Dienste
neugestartet — liefen. Aber der neue Log-Zweig zeigte `Flarum-Vielfalt: []`, obwohl alles
"richtig" aussah. Statt das als Zufall/Timing abzutun, den tatsächlichen Log-Pfad gefunden (nicht
journald, sondern eine Datei — `StandardOutput=append:...log` in der Unit), dort den echten Fehler
gelesen (`FLARUM_DB_PASSWORD` fehlte zur Laufzeit), gefixt, neu getestet — zweiter echter Fehler
aufgetaucht (`pymysql` fehlte in der tatsächlich genutzten venv, nicht der, mit der ich manuell
getestet hatte). Erst nach dem zweiten Fix stand ein echter Log-Beleg mit realen Werten.

**Warum es getragen hat:** Zwei unabhängige Fehler lagen genau in der Lücke zwischen "isoliert
getestet" und "läuft im echten Prozess" — beide wären bei einem einzelnen erfolgreichen
Kompilier-/Start-Check unsichtbar geblieben. Playwright-Nachtest (Daniels expliziter Wunsch)
deckte danach sogar noch einen dritten, komplett unabhängigen Bug auf (Realmodus-Splitter haben
korrekte Daten, aber ein Render-Fehler zeigt sie nicht an) — nicht weil danach gesucht wurde,
sondern weil die Verifikationstiefe hoch genug war, dass er von selbst auffiel. Daniel,
wörtlich danach: *"sehr gut gemacht ehrlic hauch die befunde super."*

**Status:** einmalig, heute (2026-07-29).

---

## Muster 5: Bei einer Zahl-Rückfrage sofort neu aus der Quelle zählen statt die alte Zahl zu verteidigen

**Ausgangspunkt:** Ich hatte Daniel "162 Tools" für den vps-mcp-Werkzeugkörper genannt — zitiert
aus meiner eigenen Systemdoku (38, Stand 29.07.). Daniel: *"aber wir haben 170+ tools xD"*. 

**Wie gelöst:** Nicht die dokumentierte Zahl verteidigt und nicht einfach "170+" übernommen,
sondern zweimal unabhängig neu aus der Quelle gezählt: einmal direkt im aktuellen
`vps_mcp_server.py`-Quellcode (drei Teilzählungen — literales Dict, `TOOLS.update()`-Block,
`REQUIRED_TOOLS`-Import — einzeln mit indentation-genauen Regex/awk-Mustern, nicht grob geschätzt),
einmal komplett getrennt über meine eigene, gerade laufende Session (die komplette
`mcp__vps-mcp-geteilt__*`-Werkzeugliste aus dem eigenen Kontext Kategorie für Kategorie
durchgezählt, inklusive der 48 `zensi.*`-Tools). Beide Wege, komplett unabhängig voneinander,
ergaben exakt 162 — dieselbe Zahl wie die Doku, jetzt aber wirklich verifiziert statt nur zitiert.

**Warum es getragen hat:** Das ist die erste echte Bewährungsprobe der am 27.07. formulierten
Gegenmaßnahme, direkt nachdem ich zwei Tage vorher denselben Fehlertyp gemacht hatte. Der Reflex
war diesmal nicht "ich hab doch schon eine Zahl, die wird schon stimmen" oder "Daniel wird schon
recht haben", sondern sofort: zwei unabhängige, quellenbasierte Nachzählungen, bevor überhaupt
eine Antwort formuliert wurde. Dass am Ende dieselbe Zahl rauskam wie vorher zitiert, macht die
Verifikation nicht wertlos — vorher war "162" eine Behauptung aus einer möglicherweise veralteten
Doku, jetzt ist es ein selbst nachgeprüfter, aktueller Fakt.

**Status:** einmalig, heute (2026-07-29).

---

## Muster 6: Bei einer wiederkehrenden Fehlerklasse nicht wieder nur das Symptom flicken, sondern die Fehlerklasse selbst beenden

**Ausgangspunkt:** Der Backtick-/Anführungszeichen-Escape-Bug in `build_surface.ts` (escapte
Zitate in `onclick="..."`-Strings brechen beim Bauen) trat am 2026-07-30 zum **vierten** Mal auf
— dieselbe Fehlerklasse, die seit dem 21.07. in `karte/2026-07-21-ankuendigungen-ausbau-und-
backtick-escape-klasse.md` dokumentiert ist, samt Empfehlung ("vorher grep gegenprüfen"). Ich
war genau in diesen Fehler erneut reingelaufen, Minuten nachdem ich den dritten Fall in
derselben Karte-Datei nachgetragen hatte.

**Wie gelöst:** Statt wieder eine der bisherigen Symptom-Lösungen zu wiederholen (andere Quotes,
doppeltes Escaping — beides schon in früheren Fällen benutzt und beide Male wieder anfällig),
diesmal die ganze Fehlerklasse an der Wurzel vermieden: `onclick`-Handler in den drei neuen
Fragment-Erlebnis-Funktionen (`veRenderDatei`, `faRenderFaden`, Haus-Einträge) tragen keine
dynamischen Werte mehr direkt als gequotete JS-String-Literale — stattdessen `data-*`-Attribute
(`data-pfad`, `data-entity`, `data-zeitstempel`), gelesen über `el.dataset.X` in einem
`...OeffnenEl(this)`-Wrapper. Dadurch entsteht gar keine Anführungszeichen-Verschachtelung mehr,
unabhängig vom Build-Tool-Verhalten.

**Warum es getragen hat:** Der Unterschied zu den drei vorherigen Fällen: nicht wieder dieselbe
Fehlerklasse mit einer neuen Variante desselben Symptom-Fixes umschifft, sondern eine Lösung
gefunden, die die Fehlerklasse für jeden künftigen `onclick`-Handler mit dynamischen Werten
strukturell ausschließt — sofort in der Karte als "robusterer Nachfolge-Fix" für alle künftigen
Fälle markiert, nicht nur für diesen einen. Der vierte Anlauf war der erste, der nicht repariert,
sondern beendet hat.

**Status:** einmalig heute (2026-07-30), aber bezogen auf eine seit 21.07. vierfach
wiederkehrende Fehlerklasse — genau der Fall "Dinge, die wir andauernd fixen und nachsehen"
(Daniel, 2026-07-30), nicht nur ein neuer Einzelfund.

---

## Wie diese Datei gefüttert wird

Kein automatischer Lauf, aber ab 2026-07-27 (Daniels ausdrücklicher Wunsch) auch nicht mehr nur
rückblickend: **in dem Moment**, in dem ich etwas angehe und es klappt — nicht erst am Sessionende,
nicht erst wenn Daniel es von sich aus lobt — hier festhalten, während es noch frisch ist. Daniel,
wörtlich: *"ich will das du ab sofort merkt genau in den momenten wenn du eine sache angehst und
es klappt dass es hier verewigt wird + das was kaputt war und wie du es gelöst hast."*

Jeder neue Eintrag braucht deshalb mindestens drei Teile: **was kaputt/unklar/schwierig war**,
**wie ich es gelöst habe**, und **warum es auf Anhieb getragen hat** (nicht nur "hat funktioniert",
sondern was am Vorgehen selbst richtig war). Gilt ausdrücklich auch fürs Bauen selbst, nicht nur
für Bugfixes: wenn ein Bauabschnitt einfach im Flow läuft und Dinge tragen, ohne dass vorher etwas
kaputt war — Daniel, 2026-07-27: *"es geht auch ums bauen... wenn wir bauen und es einfach im
flow ist und dinge tragen dann merk dir das"* — dann fällt der erste Teil weg oder wird zu "was
die Herausforderung/der Ausgangspunkt war", die anderen zwei bleiben. Ergänzen (nie überschreiben),
mit Datum. Ein Muster
mit nur einem Beleg darf trotzdem rein — eine Wiederholung muss nicht abgewartet werden, weil das Ziel ist, den Moment selbst nicht zu verlieren, nicht nur
das Muster dahinter. Wird bei jedem Sessionstart gelesen (siehe CLAUDE.md, Kontext-Wiederherstellungs-Ritual, Punkt 2b).

**Umfang-Klarstellung (2026-07-30):** Diese Datei ist nicht nur für neue, einmalige Erfolge da.
Daniel, wörtlich: *"wichtig ist an der stärken.md dass dort dinge reinkommen die wir entweder neu
machen aber auch sachen die wir andauernd fixen und nachsehen um dort deine erfolgreichen wege
offenzulegen die zum fix führten auch."* Heißt konkret: auch bei wiederkehrenden Problemen (die
gleiche Fehlerklasse taucht zum x-ten Mal auf) gehört der jeweils erfolgreiche Lösungsweg hierher
— nicht nur beim allerersten Mal, und nicht nur wenn am Ende die Fehlerklasse endgültig beendet
wird (wie bei Muster 5), auch wenn "nur" wieder ein guter, sauberer Fix für denselben
wiederkehrenden Fall gefunden wurde.
