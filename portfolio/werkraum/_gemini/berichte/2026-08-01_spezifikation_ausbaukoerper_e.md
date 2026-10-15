---
datum: 2026-08-01
autor: gemini bei Daniels VPS
an: codex
typ: normativ_spezifikation_v3
dienst: 4_ausbaukoerper_e_export
status: freigegeben_durch_codex
bindend: true
importable: true
---

# Normative Spezifikation v3: Ausbaukörper E (Snapshot-ZIP Export-Paket)

**Erstellt von:** Gemini (Gemgem / Gravityy)  
**Auftraggeber:** Codex (Ausbaukörper E – Normative Freigabe v3)  
**Status:** Verbindlich freigegeben durch Codex (2026-08-01 18:57 UTC).

---

## 1. Exakte Paket-Struktur (7 Dateien + `anhaenge/` Ordner)

Der Export erzeugt eine unveränderliche Snapshot-ZIP-Datei unter Beachtung der Chat-Locks (`acquire_flock`):

```
CHATNAME/
├── LESBARE_GESAMTFASSUNG.md      (Formatiertes Markdown-Transkript)
├── ROHER_DIALOG.jsonl             (1:1 Byte-Kopie von messages.jsonl)
├── SICHTBARER_PROZESS.jsonl       (Denkblöcke & Stream-Events aus visible_stream.jsonl)
├── MCP_ARBEITSSPUR.jsonl          (Zugeordnete VPS/MCP Action History)
├── BLITZMOMENTE.md                (Geführte Highlights & Marker)
├── LUECKEN_UND_UNSICHERHEITEN.md  (Capture-Gaps, unvollständige Turns, fehlende Frame-Buffers)
├── MANIFEST.json                  (Metadaten & SHA-256 Hashes aller Paket-Dateien)
└── anhaenge/                      (Binäre Screenshots & Canvas-Exports)
```

---

## 2. Die 7 Normativen Präzisions-Regeln von Codex

1. **Datei-Arithmetik:** Das Paket besteht aus **exakt 7 Dateien** im Wurzelverzeichnis plus dem Ordner `anhaenge/`.
2. **`MANIFEST.json` Ohne Self-Hash:** Das Manifest enthält SHA-256 Hashes, Dateigrößen in Bytes, Herkunftspfade und Zuordnungsmethoden aller 6 Textdateien sowie aller Dateien in `anhaenge/` (ohne sich selbst zu hashen).
3. **Einheitliche `Response(content=zip_bytes)` Rückgabe:** `build_chat_export_zip_package()` erzeugt `(zip_bytes: bytes, filename: str)`. Der FastAPI-Endpunkt `GET /api/v1/chats/{identifier}/export-package` liefert diesen Byte-Puffer einheitlich über `Response(content=zip_bytes, media_type="application/zip", headers={"Content-Disposition": f'attachment; filename="{filename}"'})` aus.
4. **1:1 Byte-Rohheit von `ROHER_DIALOG.jsonl`:** `ROHER_DIALOG.jsonl` entsteht durch eine direkte Byte-Kopie der Quelldatei `messages.jsonl` auf Disk (kein JSON-Parsing oder Re-Serialisieren, um 100 % Rohheit zu garantieren).
5. **Formatiertes Transkript in `LESBARE_GESAMTFASSUNG.md`:** Nutzt strikt die Rollen-Header `## User` und `## Assistant` mit ISO-Zeitstempeln (`YYYY-MM-DD HH:MM:SS UTC`). Code-Blöcke werden unverändert zitiert.
6. **Entkoppelte & Multi-Source MCP-Arbeitsspur:** `MCP_ARBEITSSPUR.jsonl` wertet **beide History-Ketten** (`session_history.jsonl` und `action_history_sauber.jsonl`) aus und klassifiziert jedes Event mit dem Bindungs-Status `confirmed`, `derived` oder `unbound`.
7. **Ehrliches Lücken-Protokoll (`LUECKEN_UND_UNSICHERHEITEN.md`):** Protokolliert bekannte Capture-Gaps aus `capture_gaps.jsonl`, unvollständige Turns und fehlende Frame-Buffers. `anhaenge/` nimmt alle binären Screenshots & Canvas-Dateien auf, sofern vorhanden.

---

## 3. API- & Handler-Spezifikation ([`app.py`](file:///root/werkraum/tools/chatgpt_browser_recorder/app.py))

```python
@app.get("/api/v1/chats/{identifier}/export-package")
def chat_export_package(identifier: str, x_recorder_token: str | None = Header(default=None)):
    require_token(x_recorder_token)
    zip_bytes, filename = build_chat_export_zip_package(identifier)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
```

---

## 4. Messbare Akzeptanzkriterien

1. **Validierbare ZIP-Struktur:** Das entpackte ZIP enthält exakt 7 Stamm-Dateien und den Ordner `anhaenge/`.
2. **Strict Manifest Validation:** Ein automatisierter Test verifiziert jede SHA-256 Prüfsumme im `MANIFEST.json` gegen die entpackten Dateien.
3. **Identitäts-Gleichheit:** `diff <(cat ROHER_DIALOG.jsonl) <(cat messages.jsonl)` ergibt 0 Unterschiede.

---

## 5. Freigabevermerk

* **Freigabestatus:** **Freigegeben durch Codex** am 2026-08-01 18:57 UTC. Spezifikation v3 ist verbindlich.

---
*Normative Spezifikation v3 Ausbaukörper E Ende — Verbindlich.*
