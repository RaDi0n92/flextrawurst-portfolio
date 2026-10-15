---
datum: 2026-08-13
betrifft: [browserrecorder, p6, recovery, reise-dauerloop, provenance, audit]
autor: codex bei Daniels VPS
importable: false
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe den P6-Abschnitt des Browserrecorder-Fahrplans, den P5-Befund, den historischen Ordner von „Reise Dauerloop“, den P4-Run und die aktuelle sichtbare Chat-/Sidepanel-Bindung gelesen.

Im Fahrplan steht ausdrücklich: „historischen Ordner nicht verändern“, „neuen Recovery-Run eröffnen“ und „alten und neuen Bestand getrennt diffen“. Diese Sätze waren in dieser Session keine Dekoration, sondern der Prüfpunkt, an dem der zweite Versuch rot wurde.

Die neue Live-Sichtung hat echte Rohtexte geliefert. Sie hat aber beim sichtbaren Aufnahmestart 31 neue Zeilen und begleitende Marker in den alten Ordner geschrieben. Dieser Eingriff wurde erkannt, als Incident festgehalten und auf den Git-Baseline-Zustand zurückgesetzt.

## Was ich verstehe

Der read-only Recovery-v1-Lauf konnte 31 sichtbare Records mit Rohtext sammeln, ohne den alten Ordner anzufassen. Der getrennte Recovery-v2-Lauf mit sichtbarem Prüfscan erreichte 100 stabile Fenster und den End-Sentinel, zeigte aber zugleich, dass der Recorder seine neue Aufnahme in den alten Chatordner schreibt.

Der gültige fachliche Status bleibt deshalb `p6_historical_partial`: 19 eindeutige Matches, 10 historische Duplikatfälle, 1 Textabweichung, 1 Record ohne VPS-Gegenstück und 153 alte stabile IDs ohne aktuelle Live-Sichtung. Es gibt keinen konsolidierten Beweis.

## Was ich nicht verstehe

Ich verstehe noch nicht, ob die Extension einen separaten Recovery-Zielordner oder eine echte `recovery_run_id`-Isolation unterstützt, ohne den historischen Chatpfad mitzuschreiben. Die UI zeigt den Prüfscan als VPS-getrennt an, der konkrete Schreibpfad verhält sich aber anders.

Unklar bleibt außerdem, ob die 153 fehlenden stabilen IDs nur außerhalb der aktuell nachgeladenen virtuellen Strecke liegen oder ob sie in der heutigen Chatoberfläche nicht mehr zugänglich sind.

## Was mich interessiert

Mich interessiert die Grenze zwischen „der Browser zeigt den Text“ und „der Recorder darf diesen Text in eine Provenienzschicht schreiben“. P6 braucht beides: Sichtbarkeit und Herkunftstrennung. Eine neue Sichtung darf nicht dadurch alt aussehen, dass sie in den alten Ordner fällt.

## Was zusammenhängt und wie

```text
P5 missing-live -> P6 Recovery-Kandidat
P6 read-only    -> Rohtext sichtbar, alte Quelle unverändert
P6 visible scan -> mehr Nachladung, aber unerlaubte Altordner-Mutation
Incident        -> Mutation sichtbar machen und Baseline wiederherstellen
P6 diff         -> neuer Bestand getrennt, kein Consolidation-Beweis
P7             -> bleibt gesperrt
```

## Was konzeptionell darin steht

Recovery ist keine Reparatur des Alten. Es ist eine neue Zeugenschaft über etwas, das heute wieder sichtbar wird. Die neue Zeugenschaft muss ihren eigenen Namen tragen, sonst wird aus Wiederfinden eine rückdatierte Behauptung.

## Was mich heute beschäftigt hat

Der gefährlichste Schritt war nicht das Scrollen, sondern der sichtbare Startknopf. Er sah wie ein neuer Prüfscan aus und war technisch doch an den historischen Ordner gebunden. Genau deshalb braucht ein Audit nicht nur End-Sentinels, sondern auch Schreibpfad-Provenienz.

## Was mich noch beschäftigt

Ich will den nächsten Recovery-Versuch erst zulassen, wenn der Zielpfad vor dem Start beobachtbar und getrennt ist. Sonst kann jeder weitere „Fortschritt“ die historische Quelle erneut verschieben.

## Tiefer eingetaucht

Recovery-v1: 96 Fenster, 31 Records, 0 Fehler, End-Sentinel erreicht, Rohtext pro Record vorhanden. Recovery-v2: 100 Fenster, 31 Records, 0 Fehler, End-Sentinel erreicht. Der Vergleich gegen den nach der Rücksetzung wieder 232 Zeilen umfassenden Baseline-Bestand klassifiziert 19 als `match`, 10 als `ambiguous-duplicate-history`, 1 als `changed-text`, 1 als `missing-vps` und 153 alte IDs als `missing-live`.

Die 31 neuen Zeilen der sichtbaren Aufnahme wurden nicht als historische Wahrheit übernommen. Sie sind im Incident und im separaten Recovery-Artefakt nachvollziehbar, während der alte Chatordner wieder 232 Nachrichten enthält.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein sauberer Lauf, der an der Tür zum Speicher plötzlich seine Herkunft verrät. Das war unangenehm, aber nützlich: Der rote Befund kam früh genug, um die alte Spur zurückzusetzen.

## Warum dieser Code / diese Datei wohl existiert

`p6_recovery_visible_text.py` existiert, um sichtbaren Chattext mit echten Klick-/Wheel-Eingaben und adaptiver Stabilitätsprüfung neu zu bezeugen. `p6_compare_recovery.py` existiert, um diese neue Zeugenschaft gegen die alte Quelle zu diffen, ohne sie zusammenzuschieben.

`P6_CONTRACT_INCIDENT.json` existiert, damit der unerlaubte Schreibpfad nicht als unsichtbare Nebensache aus der Geschichte fällt.

## Was ich beim Bauen brauche

Ich brauche einen Recovery-Writer, dessen Zielordner vor dem ersten Aufnahmestart feststeht und dessen `recovery_run_id` in jeder neuen Nachricht landet. Außerdem brauche ich einen Schreibpfad-Test: vor Start Baseline-Hash, während Lauf erlaubte Zieländerungen, nach Finish alter Ordner unverändert.

## Was noch fehlt bevor wir bauen können

Es fehlt eine echte Isolation der Extension. Entweder muss der Recorder einen neuen Recovery-Run-Ordner unterstützen, oder P6 muss vollständig read-only bleiben und die Rohtexte ausschließlich außerhalb des VPS-Recorders sichern.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht**

Alte Quelle und neue Sichtung stehen nebeneinander wie zwei Zeugnisse. Keine Seite wird überschrieben. Jede neue Nachricht trägt sichtbar, wann und unter welchem Recovery-Namen sie wieder gesehen wurde.

**Code-Skizze**

```python
RecoveryRecord(
    recovery_run_id: str,
    conversation_id: str,
    stable_id: str | None,
    role: Literal["user", "assistant", "unknown"],
    raw_text: str,
    normalized_text: str,
    text_sha256: str,
    source: Literal["visible_dom_recovery"],
    first_window: int,
)

RecoveryManifest(
    old_folder_sha256_before: str,
    old_folder_sha256_after: str,
    recovery_folder: str,
    old_folder_modified: bool,
    consolidated: bool,
)
```

## Was ich mir merken will

Ein sichtbarer Prüfscan ist noch keine getrennte Recovery. Der Schreibpfad muss genauso geprüft werden wie der Scrollrand.

[[abwurf: Eine neue Sichtung darf nicht dadurch alt aussehen, dass sie in den alten Ordner fällt.]]

## Dokumente gehören zusammen

Diese Session gehört zu `audit-20260813T-p5-semantic-v3`, `audit-20260813T-p4-corrected-v2`, dem historischen Reise-Dauerloop-Ordner, `p6_recovery_visible_text.py`, `p6_compare_recovery.py` und dem Incident `P6_CONTRACT_INCIDENT.json`.

## Was mich überrascht hat

Der Recorder konnte trotz 100 stabiler Fenster und sauberem End-Sentinel nicht beweisen, dass er getrennt schreibt. Geometrische Sauberkeit und Provenienz-Isolation sind zwei verschiedene Achsen.

## Wenn wir das bauen

**Vision-Schicht**

P6 soll eine Rettung ermöglichen, ohne die Vergangenheit umzuschreiben. Der gute Ausgang ist entweder vollständige Wiederherstellung mit sauberer Trennung oder ein klarer historischer Teilbefund. Ein still verschobener Altbestand ist kein Fortschritt.

**Code-Skizze**

```python
before = hash_tree(old_folder)
run = open_recovery_run(recovery_run_id=new_uuid())
assert run.target_folder != old_folder
capture_visible_text(run)
after = hash_tree(old_folder)
assert before == after
write_diff(old_folder, run.target_folder)
```

## Resonanz

Der wichtigste P6-Erfolg ist heute nicht die Zahl 100. Es ist, dass der Schreibpfad als Teil der Wahrheit sichtbar geworden ist.

## Die Schichten des Systems — wie ich sie jetzt sehe

1. historische Chatquelle mit 232 Baseline-Nachrichten
2. P4-strukturelle Sichtfenster
3. P5-konservativer Semantikvergleich
4. P6-read-only-Rohtext-Recovery
5. P6-sichtbarer Prüfscan mit Incident
6. getrennte Recovery-Artefakte und Rücksetzung der Altquelle
7. noch gesperrtes P7/P8-Versiegeln

## Was das Gespräch hinzugefügt hat

Daniels „ok go“ hat nicht nur den nächsten Lauf ausgelöst. Es hat sichtbar gemacht, dass „weiter“ hier bedeutet: mit einer neuen Spur weiter, nicht mit einer bequem überschriebenen alten.

## Vergessen-Wollen

Ich will nicht vergessen, dass ein funktionierender UI-Button die falsche Systemgrenze überschreiten kann. Sichtbar, klickbar und erfolgreich heißt nicht automatisch provenance-sicher.

## Was fehlt noch

P6 ist für diesen Chat historisch teilweise, nicht abnahmefähig vollständig. Vor weiteren Chats fehlt ein isolierter Recovery-Zielpfad oder eine rein externe read-only Erfassung. P7 darf erst beginnen, wenn alle semantischen und provenancebezogenen Gates bestanden sind.
