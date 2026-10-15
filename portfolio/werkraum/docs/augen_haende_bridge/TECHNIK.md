---
autor: claude bei Daniels VPS
datum: 2026-09-20
herkunft: technische Verträge aus der Baustartprüfung von codex bei Daniels VPS (2026-09-19); Bausteinberichte V3.1 bis V3.4 von codex bei Daniels VPS (2026-09-20, Greenfield-Bau). Neu geschrieben von Claude aus den Originalen in archiv/originale/
status: Verträge sind Arbeitsvorschläge; V3.1 bis V3.3 lokal auf dem Linux-Probeweg belegt, V3.4 als Win32-Adapter implementiert; Windows-ConPTY, native Windows-Abnahme und Anbindung laufender Original-Sessions offen
---

# Augen & Hände — Technik

Dieses Dokument sammelt, wie die Bridge technisch gebaut sein soll und was davon schon steht. Es hat zwei Teile: die technischen Verträge, die vor viel Code festgelegt werden sollen, und die vier Bausteine des Greenfield-Neubaus, die bisher gebaut wurden.

Die Nummern V3.1 bis V3.4 sind die der Bausteinberichte. Die Baufolge V3.0 bis V3.7 in `CHATGPT_UND_MCP.md` zählt teilweise anders: Dort steht V3.3 für den Fensterscanner und V3.4 für das Binding, während hier V3.3 der Resize-Roundtrip und V3.4 der Scanner-Kern ist.

## Technische Verträge

Diese Punkte sind technische Arbeitsvorschläge von Codex vom 2026-09-19 und keine rückwirkenden Daniel-Zitate. Sie sollen feststehen, bevor daraus viel Code wird.

**Identität.** Agent, konkrete Session, Elternsession, Anzeigehost, Arbeitsziel, Binding und Empfänger bekommen getrennte IDs. Labels sind änderbar. IDs hängen nicht an der Listenposition. Ziele erhalten eine Generation, damit ein wiederverwendetes Fensterhandle nicht still dasselbe Ziel ist.

**Transport.** Jede Nachricht trägt Protokollversion, Nachrichten-ID, Session- und Binding-ID, Zeit und Sequenz, und es gibt ein Größenlimit. Das Pairing ist kurzlebig und einmalig. Dauerhafte Zugangsdaten stehen nicht in URLs, Screenshots oder Git. Ein Client darf fremde Empfänger nicht einfach durch ein JSON-Feld autorisieren.

**Wahrnehmung.** Capture-Zeit und Empfangszeit werden unterschieden. Framegröße, Skalierung, Monitor- und Fensterkoordinaten und die Herkunft werden mitgeliefert. Veraltete Bilder sind deutlich markiert. Auf einer inzwischen ungültigen Zielbindung gibt es keine Aktion. Langsame Konsumenten bekommen begrenzte Puffer und keine unendliche Bildschlange.

**Eingaben.** Protokolliert wird getrennt: angefordert, angenommen, zugestellt, ausgeführt oder fehlgeschlagen, und Zustand beobachtet. TTL, neue Verbindungsgeneration und Deduplizierung verhindern die Wiederholung alter Aktionen. Steuerrechte leben nicht länger als ihre Lease. Der lokale Stop wirkt auch ohne Server.

**Terminal.** Session-ID und Prozessreferenz belegen die Quelle. ANSI, Alternate Screen, Cursor, Unicode, Resize und Eingaben werden gegen dieselbe Sitzung verglichen. Ein neuer Testprozess ist kein Ersatz. Bestehende Sicherheitsgrenzen von Konsole werden nicht nebenbei abgeschaltet. Die Anbindung laufender Sessions bleibt ein expliziter Machbarkeitsnachweis.
**Geändert durch BE01** (`ANFORDERUNGEN.md`): Bestehende Sessions werden nicht angebunden. 1:1 gilt für Sitzungen, die die Bridge selbst startet.

**Update.** Paketversion und Konfiguration werden getrennt. Einstellungen und Sessions werden gesichert, und die Rückkehr zum vorherigen Paket ist möglich. Ein kleiner separater Verbindungsprozess kann spätere UI-Neustarts abfedern. Er ist zunächst eine Option und keine bereits gebaute Infrastruktur.

**KDE.** Sitzungstyp, Compositor und die tatsächlichen virtuellen Desktop-IDs werden ermittelt. Eine Anzeige auf Desktop 2 ist nicht dasselbe wie ein zweiter X-Server. Capture und Input bei inaktivem Desktop werden separat nachgewiesen.

**WorldDOM.** Echte DOM- und Accessibility-Daten, OCR und Vision sowie künstliche Markierungen werden mit unterschiedlicher Herkunft, Konfidenz und Aktualität geführt. Eine erfundene semantische Ebene darf nicht vortäuschen, native App-Fähigkeiten zu besitzen.

**Kapseln.** Originaldaten und spätere Kommentare werden getrennt gespeichert. Auswahl und fehlende Quellen sind sichtbar. Wiederansehen ist etwas anderes als Wiederherstellen. Empfängerrechte und Export gelten auch nach dem Speichern.

**Hauhaucs.** Ein Skript zeichnet Ereignisse auf, und das Modell interpretiert optional Ausschnitte. »Aufgezeichnet«, »zugestellt« und »vom Modell verarbeitet« sind verschiedene Cursor. Aus einem laufenden Socket folgt keine Behauptung dauernder Aufmerksamkeit. Kontextgrenzen, Stop und ein eigenes Sessionbudget bleiben sichtbar.

## Gebaute Bausteine

### V3.1 — Der tragende Terminalkanal

Status: lokal belegt. Windows-ConPTY und laufende Original-Sessions sind offen.

**Zweck.** Der erste echte Terminalbaustein des Greenfield-Neubaus ist ein eigener Terminalkanal. Er ist weder eine Homepage noch eine neue Surface, und er ist kein Textfeld, das nur wie ein Terminal aussieht. Der Kanal trennt Transport, native Präsentation und Audit-Rücklese.

Die alte Oberfläche `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/reference_surface.py` und der eingefrorene Gemini-Prototyp `/root/werkraum/_gemini/windows_bridge/` wurden dafür nicht umgebaut.

**Der erzwungene Beweisweg.** Jeder Kanal hält diese Reihenfolge ein:

```text
session_owned
→ pty_connected
→ vt_output_received
→ rendered
→ input_accepted
→ input_delivered
→ input_echoed
→ state_observed
→ audited
```

`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/terminal_channel.py` blockiert bei falscher Reihenfolge, fehlender Evidenz oder einem bereits beendeten Kanal. Für die Zustände sind konkrete Belege nötig: Besitzer, Transport, Byteanzahl, Präsentationsquelle, Request-ID, Zustellmethode, Marker, Capture-Methode und Audit-Sequenz.

**Was real angeschlossen ist.** `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/probe_terminal.py` besitzt ein isoliertes Konsole-Fenster und eine eigene PTY-Shell. Die rohen PTY-Bytes gehen gleichzeitig an zwei getrennte Zeugen:

- an die native Konsole-Präsentation, damit der sichtbare Terminalzustand erhalten bleibt,
- an den Bridge-Controller über den Unix-Socket, damit die Bridge echten VT-Output lesen und ein Marker-Echo unabhängig von der Konsole-Rücklese prüfen kann.

`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/proof_surface.py` führt die Probe erst nach dem Nachweis von Session, PTY, Output und Präsentation aus. Die Eingabe bleibt absichtlich ein ungefährlicher `printf`-Marker. Danach müssen sowohl die rohen PTY-Bytes als auch der sichtbare Konsole-Scrollback denselben Marker enthalten.

**Nachweis.** Der vollständige Bericht liegt unter `/root/werkraum/augen_haende_bridge/tests/evidence/V3_1_TERMINAL_CHANNEL_EVIDENCE.md`. Die browserbedienbare Beweisoberfläche zeigt den Kanalstatus und den nächsten erwarteten Zustand. Sie bleibt ein äußerer Zeuge und ersetzt keinen nativen Windows-Beleg.

**Grenzen.**
- Das ist ein isolierter, besitzbarer Linux-, Konsole- und PTY-Probeweg. Er ist kein Zugriff auf Daniels laufende Codex-, Claude- oder Gemini-Sessions.
- Der Windows-ConPTY-Adapter existiert noch nicht als abgenommener Pfad.
- ANSI- und VT-Bytes werden transportiert und beobachtet. Ein eigener Bridge-Renderer mit vollständigem Readback von Cursor, Alternate Screen, Resize und Unicode ist der nächste Terminalbaustein.
- `rendered` bedeutet hier die native Konsole-Rücklese über `getAllDisplayedText`. Es ist kein Windows-Screenshot und kein Beweis für ein fertiges Overlay.
- Die native Windows-EXE, der native Fensterscanner und die Bindung an Windows und KDE-Desktop 1/2 bleiben offen.

**Nächster Schritt.** Ein echter Terminal-Renderer- und Resize-Vertrag auf demselben Kanal. Erst danach werden die Ziel- und Fensterscanner-Bindung und das freie Windows-Overlay daraufgesetzt. Das Anti-Terminal für ChatGPT bleibt eine spätere reale Session-Schicht und wird nicht als lokaler Dummy vorgezogen.

### V3.2 — VT-Rücklese für denselben Terminalstrom

Status: lokaler Zustandsreader belegt. Ein vollständiger Renderer ist offen.

**Zweck.** Der Terminalkanal liefert nicht nur eine Marker-Zeichenkette. Der rohe PTY-Strom wird zusätzlich in einem expliziten VT-Zustand gelesen. Das ist die erste technische Schicht für Cursor, Zeilen, SGR-Farbe, Alternate Screen, Cursor-Sichtbarkeit und Resize.

Der Reader liegt in `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/terminal_renderer.py`. Er erhebt absichtlich keinen Anspruch auf vollständige Terminalemulation. Nicht unterstützte Sequenzen bleiben als Zustand sichtbar und werden nicht als erfolgreich verarbeitet ausgegeben.

**Nachgewiesene Teilmenge.**
- UTF-8-Ausgabe mit Ersatzzeichen bei ungültigen Bytes
- Text, `CR`, `LF`, Backspace und Tabulator
- Cursorpositionierung und relative Cursorbewegung
- `CSI J` und `CSI K` für sichtbares Löschen
- SGR-Parameter als Zustand
- `CSI ?25h/l` für die Cursor-Sichtbarkeit
- `CSI ?1049h/l` für die Trennung von Primary und Alternate Screen
- dimensioniertes Resize mit Erhalt sichtbarer Zellen
- eine sichtbare Liste nicht unterstützter Sequenzen

Die Proof-Surface zeigt den serialisierten VT-Zustand unter `data-testid="terminal-renderer"`, nachdem der echte PTY-Probeweg gelaufen ist.

**Grenzen.** Der Reader ersetzt weder einen etablierten, vollständigen VT-Emulator noch die native Konsole- oder spätere Windows-ConPTY-Präsentation. Offen bleiben Scroll-Regions, vollständige DEC-Modi, Hyperlinks, Mausprotokolle, Tastatur-Encoding und Pixel- und Font-Rücklese. Genau deshalb ist `unsupported_sequences` Teil des Ergebnisses.

**Nächster Schritt.** Den Reader gegen reale Trajektorien von Resize, Cursor und Alternate Screen erweitern, dann einen Rendereradapter auswählen und erst danach den Kanal in den echten Windows-EXE-Terminalkörper führen.

### V3.3 — PTY-Resize-Roundtrip

Status: Linux-PTY-Resize mit Kernel-Rücklese belegt. ConPTY ist offen.

**Ergebnis.** Das besessene Probe-Terminal kann kontrolliert auf eine neue Größe gesetzt werden. Der Resize-Weg läuft über einen separaten Control-Socket und vermischt seine JSON-Bestätigung nicht mit dem rohen VT-Ausgabestrom.

```text
Resize-Anforderung
  → PTY TIOCSWINSZ
  → Kernel TIOCGWINSZ
  → Control-Ack mit beobachteten rows/cols
  → VTScreenState.resize()
  → sichtbarer Proof-Zustand
```

Umgesetzt ist das in `probe_terminal.py`, `proof_surface.py` und `terminal_renderer.py` unter `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/`. Der Live-Proof setzt 40×120 und liest 40×120 aus dem PTY-Kernelzustand zurück. Die browserbedienbare Proof-Surface zeigt diesen Rücklauf zusätzlich unter `data-testid="terminal-resize"`.

**Sicherheitsgrenze.** Der Control-Socket akzeptiert ausschließlich den strukturierten Vorgang `resize` und begrenzt rows und cols auf 1 bis 1000. Er ist kein allgemeiner Shell- oder Terminal-Command-Kanal. Der bereits geprüfte, sichere `printf`-Marker bleibt die einzige aktive Eingabeprobe.

**Noch nicht behauptet.** Der Roundtrip beweist die Größenänderung eines Linux-PTY. Er beweist nicht Windows-ConPTY, KDE-Fenster-Resize, pixelgenaue Font- und DPI-Darstellung und keine vollständige Trajektorie von SIGWINCH und Alternate Screen. Diese Belege gehören zu späteren Adaptertests.

### V3.4 — Windows-Fensterscanner-Kern

Status: Win32-Adapter implementiert. Die native Windows-Abnahme ist offen.

**Ergebnis.** `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/windows_scanner.py` implementiert den read-only Inventarkern für Windows. Pro Scan liefert er:

- das vollständige Windows-Desktop-Ziel als `default_target_id`,
- die sichtbaren Top-Level-Fenster in der Reihenfolge von EnumWindows,
- Handle, Generation, Titel, Klasse, Rechteck, Z-Order, Prozess-ID und, soweit Windows es erlaubt, den Prozesspfad,
- ein Capability-Profil, das zunächst nur `inventory` behauptet,
- die vom Aufrufer gelieferte visuelle Frame-Referenz und den Frame-Hash.

Pixel-Capture, Overlay, UI-Automation, Binding und Input stecken absichtlich nicht in diesem Baustein.

**Identität.** `windows:window:<hwnd>` ist die auswählbare Ziel-ID. Die Generation wird in der Scannerinstanz erhöht, wenn sich Prozess-ID oder Fensterklasse für denselben Handle ändern. Änderungen von Titel oder Geometrie behalten damit dieselbe Identität. Ein Handle-Reuse mit anderem Prozess wird nicht still als dasselbe Ziel behandelt.

Das ist eine In-Memory-Generation und noch keine über Neustarts persistierte Windows-Prozessstartzeit. Diese stärkere Identität bleibt offen und braucht native Tests auf Daniels Windows.

**Prüfstatus.** Die Fake-API-Tests in `/root/werkraum/augen_haende_bridge/tests/test_windows_scanner.py` prüfen den Default-Desktop, das Fensterinventar, die Generationen und den fehlenden Frame-Zeugen. Der Linux-VPS kann den Win32-Adapter nicht nativ ausführen. Der Teststatus ist deshalb Core- und Adaptervertrag und kein Windows-Native-PASS.
