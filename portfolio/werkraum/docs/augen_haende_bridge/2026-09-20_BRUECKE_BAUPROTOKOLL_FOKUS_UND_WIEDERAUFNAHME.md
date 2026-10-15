---
datum: 2026-09-20
autor: codex bei Daniels VPS
status: laufendes Bauprotokoll
zweck: Fokus-, Lesungs-, Bau- und Abnahmeprotokoll für den Greenfield-Neubau
---

# Augen & Hände — laufendes Bauprotokoll und Fokusspur

Dieses Dokument ist die fortlaufende Wiederaufnahme- und Bauprotokolldoku für
den aktuellen Greenfield-Neubau unter
`/root/werkraum/augen_haende_bridge/`.

Es ersetzt weder das technische Bautagebuch unter
`/root/werkraum/augen_haende_bridge/BUILD_LOG.md` noch die vollständige
Anforderungssammlung. Es hält zusätzlich fest, was vor einem Bauschritt wieder
gelesen wurde, welcher Skillstand gegolten hat, welche Herkunft bewusst
unangetastet blieb, was wirklich bewiesen wurde und wo der nächste Fokus liegt.
Damit soll ein neuer Codex-Strom nach einem Desktop-, Kontext- oder
Sessionabbruch nicht wieder bei der Oberfläche anfangen und den bereits
erarbeiteten Kern vergessen.

## 1. Verbindliche Reihenfolge pro Bauabschnitt

Die Reihenfolge ist nicht „Skill einmal lesen und dann frei losbauen“. Für
jeden einzelnen Bauabschnitt gilt:

```text
1. Kontext wieder aufnehmen
   → aktuelle Notizen, Fokusspur, relevante Bridge-Dokus, BUILD_LOG, Git,
     Code und vorhandene Evidence lesen

2. Kurz vor dem Bau den aktuellen Bridge-Skill erneut lesen
   → /config/.agents/skills/augen-und-haende-bridge/SKILL.md
   → /root/werkraum/_codex/skills/augen-haende-greenfield-builder/SKILL.md

   Zusätzlich muss der BuildCycleRun einen FocusContract tragen: Ziel,
   nächster einzelner Stein, Erhaltungsanker und verbotene Drift.

3. Sicherheitspunkt setzen
   → vor jeder Änderung ein Backup-Commit im Repository /root/werkraum

4. Einen kleinen Bau- oder Reparaturstein bearbeiten
   → kein paralleler Oberflächen-Großbau und keine stillen Nebenänderungen

5. Beweise ausführen
   → Core-Test, sichtbarer Playwright-Beleg soweit passend und nativer
     Plattformbeleg, sobald die echte Plattform erreichbar ist

6. Unmittelbar nach dem Bau beide Skills erneut lesen
   → prüfen: Ist der Stein mit dem aktuellen Vertrag vereinbar?
   → keine grüne Testzahl als Ersatz für fehlende Plattform-Evidence

7. Diesen Fokus- und Abnahmeeintrag ergänzen
   → tatsächlicher Zustand, Grenzen, Belege, offene Risiken, nächster Stein
```

Der Skill wird also bewusst **vor und nach dem Bauen** gelesen. Das Lesen
danach ist eine echte Abnahmeprüfung, keine dekorative Erwähnung.

## 2. Geltung und Herkunft

Aktuelle Ausführung erfolgt ausschließlich unter
`/root/werkraum/augen_haende_bridge/`.

Der historische Gemini-Prototyp unter
`/root/werkraum/_gemini/windows_bridge/` wurde am 2026-09-20 auf ausdrücklichen
Auftrag aus dem aktiven Baum entfernt. Seine frühere Architektur ist nur noch
über die Git-Historie als Herkunft nachvollziehbar und kein aktueller
Ausführungsvertrag. Überzogene historische Zusagen wie pauschale
Latenz-, Speicher-, VRAM- oder Not-Aus-Garantien werden nicht als bewiesen
übernommen.

Die verbindliche Korrektur dafür steht unter
`/root/werkraum/docs/augen_haende_bridge/2026-09-19_BRUECKE_BAUSTART_PRUEFUNG_UND_VEREINBARUNG.md`.
Der aktuelle Greenfield-Arbeitsvertrag steht unter
`/root/werkraum/_codex/skills/augen-haende-greenfield-builder/SKILL.md`.

## 3. Gelesene Fokusquellen am 2026-09-20

### Werkraum-Wiederaufnahme

- Alle Dateien unter `/root/werkraum/_codex/notizen/` wurden chronologisch
  wieder eingelesen.
- Alle Dateien unter
  `/root/werkraum/_codex/_import_claude_grundriss/notizen/` wurden als
  importierte Referenzspur wieder eingelesen; sie sind keine Codex-Erinnerung.
- `/root/werkraum/_codex/WERKRAUM_KARTE.md` wurde gelesen.
- Die letzten 80 Zeilen von `/root/werkraum/_codex/RESONANZFELD.md` wurden
  gelesen.
- `/root/werkraum/_shared/briefkasten/REGELN.md` und die vorhandenen
  Markdown-Briefe wurden gelesen.
- `/root/werkraum/_codex/tools/delta.sh` wurde ausgeführt. Die sichtbare
  Delta-Spur enthielt vor allem die zuletzt aufgezeichnete ChatGPT-Caller-
  Arbeit und zahlreiche bereits vorhandene Werkraumänderungen; sie wurde
  nicht mit Bridge-Code vermischt.
- `/root/werkraum/graphify-out/GRAPH_REPORT.md` wurde als Architektur-Navigator
  gelesen. `graphify update .` ist in der Umgebung weiterhin nicht verfügbar.
- Das Referenzbild unter
  `/root/visionen/ChatGPT Image 21. Mai 2026, 23_30_02.png` und die
  Quellliste unter
  `/root/werkraum/_claude/ideen/flextrawurst_490_punkte_quellliste.md` wurden
  als übergeordnete Vision gelesen, nicht als direkte Bridge-Abnahme.

### Verbindliche Bridge-Dokumente

- `/root/werkraum/docs/augen_haende_bridge/2026-09-19_BRUECKE_BAUSTART_PRUEFUNG_UND_VEREINBARUNG.md`
- `/root/werkraum/docs/augen_haende_bridge/BRUECKE_VOM_ENDZIEL_RUECKWAERTS_ZUM_START.md`
- `/root/werkraum/docs/augen_haende_bridge/BRUECKE_ALLE_ANFORDERUNGEN_UND_ABNAHMEN.md`
- `/root/werkraum/docs/augen_haende_bridge/2026-09-19_HINTERHOEFE_HAIJAGD_FENSTERSCANNER_AGENT_HARNESS.md`
- `/root/werkraum/docs/augen_haende_bridge/2026-09-19_HINTERHOEFE_RECHERCHE_TERMINAL_SCANNER_OVERLAY.md`
- `/root/werkraum/docs/augen_haende_bridge/2026-09-19_PLAYWRIGHT_GUARDIAN_HARNESS_VERTRAG.md`
- `/root/werkraum/docs/augen_haende_bridge/2026-09-19_CHATGPT_ANTI_TERMINAL_VERTRAG.md`
- `/root/werkraum/docs/augen_haende_bridge/2026-09-19_LUNA-MAX_PLANUNG_MOMENTKAPSELN_HAUHAUCS_OVERLAY.md`
- `/root/werkraum/docs/augen_haende_bridge/2026-09-20_V3_AI_STROM_ANTI_TERMINAL_MCP_P0.md`
- `/root/werkraum/docs/augen_haende_bridge/2026-09-20_V3_1_TERMINAL_CHANNEL.md`
- `/root/werkraum/docs/augen_haende_bridge/2026-09-20_V3_2_VT_RUECKLESE.md`
- `/root/werkraum/docs/augen_haende_bridge/2026-09-20_V3_3_PTY_RESIZE_RUECKLESE.md`
- `/root/werkraum/docs/augen_haende_bridge/2026-09-20_V3_4_WINDOWS_FENSTERSCANNER_KERN.md`
- `/root/werkraum/augen_haende_bridge/BUILD_LOG.md`

Die Wortlaut-Exporte unter
`/root/werkraum/docs/augen_haende_bridge/codex-session-01a0b38d-5ece-75b3-a06e-86bf715f6c36-messages.md`
und
`/root/werkraum/docs/augen_haende_bridge/codex-session-01a0b38d-5ece-75b3-a06e-86bf715f6c36-astra-planung-messages.md`
bleiben Gesprächsprovenienz. Sie dürfen erklären, warum etwas entstand, aber
ein Gesprächssatz gilt nicht automatisch als Implementierungsbeweis.

## 4. Rekonstruierter tatsächlicher Baupunkt

Die Dokus und Git-Historie ergeben diesen belastbaren Stand:

### Bewiesen oder als Core-Vertrag vorhanden

- Transportfundament mit lokalem, authentifiziertem Relay unter
  `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/transport.py`
  und `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/transport_client.py`.
- Agent-, Target-, Capability-, Lease-, Binding- und Action-Verträge sowie
  fail-closed Policy.
- VisionSession, Frame-Ring, Empfängertrennung und Scrub-Branch als Core.
- Creative Harness mit Checkpoints, Branches, Target-Capabilities und
  Proof-Gates unter
  `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/harness.py`.
- Playwright Guardian unter
  `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/guardian.py`.
  Browserbeweise werden von nativen Beweisen getrennt; `unknown` bleibt
  `unknown`.
- Providerneutraler MCP-P0-Diagnosezaun unter
  `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/mcp_p0.py`.
  `configured`, `reachable` und `tools/list` wurden diagnostisch erreicht;
  der autorisierte Atlas-Read ist nicht abgeschlossen.
- V3.1 eigener, besessener Linux-PTY-/Terminalkanal mit geordneter
  Rücklesekette.
- V3.2 VT-Zustandsreader mit sichtbaren Grenzen für nicht unterstützte
  Sequenzen.
- V3.3 Linux-PTY-Resize mit Kernel-Roundtrip und sichtbarer Rücklese.
- V3.4 read-only Win32-Scannerkern mit Default-Desktop, sichtbaren
  Top-Level-Fenstern, Generation, Prozessdaten und gekoppelter Frame-Referenz.
- Redteam-Korrekturen für den falschen Terminalmarkerbeweis und die fehlenden
  64-bit-Win32-`ctypes`-Signaturen.
- Letzter dokumentierter Stand: 71 Core-Tests grün; Playwright-Proof und
  Guardian liefen grün. Diese Zahlen belegen die getesteten Vertrags- und
  Linux-/Browserpfade, nicht Daniels natives Windows.

### Noch nicht als fertiges Produkt bewiesen

- Aktuelles, reproduzierbares Windows-Paket auf Daniels echtem Windows.
- Echter Windows-ConPTY-Kanal und Parität mit dem laufenden Codex-Terminal.
- Native Windows-Capture-Quelle plus Scannerinventar im selben Snapshot.
- Native Zielauswahl, Binding-Rücklese, Bewegung/Änderung und Pre-Action-Rescan.
- Freies Einzel-Overlay mit echtem Hit-Testing, Fokus, Not-Aus und Eingabe.
- Windows/KDE-Desktop-1/2-Abnahme.
- ChatGPT als echter Bridge-Strom sowie Claude-/Gemini-/Codex-Körper im
  Anti-Terminal.

Der vorhandene Artefaktpfad
`/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge/AugenUndHaendeBridge.exe`
wurde am 2026-09-20 entfernt. Er war ein älterer Plattform-/Smoke-Probe-Stand
und wurde nie als fertiges Produkt gewertet. Eine aktuelle native EXE-Abnahme
auf Daniels Windows existiert weiterhin nicht.

## 5. Warum die Reihenfolge jetzt so aussieht

Die Zielplanung unter
`/root/werkraum/docs/augen_haende_bridge/BRUECKE_VOM_ENDZIEL_RUECKWAERTS_ZUM_START.md`
beginnt gedanklich beim Endziel G18 und leitet G01 bis G04 rückwärts ab.
Die praktische V3-Spur unter
`/root/werkraum/docs/augen_haende_bridge/2026-09-20_V3_AI_STROM_ANTI_TERMINAL_MCP_P0.md`
ordnet den sichtbaren Produktweg als `EXE lebt → Terminal → Readback → Scanner
→ Binding → Evidence → AI-Ströme`.

Die tatsächlich erledigten V3.1–V3.4-Arbeiten sind vorbereitende Kern- und
Vertragssteine auf dem VPS. Sie sind nicht dasselbe wie der echte
Windows-Produktstart. Deshalb wird der nächste Produktabschnitt nicht als
„EXE ist fertig“ ausgegeben, sondern als neuer, reproduzierbarer
Windows-Erstkontakt-Vertikalschnitt behandelt. Danach kommt der native Scanner-
und Binding-Beweis. Die alte Tk-Probe unter
`/root/werkraum/augen_haende_bridge/client_windows/overlay_app.py` wird dabei
nicht zu einer fertigen Wunschoberfläche aufgeblasen.

## 6. Aktueller nächster Fokus

Der nächste sinnvolle Produktstein ist:

```text
aktuelles Windows-Paket reproduzierbar bauen
→ auf echtem Windows starten
→ opt-in Bridge-Verbindung aufbauen
→ eine sichtbare, rücklesbare Erstkontakt-Nachricht liefern
→ sauber stoppen und erneut verbinden
→ native Evidence sichern
```

Dieser Stein bekommt vor dem Code die erneute Skill-Lesung und nach dem Code
die erneute Skill-Lesung. Erst wenn dieser Kontakt nativ belegt ist, darf der
Windows-Fensterscanner mit echter Capture-Quelle an den Produktpfad gekoppelt
werden.

Danach bleibt ChatGPT ein eigener sichtbarer Vertikalschnitt und darf nicht in
„Multi-Agenten“ verschwinden:

```text
G06.5
nach Terminal, Fensterscanner, Binding und nativer Evidence:
echte ChatGPT-Session binden
→ eigene Raute und eigener manueller Chatkörper
→ echte Antwort mit korrekter Absenderidentität
→ Anti-Terminal-Ledger für Session/Turn/Ziel/Empfänger
→ Plain-Chat ohne impliziten Toolcall
```

Die vorhandene Caller-/Slot-Vorarbeit ist dafür nur Vorarbeit. Erst der reale
End-to-End-Dialog mit Rücklese gilt als ChatGPT-Integration.

## 7. Protokollformat für jeden weiteren Eintrag

Jeder neue Eintrag wird unter einem Zeitstempel ergänzt und enthält mindestens:

```text
### YYYY-MM-DD HH:MM — [Bauschritt]

OPENING_SKILL_READ
- /config/.agents/skills/augen-und-haende-bridge/SKILL.md: gelesen
- /root/werkraum/_codex/skills/augen-haende-greenfield-builder/SKILL.md: gelesen
- relevante Dokus und aktuelle Grenze: ...

SCOPE_AND_PROVENANCE
- bearbeitet wird: ...
- unangetastet bleibt: ...

BACKUP
- Commit: ...

BUILD
- eine konkrete Änderung: ...

EVIDENCE
- Core: ...
- Playwright: ...
- Native/Plattform: ...
- Status je Beleg: PASS / PARTIAL / BLOCKED / UNKNOWN

CLOSING_SKILL_READ
- beide Skills unmittelbar nach Bau/Test erneut gelesen: ...
- Abweichung gefunden: ...

TRUTH_AT_HANDOFF
- jetzt bewiesen: ...
- weiterhin offen: ...
- nächster einzelner Stein: ...
```

„Grün“ darf nur in der jeweils passenden Beweisschicht stehen. Ein grüner
Core-Test darf keinen nativen Windows-PASS vortäuschen; ein Playwright-
Screenshot darf keine reale Zielbindung erfinden; ein vorhandenes EXE-Artefakt
darf keinen akzeptierten Windows-Erstkontakt behaupten.

## 8. Fokusregeln gegen erneuten Drift

- Die Benutzeroberfläche kommt nicht vor dem tragenden Kontakt- und
  Wahrnehmungspfad wieder an die Reihe.
- Der alte Gemini-Prototyp ist entfernt; seine Git-Historie ist Herkunft, nicht Baustelle.
- ChatGPT, Claude und Gemini werden erst als reale Körper angeschlossen, wenn
  der gemeinsame technische Weg und seine Beweisgrenzen sichtbar sind.
- Anzeigeort, Arbeitsziel, Session und Empfänger bleiben getrennt.
- Ein einzelner Bau-Stein darf seine eigene Evidence erzeugen; keine
  nachträgliche Sammelbehauptung über mehrere ungeprüfte Schichten.
- Nach jedem Kontextabbruch beginnt die Orientierung erneut; der nächste
  Bauschritt wird aus diesem Protokoll, dem aktuellen Git und der aktuellen
  Evidence rekonstruiert, nicht aus einer alten Gesprächsbehauptung.

## 9. Erste Protokollmarke — 2026-09-20

Die aktuelle Wiederaufnahme hat die vollständige Codex- und importierte
Claude-Notizspur, die Werkraumkarte, Resonanzspur, Briefkastenregeln,
Graph-Report, Referenzbild, Bridge-Baustartprüfung, Greenfield-Skill,
Anforderungsregister, Rückwärtsbauplan, Hinterhof-Recherchen, ChatGPT-
Anti-Terminal-Vertrag, MCP-P0-Vertrag, V3.1–V3.4-Verträge und das technische
Bautagebuch erneut zusammengeführt.

Der entscheidende Fokusfund ist: Der Kern ist weiter als ein leerer Anfang,
aber die echte Windows-Brücke ist noch nicht abgenommen. Die Linux-PTY-, VT-,
Resize- und Win32-Scannerverträge tragen bereits. Die alte EXE-Datei wurde
entfernt und war nur historischer Probe-/Paketstand. Der nächste Bau muss
deshalb einen aktuellen, reproduzierbaren nativen Erstkontakt liefern und darf
nicht wieder in eine große Surface ausweichen.

## 10. Aus dem aktiven Baum entfernte Altlasten — 2026-09-20

Auf Daniels ausdrücklichen Auftrag wurden der obsolete Gemini-Prototyp, seine
alte Proof-/Playwright-Strecke, die alte Proof-Surface und der alte EXE-Einstieg
aus dem aktiven Arbeitsbaum entfernt. Betroffen waren:

- `/root/werkraum/_gemini/windows_bridge/`
- `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/proof_surface.py`
- `/root/werkraum/augen_haende_bridge/tests/playwright_proof.py`
- `/root/werkraum/augen_haende_bridge/tests/playwright_guardian.py`
- `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge/AugenUndHaendeBridge.exe`

Historische Evidence-Berichte und alte Bautagebuch-Einträge bleiben als
Provenienz lesbar. Sie sind nach dieser Entfernung keine aktuellen PASS-
Beweise. Der neue Baupfad startet mit dem echten Kern und einem späteren
nativen Windows-Erstkontakt; die gelöschte Browser-Proof-Surface wird nicht
wieder als Produktoberfläche oder Witness verwendet.

## 11. G02/G03 — TargetRegistry-Plattformgrenze und stabile Terminal-Identität

### 2026-09-20 — G02/G03

OPENING_SKILL_READ
- `/config/.agents/skills/augen-und-haende-bridge/SKILL.md` und `/root/werkraum/_codex/skills/augen-haende-greenfield-builder/SKILL.md` unmittelbar vor G03 gelesen.
- Baustartprüfung, Bauplan, `/root/werkraum/augen_haende_bridge/BUILD_LOG.md`, aktueller Code, Evidence und `ideen_scan.py terminal-identity` geprüft; keine offene Idee gefunden.

SCOPE_AND_PROVENANCE
- Bearbeitet wurde ausschließlich der aktive Greenfield-Pfad `/root/werkraum/augen_haende_bridge/`.
- Unangetastet bleiben der historische Gemini-Baum, laufende Agenten-Terminals, Windows-Native-Ziele und die bestehenden fremden Arbeitsbereiche.

BACKUP
- Sicherheitspunkte vor den einzelnen Änderungen: `a4ffe195c6`, `88bcde01e4`, `ae58888232`, `f85e27a346`, `d6b1d17675`, `4da5187225`, `2802dbbd8f`, `c565eecc92`, `9d84a5f015`, `6f67458b4d`, `523bc8b749`, `ff436fae4e`.

BUILD
- Windows-Default erhielt einen expliziten `PlatformUnavailableAdapter`; Discovery kann dort kein lokales qdbus starten.
- `refresh_terminals()` ersetzt nur entdeckte Records, schützt Auswahl/Fallback/Probe und ordnet sichtbare Slots über `service|session_path` stabil.
- Der konkrete Probe-Auswahl-Randfall aus der letzten Gemini-Prüfung wurde repariert: Selection-Migration und Fallback geschehen innerhalb von `register_probe()`.
- Die nächste Gemini-Runde erzwang zusätzlich einen atomaren Record-Tausch und zweiphasige Slotreservierung; neue Sessions können keinen erinnerten Slot vor einem überlebenden Ziel beanspruchen.
- Die abschließende Lifecycle-Prüfung ergänzte `TerminalDiscovery`-Fehlerstatus, Fehler-als-leere-Welt-Schutz, Refresh-Coalescing und Sequenzinvalidierung. Ein degradiertes qdbus-Ergebnis ersetzt keinen letzten guten Snapshot.

EVIDENCE
- Core: **PASS**, 90 Tests; `py_compile` **PASS**.
- Playwright: **PASS**, `/root/werkraum/augen_haende_bridge/tests/transport_playwright_proof.py` und `/root/werkraum/augen_haende_bridge/tests/reference_surface_proof.py`.
- Native/Plattform: **NOT_PROVEN**; Linux-Testdaten und Playwright ersetzen weder Daniels Windows noch Win32-ConPTY/Capture/Input.
- Review: Claude und Gemini wurden als unabhängige Prüfer genutzt; Gemini-Falschbefunde wurden nicht blind übernommen, echte Befunde dagegen in Code und Tests verarbeitet.

CLOSING_SKILL_READ
- Beide Skills wurden unmittelbar nach Bau und Tests erneut gelesen.
- Keine Abweichung vom aktuellen Vertrag gefunden; die offene native Grenze bleibt ausdrücklich sichtbar.

TRUTH_AT_HANDOFF
- Jetzt bewiesen: plattformneutraler Registry-Start, stale-Refresh-Fallback, stabile Session-Identität, Probe-Deduplizierung und Auswahlmigration im Core-/Browser-Slice.
- Weiterhin offen: produktiver Bridge-Readback-Refresh des Windows-Overlays, echte Windows-Native-Evidence, ChatGPT-Review über gebundene C2C-Projektsession.
- Nächster einzelner Stein: Bridge-Readback-Refresh im Overlay, danach native Windows-Abnahme; keine neue Großoberfläche.

## 12. G04 — Bridge-Readback-Refresh (2026-09-20)

OPENING_SKILL_READ
- Der Greenfield-Skill und der ausführende Bridge-Skill wurden vor dem Stein
  erneut gelesen. Der aktuelle Vertrag verlangte Readback vor Binding, getrennte
  Anzeige-/Arbeitsziele, Playwright als Browserzeuge und native Evidence für
  Windows-Fähigkeiten.

CONTEXT_REHYDRATED
- G03 war im Core-/Browser-Slice bewiesen, aber der echte Overlay-Refresh fehlte.
- Der aktive Code blieb `/root/werkraum/augen_haende_bridge/`; alte Surface,
  alte EXE und historische Gemini-Spuren wurden nicht wieder aktiviert.
- Die letzte Review warnte außerdem vor einem Idle-Disconnect und davor, dass
  ein remote gemeldetes `available` fälschlich wie lokale Verfügbarkeit wirkt.

FOCUS_CONTRACT
- Einziger Stein: read-only VPS-Terminalinventar vom Desktop anfordern,
  zurückliefern, korrelieren, atomar im Overlay-Registrybestand anwenden.
- Erhaltungsanker: Loopback-only, Capability-/Epoch-/Receipt-Prüfung,
  keine Shell/Input/Write/Delete-Rechte, keine Monsteroberfläche.
- Verbotene Drift: Terminaleingabe, Remote-Inspect, native Windows-Abnahme oder
  ChatGPT-Ausbau in diesen Stein hineinziehen.

BACKUP
- Vor der Reviewer-Reparatur: `44fdf21bbc` — `backup: vor G04 reviewer fixes`.
- Vor Abschlussdokumentation: `82c1665d1b` —
  `backup: vor G04 abschlussdokumentation`.

BUILD
- `target_inventory_request` und `target_inventory` sind getrennte, streng
  validierte Wire-Kapazitäten.
- `BridgeRuntime` antwortet optional über einen expliziten Provider, behandelt
  Anwendungssilenz als normal und begrenzt Antwort-IDs sicher.
- `TargetRegistry.bridge_inventory()` exportiert nur echte Terminal-Sessions,
  nicht `terminal-probe`. `apply_remote_inventory()` validiert und tauscht den
  Remotebestand atomar; Remote-IDs sind namespaced und bleiben ohne Remote-
  Inspect-Adapter `unavailable`.
- Der produktive VPS-Einstieg
  `/root/werkraum/augen_haende_bridge/client_vps/bridge_agent.py` verdrahtet
  den Registry-Provider mit `BridgeRuntime`; das Inventar ist damit nicht nur
  in einem Test-Callback vorhanden.
- Das Overlay führt Request-ID/Freshness-Korrelation, Timeout und einen
  nichtblockierenden Anforderungs-Thread ein. Die Terminalkarten lesen den
  tatsächlichen Registrybestand statt hardcodierter lokaler Slots.

EVIDENCE
- `PYTHONPATH=src:. python3 -m unittest discover -s tests -q`: **PASS**, 97 Tests.
- `python3 -m py_compile ...`: **PASS** für Transport, Runtime, Registry und
  Windows-Overlay.
- `/root/werkraum/augen_haende_bridge/tests/transport_playwright_proof.py`:
  **PASS**. Chromium fordert Inventar an; Produktions-Provider erzeugt es;
  Relay liefert es mit Receipts; Registry-Consumer übernimmt ein namespaced
  Ziel. Der Lauf ist als `producer_targets: 1`, `consumer_targets: 1` belegt.
- `/root/werkraum/augen_haende_bridge/tests/reference_surface_proof.py`:
  Exit-Code 0; keine alte Surface wurde als Produktbeweis verwendet.
- Native Windows: **UNKNOWN**. Linux und Playwright ersetzen keinen echten
  Windows-Start, Win32-Capture oder native Overlay-Rücklese.

REVIEW
- Claude Opus: echter Idle-Disconnect und Readback-/Namespace-Lücken erkannt;
  Befunde umgesetzt und mit Tests abgesichert.
- Gemini/Antigravity: in diesem G04-Abschluss kein verwertbarer neuer Bericht;
  kein Gemini-PASS behauptet.
- ChatGPT: nicht behauptet; C2C-Projektsession bleibt ungebunden.

CLOSING_SKILL_READ
- Nach Code und Tests wurden der Greenfield-Skill und der ausführende Bridge-
  Skill erneut gelesen. Die Implementierung bleibt read-only, provenance-
  getrennt und fail-closed. Die native Windows-Grenze wurde nicht zu PASS
  hochgestuft.

TRUTH_AT_HANDOFF
- G04-Code-/Transportstein: **abgeschlossen und reproduzierbar belegt**.
- G04-native Windows-Abnahme: **offen**; das ist der nächste Plattformstein.
- Keine Terminaleingabe, kein Remote-Inspect und keine fertige Endoberfläche
  wurden vorgetäuscht.

## 13. G05 — Windows-EXE-Paket und isolierter Start-Smoke

OPENING_SKILL_READ
- `/config/.agents/skills/augen-und-haende-bridge/SKILL.md` und
  `/root/werkraum/_codex/skills/augen-haende-greenfield-builder/SKILL.md`
  wurden vor dem Paket-Schritt gelesen. Der Vertrag verlangte ein echtes
  Paket, Playwright-Regression und eine getrennte native-Evidence-Aussage.

CONTEXT_REHYDRATED
- G04 hatte den read-only Bridge-Readback im Code/Transport bewiesen, aber
  noch keine aktuelle EXE ausgeliefert.
- Die vorhandene `dist/`-Struktur enthielt nur einen verwaisten `_internal`-
  Stand ohne EXE; der aktuelle Build durfte daraus keinen Native-PASS ableiten.

FOCUS_CONTRACT
- Einziger Stein: das aktuelle Windows-Programm vollständig bündeln und den
  Start isoliert belegen.
- Erhaltungsanker: kein alter Prototyp, keine alte Proof-Surface, kein
  Terminal-Input und kein öffentlicher VPS-Tunnel.
- Verbotene Drift: aus Wine einen echten Windows-Abnahmestand behaupten.

BACKUP
- `09923aa524` — `backup: vor G05 Windows-EXE-Bundle`.

BUILD
- Der erste Embeddable-Python-Versuch wurde wegen fehlendem Tkinter verworfen.
- Mit dem vollständigen Windows-Python-Installer 3.13.5 wurde ein isolierter
  Wine-Build mit PyInstaller 6.14.2 und `websockets` 16.1.1 erzeugt.
- Das vollständige `--onedir --windowed`-Bundle liegt unter
  `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge/`.
- Der produktive EXE-Hash ist
  `573f58992eb859c347d50965edb9f605f7b4dab9367ebbcf579e5edd6e7c8e0f`.

EVIDENCE
- Paket/PE: **PASS**; Tkinter/Tcl/Tk sind im Bundle enthalten.
- Wine-Start-Smoke: **PASS**; das Fenster `Augen & Hände Bridge` wurde mit
  `1180x680+138+60` rückgelesen.
- Core: **PASS**, 97 Tests.
- Playwright: **PASS**; Transport-Inventory-Provider/Consumer und die
  Referenzregression liefen erneut durch.
- Native Windows: **UNKNOWN**; Wine ersetzt Daniels Windows nicht.
- Vollständiger Bericht:
  `/root/werkraum/augen_haende_bridge/tests/evidence/G05_WINDOWS_EXE_PACKAGE_EVIDENCE.md`.

CLOSING_SKILL_READ
- Beide Bridge-Skills wurden nach Paket, Regression und Dokumentation erneut
  gelesen. Die Implementierung bleibt innerhalb des Greenfield-Vertrags.

TRUTH_AT_HANDOFF
- Jetzt bewiesen: eine aktuelle, vollständige Windows-EXE ist im offiziellen
  Bundlepfad vorhanden und startet als GUI-Prozess im isolierten Smoke.
- Weiterhin offen: nativer Start auf Daniels Windows, Win32-Capture, echter
  Fensterscanner-Readback und der spätere sichere VPS-Tunnel.
- Nächster einzelner Stein: echter nativer Windows-Erstkontakt; keine weitere
  Oberfläche.

## 14. G06 — Gebündelter Windows-Erstkontakt unter Wine

OPENING_SKILL_READ
- Beide Bridge-Skills wurden für den G06-Fokus erneut gelesen. Die Vorgabe
  war ein echter Paket-/Prozesskontakt mit getrenntem Wine- und Native-Status;
  Playwright bleibt für den browserbedienbaren Relaypfad verpflichtend.

CONTEXT_REHYDRATED
- G05 hatte ein vollständiges EXE-Bundle, aber nur Prozess-/Fensterstart
  bewiesen.
- Das aktuelle Overlay fordert beim Verbinden ein read-only Inventar an und
  kann `say`-Ereignisse sichtbar rendern; die lokale Relay-Grenze bleibt
  absichtlich bestehen.

FOCUS_CONTRACT
- Einziger Stein: den gebündelten Prozess selbst an den lokalen Relay hängen,
  Inventar und Nachricht durchlaufen lassen und den sichtbaren Renderzustand
  extern rücklesen.
- Erhaltungsanker: loopback-only, keine Shell, kein Terminal-Input, keine
  native Windows-Behauptung aus Wine.

BACKUP
- `0b765448b6` — `backup: vor G06 evidence und protokoll`.

BUILD
- Der GUI-Titel markiert eine empfangene `say`-Nachricht mit
  `say-received`, damit der Smoke einen sichtbaren externen Zustand lesen
  kann.
- Der Runner startet die offizielle EXE, bestätigt Inventar und Nachricht
  über den Relay und liest das Fenster über `xwininfo`.

EVIDENCE
- Runner: `/root/werkraum/augen_haende_bridge/tests/windows_exe_wine_first_contact.py`.
- Paket-Hash:
  `e011b27ecb6500cd00ec9274f92f5eb2a3a790284e15a54244a7656c7a6dcca9`.
- Paket/Verbindung/Inventar/Nachricht/Render: **PASS** im isolierten Wine-
  Lauf; sichtbares Fenster `Augen & Hände Bridge · say-received`.
- Playwright-Regression: **PASS** für den bestehenden lokalen
  Transport-/Inventory-Witness.
- Native Windows: **UNKNOWN**; kein Wine-Ergebnis wird hochgestuft.
- Vollständiger Bericht:
  `/root/werkraum/augen_haende_bridge/tests/evidence/G06_WINDOWS_EXE_FIRST_CONTACT_EVIDENCE.md`.

CLOSING_SKILL_READ
- Beide Skills wurden unmittelbar nach Runner und Regression erneut gelesen;
  die Grenze zwischen Paket-Smoke, Browserbeleg und nativer Windows-Evidence
  bleibt erhalten.

TRUTH_AT_HANDOFF
- Jetzt bewiesen: Die ausgelieferte EXE verbindet sich als Prozess, nimmt ein
  read-only Inventar an, empfängt eine Agentennachricht und zeigt sie sichtbar
  an — im isolierten Wine-Smoke.
- Weiterhin offen: echter Start auf Daniels Windows, native Fenster-/Desktop-
  Capture, native Scanner-Rücklese und der sichere entfernte VPS-Kanal.
- Nächster einzelner Stein: native Windows-Erstkontakt oder, falls Daniels
  Windows noch nicht beteiligt ist, die dafür nötige sichere Übergabestrecke.

## 15. G07 — Windows-GDI-Frame und Win32-Fensterscanner unter Wine

OPENING_SKILL_READ
- Der ausführende Bridge-Skill und der Greenfield-Skill wurden vor dem
  Capture-/Scanner-Schritt gelesen. Der Vertrag verlangte eine gekoppelte
  Frame-/Inventar-Evidence und eine weiterhin sichtbare Native-Grenze.

CONTEXT_REHYDRATED
- G06 hatte den gebündelten Prozess, den lokalen Relay und sichtbares
  Nachrichten-Rendering bewiesen.
- V3.4 hatte den Win32-Scanner als Vertrag, aber noch keinen produktiven
  Capture-Körper im EXE-Pfad.

FOCUS_CONTRACT
- Einziger Stein: read-only GDI-Frame erzeugen, hashieren, mit
  `WindowsWindowScanner` paaren und den sichtbaren Scanstatus extern lesen.
- Erhaltungsanker: kein Binding, keine Eingabe, keine geheime Startaufnahme,
  kein öffentlicher VPS-Transport und kein Native-PASS aus Wine.

BACKUP
- `c340007e85` — `backup: vor G07 Evidence und Skillvertrag`.

BUILD
- `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/windows_capture.py`
  enthält den typisierten GDI-Read-Path mit Größenlimit, BGRA-Hash und
  Cleanup der GDI-Handles.
- Der Overlay-Button und der explizite Testschalter lösen den Lauf aus;
  `WindowsWindowScanner.scan()` erhält nur den frischen Frame-Zeugen.
- Der Build erzeugte das Bundle mit EXE-Hash
  `68f55707dedf08ace0cf9de515015df25918996c88fbb236d842a7bad0e0418d`.

EVIDENCE
- Core: **PASS**, 99 Tests.
- Wine-GDI-/Win32-Smoke: **PASS**; sichtbarer Marker
  `scan-received:2` wurde von `xwininfo` zurückgelesen.
- Playwright-/Transportregression: **PASS**.
- Native Windows: **UNKNOWN**; Wine ersetzt keine native Plattformaufnahme.
- Vollständiger Bericht:
  `/root/werkraum/augen_haende_bridge/tests/evidence/G07_WINDOWS_CAPTURE_SCANNER_EVIDENCE.md`.

CLOSING_SKILL_READ
- Beide Skills wurden nach Build, Coretests und Regression erneut gelesen.
  Die Implementierung bleibt read-only; der Scannerstatus wird nicht zu
  Binding- oder Input-Fähigkeit hochgestuft.

TRUTH_AT_HANDOFF
- Jetzt bewiesen: Das gebündelte Programm kann im Windows-API-Smoke einen
  echten GDI-Frame und ein Win32-Inventar koppeln und den Scanstatus sichtbar
  anzeigen.
- Weiterhin offen: nativer Windows-Host, echte Zielauswahl/Binding,
  Capture-Rücklese auf Daniels Desktop und sicherer entfernter Transport.
- Nächster einzelner Stein: native Windows-Abnahme und danach die
  read-only Zielauswahl mit Binding-Rücklese.

## 16. G08 — Aktueller VPS-Relay und sicherer SSH-Hand-off

OPENING_SKILL_READ
- Der Greenfield-Skill und der ausführende Bridge-Skill wurden vor G08
  erneut gelesen. Der G08-Fokus blieb auf dem aktuellen Produktionspfad,
  Loopback und read-only Inventory; der historische Port `9880` wurde nicht
  wiederbelebt.

CONTEXT_REHYDRATED
- G07 hatte den EXE-seitigen GDI-/Win32-Augenpfad im Wine-Smoke bewiesen,
  aber noch keinen aktuellen Relay-Einstieg für den entfernten Hand-off.
- `BridgeClient` akzeptiert absichtlich nur `ws://127.0.0.1`; deshalb ist
  SSH LocalForward der passende kleine Transportstein, ohne einen öffentlichen
  WebSocket-Endpunkt einzuführen.

FOCUS_CONTRACT
- Einziger Stein: aktueller VPS-Relay auf neuem Loopback-Port, eingebauter
  read-only VPS-Agent und Windows-Launcher über SSH LocalForward.
- Erhaltungsanker: alter Prozess/Port `9880` unangetastet, kein öffentlicher
  Bind, keine Tokens in Dateien/Argumenten/Logs, kein Shell- oder
  Terminal-Input, keine native Windows-Abnahme behaupten.
- Verbotene Drift: zweiter Tunnel-Stack, öffentliche Freigabe oder aus dem
  lokalen Smoke eine native Windows-Evidence ableiten.

BACKUP
- `660933ba1c` — `backup: vor G08 SSH-Relay-Hand-off`.

BUILD
- Neuer Einstieg:
  `/root/werkraum/augen_haende_bridge/client_vps/bridge_server.py`.
- Neuer Windows-Launcher:
  `/root/werkraum/augen_haende_bridge/client_windows/start_with_ssh_tunnel.ps1`.
- Neuer lokaler Smoke:
  `/root/werkraum/augen_haende_bridge/tests/bridge_server_smoke.py`.
- Neue Vertragsprüfungen:
  `/root/werkraum/augen_haende_bridge/tests/test_bridge_server.py` und
  `/root/werkraum/augen_haende_bridge/tests/test_ssh_tunnel_contract.py`.

EVIDENCE
- Contract: **PASS** — fünf Server-/Grant-Tests und drei Launcher-
  Vertragsprüfungen.
- Live current relay: **PASS** — der Entry-Point lief auf einem ephemeren
  Loopback-Port; der eingebaute VPS-Agent verband sich; ein Desktop-Client
  erhielt und bestätigte `target_inventory` mit vier Targets.
- Security boundary: **PASS** — nur Loopback, getrennte starke Tokens,
  SSH-Host-Key-Prüfung nicht deaktiviert, nur der eigene Tunnelprozess wird
  beendet.
- Playwright-Regressionsspur: wird nach G08-Edit erneut ausgeführt.
- Native Windows und echter SSH-Hand-off: **UNKNOWN** — kein Windows-Ende in
  dieser Umgebung.
- Vollständiger Bericht:
  `/root/werkraum/augen_haende_bridge/tests/evidence/G08_SSH_RELAY_HANDOFF_EVIDENCE.md`.

CLOSING_SKILL_READ
- Nach Build und Smoke werden beide Bridge-Skills erneut gelesen. Der
  Abschluss darf G08 nur als lokalen Transportbeweis werten; native Windows-
  und SSH-E2E bleiben offen.

TRUTH_AT_HANDOFF
- Jetzt bewiesen: Der aktuelle Produktions-Relay und der read-only VPS-Agent
  können gemeinsam auf einem neuen Loopback-Port laufen, und der Desktop-
  Gegenpart kann das Inventar authentifiziert empfangen und bestätigen.
- Weiterhin offen: tatsächlicher Windows-Launcher-Lauf, nativer GDI-/Win32-
  Readback auf Daniels Rechner und read-only Zielauswahl mit Binding-
  Rücklese.
- Nächster einzelner Stein: native Windows-Abnahme/SSH-E2E, danach
  TARGET_SELECTED → IDENTITY_VERIFIED → BINDING_CREATED → BINDING_READ_BACK.

## 17. G09 — Read-only Zielauswahl und Binding-Rücklese-Core

OPENING_SKILL_READ
- Beide Bridge-Skills wurden vor G09 erneut gelesen. Der Schritt durfte nur
  den bestehenden Scanner-/Target-Vertrag ergänzen und durfte keine native
  Fähigkeit aus einem Python-Core-Test ableiten.

CONTEXT_REHYDRATED
- G08 hatte den aktuellen Relay und den sicheren SSH-Hand-off-Vertrag
  geliefert, aber noch kein Objekt, das den gekoppelten Scanzeugen über eine
  Zielauswahl hinweg bewahrt.
- `TargetScanSnapshot` und `TargetScanItem` tragen bereits Generation,
  Frame-Referenz und Capability-Herkunft; G09 nutzt diese Schicht, statt eine
  zweite Identitätslogik zu erfinden.

FOCUS_CONTRACT
- Einziger Stein: read-only Auswahl, Binding-Erzeugung und frische
  Binding-Rücklese.
- Erhaltungsanker: Frame-/Generation-Kopplung, `observe`-only, keine Lease,
  keine Eingabe, keine native Windows-Behauptung.
- Verbotene Drift: Scannerstrings als Inputrechte übernehmen, altes Binding
  bei Handle-Reuse weiterverwenden oder eine Oberfläche vortäuschen.

BACKUP
- `3707490945` — `backup: vor G09 read-only binding core`.

BUILD
- `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/read_only_binding.py`
  ergänzt `ReadOnlyTargetBinding`, `BindingReadback`, `BindingStatus` sowie
  fail-closed Erzeugung/Rücklese.
- Öffentliche Paketexports wurden in
  `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/__init__.py`
  ergänzt.
- Tests liegen unter
  `/root/werkraum/augen_haende_bridge/tests/test_read_only_binding.py`.

EVIDENCE
- Core: **PASS** — fünf G09-Tests; Gesamtsuite **112 Tests OK**.
- Identität: **PASS** — Generation-Wechsel wird stale.
- Bildzeuge: **PASS** — Frame-Hash/-Referenz-Wechsel wird stale.
- Rechte: **PASS** — erzeugtes Binding enthält nur `Capability.OBSERVE`.
- Playwright: **NOT_APPLICABLE** — kein browserbedienbarer Pfad geändert;
  die vorhandene Playwright-Suite bleibt ein separater Regressionstest.
- Native Windows: **UNKNOWN** — echte Zielauswahl, Hit-Testing und native
  Binding-Rücklese fehlen weiterhin.
- Vollständiger Bericht:
  `/root/werkraum/augen_haende_bridge/tests/evidence/G09_READ_ONLY_BINDING_EVIDENCE.md`.

CLOSING_SKILL_READ
- Nach Tests und Dokumentation werden beide Bridge-Skills erneut gelesen. Der
  Abschluss gilt nur für den Datenkern; die native Grenze bleibt sichtbar.

TRUTH_AT_HANDOFF
- Jetzt bewiesen: Ein aktueller Scan kann sicher als read-only Binding mit
  Frame- und Generation-Zeuge festgehalten und gegen einen frischen Scan
  rückgelesen werden.
- Weiterhin offen: native Windows-Auswahl/Binding, Anzeige-/Raute-Anker,
  echte Terminal-Parität und Eingabe.
- Nächster einzelner Stein: native Windows-Abnahme des Pfades
  `TARGET_SELECTED → IDENTITY_VERIFIED → BINDING_CREATED → BINDING_READ_BACK`.

## 18. G10 — Nativer Windows-Acceptance-Witness

OPENING_SKILL_READ
- Beide Bridge-Skills wurden für G10 erneut gelesen. Der neue Schritt ist ein
  äußerer Windows-Zeuge, kein Ersatz für die native Ausführung und keine neue
  Oberfläche.

CONTEXT_REHYDRATED
- G08 liefert den aktuellen SSH-LocalForward, G09 den frame-/generation-
  gekoppelten read-only Binding-Core. G07 bietet den expliziten
  `BRIDGE_NATIVE_SCAN_ON_START`-Schalter im EXE-Körper.

FOCUS_CONTRACT
- Einziger Stein: einen Windows-seitigen, read-only Acceptance-Witness für
  nativen EXE-Start, Scanmarker, Fensterzustand und Screenshot vorbereiten.
- Erhaltungsanker: kein Input, kein zweiter Tunnel, Token nicht in
  Argumenten, native `UNKNOWN` bleibt `UNKNOWN`.
- Verbotene Drift: statische Scriptprüfung als Windows-PASS ausgeben oder
  Zielauswahl/Binding behaupten, obwohl der Witness diese noch nicht ausführt.

BACKUP
- `4027b5d743` — `backup: vor G10 native Windows acceptance witness`.

BUILD
- `/root/werkraum/augen_haende_bridge/client_windows/native_acceptance_witness.ps1`
  liest `user32.dll`-Fenstertitel, HWND, Sichtbarkeit und Rechteck und nimmt
  einen Bildschirmbeleg auf.
- `/root/werkraum/augen_haende_bridge/client_windows/start_with_ssh_tunnel.ps1`
  akzeptiert dafür den expliziten `-NativeScanOnStart`-Schalter.
- Die statische Vertragsprüfung wurde in
  `/root/werkraum/augen_haende_bridge/tests/test_ssh_tunnel_contract.py`
  erweitert.

EVIDENCE
- Contract: **PASS** — fünf Launcher-/Witness-Tests.
- Safety: **PASS** — kein `SendInput`, kein `PostMessage`, kein globales
  Beenden fremder SSH-Prozesse.
- Native Windows: **UNKNOWN** — der Witness konnte auf dem VPS nicht laufen.
- Screenshot/JSON: **UNKNOWN** — werden erst beim echten Windows-Lauf
  erzeugt.
- Binding: **NOT_EXERCISED** — G09 bleibt die vorbereitete Datenstrecke.
- Vollständiger Bericht:
  `/root/werkraum/augen_haende_bridge/tests/evidence/G10_NATIVE_ACCEPTANCE_WITNESS_EVIDENCE.md`.

CLOSING_SKILL_READ
- Beide Skills werden nach Scriptprüfung und Dokumentation erneut gelesen.
  G10 wird nur als vorbereiteter Witness abgeschlossen, nicht als native
  Plattformabnahme.

TRUTH_AT_HANDOFF
- Jetzt vorhanden: ein Windows-seitiger, read-only Witness, der den
  vorhandenen Launcher verwendet und native Fenster-/Screenshot-Evidence
  erzeugen kann.
- Weiterhin offen: tatsächlicher Lauf auf Daniels Windows, native
  Zielauswahl, G09-Binding-Rücklese und danach weitere Overlay-Funktionen.
- Nächster einzelner Stein: den Witness auf Windows ausführen und den
  `scan-received:<n>`-Marker plus Screenshot/JSON zurücklesen.

HANDOFF
- Das vollständige Übergabearchiv liegt unter
  `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge-G10-win64-handoff.zip`.
- SHA256:
  `4730f1ec4786090d5fa70ea01c0cccdb94bcffa81b494816ff42d9e96a35c129`.
- Es enthält das komplette `onedir`-Bundle sowie Launcher, Witness und
  Anleitung; die EXE darf nicht ohne `_internal` entpackt werden.

## 19. G11 — Scan → observe-only Binding im EXE-Pfad

OPENING_SKILL_READ
- Beide Bridge-Skills wurden vor G11 erneut gelesen. Der Schritt durfte nur
  den vorhandenen Scanpfad an den G09-Datenkern anschließen; keine neue
  Monsteroberfläche und keine Inputfähigkeit.

CONTEXT_REHYDRATED
- G09 hatte Binding-Erzeugung und Rücklese als Core bewiesen. G10 hatte den
  nativen Windows-Witness vorbereitet, aber der gebündelte EXE-Pfad nutzte
  das Binding noch nicht.

FOCUS_CONTRACT
- Einziger Stein: native Scan-Einträge im bestehenden Zielrail auswählbar
  machen und die Auswahl frame-/generation-gekoppelt zurücklesen.
- Erhaltungsanker: `observe`-only, Testhaken explizit, normaler Pfad manuell,
  keine Eingabe/Leases/Terminalrechte.
- Verbotene Drift: Wine als natives Windows ausgeben oder aus dem Testhaken
  eine normale automatische Auswahl machen.

BACKUP
- `06cb72154e` — `backup: vor G11 native binding wiring`.

BUILD
- `/root/werkraum/augen_haende_bridge/client_windows/overlay_app.py` zeigt
  native Scan-Einträge und ruft bei Auswahl G09-Erzeugung plus Rücklese auf.
- `/root/werkraum/augen_haende_bridge/tests/windows_exe_wine_native_binding.py`
  prüft den expliziten Paket-Testhaken.
- Neues Paket:
  `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge-G11-win64-handoff.zip`.

EVIDENCE
- Core: **PASS** — 114 Tests.
- EXE/Wine: **PASS** — `scan-received:2 · binding-readback` extern über
  `xwininfo` zurückgelesen.
- Native Windows: **UNKNOWN** — Wine bleibt getrennt.
- Menschlicher echter Klick: **NOT_EXERCISED** — der Smoke nutzt nur den
  ausdrücklich gesetzten Testhaken.
- EXE SHA256:
  `265c9fa3713df411864d3dc7d04b8f6f97d34b947e8a7a3db7d1c3a9caf855cd`.
- Archiv SHA256:
  `0d45d7966ec17484b6396573352d0f9d21fbc78f72a7968c27139705e8307eb1`.
- Vollständiger Bericht:
  `/root/werkraum/augen_haende_bridge/tests/evidence/G11_NATIVE_BINDING_WINE_EVIDENCE.md`.

CLOSING_SKILL_READ
- Nach Build, Wine-Smokes und Dokumentation werden beide Bridge-Skills erneut
  gelesen. Der Abschluss bleibt auf den Paket-/Wine-Beleg begrenzt.

TRUTH_AT_HANDOFF
- Jetzt bewiesen: Der gebündelte Windows-Körper kann einen aktuellen
  Scanner-Eintrag in ein observe-only Binding führen und den Binding-Readback
  sichtbar markieren.
- Weiterhin offen: Daniels nativer Windows-Lauf, echter manueller Klick,
  native DPI-/Hit-Test-Evidence, Terminal-Parität und Input.
- Nächster einzelner Stein: G10/G11 auf Daniels Windows ausführen und danach
  den manuellen Auswahlpfad mit nativer Evidence abnehmen.

## 20. G12 — Manueller nativer Binding-Witness

OPENING_SKILL_READ
- Beide Bridge-Skills wurden vor G12 erneut gelesen. Der Schritt erweitert
  ausschließlich den äußeren Witness und gibt dem Skript keinerlei
  Bedienrecht.

CONTEXT_REHYDRATED
- G11 zeigte den Scan→Binding-Weg im Paket-Smoke. Für den echten Abnahmepunkt
  fehlte noch eine Möglichkeit, Daniels eigenen Klick getrennt zu beobachten.

FOCUS_CONTRACT
- Einziger Stein: nach dem Scan auf einen echten manuellen Zielrail-Klick
  warten und nur den resultierenden Readback markieren.
- Erhaltungsanker: kein automatischer Klick, kein Input in Zielprogramme,
  keine Tokenargumente, native Evidence bleibt offen.
- Verbotene Drift: den Testhaken als normalen Benutzerpfad behaupten oder
  einen fehlenden Klick durch einen Marker ersetzen.

BACKUP
- `51ceb77db5` — `backup: vor G12 manual binding witness`.

BUILD
- `/root/werkraum/augen_haende_bridge/client_windows/native_acceptance_witness.ps1`
  akzeptiert `-WaitForManualBinding`.
- Die Anleitung unter
  `/root/werkraum/augen_haende_bridge/client_windows/README.md` beschreibt
  den manuellen Lauf.
- Evidence liegt unter
  `/root/werkraum/augen_haende_bridge/tests/evidence/G12_MANUAL_BINDING_WITNESS_EVIDENCE.md`.

EVIDENCE
- Contract: **PASS** — sechs statische Tests.
- Der Handoff-Launcher löst jetzt sowohl den Quellbaum- als auch den
  entpackten Archivpfad auf. Der read-only Evidence-Validator prüft danach
  JSON, Marker, native Fensterwerte und PNG, ohne Evidence zu erzeugen.
- Regression nach diesem Fix: **121 Tests OK**.
- Safety: **PASS** — der Witness sendet keinen Klick und keine Tastatur-
  oder Terminalaktion.
- Native Windows: **UNKNOWN** — echter Lauf fehlt.
- Manueller Binding-Readback: **UNKNOWN** — noch kein Screenshot/JSON mit
  `target_selection=manual_click` vorhanden.

CLOSING_SKILL_READ
- Nach der Scriptprüfung und Dokumentation werden beide Bridge-Skills erneut
  gelesen. G12 bleibt bewusst eine vorbereitete Abnahme.

TRUTH_AT_HANDOFF
- Jetzt vorhanden: ein sicherer Witness, der nach dem Scan auf Daniels
  tatsächliche Auswahl wartet und den anschließenden Binding-Marker belegt.
- Weiterhin offen: Windows-Lauf, SSH-Ende-zu-Ende, echter Klickbeleg und
  danach weitere Overlay-/Input-Gates.
- Nächster einzelner Stein: G12 auf Windows ausführen und die erzeugte
  JSON-/PNG-Evidence gegen den G09-Binding-Zustand prüfen.

HANDOFF
- Aktuelles G12-Archiv:
  `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge-G12-win64-handoff.zip`.
- SHA256:
  `f7c6e42695af367261703bd01a62aa7d908af85781059a3f5d882850b89c047a`.

## 13. Plan-G01 — Fundament (Claude, 2026-09-20)

OPENING_SKILL_READ
- `/config/.agents/skills/augen-und-haende-bridge/SKILL.md` und `/root/werkraum/_codex/skills/augen-haende-greenfield-builder/SKILL.md` gelesen.
- Aktueller Vertrag: PLAN.md (G01), ANFORDERUNGEN.md mit BE01 bis BE04, Skills unverändert benutzen, Playwright zuletzt.

CONTEXT_REHYDRATED
- Docs (PLAN, ANFORDERUNGEN, TECHNIK, Bauprotokoll), Git (HEAD `b5f79ec197`), Code (transport, bridge_runtime, windows_scanner, windows_capture, overlay_app, vision, contracts, harness), Evidence (G01–G12) gelesen.

FOCUS_CONTRACT
- Einziger Stein: die acht Punkte von G01 mit realem Ergebnis belegen.
- Erhaltungsanker: Körper aus Terminal, Scanner je Terminal, Raute, Kamera, Mikrofon (BE03); kein Overlay als Fläche (R118); 1:1 nur für von der Bridge gestartete Sitzungen (BE01); Harness und Skills 1:1 (BE04).
- Verbotene Drift: Tk als Grundlage, Attrappen, Anbindung bestehender Sessions, Browsernachbau.

BACKUP
- Sicherheitspunkt: `b5f79ec197`.

BUILD
- Bauumgebung Wine mit Windows-Python, PyInstaller, websockets. Zwei Proben unter `augen_haende_bridge/probes/`.

EVIDENCE
- Core: **PASS**, 121 Tests unverändert grün.
- Playwright: nicht anwendbar, es gibt in G01 keinen browserbedienbaren Pfad; nichts wird als Browser-PASS ausgegeben.
- Native/Plattform: Wine-API-Ebene **PASS**, echtes Windows **UNKNOWN**.

CLOSING_SKILL_READ
- Beide Skills unmittelbar nach Bau erneut gelesen. Keine Abweichung gefunden; das Tk-Fenster widerspricht R118 und wird in G02 ersetzt.

TRUTH_AT_HANDOFF
- Jetzt bewiesen: Bauweg, Fenstereigenschaften auf API-Ebene, KDE-Fakten, Stack- und Terminalentscheidung.
- Weiterhin offen: alles Sichtbare auf Daniels Windows.
- Nächster einzelner Stein: Relay um Terminalstrom, Raute-Nachrichten und Frames je Terminal erweitern (G02, Stein 1).

## 14. Plan-G02, Zyklus A — VPS-Seite (Claude, 2026-09-21)

OPENING_SKILL_READ
- Beide Skills zu Beginn der G02-Arbeit gelesen (`/config/.agents/skills/augen-und-haende-bridge/SKILL.md`, `/root/werkraum/_codex/skills/augen-haende-greenfield-builder/SKILL.md`).
- Aktueller Vertrag: PLAN.md (G02 nach BE03), ANFORDERUNGEN.md mit BE01 bis BE04.

CONTEXT_REHYDRATED
- Docs (PLAN, ANFORDERUNGEN, TECHNIK, dieses Protokoll), Git (HEAD `56e8cb82a2`), Code (transport, bridge_runtime, bridge_server, bridge_agent, transport_client, harness), Evidence G01 gelesen.

FOCUS_CONTRACT
- Einziger Stein: Relay um Terminal- und Raute-Nachrichten erweitern und den Starter bauen, der Startlisten-Einträge in Linux-PTYs hält.
- Erhaltungsanker: Körper aus Terminal, Scanner je Terminal, Raute, Kamera, Mikrofon (BE03); kein Overlay als Fläche (R118); 1:1 nur für von der Bridge gestartete Sitzungen (BE01); Start nur aus der Startliste (BE02); Harness und Skills 1:1 (BE04).
- Verbotene Drift: Anbindung bestehender Sessions, Befehl vom Desktop, Attrappen, Relay-Token im Agentenprozess.

BACKUP
- Sicherheitspunkt: `56e8cb82a2`.

BUILD
- Relay-Erweiterung, `client_vps/terminal_launcher.py`, `bridge_cli.py`, `starts.json`, `orte.json`, Anpassung von `bridge_server.py`.

EVIDENCE
- Core: **PASS**, 165 Tests grün (Ausgangsstand 121). Ende-zu-Ende mit echtem Server-Prozess; Docker-Weg auf dem Host gegen beide Desktop-Container.
- Playwright: nicht anwendbar, dieser Zyklus hat keinen browserbedienbaren Pfad; nichts wird als Browser-PASS ausgegeben. Playwright kommt zuletzt am Ende von G02.
- Native/Plattform: Terminalkette bis `input_echoed` auf Linux **PASS**; `rendered` und alles auf Daniels Windows **UNKNOWN**.

CLOSING_SKILL_READ
- Beide Skills unmittelbar nach Bau und Tests erneut gelesen. Keine Abweichung vom Vertrag gefunden: PTY wird von der Bridge gehalten, Transport und Darstellung bleiben getrennt.

TRUTH_AT_HANDOFF
- Jetzt bewiesen: Relay und Starter auf Linux, Docker-Weg für vd1 und vd2, Sprech-Socket, Größe und Schließen.
- Weiterhin offen: Windows-Darstellung, Wiederaufsetzen nach Trennung, alles auf Daniels Windows.
- Nächster einzelner Stein: Win32-Fenster-Toolkit (G02, Zyklus B, Stein 3).

## 15. Plan-G02, Zyklen B bis H (Claude, 2026-09-24 bis 2026-09-30)

Sieben Zyklen in einer Sitzung nach dem Absturz von `virtuellerdesktop1`. Einzelheiten je Zyklus stehen in
`/root/werkraum/augen_haende_bridge/BUILD_LOG.md` und den Evidence-Berichten `PLAN_G02_B_*` bis `PLAN_G02_H_*`
unter `/root/werkraum/augen_haende_bridge/tests/evidence/`.

OPENING_SKILL_READ
- Beide Skills einmal am 2026-09-24 vor Zyklus B gelesen. Vor den Zyklen C bis H nicht erneut gelesen.

CONTEXT_REHYDRATED
- Vor Zyklus B: Git, `BUILD_LOG.md`, `PLAN.md` (G02), Teile von `ANFORDERUNGEN.md`, `koerper/`-Code, Testlauf.
- Nicht gelesen in diesen Zyklen: `TECHNIK.md`, `78_augen_und_haende_bauplan.md`, dieses Bauprotokoll,
  `ERLEBEN.md`, `NACHWEISE.md`, die Referenzskizze.

BACKUP
- `341708d702` (Sicherung des vorgefundenen `koerper/`-Stands), danach je Zyklus der vorige Zyklus-Commit.

BUILD
- B `a8c892688d`: Tests für `win32.py`, `fenster.py`, `menue.py`, `stil.py`, `terminal_fenster.py`.
- C `970ebda591`: `raute_fenster.py`.
- D `9ddfb7d615`: `kamera.py`, `mikrofon.py`, Extras in `pyproject.toml`.
- E `7502aed729`: `probes/koerper_smoketest.py`, `wine` neu installiert.
- F `ef28cffcf6`: `nachricht_fenster.py`.
- G `c46768e552`: `chat_fenster.py`.
- H `accf26348e`: `scanner_anbindung.py`, `erster_koerper.py`, `TerminalFenster.scanner_verbinden()`.

EVIDENCE
- Core: **PASS**, 376 Tests nach H; drei umgebungsbedingte Fehlschläge in `test_terminal_adapter.py` unverändert.
- Wine: Raute, Terminal, Nachricht, Chat und die Verdrahtung in `ErsterKoerper` gebaut und per Win32-API
  zurückgelesen, **PASS** unter Wine.
- Playwright: in keinem der Zyklen ausgeführt.
- Native Windows: **UNKNOWN**.

CLOSING_SKILL_READ
- In keinem der Zyklen B bis H nach dem Bau erneut gelesen. Die `BuildCycleRun`-Dateien dieser Zyklen stehen
  deshalb auf `running` vor der ersten nicht ausgeführten Lesung.

TRUTH_AT_HANDOFF
- Jetzt vorhanden: die Einzelteile des ersten Körpers als Module, unter Wine einzeln und verdrahtet gebaut.
- Weiterhin offen: siehe Abschnitt 16.
- Nächster einzelner Stein: siehe Abschnitt 16.

## 16. Wiederaufnahme-Lesung und Abgleich (Claude, 2026-09-30)

OPENING_SKILL_READ
- `/config/.agents/skills/augen-und-haende-bridge/SKILL.md`: unverändert seit der Lesung vom 2026-09-24, Wortlaut
  vollständig vorliegend und durchgegangen.
- `/root/werkraum/_codex/skills/augen-haende-greenfield-builder/SKILL.md`: ebenso.
- Vollständig gelesen: `harness.py`, `PLAN.md`, `ANFORDERUNGEN.md`, `TECHNIK.md`,
  `78_augen_und_haende_bauplan.md`, dieses Bauprotokoll, `ERLEBEN.md`, `NACHWEISE.md`, Referenzskizze
  `/vps_root/werkraum_bilder/refferenzen/hand-auge-bridge-ref.jpg`.

ABGLEICH DES BESTEHENDEN KÖRPERS MIT DEN DOKUMENTEN
- Raute: `ERLEBEN.md` verlangt, dass Klicks durch die Raute fallen; bedient wird sie über F13–F24 oder
  Klick mit gedrückter Modifikatortaste. `raute_fenster.py` fängt jeden Klick ab.
- Banner und Ticker: `ERLEBEN.md` beschreibt zwei gleichzeitige Darstellungen — Banner breit und fast mittig im
  Zielbereich mit Zug zur Raute, über 3,3 s kontinuierlich durchsichtiger; Ticker klein direkt an der Raute,
  6,6 s. `nachricht_fenster.py` ist ein einzelnes Fenster mit hartem Wechsel zwischen zwei Phasen.
- Raute: `PLAN.md` G02 verlangt Verbindung, Status und ein erreichbares Schließen. Fehlt.
- Terminal: `PLAN.md` G02 verlangt ein Terminal, das die Bridge hält. `ErsterKoerper` hat keinen Relay-Anschluss.
- Scanner: `SCANNER_PROOF_SEQUENCE` in `harness.py` und `read_only_binding.py` (G09) verlangen Identitätsprüfung,
  Binding-Erzeugung und Binding-Rücklese. `scanner_anbindung.py` benutzt `read_only_binding.py` nicht.
- Regie und Medien unten links (`ANFORDERUNGEN.md` Abschnitt „Was Daniel festgelegt hat“, UQ05, Skizze): fehlt.
- Not-Aus: `78_augen_und_haende_bauplan.md` 3.1 verlangt Wirkung unabhängig von WebSocket, MCP, Agentenstatus
  und UI-Thread. Fehlt.
- Körper-Tor `tests/pruefe_koerper.py` prüft noch `client_windows/overlay_app.py`, nicht `koerper/`.
- Playwright als letzter Zeuge (BE04): für G02 noch nicht ausgeführt. Vorhandener Weg:
  `tests/transport_playwright_proof.py` als Browser-Peer am echten Relay.
- Paket: kein PyInstaller-Bundle des `koerper/`-Körpers; vorhandene Wege aus G05/G08:
  `AugenUndHaendeBridge.spec`, `client_windows/start_with_ssh_tunnel.ps1`,
  `client_windows/native_acceptance_witness.ps1`, `tests/windows_exe_wine_first_contact.py`.

TRUTH_AT_HANDOFF
- Nächster einzelner Stein: Raute klickdurchlässig mit Modifikator-Bedienung, Verbindung/Status/Schließen.

## 17. Plan-G02, Zyklus I — Raute klickdurchlässig, Status und Schließen (Claude, 2026-09-30)

OPENING_SKILL_READ
- Beide Skills per Read-Werkzeug erneut aufgerufen, unverändert seit Abschnitt 16.

CONTEXT_REHYDRATED
- Abschnitt 16 (vollständige Lesung aller Dokumente), Git `8ad3805d47`, `raute_fenster.py`, Tests.

BACKUP
- `8ad3805d47`.

BUILD
- Raute klickdurchlässig, Strg macht sie bedienbar; Statusrand; Menü mit Schließen im `ErsterKoerper`.

EVIDENCE
- Core: **PASS** (389; drei bekannte umgebungsbedingte Fehlschläge).
- Wine: **PASS** — Klick fällt ohne Strg durch, mit echt gedrücktem Strg trifft er die Raute, Ecken nie.
- Playwright: nicht anwendbar. Native Windows: **UNKNOWN**.

CLOSING_SKILL_READ
- Beide Skills nach Bau und Tests per Read-Werkzeug erneut aufgerufen, unverändert; keine Abweichung.

TRUTH_AT_HANDOFF
- Jetzt bewiesen (Wine): Klickdurchlässigkeit und Modifikator-Bedienung der Raute, Menü mit Schließen.
- Weiterhin offen: Hotkeys F13–F24 und Status aus der echten Verbindung (mit dem Relay-Anschluss).
- Nächster einzelner Stein: Banner und Ticker als zwei gleichzeitige Fenster nach `ERLEBEN.md`.

## 18. Plan-G02, Zyklus J — Banner und Ticker getrennt (Claude, 2026-09-30)

OPENING_SKILL_READ
- Beide Skills per Read-Werkzeug erneut aufgerufen, unverändert.

CONTEXT_REHYDRATED
- `ERLEBEN.md` (Rauten und ihre Sprache), R026/R027, Git `61591f367f`, `nachricht_fenster.py`, `erster_koerper.py`.

BACKUP
- `61591f367f`.

BUILD
- Banner- und Tickerfenster getrennt, beide gleichzeitig, Banner blendet kontinuierlich aus.

EVIDENCE
- Core: **PASS** (395; drei bekannte umgebungsbedingte Fehlschläge).
- Wine: **PASS** in echter Zeit — Banner zu nach 3304 ms, Ticker nach 6607 ms, Deckkraft fällt stetig.
- Playwright: nicht anwendbar. Native Windows: **UNKNOWN**.

CLOSING_SKILL_READ
- Beide Skills nach Bau und Tests per Read-Werkzeug erneut aufgerufen, unverändert; keine Abweichung.

TRUTH_AT_HANDOFF
- Jetzt bewiesen (Wine): drei Darstellungen derselben Nachricht (Banner, Ticker, Chat) mit den Zeiten aus
  `ERLEBEN.md`.
- Weiterhin offen: gebundenes Fenster als Zielbereich; Banner folgt bewegtem Zielfenster (G05).
- Nächster einzelner Stein: Scanner über `read_only_binding.py` mit Rücklese.

## 19. Plan-G02, Zyklus K — Fensterscanner mit read-only Binding (Claude, 2026-09-30)

OPENING_SKILL_READ
- Beide Skills per Read-Werkzeug erneut aufgerufen, unverändert.

CONTEXT_REHYDRATED
- `harness.py` (`SCANNER_PROOF_SEQUENCE`), `read_only_binding.py`, Scanner/Capture, Abschnitte 15–17 (G07–G12), Git `4f833dee8b`.

BACKUP
- `4f833dee8b`.

BUILD
- Scanner-Knopf → echte Aufnahme und echtes Inventar → Auswahl → G09-Binding → Rücklese, Beweiskette in der Harness.

EVIDENCE
- Core: **PASS** (398; drei bekannte umgebungsbedingte Fehlschläge).
- Wine: **PASS** mit echtem Win32-Scanner bis `BINDING_READ_BACK`; Rechteck = echtes Fenster.
- Popup-Menü mit Daniels Klick: **UNKNOWN**. Playwright: nicht anwendbar. Native Windows: **UNKNOWN**.

CLOSING_SKILL_READ
- Beide Skills nach Bau und Tests per Read-Werkzeug erneut aufgerufen, unverändert; die Auswahl bindet nicht heimlich.

TRUTH_AT_HANDOFF
- Jetzt bewiesen (Wine): Fensterscanner je Terminal mit Binding-Rücklese; gebundenes Fenster ist Zielbereich.
- Weiterhin offen: eigene Bridge-Fenster im Inventar (Entscheidung Daniel); Bild an den Agenten (mit Relay-Stein).
- Nächster einzelner Stein: Regie- und Medienleiste unten links.

## 20. Plan-G02, Zyklus L — Anwendung mit Relay-Anschluss (Claude, 2026-09-30)

OPENING_SKILL_READ
- Abschlusslesung von Zyklus K unmittelbar davor. Keine eigene Lesung unmittelbar vor dem Bau.

CONTEXT_REHYDRATED
- Transport, Runtime, Client, `bridge_server.py`, Starter, `bridge_cli.py`, Startliste, SSH-Launcher, vorhandene
  Wine- und Playwright-Tests, `TECHNIK.md` (Transport), Git `39d28ef533`.

BACKUP
- `39d28ef533`.

BUILD
- `KoerperAnwendung` und `bild.py`; `ErsterKoerper` mit Größe, Chat-Hotkey und R114-Ausblenden.

EVIDENCE
- Core: **PASS** (429; drei bekannte umgebungsbedingte Fehlschläge).
- Echter VPS-Weg unter Linux: **PASS** (Relay, Starter, PTY, Sprech-Socket, Bild, Beenden).
- Native Fenster/Wine: in diesem Zyklus nicht. Playwright: nicht. Native Windows: **UNKNOWN**.

CLOSING_SKILL_READ
- Beide Skills nach dem Bau per Read-Werkzeug aufgerufen, unverändert; mangels Vor-Bau-Lesung nicht attestierbar.

TRUTH_AT_HANDOFF
- Jetzt bewiesen (Linux, echter VPS-Weg): der Körper hält die Bridge — Start, Strom, Eingabe, Sprechen, Bild, Beenden.
- Weiterhin offen: sichtbarer Einstieg ohne Agent (Leiste), Not-Aus, EXE.
- Nächster einzelner Stein: Regie- und Medienleiste unten links.

## 20. Plan-G02, Zyklus M — Lokaler Not-Aus (Claude, 2026-09-30)

OPENING_SKILL_READ
- Beide Skills in dieser Sitzung vollständig gelesen; vor dem Bau nicht erneut aufgerufen.

BACKUP
- `ee7088726b`.

BUILD
- `notaus.py` (Flag + `WH_KEYBOARD_LL`-Hook im eigenen Faden), Sperre im Sender-Faden, Raute-Menü, Anzeige an allen Rauten.

EVIDENCE
- Core: **PASS** (443; drei bekannte Fehlschläge). Wine: **PASS** (echter F12-Druck, GUI-Thread pumpt nicht).
- Playwright: nicht anwendbar. Native Windows: **UNKNOWN**. Keine Latenzaussage.

CLOSING_SKILL_READ
- Nach dem Bau nur die ersten 30 Zeilen beider Skills erneut gelesen (nicht vollständig).

TRUTH_AT_HANDOFF
- Jetzt bewiesen (Wine): lokaler Not-Aus, unabhängig vom GUI-Thread, sperrt Eingabe/Bild/Start hinaus.
- Nächster einzelner Stein: Regie- und Medienleiste unten links.

## 21. PLAN-G02 Zyklus N: Regie- und Medienleiste (2026-09-30)

Kleines Fenster unten links (Agent, Mik, Cam, Regie, STOP), `medien.py` mit echten Geräten nur auf ausdrückliches
Einschalten, Regiesprüche als getippter Gesprächswunsch über den Not-Aus-gesperrten Eingabeweg, Kamerabild als `frame`
mit `terminal_id`. 471 Tests (drei bekannte Fehlschläge), Wine-Probe grün. **Offen:** Mikrofon-Audio hat keine
Relay-Nachrichtenart und wird nicht übertragen; Hardware-Geräte und native Windows UNKNOWN.
Evidence: `augen_haende_bridge/tests/evidence/PLAN_G02_N_REGIELEISTE_EVIDENCE.md`.

## 22. PLAN-G02 Zyklus O: Einstiegspunkt der exe und Körper-Tor (2026-09-30)

`koerper/haupt.py` setzt den ersten Körper zusammen (Anwendung, F12-Hook, Medien, Regieleiste, Log im
`%LOCALAPPDATA%`). Regie-Menü mit Startliste und „Bridge beenden“. Körper-Tor prüft jetzt `koerper/` (0 von 4).
Wine aus dem Quellstand gegen ein echtes Relay: Verbindung, Start, Tippen, Rückgabe. 476 Tests (drei bekannte
Fehlschläge). Offen: gebaute exe, native Windows, Frage ob „Bridge beenden“ die VPS-Sitzungen schließen soll.
Evidence: `augen_haende_bridge/tests/evidence/PLAN_G02_O_EINSTIEG_EVIDENCE.md`.

## 23. PLAN-G02 Zyklus P: Paket und Übergabe (2026-09-30)

`dist/AugenUndHaendeBridge-G02-win64.zip` (SHA256 `8b31455a03d054f34e2254f643ec70d0df4644eb92c54215de1a1c652e0b0c7a`),
onedir, Versionsinfo 0.2.0-g02, Startanleitung und Manifest im ZIP. Unter Wine als gebaute exe gestartet (offline und gegen
ein echtes Relay mit echter Sitzung), Playwright zuletzt PASS. numpy/opencv wegen eines Wine-Importabbruchs nur als Dateien
beigelegt. **Native Windows ist eine offene Übergabe (UNKNOWN), nicht erledigt.**
Evidence: `augen_haende_bridge/tests/evidence/PLAN_G02_P_PAKET_EVIDENCE.md`.

## 24. PLAN-G02 Zyklus Q: gemeinsamer Chat, Raute nur vom Agenten (2026-09-30)

Nach dem ersten echten Start korrigierte Daniel: die Raute gehört dem Agenten, der Chat ist ein gemeinsames Fenster, und Daniels
Chat- und Regiebefehle gehen **nicht** ins Terminal, sondern in den Chat und 6,6 s auf den Bildschirm, damit der Agent sie sieht.
Umgesetzt und unter Wine (Fenster und Gesamtweg) belegt; neues Paket 0.2.1-g02, ZIP-SHA256
`1b45bc1794e8e195455c6e02488d57c3ec976681fc18048ca7a7d9f7a7bed278`. Offen: laufender Bilderstrom, native Windows.
Evidence: `augen_haende_bridge/tests/evidence/PLAN_G02_Q_CHAT_RAUTE_EVIDENCE.md`.

## 25. PLAN-G02 Zyklus S: Sichtbarkeit je Fenster und gespeicherte Einstellungen (2026-09-30)

Daniel definierte die Raute als räumlichen Sprech- und Präsenzort genau einer Session (Ticker/Banner, frei verschiebbar, transparent regelbar, weder Chat noch Terminal)
und wollte Terminal und Chat pro Ziel (Desktop, Fenster, Programm, Spiel) einstellbar haben, „ganz individuell“. Umgesetzt: Sichtbarkeitsregel je Fenster
(immer oder nur bei einem Programm) und gespeicherte Einstellungen. ZIP 0.3.0-g02, SHA256 `7fe1916e24b8da46958b4186d711d3d9dd1089f7fc714f513e8ea7c1ac1986cf`.
Unter Wine mit echten fremden Programmen belegt, nativ ungetestet. Evidence: `augen_haende_bridge/tests/evidence/PLAN_G02_S_SICHTBARKEIT_EVIDENCE.md`.

## 26. PLAN-G02 Zyklus U: Bedientaste, Tastenkombination je Agent, längliche Raute (2026-09-30)

Daniel: die Bedientaste soll wählbar sein (Strg+Alt statt Strg), die Tastenkombination je Agent frei festlegbar und in der Raute zusammen mit dem Namen immer sichtbar (so steht es in ERLEBEN.md),
die Raute nicht gleichseitig. Umgesetzt und unter Wine belegt; ZIP 0.4.0-g02, SHA256 `7fe1916e24b8da46958b4186d711d3d9dd1089f7fc714f513e8ea7c1ac1986cf`.
Offen: das Eingabefeld an der Raute (Doku), Agenten das `say`-Werkzeug beibringen, nativ ungetestet. Evidence: `augen_haende_bridge/tests/evidence/PLAN_G02_U_HOTKEY_RAUTE_EVIDENCE.md`.

**Korrektur zu 26 (Daniel):** Die Tastenkombination gehört dem Agenten, nicht Daniel. Er sieht sie in der Raute, drückt sie, an seiner Raute öffnet sich ein Eingabefeld, sein Text ist seine Rede. Umgesetzt in
`koerper/eingabe_fenster.py`; ZIP 0.4.1-g02. Offen: Der Agent muss die Tasten drücken können (Eingabe-Hände).

## 27. PLAN-G02 Zyklen V bis Z: Startnachricht, Hände, Bilderstrom, Sprache, Selbsttest (2026-09-30)

Auf Daniels Auftrag „alle der Reihe nach und ohne stoppen“ gebaut: (1) Agenten bekommen beim Start einen Hinweis auf ihre Werkzeuge (opt-in je Startlisten-Eintrag); (2) Eingabe-Hände: ein Agent lässt die Bridge seine
Tastenkombination drücken und in sein Eingabefeld tippen (eng begrenzt, Fokusprüfung, Not-Aus); (3) laufender Bilderstrom mit Ausschnitt je Ziel; (4) Mikrofon-Audio: Sprechtaste oder offenes Mikrofon → VPS → Whisper large-v3
(gemessen, Standard) → Text im Chat und an der Raute, `bridge_cli hoere`; (5) Selbsttest der exe für Daniels Windows. Unter Wine belegt, nativ offen. ZIP 0.5.0-g02,
SHA256 `5e66ee515bd1cc75da3de6e9e142e2853024f19337d4125a79288b26ca1ceed3`. Evidence: `augen_haende_bridge/tests/evidence/PLAN_G02_V_BIS_Z_EVIDENCE.md`.

## 28. Windows-Dateiarbeit für Claude per SSH-Reverse-Tunnel, getrennt von der Bridge (2026-09-30/10-01)

Daniel wollte, dass Claude auf seinem Windows-Rechner Dateien anlegen, lesen, bearbeiten und Befehle ausführen kann wie auf dem VPS. Das braucht keine Bridge-EXE
und kein neues Paket (jede Bridge-Änderung verlangt eine neue EXE zum Herunterladen, deshalb wird nicht gemeinsam an der Bridge gebaut). Gewählt: Weg über SSH, Claude bleibt
dieselbe Instanz auf dem VPS. Kette: Claude → Host-SSH → `127.0.0.1:2222` auf dem Host → Reverse-Tunnel → `sshd` auf Windows (nur Loopback).

Stand: eingerichtet und belegt (Anmeldung als `desktop-lgqcq4r\pc`, PowerShell 5.1). Daniel gab den Arbeitsbereich „überall“ frei. Einzelheiten, Dateien und Stolpersteine: `augen_haende_bridge/BUILD_LOG.md`,
Eintrag „Windows-Zugang für Claude per SSH-Reverse-Tunnel“. Dateien: `dist/windows_ssh_einrichten.ps1`, `dist/claude_tunnel.ps1`.
Offen: gleichartiger Zugang für die anderen Agenten, je Agent eigener Schlüssel und eigene Einschränkung; Autostart des Tunnels (Daniels Entscheidung).
Augen und Hände (Sehen und Klicken) bleiben die Bridge-Baustelle und sind hiervon unabhängig.

## 29. Nativer Selbsttest auf Daniels Windows und die Fehler, die er gezeigt hat (2026-10-01)

Der Selbsttest der exe wurde zum ersten Mal auf Daniels echtem Windows 10 ausgeführt (über den Zugang aus Abschnitt 28, als geplante Aufgabe im angemeldeten Benutzerkontext). Das hat mehrere Fehler gezeigt,
die unter Wine nicht sichtbar waren, und sie sind behoben (Versionen 0.5.1 bis 0.5.5):

- **Kamera:** Index 0 gibt es auf Daniels Rechner nicht, die Kameras sind Index 1 und 2. Die Bridge sucht jetzt Index 0 bis 3 und nimmt die erste, die ein Bild liefert.
  Das Öffnen dauert nativ 6 bis 22 s und hat die Bedienung blockiert; es läuft jetzt in einem eigenen Faden, der Zustand heißt dann „startet“ (gelb).
- **Mikrofon:** Das Windows-Standardgerät ist bei Daniel ein virtuelles (WO Mic) und liefert nur Stille. Es gibt jetzt eine Geräteauswahl im Regie-Menü, und der Selbsttest misst jedes Gerät einzeln.
  Ergebnis am 2026-10-01: alle fünf Eingabegeräte liefern digitale Stille. Das ist ein Befund an Daniels Rechner (Stummschaltung oder Pegel), kein Fehler der Bridge. Bewusst auf später verschoben.
- **Hotkeys:** Die Tastenkombination eines entfernten Agenten blieb belegt. Sie wird jetzt freigegeben.
- **Fokus:** Die Eingabe-Hände konnten den Fokus nicht immer holen. Es gibt eine Kette (direkt, Eingabefaden anhängen, Alt-Tastendruck, SwitchToThisWindow), jeweils mit Prüfung.
  Mit einem Notepad im Vordergrund nativ belegt, der Fokus geht danach zurück.
- **Selbsttest selbst:** Die Geräteprüfung schreibt Zwischenstände und hat 90-s-Zeitgrenzen. Die Durchklick-Prüfung meldet „unbekannt“ statt „Fehler“, wenn Strg/Alt schon vor dem Test gedrückt sind.
  Ein einziger solcher Fehlschlag wurde nicht bewiesen erklärt, nach der Gegenmaßnahme lief die Prüfung dreimal sauber.

Evidence: `augen_haende_bridge/tests/evidence/PLAN_G02_NATIV_SELBSTTEST_055_EVIDENCE.md`.

## 30. Terminal: Menü, Kopieren, Rollbalken, Blättern (2026-10-01, Versionen 0.5.6 und 0.5.7)

Daniel wollte das Terminal bedienen wie das hier auf `vd1`. Umgesetzt:

- Rechtsklick öffnet ein Menü (Kopieren, Einfügen, Alles markieren, Auswahl aufheben). Beim ersten Wurf erschien es an der falschen Stelle, weil Fensterkoordinaten als Bildschirmkoordinaten
  genommen wurden; behoben.
- Kopieren: Zeilen, die bis in die letzte Spalte laufen, gelten als umgebrochen und werden ohne Zeilenwechsel zusammengesetzt. Vorher entstanden harte Zeilenwechsel mitten im Befehl.
- `TerminalSession.write` schreibt, bis alles angenommen ist (Test mit echtem PTY, 100 KB). Ein tatsächliches Abschneiden auf diesem Weg ist nie nachgewiesen worden, es ist eine Absicherung.
- Rollbalken rechts (Griff ziehen, in die Leiste klicken), Mausrad drei Zeilen je Rastung, die Markierung wandert beim Blättern mit, über den Rand ziehen blättert weiter.
  Grenze: Text, der den Bildschirm verlassen hat, ist nicht Teil einer Auswahl.
- Das Rad geht an das Programm, wenn es Mausereignisse angefordert hat (Vollbild-Oberflächen).
  [status: offen] Ob das Daniels Rad-Problem war, ist nicht belegt; er bestätigte nur, dass Markieren und Scrollen mit 0.5.7 funktionieren.

Bewusst nicht geändert: `MAX_RAUTE_TIPPEN = 500` (Grenze für `bridge_cli schreibe`) und `MAX_TERMINAL_INPUT = 8192` je Stück. Das Aussehen des Terminals ist offen, bis Daniel sagt, was ihn stört.

## 31. Selbstbild: Daniel sieht, was der Agent von ihm sieht (2026-10-01, Version 0.5.8)

Das Kamerabild ging bisher nur an die Agenten, Daniel selbst sah sich nirgends. Neu: `koerper/kamera_fenster.py`, pro Agent ein kleines Fenster mit Daniels Bild. Es erscheint bei „Cam an“ und verschwindet bei „Cam aus“.
Es ist seitenverkehrt wie ein Spiegel (der Agent bekommt das Bild unverändert), verschiebbar, in der Größe verstellbar, transparent, durchklickbar mit der Bedientaste und mit der Sichtbarkeitsregel versehen;
Ort, Größe und Deckkraft werden pro Agent gemerkt. Die Vorschau läuft mit 5 Bildern pro Sekunde, zum Agenten geht weiter 1 Bild pro Sekunde. Daniel bestätigte nativ: „klappt und gefällt mir eigentlich joa“;
was an „eigentlich“ nicht ganz passt, ist nicht geklärt.

## 32. Verteilung auf Daniels Windows und eine Fehlersuche, die an meinem Vorgehen lag (2026-10-01)

Der Weg zu Daniels Rechner ist ein ZIP aus `dist/` plus eine Batchdatei. Mehrere Anläufe der Batchdatei scheiterten, weil Windows den Ordner `C:\Bridge\neu` auch bei geschlossenen Fenstern festhielt
(Umbenennen: „Der Prozess kann nicht auf die Datei zugreifen“). Ursache nicht bestimmt (Virenscanner oder Hintergrundprozess liegen nahe). Die jetzige `dist/bridge_wechseln.bat` benennt nichts mehr um,
sondern entpackt in einen frischen Ordner (`C:\Bridge\v058`) und startet von dort; nicht löschbare Altordner bleiben liegen. Sie wurde am 2026-10-01 von Daniel erfolgreich ausgeführt.
Außerdem: Auf Daniels Windows liegen von mir angelegte Testordner `test051` bis `test056` mit ZIPs; die Batchdatei räumt sie nach Möglichkeit auf.

Weiter offen:
- Die `Claude-Host`-Sitzung bekommt wegen `"model": "haiku"` in der Claude-Konfiguration auf dem Host Haiku. `client_vps/starts.json` startet sie jetzt mit `claude --model default`;
  wirksam erst nach `systemctl restart bridge-relay` und einem Neustart dieser Sitzung (Daniel macht das später).
- Mikrofon nativ (Sprechtaste, echte Aufnahme) und Zugang für andere Agenten zu Windows (Abschnitt 28).
- Aussehen des Terminals.

## 33. Terminal-Schriftgröße wie vd1 (2026-10-01, Version 0.5.9)

Daniels Eindruck „sieht etwas anders aus“ ließ sich an einem Screenshot seines Desktops (per Tunnel, danach gelöscht) messen: Das Bridge-Terminal hatte Zeilen von 27 statt 19 Pixeln und Zeichen von 11,9 statt 8,5 Pixeln Breite,
die Schrift war also etwa 1,4-mal so groß wie bei `vd1`. Schriftgröße von 16 auf 12 gesetzt (`SCHRIFT_PX` in `koerper/terminal_fenster.py`), Daniel: „so wie bei vd1“, danach „ist gut so jetzt“.
Schriftart, Farben und Deckkraft unverändert (die Deckkraft stellt Daniel selbst ein; bei 100 % ist das Terminal sauber lesbar). Installationsordner je Version neu (`C:\Bridge\v059`).

## 34. Chat umbrechen, Banner und Box neu (2026-10-01, Versionen 0.6.0 und 0.6.1)

- **Chat (0.6.0):** Lange Nachrichten werden an der Fensterbreite an Wortgrenzen umgebrochen, Folgezeilen eingerückt, der Bildlauf zählt die umgebrochenen Zeilen. Daniel: „man kann ihn gut lesen“.
- **Anzeige von Nachrichten (0.6.1), auf Daniels Beschluss:** Weg 1 Chat, Weg 2 die Box neben der Raute (größer, hoch statt lang, umgebrochen, 9,9 s, bleibt im Bildschirm), Weg 3 das Raum-Banner im Zielbereich
  (6,6 s, wird transparenter, lange Texte umgebrochen). Das sind andere Zeiten als bis dahin gebaut und in `ERLEBEN.md` stehend (Banner 3,3 s, kleiner Ticker 6,6 s); beide Dokumente (`ERLEBEN.md`, `ANFORDERUNGEN.md`)
  wurden mit Vermerk nachgezogen. Daniels eigene Worte (Chat, Regiesprüche, erkannte Sprache) gehen nur noch in den Chat und als Banner (`zeige_daniel`), nicht mehr als Box neben die Raute.
  Die Hinweise der Bridge selbst (Tastenkombination, Hände, Sprache …) erscheinen weiter als Box neben der Raute (`zeige_ticker`) und stehen damit jetzt auch 9,9 s. [status: offen] Ob die kurzen Hinweise so lange stehen sollen, ist nicht gefragt worden.
- Proben unter Wine: `probes/chat_umbruch_smoketest.py`, `probes/nachricht_umbruch_smoketest.py` (Banner 2 Zeilen, Box 4 Zeilen links der Raute am rechten Rand, Fade-Wert nach 1,5 s 186 von 255).

Außerdem festgestellt: Die `Claude-Host`-Sitzung startet in `/root` und liest dort wegen der Claude.md sechs Minuten lang das Sessionritual. Das ist kein Fehler der Bridge. Ihr Modell ist jetzt fest `claude-sonnet-5-5`
(`--model default` hatte Opus ergeben).

**Nachtrag 0.6.2 (2026-10-01):** Daniels Test mit einem sehr langen Agententext (eine „Bibel“) zeigte vier Dinge, alle behoben:
(1) Die Box neben der Raute wurde so hoch wie der Bildschirm — jetzt höchstens 10 Zeilen, die letzte endet auf „ …“, der ganze Text steht im Chat; das Banner höchstens 12 Zeilen.
(2) Banner und Box überdeckten sich — das Banner weicht der Box und der Raute aus (seitlich, darüber, darunter), die Box weicht dem Banner aus; die Box überdeckt die Raute nie.
(3) Das Banner war ein langer Streifen — jetzt schmal (höchstens 35 % der Zielbreite) und hoch, zum Lesen von oben nach unten. Unter Wine: 444 × 332 px, 12 Zeilen, keine Überlappung.
(4) Chat: echter Rollbalken rechts (Griff, Klick in die Leiste, Ziehen) und zwei Knöpfe ▲ ▼ im Kopf, die zum Anfang der vorigen bzw. nächsten Nachricht springen (sie steht dann oben).
Daniels Eindruck, das Chatfenster selbst sei „maximal hoch“ geworden: im Code gibt es keinen Pfad, der das Chatfenster vergrößert; gemeint war sehr wahrscheinlich die hohe Box (Punkt 1).
[status: offen] Ob Daniel wirklich die Box meinte, ist nicht bestätigt. Raute verschieben während die Box steht: die Box folgt, prüft aber keine Überlappung mit dem Banner neu.

**Nachtrag 0.6.3 (2026-10-01):** Chat: „[Zeit] Name:“ vor jeder Nachricht ist größer (18 px, fett) und in der Farbe des Absenders, der Text dahinter kleiner (13 px) in einer helleren Nuance derselben Farbe.
Alle Zeilen haben die Höhe der größeren Schrift. Daniels weiterer Wunsch (Ort jedes Elements wählbar: ganzer Desktop oder im Zielfenster, mit Minimieren) entspricht R113/R115 in `ANFORDERUNGEN.md` und ist
noch nicht gebaut; siehe die Rückfrage im Gespräch vom selben Tag.

## 35. Entscheidungen zum Ort der Elemente bei gebundenem Zielfenster (2026-10-01, Daniel)

Auf die Rückfrage zu dem Wunsch „je Element wählen, ob es auf dem ganzen Desktop bleibt oder in das anvisierte Fenster (z. B. Chromium) kommt, dort eingerahmt, mit Minimieren“ hat Daniel entschieden:

1. **Zielfenster wird verschoben:** Das Element wandert mit und bleibt an derselben Stelle im Fenster.
2. **Zielfenster geht zu:** Das Element verschwindet ebenfalls (es geht nicht zurück auf den Desktop).
3. **Schalter:** je Element einzeln, nicht ein Schalter für alle; er sitzt neben dem Scanner-Knopf.
4. **Zeitpunkt:** später, als eigene Etappe. Bis dahin nur festgehalten, nichts gebaut.

Das ist jetzt als R121 in `ANFORDERUNGEN.md` eingetragen (konkretisiert R113 und R115, die schon Ort „Desktop oder im Gate“ und das Minimieren von Terminals forderten).
Zu beachten beim Bauen: Daniel (2026-10-01): Minimieren hat nichts mit der Bridge oder den Agenten zu tun, die Agenten laufen sauber weiter und bekommen Bilder und alles andere dauerhaft. Offen und nicht geprüft: Wie die Bilder aussehen, wenn das *Zielfenster* minimiert ist (die Bildaufnahme der Bridge nimmt den Ausschnitt vom Bildschirm, ein minimiertes Fenster hat dort keine Pixel; `PLAN.md` fordert dafür eine sichtbare Capability); Klemmen auf das Zielrechteck braucht dessen laufende Verfolgung
(der Scanner liefert sie bereits für die Banner-Orientierung); und das Sichtbarkeitsmodell (Regel „nur bei Programm“) und die Durchklick-Verwaltung müssen mit der neuen Bindung zusammenspielen.

**Wunsch vom selben Tag (R122):** Ein Knopf, mit dem die Agenten ganz normal nur als Terminal-Agenten laufen und die „Augen und Hände“ der Bridge zeitweise ausgeschaltet sind.
Noch nicht gebaut, Einzelheiten offen (siehe Rückfrage).

**Präzisierung zu R122 und neue Erwartung R123 (Daniel, 2026-10-01):**
- „Nur Terminal“ schaltet Bilder, Hände, Kamera und den Rautenchat (mit Banner und Box) aus. **Das Mikrofon bleibt an.** Grund für den Rautenchat: Ohne Bilder gibt es kein Gegenlesen.
  Je Agent einzeln und für alle gleichzeitig wählbar; erreichbar über einen Knopf im Terminalbereich und über Rechtsklick auf die Raute.
- R123: Daniel ging davon aus, dass ein in ein Zielfenster gesperrter Agent wie früher bei Playwright & Co. auf dem virtuellen Desktop in jedem Fensterzustand (klein, verdeckt, minimiert) sehen und handeln kann.
  Die Bridge arbeitet anders (Bildschirmausschnitt aufnehmen, echte Tasten- und Mausereignisse senden); was damit in welchem Fensterzustand geht, steht in der Antwort an Daniel und ist als offene Machbarkeitsfrage eingetragen.

## 36. Netzrecherche zu R123: Sehen und Handeln im Zielfenster in jedem Zustand (2026-10-01)

Daniel wollte wissen, wie sein Ziel (Agent in ein Fenster gesperrt, egal ob klein, verdeckt oder minimiert) erreichbar ist, auch mit Playwright oder etwas anderem. Gesucht wurde im Netz; die Funde sind Foren-, Issue- und Doku-Zusammenfassungen,
**nichts davon ist hier selbst ausprobiert**, und Netzinhalte gelten nur als Anhaltspunkt (Provenienz-Prinzip), bis etwas Unabhängiges oder ein eigener Versuch sie bestätigt.

| Weg | Was die Quellen sagen | Folge für die Bridge |
|---|---|---|
| Browser über CDP (Playwright `connectOverCDP`, Chrome-DevTools-MCP) | Chrome mit `--remote-debugging-port` starten, Playwright hängt sich an den laufenden Browser. Bedienen über DOM und JavaScript braucht keine Pixel. **Screenshots** eines versteckten Dokuments (Tab im minimierten Fenster) hängen laut einem Issue bis zum Timeout, weil kein Compositor-Bild entsteht. | Für Browser die beste Ergänzung für Handeln und Lesen; das Bild eines minimierten Browsers bleibt ein Problem. Die frühere Erfahrung auf dem virtuellen Desktop lag vermutlich daran, dass die Fenster dort „sichtbar“ waren. [status: offen] |
| Fensteraufnahme `PrintWindow` mit `PW_RENDERFULLCONTENT` | Geht für verdeckte Fenster; minimierte liefern oft Schwarz; bei GPU-Fenstern, Chromium und Electron nicht immer zuverlässig. | Verbessert „verdeckt“, rettet „minimiert“ nicht. |
| Fensteraufnahme `Windows.Graphics.Capture` | Verdeckte Fenster gehen; minimierte liefern nur noch ein winziges Titelleisten-Bild (etwa 146×28) bzw. das letzte Bild. | Dasselbe: verdeckt ja, minimiert nein. |
| Eingabe ohne Vordergrund (`PostMessage`) | Unzuverlässig; Spiele und Programme mit Eingabe-Hooks ignorieren oder verwirren es. `SendInput` braucht das Fenster im Vordergrund. | Bedienen im Hintergrund bleibt für Spiele und viele Programme unzuverlässig. |
| UI Automation (Windows-MCP, SoftAuto-MCP und ähnliche MCP-Server) | Steuern Fenster über den Zugänglichkeitsbaum nach Elementnamen statt über Pixel; für Standardprogramme gut, für Spiele und gezeichnete Oberflächen nicht. | Gute Ergänzung für normale Programme. Prüfen, wie weit das bei minimierten Fenstern trägt. |
| Virtuelle Anzeige (Indirect-Display-Treiber, z. B. „Virtual-Display-Driver“, per `winget` installierbar) | Ein zusätzlicher virtueller Monitor, der sich wie ein echter verhält. Fenster darauf gelten als sichtbar und werden gerendert, auch wenn Daniel sie nicht ansieht; Größe und Auflösung frei. | Bester Weg für „Programm läuft für den Agenten unabhängig von Daniels Bildschirm“: Fenster dorthin legen, nie minimieren; die Bridge nimmt den Bereich auf und sendet Eingaben dorthin. Bedienen braucht weiter den Vordergrund (ein Agent zur Zeit je Eingabe). |

**Fazit (Empfehlung an Daniel, zu entscheiden):** Kein einzelnes Verfahren erfüllt „jedes Fenster in jedem Zustand“. Eine Kombination kommt dem nahe: Browser über CDP, Standardprogramme über UI Automation,
alles andere (Spiele, Blender) auf einem virtuellen Monitor, minimierte Ziele gelten weiter als nicht sichtbar (dazu passt Daniels Beschluss aus Abschnitt 35, dass sich die Elemente mit dem Zielfenster minimieren).
Der nächste Schritt wäre ein kleiner Versuch auf Daniels Windows (virtuellen Monitor einrichten, ein Fenster darauf aufnehmen und bedienen), danach die Entscheidung.

## 37. Entscheidung: Kombination bauen, Vorrang für „jeder Agent sieht sein ganzes Fenster“ (2026-10-01, Daniel)

Nach der Recherche (Abschnitt 36) hat Daniel entschieden:
1. Es wird so dokumentiert und **die Kombination wird gebaut** (Browser über CDP, normale Programme über UI Automation, der Rest über Fensteraufnahme und, wo nötig, einen virtuellen Monitor).
2. **Minimierte Fenster sind nicht wichtig.** Wichtiger ist sein Alltag: Er hat **einen Laptop mit einem Bildschirm** und will zum Beispiel ein Spiel im Fenstermodus an eine Stelle legen, einen Browser daneben für einen anderen Agenten
   und ein Programm darunter für wieder einen anderen, wie in seiner Skizze (`/vps_root/werkraum_bilder/refferenzen/hand-auge-bridge-ref.jpg`).
3. Seine Hoffnung: **Jeder Agent bekommt immer das vollständige Bild zu seinem eigenen Gate**, an das er gebunden ist (R124).

**Was das für die Technik heißt (meine Einordnung, noch nicht erprobt):**
- Bisher nimmt die Bridge den **Bildschirmausschnitt** des Zielfensters auf (BitBlt vom Bildschirm, `windows_capture.py`). Liegen die Fenster nebeneinander, ohne sich zu überlappen, passt das. Überdeckt aber ein anderes Fenster einen Teil des Ziels,
  enthält das Bild die fremden Pixel. Für R124 braucht jeder Agent eine **Aufnahme genau seines Fensters** (Fensteraufnahme per `PrintWindow` oder `Windows.Graphics.Capture`, die laut den Quellen auch bei verdeckten Fenstern das Fensterbild liefert).
- Eingaben (Klicks, Tasten) brauchen weiterhin das Fenster im Vordergrund; mehrere Agenten können also nicht gleichzeitig tippen, sondern nacheinander (ein Eingabefokus). Das ist eine Grenze von Windows, keine der Bridge. [status: offen] noch nicht belegt.
- Ein virtueller Monitor hilft Daniel auf einem Ein-Bildschirm-Laptop nur begrenzt (er sieht ihn nicht direkt); er bleibt als Zusatz für Programme, die nie sichtbar sein müssen.

**Reihenfolge der Etappen (Vorschlag, noch nicht beschlossen):**
- E1 Versuch auf Daniels Windows: ein Zielfenster teilweise von einem zweiten verdeckt, per Fensteraufnahme (`PrintWindow`, `Windows.Graphics.Capture`) aufnehmen und mit der Bildschirmaufnahme vergleichen. Ergebnis entscheidet das Verfahren.
- E2 Fensteraufnahme in den Bilderstrom einbauen (je Agent), mit Rückfall auf die Bildschirmaufnahme, wenn eine Fensteraufnahme leer oder schwarz ist.
- E3 Browser über CDP als zusätzlicher Weg zum Lesen und Handeln (Chromium mit `--remote-debugging-port`).
- E4 UI Automation für normale Programme.
- E5 Ort jedes Elements (R121) und „nur Terminal“ (R122) bleiben eigene Etappen.

## 38. Erst Plan, dann Goal: R121 bis R124 in der Planung (2026-10-01, Daniel)

Daniel hat den vorgeschlagenen Versuch auf seinem Windows (Abschnitt 37, E1) zurückgewiesen: Das gehört nicht jetzt als lose Probe gemacht, sondern sauber in die Planung mit eigenen Goals. Die Etappenliste E1 bis E5 aus Abschnitt 37 ist damit **ersetzt**:

- **G06.7** (neu in `PLAN.md`): Mehrere Fenster, mehrere Agenten, ein Bildschirm; jeder Agent sieht sein ganzes Fenster. Enthält die Kombination (Fensteraufnahme, CDP, UI Automation, virtueller Monitor bei Bedarf) und die Proben zur Verfahrenswahl als ersten Schritt innerhalb des Goals. Anforderungen R014, R120, R123, R124.
- **G05.5** (neu in `PLAN.md`): Ort der Elemente bei gebundenem Zielfenster und »nur Terminal«. Anforderungen R113, R114, R115, R121, R122.
- Abhängigkeiten und Vorwärtsfolge in `PLAN.md` ergänzt (G06.7 und G05.5 nach G06.5, vor G07); R121 bis R124 im Register den neuen Goals zugeordnet. Kein Goal ist gestartet, es wurde nichts gebaut.

Daniels Rückfrage zur Grenze „ein Eingabefokus“: Die Doku kennt dazu **virtuelle Controller** (R064, `ERLEBEN.md`: bis zu vier unabhängige Xbox- oder DirectInput-Controller, für jeden Agenten einer, ohne Klick-Kollision; Hybrid-Koop mit Daniels Maus und Tastatur),
geplant in G10 »Wirkliche Hände, parallele Arbeit und verlässlicher Stop«, Ziel bis vier Controller, mit Adapter- und Treibergrenzen. Das hilft nur bei Spielen und Programmen, die einen Controller unterstützen; für Programme mit reiner Maus- und Tastenbedienung bleibt der eine Eingabefokus.
Ob ein bestimmtes Spiel (z. B. WoW) mit einem Controller sinnvoll bedienbar ist, ist nicht geprüft. [status: offen]

## 39. Mehrere Mäuse und Tastaturen, Warteschlange, und welches Goal als Nächstes (2026-10-01)

**Mehrere Mäuse/Tastaturen oder Warteschlange (Daniels Frage):** Windows kennt einen Mauszeiger und einen Tastaturfokus; echte Mehrfach-Zeiger gibt es unter Windows nicht (unter Linux/X11 gibt es mit MPX etwas Ähnliches).
Zusätzliche virtuelle Eingabegeräte würden denselben einen Zeiger und Fokus bewegen. (Eigenes Wissen, hier nicht neu geprüft.) Deshalb gilt für die Planung ein Zweiweg-Entwurf:
(1) Wege **ohne** Zeiger laufen parallel, ohne Warteschlange: Browser über CDP, UI Automation, virtuelle Controller (R064). (2) Für echte Maus und Tastatur ein **Vermittler mit Warteschlange und kurzen Leasen** (`PLAN.md` G10 nennt Arbitrator, Leases und Shared-Mouse-Modus):
Jede Aktion oder kurze Folge belegt die Eingabe nur so lange wie nötig, wer wartet, steht in der Schlange mit Priorität; Daniels eigene Eingabe und F12 haben immer Vorrang. Beides ist in G10 bzw. G06.7 einzuordnen, nichts davon ist gebaut.

**Goal-Stand (G02, G03):** Der Plan verlangt für „fertig“ eine Ergebnisrücklese und einen dokumentierten Abschluss (Arbeitsvertrag Punkt 7). Praktisch ist G02 weit: Paket, Terminal, Scanner, Raute mit Banner, Ticker und Chat, Kamera sind nativ bei Daniel belegt;
offen ist u. a. das Mikrofon nativ. G03 läuft de facto (Daniels Bridge verbunden mit laufenden Sitzungen, Nachrichten über die Raute, mehrere Versionswechsel mit erhaltenen Einstellungen), aber Pause, Trennung und Wiederverbindung sowie „alte Aktionen werden nicht nachgespielt“ sind nativ nicht belegt.
Noch kein Abschlussprotokoll für beide. Korrektur an meiner früheren Aussage: G06.7 braucht nach der Abhängigkeitstabelle G06 (und damit G04, G05); die Reihenfolge nach G03 ist G04, G05, G06 usw. Vorbereitung darf früher geschehen, ein PASS nicht.

## 40. Entkopplung von Daniels Eingabe und den Agenten: was die Doku schon sagt und was die Recherche zeigt (2026-10-01)

**Was schon in der Doku steht** (`ERLEBEN.md`, Abschnitt »Die Hände«): Drei Ebenen. (1) *Im Hintergrund*: bei normalen Windows-Programmen gehen Klicks direkt an das Zielfenster, für Buttons und Menüs dient der Barrierefreiheits-Baum, ohne Mausbewegung und ohne Fokusverlust;
bei störrischen Spielen leiht sich die Bridge den echten Cursor kurz und setzt Daniels Position zurück. (2) *Sichtbar für Daniel*: farbige virtuelle Zeiger mit Namen je Agent und dezente farbige Rahmen um gesteuerte Fenster. Das ist Daniels Idee vom eigenen Mauszeiger je Gate, **bereits in der Vision**; es ist nur ein gezeichneter Zeiger.
(3) *Exklusives Vollbild und Spiele*: geteilte Maus per Zeitscheiben mit Lease-Timer, bis zu vier virtuelle Gamepads, Hybrid-Koop. Standardmäßig entzieht Daniels Bewegung der KI die Steuerung sofort; »Volle Agenten-Autonomie« lässt sie dran (R065).

**Daniels neuer Wunsch (R125):** Statt »Daniel hat Vorrang« will er seine Eingabe **ganz abkoppeln**: Er schreibt, spielt oder surft, ohne dass die Agenten dazwischenfunken, und die Agenten ignorieren seine Eingabe. Das ist ein weiterer wählbarer Modus neben den drei in der Doku.
Mein Fehler im Gespräch: Ich hatte »Daniels Eingabe hat immer Vorrang« als feststehend dargestellt; das war nur der Standard aus R065.

**Recherche (Netz, nur Anhaltspunkte, nicht selbst geprüft):**

| Weg | Was die Quellen sagen | Wirkung für R125 |
|---|---|---|
| `PostMessage`/`SendMessage` an Hintergrundfenster | Mauskoordinaten liegen im Client-Bereich; es klappt nicht bei jeder Anwendung (WPF, Rechner-Programm u. a.), und bei Chromium/Electron laut den Quellen oft nicht zuverlässig. Als Notlösung: Cursor kurz bewegen und zurücksetzen. | Für Standardprogramme teils brauchbar, für Browser besser CDP. |
| Browser über CDP | Steuerung über DOM und JavaScript, ohne Maus und ohne Fokus des Systems. | Parallel möglich, ohne Warteschlange. |
| UI Automation | Klicken, Texte setzen und Lesen über Elementnamen, ohne Zeiger. | Parallel für normale Programme. |
| Mehrere Mäuse/Tastaturen je Spielinstanz (Nucleus Co-op / Proto Input) | Starten mehrere Kopien eines Spiels und leiten per Raw Input und eingeschleusten Hooks jedem Exemplar nur ein bestimmtes Gerät zu; Fokus wird vorgetäuscht. | Zeigt, dass mehrere Eingabegeräte pro Instanz möglich sind, aber nur über Hooks in der Zielanwendung und mehrere Instanzen. Bei Online-Spielen mit Anti-Cheat vermutlich riskant (nicht geprüft). |
| Eigener Desktop (`CreateDesktop`) | Programme lassen sich auf einem zweiten Windows-Desktop starten; nur ein Desktop ist gleichzeitig der sichtbare, eingabeempfangende. | Trennt Eingabe, aber Daniel sieht den zweiten Desktop nicht gleichzeitig. Für unsichtbare Hintergrundarbeit denkbar, nicht für Spiele zum Mitspielen. |
| Virtuelle Maschine mit eigener Oberfläche | Eigene Maus, Tastatur und Fenster; GPU-Aufteilung (GPU-P) laut Quelle auf Windows 10/11 Client **nicht** unterstützt, nur Windows Server 2025 mit ausgewählten Karten. | Für Spiele auf einem Laptop kaum tragbar. |
| Virtuelle Controller (ViGEm) | Kernel-Treiber für Xbox-360- und DualShock-4-Controller; das Projekt wurde am 2. 11. 2023 archiviert, der Treiber läuft aber weiter, ein Nachfolger sei angekündigt. | Für Spiele mit Controller-Unterstützung parallel pro Agent. |

**Einordnung (Vorschlag, noch nicht beschlossen):**
- Wo Agenten ohne echten Zeiger handeln können (Browser über CDP, Standardprogramme über UI Automation, Spiele mit Controller), ist **keine Warteschlange nötig**; alles läuft parallel, und Daniel arbeitet gleichzeitig ungestört. Das deckt vermutlich den größten Teil von Daniels Alltag.
- Eine Warteschlange mit kurzen Leasen braucht nur der Rest, der **echte Maus und Tastatur auf demselben Desktop** verlangt. Dort gibt es drei Wege: Agent bleibt dem Programm fern, Agent leiht sich den Zeiger nur, wenn Daniel gerade nichts tut, oder das Programm läuft auf einem eigenen Desktop/einer eigenen Instanz.
- Der **gezeichnete Zeiger je Agent** ist unabhängig davon und bleibt in jedem Fall Teil der Oberfläche.

Quellen der Recherche (Foren, Doku, Projektseiten; nicht unabhängig bestätigt):
Microsoft Q&A und Foren zu `SendMessage`/`WM_LBUTTONDOWN` an Hintergrundfenster (learn.microsoft.com, cplusplus.com, guidedhacking.com); Nucleus Co-op (nucleuscoop.org) und Proto Input (github.com/Ilyaki/ProtoInput, splitscreen.me/docs);
Windows-Desktop-API (learn.microsoft.com, `CreateDesktop`, `SwitchDesktop`); Hyper-V GPU-Partitionierung (techcommunity.microsoft.com, learn.microsoft.com); ViGEmBus (github.com/nefarius/ViGEmBus, docs.nefarius.at).

## 41. G04 gebaut, G05 geschlossen, G05.5 und G07 begonnen (2026-10-01, Versionen 0.7.0 und 0.8.0)

Daniel nahm G02 und G03 mit Ausnahmen ab (`abnahmen/ABNAHME_G02_G03.md`) und bat, G04 bis G08 durchzuziehen und dann nach einer Prüfliste alles zu testen.

- **G04 (0.7.0):** Wiederaufnahme laufender Sitzungen (`terminal_attach`, 512 KB Ausgabepuffer im Starter), Sitzungsidentität (PID, Startzeit), DEC-Linienzeichensatz, 18 Referenzfälle, Eingabeparität durchs echte PTY, Wiederverbinden gegen den echten Server-Prozess.
  Protokoll: `abnahmen/ABNAHME_G04.md`, Belege: `tests/evidence/PLAN_G04_TERMINAL_PARITAET_EVIDENCE.md`. Erfordert einen neuen Relay (Neustart).
- **G05 (0.8.0):** Gleiche Namen werden nummeriert, Name und Farbe wählbar und gespeichert, Zurücksetzen mit Rückfrage, Zustandswort unter Mik und Cam, Regie-Menü nennt den Empfänger, „Bindung lösen“ im Scanner, das Zielrechteck folgt dem gebundenen Fenster.
- **G05.5 (0.8.0):** „Nur Terminal“ je Agent und für alle (Bilder, Hände, Kamera, Rautenchat aus; Mikrofon an), Ort der Elemente im Zielfenster (eingerahmt, wandert mit, minimiert mit, verschwindet beim Schließen) mit `ziel_halter.py`, Knöpfe „Ort“ und „A+H“ im Terminal.
- **G07 (0.8.0, teilweise):** Bilddatei als Quelle, Auslieferungszähler im Menü, „Bridge-Fenster im Bild“ (Beobachtung und Einblendung trennbar), Selbsttest-Prüfung dazu.
- **Nicht gebaut:** G06 (KDE 1/2) und G08 (Zeichnen und Objekte) brauchen Entscheidungen von Daniel; Bildfolge/Replay und Überlastanzeige (G07) offen.
- Protokoll: `abnahmen/ABNAHME_G05_G055_G07.md`; Prüfliste für Daniel: `prüflisten/PRUEFLISTE_0.8.0.md` (Daniel hat die Ordner `abnahmen/` und `prüflisten/` angelegt; neue Protokolle und Listen kommen dorthin).

## 42. G07 Rest, R020 und G08 (Windows) gebaut (2026-10-02, Version 0.9.0)

Auf Daniels Auftrag („mach G07 noch und auch R020, G06 komplett 1:1, G08 nur da, wo die Agenten sitzen, bei gebundenem Desktop dort“):
- **G07:** Bildfolge (Ordner), Überlastanzeige. **R020:** Terminal-Plätze tauschen.
- **G08 (Windows):** Objektmodell mit Undo und Redo (`objekte.py`), ein gemeinsamer Zeichner (`zeichnen_render.py`), Komposition nur im Bild des Empfängers (`komposition.py`, im Bilderstrom und im ersten Bild nach der Bindung),
  plattformneutrale Bedienlogik (`editor_logik.py`), Pixel-Alpha-Fenster (`pixel_fenster.py`), Zeichenfläche und Werkzeugleiste (`zeichen_fenster.py`), Anzeige der Bildschirmobjekte (`arbeitsflaechen_anzeige.py`), Speichern (`arbeitsflaeche.json`).
  Entwurf: ein Objekt gehört zu einem Gate; „auf dem Bildschirm“ und „nur im Bild von Agent X“ sind unabhängig; nur-für-Agenten-Objekte stehen nie auf dem Bildschirm; wo Windows den Editor nicht aus der Aufnahme ausnehmen kann, zeigt er Privates nicht.
  Tests 1130 (nur die drei bekannten Fehlschläge), Wine-Probe `probes/zeichnen_smoketest.py`.
- Protokoll: `abnahmen/ABNAHME_G07_G08_R020.md`; Prüfliste: `prüflisten/PRUEFLISTE_0.9.0.md`.
- **G06 (KDE 1/2 komplett, 1:1)** ist der nächste Block und größer als erwartet: Er braucht (1) einen Relay, der mehrere Desktops als Anzeigeorte kennt und Terminals, Bilder und Eingaben dorthin routet (R011/R012), (2) eine Linux-Oberfläche (dieselben Fenster auf X11), (3) Linux-Adapter für Aufnahme, Fensterliste, Tasten und Maus. Siehe nächsten Abschnitt, sobald gebaut.

## 43. Version 0.9.1: Zeichnen erweitert und Bild-Element (2026-10-02)

Auf Daniels Wünsche nach dem Lesen der Prüflisten (siehe Nachtrag im Abnahmeprotokoll): Objekte haben jetzt `deckkraft`, `fett`, `kursiv`, `unterstrichen`; `Dokument.groesse_aendern`; der Zeichner kennt Schriftvarianten, Unterstreichen und Deckkraft (gemeinsamer Zeilenaufbau `text_masse_px`);
Editor: Radierer (Berührtes wird rot gerahmt, gelöscht beim Loslassen, ein Befehl), Stilumschalter, Deckkraft, Größer/Kleiner, Rechtsklick-Menü (`kontext_eintraege`); Leiste: Symbole, dritte Zeile (F K U, A−, A+, Deckkraft), „Ziel …“, „Größer/Kleiner“; Anwendung: `_zeichnen_kontext_menue`, `_zeichnen_ziel_menue` (Fensterliste), `bild_element_neu`; Raute-Menü „Bild einblenden …“.
Geändertes Verhalten: „Sichtbar für …“ zeigt alle Agenten, wenn im Ziel noch keiner gebunden ist (zwei alte Tests entsprechend angepasst). Tests 1150 (nur die drei bekannten Fehlschläge), Wine-Probe erweitert und grün. Paket SHA256 `c85a6b2a8be56820bcc2ed45e4ffe1a1307566242c8dbdd58324bc1546884800`.

**Nachtrag zu 43 (gleicher Tag, vor der Auslieferung von 0.9.1):** Daniel lehnte meine Auslegung ab („ich will es so wie ich sagte“): (1) Rechtsklick in der Zeichenfläche und am Bild-Element nur mit der Bedientaste (Strg+Alt) wie bei allen Bridge-Elementen; (2) das Bild-Element ist ein eigenes, immer direkt anfassbares Fenster (verschieben, Größe, Deckkraft), nicht nur im Zeichenmodus.
Umsetzung: `Objekt.schwebend`, `bild_element_fenster.py` (Muster des Selbstbild-Fensters), `bild_elemente.py` (Abgleich Dokument ↔ Fenster, Stillstandserkennung, Seitenverhältnis), Anwendung `bild_element_neu` legt das Bild direkt ins Gate, `bild_element_menue`. Die durchklickbare Anzeige zeichnet schwebende Bilder nicht mit. Tests (28 in `test_koerper_g08_erweiterung.py`) und Wine-Probe `probes/bild_element_smoketest.py` grün.

## 44. G06 gebaut: Linux-Körper, Anzeigeorte, X11-Adapter (2026-10-02)

Auf Daniels Auftrag („bau mal jetzt bis Goal 14 komplett durch und wir prüfen erst anschließend“; ChatGPT und Mikrofon zurückgestellt; „nutze den Skill unlazy“, „lies auch wieder die Skills und Harness zur Bridge“). Arbeitsweise: unlazy-Ledger `.unlazy/g06-g14/` mit Vertrag (PLAN.md, 20 Vertragszeilen) und Gates je Teilstück; Gates sind ausführbare Prüfungen, „nativ bei Daniel“ steht ausdrücklich als offen.

- **1.1.1 Linux-Fensterschicht:** GTK 3 + Pillow, `win32_linux`-Schicht für die wenigen direkten Win32-Aufrufe, Backend-Wahl `BRIDGE_BACKEND`. Befund: GDK setzt Form und Eingabeform von Toplevels zurück und die Begrenzungsform wird nicht durchgesetzt → XShape direkt über python-xlib, nach Konfiguration und Einblenden neu gesetzt.
- **1.1.2 X11-Adapter:** Aufnahme über XComposite (automatische Umleitung ändert Daniels Anzeige nicht; läuft ein Compositor, ist es nicht verfügbar und wird gemeldet), Eingabe über XTEST mit kurzer Umbelegung freier Tastencodes für Zeichen, die die Belegung nicht kennt, Not-Aus über XRecord (schluckt die Taste nicht). Befund: Strg+Alt+F1..F12 ist bei X-Servern das Umschalten der virtuellen Konsole und kommt bei keinem Programm an. Ziel-Schlüssel jetzt `<ort>:window:<kennung>` (`ziele.py`).
- **1.1.3 Relay-Routing:** `desktops.json`, `anzeigeorte.py` (Zugangsdaten, Verteiler), Starter mit Anzeigeort und Zielort je Terminal, neue Nachrichten (`anzeigeorte`, `terminal_ort`, `terminal_umziehen`, `terminal_ziel`, `ziel_zustand`), Körper-Seite (Menü, Ziel-Gast, Zielzustände). Ältere Körper kennen die Fähigkeit nicht und bekommen nichts Neues.
- **1.1.4 Linux-Körper:** `haupt.py` über eine Plattformbeschreibung (Windows unverändert), `haupt_linux.py`, Selbsttest, Startskript, XDG-Pfade. Befund beim ersten echten Lauf: Zustandsmeldungen kamen in falscher Reihenfolge an, weil `verschieben` und `fokus_erzwingen` die GTK-Schleife selbst weiterliefen und dabei aufgereihte Aufträge vorzogen → die Bibliothek pumpt nie mehr selbst; Lage und Größe sind jetzt maßgeblich im Fenster gespeichert.
- **Integration 1.1:** Nachrichten-Konsistenz, zwei echte Körper mit echtem Relay (Körper wandert von KDE 1 nach KDE 2 und nimmt die Sitzung mit Verlauf wieder auf), Windows-/Linux-Parität (Größen und Pixel), Regression (`tests/regression_alle.py`).
- Protokoll: `abnahmen/ABNAHME_G06.md`. Zwischenfall (Testsuite einmal gegen den sichtbaren vd1-Desktop) und Schutzmaßnahme dort.

## 45. 2026-10-02 — Praxis-Harness: konkrete Belege und Körperquittung

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
