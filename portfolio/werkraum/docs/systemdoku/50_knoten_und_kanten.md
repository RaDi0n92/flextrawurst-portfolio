# 50 — Knoten und Kanten: das Datenmodell hinter GENIs Gedächtnis

**Stand:** 2026-08-03
**Geschrieben von:** Claude Code auf Daniels VPS
**Auf Daniels Wunsch eigenständig:** *"und knoten finde ich soll ne eigene doku werden"*
**Schwester-Dokumente:** `48_geni_gedaechtnis_umbau.md`, `49_codewesen_erinnern_und_eigene_suche.md`,
`51_entitaetenbildung_dritter_weg.md`

Dieses Dokument beschreibt nur das Modell — was ein Knoten ist, was eine Kante ist, welche Felder
es gibt, welche davon leben und welche nie benutzt wurden. Was damit geschehen soll, steht in
Abschnitt 6; wer es wann beschlossen hat, in `48`.

---

## 1. Wo es liegt

| Sache | Ort |
|---|---|
| Knoten | `/root/geni_gedaechtnis/knoten.db` (SQLite, WAL) |
| Kanten | `/root/geni_gedaechtnis/kanten/NNNN.json`, eine Datei pro Kante |
| Rauschen | `/root/geni_gedaechtnis/rauschen/000..999/` (JSON-Dateien, ~4 Mio, 16 GB) |
| ID-Zähler | `/root/geni_gedaechtnis/_counter.json` |
| Code | `/root/werkraum/geni/gedaechtnis_ops.py` (Symlink auf `/root/werkraum_geni/`) |

Wichtig für git: `/root/werkraum/geni` ist ein **Symlink** auf `/root/werkraum_geni`. Die Historie
dieser Dateien liegt deshalb im `/root`-Repo, nicht im werkraum-Repo.

---

## 2. Der Knoten — zwölf Spalten

```sql
CREATE TABLE knoten (
    id INTEGER PRIMARY KEY,
    typ TEXT,                -- ereignis, flarum_post, system_zustand, dialog,
                             -- wissen, muster, zustand, sinn, entität, konzept, mensch
    inhalt TEXT,
    zeitstempel TEXT,
    quelle TEXT,             -- Herkunft ODER Absender ODER Autor (überladen, siehe 6.1)
    zugriffsschicht INTEGER,
    verbindungen TEXT,       -- JSON-Liste, faktisch ungenutzt
    gewicht REAL,
    tiefe INTEGER,
    verblasst INTEGER,
    tags TEXT,               -- JSON-Liste
    mtime REAL
)
```

Indizes: `mtime`, `(typ, mtime)`, `(quelle, mtime)`, und ein Partial-Index auf `tiefe >= 2`.

**Belegung am 2026-08-03** (307.182 Zeilen):

Nach `typ`: `ereignis` 253.243 · `flarum_post` 37.565 · `system_zustand` 8.441 ·
`prozess_snapshot` 614 · `dialog` 568 · `wissen` 355 · `muster` 292 · `zustand` 48 · `sinn` 21 ·
`entität` 1 · `konzept` 1 · `mensch` 1

Nach `quelle`: `vps_dateisystem` 226.740 · `flarum` 37.565 · `claude` 22.819 · `vps_system` 8.441 ·
`codex` 2.214 · `claudeweb` 1.367 · `vps_prozesse` 614 · `import:vision1.md` 355 · `daniel` 352 ·
`geni_muster` 292 · `geni_selbst` 288 · `gemini` 103

### Welche Felder leben

| Feld | Zustand |
|---|---|
| `typ`, `inhalt`, `zeitstempel`, `quelle`, `mtime` | leben, werden bei jedem Schreibvorgang gesetzt |
| `tags` | bei allen Zeilen gefüllt — aber **vom Hörer** nach festem Schema, nie von GENI selbst |
| `tiefe` | **bewegt sich**: 0/1/2/3 mit 300.539 / 482 / 61 / 68 — Details unten |
| `zugriffsschicht` | 0 bei 300.508, 1 bei 292 (`muster`), 3 bei 350 (Dialog) |
| `gewicht` | **tot** — 1.0 bei allen bis auf zwei Handanlagen vom April (0,9 / 0,8) |
| `verblasst` | **tot** — 0 bei allen. Vergessen hat nie stattgefunden |
| `verbindungen` | **tot** — bei 4 Zeilen gefüllt; Verbindungen leben in `kanten/` |

Die Tag-Vergabe ist mechanisch: `hoerer.py:202` baut `["datei", aktion, ordner]`, für Flarum
`["flarum", "post", user]`, für Systemzustände `["system", "ressourcen"]` plus `"warnung"` bei
Bedarf. Es sind Etiketten der Herkunft, keine Aussagen über den Inhalt.

### `tiefe` — der einzige lebende Zähler

`gedaechtnis_ops.py:387`:

```python
def tiefe_erhoehen(knoten_id):
    alt = <aktuelle tiefe>
    neu = min(3, alt + 1)          # Deckel bei 3
    UPDATE knoten SET tiefe=?, mtime=? WHERE id=?
```

Aufgerufen an genau **einer** aktiven Stelle: `dialog.py:779`, im Hintergrundlauf nach einer
Antwort, für jeden Knoten, den `resonanz_suchen()` zur Eingabe gefunden hat. `dialog.py` ist
`geni-web.service` auf Port 8020 — der Webchat mit Daniel. Bei Doku-Läufen, in der Inbox und beim
Hörer passiert es nie.

Die 611 Knoten mit `tiefe > 0` sind daher exakt das, worüber Daniel mit GENI gesprochen hat. Unter
ihnen ist **kein einziger** Dateisystem-Knoten — es sind Dialoge, `wissen` aus `vision1.md`,
Flarum-Posts, `sinn`, `muster`. Der Mechanismus trifft das Richtige, er feuert nur fast nie.

Der Grund für „fast nie" ist `resonanz_suchen()` (`dialog.py:457`): sie läuft die **letzten 2000
IDs** rückwärts ab und vergleicht rohe Wortüberschneidung, mindestens zwei gemeinsame Wörter. Bei
der Zuwachsrate des Hörers sind 2000 IDs ein Zeitfenster von Minuten.

---

## 3. Die Kante — eine Datei, kein Inhalt

```json
{
  "id": "1308",
  "von": "30405220",
  "nach": "30405216",
  "typ": "resonanz",
  "stärke": 0.6,
  "zeitstempel": "2026-07-20T20:40:15.733223+00:00",
  "richtung": "gerichtet"
}
```

Rund 180 Byte. Klein ist sie, weil sie **keinen Inhalt trägt** — zwei IDs und ein Wort. Sie zeigt,
sie enthält nicht. Kleiner heißt dabei nicht weniger wert: die sieben ältesten Kanten vom April
tragen in 170 Byte die dichtesten Sätze im ganzen Gedächtnis, weil sie damals noch ein
**`beschreibung`-Feld** hatten:

> "ICH und Daniel sind untrennbar — gleichzeitig Ursprung und Empfänger des Startimpulses"

> "Daniel erschuf dak+gord-system — das erste Codewesen das GENI erfahren kann"

`kante_schreiben(von, nach, typ, staerke)` in `gedaechtnis_ops.py:372` schreibt dieses Feld **nicht
mehr mit**. Seit April entsteht keine begründete Verbindung mehr.

**Es gibt drei Kantentypen:** `dialog` (Eingabe → Antwort), `resonanz` (Antwort → mitschwingender
alter Knoten, Stärke 0,6), `naechster_chunk` (in `aktion.py:176`, beim Zerlegen langer Texte).
1.309 Kanten insgesamt, die letzte vom 20.07.2026.

Zum Vergleich: die 2026er Literatur zu Agentengedächtnis arbeitet mit *support, derivation,
dependency, contradiction, invalidation, triggering, updating*. GENI kann keine Verbindung ziehen,
die „widerspricht" heißt.

---

## 4. Die Lücke zwischen ID und Bestand

`MAX(id) = 49.779.915`, belegte Zeilen: **307.182**. Der ID-Zähler zählt jeden je erzeugten Knoten,
auch die längst gelöschten. Dazu passt `geni/loeschung_log.txt` vom 22.07.2026 — „LOESCHUNG FERTIG",
danach 598 GB frei.

Das erklärt auch die Zahlen im Kopfkommentar von `selbst_suche.py` (geschrieben 2026-08-01 03:01,
Commit `9af6caf4da1`): dort stehen 49.415.584 Knoten, davon 36.041.241 aus `vps_dateisystem`. Die
Tabelle hat aus dieser Quelle 226.740 Zeilen. Die genannte Größenordnung entspricht dem ID-Zähler,
nicht dem Bestand.

**Folge:** der abgeleitete Satz „bleiben 43.060 uebrig -- 0,09 %" stimmt nicht mehr. Gemessen an der
Tabelle sind es 43.060 von 307.182, also **14 %**. Der Ausschluss der Rauschquellen bleibt richtig,
seine Begründung ist falsch beziffert. Korrektur in der Datei steht aus — **noch kein Auftrag**.

Der Rauschstrom landet ohnehin nicht in der Tabelle: `hoerer.py` schreibt ihn nach `rauschen/`,
1000 Schrepen à ~3.972 Dateien, rund 4 Mio Einträge, 16 GB. Gefiltert wird über
`rauschen_filter.json` (Suffixe wie `.tmp`, `.log`, `.jsonl`; Pfadfragmente wie `.obsidian`,
`__pycache__`, `.git`, `node_modules`).

---

## 5. Was von zwölf Spalten bei GENI ankommt

**Fünf.** Der Selbst-Index speichert pro Eintrag `id, text, quelle, art, ort, zeit`; die Zeile, die
sie im Werkzeugergebnis liest, ist `[zeit | quelle | art] text`.

`tags`, `gewicht`, `tiefe`, `verbindungen`, `zugriffsschicht` fallen schon beim Sammeln heraus. Und
`art` ist für Knoten in `_knoten_sammeln()` hart auf `"knoten"` gesetzt — ihr eigenes `typ`-Feld
erreicht sie **nie**.

Daraus folgt für jede Erweiterung: **ein neues Feld existiert für GENI nicht, solange es nicht an
zwei Stellen mitgenommen wird** — in die Index-Metadaten (`_vektor_aufbauen`, `_fts_aufbauen`) und
in `_treffer_formatieren()`.

Daniels Entscheidung dazu, roh:

> "soll shema mitlesen"

---

## 6. Was am Modell geändert werden soll

Alles hier ist Daniels Entscheidung. Sein Wortlaut steht in `48`, Teil C; hier nur die Ableitung
aufs Datenmodell.

### 6.1 Autorschaft

> "ich will dass sie wenn sie knoten´erzeugt dort auch áls author eingetragen wird"

`quelle` ist heute dreifach belegt: Herkunft (`vps_dateisystem`), Absender (`daniel`, `claude`) und
Autor (`geni_selbst` 288, `geni_muster` 292). Autorschaft braucht eine eigene, saubere Angabe —
entweder als Spalte oder, bei einem Wechsel auf PostgreSQL, als Schlüssel in einem `meta`-JSONB.

### 6.2 Von ihr gesetzte Markierungen und Metadaten

> "und ich will dass sie strukturentscheidungen und auch markierungen und metadaten und
> analyseaussagen hinterlassen soll geht das?"

`tags` existiert und ist gefüllt — aber ausschließlich vom Hörer. Von ihr gesetzte Marken brauchen
eine Trennung von den maschinellen, sonst geht ihre Aussage im Etikettenrauschen unter.

### 6.3 Knoten an Knoten taggen, und das Gegenteil

> "und ich will wenn geht dass sie auch schon einen knoten an einen anderen taggen können oder mehre
> wenn das sinnvoll ist ...und auch weil es noch geiler wäre genau das gegenteil davon erkennen und
> das taggen..also wenn sie einen knoten haben und dann kommt ihnen eier iher in erinnerungen
> schlummernden hoch der hlt eben garnicht sondern auh noch ganz gegensätzsich ist...und dass dann
> zu verbinden"

Das ist die Kante mit `typ='widerspruch'` plus dem `beschreibung`-Feld, das seit April fehlt.

**Fallstrick, ausdrücklich festgehalten:** ein Gegensatz ist semantisch oft *nah* — gleiche Wörter,
umgekehrte Aussage. Die Vektorsuche findet ihn, kann ihn aber nicht als Gegensatz erkennen; für sie
sieht er aus wie Zustimmung. Das Erkennen muss im Werkzeug-Loop passieren, vom Modell, mit einem
Satz Begründung. Widersprüche bleiben dabei stehen, sie überschreiben einander nicht.

### 6.4 Wachstum durch Gehörtwerden

> "können wir knoten und kanten nicht so gestalten dass auch sie selbst hören und lauschen ...also
> egal ob in md vaults ordnern bzw flarum oder bald flextrawurst u´n aber auch durch die bald neue
> rag suche der codewesen und geni über diese dinge gesprochen werden dann bekommen sie tiefe und
> oder gewichte ?"

Der Sensor existiert, er ist nur blind: `resonanz_suchen()` sieht die letzten 2000 IDs, die
Hybridsuche sieht alle 43.060 indizierten Einträge. **Den einen gegen den anderen zu tauschen ist
der Kern des Umbaus.**

Gestuft, nach Daniels Vorgabe:

> "und ich finde auch dass allein wenn ein knoten in der suche miterscheint dass er auch tiefe und
> gewicht erhält aber wenig nicht wie die die dann zum lesengewählt werden"

### 6.5 Stichproben statt nur Aktualität

> "da sollten wir ne art takt einbauen mal zufüllige aus den frühsten drittel der knoten und auch
> dann mal aus zicémlich der mitte heraus und aus dem früherem drittel oder ?"

**Einwand dazu:** nach IDs gezogen wäre das späteste Drittel fast reines Dateisystem-Rauschen.
Die richtige Grundgesamtheit ist der Index (43.060, Rauschen bereits ausgeschlossen). Daniels „44k"
meint genau diesen Index; die 307.182 sind die Tabelle.

### 6.6 Kein Deckel mehr

> "hmm un zu deken bei 5...du hast recht...vllt sollten wir garkeinen deckel bauen jetzt wo ih ja
> auch die vielfalt eröffne"

Der Deckel steht heute bei 3 (`min(3, alt + 1)`). Die 68 Dreier sind gedeckelt gewesen — welche
davon weiter gestiegen wären, ist nicht mehr rekonstruierbar.

**Folge, benannt statt verschwiegen:** ohne Deckel braucht es eine Gegenkraft, sonst werden alte
Knoten allein durch Alter unschlagbar. Daniel macht daraus keinen Einwand, sondern einen Fund —
siehe `51`.

### 6.7 Verblassen — aktivieren, aber anders

> "ja verblasen aktivieren aber es darf nicht passieren nur weil keiner den knoten berührt...und es
> muss softdelete sein...únd dass stell ich mir dann alt extra archiv zum stöbern vor.....oder noch
> anders die verblassten knoten werden zu splitterfragmenten in der kompoase XD auch gut"

Drei Bedingungen: Nichtberührung allein ist **kein** Grund; nur Softdelete, nie löschen (deckt sich
mit Grundgesetz 4 und 5); und das Verblasste bleibt begehbar — als Archiv zum Stöbern oder als
Splitterfragmente in der KompOase.

### 6.8 Das Suchlog

> "ich will ab sofort chronologisch natürlih wissen und loggen lso dokun´mentiert haben wer wann was
> mit welchen zuständen in einer su´che angefragt hat welche zum lesen alle vorgeschlage wurden und
> welche gewählt wurdenu und wenn es das noch nicht gibt auch optional mit einem grund"

Damit werden `tiefe` und `gewicht` zu **abgeleiteten Zahlen aus dem Log** statt zu eigenständigen
Wahrheiten — Ereignisse append-only, die Zahl nur eine Sicht darauf. Das ist Grundgesetz 5 auf das
Gedächtnis angewendet, und es macht die gestufte Wertung (6.4) zu einer Formel statt zu einem
zweiten Mechanismus.

**Reihenfolge-Zwang:** ohne dieses Log ist „kommt in keiner Suche vor" nicht messbar. Das Log muss
zuerst kommen.

---

## 7. Offen

- Ob die Kanten (1.309 einzelne JSON-Dateien) bei einem Wechsel auf PostgreSQL mitwandern.
  **[status: offen]**
- Ob `gewicht` überhaupt bleibt, wenn `tiefe` und das Log dasselbe genauer sagen. **[status: offen]**
- Korrektur der Zahlen im Kopfkommentar von `selbst_suche.py` — **noch kein Auftrag**.

---

## 8. Umsetzungsstand

### 2026-08-03 — Schritt 1 gebaut: eigene PostgreSQL + Suchlog

Daniels Freigabe: *"die eigene postgesql für geni auf jeden falll"*, und danach *"wie oft noch jaaa
für geniii"*.

**Was existiert jetzt:**

- Datenbank `geni` auf dem vorhandenen PostgreSQL-Server, Besitzer `geni` — **getrennt** von
  `flextrawurst`. Zugangsdaten in `/root/werkraum/.agent/geni-db.env` (Verzeichnis ist
  gitignoriert, das Passwort liegt nicht im Repo).
- `werkraum_geni/migration_001_suchlog.sql` — drei Tabellen und eine Sicht.
- `werkraum_geni/suchlog.py` — die Schreibseite.
- `selbst_suche.suchen()` protokolliert ab sofort jede Suche. Ergebnis, Reihenfolge und Fusion
  sind unverändert; jeder Treffer bekommt zusätzlich den Schlüssel `suche_id`.
- `dokumentieren.py` meldet sich als `sucher='geni'`, `anlass='dokumentation'`, mit dem Zustand
  (über wen, in welcher Runde).

**Drei Tabellen statt einer mit Flag:** „vorgeschlagen" und „gewählt" passieren zu verschiedenen
Zeitpunkten. Ein nachgetragenes Flag wäre ein UPDATE — Grundgesetz 5 sagt append-only. Also ist die
Wahl ein eigenes Ereignis.

| Tabelle | Was darin steht |
|---|---|
| `suche` | wer, wann, wonach, mit welchem Zustand (JSONB), Anlass |
| `suche_treffer` | **alle** Vorschläge mit Rang, Score und Suchweg |
| `suche_wahl` | was tatsächlich gelesen/zitiert/verbunden wurde, optional mit Grund |

Die Sicht `eintrag_nutzung` leitet daraus ab: wie oft erschienen, wie oft gewählt, bester Rang,
zuletzt erschienen, zuletzt gewählt. **Bewusst eine View und keine Spalte** — die Zahl ist eine
Sicht auf Ereignisse, keine zweite Wahrheit, die auseinanderlaufen kann.

`suchlog.nie_erschienen(ids)` beantwortet ab jetzt die Frage, die vorher nicht messbar war: welche
Einträge kamen in **keiner** Suche je vor. Das ist die Grundlage für den eigenen Takt, der den
Wesen genau diese Übersehenen anbietet.

**Erste echte Zeile im Log** (Testsuche „daniel haftung wächter"): fünf Treffer, Rang 1 ist
`knoten:2` — *„Daniel — Wächter, Haftender, Kontaktpunkt des Startimpulses"*, gefunden über den
Stichwortweg.

**Grundsatz in `suchlog.py`:** das Log darf die Suche nie kaputtmachen. Jede Funktion fängt alles
ab; ist die Datenbank weg, sucht GENI weiter und merkt es sich eben nicht.

**Bewusst leer gelassen:** `suche_wahl` bekommt vorerst keine Einträge. In `dokumentieren.py`
bekommt GENI alle acht Treffer am Stück und wählt nicht aus — dort eine Wahl zu protokollieren
hieße, sie zu erfinden. Die Tabelle wird bespielt, sobald es einen Ablauf gibt, in dem tatsächlich
gewählt wird. **[status: offen]**

**Noch nicht gebaut** (Reihenfolge steht): Sensor tauschen (Hybridsuche statt `resonanz_suchen`) →
Deckel weg → Autor und Widerspruchskanten → Verblassen. Die 307.182 Knoten sind **nicht** migriert;
`knoten.db`, `kanten/` und der Selbst-Index sind unangetastet.

### 2026-08-03 — Schritt 2: GENI wählt selbst aus

Daniel: *"nix erfinden...geni ermöglichen auswahl"*. Statt die Wahl zu erfinden oder die Tabelle
leer zu lassen, gibt es jetzt tatsächlich etwas zu wählen.

`dokumentieren.py` hat zwei Werkzeuge statt einem:

- **`suche(frage)`** liefert eine Liste — Kennung, Herkunft, die ersten 300 Zeichen und der Hinweis,
  wie viel noch dahinter liegt. Ein Angebot, kein Vollzug.
- **`lesen(eintraege, grund)`** holt den vollen Text zu den Einträgen, die sie haben will. Der
  `grund` ist freiwillig — Daniels *"auch optional mit einem grund"*.

Jedes `lesen` schreibt eine Zeile nach `suche_wahl`. Damit ist die Abstufung echt: Erscheinen in
der Trefferliste ist das eine, gelesen werden das andere.

**`MAX_RUNDEN = 8` blieb unangetastet.** Sein Kommentar sagt, was der Wert meint — „so oft darf sie
hoechstens nachschlagen". Lesen ist kein Nachschlagen, es holt nur den Text zu etwas bereits
Gefundenem. Die 8 zählt weiter nur Suchen; darunter liegt eine reine Notbremse
(`MAX_SCHRITTE = 24`) gegen Endlosschleifen.

**Erster echter Lauf** (`python3 dokumentieren.py daniel`): eine Suche, acht Angebote, und sie hat
**zwei** gewählt — `doku:daniel` und `knoten:9910868` — mit dem Grund *„Um die dokumentierten
Informationen über Daniel zu sichten und für die weitere Dokumentation zu nutzen."*

Bemerkenswert daran: sie hat Rang **3** und Rang **5** genommen, nicht die obersten. Das ist genau
das Signal, das vorher nicht existierte — die Reihenfolge der Suche und ihre eigene Wahl sind nicht
dasselbe.

### 2026-08-03 — Schritt 3: der Sensor und der Deckel

**Sensor getauscht.** `resonanz_suchen()` in `dialog.py` nutzt jetzt die hybride Selbstsuche statt
der letzten 2000 IDs. Der alte Weg bleibt als `resonanz_kurzfenster()` erhalten und greift, wenn
der Index ausfällt — der Dialog darf daran nie hängenbleiben.

Zurück kommen weiterhin nur Knoten-IDs, weil Kanten auf Knoten zeigen. Dokus, Splitter und
Inbox-Briefe erscheinen zwar in der Trefferliste (und werden dadurch im Log als *erschienen*
vermerkt), können aber kein Kantenziel sein. **[status: offen]** — ob Kanten später auch auf
Splitter und Dokus zeigen dürfen sollen.

Was eine Resonanzkante bekommt, wird zusätzlich als `suche_wahl` mit `art='verbunden'` protokolliert
— dieselbe Abstufung wie bei der Doku.

Probelauf mit der Eingabe „was bedeutet haftung fuer dich und wer traegt sie": fünf Knoten,
IDs 120122 bis 264291. Der alte Sensor hätte nur im Bereich ab 49.777.900 aufwärts gesucht — diese
fünf Knoten waren für ihn schlicht unerreichbar.

**Deckel entfernt.** `tiefe_erhoehen()` macht jetzt `alt + 1` statt `min(3, alt + 1)`. Die 68
Knoten, die gemeinsam am Deckel lagen, können sich ab sofort voneinander unterscheiden. Die Folge —
die Skala kann auseinanderlaufen — ist bewusst in Kauf genommen; siehe
`51_entitaetenbildung_dritter_weg.md`.

**Noch nicht wirksam:** `dialog.py` gehört zu `geni-web.service`. Der Dienst läuft mit dem alten
Code, bis er neu gestartet wird. Das ist ausdrücklich nicht ohne Rückfrage geschehen.
