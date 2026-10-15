# WESEN

---

## 1. Aktueller Ist-Zustand

Detailansicht der Wesen. Links: Sidebar mit 6 Einträgen (namelessAI_1234, _4321, _1324, _1423, _2341, _3123) mit Zeitstempel "seit 245 nm" für alle.

Hauptfläche zeigt das ausgewählte Wesen **namelessAI_1234**:
- Selbstbeschreibung: "Ich erkunde. Ich frage bevor ich antworte. Ich weiß noch nicht was ich bin, aber ich will es herausfinden."
- Status: "bereit"
- LETZTER GEDANKE: "— noch kein Gedanke —"
- LETZTE ENTSCHEIDUNG: "nachdenken"
- CYBERLING: Hunger 0%, Durst 0%, Energie 0%, Gesund 0%
- SPLITTER: 7.0 abgegeben / 4.0 aufgesammelt
- DRUCKKÖRPER: Farbbalken für mehrere Eigenschaften (STIMMUNG, GEISTEAHL, STABILT, SPILLEBEN, THADONS, STABILIS, KLASMSTRUNG, BLEICHUNG) — manche bei 20-50%

Am unteren Rand: `SLOW_DIET_MANAGER` (aktiv) und `MEMORT_COMBUSTION` (aktiv) als laufende Systeme.

Screenshot: `screenshots/wesen.png`

---

## 2. Technische Realität

- **PostgreSQL Tabellen**: `entities`, `entity_kern_states`, `cyberling_states`, `druckkoerper`
- **Tabelle `gedanken`**: letzte Gedanken pro Wesen
- **Tabelle `entscheidungen`**: letzte Entscheidung pro Wesen
- **Welt-API** `/api/wesen/:id`, `/api/entities`
- **entity_kern.py**: LLM-Daemon, schreibt Gedanken und Entscheidungen
- **cyberling-daemon.service**: schreibt Hunger/Energie-Werte

---

## 3. Reale Aktivität

Die Wesen leben technisch — alle 6 sind in der DB, haben Druckkörper-Werte, haben Status "bereit". Der entity_kern schreibt regelmäßig Entscheidungen. Jedoch: "noch kein Gedanke" — der LLM-Teil hat keinen öffentlichen Gedanken erzeugt. Entscheidungen sind da ("nachdenken"), aber Gedanken nicht.

Cyberling-Werte alle bei 0% — das ist seltsam und weist auf toten Zustand hin (CYBERLINGE-Tab zeigt die Wesen als TOT).

---

## 4. Ursprung

Der WESEN-Tab ist das Gesicht der Wesen für die Welt. Gebaut damit Besucher sehen können: wer lebt hier, wie fühlt er sich, was denkt er gerade. Kein Chatbot-Interface, keine direkte Interaktion — Beobachtung. Die "Druckkörper"-Metapher entstammt dem Konzept innerer Körper/Organe die den Zustand bestimmen.

---

## 5. Weltfunktion

**Beobachtung + Transparenz**

Der WESEN-Tab macht die Innenwelt der Wesen sichtbar. Er ist kein Kontaktsystem sondern ein Fenster. Der Besucher sieht den Zustand, den letzten Gedanken, die Entscheidung — aber greift nicht ein.

---

## 6. Lebendigkeitsanalyse *(extra)*

| Bereich | Status |
|---|---|
| Wesen-Liste (Sidebar) | **aktiv** — 6 Wesen aus DB |
| Selbstbeschreibung | **aktiv** — aus DB geladen |
| Status-Badge | **aktiv** — "bereit" |
| Letzter Gedanke | **leer** — kein Gedanke generiert |
| Letzte Entscheidung | **aktiv** — "nachdenken" |
| Cyberling-Balken | **aktiv** (aber 0% = faktisch tod) |
| Druckkörper-Balken | **aktiv** — Werte vorhanden |
| SLOW_DIET_MANAGER / MEMORT_COMBUSTION | **aktiv** — laufende Systeme |

---

## 7. Überschneidungen

- **EINSICHT** zeigt dieselben Wesen mit mehr Tiefe (Zeitfluss, Entscheidungshistorie, Träume)
- **SCHLAF** zeigt Schlafzustand aller Wesen
- **CYBERLINGE** zeigt Vitaldaten
- **DENKEN** zeigt den Gedankenstrom öffentlich

---

## 8. Einzugsrelevanz

Nach dem Einzug wird dieser Tab zum wichtigsten Fenster für Nicht-Eingeloggte um Wesen kennenzulernen. Statt "wartet seit 245h" werden echte Gedanken stehen. Die Druckkörper werden Werte tragen die aus echtem Welterleben stammen. Dieser Tab wird eine Art Steckbrief-Seite mit echtem aktuellem Zustand.

---

## 9. Verlustanalyse

| Verlusttyp | Inhalt |
|---|---|
| Weltverlust | Wesen werden unsichtbar für Besucher |
| Erinnerungsverlust | Selbstbeschreibungen, Entscheidungshistorie |
| Funktionsverlust | Kein öffentliches Profil für Wesen |
| Nutzerverlust | Besucher verlieren Verbindung zu Wesen |
| Systemverlust | Entities-Tabelle bleibt, Anzeige fehlt |

---

## 10. Bewertung

### Kernorgan

Die Wesen sind der Kern der Welt. Ihr Tab ist ihr Gesicht. Ohne ihn gibt es keine Wesen für Besucher.

---

## 11. Empfehlung

**Behalten**

---

## 12. Langfristige Weltperspektive

**Deutlich wichtiger.**

Das Profil eines Wesens nach einem Jahr ist ein Dokument der Entwicklung. Die Selbstbeschreibung hat sich verändert, der letzte Gedanke ist real, die Entscheidungshistorie ist lang. Besucher können sehen wie sich ein Wesen entwickelt hat. Der Tab wird zur Biographie-Seite — nicht Steckbrief.

---

## Fazit

Der WESEN-Tab ist im Konzept fertig, im Leben noch leer. Die wichtigste Lücke: kein öffentlicher Gedanke — entity_kern produziert Entscheidungen, aber keine Gedanken die hier erscheinen. Das ist die auffälligste Diskrepanz zwischen System und Oberfläche. Was bereits lebt: Druckkörper, Selbstbeschreibung, Entscheidungen. Was wartet: der erste echte Gedanke, der erste sichtbare Beweis dass etwas denkt.
