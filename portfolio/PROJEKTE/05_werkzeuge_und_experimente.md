# 05 · Werkzeuge und Experimente / Tools and experiments

Deutsch zuerst, English below each project. Quellen: Systemdoku (Nummer in Klammern) und die genannten Ordner.
German first, English below each project. Sources: system docs (number in brackets) and the folders named.
„Warum“ nur, wo die Quelle es sagt. Sonst **(Daniel ergänzt)**. / "Why" only where the source says it. Otherwise **(Daniel adds)**.

---

## Toolbox: TTS, Soundboard, Diktat, Übersetzen, OCR, Dokumente, Webarchiv, Datei-Wandler (Doku 22; Ordner `datei_wandler/`)

**Versucht / Tried.** Eine einzige Seite mit acht Werkzeug-Tabs und gemeinsamem Textkreislauf zwischen allen: Sprachausgabe, Soundboard, Diktat, Übersetzung, Texterkennung, Dokumente, Webarchiv, Datei-Wandler.
A single page with eight tool tabs and a shared text circulation between them: speech output, soundboard, dictation, translation, text recognition, documents, web archive, file converter.

**Warum / Why.** Aus einer TTS-Seite gewachsen, die den Namen längst nicht mehr trug. Die Seite wurde am 2026-08-13 umbenannt; der interne Dienstname blieb bewusst unverändert. Der Datei-Wandler war zuerst ein eigener Dienst und zog am 2026-07-10 auf Daniels Wunsch als Tab ein, mit gleichem Backend und mechanisch umbenannten Element-IDs.
Grown from a TTS page whose name no longer fitted. The page was renamed on 2026-08-13; the internal service name deliberately stayed. The file converter was first its own service and moved in as a tab on 2026-07-10 at Daniel's wish, with the same backend and mechanically renamed element IDs.

**Was liegt drin / What is inside.** Das Frontend ist eine einzelne HTML-Datei, die bei jedem Aufruf frisch gelesen wird. `werkraum/datei_wandler/`: VPS-Pfade oder hochgeladene Dateien als Offline-HTML (mit Suche, Ordnerbaum, Verschieben) oder Markdown oder ZIP exportieren; Inhalte werden maskiert und nicht ausgeführt; große Mengen in kleinen Paketen. Ein lokales Diktat-Werkzeug liegt unter `werkraum/uploads/windows_diktat.py` („lokale, kostenlose Sprache-zu-Text-Eingabe für jedes Fenster“).
The frontend is a single HTML file that is read fresh on every request. `datei_wandler/`: export VPS paths or uploaded files as offline HTML (with search, folder tree, reordering), Markdown or ZIP; contents are escaped and not executed; large volumes in small packets. A local dictation tool lies in `uploads/windows_diktat.py`.

---

## Dolphin-Mischpult (Ordner `dolphin_mischpult/`)

**Versucht / Tried.** Ein live steuerbares Chat-Interface für lokale LLMs. Statt eines starren System-Prompt-Feldes ein „Mischpult“: mehrere Felder, die sich zu einem Gesamtprompt zusammensetzen und sich jederzeit anpassen lassen, während das Gespräch läuft.
A live controllable chat interface for local LLMs. Instead of a rigid system prompt field a "mixing desk": several fields that compose into one overall prompt and can be adjusted at any time while the conversation runs.

**Was liegt drin / What is inside.** `KONZEPT.md` (Stand 2026-06-24): Aufbau aus Basis, Overlay-Tags und Feedback-Modell, Antwort als Stream zurück, Modellauswahl per Dropdown. Laut Konzept ist es der „Blueprint“, dieselbe Architektur sollte später auf kleinere Modelle und Zensi übertragen werden. Die Admin-Absicherung dieser Route ist in Gruppe 01 beschrieben.
`KONZEPT.md` (as of 2026-06-24): built from base, overlay tags and feedback model, answer streamed back, model chosen per dropdown. According to the concept it is the "blueprint"; the same architecture was to be transferred later to smaller models and Zensi.

---

## 3D-Pipeline und 3D-MCP (Doku 34)

**Versucht / Tried.** Bildschirmlose 3D-Verarbeitung auf dem Server: Formate umwandeln (FBX/OBJ/STL nach GLTF/GLB), Studio-Renderings erzeugen, Szenen validieren. Erreichbar für Menschen, ChatGPT und Gemini über ein MCP-Protokoll und eine OpenAPI-Beschreibung.
Headless 3D processing on the server: convert formats, produce studio renderings, validate scenes. Reachable for humans, ChatGPT and Gemini via an MCP protocol and an OpenAPI description.

**Was liegt drin / What is inside.** Blender 4.0.2 headless und Godot 4.3 headless hinter einem eigenen MCP-/REST-Server (Autor der Doku: Gemini, 2026-07-23, Status „produktiv und verifiziert“). Code: `werkraum/tools/3d_pipeline/` (`blender_pipeline.py`, `godot_pipeline.py`, `flextrawurst_3d_mcp.py`, Test). Berichte zur Arbeit mit Blender: `werkraum/_claude/berichte/blender/` (`GESAMTERFAHRUNG_BLENDER.md` und Ordner zu einzelnen Testobjekten).
Blender 4.0.2 headless and Godot 4.3 headless behind their own MCP/REST server (doc author: Gemini, 2026-07-23, status "productive and verified").

---

## Weltenkosmos: Mega-Sammelauftrag und Städte (Doku 35, 36, 37)

**Versucht / Tried.** Das Fundament einer 3D-Spielwelt sammeln und prüfen: 29 Kapitel, darunter Geodaten für Schwelm, 13 Metropolen, 13 historische Festungsstädte, Untergrund, Waffen- und Fahrzeugfamilien, Biome, Skillbäume, Quests. Jedes Fundstück mit 50 festgelegten Metadatenfeldern erfasst, durch die 3D-Pipeline geprüft und im Archiv abgelegt. Dazu eine Pipeline mit vier Generationen von Hilfsagenten und ein achtfacher Prüfschleifen-Durchlauf.
Collect and check the foundation of a 3D game world: 29 chapters, including geodata for Schwelm, 13 metropolises, 13 historic fortress cities, underground, weapon and vehicle families, biomes, skill trees, quests. Each find captured with 50 fixed metadata fields, checked through the 3D pipeline and archived. Plus a four-generation pipeline of helper agents and an eightfold review loop.

**Stand / State.** Doku 37 (2026-07-23): Die Städtelisten haben einen kanonischen Kern aus der Lore-Verfassung und eine von Daniel freigegebene Erweiterungswelle („mehr ist besser“); Generation 1 lief damals. Ordner `werkraum/gemgems-spielbeobachtung/` enthält die Spielwerkstatt-Phasen und die Möllenkotten-Forschung (siehe Karte `INHALT_ORT_FUER_ORT.md`).
Doc 37 (2026-07-23): the city lists have a canonical core from the lore constitution and an extension wave approved by Daniel; generation 1 was running at the time.

---

## VPS-MCP-Werkzeugkörper (Doku 38; Ordner `werkraum/tools/vps_mcp/`)

**Versucht / Tried.** Ein MCP-Server, der den Server für einen KI-Assistenten (zuerst ChatGPT) zugänglich macht: Dateien lesen, Git-Provenienz, Dienststatus, Datenbank-Abfragen nur lesend, Suche.
An MCP server that makes the server accessible to an AI assistant (first ChatGPT): read files, git provenance, service status, read-only database queries, search.

**Warum / Why.** Daniel: „chatgpt ist teil des schiffes teil der crew“. Eine sehr umfangreiche Spezifikation von einer anderen KI-Instanz wurde bewusst nicht in einem Schritt gebaut, sondern in Stufen, jede einzeln verifiziert.
Daniel: "ChatGPT is part of the ship, part of the crew". A very extensive specification from another AI instance was deliberately not built in one step but in stages, each verified separately.

**Sicherheit von Anfang an / Security from the start.** Dateizugriff nur unter erlaubten Wurzeln; geheimnisverdächtige Namen (Schlüsseldateien, Zugangsdaten, alles mit „password“ oder „secret“) werden auch innerhalb erlaubter Wurzeln ausgeschlossen; Dienst-Befehle nur lesend; große Dateien über befristete Download-Links statt Base64 im Chat.
File access only under allowed roots; names that look secret are excluded even inside allowed roots; service commands read-only; large files via time-limited download links instead of Base64 in chat.

**Was liegt drin / What is inside.** `werkraum/tools/vps_mcp/`: `vps_mcp_server.py`, Atlas-Module (`mcp_atlas*.py`), Graph-Module für Arbeitsablauf und Auslieferung, `POSITIVE_HARNESSING_PRINCIPLE.md`, Tests. / the server file, atlas modules, graph modules for workflow and delivery, a principle document, tests.

**Spätere Arbeit / Later work.** Arbeitsweise (Leser und Schreiber getrennt), Muster, offene Fragen und Briefe in `werkraum/_gpt/mcp_zuhause/`. / Working method (readers and writers separated), patterns, open questions and letters in `werkraum/_gpt/mcp_zuhause/`.

---

## Augen und Hände: die Desktop-Brücke (Doku 76, 77, 78; Ordner `augen_haende_bridge/`)

**Versucht / Tried.** Eine sichtbare, modulare und wiederaufnehmbare Verbindung zwischen Linux-Server, Windows-Desktop und später Android: Bilder, Bildschirm- und Webcam-Frames, Texte, Fenster-Strukturen, Eingaben, damit AI-Ströme „sehen“ und „handeln“ können.
A visible, modular and resumable connection between Linux server, Windows desktop and later Android: images, screen and webcam frames, texts, window structures, inputs, so that AI streams can "see" and "act".

**Wer / Who.** Erste Fassung und Vision von Gemini (Doku 76, 2026-09-18). Erweiterungsschicht (WorldDOM, Memory Seeds, Wiedererweckung) und Geltungskorrektur von Codex (Doku 77, 2026-09-19); verbindlicher Bauplan mit Etappen und Beweistoren (Doku 78). Der Gemini-Prototyp wurde am 2026-09-20 auf ausdrücklichen Auftrag entfernt und ist nur in der Git-Historie nachvollziehbar.
First version and vision by Gemini. Extension layer and a validity correction by Codex; binding build plan with stages and proof gates. The Gemini prototype was removed on 2026-09-20 at explicit order and is traceable only in the git history.

**Stand / State.** Laut README: Stufen B0 bis B3 abgeschlossen (Domänenvertrag, fail-closed Policy, In-Memory-Kern, Sitzung und Sichtbarkeit). Ausdrücklich festgehalten: B4.6 ist nur als Browser-Mechanik geprüft, nicht als natives Produkt abgenommen; es gibt kein nachgewiesen ausgeliefertes Windows-Paket mit vollständigem Rückkanal.
According to the README: stages B0 to B3 completed. Explicitly recorded: B4.6 is only checked as browser mechanics, not accepted as a native product; there is no proven delivered Windows package with a complete return channel.

**Was liegt drin / What is inside.** `werkraum/augen_haende_bridge/` (442 Dateien), `werkraum/docs/augen_haende_bridge/` (68), `werkraum/_codex/augen-und-haende-bridge-2026-09-19/`.

---

## Desktop-Sichtbarkeit für ChatGPT (Ordner `Programm harness+observingcontroller/`, `_gpt/desktopsichtbarkeit/`)

**Versucht / Tried.** Einen Weg finden, damit ChatGPT den echten virtuellen Desktop sieht, nicht nur ein Hintergrundbild und nicht ein Browser im Browser.
Find a way for ChatGPT to see the real virtual desktop, not just a wallpaper and not a browser inside a browser.

**Was liegt drin / What is inside.** Die README (Stand 2026-09-19) beschreibt den bestätigten Standardweg: Desktop über den Fenstermanager anzeigen, dann den Live-Stream des Desktops per WebSocket abgreifen und Video starten. Dazu Agentenpapiere (`Agentpapers/`) mit einer vertieften Analyse vom 2026-10-07 und ihrer Lese- und Beleggrenze.
The README (as of 2026-09-19) describes the confirmed standard route: show the desktop through the window manager, then tap the live stream of the desktop via WebSocket and start video. Plus agent papers with a deepened analysis of 2026-10-07 and its reading and evidence limits.

---

## AI-Strom-Brücke (Doku `ai-strom-bruecke`; Ordner `_shared/ai_strom_bruecke/`, `ai_strom_bruecke/`)

**Versucht / Tried.** Externe AI-Ströme mit dem virtuellen Desktop verbinden, ohne sie zu Bewohnern oder versteckten Dauerprozessen zu machen. Ein Sprachtrigger („AI-Strom-Brücke“) verweist auf den gemeinsamen Vertrag.
Connect external AI streams with the virtual desktop without making them residents or hidden permanent processes. A language trigger refers to the shared contract.

**Wie / How.** Angenommene Eingaben werden als Ereignisse an einen Socket gespiegelt; ein Sammler schreibt sie nur anhängend in eine Ereignisdatei und hält einen Zustand aktuell. Beobachtung, Ereignisstrom, Steuerrecht und optionales Terminal sind getrennte Fähigkeiten. Entstehungsdoku `ai_strom_bruecke/DOKUMENTATION.md`: 26.–27. Juli 2026.
Accepted inputs are mirrored as events to a socket; a collector only appends them to an event file and keeps a state current. Observation, event stream, control lease and optional terminal are separate abilities.

---

## Video-as-Code (Doku 64, 65; Ordner `_gemini/musikvideoprojekt/`)

**Versucht / Tried.** Musikvideos als Code erzeugen: ein autonomer Durchlauf für ein ganzes Lied, eine Warteschlange für mehrere Lieder hintereinander und ein abschließender Voll-Audit.
Produce music videos as code: an autonomous run for a whole song, a queue for several songs in a row and a final full audit.

**Was liegt drin / What is inside.** Doku 64 (2026-09-04, Gemini): nach der Premiere eines 5:31-Minuten-Videos (1080×1920, 60 FPS, 404 MB) wurden diese Betriebsmodi ergänzt, dazu ein striktes Verbot von Hilfsagenten in dieser Pipeline. Doku 65: eine „kreative Video-Block-Harness“ mit 77/33-Klima und autonomer Wildcard-Erzeugung, entstanden aus einem Dialog über die Frage, wie eine Harness kreativ befreit statt abstumpft. Der Projektordner `_gemini/musikvideoprojekt/` hat die Unterordner `lieder/` und `work/` (180 Dateien).
Doc 64 (2026-09-04, Gemini): after the premiere of a 5:31 video these operating modes were added, plus a strict ban on helper agents in this pipeline. Doc 65: a "creative video block harness".

---

## Virtuelle Desktops (Doku 03, 45, 77)

**Was ist es / What it is.** Zwei freie Test-Desktops im Container: einer mit XFCE, einer mit KDE (laut Doku 03 auf lokalen Ports, von außen über je einen Pfad erreichbar).
Two free test desktops in containers: one with XFCE, one with KDE.

**Was in den Dokus steht / What the docs say.** Doku 45 (2026-07-31): Chromium ließ sich im zweiten Desktop nicht öffnen („Running as root without --no-sandbox is not supported“); behoben mit dauerhaftem Start-Skript, und der Container läuft auf Daniels Wunsch mit Host-Zugriff; ein Sicherheitsfund wird beschrieben. Doku 77 (2026-09-19): Der Desktop stürzte am 2026-09-18 zweimal ab; Speicherdruck auf dem Host.
Doc 45 (2026-07-31): Chromium would not open in the second desktop; fixed with a permanent start script, and the container runs with host access at Daniel's wish; a security finding is described. Doc 77: the desktop crashed twice on 2026-09-18; memory pressure on the host.
