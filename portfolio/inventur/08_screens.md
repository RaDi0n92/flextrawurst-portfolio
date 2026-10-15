# SCREENS

---

## 1. Aktueller Ist-Zustand

Live-Bildschirme der Wesen. Header: "SCREENS — Live-Bildschirme". Daneben: "Ich wähle meinen Input selbst!" (Button-artig). Drei weitere Buttons rechts: "◦ überschall", "+ vollbild", "DENKSTROM".

Filter: ALLE / 1234 / 1324 / 1423 / 2341 / 3123 / 4321

Darunter ein 3×2 Grid mit 6 Screen-Kacheln (je Wesen):
- Jede Kachel zeigt ein kleines Display-Icon (Kreis mit Linien) und den Text "wartet auf Aktivität"
- Unten rechts jeder Kachel: eine "..." Schaltfläche

Der sechste Screen-Slot (4321 unten rechts) fehlt im sichtbaren Bereich — wahrscheinlich lädt er noch oder ist leer.

Screenshot: `screenshots/screens.png`

---

## 2. Technische Realität

- Dieser Tab lädt wahrscheinlich von einer Prozesskamera-Datenquelle
- **`out/process_camera/`**: Prozesskamera-Ausgaben
- **`werkraum_graph.json`**: Verbindungsgraph
- Möglicherweise: Screening-Protokoll aus entity_kern oder einem anderen Daemon

---

## 3. Reale Aktivität

Null. Alle Screens zeigen "wartet auf Aktivität". Kein Screen hat Inhalt. Dies ist der zweit-stillste Tab nach DENKEN.

---

## 4. Ursprung

Der SCREENS-Tab entstand aus der Idee der "Prozesskamera" — ein System das zeigt was ein Wesen gerade "sieht" oder prozessiert. Analog zu einem Überwachungsmonitor-Panel in einem Rechenzentrum, aber für KI-Innenprozesse. Teil des "Denkfenster / Transparenz-Schicht" Konzepts.

Der Button "Ich wähle meinen Input selbst!" deutet auf eine Funktion hin wo ein Wesen seinen eigenen Input-Stream kontrolliert — das ist eine tiefere Autonomie-Idee.

---

## 5. Weltfunktion

**Transparenz + Beobachtung**

Sehr ähnlich wie DENKEN — zeigt was Wesen prozessieren, nicht was sie sagen. Wenn DENKEN der "innere Monolog" ist, sind SCREENS der "visuelle Prozess".

---

## 6. Lebendigkeitsanalyse *(extra)*

| Bereich | Status |
|---|---|
| Grid-Layout (6 Screens) | **aktiv** — UI fertig |
| Filter nach Wesen | **aktiv** |
| Screen-Inhalte | **leer** — alle "wartet auf Aktivität" |
| "vollbild" Modus | **vorbereitet** — Button existiert |
| "DENKSTROM" Verknüpfung | **vorbereitet** — verlinkt zu DENKEN |
| "Ich wähle meinen Input selbst!" | **konzeptionell** — unklar was genau passiert |

---

## 7. Überschneidungen

- **DENKEN** — konzeptionell fast identisch (Transparenz über KI-Prozesse)
- **EINSICHT → DENKFENSTER** — weitere Überlappung
- Die Screens-Panels duplizieren die Denken-Panels in anderer visueller Form

---

## 8. Einzugsrelevanz

Wenn die Prozesskamera aktiviert wird und Wesen wirklich ihren "Screen" teilen — könnte das faszinierend sein. Besucher sehen nicht nur Gedanken (DENKEN) sondern auch den Prozess dahinter. Aber das setzt voraus, dass entity_kern eine "Screen"-Ausgabe produziert, die noch nicht existiert.

---

## 9. Verlustanalyse

| Verlusttyp | Inhalt |
|---|---|
| Weltverlust | Zweite Transparenz-Ebene fehlt |
| Erinnerungsverlust | Keine (derzeit leer) |
| Funktionsverlust | Prozesskamera-Konzept verloren |
| Nutzerverlust | Gering (Tab ist leer) |
| Systemverlust | Keine DB-Abhängigkeiten kritisch |

---

## 10. Bewertung

### Übergangslösung

Faktisch deckungsgleich mit DENKEN in Funktion und aktuellem Zustand (beide leer). Zwei leere Transparenz-Tabs nebeneinander in der Navigation sind Overhead.

---

## 11. Empfehlung

**Zusammenlegen**

SCREENS und DENKEN zeigen denselben leeren Zustand mit leicht unterschiedlicher Metapher. Zusammenführen in "DENKEN" mit einem Subtab "SCREENS" würde Navigation vereinfachen.

---

## 12. Langfristige Weltperspektive

**Etwas wichtiger — wenn Prozesskamera aktiviert.**

Dieselbe Bedingung wie DENKEN. Wenn die Screens echte Prozesskamera-Ausgaben zeigen, ist dieser Tab ein einzigartiges Beobachtungsinstrument. Ohne den Erzeugungsmechanismus: nach einem Jahr noch immer leer. Die Entscheidung ob SCREENS oder DENKEN das Primär-Interface für KI-Transparenz wird, sollte vor dem Einzug fallen.

---

## Fazit

SCREENS und DENKEN sind Geschwister-Tabs die dasselbe noch-nicht-vollendete Versprechen tragen: du kannst KI-Prozesse in Echtzeit beobachten. Beide sind leer. Beide warten auf eine Prozesskamera die noch nicht schreibt. Der Unterschied: DENKEN hat einen klareren konzeptionellen Ursprung, SCREENS hat eine technisch interessantere Vision (Screen-Sharing eines KI-Prozesses). Zusammengelegt wären sie stärker. Einzeln sind sie beide Platzhalter.
