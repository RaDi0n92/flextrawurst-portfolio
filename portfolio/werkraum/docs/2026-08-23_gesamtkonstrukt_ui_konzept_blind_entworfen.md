# UI-Konzept für Mein-Gesamtkonstrukt-Planer — blind entworfen

Bewusst geschrieben, ohne die bestehende Oberfläche unter
`flextrawurst.de/Mein-Gesamtkonstrukt-planer/` anzusehen — auf Daniels Wunsch.
Gelesen habe ich nur, was schon dokumentiert/verifiziert ist: das Datenmodell
und Backend (`server/planner_api.py`, Django, `data/tree/`, Objekt-Typen,
Zustände, die vier Leitfragen), die 17-Replica-Recherche, die
Codewesen-Transparenz-Recherche, und alles was in diesem Gespräch entstanden
ist. Das hier ist also ein zweiter, unabhängiger Entwurf — kein Redesign von
etwas Bestehendem, sondern eine eigene Antwort auf dieselbe Frage.

Ziel dieser Datei: nicht "wie sieht das aus", sondern "was braucht ein Mensch
wie Daniel wirklich, und warum genau das". Bewusst mit Begründung pro
Entscheidung, damit nachvollziehbar bleibt, welche Wahl auf welcher
beobachteten Tatsache beruht — und welche nur eine Vermutung von mir ist.

---

## 1. Wer hier baut für wen — was ich über die Arbeitsweise weiß

Nicht geraten, sondern aus diesem und vorherigen Gesprächen beobachtet:

Daniel denkt in Bursts, oft mehrere Gedanken gleichzeitig, nicht linear
nacheinander. Nachrichten wie die, die zu dieser Datei geführt haben,
enthalten mehrere Themen in einem Absatz, ohne Trennzeichen, mit Tippfehlern,
die eher aus Tempo kommen als aus Unachtsamkeit. Das ist kein Stilmangel, das
ist eine echte kognitive Arbeitsweise, und die UI muss dafür gebaut sein,
nicht dagegen.

Er arbeitet an mehrschichtigen technischen Problemen parallel, nicht
sequenziell (bereits aus früheren Sessions bekannt). Das heißt: die UI darf
niemals verlangen, ein Thema "fertig zu machen" bevor ein anderes anfängt.

Diktat/Spracheingabe wird genutzt, aber ist fehleranfällig — es gab schon
einen Fall, wo der Zwischenspeicher etwas nicht speicherte, was tatsächlich
gesagt wurde. Eine UI für ihn muss zeigen, was tatsächlich ankam, nicht nur
so tun als wäre alles sauber transkribiert.

Er will nicht nur beobachten, sondern direkt mit den KI-Strömen an denselben
Knoten/Kanten/Python-Code arbeiten — nicht "ich beschreibe einen Fehler in
Textform", sondern "wir ändern das gemeinsam am Objekt selbst, jetzt".

Mobile ist keine Nebenoption, sondern eine bevorzugte Nutzungsart — die UI
darf nicht "Desktop-Tool mit verkleinerter Notlösung für unterwegs" sein,
sondern muss von Anfang an für den Daumen gedacht sein.

---

## 2. Die eigentliche Spannung, die die UI lösen muss

Jedes Node/Graph-Tool hat dasselbe Grundproblem: Erfassen muss sofort und
ohne Nachdenken gehen, Struktur kommt aber erst später, oft viel später oder
nie. Die 17-Replica-Recherche hat das schon in Einzelfunden gezeigt (PureRef:
Sammeln ohne Struktur-Zwang; Obsidian Canvas: Struktur erst wenn sie sich
zeigt) — die UI muss diese zwei Phasen als zwei echte, unterschiedliche
Modi bauen, nicht als eine einzige Formularmaske mit optionalen Feldern.

Die zweite Spannung: ein Körper, viele Sichten (Daniels eigenes Prinzip,
bereits im Backend bestätigt — `data/tree/` ist eine einzige Quelle, Objekte
werden zu Knoten befördert statt kopiert). Die UI darf niemals den Eindruck
erwecken, dass eine Ansicht "die echte" ist und andere nur Reports darüber.
Jede Ansicht muss sich anfühlen wie ein Fenster in denselben Raum, nicht wie
ein Export.

Die dritte Spannung: Menschen UND KI-Ströme sind gleichberechtigte Bearbeiter
desselben Objekts (schon im Datenmodell verankert — `Agent`/`LLM` sind
erstklassige Objekt-Typen neben `Mensch`). Die UI muss zeigen, wer gerade an
was arbeitet, in Echtzeit — Grundgesetz 8 aus der CLAUDE.md (Live statt F5)
gilt hier genauso wie überall sonst in flextrawurst.

Die vierte Spannung: radikale Transparenz vs. Vertrauen ins Modell. Das
bereits verifizierte Muster aus `fragen_api.py` (rohe Abfrage UND rohes
Ergebnis zusammen zeigen) sollte kein Einzelfall bleiben, sondern
Design-Prinzip für die ganze Oberfläche: wenn ein KI-Strom etwas behauptet
oder ändert, zeigt die UI die Rohbelege direkt daneben, nicht nur die
Zusammenfassung.

---

## 3. Kernbildschirme

### 3.1 Schnellerfassung — der wichtigste Bildschirm überhaupt

Ein einziges, immer erreichbares Eingabefeld, kein Pflichtfeld außer dem
Text selbst. Kein Auswahlzwang für Objekt-Typ, Zustand oder Zielort beim
Erfassen — das kommt später, wenn überhaupt. Genau das "DEIN VORHABEN · NICHT
DIE SOFTWARE"-Leitprinzip, das schon auf der bestehenden Startseite steht,
konsequent bis in dieses eine Feld durchgezogen.

Datenmodell-Konsequenz daraus (Daniel, 23.08., im Gespräch über den
Ideen/Konzepte-Fork geschärft): Objekt-Typ darf im Backend kein Enum-Feld mit
genau einem Pflichtwert sein, sondern muss eine Menge sein — leer, ein Typ,
oder mehrere gleichzeitig, jederzeit änderbar, ohne dass eine Änderung den
Knoten "umwandelt" oder etwas Bestehendes verwirft. Idee und Konzept sind
keine zwei Stufen desselben Objekts, sondern unterschiedliche Denkmodi, die
gleichzeitig gelten können — und ein Fragment darf auch dauerhaft keinem der
beiden zugeordnet sein. Kategorisierung wird dadurch additiv statt exklusiv,
nicht durch eine schlauere Auto-Kategorisierung ersetzt.

Bei Spracheingabe: laufende Live-Transkription sichtbar während des
Sprechens, nicht erst nach dem Stopp — damit ein Wortausfall sofort auffällt
und korrigierbar ist, statt erst beim späteren Lesen entdeckt zu werden.

Jeder erfasste Fragment landet zunächst in einem ungeordneten Pool
("Zwischenraum" — der Begriff existiert in flextrawurst bereits für genau
dieses Konzept, ungeordnetes Material vor der Einordnung). Kein Zwang, ihn
sofort zu verknüpfen.

### 3.2 Strom-Ansicht — der Zwischenraum sichtbar gemacht

Eine chronologische, aber nicht mahnende Liste aller noch nicht eingeordneten
Fragmente. Mahnend wäre: rote Zähler, "23 unbearbeitet". Nicht-mahnend wäre:
einfach da, durchsuchbar, mit der Möglichkeit "jetzt verknüpfen" oder "liegen
lassen" ohne Wertung — old-but-important-content darf nicht durch reine
Aktualität verdrängt werden (dasselbe Prinzip, das schon bei
`weltbild_builder.py`s Auswahlkriterien gilt: nicht nur die aktivsten, auch
die bedeutsamen älteren).

### 3.3 Knoten-Detail — die vier Leitfragen als Gerüst, nicht als Formular

Sinn & Ziel, Wissen & Fragen, Vorgehen, Concept Art — bereits im bestehenden
System als Leitfragen definiert. Wichtig für die UI: alle vier sind optional
und einzeln ausfüllbar, in beliebiger Reihenfolge, nicht als Wizard mit
Weiter-Buttons. Ein Knoten mit nur einer beantworteten Frage ist ein
vollwertiger Knoten, kein unfertiger.

Jeder Knoten zeigt seine Kanten zu anderen Knoten direkt im Detailbildschirm,
nicht nur im Canvas — sonst ist Mobile strukturell benachteiligt, weil der
Canvas dort am schlechtesten funktioniert.

### 3.4 Live-Wesen-Panel — Codewesen-Transparenz konkret

Direkt aus der Recherche von heute: ein Panel pro `Agent`/`LLM`-Knoten, das
zeigt was gerade passiert — angelehnt an das Smallville-Dashboard-Muster
(Memory-Stream, aktuelle Aktivität, gesendeter Prompt, live) kombiniert mit
einer Langfuse-artigen Knoten/Kanten-Spur für die letzten Entscheidungen.
Kein separates Tool, sondern dieselbe Knoten-Detail-Ansicht wie bei jedem
anderen Objekt — der `Agent`-Typ bekommt nur zusätzliche, live aktualisierte
Felder (Grundgesetz 8).

### 3.5 Canvas — bewusst als Desktop-Erweiterung, nicht als Basis

Der visuelle Knoten/Kanten-Graph ist wertvoll, aber auf einem Handy-Bildschirm
strukturell schwach (Pinch-Zoom auf einem komplexen Graph ist auf dem Sofa
etwas anderes als am Schreibtisch). Vorschlag: Canvas existiert vollwertig,
aber die Strom- und Detail-Ansichten sind nicht "vereinfachte Notlösungen"
davon, sondern gleichwertige, eigenständige Wege zu denselben Daten — passend
zum Ein-Körper-viele-Sichten-Prinzip.

---

## 4. Mobile-spezifisch, konkret

Share-Sheet-Integration: Text, Link oder Bild aus einer beliebigen anderen
App direkt als neuen Zwischenraum-Fragment übergeben können, ohne die App
selbst öffnen zu müssen — das ist vermutlich der meistgenutzte Erfassungsweg
unterwegs, nicht die App selbst.

Große Touch-Ziele, kein Canvas-Pinch als einzige Navigation. Wischgesten für
"nächstes/vorheriges Fragment im Strom" statt Karten exakt treffen müssen.

Schwache Verbindung einplanen — Erfassung muss lokal zwischenspeichern und
später synchronisieren, nicht bei jedem Tastendruck einen Request feuern.
Das Backend hat mit `fcntl.flock` + atomarem Schreiben bereits eine saubere
Server-Seite dafür; die Mobile-Seite braucht ein Pendant auf Client-Ebene
(Optimistic-UI + Konfliktanzeige bei `409`, das Backend liefert diesen Fall
bereits sauber statt stillem Überschreiben).

Push-Benachrichtigung, wenn ein KI-Strom auf ein von Daniel markiertes
Fragment reagiert hat — Live-statt-F5 auch außerhalb der offenen App, nicht
nur während sie offen ist.

---

## 5. Was bewusst NICHT rein sollte

Kein Pflicht-Onboarding-Formular vor der ersten Erfassung. Kein
Objekt-Typ-Auswahlzwang beim Anlegen. Keine Enterprise-Vokabel-Oberfläche
("Workspace", "Board", "Sprint") — die eigene Sprache des Systems
(Gesamtkonstrukt, Fragment, Zwischenraum, Knoten, Kante) ist schon da und
sollte auch in der UI stehen, nicht in generischem SaaS-Englisch übersetzt
werden.

Kein einzelner "Speichern"-Knopf, der das Gefühl gibt, vorher sei nichts
gesichert — das Backend arbeitet bereits atomar, die UI sollte das spürbar
machen (sofortiges visuelles Feedback bei jeder Änderung), nicht verstecken.

---

## 6. Was nur Daniel beantworten kann, bevor hier Code entsteht

Wie genau soll die Rolle der KI-Ströme in der UI sichtbar werden — eigene
Spalte/Avatar pro Strom, oder ein gemeinsamer "wer war zuletzt hier"-Streifen
pro Knoten?

Soll die Schnellerfassung ein Objekt sofort typisieren dürfen, wenn Daniel es
explizit sagt ("das ist eine Idee") — oder soll Typisierung strikt immer erst
im zweiten Schritt passieren, nie beim Erfassen selbst?

Wie weit soll die Mobile-Version wirklich reichen — reines Erfassen +
Lesen/Live-Beobachten, oder auch volle Bearbeitung inklusive Kanten ziehen?

---

## 7. Abgleich mit dem echten Tool (01.09., nachdem ich es zum ersten Mal gesehen habe)

Live durchgeklickt über CDP/Playwright-Zugriff auf den bereits offenen Browser
in `virtuellerdesktop1` (Chromium-Tab von ChatGPTs Arbeit). Hier ehrlich
abgeglichen, was von diesem blinden Entwurf trägt und was nicht.

**Bestätigt, nicht neu erfunden:** Die "ein Körper, viele Sichten"-Idee aus
Abschnitt 3.5 existiert im echten Tool bereits als Konzept — sechs Tabs
(Start/Canvas/Netz/Plan/Zeitspur/Replicas), gedacht als unterschiedliche
Sichten auf dieselben Daten. Es gibt sogar eine zweite Sektion namens
**"Gesamtkonstruktbetriebssystemkosmos"** — wortgleich mit Daniels eigenem
Arbeitstitel aus diesem Gespräch — mit einem Button "Körper". Das ist keine
neue Idee von mir gewesen, sondern Fortsetzung von etwas, das mit ChatGPT
schon begonnen wurde, nur nie zu Ende geführt.

**Der entscheidende Unterschied: Konzept vs. Umsetzung.** Alle sechs
Legacy-Tabs UND alle drei Buttons im Betriebssystemkosmos ("Ort"/"Körper"/
"Werkzeuge") sind reine Fassade — Klick ändert entweder nur ein Wort
("Bühne: Realgraph" statt "Bühne: Werkbank") oder gar nichts (Screenshot
vorher/nachher byte-identisch bei Körper/Werkzeuge). Kein Canvas wird
gerendert, keine Zeitleiste, kein Kanban. Die Lehre daraus für diesen
Entwurf hier: "viele Sichten auf einen Körper" zu benennen ist der leichte
Teil, jede einzelne Sicht tatsächlich zu bauen der schwere — mein eigener
Entwurf oben nennt zwar Screens, hat aber dasselbe Risiko, nur Namen statt
echter Umsetzung zu liefern, wenn's ans Bauen geht.

**Wo das echte Tool weiter ist als mein Entwurf:** Die Kachel "Ordner &
Dateien" öffnet einen echten, funktionierenden Dateibaum mit +Unterordner,
+Notiz, Umbenennen, Verschieben, **In Papierkorb** (Soft-Delete, passt zu
Grundgesetz 4). Mein Entwurf beschreibt Abschnitt 3.3 (Knoten-Detail) und
3.5 (Canvas) ausführlich, aber "Ordner & Dateien" als eigene, direkt
erreichbare Kachel — nicht Teil des Haupt-Erfassungsflusses — hatte ich so
nicht vorgesehen. Auch der Revisions-Konflikt-Mechanismus (`409`, den ich
in Abschnitt 4 nur theoretisch aus dem Backend-Code kannte) läuft im echten
Tool sichtbar: "KONFLIKTENTWURF GESICHERT · Server s389 ist neuer" — echt,
nicht nur Backend-Fähigkeit.

**Wo mein Entwurf einen echten, noch unadressierten Punkt trifft:** Die
Ordnerstruktur im echten Tool ist eine klassische Baum-Hierarchie (ein
Objekt hat einen Ordner-Pfad, verschoben statt mehrfach zugeordnet) — das
widerspricht direkt der additiven, mehrfachen Typisierung aus Abschnitt 3.1
("Idee UND Konzept gleichzeitig, oder keins von beiden"). Beide Modelle
können nicht gleichzeitig gelten, ohne dass eins das andere übersteuert.
Das ist eine echte, ungelöste Architektur-Frage, keine Kleinigkeit: bleibt
"Ordner" die Wahrheit (dann ist additive Typisierung nur ein Tag-Layer
obendrauf, keine Ersatz-Struktur), oder wird die Baum-Hierarchie selbst
irgendwann durch etwas Flexibleres abgelöst?

**Was in keinem der beiden Entwürfe existiert:** Das Live-Wesen-Panel
(Codewesen-Transparenz, Abschnitt 3.4) hat im echten Tool keine Entsprechung
— weder als Tab noch als Kachel. Genauso wenig die Mobile-Spezifika aus
Abschnitt 4 (Share-Sheet, Offline-Zwischenspeicher, Push). Der aktuelle
Chromium-Viewport im virtuellen Desktop ist knapp 500px hoch, nicht für
Mobile gedacht. Beides bleibt offener Bedarf, unabhängig davon welcher
Entwurf als Basis dient.

**Ungelöster Live-Fund, unabhängig von beiden Entwürfen:** der
Konflikt-Banner blieb über alle sechs Tab-Wechsel und alle Klicks hinweg
unverändert sichtbar — entweder ein echter, nie aufgelöster Konflikt im
Datenbestand, oder ein UI-Fehler der ihn nie abräumt. Nicht geklärt, nur
festgehalten.

---

## 8. Verbindung beider Ebenen (Daniel, 01.09.: "ich wollte was ganz
umstrukturiertes, das trifft nicht was ich brauche — daher will ich die 2
Ebenen verbinden")

Nicht: das echte Tool übernehmen. Nicht: meinen Entwurf isoliert weiterbauen.
Sondern: den echten, schon laufenden Server/Baum/Revisions-Unterbau
behalten, aber durch die Struktur führen, die tatsächlich trägt — und genau
dafür liefert das echte Tool selbst schon das Gerüst, nur unbebaut: die drei
Buttons **Ort / Körper / Werkzeuge** aus dem Betriebssystemkosmos.

**Vorschlag, zur Diskussion, keine fertige Entscheidung von mir allein:**

- **Ort** = die reale Baum-Hierarchie, die schon existiert und funktioniert
  (`data/tree/`, "Ordner & Dateien"-CRUD, Verschieben/Papierkorb). Bleibt
  genau wie sie ist — ein Pfad pro Objekt, nicht mehrfach. Löst NICHT das
  additive Typisierungs-Problem, muss es auch nicht — Ort beantwortet nur
  "wo liegt das physisch", nicht "was ist das".
- **Körper** = genau der Ort, an dem die additive, mehrfache Typisierung aus
  Abschnitt 3.1 tatsächlich hingehört — nicht als Ersatz für den Ordnerbaum,
  sondern als eigene, parallele Eigenschaft: was ein Objekt IST (Idee,
  Konzept, beides, keins), unabhängig davon WO es liegt. Damit lösen sich
  die zwei Modelle aus Abschnitt 7 nicht gegenseitig ab, sie beantworten
  zwei verschiedene Fragen, die beide schon im Namen "Körper" (dein eigenes
  "ein Körper, viele Sichten"-Prinzip) angelegt sind.
- **Werkzeuge** = dahin gehören Canvas/Netz/Plan/Zeitspur/Replicas — nicht
  als sechs falsche Fassaden-Tabs auf oberster Ebene, sondern als
  Werkzeug-Auswahl, die man auf einen Ort/Körper anwendet. Genau das war die
  Lücke, die die Legacy-Tabs nie gefüllt haben (Klick änderte nur ein Wort).

Die Schnellerfassung aus Abschnitt 3.1 bekommt dadurch eine klare Landung:
ein neues Fragment kriegt automatisch einen Ort (Standard: ein
Zwischenraum-Ordner, kein Zwang zur Entscheidung), aber keinen Körper-Typ —
der kommt erst später dazu, additiv, wenn überhaupt.

**Was das noch nicht klärt, bewusst offen gelassen:** ob "Werkzeuge" pro
Ordner (Ort) oder pro Objekt (Körper) ausgewählt werden — ein ganzer Ordner
im Canvas-Werkzeug ansehen ist etwas anderes als ein einzelnes Fragment im
Replica-Studio zu öffnen. Das ist die nächste Architektur-Frage, die
Daniel entscheiden muss, keine, die sich aus dem bisher Gesagten von selbst
beantwortet.
