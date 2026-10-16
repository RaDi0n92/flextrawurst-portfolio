# Claude-Gegencheck von ChatGPTs Vor-Einzug-Audit

Begonnen 2026-09-17, ca. 11:30 Uhr. Daniel hat ChatGPTs Abschlussmeldung zum
"Vor-Einzug-Audit" (`flextrawurst-audit/`) an mich weitergegeben und gebeten,
das selbst und eigenständig gegenzuprüfen — nicht als Fork, sondern direkt von
mir, in Etappen, nicht in einem Rutsch. ChatGPT selbst hat in seiner Antwort an
Daniel dieselbe Erwartung formuliert: keine einzelne Stichprobe reicht, es soll
systematisch gegen echte Belege (Dateien, DB-Stand, Live-Zustand) geprüft
werden, nicht nur meinem eigenen Abschlusstext geglaubt werden.

Diese Datei dokumentiert rückwirkend, was ich bis zu ihrer Anlage bereits
geprüft habe, und wächst danach mit jedem weiteren geprüften Punkt weiter —
selbes Prinzip wie die Statusliste in `_claude/karte/2026-09-17-chatgpt-verlauf-mit-daniel.md`.

Methode: keine Annahme aus dem Audit-Text selbst übernehmen, sondern die
konkret zitierte Belegdatei öffnen und/oder eine unabhängige Live-Prüfung
fahren (SQL-Query gegen die echte Postgres-DB, `curl` gegen die echte
ausgelieferte Seite, `sha256sum`/`grep` gegen die echte Datei) und das
Ergebnis mit der Behauptung abgleichen.

## Geprüfte Behauptungen

### 1. "45 Posts"-Drift im Leitstand

Behauptung (`audit_state.json`, Abschnitt `bestaetigt`): der Live-Surface-Text
zeigt weiterhin "45 Posts", während `ftw_posts` tatsächlich 46/46 public und
46/46 `ist_voreinzug` enthält. Ein Fix-Patch (`source_diskurs_count_truth_2026-09-17.patch`)
liegt vor, wurde aber laut Audit bewusst nicht live angewendet.

Prüfung: `grep -rn "45 Posts" flextrawurst-audit/` — Treffer in mehreren
gebauten/quarantänisierten Surface-Dateien und im Patch selbst, real und
konsistent. Live-DB-Query gegen die echte Postgres-DB:

```
SELECT COUNT(*) AS gesamt, COUNT(*) FILTER (WHERE sichtbarkeit='public') AS public,
       COUNT(*) FILTER (WHERE ist_voreinzug) AS voreinzug FROM ftw_posts;
```

Ergebnis: `gesamt=46, public=46, voreinzug=46`. Exakt wie behauptet.

**Status: bestätigt.**

### 2. Der zitierte "State-Hash"

ChatGPTs Abschlussnachricht an Daniel zitierte einen Hash
(`6b136c148ee28823c88b1f5f8071cc37091557228260465f0cfe0c48876f5e87`) als Beleg
für den geprüften Zustand. Eine erste Textsuche (`grep`) über den gesamten
Audit-Ordner fand diesen String nirgends als Text — offene Frage zunächst.

Prüfung: `sha256sum /root/werkraum/flextrawurst-audit/audit_state.json`.

Ergebnis: exakt derselbe Hash. Der zitierte Wert ist der SHA256 der Datei
selbst (Stand ihres letzten Schreibzeitpunkts), nicht ein Hash, der als Text
irgendwo in ihr steht — eine Datei kann ihren eigenen Hash nicht enthalten,
deshalb lief die ursprüngliche Textsuche ins Leere.

**Status: bestätigt, ursprüngliche Grep-Suche war die falsche Methode, nicht
die Behauptung falsch.**

### 3. Foreign-Key-Integrität

Behauptung: "106/106 PostgreSQL-Foreign-Keys wurden direkt über pg_constraint
inklusive realer Orphan-Joins geprüft; alle 106 sind validiert, 0 Orphans."

Prüfung, live gegen die echte DB:

```
SELECT COUNT(*) FROM pg_constraint WHERE contype='f';                        -- 106
SELECT COUNT(*) FROM pg_constraint WHERE contype='f' AND NOT convalidated;    -- 0
```

**Status: bestätigt, exakt.**

### 4. Schlafbrief-Bestand

Behauptung: "11919 Zeilen, 0 echte ist_selbstbrief=true."

Prüfung, live gegen die echte DB:

```
SELECT COUNT(*) AS gesamt, COUNT(*) FILTER (WHERE ist_selbstbrief) AS selbstbriefe FROM schlafbriefe;
```

Ergebnis: `gesamt=11919, selbstbriefe=0`. Exakt wie behauptet.

**Status: bestätigt, exakt.**

### 5. Router-Scan (301 Method+Pfad-Kombinationen, 0 Dubletten)

Behauptung: "Ein statischer Router-Scan findet 301 Method+Pfad-Kombinationen,
301 eindeutig, 0 Dubletten."

Prüfung: eigener Grep-Scan direkt über `welt/api.py`
(`@app.<methode>("<pfad>")`-Muster, dedupliziert und auf Duplikate geprüft).

Ergebnis: 301 eindeutige Treffer, 0 doppelte. Exakt wie behauptet.

**Status: bestätigt, exakt.** (Hinweis: eigener Scan nur auf `api.py`
begrenzt, nicht denselben internen Scan-Code des Audits nachvollzogen —
Ergebnis stimmt trotzdem exakt überein.)

### 6. 43 Navigationstabs live ausgeliefert

Behauptung: die live ausgelieferte Public-Surface hat 43 Navigationstabs mit
43 eindeutigen Ziel-Views.

Prüfung: `curl https://flextrawurst.de/` und Zählung der `data-view="..."`-
Attribute im tatsächlich ausgelieferten HTML.

Ergebnis: 43 eindeutige `data-view`-Einträge. Exakt wie behauptet. (Erster
Prüfversuch mit falschem Grep-Muster fand 0 bzw. 2 Treffer — eigener
Methodenfehler, kein Audit-Fehler, korrigiert durch genaueres Nachsehen in der
echten HTML-Struktur.)

**Status: bestätigt, exakt.**

### 7. Die 16 Teil-Report-Hashes in audit_state.json

Jeder Eintrag mit `path`+`sha256` in `audit_state.json` (16 Stück:
`db_integrity_report`, `recovery_report`, `tabs_backend_truth_report`,
`public_source_architecture_report`, `seo_geo_report`, `final_redteam_report`,
`innenleben_llm_retry_report`, `selfbrief_recovery_report`,
`post_relation_ownership_report`, `splitter_recovery_cutover_report`,
`similarity_themen_testdiskurs_report`, `bruecken_provenienz_voreinzug_report`,
`historical_observation_retention_report`,
`browser_agent_shutdown_recovery_report`, `post_final_truth_drift_report`,
`voreinzug_restbestand_report`) per eigenem Python-Skript gegen die echte
Datei auf der Platte geprüft (`sha256sum` gegen den eingetragenen Wert).

Ergebnis: alle 16 stimmen exakt überein.

**Status: bestätigt, 16/16.**

### 8. Eingebetteter Code-Hash: browser_agent.py

Der Report `browser_agent_shutdown_recovery_truth_2026-09-17.json` nennt
`browser_agent_sha256=1f9a21574bca58da5c73b1020297c2a4b53e0a38993f2132fa03543d27395267`.
Der echte, aktuelle Hash von `welt/browser_agent.py` stimmt damit NICHT
überein.

Grund geprüft statt einfach hingenommen: der Report ist vom 2026-09-17 08:42
Uhr. `git log -- welt/browser_agent.py` zeigt meinen letzten Commit an dieser
Datei um 11:27 Uhr desselben Tages — Teil meiner eigenen Arbeit heute Nacht am
Einzug-Vault-Zeitstempel-Fix, klar nach dem Audit-Snapshot. Die Abweichung ist
erwartete Drift durch meine eigene spätere Änderung, kein Fehler im Audit.

Der zweite geprüfte Code-Hash im selben Kontext
(`source_diskurs_count_truth_2026-09-17.patch`, Punkt 1 oben) stimmte exakt.

**Status: erklärt, kein Audit-Fehler.**

### 9. KompOase-Beobachtungsereignisse (16.912) und die zwei 410-Gone-Endpunkte

Behauptung: "Die rund 16.912 oeffentlichen actor_type=system-Beobachtungs-
ereignisse aus KompOase entstanden ungeplant vor Freigabe. Seit 2026-08-12
kamen keine neuen hinzu. Die beiden historischen Backend-Schreibendpunkte
liefern jetzt hart 410 Gone."

Erste Suche nach `event_type ILIKE '%kompoase%'` fand nichts — falsches
Suchmuster, nicht falsche Behauptung. Tatsächliche Quelle gefunden über
`welt/api.py:3811` (`/zwischenraum/splitter/verschmelzung`) und
`welt/api.py:3829` (`/zwischenraum/splitter/entstehung`) — beide seit
2026-08-12 hart auf `HTTPException(status_code=410, detail="KompOase-
Beobachtungslogging ist abgeschaltet")` gesetzt, mit Docstring "Historischer
Vorfreigabe-Pfad. Seit 2026-08-12 abgeschaltet." Die zugehörigen historischen
Event-Typen sind `splitter.verschmolzen` und `splitter.entstanden`.

Live-DB-Query:

```
SELECT event_type, COUNT(*), MAX(created_at) FROM events
WHERE actor_type='system' AND event_type IN ('splitter.verschmolzen','splitter.entstanden')
GROUP BY event_type;
```

Ergebnis: `splitter.verschmolzen` 11497 Zeilen, letzter Eintrag 2026-08-12
18:54:20 UTC; `splitter.entstanden` 5415 Zeilen, letzter Eintrag 2026-08-12
18:54:24 UTC. Summe: 11497 + 5415 = **16912** — exakt die behauptete Zahl,
exakt dasselbe Datum, zwei Endpunkte exakt gefunden.

**Status: bestätigt, exakt — nach Korrektur der eigenen Suchmethode.**

### 10. GENI-Web-Fix ("war objektiv defekt")

Behauptung: `dialog.py` endete mitten im HTML direkt nach `<body>`, wodurch
`geni-web.service` 254203 mal neu startete; der fehlende Tail wurde
rekonstruiert.

Prüfung: `systemctl show geni-web.service` → `NRestarts=0`, `ActiveState=active`,
`SubState=running`. `dialog.py` ist jetzt 2718 Zeilen lang und endet mit einem
vollständigen `uvicorn.run(...)`-Aufruf, nicht mitten im HTML. Live-Check
`curl https://flextrawurst.de/zensi/` → `HTTP 200`.

Auffällig: derselbe Fehlermuster-Typ (Datei mitten im Schreiben abgeschnitten,
Crashloop mit fünf- bis sechsstelligen Neustartzahlen), den ich unabhängig
heute Nacht bei `live_export.py` und `fragen_api.py` selbst gefunden und
repariert habe — drei unabhängige Funde desselben Bugs an drei verschiedenen
Dateien, von zwei verschiedenen AI-Strömen entdeckt.

**Status: bestätigt.**

### 11. Die restlichen 9 eingebetteten Zweit-Hashes

Alle übrigen `<name>_sha256`-Felder aus den Reports gegen die echten Dateien
geprüft:

- `api_sha256` (`welt/api.py`) — exakt bestätigt.
- `hauhau_client_sha256` (`hauhau_client.py`, liegt direkt in `/root/werkraum/`,
  nicht unter `welt/`) — exakt bestätigt.
- `llm_scheduler_sha256` (`llm_scheduler.py`, ebenfalls direkt in
  `/root/werkraum/`) — exakt bestätigt.
- `themen_cluster_sha256` (`welt/themen_cluster.py`) — exakt bestätigt.
- `splitter_daemon_sha256` (`welt/splitter_daemon.py`) — exakt bestätigt.
- `entity_takt_sha256` (`welt/entity_takt.py`) — exakt bestätigt.
- `nodes_sha256` (`innenleben/nodes.py`) — exakt bestätigt.
- `regression_sha256` (`flextrawurst-audit/innenleben_llm_retry_regression_2026-09-17.py`)
  — exakt bestätigt.
- `bruecke_sha256` — erster Versuch gegen `welt/reibung_bruecke.py` (falsche
  Dateivermutung meinerseits, ein anderes System: "Reibungsgewebe" statt
  "Bruecken-Provenienz"/`system.bruecken_sync`-Heartbeat) schlug fehl. Über
  `grep -rl bruecken_sync` die echte Quelle gefunden: `welt/bruecke.py`.
  Dagegen geprüft: exakt bestätigt.

**Status: 9/9 bestätigt** (eine davon erst nach Korrektur der eigenen
Dateivermutung, kein Audit-Fehler).

### 12. substance_sediments, weltklima.tick, wesen.vernachlaessigt

Drei Zahlen auf einmal live gegen die DB geprüft:

- `substance_sediments`-Tabelle: behauptet 279585 — `SELECT COUNT(*)`: exakt
  279585.
- `event_type='weltklima.tick'`: behauptet 15072 — exakt 15072.
- `event_type='wesen.vernachlaessigt'`: behauptet 13937, seit dem Entfernen
  des `tick_tamagotchi()`-Aufrufs am 2026-09-07 eingefroren — Query liefert
  exakt 13937, `MAX(created_at)` = 2026-09-07 02:46:47 UTC, seither kein
  einziger neuer Eintrag.

**Status: 3/3 bestätigt, exakt.**

### 13. Heartbeats: 334.963 nameless_ai/system/live_world + 619 bridge_sync

Erster Versuch mit falscher Feldkombination (`event_type='live_world'`) fand
nichts. Über den vollständigen Report
(`bruecken_provenienz_voreinzug_report_2026-09-17.json`) die echten Felder
gefunden: `event_type='system.bruecken_sync'`, unterschieden nach
`actor_type`/`actor_id`/`origin_type`.

Live-Query:
```
SELECT actor_type, actor_id, origin_type, COUNT(*) FROM events
WHERE event_type='system.bruecken_sync' GROUP BY 1,2,3;
```

Ergebnis: `actor_type=nameless_ai, actor_id=system` → 334963 (Report nennt
"historische_nameless_ai_system_live_world: 334963" — exakt gleich).
`actor_type=system, actor_id=system, origin_type=bridge_sync` → exakt 619
(Report: "system_system_bridge_sync": 619 vor dem Fix — exakt gleich).
Zusätzlich `actor_type=system, actor_id=system, origin_type=live_world` → 482,
das sind die neuen Heartbeats seit dem dokumentierten Fix-Restart um 08:13:15,
konsistent mit "seither läuft der reparierte Heartbeat weiter".

**Status: bestätigt, exakt — nach Korrektur der eigenen Feldvermutung.**

### 14. SEO/GEO: 134/134 Sitemap-URLs

Behauptung: 134 Sitemap-URLs, alle erreichbar, keine kaputt.

Unabhängig geprüft (nicht nur die Audit-eigene `seo_geo_validation_2026-09-17.json`
gelesen, sondern die echte, live ausgelieferte `sitemap.xml` abgerufen):
`curl https://flextrawurst.de/sitemap.xml` → 134 `<loc>`-Einträge, 134
eindeutig. Stichprobe von 8 zufällig gezogenen URLs quer durchs Sitemap
(`/wesen/...`, `/wissen/...`) einzeln per `curl` abgerufen — alle 8 mit
HTTP 200.

**Status: bestätigt (Live-Stichprobe, nicht Vollscan aller 134).**

### 15. 711 Chroma-Reflexionsartefakte, 679 leer/unklar

Behauptung, mit genauer Scan-Methode dokumentiert in
`innenleben_llm_retry_fix_2026-09-17.json`: "Read-only Chroma-Scan:
metadata.is_reflection=true und Dokument leer oder enthaelt 'Reflexion
unklar'." Aufschlüsselung pro Wesen mitgeliefert.

Erster eigener Versuch (grobe Heuristik über Metadata-Feld `typ`/`type` und
Dokumenttext) ging daneben (242/0) — falsche Feldnamen geraten. Zweiter
Versuch mit der im Report exakt dokumentierten Methode
(`metadata.is_reflection is True`, Dokument leer oder enthält "Reflexion
unklar") über alle Chroma-Collections lief zunächst auf 934/692 — zu hoch,
weil zusätzlich die alten `memories_namelessAI_*`-Legacy-Collections
mitgezählt wurden, die der Audit nicht einschließt.

Auf die sieben aktuellen Wesen-Collections eingeschränkt
(`memories_Schorschel`, `memories_Resonanzknoten`, `memories_F3INSCHM3CK3R`,
`memories_traeumerlie`, `memories_R1ZZ1`, `memories_jumpa`,
`memories_dak_gord-system`):

| Wesen | eigene Zaehlung (total/leer) | Audit (total/leer) |
|---|---|---|
| Schorschel | 149/142 | 149/142 |
| Resonanzknoten | 125/120 | 125/120 |
| F3INSCHM3CK3R | 149/142 | 149/142 |
| träumerlie | 1/1 | 1/1 |
| R1ZZ1 | 142/135 | 142/135 |
| jumpa | 145/139 | 145/139 |
| dak+gord-system | 0/0 | 0/0 |

Summe: 711 total, 679 leer/unklar — exakt wie behauptet, auf jedes einzelne
Wesen genau.

**Status: bestätigt, exakt — nach zwei eigenen Methodenkorrekturen (falsches
Feld, dann falscher Collection-Scope).**

## Zwischenfazit, Stand dieser Datei

29 von 29 geprüften Behauptungen/Werten bestätigt. Mehrere eigene
Methodenfehler unterwegs (falsches Grep-Muster, falsche Dateivermutung,
falsches Metadatenfeld, falscher Collection-Scope) — jedes Mal lag der Fehler
bei der eigenen ersten Abfrage, nie bei der geprüften Behauptung selbst; nach
Korrektur traf jede einzelne Zahl exakt zu, bis auf `browser_agent.py`, das
als erklärte, erwartete Drift durch meine eigene spätere Arbeit nach dem
Audit-Snapshot eingeordnet ist.

Noch nicht geprüft: die konkreten Report-internen Detailclaims, die noch
keine eigene Live-Query bekommen haben (z.B. die 27 anonym sichtbaren vs. 43
Admin-Tabs im Detail, die 115 WISSEN-Ressourcen einzeln, die 7 GESETZE-Texte
im DE→EN→DE-Roundtrip, die 301 Routen einzeln gegen echte HTTP-Aufrufe statt
nur gegen den Quellcode). Die bisher geprüfte Stichprobe deckt die
zahlenmäßig markantesten/am leichtesten falsifizierbaren Behauptungen ab und
zeigt durchgängig: keine einzige geprüfte Zahl war erfunden, beschönigt oder
falsch.
