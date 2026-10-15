---
datum: 2026-08-14
betrifft: [browser-resume, crawlrecorder, flextrawurst, visueller-gegenbeweis]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe den gesicherten Arbeitsvertrag im sichtbaren Chromium fortgesetzt. Die Recorder-Seitenleiste zeigte 19 offene Chromium-Seiten, den vorhandenen Gutenberg-Crawl und eine vorbereitete Flextrawurst-Startseite. Der aktive Browserpfad blieb `virtuellerdesktop2` mit sichtbarem Chromium.

Ich habe zunächst den vorhandenen Gegencheck geklickt. Er öffnete keinen neuen sichtbaren Tab und erzeugte keinen sichtbaren Ergebnisstatus. Das wurde nicht als Erfolg gewertet.

Danach habe ich die vorbereitete Flextrawurst-Startseite über den sichtbaren Button `Crawl starten` gestartet. Der Lauf endete sichtbar mit 1 logischer Seite, 33 Chunks, 169237 HTML-Zeichen, Queue 0 und Status `complete`.

## Was ich verstehe

Der technische Crawl ist durchgelaufen. Die sichtbare Abnahme ist dadurch nicht automatisch bestanden. Die neue Crawl-ID lautet `crawl-2026-08-14T134609043Z-e24f0e29`.

## Was ich nicht verstehe

Der sichtbare Button `Offline-Abbild gegenprüfen` liefert im Panel weiterhin keinen Ergebnisstatus. Die späteren Bilder unterscheiden sich deutlich, aber die genaue Ursache dieser Differenz — Offline-Projektion, dynamischer Weltzustand oder sichtbarer Reload — ist aus dem Panel allein nicht sicher zu bestimmen.

## Was mich interessiert

Mich interessiert, warum der Gegencheck keinen sichtbaren Abschlussstatus schreibt und wie die offizielle Ansicht, die Offline-Ansicht und der wiederverwendete Crawl-Tab im Beleg eindeutig auseinandergehalten werden können.

## Was zusammenhängt und wie

Die Crawl-ID, die 300-ms-Screenshotfolge, die sichtbare Seitenleiste und die zwei Bildzustände gehören zusammen. `complete` belegt den Laufabschluss. Die Bilddifferenz verhindert eine grüne visuelle Abnahme. Der fehlende Panelstatus verhindert zusätzlich eine eindeutige automatische Klassifikation.

## Was konzeptionell darin steht

Ein vollständiger Lauf ist ein Rohbeleg. Erst wenn Original und Offline-Abbild sichtbar wiedererkannt werden und der Vergleich seine eigene Entscheidung ausgibt, wird daraus ein Gegenbeweis. Ein fehlender Status bleibt eine Lücke, keine Zustimmung.

## Was mich heute beschäftigt hat

Die Browser-only-Fortsetzung hat funktioniert, ohne den Server oder Dienste anzufassen. Der kleine Unterschied zwischen „Crawl fertig“ und „Seite bewiesen“ wurde im Bild sichtbar und nicht nur behauptet.

## Was mich noch beschäftigt

Der Wiederverwendungsmechanismus des physischen Crawl-Tabs kann Zustände überlagern. Das muss vor dem nächsten Code-Schritt als eigene Provenienzschicht behandelt werden.

## Tiefer eingetaucht

Die Screenshotfolge wurde während der sichtbaren Aktionen im 300-ms-Takt aufgenommen. Für den Flextrawurst-Lauf liegen 242 Bilder aus Crawl/Monitoring und weitere 32 Bilder aus dem Gegencheck unter `/tmp/codex-visible-resume-flextrawurst*`. Die letzte Bildprüfung zeigte eine abweichende Statusleiste und eine veränderte Text-/Layoutdarstellung.

## Wie sich dieser Tag / diese Session angefühlt hat

Ruhiger als der Absturz am Anfang, aber mit einem klaren roten Rand: Der Browser arbeitet, doch das Bild lässt sich noch nicht als identisch bezeichnen.

## Warum dieser Code / diese Datei wohl existiert

Der CrawlRecorder soll sichtbare Webseiten als navigierbares Offline-Abbild mit Herkunft und Gegenbeweis sichern. Diese Notiz hält fest, dass der technische Teil lief, die visuelle Abnahme aber offen blieb.

## Was ich beim Bauen brauche

Ich brauche eine sichtbare Zuordnung von Original-Tab, Crawl-Tab und Offline-Tab sowie einen Panelstatus, der `passed`, `failed` oder `unknown` ausgibt. Die 300-ms-Screenshots müssen denselben Zustand und dieselbe Phase markieren.

## Was noch fehlt bevor wir bauen können

Es fehlt die eindeutige Gegencheck-Ausgabe und eine kontrollierte Erklärung der Bilddifferenz. Die bestehende Reader-Fallback-Änderung darf erst danach live bewertet oder verändert werden.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Jeder Bildbeleg trägt seine Herkunft sichtbar mit: Original, Crawl, Offline, Zeitpunkt, Aktion und Entscheidung. Ein unbekannter Vergleich ist ein ehrlicher Zustand, kein Fehler, der grün gefärbt werden darf.

**Code-Skizze:**

```ts
type VisualProof = {
  crawlId: string;
  phase: "official" | "crawl" | "offline";
  screenshots: Array<{ at: number; path: string; intervalMs: 300 }>;
  comparison: "passed" | "failed" | "unknown";
  reason?: string;
};
```

## Was ich mir merken will

`complete` ist für den neuen Flextrawurst-Lauf belegt. Visuelle Gleichheit ist nicht belegt; der Gegencheck bleibt rot beziehungsweise unbekannt. Keine Abnahme behaupten.

## Dokumente gehören zusammen

Diese Notiz gehört zur Arbeitsvertragsnotiz, zur sichtbaren Chromium-Matrix, zum visuellen Gegenbeweis, zum Ownervertrag, zur CrawlRecorder-Implementierung und zum Report mit Crawl-ID `crawl-2026-08-14T134609043Z-e24f0e29`.

## Was mich überrascht hat

Der Lauf ging sichtbar von `scanning` bei 28 Prozent zu einem vollständigen 33-Chunk-Ergebnis, ohne dass ein neuer Browser-Tab nötig war. Der technische Abschluss war stabiler als der anschließende visuelle Vergleich.

## Wenn wir das bauen

**Vision-Schicht:** Die nächste Oberfläche soll dem Menschen direkt zeigen, ob er gerade das Original, den Crawl oder das Offline-Abbild sieht — und warum ein Vergleich grün, rot oder unbekannt ist.

**Code-Skizze:**

```python
def classify_visual_proof(original, offline, metadata):
    if metadata.phase != "offline":
        return "unknown", "phase-not-bound"
    score = compare_screenshots(original, offline)
    if score >= 0.88:
        return "passed", f"score={score:.4f}"
    return "failed", f"score={score:.4f}"
```

## Resonanz

[[abwurf: `complete` ist für den neuen Flextrawurst-Lauf belegt. Visuelle Gleichheit ist nicht belegt; der Gegencheck bleibt rot beziehungsweise unbekannt.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Die sichtbare UI meldet Laufzustand. Die Screenshotfolge meldet Erscheinung. Der Crawl-Report meldet Struktur und Artefakt. Git meldet Codeherkunft. Erst gemeinsam können sie eine Abnahme tragen; aktuell widerspricht die Bildschicht der grünen Kurzform `complete`.

## Was das Gespräch hinzugefügt hat

Daniels Browser-only-Vorgabe wurde praktisch umgesetzt: Sichtbares Chromium, sichtbare Buttons, 300-ms-Screenshotspur, kein Dienstneustart und kein versteckter API-Pfad für den Arbeitslauf.

## Vergessen-Wollen

Vergessen werden soll die Gleichung `complete = visuell bestanden`. Ebenso soll der fehlende Gegencheckstatus nicht stillschweigend als Erfolg behandelt werden.

## Was fehlt noch

Offen sind die eindeutige Gegencheck-Bindung, die Erklärung der Bilddifferenz und erst danach die Entscheidung, ob der nächste Schritt im Code oder erneut sichtbar im Browser liegt. Der aktuelle Browserzustand bleibt erhalten.
