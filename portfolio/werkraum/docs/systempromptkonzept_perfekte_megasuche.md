# 📜 SYSTEMPROMPTKONZEPT & BAUAUFTRAG: DIE PERFEKTE MEGASUCHE

**Projekt:** Flextrawurst / Gesamtatlas / MegaSuche (Port 18108)  
**Autor:** GemGem (Gemini) bei Daniels VPS  
**Datum:** 2026-08-02  
**Status:** In Planung & Abstimmung mit Daniel  

---

## 1. VISION: DIE DREI SÄULEN DER PERFEKTEN MEGASUCHE

### 🎈 Säule 1: Rohheit & Die Freude des Kindes (Das Entdeckungs-Erlebnis)
- **Keine technischen Hürden:** Der Mensch gibt ein Wort ein und sieht sofort farblich getrennte Karten aller 6 AI-Ströme (Gemini, Codex, Claude, ChatGPT, Kimi, GLM).
- **Das Unboxing-Gefühl:** Ein Klick auf ein Suchergebnis zeigt nicht bloß einen abgehackten Satz, sondern öffnet das **Volltext-Modal**, in dem die gesamte Datei wie ein Buch vor einem liegt.
- **Die Nachbar-Erkundung:** Über den Tab *Querverweise & Nachbarn* sieht der Mensch auf einen Blick alle verwandten Notizen und Skripte daneben, die ähnliche Themen berühren.

### 🧠 Säule 2: Die Analytik des Gehirnforschers (2ndBrain Multi-Engine)
- **Die 3-Schichten-Trefferarchitektur:**
  1. **Schicht 1 (Exaktes 1-zu-1 Zitat):** Der genaue Fundsatz mit exakter Zeilennummer (z. B. L42-L48) und farblicher Hervorhebung.
  2. **Schicht 3 (Volltext & Inspector):** Auf Wunsch die vollständige Datei mit Editierfunktion (Bearbeiten) und Git-Backup-Schutz (Speichern).
  3. **Schicht 3 (Synaptische Nachbarschaft & Graph):** 1-Hop Nachbarknoten, Verlinkungen ([[wiki_links]]) und semantisch verwandte Dateien aus ChromaDB & Begriffsindex.
- **Multi-Quellen-Abdeckung:** Simultanes Scannen von Dateisystem, SQLite (knoten.db, BEGRIFFSINDEX.sqlite), PostgreSQL Events (events) und Foren-Archiv.

### ⚔️ Säule 3: Redteam-Härtungsplan (Gefahrenanalyse & Schranken)
- **R1 (Performance-Guard):** Nachbar-Dateien werden erst beim Klick auf den Tab *Querverweise* geladen (lazy-load), damit die Hauptsuche unter 50 ms schnell bleibt.
- **R2 (Speicher-Guard):** Binär- und Riesendateien (>2 MB) laden nicht voll in den Arbeitsspeicher, sondern werden sicher im *Binär-Inspector* oder mit 500 KB Truncate dargestellt.
- **R3 (Zero-Halluzinations-Garantie):** Das Suchergebnis zeigt IMMER den originalen Wortlaut 1-zu-1 mit Pfad, Zeilennummer und Zeitstempel.

---

## 2. BAUSCHRITTE & UMSETZUNGSPLAN

1. **Schritt 1: Backup setzen** (On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
  (commit or discard the untracked or modified content in submodules)
	modified:   .claude/worktrees/notiz-2026-07-26 (untracked content)
	modified:   WorldWORDS-ANTIBIBEL-Open-Source (untracked content)

no changes added to commit (use "git add" and/or "git commit -a")).
2. **Schritt 2: Nachbar-Dateien-Endpunkt erweitern**:  ausbauen, um für jede gewählte Datei sofort die 5 semantisch ähnlichsten Notizen aus allen 6 AI-Strömen zu berechnen.
3. **Schritt 3: Volltext-Modal verfeinern**: Tab 2 in  mit interaktiven Nachbar-Karten ausstatten, die sich per Klick sofort im Inspector ausklappen lassen.
4. **Schritt 4: E2E Playwright Verifizierung**: Testen, ob der Ablauf *Suche -> Zitat -> Volltext -> Nachbar-Datei* flüssig und lückenlos funktioniert.

---

**Freigabe durch Daniel erforderlich:** Ist dieses  genau so im Sinne deines Bauauftrags?
