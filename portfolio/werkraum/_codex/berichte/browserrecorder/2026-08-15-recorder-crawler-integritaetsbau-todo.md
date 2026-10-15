# Recorder/Crawler Integritätsbau — Todo

Stand: 2026-08-15
Quelle: Vollgutaudit AUD-001 bis AUD-032
Arbeitsregel: Jede Codegruppe bekommt vorher einen Backup-Commit, danach Syntaxcheck, gezielten Test, Graphify-Update falls Code geändert wurde und eine kleine Live-Doku.

## P0 — Versand darf nichts als zugestellt markieren, was nicht bestätigt ist

- [ ] AUD-001: Direktversand durch strict ACK führen.
- [ ] ACK-Tests für empty results, falsche event_id, partial results, HTTP 401, Timeout und Netzwerkabbruch.
- [ ] Server- und Clientfehler mit request_id/event_id/phase klassifizieren.

Abnahme: Kein direkt gesendetes Event wird aus der Queue bzw. dem Pending-Zustand entfernt, bevor genau seine event_id mit ok=true bestätigt ist.

## P1 — Fetch, Upload und Download

- [ ] Gemeinsamer Fetch-Abbruch mit AbortController, Timeout und Body-Limit.
- [ ] Upload-Limits in dekodierten Bytes vereinheitlichen.
- [ ] PDF-Attach-Handler berechnet Bytes, SHA-256 und PDF-Signatur selbst.
- [ ] Queue maxQueueSize wirklich durchsetzen.
- [ ] Queue event_id idempotent machen.
- [ ] Retry mit Versuchsalter, Jitter und sichtbarem Dead-Letter-Status.
- [ ] Downloads über chrome.downloads.onChanged bis complete/interrupt verfolgen.
- [ ] Kritische Downloads mit erwarteten Bytes und SHA-256 rücklesbar machen.

Abnahme: UI unterscheidet started, complete, interrupted und read_back; HTTP 200 allein ist nie Erfolg.

## P1 — Crawler und Bedienwahrheit

- [ ] Universalmodus erhält endliche harte Schutzgrenzen und speichert limitierte Fälle.
- [ ] Manifest-/Asset-Fetches werden als eigene Fetch-Phasen protokolliert oder bewusst abschaltbar.
- [ ] Asset-Fetches erhalten Abort/Byte-Limit/Statusjournal.
- [ ] Manueller Import expandiert standardmäßig nichts.
- [ ] Snapshot und whole_page_verified getrennt anzeigen.
- [ ] Access-/Surface-Gates werden als Befund persistiert statt als generischer Fehler verworfen.
- [ ] Scrollroot und abgeschnittene Links/Assets/HTML werden explizit protokolliert.

Abnahme: Tabwechsel allein erzeugt nichts; ein manueller Import klickt keine fremde UI ohne sichtbare Einzelaktion.

## P1/P2 — Sicherheit und Identität

- [ ] Dynamische innerHTML-Sinks in Sidepanel und Popup entfernen/escapen.
- [ ] Schwache Crawl-Hashes durch vollständige SHA-256-Hashfelder ergänzen.
- [ ] Provider-/DOM-Rollenfallbacks als unsicher markieren und nicht erfinden.
- [ ] Roh-DOM-Kontakte von gespeicherten Beiträgen trennen.
- [ ] IndexedDB-Quoten, Retention, Orphan-Scanner und Löschquittung ergänzen.
- [ ] Multi-Store-Speicherläufe recoveryfähig machen.
- [ ] Workspace-/Screenshot-Fokuswirkung sichtbar ankündigen.

Abnahme: Kein Status „vollständig“ ohne klar definierte Quelle, Scope und Belegstufe.

## Replica v1

- [ ] ReplicaManifest mit source, projections, resources, events, limits, replay, signatures.
- [ ] Artifact-Register für lokale und VPS-Dateien.
- [ ] Tab-Bundle: manifest.json, source.txt, visible.html, screenshot, optional PDF, resources/, events.jsonl.
- [ ] Replayability und fehlende Ressourcen sichtbar markieren.
- [ ] WARC/WACZ/CDXJ-Kompatibilität als nächster interoperabler Schritt prüfen, nicht als Fake-Replay ausgeben.

Abnahme: Projektion, Downloaddatei, gespeicherte VPS-Datei und Replay sind vier getrennte Zustände.

## Live-Abnahme

- [ ] Echte sichtbare Seite mit 2 Snapshots.
- [ ] Tabwechsel ohne Aufnahme.
- [ ] Manueller Import ohne automatische Klicks.
- [ ] absichtlich fehlerhafter ACK.
- [ ] echter Download bis complete plus Hash.
- [ ] lange Seite mit Limit-/Gateszenario.
- [ ] PDF/Markdown/Text 1:1 gegen Quellabschrift.
- [ ] Reload/Service-Worker-Neustart/Recovery.
- [ ] Bericht unter _codex/berichte/browserrecorder/ ergänzen.

## Nicht in diesem Bauauftrag

- Keine neuen Provider ohne Adapter-/Live-Beweis.
- Keine automatische Vollseitenaufnahme im Universalmodus.
- Keine heimliche Linknavigation.
- Keine Löschung fremder oder alter Daten.
- Keine Änderungen an laufenden Welt-/GENI-/Flarum-Systemen.

