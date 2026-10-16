# Dienst-Wahrheitsmatrix — 2026-09-07

Befund ist keine Designfreigabe. OFFEN bleibt OFFEN; keine impliziten Sollregeln.

| Dienst | Modus | Status | Kurzbefund |
|---|---|---|---|
| `codewesen-lg-daemon.service` | autonomer Poller / Checkpoint-Spiegel | **BESTAETIGT_GEFIXT** | Vor Fix lief der Checkpoint-Loop auch ohne neue Quellgedanken weiter und erzeugte 275 GB checkpoint_blobs. Jetzt Invoke nur bei neuem tick_at; drei Folgerunden 0/7, Zähler stabil. |
| `cyberling-daemon.service` | autonomer Bewohnerdaemon | **BESTAETIGT_GATED** | operative=0; letzter historischer Cyberling-Tick 2026-09-06 15:17 UTC |
| `splitter-physik.service` | autonomes Weltorgan, 60s | **BESTAETIGT_MIT_OFFENEM_RAND** | versteckter Vor-Einzug-Tamagotchi-Aufruf wurde entfernt; aktive Physik bleibt. tick_events betrachtet nur letzte 65s. 24049 passende ältere Events stehen splitter_generiert=false und würden bei einem Retro-Replay Weltmaterial erzeugen. |
| `similarity-daemon.service` | autonomer Analysepoller, 120s | **BESTAETIGT_TECHNISCH_GEFIXT** | 1035 Zeilen hatten 13,060,665 UPDATEs, weil jeder 120s-Lauf identische Scores erneut schrieb. UPSERT schreibt jetzt nur bei Score-Aenderung; erster echter Service-Lauf danach: 0 Updates. |
| `themen-cluster.service` | autonomer Clusterpoller, 300s | **BESTAETIGT_IDLE** | laufende Logs melden seit Stunden 0 neue Paare; Themenbestand 1, letzter Themen-Neuzugang 2026-05-26 |
| `vorlese-daemon.service` | autonomer Embedding-Pilot | **BESTAETIGT_PHASE1_IDLE** | genau 1 Interessensprofil = Schorschel, angelegt 2026-07-22; 0 entity_vorlese_funde |
| `welt-bruecke.service` | autonomer Selfmodel→PG-Sync, 30s | **BESTAETIGT_MIT_OFFENER_PROVENIENZ** | 30s-Heartbeat ist historisch beabsichtigt, nicht zufälliger Loop; >306k Alt-Syncs. 619 bridge_sync/system-Events aus zurückgebautem ChatGPT-Fehlversuch bleiben Auditspur. |
| `flarum-monitor.service` | autonomer Flarum-Leser, 10s | **BESTAETIGT_BEABSICHTIGT** | active/enabled; kein Beleg für versehentliche Reaktivierung |
| `innenleben-feeder.service` | autonomer Flarum→Innenleben-Feeder, 300s | **BESTAETIGT_BEABSICHTIGT_AKTUELL_IDLE** | alle sechs Cursor stehen aktuell auf Flarum Post-ID 7777 und änderten sich über Stunden nicht |
| `welt-api.service` | request-driven API | **BESTAETIGT_REQUEST_DRIVEN** | Endpointfamilien werden im Funktionsaudit getrennt geprüft; kein autonomer Hintergrundloop wie bei den Daemons |
| `codewesen-chat.service` | request-driven interaktiver Dienst | **BESTAETIGT_REQUEST_DRIVEN** | active-Status wird nicht als lebender Bewohner-Takt interpretiert |
| `dak-gord-web.service` | request-driven Webdienst | **BESTAETIGT_REQUEST_DRIVEN** | active-Status ist Erreichbarkeit, nicht Bewohneraktivität |

## Historische Großkörper

| Tabelle | Größe | Wachstum | Retention |
|---|---:|---|---|
| `checkpoint_blobs` | 275 GB | BESTAETIGT gestoppt durch codewesen-lg Fix | OFFEN_DESTRUKTIV |
| `entity_dom_events` | 13 GB | aktuell still; Browser-/Beobachtungspfad inaktiv | OFFEN |
| `entity_denkstream` | 3.7 GB | aktuell still; Browser-/Denkstream-Pfade derzeit nicht autonom aktiv | OFFEN |
