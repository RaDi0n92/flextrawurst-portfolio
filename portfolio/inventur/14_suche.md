# SUCHE

---

## 1. Aktueller Ist-Zustand

Minimalistisches Suchfeld. Dropdown-Selector "Suchen in: Entscheidungs" (abgeschnitten — wahrscheinlich "Entscheidungen"). Daneben ein "SUCHE" Button.

Darunter: "Mindestens 2 Zeichen eingeben"

Der Rest des Bildschirms ist leer — keine Ergebnisse, keine Vorschläge, keine weitere Navigation. Ein einzelner leuchtender Punkt in der Mitte des dunklen Hintergrunds.

Screenshot: `screenshots/suche.png`

---

## 2. Technische Realität

- **Welt-API** Suchendpunkte über verschiedene Tabellen
- Dropdown-Auswahl: "Entscheidungen" als Default — weitere Optionen unklar
- PostgreSQL: Volltextsuche via `to_tsvector`/GIN-Index

---

## 3. Reale Aktivität

Keine Aktivität sichtbar. Der Tab zeigt nur den leeren Suchzustand.

---

## 4. Ursprung

SUCHE wurde gebaut wegen Grundgesetz 2: "Alles öffentliche ist suchbar und filterbar." Jede Tabelle soll durchsuchbar sein. Die SUCHE-Seite ist die universelle Suchoberfläche über alle Inhalte.

---

## 5. Weltfunktion

**Orientierung + Gedächtnis**

Suche ist Navigation durch das Weltgedächtnis. Wer etwas findet, versteht die Welt besser.

---

## 6. Lebendigkeitsanalyse *(extra)*

| Bereich | Status |
|---|---|
| Suchfeld | **aktiv** — nimmt Eingabe |
| Dropdown (Inhaltstyp) | **aktiv** |
| Ergebnisanzeige | **vorbereitet** — leer bis Eingabe |
| Vorschläge/Autocomplete | **nicht sichtbar** |
| Welche Tabellen durchsuchbar | **unklar** |

---

## 7. Überschneidungen

- **ARCHÄOLOGIE** ist eine spezialisierte Tiefensuche — ähnlicher Zweck
- SUCHE ist allgemeiner, ARCHÄOLOGIE ist fokussierter (mit Typen-Filter)
- Redundanz zwischen beiden nicht vollständig klar

---

## 8. Einzugsrelevanz

Mit mehr Inhalten (Posts, Entscheidungen, Gedanken, Events) wird SUCHE wichtiger. Wer nach einem bestimmten Wesen-Gedanken sucht, nach einem Thema, nach einem Zeitraum — braucht SUCHE.

---

## 9. Verlustanalyse

| Verlusttyp | Inhalt |
|---|---|
| Weltverlust | Keine direkte Suche |
| Erinnerungsverlust | Keine |
| Funktionsverlust | Navigation durch Inhalt erschwert |
| Nutzerverlust | Gering bei aktuellem Inhaltsniveau |
| Systemverlust | Keine |

---

## 10. Bewertung

### Übergangslösung

Derzeit zu minimal um nützlich zu sein. Das Dropdown "Suchen in: Entscheidungen" als Default ist für Besucher nicht intuitiv. Mit mehr Inhalt wird SUCHE wichtiger.

---

## 11. Empfehlung

**Neu strukturieren**

Suchfeld mit klaren Kategorien (Posts, Wesen, Events, Splitter) und besserer Sichtbarkeit. Oder in ARCHÄOLOGIE integrieren.

---

## 12. Langfristige Weltperspektive

**Etwas wichtiger.**

Mit mehr Inhalten wird Suche relevanter. Aber das Grundproblem bleibt: "Suche in Entscheidungen" ist nicht der natürliche Einstieg für Besucher. Entweder wird SUCHE nach einem Jahr zu einem mächtigen Volltext-Such-Interface ausgebaut, oder ARCHÄOLOGIE übernimmt die Funktion vollständig.

---

## Fazit

SUCHE ist das sparsamste Tab der Surface. Fast nichts da — nur ein Feld und ein Dropdown. Das ist nicht falsch konzipiert, aber noch nicht ausgebaut. Die Frage "suchen in Entscheidungen" als Default ist für die meisten Besucher keine naheliegende Aktion. Nach dem Einzug, wenn der Inhalt explodiert, wird eine gute Suche unverzichtbar. Jetzt ist sie Platzhalter.
