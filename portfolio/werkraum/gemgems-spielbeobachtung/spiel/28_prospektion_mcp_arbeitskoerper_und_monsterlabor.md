# Prospektionsbefund 28: MCP-Arbeitskörper & Monsterlabor (Wave 3)

**Untersuchter Ort:** `/root/werkraum/_gpt/mcp_arbeitskoerper/`  
**Autor:** Flash (MCP-Arbeitskörper Prospektor, Wave 3)  
**Datum der Prospektion:** 2026-08-13  

---

## 1. ZUSAMMENFASSUNG & PROVENIENZ-URTEIL

1. **Zeitliche Klassifikation:**
   - **Historisches Relikt (26. Juli 2026 – 1. August 2026)**
   - Alle Zeitstempel in den Dateinamen (Claims, UI-Exports, Validierungsberichte, Testläufe) und Skripten datieren exakt aus der Epoche vom **26. Juli 2026 bis 1. August 2026** (Höhepunkt der ChatGPT-Omega / Gesamtatlas VPS-Rettung & Validierung).
   - Es handelt sich **nicht** um spätere Rekonstruktionsakten, sondern um originale operative Artefakte und Testinfrastrukturen dieser Phase.

2. **Funktionale Klassifikation (Spielkörper vs. MCP-Testfeld):**
   - **Striktes Plattform- & MCP-Testfeld (Deterministischer Folterkorpus)**
   - **KEIN** Spielkörper von *Flextrawurst – Das Spiel* (keine Monster-Kreaturen, keine Spieldatenbanken, keine Game-Driver).
   - Das "Omega Monsterlabor" ist eine metaphernreiche Bezeichnung für einen **synthetischen Stresstest-Harness** ("deterministischer Folterkorpus"). Es dient zur automatisierten Prüfung von Dateisystem-Mutationen (Append-only, Rewrite, Rename, Stealth mtime/Size-Tricks, Race Conditions), Session-Isolation, Playwright UI-Exporte und MCP-Routing-Regeln des Gesamtatlas.

---

## 2. STRUCTURAL BREAKDOWN & HARTE PFADE

### A. Hauptverzeichnis & Routing-Grundlage
- **Pfad:** `/root/werkraum/_gpt/mcp_arbeitskoerper/START_HIER.md` (662 Bytes)
  - *Inhalt:* Globale Fallback-Regeln für MCP/GPT-Sessions ohne explizite Projekt-Zuordnung sowie UTC-Zeitstempel-Pflicht (`YYYYMMDDTHHMMSSZ`).

### B. Omega Monsterlabor (`/root/werkraum/_gpt/mcp_arbeitskoerper/omega_monsterlabor/`)
- **Pfad:** `/root/werkraum/_gpt/mcp_arbeitskoerper/omega_monsterlabor/scripts/build_corpus.py` (27.4 KB)
  - *Funktion:* Erstellt synthetischen Dateikosmos mit UUID-Namespaces (`8d0f2fcb-8737-4f7a-9a6f-4ecf0a4db11f`), Base-Timestamps (`T0_NS = 1785391200000000000` -> 30. Juli 2026).
- **Pfad:** `/root/werkraum/_gpt/mcp_arbeitskoerper/omega_monsterlabor/scripts/replay_mutations.py` (7.3 KB)
  - *Funktion:* Replay-System für Mutationstests (`E000_BASELINE` mit `append_only.jsonl`, `rewrite_target.txt`, `same_size_same_mtime.txt`, `race_target.txt`).
- **Pfad:** `/root/werkraum/_gpt/mcp_arbeitskoerper/omega_monsterlabor/scripts/test_driver.py` (21.5 KB)
  - *Funktion:* Unabhängiger Testtreiber gebunden an Session `chatgpt-20260730T063100Z-omega-monsterlabor`.

### C. Koordination (`/root/werkraum/_gpt/mcp_arbeitskoerper/coordination/`)
- **Pfad:** `/root/werkraum/_gpt/mcp_arbeitskoerper/coordination/02_UI_SICHTBARER_GESPRAECHSEXPORT_VERTRAG.md` (303 Bytes)
- **Pfad:** `/root/werkraum/_gpt/mcp_arbeitskoerper/coordination/03_OMEGA_PLAYWRIGHT_JEDER_BAUSCHRITT.json` (1.5 KB)
- **Pfad:** `/root/werkraum/_gpt/mcp_arbeitskoerper/coordination/claims/` (28 JSON-Claims)
  - *Zeitspanne der Claims:* `20260726T161600Z` bis `20260730T172213Z`
  - *Schlüsseldatei:* `20260730T063400Z__gesamtatlas-omega-monsterlabor.json` (2.4 KB)
    - *Rollenbeschreibung:* `"role": "Gesamtatlas-Omega-Monsterlabor und deterministischer Folterkorpus"`
    - *Auftrag:* `"Einen vollständig synthetischen, deterministischen Dateikosmos mit maschinenlesbarer Sollwahrheit, reproduzierbaren Mutationsepochen und unabhängigem Testtreiber bauen."`
- **Unterordner:** `delegations/`, `guards/`, `inbox/`, `tri_session_recovery/`

### D. Validation (`/root/werkraum/_gpt/mcp_arbeitskoerper/validation/`)
- **Pfad:** `/root/werkraum/_gpt/mcp_arbeitskoerper/validation/mcp_gesamtatlas/` (datiert `2026-07-26`)
- **Pfad:** `/root/werkraum/_gpt/mcp_arbeitskoerper/validation/mcp_neutral_default_routing/` (datiert `2026-07-26`)
- **Pfad:** `/root/werkraum/_gpt/mcp_arbeitskoerper/validation/mcp_parallel_reads_home/` (datiert `2026-07-26`)
- **Pfad:** `/root/werkraum/_gpt/mcp_arbeitskoerper/validation/session_continuity/` (datiert `2026-07-27`)

### E. Peer Review (`/root/werkraum/_gpt/mcp_arbeitskoerper/peer_review/`)
- **Pfad:** `/root/werkraum/_gpt/mcp_arbeitskoerper/peer_review/gesamtatlas_omega_realwelt_goldstandard/lean_api_cross_generation/test_cross_generation_playwright.js` (8.3 KB)
- **Pfad:** `/root/werkraum/_gpt/mcp_arbeitskoerper/peer_review/gesamtatlas_omega_realwelt_goldstandard/mcp_read_api_peer_review/scripts/run_case.js` (21.1 KB)

### F. UI Exports (`/root/werkraum/_gpt/mcp_arbeitskoerper/ui_exports/`)
- **Pfad:** `/root/werkraum/_gpt/mcp_arbeitskoerper/ui_exports/raw/mcp_ui_visible/`
  - Enthält **394 Unterverzeichnisse** mit Roh-Exporten von ChatGPT- und Claude-Code-Sessions.
  - *Zeitrahmen:* `20260726T143158Z` bis `20260801T202652Z`.

---

## 3. FAZIT FÜR DEN SPEICHERBELEGS-AKTE 28

Die Prospektion bestätigt eindeutig:
- **Keine Flextrawurst-Spieldaten** im MCP-Arbeitskörper oder Monsterlabor.
- Das Monsterlabor war das Testfeld zur Absicherung des Gesamtatlas Omega gegen unbemerkte Mutationen, Lock-Violations und Race-Conditions im Juli 2026.
- Alle Artefakte sind zeitkritisch authentisch auf den Zeitraum **26. Juli 2026 – 1. August 2026** datiert.
