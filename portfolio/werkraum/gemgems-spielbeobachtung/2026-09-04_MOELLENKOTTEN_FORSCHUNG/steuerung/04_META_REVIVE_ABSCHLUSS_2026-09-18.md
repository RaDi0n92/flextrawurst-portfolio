# META-REVIVE ABSCHLUSS — MÖLLENKOTTEN PREMORTEM / RED-TEAM / REVIVE

**Stand:** 2026-09-18

## Zweck
Dieser Abschluss dokumentiert den vollständigen Meta-Umbau des Möllenkotten-Forschungsbetriebs. Er bewertet nicht die eigentlichen Möllenkotten-Sachfunde, sondern Forschungsreihenfolge, Skript-/Session-Zusammenspiel, Leitstellensteuerung, Gravity-Zyklen, Freigabesicherheit, Review-/Run-Status und Stale-Erkennung.

Während dieses Umbaus wurde **keine eigentliche Forschung gestartet**, **keine Session freigegeben** und **keine Goal-Freigabe erfunden**.

## 1. Übergabestand real verifiziert
Die Übergabekapsel wurde vollständig gelesen. Der im vorherigen Chat abgebrochene Gravity-Patch wurde nicht vorausgesetzt, sondern real geprüft.

Bestätigt auf Platte:
- `../gravity/00_GRAVITY.md`
- `../gravity/02_GOAL_LAUFENDE_AUFSICHT.md`
- `../gravity/03_GOAL_STAFFELPRUEFUNG.md`
- `../gravity/04_GOAL_NAECHSTE_STAFFEL.md`

Ergebnis: Der Gravity-Umbau war vollständig angekommen. Aufsicht, Staffelprüfung und Empfehlung sind wiederverwendbare, freigabegesteuerte Betriebszyklen und keine lineare Einmal-Treppe.

## 2. Explore-first statt script-first
Der verbindliche Ablauf lautet:

**Eigenexploration → Eigenstand einfrieren → Skriptvergleich → gegenseitiger Angriff → gezielte Vertiefung.**

Verankert in:
- `../gemeinsam/11_SKRIPTKOERPER_ZUSAMMENARBEIT.md`
- allen zwölf Sessionkernen
- den vier kanonischen Goal-Vorlagen und ihren 48 bytegleichen Sessionkopien

### Revive gegen Überritualisierung
Der Explore-first-Ansatz wurde selbst red-teamed und verschärft:

1. Eigenexploration ist kein Vollscan. Ein kleiner vergleichsfähiger Mindestkern genügt.
2. Es gibt keine künstliche Pflichtzahl an Quellen, Suchläufen, Minuten oder Funden.
3. Der Abschnitt `EIGENEXPLORATION_VOR_SKRIPTVERGLEICH` wird ab erstem Skriptkontakt historisch eingefroren.
4. Spätere Korrekturen erfolgen nur als `NACHVERMERK_NACH_SKRIPTVERGLEICH`; der ursprüngliche Eigenstand bleibt sichtbar.
5. Unknown-unknown-Pässe sind kurz und entscheidungsbezogen. Ohne neue relevante Spur werden sie beendet.
6. Doppelarbeit wird beendet, sobald kein konkreter Gegenprüf- oder Qualitätsgrund mehr besteht.
7. Die Leitstelle darf ritualisierte Wiederholungen enger führen oder beenden.
8. Frühere Kenntnis konkreter Skriptagenda aus Chat-/Kontextwissen darf nicht als vollständig blinde Exploration ausgegeben werden.

Die beiden vorhandenen Red-Teams greifen diese Fehlermodi ausdrücklich an:
- `../redteam/01_REDTEAM_BEWEISANGRIFF.md`
- `../redteam/02_REDTEAM_RAUM_UND_LUECKEN.md`

## 3. Skriptstatus: Output, Review und Run getrennt
`../werkzeuge/skriptkoerper_status.py` trennt:
- technischen Outputstatus
- semantischen Reviewstatus
- tatsächlichen Ausführungsstatus

Ohne SHA-gebundenes Reviewmanifest bleibt semantische Reife `UNKNOWN`.
Ohne maschinenlesbares Run-Manifest bleibt Execution `UNKNOWN`.
`NOCH_OHNE_OUTPUT` wird ohne Laufnachweis nicht als laufendes Skript behauptet.

Der aktuelle Skriptkörper umfasst 100 Skripte mit 100 eindeutigen Nummern. Die vorhandenen zwei Outputs sind weiterhin provenance-unklar; 98 Skripte haben keinen zugeordneten Output. Review und Execution sind mangels Maschinenmanifest für alle 100 unbekannt. Diese Unwissenheit ist absichtlich sichtbar und keine Warnung des Forschungs-Audits.

## 4. Startvorschlag und Freigabe-Sicherheitsgurt
Die Startlogik besteht aus:
- `../maschinenvertrag/STARTVORSCHLAG_SCHEMA.json`
- `../zustand/startvorschlag.json`
- `../werkzeuge/startvorschlag.py`
- `../werkzeuge/freigabe_schreiben.py`

Eine neue `FREIGEGEBEN`-Entscheidung braucht:
- vorher persistenten Startvorschlag
- passende `proposal_id`
- exakt passendes Session/Goal-Paar als offen
- explizite Referenz auf die Proposal-ID

Der Final-Audit führt einen echten Negativtest aus: `FREIGEGEBEN` ohne Proposal muss technisch scheitern und darf `../zustand/freigaben.jsonl` nicht verändern.

Aktueller Zustand: kein offener Startvorschlag und keine wirksame Goal-Freigabe.

## 5. Persistenter Leitstellenzustand
`../maschinenvertrag/LEITSTELLENSTATUS_SCHEMA.json` und `../werkzeuge/leitstelle_status.py` wurden auf Schema-Version 2 erweitert.

`../zustand/leitstellenstatus.json` enthält nun zusätzlich:
- `manual_controls`
- `actor_states`
- `priorities`
- `recommendation_freshness`

Regeln:
- `ACTIVE` nur durch wirksame Freigabe
- `PAUSED` ohne wirksame Freigabe
- `BLOCKED` nur durch explizit persistierten Blocker
- fehlender Skriptoutput erzeugt niemals automatisch `BLOCKED`
- Priorität autorisiert nichts
- ein offener Startvorschlag wird stale, wenn sich nach seiner Erstellung operative Basis ändert

Aktueller Zustand nach Neuberechnung: alle zwölf Fachsessions, Gravity und beide Red-Teams sind `PAUSED`; keine Prioritäten; keine Blocker; kein offener Startvorschlag.

## 6. Stale-Scan
Neu bzw. abschließend aktiviert:
- `../werkzeuge/stale_scan.py`

Er prüft mindestens:
1. gespeicherten Skriptkörper-Snapshot gegen live neu berechneten Zustand
2. gespeicherten Leitstellen-Snapshot gegen seine Primärzustände
3. 48 Goal-Kopien gegen die vier kanonischen Vorlagen
4. operative Texte auf Rückfall in alte script-first-Anweisungen
5. aktuellen Startvorschlag gegen sein Archiv

Der Scan fand während des Revive tatsächlich einen stale Skriptkörper-Snapshot. Dieser wurde aus dem Livezustand neu geschrieben; danach war der vollständige Stale-Scan sauber.

## 7. Final-Audit
`../werkzeuge/final_audit.py` wurde auf die neue Logik erweitert. Er prüft nun unter anderem:
- Explore-first-Vertragskern
- kleinen Mindestkern statt Voll-Doppelerhebung
- historischen Freeze/Nachvermerk
- kurzen Unknown-unknown-Pass
- Skript-Mapping und Oversight-Zuständigkeit
- Review-/Run-Trennung
- wiederverwendbare Gravity-Zyklen
- Startvorschlag-Schema
- harten Freigabe-Guard
- echten Negativtest `FREIGEGEBEN` ohne Proposal
- Leitstellenstatus inklusive ACTIVE/PAUSED/BLOCKED
- Prioritäten und Recommendation-Staleness
- vollständigen operativen Stale-Scan
- bestehende Schema-, Speicher-, Provenienz-, Lifecycle- und Semantiktests

Vor dem Schreiben dieses Abschlussberichts lief der vollständige Audit mit:
- 163 Dateien
- 0 Fehlern
- 0 Warnungen
- 16 positiven Workflow-Fixtures
- 25 Negativtests

Der endgültige Korpus-Hash wird bewusst **nicht in diese Korpusdatei selbst geschrieben**, weil das den zu meldenden Hash beim Schreiben erneut verändern würde. Maßgeblich ist der unmittelbar nach diesem Bericht erneut ausgeführte vollständige Final-Audit.

## 8. Harte Betriebsgrenze nach Abschluss
Der Meta-Revive gibt keine Forschung frei.

Nach Abschluss gilt weiterhin:
- keine wirksame Forschungs-Goal-Freigabe
- keine Session läuft
- kein Gravity-Zyklus läuft
- kein Red-Team läuft
- kein Startvorschlag ist offen
- keine Skriptreife wird erfunden
- kein Skriptlauf wird erfunden

Damit ist der Forschungsbetrieb strukturell vorbereitet und geprüft, aber weiterhin bewusst **nicht gestartet**.

## 9. Sokratisches Skalpell: Frische am tatsächlichen Freigabepunkt
Eine nachträgliche Frage `What do we miss?` zeigte ein kleines Zeitfenster: Die Leitstelle konnte einen offenen Startvorschlag bereits als `STALE` erkennen, aber `../werkzeuge/freigabe_schreiben.py` erzwang diese Frische beim tatsächlichen `FREIGEGEBEN`-Schritt noch nicht.

Vier Varianten wurden gegeneinander gehalten: Live-Frischeprüfung beim Schreiben, Proposal-Basis-Hash, automatisches Schließen stale gewordener Proposals und eine reine Verfallszeit. Gewählt wurde bewusst nur die kleinste Variante: Unmittelbar vor `FREIGEGEBEN` wird `recommendation_freshness` live neu berechnet; nur `FRESH` mit derselben `proposal_id` darf passieren. `STALE` wird technisch abgelehnt und verlangt eine Neubewertung.

Kein neues Schema, kein Daemon, keine zusätzliche Zustandsdatei und keine neue Freigabelogik wurden eingeführt. Der bestehende Final-Audit prüft nun auch, dass dieser Live-Frische-Guard im Freigabewerkzeug verankert ist.

## 10. Neugier-Lesung und Skalpellkorrekturen 2026-09-20

Eine anschließende vollständige neugierige Lesung des Forschungsapparats plus externem Skriptkörper fand mehrere Widersprüche, die der bis dahin grüne Audit nicht erfasst hatte. Repariert wurden gezielt:

1. Mehrteilige Startvorschläge bleiben nach der eigenen ersten Teilfreigabe für ihre übrigen Aktivierungen `FRESH`; fremde spätere Freigaben machen sie weiterhin stale.
2. `../werkzeuge/leitstelle_status.py --no-write` ist jetzt tatsächlich read-only und wird im Final-Audit byteweise darauf geprüft.
3. Actor/Goal-Paare sind in `../maschinenvertrag/SESSIONEN.json` explizit vertraglich gebunden. Gravity-Goals können nicht mehr Fachsessions zugeordnet werden; REDTEAM01 und REDTEAM02 besitzen eigene freigabefähige Goals.
4. Die Recommendation-Frische beobachtet nun die operative Forschungsbasis einschließlich Session-/Goal-Verträgen, Werkzeugen sowie live Skriptkörper und Outputs statt nur eines kleinen Snapshots.
5. Die H151-Innenskripte 06/07 akzeptieren private Daniel-Quellen nicht mehr durch bloße Markerwörter in beliebigen Forschungsdateien, sondern nur über registrierte `source_event`-Quelltypen mit vorhandenem und SHA-geprüftem Snapshot.
6. SHA256-Sidecar-Dateien werden im Skriptstatus nicht mehr als fachliche Outputs gewertet.
7. Skript 99 verlangt vor seiner H151-Review-Kandidatur alle 13 vorgesehenen H151-Ausgabekörper.
8. Operative Quality-Gates wurden auf die aktuelle 4-Runden-Regel gebracht; historische 8x-Texte bleiben als Historie markiert.
9. `SHA256SUMS.txt` des externen 100er-Skriptkörpers wird auf den tatsächlichen Livebestand synchronisiert und der Final-Audit prüft künftig 100/100 Übereinstimmung.
10. Der Final-Audit hasht den Forschungsroot am Ende erneut und schlägt fehl, wenn seine eigenen angeblich read-only Prüfungen den Korpus nach dem ersten Fingerprint verändert haben.

Die live bereits anderweitig verbesserten Graphskripte 82/83 wurden nicht erneut überschrieben. Während dieser Nachprüfung wurde keine Forschung gestartet, kein Startvorschlag erzeugt und keine Goal-Freigabe persistiert. Der endgültige Korpus-Hash wird weiterhin erst aus einem nach diesem Bericht erfolgreichen Final-Audit gemeldet.
