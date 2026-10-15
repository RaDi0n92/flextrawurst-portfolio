---
datum: 2026-09-18
betrifft: [live-viewer, export, geni, systemd, sicherheit]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe die drei laufenden Viewer auf `8098`, `8099` und `8100` gegen `/export` geprüft. Jede Kombination aus `html`, `md`, `pdf`, `docx` und `odt` lieferte HTTP 200 und ein nichtleeres Artefakt. Die Antwortgrößen lagen bei den Testdaten zwischen 79 und 16650 Bytes.

Ich habe danach `/etc/systemd/system/geni-inbox-antworten.service`, das Journal und `/root/werkraum/geni/inbox_antworten_watcher.py` gelesen. Das Journal sagt wiederholt *„Deactivated successfully“*, während die Unit `Restart=always` verwendet. Das ist kein Absturz mit Stacktrace, sondern ein sauberer Prozessausgang.

Im Root-Git zeigt der Diff für `/root/werkraum_geni/inbox_antworten_watcher.py` exakt `0 additions, 359 deletions`. `HEAD` enthält 429 Zeilen mit `main()`, `Observer`, Antwortverarbeitung und Aufräumlauf; der aktuelle Arbeitsbaum enthält nur 70 Zeilen Dokumentation und Konstanten.

## Was ich verstehe

Die Viewer-Sandbox hat die seltenen Exportpfade nicht abgeschnitten. HTML, Markdown, PDF, DOCX und ODT funktionieren auf allen drei Prozessen weiter. Die privaten Temp-Dateien und Kindprozesse von Playwright/Pandoc sind damit für den kleinen Testfall kompatibel.

Der GENI-Restartsturm ist vollständig erklärt: `/root/werkraum/geni` ist ein Symlink auf `/root/werkraum_geni`; dort liegt die gekürzte Datei. Python kompiliert sie und beendet sich sofort mit Status 0, weil nach den Konstanten kein ausführbarer Code folgt. Systemd startet sie alle 15 Sekunden erneut und steht bei ungefähr 150000 Restarts.

## Was ich nicht verstehe

Ich weiß nicht, welcher Prozess die 359 Zeilen am 20. August aus dem Arbeitsbaum entfernt hat. Der aktuelle Root-Git-Diff nennt keinen Commit als Ursache, sondern zeigt eine uncommittete Arbeitsbaumänderung.

Ich weiß auch noch nicht, ob Daniels gewünschter GENI-Vertrag seit dem letzten vollständigen Commit unverändert gilt. Die alte Version ruft beim Lesen einer Antwort über `hauhau_client` Kommentare ab und verschiebt gelesene Dateien; das ist funktional bedeutsam und nicht bloß ein harmloser Watchdog.

## Was mich interessiert

Mich interessiert die Herkunft dieser uncommitteten Kürzung: Audit-Tool, fehlgeschlagener Edit, Spiegelprozess oder manuelle Aktion. Die mtime und der Diff sind bekannt, der Verursacher noch nicht.

Außerdem interessiert mich, ob die vollständige Version vor einer Wiederherstellung erst in einem isolierten Einmal-Testlauf gegen eine Kopie von `/root/werkraum/geni_inbox` geprüft werden kann.

## Was zusammenhängt und wie

Die Viewer-Exports hängen an `/root/.claude/live_export.py`, werden aber über die drei isolierten Dienste ausgeführt. Der Test bestätigt, dass die Sicherheitsgrenze mit den echten Temp- und Subprozesspfaden vereinbar ist.

Der GENI-Dienst hängt dagegen an `/root/werkraum_geni/inbox_antworten_watcher.py` und `/root/werkraum/geni_inbox`. Der fehlende Code betrifft nicht die Viewer-Sandbox; er ist ein separater, historischer Arbeitsbaumverlust.

[[abwurf: Ein sauberer Exit ist hier kein gesunder Dienst, sondern ein fehlender Hauptteil, den systemd höflich immer wieder neu vermisst.]]

## Was konzeptionell darin steht

Ein Sicherheitsresume darf eine sichtbare Altlast diagnostizieren, ohne sie ungefragt zu reaktivieren. Die Provenienz des GENI-Codes, seine laufende Wirkung und die Grenze zwischen Reparatur und Sicherheitsfix müssen getrennt bleiben.

Die Exportprüfung zeigt die Gegenbewegung: Ein System kann stark eingeschränkt werden, wenn seine realen Pfade vorher bekannt sind. Beim GENI-Watcher ist der relevante Pfad nicht nur Datei-I/O, sondern auch die semantische Aktion „GENI liest und kommentiert“.

## Was mich heute beschäftigt hat

Mich hat beschäftigt, dass die beste Diagnose hier aus zwei unscheinbaren Fakten kam: `ExecMainStatus=0` und `0/359` im Git-Diff. Zusammen erklären sie den gesamten Restartsturm besser als tausend Journalzeilen.

Gut war auch, dass die Exportprüfung nicht nur den einfachen HTML-Weg nahm. PDF, DOCX und ODT starten echte Zusatzprozesse und sind deshalb genau die Stellen, an denen eine Sandbox gern unbemerkt bricht.

## Was mich noch beschäftigt

Offen ist die Entscheidung, ob die vollständige Version aus `/root/werkraum_geni` wiederhergestellt und der Dienst danach getestet werden darf. Ohne diese Entscheidung würde ich die geschützte GENI-Schicht still verändern.

Der Desktop-Abbruch bleibt davon unabhängig; die laufenden Sicherheitsdienste sind nicht durch den GENI-Restartsturm erklärt.

## Tiefer eingetaucht

Der vollständige Git-Stand enthält Funktionen wie `_protokoll_laden`, `_protokoll_speichern`, `_zuordnen`, `_antwort_verarbeiten`, `_kommentare_holen`, `gelesene_wegraeumen` und `main`. Besonders wichtig ist der `Observer`, der `/root/werkraum/geni_inbox` rekursiv überwacht.

Die gekürzte Datei enthält noch `INBOX_VAULT`, `FRAGEN_DIR`, `GELESEN_VON_GENI`, `RUHEZEIT_SEKUNDEN`, `AUFRAEUM_TAKT_SEKUNDEN` und `ERLAUBNIS`, aber keine Funktion, die diese Struktur benutzt. Sie ist also kein absichtlich minimalistischer Watcher, sondern ein halber Arbeitsbaum.

## Wie sich dieser Tag / diese Session angefühlt hat

Der Exportteil war erfreulich nüchtern: 15 Durchläufe, 15 Treffer. Der GENI-Teil fühlte sich dagegen wie das Auffinden einer offenen Naht an, die schon lange im Hintergrund Systemd-Rauschen produziert.

Die richtige Bewegung war diesmal nicht „sofort reparieren“, sondern den genauen Wiederherstellungspunkt aus Git festhalten und die semantische Wirkung der alten Datei ernst nehmen.

## Warum dieser Code / diese Datei wohl existiert

`/root/werkraum_geni/inbox_antworten_watcher.py` existiert als dauerhafter Brückenprozess zwischen Antwortdateien, Frage-/Antwort-Protokollen und GENIs Lese-/Kommentarbewegung. Der Systemd-Dienst `/etc/systemd/system/geni-inbox-antworten.service` soll diesen Prozess dauerhaft am Leben halten.

Die Viewer-Exportfunktionen existieren, damit ausgewählte Live-Einträge in fünf Offline-Formate ausgegeben werden können. Der heutige Test bestätigt diese Funktion nach der Isolation.

## Was ich beim Bauen brauche

Für den GENI-Watcher brauche ich vor jeder Wiederherstellung einen separaten Backup-Commit, eine explizite Freigabe für `/root/werkraum/geni/`, einen isolierten Test gegen eine Kopie und erst danach einen kontrollierten Dienststart.

Für die Exportpfade brauche ich die beibehaltene Sandbox, private Temp-Dateien und Tests mit allen fünf Formaten.

## Was noch fehlt bevor wir bauen können

Es fehlt Daniels klare Entscheidung, ob die 429-Zeilen-Version aus `HEAD` wiederhergestellt werden soll. Ohne sie bleibt die Diagnose abgeschlossen, aber der Dienst absichtlich unberührt.

Es fehlt außerdem ein Testplan für GENIs externe Modellaufrufe und die Antwortdatei-Verschiebung, damit eine Wiederherstellung nicht ungeprüft alte Nebenwirkungen neu aktiviert.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Der GENI-Watcher ist ein Vertrag zwischen einer eingehenden Antwort, einer offenen Frage, GENIs eigener Lesespur und einem späteren Aufräumen. Jede Bewegung muss nachvollziehbar bleiben: entdeckt, zugeordnet, gelesen, kommentiert, verschoben.

**Code-Skizze:**

```python
@dataclass
class AntwortEreignis:
    teilnehmer_id: str
    antwort_pfad: Path
    frage_id: str | None
    status: Literal["neu", "zugeordnet", "gelesen", "verschoben"]

def main() -> None:
    observer = Observer()
    observer.schedule(AntwortHoerer(), str(INBOX_VAULT), recursive=True)
    observer.start()
    while True:
        time.sleep(2)
        gelesene_wegraeumen()
```

## Was ich mir merken will

`ExecMainStatus=0` kann bei `Restart=always` einen dauerhaften Defekt verstecken. Immer den Prozessinhalt und den Git-Diff danebenlegen.

Die vollständige Wiederherstellung liegt in `HEAD` des Root-Repositories; der aktuelle Zustand ist nicht committed. Nichts davon wurde in dieser Session verändert.

## Dokumente gehören zusammen

Diese Notiz gehört zu `/etc/systemd/system/geni-inbox-antworten.service`, `/root/werkraum/geni/inbox_antworten_watcher.py`, `/root/werkraum_geni/inbox_antworten_watcher.py`, `/root/werkraum/_codex/tools/systemd/claude-live-isolated.service`, `/root/werkraum/_codex/tools/systemd/codex-live-isolated.service`, `/root/werkraum/_codex/tools/systemd/gemini-live-isolated.service` und `/root/.claude/live_export.py`.

Sie gehört außerdem zu `/root/werkraum/_codex/notizen/2026-09-18-tts-viewer-sandbox.md` und `/root/werkraum/_codex/notizen/2026-09-18-live-viewer-toolbox-isolation.md`.

## Was mich überrascht hat

Die 429-Zeilen-Version ist in `HEAD` vollständig vorhanden, obwohl der laufende Arbeitsbaum seit dem 20. August nur 70 Zeilen zeigt. Das macht die Wiederherstellung technisch klar, aber die Freigabeentscheidung nicht überflüssig.

Überrascht hat mich außerdem, dass alle drei Viewer trotz der Sandbox auch PDF, DOCX und ODT erfolgreich erzeugen konnten.

## Wenn wir das bauen

**Vision-Schicht:** Erst die beschädigte Herkunft sichern, dann die alte Bewegung in einem abgetrennten Raum beobachten, erst danach wieder an den lebenden GENI-Dienst anschließen. Reparatur heißt hier nicht, die alte Bedeutung wegzuoptimieren.

**Code-Skizze:**

```bash
# erst nach expliziter Freigabe und Backup
git -C /root show HEAD:werkraum_geni/inbox_antworten_watcher.py \
  > /root/werkraum_geni/inbox_antworten_watcher.py
python3 -m py_compile /root/werkraum_geni/inbox_antworten_watcher.py
systemctl restart geni-inbox-antworten.service
```

Der letzte Block ist bewusst nur eine Skizze; er wurde nicht ausgeführt.

## Resonanz

Die Exporttests zeigen: Die neue Sicherheitsform trägt bis in die praktischen Endpunkte. Der GENI-Befund zeigt: Nicht jeder offene Dienst darf im selben Sicherheitsatem repariert werden. Herkunft und Wirkung müssen vor der Handbewegung sichtbar sein.

## Die Schichten des Systems — wie ich sie jetzt sehe

Oben stehen die Viewer-Endpunkte und ihre Offline-Exporte. Darunter liegen Temp-/Subprozesse. Separat liegt der GENI-Watcher mit Dateiüberwachung, Protokollmutation, Modellaufruf und Aufräumen. Systemd hält beide Arten von Dienst am Leben, aber nur der GENI-Dienst hat aktuell die beschädigte Arbeitsbaumquelle.

Die Belegschicht besteht aus 15 erfolgreichen Exportantworten, dem sauberen Git-Diff `0/359`, dem Journal mit Status 0 und dem `HEAD`-Inhalt mit 429 Zeilen.

## Was das Gespräch hinzugefügt hat

Daniels „gogogogogo“ hat den nächsten offenen Punkt freigelegt, aber nicht automatisch die semantische Freigabe für GENI ersetzt. Die Session ist jetzt an einer klaren Kante: Viewer-Export abgeschlossen, GENI-Reparatur vorbereitet, aber bewusst nicht ausgeführt.

## Vergessen-Wollen

Vergessen werden darf die falsche Annahme, ein sauberer Exit bedeute einen funktionierenden Watcher. Vergessen werden darf auch nicht, dass ein Restore die GENI-Kommentier- und Verschiebungslogik wieder aktiviert.

## Was fehlt noch

Es fehlt nur eine Richtungsentscheidung für den GENI-Strang: vollständige Version aus `/root`-Git wiederherstellen und kontrolliert testen, oder den Dienst zunächst deaktiviert lassen und nur eine neue Reparatur planen.

`graphify update .` bleibt weiterhin nicht möglich, weil die CLI fehlt. Die Exportpfade sind geprüft; an `/root/werkraum/geni/` wurde nichts verändert.
