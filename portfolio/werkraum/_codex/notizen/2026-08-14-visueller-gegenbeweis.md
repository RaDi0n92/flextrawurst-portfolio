---
datum: 2026-08-14
autor: codex bei Daniels VPS
importable: false
---

## Was ich gelesen habe

Ich habe den bisherigen sichtbaren Crawl-Test gelesen, der Screenshots zwar alle 300 ms schrieb, sie aber nur als Dateien und Hashes ablegte. Der entscheidende alte Satz war sinngemäß: „Pixel identity is not claimed“ — damit war ein Bildbeleg vorhanden, aber kein Bildgegenbeweis.

Ich habe den Rotationslauf gelesen: `complete` wurde vorher aus Capture, Download, Inode und Text/Comparator zusammengesetzt. Beim echten Anthropic-Lauf sah ich dann den Unterschied: Newsroom erreichte strukturell 0,9128, Constitution nur 0,5846; beide mussten getrennt bleiben.

Ich habe die tatsächlichen Wikipedia-Raster geöffnet. Das Original zeigt helle Wikipedia-Navigation, Logo, Infobox und Medien. Die Offlineansicht zeigt die dunkle Flextrawurst-Lesefläche und `Offline-Mediengrenze`. Der rote Diff ist kein Schönheitsfehler, sondern der Beweis, dass Textmenge allein keine visuelle 1:1-Aussage trägt.

## Was ich verstehe

`complete` beschreibt die Beobachtung des Crawl-Endes. Es sagt nicht, dass der heruntergeladene Aufbau dem Original visuell entspricht. Dafür braucht es eine zweite, strengere Statusschicht.

Der neue Gegenbeweis rendert die aufgenommenen `page.html`-Bytes in gleicher Viewportgröße und vergleicht Original und Offline bei Scrollverhältnissen 0, 0.5 und 1. Er speichert Quellbild, Offlinebild, Diff, SHA, RMSE, MAE, pHash und normierte DOM-Geometrie.

## Was ich nicht verstehe

Noch nicht abschließend geklärt ist, wie stark dynamische Werbung, Fonts, externe Bilder, Cookie-Zustände und Zeitstempel vor einem Vergleich normalisiert werden dürfen, ohne die Herkunft der Seite zu verfälschen.

Die isolierte Atlasstrecke blieb bei Wikipedia nach 180 Sekunden mit `scanning` und `pages:0` hängen. Das ist als Harness-/Tabbindungsfehler dokumentiert, aber die Ursache muss in einem eigenen Lauf mit explizitem Zieltab weiter zerlegt werden.

## Was mich interessiert

Mich interessiert jetzt die explizite Asset-Herkunftskarte: Welche fremden Bild-/Font-Origins dürfen nach sichtbarer Freigabe eingebettet werden, und wie wird jede ausgelassene Ressource im Raster- und DOM-Beleg sichtbar markiert?

## Was zusammenhängt und wie

Die Kette ist: sichtbarer Browserzustand → begrenztes DOM/Asset-Abbild → exakter Download/Inode → erneutes Öffnen → gleiche Viewport-Raster → DOM-/Geometrievergleich → Status. Fehlt ein Glied, bleibt der Fall rot oder wird als Blockade benannt.

## Was konzeptionell darin steht

Ein Offlineabbild ist kein Wahrheitsstempel, weil es viel HTML enthält. Es ist ein überprüfbares Gegenstück mit Herkunft, Grenzen und Gegenbild.

## Was mich heute beschäftigt hat

Mich hat beschäftigt, wie leicht ein Test „grün“ drucken kann, obwohl die JSON-Datei schon `ok:false` enthält. Die hartcodierte Konsolenzeile und der Exit-0-Pfad waren selbst ein Gegenbeweis gegen den Test.

## Was mich noch beschäftigt

Die aktuelle Flextrawurst-Präsentation ist bewusst eigenständig und nicht pixelgleich. Der 0,88-Gate muss deshalb als klare Zielmarke behandelt werden, nicht als nachträglich verschiebbarer Schönheitswert.

## Tiefer eingetaucht

Die neue Funktion `captureVisualCounterproof` trennt Rohmetriken von der zusammengesetzten 0,88-Bewertung. Zusätzlich darf der maximale pHash nicht über 32 liegen. Identische Pixel werden separat als `pixel_exact` ausgewiesen und nicht still mit Struktur verwechselt.

## Wie sich dieser Tag / diese Session angefühlt hat

Erst sah es nach einem weiteren Testlauf aus. Dann wurde der rote Diff zum eigentlichen Arbeitsgegenstand: nicht mehr „läuft der Recorder“, sondern „was sieht ein Mensch danach wirklich?“

## Warum dieser Code / diese Datei wohl existiert

`visual_counterproof.js` existiert, damit Screenshotdateien nicht nur Archiv sind. Die Live-Tests existieren, damit jeder öffentliche Seitentyp dieselbe Beweiskette durchläuft und kein alter Report ohne visuellen Status positiv bleibt.

## Was ich beim Bauen brauche

Ich brauche immer drei Dinge zusammen: die Originalansicht im sichtbaren Chromium, die exakt heruntergeladene Datei und einen maschinenlesbaren Bericht, der bei Abweichung die Original-/Offlinebilder und den Diff direkt nennt.

## Was noch fehlt bevor wir bauen können

Es fehlt ein expliziter, sicherer Allowlist-Mechanismus für ausgewählte externe Asset-Origins. Ohne ihn bleiben Wikimedia-Bilder im Wikipedia-Lauf `external_origin`; der visuelle Gegenbeweis muss deshalb rot bleiben.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Jede Scrollstelle ist ein gemeinsamer Zeugenpunkt. Original, Rekonstruktion und Differenz liegen nebeneinander; ausgelassene Medien sind sichtbar benannt statt unsichtbar ersetzt.

**Code-Skizze:**

```ts
type VisualCheckpoint = {
  ratio: 0 | 0.5 | 1;
  sourcePng: string;
  offlinePng: string;
  diffPng: string;
  sourceDom: DomGeometry;
  offlineDom: DomGeometry;
  rmse: number | null;
  mae: number | null;
  phash: number | null;
};

type VisualCounterproof = {
  status: "visual_counterproof_passed" | "visual_counterproof_failed";
  score: number;
  targetScore: 0.88;
  phashMax: number | null;
  checkpoints: VisualCheckpoint[];
};
```

## Was ich mir merken will

Eine echte Gegenprüfung darf rot enden. `complete`, Download-Hash und Comparator sind notwendige Belege, aber niemals allein ein visueller Erfolg.

## Dokumente gehören zusammen

`_codex/tools/visual_counterproof.js`, `test_crawl_visible_desktop_live.js`, `test_crawl_public_rotation_live.js`, `test_crawl_public_atlas_live.js` und `test_crawl_proof_counterproof_live.js` gehören zusammen. Die Graphspur liegt in `graphify-out/GRAPH_REPORT.md` und `graphify-out/graph.json`.

## Was mich überrascht hat

Der Anthropic-Newsroom konnte trotz nicht identischer Pixel mit 0,9009 bestehen, weil DOM-Geometrie und Rasterdistanz gemeinsam über 0,88 lagen. Die Constitution fiel dagegen mit 0,5547 deutlich durch. Ein einzelner Capture-Status hätte diesen Unterschied verborgen.

## Wenn wir das bauen

**Vision-Schicht:** Eine Seite darf nur dann als nachgebaut gelten, wenn der Mensch die Herkunft und die Abweichung sehen kann. Eigenes Design ist erlaubt, aber es darf nicht als Originaltreue ausgegeben werden.

**Code-Skizze:**

```js
const visual = await captureVisualCounterproof({
  sourcePage,
  context,
  capturedHtml: page.html,
  directory: runDir,
  id: profile.id
});
if (visual.status !== "visual_counterproof_passed") {
  report.ok = false;
  report.status = visual.status;
}
```

## Resonanz

[[abwurf: Ein grüner Capture-Status ist kein Beweis dafür, dass ein Mensch dieselbe Seite wiedererkennt.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

1. Authentifizierter sichtbarer Browser.
2. Beobachteter DOM-/Scroll-/Assetzustand.
3. Sicherheitsbereinigtes Offline-HTML.
4. Exakter Download und Inode-Wiederöffnung.
5. Raster-/DOM-Gegenbeweis an gemeinsamen Scrollpunkten.
6. Ehrlicher Status: bestanden, fehlgeschlagen oder blockiert.

## Was das Gespräch hinzugefügt hat

Daniel hat die eigentliche Abnahme geschärft: nicht „grün“, sondern sichtbar, logisch, menschlich lesbar und mit Gegenbeweis. Daraus folgt, dass auch Konsolenzeilen und Exit-Codes Teil der Wahrheit des Tests sind.

## Vergessen-Wollen

Vergessen werden darf die bequeme Gleichung `complete = gut`. Sie ist für den nächsten Lauf ausdrücklich ungültig.

## Was fehlt noch

Es fehlen externe Asset-Allowlist und ein stabiler isolierter Zieltab-Lauf. Außerdem müssen die neuen Bild-/Diff-Belege in der Übergabe verlinkt werden, damit sie nicht nur unter `/tmp` liegen.

