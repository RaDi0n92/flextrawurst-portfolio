# PREMORTEM BETRIEBSSTART — MÖLLENKOTTEN

**Stand:** 2026-09-20  
**Modus:** Premortem vor echtem Forschungsstart  
**Wichtig:** Dieses Dokument startet keine Forschung, erzeugt keinen Startvorschlag und persistiert keine Goal-Freigabe.

## Ausgangsfrage

Angenommen, der gerade technisch saubere Möllenkotten-Forschungsbetrieb scheitert im ersten echten Betrieb trotz grünem Audit. Welche Ursachen sind am wahrscheinlichsten?

Die folgenden Punkte sind absichtlich als mögliche Scheiterpfade formuliert. Sie sind noch **nicht** das spätere Red-Team gegen dieses Premortem und noch **keine** Revive-Liste.

## 1. Frische-Sicherheitsgurt wird zum Start-Livelock

### Scheiterbild
Ein Startvorschlag wird korrekt erzeugt und Daniel will ihn kurz danach freigeben. Währenddessen ändert die parallel arbeitende Skriptkörper-Session irgendein beobachtetes Skript oder einen beobachteten Output. Der Vorschlag wird dadurch `STALE` und technisch abgelehnt. Bei fortlaufenden Skriptänderungen kann sich dieser Zyklus wiederholen.

### Warum das realistisch ist
Die Recommendation-Frische beobachtet bewusst die live operative Basis einschließlich des externen 100er-Skriptkörpers. Während der Reparaturrunde änderten sich nacheinander unter anderem Skripte 40–50 im Abstand von Sekunden bis Minuten; mehrere Auditläufe wurden dadurch korrekt stale.

### Frühes Warnsignal
Mehrere neu erzeugte Proposals hintereinander werden ohne fachliche Änderung am vorgeschlagenen Start allein durch externe Skriptänderungen stale.

### Möglicher Schaden
Der Schutz gegen veraltete Starts funktioniert so streng, dass der eigentliche Forschungsbetrieb bei dauerhaftem Skriptumbau praktisch nicht freigegeben werden kann.

---

## 2. H151-Fotoquellen sind formal erlaubt, technisch aber derzeit nicht konsumierbar

### Scheiterbild
Daniel liefert ein echtes Foto oder Bild zu Hauptstraße 151 und die Quelle wird korrekt als `DANIEL_FOTO_ODER_BILD` registriert. Skript 06/07 ignorieren den Snapshot trotzdem.

### Warum das realistisch ist
Der neue Autorisierungsweg ist streng und richtig an `source_event`, Quelltyp, Snapshot-Pfad und SHA gebunden. Die beiden H151-Skripte akzeptieren beim Lesen des Snapshots derzeit jedoch nur Text-/JSON-Endungen wie `.md`, `.txt`, `.json` und `.jsonl`. Reale `.jpg`, `.jpeg`, `.png` oder ähnliche Bilddateien fallen damit heraus.

### Frühes Warnsignal
Eine registrierte Daniel-Fotoquelle ist im lokalen Quellenlog sichtbar und der Snapshot-Hash stimmt, aber `source_candidates` von Skript 06/07 bleibt leer.

### Möglicher Schaden
Ausgerechnet die ausdrücklich vorgesehenen privaten Bildquellen erreichen die H151-Innenraumlogik nicht.

---

## 3. Der erste echte Ereignis-Lifecycle ist noch unbewiesen

### Scheiterbild
Eine Fachsession sammelt die erste reale Quelle und soll sie als `source_event`, Fund oder Weg append-only registrieren. Dabei entstehen falsche IDs, fehlerhafte Lifecycle-Ketten, ungültige Snapshotpfade, falsche Hashes oder ein Schemafehler. Der Fehler wird erst später beim Audit oder Merge entdeckt.

### Warum das realistisch ist
Alle 36 lokalen Session-JSONL für Funde/Quellen/Wege sowie die kanonischen Forschungs-JSONL sind aktuell leer. Nur das Freigabelog enthält bereits Ereignisse. Der Final-Audit selbst bezeichnet den echten Lauf Quelle → Snapshot → Korrektur → `ZUR_PRUEFUNG` → Gravity-Merge → Inbox weiterhin als nächsten empirischen Beweis.

Zusätzlich existiert derzeit kein allgemeines Writer-Werkzeug für Fund-, Quellen- oder Wegereignisse. Die Sessionverträge beschreiben, was geschrieben werden soll; die eigentliche Erzeugung der schema-reichen JSONL-Ereignisse ist noch nicht durch einen gemeinsamen Writer abgesichert.

### Frühes Warnsignal
Die erste aktive Session verbringt mehr Zeit mit manueller JSON-/ID-/Snapshotmechanik als mit Forschung oder produziert erst nachträglich auditierbare Korrekturen für ihr allererstes Ereignis.

### Möglicher Schaden
Der theoretisch stark geprüfte Vertrag scheitert am ersten realen Schreibzyklus oder erzeugt unnötige Reparaturarbeit.

---

## 4. Skriptvergleich kann aus mehreren Zeitständen zusammengesetzt werden

### Scheiterbild
Eine Session friert ihren Eigenstand korrekt ein und beginnt danach den Skriptvergleich. Während dieses Vergleichs verändert sich der externe Skriptkörper. Ein früher gelesenes Skript stammt dann aus Revision A, ein später gelesenes aus Revision B. Das Ergebnis wirkt wie ein einziger Vergleichsstand, obwohl es ein Mischzustand ist.

### Warum das realistisch ist
Die Verträge verlangen Skriptnummer, Skript-SHA256, Outputstand und semantische Grenzen bei der Übergabe. Es existiert aber kein eigener eingefrorener Vergleichssnapshot des gesamten für die Session verwendeten Skript-/Outputstands. Gleichzeitig wird der externe Körper real parallel weiter verändert.

### Frühes Warnsignal
Innerhalb eines einzigen `ERGEBNIS_01.md` beziehen sich Vergleichsaussagen auf Skripte/Outputs, deren aktuelle Hashes bereits während derselben Session wechseln, ohne dass der Wechsel als eigener Vergleichszeitpunkt sichtbar ist.

### Möglicher Schaden
Spätere Rekonstruktion kann zwar einzelne Hashes kennen, aber nicht eindeutig beantworten, welcher gemeinsame Skriptzustand der damaligen Vergleichsentscheidung zugrunde lag. Widersprüche können aus Versionsdrift statt aus der Sache entstehen.

---

## 5. Gravity wird zum einzigen Merge-Flaschenhals

### Scheiterbild
Mehrere Fachsessions arbeiten parallel und erzeugen prüfreife `ZUR_PRUEFUNG`-Ereignisse. Gravity ist alleiniger fachlicher Writer der kanonischen Beweis-, Quellen-, Wege-, Objekt- und Grenzzustände. Gleichzeitig soll Gravity nach jedem Aufsichts-/Prüfzyklus anhalten und auf die nächste Steuerungsentscheidung warten.

### Warum das realistisch ist
Diese Serialisierung ist absichtlich als Schutz eingebaut. Es gibt aber noch keinen echten Mehrsession-Betrieb, der gezeigt hat, wie schnell Gravity einen wachsenden Prüfblock abarbeitet und ob dabei eine nachvollziehbare Warteschlange entsteht.

### Frühes Warnsignal
Lokale Sessions melden bereits neue geprüfte Kandidaten, während ältere `ZUR_PRUEFUNG`-Ereignisse noch ungemerged liegen und die Leitstelle wiederholt Gravity-Zyklen einzeln freigeben muss.

### Möglicher Schaden
Die Fachforschung läuft schneller als der einzige kanonische Mergepfad. Der lokale Bestand wächst, der gemeinsame Zustand hinkt hinterher und spätere Sessions arbeiten auf einer unnötig alten kanonischen Sicht.

---

## 6. Parallele Freigaben sind faktisch seriell und können einen Batch nur teilweise aktivieren

### Scheiterbild
Ein Proposal enthält mehrere Aktivierungen und zwei Freigabeschreibvorgänge laufen nahezu gleichzeitig. Eine Freigabe gewinnt; die zweite sieht anschließend eine geänderte operative Basis und wird als stale abgelehnt. Das Proposal bleibt `PARTIAL`.

### Empirischer Test
Auf einer isolierten Kopie wurde ein Proposal mit
- `S01:GOAL_01_START_UND_QUELLEN`
- `S01:GOAL_02_FACHKARTIERUNG`

erzeugt und beide Freigaben gleichzeitig gestartet.

Ergebnis:
- keine doppelten Freigabe-IDs,
- keine Log-Korruption,
- genau eine Freigabe wurde persistiert,
- die andere wurde mit `STARTVORSCHLAG STALE` abgelehnt,
- Proposal blieb `PARTIAL`.

### Frühes Warnsignal
Ein ausdrücklich als gemeinsame Staffel gedachter Start aktiviert nur einen Teil, obwohl mehrere Steuerungsprozesse denselben Proposal fast gleichzeitig bearbeiten.

### Möglicher Schaden
Kein Datenverlust, aber ein nicht offensichtlich gewünschter Teilstart. Der Betrieb ist damit praktisch seriell und sollte nicht so behandelt werden, als wären Freigabeschreibvorgänge parallel atomar.

---

## 7. Skriptstatus bleibt lange UNKNOWN und erzeugt operative Unklarheit

### Scheiterbild
Die Fachsession erreicht Phase C und soll eigene Erkenntnisse gegen den Skriptkörper halten. Fast alle Skripte haben noch keinen Output; vorhandene Outputs sind veraltet; semantischer Review- und Run-Status sind für alle 100 unbekannt. Die Session muss deshalb viele Skriptbezüge als ungeklärt behandeln.

### Aktueller Zustand beim Premortem
- 100 Skripte
- 98 `NOCH_OHNE_OUTPUT`
- 2 `OUTPUT_VERALTET`
- 100 × semantischer Reviewstatus `UNKNOWN`
- 100 × Executionstatus `UNKNOWN`

### Frühes Warnsignal
Phase C produziert überwiegend `SKRIPTSTATUS_UNGEKLAERT_KEIN_OUTPUT` statt echten Vergleichsgewinn.

### Möglicher Schaden
Explore-first funktioniert, aber der versprochene Gegentest mit dem Skriptkörper liefert zunächst wenig Mehrwert und kann fachliche Sessions unnötig auf spätere Wiederholungsvergleiche verteilen.

---

## Vorläufige Premortem-Reihenfolge

Für einen ersten echten Betriebsstart wirken derzeit besonders kritisch:

1. **Erster realer Ereignis-Lifecycle noch unbewiesen**
2. **H151-Fotointake technisch unvollständig**
3. **Frische-Livelock bei parallel wanderndem Skriptkörper**
4. **Mischzeitstände beim Skriptvergleich**
5. **Gravity als möglicher Merge-Flaschenhals**
6. **Teilstart bei parallelen Freigabeschreibvorgängen**
7. **geringer Vergleichsnutzen solange Review/Run/Outputs überwiegend UNKNOWN sind**

Diese Reihenfolge ist ausdrücklich **Premortem-Hypothese**, kein endgültiges Urteil.

## Grenze dieses Schritts

Es wurden für dieses Premortem keine Forschungs-Goals freigegeben, keine Session gestartet und keine Sachforschung durchgeführt.

Es wurden außerdem bewusst noch keine Revive-Patches aus diesen Befunden abgeleitet. Der vorgesehene nächste Meta-Schritt ist ein **Red-Team gegen dieses Premortem selbst**: Welche Punkte sind übertrieben, falsch gerahmt, bereits ausreichend abgefangen, doppelt oder fehlen noch?
