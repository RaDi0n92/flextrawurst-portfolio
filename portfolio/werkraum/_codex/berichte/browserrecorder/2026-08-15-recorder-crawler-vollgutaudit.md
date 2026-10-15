# Vollgutaudit: Recorder, Crawler, Downloads, Fetches und VPS-Replikat

Datum: 2026-08-15
Scope: refferenzen/AI-UI-RECORDER-v1.6.5-DIREKT-LADEN/, zugehörige Live-Tests, VPS-Empfänger in tools/action_history/ und dessen systemd/Nginx-Pfad.
Auditart: statische Codeprüfung, vorhandene Live-Belege, lokale Artefaktprüfung und Abgleich mit offiziellen Browser-, Sicherheits- und Webarchiv-Quellen.
Auditstand: Für diesen Bericht wurde kein Code geändert.

## Aussage vorweg

Der Recorder ist nicht wertlos. Er hat inzwischen eine brauchbare sichtbare Aufnahme- und Exportstrecke: ausgewählte sichtbare Seite, gespeicherter Text, Screenshot, HTML-Projektion, Markdown, PDF, lokale Rücklese und ein token-geschützter VPS-Empfänger. Die zuletzt nachgewiesene Sammlungs-PDF wurde als 24-seitige Datei erzeugt; Markdown und PDF wurden gegen gespeicherte Quelltexte verglichen.

Aber „grün“ reicht nicht. Dieses Audit findet einen echten Ereignisverlustpfad, mehrere unbestätigte Downloadpfade, breite Berechtigungen, versteckte Fetches, unbegrenzte Universal-Snapshots, automatische UI-Klicks im manuellen Import, fehlende Ablaufintegrität zwischen IndexedDB-Stores und eine Replikatstrecke, die Projektionen speichert, aber noch kein interoperables Webarchiv mit vollständiger Ressourcen- und Replay-Provenienz ist.

Schweregrade:

- P0: Datenverlust, falsche Vollständigkeitsbehauptung oder unmittelbare Sicherheits-/Integritätsgefahr.
- P1: hoher praktischer Fehler- oder Datenschutzschaden; vor weiterer Vergrößerung des Systems beheben.
- P2: relevante Robustheits-, Bedien- oder Beweislücke.
- P3: Verbesserung, Dokumentation oder langfristige Architektur.

Beweisarten:

- K = Codefund mit Datei und Zeile.
- L = echter Live-/Desktop-Beleg, bereits in den Abnahmeprotokollen abgelegt.
- T = automatischer Test; beweist nur die getestete Fixture und Assertion.
- V = VPS-/Betriebsfund auf diesem System.
- W = externe Primärquelle.

## Datenfluss und Vertrauensgrenzen

    aktive Providerseite
      │ content.js + provider adapter + MutationObserver / sichtbarer Operator
      ├─ Live-Ereignisse ──> background.queueEvent
      │                       ├─ direkte Fetch-POST /api/v1/events
      │                       └─ IndexedDB dak_ai_ui_recorder_queue
      │                                      └─ Batch-Fetch + VPS-ACK
      ├─ manueller/automatischer Import
      │                       └─ sichtbare DOM-/Text-/Beitragsprojektion
      └─ Universal-Crawler
          ├─ scripting.executeScript(crawl_recorder)
          ├─ versteckte owner-manifest-Fetches und same-origin asset-Fetches
          ├─ Screenshot über captureVisibleTab
          └─ IndexedDB dak_web_crawl_recorder
              ├─ jobs
              ├─ pages
              └─ collections
                  ├─ lokale HTML/MD/TXT/PDF-Downloads
                  ├─ native/Chromium-PDF im Workspace
                  └─ optionaler VPS-Export aus Chat-Ereignissen

    VPS Nginx :443
      └─ /chatgpt-browser-recorder/ -> 127.0.0.1:18107
          └─ FastAPI, User root
              └─ /root/werkraum/_gpt/ui_visible_conversations/
                  MANIFEST.json, messages.jsonl, visible_stream.jsonl,
                  capture_gaps.jsonl, 1zu1.md, PAGE.md/PAGE.html,
                  exports/*, ARTIFACTS.jsonl

Die entscheidende Grenze: HTML, Lesetext, Markdown, PDF und Screenshot sind nicht dasselbe Artefakt. Eine schöne Projektion darf nicht als Rohseite, vollständiger Chat, vollständige Ressourcensicherung oder menschliche Sichtung ausgegeben werden.

## Einzelinventar aller relevanten Dateien und Übergaben

| Artefakt | Entstehung | Lokaler Ort/Zustand | Übergabe/VPS | Hauptfehler |
|---|---|---|---|---|
| Live-Ereignis | recorder_core.js | Queue oder flüchtig | POST /api/v1/events | Einzel-ACK kann fehlen |
| Queue-Eintrag | queue_db.js | IndexedDB events | späterer Batch-POST | keine Retention, kein Idempotenzindex |
| sichtbarer DOM-Snapshot | Adapter/recorder_core.js | Eventinhalt/VPS-Primärdatei | als Event | Sanitizing und 4-MiB-Truncation sind Projektionen |
| Chat-Lesetext | Adapter messageBlocks | messages.jsonl | VPS | Rollen-/Identitätsfallbacks |
| Chat-1:1-Markdown | VPS-Projektion | 1zu1.md | VPS-Datei | Projektion, kein DOM-Roharchiv |
| Ereignis-Markdown | VPS-Projektion | 1zu1+events+marker.md | VPS-Datei | reine Sichtbarkeitsbilder bewusst ausgelassen |
| Webseitenbereich | Webadapter/Events | messages.jsonl | VPS | generische Fragmentierung |
| PAGE.md | browser_web_export_data | VPS-Datei/JSON-Antwort | lokaler Download | Text wird serverseitig bereinigt |
| PAGE.html | browser_web_export_data | VPS-Datei/JSON-Antwort | lokaler Download | scriptfreie Projektion, kein Replay |
| LINKS.json | VPS-Webexport | VPS-Datei/JSON-Antwort | lokaler Download | Links nur gelistet, nicht archiviert |
| Crawl-Job | crawl_db.js | IndexedDB jobs | nicht automatisch VPS | mehrere Stores nicht atomar |
| Crawl-Seite | crawl_recorder/background | IndexedDB pages | Workspace/Export | Universal 0-Limits werden Infinity |
| Crawl-Collection | crawl_db.js | IndexedDB collections | Workspace/Export | keine Retention |
| Screenshot | captureVisibleTab | screenshot_data_url | lokale DB/Export | Fokus-/Tab-Rennen |
| Quellabschrift TXT | Workspace-Generator | Browser-Download | lokale Datei | meist nur Download-Start bewiesen |
| Markdown-Sammlung | Workspace-Generator | Browser-Download | lokale Datei | 1:1-Text nur mit Separator bewiesen |
| Sammlungs-HTML | generateWorkspaceHTML | Browser-Download | lokale Datei | Projektion, kein Webarchiv |
| Chromium-PDF | Page.printToPDF | Base64 in IndexedDB | expliziter Download | Seitenzahl teils heuristisch |
| native PDF-Anhang | Datei-Input | Base64 in IndexedDB | kein VPS | Runtime vertraut auf Metadaten |
| Office-PDF/DOCX/ODT | VPS build_office_artifact | VPS exports/* | Base64-Antwort/lokal | lokale Completion fehlt |
| Browser-HTML/MD-VPS-Artefakt | Panel-Base64 | VPS exports/* | POST client-artifact-export | kein späteres Byte-Readback |
| Experiment-Export | experiment_panel/background | VPS-Experimentablage | optional lokal | eigene Limits/Timeouts prüfen |

### Bekannte Zielpfade auf dem VPS

Der Dienst /etc/systemd/system/chatgpt-browser-recorder.service läuft als User root, hat ReadWritePaths=/root/werkraum/_gpt/ui_visible_conversations und bindet intern auf 127.0.0.1:18107. Nginx leitet /chatgpt-browser-recorder/ dorthin weiter, mit client_max_body_size 20m, proxy_read_timeout 90s und proxy_send_timeout 90s. Die sichtbaren Ablageverzeichnisse und Dateien waren auf dem geprüften System root-only.

Das ist kein Beweis für eine Backdoor. Es ist aber eine hohe Vertrauens- und Schadensgrenze: ein Fehler im Empfänger, ein kompromittierter Recorder-Token oder ein Root-Prozess betrifft unmittelbar gespeicherte Gesprächsinhalte.

## Befunde: Versand, ACK, Queue und Fetch

### AUD-001 — P0: Einzelversand verliert Ereignisse bei falschem oder leerem ACK

Beleg: background.js:547-563 ruft postBatch([wrapper]) auf, nimmt response.results[0] optional und markiert den Versand danach als erfolgreich. Die vorhandene strenge Funktion acknowledgedBatch() in background.js:652-664 wird in diesem direkten Pfad nicht aufgerufen.

Wenn der VPS HTTP 200 liefert, aber ok fehlt, results leer ist oder die Event-ID nicht passt, wird das Event nicht in IndexedDB gelegt und delivered: true zurückgegeben. Der VPS kann also ablehnen oder nicht vollständig bestätigen, während der Recorder Verlust als Erfolg meldet.

Mindestfix: auch beim Einzelversand acknowledgedBatch(response,[wrapper]) verwenden; erst danach notifyAck und Erfolgsstatus. Testfälle: 200/empty, 200/wrong-event-id, 207/partial, 401, Timeout, Verbindungsabbruch.

### AUD-002 — P1: Fetches haben überwiegend keine Abbruchfrist

Beleg: background.js:642-650, 823-858 und weitere Export-/Experiment-Fetches verwenden kein AbortController und kein Timeout. Der Crawl hat Script-Wrapper, die Asset-Fetches in crawl_recorder.js selbst aber nicht.

fetch() erfüllt bei HTTP-Fehlern trotzdem ein Response-Promise; der Status muss geprüft werden. Das geschieht beim Eventpfad, aber nicht überall mit begrenzter Body-Lesezeit. Ein hängender Server, Asset-Server oder großer Body kann UI, Service Worker oder Crawl-Lauf binden.

Mindestfix: gemeinsamer fetchWithTimeout() mit AbortSignal, maximaler Response-Größe, Request-ID und klassifizierter Fehlerart; jede Download-/Upload-Strecke separat testen.

### AUD-003 — P1: Queue-Limit ist Konfiguration ohne nachgewiesene Durchsetzung

Beleg: config.js enthält maxQueueSize: 10000; eine Suche in der aktuellen Erweiterung findet keine wirksame Nutzung dieses Wertes. queue_db.js fügt Ereignisse ein, ohne vorab zu begrenzen, zu evakuieren oder einen Dead-Letter-Zustand zu markieren.

Bei fehlendem Token, Serverausfall oder dauerndem ACK-Fehler wächst die Queue bis IndexedDB-/Plattenspeicher-/Browsergrenzen. Das ist kein kontrollierter Datenverlust, sondern ein später harter Quota-Fehler.

### AUD-004 — P1: Queue hat keine Ende-zu-Ende-Idempotenz im Client

Beleg: queue_db.js nutzt queue_id, aber keinen Unique-Index auf event_id. migrateLegacy() schreibt Einträge und entfernt alte Ablage getrennt. Bei Teilfehlern kann ein Retry einen bereits geschriebenen Eintrag nochmals einfügen.

Der VPS dedupliziert anhand event_id innerhalb seiner Primärdatei, aber der Client kann doppelte Queue-Objekte erzeugen und beide verwalten.

Mindestfix: Unique-Index oder transaktionales put-if-absent(event_id); Migration mit eindeutiger Quell-ID und Migrationscursor.

### AUD-005 — P2: Retry ist unendlich, ohne Jitter, Alter oder Dead Letter

Beleg: background.js:693-760 verdoppelt bis 30 Sekunden. Es gibt keine maximale Lebensdauer, keinen Versuchszähler, keinen Jitter und keine sichtbare Dead-Letter-Liste. Bei Fehlern wird weiter versucht, außer bei bekannten Tokenfehlern.

Das erzeugt Lastspitzen nach VPS-Wiederkehr und macht alte oder falsche Aufnahmen schwer kontrollierbar.

### AUD-006 — P2: Token bleibt persistent und alte Queue bleibt absichtlich

Beleg: background.js:588-630 speichert den Schlüssel in chrome.storage.local und nennt ausdrücklich Persistenz über Neustart. Beim Schlüsselwechsel wird die alte Queue nicht automatisch gesendet oder gelöscht. Das ist konservativ gegen ungefragten Versand, braucht aber eine klare UI: welche alten Daten warten, welchem Ursprung gehören sie und darf ein neuer Schlüssel sie übernehmen?

### AUD-007 — P1: Server nimmt JSON-Batches ohne sichtbare Feld- und Summengrenzen

Beleg: FastAPI /api/v1/events liest await request.json() und delegiert an record_browser_events; sichtbar ist nur eine Batchgrenze von 250 Ereignissen. Nginx begrenzt den Request auf 20 MiB, nicht die verschachtelte Ereignisgröße oder die Summe pro Chat.

Ein einzelnes übergroßes Event kann Parsing, Speicher und Projektionen belasten.

## Befunde: Crawling, Fetch, Asset- und Navigationsverhalten

### AUD-008 — P1: Universalmodus setzt 0 auf faktisch unbegrenzt

Beleg: background.js:1218-1229 übergibt im Universalmodus max_html_bytes: 0, inline_asset_limit: 0, inline_total_limit: 0 und max_surface_px: 0. crawl_recorder.js interpretiert diese Werte als Infinity.

Ein sichtbarer Tab kann dadurch eine sehr große DOM-Projektion, viele Assets und riesige Zeichenketten durch executeScript, IndexedDB und Workspace transportieren. Das ist kein kontrolliertes „alles können“, sondern ein potenzieller OOM-, Quota- und IPC-Absturz.

Mindestfix: harte Schutzgrenzen für Bytes, Nodes, Assets und Decode-Speicher; bei Überschreitung vollständiges surface_guard-Artefakt statt fehlendem HTML und generischem Fehler.

### AUD-009 — P1: Capture führt versteckte Netzwerk-Fetches aus

Beleg: offline_export_contract.js:72-99 und crawl_recorder.js entdecken automatisch /.well-known/dak-offline.json bzw. verlinkte Offline-Manifeste. Diese Requests verwenden credentials: omit, verlassen aber trotzdem die Seite und können DNS, Logs, Rate-Limits und Servermetriken auslösen. Asset-Inlining verwendet für same-origin Ressourcen credentials: same-origin.

Das ist keine sichtbare Navigation und kein Beweis für eine bösartige Backdoor. Es ist eine nicht-offensichtliche Nebenwirkung eines Snapshots. Der Bedienvertrag muss zwischen nur sichtbares DOM lesen, Ressourcen fetchen und Manifest prüfen unterscheiden.

### AUD-010 — P1: Legacy-Crawler navigiert und scrollt automatisch außerhalb des Universalvertrags

Beleg: background.js:1149-1184 klickt sichtbare Hash-Links; ab 1280-1348 wird zum Seitenanfang und in 70%-Schritten gescrollt. Der allgemeine Crawler folgt same-origin Links. Runtime-Resume ist weiterhin vorhanden (1660-1678) und kann alte Jobs mit stale visible_tab_id/URL fortsetzen.

Jede UI muss sichtbar unterscheiden: visible_snapshot, guided_manual_scroll oder automatic_crawl. Ein gespeicherter Job darf nicht aus einem anderen Modus automatisch in eine Nutzer-Tabnavigation kippen.

### AUD-011 — P1: Manueller Import expandiert standardmäßig Controls per Klick

Beleg: recorder_core.js:1175-1198 führt item.node.click() aus; startManualImport setzt in recorder_core.js:1521-1527 und 1542-1547 autoExpandEnabled: true.

Ein manueller Start kann Denk-, Quellen-, Artefakt- oder providerabhängige Bereiche öffnen, ohne dass der Operator jedes Öffnen selbst geklickt hat. Fehlschläge werden zwar protokolliert, aber der erste Klick ist bereits eine fremde UI-Aktion.

Mindestfix: Default aus; separate sichtbare Aktion „erkannte Bereiche öffnen“; adaptergebundene Allowlist; jede Aktion mit Vorher-/Nachher-DOMzustand und Ereignis-ID.

### AUD-012 — P1: Asset-Fetch ohne individuellen Timeout und vollständiges Ressourcenjournal

Beleg: crawl_recorder.js iteriert Stylesheets/Medien und ruft fetch(url,{credentials:"same-origin"}) auf. Es gibt keinen eigenen AbortController pro Asset. Listen werden bei 2.000 Assets/5.000 Links gekappt, ohne überall dropped-count/reason zu speichern.

Die Projektion kann „fertig“ aussehen, obwohl Assets fehlen, ein Request hängt oder nur die ersten N Einträge erfasst wurden.

### AUD-013 — P2: Scrollroot ist heuristisch, nicht semantisch

Beleg: crawl_recorder.js:379-413 und Adapter wählen den größten scrollbaren Container. Auf einer Seite mit Sidebar-Feed, Chatliste und Hauptinhalt kann der größte Container falsch sein.

Das erklärt einen Teil der früheren „Hülle ohne Inhalt“-Erfahrung: formal wurde ein sichtbarer Bereich erfasst, aber am falschen Scrollkörper. Benötigt werden Scrollroot-Rolle, Selector/DOM-Hash und sichtbare Bestätigung bei Mehrdeutigkeit.

### AUD-014 — P2: Access-Gate wird teilweise als Capture-Fehler statt als Ergebnis gespeichert

Beleg: crawl_recorder.js kann surface_guard/access_gate liefern; background.js:1104-1105 wirft aber bei fehlendem page.html, und 1300-1310 wirft bei surface_guard. Eine wahrheitsgemäße Grenze kann dadurch als generischer Fehler enden, statt als Befund mit Screenshot, URL, Gate-Typ und nicht umgangener Grenze.

### AUD-015 — P2: Stabilitätshash ist keine belastbare Inhaltsintegrität

Beleg: background.js:1193-1203 hasht nur top, die ersten 50.000 HTML-Zeichen und text_length mit einer 32-bit-FNV-ähnlichen Funktion. Auch crawl_contract.js nutzt diese schwache Chunk-Identität.

Das genügt als schnelle lokale Stabilitätsprobe, nicht als Nachweis, dass vollständige Chunk-Bytes vor/nach dem Warten oder nach Übertragung identisch sind. Für Artefakte existieren bereits SHA-256-Muster; sie müssen auch für Capture-Bytes und Ressourcenmanifest genutzt werden.

### AUD-016 — P2: Universal-Snapshot wird als complete geführt, obwohl er nicht die Seite vollständig erfasst

Beleg: background.js:1251-1266 setzt scan.complete: true, obwohl reached_end: false, transition_count: 0 und evidence_status: visible_viewport_snapshot gesetzt sind. Das ist als Snapshotstatus vertretbar; der Comparator crawl_comparator.js:20-32 meldet die Klasse aber ohne Fehler als okay.

Mindestfix: getrennte Resultate snapshot_ok und whole_page_verified; ok darf bei einem Snapshot nicht als Vollständigkeitsprüfung erscheinen.

## Befunde: Replikat, HTML, Text, Markdown und PDF

### AUD-017 — P1: Es gibt Projektionen, aber noch kein vollständiges Replica

Das System besitzt mehrere nützliche Replikaebenen:

1. sichtbares DOM als bereinigte HTML-Projektion,
2. sichtbarer Text als kanonische Gesprächszeilen,
3. serverseitige 1:1-Markdown-Projektion,
4. scriptfreie PAGE.html/MD-Projektion,
5. Screenshot,
6. Chromium-PDF als Druckprojektion.

Keine Ebene allein ist ein browserunabhängiges Original-Replay. Scripts, Forms, iframes, externe Ressourcen und viele Interaktionszustände werden entfernt oder nur als Metadaten behalten. data-dak-asset-url kann externe Ressourcen zeigen, ohne sie einzubetten.

Das ist nicht falsch, aber Replica muss in der UI aufgelöst sein: source_transcript, reader_projection, visual_projection, resource_bundle und replay_archive sind unterschiedliche Klassen.

### AUD-018 — P1: Manuelles PDF-Anhängen vertraut auf Caller-Metadaten

Beleg: background.js:2072-2104 und Collection-Variante prüfen Data-URL-Präfix und Längenobergrenze, übernehmen aber bytes, sha256 und page_count_estimate aus der Nachricht. Der UI-File-Input berechnet diese Werte, aber der Runtime-Handler selbst ist die Sicherheitsgrenze und berechnet sie nicht neu.

Ein anderer Extension-Kontext oder fehlerhafter Caller kann damit falschen Hash/Bytezahl als Beleg speichern.

Mindestfix: Data-URL dekodieren, Bytezahl und SHA-256 in der Handlergrenze neu berechnen, PDF-Magic-Bytes und Seitenstruktur prüfen; Caller-Metadaten nur als Hinweis.

### AUD-019 — P2: PDF-Seitenzahl ist eine Heuristik

Beleg: estimatePdfPageCount zählt /Type /Page-Vorkommen. Das genügt für den getesteten Chromium-PDF, ist aber keine vollständige PDF-Validierung.

Die UI muss „erkannte Seitenzahl“ sagen, nicht „geprüfte Seitenzahl“, solange kein Parser-/pdfinfo-/qpdf-artiger Validierungsschritt gespeichert wird.

### AUD-020 — P2: Download-Erfolg bedeutet oft nur Download gestartet

Beleg: sidepanel.js:966-990 startet chrome.downloads.download und revoziert die Object-URL nach einer Sekunde. background.js:866-879 gibt beim Webexport Download-ID und Zeichenlänge zurück, wartet aber nicht auf chrome.downloads.onChanged mit state=complete, error und finaler Bytezahl.

Offizielle Chrome-Dokumentation beschreibt onChanged und state=complete als Rückmeldung nach dem Dateischreiben; der Recorder nutzt diese Rückmeldung nicht systematisch.

Mindestfix: Download-Registry mit download_id, erwarteter SHA-256, erwarteter Länge, onChanged-Completion/Interrupted und sichtbarem started|complete|failed.

### AUD-021 — P2: VPS-Bytegleichheit endet vor dem finalen lokalen Dateisystem

Bei Office-Export wird die vom VPS zurückgegebene Base64 dekodiert und gegen vps_artifact.sha256 geprüft (sidepanel.js:1065-1085). Bei Browser-HTML/MD wird der vom VPS gemeldete Artefakthash gegen lokale Bytes geprüft (1015-1050). Das ist belastbar für Antwortbytes.

Es beweist nicht, dass Chrome dieselben Bytes erfolgreich auf Platte geschrieben hat. Dafür braucht es Download-ID, Completion und bei kritischen Abnahmen kontrollierte Wiederöffnung/Hash-Rücklese.

### AUD-022 — P1: Server-Uploadgröße ist nicht überall gleich begrenzt

Der Client-Artefakt-Endpunkt begrenzt serverseitig dekodierte Browserartefakte auf 25 MiB (browser_capture.py:1639-1648), Nginx auf 20 MiB Requestgröße. Office-Exports haben in der geprüften Funktion keine gleich sichtbare Artefaktgrenze. Workspace-PDF prüft im UI 60 MiB, der Runtime-Handler nennt aber 80 MiB Data-URL-Länge statt dekodierter Bytes.

Das sind verschiedene Größenräume: Zeichen, Base64-Zeichen, Requestbytes und dekodierte Bytes. Sie müssen zentral vereinheitlicht werden.

### AUD-023 — P2: Webexport verändert Text und führt Links zurück ins echte Web

browser_web_export_data nutzt strip() für Bereiche und erzeugt Links mit target=_blank. Der Export selbst fetcht die Links nicht; das ist gut. Beim späteren Öffnen beginnt aber wieder das echte Web, nicht das Replika.

Markdown/PAGE.html müssen sichtbar „Textprojektion; Links führen zurück ins Original“ tragen. Für Offline-Wiedergabe braucht es ein Resource-Bundle/WARC- oder WACZ-artiges Format.

## Befunde: Identität, Vollständigkeit und falsche Sicherheit

### AUD-024 — P1: Identitätsfallback kann Beiträge kollidieren oder Rollen vertauschen

recorder_core.js/ChatGPT-Adapter nutzen Provider-ID, DOM-ID und danach Ordinal-/Textkombinationen. chatgpt_adapter.js:314-322 kann bei unbekannter Rolle aus DOM-Heuristiken schließen; web_adapter.js erzeugt schwache 32-bit-IDs aus DOM-Pfad und Textanfang.

Bei virtualisiertem DOM, gleicher Textfolge, geändertem Reasoning oder Provider-Redesign kann ein Beitrag als derselbe oder als falsche Rolle erscheinen. Der VPS hash’t Inhalte, aber ein falscher Identifier entsteht schon vorher.

### AUD-025 — P2: turn_proof ist ein Plausibilitätsbeleg, kein Vollarchivbeweis

turn_proof.js entscheidet aus sichtbaren Status-/DOM-Merkmalen, Nutzertext, Stream, Finalantwort, VPS-ACK und offenen Collapse-Kandidaten. Es fordert nicht vollständig providerseitige Ereignisabdeckung, nicht jede Toolkarte und keinen vollständigen Quellhash der Ausgangsseite.

Die Anzeige muss „sichtbarer Beweis erfüllt“ heißen, nicht allgemein „Gespräch vollständig“, sofern keine strengere Quelle vorhanden ist.

### AUD-026 — P2: Roh-DOM-Metriken werden als Gesprächsmetriken sichtbar

recorder_core.js meldet message_count/recognized_count aus dem aktuell geladenen DOM. Der alte Red-Team-Bericht markiert dies bereits als U03/C23. Die UI sollte DOM-Kontakte, erkannte Beiträge, gespeicherte Beiträge, VPS-bestätigte Beiträge und nicht geladene Beiträge getrennt anzeigen.

### AUD-027 — P2: Comparator bestätigt Struktur, nicht Inhaltstreue

crawl_comparator.js prüft verbotene Tags, IDs, URL, Filtercount, Stable-Chunks und Overlap. Er vergleicht nicht vollständige Source-Text-/HTML-/Screenshot-Hashes gegen ein Original und verlangt keine Mindestzahl an Übergängen. Ein sichtbarer Snapshot kann deshalb strukturell okay sein, obwohl er bewusst nur den aktuellen Viewport darstellt.

## Befunde: Speicher, Transaktionen, XSS und Serverbetrieb

### AUD-028 — P1: IndexedDB speichert sensible Rohdaten ohne Retention/Deletion

queue_db.js und crawl_db.js bieten in der geprüften Schicht keine automatische Ablaufzeit, Größenüberwachung oder Lösch-/Exportquittung. Die Erweiterung besitzt unlimitedStorage. Chrome weist darauf hin, dass lokale Extensiondaten persistent sind und nicht automatisch mit dem Browserverlauf gelöscht werden.

Benötigt werden sichtbare Speichergröße, ältestes Datum, per Collection/Chat löschbare oder deaktivierbare Retention, Export vor Löschung und ein klarer Lokal/VPS-Status.

### AUD-029 — P1: Mehrere innerHTML-Sinks interpolieren Provider-/DOM-Daten

Belegte Stellen sind sidepanel.js:99, 446, 482, 673 und popup.js:48, 133, 156. Besonders provider.label, item.label, Provider-ID, Conversation-ID und unresolved collapsed labels stammen nicht garantiert aus konstantem Code. Das ist ein DOM-XSS-Risiko in einer Erweiterungsoberfläche, deren Inhalte aus fremden Webseiten/Serverantworten kommen können.

Der alte Red-Team-Bericht dokumentiert bereits U29-U31. Alle dynamischen Werte müssen textContent/DOM-Knoten oder eine geprüfte Escape-Funktion verwenden.

### AUD-030 — P2: VPS- und Client-Fehlerpfade sind nicht einheitlich klassifiziert

Einige Funktionen geben ok:false, andere werfen, andere liefern HTTP-200 mit Payload und der direkte Eventpfad wertet das Payload nicht streng genug aus. Durchgehend fehlen request_id, event_id, artifact_id, Versuch, Phase (fetch/decode/store/download/readback) und endgültiger Fehlerstatus.

### AUD-031 — P2: Datei-/DB-Projektionen sind nicht als Gesamtereignis atomar

Der VPS schreibt Primär-JSONL mit Fsync/atomarem Manifest, aber ein Event kann mehrere Dateien berühren: visible_stream.jsonl, messages.jsonl, turns/*.jsonl, Manifest und Projektionen. Der Browser-Crawler schreibt Page, Job und Collection getrennt. Prozessabbruch zwischen diesen Schritten kann Orphans oder Zählerabweichungen erzeugen.

Benötigt wird ein Recovery-Scanner, der Orphans findet und als unvollständig markiert; kein stilles Nachrechnen, das eine neue Wahrheit erfindet.

### AUD-032 — P2: Workspace-Fokus ist eine unerwartete externe UI-Wirkung

runCrawl öffnet/fokussiert am Ende den Collection-Workspace. Der Universalmodus aktiviert für Screenshots außerdem Crawl-Tab und Fenster (background.js:1106-1115). Das ist technisch für captureVisibleTab erklärbar, muss aber als UI-Wirkung angezeigt und vorab angekündigt werden.

## Was ich nicht gefunden habe

In der geprüften Erweiterung fand ich keinen versteckten allgemeinen „alle Tabs lesen und an den VPS senden“-Loop. Der Live-Ereignisversand ist an Autorisierung/Provider-Policy gebunden; Beobachtungs-Snapshots werden bewusst nicht immer remote persistiert. Ich fand auch keinen Beleg, dass der Webexport seine gelisteten Links serverseitig selbst fetcht.

Das ist keine Sicherheitsfreigabe. Nicht vollständig geprüft sind insbesondere alle realen Provider-Versionen mit echten Accounts, ein Lastlauf mit mehreren MiB DOM und tausenden Assets, alle Crash-Zwischenzustände, ein externer VPS außerhalb dieses Hosts, Download-Completion für jede Schaltfläche und vollständiger Ressourcen-Replay aus HTML.

„Kein Befund“ bedeutet hier nur „in diesem Audit nicht gefunden“, nicht „kann nicht existieren“.

## Vergleich mit Fetch-, Sicherheits- und Open-Source-Praxis

### Fetch und Browser-APIs

MDN beschreibt credentials=omit als nie Credentials senden, same-origin als same-origin-only und include als immer mitsenden. Das passt zur Feststellung: Manifest-Probes sind credentiallos, Asset-Fetches können same-origin Cookies verwenden. MDN beschreibt AbortController als Abbruch für Fetch, Response-Body und Streams; diese Schicht fehlt in vielen Recorder-Fetches. Chrome beschreibt downloads.onChanged als Rückmeldung für Zustandsänderungen und state=complete als Zeitpunkt nach dem Schreiben der Datei. Beides gehört in die Beweiskette.

### Chrome-Berechtigungen

Chrome empfiehlt optionale Permissions, wenn die Funktion es erlaubt, und beschreibt Host-Permissions als Zugriff auf URLs, Tabdaten, fetch und Script-Injektion. chrome.debugger kann Tabs instrumentieren, Netzwerkzugriffe beobachten und DOM/CSS verändern. Die Kombination aus all_urls, scripting, tabs, downloads, unlimitedStorage und debugger ist technisch mächtig und muss durch sichtbare Zweckbindung und möglichst optionale Freigaben reduziert werden.

### OWASP-Datei- und Logging-Praxis

OWASP verlangt für Uploads Größenlimits, echte Typprüfung statt Vertrauen in Content-Type, generierte Namen, Autorisierung, Speicherung außerhalb des Webroots und Least-Privilege-Dateirechte. Die aktuelle VPS-Ablage hat gute root-only Modi und sichere Komponenten-Namen, aber Attach-, Office- und Request-Grenzen sind nicht zentral vereinheitlicht.

OWASP warnt außerdem, dass Daten aus einer anderen Vertrauenszone fehlen, verändert, gefälscht oder wiederholt werden können. Recorder-Events sind genau solche Daten: Client-Hash, Timestamp und Rollen sind Hinweise; der VPS muss Schema, Größe, Quellenbindung, Sequenz und Idempotenz prüfen.

### Replikat / Replay / Archivwerkzeuge

- SingleFile speichert eine vollständige Seite als einzelne HTML-Datei, bietet CLI, ausgewählte Tabs und eine explizite Tabelle von Formaten und Grenzen. Es ist ein guter Vergleich für ein sichtbares tabfähiges Offline-Dokument, aber nicht automatisch Gesprächs-/VPS-Provenienz.
- Browsertrix, ArchiveWeb.page und ReplayWeb.page arbeiten mit WARC/WACZ-artigen Archiven, Ressourcen, Logs, Crawl-Einstellungen und Replay. Browsertrix unterscheidet Crawl-Status und QA; WACZ bündelt Daten plus Kontext.
- Die Webrecorder-Spezifikationen nennen WACZ, Signierung/Verifikation und CDXJ ausdrücklich als interoperable Bausteine. Das ist die passende Richtung für ein echtes Replica: Primärresponses, URL, Timestamp, Request-/Response-Metadaten, Hashes, Index, Provenienz und replaybare Ressourcen statt nur bereinigtes HTML plus PDF.
- ArchiveBox ist ein gutes Referenzmuster für mehrere parallele Formate (HTML, PDF, Medien, Screenshots) und klar getrennte Archivmethoden.

## Empfohlene Reihenfolge, ohne unnötigen Ausbau

### Sofort vor weiterem Featurebau

1. AUD-001 beheben und mit absichtlich kaputten ACKs testen.
2. Gemeinsamen Request-/Download-Vertrag einführen: Timeout, Abort, Größenraum, Request-ID, Phase, Fehler, Completion.
3. AUD-029 XSS-Sinks schließen.
4. Attach-Handler rechnet PDF-Größe/Hash selbst und prüft Magic Bytes.
5. Universalmodus erhält harte Schutzgrenzen und speichert Grenzfälle als blocked/limited.
6. autoExpandEnabled im manuellen Import standardmäßig aus.

### Danach: kleiner, echter Qualitätsring

1. Jede Datei bekommt artifact_id, source_id, source_url, captured_at, bytes, sha256, producer, projection_kind, scope und status.
2. Jede lokale Datei wird über downloads.onChanged bis complete verfolgt; kritische Abnahmen öffnen und hashen sie wieder.
3. Jeder Crawl speichert Manifest-Probe, Assetliste, dropped counts, Truncation, Scrollroot, Access-Gate und Snapshot-vs-whole-page-Status.
4. Browser-/Crawl-DB bekommt Quotenanzeige, Retention, Orphan-Scanner und Export-/Löschquittung.
5. Server schreibt ein append-only Artifact-Register mit Hash, Größe, Quelle, Request-ID und kanonischem Datensatzhash.

### Erst danach: Replica v1

Nicht noch mehr HTML, sondern ein bewusst benanntes Format:

    ReplicaManifest
      source: url, tab_id, provider, captured_at, viewport, scroll_root
      projections: dom_html, readable_text, markdown, pdf, screenshot
      resources: url, mime, status, bytes, sha256, stored_path, fetched_by
      events: event_id, sequence, phase, timestamp, ack, source_hash
      limits: applied, dropped, truncated, blocked, reason
      replay: format_version, replayable, missing_resources, interaction_scope
      signatures: manifest_sha256, optional detached signature

Für tabweise Einzelansicht reicht zunächst ein lokales Bundle aus manifest.json, source.txt, visible.html, screenshot.png, optional print.pdf, resources/ und events.jsonl. Für echte Replay-Anforderungen ist die WACZ/WARC/CDXJ-Richtung zu prüfen, statt eine neue proprietäre Base64-Sammlung zu erfinden.

## Abnahme-Matrix für den nächsten Lauf

| Fall | Muss sichtbar sein | Muss persistent rücklesbar sein | Darf nicht behauptet werden |
|---|---|---|---|
| normaler sichtbarer Tab | URL/Tab/Position und Screenshot | source/text/html Hash | vollständige Seite |
| Tabwechsel ohne Klick | keine neue Aufnahme | Snapshotanzahl unverändert | automatische Erweiterung |
| manueller Scroll | operatorisch ausgelöste Schritte | Positionskette und Hashliste | Vollständigkeit ohne Kette |
| Auto-Import | explizit gestarteter Modus, Scrollschritte | Übergänge, Stabilität, ACKs | menschliches Lesen |
| Manifest-/Asset-Fetch | Nebenwirkungsanzeige | URL, credentials mode, Status, Bytes/Hash | „nur gelesen“ |
| HTTP-200 leerer ACK | Fehlerstatus | Event bleibt Queue | zugestellt |
| Download | started, complete oder interrupted | Datei-Hash und Bytes | lokal gespeichert vor Completion |
| PDF | Quelle und Seitenheuristik/Parser | Base64/Datei-Hash | Originalseite 1:1 |
| große Seite | Limit/blocked/limited | Grenzgrund und Teilstatus | unbegrenzt vollständig |
| VPS-Export | Zielpfad/Artifact-ID | Server-Hash plus Readback | nur aus HTTP-200 |
| Replica-Replay | Ressourcen und Grenzen | Manifest/Index/Hashes | scriptfreie Projektion sei Replay |

## Externe Primärquellen

- Chrome: Declare permissions — https://developer.chrome.com/docs/extensions/develop/concepts/declare-permissions
- Chrome: chrome.debugger — https://developer.chrome.com/docs/extensions/reference/api/debugger
- Chrome: chrome.downloads — https://developer.chrome.com/docs/extensions/reference/api/downloads
- Chrome: chrome.storage — https://developer.chrome.com/docs/extensions/reference/api/storage
- MDN: Using the Fetch API — https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- MDN: AbortController — https://developer.mozilla.org/en-US/docs/Web/API/AbortController
- OWASP: File Upload Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
- OWASP: Logging Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- OWASP: SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- Webrecorder specifications — https://github.com/webrecorder/specs
- Browsertrix documentation — https://docs.browsertrix.com/
- Webrecorder project family — https://github.com/webrecorder
- SingleFile — https://github.com/gildas-lormeau/SingleFile
- ArchiveBox — https://github.com/ArchiveBox/ArchiveBox
- ArchiveWeb.page — https://github.com/webrecorder/archiveweb.page
- ReplayWeb.page — https://github.com/webrecorder/replayweb.page

## Schlussbefund

Der nächste richtige Schritt ist kein neuer Exportknopf. Es ist ein kleiner Integritätsring um die vorhandenen Wege: striktes ACK, Fetch-Abbruch, Download-Completion, einheitliche Byte-/Hash-Verträge, keine automatische Expansion im manuellen Modus, harte Universal-Limits und ein eindeutig benanntes Replica-Format.

Bis diese Punkte geschlossen sind, lautet die ehrliche Statussprache:

> sichtbar aufgenommen / persistent gespeichert / als Projektion exportiert ist belegbar.
>
> vollständig repliziert, lokal erfolgreich gespeichert, replaybar oder vollständig zugestellt ist je nach Pfad noch nicht allgemein belegbar.

