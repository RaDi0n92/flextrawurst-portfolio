---
name: augen-haende-greenfield-builder
description: Baue und dogfoode den Greenfield-Neubau der Augen-und-Hände-Bridge mit kreativer Python-Harness, echten Zielbindungen, Playwright-Beweisen und Terminal-Paritätsprüfung. Nur für den neuen Bridge-Pfad; der historische Gemini-Prototyp ist entfernt.
---

# Augen Haende Greenfield Builder

Dieses Skill gilt für den Neubau unter `/root/werkraum/augen_haende_bridge/`. Der alte Prototyp unter `/root/werkraum/_gemini/windows_bridge/` wurde am 2026-09-20 entfernt. Er ist nur noch über die Git-Historie nachvollziehbar und keine aktive Referenz, Laufzeit oder Testquelle.

## Schichten

Arbeite mit vier getrennten Schichten:

1. **Builder-Skill:** beschreibt, wie Codex baut, benutzt, prüft und dokumentiert.
2. **Creative Harness:** Python-Graph aus Nodes, Kanten, States, Checkpoints, Fallbacks und Proof-Gates.
3. **Bridge-Runtime:** Sichtbarkeit, Targets, Sessions, Leases, Input-Policy und Audit.
4. **Echte Ziele:** Windows-Fenster/Desktop, Linux-KDE-Desktop 1/2 und vorhandene Linux-Original-Terminals.

Der Skill verleiht keine Runtime-Rechte. Jede reale Aktion läuft durch Target, Capability, Lease, Not-Aus und Audit.

## Pflichtorientierung

**Quellenrangfolge** — gilt vor jeder Etappe (Herkunft: `START_HIER.md`, Abschnitt „Zuerst: die Quelle“):

1. Daniels dokumentierter Wortlaut, bei späterer Korrektur die spätere Fassung. Maßgeblich ist `ANFORDERUNGEN.md` (R001–R120).
2. Die Skizze `h a bridge.jpg` ist nur Orientierung. Sie ist älter als die Feinjustierung, ihre Beschriftungspfeile sind keine Bauteile, und sie zeigt drei Terminals, wo der erste Körper eines hat. Bei Widerspruch gilt das Dokumentierte.
3. Vorhandener Code steht darunter. Widerspricht er Punkt 1, ist er Altlast: entfernen oder quarantänisieren, nicht als Fundament weiterbauen.
4. Bevor Transport-, Evidence- oder Testschichten auf den Körper gesetzt werden: den Körper starten und gegen `ANFORDERUNGEN.md` halten. „Technisch grün“ ersetzt das nicht.

Vor einer neuen Etappe lesen:

- `/root/werkraum/docs/augen_haende_bridge/PLAN.md`
- `/root/werkraum/docs/augen_haende_bridge/ANFORDERUNGEN.md` — maßgeblich bei Konflikten mit älteren Fertigmeldungen.
- `/root/werkraum/docs/augen_haende_bridge/TECHNIK.md`
- `/root/werkraum/docs/systemdoku/78_augen_und_haende_bauplan.md`
- `/root/werkraum/augen_haende_bridge/BUILD_LOG.md`
- `/vps_root/werkraum_bilder/refferenzen/h a bridge.jpg`
- den relevanten aktuellen Code und den letzten Evidence-Report unter `/root/werkraum/augen_haende_bridge/tests/evidence/`

Anzeigehost, Arbeitsziel, konkrete Session und Empfänger sind unabhängig. Daniel möchte das echte Programm-Overlay auf Windows oder KDE-Desktop 1/2 anzeigen können. Der vorhandene technische Identifier `surface:windows:bridge` ist kein Verbot weiterer Anzeigeorte und kein Beweis einer laufenden Windows-Anbindung.

Die nächste Produktetappe beginnt mit Buildfähigkeit, vollständigem Windows-Paket und echtem Bild-/Nachrichten-Erstkontakt. Kapseln und Hauhaucs werden nicht vor diese Kontaktstrecke geschoben. Der Benutzer muss nicht selbst Python installieren oder kompilieren.

## Skill-Doppellesung und Fokuszyklus

Der Skill ist nicht nur eine einmalige Startlektüre. Jeder konkrete Bau- oder
Prüfabschnitt läuft durch zwei bewusste Skill-Gates:

```text
skill_opening_read
→ context_rehydrated
→ skill_prebuild_read
→ build_step_executed
→ evidence_recorded
→ skill_closing_read
→ protocol_recorded
```

Dabei gilt:

1. `skill_opening_read` klärt, welcher aktuelle Vertrag und welche Reihenfolge
   gelten.
2. `context_rehydrated` liest die relevanten Dokus, Git-Historie/-Status,
   aktuellen Code und letzte Evidence. So wird nicht aus einer alten
   Gesprächserinnerung gebaut.
3. `skill_prebuild_read` liest diesen Skill und den ausführenden Bridge-Skill
   unmittelbar vor dem Bau erneut. Erst danach darf der konkrete Stein
   verändert oder ausgeführt werden.
4. `build_step_executed` bezeichnet genau einen kleinen Bau-, Reparatur- oder
   Prüfstein.
5. `evidence_recorded` trägt Core-, Playwright- und gegebenenfalls native
   Belege mit `PASS`, `PARTIAL`, `BLOCKED` oder `UNKNOWN` ein.
6. `skill_closing_read` liest beide Skills unmittelbar nach Bau und Tests
   erneut. Dabei wird geprüft, ob die Implementierung gegen den aktuellen
   Vertrag abgedriftet ist.
7. Erst nach diesem Abschluss-Gate wird der Eintrag im laufenden
   Bauprotokoll unter
   `/root/werkraum/docs/augen_haende_bridge/2026-09-20_BRUECKE_BAUPROTOKOLL_FOKUS_UND_WIEDERAUFNAHME.md`
   als abgeschlossen markiert.

Die Creative-Harness erzwingt diese Reihenfolge als
`BuildCycleRun`. Ein fehlendes Skill-Gate, ein übersprungener Kontextschritt
oder eine fehlende Evidence- bzw. Protokollmarke blockiert den Zyklus
fail-closed. Das Harness behauptet damit nicht, Dateien selbst gelesen zu
haben; es verlangt eine explizite, auditierbare Attestierung der real
ausgeführten Lesung. Zusätzlich braucht jeder Zyklus einen `FocusContract`:
ein konkretes Ziel, genau den nächsten Stein, die unverhandelbaren
Erhaltungsanker und die verbotenen Driftformen. Fehlt ein Anker, startet der
Zyklus nicht. Damit prüft die Harness nicht nur die Arbeitsreihenfolge,
sondern hält auch aktuelle Nutzerentscheidungen gegen Kontextdrift fest.

## Verbindlicher Arbeitszyklus

Für jede Etappe:

1. `skill_opening_read` und `context_rehydrated` ausführen.
2. Herkunft, Scope und betroffene Targets benennen.
3. Einen expliziten Git-Sicherheitspunkt setzen.
4. `skill_prebuild_read` unmittelbar vor der Änderung ausführen.
5. Passende Logik-/Transportbeweise, Playwright für browserbedienbare Prüfwege und native Beweise für Betriebssystemfunktionen definieren. Reine Dokumentprüfungen benötigen keinen erfundenen UI-Lauf.
6. Den kleinsten Baustein mit `apply_patch` bauen.
7. Core-/Policy-/Integrationstests ausführen.
8. Die isolierte Prüfoberfläche oder das native Overlay starten; den jeweils geprüften Gegenstand ausdrücklich nennen.
9. Playwright bedient Browserfunktionen und liest DOM, sichtbaren Zustand, Antwort und Auditspur zurück. Native Funktionen zusätzlich mit echten Plattformaufnahmen und Zustandsrücklese prüfen; Playwright steuert Tk/Win32 nicht automatisch.
10. Screenshots und Evidence-Report unter `/root/werkraum/augen_haende_bridge/tests/evidence/` ablegen.
11. `skill_closing_read` unmittelbar nach Bau und Tests ausführen.
12. `/root/werkraum/augen_haende_bridge/BUILD_LOG.md` und das Fokusprotokoll mit Zwischenstand, Unsicherheit und nächstem Schritt ergänzen.
13. `graphify update .` versuchen; bei fehlendem Werkzeug den Blocker offen dokumentieren.
14. Nur die betroffenen Dateien committen.

Ein grüner Unit-Test allein schließt keine UI-Etappe. Browser-PASS bleibt Browser-PASS; für native Etappen sind die zugehörigen Plattformbelege zusätzlich erforderlich. Fehlende Umgebung heißt offen, nicht bestanden. Historische B4.6-Belege sind keine Produktabnahme des Overlays.

**Körper-Tor:** Vor dem Fertigmelden jeder Etappe, die den Windows-Körper berührt, ausführen:
`python3 /root/werkraum/augen_haende_bridge/tests/pruefe_koerper.py`. Es hält den Körper gegen
bereits wörtlich beanstandete Dinge (fest gemalte Agenten, Deckkraft, Attrappen, Deko-Pfeile) und
nennt zu jedem die Fundstelle. Exit 1 ist kein Testfehler, sondern die Aussage, dass der Körper den
dokumentierten Vorgaben noch nicht entspricht. Es prüft nicht, wie das geöffnete Fenster aussieht.

## Live-Dogfooding

Sobald eine UI-Schicht existiert, benutzt Codex sie selbst. Neue Funktion bedeutet nicht nur neue Datei, sondern:

```text
bauen → isolierte Dev-Instanz starten → UI bedienen → sichtbaren Zustand lesen
→ Audit prüfen → Screenshot sichern → Fehler korrigieren → dokumentieren
```

Eine synthetische Proof-Surface ist kein aktiver Produktpfad und wird nicht
mehr gestartet. Browser-Witnesses gelten nur für tatsächlich browserbedienbare
Pfade; native Windows-/KDE-Funktionen brauchen echte Plattformaufnahme und
Zustandsrücklese.

## Terminal-Paritätsgate

Terminal-Ansichten werden nicht aus Platzhaltertexten nachgebaut. Das aktuell geöffnete Original-Terminal auf dem VPS ist die Referenz. Vor einem Terminal-Gate werden read-only erfasst:

- Host, KDE-Desktop 1/2, Terminal-ID, Fenstergeometrie und Sichtbarkeit,
- Titel, Prompt, Arbeitsverzeichnis, Schrift-/Farbprofil und Scrollback,
- laufender Prozess, Cursor-/Eingabestatus und beobachtbarer Output,
- vor einer aktiven Eingabeprüfung zunächst deren sicheren, eindeutigen Marker und das echte Ziel festlegen; eine Eingabe selbst ist nicht read-only.

Die Eingabekette muss sichtbar nachweisen:

```text
accepted → delivered → echoed → observed → audited
```

`accepted` ist niemals gleich `delivered`. Keine gefährlichen Befehle als Probe. Private Tokens, Secrets und unbeteiligte Terminalinhalte gehören nicht in Screenshots oder Evidence-Dateien.

## Creative-Harness-Regeln

Die Harness unter `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/` modelliert mindestens:

- State-Nodes für sichtbare Zustände,
- Action-Nodes für deklarierte Fähigkeiten,
- Observation-Nodes für Rücklese,
- Gate-Nodes für Policy/Lease/Playwright-Beweis,
- Kanten mit Bedingungen, Herkunft, Timeout und Fallback,
- Checkpoints und neue Branches statt magischem Realwelt-Zurückspulen.

Agenten dürfen Graphen vorschlagen oder zusammensetzen. Ausführung bleibt an explizite Targets, Capabilities, Leases und den lokalen Not-Aus gebunden. Kein versteckter Shell- oder Plattform-Seiteneingang.

## Recherche-abgeleitete Architekturregeln

Die Bridge behauptet nie eine globale Fähigkeit „Overlay kann alles“. Für jedes
Target wird ein eigenes Capability-Profil geführt. Mindestens zu unterscheiden
sind `capture`, `ui_automation`, `overlay`, `terminal_read`, `terminal_write`
und `input`. Ein unbekanntes oder nicht belegtes Profil ist `unavailable`, nicht
`success`.

Terminaltransport und Darstellung bleiben getrennt. Eine echte Terminaletappe
braucht eine besitzende PTY-/ConPTY-Session oder einen ausdrücklich geprüften
Adapter; Screenshot, OCR oder ein Textfeld sind keine Terminal-Parität. Die
beobachtbare Terminalkette lautet:

```text
session_owned → pty_connected → vt_output_received → rendered
→ input_accepted → input_delivered → input_echoed
→ state_observed → audited
```

Für Targets und Aktionen gilt dieselbe Trennung:

```text
target_discovered → target_identity_stable → capability_read
→ binding_selected → lease_checked → action_accepted
→ action_delivered → target_state_observed → audited
```

WorldDOM-Objekte müssen ihre Herkunft sichtbar tragen. `native`, `ocr`,
`vision`, `user_marked` und `agent_inferred` sind keine austauschbaren Belege.
Ein gerendertes Overlay-Objekt beweist weder eine native Einfügung in das
Zielprogramm noch eine ausführbare Eingabe. Jede Quelle erhält Aktualitätszeit,
Konfidenz und Bindung an Fenster, Desktop, Terminal oder Session.

Die Creative-Harness darf einen Schritt nur freigeben, wenn seine
`required_capabilities` im Profil des konkreten Targets und seine
`required_proofs` im Beweisledger vorhanden sind. Fehlt eines davon, wird der
Run fail-closed blockiert. `accepted`, `delivered`, `observed` und `audited`
sind getrennte Ereignisse und dürfen nicht aus einem einzigen ACK abgeleitet
werden.

Windows, KDE-X11 und KDE-Wayland bleiben getrennte Adapter. Besonders gilt:
eine virtuelle KDE-Arbeitsfläche ist nicht automatisch ein zweites X11-Display,
und ein Capture-Beleg ist kein Eingabe-Beleg. Playwright beweist nur
browserbedienbare Prüfwege; native Windows-/KDE-Funktionen brauchen zusätzlich
Plattformaufnahme und Zustandsrücklese.

## Fensterscanner als eigener Augen- und Sicherheitskern

Der Fensterscanner ist kein UI-Zusatz und keine reine Fensterliste. Er ist der
erste Bridge-Schritt vor Terminal, Raute, Overlay, WorldDOM und Eingabe. Sein
Default-Ziel ist der vollständige sichtbare Windows-Desktop mit Hintergrund,
Taskleiste und allen sichtbaren offenen Programmen.

Ein Scan erzeugt zwei gekoppelte, aber getrennte Zeugen:

1. einen visuellen Desktop-/Fenster-Frame mit Zeitstempel und Hash;
2. einen strukturierten `TargetScanSnapshot` mit auswählbaren Targets,
   stabiler `target_id` plus `generation`, Geometrie, Sichtbarkeit, Z-Order,
   Prozessdaten, virtuellem Desktop, Herkunft und Capability-Profil.

Der rohe Fensterhandle ist nie alleinige Identität. Wird ein Fenster geschlossen
und ein neues Fenster erhält denselben Handle, muss die Generation wechseln und
eine alte Binding-Zuordnung ungültig werden. Ein Scan ohne strukturierten
Readback oder ein Inventar ohne zugehörigen Frame ist `UNKNOWN`.

Die Scanner-Bedienung öffnet die Auswahl, sie bindet nicht heimlich. Daniel kann
den gesamten Desktop oder ein einzelnes Fenster auswählen. Erst nach Auswahl,
Capability-Lesung und Binding-Rücklese dürfen Agent, Raute, Terminal, Text,
Bild oder Zeichnung an das Ziel geheftet werden. Einzelfenster verwenden einen
fensterrelativen Koordinatenraum und folgen Move/Resize; Desktop-Bindings
verwenden den Desktop-Koordinatenraum.

Die Scanner-Harness führt mindestens diese Kette:

```text
SCAN_REQUESTED
FRAME_CAPTURED
INVENTORY_READ
TARGET_SELECTED
IDENTITY_VERIFIED
BINDING_CREATED
BINDING_READ_BACK
PRE_ACTION_RESCAN
TARGET_STATE_OBSERVED
```

Für Bewegung, Resize und laufende Banner gilt der aus dem Blender-
Live-Reference-QA übernommene Zeugenvertrag: Baseline-Bild und strukturierter
Snapshot, genau eine Änderung, 10-Hz-Samples während Übergängen über 100 ms,
unmittelbarer After-State und erneuter Readback. Verpasste oder verspätete
Samples werden als `UNKNOWN`/Fehler dokumentiert, niemals still als `PASS`.

Vor jeder realen Aktion wird der zuletzt beobachtete Snapshot gegen einen
unmittelbaren Pre-Action-Rescan geprüft. Ein alter Screenshot, ein alter
Fensterhandle oder ein erfolgreich gesendetes Koordinatenpaket beweist nicht,
dass die Aktion noch dasselbe Ziel trifft.

## Playwright Guardian: äußerer Zeuge für jeden browserbedienbaren Übergang

Die Creative-Harness darf ihren eigenen internen Zustand nicht als alleinigen
Erfolg ausgeben. Für jeden browserbedienbaren Prüfpfad wird ein äußerer
Playwright-Witness verlangt. Er klickt einen sichtbaren Control und liest danach
mindestens vier Schichten zurück: DOM-Projektion, Core-State, Audit-Suffix sowie
den aktuellen Scanner-/Frame-Zeugen.

Der Vertrag liegt in
`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/guardian.py`.
Der frühere synthetische Playwright-Witness wurde am 2026-09-20 entfernt.
Ein neuer browserbedienbarer Witness darf erst an einen echten aktuellen
Adapter oder an die native Oberfläche gebunden werden.

Ein Guardian-Schritt hat eine stabile `step_id`, erwartete DOM-/Core-Werte, die
unmittelbar erwartete Audit-Sequenz, das konkrete Target und optional eine
native Pflicht. Nur diese Zustände sind zulässig:

```text
pass    = alle geforderten browserseitigen Zeugen stimmen überein
blocked = Zeugen widersprechen sich oder die Auditfolge fehlt
unknown = ein erforderlicher Zeuge fehlt, besonders native Windows-Evidence
```

`unknown` wird nie zu `pass` umgedeutet. Playwright beweist Browser- und
Protokollpfade; es beweist keine native Win32-/Tk-/EXE-Sichtbarkeit,
Fokusannahme oder Eingabeausführung. Native Etappen benötigen zusätzlich
Plattformaufnahme und native Rücklese.

## ChatGPT-Schicht: Chatkörper und Anti-Terminal getrennt halten

Die vollständige Bedeutung und der erste echte Vertikalschnitt stehen in
`/root/werkraum/docs/augen_haende_bridge/CHATGPT_UND_MCP.md`.
Dieser Abschnitt ist der Bauvertrag daraus:

- ChatGPT niemals als lokalen Dummy oder statische Beispielantwort nachbauen;
  der erste Slice muss eine echte ChatGPT-Web-/MCP-Session erreichen.
- Die **Raute** ist Präsenz, der **Chatkörper** ist manueller Austausch, das
  **Anti-Terminal** ist technische Wahrheit/Beweis, die **Bridge** ist der
  Transport zur Zielwelt und der **Fensterscanner** ist Ziel-/Binding-Wahrheit.
- Chatnachrichten und technische Aktionen haben getrennte Ereignisbahnen.
  Eine normale Daniel-Nachricht darf keinen MCP-/Toolcall implizit erzeugen.
- `daniel`, `chatgpt` und `bridge_context` sind verschiedene Absender. Ein
  Beobachtungsstatus darf nicht als ChatGPT-Satz ausgegeben werden.
- Ziel, Anzeigehost, konkrete Session und Empfänger bleiben unabhängig. Raute,
  Chatkörper und Anti-Terminal bleiben einzelne, verschiebbare Elemente statt
  eines neuen Monsterfensters.
- Die ChatGPT-Harness führt den Erstkontakt fail-closed über
  `session_is_real`, `target_bound`, `binding_read_back`,
  `chat_message_submitted`, `message_delivered`, `chatgpt_turn_received`,
  `response_rendered`, `sender_identity_correct`,
  `tool_not_triggered_by_plain_chat`, `target_observed` und `proof_attested`.
- Für Chat gilt `submitted → delivered → turn_received → rendered`. Für
  Aktionen gilt separat `accepted → sent → delivered → executed → observed →
  proven`. Ein Chatereignis bekommt niemals künstlich den Aktionsstatus
  `executed`.

Der erste ChatGPT-Slice ist erst fertig, wenn Daniel manuell schreibt, die
Nachricht die reale Session erreicht, die echte Antwort im Chatkörper erscheint,
die Absenderidentität stimmt und die Ziel-/Beweiskette zurückgelesen wurde.
Ein lokaler Reply, ein ACK oder eine Proof-Surface zählt nicht.

## V3: providerneutrales Anti-Terminal und MCP-P0

Die vollständige V3-Ergänzung steht in
`/root/werkraum/docs/augen_haende_bridge/CHATGPT_UND_MCP.md`.
Der verbindliche Bauvertrag daraus lautet:

- Nicht vier Anti-Terminal-UIs bauen. Einen gemeinsamen technischen Kern mit
  eigenen Adaptern für `chatgpt`, `codex`, `claude` und `gemini` bauen.
- Die AI-Ströme behalten ihre eigenen natürlichen Körper und access paths.
  ChatGPT bekommt Raute/Chatkörper, Codex sein echtes Terminal; die gemeinsame
  Schicht zeigt nur die technische Anatomie aus Handshake, tools/list, Session,
  Call-ID, Tool, Resultat, Fehler, Provenienz und Beweisstatus.
- `ai_stream_id`, `mcp_session_mode`, `access_path`, `server_id` und
  `tool_profile` sind bei jedem Provideranschluss Pflicht. `mcp_session_id` ist
  bei `stateful` Pflicht und bei `stateless` bewusst leer. Gemeinsame Dateien,
  Modellnamen oder Atlasziele verschmelzen keine Identitäten.
- MCP-P0 bleibt ein kleiner read-only Preflight und wird nicht zur neuen
  Oberflächen-Großbaustelle: `configured → reachable → handshake_succeeded →
  tools_list_received → atlas_read_verified`.
- Ein Handshake ohne `Mcp-Session-Id` braucht eine ausdrückliche
  `session_mode=stateless`-Attestierung; ein unbekannter Modus ist BLOCKED. Eine
  vorhandene Session-ID muss dagegen als `stateful` zurückgelesen und bei den
  Folgeaufrufen mitgeführt werden. Ein ACK ohne `tools/list` oder `tools/list`
  ohne harmlosen `/gesamtatlas`-Read ist kein P0-PASS.
- Das erste Profil bleibt auf `/gesamtatlas` begrenzt: lesen, suchen,
  Provenienz prüfen, Sessionstatus lesen und eigene Spur schreiben. Bridge-,
  Desktop-, Capture- und Input-Fähigkeiten brauchen eigene Capabilities,
  Leases und Belege.
- Session-Schiffbruch ist ein sichtbarer Zustand: `alive`, `reconnecting`,
  `context_compacted`, `session_changed`, `lost` oder `handoff_required`.
  Sessionwechsel darf nicht still als Kontinuität erscheinen.

Die Harness-Verträge dafür liegen als `MCPPreflightRun`,
`MCP_P0_PROOF_SEQUENCE`, `SessionContinuity`, `AI_STREAM_IDS` und
`MCP_ACCESS_PATHS` im Greenfield-Harness. MCP-P0 wird vor oder parallel zum
EXE-Grundkörper als kurzer Diagnosezaun geprüft; es darf V3 nicht in vier
Provider-Großprojekte zerlegen.

Die V3-Reihenfolge ist:

```text
MCP-P0 → EXE → echter Terminalkanal → Rücklese → Fensterscanner
→ Binding → Guardian/native Evidence → ChatGPT → Codex/Claude/Gemini-MCP-Körper
```

Ein neuer browserbedienbarer Witness muss isolierten Browser-Kontext,
web-first Assertions und Trace-Artefakte verwenden. Direkte Mutations-POSTs
dürfen keinen UI-Pass erzeugen. Die entfernte synthetische Proof-Surface und
ihre alten Playwright-Skripte sind keine Beweisquelle mehr; ein fehlender
nativer Beleg bleibt offen.

## Nicht als fertig behaupten

Nicht behaupten, dass Windows, KDE, MCP, Webcam, Terminalinput oder echte DOM-/UI-Einfügung funktionieren, solange der jeweilige Adapter nicht mit sichtbarem Playwright-/Plattformbeleg und rückgelesenem Audit nachgewiesen ist.

## V3.1 implementierter Terminalkanal

Der erste Greenfield-Terminalkanal liegt unter
`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/terminal_channel.py`.
Er ist ein Beweis- und Zustandsvertrag, kein Shell- oder Renderer-Ersatz. Seine
Reihenfolge ist verbindlich:

```text
session_owned → pty_connected → vt_output_received → rendered
→ input_accepted → input_delivered → input_echoed
→ state_observed → audited
```

Der isolierte Linux-/Konsole-Probeadapter unter
`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/probe_terminal.py`
führt rohe PTY-Ausgabe sowohl zur nativen Konsole-Präsentation als auch zum
Bridge-Controller. Ein Terminal-PASS braucht deshalb zwei getrennte Zeugen:
rohe PTY-Bytes und native Konsole-Rücklese. Ein ACK, ein Screenshot oder nur
eine Scrollback-Kopie reicht nicht.

V3.1 darf nicht als Windows-ConPTY, vollständiger VT-Renderer, laufende
Agentensession oder fertiges Overlay ausgegeben werden. Diese Nachweise sind
folgende Etappen.

## V3.2 VT-Rücklese

Der PTY-Strom wird zusätzlich durch
`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/terminal_renderer.py`
in einen expliziten `VTScreenState` gelesen. Die aktuelle Teilmenge umfasst
Text, Cursorbewegung, SGR, grundlegendes Löschen, Alternate Screen,
Cursor-Sichtbarkeit und Resize. Nicht erkannte Sequenzen werden unter
`unsupported_sequences` sichtbar gehalten.

Dieser Reader ist kein vollständiger Emulator und kein Pixelbeweis. Er darf
die native Konsole-/ConPTY-Präsentation nicht ersetzen. Ein späterer
Rendereradapter muss den gleichen Transportstrom gegen Cursor, Farben,
Alternate Screen, Resize, Unicode und Eingabe-Encoding prüfen; bis dahin
bleiben fehlende Fähigkeiten offen statt grün.

## V3.3 Resize-Roundtrip

Der isolierte Linux-PTY besitzt unter
`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/probe_terminal.py`
einen separaten Control-Socket für `resize`. Der Adapter setzt die Größe mit
`TIOCSWINSZ` und muss sie anschließend mit `TIOCGWINSZ` zurücklesen. Erst die
beobachteten Werte dürfen in `VTScreenState.resize()` übernommen werden.

Resize-Control darf nicht in den rohen VT-/Input-Strom fallen und ist kein
allgemeiner Shellkanal. Der Linux-Beleg ist kein Windows-ConPTY-Beleg; beide
Adapter bleiben getrennt und brauchen eigene native Evidence.

## V3.4 Windows-Fensterscanner-Kern

Der read-only Win32-Inventarkern liegt unter
`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/windows_scanner.py`.
Er macht den vollständigen Windows-Desktop zum Default-Ziel und führt sichtbare
Top-Level-Fenster als auswählbare `TargetScanItem`s. Ein Scan darf nur mit
gekoppelter `frame_ref` und `frame_hash` als vollständiger Scannerzeuge gelten.

Der Adapter behauptet zunächst nur `inventory`. `capture`, `overlay`,
`ui_automation`, `input` und Binding brauchen eigene Capability-/Lease-/native
Belege. Generationen werden innerhalb einer Scannerinstanz bei Prozess- oder
Klassenwechsel am gleichen Handle erneuert. Fake-API-Tests sind
Vertragsbelege, niemals Windows-Native-Evidence.

Der aktuelle read-only Capture-Körper liegt unter
`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/windows_capture.py`.
Er erzeugt über Windows-GDI einen begrenzten virtuellen Desktop-Frame und
paart `frame_ref`, `frame_hash`, Zeitstempel und Dimensionen mit demselben
`WindowsWindowScanner`-Lauf. Capture wird nicht heimlich beim Programmstart
ausgeführt; der Button oder der explizite Testschalter
`BRIDGE_NATIVE_SCAN_ON_START=1` muss ihn auslösen. Der Wine-Lauf ist nur ein
gebündelter Windows-API-/Prozessbeleg. Ein echter Windows-Host bleibt für
Native-Evidence, DPI, Capture-Quelle und Fensterwelt erforderlich.
