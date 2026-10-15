# SKALPELL NACH PREMORTEM + RED-TEAM — MÖLLENKOTTEN

**Stand:** 2026-09-20  
**Grundlage:** `05_PREMORTEM_BETRIEBSSTART_2026-09-20.md` + `06_REDTEAM_GEGEN_PREMORTEM_2026-09-20.md`

## Ziel

Nur das reparieren, was nach Premortem **und** Gegenangriff noch Substanz hat. Keine neue Meta-Schicht, kein Daemon, keine Queue-Orgie, kein Universalframework.

## Schnitt 1 — Startvorschlag-Lifecycle wahr machen

### Minimaländerung
- Beim Erzeugen eines neuen Proposals wird ein vorhandener `OPEN`- oder `PARTIAL`-Proposal zuerst explizit `CLOSED`.
- Jede Lifecycle-Änderung des aktuellen Proposals schreibt denselben Zustand auch in seine Archivdatei:
  - `PARTIAL`
  - `CONSUMED`
  - `CLOSED`
- Der Stale-Scan prüft nicht nur Archivexistenz, sondern bei aktuellem Proposal auch die Deckungsgleichheit seines Archivstands.
- Zusätzlich prüft der Audit, dass keine ältere Archivdatei als `OPEN/PARTIAL` stehen bleibt, nachdem ein neuer Proposal aktiv wurde.

### Nicht bauen
Keine separate Proposal-Datenbank und kein Event-Sourcing-System für Proposals.

---

## Schnitt 2 — Proposal-Frische auf Relevanz statt globales Zittern

### Minimaländerung
Die Frische bleibt hart, beobachtet aber bei offenem Proposal nur:
- globale Verträge/Werkzeuge, die die vorgeschlagenen Actor/Goals tatsächlich steuern;
- die betroffenen Session-/Goal-Dateien;
- für Fachsessions nur die laut `../maschinenvertrag/SKRIPT_SESSION_MAPPING.json` relevanten Skripte/Outputs;
- bei Gravity/Red-Team den größeren bzw. vollständigen Skriptbereich, wenn deren Auftrag ihn wirklich umfasst;
- fremde Freigaben seit Proposal-Erstellung.

Eine Änderung an einem fachfremden Skript darf einen Proposal nicht mehr allein deshalb stale machen.

### Nicht bauen
Kein neuer allgemeiner Hashkatalog für den ganzen Forschungsroot und kein Ablauf-Timer.

---

## Schnitt 3 — H151-Bildquelle nicht mit Bildbeobachtung verwechseln

### Minimaländerung
- Ein registrierter Originalsnapshot darf ein echtes Bildformat sein.
- Das Originalbild selbst erzeugt keine Raumbehauptung.
- Für 06/07 wird eine kleine abgeleitete, textuell/strukturiert prüfbare Beobachtung zugelassen.
- Diese Beobachtung muss über `abgeleitet_von_source_ids` eindeutig auf die autorisierte `DANIEL_FOTO_ODER_BILD`-Originalquelle zeigen.
- 06/07 konsumieren weiterhin nur prüfbare strukturierte/textuelle Evidenz, nicht rohe Bildbytes.
- Audit/Negativtest: Ein beliebiger Text ohne autorisierte Bild-Abstammung darf den privaten Innenraumkanal nicht öffnen.

### Nicht bauen
Kein OCR-Zwang, keine automatische Bilderkennungspflicht und kein allgemeines Medienframework.

---

## Schnitt 4 — Ein einziger echter Lifecycle-Durchstich vor Sachbetrieb

### Minimaltest auf isolierter Kopie
Ein realistischer vollständiger Pfad:

1. lokale echte/realistische Quelle als `source_event` anlegen,
2. Snapshot + SHA,
3. einen darauf beruhenden Fund anlegen,
4. eine append-only Korrektur erzeugen,
5. Fund/Quelle auf `ZUR_PRUEFUNG` setzen,
6. Gravity-Merge in kanonischen Bestand,
7. Ablehnung oder Rückfrage per Inbox einmal mitprüfen,
8. Final-Audit + Stale-Scan.

Wenn dieser Durchstich mit den bestehenden Mechanismen sauber funktioniert, **kein neuer Writer**.

Nur wenn die Eventerzeugung dabei praktisch unnötig fehleranfällig ist, folgt anschließend ein dünner validierender Append-Helper.

---

## Schnitt 5 — Kleiner Vergleichsanker statt Skriptkörper einfrieren

Beim ersten Phase-C-Skriptblick einer Session wird ein kleiner sessionbezogener Statussnapshot abgelegt:
- Zeitpunkt,
- relevante Skriptnummern,
- deren SHA256,
- vorhandene Outputstände/Hashes,
- semantischer Review-/Run-Status.

Die Skripte selbst werden nicht kopiert. Spätere Änderungen sind erlaubt und können als späterer Vergleichsstand dokumentiert werden.

### Nicht bauen
Kein Vollsnapshot aller 100 Skripte pro Session und kein Versionsarchiv-Duplikat des externen Körpers.

---

## Nur beobachten, nicht reparieren

### Gravity
Erst eingreifen, wenn ein realer Rückstau sichtbar wird: ältere `ZUR_PRUEFUNG`-Ereignisse bleiben liegen, während neue dauerhaft schneller hinzukommen.

### UNKNOWN-Skriptstatus
Bleibt ehrliche Zustandsinformation.

### Parallele Freigaben
Freigaben werden operativ seriell persistiert. Kein Parallelitätsframework.

## Reihenfolge

1. Proposal-Lifecycle/Archiv
2. relevante Frischebasis
3. H151 Bild→Beobachtung-Brücke
4. isolierter echter Lifecycle-Durchstich
5. kleiner Phase-C-Vergleichsanker
6. danach vollständiger Stale-Scan + Final-Audit

Erst nach diesen Schnitten wird erneut beurteilt, ob überhaupt noch ein zusätzlicher Revive-Schritt nötig ist.

## Harte Grenze

Dieses Skalpell ist ein Reparaturplan, **keine Forschungsfreigabe**. Es startet keine Fachsession, kein Gravity und kein Red-Team des Sachbetriebs.
