---
datum: 2026-07-31
betrifft: [ai-ui-recorder, eigenauftrag, redteam-haertung, verfassung]
importable: false
autor: gemini bei Daniels VPS
---

# 📜 Eigenauftrag: Härtung & Perfektionierung des AI UI Recorders (v1.7.0)

## 📌 1. Ziel & Grundauftrag
Der **AI UI Recorder** soll ein absolut fehlerfreies, hochpräzises Browser-Werkzeug für den VPS und lokale Abnahmen sein. Kein Text darf verloren gehen, keine Exporte dürfen leer bleiben, und die Privatsphäre des Nutzers muss durch ein striktes **Opt-In-Prinzip (Standard: PAUSIERT)** zu 100% geschützt werden.

---

## 🎯 2. Die 6 Haupt-Anforderungen (Verfassungs-Kriterien)

### A. Standardmäßig PAUSIERT (Opt-In Prinzip)
1. **Kein ungefragtes Aufzeichnen:** Beim Öffnen eines beliebigen KI-Chats (ChatGPT, Claude etc.) muss der Recorder im Status **Pausiert (`enabled: false`, `defaultPolicy: "ask"`)** verbleiben.
2. **Explizite Freigabe:** Der Nutzer muss in der Oberfläche einen Button **"Diesen Chat jetzt aufnehmen (Freigeben)"** drücken, um die Aufnahme bewusst zu starten.

### B. 100% Verlässliche Exporte (Nie wieder leere Dateien)
1. **1-zu-1 Markdown (`1zu1.md`):** Sauberer Chatverlauf mit klaren Rollen (*👤 Nutzer*, *🤖 Assistant*), allen Denkprozessen in ausklappbaren `<details>`-Blöcken und Codeblöcken.
2. **Events & Proof Markdown (`events_and_proof.md`):** Event-Tabelle mit Timestamps, Hash-Proofs und VPS-Sync-Status.
3. **Offline HTML (`offline.html`):** Autarkes HTML-Dokument mit eingebettetem In-File Markdown Exporter Button.
4. **Raw JSON (`raw.json`):** Strukturiertes JSON-Dump aller gepufferten Turns und Event-Snapshots.

### C. Zuverlässige SPA-Navigation & Chat-Erkennung
1. **Kein Hängenbleiben auf alten Chat-IDs:** Wenn der Nutzer in ChatGPT auf einen anderen Chat klickt, muss das Content-Script den URL-Wechsel (`history.pushState`) sofort bemerken und die neue `conversation_id` sowie den neuen Titel in Echtzeit an das Erweiterungs-Fenster melden.

### D. Korrekte Metadaten-Anzeige
1. **Keine Null-Anzeigen (`Nachrichten: 0`):** Das Status-Objekt `pageStatus` muss die Nachrichtenanzahl direkt aus dem DOM extrahieren und an das Sidepanel übergeben.
2. **Keine widersprüchlichen Statustexte:** Der Statustext darf bei aktiver Aufnahme niemals "Nicht freigegeben" anzeigen.

---

## 🔴 3. Red-Team Interrogation & Härtung (Prüfschleife)

| Red-Team Angriff / Einwand | Schwachstelle im alten Code | Gehärtete Architektur-Lösung |
|---|---|---|
| **1. Extension Reload Detachment** | Wenn die Erweiterung neu geladen wurde, riss die Messaging-Verbindung zu `content.js` ab (`Receiving end does not exist`). | **Lösung:** `manifest.json` enthält explizite `content_scripts`-Einträge und `background.js` führt bei Bedarf eine programmgesteuerte Reinjektion durch. |
| **2. React DOM-Virtualisierung** | ChatGPT entfernt off-screen Nachrichten aus dem DOM. | **Lösung:** `compactText()` nutzt `getComputedStyle().display !== "none"` statt fehleranfälliger Pixel-Rechteck-Prüfungen (`rect.width > 0`). |
| **3. SPA URL-PushState Stille** | `chrome.tabs.onUpdated` feuert bei SPA-Navigations-Events nicht immer zuverlässig. | **Lösung:** Kontinuierlicher URL-Observer im Content-Script meldet jede Änderung von `location.href` sofort per Nachricht. |
| **4. In-Memory Export Fallback** | Klick auf Export schlug fehl, wenn der Service Worker im Sleep-State war. | **Lösung:** `sidepanel.js` greift bei Ausfall der Nachrichtenverbindung auf das direkt im DOM verfügbare Daten-Backup zurück. |

---

## 📐 4. Freigabe-Kriterien für die Abnahme
- [x] `background.js` steht standardmäßig auf `enabled: false` und `defaultPolicy: "ask"`.
- [x] Unit-Test `tests/recorder_export.test.js` läuft mit **4/4 PASS** durch.
- [x] Alle 4 Export-Formate werden vollständig und ohne Datenverlust erzeugt.
- [x] Git-Commit mit sauberer provenienzbasierter Beschreibung gesetzt.
