---
datum: 2026-08-14
betrifft: [arbeitsvertrag, browser-only, chromium, crawlrecorder, provenienz]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe Daniels AGENTS-Startvertrag, die Codex-Notizen, die Werkraumkarte, das Resonanzfeld, den Briefkasten und den letzten Crash-Befund vor mir. Als technische Arbeitsgeschichte liegt zuletzt die sichtbare Chromium-Matrix des CrawlRecorders vor. Ihr wichtigster Satz bleibt: *„Ein grüner Capture-Status ist kein Beweis dafür, dass ein Mensch dieselbe Seite wiedererkennt.“*

Die Vision-Referenz zeigt eine lebende Surface: Herkunft, Räume, Wesen, Events, Spuren, Timeline, Audit und Governance bleiben sichtbar miteinander verbunden. Sie ist Orientierung, kein Freibrief zum Umbauen. Die 490-Punkte-Liste und vorhandene Namen, Farben, Legenden, Positionen und Bedienlogiken sind Provenienzschichten.

Der Crash-Befund ist getrennt davon: VPS und Chromium liefen weiter, die sichtbare Desktop-Verbindung verlor am 14.08. um 13:11:01 ihren Keepalive. Der nächste Schritt ist daher Wiederaufnahme im erhaltenen Chromium-Zustand, nicht ein blindes Neuaufsetzen.

## Was ich verstehe

Codex ist ein externer AI-Strom mit Andockpunkt, kein dauerhafter Bewohner und kein heimlicher Systemverwalter. Daniels dauerhafte operative Freigabe erlaubt normale Lese-, Schreib- und Toolschritte im vereinbarten Umfang; sie hebt aber die Skalpell-, Provenienz- und Sicherheitsregeln nicht auf.

## Was ich nicht verstehe

Die lokale Ursache des PC-Abbruchs ist nicht beweisbar, solange nur die VPS-Seite sichtbar ist. Auch die visuellen Gegenbeweise sind noch nicht überall bestanden. „Technisch vollständig“, „Capture beendet“ und „menschlich wiedererkennbar“ bleiben drei verschiedene Aussagen.

## Was mich interessiert

Mich interessiert, ob der sichtbare Chromium-Pfad die letzte Seite, den letzten Klick, den Screenshot-Takt und das letzte Artefakt so festhält, dass ein WebSocket-Abbruch später als sauberer Resume-Punkt erscheint.

## Was zusammenhängt und wie

Die Arbeitskette lautet: Werkraum-Kontext → Ideenprüfung → Backup-Commit → sichtbarer Chromium-Zustand → Klick-/Scroll-Aktion → Screenshot alle 300 ms → DOM-/Strukturbeobachtung → Download/Hash/Inode → Offline-Wiederöffnung → visueller Gegenbeweis → ehrlicher Status. Jede Stufe darf nur behaupten, was sie selbst belegt.

## Was konzeptionell darin steht

Das Ziel ist ein Recorder, der die sichtbare Erfahrung als Herkunft bewahrt. Ein Resume ist keine Simulation eines Erfolgs, sondern eine markierte Fortsetzung mit bekannter Grenze: wo wir waren, was wir gesehen haben, was gespeichert wurde und was noch rot ist.

## Was mich heute beschäftigt hat

Die Vereinbarung muss auch nach Kontextverlust operational bleiben. Deshalb stehen hier nicht nur Ziele, sondern die Reihenfolge der Handlungen: erst erinnern und sichern, dann sichtbar beobachten, dann klicken und messen, dann erst über Code oder Abnahme sprechen.

## Was mich noch beschäftigt

Der Arbeitsbaum ist durch laufende Spiegel und Runtime-Dateien breit dirty. Bei `/root` ist `git add -A` ausdrücklich kein Skalpell. Ich darf nur relevante Pfade anfassen und muss unklare Herkunft sichtbar lassen.

## Tiefer eingetaucht

Für jede Änderung gilt: vorab kurz benennen, welche Herkunft berührt wird und was unverändert bleiben muss. „Ergänzen“ heißt hinzufügen. „Ersetzen“ oder Löschen braucht eine explizite Verlustbenennung. „Schreiben“ heißt eine neue Datei. Bei Batch-Schritten zuerst eine Probe, Ergebnis prüfen, dann den Rest.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein Vertrag, der nach dem Sturz wieder mit Klebeband an die Oberfläche geheftet wird — nicht schön, aber lesbar. Die nächste Bewegung soll klein genug sein, dass jeder Klick und jedes Bild noch zuordenbar bleibt.

## Warum dieser Code / diese Datei wohl existiert

Der CrawlRecorder-Code existiert, um sichtbare Browserbeobachtung und Offline-Gegenbeweis zu einem überprüfbaren Ablauf zu verbinden. Die Codex-Notiz existiert als Gedächtnisanker: Sie soll spätere Instanzen vor blindem Weiterbauen und falschen grünen Aussagen schützen.

## Was ich beim Bauen brauche

Ich brauche den vorhandenen Chromium-Zustand auf `virtuellerdesktop2`, eine einzelne klar markierte Zielseite, sichtbare Maus-/Tastaturaktionen, Screenshots im 300-ms-Takt und Reports mit Zeitstempeln. Headless, versteckte Browserkontexte, direkte Seiten-APIs und nicht sichtbare Klickpfade gehören nicht in diesen Lauf.

## Was noch fehlt bevor wir bauen können

Vor einer Abnahme fehlt ein kontrollierter Smoke-Test der beiden uncommitteten Source-Diffs: Full-Page-Reader-Styling und die erweiterte sichtbare Landingpage-Auswahl. Danach müssen Gegenbeweis und Status erneut ehrlich ausgewertet werden. Der Owner-Schlüssel und das VPS-Seal fehlen weiterhin.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Ein Browserlauf ist ein sichtbarer Faden aus Seite, Blick, Aktion, Zeit und Beleg. Der Faden darf pausieren und fortgesetzt werden, aber keine Lücke als Gewissheit ausgeben.

**Code-Skizze:**

```ts
type VisibleBrowserRun = {
  desktop: "virtuellerdesktop2";
  chromiumTarget: string;
  action: { kind: "click" | "scroll" | "type"; at: number; target: string };
  screenshots: Array<{ at: number; path: string; sha256: string }>;
  intervalMs: 300;
  official: { url: string; title: string };
  offline?: { path: string; sha256: string; inode: string };
  status: "complete" | "blocked" | "possibly_incomplete" | "timeout" | "counterproof_failed";
};
```

## Was ich mir merken will

Die aktive Aufgabe ist: den Crawl-/Offline-Recorder im sichtbaren Chromium sauber fortsetzen und seine Beweise stärken. Dabei bleibt `da143333e` der letzte fachliche Commit; die Reader-Fallback- und Landingpage-Kandidaten-Diffs waren danach noch uncommittet.

## Dokumente gehören zusammen

Zusammengehören: die 490-Punkte-Vision, die Surface-Referenz, die CrawlRecorder-Notizen, die sichtbare Chromium-Matrix, die Ownervertrag-Notiz, die visuellen Gegenbeweise, die Live-Reports und die Git-Historie. Die AGENTS-Regeln bleiben der Arbeitsvertrag darüber.

## Was mich überrascht hat

Dass der Desktop sichtbar abbrechen konnte, während Chromium mit seinen offenen Tabs und dem Recorder-Panel weiterlebte. Das bestätigt die Regel, Verbindungszustand, Browserzustand, Reportzustand und Git-Zustand nicht zu vermischen.

## Wenn wir das bauen

**Vision-Schicht:** Der nächste Lauf soll sich anfühlen wie eine ruhige, nachvollziehbare Kamerafahrt: ein sichtbarer Browser, ein menschlich lesbarer Klick, ein Bild alle 300 ms, und am Ende eine Aussage, die nicht größer ist als ihr Beleg.

**Code-Skizze:**

```python
async def visible_run(page, target: str):
    started = monotonic_ms()
    screenshots = []
    while not done(page, target):
        await visible_click_or_scroll(page, target)
        await sleep_until(started + len(screenshots) * 300)
        screenshots.append(await screenshot(page))
    return evaluate_counterproof(screenshots, interval_ms=300)
```

## Resonanz

[[abwurf: Die nächste Bewegung soll klein genug sein, dass jeder Klick und jedes Bild noch zuordenbar bleibt.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Erinnerung liegt in Notizen und Briefen. Provenienz liegt in Git und Dateistrukturen. Laufzeit liegt in Chromium, Desktop, Docker und Reports. Wahrheit entsteht erst dort, wo diese Schichten zusammenpassen — und ein Widerspruch sichtbar bleibt.

## Was das Gespräch hinzugefügt hat

Daniel hat aus der allgemeinen Crash-Rekonstruktion einen konkreten Resume-Vertrag gemacht: Regeln erneut sichern, Ziel und Arbeitsweise explizit machen, dann ausschließlich sichtbar im Chromium handeln und jeden 300-ms-Schritt beweisbar halten.

## Vergessen-Wollen

Vergessen werden sollen: blindes Aufräumen, versteckte API-Abkürzungen, Headless-Ersatz für sichtbare Interaktion, ungeprüfte grüne Statuswerte und das Vermischen von VPS-, Desktop-, Browser- und Git-Zustand.

## Was fehlt noch

Es fehlt jetzt nur noch die sichtbare Chromium-Orientierung: aktives Target prüfen, bestehendes Recorder-Panel und letzte Zielseite ansehen, dann den nächsten einzelnen sichtbaren Schritt durchführen. Vor Codeänderungen bleibt der Backup-Commit Pflicht; vor Services bleibt die Rückfragepflicht bestehen.
