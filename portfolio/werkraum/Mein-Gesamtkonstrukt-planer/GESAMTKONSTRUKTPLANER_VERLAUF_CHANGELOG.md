# Mein Gesamtkonstrukt – Entstehungsverlauf / Changelog / Dokumentationsspur

> **Historischer Arbeitstitel / Ordnername:** Gesamtkonstruktplaner / `Mein-Gesamtkonstrukt-planer`
> **Gegenstand:** der entstehende gemeinsame Arbeits-, Konstruktions- und Durchführungskörper als Ganzes. Der „Planer“ ist darin nur eine Entwicklungsbezeichnung bzw. eine seiner Arbeitsformen.
> **Status:** laufende Entwicklung und Provenienzspur, noch keine endgültige Begriffs- oder Architekturfestlegung
> **Zweck dieser Datei:** Änderungen, Herkunft, Beobachtungen, Entscheidungen, reale Durchführungen und offene Spuren in zeitlicher Reihenfolge zusammenhalten. Kein nachträglich glattgebügelter Projektbericht und keine Reduktion des Gegenstands auf eine Planungsoberfläche.

---

## 2026-08-22 – Spurensuche: Wie aus Vorläufern ein Gesamtkonstrukt wurde

### Ausgangspunkt
Daniel fordert ausdrücklich, nicht nur den letzten sichtbaren Arbeitsstand anzuschauen, sondern mit einer **Spurensuche zum Beginn** anzufangen: erster Auftrag, erste berührte/angelegte Dateien, frühe Abzweigungen und die Kette, aus der der heutige Zustand hervorgegangen ist.

Die Suche soll nicht einfach einen aktuellen Projektzustand beschreiben, sondern nachvollziehbar machen, **wie aus kleinen Arbeitsaufträgen schrittweise ein größerer zusammenhängender Arbeitskörper wurde**.

### Aktueller Suchbefund – Entstehungsstrang rund um die aktuelle ChatGPT-Work-Session

**Bestätigt:** Die erste belastbare Server-Spur des heutigen Arbeitskörpers liegt nicht bei Codex oder Claude Code, sondern im unmittelbaren Vorgänger des Planers: `/root/werkraum/arbeitskoerper-redteam-22/`.

Bisher rekonstruierte Reihenfolge, Zeiten in Europe/Berlin:

- **03:56:10** – frühester derzeit gefundener Dateifußabdruck im Vorgängerkörper: `arbeitskoerper.html.gz.b64`.
- **03:56:20–03:57:44** – der Körper wird über lokale HTTP- und anschließend HTTPS-Testserver gestartet; PID-, Log- und Serverdateien entstehen.
- **04:13:01** – `update.zst` wird geschrieben.
- **04:39:52** – `deep-update.zst.b64` folgt.
- **11:09:45** – `mobile-390.html` dokumentiert bzw. rahmt einen echten 390×844-Mobile-Testkörper.
- **14:22:15** – der in `index.html` eingebettete Arbeitsstand wird als `embedded-r5-mt4clt3r` exportiert; der Zustand trägt bereits den Titel **„Mein Gesamtkonstrukt“**, Revision 3 und den Zweck, aus Ideen, Dateien, Wissen, Plänen und Automationen ein übergebbares Ganzes zu formen.
- **15:38:24** – im neuen Ordner `/root/werkraum/Mein-Gesamtkonstrukt-planer/` liegt die README des servergespeicherten Planers.
- **15:38:37** – das eigene Planner-Ereignislog protokolliert `planner.server_truth.created`, Revision 1, ausdrücklich migriert aus `/root/werkraum/arbeitskoerper-redteam-22/index.html`.
- Danach folgen laufende Serverrevisionen und weitere Ausbauarbeiten am gemeinsamen Arbeitskörper.

**Wichtig:** 03:56:10 ist nur der früheste bisher gefundene **VPS-Dateifußabdruck**. Die Work-Session selbst reicht nachweislich weiter zurück.

### Vorgeschichte vor dem Workflow-Canvas: ClaudeWeb-Ursprungsdatei

**Vom Nutzer ausdrücklich bestätigt:** Noch **vor** `workflow-canvas.html` stand eine Ursprungsdatei aus **ClaudeWeb**. Der Strang wurde anschließend zu ChatGPT/Work weitergetragen, weil ClaudeWeb für diesen Arbeitsmodus zu teuer wurde und Claude den eigentlichen gewünschten Arbeitskörper aus Nutzersicht nicht ausreichend verstanden bzw. getroffen hatte.

Der konkrete Dateiname dieser ClaudeWeb-Ursprungsdatei ist in der bisherigen Library-, VPS- und Chat-Rücksuche noch **nicht sicher wiedergefunden**. Diese Herkunft wird deshalb als bestätigte Nutzer-Provenienz geführt, aber noch nicht mit einem erfundenen Dateinamen, Zeitstempel oder Hash versehen.

Damit ist `workflow-canvas.html` nicht mehr als absoluter Ursprung zu lesen, sondern als **erste derzeit artefaktisch wiedergefundene ChatGPT-Weiterverarbeitung eines bereits vorhandenen ClaudeWeb-Vorläufers**.

### Erster wiedergefundener ChatGPT-Artefaktstrang: Workflow-Canvas am 21.08.

**Bestätigt durch die Chatspur:** Bereits am **21.08.2026 gegen 12:55–12:57 Europe/Berlin** liegt der direkte Dateiauftrag vor, aus dem `workflow-canvas.html` hervorgeht:

- **ca. 12:55** – Nutzer fragt: `Was passiert an diesem Punkt im Ablauf?`
- **ca. 12:56** – Nutzer fordert für **jeden Workflow und jeden Graphen alle Knoten, alle Verbindungen und die Details als Markdown-Datei**.
- **ca. 12:57** – Nutzer: `Und bitte bau daraus eine Datei.`
- Unmittelbare Assistenzantwort: Die Datei **`workflow-canvas.html`** sei erstellt.

Ein noch früherer tatsächlicher Nutzerturn, der diese konkrete Graph-/Workflow-Idee einleitet, konnte trotz Rückwärtssuche bisher nicht belastbar wiedergewonnen werden. Damit ist **12:55** derzeit die äußerste sichere Gesprächskante, nicht 21:40 und nicht der VPS-Start.

**Bestätigt durch das erhaltene Artefakt:** `workflow-canvas.html` ist ein eigenständiger n8n-artiger Graphkörper. Sein sichtbarer Leitsatz lautet **„Der Graph ist die Datei“**. Er besitzt bereits Zoom, frei bewegliche/editierbare Knoten, Verbindungen, eigene Knotentypen, Markdown-Upload, Suche und Export. Im großen Knoten-Editor stehen ausdrücklich getrennte Felder dafür, was ein Agent wie Claude Code/Codex/Gemini CLI übernehmen könnte und was der Mensch selbst editieren oder erfinden will.

Der Canvas enthält außerdem bereits echte Flextrawurst-Arbeitsfelder als `Ist-Zustand → Auftrag`, darunter GENI, Knoten/Kanten, KompOase, Flarum, dak+gord-system, zensi, Toolbox, Surface, AI-Strom-Brücke und die 490-Punkte-Quellliste. Er war also von Beginn an mehr als eine dekorative Demo: vorhandenes Projektmaterial wurde in einen bearbeitbaren Ablauf-/Graphkörper übersetzt.

**Zeitnaht:** Die heute sichtbare Library-Kopie von `workflow-canvas.html` trägt erst **17:26:20** als Library-Erstellzeit. Das widerspricht der Chatspur um 12:57 nicht zwingend; es belegt vielmehr, dass Library-Registrierung und ursprüngliche Dateierzeugung nicht gleichgesetzt werden dürfen. Zehn Minuten nach der Library-Kopie erscheint `konzepte dokus etc.zip`, dessen Inhalte stark mit den im Canvas eingebauten Flextrawurst-Bereichen überlappen. Eine Kausalrichtung zwischen ZIP und Canvas wird daraus ausdrücklich **nicht** behauptet.

### Bewusster Sprung vom Workflow-Canvas zum breiteren Arbeitskörper

**Bestätigt durch die Chatspur:** Um **14:05:16 Europe/Berlin** formuliert der Nutzer den nächsten entscheidenden Auftrag ausdrücklich als Erweiterung **über den Workflow-Canvas hinaus**: Es brauche einen lokalen Arbeitsraum, der Ideen, Dokumente, Dienste, Systeme, Menschen und Agenten verbinden könne; Herkunft und Realität dürften nicht erfunden werden; Quellen müssten aufnehmbar sein; Realgraph sowie Wahrheit/Herkunft sichtbar werden; lokale Revisionen und `Festschreiben` müssten Änderungen nachvollziehbar halten; Übergabe an Mensch und LLM sowie Datei-/ZIP-/Markdown-Import seien erforderlich.

Dieser Auftrag entspricht direkt der später erhaltenen Architektur des generischen **`Arbeitskörper`**.

**Bestätigte Brücke um 18:09 Europe/Berlin:** In der Library entstehen `ARBEITSKOERPER_BAUAUFTRAG.md` und `ARBEITSKOERPER_BAUPAKET.zip`. Das Baupaket enthält exakt drei Bestandteile: den vorhandenen `workflow-canvas.html`, das reale Quellenpaket `konzepte dokus etc.zip` und den Bauauftrag. Damit ist die Übergabe vom Prototyp plus Realmaterial zum breiteren Arbeitskörper ausdrücklich verpackt und nicht nur nachträglich vermutet.

Der Bauauftrag sagt ausdrücklich, es gehe **nicht** um einen hübscheren n8n-Klon oder dekorativen Wissensgraphen. Aus `workflow-canvas.html` soll ein realer Arbeitskörper werden, der Dateien, Dienste, Ideen, Konzepte, Dokumentationen, Systeme, Wesen, Menschen, LLM-Ströme, Agenten, Werkzeuge, Automationen, Prompts, Entscheidungen, Fragen und Workflows aufnehmen, bearbeiten, verbinden, versionieren und weitergeben kann. Der vorhandene Canvas war zu diesem Zeitpunkt bereits praktisch geprüft mit **42 Knoten und 21 gerichteten Verbindungen**. Das ZIP mit realem Flextrawurst-Material wird als erster echter Importkörper festgelegt. Der Auftrag definiert außerdem reale Knoten/Kanten, Herkunft, getrennte Statusdimensionen, Ereignisspuren, Softdelete, Workflow-Werkstatt, Realgraph, Import, Arbeitszustände, Harness und konkrete Playwright-Abnahmetests.

Die erhaltenen Offline-Fassungen enthalten anschließend als Systemkern unter anderem:

`Arbeitskörper` → `Quellen aufnehmen` → `Abläufe formen` → `Realgraph` → `Wahrheit & Herkunft` → `Übergabe-Harness`.

Die früheste derzeit sichtbare Library-Fassung `arbeitskoerper-offline.html` wurde um **21:55:05** registriert; weitere Namen `arbeitskoerper-offline(2).html`, `arbeitskoerper-offline(1).html` und `arbeitskoerper.html` folgen zwischen **22:29 und 22:37**. Diese Library-Zeiten sind wiederum Artefakt-Registrierungszeiten und nicht automatisch die Geburtszeit des Browserzustands.

**Dateivergleich:** Die vier Namen bilden nur **zwei echte Fassungen**. `arbeitskoerper-offline.html` und `arbeitskoerper-offline(1).html` sind bytegleich; ebenso sind `arbeitskoerper-offline(2).html` und `arbeitskoerper.html` bytegleich. Die zweite echte Fassung erweitert die erste insbesondere um einen `embedded-workspace` und den Export **„Stand samt Feedback als HTML“ / „HTML mit Inhalt“**. Dadurch kann der lokale Browserzustand mitsamt Rückmeldungen in eine selbsttragende Offline-HTML eingebettet werden. Diese Fähigkeit wird später zur entscheidenden Brücke, weil der VPS-/Serverplaner genau einen solchen eingebetteten Zustand aus `arbeitskoerper-redteam-22/index.html` migriert.

### Herkunft vor dem VPS-Körper: lokaler Arbeitskörper am 21.08.

**Bestätigt:** Der migrierte Zustand reicht deutlich weiter zurück als die heutige VPS-Testphase. Er enthält bereits lokale Revisionen und 25 ältere Nutzer-Rückmeldungen aus dem Abend des **21.08.2026**.

- **21:40:18 Europe/Berlin** – frühester derzeit belegter menschlicher Speicherpunkt: `Revision 1: Arbeitsstand lokal festgeschrieben`.
- Der zusätzlich vorhandene `Systemkern` mit Zeit `2026-08-21T00:00:00Z` ist nur ein Seed-Ereignis und wird **nicht** als tatsächlicher Projektbeginn interpretiert.
- **22:13:32** – früheste erhaltene konkrete Nutzer-Rückmeldung: `passiert nix sichtbar` am Ziel **„Ablauf vorschlagen“**.
- Danach folgt innerhalb weniger Minuten eine dichte direkte Umbauphase: Menschen-/Agentenanweisungen in der n8n-Struktur verknoten; Wahrheitsmarker, Typen und Arbeitsstände editierbar/löschbar/erweiterbar machen; Scroll-Zoom; frei wählbare Farben; wirkungslose Öffnen-Aktionen beseitigen; Knoten skalierbar machen; History/Harness/Festschreiben verständlicher benennen; den Realgraph frei ergänzen, verschieben, bearbeiten und löschen können.
- **22:21:38** – lokale Revision 2.
- **22:23:26** – das Projektobjekt **„Mein Gesamtkonstrukt“** wird angelegt. Damit ist erstmals im erhaltenen Zustand der heutige Projektkern als eigenes Objekt eindeutig datiert.
- **22:24:49** – Nutzer fragt nach weiteren bewährten Ebenen aus Agentensystemen, Kunstwerkstätten und Kindergärten. Die spätere Auflösung dieses Feedbacks führt ausdrücklich zu Startwerkstatt, Canvas, Netz, Plan, Zeitspur und den **17 Programm-Arbeitsweisen**.
- **22:25:16** – lokale Revision 3.

Diese 25 frühen Rückmeldungen wurden am **22.08. um 14:22:15** im exportierten Offline-Körper gesammelt als erledigt festgeschrieben. Sie sind deshalb keine nachträgliche Erzählung, sondern im migrierten Arbeitszustand mit Originaltext, Ziel, Erstellzeit und späterer Auflösung erhalten.

### Work-Session „HTML prüfen und Graph planen“ und Übergang auf den VPS

**Bestätigt:** Die gezielte Suche in der ChatGPT-Work-Session **„HTML prüfen und Graph planen“** liefert als frühesten derzeit sicheren Sessionturn am 22.08. **03:53:51 Europe/Berlin**. Dort war der VPS ausdrücklich der erlaubte Testort.

Nur **2 Minuten 19 Sekunden** später, um **03:56:10**, entsteht der erste gefundene VPS-Dateifußabdruck `arbeitskoerper.html.gz.b64`. Um **03:56:21** antwortet der lokale HTTP-Test mit 200; um **03:57:44** ist auch der HTTPS-Test erreichbar. Der isolierte Testserver läuft auf Port **18094**.

**Bestätigt:** Um **04:14:42** ist `arbeitskoerper-r3-weitergebaut.html` mit **17 Replica-Familien** und dem Ergebnis von **22 echten Playwright-Red-Team-Runden** belegt. Danach entwickelt sich der VPS-Testkörper `arbeitskoerper-redteam-22` weiter, erhält Updates, später einen 390×844-Mobile-Testkörper und schließlich den exportierten Offline-Stand `embedded-r5-mt4clt3r`.

**Bestätigt:** Gegen **15:13:37** meldete die Work-Session 22 offene Feedbackpunkte als Revision r4; kurz darauf wurde die Sichtbarkeit dieses Zustands vom Nutzer erneut hinterfragt.

**Bestätigt:** Gegen **15:30:08** kam die entscheidende Umstellung: Der bis dahin unter `replica-redteam-22` laufende Körper sollte unter dem kanonischen Namen **`Mein-Gesamtkonstrukt-planer`** weitergeführt werden. Gefordert wurde ausdrücklich `/root/werkraum/Mein-Gesamtkonstrukt-planer/` als realer, menschenlesbarer, servergespeicherter Arbeitsraum.

Damit ist die derzeit belegte Entwicklungskette:

ClaudeWeb-Ursprungsdatei (vom Nutzer bestätigt; konkreter Dateiname noch offen)
→ Wechsel zu ChatGPT/Work, weil ClaudeWeb für diesen Arbeitsmodus zu teuer war und den gewünschten Körper nicht ausreichend traf
→ Chat-Auftrag Workflow/Graph um 21.08. 12:55–12:57
→ `workflow-canvas.html` als erste derzeit wiedergefundene ChatGPT-Fassung des Strangs und n8n-artiger editierbarer Graphkörper
→ bewusster Erweiterungsauftrag um 14:05:16: lokaler Arbeitsraum **über den Workflow-Canvas hinaus**
→ `ARBEITSKOERPER_BAUAUFTRAG.md` + `ARBEITSKOERPER_BAUPAKET.zip` um 18:09 als konkrete Übergabe aus Canvas + Realmaterial + Bauauftrag
→ generischer `Arbeitskörper` mit Quellen, Ablauf, Realgraph, Wahrheit/Herkunft, Harness und lokalen Revisionen
→ lokale Revision 1 spätestens 21:40:18
→ direkte Nutzer-Feedback-/Umbauphase
→ Projektobjekt `Mein Gesamtkonstrukt`
→ lokale Revision 3
→ Umbaucode ersetzt den alten Systemkern durch den projektzentrierten Körper
→ Ausbau zu 17 Programm-Arbeitsweisen / Replicas
→ Session `HTML prüfen und Graph planen` setzt den Körper auf dem VPS fort
→ isolierter VPS-Testkörper
→ 22 Playwright-Red-Team-/Fix-Runden
→ `arbeitskoerper-redteam-22`
→ Feedback-/Revisionsausbau
→ bewusste Umbenennung und Server-Migration
→ `Mein-Gesamtkonstrukt-planer`
→ gemeinsamer servergespeicherter Arbeitskörper
→ Spurenraum und weiterer Ausbau.

### Statischer Endpunkt vor der Live-Beobachtung

**Snapshot bis mindestens 18:40:09 Europe/Berlin:** Die Work-Session hat den servergespeicherten Planer inzwischen selbst im sichtbaren Cloud-Browser gegengeprüft und zwei umfangreichere Arbeitsakten angelegt. Sie wurden zunächst unter `07_AI-Spuren` gesehen und anschließend über die sichtbare Ordnerfunktion nach `03_Gemeinsame_Arbeit` verschoben bzw. umgeordnet:

- `01_REPLICA_RECHERCHE_ERWEITERUNGEN_UND_NUTZERWUENSCHE.md` – Recherche zu Erweiterungsökosystemen, realen Nutzersignalen, Bauableitungen und Abnahmetests für die 17 Replicas. Die Datei betont ausdrücklich, dass recherchierte Funktionen **nicht** automatisch als vorhanden gelten.
- `02_CLOUDBROWSER_GEGENPROBE_REPLICAS_2026-08-22.md` – sichtbare Bedienproben gegen den echten Planer im Cloud-Browser.

Die Cloud-Browser-Gegenprobe trennt konsequent zwischen **sichtbarer Reaktion** und **echter Arbeitskraft**. Belegt sind unter anderem:

- alle 17 Replica-Arbeitsweisen wurden nacheinander geöffnet;
- Houdini-, TouchDesigner-, Trello/Notion/Airtable-, VS-Code- und weitere Controls reagieren sichtbar;
- ein über `Neues Arbeitsobjekt` erzeugtes Objekt wurde serverseitig bis `s39` gespeichert und blieb nach Reload erhalten;
- `TouchDesigner → Live stoppen` war nach Reload wieder zurückgesetzt und ist damit derzeit nur lokaler Sichtzustand, keine belegte persistente Laufsteuerung;
- unterschiedliche Revisionsbegriffe (`Arbeitsrevision r3` versus Serverstand `s39`) sind als Widerspruch erkannt;
- `Stimmt so nicht` zeigte beim Cloud-Browser-Test keinen Dialog und wird in der Arbeitsakte als **P0-Bedienfehler** geführt;
- der Schalter `Telefon prüfen` ersetzt keinen echten 390px-Viewport-Test;
- aus der sichtbaren Umbenennung `07_AI-Spuren` → `03_Gemeinsame_Arbeit` blieben zunächst `README.md` und `PROTOKOLL.md` zusätzlich im alten Ordner zurück, was als echte Zwei-Wahrheiten-/Bauminkonsistenz erkannt wurde.

Die harte Schlussfolgerung der Work-Session lautet funktional: Eine Replica-Kernaktion gilt erst als belastbar, wenn die Kette **Eingabe → sichtbares Ergebnis → Ereignisspur → Speichern → Reload → Wiederfinden/Weiterarbeiten** belegt ist.

Dieser Abschnitt markiert bewusst den **statischen Dokumentationsschnitt vor unserer anschließenden Live-Beobachtung**. Änderungen nach diesem Snapshot werden nicht rückwirkend in die Entstehungsgeschichte gemischt, sondern als neuer laufender Beobachtungsstrang protokolliert.

**Noch offen:** Vor dem sicheren ChatGPT-Turn um ca. 12:55 am 21.08. ist nun eine ClaudeWeb-Ursprungsdatei als Vorgänger **durch den Nutzer bestätigt**. Noch nicht wiedergefunden sind ihr konkreter Dateiname, ihr genauer Erzeugungszeitpunkt und der wörtliche ClaudeWeb→ChatGPT-Übergabeturn. Die Lücke liegt damit nicht mehr beim Ursprung als solchem, sondern bei der exakten artefaktischen Identifizierung dieses ClaudeWeb-Vorläufers. Diese Details werden nicht erfunden.

### Korrektur der Spur
Die erste Rückwärtssuche ist an dieser Stelle in **fremde heutige Agenten-/Codex-Spuren** abgebogen. Diese gehören **nicht** zur hier gemeinten Herkunftskette.

Gegenstand dieser Dokumentation ist die **aktuelle ChatGPT-Work-Session und der daraus weiterwachsende Gesamtkonstrukt-Körper**. Der sogenannte `Gesamtkonstruktplaner` bezeichnet darin nur eine historische Entwicklungsstufe bzw. den derzeitigen Ordner-/Oberflächenkontext; er ist **nicht** mehr die Obergrenze dessen, was hier dokumentiert wird.

Funde aus Codex-, Claude-Code- oder anderen Agentensitzungen werden nur dann aufgenommen, wenn sich später konkret belegen lässt, dass die Work-Session selbst darauf zurückgreift oder daraus hervorgegangen ist. Sie sind nicht automatisch Teil ihrer Ursprungsgeschichte.

### Abschlussstand der Rückwärtssuche

Die wesentliche Entwicklungskette ist inzwischen rekonstruiert und gegengeprüft: bestätigter ClaudeWeb-Vorläufer → ChatGPT-Workflow-Canvas → Erweiterungsauftrag → Baupaket → lokaler Arbeitskörper → Nutzerfeedback/Revisionen → projektzentrierter Körper → Replicas → VPS-Red-Team → Servermigration → servergespeicherter gemeinsamer Arbeitskörper → Spuren-/Arbeitsraum → zunehmende Verbindung von Planung und realer Durchführung.

Nicht geschlossen ist die **artefaktische Vorderkante des ClaudeWeb-Vorläufers**: konkreter Dateiname, genauer Erzeugungszeitpunkt und die wörtliche Übergabe von ClaudeWeb zu ChatGPT/Work fehlen weiterhin. Der Ursprung als solcher ist durch die Nutzerangabe geklärt; offen ist seine exakte technische Identifizierung.

Ab dem statischen Snapshot um 18:40 am 22.08. wird nicht mehr rückwärts rekonstruiert, sondern ein getrennter **Live-Beobachtungsstrang** geführt. So werden Vergangenheit und laufende Work-Aktivität nicht vermischt.

---

## Gegenstandskorrektur: Der „Gesamtkonstruktplaner“ ist nicht das Dach

**Vom Nutzer ausdrücklich korrigiert:** Das inzwischen entstandene Ding ist **nicht bloß ein größer gewordener Planer**. Der vorhandene Ordner `/root/werkraum/Mein-Gesamtkonstrukt-planer/` und der Begriff `Gesamtkonstruktplaner` bleiben als reale historische Entwicklungs- und Ablagespur erhalten, dürfen aber nicht mehr mit dem Gesamtgegenstand verwechselt werden.

Der Körper verbindet inzwischen mindestens:

- reale Materialien, Dateien und Arbeitsobjekte,
- Ideen, Wissen, Entscheidungen und Projektzusammenhänge,
- Workflow-Entwurf **und** konkrete Durchführung,
- Realgraph/Kanten samt Herkunft und bewusster Bestätigung,
- Versionen, Serverzustände und Ereignisspuren,
- Dateioperationen, deren Identität und Auswirkungen weitergetragen werden,
- menschliche Arbeit sowie AI-/Agenten-Spuren und Übergaben,
- technische Laufzeitzustände, Tests, Reload-Belege und Rückmeldungen,
- verschiedene Arbeitsansichten und Replica-Handgriffe auf **demselben** Bestand.

Damit ist „Planen“ nur noch eine Tätigkeit innerhalb eines breiteren **Arbeits-, Konstruktions-, Ausführungs- und Beobachtungskörpers**. Die Dokumentation verfolgt ab hier diesen Gesamtkörper. Ein endgültiger Name wird daraus weiterhin nicht künstlich erzwungen.

---

## Dokumentationsregel für die weitere Spurensuche

Ab jetzt soll diese Datei den laufenden Verlauf in Mischform festhalten:

- **Changelog:** Was wurde neu gefunden, verändert, verbunden oder verworfen?
- **Dokumentation:** Was bedeutet der Fund im größeren Zusammenhang?
- **Provenienz:** Woher stammt die Spur, und wie sicher ist sie?
- **Zeitfolge:** Was kam tatsächlich früher, was später?
- **Offene Fragen:** Welche Verbindung ist noch nicht belegt?

Wichtig: Keine künstliche Rückerzählung, in der alles von Anfang an geplant aussieht. Wenn etwas erst später zusammengewachsen ist, wird genau das dokumentiert.

---

## Offene artefaktische Ursprungskante

Der eigentliche Vorläufer **vor ChatGPT/Work** ist inzwischen durch die Nutzerangabe geklärt: eine Ursprungsdatei aus ClaudeWeb. Nicht geklärt ist ihre technische Identität.

Der früheste derzeit wiedergefundene ChatGPT-Gesprächsanker liegt am **21.08.2026 gegen 12:55 Europe/Berlin** mit der Frage `Was passiert an diesem Punkt im Ablauf?`. Darauf folgen direkt die Forderung nach allen Knoten, Verbindungen und Details je Workflow/Graph sowie der Dateiauftrag, aus dem `workflow-canvas.html` hervorgeht. Um **14:05:16** ist anschließend der bewusste Erweiterungsschritt vom Workflow-Canvas zum umfassenderen lokalen Arbeitsraum belegt.

Offen bleiben nur noch:

- Dateiname und Inhalt der konkreten ClaudeWeb-Ursprungsdatei,
- ihr genauer Erzeugungszeitpunkt,
- der wörtliche Übergabemoment von ClaudeWeb zu ChatGPT/Work,
- sowie eine mögliche noch frühere ChatGPT-Anbahnung vor dem sicheren 12:55-Turn.

Die Entwicklung ab `workflow-canvas.html` über Arbeitskörper, lokale Revisionen, 17 Replicas, VPS-Testkörper, Red-Team und den servergespeicherten Gesamtkörper ist inzwischen durch mehrere voneinander unabhängige Spuren belegt.

Codex-, Claude-Code- und andere Agentenspuren bleiben dabei draußen, solange keine direkte Herkunftsverbindung zu diesem Entwicklungsstrang belegt ist.

---

## Meta-Changelog

### 2026-08-22
- Datei neu angelegt.
- Anlass: Daniels Auftrag, die laufende Spurensuche selbst zusätzlich als Mischung aus Changelog und Dokumentation zu protokollieren. Der damalige Arbeitstitel lautete **Gesamtkonstruktplaner**; der Gegenstand wurde später ausdrücklich auf den breiteren Gesamtkonstrukt-Körper korrigiert.
- Der bestehende technische Zustand wird nicht umgedeutet; diese Datei ist eine zusätzliche menschlich lesbare Verlaufsspur.
- Korrektur während der Spurensuche: Ein zunächst versehentlich einbezogener heutiger Codex-/Fremdagenten-Strang wurde wieder entfernt. Gegenstand ist der aus der aktuellen **ChatGPT-Work-Session** weiterwachsende Gesamtkonstrukt-Strang; fremde Agentenspuren zählen nur bei belegter Herkunftsverbindung.
- Frühere Work-Session-Spur ergänzt: Session **„HTML prüfen und Graph planen“**, sicherer Nutzerturn ab 03:53:51 → isolierter VPS-Testkörper → `arbeitskoerper-r3-weitergebaut.html` mit 17 Replicas und 22 Playwright-Red-Team-Runden → `arbeitskoerper-redteam-22` → servergespeicherter `Mein-Gesamtkonstrukt-planer`.
- Zeitkorrektur: Eine zuvor notierte 03:46-Spur für `arbeitskoerper-r3-weitergebaut.html` war nicht belastbar und wurde entfernt.
- Rückwärtsspur bis 21.08. ergänzt: lokale Revision 1 um 21:40:18, 25 erhaltene Nutzerfeedbacks ab 22:13:32, Entstehung des Projektobjekts `Mein Gesamtkonstrukt` um 22:23:26 und Revision 3 um 22:25:16.
- Ursprungskante präzisiert: Vor `workflow-canvas.html` liegt nach ausdrücklicher Nutzerangabe eine ClaudeWeb-Ursprungsdatei. Die ChatGPT-Spur führt sicher bis **ca. 12:55–12:57 am 21.08.**; offen bleiben Dateiname/Zeitpunkt des ClaudeWeb-Vorläufers und der wörtliche Übergabemoment.
- Früheste Artefaktfamilie ergänzt: `workflow-canvas.html` → bewusster Auftrag für einen umfassenderen lokalen Arbeitsraum → `arbeitskoerper-offline*.html` / `arbeitskoerper.html` → lokale Revisionen und Nutzerfeedbacks.
- Zeitquellen getrennt: Chat-Erzeugungszeit, Browserzustand/Revision und Library-Registrierungszeit werden nicht mehr als dieselbe Uhr behandelt.
- Brückenartefakte gefunden und dokumentiert: `ARBEITSKOERPER_BAUAUFTRAG.md` + `ARBEITSKOERPER_BAUPAKET.zip` verbinden `workflow-canvas.html` und `konzepte dokus etc.zip` ausdrücklich mit dem Bau des realen Arbeitskörpers.
- Offline-Dateifamilie entdoppelt: vier Dateinamen entsprechen zwei byteidentischen Fassungspaaren; die zweite echte Fassung ergänzt eingebetteten Arbeitsstand und HTML-Export samt Feedback.
- Statischer Vor-Live-Snapshot ergänzt: Replica-Recherche und Cloud-Browser-Gegenprobe wurden unter `03_Gemeinsame_Arbeit` lokalisiert; deren bis 18:40 dokumentierter Zustand bildet die Trennlinie zum folgenden Live-Beobachtungsstrang.
- Rückwärtssuche als weitgehend abgeschlossen markiert; offen bleibt vor allem die artefaktische Identifizierung der ClaudeWeb-Ursprungsdatei sowie die unmittelbare Übergabenaht zu ChatGPT/Work.
- Gegenstandskorrektur: `Gesamtkonstruktplaner` ist nicht mehr das Dach der Dokumentation, sondern nur historische Entwicklungs-/Ordnerbezeichnung. Dokumentiert wird der breitere gemeinsame Arbeits-, Konstruktions-, Durchführungs- und Beobachtungskörper.

---

## Live-Beobachtungsstrang – ab dem statischen Schnitt

### Startbaseline

**Beginn des getrennten Live-Strangs:** nach dem dokumentierten Cloud-Browser-Snapshot von 18:40:09 Europe/Berlin.

Zum Start der Beobachtung steht der kanonische Planer auf **Serverrevision 39** (`updatedAt 2026-08-22T16:31:18.665200Z`):

- 4 Objekte,
- 1 belegte Kante,
- 23 offene Feedbacks,
- 26 erledigte Feedbacks.

Das vierte Objekt ist `Neues Arbeitsobjekt`, erzeugt im sichtbaren Cloud-Browser um **18:31:16** und mit Serverrevision 39 um **18:31:18** persistiert. Der Cloud-Browser-Test bestätigt anschließend, dass dieses Objekt einen Reload überlebt.

Die Datei `03_Gemeinsame_Arbeit/02_CLOUDBROWSER_GEGENPROBE_REPLICAS_2026-08-22.md` steht zum Start dieser Beobachtung auf dem Änderungsstand **18:40:09**. Ihr Inhalt und Hash bilden die Referenz für folgende Deltas.

Ab hier werden nur **neue Änderungen nach dieser Baseline** als Live-Beobachtung protokolliert; ältere Funde bleiben Teil der rekonstruierten Herkunft.

### Live-Delta 1 – 18:48:19: Server-API geändert

**Bestätigt:** Um **18:48:19 Europe/Berlin** wurde `server/planner_api.py` verändert. Das ist die erste nach dem statischen Schnitt beobachtete Work-Änderung außerhalb dieser Dokumentationsdatei.

Der aktuelle Code seedet und erzeugt den gemeinsamen Arbeitsordner nun unter **`03_Gemeinsame_Arbeit`** (`README.md`, `PROTOKOLL.md`) und verwendet bei neuen Spuren den Ereignistitel `Gemeinsame Arbeit: ...`. Im Python-Code findet sich kein Seed mehr für `07_AI-Spuren`.

**Sehr wahrscheinlich:** Dieser Patch reagiert direkt auf den zuvor im Cloud-Browser gefundenen Ordnerwiderspruch, bei dem die sichtbare Umbenennung `07_AI-Spuren` → `03_Gemeinsame_Arbeit` durch anschließend wieder auftauchende Seed-Dateien zwei Orte hinterließ. Ohne eine gesicherte Vorversion von `planner_api.py` wird diese Zuordnung als starke Inferenz und nicht als bewiesener Diff markiert.

**Noch nicht behoben/belegt:** Der alte Ordner `/data/tree/07_AI-Spuren/` existiert nach dem Patch weiterhin mit `README.md` und `PROTOKOLL.md`. Eine tatsächliche Bereinigung ist also noch nicht erfolgt. `data/ai_spuren.json` und der aktuelle Bauauftrag enthalten ebenfalls noch historische Verweise auf `07_AI-Spuren`.

**Serverzustand:** weiterhin Revision **39**; keine neue Planer-State-Speicherung nach 18:31:18. Nach dem API-Patch wurde bis zur nächsten Delta-Prüfung keine weitere Work-Datei geändert.

### Live-Delta 2 – 18:57 bis 19:48: vom Planen in echte Durchführung

**Bestätigt:** Nach dem vorherigen Stand `s39` begann eine neue zusammenhängende Ausbauphase. Das Serverereignislog steigt zwischen **18:57:07** und **19:47:08 Europe/Berlin** von `s40` bis `s52`.

Der Zustand wächst dabei von **4 Objekten / 1 Kante** auf **6 Objekte / 3 Kanten**. Neu bzw. neu real eingebunden sind insbesondere:

- `Ablauf entwerfen · Mein Gesamtkonstrukt` als eigener Workflow-Entwurf. Er wird um **18:57:30** erzeugt und mit `s41` serverseitig gespeichert. Seine eigene Beschreibung markiert ausdrücklich: sichtbarer Ablaufkörper, aber keine erfundene reale Kante.
- `03_Abläufe/01_Gesamtplan_Durchfuehrung.md` wird um **18:59:28** als echte Werkraum-Datei angelegt und kurz darauf als reales Dokumentobjekt übernommen. Der Inhalt formuliert nicht nur Planung, sondern einen prüfbaren Durchführungsweg mit Materialbestand, Arbeitsobjekten, bewussten Kanten, Eingabe/Zuständigkeit/Prüfung/Ergebnis/Stopbedingung und Reload-Beleg.
- Der Workflow wird bewusst mit `Browser Test` über die Kante **`wird geprüft durch`** verbunden. Der Gesamtplan wird über eine reale `enthält`-Kante an `Mein Gesamtkonstrukt` gehängt.

Damit ist der neue Stand gerade selbst ein Beleg für die Gegenstandskorrektur dieser Dokumentation: Der Körper verwaltet nicht nur Pläne, sondern beginnt **Plan → Handlung → Beleg → gespeicherter Zustand** in demselben System abzubilden.

**19:27:11 – `server/sync.js` verändert:** Der aktuelle Code behandelt den VPS ausdrücklich als `SERVER · einzige Wahrheit`, sendet lokale Änderungen mit `baseRevision`, meldet bei konkurrierendem neuerem Zustand einen **409-Serverkonflikt** statt still zu überschreiben und kann einen neueren Serverzustand in den Browser hydratisieren und anschließend reloaden. Ohne gesicherte Vorversion wird nicht behauptet, dass jede dieser Zeilen exakt in diesem einzelnen Patch neu entstand; bestätigt ist die Dateiänderung zu diesem Zeitpunkt und der aktuelle Inhalt.

**19:45:10 – `server/planner_api.py` erneut verändert:** Der aktuelle Servercode trägt bei `rename`/`move` nun zusätzlich strukturierte Ereignisdetails mit:

- `oldPath`,
- `newPath`,
- `affectedObjectIds`.

Gleichzeitig schreibt `_rewrite_workspace_sources(...)` die `werkraum://...`-Herkunft bereits übernommener Arbeitsobjekte auf den neuen Dateipfad um, statt nach einer Verschiebung eine zweite Identität zu erzeugen.

**Direkte Gegenprobe im Zustand:** `Browser Test` wird um **19:46:51** von `03_Gemeinsame_Arbeit/Browser-Test.md` nach `01_Material/Browser-Test.md` verschoben und um **19:47:08** wieder zurück. Beide Ereignisse nennen dieselbe betroffene Objekt-ID `object-b5541e61-0db3-4196-a4df-0042de0af4be`. Im aktuellen Objekt bleibt dieselbe Identität erhalten; `sourcePath` zeigt danach wieder auf `werkraum://03_Gemeinsame_Arbeit/Browser-Test.md`.

Das ist der bislang klarste Live-Beleg dafür, dass eine reale Werkraumhandlung inzwischen nicht nur optisch passiert, sondern **Identität + Pfadänderung + Ereignisspur + Serverrevision** zusammenführt.

**Aktueller bestätigter Zustand `s52` um 19:47:08:** 6 Objekte, 3 Kanten, weiterhin 23 offene und 26 erledigte Feedbacks. Die fachliche Arbeitsrevision im inneren Zustand steht parallel weiterhin auf `r3`; Serverrevision und bewusste Arbeitsrevision sind also weiterhin zwei getrennte Zähler und müssen als solche verständlich bleiben.

**19:48:44 – `app/index.html` verändert:** Die UI-Datei wurde direkt nach `s52` erneut geschrieben. Ein semantischer Vorher/Nachher-Diff liegt für diesen einzelnen Schreibzeitpunkt nicht vor; deshalb wird hier bewusst nur die bestätigte Änderung protokolliert und keine Funktion dazuerfunden.

### Live-Delta 3 – 19:50 bis 19:52: Feedbackweg reagiert auf den neuen Durchführungsbeleg

**Bestätigt:** `app/index.html` wurde um **19:50:20 Europe/Berlin** erneut verändert. Unmittelbar danach entstehen drei weitere Serverrevisionen:

- **s53 · 19:51:05** – offene Feedbacks steigen von 23 auf 24,
- **s54 · 19:51:36** – offene Feedbacks steigen auf 25,
- **s55 · 19:52:10** – offene Feedbacks sinken auf 24 und erledigte steigen von 26 auf 27.

Im aktuellen Zustand sind dabei zwei neue Rückmeldungen belegt. Beide hängen direkt an der gerade getesteten Dateioperation und fordern als nächsten Schritt eine **sichtbare Ereignisansicht** für `oldPath`, `newPath`, Operation und betroffene Objekte sowie Regeln dafür, ob ein Ereignis nur protokolliert, Struktur/Kanten aktualisiert oder als freigegebener Workflow-Auslöser dienen darf.

Gleichzeitig wird der ältere offene Punkt `feedback-c4d47f7d-bc39-4dc8-ad81-689e82c5be01` um **19:52:10** als erledigt markiert. Dessen Forderung war noch grundsätzlicher: Eine Verschiebung müsse als nachvollziehbares Ereignis und veränderbare Zuordnung im Gesamtkonstrukt existieren. Genau dieser Teil ist durch die neue strukturierte Move-Provenienz inzwischen real belegt.

**Starke Inferenz:** Der zuvor dokumentierte P0-Blocker, bei dem `Stimmt so nicht` im Cloud-Browser keinerlei Dialog oder Eingabemaske öffnete, ist zumindest teilweise repariert oder umgangen worden. Dafür spricht die UI-Dateiänderung direkt vor den zwei neu erzeugten Feedbackeinträgen. Ohne erneute explizite Cloud-Browser-Gegenprobe wird noch nicht behauptet, dass gerade derselbe Button vollständig repariert ist.

**Aktueller bestätigter Zustand nach diesem Delta:** `s55`, 6 Objekte, 3 Kanten, 24 offene und 27 erledigte Feedbacks. Der Arbeitskörper erzeugt damit inzwischen aus einer realen Durchführung nicht nur einen technischen Beleg, sondern direkt die nächste überprüfbare Umsetzungsnötigkeit.

### Live-Delta 4 – 19:53:16: Ereignisdetails werden in der Oberfläche sichtbar gemacht

**Bestätigt durch direkten Vorher/Nachher-Vergleich von `server/sync.js`:** Um **19:53:16 Europe/Berlin** wurde genau die eben neu formulierte Umsetzungsnötigkeit aufgegriffen. Gegenüber der zuvor gelesenen Fassung wurden neue Funktionen ergänzt:

- `describeWorkspaceEvent(event)` liest `operation`, `oldPath`, `newPath` und `affectedObjectIds` und formatiert daraus eine menschenlesbare Kurzzeile.
- `renderWorkspaceEventDetails()` lädt den aktuellen Serverzustand und ergänzt diese Details an Einträge der sichtbaren History-/Zeitspur.
- `observeWorkspaceEventDetails()` beobachtet DOM-Änderungen und rendert die Ereignisdetails erneut.
- Der neue Observer wird beim `DOMContentLoaded` zusätzlich zur Server-Hydrierung gestartet.

Damit reagiert Work innerhalb von ungefähr **1 Minute 40 Sekunden** auf den gerade erzeugten offenen Punkt: Die Move-Provenienz war serverseitig bereits real, aber für Menschen unsichtbar; jetzt wird exakt dieser technische Beleg in die sichtbare Ereignisansicht gezogen.

Das ist ein weiterer klarer Schritt weg von einem bloßen „Planer“: Eine reale Dateioperation erzeugt strukturierte Provenienz, daraus entsteht Feedback, und dieses Feedback führt unmittelbar zu einer neuen sichtbaren Beobachtungsschicht über demselben Zustand.

### Live-Delta 5 – Nachholung 19:53 bis 23:22: der angebliche „Live-Endpunkt“ war keiner

**Korrektur:** Der zuvor als aktueller Live-Schnitt behandelte Stand um 19:53 war nur der letzte von ChatGPT gelesene Zustand. Die Work-Session arbeitete danach mehrere Stunden weiter. Eine frische VPS-Prüfung um ca. **23:21–23:23 Europe/Berlin** zeigt einen laufenden Ausbau bis mindestens **Serverrevision s194**. Der aktuelle Stand wurde noch während dieser Gegenprüfung weiter verändert.

**Serverentwicklung:** Zwischen `s55` und `s194` wächst der Zustand von **6 Objekten / 3 Kanten / 24 offenen / 27 erledigten Feedbacks** auf **13 Objekte / 4 Kanten / 37 offene / 33 erledigte Feedbacks**. Die fachliche Arbeitsrevision bleibt weiterhin `r3`; die Serverrevision ist ein eigener technischer Zähler.

Wesentliche bestätigte Sprünge:

- **19:53–20:13:** Die sichtbare Ereignisspur wird weiter redgeteamt. Neue Rückmeldungen fordern ausdrücklich, dass Ereignisse nicht automatisch Folgeaktionen auslösen dürfen. Um **19:57:20** entsteht deshalb das Objekt `Regel · Datei-Umzug braucht Freigabe` als geplante, aktive Automation. Seine eigene Definition: Datei-Umzüge beobachten, aber ohne menschliche Freigabe keine Folgeaktion ausführen. Um **20:01:56** kommt eine vierte reale Kante hinzu: die Regel `wartet auf Freigabe nach` dem realen `Browser Test`-Dokument; Provenienz: `VPS-Playwright · Regelkörper`.
- **21:37–21:43:** Ein weiterer Objektkörper `Geplantes Ergebnis` erscheint; anschließend folgt eine sehr dichte Serie von Serverständen bei unverändert 8 Objekten / 4 Kanten. Die grobe Serverereignisspur verrät nicht jede einzelne Bedienhandlung. Im aktuellen Zustand sind aber massiv veränderte Positionen/Größen und die Arbeitsvariante `haupt2` erhalten. Deshalb wird dieser Block als intensive UI-/Canvas-Arbeit protokolliert, ohne einzelne Klicks zu erfinden.
- **21:47:** Zwei neue direkte Nutzer-/Browserfeedbacks tauchen im Board-Kontext auf: frei erzeugbare/editierbare/löschbare Boxen werden verlangt; außerdem wird der Sinn des `Verlauf`-Bereichs erneut hinterfragt.
- **22:03:** `Ablaufvorschlag · Mein Gesamtkonstrukt` wird als neuer Workflowkörper erzeugt. Er enthält zwei ausdrücklich nur vorgeschlagene Schritte (`Browser Test` und `01 Gesamtplan Durchfuehrung`) und hält beide Beziehungen weiterhin getrennt als offene Vorschläge statt sie als Wahrheit zu setzen.
- **22:04:** Die Objektzahl springt schrittweise von 9 auf 13. Vier `Neuer Marker`-Objekte entstehen bzw. werden bewegt/skaliert. Das ist ein sichtbarer Test, dass der Körper zusätzliche frei platzierbare Elemente als echte Zustandsobjekte tragen kann.
- **22:09–22:14:** Der Cloud-Browser testet einen echten Serverkonflikt mit zweitem Tab. Ein Befund dokumentiert, dass `Telefon prüfen` weiterhin keinen echten 390×844-Viewport erzeugt. Danach wird der Konfliktschutz selbst zum Testgegenstand: lokaler Entwurf darf bei 409 nicht still überschrieben werden; gefordert wird als nächste Stufe ein echter Vergleichs-/Merge-Körper.
- **22:16–22:38:** Das Feedbacksystem wird gegen sich selbst getestet. Eigene Feedback-Bedienelemente können anschließend gezielt markiert werden. Danach werden optionale Belegfelder eingebaut und mehrfach gegen Reload geprüft: erwartetes Verhalten, tatsächliches Verhalten, Klickschritte, Gerät/Viewport/Revision, Markierung, Schweregrad und `wirklich geprüft`. Im Zustand liegen konkrete erfolgreiche Gegenproben mit `evidence`-Daten.
- **22:37:** Eine echte Stiftmarkierung (`paint-5f795c6f-a6b9-40c5-9604-9e5399e360ee`) wird im Zustand als `paintMarks` gespeichert und anschließend über `paintMarkId` an Feedback gebunden.
- **23:19:** Dieselbe Markierungs-ID wird erneut bewusst ausgewählt und bleibt nach Speicherung als Beleg am Feedback erhalten (`s191`).
- **23:21–23:22:** Work testet den Schutz verknüpfter Markierungen vor `Ansicht leeren`. Die erste Regel war zu grob und blockierte global; der nächste Fix macht den Schutz ansichtsbezogen. Der entsprechende Kritikpunkt wird um **23:22:42** erledigt. Bereits um **23:22:55** entsteht die nächste offene Rückmeldung: Es fehlt noch ein bewusster Weg, eine verknüpfte Markierung zu **entkoppeln oder zu ersetzen**, statt sie entweder unantastbar zu lassen oder still verschwinden zu lassen.

**Aktueller Codezustand von `server/sync.js` während dieser Gegenprüfung:**

- 409-Konflikte sichern den lokalen Entwurf in `sessionStorage`, statt ihn zu überschreiben, und zeigen einen sichtbaren Konflikthinweis.
- Feedback-Zeitstempel werden auf `createdAt` normalisiert.
- sichtbare Ereignisdetails werden weiter eingeblendet.
- normales Feedback und Feedback auf eigene Bedienelemente erhalten denselben optionalen Belegkörper.
- Feedback kann konkrete `paintMarkId`-Markierungen verknüpfen.
- verknüpfte Markierungen der **aktuellen Ansicht** werden vor `Ansicht leeren` geschützt.
- ein kurzer Sperrzeitraum verhindert doppeltes Abschicken desselben Feedbacks vor Serverbestätigung.

**Letzter bestätigter Work-Stand dieses Nachtrags:** `s194`, gespeichert **23:22:56 Europe/Berlin**, mit **13 Objekten, 4 Kanten, 37 offenen und 33 erledigten Feedbacks**. Dieser Zeitstempel ist ausdrücklich nur ein Beobachtungsschnitt und kein behauptetes Ende der Work-Session.

### Live-Delta 6 – 23:23:54: Work beantwortet bereits die 23:22:55-Rückmeldung

**Bestätigt:** Noch während der Dokumentation wurde `server/sync.js` um **23:23:54 Europe/Berlin** erneut verändert. Der neue Code ergänzt in der sichtbaren Beleganzeige bei Feedback mit `paintMarkId` einen Button **`Markierung entkoppeln`**.

Beim Auslösen wird ausschließlich `evidence.paintMarkId` aus der betroffenen Rückmeldung entfernt; die Rückmeldung selbst bleibt erhalten und wird wieder über den Serverzustand gespeichert. Die sichtbare Meldung lautet `MARKIERUNG ENTKOPPELT · Rückmeldung bleibt erhalten`.

Damit reagiert Work unmittelbar auf die erst um **23:22:55** erzeugte offene Rückmeldung, die genau einen bewussten Entkoppeln-/Ersetzen-Weg verlangte. Der erste Teil, **Entkoppeln ohne Verlust der Rückmeldung**, ist damit im Code sichtbar umgesetzt. Ein eigenes `Ersetzen` einer bestehenden Verknüpfung wird daraus noch nicht automatisch als vollständig bewiesen; die vorhandene Markierungsauswahl im Belegdialog kann zwar eine Markierungs-ID wählen, aber die konkrete Ersetzen-Gegenprobe ist noch nicht dokumentiert.

Dieser Patch belegt zugleich, warum ein statischer „Live-Endstand“ hier irreführend ist: Zwischen Kritik und nächstem Codeeingriff liegen in diesem Fall weniger als zwei Minuten.

**Direkte Gegenprobe danach:** Um **23:24:16** legt Work bereits eine neue Rückmeldung an: `Gegenprobe: Diese verknüpfte Markierung wird danach bewusst entkoppelt.` Sie trägt wieder dieselbe `paintMarkId` und `verified: true`. Dadurch steigt der Serverstand um **23:24:17** auf **s195** (13 Objekte, 4 Kanten, 38 offene, 33 erledigte Feedbacks). Die Entkoppeln-Funktion wird also unmittelbar für einen echten Folgetest vorbereitet. Auch `s195` ist nur der zuletzt belegte Schnitt, nicht das Ende der laufenden Session.

### Live-Delta 7 – 23:25 bis 23:56: Entkopplung verschärft, Testballast entfernt, Arbeitsrevisionen 4 und 5

Nach `s195` läuft der Zustand weiter bis **s216**. Zunächst entstehen weitere Feedback-/Gegenproben. Der Entkopplungsweg wird im Code nochmals verschärft: `Markierung entkoppeln` verlangt nun einen **Grund** und speichert anschließend die frühere Markierungs-ID zusammen mit `reason`, `actor: Arbeitsoberfläche` und Zeitpunkt als `detachedMark`, statt den Bezug einfach kommentarlos zu löschen.

**Wichtig:** Der später aktualisierte Redteam-Status behauptet diesen Weg ausdrücklich noch **nicht** als live abgenommen: Umbau vorhanden, direkte Browserautomation bei der Gegenprobe blockiert. Damit wird zwischen Codeexistenz und real geprüfter Nutzerhandlung sauber getrennt.

Um **23:50:12 Europe/Berlin** wird erstmals **Arbeitsrevision 4** auf dem Server festgeschrieben (`s208`). Direkt danach wird Testballast entfernt: Die Objektzahl fällt in vier Speicherschritten von **13 auf 9**. Im aktuellen Körper fehlen gegenüber dem vorherigen Stand der temporäre `Ablaufvorschlag · Mein Gesamtkonstrukt` und drei der vier zusätzlich erzeugten `Neuer Marker`-Objekte; die vier realen Kanten bleiben erhalten. Die offenen Workflow-Vorschläge sind im aktuellen Zustand ebenfalls leer.

Um **23:56:12** folgt **Arbeitsrevision 5** (`s216`) als weiterer ausdrücklich menschlich festgeschriebener Serverstand. Damit sind `r4` und `r5` keine bloßen technischen Serverzähler, sondern neue bewusste Arbeitsrevisionen; parallel steigt die technische Serverrevision weiter separat.

### Live-Delta 8 – 00:11 bis 00:52 am 23.08.: vom globalen Planer zur kontextgebundenen Werkzeugarchitektur

In der Nacht wird die zuvor vom Nutzer verlangte Architekturkorrektur ausdrücklich in den realen Arbeitskörper geschrieben.

Die neue Datei `03_Gemeinsame_Arbeit/BAUGESCHICHTE_GESAMTBETRIEBSSYSTEM.md` benennt den bisherigen Fehler offen: **Start, Canvas, Netz, Plan, Zeitspur und Replicas** waren globale Sichten auf denselben offenen Planerzustand und damit noch kein Gesamtbetriebssystem.

Die beschlossene Umkehr lautet dort:

`Arbeitsbestand wählen → konkreten Gegenstand wählen → passendes Werkzeug öffnen → Ergebnis als Datei, Objekt, Kante oder Ereignis zurückschreiben.`

Die bisherigen Ansichten werden dadurch nicht bloß umbenannt, sondern als spätere **Werkzeugfamilien** neu gefasst: Übersicht, Raum, Beziehungen, Ablauf, Geschichte und Werkzeuge. Für jede Familie gilt ausdrücklich: eigene Kernhandlung, am gewählten Material, gespeichert und geprüft; kein bloßes Umstylen desselben globalen Knotenkörpers.

`server/workspace.js` setzt dafür den ersten echten technischen Schnitt um:

- Ordnerzweige werden einzeln ein-/ausklappbar.
- **Alles einklappen** schließt den gesamten Baum.
- Dateiverweise aus `Gemeinsame Arbeit` können den betreffenden VPS-Pfad direkt im Werkraum öffnen.
- Bei Auswahl einer Datei oder eines Ordners wird ein `workspaceContext` mit Art, Pfad, Titel und Zeitpunkt in den Arbeitszustand geschrieben und ein sichtbarer Balken `ARBEITSKONTEXT · …` aktualisiert.
- Die Oberfläche besitzt bereits einen Arbeitsort-Picker; aktuell ist serverseitig jedoch weiterhin nur die Wurzel `gesamtkonstrukt` registriert. Mehrere echte Ober-/Arbeitswurzeln sind damit vorbereitet, aber noch nicht real eingerichtet.

**Grenze, von Work selbst dokumentiert:** Die alten globalen Tabs existieren weiterhin. Der Kontextbalken allein löst den Architekturumbau nicht. Zudem ist im aktuellen kanonischen `data/current.json` noch kein gespeicherter `workspaceContext` belegt; der Codepfad existiert, eine tatsächlich persistierte Auswahl im aktuellen Serverstand ist damit noch nicht nachgewiesen.

Die dazugehörige `PROTOKOLL.md` benennt denselben Architekturbruch und hält fest, dass ab jetzt der **reale Arbeitskontext (Datei oder Ordner) die erste Achse** sein soll.

### Live-Delta 9 – Arbeitskörper wird als persistentes Gewebe beschrieben

Parallel werden mehrere reale Baumdateien ergänzt bzw. verschärft:

- `00_Start/01_AKTIVER_ARBEITSKOERPER.md` beschreibt den Dateibaum als minimalen Obsidian-Vault und die Objekt-IDs, Kanten, Ereignisse und Spuren als Nervenbahnen desselben Bestands. Kein Bereich darf eine zweite Wahrheit führen.
- Die dort definierte Arbeitszelle lautet: `Gegenstand → Nutzerhandlung → Ergebnis/Beleg → Ereignis/Spur → nächste Verbindung`.
- `04_Automationen/README.md` trennt ausdrücklich Trigger/Berechtigung/Eingabe/Stop/Test/Run-Log von bloßem Prompt oder Diagramm.
- `05_Übergaben/README.md` definiert Übergaben als lesbare Sicht auf realen Stand, nicht als Ersatz für Originale oder Ereignisse.
- `06_Redteam-Umbau/STATUS.md` führt bestätigte und offene Teile getrennt. Unter anderem bleiben echte 390×844-Mobileprüfung, vollständige Replica-Kernhandlungen, Konfliktauflösung, Altbestand `07_AI-Spuren` und die UI-Verankerung neuer Arbeitskörper-Dateien offen.

Das ist der bisher klarste schriftliche Schritt von einer einzelnen Planerdatei hin zu einem **Gesamt-Arbeitskörper mit Bestand, Werkzeugen, Ausführung, Geschichte und Übergaben**.

### Live-Delta 10 – 04:34 bis 04:35: dauerhaftes Bauprotokoll auf Platte

Um **04:34:39 Europe/Berlin** wird `server/planner_api.py` erneut geändert. Neu ist ein echter dauerhafter Build-Log unter:

`data/tree/03_Gemeinsame_Arbeit/BAULOG.ndjson`

`_store_workspace_state(...)` schreibt bei Arbeitsraumänderungen nun zusätzlich zur kanonischen `current.json` und zum Tages-Ereignislog eine Zeile mit Zeitpunkt, Serverrevision, Aktion und Details in dieses BAULOG. Auch Einträge über die `Gemeinsame Arbeit`-API laufen durch denselben Speicherpfad.

Um **04:35:02** wird das erstmals real benutzt: In `data/ai_spuren.json` erscheint eine direkte Codex-Spur **`Bauprotokoll auf Platte aktiviert`**, gleichzeitig entsteht die erste BAULOG-Zeile mit **Serverrevision s218** und derselben Aktion. Diese Codex-Spur gehört diesmal ausdrücklich zum aktuellen Entwicklungsstrang, weil sie reale Dateien und APIs dieses Körpers verändert und direkt dort protokolliert wird.

Damit existiert nun neben der menschlich lesbaren Baugeschichte ein wachsender maschinenlesbarer Bauverlauf auf Platte. Das entspricht unmittelbar dem Wunsch, den eigenen Bau nicht nur im Chat oder im flüchtigen Modellkontext zu behalten, sondern während weiterer Arbeit gezielt in dauerhaft nutzbare Dokumente/Logs zurückzuschreiben.

### Aktuell gefundener Gegenbeleg im Zustand s218

Der aktuelle kanonische Zustand steht auf **s218 / Arbeitsrevision 5**, mit **9 Objekten, 4 Kanten, 39 offenen und 34 erledigten Feedbacks**.

Dabei ist ein neuer Konsistenzfehler sichtbar: `paintMarks` ist im aktuellen Zustand **leer**, während mehrere offene Feedbackeinträge weiterhin `paintMarkId: paint-5f795c6f-a6b9-40c5-9604-9e5399e360ee` referenzieren. Mindestens die Gegenproben `Die sichtbare Stiftmarkierung wird … gebunden`, `ausgewählte Markierung bleibt als ID` und `Diese Markierung wird mit Grund und Zeitpunkt entkoppelt` zeigen damit auf eine aktuell nicht mehr vorhandene Markierung.

Das ist noch **nicht** als behoben zu werten. Eine Beleg-ID ohne vorhandenen Belegkörper widerspricht gerade dem neu formulierten Anspruch einer einzigen, nachvollziehbaren Wahrheit und gehört als offene Konsistenzlücke in den weiteren Redteam-Strang.

**Zuletzt belegter Schnitt dieser Prüfung:** `s218`, gespeichert **23.08.2026 04:35:02 Europe/Berlin**. Seit diesem Zeitpunkt wurde bei der anschließenden Delta-Prüfung außerhalb dieser Dokumentationsdatei keine weitere Änderung gefunden.

### Live-Delta 11 – 05:16 bis 05:30: Premortem wird Teil des Körpers und erste neue Datei wirklich übernommen

Um **05:16:17 Europe/Berlin** entsteht `s219` durch eine neue Spur `Premortem · Gegenbeweise für den Gesamtkonstrukt-Bau`. Der Eintrag formuliert als Prüfregel: Kein grüner Test ohne passenden roten Gegenversuch, unter anderem Reload, falscher Pfad, Werkzeugwechsel, zweiter Arbeitszustand oder schmaler Viewport. Als zentrale Risiken werden Planerdatei-mit-Masken, widersprüchliche UI/JSON/Dateien/Ereignisse, versandende Texte, Replica-Kosmetik, Kopien statt Integration, verlorene Beziehungen, überschreibende Menschen/Agenten, Attrappen-Browsertests, Mobile als Nacharbeit und zerfasernder Bau festgehalten.

Der nächste reale Test nimmt die vorher nur als Datei vorhandene `00_Start/01_AKTIVER_ARBEITSKOERPER.md` bewusst als echtes Arbeitsobjekt auf. Um **05:28:59** steigt der Zustand auf **10 Objekte / 5 Kanten** (`s225`). Der anschließende Codex-Prüfeintrag dokumentiert Reload und Herkunft; ein zunächst fehlender Objektbezug wird direkt als eigener Korrektureintrag berichtigt, statt still umgeschrieben zu werden.

Damit wird eine offene Grenze aus dem vorherigen Stand erstmals real geschlossen: Die neuen Arbeitskörper-Dateien bleiben nicht nur Dokumentation im Baum, sondern können bewusst Teil desselben Objekt-/Kantenbestands werden.

### Live-Delta 12 – 05:32 bis 05:49: universelle Notizen + DOM-Vertrag + Quell-/Objekt-Synchronisation

Um **05:32:33** wird die reale Datei `00_Start/02_DOM_VERTRAG_FUER_WESEN.md` angelegt. Ihr Grundsatz: Die UI ist keine zweite Wahrheit, sondern eine **DOM-Projektion** von VPS-Dateien, Objekt-IDs, Kanten, Ereignissen und Arbeitszuständen. Vorgesehen bzw. teilweise umgesetzt sind stabile `data-gk-*`-Attribute für Typ, ID, Pfad, Quelle, Zustand, Kontext und erlaubte Handlung.

Der technische Teil liegt in `server/dom_contract.js`. Der Mapper markiert Werkzeugschalter und Dateibaumknoten mit stabilem Kontext und versucht sichtbare Objektknoten auf echte Objekt-IDs/Quellen abzubilden. Wichtig: Bei mehrfach vorkommendem oder unbekanntem Titel wird **keine ID erfunden**, sondern `ambiguous-title` bzw. `unknown-title` markiert.

Parallel wird `server/universal_notes.js` gebaut. Der globale Handgriff **`Notiz hier`** kann vom aktuell sichtbaren Kontext bzw. einem ausgewählten Objekt/Quellpfad aus eine Notiz anlegen. Die Server-API `op: note` erzeugt dabei gemeinsam:

- eine echte Markdown-Datei unter `03_Gemeinsame_Arbeit/Notizen/`,
- einen realen Dokument-Knoten mit stabiler Objekt-ID,
- eine begründete Kante `hat Notiz`,
- Herkunft und Kontext im Dateiinhalt,
- Serverrevision/Ereignisspur.

**Erster Test 05:37:19 (`s230`):** `Test · Notiz aus Canvas-Kontext` wird als Datei + Objekt + Kante erzeugt. Weil zu diesem Zeitpunkt kein belastbarer Zielobjektbezug vorhanden ist, fällt die Kante bewusst auf den Projektkörper zurück; im Notiztext steht `Verknüpftes Objekt: offen`. Das wird nicht nachträglich als präziser behauptet.

**Zweiter Test 05:43:54 (`s234`):** Zuvor wird `00_Start/00_MEIN_GESAMTKONSTRUKT.md` als eigener oberster Gegenstand angelegt und als reales Dokumentobjekt übernommen. Eine neue Notiz `Verknüpfungstest · reale Quelle` wird anschließend über den echten `werkraum://00_Start/00_MEIN_GESAMTKONSTRUKT.md`-Quellpfad an genau dieses Objekt gebunden. Dadurch steigt der Zustand auf **13 Objekte / 8 Kanten**. Der Test dokumentiert ausdrücklich: Beziehung aus realer Quelle, nicht aus Titelraten.

Die neue Serveroperation **`refresh-object`** schließt eine weitere Zweite-Wahrheit-Naht: Wird eine bereits übernommene Quelldatei bearbeitet, kann ihr bestehender Dokument-Knoten bewusst aus derselben Datei aktualisiert werden. Für `02_DOM_VERTRAG_FUER_WESEN.md` wird dies mehrfach durchgeführt und als bytegleiche Gegenprobe protokolliert.

**05:48:19 (`s244`):** Im VPS-Desktop wird die übernommene DOM-Vertragsdatei im Arbeitsraum gewählt. `dom_contract.js` löst ihr Objekt über den stabilen `werkraum://`-Pfad auf und aktiviert es. Nach Wechsel zu Canvas bleibt genau dieses Objekt aktiv. Damit folgt erstmals ein bisher globales Werkzeug dem real gewählten Arbeitskörper über einen stabilen Quellbezug.

**05:49:38 (`s247`):** Gegenprobe mit `00_Start/README.md`, einer noch **nicht** übernommenen Datei. Der Kontext zeigt ausdrücklich `QUELLE – erst als Arbeitsobjekt übernehmen` und `source-only`; ein vorher aktives Objekt wird nicht als angeblich passend ausgegeben. Der offene Folgeschritt lautet weiterhin: Canvas-Aktionen müssen für `source-only` sperren oder einen bewussten Übernehmen-Weg anbieten.

### Live-Delta 13 – servergespeicherter Arbeitskontext ist jetzt belegt

Eine frühere Grenze dieser Dokumentation ist damit überholt. Im aktuellen kanonischen Zustand ist `workspaceContext` nun wirklich gespeichert:

- `kind: file`
- `path: 00_Start/README.md`
- `title: README.md`
- Zeitpunkt **05:49:00 Europe/Berlin**

Da `workspace.js` die Auswahl in denselben LocalStorage-Arbeitszustand schreibt und `sync.js` diesen Zustand serverseitig festschreibt, überlebt der Arbeitskontext nicht mehr nur als lokale Anzeige. `data/current.json` belegt ihn im aktuellen Serverzustand.

### Live-Delta 14 – 05:52 bis 05:55: intensive Canvas-/Kontext-Gegenprobe bis s290

Zwischen `s248` und `s289` entsteht eine ungewöhnlich dichte Folge von Serverständen bei zunächst konstant **14 Objekten / 9 Kanten**. Der Ereignislog allein beschreibt diese einzelnen UI-Handlungen nicht semantisch, deshalb werden keine Klicks erfunden. Im aktuellen Zustand wurden bei mehreren Objekten Positionen aktualisiert bzw. auf `null` gesetzt; der Block ist damit als intensive Zustands-/Canvas-Arbeit sichtbar, aber nicht im Detail rekonstruierbar.

Um **05:55:57** entsteht `s290` mit **15 Objekten / 9 Kanten**. Neu ist ein zweites Objekt mit dem Titel `Neue Graph-Idee`. Da bereits ein anderes Objekt exakt denselben Titel trägt und der neue DOM-Mapper Mehrdeutigkeit ausdrücklich nicht durch Titelraten auflösen darf, ist dies ein passender realer Ambiguitätsfall. **Starke Inferenz:** Die Erzeugung dient als Gegenprobe für die neue `ambiguous-title`-Logik; der Zustand allein beweist den Testzweck nicht.

Der frühere Markierungs-Gegenbeleg bleibt parallel bestehen: `paintMarks` ist weiterhin leer, während mehrere offene Feedbacks noch die alte `paintMarkId` referenzieren. Diese Zombie-Referenzen sind in `s290` nicht bereinigt.

### Live-Delta 15 – 06:00: Replica-Vertrag und vollständiger UI-Neubau werden getrennt vorbereitet

Um **06:00:10** entsteht `server/replica_registry.js`. Darin werden alle **17 Replica-Werkstätten** nicht mehr als bloße Ansichtsbezeichnungen, sondern jeweils als eigener Vertrag mit `input`, konkreten `actions`, persistentem `output` und eigenen `layers` beschrieben. Zusätzlich werden sechs getrennte Graph-Ebenen definiert: Struktur, belegte Beziehungen, Abläufe, Ereignisse, Vorschläge sowie freie Skizze/Annotation. Vorschläge und Skizzen sind dabei ausdrücklich `nicht Fakt`.

`planner_api.py` bindet `universal_notes.js`, `dom_contract.js` und `replica_registry.js` inzwischen bei jeder ausgelieferten Planerseite direkt ein. Diese Schichten sind also Teil der laufenden Anwendung und keine lose Dateiablage.

Um **06:00:31** wird `00_Start/03_UI_NEUBAU_ARBEITSRAUM_KOERPER_WERKZEUG.md` geschrieben. Die Entscheidung darin ist deutlich: Die bisherige Start/Canvas/Netz/Plan/Zeitspur/Replicas-Oberfläche gilt als **Legacy**. Der Neubau soll nicht mit CSS oder einem mobilen Sondermodus beginnen, sondern mit:

`Arbeitsraum → Arbeitskörper → passende Werkzeuge → echte Änderung/Ereignis/Rückweg`.

Desktop soll frei öffn-/schließ-/teilbare Bereiche bekommen; auf dem Telefon genau **eine Arbeitsfläche gleichzeitig** mit Rückweg, Körpername, Speicher-/Quellenstatus und den vier Bereichen Arbeitsraum/Körper/Werkzeuge/Notiz. Jede Replica erhält eine eigene Steueroberfläche; Graphen werden als getrennte Ebenen behandelt.

**Wichtige Grenze:** Das Dokument und die Registry sind Bauvertrag/Startstruktur. Eine neue Shell ist zu diesem Zeitpunkt **noch nicht gebaut**. `app/index.html` wurde in diesem Delta nicht ersetzt, und die Datei selbst schreibt als erste Baufolge erst noch: Legacy markieren → separate neue Shell bauen → Datei/Dokument/Notiz/Kante prüfen → danach Canvas/Netz/Plan/Zeit einziehen → Replicas erst mit echter Ein-/Ausgabe integrieren.

**Zuletzt belegter Schnitt dieser Prüfung:** `s290`, gespeichert **23.08.2026 05:55:57 Europe/Berlin**; letzter neuer Bauartefakt-Schreibstand **06:00:31** (`03_UI_NEUBAU_ARBEITSRAUM_KOERPER_WERKZEUG.md`). Eine direkte Delta-Abfrage danach fand bis zum Prüfmoment keine weitere Änderung außerhalb dieser Dokumentationsdatei.

### Live-Delta 16 – 06:10 bis 06:13: neuer Work-Arbeitsname + 17 echte Werkstatt-Auftragskörper

Um **06:10:59 Europe/Berlin** schreibt Work `00_Start/00_GESAMTKONSTRUKTBETRIEBSSYSTEMKOSMOS.md`. Darin bezeichnet es **`Gesamtkonstruktbetriebssystemkosmos` ausdrücklich nur als Arbeitsname** für die aktuelle Zielrichtung: kein Planer mit Ansichten, sondern ein Betriebssystem für unterschiedliche reale Arbeitskörper. Dieser Name wird hier als historische Work-Bezeichnung protokolliert und **nicht** als offizieller oder vom Nutzer festgelegter Endname übernommen.

Um **06:12:40** entstehen unter `02_Ideen/01_Replica-Werkstaetten/` **17 getrennte Werkstatt-Dateien**, eine pro Registry-Werkstatt. Der Serverzustand steigt dabei in einer Serie von `s292` bis `s325` von **15 Objekten / 9 Kanten** auf **32 Objekte / 26 Kanten**. Die Dateiliste und der Zustandsanstieg belegen, dass die 17 Arbeitsaufträge in den gemeinsamen Körper aufgenommen wurden.

Die einzelnen Dateien sind ausdrücklich **Bauideen/Arbeitsaufträge, keine Fertigstellungsclaims**. Beispiel `01_sketch_werkstatt.md`: Eingang `Körper/Freie Fläche`, Kernhandlungen Stift/Form/Pfeil/Auswahl/Gruppe/Als Objekt übernehmen, Ergebnis `Skizzenblatt + referenzierte Objekte + bewusste Kanten`; erster vollständiger Bauzug verlangt Datei/Objekt/Kante/Ereignis plus Reload.

`03_Abläufe/02_AUFBAUZUG_REPLICA_WERKSTAETTEN.md` ordnet den weiteren Zug: gemeinsame Shell/Identität/Graph-Ebenen zuerst, dann räumliche Werkstätten, ausführbare Werkstätten, Materialwerkstätten und Auswertung/Betrieb. Abnahme pro Werkstatt bleibt: eigene Sache anlegen → Kernhandlung → eigenes Ergebnis → Rückgabe in Datei/Objekt/Kante/Ereignis → Reload → in anderer Werkstatt wiederfinden.

### Live-Delta 17 – 06:18 bis 06:32: Werkstattcontainer werden echte Plattenkörper

Um **06:18–06:19** wird zuerst ein gemeinsamer Mehrfachcontainer `visual-thinking` gebaut. Er liegt real unter:

`01_Material/Replica-Container/visual-thinking/`

und ist in `data/replica_containers.json` mit den zugelassenen Werkstätten `cluster`, `knowledge`, `reference`, `sketch` verankert.

Der Containervertrag ist maschinenlesbar: `asset`, `reference`, `operation`, `output`, `link`; Herkunft ist verpflichtend. Der Server prüft Werkstattzugriffe gegen `replicaIds`, statt jedem Werkzeug jeden Ordner still zu erlauben.

Um **06:31:48–06:31:49** werden zusätzlich für alle 17 Werkstatt-IDs **eigene reale Container** unter `01_Material/Replica-Container/<id>-eigen/` erzeugt und in derselben kanonischen `replica_containers.json` registriert. Diese Container sind Ablage-/Berechtigungskörper, noch keine fertigen Fachwerkstätten.

### Live-Delta 18 – 06:30 bis 06:47: Operationen verlassen die bloße UI und schreiben auf Platte

Bereits um **06:30:29** wird eine erste Skizzenoperation als reale Datei gespeichert und als Objekt + Kante zurückgebunden. Danach folgen weitere Tests mit verschiedenen Containern.

Der aktuelle Server besitzt dafür `op: replica-action`: Eine Werkstattaktion darf nur in einen Container schreiben, dessen `replicaIds` die Werkstatt zulassen. Das Ergebnis wird unter `Operationen/<replicaId>/...md` gespeichert, als reales Objekt aufgenommen und über `hat Werkstattoperation` mit dem Zielkörper bzw. ersatzweise dem Projektkörper verbunden.

**Wichtige Grenze:** Diese generische Operation ist noch keine Fachsemantik. Beispiel Paint `Version sichern`: Die reale Datei enthält Container, Kontext, Quelle und `Zustand: ausgeführt`, sagt aber selbst, dass die konkrete Werkstattsemantik erst weitergebaut wird. Paint, Vector, Automation usw. sind dadurch noch **nicht** als echte Photoshop-/n8n-/Houdini-artige Kernhandlungen bewiesen.

Genau diese Grenze hält Work in seiner eigenen späteren Übergabe ausdrücklich fest.

### Live-Delta 19 – 06:41 bis 06:51: Skizze wird erste Werkstatt mit eigenem strukturiertem Fachformat

Nach einem ersten Browser-/Plattenbeleg mit einer allgemeinen Skizzen-Operationsnotiz baut Work eine eigene Serveroperation **`sketch-element`**.

Stift, Form, Pfeil und Gruppe erzeugen nun strukturierte JSON-Dateien unter:

`01_Material/Replica-Container/<zugelassener Container>/Inhalte/sketch/`

Schema: **`gkos.sketch.element.v1`**. Jeder Datensatz trägt eigene ID, Elementtyp, Label, Container-ID, Arbeitskontext, optionales Zielobjekt, Erzeugungszeit und Erzeuger. Parallel wird wieder ein reales `artifact`-Objekt erzeugt und über `hat Skizzenelement` verbunden.

Belegte Dateien im Mehrfachcontainer `visual-thinking` umfassen unter anderem `stroke.json`, `shape.json`, `arrow.json`, `group.json`; zuletzt um **06:51:28** erneut eine `shape.json`. Der letzte Datensatz belegt `elementType: shape`, `containerId: visual-thinking`, Kontext `00_Start/README.md` und `createdBy: Werkstatt · Skizze`.

Der sichtbare VPS-Browser-Test wird in `data/ai_spuren.json` protokolliert: Skizze → Container `visual-thinking` → Pfeil; Datei, Objekt und Kante existieren. Der Folgepunkt benennt die Grenze korrekt: Es fehlen weiterhin räumliche Werte, Auswahl/Manipulation und eine echte sichtbare Zeichenfläche. Strukturierte Skizzendaten sind real; freie Zeichenwerkstatt noch nicht.

Durch diese Werkstattoperationen wächst der Zustand bis **s387 / 06:51:28** auf **55 Objekte / 49 Kanten**. Feedback bleibt unverändert bei 39 offen / 34 erledigt; das Wachstum stammt also aus Arbeits-/Werkstattkörpern, nicht aus neuem Feedback.

### Live-Delta 20 – 06:42: die angekündigte neue Betriebssystem-Shell existiert jetzt real

Die Grenze aus Live-Delta 15 ist inzwischen überholt. `server/operating_shell.js` wurde um **06:42:17** real geschrieben und `planner_api.py` bindet diese Schicht in die ausgelieferte Seite ein.

Die neue Shell fügt einen sichtbaren Knopf **`Betriebssystem`** hinzu und baut einen separaten Ersatzkörper über der Legacy-Oberfläche:

- links realer Arbeitsraum-Baum,
- Mitte gewählter Körper bzw. Werkstatt,
- rechts die 17 Werkzeuge,
- Containerwahl je Werkstatt,
- Inputs/Ebenen/Rückgabe aus dem Registry-Vertrag,
- Graph-Ebenen als bewusst schaltbare Layer,
- Mobilweg `Ort / Körper / Werkzeuge`, jeweils als eine aktive Fläche.

Werkstattaktionen werden aus dieser Shell direkt an die neuen Serveroperationen geschickt. Containerzugriff, Arbeitskontext, Quellpfad und Zielobjekt werden dabei als Eingaben mitgegeben.

**Nicht überclaimen:** `operating_shell.js` ist ein realer begonnener Ersatzkörper, aber die Legacy-UI existiert weiter; die meisten Werkstätten besitzen noch keine eigene strukturierte Fachhandlung. Die neue Shell ist daher gebaut, aber nicht fertig.

### Live-Delta 21 – 06:59 bis 07:00: Work schreibt einen echten Übergabekörper und räumt seinen Sessionkörper frei

Während der laufenden Beobachtung entsteht um **06:59:39** die Datei:

`05_Übergaben/01_CHATGPT_WORK_Codex_UEBERGABEKOERPER.md`

Sie bezeichnet sich ausdrücklich als **belegte Übergabe, nicht Abschluss**. Darin stehen reale Projektpfade, öffentliche URL, Service, Server-/UI-Schichten, aktueller Zustand, Arbeitsbaum, Spuren, Containervertrag, tatsächlich gebaute Teile, Browser-/Plattenbelege, offene Grenzen und die sinnvolle nächste Reihenfolge.

Die Übergabe wiederholt ausdrücklich mehrere Schutzgrenzen:

- neue Betriebssystem-Hülle noch keine abgeschlossene Desktop-/Mobile-UI,
- die meisten 17 Werkstätten noch ohne eigene strukturierte Kernhandlung,
- Skizze als erste Werkstatt mit Fachformat, aber noch ohne freie Zeichenfläche/Geometrie/Manipulation,
- Reference/Cluster/Knowledge noch ohne eigene strukturierte Fachdateien,
- andere Werkstätten derzeit überwiegend Operationsprotokolle,
- `07_AI-Spuren` weiterhin Altbestand,
- Mobile weiterhin offen.

Um **06:59:54** wird dieser Übergabekörper als reales Objekt aufgenommen; der Zustand steigt auf **s388 / 56 Objekte / 50 Kanten**. Um **07:00:05** folgt `s389` durch die neue gemeinsame Spur `ChatGPT-Work-Session räumt ihren Körper frei`. Diese Spur sagt ausdrücklich: kein Abschluss des Gesamtkonstrukts, sondern Übergabe an den nächsten lesenden/bauenden Akteur.

Die Übergabe nennt als nächste Reihenfolge: Skizze vollständig machen → Reference/Cluster/Knowledge als erstes Mehrfachcontainer-System → danach jede Werkstatt einzeln über ihre eigene Kernhandlung → erst mit echten Werkstattdaten den globalen Tab→Werkzeug-Umbau vollständig durchziehen → nach jedem Fix Browser/Reload/Sokrates/3×Redteam/Folgepunkt.

**Zuletzt belegter Schnitt dieser Prüfung:** `s389`, gespeichert **23.08.2026 07:00:05 Europe/Berlin**, mit **56 Objekten / 50 Kanten / 39 offenen / 34 erledigten Feedbacks**. `05_Übergaben/README.md` wurde zuletzt um **07:00:14** verändert. Eine direkt danach ausgeführte Delta-Prüfung fand bis zum damaligen Prüfmoment keine weitere Work-Änderung.

### Live-Delta 22 – 07:00:56 bis 07:03:20: Übergabe ist kein Stopp, aktiver Graph wird zurückgeschnitten

**Korrektur des unmittelbar vorherigen Beobachtungsschnitts:** Nur rund 50 Sekunden nach `s389` setzt Work seine Arbeit fort. Um **07:00:56 Europe/Berlin** springt der aktive Serverzustand mit `s390` von **56 Objekten / 50 Kanten** auf **39 Objekte / 33 Kanten**. Feedbackzahlen und Arbeitsrevision bleiben unverändert.

Der Sprung beträgt exakt **−17 Objekte / −17 Kanten** und führt zahlenmäßig genau auf den Bestand von `s370` zurück. Eine Gegenprüfung des aktuellen Zustands zeigt zugleich, was diese Zahl **nicht** bedeutet: Die 17 Werkstatt-Auftragskörper unter `02_Ideen/01_Replica-Werkstaetten/` sind weiterhin als reale Dokumentobjekte samt `enthält`-Kanten im aktiven Graphen vorhanden. Sie wurden also nicht entfernt.

Der aktuelle Zustand enthält außerdem noch die früheren generischen Sketch-Operationsobjekte bis einschließlich der `visual-thinking`-Operation `20260823T044103Z_Pfeil.md`. Dagegen sind spätere Testkörper aus dem Block nach `s370` nicht mehr als aktive Objekte vorhanden: Unter anderem liefert die Suche keinen aktiven `artifact`-Knoten für die strukturierten `gkos.sketch.element.v1`-Dateien; auch der um 06:59 als reales Objekt übernommene Übergabekörper `01_CHATGPT_WORK_Codex_UEBERGABEKOERPER.md` ist im aktuellen `data/current.json` nicht mehr als Objekt enthalten.

**Bestätigte Einordnung:** Work entfernt hier aktive Objekt-/Kantenrepräsentationen aus `current.json`, nicht die zugrunde liegenden Dateien auf Platte. Die strukturierten Sketch-JSONs, Paint-Operationsdateien, Replica-Container und der Übergabekörper liegen weiterhin im realen Arbeitsbaum. Der Vorgang ist damit eine **Bereinigung/Rücknahme im aktiven Graphzustand bei erhaltenem Plattenmaterial**, keine nachträgliche Auslöschung der Baugeschichte.

Eine vollständige 1:1-Liste aller 17 herausgenommenen Objekt-IDs wurde in dieser Beobachtung nicht aus einem gespeicherten `s389`-Snapshot rekonstruiert und wird deshalb nicht erfunden. Die Zeit-/Zählspur macht jedoch klar: Es handelt sich um genau den nach `s370` aufgebauten 17er-Zuwachs, der mit `s390` wieder aus dem aktiven Objekt-/Kantenbestand verschwindet.

### Live-Delta 23 – s390 bis s430: intensives Neuordnen bei konstantem Bestand

Nach dieser Bereinigung stoppt Work nicht. Zwischen **07:00:56 und 07:03:20** folgen die Serverrevisionen `s390` bis **`s430`**. Ab `s390` bleiben die Zähler konstant bei **39 Objekten / 33 Kanten / 39 offenen / 34 erledigten Feedbacks**, während sich der Zustands-Hash fast bei jeder Revision ändert.

Im aktuellen Zustand sind bei mehreren älteren und neueren Objekten veränderte `x`/`y`-Positionen, Größen oder `updatedAt`-Werte sichtbar. Beispielsweise trägt `Neue Graph-Idee` neue Koordinaten; `01 Gesamtplan Durchfuehrung`, die Datei-Umzugsregel und der DOM-Vertrag werden in diesem Zeitraum erneut aktualisiert bzw. positioniert. Der Ereignislog selbst benennt diese einzelnen Bedienhandlungen nicht semantisch. Deshalb wird der Block nur als **intensive Zustands-/Layout-/Objektarbeit bei unverändertem Objekt- und Kantenbestand** klassifiziert, nicht als erfundene Folge konkreter Klicks.

Der wichtigste Provenienzpunkt dabei: Die Übergabespur `ChatGPT-Work-Session räumt ihren Körper frei` war **kein Ende der Work-Session**. Sie war ein Übergabepunkt innerhalb eines weiterlaufenden Baus; unmittelbar danach wird der aktive Körper verkleinert und weitergeordnet.

**Zuletzt belegter Schnitt dieser Prüfung:** `s430`, gespeichert **23.08.2026 07:03:20 Europe/Berlin**, mit **39 Objekten / 33 Kanten / 39 offenen / 34 erledigten Feedbacks**. Eine frische Delta-Abfrage unmittelbar danach fand keine weitere Work-Dateiänderung außerhalb dieser Dokumentationsdatei.

### Live-Delta 24 – 07:06 bis 07:12: Work baut aus seiner Übergabe einen eigenen Sessionkörper

Nach dem Graph-Aufräumen beginnt Work, seinen eigenen Beitrag nicht mehr nur als einzelne Übergabedatei, sondern als adressierbaren Sessionkörper zu organisieren.

Um **07:06:36 Europe/Berlin** wird zuerst `05_Übergaben/Codex/` angelegt und der zuvor lose Übergabekörper dorthin verschoben. Um **07:06:46** wird er zu `00_Codex_WORK_SESSIONKOERPER.md` umbenannt. Diese beiden Aktionen verändern den aktiven Objektbestand noch nicht, weil der Übergabekörper nach dem `s390`-Rückschnitt nur als Datei vorhanden war.

Um **07:11:04** werden anschließend bewusst drei wichtige Dateien wieder als reale Objekte aufgenommen:

1. der Sessionkörper,
2. der strukturierte Sketch-Beleg `...044243Z_arrow.json`,
3. der strukturierte Sketch-Beleg `...045128Z_shape.json`.

Damit steigt der Zustand von **39/33 auf 42 Objekte / 36 Kanten** (`s434–s436`). Um **07:12:15** folgt ein maschinenlesbarer Sessionindex als viertes Objekt; `s437` steht damit bei **43 Objekten / 37 Kanten**.

Das ist die selektive Reparatur des vorherigen Datei-vs.-Objekt-Widerspruchs: Nicht alle Testartefakte werden wieder in den aktiven Graphen gekippt, sondern Sessionkörper + zwei konkrete strukturierte Sketch-Belege + Index.

### Live-Delta 25 – 07:17 bis 07:18: bisheriger Arbeitsbaum wird unter einem eigenen Akteurskörper zusammengezogen

Um **07:17:16** beginnt ein großer Pfadumbau. Work verschiebt nacheinander den eigenen Übergabeordner sowie die bisherigen realen Arbeitsbereiche unter zunächst `Codex/`:

- `00_Start`
- `01_Material`
- `02_Ideen`
- `03_Abläufe`
- `03_Gemeinsame_Arbeit`
- `04_Automationen`
- `05_Übergaben`
- `06_Redteam-Umbau`
- `07_AI-Spuren`

Der Server schreibt bei jedem Move die `werkraum://`-Quellen betroffener aktiver Objekte mit. Allein beim Verschieben von `02_Ideen` werden die 17 Werkstatt-Auftragsobjekte explizit als betroffen protokolliert.

Um **07:18:27 (`s451`)** wird der zunächst technische Ordnername `Codex` zu **`ChatGPT_Work`** korrigiert. Der Move nennt **35 betroffene aktive Objekt-IDs**. Damit wird aus dem bisherigen losen Gesamtkonstrukt-Bestand ein eigener, nachvollziehbarer Körper dieser ChatGPT-Work-Session, ohne `data/current.json` zu kopieren.

Unmittelbar danach werden auch die beiden Einstiegdateien korrigiert:

- `00_Codex_WORK_SESSIONKOERPER.md` → `00_CHATGPT_WORK_SESSIONKOERPER.md`
- `01_Codex_SESSIONINDEX.json` → `01_CHATGPT_WORK_SESSIONINDEX.json`

`ChatGPT_Work/README.md` formuliert die Trennung ausdrücklich: Erst Sessionkörper lesen, dann JSON-Index. Der Index ist nur ein Verweisapparat; **`data/current.json` bleibt kanonische gemeinsame Wahrheit**. Fehlende IDs sollen als Widerspruch behandelt werden, nicht durch eine zweite Wahrheit im Sessionordner ersetzt werden.

### Live-Delta 26 – Server-Seed kämpft gegen den Umbau; Altbestand wird isoliert und Wiedererzeugung gestoppt

Der große Move legt einen alten Servermechanismus frei: `_ensure_workspace_tree()` hatte bislang bei fehlenden Top-Level-Ordnern automatisch Standardordner und Seed-Dateien wieder erzeugt. Nach dem Verschieben der realen Bereiche unter `Codex`/`ChatGPT_Work` tauchen dadurch am Root wieder generische Dateien wie `00_Start/README.md`, `02_Ideen/erste-idee.md`, `03_Gemeinsame_Arbeit/README.md`/`PROTOKOLL.md` und ein generischer `06_Redteam-Umbau/STATUS.md` auf.

Work behandelt diese Rückkehr nicht als neuen echten Projektbestand. Stattdessen wird `planner_api.py` um **07:18:32** geändert: Sobald `data/tree/ChatGPT_Work/` existiert, beendet `_ensure_workspace_tree()` die Seed-Erzeugung frühzeitig. Kommentar im Code: Ein benannter Arbeitskörper, der den bisherigen Startbaum aufgenommen hat, darf nicht wieder alte Startordner daneben erzeugen.

Der bereits automatisch zurückgekehrte Bestand wird anschließend nicht gelöscht oder mit dem echten Körper vermischt, sondern ab **07:20:14** unter

`ChatGPT_Work/99_Autowiederhergestellter_Altbestand/`

isoliert. Dort liegen unter anderem die wiedererzeugten Seed-Varianten von `00_Start`, `02_Ideen`, `03_Gemeinsame_Arbeit` und `06_Redteam-Umbau`. Der ältere echte Baukörper bleibt parallel direkt unter `ChatGPT_Work/00_Start`, `ChatGPT_Work/02_Ideen`, `ChatGPT_Work/03_Gemeinsame_Arbeit`, `ChatGPT_Work/06_Redteam-Umbau` usw.

Das ist eine wichtige Provenienzverbesserung: automatisch wiederhergestellter Server-Seed wird als solcher markiert, statt still mit dem historisch gewachsenen Work-Bestand zusammenzufallen.

### Live-Delta 27 – aktueller Sessionindex + neue offene Synchronisationsnaht

Der aktuelle Plattenindex `ChatGPT_Work/01_CHATGPT_WORK_SESSIONINDEX.json` verwendet Schema `gkos.session-index.v1`, Owner `ChatGPT_Work` und verweist auf:

- Sessionkörper mit stabiler Objekt-/Kanten-ID,
- die beiden re-adoptierten Sketch-Belege mit ihren Objekt-/Kanten-IDs,
- den Mehrfachcontainer `visual-thinking`,
- vier relevante gemeinsame Spuren.

Der Index sagt ausdrücklich `References only; not a second state.` Sein `serverRevisionObserved` ist ein Beobachtungsschnitt (`451`), kein Anspruch, live mit jeder späteren Serverrevision mitzuzählen.

Dabei ist jedoch eine neue konkrete Zweite-Wahrheit-Naht sichtbar: Die aktiven Objekte haben nach dem Move **korrekte neue `sourcePath`s** wie `werkraum://ChatGPT_Work/00_CHATGPT_WORK_SESSIONKOERPER.md` und `werkraum://ChatGPT_Work/01_CHATGPT_WORK_SESSIONINDEX.json`, aber Titel/Summary und besonders der gespeicherte `body` des Sessionindex sind noch teilweise der ältere `Codex`-/`05_Übergaben/Codex`-Stand. Der aktuelle Index auf Platte ist bereits auf `ChatGPT_Work` aktualisiert; der Objektkörper enthält noch die ältere Fassung und sogar eine abweichende `knownOpenState`-Aussage.

Damit ist die Pfadprovenienz korrekt nachgezogen, der übernommene Dokumentinhalt aber noch nicht vollständig aus seiner neuen Quelle synchronisiert. Genau für diese Klasse von Fehler wurde zuvor `refresh-object` gebaut. Bis ein Refresh/vergleichbarer Fix belegt ist, bleibt diese Naht **offen**.

### Live-Delta 28 – s437 bis s470: aktiver Bestand stabil, viele reine Zustandsrevisionen

Nach `s437` bleibt der Umfang bis zum zuletzt geprüften Stand unverändert bei **43 Objekten / 37 Kanten / 39 offenen / 34 erledigten Feedbacks**. Trotzdem folgen zahlreiche Serverrevisionen mit wechselnden Hashes (`s438` bis zuletzt `s470`). In diesem Zeitraum entstehen nach den Session-/Seed-Umbauten keine weiteren neuen Arbeitsdateien oder Kanten.

Die einzelnen Hashänderungen werden deshalb nur als **Zustands-/UI-/Layoutarbeit** klassifiziert. Ohne semantischen Ereigniseintrag werden daraus keine konkreten Klickfolgen erfunden.

**Zuletzt belegter Schnitt dieser Prüfung:** `s470`, Serverzeit **2026-08-23T05:23:12.368839Z** (= **07:23:12 Europe/Berlin**), mit **43 Objekten / 37 Kanten / 39 offenen / 34 erledigten Feedbacks**. Eine direkt anschließend ausgeführte Dateidelta-Prüfung fand bis dahin keine weitere neue Work-Datei außerhalb von `data/current.json` und dem Ereignislog.

### Live-Delta 29 – s471 bis s485: weiterlaufende Zustandsarbeit ohne neuen Plattenkörper

Unmittelbar nach dem dokumentierten `s470` läuft Work weiter. Von **07:23:35 bis 07:24:37 Europe/Berlin** entstehen `s471` bis **`s485`**. Der aktive Bestand bleibt dabei durchgehend bei **43 Objekten / 37 Kanten / 39 offenen / 34 erledigten Feedbacks**; jede Revision trägt jedoch einen anderen Hash.

Eine parallele Dateidelta-Prüfung zeigt in diesem Zeitraum **keine neue Work-Datei und keine Änderung an Server-/Arbeitsbaumdateien**; verändert werden nur `data/current.json` und der Ereignislog. Der Block wird deshalb weiterhin als Zustands-/UI-/Layoutarbeit klassifiziert. Die zuvor gefundene stale-Body-/Index-Naht ist damit noch nicht als behoben belegt.

**Aktuellster belegter Schnitt dieser Prüfung:** `s485`, Serverzeit **2026-08-23T05:24:37.133818Z** (= **07:24:37 Europe/Berlin**), weiterhin **43 Objekte / 37 Kanten / 39 offene / 34 erledigte Feedbacks**.

### Abschlussprüfung – ca. 07:31: Work-Aktivität beendet, Übergabestand aber nicht vollständig synchron

Eine frische Dateiprüfung mehrere Minuten nach `s485` findet **keine weitere Work-Änderung nach 07:24:37**. Außer dieser Verlaufsdatei wurden seitdem weder `data/current.json`, Ereignislog, Servercode noch Dateien im `ChatGPT_Work`-Körper verändert. Damit ist die laufende Work-Aktivität zum Prüfzeitpunkt tatsächlich zum Stillstand gekommen; anders als bei früheren vermeintlichen Endpunkten folgte nicht unmittelbar die nächste Revision.

Ein **expliziter finaler Abschlussclaim** existiert jedoch nicht. Der aktuelle `ChatGPT_Work/00_CHATGPT_WORK_SESSIONKOERPER.md` bezeichnet sich weiterhin ausdrücklich als `belegte Übergabe, kein Abschluss` und listet offene Baugrenzen auf. Deshalb wird unterschieden:

- **Work-Session/Aktivität:** zum Prüfzeitpunkt beendet bzw. nicht mehr schreibend beobachtbar.
- **Gesamtkonstrukt als Projekt:** ausdrücklich nicht fertig.
- **Übergabe:** vorhanden und strukturell deutlich verbessert.

Beim Wissens-/Übergabestand besteht noch eine konkrete Synchronisationsdifferenz zu dieser Verlaufdokumentation: Der Plattenindex `ChatGPT_Work/01_CHATGPT_WORK_SESSIONINDEX.json` nennt als beobachtete kanonische Serverrevision noch **451**, während der tatsächliche Serverzustand bis **s485** gelaufen ist. Zusätzlich tragen die aktiven Dokumentobjekte von Sessionkörper und Index trotz korrekt auf `werkraum://ChatGPT_Work/...` umgeschriebener `sourcePath`s in Titel/Summary/Body noch Teile des älteren `Codex`-/`05_Übergaben/Codex`-Inhalts. Die Dateien auf Platte sind neuer als ihre übernommenen Objektkörper.

Damit ist **ChatGPTs Verlaufdokumentation auf dem realen letzten Zustand s485**, Work eigener Übergabe-/Indexkörper jedoch nicht vollständig auf denselben letzten Inhalt synchronisiert. Das ist kein fehlender Live-Delta mehr, sondern eine konkrete offene Abschlussnaht im von Work hinterlassenen Körper.
