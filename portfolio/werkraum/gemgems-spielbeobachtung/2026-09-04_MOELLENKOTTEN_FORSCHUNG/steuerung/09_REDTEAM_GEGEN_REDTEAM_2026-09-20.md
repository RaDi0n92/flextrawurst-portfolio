# RED-TEAM GEGEN DAS RED-TEAM — MÖLLENKOTTEN

**Stand:** 2026-09-20  
**Gegenstand:** `06_REDTEAM_GEGEN_PREMORTEM_2026-09-20.md`, das daraus abgeleitete Skalpell und der Abschlussstand.  
**Modus:** Zweiter Gegenangriff. Noch keine Reparaturausführung.

## Leitfrage

Wo war das erste Red-Team selbst zu bequem, zu optimistisch oder zu stark auf „weniger bauen“ fokussiert und hat dadurch reale Konsistenz-, Frische- oder Beweisprobleme unterschätzt?

---

## 1. „Serielle Freigaben reichen“ hat das eigentliche Atomizitätsproblem verfehlt

**Urteil: ECHTER KRITISCHER TREFFER.**

Das erste Red-Team griff die Frage an, ob zwei parallele Freigabeschreibprozesse unterstützt werden müssen. Der isolierte Paralleltest zeigte keine unmittelbare Log-Korruption, also wurde Parallelität als Reparaturthema gestrichen.

Das war zu eng gefragt.

Der wichtigere Fehler liegt **innerhalb eines einzigen Freigabeschreibvorgangs**:

1. `freigaben.jsonl` wird zuerst appendet.
2. Erst danach wird die Activation im Proposal auf `FREIGEGEBEN` gesetzt.
3. Erst danach werden Proposal-Archiv und aktueller Pointer geschrieben.

Fällt Schritt 2/3 nach erfolgreichem Log-Append aus, existiert bereits eine wirksame Freigabe, während Proposal und Archiv weiterhin `PENDING` behaupten.

### Empirisch reproduziert

Auf isolierter Kopie wurde genau dieser Crash-Zwischenzustand simuliert:

- Proposal: S01/GOAL_01 weiterhin `PENDING`
- Freigabelog: passende neue Zeile `FREIGEGEBEN`

Danach:

- Final-Audit: **0 Fehler / 0 Warnungen**
- Stale-Scan: **komplett OK**
- Leitstellenstatus leitete die Freigabe aus dem Log als wirksam ab.

Damit ist nicht nur der Schreibvorgang nicht atomar; die aktuellen Prüfer erkennen den inkonsistenten Zwischenzustand **nicht einmal nachträglich**.

### Warum der Audit ihn übersieht

Die Prüfung `Aktive Freigabe-Provenienz` kontrolliert nur:

- Proposal-ID in der Freigabereferenz vorhanden,
- Archivdatei vorhanden,
- Actor/Goal-Paar kommt irgendwo in den Activations des Proposal vor.

Sie kontrolliert **nicht**:

- dass diese Activation im Archiv `FREIGEGEBEN` ist,
- dass die dortige `freigabe_id` mit dem Log übereinstimmt.

**Gegenurteil zum ersten Red-Team:**  
„Keine Paralleltransaktionsmaschine nötig“ kann weiterhin stimmen. Aber eine einzelne Freigabe braucht entweder crash-sichere Commit-Semantik oder mindestens harte Cross-State-Invarianten plus Recovery.

---

## 2. Relevanz-Frische hat fachlich relevante Maschinenmanifeste amputiert

**Urteil: ECHTER HOHER TREFFER.**

Das erste Red-Team hatte recht, dass ein S01-Proposal nicht wegen jeder fachfremden Änderung im 100er-Körper stale werden sollte.

Beim Verschlanken verschwanden jedoch aus der beobachteten Skriptbasis:

- `00_SCRIPT_REVIEW_STATUS.json`
- `00_SCRIPT_RUN_STATUS.json`

Diese Dateien sind gerade die maschinenlesbare Wahrheit über semantische Reife und tatsächlichen Laufstatus.

### Empirisch reproduziert

Isolierter S01-Proposal:

1. Proposal erstellt → `FRESH`
2. danach im isolierten Skriptroot ein Reviewmanifest mit Eintrag für Skript 31 erzeugt
3. Recommendation-Frische erneut berechnet

Ergebnis:

- weiterhin `FRESH`
- `stale_reasons = []`

Damit kann sich ein entscheidungsrelevanter maschineller Reifezustand nach Proposal-Erstellung ändern, ohne den Proposal zu entwerten.

**Gegenurteil zum ersten Red-Team:**  
„Relevanz statt globales Zittern“ bleibt richtig. Aber Relevanz muss **Skript + Output + Reviewmanifest + Runmanifest** umfassen, nicht nur Skriptdateien und JSON/GeoJSON-Outputs.

---

## 3. PARTIAL-Proposals verlieren die bereits freigegebene Hälfte aus ihrer Frischebasis

**Urteil: ECHTER SEMANTISCHER TREFFER; Schwere hängt von gewünschter Proposal-Semantik ab.**

Die neue Frischelogik bestimmt den relevanten Skriptkörper nur aus Activations mit `state = PENDING`.

Sobald eine Activation desselben Proposals freigegeben wurde, verschwindet ihr Actor aus der beobachteten Basis für die noch offenen Activations.

### Empirisch reproduziert

Gemeinsamer Proposal:

- S01: GOAL_01
- S02: GOAL_01

Ablauf:

1. Proposal `FRESH`
2. S01 wird freigegeben
3. Proposal wird `PARTIAL`, verbleibende S02-Aktivierung `FRESH`
4. danach wird Skript 31 verändert, relevant für S01 und nicht für S02
5. Proposal-Frische erneut berechnet

Ergebnis:

- verbleibende S02-Aktivierung bleibt `FRESH`
- keine stale reason

### Warum das nicht automatisch falsch ist

Wenn jede Activation im Proposal semantisch vollständig unabhängig ist, ist dieses Verhalten vertretbar.

Aber diese Unabhängigkeit ist aktuell **nicht ausdrücklich Vertragsbestandteil**. Ein Multi-Activation-Proposal kann ebenso eine gemeinsam gedachte Staffel oder koordinierte Empfehlung darstellen.

Dann kann eine Änderung an der bereits aktivierten Hälfte die Begründung für die noch offene Hälfte sehr wohl verändern.

**Gegenurteil zum ersten Red-Team:**  
Die damalige Aussage „eigene Teilfreigabe darf die restlichen Activations nicht stale machen“ war zu pauschal. Man muss unterscheiden zwischen:

- dem bloßen Freigabe-Event selbst, das nicht stale machen soll,
- späteren fachlichen Basisänderungen an bereits aktivierten Teilen eines gemeinsamen Proposals.

---

## 4. Der „historisch eingefrorene“ Vergleichsanker ist derzeit nur konventionell eingefroren

**Urteil: ECHTER MITTLERER TREFFER.**

Das Skalpell führte `SKRIPTVERGLEICH_BASIS_<UTC>.json` ein, damit später rekonstruierbar bleibt, welchen Skript-/Outputstand eine Session beim ersten Phase-C-Blick sah.

Das Werkzeug schreibt den Snapshot korrekt.

Aber Final-Audit und Stale-Scan prüfen derzeit nur:

- dass die Anweisung `--comparison-snapshot` existiert,
- dass das Werkzeug die Funktion `build_comparison_snapshot` besitzt.

Sie prüfen **keinen tatsächlich geschriebenen Vergleichssnapshot** auf:

- Schema,
- Sessionzuordnung,
- Script-SHA-Format,
- Output-Provenienz,
- spätere Manipulation,
- Bindung an das zugehörige `ERGEBNIS_01.md`.

### Gegenprobe

Auf isolierter Kopie wurde ein erzeugter Vergleichssnapshot nachträglich verändert:

- erste gespeicherte Script-SHA auf 64 Nullen gesetzt.

Es existiert aktuell kein Audit-/Stale-Codepfad, der `SCRIPT_COMPARISON_BASIS`-Snapshotdateien semantisch validiert.

Damit bedeutet „Snapshot geschrieben“ noch nicht „historischer Vergleichsanker unverändert beweisbar“.

**Gegenurteil zum ersten Red-Team:**  
Der kleine Snapshot war die richtige Richtung. Das Red-Team war aber zu schnell zufrieden, weil Erzeugbarkeit mit Integrität verwechselt wurde.

---

## 5. Der „echte Lifecycle-Durchstich“ bewies weniger als der Abschluss behauptet

**Urteil: EPISTEMISCHER MITTLERER TREFFER.**

Der materialisierte Pilot war wertvoll und tatsächlich stärker als reine In-Memory-Fixtures:

- reale JSONL-Dateien,
- reale Snapshotdatei,
- reale Lifecycle-Kette,
- reale kanonische Stores,
- reale Inbox,
- danach Final-Audit und Stale-Scan 0/0.

Aber die Ereignisse wurden programmatisch aus bereits validen Fixture-Strukturen materialisiert und gezielt korrekt in ihre Pfade geschrieben.

Damit beweist der Pilot stark:

> Das Speicher-, Schema-, Referenz- und Auditmodell kann einen vollständigen gültigen Lifecycle tragen.

Er beweist **nicht** stark:

> Eine reale Fachsession kann die schema-reichen Events im laufenden Forschungsbetrieb ohne unnötige Fehlerbelastung selbst erzeugen.

Gerade diese praktische Authoring-Fehleranfälligkeit war die ursprüngliche Begründung für die Frage, ob ein dünner Event-Helper sinnvoll sein könnte.

**Gegenurteil zum ersten Red-Team:**  
„Kein Universal-Writer nötig“ bleibt vernünftig.  
„Der bestehende Vertrag trägt damit bereits die praktische Eventerzeugung“ war zu stark formuliert.

Der noch fehlende empirische Beweis ist ein echter Session-Agent, der nach Vertrag eine neue Quelle/Fund/Lifecycle-Kette selbst erzeugt, ohne dass ein Testskript ihm die fertigen Records vorsetzt.

---

## 6. Doppelte Relevanzlogik ist unelegant, aktuell aber konservativ

**Urteil: KEIN AKUTER BLOCKER.**

`skriptkoerper_status.py` und `leitstelle_status.py` bestimmen relevante Scripts mit zwei getrennten Implementierungen.

Direkter Mengenvergleich für S01–S12 zeigte:

- keine Session, bei der die Frischelogik derzeit ein vom Statuswerkzeug als relevant betrachtetes Skript verpasst;
- mehrere Sessions, bei denen die Frischelogik zusätzliche Skripte beobachtet.

Beispiele:

- S01: zusätzlich 86
- S02: zusätzlich 46, 66, 67, 71
- S05: zusätzlich 6, 28
- S10: zusätzlich 69, 98

Das erzeugt eher unnötige Staleness als eine Sicherheitslücke.

**Gegenurteil:**  
Nicht sofort reparaturwürdig, aber langfristig sollte nur **eine** kanonische Relevanzfunktion existieren, damit die beiden Mengen nicht später auseinanderlaufen.

---

## Red-Team-gegen-Red-Team-Gesamtergebnis

### Harte neue Treffer

1. **Freigabe-Commit ist crash-inkonsistent und Audit/Stale-Scan erkennen den Zwischenzustand nicht.**
2. **Proposal-Frische ignoriert Review-/Run-Manifeste.**

### Semantisch klärungsbedürftiger Treffer

3. **PARTIAL-Proposal beobachtet fachliche Änderungen bereits freigegebener Activations nicht mehr.**
   - korrekt bei unabhängigen Activations,
   - potenziell falsch bei gemeinsam begründeten Staffel-Proposals.

### Integritäts-/Beweisproblem

4. **Phase-C-Vergleichssnapshots werden erzeugt, aber nicht auf historische Integrität geprüft.**

### Überzogene Schlussfolgerung des ersten Red-Teams

5. **Der Lifecycle-Pilot beweist Speicherkonsistenz, nicht reale Authoring-Ergonomie eines Fachagenten.**

### Kein akuter Fehler

6. **Doppelte Relevanzlogik ist aktuell konservativ überbreit, nicht unterdeckend.**

---

## Meta-Urteil

Das erste Red-Team war an der richtigen Stelle skeptisch gegenüber Overengineering, wurde danach aber stellenweise selbst zu optimistisch:

- Es verwechselte **keine notwendige Parallelmaschine** mit **keinem Atomizitätsproblem**.
- Es verwechselte **fachbezogene Frische** mit einer bereits vollständigen relevanten Frischebasis.
- Es verwechselte **Snapshot-Erzeugung** mit **Snapshot-Integrität**.
- Es verwechselte **materialisierte gültige Events** mit **bewiesener praktischer Event-Autorierbarkeit**.

Der zweite Gegenangriff spricht damit **nicht** dafür, wieder eine Meta-Kathedrale zu bauen. Er spricht für einen noch kleineren, härteren zweiten Skalpellschritt an genau diesen vier Stellen.

## Grenze

Dieses Dokument führt keine Reparatur aus, startet keine Sachforschung, erzeugt keinen Startvorschlag und persistiert keine Goal-Freigabe.
