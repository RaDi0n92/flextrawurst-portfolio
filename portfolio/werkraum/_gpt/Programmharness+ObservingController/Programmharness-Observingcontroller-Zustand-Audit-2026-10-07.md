# Programmharness + Observing Controller for AI-Beings
## Zustandsbild, Audit und ehrliche Einschätzung

**Stand: 7. Oktober 2026**

Diese Datei ist keine Entwicklungs-, Fehler- oder Verlaufsdokumentation. Sie beschreibt den heutigen Zustand, prüft ihn gegen das beabsichtigte System und hält fest, was ich inzwischen als eigentliches Ziel dieses Arbeitskörpers verstehe.

---

## 1. Mein Verständnis dessen, was hier eigentlich entstehen soll

Der Arbeitstitel **„Programmharness + Observing Controller for AI-Beings“** beschreibt wesentlich mehr als ein Dashboard für technische Zustände.

Gemeint ist eine Arbeitsumgebung, in der AI-Beings tatsächlich arbeiten können und ihr laufendes Tun zugleich beobachtbar, steuerbar und korrigierbar wird.

Der Mittelpunkt ist nicht die Logdatei, nicht die Regel und nicht das Dashboard selbst. Der Mittelpunkt ist das AI-Being während einer Aufgabe.

Ein AI-Being soll einen Auftrag haben, Mittel benutzen, Zustände verändern, Ergebnisse erzeugen und dabei eine reale Möglichkeit bekommen zu bemerken, wenn es sich verrennt. Es soll sagen können: Ich wiederhole gerade denselben erfolglosen Schritt. Mir fehlt ein Teil der Datei. Mein letzter Versuch hat den Zustand nicht verändert. Ich habe etwas nur vermessen, aber nicht gelesen. Mein Text beantwortet die Aufgabe noch nicht. Ich komme hier nicht weiter.

Der **Program Harness** soll dafür den Arbeitskörper tragen: Auftrag, Werkzeuge, Rechte, Zwischenzustände, laufende Arbeit, Übergänge, Rücksprünge, Wiederaufnahme und gegebenenfalls mehrere beteiligte AI-Beings.

Der **Observing Controller** soll nicht nachträglich Logs bewerten. Er soll parallel zum laufenden Tun beobachten, ob Handlung und Wirkung zusammenpassen. Er soll relevante Abweichungen noch im Arbeitsmoment zurückgeben, solange das AI-Being seinen Kurs ändern kann.

Die **Augen-&-Hände-Bridge** ist dabei ein Wahrnehmungs- und Handlungskanal in sichtbare Arbeitsumgebungen. Sie ist ein Teil des Systems, nicht dessen Gesamtzweck.

Für Daniel soll daraus kein Überwachungsjob entstehen. Er soll nicht hundert Rohereignisse lesen und aus ihnen selbst rekonstruieren müssen, was schiefging. Er soll einen verständlichen Arbeitszustand sehen, eingreifen können, wenn seine Entscheidung gebraucht wird, und ansonsten beobachten können, wie die AI-Beings arbeiten, korrigieren, warten, übergeben und weiterkommen.

Damit ist das Ziel weder „Agenten-Dashboard“ noch „Harness-Adminseite“. Es ist näher an einem **Betriebssystem und Arbeitsraum für AI-Beings**, in dem Beobachtung, Steuerung, Kommunikation, Rechte, Lernen und laufende Arbeit zusammenkommen.

---

## 2. Was heute tatsächlich existiert

Unter dem jetzigen System liegt bereits ein substantieller technischer Körper.

Vorhanden sind unter anderem:

- persistente Harness-Schichten mit CORE, PROJECT, TASK und EPHEMERAL;
- getrennte Desired-, Effective- und Health-Zustände;
- globale und einzelne Zustandssteuerung;
- Gründe, Actor, TTL und Ereignisverläufe;
- TASK-Scope als vorgeschaltete Arbeitsgrenze;
- Aktionsklassifikation und Arbeitsmodi;
- Control-Leases;
- Direktiven mit Originalwortlaut, Ableitungen und Autoritätsstatus;
- Resonanz, Kommentare, Bewertungen und strukturierte Vorschläge;
- getrennte Daniel-/ChatGPT-Kommunikationswege;
- eine Lernpipeline mit Kandidaten, Tests, Aktivierung, Abschwächung und Stilllegung;
- Parent-/Child-Beziehungen zwischen Harness-Schichten;
- persistierter Kontext zu Schichten;
- ein Live-State aus dem tatsächlichen Harness-Unterbau statt aus einer statischen Demo;
- Grundlagen für AI-Streams außerhalb der aktuellen Dashboard-Oberfläche.

Der aktuelle Live-Snapshot zeigt:

- Master: **ACTIVE / HEALTHY**
- 12 wirksame Schichten
- 0 pausierte Schichten
- 0 durch Parent blockierte Schichten
- 0 technisch gestörte Schichten
- 2 abgelaufene Schichten
- 1 EPHEMERAL-Schicht
- keine aktive ChatGPT-Control-Lease
- ChatGPT-Inbox: 0 offen

Das ist kein Mockup. Die darunterliegenden Steuer- und Zustandsfunktionen existieren tatsächlich.

---

## 3. Was das heutige Dashboard wirklich ist

Nach vollständiger manueller Bedienung ist mein Urteil deutlich härter als nach dem reinen Codevergleich:

**Die aktuelle Oberfläche ist im Kern ein sehr langer Verwaltungs-, Erklär- und Ereignisfeed über einem bereits recht substantiellen Harness-Backend.**

Sie besitzt echte Controls. Sie ist deshalb nicht bloß read-only.

Aber ihre Grundform ist trotzdem falsch für das beabsichtigte System.

Fast alles liegt vertikal untereinander:

- Gesamtzustand
- Aufmerksamkeit
- Inboxen
- globale Controls
- Control-Leases
- Struktur
- Layerkarten
- Definitionen
- Kontext
- Historie
- Direktiven
- Lernregeln
- Resonanz
- gemeinsame Resonanzspur
- Begriffserklärungen

„Alltag“ und „Voll“ reduzieren beziehungsweise erweitern diesen Feed. Suche, Filter, Strukturbaum und einklappbare Details helfen bei der Orientierung. Sie ändern aber nicht die eigentliche Informationsarchitektur.

Es gibt keine tragende Aufteilung in echte Arbeitsbereiche, zwischen denen man wie in einem Betriebssystem wechselt. Es gibt keine klare räumliche Trennung von laufender Arbeit, AI-Beings, Steuerung, Bau/Editieren, Lernen, Direktiven, Kommunikation und Historie.

Dadurch entsteht beim Benutzen nicht das Gefühl:

> „Hier betreibe und forme ich ein System.“

Sondern eher:

> „Hier lese ich sehr viele Informationen über das System und finde zwischen ihnen einzelne Aktionen.“

Das ist der zentrale Befund der manuellen Abnahme.

---

## 4. Steuerbarkeit: technisch real, als Gesamtsystem noch nicht ausreichend

Die einzelnen Controls sind keine Attrappen.

Globales Aktivieren/Fortsetzen, Arbeitsmodus, Layerzustände, dynamische Schichten, TTL, Definitionen, Historie, Resonanz, Inbox, Direktiven und Leases sind echte Pfade.

Auch Rechte sind inzwischen klar unterscheidbar: ChatGPT kann sich nicht selbst sensible Steuerrechte geben. CORE-Änderungen können nicht einfach lokal von ChatGPT überschrieben werden. Vorschlag und direkte Änderung sind unterschiedliche Dinge.

Trotzdem ergibt die Summe dieser Controls noch keinen Betriebssystem-Controller.

Der Grund ist nicht fehlende Buttonanzahl.

Es fehlt eine Ebene, auf der Daniel das **System als System** manipuliert:

- Welche AI-Beings existieren gerade?
- Welchen Auftrag hat jedes?
- Was tut es in diesem Moment?
- Woran arbeitet es?
- Wo hängt es?
- Was hat der Controller gerade beobachtet?
- Welche Rückmeldung bekam das AI-Being?
- Hat es darauf seinen Weg verändert?
- Welche Zwischenzustände gehören zu seinem aktuellen Versuch?
- Wo kann es zurücksetzen oder verzweigen?
- Welche Werkzeuge, Rechte und Umgebungen gehören zu diesem Arbeitsstrom?
- Welche anderen AI-Beings sind beteiligt?
- Was wurde übergeben?
- Was wartet auf Daniel?
- Was darf Daniel direkt verändern?
- Welche Struktur möchte Daniel neu anlegen oder umbauen?

Diese Ebene existiert heute nicht als zusammenhängender Bedienraum.

---

## 5. Editierbarkeit: vorhanden, aber nicht in der Form, die der Zielkörper braucht

Im heutigen Dashboard können Dinge tatsächlich geändert werden.

Layerdefinitionen können bearbeitet werden. Dynamische Schichten können angelegt werden. Zustände können verändert werden. Kommentare, Bewertungen und Vorschläge können geschrieben werden. Direktiven und Lernregeln besitzen Verwaltungswege.

Deshalb wäre die Aussage „gar nichts editierbar“ technisch falsch.

**Aber Daniels Kritik „keine Editierbarkeit“ trifft die Erfahrung der Oberfläche trotzdem.**

Denn Editieren ist momentan eine lokale Fähigkeit innerhalb einzelner Karten und aufgeklappter Details. Es gibt keinen eigentlichen Editiermodus für den Arbeitskörper.

Es fehlt ein Ort, an dem man:

- Strukturen baut und umordnet;
- neue Funktionsbereiche erfindet;
- Beziehungen zwischen Bestandteilen verändert;
- AI-Beings und Arbeitsströme zusammensetzt;
- Zuständigkeiten und Übergaben formt;
- Controller-Beobachtungen mit laufenden Arbeitszuständen verbindet;
- neue Arbeitslogik sichtbar in einen bestehenden Zusammenhang einsetzt.

Das vorhandene „neue Layer anlegen“ ist dafür zu klein.

Es ist ein Formular zum Erzeugen einer Schicht, kein Systemeditor.

---

## 6. Der Observing Controller ist bisher mehr Behauptung und Unterbau als sichtbare Realität

Hier liegt für mich die größte konzeptionelle Lücke.

Die beiden Agenten-Papers machen deutlich, dass der Observing Controller **im laufenden Arbeitsmoment** wirken soll.

Er soll nicht nur wissen, dass ein Toolaufruf stattfand.

Er soll beispielsweise feststellen können:

- derselbe Versuch wurde wiederholt, ohne dass sich der Zustand änderte;
- ein erwarteter GUI-Zustand trat nicht ein;
- ein Abschnitt wurde nie tatsächlich gelesen;
- ein mechanischer Dateiweg wird sprachlich als inhaltliches Lesen oder Schreiben ausgegeben;
- ein Reviewer bekam nur eine Zusammenfassung statt des Originals;
- eine Aktion wurde blockiert und der Agent rennt erneut gegen denselben Block;
- Handlung und behauptetes Ergebnis passen nicht zusammen;
- ein neuer Versuch unterscheidet sich in Wirklichkeit gar nicht vom vorigen.

Und diese Beobachtung soll anschließend wieder **in den laufenden Denk- und Handlungskreislauf des AI-Beings** gelangen.

Das heutige Dashboard zeigt Zustände, Historien, offene Gegenprüfungen, Regeln und Resonanz.

Es zeigt aber noch keinen lebenden Kreislauf:

**Versuch → Beobachtung → erkannte Abweichung → Rückmeldung an AI-Being → veränderte Strategie → neuer Versuch → unmittelbare Gegenprobe.**

Genau dieser Kreislauf ist nach meinem heutigen Verständnis der eigentliche Kern des Observing Controllers.

Solange dieser Kreislauf nicht als reale Laufzeitfunktion existiert und im System sichtbar wird, ist „Observing Controller“ für den Gesamtzustand noch zu groß als Bezeichnung.

---

## 7. AI-Beings fehlen ausgerechnet in der Oberfläche für AI-Beings

Im Sollbild und in den vorhandenen VPS-Grundlagen tauchen mehrere AI-Ströme beziehungsweise AI-Beings auf.

Im aktuellen Dashboard fehlt daraus aber der zentrale Arbeitsraum.

Es gibt keine erste Klasse „AI-Being“ in der Oberfläche, über die Daniel direkt sieht:

- Identität/Quelle des Stroms;
- aktuelle Session;
- aktueller Auftrag;
- Arbeitszustand;
- letzte relevante Handlung;
- wahrgenommener Zustand;
- Blocker;
- Controller-Hinweis;
- eigener gemeldeter Zweifel/Fehler;
- nächste geplante Handlung;
- Wartezustand;
- Übergaben;
- Ergebnis;
- benötigte Entscheidung.

Damit fehlt dem heutigen Dashboard genau das Objekt, um das der Arbeitstitel eigentlich kreist.

Der Harness wird sichtbar.

Die AI-Beings beim Arbeiten werden es noch nicht.

---

## 8. Die Scheuklappen-Idee ist ebenfalls noch nicht Teil des fertigen Körpers

Der spätere strenge Wunsch war nicht bloß Session-IDs zu speichern.

Eine normale AI-Session soll grundsätzlich nur ihren eigenen Auftrag und Arbeitsraum sehen und möglichst gar nicht automatisch mitbekommen, was andere Sessions tun.

Ein Leitstellen-/Observerblick darf mehr sehen, aber dieser Blick ist eine andere Rolle.

Diese Trennung ist für das geplante System wichtig, weil sonst „mehrere AI-Beings beobachten“ leicht dazu führt, dass alle Sessions unbeabsichtigt einen gemeinsamen Informationsraum bekommen.

Der frühere Codecheck fand dafür keine vollständige Runtime-Sichtisolierung.

Daran ändert die heutige Dashboard-Bedienung nichts.

Damit fehlt weiterhin ein fundamentaler Bestandteil des Multi-AI-Zielbilds.

---

## 9. Lernen ist substantiell, aber noch nicht dasselbe wie ein lernendes Betriebssystem

Die vorhandene Selbstlernschleife ist einer der interessanteren technischen Teile.

Sie trennt Kandidaten, Tests, Aktivierung, Abschwächung und Stilllegung. Eine Kandidatenregel wird nicht allein durch ihre Existenz aktiv. Alte Erfahrungen können zur Gegenprüfung benutzt werden.

Das ist wesentlich besser als ein System, in dem das Modell nach einem Fehler spontan eine neue ewige Regel erfindet.

Trotzdem bleibt die sichtbare Lernoberfläche heute wieder eine lange Folge von Karten.

Und noch wichtiger:

Ein lernender Regelkörper ist nicht automatisch dasselbe wie ein Agent, der **während einer konkreten Aufgabe merkt, dass er feststeckt, seine Strategie ändert und sofort prüft, ob die Änderung geholfen hat**.

Das eine kann das andere unterstützen.

Es ersetzt es nicht.

---

## 10. Was heute bereits wirklich trägt

Trotz des harten Gesamturteils wäre es falsch, den vorhandenen technischen Körper als wertlos abzuschreiben.

Tragfähig wirken vor allem:

### Persistenter Harness-Zustand

Zustände, Gründe, Actor, TTL, Historien und Definitionen sind nicht bloß Frontend-Dekoration.

### Trennung verschiedener Zustandsbegriffe

Desired, Effective und Health getrennt zu halten, ist richtig und wichtig.

### Task-Scope als eigene Arbeitsgrenze

Der Auftrag kann technisch vor anderen normalen Aktionsentscheidungen berücksichtigt werden.

### Rechte und Control-Leases

Die Idee, AI-Beings nicht pauschal alles steuern zu lassen, sondern gezielt und widerrufbar Rechte zu geben, passt zum Zielsystem.

### Direktiven als eigener Körper

Originalwortlaut, abgeleitete technische Bedeutung und Autorität nicht einfach zusammenzuwerfen, ist eine wichtige Grundlage.

### Resonanz und Vorschläge

Daniel und ChatGPT können an einem Baustein unterschiedliche Einschätzungen hinterlassen. Strukturierte Vorschläge sind von direkter Änderung getrennt.

### Lernpipeline

Kandidat, Test und Aktivierung sind getrennte Schritte. Regeln können später wieder geschwächt oder stillgelegt werden.

### Live-Anbindung

Das Dashboard arbeitet mit dem tatsächlichen Harness-State und nicht mit statischen Beispielkarten.

Diese Bestandteile können in einem späteren wirklichen Programmharness + Observing Controller weiterleben.

Das Problem ist weniger, dass nichts gebaut wurde.

Das Problem ist, dass die vorhandenen Teile noch nicht zu dem beabsichtigten Gesamtorganismus zusammengesetzt sind.

---

## 11. Was nur nach mehr Fertigstellung aussieht, als es tatsächlich bedeutet

Einige vorhandene Funktionen verführen zu einem zu positiven Urteil.

### Strukturbaum

Ein Parent-/Child-Baum plus Sprunglinks ist Navigation innerhalb des Feeds.

Er ist noch keine Arbeitsarchitektur des Betriebssystems.

### Alltag / Voll

Das Verstecken fortgeschrittener Bereiche reduziert Informationsmenge.

Es ersetzt keine echten Bereiche, Tabs oder Arbeitsräume.

### Layer editieren

Texte und Zustände eines Layers ändern zu können bedeutet nicht, dass der Systemkörper editierbar geworden ist.

### Live-Polling

Sekündlicher State-Refresh macht den Zustand frisch.

Er macht daraus noch keinen Observing Controller, der laufende Handlung und Wirkung semantisch verfolgt.

### Lernkarten

Viele sichtbare Lernregeln zeigen, dass es eine Lernpipeline gibt.

Sie zeigen noch nicht, dass ein AI-Being im Arbeitsmoment sinnvoll selbstkorrigierend geworden ist.

### Resonanzspur

Eine gute Kommunikationshistorie ist nützlich.

Sie ist nicht der laufende Controller-Feedbackkanal selbst.

Diese Unterschiede waren im reinen Codeaudit zu wenig gewichtet.

---

## 12. Ehrliche Einordnung des heutigen Gesamtsystems

Wenn ich dem aktuellen Stand heute einen möglichst präzisen Namen geben müsste, wäre es ungefähr:

**Ein substantieller Harness-Unterbau mit Live-Control-Plane, Verwaltungs-, Erklär-, Direktiven-, Lern- und Resonanzoberfläche.**

Das ist deutlich mehr als ein Statusdashboard.

Aber:

**Es ist noch kein Betriebssystem für AI-Beings.**

Und:

**Es ist noch kein vollständiger Observing Controller im Sinne der beiden Agenten-Papers.**

Der heutige Körper verwaltet und erklärt vor allem den Harness.

Der geplante Körper soll AI-Beings **beim tatsächlichen Arbeiten** tragen, beobachten und steuerbar machen.

Das ist keine kosmetische Differenz.

Es ist der Unterschied zwischen einer Verwaltungsoberfläche für Infrastruktur und einem Arbeitsbetriebssystem, in dem die laufenden Akteure selbst erste Klasse sind.

---

## 13. Woran ich den Zielzustand künftig messen würde

Ich würde das System erst dann ehrlich als den beabsichtigten Programmharness + Observing Controller for AI-Beings bezeichnen, wenn folgende Dinge zusammenkommen:

1. **AI-Beings sind sichtbare erste Klasse des Systems.**
   Nicht nur Layer oder Session-IDs, sondern laufende Arbeitskörper mit Auftrag, Zustand, Handlung, Blocker, Ergebnis und Übergaben.

2. **Die Oberfläche besitzt echte Arbeitsräume statt eines Gesamtfeeds.**
   Überblick, AI-Beings, laufende Arbeit, Harness-Struktur, Controller, Lernen, Direktiven, Resonanz und Historie müssen als unterscheidbare Räume navigierbar sein.

3. **Der Systemkörper ist wirklich editierbar.**
   Nicht nur Felder in Karten, sondern Strukturen, Beziehungen, Arbeitsströme, Zuständigkeiten und neue Bestandteile können bewusst geformt werden.

4. **Der Observing Controller arbeitet im Moment der Handlung.**
   Er verfolgt erwartete und tatsächliche Wirkung und liefert relevante Abweichungen zurück, bevor der Agent stumpf weiterläuft.

5. **Selbstkorrektur verändert den nächsten Versuch.**
   „Zurückgehen“ bedeutet nicht Wiederholen, sondern eine andere Annahme, einen anderen Pfad, andere Eingabe oder andere Prüfmethode.

6. **Arbeitsbehauptungen bleiben an tatsächliche Arbeit gebunden.**
   Messen, Lesen, Schreiben, Formatieren, Prüfen und Zusammenfassen dürfen nicht sprachlich ineinander verschwimmen.

7. **Observerblick und normale Session-Sicht sind getrennt.**
   Multi-AI-Beobachtung darf die Scheuklappen einzelner Sessions nicht zerstören.

8. **Daniel sieht das Wesentliche, nicht den Maschinenkeller.**
   Er sieht, wer arbeitet, wer hängt, wer korrigiert, was seine Entscheidung braucht und wo er eingreifen kann.

9. **Der Controller ist Teil des Arbeitskreislaufs.**
   Nicht nur Log, nicht nur Audit, nicht nur Regelwerk.

---

## 14. Mein abschließendes Verständnis

Ich glaube inzwischen, dass die ursprüngliche Idee leicht falsch verstanden werden kann, wenn man zu früh auf Begriffe wie Harness, Dashboard, LangGraph, PostgreSQL, MCP, Regeln oder Logs schaut.

Diese Dinge sind Mittel.

Der eigentliche Entwurf ist ein **Arbeitsökosystem für AI-Beings**.

Ein AI-Being soll nicht nur eine Antwortmaschine sein, die einen Auftrag erhält und irgendwann ein Ergebnis ausspuckt.

Es soll innerhalb eines Arbeitskörpers handeln können.

Dieser Arbeitskörper soll mitbekommen, was tatsächlich geschieht.

Ein zweiter Blick soll Wirkung und Behauptung gegeneinander halten können.

Das AI-Being soll diese Beobachtung noch benutzen können, solange die Aufgabe läuft.

Es soll Fehler nicht nur produzieren und später erklärt bekommen, sondern eine reale Gelegenheit erhalten, sie zu bemerken, auszusprechen, zurückzugehen und anders weiterzuarbeiten.

Mehrere AI-Beings sollen darin existieren können, ohne automatisch gegenseitig ihre Arbeit zu sehen.

Daniel soll darüber stehen können, ohne zum Mikromanager jedes Klicks zu werden.

Er soll Strukturen schaffen, verändern und freigeben können. Er soll sehen können, wann ein AI-Being selbst weiterkommt und wann menschliche Resonanz gebraucht wird.

Das Dashboard ist deshalb nicht bloß Darstellung des Harness.

**Es ist die sichtbare, bedienbare Seite dieses Betriebssystems.**

Und genau daran scheitert der heutige Stand noch am deutlichsten:

Der technische Unterbau ist bereits ernstzunehmend.

Die Oberfläche zeigt viel davon.

Aber sie macht daraus noch keinen Ort, an dem AI-Beings als lebende Arbeitsströme organisiert, beobachtet, verändert und geführt werden.

---

# Schlussurteil

Der bisherige Bau hat **mehr Substanz im Unterbau als die aktuelle Oberfläche vermuten lässt**.

Gleichzeitig hat die Oberfläche **mehr Funktionen, als ihr Gesamtgefühl rechtfertigt**.

Das reine Codeaudit hat deshalb zu positiv gewirkt.

Die manuelle Bedienung zeigt:

**Der Harness-Unterbau ist weit genug entwickelt, dass Weiterbauen sinnvoll ist.**

**Der heutige sichtbare Körper ist aber noch hauptsächlich Control-Plane + Feed + Verwaltung.**

**Der eigentliche Programmharness + Observing Controller for AI-Beings ist als Gesamtorganismus noch nicht da.**

Die größte fehlende Sache ist nicht ein weiterer Button.

Es fehlt die Transformation von einer langen Verwaltungsseite über Harness-Bestandteile zu einem **wirklichen Arbeits- und Betriebssystem für laufende AI-Beings**, in dem Beobachtung, Steuerung, Selbstkorrektur, Kommunikation, Rechte und Struktur nicht nur vorhanden, sondern als ein zusammenhängender lebender Arbeitsraum erfahrbar sind.
