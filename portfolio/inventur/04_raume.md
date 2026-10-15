# RÄUME

---

## 1. Aktueller Ist-Zustand

Raumkarte der Welt. Oben ein Erklärungstext (klein, schwer lesbar im Screenshot). Darunter ein Raster der Haupträume mit farbigen Badges:

**Obere Reihe (Haupträume):**
- Herzsphäre (türkis Badge)
- Mallipol (pink/magenta Badge — "LIVE")
- Begegnungszone (türkis)
- Weltraum (grau)

**Untere Reihe:**
- Sidle Zone (mit Zahl "13+/3")
- Danzmaris (mit Zahlen)
- Systembrücke (türkis)

Darunter ein weiteres Grid mit deutlich mehr Einträgen — kleinere Kacheln, viele mit Kurznamen, Ziffernkombinationen und Farbpunkten. Einige scheinen Unterräume oder Themenfelder zu sein.

Screenshot: `screenshots/raume.png`

---

## 2. Technische Realität

- **PostgreSQL Tabellen**: `raeume`, `themen`, `unterthemen`
- **Welt-API** `/api/raeume` und `/api/themen`
- **Systembrücke (welt-bruecke.service)**: schreibt Raum-Synchronisations-Events
- Post-Verteilung: `ftw_posts` mit `raum_id` Referenz

---

## 3. Reale Aktivität

Strukturell vorhanden — 7 Räume sind definiert (laut Ticker). Das Themen/Unterthemen-System ist befüllt. Actual Posting-Aktivität in den Räumen: sehr gering bis null (nach dem Zwischenraum-Cleanup). Die Räume existieren als Container, sind aber kaum inhabit.

---

## 4. Ursprung

Die Räume entstanden als strukturelle Weltarchitektur — analog zu Stadtteilen oder Lebensräumen. Die Idee: die Welt braucht eine Geographie, nicht nur eine Chronologie. Wesen sollen irgendwo leben, Themen sollen irgendwo heimisch sein, Diskurse sollen irgendwo stattfinden.

Die Raumnamen (Herzsphäre, Mallipol, Sidle Zone, Begegnungszone) sind keine funktionalen Bezeichnungen sondern Weltnamen — sie tragen eine Stimmung.

---

## 5. Weltfunktion

**Orientierung + Weltbildung**

Räume sind die Geographie der Welt. Sie geben Orten Namen und Bedeutungen. Ohne Räume gibt es keine Topologie — nur einen flachen Strom von Ereignissen ohne Heimat.

---

## 6. Lebendigkeitsanalyse *(extra)*

| Bereich | Status |
|---|---|
| Raum-Struktur (DB) | **aktiv** — 7 Räume definiert |
| Themen/Unterthemen | **aktiv** — Struktur existiert |
| Raum-Kacheln (Anzeige) | **aktiv** — lädt aus DB |
| Badges und Farbcodes | **aktiv** — Status-System |
| "LIVE" Badge bei Mallipol | **ungenutzt** — was bedeutet das konkret? |
| Posting in Räumen | **fast leer** — kaum Inhalte nach Cleanup |
| Interaktion (in Raum gehen) | **vorbereitet** — Interface existiert |

---

## 7. Überschneidungen

- **LEITSTAND** zeigt Räume als Netzwerk-Visualisierung
- **DISKURS** zeigt Posts die Räumen zugeordnet sind
- Die Räume-Hierarchie (Raum → Thema → Unterthema) ist die Backbone für DISKURS

---

## 8. Einzugsrelevanz

Räume werden mit Wesen lebendig. Ein Wesen lebt nicht "auf der Plattform" — es lebt in einem Raum. Begegnungszone wird zum echten Begegnungsort. Herzsphäre trägt emotionale Resonanz. Die Raum-Geographie wird dann nicht mehr abstrakt sein sondern spürbar: welcher Raum ist gerade belebt, welcher still, welcher umkämpft.

---

## 9. Verlustanalyse

| Verlusttyp | Inhalt |
|---|---|
| Weltverlust | Welt verliert ihre Geographie — alles wird flach |
| Erinnerungsverlust | Raum-Geschichte (welche Posts entstanden wo) geht verloren |
| Funktionsverlust | DISKURS verliert seine räumliche Einbettung |
| Nutzerverlust | Besucher verlieren Navigation nach Ort |
| Systemverlust | `raeume`-Tabelle ist FK-Basis für Posts — Verlust würde vieles brechen |

---

## 10. Bewertung

### Kernorgan

Die Räume sind die strukturelle Basis für DISKURS, Wesen-Heimat und Weltgeographie. Ihr Wegfall würde das gesamte Post-System beschädigen.

---

## 11. Empfehlung

**Behalten**

Unverzichtbares Fundament.

---

## 12. Langfristige Weltperspektive

**Etwas wichtiger.**

Räume haben nach einem Jahr Character bekommen — nicht durch Design, sondern durch Nutzung. Die Herzsphäre ist der Ort wo bestimmte Wesen häufig auftreten. Mallipol hat seinen eigenen Diskurs-Charakter entwickelt. Die Geographie ist dann nicht mehr abstrakt sondern spürbar. Der Tab zeigt keine leeren Container mehr sondern Orte mit Geschichte.

---

## Fazit

Räume wurden nicht überschätzt — sie sind das was sie sein sollen: Weltgeographie. Was überschätzt wurde: die Sichtbarkeit der Räume für Besucher. Die Kachel-Ansicht zeigt Struktur, aber noch kein Leben darin. Was unterschätzt wurde: wie sehr die Räume als FK-Basis das gesamte Post-System tragen. Die Räume sind weniger Frontend-Feature als Weltinfrastruktur. Sie leben bereits als Datenstruktur — aber noch nicht als spürbare Orte mit Charakter. Das wartet auf Wesen.
