# 🛡️ TIEFENBERGUNG IV — VERIFIER REPORT: BLOCK 2 (V21 CALLGRAPH & MECHANIKBEWEIS)

**Datum:** 2026-08-14  
**Prüfer:** Tiefenbergung IV Independent Verifier  
**Status:** **PASSED / CODEPROVENIENZ VERIFIZIERT**  
**Nodes-Artefakt:** [`evidence/v21/callgraph_nodes.jsonl`](file:///root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_4/evidence/v21/callgraph_nodes.jsonl) (686 Records)  
**Edges-Artefakt:** [`evidence/v21/callgraph_edges.jsonl`](file:///root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_4/evidence/v21/callgraph_edges.jsonl) (2.360 Records)

---

## 1. DURCHGEFÜHRTE INDEPENDENT PRÜFUNGEN

1. **Pickpocket & Stealth Laufzeit-Verifikation:** In [`v21_skill_action_bodies.js`](file:///root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/src/v21_skill_action_bodies.js#L64-L68) existieren `attemptPickpocket21(entityId, approach)` und `returnPickpocket21(entityId)` als ausführbarer Quellcode mit realen Mutationen an `mastery21.inventory`, `rel.disturbance` (+1.5 / +2.2) und `rel.trust` (-0.8 / -0.4).
2. **Exponierung:** Exponiert via `window.FW_TEST.pickpocket21(id, approach)` (Zeile 86).
3. **Callgraph:** 686 Funktionsknoten und 2.360 Aufrufkanten maschinenlesbar erfasst.
4. **Source Ledger Alignment:** Sämtliche 30 V21 JS-Dateien wurden mit unverkürzten SHA-256 Hashes im Source Ledger hinterlegt.

---

## 2. BLOCK-PRÜFURTEIL

- `callgraph_nodes_count`: 686
- `callgraph_edges_count`: 2360
- `reachability_verified`: `DEFINED_TEST_AND_UI` (Pickpocket & Stealth)
- `status`: **`PASS`**
