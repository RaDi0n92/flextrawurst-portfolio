---
datum: 2026-08-13
betrifft: [browser-recorder, historische-recovery, p6, p7, provenance]
importable: false
autor: codex bei Daniels VPS
---

# Browser Recorder — native historische Recovery-Isolation

## Was ich gelesen habe

Ich habe den bestehenden Browser-Capture-Pfad in `tools/action_history/browser_capture.py` gelesen. Entscheidend war der alte gemeinsame Einstieg über `resolve_conversation()`: Auch `historical_import_*`-Events konnten dadurch im stabilen Chatordner landen.

Ich habe außerdem die beiden Extension-Quellen gelesen: die Arbeitskopie unter `tools/chatgpt_browser_recorder/extension/` und die direkt geladene Referenz unter `refferenzen/AI-UI-RECORDER-v1.6.5-DIREKT-LADEN/`. Der sichtbare Recorder lebt in beiden Schichten: Server-Ack und laufender Import-State müssen dieselbe Recovery-Identität kennen.

Die vorhandenen P6-Artefakte und Isolation-Gate-Läufe bleiben Referenz. Sie wurden nicht umgeschrieben. Der bisherige P6-Befund bleibt `p7_eligible: false`, weil fehlende Live-Treffer, historische Duplikate, Textänderungen und Varianten nicht durch eine neue Ablage verschwinden.

## Was ich verstehe

Historische Sichtung ist eine eigene Aufnahmequelle. Sie darf den stabilen Live-Chatordner nicht mit nachgeladenen oder rekonstruierten Turns anreichern. Der Import braucht deshalb eine unveränderliche `import_id`, einen eigenen Recovery-Ordner und eine explizite Exportroute.

## Was ich nicht verstehe

Noch nicht live geprüft ist, ob der aktuell laufende Chromium-Prozess nach einem kontrollierten Extension-/Service-Reload alle neuen Ack-Felder tatsächlich bis zum Ende des UI-Imports behält. Die Quellpfade sind angepasst und die Tests grün; der laufende Service wurde gemäß Betriebsregel nicht automatisch neu gestartet.

## Was mich interessiert

Mich interessiert als nächstes der echte Übergang von `recovery_run_id` aus dem Server-Ack in die sichtbare Delivery-Zusammenfassung. Dort muss der Recovery-Lauf als eigene Herkunft lesbar bleiben, ohne dass er wie ein normaler Chat-Export aussieht.

## Was zusammenhängt und wie

`import_id` identifiziert den historischen Import. Daraus entsteht serverseitig ein eigener Ordner. Der Ordner erhält `recovery_run_id = recovery-{import_id}`. Die API gibt diese ID im Ack zurück, und die Extension übernimmt sie in den aktiven Importjob. Ein Export mit `import_id` liest den Recovery-Ordner; ein vollständiger Chat-Export liest weiter ausschließlich den stabilen Quellordner.

## Was konzeptionell darin steht

Die Isolation ist keine technische Ablagekosmetik, sondern eine Provenienzgrenze: Live-Geschichte und historische Wiederholung dürfen nebeneinander existieren, aber nicht dieselbe Identität behaupten. Ein Recovery-Lauf ist ein Ereignis über eine Quelle, nicht die Quelle selbst.

## Was mich heute beschäftigt hat

Die lange P4-Sichtung hat gezeigt, wie schnell ein scheinbar kleiner UI-Schritt zu einem falschen Vollständigkeitsbeleg werden kann: Overlay, virtueller Viewport und eine unpassende Mindestschrittweite waren jeweils eigene Fehlerklassen. Die Korrektur musste deshalb zuerst die Beweisführung reparieren und erst danach den Lauf fortsetzen.

## Was mich noch beschäftigt

Die P6-Zahlen sind weiterhin ein Befund, kein Freifahrtschein: 190 exakte Treffer stehen neben 293 fehlenden Live-Treffern, 118 mehrdeutigen historischen Duplikaten, 18 Textänderungen, 7 Varianten und 11 fehlenden VPS-Fällen. P7 darf erst nach einer frischen, isolierten Live-Sichtung neu bewertet werden.

## Tiefer eingetaucht

Die native Lösung hängt nicht an Dateinamen allein. Der Index merkt sich `historical_imports[import_id]` mit Quellkonversation, Recovery-Lauf und Zielordner. Das Manifest des Recovery-Ordners markiert `capture_scope: historical_import_recovery` und `source_folder_immutable: true`. Dadurch bleibt die Herkunft selbst dann erkennbar, wenn später ein Export oder eine Auswertung auf den Ordner zugreift.

## Wie sich dieser Tag / diese Session angefühlt hat

Zäh, aber nützlich. Der Lauf war langsam genug, um Ungeduld als Fehlerquelle sichtbar zu machen. Am Ende war die wichtigste Bewegung nicht mehr Scrollen, sondern eine klare Grenze zwischen dem, was bereits belegt ist, und dem, was erst nach Reload und neuer Sichtung belegt werden darf.

## Warum dieser Code / diese Datei wohl existiert

Der Capture-Code existiert, damit sichtbare UI-Handlungen als nachvollziehbare, append-only Spuren in den Werkraum gelangen. Diese Änderung sorgt dafür, dass eine historische Handlung nicht versehentlich die Identität der Live-Unterhaltung übernimmt.

## Was ich beim Bauen brauche

Ich brauche weiterhin die echte Chatoberfläche, den sichtbaren Sidepanel-Import, stabile DOM-Snapshots und eine persistente Trennung von Quell- und Recoveryordner. Der Service muss für die nächste Live-Prüfung kontrolliert neu geladen werden; dieser Schritt ist noch nicht ausgeführt.

## Was noch fehlt bevor wir bauen können

Für die nächste Abnahme fehlen ein kontrollierter Reload des laufenden Recorders, ein kleiner Smoke-Test mit einem neuen historischen Import und danach ein neuer P6-Vergleich. Erst wenn dieser Durchlauf die Recovery-Ordner bestätigt und die historischen Quellordner unverändert bleiben, kann P7 erneut geprüft werden.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht**

Ein historischer Import ist ein eigener Raum mit sichtbarer Herkunft. Er darf sich auf dieselbe Unterhaltung beziehen, aber nie deren Live-Körper werden. `import_id` ist der Anker; `recovery_run_id` erzählt, welcher Wiederherstellungslauf daraus entstanden ist.

**Code-Skizze**

```python
index["historical_imports"][import_id] = {
    "folder_name": recovery_folder,
    "conversation_id": cid,
    "local_conversation_id": lid,
    "recovery_run_id": f"recovery-{import_id}",
    "created_utc": now,
}

manifest = {
    "capture_scope": "historical_import_recovery",
    "historical_import_id": import_id,
    "recovery_run_id": f"recovery-{import_id}",
    "source_conversation_folder": stable_folder,
    "source_folder_immutable": True,
}
```

## Was ich mir merken will

Nicht `historical_import_*` über den normalen Conversation-Resolver laufen lassen. Nicht aus einem erreichten Scroll-Ende auf semantische Vollständigkeit schließen. Und: Ein grüner Test im Temp-Store ist ein Codebeleg, kein Beleg dafür, dass der laufende Browser bereits den neuen Code geladen hat.

## Dokumente gehören zusammen

Die native Implementierung gehört zu `browser_capture.py`, den beiden Extension-Ack-/Core-Paaren, dem Human-Documents-Regressionstest und dem P6-Isolation-Gate. Die P6-Read-only-Berichte gehören als unveränderte Vergleichsbasis daneben, nicht in denselben Recoveryordner.

## Was mich überrascht hat

Der eigentliche Serverumbau war klein: ein eigener Resolver und ein expliziter Exportpfad. Die größere Arbeit lag in den Identitätsübergängen und darin, dass der bestehende Test zuerst eine stabile sichtbare Quelle anlegen musste, bevor sein historischer Export sinnvoll geprüft werden konnte.

## Wenn wir das bauen

**Vision-Schicht**

Wir bauen keinen Import, der Vergangenheit in Gegenwart umschreibt. Wir bauen eine kontrollierte Sichtungsschicht, in der jede Wiederholung ihren eigenen Abdruck trägt und die Quelle unangetastet bleibt.

**Code-Skizze**

```javascript
function handleAck(state, ack) {
  const job = state.activeImport;
  if (job && ack.import_id === job.importId && ack.recovery_run_id) {
    job.recoveryRunId = ack.recovery_run_id;
  }
  // bestehende Ack-Verarbeitung bleibt erhalten
}
```

Als nächster Bauschritt kommt kein weiterer Umbau, sondern der kontrollierte Reload und der echte UI-Smoke-Test. Danach wird P6 mit neuen, getrennten Artefakten wiederholt.

## Resonanz

[[abwurf: Ein Recovery-Lauf darf sich auf dieselbe Unterhaltung beziehen, aber nie deren Live-Körper werden.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Unten liegt die sichtbare Chatoberfläche. Darüber liegt der Recorder mit echten Klicks, Home und Wheel. Daneben liegt der serverseitige Action-History-Capture mit stabilen und historischen Ordnern. Darüber liegen P6-Vergleich und P7-Eignung. Die Schichten dürfen Informationen austauschen, aber ihre Provenienzen nicht verschmelzen.

## Was das Gespräch hinzugefügt hat

Daniels wiederholtes „ok go“ bedeutet hier: weiterarbeiten und den Abbruch sauber fortsetzen, nicht den offenen Betriebsübergang verschweigen. Deshalb ist der Code fertig gesichert, aber der laufende Service nicht still neu gestartet.

## Vergessen-Wollen

Vergessen werden soll die Versuchung, die vorhandenen P4-/P5-Partialstände nachträglich grün zu färben. Sie bleiben als Geschichte des Fehlers und der Korrektur erhalten.

## Was fehlt noch

- kontrollierter Reload von `chatgpt-browser-recorder.service` beziehungsweise der geladenen Extension;
- neuer kleiner historischer UI-Import mit sichtbarer `recovery_run_id`-Weitergabe;
- erneuter P6-Live-/History-Vergleich;
- P7-Entscheidung erst auf Basis dieses neuen Laufs.
