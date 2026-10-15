# Red Team, Premortem und Red Team gegen das Premortem (Stand 2026-10-02)

Gegenstand: die Skills `skill-schreiben` und `bridge-praxistest`, die Praxis-Harness und die
Antworten aus `SOKRATES_SKILLS_UND_HARNESS.md`.

Vorgehen von Hand, ohne Skript: je Runde Angriffe sammeln, Urteil fällen, Verbesserung festhalten.

## Teil A: Red Team gegen die Antworten, drei Runden

### Runde 1

| Angriff | Urteil | Verbesserung |
|---|---|---|
| „Gesamtregression grün“ gilt nur für den Stand vor den Szenarien und dem Skill `skill-schreiben`. | stimmt | Aussage trägt jetzt den Stand; ein neuer Lauf wurde gestartet (Ergebnis unten). |
| Die Zeilenzählung (über 160 Zeichen) misst gröber als die Regel (etwa 100). | stimmt | Neu gezählt ohne Tabellen und Code: 17 und 24 Zeilen über 100 Zeichen. |
| „Beschreibungs-Optimierer nicht vorhanden?“ war ungeprüft. | stimmt | Geprüft: `run_loop.py`, `improve_description.py`, `run_eval.py`, `quick_validate.py` liegen vor. Validator läuft: beide Skills „valid“. |
| Die Ursache des Claude-Abbruchs steht als Tatsache da. | zu stark | Belegt ist: Dialog war sichtbar (Terminalaufnahme), Startnachricht wurde danach getippt, Exit 1. Gemgem-Host endete ohne Tippen mit Exit 1, also gibt es mindestens eine weitere Ursache. Nach der Korrektur lief Claude-Host weiter: Indiz, kein Beweis. Aussage: „sehr wahrscheinlich“. |
| „Scrubber wie ein Film“ überzieht. | stimmt | Kapseln halten je Agent höchstens zehn Bilder. Aussage: Zeitraffer aus Ereignissen und Standbildern. |
| Eine Repo-Datei zählt Fehler einzeln auf. | stimmt, schwerwiegend | Doku auf „Erfüllt / Offen“ umgestellt, ohne Rückblick auf Vorgänge. |
| Was die Antwort ganz übersah: Erscheint die Ansage wirklich in der Raute? | **wichtigster Fund** | Der Körper tippt nur unter Bedingungen (Hände an, kein Not-Aus, nicht beschäftigt, nicht „nur Terminal“). Die Harness bucht die Ansage schon beim Senden als erledigt. Das untergräbt Regel 0. Als P0 geführt. |

### Runde 2 (Angriff auf die verbesserte Fassung)

| Angriff | Urteil | Verbesserung |
|---|---|---|
| Die Reihenfolge setzt Doku vor den Fund aus Runde 1. | stimmt | P0 (Bestätigung der Ansage) steht vor allem anderen. |
| Pimp-Ideen stehen neben Pflichten und lenken ab. | stimmt | Pimp in eigene Liste „erst nach P0 und P1“. |
| Klick-Ringe: Machbarkeit unbelegt. | stimmt | Als Idee mit Prüfpunkt; erst kleiner Test auf vd1. |
| Paket 0.10.1 vor der Käfig-Änderung baut doppelt. | stimmt | Erst alle Körperänderungen (Bestätigung der Ansage, Menü-Freigabe), dann ein Paket. |
| „valid“ des Validators beweist Wirkung nicht. | stimmt | Er prüft Form. Wirkung belegen nur Evals mit echten Anfragen. Steht so im Dokument. |

### Runde 3 (Angriff auf Runde 2)

| Angriff | Urteil | Verbesserung |
|---|---|---|
| Zu viele P0. Daniel kann nicht alles zugleich prüfen; wann sieht er etwas? | stimmt | Zwischenlösung ohne Code, sofort: Der Handelnde sagt jeden Schritt **zusätzlich per `say`** an (Banner und Ticker, sichtbar). Das gehört in den Skill, bis die Bestätigung gebaut ist. |
| Annahme „Daniel liest jede Ansage“ verkennt die Last bei 23 Schritten. | stimmt | Lesezeit einstellbar machen (`--lesezeit=`); Tafel mit Countdown; Knopf „nicht verstanden“. |
| Der Maßstab war nur Dokumente. Der echte Maßstab ist Daniels Erleben. | stimmt | Erfolgsmaß: Konnte Daniel jeden Schritt ohne Rückfrage nachvollziehen? Gemessen über seine „nicht verstanden“-Markierungen. |
| „Behoben“ ohne Gate ist wieder nur Behauptung. | stimmt | Jede Verbesserung gilt erst nach einem Gate im Ledger. Bis dahin steht „geplant“. |

### Ergebnis der drei Runden: verbesserte Reihenfolge

1. **P0 Bestätigung der Ansage** (Körper meldet, ob die Raute getippt hat; Harness öffnet den
   Knoten nur dann, sonst freundliche Hilfe und `say` als Notbehelf).
2. **Vorflug-Check** vor Schritt 1.
3. **Käfig-Freigabe für Bridge-Menüs** mit Liste erlaubter Einträge.
4. **Ein** Paketbau (0.10.1) mit allen Körperänderungen; Doku und Abnahme nachziehen.
5. Dann Tafel, Klick-Ringe, Kapseln und Seeds aus dem Lauf.

## Teil B: Premortem gegen die Skills und die Harness

Annahme: Zwei Wochen später gilt der Praxistest als gescheitert. Warum?

Wahrscheinlichkeit ist geschätzt, nicht gemessen. Zuverlässiger sind die Frühindikatoren.

| Nr | Ursache des Scheiterns | Geschätzt | Frühindikator | Gegenmaßnahme |
|---|---|---|---|---|
| 1 | Die Ansage erscheint nicht sichtbar in der Raute. | hoch | Daniel sieht nichts, Harness meldet „angesagt“ | P0 (Bestätigung), `say` als Notbehelf |
| 2 | Ein Agent findet den Skill nicht (besonders Gemgem/agy). | hoch | kein `test start` binnen fünf Minuten | Startsatz von Daniel mit Pfad; Harness erklärt sich selbst über `test karte`; Entscheidung für Daniel: Startnachricht ergänzen |
| 3 | Spuren sind leicht zu erfüllen, ohne dass etwas Sinnvolles geschah. | mittel | gleiche Spur mehrfach in Folge, Bild unverändert | Spur ist notwendig, nicht hinreichend: Zuschauerblick, Daniels Markierung, Hinweis bei unverändertem Bild |
| 4 | Ein Agent klickt etwas Gefährliches (STOP, „Bridge beenden“) und beendet den Test. | mittel | Körper meldet Beenden | Menü-Freigabe nur mit Liste erlaubter Einträge; Szenario markiert „nicht anklicken“ |
| 5 | Ein Agent ändert Szenario oder Skill, statt den Schritt zu tun (Dateien sind beschreibbar). | niedrig bis mittel | Hash des Szenarios ändert sich im Lauf | Hash im Protokoll, Warnung bei Änderung |
| 6 | Neustart des Starters zerstört den Lauf. | hoch | Lauf weg, Agenten beendet | `test weiter` liest das Protokoll; `--ab=N` besteht schon |
| 7 | Daniel greift ein; die Lesezeit läuft weiter. | mittel | Schritt ohne Lesen übersprungen | Lesezeit pausiert bei Übernahme |
| 8 | Leselast und Ermüdung bei Daniel (23 Schritte, je mehrere Texte). | hoch | Daniel bricht ab | einstellbare Lesezeit, Tafel, kurze Ansagen |
| 9 | Szenarien veralten, wenn sich die Oberfläche ändert. | mittel | Schritt passt nicht mehr zum Bild | `erwartet`-Knoten pro Szenario wie bei Abläufen |
| 10 | Die Vorlage der Ansage wird ohne Nachdenken benutzt. | mittel | alle Ansagen gleichlautend | Karte nennt Vorlage nur als Hilfe; Zuschauer darf „zu knapp“ sagen |
| 11 | Skill und Werkzeug laufen auseinander. | mittel | Prüfer meldet fehlende Befehle | Skill-Tests laufen in der Regression (bestehen schon) |
| 12 | Öffentliche Version enthält Daniels Pfade. | sicher, später | Pfade `/root/werkraum` | Pfade konfigurierbar vor dem Export |

## Teil C: Red Team gegen das Premortem

| Angriff | Urteil | Verbesserung |
|---|---|---|
| Das Premortem ist technisch gedacht. Es fehlen Daniel (Ermüdung, Freude) und die Sicht der Agenten (wann geben sie auf?). | stimmt | Ursache 8 und 10 vertieft; Erfolgsmaß aus Runde 3 aufgenommen; Agenten-Reibung wird im Lauf erfasst (`test entdeckung`). |
| Es kennt nur, was ich mir vorstellen kann. | stimmt | Ein **naiver Agent** (ohne Vorwissen, frisches Terminal) liest nur den Skill und startet; seine Stolpersteine sind die unbekannten Risiken. |
| Die Gegenmaßnahmen sind selbst neue Komplexität (Hash, Pause, Tafel, Bestätigung). | stimmt | Kleinster Satz zuerst: Bestätigung, Vorflug, Menü-Liste. Rest erst nach dem ersten echten Lauf. |
| Die Schätzungen wirken genauer, als sie sind. | stimmt | Als „geschätzt“ markiert; Entscheidungen hängen an Frühindikatoren. |
| Es fehlt ein Erfolgsbegriff. | stimmt | Erfolg heißt: mindestens 20 von 23 Schritten sichtbar durchgeführt, kein Schritt ohne Ansage, mindestens 90 Prozent der Schritte von Daniel ohne Rückfrage verstanden, Befundliste vollständig. |
| Die Menü-Freigabe könnte gar nicht machbar sein (Menüs sind eigene Fenster, die Aufnahme zeigt nur das Zielfenster). | berechtigt | Erst ein **Spike** (kleiner Versuch): Menü öffnen, Aufnahme prüfen, einen Klick im Menü versuchen. Danach erst bauen. |
| Ursache 2 lässt sich nur mit Daniels Entscheidung lösen (Startnachricht). | stimmt | Als Frage an Daniel geführt, nicht allein umgesetzt. |

### Verbessertes Premortem in einem Satz

Die größten Gefahren sind eine unsichtbare Ansage, ein nicht gefundener Skill und ein Test, der Daniel
ermüdet; wir schließen sie mit Bestätigung, Vorflug, Startsatz und einstellbarer Lesezeit und prüfen
alles Übrige erst am ersten echten Lauf mit einem naiven Agenten.

## Offene Entscheidungen für Daniel

1. Soll die Startnachricht der Agenten den Skill nennen (alle Agenten betroffen)?
2. Darf die Ansage vorerst doppelt erfolgen (`schreibe` und `say`), bis die Bestätigung gebaut ist?
3. Welche Menüeinträge der Bridge dürfen Agenten bedienen, welche nie („Bridge beenden“)?

## Teil D: Red Team gegen Aufblähung (Skill `skill-schreiben` samt Harness)

Frage: Ist der Skill, der Skills und Programm-Harness zusammenfasst, zu viel geworden?

### Messung vorher

- Beschreibung 743 Zeichen, Körper 823 Wörter in sechs Abschnitten.
- Dopplungen: „Regeln für den Text“ wiederholte Schritt 3 und 4 des Weges, die Checkliste
  „Vor dem Abgeben“ wiederholte den Prüfer, die Python-Anleitung zum Erweitern stand im Körper statt
  in der Referenz.
- Der Skill beschrieb eigene Prüf- und Erprobungsschritte, obwohl der Skill-Creator sie mitbringt
  (`quick_validate.py`, `run_eval.py`, `run_loop.py`, `improve_description.py`).
- Zeilen über 100 Zeichen: 24 (`skill-schreiben`) und 17 (`bridge-praxistest`) im Körper, dazu mehrere
  in den Referenzen.

### Eingriffe

- Abschnitt „Regeln für den Text“ auf sechs Zeilen verdichtet, Schritt 3 und 4 verweisen nicht mehr
  doppelt. Checkliste gestrichen, denn der Prüfer ist die Checkliste.
- Erweitern (Spurart, Rolle, Kante) in `references/szenario-schema.md` Abschnitt 6 verlegt.
- Schritt 6 und 7 nutzen die Werkzeuge des Skill-Creators, statt sie zu beschreiben.
- Der Prüfer kennt jetzt die Lesbarkeitsregel (Zeilen über 110 Zeichen, ohne Tabellen, Code und Adressen).
- Beide Skills und alle Referenzen von Hand auf kurze Absätze gebracht.

### Messung nachher

| | vorher | nachher |
|---|---|---|
| `skill-schreiben`: Beschreibung | 743 Zeichen | 519 Zeichen |
| `skill-schreiben`: Körper | 823 Wörter | 442 Wörter |
| Prüfer-Befunde beider Skills | Hinweise vorhanden | 0 Fehler, 0 Hinweise |
| Validator des Skill-Creators | nicht gelaufen | beide „valid“ |

### Angriff auf das Ergebnis

- Ist `bridge-praxistest` mit 695 Wörtern noch zu lang? Urteil: Er ist der Skill, den Agenten in
  der Praxis lesen. Der Rhythmus (sechs Schritte), „Warum“ und die Ausreden-Tabelle tragen das
  Befolgen; gekürzt wird erst, wenn der Erprobungslauf zeigt, was nie gelesen wird.
- Doppelt der Skill `skill-schreiben` den Skill-Creator? Urteil: nur dort, wo Bridge-Wissen hinzukommt
  (Harness, Befehlsprüfung, Szenario-Gerüst, Lesbarkeit). Alles Allgemeine verweist auf ihn.
- Ist der Prüfer mit seinen vielen Regeln selbst aufgebläht? Urteil: 170 Zeilen, jede Regel hat einen
  Test mit Gegenprobe. Neue Regeln nur mit solchem Beleg.
- Offen: Ob der Skill im Gebrauch trägt, zeigt nur ein Erprobungslauf mit einem naiven Agenten.
