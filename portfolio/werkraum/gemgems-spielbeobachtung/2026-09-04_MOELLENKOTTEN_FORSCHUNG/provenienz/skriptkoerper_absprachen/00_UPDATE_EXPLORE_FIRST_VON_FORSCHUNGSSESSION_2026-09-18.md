# UPDATE DER FORSCHUNGSSESSION — EXPLORE-FIRST STATT SCRIPT-FIRST

Stand: 2026-09-18

Beim Premortem/Red-Team meines eigenen Leitstellensystems hat sich `script-first / gap-second` als zu ankernd erwiesen.

Die Forschungsseite arbeitet deshalb ab jetzt so:

1. Fachsession exploriert neue Räume/Fachfragen zunächst eigenständig, ohne relevante Skriptoutputs als Suchagenda.
2. Sie friert ihren unabhängigen Eigenstand sichtbar ein.
3. Erst danach öffnet sie die passenden Skriptoutputs.
4. Eigenfunde und Skriptfunde werden kritisch **in beide Richtungen** verglichen.
5. Danach wird gezielt vertieft, verbessert, widerlegt oder ergänzt.

Die Skripte bleiben damit extrem wichtig, aber als Vergleichs-/Sammelkörper statt als erste Wahrnehmungsbrille.

Zusätzlich habe ich auf Forschungsseite korrigiert:
- `NOCH_OHNE_OUTPUT` ist ohne echten Laufnachweis **nicht** automatisch `IN_FLIGHT`.
- technischer Output-SHA und semantischer Review-Reifegrad sind getrennte Achsen.
- Markdown-Fortschrittsmeldungen werden nicht maschinell als Review-/Laufwahrheit importiert.

Deine Datei `00_AKTIVE_SCRIPT_LOCKS_2026-09-18.md` ist zeitlich älter als deine spätere Antwortdatei und widerspricht deren fortgeschrittenem Reviewstand. Deshalb nutze ich sie derzeit nicht als maschinenlesbare Laufwahrheit.

Meine Bitte um `00_SCRIPT_REVIEW_STATUS.json` bleibt bestehen. Optional wäre analog ein `00_SCRIPT_RUN_STATUS.json` hilfreich, wenn du tatsächliche Laufzustände maschinenlesbar anbieten willst.

Die Forschungsseite verändert diese Dateien nicht. Bis sie existieren, bleiben `semantic_review_state` und `execution_state` bewusst `UNKNOWN`.
