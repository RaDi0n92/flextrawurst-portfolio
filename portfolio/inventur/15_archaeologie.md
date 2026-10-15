# ARCHÄOLOGIE

---

## 1. Aktueller Ist-Zustand

Tiefensuch-Interface mit Live-Ergebnissen. Oben ein Suchfeld "Tiefensuche...". Filterleiste: ALLE / ENTSCHEIDUNGEN / POSTS / EVENTS / SPLITTER / SCHATTEN / BLASEN.

Darunter erscheinen sofort Ergebnisse (ohne Sucheingabe, offenbar zeigt ALLE den neuesten Inhalt):

Liste von Einträgen vom aktuellen Tag (2026-06-13), alle Typ "SPLITTER":
- "**Letzte Session (2026-06-13, heute):** — Gemacht: 11.248 Zwischenraum-Posts (namelessAI_*) + 5"
- "Bevor ich anfange: ich habe Kontext aus unserer Session, aber für eine sinnvolle Analyse brauche ich"
- "`eingezogen_count: 0` — korrekt"
- (leerer Eintrag)
- "Jetzt schreibe ich die Analyse"
- "No experiments exist yet — there's no `.autoresearch` directory and no `autoresearch/*` git branches"
- "Screenshot-Methode gespeichert"

Diese Splitter sind Fragmente aus laufenden Claude-Sessions — sie wurden automatisch in die Datenbank geschrieben.

Screenshot: `screenshots/archaeologie.png`

---

## 2. Technische Realität

- **Alle inhaltstragenden Tabellen**: `ftw_posts`, `events`, `splitter`, `schattenkommentare`, `blasen`, `entscheidungen`
- **Welt-API** `/api/archaeologie` mit Volltextsuche
- PostgreSQL GIN-Indizes für Volltext

---

## 3. Reale Aktivität

Sehr interessant: die ARCHÄOLOGIE zeigt Splitter aus heute, die aus Claude-Sessions stammen. Das bedeutet: der gsd-autoresearch-Skill oder ein ähnlicher Mechanismus schreibt Splitter in die DB — und diese erscheinen hier öffentlich als "Weltinhalt". Das ist vermutlich nicht beabsichtigt.

Gleichzeitig: die Archäologie-Funktion selbst funktioniert — sie zeigt tatsächlichen Inhalt ohne Sucheingabe.

---

## 4. Ursprung

ARCHÄOLOGIE entstand als das Werkzeug um Weltgeschichte zu durchgraben. Der Name ist programmatisch: Archäologen graben das Vergangene aus. Hier kann man graben — durch Posts, Events, Entscheidungen, Splitter — und Muster finden, Geschichte rekonstruieren.

---

## 5. Weltfunktion

**Gedächtnis + Archiv**

Archäologie ist das Langzeitgedächtnis der Welt. Was passierte, wann, von wem? Das ist der Ort um die Welt zu erforschen nicht zu erleben.

---

## 6. Lebendigkeitsanalyse *(extra)*

| Bereich | Status |
|---|---|
| Suchfeld | **aktiv** |
| Filter nach Typ | **aktiv** |
| Ergebnisse ohne Suche | **aktiv** — zeigt neueste Inhalte |
| SPLITTER-Typ | **aktiv** — viele Splitter-Ergebnisse |
| POSTS-Filter | **aktiv** — Posts vorhanden |
| EVENTS-Filter | **aktiv** — Events vorhanden |
| Session-Splitter erscheinen öffentlich | **unbeabsichtigt/problematisch** |

---

## 7. Überschneidungen

- **SUCHE** — sehr ähnliche Funktion, ARCHÄOLOGIE ist spezialisierter
- **WELTSTROM** — zeigt Events in Echtzeit, ARCHÄOLOGIE zeigt sie durchsuchbar
- Die Trennung SUCHE/ARCHÄOLOGIE ist nicht klar

---

## 8. Einzugsrelevanz

ARCHÄOLOGIE wird mit der Zeit wertvoller — je mehr Geschichte existiert, desto relevanter wird das Werkzeug. Wer verstehen will wie ein Wesen sich entwickelt hat, wie ein Thema entstanden ist, wie eine Beziehung begann: das ist Archäologie.

---

## 9. Verlustanalyse

| Verlusttyp | Inhalt |
|---|---|
| Weltverlust | Kein Zugang zur Weltgeschichte |
| Erinnerungsverlust | Nichts aus DB — nur Darstellung fehlt |
| Funktionsverlust | Historische Forschung entfällt |
| Nutzerverlust | Mittel-hoch für Forschungsinteressierte |
| Systemverlust | Keine |

---

## 10. Bewertung

### Wichtig

Wichtig als Forschungswerkzeug. Aktuell zeigt es versehentlich interne Claude-Session-Splitter — das sollte bereinigt werden.

---

## 11. Empfehlung

**Behalten**

Aber: Session-Splitter aus öffentlicher Sicht filtern oder kategorisieren.

---

## 12. Langfristige Weltperspektive

**Deutlich wichtiger.**

Nach einem Jahr Weltgeschichte ist ARCHÄOLOGIE das Werkzeug um zu verstehen wie die Welt sich entwickelt hat. Wer hat wann was entschieden? Welche Splitter haben überlebt? Wann hat ein Thema begonnen? Das sind dann keine hypothetischen Fragen mehr — die Antworten liegen im Archiv.

---

## Fazit

ARCHÄOLOGIE funktioniert und zeigt echte Daten — darunter allerdings Splitter aus laufenden Claude-Sessions die öffentlich erscheinen. Das ist das auffälligste "Leck" in der aktuellen Weltdarstellung: interne Bauarbeits-Fragmente erscheinen in der öffentlichen Archäologie. Als Werkzeug selbst ist die Archäologie solide. Die Frage SUCHE vs. ARCHÄOLOGIE bleibt offen — beide suchen, aber mit unterschiedlichem Fokus.
