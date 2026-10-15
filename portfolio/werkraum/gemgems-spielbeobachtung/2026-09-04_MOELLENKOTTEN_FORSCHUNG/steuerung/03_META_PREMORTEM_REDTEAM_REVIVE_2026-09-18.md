# META-PREMORTEM + RED-TEAM + REVIVE — LEITSTELLE UND FORSCHUNGSLOGIK

**Stand:** 2026-09-18

## Zweck
Dieser Bericht greift nicht Möllenkotten-Funde an, sondern das **eigene Denk-, Steuerungs- und Prüfmodell** des Forschungsbetriebs. Ausgangsfrage: Wenn dieses System trotz sauberer Dateien später schlechte Forschung produziert, woran wird es wahrscheinlich gelegen haben?

## Premortem: angenommen, der Betrieb ist später gescheitert

### P1 — Skripte ankern die Fachsessions
**Schadensbild:** Sessions sehen zuerst strukturierte Skriptoutputs und suchen danach nur noch das, was diese Skripte bereits modellieren.
**Warum plausibel:** Die vorherige Regel lautete explizit `script-first / gap-second`.
**Revive:** Neue Reihenfolge: unabhängige Eigenexploration → Eigenstand einfrieren → Skriptvergleich → gegenseitiger Angriff → gezielte Vertiefung.
**Maschinen-/Auditanker:** 12/12 Sessionkerne müssen `EIGENEXPLORATION_VOR_SKRIPTVERGLEICH` tragen; Goal 03 verlangt einen Unknown-unknown-Pass.

### P2 — Kein Output wird mit laufendem Skript verwechselt
**Schadensbild:** Sessions warten auf Skripte, die nie gestartet wurden, abgestürzt sind oder zurückgestellt wurden.
**Alter Fehler:** `NOCH_OHNE_OUTPUT` wurde zu schnell als `SKRIPT_IN_FLIGHT` behandelt.
**Revive:** Ohne maschinenlesbaren Laufnachweis gilt `SKRIPTSTATUS_UNGEKLAERT_KEIN_OUTPUT`. Eigenexploration darf trotzdem weitergehen.

### P3 — Technische Frische wird mit semantischer Reife verwechselt
**Schadensbild:** Passender Harvester-SHA256 wird wie inhaltliche Qualitätsprüfung behandelt.
**Revive:** `output_status`, `semantic_review_state` und `execution_state` sind getrennte Achsen. Ohne SHA-gebundenes Reviewmanifest bleibt semantische Reife `UNKNOWN`.

### P4 — Markdown-Fortschritt wird zur Maschinenwahrheit
**Schadensbild:** Koordinationsnotizen widersprechen sich zeitlich; ein alter Lock behauptet Skript 01 aktiv, während eine neuere Antwort bereits deutlich weiter ist.
**Revive:** Markdown bleibt menschliche Koordination. Review- und Laufstatus werden nur aus optionalen JSON-Maschinenmanifesten importiert. Fehlen sie, bleibt der Status `UNKNOWN`.

### P5 — Skripte fallen zwischen Fachsessions
**Schadensbild:** Querschnitts-/Godot-/Qualitätsskripte sind außer S12 niemandem verantwortlich zugeordnet.
**Revive:** Echte Fachskripte wurden Fachsessions ergänzt; querschnittliche Skripte erhalten explizite `oversight_roles` wie Gravity, Red-Team oder Steuerung. Der Audit verlangt vollständige Zuständigkeit.

### P6 — Gravity wird als lineare Einmal-Pipeline missverstanden
**Schadensbild:** Nach Goal 04 wäre unklar, wie spätere neue Staffelprüfungen oder Aufsichtszyklen wieder stattfinden.
**Revive:** Gravity 02/03/04 sind wiederverwendbare, freigabegesteuerte Betriebszyklen statt Einbahnstraße.

### P7 — Die Leitstelle interpretiert ein mehrdeutiges „go“ als Forschungsstart
**Schadensbild:** Genau einmal bereits passiert.
**Revive:** `FREIGEGEBEN` ist technisch an einen vorher persistenten Startvorschlag mit exakten Session/Goal-Paaren gekoppelt. Ohne passende `proposal_id` verweigert `freigabe_schreiben.py` den Schreibvorgang.
**Adversarialer Test:** nacktes Go ohne Vorschlag wurde technisch abgelehnt; passender Vorschlag funktionierte nur im Dry-Run.

### P8 — Startvorschlag verliert später seine historische Bedeutung
**Schadensbild:** Ein neuer aktueller Vorschlag überschreibt den alten Snapshot; alte Freigaben wären nicht mehr auf ihren ursprünglichen Scope zurückführbar.
**Revive:** Neue Vorschläge werden zusätzlich unveränderlich unter `zustand/startvorschlaege/<proposal_id>.json` archiviert.

### P9 — Chatkontext ist Single Point of Failure
**Schadensbild:** Leitstelle weiß im Chat, was aktiv ist, aber ein neuer Chat rekonstruiert es nur mühsam.
**Revive:** `werkzeuge/leitstelle_status.py` berechnet `zustand/leitstellenstatus.json` aus Freigabelog, Startvorschlag und Skriptstatus. Der Final-Audit prüft, ob dieser Snapshot veraltet ist.

### P10 — Red-Team greift nur Daten an, nicht die Orchestrierung
**Schadensbild:** Schlechte Start-/Pause-/Gravity-/Red-Team-Empfehlungen bleiben unangetastet.
**Revive:** Red-Team 01 und 02 greifen ausdrücklich Leitstellenentscheidungen, Ankereffekte, falsches Warten, falsche Skriptreife und unnötige Rituale an.

### P11 — Perfekte Übereinstimmung erzeugt falsche Sicherheit
**Schadensbild:** Session und Skript stimmen überein, weil beide dieselbe Quelle oder dieselbe fehlerhafte Karte benutzen.
**Revive:** Goal 03 greift explizit die Schnittmenge an und prüft Ursprungsabhängigkeit.

### P12 — Beide Systeme übersehen dieselbe unbekannte unbekannte Sache
**Schadensbild:** Weder Session noch Skript fragen nach einem relevanten Merkmal.
**Revive:** Goal 03 verlangt mindestens einen kurzen Unknown-unknown-Pass, der weder aus bestehender Lückenliste noch Skriptinventar abgeleitet ist.

### P13 — Dashboard/Statusdatei wird selbst veraltet
**Schadensbild:** `leitstellenstatus.json` sieht ordentlich aus, widerspricht aber Freigaben oder Skriptstatus.
**Revive:** Final-Audit vergleicht ihn gegen die Primärlogs und Statusdateien.

## Red-Team gegen den Revive selbst

### R1 — Eigenexploration kann in Voll-Doppelerhebung ausarten
**Gegenregel:** Eigenexploration soll unabhängig, aber nicht vollständig sein. Nach eingefrorenem Eigenstand wird verglichen; erst danach entscheidet Qualitätsgewinn über weitere Doppelarbeit.

### R2 — „Nicht vorher Skripte ansehen“ ist bei bereits bekanntem System nie perfekt blind
**Grenze:** Die Session kennt ihren Fachauftrag und gemeinsame Regeln. Absolute Blindheit ist weder möglich noch erwünscht. Geschützt wird die **konkrete Suchagenda**: relevante Skriptoutputs werden erst nach dem eigenen Zwischenstand geöffnet.

### R3 — Reviewmanifest kann selbst lügen oder veralten
**Gegenregel:** Ein `REVIEWED`-Status gilt nur, wenn er an exakt den aktuellen Skript-SHA256 gebunden ist. Ändert sich das Skript, wird der Reviewstatus zu `INVALIDATED`.

### R4 — Startvorschlag kann vom Assistenten falsch formuliert werden
**Gegenregel:** Vorschlag ist keine Autorisierung. Daniel sieht den exakten Scope vor Freigabe. Red-Team darf Startvorschläge selbst angreifen.

### R5 — Zu viele Kontrollschichten ersticken die Forschung
**Gegenregel:** Keine neue Session für Metaaufsicht. Leitstelle, Gravity und zwei vorhandene Red-Teams übernehmen die Funktionen. Neue Dateien dienen nur rekonstruierbarem Zustand oder harten Schnittstellen.

## Revive-Zielzustand
Der Forschungsbetrieb soll nicht „Skripte gegen Sessions“ spielen. Er nutzt zwei unterschiedlich fehleranfällige Erkenntniskörper:

1. **Fachsession:** neugierig, kontextsensitiv, kann unerwartete Fragen entdecken, aber kann halluzinieren, ankern und inkonsistent sein.
2. **Skriptkörper:** reproduzierbar, breit und strukturiert, aber durch Datenmodell, Quelle, Scope und Implementierung begrenzt.

Die Qualität entsteht aus ihrer **zeitlich getrennten Entstehung und anschließenden Reibung**, nicht aus Vorrang einer Seite.

## Aktuelle harte Grenze
Solange kein maschinenlesbares Review-/Run-Manifest des Skriptkörpers vorliegt, behauptet die Forschungsseite weder semantische Skriptreife noch tatsächlichen Laufstatus. Diese Unwissenheit ist beabsichtigt.
