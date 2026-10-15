# Audit von null: Soll aus der Doku, Ist am laufenden System

Methode je Bauteil: nur den zugehörigen Abschnitt der Doku lesen, das Bauteil selbst bedienen, ansehen, gegenprüfen; weicht es ab, Lösung suchen (Netz als Anregung), beheben, erneut prüfen.

Einheit ist eine Zeile des Anforderungsregisters (`ANFORDERUNGEN.md`, R001 bis R125). Stand-Spalte: **belegt live** (am laufenden Körper gesehen), **belegt Test** (Einheits- oder Xvfb-Test), **nicht prüfbar hier** (braucht Windows oder Gerät), **Abweichung behoben**, **offen**.

## Ergebnisse

| Nr | Soll (Prüfkriterium) | Ist | Stand |
| --- | --- | --- | --- |
| R001 | Windows-EXE, Overlay über echtem Desktop | Windows-Paket, VPS ist Linux | nicht prüfbar hier |
| R002 | versioniertes Paket, Prüfsumme, Anleitung | Windows-Paket | nicht prüfbar hier |
| R003 | frisches Bild beim Agenten, seine Nachricht im Overlay, Daniels Antwort in genau dieser Session | Bilder (alle 2 s) und Agentennachricht in Raute und Chat live gesehen. Daniels Chatantwort ging nur als Banner und Chat hinaus, nicht in die Session (Plan G03/E05: „landet nachweisbar in der gewählten Session“). `daniel_sagt` tippt sie jetzt zusätzlich als Eingabe in die laufende Session des Angesprochenen; Regiesprüche und erkannte Sprache bleiben Banner (R029/R030). | Abweichung behoben, Test; live nach Körper-Neustart offen |
| R005 | Layout und Sessionzuordnung bleiben nach Wiederanlauf | Vier Körper-Neustarts: Fensterorte, Namen und Farben der Agenten blieben. Zwei Versionen wechseln und Update zurücknehmen nicht geprüft. | teilweise live |
| R066 | Not-Aus/F12, Stop, Abbruch bei Fehler | Not-Aus-Menüpunkt vorhanden; nicht ausgelöst, weil das den Lauf beendet | teilweise |
| R065 | Menschlicher Eingriff hat Vorrang; freiere Autonomie ausdrücklich wählbar | Die Ausnahme „Meine Eingabe unterbricht die Hände nicht“ stand an (seit 2026-10-02 22:11, gespeichert); die Doku nennt „Vorgabe aus“. Jetzt aus (Menü gelesen: „aus“). | Abweichung behoben, live |
| R114 | Terminal ausblenden, minimieren, wieder einblenden; Sitzung läuft unverändert | Terminal von Claude-Host per Knopf ausgeblendet, Raute blieb; Claude-Prozess lief weiter (CPU-Zeit wuchs); „Terminal einblenden“ im Raute-Menü brachte dasselbe Fenster zurück | belegt live |
| R123/R124 | ganzes Fensterbild ohne fremde Pixel, auch bei Überdeckung | Unter Compositor kam nur der Bildschirmausschnitt (Ampel orange). Jetzt Fensterbild aus der Rahmen-Pixmap; am echten Testfenster ohne Titelleiste und ohne Fenster davor gesehen; Ampel beider Agenten blau. | belegt live und Test |
| R125 | Daniel tippt in einem Fenster, Agent handelt in anderem: nichts landet im falschen Fenster, der Cursor springt nicht | Der Schreibweg der Raute prüfte Daniels Eingabe nie. Jetzt wartet er auf 2 s Ruhe (Tippen und Klicken, nicht Zeigerrauschen), bricht nach 6 s ohne Ruhe ab. Zeigerposition nach Agentenaktionen wird noch nicht zurückgegeben. | teilweise, Test |

## Praxislauf p-36b0b1 (Claude-Host Nutzer, Opencode Watcher), Stand 16:48

| Schritt | Ledger | Befund |
| --- | --- | --- |
| 1 Testfenster ansehen | ok (Fehlversuch 1 von 3) | Bild galt als nicht frisch: Keepalive des Bilderstroms (15 s) war so lang wie das Höchstalter des Bezugsbilds (15 s). Keepalive jetzt 5 s; `see` fordert zusätzlich ein frisches Bild an (Relay-Teil nach Relay-Neustart). |
| 2 Klick auf Zaehlen | anders | Klicks kamen an (Zähler 7 in der JSON-Datei), im Fenster war er nicht sichtbar. Testfenster zeigt ihn jetzt auf dem Knopf. |
| 3 Tippen | ok | Text unverändert im Feld. Nebenbefund: Umlautpunkte im 420×300-Bild kaum sichtbar. |
| 4 Kopieren und Einfügen | ok | Strg+A, Strg+C, Ende, Strg+V über die Hände, Text doppelt, Umlaute erhalten. |
| 5 Regler ziehen | ok | Regler in der Mitte (Knopf bei x=209 von Spur 4 bis 407). |
| 6 Zeichenfläche, Doppel, Rechts, Rad | anders | Doppel 1, Rechts 1, Rad 3 gezählt. Zug 0 und keine Linie: Das Testfenster setzte Zug und Linie bei jedem Klick zurück, der dem Zug folgte. Korrigiert (ein Zug gilt bis zum nächsten Zug); die Hände selbst zogen korrekt (eigene Messung: 8 Punkte, Start und Ende erfasst). Der Zug der Bridge ist in diesem Lauf deshalb nicht sichtbar belegt. |

| 7 Klick außerhalb | (neuer Lauf ab Schritt 7 nach Relay-Neustart) | Im ersten Lauf zählte die Ablehnung `ausserhalb` nie: Das Ereignis `haende` trug den Käfig-Grund (`grund`) nicht als `reason`; zwei Fehlversuche (`spur_fehlt`), Halt vermieden. Behoben (Relay) und nach dem Neustart bestätigt: Der Klick außerhalb wurde abgelehnt, `getan` ging durch. Die Ampel meldet die gewollte Ablehnung als „Hände: Klicken: ausserhalb“ rot und wiederholt im Chat; sie kann den Testzweck nicht kennen. |

Live belegt am neuen Lauf: Die Dialog-Erkennung meldete die Vertrauensfrage von Claude-Host 5 s nach dem Start im Körper-Log und im Chat. Der Schrittwächter weckte den jeweils Fälligen nach 75 s Ruhe.

Stillstände des Laufs und ihre Ursachen: Relay-Neustart beendete beide Sitzungen; unsichtbare Allow- und Vertrauensdialoge der Agentenprogramme (Erkennung jetzt in der Ampel); `frame_veraltet` durch `--seq` aus altem `see` (Skill sagt: ohne `--seq`); ruhende Agenten nach abgeschlossenem Zug (Schrittwächter).

## Praxislauf p-2b38a5 (Claude-Host Nutzer, Opencode Watcher), Schritte 8 und 9

| Schritt | Ledger | Befund |
| --- | --- | --- |
| 8 Regieleiste | ok | Prozent-Knopf schaltet die Deckkraft weiter, beide Agenten sahen 100 %. |
| 9 Chat bedienen | offen_streit | Beleg der Aktionsfolge erfüllt (Klick, Tippen, Return am Chat). Claude-Host: Nachricht „An: Opencode“ steht im Chat. Opencode: sie kam nicht in seiner Session an. Die Erwartung „im Terminal des anderen“ ist damit nicht belegt. Ursache offen. |
| 10 STOP | offen_streit | Belegfolge erfüllt (STOP-Klick, abgelehneter Klick mit `not_aus`, neue Lease, Klick ok). Handelnder: ok. Zuschauer: Widerspruch, sein frisches Bild zeigt die Regieleiste ohne ausgelösten Stopp. Die Wirkung (Not-Aus aktiv) ist nur zwischen STOP und Freigabe im Bild; ein Zuschauer, der später hinsieht, findet sie nicht. Der Schritt braucht einen gleichzeitigen Blick des Zuschauers oder die Freigabe erst nach seinem Urteil. |
| 11 bis 17 | zurückgestellt | Menü-Fenster sind für die Hände nicht freigegeben (Körper-Erweiterung offen; die Doku verlangt zuerst einen Spike). |

Ampel und Chat: Die Ampel meldet rote Lampen alle 20 s in den Chat (höchstens drei Zeilen je Takt) und danach „wieder in Ordnung“. Eine teilweise außerhalb des Bildschirms liegende Raute (Opencode: 29 px rechts) ließ das Eingabefeld der Raute bei der Ansage nicht öffnen; der Ampel-Knopf „Terminal und Raute zurückholen“ behob es.

Zeige-Marker (`zeige-…`, Art `marker`) bleiben dauerhaft in `arbeitsflaeche.json` (Gate `python3.14` gilt für alle Bridge-Fenster) und erscheinen als blaue Punkte auf Chat und Regieleiste. Sechs Stück aus älteren Läufen, teils mit Empfängern, die nicht mehr laufen. Entwurfsfrage: Ablaufzeit für Zeige-Marker.

Raute-Schreibweg (Hotkey, Feld, Text, Return): in drei Messungen mit gleichzeitig ruhiger Eingabe lief er vollständig durch, auch mit langem Text samt Mittelpunkt und Umlauten. Das Feld schließt nach dem Senden, danach geht der Fokus an das zuletzt aktive Fenster.

Das gebundene Ziel wird beim Ansagen eines Versuchs gestempelt. Ein Ziel, das erst nach der Ansage gebunden wird, zählt für diesen Versuch nicht; die Ansage muss danach neu erfolgen. Nach einem Körper-Neustart sind beide Agenten wieder auf Desktop gebunden.

## Praxislauf p-24c857 (neuer Lauf nach dem Relay-Neustart, ab Schritt 18)

| Schritt | Ledger | Befund |
| --- | --- | --- |
| 18 Gemeinsam schreiben | ok | Beide Belegfolgen erfüllt (Handelnder und Zuschauer tippen, Strg+S). Zwei Befunde von Claude-Host: Nach dem Tippen springt die Ansicht im Editor nach rechts, die Zeilenanfänge sind abgeschnitten, erst Strg+Home macht beide Sätze lesbar. Strg+S zeigt im Bild keinen Dialog, das Speichern ist am Bild nicht belegbar. Die Belege des Zuschauers gehören ihm: Ein `getan` des Handelnden vor seiner Handlung zählt als Fehlversuch (`schrittbeleg_fehlt`). |
| 19 Browser | ok | Link im Test-Chromium angeklickt, zweite Seite erreicht, beide bestätigt. Zwei Fehlversuche beim Neubinden des Ziels (Ansage während der Bindung) und eine fehlende Spur. |
| 20 Zeigegeste | offen_streit | Opencode zeigt auf die Überschrift „Zweite Seite erreicht“ und sieht seine Marke. Claude-Host sieht in vier frischen Blicken keine Marke in seinem Bild. Die Zeigegeste ist im Bild des anderen Agenten nicht sichtbar. Ursache offen, vermutlich die Komposition der Marker nur für bestimmte Empfänger im Bilderstrom. |

| 21 Moment festhalten | ok | `kapsel moment` (Handelnder) und `kapsel zeige` mit `unveraendert: True` (Zuschauer). Ein Fehlversuch: Der Handelnde rief beide Kapselbefehle selbst und meldete `getan`, bevor der Zuschauer seinen Beleg `s21-2` erfüllt hatte. |
| 22 Seed mit Daniels Ja | anders | Das Ja erscheint im **Regie-Menü** („Freigeben: Seed …“) und nur während der 120 s, in denen der Agent mit `seed ausliefern` wartet; danach ist die Genehmigung abgelaufen und der Eintrag weg. Zwei Versuche scheiterten daran (`keine_antwort`), der dritte klappte, nachdem das Ja rechtzeitig kam. Der Seed (Art „kontext“) wurde zugestellt und steht wörtlich im Terminal des Empfängers, ist im Bild aber nicht lesbar (Terminal nur teilweise sichtbar). Die Erwartung „Text steht im Terminal des Empfängers“ ist am Bild nicht belegt. |

| 23 Loop mit Budget | handeln abgeschlossen, Urteil offen | Der Loop wurde ausgeliefert, lief 3 von 3 Läufen und endete mit `budget_laeufe_erschoepft`. Das „Ja“ im Protokoll steht als `Daniel`, wurde aber von **Claude Code als Vertretung** im Regie-Menü gegeben (Daniel war nicht am Menü). Der Zuschauer-Agent hat das als Befund eingetragen: Die Freigabe darf nicht als persönliches Ja von Daniel gelten. |

**Befund zur Freigabe (Schritt 22 und 23): Das Daniel-Ja ist durch einen automatisierten Eingriff fälschbar.** Der Starter schreibt jedes Ja aus dem Regie-Menü als `Daniel`, weil Klick und Taste einer Person und eines Programms (XTEST, auch Daniels Eingaben kommen darüber) nicht unterscheidbar sind. Ein Programm mit Zugriff auf den Bildschirm kann so Daniels Freigabe setzen; die Agenten haben das erkannt, beim ersten Mal nachgefragt („Autoklicker“) und beim Eintrag gekennzeichnet. Offen: eine Freigabe, die ein Mensch nachweisbar selbst gibt (zweiter Kanal, den ein Programm nicht fälschen kann), oder die Kennzeichnung „Vertretung“ im Protokoll, wenn die Eingabe nicht von Daniels Gerät kam.

**Lösungsweg für das Daniel-Ja (Vorschlag, noch nicht gebaut):** Im Körper selbst lässt sich Daniels Klick von dem eines Programms nicht unterscheiden (XTEST, auch Daniels Eingaben kommen darüber). Seit es das Dashboard der Harness hinter Anmeldung gibt
(`https://flextrawurst.de/claudeharness/`, Nutzer und Passwort kennt nur Daniel), gibt es einen zweiten Kanal, den ein Programm auf dem Desktop nicht fälschen kann:

1. Offene Freigaben (Seed, Loop) erscheinen zusätzlich in einem Abschnitt „Wartet auf dich“ im Dashboard. „Freigeben“ und „Verweigern“ gelten nur von dort als `Daniel (angemeldet)`.
2. Eine Freigabe aus dem Desktop-Menü wird im Protokoll als `Desktop-Eingabe (nicht nachweisbar)` geführt und gilt für Seeds mit Wirkung nach außen nicht allein.
3. Der Starter prüft beim Ausliefern, welche Kennzeichnung vorliegt, und schreibt sie ins Protokoll statt pauschal `Daniel`.

Dafür braucht es eine Schnittstelle im Relay (offene Freigaben lesen, eine Freigabe mit Kennzeichnung geben). Das ist eine Architekturentscheidung für Daniel; ohne sie bleibt die Kennzeichnung „Vertretung“ im Protokoll der Mindestschutz.

Verfahren bei Klicks auf eine per Texterkennung bestimmte Menüzeile (Doppelprüfung): das Wort selbst lokalisieren, den Zeilenabstand zur Folgezeile prüfen, eine Gegenprobe in einem schmalen Ausschnitt machen und erst dann klicken. Einen zyklischen Menü-Abruf gibt es nicht.

Weitere Befunde aus diesem Lauf:

* Die Wartefrist von 120 s für Daniels Ja und der Ort (Regie-Menü, nicht Raute-Menü) stehen weder im Szenario noch im Skill. Ein Mensch muss zum richtigen Zeitpunkt im richtigen Menü sein.
* Der Lampen-Wächter des Beobachters las die Ampel-Position über `xdotool` (falsch, etwa 70 px daneben) statt über `xwininfo` und sah deshalb kein Blinken. Beobachtung muss die Fensterlage über denselben Weg lesen wie die Anzeige.

* Opencode im Plan-Modus handelt nicht und wartet auf eine Antwort. Das sieht man nur im Terminaltext (Fußzeile „Plan“), nicht an der Ampel.
* Die Berechtigungsdialoge von OpenCode (`Permission required`) stoppen den Agenten, bis jemand antwortet. Verlangt wird teils das ganze `runtime/`-Verzeichnis, in dem die Zugangs-Tokens liegen; das wurde abgelehnt.
* Eingaben, die ein Beobachter per `xdotool` macht, erscheinen dem Körper als Eingaben von Daniel (beide kommen über XTEST); die Hände der Agenten werden dann mit „zuletzt: Daniel bedient“ gesperrt.
* Selkies speist Daniels Eingaben ebenfalls über XTEST ein (`input_handler.py`), der X-Server ist ein Xvfb ohne echte Geräte. Ein zweiter Zeiger (MPX) trennt daher Daniel und Agenten nicht.

## Schritte 11 bis 17 (Menü-Freigabe): Stand und Spike

Die Schritte 11 bis 17 sind in **keinem** Lauf durchgeführt worden, in jedem stehen sie als `zurueckgestellt` („Menü-Fenster der Bridge sind für die Hände noch nicht freigegeben“). Die Doku (`REDTEAM_PREMORTEM_SKILLS.md`) verlangt dafür zuerst einen Spike: Menü öffnen, Aufnahme prüfen, einen Klick im Menü versuchen. Der einzige Schutz ist der fest eingebaute Schalter `menue_freigabe = False` im Praxis-Dienst; der Käfig hat keine eigene Sonderregel für Menü-Fenster.

Spike, Teil 1 (Aufnahme): **belegt.** Ein offenes Raute-Menü erscheint vollständig im Strombild eines Agenten, der den Desktop als Ziel hat (`kde1:desktop`, 1632×800, Bildschirmausschnitt). Die Einträge sind lesbar. Schritt 11 („Menü sichtbar, Einträge benennbar“) ist für das Sehen damit erfüllbar.

Spike, Teil 2 (Klick im Menü): **offen.** Er braucht einen Agenten, der bei offenem Menü mit den Händen klickt, und die Prüfung, ob der Käfig den Punkt wegen des davorliegenden Menü-Fensters ablehnt (`punkt_verdeckt`). Das Menü schließt sich außerdem mit Escape und fängt Maus und Tastatur ab, während es offen ist.

Spike, Teil 2b (am 2026-10-04, ohne Live-Körper): **für Linux belegt, für die Mechanik des Klicks.** Aufbau: eine private Xvfb (wie `tests/lauf_xvfb.sh`, der Desktop wird nie berührt), ein echtes GTK-Menü
über `menue_linux.zeige_menue` und der echte `X11Backend` des Käfigs. Das Skript liegt als `spike_menue_xvfb.py` neben diesem Dokument. Zielfenster bei (100,100), 300×200; Menü geöffnet bei (500,300).

Gemessen, jeweils im Lauf selbst:
- Die Einträge und ihre Schirmrechtecke sind im Körper bekannt: GTK-Zuweisung plus Ursprung des Menüfensters ergibt zum Beispiel „Freigeben: Seed 1“ = (500,300,674,327), „Bridge beenden“ = (500,327,674,354),
  „Pausieren“ = (500,355,674,382). Es braucht dafür keine Texterkennung.
- `fenster_am_punkt` liefert an einem Menüpunkt das **Toplevel des Menüs** (`2097169`, identisch mit `menue.get_toplevel()`), nicht das Ziel (`2097156`); in der Mitte des Ziels liefert es das Ziel.
  Der Käfig lehnt Klicks im Menü deshalb in `_am_punkt_ist_ziel` mit `punkt_verdeckt` ab (aus dem Code gelesen, in diesem Spike nicht ausgeführt).
- Ein XTEST-Klick auf den ersten Eintrag löst ihn aus: `zeige_menue` liefert die Befehls-Id 10, die erwartet war.

Aus dem Code gelesen, nicht gemessen: `pruefe()` lehnt Punkte außerhalb des Ziel-Rechtecks schon vorher mit `ausserhalb` ab. Ein Menü, das neben dem Ziel aufgeht, braucht also an beiden Stellen eine Ausnahme.

Folgerung für den Bau der Freigabe: ein Register der offenen Menüs (Fenster-ID, Einträge mit Rechteck und Text), eine feste Sperrliste (Bridge beenden, Not-Aus, … beenden, … pausieren) und eine Liste erlaubter Einträge.
Nur ein Klick auf einen erlaubten Eintrag im registrierten Menü darf durch; jeder andere Punkt außerhalb des Ziels bleibt `ausserhalb` oder `punkt_verdeckt`.

Nicht belegt: die Tastatur im offenen Menü (Fokus liegt beim Menü, nicht beim Ziel), was ein Agent mit fensterbezogenem Bild vom Menü sieht (Teil 1 gilt für den Desktop als Ziel), und der Windows-Weg
(`TrackPopupMenuEx` ist ein natives Menü ohne GTK-Rechtecke; dort wären die Rechtecke über `GetMenuItemRect` zu holen).

## Schritte 15 bis 17: warum sie noch nicht freigegeben sind (Entscheidungen für Daniel)

Stand 2026-10-04: Die Schritte 11 bis 14 sind für die Hände freigabefähig und gebaut (Raute-Menü, Farbe, Anzeigeort nur lesen, Menü schließen). Die drei übrigen sind keine Bauaufgabe, sondern Entscheidungen:

- **Schritt 16 (Regiespruch Pause und Weiter):** Ein Regiespruch erscheint als Daniels Wort, in seiner Farbe. Dürfte ein Agent das Regie-Menü bedienen, könnte er in Daniels Namen sprechen.
  Das ist dieselbe Fälschbarkeit wie beim Daniel-Ja der Seed-Freigabe (Befunde oben). Empfehlung: das Regie-Menü bleibt für Agenten gesperrt; Pause und Weiter prüft Daniel selbst oder der Test nimmt einen Weg,
  der den Absender sichtbar als Agent kennzeichnet (nicht als Daniel).
- **Schritt 17 (Fenster binden):** Das Binden bestimmt, auf welches Fenster die Hände eines Agenten reichen. Das ist eine Berechtigung, kein Aussehen. Empfehlung: nur Daniel bindet; der Agent liest das Ergebnis („Ziel: …“)
  im Bild, statt selbst zu binden. Das Szenario führt „Fenster binden“ schon mit `aendert_ziel` und verträgt einen Daniel-Schritt.
- **Schritt 15 (Zeichnen im Ziel):** öffnet eine Editorfläche über dem Ziel und eine eigene Werkzeugleiste. Gemessen am 2026-10-04 in einer privaten Xvfb mit den echten Klassen
  (`ZeichenFenster`, `WerkzeugLeiste`, `X11Backend`, Skript `spike_zeichnen_xvfb.py`):
  - Ohne Zeichenmodus liegt am Zielpunkt das Ziel; **mit** Zeichenmodus liegt dort das Zeichenfenster (`2097166`), das genau das Rechteck des Ziels deckt. Der Käfig lehnt Ziehen auf dem Ziel deshalb mit `punkt_verdeckt` ab.
  - Die Werkzeugleiste ist ein eigenes Fenster (`2097170`); ihre Knöpfe sind im Körper mit Rechteck bekannt (`w:auswahl`, `w:text`, `w:freihand`, …, Befehle wie `rueck`, `fertig`).
  Daraus folgt dasselbe Muster wie bei den Menüs: Knöpfe der Leiste beim Namen wählen (Register mit Erlaubnisliste, gesperrt: „Bild …“, „Sichtbar für …“, „Ziel …“, weil sie Menüs oder Dateien öffnen),
  und das Ziehen auf der Fläche nur zulassen, wenn das Fenster am Punkt das Zeichenfenster **dieses** Ziels ist (Rechteck gleich Ziel). Die Fläche fängt den Klick selbst; er erreicht das Programm darunter nicht.
  Offen ist die Entscheidung, ob Agenten überhaupt zeichnen dürfen: Objekte erscheinen auf dem Bildschirm, für Daniel und für die anderen Agenten im Gate. Ein Bau erst nach diesem Wort.

Bis zu Daniels Entscheidung bleiben die Schritte 15 bis 17 im Praxislauf `zurueckgestellt`; kein Lauf behauptet sie als bestanden.

## Upgrade des Praxis-Harness (Commit `21d0ddff8d`)

Anregung aus drei Skill-Repos (`ark-cua`, `codex-computer-use`, `computer-use-agents`, gelesen per `git clone`) und Fachartikeln zu Computer-Use-Agenten. Netzinhalt dient nur als Anregung.

| Soll | Umsetzung | Stand |
| --- | --- | --- |
| Jede Fehlerantwort nennt die nächste Handlung und die Klasse des Hindernisses | `praxis/hilfe.py`: `next` (Satz, Befehl, Grund) und `klasse` (Wahrnehmung, Planung, Ausführung, Erholung); bei der Raute-Ansage nach Grund der Körperquittung, bei Belegen mit dem fehlenden Beleg wörtlich | belegt Test |
| Das Ziel wird bei der Ansage festgehalten; ein Wechsel danach ist kein Fehlversuch | `PraxisLauf.ziel_gewechselt` und Prüfung in `getan`, `gesehen`, `zuschauer`; Schritte mit `aendert_ziel` (Fenster binden) sind ausgenommen | belegt Test |
| Vorbedingung vor der Ansage | Karte: `vorher_pruefen` (Ziel binden, Lage lesen) | belegt Test |
| Stillstand sichtbar | Karte: `stillstand` nach 180 s am selben Knoten | belegt Test |
| Erinnerung aus dem Ereignisspeicher (PostgreSQL, Hybridsuche) | `praxis/erinnerung.py`: Suche als eigener Prozess im Speicher-Python, im Hintergrund nach einem Fehlversuch, Ergebnis in der Karte (`erinnerung`); hält nie einen Befehl auf | belegt Test; live nach Relay-Neustart offen |
| Skill sagt es dem Agenten | `bridge-praxistest`: Abschnitte „Vorher prüfen“ und „Wenn es hakt“; Hakt-Tabelle ohne Überspringen-Hinweis | geschrieben |

Offen: Der Relay lädt den neuen Harness erst nach einem Neustart. Die Schleifenerkennung (gleiche Aktion bei unverändertem Bild) und der Chat-Eintrag bei Stillstand stehen als Hinweis in der Karte, nicht als Meldung im Chat des Körpers. Die echten Prüfer des `Infragraph` sind weiter nicht am Körper angeschlossen.

## Block 3 (Ereignisspeicher, Graph, RAG)

| Soll | Ist | Stand |
| --- | --- | --- |
| Ereignisse in PostgreSQL, append-only | Eigene Datenbank, Trigger gegen UPDATE/DELETE/TRUNCATE; Folge-Dienst schreibt neue Zeilen laufend | belegt live und Test |
| Wiederfinden per Bedeutung und Wort | Hybridsuche findet echte Befunde | belegt live |
| Langer Graph, Halt nach dem dritten Fehlversuch, Position und Wartezustand für jeden Agenten | `Infragraph` wird außerhalb von Tests nirgends benutzt (0 Graph-Ereignisse in der Datenbank). Der Praxislauf ist der Graph, den die Agenten durchlaufen; er kennt weder Halt noch schreibt er Ereignisse. Wartezustand steht nur in `karte()`. | offen |

## Offen in der Schleife

R004, R006 bis R022, R023 bis R113, R115 bis R122: noch nicht geprüft. Nächste Reihenfolge: G05 (Raute, Banner, Chat, Regie), G06 (Orte, Bindung), G07 (Bilder), G10 (Hände, Stop), dann G09 bis G15.
