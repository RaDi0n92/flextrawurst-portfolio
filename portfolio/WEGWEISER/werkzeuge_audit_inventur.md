# Wegweiser: Werkzeuge, Audit, Tests, Inventur

Quelle: Docstrings, READMEs. Keine Deutung.

## Audit (`werkraum/flextrawurst-audit/`, 19 Dateien)

| Datei | Inhalt |
|---|---|
| `CHAT_UEBERGABE_2026-09-16.md` | Übergabe an einen neuen Chat |
| `claude_gegencheck_2026-09-17.md` | "Claude-Gegencheck von ChatGPTs Vor-Einzug-Audit" |
| `service_truth_matrix.md` (+ `_2026-09-07_HISTORISCH`) | Dienst-Wahrheitsmatrix (Messpunkt 2026-09-17) |
| `tab_semantic_audit.md`, `build_tab_semantic_*.py`, `check_live_43_tabs_*.py`, `verify_surface.py` | 43-Tab-Semantik-/Crawl-Audit der Surface |
| `*_regression_*.py`, `update_audit_state_*.py`, `mark_testmaterial_*`, `fix_testbestand_*` | Regressionstests und Zustands-Updates (Browser-Agent-Shutdown, Diskurs-Sichtbarkeit, Innenleben-LLM-Retry, Reibung-Ordering …) |

## Inventur (`inventur/`, 36 Dateien)

`01_was_ist_das.md` … `28_admin.md`: pro Surface-Tab ein Ist-Zustand-Dokument (WAS IST DAS, LEITSTAND, WELTSTROM, RÄUME, DISKURS,
WESEN, DENKEN, SCREENS, KOMPOASE, BLASEN, MENSCHEN, SCHLAF, EINSICHT, SUCHE, ARCHÄOLOGIE, CYBERLINGE, SPLITTER, ZITATE, SCHATTEN,
GRUPPEN, SYSTEME, WISSEN, GESETZE, FORSCHUNG, PARTNER, GORDSLIDER, MEINEWELT, ADMIN), `inventur_index.md`, Screenshot-Skripte.

## Werkzeuge

| Ort | Inhalt |
|---|---|
| `werkraum/datei_wandler/` | README: Web-Service für gemischte Datei-Exporte (Offline-HTML, Markdown oder ZIP; Inhalte werden escaped, nicht ausgeführt); `app.py`, `tests/` |
| `werkraum/tools/vps_mcp/` | MCP-Server (`vps_mcp_server.py`) mit Atlas-, Harness- und Workflow-Graphen; `tests/` |
| `werkraum/tools/gesamtatlas_*/` | Atlas-Bausteine (Dateikörper, Omega, Organismus, World, Endproduktbeweis, Ursprungsring) |
| `werkraum/tools/action_history/` | Browser-Aufnahmen/Timeline/Office-Export |
| `werkraum/tools/3d_pipeline/`, `run_3d_pipeline_validation.py`, `kosmos_registrar.py`, `populate_kosmos*.py`, `harvest_kosmos_assets.py` | 3D-Pipeline und Kosmos-Katalog |
| `werkraum/tools/config_waechter.py` (+ Baseline-JSON) | Konfigurations-Wächter |
| `werkraum/tools/flarum_export.py`, `flarum_exporter/flarum_export.py` | Read-only-Export des Flarum-Forums (nur GET; HTML + JSON + Index + ZIP) |
| `werkraum/uploads/windows_diktat*.py`, `tools/windows_diktat*.py` | Windows-Diktat-Hilfen |
| `werkraum/scripts/` | `flarum_sync.py`, Versionsarchiv-Skripte für GENI-Dokumentation, `journal.sh`, `eval_mcp_fast.sh` |
| `kompoase/server.py` | kleiner Server (KompOase-Datenfeed) |
| `werkraum/app/` | kleine FastAPI-App (`main.py`, `models.py`, `security.py`, `services.py`) |

## Tests

`werkraum/tests/` (25 Dateien: Rechte-/Auth-Integration, Archivzugriff, Lieder-Agent-Verträge …), `flextrawurst/tests/`
(Ring-Tests, Surface-Tests), `zensi/test_*.py`, `werkraum/welt/test_*.py`.
