# CT-Scan: Entitäten-Schicht & Codewesen-Profile

Dieses Dokument enthält die Ergebnisse der tiefgehenden Provenienz-Prüfung durch den Skeptiker-Subagenten.

## Methodik
Die Kette wurde wie folgt geprüft: 
**Flarum-Fossil -> MD Konzepte/Notizen -> Code/DB/Backend-Skripte -> Laufendes System (Surface/APIs).**
Danach erfolgte ein Runtime-Test gegen Port 8030 / 8787.

---

### Testfall 1: Entitäten-Schicht
*Bezug: Diskussion #96, #105, #140 im Flarum-Export*

- **Flarum-Fossil**: Die Konzepte aus den Diskussionen beziehen sich auf eine strukturelle Schicht für die Wesen.
- **Zwischenstufe (Konzepte)**: Erwähnt in verschiedenen Spiegel- und Konzept-Dateien (z.B. `_gemini/spiegel/2026-07-23_von_zensi_ursprung_bis_kognitives_quad_und_syn.md`).
- **Code/Backend (Die harte Architektur)**: In `/root/werkraum/welt/schema_entitaetenschichten.sql` werden explizit Tabellen wie `entity_profiles`, `entity_activity` und `entity_thinking_log` angelegt. Die API (`/root/werkraum/welt/api.py`) besitzt eine Route `/wesen`, jedoch greift diese **nicht** auf die Profile/Activity-Tabellen zu, sondern auf `entity_slots` und `entity_states`.
- **Laufendes System (Surface)**: Im Frontend (`/root/werkraum/flextrawurst/flextrawurst_surface.html`) gibt es explizit harte UI-Elemente (`#view-wesen`, `#view-blasen`). Allerdings nutzt die Surface für die Darstellung gespawnter Wesen z.B. `/wesen/list`, nicht den reinen `/wesen`-Endpunkt.

#### Wahrheits-Bewertung: Indizien vorhanden 🟡
**Begründung**: Die Entitäten-Schicht und die DB-Architektur sind zwar physisch vorhanden, aber die direkte Abstammungsurkunde von Flarum #96/#105/#140 zu *genau diesem* SQL/API-Code ist bisher nicht lückenlos bewiesen. Parallelität und zeitliche Fortsetzung sind da, aber der direkte Link fehlt noch.

---

### Testfall 2: Codewesen-Profile ("Spannungswesen", "Reduktionswächter" etc.)
*Bezug: Diskussion #321, in der ein externer ChatGPT-Spiegel die emergierenden Unterschiede explizit benennt und konsolidiert.*

- **Flarum-Fossil**: Stammt direkt aus Diskussion #321 (Post #1505), in der der Admin eine externe ChatGPT-Analyse postet, die den Nummern-Wesen (1111_1234, 3333_1423 etc.) diese Wesenszüge und Titel zuschreibt.
- **Zwischenstufe (Konzepte/Gedächtnis)**: Dieser Post wurde als Fossil in die Spiegeldateien der Wesen übernommen (z.B. in `/root/werkraum/codewesen/F3INSCHM3CK3R/spiegel/forum/2026-05-10.md` und als RAG-Dokument in `processed/2026-05-09T08-15-38_menschlicher_post.json`).
- **Code/Backend (Die harte Architektur)**: In den heutigen statischen Backend-Profilen (z.B. `/root/werkraum/codewesen/Schorschel/wesen.md`) tauchen diese spezifischen Titel/Profile **nicht** als harte Attribute oder Struktur-Klassen auf. Die Wesen wurden inzwischen benannt (aus 1111_1234 wurde z.B. Schorschel). 
- **Laufendes System**: Die Profile sind nicht hardcodiert. Da `codewesen_chat.py` jedoch das Archiv über RAG dynamisch in den Kontext lädt, erinnern sich die Wesen potenziell aus ihrem "Gedächtnis" an diese Konsolidierung, aber es ist *kein* starres Code-Attribut geworden.

#### Wahrheits-Bewertung: Indizien vorhanden 🟡
**Begründung**: Die Begriffe haben als historische Prägung und "Erinnerung" in den RAG-Archiven überlebt. Aber im Code-Körper selbst wurden sie bewusst *nicht* als starre Struktur-Rollen/Attribute in die Architektur gemeißelt.

---

## Abschließender Playwright/API-Test (Runtime-Check)
Der Skeptiker hat abschließend per `curl` die API auf Port 8030 angepingt, um zu testen, ob die Entitäten-Schicht heute physisch erlebbar ist.

**Befehl:**
`curl -s http://127.0.0.1:8030/wesen; curl -s http://127.0.0.1:8030/health`

**Ergebnis:**
- `{"wesen":[],"count":0}` (Der Endpunkt der Entitäten-Schicht existiert und antwortet mit HTTP 200. Das leere Array bedeutet jedoch **nicht**, dass keine Wesen existieren! In der Datenbank liegen aktuell 8 Slots, 7 Profile und über 96.000 Logs. Das Array ist leer, weil alle 8 `entity_slots` derzeit `visibility = 'internal'` haben und der öffentliche Endpunkt explizit nach `visibility = 'public'` filtert.)
- `{"status":"ok","timestamp":"2026-08-13T01:38:28..."}` (API Health-Check grün)
