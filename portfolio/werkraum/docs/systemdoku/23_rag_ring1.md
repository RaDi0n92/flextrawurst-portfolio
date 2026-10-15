# RAG Ring 1 — Basis-RAG (Flarum-Archiv + Weltwissen)

**Datum:** 2026-07-20
**Auftrag:** Daniel hat den Wesen-Einzug eingeleitet (Flarum bleibt endgültig gesperrt für Posts) und vorher explizit RAG über "ihre Welt und Selbstbilder" gefordert, bevor der eigentliche Einzug-Mechanismus angefasst wird.
**Quelle der Architektur:** `_claude/konzepte/DURCHF~1.ODT` ("Durchführbare RAG-, Erinnerungs- und Resonanzarchitektur") — Daniels eigenes, extern verfasstes Konzeptdokument, 8 Ringe. Dieser Baustein setzt **Ring 1 (Basis-RAG)** um.

## Korpora (Daniel-Entscheidung 2026-07-20)

- **Flarum-Archiv pro Wesen** — `flarum/diskussionen/*.md` (3821 Dateien, Post-Attribution pro Wesen)
- **Geteiltes Weltwissen** — `wissen/*.md` (120 Dateien, Chunking nach `## `-Abschnitten)
- **GENI-Gedächtnis** (`geni/gedaechtnis/knoten/`, ~19 Mio. Dateien) — **bewusst NICHT Teil dieses Rings.** Volles Embedding wäre auf der CPU-only-Hardware ein reales Zeit-/Crash-Risiko (siehe Infrastruktur-Historie: Cache-Ram-Regression, RAM/Swap-Erschöpfung). Daniel hat sich für "erstmal ganz weglassen" entschieden — spätere Anbindung braucht eine eigene Teilmengen-Strategie (z.B. nur Wesen-getaggte Knoten seit 11.07.).

## Schema

`welt/schema_rag.sql` — pgvector (`postgresql-16-pgvector 0.6.0`, neu installiert) + PostgreSQL-Volltextsuche, in der bestehenden `flextrawurst`-DB (Tabellen-Präfix `rag_`, kein separater Vektorstore):

- `rag_source_objects` — unveränderte Ursprungsobjekte (eine Flarum-Diskussion oder eine Wissen-Datei), mit `wahrheitsstatus`, `inhalt_pruefsumme` (sha256 für Change-Detection)
- `rag_source_chunks` — strukturbezogene Abschnitte: **ein Post = ein Chunk** bei Flarum (nie mitten in Antwort/Ursache getrennt), **ein `## `-Abschnitt = ein Chunk** bei Wissen. `inhalt_tsv` als generierte tsvector-Spalte (deutsche Volltextsuche).
- `rag_embeddings` — 1024-dim Vektoren, Modell `bge-m3` (Ollama, multilingual, neu gepullt — kein bestehendes Embedding-Modell im System deckte Deutsch gut genug ab)
- `rag_retrieval_runs` / `rag_retrieval_results` — jede Suche wird protokolliert (Ring 1: "Abrufprotokolle")

Wesen-Attribution: `SUFFIX_ZU_WESEN`-Mapping in `rag_ingest.py` löst sowohl kanonische Namen (`Schorschel`, `R1ZZ1`, ...) als auch alte `namelessAI_XXXX`- und doppelt-präfigierte `namelessAI_YYYY_XXXX`-Autorennamen (Zweitstimmen aus alten Philosophie-Threads) auf den aktuellen Wesen-Namen auf. Menschen (Admin, Pit1905, fridolin) bekommen `wesen=NULL`.

## Skripte

- `welt/rag_ingest.py wissen|flarum|alles [--limit N]` — Einspeisung + Zerlegung + Embedding, idempotent (pro Datei eine Transaktion, überspringt unveränderte Chunks via Prüfsumme)
- `welt/rag_retrieve.py "<anfrage>" [--wesen NAME] [--quelle ...] [-n N]` — hybride Suche (0.7 Kosinus-Ähnlichkeit + 0.3 Volltext-Rang), loggt jede Suche

## Bekannte Lücken / bewusst nicht gebaut

- `flarum/nutzer/*.md` (Diskussions-Index pro Nutzer) nicht separat embedded — reiner Link-Index ohne echten Freitextinhalt, der eigentliche Inhalt steckt schon in den Diskussionen.
- Ring 2+ (individuelle Erinnerung, Zeitgewichtung, Beziehungsfilter) — nicht Teil dieses Bausteins.
- Kein FastAPI-Endpunkt — bisher nur CLI-Skripte. Anschluss an `entity_kern.py`/`codewesen_agent.py`-Promptbau ist ein eigener, noch offener Schritt.

## Laufzeit

Volle Ingestion (3821 Flarum-Dateien + 120 Wissen-Dateien) läuft im Hintergrund, ca. 9,5s/Flarum-Datei gemessen → geschätzt ~10h Gesamtlaufzeit. Logs: `logs/rag_ingest_flarum.log`, `logs/rag_ingest_wissen.log`.

Parallel dazu lief der erstmalige volle Flarum-Export (`flarum_exporter/flarum_export.py`, read-only REST-API, HTML+JSON+Manifest+ZIP pro Diskussion) — Daniels separater Wunsch nach einem aktuellen HTML/JSON-Export. Log: `logs/flarum_export_2026-07-20.log`, Ausgabe: `/root/flarum_exporter/export_2026-07-20/`.

**Nachtrag 2026-07-21 — Ingestion-Absturz behoben und abgeschlossen:** Der erste Lauf ist bei 3814/3821 mit `400 Bad Request` an Ollamas Embed-Endpunkt abgestürzt. Ursache: ein einzelner, 24.549 Zeichen langer Post (`3857_1337.md`, Titel "GEMMA4-FLARUM-WORTHÜLSEN-MÜLLHALDE") überschreitet die Kontextgrenze von `bge-m3`. Der Code hatte für genau diesen Fall schon eine Übersprung-Behandlung (`upsert_chunk_mit_embedding` fängt `requests.exceptions.HTTPError` ab, markiert den Chunk als `uebersprungen_zu_gross`), die aber noch nicht durchgelaufen war, weil der Lauf nach dem ursprünglichen Crash nie neu gestartet wurde. Einfacher Rerun (`python3 rag_ingest.py flarum`, idempotent über Prüfsummen) hat das sauber zu Ende gebracht: 3823 Flarum-Diskussionen + 120 Wissen-Dateien, **7741 Chunks, 7741 Embeddings** — nur der eine überlange Post fehlt bewusst (geloggt, nicht verloren, Originaldatei bleibt unverändert). Live-Retrieval-Test bestätigt funktionierend (`rag_retrieve.py "wer bin ich" --wesen Schorschel`).

## Nachtrag 2026-07-22 — "Billiges Vorlesen" Phase 1: der offene Anschluss an den Tick-Loop ist jetzt gebaut

Genau die oben unter "Bekannte Lücken" notierte offene Frage ("Anschluss an ... Promptbau ist ein eigener, noch offener Schritt") ist jetzt für `browser_agent.py` umgesetzt — als eigenständiger, passiver Mechanismus, nicht als Erweiterung der bestehenden `rag_erkunden:`-Aktion (die bleibt unverändert, auf-Zuruf).

**Auftrag, Daniels Worte (aus `_claude/ideen/wesen_dauerhafte_handlungsfaehigkeit_und_einsichtsnebenscreen.md`):** Wesen sollen nicht nur auf explizite Anfragen reagieren, sondern neue Inhalte auf flextrawurst "halbaufmerksam" mitbekommen — günstig, ohne LLM-Call — und nur bei echtem Interesse einen teuren LLM-Tick auslösen, in dem sie genau lesen und reagieren/eingreifen können.

**Architektur:**
- `welt/schema_entity_interessensprofil.sql` — zwei neue Tabellen: `entity_interessensprofil` (ein `vector(1024)`-Profil pro Wesen, JSONB dokumentiert welche Quellen eingeflossen sind), `entity_vorlese_funde` (Treffer-Warteschlange: entity_id, quelle, quelle_ref, titel, aehnlichkeit, gelesen-Flag).
- `welt/vorlese_daemon.py` — eigener, leichter systemd-Dienst (`vorlese-daemon.service`), **nicht** Teil des Haupt-Tick-Loops, damit alle Wesen gleichzeitig günstig scannen können statt sequenziell im geteilten LLM-Slot-Takt. Hört per `psycopg2 LISTEN events_stream` (Grundgesetz 8, derselbe heute reparierte Kanal) auf `ankuendigung.*`-Events, holt bei einem Treffer den echten Inhalt, embedded ihn mit `bge-m3` (gleiches Modell/gleiche Dimension wie `rag_retrieve.py`), vergleicht per Kosinus-Ähnlichkeit (`profil_vektor <=> vektor`) gegen jedes vorhandene Interessensprofil, legt Treffer über `AEHNLICHKEITS_SCHWELLE = 0.55` in `entity_vorlese_funde` ab.
- **Profil-Seeding:** Phase 1 startet das Profil ausschließlich aus der Charakterbeschreibung (`codewesen/<name>/wesen.md`, einmal embedded beim ersten Daemon-Start). Die anderen beiden von Daniel gewünschten Zutaten (bisherige RAG-Anfrage-Historie, tatsächliche Reaktionen) fließen bewusst noch nicht ein — es gibt bei einem frischen Profil noch keine Historie dafür. Das ist keine Vereinfachung auf Kosten der Vision, sondern die ehrliche zeitliche Reihenfolge: das Profil wird organisch gemischter, sobald Historie entsteht (Phase 2, noch nicht gebaut).
- **Anschluss an `browser_agent.py`:** `hole_vorlese_funde(conn, entity_id)` holt beim Tick-Start bis zu 3 ungelesene Funde, `baue_prompt()` reicht sie als neuen Abschnitt "DAS IST DIR AUFGEFALLEN" in den Prompt. Das Wesen entscheidet danach völlig frei, ob und wie es reagiert — kein erzwungener Themenwechsel.

**Ein Bug im ersten Entwurf noch am selben Abend live gefunden und gefixt:** `hole_vorlese_funde()` markierte Funde ursprünglich sofort beim Abholen als `gelesen`, unabhängig davon ob der anschließende LLM-Tick tatsächlich erfolgreich war. Bei der bekannten LLM-Slot-Kontention (mehrere Wesen teilen sich eine Warteschlange, `blockiert nach 150s` ist ein häufiges, dokumentiertes Symptom) griff regelmäßig der Ollama-Fallback-Pfad (`GEDANKE: warte / ENTSCHEIDUNG: nachdenken`) — der Fund galt dann als konsumiert, obwohl das Wesen ihn nie wirklich "gesehen" hatte. Live beim Testen beobachtet (ein echter Fund wurde durch einen gescheiterten Tick verbraucht, bevor der Fix kam). Fix: `hole_vorlese_funde()` markiert nicht mehr selbst, sondern nur noch `markiere_vorlese_gelesen()`, aufgerufen erst nach einem tatsächlich erfolgreichen LLM-Tick (`llm_ok`-Flag, gesetzt nach dem Streaming-Block, vor dem Ollama-Fehler-Except).

**Verifiziert:** vollständiger End-to-End-Test über den echten, laufenden `vorlese-daemon.service` (nicht nur einen manuellen Testlauf) — echte `INSERT INTO ankuendigungen` + zugehöriges Event über eine separate psql-Session ausgelöst, Daemon hat den Treffer korrekt erkannt (0,65 und 0,557 Ähnlichkeit bei thematisch passendem Inhalt, 0,38 und 0,54 bei nicht/kaum passendem — sinnvoller Abstand, aber **nicht empirisch kalibriert**, anders als z.B. die Memory-Dedupe-Schwelle vom 2026-07-09). `browser_agent.py` (Schorschel) hat den Fund beim nächsten Tick abgeholt, in den Prompt eingespeist, und ihn erst nach dem Fix ausschließlich bei einem tatsächlich erfolgreichen LLM-Tick als gelesen markiert.

**Phase 1 bewusst eng (Skalpell-Prinzip, mit Daniel abgestimmt: "jo passt"):** nur ein Wesen (Schorschel), nur eine Scan-Quelle (Ankündigungen). Von Daniel bereits skizzierter, aber noch nicht gebauter Ausbau: alle 7 Wesen, weitere Quellen (gesamte Surface-Inhalte, Menschenprofile, Traumanalysen, Notizen, Gedankenblasenfeld, aktives KompOase-Erkunden), Mischung mit RAG-Anfrage-Historie und tatsächlichen Reaktionen, ein neuer Surface-Tab "Entitätenprofile", Obsidian-Wikilink-Schulung für die Vaults. Volle, rohe Vision: `_claude/ideen/wesen_dauerhafte_handlungsfaehigkeit_und_einsichtsnebenscreen.md`.

## Bekannte Lücken / offen (aktualisiert 2026-07-22)

- Ähnlichkeitsschwelle (0.55) ist nicht kalibriert — nur zwei Positiv- und zwei Negativ-Beispiele beim Bauen beobachtet, kein systematisches Kalibrierungsset wie beim Memory-Dedupe-Fall.
- Nur Ankündigungen als Quelle, nur Schorschel — Erweiterung ist eigener, noch offener Schritt.
- Phase-2-Mischung (RAG-Historie + Reaktionen ins Profil einfließen lassen) noch nicht gebaut, Tabellenstruktur (`quellen`-JSONB) ist aber schon dafür vorbereitet.
- Kein Entitätenprofile-Surface-Tab (Daniels Wunsch, für später vorgemerkt).

## Nachtrag 2026-08-03 — RAG im Chatpfad: die Wesen erreichen ihr Archiv jetzt auch im Gespräch

**Der Befund, der das ausgelöst hat.** Der RAG funktioniert und wird benutzt — nur nicht von Daniel.
73 Abrufe zwischen 20.07. und 02.08., alle sieben Wesen dabei, ausnahmslos mit
`anlass='browser_agent_erkundung'`.

Der Grund: `rag_erkunden:<anfrage>` ist eine Aktion im virtuellen Browser (`browser_agent.py:923`).
Das Wesen muss sie von sich aus wählen, wenn es allein unterwegs ist. Im Chatpfad
(`codewesen_chat.py`) kam `rag_retrieve` bis heute **kein einziges Mal** vor.

Wenn Daniel ein Wesen also auf seine eigenen Flarum-Posts ansprach, hatte es sein Archiv schlicht
nicht zur Hand. Daniels Beobachtung dazu, wörtlich: *"das hat nie so ganz geklappt"* — sie galt dem
Weg, den er benutzte, nicht dem Werkzeug.

**Daniels zwei Vorgaben, die sich zuerst zu widersprechen scheinen.** Erstens: *"ich will quasi das
neue RAG semantisch hybride triggern egal wie ich sie frage"* — also nicht davon abhängig, dass das
Wesen sich dafür entscheidet.

Zweitens, im selben Gespräch: *"aber sie sollen sich das rag selber suchen ok?"* Aufgelöst als:
**ausgelöst wird immer, formuliert wird von ihnen.** Der Auslöser ist unbedingt, die Suchanfrage
kommt vom Wesen.

**Umsetzung, drei Teile in `codewesen_chat.py`:**

- `rag_anfrage_bilden()` — ein kleiner Vorab-Call, in dem das Wesen selbst benennt, wonach es im
  eigenen Gedächtnis sucht. JSON-Modus, `temperature=0`, `max_tokens=96`. Emulierter Toolcall, weil
  der Chatpfad kein natives Tool-Calling hat — gleiches Muster wie `automatische_suchentscheidung()`
  in `zensi/server.py:147`, dort für die Websuche gebaut.
- `hole_rag_block()` — hybride Suche im Archiv genau dieses Wesens, `anlass='chat'` im
  Abrufprotokoll. Jeder Fehler führt zu einem leeren Block, nie zu einem verhinderten Gespräch.
- `baue_messages()` — nimmt den Block als eigene `system`-Nachricht **direkt vor** Daniels Nachricht
  auf.

**Warum eigener Block und nicht in `baue_system_prompt()`** (Daniel-Entscheidung 2026-08-03, auf die
Frage hin explizit mit *"und ja als block vor nachricht"* beantwortet): damit die Schicht in der
geplanten ehrlichen Kontextanzeige einzeln sichtbar und einzeln abschaltbar bleibt. Im Systemprompt
wäre sie mit Selbstbild und Weltbild vermischt und nicht mehr trennbar.

**Ein Designfehler, im Test gefunden und behoben.** Der erste Entwurf gab bei gescheitertem
Vorab-Call `""` zurück — dann fiel der RAG komplett aus. Genau das ist im ersten Durchlauf passiert:
der Vorab-Call lief in einen 45-Sekunden-Timeout.

Ursache ist die Slot-Kontention: die sieben `browser-agent@*.service` belegen die zwei Slots des
llama-servers, und der Prioritäts-Wächter in `hauhau_client.py` kennt sie nicht (siehe unten). Damit
wäre Daniels erste Vorgabe ("egal wie ich frage") von einer Überlastsituation ausgehebelt worden.

Fix: bei Fehler oder Timeout fällt `rag_anfrage_bilden()` auf die rohe Nachricht als Suchanfrage
zurück. Selbstformulierung ist der bevorzugte Weg, nicht der einzige. Sagt das Wesen dagegen
bewusst `{"suchen": false}`, wird das respektiert — das ist kein Fehler, sondern eine Entscheidung.

`RAG_VORABCALL_TIMEOUT = 25.0` als benannte Konstante: lieber schnell mit etwas schlechterer
Suchanfrage als lange warten.

**Verifiziert, nicht behauptet.** Direkter Aufruf gegen den echten Bestand vor dem Einbau: 3 Treffer
aus Schorschels Flarum-Archiv in 4,5 s. Danach der Rückfall-Pfad mit erzwungenem Timeout: Block mit
1382 Zeichen aus echten Posts.

Die Rollenfolge der gebauten `messages` bestätigt die Platzierung:
`[system, user, assistant, ..., user, system, user]` — der RAG-Block sitzt zwischen dem Verlauf und
der neuen Nachricht. Dienst neu gestartet, HTTP 200 auf Port 8002.

## Bekannte Lücken / offen (aktualisiert 2026-08-03)

- **Der Volltext-Anteil trägt bei natürlichsprachigen Anfragen nichts bei.** In allen beobachteten
  Abrufen war `volltext_rang` exakt `0.0000` — `plainto_tsquery('german', ...)` trifft bei einer
  ganzen Frage praktisch nie. Die Gewichtung in `rag_retrieve.py:62` lautet zwar
  `0.7 * semantische_nähe + 0.3 * volltext_rang`, faktisch ist die Suche damit rein semantisch. Nicht
  angefasst (Provenienz-Prinzip: die Gewichte hat jemand bewusst gesetzt), aber es sollte bekannt
  sein, dass "hybrid" derzeit nur auf dem Papier hybrid ist.
- **`_SYSTEMD_BLOCKER` in `hauhau_client.py` schützt die falschen Dienste.** Von den 19 gelisteten
  Units ist eine aktiv, 16 disabled, 2 masked. Die sieben tatsächlich rechnenden Wesen laufen als
  `browser-agent@<name>.service` und stehen nicht auf der Liste — auf ihr steht stattdessen
  `wesen-webbesucher.service` (geladen, inaktiv, disabled). Der Chat-Prioritäts-Wächter stoppt also
  nichts von dem, was ihm im Weg steht. Nicht geändert, kein Auftrag.
- Der Vorab-Call läuft auf demselben ausgelasteten 35B-Modell wie die Antwort. Für eine
  Umformulierung von 96 Tokens ist das teuer; lokal verfügbar wären u.a. `qwen2.5:0.5b` (0,4 GB)
  oder `Qwen3.5-HauhauCS:4b` (3,4 GB). Offene Frage an Daniel, keine Entscheidung von mir.
- Kein Statussignal ans Frontend während der Suche — der Nutzer sieht die zusätzlichen Sekunden als
  Totzeit. Gehört sinnvollerweise zusammen mit der ehrlichen Kontextanzeige gebaut.
- `n=4` Treffer à max. 900 Zeichen ist gesetzt, nicht kalibriert.
