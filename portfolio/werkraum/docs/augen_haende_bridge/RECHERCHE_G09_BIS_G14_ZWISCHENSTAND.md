# Netzrecherche zu Controller, Verlauf/Zeitreise, Modellserver, Bildgrundierung (2026-10-02)

Netzinhalte sind Anregung, keine Wahrheit; was unabhängig bestätigt ist, steht als „bestätigt“. Alles andere ist Hinweis zum Prüfen.

## 1. Virtuelle Controller unter Linux (uinput)
- Hinweis (mehrere Quellen, u. a. ArchWiki und Issue-Berichte): Erkennt SDL oder Steam die Identität eines virtuellen Geräts nicht, erzeugt SDL ein Standardlayout aus der Reihenfolge der Tastencodes, und Knöpfe landen falsch (z. B. X und Y vertauscht).
  Gegenmittel: echte Xbox-Kennung (Microsoft, Vendor 0x045E, Produkt 0x028E) mit xpad-typischen Codes. Unser `UinputBackend` nutzt genau diese Kennung, Steuerkreuz als Hut-Achse, Trigger 0 bis 255. Ob SDL das Gerät mit richtigem Layout erkennt, ist **nicht** geprüft (kein SDL-Test) — Prüfpunkt für Daniel mit einem echten Spiel.
- Hinweis: Zugriff auf /dev/uinput braucht Rechte (udev-Regeln); der Zugriff gilt als sicherheitsrelevant (Issue im Valve-Repo). Wir erkennen „nicht beschreibbar“ als Grund und ändern keine Rechte.
- Hinweis: Mit `SDL_GAMECONTROLLER_IGNORE_DEVICES` lassen sich echte Controller ausblenden, damit ein Spiel nur das virtuelle sieht.

## 2. Virtuelle Controller unter Windows
- Bestätigt (mehrere Quellen): ViGEmBus ist seit 2023-11 archiviert, läuft aber weiter; ein Nachfolger heißt VirtualPad.
- Hinweis (nur Eigenaussagen der Projekte): Treiberfreie Wege im Benutzermodus — HIDMaestro, LizardByte libvirtualhid mit „Virtual HID Driver“, VIIPER (USBIP). Vorteil, wenn bestätigt: keine Kernel-Treiber-Installation. Das wäre eine **Entscheidung für Daniel** (anderer Weg als der freigegebene ViGEm-Treiber); nichts davon wird ohne sein Wort eingebaut.
- Zusatz: HidHide blendet physische Controller aus, damit nur das virtuelle gesehen wird.

## 3. Verlauf, Zeitreise, Zweige (G12/G13)
- Bestätigt über mehrere Quellen (LangGraph u. a.): Zweig aus einem Checkpoint ohne Veränderung des Originals ist das gängige Muster; Zufall (Temperatur) für Wiedergabe niedrig halten; Zustand flach und klar benennen; Wiedergabe mit aufgezeichneten Antworten ohne Modellkosten („Stubs“).
- Wir haben das: Zweig aus Checkpoint (Original bleibt), Spur wiedergeben ohne Ausführung, Kapsel unveränderlich. Lücke: Wiedergabe einer Kapsel mit aufgezeichneten Modellantworten gibt es nicht.

## 4. Modellserver (G14)
- Bestätigt (llama.cpp-Doku und mehrere Berichte): Übersteigt der Prompt die Kontextgröße, antwortet der llama.cpp-Server mit HTTP 400 samt `n_prompt_tokens` und `n_ctx`; Ollama dagegen kürzt still. Mit aktiviertem Kontext-Shift verwirft llama.cpp die ältesten Tokens still.
- Folge für uns: Unser Client meldet bei HTTP 400 derzeit „modell_nicht_erreichbar“ — das ist irreführend. Besser: „kontext_zu_gross“ mit beiden Zahlen. Und: der Server kann bei aktivem Kontext-Shift kürzen, ohne es zu melden; unsere Anzeige „Serverkürzung vermutet“ (Vergleich Schätzung/Messung) ist dafür richtig, aber keine Garantie.
- Zu bauen (Quelldatei, erst nach den laufenden Gates): HTTP-400-Antwort auswerten und im Chat und bei „jetzt“ als eigenen Grund mit Zahlen zeigen.

## 5. Bildgrundierung und WorldDOM (G11)
- Bestätigt über Forschungsarbeiten (OmniParser, Set-of-Mark, Windows Agent Arena): Elemente mit Kennung statt rohen Pixelkoordinaten verbessern die Treffsicherheit; Bedienungshilfen-Baum plus Bild plus Texterkennung gemeinsam sind der robuste Weg. Das ist unsere Architektur (Knoten mit Herkunft, relative Lage in Profilen).
- Lücke: Ein „Set-of-Mark“-Bild (Knotenkennungen als Nummern im Bild an den Agenten) gibt es nicht. Vorschlag zum gemeinsamen Entscheiden: ein Befehl `weltdom --markiert`, der ein Bild mit Nummern an den Knoten sendet.

---
# Erweiterung: G01 bis G18 (2026-10-02)
Der Plan führt G01 bis G18 (G06.5 und G06.7 dazwischen); G19 bis G21 gibt es nicht. Wieder gilt: Netzinhalt ist Anregung, nicht Wahrheit.

## G01/G02 Paket und Start
- Bestätigt (mehrere Quellen): `--onedir` löst weniger Virenmeldungen aus als `--onefile`; die größte Wirkung hat eine Code-Signatur. Eine Signatur entfernt „Unbekannter Herausgeber“, SmartScreen warnt aber weiter, bis der Herausgeber Reputation gesammelt hat. Wir liefern onedir und unsigniert, das steht ehrlich in der Startanleitung.
- Hinweis: Den PyInstaller-Bootloader selbst zu bauen verringert Treffer, weil der vorkompilierte Bootloader den Virenherstellern bekannt ist. Prüfpunkt, kein Auftrag. Zur Reproduzierbarkeit unter Wine fanden die Quellen nichts.

## G04/G05 Terminal
- Hinweis (Fehlerberichte zu ConPTY): Seit ConPTY 1.22 zeichnet es nach einer Größenänderung nicht mehr neu und erwartet, dass das Terminal genauso umbricht wie ConPTY; weicht der Umbruch ab, laufen die Bilder auseinander. Außerdem: Größenänderung nach dem Schließen nutzt ein freigegebenes Handle; über Lesegrenzen zerrissene UTF-8-Zeichen gehen verloren.
- Zu prüfen bei uns: Zerreißen wir Mehrbyte-Zeichen an Lesegrenzen (Terminal läuft über das Relay in Stücken)? Ein Test mit einem „ä“ genau an der Stückgrenze fehlt. Prüfpunkt, noch nicht geprüft.

## G06/G06.7/G08 Anzeige und Bild
- Bestätigt: Windows.Graphics.Capture erfasst verdeckte Fenster samt DWM-Rahmen; PrintWindow verpasst, was der DWM zeichnet (Rahmen, Titelleiste, Mica/Acryl) und zeigt Direct2D-Kinder oft nur bei aktivem, frisch gezeichnetem Fenster. DXGI Desktop Duplication ist schnell, erfasst aber den Bildschirm, nicht ein einzelnes Fenster.
- Folge: Windows.Graphics.Capture steht schon auf der Bauliste (R2, nativ prüfbar); PrintWindow bleibt Rückfall. DPI: echte Pixel nur mit pro-Monitor-DPI-bewusstem Prozess lesen — bei uns ist die Geometrie-Prüfung schon im Hände-Käfig.

## G09 Mehr-Agenten
- Bestätigt (mehrere Quellen): Gängige Bausteine sind ein dauerhafter Briefkasten mit Reihenfolge je Empfänger („FIFO“) und abgesicherten Terminal-Hinweisen, gemeinsame Aufgabenliste mit Abhängigkeiten, Dateisperren und Git-Worktrees je Agent gegen Kollisionen. Claude ist beim Parallelisieren von sich aus zurückhaltend.
- Wir haben: Nachrichten und Aufträge mit Status, Gruppen, Zustellung ins Terminal. Lücken: Reihenfolge-Garantie je Empfänger ist nicht ausdrücklich getestet; Dateisperren/Worktrees sind nicht Sache der Bridge (die Agenten arbeiten selbst im Repo) — Entscheidung für Daniel, ob die Bridge dort etwas anbieten soll.

## G10 Hände
- Bestätigt (Old New Thing, Foren): Tastatureingabe lässt sich nicht verlässlich mit PostMessage nachbilden; PostMessage läuft ohne Fokus, aktualisiert aber den globalen Tastenzustand nicht und wird von DirectX/RawInput/Qt oft ignoriert. SendInput braucht Fokus und trägt die Kennzeichnung „injiziert“; UIPI sperrt Eingabe an Programme mit höheren Rechten.
- Wir nutzen SendInput mit Fokus (AttachThreadInput) und erkennen eigene injizierte Ereignisse für Daniels Übernahme. Grenze: Spiele mit Anti-Cheat können injizierte Eingaben blockieren; wir umgehen das **nicht** (kein Auftrag, und nicht unser Ziel). Controller über ein virtuelles Gerät ist dort der vorgesehene Weg.

## G15 Aus Erfahrung wird Wissen und Handeln
- Bestätigt (mehrere neue Arbeiten): Ein Skill ist eine Ordnerstruktur um SKILL.md mit Skripten und Referenzen; „Procedural Memory“ (Voyager, Agent Workflow Memory) legt wiederkehrende Abläufe als wiederverwendbare Fähigkeit ab und verfeinert sie durch Rückmeldung. Warnung aus der Literatur: Abläufe können bei Veränderung der Oberfläche altern („Reuse and Interference“) — Prüfen vor Wiederverwendung ist Pflicht.
- Wir haben die Grundlage (versionierte Abläufe, Lernen nur von Daniel eingeschaltet, nie aus Simuliertem, Kapseln mit Lernstrecken). Offen: Auswahl und Verfeinerung gespeicherter Abläufe nach Rückmeldung; Altern erkennen (Vergleich der Knoten beim Start).

## G16 Android
- Bestätigt (Android-Dokumentation und Berichte): `dispatchGesture` mit `canPerformGestures` kann Tippen, Wischen, Zwei-Finger-Gesten ausführen. MediaProjection braucht einen Vordergrunddienst vom Typ mediaProjection und ein Nutzerfenster; seit Android 14 muss der Dienst vor dem Projektionsobjekt starten.
- Wichtige Hürde: Seit Android 13 sperren „Eingeschränkte Einstellungen“ die Bedienungshilfen für nachinstallierte Apps (Weg über Einstellungen → App-Info → eingeschränkte Einstellungen zulassen); bei aktivem „Erweitertem Schutz“ wird der Zugriff weiter eingeschränkt, nach Berichten stärker in neuen Android-Versionen. Eine Bridge-App muss damit rechnen, dass der Nutzer die Freigabe von Hand erteilen muss und dass sie je nach Version nicht erteilt werden kann.

## G17 Wiedererweckung, Sparbetrieb, Paket
- Siehe G01/G02 zu Signatur und Virenmeldungen. Für Sparbetrieb: Whisper ist nicht dauernd nötig; VAD vor der Erkennung spart Rechenzeit.

## Mikrofon (zurückgestellt, aber nützlich für später)
- Bestätigt: Aufnahme, Spracherkennung, Erkennung und Oberfläche gehören in getrennte Warteschlangen/Threads, damit Inferenz die Aufnahme nicht blockiert; ein VAD (z. B. Silero) vor Whisper spart Zeit und senkt Latenz (0,5 bis 2 s hinter der Sprache). Zu Windows-Gerätekonfiguration (WASAPI) fanden die Quellen nichts: dort bleibt unser eigener Befund (alle Geräte am Testrechner liefern Stille) offen.

## Gesamtliste: Was daraus ein Bauauftrag werden kann (nur mit Daniels Wort)
1. HTTP-400 des Modellservers als „Kontext zu groß“ mit Zahlen (klein, Quellcode, eindeutig sinnvoll).
2. Test: Mehrbyte-Zeichen an Terminal-Stückgrenzen.
3. Set-of-Mark-Bild für WorldDOM.
4. Altern von Abläufen erkennen (Knotenvergleich vor dem Start).
5. Reihenfolge-Test je Empfänger bei Nachrichten.
6. Wiedergabe einer Kapsel mit aufgezeichneten Modellantworten.
7. Entscheidungen für Daniel: treiberfreie Controller-Wege unter Windows; Signatur oder eigener Bootloader; Dateisperren/Worktrees für Agenten.
