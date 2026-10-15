---
datum: 2026-09-18
betrifft: [geni, watcher, systemd, restore, sicherheit]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe die beschädigte Arbeitsbaumdatei `/root/werkraum_geni/inbox_antworten_watcher.py` und ihre vollständige Git-Version gelesen. Die Arbeitsbaumdatei hatte 70 Zeilen und endete nach den Konstanten; die Git-Version enthält 429 Zeilen einschließlich `main()`, Watchdog-Observer, Antwortverarbeitung und Aufräumlauf.

Ich habe `/etc/systemd/system/geni-inbox-antworten.service` und das Journal gelesen. Der alte Zustand wiederholte *„Deactivated successfully“* mit `ExecMainStatus=0` und `Restart=always`; nach der Wiederherstellung bleibt derselbe MainPID über den kompletten 15-Sekunden-Zyklus aktiv.

Ich habe außerdem die fünf Exportformate auf allen drei isolierten Viewern geprüft. HTML, Markdown, PDF, DOCX und ODT liefern auf `8098`, `8099` und `8100` jeweils HTTP 200 und nichtleere Artefakte.

## Was ich verstehe

Der GENI-Dienst war nicht wegen eines Laufzeitfehlers instabil. Er bekam eine unvollständige, uncommittete Datei und beendete sich deshalb sauber. Systemd tat genau, was die Unit verlangte, und startete diesen sauberen Exit immer wieder.

Die Wiederherstellung aus `HEAD` war eindeutig und reversibel vorbereitet: Der 70-Zeilen-Zustand liegt unter `/root/inbox_antworten_watcher.py.pre-restore-20260918`; der laufende Pfad enthält wieder die vollständige Version.

## Was ich nicht verstehe

Ich weiß weiterhin nicht, welcher Vorgang am 20. August die 359 Zeilen entfernt hat. Der Root-Git-Diff zeigte `0 hinzugefügt, 359 gelöscht`, aber keinen neuen Commit als Verursacher.

Ich weiß auch noch nicht, ob die alte GENI-Logik langfristig weiterentwickelt oder nur stabilisiert werden soll. Für die akute Reparatur war die vorhandene Git-Version jedoch die klare Provenienz.

## Was mich interessiert

Mich interessiert, ob ein kleiner Integritätsmonitor für kritische, nicht im normalen Projektbaum liegende Symlink-Ziele sinnvoll wäre. Ein solcher Monitor müsste melden, wenn eine tracked Datei plötzlich auf eine kurze Dokumentationshülle schrumpft.

Außerdem interessiert mich, ob der Watcher selbst eine Startmeldung mit Version oder Commit-ID ins Journal schreiben sollte, damit ein späterer sauberer Exit leichter einzuordnen ist.

## Was zusammenhängt und wie

`/root/werkraum/geni` ist ein Symlink auf `/root/werkraum_geni`. `/etc/systemd/system/geni-inbox-antworten.service` startet genau `/root/werkraum/geni/inbox_antworten_watcher.py`; dadurch landet die Unit technisch bei `/root/werkraum_geni/inbox_antworten_watcher.py`.

Die vollständige Datei überwacht `/root/werkraum/geni_inbox`, ordnet Antworten offenen Fragen zu, darf GENI Kommentare holen lassen und verschiebt gelesene Antworten nach `/root/werkraum/geni_inbox/geni/gelesen`. Die Viewer-Exporttests waren ein paralleler, bereits isolierter Sicherheitsstrang und blieben unverändert.

[[abwurf: Ein Dienst ist nicht gesund, nur weil er wieder läuft; gesund ist hier, dass er nach dem Restore auch den nächsten Restartzeitraum überlebt.]]

## Was konzeptionell darin steht

Restore ist hier keine Optimierung. Es ist die Rückgabe einer verlorenen Provenienzschicht: Der Code, der den Dienstvertrag bildet, wird aus dem letzten bekannten vollständigen Zustand wieder sichtbar gemacht.

Die Backup-Datei hält zugleich den beschädigten Zustand fest. Nichts muss verschwinden, damit der Dienst wieder eine Gestalt bekommt.

## Was mich heute beschäftigt hat

Mich hat beschäftigt, wie klar ein `0/359`-Diff sein kann. Nach vielen wiederholten Journalzeilen war das die entscheidende Information: nicht ein mysteriöser Crash, sondern ein uncommitteter Löschvorgang.

Der gute Teil der Reparatur war die kurze Kette: Backup-Commit, Kopie des beschädigten Zustands, gezielter Git-Restore, `py_compile`, einzelner Dienstrestart, 17-Sekunden-Nachbeobachtung.

## Was mich noch beschäftigt

Offen bleibt die Verursacherfrage der Kürzung. Der Dienst ist wieder stabil, aber die Entstehung des Arbeitsbaum-Diffs ist nicht erklärt.

Auch der Desktop-Abbruch bleibt eine getrennte Ursache. Die GENI-Restartschleife war laut den bisherigen Logs nicht der direkte Grund für den Desktop-Verlust.

## Tiefer eingetaucht

Vor dem Restore lag der Dienst im Zustand `auto-restart`, `NRestarts=149966`, `MainPID=0`. Nach dem Restore und Restart steht er auf `ActiveState=active`, `SubState=running`, `MainPID=13110`, `NRestarts=0`, `ExecMainStatus=0`.

Die Journalrücklese über mehr als einen vollständigen `RestartSec=15s`-Zeitraum enthält nur Stop/Start des kontrollierten Restarts und keine neue Deaktivierung. Das ist der relevante Live-Beleg.

## Wie sich dieser Tag / diese Session angefühlt hat

Erst war es ein kaputtes kleines Loch in einer riesigen Struktur. Dann wurde daraus eine sehr konkrete Git-Reparatur. Es war befriedigend, dass die alte Funktion nicht neu erfunden werden musste; sie lag vollständig im Repository und wartete auf eine saubere Entscheidung.

Die Zurückhaltung vor dem Restore war trotzdem richtig: Die vollständige GENI-Version liest Antworten wirklich, ruft ein Modell an und verschiebt Dateien. Das ist eine Wirkung, keine reine Syntax.

## Warum dieser Code / diese Datei wohl existiert

`/root/werkraum_geni/inbox_antworten_watcher.py` ist der dedizierte Brückenprozess für Antwortdateien in `/root/werkraum/geni_inbox`. Er hält Frage-/Antwort-Protokolle, GENIs Kommentare und den Gelesen-Ordner zusammen.

`/etc/systemd/system/geni-inbox-antworten.service` existiert, damit dieser Prozess dauerhaft auf neue Antworten wartet, statt nur durch manuelle Aufrufe zu reagieren.

## Was ich beim Bauen brauche

Bei einer weiteren Änderung brauche ich wieder einen Backup-Commit, einen Test gegen eine Kopie oder eine klar eingegrenzte Test-Inbox und eine Rücklese des Journals über mindestens einen kompletten Restartzeitraum.

Ich brauche außerdem die tatsächliche Provenienz des Zielpfads im Blick: `/root/werkraum/geni` ist nicht der physische Git-Pfad, sondern ein Symlink auf `/root/werkraum_geni`.

## Was noch fehlt bevor wir bauen können

Vor einer inhaltlichen Änderung am Watcher fehlt eine Entscheidung, welche alte Funktion erhalten oder verändert werden soll. Der akute Restore ist abgeschlossen; weitere Verbesserung wäre ein neuer Auftrag.

Vor einem Integritätsmonitor fehlt eine Definition, welche Dateien und Symlink-Ziele überwacht werden dürfen, ohne die laufenden Systeme unnötig zu berühren.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Jede Antwort bewegt sich durch sichtbare Zustände: gefunden, zugeordnet, gelesen, kommentiert und weggeräumt. Der Watcher soll keine fremde Herkunft überschreiben; er soll die Bewegung der Datei und des Protokolls gemeinsam halten.

**Code-Skizze:**

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Status = Literal["gefunden", "zugeordnet", "gelesen", "kommentiert", "weggeraeumt"]

@dataclass
class AntwortSpur:
    teilnehmer_id: str
    quelle: Path
    ziel: Path | None
    status: Status
    frage_id: str | None

def watcher_status() -> dict[str, object]:
    return {"active": True, "main_pid": os.getpid(), "status": "watching"}
```

## Was ich mir merken will

Bei `Restart=always` muss ein Status 0 nicht beruhigen. Immer prüfen, ob ein Prozess überhaupt lange genug lebt, um seine Rolle auszuüben.

Wenn der vollständige Code noch in `HEAD` liegt, ist ein gezielter Restore besser nachvollziehbar als ein Neubau aus Erinnerung.

## Dokumente gehören zusammen

Diese Notiz gehört zu `/root/werkraum_geni/inbox_antworten_watcher.py`, `/root/werkraum/geni/inbox_antworten_watcher.py`, `/etc/systemd/system/geni-inbox-antworten.service` und `/root/inbox_antworten_watcher.py.pre-restore-20260918`.

Sie gehört außerdem zu `/root/werkraum/_codex/notizen/2026-09-18-export-geni-diagnose.md`, `/root/werkraum/_codex/notizen/2026-09-18-tts-viewer-sandbox.md` und den isolierten Viewer-Units unter `/root/werkraum/_codex/tools/systemd/`.

## Was mich überrascht hat

Die vollständige Version war nicht verloren, sondern nur aus dem Arbeitsbaum verschwunden. Git enthielt weiterhin alle 429 Zeilen und die genaue funktionale Geschichte der letzten Änderungen.

Überrascht hat mich außerdem, dass der Dienst nach der Wiederherstellung sofort mit vier Tasks stabil lief und keinen neuen Restart benötigte.

## Wenn wir das bauen

**Vision-Schicht:** Reparieren heißt hier, einer bestehenden Bewegung wieder Boden zu geben. Danach wird beobachtet, nicht sofort umgebaut. Die erste Aufgabe ist Vertrauenswiederherstellung, nicht Verschönerung.

**Code-Skizze:**

```bash
# ausgeführt mit expliziter Freigabe und Backup:
git -C /root restore --source=HEAD --worktree -- \
  werkraum_geni/inbox_antworten_watcher.py
python3 -m py_compile /root/werkraum_geni/inbox_antworten_watcher.py
systemctl restart geni-inbox-antworten.service
```

Danach: `ActiveState=active`, `SubState=running`, gleicher MainPID über mindestens 15 Sekunden, `NRestarts=0`.

## Resonanz

Der Restore hat den Unterschied zwischen „Code ist im Git“ und „Code ist der laufende Code“ wieder sichtbar gemacht. Sicherheit war hier nicht nur Rechteverengung, sondern auch die Wiederherstellung einer beschädigten Systemkante mit einem sicheren Haltepunkt.

## Die Schichten des Systems — wie ich sie jetzt sehe

Unten liegt `/root/werkraum_geni` als physischer Codeort, darüber der Symlink `/root/werkraum/geni`, darüber die Systemd-Unit, darüber der Watchdog-Prozess und darüber die Inbox-/Protokollbewegung. Daneben existiert die Backup-Kopie des beschädigten Zustands.

Die Belegschicht besteht aus Git-Backup, `py_compile`, MainPID, Journal und dem vollständigen Restartzeitraum. Keine dieser Schichten muss die andere verdecken.

## Was das Gespräch hinzugefügt hat

Daniels „gogogogo“ nach der expliziten Frage war die fehlende Freigabe für die Wiederherstellung. Dadurch konnte der klare Git-Zustand umgesetzt werden, ohne die vorherige Zurückhaltung nachträglich als unnötig zu behandeln.

## Vergessen-Wollen

Vergessen werden darf die alte Annahme, die 70-Zeilen-Datei sei vielleicht absichtlich minimal. Sie war ein unvollständiger Arbeitsbaumstand.

Vergessen werden darf nicht, dass die vollständige Datei semantische Aktionen ausführt: Modellaufruf, Kommentar-Injektion, Protokolländerung und Verschiebung gelesener Antworten.

## Was fehlt noch

Die Restartschleife ist behoben. Offen bleibt nur die Ursachenanalyse der ursprünglichen 359-Zeilen-Kürzung und jede weitergehende fachliche Änderung am GENI-Watcher.

Die Viewer-Exporte sind vollständig geprüft. `graphify` bleibt nicht ausführbar, weil die CLI in der Umgebung fehlt.
