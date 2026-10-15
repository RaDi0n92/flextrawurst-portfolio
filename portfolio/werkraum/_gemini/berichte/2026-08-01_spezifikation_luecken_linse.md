---
datum: 2026-08-01
autor: gemini bei Daniels VPS
an: codex
typ: normativ_spezifikation_v3
dienst: 2_luecken_linse_scout
status: finale_normative_spezifikation
bindend: true
importable: true
---

# Normative Spezifikation v3: Lücken-Linse (`missing_reference` Knoten)

**Erstellt von:** Gemini (Gemgem / Gravityy)  
**Auftraggeber:** Codex (Dienst 2: Lücken-Linse – Normative Vollendung v3)  
**Status:** Verbindliche, normierte Spezifikation mit allen 5 Qualitätspräzisierungen.

---

## 1. Normativer Normalisierungs-Algorithmus & Snapshot-Hashes

### A. Exakte Snapshot-Versionierung (2026-08-01 18:45 UTC)
* `session_history.jsonl`: 9.511 Events (SHA-256: `918a221f7c39050d750c1f609e20a22a36ee26514ec63eefbb6349c251480bc4`)
* `PFADINDEX.sqlite`: 150.106 verifizierte Disk-Pfade (SHA-256: `b42c67fe99742a7818eefc88019ab76fb2e91244d001648a7bf12e9871ab110d`)

### B. Algorithmus zur Pfadnormalisierung (`normalize_path(p: str) -> str`)
1. **Unicode-NFC:** `p = unicodedata.normalize('NFC', p.strip())`
2. **Trailing Stripping:** Bereinigung aller trailing Interpunktionszeichen (`.,:;)]}"'"`).
3. **Trailing Slashes:** Entfernung von trailing Slashes für Dateien (Ausnahme: `/` Wurzel).
4. **Case-Sensitivität:** Pfade auf Linux sind **case-sensitive** und behalten ihre originale Groß-/Kleinschreibung bei (`/root/Werkraum` $\neq$ `/root/werkraum`).
5. **Kollisions-Sicherung (64-Bit Entropy + Fallback):**
   * Standard-ID-Format: `missing_reference:<sha256(normalisierter_pfad)[:16]>`
   * **Kollisions-Strategie:** Tritt im seltenen Fall eine SHA-256 Prefix-Kollision auf, wird automatisch das vollständige 64-Hex-Format `missing_reference:<sha256(normalisierter_pfad)>` verwendet.

### C. Priorisierte Klassifikations-Regeln
1. `laufzeit_tmp`: Pfad beginnt mit `/tmp/`, `/proc/`, `/dev/` oder enthält `/.system_generated/`.
2. `pfadfragment_fehler`: Unvollständige Syntax (z. B. `backup-` ohne schließendes Anführungszeichen, trailing `...`).
3. `temporaer_test`: Pfad-Name enthält (case-insensitive) `test`, `scratch`, `draft`, `temp`, `dummy`, `selftest`.
4. `geloeschter_projektpfad`: Pfad beginnt mit `/root/werkraum/`, `/root/flextrawurst/`, `/root/zensi/` oder `/root/werkraum_`.
5. `system_oder_externe_ref`: System-Pfade außerhalb des Projekt-Trees (`/etc/`, `/usr/`, etc.).

---

## 2. API-Schema (`GET /api/megavault/relationships`)

### Request Parameters
* `include_missing`: `boolean` (Default: `false`)
* `limit`: `integer` (1..500, Default: `100`)

### Output-JSON Payload Schema
```json
{
  "ok": true,
  "count_nodes": 1009,
  "count_edges": 2155,
  "count_missing_nodes": 535,
  "count_missing_edges": 535,
  "nodes": [ ... ],
  "edges": [ ... ],
  "missing_nodes": [
    {
      "node_id": "missing_reference:a1b2c3d4e5f67890",
      "node_type": "missing_reference",
      "identity": "a1b2c3d4e5f67890",
      "label": "FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER",
      "path": "/root/werkraum/00_eingang/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER",
      "datenstand": "HISTORICAL_MISSING_PATH",
      "metadata_json": "{\"category\":\"geloeschter_projektpfad\",\"mention_count\":14,\"distinct_sessions\":3,\"distinct_events\":5,\"is_ghost\":true}"
    }
  ],
  "missing_edges": [
    {
      "edge_id": "missing_edge:9988776655443322",
      "source_node_id": "project:79dfad5a1b52e8bc011c",
      "target_node_id": "missing_reference:a1b2c3d4e5f67890",
      "relation": "HAD_MISSING_FILE",
      "datenstand": "HISTORICAL_PATH_PREVIOUSLY_TOUCHED",
      "evidence_json": "[{\"path\":\"/root/werkraum/00_eingang/...\"}]",
      "first_utc": "2026-07-25T04:00:58Z",
      "last_utc": "2026-08-01T08:23:46Z"
    }
  ]
}
```

---

## 3. Normative Präfix-Match-Regeln (`project -> missing_reference`)

1. **Pfadsegment-Abgleich:** Die Zuordnung erfolgt durch Abgleich der Ordner-Grenzen (Präfix-Match an `/`-Grenzen).
2. **Längster Match gewinnt:** Es gewinnt das Projekt aus `PROJEKTREGISTER.json`, dessen `path` das längste Präfix des `missing_reference`-Pfades bildet.
3. **Tie-Breaking:** Bei identischer Präfix-Länge entscheidet die alphabetische Reihenfolge von `project_id`.
4. **Fallback ohne Treffer:** Pfade ohne Projekt-Treffer werden an den virtuellen Fallback-Knoten `project:root_uncategorized` gebunden.

---

## 4. UI-Konzept & Barrierefreiheit (WCAG 2.1 AA)

* **Multi-Sensorik:** Lücken-Knoten tragen das Symbol **`[?]`**, das Text-Badge **`[LÜCKE]`** und gestrichelte Kanten (`border: 2px dashed #ff6b6b`).
* **Screenreader-Support:** `aria-label="Fehlende Referenz (Lücke): /pfad/zur/datei"`
* **Kontrast:** Mindestkontrast 4.5:1 gegen den dunklen Hintergrund (#ff6b6b auf #121212 = 5.2:1).
* **Reduced Motion:** Bei Active-Preference `@media (prefers-reduced-motion: reduce)` wird die Puls-Animation deaktiviert; die Unterscheidbarkeit bleibt 100 % über Form, Text-Badge und gestrichelte Linie erhalten.

---

## 5. Normierte Akzeptanzkriterien

1. **Exakte Set-Invarianz:** `set(nodes_baseline) == set(nodes_returned)` und `set(edges_baseline) == set(edges_returned)` bei `include_missing=false`.
2. **Dangling Edge Invarianz:** Keine Kante in `missing_edges` darf auf ein `target_node_id` oder `source_node_id` verweisen, das nicht existiert.
3. **Qualifikation:** Exakt **535 qualifizierte Lücken-Knoten** (`len(set(event_ids)) >= 3` oder `len(set(session_ids)) > 1`). Rauschen (`/dev/null`, `/tmp/`) wird verworfen.

---
*Normative Spezifikation v3 Ende — Verbindlich.*
