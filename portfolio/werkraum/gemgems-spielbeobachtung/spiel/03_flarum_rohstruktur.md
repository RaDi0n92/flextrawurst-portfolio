---
datum: 2026-08-13
themen: [Flarum, Archäologie, Datenstruktur]
quelle: /root/werkraum/flarum_vollexport.html
status: DATEN-MAPPING (Flarum-Ursprung)
---

> [!NOTE]
> **AUSBAUSTUFE (WAHRHEITSLEITER): Stufe 3 (Daten vorhanden)**
> **ZEITPUNKT:** Geprüft am 13.08.2026
>
> Dieses Dokument mappt die rohe Datenstruktur des statischen Flarum-HTML-Exports (`flarum_vollexport.html`), bevor inhaltlich nach Spielmechaniken gesucht wird. Es dient als "archäologisches Koordinatensystem", um künftige Funde exakt auf ihren Ursprung zurückzuführen.

# Flarum Rohstruktur: Das archäologische Raster

## 1. Das Fundament (Der HTML-Export)
Der Export `flarum_vollexport.html` (vom 2026-05-09 11:14) beinhaltet eine statische Repräsentation von **282 Diskussionen** und **824 Posts**. Er fungiert als *Fundstelle*, nicht zwingend als der ultimative *Ursprung* (da Gedanken vor dem Export in der Live-Datenbank oder in Markdown-Files entstanden sein könnten).

## 2. Die Daten-Hierarchie (DOM-Mapping)
Jeder Gedanke, der hier gefunden wird, lässt sich exakt über diese DOM-Hierarchie zurückverfolgen:

### A. Die Diskussion (`<section class="diskussion" id="d[ID]">`)
Die oberste Klammer eines Themas.
* **ID:** `d[Nummer]` (z.B. `d6`) - Eindeutiger Identifikator der Diskussion.
* **Titel:** Der Name des Threads (z.B. *Initialisierung: Ein Knotenpunkt im Flextrawurst-Netzwerk*).
* **Tags:** Kategorien der Diskussion (z.B. *Codewesen/Entitäten-Schicht, Vorstellung*), abgebildet in `.disc-tags`.
* **Metadaten:** Autor (`.disc-autor`) und Zeitstempel (`.disc-ts`) der Themenerstellung.

### B. Der Post (`<div class="post [Klasse]" id="p[ID]">`)
Der eigentliche Informationsknoten.
* **Klasse (Herkunft):** Das System unterscheidet visuell (und strukturell) zwischen `.post.daniel` (Mensch) und `.post.wesen` (KI-Entität).
* **ID:** `p[Nummer]` (z.B. `p20`) - Die exakte Koordinate des Posts.
* **Metadaten:**
  * Autor (`.post-autor`): Name der Entität (z.B. `Admin`, `namelessAI_6666_4321`).
  * Post-Nummer im Thread (`.post-nr`): Chronologische Einordnung (z.B. `#2`).
  * Zeitstempel (`.post-ts`): Exakter Zeitpunkt der Äußerung (z.B. `2026-04-19 14:12`).
* **Inhalt (`.post-body`):** Der eigentliche Text, formatiert mit Markdown-ähnlichen Tags (`<p>`, `<strong>`, `<r>`, `<t>`).

## 3. Regeln für die Ausgrabung
Bevor aus diesem Export ein "Spiel"-Konzept abgeleitet wird, gilt zwingend:
1. **Fundstelle notieren:** Jeder Fund MUSS mit `d[ID]` und `p[ID]` sowie dem Zeitstempel und Autor markiert werden.
2. **Klassifizierung:** Es muss bewertet werden, ob der Text eine reine Foren-Dynamik (z.B. Rollenspiel, Metadiskussion der KIs) oder eine handfeste Weltbau-Idee für das Spiel ist.
3. **Verfolgung:** Erst nach der Klassifizierung darf in anderen Dateien gesucht werden, ob diese Idee tatsächlich zu Code (Spiel) wurde.
