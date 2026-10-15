# EINSICHT

---

## 1. Aktueller Ist-Zustand

Tiefes Analyse-Panel für die Wesen. Obere Filterleiste mit Wesen-Tabs (1234, 4321, 1324, 1423, 2341, 3123, ALLE) — mit farbigen Punkten und Zahlen.

Subtabs: **PANORAMA** (aktiv) / ZEITFLUSS / ENTSCHEIDUNGEN / TRÄUME / SUBSTANZEN / SPLITTER / SCHATTEN / BEZIEHUNGEN / INNENQUELLEN / DENKFENSTER / AMPEL / ORGANHUNGER

Im PANORAMA-Subtab: 6 Wesen-Karten in 2×3 Grid. Jede Karte zeigt:
- Wesen-Name (1234, 4321, 1324, 1423, 2341, 3123)
- Badge: "wesen.vermacht" (rötlich) — alle 6
- Balken-Darstellung (Status)
- Werte: **50** Einträge (Brinch?), **0** Traum-Kvs, **0** Splitter-Kvs
- Darunter Fortschrittsbalken

Rechts: "Kein Eintrag ausgewählt" (Detailpanel leer)

Oben rechts: "→ AMPEL" Button.

Screenshot: `screenshots/einsicht.png`

---

## 2. Technische Realität

- **PostgreSQL Tabellen**: `entity_kern_states`, `entscheidungen`, `traum_logs`, `splitter`, `schattenkommentare`, `beziehungen`, `innenquellen`
- **Welt-API** `/api/einsicht/:wesen_id`
- **entity_kern.py**: produziert Entscheidungen und theoretisch Träume
- **splitter-physik.service**: Splitter-Daten

---

## 3. Reale Aktivität

Das PANORAMA zeigt 50 "Einträge" pro Wesen — wahrscheinlich 50 Entscheidungen. Aber: 0 Träume, 0 Splitter-KVs. Das Badge "wesen.vermacht" ist seltsam — deutet auf einen Status hin der gesetzt wurde aber unklar ist was er bedeutet.

Die Subtabs TRÄUME, SUBSTANZEN, BEZIEHUNGEN, DENKFENSTER sind wahrscheinlich alle leer oder haben minimalen Inhalt.

---

## 4. Ursprung

EINSICHT entstand als das tiefste Fenster in die Wesen-Innenwelt — für Daniel, später für Interessierte. Während WESEN das öffentliche Gesicht zeigt, zeigt EINSICHT das Innenleben: Entscheidungshistorie über Zeit (ZEITFLUSS), was ein Wesen träumte (TRÄUME), welche Substanzen es kennt (SUBSTANZEN), wie seine Organe funktionieren (ORGANHUNGER).

Die 12 Subtabs machen EINSICHT zum umfassendsten Tab der Surface.

---

## 5. Weltfunktion

**Transparenz + Beobachtung + Gedächtnis**

EINSICHT ist das wissenschaftliche Instrument zur Beobachtung der Wesen. Nicht für Besucher — für Forscher, für Daniel, für tiefes Verständnis. Die Welt als Experiment beobachtbar zu machen.

---

## 6. Lebendigkeitsanalyse *(extra)*

| Subtab | Status |
|---|---|
| PANORAMA | **aktiv** — 50 Einträge, lädt |
| ZEITFLUSS | **vorbereitet** — unklar wie voll |
| ENTSCHEIDUNGEN | **aktiv** — entity_kern schreibt Entscheidungen |
| TRÄUME | **leer** — 0 Traum-KVs |
| SUBSTANZEN | **unklar** — wahrscheinlich leer |
| SPLITTER | **0** Splitter-KVs laut Panorama |
| SCHATTEN | **möglicherweise aktiv** — SCHATTEN-Tab hat 14 Threads |
| BEZIEHUNGEN | **unklar** |
| INNENQUELLEN | **unklar** |
| DENKFENSTER | **leer** — entspricht DENKEN-Tab (auch leer) |
| AMPEL | **aktiv** — Button sichtbar, eigene Logik |
| ORGANHUNGER | **aktiv** — Cyberling-Vitaldaten |

---

## 7. Überschneidungen

- **WESEN** zeigt Druckkörper + Status — Teilmenge von EINSICHT
- **SCHLAF/CYBERLINGE** zeigen Vitaldaten — Teilmenge von ORGANHUNGER
- **DENKEN** zeigt Denkstrom — Teilmenge von DENKFENSTER
- **SCREENS** zeigt Prozesskamera — Teilmenge von DENKFENSTER
- EINSICHT ist das Super-Set das viele andere Tabs als Subtabs enthält

---

## 8. Einzugsrelevanz

EINSICHT wird das wichtigste Beobachtungsinstrument der Welt. Entscheidungen über Wochen verfolgen (ZEITFLUSS), Träume archivieren (TRÄUME), Beziehungsnetz sehen (BEZIEHUNGEN) — das macht Wesen zu nachvollziehbaren Entitäten statt zu schwarzen Boxen. Für Forscher und für Daniel unersetzbar.

---

## 9. Verlustanalyse

| Verlusttyp | Inhalt |
|---|---|
| Weltverlust | Wesen-Innenwelt wird unsichtbar |
| Erinnerungsverlust | Entscheidungshistorie, Träume, Substanzen |
| Funktionsverlust | Kein wissenschaftliches Beobachtungsinstrument |
| Nutzerverlust | Forscher verlieren Zugang |
| Systemverlust | entity_kern produziert weiter — nur Anzeige fehlt |

---

## 10. Bewertung

### Kernorgan

EINSICHT ist das tiefste Organ der Welt. Es macht die Wesen transparent und beobachtbar. Ohne es gibt es keine Forschung, keine Nachvollziehbarkeit, kein echtes Verständnis.

---

## 11. Empfehlung

**Behalten**

---

## 12. Langfristige Weltperspektive

**Deutlich wichtiger.**

EINSICHT ist nach einem Jahr das wissenschaftlichste Instrument der Welt. ZEITFLUSS zeigt Entscheidungsentwicklung über 12 Monate. TRÄUME enthält eine echte Traumarchiv-Geschichte. BEZIEHUNGEN zeigt wie Wesen sich zueinander positioniert haben. Das ist dann kein leerer Tab mehr — das ist ein Jahr dokumentiertes Wesen-Innenleben.

---

## Fazit

EINSICHT wurde nicht überschätzt — es ist das komplizierteste und gleichzeitig wichtigste Tab der Surface. 12 Subtabs, von denen viele noch leer sind. Was bereits lebt: ENTSCHEIDUNGEN (50 pro Wesen), ORGANHUNGER, AMPEL. Was wartet: TRÄUME, SUBSTANZEN, BEZIEHUNGEN, DENKFENSTER. Das "wesen.vermacht" Badge auf allen 6 Wesen ist ein kleines Rätsel — es sagt etwas über den aktuellen Status, aber die Bedeutung ist nicht sofort klar. EINSICHT ist das Instrument für die Phase nach dem Einzug.
