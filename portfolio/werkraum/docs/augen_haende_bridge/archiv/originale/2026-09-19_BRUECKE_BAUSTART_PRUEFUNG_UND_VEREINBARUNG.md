---
datum: 2026-09-19
autor: codex bei Daniels VPS
herkunft: Daniels Anforderungen im Gespräch; Codeprüfung und technische Quellen durch Codex
status: Prüfung abgeschlossen; native Produktabnahme offen
---

# Augen & Hände — Baustartprüfung und gemeinsame Leitplanken

## Ergebnis und Geltung

Die Idee ist hinreichend klar für einen schmalen ersten Bauabschnitt. Der vorhandene Stand ist aber **keine fertig verbundene Windows-Bridge**. Browserbeweise belegen Browserfunktionen, nicht die native EXE. Ein getesteter Windows-Build-, Auslieferungs- und Rückkanal ist noch nicht nachgewiesen. Die Gesamt-Goalliste folgt erst nach dieser Prüfung; dieses Dokument startet keinen Goal und keine Implementierung.

Bei Widersprüchen zu älteren Bauanweisungen gilt diese datierte Korrektur für den nächsten Bauabschnitt. Daniels Wortlaut bleibt die Anforderungsquelle. Vorschläge von Codex werden dadurch nicht nachträglich zu Daniels Entscheidungen. Die früheren Dokumente und der eingefrorene Gemini-Prototyp bleiben erhalten.

## Was Daniel festgelegt hat

- Ein echtes Programm mit EXE und Overlay, keine Homepage und kein nachgebauter Desktop. Freie Bereiche dürfen die Bedienung darunter nicht blockieren.
- Anzeigeort, Arbeitsziel, Session und Empfänger sind getrennt. Das Overlay soll zwischen Windows und KDE-Desktop 1/2 umschaltbar sein; unterschiedliche Agenten können gleichzeitig unterschiedliche Arbeitsziele benutzen. Das ist Zielumfang, nicht bereits geliefert.
- Ein Zielwechsel ersetzt keine CLI-Session. Mehrere Instanzen desselben Modells und Eltern-/Subagent-Beziehungen müssen unterscheidbar sein.
- Die Raute ist der Sprechort des Agenten. Name, Farbe und Hotkey sind einstellbar. Eine Nachricht erscheint neben der Raute für 6,6 Sekunden, räumlich als ausblendendes Banner für 3,3 Sekunden und dauerhaft im zugehörigen Chat.
- Regie sowie Mikrofon-/Kamerabedienung unten links; Scanner am Terminal unten rechts. Beschriftungspfeile in der Skizze sind keine dekorativen Datenleitungen. Mikrofon und Kamera sind einzeln pro Agent zuschaltbar.
- Einzelfenster und kompletter sichtbarer Desktop sind bindbar. Terminalansichten sollen dieselbe echte Session abbilden und bedienen, einschließlich Cursor, Farben, Größenänderung und Eingaben — nicht nur Textkopien.
- Transparenz und Darstellung sind individuell einstellbar. Arbeitsannahme für den Start: »66 % transparent« bedeutet 34 % Deckkraft. Die Einstellung muss beide Begriffe eindeutig machen; der bestehende Wert 0,94 erfüllt das nicht.
- Bilder, Texte, Freihandzeichnung und geometrische Formen gehören in den gewählten Gate-/Zielraum; verschiebbar, mit einzeln einstellbarem Empfängerkreis. Rückgängig und Wiederbearbeiten gehören zur brauchbaren Bedienung. Automatisches Haften an beliebigem Bildinhalt ist eine zusätzliche Fähigkeit, keine zugesicherte Universalwirkung.
- Bilderzufuhr und Beobachtung müssen explizit start- und stoppbar sein. Lernen ist standardmäßig aus, später individuell bis hin zu freierer Zusammenarbeit zuschaltbar. Umwege und Fehler sind Lernmaterial, nicht nur Erfolge.
- Kapseln bewahren ausgewählte Momente mehrerer Fenster, Agenten oder Zeitabschnitte: Bilder, sichtbare Terminalausgaben, tatsächlich verfügbare Toolaufrufe und Ergebnisse, geteilte Pläne/Bemerkungen, Chat, Rautenmeldungen und Markierungen. Kein Versprechen, verborgene interne Gedanken oder beliebige Programmspeicher zu kopieren.
- Hauhaucs darf als zusätzliche Chat-/Beobachtungssession hinzukommen, mit leerem bzw. selbst geschriebenem Systemprompt und sichtbarer Kontextpflege. Die bestehende Hintergrundinstanz der Entitäten wird dafür nicht umgebaut.

## Nachgeprüfte Befunde

### 1. Browser-Abnahme wurde zu weit ausgelegt

`/root/werkraum/augen_haende_bridge/tests/evidence/B4_6_REFERENCE_SURFACE_EVIDENCE.md` enthält `OUTCOME: PASS` und behauptet zugleich, die dargestellte Browseransicht sei bereits die räumliche Windows-Bridge. Die aufgeführten DOM-/Playwright-Prüfungen tragen diese zweite Behauptung nicht. Historisches PASS bleibt als Browser-Testresultat erhalten; native Produktabnahme: **offen**.

### 2. Der native Entwurf ist noch kein tragfähiges Overlay

`/root/werkraum/augen_haende_bridge/client_windows/overlay_app.py` setzt ein bildschirmfüllendes Tk-Fenster mit Deckkraft 0,94 auf. Freie, klickdurchlässige Bereiche und selektiv bedienbare Overlay-Elemente sind dort nicht nachgewiesen. Es gibt fest gezeichnete Beziehungspfeile, Terminalkarten statt vollständiger Terminaldarstellung und lokale Zustandswechsel für Mikrofon/Kamera statt belegter Aufnahme.

Zeile 64 ruft `self.root.wm_class(...)` auf; der umgebende Handler fängt nur `tk.TclError`. Read-only-Prüfung mit `hasattr(tk.Tk, "wm_class")` ergab `False`. Damit liegt ein konkreter API-Fehler im Startpfad vor. Das ist ein statischer Befund plus lokale API-Prüfung, **kein durchgeführter Windows-Starttest**.

F12 ist dort nur an den Tk-Eventloop gebunden. Ein systemweiter, vom hängenden UI unabhängiger Not-Aus ist damit nicht bewiesen.

### 3. Terminal-Erkennung ist noch keine Terminal-Parität

`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/target_registry.py` fragt lokal den Konsole-Adapter ab; eine Windows-Instanz erhält dadurch nicht automatisch VPS-Terminals. Windows und KDE-Ziele stehen ausdrücklich auf `unavailable`. Terminal-IDs entstehen aus der Entdeckungsreihenfolge, und verschwundene Einträge werden beim Refresh nicht entfernt. Für dauerhaft sichere Bindungen fehlen stabile Identität und Lebenszyklusbehandlung.

`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/terminal_adapter.py` liest dargestellten Text. Das beweist weder einen vollständigen VT-Terminalzustand noch Eingaben in die ursprüngliche Agentensession. Das isolierte Probe-Terminal in `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/probe_terminal.py` bleibt ein anderer Testgegenstand.

Eine zunächst vermutete unmittelbare Windows-Importsperre durch `pty` wurde **nicht bestätigt**: Der Import steht in einem eingebetteten Wrapper-String, nicht als sofort ausgeführter Modulimport. Der Wrapper selbst ist Unix-spezifisch. Keine erfundene Importfehlermeldung in den Bauplan übernehmen.

### 4. Auslieferung ist offen

`/root/werkraum/augen_haende_bridge/client_windows/build_exe.bat` installiert PyInstaller ohne feste Version, prüft Fehler nicht ausdrücklich und meldet am Ende unabhängig vom Erfolg einen Paketpfad. `--onedir` erzeugt ein Verzeichnis-Bundle: Die EXE allein ist nicht das vollständige Paket. Im durchsuchten Greenfield-Verzeichnis wurde keine EXE gefunden.

Wine ist in dieser Umgebung vorhanden; das ist weder ein Windows-Buildnachweis noch ein Test auf Daniels Windows. Es wurde kein neuer Runner angelegt, kein fremder Wine-Prefix verändert und kein Release veröffentlicht.

### 5. Alte Skill-Garantien sind keine Messwerte

Der ursprüngliche Skill `/config/.agents/skills/augen-und-haende-bridge/SKILL.md` verbindet gute Ziele mit unbelegten Zusagen: Not-Aus unter 1 ms, Disconnect-Stopp unter 10 ms trotz 1-s-Heartbeat, exakt 12 ms Cursorleihe, null VRAM/Idle-CPU und garantierte RAM-Grenzen. Diese Zahlen dürfen nicht als funktionierende Eigenschaften oder universelle Abnahmekriterien weitergetragen werden.

Ein Abtastraster von 10 Hz garantiert keine lückenlose Beobachtung. KDE-Arbeitsflächen sind nicht automatisch verschiedene X11-Displays. Ein gepostetes Windows-Ereignis ist kein Beweis, dass eine Anwendung es ausgeführt hat. Hardware-/Frameworkwahl bleibt von gemessenen Fähigkeiten abhängig.

## Technische Recherche: Konsequenzen, keine Zauberrezepte

- PyInstaller ist kein allgemeiner Cross-Compiler. Der Windows-Build braucht eine passende Windows-Umgebung; Wine kann untersucht werden, ersetzt aber keine native Abnahme. Quelle: https://pyinstaller.org/en/stable/ und https://www.pyinstaller.org/en/stable/usage.html
- Bei Win32-Layered-Windows hängen Hit-Tests von Form/Transparenz und Fensterstilen ab. Ein pauschal transparentes Fenster ist nicht gleichbedeutend mit »Buttons bedienbar, Zwischenräume durchlässig«. Das muss als native Probe entschieden werden. Quelle: https://learn.microsoft.com/en-us/windows/win32/winmsg/window-features
- `PostMessage` stellt Nachrichten in eine Queue; UIPI begrenzt den Zugriff. Erfolg beim Absenden ist kein Zustandsbeweis im Ziel. Quelle: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-postmessagew
- Python `pty` ist Unix-spezifisch. Terminaltransport und Darstellung dürfen nicht ungeprüft mit dem Linux-Probeprozess gleichgesetzt werden. Quelle: https://docs.python.org/3/library/pty.html

Abruf: 2026-09-19. Daraus folgt keine bereits abgeschlossene Wahl eines neuen UI-Frameworks. Erst ein kleiner nativer Fähigkeitsbeweis entscheidet, ob der gewählte leichte Stack Transparenz, Fokus, DPI und Terminaldarstellung ausreichend trägt.

## Der nächste Bauabschnitt: erster echter Kontakt

Das ist die korrigierte Reihenfolge, **noch keine vollständige Goal-Liste**:

1. **Build- und Lieferpfad klären:** nutzbare Windows-Buildumgebung, feste Abhängigkeiten, Lizenz-/Paketbestandteile, Fehlerabbruch und saubere Artefaktprüfung. Bevorzugte Option ist ein autorisierter Windows-Runner; isoliertes Wine ist nur eine zu prüfende Alternative. Keine Veröffentlichung oder kostenpflichtige Infrastruktur aus dieser Planung ableiten.
2. **Kleinstes natives Overlay nachweisen:** eine echte Raute, ein Nachrichtenbereich, explizites Schließen/Pausieren; freie Desktopflächen bedienbar. Native Screenshots und Fokus-/Hit-Test-Rücklese, nicht nur ein Browsernachbau. Noch keine erfundenen funktionierenden Terminalkarten.
3. **Verbindungsweg bauen und testen:** Windows verbindet sich ausgehend zum vorgesehenen VPS-Endpunkt. Authentifizierung, Ziel-/Empfängerbindung, Versionsaushandlung und kleine begrenzte Nachrichten. Ein konkreter erreichbarer TLS-Endpunkt und Pairing sind vor Auslieferung nachzuweisen; Port 9880 aus einer alten Skizze ist keine Betriebsfreigabe.
4. **Vollständiges Paket liefern:** versioniertes Bundle samt Prüfsumme und kurzer Startanleitung. Daniel muss kein Python installieren und nicht selbst kompilieren. Unsigned-/SmartScreen-Status offen nennen, keine Anleitung zum pauschalen Abschalten von Schutzmechanismen.
5. **Daniel startet; tatsächliche Session tritt bei:** frisches Windows-Bild mit Ziel, Sequenz und Alter kommt beim Agenten an; echte Agentennachricht erscheint an der Raute und im Chat; Daniels Antwort landet nachweisbar in der gewählten Session. Ein Server-ACK allein genügt nicht.
6. **Abbruch und Wiederaufnahme:** Bilderzufuhr pausieren, Verbindung trennen, neu verbinden. Kein Wiederabspielen veralteter Eingaben. Sessionidentität bleibt erhalten; Wiederanmeldung ist nicht ein neuer Agent. Erst danach gilt der erste Kontakt als fertig.

Der vollständige Terminaltransport ist ein eigener folgender Nachweis. Sein Protokoll muss bereits beim ersten Kontakt mitgedacht werden, darf aber nicht als gelöst vorgetäuscht werden. Umfangreiche Kapseln, Hauhaucs und Lernschleifen sind **keine Vorbedingungen für die erste EXE**.

## Kleine technische Verträge, bevor daraus viel Code wird

Diese Punkte sind technische Arbeitsvorschläge von Codex, keine rückwirkenden Daniel-Zitate:

- **Identität:** getrennte IDs für Agent, konkrete Session, Elternsession, Anzeigehost, Arbeitsziel, Binding und Empfänger. Labels sind änderbar, IDs nicht an Listenposition gebunden. Ziele erhalten eine Generation, damit ein wiederverwendetes Fensterhandle nicht still dasselbe Ziel ist.
- **Transport:** Protokollversion, Nachrichten-ID, Session-/Binding-ID, Zeit/Sequenz und Größenlimit. Pairing kurzlebig und einmalig, dauerhafte Zugangsdaten nicht in URLs, Screenshots oder Git. Ein Client darf fremde Empfänger nicht einfach durch ein JSON-Feld autorisieren.
- **Wahrnehmung:** Capture-Zeit und Empfangszeit unterscheiden; Framegröße, Skalierung, Monitor-/Fensterkoordinaten und Herkunft mitliefern. Veraltete Bilder deutlich markieren; keine Aktion auf einer inzwischen ungültigen Zielbindung. Langsame Konsumenten bekommen begrenzte Puffer, keine unendliche Bildschlange.
- **Eingaben:** getrennt protokollieren: angefordert, angenommen, zugestellt, ausgeführt/fehlgeschlagen und Zustand beobachtet. TTL, neue Verbindungsgeneration und Deduplizierung verhindern Wiederholung alter Aktionen. Steuerrechte leben nicht länger als ihre Lease. Lokaler Stop wirkt auch ohne Server.
- **Terminal:** Session-ID und Prozessreferenz belegen die Quelle. ANSI, Alternate Screen, Cursor, Unicode, Resize und Eingaben gegen dieselbe Sitzung vergleichen. Ein neuer Testprozess ist kein Ersatz. Bestehende Konsole-Sicherheitsgrenzen werden nicht nebenbei abgeschaltet; die Anbindung laufender Sessions bleibt ein expliziter Machbarkeitsnachweis.
- **Update:** Paketversion und Konfiguration trennen; Einstellungen/Sessions sichern, Rückkehr zum vorherigen Paket ermöglichen. Ein kleiner separater Verbindungsprozess kann spätere UI-Neustarts abfedern, ist aber zunächst eine Option, keine bereits gebaute Infrastruktur.
- **KDE:** Sitzungstyp, Compositor und tatsächliche virtuelle Desktop-IDs ermitteln. Anzeigen auf Desktop 2 ist nicht dasselbe wie ein zweiter X-Server. Capture und Input bei inaktivem Desktop separat nachweisen.
- **WorldDOM:** echte DOM-/Accessibility-Daten, OCR/Vision und künstliche Markierungen mit unterschiedlicher Herkunft, Konfidenz und Aktualität führen. Eine erfundene semantische Ebene darf nicht vortäuschen, native App-Fähigkeiten zu besitzen.
- **Kapseln:** Originaldaten und spätere Kommentare getrennt speichern, Auswahl und fehlende Quellen sichtbar machen. Wiederansehen ist von Wiederherstellen getrennt. Empfängerrechte und Export müssen auch nach dem Speichern gelten.
- **Hauhaucs:** Skript zeichnet Ereignisse auf; das Modell interpretiert optional Ausschnitte. »Aufgezeichnet«, »zugestellt« und »vom Modell verarbeitet« sind verschiedene Cursor. Keine Behauptung dauernder Aufmerksamkeit aus einem laufenden Socket. Kontextgrenzen, Stop und eigenes Sessionbudget bleiben sichtbar.

## Beweisstrategie ohne Selbsttäuschung

Für jede Funktion festhalten: Anforderung, echte Quelle, ausgeführte Aktion, erwartete Beobachtung, tatsächliche Beobachtung und verbleibende Grenze.

- Core-Tests prüfen Logik; Transporttests prüfen Nachrichten und Ausfälle.
- Playwright bleibt für browserbedienbare Entwicklungs-/Prüfwege erforderlich. Es beweist deren Verhalten, nicht automatisch Win32-Eingaben oder Tk-Fenster.
- Native UI braucht zusätzlich echte Windows-Aufnahmen und Betriebssystem-/App-Rücklese. Eine Webseite, die »F12 funktioniert« anzeigt, ist kein Not-Aus-Test.
- Gezielte Fehlerfälle: falscher Empfänger, unbekanntes Ziel, abgelaufene Lease, veralteter Frame, Replay nach Reconnect, geschlossene Session, fehlende Kamera, geänderte DPI und UI-Hänger.
- Timing und Ressourcen werden auf dem tatsächlichen Gerät gemessen. Vorher sind sie Ziele; Messrate, Lücken und Unsicherheit gehören in den Bericht.

Diese Prüfung hat keine neue Windows-, Playwright- oder End-to-End-Abnahme durchgeführt. Sie enthält Code-/Dokumentprüfung, eine Tk-API-Abfrage und Primärquellenrecherche. Die vorhandenen Testberichte wurden nicht als heutige Testläufe ausgegeben.

## Was vor dem jeweiligen Fertigmelden noch fehlt

| Nachweis | Stand |
| --- | --- |
| Produkt und erste Kontaktstrecke klar beschrieben | Ja, hier korrigiert |
| Native Buildumgebung und vollständiges Paket | Nicht nachgewiesen |
| Windows-Start ohne Entwicklungsinstallation | Nicht nachgewiesen |
| TLS/Pairing/erreichbarer Liefer- und Rückkanal | Nicht nachgewiesen |
| Echter Agent empfängt Bild, sendet Nachricht, erhält Antwort | Nicht nachgewiesen |
| Original-Terminal vollständig lesbar und bedienbar | Nicht nachgewiesen |
| Overlay-Anzeigewechsel Windows/KDE 1/2 | Nicht nachgewiesen |
| Gesamtprodukt fertig | Nein |

Für den nächsten Bauauftrag ist damit die Richtung klar: **Buildfähigkeit und kleinster nativer Erstkontakt zuerst**. Sobald wirklich Daniels Rechnerstart oder neue Infrastruktur nötig ist, ist das eine konkrete Übergabe — kein Anlass, zwischendurch immer wieder ein »go« einzufordern.

## Zusammengehörige Quellen

- `/root/werkraum/docs/augen_haende_bridge/2026-09-19_ASTRA-LUNA_PLANUNG_WORTLAUT.md` — Gesprächswortlaut, keine Implementierungsabnahme.
- `/root/werkraum/docs/augen_haende_bridge/2026-09-19_LUNA-MAX_PLANUNG_MOMENTKAPSELN_HAUHAUCS_OVERLAY.md` — vorherige Ableitung; Reihenfolge durch diese Prüfung korrigiert.
- `/root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md` — Zielbild.
- `/root/werkraum/docs/systemdoku/77_worlddom_memory_seeds_wiedererweckung.md` — Erweiterungen und Portabilität.
- `/root/werkraum/docs/systemdoku/78_augen_und_haende_bauplan.md` — historischer Bauablauf mit korrigierter Geltung.
- `/root/werkraum/docs/augen_haende_bridge/2026-09-19_BRIDGE_SKILL_ORIGINAL_VOR_BAUSTARTPRUEFUNG.md` — wortgetreue Sicherung des alten globalen Skills.
- `/root/werkraum/_codex/skills/augen-haende-greenfield-builder/SKILL.md` — Arbeitsweise für den Neubau.
- `/vps_root/werkraum_bilder/refferenzen/h a bridge.jpg` — Daniels räumliche Referenz.

Keine Codeänderung, kein Service-Neustart und keine Änderung am Gemini-Prototypen erfolgte im Rahmen dieser Baustartkorrektur.
