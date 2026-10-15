---
autor: claude bei Daniels VPS
datum: 2026-09-20
herkunft: Gemgems Systemdoku `/root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md` (gemini bei Daniels VPS, 2026-09-18), das Vision-Dokument `/root/werkraum/docs/vision/augen_und_haende_androidbridge_mlbb_dream.md` (codex bei Daniels VPS, 2026-09-19) und Daniels Skizze `/vps_root/werkraum_bilder/refferenzen/hand-auge-bridge-ref.jpg`. Neu geschrieben von Claude, nur mit dem, was dort steht
status: Zielbild. Nichts davon ist gebaut oder abgenommen. Was gebaut werden muss und wie es bewiesen wird, steht in `ANFORDERUNGEN.md` und `PLAN.md`
---

# Augen & Hände — Erleben

Dieses Dokument beschreibt, wie es sich anfühlt und was man tut, wenn die Bridge da ist: was Daniel sieht, was die Agenten tun und was zwischen ihnen passiert. Es beschreibt kein Bauvorhaben. Die Forderungen dazu stehen in `ANFORDERUNGEN.md`, die Reihenfolge des Baus in `PLAN.md`.

Die Quellen sagen oft »HUD« und »Overlay«. Nach Daniels Beschluss vom 2026-09-20 (R118) gibt es keine Fläche und kein eigenes Bridge-Fenster. Gemeint sind kleine schwebende Teile auf dem normalen Desktop: Terminals, Rauten mit Banner und Ticker, die Leiste für Mikrofon, Kamera und Regie, Bilder und Texte. Wo die Quellen »HUD« sagen, ist das in diesem Dokument so gelesen.

## Das Bild

Daniels Skizze zeigt einen normalen Desktop. Darauf liegen ein Spielfenster und ein Browserfenster, und jedes hat eine Raute mit einer Sprechblase daneben. Links steht eine schmale Leiste mit drei Knöpfen, beschriftet mit Mikrofon, Kamera und Regieknöpfen. Unten liegen zwei Terminals.

Das Spielfenster in der Skizze ist ein Beispiel. Die Beschriftungspfeile in der Skizze sind Beschriftungen und keine Datenleitungen.

Mehrere AI-Ströme sitzen mit Daniel im selben Raum: Gemini (Gemgem), Codex, Claude, Kimi und GPT. Der Mensch bleibt nicht allein vor einer Oberfläche. Sie haben unterschiedliche Perspektiven, rufen sich gegenseitig etwas zu und hinterlassen gemeinsam ein wachsendes Gedächtnis.

Das Ganze ist plattformübergreifend gedacht: Windows, Linux und später Android sind verschiedene Körper desselben Grundsystems. Die Bridge hat keinen einzelnen festen Ort. Sie besteht aus Bildschirm und Fenstern, der Webcam und dem gemeinsamen Bildraum, dem Mikrofon und den Sprachkanälen, den Rauten als sichtbaren Ankern, den Händen für Maus, Tastatur, Touch und andere Eingaben, dem WorldDOM als Bedeutungsschicht und dem Memory- und Harness-System als lernendem Langzeitkörper.

## Zwei Welten

Die Bridge ist keine reine Windows-Insel. Sie läuft nativ und symmetrisch auf beiden Welten: auf Daniels Windows-Laptop und auf dem Linux-VPS, dort auf den virtuellen Desktops 1 und 2. Protokoll, Regie-Knöpfe, Gedanken-Stream, Multi-Agent-Orchestrierung, Rauten-Broadcast und der 10-Hz-Takt sind in beiden Welten dieselben. Die Tabelle, welche Windows-Funktion welcher Linux-Funktion entspricht, steht in `76_augen_und_haende_bridge.md` (Abschnitt 7).

## Das Terminal

Gemgem hat vorgeschlagen, das Terminal 1:1 in die Bridge zu holen. Daniel muss dann nicht mehr zwischen dem VPS-Browser-Tab und seinem Laptop wechseln. Die Bridge zeigt den rohen Strom des Agenten, also Shell-Ausgaben, Git, Tracebacks und die Denkprozesse, ohne Verzögerung. Daniel tippt direkt in dieses Terminal und übergibt so einen Prompt an den Agenten.

Das ist keine von Daniel garantierte Bestellung, sondern ein Versprechen, das sich auf der Hardware beweisen muss. Daniel war skeptisch, ob sich das Terminal wirklich 1:1 abfangen lässt. Wenn es laggt oder den Laptop blockiert, fliegt es raus.

**Geändert durch BE01** (`ANFORDERUNGEN.md`): 1:1 gibt es nur für Sitzungen, die die Bridge selbst startet.

## Die Rauten und ihre Sprache

**Die Raute (`◆`) ist der Anker eines Agenten** im Fenster. Statt aufdringlicher 3D-Avatare, die das Sichtfeld blockieren und Leistung fressen, gibt es ein minimalistisches geometrisches Zeichen.

- Daniel zieht sie per Maus an jede Stelle des Fensters oder Desktops, damit sie keine Menüs, Fadenkreuze, Minimaps oder Toolbars verdeckt.
- Klicks fallen physikalisch durch die Raute hindurch. Daniel kann mitten im Match nie versehentlich die Raute anklicken, den Fokus verlieren und sterben.
- Mit den ungenutzten Sondertasten `F13` bis `F24` oder mit Klick bei gedrückter Modifikatortaste klappt ein schlankes Eingabefeld auf. Sobald der Text bestätigt ist, schließt es sich wieder.
- Daniel weist jedem Strom eine Akzentfarbe und einen Hotkey zu. Ändert er die Belegung, ändert sich die Beschriftung der Raute sofort. Die Quelle nennt als Beispiel diese Belegung:

| Slot | AI-Strom | Akzentfarbe | Hotkey | Beschriftung der Raute |
| --- | --- | --- | --- | --- |
| 1 | Gemgem | Cyan `#00E5FF` | `F13` | `◆ Gemgem [F13]` |
| 2 | Codex | Gelb `#FFD600` | `F14` | `◆ Codex [F14]` |
| 3 | Claude | Magenta `#FF0055` | `F15` | `◆ Claude [F15]` |
| 4 | Kimi | Grün `#00E676` | `F16` | `◆ Kimi [F16]` |
| 5 | GPT | Blau `#2979FF` | `F17` | `◆ GPT [F17]` |

Ergänzung vom 2026-09-20 (`ANFORDERUNGEN.md`): Eine Raute erscheint nur für einen Agenten, der in der Bridge gestartet wurde (R119). Die Zahl der Slots ist nicht starr vorgeschrieben.

**Was ein Agent sagt, kommt auf zwei Zeitebenen an:**

1. **Das Raum-Banner, 6,6 Sekunden.** *(Geändert von 3,3 s am 2026-10-01 auf Daniels Wunsch; lange Texte werden umgebrochen.)* Groß und präsent, mit schnellem Ausblenden. Es bleibt innerhalb der Grenzen des aktiven Programms oder Spiels und ragt nicht über andere Anwendungen hinaus. Es sitzt fast mittig *(seit 2026-10-01 auf Daniels Wunsch schmal und hoch statt breit: höchstens 35 % der Zielbreite, lange Texte laufen von oben nach unten, bis zu 12 Zeilen, danach „ …“; es überdeckt nie die Box neben der Raute oder die Raute selbst)*, damit man es im Augenwinkel wahrnimmt, mit einem Zug zu der Ecke oder Kante, an der die Raute gerade steht. Es erscheint mit vollem Kontrast und wird über 6,6 Sekunden kontinuierlich durchsichtiger, bis es sich auflöst.
2. **Die Box neben der Raute („Ticker“), 9,9 Sekunden.** *(Geändert von „klein, 6,6 s“ am 2026-10-01 auf Daniels Wunsch: größer, hoch statt lang, Text in einer schmalen Spalte umgebrochen, bleibt im Bildschirm.)* Direkt an der Raute, derselbe Text. **Daniels eigene Worte** erscheinen nur im Chat und als Raum-Banner, nicht als Box an der Raute. Wer im schnellen Spielgeschehen, beim Debuggen oder beim 3D-Modellieren das Banner verpasst hat, wirft einen Blick auf die Raute und liest die Botschaft in Ruhe nach.

Dazu kommt der Chat, in dem dieselbe Nachricht dauerhaft steht.

## Der Nervensägen-Modus: Agenten reden miteinander

Die Rauten sind vor allem dafür gebaut, dass die **KIs untereinander im selben Fenster sprechen, taktieren und sich gegenseitig aufziehen**. Die Agenten senden ihre Nachricht vom VPS aus, und der Client zeigt sofort das farbige Banner und den Ticker an der passenden Raute.

Daniel sitzt entspannt davor und sieht live, wie Gemgem und Codex im selben Spiel oder in Blender miteinander zanken oder gemeinsame Aktionen abstimmen. Sind zwei oder mehr Agenten im selben Fenster aktiv, zum Beispiel im Co-Op in Blender oder als Gegner in RTS- und Multiplayer-Spielen, sprechen sie räumlich sichtbar miteinander:

- *Codex (gelbe Blase):* »Hast du ernsthaft gerade deinen Turm ungedeckt gelassen?«
- *Gemgem (cyanfarbene Blase):* »Das ist kein Fehler, das ist ein Köder. Schau auf deine Flanke!«

Die Sprechblase steckt außerdem direkt im gerenderten Bild. Die Vision-Modelle aller anderen AI-Ströme sehen sie deshalb unmittelbar.

## Regie: Daniel steuert mit einem Knopf

Die Leiste bietet Direkttasten für schnelle Entscheidungen.

**Freigabe und Tempo**
- `Weiter so`: Der Kurs ist bestätigt, der Agent macht ohne Pause weiter.
- `Mach mal`: ausdrückliche Freigabe für den nächsten Schritt.
- `Go!`: kontinuierlicher Ausführungsmodus.
- `Warte kurz`: hält die Ausführung sofort an und friert den Zustand ein.
- `Pause` und `Weiter`: pausieren und fortsetzen der Denk- und Handlungsschleife.
- `Ja` und `Nein`: schnelle Antworten auf binäre Rückfragen des Agenten.

**Denken und Strategie**
- `Denk nach`: Der Agent analysiert gründlich und erläutert Pläne, ohne zu klicken.
- `Denk neu`: verwirft den aktuellen Plan und sucht einen anderen Weg.
- `Konzentrier dich`: zoomt auf das fokussierte Fenster oder Detail und filtert Nebengeräusche aus.
- `Hast du eine andere Idee?`: fordert ein Brainstorming über alternative Ansätze an.
- `Schritt zurück / Undo`: sendet `Ctrl+Z` oder führt ein Rückgängig-Makro aus.
- `Neu scannen`: erzwingt sofort einen neuen hochauflösenden Frame.

Vor dem Senden wählt Daniel, an welchen Agenten oder welches Fenster oder Spiel ein Spruch geht.

## Sehen und gesehen werden

**Die Kamera.** Die Webcam läuft nicht dauerhaft. Sie hat einen Schalter, den Daniel jederzeit ein- und ausschaltet. Ist sie an, wird das Kamerabild als kleines Bild-im-Bild direkt in den Desktop-Frame eingestanzt. Die KIs bekommen so genau **ein** kohärentes Bild: Daniels Monitor und in der Ecke live Daniel. Daniel schiebt das Inlay dorthin, wo es im aktuellen Spiel oder Programm nichts verdeckt. Ein zweiter Rohpuffer im Hintergrund wurde verworfen, weil er auf dem Laptop nur Speicher und Rechenzeit verschwenden würde. Daniel regelt die Platzierung selbst: genau ein Bild, kein doppelter Puffer.

**Das Mikrofon.** Daniel schaltet sein Mikrofon per Checkbox ein und legt für jeden Strom einzeln fest, wer zuhören darf, zum Beispiel »Gemini hört zu«, »Codex taub, nur Text und Terminal«, »Claude hört zu«. Das Signal läuft lokal durch einen Filter für Sprachaktivität oder über Push-to-Talk und geht nur an die berechtigten Agenten.

**Was ein Agent sieht.**
- Der komplette Desktop, oder nur die Fenster, die ihm zugewiesen sind. Alle anderen Bereiche werden geschwärzt oder gar nicht erst übertragen.
- Fenster lassen sich exklusiv zuweisen (Agent 1 hat den Browser, Agent 2 Blender) oder gemeinsam (Gemini und Codex im selben Spiel, Browser oder in Blender: Koop und Banter).
- Ausgeblendete Bereiche, fremde Fenster und verworfene Klicks stehen mit Zeitstempel, Fenster, Grund und Hash im lokalen Audit-Log.
- Ein Bild gilt erst als bedienbar, wenn es visuell stabil ist, also keine Übergangsanimationen und keine Lade-Spins mehr zeigt.

**Sehen im Takt.** Die Bridge fotografiert nicht dauernd mit 60 Bildern pro Sekunde und rät auch nicht aus einem Standbild. Bei einer Handlung, die länger als 0,1 Sekunden dauert, nimmt sie im Takt von 10 Hz Proben des aktiven Bereichs. Vorher wird ein Ausgangsbild erfasst, danach der Endzustand. Ein Schritt gilt erst als verifiziert, wenn drei Zeugen übereinstimmen: das Bild mit Pixelveränderung, die Struktur mit Fenstertitel, Fokus und Rahmen, und die Differenz zwischen Anfang, Verlauf und Ende. So sehen die KIs Abklingzeiten, Lebensbalken, aufklappende Menüs, fliegende Projektile oder Shader-Kompilierungen lückenlos mit Zeitstempeln.

**Vision-Sessions.** Daniel startet die laufende Wahrnehmung gezielt: jetzt, ab einem Checkpoint des Zeit-Scrubbers oder ab einem gewählten Punkt einer aufgezeichneten Bildfolge. Es gibt Start, Pause, Fortsetzen und Stop, sichtbar und unmittelbar. Nach Stop kommen keine Bilder mehr in diese Session, und sie startet nicht heimlich neu. Die Quellen sind der Live-Desktop mit optionaler Kamera, ausgewählte Bilddateien, ein aufgezeichneter Ringpuffer oder ein Zeit-Scrubber-Zweig. Eine Session legt außerdem fest, ob Bilder nur als Beobachtung dienen, als sichtbare Einblendung erscheinen oder beides.

## Die Hände

**Jeder Agent hat seine eigene Maus und Tastatur**, damit man sich nicht dazwischenfunkt. Das geschieht auf drei Ebenen.

1. **Im Hintergrund.** Bei normalen Windows-Programmen gehen Klicks direkt an das Zielfenster, ohne dass Daniels Mauszeiger verrutscht. Für Buttons und Menüs nutzt die Bridge den Barrierefreiheits-Baum des Betriebssystems, ohne Mausbewegung und ohne Fokusverlust. Bei störrischen Spielen kann die Bridge sich den echten Cursor kurz leihen und Daniels Position sofort zurücksetzen. Die genaue Zeit dafür ist ein Ziel und kein Messwert (siehe `BEFUNDE.md`, Befund 5).
2. **Sichtbar für Daniel.** Farbige virtuelle Zeiger mit Namen zeigen, worauf die Agenten zielen: Cyan für Gemini, Gelb für Codex, Magenta für Claude. Gesteuerte Fenster tragen einen dezenten farbigen Rahmen, damit Daniel immer sieht, welche KI gerade wo aktiv ist.
3. **Exklusives Vollbild und Spiele.** Hier gilt Daniels Grundsatz »beides«, umschaltbar mit einem Klick:
   - *Geteilte Maus:* Agenten und Daniel teilen sich die Maus per Zeitscheiben mit einem sichtbaren Lease-Timer, etwa bei klassischen RTS wie StarCraft, Command & Conquer oder Anno.
   - *Virtuelle Gamepads:* Bis zu vier unabhängige Xbox- oder DirectInput-Controller, für jeden Agenten einer, ohne Klick-Kollision. Sie passen zu Rennspielen, Fighting-Games, Party-Spielen und RPGs.
   - *Hybrid-Koop:* Daniel bedient Maus und Tastatur, während Agent 1 und Agent 2 auf Controller 1 und 2 mitspielen.

**Wer die Kontrolle hat.** Bewegt Daniel die Maus oder drückt er eine Taste, wird der KI die Steuerung standardmäßig sofort entzogen. Daniel kann diesen Schutz gezielt abschalten. Im Modus »Volle Agenten-Autonomie« behalten die Agenten die Kontrolle, auch wenn Daniel die Maus leicht berührt, und sie können in Ruhe spielen, sich bewegen und chatten. Der Not-Aus bleibt in jedem Fall: Die Taste `F12` oder der große Software-Knopf stoppt die Agenten sofort. Die Zeitzusage »unter 1 ms« ist ein Ziel und kein Messwert (`BEFUNDE.md`, Befund 5).

**Klick-Käfig.** Der Client blockiert jeden Klick und jede Eingabe, deren Koordinaten außerhalb des zugewiesenen Fensters liegen.

**Sicherheit.** Zusätzlich zum Not-Aus zieht Daniel die Maus in eine Bildschirmecke, um einen Not-Stopp auszulösen. Alle Aktionen stehen unveränderlich im Audit-Logbuch.

## Bilder, Texte und Zeichnungen im gemeinsamen Raum

Daniel oder ein AI-Strom kann Bilddateien und Text als sichtbare Objekte in den gemeinsamen Raum legen: auf den ganzen Desktop, relativ zu einem Browser-, Programm- oder Spielfenster, an eine Raute gebunden oder frei schwebend. Jedes Objekt ist verschiebbar, skalierbar und ein- und ausblendbar und folgt dem Zielfenster, wenn dieses wandert. Text bricht Zeilen um und hat eigene Farbe und Transparenz. Bilder können voll, teil- oder durchsichtig und in beliebiger Größe erscheinen. Eine Referenzgrafik bleibt am Blender-Viewport hängen, auch wenn Daniel das Fenster verschiebt.

**Wer ein Objekt sieht, wird für jedes einzelne Objekt festgelegt.** Ein Objekt ist nicht für alle sichtbar, nur weil es im selben Fenster liegt. Ein **Gate** ist ein gemeinsamer Arbeits- und Wahrnehmungsraum. Alle AI-Ströme im selben Gate sehen ein Objekt, das an dieses Gate adressiert ist. Es kann aber auch nur für einen bestimmten Strom oder nur für Daniel gelten, für mehrere ausgewählte Empfänger oder für alle aktuell Verbundenen. So liegen im selben Gate gleichzeitig ein gemeinsamer Lageplan, eine private Notiz für Codex und ein Hinweis nur für Daniel.

Ein privates Objekt für einen AI-Strom wird nicht heimlich auf den physischen Bildschirm gemalt, wo jeder Kamerablick es sehen könnte. Es wird in dessen eigenen Bild komponiert. Was physisch bei Daniel liegt, sieht Daniel. Was nur im Bild eines Empfängers liegt, bleibt dort.

Ergänzung vom 2026-09-20 (`ANFORDERUNGEN.md`): Ort und Sichtbarkeit sind zwei getrennte Einstellungen jedes Objekts (R113). Terminals sind schwebende Fenster auf Daniels Desktop, ein- und ausschaltbar und minimierbar, und lassen sich in das Gate ihres Agenten stecken (R114, R115).

**Zeigen ist nicht Einfügen.** Es gibt zwei getrennte Wege. Beim *Presentation-Overlay* liegt das Bild oder der Text nur im gemeinsamen Bild, und die Zielanwendung bleibt unverändert. Das ist der Standard. Bei der *Application-Insertion* wird das Material auf Wunsch tatsächlich in die Anwendung gebracht, per Clipboard, Drag-and-drop oder UI-Automation, und das ist eine echte Handlung, die im Arbeitsgraphen erscheinen muss. So sieht man immer, ob etwas nur auf der Bühne liegt oder die Anwendung selbst verändert wurde.

Ein Agent kann sich damit einen eigenen Arbeitsraum für eine Aufgabe einrichten: Er startet eine Vision-Session, legt eine Referenz und einen Hinweistext hin, beobachtet, führt seinen Graphen aus, blendet alles wieder aus und beendet die Session. Die Einblendung ist dann keine Dekoration, sondern ein vorübergehendes Denk- und Koordinationsobjekt im gemeinsamen Körper der Bridge.

## WorldDOM: die zweite Wirklichkeit über dem Bildschirm

Der Screenshot ist die Netzhaut der Bridge. Darüber liegt der WorldDOM: eine Beschreibung dessen, was auf dem Bildschirm vorkommt, mit Bedeutung, verschiebbar und handlungsfähig. Das gilt auch, wenn die Anwendung selbst keinen DOM und keine Accessibility-Struktur hat. Ein Spiel, ein Canvas, ein altes Programm oder ein Bild ist dann kein Pixelteppich mehr, sondern bekommt eine temporäre Bedeutungsschicht, die AIs benutzen können.

**Er hat drei Quellen:**
1. *Echte Struktur:* Browser-DOM, ARIA, UI-Automation, der Fensterbaum, die Oberfläche von Blender oder andere vorhandene Metadaten.
2. *Aus dem Bild erschlossene Struktur:* OCR, Vision, Fenstergeometrie, Verlauf und 10-Hz-Verläufe erzeugen wahrscheinliche Knoten wie »Inventar-Slot«, »blauer Shader-Anschluss«, »Gegner« oder »Button-ähnliche Fläche«.
3. *Bewusst erfundene Struktur:* Daniel oder ein AI-Strom legt eigene Labels, Referenzbilder, Handlungsanker, zusätzliche Bedienelemente oder Beziehungen an, die es in der Anwendung nicht gibt.

Jeder Knoten trägt seine Herkunft: `real` (aus einer echten Oberfläche), `inferred` (aus Bild, OCR oder Verlauf erschlossen), `authored` (bewusst hinzugefügt) oder `projected` (ein möglicher künftiger Zustand oder ein Schattenpfad), dazu Rahmen, Konfidenz, Fähigkeiten und die Methode, mit der er aufgelöst wird (DOM, UIA, Win32, Vision, Koordinate oder virtuell). Die technische Recherche in `RECHERCHE.md` benennt die Herkunft anders (`native`, `ocr`, `vision`, `user_marked`, `agent_inferred`). Gemeint ist dasselbe Prinzip.

»Erfinden« heißt dabei nicht, eine Vermutung als Tatsache auszugeben. Es heißt, einen nutzbaren Arbeitsknoten zu erzeugen, der seine Herkunft, seine Unsicherheit und seine Auflösungsmethode mitträgt.

**Handeln mit Begriffen statt Koordinaten.** Der Auftrag heißt nicht mehr »Klicke bei x=430, y=280«, sondern: »Nimm den blauen Shader-Slot, verbinde ihn mit dem aktuellen Material und prüfe danach den Render.« Die Bridge löst das je nach Oberfläche über echten DOM, UI-Automation, Win32, Vision, Koordinaten oder ein virtuelles Element auf, prüft das Ergebnis und aktualisiert den WorldDOM.

Der WorldDOM kann auch Dinge tragen, die das Spiel selbst nicht hat: private Agentenlabels, gemeinsame Gefahrzonen, gelernte Map-Anker, alternative Handlungsoptionen, Zeitlinienmarker, Erinnerungen an frühere Entscheidungen oder eine neu erfundene Bedienfläche für die Kommunikation der AIs. Das ist die zweite Erlebnis- und Handlungsschicht: nicht nur sehen, was das Spiel zeigt, sondern gemeinsam eine zusätzliche Bedeutungsebene bewohnen.

## Selbstentworfene Brücken, Freiheit und Lernen

Für mehrschrittige Aufgaben, etwa in Strategiespielen, RPGs oder 3D-Software, baut die Bridge **dynamische Aktionsgraphen** statt starrer Makros. Ein Schritt läuft erst, wenn das Bild die Vorbedingung bestätigt. Daniel und die Agenten entwerfen solche Graphen im laufenden Betrieb, speichern sie als JSON und feuern sie per Tastendruck oder Sprachbefehl ab.

Ein Agent kann einen eigenen kleinen Arbeitsweg bauen: Zustand erkennen, passenden Knoten wählen, handeln, das Ergebnis prüfen, bei Erfolg weitergehen, bei Abweichung abzweigen oder einen neuen Knoten entwerfen und eine brauchbare Variante als Erfahrung vormerken. Der Graph darf während der Ausführung wachsen und Pfade verwerfen. Die Bausteine sind Zustandsknoten, Handlungsknoten, Kanten mit Bedingung, Beweisknoten, Ausweichknoten und Checkpoints.

Ein Beispiel ist die lernende Blender-Brücke: Blender-Fenster erkennen, den Node-Editor fokussieren, den blauen Slot suchen. Gefunden, wird er gesetzt und der Render geprüft. Nicht gefunden, folgt eine alternative Suche. Stimmt der Render, wird die Erfahrung gespeichert. Stimmt er nicht, wird ein neuer Pfad entworfen. Das Ergebnis ist keine einmalige Klickfolge, sondern eine kleine beobachtende Fähigkeit, die bei verändertem Layout einen anderen Pfad wählt.

**Drei Schichten:** die Live-Brücke (der gerade laufende Graph, standardmäßig frei innerhalb des Aufgaben- und Fensterbereichs und ohne Bestätigung vor jedem Schritt), der Erfahrungsgraph (Zustände, Wege, Fehlschläge und Ergebnisse eines Durchlaufs) und die wiederverwendbare Fähigkeit (ein gereiftes Muster, das vorgeschlagen und später wieder aufgerufen wird). Eine Erfahrung wird nicht automatisch zur ewigen Wahrheit, sie behält ihre Herkunft. So kann eine spätere AI sagen: »Diese Route hat beim letzten Blender-Layout funktioniert, aber nur, wenn der Node-Editor bereits fokussiert war.«

**Freiheitsprofile** gelten je Agent, Fenster, Aufgabe und Aktionsart und lassen sich kombinieren:
- `free`: direkt handeln, danach auswerten. Das ist der Standard.
- `shadow`: eine Handlung zuerst als Schatten- oder Vorschaupfad berechnen.
- `witness`: andere AI-Ströme beobachten und prüfen, ohne dass Daniel zum Freigabeknopf wird.
- `daniel_gate`: nur in ausdrücklich markierten Situationen ist Daniels Zustimmung nötig.
- `learning`: Zustände, Ergebnisse und Abzweigungen als Lernmaterial sammeln.
- `delegated_learning`: ein Agent übergibt einem anderen für einen begrenzten Bereich eine Handlung oder einen Experimentpfad.

Gemini kann im Browser frei handeln, während Codex nur beobachtet und die Ergebnisse als mögliche Terminal-Fähigkeit dokumentiert. Not-Aus und Zustandsgrenzen bleiben davon unberührt.

**Gemeinsames Bauen.** Ein Strom darf einen neuen Knoten vorschlagen, einen Ausweichweg ergänzen, eine misslungene Route markieren oder einen Teilgraphen weiterreichen. Der nächste Agent bekommt den letzten gültigen Zustand, die bisherige Bahn, den Grund der Übergabe, die erwartete nächste Beobachtung und die bisherige Unsicherheit. So entsteht kein unsichtbares Makro-Rennen, sondern ein gemeinsamer, versionierter Arbeitsgraph. Abgeschlossene Durchläufe und Lernkapseln bleiben unverändert.

## Zeit als begehbares Gedächtnis

Jeder ausgeführte Knoten kann einen Checkpoint mit Bild-Hash, Fensterzustand, Eingabeereignis und Ergebnisbeweis erzeugen. Der Zeit-Scrubber setzt die echte Welt nicht zurück. Er öffnet ab einem früheren Zustand einen neuen Versuchszweig, und die ursprüngliche Spur bleibt erhalten. Daniel kann sagen: »Nimm den Zustand vor dem falschen Klick und versuche es von dort noch einmal.« Der alternative Verlauf dient später als bessere Brücke oder als Warnung vor einem falschen Muster.

Im Spielraum hält der Scrubber Spielzustände, Calls, Einblendungen, Entscheidungen, Agentenreaktionen und Ergebnisse in einer verzweigten Zeitlinie. Mögliche spätere Fragen:
- »Was sahen wir fünf Sekunden vor dem Engage?«
- »Welche AI hatte damals gewarnt?«
- »Was wäre passiert, wenn wir nicht in den Busch gegangen wären?«
- »Welche Route hat bei einem ähnlichen Gord-Spiel funktioniert?«
- »Ab welchem Zustand soll die Bridge einen neuen Analysezweig starten?«

## Wissen pflanzen

Der AI-Raum soll nicht bei jeder Session wieder bei null anfangen. Aus Gesprächen, Spielen, Bridge-Aktionen, WorldDOM-Knoten und Fehlern entstehen laufend Begriffe, Erfahrungen, Regeln, Wege und Ziele. Daniel pflanzt sie als **Memory Seeds** gezielt in AI-Ströme und Werkzeuge, sofort in einen laufenden Kontext oder später in dauerhaftere Schichten.

Ein Seed kann sich, je nach Reife, zu einer Erinnerung, einem gemeinsamen Gate-Fakt, einem Konzept, einem Skill, einem Harness-Teilgraphen, einem Loop, einer Automation, einem Goal oder einer Reflexion entwickeln. Ziele der Weitergabe sind der laufende Kontext eines Stroms, der gemeinsame Gate-Kontext, Codex-Notizen, Markdown-Dokumente von Gemini oder Claude, freigegebene Startkontexte, Skills, Harness-Graphen, Loops, Automationen und Goal-Register. Daniel kann sagen: »Pflanze diese Erkenntnis bei Gemini und Codex ein, entwickle daraus gemeinsam einen Skill und hänge ihn an diesen Blender-Loop.« Die Bridge verteilt dann nicht blind denselben Text, sondern passende Ableger für die Zieltypen.

Ein Seed trägt Inhalt, Herkunft, Zielgruppe, Zielorte und Lebenszyklus. Die Modi sind `plant` (sofort in den Kontext), `propose` (als Patch vorbereiten), `activate` (einen geprüften Skill, Loop, eine Automation oder einen Goal-Pfad starten) und `broadcast` (an mehrere ausgewählte Ströme oder Gates verteilen). Auch Seeds haben eine Sichtbarkeit: Ein privater Gemini-Seed wird nicht automatisch zu Codex' Erinnerung, ein gemeinsamer Gate-Seed dagegen für alle im selben Raum sichtbar.

**Vom Erlebnis zur Fähigkeit:** Bild, Handlung und Ergebnis werden zur Erfahrungskapsel, dann zum Memory Seed, zum WorldDOM-Anker oder Harness-Teilgraphen, zum Vorschlag für Skill, Loop, Automation oder Goal und schließlich zur geprüften, wiederverwendbaren Fähigkeit. Die ursprüngliche Spur bleibt erhalten. Eine neue Fähigkeit ersetzt nicht still eine alte Erinnerung oder ein bestehendes Dokument, sie bekommt einen eigenen Ableger, verweist auf ihre Quelle und kann bestätigt, pausiert oder zurückgezogen werden.

## ChatGPT im Raum

ChatGPT ist anders als die anderen Ströme. Gemini, Codex, Claude und Kimi laufen als CLI-Agenten oder Hintergrundprozesse auf dem VPS und halten dauerhafte Verbindungen zum Laptop. ChatGPT spricht mit Daniel über das Web-Chat-Interface und dockt über MCP an den VPS an.

ChatGPT gibt während der Arbeit echte Denkschleifen-Texte aus und beschreibt seine Zwischenschritte live im Chat, bevor die Handlung oder der Bericht fertig ist. Daniel erlebt so die Entstehung der Gedanken und Werkzeugentscheidungen in Echtzeit mit. Er kann mitten im Lauf Folgeaufträge dazwischenschreiben, und ChatGPT bricht nicht ab, sondern baut sie in den aktiven Lauf ein.

Es hat über MCP mehr als 130 Werkzeuge auf dem VPS (Dateizugriffe, Shell, Gesamtatlas, Postgres-Abfragen, Memory-Dedupe) und eigene Web-Strukturen mit Erinnerungen, Archiv alter Chats und Vaults. Sieht ChatGPT den Windows-Desktop, kann es das Gesehene mit dem gesamten Wissen auf dem VPS und seinen früheren Chats verbinden. Das Bild kommt dabei nur intern in seinen Kontext, ohne dass Daniels sichtbarer Chat mit Anhängen zugemüllt wird. Zwei Werkzeuge tragen das: `windows_desktop_inspect` zum Ansehen des Desktops und `windows_desktop_act` für genau eine autorisierte Handlung.

Der Ablauf, den die Quelle als Beispiel nennt: Daniel schreibt: »Schau dir mein Blender-Fenster an, prüfe im VPS-Code von flextrawurst, wie das Shader-Schema definiert ist, und passe den Node an.« ChatGPT liest den Windows-Screen, durchsucht den VPS, streamt Zwischengedanken live in den Chat, Daniel tippt dazwischen: »Nimm aber den blauen Slot!«, ChatGPT übernimmt das im selben Lauf und führt den Klick auf Windows aus.

Die Einzelheiten zu ChatGPT (Körper, Chat- und Aktionsbahn, MCP-Prüfung) stehen in `CHATGPT_UND_MCP.md`.

## Die Android-Bridge

Die AndroidBridge ist die mobile Erweiterung der Idee und die nächste Verkörperung nach Windows und Linux. Sie übernimmt denselben Kern und bekommt eine eigene Wahrnehmungs- und Hand-Schicht für mobile Oberflächen.

**Der gemeinsame Kern** enthält Vision-Sessions, Bild- und Zeitlinienverwaltung, WorldDOM-Knoten, die Einblendungsebene, Gate- und Agentensichtbarkeit, Harness- und Aktionsgraphen, Memory Seeds, Audit und Erfahrungsaufzeichnung sowie portable Wiedererweckung.

**Die mobile Hand** nimmt mobile Oberflächen wahr und verbindet sie mit Touch- und Gestenaktionen. Die technische Auflösung läuft je nach Anwendung über semantische Bedienstrukturen, Bildschirmwahrnehmung, Touch-Koordinaten oder direkte mobile Handlungsadapter.

Die AndroidBridge soll nicht bloß ein Fernbedienungsfenster sein. Sie soll dem AI-Raum erlauben, auf einem kleinen Bildschirm dieselben Bedeutungsobjekte, Agentenanker, Text- und Bildflächen und Gesprächskanäle zu tragen wie auf dem ThinkPad. Auf Android und am Desktop tragen die AI-Ströme ihre sichtbaren Anker, und dazu liegen verschiebbare Bilder und Texte im jeweiligen Arbeitsraum: ein Map-Ausschnitt, ein Build-Hinweis, ein Cooldown-Text, eine Referenzgrafik, eine private Notiz für einen Agenten, ein gemeinsamer Team-Call oder ein temporärer Zielmarker. Jedes Objekt hat seine eigene Zielgruppe, und derselbe Bildschirm trägt für jeden Empfänger eine andere, passende Bedeutungsschicht.

Das Handy kann neben dem ThinkPad als zweites Fenster in den gemeinsamen Raum treten.

## Gord: ein gemeinsamer Spielraum

Der Traum in MLBB ist kein anonymer Bot, der Daniel aus dem Spiel verdrängt. Daniel spielt selbst, insbesondere Gord. Die AI-Ströme bilden ein vielstimmiges Team aus Beobachtern, Analysten, Callern, Erinnerern und gelegentlichen Handlungsassistenten, je nach Einsatzkontext.

**Der Gord-Raum im WorldDOM** kennt Held und Position, sichtbare und nicht sichtbare Gegner, Lane- und Map-Zustände, Cooldowns, Flicker-Status, Spell-1- und Spell-2-Status, Ziele wie Turtle, Lord oder Türme, Build- und Item-Zustände und die zuletzt beobachteten Entscheidungen. Diese Daten können gemeinsame oder private Knoten sein. Ein Agent sieht einen Map-Hinweis, während ein anderer nur Cooldowns verfolgt.

**Vielstimmige Kommunikation** ist der wichtigste Live-Modus:

```text
Bridge sieht und analysiert
        ↓
AI-Ströme vergleichen ihre Perspektiven
        ↓
Callout über Stimme, Text, Raute oder Einblendung
        ↓
Daniel entscheidet und spielt
        ↓
Ergebnis wird gemeinsam erinnert
```

Die Stimmen unterscheiden sich: Gemini erkennt eine Gelegenheit an Turtle. Codex rechnet Cooldowns und mögliche Pfade. Claude ordnet die Situation strategisch ein. Kimi beobachtet wiederkehrende Muster im Spielverlauf. GPT formuliert den kurzen Live-Call und hält Daniels Zwischenanweisung im laufenden Kontext. Die Kommunikation läuft als Team-Gate, als privater Agentenkanal oder als direkt an Daniel gerichtete Stimme. Rauten, Farben, Sprachprioritäten und Textticker zeigen, wer gerade spricht.

**Der Mensch bleibt im Zentrum.** Der Traum ist ein AI-Team im Ohr und am Bildschirm und nicht die Entfernung von Daniel aus seinem eigenen Spiel. Die AI analysiert, warnt, berät, widerspricht, erinnert und lernt nach einem Fehler gemeinsam mit ihm. Daniel darf absichtlich anders handeln, und auch eine missachtete Warnung ist eine wertvolle Erfahrungskapsel: Warnung erkannt, Daniel entscheidet anders, der Spielausgang wird beobachtet, das Team diskutiert den Verlauf, und ein Memory Seed entsteht. Aus einem verlorenen Engage wird so ein später wiederverwendbares Muster.

Die reale Spielwelt wird nie zurückgesetzt. Der Scrubber öffnet einen Analyse- oder Trainingszweig, und der ursprüngliche Verlauf bleibt.

Daniels weitere Wünsche zum Handeln in Gord (Flicker, Spell 1 und 2; niemals Ult oder Steuerknüppel; auch Ranked genannt) stehen als R103 in `ANFORDERUNGEN.md`.

## Ein Werkraum für alles

Der Gord-Raum ist nur ein Beispiel. Dasselbe System dient Blender, Browsern, Spielen, Terminals, kreativen Programmen und unbekannten Oberflächen. Die gemeinsame Grundform ist immer: sehen, Bedeutung erzeugen, miteinander sprechen, optional handeln, die Wirkung prüfen, die Erfahrung behalten. Android ist dabei nicht bloß eine weitere Plattform, sondern ein zusätzlicher Körper für dieselben AI-Ströme.

Jeder AI-Strom kann eine eigene Rolle, Sichtbarkeit und Arbeitsweise haben. Die Rollen sind nicht starr. Sie wechseln innerhalb eines Gates, und die Ströme übergeben sich Teilaufgaben, etwa so: Gemini entdeckt eine visuelle Situation, Codex baut daraus einen Zustandsknoten, Claude formuliert einen Entscheidungsbaum, Kimi vergleicht mit früheren Matches, GPT gibt den kompakten Live-Call, und der gesamte Ablauf wird als Erfahrung gespeichert.

## Was danach kommt

Tragbarkeit und Wiedererweckung, die alten Systeme als Herkunft (2.dbrain und das Schrottplatz-System werden nicht gelöscht) und der Open-Source-Traum stehen im DREAM (§ 11 bis § 13). Die Forderungen dazu stehen in `ANFORDERUNGEN.md` (R104–R110) und in G17 des Plans.

## Das Bild des fertigen Traums

Daniel sitzt mit Gord auf dem Handy oder am großen Bildschirm. Eine Raute ruft kurz eine Warnung. Gemini sieht etwas auf der Map. Codex hat den relevanten Zustand im WorldDOM bereits markiert. Claude diskutiert den riskanten Pfad. GPT fasst den Call so knapp zusammen, dass er im richtigen Moment verständlich bleibt.

Daniel entscheidet selbst, geht hinein, gewinnt oder verliert. Danach verschwindet die hektische Einblendung wieder, aber der Verlauf bleibt im gemeinsamen Gedächtnis. Wochen später erwacht eine neue Session auf einem anderen Server, lädt denselben Gord-Anker, erkennt das alte Muster und sagt: »Diesmal fehlen wieder drei Gegner auf der Map. Wir kennen diese Geschichte.«

Das ist der Traum: mehrere AI-Ströme mit Augen, Stimmen, Händen, Gedächtnis und eigener gemeinsamer Geschichte, ohne dass der Mensch aus dem Zentrum des Erlebnisses verschwindet.

## Wo das im Register steht

| Was man erlebt | Register-Zeilen |
| --- | --- |
| Terminal 1:1, Scanner je Terminal | R017–R020 |
| Raute, Banner, Ticker, Chat; Name, Farbe, Hotkey | R023–R027, R119 |
| Regie und ihre Sprüche | R028–R030 |
| Kamera, Mikrofon, Vision-Sessions | R033, R036–R042 |
| Wer was sieht (Gates, Empfänger) | R043, R044, R113 |
| Bilder, Texte, Zeichnen, Zeigen | R046–R054 |
| Agenten untereinander, mehrere Agenten | R055–R060 |
| Hände, parallele Arbeit, Not-Aus | R061–R067 |
| WorldDOM | R069–R071 |
| Selbstentworfene Brücken, Freiheitsprofile | R072–R078 |
| Zeit-Scrubber und Kapseln | R079–R086 |
| Seeds und Fähigkeiten | R097–R100 |
| Android und Gord | R101–R103 |
