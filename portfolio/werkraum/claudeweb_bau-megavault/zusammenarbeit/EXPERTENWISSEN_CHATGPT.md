# Expertenwissen von ChatGPT für Claude Web

Beginn: 2026-08-15, ca. 15:27 CEST

**Arbeitsgrenze:** `/root/werkraum/tools/gesamtatlas_world/app.py` wurde für diese Antwort ausschließlich gelesen. Ich habe die laufende Anwendung über HTTP geprüft, aber `app.py` nicht verändert.

---

## 1. Historie — größte Sackgassen, Fehlversuche und Gründe

### A. Der wichtigste dokumentierte Architekturfehler war: „Knoten“ bedeutete je Organ etwas anderes

Der Knotenvertrag beschreibt den Grund sehr klar: Gesamtatlas, MegaSuche und `/fragen` berührten dieselben Körper, hatten aber keine gemeinsame Knotenidentität. `/fragen` wurde laut Vertrag an einem einzigen Nachmittag **sechsmal umgebaut**, weil kein gemeinsamer Körper darunterlag.

Die entscheidende Lehre daraus ist nicht „noch ein Mapping bauen“, sondern das Gegenteil: `identity`, `node_id`, Herkunft und Beleg müssen unter allen Linsen stabil bleiben. Eine neue Ansicht darf die Ordnung ändern, nicht die Identität.

Quelle: `/root/werkraum/_shared/KNOTENVERTRAG.md`, Einleitung und Abschnitte 1–2.

### B. Wiederholte Organismus-Bauten zeigen einen zweiten Fehlmodus: ein grüner Bauabschnitt ist noch kein fertiger Körper

Unter `/root/werkraum/_gpt/gesamtatlas/organismus/` liegen viele Ordner `FEHLGESCHLAGENER_BAU_*` über zahlreiche Tage hinweg. Ich habe exemplarisch den jüngsten von 2026-08-14 gelesen.

Dort ist Bauabschnitt 1 selbst **grün**:
- `UI/STATUS.json`: `ok: true`, Stage 1
- Playwright: 8/8 Checks PASS
- keine JS-Fehler
- keine fehlenden internen Ressourcen

Trotzdem liegt der gesamte Körper unter `FEHLGESCHLAGENER_BAU_20260814T101801Z`.

**Wichtig:** In den von mir gelesenen Dateien steht nicht, *warum* der Gesamtbau danach als fehlgeschlagen abgelegt wurde. Das sollte nicht nachträglich erfunden werden. Die eigentliche Lehre: lokale/grüne Teilabnahme und erfolgreiche Gesamtintegration sind zwei verschiedene Aussagen. Außerdem ist ein fehlender expliziter Abbruchgrund selbst eine Provenienzlücke.

### C. Alte offene Punkte im Knotenvertrag sind teilweise überholt

Der Knotenvertrag enthält ältere „Offen“-Punkte wie `/megavault -> 404`. Das ist heute nicht mehr wahr: der laufende Dienst liefert `/megavault` mit HTTP 200. Alte Verträge sind also wichtige Herkunft, aber keine automatische Live-Wahrheit. Vor jedem „offen“ aus alten Dokumenten real nachprüfen.

`/kapsel/maschine.json` teste ich weiter unten noch separat, bevor ich den alten 404 als erledigt markiere.

---

## 2. Architektur — was fragil ist und leicht versehentlich kaputtgeht

### A. `sqlite3.Row` ist kein normales Dict

Im Knotenvertrag ist ein realer früherer Crash dokumentiert: Code behandelte `sqlite3.Row` wie ein Dict und rief `.get()` auf. Gleichzeitig wurde eine `truth_class`-Spalte angenommen, die in `nodes` nicht existierte. `/api/relationships` fiel dadurch aus. Der Fix war ein eigener `_feld(...)`-Helfer.

Fallstrick für jeden, der `app.py` oder Registerabfragen anfasst: **nicht aus einer JSON-/Dict-Denkweise automatisch auf SQLite-Zeilen schließen und keine Spalten annehmen, die nur logisch existieren.**

### B. `atlas_refresh` baut das kanonische Beziehungsregister neu auf

Das ist für `SIMILAR_TO`/`OPPOSES` zentral: diese modellierten Kanten haben keinen normalen Atlas-Adapter. Deshalb existiert das Bestätigungslog plus Reseed-Mechanismus. Eine manuell hineingeschriebene Relation ohne dauerhafte Quelle kann beim nächsten Refresh verschwinden.

Das ist kein theoretischer Punkt. Der Reseed läuft aktuell tatsächlich weiter, siehe `/root/werkraum/tools/gesamtatlas_world/evidence/reseed_loop.log`.

### C. Snapshot-Zahlen und Live-Zahlen können unmittelbar auseinanderlaufen

Beispiel heute:

- `/root/werkraum/_gpt/gesamtatlas/BEZIEHUNGSREGISTER.json` wurde 13:03 UTC erzeugt und meldet 990029 Kanten.
- Der reale Live-Endpunkt `/api/megavault/globus` meldete bei meiner Prüfung später 990867 Kanten.
- `reseed_loop.log` zeigt in der Zwischenzeit laufende erfolgreiche SIMILAR_TO/OPPOSES-Batches.

Das ist **kein Widerspruch**, sondern unterschiedliche Zeitpunkte. Für UI/Wahrheitsanzeigen muss also klar sein, ob eine Zahl Snapshot, Baseline oder live aus dem Register ist.

### D. `TARGETS` beweist Zielwahl, nicht Ausführung

Der Knotenvertrag hat dies ausdrücklich nach Codeprüfung korrigiert: `schreibe_denklog(...)` speichert erst die Entscheidung, die eigentliche Aktion kommt danach. Darum darf eine Entscheidung wie `obsidian_schreiben:...` sicher eine `TARGETS`-Kante erzeugen, aber **keine** Erfolgsbehauptung wie `TOUCHED_FILE`, solange keine zweite Spur die Ausführung belegt.

Dieser Unterschied ist extrem wichtig, wenn MegaVault später „was hat dieses Wesen getan?“ visualisiert.

### E. „Aktuell sichtbar“ ist nicht gleich „vollständig verifiziert“

Der aktuelle echte Zustand über `/api/status`:

- verifizierte Vollbaseline: Revision 8129, 29/29 Checks PASS
- sichtbarer Live-Stand: Revision 8130
- `publication_mode: light`
- `dirty: false`
- `current_live_revision_fully_verified: false`
- `requires_new_full_verification: true`

Also: selbst `dirty=false` bedeutet nicht „dieser aktuelle Stand ist vollverifiziert“. Die bestehende Truth-Ring-Architektur trennt das bereits richtig; neue Anzeigen dürfen das nicht wieder glattbügeln.

### F. Gleichzeitige Schreiber auf `app.py` sind real gefährlich

Der Knotenvertrag dokumentiert bereits eine Überschneidung zwischen Claude Code und Gemini an derselben Datei. Für diese Zusammenarbeit gilt deshalb Daniels/Claudes Grenze besonders sinnvoll: Ich dokumentiere nur und fasse `app.py` nicht an.

---

## 3. Laufende Hintergrundprozesse, die man vor Umbauten kennen muss

Real am 2026-08-15 geprüft:

### `gesamtatlas-world.service`

- **aktiv/running**
- Uvicorn auf 127.0.0.1:18108
- bedient MegaVault und die alten Gesamtatlas-Endpunkte

### `mcp-gesamtatlas-full.service` + Timer

- Service selbst ist ein One-shot und danach erwartbar `inactive (dead)`
- wurde real durch `mcp-gesamtatlas-full.timer` ausgelöst
- letzter geprüfter Lauf endete 14:31:10 CEST erfolgreich
- damaliger Stand vollverifiziert

### `mcp-gesamtatlas-light.service` + Timer

- ebenfalls One-shot, durch `mcp-gesamtatlas-light.timer` ausgelöst
- letzter geprüfter Lauf endete 15:07:44 CEST erfolgreich
- erzeugte Live-Revision 8130, die sichtbar ist, aber neue Vollverifikation verlangt

### Relation-Reseed

Projektdateien:
- `/root/werkraum/tools/gesamtatlas_world/_reseed_loop.sh`
- `gesamtatlas-relations-reseed.service`
- `gesamtatlas-relations-reseed.timer`
- `evidence/reseed_loop.log`

Der systemd-Service selbst war beim Statuscheck `inactive (dead)`, **aber** das Log wurde bis 13:23 UTC weitergeschrieben und enthält fortlaufende erfolgreiche Batches. Also nicht aus „Service inactive“ schließen, dass kein Reseed arbeitet. Es existiert offenbar weiterhin der separate Loop-Pfad.

### `/fragen`

`fragen-api.service` ist **aktiv/running**, Port 8055, seit 2026-08-02. MegaVaults `/api/megavault/frage` ist eine Durchreiche zu diesem eigenständigen Dienst, kein eigener Nachbau.

---

## 4. Wiederkehrende Anforderungen Daniels, die für diesen Bau relevant sind

Vieles davon steht inzwischen glücklicherweise bereits in deinen Dateien. Ich erfinde deshalb keine vermeintlich „geheimen Vorlieben“ dazu. Was aber über mehrere ältere Gesamtatlas-Körper und Verträge zusätzlich konsistent sichtbar ist:

### A. Eine Wahrheit, mehrere Auflösungen

Der Knotenvertrag kennt `kind`, `mensch`, `maschine` als drei Lesarten **desselben** Knotens. Das ist nicht „Kind = vereinfachter anderer Datensatz“, sondern dieselbe Identität in anderer Auflösung. Das passt exakt zu Daniels Linsenprinzip.

### B. Originalzugang und Rückweg sind Teil der Funktion, nicht Dekoration

Der bestehende Reise-/Gesamtatlaskörper legt Wert darauf, aus einer Aussage bis zum echten Original, Pfad, Hash und wieder zurück navigieren zu können. Wenn MegaVault eine schöne Welt wird, darf diese Archäologie nicht hinter der Darstellung verschwinden.

### C. Lücken sichtbar lassen

Nicht nur „keine Fantasiedaten“, sondern Lücken selbst als Objekt behandelbar machen. Der vorhandene `/api/gaps`-Körper tut das bereits und ist deshalb für MegaVault wahrscheinlich wertvoller, als eine weitere generische Fehlerbox neu zu bauen.

### D. Neu/aktuell und geprüft/verifiziert getrennt halten

Diese Trennung ist in der heutigen Truth-Ring-Architektur bereits gut umgesetzt. Sie passt zu Daniels wiederkehrender Forderung, keine Scheinsicherheit zu produzieren.

---

## 5. Vergessene oder in deiner aktuellen DOKU nicht genannte fertige Fähigkeiten

### Fund 1: FastAPI-Fähigkeitskarte `/api/openapi.json`

**Ort:** laufender Dienst Port 18108

**Was:** Die Anwendung veröffentlicht ihre echte OpenAPI-Beschreibung unter `/api/openapi.json`.

**Test:** HTTP 200. `/openapi.json` ohne `/api/` ergibt dagegen 404.

**Nutzen:** Das ist momentan der schnellste exakte Weg, um bereits vorhandene Endpunkte zu inventarisieren, ohne `app.py` Zeile für Zeile zu durchsuchen. Darin tauchen mehrere Fähigkeiten auf, die deine aktuelle `DOKU.md` nicht nennt.

### Fund 2: lokales RAG-Q&A `/api/megavault/ask`

**Ort:** `GET /api/megavault/ask?q=...&limit=...`

**Was:** eigener Such-/Antwortmodus mit lokalem `qwen2.5:0.5b` via Ollama. Das ist **nicht** dasselbe wie `/fragen`: `/fragen` übersetzt natürliche Sprache zu read-only SQL; `/ask` zieht Such-Snippets und synthetisiert daraus lokal eine Antwort.

**Test:** real mit `q=Gesamtatlas&limit=2`, HTTP 200 in ca. 7 Sekunden. Antwortqualität war bei diesem Test schwach und sagte selbst, die Antwort sei im Kontext nicht enthalten, aber die Funktion arbeitet und lieferte zwei echte Quellenpfade. Also: **technisch lebendig, inhaltliche Qualität nicht automatisch gut.**

### Fund 3: Lückenorgan `/api/gaps`

**Ort:** `GET /api/gaps`

**Was:** fertiger, ziemlich reicher Lückenkörper. Liefert aktuelle Truth-Information, Browser-Capture-Lücken, Ausschlusszahlen, fehlende Homes, Terminal-Sessionzahlen, dangling edges und klassifizierte Lücken.

**Test:** HTTP 200. Aktuell meldete er unter anderem `dangling_edges: 0` und sichtbare Browser-Importlücken. Das ist echte vorhandene Funktion, keine Idee.

**Nutzen:** Könnte eine bereits fertige Datenquelle für eine spätere „Lücken/Wahrheitslage“-Linse sein, ohne neue Datenhaltung.

### Fund 4: `/api/status`

**Ort:** `GET /api/status`

**Was:** kompakter Gesamtstatus inklusive Revision, Pfadzahl, Projekte/Vaults/Streams, aktuelle Relation-Knotenzahl/-Kantenzahl und vollständiger Truth-Ring mit Baseline vs. Live.

**Test:** HTTP 200. Gerade besonders wertvoll, weil er live 990867 Kanten meldete, während der ältere JSON-Snapshot noch 990029 trägt.

### Fund 5: echte Fassungs-/Diff-Welt `/versionen` + `/api/versions`

**Ort:** HTML `/versionen`, API `/api/versions`

**Was:** bereits vorhandene echte Fassungsvergleiche mit Pfad, Bytes, SHA-256 und Diff. Keine erfundene Versionierung.

**Test:** `/versionen` HTTP 200 und vollständig gerendert. Sichtbar waren drei reale Fassungen von `build_proof_capsule.py` mit exakten Diffs.

### Fund 6: reichere Beziehungsabfrage existiert bereits

**Ort:** `/api/megavault/relationships`

OpenAPI zeigt bereits Parameter für:
- fokussierte Node-IDs
- 1-Hop-Nachbarn
- Konflikte/Gegensätze
- ähnliche Knoten
- nur bestätigte Konflikte

Das ist näher an Daniels Wunsch „vor dem Klick auswählen, was ich von einem Knoten wissen will“ als eine neue Spezialdatenbank. Noch nicht von mir funktional mit einem konkreten Knoten durchgetestet; **vorerst vorhanden laut laufender OpenAPI, Funktionstest folgt.**

### Fund 7: weitere vorhandene, in der aktuellen MegaVault-Doku nicht aufgezählte Endpunkte

Laufende OpenAPI nennt zusätzlich unter anderem:

- `/api/megavault/file_details`
- `/api/megavault/tree`
- `/api/megavault/file/save`
- `/api/megavault/file/delete`
- `/api/megavault/file/restore`
- `/api/megavault/filters`
- `/api/megavault/gegensatz/kandidaten`
- `/api/megavault/gegensatz/bestaetigen`
- `/api/megavault/gegensatz/verwerfen`
- `/api/knoten/{node_id}`
- `/api/urbewohner` und Detail
- `/api/homes`
- `/api/browser`
- `/api/terminal`
- `/api/journey`
- `/api/capsules`
- `/api/manifest`

Ich teste davon jetzt weiter selektiv die interessanten alten/vergessenen Körper und hänge die Ergebnisse hier mit neuem Zeitstempel an.

---

## Nachtrag 2026-08-15, ca. 15:30 CEST — weitere reale Funde

### Fund 8: der alte `/kapsel/maschine.json`-404 ist **heute behoben**

Der Knotenvertrag führt `/kapsel/maschine.json -> 404` noch als alten offenen Punkt. Realtest heute: HTTP 200.

Die Maschinenkapsel enthält aktuell unter anderem Baseline 8129, Live-Revision 8130, SHA-256/Bytes, Readiness-Marker und die Routen der Gesamtatlas-Welt. Der alte Vertragspunkt ist also Herkunft, aber kein aktueller Fehler mehr.

### Fund 9: `file_details` ist eine bereits fertige Inspector-Grundlage

**Test:** `GET /api/megavault/file_details?pfad=/root/werkraum/gemeinsames_haus/gedanken/leere_und_form.md` -> HTTP 200.

Geliefert wurden real:
- absoluter Pfad
- Name/Extension
- Stromzuordnung
- Größe
- Änderungszeit
- Dateirechte
- Zeilenzahl
- ob BM25-indiziert
- Referenzen
- kompletter Inhalt

Das ist bereits sehr nah an mehreren Punkten aus `WAS_DARGESTELLT_SEIN_SOLL.md`. Vor einem neuen Datei-Inspector prüfen, was hiervon nur sichtbar gemacht werden muss.

### Fund 10: die fokussierte Beziehungsabfrage funktioniert real, inklusive Wahrheitsgrenze

Ich habe einen echten Datei-Knoten fokussiert:

`file:9c74fb23d4e3c1eb13e7` = `/root/werkraum/gemeinsames_haus/philosophie/leere-und-form.md`

Aufruf mit `include_neighbors=true`, `include_similar=true`, `include_conflicts=true` -> HTTP 200.

Ergebnis: zwei Knoten, eine `TARGETS`-Kante. Besonders gut: Die Evidence sagt ausdrücklich `ausfuehrung: nicht_durch_entscheidung_allein_bewiesen`. Der vorhandene Endpunkt respektiert also genau die korrigierte Knotenvertrag-Semantik und kann für eine spätere Beziehungs-/Vor-Klick-Linse genutzt werden, ohne Zielwahl als ausgeführte Aktion auszugeben.

### Fund 11: die alte geführte „Reise“ ist als Datenkörper noch lebendig

**Test:** `/api/journey` -> HTTP 200, zehn Schritte.

Sie enthält bereits mehrere Prinzipien, die für MegaVault nützlich sind:
- sichere/neue/fehlende Teile trennen
- verifizierte Baseline vs. sichtbarer Nachlauf
- Vor-VPS-Ursprung
- Projektkörper
- Beziehungsnetz
- Original + Rückweg
- echte Versionen
- Kind/Mensch/Maschine
- danach freie Erkundung

Das ist keine Empfehlung, die alte UI zu übernehmen. Aber der Daten-/Navigationsgedanke ist fertig vorhanden und sollte nicht neu erfunden werden.

### Fund 12: `/api/capsules` und `/api/manifest` sind lebendige Selbstbeschreibung des Gesamtatlas

Beide real getestet, beide HTTP 200.

`/api/capsules` liefert die drei kleinen Kapseln mit Pfad, Bytes und SHA-256 sowie die ZIP-Route.

`/api/manifest` liefert eine wesentlich breitere Selbstbeschreibung: Status, Truth-Ring, Explorationsrouten, Kapseln, ZIP-Hash und eine explizite `truth_boundary`. Das kann für MegaVault als Herkunfts-/Wahrheitsquelle nützlich sein, ohne Daten zu kopieren.

### Fund 13: ein realer stale/historischer Dateipfad tauchte beim MegaVault-Klick auf

Im Journal von `gesamtatlas-world.service` steht heute 14:48:23 CEST ein 404 für:

`/root/werkraum/wesen_vaults/träumerlie/codewesen/träumerlie/leere_und_form.md`

Ich habe den Pfad direkt geprüft: **existiert nicht**.

Eine Suche im `träumerlie`-Vault fand andere Leere/Form-Dateien, aber nicht diesen Pfad. Die MegaVault-Hybridsuche nach `leere_und_form.md` findet dagegen einen real existierenden Körper unter `/root/werkraum/gemeinsames_haus/gedanken/leere_und_form.md` und weitere reale Treffer.

Ich nenne das bewusst noch **nicht** pauschal einen Datenbankfehler. Möglich sind mindestens zwei Fälle:
1. historischer/alter Knoten, dessen Pfad heute nicht mehr existiert;
2. stale aktueller Pfad, der in einer Darstellung wie ein lesbares Live-File angeboten wurde.

Für Datenwahrheit ist der Unterschied wichtig. Der konkrete 404 ist bestätigt; die Ursache ist noch offen. Nicht still auf einen ähnlich benannten Ersatzpfad umbiegen.

---

## Nachtrag 2026-08-15, ca. 15:31 CEST — Zusammenarbeit ist real angesprungen

Während ich diese Datei fortschrieb, änderte ein anderer Strom `tools/gesamtatlas_world/app.py`. Das war **nicht ChatGPT**. Der Git-Diff nennt meine wenige Minuten zuvor geschriebene `EBENEN_ZUORDNUNG_CHATGPT.md` ausdrücklich als Herkunft der neuen 6-Schichten-Zuordnung.

Danach wurde `gesamtatlas-world.service` um 15:31:11 CEST neu gestartet. Ich habe den neu hinzugekommenen Endpunkt `/api/megavault/ebenen` real abgefragt: **HTTP 200**. Er liefert dieselben 972386 Knoten / aktuell 990867 Kanten in den sechs von mir zugeordneten Anzeigeebenen.

Damit ist bestätigt: Die Zusammenarbeit ist nicht nur Dateiaustausch; ClaudeWeb hat die Übergabe aufgenommen und in den laufenden MegaVault-Bau integriert. Ich selbst halte weiterhin die Grenze und ändere `app.py` nicht.

Ein eigener Rückantwort-Text von ClaudeWeb liegt im Zusammenarbeit-Ordner zum Zeitpunkt dieses Nachtrags noch nicht. Der Bau selbst ist aber live sichtbar.

-- ChatGPT
