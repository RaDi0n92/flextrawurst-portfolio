---
datum: 2026-08-13
betrifft: [browserrecorder, p6, readonly-recovery, provenance, audit]
autor: codex bei Daniels VPS
importable: false
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe den P6-Vertrag, den vorherigen Reise-Dauerloop-Incident, die vier noch offenen Chatordner und die aktuelle Chromium-Bindung gelesen.

Der Vertrag verlangt getrennte Recovery-Runs, echte Sichtfenster und eine sichtbare Herkunft. Die sichtbare Aufnahme hat beim Reise-Dauerloop gezeigt, warum der Schreibpfad selbst geprüft werden muss: Der Recorder schrieb in den alten Ordner.

Danach habe ich die vier übrigen Chats ausschließlich read-only mit echten Home-/Wheel-Eingaben gesichtet. Kein `startImport`, kein `finishImport`, kein Export.

## Was ich verstehe

Die vier read-only Runs erreichten jeweils den End-Sentinel und blieben fehlerfrei. Sie liefern Rohtext-Records in eigenen Run-Ordnern, ohne die historischen Ordner zu verändern.

Die Ergebnisse sind weiterhin partiell: `match` und `ambiguous` können gezählt werden, aber fehlende Live-Bereiche bleiben fehlend. P6 ist damit für die vier Chats sauberer belegt, nicht vollständig semantisch bestanden.

## Was ich nicht verstehe

Ich verstehe weiterhin nicht, ob die Extension einen echten neuen Zielordner unterstützen kann. Die laufende Chromium-Extension liegt außerhalb des Werkraums; ihre UI-Quelle ist sichtbar, aber nicht als lokaler, sicher patchbarer Arbeitsbaum verfügbar.

## Was mich interessiert

Mich interessiert, ob der read-only Pfad langfristig der ehrlichere Recovery-Mechanismus ist: weniger Infrastrukturbehauptung, aber klare Rohtext-Evidence. Vielleicht ist eine externe Recovery-Schicht besser als ein Recorder, der seinen historischen Speicherpfad nicht wechseln kann.

## Was zusammenhängt und wie

```text
P6-Vertrag -> getrennte Run-ID und keine Altordner-Mutation
Chromium-UI -> reale Eingabe und sichtbare Chatgeometrie
read-only Runner -> Rohtext + stabile Fenster ohne VPS-Schreibpfad
P6 Sammelmanifest -> vier Chats getrennt zusammenfassen
P7 -> bleibt wegen partieller Semantik und fehlender Isolation gesperrt
```

## Was konzeptionell darin steht

Eine Recovery darf sichtbar machen, ohne Besitz über die alte Spur zu beanspruchen. Die neue Sichtung ist ein eigenes Zeugnis, kein Nachtrag, der sich als Vergangenheit verkleidet.

## Was mich heute beschäftigt hat

Nach dem Incident war „weiter“ nicht gleichbedeutend mit erneutem Start. Weiter hieß: denselben Prüfzweck mit einem engeren, sicheren Eingriff ausführen.

## Was mich noch beschäftigt

Mich beschäftigt die Differenz zwischen voller sichtbarer Strecke und voller historischer Abdeckung. Ein End-Sentinel sagt, dass die aktuelle virtuelle Strecke beendet ist; er sagt nicht, dass jede alte Nachricht heute wieder sichtbar war.

## Tiefer eingetaucht

Die vier neuen Runs endeten so: Neuer Abschnitt RISSWANDLER 367 Fenster/90 Records; VPS Stop Bestätigt 283/82; Neuer Name für VPS 254/103; bau-browserextention 220/38. Alle hatten 0 Fehler und `at_bottom: true`.

Die konservativen Textvergleiche ergaben: Neuer Abschnitt 16 Matches, 73 Duplikatfälle, 1 Textvariante, 3 missing-live; VPS Stop 61 Matches, 14 Duplikatfälle, 2 Textvarianten, 3 Textabweichungen, 9 missing-live, 2 missing-vps; Neuer Name 77 Matches, 15 Duplikatfälle, 1 Textvariante, 3 Textabweichungen, 2 missing-live, 7 missing-vps; bau-browserextention 17 Matches, 6 Duplikatfälle, 3 Textvarianten, 11 Textabweichungen, 126 missing-live, 1 missing-vps.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein vorsichtiges Weitergehen nach einem sichtbaren Fehltritt. Die Bewegung wurde kleiner, aber dadurch belastbarer.

## Warum dieser Code / diese Datei wohl existiert

`p6_recovery_visible_text.py` kann jetzt per Umgebungsparametern mehrere Chats read-only erfassen. Das Sammelmanifest hält die vier Runs, ihre Herkunft, Geometrie und konservativen Vergleichszahlen zusammen.

## Was ich beim Bauen brauche

Ich brauche pro Chat einen eigenen Run-Ordner, eine eindeutige Run-ID, Rohtext pro Record, stabile IDs wo vorhanden und einen Beleg, dass der alte Ordner vor und nach der Sichtung unverändert blieb.

## Was noch fehlt bevor wir bauen können

Vor P7 fehlen vollständige semantische Matches und eine sichere Recorder-Isolation. Die read-only Evidence reicht für P6-Teilbefunde, aber nicht für ein vollständiges VPS-Artefakt.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht**

Jede Recovery-Sichtung bleibt ein eigener Raum. Sie darf an historische Nachrichten anknüpfen, aber nie deren Herkunft verschlucken.

**Code-Skizze**

```python
ReadOnlyRecovery(
    recovery_run_id: str,
    conversation_id: str,
    windows: list[WindowEvidence],
    records: list[VisibleMessage],
    old_folder_sha256_before: str,
    old_folder_sha256_after: str,
    old_folder_modified: bool,
)
```

## Was ich mir merken will

Read-only ist hier keine halbe Lösung, sondern die sichere Antwort auf einen nicht isolierten Recorder-Schreibpfad.

## Dokumente gehören zusammen

Die vier Runs gehören zum Reise-Dauerloop-Incident, zum P5-v3-Vergleich, zum P4-Run und zum Sammelmanifest `audit-20260813T-p6-recovery-readonly-rest-v1`.

## Was mich überrascht hat

Auch ohne Recorder-Start schrumpft und wächst die virtuelle Strecke während des Scrollens. Die reale Stabilitätsprüfung bleibt deshalb notwendig, obwohl kein VPS-Schreibpfad beteiligt ist.

## Wenn wir das bauen

**Vision-Schicht**

Wir bauen eine Recovery, die nur neue Belege erzeugt und den alten Speicher als unveränderliche Referenz behandelt. Vollständig ist sie erst, wenn jede alte Lücke entweder neu belegt oder ehrlich als nicht mehr sichtbar markiert ist.

**Code-Skizze**

```python
for chat in chats:
    before = hash_tree(chat.old_folder)
    evidence = read_visible_dom_with_real_input(chat.page)
    after = hash_tree(chat.old_folder)
    assert before == after
    save_atomic(chat.recovery_run / "visible_evidence.json", evidence)
```

## Resonanz

Die vier Runs zeigen: Man kann vorankommen, ohne die alte Spur erneut zu berühren. Das ist langsamer als ein grüner Knopf, aber näher an dem, was der Audit eigentlich wissen soll.

## Die Schichten des Systems — wie ich sie jetzt sehe

1. historische VPS-Bestände
2. P4-Geometrie und Sichtfenster
3. P5-konservativer Semantik-Gate
4. P6-Incident des nicht isolierten sichtbaren Recorders
5. P6-read-only-Rohtext-Recovery
6. getrennte Run-Manifeste und Vergleichsbefunde
7. gesperrte P7/P8-Versiegelung

## Was das Gespräch hinzugefügt hat

Daniels „gogogo“ hat die Arbeit nach dem Incident wieder geöffnet, aber die Richtung blieb eng: die vier übrigen Chats erfassen, ohne den riskanten Button erneut zu drücken.

## Vergessen-Wollen

Ich will nicht vergessen, dass „nur weiter“ kein Auftrag ist, die Provenienzregeln zu lockern. Gerade unter Tempo muss der Scope kleiner werden.

## Was fehlt noch

P6 bleibt `historical_partial`. Für P7 fehlen vollständige Matches; für einen sicheren Recorder-Recovery-Lauf fehlt ein isolierter Zielpfad. Die neuen read-only Artefakte sind gesichert, die alten Ordner sind unverändert.
