# RED-TEAM GEGEN DAS PREMORTEM — MÖLLENKOTTEN

**Stand:** 2026-09-20  
**Gegenstand:** `05_PREMORTEM_BETRIEBSSTART_2026-09-20.md`  
**Modus:** Angriff auf das eigene Premortem, noch keine Reparaturausführung.

## Leitfrage

Welche Premortem-Punkte sind wirklich Betriebsrisiken, welche sind bereits ausreichend abgefangen, welche sind nur Beobachtungsbedingungen und was hat das Premortem selbst übersehen?

## Urteil pro Premortem-Punkt

### 1. Frische-Sicherheitsgurt wird zum Start-Livelock

**Urteil: ÜBERLEBT, aber enger formulieren.**

Der Befund ist real. Die aktuelle Frischebasis beobachtet den gesamten externen 100er-Skriptkörper. Während der Meta-Arbeit veränderten sich Skripte im Abstand von Sekunden bis Minuten; dadurch wurden Vorschläge und Audits korrekt stale.

Der Premortem-Fehler liegt in der impliziten Annahme, jede Skriptänderung sei für jeden Startvorschlag gleich relevant. Das ist zu grob. Wenn etwa ein S01-Start vorgeschlagen wird, muss eine Änderung an einem fachfremden S10-Skript nicht zwingend die Startentscheidung entwerten.

**Red-Team-Fazit:** Nicht Frische abschalten. Stattdessen die Frischebasis auf die für den konkreten Proposal relevanten Actor-/Goal-Verträge und Skriptbereiche verengen.

---

### 2. H151-Fotoquellen sind technisch nicht konsumierbar

**Urteil: ÜBERLEBT, aber das Premortem hat das Problem falsch benannt.**

Der 100er-Skriptkörper kann Rasterbilder grundsätzlich katalogisieren; unter anderem behandeln Skripte 66, 67, 74 und 75 `.jpg/.jpeg/.png/.webp/.tif/.tiff` als Bildkandidaten.

Das H151-Problem ist enger: Skript 06/07 akzeptieren für ihren privaten Innenraum-Evidenzpfad nur textuell lesbare Snapshots. Ein Originalfoto darf aus Sicherheitsgründen ohnehin nicht dadurch zu Raumwissen werden, dass Binärbytes bloß als Quelle registriert sind.

**Eigentlich fehlend ist die Ableitungsbrücke:**

autorisierte Originalbildquelle  
→ prüfbare Bildbeobachtung / strukturierte Beschreibung  
→ explizite Ableitungsbeziehung zur Originalquelle  
→ erst dann H151-Innenraumkandidat.

Das Datenmodell besitzt mit `abgeleitet_von_source_ids` bereits die passende Provenienzachse.

**Red-Team-Fazit:** Kein Bildparser in 06/07 hineinquetschen. Eine kleine, explizite Bild→Beobachtung-Brücke reicht.

---

### 3. Erster echter Ereignis-Lifecycle unbewiesen

**Urteil: ÜBERLEBT STARK.**

Das Premortem trifft hier den wichtigsten empirischen Blindfleck. Die lokalen Forschungs-JSONL und kanonischen Forschungs-JSONL sind weiterhin leer. Fixtures und adversariale Tests beweisen den Vertrag, aber noch nicht, dass eine echte Session mit echter Quelle den vollständigen Weg fehlerarm bedienen kann.

Das Premortem ging allerdings zu schnell in Richtung „gemeinsamer Writer fehlt“. Ein neuer Universal-Writer wäre bereits eine Architekturentscheidung, bevor der echte Fehler überhaupt beobachtet wurde.

**Red-Team-Fazit:** Erst ein vollständiger isolierter Betriebsdurchstich mit realistischem Eventkörper. Nur wenn dabei die manuelle Eventmechanik tatsächlich scheitert oder unnötig fehleranfällig ist, entsteht daraus ein dünner Writer als Folgemaßnahme.

---

### 4. Skriptvergleich aus mehreren Zeitständen

**Urteil: TEILWEISE ÜBERLEBT, Priorität herunter.**

Die Verträge verlangen bei skriptgestützten Funden spätestens bei der Übergabe Skriptnummer, Skript-SHA256, Outputstand und semantische Grenzen. Damit ist Versionsdrift nicht unsichtbar.

Was fehlt, ist kein vollständiger Freeze des 100er-Körpers, sondern ein klarer Startpunkt für Phase C: Welcher relevante Skriptstatus wurde beim Beginn des Vergleichs gesehen?

**Red-Team-Fazit:** Kein Kopieren oder Einfrieren aller Skripte. Ein kleiner sessionbezogener Vergleichsstatus-Snapshot bei Phase-C-Beginn genügt.

---

### 5. Gravity als Merge-Flaschenhals

**Urteil: BEOBACHTEN, NICHT VORAB REPARIEREN.**

Gravity als alleiniger kanonischer Writer ist absichtlich serialisiert. Noch existiert kein echter Mehrsession-Durchsatz, der einen Rückstau belegt. Das Premortem beschreibt einen plausiblen Skalierungseffekt, aber noch keinen gegenwärtigen Fehler.

Eine Queue, automatische Merge-Pipeline oder zusätzliche Writer jetzt einzubauen wäre genau die Art präventive Bürokratie, gegen die der Meta-Revive bereits gearbeitet hat.

**Red-Team-Fazit:** Nur ein Warnsignal definieren: Wenn `ZUR_PRUEFUNG` dauerhaft schneller anwächst als Gravity abarbeitet, erneut bewerten. Bis dahin nichts bauen.

---

### 6. Parallele Freigaben erzeugen Teilstart

**Urteil: ALS REPARATURTHEMA STREICHEN.**

Der isolierte Test zeigte:
- keine doppelten IDs,
- keine Log-Korruption,
- eine Aktivierung gewinnt,
- die konkurrierende wird stale,
- Proposal bleibt nachvollziehbar `PARTIAL`.

Das Steuerungsmodell besitzt ohnehin genau einen fachlichen Writer für Freigaben. Parallele Freigabeschreibprozesse sind kein erforderlicher Normalbetrieb.

**Red-Team-Fazit:** Serielles Persistieren ist zulässige Betriebssemantik. Kein Paralleltransaktionsapparat nötig.

---

### 7. Skriptstatus bleibt UNKNOWN

**Urteil: ALS FEHLER STREICHEN.**

`UNKNOWN` ist hier bewusst ehrliche Information:
- fehlender Output wird nicht als laufender Prozess erfunden,
- fehlendes Reviewmanifest wird nicht als Reife umgedeutet,
- fehlendes Run-Manifest bleibt unbekannt.

Dass Phase C zu Beginn wenig Skriptvergleich liefern kann, ist eine Eigenschaft des aktuellen Materialstands und kein Defekt des Forschungsbetriebs.

**Red-Team-Fazit:** Nicht reparieren. Erst wenn wiederholte Sessions nachweislich an demselben fehlenden Vergleichsmaterial hängen, wird daraus ein Planungsproblem.

---

## Was das Premortem selbst übersehen hat

### A. Startvorschlag-Lifecycle und Archiv widersprechen dem Vertrag

**Urteil: NEUER ECHTER TREFFER.**

Der Vertrag in `01_LEITSTELLENLOGIK.md` sagt:

> Wenn sich der Vorschlag fachlich ändert, wird der alte geschlossen und ein neuer erzeugt.

Der aktuelle `../werkzeuge/startvorschlag.py` erzeugt jedoch einen neuen Proposal, ohne einen vorhandenen `OPEN`- oder `PARTIAL`-Proposal zuerst zu schließen.

Zusätzlich wird das Archiv unter `../zustand/startvorschlaege/<proposal_id>.json` nur beim Erzeugen geschrieben. Spätere Zustände wie `PARTIAL`, `CONSUMED` oder `CLOSED` werden nur im aktuellen Pointer `../zustand/startvorschlag.json` fortgeschrieben.

### Empirischer isolierter Test

1. Proposal A erzeugt.
2. Proposal B erzeugt, ohne A zu schließen.
3. Archiv A blieb `OPEN`.
4. Archiv B blieb `OPEN`.
5. Aktueller Pointer zeigte B.
6. B wurde anschließend korrekt geschlossen.
7. Aktueller Pointer wurde `CLOSED`.
8. Archiv B blieb trotzdem `OPEN` mit `closed_at = null`.

Damit können historische Archivdateien dauerhaft einen operativ falschen Zustand behaupten.

Der aktuelle Stale-Scan prüft nur, **ob** eine Archivdatei für den aktuellen Proposal existiert, nicht ob ihr Lifecycle mit dem aktuellen Proposal übereinstimmt.

**Red-Team-Fazit:** Dieser Punkt gehört vor Betriebsstart tatsächlich ins Skalpell.

---

## Red-Team-Gesamtergebnis

### Als echte Reparaturthemen übrig
1. Proposal-Frische ist zu global und muss auf relevante Entscheidungsbasis verengt werden.
2. H151 braucht eine saubere Originalbild→abgeleitete Beobachtung-Brücke.
3. Startvorschlag-Lifecycle/Archiv muss wahrheitsgetreu werden.

### Vor Betriebsstart empirisch testen, aber nicht sofort architektonisch aufblasen
4. vollständiger echter Event-Lifecycle-Durchstich.
5. sessionbezogener Skriptvergleichs-Snapshot als kleiner Reproduzierbarkeitsanker.

### Nur beobachten
6. Gravity-Durchsatz / möglicher Merge-Rückstau.

### Aus der Reparaturliste gestrichen
7. parallele Freigabeschreibvorgänge.
8. UNKNOWN-Review-/Run-/Outputlage als solche.

## Meta-Urteil

Das Premortem war nützlich, aber an zwei Stellen zu schutzfreudig: Es machte eine absichtliche Serialisierung und ehrliche Unwissenheit zu vermeintlichen Fehlern. Gleichzeitig übersah es den realen Proposal-Archiv-Widerspruch.

Genau deshalb folgt jetzt kein „alles absichern“, sondern ein Skalpell.
