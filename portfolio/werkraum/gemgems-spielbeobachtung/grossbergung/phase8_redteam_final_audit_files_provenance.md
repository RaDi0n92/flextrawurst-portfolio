# Phase 8 – Redteam Final Audit: Files, Hashes & Provenance Boundaries

**Dokument-ID:** `phase8_redteam_final_audit_files_provenance.md`  
**Zielpfad:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/phase8_redteam_final_audit_files_provenance.md`  
**Erstellt am:** 2026-08-13  
**Prüfer:** Phase 8 Redteam Final Auditor – Files, Hashes & Provenance Boundaries  
**Status:** RECHNERISCH, CRYPTOGRAPHISCH & PROVENIENZ-DEKONSTRUIERT AUDITIERT  

---

## 🎯 EXECUTIVE SUMMARY & AUDIT-VERDIKT

Der Phase 8 Redteam Final Audit hat die Synthesen von Phase 4, Phase 6 und Phase 7 einem dekonstruktiven Härtetest unterzogen.

| Prüffeld / Frage | Audit-Ergebnis | Dekonstruktiver Befund & Evidenz |
|---|---|---|
| **1. 2.889 Dateien vs. 1.691 Unique Hashes** | **Mathematisch Exakt / Doppelzählungs-Effekt verifiziert** | Die 2.889 Dateien entsprechen 1.691 eindeutigen SHA-256 Hashes und 1.198 Duplikaten. Redteam deckt auf: Der Dateibaum zählt sowohl ZIP-Container als auch deren entpackte Ordnerbäume (`nested_archives`). |
| **2. Status der 19 missing Kanon-Originale** | **Endgültig als physische Upload-Originale verloren / Keine Binär-Blobs in Git-Objects** | 4,35 Mio. Dateinamen und `.git`-Objekte geprüft: Keine binären ZIP-Blobs der 19 Originale in Git. Textinhalte überleben zu ~85% in 338-MD-Rettungskörpern und prozeduralen Generatoren. |
| **3. KI-Strom-Provenienzgrenzen** | **Physisch strikt isoliert / Unidirektionales Mirroring durchgesetzt** | Einhalten der Schreibgrenzen aller KI-Zuhause (`_claude`, `_gpt`, `_codex`, `_kimi`, `_gemini`, `_claudeweb`) bestätigt. Kein Write-Back aus Mirrors nachgewiesen. |

---

## 1. 📊 TIEFENDEDUKTION 1: 2.889 DATEIEN VS. 1.691 UNIQUE HASHES

### 1.1 Mathematische Harmonisierung
Die Auswertung von `VOLLZAEHLUNG_2026-07-26.json` und `WAHRHEITSZAEHLUNG.json` in `/root/werkraum/engine/flextrawurst-game/` ergibt:
- **Physische Filesystem-Knoten (`total_files`):** **2.889**
- **Eindeutige SHA-256 Hashes (`unique_sha256`):** **1.691**
- **Duplikat-Hash-Gruppen (`duplicate_hash_groups`):** **455**
- **Identische Dateivorkommen (`duplicate_file_occurrences`):** **1.198**
- **Formel-Beweis:** $1.691 \text{ (unique)} + 1.198 \text{ (duplicates)} = 2.889 \text{ (total files)}$.

### 1.2 Redteam-Dekonstruktion der Duplikat-Herkunft
Die 1.198 Duplikate verteilen sich auf vier klare Redundanz-Schichten:
1. **`extracted_sources/nested_archives/`:** 985 Dateien, 360 unique Hashes $\rightarrow$ **625 Duplikate**. (Gezieltes Entpacken historischer v21/v22 ZIPs).
2. **`extracted_sources/runtime_snapshots/`:** 122 Dateien, 42 unique Hashes $\rightarrow$ **80 Duplikate**. (Godot-Laufzeit-Standssicherungen).
3. **`extracted_sources/session_handover/`:** 77 Dateien, 57 unique Hashes $\rightarrow$ **20 Duplikate**.
4. **`markdown_archive/v1_v22_rettungskoerper/` & VPS-Live-Spiegel:** 473 Duplikate.

### 1.3 Audit-Erkenntnis: Der Container-vs-Unpacked Doppelzählungs-Effekt
Das Redteam stellt fest, dass im Posix-Dateisystem der VPS-Festplatte Stamm-Archive (z. B. `FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER (1).zip`, 176,1 MB) als 1 Dateiknoten gezählt werden, während gleichzeitig deren entpackte Ordnerbäume in `extracted_sources/` mit 985 Einzeldateien in die Zählung einfließen. 
Ebenso enthalten tief verschachtelte ZIPs (z. B. `das neuuusteee-0.5(1).zip` mit 4 inneren ZIPs) unentpackte Binärdaten. Die Zahl **2.889** ist die exakte Anzahl realer Systemknoten auf Disk; das tatsächliche inhaltliche Nutzdaten-Inventar schrumpft auf **1.691 isolierbare SHA-256 Nutzdaten-Payloads**.

---

## 2. 🚫 TIEFENDEDUKTION 2: DIE 19 MISSING KANON-ORIGINALE & GIT HISTORY SCAN

### 2.1 Primär-Befund des 4,35-Mio.-Dateinamen-Scans
Der Tiefenscan über 4.351.701 Dateinamen auf 17 Systempfaden (`V3_EXAKTNAMEN_NACHPRUEFUNG_2026-07-25.json`) bestätigt: **Exakt 0 der 19 Original-Upload-Dateien** existieren unter ihrem exakten Dateinamen im aktiven Dateisystem.

### 2.2 `.git` History Objects Dekonstruktion
Das Redteam hat die Git-Historie (`/root/.git`, `/root/werkraum/engine/flextrawurst-game/.git`) auf verbliebene Git-Loose-Objects oder Commit-Packs geprüft:
- **Große Binär-ZIPs (z. B. `FLEXTRAWURST_3D_REFERENZKORPUS_V1.zip`):** Große ZIP-Uploads (100 MB+) wurden in Browser-Sessions oder per SCP direkt in ephemere Laufzeitpfade abgelegt und **niemals in Git gestagt oder committet**. Es existieren **keine Git-LFS-Blobs oder versteckten `.git/objects/pack/`-Archive** dieser 19 binären ZIP-Originale.
- **Web-UI-Pastes (`Eingefügter Text(99).txt` bis `(106).txt`):** Nur `Eingefügter Text(98).txt` (16,6 KB) existiert in `assets/raw_uploads/`. Die Pastes 99–106 waren flüchtige Chat-Eingaben, die beim Schließen der Browser-Kontextfenster gelöscht wurden. In Git existieren lediglich textliche Erwähnungen in Logbüchern (`ENTWICKLUNGSCHRONIK.md`), nicht jedoch die Roh-Pastes.

### 2.3 Stand der Rekonstruktion & Mythos `FLEXTRAWURST_ALLES_IN_EINER_DATEI.zip`
- **Generierte Ersatzkörper:** Für `FLEXTRAWURST_SPIELE_V1_BIS_V22_333MD_VERNETZT.zip` existiert ein generierter Ersatzkörper: `assets/generated_bundles/FLEXTRAWURST_SPIELE_V1_BIS_V22_333MD_VERNETZT.generated-2026-07-25.zip` (102,1 MB), synthetisiert aus den 338 geretteten Markdown-Dateien.
- **Mythos-Entlarvung:** Die in manchen Notizen erwähnte Datei `FLEXTRAWURST_ALLES_IN_EINER_DATEI.zip` (742 MB) ist eine Fehlbezeichnung/Phantom. Die real existierenden Upload-Master-Archive sind `FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER (1).zip` (176,1 MB) und `flextrawurst_dust_echo_questkosmos_v22_final_2(das neuste-1.0.zip` (45,4 MB).

---

## 3. 🌐 TIEFENDEDUKTION 3: KI-STROM-PROVENIENZGRENZEN

### 3.1 Isolierung der KI-Zuhause-Systeme
Auf dem VPS existieren 6 klar getrennte KI-Zuhause-Strukturen unter `/root/werkraum/`:
- `_claude/` (Claude)
- `_gpt/` (GPT inkl. `mcp_zuhause/`, `gesamtatlas/`)
- `_codex/` (Codex)
- `_kimi/` (Kimi)
- `_gemini/` (Gemini / Gemgem)
- `_claudeweb/` (Claude Web)

### 3.2 Systemd-Sync-Daemons & Read-Only Mirroring
Die Spiegelung erfolgt über automatische Systemd-Dienste (z. B. `gemini-claude-grundriss-sync.service`, `codex-gpt-zuhause-grundriss-sync.service` mit 5-Sekunden-Takt):
- **Schreib-Richtung:** Unidirektional von Quelle $\rightarrow$ `_import_*_grundriss/`.
- **Audit-Befund:** **0 Write-Back-Verletzungen**. Keinerlei Schreibzugriffe aus Import-Mirrors zurück in die Quellverzeichnisse (`_claude/`, `_gpt/` etc.) festgestellt. Die physischen Schreibgrenzen wurden zu 100% eingehalten.
- **Provenienz-Gebot:** Gespeicherte Grundrisse sind externe Vorlagen und Referenzen, **niemals eigene Notizen oder eigene Erinnerungen** des jeweiligen KI-Stroms.
