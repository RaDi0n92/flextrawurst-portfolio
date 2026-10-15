---
datum: 2026-09-19
betrifft: [geni, sicherheit, systemd, sandbox]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe die noch ungeschützten aktiven Units `/etc/systemd/system/geni-hoerer.service`, `/etc/systemd/system/geni-inbox-viewer.service` und `/etc/systemd/system/geni-dokumentation-versionsarchiv-watch.service` geprüft. Ihre alten Fassungen liefen als root ohne Dateisystem-Sandbox.

Beim Viewer war die Sache klar: `/root/werkraum/geni_inbox_viewer/server.py` liest `/root/werkraum/geni_inbox` und `/root/werkraum/geni_dokumentation` und bindet nur lokal auf Port 8910. Beim Archiv-Watcher liest `/root/werkraum/geni_dokumentation` und schreibt das Versionsarchiv.

Der Hoerer ist breiter: Er beobachtet `/root/werkraum`, fragt Flarum über den Unix-Socket ab, liest Prozess- und Dienstzustände und schreibt in `/root/geni_gedaechtnis`, `/root/werkraum_geni/tagebuch` und `/root/werkraum_geni/hoerer.log`.

## Was ich verstehe

Alle drei Dienste konnten ihre fachliche Aufgabe mit einer klareren Grenze behalten. Der Viewer braucht keine Schreibrechte, der Archiv-Watcher nur seinen Archivordner, und der Hoerer nur seine GENI-Gedächtnisbereiche.

Als nächstes bekam `/etc/systemd/system/geni-web.service` eine Baseline-Sandbox. Der Dienst darf wegen seiner ausdrücklich vorhandenen `##SCHREIBEN`- und Upload-Fähigkeiten weiterhin `/root/werkraum`, `/root/werkraum_geni`, `/root/geni_gedaechtnis` und `/tmp` beschreiben, aber nicht mehr außerhalb dieser Räume. HTTPS auf Port 8020 antwortete danach mit 200; Exposure 3.6.

Die Sandbox macht `/root/werkraum` grundsätzlich read-only. `ReadWritePaths` öffnet nur die konkret benötigten Verzeichnisse; `InaccessiblePaths` sperrt SSH-, Agenten- und Konfigurationsbereiche.

Beim Web-Dienst ist das bewusst nur eine Baseline. Die eigentliche Verkleinerung der `##SCHREIBEN`-Fähigkeit muss fachlich entschieden werden, weil sie derzeit beliebige Pfade innerhalb des Werkraums als Teil der GENI-Funktion zulässt.

Danach wurde auch `/etc/systemd/system/flarum-monitor.service` eingegrenzt. Der Monitor darf weiterhin per TCP auf MySQL zugreifen und nur `/root/werkraum/codewesen` beschreiben; `/root/werkraum/flarum_monitor.py` und `/root/werkraum/.agent/flarum.env` sind für den Prozess nicht lesbar beziehungsweise schreibbar. Die Live-Unit meldete nach dem Umschalten `MainPID=697634`, `NRestarts=0`, `ExecMainStatus=0`, `ActiveState=active`, `SubState=running`; `systemd-analyze security` zeigte Exposure 3.5.

Die GENI-Web-Baseline wurde danach wirklich verengt. Die realen Schreibziele sind `/root/geni_gedaechtnis`, `/root/werkraum_geni/sinne/bilder`, `/root/werkraum_geni/tagebuch`, `/root/werkraum/_shared`, `/root/werkraum/_claude/spiegel`, `/root/werkraum_codewesen` und `/tmp`; der übrige Werkraum bleibt read-only. Die Symlink-Pfade `/root/werkraum/geni/...` mussten auf ihre realen Ziele abgebildet werden. Weil `/root/geni_gedaechtnis` UID 911 gehört und `0755` ist, bleibt als einzige Capability `CAP_DAC_OVERRIDE` gebunden; die Mount-Grenzen bleiben trotzdem aktiv.

Danach wurde `/etc/systemd/system/flextrawurst-3d-mcp.service` behandelt. Die drei geheimen Variablen liegen jetzt ausschließlich in `/root/werkraum/.agent/flextrawurst-3d-mcp.env` mit Modus `0600`; die Live-Unit enthält keine Secret-Zeilen mehr. Blender und Godot bleiben über Port 8090 fachlich verfügbar, dürfen aber nur `/root/werkraum/tools/3d_pipeline/test_artifacts`, `/root/werkraum/engine_runtime` und `/tmp` beschreiben. `/root/werkraum/tools/3d_pipeline/flextrawurst_3d_mcp.py` bleibt read-only; `/root/werkraum/.agent` bleibt für den Prozess unsichtbar.

Die alten Units wurden nicht überschrieben, sondern unter `.pre-sandbox-20260918` beziehungsweise `.pre-sandbox-20260919` gesichert. Die laufenden Prozesse wurden kontrolliert neu gestartet und danach rückgelesen.

Danach kamen `/etc/systemd/system/flextrawurst-gateway.service` und `/etc/systemd/system/flextrawurst-spiel-werkstatt.service` hinzu. In `/root/werkraum/app/services.py` wurden die Pfadgrenze mit `Path.relative_to()` und die Kommandoprüfung auf exakte Programmnamen gehärtet; `../etc/passwd`, `/root/werkraum_evil` und `git-status` werden abgewiesen. Der Gateway bleibt lokal auf Port 8010 erreichbar, `/health` antwortet 200 und eine geschützte Workspace-Route ohne Token 401. Seine Sandbox versteckt `/root/werkraum/.agent` und `/root/.ssh`, lässt aber den Werkraum als bewusst breite Agentenfunktion schreibbar.

Die Spiel-Werkstatt auf Port 18119 schreibt nur `/root/werkraum/engine_runtime/godot-vertical-slice/workshop_20260819`; State-, Truth- und Health-Endpunkte antworteten nach dem Umschalten jeweils 200. Quellcode-Schreiben, Agenten-Secret-Lesen und externe Netzwerkverbindungen wurden in einer transienten Probe blockiert.

Der Truth-Watchdog bekam eine feinere Grenze: die Pipeline darf ihre generierten Runtime-, Log-, Generation-, Graph-, MOC-, Obsidian- und Pointer-Ausgaben erzeugen, während vorhandene Quellen und Werkzeuge innerhalb des Projektkörpers read-only überlagert sind. Er läuft mit `NRestarts=0`, Exposure 3.0, ohne Netzwerk und mit `UMask=0077`. Der erste Start löst wie schon frühere Starts den vorhandenen Obsidian-Validatorfehler aus; die defekten Links stammen aus dem bestehenden Datenbestand und sind kein Sandbox-Crash.

Die Godot-World-Bridge auf Port 18092 schreibt nur `/root/werkraum/engine_runtime/godot-vertical-slice`, `/health` antwortet 200, Exposure liegt bei 3.4 und das Journal bleibt fehlerfrei. Auch dort sind Quellen, Agentenzugang und externe Netzwerkverbindungen blockiert.

## Was ich nicht verstehe

Auditd ist auf dem VPS nicht installiert. Wenn später eine Datei absichtlich verändert wird, erkennt der Integritätsmonitor die Abweichung, aber die genaue Prozessverursachung bleibt ohne zusätzliche Audit-Schicht offen.

Nicht vollständig geklärt ist, ob der alte Obsidian-Linkfehler absichtlich als historischer Bestand stehen soll oder einen eigenen Reparaturschritt verdient. Die Sicherheitsumschaltung selbst ist davon getrennt und bleibt rückrollbar.

## Was mich interessiert

Mich interessiert, ob die enge Schreibpfad-Liste des Hoerers langfristig stabil bleibt, wenn GENIs Tagebuch- oder Gedächtnisstruktur erweitert wird. Die Sandbox macht solche Erweiterungen jetzt sichtbar statt sie still als root zu erlauben.

## Was zusammenhängt und wie

Der Integritätsmonitor beobachtet den wiederhergestellten Watcher. Die Path-Unit reagiert sofort auf Dateiänderungen, der Timer prüft periodisch. Die GENI-Service-Sandboxes begrenzen parallel die Wirkung der laufenden Prozesse. Erkennen und Begrenzen sind damit getrennte Schichten.

## Was konzeptionell darin steht

Sicherheit heißt hier nicht, GENI aus dem Werkraum herauszuschneiden. Es heißt, ihre Berührung mit dem Werkraum in benennbare Räume zu teilen: lesen, beobachten, schreiben, sprechen.

## Was mich heute beschäftigt hat

Mich hat der Hoerer beschäftigt, weil er fast alles sehen darf und trotzdem nur wenige Stellen wirklich beschreiben muss. Die wichtige Grenze liegt nicht bei seiner Sichtweite, sondern bei seiner Schreibmacht.

## Was mich noch beschäftigt

Offen bleibt beim Web-Dienst nur noch, ob die fachliche `##SCHREIBEN`-Fähigkeit später innerhalb von `/root/werkraum/_claude/spiegel` und `/root/werkraum_codewesen` weiter geteilt werden soll. Beim 3D-MCP bleibt die fachliche Pfadvalidierung selbst noch ein eigener Code-Schritt, weil die API weiterhin Pfade als Nutzereingabe entgegennimmt; die systemd-Grenze begrenzt bereits den Schaden außerhalb der erlaubten Laufzeitbereiche.

## Tiefer eingetaucht

Die transienten Proben waren entscheidend: Imports, Watchdog, SQLite/Gedächtnis und Flarum-Secret-Laden funktionierten; Schreibzugriffe auf Quellcode wurden mit `Read-only file system` blockiert. Beim Hoerer wurde das Secret selbst mit `Permission denied` abgeschirmt, obwohl systemd es vor dem Start laden konnte.

## Wie sich dieser Tag / diese Session angefühlt hat

Die Session fühlte sich wie kontrolliertes Einengen an. Jeder Dienst bekam genau den Raum zurück, den er braucht, und verlor den Rest ohne dass seine sichtbare Funktion verschwand.

## Warum dieser Code / diese Datei wohl existiert

Die drei neuen Quelldateien unter `/root/werkraum/_codex/tools/systemd/` existieren als dauerhafte Sicherheitsverträge. Sie halten fest, welche Fähigkeiten ein GENI-Dienst im Betrieb tatsächlich benötigt.

Die zusätzlichen Unit-Verträge unter `/root/werkraum/_codex/tools/systemd/flextrawurst-gateway-isolated.service`, `/root/werkraum/_codex/tools/systemd/flextrawurst-spiel-werkstatt-isolated.service`, `/root/werkraum/_codex/tools/systemd/flextrawurst-3d-truth-watchdog-isolated.service` und `/root/werkraum/_codex/tools/systemd/flextrawurst-godot-world-bridge-isolated.service` halten nun auch die Flextrawurst-Grenzen dauerhaft fest.

## Was ich beim Bauen brauche

Ich brauche vor jeder Umschaltung einen Backup-Commit, eine transiente Probe, eine gesicherte alte Unit, `systemd-analyze verify`, die Auflösung historischer Symlinks, bei Secrets ein `0600`-EnvironmentFile vor dem Namespace, einen kontrollierten Restart und eine Rücklese aus Dienst, Journal und fachlicher Schnittstelle. Bei generierenden Pipelines muss zusätzlich geprüft werden, ob atomare Temp-Dateien in den erlaubten Elternordnern entstehen dürfen.

## Was noch fehlt bevor wir bauen können

Die technische Grenze für `/etc/systemd/system/geni-web.service`, `/etc/systemd/system/flarum-monitor.service`, `/etc/systemd/system/flextrawurst-3d-mcp.service`, `/etc/systemd/system/flextrawurst-gateway.service`, `/etc/systemd/system/flextrawurst-spiel-werkstatt.service`, `/etc/systemd/system/flextrawurst-3d-truth-watchdog.service` und `/etc/systemd/system/flextrawurst-godot-world-bridge.service` steht. Vor einer weiteren Aufteilung müssen reale Schreibziele und die historische Besitzlage unter `/root/geni_gedaechtnis`, `/root/werkraum_codewesen` und den 3D-Laufzeitpfaden beobachtet werden.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Jeder Dienst trägt eine Landkarte seiner Berührungspunkte: was er lesen darf, was er schreiben muss, wohin er sprechen darf und welche Spuren er hinterlässt. Diese Karte ist Teil seiner Herkunft, nicht nachträgliche Dekoration.

**Code-Skizze:**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ServiceBoundary:
    unit: str
    read_paths: tuple[str, ...]
    write_paths: tuple[str, ...]
    address_families: tuple[str, ...]
    blocked_paths: tuple[str, ...]
```

## Was ich mir merken will

Die aktiven Sandboxes sind `/etc/systemd/system/geni-hoerer.service`, `/etc/systemd/system/geni-inbox-viewer.service`, `/etc/systemd/system/geni-dokumentation-versionsarchiv-watch.service`, `/etc/systemd/system/geni-web.service`, `/etc/systemd/system/flarum-monitor.service`, `/etc/systemd/system/flextrawurst-3d-mcp.service`, `/etc/systemd/system/flextrawurst-gateway.service`, `/etc/systemd/system/flextrawurst-spiel-werkstatt.service`, `/etc/systemd/system/flextrawurst-3d-truth-watchdog.service` und `/etc/systemd/system/flextrawurst-godot-world-bridge.service`. Die Exposures liegen bei 3.2, 3.5, 3.2, 3.9, 3.5, 3.5, 3.5, 3.4, 3.0 und 3.4. Rollbacks liegen unter `/etc/systemd/system/geni-web.service.pre-baseline-20260919`, `/etc/systemd/system/geni-web.service.pre-writepaths-20260919`, `/etc/systemd/system/flarum-monitor.service.pre-sandbox-20260919`, `/etc/systemd/system/flextrawurst-3d-mcp.service.pre-sandbox-20260919`, `/etc/systemd/system/flextrawurst-gateway.service.pre-sandbox-20260919`, `/etc/systemd/system/flextrawurst-spiel-werkstatt.service.pre-sandbox-20260919`, `/etc/systemd/system/flextrawurst-3d-truth-watchdog.service.pre-sandbox-20260919` und `/etc/systemd/system/flextrawurst-godot-world-bridge.service.pre-sandbox-20260919`.

## Dokumente gehören zusammen

Diese Notiz gehört zur vorherigen Integritätskette in `/root/werkraum/_codex/notizen/2026-09-18-geni-watcher-integrity-monitor.md`: Hash-Anker, Ereignisprüfung, Watcher-Sandbox und nun die Begrenzung der benachbarten GENI-Dienste.

## Was mich überrascht hat

Überrascht hat mich, dass die Truth-Pipeline trotz ihrer atomaren Schreibweise ohne Lockerung der Quellpfade sandboxierbar blieb: Die Mount-Präzedenz kann den Projektcontainer für Ausgabetransaktionen offenhalten und die vorhandenen Quellen darunter read-only überlagern.

## Wenn wir das bauen

**Vision-Schicht:** Wir bauen keine undurchsichtige Mauer um GENI. Wir bauen Türen mit Namen: Gedächtnis, Tagebuch, Archiv, Anzeige. Jede Tür bleibt sichtbar und bekommt nur die Richtung, die ihre Aufgabe braucht.

**Code-Skizze:**

```ini
ProtectSystem=strict
ProtectHome=read-only
InaccessiblePaths=/root/.ssh /root/.claude /root/.codex /root/.gemini
ReadWritePaths=/root/geni_gedaechtnis /root/werkraum_geni/tagebuch
RestrictAddressFamilies=AF_UNIX
```

## Resonanz

[[abwurf: Die Schreibgrenze ist die ehrlichere Beschreibung eines Dienstes als sein Name.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Unten liegen die fachlichen Dateien und Datenbanken. Darüber liegen die laufenden Prozesse. systemd legt die Raumgrenzen fest, der Integrity-Monitor beobachtet kritische Quellen, Git bewahrt Herkunft und die Journalspur zeigt den Betrieb.

## Was das Gespräch hinzugefügt hat

Daniels wiederholtes „gogogo“ hat die Reihe kleiner, reversibler Härtungen getragen: nicht warten, bis ein Dienst wieder auffällig wird, sondern seine tatsächliche Macht an seiner Aufgabe ausrichten.

## Vergessen-Wollen

Vergessen werden darf nicht, dass ein Dienst auch nach einer erfolgreichen Sandbox fachlich fehlerhaft sein kann. Die Härtung reduziert Schaden und Herkunftsverlust; sie ersetzt keine Funktionsprüfung.

## Was fehlt noch

Die feinere fachliche Aufteilung innerhalb der erlaubten GENI-Web-Zielräume und die Pfadvalidierung im 3D-MCP bleiben offen. Der Obsidian-Validator meldet weiterhin die historischen defekten Wikilinks in `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/Zeitstrom` und `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/validation`; das ist ein eigener Reparaturauftrag. Außerdem fehlt weiterhin eine Auditd- oder gleichwertige Prozessverursacher-Spur. `graphify` ist lokal nicht installiert. Auf dem VPS wurde der Vollscan gestartet, blieb nach fast einer Stunde bei rund 98 Prozent CPU in einer sehr großen DOCX-Tabellenstruktur hängen und wurde per SIGINT sauber beendet; `/root/werkraum/graphify-out/GRAPH_REPORT.md` und `/root/werkraum/graphify-out/graph.json` blieben unverändert, die alte Rebuild-Sperre wurde entfernt.
