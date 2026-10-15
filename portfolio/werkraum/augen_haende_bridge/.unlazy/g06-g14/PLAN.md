# Plan: Augen-und-Hände-Bridge G06, G06.7, G09 bis G14 vollständig bauen

Scope: g06-g14
Depth: tree 3
Mode: orchestrated

## Contract

Auftrag (Daniel, 2026-10-02): „bau mal jetzt bis goal14 komplett durch und wir prüfen erst anschließend“. ChatGPT (G06.5) und Mikrofon sind von Daniel auf später verschoben. Dazu: „nutze mal den skill unlazy“ und „lies auch mal wieder die skills und harness zur bridge“ (beide Bridge-Skills sind gelesen; ihr Etappenzyklus gilt: Sicherheitspunkt, Bau, Tests, Evidence, Bauprotokoll, Commit).

- Interfaces: bestehender Körper unter `src/augen_haende_bridge/koerper/`, Relay `client_vps/bridge_server.py`, Launcher `client_vps/terminal_launcher.py`, Creative-Harness `src/augen_haende_bridge/harness.py`, Verträge `contracts.py`, `arbitrator.py`, `policy.py`, `vision.py`. Neue Module bekommen deutsche Namen im Körper-Stil, plattformneutrale Logik getrennt von Win32/X11.
- Ownership: je Leaf eigene neue Dateien und eigene Tests (siehe Tabelle); gemeinsame Dateien (`anwendung.py`, `haupt.py`, `transport.py`, `bridge_server.py`) werden nur von dem Leaf angefasst, das sie in `Owns` hat, sonst als Abhängigkeit geordnet.
- Dependencies: nach Goal-Abhängigkeiten aus `PLAN.md` (docs): G06 vor G06.7 und G10; G09 vor G10 und G13; G10 vor G11; G11 vor G12; G09/G08 vor G13; G13 vor G14.
- Host launch mode: sequential fallback (der Fahrer baut jedes Leaf selbst; keine Unteragenten: die Leaves teilen Dateien und Kontext, und Daniel hat keine verlangt).
- Wave policy: eine Welle je Leaf, strikt nacheinander.
- Toolchain: Linux-VPS mit Python 3.12 (Tests: `PYTHONPATH=src:tests:client_vps python3 -m unittest <modul>`), Windows-Python 3.13 unter Wine 10 + Xvfb für Windows-Proben, GTK 3 (gi) unter eigenem Xvfb für Linux-Proben. Shell /bin/sh, Arbeitsverzeichnis `/vps_root/werkraum/augen_haende_bridge`.
- Conventions: Deutsch in Namen und Texten; Plattformbelege getrennt von Unit-Tests; „nativ bei Daniel offen“ ist ein eigenes manuelles Gate, nie ein grünes; kein Treiber (ViGEm, virtueller Monitor) wird ohne Daniels Wort installiert; keine <1-ms-Behauptungen ohne Messung; accepted, delivered, observed, audited getrennt.
- Manual review: Daniel prüft alles Native nach der Lieferung (Prüfliste je Version). Bis dahin bleiben diese Gates ausdrücklich unerfüllt und stehen im Abschlussbericht als Übergabe.

## Current contract inventory

Contract revision: 1.

| ID | Required outcome or constraint | Owner | Observing gate or manual review | Disposition | Revision |
|---|---|---|---|---|---|
| C1 | G06.5 (ChatGPT) und Mikrofon nativ sind verschoben | Daniel | Erklärung vom 2026-10-02 | DEFERRED | 1 |
| C2 | G06: das Overlay erscheint auf KDE 1 und KDE 2; Anzeigeort und Arbeitsziel sind unabhängig wählbar | node-1.1 | node-1.1:N3 | ACTIVE | 1 |
| C3 | G06: Windows-Ansicht und Linux-Ansicht haben dasselbe Aussehen und Verhalten (Daniel: 1:1) | leaf-1.1.1 | leaf-1.1.1:G2 | ACTIVE | 1 |
| C4 | G06: Bindung gemeinsam oder getrennt; ein geschlossenes oder ersetztes Fenster bindet nie still ein anderes | leaf-1.1.3 | leaf-1.1.3:G3 | ACTIVE | 1 |
| C5 | G06: die Oberfläche zeigt Host, Arbeitsplatz, Session und Ziel getrennt; inaktive, minimierte, verdeckte Ziele tragen eine sichtbare Capability | leaf-1.1.3 | leaf-1.1.3:G4 | ACTIVE | 1 |
| C6 | G06.7: zwei Fenster nebeneinander, eines teilweise verdeckt: jeder Agent bekommt das ganze Bild seines Fensters ohne fremde Pixel; leere oder schwarze Aufnahme fällt sichtbar zurück | node-1.2 | node-1.2:N3 | ACTIVE | 1 |
| C7 | G06.7: Browser über CDP, normale Programme über UI Automation lesen und bedienen, mit Aussage zu klein, verdeckt, minimiert | leaf-1.2.2 | leaf-1.2.2:G1 | ACTIVE | 1 |
| C8 | G09: mehrere Sessions desselben Modells, verschiedene Agenten und ein unterstützter Subagent bleiben richtig zugeordnet; Neu starten und Anbinden sind getrennte Aktionen; Gruppen, Delegation, Beobachten, Pause, Beenden | node-1.3 | node-1.3:N3 | ACTIVE | 1 |
| C9 | G09: jeder gewünschte Adapterweg (Codex, Gemini, Claude, Kimi, Opencode) ist real geprüft oder als offen benannt | leaf-1.3.2 | leaf-1.3.2:G1 | ACTIVE | 1 |
| C10 | G10: Klicken, Tippen, Ziehen, Hotkeys mit echtem Ergebnis; Hintergrund- und Shared-Mouse-Modus unterscheidbar; Zielprüfung statt Listenindex | node-1.4 | node-1.4:N3 | ACTIVE | 1 |
| C11 | G10: F12 und lokaler Stop wirken trotz Verbindungsabbruch und UI-Hänger; nach Abbruch keine hängenden Tasten; Daniels Override und Ausnahme behalten den Not-Aus | leaf-1.4.3 | leaf-1.4.3:G1 | ACTIVE | 1 |
| C12 | G10: Negativtests (falsches Ziel, DPI- und Fokuswechsel, alte Frames, abgelaufene Leases, fehlende Rechte); virtuelle Controller als Adapter mit sichtbarer Grenze (kein Treiber ohne Daniels Wort) | leaf-1.4.2 | leaf-1.4.2:G2 | ACTIVE | 1 |
| C13 | G11: echter DOM- oder Accessibility-Knoten, aus dem Bild erschlossener Knoten und Anker mit Herkunft, Confidence, Aktualität; unauflösbarer Knoten löst keine erfundene Aktion aus | node-1.5 | node-1.5:N3 | ACTIVE | 1 |
| C14 | G11: Overlay-Zeigegeste und tatsächliche Einfügung haben getrennte Wege; veraltete Zeigegeste warnt statt zu klicken | leaf-1.5.3 | leaf-1.5.3:G1 | ACTIVE | 1 |
| C15 | G12: ein Agent entwirft, speichert, führt einen Ablauf aus, wählt bei Abweichung Fallback, übergibt Teilauftrag; Daniel kann starten, pausieren, fortsetzen, abbrechen, Zweig wählen; neuer Ablauf ohne neuen Build | node-1.6 | node-1.6:N3 | ACTIVE | 1 |
| C16 | G12: Modi Free, Shadow, Witness, Daniel-Gate, Learning einzeln kombinierbar (Lernen anfangs aus); Regiesprüche mit echter Wirkung oder ehrlich als Gesprächsanweisung | leaf-1.6.2 | leaf-1.6.2:G1 | ACTIVE | 1 |
| C17 | G13: Momentkapseln und Zeit-Scrubber; Fehlerverlauf speichern, öffnen, vergleichen, kommentieren; neuer Zweig ab altem Punkt; beim Scrubben keine versteckte Eingabe | node-1.7 | node-1.7:N3 | ACTIVE | 1 |
| C18 | G14: Hauhaucs liest drei Agenten mit; Aufzeichnen, Zustellen, Verarbeiten getrennt; Stop und Budget wirken; „Jetzt dokumentieren“ mit Quellenbezug | node-1.8 | node-1.8:N3 | ACTIVE | 1 |
| C19 | G14: leere neue Session ist wirklich leer; Kontextmischpult (Auswahl, Bearbeiten, Leeren, Halbieren, Zurückspringen, Einspeisung, Import/Export) bleibt nach Neuladen exakt | leaf-1.8.2 | leaf-1.8.2:G1 | ACTIVE | 1 |
| C20 | Alles Native (Daniels Windows, KDE-Desktops) ist nur durch Daniel belegbar; bis dahin als Übergabe ausgewiesen | Daniel | node-1.9:N1 | ACTIVE | 1 |

## State vocabulary

Leaf state is exactly one of: WAITING, READY, IN-FLIGHT, VERIFIED, ABANDONED. Branch state is exactly one of OPEN, VERIFIED, ABANDONED.

## Tree

- 1 G06 bis G14 .............. GATES.md
  - 1.1 G06 Plattform und Anzeigeort ........ gates/node-1.1.md
    - 1.1.1 Linux-Fensterbackend ............ gates/leaf-1.1.1.md
    - 1.1.2 Linux-Adapter (Aufnahme, Scanner, Eingabe) ... gates/leaf-1.1.2.md
    - 1.1.3 Relay-Routing und Anzeigeort .... gates/leaf-1.1.3.md
    - 1.1.4 Linux-Körper starten ............ gates/leaf-1.1.4.md
  - 1.2 G06.7 Fensteraufnahme je Agent ...... gates/node-1.2.md
    - 1.2.1 Fensteraufnahme und Rückfall .... gates/leaf-1.2.1.md
    - 1.2.2 Browser über CDP ................ gates/leaf-1.2.2.md
    - 1.2.3 UI Automation ................... gates/leaf-1.2.3.md
  - 1.3 G09 Multi-Agent ..................... gates/node-1.3.md
    - 1.3.1 Register, Gruppen, Delegation .... gates/leaf-1.3.1.md
    - 1.3.2 Adapterwege je Strom ............. gates/leaf-1.3.2.md
  - 1.4 G10 Hände ............................ gates/node-1.4.md
    - 1.4.1 Eingabeadapter Windows und Linux . gates/leaf-1.4.1.md
    - 1.4.2 Steuerprofile, Leases, Controller . gates/leaf-1.4.2.md
    - 1.4.3 Not-Aus und hängende Tasten ..... gates/leaf-1.4.3.md
  - 1.5 G11 WorldDOM ........................ gates/node-1.5.md
    - 1.5.1 Knoten- und Ankermodell ......... gates/leaf-1.5.1.md
    - 1.5.2 Auflösen, Ausführen, Rücklesen .. gates/leaf-1.5.2.md
    - 1.5.3 Zeigegeste und Einfügung ........ gates/leaf-1.5.3.md
  - 1.6 G12 Workflows ........................ gates/node-1.6.md
    - 1.6.1 Ablaufsprache und Durchläufe .... gates/leaf-1.6.1.md
    - 1.6.2 Modi und Delegation ............. gates/leaf-1.6.2.md
    - 1.6.3 Regiesprüche mit Wirkung ........ gates/leaf-1.6.3.md
  - 1.7 G13 Momente ........................... gates/node-1.7.md
    - 1.7.1 Kapseln ......................... gates/leaf-1.7.1.md
    - 1.7.2 Scrubber ........................ gates/leaf-1.7.2.md
  - 1.8 G14 Hauhaucs ........................... gates/node-1.8.md
    - 1.8.1 Anbindung und Mitlesen .......... gates/leaf-1.8.1.md
    - 1.8.2 Kontextmischpult ................ gates/leaf-1.8.2.md
  - 1.9 Übergabe an Daniel ..................... gates/node-1.9.md

## Leaf dispatch table

| Leaf | Owns | Needs | Tier | Planned wave | State |
|---|---|---|---|---|---|
| 1.1.1 | src/augen_haende_bridge/koerper/fenster_linux.py, src/augen_haende_bridge/koerper/plattform.py, src/augen_haende_bridge/koerper/win32_linux.py, src/augen_haende_bridge/koerper/menue_linux.py, src/augen_haende_bridge/koerper/x11_helfer.py, src/augen_haende_bridge/koerper/tasten_x11.py, tests/test_koerper_fenster_linux.py, probes/linux_fenster_smoketest.py, probes/linux_koerper_zeichnen.py | - | judgment | 1 | READY |
| 1.1.2 | src/augen_haende_bridge/koerper/linux_adapter.py, tests/test_koerper_linux_adapter.py | 1.1.1 | judgment | 2 | WAITING |
| 1.1.3 | src/augen_haende_bridge/koerper/anzeigeort.py, tests/test_anzeigeort.py, tests/test_bridge_server_anzeigeort.py | 1.1.2 | judgment | 3 | WAITING |
| 1.1.4 | src/augen_haende_bridge/koerper/haupt_linux.py, client_vps/koerper_linux_starten.sh, tests/test_koerper_haupt_linux.py | 1.1.3 | judgment | 4 | WAITING |
| 1.2.1 | src/augen_haende_bridge/koerper/fensteraufnahme.py, tests/test_koerper_fensteraufnahme.py | 1.1.4 | judgment | 5 | WAITING |
| 1.2.2 | src/augen_haende_bridge/koerper/cdp.py, tests/test_koerper_cdp.py | 1.2.1 | judgment | 6 | WAITING |
| 1.2.3 | src/augen_haende_bridge/koerper/uia.py, tests/test_koerper_uia.py | 1.2.1 | judgment | 6 | WAITING |
| 1.3.1 | src/augen_haende_bridge/koerper/agentenregister.py, tests/test_koerper_agentenregister.py | 1.1.4 | judgment | 5 | WAITING |
| 1.3.2 | src/augen_haende_bridge/adapterwege.py, tests/test_adapterwege.py | 1.3.1 | judgment | 6 | WAITING |
| 1.4.1 | src/augen_haende_bridge/koerper/eingabe_adapter.py, tests/test_koerper_eingabe_adapter.py | 1.3.1, 1.2.1 | judgment | 7 | WAITING |
| 1.4.2 | src/augen_haende_bridge/koerper/steuerprofile.py, tests/test_koerper_steuerprofile.py | 1.4.1 | judgment | 8 | WAITING |
| 1.4.3 | src/augen_haende_bridge/koerper/notaus_kern.py, tests/test_koerper_notaus_kern.py | 1.4.1 | judgment | 8 | WAITING |
| 1.5.1 | src/augen_haende_bridge/koerper/weltdom.py, tests/test_koerper_weltdom.py | 1.2.2, 1.2.3 | judgment | 9 | WAITING |
| 1.5.2 | src/augen_haende_bridge/koerper/weltdom_aktion.py, tests/test_koerper_weltdom_aktion.py | 1.5.1, 1.4.2 | judgment | 10 | WAITING |
| 1.5.3 | src/augen_haende_bridge/koerper/zeigegeste.py, tests/test_koerper_zeigegeste.py | 1.5.2 | judgment | 11 | WAITING |
| 1.6.1 | src/augen_haende_bridge/ablauf.py, tests/test_ablauf.py | 1.5.2 | judgment | 11 | WAITING |
| 1.6.2 | src/augen_haende_bridge/ablauf_modi.py, tests/test_ablauf_modi.py | 1.6.1, 1.3.1 | judgment | 12 | WAITING |
| 1.6.3 | src/augen_haende_bridge/koerper/regiespruch_wirkung.py, tests/test_regiespruch_wirkung.py | 1.6.2 | judgment | 13 | WAITING |
| 1.7.1 | src/augen_haende_bridge/kapseln.py, tests/test_kapseln.py | 1.6.1, 1.3.1 | judgment | 12 | WAITING |
| 1.7.2 | src/augen_haende_bridge/koerper/scrubber.py, tests/test_koerper_scrubber.py | 1.7.1 | judgment | 13 | WAITING |
| 1.8.1 | src/augen_haende_bridge/hauhaucs.py, tests/test_hauhaucs.py | 1.7.1 | judgment | 14 | WAITING |
| 1.8.2 | src/augen_haende_bridge/kontextmischpult.py, tests/test_kontextmischpult.py | 1.8.1 | judgment | 15 | WAITING |

## Status log

Ereignisse stehen in `.unlazy/g06-g14/status.log` (append-only, per `gate-check --scope g06-g14 --log`).
