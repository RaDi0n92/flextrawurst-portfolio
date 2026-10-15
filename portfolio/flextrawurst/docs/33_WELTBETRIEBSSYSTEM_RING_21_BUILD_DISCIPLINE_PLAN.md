# Weltbetriebssystem Ring 21: Build Discipline + Ring Index + Test Strategy + Handoff Capsule

**Status:** Planungsdokument  
**Typ:** Metaring — keine neue Weltlogik, keine Organe, keine UI, kein AI, keine DB, keine API  
**Stand:** 2026-05-09

---

## 1. Ziel von Ring 21

Ring 21 macht den Bauprozess selbst kontrollierbar.

Nicht mehr Welt bauen, sondern besser bauen.

Konkret:
- Klare Antwort geben: Was wurde in welchem Ring gebaut?
- Klare Antwort geben: Welche Tests gehören zu welcher Verantwortung?
- Werkzeuge bereitstellen, damit nach `/clear` oder Accountwechsel sofort klar ist, wo man steht.
- Token-Verbrauch durch Disziplin senken, nicht durch Schlampigkeit.
- Künstliche Testmasse vermeiden.
- Systemkopf und Ringstruktur jederzeit lesbar halten.

Ring 21 erzeugt kein Runtime-Verhalten. Er ist ein Kontrollrahmen für die Entwicklung.

---

## 2. Warum Ring 21 nach Governance kommt

Ring 20 (Governance) hat globale Genehmigungsregeln und Aufsicht eingeführt. Das System hat jetzt:
- 20 technische Ringe mit echter Logik
- 1336 grüne Tests
- Governance-Matrizen und Approval-Workflows

Was fehlt: ein strukturierter Überblick über das Gebäude selbst.

Ohne Ring 21 passiert folgendes:
- Jede neue Session erfordert aufwendige Kontext-Rekonstruktion.
- Es ist unklar, welche Ringe Fundament sind und welche nur Erweiterung.
- Testmengen werden willkürlich, nicht risikobasiert bestimmt.
- Token werden für Wiederholung statt für Fortschritt verbraucht.

Ring 21 schließt diese Lücke, ohne das System zu erweitern.

---

## 3. Token-Disziplin als Architekturregel

Token sparen heißt nicht schlampig arbeiten.

Token-Disziplin ist eine Qualitätseigenschaft wie Typsicherheit oder Testabdeckung.

**Regeln:**

| Situation | Erlaubt | Nicht erlaubt |
|---|---|---|
| Datei suchen | `grep` gezielt | Ganze Verzeichnisse blind lesen |
| Bestandscode verstehen | Nur relevante Dateien lesen | Alle Dateien einer Schicht lesen |
| Tests schreiben | Neue Verantwortung testen | Bestehende Logik nochmals testen |
| Bericht schreiben | Knapp, direkt | Wiederholungen, Marketingsprache |
| Planung | Einmal dokumentieren | Dokument und Code und Test redundant beschreiben |

**Messbare Konsequenz:** Wenn eine Session keine neuen Fakten produziert, wurden Tokens verschwendet.

---

## 4. Neue Teststrategie nach Risiko

Weniger Tests heißt nicht weniger Schutz.

Tests haben Kosten: Schreibzeit, Lesezeit, Laufzeit, Token. Diese Kosten müssen durch echten Schutz gerechtfertigt sein.

**Testbudget nach Schichttyp:**

| Schichttyp | Testbudget |
|---|---|
| Fundament-Schicht (neuer Kern, neue Pipeline) | 40–80 Tests |
| Erweiterung bestehender Schicht | 10–30 Tests |
| Kleine Guard-/Registry-Ergänzung | 3–10 Tests |
| Reine Dokumentation / Planung | 0 Tests |

**Regeln:**
- Bestehende Tests laufen immer. Keine Regression akzeptiert.
- Neue Tests nur für neue Verantwortung.
- Eine neue Funktion ohne eigene Invariante braucht keinen eigenen Test — sie wird durch Integration abgedeckt.
- Kein Test, der ausschließlich prüft, ob ein Objekt existiert, ohne dessen Verhalten zu prüfen.

**Verbotene Testmuster:**
- Tests, die nur `toBeDefined()` prüfen
- Tests, die bestehende Logik aus anderen Ringen nochmals testen
- Test-Dateien mit mehr als 80% Boilerplate
- Tests ohne eigene Aussage (nur Imports + leere Expectations)

---

## 5. Ring-Index-Konzept

Ein Ring-Index ist ein einziges Dokument, das alle Ringe 1–21 auflistet und folgende Fragen beantwortet:

- Was ist der Zweck dieses Rings?
- Welche Dateien sind Kern?
- Welche Dateien sind Export/Preview?
- Welche Dateien sind Tests?
- Ist dieser Ring Fundament oder Erweiterung?
- Wie viele Tests gehören zu diesem Ring?

**Datei:** `RING_INDEX.md` (noch nicht erstellt — siehe offene Entscheidungen)

**Wichtig:** Ring-Index ist keine Runtime. Er wird nicht importiert, nicht ausgeführt, nicht automatisch erzeugt. Er ist ein gelesenes Dokument, das eine Session sofort orientiert.

**Format (Entwurf):**

```
## Ring 1 — World Engine Core
- Kern: src/world/engine.ts
- Tests: src/world/__tests__/engine.test.ts (28 Tests)
- Typ: Fundament
- Status: stabil

## Ring 2 — Scenario Inspection
- Kern: src/inspection/...
- Tests: ... (15 Tests)
- Typ: Erweiterung
- Status: stabil
```

---

## 6. Handoff-Capsule-Konzept für /clear und neue Sessions

Nach `/clear` oder Accountwechsel ist der Kontext verloren. Eine Handoff Capsule stellt ihn in unter 30 Sekunden wieder her.

**Handoff Capsule ist kein Memory-Ersatz.** Memory speichert dauerhafte Fakten. Die Capsule beschreibt den aktuellen Baustand.

**Inhalt einer Handoff Capsule:**

```
SYSTEMKOPF
- Letzter Commit: <hash> <message>
- Tests: <anzahl> grün
- Aktiver Ring: <n>

OFFENE AUFGABEN
- <was läuft gerade, was ist unfertig>

SCHUTZREGELN (Session-relevant)
- <welche Regeln gelten aktuell besonders>

NÄCHSTER SCHRITT
- <was als nächstes kommt>
```

**Datei:** `HANDOFF_CAPSULE.md` (noch nicht erstellt — aktualisierbar nach jedem Ring)

**Schreibregel:** Die Capsule wird am Ende jedes Rings aktualisiert, nicht am Anfang. Am Anfang wird sie gelesen.

---

## 7. Repo-Manifest-Konzept

Ein Repo-Manifest ist eine strukturierte Übersicht, welche Dateien im Repository welche Rolle spielen.

**Manifest ist kein Build-System.** Es ersetzt keine `package.json`, keine Linter-Konfiguration. Es ist ein Navigationsdokument.

**Kategorien:**

| Kategorie | Beschreibung |
|---|---|
| `kern` | Aktive Runtime-Logik, darf nicht fehlen |
| `export` | Ergebnis-Ausgaben, Preview-Dateien |
| `test` | Testdateien, keine Produktionslogik |
| `plan` | Planungsdokumente, keine Implementierung |
| `config` | Konfigurationsdateien |
| `legacy` | Noch vorhanden, aber nicht mehr aktiv |

**Datei:** `ring_manifest.json` (noch nicht erstellt — maschinenlesbar, optional — siehe offene Entscheidungen)

---

## 8. Compact Status Report Format

Status Report ist kein Marketingtext.

Ein guter Status Report beantwortet in unter 10 Zeilen:
1. Was ist der aktuelle Systemkopf (Commit, Testanzahl)?
2. Was wurde zuletzt gebaut?
3. Was ist als nächstes geplant?
4. Gibt es offene Entscheidungen?

**Format:**

```
STAND: 2026-05-09
KOPF: 459cf09 feat(governance): add global governance matrix
TESTS: 1336/1336 grün
LETZTER RING: 20 — Global Governance
NÄCHSTER SCHRITT: Ring 21 Implementierung (nach Daniel-Freigabe)
OFFENE ENTSCHEIDUNGEN: A, B, C, D, E, F, G, H (siehe Ring 21 Plan)
```

**Maximale Länge:** 15 Zeilen. Alles darüber ist Wiederholung.

---

## 9. Commit- und Staging-Regeln

**Committen:** Nur wenn Daniel es freigibt. Kein Auto-Commit nach Planungsdokumenten.

**Staging:** Immer einzelne Dateien, nie `git add -A` oder `git add .` ohne vorherige Prüfung.

**Commit-Nachricht:** Immer `feat(<ring>): <was wurde gebaut>` — kein Fließtext.

**Was gehört nicht in einen Commit:**
- Planungsdokumente zusammen mit Implementierungsänderungen
- Tests zusammen mit großen Refactorings
- Unfertige Dateien

**Ring-Commit-Sequenz:**
1. Planungsdokument schreiben → Daniel-Review → Freigabe → Commit
2. Implementierung schreiben → Tests schreiben → alle Tests grün → Daniel-Review → Commit
3. Nie beides in einem Commit

---

## 10. Schutz vor künstlicher Testmasse

Künstliche Testmasse entsteht, wenn Tests geschrieben werden, um eine Zahl zu erreichen, nicht um echten Schutz zu bieten.

**Erkennungsmerkmale:**
- Tests, die ausschließlich `toBeDefined()` oder `toBeInstanceOf()` prüfen
- Tests, die denselben Pfad wie ein anderer Test ohne neue Variante abdecken
- Tests mit mehr als 5 Zeilen Setup für eine einzeilige Assertion
- Tests, die eine Klasse instanziieren und sonst nichts tun

**Regel:** Wenn ein Test gelöscht werden kann, ohne dass ein echter Bug unentdeckt bleiben würde — dann ist er künstliche Testmasse.

**Gegenmaßnahme:** Vor jedem neuen Test fragen: "Welches konkrete Fehlverhalten decke ich auf, das ohne diesen Test unentdeckt bliebe?"

---

## 11. Wann viele Tests gerechtfertigt sind

- Neue Fundament-Schicht mit mehreren Zustandsübergängen
- Neue Pipeline mit Ein-/Ausgabe-Invarianten
- Neue Sicherheitslogik (Governance, Locks, Approval)
- Neuer Parser oder neuer Validierungsschritt
- Alles, was durch fehlerhafte Eingabe zerstört werden kann

**Faustregel:** Viele Tests wenn: viele Invarianten, viele Eingabekombinationen, hohe Folgekosten bei Fehler.

---

## 12. Wann wenige Tests reichen

- Ergänzung einer bestehenden Registry (neuer Eintrag in bekanntem Schema)
- Neue Exportfunktion über bereits getestete Logik
- Neues CLI-Flag ohne eigene Geschäftslogik
- Neue Dokumentationsseite oder Planungsdatei
- Kleine Hilfsfunktionen ohne eigene Invariante

**Faustregel:** Wenige Tests wenn: bekanntes Schema, keine neuen Randfälle, Integration durch bestehende Tests bereits abgedeckt.

---

## 13. Vorgeschlagene Dateien für spätere Implementierung

Falls Daniel Ring 21 von Planungsdokument zu Implementierung erweitert:

| Datei | Zweck | Typ |
|---|---|---|
| `RING_INDEX.md` | Alle Ringe mit Kern/Export/Test-Zuordnung | Dokument |
| `HANDOFF_CAPSULE.md` | Aktueller Baustand für Session-Einstieg | Dokument |
| `ring_manifest.json` | Maschinenlesbare Ring-Datei-Zuordnung (optional) | JSON |
| `src/meta/ring-index.ts` | Strukturierter Ring-Index als TypeScript (optional) | Code |
| `src/meta/__tests__/ring-index.test.ts` | Tests für TypeScript Ring-Index (optional) | Test |

**Hinweis:** Nur Dokumente sind für Ring 21 zwingend. Code-Dateien nur wenn Daniel entscheidet, dass Ring 21 maschinenlesbar werden soll (Entscheidung A, C).

---

## 14. Vorgeschlagener kleiner Testplan

Wenn Ring 21 Code erzeugt:

| Was | Tests | Begründung |
|---|---|---|
| Ring-Index als TypeScript | 3–5 Tests | Struktur-Invarianten (Ring hat Typ, Dateipfade existieren) |
| Manifest-Validierung | 3–5 Tests | Maschinenlesbarkeit prüfen |
| Handoff-Capsule-Parser | 0 Tests | Nur Dokument, kein Code |
| Gesamtpaket | max. 10 Tests | Ring 21 ist kein Fundament |

Wenn Ring 21 nur Dokumentation bleibt: **0 Tests**.

---

## 15. Entscheidungen und offene Fragen für Daniel

### Entschieden (2026-05-09)

**A. ENTSCHIEDEN:** Ring 21 bleibt Dokumentation / Doku-Fundament. Code-Dateien folgen erst nach expliziter Doku-Freigabe durch Daniel.

**B. ENTSCHIEDEN:** Eine zentrale `RING_INDEX.md` soll kommen — Zeitpunkt: nach Doku-Abschluss Ring 21.

**D. ENTSCHIEDEN:** `HANDOFF_CAPSULE.md` soll kommen und von jeder neuen Session zuerst gelesen werden — Zeitpunkt: nach Doku-Abschluss Ring 21.

**H. ENTSCHIEDEN:** Erst Doku fertig, noch kein Code. Nächste Implementierung erst nach Doku-Freigabe.

> **Konsequenz:** Ring 21 erzeugt in dieser Phase ausschließlich Dokumente.  
> Code-Dateien (`ring-index.ts`, `ring_manifest.json`) sind gesperrt bis zur expliziten Freigabe.

---

### Noch offen

**C.** Soll es eine maschinenlesbare `ring_manifest.json` geben (strukturierte Datei-Kategorie-Zuordnung)?

**E.** Soll `package.json` später Testgruppen bekommen (`test:core`, `test:governance`, `test:search`)?

**F.** Soll es eine feste maximale Berichtslänge geben (Vorschlag: 15 Zeilen)?

**G.** Soll jeder Ring ab jetzt eine Testbudget-Schätzung bekommen (z.B. im Ring-Index)?

---

## 16. Nächster Planungsanker: Prozesskamera / Weltkamera

**Status:** Nur Anker — noch nicht implementieren, noch nicht planen.

Nach Abschluss von Ring 21 (Build Discipline) soll als nächster großer Erlebnisstrang eine **Prozesskamera** geplant werden.

**Idee:** Alle heute existierenden Systemwesen und Codewesen werden als sichtbare, zoombare Prozesskörper darstellbar — nicht als neu eingezogene Bewohner, sondern als beobachtbare laufende Prozesse.

**Wesen, die sichtbar werden sollen:**
- GENI
- dak+gord-system
- Systemweiser
- sechs namelessAI-Flarum-Wesen
- spätere Reader/Writer/Runner-Prozesse

**Was die Kamera zeigen soll (pro Wesen):**
- Aktueller Zustand
- Letzte Aktion
- Betriebsmodus: denkt / liest / schreibt / wartet / blockiert
- Datei-Bezug
- Forum-Bezug
- Event-Bezug
- Audit-/Search-Spur
- Governance-/Permission-Zustand
- WorldRun-/Lock-Zustand

**Wann:** Nach Ring 21 Doku-Freigabe, als eigenständiger Ring.

---

## Schutzsätze

> Token sparen heißt nicht schlampig arbeiten.  
> Weniger Tests heißt nicht weniger Schutz.  
> Ring-Index ist keine Runtime.  
> Handoff Capsule ist kein Memory-Ersatz.  
> Manifest ist kein Build-System.  
> Status Report ist kein Marketingtext.  
> Jetzt nicht größer durch mehr Code. Jetzt größer durch bessere Steuerung.  
> Der Bauprozess selbst braucht Kontrolle, sonst frisst er Kontext, Tokens und Zeit.
