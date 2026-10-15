---
datum: 2026-09-18
betrifft: [geni, sicherheit, systemd, integritaet]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe den wiederhergestellten Watcher unter `/root/werkraum_geni/inbox_antworten_watcher.py` erneut gegen den Git-Zustand geprüft: 429 Zeilen und SHA-256 `cd11a721b9ac8ebefa8b46e4fdebb39f24289db12c5331d245c410491276661c`.

Ich habe die neue Prüflogik in `/root/werkraum/_codex/tools/geni_watcher_integrity.py` sowie die beiden Unit-Quelldateien `/root/werkraum/_codex/tools/systemd/geni-watcher-integrity.service` und `/root/werkraum/_codex/tools/systemd/geni-watcher-integrity.timer` gelesen und lokal mit Python und `systemd-analyze verify` geprüft.

Auf dem VPS habe ich Journal, systemd-Zustand und den Watcher-Prozess rückgelesen. Der neue Prüfer meldete zweimal PASS; der Watcher blieb mit MainPID 13110, `NRestarts=0` und `active/running` unverändert.

## Was ich verstehe

Der sichere nächste Schritt nach der Wiederherstellung ist ein Beobachter, der eine erneute Abweichung sichtbar macht, ohne selbst zum Reparatur- oder Löschwerkzeug zu werden.

Der Prüfer vergleicht nur zwei feste Eigenschaften: Zeilenzahl und SHA-256 des wiederhergestellten Watchers. Ein Treffer endet erfolgreich, eine Abweichung landet als ALERT im Journal und liefert Exit-Code 1.

Der negative Pfad wurde mit einer temporären Ein-Zeilen-Datei ohne Berührung des echten Watchers geprüft: `check_target()` lieferte `False` und meldete `ALERT watcher integrity mismatch`.

Der systemd-Timer ruft den One-Shot-Dienst alle fünf Minuten auf. `ProtectHome=read-only`, `ProtectSystem=strict`, leere Capability-Bounding-Set und weitere Einschränkungen halten die neue Fähigkeit klein.

Zusätzlich beobachtet `/etc/systemd/system/geni-watcher-integrity.path` die Datei ereignisgesteuert. Die Path-Unit ist `enabled/active/waiting`; der Timer bleibt als zeitlicher Fallback aktiv.

Der ursprüngliche GENI-Antwort-Watcher lief anschließend selbst in einer Sandbox. `/etc/systemd/system/geni-inbox-antworten.service` ist jetzt `ProtectSystem=strict` und `ProtectHome=read-only`; Schreibzugriff gibt es nur für `/root/werkraum/geni_inbox` und `/root/geni_gedaechtnis/fragen_antworten`. Die Sicherheitsbewertung liegt bei Exposure 3.5.

Danach wurden auch `/etc/systemd/system/geni-inbox-viewer.service` und `/etc/systemd/system/geni-dokumentation-versionsarchiv-watch.service` gehärtet. Der Viewer liest nur und bleibt komplett read-only; der Archiv-Watcher darf ausschließlich `/root/werkraum/geni_dokumentation_versionsarchiv` beschreiben. Ihre Exposures liegen bei 3.5 beziehungsweise 3.2.

## Was ich nicht verstehe

Die genaue Herkunft der früheren 359 gelöschten Zeilen ist weiterhin nicht aus den erhaltenen Logs beweisbar. Der Integritätsmonitor erkennt eine neue Abweichung, erklärt aber nicht ihren Verursacher.

Ich weiß noch nicht, ob Daniels gewünschte Alarmierung später nur über Journal-Auswertung reicht oder ob eine sichtbare Surface-/Resonanz-Anzeige gebraucht wird.

## Was mich interessiert

Interessant ist, ob sich aus einem späteren ALERT zuverlässig eine zeitnahe Korrelation mit Audit-, Git- oder Session-Spuren bauen lässt, ohne den Watcher selbst mit zusätzlicher Logik zu belasten.

## Was zusammenhängt und wie

Die Wiederherstellung aus Git liefert den bekannten guten Zustand. Der feste Hash konserviert diesen Zustand als Sicherheitsanker. Der Timer erzeugt wiederholte Beobachtungen, das Journal bewahrt die einzelnen Ergebnisse, und der laufende GENI-Dienst bleibt davon getrennt.

## Was konzeptionell darin steht

Hier steht kein Selbstheilungssystem, sondern eine schmale Grenze zwischen „unverändert“ und „sichtbar abweichend“. Die Integrität wird beobachtbar, ohne neue Autorität über den laufenden Prozess zu beanspruchen.

## Was mich heute beschäftigt hat

Mich hat beschäftigt, wie wenig man nach einem Desktop-Absturz und einer beschädigten Datei noch sicher behaupten darf. Der Watcher ist jetzt wieder funktional; die Herkunft des Schadens bleibt eine offene forensische Frage.

## Was mich noch beschäftigt

Offen bleibt, wie lange der Timer selbst sichtbar und zuverlässig läuft, wenn genau die systemd- oder Journal-Schicht später ebenfalls Probleme bekommt.

## Tiefer eingetaucht

Der Prüfer liest Bytes, zählt `splitlines()` und bildet SHA-256. Er schreibt weder Zieldatei noch Git-Index und startet keinen Dienst neu. Der One-Shot lief erfolgreich, danach blieb nur der Timer wartend aktiv.

## Wie sich dieser Tag / diese Session angefühlt hat

Die Session fühlte sich nach dem forensischen Teil angenehm klein an: ein klarer Hash, ein kleiner Prüfer, zwei Units und ein sichtbarer PASS. Gerade nach dem vorherigen Chaos war die Begrenzung der neuen Macht der wichtigste Teil.

## Warum dieser Code / diese Datei wohl existiert

`/root/werkraum/_codex/tools/geni_watcher_integrity.py` existiert, damit der wiederhergestellte Watcher nicht wieder still in einen verkürzten Zustand fallen kann. Die systemd-Dateien existieren, damit diese Kontrolle nicht von einem offenen Terminal abhängt.

## Was ich beim Bauen brauche

Ich brauche weiterhin den bekannten guten Hash, einen gezielten Backup-Commit vor jeder Änderung, eine getrennte Unit und eine Rücklese aus Journal und systemd. Der Watcher selbst darf dabei nicht als Schreibziel dienen.

Für die unmittelbare Reaktion brauche ich jetzt nur noch die saubere Trennung zwischen Path-Trigger und Timer-Fallback; beide müssen denselben report-only-Dienst verwenden.

Für den laufenden Watcher brauche ich dieselbe Begrenzung auch im Unit-Vertrag: lesen aus Code und GENI-Kontext, schreiben nur in die beiden fachlich vorgesehenen Verzeichnisse, lokales Netzwerk nur für die LLM-Anfrage.

Für den Viewer und den Versionsarchiv-Watcher reicht eine noch engere Schicht: kein Netzwerk beim Archiv-Watcher, lokales HTTP beim Viewer, keine Schreibrechte außerhalb der jeweils fachlich nötigen Pfade.

## Was noch fehlt bevor wir bauen können

Für den reinen Monitor fehlt nichts Wesentliches. Für automatische Alarmierung oder Reparatur fehlen noch eine ausdrücklich definierte Reaktion, ein Zustandsmodell und eine Entscheidung, wer diese Reaktion ausführen darf.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Ein Integritätsereignis soll nicht nur „kaputt“ sagen, sondern den beobachteten Zustand, den erwarteten Anker, den Zeitpunkt und die Herkunft der Beobachtung sichtbar halten. Die Beobachtung bleibt append-only und verändert das beobachtete Wesen nicht.

**Code-Skizze:**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class IntegrityResult:
    target: str
    expected_sha256: str
    actual_sha256: str | None
    expected_lines: int
    actual_lines: int | None
    status: str  # "pass" | "alert" | "unreadable"
```

## Was ich mir merken will

Der aktuelle Anker ist `cd11a721b9ac8ebefa8b46e4fdebb39f24289db12c5331d245c410491276661c`, 429 Zeilen. Der Monitor meldet nur; er repariert nicht.

## Dokumente gehören zusammen

Die Wiederherstellungsnotiz `/root/werkraum/_codex/notizen/2026-09-18-geni-watcher-restore.md`, die Herkunftsnotiz `/root/werkraum/_codex/notizen/2026-09-18-geni-deletion-origin.md` und diese Monitornotiz bilden eine Kette: zurückholen, Herkunft begrenzen, erneute Abweichung sichtbar machen.

## Was mich überrascht hat

Überrascht hat mich, dass der laufende Watcher nach der Wiederherstellung stabil blieb und der neue Prüfer mit sehr wenig Code eine klare, wiederholbare Aussage liefern kann.

## Wenn wir das bauen

**Vision-Schicht:** Der Monitor bleibt ein stiller Zeuge. Er darf die Erinnerung an den guten Zustand tragen, aber nicht eigenmächtig entscheiden, dass eine Abweichung eine Reparatur rechtfertigt.

**Code-Skizze:**

```python
def check_target() -> bool:
    content = TARGET.read_bytes()
    actual = sha256(content).hexdigest()
    lines = len(content.splitlines())
    if actual != EXPECTED_SHA256 or lines != EXPECTED_LINES:
        logger.error("ALERT watcher integrity mismatch")
        return False
    logger.info("PASS watcher integrity")
    return True
```

## Resonanz

[[abwurf: Ein Sicherheitsmonitor ist hier gut, wenn seine Macht kleiner bleibt als die Unsicherheit, die er sichtbar macht.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Unten liegt die wiederhergestellte Datei als Arbeitswirklichkeit. Darum liegt Git als Herkunftsanker. Darüber liegt der report-only-Prüfer. Daneben läuft systemd als zeitlicher Taktgeber und Journal als sichtbare Spur. Keine dieser Schichten darf unbemerkt die anderen ersetzen.

## Was das Gespräch hinzugefügt hat

Daniels wiederholtes „gogogo“ hat die Entscheidung für den nächsten kleinen, reversiblen Sicherheitsschritt getragen: weiterarbeiten, aber ohne Reparaturautomatik und ohne den stabilen Watcher erneut zu berühren.

## Vergessen-Wollen

Vergessen werden darf nicht, dass der frühere Schaden trotz intensiver Suche keinen beweisbaren Verursacher ergeben hat. Ebenso darf nicht vergessen werden, dass ein grüner Hash nur den Zustand beweist, nicht die Absicht hinter einer späteren Änderung.

## Was fehlt noch

Es fehlt eine spätere Entscheidung über Alarmweiterleitung und Aufbewahrung von ALERT-Ereignissen. Außerdem ist `graphify` in der lokalen Umgebung nicht installiert; ein Graph-Update konnte deshalb nicht ausgeführt werden.

Die echte Ereignisauslösung wurde nicht durch Berühren der Produktionsdatei künstlich provoziert. Validiert sind Unit-Syntax, Aktivierung und der separate negative Prüferpfad.

Auditd ist auf dem VPS nicht installiert. Die Verursacher-Zuordnung bleibt deshalb eine offene zweite Ausbaustufe; die aktuelle Sandbox verhindert zumindest, dass der Watcher außerhalb seiner erlaubten Schreibbereiche weiterwirkt.

Die drei aktiven GENI-Dienste wurden nacheinander kontrolliert neu geladen und geprüft. Die alten Units liegen unter `/etc/systemd/system/geni-inbox-antworten.service.pre-sandbox-20260918`, `/etc/systemd/system/geni-inbox-viewer.service.pre-sandbox-20260918` und `/etc/systemd/system/geni-dokumentation-versionsarchiv-watch.service.pre-sandbox-20260918`.
