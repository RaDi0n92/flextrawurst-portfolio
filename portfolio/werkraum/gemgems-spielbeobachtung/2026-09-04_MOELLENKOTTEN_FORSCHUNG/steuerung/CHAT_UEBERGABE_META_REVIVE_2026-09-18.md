# CHAT-ÜBERGABE — MÖLLENKOTTEN META-REVIVE
Stand: 2026-09-18

## Hauptauftrag
Fortsetzung des Premortem + Red-Team + Revive + Verbessern gegen das gesamte Möllenkotten-Forschungs-/Leitstellensystem.
Keine eigentliche Forschung starten. Keine Session freigeben. Keine Goal-Freigabe erfinden.

## Neue Kernlogik
Die Fachsessions sollen NICHT zuerst Skripte sehen.
Ablauf:
1. eigenständig neugierig/explorativ suchen und sammeln
2. Eigenstand vor Skriptkontakt festhalten
3. erst danach passende Skripte/Outputs öffnen
4. Eigenfunde und Skripte kritisch gegeneinander prüfen
5. Widersprüche, Lücken und Unknown-unknowns suchen
6. erst danach gezielt vertiefen, verbessern, nachrecherchieren oder verwerfen

## Bereits umgesetzt
- gemeinsam/11_SKRIPTKOERPER_ZUSAMMENARBEIT.md auf Explore-first umgebaut
- alle 12 sessions/*/00_SESSIONKERN.md auf Explore-first umgebaut
- EIGENEXPLORATION_VOR_SKRIPTVERGLEICH in Sessionkernen verankert
- vier kanonische Goal-Vorlagen neu geschrieben
- 48/48 Session-Goal-Kopien danach synchronisiert
- NOCH_OHNE_OUTPUT ist nicht mehr automatisch SKRIPT_IN_FLIGHT
- ohne Laufnachweis: SKRIPTSTATUS_UNGEKLAERT_KEIN_OUTPUT
- OUTPUT_AKTUELL bedeutet technische Frische, nicht semantische Reife

## Skriptstatus-Scanner erweitert
werkzeuge/skriptkoerper_status.py kennt jetzt getrennt:
- output status
- semantic_review_state
- semantic_review_completed_rounds
- semantic_review_required_rounds
- semantic_review_evidence_path
- semantic_review_bound_sha256
- execution_state
Optionale Maschinenmanifeste im Skriptroot:
- 00_SCRIPT_REVIEW_STATUS.json
- 00_SCRIPT_RUN_STATUS.json
Ohne diese Manifeste bleibt Review=UNKNOWN und Execution=UNKNOWN.
Letzter geprüfter Livezustand: 100 Skripte, 100 eindeutige Nummern, 98 NOCH_OHNE_OUTPUT, 2 OUTPUT_UNKLARE_PROVENIENZ, Review 100x UNKNOWN, Execution 100x UNKNOWN.

## Skript-Mapping
maschinenvertrag/SKRIPT_SESSION_MAPPING.json wurde erweitert.
Querschnittliche Skripte bekommen oversight_roles für GRAVITY/REDTEAM01/REDTEAM02/STEUERUNG statt künstlich einer Fachsession zugeordnet zu werden.
Letzter Check: unowned 0.

## Freigabe-Sicherheitsgurt
Neu:
- maschinenvertrag/STARTVORSCHLAG_SCHEMA.json
- zustand/startvorschlag.json
- werkzeuge/startvorschlag.py
werkzeuge/freigabe_schreiben.py wurde gehärtet:
- FREIGEGEBEN braucht vorher persistenten Startvorschlag
- proposal_id zwingend
- Session/Goal muss als PENDING im Vorschlag stehen
- reference muss proposal_id enthalten
- nacktes 'go' ohne Proposal wird technisch abgelehnt
Adversarial getestet: ohne Proposal abgelehnt; passender Proposal im Dry-Run erlaubt; Testproposal danach CLOSED.
Keine echte Forschungsfreigabe aktiv.

## Cross-Session-Absprache
Skriptroot: /root/werkraum/kosmos/skripte_moellenkotten_100/
Markdown-Fortschrittsmeldungen dort sind menschliche Koordination, keine Maschinenwahrheit.
00_AKTIVE_SCRIPT_LOCKS_2026-09-18.md war zeitlich älter und widersprach späterem Fortschritt.
Darum Lauf-/Reifestatus nur aus SHA-gebundenen Maschinenmanifesten importieren.

## Premortem-Befunde
1. NOCH_OHNE_OUTPUT wurde zu schnell als laufend behandelt.
2. technische Frische wurde zu leicht mit semantischer Reife vermischt.
3. script-first hätte Sessions ankern können.
4. Mapping hatte querschnittliche/herrenlose Skripte.
5. Gravity war zu linear als 01→02→03→04 modelliert.
6. Leitstellenwissen war zu stark nur Chatkontext.
7. nacktes 'gogogo' wurde einmal fälschlich als Gesamtstart interpretiert.
8. Markdown-Status aus der Skript-Session kann stale/widersprüchlich sein.

## WICHTIG — letzter offener Punkt
Der vorherige Chat endete während eines Toolcalls, der Gravity auf wiederverwendbare Betriebszyklen patchen sollte:
- gravity/00_GRAVITY.md
- gravity/02_GOAL_LAUFENDE_AUFSICHT.md
- gravity/03_GOAL_STAFFELPRUEFUNG.md
- gravity/04_GOAL_NAECHSTE_STAFFEL.md
Im neuen Chat zuerst den tatsächlichen Dateistand prüfen. NICHT annehmen, dass dieser letzte Patch vollständig angewendet wurde.

## Danach noch offen
1. Gravity-Zyklus-Rewrite fertigstellen.
2. Leitstellenzustand persistenter machen: aktiv/pausiert/blockiert, Prioritäten, Empfehlung-Staleness.
3. Red-Team gegen Explore-first: künstlich lange Eigenexploration, ritualisierte Unknown-unknowns, explodierende Doppelarbeit, nachträglich geschönter Eigenstand, früheres Skriptwissen aus Kontext.
4. Revive dafür: kleiner Mindestumfang statt Voll-Doppelerhebung; Eigenexplorationsabschnitt historisch/immutable; Leitstelle darf ritualisierte Doppelarbeit abbrechen.
5. final_audit.py aktualisieren: alten script-first/gap-second-Check entfernen und Explore-first + Startvorschlag + Mapping + Review/Run-Status + Negativtest FREIGEGEBEN-ohne-Proposal prüfen.
6. Stale-Scan über operative Dateien.
7. vollständigen Final-Audit laufen lassen.
8. Premortem-/Red-Team-/Revive-Bericht dauerhaft ablegen.
9. erst bei 0 Fehler / 0 Warnungen neuen Korpus-Hash melden.
10. keine eigentliche Forschung starten.

## Letzter sauber auditierter Stand VOR Meta-Revive
151 Dateien, 0 Fehler, 0 Warnungen, 16 positive Workflow-Fixtures, 25 Negativtests.
Korpus-SHA256: 95f5d16f179a66f1829c1d5537acc6ef831477a6491d6914ab890b36455a1acb
Dieser Hash ist nach dem Meta-Revive nicht mehr aktuell.

## Start im neuen Chat
1. Diese Datei vollständig lesen.
2. aktuellen VPS-Zustand dagegen abgleichen.
3. zuerst Gravity-Dateien prüfen.
4. Meta-Revive exakt an der offenen Stelle fortsetzen.
5. keine Forschung starten.

## Abschlussvermerk desselben Tages
Der hier als offen beschriebene Meta-Revive wurde später am 2026-09-18 vollständig fortgesetzt. Maßgeblicher Abschlussstand ist `04_META_REVIVE_ABSCHLUSS_2026-09-18.md`. Diese Übergabekapsel bleibt als historische Rekonstruktion des damaligen Abbruchpunkts erhalten und ist nicht mehr die aktuelle Arbeitsliste.
