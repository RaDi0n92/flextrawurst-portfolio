---
datum: 2026-08-01
autor: gemini bei Daniels VPS
an: codex
typ: status_matrix_ausbaukoerper
dienst: 4_ausbaukoerper_abgleich_a_bis_f
bindend: false
importable: false
---

# Status-Matrix: Ausbaukörper A–F (ChatGPT / Browser Recorder)

**Erstellt von:** Gemini (Gemgem / Gravityy)  
**Auftraggeber:** Codex (Dienst 4: Ausbaukörper-Abgleich A–F)  
**Status:** Rein lesender Code- & Struktur-Abgleich (`app.py`, `extension/`, `browser_capture.py`, `browser_experiments.py`)

---

## 📊 Gesamt-Übersicht der Ausbaukörper A–F

| Ausbaukörper | Status | Fundstellen im Code | Fehlende Bausteine |
| :--- | :---: | :--- | :--- |
| **A. Zeitreise-Wiedergabe eines Turns** | **TEILWEISE** | `app.py:206` (`GET /api/v1/chats/{id}/timeline`), `browser_capture.py` (`read_browser_timeline` mit `from_utc`/`to_utc`/`turn_id`). | Zeitreise-Regler (00:00 $\rightarrow$ 01:02) im Frontend; schrittweise Replay-Engine für blinkende Denkblöcke & Zwischenstufen. |
| **B. UI- & VPS-Arbeit verweben** | **TEILWEISE** | `app.py:140` (`GET /api/v1/experiments/{id}/timeline`), `browser_experiments.py` (`include_derived=True` verknüpft Chat- & MCP-Events). | Synchrone 2-Spalten-Ansicht im UI (*CHATGPT-UI links ↔ VPS/MCP rechts*) mit lückenlosem Turn-Versiegelung-Stempel. |
| **C. Blitzmoment-Knopf** | **FEHLT** | `app.py:172` (`set_browser_chat_alias` vorhanden, aber keine Marker-APIs). | API-Endpunkt `POST /api/v1/chats/{id}/markers`; Marker-Kategorien (`Blitzmoment`, `Entscheidung`, `offene Frage`, `Ursprung`, `Irrweg`); Extension-Knopf. |
| **D. Rohkörper vs. spätere Glättung** | **FEHLT** | Keines. Rohe Events liegen unter `/api/v1/events`, aber keine Diff-Engine. | Diff- & Vergleicher-Engine für 4 Stufen: (1) Roher Satz, (2) Erste Reaktion, (3) Technische Übersetzung, (4) Erzeugte Regel/Datei. |
| **E. Gesprächskörper-Export Paket** | **VORHANDEN** (80 %) | `app.py:187` (`export-data`), `app.py:166` (`export_browser_experiment`). | Exaktes 8-Dateien-Paket (`CHATNAME/`: `LESBARE_GESAMTFASSUNG.md`, `ROHER_DIALOG.jsonl`, `SICHTBARER_PROZESS.jsonl`, `MCP_ARBEITSSPUR.jsonl`, `BLITZMOMENTE.md`, `LUECKEN_UND_UNSICHERHEITEN.md`, `MANIFEST.json`). |
| **F. Lebendige Suchfunktion** | **TEILWEISE** | `app.py:206` (Filter `q`, `turn_id`, `event_type`), VPS Gesamtatlas RAG-Suche (`/api/megavault/search`). | Semantisch-kausale Spezial-Filter (*„Wo erstmals gesagt?“*, *„Wo widerspricht spätere Regel dem Rohwunsch?“*). |

---

## 🔍 Detaillierte Befunde zu den einzelnen Körpern

### A. Zeitreise-Wiedergabe eines Turns (Prozesskamera)
* **Ist-Stand:** Das Backend erfasst bereits hochgradig verfeinerte Zeitstempel je Event (`from_utc`, `to_utc`, `turn_id`). Über `GET /api/v1/chats/{identifier}/timeline` lassen sich alle Zwischenschritte als Ereignis-Array abrufen.
* **Lücke:** Es fehlt das interaktive Replay-Frontend (Schieberegler von 00:00 bis 01:02), das den Text wachsen sieht und Zwischenformulierungen animiert wiederholt.

### B. UI und VPS-Arbeit zu einer gemeinsamen Spur verweben
* **Ist-Stand:** In `browser_experiments.py` baut `build_browser_experiment_timeline` bereits eine verknüpfte Timeline, die Browser-Events und MCP/Action-History-Ereignisse über `mcp_session_id` zusammenführt (`include_derived=True`).
* **Lücke:** Das Visuelle 2-Spalten-Layout (CHATGPT-UI ↔ VPS/MCP) ist noch nicht in einer Frontend-Ansicht zusammengeführt.

### C. Blitzmoment-Knopf
* **Ist-Stand:** Bisher existiert lediglich eine einfache Alias-Funktion (`POST /api/v1/alias`).
* **Lücke:** Es fehlen Marker-Pointers im Extension-DOM-Injector sowie das Schema in `browser_capture.py` zur Speicherung von Markern auf Turns, Denkblöcke oder Textstellen.

### D. Unterschied zwischen Rohkörper und späterer Glättung
* **Ist-Stand:** Rohe User-Eingaben werden unverändert in den Event-Streams gespeichert.
* **Lücke:** Es gibt noch kein Aggregat, das den rohen Satz direkt neben der daraus entstandenen System-Regel (z. B. "HARD RULE 8") oder Datei darstellt.

### E. Gesprächskörper auf Knopfdruck exportieren
* **Ist-Stand:** Exporte existieren über `/api/v1/chats/{id}/export-data` und `/api/v1/experiments/{id}/export` als strukturierte JSON/Zip-Dateien.
* **Lücke:** Die spezifische 8-Dateien-Ordnerstruktur aus Daniels Fahrplan (`LESBARE_GESAMTFASSUNG.md`, `BLITZMOMENTE.md`, `MANIFEST.json`, etc.) muss als Ziel-Exportformat implementiert werden.

### F. Lebendige Suchfunktion
* **Ist-Stand:** Exakte Volltextsuche und RAG-Vektor-Suche stehen über den Gesamtatlas auf Port 18108 zur Verfügung.
* **Lücke:** Kausale Beziehungs-Filter für Erstnennung, Verhärtung von Ideen und Regel-Ursprüngen.

---

## 🎯 Empfehlung für den nächsten Prioritäts-Schritt:

1. **Ausbaukörper E (Gesprächskörper-Export) vollenden:** Ist zu 80 % vorbereitet und kann mit minimalem Risiko auf die exakte 8-Dateien-Struktur finalisiert werden.
2. **Ausbaukörper C (Blitzmoment-Knopf):** Bietet den höchsten sofortigen Nutzen für die Provenienzlogik.

---
*Status-Matrix Ende.*
