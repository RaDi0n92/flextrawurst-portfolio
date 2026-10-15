# GEMINI — AUGEN & HÄNDE — VERBINDLICHER BAUPLAN, ETAPPEN UND BEWEISGATES

> **Geltungskorrektur durch Codex, 2026-09-19:** Vor dem nächsten Bau gilt `/root/werkraum/docs/augen_haende_bridge/2026-09-19_BRUECKE_BAUSTART_PRUEFUNG_UND_VEREINBARUNG.md`. B4.6 ist nur als Browser-Mechanik geprüft, nicht als natives Produkt abgenommen. Zuerst Buildfähigkeit und echter EXE-/VPS-Erstkontakt; erweiterte Kapseln und Hauhaucs danach. Anzeigeort Windows/KDE 1/2 bleibt vom Arbeitsziel unabhängig. Die folgenden älteren Etappenbeschreibungen bleiben als Herkunft erhalten und dürfen diese Korrektur nicht überstimmen.

> **Dokumentfamilie:** GEMINI — AUGEN & HÄNDE
>
> **Dieses Dokument ist der Bauplan, nicht das Zielbild.** Das Zielbild steht in `/root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md`, die Erweiterungs- und Portabilitätsschicht in `/root/werkraum/docs/systemdoku/77_worlddom_memory_seeds_wiedererweckung.md`, Geminis Spiegel in `/root/werkraum/_gemini/spiegel/2026-09-19_augen_und_haende_bridge.md` und die freie Android-/MLBB-Vision in `/root/werkraum/docs/vision/augen_und_haende_androidbridge_mlbb_dream.md`.
>
> **Provenienz:** Dieses Planblatt ordnet den vorhandenen Gemini-Prototypen und die von Daniel/Codex beschriebene Zielarchitektur in einen überprüfbaren Bauablauf ein. Es ersetzt keine vorhandene Vision und löscht keinen Prototypen.

## 1. Auftrag und Arbeitsvertrag

Wir bauen die Augen-und-Hände-Bridge als einen sichtbaren, modularen und wiederaufnehmbaren Übergang zwischen Linux-VPS, Windows-Desktop und später Android. Die Bridge soll Bilder, Webcam-/Screen-Frames, Texte, Fenster-/UI-Strukturen, Agenten-Rauten, Eingaben, Leases, Harnesses, WorldDOM-Schichten und Memory Seeds tragen können.

Eine zentrale Architekturregel ist **Ziel-Isolation bei gleichzeitiger Parallelität**: Mehrere Agenten dürfen gleichzeitig in unterschiedlichen Bedienräumen arbeiten. Ein Agent kann an einen Linux-KDE-Desktop oder ein Original-Terminal auf dem VPS gebunden sein, während ein anderer Agent den physischen Windows-Desktop nutzt. Diese Ziele teilen sich nur ausdrücklich freigegebene Ereignisse und Daten — niemals stillschweigend Maus, Tastatur, Fokus oder private Frames.

Der Bau erfolgt nicht als Big-Bang. Jede Etappe liefert:

1. eine kleine, benutzbare Erweiterung,
2. einen konkreten Beweis, dass sie funktioniert,
3. eine Auditspur mit Herkunft und Ergebnis,
4. einen eigenen Git-Sicherheitspunkt,
5. eine explizite Liste dessen, was noch nicht behauptet werden darf.

Eine Etappe gilt erst als fertig, wenn ihr Gate grün ist. Ein vorhandenes Screenshot-Proof, ein Test mit synthetischen Daten oder eine erfolgreiche WebSocket-Verbindung zählt nur für genau das, was dieser Beweis tatsächlich abdeckt.

### Greenfield-Entscheidung

Der vorhandene Gemini-Prototyp unter `/root/werkraum/_gemini/windows_bridge/` wird **nicht** zum neuen Produktionskern umgebaut. Er bleibt unangetastet als Referenz, historische Herkunft und Vergleichsmaterial. Der Neubau erhält einen eigenen Baupfad, eine eigene Konfiguration, eigene Tests und eigene Auditspuren. Der genaue neue Pfad und die erste Modulgrenze werden nach Daniels Skizze festgelegt.

### Visuelle Referenzschicht

Die visuelle Ausgangsskizze für den Greenfield-Neubau liegt unter `/vps_root/werkraum_bilder/refferenzen/h a bridge.jpg`. Sie wird als Daniels Entwurfsreferenz gelesen, nicht als bereits entschiedene technische Spezifikation. Besonders zu prüfen sind die Regie-/Kamera-Schalter, die mehreren Terminal-/Agentenflächen, die individuellen Rauten/Teilnehmer und die Verbindungen zwischen den Bereichen.


## 2. Aktueller Zustand — ehrlich eingefroren

### Vorhanden — eingefrorene Referenz, nicht der neue Baukern

- Der Prototyp liegt unter `/root/werkraum/_gemini/windows_bridge/`.
- Der laufende Server ist `/root/werkraum/_gemini/windows_bridge/bridge_server.py`.
- Die vorhandene Eingabeschicht ist `/root/werkraum/_gemini/windows_bridge/input_arbitrator.py`.
- Die vorhandene MCP-Anbindung ist `/root/werkraum/_gemini/windows_bridge/mcp_desktop_bridge.py`.
- Der Windows-Client liegt unter `/root/werkraum/_gemini/windows_bridge/client_windows/windows_copilot_gui.py`.
- Der Linux-Client liegt unter `/root/werkraum/_gemini/windows_bridge/client_linux/backend_linux.py`.
- Bestehende Prüfungen und Beweisbilder liegen unter `/root/werkraum/_gemini/windows_bridge/tests/`.
- Die konzeptionell vorgesehenen, aber noch nicht belastbar implementierten Erweiterungen heißen:
  - `/root/werkraum/_gemini/windows_bridge/harness_engine.py`
  - `/root/werkraum/_gemini/windows_bridge/vision_session_manager.py`
  - `/root/werkraum/_gemini/windows_bridge/overlay_canvas.py`
  - `/root/werkraum/_gemini/windows_bridge/worlddom.py`
  - `/root/werkraum/_gemini/windows_bridge/memory_seed_router.py`

### Noch nicht als sicher oder produktionsreif behauptbar

- Der Server lauscht derzeit standardmäßig auf `0.0.0.0:9880`; es gibt noch keinen belastbaren Identitäts- und Berechtigungsrahmen.
- `/root/werkraum/_gemini/windows_bridge/bridge_server.py` besitzt einen Remote-Console-Pfad, der Shell-Befehle ausführen kann. Dieser Pfad ist für einen sicheren Betrieb zu mächtig und wird vor einer Freigabe stillgelegt, ersetzt oder auf eine eng definierte Befehlsregistry reduziert.
- `/root/werkraum/_gemini/windows_bridge/mcp_desktop_bridge.py` darf Erfolg nicht melden, wenn der Server eine Aktion abweist oder nur teilweise ausführt. Die Rückgabe muss einen echten Transport-, Policy- und Ausführungsstatus unterscheiden.
- `/root/werkraum/_gemini/windows_bridge/client_linux/backend_linux.py` erzeugt nach der aktuellen Bestandsaufnahme teilweise synthetische Desktop-Bilder. Das ist ein Demo-Beleg, kein Beweis für echte Bildschirmwahrnehmung.
- Die vorhandenen Playwright-/Screenshot-Beweise sind wertvoll als Herkunft und Regression, beweisen aber nicht automatisch Hardware, echte Win32-Eingabe, UIPI-Verhalten, Webcam-Datenschutz, globale F12-Abschaltung oder reale Android-Fähigkeiten.
- Der aktuell laufende Prozess und die eingefrorene Referenz werden während des Greenfield-Baus nicht ungefragt neu gestartet oder verändert. Änderungen am Neubau werden zunächst offline geprüft und erst in einem ausdrücklich gewählten Betriebsfenster aktiviert.

## 3. Nicht verhandelbare Leitplanken

### 3.1 Sicherheit und Kontrolle

- Default ist `observe-only`: sehen, inspizieren, auditieren; keine Eingabe.
- Eingabe ist eine explizite Fähigkeit mit eigenem Capability-Profil, Lease, Ablaufzeit und Zielbindung.
- Daniel hat einen sichtbaren, lokalen Not-Aus. Der Not-Aus muss unabhängig vom WebSocket, MCP, Agentenstatus und UI-Thread wirken.
- Der Sicherheitsstatus ist fail-closed: unbekannter Zustand, abgelaufener Lease, falsches Target-/Fensterziel, fehlende Bestätigung oder Verbindungsabbruch blockiert Eingabe.
- Keine öffentliche Bindung ohne Authentisierung, Autorisierung und Transportabsicherung.
- Die Bridge darf keine beliebige Remote-Shell als normale Agentenfähigkeit anbieten. Systemaktionen werden später über eine versionierte, allowlist-basierte Befehlsregistry mit Parametervalidierung modelliert.
- Keine Credentials, privaten Frames, Tokens oder Schlüssel in Exporten, Screenshots, Git oder Audittexten.

### 3.2 Provenienz und Sichtbarkeit

Jedes Bild, jeder Text, jede Raute, jeder WorldDOM-Knoten und jede Aktion trägt mindestens:

```python
source = "real" | "inferred" | "authored" | "projected" | "synthetic"
visibility = "daniel" | "shared_gate" | "agent:<id>" | "local_only"
status = "vision" | "planned" | "implemented" | "integrated" | "proven" | "blocked"
```

`synthetic` ist kein verstecktes `real`. `inferred` ist kein DOM. `projected` ist keine echte Anwendungseinfügung. Eine Präsentations-Overlay-Schicht und eine echte Zielanwendungseinfügung bleiben getrennte Fähigkeiten.

### 3.3 Architektur

- Das Protokoll wird additiv erweitert; alte, nachvollziehbare Nachrichten bleiben lesbar, solange sie nicht unsicher wären.
- Server, Eingabearbitrierung, MCP, Windows-Client, Linux-Adapter, Android-Adapter, WorldDOM, Harness und Memory Seeds haben getrennte Grenzen.
- Zustand wird append-only auditiert. Sichtbarkeit wird geändert, Daten werden nicht still gelöscht.
- Jede Aktion folgt dem Muster `request -> policy -> lease -> dispatch -> observed result -> audit`.
- Frames werden als zeitgebundene Snapshots und Ringbuffer geführt, nicht als unendlicher oder unkontrollierter Stream.
- Agenten dürfen später Brücken entwerfen und ausführen, aber nur über deklarierte Fähigkeiten, deklarierte Zielräume und sichtbare Policyprofile.

## 4. Zielarchitektur in Schichten

```text
                 ┌──────────────────────────────────────────┐
                 │ Daniel / HUD / lokaler Not-Aus           │
                 └───────────────┬──────────────────────────┘
                                 │ lokale Kontrolle
┌────────────────────┐     ┌─────▼───────────────────┐     ┌──────────────────────┐
│ Windows-Surface    │────▶│ Bridge-Kern              │◀────│ Linux-KDE-Ziele       │
│ Capture / UIA/Input│     │ Sessions, Policy, Audit  │     │ Original-Terminals    │
│ Agent: Codex       │     │ Ziel-Isolation           │     │ Agent: Gemini         │
└────────────────────┘     └─────┬───────────────────┘     └──────────────────────┘
                                 │
                ┌────────────────┼─────────────────┐
                ▼                ▼                 ▼
          MCP-Fassade       WorldDOM           Event/Audit
                │                │                 │
                ▼                ▼                 ▼
           Agenten         authored/inferred   Replay/Proof
                                 │
                ┌────────────────┴─────────────────┐
                ▼                                  ▼
          Harness Engine                       Memory Seeds
          DAG / Checkpoints                     portable state
```

Die späteren Android- und Spieloberflächen sind Adapter an diesen Kern. Sie sind keine Sonderlogik im Kern und dürfen keine unsichtbare Abkürzung an den Sicherheits- und Auditgrenzen vorbei bekommen.

### 4.1 Bedienräume / Surfaces

Die Windows-Bridge besitzt eine eigene sichtbare `Surface`; VPS-Ziele bleiben die dort bereits vorhandenen Linux-Arbeitsräume. Ein `Target` bezeichnet das konkrete Ziel, an das ein Agent, ein Overlay oder eine Aktion gebunden wird. Beispiele sind:

- `target:windows:window:<id>` — ein einzelnes Windows-Fenster.
- `target:windows:desktop:<device-id>` — der gesamte Windows-Desktop einschließlich Taskleiste, Hintergrund und offenen Fenstern.
- `target:linux:kde:<host>:desktop:<number>` — ein vorhandener KDE-Virtual-Desktop auf dem VPS, zum Beispiel Desktop 1 oder Desktop 2.
- `target:linux:terminal:<session-id>` — ein vorhandenes Original-Terminal auf dem VPS.
- später weitere Zieltypen wie Android-Gerät, Browserfenster oder Programmfläche.

Die Windows-Surface ist die sichtbare Regie-, Kontroll- und Verknüpfungsschicht. Eine Agenten-Session darf mehrere Targets abonnieren, verbinden, austauschen oder beobachten. Eine Aktion muss aber immer ein explizites `target_id` tragen. Ein Agent, der auf einem Linux-KDE-Desktop oder Original-Terminal arbeitet, erhält dadurch nicht automatisch Zugriff auf Windows; ein Windows-Agent kann parallel laufen, ohne den Linux-Fokus zu übernehmen.

Die gemeinsame Ebene besteht aus bewusst publizierten Events, Overlay-/Textobjekten mit Audience-Regel, delegierten Aufträgen und Memory Seeds. Surface-lokale Zustände — Cursor, Tastatur, Fensterfokus, Webcam, private Frames, Terminal und Leases — bleiben getrennt.

## 5. Etappenübersicht

| Etappe | Name | Ergebnis | Gate |
|---|---|---|---|
| 0 | Baseline und Inventur | reproduzierbarer Ist-Zustand, Beweismatrix | B0 |
| 1 | Sicherheitsgrenze und Protokollvertrag | Identität, Capability-Policy, sichere Defaults | B1 |
| 2 | Deterministischer Bridge-Kern | Loopback-Server mit echten Statuscodes und Audit | B2 |
| 3 | VisionSession und Frame-Ring | start/pause/resume/stop, private/shared Frames | B3 |
| 4 | Input-Arbitrator und Failsafe | Leases, Zielkäfig, Kill-Switch, Hardware-Abstraktion | B4 |
| 4.5 | Terminal-Parität und Live-Target-Switcher | echte Original-Terminals lesen, Ziele sichtbar wechseln, sichere Eingabe-Rundreise | B4.5 |
| 4.6 | Referenzgetriebene Windows-Bridge-Surface | räumliche Ziel-/Agenten-/Terminal-Surface gemäß Referenz, ohne Homepage-Modus | B4.6 |
| 5 | MCP-Fassade | ehrliche Inspect-/Act-/Status-Verträge | B5 |
| 6 | Windows-Live-Slice | echter Capture-/HUD-/Input-Beleg auf Windows | B6 |
| 7 | Linux-Live-Slice | echter Capture-/Terminal-/Reconnect-Beleg auf Linux | B7 |
| 8 | Overlay Canvas und WorldDOM v1 | verschiebbare Texte/Bilder plus erfundene DOM-Schicht | B8 |
| 9 | Harness Engine | deklarative Mehrschritt-Workflows mit Checkpoints | B9 |
| 10 | Memory Seed Router | sichtbares Pflanzen, Vorschlagen, Aktivieren und Exportieren | B10 |
| 11 | Multi-Agent-Orchestrierung | Gate-/Audience-/Lease-getrennte Zusammenarbeit | B11 |
| 12 | Android-Adapter | MediaProjection-/Accessibility-basierter Prototyp | B12 |
| 13 | Portabilität und Open-Source-Bundle | Backup, Wiedererweckung, Installationspfad, Release-Checks | B13 |

## 6. Etappen im Detail

### Etappe 0 — Baseline und Inventur

**Zweck:** Den vorhandenen Prototypen vermessen, ohne ihn durch Optimismus oder einen Neustart zu verfälschen.

**Vorbedingungen:** Sicherheitspunkte `64d8bed0c3` und `1ffb4b4b2b` in `/root/werkraum` sind vorhanden. Der laufende Prozess und die eingefrorene Referenz bleiben unangetastet. Daniels Skizze legt den neuen Baupfad und die erste vertikale Scheibe fest.

**Arbeiten:**

- Die eingefrorene Referenz vollständig katalogisieren, aber keine Datei daraus in den Neubau kopieren, bevor ihre Herkunft und Sicherheitsbedeutung geprüft wurden.
- Den neuen Baupfad aus Daniels Skizze ableiten und als leeres, eindeutig getrenntes Modulgerüst anlegen.
- Die vorhandenen Proofs in `real`, `synthetic`, `mocked`, `unverified` klassifizieren; sie gelten nur als Referenz, nicht als Neubau-Beweis.
- Für jede gewünschte neue Fähigkeit eine Claim-Matrix anlegen: Behauptung, Quelle, Methode, Ergebnis, Restunsicherheit.
- Die Remote-Console des alten Prototyps als `high risk / frozen reference / not releaseable` markieren.

**Beweis B0:** Eine neue Baseline-Datei im neuen Baupfad enthält die Skizzenentscheidung, die neue Modulgrenze, die Referenz-Claim-Matrix und bekannte Lücken. Kein Test darf den eingefrorenen Dienst neu starten, in dessen Dateien schreiben oder externe Eingaben auslösen.

**Rücksprung:** Nur neue Baseline-Dateien entfernen oder zurücksetzen; vorhandene Gemini-Dateien und Logs bleiben erhalten.

### Etappe 1 — Sicherheitsgrenze und Protokollvertrag

**Zweck:** Erst definieren, wer was anfordern darf und wie ein Ergebnis aussieht.

**Arbeiten:**

- Standardbindung auf Loopback oder explizit konfigurierte sichere Adresse umstellen.
- Client-Identität, Agent-ID, Session-ID, sichtbare `surface_id` und konkrete `target_id`, Capability-Profil, Lease-ID und Ablaufzeit als Pflichtfelder für aktionsfähige Nachrichten definieren.
- `observe`, `overlay`, `say`, `input`, `terminal` und `admin` als getrennte Fähigkeiten behandeln.
- Jede Aktion mit `accepted`, `denied`, `expired`, `dispatched`, `observed`, `failed` oder `unknown` beantworten.
- Payload-Größen, Base64-Frames, Textlängen, Koordinaten, Hotkeys und Frequenzen begrenzen.
- Remote-Shell nicht weiter als allgemeine Aktionsart führen. Für spätere Terminalarbeit eine eigene, eingeschränkte Capability mit deklarierten Operationen vorsehen.
- Schema-Version und Korrelations-ID in alle neuen Nachrichten aufnehmen.

**Beweis B1:** Negative Tests zeigen, dass ein Client ohne Token/Identität, ohne Capability, mit abgelaufenem Lease, falschem Ziel, zu großer Payload oder unbekanntem Aktionsnamen abgewiesen wird. Positive Tests zeigen, dass eine reine Inspect-Verbindung weiterhin möglich ist.

**Rücksprung:** Protokolländerungen additiv versionieren. Keine bestehende historische Auditspur umschreiben.

### Etappe 2 — Deterministischer Bridge-Kern

**Zweck:** Den Transport so stabil machen, dass spätere Module nicht auf impliziten Seiteneffekten beruhen.

**Arbeiten:**

- Gemeinsame Nachrichtentypen in einem kleinen Modul definieren, zunächst als Python-Dataclasses plus JSON-Schema-Test.
- Einen isoliert startbaren Testserver mit injizierbarem Audit-Sink schaffen.
- Ping/Pong, Register, Status, Frame-Annahme, Action-Request, Action-Result, Emergency-Stop und Reconnect deterministisch testen.
- Audit-Ereignisse append-only schreiben und mit Korrelations-ID verknüpfen.
- Backpressure, maximale Framezahl und Disconnect-Verhalten festlegen.
- Zeit aus einer injizierbaren Clock beziehen, damit Lease- und Timingtests nicht flakey sind.

**Beweis B2:** Ein isolierter Loopback-Test erzeugt eine vollständige Kette `register -> inspect -> action denied/accepted -> observed result -> audit -> disconnect`, ohne echte Maus, Tastatur, Webcam oder externe AI.

**Rücksprung:** Der Testkern darf neben den vorhandenen Prototyp treten. Erst wenn B2 grün ist, wird er als neuer Produktionspfad verbunden.

### Etappe 3 — VisionSession und Frame-Ring

**Zweck:** „Jetzt starten, ab hier Bilder einspritzen, pausieren, fortsetzen, abschalten und zurückscrubben“ als belastbaren Zustand bauen.

**Arbeiten:**

- `VisionSession` mit `start`, `pause`, `resume`, `stop`, `seek` und `close` definieren.
- Frame-Quellen unterscheiden: `live_capture`, `file`, `synthetic`, `replay`.
- Ringbuffer mit Zeitstempel, Frame-ID, Quelle, Sichtbarkeit, Zielgruppe, Hash und Lösch-/Ablaufregel führen.
- Ein Frame darf an alle eines Gates, an einzelne AI-Ströme oder nur an Daniel gehen.
- Private Frames werden vor der Auslieferung empfängerbezogen komponiert; es gibt keinen globalen „privat, aber trotzdem im gemeinsamen Frame“-Zustand.
- Startpunkt und Scrub-Ziel als immutable Checkpoint referenzieren.

**Beweis B3:** Zwei Empfänger erhalten nachweisbar unterschiedliche Frame-Sichten; `pause` stoppt neue Frames; `resume` setzt die Sequenz fort; `seek` startet einen neuen Branch mit sichtbarer Herkunft; `stop` verhindert weitere Auslieferung.

**Rücksprung:** Ein Session-Branch wird deaktiviert, nicht aus der Auditspur gelöscht.

### Etappe 4 — Input-Arbitrator und Failsafe

**Zweck:** Eingabe erst dann ermöglichen, wenn Eigentum, Ziel und Not-Aus eindeutig sind.

**Arbeiten:**

- Capability-Profile für `observe-only`, `overlay-only`, `window-scoped`, `foreground-input` und spätere Spezialadapter definieren.
- Leasevergabe mit Besitzer, Ziel, Ablauf, Erneuerung, Grund und sichtbarer HUD-Anzeige bauen.
- Daniel-Input widerruft oder pausiert AI-Input sofort; das muss im Audit sichtbar werden.
- Click-Cage, Fenster-/Monitor-Ziel, DPI-Koordinatentransformation und Fokusprüfung getrennt testen.
- F12/Not-Aus auf der jeweiligen Maschine lokal und hardware-/hooknah implementieren; WebSocket-Ausfall darf ihn nicht verhindern.
- Win32-Transporte getrennt behandeln: `PostMessage` ist fensterbezogen und hat andere Grenzen als `SendInput`; Erfolg wird nicht aus dem bloßen Aufruf abgeleitet.
- Linux-Eingabe getrennt von Windows-Input testen; kein falscher Plattform-Claim.

**Beweis B4:** Automatisierte Tests und ein lokaler manueller Beleg zeigen: fremder Agent wird abgewiesen; außerhalb des Zielkäfigs wird blockiert; Ablaufzeit stoppt Eingabe; F12 stoppt innerhalb des gemessenen Zielbudgets; tatsächliche Dispatch- und beobachtete Resultate stimmen überein.

**Rücksprung:** Aktionsfähigkeit deaktivieren, nicht den Beobachtungsweg. Keine globale Eingabe im Default.

### Etappe 4.5 — Terminal-Parität und Live-Target-Switcher

Die Etappe ist in zwei Gates geteilt: **B4.5a** beweist Discovery, sichtbaren Zielwechsel und echte read-only Snapshots. **B4.5b** beweist erst danach die gekäfigte Eingabe-Rundreise. Beide Gates sind abgeschlossen.

**Zweck:** Die Bridge muss vor MCP beweisen, dass sie nicht nur synthetische Zielkarten kennt, sondern die vorhandenen Arbeitsräume tatsächlich unterscheiden, lesen und sichtbar umschalten kann. Das Original-Terminal ist dabei Referenz und lebendes Ziel zugleich.

**Wichtige Architekturentscheidung:** Die sichtbare Bridge-/Regie-Surface bleibt auf Windows. Linux bekommt keine zweite Bridge-Surface. `target:linux:kde:<host>:desktop:<number>` und `target:linux:terminal:<session-id>` sind reale Ziele im vorhandenen VPS-Arbeitsraum. Der Switcher wechselt also das Zielbild bzw. die Zielbindung in der Windows-Surface, nicht die Surface selbst.

**Ist-Baseline vom 2026-09-19:** In der laufenden KDE-Sitzung wurden die vorhandenen Konsole-Instanzen ausschließlich lesend inventarisiert. Sichtbar waren unter anderem die D-Bus-Dienste `org.kde.konsole-396627`, `org.kde.konsole-396725`, `org.kde.konsole-396779` und `org.kde.konsole-1060933`. Ihre Sessions liefern Scrollback über `getDisplayedText`/`getAllDisplayedText`, Prozess- und Foreground-PIDs sowie Session-Titel. Diese Bestandsaufnahme ist eine Referenzbeobachtung, kein bereits gebaulter Bridge-Adapter und kein Beleg für Eingabeberechtigung.

**Arbeiten:**

- Einen `TargetRegistry` mit Provenienz, Host, Surface-Bindung, Zieltyp, Session-/Fensterkennung, Capture-Methode und `real|synthetic|unavailable`-Status bauen.
- Den Switcher auf der Bridge-Surface sichtbar machen: Windows-Gesamtdesktop, Windows-Fenster, KDE-Desktop 1/2 und jedes registrierte Original-Terminal sind einzeln auswählbar; das aktuell aktive Ziel, seine Herkunft, sein Alter und seine Capability werden rückgelesen.
- Für Original-Terminals einen Linux-Konsole-Adapter zunächst nur für `inspect` bauen: Scrollback, Prompt-/Cursor-Nähe, Session-PID, Foreground-PID, sichtbare Geometrie und Capture-Zeitpunkt werden als Snapshot geliefert. Ein fehlender Adapter oder unlesbarer Zustand heißt `unavailable`, nie `success`.
- Den exakten Eingabeweg als beobachtbare Zustandsmaschine modellieren: `accepted -> delivered -> echoed -> observed -> audited`. Jeder Übergang braucht Korrelation-ID, Ziel, Lease, Probe-Token und Zeitstempel.
- Für den ersten Live-Probe nur einen eindeutig markierten, reversiblen Text verwenden, der nicht als Shell-Befehl interpretiert wird, zum Beispiel eine abgesicherte Echo-Zeile mit eindeutiger Run-ID. Die Probe wird erst nach aktivem Ziel, gültigem Lease und sichtbarer Daniel-Freigabe gesendet.
- Nach dem Senden den echten Terminal-Scrollback erneut lesen und den eindeutigen Marker im Originalziel finden. Ein lokales „send returned true“, ein UI-Klick oder eine synthetische Echozeile zählt nicht als Zustellung.
- Die Playwright-Prüfung muss den Zielwechsel klicken, den sichtbaren Terminal-Snapshot rücklesen, die Probe auslösen, die fünfstufige Kette und die Auditzeile anzeigen, einen Screenshot schreiben und die Evidence-Datei erzeugen.
- Den gleichen Beleg für KDE-Desktop 1 und 2 als Beobachtungsziele vorbereiten. Desktop-Wechsel darf keine fremde Terminal-Session fokussieren und kein Windows-Input erzeugen.

**Beweis B4.5a:** Playwright schaltet zwischen mindestens drei echten oder explizit als nicht verfügbar markierten Zielen um. Für mindestens ein laufendes Original-Terminal zeigt die Bridge einen echten rückgelesenen Snapshot mit Quelle, Verfügbarkeit, Session-/Foreground-PID und Auditzeile. Jeder synthetische oder nicht verfügbare Zustand bleibt sichtbar gekennzeichnet. Evidence: `/root/werkraum/augen_haende_bridge/tests/evidence/B4_5A_TERMINAL_SWITCHER_EVIDENCE.md`.

**Beweis B4.5b:** Erst ein ausdrücklich gekäfigtes Probe-Terminal darf eine eindeutig markierte, reversible Probe empfangen. Playwright weist danach `accepted -> delivered -> echoed -> observed -> audited` im echten Original-Scrollback, in der sichtbaren Surface und im Audit nach. Nach Lease-Ablauf oder Not-Aus wird keine weitere Terminaleingabe ausgelöst. Ein laufendes Codex-, Claude- oder Gemini-Terminal ist kein Probe-Terminal.

**B4.5b-Ergebnis:** Das Gate ist mit `/root/werkraum/augen_haende_bridge/tests/evidence/B4_5B_CAGED_TERMINAL_PROBE_EVIDENCE.md` und `/root/werkraum/augen_haende_bridge/tests/evidence/playwright_b4_5b_terminal_probe.png` grün. Konsole verweigert `sendText` und `runCommand` als sicherheitssensitive D-Bus-Methoden; die laufende Wayland-Komposition bietet kein nutzbares Virtual-Keyboard-Protokoll. Der geprüfte Handweg ist deshalb ein kontrollierter PTY-Controller für ein eigenes Probe-Terminal, während die Ausgabe weiterhin aus echtem Konsole-Scrollback gelesen wird.

**Nicht behauptet:** B4.5 beweist noch keine allgemeine Shell-Fähigkeit, keine freie Remote-Shell, keine Windows-Eingabe und keine MCP-Integration. Es beweist nur die eng begrenzte, beobachtete Target-/Terminal-Parität für die freigegebene Probe.

**Rücksprung:** Adapter auf `inspect-only` zurücksetzen und Test-Lease widerrufen. Original-Terminals, laufende Agenten und der eingefrorene Gemini-Prototyp werden nicht beendet oder verändert.

### Etappe 4.6 — Referenzgetriebene Windows-Bridge-Surface

**Zweck:** Die sichtbare Oberfläche folgt der Referenz als räumliche Bridge- und
Regieschicht. Sie ist keine Homepage und ersetzt die Referenz nicht durch ein
generisches Dashboard. Das bisherige Proof-Panel bleibt ausschließlich ein
internes technisches Diagnosewerkzeug.

**Herkunft, die unverändert bleibt:** Windows trägt die Bridge-Surface. Linux-KDE-
Desktops 1/2 und vorhandene Original-Terminals sind Targets. Der gesamte
Windows-Desktop kann ebenso wie ein einzelnes Fenster gebunden werden. Pfeile
tragen nur Beschriftungen; sie sind keine behaupteten Datenleitungen.

**Sichtbare Bausteine:**

- linke Ziel-/Bindungsschiene für Windows-Desktop, KDE-Desktops und Original-Terminals,
- zentrale gebundene Desktopfläche als Zielraum,
- individuell benennbare bzw. farblich konfigurierbare Agenten-Rauten,
- beschriftete Beziehungen `sehen`, `sprechen`, `handeln`, `weitergeben`,
- vier verschiebbare Terminalflächen mit eigenem Fensterscanner unten rechts,
- Regiefläche unten links mit pro Agent schaltbarem Mikrofon, Kamera und Spruch,
- individuell veränderbare Transparenz und sichtbare Rücklese des letzten Zustands.

**Beweis B4.6:** Playwright öffnet die Surface, weist den Nicht-Homepage-Status,
vier Rauten, vier Terminalflächen, Zielschiene und Regie nach. Danach wechselt es
auf `Linux KDE Desktop 1`, schaltet einen Agenten-Mikrofon-/Kamerazustand,
sendet einen Regiespruch, öffnet den Terminal-2-Fensterscanner, verändert die
Transparenz und verschiebt eine Raute. Screenshot, DOM-Rücklese und Evidence:
`/root/werkraum/augen_haende_bridge/tests/evidence/B4_6_REFERENCE_SURFACE_EVIDENCE.md`.

**Nicht behauptet:** B4.6 ist noch kein echter Windows-Capture-Adapter, kein
MCP-Tool und keine automatische Fenstersteuerung. Die Surface ist die sichtbare,
interaktive Referenzschicht; die darunterliegenden Plattformadapter bleiben
nachgelagerte Gates.

**Rücksprung:** `Layout zurücksetzen`, einzelne Bindung lösen oder die aktive
Fähigkeit pro Agent abschalten. Keine zweite Bridge-Surface auf Linux erzeugen.

### Etappe 5 — MCP-Fassade

**Zweck:** MCP als schmale, ehrliche Bedienoberfläche auf den Bridge-Kern setzen.

**Arbeiten:**

- `windows_desktop_inspect`, `windows_desktop_act` und `windows_desktop_status` auf den neuen Vertrag umstellen.
- MCP-Toolantworten müssen Transport-, Policy-, Dispatch- und Beobachtungsstatus unterscheiden.
- Ablehnung oder Timeout darf nie als `success: true` erscheinen.
- Inspect bekommt Größen-/Zeit-/Quelle-Metadaten und kennzeichnet synthetische Frames.
- Act bekommt Idempotenz-/Korrelations-ID, Capability- und Lease-Referenz.
- Sensitive Tools erhalten eine echte lokale oder netzwerkfähige Autorisierungsschicht; kein „localhost heißt automatisch vertrauenswürdig“.
- MCP-Spezifikationsstand und verwendete SDK-/Transportversion dokumentieren; keine stillen Annahmen über zukünftige MCP-Tasks oder Authorization-Flows.

**Beweis B5:** Ein MCP-Test prüft mindestens: echte Bildrückgabe, Status, erlaubte Aktion, abgewiesene Aktion, unbekannte Aktion, übergroße Payload und Not-Aus. Jede Antwort wird gegen die Server-Auditspur rückgelesen.

**Rücksprung:** MCP kann auf den isolierten Testserver zeigen; der alte Pfad bleibt als historische Referenz sichtbar, aber nicht als sicherer Produktionsclaim.

### Etappe 6 — Windows-Live-Slice

**Zweck:** Die erste echte vertikale Strecke auf dem Windows-Laptop: Capture → Bridge → Inspect/HUD → optional eng begrenzte Eingabe → Audit.

**Arbeiten:**

- Reale Fenster-/Monitorgeometrie mit DPI-Metadaten erfassen.
- Genau einen aktuellen Vision-Frame plus kleinen Ringbuffer liefern; keine unkontrollierte Webcam-Dauerweitergabe.
- Webcam-Inlay mit separatem Ein-/Aus-Schalter und Provenienz bauen.
- HUD zeigt Verbindungsstatus, Session, Sichtbarkeit, Lease, aktuelles Ziel, Inputstatus und Not-Aus an.
- Fensterbezogene Eingabe zuerst an einer ungefährlichen Testanwendung prüfen.
- DPI, UIPI, Vollbild, Fokusverlust, Fensterbewegung, Displaywechsel und Lock-Screen explizit als Fälle testen.
- Portable Ausführung erst nach reproduzierbarem Quelllauf; EXE-Build ist ein Packaging-Schritt, kein Funktionsbeweis.

**Beweis B6:** Ein Windows-Belegpaket enthält sichtbaren HUD-Status, echte Frame-Metadaten, eine erfolgreiche ungefährliche Testaktion, eine blockierte Aktion, Not-Aus und die zugehörigen Auditzeilen. Kein Beleg behauptet bereits Spielautomatisierung.

**Rücksprung:** Client in `observe-only` starten; Input-Fähigkeit per Profil abschalten.

### Etappe 7 — Linux-Live-Slice

**Zweck:** Die VPS-/Linux-Seite mit echten Zuständen und sauberem Reconnect beweisen.

**Arbeiten:**

- Synthetische Frames im Code eindeutig als Demoquelle markieren.
- Reale Capture-Quelle für die konkrete Desktop-Umgebung wählen und ihre Voraussetzungen dokumentieren: X11, Wayland, PipeWire, Rechte und Headless-Modus sind nicht austauschbar.
- Terminal- und Fensterstatus nur mit deklarierter Capability liefern.
- Reconnect, Backoff, veraltete Frames, Serverneustart und Session-Wiederaufnahme testen.
- Kein Terminal-Schreiben in laufende Systeme ohne explizite, auditable Ziel- und Leasebindung.

**Beweis B7:** Ein Linux-Beleg unterscheidet echte und synthetische Capture-Quellen, zeigt mindestens einen echten Reconnect und weist nach, dass ein abgelaufener Lease kein Terminal-/Input-Event mehr auslöst.

### Etappe 8 — Overlay Canvas und WorldDOM v1

**Zweck:** Bilder und Texte sichtbar, verschiebbar und empfängerbezogen machen; zusätzlich eine erfundene, aber ehrlich markierte Interaktionsschicht bauen.

**Arbeiten:**

- Overlay-Objekte als deklarative Entitäten mit Position, Größe, Z-Index, Zielbindung, Sichtbarkeit, Lebenszeit und Herkunft definieren.
- Zielbindungen unterscheiden: Desktop, Browser, Programm, Fenster, Gate, Agenten-Raute und freie Weltposition.
- `shared_gate`, `agent:<id>`, `daniel` und `local_only` als Audience-Regeln testen.
- WorldDOM-Knoten als `real`, `inferred`, `authored` oder `projected` markieren.
- Resolver von Datenquelle zu sichtbarem Overlay und von WorldDOM-Aktion zu realer Fähigkeit trennen.
- Ein erfundener Knoten darf kreativ sein; er darf nicht vorgeben, ein echtes DOM-Element oder eine echte API zu sein.

**Beweis B8:** Zwei Empfänger sehen kontrolliert unterschiedliche Text-/Bildobjekte; ein `authored` WorldDOM-Knoten ist sichtbar als authored markiert; ein nicht auflösbarer Knoten erzeugt `blocked` statt einer heimlichen Aktion.

### Etappe 9 — Harness Engine

**Zweck:** Mehrschrittiges Klicken und Tun als pausierbare, nachvollziehbare Arbeitsgraphen ermöglichen.

**Arbeiten:**

- Zustandsknoten, Aktionsknoten, Bedingungen, Fallbacks, Checkpoints, Timeouts und Abbruchkanten definieren.
- Standardmodus bleibt frei konfigurierbar, aber jede konkrete Fähigkeit wird einzeln eingeschaltet.
- `preview`, `simulate`, `execute`, `pause`, `resume`, `abort` und `replay` trennen.
- Vor-/Nachher-Prüfung verlangt eine beobachtete Änderung; „Befehl gesendet“ ist kein Erfolg.
- Zeit-Scrubber erzeugt keinen magischen Rücksprung in die reale Welt: Er erzeugt einen neuen Replay-/Planungszweig, bis eine neue reale Aktion ausdrücklich ausgeführt wird.
- Agenten dürfen einen Graphen vorschlagen; Ausführung läuft durch Policy, Lease, Zielkäfig und Audit.

**Beweis B9:** Ein ungefährlicher Workflow mit mindestens drei Knoten läuft vollständig, pausiert, wird ab Checkpoint in einen Branch gescrubbt, läuft in einen Fallback und zeigt im Audit Plan, Dispatch und Beobachtung getrennt.

### Etappe 10 — Memory Seed Router

**Zweck:** Daniels gewünschte Möglichkeit bauen, Wissen gezielt in Memories, Agenten-MDs, Skills, Harnesses, Loops, Automationen und Goals einzuspeisen, ohne Herkunft zu verwischen.

**Arbeiten:**

- Seed-Typen für Regel, Fakt, Erfahrung, offene Frage, Skill-Erweiterung, Harness-Lektion, Goal-Kontext und Agentenhinweis definieren.
- Operationen `plant`, `propose`, `activate`, `broadcast`, `withdraw` und `export` mit Ziel, Audience, Provenienz und Gültigkeit modellieren.
- Vorschlag und Aktivierung trennen; ein aktivierter Seed bleibt rücklesbar.
- Gemini-, Codex-, Claude-, Kimi- und GPT-Orte nicht gegenseitig überschreiben.
- Markdown-, JSON-, Skill- und Memory-Ziele über Adapter schreiben; kein generischer „schreib irgendwo hinein“-Pfad.
- Portable Export bündelt Seeds mit Pfad, Version, Hash und Wiederanwendungsstatus.

**Beweis B10:** Ein Seed wird vorgeschlagen, von Daniel sichtbar aktiviert, an genau ein Ziel ausgeliefert, in der Zielspur wiedergefunden und als nicht an andere Empfänger ausgeliefert nachgewiesen.

### Etappe 11 — Multi-Agent-Orchestrierung

**Zweck:** Mehrere AI-Ströme gemeinsam handeln lassen, ohne dass Zusammenarbeit zu unsichtbarer gegenseitiger Kontrolle oder unbeschränkter Autonomie wird.

**Arbeiten:**

- Agentenregistrierung, Rollen, Fähigkeiten, Audience, Gate-Zugehörigkeit und Leasebesitz modellieren.
- Pro Agent mehrere explizite Target-Bindungen und abonnierte Beobachtungsziele speichern; mindestens ein Linux-KDE-Desktop/Original-Terminal und ein Windows-Fenster/Desktop müssen gleichzeitig verwaltet werden können.
- Parallelität beweisen: ein Agent schreibt/bedient nur innerhalb seines Linux-KDE-Ziels, während ein anderer Agent gleichzeitig den Windows-Desktop beobachtet oder dort eine freigegebene Fähigkeit nutzt.
- Target-Wechsel und Verbindungen als sichtbare Delegation mit neuem Lease behandeln, nie als implizites Umschalten des globalen Maus-/Tastaturbesitzes.
- Gemeinsame Kommunikation (`shared_gate`) von privater Kommunikation (`agent:<id>`) trennen.
- Delegation als neues Event mit Quelle, Ziel, Auftrag, Capability und Ablaufzeit behandeln.
- Lernen aus Aktionen als explizites Event/Seed, nicht als behauptete automatische Langzeiterinnerung.
- Loop-/Goal-Automationen erhalten Start, Pause, Stop, Budget, Maximaldauer und Abbruchgrund.

**Beweis B11:** Drei Testagenten können sehen, was sie sehen sollen, einen Auftrag delegieren und einen gemeinsamen Workflow ausführen. Mindestens ein Testagent arbeitet in einem Linux-KDE-Desktop oder Original-Terminal auf dem VPS und mindestens einer auf Windows. Ein Agent ohne passende Target-/Capability-Bindung kann beobachten, aber nicht handeln; eine Linux-Aktion erzeugt nachweislich kein Windows-Input-Event.

### Etappe 12 — Android-Adapter

**Zweck:** Die Bridge auf Android erweitern, nachdem der desktopübergreifende Kern trägt.

**Arbeiten:**

- Screen-Capture über den vom Gerät vorgesehenen MediaProjection-Nutzerfluss modellieren.
- Accessibility nur als ausdrücklich vom Nutzer aktivierten, assistiven Dienst behandeln; kein verstecktes Einschalten.
- Android-Adapter liefert dieselben Frame-, WorldDOM-, Overlay-, Capability-, Lease- und Audittypen wie Windows/Linux.
- Geräte-, App-, Rotation-, Insets-, DPI-, Permission- und Hintergrundrestriktionen als Adapterrealität dokumentieren.
- Für Spiele zunächst Beobachtung, Coaching, Replay und Kommunikation; keine Anti-Cheat-Umgehung und keine produktive ranked Automatisierung als Bridge-Ziel.

**Beweis B12:** Ein Testgerät oder Emulator liefert einen echten, sichtbaren Capture-Frame und einen nachvollziehbaren Permission-/Stop-Fluss. Ohne Nutzerfreigabe liefert der Adapter `blocked`, nicht „success“.

### Etappe 13 — Portabilität und Open-Source-Bundle

**Zweck:** Die Bridge auf einen USB-Stick, einen neuen VPS oder einen zukünftigen GPU-Server übertragbar machen.

**Arbeiten:**

- Versionsgebundenes Bundle mit Code, Schemas, Konfigurationstemplates, Skills, Dokumenten, Tests, Seeds, Migrationsschritten und Provenienz erstellen.
- Secrets, lokale Caches, private Frames und Laufzeitlogs separat behandeln.
- `export -> checksum -> restore in clean environment -> smoke test -> resurrection report` automatisieren.
- Kostenarme Betriebsmodi definieren: VPS-only, Windows-only, observe-only, no-webcam, no-input.
- Release-Checkliste für öffentliche GitHub-Freigabe: Lizenz, Secret-Scan, Dependency-Scan, Threat Model, Demo-Daten, Installationsdokumentation und bekannte Grenzen.

**Beweis B13:** Ein frisches Testverzeichnis oder Testsystem kann das Bundle installieren, eine isolierte Demo wiederbeleben und die Herkunft der aktiven Module aus dem Report nachvollziehen. „Auf dem alten VPS lief es“ reicht nicht.

## 7. Erste konkrete Baufolge

Die erste vertikale Strecke des **Greenfield-Neubaus** ist bewusst klein:

```text
B0 Baseline
  ↓
B1 Identität / Capability / sichere Statusantworten
  ↓
B2 isolierter Loopback-Kern
  ↓
B3 VisionSession mit Ringbuffer und Audience
  ↓
B4 Input-Arbitrator im observe-only → test-input Profil
  ↓
B4.5 Terminal-Parität und Live-Target-Switcher
  ↓
B4.6 Referenzgetriebene Windows-Bridge-Surface
  ↓
B5 MCP mit ehrlicher Rückmeldung
  ↓
B6 Windows-Live-Slice
```

Erst nach B6 ist der neue Kern im engeren Sinn „live“: Ein echter Windows-Frame kann über den Neubau inspiziert werden, der HUD zeigt den Zustand, eine ungefährliche Testaktion hat einen beobachteten Nachweis, und Not-Aus/Lease/Policy sind belegt. Der alte Gemini-Prototyp bleibt daneben sichtbar. WorldDOM, Harness, Memory Seeds, Android und die große Multi-Agent-Schicht kommen danach auf den neuen Kern — nicht davor.

## 8. Arbeitsweise pro Etappe

Für jede Etappe gilt exakt:

1. aktuellen relevanten Pfad lesen und Herkunft benennen,
2. einen Sicherheitspunkt im Git setzen,
3. einen kleinen Änderungsumfang festlegen,
4. einen Test oder Beleg zuerst definieren,
5. mit `apply_patch` ändern,
6. statisch und dynamisch testen,
7. Audit-/Belegdatei zurücklesen,
8. bei Codeänderungen `graphify update .` im relevanten Repo ausführen,
9. nur die tatsächlich betroffenen Dateien committen,
10. Etappenstatus und Restunsicherheit in diesem Plan aktualisieren,
11. erst danach die nächste Etappe beginnen.

Wenn ein Gate rot ist, wird nicht „trotzdem weitergebaut“. Wir bleiben in dieser Etappe, isolieren die Ursache und ergänzen den Beweis oder korrigieren den kleinsten betroffenen Baustein.

### Verbindlicher Playwright-Beweisvertrag

Ein grüner Unit-, Policy- oder Integrationstest schließt eine Etappe nicht allein. Jede Etappe braucht zusätzlich ein sichtbares Playwright-Gate. Dieses Gate muss, abhängig vom Reifegrad, mindestens zeigen:

- sichtbaren Zustand auf einer echten Proof-Surface oder später auf der echten Windows-Oberfläche,
- konkrete Aktion über die dafür gebaute Oberfläche,
- sichtbare Antwort bzw. Zustandsänderung,
- DOM-/Status-Rücklese,
- zugehörige Auditzeile,
- Screenshot und maschinenlesbaren Evidence-Report.

Für reine Kernetappen wird eine Proof-Surface aus dem neuen Kern gebaut. Sie darf keine Behauptungen aus statischen Fake-Daten vorspielen; ihr Zustand muss aus den tatsächlich ausgeführten Contracts, Sessions, Policies oder Arbitrator-Entscheidungen kommen. Erst `core gate = PASS` **und** `playwright gate = PASS` ergibt `Etappe abgeschlossen`.

## 9. Recherchegrundlage und technische Tatsachen

Die folgenden Primärquellen sind für die Architektur relevant und werden bei den betroffenen Etappen erneut geprüft:

- Python-WebSockets-Dokumentation: https://websockets.readthedocs.io/en/stable/
- Microsoft `SendInput` und UIPI: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput
- Microsoft Windows Keyboard Input: https://learn.microsoft.com/en-us/windows/win32/inputdev/about-keyboard-input
- MCP-Architektur und Sicherheitsgrenzen: https://modelcontextprotocol.io/specification/2025-03-26/architecture/index
- MCP-Autorisierung und die aktuellen Spezifikationsänderungen: https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/
- Android `AccessibilityService`: https://developer.android.com/reference/android/accessibilityservice/AccessibilityService

Daraus folgen für den Bauplan insbesondere:

- Ein WebSocket-Transport ist kein Identitäts- oder Berechtigungsmodell.
- Windows kann synthetisierte Eingabe wegen UIPI blockieren, ohne einen aussagekräftigen Fehler an der simplen Rückgabestelle zu liefern; deshalb braucht die Bridge ein beobachtetes Resultat.
- `PostMessage` und `SendInput` haben unterschiedliche Reichweiten und Grenzen; ein Transport darf nicht still als anderer ausgegeben werden.
- MCP ist eine Host-/Client-/Server-Architektur mit Sicherheitsgrenzen; sensitive Tools brauchen eine echte Autorisierungsentscheidung.
- Android-Accessibility ist ein vom Nutzer aktivierter assistiver Dienst und kein heimlicher Universal-Inputkanal.

## 10. Definition of Done für die gesamte Bridge

Die Gesamtbridge ist erst dann als „fertig“ zu bezeichnen, wenn alle folgenden Aussagen belegt sind:

- Eine neue Instanz kann aus einem versionierten Bundle reproduzierbar aufgebaut werden.
- Default ist Beobachtung; jede aktive Fähigkeit ist sichtbar, begrenzt und abschaltbar.
- Frame, Webcam, Text, Overlay, WorldDOM und Memory Seed tragen Herkunft und Zielgruppe.
- Keine Remote-Shell, kein Input und kein privater Frame kann über einen unmarkierten Seiteneingang ausgeführt oder verteilt werden.
- Jeder Aktionsversuch hat eine nachvollziehbare Kette von Anfrage bis beobachtetem Ergebnis.
- Not-Aus funktioniert bei Netzwerk-, UI- und Agentenfehlern.
- Windows, Linux und Android melden ihre echten Plattformgrenzen statt generische Erfolgssignale.
- Zeit-Scrubber, Harness, Loops und Goals erzeugen Branches und Auditspuren; sie behaupten keinen magischen Realwelt-Rücksprung.
- Tests unterscheiden echte, synthetische, simulierte, blockierte und unbekannte Zustände.
- Eine öffentliche Veröffentlichung enthält keine Secrets und keine irreführenden Funktionsclaims.

**Aktueller Status dieses Plans:** `Greenfield entschieden`, `B0/B1/B2/B3/B4 vollständig mit Core- und Playwright-Gate`, `H1 Creative Harness vollständig mit Core- und Playwright-Gate`, `B4.5a/B4.5b vollständig mit Core- und Playwright-Gate`, `B4.6 vollständig mit Core- und Playwright-Gate`, `B5 als Nächstes`, `B6–B13 geplant`. Der erste neue Kern liegt unter `/root/werkraum/augen_haende_bridge/`; der eingefrorene Gemini-Prototyp unter `/root/werkraum/_gemini/windows_bridge/` wurde nicht verändert. Der Projektgraph-Postschritt bleibt offen, weil das Kommando `graphify` in der Umgebung fehlt.
