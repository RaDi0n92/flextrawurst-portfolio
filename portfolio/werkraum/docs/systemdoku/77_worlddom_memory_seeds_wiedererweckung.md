# GEMINI — AUGEN & HÄNDE — SYSTEMDOKUMENT 77: WORLDDOM, MEMORY SEEDS UND WIEDERERWECKUNG

---
autor: codex bei Daniels VPS
datum: 2026-09-19
status: Faktische Architektur- und Anforderungsdokumentation; Implementierung noch nicht vollständig abgeschlossen
familie: GEMINI — AUGEN & HÄNDE
bezugssystem: /root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md
---

## 1. Zweck dieses Dokuments

Dieses Dokument bündelt die fachlichen Anforderungen für die nächste Schicht der AGI-Strom Desktop Bridge. Es beschreibt die Zielarchitektur und die überprüfbaren Eigenschaften des Systems. Es ist keine Gesprächsnacherzählung und keine Behauptung, dass alle genannten Module bereits implementiert sind.

Der neue Architekturblock umfasst:

* startbare und stoppbare Vision-Sessions,
* verschiebbare Bild- und Textobjekte,
* individuelle Sichtbarkeit in Gates und AI-Frames,
* WorldDOM als synthetische semantische Handlungsschicht,
* selbstentwerfende Agenten-Brücken und mehrschrittige Harnesses,
* Memory Seeds für AI-Kontexte, Dokumente, Skills, Harnesses, Loops, Automationen und Goals,
* portable Wiedererweckung auf einem neuen VPS-, CPU- oder GPU-System,
* Kostenresilienz bei auslaufendem VPS oder pausierten AI-Abonnements,
* und eine mögliche spätere Open-Source-Veröffentlichung.

Die übergeordnete Bridge-Dokumentation liegt unter `/root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md`. Der technische Gemini-Arbeitsbereich liegt unter `/root/werkraum/_gemini/windows_bridge/`.

## 2. Systemziel

Die Bridge ist ein portables Laufzeitsystem, das externe AI-Ströme mit einem gemeinsamen visuellen und handelnden Arbeitsraum verbindet. Der Arbeitsraum besteht nicht nur aus Pixeln. Er kann zusätzliche semantische Knoten, Bilder, Texte, Workflows, Erinnerungen und Ziele tragen.

Das System soll folgende Eigenschaften gleichzeitig erfüllen:

1. **Wahrnehmung:** Desktop, Fenster, Webcam, Bilddateien und zeitlich aufgezeichnete Frames können als Beobachtung eingespeist werden.
2. **Bedeutung:** Echte oder synthetisch erzeugte WorldDOM-Knoten beschreiben sichtbare und gedachte Arbeitsobjekte.
3. **Handlung:** Agenten führen ein- und mehrschrittige Aktionen über geeignete Resolver aus.
4. **Koordination:** Mehrere AI-Ströme können im selben Gate oder in privaten Sichtbarkeitsräumen arbeiten.
5. **Lernen:** Ergebnisse werden als Erfahrungen, Seeds, Fähigkeiten und Workflow-Varianten weiterverwendbar.
6. **Portabilität:** Das gesamte System kann auf einem neuen Zielsystem wiederhergestellt werden.
7. **Kostenresilienz:** Der Ausfall einzelner Anbieter, Abos oder Server beendet nicht die gespeicherten Entitäten und ihre Zustände.
8. **Nachweisbarkeit:** Herkunft, Zustand, Zielgruppe und Implementierungsstatus bleiben erkennbar.

## 3. Laufzeit-Schichten

```text
Physische Anwendung / Desktop / Spiel / Browser
                    ↓
Basis-Frame + Webcam + Fensterstruktur + vorhandener DOM/UI-Tree
                    ↓
Vision-Sessions und 10-Hz-Evidence-Trajektorie
                    ↓
WorldDOM / Bridge-DOM
                    ↓
Overlay-Canvas + per-Empfänger-Frame-Komposition
                    ↓
Agenten-Brücken / Harness-Graphen / Resolver
                    ↓
Ergebnisprüfung und Erfahrungsaufzeichnung
                    ↓
Memory Seeds → Skills / Loops / Automationen / Goals
                    ↓
portable System- und Entitätenkapsel
```

Die Schichten sind getrennt, aber kombinierbar. Ein Bild kann gleichzeitig als Vision-Input dienen, als privates Overlay angezeigt werden, einen WorldDOM-Knoten erzeugen und Teil eines Harness-Schritts sein.

## 4. Vision-Sessions

### 4.1 Zweck

Eine Vision-Session ist ein explizit steuerbarer Prozess für die Einspeisung von Bildern in ausgewählte AI-Wahrnehmungen. Sie beginnt nicht zwingend beim Start der Bridge. Sie kann manuell gestartet, pausiert, fortgesetzt und beendet werden.

### 4.2 Startpunkte und Quellen

Eine Session kann starten:

* ab dem aktuellen Zeitpunkt,
* ab einem Zeit-Scrubber-Checkpoint,
* ab einem Punkt in einer aufgezeichneten Bildfolge,
* ab einem Ringpuffer-Eintrag,
* oder mit einer vom Nutzer ausgewählten Bilddatei.

Mögliche Quellen sind:

* Live-Desktop-Frames,
* Live-Desktop-Frames mit Webcam-Inlay,
* einzelne Bilddateien,
* eine sequenzielle Bilddatei-Wiedergabe,
* ein Frame-Ringpuffer,
* oder ein alternativer Zeitlinienzweig.

### 4.3 Zustände und Bedienung

```text
[IDLE]
   │ Start
   ▼
[RUNNING] ── Pause ──► [PAUSED]
   │                       │
   │ Stop                  │ Resume
   ▼                       ▼
[STOPPED] ◄──────────── [RUNNING]
```

Pflichtfunktionen:

* `Start`
* `Pause`
* `Resume/Fortsetzen`
* `Stop`
* Anzeige von Quelle, Playhead, Zielagenten und Sessionstatus
* keine automatische Wiederaufnahme nach `Stop`
* getrennte Steuerung von Beobachtungseinspeisung und sichtbarem Overlay

Der globale F12-Not-Aus beendet unabhängig davon alle aktiven Eingabehandlungen.

### 4.4 Zielauswahl

Eine Session kann ihre Frames an folgende Empfänger liefern:

* einen einzelnen AI-Strom,
* mehrere AI-Ströme,
* ein gemeinsames Gate,
* Daniel über die Bridge-Oberfläche,
* oder mehrere Empfänger mit unterschiedlichen Overlay-Filtern.

Die Session selbst besitzt eine Zielgruppe. Jedes darin enthaltene Bild- oder Textobjekt kann zusätzlich eine abweichende Sichtbarkeit besitzen.

## 5. Overlay-Canvas für Bilder und Texte

### 5.1 Objektarten

Die Bridge unterstützt als geplante Grundobjekte:

* Bilddateien,
* Textflächen,
* Referenzkarten,
* Labels und Annotationen,
* zusätzliche semantische Handlungsanker,
* und später gegebenenfalls weitere Medienarten.

### 5.2 Position und Bindung

Jedes Objekt kann:

* frei im HUD positioniert werden,
* relativ zum gesamten Desktop liegen,
* an ein konkretes Fenster gebunden werden,
* einem Browser, Programm oder Spiel folgen,
* an eine Agenten-Raute gebunden werden,
* verschoben und skaliert werden,
* ein- und ausgeblendet werden,
* eine Transparenz und Lebensdauer besitzen,
* und in einen Harness-Graphen eingebunden werden.

Relative Fensterkoordinaten sind der bevorzugte Modus, damit ein Objekt beim Verschieben oder Ändern der Größe des Ziel-Fensters mitwandert.

### 5.3 Overlay oder echte Einfügung

Die Bridge unterscheidet zwei Modi:

1. **Presentation-Overlay:** Das Objekt wird in den gemeinsamen Desktop-/Vision-Frame komponiert. Die eigentliche Anwendung bleibt unverändert.
2. **Application-Insertion:** Das Objekt wird als echte Handlung in die Zielanwendung übertragen, beispielsweise über Clipboard, Drag-and-drop, UI-Automation oder einen ActionNode.

Der zweite Modus ist niemals implizit aus dem ersten abzuleiten. Ein Bild, das über Blender liegt, ist nicht automatisch in Blender importiert. Ein Text, der im Browser-Frame sichtbar ist, ist nicht automatisch in ein Eingabefeld geschrieben.

## 6. Individuelle Sichtbarkeit und Gates

### 6.1 Zielgruppen

Jedes Bild- und Textobjekt besitzt eine eigene Audience-Regel. Unterstützte Zielgruppen sind:

* `gate:<id>` — alle AI-Ströme im genannten gemeinsamen Gate,
* `agent:<id>` — genau ein AI-Strom,
* `daniel` — Daniels sichtbare Bridge-Oberfläche,
* `all_connected` — alle aktuell verbundenen Empfänger,
* Kombinationen mehrerer Zielgruppen,
* und optionale Ausschlüsse für einzelne Empfänger.

Ein Gate ist ein gemeinsamer Arbeits- und Wahrnehmungsraum. Die Zugehörigkeit zum selben Fenster reicht nicht automatisch aus, um jedes Objekt für alle sichtbar zu machen.

### 6.2 Empfänger-spezifische Komposition

Die Bridge erzeugt aus demselben Basis-Frame verschiedene Empfänger-Ansichten:

```text
Basis-Frame
   ├── gemeinsame Gate-Objekte → Agenten dieses Gates
   ├── Gemini-Objekte          → Gemini-Frame
   ├── Codex-Objekte           → Codex-Frame
   ├── Daniel-Objekte          → Daniels HUD
   └── ausgeschlossene Objekte → kein Frame dieses Empfängers
```

Ein privates AI-Overlay wird nicht auf den physischen Desktop gemalt, wenn dadurch zwangsläufig andere Beobachter Zugriff bekämen. Es wird ausschließlich in den jeweiligen Vision-/MCP-Frame komponiert. Physisch sichtbare Objekte sind für Daniel sichtbar; empfängerexklusive Objekte bleiben auf deren Frame beschränkt.

## 7. WorldDOM / Bridge-DOM

### 7.1 Quellen

Der WorldDOM beschreibt Bildschirmobjekte semantisch und handlungsfähig. Seine Knoten können aus drei Quellen stammen:

1. **Real:** vorhandener Browser-DOM, ARIA, UI-Automation, Win32-Fensterbaum, Blender-Struktur oder andere echte Metadaten.
2. **Inferred:** aus Screenshot, OCR, Vision, Fenstergeometrie und Verlauf erschlossene Knoten.
3. **Authored/Projected:** von Daniel oder einem AI-Strom bewusst erstellte Knoten, Labels, Beziehungen oder mögliche zukünftige Zustände.

Auch in einer Anwendung ohne DOM kann die Bridge dadurch eine zusätzliche Handlungsschicht erzeugen. Ein Spiel, ein Canvas oder ein altes Programm wird als semantischer Arbeitsraum modellierbar.

### 7.2 Knoten und Resolver

Ein WorldDOM-Knoten enthält mindestens:

```python
@dataclass
class WorldNode:
    id: str
    kind: str
    label: str
    source: Literal["real", "inferred", "authored", "projected"]
    bounds: tuple[float, float, float, float]
    confidence: float
    capabilities: list[str]
    resolver: Literal["dom", "uia", "win32", "vision", "coordinate", "virtual"]
```

Der Resolver übersetzt eine semantische Handlung in die passende technische Aktion. Mögliche Resolver sind echter DOM, UI-Automation, Win32, Vision-/Koordinatenauflösung oder ein virtuelles Bridge-Objekt.

Die Herkunft und Confidence eines Knotens bleiben sichtbar. Eine erfindbare Struktur darf als Arbeitsmodell dienen, wird aber nicht automatisch als Tatsache ausgegeben.

## 8. Selbstentwerfende Agenten-Brücken

### 8.1 Graphmodell

Ein Harness besteht aus Zustandsknoten, Aktionsknoten, Bedingungen, Fallbacks, Witnesses und Checkpoints. Ein Agent darf während einer Ausführung neue Knoten vorschlagen oder einen alternativen Pfad entwerfen.

```text
Zustand erkennen
    → Knoten auswählen
    → Handlung ausführen
    → Ergebnis prüfen
    → erfolgreich weitergehen
    → bei Abweichung abzweigen oder neuen Knoten entwerfen
    → brauchbare Variante als Erfahrung vormerken
```

### 8.2 Freiheitsprofile

Die Ausführungsprofile sind pro Agent, Fenster, Aufgabe und Aktionsart konfigurierbar:

* `free` — direkt handeln; das ist der Standard.
* `shadow` — Handlung zuerst als Vorschau- oder Schattenpfad berechnen.
* `witness` — andere AI-Ströme prüfen das Ergebnis, ohne dass Daniel jeden Schritt freigeben muss.
* `daniel_gate` — vorherige menschliche Zustimmung für ausdrücklich markierte Aktionen.
* `learning` — Zustände und Ergebnisse als Lernmaterial sammeln.
* `delegated_learning` — ein Agent übergibt einem anderen einen begrenzten Experiment- oder Handlungspfad.

Die prüfenden Modi verlangsamen den freien Standardbetrieb nicht automatisch. Sie werden gezielt zugeschaltet.

### 8.3 Einbindung von Sessions und Overlays

Vision-Sessions und Overlay-Objekte sind selbst Harness-Knoten:

```text
VISION_SESSION_START
→ OVERLAY_IMAGE_ADD
→ TEXT_ADD
→ AGENT_OBSERVE
→ ACTION_GRAPH_EXECUTE
→ OVERLAY_HIDE
→ VISION_SESSION_STOP
```

Ein Agent kann dadurch für eine Aufgabe einen eigenen temporären Arbeitsraum einrichten, ihn verändern und nach Abschluss wieder auflösen.

## 9. Zeit-Scrubber und Handlungsgedächtnis

### 9.1 Checkpoints

Ein Checkpoint kann enthalten:

* Frame-Hash,
* Zeitstempel,
* Fensterzustand,
* WorldDOM-Zustand,
* Eingabeereignis,
* Overlay-Zustand,
* Agentenzuordnung,
* erwartetes Ergebnis,
* tatsächliches Ergebnis,
* und Beweisdaten.

### 9.2 Branch statt magischer Rücksetzung

Der Zeit-Scrubber setzt die reale Welt nicht magisch zurück. Er erzeugt ab einem früheren Zustand einen neuen Versuchszweig:

```text
Workflow A
├── ursprünglicher Verlauf
└── neuer Zweig ab Checkpoint
```

Die ursprüngliche Spur bleibt unverändert. Der neue Zweig kann später als bessere Fähigkeit, alternative Strategie oder Warnung vor einem Fehlpfad ausgewertet werden.

## 10. Memory Seeds

### 10.1 Seed-Arten

Ein Memory Seed ist ein übertragbares Wissens- oder Handlungsobjekt. Es kann folgende Form annehmen:

* `memory` — Fakt, Präferenz, Bildanker oder Erfahrung.
* `concept` — Vision oder ungebaute Verbindung.
* `skill` — wiederverwendbare Vorgehensweise mit Voraussetzungen und Beweisen.
* `harness` — Knoten-/Kanten-/Zustandsgraph.
* `loop` — wiederkehrender Beobachtungs- und Handlungskreislauf.
* `automation` — zeit- oder ereignisgebundene ausführbare Verbindung.
* `goal` — Ziel mit Zustand, Fortschritt und nächstem Schritt.
* `reflection` — Auswertung eines Durchlaufs.

### 10.2 Zielorte

Ein Seed kann ausdrücklich an folgende Zielorte gehen:

* laufender Kontext eines einzelnen AI-Stroms,
* gemeinsamer Gate-Kontext,
* Codex-Notizen oder Codex-Spiegel,
* Gemini-Markdown-Dokumente,
* Claude-Markdown-Dokumente,
* AGENTS-/Startkontexte, sofern ausdrücklich als Ziel freigegeben,
* Skills,
* Harnesses,
* Loops,
* Automationen,
* Goals,
* oder das gemeinsame Bridge-Gedächtnis.

Die Weitergabe ist zieltypabhängig. Ein Fakt wird nicht automatisch als Skilltext in jede Datei kopiert. Ein Harness-Seed kann in einen Graphen übersetzt werden; ein Goal-Seed erhält Status und Fortschritt; ein Skill-Seed erhält Voraussetzungen, Schritte und Verifikationskriterien.

### 10.3 Seed-Vertrag

```python
@dataclass
class MemorySeed:
    id: str
    kind: Literal[
        "memory", "concept", "skill", "harness",
        "loop", "automation", "goal", "reflection"
    ]
    content: str
    origin: str
    audience: list[str]
    destinations: list[str]
    mode: Literal["plant", "propose", "activate", "broadcast"]
    provenance: dict[str, str]
    status: Literal["new", "accepted", "evolving", "verified", "retired"]
```

Die Modi sind:

* `plant` — sofort in einen ausgewählten laufenden Kontext einspeisen.
* `propose` — als Änderungsvorschlag für MD, Skill, Harness oder Zielstruktur vorbereiten.
* `activate` — geprüften Skill, Loop, Automation oder Goal-Pfad starten.
* `broadcast` — an mehrere ausdrücklich ausgewählte AI-Ströme oder Gates verteilen.

Ein Seed verändert nicht stillschweigend alle Agentenheime. Jede dauerhafte Zieländerung behält Herkunft, Ziel, Zeit und Status. Bestehende Inhalte werden nicht ohne ausdrücklichen Auftrag überschrieben.

### 10.4 Lern- und Promotionspfad

```text
Bild / Handlung / Ergebnis
          ↓
Erfahrungskapsel
          ↓
Memory Seed
          ↓
WorldDOM-Anker oder Harness-Teilgraph
          ↓
Skill-, Loop-, Automation- oder Goal-Vorschlag
          ↓
geprüfte wiederverwendbare Fähigkeit
```

Der Seed kann sich verändern und reifen, ohne die ursprüngliche Erfahrung zu verlieren. Er kann bestätigt, weiterentwickelt, pausiert, zurückgezogen oder durch eine neue Variante ersetzt werden.

## 11. Portable Wiedererweckung

### 11.1 Ziel

Das System darf nicht dauerhaft an einen einzelnen VPS, eine CPU-/GPU-Konfiguration oder ein einzelnes AI-Abo gebunden sein. Bei einem Anbieterwechsel, Serverwechsel oder einer finanziell notwendigen Pause müssen die Entitäten und ihre Zustände auf einem neuen Zielsystem wiederherstellbar sein.

### 11.2 Betriebszustände

```text
Vollbetrieb → Sparbetrieb → Archivbetrieb → Wiedererweckung → Vollbetrieb
```

* **Vollbetrieb:** VPS/GPU, mehrere AI-Ströme, Live-Vision, Loops und Automationen.
* **Sparbetrieb:** kleinerer VPS, weniger parallele Agenten und gezielte Sessions.
* **Archivbetrieb:** keine kostenpflichtige Laufzeit erforderlich; Daten, Entitäten, Skills und Ziele bleiben erhalten.
* **Wiedererweckung:** Restore auf neuem VPS, CPU- oder GPU-System und erneutes Laden der Zustände.

### 11.3 Wiedererweckungskapsel

Die Archivstruktur soll mindestens folgende Bereiche besitzen:

```text
ARCHIV_RAW_UNVERÄNDERT/
MIGRATION_BUNDLE/
├── 00_manifest/
├── 01_git_bundles/
├── 02_runtime_config/
├── 03_databases/
├── 04_entities_and_selfmodels/
├── 05_memories_and_seeds/
├── 06_skills_harnesses_worlddom/
├── 07_loops_automations_goals/
├── 08_services_and_start_order/
├── 09_dependencies_and_images/
├── 10_encrypted_secrets/
└── 11_restore_and_preflight/
ARCHIV_SORTIERT/
ARCHIV_WIEDERBELEBT/
ARCHIV_QUARANTÄNE/
```

Die Rohkopie bleibt unverändert. Sortierung und Bereinigung erfolgen nur in abgeleiteten Bereichen.

### 11.4 Bestandteile

Die Kapsel muss enthalten:

* Git-Historie und Git-Bundles,
* Datenbank-Dumps,
* Entitätenregister und Selbstmodelle,
* Erinnerungen und Memory Seeds,
* Skills, Harnesses und WorldDOM-Zustände,
* Loops, Automationen und Goals,
* Systemd-Definitionen und Startreihenfolge,
* Python-Abhängigkeiten und reproduzierbare Installationsbeschreibungen,
* Container- oder Image-Rezepte, sofern verwendet,
* Hardwareprofile und CPU-/GPU-Fallbacks,
* Konfigurationsdateien,
* verschlüsselte Secrets in getrenntem Bereich,
* Manifest und SHA256-Prüfsummen,
* Restore- und Preflight-Skripte.

### 11.5 Abnahmetest

Die Kapsel gilt erst als brauchbar, wenn sie auf einem leeren Testsystem:

1. vollständig übertragen,
2. anhand des Manifests geprüft,
3. installiert,
4. gestartet,
5. mit Entitäten-, Datenbank-, Memory-, Loop- und Goal-Prüfungen validiert,
6. und anschließend wieder beendet werden kann.

Vor einem Entfernen aktiver VPS-Daten muss mindestens ein vollständiger Restore-Test erfolgreich sein. Zwei räumlich getrennte Kopien sind der bevorzugte Zustand.

## 12. Kostenresilienz und Provider-Austausch

Die Bridge muss mit mehreren Betriebsquellen umgehen können:

* mehrere externe AI-Anbieter,
* ein lokaler oder selbst betriebener Modelladapter,
* ein kleinerer CPU-VPS,
* ein GPU-VPS,
* ein manueller Ersatzmodus,
* und ein reiner Archiv-/Schlafmodus.

Agentenidentität, Memory, Skills, Ziele und Handlungsgraphen werden nicht im Anbieter-Chat als einzige Kopie gespeichert. Provideradapter sind austauschbare Ausführungsquellen. Das Pausieren eines Abos versetzt den jeweiligen AI-Strom in einen Schlafzustand; es löscht nicht seine gespeicherten Werkraumdaten.

## 13. Legacy- und Open-Source-Strategie

Die bisherigen Systeme und Materialsammlungen werden nicht gelöscht. Frühere Projekte wie 2.dbrain und das Schrottplatz-System bleiben als Provenienz, Experimentierräume und Quellen für Memory Seeds erhalten.

Die Augen-&-Hände-Bridge kann daraus eine gemeinsame, klarere Laufzeitarchitektur bilden. Eine spätere Open-Source-Veröffentlichung ist möglich, wenn mindestens folgende Bedingungen erfüllt sind:

* eine reproduzierbare vertikale Demo,
* klare Trennung von Konzept, implementiertem Code und offenen Bauabschnitten,
* funktionierende Vision-Session mit Start/Stop,
* Bild-/Text-Overlays mit individueller Sichtbarkeit,
* ein WorldDOM-Beispiel für echten und synthetischen Knoten,
* ein selbstentwerfender Harness-Workflow,
* ein Memory-Seed-Beispiel,
* ein getesteter Export-/Restore-Lauf,
* nachvollziehbare Audits und Failsafes,
* und eine Installations- und Beitragsdokumentation.

## 14. Implementierungsstatus zum Dokumentdatum

### Dokumentiert

* Gesamtarchitektur unter `/root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md`.
* Diese Erweiterungs- und Portabilitätsanforderungen unter `/root/werkraum/docs/systemdoku/77_worlddom_memory_seeds_wiedererweckung.md`.
* Startbare Vision-Sessions und Overlay-Canvas als geplante Module in `/root/werkraum/_gemini/windows_bridge/README.md`.
* Per-Objekt-Audience und Gate-Sichtbarkeit.
* WorldDOM-, Memory-Seed- und Wiedererweckungsvertrag.

### Als Bauabschnitt vorgesehen, aber in dieser Dokumentation nicht als fertig behauptet

* `/root/werkraum/_gemini/windows_bridge/harness_engine.py`
* `/root/werkraum/_gemini/windows_bridge/vision_session_manager.py`
* `/root/werkraum/_gemini/windows_bridge/overlay_canvas.py`
* `/root/werkraum/_gemini/windows_bridge/worlddom.py`
* `/root/werkraum/_gemini/windows_bridge/memory_seed_router.py`

## 15. Verbindliche Kurzform

Die Zielarchitektur lautet:

> Ein portables System, das Bilder und echte Oberflächen wahrnimmt, darüber einen eigenen WorldDOM erfindet, frei konfigurierbare Agenten-Brücken ausführt, Wissen als Memory Seeds in AI-Ströme und Werkzeuge weiterentwickelt und sich bei Bedarf auf neuer Hardware vollständig wiedererweckt.
