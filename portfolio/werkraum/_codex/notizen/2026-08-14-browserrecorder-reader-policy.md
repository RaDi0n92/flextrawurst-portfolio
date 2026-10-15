---
datum: 2026-08-14
betrifft: [browserrecorder, chromium, flextrawurst, reader-policy, sichtbarer-crawl]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also habe ich diese Datei selbst als Arbeitsgedächtnis geschrieben.

## Was ich gelesen habe

Ich habe den wiederhergestellten Chromium-Zustand auf `virtuellerdesktop2` erneut sichtbar geprüft. Der Recorder lag als Extension-Seite vorne; der gespeicherte alte Crawl zeigte `https://flextrawurst.de/`, war technisch abgeschlossen und hatte zuvor eine bestandene Strukturprüfung.

Die Startvorschau zeigte zunächst die alte vollständige Sichtseite. Nach dem sichtbaren Aktualisieren war die aktuelle Policy ausdrücklich `sichtbarer Artikel-/Hauptinhalt`; die Assetdarstellung war als Manifest ohne Einbettung ausgewiesen. Das war ein neuer Prüfpunkt, nicht rückwirkend eine Änderung am alten Crawl.

Die UI selbst sagt weiterhin klar: *„Visueller Originalabgleich: nicht ausgeführt.“* Dieser Satz bleibt wichtiger als ein bequemes grünes `complete`.

## Was ich verstehe

Der neue Lauf wurde aus der sichtbaren Reader-Policy gestartet und auf `https://flextrawurst.de/` ausgeführt. Er endete mit fünf logischen Seiten, Queue null und 228978 HTML-Zeichen. Die anschließende sichtbare Struktur-/Vertragsprüfung bestand für fünf von fünf Seiten ohne dokumentierte Warnung.

## Was ich nicht verstehe

Der strenge visuelle Originalabgleich ist weiterhin nicht Teil des Panelbuttons. Der Offline-Crawl-Export erzeugt einen Blob und meldet 293576 Zeichen, aber Chromiums eigene Downloadansicht blieb leer, weil die CDP-Verbindung den Blob abfing und keinen dauerhaften Dateieintrag erzeugte.

## Was mich interessiert

Mich interessiert, ob der nächste Gegenbeweis Original-Tab, physischem Crawl-Tab und Offline-Wiedergabe so bindet, dass fünf Seiten nicht nur strukturell vollständig, sondern auch visuell wiedererkennbar sind.

## Was zusammenhängt und wie

Start-Preview, Crawl-ID, sichtbare Seitenfolge, Strukturprüfung, Exportstatus und Screenshots gehören zu diesem Lauf. Der Crawlstatus `bereit` beweist Vollständigkeit des technischen Laufs; die Prüfzeile beweist Vertrag und Struktur; keine dieser Aussagen beweist visuelle Gleichheit.

## Was konzeptionell darin steht

Die Reader-Policy ist eine neue Beobachtungsentscheidung: Sie versucht, den menschlich relevanten Hauptinhalt zu bewahren, ohne verstecktes DOM oder nicht sichtbare Geheimnisse einzusammeln. Der Nachweis muss genau diese Entscheidung sichtbar mittragen.

## Was mich heute beschäftigt hat

Der Browser war mehrfach technisch lebendig, während der sichtbare Fokus verloren ging. Erst das explizite Nach-vorne-Bringen des Recorder-Tabs, die DOM-Prüfung und die Bildfolge haben wieder einen belastbaren Faden erzeugt.

## Was mich noch beschäftigt

Die Browser-Downloadstrecke ist noch nicht als persistenter Beleg geschlossen. Ein Blob-Download und eine Statusmeldung dürfen nicht mit einer dauerhaft wiederöffbaren Datei verwechselt werden.

## Tiefer eingetaucht

Der neue Crawl erhielt die ID `crawl-2026-08-14T214708584Z-e24f0e29`. Er lief ungefähr 95 Sekunden und wurde mit 645 Playwright-Screenshots im 100-ms-Takt überwacht. Die Gegenprüfung lief danach mit weiteren 27 Bildern; der Export mit 21 Bildern.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein Browser, der nicht verschwunden war, aber immer wieder seine sichtbare Bindung wechselte. Der ruhige Fortschritt kam erst zurück, als jede Aktion unmittelbar mit UI-Text, DOM und Bild bestätigt wurde.

## Warum dieser Code / diese Datei wohl existiert

Der Recorder-Code existiert, um sichtbare Seiten in überprüfbare Offline-Artefakte zu überführen. Diese Notiz existiert, damit der neue Reader-Policy-Lauf samt Grenze des visuellen Beweises nach einem weiteren Abbruch nicht als vollständig abgenommen erinnert wird.

## Was ich beim Bauen brauche

Ich brauche eine dauerhafte, sichtbare Zuordnung aus Browserseite, Crawl-ID, Policy, Screenshotfolge und Exportdatei. Für Downloadartefakte braucht es entweder den echten Chromium-Downloadpfad oder eine explizite VPS-Speicherung mit Hash und Wiederöffnung.

## Was noch fehlt bevor wir bauen können

Es fehlt weiterhin der echte visuelle Originalabgleich. Außerdem ist zu klären, ob die fünf Seiten unter der Reader-Policy die gewünschte menschliche Wiedererkennbarkeit tragen; die 0 Bytes inline sind bewusst als Assetgrenze sichtbar und kein stiller Erfolg.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Ein sichtbarer Lauf ist ein Faden aus Policy, Seite, Blick, Aktion, Zeit und Beleg. Die neue Reader-Policy darf die Seite fokussieren, aber nicht die Herkunft des Bildes verschleiern.

**Code-Skizze:**

```ts
type ReaderPolicyRun = {
  crawlId: string;
  origin: string;
  projection: "reader_main_sanitized" | "full_visible_page";
  logicalPages: number;
  htmlChars: number;
  assets: { inlineBytes: number; budgetBytes: number; mode: "manifest" | "inline" };
  structure: "passed" | "failed" | "unknown";
  visual: "passed" | "failed" | "not_run";
  screenshots: Array<{ path: string; intervalMs: 100; phase: string }>;
};
```

## Was ich mir merken will

Neue Crawl-ID: `crawl-2026-08-14T214708584Z-e24f0e29`. Ergebnis: fünf Seiten, 228978 HTML-Zeichen, Strukturprüfung 5/5 bestanden, Export 293576 Zeichen, visueller Originalabgleich nicht ausgeführt.

## Dokumente gehören zusammen

Diese Spur gehört zur Arbeitsvertragsnotiz, zur sichtbaren Chromium-Matrix, zur CrawlRecorder-Implementierung, zum Commit `abbfceb82`, zum Panelstatus und zu den Live-Reports mit ihren strengen visuellen Grenzen.

## Was mich überrascht hat

Die Änderung der Startvorschau von vollständiger sichtbarer Seite zu sichtbarem Artikel-/Hauptinhalt führte im nächsten Lauf zu fünf logischen Seiten statt einer. Das ist ein beobachteter Unterschied, aber noch keine Aussage über bessere visuelle Qualität.

## Wenn wir das bauen

**Vision-Schicht:** Der nächste Schritt soll nicht einfach mehr Seiten sammeln, sondern Original und Offlinebild so nebeneinander führen, dass ein Mensch die gleiche Welt wiedererkennt und zugleich sieht, welche Teile absichtlich nur als Assetmanifest vorliegen.

**Code-Skizze:**

```python
def classify_run(run: ReaderPolicyRun, visual_result: dict) -> str:
    if run.structure != "passed":
        return "counterproof_failed"
    if visual_result.get("status") != "passed":
        return "visual_counterproof_pending"
    return "complete"
```

## Resonanz

[[abwurf: Ein technischer Abschluss darf die fehlende visuelle Wiederöffnung nicht übertönen.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Oben liegt der sichtbare Chromium-Tab. Darunter liegen Extension-DOM, Crawlstatus und Policy. Daneben liegen Screenshots, Export-Blob, Downloadpfad und Git-Herkunft. Erst wenn diese Schichten zusammenpassen, darf aus `complete` eine visuelle Abnahme werden.

## Was das Gespräch hinzugefügt hat

Daniels wiederholtes „ich sehe nichts“ hat den operativen Maßstab geschärft: Eine Aktion zählt erst, wenn der sichtbare Browser vorne ist, die Aktion beobachtet wurde und der neue Zustand unmittelbar erneut geprüft wurde.

## Vergessen-Wollen

Vergessen werden soll, dass ein abgefangener Blob bereits eine wiederöffbare Datei sei. Ebenso soll die Reader-Policy nicht nachträglich als Beweis für visuelle Gleichheit ausgegeben werden.

## Was fehlt noch

Offen sind der echte Original-/Offline-Gegenbeweis für den Fünf-Seiten-Lauf, die persistente Export-Wiederöffnung und die Entscheidung, ob die Reader-Policy fachlich trägt. Der Chromium-Zustand bleibt aktuell vorne beim Recorder und wurde nicht beendet.
