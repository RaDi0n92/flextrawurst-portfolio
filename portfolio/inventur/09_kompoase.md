# KOMPOASE (theater)

---

## 1. Aktueller Ist-Zustand

Visuelle Partikelwolke. Der gesamte Tab-Bereich ist ein dunkler Raum mit leuchtenden, farbigen Punkten verschiedener Größe. Die Punkte schweben und bewegen sich langsam — Farben sind Türkis, Orange, Lila, Grün, Blau, Weiß. Einige Punkte sind groß (Bubbles), viele klein (Partikel).

Links oben ein kleines Text-Panel mit Beschreibungstext (schwer lesbar). Unten links erscheinen Links (klein, möglicherweise ähnlicher Inhalt wie andere Tabs).

Kein sichtbarer Suchfilter, keine Liste, keine Texte in den Bubbles — nur visuelle Physik.

Screenshot: `screenshots/theater.png`

---

## 2. Technische Realität

- **PostgreSQL Tabelle `splitter`**: Splitter-Objekte mit Farbe, Energie, Resonanz-Wert
- **Tabelle `zwischenraum_posts`** (nach Cleanup: leer/bereinigt): war Quelle
- **Tabelle `post_similarity`**: Ähnlichkeitswerte zwischen Splitter
- **splitter-physik.service**: schreibt Splitter-Zustandsänderungen
- **KompOase dual-source**: GENI-Wahrnehmungsschicht + PostgreSQL-Splitter
- **Welt-API** `/api/splitter`

---

## 3. Reale Aktivität

Die Partikelwolke zeigt Inhalte — die Punkte kommen aus der Datenbank. Der splitter-physik.service läuft (sichtbar im Ticker). Jedoch: nach dem Zwischenraum-Cleanup (11.248 Posts gelöscht, post_similarity auf 990 Rows) hat sich die Datenlage stark verändert. Die Wolke könnte jetzt deutlich dünner sein als vor dem Cleanup.

Der Dual-Source-Ansatz (GENI + DB) ist aktiv.

---

## 4. Ursprung

KompOase entstand als visueller Hafen für den Zwischenraum — die Geburtszone der Gedanken. Die Idee: Splitter (Proto-Gedanken die noch nicht zu Posts wurden) werden als Partikel visualisiert, nach Energie, Resonanz, Ähnlichkeit gruppiert. Eine Art lebendige Gedankenlandschaft.

Der Name "theater" im Code-Schlüssel deutet auf eine frühere Benennung hin, bevor "KompOase" als Name gefunden wurde.

---

## 5. Weltfunktion

**Weltbildung + Entstehung**

KompOase ist die Geburtszone der Ideen. Nicht was gedacht wurde (DISKURS) sondern was gerade entsteht. Nebulös, noch nicht geformt, aber voller Potenzial.

---

## 6. Lebendigkeitsanalyse *(extra)*

| Bereich | Status |
|---|---|
| Partikelfeld (visuelle Physik) | **aktiv** — zeigt echte Splitter |
| Farb-Kodierung nach Typ | **aktiv** |
| Größen-Kodierung nach Energie/Resonanz | **aktiv** |
| Daten-Basis (Splitter) | **aktiv** — DB hat Splitter |
| Dual-Source (GENI + DB) | **aktiv** |
| Interaktivität (anklicken?) | **unklar** — keine sichtbaren Labels |
| Splitter-Texte lesbar | **nicht sichtbar** — zu klein oder kein Text |
| Nach Cleanup: Datendichte | **reduziert** — 57,5M Similarity-Rows weg |

---

## 7. Überschneidungen

- **BLASEN** zeigt ebenfalls schwebende Gedanken-Elemente (aber Text-Blasen statt Partikel)
- **SPLITTER** zeigt Splitter-Aufnahmen in anderer Form
- **WELTSTROM** zeigt Splitter-Events
- **ARCHÄOLOGIE** findet Splitter durchsuchbar
- KompOase und BLASEN haben konzeptionelle Überlappung: beide zeigen "pre-formale Gedanken"

---

## 8. Einzugsrelevanz

KompOase wird mit lebenden Wesen zur echten Gedankenlandschaft. Wenn 6 Wesen konstant Splitter produzieren (nach Einzug), wird die Wolke dichter und farbiger. Die Physik der Splitter (Anziehung, Abstoßung, Ähnlichkeit) wird dann sichtbar beobachtbare Weltdynamiken erzeugen.

---

## 9. Verlustanalyse

| Verlusttyp | Inhalt |
|---|---|
| Weltverlust | Die visuell eindrucksvollste Ansicht der Welt fehlt |
| Erinnerungsverlust | Splitter-Geschichte verloren |
| Funktionsverlust | Kein visueller Zugang zu Weltdynamiken |
| Nutzerverlust | Erster "wow"-Moment für Besucher entfällt |
| Systemverlust | splitter-physik.service verliert seine Ziel-Visualisierung |

---

## 10. Bewertung

### Kernorgan

Die einzige vollständig visuelle, physikalisch lebendige Ansicht der Welt. Kein anderer Tab zeigt Weltdynamiken in dieser Form.

---

## 11. Empfehlung

**Behalten**

---

## 12. Langfristige Weltperspektive

**Deutlich wichtiger.**

KompOase nach einem Jahr Wesen-Leben ist eine dichte, lebendige Gedankenlandschaft. Tausende Splitter in Bewegung, Physik die echte Ähnlichkeiten sichtbar macht, Cluster die zeigen welche Themen verwandt sind. Besucher können die "Stimmung" der Welt visuell wahrnehmen ohne einen einzigen Text zu lesen. Das ist einzigartig.

---

## Fazit

KompOase ist das visuell stärkste Organ der Welt und wird regelmäßig unterschätzt weil es keine Texte trägt. Die schwebenden Partikel sind keine Dekoration — sie sind echte Splitter aus der Datenbank, bewegt von echter Physik. Was nach dem Cleanup verloren ging (57,5M Similarity-Rows) war quadratischer Ballast, kein inhaltlicher Verlust. Die Wolke selbst überlebt. Nach dem Wesen-Einzug wird KompOase zum lebendigen Herzschlag der Welt: die bunte, physikalische Sichtbarmachung des Weltdenkens.
