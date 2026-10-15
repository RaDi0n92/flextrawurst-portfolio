# Augen & Hände — fortlaufendes Bautagebuch

Die fortlaufende Fokus-, Lesungs- und Abnahmespur steht unter
`/root/werkraum/docs/augen_haende_bridge/2026-09-20_BRUECKE_BAUPROTOKOLL_FOKUS_UND_WIEDERAUFNAHME.md`.
Vor und nach jedem neuen Bauabschnitt werden dort die beiden Skill-Lesungen,
die Provenienzgrenze, die Evidence-Schichten und der tatsächliche nächste
Stein festgehalten. Dieses Bautagebuch bleibt die technische Ereignischronik.

## 2026-09-20 — Altlasten ausdrücklich entfernt

Auf Daniels ausdrücklichen Auftrag wurden der alte Gemini-Prototyp unter
`/root/werkraum/_gemini/windows_bridge/`, die alte Proof-Surface, die alten
Playwright-Witness-Skripte und der alte EXE-Einstieg aus dem aktiven Baum
entfernt. Die historischen Einträge darunter bleiben unverändert als
Provenienz. Ihre damaligen Browser-/Smoke-Ergebnisse sind keine aktuellen
Produktbeweise und werden im Greenfield-Neubau nicht wieder gestartet.

## 2026-09-19 — Baustartprüfung und Geltungskorrektur (Codex)

Die älteren Einträge bleiben als Verlauf erhalten. B4.6 belegt Browsermechanik, nicht das geforderte native Overlay. Windows-only-Anzeige ist durch Daniels spätere Vorgabe Windows/KDE 1/2 überholt. Die EXE-/VPS-Kontaktstrecke und vollständige Original-Terminal-Parität sind offen. Ein Tk-API-Fehler im Startpfad wurde statisch plus lokaler API-Abfrage festgestellt; keine Reparatur oder neue native Abnahme in dieser Dokumentationsetappe.

Prüfung, Quellen, Reihenfolge und offene Nachweise: `/root/werkraum/docs/augen_haende_bridge/2026-09-19_BRUECKE_BAUSTART_PRUEFUNG_UND_VEREINBARUNG.md`. Skills wurden gezielt korrigiert, alter globaler Skill wortgetreu gesichert. Kein Produktionscode und kein laufender Dienst geändert. Playwright bleibt Browserbeweis; native UI benötigt zusätzlich Plattformbelege.

Dieses Blatt hält Zwischenstände fest. Es unterscheidet immer zwischen:

- **Core:** reine Vertrags-, Policy- oder Zustandslogik.
- **Playwright:** sichtbarer, rücklesbarer Beweis über eine echte Proof-Surface oder später über die echte Windows-Oberfläche.
- **Umgebung:** Werkzeuge oder Plattformen, die für einen Beweis noch fehlen.

## 2026-09-19 — Greenfield-Start

- Der alte Prototyp unter `/root/werkraum/_gemini/windows_bridge/` bleibt eingefroren.
- Der neue Pfad ist `/root/werkraum/augen_haende_bridge/`.
- Die sichtbare Bridge-Surface ist `surface:windows:bridge`.
- Windows-Fenster/Desktop und Linux-KDE-Desktops/Original-Terminals sind Targets.

## 2026-09-19 — G01 Transportfundament: lokaler bidirektionaler Relay

- Herkunft/Scope: neuer Greenfield-Pfad; der Gemini-Prototyp und laufende Systeme bleiben unangetastet.
- Implementiert: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/transport.py` und `transport_client.py`.
- Der Relay bindet absichtlich nur an `127.0.0.1`, authentifiziert zwei explizite Sessions, trennt `forwarded` von `received`, prüft Ziel/Session-Epoch, dedupliziert Nachrichten und führt ein privates SQLite-Metadatenjournal ohne Text-/Bild-/Token-Inhalt.
- Text und synthetische PNG-Testframes laufen in beide Richtungen. Es gibt weiterhin keine Desktopaufnahme, keine Eingabe, keine Shell und keinen öffentlichen VPS-Endpunkt.
- Core-/Socket-Beleg: 9 Transporttests grün; gesamte vorhandene unittest-Menge: 35 Tests grün.
- Playwright-Beleg: `/root/werkraum/augen_haende_bridge/tests/evidence/TRANSPORT_LOCAL_PLAYWRIGHT_EVIDENCE.md` und `/root/werkraum/augen_haende_bridge/tests/evidence/transport_local_playwright.png`.
- Der erste Playwright-Versuch scheiterte an Chromiums `ERR_BLOCKED_BY_LOCAL_NETWORK_ACCESS_CHECKS`, weil eine künstliche Seite auf `127.0.0.1` zugreifen sollte. Der Prüfstand läuft nun über einen echten lokalen HTTP-Origin und ist grün. Das ist kein Produktfehler und kein Windows-/VPS-Beleg.
- Offen für den nächsten Baustein: native Windows-Client-Anbindung, Build-/EXE-Paket, TLS/Pairing für VPS und reale Capture-Quelle.

## B0/B1 — Core und Playwright grün

- Verträge für Agent, Target, Capability, Lease, Binding und ActionRequest.
- Fail-closed Policy für unbekannte Ziele, fehlende Bindung, fehlende Capability, Lease-Ablauf und Not-Aus.
- Core-Beleg: `/root/werkraum/augen_haende_bridge/tests/evidence/B0_B1_EVIDENCE.md`.
- Playwright-Beweis: `PW-B0-01`, `PW-B0-02`, `PW-B1-01` PASS in `/root/werkraum/augen_haende_bridge/tests/evidence/B0_B4_PLAYWRIGHT_EVIDENCE.md`.

## B2 — Core und Playwright grün

- In-Memory-Loopback mit `action.requested` und Policyentscheidung.
- Noch kein Plattform-Dispatch.
- Core-Beleg: `/root/werkraum/augen_haende_bridge/tests/evidence/B2_EVIDENCE.md`.
- Playwright-Beweis: `PW-B2-01` PASS in `/root/werkraum/augen_haende_bridge/tests/evidence/B0_B4_PLAYWRIGHT_EVIDENCE.md`.

## B3 — Core und Playwright grün

- VisionSession mit `start`, `pause`, `resume`, `stop`.
- Begrenzter Frame-Ring, empfängerbezogene Sichtbarkeit und Scrub-Branch.
- Core-Beleg: `/root/werkraum/augen_haende_bridge/tests/evidence/B3_EVIDENCE.md`.
- Playwright-Beweis: `PW-B3-01` und `PW-B3-02` PASS in `/root/werkraum/augen_haende_bridge/tests/evidence/B0_B4_PLAYWRIGHT_EVIDENCE.md`.

## B4 — Core und Playwright grün

- Input-Arbitrator mit Target-Cage, Lease-Vorprüfung, menschlichem Override und Not-Aus.
- Core-Beleg: `/root/werkraum/augen_haende_bridge/tests/evidence/B4_EVIDENCE.md`.
- Playwright-Beweis: `PW-B4-01` bis `PW-B4-03` PASS.
- Plattformdispatch bleibt bewusst noch offen.

## H1 — Creative Harness dogfoodet

- Harness-Core: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/harness.py`.
- Playwright startet den Harness über die sichtbare Oberfläche.
- Nachgewiesen: Action-Node, Observation-Node, Gate-Node, Checkpoint und Branch.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/H1_HARNESS_PLAYWRIGHT_EVIDENCE.md`.
- Die Harness-Ausführung bleibt bis zum echten Adapter rein deklarativ; kein versteckter Plattformdispatch.

## B4.5a — Terminal-Inspector und Live-Target-Switcher grün

- Die sichtbare Bridge-/Regie-Surface bleibt auf Windows; Linux-KDE-Desktops und vorhandene Original-Terminals bleiben Targets.
- Read-only-Baseline der laufenden Konsole-Sessions: `org.kde.konsole-396627`, `org.kde.konsole-396725`, `org.kde.konsole-396779`, `org.kde.konsole-1060933`.
- Konsole stellt für die Baseline Scrollback, Session-PID und Foreground-PID über D-Bus bereit.
- Der neue read-only Adapter entdeckt vier reale Konsole-Sessions und liest einen echten Scrollback-Snapshot zurück.
- Playwright-Beleg: `/root/werkraum/augen_haende_bridge/tests/evidence/B4_5A_TERMINAL_SWITCHER_EVIDENCE.md` und `/root/werkraum/augen_haende_bridge/tests/evidence/playwright_b4_5_target_switcher.png`.
- Noch nicht behauptet: echte Eingabezustellung oder vollständige Terminal-Parität. Dafür gilt die Kette `accepted -> delivered -> echoed -> observed -> audited`.

## B4.5b — gekäfigte Live-Eingabeprobe grün

- Eine eigene Konsole-Session wird als `terminal-probe` gestartet und nach dem Beleg wieder geschlossen.
- Der Bridge-eigene PTY-Controller sendet ausschließlich eine validierte `printf`-Markerprobe.
- Der echte Scrollback enthält Prompt, ausgeführte Probe und Marker; die sichtbare Pipeline lautet `accepted -> delivered -> echoed -> observed -> audited`.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/B4_5B_CAGED_TERMINAL_PROBE_EVIDENCE.md`.
- Konsole-D-Bus-Input (`sendText`/`runCommand`) und Wayland-virtual-keyboard wurden ehrlich als gesperrte Alternativen dokumentiert.
- Kein Input in laufende Codex-, Claude- oder Gemini-Sessions.

## B4.6 — Referenz-Surface statt Homepage grün

- Die sichtbare Oberfläche wurde aus der Referenzlogik gebaut: Windows bleibt die
  einzige Bridge-/Regie-Surface; Linux-KDE-Desktops und Original-Terminals sind
  auswählbare Ziele.
- Sichtbar und interaktiv bewiesen: Zielwechsel, vier Agenten-Rauten, vier
  Terminalflächen, Regie unten links, Fensterscanner unten rechts je Terminal,
  individuelle Mikrofon-/Kamera-Schalter, Regiespruch, Transparenz und Drag einer
  Raute.
- Pfeile sind ausschließlich beschriftete visuelle Beziehungen. Die Surface ist
  ausdrücklich keine Homepage.
- Playwright-Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/B4_6_REFERENCE_SURFACE_EVIDENCE.md`.
- Screenshots: `/root/werkraum/augen_haende_bridge/tests/evidence/playwright_b4_6_reference_surface.png`
  und `/root/werkraum/augen_haende_bridge/tests/evidence/playwright_b4_6_reference_surface_interaction.png`.
- Das bisherige Proof-Panel bleibt als internes technisches Gate erhalten; es wird
  nicht als gewünschte Benutzeroberfläche ausgegeben.

## Offene Umgebungsnotiz

`graphify update .` wurde versucht, ist aber in der aktuellen Umgebung nicht verfügbar (`graphify: command not found`). Das wird nicht als erledigter Graph-Schritt ausgegeben.

## 2026-09-19 — ChatGPT-Chatkörper und Anti-Terminal-Vertrag

- Doku: `/root/werkraum/docs/augen_haende_bridge/2026-09-19_CHATGPT_ANTI_TERMINAL_VERTRAG.md` trennt Raute, Chatkörper, Anti-Terminal, Bridge und Fensterscanner sowie CHAT-/ACTION-Ereignisse.
- Skill: `/root/werkraum/_codex/skills/augen-haende-greenfield-builder/SKILL.md` trägt jetzt die verbindlichen ChatGPT-Bauregeln: echte MCP-/Web-Session, kein lokaler Dummy, keine impliziten Toolcalls aus normalem Chat, getrennte Absender und getrennter Beweisfluss.
- Harness: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/harness.py` enthält `ChatGPTHarnessRun`, getrennte Ledger-Lanes und die geordnete Erstkontakt-Proofliste. Ein plain-chat-zu-Action-Versuch blockiert fail-closed.
- Tests: neue Core-Tests decken Lane-Trennung, impliziten Toolcall-Block, explizite Aktion, Absenderprüfung und geordnete Beweise ab. Diese Etappe ändert keine Benutzeroberfläche und ist deshalb kein neuer nativer/Playwright-Produktbeleg.
- Grenze: Der reale ChatGPT-Web-/MCP-Rundlauf, die native EXE, der Fensterscanner und die echte Zielbeobachtung bleiben für den späteren Vertikalschnitt offen.

## 2026-09-20 — V3 AI-Strom-Anti-Terminal und MCP-P0

- Doku: `/root/werkraum/docs/augen_haende_bridge/2026-09-20_V3_AI_STROM_ANTI_TERMINAL_MCP_P0.md` hält ChatGPTs Session-Schiffbruchzustände, den providerneutralen Anti-Terminal-Kern, vier AI-Strom-Adapter, das enge `/gesamtatlas`-Profil und die V3-Reihenfolge fest.
- Skill: `/root/werkraum/_codex/skills/augen-haende-greenfield-builder/SKILL.md` verbietet vier kopierte Anti-Terminal-UIs und macht MCP-P0 zu einem kurzen read-only Diagnosezaun.
- Harness: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/harness.py` trägt `MCPPreflightRun`, `MCP_P0_PROOF_SEQUENCE`, `SessionContinuity`, `AI_STREAM_IDS` und `MCP_ACCESS_PATHS`.
- Tests: MCP-P0-Reihenfolge, stateful Session-ID oder expliziter stateless Transportmodus, Atlas-Profil und sichtbare Continuity-/Schiffbruchzustände sind als Core-Tests ergänzt.
- Grenze: Die tatsächlichen Codex-/Claude-/Gemini-MCP-Anschlüsse und der alte Codex-Fehler sind noch nicht live repariert oder abgenommen. Dafür ist MCP-P0 der nächste kurze Diagnose- und Beweisschritt.

## 2026-09-20 — MCP-P0 Live-Read-only-Befund

- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/MCP_P0_LIVE_READONLY_EVIDENCE.md`.
- Die sechs VPS-MCP-Units sind offline als `enabled` markiert; die Ports 8091–8096 lauschen. Die öffentliche ChatGPT-, Codex-, Claude-, Gemini- und Grok-Route antwortet.
- `initialize` liefert real `flextrawurst-vps-mcp` Version `1.1.1`; `tools/list` liefert real 137 Werkzeuge und enthält `atlas_hybrid_search`.
- Der aktuelle Antwortweg liefert keine `Mcp-Session-Id`. Das ist nicht automatisch ein Protokollfehler: Der Legacy-MCP kann stateless sein. Nach dem V3-Harness muss dieser Modus aber ausdrücklich als `stateless` attestiert werden; unbekannt bleibt BLOCKED.
- Ein unauthorisierter harmloser Atlas-Call wird strukturiert mit OAuth-Anforderung zurückgewiesen. `atlas_read_verified` bleibt `NOT_TESTED`; kein Token wurde ausgelesen oder verwendet.
- Der konkrete alte Codex-Befund ist enger: `/vps_system/etc/systemd/system/vps-mcp-codex.service` und Port 8094 existieren; `/config/.codex/config.toml` enthält aber keinen MCP-Servereintrag. Infrastruktur und Client-Aktivierung sind nicht dasselbe.
- Ergebnis: `configured`/`reachable`/`tools/list` belegt, MCP-P0 insgesamt **BLOCKED** bei Modusattestierung und autorisiertem Atlas-Read. Kein EXE-, Windows- oder Fensterscanner-Schritt wird dadurch vorgezogen.

## 2026-09-20 — Greenfield MCP-P0 Runner

- Neuer Runner: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/mcp_p0.py`.
- Der Runner ist providerneutral, read-only und fail-closed. Er prüft `configured`, Erreichbarkeit, `initialize`, `Mcp-Session-Id`, `tools/list` und optional einen autorisierten Atlas-Call mit rückgelesenem Textinhalt.
- Er nimmt öffentliche Basis-URLs direkt an und ergänzt `/mcp` deterministisch. Bearer-Tokens werden nur als In-Memory-Header vom aufrufenden Prozess verwendet; sie erscheinen nicht in Resultat oder Log.
- Tests: `/root/werkraum/augen_haende_bridge/tests/test_mcp_p0.py` ergänzt Fake-Transportfälle für unbekannten Sessionmodus, explizit statelessen Transport, fehlendes Token und vollständigen Read-only-Lauf. Gesamt: 58 Tests grün.
- Live-Dogfood gegen den echten Codex-Klon: Runner erreicht `/mcp`, liest `serverInfo` und blockiert ohne Providerprofil bei `session_mode_unattested`. Mit explizitem `session_mode=stateless` läuft er weiter bis zum fehlenden OAuth-Token. Kein Atlas-PASS erfunden.
- Playwright bleibt für diesen reinen MCP-Transportbaustein nicht der Beweiszeuge; der bestehende Guardian-Witness wird zusätzlich als Regression ausgeführt. Native Windows-Evidence bleibt separat offen.

## 2026-09-20 — MCP Providerprofile

- Der Runner enthält nun vier nichtgeheime Profile für ChatGPT, Codex, Claude und Gemini: öffentliche Route, `ai_stream_id`, `server_id`, `access_path` und expliziter `session_mode=stateless`.
- CLI-Aufruf ist damit `PYTHONPATH=src python3 -m augen_haende_bridge --provider codex` oder weiterhin vollständig explizit mit `--stream` und `--endpoint`. Bearer-Tokens bleiben ausschließlich Prozessinput über `--bearer-env`.
- Grok bleibt absichtlich außerhalb der Greenfield-Providerliste; sein vorhandener VPS-Klon wurde diagnostisch gesehen, aber nicht ungefragt zum Bridge-AI-Strom erklärt.

## 2026-09-20 — V3.1 tragender Terminalkanal

- Herkunft/Scope: neuer Greenfield-Pfad unter `/root/werkraum/augen_haende_bridge/`; der Gemini-Prototyp unter `/root/werkraum/_gemini/windows_bridge/` blieb eingefroren. Vor dem Bauschritt wurde der Git-Sicherheitspunkt `1a79db0f7f` gesetzt.
- Neuer Vertrag: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/terminal_channel.py` erzwingt `session_owned -> pty_connected -> vt_output_received -> rendered -> input_accepted -> input_delivered -> input_echoed -> state_observed -> audited`. Falsche Reihenfolge oder fehlende Evidenz blockieren fail-closed.
- PTY-Adapter erweitert: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/probe_terminal.py` liefert rohe PTY-Bytes zusätzlich zur nativen Konsole-Ausgabe an den Bridge-Controller. Die native Präsentation wird nicht durch den Transportzeugen ersetzt.
- Proof-Surface integriert den Kanal in `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/proof_surface.py` und zeigt den aktuellen sowie den nächsten Kanalzustand. Der Marker bleibt absichtlich ein reversibler `printf`-Probe.
- Tests: `/root/werkraum/augen_haende_bridge/tests/test_terminal_channel.py` prüft exakte Reihenfolge, Evidenzpflicht und Blockierung. Die Gesamtmenge umfasste 62 Tests und war grün.
- Playwright: `/root/werkraum/augen_haende_bridge/tests/playwright_proof.py` lief nach Korrektur des nativen Ausgabe-Fan-outs grün; `/root/werkraum/augen_haende_bridge/tests/playwright_guardian.py` lief ebenfalls grün. Die zugehörigen Browserartefakte liegen unter `/root/werkraum/augen_haende_bridge/tests/evidence/`.
- Evidence: vollständiger Bericht unter `/root/werkraum/augen_haende_bridge/tests/evidence/V3_1_TERMINAL_CHANNEL_EVIDENCE.md`.
- Korrektur im Lauf: Eine erste Variante sendete rohe PTY-Bytes nur an den Controller und ließ dadurch die Konsole-Präsentation leer. Das wurde durch gleichzeitiges Schreiben an native Konsole und Controller behoben; der Test erzwingt nun beide Zeugen.
- Grenze: V3.1 ist ein isolierter Linux-/Konsole-/PTY-Beleg. Windows-ConPTY, native EXE, Fensterscanner, freie Overlay-Hit-Tests und Bindung an laufende Agentensessions bleiben offen.
- Graphify: `graphify update .` bleibt nach Codeänderungen zu versuchen; wenn das Werkzeug fehlt, wird das offen als Umgebungsgrenze dokumentiert.

## 2026-09-20 — V3.2 VT-Rücklese

- Neuer Zustandsreader: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/terminal_renderer.py` verarbeitet den echten rohen PTY-Strom mit Cursor, Text, SGR, grundlegenden CSI-Löschbefehlen, Alternate Screen, Cursor-Sichtbarkeit und Resize.
- Nicht unterstützte VT-Sequenzen bleiben in `unsupported_sequences` sichtbar. Der Reader behauptet damit keine vollständige Terminalemulation.
- Die Proof-Surface zeigt den serialisierten VT-Zustand unter `data-testid="terminal-renderer"`; sie bleibt eine sichtbare browserbedienbare Rücklese, kein nativer Windows-Beleg.
- Tests: `/root/werkraum/augen_haende_bridge/tests/test_terminal_renderer.py` ergänzt Text/Cursor/SGR, Alternate Screen, Unsupported-Readback und Resize. Gesamtmenge: 66 Tests grün.
- Realer Lauf: isolierter PTY-Marker blieb in rohem PTY-Output und nativer Konsole-Rücklese vorhanden; der Terminalkanal endete in `completed`.
- Playwright: `/root/werkraum/augen_haende_bridge/tests/playwright_proof.py` Exit 0; `/root/werkraum/augen_haende_bridge/tests/playwright_guardian.py` Exit 0.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/V3_2_VT_RUECKLESE_EVIDENCE.md`; Konzeptvertrag unter `/root/werkraum/docs/augen_haende_bridge/2026-09-20_V3_2_VT_RUECKLESE.md`.
- Grenze: vollständiger VT-Emulator, Windows-ConPTY, native EXE, Fensterscanner und laufende Original-Agentensessions bleiben offen.
- Graphify: `graphify update .` wurde nach dem Codeversuch ausgeführt und ist weiterhin nicht verfügbar (`command not found`).

## 2026-09-20 — V3.3 PTY-Resize-Roundtrip

- Der besessene Probe-PTY unter `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/probe_terminal.py` besitzt jetzt einen separaten Control-Socket für strukturierte Resize-Anforderungen. Rohes VT bleibt auf dem Ausgabesocket getrennt.
- Der Wrapper setzt `TIOCSWINSZ` und liest `TIOCGWINSZ` direkt aus dem Kernel zurück. Der Proof-Lauf beobachtete 40×120 und übergab diese Größe an `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/terminal_renderer.py`.
- Die Proof-Surface unter `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/proof_surface.py` hat einen sichtbaren `Resize owned PTY to 40x120`-Button und DOM-Rücklese. Kein allgemeiner Shellkanal wurde hinzugefügt.
- Tests: 66 Tests grün; `/root/werkraum/augen_haende_bridge/tests/playwright_proof.py` Exit 0; `/root/werkraum/augen_haende_bridge/tests/playwright_guardian.py` Exit 0.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/V3_3_PTY_RESIZE_EVIDENCE.md`; Konzept unter `/root/werkraum/docs/augen_haende_bridge/2026-09-20_V3_3_PTY_RESIZE_RUECKLESE.md`.
- Grenze: Linux-PTY-Resize ist belegt. Windows-ConPTY, native EXE-/DPI-/Font-Rücklese und der native Fensterscanner bleiben offen.

## 2026-09-20 — V3.4 Windows-Fensterscanner-Kern

- Neuer read-only Adapter: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/windows_scanner.py` inventarisiert vollständigen Windows-Desktop plus sichtbare Top-Level-Fenster über Win32 `EnumWindows`/Rechteck-/Prozess-Rücklese.
- Der Desktop ist immer `default_target_id`; Fenster tragen `windows:window:<hwnd>`, Generation, Rechteck, Z-Order, Prozess-ID/-Pfad und zunächst ausschließlich Capability `inventory`.
- Handle-Reuse wird innerhalb einer Scannerinstanz über Prozess-ID/Fensterklasse in eine neue Generation überführt. Persistente Prozessstartzeit über Neustarts ist noch offen.
- Paired-frame-Gate: `scan()` verlangt `frame_ref` und `frame_hash`; der Scanner erfindet keinen visuellen Beleg und führt selbst noch keinen Capture durch.
- Tests: `/root/werkraum/augen_haende_bridge/tests/test_windows_scanner.py` ergänzt Default-Desktop, sichtbare Fenster, Generationen und fehlenden Frame-Zeugen. Gesamt: 70 Tests grün.
- Playwright Regression: `/root/werkraum/augen_haende_bridge/tests/playwright_proof.py` Exit 0; `/root/werkraum/augen_haende_bridge/tests/playwright_guardian.py` Exit 0.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/V3_4_WINDOWS_SCANNER_CONTRACT_EVIDENCE.md` ist bewusst `OUTCOME: PARTIAL`, weil der Linux-VPS keine native Windows-Abnahme ersetzt. Konzept: `/root/werkraum/docs/augen_haende_bridge/2026-09-20_V3_4_WINDOWS_FENSTERSCANNER_KERN.md`.
- Grenze: kein Windows-Capture, keine virtuellen Desktops, kein Overlay-/Input-Beleg und keine Binding-Ausführung. Der alte Overlay-Prototyp unter `/root/werkraum/augen_haende_bridge/client_windows/overlay_app.py` wurde nicht zum Scanner erklärt.

## 2026-09-20 — Redteam-Korrektur V3.1 Marker-Proof

- Sicherheitspunkt: `669ddeaa5b` vor Codeänderung; Dokumentationspunkt: `dace92830b`.
- Befund aus lokalem Luna-Review und Gemini-Review: `printf '%s\\n' '<marker>'` ließ den vollständigen Marker bereits im PTY-Command-Echo erscheinen. Der Beleg war dadurch ein False Positive, obwohl 70 Tests grün waren.
- Korrektur in `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/terminal_adapter.py` und `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/probe_terminal.py`: gemeinsame `build_probe_command()`-Form `printf-split-marker`; der sichere Marker wird in zwei Argumente geteilt.
- Korrektur in `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/proof_surface.py`: Der Readback-Loop bricht erst ab, wenn roher PTY-Output und nativer Konsole-Readback denselben Marker enthalten.
- Testbeleg: `/root/werkraum/augen_haende_bridge/tests/test_terminal_adapter.py` prüft die Command-Echo-Trennung; vollständige Suite `71 Tests OK`; `/root/werkraum/augen_haende_bridge/tests/playwright_proof.py` und `/root/werkraum/augen_haende_bridge/tests/playwright_guardian.py` jeweils Exit 0.
- Grenze: Diese Korrektur macht den Linux-Probe-Beleg ehrlicher. Sie beweist weiterhin keinen Windows-ConPTY-, EXE-, Win32- oder nativen Overlay-Beleg.

## 2026-09-20 — Redteam-Korrektur V3.4 Win32-ABI

- Sicherheitspunkt: `c9c5b7e820` vor der Codeänderung; Dokumentationspunkt: `c88fc9bc78`.
- Befund aus Claude-, Gemini- und Luna-Prüfung: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/windows_scanner.py` rief Win32-Funktionen ohne explizite `argtypes`/`restype` auf. Das ist auf 64-bit Windows besonders für Prozess-Handles ein echter ABI-Risikopfad.
- Korrektur: `GetSystemMetrics`, `EnumWindows`, Sichtbarkeits-/Rechteck-/Text-/Klassen-/PID-Rücklese sowie `OpenProcess`, `QueryFullProcessImageNameW` und `CloseHandle` verwenden jetzt typisierte `ctypes`-Signaturen; der Enum-Callback-Typ bleibt am API-Objekt gehalten.
- Testbeleg: `py_compile`, Windows-Scanner-Unit-Tests und vollständige Suite `71 Tests OK`.
- Grenze: Es gibt weiterhin keinen echten Lauf von `Win32WindowApi` auf Daniels Windows. Fake-API und Syntaxbeleg ersetzen diesen nativen Plattformbeweis nicht.
# 2026-09-19 — G01 Plattform-Preflight

- Vor der Änderung: Backup-Commit `607489fcd6`.
- Neu: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/preflight.py` meldet Windows-Runner, PyInstaller, Tkinter, KDE-Session, Transportabhängigkeit und offene native/Terminal-Beweise ohne Seiteneffekte.
- Tests: 2 Preflight-Tests grün; vollständige vorhandene unittest-Menge 37 Tests grün.
- Ergebnis: Linux/KDE, Transport und die konkrete read-only-Originalterminal-Rücklese sind lokal sichtbar. Windows-EXE und native Overlay-Capture/Click/Focus/DPI/Stop bleiben `NOT_PROVEN`.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/G01_PREFLIGHT_EVIDENCE.md`.
- Nachtrag: Der vorhandene read-only-Konsole-Adapter entdeckte vier echte KDE-Sessions und las vier echte Scrollback-Snapshots mit Status `observed` zurück. Eingabe in bestehende Sessions bleibt unberührt.
- Windows-Paket: `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge/` mit PyInstaller 6.14.2 unter Windows-Python 3.13.15 in isoliertem Wine gebaut; PE32+ x86-64, SHA256 `9b01def12bced801e3e1f0c589434c1510a25f1123b745292414da717e69b040`.
- Bundle-Smoke: Die EXE startete unter Wine als `Augen & Hände Bridge`-Fenster und wurde als genau gestarteter Testprozess beendet. Daniels echtes Windows bleibt für native Abnahme offen.
- Korrektur nach Nutzerfeedback: Vollbildstart entfernt. Aktuelles Fenster-EXE-Bundle startet unter Wine mit `1180x680` bei `314,60`; aktueller SHA256 `77719ce7479a38cb61e8c25eb90e45f1dd6a93d48d9eff48596c649f9f988e85`.
- Transport-Baustein: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/bridge_runtime.py` kapselt den vorhandenen `BridgeClient` in einem opt-in Hintergrundthread. Konstruktion verbindet nicht automatisch; eingehende Events werden bestätigt, GUI-Thread und Asyncio bleiben getrennt.
- EXE-Anbindung: Der native Einstieg lädt den Transport nur mit vollständiger `BRIDGE_URL`/`BRIDGE_TOKEN`-Konfiguration; ohne beide Variablen bleibt er offline. Empfangene `say`-Events werden sichtbar und mit 3,3-Sekunden-Banner quittiert.
- EXE-Bundle danach neu gebaut: `websockets==16.1.1` und der Bridge-Runtime-Pfad sind enthalten; aktueller EXE-SHA256 `8b118d1a53b606bccb9512ab7180ebf3e8a6cc62b1a96adde7af96d94ba8982f`. 39 Tests grün; Surface für diesen Schritt nicht gestartet.
- BridgeRuntime-Shutdown korrigiert: Socket wird beim Stop sauber geschlossen, der Asyncio-Loop wird nicht mehr hart aus dem GUI-Kontext angehalten.
- Echter Runtime-Integrationstest grün: Loopback-Relay → EXE-Runtime-Thread → `say`-Event → Receipt `received`; vollständige Testmenge 40 Tests.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/G01_EXE_TRANSPORT_BINDING_EVIDENCE.md`.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/G01_WINDOWS_EXE_BUILD_EVIDENCE.md`.

## 2026-09-19 — Recherchevertrag für Target-Capabilities und Proof-Gates

- Herkunft/Scope: Recherchedatei `/root/werkraum/docs/augen_haende_bridge/2026-09-19_HINTERHOEFE_RECHERCHE_TERMINAL_SCANNER_OVERLAY.md`; Greenfield-Harness unter `/root/werkraum/augen_haende_bridge/`; eingefrorener Gemini-Prototyp unangetastet.
- Skill ergänzt: `/root/werkraum/_codex/skills/augen-haende-greenfield-builder/SKILL.md` führt jetzt Capability-Profile pro Target, getrennten Terminal-/Target-Beweis, WorldDOM-Provenienz und fail-closed Proof-Gates verbindlich.
- Harness ergänzt: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/harness.py` unterstützt optionale `required_capabilities`, `required_proofs`, per-Target-Capabilities, attestierte Proofs und vererbt diese beim Branch/Fork.
- Tests ergänzt: `/root/werkraum/augen_haende_bridge/tests/test_harness.py` prüft fehlende Target-Capability, fehlenden Proof und Proof-/Capability-Erhalt im Branch.
- Core-Beleg: vollständige unittest-Menge `42 Tests grün`.
- Graphify: `graphify update .` wurde versucht, ist in der Umgebung aber nicht verfügbar (`graphify: command not found`). Kein Graph-Update behauptet.
- Grenze: Noch kein Windows-Native-Proof, kein echter ConPTY-Adapter und keine Änderung am laufenden Dienst. Diese Etappe verankert nur die Verträge und ihre Core-Prüfung.

## 2026-09-19 — Fensterscanner als erster Augen- und Sicherheitskern

- Neue Hinterhof-Recherche: `/root/werkraum/docs/augen_haende_bridge/2026-09-19_HINTERHOEFE_HAIJAGD_FENSTERSCANNER_AGENT_HARNESS.md`.
- Der Scanner ist jetzt als eigener Vor-Binding-Schritt dokumentiert: vollständiger Windows-Desktop als Default, visueller Frame plus strukturiertes Inventar, stabile Snapshot-/Target-Identität, Capability-Lesung, Binding-Rücklese und Pre-Action-Rescan.
- Neuer Core-Vertrag: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/contracts.py` enthält `TargetScanItem` und `TargetScanSnapshot` mit Generation, Geometrie, Z-Order, Prozess, virtuellem Desktop, Frame-Referenz/-Hash, Herkunft und Capabilities.
- Harness-Vertrag: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/harness.py` führt `SCANNER_PROOF_SEQUENCE` und blockiert Scanner-Beweise außerhalb der Reihenfolge: `SCAN_REQUESTED -> FRAME_CAPTURED -> INVENTORY_READ -> TARGET_SELECTED -> IDENTITY_VERIFIED -> BINDING_CREATED -> BINDING_READ_BACK -> PRE_ACTION_RESCAN -> TARGET_STATE_OBSERVED`.
- Blender-Live-Reference-QA übernommen: Baseline, genau eine Änderung, 10-Hz-Trajektorie bei Übergängen über 100 ms, After-State und strukturierter Readback. Ein Screenshot allein ist kein Ziel-/Binding-Beweis.
- Tests: vollständige unittest-Menge `44 Tests grün`.
- Grenze: Der native Windows-Fensterscanner selbst ist noch nicht implementiert oder auf Daniels Windows abgenommen. Diese Etappe verankert den Vertrag und das Core-Gate, nicht den Plattformadapter.

## 2026-09-19 — Playwright Guardian gegen Harness-Abkürzungen

- Anlass: Die Harness konnte zwar deklarative Proofs und sichtbare Zustände führen, aber ein zu großzügiger Witness hätte eine UI-Behauptung oder einen internen Zustand zu leicht als Erfolg ausgeben können.
- Neuer Vertrag: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/guardian.py` prüft pro Schritt DOM-Projektion, Core-Werte, Audit-Suffix, Target-ID und frischen Scanner-/Frame-Zeugen. `pass`, `blocked` und `unknown` sind getrennt.
- Proof-Surface ergänzt: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/proof_surface.py` zeigt einen als synthetisch markierten `TargetScanSnapshot` mit Inventar, `scan_id` und `frame_hash`, damit der Guardian nicht nur Erfolgstext prüft.
- Playwright-Witness: `/root/werkraum/augen_haende_bridge/tests/playwright_guardian.py` benutzt ausschließlich sichtbare Button-Aktionen, vergleicht DOM und `/api/state`, zeichnet Trace/Screenshots auf und lässt einen fehlenden nativen Windows-Beleg bewusst als `unknown` stehen.
- Core-Test: `/root/werkraum/augen_haende_bridge/tests/test_guardian.py` deckt vollständigen Pass, DOM-Erfolg ohne Audit (`blocked`) und fehlenden nativen Zeugen (`unknown`) ab.
- Ergebnis: `47 Tests in 6.974s OK`; der Guardian-Witness endet mit Exit-Code 0. Die Testumgebung meldet beim bestehenden WebSocket-Sicherheitstest erwartungsgemäß einen ungültigen Origin-Handshake im Serverlog, der Test bleibt grün.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/GUARDIAN_PLAYWRIGHT_EVIDENCE.md`; Trace und Screenshots liegen daneben.
- Grenze: Playwright beweist weiterhin nur browserbedienbare Proof-/Protokollpfade. Die native Windows-EXE, der native Scanner, Fokus/Hit-Test und echte Eingabe bleiben offen.
- Graphify: `graphify update .` bleibt zu versuchen; das Werkzeug war in der Umgebung bereits nicht verfügbar (`graphify: command not found`).

## 2026-09-20 — G02 TargetRegistry-Plattformgrenze und Reviewer-Gate

- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/G02_TARGET_REGISTRY_PLATFORM_EVIDENCE.md`.
- Windows-Default ist jetzt explizit plattformneutral: `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/target_registry.py` lädt auf `os.name == "nt"` keinen lokalen KDE-/qdbus-Adapter. Der Test verbietet dabei sowohl `shutil.which` als auch `subprocess.run` und bleibt grün.
- `refresh_terminals()` entfernt entdeckte geschlossene Sessions, stellt `terminal-1` als synthetischen Fallback wieder her, bewahrt `terminal-probe` und verwirft eine verschwundene Auswahl auf `win-desktop`.
- Core: vollständige Suite `80 Tests OK`; `py_compile` von Registry, Windows-Overlay und Win32-Scanner grün.
- Playwright: `/root/werkraum/augen_haende_bridge/tests/transport_playwright_proof.py` und `/root/werkraum/augen_haende_bridge/tests/reference_surface_proof.py` jeweils Exit 0. Das bleibt ein lokaler/browserbedienbarer Beleg und kein Windows-Nativbeweis.
- Reviewer: Claude Opus bestätigt den Kern mit Follow-ups; Gemini/Antigravity bestätigt den ursprünglichen Windows-Fehler, aber seine späteren `inspect`-Signaturbefunde waren gegen den tatsächlichen Diff falsch und lokal widerlegt.
- ChatGPT wurde nicht als Review behauptet: C2C-Doctor läuft, aber die Projektsession ist noch ungebunden (`session: null`, `projectReady: false`).
- Nächster Stein G03: stabile Identität aus `service + session_path`, getrennte UI-Slot-Abbildung und echter Refresh-/Bridge-Readback-Pfad, bevor Terminal-Input an entdeckte Sessions gebunden wird.
- Graphify: `graphify update .` erneut versucht; in dieser Umgebung weiterhin `command not found`.

## 2026-09-20 — G03 stabile Terminal-Identität und Slot-Sicherheit

- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/G03_TERMINAL_IDENTITY_EVIDENCE.md`.
- `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/target_registry.py` hält die Identität einer Konsole an `service|session_path`; sichtbare `terminal-N`-IDs bleiben reine kompatible UI-Slots.
- Discovery-Reordering, Schließen und Wiedererscheinen verschieben keine laufende Session still unter eine andere Slot-Bindung. `terminal-probe` reserviert seine Identität und wird nicht doppelt entdeckt.
- Zwei Redteam-Korrekturen wurden umgesetzt: Auswahl erst nach Wiederbevölkerung validieren; Probe-Auswahl und synthetischen `terminal-1`-Fallback sofort atomar wiederherstellen.
- Eine weitere Redteam-Runde fand Zwischenzustände während Discovery und Slot-Stehlen durch neue Sessions. Die Registry baut nun einen vollständigen Ersatzsatz, tauscht ihn geschützt aus und reserviert erinnerte Slots in einem ersten Durchlauf.
- Eine weitere Claude-Prüfung fand Fehler-als-leere-Welt und Refresh-Starvation. `TerminalDiscovery` unterscheidet vertrauenswürdige von degradierten Ergebnissen; Coalescing und Sequenzinvalidierung schützen den letzten guten Zustand.
- Core: `90 Tests OK`; `py_compile` für Registry, Terminaladapter, Windows-Overlay und Win32-Scanner grün.
- Playwright: `/root/werkraum/augen_haende_bridge/tests/transport_playwright_proof.py` und `/root/werkraum/augen_haende_bridge/tests/reference_surface_proof.py` jeweils Exit 0. Kein nativer Windows-PASS daraus abgeleitet.
- Nächster einzelner Stein: echter Bridge-Readback-Refresh im Windows-Overlay und danach native Windows-Evidence; noch kein Terminal-Input an laufende Agentensessions.
- Graphify: `graphify update .` nach G03 erneut versucht; `graphify: command not found`.

## 2026-09-20 — G04 Bridge-Readback-Refresh (Code-/Transportstein)

- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/G04_BRIDGE_READBACK_EVIDENCE.md`.
- Scope: Der bestehende Loopback-Relay erhält einen streng read-only
  `target_inventory_request`-/`target_inventory`-Pfad. Die Desktop-Seite kann
  keine Shell-, Input-, Schreib- oder Löschaktion daraus ableiten.
- `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/bridge_runtime.py`
  unterstützt nun Providerantworten, Request-IDs, sichere Message-ID-Längen,
  Idle-Silenz ohne falschen Disconnect und explizite Laufzeitfehler.
- `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/target_registry.py`
  erzeugt ein gefiltertes VPS-Inventar und übernimmt Antworten atomar. Remote-
  Ziele werden namespaced und bleiben ohne Remote-Inspect-Adapter ehrlich
  `unavailable`; Test-Probes werden nicht exportiert.
- Transportvalidierung prüft Capability, Status, Zielart, Feldlängen und
  doppelte IDs. Das Overlay korreliert Antworten, verwirft veraltete/fremde
  Antworten und blockiert die GUI nicht beim Anfordern.
- Core: **PASS**, vollständige aktive Suite `97 Tests OK`; `py_compile`
  **PASS**.
- Der produktive VPS-Einstieg
  `/root/werkraum/augen_haende_bridge/client_vps/bridge_agent.py` verdrahtet
  `TargetRegistry.bridge_inventory()` mit `BridgeRuntime`; der Provider ist
  nicht mehr nur eine Test-Lambda.
- Playwright: **PASS** — echter Chromium-Testpeer, produktiver Registry-
  Provider und Registry-Consumer; Request/Response, Receipt, Identity,
  Namespacing und Auditsequenz sind im Lauf belegt.
- Review: Claude Opus fand einen realen 60-Sekunden-Idle-Disconnect sowie
  mehrere Readback-/Namespace-Lücken; alle priorisierten Befunde wurden
  eingearbeitet und durch Tests ergänzt. Für diesen Abschluss liegt kein neuer
  verwertbarer Gemini-Bericht vor; kein Gemini-PASS wird behauptet.
- Native Grenze: **UNKNOWN** — Windows-EXE, Win32-Capture und native Overlay-
  Evidence müssen auf echtem Windows noch laufen. Der Browserbeleg wird nicht
  als Windows-Abnahme ausgegeben.
- Graphify: erneut versucht; Werkzeug fehlt weiterhin (`graphify: command not found`).

## 2026-09-20 — G05 Windows-EXE-Paket und isolierter Start-Smoke

- Herkunft/Scope: ausschliesslich das aktuelle Greenfield-Programm unter
  `/root/werkraum/augen_haende_bridge/`; keine alte Surface und kein alter
  Gemini-/EXE-Pfad wurden wiederbelebt.
- Sicherheitspunkt vor dem Paket-Write: `09923aa524` — `backup: vor G05 Windows-EXE-Bundle`.
- Der erste Embeddable-Python-Build wurde verworfen, weil Tkinter darin nicht
  vorhanden war. Danach wurde in einem isolierten Wine-Prefix ein
  vollstaendiger Windows-Python-3.13.5-Installer verwendet. Das Bundle wurde
  mit PyInstaller 6.14.2 und `websockets` 16.1.1 als `--onedir --windowed`
  erzeugt.
- Lieferpfad:
  `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge/AugenUndHaendeBridge.exe`
- Paketbeleg: **PASS** — `file` meldet `PE32+ executable for MS Windows`,
  x86-64; Tkinter, Tcl/Tk und `_tkinter.pyd` liegen im zugehörigen
  `_internal`-Bundle. SHA256 der EXE:
  `573f58992eb859c347d50965edb9f605f7b4dab9367ebbcf579e5edd6e7c8e0f`.
- Start-Smoke: **PASS** — die gebaute EXE blieb unter Wine acht Sekunden
  lebendig; ein laufender UI-Test fand das Fenster `Augen & Hände Bridge` mit
  `1180x680` bei `+138+60`. Der temporäre Testprozess wurde durch sein
  Timeout beendet.
- Regression: **PASS** — 97 Unittests, der echte Chromium-
  `transport_playwright_proof.py` mit Produktions-Inventory-Provider und
  `reference_surface_proof.py` liefen erneut durch. Der erwartete ungültige
  Origin-Handshake erscheint nur als negativer Sicherheitstest im Log.
- Native Windows: **UNKNOWN** — Wine ist kein Beleg für Daniels echtes
  Windows. Native Win32-Capture-, DPI-, Fensterscanner-, Fokus- und
  Eingabeprüfung sind weiterhin offen. Der Transport bleibt absichtlich
  Loopback-only und ist kein öffentlicher VPS-Tunnel.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/G05_WINDOWS_EXE_PACKAGE_EVIDENCE.md`.
- Graphify: `graphify update .` bleibt nach dem Paket-/Dokumentationsschritt
  zu versuchen; das Werkzeug ist in dieser Umgebung nicht installiert.

**G05-Ergebnis: PARTIAL.** Das EXE-Paket ist jetzt real vorhanden und startet
als gebündeltes Programm; der nächste Stein ist der echte native Windows-
Erstkontakt, nicht eine weitere Oberfläche.

## 2026-09-20 — G06 Gebündelter Windows-Erstkontakt unter Wine

- Herkunft/Scope: der aktuelle EXE-Pfad und der bestehende Loopback-Relay;
  keine öffentliche Verbindung, keine alte Surface und kein Terminal-Input.
- Der native GUI-Einstieg setzt seinen sichtbaren Fenstertitel bei einer
  empfangenen `say`-Nachricht auf `Augen & Hände Bridge · say-received`.
  Dadurch kann der externe Smoke nicht nur Prozessleben, sondern einen
  sichtbaren Renderzustand rücklesen.
- Neuer reproduzierbarer Test:
  `/root/werkraum/augen_haende_bridge/tests/windows_exe_wine_first_contact.py`.
  Er startet die offizielle gebündelte EXE unter dem isolierten Wine-Prefix,
  verbindet einen echten lokalen Relay-Agenten, bestätigt das initiale
  read-only Terminalinventar, sendet ein `say`-Ereignis und liest den
  sichtbaren Fenstertitel über `xwininfo` zurück.
- Paket nach dem G06-Rebuild:
  `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge/AugenUndHaendeBridge.exe`
  mit SHA256
  `e011b27ecb6500cd00ec9274f92f5eb2a3a790284e15a54244a7656c7a6dcca9`.
- `PYTHONPATH=src:. python3 tests/windows_exe_wine_first_contact.py`:
  **PASS** — `packaged Windows EXE under Wine; local relay; visible title
  readback`; Fenster `Augen & Hände Bridge · say-received`.
- Die Kette ist damit im isolierten Paket-Smoke beobachtet:
  `connected → target_inventory_request → target_inventory received → say
  forwarded → say received → visible title readback`.
- Native Windows: **UNKNOWN** — Wine ersetzt keinen echten Windows-Desktop,
  Win32-Fensterscanner, DPI-/Fokusbeleg oder native Capture.
- Playwright bleibt **PASS** für den bestehenden browserbedienbaren
  Transport-/Inventory-Beleg; der EXE-Smoke wird nicht als Playwright-
  Windowsbeweis ausgegeben.
- Evidence:
  `/root/werkraum/augen_haende_bridge/tests/evidence/G06_WINDOWS_EXE_FIRST_CONTACT_EVIDENCE.md`.

**G06-Ergebnis: PARTIAL.** Der gebündelte Prozess nimmt lokal Kontakt auf und
rendert eine empfangene Nachricht sichtbar. Der nächste echte Nachweis ist
Daniels native Windows-Start mit nativer Ziel-/Fensterrücklese.

## 2026-09-20 — G07 Windows-GDI-Frame und Win32-Fensterscanner unter Wine

- Herkunft/Scope: read-only Augenpfad im aktuellen Greenfield-Programm;
  Windows-GDI-Capture und Win32-EnumWindows werden gekoppelt, aber weder
  Binding noch Eingabe werden daraus abgeleitet.
- Neuer Capture-Körper:
  `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/windows_capture.py`.
  Erzeugt einen begrenzten virtuellen Desktop-Frame, berechnet den SHA256 des
  rohen BGRA-Frames und liefert Zeitstempel, Dimensionen und `frame_ref`.
- Der Overlay-Button `Windows-Fensterscan` und der explizite Testschalter
  `BRIDGE_NATIVE_SCAN_ON_START=1` führen genau einen Capture-/Inventory-Lauf
  aus. Der Scan wird nur mit dem frisch erzeugten Frame-Zeugen akzeptiert.
- Der neu gebaute EXE-Hash ist
  `68f55707dedf08ace0cf9de515015df25918996c88fbb236d842a7bad0e0418d`.
- Übergabearchiv:
  `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge-G07-win64.zip`
  mit SHA256
  `291d682c905dbcd7352f1ae141eb9c82044de6e9843ade87b5bb8424c2fee34e`.
- Core: **PASS**, vollständige Suite jetzt 99 Tests.
- Wine-API-Smoke:
  `/root/werkraum/augen_haende_bridge/tests/windows_exe_wine_native_scan.py`:
  **PASS** — die gebündelte EXE erzeugte Frame-/Scannerstatus und `xwininfo`
  las `Augen & Hände Bridge · scan-received:2` zurück.
- Regression: G06-Paket-/Relay-Erstkontakt, Transport-Playwright und
  Referenzregression liefen erneut durch.
- Native Windows: **UNKNOWN** — Wine ist kein nativer Windows-Host. Offen
  bleiben echte Desktopdaten, DPI, Capture-Rücklese, virtuelle Desktops und
  native Fensterauswahl auf Daniels Rechner.
- Evidence:
  `/root/werkraum/augen_haende_bridge/tests/evidence/G07_WINDOWS_CAPTURE_SCANNER_EVIDENCE.md`.

**G07-Ergebnis: PARTIAL.** Der EXE-Körper besitzt jetzt einen echten
read-only Windows-GDI-/Win32-Augenpfad im Paket-Smoke. Der nächste Stein ist
die native Windows-Abnahme und danach die sichere Zielauswahl/Binding-Kette;
keine Eingabe wird aus diesem Scan behauptet.

## 2026-09-20 — G08 Aktueller VPS-Relay und sicherer Windows-Hand-off

- Herkunft/Scope: aktueller Greenfield-Transport unter
  `/root/werkraum/augen_haende_bridge/`; der historische Port `9880` und der
  entfernte Gemini-Prototyp bleiben unberührt.
- Neuer aktiver VPS-Einstieg:
  `/root/werkraum/augen_haende_bridge/client_vps/bridge_server.py`.
  Er startet den bestehenden Relay und den bestehenden read-only
  `TargetRegistry`-Agenten gemeinsam, bindet nur `127.0.0.1` und verwendet
  standardmäßig Port `19880`.
- Die G08-Grantstruktur bleibt getrennt: Windows darf Frames veröffentlichen
  und Inventar anfordern; der VPS-Agent darf nur Inventar veröffentlichen.
  Tokens kommen ausschließlich aus den Umgebungsvariablen
  `BRIDGE_DESKTOP_TOKEN` und `BRIDGE_AGENT_TOKEN`.
- Neuer Windows-Hand-off:
  `/root/werkraum/augen_haende_bridge/client_windows/start_with_ssh_tunnel.ps1`.
  Er baut einen SSH-LocalForward
  `127.0.0.1:19880 -> VPS:127.0.0.1:19880`, setzt die EXE auf den lokalen
  WebSocket und beendet beim Ende ausschließlich seinen eigenen SSH-Prozess.
- Core: **PASS**, neue Token-/Grant-/Launcher-Verträge grün.
- Live-Relay-Smoke:
  `/root/werkraum/augen_haende_bridge/tests/bridge_server_smoke.py`:
  **PASS** — aktueller Entry-Point, eigener VPS-Agent, Desktop-Client,
  read-only `target_inventory` empfangen und bestätigt.
- Native Windows/echter SSH-Login: **UNKNOWN** — Linux kann den nativen
  Windows-/OpenSSH-Hand-off nicht abnehmen.
- Evidence:
  `/root/werkraum/augen_haende_bridge/tests/evidence/G08_SSH_RELAY_HANDOFF_EVIDENCE.md`.

**G08-Ergebnis: PARTIAL.** Der aktuelle Relay-/Agent-Hand-off ist lokal real
bewiesen und verwendet nicht den alten Listener. Offen bleiben der echte
Windows-Start, der SSH-Ende-zu-Ende-Beleg und danach die read-only
Zielauswahl/Binding-Rücklese.

## 2026-09-20 — G09 Read-only Zielauswahl und Binding-Rücklese

- Herkunft/Scope: aktueller Scanner-/Target-Vertrag unter
  `/root/werkraum/augen_haende_bridge/`; kein natives Windows-Hit-Testing und
  keine Eingabe wurden aus dem Core abgeleitet.
- Neuer Core:
  `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/read_only_binding.py`.
  Eine Auswahl speichert Target-Generation, Scan-ID und den gekoppelten
  Frame-Hash/-Verweis. Der Rückleser fail-closed bei fehlendem Target,
  Generation-Wechsel, Frame-Wechsel, Unsichtbarkeit oder fehlender
  Beobachtungsfähigkeit.
- Das Binding gewährt ausschließlich `Capability.OBSERVE`; es erstellt keine
  Lease und keinerlei `INPUT`-/`TERMINAL`-Recht.
- Core: **PASS**, fünf neue Tests; Gesamtsuite **112 Tests OK**.
- Native Windows: **UNKNOWN** — Auswahl, Hit-Testing und native Rücklese
  bleiben offen.
- Playwright: **NOT_APPLICABLE** für diesen reinen Core-Schritt; die bestehende
  Transport-/Referenzregression bleibt separat grün zu halten.
- Evidence:
  `/root/werkraum/augen_haende_bridge/tests/evidence/G09_READ_ONLY_BINDING_EVIDENCE.md`.

**G09-Ergebnis: PARTIAL.** Der sichere Binding-Datenkern trägt jetzt die
spätere native Zielauswahl. Der nächste echte Nachweis ist native Windows-
Auswahl/Binding-Rücklese; danach folgen erst Overlay-Anker und Eingabegates.

## 2026-09-20 — G10 Nativer Windows-Acceptance-Witness vorbereitet

- Herkunft/Scope: Windows-Seite des aktuellen Greenfield-Bundles; der Witness
  wiederverwendet den G08-SSH-Launcher und den G07-Testschalter.
- Neuer Witness:
  `/root/werkraum/augen_haende_bridge/client_windows/native_acceptance_witness.ps1`.
  Er liest den eigenen EXE-Fensterzustand über `user32.dll`, wartet auf den
  nativen `scan-received:<n>`-Marker und schreibt JSON plus Screenshot.
- Der bestehende Launcher erhielt einen expliziten
  `-NativeScanOnStart`-Schalter. Token bleiben Umgebungsvariablen; kein
  zweiter Tunnel und keine Eingabe werden eingeführt.
- Contract: **PASS**, fünf statische PowerShell-Vertragsprüfungen.
- Native Laufzeit: **UNKNOWN** — dieser VPS hat keinen echten Windows-Host;
  der Witness wurde nicht als ausgeführt behauptet.
- Binding: **NOT_EXERCISED** — G09-Datenkern ist vorbereitet, aber der native
  Auswahl-/Rückleselauf folgt nach dem ersten Windows-Beleg.
- Evidence:
  `/root/werkraum/augen_haende_bridge/tests/evidence/G10_NATIVE_ACCEPTANCE_WITNESS_EVIDENCE.md`.

- Übergabearchiv:
  `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge-G10-win64-handoff.zip`,
  SHA256 `4730f1ec4786090d5fa70ea01c0cccdb94bcffa81b494816ff42d9e96a35c129`.

**G10-Ergebnis: PARTIAL.** Die native Abnahme hat jetzt einen reproduzierbaren
Windows-seitigen Zeugen. Der nächste Außenbeleg muss auf Daniels Windows
erzeugt werden; danach wird die tatsächliche Auswahl an G09 gekoppelt.

## 2026-09-20 — G11 Scan → observe-only Binding im EXE-Pfad

- Herkunft/Scope: bestehendes natives Overlay unter
  `/root/werkraum/augen_haende_bridge/client_windows/overlay_app.py`; keine
  neue Surface und keine Inputfähigkeit.
- Nach dem expliziten GDI-/Win32-Scan zeigt der Zielrail die nativen
  Scan-Einträge. Auswahl bewahrt den G09-Frame-/Generationzeugen und führt
  sofort eine read-only Rücklese aus.
- Der explizite Testhaken `BRIDGE_NATIVE_BIND_TARGET_ID` ermöglicht den
  reproduzierbaren Paket-Smoke; ohne ihn bleibt die Auswahl manuell.
- EXE neu gebaut: SHA256
  `265c9fa3713df411864d3dc7d04b8f6f97d34b947e8a7a3db7d1c3a9caf855cd`.
- Core: **PASS**, 114 Tests.
- Wine-Scan→Binding-Smoke:
  `/root/werkraum/augen_haende_bridge/tests/windows_exe_wine_native_binding.py`:
  **PASS** — externes Fenster-Readback meldete zuletzt
  `scan-received:2 · binding-readback`; der Fenstercount ist umgebungsabhängig.
- Native Windows und echter menschlicher Klick: **UNKNOWN/NOT_EXERCISED**.
- Übergabearchiv:
  `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge-G11-win64-handoff.zip`,
  SHA256 `0d45d7966ec17484b6396573352d0f9d21fbc78f72a7968c27139705e8307eb1`.
- Evidence:
  `/root/werkraum/augen_haende_bridge/tests/evidence/G11_NATIVE_BINDING_WINE_EVIDENCE.md`.

**G11-Ergebnis: PARTIAL.** Die gebündelte EXE kann jetzt einen aktuellen
Scan-Eintrag in den observe-only Binding-Core führen. Offen bleiben native
Windows-Evidence, echter manueller Klick und die spätere Input-/Terminalkette.

## 2026-09-20 — G12 Manueller nativer Binding-Witness vorbereitet

- Der Witness unter
  `/root/werkraum/augen_haende_bridge/client_windows/native_acceptance_witness.ps1`
  akzeptiert jetzt `-WaitForManualBinding`.
- Nach dem read-only Scan wartet er sichtbar auf Daniels Klick im Zielrail und
  liest anschließend nur `binding-readback`, Fensterzustand, Screenshot und
  JSON zurück.
- Contract: **PASS**, sechs statische Tests.
- G12-Evidence-Validator: **PASS** — vier read-only JSON/PNG-Tests unter
  `/root/werkraum/augen_haende_bridge/tests/test_native_binding_evidence.py`;
  der Validator selbst liegt unter
  `/root/werkraum/augen_haende_bridge/tests/validate_native_binding_evidence.py`.
- Nach dem Handoff-Pfad-Fix: vollständige Suite **121 Tests OK**.
- Automatische Eingabe: **PASS ausgeschlossen** — kein `SendInput`, kein
  `PostMessage`, kein automatischer Klick.
- Echter Windows-/Klicklauf: **UNKNOWN** — noch nicht auf Daniels Rechner
  ausgeführt.
- Evidence:
  `/root/werkraum/augen_haende_bridge/tests/evidence/G12_MANUAL_BINDING_WITNESS_EVIDENCE.md`.
- Übergabearchiv:
  `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge-G12-win64-handoff.zip`,
  SHA256 `f7c6e42695af367261703bd01a62aa7d908af85781059a3f5d882850b89c047a`.

**G12-Ergebnis: PARTIAL.** Die manuelle native Abnahme ist jetzt als sicherer
Witness vorbereitet; der nächste Beleg muss von Daniels Windows kommen.

## 2026-09-20 — PLAN-G01 Fundament (Claude)

- Gemeint ist das G01 aus `docs/augen_haende_bridge/PLAN.md` (nicht Codex' frühere Bauzählung G01–G12).
- Sicherheitspunkt vor dem Schritt: `b5f79ec197`. Neu angelegt wurden nur Dateien unter `augen_haende_bridge/probes/` und der Evidence-Bericht.
- Bauumgebung: isolierter Wine-Prefix `/config/wine-bridge-build/prefix` mit Windows-Python 3.13.5, PyInstaller 6.14.2, websockets 16.1.1.
  Rust scheidet aus: nur Linux-Ziel, kein Windows-Std, kein mingw-w64.
- Proben: `probes/window_probe.py` (Win32 über ctypes: Deckkraft, Rautenform, Trefferlogik per `WindowFromPoint`, Textfokus, Esc, DPI, Ausschluss aus der Aufnahme) und
  `probes/conpty_probe.py` (ConPTY unter Wine: Ausgabe landet nicht in der Pipe, also nicht testbar).
- Entscheidungen: Terminal = Linux-PTY der Bridge auf dem VPS über das Relay (BE01/BE02); Stack = Python mit ctypes-Fenstern, Terminal-Emulationsbibliothek, Pillow, PyInstaller `--onedir`.
- Ausgangstests: 121 Tests OK (vd1). Preflight: KDE live, Windows-Runner und native Fensterbeweise `NOT_PROVEN`.
- Native Windows: **UNKNOWN** — Deckkraft sichtbar, Durchklicken mit der Hand, DPI und der Ausschluss aus der Aufnahme gehen als Selbsttest-Übergabe in G02.
- Graphify: `graphify update .` versucht, `graphify: command not found` — Blocker offen, wie bei Codex' letzten Läufen.
- Harness: der Zyklus wurde als `BuildCycleRun` mit `FocusContract` attestiert (`completed`), Datei `tests/evidence/PLAN_G01_BUILD_CYCLE.json`.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/PLAN_G01_FUNDAMENT_EVIDENCE.md`.

**PLAN-G01-Ergebnis: PASS** für Umgebung, Fenster-API unter Wine und Festlegungen; **UNKNOWN** für alles, was nur auf Daniels Windows sichtbar wird.

## 2026-09-21 — PLAN-G02 Zyklus A: VPS-Seite (Claude)

- Gemeint ist G02 aus `docs/augen_haende_bridge/PLAN.md` (die exe mit dem kompletten ersten Körper, BE03); dieser Zyklus ist der erste von mehreren und deckt nur die Linux-Seite ab.
- Sicherheitspunkt vor dem Zyklus: `56e8cb82a2` (Plan-G01). Geändert wurden nur Dateien der Bridge unter `augen_haende_bridge/`.
- Relay (`src/augen_haende_bridge/transport.py`): neue Nachrichten für Terminal-Liste, Start, Zustand, Schließen, Eingabe, Größe, Ausgabe und `raute_say`; `frame` darf eine `terminal_id` tragen.
  Ströme laufen ohne Journal, Quittung und Ergebnis. Zwei neue Fähigkeiten je Principal (`terminal_control`, `terminal_serve`).
- Starter (`client_vps/terminal_launcher.py`, `bridge_cli.py`, `starts.json`, `orte.json`): startet nur Einträge der Startliste (BE02) in Linux-PTYs, die die Bridge hält (BE01),
  an den Orten Host, vd1, vd2 (`docker exec -it`); Umgebung per Allowlist, Token nie in der Prozessliste; Bildablage je Terminal; Sprech-Socket mit Token je Terminal für `say`/`see`.
  Schließen beendet auch die Prozesse im Container. `bridge_server.py` startet Relay, Starter und den bisherigen Inventar-Agenten gemeinsam.
- Tests: **165 OK** (Ausgangsstand 121). Ende-zu-Ende mit echtem Server-Prozess, echten PTYs, echtem Sprech-Socket; Docker-Weg auf dem Host gegen `virtuellerdesktop1` und `virtuellerdesktop2` geprüft (Start, Größe, Größenänderung, Schließen).
- Windows-Darstellung des Terminals: **UNKNOWN** — kommt in den nächsten Zyklen. Wiederaufsetzen nach einer Trennung: offen.
- Graphify: `graphify update .` versucht, `graphify: command not found` — Blocker weiter offen.
- Harness: der Zyklus wurde als `BuildCycleRun` mit `FocusContract` attestiert, Datei `tests/evidence/PLAN_G02_A_BUILD_CYCLE.json`.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/PLAN_G02_A_VPS_SEITE_EVIDENCE.md`.

**PLAN-G02-A-Ergebnis: PASS** für Relay und Starter auf Linux (Host, vd1, vd2); **UNKNOWN** für alles, was das Windows-Fenster betrifft.

## 2026-09-24 — PLAN-G02 Zyklus B: Fenster-Toolkit-Tests (Claude)

- Ausgangslage: `virtuellerdesktop1` war 3-4 Tage vor diesem Zyklus abgestürzt und wurde über `anthropic_claude`
  wiederhergestellt. Diese Sitzung knüpft an `0682b9c5c3` (PLAN-G02-A) an.
- Fund bei der Wiederaufnahme: nach `0682b9c5c3`, mit Zeitstempeln bis 2026-09-21 00:22 Uhr, lag bereits ein
  vollständiges neues Modul `src/augen_haende_bridge/koerper/` (`win32.py`, `fenster.py`, `menue.py`, `stil.py`,
  `terminal_fenster.py`, `terminal_modell.py`, dazu `tests/test_koerper_terminal_modell.py`) ungecommittet im
  Arbeitsbaum — Stein 3 (Win32-Fenster-Toolkit) und Stein 4 (Terminalfenster). Sicherheitspunkt vor diesem Zyklus:
  Backup-Commit `341708d702` (sichert `koerper/` und vier `docs/opus/`-Advisory-Notizen).
- Umgebung: der `venv` unter `/root/werkraum/.venv` zeigte auf `/usr/bin/python3`, das in diesem Container nach der
  Wiederherstellung jetzt Python 3.14 statt 3.12 ist; `pyte` und `websockets` fehlten dadurch und wurden neu
  installiert (`websockets==16.1.1`, passend zum gepinnten Wert). Nebenwirkung: ein vorher installiertes
  `websockets 17.1` wurde systemweit auf 16.1.1 zurückgesetzt.
- Build-Schritt: fünf neue Testdateien für den Win32-Körper-Teil geschrieben (keine Produktionsdatei geändert):
  `test_koerper_win32.py`, `test_koerper_stil.py`, `test_koerper_menue.py` (reine Helfer bzw. Windows-Gating),
  `test_koerper_fenster.py` (`Fenster.nachricht`- und `_wndproc`-Dispatcher per `object.__new__`-Fixture ohne
  echtes Fenster) und `test_koerper_terminal_fenster.py` (Geometrie, Trefferprüfung, Maus-Auswahl-Drag,
  Knopf-/Mausrad-/Tastatur-Routing inkl. AltGr und UTF-16-Ersatzpaaren, Zwischenablage, Timer-Routing — ebenfalls
  per `object.__new__`-Fixture mit gestubbten Win32-Methoden statt echtem Fenster).
- Tests: **287 gesamt** (Ausgangsstand 183), 104 neue Tests grün. Drei vorbestehende, umgebungsbedingte
  Fehlschläge in `test_terminal_adapter.py` (Erkennung einer echten laufenden Terminalsitzung ohne interaktives
  TTY) bleiben unverändert und sind nicht `koerper`-bezogen.
- Körper-Tor: `python3 tests/pruefe_koerper.py` — PASS (0 von 4 beanstandeten Dingen), prüft aber weiterhin den
  alten `client_windows/overlay_app.py`, nicht `koerper/`; Umstellung des Tors bleibt ein späterer, offener Schritt.
- Graphify: nicht versucht (kein Produktionscode geändert).
- Harness: `BuildCycleRun` mit `FocusContract` unvollständig (Stand `running`, nächste Phase
  `skill_prebuild_read`): beide Skills wurden einmal vor dem Bau gelesen, aber weder unmittelbar vor noch nach
  dem Bau erneut. Datei `tests/evidence/PLAN_G02_B_FENSTER_TOOLKIT_TESTS_BUILD_CYCLE.json`.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/PLAN_G02_B_FENSTER_TOOLKIT_TESTS_EVIDENCE.md`.

**PLAN-G02-B-Ergebnis: PASS** für die reine Logik des Fenster-Toolkits unter Linux (Geometrie, Trefferprüfung,
Tastatur-/Zeichen-Kodierung, Auswahl- und Knopf-Zustandsmaschine, Nachrichtenverteilung); **UNKNOWN** für alles,
was echtes Windows-/Wine-Fensterverhalten braucht. Kein Windows-Overlay wurde gestartet oder behauptet.

## 2026-09-24 — PLAN-G02 Zyklus C: Raute-Fenster (Claude)

- Direkte Fortsetzung von Zyklus B in derselben Sitzung. Sicherheitspunkt vor diesem Zyklus: `a8c892688d`.
- Warum nur die Raute: `ANFORDERUNGEN.md` führt R023 (Raute ist Sprechort), R024 (Name/Farbe/Hotkey/Position),
  R026 (ein Ereignis als Ticker/Banner/Chat gleichzeitig) und R027 (Banner räumlich zur Raute orientiert)
  ausdrücklich als **offen** — keine legt fest, ob Banner, Ticker und Chat eigene Fenster sind oder Teile eines
  gemeinsamen. Das ist eine Architekturentscheidung, die nicht allein getroffen wird. Dieser Zyklus baut deshalb
  nur die Raute selbst; Banner/Ticker/Chat bleiben ausdrücklich offen und werden benannt statt entschieden.
- Build-Schritt: `src/augen_haende_bridge/koerper/raute_fenster.py` (neu) — `RauteFenster(Fenster)`: Rautenform aus
  vier Eckpunkten über `setze_form()` (R118, kein flächiges Overlay), Farbe/Kürzel, eine Ziehen-gegen-Klick-
  Unterscheidung über `maus_position()` (Bildschirmkoordinaten, nicht das client-relative `WM_MOUSEMOVE`-lParam,
  da sich das Bezugssystem sonst mit jedem `SetWindowPos` mitverschiebt), `sagen(text)` als Anschlussstelle für
  den späteren Banner-/Ticker-/Chat-Baustein. `tests/test_koerper_raute_fenster.py` (neu, 12 Tests) per
  `object.__new__`-Fixture wie beim Terminalfenster.
- Tests: **299 gesamt** (Ausgangsstand 287), 12 neue Tests grün. Dieselben drei vorbestehenden,
  umgebungsbedingten Fehlschläge in `test_terminal_adapter.py` unverändert, kein Bezug zur Raute.
- Körper-Tor: `python3 tests/pruefe_koerper.py` — PASS (0 von 4), weiterhin gegen den alten `overlay_app.py`.
- Graphify: nicht versucht (kein Produktionscode außerhalb von `koerper/` geändert).
- Harness: `BuildCycleRun` mit `FocusContract` unvollständig (Stand `running`, nächste Phase
  `skill_opening_read`): beide Skills wurden in diesem Zyklus weder vor noch nach dem Bau gelesen. Datei
  `tests/evidence/PLAN_G02_C_RAUTE_FENSTER_BUILD_CYCLE.json`.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/PLAN_G02_C_RAUTE_FENSTER_EVIDENCE.md`.

**PLAN-G02-C-Ergebnis: PASS** für Form, Zieh-/Klick-Logik und `sagen()` unter Linux; **UNKNOWN** für echtes
Windows-/Wine-Fensterverhalten. Banner, Ticker und Chat bleiben bewusst offen — die Fensterarchitektur dafür ist
eine Entscheidung mit Daniel, kein Implementierungsdetail.

## 2026-09-24/25 — PLAN-G02 Zyklus D: Kamera und Mikrofon (Claude)

- Direkte Fortsetzung von Zyklus C in derselben Sitzung. Sicherheitspunkt vor diesem Zyklus: `970ebda591`.
- Anders als bei der Raute keine offene Architekturfrage hier — nur der bewusst kleinere Umfang der „ersten
  Fassung“ (G02/BE03) gegenüber der vollen G07-Fassung (Pro-Agent-Routing, VAD, PiP-Layout, Replay).
- Build-Schritt: `src/augen_haende_bridge/koerper/kamera.py` und `mikrofon.py` (neu) — injizierbares
  `KameraQuelle`/`MikrofonQuelle`-Backend, `Cv2KameraQuelle`/`SounddeviceMikrofonQuelle` importieren `cv2`/
  `sounddevice` lazy erst bei `oeffnen()`. Echte `KameraFrame`/`AudioBlock`-Objekte mit Sequenz, Aufnahmezeit und
  Herkunft statt eines Booleans (V04-MEDIEN-ATTRAPPE). Mikrofon zusätzlich mit Stummschaltung und
  Push-to-talk/offen-Modus (R041). `pyproject.toml` um die Extras `terminal` (macht die bisher undeklarierte
  `pyte`-Abhängigkeit von `terminal_modell.py` sichtbar) und `medien` (opencv-python-headless, sounddevice)
  ergänzt. `tests/test_koerper_kamera.py`, `test_koerper_mikrofon.py` (neu, 22 Tests): Fake-Quelle für die
  Zustandslogik, dazu je ein echter Lauf gegen dieses Container ohne Kamera-Hardware bzw. ohne PortAudio-Bibliothek
  als Beleg, dass beide Fehlschläge kontrolliert als `KameraFehler`/`MikrofonFehler` ankommen.
- Echte Geräteproben in diesem Container: `cv2.VideoCapture(0).isOpened()` → `False` (kein `/dev/video0`);
  `import sounddevice` → `OSError('PortAudio library not found')`. Beide real, nicht umgangen.
- Tests: **321 gesamt** (Ausgangsstand 299), 22 neue Tests grün. Dieselben drei vorbestehenden,
  umgebungsbedingten Fehlschläge in `test_terminal_adapter.py` unverändert, kein Bezug zu Kamera/Mikrofon.
- Körper-Tor: `python3 tests/pruefe_koerper.py` — PASS (0 von 4), weiterhin gegen den alten `overlay_app.py`.
- Graphify: nicht versucht (`graphify: command not found`, Blocker weiter offen).
- Harness: `BuildCycleRun` mit `FocusContract` unvollständig (Stand `running`, nächste Phase
  `skill_opening_read`): beide Skills wurden in diesem Zyklus weder vor noch nach dem Bau gelesen. Datei
  `tests/evidence/PLAN_G02_D_KAMERA_MIKROFON_BUILD_CYCLE.json`.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/PLAN_G02_D_KAMERA_MIKROFON_EVIDENCE.md`.

**PLAN-G02-D-Ergebnis: PASS** für Zustandslogik und echte Gerätefehler-Behandlung unter Linux; **UNKNOWN** für
echte Aufnahme mit tatsächlicher Kamera-/Mikrofon-Hardware (Daniels native Abnahme) und für das PyInstaller-Bundling
der nativen Abhängigkeiten. Weiterleitung an Relay/Bridge-Runtime ist als Anschlussstelle vorbereitet, noch nicht
verdrahtet.

## 2026-09-25 — PLAN-G02 Zyklus E: Wine-Smoketest für Raute und Terminal (Claude)

- Direkte Fortsetzung von Zyklus D in derselben Sitzung. Das `wine`-Systempaket fehlte nach dem VD1-Absturz
  (`apt-cache policy wine`: „Installed: (none)"); der Prefix `/config/wine-bridge-build/prefix` aus G01 existierte
  unverändert. Auf Daniels Auftrag mit `apt-get install wine` (10.0) wiederhergestellt; der bestehende Prefix
  funktionierte sofort. `sounddevice` im Wine-Python ergänzt (cv2/pyte/pyinstaller/websockets waren schon da).
- Build-Schritt: `probes/koerper_smoketest.py` (neu, im Stil von `window_probe.py`) baut ein echtes `RauteFenster`
  und ein echtes `TerminalFenster` aus `koerper/*.py` unter Wine und liest per `WindowFromPoint`/`GetWindowRect`/
  `GetLayeredWindowAttributes`/`GetWindowRgnBox` zurück — kein Pixel-Screenshot, aus denselben Gründen wie schon in
  G01 (Xvfb ohne Compositor stellt Layered-/geformte Fenster irreführend dar).
- Ergebnis (zweimal reproduziert, identisch): Raute **PASS** — 48×48 px an der richtigen Position, Deckkraft-Alpha
  87 (= 34 %, R031) korrekt zurückgelesen, Diamant-Region echt gesetzt (Mitte trifft, alle vier Quadratecken
  treffen nicht), Kürzel-Schrift real aufgebaut. Terminal **PASS mit einer offenen Abweichung**: reale
  Schriftauflösung inkl. korrektem Fallback auf Liberation Mono, eingespeister Text erscheint im Modell; aber
  `zeilen_spalten()` liefert nach echter Fenstererzeugung `(23, 79)` statt der angeforderten `(24, 80)` — vermutlich
  ein `GetClientRect`-Rundungsunterschied unter diesem Wine/Xvfb/openbox-Aufbau, nicht korrigiert, offen benannt.
- Blocker gefunden: `cv2` zusammen mit `numpy 2.5.3` stürzt unter dieser Wine-Version beim Import ab
  (`unimplemented function ucrtbase.dll.crealf`, startet `winedbg`, hängt); `kamera.py` konnte deshalb nicht mit
  unter Wine geprüft werden, nur die Fake-Quelle-Tests aus Zyklus D und der reale cv2-Lauf direkt unter Linux.
- Tests: unverändert 321/gleiche drei vorbestehende Fehlschläge (dieser Zyklus fügt keine neuen `unittest`-Tests
  hinzu, der Smoketest läuft nur unter Wine).
- Körper-Tor: nicht erneut ausgeführt (kein Produktionscode geändert).
- Graphify: nicht versucht.
- Harness: `BuildCycleRun` mit `FocusContract` unvollständig (Stand `running`, nächste Phase
  `skill_opening_read`): beide Skills wurden in diesem Zyklus weder vor noch nach dem Bau gelesen. Datei
  `tests/evidence/PLAN_G02_E_WINE_SMOKETEST_BUILD_CYCLE.json`.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/PLAN_G02_E_WINE_SMOKETEST_EVIDENCE.md`,
  Rohausgabe `PLAN_G02_E_WINE_SMOKETEST_OUTPUT.json`.

**PLAN-G02-E-Ergebnis: PASS** für Raute-Form/Deckkraft/Trefferlogik und Terminal-Fensteraufbau/Schriftauflösung
unter Wine — hebt beide von reiner Logikprüfung auf reale native Evidence. **UNKNOWN** bleibt: echtes Windows (kein
Wine-Ersatz), cv2 unter dieser Wine-Version, das Terminal-Geometrie-Delta, echte Bild-/Tonaufnahme.

## 2026-09-25 — PLAN-G02 Zyklus F: Nachricht-Fenster (Banner/Ticker) (Claude)

- Direkte Fortsetzung von Zyklus E. Sicherheitspunkt: `7502aed729`. Architekturfrage vorher an Daniel gestellt (drei
  eigene Fenster / Banner+Ticker in der Raute+eigener Chat / ein gemeinsames Begleitfenster / zurückstellen);
  Antwort „so wie es geschrieben steht“ — gemeint der historische Rauten-Anker-Entwurf im Bridge-Skill (Abschnitt 2,
  dort als Orientierung markiert). Zusammen mit R026 („gleiches Ereignis … in drei Darstellungen“) gelesen als: EIN
  Fenster mit zwei zeitlichen Phasen für Banner/Ticker, kein eigenes Fenster je Darstellung. Chat bleibt eigener,
  späterer Baustein.
- Build-Schritt: `src/augen_haende_bridge/koerper/nachricht_fenster.py` (neu) — `NachrichtFenster(Fenster)` mit
  reinen Geometriefunktionen (`banner_position`/`-groesse`, `ticker_position`/`-groesse`: Banner zentriert über der
  Raute mit Abstand, Ticker rechts daneben auf ihrer Mitte) und einer Timer-Zustandsmaschine (Phasenwechsel bei
  3,3 s, Selbstschließung bei 6,6 s Gesamtdauer). `tests/test_koerper_nachricht_fenster.py` (neu, 9 Tests).
  `probes/koerper_smoketest.py` um einen dritten Abschnitt erweitert: echtes `NachrichtFenster` unter Wine, an
  eine echte Raute-Position angehängt, Phasenwechsel direkt ausgelöst (ohne die echten 3,3 s abzuwarten).
- Echter Wine-Lauf (zweimal, identisch): Banner sitzt real oberhalb der Raute (Abstand exakt wie konfiguriert),
  Ticker real rechts daneben und kleiner als der Banner, beide Phasen mit real aufgebauten Schriften.
- Tests: **330 gesamt** (Ausgangsstand 321), 9 neue Tests grün. Dieselben drei vorbestehenden,
  umgebungsbedingten Fehlschläge in `test_terminal_adapter.py` unverändert. Körper-Tor: PASS (0 von 4).
- Graphify: nicht versucht.
- Harness: `BuildCycleRun` mit `FocusContract` unvollständig (Stand `running`, nächste Phase
  `skill_opening_read`): beide Skills wurden in diesem Zyklus weder vor noch nach dem Bau gelesen. Datei
  `tests/evidence/PLAN_G02_F_NACHRICHT_FENSTER_BUILD_CYCLE.json`.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/PLAN_G02_F_NACHRICHT_FENSTER_EVIDENCE.md`,
  Rohausgabe `PLAN_G02_F_NACHRICHT_FENSTER_WINE_OUTPUT.json`.

**PLAN-G02-F-Ergebnis: PASS** für Geometrie und Phasenwechsel unter Linux-Unittest UND unter Wine. **UNKNOWN**:
echtes Windows, der Chat-Baustein (noch nicht gebaut), die Verdrahtung von `RauteFenster.sagen()` zu einem echten
`NachrichtFenster`, das Fade-Out am Phasenübergang (aktuell ein harter Wechsel statt einer Deckkraft-Rampe).

## 2026-09-25 — PLAN-G02 Zyklus G: Chat-Fenster (Claude)

- Direkte Fortsetzung von Zyklus F. Sicherheitspunkt: `ef28cffcf6`. R026: Chat ist die dauerhafte Darstellung
  desselben Ereignisses (im Unterschied zu ephemer Banner/Ticker aus Zyklus F). `TerminalFenster.tippe()`
  (bereits vorhanden) übernimmt den Weg zurück in die Sitzung — `ChatFenster` baut keinen eigenen Kanal, nur einen
  `gesendet`-Callback.
- Build-Schritt: `src/augen_haende_bridge/koerper/chat_fenster.py` (neu) — `ChatFenster(Fenster)`, schließt sich
  anders als `NachrichtFenster` nicht von selbst. Reine Funktionen (`verlauf_anhaengen` mit R045-Verlaufsbegrenzung,
  `sichtbare_zeilen`, `maximaler_versatz`), Tastatureingabe (Zeichen/Backspace/Enter-zum-Senden), Mausrad-Bildlauf,
  blinkender Eingabecursor bei Fokus. Erste Fassung bewusst ohne Zeilenumbruch und ohne Chrome-Knöpfe — offen
  benannt. `tests/test_koerper_chat_fenster.py` (neu, 23 Tests). `probes/koerper_smoketest.py` um einen vierten
  Abschnitt erweitert: echtes `ChatFenster` unter Wine, echte Zeichen getippt und per Enter gesendet.
- Echter Wine-Lauf (zweimal, identisch): eingehende und getippte Nachricht stehen beide korrekt im Verlauf, der
  `gesendet`-Callback feuert mit dem getippten Text, Eingabezeile danach leer, Schrift real aufgebaut.
- Tests: **353 gesamt** (Ausgangsstand 330), 23 neue Tests grün. Dieselben drei vorbestehenden,
  umgebungsbedingten Fehlschläge unverändert. Körper-Tor: PASS (0 von 4).
- Graphify: nicht versucht.
- Harness: `BuildCycleRun` mit `FocusContract` unvollständig (Stand `running`, nächste Phase
  `skill_opening_read`): beide Skills wurden in diesem Zyklus weder vor noch nach dem Bau gelesen. Datei
  `tests/evidence/PLAN_G02_G_CHAT_FENSTER_BUILD_CYCLE.json`.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/PLAN_G02_G_CHAT_FENSTER_EVIDENCE.md`,
  Rohausgabe `PLAN_G02_G_CHAT_FENSTER_WINE_OUTPUT.json`.

**PLAN-G02-G-Ergebnis: PASS** für Verlauf/Bildlauf/Eingabe unter Linux-Unittest UND unter Wine. **Stand nach diesem
Zyklus:** alle vier Körperteile aus BE03 (Terminal, Raute, Banner/Ticker, Chat, dazu Kamera/Mikrofon aus Zyklus D)
existieren als eigene, getrennt getestete Module. Es fehlt keine neue Einzelkomponente mehr, sondern die
**Gesamtverdrahtung**: Fenster aus einer Startliste erzeugen, Callbacks aneinanderhängen, Fensterscanner ans
Terminal anschließen, PyInstaller-Paket bauen.

## 2026-09-30 — PLAN-G02 Zyklus H: Gesamtverdrahtung (ErsterKoerper) (Claude)

- Auslöser: Daniel fragte, ob schon eine exe fertig sei; ehrliche Antwort mit konkreter Lückenliste (kein
  Gesamtprogramm, kein Fensterscanner-Anschluss, kein PyInstaller-Paket, kein echtes Windows). Daniel: „ja so
  meinte ich das. dann rann an die arbeit oder?“ Sicherheitspunkt vor diesem Zyklus: `c46768e552`.
- Build-Schritt: `src/augen_haende_bridge/koerper/scanner_anbindung.py` (neu) — verbindet den Scanner-Knopf mit
  dem unveränderten `windows_scanner.py`/`windows_capture.py` (G01/V3.4): scannen, Ergebnis als natives Popup-Menü
  zeigen, bei Auswahl `terminal.setze_ziel()`. `TerminalFenster.scanner_verbinden()` (neue, kleine öffentliche
  Methode) ergänzt, um den Henne-Ei-Konflikt zu lösen (der echte Callback braucht das schon gebaute Terminal).
  `src/augen_haende_bridge/koerper/erster_koerper.py` (neu) — `ErsterKoerper`: komponiert Raute, Terminal,
  Nachricht, Chat über injizierbare Fensterklassen; Raute.sagen()→Nachricht+Chat, Raute-Klick→Chat auf/zu,
  Chat.gesendet→Terminal.tippe(), Terminal-Scanner→scanner_anbindung. Echte Relay-Anbindung bewusst nicht
  mitgebaut (`terminal_senden` injizierbar, Standard No-Op). 22 neue Tests (7 scanner_anbindung, 1
  scanner_verbinden, 15 erster_koerper), alle ohne Windows/Wine dank durchgängiger Dependency Injection.
  `probes/koerper_smoketest.py` um einen fünften Abschnitt erweitert: ein echtes `ErsterKoerper` unter Wine.
- Echter Wine-Lauf (zweimal, identisch): `raute.sagen()` erzeugt echt ein `NachrichtFenster`, `raute._klick()`
  öffnet echt ein `ChatFenster`, echtes Tippen+Enter im Chat kommt über die volle Kette
  (Chat→Terminal.tippe()→_eingabe()→terminal_senden) echt beim Sende-Callback an. Der **echte** (nicht gefakte)
  `WindowsWindowScanner`/`WindowsScreenCapture` hat unter Wine den echten virtuellen Bildschirm erfasst und die
  soeben selbst erzeugten Fenster in der echten Fensterliste wiedergefunden. Das native Popup-Menü selbst wurde
  bewusst nicht automatisiert (blockierender, auf echte Maus wartender Aufruf) — nur die Scan-/Capture-Ebene davor.
- Tests: **376 gesamt** (Ausgangsstand 353), 22 neue Tests grün. Dieselben drei vorbestehenden,
  umgebungsbedingten Fehlschläge unverändert. Körper-Tor: PASS (0 von 4).
- Graphify: nicht versucht.
- Harness: `BuildCycleRun` mit `FocusContract` unvollständig (Stand `running`, nächste Phase
  `skill_opening_read`): beide Skills wurden in diesem Zyklus weder vor noch nach dem Bau gelesen. Datei
  `tests/evidence/PLAN_G02_H_GESAMTVERDRAHTUNG_BUILD_CYCLE.json`.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/PLAN_G02_H_GESAMTVERDRAHTUNG_EVIDENCE.md`,
  Rohausgabe `PLAN_G02_H_GESAMTVERDRAHTUNG_WINE_OUTPUT.json`.

**PLAN-G02-H-Ergebnis: PASS** für die komplette lokale Verdrahtung unter Linux-Unittest UND unter Wine, inklusive
des echten (nicht gefakten) Fensterscanners. **UNKNOWN**: echtes Windows, die native Menü-Interaktion selbst, die
echte Relay-/Sitzungsverbindung, das Terminal-Geometrie-Delta, cv2/numpy unter dieser Wine-Version, das
PyInstaller-Paket. **Stand:** alle vier Körperteile sind nicht mehr nur einzeln vorhanden, sondern echt
zusammengeschaltet und unter Wine end-to-end durchgespielt.

## 2026-09-30 — PLAN-G02 Zyklus I: Raute klickdurchlässig, Status und Schließen (Claude)

- Vor diesem Zyklus alle Dokumente vollständig gelesen (siehe Bauprotokoll Abschnitt 16); Sicherheitspunkt
  `8ad3805d47`. Skills vor und nach dem Bau per Read-Werkzeug erneut aufgerufen, unverändert.
- Build: `raute_fenster.py` klickdurchlässig nach `ERLEBEN.md`, bedienbar nur bei gedrückter Strg-Taste
  (Timer über `GetAsyncKeyState`), Statusrand, Titel „◆ Name [Hotkey]“; `erster_koerper.py` mit Raute-Menü
  (Status, Chat, Terminal ein/aus, Agent beenden, Bridge beenden).
- Tests: **389 gesamt**, drei bekannte, umgebungsbedingte Fehlschläge in `test_terminal_adapter.py`.
- Wine: ohne Strg fällt ein Klick durch die Raute; mit echt gedrücktem Strg trifft die Mitte, die Ecken nicht;
  losgelassen wieder durchlässig. Playwright nicht anwendbar. Native Windows **UNKNOWN**.
- Harness: `tests/evidence/PLAN_G02_I_RAUTE_KLICKDURCHLAESSIG_BUILD_CYCLE.json` (`completed`).
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/PLAN_G02_I_RAUTE_KLICKDURCHLAESSIG_EVIDENCE.md`.

## 2026-09-30 — PLAN-G02 Zyklus J: Banner und Ticker getrennt (Claude)

- Sicherheitspunkt `61591f367f`. Skills vor und nach dem Bau per Read-Werkzeug erneut aufgerufen, unverändert.
- Build: `nachricht_fenster.py` neu mit `BannerFenster` (Zielbereich, Zug zur Raute, kontinuierliches Ausblenden
  über 3,3 s) und `TickerFenster` (an der Raute, 6,6 s, folgt ihr), beide klickdurchlässig; `ErsterKoerper` erzeugt
  beide gleichzeitig, Zielbereich Standard Arbeitsfläche (R120).
- Tests: **395 gesamt**, drei bekannte, umgebungsbedingte Fehlschläge.
- Wine, echte Zeit: Deckkraft fällt von 237 auf 20 in zwölf Messpunkten; Banner zu nach 3304 ms, Ticker nach
  6607 ms; beide klickdurchlässig. Playwright nicht anwendbar. Native Windows **UNKNOWN**.
- Harness: `tests/evidence/PLAN_G02_J_BANNER_TICKER_BUILD_CYCLE.json` (`completed`).
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/PLAN_G02_J_BANNER_TICKER_EVIDENCE.md`.

## 2026-09-30 — PLAN-G02 Zyklus K: Fensterscanner mit read-only Binding (Claude)

- Sicherheitspunkt `4f833dee8b`. Skills vor und nach dem Bau per Read-Werkzeug erneut aufgerufen, unverändert.
- Build: `scanner_anbindung.py` führt je Knopfdruck einen `HarnessRun` über die `SCANNER_PROOF_SEQUENCE` bis
  `BINDING_READ_BACK` und benutzt `read_only_binding.py` (G09); Fehler sichtbar in der Zielzeile;
  `ErsterKoerper` macht das gebundene Fenster zum Banner-Zielbereich.
- Tests: **398 gesamt**, drei bekannte, umgebungsbedingte Fehlschläge.
- Wine mit echtem Win32-Scanner: sieben Beweisschritte, Binding nur `observe`, gebundenes Rechteck = echtes
  Fensterrechteck, Banner danach im gebundenen Fenster. Popup-Menü-Interaktion und native Windows **UNKNOWN**.
- Offen für Daniel: eigene Bridge-Fenster erscheinen im Inventar als wählbare Ziele.
- Harness: `tests/evidence/PLAN_G02_K_SCANNER_BINDING_BUILD_CYCLE.json` (`completed`).
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/PLAN_G02_K_SCANNER_BINDING_EVIDENCE.md`.

## 2026-09-30 — PLAN-G02 Zyklus L: Anwendung mit Relay-Anschluss (Claude)

- Sicherheitspunkt `39d28ef533`.
- Build: `koerper/anwendung.py` (Verbindung nur mit `BRIDGE_URL`/`BRIDGE_TOKEN`, Startliste, Start per `start_id`,
  Körper je gestarteter Sitzung, Terminalstrom, `raute_say`, Eingabe/Größe/Beenden, gebundenes Bild als JPEG an
  genau diesen Agenten, Sender-Faden), `koerper/bild.py`, Ergänzungen an `ErsterKoerper` (R114: X blendet nur aus).
- Tests: **429 gesamt**, drei bekannte, umgebungsbedingte Fehlschläge. Echter VPS-Weg (Relay, Starter mit PTY,
  Sprech-Socket) dreimal grün: Tippen kommt durch die PTY zurück, der Agent spricht an seine Raute, sieht das
  gebundene Bild, wird beendet.
- Harness: `tests/evidence/PLAN_G02_L_ANWENDUNG_RELAY_BUILD_CYCLE.json` — `running` vor `skill_prebuild_read`, weil
  vor dem Bau keine eigene Skill-Lesung stattfand.
- Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/PLAN_G02_L_ANWENDUNG_RELAY_EVIDENCE.md`.

## 2026-09-30 — PLAN-G02 Zyklus M: Lokaler Not-Aus F12 (Claude)

- Sicherheitspunkt `ee7088726b` (Zyklus L der anderen Instanz geprüft). Hook im eigenen Faden, Sperre im Sender-Faden,
  Menüpunkt in der Raute. Tests: **443**, drei bekannte Fehlschläge. Wine: echter F12-Druck löst aus, Haupt-Thread
  pumpt nicht; keine Latenzaussage. Native Windows UNKNOWN.
- Harness: `PLAN_G02_M_NOTAUS_BUILD_CYCLE.json` bewusst `running` (Lesestand siehe Datei).

## 2026-09-30 — PLAN-G02 Zyklus N: Regie- und Medienleiste (Claude)

- Sicherheitspunkt `1737e988ea`. `regie_fenster.py`, `medien.py`, `bgr_zu_jpeg`, Anbindung in `anwendung.py`.
  Tests: **471**, drei bekannte Fehlschläge. Wine: Trefferprüfung und Klicklogik echt, PASS unter Wine.
- Offen: Mikrofon-Audio ohne Relay-Kind (nicht übertragen), Hardware-Kamera/-Mikrofon ungetestet, native Windows UNKNOWN.
- Harness: `PLAN_G02_N_REGIELEISTE_BUILD_CYCLE.json` bewusst `running`.

## 2026-09-30 — PLAN-G02 Zyklus O: Einstiegspunkt und Körper-Tor (Claude)

- Sicherheitspunkt `0300d4bc4c`. `koerper/haupt.py`, `client_windows/koerper_app.py`, Regie-Menü mit Startliste,
  `pruefe_koerper.py` auf `koerper/`. Tests: **476**, drei bekannte Fehlschläge. Wine aus dem Quellstand gegen echtes
  Relay: Verbindung, Start, Tippen, Rückgabe, F12-Hook. Gebaute exe noch ungetestet; native Windows UNKNOWN.
- Harness: `PLAN_G02_O_EINSTIEG_BUILD_CYCLE.json` bewusst `running`.

## 2026-09-30 — PLAN-G02 Zyklus P: Paket und Übergabe (Claude)

- Sicherheitspunkt `7b44156fa8`. `dist/AugenUndHaendeBridge-G02-win64.zip` (SHA256 `8b31455a…c7a`), Spec, `build_exe_koerper.bat`,
  Versionsinfo, Startanleitung. Wine: gebaute exe (aus Ordner und entpacktem ZIP) verbindet, startet Sitzung, tippt, liest zurück.
  Playwright zuletzt PASS (lokaler Transportbeleg). numpy/cv2 nur als Dateien beigelegt (Wine-Abbruch beim Import).
- **Offene Übergabe: native Windows UNKNOWN.** Details: `tests/evidence/PLAN_G02_P_PAKET_EVIDENCE.md`.
- Harness: `PLAN_G02_P_PAKET_BUILD_CYCLE.json` bewusst `running`.

## 2026-09-30 — Relay-Dienst `bridge-relay.service` (Claude, Auftrag Daniel: „ja, Dienst anlegen“)

- Unit angelegt unter `/etc/systemd/system/bridge-relay.service` (Kopie: `client_vps/bridge-relay.service`), Tokens in
  `/root/werkraum/.agent/bridge-relay.env` (0600, nicht im Repo). Von diesem Container aus **nicht aktiviert**: kein Zugriff
  auf das Host-systemd. Aktivierung muss auf dem Host geschehen (`daemon-reload`, `enable --now`). Bis dahin läuft kein Relay.

## 2026-09-30 — Korrektur `start_with_ssh_tunnel.ps1` (Claude, beim ersten Windows-Start gefunden)

- Beim ersten echten Start von Daniel schloss das Skript den SSH-Tunnel sofort: `& $ExePath` wartet auf ein Fensterprogramm
  nicht, das `finally` beendete danach ssh, die Bridge bekam „Verbindung abgelehnt“. Jetzt `Start-Process -Wait`.
  Nicht in PowerShell getestet (hier keine PowerShell); die Wirkung bestätigt erst Daniels Lauf.
- ZIP neu gepackt (SHA256 `8b31455a03d054f34e2254f643ec70d0df4644eb92c54215de1a1c652e0b0c7a`, Manifest neu, nur das ps1 geändert);
  einzelnes ps1: `dist/start_with_ssh_tunnel_G02.ps1` (SHA256 `75639dcc…4083`).
- Ebenfalls: SSH-Schlüssel des Windows-PC in `/root/.ssh/authorized_keys` (`restrict,port-forwarding,permitopen=127.0.0.1:19880`,
  Sicherung `authorized_keys.bak-vor-bridge-20260930`), Relay-Dienst `bridge-relay.service` auf dem Host aktiv.

## 2026-09-30 — PLAN-G02 Zyklus Q: gemeinsamer Chat, Raute nur vom Agenten (Claude, nach Daniels Korrektur)

- Sicherheitspunkt `3e7b69efd1`. Ein gemeinsamer Chat statt eines Chats je Raute; Daniels Worte (Chat, Regie) nur in den
  Chat und 6,6 s an die Raute, nicht ins Terminal; Raute ohne Klick-Zweck, mit Deckkraft/Größe im Menü. Tests: **487**, drei
  bekannte Fehlschläge; Wine-Fenster und Gesamtweg (simulierter Agent) grün. Neues ZIP 0.2.1-g02, SHA256 `2216a63e…d5f` (0.2.2-g02).
- Offen: laufender Bilderstrom (Agent sieht Daniels Worte nur bei einem Bild), native Windows (außer dem ersten Start), Zeilenumbruch im Chat.
- Harness: `PLAN_G02_Q_CHAT_RAUTE_BUILD_CYCLE.json` bewusst `running`.
- Nachtrag: „Bridge beenden“ ließ bei Daniel die Regieleiste offen. Ursache offen (unter Wine nicht reproduzierbar); Beenden gehärtet
  (Fenster zuerst, jeder Schritt im Log, Notbremse 8 s), ZIP 0.2.2-g02, SHA256 `2216a63e…d5f`.
- Nachtrag: Chat und Regiesprüche gehen standardmäßig „an alle“ (Ticker an jeder Raute), Klick auf „An:“ schaltet durch, F13–F24 einzeln.
  ZIP 0.2.3-g02, SHA256 `ab1f6fc6…0806`. Mehrere Agenten gleichzeitig nur per Test belegt.
- Nachtrag: Raute wurde beim Vergrößern in Startgröße gezeichnet (behoben, unter Wine per Pixel belegt); nach gewünschtem Beenden verschwindet der
  ganze Körper. ZIP 0.2.4-g02, SHA256 `1b45bc17…d278`.
- Nachtrag: Regieleiste verschiebbar (Griff) und mit Deckkraft-Knopf; Fenster-Positionen werden nicht gespeichert. ZIP 0.2.5-g02. Offen: Terminal und Chat pro Ziel einstellbar (Rückfrage an Daniel).

## 2026-09-30 — PLAN-G02 Zyklus S: Sichtbarkeit je Fenster, gespeicherte Einstellungen (Claude, nach Daniels Vorgabe)

- Jedes Fenster (Raute, Terminal je Agent, Chat, Regieleiste) hat eine eigene Regel „immer“ oder „nur bei <Programm>“, Ort/Größe/Deckkraft/Regel bleiben gespeichert
  (`%LOCALAPPDATA%\AugenUndHaendeBridge\einstellungen.json`). Tests: **561** (drei bekannte Fehlschläge). Wine mit echtem notepad/regedit belegt.
  ZIP 0.3.0-g02, SHA256 `bde0d28d…4cd4`. Offen: Programm statt Einzelfenster, native Windows (Spiele), Monitorwechsel.

## 2026-09-30 — PLAN-G02 Zyklus T: Durchklick-Modus, Host-Starteinträge (Claude, nach Daniels Vorgaben)

- Chat, Leiste und Terminal durchklickbar wie die Raute (Strg zum Bedienen), je Fenster abschaltbar und gespeichert; `starts.json` um `claude-host`, `codex-host`, `gemgem-host`
  erweitert (Dienst muss neu gestartet werden); stabile Agentenfarben. Tests **579**. ZIP 0.3.1-g02, SHA256 `559547e5…1724`.

## 2026-09-30 — PLAN-G02 Zyklus U: Bedientaste wählbar, Tastenkombination je Agent, Raute mit Name und Kombination (Claude, nach Daniels Hinweisen)

- Bedientaste Strg/Strg+Alt/Alt/… wählbar (Standard Strg+Alt), Tastenkombination je Agent festlegbar (Erfassen per Tastendruck) und in der Raute sichtbar; Raute jetzt länglich
  (Name + Kombination). Tests **614**. ZIP 0.4.0-g02, SHA256 `863e60d0…9bf59`. Offen: Eingabefeld an der Raute (Doku), Agenten beibringen `bridge_cli say`, nativ ungetestet.
- Korrektur zu Zyklus U: die Tastenkombination gehört dem Agenten; sie öffnet das Eingabefeld an seiner Raute, der Text ist seine Rede. `eingabe_fenster.py`, Tests **637**, Wine mit echtem Hotkey belegt.
  ZIP 0.4.1-g02, SHA256 `7fe1916e…86cf`. Offen: der Agent muss die Tasten drücken können (spätere Eingabe-Hände).

## 2026-09-30 — PLAN-G02 Zyklen V bis Z: Startnachricht, Hände, Bilderstrom, Sprache, Selbsttest (Claude, Auftrag Daniel „alle der Reihe nach“)

- Startnachricht und `hilfe`; Hände (`schreibe`/`raute_tippen`, SendInput, eng begrenzt); laufender Bilderstrom (+ `CAPTUREBLT`); Sprache (Mikrofon → VPS → Whisper large-v3 → Chat/Ticker, `hoere`); Selbsttest (`--selbsttest`, `selbsttest.bat`).
  Tests **784**. ZIP 0.5.0-g02, SHA256 `5e66ee51…ceed3`. Evidence: `tests/evidence/PLAN_G02_V_BIS_Z_EVIDENCE.md`.
- Offen: Dienstneustart durch Daniel; nativer Selbsttest-Bericht; echtes Mikrofon/Kamera nativ.

## 2026-09-30/10-01 — Windows-Zugang für Claude per SSH-Reverse-Tunnel (Claude in `virtuellerdesktop2`, Auftrag Daniel)

Kein Bridge-Code und kein neues Paket. Daniel will, dass Claude auf seinem Windows-Rechner mit Dateien und Befehlen arbeiten kann wie auf dem VPS
(getrennt von Augen und Händen; die Bridge-EXE bleibt davon unberührt). Gewählter Weg: Claude bleibt auf dem VPS, Windows baut einen Reverse-Tunnel auf.

- Kette: Claude-Container → SSH auf den Host (`id_ed25519_hostzugang`) → `127.0.0.1:2222` auf dem Host (Ende des Reverse-Tunnels) → `sshd` auf Windows (nur `127.0.0.1:22`).
  Host-`sshd` erlaubt das (`allowtcpforwarding yes`, `permitlisten any`, `gatewayports no`, also nur Loopback).
- Windows, einmalig: `dist/windows_ssh_einrichten.ps1` (Administrator) installiert den OpenSSH-Server, setzt `ListenAddress 127.0.0.1`, nur Schlüsselanmeldung, trägt Claudes
  öffentlichen Schlüssel in `C:\ProgramData\ssh\administrators_authorized_keys` ein (Admin-Konto: nicht in den Benutzerordner), PowerShell als Standardshell, erzeugt den
  Tunnel-Schlüssel `id_ed25519_claude_tunnel`. Sicherung der `sshd_config` vorher. Erstfassung nannte die Gruppe „Administrators“ beim `icacls`; auf deutschem Windows
  hat das die Dateirechte nicht gesetzt. Jetzt SIDs (`*S-1-5-32-544`, `*S-1-5-18`).
- Host: eigener Schlüssel für den Tunnel in `/root/.ssh/authorized_keys` mit `restrict,port-forwarding,permitlisten="127.0.0.1:2222"` (nur dieser eine Reverse-Forward, keine Shell).
  Sicherung vorher: `authorized_keys.bak-vor-claude-tunnel-20260930`. Der Bridge-Schlüssel (`permitopen="127.0.0.1:19880"`) ist unberührt.
- Tunnel starten: `dist/claude_tunnel.ps1 -VpsHost <VPS-Adresse>` (hält den Tunnel, Wiederaufbau alle 5 s); Daniel hat dazu auf Windows selbst `Claude-Tunnel-starten.bat` in
  `C:\Bridge\neu\` angelegt. Das Fenster muss offen bleiben; kein Autostart, bewusst (macht den Zugang dauerhaft, Daniels Entscheidung).
- Claude-Seite: Schlüssel `/config/.ssh/id_ed25519_zu_windows`, Kurzbefehl `ssh -F /config/.ssh/config win '<PowerShell-Befehl>'` (ohne `-F` liest `ssh` hier die Datei nicht).
- Belegt: Anmeldung als `desktop-lgqcq4r\pc`, Windows PowerShell 5.1, Lesen von `C:\Bridge\neu\Claude-Tunnel-starten.bat`. Daniel: Arbeitsbereich „überall“ (Administrator-Konto).
- Stolpersteine, die bei Daniel auftraten: lange Zeilen aus dem Chat brechen beim Kopieren hart um (Skripte in kurze Zeilen fassen oder als Datei in `dist/` ablegen);
  ein Pfad in Anführungszeichen ohne `&` gibt in PowerShell nur Text aus.
- Offen: Zugang für die anderen Agenten (Codex, Gemini, GPT …) gleichartig bauen, je Agent eigener Schlüssel und eigene Einschränkung, nicht derselbe Schlüssel; Autostart des Tunnels.

## 2026-10-01 — 0.5.5-g02, nativer Selbsttest

Kamera-Öffnen im Faden, Selbsttest mit Zwischenständen und längeren Timeouts, Durchklick-Prüfung mit Vorbedingung.
Nativ: Kamera ok, Mikrofon an allen Geräten stumm (Befund an Daniels Rechner). Details:
`tests/evidence/PLAN_G02_NATIV_SELBSTTEST_055_EVIDENCE.md`. ZIP SHA256 `5f875fea…1fbd`.

## 2026-10-01 — 0.5.6-g02, Terminal: Rechtsklick-Menü, Kopieren ohne harte Umbrüche, sicheres Schreiben

- Rechtsklick im Terminal öffnet ein Menü (Kopieren, Einfügen, Alles markieren, Auswahl aufheben) statt sofort zu kopieren/einzufügen.
- Kopieren: umgebrochene Zeilen (Text läuft bis in die letzte Spalte) werden ohne Zeilenwechsel zusammengesetzt; ein langer Befehl
  bleibt beim Einfügen eine Zeile (vorher: harter Zeilenwechsel an jedem Umbruch).
- `TerminalSession.write` schreibt bis alles angenommen ist (teilweises `os.write`, voller Puffer). Test mit echtem PTY: 100 KB komplett.
- Nicht verändert, bewusst: `MAX_RAUTE_TIPPEN = 500` (Grenze für `bridge_cli schreibe`), `MAX_TERMINAL_INPUT = 8192` je Stück.
- ZIP SHA256 `85cdf015…f621`, nativ noch nicht bedient getestet (Menü kann der Selbsttest nicht auslösen).

## 2026-10-01 — 0.5.7-g02, Terminal: Menüposition, Rollbalken, Rad, Markieren mit Blättern

Befund aus Daniels Test von 0.5.6: Menü erschien an falscher Stelle (Fensterkoordinaten statt Bildschirmkoordinaten), Rad blätterte nicht,
kein Rollbalken, Markierung wanderte beim Blättern nicht mit.
- Menü an `rechteck()`-Ursprung + Klickstelle. Rollbalken rechts (Griff, Klick in die Leiste, Ziehen), Rad 3 Zeilen je Raste.
- Mausrad geht an das Programm, wenn es Mausereignisse angefordert hat (DECSET 1000/1002/1003, SGR 1006) — Vollbild-Oberflächen
  mit eigenem Blättern. [status: offen] ob das Daniels Rad-Problem war (nicht nativ belegt; Alternative: Durchklick-Fenster ohne Strg
  bekommen das Rad nicht).
- Markieren: Auswahl wandert beim Blättern mit; über den Rand ziehen blättert weiter (Autoscroll). Grenze: Text, der den Bildschirm
  verlassen hat, ist nicht Teil einer Auswahl.
- Probe unter Wine: `probes/terminal_rollbalken_smoketest.py`. Tests 836, nur die drei bekannten Fehlschläge.
- `dist/bridge_wechseln.bat` nimmt jetzt `C:\Bridge\AugenUndHaendeBridge-G02-win64.zip`.

## 2026-10-01 — 0.5.8-g02, Selbstbild bei jedem Agenten

Daniel (nach Test von 0.5.7: Markieren/Scrollen ok, Kamera-LED grün, aber „ich sehe mich nirgends“): Das Kamerabild war nur an den Agenten
gegangen, es gab kein Fenster dafür. Neu: `koerper/kamera_fenster.py` — pro Agent ein kleines Fenster mit Daniels Bild (seitenverkehrt wie ein
Spiegel; zum Agenten geht das Bild unverändert), verschiebbar am Kopf, an den Kanten vergrößerbar, transparent (Prozent-Knopf, Mausrad),
durchklickbar wie die anderen Fenster (Bedientaste), Sichtbarkeitsregel, Ort/Größe/Deckkraft gemerkt (`kamera:<Name>`). Erscheint bei „Cam an“,
verschwindet bei „Cam aus“; X blendet nur aus (bis aus/an). Das Fenster steht im Bildschirmausschnitt, den der Agent sieht.
Medien liest für die Vorschau alle 0,2 s, zum Agenten geht weiter nur jedes `takt_s`. Regie-Menü: „Selbstbild: durchklickbar …“.
Probe unter Wine: `probes/kamera_fenster_smoketest.py` (Pixel: links blau, rechts rot = gespiegelt, Farben stimmen). Tests 858, nur die drei bekannten.

## 2026-10-01 — 0.5.9-g02, Terminal-Schriftgröße wie vd1

Daniel: das Bridge-Terminal sieht „etwas anders“ aus als vd1. Per Screenshot (Tunnel, danach gelöscht) verglichen: Zeile 27 statt 19 px,
Zeichenbreite 11,9 statt 8,5 px — Schrift also etwa 1,4-mal so groß. Schriftgröße von 16 auf 12 (`SCHRIFT_PX` in `terminal_fenster.py`), „so wie bei vd1“ (Daniel).
Schriftart (Cascadia Mono), Farben, Rahmen unverändert. Die Deckkraft war nicht das Anliegen (Daniel stellt sie selbst ein); bei 100 % ist das Terminal sauber lesbar.
`dist/bridge_wechseln.bat` entpackt jetzt nach `C:\Bridge\v059` (je Version ein neuer Ordner, v058 wird aufgeräumt).

## 2026-10-01 — 0.6.0-g02, Chat: lange Nachrichten werden umgebrochen

Daniel: bei kleinem Chatfenster sind längere Nachrichten nicht ganz lesbar (die Zeilen liefen am Rand ab; das stand als bewusste Lücke im Kopf von `chat_fenster.py`).
Jetzt: Umbruch an Wortgrenzen bei der gemessenen Fensterbreite (zu lange Wörter zeichenweise), Folgezeilen eingerückt, nur die erste Zeile trägt „[Zeit] Absender:“,
der Bildlauf zählt die umgebrochenen Zeilen, das Ergebnis wird je Verlauf und Breite gemerkt. Probe unter Wine mit echter Schriftmessung: `probes/chat_umbruch_smoketest.py`
(260 px breit: 19 Zeilen, längste 241 px; 600 px breit: 9 Zeilen). Tests 870, nur die drei bekannten Fehlschläge. Installationsordner `C:\Bridge\v060`.
Außerdem festgestellt: `claude-host` startet in `/root`, dort steht die Claude.md mit dem Sessionritual — die Sitzung liest deshalb beim Start sechs Minuten lang alles. Kein Fehler der Bridge.

## 2026-10-01 — 0.6.1-g02, Banner 6,6 s, Box neben der Raute 9,9 s, Daniels Worte nur als Banner

Daniel: sein Text erschien klein neben der Raute, soll aber größer im Bildschirm stehen. Beschluss: Weg 1 Chat; Weg 2 Box neben der Raute (größer, hoch statt lang, 9,9 s);
Weg 3 Banner im Bildschirm (6,6 s, transparenter werdend). Daniels Worte: Chat und Banner, keine Box (`ErsterKoerper.zeige_daniel`). Hinweise der Bridge bleiben Box (`zeige_ticker`).
Banner und Box brechen lange Texte um (`nachricht_fenster.py`, `umbrechen` aus `chat_fenster.py`); die Box bleibt im Bildschirm (links der Raute, wenn rechts kein Platz ist).
`ERLEBEN.md` und `ANFORDERUNGEN.md` mit Vermerk auf die neuen Zeiten umgestellt. Probe: `probes/nachricht_umbruch_smoketest.py`. Tests 875, nur die drei bekannten. Ordner `C:\Bridge\v061`.

## 2026-10-01 — 0.6.2-g02, Banner schmal und hoch, keine Überlappung, Chat-Rollbalken und Sprungknöpfe

Nach Daniels Test mit sehr langem Agententext: Box höchstens 10 Zeilen, Banner höchstens 12 Zeilen (mit „ …“), Banner ≤ 35 % der Zielbreite (schmal und hoch),
Banner und Box weichen einander und der Raute aus (`nachricht_fenster.py`: `schneidet`, `_frei`, `banner_position`/`ticker_position` mit `meiden`; `ErsterKoerper` baut erst die Box, dann das Banner).
Chat: Rollbalken (`griff_rechteck`, `versatz_fuer`), ▲ ▼ springen zum Anfang der vorigen/nächsten Nachricht (`sprung_versatz`), der Text reicht nicht unter den Balken.
Proben unter Wine: `probes/nachricht_umbruch_smoketest.py` (keine Überlappung, Banner 12 Zeilen), `probes/chat_umbruch_smoketest.py`. Ordner `C:\Bridge\v062`.

## 2026-10-01 — 0.6.3-g02, Chat: Zeit und Name größer und farblich abgesetzt

Daniel: im Chat sollen „[Zeit] Name:“ vor der Nachricht größer sein als der Text dahinter und sich farblich als Nuance abheben. Jetzt: Kopf 18 px fett in der Farbe des Absenders, Text 13 px in einer
zur Textfarbe hin gemischten Nuance (`stil.mischen`, 45 %); alle Zeilen so hoch wie die größere Schrift (keine Verschiebung beim Blättern); der Umbruch rechnet die Breite des Kopfs ein.
Tests 905 (Chat), Probe unter Wine ok. Ordner `C:\Bridge\v063`.

## 2026-10-01 — 0.6.4-g02, Startanleitung neu und Paketbau im Repo

Beim Abnahmeprotokoll G02/G03 fiel auf: Die Startanleitung und die `VERSION.txt` des Pakets lagen nur in einem temporären Ordner und waren überholt (Banner 3,3 s, „Chat-Zeilen brechen nicht um“, „nur der erste Start auf Windows gesehen“).
Neu: `client_windows/START_ANLEITUNG.txt` (Platzhalter `@VERSION@`), `client_windows/selbsttest.bat` und `build_paket.sh` (Version aus `haupt.py`, PyInstaller unter Wine mit Fehlerabbruch, Paket zusammenstellen, `VERSION.txt` mit den
verwendeten Versionen, `PAKET_SHA256.txt`, ZIP und `.sha256` nach `dist/`). Keine Programmänderung. ZIP SHA256 `c8f30bf6…7885`, Ordner `C:\Bridge\v064`.

## 2026-10-01 — 0.7.0-g02, G04: Terminal-Wiederaufnahme, Identität, Referenzfälle, Eingabeparität

Der Starter merkt sich je Sitzung die letzte Ausgabe (512 KB); neue Nachricht `terminal_attach` (Stream, kein Journal) spielt sie mit `replay`-Markierung ein; die Bridge fragt nach jedem Verbinden und baut den Bildschirm neu auf.
`terminal_list` trägt `pid` und `gestartet`; andere Prozesse unter derselben ID werden gemeldet. DEC-Linienzeichensatz behoben (`terminal_modell.Strom`). Neue Tests: Referenzfälle (18), Eingabeparität durchs echte PTY (9),
Wiederverbinden gegen den echten Server-Prozess (1), Launcher/Transport/Client/Modell (25). Tests 945, nur die drei bekannten Fehlschläge. **Relay-Neustart nötig** (`systemctl restart bridge-relay`), sonst weist der alte Relay `terminal_attach` ab.
Belege: `tests/evidence/PLAN_G04_TERMINAL_PARITAET_EVIDENCE.md`, `docs/augen_haende_bridge/abnahmen/ABNAHME_G04.md`. ZIP SHA256 `76789f29…3602`, Ordner `C:\Bridge\v070`.

## 2026-10-01 — 0.8.0-g02, G05 geschlossen, G05.5 gebaut, G07 teilweise

Siehe `docs/augen_haende_bridge/abnahmen/ABNAHME_G05_G055_G07.md` und `docs/augen_haende_bridge/prüflisten/PRUEFLISTE_0.8.0.md`. Neue Module: `ziel_halter.py` (Ort der Elemente im Zielfenster), `dateiwahl.py` (Datei-Dialog).
Neue Proben: `probes/identitaet_smoketest.py`, `probes/ziel_halter_smoketest.py`. Tests 1015, nur die drei bekannten Fehlschläge. ZIP SHA256 `02e9f769…5913`, Ordner `C:\Bridge\v080`.

## 2026-10-02 — 0.10.0-g02, G06 bis G14 gebaut

Siehe `bridge_docs/abnahmen/ABNAHME_G11_bis_G14.md` und `bridge_docs/prüflisten/PRUEFLISTE_0.10.0.md`. Neu im Körper: `controller_adapter.py` (virtuelle Controller, uinput und ViGEm-Anbindung ohne Installation), `weltdom_profile.py` (Profile pro Programm, Seite oder Spiel).
Neu im Starter (kein Windows-Update nötig, aber Relay-Neustart): `kapsel_dienst.py` mit Ereignisprotokoll, Kapseln, Zeitlinie, Mischpult, Beobachtung und freiem Chat mit Hauhaucs (`bridge_cli.py chat|kapsel|beobachtung|pult|profil|controller`).
Ledger `.unlazy/g06-g14/gates/`: Knoten 1.1 und 1.3 bis 1.8 erfüllt (1.3 als Ganzes noch einmal laufen lassen). Windows nativ: offen. ZIP SHA256 `62c1eb02…fac5`.

## 2026-10-02 — Praxis-Harness: konkrete Belege und Körperquittung

Auf Daniels Auftrag wurden Claudes zwei Skills und Praxis-Harness geprüft und
repariert. Ansagen warten jetzt auf eine korrelierte Körperquittung; v2-Schritte
verlangen geordnete Aktionsbelege mit Actor, Versuch, Ziel und Ressourcenbindung.
Frische Bilder, gegenseitige Beobachtung, explizit nicht getestete Schritte,
fehlgeschlagene Ledger-Writes und unterbrochene Checkpoints bleiben unterscheidbar.
Ein expliziter Stop speichert ABORTED und wird nach Neustart nicht als RUNNING
fehlgedeutet. Kein Dienst wurde neu gestartet; kein Windows-Paket gebaut.

Belege: `tests/evidence/PRAXIS_REPAIR_2026-10-02_TEST_RUN.txt`,
`tests/evidence/PRAXIS_REPAIR_2026-10-02_PACKET_INTEGRITY.json` und
`tests/evidence/PRAXIS_REPAIR_2026-10-02_REPORT.md`.
Die gezielte Suite umfasst 172 Tests. Körper-Quellcheck: 0/4 Beanstandungen.
Beide Skill-Prüfer und Skill-Creator-Validatoren bestehen. Claude-Lesekopie:
25/25 MATCH. `graphify update .` versucht, Werkzeug nicht installiert.

Grenzen: keine native Desktop-Abnahme; Körper-ACK beweist Backend-Abschluss,
keine sichtbaren Pixel. Drei Terminal-Discovery-Befunde des früheren Gesamtlaufs
bleiben offen. Nächster tatsächlicher Prüfschritt: isolierte native Ansage samt
frischem Zielbild mit zwei verbundenen Agenten; Menüschritte ohne Freigabe bleiben
zurückgestellt. Ausführliche Reparaturchronik: `BRIDGE_PRAXIS_SPIEGELDATEI_2026-10-02.md`.

## Stand nach 0.10.0: G15, Praxis-Harness, Skills, Szenarien, Augen-Fallback, Ampel

- G15 (`5ce4e8236f`): Seeds (`seeds.py`, Zielumfang nur laut `freigaben.json`, markierter Block mit Backup, Ja über offene Fragen) und
  Loops/Goals (`loops.py`, Budget, Stop ohne heimliche Wiederholung), jeweils mit Modul und Tests. Die Abnahme von G15 als eigenes
  Dokument steht aus.
- Praxistest als Graph (`ac7a1aad79`): Lauf auf der Harness (Knoten ansage, lesen, handeln, sehen, urteil, zuschauer, klaeren),
  Starter-Dienst, Werkzeug `test`, Spuren für say, schreibe, see. In der Raute steht nur die Ansage, Urteile stehen im Ledger.
- Skills: bridge-praxistest und skill-schreiben mit Prüfern, Referenzen und Lesbarkeitsregel.
- Szenarien: menschlich, gemgem-allein, nutzerin-anwendungsfaelle (14 Schritte, fünf Anwendungsfälle).
- Bilderstrom: jeder Agent beginnt auf dem ganzen Desktop; ein verschwundenes Fenster und "Bindung lösen" fallen auf den Desktop zurück;
  jede stille Verzweigung schreibt ihren Grund ins `bridge.log`, dazu ein Herzschlag pro Minute (`bilderstrom.py`).
- Ampel (`ampel.py`, `ampel_fenster.py`): ein eigenes Fenster je Agent in dessen Farbe, ruhige Fläche im Ruhezustand, Zeilen bei Auffälligkeit,
  Rechtsklick-Menü mit allen Funktionen und Zustand in Klammern, Chat-Meldung alle 20 s bei Rot, Piepton beim Wechsel auf Rot,
  Behebungen (Desktop binden, Bilder neu starten, Fenster nach vorn, Terminal zurückholen). Hände nach Aktionsart und Programm.
- Desktop vd1: Compositor von Xfwm4 eingeschaltet (Transparenz wirkt).

Praxis auf vd1: Lauf p-451034 mit Opencode als Nutzerin und Claude-Host als Gutachter, `INCOMPLETE_WITH_DEFERRED`. Bestätigt: Schritte 1, 4, 5, 6, 14.
Anders: 3. Nicht getestet: 2, 7 bis 13. Zustände, Ursachen und Belege stehen in `bridge_docs/praxistest/SITZUNGSPROTOKOLL_vd1_2026-10-02_bis_03.md`
und `RUECKWAERTS_ENGINEERING_PRAXISTEST_vd1.md`. Kein neues Windows-Paket; `dist/AugenUndHaendeBridge-G02-win64.zip` ist gegenüber dem
Körper-Stand veraltet.
