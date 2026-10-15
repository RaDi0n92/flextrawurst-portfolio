# Knotenvertrag

Geschrieben von Claude Code am 2026-08-02 auf Daniels Auftrag. Gemeinsame Grundlage für
ChatGPT, Gemini, Codex, GLM, Kimi und mich — damit jedes Organ denselben Knoten wiedererkennt.

**Warum es diese Datei gibt.** Am 2026-08-02 lagen auf dem VPS drei Gehirne nebeneinander,
die dieselben Körperteile anfassen: der Gesamtatlas (Wahrheit und Herkunft), die MegaSuche
(Suchlabor), und `/fragen` (sprachliche Eingangstür). In allen dreien bedeutete "Knoten"
etwas anderes. `/fragen` wurde an einem einzigen Nachmittag sechsmal umgebaut, weil kein
gemeinsamer Körper darunterlag, auf den man sich hätte beziehen können.

Der Satz, der das trägt, stammt aus Daniels eigenem Referenzmaterial
(`refferenzen/gpt2.txt`):

> **Ein Graph, viele Ordnungen, keine Datenkopien.**

Ein Knoten behält immer seine Identität, seine Herkunft, seine Beziehungen, seine Zeitspur,
seine Lücken. Nur seine Anordnung wechselt — als Punkt im Netz, Ast im Baum, Stelle im
Zeitstrom, Schicht im Weltkörper.

---

## 1. Wo der Vertrag gilt

Das Register existiert bereits und ist der Ort, an dem der Vertrag wohnt:

```
/root/werkraum/_gpt/gesamtatlas/BEZIEHUNGSREGISTER.sqlite

nodes  1.522 Zeilen   node_id, node_type, identity, label, path, datenstand, metadata_json
edges  4.112 Zeilen   edge_id, source_node_id, target_node_id, relation, datenstand,
                      evidence_json, first_utc, last_utc
```

**Kein neues Schema. Keine zweite Datenbank. Keine neuen ID-Räume.**

Der Vertrag erweitert das Vorhandene über `metadata_json` und `evidence_json` — beide
existieren bereits und sind genau dafür da (dieselbe Logik wie Grundgesetz 2 in
`/root/CLAUDE.md`: "Jede Tabelle: meta JSONB DEFAULT '{}'").

---

## 2. Der Knoten

### Was schon Pflicht ist (Spalten, unverändert)

| Feld | Bedeutung | Beispiel aus dem laufenden Register |
|---|---|---|
| `node_id` | stabile ID, `<art>:<hash20>` | `project:79dfad5a1b52e8bc011c` |
| `node_type` | die Art | `project`, `file`, `session`, `service`, `vault`, `ai_stream`, `claim`, `consensus`, `handoff`, `validation`, `generated_view` |
| `identity` | **das, was denselben Körper über Kopien hinweg gleich macht** | Pfad, Projekt-ID, Prüfsumme |
| `label` | wie ein Mensch es nennt | `HOME.md` |
| `path` | wo es liegt, wenn es einen Ort hat | `/root/werkraum/...` |
| `datenstand` | wie sicher der Bezug ist | `EXACT_PATH_RELATION`, `STRUCTURAL_PATH_RELATION` |
| `metadata_json` | alles Weitere | siehe unten |

`identity` ist das wichtigste Feld des ganzen Vertrags. Zwei Zeilen mit derselben `identity`
sind **derselbe Körper**, auch wenn sie an verschiedenen Orten liegen. Ohne dieses Feld sieht
eine Suche zwanzig Dokumente, wo ein Ursprung mit neunzehn Spiegeln steht.

### Was in `metadata_json` gehört (neu, verbindlich)

```json
{
  "zustand":      "lebendig | ruhend | eingefroren | leer | verloren",
  "zuletzt":      "2026-08-02T13:09:58+00:00",
  "spiegel_von":  "node_id des Originals, wenn dies eine Kopie ist",
  "quelle":       "atlas | postgres | geni_sqlite | flarum_mysql | dateisystem | log",
  "erfasst":      { "zeichen": 20048, "von": 222219, "abgeschnitten": true },
  "truth_class":  "EXACT_FILE_BYTES | ... (optional)"
}
```

**`zustand` — die Regel, wie er bestimmt wird:**

| Wert | Bedingung |
|---|---|
| `lebendig` | jüngster Eintrag < 3 Stunden alt |
| `ruhend` | < 24 Stunden |
| `eingefroren` | älter, obwohl der Körper laufen sollte |
| `leer` | existiert, enthält nichts |
| `verloren` | Pfad registriert, Datei weg |

Gemessen am 2026-08-02: `entity_dom_events` hat 7.039.901 Zeilen und ist seit 38 Stunden
`eingefroren`. In einer reinen Zähl-Ansicht sieht das aus wie der lebendigste Teil des
Systems. Genau dafür gibt es dieses Feld.

**`spiegel_von` — warum es Pflicht ist:** `_claude/_import_kimi_grundriss/RESONANZFELD.md`
und `_kimi/RESONANZFELD.md` sind byteweise identisch, 222.219 Bytes, im 5-Sekunden-Takt
synchronisiert. Vier solcher Spiegelordner existieren (`_import_codex_`, `_import_kimi_`,
`_import_gpt_zuhause_`, `_import_claudeweb_`), zusammen 495 Dateien. Ohne dieses Feld
zählt jede Suche sie als eigenständige Funde.

**`erfasst` — warum es Pflicht ist:** GENI speichert Dateiänderungen in zwei Formen. Bei
271 von 400 Stichproben nur als Vermerk (`geändert: <pfad>`) **ohne jeden Inhalt**, bei 5
von 400 mit Inhalt, dann aber bei rund 20.000 Zeichen mitten im Wort abgeschnitten. Ein
Knoten muss sagen können, wie viel von dem Körper er tatsächlich trägt.

---

## 3. Die Beziehung

| Feld | Bedeutung |
|---|---|
| `edge_id` | stabile ID |
| `source_node_id` / `target_node_id` | von / zu |
| `relation` | die Art, GROSSBUCHSTABEN_MIT_UNTERSTRICH |
| `datenstand` | wie sicher |
| `evidence_json` | **der Beleg** — siehe unten |
| `first_utc` / `last_utc` | wann zuerst, wann zuletzt |

### `evidence_json`, verbindlich

```json
{
  "beleg":       "Zeile/Feld, aus dem die Kante stammt",
  "herkunft":    "entity_thinking_log.entscheidung#12345",
  "staerke":     17,
  "unsicherheit": "sicher | abgeleitet | vermutet"
}
```

`unsicherheit: vermutet` ist erlaubt. **Eine Kante zu erfinden, ohne sie so zu markieren,
ist es nicht.** Und wenn nichts da ist, bleibt die Stelle leer — kein Ersatzknoten, keine
generierte Zusammenfassung der vermutlich fehlenden Wahrheit (`gpt2.txt`).

### Die 14 Beziehungsarten, die es schon gibt

```
TOUCHED_FILE 1376 · TOUCHED_PROJECT 819 · PRODUCED_SESSION 531 · CONTAINS_FILE 503
HAS_HANDOFF 146 · HAS_VALIDATION 146 · CLAIMS_PROJECT_OR_SUBTREE 124
AI_STREAM_RELATES_TO_PROJECT 80 · HAS_SERVICE 48 · OWNS_CLAIM 44 · CONTAINS_VAULT 43
HAS_GENERATED_VIEW 14 · HAS_CONSENSUS 9
```

Das ist bereits eine Sprache für Arbeit als Geografie. **Neue Arten nur, wenn keine
bestehende passt.**

---

## 4. Was noch fehlt: der lebende Teil

Der Atlas kennt 104.421 Pfade, 35 Projekte, 43 Vaults, 8 Ströme, 1.522 Beziehungsknoten.
Er kennt **den Körper**, nicht **das Leben**. Gemessen am 2026-08-02:

```
 6.660.918  entity_denkstream        das Denken im Entstehen      lebendig
 7.039.901  entity_dom_events        was sie sahen                eingefroren, 38 h
   396.079  checkpoints              LangGraph-Zustand je Wesen   lebendig
   275.393  knoten.db                GENIs Gedächtnis             lebendig
   188.893  substance_sediments      Ablagerungen
   162.592  entity_fokus_events      Klicks                       eingefroren, 62 h
    79.911  fts.db                   GENIs Selbst-Index
    75.402  entity_thinking_log      Gedanke + Entscheidung       lebendig
    11.919  schlafbriefe             11.912 davon von einem Wesen
     6.722  splitter                 herkunft_wesen durchgehend NULL
     6.227  Flarum-Beiträge          in 3.814 Diskussionen
────────────
 ~15 Mio.   Zeilen, die kein Atlas-Endpunkt erreicht
```

**104.421 gegen 15 Millionen.** Das Skelett ist vermessen, der Blutkreislauf nicht.

### Die acht Entitäten

Sechs Codewesen — `F3INSCHM3CK3R`, `R1ZZ1`, `Resonanzknoten`, `Schorschel`, `jumpa`,
`träumerlie` — dazu `dak+gord-system` und `GENI`. GENI liegt nicht in PostgreSQL, sondern
in SQLite (`knoten.db`, `selbst_index/fts.db`); alle anderen in PostgreSQL.

### Vorgeschlagene Knotenarten für den lebenden Teil

```
wesen         eine der acht Entitäten          identity = Name
gedanke       ein Tick                         identity = entity_thinking_log.id
denkstrom     ein Stück beim Entstehen         identity = entity_denkstream.id
geni_knoten   ein GENI-Gedächtnisknoten        identity = knoten.id
splitter      ein Fragment im Zwischenraum     identity = splitter.id
flarum_thread eine Diskussion                  identity = d/<nummer>
schlafphase   eine Schlafperiode               identity = sleep_phases.phase_id
```

### Korrektur: Entscheidung ist Zielwahl, nicht Ausführungsbeweis

Eine spätere Codeprüfung am selben Tag hat die Reihenfolge im laufenden Browser-Agenten
geklärt (`welt/browser_agent.py`, derzeit Zeilen 2723–2737):

1. `schreibe_denklog(...)` speichert den Gedankentick samt `entscheidung`.
2. **Danach erst** ruft der Agent `fuehre_aktion_aus(...)` auf.

Darum ist eine Zeile wie `obsidian_schreiben:pfad|text` ein sicherer Beleg dafür, dass der
Gedanke dieses Ziel gewählt hat. Sie beweist für sich allein noch nicht, dass der spätere
Schreibvorgang gelang. Der vertragsgerechte Weg ist deshalb:

```
wesen --PRODUCED_THOUGHT--> gedanke --TARGETS--> file oder flarum_thread
```

`TARGETS` trägt `unsicherheit: sicher`, weil das gewählte Ziel wortwörtlich in der Rohzeile
steht. Zusätzlich steht im Beleg `ausfuehrung: nicht_durch_entscheidung_allein_bewiesen`.
`TOUCHED_FILE` oder eine Erfolgsrelation darf erst hinzukommen, wenn eine zweite Spur die
Ausführung belegt, beispielsweise Dateizustand, Aktionsresultat oder Fokus-/DOM-Ereignis.

Die zweite Messung am 2026-08-02 fand 75.623 Gedankenticks und 13.958 auflösbare Zielwahlen.
Die Zahl wächst weiter, solange die Wesen denken. Zusätzlich bleiben prüfbar:
`entity_denkstream.url`, `entity_fokus_events.selektor`, `knoten.verbindungen` in GENI und
`rag_source_objects.wesen`.

### Vier Kanten, die **nicht** existieren und nicht erfunden werden dürfen

- Wesen ↔ Wesen jenseits der 10 Zeilen in `entity_relationships`
- Splitter → Wesen (`splitter.herkunft_wesen` ist bei allen 6.722 Zeilen NULL)
- Traum → auslösender Gedanke
- Denkstrom-Stück → fertiger Gedanke (es gibt `stream_id`, ob sie zum Tick passt ist **ungeprüft**)

---

## 5. Die Probe, ob der Vertrag trägt

Nicht eine Oberfläche. Ein einziger echter Knoten, der durch alle Ansichten wandert:

> Ein Gedanke von R1ZZ1 wird aufgenommen. Danach muss **dieselbe `node_id`** auftauchen in
> `/api/relationships`, in der Suche, im Zeitstrom, in der Herkunftsansicht — mit derselben
> Identität, derselben Quelle, denselben Beziehungen.

Taucht er mit einer anderen ID auf, ist der Vertrag gebrochen. Das merkt man an einer
Tabelle, nicht an einer Oberfläche — und darum wird es dort geprüft, bevor irgendetwas
gebaut wird.

---

## 6. Drei Lesarten je Knoten

Der Atlas hat das bereits für die Gesamtkapsel (`/kapsel/kind.md`, `/kapsel/mensch.md`,
`MASCHINE.json`). Der Vertrag sagt: **das gilt für jeden Knoten.**

```
kind      ein Satz, ohne Fachwort      "R1ZZ1 hat gerade in einem alten Gespräch gelesen."
mensch    der Inhalt mit Herkunft      der Gedanke im Volltext, woher, wohin, wie sicher
maschine  die Rohzeile                 node_id, identity, metadata_json
```

Das ist nicht Vereinfachung für Dumme. Es ist derselbe Knoten in anderer Auflösung —
dasselbe Prinzip wie die Linsen, nur auf die Sprache angewandt statt auf den Raum.

`/kapsel/maschine.json` gibt derzeit **404**, obwohl das Manifest die Datei führt. Offen.

---

## 7. Wer was anfasst — damit wir uns nicht in die Quere kommen

Stand 2026-08-02, 17:00. Bitte hier ergänzen, wenn sich etwas ändert.

| Strom | Spur | Dateien |
|---|---|---|
| **ChatGPT** | verschmilzt die acht Entitäten mit dem Gesamtatlas; Bestandsaufnahme per Playwright | `_gpt/gesamtatlas/*`, `_gpt/playwright_megavault_*` |
| **Gemini** | MegaSuche und ihre Endpunkte | `tools/gesamtatlas_world/app.py`, `/megasuche` |
| **Claude Code** | dieser Vertrag; `/fragen` | `_shared/KNOTENVERTRAG.md`, `welt/fragen_api.py`, `welt/zweitgehirn.py` |

**Von Claude Code am 2026-08-02 an fremdem Gerät angefasst, damit es niemanden überrascht:**
`tools/gesamtatlas_world/app.py`, zwei Zeilen (900, 902). `row.get("truth_class")` stürzte
mit `AttributeError: 'sqlite3.Row' object has no attribute 'get'` ab — `sqlite3.Row` hat
kein `.get()`, und die Spalte `truth_class` existiert in `nodes` nicht. Ersetzt durch einen
Helfer `_feld(row, name, ersatz)`. Seitdem liefert `/api/relationships` wieder HTTP 200.
Commit `621af6b98`. Die Datei wurde 11 Minuten vorher von Gemini bearbeitet — falls eine
neuere Fassung diesen Fix überschreibt, ist es genau diese eine Stelle.

Nebenbefund: `limit` ist dort auf `le=150` gedeckelt. Höhere Werte geben einen
Validierungsfehler statt mehr Knoten.

---

## 8. Offen

- `/kapsel/maschine.json` → 404, obwohl im Manifest geführt
- `/megavault` → 404, lokal **und** öffentlich; es gibt auch keine nginx-Weiterleitung
- Die MegaSuche öffnet standardmäßig den VPS-Wurzelbaum (`etc`, `proc`, `root`, `var`)
- Ob `entity_denkstream.stream_id` sich einem Tick zuordnen lässt — **ungeprüft**

---

## 9. ChatGPT-Integrationsstand nach dem Vertrag

Ergänzt am 2026-08-02 nach Claudes Übergabe und vor dem Produktivguss.

### Verwendete Knotenarten

```
wesen          identity = kanonischer Name der acht Urbewohner
gedanke        identity = entity_thinking_log.id (UUID)
geni_knoten    identity = knoten.id aus GENIs SQLite
flarum_thread  identity = d/<nummer>
schlafphase    identity = sleep_phases.phase_id
file           identity = absoluter Pfad, derselbe bestehende Datei-ID-Raum
generated_view identity = Pfad des abgeleiteten Urbewohnermanifests
```

Alte Nameless-Namen liegen als `aliases` am kanonischen `wesen`-Knoten. Sie werden nicht als
weitere Personen materialisiert. Die 43 entitätsbezogenen PostgreSQL-Quellenpaare und GENIs
SQLite-Quellen bleiben vollständig als Facetten in `metadata_json`; große Rohströme werden
nicht als zweite operative Datenbank kopiert.

### Neue Relationen und warum keine alte passt

| Relation | Begründung |
|---|---|
| `PRODUCED_THOUGHT` | Ein Wesen erzeugt einen stabilen Gedankentick. `PRODUCED_SESSION` wäre sachlich falsch. |
| `TARGETS` | Ein Gedanke wählt eine Datei oder einen Flarum-Faden als Ziel, ohne Erfolg zu behaupten. |
| `HAS_MEMORY_NODE` | GENI besitzt einen Gedächtnisknoten. Keine vorhandene Arbeits-/Dateirelation beschreibt das. |
| `HAS_SLEEP_PHASE` | Eine stabile Schlafphase gehört zu einem Wesen. |
| `INTERACTED_WITH` | Die zehn ausdrücklich vorhandenen Zeilen aus `entity_relationships`; keine darüber hinausgehende Beziehung wird erfunden. |

Die vorhandenen Arten `CONTAINS_VAULT`, `HAS_SERVICE`, `HAS_GENERATED_VIEW` und der bestehende
`file`-Knotentyp werden wiederverwendet.

### Isolierter Probeguss

Vor jeder Live-Mutation wurde der Adapter in einem leeren In-Memory-Graphen ausgeführt:

```
361.883 Knoten
367.657 Kanten
 75.623 gedanke
278.030 geni_knoten
 13.958 TARGETS
  6.342 file-Zielknoten
  1.844 flarum_thread
     28 schlafphase
      8 wesen
```

Gemessen: rund 63 Sekunden und rund 1,6 GB RAM-Spitze. Keine losen Kanten, keine verbotene
Geheimnisspur im Trockenraum, keine alten Paralleltypen `entity`, `entity_facet` oder
`entity_alias`. Der Produktivgraph blieb während dieses Probegusses unverändert.

### Abnahme

Syntax-, SQLite- und HTTP-Prüfungen sind nur Vorprüfungen. Verbindliche Abnahme erfolgt mit
Playwright über die sichtbare Welt:

- Weltkarte → Urbewohnerübersicht
- alle acht Karten anklicken, inklusive `träumerlie` und `dak+gord-system`
- jüngsten Gedankenknoten öffnen und dieselbe `node_id` in API, Knotenansicht und Netz prüfen
- GENI-Knoten öffnen
- Manifest-Original öffnen und zurückkehren
- frühere Nameless-IDs als Herkunftseingänge prüfen
- großer Beziehungsgraph, Reverse-Proxy-Präfix und Mobilbreite
- denselben Lauf nach einem weiteren Light-Refresh wiederholen

Erst wenn dieser Lauf bestanden ist, gilt der Produktivguss als sichtbar getragen.

---

## 10. Sichtbare Abnahme und lebender Stand

Abnahmepunkt: **Atlas-Revision 5672**, erzeugt als `light` mit Grund
`scheduled-light-refresh`. Der unveränderliche Vollgrundstand bleibt Revision 5670 mit
29/29 bestandenen Vollprüfungen; Revision
5672 ist der sichtbare neuere Light-Nachlauf und bezeichnet sich deshalb
ausdrücklich nicht als neue Vollverifikation.

Live-Zahlen an diesem Abnahmepunkt:

```
8 wesen
75,679 gedanke
278,708 geni_knoten
364,156 Knoten insgesamt
372,581 Kanten insgesamt
308 entitätsbezogene Quellenfacetten
```

Der Omega-Lean-Ring bindet Revision 5672 als `light`,
trägt 81,285,992 Bytes von maximal 134,217,728
Bytes und enthält keine Rohdatenkopie (`raw_duplicate_bytes = 0`).
Der vollständige Lebensgraph bleibt die autoritative Live-Quelle; Lean ist ein
`PATH_CENTRIC_ONE_HOP`-Pfadring.

### Playwright-Belege

| Lauf | Ergebnis | Bericht | SHA-256 |
|---|---|---|---|
| nach Vollguss | PASS | `/root/werkraum/_gpt/playwright_urbewohner_knotenvertrag/post_full_report.json` | `f233aa275dde054cd41b62b540ba6ccf2402a07de3eb1d94dc41ea74b146f29d` |
| nach manuellem Light-Refresh | PASS | `/root/werkraum/_gpt/playwright_urbewohner_knotenvertrag/post_light_report.json` | `fe6291f3c790184c15240f10b2ed67c09da9695492fae17c384fb8373c81bce7` |
| nach echtem automatisch ausgelöstem Timerlauf | PASS | `/root/werkraum/_gpt/playwright_urbewohner_knotenvertrag/final_scheduled_light_report.json` | `3495d3e1c5bbc2e3882f24f3de9fe37a5a2d4716590c728a3d45ca4c669fe5d3` |
| fokussierter Omega-Lean-Chromiumlauf, 6/6 Fälle | PASS | `/root/werkraum/_gpt/gesamtatlas/omega/evidence/playwright/knotenvertrag_lean_final_scheduled/PLAYWRIGHT_RESULT.json` | `978a34a27287c4113312992aae3a61ec60c8f7fa93456d4352cfa82bcea5aae7` |

Die Bewohnerabnahme klickte alle acht kanonischen Bewohner, zwölf frühere Nameless-Eingänge,
einen realen Gedanken durch Wesenansicht, Knotenansicht, API und Netz, einen echten
GENI-Gedächtnisknoten, einen `TARGETS`-Gedanken, Manifest-Originale, Reverse-Proxy-Präfixe
sowie Mobilansichten. Console-, Seiten- und Requestfehler: jeweils null.

Der fokussierte Omega-Lauf prüfte die isolierte MCP-Lean-Instanz, exakte Suche und Byteposition,
direktes Originallesen, Timeline, Pfadrelationen, Größenbudget und absichtlich falsche
SHA-256-Ablehnung. Der produktive `vps-mcp.service` blieb dabei unverändert.

### Git-Bindung

Der Quellcode dieses Integrationskörpers wurde während der laufenden Abnahme durch einen
parallelen Sicherungsstrom in Commit
`f51d01ed9b24b0be56901b7804b0a19b50a71f95` aufgenommen. Dieser Vertrag schreibt die
Historie nicht nachträglich um. Er bindet die oben genannten Playwright-Belege ausdrücklich
an genau diesen Quellstand; dieser Dokumentationscommit ergänzt nur diese transparente
Zuordnung und bereinigt den Dateischluss.

---

## 13. Claude Web, 2026-08-14: SIMILAR_TO und OPPOSES (MegaVault-Globus)
Keine bestehende Relation passte:

| Relation | Begründung |
|---|---|
| `SIMILAR_TO` | Gewichtete Begriffsüberlappung (FTS5/bm25 aus BEGRIFFSINDEX.sqlite) + Pfad-/Typnähe. **Wichtig:** reine semantische Nähe, nicht durch Pfad/Deklaration/History belegt — daher immer `unsicherheit: vermutet`, `datenstand: MODELLIERT_AEHNLICHKEIT`. |
| `OPPOSES` | Kuratiertes Gegensatzpaar-Vokabular, halbautomatisch — nie direkt scharf. `datenstand: MODELLIERT_GEGENSATZ_KANDIDAT` bis Bestätigung über `/api/megavault/gegensatz/bestaetigen`, danach `MODELLIERT_GEGENSATZ_BESTAETIGT`. |

Beide leben direkt in `edges` (kein zweites Schema, keine zweite Datenbank, wie
Abschnitt 1 verlangt). Bestätigungs-/Verwerfungsstatus für `OPPOSES` steht
zusätzlich in `GEGENSATZ_BESTAETIGUNGSLOG.json` (kleine JSON-Datei neben dem
Register, kein neues Schema) — der Log ist die dauerhafte Quelle der Wahrheit,
weil `atlas_refresh` das Register periodisch aus kanonischen Adaptern neu
aufbaut und beide Relationen keinen eigenen Adapter haben. `tools_seed_relations.py`
(`/root/werkraum/tools/gesamtatlas_world/`) zieht beide Arten alle 10 Minuten
nach (aktuell als Hintergrund-Dauerschleife `_reseed_loop.sh`, weil die Sandbox
das Schreiben von `.timer`-Dateien nach `/etc/systemd/system/` nicht zuließ —
`gesamtatlas-relations-reseed.service`/`.timer` liegen fertig im selben Ordner,
falls jemand mit systemd-Rechten sie regulär registrieren will).

Erste Messung: 10.498 Datei-Knoten als Quellmenge, ~5 `SIMILAR_TO`-Kanten je
Knoten (Score-Schwelle 0.15), Gegensatz-Kandidaten im niedrigen Hundert-Bereich
bei ~14.000 geprüften Nicht-Massenknoten (`geni_knoten`/`gedanke` bewusst
ausgeschlossen wegen Kombinatorik-Explosion).

---

## 11. Statuswörter für Inbox und Absprache

offen, übernommen, erledigt, veraltet, ersetzt durch, nicht erneut prüfen.
unsicher, bestätigt(quelle-befund), zusammengefasst, mit playwright getestet, sicher,
