# Ereignisspeicher, Infrastruktur-Graph und RAG (Block 3)

Zustand und Logik. Code: `augen_haende_bridge/src/augen_haende_bridge/speicher/`, Tests: `tests/test_speicher.py`.

Zuordnung zu den Goals: Ereignisspeicher G13, Graph und Warteschlange G09 und G12, RAG G15, Augen-Fallback G06.7, Hände und Stop G10.

## 1. Ereignisspeicher (PostgreSQL)

Eigene Datenbank, Adresse in der Umgebungsvariable `BRIDGE_DB_URL`. Die Datenbank `flextrawurst` bleibt unberührt.

Die Tabelle `ereignis` ist append-only: Trigger verbieten UPDATE, DELETE und TRUNCATE, auch für den Besitzer. Das Gleiche gilt für `einbettung`.

Jede Zeile trägt Zeit, Quelle (`protokoll`, `ledger`, `graph`), Art, Agent, Lauf, Knoten, Versuch, Grund, Text und `daten` als JSONB.

`(quelle, extern_id)` ist eindeutig. Dadurch ist das Einlesen wiederholbar: ein zweiter Durchgang schreibt nichts doppelt.

Quellen und ihr Weg in den Speicher:

| Quelle | Weg |
| --- | --- |
| `ereignisse.jsonl` des Starters | `speicher einlesen` (Nachholen) und `Spiegel` (live) |
| Praxis-Ledger `runtime/praxis/*.jsonl` | `speicher einlesen` |
| Knoten und Kanten des Graphen | schreibt der Graph selbst |

Der Spiegel hängt sich an das Ereignisprotokoll und schreibt in einem eigenen Faden. Das Aufzeichnen wartet nie auf die Datenbank.

Fällt die Datenbank aus, bleiben bis zu 20 000 Ereignisse in der Warteschlange und werden mit wachsendem Abstand erneut versucht.

Was darüber hinaus verworfen wird, zählt `Spiegel.verworfen`; es bleibt in `ereignisse.jsonl` und kommt mit `speicher einlesen` nach.

Ohne `BRIDGE_DB_URL` startet kein Spiegel. Der Kapsel-Dienst hängt ihn nur bei gesetzter Variable ein.

Sichten über denselben Strom:

* `lauf_position`: der zuletzt betretene Knoten je Lauf.
* `wartezustand`: wer wartet worauf seit wann (letztes Warte-Ereignis eines Agenten, solange danach kein Ende kam).
* `fehlversuche`: Fehlversuche je Lauf und Knoten seit dem letzten Erfolg oder der letzten Entsperrung.

## 2. Infrastruktur-Graph (LangGraph)

Sechs Knoten in fester Reihenfolge:

    ziel_gebunden → strom_frisch → lease → hand → beleg → urteil → ende

Jeder Knoten hat einen Prüfer, der `(erfüllt, Grund)` liefert. Der Graph verlangt für alle sechs Knoten einen Prüfer; fehlt einer, wird er nicht gebaut.

Es gibt keine Kante, die einen Knoten überspringt. Was der Agent im Knoten tut, bleibt frei, der Knoten verlangt nur seinen Beleg.

Erfüllt: Ereignis `knoten_ok`, Ereignis `kante`, nächster Knoten. Nicht erfüllt: Ereignis `fehlversuch` mit Grund, dann `wartet` mit Grund; der Lauf bleibt am Knoten.

Ein Prüfer, der einen Fehler wirft, zählt als Fehlversuch mit dem Grund `pruefer_fehler:<Typ>`, nie als Erfolg.

Der dritte Fehlversuch an einem Knoten führt in `blockiert` und `diagnose` (Ereignisse `halt`, `diagnose`). Der Halt gilt, bis `entsperren` eine benannte Ursache (mindestens acht Zeichen) bekommt.

Ein inzwischen grüner Prüfer hebt den Halt nicht auf. Nach dem Entsperren geht es am selben Knoten weiter, der Zähler beginnt bei null.

`weiter(lauf, agent)` führt den Lauf von seiner gespeicherten Position bis zum Warten, Halt oder Ende. Die Position steht im Ereignisspeicher, nicht im Speicher des Prozesses.

## 3. Position und Warten für jeden Agenten

`karte(lauf, agent)` liefert: Knoten, Position („3 von 6“), Zustand (`dran`, `wartet`, `halt`, `fertig`), einen Satz in Klartext, Versuche von Maximum, Wartegrund, Wartebeginn und die anderen Wartenden.

`python -m augen_haende_bridge.speicher position <lauf> <agent>` und `... wartet` zeigen das auf der Kommandozeile.

## 4. RAG

Einbettung lokal per ONNX, 384 Dimensionen, Kosinus-Abstand in pgvector (HNSW-Index). Kein Netz, kein Drittanbieter.

Erste Wahl ist `paraphrase-multilingual-MiniLM-L12-v2`, weil die Ereignisse deutsch sind. Ersatz ist `all-MiniLM-L6-v2` (englisch).

Gemessen mit denselben Texten: das englische Modell setzt „Kaffeemaschine leer“ (0,29) so nah an „Urteil ohne aktuelles Bild“ wie den echten Treffer (0,28). Das mehrsprachige trennt klar (0,42 gegen 0,12 und 0,21).

Jeder Vektor trägt seinen Modellnamen; gesucht wird nur im Raum des eigenen Modells.

Nicht eingebettet werden `frame`-Ereignisse. Das sind rund 23 000 von 23 900 Zeilen mit nur 24 verschiedenen Texten („Bild 1632×800“); sie würden jede Frage treffen. Eingebettet werden dadurch 859 Ereignisse.

Der Dokumenttext besteht aus Art, Agent, Knoten, Grund und Text. So trägt auch ein Hände-Ereignis, dessen Text nur „haende“ lautet, seinen Grund (`kein_fenster_ziel`) in den Vektor.

Suche: `speicher suche "<frage>" [-n 5] [--lauf L] [--art A]` verbindet standardmäßig Bedeutung und Wort (Reciprocal Rank Fusion); `--bedeutung` nur Bedeutung, `--wort` nur Volltext über den GIN-Index (ein Treffer-Wort genügt, mehr Treffer-Wörter stehen oben).

Gemessen: „Tastendruck zugestellt, aber der Harness zählt keinen Beleg“ findet mit reiner Bedeutung nur Körperquittungen; mit Wort und Bedeutung steht der Befund aus Lauf p-451034 (Beleg-Stau bei Strg+S) an erster Stelle.

Messung mit den echten Daten: „Gutachter hatte kein frisches Bild und konnte nicht urteilen“ findet an erster Stelle den Befund des Gutachters aus Lauf p-2fa24c (Abstand 0,41). „Strg+S Beleg fehlt“ findet per Volltext die beiden Befunde zu Tasten ohne Beleg aus Lauf p-451034.

## 5. Betrieb

Die Tests laufen gegen eine eingebettete, private PostgreSQL 18 (pgvector 0.8) in einem Temp-Ordner, nie gegen die echte Datenbank.

Die echte Datenbank ist eine eigene PostgreSQL, die nur dem Ereignisspeicher gehört. Daten: `/root/bridge_speicher/pgdata`, Programme und Pakete: `/root/bridge_speicher/venv`, beides außerhalb des Repos.

Start oder Wiederfinden: `sh /root/bridge_speicher/start.sh`. Die Adresse steht in `/root/bridge_speicher/db_url`; `BRIDGE_DB_URL` hat Vorrang.

Der Speicher startet die Datenbank selbst, wenn sie beim Verbinden nicht läuft (nur bei Adresse aus der Datei). `psycopg` wird aus der venv nachgeladen, wenn der Starter im System-Python läuft.

Der Kapsel-Dienst hängt den Spiegel nur ein, wenn sein Ordner unter `runtime/` liegt oder `BRIDGE_DB_URL` gesetzt ist. Tests mit Temp-Ordnern schreiben so nie in die echte Datenbank.

Die Praxis-Ledger-Zeilen gehen über denselben Spiegel live in den Speicher. Die Kennung einer Ledger-Zeile folgt aus ihrem Inhalt; live geschrieben und später aus der Datei eingelesen ergibt keine zweite Zeile.

Befehle: `speicher schema`, `speicher einlesen`, `speicher einbetten`, `speicher suche`, `speicher position`, `speicher wartet` (Aufruf mit `/root/bridge_speicher/venv/bin/python -m augen_haende_bridge.speicher`, Arbeitsordner `augen_haende_bridge`, `PYTHONPATH=src`).

Stand beim Einrichten: 25 194 Ereignisse eingelesen (davon 45 Ledger-Zeilen), 859 eingebettet. Der Spiegel wirkt, sobald der Relay neu gestartet wird (`bash /root/relay-neu.sh`).

Abhängigkeiten: `langgraph`, `psycopg[binary]`, `onnxruntime`, `tokenizers`, `numpy`, `pixeltable-pgserver`. Fehlt eine, überspringen die Tests sich mit Angabe des Grundes.

## 6. Wartezustand im Praxislauf

`PraxisLauf.karte(agent)` enthält jetzt `wartezustand`: `wartet`, `worauf`, `wer`, `seit_s` und `auf_dich` (wer auf diesen Agenten wartet).

Beispiele: in `ansage` wartet der Zuschauer auf die Ansage des Handelnden; in `lesen` warten beide auf Daniels Lesezeit; in `handeln` wartet der Zuschauer auf die Handlung; in `sehen` und `urteil` auf das Urteil mit eigenem frischem Bild; in `zuschauer` wartet der Handelnde auf die Bestätigung; in `klaeren` warten beide aufeinander.

Die Sekunden zählen ab der ersten Beobachtung des Knotens, nicht ab dem Betreten.

## 7. Offen

* Die echten Prüfer (Ziel gebunden, Strom frisch, Lease, Hand, Beleg, Urteil) aus dem Körper an den Graph hängen; heute liefert die Testumgebung sie.
* Lampe „Lauf“ in der Ampel aus Position und Wartezustand.
