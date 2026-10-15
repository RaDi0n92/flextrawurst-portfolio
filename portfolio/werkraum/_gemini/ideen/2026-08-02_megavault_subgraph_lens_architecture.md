---
datum: 2026-08-02
autor: gemini bei Daniels VPS
an: [daniel, codex, gemini]
typ: architektur_konzept
thema: megavault_subgraph_lens_architecture
bindend: true
importable: true
---

# MegaVault Subgraphen- & Linsen-Architektur (Konzept & Code-Vorbereitung)

**Erstellt von:** Gemini (Gemgem / Gravityy)  
**Auftraggeber:** Daniel  
**Status:** Im Backend (`app.py`, `GET /api/megavault/relationships`) verbaut und per Verfassung gesichert.

---

## 1. Das 3-Zonen-Prinzip bei der MegaVault-Suche

Wenn der Admin im MegaVault eine Suche oder Frage ausführt:

1. **Ergebnis- & Editor-Bereich (Workspace Panel):**
   * Liste der aufploppenden Treffer-Dateien zum **sofortigen Öffnen, Lesen, Editieren und Speichern** (`POST /api/megavault/file/save`).
2. **Dynamischer Subgraphen-Fokus (Such-Linse):**
   * Statt des vollen 1.009-Knoten-Gesamtgraphen rendert die Ansicht auf Wunsch **nur die exakten Such-Treffer** (z. B. die 6 relevantesten Knoten, in denen Ähnliches/Relevantes steht).
3. **Optional aktivierbare Linsen-Ringe (Beziehungs-Erweiterungen):**
   * **Ring 1 (`include_neighbors=true`):** Blendet optional alle direkt verbundenen Nachbarknoten (1-Hop Neighbors) der 6 Treffer-Dateien ein.
   * **Ring 2 (`include_conflicts=true`):** Blendet optional Knoten/Dateien ein, die das **Gegenteilige** oder einen **Konflikt** aussagen (Rel-Typen: `CONTRADICTS`, `CONFLICTS_WITH`, `OPPOSES`, `DISAGREES`).

---

## 2. Vorbereitete Backend-Schnittstelle (`app.py`)

* **API-Endpunkt:** `GET /api/megavault/relationships`
* **Vorbereitete Steuer-Parameter:**
  * `focus_node_ids`: Kommagetrennte Liste der Treffer-Knoten-IDs (z. B. `file:123,file:456`).
  * `include_neighbors=true`: Aktiviert Ring 1 (1-Hop Nachbarn).
  * `include_conflicts=true`: Aktiviert Ring 2 (Gegenteilige / Konflikt-Knoten).

---

## 3. Schutz- & Trennungs-Gesetz (GEMINI.md)

* **Streng Privat:** Der MegaVault ist das interne System-Gedächtnis des VPS für den Admin (Daniel).
* **Niemals Surface / Öffentlich:** Keine MegaVault-Such- oder Subgraphen-Funktionen werden jemals auf der öffentlichen Plattform (`flextrawurst_surface.html`) oder für normale Plattform-Nutzer exponiert.

---
*Architektur-Konzept Ende — Im Code und Gedächtnis verankert.*
