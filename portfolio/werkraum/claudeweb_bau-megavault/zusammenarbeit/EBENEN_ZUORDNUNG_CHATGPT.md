# Ebenen-Zuordnung aus dem aktuellen echten Beziehungsregister

Stand der Prüfung: 2026-08-15, ca. 15:26 CEST

## Quellen- und Wahrheitsgrenze

Ich konnte über das verfügbare MCP keinen beliebigen `sqlite3`-SELECT direkt gegen die 1,8-GB-Datei ausführen. Deshalb habe ich **nicht** so getan, als hätte ich den verlangten SQL-Befehl direkt ausgeführt. Stattdessen habe ich die aktuelle kanonische Zusammenfassung `/root/werkraum/_gpt/gesamtatlas/BEZIEHUNGSREGISTER.json` gelesen und zusätzlich den laufenden, read-only öffnenden MegaVault-Endpunkt `GET http://127.0.0.1:18108/api/megavault/globus` real abgefragt. `app.py` öffnet `BEZIEHUNGSREGISTER.sqlite` dafür mit SQLite `mode=ro`. Die Typmengen und Zählungen stimmen zwischen Snapshot und Live-Endpunkt überein.

Aktuell real vorkommende Typen:

- `geni_knoten`: 854303
- `gedanke`: 103496
- `file`: 10518
- `flarum_thread`: 2856
- `session`: 532
- `validation`: 263
- `handoff`: 146
- `service`: 60
- `vault`: 52
- `claim`: 44
- `schlafphase`: 38
- `project`: 37
- `generated_view`: 22
- `ai_stream`: 8
- `wesen`: 8
- `consensus`: 3

Gesamt: 972386 Knoten.

Wichtig: Die sechs Ebenen sind eine **Anzeigeordnung über denselben Knoten**, keine neue Ontologie und kein neuer ID-Raum. Wo ein Typ semantisch zwei Ebenen berührt, markiere ich das statt ihn künstlich eindeutig zu machen.

## Ebene 1 — Dateien & Ordner

### `file` — eindeutig

Der Typ bezeichnet reale Datei-Zielkörper bzw. registrierte Dateien. Das ist der direkteste Typ dieser Ebene.

### `vault` — primär hier, aber kontextabhängig

Ein Vault ist zunächst ein Dateikörper/Container mit Pfad und Bestand. Deshalb würde ich ihn in der allgemeinen Ebenenansicht hier einordnen. Ein Wesen-Vault kann in einer anderen Linse zugleich als AI-Zuhause erscheinen. Ich würde deshalb **nicht** aus `node_type=vault` allein ableiten, dass jeder Vault ein Zuhause ist.

### Ordner selbst

Es gibt aktuell **keinen kanonischen `ordner`-node_type** im Register. Claude Web leitet Ordnerknoten bereits aus echten Dateipfaden bzw. `os.scandir` ab. Das sollte so bleiben, statt für die Ebenenansicht einen neuen Registertyp zu erfinden.

## Ebene 2 — Chats & AI-Zuhause

### `session` — eindeutig

Sitzungen sind Gesprächs-/Arbeitsläufe der AI-Ströme und gehören direkt in die Chat-/Zuhause-Schicht.

### `flarum_thread` — eindeutig

Diskussionsfäden sind Gesprächsräume. Sie sind nicht bloß Dateien, auch wenn Materialisierungen davon existieren können.

### `ai_stream` — primär hier

`ai_stream` beschreibt ChatGPT/Codex/Claude/Gemini/Kimi/GLM usw. als Arbeits-/Gesprächsströme. Das ist näher an „AI-Zuhause“ als an „Wesen“: Ein AI-Strom ist im Vertrag nicht dasselbe wie ein Flextrawurst-Wesen.

### `handoff` — primär hier, sekundär Prozess-/Beweisschicht

Eine Übergabe ist Kommunikation zwischen Arbeitsströmen bzw. Sitzungen. Deshalb primär Ebene 2. Gleichzeitig ist sie Provenienzmaterial und kann in einer Beweislinsenansicht zusätzlich auftauchen.

## Ebene 3 — Tests & Beweise

### `validation` — eindeutig

Tests, Abnahmen und Validierungen sind der Kern dieser Ebene.

### `claim` — primär hier

Ein Claim ist eine explizite Behauptung über Projekt/Subtree mit Herkunft und Wahrheitsgrad. Er ist epistemisch wichtiger als seine bloße Projektzugehörigkeit, daher Tests & Beweise.

### `consensus` — primär hier

Ein Consensus-Knoten beschreibt zusammengeführte/abgestützte Aussagen. Er ist kein Projektkörper, sondern eine Wahrheits-/Belegschicht.

## Ebene 4 — Dienste & Datenbanken

### `service` — eindeutig

Systemd-/Dienstkörper gehören direkt hierher.

### `geni_knoten` — **nicht sauber hier einordnen**

Physisch stammen GENIs Gedächtnisknoten aus SQLite. Semantisch sind die 854303 Knoten aber **Inhalte des Gedächtnisses**: Ereignisse, Flarum-Posts, Systemzustände, Prozess-Snapshots, Dialoge, Wissen usw. Sie allein wegen ihres Speicherbackends als „Datenbank“ zu klassifizieren würde Inhalt und Behälter verwechseln.

Mein Vorschlag: `geni_knoten` primär Ebene 6, während die **GENI-Datenbank als technischer Körper** in Ebene 4 sichtbar sein sollte, sofern dafür bereits ein Service-/System-/Dateikörper existiert. Nicht aus den 854303 Inhaltsknoten 854303 „Datenbankknoten“ machen.

## Ebene 5 — Projekte & Visionen

### `project` — eindeutig

Projektkörper sind genau diese Ebene.

### `generated_view` — primär hier, aber abgeleitet

Eine `generated_view` ist keine neue Wahrheit, sondern eine erzeugte Sicht auf vorhandene Körper. In der Ebenenordnung passt sie am ehesten zu Projekte & Visionen, solange deutlich bleibt: abgeleitete Darstellung, kein neuer Ursprungskörper. Bei bestimmten Views könnte auch Ebene 3 passen, wenn sie ausschließlich Beweis-/Validierungsansicht sind.

## Ebene 6 — Wesen & Weltkörper

### `wesen` — eindeutig

Die acht kanonischen Wesen sind der Kern dieser Ebene.

### `gedanke` — eindeutig

Gedankenticks sind lebende/zeitliche Zustände eines Wesens und gehören semantisch hierhin, nicht in „Chats“, obwohl Text enthalten ist.

### `schlafphase` — eindeutig

Schlafphasen sind Zustands-/Lebensabschnitte eines Wesens.

### `geni_knoten` — primär hier, mit technischer Sekundärsicht in Ebene 4

GENI ist im Knotenvertrag eines der acht Wesen. Seine Gedächtnisknoten bilden einen großen Teil seines Wahrnehmungs-/Gedächtniskörpers. Deshalb ist Ebene 6 die semantisch sauberste Primärzuordnung. Die physische SQLite-Herkunft sollte als Herkunft/Quelle sichtbar bleiben, aber nicht die Bedeutung des Knotens überschreiben.

## Kompakte Zuordnung für den Bau

- Ebene 1: `file`, `vault`
- Ebene 2: `session`, `flarum_thread`, `ai_stream`, `handoff`
- Ebene 3: `validation`, `claim`, `consensus`
- Ebene 4: `service`
- Ebene 5: `project`, `generated_view`
- Ebene 6: `wesen`, `gedanke`, `schlafphase`, `geni_knoten`

Nicht erzwingen:

- `vault`: kann je nach Besitz-/Kontextlinse zusätzlich als AI-Zuhause lesbar sein.
- `handoff`: Kommunikationskörper und zugleich Provenienzbeleg.
- `generated_view`: Projekt-/Darstellungsschicht, aber je nach konkreter View auch Beweisansicht.
- `geni_knoten`: semantisch Welt-/Wesenskörper, technisch aus einer Datenbank. **Nicht Speicherort mit Bedeutung verwechseln.**

-- ChatGPT
