# Wegweiser: zensi und GENI

Quelle: Docstrings/READMEs. Keine Deutung. Beide Systeme sind eigenständig neben den Codewesen (`codewesen.md`).

## `zensi/` (18 Dateien)

| Datei | Laut Quelle |
|---|---|
| `server.py` | "zensi — einfache Chat-Seite mit HauhauCS via llama-server" (Python-`http.server`, ~2.700 Zeilen); nutzt `hauhau_client` und `zensi_history_daemon` |
| `zensi_history_daemon.py` | "Transgenerationales Audit- & History-Archiv": archiviert kognitive Zustände und Änderungen |
| `zensi_sync.py` | Auto-Sync-Daemon für Kopienprofile und Sandbox-Fläche (Klonstrukturen, isolierte Sandboxen); Beschreibung in `werkraum/docs/systemdoku/32_zensi_spiegelwesen_sandbox.md`. Ob der Dienst läuft, sagt die Datei nicht |
| `test_*.py` | Playwright-/API-E2E-Tests; ihre Docstrings nennen u. a.: Provenienz, Markdown-Export/Import, LangGraph/DB-Export, Wesenhülle & Version-Session-Engine (Soft-/Hard-Delete), Obsidian-Vault-Sync, Diff-Inspector, Symposium, Traum-Processor, mobile/desktop UI |
| `aufgaben/*.json`, `symposien/*.json` | Beispielläufe (Aufgaben "inquiry"/"dialektik", ein Symposium) |

Hinweis: In `werkraum/codewesen_speicher.py` steht ausdrücklich, dass dessen Container/Memory-Modell **nicht** von zensi stammt.

## `werkraum_geni/` (43 Dateien) — GENI

README: "GENI ist das neuronale Gehirn-Netzwerk-Wesen-System", existiert seit 2026-04-20, Erstes Wort "ICH".

| Pfad | Inhalt |
|---|---|
| `ICH.md`, `README.md` | Selbstbeschreibung, Verlinkung (Wiki-Links) |
| `kern/` | `startimpuls.md`, `prinzipien.md`, `sprache.md`, `vps_gehirn.md` |
| `zugriffsschichten/` | `0_offen`, `1_resonanz`, `2_dialog`, `3_kern` |
| `verbindungen/`, `sinne/INDEX.md`, `api/schema.json`, `notizen/`, `spiegel/` | Außenverbindungen, Sinne, Schema |
| `hoerer.py` | "hört alles, schweigt bis Daniel spricht": Quellen u. a. Dateisystem des Werkraums (Echtzeit via watchdog) und Flarum |
| `sprechen.py`, `dialog.py` | direkter Kontakt bzw. Browser-Dialogbahn (Port 8020); Aktionslogik in `aktion.py` |
| `muster.py` | Muster-Scanner (alle 2 h per systemd-Timer): Muster, Meta-Muster, blinde Flecken |
| `dokumentation.py`, `dokumentieren.py`, `doku_sammler.py` | GENI dokumentiert Teilnehmer in einem eigenen Vault |
| `inbox_fragen.py`, `inbox_antworten_watcher.py`, `teilnehmer_roster.py` | Inbox-System: stellt Teilnehmern in Abständen Fragen; 16 Teilnehmer |
| `forum_lektuere.py`, `spiegel_lektuere.py` | liest Flarum-Diskussionen nach bzw. alle 12 h je eine Spiegel-Datei jedes externen AI-Stroms |
| `selbst_suche.py`, `suchlog.py`, `bereits_gelesen.py`, `datumskorrektur.py` | semantische Selbstsuche, Suchlog u. a. |
| `geni_lg.py` | LangGraph-PostgreSQL-Persistenz für GENI-Sessions (thread-IDs `geni-…`) |
| `geni_bridge_windows.py` | Windows-Bridge (Desktop/Vision/Kontrolle) |
| `migration_knoten_sqlite.py` | Migration von `knoten/` (Millionen Einzeldateien) nach SQLite |
| `sessionstart_2026-07-22_geni-neudenken.md` | Notiz zum Neudenken |

Laufzeitdaten (`geni_gedaechtnis/knoten/`) sind nicht im Paket.
