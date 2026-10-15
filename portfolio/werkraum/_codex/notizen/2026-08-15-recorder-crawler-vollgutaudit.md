---
datum: 2026-08-15
betrifft: [browserrecorder, crawler, fetch, downloads, replica, provenance]
importable: false
autor: codex bei Daniels VPS
---

# Sessionnotiz: Recorder-/Crawler-Vollgutaudit

## Was ich gelesen habe

Ich habe die aktuelle Direkt-Laden-Erweiterung, den Queue-/Crawl-/PDF-/Workspace-Code, die Adapter, die Live-Tests und den vorhandenen Red-Team-Bericht gelesen. Besonders hängen geblieben ist der Unterschied zwischen einem formal grünen Test und einer wirklich bestätigten Datei.

Ich habe die VPS-Empfangsschicht in tools/action_history/browser_capture.py, den FastAPI-Empfänger, systemd und die Nginx-Weiterleitung gelesen. Der VPS schreibt atomare Primärdateien und prüft Browserartefakte besser als der direkte Client-ACK-Pfad.

Ich habe offizielle Chrome-, MDN-, OWASP- und Webrecorder-/SingleFile-/ArchiveBox-/Replay-Quellen verglichen. Fetch, Download-Completion und Replay sind eigene Beweisstufen.

## Was ich verstehe

Der Recorder besitzt sichtbare Snapshots, Text, HTML-Projektionen, Markdown, PDF und VPS-Dateien. Das ist ein brauchbarer Grundkörper, aber keine einzige Datei ist automatisch das Original oder ein vollständiges Replay.

Die kritischste konkrete Lücke ist AUD-001: Einzelversand kann bei HTTP 200 ohne vollständige Ergebnisse als zugestellt gelten. Daneben stehen versteckte Manifest-Fetches, unbegrenzte Universal-0-Limits, standardmäßiges Auto-Expand im manuellen Import, nicht bestätigte Downloads und XSS-Sinks.

## Was ich nicht verstehe

Nicht vollständig belegt sind reale Provider-Redesigns außerhalb der geprüften Fixtures, alle Crash-Zwischenzustände und jede lokale Downloaddatei bis zur finalen Byte-Rücklese.

Auch ist noch offen, ob ein echtes WARC/WACZ-Replikat gewollt ist oder ob zunächst nur ein ehrliches tabweises Bundle mit Text, sichtbarem HTML, Screenshot, PDF, Ressourcenmanifest und Ereignissen genügt.

## Was mich interessiert

Mich interessiert jetzt der kleinste Integritätsring, der die vorhandenen Funktionen wahr macht: ACK, Abort, Größen, Hash, Completion, Quelle und Grenze.

## Was zusammenhängt und wie

Fetch bestimmt, ob überhaupt zusätzliche Daten angefordert werden. Capture bestimmt, welche Projektion entsteht. Queue und ACK bestimmen, ob sie den VPS erreicht. Download-Completion bestimmt, ob die lokale Datei wirklich existiert. Replay bestimmt, ob ein späteres Öffnen noch dieselbe Welt zeigt.

## Was konzeptionell darin steht

Eine Projektion darf nützlich und schön sein, ohne sich als Original auszugeben. Ein Replica braucht Herkunft, Ressourcen, Zustände, Grenzen und überprüfbare Identität.

## Was mich heute beschäftigt hat

Dass ein leerer oder falscher ACK im direkten Weg schwerer wiegt als ein fehlender neuer Exportknopf.

## Was mich noch beschäftigt

Die Bedienung darf nicht wieder heimlich anfangen: manuelle Aufnahme muss manuell bleiben; automatisches Expandieren und Scrollen müssen eigene, sichtbare Modi sein.

## Tiefer eingetaucht

Der VPS-Pfad ist root-only und atomar auf Dateiebene, aber die Gesamtprojektion berührt mehrere Dateien und kann zwischen diesen Schritten auseinanderfallen.

## Wie sich dieser Tag / diese Session angefühlt hat

Nüchtern und etwas ernüchternd: viel funktioniert, aber die Wahrheit sitzt in den Übergängen und nicht im grünen Button.

## Warum dieser Code / diese Datei wohl existiert

Der Recorder soll sichtbare Arbeit festhalten, ohne aus Beobachtung still Navigation, Vollständigkeit oder Replay zu erfinden.

## Was ich beim Bauen brauche

Kleine Änderungen, einen Backup-Commit vor jedem Eingriff, eine sichtbare Einzelaktion, Rücklese aus Zustand und ein Protokoll mit offen/unbekannt.

## Was noch fehlt bevor wir bauen können

Vor dem nächsten Bau muss AUD-001 als P0 entschieden und als absichtlich fehlerhafter ACK-Test reproduziert werden. Danach erst die gemeinsamen Fetch-/Download-Verträge.

## Datenstruktur die ich mir vorstelle

Vision-Schicht: Ein tabweises Replikat ist eine ehrliche Kapsel aus Quelle, sichtbarer Projektion, Lesetext, Screenshot, Druckbild, Ressourcen, Ereignissen, Grenzen und späterem Wiedergabestatus. Keine Schicht darf eine andere verkleiden.

Code-Skizze: ReplicaManifest mit source, projections, resources, events, limits, replay und signatures; jede Datei mit artifact_id, source_id, bytes, sha256, producer, scope und status. Ein DownloadStatus führt started, complete, interrupted und read_back.

## Was ich mir merken will

HTTP 200 ist keine Zustellung. Download gestartet ist keine gespeicherte Datei. Scriptfreies HTML ist kein Replay. Grün ist nur so stark wie seine Assertion.

## Dokumente gehören zusammen

Der neue Vollaudit liegt unter _codex/berichte/browserrecorder/2026-08-15-recorder-crawler-vollgutaudit.md. Die vorhandenen Live-Abnahmen für tabweise Sammlung und 1:1-Quellvergleich bleiben die konkreten positiven Belege.

## Was mich überrascht hat

Der VPS prüft beim Browser-HTML/MD-Artefakt bereits dekodierte Bytes und SHA-256, während der direkte Eventpfad diese vorhandene Strenge nicht wiederverwendet.

## Wenn wir das bauen

Vision-Schicht: Der Operator soll jederzeit wissen, ob gerade nur der sichtbare Tab, ein geführter Verlauf, ein automatischer Crawl, eine Projektion oder ein echtes Ressourcen-Replay entsteht.

Code-Skizze: captureMode als Union, fetchWithTimeout mit AbortSignal, strictAck(response,batch), DownloadRegistry mit chrome.downloads.onChanged und ReplicaManifest als append-only Artefaktregister.

## Resonanz

Der Recorder wird nicht wahrer, indem er mehr sammelt. Er wird wahrer, indem er jede Grenze mit ablegt.

## Die Schichten des Systems — wie ich sie jetzt sehe

Auge und Klick liegen oben. DOM-/Text-/Screenshot-Projektion liegt darunter. Queue/ACK und VPS-Primärdateien liegen darunter. Markdown/PDF sind Leseschichten. Replay ist eine weitere, noch nicht fertig gebaute Schicht.

## Was das Gespräch hinzugefügt hat

Daniels Hinweis auf Fetch und Replica hat verhindert, dass Exportdateien nur als fertige Endprodukte betrachtet werden. Jetzt zählt auch, was unterwegs zusätzlich angefordert, gespeichert, bestätigt und später wiedergegeben wird.

## Vergessen-Wollen

Ich will nicht wieder „vollständig“ sagen, wenn nur ein Snapshot, ein HTTP-200 oder ein gestarteter Download belegt ist.

## Was fehlt noch

P0 ACK-Test und Fix, Download-Completion, zentrale Timeout-/Byteverträge, XSS-Bereinigung, Auto-Expand-Default aus, Universal-Limits und danach ein kleines Replica-Bundle.

