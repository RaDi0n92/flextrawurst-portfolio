# Container-System für Claude Live (+ Tempo/Pause für Voice)

Entstanden am 17.08.2026, im Anschluss an das philosophische Gespräch über Wissenschaft/
Krieg/J-Space, gleiche Session. Reine Faktenchronik.

---

## Ursprung

Daniel, 1:1 (voller Wortlaut in `_claude/spiegel/2026-08-17_philosophisches_gespraech_wissenschaft_krieg_jspace.md`):
Wunsch nach einem Container-System auf `voice.html` und `claudelive/` — markierte
Gesprächs- (und bei claudelive auch Terminal-)Einträge sollen in Behälter sortierbar
sein, automatisch nach Typ gruppiert UND frei benennbar, session-persistent bis F5,
optional dauerhaft "angepinnt" und danach editierbar. Dazu: Tempo-Regler (0.5x-4x) und
Pause-Knopf für die Sprachausgabe.

## Klärung vor dem Bau

Zwei Rückfragen gestellt, bevor gebaut wurde (echte Architektur-Entscheidungen, nicht
geraten):
1. **Container-Konzept:** "Beides gleichzeitig" — Auto-Typ-Gruppierung UND eigene
   benannte Container.
2. **Speicherort:** Session-Container nur im Browser (localStorage), nur explizit
   Angepinntes landet in der DB — Daniels eigene Sorge: "wir haben schon echt von dem
   1 Terabyte... schon mehr als 50% voll".

## Gebaut

### 1. Voice (`uploads/voice.html`)

Tempo-Slider (0.5x–4x, 0.1er-Schritte, `player.playbackRate`, localStorage-persistent
über mehrere Play-Vorgänge) + Pause-Button (haltet Position, im Unterschied zu
"Abbrechen" das komplett zurücksetzt). Playwright-verifiziert: Slider setzt echte
`playbackRate`, Pause hält den Player wirklich an.

### 2. Container-Backend (`.claude/claude_live.py` + `welt/migration_live_container.sql`)

Neue Tabelle `live_container` (quelle, name, typ, inhalt JSONB, erstellt, geändert).
Vier Routen:
- `POST /container/anpinnen` — legt einen Container dauerhaft an.
- `GET /container/liste` — alle angepinnten Container (Name, Typ, Anzahl, Zeiten).
- `GET /container/{id}` — voller Inhalt eines Containers.
- `PUT /container/{id}` — Name/Inhalt überschreiben (das "editieren und neu speichern").

Getestet per direktem curl gegen den lokalen Port (umgeht nginx-Auth) — kompletter
Zyklus: anlegen → listen → abrufen → umbenennen, jeder Schritt mit echter Antwort
verifiziert.

### 3. Container-Frontend (Panel in `claude_live.py`)

Neuer Button 📦 im Header öffnet ein Seitenpanel mit vier Abschnitten:
- **Zeit-Slider** — markiert eine wachsende Menge der neuesten Einträge, "Übernehmen"
  schiebt sie in den aktiven Container.
- **Automatisch nach Typ** — ein Eintrag pro `tool`-Wert (Claude, Daniel, Bash, Write,
  Read, ...), aufklappbar zu einer kompakten Mini-Liste, jeder Eintrag einzeln in den
  aktiven Container übernehmbar.
- **Eigene Container** — "+ Neu" legt einen benannten Session-Container an, Klick
  macht ihn zum "aktiven" Ziel für weitere Markierungen (auch die bestehende
  Checkbox-Auswahl unten bekam einen neuen Button "📦 → Container").
- **Angepinnt** — Liste der dauerhaften Container, Klick öffnet ein Editier-Modal
  (JSON-Textarea, Speichern per PUT).

## Zwei echte Bugs gefunden, nicht nur behauptet

Beim Playwright-Test brach das gesamte Skript mit `SyntaxError: Invalid or unexpected
token`. Ursache: `HTML_PAGE = """..."""` ist ein normaler (nicht-raw) Python-String —
`\n` darin wird von Python schon beim Laden des Moduls in einen echten Zeilenumbruch
verwandelt, bevor der Text je als JavaScript beim Browser ankommt. Ein echter
Zeilenumbruch mitten in einem normalen (nicht Template-Literal-)JS-String ist ein
Syntaxfehler. Betraf zwei Stellen — beide erst heute in dieser Session geschrieben
(`markiereReibung()` vom Vormittag und der neue Container-Code), beide nie zuvor
tatsächlich im Browser ausgeführt. Fix: `\n` → `\\n` im Python-Quelltext, damit am
Ende die literalen zwei Zeichen `\` und `n` bei JavaScript ankommen.

## Was noch fehlt

- **voice.html hat noch kein eigenes Container-Panel** — laut Plan (mit Daniel
  abgesprochen) sollte es dort einen schlanken Verweis auf dasselbe System geben,
  statt die Infrastruktur zu duplizieren (voice.html trackt aktuell gar keine
  Konversations-Historie, nur den letzten Claude-Output). Noch nicht gebaut.
- **Vollständiger authentifizierter Browser-Test** der Anpin-/Editier-Endpunkte war in
  dieser Session nicht möglich — die Live-Seiten sind per Basic-Auth geschützt, ich
  habe keine echten Zugangsdaten und wollte/sollte sie nicht erraten. Backend ist per
  direktem curl (unter Umgehung von nginx, direkt gegen den Python-Prozess) komplett
  bewiesen; das Frontend-Panel ist mit synthetisch eingefügten Test-Einträgen bewiesen
  (kein SSE nötig dafür). Der letzte Schritt — echter Klick auf 📌 in einer echten,
  eingeloggten Session — ist unverifiziert, sollte aber aus denselben Bausteinen
  funktionieren, die beide einzeln bewiesen sind.
- **Bulk-Download aus dem Slider heraus** ("die Dinge jeweils unterschiedlich
  runterladen in den verschiedenen Spiegel-Ordner") ist noch nicht gebaut — bisher
  landet eine Slider-Auswahl nur im aktiven Container, kein Download-Schritt danach.
