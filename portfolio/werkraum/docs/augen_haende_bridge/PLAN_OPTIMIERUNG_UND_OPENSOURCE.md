# Plan: Optimieren, Annehmen, Open-Source-reif machen

Nur Plan, nichts davon ist gebaut. Jede Phase endet mit Gates (Ledger-Stil, Beleg per Befehl). Etwas nach außen Wirksames (Repo, Upload, Veröffentlichung) geschieht erst nach Daniels ausdrücklichem Wort.

## Phase 0: Offene Funde aus der Recherche (klein, eindeutig, sofort baubar)
| Nr | Auftrag | Beleg |
|---|---|---|
| 0.1 | HTTP 400 des Modellservers als „kontext_zu_gross“ mit `n_prompt_tokens` und `n_ctx` melden (Chat und `beobachtung jetzt`) | Test mit Fake-Server, der 400 liefert |
| 0.2 | Test: Mehrbyte-Zeichen an Terminal-Stückgrenzen | Test mit „ä“ genau an der Grenze, Ausgabe lückenlos |
| 0.3 | Test: Reihenfolge der Nachrichten je Empfänger (FIFO) | Test mit 50 schnellen Nachrichten |
| 0.4 | Zweig aus Kapsel: Test für „startet erst nach frischer Messung“ | Test im Integrationsrahmen |
| 0.5 | Live-Probe gegen Chat-Server 11435 (nur auf Wunsch, Port 11436 nie) | `BRIDGE_LIVE_CHAT=1` |
| 0.6 | Altern von Abläufen erkennen (Knotenvergleich vor dem Start, Warnung statt Handlung) | Test mit verändertem Knoten |

## Phase 1: Belege, die nur nativ gehen (Daniel oder Testrechner)
Prüfliste 0.10.0: Hände, Fokus, Fensterbild, UIA, Controller unter Windows; Claude hinter dem Vertrauensdialog; Kimi, GLM. Bis dahin steht in der Außenwirkung „unter Windows nicht nativ geprüft“. Dazu Bauaufträge R2 (Windows.Graphics.Capture), R4 (XInput2-Erkennung).

## Phase 2: Entkoppeln
1. Starter-Konfiguration statt fester Pfade (`/root/werkraum`, `/vps_root`): Konfigdatei und Umgebungsvariablen.
2. VPS-Adresse und Token nur aus Konfiguration (Skripte und `.bat` ohne feste Adresse).
3. Hauhaucs, Codewesen, Flextrawurst als **optionale** Plug-ins; die Bridge startet ohne sie.
4. Sprachen: Nachrichten des Werkzeugs und der Oberfläche über Übersetzungstabelle (Deutsch, Englisch), wie im Flextrawurst-i18n-Muster.
Gate: Bridge startet auf einer frischen Maschine ohne `/root/werkraum`.

## Phase 3: Sauberer Export
1. Neues Repo-Verzeichnis außerhalb des Monorepos; Historie nur der Bridge (z. B. mit `git filter-repo` auf diesen Unterordner) **oder** Neustart mit einem Anfangs-Commit — Entscheidung für Daniel (Historie behalten heißt Geheimnis-Scan der ganzen Historie).
2. `dist/` und große Binärdateien raus aus der Historie; Pakete nur als Release.
3. Geheimnis-Scan (gitleaks) über Historie und Arbeitsbaum.
4. `LICENSE` (Daniel wählt), `NOTICE`, Drittanbieter-Lizenzliste (Pillow, pyte, websockets, sounddevice, OpenCV …; die Lizenz von evdev und vgamepad prüfen).
5. `SECURITY.md` mit Bedrohungsmodell (Lease, Käfig, Not-Aus, was die Bridge nie tut), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
Gate: Scan ohne Fund; `LICENSE` vorhanden; Export baut und besteht die Tests.

## Phase 4: Installer und Schnellstart
1. Windows-Setup (Inno Setup oder MSIX), signiert, ohne Treiber-Installation; Controller-Treiber nur als eigener, ausdrücklicher Schritt (alternativ treiberfreier Weg, Entscheidung für Daniel).
2. `pip install` plus `bridge init` und `bridge start` für den Starter; Container-Datei für den Relay.
3. Selbsttest-Befehl, der in einer Minute sagt, was geht und was nicht.
4. Reproduzierbarer Bau: Skript und Versionssperre; PyInstaller-Bootloader prüfen (Virenmeldungen).
Gate: Eine fremde Person installiert auf einem frischen Windows und startet einen Agenten in unter fünf Minuten.

## Phase 5: Außenauftritt
Englisches README mit Demo-GIF (drei Agenten, F12), Architekturbild, Vergleichstabelle zu verwandten Werkzeugen (ehrlich), Fehlersuche, Roadmap, Issue-Vorlagen, CI (Tests auf Linux, Build auf Windows), Release-Notizen. Veröffentlichung erst nach Phase 1 bis 4 und Daniels Wort.

## Phase 6: Weiterentwicklung (Auswahl aus der Recherche, mit Daniels Entscheidung)
Set-of-Mark-Bild für den WorldDOM; Wiedergabe einer Kapsel mit aufgezeichneten Modellantworten; Auswahl und Verfeinerung gespeicherter Abläufe; Dateisperren oder Worktrees als Angebot an Agenten; Android (Hürde: eingeschränkte Einstellungen); Mikrofon (nach Klärung des stillen Geräts); Wayland-Körper; Chat mit Entitäten, Zensi und Handy (Speicherort vorher gemeinsam entscheiden).

## Entscheidungen, die Daniel treffen muss
Lizenz (MIT oder Apache-2.0); Historie behalten oder neu anfangen; Produktname (ohne Fremdmarken); Signatur (Zertifikat kaufen) und Weg bei Controller-Treibern; Dateisperren und Worktrees anbieten oder nicht; Reihenfolge der Phase 6.

## Warum dieser Aufbau
Er folgt den Befunden aus `SOKRATES_BRIDGE.md`: Vertrauen kommt vor Reichweite, Belege vor Behauptungen, Entkoppeln vor Export, Export vor Veröffentlichen.

## Daniels Entscheidungen (2026-10-02)
- **Lizenz:** „die Standard-Open-Source-Lizenz“. Empfehlung: **Apache-2.0** (erlaubt alles Übliche, schützt zusätzlich vor Patentklagen; bei MIT fehlt dieser Patentschutz). Gesetzt wird sie erst beim Export.
- **Historie:** Die Arbeit hier geht unverändert weiter und behält alles. Für die Öffentlichkeit gilt als Vorschlag: ein **neues, sauberes Repo mit demselben Code** und frischer Commit-Spur, weil die jetzige Spur im privaten Monorepo mit Privatem vermischt ist. Nichts geht verloren, alles Private bleibt hier.
- **Reihenfolge:** erst die Bridge so weiterbauen und vervollständigen wie bisher (Phase 0 und 1), dann entkoppeln und exportieren.
- **Ausrichtung nach außen:** nicht „ein Werkzeug“, sondern die lokale, modellunabhängige Mehr-Agenten-Bedienung: Terminals unten, pro Agent eine Raute, jeder Agent in seinem eigenen Fenster oder Programm (Browser, Blender, Spiele, Dateien), Mensch hat Vorrang und Not-Aus, mehrere Bildschirme, Windows und Linux zugleich, auch auf einem VPS mit virtuellem Desktop. Ob große Anbieter Vergleichbares schwach umgesetzt haben, ist eine Behauptung, die ich erst durch eigene Recherche belegen muss (Aufgabe für Phase 5: Vergleichstabelle mit Belegen).
