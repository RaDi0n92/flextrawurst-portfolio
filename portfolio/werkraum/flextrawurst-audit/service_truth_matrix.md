# Dienst-Wahrheitsmatrix — aktueller Messpunkt 2026-09-17

systemd active bedeutet Erreichbarkeit/Loop, nicht automatisch Bewohneraktivitaet. Gegenwartsaussagen sind Messpunkt, keine ewige Wahrheit.

Basis: `daemon_real_writes_report_2026-09-16.json` · Historischer Sep-7-Snapshot: `service_truth_matrix_2026-09-07_HISTORISCH.json`

| Dienst | systemd | Gegenwartsbefund / Abgrenzung |
|---|---|---|
| `codewesen-lg-daemon.service` | active | aktiv spiegelnd: neue entity_thinking_log-Ticks werden checkpointed; kein eigener LLM-Aufruf |
| `cyberling-daemon.service` | active | Hard gate auf entity_slots eingezogen/schlaeft UND entity_profiles.meta.einzug_timestamp. Live eligible_now=0; aktuell keine Cyberling-Writes. |
| `splitter-physik.service` | active | 13.764 Splitter insgesamt, aber 0 nicht-verblasste und 0 aktive. Alter Tamagotchi-Aufruf im aktiven run() abgeschaltet. Event-Konverter betrachtet nur letzte 65s. |
| `similarity-daemon.service` | active | 1.035 Kanten = alle Paare der 46 bekannten Testposts; letzter Updatezeitpunkt aller Kanten 2026-09-07 nach Churn-Fix. Keine laufenden identischen UPDATEs mehr. |
| `themen-cluster.service` | active | Historisch 1 Auto-Thema 'Vertrauen · Vielleicht · Denke', 44/46 Testposts mit thema_id, 46/46 mit raum_id. Aktuell nur 1 Similarity-Kante ueber Cluster-Schwelle; keine neue Struktur. |
| `vorlese-daemon.service` | active | Genau 1 Interessensprofil fuer Schorschel seit 2026-07-22; 0 entity_vorlese_funde. |
| `welt-bruecke.service` | active | Historisch beabsichtigter system.bruecken_sync-Heartbeat bleibt erhalten. 334.428 Alt-Heartbeats. Vor Fix wurden dennoch alle sechs entity_states alle 30s unveraendert neu geschrieben und updated_at gefaelscht. |
| `flarum-monitor.service` | active | Ausgehendes Flarum-Posting bleibt gestoppt; Monitor liest weiter und kann Inbox/Feed-Dateien schreiben. State wurde vor Fix auch ohne Cursor-Aenderung alle 10s neu geschrieben. |
| `innenleben-feeder.service` | active | aktiv; alle sechs feeder_state-Cursor stehen bei Flarum Post-ID 7780 |
| `reibung-bruecke.service` | active | aktiv; Ordering-/Replay-Race aus Recovery-Block repariert und regressionsgetestet |
| `on-demand-beobachtung.service` | active | Controller aktiv; parallel dazu laufen am 2026-09-17 eigenstaendige browser-agent-Prozesse, nicht als Beweis einer reaktivierten Juli-On-Demand-Sitzung |
| `ai-strom-bruecke.service` | active | Kein Flextrawurst-PG-Writer. Lokaler events.jsonl 72.698.732 Bytes, zuletzt 2026-07-30 geaendert. |
| `geni-hoerer.service` | active | In letzten 24h 2.837 neue GENI-Knoten: 2.453 ereignis, 288 prozess_snapshot, 96 system_zustand. Quellen: 2.042 vps_dateisystem, 288 vps_prozesse, 209 codex, 202 claude, 96 vps_system. Letzte IDs ca. 54,1 Mio.; knoten.db ca. 2,57 GB. |
| `welt-api.service` | active | siehe Basisreport |
| `kompoase.service` | active | siehe Basisreport |
| `llama-hauhaucs-hintergrund.service` | active | siehe Basisreport |

## Wichtige Red-Team-Korrekturen

- Der frühere Checkpoint-Schaden von ca. **275 GB ist kein aktueller Bestand**. Er wurde auf Daniels ausdrücklichen Auftrag physisch entfernt. Messung 2026-09-17: `public.checkpoint_blobs` 37 MB, `public.checkpoints` 16 MB, `public.checkpoint_writes` 14 MB.
- `codewesen-lg-daemon.service` ist ein **Checkpoint-Spiegel ohne eigenen LLM-Aufruf**. Am 17.09. kommen wieder neue `browser_agent`-Quellgedanken herein; der Daemon spiegelt sie.
- `innenleben-feeder` ist nicht mehr bei Post 7777/7778 idle: alle sechs Cursor stehen beim Messpunkt auf **7780**.
- Der Reibung-Ordering-/Replay-Randfall ist im Recovery-Block repariert und getestet; er ist nicht mehr OPEN.
- Aktive Browser-Agent-Prozesse am 17.09. sind ein paralleler Lauf. Daraus wird **kein realer Einzug** abgeleitet.

## Historische Großkörper

| Körper | historisch | aktuell / Status |
|---|---:|---|
| `public.checkpoint_blobs` | ca. 275 GB Peak | **37 MB**, Altbestand gelöscht |
| `entity_dom_events` | ~13 GB | Retention OPEN |
| `entity_denkstream` | ~3.7 GB | Retention OPEN |
