---
datum: 2026-08-12
typ: lebender-fahrplan
status: entwurf-v1
betrifft: [browserrecorder, playwright, ui-visible-conversations, export, audit, redteam, workflow]
autor: codex bei Daniels VPS
---

# Browserrecorder — lebender Fahrplan bis zum Ziel

## Zielbild

Wir wollen nicht nur fünf vorhandene Ordner mit vielen Dateien haben. Wir wollen für jeden Chat eine belastbare, wiederholbare und später erneut prüfbare Kette:

```text
offener Chat
  ↓ echte Desktop-Aktivierung
sichtbare Bereiche vollständig und überlappend erfasst
  ↓ unabhängiger semantischer Abgleich
VPS-Nachrichtenbestand bewiesen
  ↓ atomare Versiegelung
Exportbytes auf VPS gespeichert
  ↓ exakter Download derselben Bytes
Download persistent abgelegt und erneut geprüft
  ↓ Abschlussbericht
Chatstatus = complete
```

Das Ziel ist erreicht, wenn alle fünf Chats entweder `complete` sind oder ehrlich als `partial`/`blocked` dokumentiert wurden. Ein unbewiesener Chat darf niemals durch einen schönen Dateinamen als vollständig erscheinen.

## Zwei getrennte Arbeitslinien

### Linie A — die fünf vorhandenen Chats retten oder ehrlich versiegeln

Diese Linie untersucht den historischen Lauf vom 03.08. Wenn die offenen Chats noch dieselben Inhalte zeigen, können fehlende Bereiche durch einen neuen, klar getrennten Recovery-Run nacherfasst werden. Fehlende historische Daten werden nicht erfunden und nicht still mit dem neuen Lauf vermischt.

Ergebnis pro Chat:

- `recovered-complete`
- `historical-partial`
- `blocked-no-source`
- `ambiguous-needs-review`

### Linie B — den Recorder und den Prüfworkflow dauerhaft härten

Diese Linie baut die unabhängigen Gates, Manifeste, Hashketten, Downloadprüfungen und Regressionstests. Sie sorgt dafür, dass ein neuer Lauf nicht wieder nur Dateien erzeugt, sondern seinen eigenen Beweis mitliefert.

Die Linien dürfen sich gegenseitig informieren, aber ihre Runs, Dateien und Statuswerte bleiben getrennt.

## Arbeitsregeln für den gesamten Fahrplan

1. Normale Lese-, Schreib-, Test- und Playwright-Schritte laufen innerhalb der erteilten operativen Freigabe ohne Kleinstfragen.
2. Chataktionen erfolgen nur über den realen virtuellen Desktop: echte Tab-Aktivierung, echter Klick, echtes Mausrad, echte Tastatur.
3. DOM-Auswertung ist Lesen; `evaluate` darf keine Klicks oder Scrollbewegungen vortäuschen.
4. Jeder Chat bekommt eine eigene Conversation-ID, einen eigenen `run_id` und eine eigene `tab_instance_id`.
5. Jede Lücke bleibt sichtbar und blockiert `complete`.
6. Alte Dateien werden nicht überschrieben, wenn dadurch Provenienz verloren ginge.
7. Jede Etappe hat ein eigenes Prüfartefakt und ein klares Abnahmekriterium.
8. Nach jeder Etappe wird der Fahrplan selbst auf neue Erkenntnisse geprüft und bei Bedarf versioniert ergänzt.
9. Laufende Services werden nicht ohne ausdrücklichen Auftrag neu gestartet.
10. Am Ende eines wichtigen Arbeitsblocks werden Status, offene Punkte und nächste Etappe als Notiz persistiert.

## Phasenübersicht

| Phase | Name | Hauptziel | Ausgang nur bei |
|---|---|---|---|
| P0 | Fahrplan und Beweisvertrag | Ziel, Zustände und Grenzen festschreiben | Vertrag geprüft |
| P1 | Bestand einfrieren | Historische Daten und offene Tabs eindeutig inventarisieren | Bestand reproduzierbar |
| P2 | Unabhängiger Audit-Runner | Fünf Chats ohne Export gegeneinander prüfen | Runner liefert ehrliche Statuswerte |
| P3 | Echte Tab-Aktivierung | Seitenleisten-/Tab-Bindung sicher machen | aktiver Chat beweisbar |
| P4 | Sichtungsprotokoll | Überlappende Sichtfenster vollständig erfassen | Anfang/Ende/Lücken belegt |
| P5 | Semantik-Gate | Nachrichten unabhängig vergleichen | Match/Ambiguous/Mismatch korrekt |
| P6 | Recovery der fünf Chats | Fehlende historische Bereiche sauber nacherfassen | jeder Chat klassifiziert |
| P7 | VPS-Versiegelung | Artefakte atomar und versioniert speichern | Hashkette nachweisbar |
| P8 | Download-Versiegelung | VPS-Bytes und lokale Dateien gleich machen | Downloadhash identisch |
| P9 | Formatprüfung | HTML, MD, Events, JSON, Office prüfen | jedes Format klassifiziert |
| P10 | Fehler- und Recoverypfade | Abbruch, Reload, Netzwerk und Doppelungen testen | Fehler bleiben sichtbar |
| P11 | Fünf-Tab-Regressionslauf | gesamtes System real durchlaufen | fünf unabhängige Ergebnisse |
| P12 | Zielabnahme und Betrieb | Definition of Done und Pflege etablieren | Zielbild erfüllt |

---

## P0 — Fahrplan und Beweisvertrag

### Aufgabe

Den Statusvorrat und die Begriffe festlegen, bevor weitere Dateien oder Exporte bewertet werden.

### Zu definierende Zustände

```text
unknown       = noch nicht geprüft
running       = Prüfung läuft
complete      = alle Gates bestanden
partial       = Daten vorhanden, aber Lücke oder fehlender Beweis
blocked       = Prüfung kann wegen fehlender Quelle nicht abgeschlossen werden
ambiguous     = mehrere plausible Zuordnungen, menschliche Entscheidung nötig
superseded    = durch einen späteren Run ersetzt, historisch erhalten
```

### Artefakte

- Beweisvertrag mit Definitionen
- Statusschema
- Run-Namenskonvention
- Liste der fünf Conversation-IDs
- klare Trennung von historischem Run und Recovery-Run

### Abnahme

Jeder spätere Bericht kann erklären, warum ein Chat genau diesen Status hat. Kein Status hängt an einem Dateinamen.

### Rücksprung

Wenn neue Recorderdaten einen weiteren Zustand brauchen, wird P0 versioniert ergänzt, bevor bestehende Statuswerte umgedeutet werden.

---

## P1 — Bestand einfrieren

### Aufgabe

Den aktuellen Zustand der fünf offenen Tabs und der zugeordneten VPS-Ordner als Startpunkt festhalten.

### Prüfung

- URL und Conversation-ID pro Tab lesen
- Fensternummer, Tab-ID und Tab-Titel festhalten
- Recorder-Version und Browser-Version festhalten
- VPS-Ordner, Manifest, Nachrichten, Lücken und Zeitspuren inventarisieren
- vorhandene Downloads und Downloadpfade inventarisieren
- Hashes aller vorhandenen relevanten Dateien berechnen

### Regeln

Es wird nichts repariert und nichts überschrieben. Die Inventur ist read-only.

### Artefakte

```text
audit_runs/<run_id>/inventory.json
audit_runs/<run_id>/vps-files.jsonl
audit_runs/<run_id>/browser-tabs.json
audit_runs/<run_id>/checksums.sha256
```

### Abnahme

Ein zweiter Prüflauf kann anhand der Inventur feststellen, ob sich der Bestand verändert hat.

### Rücksprung

Bei nicht eindeutiger Zuordnung zurück nach P1; nicht mit einem vermuteten Ordner weiterarbeiten.

---

## P2 — Unabhängiger Audit-Runner

### Aufgabe

Ein kleiner read-only Runner prüft Live-DOM und VPS-Bestand, ohne den Exporter als Wahrheitsquelle zu verwenden.

### Mindestfunktionen

- fünf Conversation-IDs automatisch erkennen
- pro Chat separaten Auditdatensatz öffnen
- Live-Zähler, VPS-Zähler, Rollen, Lücken und Turnstatus aufnehmen
- Rohtext nur lesen, nicht verändern
- `complete`, `partial`, `blocked`, `ambiguous` ausgeben
- keine Downloads und keine Serverneustarts auslösen

### Abnahme

Der Runner muss den bekannten Bestand als nicht vollständig melden. Ein Runner, der alle fünf Chats grün meldet, ist kaputt.

### Redteam

- aktiver Tab wird verwechselt
- Chatseite steht bereits am Ende
- virtuelle Liste zeigt nur einen Ausschnitt
- UI-Hilfstexte werden als Nachricht gezählt
- unbekannte Rollen werden verworfen

### Verbesserung

Jeder Live-Datensatz enthält `conversation_id`, `tab_id`, `window_id`, `tab_instance_id`, Scrollposition, Viewport und einen DOM-Snapshot-Hash.

---

## P3 — Echte Tab-Aktivierung

### Aufgabe

Die bisher erkannte Schwachstelle der separat geöffneten Extension-Seite wird sauber lösen: Die Seitenleiste muss an den wirklich aktiven Chat gebunden sein.

### Vorgehen

1. echten Chat-Tab im virtuellen Desktop sichtbar aktivieren
2. kurzen realen Klick in den Chatbereich setzen
3. Seitenleiste über den normalen sichtbaren Mechanismus öffnen oder fokussieren
4. sichtbare Conversation-ID der Seitenleiste lesen
5. URL-ID, DOM-ID und Seitenleisten-ID vergleichen
6. nur bei dreifacher Übereinstimmung fortfahren

### Abnahme

Für jeden der fünf Tabs gilt:

```text
URL conversation_id
= Chat-DOM conversation_id
= Recorder-Seitenleisten conversation_id
```

### Blocker

Wenn die echte Seitenleiste nicht zuverlässig an den aktiven Tab gebunden werden kann, wird P3 als `blocked` markiert. Dann wird kein Cloud-Export als gültiger Beweis ausgegeben.

---

## P4 — Sichtungsprotokoll

### Aufgabe

Den sichtbaren Chat vollständig, sequenziell und überlappend erfassen.

### Sichtungsalgorithmus

1. Scrollcontainer erkennen und seine Geometrie lesen.
2. Container real anklicken.
3. Mit realem `Home` an den Anfang gehen.
4. warten, bis sich DOM und Scrollhöhe stabilisieren.
5. sichtbare Nachrichten als Fenster speichern.
6. mit mindestens 30 Prozent Überlappung weiter scrollen.
7. nach jedem Schritt wieder Stabilität abwarten.
8. „Mehr anzeigen“, eingeklappte Bereiche und laufende Antworten klassifizieren.
9. am Ende End-Sentinel und letzte Scrollposition speichern.

### Jede Sichtung speichert

```ts
type ViewWindow = {
  index: number;
  scrollTop: number;
  scrollHeight: number;
  viewportHeight: number;
  domHashBefore: string;
  domHashAfter: string;
  stable: boolean;
  messageKeys: string[];
  collapsedCount: number;
  expandedCount: number;
  timestamp: string;
};
```

### Abnahme

Anfangs- und End-Sentinel sind vorhanden, Fenster überlappen, kein Fenster endet mit instabilem DOM und jede Lücke hat Ursache oder ist ausdrücklich unbekannt.

---

## P5 — Semantik-Gate

### Aufgabe

Nicht rohe Dateien, sondern strukturierte Nachrichten vergleichen.

### Vergleichsschichten

1. Rohtext mit Rohhash
2. normalisierter Text mit Normalisierungsversion
3. Rolle
4. lokale Reihenfolge
5. Kontextfenster
6. Recorder-/VPS-ID, soweit vorhanden

### Ergebnis pro Nachricht

```text
match
missing-live
missing-vps
ambiguous
role-mismatch
text-mismatch
order-mismatch
```

### Abnahme

Künstlich veränderte Testdaten werden sicher erkannt: ein Zeichen, eine Rolle, eine vertauschte Reihenfolge und eine fehlende Nachricht müssen jeweils rot werden.

### Regel

`unknown` und `ambiguous` sind echte Ergebnisse, keine Fehler, die man für eine grüne Anzeige wegfiltern darf.

---

## P6 — Recovery der fünf Chats

### Aufgabe

Die historischen Aufnahmen retten, soweit die offenen Chatseiten die fehlenden Inhalte noch zeigen.

### Pro Chat

1. historischen Ordner nicht verändern
2. neuen Recovery-Run eröffnen
3. Chat anhand dreifacher ID-Zuordnung validieren
4. fehlende Sichtfenster real nacherfassen
5. neue Nachrichten mit Herkunft `recovery_run_id` markieren
6. alten und neuen Bestand getrennt diffen
7. nur bei vollständigem Match einen konsolidierten Beweis erzeugen

### Mögliche Ergebnisse

- **vollständig wiederhergestellt:** alle alten Lücken geschlossen und neu belegt
- **historisch teilweise:** Quelle zeigt nicht mehr alle fehlenden Bereiche
- **blockiert:** Chat nicht mehr zugänglich oder Zuordnung unklar
- **mehrdeutig:** sichtbarer Bestand kann nicht eindeutig dem alten Run zugeordnet werden

### Nicht erlaubt

- alte Lücken mit neuen Nachrichten still überschreiben
- neue Sichtungen auf das alte Startdatum zurückdatieren
- fehlende Antworten aus Kontext rekonstruieren

---

## P7 — VPS-Versiegelung

### Aufgabe

Nur bestandene semantische Audits dürfen zu einem vollständigen VPS-Artefakt versiegelt werden.

### Ablauf

1. kanonische Nachrichtenstruktur erzeugen
2. Exportbytes erzeugen
3. Bytezahl und SHA-256 berechnen
4. temporär schreiben
5. `fsync`
6. atomar in den Run-Ordner verschieben
7. Manifest mit Parent-Hash aktualisieren
8. Versiegelungsereignis append-only protokollieren

### Abnahme

Nach einem absichtlichen Abbruch existiert entweder das vollständige Artefakt oder kein als vollständig markiertes Artefakt.

### Datenmodell

```python
seal = {
    "run_id": run_id,
    "conversation_id": conversation_id,
    "message_count": message_count,
    "turn_count": turn_count,
    "gap_count": gap_count,
    "sha256": digest,
    "bytes": len(payload),
    "parent_manifest_sha256": parent_hash,
    "status": "sealed",
}
```

---

## P8 — Download-Versiegelung

### Aufgabe

Der Download muss exakt dieselben Bytes enthalten wie das VPS-Artefakt.

### Ablauf

1. Exportbytes vom bereits versiegelten Artefakt beziehen.
2. Download mit eindeutigem `run_id` und `artifact_id` auslösen.
3. Datei sofort in einen persistenten Auditordner schreiben.
4. Download-Hash berechnen.
5. VPS-Hash und Download-Hash vergleichen.
6. Datei aus dem persistenten Pfad erneut öffnen.
7. Prüfung im Manifest vermerken.

### Abnahme

```text
vps_sha256 == download_sha256
vps_bytes == download_bytes
vps_artifact_id == download_artifact_id
```

### Sonderfall

Ein temporärer Playwright-Pfad ist kein persistenter Downloadbeweis. `download.path()` allein zählt nicht als abgeschlossen; die Datei muss mit `saveAs()` in einem kontrollierten Ordner landen.

---

## P9 — Formatprüfung

### Aufgabe

Alle relevanten Exportformate gegen denselben kanonischen Nachrichtenbestand prüfen.

### Formate

- HTML: DOM-Nachrichten und sichtbare Rollen erneut zählen
- 1:1-Markdown: Nachrichtenblöcke und Reihenfolge extrahieren
- Events/Proof-Markdown: Marker, Lücken und Herkunft prüfen
- Raw JSON: kanonisch serialisieren und semantisch diffen
- DOCX: Text und Struktur extrahieren
- ODT: Text und Struktur extrahieren
- PDF: extrahierten Text gegen erwartete Nachrichten prüfen

### Abnahme

Jedes Format erhält einen eigenen `ExportAudit`-Status. Ein grünes JSON macht ein rotes PDF nicht grün.

---

## P10 — Fehler- und Recoverypfade

### Aufgabe

Nicht nur den Idealweg testen, sondern die Fehler, die den aktuellen Bestand verursacht oder verschleiert haben könnten.

### Tests

1. Browser steht am Ende, bevor `Home` gesendet wird.
2. Scrollbereich ist nicht fokussiert.
3. DOM ändert sich während eines Fensters.
4. Antwort bleibt im Status `streaming`.
5. „Mehr anzeigen“ bleibt geschlossen.
6. Recorder verliert Netzwerkverbindung.
7. VPS antwortet nach dem Upload nicht.
8. Export bricht nach temporärem Schreiben ab.
9. Download wird umbenannt oder doppelt erzeugt.
10. Browser stürzt zwischen zwei Fenstern ab.

### Abnahme

Jeder Fehler führt zu einem sichtbaren Status und einem wiederaufnehmbaren Checkpoint. Kein Fehler führt zu einem falschen `complete`.

---

## P11 — Fünf-Tab-Regressionslauf

### Aufgabe

Den kompletten Workflow mit allen fünf offenen Chats in fester Reihenfolge durchlaufen.

### Reihenfolge

1. Neuer Abschnitt RISSWANDLER
2. Reise Dauerloop
3. bau-browserextention
4. Neuer Name für VPS
5. VPS Stop Bestätigt

### Pro Chat wird geprüft

- dreifache Tab-ID-Übereinstimmung
- Anfang und Ende sichtbar
- überlappende Sichtfenster
- semantischer Match
- Lückenstatus
- VPS-Siegel
- lokaler Download
- Hashgleichheit
- Formatstatus

### Abnahme

Der Bericht zeigt fünf getrennte Reihen mit vollständiger Provenienz. Parallelität existiert nur auf Tab-Ebene; kritische Prüfung und Export laufen seriell.

---

## P12 — Zielabnahme und Betrieb

### Definition of Done

Das Ziel ist erreicht, wenn:

- alle fünf Chats einen eindeutigen Endstatus haben
- jeder `complete`-Chat Anfang, Ende und alle Gates bestanden hat
- jeder Download persistent vorhanden und hashgleich zum VPS ist
- kein Chat wegen stiller Lücken grün erscheint
- alle Formate separat geprüft oder bewusst als nicht erzeugt markiert sind
- ein zweiter Lauf denselben Bestand reproduzierbar bewertet
- ein Fehlerlauf nicht zu falscher Vollständigkeit führt
- Auditnotiz, Manifeste und Hashketten vorhanden sind

### Wenn nicht alle fünf vollständig werden

Das ist kein Scheitern des Systems. Ein ehrliches Ergebnis kann sein:

```text
2 complete
1 partial
1 blocked
1 ambiguous
```

Das Ziel ist nicht, fünf grüne Lichter zu erzwingen. Das Ziel ist, für jedes Licht einen belastbaren Grund zu haben.

---

## Lebender Überarbeitungszyklus

Der Fahrplan wird nicht einmal geschrieben und dann vergessen. Er bekommt einen festen Änderungszyklus.

### Nach jeder Arbeitsphase

1. Was hat die Phase bewiesen?
2. Was hat sie widerlegt?
3. Welche neue Fehlerklasse ist aufgetaucht?
4. Welche Annahme war falsch?
5. Welche Phase muss zurückgesetzt oder erweitert werden?
6. Welche neue Abnahmeregel fehlt?

### Versionierung

```text
v1.0  Grundfahrplan
v1.1  neue Erkenntnis ohne Phasenverschiebung
v1.2  neue Abnahmeregel oder neuer Fehlerpfad
v2.0  Änderung des Beweisvertrags oder der Gate-Reihenfolge
```

Jede Änderung bekommt Datum, Anlass, betroffene Phase und Entscheidung. Alte Fassungen bleiben nachvollziehbar; der aktuelle Fahrplan wird nicht rückwirkend umgeschrieben.

### Selbstprüfung durch Codex bei jedem Folgeauftrag

Vor dem nächsten Bauschritt prüfe ich automatisch:

- welcher aktuelle Fahrplanstand gilt
- welche Phase zuletzt abgenommen wurde
- welche Gates rot oder unklar sind
- ob neue Dateien oder Recorder-Versionen aufgetaucht sind
- ob der neue Auftrag in den bestehenden Scope passt
- ob der Fahrplan durch die neue Erkenntnis ergänzt oder wirklich geändert werden muss

Ich ergänze zuerst die Roadmap und handle danach. Dadurch bleibt sichtbar, warum ein neuer Schritt hinzugekommen ist.

## Fortschrittsformat für künftige Sessions

```text
Fahrplan: v1.x
Aktuelle Phase: Pn — Name
Status: grün / gelb / rot / blockiert
Bewiesen: ...
Widerlegt: ...
Neue Erkenntnis: ...
Nächster Schritt: ...
Rücksprungpunkt: ...
Keine Änderung an: ...
```

## Erster tatsächlicher Umsetzungsschnitt

Der gesamte Fahrplan ist groß, aber der erste Umsetzungsschnitt bleibt klein und vollständig:

1. P1-Inventur als reproduzierbares JSON erzeugen.
2. P2-Audit-Runner für genau die fünf bekannten IDs bauen.
3. P3-Dreifach-ID-Bindung an einem Chat beweisen.
4. P4 einen Chat vollständig mit überlappenden Fenstern erfassen.
5. Erst nach diesem einen grünen Teilabschnitt auf die übrigen vier Chats ausrollen.

Das ist kein erneutes Kleindenken. Es ist die kleinste vertikale Scheibe, die bereits die gesamte Beweiskette berührt und deshalb zeigt, ob die Architektur trägt.

## Aktueller Startpunkt

Aus dem bisherigen Audit starten wir nicht bei null:

- fünf offene Chats sind identifiziert
- die zugehörigen VPS-Ordner sind bekannt
- alle fünf historischen Aufnahmen haben sichtbare Lücken
- der semantische VPS-Export blockiert bereits korrekt bei Abweichung
- persistente Browserdownloads sind noch nicht nachgewiesen
- der nächste operative Schritt ist P1/P2, nicht ein blindes Neugenerieren von Dateien

## Schlussregel

Wir bauen nicht auf das Ziel hin, fünf Dateien zu erzeugen. Wir bauen auf das Ziel hin, bei jedem Chat jederzeit sagen zu können:

> Das hier war sichtbar. Das wurde eindeutig erfasst. Das liegt so auf dem VPS. Diese Downloadbytes sind dieselben. Und hier ist der Beweis dafür.
