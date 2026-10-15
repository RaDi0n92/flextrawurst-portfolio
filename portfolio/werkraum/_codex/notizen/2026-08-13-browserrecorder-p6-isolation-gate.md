---
datum: 2026-08-13
betrifft: [browserrecorder, p6, isolation, provenance, gate]
autor: codex bei Daniels VPS
importable: false
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe den P6-Gesamtvergleich, den Reise-Dauerloop-Incident und die fünf read-only Recovery-Artefakte gelesen.

Der entscheidende Befund war: read-only Recovery funktioniert, aber der sichtbare Recorder kann bei einem normalen Aufnahmestart in den historischen Ordner schreiben. Deshalb habe ich einen separaten Isolation-Gate-Runner gebaut.

## Was ich verstehe

Das Gate hasht jeden historischen Chatordner vor und nach der Prüfung. Es lässt nur `P6_READ_ONLY=1` zu, verlangt bei echten neuen Läufen eine neue Run-ID und bricht bei einer Altordner-Mutation fehl.

Zwei Prüfungen gegen die vorhandenen Recovery-Artefakte liefen mit `p6_isolation_passed`, null Mutationen und read-only-Markierung für alle fünf Chats.

## Was ich nicht verstehe

Der Recorder selbst ist weiterhin nicht als lokaler Quellbaum verfügbar. Das Gate schützt deshalb den äußeren Ablauf, ersetzt aber noch keine Änderung im Extension-Code.

## Was mich interessiert

Mich interessiert, ob aus dem Gate später ein verpflichtender Wrapper für jeden P6-Lauf wird oder ob die Extension eine native Recovery-Zielkonfiguration bekommt. Beides würde dieselbe Grenze ausdrücken.

## Was zusammenhängt und wie

```text
P6 read-only Evidence -> neue Rohtext-Records
Hash-Snapshot         -> historische Quelle unverändert prüfen
neue Run-ID           -> keine Überschreibung alter Recovery-Artefakte
Isolation-Gate        -> Provenienz vor/nach Lauf maschinell bewerten
P7                   -> bleibt bei partieller Semantik gesperrt
```

## Was konzeptionell darin steht

Ein Recovery-Lauf braucht einen Wächter an der Quelle. Nicht nur der Inhalt, auch der Ort, an dem er landet, gehört zum Beweis.

## Was mich heute beschäftigt hat

Der eigentliche Fortschritt war klein: ein Hash vor und nach dem Lauf. Aber genau dieser kleine Rand verhindert, dass ein scheinbar erfolgreicher Recovery-Lauf unbemerkt die Vergangenheit verändert.

## Was mich noch beschäftigt

Mich beschäftigt, ob der Gate-Lauf vor jedem Chat einzeln oder einmal als Batch über alle fünf Quellen laufen sollte. Einzelne Gates sind genauer, ein Batch-Manifest ist übersichtlicher.

## Tiefer eingetaucht

`p6_isolation_gate.py` kann bestehende read-only Artefakte prüfen oder neue Läufe seriell starten. Der echte `--run`-Modus verlangt ausdrücklich `--run-id-prefix`; dadurch können vorhandene Run-Verzeichnisse nicht versehentlich wiederverwendet werden.

Die geprüften historischen Nachrichtenbestände bleiben bei 179, 232, 111, 130 und 260 Zeilen. Das Gate meldet für alle fünf Quellen byte-identische Vorher-/Nachher-Bäume.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein dünner Sicherheitsfaden, der plötzlich eine ganze Bewegung hält. Kein großer Umbau, aber eine Grenze, die nun maschinell sichtbar ist.

## Warum dieser Code / diese Datei wohl existiert

Der Gate-Runner existiert, weil Provenienz nicht als Kommentar im Manifest genügen darf. Er macht aus „der alte Ordner wurde nicht verändert“ eine nachprüfbare Bedingung.

## Was ich beim Bauen brauche

Ich brauche für jeden Recovery-Lauf: Baseline-Hash, neue Run-ID, read-only-Vertrag, Ergebnisstatus und Nachher-Hash. Erst wenn alle fünf stimmen, darf der Gesamtvergleich als provenance-sauber gelten.

## Was noch fehlt bevor wir bauen können

Es fehlt weiterhin ein vollständiger semantischer Match. Das Gate löst die Provenienzfrage, nicht die 293 offenen Live-IDs oder die historischen Duplikate.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht**

Das Gate ist eine Schwelle zwischen Vergangenheit und neuer Sichtung. Es sagt nicht, was wahr ist; es verhindert, dass die beiden Zeugnisse heimlich ineinanderlaufen.

**Code-Skizze**

```python
before = tree_snapshot(old_folder)
assert read_only
run_recovery(new_run_id)
after = tree_snapshot(old_folder)
if before["tree_sha256"] != after["tree_sha256"]:
    fail_closed("historical_folder_mutated")
```

## Was ich mir merken will

Die Run-ID ist ein Sicherheitsfeld, kein Etikett. Wenn sie wiederverwendet werden kann, ist die Trennung nicht belastbar.

## Dokumente gehören zusammen

Das Gate gehört zum P6-Gesamtmanifest, zu den fünf read-only Runs und zum früheren sichtbaren Recorder-Incident des Reise-Dauerloops.

## Was mich überrascht hat

Der Gate-Code ist klein, aber die von ihm gesicherten Bäume sind groß genug, dass ein einzelner unerlaubter Marker sofort sichtbar würde.

## Wenn wir das bauen

**Vision-Schicht**

Wir bauen keine Versiegelung auf Vertrauen. Wir bauen eine Folge kleiner Schwellen, an denen ein falscher grüner Status nicht weiterwandern kann.

**Code-Skizze**

```python
gate = run_isolation_gate(
    old_folders=historical_sources,
    recovery_mode="read_only",
    require_new_run_id=True,
)
assert gate.status == "p6_isolation_passed"
assert not gate.mutations
```

## Resonanz

Der nächste sinnvolle Schritt ist jetzt nicht mehr „noch einmal klicken“, sondern die Schutzbedingung vor jeden weiteren Klick zu setzen.

## Die Schichten des Systems — wie ich sie jetzt sehe

1. historische Quellen
2. sichtbare Chatoberfläche
3. read-only Recovery-Evidence
4. Isolation-Gate mit Baum-Hashes
5. P6-Gesamtvergleich
6. gesperrte P7/P8-Versiegelung

## Was das Gespräch hinzugefügt hat

Daniels „ok go“ hat den P6-Blocker in eine konkrete technische Aufgabe übersetzt: Schutz vor Altordner-Mutation, bevor überhaupt ein neuer Lauf als gültig gelten darf.

## Vergessen-Wollen

Ich will nicht vergessen, dass das Gate nicht behauptet, die Semantik sei vollständig. Es schützt nur die Herkunft der noch partiellen Evidence.

## Was fehlt noch

P7 bleibt gesperrt. Es fehlen weiterhin vollständige historische Matches und eine native Recorder-Isolation. Das Gate ist der nächste Sicherheitsbaustein, nicht das Ende der Auditkette.
