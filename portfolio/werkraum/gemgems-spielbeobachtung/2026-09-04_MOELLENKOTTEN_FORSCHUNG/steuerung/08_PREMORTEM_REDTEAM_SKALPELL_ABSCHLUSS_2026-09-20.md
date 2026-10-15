# PREMORTEM → RED-TEAM → SKALPELL — ABSCHLUSS 2026-09-20

## Grundlage

Dieser Abschluss folgt auf:

- `05_PREMORTEM_BETRIEBSSTART_2026-09-20.md`
- `06_REDTEAM_GEGEN_PREMORTEM_2026-09-20.md`
- `07_SKALPELL_NACH_PREMORTEM_REDTEAM_2026-09-20.md`

Während dieses Zyklus wurde **keine Sachforschung gestartet**, **kein echter Startvorschlag erzeugt** und **keine Goal-Freigabe persistiert**. Alle Betriebsversuche liefen auf isolierten Kopien.

## 1. Startvorschlag-Lifecycle repariert

`../werkzeuge/startvorschlag.py` hält aktuellen Pointer und Archiv nun gemeinsam aktuell.

Bestätigt im isolierten Test:

- Proposal A wird beim Erzeugen von Proposal B automatisch `CLOSED`.
- Archiv A trägt denselben geschlossenen Zustand.
- Proposal B und sein Archiv sind im Zustand `OPEN` byteinhaltlich deckungsgleich.
- `--close --dry-run` verändert den Pointer nicht.
- Ein echtes `--close` schreibt `CLOSED`, `closed_at` und Grund sowohl in Pointer als auch Archiv.
- `../werkzeuge/freigabe_schreiben.py` schreibt `PARTIAL/CONSUMED` ebenfalls in beide Zustände.

`../werkzeuge/stale_scan.py` prüft jetzt zusätzlich:
- Deckungsgleichheit von aktuellem Proposal und Archiv,
- dass genau der aktuelle offene Proposal als `OPEN/PARTIAL` im Archiv existiert,
- dass keine alten Zombie-Proposals offen bleiben.

## 2. Proposal-Frische auf relevante Basis verengt

Die Frischelogik in `../werkzeuge/leitstelle_status.py` beobachtet weiterhin globale Maschinen-/Forschungsverträge, aber beim externen Skriptkörper nur den für noch offene Aktivierungen relevanten Ausschnitt.

Isolierter Test mit S01:

- Ausgang: `FRESH`
- Änderung an fachfremdem Skript 50: weiterhin `FRESH`
- Änderung an relevantem Skript 31: `STALE`

Für Gravity/Red-Team bleibt der größere bzw. vollständige Skriptkörper relevant.

Der Final-Audit enthält dafür einen Relevanztest: S01 muss den 31er-Bereich sehen, Skript 50 nicht; Gravity muss Skript 50 sehen.

## 3. H151-Bildquelle und Bildbeobachtung getrennt

Skripte 06/07 behandeln ein autorisiertes Daniel-Bild nicht selbst als Raumbehauptung.

Der zulässige Pfad lautet jetzt:

**autorisierte DANIEL-Bildquelle → EIGENE_BEOBACHTUNG → `abgeleitet_von_source_ids` auf die autorisierte Originalquelle → H151-Text-/Strukturevidenz**

Isolierter Test:

- Rohbild `.jpg` mit korrektem Daniel-Quelltyp: wird nicht als Text-/Raumevidenz gelesen.
- strukturierte Beobachtung mit Abstammung zum autorisierten Bild: wird akzeptiert.
- identischer Beobachtungstext ohne autorisierte Abstammung: wird blockiert.

Damit bleibt die private Innenraumgrenze hart, ohne echte Bildquellen wirkungslos zu machen.

## 4. Vollständiger Ereignis-Lifecycle materialisiert getestet

Das Premortem vermutete, dass vor echtem Betrieb eventuell noch ein allgemeiner Event-Writer nötig sei. Das Red-Team verlangte zuerst einen realen Durchstich statt präventiver Architektur.

Auf einer isolierten vollständigen Forschungswurzel wurden echte Dateien materialisiert:

1. lokales `source_event: ANLEGEN`,
2. echter Snapshot + SHA,
3. append-only `INHALT_KORRIGIEREN`,
4. `MERGE_STATUS_AENDERN → ZUR_PRUEFUNG`,
5. darauf beruhender lokaler Fund,
6. Fund auf `ZUR_PRUEFUNG`,
7. kanonischer Gravity-Quellenmerge,
8. kanonischer Gravity-Fundmerge,
9. Weg-/Objekt-/Grenzereignisse,
10. echte Inbox-Nachricht im Empfängerordner.

Ergebnis des vollständigen Audits auf diesem materialisierten Pilot:

- **168 Dateien**
- **0 Fehler**
- **0 Warnungen**
- vollständiger Stale-Scan ebenfalls grün.

Daraus folgt bewusst: **kein Universal-Writer wird jetzt gebaut**. Der bestehende Vertrag trägt den realen materialisierten Lifecycle. Ein Writer wird erst dann sinnvoll, wenn echte Forschung später praktische Schreibfehler zeigt.

## 5. Kleiner Phase-C-Vergleichsanker

`../werkzeuge/skriptkoerper_status.py` besitzt nun:

`--comparison-snapshot`

Zusammen mit `--session S01..S12` schreibt der Scanner einen kleinen:

`SKRIPTVERGLEICH_BASIS_<UTC>.json`

in den jeweiligen Session-`snapshots/`-Ordner.

Enthalten sind nur:
- relevante Skripte,
- Skript-SHA256,
- Outputstände und Output-Provenienz,
- semantischer Reviewstatus,
- Executionstatus,
- Zeitpunkt und Session.

Die Skriptdateien selbst werden nicht kopiert.

Isolierter S01-Test:
- Snapshot wurde real geschrieben,
- enthielt 25 für S01 relevante Skripte,
- jeder Eintrag trug SHA, Outputliste, Review- und Executionstatus.

Die kanonische Goal-01-Vorlage, ihre zwölf Sessionkopien, die Sessionkerne und `../gemeinsam/11_SKRIPTKOERPER_ZUSAMMENARBEIT.md` verlangen diesen Anker jetzt beim ersten Phase-C-Blick.

## 6. Bewusst nicht gebaut

Nach dem Red-Team wurden folgende Premortem-Ideen **nicht** zu neuen Systemschichten:

- kein Parallel-Freigabe-Framework,
- kein automatischer Gravity-Queue-Apparat,
- kein Universal-Event-Writer,
- kein Vollsnapshot aller 100 Skripte pro Session,
- kein OCR-/Vision-Zwang für H151,
- kein künstliches Beseitigen ehrlicher `UNKNOWN`-Zustände.

## 7. Verbleibende Beobachtungspunkte

Nur noch beobachten:

- ob Gravity im echten Mehrsession-Betrieb tatsächlich Rückstau erzeugt,
- ob praktische Eventerzeugung trotz bestandenem Materialisierungstest später einen dünnen Helper rechtfertigt,
- ob wiederholte Phase-C-Zyklen zusätzlichen Vergleichsnutzen liefern.

Das sind keine aktuellen Blocker.

## 8. Grenze

Dieser Abschluss ist ein Meta-/Betriebsabschluss. Er autorisiert keine Sachforschung.

Der nächste echte Forschungsstart bleibt weiterhin an einen konkret persistenten Startvorschlag und Daniels ausdrückliche Freigabe genau dieses Vorschlags gebunden.
