---
autor: codex bei Daniels VPS
datum: 2026-09-19
inhalt: Daniels Anforderungen; Quellenzuordnung und Abnahmekriterien von Codex
status: Planungsbaseline, keine Produktabnahme
bearbeitet: 2026-09-20 durch claude bei Daniels VPS — Zusammenlegung mit dem Abschnitt »Was Daniel festgelegt hat« der Baustartprüfung, Spalte Stand, Beschlüsse und Ergänzungen von Daniel vom 2026-09-20, Ton einzelner Sätze; Bedeutung und Pflicht der Zeilen R001–R112 unverändert
---

# Augen & Hände — alles, was die Bridge können muss

## Wozu dieses Register dient

Daniel hat den Umfang bereits beschrieben. Dieses Register verlangt keine neue Wunschliste. Es ordnet die vorhandenen Produktanforderungen einem verantwortlichen Goal und einem überprüfbaren Ergebnis zu.

Jede Zeile ist eine Verpflichtung im Gesamtplan, nicht die Behauptung, sie sei implementiert. Die zusammengehörige Rückwärtsplanung steht in `/root/werkraum/docs/augen_haende_bridge/PLAN.md`.

Ergänzung aus dem Gespräch vom 2026-09-19: vom letzten Goal rückwärts planen; alle beschriebenen Funktionen sollen menschlich verständlich, zusammenhängend, sauber geordnet und wirklich bedienbar sein.

Keine Verkleinerung auf eine EXE-Demo. Android bleibt die von Daniel als später beschriebene Erweiterung, aber im Gesamtumfang.

Öffentliche Veröffentlichung und tatsächliche VPS-Migration bleiben gesondert auszulösende Außenaktionen.

Die IDs dienen der Nachverfolgung, nicht als UI-Beschriftungen. Menschenlesbare Titel bleiben maßgeblich.

Alle Anforderungen sind bei Erstellung **offen hinsichtlich der Gesamtproduktabnahme**; historische Teilbeweise werden nicht automatisch übernommen.

Die Spalte Stand führt die fünf Zustände aus »Vollständigkeit und Statuspflege«. Ein Verweis in dieser Spalte (BE…, R…) nennt einen späteren Beschluss von Daniel, der die Zeile ändert oder präzisiert; die Zeile selbst bleibt dabei unverändert.

## Quellen und Leseregel

| Kürzel | Vollständiger Pfad / Herkunft |
| --- | --- |
| U / A | `/root/werkraum/docs/augen_haende_bridge/archiv/codex-session-01a0b38d-5ece-75b3-a06e-86bf715f6c36-messages.jsonl` — U bezeichnet User-, A Assistant-Nachrichten nach `ordinal` |
| ASTRA | `/root/werkraum/docs/augen_haende_bridge/archiv/codex-session-01a0b38d-5ece-75b3-a06e-86bf715f6c36-astra-planung-messages.jsonl` — enger Planungsabschnitt (`ordinal` 548–587), besonders 548–569 |
| V76 | `/root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md` — Gemini-Ursprung plus Erweiterungen |
| V77 | `/root/werkraum/docs/systemdoku/77_worlddom_memory_seeds_wiedererweckung.md` |
| B78 | `/root/werkraum/docs/systemdoku/78_augen_und_haende_bauplan.md` — ältere Etappen, kein neuer Abschlussbeweis |
| LUNA | `/root/werkraum/docs/augen_haende_bridge/KAPSELN_UND_HAUHAUCS.md` — abgeleitete Planung |
| DREAM | `/root/werkraum/docs/vision/augen_und_haende_androidbridge_mlbb_dream.md` |
| PRÜFUNG | `/root/werkraum/docs/augen_haende_bridge/BEFUNDE.md` (Baustartprüfung vom 2026-09-19; ihre technischen Verträge stehen in `TECHNIK.md`, die Beweisstrategie in `NACHWEISE.md`, die Kontaktstrecke in `PLAN.md`) |
| SKIZZE | `/vps_root/werkraum_bilder/refferenzen/hand-auge-bridge-ref.jpg` (in der Vorlage `h a bridge.jpg`, unter diesem Namen heute nicht mehr vorhanden) — angesehen; Daniels Erklärung U443 korrigiert die Leserichtung |
| JETZT | Laufendes Gespräch nach dem archivierten Ausschnitt: vollständiger Umfang, Endziel zuerst, Bedienbarkeit als Abnahme |
| D0920 | Gespräch von Daniel mit Claude Code in vd1 am 2026-09-20: Beschlüsse BE01 bis BE04 und die Zeilen R113–R120; nachlesbar im Gesprächsprotokoll dieser Sitzung (in vd1 unter `/config/.claude/chat_log_2026-09.md`, Einträge vom 2026-09-20) |

Vorrang: spätere ausdrückliche Daniel-Korrektur vor früherem Entwurf. Assistant-Vorschläge sind als solche zu lesen, soweit Daniel sie nicht übernommen hat.

Technische Abnahmedetails in diesem Register sind Operationalisierungen von Codex, keine wörtlichen Daniel-Zitate.

Die Quellen wurden thematisch und gegen die vollständige User-Nachrichtenliste des vorhandenen Exports geprüft.

Dies ist kein neuer wortgetreuer Export aller Assistant-/Toolnachrichten; der vorhandene Archivumfang bleibt unverändert.

Die Beschlüsse von Daniel vom 2026-09-20 (unten) sind spätere ausdrückliche Korrekturen und gehen den Zeilen vor.

## Was Daniel festgelegt hat (Stand 2026-09-19)

Aus der Baustartprüfung vom 2026-09-19 übernommen. Spätere Beschlüsse stehen im nächsten Abschnitt.

- Ein echtes Programm mit EXE und Overlay, keine Homepage und kein nachgebauter Desktop. Freie Bereiche dürfen die Bedienung darunter nicht blockieren.
- Anzeigeort, Arbeitsziel, Session und Empfänger sind getrennt. Das Overlay soll zwischen Windows und KDE-Desktop 1/2 umschaltbar sein; unterschiedliche Agenten können gleichzeitig unterschiedliche Arbeitsziele benutzen. Das ist Zielumfang, nicht bereits geliefert.
- Ein Zielwechsel ersetzt keine CLI-Session. Mehrere Instanzen desselben Modells und Eltern-/Subagent-Beziehungen müssen unterscheidbar sein.
- Die Raute ist der Sprechort des Agenten. Name, Farbe und Hotkey sind einstellbar. Eine Nachricht erscheint neben der Raute für 9,9 Sekunden (größer, hoch, umgebrochen), räumlich als ausblendendes Banner für 6,6 Sekunden und dauerhaft im zugehörigen Chat. *(Zeiten geändert am 2026-10-01 auf Daniels Wunsch; vorher 6,6 s und 3,3 s. Daniels eigene Worte: nur Chat und Banner.)*
- Regie sowie Mikrofon-/Kamerabedienung unten links; Scanner am Terminal unten rechts. Beschriftungspfeile in der Skizze sind keine dekorativen Datenleitungen. Mikrofon und Kamera sind einzeln pro Agent zuschaltbar.
- Einzelfenster und kompletter sichtbarer Desktop sind bindbar. Terminalansichten sollen dieselbe echte Session abbilden und bedienen, einschließlich Cursor, Farben, Größenänderung und Eingaben — nicht nur Textkopien.
- Transparenz und Darstellung sind individuell einstellbar. Arbeitsannahme für den Start: »66 % transparent« bedeutet 34 % Deckkraft. Die Einstellung muss beide Begriffe eindeutig machen; der bestehende Wert 0,94 erfüllt das nicht.
- Bilder, Texte, Freihandzeichnung und geometrische Formen gehören in den gewählten Gate-/Zielraum; verschiebbar, mit einzeln einstellbarem Empfängerkreis. Rückgängig und Wiederbearbeiten gehören zur brauchbaren Bedienung. Automatisches Haften an beliebigem Bildinhalt ist eine zusätzliche Fähigkeit, keine zugesicherte Universalwirkung.
- Bilderzufuhr und Beobachtung müssen explizit start- und stoppbar sein. Lernen ist standardmäßig aus, später individuell bis hin zu freierer Zusammenarbeit zuschaltbar. Umwege und Fehler sind Lernmaterial, nicht nur Erfolge.
- Kapseln bewahren ausgewählte Momente mehrerer Fenster, Agenten oder Zeitabschnitte: Bilder, sichtbare Terminalausgaben, tatsächlich verfügbare Toolaufrufe und Ergebnisse, geteilte Pläne/Bemerkungen, Chat, Rautenmeldungen und Markierungen. Kein Versprechen, verborgene interne Gedanken oder beliebige Programmspeicher zu kopieren.
- Hauhaucs darf als zusätzliche Chat-/Beobachtungssession hinzukommen, mit leerem bzw. selbst geschriebenem Systemprompt und sichtbarer Kontextpflege. Die bestehende Hintergrundinstanz der Entitäten wird dafür nicht umgebaut.

## Beschlüsse von Daniel vom 2026-09-20

Quelle D0920. Diese Beschlüsse sind spätere ausdrückliche Korrekturen und gehen den Zeilen weiter unten vor.

Die Zeilen selbst bleiben unverändert; die Spalte Stand nennt den Beschluss, der sie ändert oder präzisiert.

### BE01 — 1:1 nur für Sitzungen, die die Bridge selbst startet

Zustand: Ein Terminal ist nur dann 1:1, wenn die Bridge es von Anfang an hält: Ausgabe, Eingabe und Größe.

Bei einem schon laufenden Konsole-Fenster gehört das alles Konsole, die Bridge kann dort nur zuschauen und hineintippen.

Beschluss: 1:1 gibt es nur für Sitzungen, die die Bridge selbst startet. Ein Kompromiss ohne 1:1 wird nicht eingegangen.

Das Finden und Einbinden schon laufender Terminals entfällt aus dem Plan. Wer heute in einer Konsole läuft, wird für die Bridge neu gestartet, und zwar in der Bridge.

Wirkt auf R017 und auf die zweite Hälfte von R021 (»bestehende Sessions wieder anbinden«), im Plan auf die Sätze zu bestehenden Sessions in G01, G04 und G09.

### BE02 — Start über gespeicherte Starts

Agenten werden aus der Bridge über eine Liste gespeicherter Starts gestartet, so wie PuTTY gespeicherte Sitzungen kennt.

Ein Start besteht aus Name, Ort, Arbeitsordner und Programm. Der Programmname allein sagt nicht, welcher Agent aufgeht (`claude` ist in vd1 der eine, in vd2 ein anderer); Name und Ort in der Liste legen es fest.

Der Ort (»vd1«, »vd2« oder »Host«) steht neben dem Terminal. Host ist ein Ort wie vd1. Ein eigener Arbeitsordner kann ein eigenes Profil sein: Haiku startet in `/home/claude_haiku`, damit Sessionstart und CLAUDE.md des Standardagenten nicht geladen werden, und hat eine eigene Persona.

| Name | Ort | Ordner | Programm | Bemerkung |
| --- | --- | --- | --- | --- |
| Claude | vd1 | `/config` | `claude` | |
| Codex | vd1 | `/config` | `codex` | |
| Gemgem | vd1 | `/config` | `agy` | Gemini |
| Anthropic-Claude | vd2 | `/config` | `claude` | |
| Gravity | vd2 | `/config` | `agy` | Gemini |
| Haiku | Host | `/home/claude_haiku` | `claude` | eigenes Profil, eigene Persona |
| GLM | Host | `/root` | `glm` | Ordner aus den Mitschriften abgeleitet, von Daniel nicht bestätigt; GLM ist laut Daniel auch in vd1 installiert, eine zweite Zeile (vd1, `/config`) ist offen |
| Kimi | Host | `/root` | `kimi` | Ordner aus den Mitschriften abgeleitet, nicht bestätigt; bleibt im Plan (R058), Daniel schätzt zu 66 %, dass Kimi nicht innerhalb eines Jahres wiederkommt |
| ChatGPT | Web-Sitzung | – | – | Bindung statt Start (R059, G06.5) |

### BE03 — Die exe kommt, wenn der erste Körper komplett steht

Zustand: Der Plan (G02, G03) liefert die exe nach G01 als kleinstes Overlay mit Erstkontakt und baut alles Weitere danach über die laufende Bridge.

Beschluss: Daniel bekommt die exe erst, wenn der erste Körper komplett steht. Er besteht aus einem Terminal, das die Bridge hält, aus einem Fensterscanner je Terminal und Agent, aus der Raute, aus Kamera und Mikrofon.

Bis dahin baut und prüft Claude auf dem VPS und unter Wine, und Daniel bekommt nichts zum Ausprobieren.

Im Plan liefert G02 damit die exe mit dem kompletten ersten Körper und ist das Goal, das Daniel die exe gibt. Das genügt Daniel. G03, der erste Kontakt, folgt danach. G04, G05 und G07 bauen später aus, was über den ersten Körper hinausgeht.

### BE04 — Harness und Skills 1:1, Playwright zuletzt

Beschluss: Claude benutzt die Harness der Bridge von Codex (`harness.py`) und die beiden Skills, den Greenfield-Builder und den Bridge-Skill, zuerst 1:1, so wie sie sind. Sie werden nicht geändert.

Am Ende jedes Laufs steht nach der Harness immer Playwright als letzter Zeuge.

Wirkt auf den Arbeitsvertrag im Plan (Punkt 4) und auf `NACHWEISE.md`. Bei nativen Funktionen bleibt die dortige Grenze bestehen: Playwright allein genügt nicht, es braucht zusätzlich die native Aufnahme und Rücklese, sonst lautet das Ergebnis `UNKNOWN`.

### Offene Punkte zu den Beschlüssen

**»Bestehende« Sitzung in R003 und G03.** Mit BE01 ist gemeint: eine aus der Bridge gestartete Sitzung. Zu bestätigen von Daniel.

**Kein Overlay, kein Fenster (R118).** R001 und die Baustartprüfung sprechen von einem Overlay. Gelesen wird es als: keine große Fläche und kein eigenes Bridge-Fenster, sondern kleine schwebende Teile über dem Desktop. Daniel hat am 2026-09-20 bestätigt, dass es kein Overlay gibt. Das Wort steht in den Codex-Zeilen weiter, gemeint ist nach R118 keine Fläche.

**GLM und Kimi.** Arbeitsordner (beide `/root`) und die zweite Zeile für GLM in vd1 sind nicht bestätigt.

## 1. Programm, Lieferung und Arbeiten ohne ständige Betreuung

| ID | Forderung | Stand | Quelle | Goal | Nachweis |
| --- | --- | --- | --- | --- | --- |
| R001 | Echtes Windows-Programm/EXE; Overlay über dem tatsächlichen Desktop, keine Homepage | offen · R118 | U513,529,532 | G02 | Paket startet ohne Entwicklungsinstallation; native Aufnahme zeigt echte Programme darunter |
| R002 | Vollständiges versioniertes Paket statt Buildanleitung für Daniel | offen · BE03 | U540,546; ASTRA551 | G02 | Downloadbestandteile, Prüfsumme, Starttest und verständliche Anleitung stimmen überein |
| R003 | Wirklicher Erstkontakt zur bestehenden Agentensession | offen · BE01, Auslegung offen | U540,546; ASTRA551 | G03 | frisches Bild beim Agenten, seine Nachricht im Overlay, Daniels Antwort in genau dieser Session |
| R004 | Agent sieht und benutzt die Bridge während ihrer Weiterentwicklung | offen | U470,472,536 | G03 | nachgewiesene Inspektion und Bedienung der laufenden Version, später bei jeder UI-Etappe |
| R005 | Update, Wiederanlauf und Rückkehr ohne verlorene Einstellungen | offen | ASTRA553,555; JETZT | G03 | zwei Versionen wechseln; fehlerhaftes Update zurücknehmen; Layout und Sessionzuordnung erhalten |
| R006 | Lokale Bedienung funktioniert auch ohne antwortenden Agenten | offen | ASTRA555; JETZT | G05 | offline verschieben, konfigurieren, schließen und Verbindung verwalten |
| R007 | Längerlaufende, abschließbare Arbeitspakete statt ständigem »go« | offen | U217,534,536; JETZT | G01 | jedes Goal besitzt Outcome, Beleg, Grenzen und konkreten Übergabepunkt |
| R008 | Zwischendokumentation, eigene Harness/Skill, sichtbare Tests | offen | U459,462,479,536 | G01 | Verfahren festgelegt; pro Bauetappe reale Evidenz und Zwischenstand, keine bloßen PASS-Etiketten |
| R009 | Frozen-Prototyp, Originale und Legacy-Spuren bleiben erhalten | offen | U281,364,421; V77§13 | G01 | Änderungen nur im Neubau/zugeordneten Planpfad; Herkunft und Backups nachvollziehbar |
| R010 | Namen und Dokumente sind für Daniel verständlich und mit Autoren versehen | offen | U323,327,384 | G17 | Einstieg erklärt zusammengehörige Dateien; absolute Pfade, Provenienz und klare Funktionsnamen |

## 2. Anzeigeorte, Arbeitsziele und echte Terminals

| ID | Forderung | Stand | Quelle | Goal | Nachweis |
| --- | --- | --- | --- | --- | --- |
| R011 | Overlay-Anzeige zwischen Windows, KDE 1 und KDE 2 wählbar | offen | U470 überholt U445 | G06 | dieselbe Konfiguration an allen drei Anzeigeorten; kein neuer Agent durch Anzeigewechsel |
| R012 | Arbeitsziel unabhängig vom Anzeigeort und Empfänger | offen | U424,445,470,556 | G06 | Windows-Raute arbeitet an KDE 2; anderer Agent gleichzeitig auf Windows |
| R013 | Ganzes sichtbares Desktopbild einschließlich Taskleiste, Hintergrund und offenen Programmen bindbar | offen | U443,445 | G06 | Vergleich zu Originalaufnahme für Windows und beide KDE-Arbeitsflächen |
| R014 | Einzelnes Fenster/Browser/Programm/Spiel bindbar; exklusive oder gemeinsame Gates | offen | U346,350,443; V76§2.4 | G06 | zwei getrennte Ziele und ein geteiltes Ziel; unzugehörige Bereiche fehlen beim Empfänger |
| R015 | Fensterscanner unten rechts an jeder Terminalansicht, Dropdown zur Bindung | offen · R120 | U443; SKIZZE | G05 | auswählen, binden, wechseln, lösen; Ziel und Agent sichtbar, verschwundenes Ziel erklärt |
| R016 | Kein automatischer Fenster-Arrange-Zwang im Scanner | offen | U443 | G05 | Binden verschiebt/vergrößert das Originalfenster nicht |
| R017 | Genau dieselbe Original-Terminalsession spiegeln, nicht eine ähnlich aussehende neue Shell | offen · eingeschränkt durch BE01 | U474,477 | G04 | Session-/Prozessidentität und gleichzeitiger Original-/Overlay-Vergleich |
| R018 | Ausgabe, ANSI-Farben, Cursor, Unicode, Scrollback und Vollbild-Terminalprogramme korrekt | offen | U474; ASTRA553 | G04 | identische Referenzfälle mit laufender Ausgabe, Cursor und Alternate Screen |
| R019 | Eingaben, Sondertasten, Einfügen und Größenänderung kommen richtig an | offen | U477; ASTRA553 | G04 | einmalige Probe im tatsächlichen Ziel; Resize und Eingabezustand rückgelesen; keine Doppelzustellung |
| R020 | Terminalansichten auswählen, austauschen, verbinden, individuell verschieben/vergrößern | offen · erweitert durch R114, R115 | U443; SKIZZE | G05 | zwei Ansichten umbelegen; Quelle bleibt eindeutig, laufende Session bleibt erhalten |
| R021 | Agenten auf Wunsch am VPS einbinden/starten; bestehende Sessions wieder anbinden | offen · BE01: zweite Hälfte entfällt; BE02 | U443,558 | G09 | »bestehende verbinden« und »neue starten« unterscheidbar; tatsächliche Runtime-Antwort |
| R022 | Bindungen bleiben bei geschlossenem/neu erzeugtem Fenster eindeutig | offen | PRÜFUNG; aus R012–R020 abgeleitet | G06 | kein Input an wiederverwendetes Handle oder veraltete Terminal-ID |

## 3. Rauten, Regie und tägliche UI

| ID | Forderung | Stand | Quelle | Goal | Nachweis |
| --- | --- | --- | --- | --- | --- |
| R023 | Agentenraute ist der Sprechort des Agenten | offen · R119 | U443,556 | G05 | Agent sendet über seine Session; Raute stellt richtigen Absender und Zielraum dar |
| R024 | Name, Farbe, Hotkey und Position pro Raute einstellbar | offen | U443; V76§2.9 | G05 | zwei gleiche Modellnamen trotzdem unterscheidbare Sessions; Einstellungen nach Neustart |
| R025 | Hotkey-/Modifikator-Eingabe ohne unerwünschten Fokusverlust | offen | U443; V76§2.9 | G05 | gezieltes Öffnen/Schließen; Normalmodus lässt darunterliegende App bedienbar |
| R026 | Gleiches Ereignis als 9,9-s-Box an der Raute, 6,6-s-Fade-Banner und Chatnachricht (Zeiten seit 2026-10-01) | offen | U443; V76§2.9 | G05 | eine Nachrichten-ID in drei Darstellungen; gemessene Zeiten und keine Chatduplikate |
| R027 | Banner räumlich zur Raute orientiert und innerhalb des Zielraums | offen | U443; V76§2.9 | G05 | Fenster bewegen/skalieren, lange Texte und mehrere Sprecher ohne Abdriften |
| R028 | Regie unten links, aufklappbare/scrollbare Sprüche, Ziel und Empfänger vor Versand wählbar | offen | U443; SKIZZE | G05 | einzelner Agent, Gruppe und Zielwechsel; Vorschau des Adressaten, Rückmeldung zur Zustellung |
| R029 | Alle dokumentierten Regiesprüche erhalten | offen | V76§3; U443 | G05 | Weiter so, Mach mal, Go, Warte kurz, Pause/Weiter, Ja/Nein, Denk nach, Denk neu, Konzentrier dich, andere Idee, Undo, Neu scannen einzeln geprüft |
| R030 | Regie-Semantik ehrlich: Gesprächswunsch, Laufpause, Bildpause, Undo und Not-Aus nicht verwechseln | offen | PRÜFUNG; aus R029 abgeleitet | G12 | »Denk nach« stoppt keine fremde Runtime heimlich; tatsächliche Wirkung/fehlende Unterstützung sichtbar |
| R031 | Transparenz jedes Bereichs/Buttons einzeln; 66 % Transparenz als Startwert | offen | U443 | G05 | getrennte Werte bleiben gespeichert; Deckkraft/Transparenz eindeutig; Rücksetzen verfügbar |
| R032 | Keine Skizzen-Erklärungspfeile oder Ersatzdesktop als Dekoration | offen | U443,513; SKIZZE | G05 | Referenzvergleich; eigene später gezeichnete Pfeile bleiben natürlich möglich |
| R033 | Webcam, Raute und Regiemeldungen passend im gebundenen Zielraum | offen | U443 | G07 | Wechsel Desktop→Fenster verändert Platzierung/Adressierung, nicht heimlich die Session |
| R034 | Handlungsorte visuell erkennbar: Agentencursor, Zielrahmen, aktueller Steuerbesitz | offen | V76§2.6,§5 | G10 | ein Agentenindikator entspricht einer echten Bindung/Aktion; kein vorgetäuschter zweiter Hardwarecursor |
| R035 | Verständliche, vollständige Bedienung statt nur vorhandener Buttons | offen | JETZT | G18 | UI-Abnahme UQ01–UQ10 unten, einschließlich Fehler-/Offlinezuständen |

## 4. Sehen, Kamera, Mikrofon und Empfängerschutz

| ID | Forderung | Stand | Quelle | Goal | Nachweis |
| --- | --- | --- | --- | --- | --- |
| R036 | Vision pro Session starten, pausieren, fortsetzen und stoppen | offen | U346; V77§4 | G07 | sichtbarer Zustandswechsel plus Auslieferungszähler; Stop liefert keine neuen Bilder und startet nicht heimlich neu |
| R037 | Start jetzt, ab Checkpoint, Ringpuffer oder gewähltem Bildfolgenpunkt | offen | V76§4.8; V77§4 | G13 | Playhead/Quelle sichtbar; Vergangenheit nicht mit Live verwechselt |
| R038 | Livebild, Einzeldatei, Bildsequenz und Replay als Quellen | offen | U346; V77§4.2 | G07 | jede Quelle ausprobiert; Replay-Checkpoint-Anbindung in G13 ergänzt |
| R039 | Beobachtungseinspeisung und sichtbares Overlay unabhängig schaltbar | offen | V76§4.8; V77§4.3 | G07 | nur sehen, nur anzeigen und beides getrennt getestet |
| R040 | Kamera pro Agent zuschaltbar, PiP frei platzierbar, optional im Gesamtbild | offen | U443; V76§2.2 | G07 | echte Aufnahme nur bei Aktivierung; ausgewählter Empfänger sieht PiP, anderer nicht |
| R041 | Mikrofon individuell geroutet; Push-to-talk bzw. VAD-Weg bedienbar | offen | U443; V76§2.3 | G07 | echte Audiodaten/unterstützte Verarbeitung, Mute und Gerätefehler nachgewiesen |
| R042 | Wahrnehmung ist frisch, begrenzt gepuffert und nach Quelle unterscheidbar | offen | V76§2.10; PRÜFUNG | G07 | Bildalter, Sequenzen, Samplinglücken und Überlast sichtbar; keine Phantom-Livebilder |
| R043 | Gate, einzelner Agent, Daniel, Kombinationen und Ausschlüsse pro Objekt | offen · erweitert durch R113 | U350; V77§6 | G08 | Bild/Text für A, nicht B; Vergleich tatsächlicher Empfänger-Payloads, nicht nur UI-Checkboxen |
| R044 | Privates Material leckt weder in Basis-Capture noch Chat, Replay oder Export | offen | V76§4.9.1; V77§6 | G08 | negative End-to-End-Tests einschließlich bereits sichtbar gerenderter Daniel-Notiz |
| R045 | Sparsamer Betrieb auf Daniels ThinkPad, keine unnötigen Dauerstreams/lokalen Modelle | offen | V76§2.11 | G18 | Ressourcenprofil idle/capture/Kamera/mehrere Agenten auf echtem Gerät; Budgetabweichungen offen |

## 5. Malen, Text, Bilder und gemeinsames Zeigen

| ID | Forderung | Stand | Quelle | Goal | Nachweis |
| --- | --- | --- | --- | --- | --- |
| R046 | Bilddateien hinzufügen, verschieben, skalieren, ausblenden, Transparenz ändern | offen | U346; V77§5 | G08 | reale Datei in Fenster/Gate/Desktop; Persistenz und Audience geprüft |
| R047 | Klick→Text schreiben→Enter; später bearbeiten und verschieben | offen | U558; V76§4.9 | G08 | keine ungewollte Eingabe in darunterliegende Anwendung; Abbrechen möglich |
| R048 | Freihand, Marker, Farben, Strichstärken | offen | U558,560; A559 | G08 | Striche mit Maus zeichnen, ändern, speichern und wieder öffnen |
| R049 | Linien, eigene Pfeile, Rechtecke, Kreise und schnelle geometrische Formen | offen | U558,560; A559 | G08 | Auswahlwerkzeuge tatsächlich bedienbar, Objekt statt eingebranntem Wegwerf-Pixel |
| R050 | Einzel-/Mehrfachauswahl, Gruppierung, Reihenfolge, Resize, Undo/Redo | offen | U558,560; A559 | G08 | mehrere Objekte gemeinsam bewegen; Undo betrifft richtige Ebene, nicht die Zielapp |
| R051 | Bleibt so lange gewünscht im gebundenen Gate; dort frei beweglich | offen | U558,560 | G08 | weder Banner-Timer noch Agenten-Zielwechsel entfernt die Zeichnung ungefragt |
| R052 | Zeigegeste enthält gemeinten Ort, Ziel und damaligen Bildbezug | offen | A557; U558,560 | G11 | nach Layoutwechsel Warnung/Neuauflösung statt blindem Klick auf alte Koordinaten |
| R053 | Inhaltshaftung, wo zuverlässig verfügbar; sonst erkennbare Fensterbindung | offen | A559; U560 korrigiert Priorität | G11 | Scroll-/Resize-Test mit echtem Anker; fehlende Erkennung bleibt sichtbar statt vorgetäuscht |
| R054 | Darstellung getrennt von echter Einfügung in die Anwendung | offen | V76§4.10; V77§5.3 | G11 | Overlay verändert App nicht; ausdrücklich gewählte Einfügung hat eigenen Ergebnisbeleg |

## 6. Mehrere Agenten und wirkliche Hände

| ID | Forderung | Stand | Quelle | Goal | Nachweis |
| --- | --- | --- | --- | --- | --- |
| R055 | Mehrere Sessions desselben Modells gleichzeitig, getrennte Aufgaben/Chats/Rauten | offen | U558 | G09 | zwei Codex-/andere gleichartige Sessions bleiben bei Reconnect unterscheidbar |
| R056 | Eltern-/Subagent-Beziehungen, Gruppenwahl, Auftrag, Status und Ergebnis | offen | U558; A559 | G09 | realer unterstützter Subagent mit Parent und Rückgabe; nicht steuerbare Kinder klar markiert |
| R057 | Einzelne/Gruppe verbinden, ansprechen, beobachten, pausieren und beenden soweit Runtime unterstützt | offen | U558,560; A559 | G09 | Capability-Matrix gegen echte Adapter; fehlende Pause nicht als ausgeführt melden |
| R058 | Codex, Gemini, Claude, Kimi und GPT als unterscheidbare Teilnehmer anbinden | offen · BE02 | V76§1,§2.8; U295 | G09 | echte erlaubte Adapterwege, keine Attrappen; bestehende Kimi-Betriebsgrenzen erhalten |
| R059 | ChatGPT/MCP mit ehrlichem Inspect/Act/Status und sichtbaren Arbeitsmeldungen | offen · R116, R117 | V76§2.8; PRÜFUNG | G09 | tatsächlicher Host erhält Bild/Status und unterscheidet Fehler von Erfolg; kein Versprechen über verborgenes Denken/Chatdarstellung |
| R060 | Gemeinsames Gate und private Kommunikation, inklusive Agent→Agent | offen | U350,424; V76§2.9 | G09 | drei Empfänger, richtige Zustellung und keine Selbst-Echo-Endlosschleife |
| R061 | Agenten parallel auf Windows und Linux, ohne fremden Fokus/Input zu übernehmen | offen | U424 | G10 | zwei gleichzeitige reale Aufgaben, getrennte Ziel-/Eingabespuren |
| R062 | Maus/Tastatur-Handlungen einschließlich Klicken, Tippen, Ziehen und Hotkeys | offen | V76§2.6,§4 | G10 | sichtbare Vor-/Nachher-Wirkung in ungefährlicher echter App je Plattform |
| R063 | Hintergrundbedienung, wo unterstützt; Shared-Mouse-Lease als eigener Modus | offen | V76§2.6 | G10 | Fähigkeiten pro App nachgewiesen; Fallback sichtbar, kein heimlicher Cursor-/Fokusdiebstahl |
| R064 | Virtuelle Controller und Hybrid Mensch+Agenten als wählbare Adapterfähigkeiten | offen | V76§2.6 | G10 | Treiber-/Geräteprüfung; mehrere getrennte Controller, Ziel bis vier; Hybrid-Eingabe in geeignetem Test |
| R065 | Menschlicher Eingriff hat Vorrang; ausdrücklich wählbare freiere Autonomie | offen | V76§2.5; U336 | G10 | Override und gewählte Ausnahme getrennt testen; Not-Aus gilt in beiden |
| R066 | Lokaler Not-Aus/F12, sichtbarer Stop, Fehler-/Disconnect-Abbruch | offen | V76§5; PRÜFUNG | G10 | auch bei UI-Hänger/Netzausfall; gedrückte Tasten freigeben; gemessene statt erfundene Latenz |
| R067 | Zielkäfig, Lease, Koordinaten/DPI, Rechte, Fokus und Aktualität berücksichtigen | offen | V76§2.4; B78§3,6 | G10 | veraltetes/unerlaubtes/falsches Ziel blockiert; positive Aktion separat belegt |
| R068 | Kein verspätetes Wiederabspielen alter Eingaben nach Reconnect | offen | PRÜFUNG; ASTRA553 | G03 | verzögerte/duplizierte Nachricht verursacht keine zweite oder nachträgliche Mutation |

## 7. WorldDOM, selbstentworfene Brücken und Freiheit

| ID | Forderung | Stand | Quelle | Goal | Nachweis |
| --- | --- | --- | --- | --- | --- |
| R069 | Echte DOM-/Accessibility-Struktur zusätzlich zum Screenshot nutzen | offen | U355; V77§7 | G11 | echte Strukturquelle mit Herkunft, Geometrie und aktueller Auflösung |
| R070 | Auch ohne nativen DOM: aus Bild erschlossene und bewusst erfundene Knoten/Kanten | offen | U355; V76§4.12 | G11 | Canvas-/Bildbeispiel mit inferred/authored/projected; Konfidenz und Grenzen sichtbar |
| R071 | Semantischer Auftrag wird zur konkreten Handlung mit Ergebnisrücklese | offen | V76§4.12; V77§7.2 | G11 | benannten Knoten auflösen, handeln, Wirkung prüfen; ungelöster Knoten bleibt ungelöst |
| R072 | Python-Harness aus Zuständen, Aktionen, Kanten, Guards, Witnesses, Fallbacks und Checkpoints | offen | U338,341; V76§4 | G12 | echter mehrschrittiger Workflow verzweigt bei geändertem Zustand und ist pausierbar |
| R073 | Agenten entwerfen, ändern, speichern und wiederverwenden eigene Teilbrücken | offen | U338; V76§4.1–4.7 | G12 | Agent erzeugt ausführbaren Graph, Version bleibt sichtbar, geänderter Durchlauf überschreibt Original nicht |
| R074 | Gemeinsame Arbeit/Delegation mit Zustand, Verlauf, Grund und Unsicherheit | offen | V76§4.6; U336 | G12 | realer Handoff an zweite Session mit nachvollziehbarer Fortsetzung |
| R075 | Freier Modus ohne zusätzliche Einzelklick-Bestätigung; optionale Profile einzeln | offen | U336; V77§8.2 | G12 | free/shadow/witness/daniel_gate/learning/delegated_learning getrennt bzw. kombiniert; lernen initial aus |
| R076 | Vorschau, Ausführung, Pause, Fortsetzen, Abbruch, Replay klar getrennt | offen | V76§4; B78§6 | G12 | Replay führt nichts in Live-App aus; Stop hält weitere Knoten an |
| R077 | Loops, Automationen und Goals mit Start/Stop/Budget/Fortschritt | offen | U357; B78§6 | G15 | wiederkehrender Auftrag läuft begrenzt, pausiert, beendet sich mit echtem Ergebnis |
| R078 | Neue Abläufe ohne neuen EXE-Build nutzbar, soweit keine neue Plattformfähigkeit nötig ist | offen | ASTRA555; U338 | G12 | neuen deklarativen Graph laden und benutzen, gleiche Clientversion |

## 8. Zeit-Scrubber und Momentkapseln

| ID | Forderung | Stand | Quelle | Goal | Nachweis |
| --- | --- | --- | --- | --- | --- |
| R079 | Letzte Sekunden durchgehen, Zeitpunkt wählen, neuen Versuch/Analysezweig beginnen | offen | U336,558; V77§9 | G13 | Original erhalten, neuer Branch referenziert Start; Livezustand vor neuer Aktion frisch prüfen |
| R080 | Snapshot einzelner oder mehrerer Fenster/Gates/Agenten/Zeitabschnitte | offen | U558 | G13 | Mehrfachauswahl speichert genau diese Auswahl, keine fremden Quellen |
| R081 | Arbeitszustand umfasst Terminal, Tools/Resultate, Auftrag/Plan/Richtung, geteilte Bemerkungen | offen | U560 | G13 | Kapsel enthält tatsächlich verfügbare Ereignisse mit Quelle/Zeit und sichtbaren Lücken |
| R082 | Chat, Rauten-/Bannermeldungen, Bilder, Zeichnungen und Bindungen gemeinsam aufbewahren | offen | U558,560 | G13 | spätere Ansicht rekonstruiert den damaligen Arbeitsmoment ohne Live-Verwechslung |
| R083 | Frei erweiterbare Mehrfachkategorien: Idee, Verwirrung, Fehler, Lösung, Umweg usw. | offen | U558,560; A559 | G13 | eigene Kategorie anlegen, mehrfach zuordnen, wiederfinden |
| R084 | Später gemeinsam ansehen, annotieren, vergleichen und Lernstrecken bilden | offen | U558,560; A559 | G13 | zwei Kapseln vergleichen und kommentieren; Original-Hashes unverändert |
| R085 | Fehlversuche und schmutzige Umwege ausdrücklich erhalten | offen | U558 | G13 | gescheiterter und erfolgreicher Pfad gleich gut auffindbar, nichts automatisch schöngeschrieben |
| R086 | Aufgezeichnete Beobachtung statt erfundener Totalzustand/verborgener Gedanken | offen | U560; PRÜFUNG | G13 | Aufnahmeinventar benennt fehlende Quellen; keine behauptete beliebige App-Wiederherstellung |

## 9. Hauhaucs und das Kontext-Mischpult

| ID | Forderung | Stand | Quelle | Goal | Nachweis |
| --- | --- | --- | --- | --- | --- |
| R087 | Vorhandene Hauhaucs-Chatinstanz anbinden; Hintergrundinstanz der Wesen unberührt | offen | U562 | G14 | tatsächlicher Endpunkt/Sessionpfad geprüft; keine Änderung an Hintergrundbetrieb |
| R088 | Aufnahme ohne Modell; optional aktives Mitlesen und »jetzt dokumentieren« | offen | U560,562; A563 | G14 | Aufzeichnung funktioniert ohne Inferenz; Modellmodus verarbeitet gewählte Ausschnitte |
| R089 | Zwei/drei Agenten mitlesen, Quellen unterscheidbar, Aufnahme-/Lese-Cursor sichtbar | offen | U560; A563 | G14 | ausgewählte Ereignisse vollständig zuordenbar; ungelesener Rest nicht als gelesen angezeigt |
| R090 | Neue Session mit tatsächlich leerem Systemprompt, eigene benennbare Zusatzfelder | offen | U564,567; A569 | G14 | effektiven Request prüfen, keine verborgene Standardpersönlichkeit/Alt-Zusatzfelder |
| R091 | Prompt schreiben, schalten, ansehen, importieren/exportieren; Einmalfeedback und Ausgabegrenzen | offen | U567; A569 | G14 | Vorschau entspricht gesendetem Request; Feedback genau einmal, Grenzen erkennbar |
| R092 | Kontextanzeigen gesamt/je Nachricht, Schätzungen von Server-Tokenwerten trennen | offen | U567; A569 | G14 | Anzeige gegen Request und Serverbericht prüfen; keine falsche Präzision |
| R093 | Kontext leeren/halbieren, beliebige Nachrichten wählen, einzelne Sätze entfernen, zurückspringen | offen | U567; A569 | G14 | nach Speichern/Neuladen genau gleiche Auswahl/Änderung; Archiv erhalten |
| R094 | Text und mehrere MD-/Textdateien einspeisen ohne sofortige Antwort | offen | A569; U567 | G14 | Material im Kontext, kein unerwünschter Inferenzaufruf |
| R095 | Sessions benennen, speichern/laden, archivieren, importieren/exportieren; flüchtige Geister-Session | offen | U564,567; A569 | G14 | Isolation und Persistenz; flüchtige Session klar kenntlich |
| R096 | Beobachtung stoppen oder am gewählten Kontext-/Tokenbudget beenden; Bilder separat optional | offen | U560 | G14 | keine weiteren Modellaufrufe nach Stop; Kontextkürzung transparent, Dokumentation mit Quellen |

## 10. Wissen pflanzen, Tragbarkeit, Android und Gesamtende

| ID | Forderung | Stand | Quelle | Goal | Nachweis |
| --- | --- | --- | --- | --- | --- |
| R097 | Wissen in gewählten laufenden Kontext/Gate pflanzen und gezielt verteilen | offen | U357; V77§10 | G15 | gewünschter Empfänger erhält Seed, ungewählter nicht; Herkunft bleibt erhalten |
| R098 | MD-/Memory-/Agentenstart-/Skill-Ziele separat und mit konkreter Freigabe bearbeiten | offen | U357; V77§10 | G15 | zieltypgerechter Vorschlag/Patch, Rücklese, keine fremden Heime überschrieben |
| R099 | Erfahrung→Seed→Skill/Harness/Loop/Automation/Goal entwickeln | offen | U336,357; V77§10 | G15 | eine wirkliche Erfahrung wird wiederverwendbare Fähigkeit; kein behauptetes Modelltraining |
| R100 | Seeds vorschlagen, aktivieren, zurückziehen, versionieren und exportieren | offen | V77§10 | G15 | Lebenszyklus bedienbar, Originalquelle und aktive Ableger nachvollziehbar |
| R101 | Windows/Linux-Kern später auf Android mit Capture, Overlay, Touch/Gesten erweitern | offen | U388,400; DREAM§3 | G16 | reale Geräteaufnahme, mobile Bedienung, Rotation/Stop/Verbindung und gleiche Sessionsemantik |
| R102 | Android/Gord: gemeinsames Beobachten, Calls, Kommunikation und spätere Matchanalyse | offen | U388,408; DREAM§4 | G16 | mobile Team-Kommunikation und wiederöffnbarer Spielmoment; keine erfundenen unsichtbaren Gegnerdaten |
| R103 | Daniels zusätzliche Handlungsvision: Flicker/Spell 1/2, niemals Ult oder Steuerknüppel; auch Ranked genannt | offen | U390,392,394,400 | G16 | Wünsche nicht auf Coaching verkürzt; getrennte Aktionen mit Negativbelegen für Ult/Steuerknüppel; Live-Einsatz nicht durch diesen Plan aktiviert |
| R104 | Vollbetrieb, Sparbetrieb, Archiv/Schlaf und Wiedererweckung | offen | U366,370,372; V77§11–12 | G17 | ohne bezahlte Laufzeit lesbares Archiv; später Start aus exportiertem Zustand |
| R105 | Vollständige Rohsicherung und sortierte Ableitung, einschließlich alter MD/Python/JSON-Spuren | offen | U364; V77§11.3 | G17 | Manifest/Prüfsummen, unveränderte Rohkopie; keine Löschung als impliziter Schritt |
| R106 | Migration samt Git, Datenbanken, Entitäten/Selbstmodellen, Memories, Skills, Loops/Goals und Services | offen | U370; V77§11.4 | G17 | Wiederherstellung auf isoliertem frischem Ziel mit Startreihenfolge und Datenvergleich |
| R107 | Konfiguration, Abhängigkeiten, CPU-/GPU-Profile und getrennt geschützte Secrets | offen | V77§11–12 | G17 | Preflight zeigt fehlende Hardware/Secrets; keine Geheimnisse im öffentlichen Bundle |
| R108 | Anbieterwechsel/Abopause löscht weder Erinnerung noch offene Aufgaben | offen | U372; V77§12 | G17 | Adapter fällt aus, Daten bleiben nutzbar; Austausch verliert keine Provenienz |
| R109 | Rechtzeitig vor möglichem VPS-Ende migrationsfähig; USB-Archiv als geplanter Weg | offen | U364,366,370 | G17 | relativer Wunsch »ca. drei Monate vorher« dokumentiert; realer Vertragstermin vor Terminierung prüfen |
| R110 | Open-Source-fähiges Paket mit Installation, Demo, Lizenz-/Abhängigkeitsprüfung und Beitragsdoku | offen | U360; V77§13; DREAM§13 | G17 | frischer Installations-/Restorelauf, private Daten getrennt; Veröffentlichung erst auf Auftrag |
| R111 | Alle Funktionen zusammenhängend statt lose Einzel-Demos | offen | JETZT | G18 | End-to-End-Szenarien E01–E10 des Goal-Plans plus alle Registerzeilen belegt |
| R112 | Gute UI nicht erst am Ende: in jeder Etappe richtige Platzierung, klare Zustände, Fehlerrückmeldung | offen | U443,462,470; JETZT | G18 | UQ-Kriterien gelten fortlaufend; Endabnahme prüft nochmals das Zusammenspiel |

## 11. Ergänzungen vom 2026-09-20

Neue Zeilen nach dem Gespräch D0920. Die Forderungen geben Daniels Aussagen wieder; die Nachweise sind Vorschläge von Claude und keine Daniel-Zitate.

| ID | Forderung | Stand | Quelle | Goal | Nachweis |
| --- | --- | --- | --- | --- | --- |
| R113 | Jedes Objekt (Text, Bild, Zeichnung, Chat, Terminal) hat zwei voneinander unabhängige Einstellungen: Ort (Daniels Desktop oder im Gate) und Sichtbarkeit (je Teilnehmer des Gates einzeln wählbar) | offen | D0920 | G08 | Ort und Sichtbarkeit einzeln ändern; die tatsächlichen Empfänger-Payloads stimmen mit der Einstellung überein |
| R114 | Terminals der Bridge sind schwebende oberste Fenster auf Daniels Desktop; jedes ist einzeln ein- und ausschaltbar und minimierbar | offen | D0920 | G05 | Terminal ausblenden, minimieren und wieder einblenden; die Sitzung läuft dabei unverändert weiter |
| R115 | Jedes einzelne Terminal lässt sich in das Gate seines Agenten stecken; wer es dort sieht, wird je Teilnehmer gewählt | offen | D0920 | G06 | Terminal in ein Gate stecken und wieder herausnehmen; nur die gewählten Teilnehmer sehen es; die Sitzung bleibt dieselbe |
| R116 | Der ChatGPT-Chat löst nichts aus. Er ist für alle Teilnehmer desselben Gates lesbar; ob er für einzelne unsichtbar geschaltet werden kann, ist offen — falls ja, individuell wählbar | offen | D0920 | G06.5 | Eine normale Chatnachricht erzeugt keinen Tool-Aufruf; Sichtbarkeit je Teilnehmer gegen die tatsächlichen Empfänger geprüft; kein Leck über Replay oder Export (R044); Machbarkeit der Unsichtbarschaltung entschieden und festgehalten |
| R117 | ChatGPT hat ein eigenes Anti-Terminal und daneben eine zweite Chatbox | offen | D0920 | G06.5 | Anti-Terminal und Chatbox sind getrennt verschiebbar; das Anti-Terminal zeigt Sitzung, Turn, Ziel und Beleg, die Chatbox den Chat |
| R118 | Kein Overlay als Fläche und kein eigenes Bridge-Fenster; die Bridge besteht aus kleinen schwebenden Teilen | offen | D0920 | G02 | Native Aufnahme zeigt kein vollflächiges Fenster; freie Bereiche lassen Eingaben durch |
| R119 | Eine Raute erscheint nur für einen Agenten, der in der Bridge gestartet wurde | offen | D0920 | G05 | Ohne gestarteten Agenten keine Raute; nach dem Start aus der Startliste erscheint genau seine Raute |
| R120 | Standardziel ist der komplette Desktop, ungebunden; gesehen und gesendet wird erst, wenn im Fensterscanner etwas gebunden ist | offen | D0920 | G06 | Beim Start ist der Desktop Ziel und ungebunden; erst nach der Bindung kommen Bilder beim Agenten an |
| R121 | Ort jedes einzelnen Bridge-Elements bei gebundenem Zielfenster: Ist als Ziel kein ganzer Desktop gebunden (z. B. ein Chromium-Browser), gibt es neben dem Scanner-Knopf einen Schalter je Element (Raute, Terminal, Chat, Regieleiste, Selbstbild …): auf dem ganzen Desktop bleiben oder in das Zielfenster. Im Zielfenster ist das Element eingerahmt, es lässt sich nur dort bewegen, wandert beim Verschieben des Zielfensters an derselben Stelle mit, wird mit dem Zielfenster minimiert und verschwindet, wenn das Zielfenster geschlossen wird | offen · konkretisiert durch R113/R115 | Daniel 2026-10-01 | G05.5 | Je Element einzeln schaltbar; Zielfenster verschieben (Element geht mit), minimieren (Element mit), schließen (Element weg), wiederherstellen (Element wieder da); ein Element auf „Desktop“ bleibt davon unberührt |
| R122 | Schalter „nur Terminal“ je Agent und für alle gleichzeitig (wählbar): ausgeschaltet werden Bilder (Bilderstrom), Hände, Kamera und der Rautenchat samt Banner und Box (es kann ohne Bilder kein Gegenlesen stattfinden); das Mikrofon bleibt ausdrücklich an. Der Agent läuft als normaler Terminal-Agent weiter, Einschalten stellt alles wieder her. Zu erreichen über einen Knopf im Terminalbereich und über Rechtsklick auf die Raute | offen | Daniel 2026-10-01 | G05.5 | Schalter aus: keine Bilder, keine Hände, keine Kamera, kein Raute-Banner und -Chat für diesen Agenten, Mikrofon läuft weiter, Terminal läuft unverändert; Schalter an: alles wieder wie vorher; „für alle“ schaltet alle Agenten gleichzeitig |
| R123 | Daniels Erwartung an ein gebundenes Zielfenster: Der Agent soll in einem gebundenen Browser, Spiel oder Programm sehen und handeln können, egal wie groß oder klein, wo, verdeckt oder minimiert das Fenster ist (so war es bei Playwright & Co. auf dem virtuellen Desktop). Entscheidung 2026-10-01: Umsetzung als Kombination (Browser über CDP, normale Programme über UI Automation, übrige über Fensteraufnahme und optional virtuellen Monitor); „minimiert“ ist Daniel nicht wichtig; Vorrang hat R124 | offen · Entscheidung getroffen, Machbarkeit je Baustein zu belegen | Daniel 2026-10-01 | G06.7 | Je Fensterzustand (klein, verdeckt, minimiert) dokumentiert, ob Bild und Eingabe ankommen und mit welchem Verfahren; klar benannte Grenzen statt Versprechen |
| R124 | Mehrere Agenten, mehrere Fenster, ein Bildschirm: Daniel arbeitet an einem Laptop mit einem Bildschirm und legt z. B. ein Spiel im Fenstermodus an eine Stelle, einen Browser daneben (anderer Agent) und ein Programm darunter (wieder ein anderer), wie in der Skizze. Jeder Agent bekommt immer das **vollständige Bild seines eigenen gebundenen Fensters (Gate)**, auch wenn ein anderes Fenster oder Daniels Arbeit es teilweise verdeckt. Fensterzustand „minimiert“ ist dafür ausdrücklich nicht wichtig | offen | Daniel 2026-10-01 | G06.7 | Zwei Zielfenster nebeneinander und eines teilweise verdeckt: jeder Agent bekommt das ganze Bild seines Fensters ohne fremde Pixel; je Agent eigene Bildfolge; Eingaben gehen nur an das Fenster des jeweiligen Agenten |
| R125 | Daniels Eingabe ist von der Eingabe der Agenten **entkoppelt**, wählbar neben den bestehenden Modi (Vorrang für Daniel, geteilte Maus, volle Autonomie): Daniel schreibt, spielt oder surft, ohne dass die Agenten dazwischenfunken, und die Agenten ignorieren seine Eingaben. Jeder Agent bekommt in seinem Gate einen eigenen sichtbaren, nur gezeichneten Zeiger (aus `ERLEBEN.md`: farbige virtuelle Zeiger mit Namen); wo ein Weg ohne echten Zeiger möglich ist (Browser über CDP, UI Automation, virtuelle Controller), handeln die Agenten parallel ohne Warteschlange. Wo nur echte Maus und Tastatur gehen, gilt eine Regel für den gemeinsamen Zeiger (Warteschlange mit kurzen Leasen) oder der Weg bleibt dem Agenten verwehrt | offen · Machbarkeit je Programmart zu belegen | Daniel 2026-10-01 | G06.7, G10 | Daniel tippt in einem Fenster, während ein Agent in einem anderen klickt oder tippt: keine Eingabe landet im falschen Fenster, der Cursor springt nicht; je Programmart (Browser, Standardprogramm, Spiel) ausgewiesen, welcher Weg gilt |

## UI-Qualität: Was »menschlogisch nutzbar« konkret bedeutet

Diese Kriterien sind Codex' prüfbare Übersetzung, kein Anspruch, Geschmack durch ein Testskript abschließend messen zu können.

Daniels abschließender Blick auf die tatsächliche UI bleibt Teil der Abnahme.

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

## Konflikte und fehlende Eindeutigkeit — bleiben sichtbar

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

Die frühen Crash-/Sicherheitsfix-Nachrichten, Scherze über Codex, die Song-Anfrage und reine »go«-/Dankes-/Statusnachrichten sind nicht eigenständige Bridge-Funktionen.

Wiederholungen verstärken Anforderungen, erzeugen keine künstlichen Duplikate. Wortlautarchiv, Autorenschaft, verständliche Titel, Sicherung und Dokumentation bleiben Arbeitsanforderungen (R008–R010), keine zusätzlichen Produktfunktionen.

U313 erwog Löschen; U364 und U421 legen später ausdrücklich Erhalten/Neubau fest. Der Prototyp wird nicht gelöscht.

2.dbrain/Schrottplatz dürfen als Nutzungszentrum abgelöst werden, ihre Daten bleiben Herkunft (R009/R105).

Ein 4-TB-Stick und eine Gigabitleitung sind Daniels geplanter Transportweg, keine jetzt vorhandene Infrastruktur und keine Aufforderung, Hardware zu kaufen.

## Vollständigkeit und Statuspflege

Die Tabelle deckt die hier ausgewerteten Produktanforderungen ab, nicht eine mathematische Garantie, dass kein Gesprächsdetail übersehen werden kann.

Bei neu gefundenem Detail: Quelle angeben, bestehender ID zuordnen oder neue hinzufügen; keine stille Änderung des Wortlautarchivs.

Jede Abnahme nennt Build/Plattform/Datum/Belegpfad. `offen`, `implementiert`, `integriert`, `belegt` und `von Daniel abgenommen` bleiben unterschiedliche Zustände.

Ein offener Adapter oder fehlender Gerätezugang darf ein einzelnes Goal tatsächlich aufhalten. Er darf weder als Erfolg zählen noch die betreffende Anforderung aus dem Gesamtziel verschwinden lassen.

Die vollständige Bridge ist erst fertig, wenn alle obligatorischen Zeilen und UI-Kriterien belegt sind; verbleibende Grenzen müssen ausdrücklich mit Daniel entschieden werden, nicht einseitig mit dem Etikett »später« aus dem Umfang genommen werden.
