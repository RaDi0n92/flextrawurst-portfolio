---
autor: codex bei Daniels VPS
datum: 2026-09-19
inhalt: Daniels Anforderungen; Quellenzuordnung und Abnahmekriterien von Codex
status: Planungsbaseline, keine Produktabnahme
---

# Augen & Hände — alles, was die Bridge können muss

## Wozu dieses Register dient

Daniel hat den Umfang bereits beschrieben. Dieses Register verlangt keine neue Wunschliste. Es ordnet die vorhandenen Produktanforderungen einem verantwortlichen Goal und einem überprüfbaren Ergebnis zu. Jede Zeile ist eine Verpflichtung im Gesamtplan, nicht die Behauptung, sie sei implementiert. Die zusammengehörige Rückwärtsplanung steht unter `/root/werkraum/docs/augen_haende_bridge/BRUECKE_VOM_ENDZIEL_RUECKWAERTS_ZUM_START.md`.

Das aktuelle Gespräch ergänzt: vom letzten Goal rückwärts planen; alle beschriebenen Funktionen sollen menschlich verständlich, zusammenhängend, sauber geordnet und wirklich bedienbar sein. Keine Verkleinerung auf eine EXE-Demo. Android bleibt die von Daniel als später beschriebene Erweiterung, aber im Gesamtumfang. Öffentliche Veröffentlichung und tatsächliche VPS-Migration bleiben gesondert auszulösende Außenaktionen.

Die IDs dienen der Nachverfolgung, nicht als UI-Beschriftungen. Menschenlesbare Titel bleiben maßgeblich. Alle Anforderungen sind bei Erstellung **offen hinsichtlich der Gesamtproduktabnahme**; historische Teilbeweise werden nicht automatisch übernommen.

## Quellen und Leseregel

| Kürzel | Vollständiger Pfad / Herkunft |
| --- | --- |
| U / A | `/root/werkraum/docs/augen_haende_bridge/2026-09-18_19_CODEX_GESAMTSESSION_WORTLAUT.jsonl` — U bezeichnet User-, A Assistant-Nachrichten nach `ordinal` |
| ASTRA | `/root/werkraum/docs/augen_haende_bridge/2026-09-19_ASTRA-LUNA_PLANUNG_WORTLAUT.md` — enger Planungsabschnitt, besonders 548–569 |
| V76 | `/root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md` — Gemini-Ursprung plus Erweiterungen |
| V77 | `/root/werkraum/docs/systemdoku/77_worlddom_memory_seeds_wiedererweckung.md` |
| B78 | `/root/werkraum/docs/systemdoku/78_augen_und_haende_bauplan.md` — ältere Etappen, kein neuer Abschlussbeweis |
| LUNA | `/root/werkraum/docs/augen_haende_bridge/2026-09-19_LUNA-MAX_PLANUNG_MOMENTKAPSELN_HAUHAUCS_OVERLAY.md` — abgeleitete Planung |
| DREAM | `/root/werkraum/docs/vision/augen_und_haende_androidbridge_mlbb_dream.md` |
| PRÜFUNG | `/root/werkraum/docs/augen_haende_bridge/2026-09-19_BRUECKE_BAUSTART_PRUEFUNG_UND_VEREINBARUNG.md` |
| SKIZZE | `/vps_root/werkraum_bilder/refferenzen/h a bridge.jpg` — angesehen; Daniels Erklärung U443 korrigiert die Leserichtung |
| JETZT | Laufendes Gespräch nach dem archivierten Ausschnitt: vollständiger Umfang, Endziel zuerst, Bedienbarkeit als Abnahme |

Vorrang: spätere ausdrückliche Daniel-Korrektur vor früherem Entwurf. Assistant-Vorschläge sind als solche zu lesen, soweit Daniel sie nicht übernommen hat. Technische Abnahmedetails in diesem Register sind Operationalisierungen von Codex, keine wörtlichen Daniel-Zitate. Die Quellen wurden thematisch und gegen die vollständige User-Nachrichtenliste des vorhandenen Exports geprüft. Dies ist kein neuer wortgetreuer Export aller Assistant-/Toolnachrichten; der vorhandene Archivumfang bleibt unverändert.

## 1. Programm, Lieferung und Arbeiten ohne Babysitten

| ID | Verbindliches Ergebnis | Quelle | Goal | Fertigbeleg |
| --- | --- | --- | --- | --- |
| R001 | Echtes Windows-Programm/EXE; Overlay über dem tatsächlichen Desktop, keine Homepage | U513,529,532 | G02 | Paket startet ohne Entwicklungsinstallation; native Aufnahme zeigt echte Programme darunter |
| R002 | Vollständiges versioniertes Paket statt Buildanleitung für Daniel | U540,546; ASTRA551 | G02 | Downloadbestandteile, Prüfsumme, Starttest und verständliche Anleitung stimmen überein |
| R003 | Wirklicher Erstkontakt zur bestehenden Agentensession | U540,546; ASTRA551 | G03 | frisches Bild beim Agenten, seine Nachricht im Overlay, Daniels Antwort in genau dieser Session |
| R004 | Agent sieht und benutzt die Bridge während ihrer Weiterentwicklung | U470,472,536 | G03 | nachgewiesene Inspektion und Bedienung der laufenden Version, später bei jeder UI-Etappe |
| R005 | Update, Wiederanlauf und Rückkehr ohne verlorene Einstellungen | ASTRA553,555; JETZT | G03 | zwei Versionen wechseln; fehlerhaftes Update zurücknehmen; Layout und Sessionzuordnung erhalten |
| R006 | Lokale Bedienung funktioniert auch ohne antwortenden Agenten | ASTRA555; JETZT | G05 | offline verschieben, konfigurieren, schließen und Verbindung verwalten |
| R007 | Längerlaufende, abschließbare Arbeitspakete statt ständigem »go« | U217,534,536; JETZT | G01 | jedes Goal besitzt Outcome, Beleg, Grenzen und konkreten Übergabepunkt |
| R008 | Zwischendokumentation, eigene Harness/Skill, sichtbare Tests | U459,462,479,536 | G01 | Verfahren festgelegt; pro Bauetappe reale Evidenz und Zwischenstand, keine bloßen PASS-Etiketten |
| R009 | Frozen-Prototyp, Originale und Legacy-Spuren bleiben erhalten | U281,364,421; V77§13 | G01 | Änderungen nur im Neubau/zugeordneten Planpfad; Herkunft und Backups nachvollziehbar |
| R010 | Namen und Dokumente sind für Daniel verständlich und mit Autoren versehen | U323,327,384 | G17 | Einstieg erklärt zusammengehörige Dateien; absolute Pfade, Provenienz und klare Funktionsnamen |

## 2. Anzeigeorte, Arbeitsziele und echte Terminals

| ID | Verbindliches Ergebnis | Quelle | Goal | Fertigbeleg |
| --- | --- | --- | --- | --- |
| R011 | Overlay-Anzeige zwischen Windows, KDE 1 und KDE 2 wählbar | U470 überholt U445 | G06 | dieselbe Konfiguration an allen drei Anzeigeorten; kein neuer Agent durch Anzeigewechsel |
| R012 | Arbeitsziel unabhängig vom Anzeigeort und Empfänger | U424,445,470,556 | G06 | Windows-Raute arbeitet an KDE 2; anderer Agent gleichzeitig auf Windows |
| R013 | Ganzes sichtbares Desktopbild einschließlich Taskleiste, Hintergrund und offenen Programmen bindbar | U443,445 | G06 | Vergleich zu Originalaufnahme für Windows und beide KDE-Arbeitsflächen |
| R014 | Einzelnes Fenster/Browser/Programm/Spiel bindbar; exklusive oder gemeinsame Gates | U346,350,443; V76§2.4 | G06 | zwei getrennte Ziele und ein geteiltes Ziel; unzugehörige Bereiche fehlen beim Empfänger |
| R015 | Fensterscanner unten rechts an jeder Terminalansicht, Dropdown zur Bindung | U443; SKIZZE | G05 | auswählen, binden, wechseln, lösen; Ziel und Agent sichtbar, verschwundenes Ziel erklärt |
| R016 | Kein automatischer Fenster-Arrange-Zwang im Scanner | U443 | G05 | Binden verschiebt/vergrößert das Originalfenster nicht |
| R017 | Genau dieselbe Original-Terminalsession spiegeln, nicht eine ähnlich aussehende neue Shell | U474,477 | G04 | Session-/Prozessidentität und gleichzeitiger Original-/Overlay-Vergleich |
| R018 | Ausgabe, ANSI-Farben, Cursor, Unicode, Scrollback und Vollbild-Terminalprogramme korrekt | U474; ASTRA553 | G04 | identische Referenzfälle mit laufender Ausgabe, Cursor und Alternate Screen |
| R019 | Eingaben, Sondertasten, Einfügen und Größenänderung kommen richtig an | U477; ASTRA553 | G04 | einmalige Probe im tatsächlichen Ziel; Resize und Eingabezustand rückgelesen; keine Doppelzustellung |
| R020 | Terminalansichten auswählen, austauschen, verbinden, individuell verschieben/vergrößern | U443; SKIZZE | G05 | zwei Ansichten umbelegen; Quelle bleibt eindeutig, laufende Session bleibt erhalten |
| R021 | Agenten auf Wunsch am VPS einbinden/starten; bestehende Sessions wieder anbinden | U443,558 | G09 | »bestehende verbinden« und »neue starten« unterscheidbar; tatsächliche Runtime-Antwort |
| R022 | Bindungen bleiben bei geschlossenem/neu erzeugtem Fenster eindeutig | PRÜFUNG; aus R012–R020 abgeleitet | G06 | kein Input an wiederverwendetes Handle oder veraltete Terminal-ID |

## 3. Rauten, Regie und tägliche UI

| ID | Verbindliches Ergebnis | Quelle | Goal | Fertigbeleg |
| --- | --- | --- | --- | --- |
| R023 | Agentenraute ist der Sprechort des Agenten | U443,556 | G05 | Agent sendet über seine Session; Raute stellt richtigen Absender und Zielraum dar |
| R024 | Name, Farbe, Hotkey und Position pro Raute einstellbar | U443; V76§2.9 | G05 | zwei gleiche Modellnamen trotzdem unterscheidbare Sessions; Einstellungen nach Neustart |
| R025 | Hotkey-/Modifikator-Eingabe ohne unerwünschten Fokusverlust | U443; V76§2.9 | G05 | gezieltes Öffnen/Schließen; Normalmodus lässt darunterliegende App bedienbar |
| R026 | Gleiches Ereignis als 6,6-s-Ticker, 3,3-s-Fade-Banner und Chatnachricht | U443; V76§2.9 | G05 | eine Nachrichten-ID in drei Darstellungen; gemessene Zeiten und keine Chatduplikate |
| R027 | Banner räumlich zur Raute orientiert und innerhalb des Zielraums | U443; V76§2.9 | G05 | Fenster bewegen/skalieren, lange Texte und mehrere Sprecher ohne Abdriften |
| R028 | Regie unten links, aufklappbare/scrollbare Sprüche, Ziel und Empfänger vor Versand wählbar | U443; SKIZZE | G05 | einzelner Agent, Gruppe und Zielwechsel; Vorschau des Adressaten, Rückmeldung zur Zustellung |
| R029 | Alle dokumentierten Regiesprüche erhalten | V76§3; U443 | G05 | Weiter so, Mach mal, Go, Warte kurz, Pause/Weiter, Ja/Nein, Denk nach, Denk neu, Konzentrier dich, andere Idee, Undo, Neu scannen einzeln geprüft |
| R030 | Regie-Semantik ehrlich: Gesprächswunsch, Laufpause, Bildpause, Undo und Not-Aus nicht verwechseln | PRÜFUNG; aus R029 abgeleitet | G12 | »Denk nach« stoppt keine fremde Runtime heimlich; tatsächliche Wirkung/fehlende Unterstützung sichtbar |
| R031 | Transparenz jedes Bereichs/Buttons einzeln; 66 % Transparenz als Startwert | U443 | G05 | getrennte Werte bleiben gespeichert; Deckkraft/Transparenz eindeutig; Rücksetzen verfügbar |
| R032 | Keine Skizzen-Erklärungspfeile oder Ersatzdesktop als Dekoration | U443,513; SKIZZE | G05 | Referenzvergleich; eigene später gezeichnete Pfeile bleiben natürlich möglich |
| R033 | Webcam, Raute und Regiemeldungen passend im gebundenen Zielraum | U443 | G07 | Wechsel Desktop→Fenster verändert Platzierung/Adressierung, nicht heimlich die Session |
| R034 | Handlungsorte visuell erkennbar: Agentencursor, Zielrahmen, aktueller Steuerbesitz | V76§2.6,§5 | G10 | ein Agentenindikator entspricht einer echten Bindung/Aktion; kein vorgetäuschter zweiter Hardwarecursor |
| R035 | Verständliche, vollständige Bedienung statt nur vorhandener Buttons | JETZT | G18 | UI-Abnahme UQ01–UQ10 unten, einschließlich Fehler-/Offlinezuständen |

## 4. Sehen, Kamera, Mikrofon und Empfängerschutz

| ID | Verbindliches Ergebnis | Quelle | Goal | Fertigbeleg |
| --- | --- | --- | --- | --- |
| R036 | Vision pro Session starten, pausieren, fortsetzen und stoppen | U346; V77§4 | G07 | sichtbarer Zustandswechsel plus Auslieferungszähler; Stop liefert keine neuen Bilder und startet nicht heimlich neu |
| R037 | Start jetzt, ab Checkpoint, Ringpuffer oder gewähltem Bildfolgenpunkt | V76§4.8; V77§4 | G13 | Playhead/Quelle sichtbar; Vergangenheit nicht mit Live verwechselt |
| R038 | Livebild, Einzeldatei, Bildsequenz und Replay als Quellen | U346; V77§4.2 | G07 | jede Quelle ausprobiert; Replay-Checkpoint-Anbindung in G13 ergänzt |
| R039 | Beobachtungseinspeisung und sichtbares Overlay unabhängig schaltbar | V76§4.8; V77§4.3 | G07 | nur sehen, nur anzeigen und beides getrennt getestet |
| R040 | Kamera pro Agent zuschaltbar, PiP frei platzierbar, optional im Gesamtbild | U443; V76§2.2 | G07 | echte Aufnahme nur bei Aktivierung; ausgewählter Empfänger sieht PiP, anderer nicht |
| R041 | Mikrofon individuell geroutet; Push-to-talk bzw. VAD-Weg bedienbar | U443; V76§2.3 | G07 | echte Audiodaten/unterstützte Verarbeitung, Mute und Gerätefehler nachgewiesen |
| R042 | Wahrnehmung ist frisch, begrenzt gepuffert und nach Quelle unterscheidbar | V76§2.10; PRÜFUNG | G07 | Bildalter, Sequenzen, Samplinglücken und Überlast sichtbar; keine Phantom-Livebilder |
| R043 | Gate, einzelner Agent, Daniel, Kombinationen und Ausschlüsse pro Objekt | U350; V77§6 | G08 | Bild/Text für A, nicht B; Vergleich tatsächlicher Empfänger-Payloads, nicht nur UI-Checkboxen |
| R044 | Privates Material leckt weder in Basis-Capture noch Chat, Replay oder Export | V76§4.9.1; V77§6 | G08 | negative End-to-End-Tests einschließlich bereits sichtbar gerenderter Daniel-Notiz |
| R045 | Sparsamer Betrieb auf Daniels ThinkPad, keine unnötigen Dauerstreams/lokalen Modelle | V76§2.11 | G18 | Ressourcenprofil idle/capture/Kamera/mehrere Agenten auf echtem Gerät; Budgetabweichungen offen |

## 5. Malen, Text, Bilder und gemeinsames Zeigen

| ID | Verbindliches Ergebnis | Quelle | Goal | Fertigbeleg |
| --- | --- | --- | --- | --- |
| R046 | Bilddateien hinzufügen, verschieben, skalieren, ausblenden, Transparenz ändern | U346; V77§5 | G08 | reale Datei in Fenster/Gate/Desktop; Persistenz und Audience geprüft |
| R047 | Klick→Text schreiben→Enter; später bearbeiten und verschieben | U558; V76§4.9 | G08 | keine ungewollte Eingabe in darunterliegende Anwendung; Abbrechen möglich |
| R048 | Freihand, Marker, Farben, Strichstärken | U558,560; A559 | G08 | Striche mit Maus zeichnen, ändern, speichern und wieder öffnen |
| R049 | Linien, eigene Pfeile, Rechtecke, Kreise und schnelle geometrische Formen | U558,560; A559 | G08 | Auswahlwerkzeuge tatsächlich bedienbar, Objekt statt eingebranntem Wegwerf-Pixel |
| R050 | Einzel-/Mehrfachauswahl, Gruppierung, Reihenfolge, Resize, Undo/Redo | U558,560; A559 | G08 | mehrere Objekte gemeinsam bewegen; Undo betrifft richtige Ebene, nicht die Zielapp |
| R051 | Bleibt so lange gewünscht im gebundenen Gate; dort frei beweglich | U558,560 | G08 | weder Banner-Timer noch Agenten-Zielwechsel entfernt die Zeichnung ungefragt |
| R052 | Zeigegeste enthält gemeinten Ort, Ziel und damaligen Bildbezug | A557; U558,560 | G11 | nach Layoutwechsel Warnung/Neuauflösung statt blindem Klick auf alte Koordinaten |
| R053 | Inhaltshaftung, wo zuverlässig verfügbar; sonst erkennbare Fensterbindung | A559; U560 korrigiert Priorität | G11 | Scroll-/Resize-Test mit echtem Anker; fehlende Erkennung bleibt sichtbar statt vorgetäuscht |
| R054 | Darstellung getrennt von echter Einfügung in die Anwendung | V76§4.10; V77§5.3 | G11 | Overlay verändert App nicht; ausdrücklich gewählte Einfügung hat eigenen Ergebnisbeleg |

## 6. Mehrere Agenten und wirkliche Hände

| ID | Verbindliches Ergebnis | Quelle | Goal | Fertigbeleg |
| --- | --- | --- | --- | --- |
| R055 | Mehrere Sessions desselben Modells gleichzeitig, getrennte Aufgaben/Chats/Rauten | U558 | G09 | zwei Codex-/andere gleichartige Sessions bleiben bei Reconnect unterscheidbar |
| R056 | Eltern-/Subagent-Beziehungen, Gruppenwahl, Auftrag, Status und Ergebnis | U558; A559 | G09 | realer unterstützter Subagent mit Parent und Rückgabe; nicht steuerbare Kinder klar markiert |
| R057 | Einzelne/Gruppe verbinden, ansprechen, beobachten, pausieren und beenden soweit Runtime unterstützt | U558,560; A559 | G09 | Capability-Matrix gegen echte Adapter; fehlende Pause nicht als ausgeführt melden |
| R058 | Codex, Gemini, Claude, Kimi und GPT als unterscheidbare Teilnehmer anbinden | V76§1,§2.8; U295 | G09 | echte erlaubte Adapterwege, keine Attrappen; bestehende Kimi-Betriebsgrenzen erhalten |
| R059 | ChatGPT/MCP mit ehrlichem Inspect/Act/Status und sichtbaren Arbeitsmeldungen | V76§2.8; PRÜFUNG | G09 | tatsächlicher Host erhält Bild/Status und unterscheidet Fehler von Erfolg; kein Versprechen über verborgenes Denken/Chatdarstellung |
| R060 | Gemeinsames Gate und private Kommunikation, inklusive Agent→Agent | U350,424; V76§2.9 | G09 | drei Empfänger, richtige Zustellung und keine Selbst-Echo-Endlosschleife |
| R061 | Agenten parallel auf Windows und Linux, ohne fremden Fokus/Input zu übernehmen | U424 | G10 | zwei gleichzeitige reale Aufgaben, getrennte Ziel-/Eingabespuren |
| R062 | Maus/Tastatur-Handlungen einschließlich Klicken, Tippen, Ziehen und Hotkeys | V76§2.6,§4 | G10 | sichtbare Vor-/Nachher-Wirkung in ungefährlicher echter App je Plattform |
| R063 | Hintergrundbedienung, wo unterstützt; Shared-Mouse-Lease als eigener Modus | V76§2.6 | G10 | Fähigkeiten pro App nachgewiesen; Fallback sichtbar, kein heimlicher Cursor-/Fokusdiebstahl |
| R064 | Virtuelle Controller und Hybrid Mensch+Agenten als wählbare Adapterfähigkeiten | V76§2.6 | G10 | Treiber-/Geräteprüfung; mehrere getrennte Controller, Ziel bis vier; Hybrid-Eingabe in geeignetem Test |
| R065 | Menschlicher Eingriff hat Vorrang; ausdrücklich wählbare freiere Autonomie | V76§2.5; U336 | G10 | Override und gewählte Ausnahme getrennt testen; Not-Aus gilt in beiden |
| R066 | Lokaler Not-Aus/F12, sichtbarer Stop, Fehler-/Disconnect-Abbruch | V76§5; PRÜFUNG | G10 | auch bei UI-Hänger/Netzausfall; gedrückte Tasten freigeben; gemessene statt erfundene Latenz |
| R067 | Zielkäfig, Lease, Koordinaten/DPI, Rechte, Fokus und Aktualität berücksichtigen | V76§2.4; B78§3,6 | G10 | veraltetes/unerlaubtes/falsches Ziel blockiert; positive Aktion separat belegt |
| R068 | Kein verspätetes Wiederabspielen alter Eingaben nach Reconnect | PRÜFUNG; ASTRA553 | G03 | verzögerte/duplizierte Nachricht verursacht keine zweite oder nachträgliche Mutation |

## 7. WorldDOM, selbstentworfene Brücken und Freiheit

| ID | Verbindliches Ergebnis | Quelle | Goal | Fertigbeleg |
| --- | --- | --- | --- | --- |
| R069 | Echte DOM-/Accessibility-Struktur zusätzlich zum Screenshot nutzen | U355; V77§7 | G11 | echte Strukturquelle mit Herkunft, Geometrie und aktueller Auflösung |
| R070 | Auch ohne nativen DOM: aus Bild erschlossene und bewusst erfundene Knoten/Kanten | U355; V76§4.12 | G11 | Canvas-/Bildbeispiel mit inferred/authored/projected; Konfidenz und Grenzen sichtbar |
| R071 | Semantischer Auftrag wird zur konkreten Handlung mit Ergebnisrücklese | V76§4.12; V77§7.2 | G11 | benannten Knoten auflösen, handeln, Wirkung prüfen; ungelöster Knoten bleibt ungelöst |
| R072 | Python-Harness aus Zuständen, Aktionen, Kanten, Guards, Witnesses, Fallbacks und Checkpoints | U338,341; V76§4 | G12 | echter mehrschrittiger Workflow verzweigt bei geändertem Zustand und ist pausierbar |
| R073 | Agenten entwerfen, ändern, speichern und wiederverwenden eigene Teilbrücken | U338; V76§4.1–4.7 | G12 | Agent erzeugt ausführbaren Graph, Version bleibt sichtbar, geänderter Durchlauf überschreibt Original nicht |
| R074 | Gemeinsame Arbeit/Delegation mit Zustand, Verlauf, Grund und Unsicherheit | V76§4.6; U336 | G12 | realer Handoff an zweite Session mit nachvollziehbarer Fortsetzung |
| R075 | Freier Modus ohne zusätzliche Einzelklick-Bestätigung; optionale Profile einzeln | U336; V77§8.2 | G12 | free/shadow/witness/daniel_gate/learning/delegated_learning getrennt bzw. kombiniert; lernen initial aus |
| R076 | Vorschau, Ausführung, Pause, Fortsetzen, Abbruch, Replay klar getrennt | V76§4; B78§6 | G12 | Replay führt nichts in Live-App aus; Stop hält weitere Knoten an |
| R077 | Loops, Automationen und Goals mit Start/Stop/Budget/Fortschritt | U357; B78§6 | G15 | wiederkehrender Auftrag läuft begrenzt, pausiert, beendet sich mit echtem Ergebnis |
| R078 | Neue Abläufe ohne neuen EXE-Build nutzbar, soweit keine neue Plattformfähigkeit nötig ist | ASTRA555; U338 | G12 | neuen deklarativen Graph laden und benutzen, gleiche Clientversion |

## 8. Zeit-Scrubber und Momentkapseln

| ID | Verbindliches Ergebnis | Quelle | Goal | Fertigbeleg |
| --- | --- | --- | --- | --- |
| R079 | Letzte Sekunden durchgehen, Zeitpunkt wählen, neuen Versuch/Analysezweig beginnen | U336,558; V77§9 | G13 | Original erhalten, neuer Branch referenziert Start; Livezustand vor neuer Aktion frisch prüfen |
| R080 | Snapshot einzelner oder mehrerer Fenster/Gates/Agenten/Zeitabschnitte | U558 | G13 | Mehrfachauswahl speichert genau diese Auswahl, keine fremden Quellen |
| R081 | Arbeitszustand umfasst Terminal, Tools/Resultate, Auftrag/Plan/Richtung, geteilte Bemerkungen | U560 | G13 | Kapsel enthält tatsächlich verfügbare Ereignisse mit Quelle/Zeit und sichtbaren Lücken |
| R082 | Chat, Rauten-/Bannermeldungen, Bilder, Zeichnungen und Bindungen gemeinsam aufbewahren | U558,560 | G13 | spätere Ansicht rekonstruiert den damaligen Arbeitsmoment ohne Live-Verwechslung |
| R083 | Frei erweiterbare Mehrfachkategorien: Idee, Verwirrung, Fehler, Lösung, Umweg usw. | U558,560; A559 | G13 | eigene Kategorie anlegen, mehrfach zuordnen, wiederfinden |
| R084 | Später gemeinsam ansehen, annotieren, vergleichen und Lernstrecken bilden | U558,560; A559 | G13 | zwei Kapseln vergleichen und kommentieren; Original-Hashes unverändert |
| R085 | Fehlversuche und schmutzige Umwege ausdrücklich erhalten | U558 | G13 | gescheiterter und erfolgreicher Pfad gleich gut auffindbar, nichts automatisch schöngeschrieben |
| R086 | Aufgezeichnete Beobachtung statt erfundener Totalzustand/verborgener Gedanken | U560; PRÜFUNG | G13 | Aufnahmeinventar benennt fehlende Quellen; keine behauptete beliebige App-Wiederherstellung |

## 9. Hauhaucs und das Kontext-Mischpult

| ID | Verbindliches Ergebnis | Quelle | Goal | Fertigbeleg |
| --- | --- | --- | --- | --- |
| R087 | Vorhandene Hauhaucs-Chatinstanz anbinden; Hintergrundinstanz der Wesen unberührt | U562 | G14 | tatsächlicher Endpunkt/Sessionpfad geprüft; keine Änderung an Hintergrundbetrieb |
| R088 | Aufnahme ohne Modell; optional aktives Mitlesen und »jetzt dokumentieren« | U560,562; A563 | G14 | Aufzeichnung funktioniert ohne Inferenz; Modellmodus verarbeitet gewählte Ausschnitte |
| R089 | Zwei/drei Agenten mitlesen, Quellen unterscheidbar, Aufnahme-/Lese-Cursor sichtbar | U560; A563 | G14 | ausgewählte Ereignisse vollständig zuordenbar; ungelesener Rest nicht als gelesen angezeigt |
| R090 | Neue Session mit tatsächlich leerem Systemprompt, eigene benennbare Zusatzfelder | U564,567; A569 | G14 | effektiven Request prüfen, keine verborgene Standardpersönlichkeit/Alt-Zusatzfelder |
| R091 | Prompt schreiben, schalten, ansehen, importieren/exportieren; Einmalfeedback und Ausgabegrenzen | U567; A569 | G14 | Vorschau entspricht gesendetem Request; Feedback genau einmal, Grenzen erkennbar |
| R092 | Kontextanzeigen gesamt/je Nachricht, Schätzungen von Server-Tokenwerten trennen | U567; A569 | G14 | Anzeige gegen Request und Serverbericht prüfen; keine falsche Präzision |
| R093 | Kontext leeren/halbieren, beliebige Nachrichten wählen, einzelne Sätze entfernen, zurückspringen | U567; A569 | G14 | nach Speichern/Neuladen genau gleiche Auswahl/Änderung; Archiv erhalten |
| R094 | Text und mehrere MD-/Textdateien einspeisen ohne sofortige Antwort | A569; U567 | G14 | Material im Kontext, kein unerwünschter Inferenzaufruf |
| R095 | Sessions benennen, speichern/laden, archivieren, importieren/exportieren; flüchtige Geister-Session | U564,567; A569 | G14 | Isolation und Persistenz; flüchtige Session klar kenntlich |
| R096 | Beobachtung stoppen oder am gewählten Kontext-/Tokenbudget beenden; Bilder separat optional | U560 | G14 | keine weiteren Modellaufrufe nach Stop; Kontextkürzung transparent, Dokumentation mit Quellen |

## 10. Wissen pflanzen, Tragbarkeit, Android und Gesamtende

| ID | Verbindliches Ergebnis | Quelle | Goal | Fertigbeleg |
| --- | --- | --- | --- | --- |
| R097 | Wissen in gewählten laufenden Kontext/Gate pflanzen und gezielt verteilen | U357; V77§10 | G15 | gewünschter Empfänger erhält Seed, ungewählter nicht; Herkunft bleibt erhalten |
| R098 | MD-/Memory-/Agentenstart-/Skill-Ziele separat und mit konkreter Freigabe bearbeiten | U357; V77§10 | G15 | zieltypgerechter Vorschlag/Patch, Rücklese, keine fremden Heime überschrieben |
| R099 | Erfahrung→Seed→Skill/Harness/Loop/Automation/Goal entwickeln | U336,357; V77§10 | G15 | eine wirkliche Erfahrung wird wiederverwendbare Fähigkeit; kein behauptetes Modelltraining |
| R100 | Seeds vorschlagen, aktivieren, zurückziehen, versionieren und exportieren | V77§10 | G15 | Lebenszyklus bedienbar, Originalquelle und aktive Ableger nachvollziehbar |
| R101 | Windows/Linux-Kern später auf Android mit Capture, Overlay, Touch/Gesten erweitern | U388,400; DREAM§3 | G16 | reale Geräteaufnahme, mobile Bedienung, Rotation/Stop/Verbindung und gleiche Sessionsemantik |
| R102 | Android/Gord: gemeinsames Beobachten, Calls, Kommunikation und spätere Matchanalyse | U388,408; DREAM§4 | G16 | mobile Team-Kommunikation und wiederöffnbarer Spielmoment; keine erfundenen unsichtbaren Gegnerdaten |
| R103 | Daniels zusätzliche Handlungsvision: Flicker/Spell 1/2, niemals Ult oder Steuerknüppel; auch Ranked genannt | U390,392,394,400 | G16 | Wünsche nicht auf Coaching verkürzt; getrennte Aktionen mit Negativbelegen für Ult/Steuerknüppel; Live-Einsatz nicht durch diesen Plan aktiviert |
| R104 | Vollbetrieb, Sparbetrieb, Archiv/Schlaf und Wiedererweckung | U366,370,372; V77§11–12 | G17 | ohne bezahlte Laufzeit lesbares Archiv; später Start aus exportiertem Zustand |
| R105 | Vollständige Rohsicherung und sortierte Ableitung, einschließlich alter MD/Python/JSON-Spuren | U364; V77§11.3 | G17 | Manifest/Prüfsummen, unveränderte Rohkopie; keine Löschung als impliziter Schritt |
| R106 | Migration samt Git, Datenbanken, Entitäten/Selbstmodellen, Memories, Skills, Loops/Goals und Services | U370; V77§11.4 | G17 | Wiederherstellung auf isoliertem frischem Ziel mit Startreihenfolge und Datenvergleich |
| R107 | Konfiguration, Abhängigkeiten, CPU-/GPU-Profile und getrennt geschützte Secrets | V77§11–12 | G17 | Preflight zeigt fehlende Hardware/Secrets; keine Geheimnisse im öffentlichen Bundle |
| R108 | Anbieterwechsel/Abopause löscht weder Erinnerung noch offene Aufgaben | U372; V77§12 | G17 | Adapter fällt aus, Daten bleiben nutzbar; Austausch verliert keine Provenienz |
| R109 | Rechtzeitig vor möglichem VPS-Ende migrationsfähig; USB-Archiv als geplanter Weg | U364,366,370 | G17 | relativer Wunsch »ca. drei Monate vorher« dokumentiert; realer Vertragstermin vor Terminierung prüfen |
| R110 | Open-Source-fähiges Paket mit Installation, Demo, Lizenz-/Abhängigkeitsprüfung und Beitragsdoku | U360; V77§13; DREAM§13 | G17 | frischer Installations-/Restorelauf, private Daten getrennt; Veröffentlichung erst auf Auftrag |
| R111 | Alle Funktionen zusammenhängend statt lose Einzel-Demos | JETZT | G18 | End-to-End-Szenarien E01–E10 des Goal-Plans plus alle Registerzeilen belegt |
| R112 | Gute UI nicht erst am Ende: in jeder Etappe richtige Platzierung, klare Zustände, Fehlerrückmeldung | U443,462,470; JETZT | G18 | UQ-Kriterien gelten fortlaufend; Endabnahme prüft nochmals das Zusammenspiel |

## UI-Qualität: Was »menschlogisch nutzbar« konkret bedeutet

Diese Kriterien sind Codex' prüfbare Übersetzung, kein Anspruch, Geschmack durch ein Testskript abschließend messen zu können. Daniels abschließender Blick auf die tatsächliche UI bleibt Teil der Abnahme.

| ID | Kriterium und praktische Prüfung |
| --- | --- |
| UQ01 | Normale Aufgaben brauchen weder Shell noch manuelle JSON-Änderung. Alle Registerfunktionen besitzen einen auffindbaren Bedienweg; Agentenwerkzeuge sind zusätzliche Wege. |
| UQ02 | Vor Versand/Handlung erkennbar: wer, welche Session, welches Ziel, welche Empfänger. Gleiche Modellnamen führen nicht zu Verwechslung. |
| UQ03 | Ein Button reagiert sichtbar und unterscheidet laufend/erfolgreich/abgewiesen/fehlgeschlagen/offline. Unsupported ist erklärt und nicht scheinbar bedienbar. |
| UQ04 | Freie Overlay-Bereiche lassen die echte App arbeiten; Text/Zeichnen/Drag erhalten gezielt Fokus. Escape/Abbrechen verlässt den Modus ohne versehentliche App-Aktion. |
| UQ05 | Platzierung folgt SKIZZE plus U443: unten links Regie/Medien, Scanner pro Terminal unten rechts. Keine künstliche Arbeitsdesktop-Kopie. |
| UQ06 | Namen, Farben, Kürzel, Positionen, Größen, Transparenzen, Bindungen und Profile bleiben nach Neustart erhalten. Konflikte und Zurücksetzen sind verständlich. |
| UQ07 | Lange deutsche Texte, viele Agenten, Dropdowns, kleine Fenster, Monitorwechsel und mehrere DPI-Werte bleiben bedienbar: keine abgeschnittenen Kernaktionen oder unerreichbaren Dialoge. |
| UQ08 | Tastaturwege, erkennbare Fokusmarkierung und lesbare Beschriftungen; Status nicht nur durch Farbe. Frei gewählte Transparenz erhält erreichbare Wiederherstellungsbedienung. |
| UQ09 | Rückgängig/Redo/Schließen/Stop wirken auf die klar benannte Ebene. Aufnahme löschen/ausblenden ist nicht Zielapp-Undo; Vision-Pause nicht globaler Not-Aus. |
| UQ10 | Im echten gemeinsamen Einsatz kann Daniel die End-to-End-Aufgaben ohne mündliche Geheimanleitung erledigen. Auffindbarkeitsprobleme werden als Defekte erfasst, nicht durch Hinweise des Agenten wegmoderiert. |

## Konflikte und fehlende Eindeutigkeit — nicht unter den Teppich

| Konflikt | Arbeitsentscheidung / offen gebliebene Frage |
| --- | --- |
| »Nur Windows-Anzeige« gegen späteren Wechsel Windows/KDE | U470 ist später und gilt. |
| Browserbeweis gegen echtes Programm | Native Abnahme bleibt nötig; B4.6 ist kein fertiges Produkt. |
| Freier Default gegen »observe-only« aus B78 | Neue Verbindung erhält nicht still Eingaberechte. Innerhalb des von Daniel eingeschalteten Handlungsbereichs ist free ohne zusätzliche Einzelklick-Freigaben der Default. Lernen/Vorschau sind initial aus. |
| Alle sehen denselben Frame gegen individuelle private Objekte | Pro-Empfänger-Komposition und capture-sichere Trennung erforderlich. Nicht beide Garantien widersprüchlich behaupten. |
| 66 % transparent gegen vorhandene Alpha-Werte | Arbeitsannahme 34 % Deckkraft; Anzeige erklärt beide Begriffe. |
| Mehrfachansicht gegen neue Agenteninstanz | »Weitere Ansicht« und »neue Session« sind verschiedene UI-Aktionen. |
| Gesamtsnapshot gegen beliebigen Speicher-Restore | U560 konkretisiert den sichtbaren Arbeitsmoment. Keine verborgenen Gedanken oder universellen RAM-Snapshots versprechen. |
| Neue Freiheiten gegen Kimi-Sonderregeln | Kimi keine Subagents aufzwingen; Fähigkeiten je Runtime, nicht global vortäuschen. |
| Ranked-/Handlungswunsch fehlt im geglätteten DREAM | R103 hält Daniels tatsächlichen Wunsch fest. Keine stillschweigende Umdeutung zu ausschließlich Coaching; Plattform-/Einsatzgrenzen werden bei der technischen Etappe gesondert ausgewiesen, nicht durch Behauptungen gelöst. |
| <60 MB RAM / 0 VRAM / <1 ms und ähnliche frühere Garantien | Historische Zielzahlen bleiben Herkunft, nicht erwiesene Zusagen. G01 legt messbare Budgets vor Implementierung fest; Abweichungen dürfen nicht als PASS verborgen werden. |
| »36 Stunden komplett« | U368 bleibt Zeitwunsch, kein gemessener Aufwand. Keine erfundene Termingarantie; Fortschritt über bestandene Abnahmen. |
| Vorschläge Rauten-Chor/Baton/automatische F12-Blackbox | Nach U336 nicht als neue verpflichtende Produkte aufnehmen. Normale Kommunikation, Steuerstatus und Scrubber bleiben separat ausdrücklich gewünscht. |
| Frühere pauschale Ablehnung »andere drei Dinge« | Der Scrubber wurde im selben Beitrag ausdrücklich gelobt und später mehrfach konkretisiert; er wird nicht aufgrund der unklaren Zählung entfernt. |

## Nicht vergessen, aber keine zusätzliche Produktfunktion

Die frühen Crash-/Sicherheitsfix-Nachrichten, Scherze über Codex, die Song-Anfrage und reine »go«-/Dankes-/Statusnachrichten sind nicht eigenständige Bridge-Funktionen. Wiederholungen verstärken Anforderungen, erzeugen keine künstlichen Duplikate. Wortlautarchiv, Autorenschaft, verständliche Titel, Sicherung und Dokumentation bleiben Arbeitsanforderungen (R008–R010), keine neue Funktionskathedrale.

U313 erwog Löschen; U364 und U421 legen später ausdrücklich Erhalten/Neubau fest. Der Prototyp wird nicht gelöscht. 2.dbrain/Schrottplatz dürfen als Nutzungszentrum abgelöst werden, ihre Daten bleiben Herkunft (R009/R105). Ein 4-TB-Stick und eine Gigabitleitung sind Daniels geplanter Transportweg, keine jetzt vorhandene Infrastruktur und keine Aufforderung, Hardware zu kaufen.

## Vollständigkeit und Statuspflege

Die Tabelle deckt die hier ausgewerteten Produktanforderungen ab, nicht eine mathematische Garantie, dass kein Gesprächsdetail übersehen werden kann. Bei neu gefundenem Detail: Quelle angeben, bestehender ID zuordnen oder neue hinzufügen; keine stille Änderung des Wortlautarchivs. Jede Abnahme nennt Build/Plattform/Datum/Belegpfad. `offen`, `implementiert`, `integriert`, `belegt` und `von Daniel abgenommen` bleiben unterschiedliche Zustände.

Ein offener Adapter oder fehlender Gerätezugang darf ein einzelnes Goal tatsächlich aufhalten. Er darf weder als Erfolg zählen noch die betreffende Anforderung aus dem Gesamtziel verschwinden lassen. Die vollständige Bridge ist erst fertig, wenn alle obligatorischen Zeilen und UI-Kriterien belegt sind; verbleibende Grenzen müssen ausdrücklich mit Daniel entschieden werden, nicht einseitig als »später« entsorgt werden.
